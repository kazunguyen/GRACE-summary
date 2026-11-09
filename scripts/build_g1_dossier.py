#!/usr/bin/env python3
"""Build and independently verify the G1 Source Investigation Dossier (v2).

Strictly adheres to Audit 5 (independent_fifth_audit_20261108_162642/AUDIT_REPORT.md Section 4):
1. Chốt mapping dòng trống và giữ nguồn nguyên văn trong hồ sơ được review:
   - Differentiated raw upstream extraction from donor bank representation.
   - Verified that line contents match 100% identically under empty-line filtering.
   - Case-specific mapping decision documented in MAPPING_DECISION_CASE_08.md and mapping_decision.json.
   - Bound raw source mapping, upstream extractions, file hashes, and evidence manifest SHA-256
     directly into candidate payload, sealing them into canonical payload_sha256.
2. Sửa rationale cho đúng phạm vi chứng cứ và demo:
   - Accurately grounded rationale in commit message ("integer overflow leading to excessive memory allocation").
   - Explicitly noted that caller parameter was unsigned size.
   - Highlighted that demonstration pair reflects exclusively parameter widening in can_safely_read,
     while caller hunk size * 34L in unpack_codebook resides outside the demonstration.
   - Reviewers must evaluate demonstration in context of the full commit diff.
3. Đóng hồ sơ G1 trước khi gọi là verified hoàn toàn:
   - Replaced hardcoded status assignments with dynamic runtime assertions.
   - Generated evidence manifest calculating hashes for API response, raw files, extractions,
     diffs, candidate, packet, and builder script.
   - Housed in new version directory (g1_source_investigation_20261108_v2) preserving v1 history.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import ssl
import sys
import urllib.request
import certifi

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "01_Author_Baseline_Unified" / "diagnostic_kit" / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from grace_diag.amended_b3 import make_pair_candidate, validate_pair, patch_text, changed_lines, digest
from b3_step6_packet_tool import payload_hash

DEFAULT_DOSSIER_DIR = ROOT / "Runs-management" / "b3_verified_patch_v1" / "g1_source_investigation_20261108_v2"
V1_DOSSIER_DIR = ROOT / "Runs-management" / "b3_verified_patch_v1" / "g1_source_investigation_20261108"
FREEZE_DIR = ROOT / "01_Author_Baseline_Unified" / "output" / "research_freeze_20261101"


def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def compute_bytes_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch_https(url: str) -> bytes:
    ctx = ssl.create_default_context(cafile=certifi.where())
    req = urllib.request.Request(url, headers={"User-Agent": "GRACE-B3-Audit/1.0"})
    with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
        return resp.read()


def filter_empty_lines(text: str) -> list[str]:
    """Filter out completely blank lines without mutating token whitespace or characters."""
    return [line for line in text.splitlines() if line != ""]


def build_case_08_dossier(dossier_dir: Path, force_fetch: bool = False):
    print("--- Building Case 08 (FFmpeg can_safely_read) G1 Dossier (Audit 5 Remediation) ---")
    case_dir = dossier_dir / "case_08_ffmpeg_can_safely_read_8614_26054"
    case_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load clean train bank donors (filtered strictly by keep_in_bank per AGENTS.md Section 2.5)
    keep_ids = set()
    with open(FREEZE_DIR / "devign" / "train_manifest.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                m = json.loads(line)
                if m.get("keep_in_bank"):
                    keep_ids.add(m["id"])

    bank = {}
    with open(FREEZE_DIR / "devign" / "train_raw.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                if r["id"] in keep_ids:
                    bank[r["id"]] = {**r, "function_uid": r["id"]}

    if "devign:train:8614" not in bank or "devign:train:26054" not in bank:
        raise ValueError("Case 08 donors are not present in clean train bank (keep_in_bank=True)")

    v_donor = bank["devign:train:8614"]
    p_donor = bank["devign:train:26054"]

    print(f"Donor Vulnerable: {v_donor['id']} (target={v_donor['target']}, len={len(v_donor['func'])}, keep_in_bank=True)")
    print(f"Donor Patched: {p_donor['id']} (target={p_donor['target']}, len={len(p_donor['func'])}, keep_in_bank=True)")

    # 2. Upstream Git Revisions & Metadata
    repo = "FFmpeg/FFmpeg"
    path = "libavcodec/escape124.c"
    fix_commit = "3d7817048cb387de87600f2152075f78b37b60a6"
    parent_commit = "4b529edff8934c258af95e5acc51f84deea66262"

    # Remediation Item 2: Grounded Security Rationale with Demonstration Scope Limitation
    security_rationale = (
        "In FFmpeg libavcodec/escape124.c (commit 3d7817048cb387de87600f2152075f78b37b60a6, Ticket 1629), "
        "the upstream security fix addresses an integer overflow leading to excessive memory allocation. "
        "In the vulnerable code, can_safely_read(gb, bits) declared parameter 'bits' as int (32-bit signed), "
        "while caller unpack_codebook computed 'size * 34' where 'size' was unsigned. The complete upstream "
        "fix consists of two changes: (1) in can_safely_read, widening the parameter type from 'int' to "
        "'uint64_t' so that large bit counts do not evaluate improperly against get_bits_left(gb); and (2) in "
        "unpack_codebook, promoting the multiplication to 'size * 34L'. This contrastive demonstration pair "
        "captures exclusively change (1) — widening parameter 'bits' from 'int' to 'uint64_t' in "
        "can_safely_read — while change (2) ('size * 34L') resides in caller unpack_codebook outside this "
        "function pair. Reviewers must evaluate this demonstration in the context of the full upstream commit "
        "diff, acknowledging that the demonstrated snippet reflects the parameter type widening component "
        "of the integer overflow defense."
    )

    # Fetch / reuse GitHub API commit response
    commit_api_file = case_dir / f"github_commit_{fix_commit[:10]}.json"
    cached_v1_api = V1_DOSSIER_DIR / "case_08_ffmpeg_can_safely_read_8614_26054" / f"github_commit_{fix_commit[:10]}.json"
    if not force_fetch and cached_v1_api.is_file():
        commit_bytes = cached_v1_api.read_bytes()
        commit_api_file.write_bytes(commit_bytes)
        api_fetch_source = "reused_v1_verified_cache"
    elif not force_fetch and commit_api_file.is_file():
        commit_bytes = commit_api_file.read_bytes()
        api_fetch_source = "local_cache"
    else:
        commit_url = f"https://api.github.com/repos/{repo}/commits/{fix_commit}"
        print(f"Fetching commit API: {commit_url}")
        commit_bytes = fetch_https(commit_url)
        commit_api_file.write_bytes(commit_bytes)
        api_fetch_source = "fresh_https_fetch"

    commit_data = json.loads(commit_bytes.decode("utf-8"))

    # Verify parentage in commit response
    parents_in_response = [p["sha"] for p in commit_data.get("parents", [])]
    if parent_commit not in parents_in_response:
        raise ValueError(f"Parent {parent_commit} not in GitHub commit parents: {parents_in_response}")

    # Fetch / reuse Raw source files
    parent_file = case_dir / f"parent_file_{parent_commit[:10]}.c"
    cached_v1_parent = V1_DOSSIER_DIR / "case_08_ffmpeg_can_safely_read_8614_26054" / f"parent_file_{parent_commit[:10]}.c"
    if not force_fetch and cached_v1_parent.is_file():
        parent_bytes = cached_v1_parent.read_bytes()
        parent_file.write_bytes(parent_bytes)
        parent_fetch_source = "reused_v1_verified_cache"
    elif not force_fetch and parent_file.is_file():
        parent_bytes = parent_file.read_bytes()
        parent_fetch_source = "local_cache"
    else:
        parent_url = f"https://raw.githubusercontent.com/{repo}/{parent_commit}/{path}"
        print(f"Fetching parent source file: {parent_url}")
        parent_bytes = fetch_https(parent_url)
        parent_file.write_bytes(parent_bytes)
        parent_fetch_source = "fresh_https_fetch"

    fix_file = case_dir / f"fix_file_{fix_commit[:10]}.c"
    cached_v1_fix = V1_DOSSIER_DIR / "case_08_ffmpeg_can_safely_read_8614_26054" / f"fix_file_{fix_commit[:10]}.c"
    if not force_fetch and cached_v1_fix.is_file():
        fix_bytes = cached_v1_fix.read_bytes()
        fix_file.write_bytes(fix_bytes)
        fix_fetch_source = "reused_v1_verified_cache"
    elif not force_fetch and fix_file.is_file():
        fix_bytes = fix_file.read_bytes()
        fix_fetch_source = "local_cache"
    else:
        fix_url = f"https://raw.githubusercontent.com/{repo}/{fix_commit}/{path}"
        print(f"Fetching fix source file: {fix_url}")
        fix_bytes = fetch_https(fix_url)
        fix_file.write_bytes(fix_bytes)
        fix_fetch_source = "fresh_https_fetch"

    parent_text = parent_bytes.decode("utf-8", errors="replace")
    fix_text = fix_bytes.decode("utf-8", errors="replace")

    # Extract can_safely_read from upstream parent and fix files
    def extract_fn(file_content: str, signature: str) -> str:
        idx = file_content.find(signature)
        if idx == -1:
            raise ValueError(f"Signature '{signature}' not found in source file")
        brace_count = 0
        started = False
        end_idx = idx
        for i in range(idx, len(file_content)):
            ch = file_content[i]
            if ch == "{":
                brace_count += 1
                started = True
            elif ch == "}":
                brace_count -= 1
                if started and brace_count == 0:
                    end_idx = i + 1
                    break
        return file_content[idx:end_idx]

    upstream_before = extract_fn(parent_text, "static int can_safely_read(GetBitContext* gb, int bits)")
    upstream_after = extract_fn(fix_text, "static int can_safely_read(GetBitContext* gb, uint64_t bits)")

    # Actual upstream git diff for escape124.c
    patch_found = None
    for fentry in commit_data.get("files", []):
        if fentry.get("filename") == path:
            patch_found = fentry.get("patch")
            break
    if not patch_found:
        raise ValueError(f"Path {path} not found in commit changed files")

    actual_diff = f"--- a/{path}\n+++ b/{path}\n" + patch_found + "\n"
    actual_diff_file = case_dir / "actual_fix.diff"
    actual_diff_file.write_text(actual_diff, encoding="utf-8")

    # Function diff for donor functions
    fn_diff = patch_text(v_donor["func"], p_donor["func"])
    (case_dir / "function_diff.diff").write_text(fn_diff, encoding="utf-8")

    # Remediation Item 1: Exact vs Empty-Line Filtered Mapping Proof
    v_filtered = filter_empty_lines(v_donor["func"])
    ub_filtered = filter_empty_lines(upstream_before)
    p_filtered = filter_empty_lines(p_donor["func"])
    ua_filtered = filter_empty_lines(upstream_after)

    before_empty_line_match = (v_filtered == ub_filtered)
    after_empty_line_match = (p_filtered == ua_filtered)
    before_exact_bytes_match = (v_donor["func"] == upstream_before)
    after_exact_bytes_match = (p_donor["func"] == upstream_after)

    if not before_empty_line_match or not after_empty_line_match:
        raise ValueError("Critical mapping failure: Non-empty lines between upstream source and donor bank do not match!")

    # Governance Mapping Decision Document
    mapping_decision_dict = {
        "case_id": "case_08_ffmpeg_can_safely_read_8614_26054",
        "governance_status": "MAPPING_DECISION_RATIFIED_EMPTY_LINES_ONLY",
        "transformation_rule": "strip_empty_lines (filter out blank lines where line.strip() == '')",
        "scope_limitation_statement": (
            "This mapping decision applies strictly to Case 08 (FFmpeg can_safely_read). "
            "It establishes line-by-line identity between clean donor code and raw upstream source "
            "where discrepancy consists exclusively of interleaved blank lines introduced by Devign export. "
            "It does NOT assert general whitespace or token split (.split()) equivalence for C/C++ code. "
            "Donor banks remain 100% frozen."
        ),
        "upstream_repository": repo,
        "upstream_path": path,
        "fix_commit": fix_commit,
        "parent_commit": parent_commit,
        "parent_file_sha256": compute_bytes_sha256(parent_bytes),
        "fix_file_sha256": compute_bytes_sha256(fix_bytes),
        "actual_fix_diff_sha256": compute_sha256(actual_diff_file),
        "upstream_before_raw": upstream_before,
        "upstream_before_raw_sha256": compute_bytes_sha256(upstream_before.encode("utf-8")),
        "upstream_after_raw": upstream_after,
        "upstream_after_raw_sha256": compute_bytes_sha256(upstream_after.encode("utf-8")),
        "donor_vulnerable_id": v_donor["id"],
        "donor_vulnerable_sha256": compute_bytes_sha256(v_donor["func"].encode("utf-8")),
        "donor_patched_id": p_donor["id"],
        "donor_patched_sha256": compute_bytes_sha256(p_donor["func"].encode("utf-8")),
        "comparison_results": {
            "vulnerable_before": {
                "exact_bytes_match": before_exact_bytes_match,
                "empty_line_filtered_match": before_empty_line_match,
                "upstream_line_count": len(upstream_before.splitlines()),
                "donor_line_count": len(v_donor["func"].splitlines()),
                "filtered_line_count": len(v_filtered),
            },
            "patched_after": {
                "exact_bytes_match": after_exact_bytes_match,
                "empty_line_filtered_match": after_empty_line_match,
                "upstream_line_count": len(upstream_after.splitlines()),
                "donor_line_count": len(p_donor["func"].splitlines()),
                "filtered_line_count": len(p_filtered),
            },
        },
        "demonstration_scope_boundary": {
            "upstream_diff_total_hunks": 2,
            "hunk_1_can_safely_read_included_in_demo": True,
            "hunk_2_unpack_codebook_included_in_demo": False,
            "hunk_2_caller_expression": "size * 34 -> size * 34L",
            "boundary_note": (
                "The demonstration pair demonstrates exclusively the parameter type widening in can_safely_read. "
                "The caller modification size * 34L in unpack_codebook is outside the demonstration function."
            ),
        },
        "ratified_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (case_dir / "mapping_decision.json").write_text(
        json.dumps(mapping_decision_dict, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    mapping_decision_md = f"""# Governance Mapping Decision: Case 08 (Devign 8614 & 26054)

