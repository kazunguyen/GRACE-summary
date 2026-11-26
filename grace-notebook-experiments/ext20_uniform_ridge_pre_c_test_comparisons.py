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
import ext20_test_pipeline as testio
import ext20_uniform_ridge_pre_c_runner as uniform

OUT = uniform.OUT
PRED = uniform.PRED
LOCK = uniform.LOCK
SCORE_MANIFEST = uniform.SCORE_MANIFEST
RESULTS = OUT / "test_comparisons_B0_B2.json"
FROZEN_METRICS = uniform.RESULTS


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    score_manifest = json.loads(SCORE_MANIFEST.read_text(encoding="utf-8"))
    if score_manifest["predictions_sha256"] != sha(PRED):
        raise RuntimeError("prediction hash mismatch; no test labels loaded")
    if score_manifest["validation_lock_sha256"] != sha(LOCK):
        raise RuntimeError("validation-lock hash mismatch; no test labels loaded")
    pred = pd.read_csv(PRED, dtype={"id": str})
    if {"target_label", "group_id"} & set(pred.columns):
        raise RuntimeError("frozen prediction file contains truth fields")
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    frozen_metrics = json.loads(FROZEN_METRICS.read_text(encoding="utf-8"))
    prior = (json.loads(RESULTS.read_text(encoding="utf-8"))
             if RESULTS.is_file() else None)

    # Read test targets/groups only after validating the frozen prediction and
    # validation-lock hashes above.
    truth = pd.read_parquet(
        testio.ext3.SOURCE / "inputs.parquet",
        columns=["split", "dataset", "id", "target_label", "group_id"],
        filters=[("split", "==", "test")], engine="pyarrow")
    if set(truth.split.astype(str)) != {"test"}:
        raise ValueError("truth projection included a non-test split")
    result = {
        "status": "evaluated_after_prediction_hash_check",
        "classification": "exploratory_test_extension",
        "test_exposure_caveat": "Benchmark appeared in earlier exploratory candidate analyses; not independent confirmation.",
        "prediction_sha256": sha(PRED),
        "validation_lock_sha256": sha(LOCK),
        "bootstrap_draws": int(testio.DRAWS),
        "bootstrap_seed": int(testio.BOOT_SEED),
        "MCC_threshold": "P_pre validation threshold, shared by all systems",
        "datasets": {},
    }
    for ds in testio.DATASETS:
        t = truth[truth.dataset == ds].copy()
        p = pred[pred.dataset == ds].copy()
        t["id"] = t.id.astype(str)
        z = t.merge(p, on=["dataset", "id"], how="outer",
                    validate="one_to_one", indicator=True)
        if not z._merge.eq("both").all():
            raise ValueError(f"{ds}: truth/prediction IDs mismatch")
        z = z.drop(columns="_merge").sort_values("id").reset_index(drop=True)
        y = z.target_label.to_numpy(np.int8)
        g = z.group_id.astype(str).to_numpy()
        tau = float(lock["datasets"][ds]["P_pre_tau"])
        scores = {
            "P_pre": z.P_pre.to_numpy(float),
            "P_post": z.P_post.to_numpy(float),
            "B0": z.arm_B0.to_numpy(float),
            "B2": z.arm_B2.to_numpy(float),
        }
        metrics = {name: dict(frozen_metrics["datasets"][ds]["metrics"][name])
                   for name in ("P_pre", "P_post", "B2")}
        b0 = scores["B0"]
        metrics["B0"] = {
            "AP": float(average_precision_score(y, b0)),
            "AUROC": float(roc_auc_score(y, b0)),
            "MCC": float(matthews_corrcoef(y, b0 >= tau)),
            "positive_predictions": int(np.sum(b0 >= tau)),
        }
        if abs(metrics["P_pre"]["AP"] - average_precision_score(y, scores["P_pre"])) > 1e-12:
            raise RuntimeError(f"{ds}: frozen P_pre metric mismatch")
        if abs(metrics["P_post"]["AP"] - average_precision_score(y, scores["P_post"])) > 1e-12:
            raise RuntimeError(f"{ds}: frozen P_post metric mismatch")
        pairs = (("P_pre_minus_B0", "P_pre", "B0"),
                 ("P_pre_minus_B2", "P_pre", "B2"))
        draws = ext5.group_draws(g, int(testio.DRAWS), int(testio.BOOT_SEED))
        samples = {key: {m: [] for m in ("AP", "AUROC", "MCC")} for key, _, _ in pairs}
        valid = 0
        for weights in draws:
            ix = np.flatnonzero(weights)
            sample_weight = weights[ix]
            if not len(ix) or not np.any((y[ix] == 0) & (sample_weight > 0)) or not np.any((y[ix] == 1) & (sample_weight > 0)):
                continue
            valid += 1
            draw_metrics = {}
            for name in ("P_pre", "B0", "B2"):
                s = scores[name]
                draw_metrics[name] = {
                    "AP": float(average_precision_score(y[ix], s[ix], sample_weight=sample_weight)),
                    "AUROC": float(roc_auc_score(y[ix], s[ix], sample_weight=sample_weight)),
                    "MCC": float(matthews_corrcoef(y[ix], (s[ix] >= tau).astype(int),
                                                   sample_weight=sample_weight)),
                }
            for key, left, right in pairs:
                for metric in ("AP", "AUROC", "MCC"):
                    samples[key][metric].append(draw_metrics[left][metric] -
                                                draw_metrics[right][metric])
        if valid < int(testio.DRAWS * .99):
            raise RuntimeError(f"{ds}: insufficient valid bootstrap draws: {valid}")
        comparisons = dict(prior["datasets"][ds]["comparisons"]) if prior else {}
        comparisons["P_post_minus_P_pre"] = frozen_metrics["datasets"][ds]["P_post_minus_P_pre"]
        comparisons["P_post_minus_B2"] = frozen_metrics["datasets"][ds]["P_post_minus_B2"]
        for key, left, right in pairs:
            comparisons[key] = {}
            for metric in ("AP", "AUROC", "MCC"):
                comparisons[key][metric] = {
                    "delta": metrics[left][metric] - metrics[right][metric],
                    "CI95": np.percentile(np.asarray(samples[key][metric]),
                                          [2.5, 97.5]).tolist(),
                }
        result["datasets"][ds] = {
            "n": int(len(y)), "groups": int(pd.Series(g).nunique()),
            "threshold": tau, "metrics": metrics, "comparisons": comparisons,
            "valid_bootstrap_draws": int(valid),
        }
    RESULTS.write_text(json.dumps(result, ensure_ascii=False, indent=2,
                                  allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
