# OSF Preregistration Pack (`grace_diag_replication_v1`)

**Status:** READY FOR OSF REGISTRY SUBMISSION  
**Study ID:** `grace_diag_replication_v1`  
**Document & Package Version:** `prereg-v1`  
**Git Tag for submission:** `prereg-v1` (verify that it resolves to the exact commit of the submitted package)
**Pack Generation Date:** 2026-11-03 (Asia/Bangkok)  

---

## 1. Submission Deliverables

1. **Official Registration Document (PDF):**
   - Path: `output/pdf/GRACE_OSF_PREREGISTRATION_20261102.pdf`
   - Compiled directly from `preregistration.md` (English) via ReportLab and Matplotlib mathtext. Includes full provenance, exposure ledger, 11 hypotheses with $\delta = 0.02$ margins, 14 locked decision thresholds, prompt contracts, and Appendix C checklist.
2. **Stand-alone Reproducible Code & Configuration Archive (ZIP):**
   - Path: `GRACE_OSF_PREREGISTRATION_20261102.zip`
   - Contains:
     - `preregistration.md` (Official English submission document)
     - `preregistration_en.md` & `preregistration_vi.md` (Bilingual reference files)
     - `configs/protocol.yaml` & `configs/protocol_en.yaml` (Locked YAML protocol and English annotated companion)
     - `configs/thresholds.json` & `configs/thresholds_flat.json` (14 validation-selected decision thresholds; current `locked_sha256` `9252aadebf19b0f86bd9da8e59992e2adebd87d386ab6600302b9ac10a2914a3`, resealed 2026-11-03 without refitting; prior identity retained as `previous_locked_sha256`)
     - `Runs-management/step0_diagnostic/` (5,000 bootstrap reps confirmatory diagnostic report)
     - `Runs-management/dry_run_validation_20261102/` (70,070 validation prompts rendered across 10 arms; five arms blocked; no unresolved label-leak flags within the checked scope; 0 LLM calls)
     - `01_Author_Baseline_Unified/diagnostic_kit/src/grace_diag/` (Core source code for evaluation and thresholds)
3. **Audit Hash Verification Table:**
   - Path: `attachment_sha256.json`
   - Records byte count and SHA-256 digest for every file in the package.
4. **Step-by-Step Submission Guides:**
   - English: `docs/OSF_SUBMISSION_GUIDE_EN.md`
   - Vietnamese: `docs/OSF_SUBMISSION_GUIDE.md`

---

## 2. Instructions for OSF Registries Web Submission

1. Log into **[https://osf.io/registries](https://osf.io/registries)**.
2. Click **Add New Registration** -> Select **OSF Preregistration**.
3. Follow the field-by-field instructions in `docs/OSF_SUBMISSION_GUIDE_EN.md`.
4. Upload `output/pdf/GRACE_OSF_PREREGISTRATION_20261102.pdf` as primary document, `GRACE_OSF_PREREGISTRATION_20261102.zip` as archive, and `attachment_sha256.json` as checksum verification.
5. Provide permanent GitHub repository tag: `https://github.com/kazunguyen/GRACE-summary/tree/prereg-v1`
6. Submit and confirm via email links sent to all contributors.
7. **Existing test exposure:** B0/B1/B2 test inference and exploratory metrics preceded OSF submission; B2-flip Devign test has 230 viewed raw labels. Preserve their timestamps and manifests. Apply validation → threshold lock → test to work still unexecuted, and record the actual OSF URL/timestamp after approval.
