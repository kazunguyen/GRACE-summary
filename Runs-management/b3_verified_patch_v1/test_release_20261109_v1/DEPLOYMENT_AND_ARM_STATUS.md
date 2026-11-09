# B3 test deployment and other arm status

Checked 2026-11-09 16:08 UTC (23:08 Asia/Saigon). Kaggle status requests returned normally; the observed condition is queueing, not a server error.

## B3 new-algorithm test on lznt123

- The private input dataset `lznt123/grace-b3-test-release-20261109-v1` passed remote readback: the sealed manifest and all seven member hashes match, and test labels are absent from the Kaggle input.
- Canonical kernel `lznt123/grace-b3-new-test-20261109-v1`, version 2, was successfully pushed. Kaggle readback confirms all five executable code-cell sources match the sealed local notebook; the whole notebook hash differs because Kaggle normalizes metadata and the code filename. Its latest status is `QUEUED`.
- The earlier title-derived duplicate `lznt123/grace-b3-new-algorithm-test-devign-and-reveal` is `CANCEL_REQUESTED`; cancellation is not yet confirmed complete.
- No inference has started: there are no test records or runtime provenance from this release. Runtime acceptance remains pending. Do not treat `PUSHED` or `QUEUED` as evidence of execution.
- The previous push encountered Kaggle's two-session batch limit. The current version 2 push succeeded. The status endpoint currently responds normally.

## Other arms

| Arm | Current evidence | Status |
|---|---|---|
| B1-shuf test | All six seed/dataset groups completed: 15,018/15,018. Four runtime provenance sessions pass the locked six-package contract, full 49/49 layer offload on 2x Tesla T4, and constructor checks. | **Complete; runtime accepted under B1-shuf contract.** See `Runs-management/b1_shuf_kaggle_output_20261109/RUNTIME_ACCEPTANCE_20261109.md`. |
| B1-full test | 5,006/5,006, accepted under its six-package launch contract. | Complete; no rerun needed. |
| B3-new validation | Devign and REVEAL validation complete; runtime and threshold acceptance recorded under the seven-package contract. | Complete; no validation rerun needed. |
| B2-labelonly, B2-nolabel, B2-rep tests | Results exist, but previous acceptance records do not certify the full newer runtime lock. | Do not represent as fully runtime-certified. |
| Historical B3 test/validation | Separate from the verified-patch algorithm; no full retrospective runtime acceptance for inherited outputs. | Do not treat as the new-algorithm test. |
| B3-nodiff | Not included in the current B3-only test request. | No new run planned here. |

## Decision

B1-shuf is complete and runtime-accepted. The B3 test package and version 2 kernel are deployed, but execution remains queued and runtime is not yet attested. The latest Kaggle responses do not show a server error.
