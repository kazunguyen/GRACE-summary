# B3 new-test preflight remediation - 2026-11-10

## Diagnosis

Version 2 failed in cell `In [2]` under a combined input-discovery guard. Version 4 added diagnostics and proved the test manifest lookup returned no candidates: Kaggle mounts data at `/kaggle/input/datasets/<owner>/<dataset>/`, while the notebook searched only immediate children `/kaggle/input/*`. The dataset listing itself contains the manifest and all seven package members. Both attempts stopped before dependency installation, model load, GPU/runtime attestation, and inference; no test samples were processed.

## Fix and deployment

Updated only the notebook preflight cell to recursively find the unique sealed manifest, resolve the package from its parent, validate either the expanded input directory or pinned archive, prefer the previously verified model-source path, and emit diagnostic candidate paths. The runtime lock, model, packages, worker, prompts, pools, and validation-fitted thresholds were preserved. Local syntax and manifest/archive/member/threshold hash checks passed.

Pushed canonical Kaggle kernel version 5. Remote readback confirms all five executable cell sources match local, including the recursive lookup. Latest check at 2026-11-09 22:19 UTC still reports `RUNNING`. Live output retrieval has not yet returned logs, so successful preflight, runtime attestation, and inference are not yet confirmed.

Evidence: `Runs-management/b3_verified_patch_v1/test_release_20261109_v1/audit/failure_diagnosis_20261110.md`, `audit/remote_source_verification_v5.json`, and versioned Kaggle output directories.


## Follow-up: v5 actual failure and v6 correction

- Used the lznt123 Kaggle config and retrieved v5 output. Version 5 did **not** fail manifest discovery: it passed the sealed manifest, 5,006 prompt rows, validation threshold locks, model file hash, package pins, and 2x T4 enumeration.
- Exact failure: `NameError: INPUT_DIR is not defined` in cell `In [5]`; zero worker inference records. Actual native model load, 49/49 offload, and runtime provenance were not reached.
- Compared the test launch cell with prior validation's worker/coordinator interface. Fixed the mismatch by defining `INPUT_DIR` on the expanded-input path and implementing safe, hash-verified materialization on archive-only input. Also made manifest discovery explicitly match Kaggle's pinned `/datasets/<owner>/<dataset>` mount and symlink-following fallback.
- Only preflight/input staging logic changed; runtime/build/GPU and inference code cells remain unchanged from remote v5. Syntax and variable-binding checks passed. v6 is local only pending Kaggle push/readback.
- Full evidence: `Runs-management/b3_verified_patch_v1/test_release_20261109_v1/audit/failure_diagnosis_20261110.md`; raw log `live_output_v5/grace-b3-new-test-20261109-v1.log`.


### Version 6 deployment/readback

- Pushed the corrected notebook to canonical `lznt123/grace-b3-new-test-20261109-v1`; Kaggle accepted version 6 and reported `RUNNING`.
- Pulled the remote source into `remote_source_readback_v6/`; all 5/5 executable code-cell sources exactly match local. Verification receipt: `audit/remote_source_verification_v6.json`.
- This is source/readback acceptance only. Wait for v6 live output to establish all-member preflight, model loading, native CUDA offload 49/49 across 2x T4, runtime provenance, and inference progress before claiming runtime acceptance.
