# B1-H2 test on Kaggle - 9 hours

Delivery for the completed Kaggle validation run, with fixed thresholds **Devign 0.09** and **ReVeal 0.21**. Runs 2,732 Devign and 2,274 ReVeal test prompts (5,006 total).

## Start on Kaggle

1. Upload `grace_b1_h2_test_inputs.zip` as a private Kaggle Dataset and attach it to the notebook. Kaggle may retain the outer ZIP, expose the two inner ZIPs, or extract all files: the loader accepts all three layouts after verifying pinned member hashes.
2. Import `02_kaggle_qwen_q4_b1_h2_test_20261106.ipynb`. Set **Accelerator: GPU T4 x2** and **Internet: On**. The notebook checks that exactly two T4 GPUs are present.
3. Attach the same GGUF model input as validation: `Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf`. The existing source is the output of `quangdung1111/qwen3coder30b-prepare-notebook`. Model discovery searches attached inputs and requires one exact filename and the registered SHA-256.
4. For the first session, attach no checkpoint. Select **Run All** (or **Save Version / Run All** to preserve Kaggle Output).
5. Download `grace_b1_h2_test_checkpoint.zip` and `grace_diagnostics.zip` from Output. In the checkpoint, `batch_summary.json` must say `test_complete` with `42/devign=2732`, `42/reveal=2274` before reporting the entire test census as complete.

## Resume after the budget or an interrupted session

Keep the same input bundle and model. Attach the most recent **test** checkpoint `grace_b1_h2_test_checkpoint.zip` as an additional input and rerun the notebook from the start. It validates IDs, prompt hashes, model/environment identity, inference seed and threshold seal before skipping completed samples. A validation checkpoint or a checkpoint from the earlier Colab run is not interchangeable with this run. If more than one test checkpoint is attached, set `CHECKPOINT_INPUT_PATH` explicitly in the configuration cell.

Within the same Kaggle runtime, existing output is resumable directly. Detach the imported checkpoint when continuing existing `/kaggle/working/b1_h2_test/` output; the notebook refuses to overwrite local records with an imported archive. Corrupt JSON or conflicting records cause an explicit error for inspection.

## Time limit and saved results

- The first executable line prints `[PING] B1-H2 notebook: Python execution started`, before disk access, dependency installation or GPU probing. A daemon thread prints `[PING] ... kernel_alive ... stage=...` every 30 seconds, including when the foreground is waiting for a child process. Stage changes print immediately. The GPU startup probe has a 30-second timeout. The heartbeat stops on a cell error or after the final export and does not duplicate when the first cell is rerun.
- PING establishes Python kernel liveness, not GPU progress. It cannot run while Kaggle is still allocating a runtime or before the first cell starts, and live display still depends on Kaggle delivering stdout to its viewer. A hard kernel kill or a native operation that holds the Python GIL can stop the heartbeat.
- The wall-clock budget is **9 hours from the first code cell**, including setup and installation. No new inference starts during the last 5 minutes; the runner additionally accounts for recent sample durations. A subprocess watchdog leaves 2 minutes for export if a subprocess hangs.
- Each completed record is flushed and fsynced. A downloadable checkpoint ZIP is refreshed after 100 completed records or 120 seconds between checkpoint updates; finalization refreshes the ZIP again on completion, timeout or an inference error. An abrupt platform kill can prevent final export, so retain Kaggle Output and the latest available checkpoint.
- Outputs are under `/kaggle/working/b1_h2_test/seed_42/{dataset}/test/`: `records.jsonl`, `run_manifest.json`, and `evaluation.json` after that dataset is complete. Dataset metrics use the fixed validation threshold on **all score-valid rows**, including rows whose raw greedy response is not a digit. Partial output is a checkpoint, not a completed census.
- `records.jsonl` includes both label logprobs, continuous `s`, raw response validity, `tau`, `pred_tau`, threshold seal, model/tokenizer identity, inference seed and per-sample timing. Labels are offline evaluation metadata; only the unchanged `prompt` text is passed into the model.

## Match to the completed validation run

Uses the original Hiếu B1-H2 prompts, without selecting new H2 evidence or substituting later v5/v6 candidates. Preparation verified that all **5,005 original validation prompt texts** match the Kaggle validation inputs and retained all 5,006 original test prompt texts exactly. Test labels are joined by frozen source ID.

- Model: Qwen3-Coder-30B-A3B-Instruct GGUF Q4_K_M; SHA-256 `f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335`.
- Tokenizer revision: `b2cff646eb4bb1d68355c01b18ae02e7cf42d120`.
- Backend: `llama-cpp-python==0.3.16`; Transformers 4.57.1; Hugging Face Hub 0.36.2; tokenizers 0.22.2; NumPy 2.1.3; scikit-learn 1.5.2.
- Inference: first-token full-vocabulary logits, context 8,192, batch 256, all GPU layers requested, layer split `[1.0, 1.0]` over two T4s.
- Prompt-set seed is **42**. Inference uses **`LLAMA_DEFAULT_SEED=4294967295`**, matching the executed Kaggle validation helper. This differs from a manually set RNG seed of 42; both identities are recorded.
- Validation threshold seal: `b5dc7e0da070f75cfabc10c366a08675d1c3f471f1e11fb86ee826a22ce674f8`. Included locks are authenticated before test execution. No threshold fitting routine is present in the test runner.
- Input bundle SHA-256: `991f75e55646ff68db0436c409e2866a06f32f7c045e0cd4d9865199588f8fdc`.

See `delivery_manifest.json` for artifact hashes and `verification_report.json` for CPU checks. Real GPU offload, throughput and final completion will be established by the Kaggle execution logs; none was executed during preparation.

Rebuild from the repository root with `python 11_Arm_B1H2_Evidence/prepare_kaggle_b1h2_test.py`. Run the isolated CPU checks with `python 11_Arm_B1H2_Evidence/kaggle_b1h2_test_20261106/verify_delivery.py`.
