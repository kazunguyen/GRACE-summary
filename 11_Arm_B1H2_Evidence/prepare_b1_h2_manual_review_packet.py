"""Prepare a blind, two-reviewer sample from the B1-H2 v5 validation candidate."""
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
OUT = CANDIDATE / "manual_review_20261105_v2"
DATASETS = {"devign": 2732, "reveal": 2273}
ALLOCATIONS = {
    "devign": {"missing_cpg": 3, "no_usable_evidence": 10, "cdg_cluster": 10, "closed_prefix": 7},
    "reveal": {"missing_cpg": 6, "no_usable_evidence": 10, "cdg_cluster": 8, "closed_prefix": 6},
}
FIELDS = [
    "sample_id", "dataset", "split", "arm", "seed", "id", "prompt_sha256",
    "reviewer_name", "reviewed_at", "target_code_intact", "graph_valid",
    "demo_valid", "no_target_label_leak", "variant_correct",
    "truncation_acceptable", "overall_verdict", "comments",
]


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_rows(path: Path):
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            if line.strip():
                yield json.loads(line)


def sample_key(dataset: str, category: str, row: dict) -> str:
    return hashlib.sha256(
        f"b1-h2-v5-manual-review-20261105|{dataset}|{category}|{row['id']}".encode("utf-8")
    ).hexdigest()