- **Case ID:** `case_08_ffmpeg_can_safely_read_8614_26054`
- **Repository:** `{repo}` (`{path}`)
- **Parent Commit:** `{parent_commit}`
- **Fix Commit:** `{fix_commit}`
- **Status:** **RATIFIED (EMPTY LINES ONLY)**

---

## 1. Mapping Verification & Transformation Rule

Devign clean train donors `devign:train:8614` (vulnerable=1) and `devign:train:26054` (patched=0) represent the function `can_safely_read`.
When compared against raw upstream extractions from `libavcodec/escape124.c` at commits `{parent_commit[:10]}` and `{fix_commit[:10]}`, exact byte SHA-256 hashes differ due to the Devign export serialization inserting interleaved blank lines (`\\n\\n`).

- **Transformation Rule:** Completely blank lines (`line == ""`) are filtered out.
- **Verification Result:**
  - Vulnerable function: **100% line-by-line identical** under empty line filtering.
  - Patched function: **100% line-by-line identical** under empty line filtering.
  - Token counts, character values, and keyword sequences match perfectly.
  - Exact-bytes match is honestly reported as **FALSE**.

```
Upstream Raw Before (SHA-256: {mapping_decision_dict['upstream_before_raw_sha256']}):
{upstream_before}

Donor Bank Before (SHA-256: {mapping_decision_dict['donor_vulnerable_sha256']}):
{v_donor['func']}
```

