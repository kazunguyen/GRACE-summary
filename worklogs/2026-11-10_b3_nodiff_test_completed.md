# B3-nodiff test inference completed — 2026-11-10

## Scope and source

- Kaggle kernel: `quangdung1111/03-kaggle-qwen-q4-b3-nodiff-test-runtime-locked-20`.
- Arm/split/prompt seed: `B3-nodiff`, test, seed 42.
- Notebook: `14_Arm_B3_NoDiff/notebooks/03_kaggle_qwen_q4_b3_nodiff_test_runtime_locked_20261109.ipynb`; downloaded executed notebook committed together with the Kaggle output.
- Output directory: `Runs-management/kaggle_outputs_20261110/b3_nodiff_test_runtime_locked/`.
- Dataset bundle SHA-256: Devign `246e47e64055fdf6e7309f696d1527a3a8cfc6d7315468750778e3fb9e340da9`; ReVeal `b4e4d90165969e6f0c6807ea4d08ae6f0e4eb46339aa1511f0a729a30ebcbbe3`.

## Completion and runtime provenance

- Devign started `2026-11-10T01:58:43Z` and completed `2026-11-10T06:17:14Z` (08:58:43–13:17:14 GMT+7), **2,732/2,732**.
- ReVeal started `2026-11-10T06:17:24Z` and completed `2026-11-10T16:59:14Z` (13:17:24–23:59:14 GMT+7), **2,274/2,274**.
- Both status files say `complete`, `timed_out=false`; total **5,006/5,006** records.
- `runtime_contract_sha256`: `bf1f859dc786e206a3c11d655b04b528dc68f59a15a82d4db894ac5944b0ac2e`. Model SHA-256: `f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335`; tokenizer revision `b2cff646eb4bb1d68355c01b18ae02e7cf42d120`.
- Kaggle diagnostics identify two Tesla T4 GPUs; both Devign and ReVeal `model_load_offload.log` files record `offloaded 49/49 layers to GPU`.
- The only thresholds applied were the validation-locked values, Devign **0.92** and ReVeal **0.01** (`locked_validation`). The test run did not fit or select thresholds. `thresholds_used.json` points to validation threshold-lock SHA-256 `64dde9b94a44ae56b3abe0b7e6abd6ced2a5320d7fee2785a961c5da225a786c`; the source validation runtime lock is recorded as `85d8770839f80260cdc7c27b27b6cce6bf8815675c8593db68fb102589c5cbd6`.

## Shared evaluator results

The notebook called `grace_diag.evaluate_final.table_a`; the downloaded CSV and JSON are preserved under `b3_nodiff_test/shared_evaluator_output/`.

| Dataset | n | Score-valid | AUROC | AUPRC | τ | MCC@τ | Balanced accuracy@τ | F1@τ | TP / FP / TN / FN @τ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Devign | 2,732 | 2,732 | 0.535915 | 0.500679 | 0.92 | 0.053011 | 0.526507 | 0.522885 | 714 / 762 / 715 / 541 |
| ReVeal | 2,274 | 2,274 | 0.557163 | 0.118942 | 0.01 | 0.060267 | 0.547975 | 0.198220 | 167 / 1,288 / 756 / 63 |

The evaluator CSV's unsuffixed `TP,FP,TN,FN` columns are computed at 0.5 (`m05`) even though the row also contains locked-threshold metrics. The confusion matrices above were recalculated from record scores at the locked τ values and checked against MCC/BA/F1/PPR@τ.

Devign has one raw response marked invalid (`response_coverage=0.999634`), but all 2,732 rows have valid scores; ReVeal has 2,274 valid responses and scores. The run is complete as an inference census; the metrics are weak and should be interpreted as reported, without threshold changes based on test.

## Commits

1. `b5c65fa results: archive B3-nodiff test inference` — downloaded output and executed notebook.
2. `b9bc35b docs(runs): record B3-nodiff test completion` — `Runs-management/RUNS.md`, entry I-27.
3. This worklog is committed separately after the two preceding commits.