def category(row: dict) -> str:
    h2 = row["evidence"]["h2"]
    if int(h2.get("source_nodes", 0)) == 0:
        return "missing_cpg"
    if h2.get("no_usable_evidence"):
        return "no_usable_evidence"
    if h2.get("input_policy") == "cdg_cluster":
        return "cdg_cluster"
    return "closed_prefix"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=False)
    selected = []
    allocation_counts = {}
    selection_details = {}
    for dataset, expected in DATASETS.items():
        source = CANDIDATE / dataset / "validation/B1-H2/42/prompts.jsonl"
        rows = list(load_rows(source))
        if len(rows) != expected or len({r["id"] for r in rows}) != expected:
            raise ValueError(f"Unexpected candidate census for {dataset}")
        audit_path = CANDIDATE / dataset / "validation/B1-H2/42/audit_rows.csv"
        with audit_path.open(encoding="utf-8-sig", newline="") as stream:
            audit_by_id = {row["id"]: row for row in csv.DictReader(stream)}
        if set(audit_by_id) != {row["id"] for row in rows}:
            raise ValueError(f"Audit CSV ID mismatch for {dataset}")
        grouped = {name: [] for name in ALLOCATIONS[dataset]}
        for row in rows:
            grouped[category(row)].append(row)
        allocation_counts[dataset] = {}
        selection_details[dataset] = {}
        for name, count in ALLOCATIONS[dataset].items():
            pool = sorted(grouped[name], key=lambda row: sample_key(dataset, name, row))
            if len(pool) < count:
                raise ValueError(f"Insufficient {dataset}/{name} candidates")
            chosen = []
            truncated = [row for row in pool if any(
                audit_by_id[row["id"]][key] == "True"
                for key in ("code_truncated", "graph_truncated", "demo_truncated")
            )]
            long_rows = [row for row in pool if int(audit_by_id[row["id"]]["tokens_total"]) >= 2000]
            if truncated:
                chosen.append(truncated[0])
            for row in long_rows:
                if len(chosen) == count:
                    break
                if row["id"] not in {entry["id"] for entry in chosen}:
                    chosen.append(row)
                    break
            for row in pool:
                if len(chosen) == count:
                    break
                if row["id"] not in {entry["id"] for entry in chosen}:
                    chosen.append(row)
            allocation_counts[dataset][name] = {"available": len(pool), "sampled": count}
            selection_details[dataset][name] = {
                "sampled_truncated": sum(any(
                    audit_by_id[row["id"]][key] == "True"
                    for key in ("code_truncated", "graph_truncated", "demo_truncated")
                ) for row in chosen),
                "sampled_at_least_2000_tokens": sum(int(audit_by_id[row["id"]]["tokens_total"]) >= 2000 for row in chosen),
            }
            selected.extend((dataset, row) for row in chosen)

    selected.sort(key=lambda item: (item[0], item[1]["id"]))
    records = []
    for i, (dataset, row) in enumerate(selected, start=1):
        records.append({
            "sample_id": f"{i:02d}", "dataset": dataset, "split": "validation",
            "arm": "B1-H2", "seed": 42, "id": row["id"],
            "prompt_sha256": row["prompt_sha256"], "prompt": row["prompt"],
            "sampling_category": category(row),
        })

    with (OUT / "manual_sample.jsonl").open("w", encoding="utf-8", newline="\n") as stream:
        for row in records:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    for reviewer in ("reviewer_1.csv", "reviewer_2.csv"):
        with (OUT / reviewer).open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=FIELDS)
            writer.writeheader()
            for row in records:
                writer.writerow({key: row.get(key, "") for key in FIELDS})

    lines = [
        "# Blind manual review — B1-H2 v5 validation candidate", "",
        "Scope: 60 validation prompts from candidate v5, 30 Devign and 30 ReVeal. No target labels, inference outputs, thresholds, model verdicts, or sample strata are shown in the review packet.",
        "Each reviewer should work independently, complete every criterion, and record their actual name and review time. Do not copy scores between forms.",
    ]
    lines += [
        "", "## Review criteria", "",
        "For each criterion use `pass`, `fail`, `unclear`, or `not_applicable`; include a short reason and location for every fail/unclear.",
        "- `target_code_intact`: target code matches the expected source and truncation has not removed essential context.",
        "- `graph_valid`: graph belongs to the target and H2 evidence is understandable; a missing CPG must be called out.",
        "- `demo_valid`: B1-H2 has no demonstrations; enter `not_applicable`.",
        "- `no_target_label_leak`: no target label or answer is exposed in the prompt.",
        "- `variant_correct`: prompt follows the B1-H2 H2 execution-evidence presentation specified for this candidate.",
        "- `truncation_acceptable`: truncation leaves a usable prompt within its stated evidence limits.",
        "- `overall_verdict`: `pass`, `fail`, or `unclear`.",
        "", "## Files", "",
        "- `manual_packet.md`: readable blind prompt packet.",
        "- `manual_sample.jsonl`: internal sampling audit trail; do not show this file to reviewers.",
        "- `reviewer_1.csv`, `reviewer_2.csv`: separate blank forms; preserve both originals.",
        "- Rubric reference: `../../prompt_audit_20261102/RUBRIC.md`.",
        "", "Candidate prompt files remain unchanged. This sample is not a substitute for reviewing inference results or target labels.", "",
    ]
    (OUT / "README.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")

    packet = ["# Manual review packet — B1-H2 v5", ""]
    for row in records:
        packet.extend([
            f"## Sample {row['sample_id']} · {row['dataset']} · {row['arm']} · seed {row['seed']}", "",
            f"ID: `{row['id']}`  ", f"Prompt SHA-256: `{row['prompt_sha256']}`", "", "~~~~~text", row["prompt"], "~~~~~", "",
        ])
    (OUT / "manual_packet.md").write_text("\n".join(packet), encoding="utf-8", newline="\n")

    hashes = {}
    for path in sorted(OUT.iterdir()):
        if path.is_file() and path.name != "SHA256.json":
            hashes[path.name] = sha_bytes(path.read_bytes())
    (OUT / "SHA256.json").write_text(
        json.dumps({"schema": "b1_h2_v5_manual_review_packet_v2", "files": hashes,
                    "candidate_manifest_sha256": sha_bytes((CANDIDATE / "manifest.json").read_bytes()),
                    "strata": allocation_counts, "sample_detail": selection_details}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({"output": str(OUT), "samples": len(records),
                      "by_dataset": dict(Counter(row["dataset"] for row in records)),
                      "review_forms": 2}, ensure_ascii=False))


if __name__ == "__main__":
    main()
