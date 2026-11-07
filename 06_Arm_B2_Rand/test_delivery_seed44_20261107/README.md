# B2-rand seed 44 test delivery

Validation completed for seed 44: Devign 2,732/2,732; REVEAL 2,273/2,273. Thresholds were selected from validation only and locked before this test bundle was created:

| Dataset | tau | Validation MCC |
|---|---:|---:|
| Devign | 0.99 | 0.055851 |
| REVEAL | 0.64 | 0.089166 |

Threshold lock SHA-256: `48c12066bbddabc8ef674a70f6f9ac68cb74cbeecc2a5ebbbda3cb4cb6498735`. Runtime lock SHA-256: `bf1f859dc786e206a3c11d655b04b528dc68f59a15a82d4db894ac5944b0ac2e`.

## Run on Kaggle

1. Upload `grace_b2_rand_test_seed44_bundle.zip` as a Kaggle Dataset and attach it to the notebook.
2. Attach the same pinned Qwen3-Coder-30B-A3B-Instruct Q4_K_M model dataset as validation; select **GPU T4 ×2** and Internet on.
3. Run all cells in `02_kaggle_qwen_q4_b2_rand_seed44_test.ipynb`.

The Devign threshold uses all verified validation rows, including 2,426 carried from I-15 with the reviewed legacy-resume provenance; these rows are not retroactively relabeled as locked-runtime outputs. The notebook applies `configs/inference_runtime_lock.json`, validates every dependency and source hash, requests all 49 layers on GPU and aborts unless the load log proves 49/49. It accepts either the intact delivery ZIP or Kaggle's recursively extracted files, checking hashes before loading. It runs only seed44 test: Devign 2,732 and REVEAL 2,274. Test data is never used to fit thresholds.

The nine-hour time cap includes install, CUDA build, and model load; a five-minute reserve stops new records for export. Per-ID records are fsynced. To resume after interruption, attach the prior `grace_b2_rand_seed44_test_checkpoint.zip`; completed records are checked and skipped.
