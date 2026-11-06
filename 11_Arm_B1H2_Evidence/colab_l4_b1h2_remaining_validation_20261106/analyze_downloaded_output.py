from __future__ import annotations

import hashlib
import json
import math
import statistics
import zipfile
from collections import Counter
from pathlib import Path


base = Path(__file__).parent
bundle_path = base / "bundles" / "b1h2_l4_remaining_validation_bundle.zip"
output_path = base / "downloaded_output" / "l4_remaining_validation_output.zip"


def read_jsonl(raw: bytes) -> list[dict]:
    return [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]


with zipfile.ZipFile(bundle_path) as z:
    manifest = json.loads(z.read("bundle_manifest.json"))
    prompts_raw = z.read("prompts.jsonl")
    prompts = read_jsonl(prompts_raw)

with zipfile.ZipFile(output_path) as z:
    members = z.namelist()
    records_member = next((name for name in members if name.endswith("records.jsonl")), None)
    if records_member is None:
        raise ValueError(f"No records.jsonl in output: {members}")
    records = read_jsonl(z.read(records_member))
    json_members = {name.rsplit("/", 1)[-1]: name for name in members if name.endswith(".json")}
    status = json.loads(z.read(json_members["pilot_status.json"])) if "pilot_status.json" in json_members else None
    load_summary = json.loads(z.read(json_members["load_summary.json"])) if "load_summary.json" in json_members else None
    events = z.read("events.log").decode("utf-8", errors="replace") if "events.log" in members else ""

prompt_by_id = {row["id"]: row for row in prompts}
record_by_id = {row["id"]: row for row in records}
duplicate_ids = len(records) - len(record_by_id)
missing = sorted(set(prompt_by_id) - set(record_by_id))
extra = sorted(set(record_by_id) - set(prompt_by_id))
hash_mismatches = [
    sample_id
    for sample_id in set(prompt_by_id) & set(record_by_id)
    if prompt_by_id[sample_id]["prompt_sha256"] != record_by_id[sample_id].get("prompt_sha256")
]
raw_counts = Counter(str(row.get("raw")) for row in records)
response_invalid = [row for row in records if row.get("response_valid") is False]
bad_scores = [
    row["id"]
    for row in records
    if any(not isinstance(row.get(key), (int, float)) or not math.isfinite(row[key]) for key in ("logprob_0", "logprob_1", "s"))
]
elapsed = [float(row["elapsed_s"]) for row in records if isinstance(row.get("elapsed_s"), (int, float))]
dataset_counts = Counter(row.get("dataset") for row in records)
arm_counts = Counter(row.get("arm") for row in records)
gpu_counts = Counter(row.get("gpu") for row in records)

report = {
    "output_zip": output_path.name,
    "output_zip_bytes": output_path.stat().st_size,
    "output_zip_sha256": hashlib.sha256(output_path.read_bytes()).hexdigest(),
    "output_members": members,
    "bundle_manifest_count": manifest["count"],
    "bundle_prompt_sha256": manifest["prompts_sha256"],
    "source_archive_sha256": manifest["source_archive_sha256"],
    "records_count": len(records),
    "unique_records": len(record_by_id),
    "duplicate_ids": duplicate_ids,
    "missing_ids_count": len(missing),
    "extra_ids_count": len(extra),
    "prompt_hash_mismatch_count": len(hash_mismatches),
    "invalid_response_count": len(response_invalid),
    "raw_response_counts": dict(raw_counts),
    "bad_score_count": len(bad_scores),
    "dataset_counts": dict(dataset_counts),
    "arm_counts": dict(arm_counts),
    "gpu_counts": dict(gpu_counts),
    "elapsed_s_mean": statistics.mean(elapsed) if elapsed else None,
    "elapsed_s_median": statistics.median(elapsed) if elapsed else None,
    "elapsed_s_max": max(elapsed) if elapsed else None,
    "status": status,
    "load_summary": load_summary,
    "last_event_lines": events.splitlines()[-8:],
    "missing_id_examples": missing[:10],
    "extra_id_examples": extra[:10],
    "hash_mismatch_examples": hash_mismatches[:10],
    "invalid_response_examples": [
        {key: row.get(key) for key in ("id", "raw", "s", "response_valid")}
        for row in response_invalid[:10]
    ],
}

report_path = base / "output_analysis.json"
report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2, ensure_ascii=False))
