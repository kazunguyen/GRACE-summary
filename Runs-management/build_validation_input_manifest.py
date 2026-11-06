
"""Inventory and validate the exact local GRACE validation inputs without inference."""
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "grace_15arms_prompts_and_clean_specs"
RUNS = ROOT / "Runs-management"
DRY = RUNS / "dry_run_validation_20261102"
BASE = ROOT / "01_Author_Baseline_Unified/output"
FREEZE = BASE / "research_freeze_20261101"
ARMS = (
    "B0", "B1", "B2", "B2-flip", "B2-rep", "B2-rand", "B2-nolabel",
    "B2-labelonly", "B1-shuf", "B1-full", "B1-H2", "B3", "B3-nodiff",
    "B3-swap", "B3-flip",
)
EXTENSIONS = {"B1-H2", "B3", "B3-nodiff", "B3-swap", "B3-flip"}


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def rows(path):
    with path.open(encoding="utf-8-sig") as stream:
        for line in stream:
            if line.strip():
                yield json.loads(line)


def artifact(path):
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path)}


def audit_dataset(dataset, expected):
    frozen = FREEZE / dataset / "validation_raw.jsonl"
    expected_hash = read(FREEZE / "freeze_manifest.json")["datasets"][dataset]["files_sha256"]["validation_raw.jsonl"]
    if sha(frozen) != expected_hash:
        raise ValueError(f"Frozen validation hash mismatch for {dataset}")
    ids = {row["id"] for row in rows(frozen)}
    if len(ids) != expected:
        raise ValueError(f"Unexpected frozen ID count for {dataset}")
    cache = RUNS / "donor_reconciliation_20261101/cache" / f"{dataset}_new_bank.jsonl"
    proof = RUNS / "donor_reconciliation_20261101" / f"{dataset}_retrieval_provenance.json"
    if sha(cache) != read(proof)["new"]["cache_sha256"]:
        raise ValueError(f"Donor bank hash mismatch for {dataset}")
    bank = {row["id"]: (row["func"].strip(), int(row["target"])) for row in rows(cache)}
    packaged_specs = PACKAGE / "specs" / f"{dataset}_validation_15arms.jsonl"
    spec_pairs = {}
    bad_spec_donors = 0
    for row in rows(packaged_specs):
        uid = row.get("original_id", row["id"])
        if uid in spec_pairs:
            raise ValueError(f"Duplicate packaged spec {uid}")
        spec_pairs[uid] = [demo["function_uid"] for demo in row["demonstrations_pair"]]
        for field in ("demonstrations", "demonstrations_pair"):
            for demo in row[field]:
                bad_spec_donors += bank.get(demo["function_uid"]) != (
                    demo["func"].strip(), int(demo["target"]),
                )
    if spec_pairs.keys() != ids or bad_spec_donors:
        raise ValueError(f"Packaged spec ID or donor mismatch for {dataset}")

    entries = []
    b2_hashes = {}
    for arm in ARMS:
        for seed in ((42, 43, 44) if arm in {"B1-shuf", "B2-rand"} else (42,)):
            rel = Path(dataset) / "validation" / arm / str(seed)
            origin = DRY / rel
            prompt = origin / "prompts.jsonl"
            if arm in EXTENSIONS:
                prompt = PACKAGE / "prompts" / DRY.name / rel / prompt.name
            if arm == "B2":
                prompt = PACKAGE / "prompts/reference_B2" / dataset / "validation/prompts.jsonl"
            metadata = read(origin / "manifest.json")
            audit = read(origin / "audit_summary.json")
            prompt_artifact = artifact(prompt)
            if arm == "B2":
                ref = RUNS / "donor_reconciliation_20261101/new_reference/B2" / dataset / "validation/prompts.jsonl"
                if sha(ref) != prompt_artifact["sha256"]:
                    raise ValueError(f"B2 reference copy differs for {dataset}")
            elif prompt_artifact["sha256"] != metadata["prompts_sha256"] or prompt_artifact["sha256"] != audit["prompts_sha256"]:
                raise ValueError(f"Source prompt hash mismatch for {rel}")

            seen = set()
            counts = Counter()
            outside = Counter()
            for row in rows(prompt):
                uid = row["id"]
                digest = hashlib.sha256(row["prompt"].encode("utf-8")).hexdigest()
                if uid in seen or digest != row["prompt_sha256"]:
                    raise ValueError(f"Duplicate ID or prompt text hash mismatch in {rel}: {uid}")
                if row.get("dataset") != dataset or row.get("split") != "validation" or row.get("arm") != arm or row.get("seed", 42) != seed:
                    raise ValueError(f"Prompt identity mismatch in {rel}: {uid}")
                seen.add(uid)
                evidence = row.get("evidence", {})
                if arm == "B2":
                    b2_hashes[uid] = digest
                    counts["donor_id_outside_frozen_bank"] += sum(demo not in bank for demo in row["demo_ids"])
                if arm == "B2-rep" and (digest != b2_hashes[uid] or not evidence.get("repeat")):
                    raise ValueError(f"B2-rep pairing mismatch: {uid}")
                if arm == "B1-H2":
                    counts["no_guarded_sink_message"] += "No guarded sink evidence detected." in row["prompt"]
                if arm.startswith("B3"):
                    demos = evidence["demo"]["demos"]
                    if len(demos) != 2 or {demo["true_label"] for demo in demos} != {0, 1}:
                        raise ValueError(f"Invalid contrastive pair in {rel}: {uid}")
                    ordered = list(reversed(demos)) if arm == "B3-swap" else demos
                    counts["same_pair_ids_as_packaged_specs"] += (
                        [demo["function_uid"] for demo in ordered] == spec_pairs[uid]
                    )
                    for demo in demos:
                        key = demo["function_uid"]
                        if key not in bank:
                            outside[key] += 1
                        elif bank[key][1] != demo["true_label"]:
                            raise ValueError(f"Frozen donor label mismatch in {rel}: {key}")
            if seen != ids:
                raise ValueError(f"Validation coverage mismatch in {rel}")
            if arm == "B2" and counts["donor_id_outside_frozen_bank"]:
                raise ValueError(f"Frozen B2 donor mismatch in {rel}")

            blockers = []
            if arm == "B1-H2":
                blockers.append("H2 pipeline evidence provenance is not established for this artifact.")
            if arm.startswith("B3"):
                blockers.append("Packaged specs and rendered pair IDs do not reconcile.")
                if outside:
                    blockers.append("Rendered donor IDs require frozen-bank reconciliation.")
            if arm in EXTENSIONS:
                blockers.append("No completed two-reviewer audit covers this extension.")
            if audit["rate_demo_empty"] > 0.01 or audit["rate_graph_missing"] > 0.05 or audit["n_label_leak"]:
                blockers.append("Source automatic audit exceeds a protocol stop threshold.")

            entries.append({
                "dataset": dataset, "split": "validation", "arm": arm, "seed": seed,
                "rows": len(seen), "prompt": prompt_artifact,
                "source_manifest": artifact(origin / "manifest.json"),
                "source_audit": artifact(origin / "audit_summary.json"),
                "source_audit_metrics": {
                    key: audit.get(key) for key in (
                        "status", "rate_demo_empty", "rate_graph_missing", "n_label_leak",
                        "tokens_p50", "tokens_p95", "any_approx_tokens",
                    )
                },
                "audit_counts": dict(counts),
                "rendered_donor_occurrences_outside_frozen_id_namespace": sum(outside.values()),
                "distinct_rendered_donor_ids_outside_frozen_id_namespace": len(outside),
                "blocked_reasons": blockers,
                "repeat_response_cache_tag": "repeat" if arm == "B2-rep" else None,
            })
    print(f"{dataset}: {len(entries)} verified file identities", flush=True)
    return {
        "dataset": dataset, "frozen_validation": artifact(frozen),
        "ids": sorted(ids), "donor_bank": artifact(cache),
        "donor_retrieval_provenance": artifact(proof),
        "packaged_specs": artifact(packaged_specs),
        "packaged_specs_are_not_render_provenance": True,
        "inputs": entries,
    }



