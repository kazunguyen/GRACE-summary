# 2026-11-06 — Các câu trả lời cập nhật đăng ký OSF của GRACE

Ngày worklog: **06/11/2026**.

Hồ sơ revision: 6aedfc2fb06257287680bc5e.

Bản chép gồm Justification và đủ 14 câu hỏi xuất hiện trong danh sách các câu hỏi đã sửa trên trang Review. Nội dung tiếng Anh trong từng ô được giữ theo bản Review đã sao chép, kể cả các đoạn cũ còn sót tại thời điểm sao chép. Người nộp sau đó xác nhận đã gửi update. Chưa có bản xuất của revision sau khi nộp để đối chiếu nguyên văn.

Các nội dung được đề xuất sửa sau khi rà Review nằm ở cuối file. Ngày worklog dùng để lưu hồ sơ. Thời điểm nộp do OSF ghi nhận.

## Justification

### Justification for update

```text
We request a transparent amendment to the existing GRACE registration to (1) correct B0/B1 decision thresholds that were carried into the submitted threshold table as fixed values rather than recomputed from the complete validation splits; (2) document the validation-only threshold-selection procedure for the already registered B1-H2 arm, whose numeric thresholds were absent from the original 14-value lock; and (3) replace the B3 demonstration-pair construction and difference-generation procedure with a verified same-function, vulnerable/patched design. The registered Kaggle environment with two Tesla T4 GPUs remains the execution environment for all arms; this update does not request Colab as an alternative platform. This is an amendment to an ongoing study. B0/B1/B2/B2-flip inference outputs and metrics, and a post-hoc reanalysis including validation-selected thresholds and paired bootstrap contrasts, existed before this amendment. B1-H2 validation and test inference were also performed on Colab L4 as platform-deviant exploratory runs. The resulting Colab thresholds (Devign 0.09; ReVeal 0.67) and Colab test inference are disclosed as exploratory and superseded. The complete B1-H2 Kaggle validation census is now finished: Devign selected tau=0.09 (MCC 0.066793, n=2,732); ReVeal selected tau=0.21 (MCC 0.083632, n=2,273). The Devign value coincides numerically with the old Colab value but was independently selected from Kaggle validation records; the ReVeal value differs. No test records, labels or metrics were read for this Kaggle threshold selection. These activities and deviations are disclosed retrospectively; this update does not establish that they were preregistered before execution or analysis. The original registration and its PDF/ZIP attachments remain preserved. The revised methods below apply from the actual amendment date to the work to which they relate. Hypotheses, sample sizes, data partitions, model weights, quantization, tokenizer, scoring, decoding, seeds, statistical decision rules and the registered Kaggle execution environment remain as registered except for the specific threshold and B3 method changes stated below. Reproducible validation-only threshold evidence is archived at commit d9127fc7b12a128d8499012454ad134733f810ff. The original optimizer is byte-identical to the 1 November implementation. The verifier reproduces all four corrected thresholds using complete validation only; source/input hashes and file-read audits are provided: https://github.com/kazunguyen/GRACE-summary/blob/d9127fc7b12a128d8499012454ad134733f810ff/Runs-management/osf_amendment_20261106/README.md B1-H2 was already specified in the registered experimental matrix, but it was absent from the original 14-value threshold lock. The complete Kaggle validation census has now supplied a validation-only lock: Devign tau=0.09 (MCC 0.0667928192, n=2,732) and ReVeal tau=0.21 (MCC 0.0836323479, n=2,273). Predictions were joined to the frozen labels by exact ID and checked against prompt hashes; all 99 registered MCC grid points and tie-breaks were independently reproduced. The Devign value happens to equal the preliminary Colab value, while ReVeal differs from Colab's 0.67; neither Kaggle value was copied from the Colab lock. The old Colab test inference and lock remain exploratory and superseded. No test records, labels or metrics were read for this threshold selection. The Kaggle evidence is identified under E19-E22.
```

## Overview

### Explanation of foreknowledge and managing unintended influences

```text
TEST EXPOSURE DISCLOSURE & EXPOSURE LEDGER
Status as of 6 November 2026

1. Prior data exposure

The Devign (N=2,732) and REVEAL (N=2,274) test sets had previously been accessed during exploratory work, including exploratory API runs, a dev-100 subset, and preliminary H1-H3 motivation measurements for Tier 1 arms B0, B1, and B2. Full validation and test inference outputs for B0, B1, B2, and B2-flip existed before this amendment. A post-hoc reanalysis of validation thresholds, test metrics, sensitivity results, and selected paired-bootstrap contrasts was also completed and inspected before this amendment. This update is therefore retrospective with respect to those activities; it does not represent those analyses as having been conducted before any test exposure.

2. Threshold and analysis disclosures

The original threshold lock contained 14 values and did not include B1-H2. This amendment corrects four B0/B1 threshold values using the complete official validation splits and adds validation-selected thresholds for the already registered B1-H2 arm. The B1-H2 Kaggle validation-only thresholds are Devign tau=0.09 (MCC=0.0667928192, n=2,732) and REVEAL tau=0.21 (MCC=0.0836323479, n=2,273). No test records, labels, or metrics were read for this Kaggle threshold selection. The Devign value coincides numerically with the earlier Colab value; the REVEAL value differs from the superseded Colab value of 0.67. The earlier Colab threshold lock and test inference are disclosed as exploratory, platform-deviant work and are not the source of the current Kaggle thresholds.

The 6 November post-hoc reanalysis included test metrics and selected paired-bootstrap contrasts. It is not equivalent to completion of the confirmatory Holm analysis of all 11 registered contrasts. Historical test exposure and analyses remain disclosed; the safeguards below do not erase or retroactively prevent that exposure.

3. Platform and method deviations

B1-H2 validation and test inference were previously run on Colab L4 as exploratory work, although Kaggle with two Tesla T4 GPUs is the registered execution platform. A complete B1-H2 validation census has since been completed on Kaggle. Any new confirmatory B1-H2 test inference will use Kaggle and the validation-only thresholds stated above.

The B3 demonstration-pair construction and difference-generation method is being amended to use a verified same-function vulnerable/patched design. The amended B3 algorithm has been implemented, but no verified inference output from the amended B3 method is established here. Any output from the prior B3 method will remain separately identified and will not be combined with output from the amended method.

4. Run status

B0, B1, B2, and B2-flip have validation and test inference outputs on both datasets. The latest checked B2-rand status recorded for this update was 7,789/15,015 validation records; no B2-rand test output was recorded in that status check. B2-rep had not been executed on GPU in the local run ledger at that check. Other arm-level execution status is recorded in the versioned run ledger and progress evidence; it should not be inferred from the former blanket statement that all Tier 2-3 arms were unexecuted or that all analyses preceded execution.

5. Risk-reduction and provenance

Threshold selection for the corrected values described in this amendment uses validation data only, with the registered 0.01-0.99 MCC search grid and tie-break rule. The verification artifacts preserve the relevant source and input hashes and document the files read. This supports the provenance of these specific validation-only threshold selections; it does not establish that all earlier test exposure or analyses were prospective.

The validation-threshold evidence, B1-H2 Kaggle lock, Colab exploratory-run audit, reanalysis, amended B3 implementation, and arm-level progress records are linked in the immutable evidence references in the updated registration materials. The original registration and its submitted PDF/ZIP attachments remain unchanged.
```

