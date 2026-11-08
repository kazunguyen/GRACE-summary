# Scope Decision Record — Release v5 (Devign Validation Locked)

**Document Status:** RATIFIED BY PROJECT LEAD  
**Release ID:** `release_20261108_v5`  
**Release Version:** `v5_devign_validation_locked`  
**Method ID:** `b3-verified-patch-v1`  
**Authority:** Lead PI (Nguyen Huu Hieu) & Advisory Directives  
**Decision Timestamp:** `2026-11-08T12:00:00Z`  
**Seal SHA-256:** `ab762bfc205b4e87575aa47149373989c146a3d4d50725cc165486c51d210ec4`  

---

## 1. Approved Execution Scope
- **Dataset:** Devign
- **Split:** Validation census
- **Arm:** B3 (Verified Patch-Pair Contrastive Demonstration)
- **Prompt Seed:** 42
- **Expected Census Count:** 2,732 targets
- **Pool Hash:** `306b3c3391b21649635d1757af365fc9de5fb928894989bfe382fd6498a9f8f9`
- **Active Pairs:** 1 verified pair (`case_08_ffmpeg_can_safely_read_8614_26054`)

## 2. Mandatory Scope Boundary & Disclosure
1. **Single-Pair Scope Limitation:**
   Single verified pair in Devign pool: all 2,732 validation targets select this identical pair. This verifies prompt syntax, Figure 6 ordering, context budgets, and inference pipeline integrity, but does NOT evaluate dynamic target-dependent pair retrieval across a diverse pool. Pool composition is permanently locked before inference.
2. **REVEAL Blocker:**
   All 17,636 clean-train donors in REVEAL lack upstream commit hashes in frozen data. REVEAL is preserved in the overarching research matrix but safely blocked from this execution delivery until authentic provenance can be established.
3. **Test Split Exclusion:**
   Test split evaluation is strictly forbidden prior to full validation census completion and formal tau* threshold derivation.
4. **Exploratory Variant Arms:**
   B3-nodiff, B3-swap, and B3-flip are verified via CPU rendering but excluded from GPU launch in this delivery.

## 3. Governance Classification
- **Method Classification:** `AMENDED_EXPLORATORY_SUBPROTOCOL`
- **OSF Registration Anchor:** `https://osf.io/fqgh2`
- **Documentation:** Logged in `CHANGES_AFTER_PREREG.md`.