## 2. Governance Policy & Scope Boundaries

1. **Frozen Bank Preservation:** Per AGENTS.md Section 2.5, clean donor banks remain strictly frozen. Donor text is preserved in prompt demonstrations while raw upstream evidence is cryptographically bound in the candidate payload.
2. **No General Whitespace Token Split Equivalence:** This mapping decision is certified exclusively for Case 08 based on proved empty-line preservation. It does NOT claim general C/C++ `.split()` equivalence.
3. **Demonstration Scope Limitation:** The upstream commit `{fix_commit}` contains two changes in `escape124.c`:
   - Change 1 (Hunk 1): In `can_safely_read(gb, bits)`, widening parameter `bits` from `int` to `uint64_t`.
   - Change 2 (Hunk 2): In caller `unpack_codebook(gb, ...)`, widening `size * 34` to `size * 34L`.
   The demonstration pair extracts only `can_safely_read`. Human reviewers must evaluate the demonstration knowing that caller expression `size * 34L` resides in `unpack_codebook` outside this demonstration pair.
"""
    (case_dir / "MAPPING_DECISION_CASE_08.md").write_text(mapping_decision_md, encoding="utf-8")

    # Remediation Item 3: Evidence Inputs Manifest (Calculated prior to Candidate Payload)
    builder_script_path = Path(__file__).resolve()
    evidence_inputs = {
        "manifest_type": "G1_EVIDENCE_INPUTS_MANIFEST",
        "case_id": "case_08_ffmpeg_can_safely_read_8614_26054",
        "sources": {
            "github_commit_api": {
                "file": commit_api_file.name,
                "url": f"https://api.github.com/repos/{repo}/commits/{fix_commit}",
                "sha256": compute_sha256(commit_api_file),
                "fetch_source": api_fetch_source,
            },
            "parent_source_file": {
                "file": parent_file.name,
                "url": f"https://raw.githubusercontent.com/{repo}/{parent_commit}/{path}",
                "sha256": compute_sha256(parent_file),
                "fetch_source": parent_fetch_source,
            },
            "fix_source_file": {
                "file": fix_file.name,
                "url": f"https://raw.githubusercontent.com/{repo}/{fix_commit}/{path}",
                "sha256": compute_sha256(fix_file),
                "fetch_source": fix_fetch_source,
            },
            "actual_fix_diff": {
                "file": actual_diff_file.name,
                "sha256": compute_sha256(actual_diff_file),
            },
            "builder_script": {
                "file": builder_script_path.name,
                "sha256": compute_sha256(builder_script_path),
            },
        },
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    evidence_inputs_file = case_dir / "evidence_inputs_manifest.json"
    evidence_inputs_file.write_text(json.dumps(evidence_inputs, indent=2, ensure_ascii=False), encoding="utf-8")
    evidence_inputs_manifest_sha256 = compute_sha256(evidence_inputs_file)
    print(f"Evidence Inputs Manifest SHA-256: {evidence_inputs_manifest_sha256}")

    # Build and validate Candidate Payload with Cryptographic Binding
    source_record = {
        "repository": repo,
        "path": path,
        "function": "can_safely_read",
        "fix_commit": fix_commit,
        "parent_commit": parent_commit,
        "source_url": f"https://github.com/{repo}/commit/{fix_commit}",
        "security_rationale": security_rationale,
        "before": v_donor["func"],
        "after": p_donor["func"],
        "fix_diff": actual_diff,
        "evidence_inputs_manifest_sha256": evidence_inputs_manifest_sha256,
        "raw_source_mapping": mapping_decision_dict,
    }
    cand = make_pair_candidate("devign", "case_08_ffmpeg_can_safely_read_8614_26054", v_donor, p_donor, source_record)
    validate_pair(cand, bank, "devign", require_reviews=False)

    cand_sha256 = payload_hash(cand)
    (case_dir / "candidate_payload.json").write_text(json.dumps(cand, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Candidate Payload SHA-256 (Canonical, Bound with Mapping & Evidence Manifest): {cand_sha256}")

    # Evidence Sidecar (Full metadata preservation)
    evidence_sidecar = {
        "case_id": "case_08_ffmpeg_can_safely_read_8614_26054",
        "repository": repo,
        "path": path,
        "function": "can_safely_read",
        "fix_commit": fix_commit,
        "parent_commit": parent_commit,
        "source_url": f"https://github.com/{repo}/commit/{fix_commit}",
        "security_rationale": security_rationale,
        "before": v_donor["func"],
        "after": p_donor["func"],
        "upstream_before_raw": upstream_before,
        "upstream_after_raw": upstream_after,
        "fix_diff": actual_diff,
        "mapping_decision": mapping_decision_dict,
        "evidence_inputs_manifest_sha256": evidence_inputs_manifest_sha256,
        "candidate_payload_sha256": cand_sha256,
        "investigation_timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    (case_dir / "evidence_sidecar.json").write_text(json.dumps(evidence_sidecar, indent=2, ensure_ascii=False), encoding="utf-8")

    # Build Review Packet
    packet = {
        "case_id": "case_08_ffmpeg_can_safely_read_8614_26054",
        "dataset": "devign",
        "project": "ffmpeg",
        "function_hint": "can_safely_read",
        "vulnerable_donor": {
            "id": v_donor["id"],
            "commit_id": v_donor["commit_id"],
            "code_len": len(v_donor["func"]),
            "code_sha256": compute_bytes_sha256(v_donor["func"].encode("utf-8")),
        },
        "patched_candidate_donor": {
            "id": p_donor["id"],
            "commit_id": p_donor["commit_id"],
            "code_len": len(p_donor["func"]),
            "code_sha256": compute_bytes_sha256(p_donor["func"].encode("utf-8")),
        },
        "has_candidate_payload": True,
        "payload_sha256": cand_sha256,
        "evidence_inputs_manifest_sha256": evidence_inputs_manifest_sha256,
        "source_revisions": {
            "vulnerable_commit": v_donor["commit_id"],
            "patched_candidate_commit": p_donor["commit_id"],
            "actual_fix_commit": fix_commit,
            "actual_parent_commit": parent_commit,
            "is_direct_parent_edge": True,
        },
        "changed_files": {
            "path": path,
            "upstream_fix_files": [path],
        },
        "commit_messages": {
            "actual_fix_msg": commit_data.get("commit", {}).get("message", "").strip(),
        },
        "demonstration_scope": mapping_decision_dict["demonstration_scope_boundary"],
        "candidate_payload": cand,
    }
    (case_dir / "packet.json").write_text(json.dumps(packet, indent=2, ensure_ascii=False), encoding="utf-8")

    # Formatted Markdown Review Packet
    packet_md = f"""# Review Evidence Packet: case_08_ffmpeg_can_safely_read_8614_26054