## Research Design

### Study design

```text
15-arm observational benchmark replication experiment. The study includes graph-representation ablations (B0, B1, B1-shuf, B1-full, B1-H2), demonstration-content ablations (B2, B2-rand, B2-nolabel, B2-labelonly, B2-flip, B2-rep), and contrastive-pair arms (B3, B3-nodiff, B3-swap, B3-flip), alongside three supervised frozen-embedding baselines (SUP-LR, SUP-MLP, SUP-METRIC) and two meta-models (P-PRE, P-POST).

B3 method amendment: This replaces the previously registered B3 demonstration-pair construction and difference-generation procedure. An eligible pair consists of vulnerable and patched versions of the same source function across an identified security-fix commit. Both examples must come from the frozen clean training donor bank; targets and validation/test functions are excluded. Each pair must be checked against the source diff and security rationale by two reviewers, with disagreements resolved before admission.

For each target, eligible pairs are ranked deterministically using the mean token-set Jaccard similarity between the target and each function; the highest-scoring pair is selected, with exact ties resolved by stable pair ID. Target labels and validation/test performance are not used to select donors or alter this rule. The Key difference must be supported by the verified source diff. The existing section order, tokenizer, token budget, graph input, output schema, and scoring remain unchanged. Amended B3-family prompts will be frozen and hashed before inference.

The B3 hypotheses and outcome definitions remain unchanged. The amended selector algorithm is implemented, but no real pair has yet been approved, no amended real prompt set has been frozen, and no amended B3 inference or threshold fitting is claimed as complete. B3 execution remains paused until eligible source pairs are authenticated and reviewed within the frozen donor bank.
```

### Randomization

```text
The study employs a fully paired, within-subject experimental design where all test instances are evaluated across all active experimental arms (no random assignment of samples to arms).

For components requiring pseudo-randomization:
1. Stochastic Ablation Arms: Arm B2-rand (random demonstration donor sampling from clean train bank) and Arm B1-shuf (CPG graph node/edge permuting) use fixed pre-registered pseudo-random seeds (primary seed 42, evaluated across seeds 42, 43, 44).
2. Supervised Baselines & Meta-Models: StratifiedGroupKFold cross-validation (grouped by commit_id / file_hash) and baseline training (SUP-LR, SUP-MLP) use fixed seeds (42, 43, 44).
3. Statistical Estimation: Paired cluster bootstrap resamples (B=5,000 iterations) are executed with a strictly locked random seed 20261117.
4. Routing Baselines: Equal-rate random expert baseline is evaluated across 20 pre-specified random seeds.
5. LLM Sampling: Temperature is fixed to 0.0 (greedy decoding) to enforce deterministic output generation.

For amended B3, eligible demonstration pairs are selected deterministically using the ranking and tie-break rule described in the Study Design. This changes donor-pair selection; it does not change assignment of test instances to experimental arms or the registered seeds for other components.
```

## Sampling

### Data collection procedures

```text
Data are drawn from two standard, publicly available C/C++ vulnerability detection benchmarks:
1. Devign (FFmpeg and QEMU repositories, curated via Joern Code Property Graphs; N=5,464).
2. REVEAL (Chromium and Linux Debian kernel vulnerabilities; N=4,547).

Rigorous Pre-processing and Data Sanitization:
- Exact Deduplication: All donor functions in the retrieval bank sharing exact code overlap (normalized by stripping whitespace, newlines, and comments) with any validation or test instance were purged to guarantee zero-leakage retrieval (108 Devign and 52 REVEAL duplicates removed).
- Conflict Removal: Duplicate code instances with conflicting vulnerability labels were purged; clean clusters retain a single canonical instance.
- Near-Duplicate Auditing: Near-duplicates (token 3-gram Jaccard similarity >= 0.9) are flagged; confirmatory results will be reported on both full test and near-deduplicated test splits.
- Clean Donor Retrieval Banks: Devign clean donor bank contains 21,691 functions; REVEAL clean donor bank contains 17,636 functions.

Prompt Packaging and Token Budgets:
- Prompts follow the canonical canonical order from Figure 6 of the original GRACE publication: [system_role -> target_code -> question -> graph_node_info -> graph_edge_info -> demonstration -> answer].
- Context window: Fixed at n_ctx = 8,192 tokens under Qwen3-Coder-30B-A3B-Instruct BPE tokenizer (Target code <= 3,000; Demonstrations <= 1,500; CPG graph <= 1,500; Reserve = 64 tokens; Graph prefix caps = 40 nodes, 80 edges).
- Pre-execution Audit: All 10,011 prompts across 15 arms underwent automated integrity auditing to ensure zero label leakage, syntax integrity, and that no demonstration is silently truncated below 25% of original length.

Execution Environment:
- Inference is served via llama-server (llama.cpp b3920) with Qwen3-Coder-30B-A3B-Instruct GGUF Q4_K_M (SHA-256: f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335) under temperature 0.0. All decision thresholds (tau*) are strictly pre-computed and locked on the official validation splits prior to test evaluation under a zero-test-exposure protocol.

B3 amendment: Candidate demonstration pairs will be drawn only from the corresponding frozen clean training donor bank. Each eligible pair must contain vulnerable and patched versions of the same source function across an identified security-fix commit, supported by source-diff and security-rationale evidence. Two reviewers must assess each pair and resolve disagreements before admission. Targets and validation/test instances are excluded from the donor pool; no external donor dataset is introduced. If an adequate verified pair pool cannot be established under these restrictions, B3 remains paused. As of this update, no real pair has been approved and no amended B3 prompt set or inference output is claimed as complete.
```

