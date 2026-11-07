# B2-rand test bundles and notebooks

> **Cập nhật 07/11/2026:** seed44 validation đã hoàn tất và ngưỡng đã khóa. Phần “Resume B2-rand validation for seed 44” phía dưới là ghi chú chuẩn bị lịch sử, không còn là bước cần làm. Để chạy test seed44 ngay, dùng thư mục mới [test_delivery_seed44_20261107](../test_delivery_seed44_20261107/) với bundle và notebook riêng. Seed42/43 test notebooks ở thư mục này vẫn giữ nguyên.

## Fixed validation thresholds

The per-arm lock lives at `../config/threshold.json`. It covers seeds 42, 43, and 44. Seed44 thresholds and delivery are documented in the separate folder linked above; the bundle here remains the earlier seed42/43 bundle with its original threshold-lock hash.

| Prompt seed | Dataset | Validation rows | Locked tau | Validation MCC |
|---:|---|---:|---:|---:|
| 42 | Devign | 2,732 | 0.99 | 0.066204 |
| 42 | REVEAL | 2,273 | 0.89 | 0.080819 |
| 43 | Devign | 2,732 | 0.99 | 0.061036 |
| 43 | REVEAL | 2,273 | 0.62 | 0.077064 |

Rule: maximize MCC on the 0.01–0.99 grid using finite valid validation scores; predict positive when `s >= tau`; ties within `1e-9` go closest to 0.5, then lower tau. Test records are not read when fitting these values.

## Run the two test notebooks

Upload `grace_b2_rand_test_seeds_42_43_bundle.zip` as a Kaggle Dataset. In both notebooks add that dataset and the same pinned GGUF Q4_K_M model dataset used for validation. Choose **GPU T4 ×2**, Internet on, then run all cells. The two notebooks are:

Kaggle may recursively extract the seed/dataset ZIPs inside the uploaded bundle. The notebooks accept either those extracted directories or intact nested ZIPs, check each frozen member hash, and rebuild a temporary local ZIP when the inference runner requires one. After replacing a notebook with the corrected local copy, upload/replace the Kaggle notebook version and rerun from the top; no new bundle upload is needed.

- `02_kaggle_qwen_q4_b2_rand_seed42_test.ipynb`
- `02_kaggle_qwen_q4_b2_rand_seed43_test.ipynb`

Each notebook accepts one seed and its complete two-dataset test census only. It loads the fixed threshold from the hash-locked bundle, scores logits directly, records one fsynced row per ID, and never fits or changes a threshold. It uses the B2-rand validation constructor settings: llama-cpp-python 0.3.16, default inference seed, `n_ctx=8192`, `n_batch=256`, `n_gpu_layers=-1`, and `logits_all=True`.

The nine-hour budget includes installs, CUDA build, and model loading; five minutes are held for export. If Kaggle disconnects the session, download that notebook's `grace_b2_rand_seed{42|43}_test_checkpoint.zip` output, upload it as a Kaggle Dataset, attach it, and run all cells again. The notebook verifies each saved record and skips completed IDs. Keep seed 42 and seed 43 outputs/checkpoints separate.

## Historical resume instructions for B2-rand validation seed 44 (completed by I-17)

At the time this note was written, the validation notebook was the planned continuation. I-17 later completed the remaining seed44 prompts. Do not use this resume note now; see `../test_delivery_seed44_20261107/README.md` for test execution.

I-17 completed all 15,015 validation rows. Seed44 tau was selected on validation and stored in the canonical lock; no test record was used to fit it.

Validation continuation is complete; no further seed44 validation resume is pending.

See `../config/threshold.json`, `delivery_manifest.json`, and `../../worklogs/2026-11-07_b1h2_b2rand_kaggle_progress_and_delivery.md` for hashes and run evidence.


## Shared runtime lock (2026-11-07)

Both test notebooks now embed and enforce configs/inference_runtime_lock.json. Upload the updated notebook only; the prompt ZIP/model Inputs stay the same. Setup checks packages and source archive SHA before CUDA build; inference verifies the model/tokenizer, applies the approved constructor and requires a 49/49 GPU offload report. Runtime provenance and contract hashes are exported. Previous checkpoints without this exact runtime contract identity are rejected. See worklogs/2026-11-07_b2_rand_test_runtime_lock_integration.md.
