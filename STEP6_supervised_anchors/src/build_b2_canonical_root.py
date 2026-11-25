"""Assemble the canonical B2 seed-42 input root for the Step 6 rerun.

The Step 6 lock run used B2 records from run3 (before the 66-row donor change).
Tables A/B use the canonical B2 records after the donor change. This script
copies the canonical records byte for byte into one root with the layout that
step6_complementarity.py reads, and checks that the canonical records differ
from run3 only in the expected rows:

- Devign validation: 28 rows (donor-28 review list)
- Devign test: 38 rows
- ReVeal validation and test: 0 rows

No inference, no threshold change. Only reads records and writes a new root.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from pathlib import Path

RUN3 = Path("01_Author_Baseline_Unified/kaggle_qwen_q4_b2/downloaded_output_20261101_run3/grace_b2_four_split_8h")
FROZEN = Path("01_Author_Baseline_Unified/output/local_full/inference_qwen_q4_b2_frozen_donor_20261102")
# Records of the 66-row donor rerun (I-09). Read as git blobs (LF), whose hashes
# match the donor-28 review (validation 794aa82b...).
RERUN66 = "Runs-management/kaggle_outputs_20261105/b2_rand/grace_b2_rand_three_seed_11h/b2_donor_rerun_66/devign/{split}/records.jsonl"
# Devign validation has no canonical file on this machine: it is rebuilt as run3
# with the 28 rerun rows replaced in place. The other splits are copied.
CANONICAL = {
    ("devign", "validation"): None,
    ("devign", "test"): FROZEN / "devign" / "test" / "records.jsonl",
    ("reveal", "validation"): RUN3 / "reveal" / "validation" / "records.jsonl",
    ("reveal", "test"): FROZEN / "reveal" / "test" / "records.jsonl",
}
EXPECTED_CHANGED = {("devign", "validation"): 28, ("devign", "test"): 38,
                    ("reveal", "validation"): 0, ("reveal", "test"): 0}
DONOR28_CSV = Path("docs/hieu_review_28_devign_validation.csv")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_records(path: Path) -> dict[str, dict]:
    return parse_lines(path.read_text(encoding="utf-8").splitlines(), str(path))


def parse_lines(lines: list[str], where: str) -> dict[str, dict]:
    rows = {}
    for line in lines:
        if line.strip():
            r = json.loads(line)
            if r["id"] in rows:
                raise ValueError(f"duplicate id {r['id']} in {where}")
            rows[r["id"]] = r
    return rows


def git_blob_lines(root: Path, rel: str) -> tuple[list[str], str]:
    data = subprocess.run(["git", "-C", str(root), "show", f"HEAD:{rel}"],
                          check=True, capture_output=True).stdout
    return data.decode("utf-8").splitlines(), hashlib.sha256(data).hexdigest()


def replace_rows(run3_path: Path, rerun_lines: list[str]) -> list[str]:
    """run3 lines in run3 order, with rerun rows replacing rows of the same ID."""
    rerun = {json.loads(l)["id"]: l for l in rerun_lines if l.strip()}
    out, used = [], set()
    for line in run3_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rid = json.loads(line)["id"]
        if rid in rerun:
            out.append(rerun[rid])
            used.add(rid)
        else:
            out.append(line)
    if used != set(rerun):
        raise SystemExit("FAIL rerun IDs missing from run3")
    return out


def changed_ids(old: dict[str, dict], new: dict[str, dict]) -> list[str]:
    if set(old) != set(new):
        raise ValueError("ID sets differ between run3 and canonical records")
    out = []
    for rid in sorted(new):
        a, b = old[rid], new[rid]
        if a["prompt_sha256"] != b["prompt_sha256"] or a["s"] != b["s"]:
            out.append(rid)
        elif a["label"] != b["label"]:
            raise ValueError(f"label differs for {rid}")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--summary-root", type=Path, default=Path("."))
    ap.add_argument("--out", type=Path,
                    default=Path("STEP6_supervised_anchors/inputs/b2_canonical_frozen_donor_20261102"))
    args = ap.parse_args()
    root = args.summary_root.resolve()
    out = (root / args.out).resolve()

    with (root / DONOR28_CSV).open(encoding="utf-8-sig", newline="") as f:
        donor28 = sorted(row["target_id"] for row in csv.DictReader(f))

    report = {"schema": "b2_canonical_root_v1",
              "purpose": "Step 6 rerun with canonical B2 (after 66-row donor change)",
              "run3_root": RUN3.as_posix(), "splits": {}}
    rerun = {split: git_blob_lines(root, RERUN66.format(split=split))
             for split in ("validation", "test")}
    report["rerun66_git_blob_sha256"] = {s: h for s, (_, h) in rerun.items()}
    for (ds, split), src in CANONICAL.items():
        run3_path = root / RUN3 / ds / split / "records.jsonl"
        if src is None:
            lines = replace_rows(run3_path, rerun[split][0])
            text = "\n".join(lines) + "\n"
            src_desc = f"{RUN3.as_posix()}/{ds}/{split}/records.jsonl with rows from {RERUN66.format(split=split)}"
        else:
            text = (root / src).read_text(encoding="utf-8")
            src_desc = src.as_posix()
        new = parse_lines(text.splitlines(), src_desc)
        old = read_records(run3_path)
        diff = changed_ids(old, new)
        if ds == "devign":
            rerun_ids = sorted(parse_lines(rerun[split][0], "rerun"))
            if diff != rerun_ids:
                raise SystemExit(f"FAIL {ds}/{split}: changed IDs are not exactly the rerun-66 IDs")
            rerun_rows = parse_lines(rerun[split][0], "rerun")
            if any(new[i]["s"] != rerun_rows[i]["s"] or new[i]["prompt_sha256"] != rerun_rows[i]["prompt_sha256"]
                   for i in rerun_ids):
                raise SystemExit(f"FAIL {ds}/{split}: canonical rows differ from rerun-66 rows")
        if len(diff) != EXPECTED_CHANGED[(ds, split)]:
            raise SystemExit(f"FAIL {ds}/{split}: {len(diff)} changed rows, "
                             f"expected {EXPECTED_CHANGED[(ds, split)]}")
        if (ds, split) == ("devign", "validation") and diff != donor28:
            raise SystemExit("FAIL devign/validation: changed IDs differ from donor-28 list")
        for r in new.values():
            if r["arm"] != "B2" or str(r["seed"]) != "42" or r["dataset"] != ds or r["split"] != split:
                raise SystemExit(f"FAIL {ds}/{split}: unexpected arm/seed/tag in {r['id']}")

        dst = out / ds / split
        dst.mkdir(parents=True, exist_ok=True)
        (dst / "records.jsonl").write_bytes(text.encode("utf-8"))
        rec_sha = sha256_file(dst / "records.jsonl")

        manifest = json.loads((root / RUN3 / ds / split / "run_manifest.json").read_text(encoding="utf-8"))
        manifest["canonical_assembly"] = {
            "records_source": src_desc,
            "records_sha256": rec_sha,
            "run3_records_sha256": sha256_file(run3_path),
            "rows": len(new),
            "rows_changed_vs_run3": len(diff),
            "note": ("Fields above canonical_assembly are copied from the run3 run_manifest. "
                     "When rows_changed_vs_run3 > 0, prompt_set_sha256 there describes run3, "
                     "not this record set."),
        }
        (dst / "run_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
                                               encoding="utf-8")
        report["splits"][f"{ds}/{split}"] = {
            "source": src_desc, "sha256": rec_sha,
            "rows": len(new), "changed_vs_run3": len(diff), "changed_ids": diff}
        print(f"PASS {ds}/{split}: rows={len(new)} changed_vs_run3={len(diff)}")

    (out / "assembly_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                                              encoding="utf-8")
    print(f"Wrote {out.relative_to(root).as_posix()}")


if __name__ == "__main__":
    main()