def assemble_candidate(candidate_path, output_path=None):
    inventory_path = PACKAGE / "validation_input_manifest.json"
    inventory = read(inventory_path)
    candidate = read(candidate_path)
    if candidate["source_inventory"] != artifact(inventory_path):
        raise ValueError("Candidate source inventory changed")
    replacements = {
        (item["dataset"], item["arm"], item["seed"]): item
        for item in candidate["input_sets"]
    }
    expected = {(dataset["dataset"], arm, 42) for dataset in inventory["datasets"] for arm in EXTENSIONS}
    if len(candidate["input_sets"]) != len(expected) or replacements.keys() != expected:
        raise ValueError("Candidate set identity mismatch")
    for dataset in inventory["datasets"]:
        for entry in dataset["inputs"]:
            replacement = replacements.get((entry["dataset"], entry["arm"], entry["seed"]))
            if replacement is None:
                continue
            if replacement["rows"] != entry["rows"] or replacement["split"] != "validation":
                raise ValueError("Candidate count or split mismatch")
            entry["prior_prompt"] = entry["prompt"]
            entry["prompt"] = replacement["prompt"]
            if artifact(ROOT / entry["prompt"]["path"]) != entry["prompt"]:
                raise ValueError("Candidate prompt changed")
            entry.pop("source_manifest")
            entry.pop("source_audit")
            entry.pop("source_audit_metrics")
            entry.pop("audit_counts")
            entry.pop("rendered_donor_occurrences_outside_frozen_id_namespace")
            entry.pop("distinct_rendered_donor_ids_outside_frozen_id_namespace")
            entry["candidate_audit"] = replacement
            entry["blocked_reasons"] = ["Awaiting two independent reviewers."]
            if not replacement["automatic_audit_pass"]:
                entry["blocked_reasons"].append("Automatic audit has unresolved findings.")
    inventory.update(
        schema="grace_validation_candidate_input_manifest_v1",
        scope="All 38 validation input sets, including 10 replacement candidates pending acceptance.",
        candidate_manifest=artifact(candidate_path),
        source_inventory=artifact(inventory_path),
    )
    dest = output_path or PACKAGE / "validation_candidate_manifest.json"
    if dest.parent != PACKAGE:
        raise ValueError("Candidate manifest must be written inside the validation package")
    temp = dest.with_suffix(".tmp")
    temp.write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(dest)
    print(dest, flush=True)


