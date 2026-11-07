# B2-rand test bundles and notebooks

## Fixed validation thresholds

The per-arm lock lives at `../config/threshold.json`. It covers only seeds 42 and 43, whose complete validation outputs were checked against every frozen ID, prompt hash, label, and model hash. Seed 44 is still incomplete and has no threshold entry.

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

## Resume B2-rand validation for seed 44

Open `../notebooks/02_kaggle_qwen_q4_b2_rand.ipynb`. Add the original `grace_b2_rand_inputs.zip`, the pinned model, and the latest checkpoint output from `Runs-management/kaggle_outputs_20261107/b2_rand_latest/grace_b2_rand_checkpoint.zip` (or upload that checkpoint as a Kaggle Dataset and attach it). The notebook selects the checkpoint with the largest verified history and checks the immutable I-11 prefix.

The latest checkpoint already contains 12,436/15,015 validation records: seeds 42 and 43 are complete; seed 44 has 2,426/2,732 Devign and 0/2,273 REVEAL. It should skip the first two seeds and resume the remaining 306 Devign rows, then run the 2,273 REVEAL rows. The nine-hour cap remains active. It stops after validation; it does not fit seed 44's threshold or start test.

After the run, download the new `grace_b2_rand_checkpoint.zip` and attach that checkpoint to the validation notebook for any further resume. Do not use a seed 42/43 test notebook as the validation notebook's checkpoint.

See `../config/threshold.json`, `delivery_manifest.json`, and `../../worklogs/2026-11-07_b1h2_b2rand_kaggle_progress_and_delivery.md` for hashes and run evidence.


## Shared runtime lock (2026-11-07)

Both test notebooks now embed and enforce configs/inference_runtime_lock.json. Upload the updated notebook only; the prompt ZIP/model Inputs stay the same. Setup checks packages and source archive SHA before CUDA build; inference verifies the model/tokenizer, applies the approved constructor and requires a 49/49 GPU offload report. Runtime provenance and contract hashes are exported. Previous checkpoints without this exact runtime contract identity are rejected. See worklogs/2026-11-07_b2_rand_test_runtime_lock_integration.md.
