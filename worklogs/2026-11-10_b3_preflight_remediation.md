# B3 new-test preflight remediation - 2026-11-10

## Diagnosis

Version 2 failed in cell `In [2]` under a combined input-discovery guard. Version 4 added diagnostics and proved the test manifest lookup returned no candidates: Kaggle mounts data at `/kaggle/input/datasets/<owner>/<dataset>/`, while the notebook searched only immediate children `/kaggle/input/*`. The dataset listing itself contains the manifest and all seven package members. Both attempts stopped before dependency installation, model load, GPU/runtime attestation, and inference; no test samples were processed.

## Fix and deployment

Updated only the notebook preflight cell to recursively find the unique sealed manifest, resolve the package from its parent, validate either the expanded input directory or pinned archive, prefer the previously verified model-source path, and emit diagnostic candidate paths. The runtime lock, model, packages, worker, prompts, pools, and validation-fitted thresholds were preserved. Local syntax and manifest/archive/member/threshold hash checks passed.

Pushed canonical Kaggle kernel version 5. Remote readback confirms all five executable cell sources match local, including the recursive lookup. Latest check at 2026-11-09 22:19 UTC still reports `RUNNING`. Live output retrieval has not yet returned logs, so successful preflight, runtime attestation, and inference are not yet confirmed.

Evidence: `Runs-management/b3_verified_patch_v1/test_release_20261109_v1/audit/failure_diagnosis_20261110.md`, `audit/remote_source_verification_v5.json`, and versioned Kaggle output directories.
