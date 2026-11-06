"""Verify identity, blinding, quotas and file hashes for the B1-H2 v5 review packet."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARM = ROOT / "11_Arm_B1H2_Evidence"
RUNS = ROOT / "Runs-management"
CANDIDATE = ROOT / "11_Arm_B1H2_Evidence/validation_h2_cluster_v5_20261104"
PACKET = CANDIDATE / "manual_review_20261105_v2"
OUT = ROOT / "11_Arm_B1H2_Evidence/audit/b1_h2_manual_review_packet_audit_20261105.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows(path: Path):
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            if line.strip():
                yield json.loads(line)


def main() -> None:
    manifest = json.loads((PACKET / "SHA256.json").read_text(encoding="utf-8"))
    for name, digest in manifest["files"].items():
        if sha(PACKET / name) != digest:
            raise ValueError(f"Packet file hash mismatch: {name}")
    candidate_hash = sha(CANDIDATE / "manifest.json")
    if candidate_hash != manifest["candidate_manifest_sha256"]:
        raise ValueError("Candidate manifest hash mismatch")

    sample = list(read_rows(PACKET / "manual_sample.jsonl"))
    if len(sample) != 60 or len({row["id"] for row in sample}) != 60:
        raise ValueError("Sample count or ID uniqueness failure")
    by_dataset = Counter(row["dataset"] for row in sample)
    if by_dataset != {"devign": 30, "reveal": 30}:
        raise ValueError(f"Unexpected dataset counts: {dict(by_dataset)}")

    prompt_hash_checks = []
    for dataset in by_dataset:
        source = CANDIDATE / dataset / "validation/B1-H2/42/prompts.jsonl"
        source_by_id = {row["id"]: row for row in read_rows(source)}
        for item in (row for row in sample if row["dataset"] == dataset):
            original = source_by_id[item["id"]]
            text_hash = hashlib.sha256(item["prompt"].encode("utf-8")).hexdigest()
            if (text_hash != item["prompt_sha256"]
                    or item["prompt"] != original["prompt"]
                    or item["prompt_sha256"] != original["prompt_sha256"]):
                raise ValueError(f"Sample prompt differs from candidate: {item['id']}")
            prompt_hash_checks.append(item["id"])

    manual = (PACKET / "manual_packet.md").read_text(encoding="utf-8")
    if any(row["id"] not in manual or row["prompt_sha256"] not in manual for row in sample):
        raise ValueError("Readable packet is missing a sample identity/hash")
    if "sampling_category" in manual or "Stratum:" in manual:
        raise ValueError("Sampling strata leaked into the reviewer-facing packet")

    reviewer_forms = {}
    for name in ("reviewer_1.csv", "reviewer_2.csv"):
        with (PACKET / name).open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
        if len(rows) != 60:
            raise ValueError(f"Unexpected row count in {name}")
        required_blank = [
            "reviewer_name", "reviewed_at", "target_code_intact", "graph_valid",
            "demo_valid", "no_target_label_leak", "variant_correct",
            "truncation_acceptable", "overall_verdict", "comments",
        ]
        nonblank = sum(bool(row[key].strip()) for row in rows for key in required_blank)
        if nonblank:
            raise ValueError(f"Reviewer form unexpectedly contains judgments: {name}")
        if [row["prompt_sha256"] for row in rows] != [row["prompt_sha256"] for row in sample]:
            raise ValueError(f"Reviewer form ordering/identity mismatch: {name}")
        reviewer_forms[name] = {"rows": len(rows), "judgments_filled": nonblank}

    strata = manifest["strata"]
    detail = manifest["sample_detail"]
    out = {
        "schema": "b1_h2_manual_review_packet_audit_v1",
        "packet_path": str(PACKET),
        "candidate_manifest_sha256": candidate_hash,
        "packet_file_hashes_pass": True,
        "sample_rows": len(sample),
        "sample_counts_by_dataset": dict(by_dataset),
        "candidate_prompt_identity_and_sha256_pass": len(prompt_hash_checks) == 60,
        "reviewer_facing_packet_hides_sampling_strata": True,
        "reviewer_forms": reviewer_forms,
        "sampling_strata": strata,
        "sample_detail": detail,
        "overall_pass": True,
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
