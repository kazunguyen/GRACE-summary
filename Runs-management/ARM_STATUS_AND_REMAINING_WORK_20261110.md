# GRACE arm execution status and remaining work

**Checked:** 2026-11-10 00:16 UTC (07:16 Asia/Saigon). Kaggle CLI was queried with the `lznt123` account config. This document separates census completion from runtime acceptance; a complete result is not automatically a certified runtime.

## Latest runtime reconciliation and B3-swap deployment

Updated late 2026-11-10: [session-by-session runtime report](runtime_session_reconciliation_20261110/REPORT.md) now closes the retrospective audit work to the extent supported by current artifacts. Six B2-nolabel/labelonly/rep test processes match all 15,018 records, but lack native placement/full provenance. Four B2-rand test sessions are reconciled to all final records; original source/lock bytes are recovered from Git blobs, while native/build logs remain to be restored. Two historical B3 resume sessions pass launch-runtime checks for exactly 976 referenced records; the 4,029 inherited rows remain outside full-lock certification.

B3-swap was submitted as private `thanhduy9a4tv/grace-b3-swap-test-20261110-v1`. All four account configs were checked: only Thanh Duy had positive GPU quota (about 30 hours). Versions 1 and 2 were submitted; latest observed state is QUEUED. Further push attempts were rejected by the server with `Maximum batch GPU session count of 2 reached.` Session cancellation is unconfirmed because the public API does not expose the required session ID. See [deployment status](b3_swap_launch_20261110/STATUS.md). No B3-swap runtime acceptance yet.

## Earlier run-state snapshot (07:16 Asia/Saigon)

| Work item | Current evidence | State |
|---|---|---|
| B3 new algorithm, Devign + REVEAL test | Canonical kernel `lznt123/grace-b3-new-test-20261109-v1`, v6. Kaggle status `RUNNING`; remote source readback matches all 5 executable cells. Latest output request returned no files. | **In progress; 0 v6 records observed.** Runtime acceptance and inference progress are pending output. |
| Prior duplicate B3 test kernel | `lznt123/grace-b3-new-algorithm-test-devign-and-reveal` | `CANCEL_REQUESTED`; terminal cancellation is not confirmed. Do not launch a duplicate against it. |
| B1-shuf continuation | `lznt123/grace-b1-shuf-resume-12290-20261109` | `COMPLETE`; downloaded census 15,018/15,018 and runtime acceptance documented. |
| B3 new validation | `lznt123/grace-b3-checkpoint-resume-v2` and `lznt123/grace-b3-new-dual-linuxfix-20261109` | Both `COMPLETE`; accepted Devign 2,732/2,732 and REVEAL 2,273/2,273 validation records under the amended B3 contract. |

### B3 test version history

- v2 and v4 failed before inference during input preflight.
- v5 passed the sealed input, model hash, prompt/threshold, package, and two-T4 checks, then failed in cell `In [5]` with `NameError: INPUT_DIR`; the worker did not start and wrote no scores.
- v6 defines the worker input directory for expanded and archive-only input. It was pushed and read back exactly. `RUNNING` and source readback do not yet prove model load, 49/49 layer offload, runtime provenance, or inference.
- Runtime attestation for v6 requires the exact package/build/model/tokenizer checks, two T4 GPUs, 49/49 offloaded layers, matching runtime provenance and logs, then identity-valid census records. Do not join test labels before score download and integrity checks; do not refit thresholds on test.

Evidence: [deployment status](b3_verified_patch_v1/test_release_20261109_v1/DEPLOYMENT_AND_ARM_STATUS.md), [failure diagnosis](b3_verified_patch_v1/test_release_20261109_v1/audit/failure_diagnosis_20261110.md), [v6 source readback](b3_verified_patch_v1/test_release_20261109_v1/audit/remote_source_verification_v6.json), [execution manifest](b3_verified_patch_v1/test_release_20261109_v1/execution_manifest.json).

## Arm matrix

?Census complete? means the listed records exist in local output/handoff artifacts at expected coverage. Runtime acceptance is tracked separately.

