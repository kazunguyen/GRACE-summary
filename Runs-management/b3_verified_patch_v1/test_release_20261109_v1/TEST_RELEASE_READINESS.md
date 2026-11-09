# B3 new algorithm — test delivery readiness

**Status: VERSION 2 PUSHED; ALL FIVE EXECUTABLE CELLS VERIFIED BY READBACK; CANONICAL KERNEL QUEUED; RUNTIME ATTESTATION PENDING.**

## Completed and verified

- Rendered and exact-tokenizer-audited all **5,006** frozen test prompts: Devign **2,732**, REVEAL **2,274**. The renderer consumes the frozen test specs but passes only ID, code, and graph fields to the B3 selector.
- Confirmed unique census IDs, prompt hashes, Figure 6 ordering, component limits, and 8,192-token context budget with 64-token reserve. See `audit/*_prompt_census.jsonl` and `audit/prompt_audit_report.json`.
- Kept test labels in `private_evaluation_only/test_labels.json`; no label values or label-named files are in `kaggle_input.zip`.
- Verified the two selected retrieval pool byte hashes against the locked validation identities:
  - Devign pool `306b3c3391b21649635d1757af365fc9de5fb928894989bfe382fd6498a9f8f9`.
  - REVEAL pool `37bb24c5be0e36c9f6c03a046e17687265461abeb1873fe399c9232c7e761203`.
- Revalidated both sealed threshold locks against the method, pool, model, tokenizer, runtime, scoring, validation-worker hash, and canonical seal. Devign `tau*=0.99`; REVEAL `tau*=0.01`; both have `fit_split=validation`.
- Verified the test archive inventory and per-member checksums. It contains only prompts, pools, threshold locks, and the pinned runtime lock. Archive SHA-256: `cee276c8bf5024fd5365523d23414871ccba348b4cea3d4b58c1853ea5e340b1`.
- Python syntax compilation passed for the prompt builder, finalizer, and test loader.
- Built a dedicated test-only worker at `worker/kaggle_inference_test.py`. The validation-only label evaluator and validation bundle loader were removed. The score function is AST-identical to the accepted validation worker. Output rows contain scores/log-probabilities and `threshold_prediction`, never target labels; resume checks bind every record to prompt, model, runtime, threshold, and worker identities.
- Threshold locks are revalidated in the worker before inference. Checkpoint validation checks `s = sigmoid(logprob_1 - logprob_0)` and `threshold_prediction = int(s >= tau*)`; corrupted identity/threshold records fail closed.
- Built a private Kaggle notebook and dataset staging package for **account `lznt123`**. Notebook pins the manifest, archive, worker, model and runtime lock; requires 2×Tesla T4, locked package versions, CUDA backend from the SHA-verified `llama-cpp-python==0.3.16` source archive, Q4_K_M model SHA, 8,192 context, layer auto-split across both GPUs, and the contract's 49/49 layer offload check. Kaggle timeout is 9 hours with a 300-second checkpoint reserve.
- Published private dataset `lznt123/grace-b3-test-release-20261109-v1`, then versioned it after a readback found the first manifest stale. Downloaded the latest remote version and verified the manifest seal, all seven input member hashes, and absence of labels. The remote dataset version now matches the worker SHA and archive used by the notebook.
- Kernel code is pushed under `lznt123/grace-b3-new-test-20261109-v1`; remote readback code cells match local. The metadata title was corrected to match its slug. Kaggle also has an earlier title-derived kernel `lznt123/grace-b3-new-algorithm-test-devign-and-reveal`; its code cells match the canonical kernel. **Both report QUEUED**, so this is a duplicate submission that may consume both available batch slots. A push for a later version was refused with `Maximum batch GPU session count of 2 reached`.
- Local execution manifest: `execution_manifest.json`; worker SHA-256 `2b82c468f842f4ad45993d5a9b09c2fc843b1d3903b2751800c41f3cbbcaedc8`; notebook SHA-256 `409a23aa60794b10fd5a87cce560a9f11e2e866094d3e94ba139a6a0a1ee11fc`.
- Local checks passed for notebook syntax, worker syntax, validation/test scoring-function parity, no target-label evaluator, manifest/archive/member hashes, threshold-lock seals, positive checkpoint validation, and rejection of a deliberately corrupted threshold prediction.
- The 2026-11-09 integration recheck found and fixed two startup blockers in the previous draft: the runtime helper imported an unpackaged validation module, and the tokenizer local path failed the contract's repository-identity check. The test package now includes a standalone native-log checker with the original function preserved, and loads the tokenizer from the contract repository at its pinned revision. Backend build output is saved to the diagnostics path consumed by provenance collection. A mocked backend exercise verified the actual model-load helper path and rejection of a wrong tokenizer. This local mock is **not actual GPU evidence**. Details: `audit/worker_integration_audit.json`.

## Required before Kaggle upload or launch

1. Resolve the duplicate queued kernel session. The installed Kaggle CLI has no cancellation command, and the status endpoint does not return a session ID. An auto-review rejected calling the cancel endpoint with guessed ID `1`, because it could cancel another Kaggle session. Obtain a verified session ID or cancel the duplicate through Kaggle's UI; then keep one canonical run.
2. On Kaggle, prove Python/package pins, two Tesla T4 devices, CUDA backend build/source hash, 49/49 layer placement, model file hash, tokenizer identity, and runtime provenance **before inference**. The code enforces these conditions, but no runtime evidence exists until a real kernel session produces it.
3. Preserve resumable score-only checkpoints and retrieve output. Join scores to local labels after download; compute test metrics locally without refitting thresholds.

## Current blocker

The canonical kernel `lznt123/grace-b3-new-test-20261109-v1` version 2 was pushed successfully. Readback confirms all five executable code-cell sources match the sealed local notebook; Kaggle normalized metadata, so the whole notebook byte hash differs. Its latest status is `QUEUED`. The earlier title-derived duplicate reports `CANCEL_REQUESTED`, not confirmed canceled. Kaggle status requests are responding normally; no server error was observed. No inference records or runtime provenance exist yet. Verify `RUNNING` before claiming execution has started.