### Sample size

```text
The planned sample is a census of the official benchmark partitions without downsampling. The counts below describe the study design; they do not imply that every arm has completed inference.

1. Devign Benchmark:
   - Total benchmark sample: N = 5,464 C/C++ functions.
   - Validation split: N = 2,732 functions.
   - Test split: N = 2,732 functions. The original design designated this as the test evaluation split. Prior test exposure, inference, and reanalysis are disclosed elsewhere in this update; this amendment does not describe the test data as wholly unobserved.
   - Clustering structure: 2,068 unique commit_id clusters in the test split.
   - Retrieval donor bank: 21,691 clean training functions.

2. REVEAL Benchmark:
   - Total benchmark sample: N = 4,547 C/C++ functions.
   - Validation split: N = 2,273 functions.
   - Test split: N = 2,274 functions. The original design designated this as the test evaluation split. Prior test exposure, inference, and reanalysis are disclosed elsewhere in this update; this amendment does not describe the test data as wholly unobserved.
   - Clustering structure: 646 unique file_hash clusters in the test split.
   - Retrieval donor bank: 17,636 clean training functions.

3. Threshold record:
   - The original threshold lock contained 14 values and omitted B1-H2. The amended lock contains two additional B1-H2 values and corrects four B0/B1 values.
   - The corrected B0/B1 values and the B1-H2 values are documented in the Analysis Plan. The B1-H2 values were selected using the complete Kaggle validation splits only: Devign tau=0.09 and REVEAL tau=0.21. No test records, labels, or metrics were read to select these B1-H2 thresholds.
   - This description does not imply that all threshold values were newly recomputed as part of this amendment.

4. Unit of analysis and planned design:
   - Unit of analysis: function-level binary vulnerability classification (0/1).
   - The planned design applies all 15 diagnostic arms to the same 2,732 Devign and 2,274 REVEAL test instances. A complete 15-arm test matrix would contain 5,006 test-instance-by-arm evaluations per arm set, or 75,090 in total. This is the planned full-matrix count, not a statement that all evaluations have been completed.
   - Across the validation and test partitions, the planned full matrix comprises 10,011 instances per arm set, or 150,165 instance-by-arm evaluations if all 15 arms are run on every instance. Actual completion status is reported separately in the run ledger.
   - Functions sharing a commit_id in Devign or a file_hash in REVEAL are treated as clusters in the registered statistical analyses.
```

### Starting and stopping rules

```text
1. Starting Rule and amendment history

The original registration specified that confirmatory test evaluation would begin only after the OSF registration was stamped and the corresponding Git commit was tagged prereg-v1. This records the original plan, but not the actual sequence of all study activities. Before this amendment, B0, B1, B2, and B2-flip already had validation and test inference outputs, and a post-hoc reanalysis had been completed and inspected. These activities and the prior exposure of the test sets are disclosed in the Foreknowledge section and the run ledger; they are not represented as wholly prospective or blind analyses.

B1-H2 validation and test inference were also conducted on Colab L4 as exploratory, platform-deviant runs. The Colab threshold lock is superseded. Complete Kaggle B1-H2 validation has since supplied Devign tau=0.09 and REVEAL tau=0.21 using validation records only. No test records, labels, or metrics were read to select these Kaggle thresholds. The corrected B0/B1 values and B1-H2 values are specified in the Analysis Plan and validation evidence.

The original 14-value threshold lock and SHA-256 digest are historical; the original lock omitted B1-H2 and is not the current threshold record. This amendment corrects four B0/B1 values and adds two B1-H2 values. Before any remaining run that depends on these thresholds, the current threshold file must match the amended threshold evidence. A mismatch must be resolved before the run proceeds.

Kaggle with two NVIDIA Tesla T4 GPUs remains the required platform for all arms. Colab/L4 is not authorized as an alternative platform by this amendment. Any further B1-H2 test inference must use Kaggle and the locked Kaggle validation thresholds, with the run's actual environment recorded.

The amended B3 selector algorithm is implemented, but no real pair has been approved, no amended real prompt set has been frozen, and no amended B3 inference or threshold fitting is complete. B3 remains paused until eligible vulnerable/patched pairs are verified and reviewed within the frozen clean training donor bank and the prompts are frozen.

2. Stopping Rule (Fixed-Sample Census Termination)

The planned design uses the complete specified validation and test partitions without downsampling. An arm/dataset run is complete only when its full specified partition has been evaluated and its outputs pass the registered integrity checks. The 75,090 test instance-by-arm evaluations and 150,165 validation/test instance-by-arm evaluations describe the planned complete 15-arm matrix; they are not a claim that all evaluations have been completed. Actual completion is reported by arm in the run ledger.

The fixed-sample design does not authorize sequential testing or adaptive early stopping. Prior exploratory runs, partial runs, test exposure, and the completed post-hoc reanalysis are disclosed separately and are not erased by this amendment. An incomplete run does not count as a completed arm/dataset evaluation.

3. Study Abort and Quality Control Decision Rules

- Supervised anchor validity: If the SUP-LR performance advantage disappears after deduplication or label auditing, halt the affected analysis and resolve the data-integrity issue before proceeding.
- Prompt delivery integrity: If the pre-execution audit finds that graph or demonstration components fail to reach the model, including empty demonstrations or a missing-graph rate above 5%, correct the prompt generator and rerun affected arms. For amended B3, additionally require the verified source-pair evidence, two reviewer judgments, and frozen prompt hashes specified in the amended B3 method before inference.
- Threshold integrity: Use the amended threshold table and its associated validation evidence, not the historical 14-value checksum. If the threshold artifact does not match the amended evidence, halt the affected run until the mismatch is resolved.
- B2-rep cache isolation: Preserve the registered repeat execution and separate cache tag so B2-rep cannot reuse cached B2 responses.
- Further deviations or expansions: This update explicitly discloses the B0/B1 threshold corrections, the addition of B1-H2 validation thresholds, the B3 method replacement, prior test exposure, and the Colab deviation. These changes are retrospective disclosures and are not claimed to have preceded the relevant data exposure or analyses. Any additional model, threshold, or prompt change after this update must be separately disclosed; exploratory extensions will be reported as post-hoc.
```

