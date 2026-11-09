# B3-nodiff test delivery with locked validation thresholds

Date: 2026-11-09 (Asia/Bangkok)
Status: Prepared for Kaggle; test inference not launched.

## Inputs and scope

Prepared the complete test census from the frozen test specifications in `grace_15arms_prompts_and_clean_specs.zip`: Devign 2,732 and ReVeal 2,274 (5,006 total), seed 42. Each test prompt uses only its own test target code and graph. The B3 demonstrations come from the same dataset's exact vulnerable/patched train pair used for validation, with the two existing review approvals and source evidence carried into each inner bundle. The B3-nodiff prompt omits the Key difference block. Test labels stay in row metadata for downstream scoring and are not rendered into prompt text.

Thresholds are imported from the completed, sealed validation lock and pinned by raw file SHA-256 `c4c438a413ffafcbcac993be49c12963497a3290a8dc679f2c3e6fee763bdebf` and internal lock ID `64dde9b94a44ae56b3abe0b7e6abd6ced2a5320d7fee2785a961c5da225a786c`. Devign uses tau 0.92 and ReVeal tau 0.01. Notebook scoring applies `score >= tau`; it never chooses or adjusts thresholds using test data.

## Files

- Notebook: `14_Arm_B3_NoDiff/notebooks/03_kaggle_qwen_q4_b3_nodiff_test_runtime_locked_20261109.ipynb`.
- Kaggle upload: `14_Arm_B3_NoDiff/kaggle_delivery_20261109/grace_b3_nodiff_test_inputs.zip`.
- Reproducible builders: `14_Arm_B3_NoDiff/scripts/prepare_b3_nodiff_test_delivery.py` and `14_Arm_B3_NoDiff/scripts/build_b3_nodiff_test_notebook.py`.
- Output checkpoints: `grace_b3_nodiff_devign_test_checkpoint.zip`, `grace_b3_nodiff_reveal_test_checkpoint.zip`; each run also writes `test_predictions_at_validation_threshold.jsonl`, `batch_summary.json`, and diagnostics.

Outer delivery SHA-256: `1b8e1e7e45da033a753cf24b4338233b3c99cf59b6aaa8110a17f178c74a0d26`. The runtime lock remains the user-designated lock with SHA-256 `85d8770839f80260cdc7c27b27b6cce6bf8815675c8593db68fb102589c5cbd6`.

## Safeguards and checks

The notebook supports Kaggle's two observed input shapes: an auto-extracted outer dataset (with either auto-extracted or still-packed inner dataset archives), and a still-present upload archive. It recursively discovers the delivery manifest and model, verifies the sealed manifest and file hashes, and reports discovered paths/reasons if discovery fails. During inference, a reader thread drains child output while the notebook emits a 60-second heartbeat from the runner's atomic status file and counts checkpoint records; a quiet model call therefore does not leave the cell apparently frozen. Resume requires an explicit checkpoint input path.

The notebook applies the existing 10.5-hour run budget and 300-second checkpoint reserve, checks the exact runtime contract and model digest, and produces separate per-dataset resumable checkpoints. Before inference, it tokenizes the full test census using the exact locked HF tokenizer and fails early if any prompt exceeds the 8,192-token context. The notebook's Python cells compile. Both inner prompt bundles passed the included runtime helper's sealed root, member inventory, bundle seal, census, unique ID, split, and prompt-hash checks (2,732 and 2,274 rows); test prompt text was checked for label leakage; the outer ZIP manifest and SHA-256 were checked. This is local artifact validation only; the test GPU run has not been performed.
