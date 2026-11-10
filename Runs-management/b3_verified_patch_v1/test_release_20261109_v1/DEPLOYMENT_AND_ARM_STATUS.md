# B3 test deployment and arm status

Checked 2026-11-10 00:16 UTC (07:16 Asia/Saigon). Kaggle status/output checked with the lznt123 account config.

## B3 new-algorithm test on lznt123

- Private release `lznt123/grace-b3-test-release-20261109-v1`: sealed manifest and seven input-member hashes verified; test labels remain outside Kaggle input.
- Canonical kernel `lznt123/grace-b3-new-test-20261109-v1`, v6: Kaggle reports `RUNNING`; source readback confirms all 5 executable code cells match local.
- Latest output request returned no files. Therefore no v6 worker progress, model load, 49/49 offload, runtime provenance, or inference records are currently observable. Do not treat RUNNING/readback as runtime acceptance.
- v5 passed preflight and environment checks but failed at worker launch with `NameError: INPUT_DIR`; worker did not start and wrote zero records. v6 repairs this binding for expanded and archive-only mounts. Versions 2 and 4 failed earlier in preflight.
- Duplicate kernel `lznt123/grace-b3-new-algorithm-test-devign-and-reveal` remains `CANCEL_REQUESTED`; cancellation is not confirmed.

## Other current arms

| Arm/work | Latest evidence | Status |
|---|---|---|
| B1-shuf test | 15,018/15,018; two T4, 49/49; accepted under its six-package contract | COMPLETE / runtime accepted |
| B1-full test | 5,006/5,006; accepted under its recorded launch contract | COMPLETE |
| B3 verified-patch validation | Devign 2,732 + REVEAL 2,273; runtime and threshold audit complete | COMPLETE; tau*=0.99 / 0.01 locked in separate amended release |
| B3 verified-patch test | v6 source readback 5/5; Kaggle `RUNNING`; output endpoint empty | IN PROGRESS; acceptance pending |
| B3-swap / B3-flip | No separate verified-patch test bundle | NOT PREPARED FOR GPU LAUNCH |
| B3-nodiff | No current test bundle; user excluded it from current run scope | EXCLUDED |
| B2-nolabel / B2-labelonly / B2-rep | Full test outputs exist; current acceptance summary lacks full newer-runtime certification | CENSUS COMPLETE; retrospective provenance audit pending |

See [full arm matrix and required next steps](../../ARM_STATUS_AND_REMAINING_WORK_20261110.md), [failure diagnosis](audit/failure_diagnosis_20261110.md), and [v6 readback verification](audit/remote_source_verification_v6.json).
