#!/usr/bin/env python3
"""
discover_local.py - Local Donor Indexing & Heuristic Candidate Pair Discovery

Discovers heuristic patch candidates from frozen local donor datasets (Devign/REVEAL)
by matching function names across vulnerable (label=1) and non-vulnerable (label=0)
functions within the same project.

Integrity and protocol compliance:
- Validates frozen input files via streaming SHA-256 against freeze_manifest.json before writing outputs.
- Enforces unique IDs, identical raw/manifest ID sets, code hashes, and donor_count matching.
- Rejects existing output directories without alteration.
- Completes all integrity validation BEFORE creating output directory or artifacts.
- Strictly adheres to Python 3.10 standard library without network or subprocesses.
"""

import argparse
import hashlib
import itertools
import json
import os
import re
import sys
from typing import Any, Dict, List, Optional, Tuple


def compute_file_sha256(filepath: str) -> str:
    """Compute SHA-256 over exact file bytes using streaming reads."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def extract_function_hint(func: str) -> Optional[str]:
    """
    Extract function-name hint heuristic:
    ONLY the first match of r"([A-Za-z_]\w*)\s*\(" in func.split("{", 1)[0], or None.
    It is deliberately an imperfect heuristic.
    """
    header = func.split("{", 1)[0]
    match = re.search(r"([A-Za-z_]\w*)\s*\(", header)
    if match:
        return match.group(1)
    return None


def project_sort_key(project: Optional[str]) -> Tuple[int, str]:
    """Consistent sorting key for project handling None without comparing None to str."""
    if project is None:
        return (1, "")
    return (0, str(project))


def donor_id_sort_key(donor_id: Any) -> Tuple[int, str]:
    """Consistent sorting key for donor IDs handling potential mixed types."""
    return (0, str(donor_id))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Discover local heuristic candidate pairs from frozen donor dataset."
    )
    parser.add_argument(
        "--freeze",
        required=True,
        type=str,
        help="Path to directory containing freeze_manifest.json and dataset subdirectories.",
    )
    parser.add_argument(
        "--dataset",
        required=True,
        choices=["devign", "reveal"],
        help="Dataset name: devign or reveal.",
    )
    parser.add_argument(
        "--out",
        required=True,
        type=str,
        help="Path to new output directory (must not exist).",
    )

    args = parser.parse_args()

    # Step 1: Reject existing out directory without altering it
    if os.path.exists(args.out):
        sys.exit(f"Error: Output directory already exists: '{args.out}'. Existing output must be rejected.")

    # Step 2: Validate freeze directory and manifest existence
    freeze_dir = os.path.abspath(args.freeze)
    if not os.path.isdir(freeze_dir):
        sys.exit(f"Error: Freeze path '{freeze_dir}' is not a directory.")

    manifest_path = os.path.join(freeze_dir, "freeze_manifest.json")
    if not os.path.isfile(manifest_path):
        sys.exit(f"Error: freeze_manifest.json not found in '{freeze_dir}'.")

    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            freeze_manifest = json.load(f)
    except Exception as e:
        sys.exit(f"Error reading freeze_manifest.json: {e}")

    datasets_manifest = freeze_manifest.get("datasets", {})
    if args.dataset not in datasets_manifest:
        sys.exit(f"Error: Dataset '{args.dataset}' not configured in freeze_manifest.json.")

    dataset_spec = datasets_manifest[args.dataset]
    expected_donor_count = dataset_spec.get("donor_count")
    if expected_donor_count is None:
        sys.exit(f"Error: 'donor_count' missing for dataset '{args.dataset}' in freeze_manifest.json.")

    expected_files_sha256 = dataset_spec.get("files_sha256", {})
    for required_file in ["train_raw.jsonl", "train_manifest.jsonl"]:
        if required_file not in expected_files_sha256:
            sys.exit(f"Error: Expected SHA-256 for '{required_file}' missing in freeze_manifest.json.")

    dataset_subdir = os.path.join(freeze_dir, args.dataset)
    if not os.path.isdir(dataset_subdir):
        sys.exit(f"Error: Dataset subdirectory '{dataset_subdir}' not found.")

    train_raw_path = os.path.join(dataset_subdir, "train_raw.jsonl")
    train_manifest_path = os.path.join(dataset_subdir, "train_manifest.jsonl")

    if not os.path.isfile(train_raw_path):
        sys.exit(f"Error: File '{train_raw_path}' does not exist.")
    if not os.path.isfile(train_manifest_path):
        sys.exit(f"Error: File '{train_manifest_path}' does not exist.")

    # Step 3: Verify streaming file SHA-256 hashes against freeze manifest
    raw_file_sha256 = compute_file_sha256(train_raw_path)
    if raw_file_sha256 != expected_files_sha256["train_raw.jsonl"]:
        sys.exit(
            f"Error: SHA-256 mismatch for train_raw.jsonl. "
            f"Expected {expected_files_sha256['train_raw.jsonl']}, got {raw_file_sha256}."
        )

    manifest_file_sha256 = compute_file_sha256(train_manifest_path)
    if manifest_file_sha256 != expected_files_sha256["train_manifest.jsonl"]:
        sys.exit(
            f"Error: SHA-256 mismatch for train_manifest.jsonl. "
            f"Expected {expected_files_sha256['train_manifest.jsonl']}, got {manifest_file_sha256}."
        )

    # Step 4: Parse train_raw.jsonl
    raw_records: Dict[Any, Dict[str, Any]] = {}
    raw_count = 0
    with open(train_raw_path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line_str = line.strip()
            if not line_str:
                sys.exit(f"Error: Empty line at line {line_no} in '{train_raw_path}'.")
            try:
                row = json.loads(line_str)
            except Exception as e:
                sys.exit(f"Error: Malformed JSON at line {line_no} in '{train_raw_path}': {e}")

            for field in ["id", "dataset", "split", "func", "target", "project", "commit_id", "source_id"]:
                if field not in row:
                    sys.exit(f"Error: Missing field '{field}' at line {line_no} in '{train_raw_path}'.")

            row_id = row["id"]
            if row_id in raw_records:
                sys.exit(f"Error: Duplicate ID '{row_id}' found at line {line_no} in '{train_raw_path}'.")

            if row["dataset"] != args.dataset:
                sys.exit(
                    f"Error: Invalid dataset '{row['dataset']}' (expected '{args.dataset}') "
                    f"at line {line_no} in '{train_raw_path}'."
                )

            if row["split"] != "train":
                sys.exit(
                    f"Error: Invalid split '{row['split']}' (expected 'train') "
                    f"at line {line_no} in '{train_raw_path}'."
                )

            if row["target"] not in (0, 1):
                sys.exit(
                    f"Error: Invalid target '{row['target']}' (expected 0 or 1) "
                    f"at line {line_no} in '{train_raw_path}'."
                )

            if not isinstance(row["func"], str):
                sys.exit(f"Error: 'func' must be a string at line {line_no} in '{train_raw_path}'.")

            raw_records[row_id] = row
            raw_count += 1

    # Step 5: Parse train_manifest.jsonl
    manifest_records: Dict[Any, Dict[str, Any]] = {}
    with open(train_manifest_path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line_str = line.strip()
            if not line_str:
                sys.exit(f"Error: Empty line at line {line_no} in '{train_manifest_path}'.")
            try:
                row = json.loads(line_str)
            except Exception as e:
                sys.exit(f"Error: Malformed JSON at line {line_no} in '{train_manifest_path}': {e}")

            for field in ["id", "keep_in_bank", "label", "code_sha256"]:
                if field not in row:
                    sys.exit(f"Error: Missing field '{field}' at line {line_no} in '{train_manifest_path}'.")

            row_id = row["id"]
            if row_id in manifest_records:
                sys.exit(f"Error: Duplicate ID '{row_id}' found at line {line_no} in '{train_manifest_path}'.")

            if not isinstance(row["keep_in_bank"], bool):
                sys.exit(f"Error: 'keep_in_bank' must be a boolean at line {line_no} in '{train_manifest_path}'.")

            if row["label"] not in (0, 1):
                sys.exit(
                    f"Error: Invalid label '{row['label']}' (expected 0 or 1) "
                    f"at line {line_no} in '{train_manifest_path}'."
                )

            if not isinstance(row["code_sha256"], str):
                sys.exit(f"Error: 'code_sha256' must be a string at line {line_no} in '{train_manifest_path}'.")

            manifest_records[row_id] = row

    # Step 6: Validate ID set correspondence
    raw_id_set = set(raw_records.keys())
    manifest_id_set = set(manifest_records.keys())
    if raw_id_set != manifest_id_set:
        diff_raw = raw_id_set - manifest_id_set
        diff_manifest = manifest_id_set - raw_id_set
        sys.exit(
            f"Error: ID sets between train_raw.jsonl and train_manifest.jsonl do not match. "
            f"In raw only: {len(diff_raw)}, in manifest only: {len(diff_manifest)}."
        )

    # Step 7: Filter donors and validate kept row label and code hash
    donors: List[Dict[str, Any]] = []
    donors_missing_commit_id = 0

    for row_id, m_row in manifest_records.items():
        if m_row["keep_in_bank"]:
            r_row = raw_records[row_id]

            # Label validation
            if r_row["target"] != m_row["label"]:
                sys.exit(
                    f"Error: Kept row label mismatch for ID '{row_id}': "
                    f"raw target={r_row['target']}, manifest label={m_row['label']}."
                )

            # Code SHA-256 validation over exact func UTF-8 bytes (no normalization)
            computed_code_hash = hashlib.sha256(r_row["func"].encode("utf-8")).hexdigest()
            if computed_code_hash != m_row["code_sha256"]:
                sys.exit(
                    f"Error: Kept row code hash mismatch for ID '{row_id}': "
                    f"manifest code_sha256={m_row['code_sha256']}, computed={computed_code_hash}."
                )

            commit_id = r_row["commit_id"]
            if commit_id is None or (isinstance(commit_id, str) and not commit_id.strip()):
                donors_missing_commit_id += 1

            hint = extract_function_hint(r_row["func"])

            donor_entry = {
                "id": row_id,
                "label": r_row["target"],
                "project": r_row["project"],
                "function_hint": hint,
                "func": r_row["func"],
                "commit_id": commit_id,
                "code_sha256": m_row["code_sha256"],
                "source_id": r_row["source_id"],
            }
            donors.append(donor_entry)

    bank_count = len(donors)
    if bank_count != expected_donor_count:
        sys.exit(
            f"Error: Donor count mismatch for dataset '{args.dataset}'. "
            f"Expected {expected_donor_count} from freeze_manifest.json, found {bank_count}."
        )

    # Step 8: Group donors by (project, function_hint) for heuristic candidate pair enumeration
    # Skipping missing hints
    groups: Dict[Tuple[Optional[str], str], List[Dict[str, Any]]] = {}
    for d in donors:
        hint = d["function_hint"]
        if hint is not None:
            group_key = (d["project"], hint)
            groups.setdefault(group_key, []).append(d)

    # Deterministic group ordering
    sorted_group_keys = sorted(
        groups.keys(),
        key=lambda k: (project_sort_key(k[0]), k[1])
    )

    candidate_pairs: List[Dict[str, Any]] = []
    same_commit_candidate_count = 0

    for group_key in sorted_group_keys:
        group_donors = groups[group_key]
        label1_donors = [d for d in group_donors if d["label"] == 1]
        label0_donors = [d for d in group_donors if d["label"] == 0]

        if not label1_donors or not label0_donors:
            continue

        label1_donors.sort(key=lambda d: donor_id_sort_key(d["id"]))
        label0_donors.sort(key=lambda d: donor_id_sort_key(d["id"]))

        for v1, v0 in itertools.product(label1_donors, label0_donors):
            if v1["id"] == v0["id"]:
                continue

            c1 = v1["commit_id"]
            c0 = v0["commit_id"]
            same_commit = bool(
                c1 is not None
                and c0 is not None
                and isinstance(c1, str)
                and isinstance(c0, str)
                and c1.strip()
                and c1 == c0
            )
            if same_commit:
                same_commit_candidate_count += 1

            chars = len(v1["func"]) + len(v0["func"])

            pair = {
                "project": v1["project"],
                "function_hint": v1["function_hint"],
                "vulnerable_id": v1["id"],
                "patched_candidate_id": v0["id"],
                "vulnerable_commit": c1,
                "patched_candidate_commit": c0,
                "before_sha256": v1["code_sha256"],
                "after_sha256": v0["code_sha256"],
                "characters": chars,
                "same_commit": same_commit,
                "status": "UNVERIFIED_NAME_MATCH_NOT_AN_ELIGIBLE_PAIR",
            }
            candidate_pairs.append(pair)

    candidate_count = len(candidate_pairs)

    # Sort prioritized candidates: up to 12 shortest pairs, stable ID tiebreak
    prioritized_candidates = sorted(
        candidate_pairs,
        key=lambda p: (
            p["characters"],
            donor_id_sort_key(p["vulnerable_id"]),
            donor_id_sort_key(p["patched_candidate_id"]),
        ),
    )[:12]

    # Prepare donor index records (deterministic order by ID, no function body)
    donors_sorted = sorted(donors, key=lambda d: donor_id_sort_key(d["id"]))
    donor_index_records = []
    for d in donors_sorted:
        donor_index_records.append({
            "id": d["id"],
            "code_sha256": d["code_sha256"],
            "project": d["project"],
            "function_hint": d["function_hint"],
            "commit": d["commit_id"],
            "commit_id": d["commit_id"],
            "source_id": d["source_id"],
        })

    # Step 9: INTEGRITY VALIDATION COMPLETED. Now create output directory and materialize artifacts.
    try:
        os.makedirs(args.out, exist_ok=False)
    except Exception as e:
        sys.exit(f"Error creating output directory '{args.out}': {e}")

    candidate_pairs_path = os.path.join(args.out, "candidate_pairs.jsonl")
    donor_index_path = os.path.join(args.out, "donor_index.jsonl")
    prioritized_path = os.path.join(args.out, "prioritized_candidates.json")
    summary_path = os.path.join(args.out, "summary.json")

    # Write candidate_pairs.jsonl
    with open(candidate_pairs_path, "w", encoding="utf-8") as f:
        for p in candidate_pairs:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")

    # Write donor_index.jsonl
    with open(donor_index_path, "w", encoding="utf-8") as f:
        for d_rec in donor_index_records:
            f.write(json.dumps(d_rec, ensure_ascii=False) + "\n")

    # Write prioritized_candidates.json
    with open(prioritized_path, "w", encoding="utf-8") as f:
        json.dump(prioritized_candidates, f, indent=2, ensure_ascii=False)
        f.write("\n")

    # Step 10: Compute output SHA-256 for artifacts other than summary
    output_sha256 = {
        "candidate_pairs.jsonl": compute_file_sha256(candidate_pairs_path),
        "donor_index.jsonl": compute_file_sha256(donor_index_path),
        "prioritized_candidates.json": compute_file_sha256(prioritized_path),
    }

    input_sha256 = {
        "train_raw.jsonl": raw_file_sha256,
        "train_manifest.jsonl": manifest_file_sha256,
    }

    limitations = [
        "Candidate similarity is an unverified heuristic name match, NOT verified source patch identity.",
        "Candidate pairs are generated via combinatorial Cartesian product of same-name label 1 and label 0 functions within the same project; they are not confirmed before-after patch pairs.",
        "Function-name hint is derived from a simple regex on the pre-brace header, which may fail or select macro names on complex C/C++ declarations.",
        "No human review or verification has been performed; candidate pairs must not be treated as ground-truth patches.",
        "Candidate pairs carry status UNVERIFIED_NAME_MATCH_NOT_AN_ELIGIBLE_PAIR and must not be used in confirmatory benchmark tables without verified patch provenance.",
    ]

    summary_data = {
        "dataset": args.dataset,
        "raw_count": raw_count,
        "bank_count": bank_count,
        "candidate_count": candidate_count,
        "donors_missing_commit_id": donors_missing_commit_id,
        "same_commit_candidate_count": same_commit_candidate_count,
        "verified_pairs": 0,
        "reviewed_pairs": 0,
        "input_sha256": input_sha256,
        "output_sha256": output_sha256,
        "limitations": limitations,
    }

    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2, ensure_ascii=False)
        f.write("\n")


if __name__ == "__main__":
    main()
