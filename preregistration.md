# Pre-registration Protocol: Diagnostic Replication of GRACE (v1)

- **Study ID:** `grace_diag_replication_v1`
- **Version:** `prereg-v1`
- **Registration Date:** 2026-10-31 (Standardization update completing Step 4: 2026-11-02)
- **Repository Version / Git Tag:** `prereg-v1`
- **Protocol Configuration File:** [`01_Author_Baseline_Unified/diagnostic_kit/configs/protocol.yaml`](https://github.com/kazunguyen/GRACE-summary/blob/prereg-v1/01_Author_Baseline_Unified/diagnostic_kit/configs/protocol.yaml) & [`configs/protocol.yaml`](https://github.com/kazunguyen/GRACE-summary/blob/prereg-v1/configs/protocol.yaml)
- **Locked Thresholds File:** [`configs/thresholds.json`](https://github.com/kazunguyen/GRACE-summary/blob/prereg-v1/configs/thresholds.json) & [`configs/thresholds_flat.json`](https://github.com/kazunguyen/GRACE-summary/blob/prereg-v1/configs/thresholds_flat.json)
- **Current Threshold Lock Identity (`locked_sha256`):** `9252aadebf19b0f86bd9da8e59992e2adebd87d386ab6600302b9ac10a2914a3` (resealed 2026-11-03; earlier identity `a0108431ad859aacc3dab29ca7e88a7eb404428b4d60fc251e3bbae7d350c831` is retained only as `previous_locked_sha256`).
- **Original Research Proposal Document:** [`00_Reports_and_Docs/PhuongAn2_De_cuong_nghien_cuu_GRACE_hop_nhat.pdf`](https://github.com/kazunguyen/GRACE-summary/blob/prereg-v1/00_Reports_and_Docs/PhuongAn2_De_cuong_nghien_cuu_GRACE_hop_nhat.pdf)

The date 2026-10-31 above identifies the historical protocol document; it is **not** an OSF submission or approval timestamp. The actual OSF registration URL and timestamp remain pending. The `prereg-v1` tag identifies a repository snapshot, not proof that every decision preceded the test runs listed below.

---

## 1. Test Exposure Disclosure & Exposure Ledger

The test sets of Devign and ReVeal were previously exposed during the initial exploratory phase (including 36 exploratory API test runs, the dev-100 subset, and preliminary H1–H3 motivation measurements).

The exposure ledger below records test inference and exploratory metric inspection before OSF submission. The current protocol, prompts, arms and thresholds are documented for subsequent work; this document does **not** claim that every decision was frozen before those historical test runs. Threshold values in `configs/thresholds.json` were selected on validation, but no evidence establishes that their lock preceded every Tier 1 or B2-flip test inference. The earlier Tier 1 metrics are existing-data results following analysis, not prospectively confirmed by this registration; 230 B2-flip Devign test raw labels were viewed, and B2-rand validation inference had begun. Later reruns do not erase these exposures. Future changes and analyses must be dated and disclosed in `CHANGES_AFTER_PREREG.md`; any claim of prospective confirmation applies only to a specific analysis demonstrably unperformed when OSF registration occurs.

### 1.1. OSF Existing Data Declarations

According to Open Science Framework (OSF) registration classifications:
- **Registration following analysis of the data:** Applies to Tier 1 arms (B0, B1, B2) on the test sets of Devign and ReVeal because exploratory metrics (MCC, AUROC) were computed during the exploratory phase. When Table B is generated, these historical contrasts must be marked "observed prior to registration"; the table has not yet been generated.
- **Registration prior to analysis of the data:** Applies only to each specified test analysis or contrast demonstrably unperformed at the actual OSF submission time, including eligible planned Table B/D analyses. It does not apply automatically to an entire tier or to the completed 60-prompt, two-rater review. B2-rand validation inference has begun, and 230 B2-flip Devign test raw labels were viewed before registration and are marked for rerun; those exposures remain disclosed even if the planned contrasts have not been computed.

### 1.2. Exposure Ledger & 3-Condition Audit for Keep vs. Rerun

In accordance with scientific advisory directives, the research team audited historical runs against three explicit conditions:
- **Condition 1 (Protocol match):** Cross-check the run manifest against `protocol.yaml`. All retained runs share checkpoint `Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf` (SHA-256 `f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335`), backend `llama-cpp-python 0.3.16`, context limit 8,192 tokens, and canonical Figure 6 prompt ordering.
- **Condition 2 (Logprob completeness and upper bounding):** All records store logprobs for tokens `0` and `1` to compute $s = \operatorname{sigmoid}(\operatorname{logit}_1 - \operatorname{logit}_0)$. For tokens absent from top-k (if any), a conservative upper bound $p \le p(\text{lowest token in top-}k)$ is applied alongside the `s_bounded` flag, ensuring a bounded rate $< 1\%$.
- **Condition 3 (B2-rep cache isolation):** Arm B2-rep has never run on GPU; when executed, `repeat: true` and `tag="repeat"` in diagnostic kit v1.1 are mandatory to isolate the cache, guaranteeing it never re-reads responses from the B2 cache.

| Arm | Dataset | Split | First Run (UTC) | Commit | Metrics Viewed | Matches Frozen Protocol? | Action |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **B0** | Devign | Val / Test | 2026-11-01T04:21:38Z | `7b045e7` | MCC, AUROC, CM | Yes (`yes`) | Retain (`keep`) |
| **B0** | ReVeal | Val / Test | 2026-11-01T04:21:38Z | `7b045e7` | MCC, AUROC, CM | Yes (`yes`) | Retain (`keep`) |
| **B1** | Devign | Val / Test | 2026-11-01T10:17:36Z | `0785f78` | MCC, AUROC | Yes (`yes`) | Retain (`keep`) |
| **B1** | ReVeal | Val / Test | 2026-11-01T10:17:36Z | `0785f78` | MCC, AUROC | Yes (`yes`) | Retain (`keep`) |
| **B2** | Devign | Val / Test | 2026-10-31T17:05:34Z | `8f48ea9` | MCC, AUROC, CM | Yes (`yes`) | Retain (`keep`) |
| **B2** | ReVeal | Val / Test | 2026-10-31T17:05:34Z | `8f48ea9` | MCC, AUROC, CM | Yes (`yes`) | Retain (`keep`) |
| **B2-flip** | Devign | Validation | 2026-11-01T14:46:02Z | `484b901` | None (`none`) | Yes (`yes`) | Retain (`keep`) |
| **B2-flip** | Devign | Test | 2026-11-01T14:46:02Z | `484b901` | Raw labels 230 samples | Yes (`yes`) | Rerun (`rerun`) |
| **B2-flip** | ReVeal | Validation | 2026-11-01T14:46:02Z | `484b901` | None (`none`) | Yes (`yes`) | Retain (`keep`) |
| **B2-flip** | ReVeal | Test | Unexecuted | None | None (`none`) | Yes (`yes`) | Retain (`keep`) |
| **B2-rep** | Both | Val / Test | Unexecuted | None | None (`none`) | Yes (`yes`) | Fresh run without cache (`rerun_repeat_only`) |
| **B2-rand** | Both | Validation | 2026-11-02T00:04:23Z | `484b901` | None (`none`) | Yes (`yes`) | Retain (`keep`) |
| **Remaining Tier 2–3 work** | Both | As applicable | Not yet executed; see B2-flip and B2-rand rows above | None | None (`none`) | Pending per run | Classify each planned analysis by its actual exposure at OSF submission |

---

## 2. Table of 11 Pre-registered Hypotheses (Table 4.3)

| ID | Hypothesis Name | Specification & Decision Criteria (Pre-declared Practical Margin $\delta$) |
| :--- | :--- | :--- |
| **H1.1** | GRACE does not outperform Zero-shot on Devign | Arm B2 (full GRACE) does not outperform B0 (zero-shot) in discriminative ability on Devign Test: Upper bound of 95% CI for $\Delta\text{MCC}(\text{B2} - \text{B0}) < 0.03$ and $\Delta\text{AUROC} < 0.02$ (practical margin $\delta = 0.02$). |
| **H1.2** | GRACE does not outperform Zero-shot on ReVeal & Fails to reach published baseline | Arm B2 does not outperform B0 on ReVeal Test: Upper bound of 95% CI for $\Delta\text{MCC}(\text{B2} - \text{B0}) < 0.03$ and $\Delta\text{AUROC} < 0.02$; GRACE fails to reproduce published performance in original paper: $\text{MCC}(\text{B2}) < 0.15$ on both datasets; $F_1(\text{B2})$ on Devign is lower than always-vulnerable baseline ($62.95\%$). |
| **H2.1** | Demonstrations act via surface labels | In-context demonstrations operate primarily through surface label priming: Net label sensitivity $\ge 15$ percentage points (proportion change when inverting labels $\text{B2} \leftrightarrow \text{B2-flip}$ minus natural variance $\text{B2} \leftrightarrow \text{B2-rep}$). |
| **H2.2** | Demo source code conveys no intrinsic signal | Demonstration source code adds no genuine signal: Upper bound of CI for $\Delta\text{AUROC}(\text{B2} - \text{B2-rand}) < 0.02$ and $\Delta\text{AUROC}(\text{B2-nolabel} - \text{B1}) < 0.02$; B2-labelonly recovers $\ge 80\%$ of the gap between B2 and B1. |
| **H2.3** | Contrastive pairs merely shift operating points | Contrastive demonstration pairing (B3) shifts operating decision points rather than increasing discriminative separation: B3 positive prediction rate is higher than B2 by $\ge 10$ percentage points while upper bound of 95% CI for $\Delta\text{AUROC}(\text{B3} - \text{B2}) < 0.02$. |
| **H3.1** | LLMs do not read Code Property Graphs | Textualized CPG information provides no additional signal to the LLM: Upper bound of CI for $\Delta\text{AUROC}(\text{B1} - \text{B0}) < 0.02$ and $\Delta\text{AUROC}(\text{B1} - \text{B1-shuf}) < 0.02$; B1-H2 shows no significant difference under the same criterion. |
| **H4.1** | Threshold-free evaluation indicates near-random performance | When evaluated threshold-independently (AUROC), the entire LLM pipeline performs near random guess level: $\text{AUROC} \le 0.62$ on both Devign and ReVeal across all LLM arms. |
| **H5.1** | Supervised baseline significantly outperforms LLM | Simple supervised classifier on frozen embeddings decisively outperforms LLM pipeline: $\Delta\text{MCC}(\text{SUP-LR} - \text{B2}) \ge 0.15$ with CI excluding 0; $\text{AUROC}(\text{SUP-LR}) \ge 0.68$. |
| **H5.2** | LLM provides no orthogonal post-query signal | LLM scores add no orthogonal signal after conditioning on 34 baseline features: Upper bound of 95% CI for $\Delta\text{MCC}(P_\text{post} - P_\text{pre}) < 0.02$ (identical 34 baseline features, identical StratifiedGroupKFold splits, identical threshold $\tau^*$). |
| **H5.3** | Unpredictable expert deferral (Routing $q=10\%$ Benefit vs Confidence & Complementarity) | At expert call budget $q=10\%$, Ridge Benefit Router does not outperform Confidence Router: Paired Bootstrap CI for $\Delta\text{Balanced Accuracy}(\text{benefit} - \text{confidence})$ and $\Delta\text{MCC}$ have upper bounds $< \delta = 0.02$ (verdict `no_meaningful_benefit`); additionally $\Delta\text{Balanced Accuracy}(\text{benefit} - \text{random})$ CI upper bound $< 0.01$; LLM error repairs do not exceed the 95th percentile of an equal-positive-rate random expert (20 seeds). |
| **H6.1** | Retrieval mechanism misalignment | Retrieved demonstrations rarely match the underlying vulnerability mechanism; relevance does not imply correctness: "Neither" rate $\ge 40\%$ on Devign; accuracy difference between related and unrelated demos has CI containing 0. |

### Pre-specified Verdict Interpretation for All Pairwise Contrasts ($\Delta = \text{metric}(B) - \text{metric}(A)$)

- **`benefit` (Evidence of benefit):** CI lies strictly above 0 ($\text{lower bound} > 0$) and $\Delta \ge \delta$.
- **`no_meaningful_benefit` (No meaningful benefit):** CI upper bound $< \delta$.
- **`harm` (Evidence of harm):** CI lies strictly below 0 ($\text{upper bound} < 0$).
- **`inconclusive` (Inconclusive evidence):** CI contains 0 or upper bound $\ge \delta$ while lower bound $\le 0$.

Pre-declared $\delta$ margins: General standard for practical equivalence margin is $\delta = 0.02$ (details: $\delta_\text{MCC} = 0.03$, $\delta_\text{AUROC} = 0.02$, $\delta_\text{BA} = 0.01$, $\delta_\text{MCC\_meta} = 0.02$, $\delta_\text{routing} = 0.02$).

---

## 3. Analysis Rules & Statistical Methodology (Section 6)

1. **Sanitization & Repository Freezing:**
   - Donor training data has all exact duplicate samples with validation and test sets removed (after normalizing whitespace and comments).
   - In the donor bank, keep one representative for duplicate code groups with matching labels; eliminate code groups with conflicting labels.
   - Near-duplicate pairs (Jaccard token 3-gram $\ge 0.9$) are flagged for sensitivity analysis (reported on both full test and deduplicated test).
2. **Locking 14 Optimal Decision Thresholds ($\tau^*$):**
   - Arbitrary thresholds are strictly prohibited.
   - Threshold optimization formula for dataset $d$, arm $a$, and seed $r$:
     $$\tau^*(d, a, r) = \operatorname{argmax}_{\tau \in \{0.01, 0.02, \dots, 0.99\}} \operatorname{MCC}(y_\text{val}(d), \mathbf{1}[s_\text{val}(d, a, r) \ge \tau])$$
   - **Tie-break rule:** In case of ties, select the threshold closest to 0.5 (`closest_to_0.5`); if tied in distance to 0.5, take the smaller threshold. Use only valid validation samples (`valid == True`); thresholds yielding undefined MCC (all predictions in one class) are discarded.
   - **Threshold Inheritance Rule:** Label intervention and repetition probes ($B2\text{-rep}$, $B2\text{-flip}$, $B3\text{-flip}$, $B3\text{-swap}$) **must not select $\tau^*$ independently on validation**, but instead directly inherit the locked $\tau^*$ of the corresponding base arm ($B2$ or $B3$). Re-optimizing thresholds for an arm with inverted labels or repetitions would "repair" the intervention effect and confound threshold tuning variance with the experimental treatment.
   - The following 14 threshold values are recorded in `configs/thresholds.json` and `Runs-management/thresholds.json`. The current `locked_sha256` is `9252aadebf19b0f86bd9da8e59992e2adebd87d386ab6600302b9ac10a2914a3`; `a0108431ad859aacc3dab29ca7e88a7eb404428b4d60fc251e3bbae7d350c831` is the prior lock identity, retained for provenance. The protocol disclosure was corrected and the lock resealed on 2026-11-03 without refitting any of the 14 values. They were selected on validation; the reseal is **not** evidence that the lock preceded historical test inference:
     - **Devign LLM Arms**: `devign|B0|42` = 0.08, `devign|B1|42` = 0.88, `devign|B2|42` = 0.70, `devign|B2-flip|42` = 0.70 (inherited from B2), `devign|B2-rep|42` = 0.70 (inherited from B2).
     - **ReVeal LLM Arms**: `reveal|B0|42` = 0.44, `reveal|B1|42` = 0.74, `reveal|B2|42` = 0.12, `reveal|B2-flip|42` = 0.12 (inherited from B2), `reveal|B2-rep|42` = 0.12 (inherited from B2).
     - **Meta-Models**: `devign|P-PRE|42` = 0.54, `devign|P-POST|42` = 0.60; `reveal|P-PRE|42` = 0.38, `reveal|P-POST|42` = 0.10.
3. **Confirmatory Statistics & Pairwise Contrasts (Table B):**
   - Paired Bootstrap $B = 5000$ iterations with fixed seed `20261117`.
   - Cluster Units:
     - **Devign:** Cluster Bootstrap by `commit_id` (2,068 independent clusters on Test $N = 2,732$).
     - **ReVeal:** Cluster Bootstrap by File-level Hashes (`file_hash`, 646 independent clusters on Test $N = 2,274$, completely resolving the chrome/debian cluster collapse risk identified in Step 0).
   - Meta-model fold splitting: `StratifiedGroupKFold` (3 folds) on Validation ensuring independence of code groups.
   - Family-wise error rate control: Holm-Bonferroni method (`family_correction: holm`).
4. **Complementarity & Routing Analysis:**
   - 34 baseline features $P_\text{pre}$ include 5 foundation model logits, ensemble probability $p$, $|p - 0.5|$, MLP-Lexical discrepancy, and 26 code metrics.
   - 4 LLM features include: continuous score $s$, `valid` flag of candidate **score**, interaction $s \cdot p$, and discrepancy $s - p$. When no valid score is available, the meta-model uses symmetric fallback ($s = 0.5, valid = 0$); raw greedy `response_valid` is reported separately.
   - Meta-model employs Logistic Regression ($C = 1.0$), 3-fold Out-Of-Fold (OOF).
   - Routing evaluation at 5%, 10%, 25% expert call budgets with direct Paired Bootstrap CI between Benefit Router vs. Confidence Router, 20 random seeds for RANDOM baseline, and Oracle ceiling.

---

## 4. 15 Experimental Arms Matrix & Probe Construction Rules (Section 6.3)

| Tier | Arm ID | Prompt Content & Probe Specification | Difference Relative to Base Arm | Corresponding RQ |
| :--- | :--- | :--- | :--- | :--- |
| **Floor & Anchors** | ALL-0, ALL-1, RAND | Predict constant 0, constant 1, or random sampling matching label prior | No LLM call; label distribution baseline | All |
| **Floor & Anchors** | SUP-LR, SUP-MLP, SUP-METRIC | Logistic Regression on CodeT5 768d, MLP 768→128→1, LR on 26 code metrics | Supervised anchor on frozen embeddings (3 seeds: 42, 43, 44) | RQ5 |
| **Tier 1** | **B0** | Role + domain + target code + binary question | Zero-shot; no CPG graph, no demonstration | RQ1 |
| **Tier 1** | **B1** | B0 + CPG nodes & edges (prefix 40 nodes / 80 edges) | Adds textualized CPG graph as reimplemented | RQ1, RQ3 |
| **Tier 1** | **B2** | B1 + 1 demonstration retrieved from clean donor bank with true label | Full GRACE pipeline | RQ1, RQ2 |
| **Tier 1** | **B2-flip** | B2 with inverted demonstration label ($1 \leftrightarrow 0$) in prompt | Measures net label sensitivity | RQ2 |
| **Tier 1** | **B2-rep** | B2 repeated with identical prompt (bypassing cache) | Measures natural variance from batching / GPU nondeterminism | RQ2 |
| **Tier 2** | **B2-rand** | B1 + 1 random demonstration from clean donor bank with true label | Demonstration code unrelated to mechanism (3 seeds: 42, 43, 44) | RQ2 |
| **Tier 2** | **B2-nolabel** | B1 + retrieved demonstration; prompt altered to "The following is a related example." (unlabelled) | Strips demonstration label | RQ2 |
| **Tier 2** | **B2-labelonly** | B1 + prompt "A function similar to the one above was labelled Vulnerable/Non-vulnerable." (no code) | Surface label priming prompt only | RQ2 |
| **Tier 2** | **B1-shuf** | B0 + CPG from an unrelated function with matched node count ($\pm 10\%$), same budget | Graph conveys no target semantics (3 seeds: 42, 43, 44) | RQ3 |
| **Tier 3** | **B1-full** | B0 + CPG expanding up to full 1,500 token budget | Altered graph truncation policy (larger node prefix) | RQ3 |
| **Tier 3** | **B1-H2** | B0 + H2 guarded execution evidence cluster packed to 1,500 tokens | Packages execution trace paths instead of raw prefix | RQ3 |
| **Tier 3** | **B3** | B1 + contrastive demo pair (1 vuln, 1 safe) + Key difference block | Proposed Contrastive ICL method | RQ2, RQ4 |
| **Tier 3** | **B3-nodiff** | B3 with Key difference block omitted | Isolates effect of differential explanation block | RQ2 |
| **Tier 3** | **B3-swap** | B3 with order of the two contrastive demonstrations swapped | Measures recency / order bias | RQ2 |
| **Tier 3** | **B3-flip** | B3 with labels of both demonstrations inverted ($1 \leftrightarrow 0$) | Measures label sensitivity under balanced demonstration design | RQ2 |

---

## 5. Prompt Contract, Token Budget & Section Ordering (Figure 6 & Section 6.4)

1. **Canonical Section Ordering (Figure 6 & Author Code):**
   `[role_domain, target_code, question, node_info, edge_info, demonstration, answer]`
   *Invariant rule: Target code comes first, graph in the middle, demonstration at the end immediately preceding the answer prompt. Target labels never appear in the prompt.*
2. **Maximum Token Budget (8,192 Token Context):**
   - Target source code: $\le 3,000$ tokens.
   - Demonstration: $\le 1,500$ tokens per demo.
   - CPG Graph: $\le 1,500$ tokens.
   - Reserve: $64$ tokens.
   - Measurement unit: Strictly measured via the model's tokenizer (`Qwen3-Coder-30B-A3B-Instruct`).
3. **Output, Score & Validity for Executed Inference:**
   - The Kaggle notebook invokes `llama-cpp-python` directly, reading all logits at the first token position after the prompt; resolves separate token IDs for `0` and `1`, then computes `logprob_0`, `logprob_1`. Continuous score $s = \frac{p(1)}{p(0)+p(1)} = \operatorname{sigmoid}(\operatorname{logit}_1-\operatorname{logit}_0)$. The `top5` dictionary is preserved for diagnostics, **not** as a prerequisite for score extraction.
   - `valid` is the **score validity** flag: both token IDs must be resolvable, distinct, within vocabulary; logits must be finite and $s$ computable. If logits are missing, non-finite, tokenizer mismatched, or backend fails, no valid score exists; score is not forced to 0. In the current notebook, pre-record errors abort the run or checkpoint completed records, rather than creating artificial `valid=false` records.
   - `raw` is the greedy token over the **entire vocabulary**; `response_valid = true` strictly when decoded raw is `'0'` or `'1'`. Raw differing from both labels can occur even when `valid=true` and $s$ is finite. Separately report counts/rates of `valid` and `response_valid`; finite scores are not discarded merely because raw is non-compliant. `pred_argmax` of the score uses $s \ge 0.5$; when evaluated against locked thresholds, $s \ge \tau^*$ is used, without confounding these predictions with raw greedy output.
   - The legacy OpenAI-compatible parser in `llm_backend.py` used `top_logprobs` requiring **both tokens `0` and `1`** in top-k. That rule pertained to legacy API mode, not the Kaggle notebook's full logit scoring.

---

## 6. Stopping Rules

1. **SUP-LR Advantage Disappears:** If after deduplication and label auditing SUP-LR no longer significantly outperforms B2, halt the study to review preprocessing before drafting.
2. **Prompt Audit Failure:** If empty demonstration rate $> 1\%$, missing graph rate $> 5\%$ (excluding flagged Joern errors), or target label leakage $> 0$, halt pipeline, correct prompt contract, and rerun all affected arms.
3. **Backend Smoke Test Failure:** If valid response rate containing token 0/1 in top-5 logprob $< 99\%$, do not execute confirmatory matrix until backend achieves quantitative stability. This is Step 1 API smoke test criteria, not the validity definition in Kaggle full-logit inference.
4. **Prospective Protocol Freeze:** From the documented freeze onward, changes to arms, models or thresholds require a dated amendment and explicit exploratory classification. This rule does not retroactively describe the already exposed Tier 1/B2-flip test runs. Any later analyses outside the registered plan must be labeled "exploratory post-hoc" in the final manuscript.

---

## 7. Frozen Hashes, Manifests & Provenance Tables

### 7.1. SHA-256 Checksum Table for Data & Manifests

| Dataset | Partition / Asset | Rows (Samples) | Positive Rate (Vuln) | File Path / Permanent Link | SHA-256 Hash |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Devign** | Raw Train | 21,854 | 45.84% | [`data/raw/devign_train.jsonl`](https://github.com/kazunguyen/GRACE-summary/blob/prereg-v1/01_Author_Baseline_Unified/output/research_freeze_20261101/devign/train_raw.jsonl) | `e456e20da10aa9a30df406d78dcf5f15f91da8c49fd5028584ca248b03f13f35` |
| **Devign** | Raw Validation | 2,732 | 43.45% | [`data/raw/devign_validation.jsonl`](https://github.com/kazunguyen/GRACE-summary/blob/prereg-v1/01_Author_Baseline_Unified/output/research_freeze_20261101/devign/validation_raw.jsonl) | `7318bc4aab8fecdac3ce1afe51c7833714be1b807c5437ab2c7dc0384a6543e0` |
| **Devign** | Raw Test | 2,732 | 45.94% | [`data/raw/devign_test.jsonl`](https://github.com/kazunguyen/GRACE-summary/blob/prereg-v1/01_Author_Baseline_Unified/output/research_freeze_20261101/devign/test_raw.jsonl) | `7f77094d9328624036cbd43ab1281aaf0c3378e220d5b3a10ba0a98922ab39c6` |
| **Devign** | Clean Donors Bank | 21,691 | 45.91% | [`data/manifests/devign_donor_clean.jsonl`](https://drive.google.com/file/d/10f_cARhg4BoMeIn4Q57qLzGiQuZUv00_/view?usp=sharing) | `5eda46695ea98091168c2a87591010b4fe6c08597a376c3361b4cf40297d1dfe` |
| **Devign** | **Manifest Concatenation** | - | - | [`data/manifests/devign_manifest_stats.json`](https://github.com/kazunguyen/GRACE-summary/blob/prereg-v1/01_Author_Baseline_Unified/output/research_freeze_20261101/devign/stats.json) | **`5a084a10e5c191039e56e351bf8d722fe017424f159a84d6b92be86a1d0f4952`** |
| **Devign** | Val Subset 600 (Seed 42) | 600 | 43.50% | [`data/specs/devign_val_subset600.jsonl`](https://github.com/kazunguyen/GRACE-summary/blob/prereg-v1/data/specs/devign_val_subset600.jsonl) | `88f749c000a7b110ed87641d9d5dc4bc912b9f2fdb3dcc2a97753238a4dbcdfd` |
| **Devign** | Test Specs | 2,732 | 45.94% | `data/specs/devign_test.jsonl` | `bd0f4d025afd051c064ab58c1495a887c5851b6408e2d47d39ae64d421b898c6` |
| **ReVeal** | Raw Train | 18,187 | 9.90% | [`data/raw/reveal_train.jsonl`](https://github.com/kazunguyen/GRACE-summary/blob/prereg-v1/01_Author_Baseline_Unified/output/research_freeze_20261101/reveal/train_raw.jsonl) | `87c6ec979d8724d1db25217ae6c5637fedaca5350fc954baab4c615efc56f66c` |
| **ReVeal** | Raw Validation | 2,273 | 9.24% | [`data/raw/reveal_validation.jsonl`](https://github.com/kazunguyen/GRACE-summary/blob/prereg-v1/01_Author_Baseline_Unified/output/research_freeze_20261101/reveal/validation_raw.jsonl) | `03ccd535ecc5c85601377d1880f05307d20577e195cc8808d2c5cbd880725d50` |
| **ReVeal** | Raw Test | 2,274 | 10.11% | [`data/raw/reveal_test.jsonl`](https://github.com/kazunguyen/GRACE-summary/blob/prereg-v1/01_Author_Baseline_Unified/output/research_freeze_20261101/reveal/test_raw.jsonl) | `5132c4a2cab7cea81435b5039af964cab184e6ce7b4d9e2df524962b0f6d45f3` |
| **ReVeal** | Clean Donors Bank | 17,636 | 9.57% | [`data/manifests/reveal_donor_clean.jsonl`](https://drive.google.com/file/d/162syKwALRE2EvMbP5bBHA4P9eis30hjA/view?usp=sharing) | `9e891cf5b8dfa93c2c3d9d5039e328c5d36c115d173051c5991fc0939e1d372d` |
| **ReVeal** | **Manifest Concatenation** | - | - | [`data/manifests/reveal_manifest_stats.json`](https://github.com/kazunguyen/GRACE-summary/blob/prereg-v1/01_Author_Baseline_Unified/output/research_freeze_20261101/reveal/stats.json) | **`59498c4a4ab038babe558675c183c2b104b0145590fb0accf8b02cd5440d57f7`** |
| **ReVeal** | Val Subset 600 (Seed 42) | 600 | 9.17% | [`data/specs/reveal_val_subset600.jsonl`](https://github.com/kazunguyen/GRACE-summary/blob/prereg-v1/data/specs/reveal_val_subset600.jsonl) | `72ce24b2629588a7edf5206c99b26865b630a489580a6b03964c368fad79858e` |
| **ReVeal** | Test Specs | 2,274 | 10.11% | `data/specs/reveal_test.jsonl` | `26d79cec7a31e45a99cf8f22266aa793f323eacb6328cf8d5bd2fc1b34131deb` |

**Artifact Reconciliation Note:** Display names in the path column follow the preregistration protocol; GitHub links resolve to frozen raw/stats artifacts under snapshot `research_freeze_20261101`, while the two Google Drive links point to `donors.jsonl` files from the same snapshot (Devign SHA-256 `7727d2793fbb9f305e547bd6e7126ae70f2e0ee97e2b7c5c260322c6b6af5a62`; ReVeal SHA-256 `6bf44ab86c8524d239e610fdccff5916cfc402fef7945d7cbe7f695e287abbce`). The printed SHA-256 values are historical manifest checkpoints and do not match the bytes of every linked raw/stats/donor artifact; they must not be used to authenticate those links. The two standardized 600-sample validation subsets `data/specs/devign_val_subset600.jsonl` (SHA-256 `88f749c000a7b110ed87641d9d5dc4bc912b9f2fdb3dcc2a97753238a4dbcdfd`) and `data/specs/reveal_val_subset600.jsonl` (SHA-256 `72ce24b2629588a7edf5206c99b26865b630a489580a6b03964c368fad79858e`) match 100% exactly with the table above and have explicit `.gitignore` inclusion exceptions.

### 7.2. Model Checkpoint & Inference Environment (Standardized Provenance)

- **Architecture and tokenizer:** `Qwen/Qwen3-Coder-30B-A3B-Instruct`; tokenizer at revision `b2cff646eb4bb1d68355c01b18ae02e7cf42d120`.
- **Model weights:** GGUF from `ggml-org/Qwen3-Coder-30B-A3B-Instruct-GGUF`, file `Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf`, quantization `Q4_K_M`, SHA-256 `f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335`. Manifests of executed B0, B1, B2, B2-flip, and B2-rand runs record this exact identifier.
- **Inference backend:** `llama-cpp-python 0.3.16` invoking `Llama(...)` directly on Kaggle GPU 2× Tesla T4, with `n_ctx=8192`, `n_batch=256`, `n_gpu_layers=-1`, `logits_all=True`; scoring from first token logits of labels `0` and `1`. This matches the configuration in notebooks and run manifests, distinct from REST/Cloudflare `llama-server`.
- **Kaggle model source:** Notebook B2 resolves the GGUF file in output of `quangdung1111/qwen3coder30b-prepare-notebook`; other arm notebooks attach the GGUF file as input and verify SHA-256 prior to inference. Slug `tnthnhneee/qwen3-30b-a3b/gguf/coder-instruct-ud-q4_k_xl` in old protocol drafts does not identify the executed `Q4_K_M` file.
- **Fallback model scope:** None of the reconciled inference runs B0/B1/B2/B2-flip/B2-rand used vLLM or Qwen2.5-Coder. Those options in `protocol.yaml` were prospective fallbacks and are not combined with GGUF results.
- **Note on locked files:** Both `protocol.yaml` files are preserved as historical artifacts because `thresholds.json` stores the locked protocol SHA-256. This section represents post-hoc reconciliation against notebooks and outputs without altering the timing or contents of the locked protocol.

---

## 8. Pre-registration Acceptance Checklist (Appendix C - Proposal)

This appendix also tracks deliverables scheduled after registration. An unchecked later-stage item records work still to be done; it does not by itself establish whether the OSF submission is ready.

- [x] **Step 0:** Historical metrics reproduced from sample-level files (discrepancy $\le 0.001$); repair-harm table includes ALL-0 / ALL-1 / RANDOM rows; paired bootstrap 5,000 reps; cluster unit resolved: Devign (2,068 commit groups), ReVeal (646 file hash groups); StratifiedGroupKFold OOF; Paired Bootstrap CI for Routing q=10% (Benefit vs Confidence).
- [x] **Backend Smoke Test (measured scope):** In 20 sampled prompts, both tokens 0 and 1 appeared in top-5 logprobs (100%); repeated-call agreement was 100%, and throughput/latency were measured. The planned top-20 API criterion and fail-fast behavior have not been independently verified by this report.
- [x] **Data Manifests (scope stated):** The deduplication audit excluded 18 Devign and 129 ReVeal cases; the sanitized donor banks contain 21,691 and 17,636 samples. Frozen manifests exist, but SHA-256 values printed in Table 7.1 do not authenticate every linked raw/stats/donor file; see the artifact reconciliation note below that table.
- [x] **Tests & Prompt Audit (available artifacts):** Tests and automatic checks passed for the artifacts inspected; the review packet contains 30 prompts per dataset, and two reviewers completed the 60-prompt assessment. No unresolved label leaks remain within that inspected scope. The full 15-arm validation dry-run is not complete: five arms remain blocked; this checkmark does not assert full-study prompt acceptance.
- [x] **Research Protocol and Exposure Disclosure:** Current protocol and `preregistration.md` are documented under `prereg-v1` for OSF submission; actual OSF submission is pending. Tier 1 test inference and exploratory metrics predate submission and are declared as existing data following analysis.
- [x] **Current Threshold Record (Step 5):** The 14 $\tau^*$ values are documented as validation-selected in `thresholds.json` with current `locked_sha256` `9252aadebf19b0f86bd9da8e59992e2adebd87d386ab6600302b9ac10a2914a3`; the prior identity remains in `previous_locked_sha256`. The 2026-11-03 reseal did not refit thresholds and does not establish a lock before historical test runs. Repeated/inverted probes ($B2\text{-flip}$, $B2\text{-rep}$, $B3\text{-flip}$, $B3\text{-swap}$) inherit the base-arm $\tau^*$ under the current protocol. Historical Tier 1 test results remain disclosed as following analysis.
- [x] **Test Exposure Ledger (documented history):** `exposure_ledger` records the known executed arms, datasets, splits, first-run times, viewed results and retain/rerun decisions. Its identity flags require case-by-case verification against historical run manifests; B2-rep has not yet run, so no B2-rep cache reuse has occurred.
- [ ] **Execution Schema B.2:** B1 and the frozen-donor B2 each have 10,011 records with unique IDs, scores, both digit logprobs, and a `run_manifest.json`. Their Kaggle fields differ from B.2: `prompt_sha256` and a nested `tokens` object replace B.2 field names; `truncated`, `both_in_topk`, `s_bounded`, `cache_tag`, and `group` are absent. The run manifests do not record the protocol/specs hashes required by the kit's `manifest.json`. Preserve the raw outputs; validate a separate normalized copy against B.2, join groups from the frozen manifests by ID, and mark unrecoverable fields unknown. Cache identity and remaining runs still require verification.
- [ ] **Meta-Models & Routing Step 6:** Historical Step 0 is complete within its stated scope: it reports P_pre/P_post, oracle/random routing curves, and a 5,000-replicate paired cluster-bootstrap CI for benefit versus confidence at q=10% on both datasets. Its historical DeepSeek expert does not substitute for the Qwen expert in Step 6. No three-seed SUP-LR/SUP-MLP/SUP-METRIC score artifact or completed Qwen-based P_pre/P_post and routing result is available for this campaign.
- [ ] **Final Evaluation & Tables A/B/C/D:** No complete final Tables A–D or both figure types have been generated and verified for this campaign. The current `evaluate_final.py` implements Tables A–C and figures but not Table D from Step 6, and Table B does not yet emit the proposal's prior-test-exposure status. Table C also requires B2-rep for its B3 pair. Complete the inputs and script, then verify rows, contrasts, verdicts, and degenerate-bootstrap counts; a CSV file alone is not evidence of a complete table.
- [x] **11 Scientific Hypotheses Cross-Check:** Table 4.3 documents support / reject / inconclusive criteria and practical margin $\delta$ for the current plan. These criteria are not claimed to predate historical Tier 1 test exposure; prospective status must be assessed separately for each still-unperformed contrast.
- [ ] **Blind Review & Label Audit (Step 8):** Two reviewers completed the 60-prompt packet and adjudication ($\kappa$ recorded). Conditional analysis tables and the 100-case-per-dataset label audit remain unfinished; this combined acceptance item stays unchecked.
- [x] **OSF Bundle Assembly & Hash Verification:** The ZIP contains 40 artifacts plus `attachment_sha256.json`; extraction and SHA-256 verification succeeded. Reproduction on an independent clean machine and a separate credential scan have not been established by this checkmark.
