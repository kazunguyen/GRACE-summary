# Step-by-Step OSF Registries Submission Guide for GRACE Replication

> **Study ID:** `grace_diag_replication_v1`  
> **Version:** `prereg-v1`  
> **Primary Submission Document:** `Runs-management/osf_registration_draft_20261102/output/pdf/GRACE_OSF_PREREGISTRATION_20261102.pdf`  
> **Attached Reproducible Archive:** `Runs-management/osf_registration_draft_20261102/GRACE_OSF_PREREGISTRATION_20261102.zip`  
> **Audit Hash Table:** `Runs-management/osf_registration_draft_20261102/attachment_sha256.json`  

---

## 1. Pre-Submission Verification

Before logging into OSF Registries, verify that:
1. Git repository working directory is clean and tracking the intended branch:
   ```powershell
   git status
   ```
2. Automated test suite and 15-arm dry-run audit pass 100%:
   ```powershell
   python -m pytest tests/test_preregistration_integrity.py
   python -m pytest 01_Author_Baseline_Unified/diagnostic_kit/tests/test_probes.py
   python -m pytest 01_Author_Baseline_Unified/diagnostic_kit/tests/test_stats_and_complementarity.py
   ```
3. The submission bundle has been compiled:
   ```powershell
   python scripts/build_osf_preregistration_bundle.py
   ```
4. Output files in `Runs-management/osf_registration_draft_20261102/` are verified:
   - `output/pdf/GRACE_OSF_PREREGISTRATION_20261102.pdf`
   - `GRACE_OSF_PREREGISTRATION_20261102.zip`
   - `attachment_sha256.json`

---

## 2. Step-by-Step Form Filling on OSF Registries Web Interface