| Arm | Data/output status | Runtime / follow-up |
|---|---|---|
| B0 | Full census historically recorded; current audit directly reads 5,005 validation rows and saved I-03 output. | Native/core evidence for I-03; restore raw test/checkpoint. Full new lock not certified. |
| B1 | Full census historically recorded; 5,005 current validation rows are carried from I-07. | I-08 native log cannot certify I-07 rows. Restore session-specific logs/test checkpoint. |
| B1-full | Test 5,006/5,006. | Test launch contract accepted separately. Validation core/native matches, full validation provenance incomplete. |
| B1-H2 | Kaggle validation 5,005 and test 5,006 have matching saved-session timestamps/native 49/49. | Full lock not certified; test manifest records fixed tensor_split=[1,1]. Colab remains separate. |
| B1-shuf | Test 15,018/15,018 runtime-accepted. | Validation audit binds only 2,892 rows to the reviewed seed44 log; 12,123 validation rows need their own logs. Test acceptance is unchanged. |
| B2 | Full 10,011 original records plus 66 donor corrections stored separately. | I-05 native output binds 1,297 fresh rows; I-02/I-04/correction source sessions require their own logs. |
| B2-rand | Validation 15,015 and test 15,018 census complete. | All final test records exactly assigned to 4 sessions; source/lock recovered from Git. Restore each native/build log before full runtime recertification. Mixed 6/7-package REVEAL head/tail profiles remain explicit. |
| B2-nolabel | Test 5,006/5,006; two processes fully reconciled to records/logs. | PARTIAL_CORE_MATCH_NOT_FULL_LOCK. Build wheel/CMake recovered; test native/full provenance absent. Validation native evidence remains separate. |
| B2-labelonly | Test 5,006/5,006; two processes fully reconciled to records/logs. | PARTIAL_CORE_MATCH_NOT_FULL_LOCK. Build wheel/CMake recovered; test native/full provenance absent. Validation native evidence remains separate. |
| B2-flip | Full census historically recorded; saved I-10 native 49/49 output exists. | Raw I-06/I-10 result paths are not currently available; restore records/checkpoints. Full lock not certified. |
| B2-rep | Test 5,006/5,006; all repeat/tag flags and two processes verified. | PARTIAL_CORE_MATCH_NOT_FULL_LOCK. Record/log/time matching passes; test native/full provenance absent. |
| B3, historical algorithm | Validation 5,005; 976 resume records have verified session provenance. | PASS launch runtime only for 29+947 rows. 4,029 original rows have core/native evidence but no full contract chain. |
| B3, verified-patch-v1 | Validation complete: Devign 2,732/2,732; REVEAL 2,273/2,273. | Runtime accepted for the score-producing sessions. Separate amended threshold locks: Devign tau*=0.99; REVEAL tau*=0.01. Classified `AMENDED_EXPLORATORY_SUBPROTOCOL`, not an OSF preregistered lock. |
| B3-nodiff | User update on 2026-11-10: Dũng has also run this arm. | Execution reported by user; output, version, split/census, independent validation threshold and runtime acceptance must be reconciled with Dũng's artifacts. The earlier exclusion described a prior launch scope. |
| B3-swap | Submitted on thanhduy9a4tv with all 5,006 test prompts; source readback matches. | Latest observed QUEUED; extra pushes rejected at 2 batch GPU sessions. Runtime acceptance pending. |
| B3-flip | Prepared 2026-11-10: complete 5,006-target paired prompt delivery; notebook also placed at `16_Arm_B3_Flip/kaggle_kernel/`. | LOCAL READY; 9 probe delivery tests pass. Upload/source readback/GPU runtime acceptance pending. Inherits B3 threshold. |

Older rendered/validation artifacts for variants are not a substitute for a sealed test delivery built from the current verified-patch B3 pair selector and current test census.

## Remaining work and hard checks

### 1. Finish and accept B3 verified-patch test (currently running)

**Already available:** sealed private test release for 5,006 targets; labels kept outside Kaggle input; seven pinned input members; B3 validation threshold locks; pinned model/runtime contract; test-only worker; v6 notebook; remote source readback 5/5.

**Still required:**

1. Obtain terminal output/checkpoint and determine whether the worker actually started. Never use API `RUNNING` as evidence of progress or acceptance.
2. Verify manifest and every member hash, worker/runtime-lock hashes, model SHA and tokenizer revision on the run that produced records.
3. Verify exact package versions, CUDA source/build hashes, two Tesla T4 identities, effective constructor and 49/49 GPU layer offload from native logs/provenance.
4. Validate record uniqueness and expected 2,732 Devign + 2,274 REVEAL census, scores against logits, prompt/worker/model/runtime/threshold identities, and checkpoint integrity. If interrupted, resume only from verified matching checkpoint; do not overwrite or rerun completed IDs.
5. Only after downloading and validating score-only outputs, join the held-out labels locally and compute test metrics at the already locked thresholds. Never tune on test.

