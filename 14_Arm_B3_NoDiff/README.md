# Arm B3-nodiff — validation delivery

Arm chẩn đoán thuộc họ B3, giữ cặp demonstration contrastive (một hàm vulnerable, một hàm patched) và bỏ hoàn toàn phần giải thích `Key difference`. Arm id `B3-nodiff`; base arm `B3`; seed 42; model Qwen3-Coder-30B-A3B-Instruct GGUF Q4_K_M theo runtime lock.

This package is prepared for **validation inference only** (seed 42): Devign 2,732 targets and ReVeal 2,273 targets. It does not contain test prompts.

## Kaggle files

- Notebook: `notebooks/02_kaggle_qwen_q4_b3_nodiff_validation_runtime_locked_20261109.ipynb`
- Kaggle Dataset upload: `kaggle_delivery_20261109/grace_b3_nodiff_validation_inputs.zip`
- Upload the ZIP as one Kaggle Dataset. Kaggle auto-extracts it; the notebook traverses mounted input directories (including symlinks), verifies the sealed delivery manifest and every member hash, and reports discovered paths/rejection reasons if validation fails (it also accepts the original ZIP if present). Attach exactly one `Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf` model input, enable Internet, choose 2x Tesla T4, then run the notebook cells in order.

Runtime lock source is the user-designated `Runs-management/kaggle_outputs_20261107/b2_rand_seed42_test_latest/b2_rand_seed42_test/inference_runtime_lock.json`, SHA-256 `85d8770839f80260cdc7c27b27b6cce6bf8815675c8593db68fb102589c5cbd6`. The notebook allows up to 10.5 hours from the first cell, with a five-minute checkpoint reserve, and verifies the lock bytes and internal seal; package versions, GGUF hash, tokenizer revision, full constructor, score calculation, device profile, and 49-layer offload are guarded by the contract. It writes package/build/GPU/offload/runner provenance.

## Prompt construction

The input source is `B3_NEW_ALGORITHM_PROMPTS_DEVIGN_REVEAL_20261108.zip`. The transform removes the complete `Key difference` and `Security rationale` explanation block from each B3 prompt. It preserves target code, graph, both examples, answer instruction, labels and IDs. Prompt SHA-256 values are recomputed and sealed. The ZIP retains the pair provenance and both review forms.

- Devign demonstration: `case_08_ffmpeg_can_safely_read_8614_26054`
- ReVeal demonstration: `case_reveal_curl_alloc_addbyter_16061_17887`

## Outputs

Kaggle Output will contain separate resumable checkpoints:

- `grace_b3_nodiff_devign_validation_checkpoint.zip`
- `grace_b3_nodiff_reveal_validation_checkpoint.zip`
- `grace_diagnostics.zip`

After both validation datasets reach full ID coverage, the notebook fits one threshold per dataset using the registered `validation_mcc_grid_v1` MCC grid (0.01–0.99), applies the `score >= threshold` rule and writes a sealed `validation_threshold_lock.json` with score coverage, confusion matrix, accuracy, full MCC grid, and run evidence. Incomplete runs retain checkpoints and skip threshold locking. It never reads test inputs. GPU execution has not yet been performed.

## Test delivery (threshold locked)

- Notebook: `notebooks/03_kaggle_qwen_q4_b3_nodiff_test_runtime_locked_20261109.ipynb`
- Kaggle Dataset upload: `kaggle_delivery_20261109/grace_b3_nodiff_test_inputs.zip`
- Scope: Devign test 2,732 and ReVeal test 2,274, seed 42.
- Upload the ZIP as one Kaggle Dataset. Kaggle may expose only extracted folders; the notebook searches mounted inputs recursively, verifies the sealed delivery manifest and member hashes, and handles recursively extracted nested prompt ZIPs. It also accepts a still-packed nested ZIP. It prints a 60-second heartbeat with record progress during quiet inference periods.
- Attach exactly one `Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf` model matching SHA-256 `f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335`, enable Internet, select 2x Tesla T4, then run cells in order.
- Validation thresholds are pinned and applied unchanged: Devign `0.92`, ReVeal `0.01`; the notebook never fits a threshold on test. It writes one checkpoint per dataset and `test_predictions_at_validation_threshold.jsonl` with score, locked threshold, prediction and label for later evaluation.
- Before loading the model for inference, it tokenizes every test prompt with the exact locked tokenizer and fails early with the offending target if any prompt exceeds the 8,192-token context.
- Test targets use the frozen 15-arm test code/graph. Demonstrations reuse the corresponding dual-reviewed train pair from validation. Labels remain outside prompt text.
- Outer bundle SHA-256: `2aeef20d4eac4e50df204d79183db3cb8a1c2856258a51e39aa716f8e67f2b16`. Runtime contract SHA-256 remains `85d8770839f80260cdc7c27b27b6cce6bf8815675c8593db68fb102589c5cbd6`; validation threshold lock raw SHA-256 is pinned in the notebook.
- Local bundle and notebook integrity checks passed; no Kaggle test inference has been launched. See `worklogs/2026-11-09_b3_nodiff_test_kaggle_delivery.md`.
