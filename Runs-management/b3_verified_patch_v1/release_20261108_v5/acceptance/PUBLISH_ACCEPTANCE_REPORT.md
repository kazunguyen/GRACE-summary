# Publication and Acceptance Report — B3 Release v5 (Devign Validation Locked)

> **Release Target:** `release_20261108_v5`  
> **Release Version:** `v5_devign_validation_locked`  
> **Parent Release:** `release_20261108_v4`  
> **Method ID:** `b3-verified-patch-v1`  
> **Status:** **FROZEN — CPU PREFLIGHT ACCEPTED — GPU INFERENCE STOPPED PENDING USER APPROVAL**  
> **Authority:** Lead PI Nguyễn Hữu Hiếu & Advisory Directives  
> **Timestamp (UTC):** `2026-11-08T13:10:00Z`  
> **OSF Registration Anchor:** [`https://osf.io/fqgh2`](https://osf.io/fqgh2) | Baseline Tag: `prereg-v1`  

---

## 1. Executive Summary & Scope

In accordance with [docs/B3_NEXT_RELEASE_PREPARATION_AND_ACCEPTANCE_20261108.md](../../../../docs/B3_NEXT_RELEASE_PREPARATION_AND_ACCEPTANCE_20261108.md), this report documents the complete technical preparation, metadata reconciliation, test verification, and delivery packaging for the amended algorithm **B3 (Verified Patch-Pair Contrastive Selector)**.

### Scope Boundaries:
1. **Target Census:** Devign Validation census ($N=2,732$), Arm `B3`, Prompt Seed `42`.
2. **Verified Pool:** Devign Pool contains **1 verified pair** (Case 08 `case_08_ffmpeg_can_safely_read_8614_26054`, SHA-256 `306b3c3391b21649635d1757af365fc9de5fb928894989bfe382fd6498a9f8f9`), independently approved by Hiếu and Dũng.
3. **Scope Limitation Declaration:** With 1 admitted pair in the pool, all 2,732 Devign validation targets select this identical pair under exhaustive token-set Jaccard ranking. This fully tests syntax, prompt composition, Figure 6 block ordering, context budgets, and inference pipeline stability, but does not evaluate dynamic target-dependent pair retrieval across a multi-pair pool.
4. **REVEAL Safe Pause:** REVEAL contains 0 admitted pairs (`BLOCKED_EMPTY_POOL`). All 17,636 clean-train donors lack upstream commit hashes in the frozen export. REVEAL validation targets ($N=2,273$) remain safely paused (`NOT_EVALUATED_BLOCKED_EMPTY_POOL`).
5. **No Historical Thresholds:** Validation inference prospectively derives the new optimal threshold $\tau^*$. The validation delivery bundle strictly forbids reading or enforcing historical thresholds (such as $\tau^*=0.77$).
6. **Execution Stop:** **NO GPU INFERENCE HAS BEEN LAUNCHED.** Preparation is 100% complete and verified on CPU; execution is paused awaiting explicit user authorization.

---

## 2. Acceptance Gates (G0 – G7)

| Gate | Name | Prerequisite Evidence | Status | Transition Decision |
|---|---|---|---|---|
| **G0** | Software Integrity | Bug fixes verified; 4 test suites pass (91 tests total, 0 fail) | **PASSED** | Ready for tool-assisted packaging |
| **G1** | Source Provenance | Upstream commit, diff, line mapping, and payload SHA-256 verified for Case 08 | **PASSED** | Eligible for independent review |
| **G2** | Review Consensus | Independent reviews from Hiếu & Dũng approved; pool sealed with 1 Devign pair | **PASSED** | Authorized for prompt rendering |
| **G3** | Prompt Census | 2,732 Devign validation prompts rendered; Figure 6 order compliant; budget $\le 8,192$ | **PASSED** | Authorized for delivery packaging |
| **G4** | Runtime Acceptance | Delivery pins 7 packages, 2x T4 offload, stable float64 scoring; CPU preflight pass | **PARTIAL** | CPU preflight PASSED; GPU inference PAUSED |
| **G5** | Score Census | Full 2,732 valid predictions and scores generated on GPU | **PENDING** | Blocked pending GPU inference |
| **G6** | Threshold Lock | $\tau^*$ derived post-validation across 0.01–0.99 MCC grid and locked | **PENDING** | Blocked pending validation scores |
| **G7** | Test Evaluation | Confirmatory test evaluation at newly locked $\tau^*$ | **PENDING** | Blocked pending threshold lock |

---

## 3. Cryptographic Hash Chain & Manifest Integrity

The release follows a strict monotonic hierarchy without circular self-referencing hashes:

```
[Case 08 Review Forms & Dossier]
         │
         ▼
[pools/pool_manifest.json] ── Seal: 73426c738d6c7bbfc176b070bff0e72cc09baee584523d9eeff80c75d38b9ad3 (File SHA-256: fb856cec6c22d11c79908d2e42ec2371c0e179c89e0dfa6092c9f80268351994)
         │
         ▼
[inputs_manifest.json] ──── Seal SHA-256: 1f1ccd0dc3f2b74ffe162a0aea2fc094e4b0533c79cc2dac93a9d888ba8fefd8 (File SHA-256: e0fe6b1de28765aeb388316ddd78b6def786da41994c6a4d049cc70123b92d13)
         │
         ▼
[acceptance/step7_selector_renderer_report.json] ── Verifier Status: STEP7_VERIFICATION_PASSED (File SHA-256: c7b504333d74658a16fd3467982b6ae0265ada2ee2133df48d4b997012391690)
         │
         ▼
[validation_prompt_manifest] ── Manifest Seal: bdeabdccbc2fb48d6201a79756d93424215e123c4055a73127d525c4afad1a01 (File SHA-256: 6d3863da6b00da4f9274d239cb9eae19cf8c131f3d5a939fe241e495b1d24c8a)
         │
         ▼
[b3_devign_val_input.zip] ── SHA-256: 8d030884ed34deea0c4e7c55c50c8b8fc058de9a64116d9c9a483f8793306645
         │
         ▼
[inference_input_manifest] ── Manifest Seal: 34f41471085f2fc96bc9d1beb1986656008eca695adfb63fd74d374ffe391b93 (File SHA-256: 4df947d0d54da9e953e1e7da033ec43c897bb3e37d075672c21ec0c3aa94219e)
         │
         ▼
[delivery/notebook.ipynb] ── SHA-256: ca2c40b804cc4a2f3fe7938914bc82d674206901170cae1e3cf690c61d4fef70
         │
         ▼
[delivery_manifest.json] ── Manifest Seal: fd638c5a108918444b830e18f5cce416f5485a46471cf600e53e2c59991721d6 (File SHA-256: 45f09df978ef27d3d76abba4a7723677565b2fdcb43ee6abe26cc8c104d2f130)
```

---

## 4. Verification Test Results (Table 8 T1 – T12)

All mandatory verification suites were executed directly in the repository environment:

```powershell
python -m pytest tests/test_amended_b3.py
python -m pytest tests/test_preregistration_integrity.py
python -m pytest 01_Author_Baseline_Unified/diagnostic_kit/tests/test_probes.py
python -m pytest 01_Author_Baseline_Unified/diagnostic_kit/tests/test_stats_and_complementarity.py
```

### Results Summary:
1. `tests/test_amended_b3.py`: **54 passed in 69.77s** (100% pass rate).
   - T1: Case 08 authentic source diff, line mapping, and payload binding.
   - T2: Review consensus, whitespace/case normalization, rejection ledger.
   - T3: Ingestion ledger, membership diff, safe preservation on errors.
   - T4: Mandatory groups gate, manifest hash validation, unified v5 metadata.
   - T5: Exhaustive exact token-set Jaccard ranking, lexicographic tie-breaking, no label leakage.
   - T6: Prompt census (2,732 Devign, Figure 6 order compliant, exact token budget $\le 8,192$).
   - T7: Notebook AST syntax check, scope validation (Devign validation only), no historical test thresholds.
   - T8: ZIP and unpacked directory loader parser, rejection of ambiguous roots or corrupt members.
   - T9: Checkpoint resume identity check, rejection of duplicate IDs with conflicting/non-finite scores.
   - T10: Float64 stable scoring `s = exp(lp1 - logaddexp(lp0, lp1))`, handling of extreme logits $[-1000, 1000]$, NaN/inf rejection, non-binary greedy token handling.
   - T11: Runtime log native parser verifying 2x Tesla T4, 49/49 offloaded layers, 8,192 context, and 7 package pins.
   - T12: Gate verdict integrity and failure-closed behavior.
2. `tests/test_preregistration_integrity.py`: **6 passed in 1.77s**.
3. `01_Author_Baseline_Unified/diagnostic_kit/tests/test_probes.py`: **20 passed in 0.40s**.
4. `01_Author_Baseline_Unified/diagnostic_kit/tests/test_stats_and_complementarity.py`: **11 passed in 2.26s**.
- **Grand Total:** **91 tests passed, 0 failed, 0 skipped.**

---

## 5. Runtime Lock Contract (`grace_qwen_q4_runtime_v1`)

The delivery notebook enforces the exact runtime specifications from `configs/inference_runtime_lock.json` (SHA-256 `4c9c3bcff5e9fd32532d7edf85df7a961e45ec9c64bee3df8833d986a2eb276e`):

- **Model Checkpoint:** `Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf` (SHA-256 `f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335`).
- **Tokenizer Revision:** `b2cff646eb4bb1d68355c01b18ae02e7cf42d120`.
- **Backend Source sdist:** `llama_cpp_python-0.3.16.tar.gz` (SHA-256 `34ed0f9bd9431af045bb63d9324ae620ad0536653740e9bb163a2e1fcb973be6`).
- **7 Locked Packages:**
  * `llama-cpp-python == 0.3.16`
  * `transformers == 4.57.1`
  * `huggingface-hub == 0.36.2`
  * `tokenizers == 0.22.2`
  * `numpy == 2.1.3`
  * `scipy == 1.16.3`
  * `scikit-learn == 1.5.2`
- **Hardware Profile:** 2x Tesla T4 (`kaggle_t4_x2`), `LLAMA_SPLIT_MODE_LAYER`, `main_gpu: 0`, `tensor_split: null`, 49/49 layers offloaded.
- **Scoring:** Reset before each prompt, unconstrained last-position logits, stable float64 `s = exp(lp1 - logaddexp(lp0, lp1))`.

---

## 6. Current Operational State & Conclusion

All prerequisites for Gate G4 CPU technical acceptance are satisfied. The delivery artifacts under `release_20261108_v5/delivery/` are fully packaged, sealed, and ready for deployment to Kaggle.

**CURRENT STATUS: GPU INFERENCE STOPPED.**  
Per explicit user directive, execution has stopped prior to launching GPU inference or uploading the kernel to Kaggle. Awaiting user authorization to proceed.