def main():
    datasets = [audit_dataset(dataset, count) for dataset, count in (("devign", 2732), ("reveal", 2273))]
    entries = [entry for dataset in datasets for entry in dataset["inputs"]]
    result = {
        "schema": "grace_validation_input_inventory_v1",
        "scope": "Local prompt identity and coverage; this inventory does not authorize inference.",
        "protocol": artifact(ROOT / "configs/protocol.yaml"),
        "arms_config": artifact(ROOT / "configs/arms.yaml"),
        "thresholds_reference": artifact(ROOT / "configs/thresholds.json"),
        "backend_smoke_manifest": artifact(RUNS / "step1_backend_smoke/backend_manifest.json"),
        "renderer_source_hash_record": artifact(DRY / "source_hashes.json"),
        "frozen_snapshot_manifest": artifact(FREEZE / "freeze_manifest.json"),
        "total_sets": len(entries),
        "total_prompt_rows": sum(entry["rows"] for entry in entries),
        "blocked_sets": sum(bool(entry["blocked_reasons"]) for entry in entries),
        "datasets": datasets,
    }
    dest = PACKAGE / "validation_input_manifest.json"
    temp = dest.with_suffix(".tmp")
    temp.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(dest)
    print(dest, result["total_sets"], result["total_prompt_rows"], result["blocked_sets"], flush=True)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path)
    parser.add_argument("--output", type=Path, help="Output manifest inside the validation package")
    args = parser.parse_args()
    if args.candidate:
        assemble_candidate(args.candidate.resolve(), args.output.resolve() if args.output else None)
    else:
        main()

