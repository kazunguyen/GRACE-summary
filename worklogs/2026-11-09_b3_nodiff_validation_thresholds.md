# B3-nodiff validation acceptance and threshold lock

Date: 2026-11-09 (Asia/Bangkok)
Branch: `dung`
Kaggle kernel: `quangdung1111/02-kaggle-qwen-q4-b3-nodiff-validation-runtime-loc`

## Output and scope

Downloaded the completed kernel outputs with the user-requested Kaggle CLI command into `Runs-management/kaggle_outputs_20261109/b3_nodiff_validation_runtime_loc/`. The batch summary reports `complete`; Devign has 2,732/2,732 records and ReVeal has 2,273/2,273. All 5,005 expected validation IDs have unique records and 100% valid finite scores. No test data was read.

## Threshold rule and results

Recomputed both thresholds independently with the existing `Runs-management/kaggle_outputs_20261105/b2_flip/validation_lock.py` `validation_mcc_grid_v1` rule: scan 0.01–0.99, maximize MCC, positive when `score >= threshold`, ties within 1e-9 resolved by closest to 0.5 then lower threshold. The recomputed values exactly match the notebook's self-sealed lock:

| Dataset | N valid | Locked threshold | Validation MCC | Accuracy at threshold | Confusion matrix [[TN, FP], [FN, TP]] |
|---|---:|---:|---:|---:|---|
| Devign | 2,732 | 0.92 | 0.0503599266 | 0.5212298682 | [[763, 782], [526, 661]] |
| ReVeal | 2,273 | 0.01 | 0.0804227825 | 0.4368675759 | [[840, 1223], [57, 153]] |

These are validation-selected operating thresholds and validation fit metrics; the metrics are not an unbiased test estimate. The frozen global `Runs-management/thresholds.json` and preregistration files were not modified. Threshold lock SHA-256: `64dde9b94a44ae56b3abe0b7e6abd6ced2a5320d7fee2785a961c5da225a786c`.

## Runtime/output checks

- The exact requested runtime-lock SHA-256 is `85d8770839f80260cdc7c27b27b6cce6bf8815675c8593db68fb102589c5cbd6`.
- Both runs have matching model/prompt/runtime identities; `b3_delivery_runtime.checked_records` validates the full records and runtime provenance. Thresholds recompute exactly from the downloaded raw records.
- The pinned package versions are recorded. Runtime provenance identifies two Tesla T4 devices; native logs show 49/49 layers offloaded for each run.
- Curated evidence, records, input bundles, manifests, run metadata, provenance and diagnostic archive are under `Runs-management/run_handoff_20261109/B3_NODIFF_VALIDATION/`; `validation_acceptance.json` inventories SHA-256 values.

This is a validation threshold lock for the registered B3-nodiff arm. It authorizes subsequent test evaluation with these fixed per-dataset thresholds; test outputs must not be used to adjust them.