## Variables

### Manipulated variables

```text
The study manipulates five factorial dimensions across 15 diagnostic arms and supervised baselines in a paired within-subject design:

1. Graph Representation (CPG Structure):
   - None (B0): Raw source code without graph information.
   - Canonical Prefix (B1, B2): Textualized Code Property Graph capped at 40 nodes and 80 edges.
   - Shuffled Graph (B1-shuf): CPG extracted from an unrelated donor function with matched node count (+/-10%), preserving graph syntax while destroying semantic correspondence with target code.
   - Token-Budget Full Expansion (B1-full): CPG expanded to consume up to the full 1,500 token budget.
   - Guarded Execution Trace Packing (B1-H2): CPG repackaged to prioritize execution paths and guard conditions within the 1,500 token budget.

2. In-Context Demonstration Content & Semantics:
   - None (B0, B1): Zero-shot evaluation.
   - Mechanistically Retrieved (B2): Single demonstration retrieved via graph-code similarity from the sanitized donor bank with its ground-truth label.
   - Random Demonstration (B2-rand): Single demonstration sampled uniformly at random from the clean donor bank with its ground-truth label (evaluating semantic vs. random exemplar effect).
   - Unlabelled Demonstration (B2-nolabel): Retrieved demonstration provided with code only, omitting vulnerability labels.
   - Surface Label Priming (B2-labelonly): Prompt contains only the natural language label assertion ("A function similar to the one above was labelled Vulnerable/Non-vulnerable") without demonstration code.

3. Label Faithfulness & Output Robustness:
   - True Label (B2): Demonstrations carry true ground-truth labels.
   - Flipped Label (B2-flip): Demonstrations carry inverted labels (0 -> 1, 1 -> 0) to measure net surface label sensitivity.
   - Repeated Query (B2-rep): Identical prompt to B2 re-queried with dedicated cache isolation (tag="repeat") to measure run-to-run variance from GPU batching and non-determinism.

4. Contrastive Demonstration Design — Amended B3 Method:
   - Full Contrastive (B3): Two demonstrations comprising vulnerable and patched versions of the same source function across an identified security-fix commit, accompanied by a "Key difference" explanation supported by the verified source diff and security rationale.
   - Pair Eligibility: Both examples must belong to the corresponding frozen clean training donor bank. Targets and validation/test functions are excluded; no external donor dataset is introduced. Two reviewers must verify each pair and resolve disagreements before admission.
   - Deterministic Pair Selection: Rank eligible pairs by the mean token-set Jaccard similarity between the target and each of the two functions, using the existing token normalization. Select the highest-scoring pair; exact ties are resolved by lexicographic stable pair ID. Target labels and validation/test performance are not used for donor selection.
   - Contrastive without Explanation (B3-nodiff): Use exactly the same selected pair as amended B3, omitting only the Key difference block.
   - Swapped Presentation Order (B3-swap): Use the same pair and explanation, changing only demonstration order.
   - Flipped Contrastive (B3-flip): Use the same pair and explanation, changing only both demonstration labels under the registered probe convention.
   - Preserve the registered prompt section order, tokenizer, token budget, graph input, output schema, and scoring. Freeze and hash amended prompts before inference.
   - The amended algorithm is implemented, but no real pair has been approved, no amended real prompt set has been frozen, and no amended B3 inference or threshold fitting is established by this update. B3 remains paused until the required pair verification is completed.

5. Baseline Model Representations & Ensembling:
   - Supervised Anchors (SUP-LR, SUP-MLP, SUP-METRIC): Logistic Regression and MLP on frozen CodeT5 768d embeddings and 26 static code metrics.
   - Meta-Models (P-PRE vs. P-POST): Pre-model (34 foundation features) vs. Post-model (34 foundation features + 4 LLM interaction features).
   - Routing Policies: Random, Confidence-based, Benefit-router (Ridge), and Oracle ceilings at 5%, 10%, and 25% computational budgets.
```

### Measured variables

```text
1. Primary Model Outcome Measures (Per Sample):
   - Continuous Vulnerability Score (s): Estimated probability of vulnerability derived directly from model output logits: s = p(1) / (p(0) + p(1)) = sigmoid(logit_1 - logit_0), bounded in [0.0, 1.0].
   - Score Validity Flag (valid): Boolean flag indicating whether valid, finite logits for both tokens '0' and '1' could be computed. When logits fail, valid=False, and s is not artificially forced to 0.
   - Raw Vocabulary Token (raw): Greedy decoded token at position 1 across the full vocabulary.
   - Response Validity Flag (response_valid): Boolean flag strictly indicating whether raw in {'0', '1'}.
   - Default Binary Prediction: y_hat_0.5 = 1[s >= 0.5].
   - Validation-Thresholded Prediction: y_hat_tau = 1[s >= tau*], using the applicable validation-selected threshold in the amended threshold record. The original lock omitted B1-H2 and contained four B0/B1 values corrected by this amendment. The corrected B0/B1 values and the added Kaggle B1-H2 values are specified under Indices and in the Analysis Plan.

2. Benchmark Predictors and Structural Covariates:
   - Ground Truth Label (y): Binary vulnerability ground truth (1 = vulnerable, 0 = non-vulnerable).
   - Dataset Identifier: Devign (N=5,464) or REVEAL (N=4,547).
   - Split Partition: Validation data are used for threshold selection; test data are used for evaluation. Prior test exposure, completed inference, and post-hoc reanalysis are disclosed in the Foreknowledge section. This amendment does not represent all test analyses as wholly prospective or blind.
   - Cluster Grouping Variables: commit_id (Devign: 2,068 test clusters) and file_hash (REVEAL: 646 test clusters), used for clustered standard errors.
   - Token Budgets: Target code tokens, demonstration tokens, graph tokens, and total prompt tokens measured by the Qwen3-Coder BPE tokenizer.

3. Variables for Subsetting, Exclusions, and Sensitivity Audits:
   - Near-Duplicate Flag (near_duplicate_jaccard_3gram): Samples sharing token 3-gram Jaccard similarity >= 0.9 with retrieval donors (used to report results both on full test and deduplicated test partitions).
   - Missing Graph Flag (graph_missing): Flagged when Joern CPG generation fails (such samples are retained in inference and reported as coverage).
   - Demonstration Truncation Flag: Flagged when a demonstration is truncated below 25% of its original token length.

4. Human Blind Review Variables (Step 8 Audit):
   - Retrieval Relevance Rubric: Independent blind ratings on four criteria: vulnerability sink, vulnerable variable, guard condition, and evidence line correspondence.
   - Error Inspection Packets: Stratified categorization of 60 inspection cases into False Negative repaired/created and False Positive repaired/created.
   - Label Integrity Audit: Qualitative verdicts (label_ok, label_suspicious, not_enough_context) across 100 audit samples per dataset.
```

