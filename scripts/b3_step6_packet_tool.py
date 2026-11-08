#!/usr/bin/env python3
"""Step 6: Review Packet Generation, Automated Technical Triage, and Pool Manifest Seal.

Implements the strict separation between:
1. Automated Technical Triage (machine checks of git parentage, files, diffs)
2. Review Packet Generation (evidence packets with canonical payload_sha256)
3. Independent Human Review Ingestion (validates real reviewer forms without fabrication)
4. Eligible Pair Pool Manifest Seal (freeze of verified pair pool)

Addresses audit finding F01: eliminates all auto-generated review comments and fake signatures.
"""

import argparse
from datetime import datetime, timezone, timedelta
import hashlib
import json
import os
from pathlib import Path
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RELEASE_DIR = ROOT / "Runs-management" / "b3_verified_patch_v1" / "release_20261108_v3"
SRC = ROOT / "01_Author_Baseline_Unified" / "diagnostic_kit" / "src"
sys.path.insert(0, str(SRC))

from grace_diag.amended_b3 import digest, payload_hash, validate_pair


def compute_file_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def compute_bytes_sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def generate_review_packets(release_dir: Path, candidates: list = None):
    archive_dir = release_dir / "source_archive" / "devign"
    packets_dir = release_dir / "review_packets"
    candidates_dir = release_dir / "candidates"
    packets_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load candidate pairs if available to ensure packet binds to full pair payload (R1)
    candidates_by_id = {}
    if candidates:
        for c in candidates:
            candidates_by_id[c["pair_id"]] = c
    else:
        cand_file = candidates_dir / "candidates.jsonl"
        if cand_file.is_file():
            with open(cand_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        c = json.loads(line)
                        candidates_by_id[c["pair_id"]] = c

    case_manifests = []
    if archive_dir.is_dir():
        for case_folder in sorted(archive_dir.glob("case_*")):
            mfile = case_folder / "case_manifest.json"
            if mfile.is_file():
                with open(mfile, "r", encoding="utf-8") as f:
                    cm = json.load(f)
                    case_manifests.append(cm)
                    cid = cm.get("case_id")
                    if cid and cid not in candidates_by_id:
                        if (case_folder / "candidate.json").is_file():
                            with open(case_folder / "candidate.json", "r", encoding="utf-8") as cf:
                                candidates_by_id[cid] = json.load(cf)
                        elif cm.get("candidate"):
                            candidates_by_id[cid] = cm["candidate"]

    packets = []
    for cm in case_manifests:
        case_id = cm["case_id"]
        proj = cm["project"]
        hint = cm["function_hint"]
        sinv = cm["source_investigation"]
        v_sha = cm["vulnerable_donor"]["commit_id"]
        p_sha = cm["patched_candidate_donor"]["commit_id"]

        candidate = candidates_by_id.get(case_id)
        has_cand = candidate is not None

        if has_cand:
            cand_body = {k: v for k, v in candidate.items() if k != "reviews"}
            packet_sha256 = payload_hash(candidate)
        else:
            cand_body = None
            packet_sha256 = None

        packet = {
            "case_id": case_id,
            "dataset": "devign",
            "project": proj,
            "function_hint": hint,
            "vulnerable_donor": cm["vulnerable_donor"],
            "patched_candidate_donor": cm["patched_candidate_donor"],
            "has_candidate_payload": has_cand,
            "payload_sha256": packet_sha256,
            "source_revisions": {
                "vulnerable_commit": v_sha,
                "patched_candidate_commit": p_sha,
                "vulnerable_parents": sinv.get("vulnerable_parent_shas", []),
                "patched_parents": sinv.get("patched_parent_shas", []),
                "is_direct_parent_edge": sinv.get("is_direct_parent_edge", False),
            },
            "changed_files": {
                "vulnerable_files": sinv.get("vulnerable_changed_files", []),
                "patched_files": sinv.get("patched_changed_files", []),
                "shared_files": sinv.get("shared_files", []),
            },
            "commit_messages": {
                "vulnerable_commit_msg": sinv.get("vulnerable_commit_msg", ""),
                "patched_commit_msg": sinv.get("patched_commit_msg", ""),
            },
        }
        if has_cand:
            packet["candidate_payload"] = cand_body

        # Save packet JSON
        with open(packets_dir / f"{case_id}.json", "w", encoding="utf-8") as pf:
            json.dump(packet, pf, indent=2, ensure_ascii=False)

        # Markdown evidence with archived code and fix diff
        evidence_md = ""
        if has_cand and "source" in candidate:
            src = candidate["source"]
            evidence_md = f"""
## Archived Source Evidence
- **Repository:** `{src.get('repository')}`
- **Source File Path:** `{src.get('path')}`
- **Security Rationale:** {src.get('security_rationale', '')}
- **Key Difference:** {candidate.get('key_difference', '')}

### Vulnerable Source Function (Before)
```c
{src.get('before', '')}
```

### Patched Source Function (After)
```c
{src.get('after', '')}
```

### Actual Fix Diff
```diff
{src.get('fix_diff', '')}
```
"""

        packet_md = f"""# Review Evidence Packet: {case_id}

- **Dataset:** Devign
- **Project:** {proj}
- **Function Hint:** `{hint}`
- **Vulnerable Donor:** `{cm['vulnerable_donor']['id']}` (Commit `{v_sha}`)
- **Patched Candidate:** `{cm['patched_candidate_donor']['id']}` (Commit `{p_sha}`)
- **Payload SHA-256 (Canonical Candidate Hash):** `{packet_sha256 or 'INELIGIBLE_NO_CANDIDATE'}`
- **Admissible Candidate Available:** **{has_cand}**

## Source Revisions
- Direct Parent Edge in Git: **{sinv.get('is_direct_parent_edge', False)}**
- Vulnerable Parents: `{sinv.get('vulnerable_parent_shas', [])}`
- Patched Parents: `{sinv.get('patched_parent_shas', [])}`

## Changed Files
- Vulnerable Commit Modified: `{sinv.get('vulnerable_changed_files', [])}`
- Patched Commit Modified: `{sinv.get('patched_changed_files', [])}`
- Shared Files: `{sinv.get('shared_files', [])}`

## Commit Messages
- **Vulnerable:** {sinv.get('vulnerable_commit_msg', '')}
- **Patched:** {sinv.get('patched_commit_msg', '')}
{evidence_md}
## Review Instructions for Human Reviewers
Please fill out a separate review form verifying:
1. `same_function_verified`: Are the two functions genuinely the same function in upstream source?
2. `security_fix_verified`: Does the change represent an authentic security vulnerability fix?
3. `source_revisions_verified`: Do the commit revisions connect via git parentage and actual patch diff?
4. `explanation_supported`: Is the difference rationale supported by reviewed code changes?
Include `payload_sha256` matching above to certify authenticity.
"""
        with open(packets_dir / f"{case_id}.md", "w", encoding="utf-8") as pmf:
            pmf.write(packet_md)

        # Save blank review form template
        blank_form = {
            "case_id": case_id,
            "reviewer": "REVIEWER_NAME_HERE",
            "reviewed_at": "YYYY-MM-DDTHH:MM:SSZ",
            "payload_sha256": packet_sha256 or "INELIGIBLE_NO_CANDIDATE",
            "same_function_verified": False,
            "security_fix_verified": False,
            "source_revisions_verified": False,
            "explanation_supported": False,
            "decision": "reject",
            "comments": "REVIEWER_COMMENTS_HERE",
        }
        with open(packets_dir / f"{case_id}_review_form_template.json", "w", encoding="utf-8") as form_f:
            json.dump(blank_form, form_f, indent=2, ensure_ascii=False)

        packets.append(packet)

    return packets


def run_automated_technical_triage(release_dir: Path):
    packets_dir = release_dir / "review_packets"
    reviews_dir = release_dir / "reviews"
    reviews_dir.mkdir(parents=True, exist_ok=True)

    packet_files = [
        pf for pf in sorted(packets_dir.glob("case_*.json"))
        if not pf.name.endswith("_review_form_template.json")
    ]
    triage_records = []

    for pf in packet_files:
        with open(pf, "r", encoding="utf-8") as f:
            pkt = json.load(f)

        case_id = pkt["case_id"]
        p_sha = pkt.get("payload_sha256")
        has_cand = pkt.get("has_candidate_payload", False)
        cand_payload = pkt.get("candidate_payload")

        # Distinguish verified actual candidate source from recorded donor commit reconnaissance signals (T3-04)
        is_recorded_parent = pkt.get("source_revisions", {}).get("is_direct_parent_edge", False)
        recorded_shared = pkt.get("changed_files", {}).get("shared_files", [])

        reasons = []
        if has_cand and cand_payload and isinstance(cand_payload, dict):
            src = cand_payload.get("source", {})
            req_src = ("repository", "path", "fix_commit", "parent_commit", "fix_diff", "before", "after")
            missing_src = [f for f in req_src if not src.get(f)]
            if missing_src:
                reasons.append(f"Candidate source payload missing verified fields: {sorted(missing_src)}")
            triage_status = "AUTOMATED_TRIAGE_REJECT" if reasons else "AUTOMATED_TRIAGE_PASS"
        else:
            if not is_recorded_parent:
                reasons.append("Commits do not form parent-child edge in git history")
            if not recorded_shared:
                reasons.append("Commits modify completely different files; no shared file")
            if not reasons:
                reasons.append("No verified candidate payload available")
            triage_status = "AUTOMATED_TRIAGE_REJECT"

        triage_records.append({
            "case_id": case_id,
            "payload_sha256": p_sha,
            "evaluation_type": "AUTOMATED_TECHNICAL_TRIAGE",
            "has_candidate_payload": has_cand,
            "is_direct_parent_edge": is_recorded_parent,
            "shared_files_count": len(recorded_shared),
            "status": triage_status,
            "technical_rejection_reasons": reasons,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        })

    with open(reviews_dir / "triage_ledger.jsonl", "w", encoding="utf-8") as f:
        for tr in triage_records:
            f.write(json.dumps(tr, ensure_ascii=False) + "\n")

    return triage_records


REQUIRED_REVIEW_FIELDS = {
    "case_id",
    "reviewer",
    "reviewed_at",
    "payload_sha256",
    "same_function_verified",
    "security_fix_verified",
    "source_revisions_verified",
    "explanation_supported",
    "decision",
    "comments",
}


def validate_review_form(rdata: dict, known_packets: dict, triage_records: dict, *, allow_synthetic: bool = False) -> tuple[bool, str | None]:
    """Validates a single human review form against packet payload, triage status, and review rules.

    Returns (is_valid: bool, rejection_reason: str or None)
    """
    if not isinstance(rdata, dict):
        return False, "REJECTED_NOT_A_DICT"

    missing = REQUIRED_REVIEW_FIELDS - set(rdata.keys())
    if missing:
        return False, f"REJECTED_MISSING_REQUIRED_FIELDS: {sorted(missing)}"

    case_id = rdata.get("case_id")
    if case_id not in known_packets:
        return False, f"REJECTED_UNKNOWN_CASE_ID: {case_id}"

    pkt = known_packets[case_id]
    expected_payload_sha = pkt.get("payload_sha256")
    if not expected_payload_sha or expected_payload_sha in ("INELIGIBLE_NO_CANDIDATE", "None", None):
        return False, f"REJECTED_NO_ADMISSIBLE_CANDIDATE: Case {case_id} has no valid candidate payload"

    # Reviewer identity verification (R4)
    reviewer = rdata.get("reviewer")
    if not isinstance(reviewer, str) or not reviewer.strip():
        return False, "REJECTED_INVALID_REVIEWER_NAME: empty name"
    reviewer = reviewer.strip()
    if reviewer in ("REVIEWER_NAME_HERE", "REVIEWER_NAME"):
        return False, f"REJECTED_INVALID_REVIEWER_NAME: placeholder {reviewer!r}"

    # Timestamp verification (R4): reject placeholder or malformed timestamps
    ts = rdata.get("reviewed_at")
    if not isinstance(ts, str) or not ts.strip():
        return False, "REJECTED_INVALID_TIMESTAMP: reviewed_at must be non-empty string"
    ts = ts.strip()
    # Check for placeholder template strings
    if any(placeholder in ts for placeholder in ("YYYY", "MM-DD", "HH:MM")):
        return False, f"REJECTED_PLACEHOLDER_TIMESTAMP: {ts!r}"
    if "TEST-FIXTURE" in ts:
        if not allow_synthetic:
            return False, f"REJECTED_SYNTHETIC_TIMESTAMP_IN_PRODUCTION: {ts!r} not permitted in production"
        # In explicit test mode with allow_synthetic=True, synthetic fixture timestamp marker is permitted
    else:
        try:
            ts_iso = ts.replace("Z", "+00:00")
            parsed_dt = datetime.fromisoformat(ts_iso)
            if parsed_dt.tzinfo is None:
                return False, f"REJECTED_TIMESTAMP_NO_TIMEZONE: {ts!r} requires UTC timezone"
            now_utc = datetime.now(timezone.utc)
            if parsed_dt > now_utc + timedelta(minutes=5):
                return False, f"REJECTED_FUTURE_TIMESTAMP: {ts!r} is in the future"
        except Exception as exc:
            return False, f"REJECTED_MALFORMED_TIMESTAMP: {ts!r} ({exc})"

    # Payload hash verification (R1)
    if rdata.get("payload_sha256") != expected_payload_sha:
        return False, f"REJECTED_PAYLOAD_HASH_MISMATCH: expected {expected_payload_sha}, got {rdata.get('payload_sha256')}"

    # Verification boolean checks
    for bfield in ("same_function_verified", "security_fix_verified", "source_revisions_verified", "explanation_supported"):
        if not isinstance(rdata.get(bfield), bool):
            return False, f"REJECTED_NON_BOOLEAN_FIELD: {bfield}={type(rdata.get(bfield))}"

    decision = rdata.get("decision")
    if decision not in ("approve", "reject"):
        return False, f"REJECTED_INVALID_DECISION: {decision!r}"

    if decision == "approve":
        unverified = [b for b in ("same_function_verified", "security_fix_verified", "source_revisions_verified", "explanation_supported") if rdata[b] is not True]
        if unverified:
            return False, f"REJECTED_APPROVE_WITHOUT_ALL_VERIFICATIONS: unverified {sorted(unverified)}"

        # Check triage status: machine git checks must have passed
        triage_info = triage_records.get(case_id, {})
        if triage_info.get("status") != "AUTOMATED_TRIAGE_PASS":
            return False, f"REJECTED_CANNOT_APPROVE_FAILED_TRIAGE: Case failed automated technical triage ({triage_info.get('status')})"

    return True, None


def _parse_iso_utc(ts_str: str | None) -> datetime:
    """Parse ISO timestamp and normalize to UTC timezone."""
    if not ts_str or not isinstance(ts_str, str):
        return datetime.min.replace(tzinfo=timezone.utc)
    try:
        ts_iso = ts_str.strip().replace("Z", "+00:00")
        dt = datetime.fromisoformat(ts_iso)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return datetime.min.replace(tzinfo=timezone.utc)


def resolve_review_consensus(case_id: str, reviews: list[dict]) -> tuple[str, list[dict], str]:
    """Unified consensus evaluator applying dual independent human review rules.

    Requirements:
    1. Normalizes reviewer names (whitespace and case-insensitive).
    2. Retains the latest review per reviewer (using parsed UTC timestamp).
    3. Detects timestamp tie conflicts (same reviewer, identical timestamp, different decision or payload).
    4. Strict consensus: If any reviewer rejects, candidate is blocked for disagreement.
    5. Disallows > 2 distinct reviewers without formal adjudication.
    6. Requires exactly 2 distinct approving reviews for admission.
    """
    latest_by_reviewer = {}
    conflicted_reviewers = set()

    for r in reviews:
        rev_name = r.get("reviewer", "")
        if not isinstance(rev_name, str) or not rev_name.strip():
            continue
        rev_key = " ".join(rev_name.strip().split()).casefold()
        if rev_key not in latest_by_reviewer:
            latest_by_reviewer[rev_key] = r
        else:
            existing_r = latest_by_reviewer[rev_key]
            t_new = _parse_iso_utc(r.get("reviewed_at"))
            t_old = _parse_iso_utc(existing_r.get("reviewed_at"))
            if t_new > t_old:
                latest_by_reviewer[rev_key] = r
            elif t_new == t_old:
                if (r.get("decision") != existing_r.get("decision") or
                        r.get("payload_sha256") != existing_r.get("payload_sha256")):
                    conflicted_reviewers.add(rev_key)

    if conflicted_reviewers:
        return "BLOCKED_SUPERSEDED_CONFLICT", [], f"Candidate {case_id} not admitted: conflicting reviews from reviewer with identical timestamps."

    active_reviews = list(latest_by_reviewer.values())

    if any(r.get("decision") != "approve" for r in active_reviews):
        return "BLOCKED_DISAGREEMENT", active_reviews, f"Candidate {case_id} not admitted: active disagreement or rejection present."

    if len(active_reviews) > 2:
        return "BLOCKED_MULTI_REVIEWER", active_reviews, f"Candidate {case_id} not admitted: unresolved multi-reviewer supersession ({len(active_reviews)} reviewers)."

    approvals = [r for r in active_reviews if r.get("decision") == "approve"]
    if len(approvals) < 2:
        return "PENDING_INSUFFICIENT_REVIEWS", approvals, f"Candidate {case_id} pending: {len(approvals)} approval(s), 2 required."

    return "ADMITTED", approvals[:2], f"Candidate {case_id} admitted with 2 independent approving reviews."


def determine_eligible_pairs(valid_reviews: list, known_packets: dict, triage_records: dict, candidates: list, banks: dict) -> dict:
    """Determines eligible pairs admitted by dual independent human review.

    Requirements for admission:
    1. Automated technical triage status == AUTOMATED_TRIAGE_PASS
    2. Exactly 2 distinct approving reviewers evaluated via resolve_review_consensus
    3. Candidate exists and passes validate_pair(pair, bank, dataset, require_reviews=True)
    """
    from collections import defaultdict
    reviews_by_case = defaultdict(list)
    for rev in valid_reviews:
        reviews_by_case[rev["case_id"]].append(rev)

    candidates_by_id = {c["pair_id"]: c for c in candidates}
    admitted = {"devign": [], "reveal": []}

    for case_id, revs in reviews_by_case.items():
        if triage_records.get(case_id, {}).get("status") != "AUTOMATED_TRIAGE_PASS":
            continue

        verdict, approvals, reason = resolve_review_consensus(case_id, revs)
        if verdict != "ADMITTED":
            print(f"Candidate {case_id} not admitted: {reason}")
            continue

        cand = candidates_by_id.get(case_id)
        if not cand:
            continue

        admitted_pair = json.loads(json.dumps(cand))
        admitted_pair["reviews"] = approvals[:2]

        ds = admitted_pair.get("dataset", "devign")
        bank = banks.get(ds, {})
        try:
            validate_pair(admitted_pair, bank, ds, require_reviews=True)
            admitted[ds].append(admitted_pair)
        except Exception as exc:
            print(f"Validation error for candidate {case_id}: {exc}")
            continue

    return admitted



def ingest_human_reviews_and_seal_pools(release_dir: Path, *, raise_on_error: bool = False):
    reviews_dir = release_dir / "reviews"
    pools_dir = release_dir / "pools"
    packets_dir = release_dir / "review_packets"
    candidates_dir = release_dir / "candidates"
    reviews_dir.mkdir(parents=True, exist_ok=True)
    pools_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load known packets
    known_packets = {}
    if packets_dir.is_dir():
        for pf in sorted(packets_dir.glob("case_*.json")):
            if not pf.name.endswith("_review_form_template.json"):
                with open(pf, "r", encoding="utf-8") as f:
                    pkt = json.load(f)
                    known_packets[pkt["case_id"]] = pkt

    # 2. Load triage records
    triage_records = {}
    triage_file = reviews_dir / "triage_ledger.jsonl"
    if triage_file.is_file():
        with open(triage_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    tr = json.loads(line)
                    triage_records[tr["case_id"]] = tr

    # 3. Load candidates if any
    candidates = []
    candidates_file = candidates_dir / "candidates.jsonl"
    if candidates_file.is_file():
        with open(candidates_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    candidates.append(json.loads(line))

    # 4. Ingest actual human reviews if submitted by reviewers in reviews/submitted/
    submitted_dir = reviews_dir / "submitted"
    submitted_dir.mkdir(exist_ok=True)

    submitted_reviews = []
    valid_reviews = []
    rejected_reviews = []

    if submitted_dir.is_dir():
        for rf in sorted(submitted_dir.glob("*.json")):
            try:
                with open(rf, "r", encoding="utf-8") as f:
                    rdata = json.load(f)
                    is_valid, reason = validate_review_form(rdata, known_packets, triage_records)
                    record_entry = {**rdata, "source_file": rf.name}
                    if is_valid:
                        record_entry["ingestion_status"] = "VALIDATED_HUMAN_REVIEW"
                        valid_reviews.append(record_entry)
                    else:
                        record_entry["ingestion_status"] = "REJECTED_REVIEW_FORM"
                        record_entry["rejection_reason"] = reason
                        rejected_reviews.append(record_entry)
                    submitted_reviews.append(record_entry)
            except Exception as exc:
                err_entry = {
                    "source_file": rf.name,
                    "case_id": "UNKNOWN_PARSE_ERROR",
                    "reviewer": "UNKNOWN",
                    "ingestion_status": "REJECTED_PARSE_ERROR",
                    "rejection_reason": str(exc),
                }
                rejected_reviews.append(err_entry)
                submitted_reviews.append(err_entry)

    # Save review ledger (reflects all submitted files, valid and invalid)
    with open(reviews_dir / "review_ledger.jsonl", "w", encoding="utf-8") as f:
        for rev in submitted_reviews:
            f.write(json.dumps(rev, ensure_ascii=False) + "\n")

    # 5. Load banks to validate any admitted pairs
    banks = {}
    freeze_dir = ROOT / "01_Author_Baseline_Unified" / "output" / "research_freeze_20261101"
    for ds in ("devign", "reveal"):
        raw_p = freeze_dir / ds / "train_raw.jsonl"
        manifest_p = freeze_dir / ds / "train_manifest.jsonl"
        if raw_p.is_file() and manifest_p.is_file():
            keep_ids = set()
            with open(manifest_p, "r", encoding="utf-8") as mf:
                for line in mf:
                    if line.strip():
                        m = json.loads(line)
                        if m.get("keep_in_bank"):
                            keep_ids.add(m["id"])
            bank = {}
            with open(raw_p, "r", encoding="utf-8") as rf:
                for line in rf:
                    if line.strip():
                        r = json.loads(line)
                        if r["id"] in keep_ids:
                            bank[r["id"]] = {**r, "function_uid": r["id"]}
            banks[ds] = bank

    # 6. Determine admitted pairs
    admitted = determine_eligible_pairs(valid_reviews, known_packets, triage_records, candidates, banks)
    admitted_devign = admitted.get("devign", [])
    admitted_reveal = admitted.get("reveal", [])

    # 7. Write pool files safely and handle disagreements (non-destructive preservation per R3, T3-02, R04)
    devign_pool_file = pools_dir / "eligible_pairs.devign.jsonl"
    reveal_pool_file = pools_dir / "eligible_pairs.reveal.jsonl"
    existing_manifest_file = pools_dir / "pool_manifest.json"

    # If submitted forms had validation/parse errors, do not overwrite existing valid pool or manifest (T3-02, R01)
    has_rejected_reviews = len(rejected_reviews) > 0
    if has_rejected_reviews:
        print(f"ERROR: {len(rejected_reviews)} invalid review form(s) encountered in submitted reviews:")
        for rj in rejected_reviews:
            print(f"  - File {rj.get('source_file')}: {rj.get('rejection_reason')}")
        if raise_on_error:
            raise ValueError(f"Submitted review forms failed validation ({len(rejected_reviews)} invalid forms). Ingestion aborted.")
        if existing_manifest_file.is_file() or devign_pool_file.is_file() or reveal_pool_file.is_file():
            print("Preserving existing pool files and pool manifest intact without publishing active release.")
            return False, {}
        return False, {}

    pool_stats = {}
    for ds, pool_file, admitted_ds in [
        ("devign", devign_pool_file, admitted_devign),
        ("reveal", reveal_pool_file, admitted_reveal),
    ]:
        existing_pairs = []
        if pool_file.is_file() and pool_file.stat().st_size > 0:
            try:
                lines = [line.strip() for line in pool_file.read_text(encoding="utf-8").splitlines() if line.strip()]
                existing_pairs = [json.loads(line) for line in lines]
            except Exception:
                existing_pairs = []

        # Check existing pairs against the current valid review ledger (T3-02, R02, R04)
        disputed_case = None
        for ep in existing_pairs:
            pid = ep.get("pair_id")
            case_revs = [r for r in valid_reviews if r.get("case_id") == pid]
            if case_revs:
                verdict, _, _ = resolve_review_consensus(pid, case_revs)
                if verdict != "ADMITTED":
                    disputed_case = pid
                    break
            else:
                verdict, _, _ = resolve_review_consensus(pid, ep.get("reviews", []))
                if verdict != "ADMITTED":
                    disputed_case = pid
                    break

        pool_by_id = {}
        retained = []
        added = []
        updated = []
        removed = []

        if disputed_case is not None:
            # Active disagreement / rejection on an existing pair blocks the pool! (T3-02)
            cur_status = "BLOCKED_DISAGREEMENT"
            cur_reason = f"Candidate {disputed_case} has active disagreement or rejection in current review ledger; pool activation blocked."
            admitted_count = 0
            removed.append({"pair_id": disputed_case, "reason": cur_reason})
            # History is preserved, but pool is blocked from execution
        elif admitted_ds or existing_pairs:
            # First, evaluate existing pairs
            for ep in existing_pairs:
                pid = ep.get("pair_id")
                new_matching = [p for p in admitted_ds if p.get("pair_id") == pid]
                if new_matching:
                    pool_by_id[pid] = new_matching[0]
                    updated.append({"pair_id": pid, "reason": "Updated reviews from active review ledger"})
                else:
                    try:
                        bank = banks.get(ds, {})
                        validate_pair(ep, bank, ds, require_reviews=True)
                        pool_by_id[pid] = ep
                        retained.append({"pair_id": pid, "reason": "Existing verified pair retained intact"})
                    except Exception as exc:
                        removed.append({"pair_id": pid, "reason": f"Corrupt or invalid pair in existing pool: {exc}"})

            # Next, add newly admitted pairs that are not already present (R04: no silent dropping)
            for np in admitted_ds:
                pid = np.get("pair_id")
                if pid not in pool_by_id:
                    pool_by_id[pid] = np
                    added.append({"pair_id": pid, "reason": "Newly admitted pair via dual independent human review"})

            proposed_pool = list(pool_by_id.values())
            if proposed_pool:
                with open(pool_file, "w", encoding="utf-8") as f:
                    for p in proposed_pool:
                        f.write(json.dumps(p, ensure_ascii=False) + "\n")
                cur_status = "ACTIVE_VERIFIED_POOL"
                cur_reason = f"{len(proposed_pool)} pairs verified active (retained={len(retained)}, added={len(added)}, updated={len(updated)})."
                admitted_count = len(proposed_pool)
            else:
                pool_file.write_text("", encoding="utf-8")
                cur_status = "BLOCKED_EMPTY_POOL"
                admitted_count = 0
                cur_reason = f"Zero valid pairs retained or admitted for {ds}."
        else:
            pool_file.write_text("", encoding="utf-8")
            cur_status = "BLOCKED_EMPTY_POOL"
            admitted_count = 0
            if ds == "devign":
                cur_reason = "Zero pairs admitted: all investigated cases rejected by automated technical triage or lack of consensus."
            else:
                cur_reason = "All 17,636 donors missing upstream commit revisions in frozen export."

        actual_lines_in_file = len([line for line in pool_file.read_text(encoding="utf-8").splitlines() if line.strip()]) if pool_file.is_file() else 0
        pool_stats[ds] = {
            "status": cur_status,
            "reason": cur_reason,
            "admitted_count": admitted_count,
            "pairs_in_file": actual_lines_in_file,
        }

        # Save membership diff
        diff_record = {
            "dataset": ds,
            "initial_count": len(existing_pairs),
            "proposed_count": admitted_count,
            "retained_count": len(retained),
            "added_count": len(added),
            "updated_count": len(updated),
            "removed_count": len(removed),
            "retained": retained,
            "added": added,
            "updated": updated,
            "removed": removed,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        }
        with open(pools_dir / f"membership_diff_{ds}.json", "w", encoding="utf-8") as f:
            json.dump(diff_record, f, indent=2, ensure_ascii=False)

    devign_status = pool_stats["devign"]["status"]
    devign_reason = pool_stats["devign"]["reason"]
    reveal_status = pool_stats["reveal"]["status"]
    reveal_reason = pool_stats["reveal"]["reason"]

    devign_pool_sha = compute_file_sha256(devign_pool_file) if devign_pool_file.is_file() else ""
    reveal_pool_sha = compute_file_sha256(reveal_pool_file) if reveal_pool_file.is_file() else ""

    # 8. Record triage and review status report (honest, no fabricated quotes or signatures)
    triage_rejects = [tr for tr in triage_records.values() if tr.get("status") == "AUTOMATED_TRIAGE_REJECT"]
    triage_passes = [tr for tr in triage_records.values() if tr.get("status") == "AUTOMATED_TRIAGE_PASS"]
    total_evaluated = len(known_packets)
    triage_reject_pct = (len(triage_rejects) / total_evaluated * 100) if total_evaluated > 0 else 0.0

    if total_evaluated == 0:
        triage_summary_md = "- Chưa có ứng viên nào được đánh giá triage."
    elif len(triage_passes) == 0:
        triage_summary_md = f"""- Kết quả kiểm tra git upstream tự động cho {total_evaluated} cặp ứng viên:
  * 100% ({len(triage_rejects)}/{total_evaluated} ca) bị loại ở bước sàng lọc kỹ thuật (`AUTOMATED_TRIAGE_REJECT`).
  * Lý do: Các commit không phải là quan hệ cha-con trong lịch sử git và/hoặc sửa ở các file mã nguồn hoàn toàn khác nhau.
  * Không có bất kỳ cặp nào thỏa mãn điều kiện là bản vá lỗi của cùng một hàm mã nguồn."""
    else:
        triage_summary_md = f"""- Kết quả kiểm tra git upstream tự động cho {total_evaluated} cặp ứng viên:
  * {len(triage_passes)} ca vượt qua sàng lọc kỹ thuật (`AUTOMATED_TRIAGE_PASS`).
  * {len(triage_rejects)} ca ({triage_reject_pct:.1f}%) bị loại ở bước sàng lọc kỹ thuật (`AUTOMATED_TRIAGE_REJECT`)."""

    status_report_md = f"""# BÁO CÁO KẾT QUẢ TRIAGE KỸ THUẬT VÀ TÌNH TRẠNG THẨM ĐỊNH B3

**Ngày lập:** {datetime.now().strftime('%d/%m/%Y')}  
**Giao thức áp dụng:** `docs/B3_NEW_ALGORITHM_EXECUTION_PLAN_20261108.md` (Bước 6)  
**Phân loại:** Automated Technical Triage & Independent Human Review Ingestion  

---

## 1. Kết quả Sàng lọc Kỹ thuật Tự động (Automated Technical Triage)
- Đã lập hồ sơ {len(known_packets)} review packets hoàn chỉnh với mã băm niêm phong `payload_sha256` tại `review_packets/`.
{triage_summary_md}

## 2. Tình trạng Thẩm định Độc lập của Con người (Human Review Status)
- Số lượng phiếu duyệt của con người được nộp: **{len(submitted_reviews)} phiếu** ({len(valid_reviews)} hợp lệ, {len(rejected_reviews)} bị từ chối).
- Số lượng cặp đạt đồng thuận phê duyệt độc lập (dual review approval): **{len(admitted_devign) + len(admitted_reveal)} ca**.
- **Không tự sinh chữ ký hay nhận xét giả lập của con người** (tuân thủ nghiêm ngặt chuẩn mực liêm chính khoa học và kết luận kiểm toán độc lập F01).

## 3. Niêm phong Eligible Pair Pool
- Pool Devign (`eligible_pairs.devign.jsonl`): **{pool_stats['devign']['admitted_count']} pairs** ({devign_status}).
- Pool REVEAL (`eligible_pairs.reveal.jsonl`): **{pool_stats['reveal']['admitted_count']} pairs** ({reveal_status}).
- Thuật toán `VerifiedPairSelector` dừng có kiểm soát (`PAUSED`) khi pool rỗng hoặc bị chặn.
"""
    with open(reviews_dir / "TRIAGE_AND_REVIEW_STATUS.md", "w", encoding="utf-8") as sf:
        sf.write(status_report_md)

    now_utc = datetime.now(timezone.utc).isoformat()

    # 9. Create pool manifest with seal
    gov_scope = release_dir / "governance" / "scope_decision.json"
    gov_meta = {}
    if gov_scope.is_file():
        try:
            gov_meta = json.loads(gov_scope.read_text(encoding="utf-8"))
        except Exception:
            gov_meta = {}

    im_path = release_dir / "inputs_manifest.json"
    im_meta = {}
    if im_path.is_file():
        try:
            im_meta = json.loads(im_path.read_text(encoding="utf-8"))
        except Exception:
            im_meta = {}

    is_v5 = "v5" in release_dir.name
    rel_ver = gov_meta.get("release_version") or im_meta.get("release_version") or ("v5_devign_validation_locked" if is_v5 else "v3_remediated")
    parent_rel = gov_meta.get("parent_release") or im_meta.get("parent_release") or ("release_20261108_v4" if is_v5 else "v2_remediated")
    method_id = gov_meta.get("method_id") or im_meta.get("method_id", "b3-verified-patch-v1")
    rel_id = gov_meta.get("release_id") or im_meta.get("release_id", release_dir.name)
    schema_ver = gov_meta.get("schema_version") or im_meta.get("schema_version", 1)
    rel_status = gov_meta.get("release_status") or im_meta.get("release_status", "FROZEN")

    pool_manifest = {
        "schema_version": schema_ver,
        "release_id": rel_id,
        "release_version": rel_ver,
        "parent_release": parent_rel,
        "release_status": rel_status,
        "method_id": method_id,
        "created_at_utc": now_utc,
        "governance": f"amended_{method_id}",
        "scope": gov_meta.get("scope") or im_meta.get("scope", {
            "dataset": "devign",
            "split": "validation",
            "arm": "B3",
            "prompt_seed": 42,
            "expected_count": 2732
        }),
        "excluded_from_execution": gov_meta.get("excluded_from_execution") or im_meta.get("excluded_from_execution", {
            "reveal": "BLOCKED_UNRESOLVED_PROVENANCE"
        }),
        "review_process": {
            "triage_type": "AUTOMATED_TECHNICAL_TRIAGE",
            "triage_result": f"{len(triage_records)}_cases_evaluated_by_technical_triage",
            "human_reviews_submitted": len(submitted_reviews),
            "human_reviews_validated": len(valid_reviews),
            "human_reviews_rejected": len(rejected_reviews),
            "human_reviews_admitted": len(valid_reviews),
            "fabrication_disclaimer": "No autogenerated human review opinions or signatures used."
        },
        "pools": {
            "devign": {
                "dataset": "devign",
                "clean_train_donors": 21691,
                "candidate_combinations": 26700,
                "investigated_cases_count": len(known_packets),
                "pairs_in_pool_file": pool_stats["devign"]["pairs_in_file"],
                "admitted_pairs_count": pool_stats["devign"]["admitted_count"],
                "newly_admitted_count": len(admitted_devign),
                "pool_file": devign_pool_file.relative_to(release_dir).as_posix(),
                "pool_sha256": devign_pool_sha,
                "status": devign_status,
                "blocker_reason": (devign_reason if devign_status != "ACTIVE_VERIFIED_POOL" else None),
            },
            "reveal": {
                "dataset": "reveal",
                "clean_train_donors": 17636,
                "candidate_combinations": 33947,
                "pairs_in_pool_file": pool_stats["reveal"]["pairs_in_file"],
                "admitted_pairs_count": pool_stats["reveal"]["admitted_count"],
                "newly_admitted_count": len(admitted_reveal),
                "pool_file": reveal_pool_file.relative_to(release_dir).as_posix(),
                "pool_sha256": reveal_pool_sha,
                "status": reveal_status,
                "blocker_reason": (reveal_reason if reveal_status != "ACTIVE_VERIFIED_POOL" else None),
            },
        },
        "synthetic_fixtures_permitted": False,
        "synthetic_fixtures_count": 0,
        "timestamp_utc": now_utc,
    }

    manifest_bytes = json.dumps(pool_manifest, sort_keys=True, ensure_ascii=False, indent=2).encode("utf-8")
    manifest_seal = compute_bytes_sha256(manifest_bytes)
    pool_manifest["manifest_seal_sha256"] = manifest_seal

    with open(pools_dir / "pool_manifest.json", "w", encoding="utf-8") as f:
        json.dump(pool_manifest, f, indent=2, ensure_ascii=False)

    print(f"Step 6 Complete! Eligible pool manifest sealed: {manifest_seal}")
    print(f"Devign Pool: {devign_pool_file} ({len(admitted_devign)} pairs)")
    print(f"REVEAL Pool: {reveal_pool_file} ({len(admitted_reveal)} pairs)")
    print("Automated Triage Ledger and Status Report recorded without autogenerated human review.")


def run_step6(release_dir: Path = DEFAULT_RELEASE_DIR):
    print(f"=== Step 6: Review Packets, Technical Triage, and Pool Seal (Target: {release_dir.name}) ===")
    packets = generate_review_packets(release_dir)
    print(f"Generated {len(packets)} review packets.")
    triage = run_automated_technical_triage(release_dir)
    print(f"Recorded automated technical triage for {len(triage)} cases.")
    ingest_human_reviews_and_seal_pools(release_dir, raise_on_error=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Step 6: Review packets and pool seal")
    parser.add_argument("--release-dir", type=Path, default=DEFAULT_RELEASE_DIR, help="Output release directory")
    args = parser.parse_args()
    run_step6(args.release_dir)
