#!/usr/bin/env python3
"""Step 5: Create candidate records according to schema and run local validation.

Audits investigated candidate cases against amended_b3 schema requirements.
Addresses audit finding F04: completely removes dummy/fabricated fix diffs from
the real-data pipeline. Candidates are only constructed when authentic upstream
source evidence (real repo, real path, real fix diff, identical before/after) exists.
"""

import argparse
from datetime import datetime, timezone
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

from grace_diag.amended_b3 import (
    digest,
    function_hint,
    make_pair_candidate,
    payload_hash,
    validate_pair,
)

FREEZE_DIR = ROOT / "01_Author_Baseline_Unified" / "output" / "research_freeze_20261101"


def run_step5(release_dir: Path = DEFAULT_RELEASE_DIR):
    print(f"=== Step 5: Candidate Schema Generation and Real Source Audit (Target: {release_dir.name}) ===")
    candidates_dir = release_dir / "candidates"
    candidates_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load clean donor bank
    banks = {}
    for ds in ["devign", "reveal"]:
        manifest_p = FREEZE_DIR / ds / "train_manifest.jsonl"
        raw_p = FREEZE_DIR / ds / "train_raw.jsonl"
        keep_ids = set()
        with open(manifest_p, "r", encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                if r["keep_in_bank"]:
                    keep_ids.add(r["id"])
        bank = {}
        with open(raw_p, "r", encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                if r["id"] in keep_ids:
                    bank[r["id"]] = {**r, "function_uid": r["id"]}
        banks[ds] = bank
        print(f"Loaded {len(bank)} clean donors for {ds}.")

    # 2. Inspect case manifests from Step 3
    archive_dir = release_dir / "source_archive" / "devign"
    case_manifests = []
    if archive_dir.is_dir():
        for case_folder in sorted(archive_dir.glob("case_*")):
            mfile = case_folder / "case_manifest.json"
            if mfile.is_file():
                with open(mfile, "r", encoding="utf-8") as f:
                    case_manifests.append(json.load(f))

    print(f"Loaded {len(case_manifests)} case manifests from Step 3.")

    candidates = []
    ineligibility_records = []

    for cm in case_manifests:
        case_id = cm["case_id"]
        proj = cm["project"]
        hint = cm["function_hint"]
        v_id = cm["vulnerable_donor"]["id"]
        p_id = cm["patched_candidate_donor"]["id"]
        v_commit = cm["vulnerable_donor"]["commit_id"]
        p_commit = cm["patched_candidate_donor"]["commit_id"]
        sinv = cm["source_investigation"]
        decision = cm.get("decision", {})

        v_donor = banks["devign"].get(v_id)
        p_donor = banks["devign"].get(p_id)

        if not v_donor or not p_donor:
            ineligibility_records.append({
                "case_id": case_id,
                "ineligible_reason": f"Donor missing from clean bank: v={v_id in banks['devign']}, p={p_id in banks['devign']}",
                "admissible_for_candidate": False,
            })
            continue

        # Real Source Requirement Check (No Dummy Diffs!)
        # Check evidence sidecar first (authentic upstream fix + parentage)
        evidence_file = archive_dir / case_id / "evidence_sidecar.json"
        actual_diff_file = archive_dir / case_id / "actual_fix.diff"
        has_evidence_sidecar = evidence_file.is_file() and actual_diff_file.is_file()

        if has_evidence_sidecar:
            try:
                ev = json.loads(evidence_file.read_text(encoding="utf-8"))
                actual_diff_text = actual_diff_file.read_text(encoding="utf-8")

                # Strictly require before and after functions in sidecar (T3-03)
                if "before" not in ev or not isinstance(ev["before"], str) or not ev["before"].strip():
                    raise ValueError("Evidence sidecar missing required 'before' function source; fallback to donor code forbidden (T3-03)")
                if "after" not in ev or not isinstance(ev["after"], str) or not ev["after"].strip():
                    raise ValueError("Evidence sidecar missing required 'after' function source; fallback to donor code forbidden (T3-03)")
                for req_meta in ("repository", "path", "fix_commit", "parent_commit", "security_rationale"):
                    if req_meta not in ev or not ev[req_meta]:
                        raise ValueError(f"Evidence sidecar missing required metadata field: {req_meta}")
                if not actual_diff_text.strip():
                    raise ValueError("Actual fix diff file is empty; authentic patch diff required")

                sidecar_before = ev["before"]
                sidecar_after = ev["after"]

                # Verify archived functions match donor bank functions (R6)
                v_code = v_donor["func"]
                p_code = p_donor["func"]

                if digest(sidecar_before.strip()) != digest(v_code.strip()):
                    raise ValueError("Sidecar before function does not match clean donor function byte-for-byte")
                if digest(sidecar_after.strip()) != digest(p_code.strip()):
                    raise ValueError("Sidecar after function does not match clean donor function byte-for-byte")

                source = {
                    "repository": ev["repository"],
                    "path": ev["path"],
                    "function": ev.get("function", hint),
                    "fix_commit": ev["fix_commit"],
                    "parent_commit": ev["parent_commit"],
                    "source_url": ev.get("source_url", f"https://github.com/{ev['repository']}/commit/{ev['fix_commit']}"),
                    "security_rationale": ev["security_rationale"],
                    "before": sidecar_before,
                    "after": sidecar_after,
                    "fix_diff": actual_diff_text,
                }
                cand = make_pair_candidate("devign", case_id, v_donor, p_donor, source)
                validate_pair(cand, banks["devign"], "devign", require_reviews=False)
                candidates.append(cand)
                # Archive candidate JSON in case folder for Step 6 packet binding
                with open(archive_dir / case_id / "candidate.json", "w", encoding="utf-8") as cf:
                    json.dump(cand, cf, indent=2, ensure_ascii=False)
            except Exception as exc:
                ineligibility_records.append({
                    "case_id": case_id,
                    "vulnerable_id": v_id,
                    "patched_id": p_id,
                    "function_hint": hint,
                    "ineligible_reason": f"CANDIDATE_VALIDATION_ERROR: {exc}",
                    "admissible_for_candidate": False,
                })
            continue

        # If no verified sidecar exists, evaluate recorded donor commits as investigation signals (R6)
        has_both_responses = sinv.get("has_both_commit_responses", False)
        is_direct_parent = sinv.get("is_direct_parent_edge", False)
        shared_files = sinv.get("shared_files", [])

        if not has_both_responses:
            ineligibility_records.append({
                "case_id": case_id,
                "vulnerable_id": v_id,
                "patched_id": p_id,
                "function_hint": hint,
                "ineligible_reason": "UNRESOLVED_SOURCE_FETCH: Missing upstream commit response from reconnaissance.",
                "admissible_for_candidate": False,
            })
            continue

        if not is_direct_parent or not shared_files:
            reasons = []
            if not is_direct_parent:
                reasons.append("Commits do not form direct parent-child edge in git history")
            if not shared_files:
                reasons.append("Commits modify completely different files; no shared file")
            ineligibility_records.append({
                "case_id": case_id,
                "vulnerable_id": v_id,
                "patched_id": p_id,
                "function_hint": hint,
                "ineligible_reason": "UNRESOLVED_SOURCE_PARENTAGE: " + "; ".join(reasons),
                "admissible_for_candidate": False,
            })
            continue

        reasons = []
        if not is_direct_parent:
            reasons.append("recorded commits lack direct parent edge")
        if not shared_files:
            reasons.append("recorded commits modify different files")
        signal_msg = "; ".join(reasons) if reasons else "recorded commits have direct edge but no verified sidecar"
        ineligibility_records.append({
            "case_id": case_id,
            "vulnerable_id": v_id,
            "patched_id": p_id,
            "function_hint": hint,
            "ineligible_reason": f"UNRESOLVED_NO_EVIDENCE_SIDECAR: {signal_msg}. Requires verified upstream evidence sidecar with authentic repository, path, revisions, fix diff, and security rationale.",
            "admissible_for_candidate": False,
        })

    # Save candidates (0 if none met real source requirements)
    with open(candidates_dir / "candidates.jsonl", "w", encoding="utf-8") as f:
        for c in candidates:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    # Save ineligibility records
    with open(candidates_dir / "candidate_ineligibility_records.jsonl", "w", encoding="utf-8") as f:
        for ir in ineligibility_records:
            f.write(json.dumps(ir, ensure_ascii=False) + "\n")

    summary = {
        "cases_audited": len(case_manifests),
        "candidates_admitted": len(candidates),
        "ineligible_cases_count": len(ineligibility_records),
        "dummy_fixtures_used": False,
        "methodology_note": (
            "Per audit finding F04, no dummy diffs or synthetic fixtures are used in the real-data pipeline. "
            "Cases failing parentage or file sharing are stopped at investigation and recorded as ineligible. "
            "make_pair_candidate is only called when authentic source diffs exist."
        ),
        "status": "STEP5_CANDIDATE_AUDIT_COMPLETED",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }

    with open(candidates_dir / "candidates_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("Step 5 Complete! Summary:")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Step 5: Candidate schema generation and audit")
    parser.add_argument("--release-dir", type=Path, default=DEFAULT_RELEASE_DIR, help="Output release directory")
    args = parser.parse_args()
    run_step5(args.release_dir)