### Indices

```text
Measured variables are combined into performance indices and statistical contrasts using the following pre-specified mathematical formulations:

1. Continuous Scoring Formula:
   s = p(1) / (p(0) + p(1)) = 1 / (1 + exp(-(logit_1 - logit_0)))
   If only top-k logprobs are available and one token is absent, its probability is upper-bounded by the minimum top-k logprob and flagged as s_bounded. If both tokens are absent, the instance is flagged invalid.

2. Threshold-Free Discriminative Indices:
   - AUROC: Area Under the Receiver Operating Characteristic curve computed non-parametrically across all valid continuous scores s against ground-truth labels y.
   - AUPRC: Area Under the Precision-Recall curve.

3. Thresholded Classification Indices:
   Calculated at default tau = 0.5 and locked validation-optimal threshold tau*:
   - Matthews Correlation Coefficient (MCC):
     MCC = (TP * TN - FP * FN) / sqrt((TP + FP)(TP + FN)(TN + FP)(TN + FN))
     (Undefined cases where denominator = 0 are tracked and reported).
   - Balanced Accuracy (BA): BA = 0.5 * (TP / (TP + FN) + TN / (TN + FP)).
   - F1-Score: F1 = 2 * TP / (2 * TP + FP + FN).
   - Positive Prediction Rate: PPR = (TP + FP) / N.
   - Invalid Rate: IR = sum(1[valid == False]) / N.

4. Validation Threshold Decision Rule and Amended Threshold Record:

   tau*(dataset, arm, seed) = argmax MCC(y_val, 1[s_val >= tau])
   over tau = 0.01, 0.02, ..., 0.99, using the complete applicable official validation split.

   - Exclude grid points with undefined MCC.
   - Tie-break: Select the threshold closest to 0.5; if a tie remains, select the smaller threshold.
   - This amendment corrects four submitted B0/B1 values:
       Devign B0: 0.08 -> 0.98
       REVEAL B0: 0.44 -> 0.30
       Devign B1: 0.88 -> 0.98
       REVEAL B1: 0.74 -> 0.63
   - B1-H2 was already included in the experimental matrix but absent from the original threshold lock. Complete Kaggle validation adds:
       Devign B1-H2: tau*=0.09, MCC=0.0667928192, n=2,732.
       REVEAL B1-H2: tau*=0.21, MCC=0.0836323479, n=2,273.
   - No test records, labels, or metrics were read for the Kaggle B1-H2 threshold selection. The prior Colab-derived B1-H2 thresholds of 0.09/0.67 are superseded; the Kaggle values were independently selected from Kaggle validation outputs.
   - Inheritance: B2-rep and B2-flip inherit the corresponding B2 threshold. Amended B3-swap and B3-flip inherit the amended B3 threshold without re-tuning. B3-nodiff retains its independently selected validation threshold.
   - The amended B3 threshold must be selected from complete validation and locked before the corresponding new test inference. No amended B3 threshold fitting is claimed as complete.

5. Diagnostic Treatment Effect Indices (Pairwise Contrasts):
   - Contrast Delta: Delta_Metric = Metric(Arm_B) - Metric(Arm_A).
   - Net Label Sensitivity Index:
     Net_Sens = |Acc(B2) - Acc(B2-flip)| - |Acc(B2) - Acc(B2-rep)|
     (Isolates true surface label priming from non-deterministic GPU batching noise).
   - Label Priming Recovery Ratio:
     Recovery_Ratio = Delta_Metric(B2-labelonly - B1) / Delta_Metric(B2 - B1).

6. Complementarity & Routing Indices:
   - LLM Interaction Features in P_POST: Derived features include s * p and (s - p), where p is the foundation ensemble baseline probability.
   - Incremental Complementarity: Delta_MCC = MCC(P_POST) - MCC(P_PRE) evaluated via 3-fold Out-Of-Fold (OOF) StratifiedGroupKFold cross-validation.
   - Routing Benefit at q = 10% budget: Delta_BA(Benefit Router - Confidence Router).
   - Inter-Rater Reliability: Cohen's kappa (kappa) for qualitative blind reviews.
```

## Analysis Plan

### Statistical models

