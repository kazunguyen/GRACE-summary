"""Ext20 comparison using P_pre's uniform ridge penalty and grouped-OOF C rule.

The score phase fits on validation only and writes label-free test predictions.
The separate evaluate phase loads test targets/groups only after checking the
prediction hash. This is a post-registration exploratory extension.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, matthews_corrcoef, roc_auc_score

HOME = Path(__file__).resolve().parent
sys.path.insert(0, str(HOME))

import ext05_runner as ext5
import ext16_focal_loss_mm_runner as ext16
import ext20_context_interaction_runner as ext20
import ext20_test_pipeline as testio

OUT = HOME / "runs/independent-post-ext20-uniform-ridge-pre-c-test-20261126/attempt-1"
PRED = OUT / "frozen_test_predictions.csv"
LOCK = OUT / "validation_lock.json"
PARAMS = OUT / "locked_model_parameters.npz"
SCORE_MANIFEST = OUT / "score_manifest.json"
RESULTS = OUT / "test_metrics.json"
REPORT = OUT / "test_report.md"
DATASETS = testio.DATASETS
CS = tuple(float(c) for c in ext20.CS)
SEED = int(testio.FINAL_CV_SEED)
BOOT_DRAWS = int(testio.DRAWS)
BOOT_SEED = int(testio.BOOT_SEED)


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def atomic_json(path: Path, obj) -> None:
    path = Path(path)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")
    os.replace(tmp, path)


def uniform_prepare(X):
    """Keep Ext20 fold-local scaling/features, replace only its penalty matrix."""
    prep = ext20.prepare_partition(X)
    prep["penalty"] = np.eye(int(prep["width"]), dtype=np.float64)
    prep["interaction_penalty"] = 1.0
    prep["penalty_rule"] = "uniform_l2_all_150_slopes_intercept_unpenalized"
    return prep


def select_c_like_pre(data, Q, seed):
    """Grouped 3-fold OOF AP maximization; ties go to the smaller C, like P_pre."""
    Q = np.asarray(Q, dtype=int)
    y = np.asarray(data["y"], dtype=np.int8)
    groups = np.asarray(data["g"]).astype(str)
    folds = ext20.group_folds(y[Q], groups[Q], int(seed))
    oof = {c: np.full(len(Q), np.nan, dtype=np.float64) for c in CS}
    fold_diagnostics = []
    for k, (tr, va) in enumerate(folds):
        A, B = Q[tr], Q[va]
        Xtr = ext20.feature_matrix(data, A)
        Xva = ext20.feature_matrix(data, B)
        prep = uniform_prepare(Xtr)
        row = {"fold": int(k), "train_n": int(len(A)), "heldout_n": int(len(B)),
               "C": {}}
        for c in CS:
            model, diag = ext20.fit_post(Xtr, y[A], c, prep)
            row["C"][str(c)] = {"usable": bool(diag["usable"]),
                                "iterations": int(diag["iterations"]),
                                "failure": diag["failure"]}
            if not diag["usable"]:
                raise RuntimeError(f"C={c} fold={k}: Ext20 uniform-penalty fit unusable")
            _, pred = ext20.predict_post(model, Xva)
            oof[c][va] = pred
        fold_diagnostics.append(row)
    if any(not np.isfinite(v).all() for v in oof.values()):
        raise RuntimeError("incomplete grouped-OOF scores; refusing a C fallback")
    aps = {str(c): float(average_precision_score(y[Q], oof[c])) for c in CS}
    chosen = max(CS, key=lambda c: (aps[str(c)], -c))
    return {"C": float(chosen), "AP_OOF_by_C": aps,
            "selection_rule": "maximum pooled grouped-OOF AP; ties to smaller C",
            "seed": int(seed), "folds": fold_diagnostics}


def save_params(parameters):
    arrays = {}
    for ds, item in parameters.items():
        pre = item["pre"]["model"]
        scaler = pre.named_steps["standardscaler"]
        lr = pre.named_steps["logisticregression"]
        post = item["post"]
        prep = post["prepared"]
        arrays[f"{ds}_pre_mean"] = scaler.mean_
        arrays[f"{ds}_pre_scale"] = scaler.scale_
        arrays[f"{ds}_pre_coef"] = lr.coef_
        arrays[f"{ds}_pre_intercept"] = lr.intercept_
        arrays[f"{ds}_post_theta"] = post["theta"]
        arrays[f"{ds}_post_h3_mean"] = prep["h3_scaler"].mean_
        arrays[f"{ds}_post_h3_scale"] = prep["h3_scaler"].scale_
        arrays[f"{ds}_post_family_mean"] = prep["family_scaler"].mean_
        arrays[f"{ds}_post_family_scale"] = prep["family_scaler"].scale_
        arrays[f"{ds}_post_signal_mean"] = prep["signal_scaler"].mean_
        arrays[f"{ds}_post_signal_scale"] = prep["signal_scaler"].scale_
        arrays[f"{ds}_post_interaction_mean"] = prep["interaction_mean"]
        arrays[f"{ds}_post_interaction_scale"] = prep["interaction_scale"]
        arrays[f"{ds}_post_penalty_diagonal"] = np.diag(prep["penalty"])
    np.savez_compressed(PARAMS, **arrays)


def score_only():
    OUT.mkdir(parents=True, exist_ok=True)
    frozen = ext20.assert_frozen_hashes()
    meta = ext5.load_inputs()
    testio.ext3.verify_donors(meta)
    models, locks, params = {}, {}, {}

    # All selection and fitting finish and are written to LOCK before test inputs load.
    for ds in DATASETS:
        data = ext5.build_sources(meta, ds)
        Q = np.arange(len(data["y"]), dtype=int)
        pre = ext16.frozen_pre(data, Q, SEED)
        post_selection = select_c_like_pre(data, Q, SEED)
        Xv = ext20.feature_matrix(data, Q)
        prep = uniform_prepare(Xv)
        post, diag = ext20.fit_post(Xv, data["y"], post_selection["C"], prep)
        if not diag["usable"]:
            raise RuntimeError(f"{ds}: final P_post fit is unusable")
        old_lock = json.loads((testio.OUT / "validation_lock.json").read_text(encoding="utf-8"))
        old_pre = old_lock["datasets"][ds]
        if float(pre["C"]) != float(old_pre["P_pre_C"]):
            raise RuntimeError(f"{ds}: recomputed P_pre C differs from the existing validation lock")
        if abs(float(pre["tau"]) - float(old_pre["P_pre_tau"])) > 1e-12:
            raise RuntimeError(f"{ds}: recomputed P_pre threshold differs from the existing lock")
        locks[ds] = {
            "validation_n": int(len(Q)),
            "validation_groups": int(pd.Series(data["g"]).nunique()),
            "shared_group_cv_seed": SEED,
            "P_pre_C": float(pre["C"]),
            "P_pre_tau": float(pre["tau"]),
            "P_pre_OOF_AP_by_C": pre["AP_by_C"],
            "P_post_C": float(post_selection["C"]),
            "P_post_OOF_AP_by_C": post_selection["AP_OOF_by_C"],
            "P_post_selection_rule": post_selection["selection_rule"],
            "P_post_penalty": "uniform L2 on all 150 slopes; intercept unpenalized",
            "P_post_final_solver": {k: v for k, v in diag.items()},
        }
        models[ds] = {"pre": pre, "post": post}
        params[ds] = models[ds]

    atomic_json(LOCK, {
        "protocol": "Ext20 same-penalty-and-C-rule-as-P_pre test extension",
        "training_scope": "validation rows only",
        "test_selection_or_fitting": False,
        "P_post_penalty_diagonal": "identity for 48 main effects and 102 interactions; intercept excluded",
        "P_post_C_rule": "same grouped 3-fold OOF AP maximization as P_pre; ties to smaller C; no 15-arm eligibility gate",
        "C_grid": list(CS),
        "datasets": locks,
        "validation_runner_sha256": frozen["runner_sha256"],
        "validation_protocol_sha256": frozen["protocol_sha256"],
        "prior_test_exposure": "test split appeared in earlier exploratory candidate analyses; this remains exploratory",
    })
    save_params(params)
    predictions, sources = [], {}
    for ds in DATASETS:
        ids = testio.get_test_ids(ds)  # only split/dataset/id columns
        Xt, names, h3hash = testio.h3_test(ds, ids)
        arms, arm_sources = testio.all_test_arms(ds, ids)  # label-selective parsing
        Xtest = ext20.feature_matrix({"x": Xt, "names": names, "arms": arms},
                                     np.arange(len(ids), dtype=int))
        ppre = models[ds]["pre"]["model"].predict_proba(Xt)[:, 1]
        post_eta, ppost = ext20.predict_post(models[ds]["post"], Xtest)
        if not np.isfinite(ppre).all() or not np.isfinite(ppost).all():
            raise FloatingPointError(f"{ds}: nonfinite frozen test predictions")
        frame = pd.DataFrame({"dataset": ds, "id": ids, "P_pre": ppre,
                              "P_post": ppost, "P_post_logit": post_eta})
        for arm, scores in arms.items():
            frame[f"arm_{arm}"] = scores
        predictions.append(frame)
        sources[ds] = {"n": len(ids), "h3_sha256": h3hash,
                       "arms": arm_sources, "test_label_values_decoded": False}
    pred = pd.concat(predictions, ignore_index=True)
    if {"target_label", "group_id"} & set(pred.columns):
        raise AssertionError("labels or groups entered frozen predictions")
    pred.to_csv(PRED, index=False)
    atomic_json(SCORE_MANIFEST, {
        "phase": "score_only_completed",
        "predictions_sha256": sha(PRED),
        "validation_lock_sha256": sha(LOCK),
        "parameters_sha256": sha(PARAMS),
        "rows": int(len(pred)),
        "test_labels_loaded_before_prediction_freeze": False,
        "test_sources": sources,
    })
    print(json.dumps({"phase": "score_only_completed", "rows": len(pred),
                      "predictions_sha256": sha(PRED),
                      "selected_C": {ds: {"P_pre": locks[ds]["P_pre_C"],
                                           "P_post": locks[ds]["P_post_C"]}
                                      for ds in DATASETS}}, indent=2))


def evaluate():
    if not PRED.is_file() or not LOCK.is_file() or not SCORE_MANIFEST.is_file():
        raise FileNotFoundError("run score phase first")
    sm = json.loads(SCORE_MANIFEST.read_text(encoding="utf-8"))
    if sm["predictions_sha256"] != sha(PRED):
        raise RuntimeError("prediction hash mismatch; refusing to load test labels")
    if sm["validation_lock_sha256"] != sha(LOCK):
        raise RuntimeError("validation lock changed; refusing to load test labels")
    pred = pd.read_csv(PRED, dtype={"id": str})
    if {"target_label", "group_id"} & set(pred.columns):
        raise ValueError("truth fields found in frozen predictions")
    lock = json.loads(LOCK.read_text(encoding="utf-8"))

    # First target/group read; prediction and lock hashes were verified above.
    truth = pd.read_parquet(testio.ext3.SOURCE / "inputs.parquet",
        columns=["split", "dataset", "id", "target_label", "group_id"],
        filters=[("split", "==", "test")], engine="pyarrow")
    if set(truth.split.astype(str)) != {"test"} or truth.group_id.isna().any():
        raise ValueError("invalid test truth projection")
    if set(truth.target_label.astype(int).unique()) != {0, 1}:
        raise ValueError("test labels must contain both classes")

    from sklearn.metrics import average_precision_score, matthews_corrcoef, roc_auc_score
    results = {"phase": "labels_evaluated_after_frozen_predictions",
               "bootstrap_draws": BOOT_DRAWS, "bootstrap_seed": BOOT_SEED,
               "datasets": {},
               "classification": "exploratory_test_extension",
               "test_exposure_caveat": "This benchmark split appeared in earlier exploratory candidate analyses; not independent confirmatory evidence."}
    for ds in DATASETS:
        t = truth[truth.dataset == ds].copy()
        p = pred[pred.dataset == ds].copy()
        t["id"] = t.id.astype(str)
        z = t.merge(p, on=["dataset", "id"], how="outer",
                    validate="one_to_one", indicator=True)
        if not z._merge.eq("both").all():
            raise ValueError(f"{ds}: truth/prediction ID join mismatch")
        z = z.drop(columns="_merge").sort_values("id").reset_index(drop=True)
        y = z.target_label.to_numpy(np.int8)
        g = z.group_id.astype(str).to_numpy()
        pre = z.P_pre.to_numpy(float)
        post = z.P_post.to_numpy(float)
        tau = float(lock["datasets"][ds]["P_pre_tau"])
        b2 = z["arm_B2"].to_numpy(float)
        metrics = {}
        for name, scores in (("P_pre", pre), ("P_post", post), ("B2", b2)):
            pred_pos = scores >= tau
            metrics[name] = {
                "AP": float(average_precision_score(y, scores)),
                "AUROC": float(roc_auc_score(y, scores)),
                "MCC": float(matthews_corrcoef(y, pred_pos)),
                "positive_predictions": int(pred_pos.sum()),
            }
        delta = {"AP": [], "AUROC": [], "MCC": []}
        delta_b2 = {"AP": [], "AUROC": [], "MCC": []}
        valid = 0
        for weights in ext5.group_draws(g, BOOT_DRAWS, BOOT_SEED):
            ix = ext5.idx_from_weights(weights)
            if len(ix) == 0 or np.unique(y[ix]).size < 2:
                continue
            valid += 1
            for scores, ref, bucket in ((post, pre, delta), (post, b2, delta_b2)):
                bucket["AP"].append(float(average_precision_score(y[ix], scores[ix]) -
                                             average_precision_score(y[ix], ref[ix])))
                bucket["AUROC"].append(float(roc_auc_score(y[ix], scores[ix]) -
                                                 roc_auc_score(y[ix], ref[ix])))
                bucket["MCC"].append(float(matthews_corrcoef(y[ix], scores[ix] >= tau) -
                                            matthews_corrcoef(y[ix], ref[ix] >= tau)))
        if valid < int(BOOT_DRAWS * .99):
            raise RuntimeError(f"{ds}: insufficient valid paired group-bootstrap samples")
        ci = lambda v: np.percentile(np.asarray(v, float), [2.5, 97.5]).tolist()
        comparisons = {}
        for name, ref in (("P_pre", delta), ("B2", delta_b2)):
            comparisons[name] = {}
            for m in ("AP", "AUROC", "MCC"):
                comparisons[name][m] = {
                    "delta": metrics["P_post"][m] - metrics[name][m],
                    "CI95": ci(ref[m]),
                }
        results["datasets"][ds] = {
            "n": int(len(y)), "groups": int(pd.Series(g).nunique()),
            "threshold_shared_from_validation": tau,
            "metrics": metrics,
            "P_post_minus_P_pre": comparisons["P_pre"],
            "P_post_minus_B2": comparisons["B2"],
            "valid_bootstrap_draws": int(valid),
            "current_MCC_rule_point_gt_0_02_and_CI_lower_gt_0": bool(
                comparisons["P_pre"]["MCC"]["delta"] > .02 and
                comparisons["P_pre"]["MCC"]["CI95"][0] > 0),
        }
    atomic_json(RESULTS, results)
    lines = [
        "# Ext20: uniform ridge và quy tắc chọn C kiểu P_pre",
        "",
        "Đánh giá thăm dò trên test; test split đã xuất hiện trong các phân tích ứng viên trước.",
        "P_pre/P_post và C được fit/chọn trên validation; dự đoán test được hash trước khi nạp nhãn.",
        "P_post dùng ridge đồng nhất trên 150 hệ số; selector chọn AP OOF cao nhất, hòa chọn C nhỏ hơn.",
        "",
    ]
    for ds in DATASETS:
        d = results["datasets"][ds]
        c = lock["datasets"][ds]
        lines += [f"## {ds}",
            f"C_pre={c['P_pre_C']}; C_post={c['P_post_C']}; threshold={d['threshold_shared_from_validation']:.2f}; n={d['n']}; groups={d['groups']}.",
            "| Model | AP | AUROC | MCC |",
            "|---|---:|---:|---:|",
        ]
        for model in ("P_pre", "P_post", "B2"):
            m = d["metrics"][model]
            lines.append(f"| {model} | {m['AP']:.5f} | {m['AUROC']:.5f} | {m['MCC']:.5f} |")
        lines.append("")
        for metric, cval in d["P_post_minus_P_pre"].items():
            lo, hi = cval["CI95"]
            lines.append(f"Δ{metric}(P_post−P_pre) = {cval['delta']:+.5f}; CI95 [{lo:+.5f}, {hi:+.5f}].")
        lines.append("")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    atomic_json(OUT / "evaluation_manifest.json", {
        "phase": "completed_after_prediction_hash_check",
        "prediction_sha256": sha(PRED), "metrics_sha256": sha(RESULTS),
        "test_labels_loaded_after_prediction_freeze": True,
        "classification": "exploratory_test_extension",
    })
    print(json.dumps({ds: results["datasets"][ds]["P_post_minus_P_pre"]
                      for ds in DATASETS}, indent=2))


if __name__ == "__main__":
    phase = sys.argv[1] if len(sys.argv) > 1 else "score"
    if phase == "score":
        score_only()
    elif phase == "evaluate":
        evaluate()
    else:
        raise SystemExit("usage: ext20_uniform_ridge_pre_c_runner.py [score|evaluate]")
