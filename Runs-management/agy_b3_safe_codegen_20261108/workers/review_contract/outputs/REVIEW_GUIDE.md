# B3 Paired-Donor Admission and Verification Guide

## 1. Scope and Objective
This document defines the mandatory, auditable verification workflow for admitting paired vulnerable/patched demonstration exemplars into Arm B3 (paired diff demonstration with security rationale). The current scope is strictly limited to Arm B3. Under no circumstances may candidate pairs be admitted into confirmatory evaluation without completing every mechanical gate and independent dual human sign-off specified herein.

### Core Invariants
- **Clean Donor Origin**: Candidates must originate strictly from the frozen, same-dataset clean TRAIN split bank. No candidate may be drawn from validation splits, test splits, or external data pools. Never silently expand frozen donor banks.
- **Label Authenticity**: The vulnerable exemplar must possess ground-truth label `1` and the patched counter-exemplar must possess ground-truth label `0`.
- **True Source Identity**: Function similarity, lexical overlap, vector distance, or AST tree-distance metrics do not constitute verified source identity. Identity requires deterministic repository authentication.
- **Source Anchoring**: Both variants must map to the same source repository, file path, and function symbol, separated by full 40-hex git commit revisions (a parent vulnerable revision and a child fix commit revision).
- **Physical Evidence Integrity**: Canonical payload SHA-256 hashes, exact byte-level function slices before and after patch application, and full diff artifacts must be permanently archived.
- **Independent Dual Human Review**: Two distinct, qualified human reviewers must independently evaluate the canonical artifact payload and sign off. An automated model check, LLM output, or heuristic script is never a human review. Approvals must never be fabricated, simulated, or pre-populated.

---

## 2. End-to-End Admission Lifecycle

The admission pipeline follows eight strictly sequential, non-bypassable stages:

```
Candidate Discovery
       │
       ▼
Source Authentication
       │
       ▼
Independent Human Reviews (2 distinct reviewers)
       │
       ▼
Machine Admission Gate
       │
       ▼
Label-Blind Selection
       │
       ▼
Prompt Audit & Prompt Freeze
       │
       ▼
Full Validation & Threshold Recalibration (tau*)
       │
       ▼
Confirmatory Test Evaluation
```

### Stage 1: Candidate Discovery
- Query the frozen clean TRAIN bank for records that share project, repository, or identifier tags indicating prospective vulnerability-patch pairs.
- Verify preliminary status: prospective vulnerable candidate (`label = 1`) and prospective fixed candidate (`label = 0`).
- High embedding or lexical similarity is merely an indicator for discovery filtering, never an admission criterion.

### Stage 2: Source Authentication
- Authenticate the pair against the actual upstream Git repository.
- Confirm exact file path and function signature match across revisions.
- Verify the fix revision is a full 40-hex Git commit hash, and the parent revision is a full 40-hex Git commit hash matching the vulnerable state.
- Extract and archive:
  1. Exact before-patch function bytes (`vuln_bytes`) and SHA-256 checksum.
  2. Exact after-patch function bytes (`fixed_bytes`) and SHA-256 checksum.
  3. Upstream unified diff between parent and fix revisions.
- Confirm that the unified diff directly produces the observed changed lines in the function body.
- Retrieve the sourced security rationale (e.g., CVE advisory, commit log, security bulletin, or developer issue discussion). Generating or guessing security rationale via keyword heuristics or ungrounded model completions is strictly prohibited.
- Assemble the Canonical Verification Payload and calculate its `canonical_payload_sha256`.

### Stage 3: Independent Human Reviews
- Two distinct human reviewers with domain expertise in secure code auditing inspect the unredacted canonical verification payload independently.
- Each reviewer evaluates four atomic criteria:
  1. `same_function_verified`: Confirmed that before/after snippets belong to the identical logical function entity.
  2. `security_fix_verified`: Confirmed that the delta directly remediates a security vulnerability rather than performing non-security refactoring, cosmetics, or unrelated feature work.
  3. `source_revisions_verified`: Confirmed the upstream repository, 40-hex parent revision, and 40-hex fix revision are authentic and reproducible.
  4. `explanation_supported`: Confirmed that the rationale is grounded in upstream evidence and factually explains the security vulnerability and its fix.
- Both reviewers record their real reviewer identifier, ISO-8601 UTC timestamp, cryptographic signature or attestation bound to the `canonical_payload_sha256`, and explicit boolean judgments.

### Stage 4: Machine Admission
- Automated validator re-computes `canonical_payload_sha256` and verifies both human approval records are bound to that exact hash.
- Validates reviewer diversity (`reviewer_1_id != reviewer_2_id`).
- Verifies all four boolean assertions are `True` for both reviews.
- Validates byte hashes against archived files.
- Admits the record to the Admitted B3 Exemplar Bank with an immutable manifest record.

### Stage 5: Label-Blind Selection
- When selecting the demonstration pair for B3 evaluation prompts, selection must remain completely blind to test-split labels and test-split performance.
- Selection follows pre-registered deterministic ranking (e.g., lexical match with query code, or fixed pre-registered donor index) strictly within the admitted pool.

### Stage 6: Prompt Audit & Prompt Freeze
- Construct the formatted prompt according to the pre-registered B3 contract (role domain -> target code -> question -> graph node/edge -> demonstration -> answer).
- Audit prompt token length against the 8,192 token limit (demonstration budget <= 1,500 tokens).
- Verify target code labels never appear in the prompt.
- Freeze the prompt templates and exemplar manifests; commit cryptographic hashes to the experiment tracking record.

### Stage 7: Full Validation & Threshold Recalibration
- If admitting a new B3 demonstration exemplar alters the prompt representation for validation splits, execute inference across the complete validation census.
- Recompute optimal decision threshold tau* on the full validation split using the pre-registered objective.
- Freeze `configs/thresholds.json` and sign with self-checksum prior to touching any test evaluation split.

### Stage 8: Confirmatory Test Evaluation
- Run frozen Arm B3 against the immutable test census (Devign Test N=2,732; REVEAL Test N=2,274).
- Apply inherited or frozen thresholds without exploratory post-hoc tuning.
- Execute paired cluster bootstrap analysis (B=5,000) and Holm-Bonferroni correction.

---

## 3. Disclosed Protocol Decisions & Edge Cases

### Handling Source Formatting Mismatches
- When upstream repository code formatting (indentation, line breaks, macro formatting) conflicts with dataset bank tokenization:
  - Normalization must be purely mechanical, reversible, and fully scripted.
  - The exact transformation script and pre/post transformation SHA-256 hashes must be archived.
  - Formatting changes that alter AST nodes or semantic tokens are fatal errors; the candidate must be rejected.
  - All normalization decisions must be formally documented as a disclosed protocol decision in `CHANGES_AFTER_PREREG.md`.

### Zero Eligible Pairs Scenario
- If no candidates from the frozen clean TRAIN bank satisfy both machine checks and dual human review:
  - **DO NOT** expand the search into validation/test splits or external datasets.
  - **DO NOT** synthesize artificial pairs or use generative model reconstructions.
  - The failure must be logged, and Arm B3 must be reported as unadmitted due to lack of eligible verified pairs under the frozen protocol, or evaluated strictly under the pre-registered fallback arm.

---

## 4. Prohibited Practices
- Synthesizing human review signatures, IDs, or timestamps.
- Approving pairs using LLMs or algorithmic proxies in place of human sign-off.
- Editing diffs to fit prompt budgets without recording original source diff hashes.
- Inventing or extrapolating security explanations not supported by commit history or advisories.
- Re-tuning evaluation thresholds directly on test predictions.
