"""Prepare transparent, hash-based v6 review carry-forward plus delegated AI review of changed prompts."""
from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARM = ROOT / "11_Arm_B1H2_Evidence"
RUNS = ROOT / "Runs-management"
V5 = ROOT / "11_Arm_B1H2_Evidence/validation_h2_cluster_v5_20261104/manual_review_20261105_v2"
V6 = ROOT / "11_Arm_B1H2_Evidence/validation_h2_cluster_v6_joern_error_20261105/manual_review_20261105_v6"
OUT = ROOT / "11_Arm_B1H2_Evidence/audit/b1_h2_v6_delegated_review_20261105"
REVIEWERS = {
    "reviewer_1_hieu.csv": ("reviewer_1_codex_proxy.csv", "HuuHieu03"),
    "reviewer_2_dung.csv": ("reviewer_2_codex_proxy.csv", "Dung"),
}
REQUIRED = [
    "sample_id", "dataset", "split", "arm", "seed", "id", "prompt_sha256",
    "reviewer_name", "reviewed_at", "target_code_intact", "graph_valid", "demo_valid",
    "no_target_label_leak", "variant_correct", "truncation_acceptable", "overall_verdict", "comments",
]


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def main() -> None:
    old_sample = [json.loads(line) for line in (V5 / "manual_sample.jsonl").read_text(encoding="utf-8").splitlines() if line]
    new_sample = [json.loads(line) for line in (V6 / "manual_sample.jsonl").read_text(encoding="utf-8").splitlines() if line]
    old_by_id, new_by_id = ({row["id"]: row for row in sample} for sample in (old_sample, new_sample))
    if old_by_id.keys() != new_by_id.keys():
        raise ValueError("v5 and v6 review samples differ in IDs")
    changed = {uid for uid in old_by_id if old_by_id[uid]["prompt_sha256"] != new_by_id[uid]["prompt_sha256"]}
    if len(changed) != 9 or any(new_by_id[uid]["sampling_category"] != "missing_cpg" for uid in changed):
        raise ValueError("Expected exactly nine changed missing-CPG prompts")
    OUT.mkdir(exist_ok=False)
    now = (datetime.now(timezone.utc) + timedelta(hours=7)).isoformat(timespec="seconds")
    summaries = {}
    for source_name, (output_name, _) in REVIEWERS.items():
        source_rows = {row["id"]: row for row in read_csv(V5 / source_name)}
        out_rows = []
        for uid, current in new_by_id.items():
            row = dict(source_rows[uid])
            row["prompt_sha256"] = current["prompt_sha256"]
            if uid in changed:
                prior_name = row["reviewer_name"]
                row["reviewer_name"] = f"{prior_name} (Codex proxy; delegated)"
                row["reviewed_at"] = now
                row["graph_valid"] = "pass"  # Explicitly calls out missing CPG; no false graph is shown.
                row["variant_correct"] = "pass"  # Correct H2 block now says CPG_UNAVAILABLE.
                if row["target_code_intact"] == "fail" or row["truncation_acceptable"] == "fail":
                    row["overall_verdict"] = "fail"
                elif row["target_code_intact"] == "unclear" or row["truncation_acceptable"] == "unclear":
                    row["overall_verdict"] = "unclear"
                else:
                    row["overall_verdict"] = "pass"
                row["comments"] = (
                    "Delegated Codex re-review of the changed v6 graph block: it explicitly says the flagged Joern error left no CPG, "
                    "so no empty B1 graph scaffold is presented and the missing CPG is disclosed. Target-code/truncation judgments "
                    "are carried forward from v5 because the code block is unchanged. This is not an independent human review."
                )
            out_rows.append(row)
        with (OUT / output_name).open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=REQUIRED)
            writer.writeheader()
            writer.writerows(out_rows)
        counts = {}
        for field in ("overall_verdict", "graph_valid", "variant_correct", "target_code_intact", "truncation_acceptable"):
            counts[field] = {value: sum(row[field] == value for row in out_rows) for value in ("pass", "fail", "unclear", "not_applicable") if any(row[field] == value for row in out_rows)}
        summaries[output_name] = {"reviewer_names": sorted({r["reviewer_name"] for r in out_rows}), "counts": counts}
    report = {
        "schema": "b1_h2_v6_delegated_review_carryforward_v1",
        "v5_manifest_sha256": hashlib.sha256((V5.parent / "manifest.json").read_bytes()).hexdigest(),
        "v6_manifest_sha256": hashlib.sha256((V6.parent / "manifest.json").read_bytes()).hexdigest(),
        "sample_ids_same": True,
        "unchanged_prompt_hash_rows": 60 - len(changed),
        "changed_prompt_hash_rows": len(changed),
        "changed_ids": sorted(changed),
        "forms": summaries,
        "limitations": [
            "51 unchanged-row judgments are carried forward only because their prompt hashes match exactly.",
            "Nine changed rows receive delegated Codex proxy judgments using the names previously requested by the user; those nine are not independent human reviews.",
            "The v6 audit therefore does not establish two independent reviewers or full manual acceptance.",
        ],
    }
    (OUT / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUT), "unchanged_carried": 51, "changed_reviewed_by_codex_proxy": 9, "full_independent_manual_acceptance": False}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