```text
The study employs a non-parametric, paired cluster bootstrap statistical framework alongside supervised ensembling and meta-modeling:

1. Primary Estimators & Pairwise Treatment Contrasts (Table B):
   - Paired Cluster Bootstrap: B = 5,000 resamples with fixed random seed 20261117.
   - Clustering Units: Clustered at commit_id for Devign (2,068 independent test clusters) and file_hash for REVEAL (646 independent test clusters), preserving intra-cluster syntactic dependence.
   - Treatment Effect Estimator: Delta_Metric = Metric(Arm_B) - Metric(Arm_A), evaluated for AUROC, MCC, Balanced Accuracy, and F1.
   - 11 Pre-registered Confirmatory Contrasts:
     * H1.1 & H1.2 (GRACE vs. Zero-Shot): B2 vs. B0 on Devign Test and REVEAL Test.
     * H2.1 (Surface Label Sensitivity): B2 vs. B2-flip, baseline-corrected by natural batch variance |B2 - B2-rep|.
     * H2.2a, b, c (Demonstration Content Invariance): B2 vs. B2-rand, B1 vs. B2-nolabel, and B2-labelonly vs. B2.
     * H2.3 (Contrastive Operating Point): B2 vs. B3.
     * H3.1a, b, c (Graph Representation Invariance): B0 vs. B1, B1-shuf vs. B1, and B1 vs. B1-H2.
     * H5.1 (Supervised Baseline Superiority): SUP-LR vs. B2.
     * H5.3 (Routing Efficacy & LLM Orthogonality): Benefit Router vs. Confidence Router at q=10% budget; P-PRE vs. P-POST meta-models.

2. Supervised Anchors & Meta-Models:
   - Supervised Baselines: Logistic Regression (SUP-LR) and MLP (SUP-MLP) on frozen CodeT5 768-dimensional embeddings and 26 static code metrics (SUP-METRIC), evaluated across 3 pre-registered seeds (42, 43, 44; headline seed 42).
   - Meta-Models (P-PRE vs. P-POST): 3-fold Out-Of-Fold (OOF) cross-validation using StratifiedGroupKFold (grouped by commit/file hash). Pre-model incorporates 34 foundation features (5 view logits, ensemble p, |p - 0.5|, MLP-lexical gap, 26 metrics); Post-model appends 4 LLM expert interaction features [s, valid, s*p, s-p].
   - Routing Policies: Evaluated across fixed budgets (q in {0.05, 0.10, 0.25}) comparing Confidence Router (|logit p - logit tau|), Benefit Router (Ridge regression alpha=10), Random Router (20 seeds), and Oracle Ceiling.

3. Positive/Negative Controls & Model Checks:
   - Positive Control: SUP-LR serving as high-performance supervised benchmark.
   - Negative Controls: ALL-0, ALL-1, and RAND (random sampling matching label prior across 20 seeds).
   - Manipulation Checks: B2-rep verifies run-to-run GPU reproducibility; B1-shuf verifies graph syntax invariance; B2-flip verifies directional label sensitivity.

Amendment and analysis status: The registered statistical framework, contrasts, and multiple-testing rules remain as specified. The 6 November 2026 post-hoc reanalysis recalculated validation thresholds, test metrics, sensitivity results, and selected paired-bootstrap contrasts. Those results were inspected before this update and are disclosed retrospectively. This reanalysis does not constitute completion of the confirmatory Holm analysis of all 11 registered contrasts.

The B3 hypotheses and outcome definitions remain unchanged, but subsequent B3-family analyses will use the amended pair-construction and difference-generation method described in the Study Design. Outputs from the original and amended B3 methods will retain separate version identities and will not be pooled. The amended selector is implemented; no verified real pair set, frozen real prompt set, amended B3 inference, or amended B3 threshold fitting is established by this update.
```

### Transformations

```text
1. Dependent Variable Coding:
   Ground-truth vulnerability labels are binary: 0 = non-vulnerable, 1 = vulnerable.

2. Model Output Probability Transformation:
   Continuous vulnerability score s is computed directly from model output logits:
   s = p(1) / (p(0) + p(1)) = 1 / (1 + exp(-(logit_1 - logit_0)))
   This maps unbounded logit differences into a strictly bounded probability scale in [0.0, 1.0].

3. Threshold Discretization and Amended Threshold Record:

Thresholded metrics (MCC, F1, Balanced Accuracy) are evaluated at:
- The default boundary tau=0.5.
- The applicable validation-selected boundary tau*.

Threshold selection uses the complete official validation split: Devign n=2,732 and REVEAL n=2,273. Search tau=0.01, 0.02, ..., 0.99 to maximize validation MCC. Exclude grid points with undefined MCC. Ties select the threshold closest to 0.5, then the smaller threshold.

Four B0/B1 values in the submitted threshold table are corrected:
- Devign B0: 0.08 -> 0.98; validation MCC=0.076010.
- REVEAL B0: 0.44 -> 0.30; validation MCC=0.080120.
- Devign B1: 0.88 -> 0.98; validation MCC=0.074755.
- REVEAL B1: 0.74 -> 0.63; validation MCC=0.083264.

B1-H2 was already registered as an arm but absent from the original threshold lock. Complete Kaggle validation supplies:
- Devign B1-H2: tau*=0.09; validation MCC=0.0667928192; n=2,732.
- REVEAL B1-H2: tau*=0.21; validation MCC=0.0836323479; n=2,273.

No test records, labels, or metrics were read for this Kaggle B1-H2 threshold selection. These values were independently computed from Kaggle outputs. The previous Colab-derived B1-H2 lock of 0.09/0.67 is superseded.

Prior test exposure and completed reanalysis are disclosed retrospectively; the statement that every threshold was locked before all historical test inference is corrected. Applicable validation thresholds must be locked before the corresponding remaining test inference.

B2-rep and B2-flip inherit B2 thresholds. Amended B3-swap and B3-flip inherit amended B3 thresholds; B3-nodiff retains its independent validation-threshold policy. No amended B3 threshold fitting is claimed as complete.

4. Meta-Model Feature Standardization:
   Continuous predictor features (26 static code metrics, token counts, and interaction terms) are scaled using StandardScaler (zero mean, unit variance) fit strictly within training folds to prevent data leakage. Derived interaction features include s*p and (s - p), where p is the base ensemble probability.
```

### Data inclusion and exclusion

```text
1. Inclusion:
   Evaluation conducts a complete census of the official Devign (N=5,464) and REVEAL (N=4,547) validation and test partitions without downsampling. All instances with complete target code are included.

2. Pre-execution Donor Sanitization (Exclusion from Retrieval Banks):
   - Exact Duplication Purge: Any donor function in the training retrieval bank that exactly matched a validation or test sample (after normalizing whitespace, newlines, and comments) was purged to guarantee zero retrieval leakage (108 Devign functions, 52 REVEAL functions excluded from donor bank).
   - Conflicting Label Groups: Code clusters in the donor bank exhibiting conflicting vulnerability labels were purged.

3. Sensitivity Subsetting (Near-Duplicate Auditing):
   Instances sharing token 3-gram Jaccard similarity >= 0.9 with retrieval donors are flagged. In accordance with the protocol, these are not discarded from raw test sets; instead, all confirmatory metrics are reported on both:
   (a) Full official test partition (complete census).
   (b) Clean deduplicated test partition (near-duplicates removed).

4. Missing Graph Handling:
   Samples where Joern CPG generation fails (flagged as graph_missing) are NOT excluded from LLM inference. All arms evaluate these samples, and the failure rate is explicitly tracked and reported as representation coverage.

5. Outliers and Length Budget Enforcement:
   No samples are excluded as token length outliers. All prompts are capped strictly within the n_ctx = 8,192 token context window (target code <= 3,000, demos <= 1,500, graph <= 1,500) using deterministic truncation policies. Demonstrations truncated below 25% of original length are flagged.

6. Amended B3 Donor-Pair Eligibility:

Both members of a B3 pair must remain eligible examples in the corresponding frozen clean training donor bank. Each pair must represent vulnerable and patched versions of the same source function across an identified security-fix commit. Record the repository, path, function identity, fixing commit and parent revision, donor IDs, code hashes, labels, and supporting source-diff/security evidence.

Two reviewers must assess each pair and resolve disagreements before admission. A shared commit alone is insufficient evidence of a valid pair. Targets and validation/test functions are excluded from the donor pool. No external donor dataset is authorized. If an adequate verified pair pool cannot be established within the frozen donor bank, B3 remains paused; any donor-bank expansion requires a separately disclosed decision before inference.
```

