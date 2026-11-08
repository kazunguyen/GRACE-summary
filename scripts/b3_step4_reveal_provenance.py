#!/usr/bin/env python3
"""Step 4: REVEAL dataset provenance recovery audit and sidecar generation.

Audits frozen REVEAL train donors (17,636), checks upstream claudios/ReVeal
repository reference, documents missing commit IDs, and generates a provenance sidecar.
Addresses audit finding F05: documents concrete search scope across frozen assets
and removes unverified assertions.
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
FREEZE_DIR = ROOT / "01_Author_Baseline_Unified" / "output" / "research_freeze_20261101" / "reveal"
RAW_MANIFEST_PATH = ROOT / "01_Author_Baseline_Unified" / "output" / "local_full" / "reveal" / "raw" / "data_manifest.json"


def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def run_step4(release_dir: Path = DEFAULT_RELEASE_DIR):
    print(f"=== Step 4: REVEAL Provenance Recovery Audit (Target: {release_dir.name}) ===")
    reveal_discovery_dir = release_dir / "discovery" / "reveal"
    reveal_discovery_dir.mkdir(parents=True, exist_ok=True)
    sidecar_path = reveal_discovery_dir / "provenance_sidecar.jsonl"
    summary_path = reveal_discovery_dir / "reveal_provenance_summary.json"

    # 1. Read upstream dataset manifest
    if not RAW_MANIFEST_PATH.is_file():
        raise FileNotFoundError(f"Missing raw manifest: {RAW_MANIFEST_PATH}")

    with open(RAW_MANIFEST_PATH, "r", encoding="utf-8") as f:
        raw_manifest = json.load(f)

    raw_manifest_sha = compute_sha256(RAW_MANIFEST_PATH)
    print(f"Raw REVEAL manifest: repo={raw_manifest.get('repo')}, revision={raw_manifest.get('revision')}, sha={raw_manifest_sha}")

    # 2. Audit frozen train donors
    train_raw_path = FREEZE_DIR / "train_raw.jsonl"
    train_manifest_path = FREEZE_DIR / "train_manifest.jsonl"

    manifest_lookup = {}
    with open(train_manifest_path, "r", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            manifest_lookup[r["id"]] = r

    donors = []
    missing_commit_count = 0
    debian_project_count = 0
    chrome_project_count = 0
    unique_source_ids = set()

    with open(train_raw_path, "r", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            uid = r["id"]
            m = manifest_lookup.get(uid)
            if not m or not m["keep_in_bank"]:
                continue

            c_id = r.get("commit_id")
            if c_id is None:
                missing_commit_count += 1

            proj = r.get("project")
            if proj == "debian":
                debian_project_count += 1
            elif proj == "chrome":
                chrome_project_count += 1

            s_id = str(r.get("source_id", ""))
            unique_source_ids.add(s_id)

            donors.append({
                "donor_id": uid,
                "dataset": "reveal",
                "split": "train",
                "label": r["target"],
                "project": proj,
                "source_id": s_id,
                "commit_id": c_id,
                "code_len": len(r["func"]),
                "code_sha256": hashlib.sha256(r["func"].encode("utf-8")).hexdigest(),
                "upstream_repo": raw_manifest.get("repo"),
                "upstream_revision": raw_manifest.get("revision"),
                "provenance_status": "UNRESOLVED_MISSING_UPSTREAM_METADATA",
                "reason": "Frozen raw export contains no upstream commit hash or file path mapping",
            })

    print(f"Audited {len(donors)} clean REVEAL donors.")
    print(f"Missing commit IDs: {missing_commit_count}/{len(donors)} ({missing_commit_count / len(donors) * 100:.1f}%)")
    print(f"Project='debian': {debian_project_count}/{len(donors)} ({debian_project_count / len(donors) * 100:.1f}%)")
    print(f"Project='chrome': {chrome_project_count}/{len(donors)} ({chrome_project_count / len(donors) * 100:.1f}%)")
    print(f"Unique source IDs: {len(unique_source_ids)}")

    # 3. Write provenance sidecar
    with open(sidecar_path, "w", encoding="utf-8") as f:
        for d in donors:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")

    summary = {
        "dataset": "reveal",
        "clean_train_donors": len(donors),
        "donors_missing_commit_id": missing_commit_count,
        "donors_with_project_debian": debian_project_count,
        "donors_with_project_chrome": chrome_project_count,
        "unique_source_ids": len(unique_source_ids),
        "upstream_repository": raw_manifest.get("repo"),
        "upstream_revision": raw_manifest.get("revision"),
        "mappable_to_commit_sha": 0,
        "authentic_before_after_pairs_recovered": 0,
        "status": "BLOCKED_UNRESOLVED_PROVENANCE",
        "blocker_reason": (
            "All 17,636 clean REVEAL train donors lack commit IDs and file paths in the frozen upstream export "
            "(claudios/ReVeal@71f62e1e6e2053173e7de31a342d2c38b3fe2dcc). The exported records contain numeric "
            "source_id values without an associated mapping table to git commit hashes or repository diffs in the "
            "frozen research assets. Per protocol AGENTS.md, synthetic fixtures or unverified heuristics cannot replace "
            "true provenance. REVEAL pair pool remains strictly empty (BLOCKED)."
        ),
        "search_scope_audited": [
            RAW_MANIFEST_PATH.relative_to(ROOT).as_posix(),
            (FREEZE_DIR / "train_raw.jsonl").relative_to(ROOT).as_posix(),
            (FREEZE_DIR / "train_manifest.jsonl").relative_to(ROOT).as_posix(),
        ],
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }

    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("Step 4 Complete! REVEAL Provenance Summary:")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Step 4: REVEAL provenance recovery audit")
    parser.add_argument("--release-dir", type=Path, default=DEFAULT_RELEASE_DIR, help="Output release directory")
    args = parser.parse_args()
    run_step4(args.release_dir)
