# B3 Diagnostic Arm Review & Admission Guide

## 1. Scope & Applicability
- **Target Arm**: This guide applies exclusively to the **B3** diagnostic arm (Contrastive Counterfactual Demonstration).
- **Donor Source**: All admitted pairs must originate from the **same frozen clean TRAIN bank** corresponding to the evaluated dataset (Devign or REVEAL).
- **Protocol Boundary**: Candidate token similarity does not constitute verified source identity. Local data declarations and hash consistency checks do not prove source authenticity. Real source authentication and security meaning require independent human review. No human reviews may be fabricated.

---

## 2. Donor Pair Specification & Admission Checklist

Each candidate B3 donor pair must contain the exact fields listed below:

1. **Provenance & Identifiers**:
   - `pair_id`: Unique deterministic identifier string.
   - `repository`: Repository name or canonical URL.
   - `path`: Relative file path within the repository.
   - `source_url`: Verifiable URL linking directly to the commit or source file.
   - `fix_commit`: Distinct full 40-character hexadecimal SHA of the fix commit.
   - `parent_commit`: Distinct full 40-character hexadecimal SHA of the parent commit (`fix_commit != parent_commit`).

2. **Source Code & Labels**:
   - `source.before`: Archived exact source code of the function prior to the fix (label = `1`, vulnerable).
   - `source.after`: Archived exact source code of the function after the fix (label = `0`, non-vulnerable/fixed).
   - `before_sha256`: SHA256 hex digest computed over the UTF-8 bytes of `source.before`.
   - `after_sha256`: SHA256 hex digest computed over the UTF-8 bytes of `source.after`.
   - `source.fix_diff`: Actual unified diff between `source.before` and `source.after` demonstrating and supporting the changed lines.

3. **Causal Explanation & Security Rationale**:
   - `security_rationale`: Objective rationale confirming the change addresses a genuine security vulnerability.
   - `key_difference`: Generated factual description detailing the contrastive security fix between before and after.

4. **Byte Identity & Formatting Invariance**:
   - `source.before` must match the corresponding donor entry in the frozen clean TRAIN bank byte-for-byte.
   - **Formatting Mismatch Rule**: Any byte or whitespace mismatch must be flagged as an **unresolved formatting mismatch**. Reviewers and automated scripts must **never normalize bank bytes** or claim that an unvetted formatting transformation is approved.

---

## 3. Human Review Protocol

Admitting a donor pair into the B3 pool requires **two distinct genuine human reviews**. Local scripts, hash checks, and similarity heuristics do not establish authentic source code provenance or vulnerability semantics.

### 3.1. Review Object Schema
Every review in the `reviews` array must contain exactly these 8 fields and no others:
- `reviewer`: Identifier string of the human reviewer.
- `reviewed_at`: ISO 8601 formatted timestamp string.
- `decision`: Must be exactly `"approve"`.
- `payload_sha256`: Hexadecimal SHA256 digest of the canonical JSON payload (see Section 3.2).
- `same_function_verified`: Boolean `true`, certifying both versions represent the exact same function.
- `security_fix_verified`: Boolean `true`, certifying the diff represents a valid security remediation.
- `source_revisions_verified`: Boolean `true`, certifying `fix_commit` and `parent_commit` link to genuine historical revisions.
- `explanation_supported`: Boolean `true`, certifying `key_difference` accurately reflects the causal fix.

### 3.2. Canonical Payload Hash Calculation
`payload_sha256` locks the integrity of the reviewed content. It is calculated by taking the SHA256 digest of the UTF-8 bytes of the full pair object excluding the `reviews` key, serialized with standard library `json.dumps`:

```python
import hashlib
import json

def compute_payload_sha256(pair_dict: dict) -> str:
    # Exclude reviews key completely from payload hashing
    payload = {k: v for k, v in pair_dict.items() if k != "reviews"}
    canonical_json = json.dumps(
        payload,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
```

*Governance Constraints*: Do not invent cryptographic signature requirements, active review expiration windows, or extra field names.

---

## 4. Exact Selection & Retrieval Protocol

When constructing B3 demonstrations for a target function:

1. **Exhaustive Fraction-Based Jaccard**:
   - Compute token-set Jaccard similarity between the target code tokens and `source.before` tokens.
   - Compute token-set Jaccard similarity between the target code tokens and `source.after` tokens.
   - Calculate the arithmetic mean: `(Jaccard(target, before) + Jaccard(target, after)) / 2`.
   - All computations must use exact rational arithmetic via Python `fractions.Fraction`:
     $$\text{Jaccard}(A, B) = \frac{|A \cap B|}{|A \cup B|}$$
   - The mean must be computed exhaustively across the entire pool of admitted pairs.

2. **Deterministic Tie-Breaking**:
   - In the event of identical mean Jaccard fractions, break ties strictly by the **lexicographic order** of `pair_id`.

3. **Prohibited Shortcuts**:
   - ❌ **No B2 anchor ranking**: Do not select pairs based on pre-existing B2 single-demonstration indices.
   - ❌ **No top-200 candidate shortcut**: The search must evaluate every admitted candidate pair exhaustively.
   - ❌ **No alternate fixed-index ranking**: Dynamic runtime sorting must strictly follow exact mean Jaccard.

---

## 5. Prompt Formatting & Budget Enforcement

### 5.1. Section Order (Figure 6 Contract)
Prompts must adhere strictly to the pre-registered structural sequence:
1. `role_domain`
2. `target_code`
3. `question`
4. `node_info`
5. `edge_info`
6. `demonstration` (containing both `source.before` and `source.after` with `key_difference`)
7. `answer`

Target labels must never enter the prompt.

### 5.2. Token Budget Caps
All inputs are evaluated using the model tokenizer against a hard 8,192 token limit:
- `target_code`: $\le 3,000$ tokens
- Graph (`node_info` + `edge_info`): $\le 1,500$ tokens
- Each demonstration function: $\le 1,500$ tokens
- Generation reserve: $64$ tokens
- **Overall context ceiling**: $\le 8,192$ tokens

### 5.3. Exception Handling
- **Oversized Pair Policy**: If the top-ranked admitted pair causes the demonstration or prompt to exceed the token budget, the runner **must halt immediately**. Silent fallback, reselection of sub-optimal pairs, or truncation of causal demonstration code is strictly forbidden.
- **Empty Pool Policy**: If no verified pair exists in the pool, execution **must pause immediately**. There is **no authorized fallback arm**.

---

## 6. Pre-Registration Threshold & Spec Governance

- **Immutability of Pre-registered Baseline**:
  - ❌ **NEVER edit or regenerate** `configs/thresholds.json` or `configs/thresholds_flat.json`.
  - ❌ **NEVER modify** frozen spec files (`data/specs/*_15arms.jsonl`), `configs/arms.yaml`, or `preregistration.md`.
- **Validation & Threshold Derivation**:
  - Evaluating B3 requires a full validation split run.
  - Derived candidate thresholds must be written to an independent, **separate candidate threshold artifact** under existing project rules.
- **Protocol Changes**:
  - Any modification to the protocol, experimental matrix, or thresholds requires an explicit, documented governance decision. This guide does not authorize any changes to frozen protocol artifacts.
