# B1-H2 original test inference preparation — 2026-11-06

Prepared 5,006 test prompts (Devign 2,732; ReVeal 2,274) from the original Hiếu archive, using its `specs/{dataset}_test_15arms.jsonl` and original `h2_evidence` text with the same renderer and scaffold as validation. Target labels are removed before rendering and excluded from the bundle. Evidence is not reselected. The original archive SHA-256 was verified as `9db0d3eebb66a2f83c1f9803ceb0192954a3dfe2c3de9515188a996ede84ed7b`.

The bundle includes the already locked threshold config: Devign 0.09, ReVeal 0.67, seal `eedb783ebba986cec772bde2bdcca1cb95a2cd9db4bebd8141a44f49342178e5`. The notebook verifies the bundle SHA, prompt payload SHA, individual prompt hashes, threshold self-checksum, model SHA, tokenizer identity, context limit, and arm/split/seed. It records `pred_tau` using those fixed values without fitting thresholds on test.

- Bundle SHA-256: `c1557cdd26c2e59a5e2f77fee42cd94f6dc802558fbdd5a7745facc791257c24`.
- Drive folder: https://drive.google.com/drive/folders/1uoac8VUrFiZG8EVL8RZQE62A6kN4V-BA
- Bundle: https://drive.google.com/file/d/1fd8sscUUmeoSbiiwB7SHWeljytYwHMee/view
- Colab notebook: https://colab.research.google.com/drive/1xhB1z2TPP4o0kETce5vz7aVSEdFly0ee
- Local notebook: `11_Arm_B1H2_Evidence/notebooks/colab_l4_b1h2_test_20261106.ipynb`.

## Resume and output

Use Colab Runtime Version 2026.10 / Python 3.13.x and one L4, mounting the same Google Drive account. Outputs live in `MyDrive/GRACE_B1H2_COLAB_L4_TEST_20261106/l4_test_output/`. Each completed prompt is saved as a separate ID-hashed JSON under `checkpoints/`, using a temporary file, fsync, rename, and readback verification before advancing. Reconnecting and running from the top reloads and validates these records, then skips completed IDs. Only an interrupted in-flight sample needs recomputing. Truncated checkpoint JSON is quarantined for inspection and recomputed; mismatched prompt/model/threshold identity aborts.

The consolidated `records.jsonl` and `test_status.json` are rebuilt from validated records; individual checkpoints remain authoritative if the runtime is killed before finalization. A Drive write failure stops progress so completed-but-unpersisted work is not silently counted. The session cap is nine hours measured from setup, with an adaptive per-sample reserve; final export has additional room before the previously requested ten-hour budget. This does not prevent Colab idle/session eviction, which is why durable checkpoints are required.

## Logging and offload repair

All pip/compiler output, including verbose `Found link` messages, goes to full log files on local Colab disk and is copied to Drive. The notebook prints bounded progress summaries (CUDA build: every 2,000 captured lines; inference: every 50 records). Logs are retained separately under `sessions/{UTC_timestamp}/`, so reconnecting does not replace the previous session's logs.

The model-load log captures the explicit native `llama_log_set` callback and OS stdout/stderr file descriptors. It writes directly to local disk, fsyncs, then saves to Drive. The notebook also records post-load `nvidia-smi`. It parses `offloaded N/N layers to GPU` and blocks test inference unless the report is present and confirms all layers. Thus an empty or unverified load log cannot silently accompany a test run. Actual L4 offload is still to be established when this notebook executes on Colab.

## Local verification

All 5,005 original validation prompts were independently re-rendered from the archived specs and matched the supplied validation packet byte-for-byte (Devign 2,732; ReVeal 2,273). See `11_Arm_B1H2_Evidence/colab_l4_b1h2_test_20261106/full_validation_renderer_check.json`.

All generated code cells compile. A synthetic three-row execution checked initial checkpoint creation, resume with zero recomputation, quarantine/recomputation of a truncated checkpoint, and rejection of a checkpoint with a different threshold seal. See `11_Arm_B1H2_Evidence/colab_l4_b1h2_test_20261106/checkpoint_smoke_report.json`. The uploaded bundle and notebook were downloaded with gdrive and their SHA-256 hashes matched the local files. No L4 model execution or test inference occurred locally. The notebook and bundle have been uploaded; the actual test run is pending the user starting Colab.

The already documented platform deviation remains: Colab single L4 / runtime 2026.10 versus preregistered Kaggle 2×T4. Model/tokenizer/backend/package pins and the first-token scoring method are retained. Preparing this notebook is not a claim that OSF has accepted a platform amendment.