### Other planned analysis

```text
1. Qualitative Double-Blind Human Adjudication (Step 8):
   - Retrieval Relevance: 100 stratified targets per dataset evaluated blindly by 2 independent raters across 4 rubric dimensions (vulnerability sink, variable, guard, evidence line correspondence). Disagreements are adjudicated by a third rater to report Cohen's kappa.
   - Error Packet Inspection: 60 stratified cases across 4 error cells (15 False Negatives repaired, 15 False Negatives created, 15 False Positives repaired, 15 False Positives created by LLM routing) to establish whether repairs reflect genuine program semantic reasoning or surface bias shifts.
   - Ground-Truth Label Audit: 100 cases per dataset (50 False Positives + 50 False Negatives of the SUP-LR baseline) audited to quantify benchmark label noise.

2. Computational Overhead & Efficiency Accounting:
   Empirical measurement of inference resource profiles across arms:
   - Average prompt token length and breakdown.
  - GPU execution wall-clock time (seconds per 1,000 queries) on the registered Kaggle environment with two NVIDIA Tesla T4 GPUs. Record the actual runtime, GPU/VRAM, OS, Python, CUDA, driver, package versions, backend build settings, model-load/offload evidence, and GPU utilization for each run.
  - Earlier B1-H2 Colab L4 validation and test runs are disclosed as platform-deviant exploratory work. Their threshold lock is superseded and their test outputs are excluded from the confirmatory Kaggle analysis. This amendment does not authorize Colab/L4 or A100 as an alternative execution platform.
   - Impact of cold vs. warm KV-cache reuse on repeated queries (B2-rep).
```

## Other

### Context and additional information

```text
1. Original Registration and Amendment Repository Snapshots

The original registration recorded repository commit:
7a1e16168591c37f005599cb4d5dc3ce33f7d950
https://github.com/kazunguyen/GRACE-summary/tree/7a1e16168591c37f005599cb4d5dc3ce33f7d950

The repository snapshot prepared for this amendment is identified by:
Tag: prereg-v1.1
Commit: f4553d97247a79d84b47865c59ac221d1b4f8f6c
https://github.com/kazunguyen/GRACE-summary/tree/f4553d97247a79d84b47865c59ac221d1b4f8f6c

The commit URL identifies the specific amendment snapshot. The tag is a repository version label and does not establish OSF submission or approval. The amendment's effective submission and approval dates are those actually recorded by OSF.

2. Historical Submission Checksums

The following checksums describe the original submission artifacts and are retained as historical identifiers:

- GRACE_OSF_PREREGISTRATION_20261102.pdf:
  SHA-256: 22648ead896baf5c1032de700c12fb97bd6dc44f0a8049292532ae6c0468b14c

- GRACE_OSF_PREREGISTRATION_20261102.zip:
  SHA-256: 6d6e8fe46f1dc59bf5f399defca59ba8ab0c362a0b13d0cb101c16320a2a082e

- attachment_sha256.json:
  SHA-256: 41888a239e902dc1911f7e19b5c033726ea537689fcbc82caf6aaee275dde049

- Original configs/protocol.yaml:
  SHA-256: acbea3283f5c9e2b14644a47ef0e8524d7775ad67c9fe16f6b0f4d3cb99320b3

- Original 14-value threshold lock:
  Recorded locked-payload digest: a0108431ad859aacc3dab29ca7e88a7eb404428b4d60fc251e3bbae7d350c831

The original threshold digest does not identify the amended threshold record. The original PDF/ZIP attachments remain preserved; the specific methods and threshold entries identified in this update supersede the corresponding statements in those historical attachments.

3. Amended Threshold Record

Four submitted B0/B1 thresholds are corrected using complete validation:
- Devign B0: 0.08 -> 0.98.
- REVEAL B0: 0.44 -> 0.30.
- Devign B1: 0.88 -> 0.98.
- REVEAL B1: 0.74 -> 0.63.

B1-H2 was already included in the registered matrix but absent from the original threshold lock. Complete Kaggle validation adds:
- Devign B1-H2: tau=0.09; MCC=0.0667928192; n=2,732.
- REVEAL B1-H2: tau=0.21; MCC=0.0836323479; n=2,273.

The B1-H2 Kaggle thresholds were independently selected from Kaggle validation records. No test records, labels, or metrics were read for that selection. The earlier Colab-derived values of 0.09/0.67 are superseded.

The Kaggle B1-H2 lock artifact has locked-payload SHA-256:
b5dc7e0da070f75cfabc10c366a08675d1c3f471f1e11fb86ee826a22ce674f8
This identifies that lock payload, not the byte-level checksum of configs/thresholds.json.

Existing B0/B1 test scores are retained. Analyses under the submitted and corrected thresholds will be identified explicitly; corrected-threshold analyses of previously inspected test outputs are retrospective/post-hoc.

4. Model, Platform, and Runtime

Primary model: Qwen/Qwen3-Coder-30B-A3B-Instruct, GGUF Q4_K_M.
Model weight SHA-256:
f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335

Tokenizer revision:
b2cff646eb4bb1d68355c01b18ae02e7cf42d120

The execution configuration documented for this amendment uses llama-cpp-python==0.3.16 through direct Llama invocation, with n_ctx=8192, n_batch=256, n_gpu_layers=-1, logits_all=True, greedy decoding, temperature 0, and the registered seeds.

Kaggle with two NVIDIA Tesla T4 GPUs remains the required platform for all arms. Record the actual runtime, GPU/VRAM, OS, Python, CUDA, driver, package versions, backend build flags, model/tokenizer/prompt hashes, code commit, model-load/offload evidence, and GPU utilization for each run.

Earlier B1-H2 Colab L4 validation and test inference are disclosed as platform-deviant exploratory work. This amendment does not authorize Colab/L4 as an alternative platform. Those Colab test outputs are excluded from the confirmatory Kaggle analysis.

5. Audit and B3 Implementation Status

Audits establish only the checks documented for their specific artifacts. The earlier blanket statement that all prompts across all 15 arms had already passed a complete audit is corrected.

The B1-H2 Kaggle audit covers all 5,005 validation records, including unique IDs, frozen-label joins, prompt hashes, score validity, threshold-grid reproduction, and runtime provenance.

The amended B3 selector algorithm is implemented. Software tests and synthetic prompt rendering do not establish source authenticity, human approval of real pairs, or completed model inference. At preparation of the amendment draft, no real pair had been approved, no amended real prompt set had been frozen, and no amended B3 inference or threshold fitting had occurred. B3 remains paused until the required verified pair pool is available within the frozen clean training donor bank.

6. Retrospective Transparency

Before this amendment, B0/B1/B2/B2-flip inference outputs and metrics existed, and the 6 November 2026 reanalysis of validation thresholds, test metrics, sensitivity results, and selected paired-bootstrap contrasts had been inspected. These activities are disclosed retrospectively. This update does not establish that they preceded test exposure or represent a completed Holm analysis of all 11 registered contrasts.

The amendment corrects threshold entries, supplements B1-H2 threshold provenance, replaces the B3 method, and discloses platform deviations and completed work. The original registration and historical outputs remain preserved.

7. Immutable Evidence References

The full amendment methods, disclosures, and evidence index E1-E30 are archived at the fixed amendment commit:
https://github.com/kazunguyen/GRACE-summary/blob/f4553d97247a79d84b47865c59ac221d1b4f8f6c/Runs-management/osf_amendment_20261106/OSF_UPDATE_EN.md

B0/B1 validation-only reproduction instructions and evidence:
https://github.com/kazunguyen/GRACE-summary/blob/d9127fc7b12a128d8499012454ad134733f810ff/Runs-management/osf_amendment_20261106/README.md

Kaggle B1-H2 threshold lock:
https://github.com/kazunguyen/GRACE-summary/blob/4838a55135e2d9a5b19292815e3c4b5a12467ed9/Runs-management/b1h2_kaggle_validation_threshold_lock_20261106.json

Kaggle B1-H2 independent validation audit:
https://github.com/kazunguyen/GRACE-summary/blob/4838a55135e2d9a5b19292815e3c4b5a12467ed9/Runs-management/b1h2_kaggle_validation_audit_20261106.json

Retrospective reanalysis report:
https://github.com/kazunguyen/GRACE-summary/blob/90c5b3ff5f5e86927ab2a8b451c99c458fcddcaf/Runs-management/reanalysis_20261106/REPORT.md

Amended B3 implementation:
https://github.com/kazunguyen/GRACE-summary/blob/f445a30c8315aeb6c49337acde6cf9df0ac0d6f8/01_Author_Baseline_Unified/diagnostic_kit/src/grace_diag/amended_b3.py

B3 feasibility and implementation status:
https://github.com/kazunguyen/GRACE-summary/blob/f445a30c8315aeb6c49337acde6cf9df0ac0d6f8/Runs-management/b3_amended_20261106/README.md
```

