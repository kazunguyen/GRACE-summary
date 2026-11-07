# B2-rand validation-only resume after I-11 — 2026-11-06

Updated and synchronized both active notebooks:

- `06_Arm_B2_Rand/notebooks/02_kaggle_qwen_q4_b2_rand.ipynb`
- `Runs-management/kaggle_validation_6arms_20261104/02_kaggle_qwen_q4_b2_rand.ipynb`

Use the original `grace_b2_rand_inputs.zip`, pinned GGUF Q4_K_M model, and **I-11 checkpoint or a verified descendant**. The local I-11 checkpoint is `06_Arm_B2_Rand/output/kaggle_run_02/grace_b2_rand_checkpoint.zip`, SHA-256 `96ad982e681a1c910be5290d4454e67899cae934421b8b648fd6e387e32052a3`. The older checkpoint in the original delivery directory is I-09 and is insufficient by itself for this continuation.

The notebook verifies preserved I-09 bytes and all 7,789 I-11 validation rows. If multiple checkpoint Inputs are attached, it selects the candidate containing the other candidates' record history; conflicting histories abort. Old completed IDs are skipped. Remaining work is 2,221 ReVeal seed 43, 2,732 Devign seed 44, and 2,273 ReVeal seed 44, total 7,226. Existing completed donor rerun data is preserved without inference.

Only six validation bundles are materialized; the driver schedules validation exclusively. A second gate inside the embedded runner rejects non-validation runs before importing/loading llama.cpp, so a direct test CLI call also fails. Completion sets `validation_complete`, `awaiting_threshold_lock=true`, `thresholds_fitted=false`, and `test_started=false`. The notebook does not select or seal thresholds and does not transition to test. The checkpoint archive is produced on completion, timeout, or inference failure reached inside the driver.

The nine-hour budget starts in the first setup cell and includes installation/build/model loading and checkpoint validation. Re-running setup in the same Python session does not reset it. New inference records stop ten minutes before the deadline. A subprocess watchdog kills the process group five minutes before the deadline if it overruns, leaving export time. If validation remains incomplete, resume again from the new checkpoint rather than assuming one session will finish all remaining prompts.

Model hash, Q4_K_M quantization, backend 0.3.16, tokenizer revision, batch 256, context 8,192, prompt content and prompt seeds 42/43/44 are preserved. Inference sampler seed remains the backend default, matching the prior B2-rand constructor. Dependency installation now explicitly pins the versions observed in the prior Kaggle run: NumPy 2.1.3, Transformers 4.57.1, Hub 0.36.2, tokenizers 0.22.2, scikit-learn 1.5.2. Build remains CUDA SM75 for T4. Checkpoint runtime identity checks remain enforced; a different Python runtime is not silently accepted.

Verification used the actual I-11 checkpoint and frozen prompt bundles with a simulated inference subprocess. It confirmed exactly 7,226 missing IDs scheduled, no completed rows re-inferred, preserved historical bytes, auto-selection of I-11 when I-09 is also attached, timeout without granting another nine hours after setup, unchanged threshold files, rejection of an I-09-only continuation, and direct CLI test rejection before model import. All code cells compile. See `06_Arm_B2_Rand/validation_resume_20261106/verification_report.json` and the reproducible `verify_resume.py` beside it. Actual GPU inference was not run locally.

The new notebook hash and delivery details are in `06_Arm_B2_Rand/validation_resume_20261106/delivery_manifest.json`. The original 04/11 delivery manifest is retained as a historical record.
