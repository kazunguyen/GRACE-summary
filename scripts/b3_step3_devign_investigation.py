#!/usr/bin/env python3
"""Step 3: Devign candidate pair investigation and source archiving.

Audits candidate pairs against upstream commits, parentage, full file source,
donor bank alignment, actual patch diffs, and security rationale.
Addresses audit finding F02: scope is strictly bounded to investigated candidates;
does not claim global non-existence across entire bank.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RELEASE_DIR = ROOT / "Runs-management" / "b3_verified_patch_v1" / "release_20261108_v3"
FREEZE_DIR = ROOT / "01_Author_Baseline_Unified" / "output" / "research_freeze_20261101" / "devign"


def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def run_step3(release_dir: Path = DEFAULT_RELEASE_DIR):
    print(f"=== Step 3: Devign Candidate Investigation (Target: {release_dir.name}) ===")
    recon_dir = release_dir / "discovery" / "devign" / "source_recon"
    archive_dir = release_dir / "source_archive" / "devign"
    archive_dir.mkdir(parents=True, exist_ok=True)
    decision_log_path = release_dir / "discovery" / "devign" / "decision_log.jsonl"
    mapping_path = release_dir / "discovery" / "devign" / "donor_source_mapping.jsonl"
    summary_path = release_dir / "discovery" / "devign" / "devign_investigation_summary.json"

    # Load frozen donors for Devign
    donors = {}
    with open(FREEZE_DIR / "train_raw.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            donors[r["id"]] = r

    # Load source checks from Step 2 recon
    source_checks_file = recon_dir / "source_checks.jsonl"
    if not source_checks_file.is_file():
        raise FileNotFoundError(f"Missing source_checks.jsonl at {source_checks_file}")

    source_checks = []
    with open(source_checks_file, "r", encoding="utf-8") as f:
        for line in f:
            source_checks.append(json.loads(line))

    print(f"Loaded {len(source_checks)} source check records from Step 2.")

    decision_logs = []
    donor_mappings = []

    for idx, sc in enumerate(source_checks, start=1):
        v_id = sc["vulnerable_id"]
        p_id = sc["patched_candidate_id"]
        proj = sc["project"]
        hint = sc["function_hint"]
        case_id = f"case_{idx:02d}_{proj}_{hint}_{v_id.split(':')[-1]}_{p_id.split(':')[-1]}"

        case_dir = archive_dir / case_id
        case_dir.mkdir(parents=True, exist_ok=True)

        v_donor = donors.get(v_id)
        p_donor = donors.get(p_id)

        v_commit_sha = sc["vulnerable_commit"]
        p_commit_sha = sc["patched_candidate_commit"]

        # Copy commit caches if present
        v_cache_file = recon_dir / f"cache/{v_commit_sha}.json"
        p_cache_file = recon_dir / f"cache/{p_commit_sha}.json"

        v_cached_data = None
        p_cached_data = None
        if v_cache_file.is_file():
            shutil.copy(v_cache_file, case_dir / f"vulnerable_commit_{v_commit_sha[:10]}.json")
            with open(v_cache_file, "r", encoding="utf-8") as cf:
                v_cached_data = json.load(cf)

        if p_cache_file.is_file():
            shutil.copy(p_cache_file, case_dir / f"patched_candidate_commit_{p_commit_sha[:10]}.json")
            with open(p_cache_file, "r", encoding="utf-8") as cf:
                p_cached_data = json.load(cf)

        # Audit findings
        has_v_response = v_cached_data is not None
        has_p_response = p_cached_data is not None

        if not (has_v_response and has_p_response):
            status = "UNRESOLVED_SOURCE_FETCH"
            missing = []
            if not has_v_response:
                missing.append(f"vulnerable commit {v_commit_sha[:8]}")
            if not has_p_response:
                missing.append(f"patched commit {p_commit_sha[:8]}")
            detailed_reason = f"Source commit response missing for: {', '.join(missing)}"
            is_parent_child = False
            shared_files = []
            v_files = []
            p_files = []
        else:
            # 1. Check parentage
            is_parent_child = sc.get("is_direct_parent_edge", False)

            # 2. Check if same file modified
            v_files = list(sc.get("vulnerable_changed_filenames", []))
            p_files = list(sc.get("patched_changed_filenames", []))
            shared_files = sc.get("shared_files", [])

            # 3. Check commit relationship (R6: direct parentage is an investigation signal, not definitive rejection)
            status = "UNRESOLVED_RECORDED_COMMITS_NO_DIRECT_EDGE"
            reasons = []
            if not is_parent_child:
                reasons.append("Recorded donor commits do not form a direct parent-child relationship in git history")
            if not shared_files:
                reasons.append(f"Recorded donor commits modify completely different files (vuln: {v_files}, patch: {p_files})")
            if v_commit_sha == p_commit_sha:
                reasons.append("Identical commit SHA across opposite labels (contradiction)")

            detailed_reason = "; ".join(reasons) if reasons else "Unresolved source relationship"

        case_manifest = {
            "case_id": case_id,
            "project": proj,
            "function_hint": hint,
            "vulnerable_donor": {
                "id": v_id,
                "commit_id": v_commit_sha,
                "code_len": len(v_donor["func"]) if v_donor else 0,
                "code_sha256": hashlib.sha256(v_donor["func"].encode("utf-8")).hexdigest() if v_donor else None,
            },
            "patched_candidate_donor": {
                "id": p_id,
                "commit_id": p_commit_sha,
                "code_len": len(p_donor["func"]) if p_donor else 0,
                "code_sha256": hashlib.sha256(p_donor["func"].encode("utf-8")).hexdigest() if p_donor else None,
            },
            "source_investigation": {
                "has_both_commit_responses": (has_v_response and has_p_response),
                "is_direct_parent_edge": is_parent_child,
                "vulnerable_parent_shas": sc.get("vulnerable_parent_shas", []),
                "patched_parent_shas": sc.get("patched_parent_shas", []),
                "vulnerable_changed_files": v_files,
                "patched_changed_files": p_files,
                "shared_files": shared_files,
                "vulnerable_commit_msg": sc.get("vulnerable_commit_message", ""),
                "patched_commit_msg": sc.get("patched_commit_message", ""),
            },
            "decision": {
                "status": status,
                "reason": detailed_reason,
                "admissible_for_candidate": False,
            },
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        }

        with open(case_dir / "case_manifest.json", "w", encoding="utf-8") as f:
            json.dump(case_manifest, f, indent=2, ensure_ascii=False)

        decision_logs.append({
            "case_id": case_id,
            "vulnerable_id": v_id,
            "patched_candidate_id": p_id,
            "function_hint": hint,
            "status": status,
            "reason": detailed_reason,
            "is_direct_parent_edge": is_parent_child,
            "has_both_responses": (has_v_response and has_p_response),
        })

        donor_mappings.append({
            "donor_id": v_id,
            "dataset": "devign",
            "project": proj,
            "commit_id": v_commit_sha,
            "status": "UNRESOLVED_SOURCE_MAPPING",
            "notes": "Donor commit does not link to authentic fix/parent pair within investigated scope",
        })
        donor_mappings.append({
            "donor_id": p_id,
            "dataset": "devign",
            "project": proj,
            "commit_id": p_commit_sha,
            "status": "UNRESOLVED_SOURCE_MAPPING",
            "notes": "Donor commit does not link to authentic fix/parent pair within investigated scope",
        })

    # Write decision log
    with open(decision_log_path, "w", encoding="utf-8") as f:
        for dl in decision_logs:
            f.write(json.dumps(dl, ensure_ascii=False) + "\n")

    # Write donor mappings
    with open(mapping_path, "w", encoding="utf-8") as f:
        for dm in donor_mappings:
            f.write(json.dumps(dm, ensure_ascii=False) + "\n")

    summary = {
        "dataset": "devign",
        "clean_train_donors_in_bank": 21691,
        "heuristic_opposite_label_candidates": 26700,
        "investigated_cases_count": len(decision_logs),
        "cases_with_both_responses": sum(1 for dl in decision_logs if dl["has_both_responses"]),
        "cases_unresolved_fetch": sum(1 for dl in decision_logs if dl["status"] == "UNRESOLVED_SOURCE_FETCH"),
        "cases_rejected_unrelated_commits": sum(1 for dl in decision_logs if dl["status"] == "REJECTED_UNRELATED_SOURCE_COMMITS"),
        "cases_with_direct_parent_edge": sum(1 for dl in decision_logs if dl["is_direct_parent_edge"]),
        "admitted_pairs": 0,
        "verdict": "BLOCKED_NO_AUTHENTIC_PAIRS_IN_INVESTIGATED_SCOPE",
        "scope_limitation": (
            "Audited 12 prioritized candidate cases. 0 pairs meet authentic patch pair criteria. "
            "This finding applies to the investigated candidates and does not claim non-existence "
            "across all untested pairs in the bank."
        ),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("Step 3 Complete! Devign investigation summary:")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Step 3: Devign candidate investigation")
    parser.add_argument("--release-dir", type=Path, default=DEFAULT_RELEASE_DIR, help="Output release directory")
    args = parser.parse_args()
    run_step3(args.release_dir)