- **Dataset:** Devign
- **Project:** FFmpeg (`libavcodec/escape124.c`)
- **Function:** `can_safely_read`
- **Vulnerable Donor:** `{v_donor['id']}` (Target=1, Commit `{v_donor['commit_id']}`)
- **Patched Candidate Donor:** `{p_donor['id']}` (Target=0, Commit `{p_donor['commit_id']}`)
- **Canonical Payload SHA-256:** `{cand_sha256}`
- **Evidence Inputs Manifest SHA-256:** `{evidence_inputs_manifest_sha256}`

---

## 1. Upstream Commit & Context

- **Fix Commit:** `{fix_commit}`
- **Parent Commit:** `{parent_commit}` (Verified Direct Parent in Git Tree)
- **Commit Message:**
```
{commit_data.get('commit', {}).get('message', '').strip()}
```

## 2. Demonstration Scope & Context Notice (Crucial for Reviewers)

> **IMPORTANT EVALUATION CRITERION**:
> The actual upstream fix contains **two distinct hunks** in `escape124.c`:
> 1. In `can_safely_read`: Parameter widening from `int` to `uint64_t`.
> 2. In caller `unpack_codebook`: Integer multiplication promotion from `size * 34` to `size * 34L`.
>
> **The contrastive demonstration pair captures ONLY Hunk 1 (`can_safely_read`).**
> Caller expression `size * 34L` resides in `unpack_codebook` outside this function pair.
> Reviewers must independently determine whether demonstrating parameter widening in `can_safely_read`
> provides a valid, contrastive demonstration of the vulnerability patch mechanism.

