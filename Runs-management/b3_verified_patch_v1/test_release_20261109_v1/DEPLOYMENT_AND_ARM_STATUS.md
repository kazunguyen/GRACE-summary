# B3 test deployment and other arm status

Checked 2026-11-09 22:19 UTC (2026-11-10 05:19 Asia/Saigon). Kaggle status and output requests returned normally.

## B3 new-algorithm test on lznt123

- The private input dataset `lznt123/grace-b3-test-release-20261109-v1` is intact: remote readback confirms the sealed manifest and all seven member hashes; target labels are absent from the Kaggle input.
- Canonical kernel version 5 has been pushed. Remote readback confirms all five code-cell sources match the fixed local notebook, including recursive manifest discovery. Kaggle reports `RUNNING`.
- Version 4 stopped in preflight before package installation, model load, GPU/offload attestation, or inference. No test records exist and no test sample was processed. The earlier version 2 also stopped at the combined preflight guard.
- Version 5 fixes the mount discovery. The current live output endpoint has not exposed logs while the run is active, so successful preflight, GPU/runtime attestation, and inference are not yet confirmed. Runtime lock, model, worker, prompts, pools, and validation-fitted thresholds are unchanged.
- The earlier title-derived duplicate `lznt123/grace-b3-new-algorithm-test-devign-and-reveal` remains `CANCEL_REQUESTED`; cancellation is not confirmed. Runtime attestation for B3 test is pending; current output logs are not yet available.

See `audit/failure_diagnosis_20261110.md`, version 4 log under `running_output_20261110_v4/`, and version 5 readback under `audit/remote_source_verification_v5.json`.

## Other arms

| Arm | Current evidence | Status |
|---|---|---|
| B1-shuf test | All six seed/dataset groups completed: 15,018/15,018. Four runtime provenance sessions pass the locked six-package contract, full 49/49 layer offload on 2x Tesla T4, and constructor checks. | **Complete; runtime accepted under B1-shuf contract.** See `Runs-management/b1_shuf_kaggle_output_20261109/RUNTIME_ACCEPTANCE_20261109.md`. |
| B1-full test | 5,006/5,006, accepted under its six-package launch contract. | Complete; no rerun needed. |
| B3-new validation | Devign and REVEAL validation complete; runtime and threshold acceptance recorded under the seven-package contract. | Complete; no validation rerun needed. |
| B2-labelonly, B2-nolabel, B2-rep tests | Results exist, but prior acceptance records do not certify the full newer runtime lock. | Do not represent as fully runtime-certified. |
| Historical B3 test/validation | Separate from the verified-patch algorithm; no full retrospective runtime acceptance for inherited outputs. | Do not treat as the new-algorithm test. |
| B3-nodiff | Not included in the current B3-only test request. | No new run planned here. |

## Decision

B1-shuf is complete and runtime-accepted. B3 version 5 is running with source readback verified. Wait for live logs to confirm the preflight and runtime checks before treating inference as started.