## Các chỉnh sửa được đề xuất sau khi rà bản Review

Các đoạn dưới đây được soạn sau khi bản Review trên được sao chép. Chưa đối chiếu được chúng với nguyên văn trên revision đã nộp.

### Sampling → Data collection procedures

Thay dòng Pre-execution Audit bắt đầu bằng “All 10,011 prompts across 15 arms” bằng:

```text
- Pre-execution Audit: Audit completion is established separately for each versioned prompt set and run. The B1-H2 Kaggle audit covers all 5,005 validation records. The amended B3 selector has passed software and synthetic-prompt checks, but no real pair has been approved and no amended real prompt set has been frozen. A completed audit of all amended prompts across all 15 arms is not claimed. Required input audits must be completed before the corresponding inference.
```

Dưới Execution Environment, thay đoạn bắt đầu bằng “Inference is served via llama-server” và kết thúc bằng “zero-test-exposure protocol” bằng ba đoạn sau. Đoạn B3 amendment nằm ngay sau phần này.

```text
- Inference uses llama-cpp-python==0.3.16 through direct Llama invocation with Qwen3-Coder-30B-A3B-Instruct GGUF Q4_K_M (model SHA-256: f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335), n_ctx=8192, n_batch=256, n_gpu_layers=-1, logits_all=True, greedy decoding, temperature 0, and the registered seeds.

- Kaggle with two NVIDIA Tesla T4 GPUs remains the required execution platform. Actual runtime, package, GPU, and model-load/offload provenance must be recorded for each run. Earlier B1-H2 Colab L4 validation and test runs are disclosed as platform-deviant exploratory work; this amendment does not authorize Colab as an alternative platform.

- Prior test exposure and completed analyses are disclosed in the Foreknowledge section. The four B0/B1 threshold corrections and two added B1-H2 thresholds are documented with validation-only evidence. This amendment does not claim a zero-test-exposure history or that every historical threshold was locked before all test inference.
```

### Sampling → Sample size

Đổi “per arm set” thành “per arm” ở hai câu về 5,006 mẫu test và 10,011 mẫu validation/test mỗi arm. Tổng dự kiến lần lượt là 75,090 và 150,165 lượt đánh giá.

## Sửa liên kết bằng chứng trên GitHub sau khi nộp

Commit [f15368a](https://github.com/kazunguyen/GRACE-summary/commit/f15368a) thay hai URL 404 của E1/E2 trong tài liệu bằng các bản công khai có cùng nội dung. Đây là bản đính chính liên kết trong repo sau khi nộp.

- [E1 — mã optimizer](https://github.com/kazunguyen/GRACE-summary/blob/d9127fc7b12a128d8499012454ad134733f810ff/Runs-management/validation_lock.py)
- [E2 — artifact ngưỡng B0 lịch sử](https://github.com/kazunguyen/GRACE-summary/blob/d9127fc7b12a128d8499012454ad134733f810ff/Runs-management/analysis_lock_20261101/thresholds.initial.json)