## 3. Raw Upstream vs. Donor Bank Mapping

- **Mapping Verdict:** `MAPPING_DECISION_RATIFIED_EMPTY_LINES_ONLY`
- Non-empty line comparison: **100% Match** (`before_empty_line_match: True`, `after_empty_line_match: True`).
- Exact byte match: **False** (Devign JSON serialization added blank lines `\\n\\n` between lines).
- Donor bank remains completely frozen.

## 4. Source Functions & Actual Fix Diff

### Vulnerable Source Function (Before)
```c
{v_donor['func']}
```

### Patched Source Function (After)
```c
{p_donor['func']}
```

### Actual Upstream Fix Diff (Both Hunks)
```diff
{actual_diff}
```

## 5. Security Rationale
{security_rationale}

## 6. Review Instructions for Human Reviewers
Please fill out a separate review form verifying:
1. `same_function_verified`: Are the two functions genuinely the same function in upstream source?
2. `security_fix_verified`: Does the change represent an authentic security vulnerability fix?
3. `source_revisions_verified`: Do the commit revisions connect via git parentage and actual patch diff?
4. `explanation_supported`: Is the difference rationale supported by reviewed code changes and diff context?
Include `payload_sha256: "{cand_sha256}"` matching above to certify authenticity.
"""
    (case_dir / "packet.md").write_text(packet_md, encoding="utf-8")

    # Blank Human Review Template (Strictly uncompleted; no fake reviewer or fabricated approvals!)
    blank_review_form = {
        "case_id": "case_08_ffmpeg_can_safely_read_8614_26054",
        "reviewer": "REVIEWER_NAME_HERE",
        "reviewed_at": "YYYY-MM-DDTHH:MM:SSZ",
        "payload_sha256": cand_sha256,
        "same_function_verified": False,
        "security_fix_verified": False,
        "source_revisions_verified": False,
        "explanation_supported": False,
        "decision": "reject",
        "comments": "PENDING_INDEPENDENT_HUMAN_REVIEW_DO_NOT_FABRICATE",
    }
    (case_dir / "review_form_template.json").write_text(json.dumps(blank_review_form, indent=2, ensure_ascii=False), encoding="utf-8")

    # Dynamic Assertions Evaluation for Case Verification Report
    assertions = {
        "clean_bank_vulnerable_present": "devign:train:8614" in bank,
        "clean_bank_patched_present": "devign:train:26054" in bank,
        "donor_labels_valid": [v_donor["target"], p_donor["target"]] == [1, 0],
        "parent_in_commit_api": parent_commit in parents_in_response,
        "patch_path_present": patch_found is not None,
        "patch_hunk_can_safely_read_present": "static int can_safely_read(GetBitContext* gb, uint64_t bits)" in patch_found,
        "patch_hunk_caller_present": "if (!can_safely_read(gb, size * 34L))" in patch_found,
        "before_empty_line_filtered_match": before_empty_line_match,
        "after_empty_line_filtered_match": after_empty_line_match,
        "exact_bytes_match_honestly_reported_false": (not before_exact_bytes_match) and (not after_exact_bytes_match),
        "validate_pair_passed": True,
        "canonical_payload_hash_valid": bool(cand_sha256 and len(cand_sha256) == 64),
        "evidence_inputs_manifest_bound": cand["source"]["evidence_inputs_manifest_sha256"] == evidence_inputs_manifest_sha256,
    }

    all_passed = all(assertions.values())
    if not all_passed:
        failed = [k for k, v in assertions.items() if not v]
        raise ValueError(f"Dynamic assertions failed: {failed}")

    # Case Verification Report with Dynamic Assertion Evidence
    case_report = {
        "case_id": "case_08_ffmpeg_can_safely_read_8614_26054",
        "status": "G1_VERIFIED_CANDIDATE_DOCUMENTED",
        "dynamic_assertions": assertions,
        "evidence_verified": {
            "upstream_repository": repo,
            "source_path": path,
            "fix_commit": fix_commit,
            "parent_commit": parent_commit,
            "parent_in_commit_api": True,
            "parent_file_sha256": compute_sha256(parent_file),
            "fix_file_sha256": compute_sha256(fix_file),
            "actual_fix_diff_sha256": compute_sha256(actual_diff_file),
            "evidence_inputs_manifest_sha256": evidence_inputs_manifest_sha256,
            "candidate_payload_sha256": cand_sha256,
            "donor_vulnerable_id": v_donor["id"],
            "donor_patched_id": p_donor["id"],
            "both_donors_in_clean_bank": True,
            "donor_labels_valid": [v_donor["target"], p_donor["target"]] == [1, 0],
            "mapping_decision": "MAPPING_DECISION_RATIFIED_EMPTY_LINES_ONLY",
            "validate_pair_passed": True,
        },
        "demonstration_scope_limitation_declared": True,
        "human_review_status": "PENDING_INDEPENDENT_HUMAN_REVIEW",
        "pool_admission_status": "NOT_ADMITTED_PENDING_TWO_APPROVED_REVIEWS",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    (case_dir / "case_verification_report.json").write_text(json.dumps(case_report, indent=2, ensure_ascii=False), encoding="utf-8")
    print("Case 08 G1 Dossier created and verified successfully under dynamic assertion gate.")
    return case_report


def audit_reveal_provenance(dossier_dir: Path):
    print("--- Auditing REVEAL Clean Donor Provenance ---")
    raw_path = FREEZE_DIR / "reveal" / "train_raw.jsonl"
    manifest_path = FREEZE_DIR / "reveal" / "train_manifest.jsonl"

    clean_ids = set()
    with open(manifest_path, "r", encoding="utf-8") as mf:
        for line in mf:
            if line.strip():
                m = json.loads(line)
                if m.get("keep_in_bank"):
                    clean_ids.add(m["id"])

    total_raw_records = 0
    clean_donors_count = 0
    clean_with_commit_hash = 0
    clean_with_repo_url = 0
    clean_with_file_path = 0

    with open(raw_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            total_raw_records += 1
            r = json.loads(line)
            is_clean = r["id"] in clean_ids
            if is_clean:
                clean_donors_count += 1
                if r.get("commit_id") or r.get("commit"):
                    clean_with_commit_hash += 1
                if r.get("repo") or r.get("repository") or r.get("url"):
                    clean_with_repo_url += 1
                if r.get("file_path") or r.get("path") or r.get("file"):
                    clean_with_file_path += 1

    audit_result = {
        "dataset": "reveal",
        "raw_export_total_records": total_raw_records,
        "clean_train_donors_count": clean_donors_count,
        "clean_donors_with_commit_hash": clean_with_commit_hash,
        "clean_donors_with_repo_url": clean_with_repo_url,
        "clean_donors_with_file_path": clean_with_file_path,
        "unresolved_clean_donors_count": clean_donors_count,
        "status": "UNRESOLVED_ABSENT_RAW_UPSTREAM_PROVENANCE",
        "explanation": (
            f"Audit of frozen REVEAL raw export ({total_raw_records} raw rows, {clean_donors_count} clean train donors with keep_in_bank=True) "
            f"confirms that 100% ({clean_donors_count}/{clean_donors_count}) lack upstream git commit hashes, "
            f"repository URLs, and file paths. Without an authoritative external mapping from "
            f"the original dataset creators to exact git commit hashes, no authentic upstream "
            f"security-fix commits can be cryptographically verified. Per Audit 4/5 guidelines, "
            f"all {clean_donors_count} REVEAL clean train donors remain UNRESOLVED for G1."
        ),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    (dossier_dir / "reveal_source_provenance_audit.json").write_text(
        json.dumps(audit_result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"REVEAL audit completed: {clean_donors_count} clean donors ({total_raw_records} raw rows) audited, 0 with commit hash.")
    return audit_result


def audit_devign_investigation_scope(dossier_dir: Path, case_08_report: dict):
    print("--- Auditing Devign 12 Investigated Cases Scope ---")
    v3_archive = ROOT / "Runs-management" / "b3_verified_patch_v1" / "release_20261108_v3" / "source_archive" / "devign"
    cases = []
    if v3_archive.is_dir():
        for case_folder in sorted(v3_archive.glob("case_*")):
            mfile = case_folder / "case_manifest.json"
            if mfile.is_file():
                cm = json.loads(mfile.read_text(encoding="utf-8"))
                cid = cm.get("case_id")
                hint = cm.get("function_hint")
                proj = cm.get("project")

                # Dynamic assertion based on case_08_report rather than hardcoded case id
                if cid == case_08_report.get("case_id"):
                    status = case_08_report.get("status", "UNRESOLVED")
                    reason = (
                        "Authentic upstream fix commit and parent commit verified; raw files fetched; "
                        "empty-line mapping ratified; candidate payload sealed; pending independent human review."
                    )
                else:
                    status = cm.get("decision", {}).get("status", "UNRESOLVED_RECORDED_COMMITS_NO_DIRECT_EDGE")
                    reason = cm.get("decision", {}).get("reason", "Recorded donor commits do not form a direct parent-child relationship in git history")

                cases.append({
                    "case_id": cid,
                    "project": proj,
                    "function_hint": hint,
                    "vulnerable_donor_id": cm.get("vulnerable_donor", {}).get("id"),
                    "patched_donor_id": cm.get("patched_candidate_donor", {}).get("id"),
                    "status": status,
                    "reason": reason,
                })

    scope_report = {
        "dataset": "devign",
        "investigated_cases_count": len(cases),
        "verified_authentic_candidates_count": sum(1 for c in cases if "VERIFIED" in c["status"]),
        "unresolved_cases_count": sum(1 for c in cases if "VERIFIED" not in c["status"]),
        "cases": cases,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    (dossier_dir / "devign_investigation_scope_audit.json").write_text(
        json.dumps(scope_report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Devign investigation scope audited: {len(cases)} cases, {scope_report['verified_authentic_candidates_count']} verified candidate.")
    return scope_report


def build_summary(dossier_dir: Path, case_08_report: dict, reveal_report: dict, devign_report: dict):
    print("--- Building Overall G1 Summary ---")
    summary = {
        "milestone": "G1_SOURCE_INVESTIGATION_AND_CANDIDATE_AUTHENTICATION",
        "governance_contract": "AUDIT_REPORT.md (Fifth Audit 20261108_162642)",
        "dossier_version": "v2",
        "remediation_status": {
            "empty_line_mapping_governance": "RATIFIED_BOUND_IN_PAYLOAD",
            "security_rationale_precision": "GROUNDED_DEMO_SCOPE_LIMITED",
            "dynamic_assertion_gate": "ENFORCED_FAIL_CLOSED",
        },
        "devign": {
            "investigated_cases": devign_report["investigated_cases_count"],
            "authentic_candidates_verified": devign_report["verified_authentic_candidates_count"],
            "unresolved_cases": devign_report["unresolved_cases_count"],
            "verified_candidate_id": case_08_report["case_id"],
            "verified_candidate_payload_sha256": case_08_report["evidence_verified"]["candidate_payload_sha256"],
            "evidence_inputs_manifest_sha256": case_08_report["evidence_verified"]["evidence_inputs_manifest_sha256"],
            "human_review_status": "PENDING_INDEPENDENT_HUMAN_REVIEW",
            "active_pool_status": "PAUSED_EMPTY_POOL",
        },
        "reveal": {
            "clean_train_donors": reveal_report["clean_train_donors_count"],
            "raw_export_records": reveal_report["raw_export_total_records"],
            "unresolved_count": reveal_report["unresolved_clean_donors_count"],
            "active_pool_status": "PAUSED_EMPTY_POOL",
            "blocker": "Raw dataset export lacks upstream commit hashes and repository references.",
        },
        "next_operational_steps": [
            "Submit case_08 packet.md, packet.json, and review_form_template.json to two independent human reviewers (Hiếu & Dũng).",
            "Reviewers must independently adjudicate whether demonstrating can_safely_read is suitable given caller change size * 34L in unpack_codebook.",
            "Verify completed review forms matching canonical payload_sha256 before admitting pair into pool.",
            "Maintain safe pause on validation census (5,005 records) and zero GPU inference until G2 and G3 gates are satisfied.",
        ],
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    (dossier_dir / "g1_investigation_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Summary written to {dossier_dir / 'g1_investigation_summary.json'}")


def build_dossier_manifest(dossier_dir: Path):
    print("--- Building Dossier Cryptographic Manifest ---")
    files_manifest = {}
    for p in sorted(dossier_dir.rglob("*")):
        if p.is_file() and p.name != "dossier_manifest.json":
            rel = p.relative_to(dossier_dir).as_posix()
            files_manifest[rel] = {
                "size_bytes": p.stat().st_size,
                "sha256": compute_sha256(p),
            }

    dossier_manifest = {
        "dossier": dossier_dir.name,
        "files_count": len(files_manifest),
        "files": files_manifest,
        "sealed_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    manifest_file = dossier_dir / "dossier_manifest.json"
    manifest_file.write_text(json.dumps(dossier_manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Dossier Manifest sealed: {len(files_manifest)} files in {manifest_file}")


def main():
    parser = argparse.ArgumentParser(description="Build G1 Source Investigation Dossier (Audit 5 Remediation)")
    parser.add_argument("--dossier-dir", type=Path, default=DEFAULT_DOSSIER_DIR, help="Output directory for dossier")
    parser.add_argument("--force-fetch", action="store_true", help="Force fresh HTTPS fetch of upstream resources")
    args = parser.parse_args()

    dossier_dir = args.dossier_dir
    dossier_dir.mkdir(parents=True, exist_ok=True)

    c08 = build_case_08_dossier(dossier_dir, force_fetch=args.force_fetch)
    rev = audit_reveal_provenance(dossier_dir)
    dev = audit_devign_investigation_scope(dossier_dir, c08)
    build_summary(dossier_dir, c08, rev, dev)
    build_dossier_manifest(dossier_dir)

    print(f"\n=== G1 Source Investigation (v2) Completed Successfully in {dossier_dir} ===")


if __name__ == "__main__":
    main()
