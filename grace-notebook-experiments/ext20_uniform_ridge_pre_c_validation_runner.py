from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, matthews_corrcoef, roc_auc_score

HOME = Path(r"D:\JUNIOR\LabThayTho\GRACE-summary\grace-notebook-experiments")
sys.path.insert(0, str(HOME))

import ext05_runner as ext5
import ext16_focal_loss_mm_runner as ext16
import ext20_context_interaction_runner as ext20
import ext20_uniform_ridge_pre_c_runner as uniform

OUT = HOME / "runs/independent-post-ext20-uniform-ridge-pre-c-validation-20261126/attempt-1"
BOOT_DRAWS = 5000
BOOT_SEED = int(ext16.BASE + 9000)


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    frozen = ext20.assert_frozen_hashes()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "run_state.json").write_text(
        json.dumps({"state": "validation_only_fit_started",
                    "test_rows_labels_scores_predictions_read": False,
                    "registered_hashes_verified": True,
                    "frozen_runner_sha256": frozen["runner_sha256"]},
                   indent=2) + "\n", encoding="utf-8")
    meta = ext5.load_inputs()
    print("loaded validation metadata", flush=True)
    data_by = {ds: ext5.build_sources(meta, ds) for ds in ("devign", "reveal")}
    print("built validation sources", flush=True)
    old3 = pd.read_csv(ext20.EXT03 / "outer_predictions.csv", low_memory=False)
    old4 = pd.read_csv(ext20.EXT04 / "outer_predictions.csv", low_memory=False)
    r3 = json.loads((ext20.EXT03 / "results.json").read_text(encoding="utf-8"))
    r4 = json.loads((ext20.EXT04 / "results.json").read_text(encoding="utf-8"))

    results = {
        "status": "completed",
        "protocol": "uniform L2 on all 150 P_post slopes; P_pre-like grouped OOF AP C selection",
        "validation_only": True,
        "test_rows_labels_scores_predictions_read": False,
        "outer_seed": int(ext20.BASE + 8100),
        "inner_seed_rule": "ext20.BASE + 100000 + 1000 * outer_fold",
        "C_grid": list(uniform.CS),
        "bootstrap_draws": BOOT_DRAWS,
        "datasets": {},
    }
    all_predictions = []
    for ds_index, ds in enumerate(("devign", "reveal")):
        d = data_by[ds]
        y = np.asarray(d["y"], dtype=np.int8)
        g = np.asarray(d["g"]).astype(str)
        ids = np.asarray(d["ids"]).astype(str)
        outer = ext20.group_folds(y, g, ext20.BASE + 8100)
        pre = np.full(len(y), np.nan)
        post = np.full(len(y), np.nan)
        tau = np.full(len(y), np.nan)
        fold_info = []
        for oi, (train, heldout) in enumerate(outer):
            print(f"{ds}: outer fold {oi} selecting C", flush=True)
            seed = int(ext20.BASE + 100000 + 1000 * oi)
            selection = uniform.select_c_like_pre(d, train, seed)
            Xtr = ext20.feature_matrix(d, train)
            prepared = uniform.uniform_prepare(Xtr)
            model, diag = ext20.fit_post(Xtr, y[train], selection["C"], prepared)
            if not diag["usable"]:
                raise RuntimeError(f"{ds} outer {oi}: P_post fit unusable: {diag}")
            _, ppost = ext20.predict_post(model, ext20.feature_matrix(d, heldout))

            frozen_pre = ext16.frozen_pre(d, train, seed)
            ppre = frozen_pre["model"].predict_proba(d["x"][heldout])[:, 1]
            pre[heldout] = ppre
            post[heldout] = ppost
            tau[heldout] = float(frozen_pre["tau"])
            fold_info.append({
                "outer_fold": oi,
                "train_n": int(len(train)),
                "heldout_n": int(len(heldout)),
                "C_post": float(selection["C"]),
                "C_pre": float(frozen_pre["C"]),
                "tau_pre": float(frozen_pre["tau"]),
                "P_post_AP_OOF_by_C": selection["AP_OOF_by_C"],
                "P_post_selection_rule": selection["selection_rule"],
                "P_post_fit": diag,
            })
            print(f"{ds}: outer fold {oi} complete; C_post={selection['C']}", flush=True)
        if not (np.isfinite(pre).all() and np.isfinite(post).all() and np.isfinite(tau).all()):
            raise RuntimeError(f"{ds}: incomplete nested out-of-fold predictions")

        # Recompute FrozenPre and require exact fold/prediction parity with two
        # existing validation-only ledgers before reporting the new extension.
        pre_audit = []
        for ledger, ledger_result, pred_col in (
            (old3, r3, "prediction"), (old4, r4, "prediction")
        ):
            q = ledger[(ledger.dataset == ds) & (ledger.model == "P_pre")].copy()
            q["id"] = q.id.astype(str)
            q = q.set_index("id").reindex(ids)
            if q[pred_col].isna().any():
                raise RuntimeError(f"{ds}: missing P_pre ledger predictions")
            if not np.array_equal(q.target_label.to_numpy(int), y):
                raise RuntimeError(f"{ds}: validation label mismatch with P_pre ledger")
            if not np.array_equal(q.group_id.astype(str).to_numpy(), g):
                raise RuntimeError(f"{ds}: validation group mismatch with P_pre ledger")
            fold_diffs = []
            for oi, (_, heldout) in enumerate(outer):
                if not np.array_equal(q.iloc[heldout].outer_fold.to_numpy(int),
                                      np.full(len(heldout), oi)):
                    raise RuntimeError(f"{ds}: P_pre outer split mismatch")
                dmax = float(np.max(np.abs(pre[heldout] - q.iloc[heldout][pred_col].to_numpy(float))))
                fold_diffs.append(dmax)
                expected = ledger_result["datasets"][ds]["outer_folds"][oi]
                got = fold_info[oi]
                expected_C = expected.get("P_pre_C_outer_train", expected.get("P_pre_C"))
                expected_tau = expected.get("tau_T", expected.get("P_pre_tau"))
                if expected_C is not None and abs(got["C_pre"] - float(expected_C)) > 1e-12:
                    raise RuntimeError(f"{ds}: P_pre C parity mismatch at outer fold {oi}")
                if expected_tau is not None and abs(got["tau_pre"] - float(expected_tau)) > 1e-12:
                    raise RuntimeError(f"{ds}: P_pre threshold parity mismatch at outer fold {oi}")
            pre_audit.append(max(fold_diffs))
        if max(pre_audit) > 1e-12:
            raise RuntimeError(f"{ds}: FrozenPre prediction parity failed: {pre_audit}")

        arms = {"B0": np.asarray(d["arms"]["B0"], dtype=float),
                "B2": np.asarray(d["arms"]["B2"], dtype=float)}
        scores = {"P_pre": pre, "P_post": post, "B0": arms["B0"], "B2": arms["B2"]}
        metrics = {}
        for name, p in scores.items():
            metrics[name] = {
                "AP": float(average_precision_score(y, p)),
                "AUROC": float(roc_auc_score(y, p)),
                "MCC": float(matthews_corrcoef(y, p >= tau)),
            }

        groups_draw = ext5.group_draws(g, BOOT_DRAWS, BOOT_SEED + ds_index)
        boot = {name: {m: [] for m in ("AP", "AUROC", "MCC")}
                for name in ("P_post_minus_P_pre", "P_pre_minus_B0",
                             "P_post_minus_B0", "P_pre_minus_B2", "P_post_minus_B2")}
        valid = 0
        pair_defs = (
            ("P_post_minus_P_pre", "P_post", "P_pre"),
            ("P_pre_minus_B0", "P_pre", "B0"),
            ("P_post_minus_B0", "P_post", "B0"),
            ("P_pre_minus_B2", "P_pre", "B2"),
            ("P_post_minus_B2", "P_post", "B2"),
        )
        for weights in groups_draw:
            ix = np.flatnonzero(weights)
            sample_weight = weights[ix]
            if not len(ix) or not np.any((y[ix] == 0) & (sample_weight > 0)) or not np.any((y[ix] == 1) & (sample_weight > 0)):
                continue
            valid += 1
            draw_metrics = {}
            for name, p in scores.items():
                draw_metrics[name] = {
                    "AP": float(average_precision_score(y[ix], p[ix], sample_weight=sample_weight)),
                    "AUROC": float(roc_auc_score(y[ix], p[ix], sample_weight=sample_weight)),
                    "MCC": float(matthews_corrcoef(y[ix], (p[ix] >= tau[ix]).astype(int),
                                                   sample_weight=sample_weight)),
                }
            for cname, a, b in pair_defs:
                for metric in ("AP", "AUROC", "MCC"):
                    boot[cname][metric].append(draw_metrics[a][metric] - draw_metrics[b][metric])
        if valid < int(BOOT_DRAWS * .99):
            raise RuntimeError(f"{ds}: only {valid} valid group bootstrap draws")
        comparisons = {}
        for cname, a, b in pair_defs:
            comparisons[cname] = {}
            for m in ("AP", "AUROC", "MCC"):
                comparisons[cname][m] = {
                    "delta": metrics[a][m] - metrics[b][m],
                    "CI95": np.percentile(np.asarray(boot[cname][m]), [2.5, 97.5]).tolist(),
                }
        results["datasets"][ds] = {
            "n": int(len(y)), "groups": int(pd.Series(g).nunique()),
            "metrics": metrics, "comparisons": comparisons,
            "valid_bootstrap_draws": int(valid),
            "pre_prediction_max_abs_diff_to_frozen_ledgers": float(max(pre_audit)),
            "outer_folds": fold_info,
        }
        print(f"{ds}: bootstrap complete; valid={valid}", flush=True)
        for i, sample_id in enumerate(ids):
            all_predictions.append({
                "dataset": ds, "id": sample_id, "group_id": g[i], "target_label": int(y[i]),
                "P_pre": float(pre[i]), "P_post": float(post[i]), "tau_pre": float(tau[i]),
                "B0": float(arms["B0"][i]), "B2": float(arms["B2"][i]),
            })

    pred_path = OUT / "validation_outer_predictions.csv"
    pd.DataFrame(all_predictions).to_csv(pred_path, index=False)
    res_path = OUT / "validation_metrics.json"
    res_path.write_text(json.dumps(results, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
                        encoding="utf-8")
    manifest = {
        "status": "completed", "validation_only": True,
        "test_rows_labels_scores_predictions_read": False,
        "runner_sha256": sha(Path(__file__)),
        "registered_ext20_runner_sha256": frozen["runner_sha256"],
        "registered_protocol_sha256": frozen["protocol_sha256"],
        "prediction_sha256": sha(pred_path), "results_sha256": sha(res_path),
        "C_rule": "same as P_pre: grouped 3-fold OOF AP maximum on the fixed grid; ties to smaller C",
        "penalty": "uniform identity L2 on 48 main effects + 102 interactions; intercept excluded",
        "test_rows_read": False,
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                                       encoding="utf-8")
    (OUT / "run_state.json").write_text(
        json.dumps({"state": "completed", "exit_status": 0,
                    "test_rows_labels_scores_predictions_read": False,
                    "results_sha256": sha(res_path)}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({ds: {"metrics": item["metrics"], "comparisons": item["comparisons"]}
                      for ds, item in results["datasets"].items()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
