# GRACE arm execution status and remaining work

**Checked:** 2026-11-10 00:16 UTC (07:16 Asia/Saigon). Kaggle CLI was queried with the `lznt123` account config. This document separates census completion from runtime acceptance; a complete result is not automatically a certified runtime.

## Current run state

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
| B0 | Validation and test census recorded: Devign 2,732 each; REVEAL 2,273 validation / 2,274 test. | Historical run; do not infer new-lock acceptance from completeness. |
| B1 | Validation and test census recorded at full coverage. | Historical run; any stronger current-lock claim needs provenance review. |
| B1-full | Test 5,006/5,006. | Accepted under its recorded launch contract; evidence in `run_handoff_20261108/B1_FULL_RUNTIME_ACCEPTANCE.md`. |
| B1-H2 | Test 5,006/5,006; validation/test outputs exist. | Census complete. Preserve the documented Kaggle threshold lineage; Colab results remain exploratory. |
| B1-shuf | Test 15,018/15,018 across six seed/dataset groups. | Runtime accepted: two T4, 49/49 offload and locked six-package contract; see `b1_shuf_kaggle_output_20261109/RUNTIME_ACCEPTANCE_20261109.md`. |
| B2 | Validation and test full-census outputs recorded, including donor-reconciled results. | Historical runtime evidence; do not rewrite old records. Audit provenance if a current-lock certification is needed. |
| B2-rand | Validation 15,015/15,015 and test 15,018/15,018 across seeds 42/43/44. | Census complete. Runtime evidence is session-specific; seed44 head/tail merge is documented in `worklogs/2026-11-08_b2_rand_seed44_test_head_tail_merge.md`. |
| B2-nolabel | Test 5,006/5,006. | Census accepted; existing summary says full newer runtime lock is not yet certified. Retrospective provenance audit remains. |
| B2-labelonly | Test 5,006/5,006. | Census accepted; existing summary says full newer runtime lock is not yet certified. Retrospective provenance audit remains. |
| B2-flip | Validation and test records complete: 5,005 validation + 5,006 test; probe inherits B2 thresholds. | Census complete. Keep the donor/version lineage attached; audit runtime provenance before claiming newer-lock acceptance. |
| B2-rep | Test 5,006/5,006; manifests record `repeat: true`, `tag: "repeat"`. | Census/cache-isolation requirement met in recorded manifests. Full newer runtime lock remains uncertified in current acceptance summary; audit the actual run provenance. |
| B3, historical algorithm | Historical validation is complete; it is distinct from the verified-patch algorithm. | Do not substitute it for the B3 new-algorithm validation/test. |
| B3, verified-patch-v1 | Validation complete: Devign 2,732/2,732; REVEAL 2,273/2,273. | Runtime accepted for the score-producing sessions. Separate amended threshold locks: Devign tau*=0.99; REVEAL tau*=0.01. Classified `AMENDED_EXPLORATORY_SUBPROTOCOL`, not an OSF preregistered lock. |
| B3-nodiff | No current verified-patch test release or test run. | Excluded from the present GPU scope per user instruction. If later included, it needs its own validation-derived threshold before test. |
| B3-swap | No current verified-patch test release or test run. | Not run-ready; preparation and gates are below. Inherits B3 threshold; no retuning. |
| B3-flip | No current verified-patch test release or test run. | Not run-ready; preparation and gates are below. Inherits B3 threshold; no retuning. |

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

### 2. Prepare B3-swap and B3-flip as separate test arms (not yet ready to launch)

**Available:** locked B3 thresholds; current B3 selector/pool and reviewed pair; CPU renderer/selector-family checks; arm definitions in `configs/arms.yaml`. The current B3 test release contains B3 only, not swap/flip test prompt bundles.

**Required prompt semantics:** for each target use the same verified-patch B3-selected pair, target code/graph, and `Key difference` content as B3. Render a separate prompt and hash for each arm:

- B3-swap reverses the two demonstration blocks while keeping each label attached to its original code.
- B3-flip keeps the order and code blocks but reverses both demonstration labels.

**Before a teammate launches either arm, check:**

1. Generate the full Devign 2,732 and REVEAL 2,274 target census from the current B3 test selection; do not use historical pair selections or select a different donor pair for the variant.
2. Prove the only change from the paired B3 prompt is the specified order/label manipulation; preserve target fields, graph, pair IDs, and `Key difference`.
3. Prove no target labels or label-derived fields enter prompts/input; keep test labels private.
4. Audit exact-tokenizer counts, Figure 6 section order, per-component/context limits, unique IDs, prompt hashes, and expected row counts.
5. Pin a separate variant manifest/archive and worker/runner hashes; verify the runner supports the arm ID and never reads a B3 response cache.
6. Load B3's sealed dataset-specific threshold locks byte-for-byte (Devign 0.99, REVEAL 0.01); do not optimize thresholds on variant validation/test.
7. Attach the private release/model to the execution account, verify T4 x2 configuration, and read back the exact notebook source before launch. Runtime acceptance still requires logs/provenance and 49/49 offload.

Only after these checks pass is the arm ready for GPU execution. Prompt-generation/CPU auditing can be delegated now; GPU launch is a separate gate.

### 3. B3-nodiff scope decision

The current instruction excludes B3-nodiff from this execution. Do not add it implicitly to the B3/swap/flip package. If the project later elects to include it, prepare its own validation prompts/results and lock a separate validation threshold before preparing test inference; it cannot inherit B3's threshold under the stated protocol.

### 4. Retrospective runtime audit for completed legacy outputs

B2-nolabel, B2-labelonly, and B2-rep have complete output censuses, but current documentation does not certify them against the newer full runtime lock. A teammate can audit existing run artifacts first. For each score-producing session, match records to the exact run manifest, runtime lock, package freeze, model/tokenizer identity, native model-load/offload log, build/source archive hash, and runtime provenance. Record evidence per session/seed/dataset; do not generalize one session's T4/offload evidence to another. Do not repeat test inference merely to fill documentation gaps unless the audit demonstrates evidence is unrecoverable and the project explicitly approves a new run scope.

## Current handoff recommendation

- **Run already underway:** B3 verified-patch test v6. Handoff monitoring, checkpoint/output collection, and runtime/result acceptance; do not create another B3 base run.
- **Offline prep teammate can start:** B3-swap and B3-flip prompt bundle generation and audit against the checks above.
- **Do not launch yet:** B3-swap/flip until the variant bundles and exact source readback pass; B3-nodiff remains excluded.
- **Non-GPU audit task:** retrospective provenance review for completed B2-nolabel/B2-labelonly/B2-rep.

## Governance note

The verified-patch B3 threshold release is an amended/exploratory subprotocol. The frozen OSF registration, preregistration threshold files, arm matrix, and historical outputs are not changed by this status report. All deviations/operational changes remain recorded in `CHANGES_AFTER_PREREG.md`.
