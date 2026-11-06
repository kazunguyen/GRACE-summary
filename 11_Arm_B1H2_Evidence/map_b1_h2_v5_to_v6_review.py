"""Map completed v5 judgments to exact-hash prompts in v6 without editing forms."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARM = ROOT / "11_Arm_B1H2_Evidence"
RUNS = ROOT / "Runs-management"
V5 = ROOT / "11_Arm_B1H2_Evidence/validation_h2_cluster_v5_20261104/manual_review_20261105_v2"
V6 = ROOT / "11_Arm_B1H2_Evidence/validation_h2_cluster_v6_joern_error_20261105/manual_review_20261105_v6"
OUT = ROOT / "11_Arm_B1H2_Evidence/audit/b1_h2_v5_v6_review_carryforward_20261105.json"
FORMS = ("reviewer_1_hieu.csv", "reviewer_2_dung.csv")


def load_rows(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def main() -> None:
    old_sample = [json.loads(line) for line in (V5 / "manual_sample.jsonl").read_text(encoding="utf-8").splitlines() if line]
    new_sample = [json.loads(line) for line in (V6 / "manual_sample.jsonl").read_text(encoding="utf-8").splitlines() if line]
    old_by_id = {row["id"]: row for row in old_sample}
    new_by_id = {row["id"]: row for row in new_sample}
    if old_by_id.keys() != new_by_id.keys():
        raise ValueError("v5/v6 blinded samples do not contain the same IDs")
    forms = {name: {row["id"]: row for row in load_rows(V5 / name)} for name in FORMS}
    unchanged, changed = [], []
    for uid, current in new_by_id.items():
        prior = old_by_id[uid]
        record = {
            "id": uid,
            "dataset": current["dataset"],
            "prior_prompt_sha256": prior["prompt_sha256"],
            "current_prompt_sha256": current["prompt_sha256"],
        }
        if prior["prompt_sha256"] == current["prompt_sha256"]:
            record["review_status"] = "exact_hash_match_prior_judgments_reusable"
            record["prior_reviewers"] = {
                name: {
                    "reviewer_name": forms[name][uid]["reviewer_name"],
                    "reviewed_at": forms[name][uid]["reviewed_at"],
                    "overall_verdict": forms[name][uid]["overall_verdict"],
                    "graph_valid": forms[name][uid]["graph_valid"],
                    "variant_correct": forms[name][uid]["variant_correct"],
                    "truncation_acceptable": forms[name][uid]["truncation_acceptable"],
                    "comments": forms[name][uid]["comments"],
                }
                for name in FORMS
            }
            unchanged.append(record)
        else:
            record["review_status"] = "prompt_changed_re_review_required"
            record["prior_reviewers"] = {
                name: {
                    "reviewer_name": forms[name][uid]["reviewer_name"],
                    "reviewed_at": forms[name][uid]["reviewed_at"],
                    "overall_verdict": forms[name][uid]["overall_verdict"],
                    "graph_valid": forms[name][uid]["graph_valid"],
                    "variant_correct": forms[name][uid]["variant_correct"],
                    "comments": forms[name][uid]["comments"],
                }
                for name in FORMS
            }
            changed.append(record)
    out = {
        "schema": "b1_h2_v5_v6_review_carryforward_v1",
        "scope": "Hash-based mapping only. Does not modify or sign v6 reviewer forms.",
        "v5_candidate_manifest_sha256": hashlib.sha256((V5.parent / "manifest.json").read_bytes()).hexdigest(),
        "v6_candidate_manifest_sha256": hashlib.sha256((V6.parent / "manifest.json").read_bytes()).hexdigest(),
        "sample_ids_identical": True,
        "rows_with_exact_same_prompt_hash": len(unchanged),
        "rows_requiring_fresh_review": len(changed),
        "unchanged_rows": unchanged,
        "changed_rows": changed,
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: out[key] for key in ("schema", "sample_ids_identical", "rows_with_exact_same_prompt_hash", "rows_requiring_fresh_review")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
