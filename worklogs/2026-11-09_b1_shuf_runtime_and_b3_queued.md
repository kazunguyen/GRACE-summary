# B1-shuf runtime acceptance and B3 test queue - 2026-11-09

## B1-shuf

Pulled the latest output from `lznt123/grace-b1-shuf-resume-12290-20261109`. Kaggle reports `COMPLETE`, and `status.json` reports `complete`. All six registered seed/dataset groups have their full census: Devign 2,732 and REVEAL 2,274 for seeds 42, 43, and 44 (15,018 records total).

Audited the pinned runtime contract SHA-256 `85d8770839f80260cdc7c27b27b6cce6bf8815675c8593db68fb102589c5cbd6`, canonical contract seal, record-to-provenance links, six package versions, model/runner/helper/source hashes, constructor, Linux/Python 3.13 provenance, two Tesla T4 devices, and native offload/context logs for all four sessions. All pass the contract's 49/49 layer offload and 2xT4 checks. Exact compiled backend binary hashes are recorded by Kaggle but could not be independently re-hashed locally because the binaries are not part of downloadable output. The contract allows a Kaggle platform build and makes no bit-identical binary claim.

Verdict: **B1-shuf complete and runtime-accepted under its locked contract.** Full evidence: `Runs-management/b1_shuf_kaggle_output_20261109/RUNTIME_ACCEPTANCE_20261109.md`.

## B3 new-algorithm test

Verified the existing private test dataset readback and pushed canonical kernel `lznt123/grace-b3-new-test-20261109-v1` version 2. Readback verified all five executable cell sources. Latest Kaggle status check at 2026-11-09 16:08 UTC: canonical version 2 `QUEUED`; earlier title-derived duplicate `CANCEL_REQUESTED`. The Kaggle status endpoint responded normally, so no server error was observed. No test inference or runtime attestation has started.

The earlier push had hit the two-session limit; the version 2 push succeeded. Do not treat a successful push or queue state as a running/completed test. Keep the B3 execution exploratory/amended relative to the public OSF registration unless a formal amendment is submitted.

Evidence and live status: `Runs-management/b3_verified_patch_v1/test_release_20261109_v1/DEPLOYMENT_AND_ARM_STATUS.md`, `execution_manifest.json`, and `TEST_RELEASE_READINESS.md`.
