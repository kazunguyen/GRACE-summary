# Kaggle progress and B2-rand test delivery — 2026-11-07

## Latest downloaded outputs

Fetched outputs with the requested Kaggle CLI commands into `Runs-management/kaggle_outputs_20261107/`:

- `b1h2_test_latest/`: `duchuynguyen1802/02-kaggle-qwen-q4-b1-h2-test-20261106-ipynb`
- `b2_rand_latest/`: `duchuynguyen1802/02-kaggle-qwen-q4-b2-rand-ipynb`

### B1-H2 test — complete

The downloaded Kaggle notebook papermill metadata reports Python 3.13.16, T4 accelerator, execution 2026-11-06 17:04:35–19:40:00 UTC. `seed_42_status.json` records the inference worker from 17:22:41 to 19:39:54 UTC, complete without timeout. At GMT+7 the inference worker ran 2026-11-07 00:22:41–02:39:54.

The output checkpoint has all **5,006/5,006** test records: Devign 2,732 and REVEAL 2,274. Each record ID, label, prompt hash, and model SHA was matched against the exact bundles exported by Kaggle. Every numeric score is finite. There are 306 invalid raw responses (150 Devign, 156 REVEAL), retained with scores. Test used the Kaggle validation lock at tau Devign 0.09 / REVEAL 0.21; no threshold was refit on test. Native runtime log confirms 49/49 model layers offloaded to GPU and context/batch 8,192/256.

Metrics at the inherited thresholds:

| Dataset | AUROC | MCC | Balanced accuracy | Response-valid |
|---|---:|---:|---:|---:|
| Devign | 0.547685 | 0.065478 | 0.532370 | 2,582/2,732 |
| REVEAL | 0.595637 | 0.109270 | 0.587624 | 2,118/2,274 |

Notebook metadata says `isGpuEnabled=false` despite `accelerator=nvidiaTeslaT4`; the saved GPU probe and native offload log confirm the actual completed run used GPU. New B2-rand test notebooks explicitly set GPU enabled in Kaggle metadata.

### B2-rand validation — partial, validation-only

The latest local notebook metadata identifies Python 3.13.15, T4 accelerator, papermill start 2026-11-06 15:22:02 UTC, end 2026-11-07 00:12:11 UTC. Its single 9-hour batch session is `timed_out`, `validation_only=true`, `test_started=false`; within the session the runner completed seed 43 and then worked on seed 44. Native logs for both run processes show 49/49 layers offloaded.

| Prompt seed | Devign validation | REVEAL validation | State |
|---:|---:|---:|---|
| 42 | 2,732/2,732 | 2,273/2,273 | Complete |
| 43 | 2,732/2,732 | 2,273/2,273 | Complete |
| 44 | 2,426/2,732 | 0/2,273 | Incomplete |

Lũy kế **12,436/15,015 validation**; còn **2,579**, gồm 306 Devign + 2,273 REVEAL seed 44. Validation records of seeds 42 and 43 were fully matched by ID, label, prompt hash, and model hash to the frozen bundle. Raw-invalid counts are 2 for seed 42 REVEAL, 0 for seed 43, and 0 among seed 44's partial records; numerical scores are valid.

The saved notebook also had `isGpuEnabled=false` despite a T4 accelerator and actual two-T4 execution logs. Both active validation notebook copies now set `isGpuEnabled=true` and explain the I-12 checkpoint status. Resume from `grace_b2_rand_checkpoint.zip` downloaded in this worklog's output directory; the notebook checks the I-11 prefix, skips complete seed 42/43, and schedules only the 2,579 missing seed 44 validation rows. It remains validation-only with a nine-hour cap and does not fit thresholds or start test.

## Thresholds locked from complete validation

Created the arm-specific `06_Arm_B2_Rand/config/threshold.json`; the preregistered global `configs/thresholds.json` and its flat mirror were not modified. The lock uses the project MCC grid rule: tau 0.01–0.99 step 0.01, finite valid validation scores, positive prediction for `s >= tau`, ties within `1e-9` closest to 0.5 then lower tau. Each prompt seed × dataset has an independent entry.

| Prompt seed | Dataset | N | tau | Validation MCC |
|---:|---|---:|---:|---:|
| 42 | Devign | 2,732 | 0.99 | 0.0662037324 |
| 42 | REVEAL | 2,273 | 0.89 | 0.0808188331 |
| 43 | Devign | 2,732 | 0.99 | 0.0610358927 |
| 43 | REVEAL | 2,273 | 0.62 | 0.0770637527 |

Threshold lock SHA-256: `8df76b64817d864b5cea0c039f7434b2a4a3523814703180d898f2ff56254b70`. Seed 44 is absent until its validation census is complete. No test input/records were used to calculate these thresholds.

## Test delivery prepared

Created one shared test ZIP for the four frozen test prompt bundles for seeds 42 and 43, with their hash-sealed validation lock: `06_Arm_B2_Rand/test_delivery_20261107/grace_b2_rand_test_seeds_42_43_bundle.zip` (SHA-256 `703f7de196be9844ee8f69a675504afc311c6f23c8c50e82e21e984b36acd465`). The prompts are copied byte-for-byte from the existing frozen input archive; only wrapper metadata adds the test tau and lock digest.

Created two separate, resumable Kaggle notebooks:

- `06_Arm_B2_Rand/test_delivery_20261107/02_kaggle_qwen_q4_b2_rand_seed42_test.ipynb`
- `06_Arm_B2_Rand/test_delivery_20261107/02_kaggle_qwen_q4_b2_rand_seed43_test.ipynb`

They share the bundle but each accepts only one prompt seed and its complete test census. They verify the threshold lock and model/prompt hashes, fsync one row per ID, stop at the nine-hour wall-clock cap with a five-minute checkpoint-export reserve, and can resume from the matching seed's checkpoint. The llama.cpp constructor follows B2-rand validation: version 0.3.16, default inference seed, n_ctx=8192, n_batch=256, n_gpu_layers=-1, logits_all=True; no test threshold fitting. The notebooks have not been run on Kaggle.

See `06_Arm_B2_Rand/test_delivery_20261107/README.md` for Kaggle upload, attachment, run, and resume steps.
