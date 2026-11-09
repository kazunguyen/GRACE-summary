# B3 new-test preflight failures and correction - 2026-11-10

## Version 2

Kaggle reported `ERROR`; the log failed in cell `In [2]` with `Expected one private test release and pinned model dataset`. That guard combined three conditions and did not emit candidate counts, so the v2 log alone could not identify the failed condition. No inference began.

## Version 4: exact root cause

Version 4 added diagnostics. Its log showed:

- Kaggle top-level input roots: `/kaggle/input/datasets` and `/kaggle/input/notebooks`
- `manifest_candidates: []`
- Failure: `Expected exactly one B3 test manifest`

The test dataset is mounted below `/kaggle/input/datasets/<owner>/<dataset>/`, but the notebook searched only immediate children of `/kaggle/input`. Therefore it could not see the manifest. The published dataset file listing confirms `test_release_manifest.json` at the dataset root and the seven input members under `kaggle_input/`. The model discovery was never reached in this attempt.

## Impact

Both failures occurred before package installation, model load, GPU/offload attestation, and inference. No Devign or REVEAL test records were produced; no test sample was processed; no threshold was refit. These failures do not test the B3 algorithm.

## Version 5 correction

The notebook now recursively discovers the unique `test_release_manifest.json` below `/kaggle/input` and uses its parent as the release root. It validates either the expanded `kaggle_input/` tree or the exact-hash archive, prefers the previously verified pinned model-source path, verifies the model SHA-256, and prints candidate paths if resolution fails. The runtime lock, model, packages, worker, test prompts, retrieval pools, and validation-fitted thresholds remain unchanged. Local Python syntax and release-package hash checks pass. Version 5 has been pushed and read back with all five executable code cells matching local; Kaggle reports `RUNNING`. Live output is not available yet, so preflight and runtime have not been accepted.

Evidence: `failed_output_20261110_v1/grace-b3-new-test-20261109-v1.log` and `running_output_20261110_v4/grace-b3-new-test-20261109-v1.log`.