### Step 2.1: Access and Initialize Registration
1. Navigate to: **[https://osf.io/registries](https://osf.io/registries)**
2. Log in with your OSF credentials.
3. Click **"Add New Registration"** (or open the project on OSF -> navigate to **Registrations** tab -> **New Registration**).
4. **Choose Registration Template:**
   - Select: **OSF Preregistration** (or *Open-Ended Registration*).
   - Click **Create draft**.

---

### Step 2.2: Fill Metadata

* **Title:**
  ```text
  Diagnostic Replication of GRACE: Evaluating Graph Representations and In-Context Demonstration Retrieval for LLM-Based Vulnerability Detection
  ```

* **Contributors:**
  - Add all authors and research team members with their OSF accounts / ORCIDs.
  - Set permissions (Lead PI as Administrator, co-authors as Read+Write).

* **Description (Abstract):**
  ```text
  This preregistration documents a diagnostic replication of GRACE across 15 arms on Devign and REVEAL using Qwen3-Coder-30B-A3B-Instruct (GGUF Q4_K_M). B0, B1 and B2 test inference and exploratory metrics preceded OSF submission; 230 B2-flip Devign test raw labels were also viewed. The 14 current decision thresholds were selected on validation, but their lock is not claimed to predate every historical test run. The registration specifies rules for future analyses and discloses prior exposure; independent confirmation requires data not used to shape the plan.
  ```

* **License:**
  - Select **CC-By Attribution 4.0 International** or **MIT License**.

* **Subject / Category:**
  - Computer Sciences -> Software Engineering -> Computer and Information Security.

* **Keywords:**
  ```text
  Vulnerability Detection, Large Language Models, In-Context Learning, Code Property Graph, Diagnostic Replication, Pre-registration, Software Security, Qwen3-Coder
  ```

---

### Step 2.3: Fill Hypotheses (Section 2 / Table 4.3)

Copy verbatim the 11 pre-registered hypotheses:

```text
- H1.1 (GRACE vs Zero-shot on Devign): Arm B2 does not outperform B0 on Devign Test: Upper bound of 95% CI for ΔMCC(B2 - B0) < 0.03 and ΔAUROC < 0.02 (practical equivalence margin δ = 0.02).
- H1.2 (GRACE vs Zero-shot on REVEAL & Published Benchmark): Arm B2 does not outperform B0 on REVEAL Test (ΔMCC < 0.03, ΔAUROC < 0.02). GRACE does not reproduce published MCC >= 0.15 on either benchmark; Devign B2 F1 is below always-vulnerable baseline (62.95%).
- H2.1 (Surface Label Sensitivity): Demonstrations act predominantly via surface label priming: Net label sensitivity >= 15 percentage points (|B2 - B2-flip| minus |B2 - B2-rep| natural variance).
- H2.2 (Code Invariance in Demos): Demo source code does not provide intrinsic logic signals: Upper bound of CI for ΔAUROC(B2 - B2-rand) < 0.02 and ΔAUROC(B2-nolabel - B1) < 0.02; B2-labelonly recovers >= 80% of (B2 - B1) delta.
- H2.3 (Contrastive Demonstration Operating Point): Contrastive pairs (B3) shift operating decision points without improving discriminative capacity: B3 positive prediction rate is >= 10 percentage points higher than B2 while upper bound of 95% CI for ΔAUROC(B3 - B2) < 0.02.
- H3.1 (LLM Graph Invariance): Textual CPG information does not provide additional discriminative signal: Upper bound of CI for ΔAUROC(B1 - B0) < 0.02 and ΔAUROC(B1 - B1-shuf) < 0.02; B1-H2 (guarded evidence) shows equivalent behavior.
- H4.1 (Threshold-Free Randomness): Across all LLM arms, AUROC <= 0.62 on both Devign and REVEAL.
- H5.1 (Supervised Baseline Superiority): Supervised classifier on frozen CodeT5 embeddings (SUP-LR) substantially outperforms LLM pipeline: ΔMCC(SUP-LR - B2) >= 0.15 with CI excluding 0; AUROC(SUP-LR) >= 0.68.
- H5.2 (No Orthogonal LLM Signal): LLM output scores do not add orthogonal predictive value over 34 base features: Upper bound of 95% CI for ΔMCC(P_post - P_pre) < 0.02 under identical StratifiedGroupKFold splits.
- H5.3 (Expert Routing Efficacy at q=10%): Benefit router (Ridge) does not outperform Confidence router: Paired Bootstrap CI upper bound for ΔBalanced_Accuracy(benefit - confidence) < 0.02; ΔBalanced_Accuracy(benefit - random) < 0.01; LLM error corrections do not exceed 95th percentile of equal-rate random expert across 20 seeds.
- H6.1 (Retrieval Mechanism Mismatch): Retrieved demonstrations rarely match true underlying vulnerability mechanisms: "Neither" rate >= 40% on Devign; accuracy difference between related and unrelated demos has CI containing 0.
```

---

### Step 2.4: Design Plan & Data Exposure Disclosure

* **Study Design:**
  ```text
  15-arm observational benchmark replication experiment. Fully factorial ablation across graph representations (B0, B1, B1-shuf, B1-full, B1-H2), demonstration content (B2, B2-rand, B2-nolabel, B2-labelonly, B2-flip, B2-rep), and contrastive pairs (B3, B3-nodiff, B3-swap, B3-flip), alongside 3 supervised frozen-embedding baselines (SUP-LR, SUP-MLP, SUP-METRIC) and meta-models (P-PRE, P-POST).
  ```

* **Existing Data Declaration:**
  - Select: **Registration following analysis of the data** (for Tier 1 arms B0, B1, B2 on Devign and ReVeal test sets where exploratory metrics were computed prior to formal pre-registration).
  - Use **Registration prior to analysis of the data** only for each analysis genuinely unperformed at submission. Disclose partial B2-rand validation inference and the 230 B2-flip Devign test raw labels; do not classify all Tier 2–3 work uniformly.

* **Existing Data Explanation:**
  Paste the Exposure Ledger table from Section 1.2 of `preregistration.md`.

* **Sample Sizes:**
  - Devign: 2,732 Validation, 2,732 Test (Total 5,464). Clean donor bank: 21,691.
  - REVEAL: 2,273 Validation, 2,274 Test (Total 4,547). Clean donor bank: 17,636.

---

### Step 2.5: Analysis Plan & Statistical Rules

* **Statistical Estimators & Bootstrap Specification:**
  ```text
  - Paired Cluster Bootstrap: B = 5,000 iterations, fixed random seed 20261117.
  - Cluster Units: Devign clustered by commit_id (2,068 clusters); REVEAL clustered by file_hash (646 clusters).
  - Multiple Testing Correction: Holm-Bonferroni step-down procedure (family_correction: holm).
  - Decision Rule Margins: Practical equivalence margin delta = 0.02 (delta_MCC = 0.03, delta_AUROC = 0.02, delta_BA = 0.01).
  - Verdict Classification:
    * 'benefit': CI lower bound > 0 and point estimate >= delta.
    * 'no_meaningful_benefit': CI upper bound < delta.
    * 'harm': CI upper bound < 0.
    * 'inconclusive': CI overlaps 0 or upper bound >= delta with lower bound <= 0.
  - Threshold Fitting: 14 optimal thresholds tau* locked via argmax MCC on validation grid [0.01, 0.99] step 0.01.
  ```

---

### Step 2.6: Upload Attachments

Under **Files / Attachments**:
1. **Primary Registration Document:** Upload:
   `Runs-management/osf_registration_draft_20261102/output/pdf/GRACE_OSF_PREREGISTRATION_20261102.pdf`
2. **Reproducible Code & Configuration Archive:** Upload:
   `Runs-management/osf_registration_draft_20261102/GRACE_OSF_PREREGISTRATION_20261102.zip`
3. **Checksum Verification File:** Upload:
   `Runs-management/osf_registration_draft_20261102/attachment_sha256.json`
4. In the File Description field, write:
   ```text
   Stand-alone reproducible preregistration pack containing protocol YAML, frozen threshold tables, analysis lock manifests, 15-arm validation dry-run audit summary (95,095 prompts rendered, 0 leaks, 0 LLM calls), and core diagnostic evaluation code. All files verified against SHA-256 digests in attachment_sha256.json. Permanent GitHub repository tag: https://github.com/kazunguyen/GRACE-summary/tree/prereg-v1
   ```

---

### Step 2.7: Review, Select Visibility & Submit

1. Click **Review** to preview all entries.
2. Select **Registration Visibility**:
   - **Public immediately** (recommended if test inference begins promptly).
   - **Embargo** (optional if embargo period is desired before conference submission, up to 4 years).
3. Click **Submit**.
4. All contributors will receive an email from OSF Registries to approve the submission. All must approve within 48 hours for the registration to be timestamped and assigned a DOI.

---

## 3. Post-Submission Archiving

Once approved:
1. Record official registration URL (`https://osf.io/XXXXX`) and DOI.
2. Verify git tag `prereg-v1` on GitHub:
   ```powershell
   git ls-remote --tags origin prereg-v1
   ```
3. Proceed with new or required rerun test work under the frozen protocol; preserve historical run timestamps and manifests.
