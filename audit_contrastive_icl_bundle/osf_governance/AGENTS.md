# AGENTS.md — AI Agent Operating Manual & Governance Contract

> **Project:** GRACE Diagnostic Replication & Contrastive Evaluation (`grace_diag_replication_v1`)  
> **Registration Status:** **PUBLIC REGISTRATION** on OSF Registries ([`https://osf.io/fqgh2`](https://osf.io/fqgh2))  
> **Official Timestamp:** `Nov 3, 2026, 11:13 PM` (Asia/Bangkok)  
> **Repository Baseline Tag:** `prereg-v1` (Commit `7a1e16168591c37f005599cb4d5dc3ce33f7d950`)  
> **Dedicated Freeze Branch:** `release/osf-preregistration`  
> **Governance Authority:** Lead PI & Advisory Directives (`De_cuong_nghien_cuu_GRACE_hop_nhat.docx`, `PhanhoiHieuDungVeDangKyOsf.pdf`)

---

## 1. PURPOSE & APPLICABILITY

This document establishes the **binding operational rules, architectural constraints, and methodological safeguards** for any AI agent (Claude, Codex, Antigravity, Gemini, etc.) or human developer working in this repository.

Now that the formal OSF Pre-registration has been stamped and made public, **all core protocol contracts, decision thresholds, experimental arms, and data specifications are permanently frozen**. Any AI agent operating in this codebase must strictly abide by the rules detailed below.

---

## 2. STRICTLY FORBIDDEN ACTIONS (WHAT AGENTS MUST NEVER DO)

### 2.1. Git & Branching Governance
- ❌ **NEVER modify, rebase, or force-push to `release/osf-preregistration`**: This branch is the immutable Git anchor matching the exact OSF submission.
- ❌ **NEVER delete, re-tag, or force-push tag `prereg-v1`**: This tag is cryptographically locked to commit `7a1e16168591c37f005599cb4d5dc3ce33f7d950`.
- ❌ **NEVER rewrite public Git history** or delete historical worklogs documenting pre-registration audits.

### 2.2. Frozen Pre-Registration Deliverables
- ❌ **NEVER modify or re-generate files in `Runs-management/osf_registration_draft_20261102/`**:
  * `output/pdf/GRACE_OSF_PREREGISTRATION_20261102.pdf` (SHA-256: `22648ead896baf5c1032de700c12fb97bd6dc44f0a8049292532ae6c0468b14c`)
  * `GRACE_OSF_PREREGISTRATION_20261102.zip` (SHA-256: `6d6e8fe46f1dc59bf5f399defca59ba8ab0c362a0b13d0cb101c16320a2a082e`)
  * `attachment_sha256.json` (SHA-256: `41888a239e902dc1911f7e19b5c033726ea537689fcbc82caf6aaee275dde049`)
- ❌ **NEVER edit `preregistration.md`** to alter pre-registered hypotheses, sample sizes, or decision rules.

### 2.3. Decision Thresholds & Optimization Freezes
- ❌ **NEVER alter `configs/thresholds.json` or `configs/thresholds_flat.json`**:
  * All 14 optimal thresholds ($\tau^*$) are locked on validation splits.
  * Self-signing checksum: `a0108431ad859aacc3dab29ca7e88a7eb404428b4d60fc251e3bbae7d350c831`.
  * Evaluation runners (`evaluate_final.py`) MUST abort if threshold checksum verification fails.
- ❌ **NEVER re-tune thresholds for perturbation/probe arms**:
  * $B2\text{-flip}$ and $B2\text{-rep}$ MUST inherit $\tau^*$ directly from $B2$.
  * $B3\text{-flip}$ and $B3\text{-swap}$ MUST inherit $\tau^*$ directly from $B3$.
  * Independent threshold re-tuning for flipped/repeated probes constitutes p-hacking and is strictly prohibited.

### 2.4. Experimental Matrix & Prompt Contracts
- ❌ **NEVER modify `configs/arms.yaml`**: The 15 diagnostic arms (B0, B1, B1-full, B1-H2, B1-shuf, B2, B2-rand, B2-nolabel, B2-labelonly, B2-flip, B2-rep, B3, B3-nodiff, B3-swap, B3-flip) are fixed. No exploratory arms may be inserted into confirmatory tables.
- ❌ **NEVER alter prompt section ordering** from Figure 6:
  `[role_domain -> target_code -> question -> node_info -> edge_info -> demonstration -> answer]`.
  Target code comes first, graph in the middle, demonstration at the end. Target labels must NEVER enter the prompt.
- ❌ **NEVER violate the 8,192 token budget**: Target code $\le 3,000$, demo $\le 1,500$, graph $\le 1,500$, reserve $64$ tokens.

### 2.5. Data Specs & Clean Retrieval Banks
- ❌ **NEVER alter the sanitized 15-arm specs**:
  * `data/specs/devign_validation_15arms.jsonl` (2,732 rows, 0 bad demos, 0 bad pairs)
  * `data/specs/devign_test_15arms.jsonl` (2,732 rows, 0 bad demos, 0 bad pairs)
  * `data/specs/reveal_validation_15arms.jsonl` (2,273 rows, 0 bad demos, 0 bad pairs)
  * `data/specs/reveal_test_15arms.jsonl` (2,274 rows, 0 bad demos, 0 bad pairs)
- ❌ **NEVER modify the clean donor banks** (Devign $N=21,691$, REVEAL $N=17,636$). Exact duplicates and label-conflicting groups are purged and frozen.

### 2.6. Methodological & Cache Safeguards
- ❌ **NEVER run $B2\text{-rep}$ without cache isolation**: Arm $B2\text{-rep}$ MUST run with `repeat: true` and `tag="repeat"`. It must NEVER read cached responses from $B2$.
- ❌ **NEVER apply interim data-dependent stopping**: Test evaluation follows a fixed-sample census ($N=2,732$ on Devign Test; $N=2,274$ on REVEAL Test). Early stopping is forbidden.
- ❌ **NEVER report uncorrected p-values as confirmatory**: All 11 Table B contrasts MUST be adjusted using the Holm-Bonferroni method (`family_correction: holm`).

---

## 3. PERMITTED & REQUIRED ACTIONS (WHAT AGENTS SHOULD DO)

### 3.1. Step 5: Confirmatory GPU Inference Execution
- ✅ **Execute remaining & rerun arms on GPU**:
  * Arm $B2\text{-rep}$ on Devign Test and REVEAL Test (fresh execution with dedicated cache tag).
  * Arm $B2\text{-flip}$ on Devign Test ($N=2,732$) and REVEAL Test ($N=2,274$).
  * Tier 2 arms: $B2\text{-rand}$, $B2\text{-nolabel}$, $B2\text{-labelonly}$, $B1\text{-shuf}$.
  * Tier 3 arms: $B1\text{-full}$, $B1\text{-H2}$, $B3$, $B3\text{-nodiff}$, $B3\text{-swap}$, $B3\text{-flip}$.
- ✅ **Verify model checkpoint & runtime provenance**:
  * Primary model: `Qwen/Qwen3-Coder-30B-A3B-Instruct` (GGUF Q4_K_M, SHA-256 `f6050b4da...`, revision `b2cff646...`).
  * Backend: `llama-server (llama.cpp b3920)` with `--n_ctx 8192` on 2x Tesla T4 GPUs (Kaggle Linux) or vLLM FP8/bf16.
  * Decoding: Greedy decoding (temperature 0.0, seed 42).
  * Score calculation: $s = \frac{p(1)}{p(0) + p(1)} = \operatorname{sigmoid}(\operatorname{logit}_1 - \operatorname{logit}_0)$.

### 3.2. Step 6: Supervised Baselines & Meta-Model Complementarity
- ✅ **Evaluate supervised anchors**:
  * SUP-LR and SUP-MLP on frozen CodeT5 768d embeddings; SUP-METRIC on 26 static code metrics.
  * Evaluate across 3 pre-registered seeds: 42, 43, 44 (headline seed 42).
- ✅ **Train meta-models ($P_{\text{pre}}$ vs. $P_{\text{post}}$)**:
  * 3-fold Out-Of-Fold (OOF) cross-validation with `StratifiedGroupKFold` (clustered by `commit_id` / `file_hash`).
  * $P_{\text{pre}}$: 34 base features.
  * $P_{\text{post}}$: 34 base + 4 LLM interaction features $[s, \text{valid}, s \cdot p, s - p]$.
  * Symmetric fallback: If LLM output is invalid, fall back to $P_{\text{pre}}$ ($s = 0.5, \text{valid} = 0$).
- ✅ **Compute routing curves**:
  * Evaluate budgets $q \in \{0.05, 0.10, 0.25\}$.
  * Compare Confidence Router, Benefit Router (Ridge $\alpha=10$), Random Router (20 seeds), and Oracle Ceiling.

### 3.3. Step 7: Confirmatory Statistics & Table B Compilation
- ✅ **Execute Paired Cluster Bootstrap**:
  * $B = 5,000$ iterations with fixed seed `20261117`.
  * Clustering: `commit_id` for Devign ($2,068$ test clusters); `file_hash` for REVEAL ($646$ test clusters).
  * Compute 95% CIs for $\Delta \text{AUROC}$, $\Delta \text{MCC}$, $\Delta \text{BA}$, and $\Delta \text{F1}$.
  * Apply Holm-Bonferroni correction and apply pre-specified verdict rules:
    - `'benefit'`: CI lower bound $> 0$ AND point estimate $\ge \delta$.
    - `'no_meaningful_benefit'`: CI upper bound $< \delta$.
    - `'harm'`: CI upper bound $< 0$.
    - `'inconclusive'`: CI spans 0 or upper bound $\ge \delta$ with lower bound $\le 0$.
- ✅ **Dual-partition reporting**: Report all primary metrics on both (a) full official test census and (b) clean near-deduplicated test.

### 3.4. Step 8: Qualitative Human Blind Review
- ✅ **Process double-blind adjudication data**:
  * 100 retrieval targets rated across sink, variable, guard, and evidence line criteria.
  * 60 error packets across 4 cells (FN repaired, FN created, FP repaired, FP created).
  * 100 label audit cases for SUP-LR.
  * Compute Cohen's $\kappa$ and document adjudications.

### 3.5. Post-Registration Deviations & Logging
- ✅ **Document all operational changes**: Any bug fix, script update, or unexpected deviation MUST be logged with date, rationale, affected analyses, and exploratory classification in `CHANGES_AFTER_PREREG.md`.

---

## 4. WORKFLOW & CODE QUALITY STANDARDS

1. **Active Branches**:
   - Feature and inference work occurs on branch `hieu` or dedicated feature branches (e.g. `feat/step5-inference`).
   - Merges into `baseline-unified` must be reviewed and tested.
2. **Automated Verification Before Commit**:
   - Run integrity and diagnostic tests before pushing code:
     ```powershell
     python -m pytest tests/test_preregistration_integrity.py
     python -m pytest 01_Author_Baseline_Unified/diagnostic_kit/tests/test_probes.py
     python -m pytest 01_Author_Baseline_Unified/diagnostic_kit/tests/test_stats_and_complementarity.py
     ```
3. **Commit Messages**: Follow Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`).
4. **Encoding & Cross-Platform Integrity**:
   - Always enforce UTF-8 without BOM (`encoding="utf-8"`) on all text and script operations.
   - Respect `.gitattributes` binary/text declarations to prevent CRLF/LF cryptographic hash corruption.

---

*This document is effective immediately upon OSF public registration approval (2026-11-03T23:23:00+07:00). All future agent instructions and pull requests must comply with this contract.*