### 2. B3-swap and B3-flip separate test deliveries (local preparation passed)

**Available:** locked B3 thresholds; current selector/pool and reviewed pair; full separate prompt deliveries, shared worker and notebooks in `probe_test_release_20261110_v1/`. Prompt/census checks and 9 acceptance tests pass. Reference audit matches the core runtime/scorer in all five original locked notebooks; the current lock adds the documented SciPy pin. Remote upload, exact source readback and GPU runtime acceptance remain pending.

**Required prompt semantics:** for each target use the same verified-patch B3-selected pair, target code/graph, and `Key difference` content as B3. Render a separate prompt and hash for each arm:

- B3-swap reverses the two demonstration blocks while keeping each label attached to its original code.
- B3-flip keeps the order and code blocks but reverses both demonstration labels and flips label words in `Key difference` via the existing `_flip_words` renderer. The former requirement to preserve that text byte-for-byte was inaccurate for flip.

**Before a teammate launches either arm, check:**

1. Generate the full Devign 2,732 and REVEAL 2,274 target census from the current B3 test selection; do not use historical pair selections or select a different donor pair for the variant.
2. Prove the only change from the paired B3 prompt is the specified order/label manipulation; preserve target fields, graph and pair IDs. Preserve `Key difference` for swap; apply the registered label-word flip for flip.
3. Prove no target labels or label-derived fields enter prompts/input; keep test labels private.
4. Audit exact-tokenizer counts, Figure 6 section order, per-component/context limits, unique IDs, prompt hashes, and expected row counts.
5. Pin a separate variant manifest/archive and worker/runner hashes; verify the runner supports the arm ID and never reads a B3 response cache.
6. Load B3's sealed dataset-specific threshold locks byte-for-byte (Devign 0.99, REVEAL 0.01); do not optimize thresholds on variant validation/test.
7. Attach the private release/model to the execution account, verify T4 x2 configuration, and read back the exact notebook source before launch. Runtime acceptance still requires logs/provenance and 49/49 offload.

Only after these checks pass is the arm ready for GPU execution. Prompt-generation/CPU auditing can be delegated now; GPU launch is a separate gate.

### 3. B3-nodiff execution reported by user

The user confirmed on 2026-11-10 that Dũng has run B3-nodiff. Obtain the actual version, outputs, split/census, validation-derived threshold lock and runtime provenance before accepting it. It cannot inherit B3's threshold under the stated protocol. This supersedes the prior launch-scope exclusion; execution reported by the user is not itself runtime acceptance.

### 4. Retrospective runtime audit for completed legacy outputs

This reconciliation has now been performed: see [the detailed report](runtime_session_reconciliation_20261110/REPORT.md), session ledger, raw artifact hashes and recovered evidence. B2-nolabel/labelonly/rep retain partial-runtime status; missing native placement cannot be supplied by their validation logs. B2-rand has exact source-session assignment but needs original native/build logs restored. Historical B3 has a 976-row launch-runtime acceptance subset. Restore the specific remaining artifacts listed in the report; do not rerun merely to fill documentation gaps without a separately justified run scope.

## Current handoff recommendation

- **Run already underway:** B3 verified-patch test v6. Handoff monitoring, checkpoint/output collection, and runtime/result acceptance; do not create another B3 base run.
- **B3-flip handoff:** full local preparation is complete; remote deployment/runtime acceptance remain.
- **B3-swap/flip preparation:** see `b3_verified_patch_v1/probe_test_release_20261110_v1/` for the new paired test deliveries and local acceptance checks. Remote runtime acceptance remains a launch-time gate.
- **B3-nodiff:** Dũng has run it according to the user; reconcile artifacts before acceptance.
- **Non-GPU follow-up:** restore the specific native/build/checkpoint artifacts listed in the completed session reconciliation; partial legacy rows remain explicitly classified.

## Governance note

The verified-patch B3 threshold release is an amended/exploratory subprotocol. The frozen OSF registration, preregistration threshold files, arm matrix, and historical outputs are not changed by this status report. All deviations/operational changes remain recorded in `CHANGES_AFTER_PREREG.md`.
