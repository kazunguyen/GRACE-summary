"""Validate and summarize the two completed B1-H2 v5 reviewer forms."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARM = ROOT / "11_Arm_B1H2_Evidence"
RUNS = ROOT / "Runs-management"
PACKET = ROOT / "11_Arm_B1H2_Evidence/validation_h2_cluster_v5_20261104/manual_review_20261105_v2"
OUT = ROOT / "11_Arm_B1H2_Evidence/audit/b1_h2_manual_review_results_20261105.json"
FORMS = {
    "HuuHieu03": PACKET / "reviewer_1_hieu.csv",
    "Dung": PACKET / "reviewer_2_dung.csv",
}
JUDGMENTS = (
    "target_code_intact", "graph_valid", "demo_valid", "no_target_label_leak",
    "variant_correct", "truncation_acceptable", "overall_verdict",
)
REQUIRED = ("reviewer_name", "reviewed_at", *JUDGMENTS)


def load_csv(path: Path) -> tuple[list[dict[str, str]], str]:
    raw = path.read_bytes()
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream)), hashlib.sha256(raw).hexdigest()


def main() -> None:
    samples = [json.loads(line) for line in (PACKET / "manual_sample.jsonl").read_text(encoding="utf-8").splitlines() if line]
    expected = [(row["id"], row["prompt_sha256"]) for row in samples]
    by_reviewer = {}
    form_metadata = {}
    for reviewer, path in FORMS.items():
        rows, digest = load_csv(path)
        if len(rows) != len(expected):
            raise ValueError(f"{reviewer}: expected {len(expected)} rows, got {len(rows)}")
        if [(row["id"], row["prompt_sha256"]) for row in rows] != expected:
            raise ValueError(f"{reviewer}: row identity/order differs from blind packet")
        if any(row["reviewer_name"] != reviewer for row in rows):
            raise ValueError(f"{reviewer}: reviewer name is inconsistent within form")
        missing = [(row["id"], key) for row in rows for key in REQUIRED if not row[key].strip()]
        if missing:
            raise ValueError(f"{reviewer}: blank judgments or metadata: {missing[:5]}")
        comments_missing = [row["id"] for row in rows if row["overall_verdict"] in {"fail", "unclear"} and not row["comments"].strip()]
        if comments_missing:
            raise ValueError(f"{reviewer}: fail/unclear rows lack reasons: {comments_missing}")
        by_reviewer[reviewer] = rows
        form_metadata[reviewer] = {
            "file": path.name,
            "sha256": digest,
            "rows": len(rows),
            "self_reported_reviewed_at": sorted({row["reviewed_at"] for row in rows}),
            "counts": {field: dict(Counter(row[field] for row in rows)) for field in JUDGMENTS},
        }

    reviewers = list(by_reviewer)
    left, right = (by_reviewer[name] for name in reviewers)
    agreement = {field: sum(a[field] == b[field] for a, b in zip(left, right)) for field in JUDGMENTS}
    disagreements = []
    for a, b in zip(left, right):
        fields = [field for field in JUDGMENTS if a[field] != b[field]]
        if fields:
            disagreements.append({"id": a["id"], "fields": {field: [a[field], b[field]] for field in fields}})

    sample_by_id = {row["id"]: row for row in samples}
    graph_variant_failures = [
        row["id"] for row in left
        if row["graph_valid"] == "fail" or row["variant_correct"] == "fail"
    ]
    if len(graph_variant_failures) != 9 or any(sample_by_id[item]["sampling_category"] != "missing_cpg" for item in graph_variant_failures):
        raise ValueError("Graph/variant failures are not exactly the sampled missing-CPG rows; inspect manually")

    out = {
        "schema": "b1_h2_completed_manual_review_audit_v1",
        "packet_path": str(PACKET),
        "candidate_manifest_sha256": hashlib.sha256((ROOT / "11_Arm_B1H2_Evidence/validation_h2_cluster_v5_20261104/manifest.json").read_bytes()).hexdigest(),
        "scope": "Checks completed forms against the blind sample IDs and prompt hashes; summarizes reviewer-entered judgments. Names and times are self-reported and are not independently authenticated by this script.",
        "forms": form_metadata,
        "duplicate_alias_files": {
            "reviewer_1_filled.csv": "reviewer_1_hieu.csv",
            "reviewer_2_filled.csv": "reviewer_2_dung.csv",
        },
        "reviewer_agreement_count_out_of_60": agreement,
        "disagreements": disagreements,
        "graph_and_variant_failures": {
            "count": len(graph_variant_failures),
            "all_are_sampled_missing_cpg_rows": True,
            "ids": graph_variant_failures,
        },
        "full_prompt_audit_verdict": "fail_or_unclear_rows_present_in_both_forms",
        "automatic_structural_checks": "pass",
        "note": "This report validates form completeness and packet identity; it does not adjudicate the four differing overall verdicts or replace reviewer sign-off.",
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
