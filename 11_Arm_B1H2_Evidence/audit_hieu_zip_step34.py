
"""Re-audit validation inputs against the original Hieu ZIP without changing it."""
import csv
import hashlib
import io
import json
import sys
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
ARM = ROOT / "11_Arm_B1H2_Evidence"
RUNS = ROOT / "Runs-management"
sys.path.insert(0, str(RUNS))
from audit_prompt_integrity import make_manual, split_prompt
from build_validation_input_manifest import ROOT, RUNS, FREEZE, artifact, read, rows, sha
from dry_run_full_validation import BUDGET, REV, resolve_hits
from grace_diag.prompt_audit import audit_rows

ZIP = ROOT / "grace_15arms_prompts_and_clean_specs.zip"
OUT = ARM / "audit/hieu_zip_step34_20261104"
DRY = RUNS / "dry_run_validation_20261102"
REVIEW = RUNS / "prompt_audit_20261102"
H2 = ARM / "validation_h2_cluster_v5_20261104"
B3 = ("B3", "B3-nodiff", "B3-swap", "B3-flip")


def dump(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def zip_rows(archive, path):
    with archive.open(path) as stream:
        for line in io.TextIOWrapper(stream, encoding="utf-8-sig"):
            if line.strip():
                yield json.loads(line)


def source_files(archive):
    initial = read(ROOT / "worklogs/2026-11-04_goi_hieu_baseline_sha256.json")
    known = {row["relative_path"]: row["sha256"] for row in initial["entries"]}
    names = [info.filename for info in archive.infolist() if not info.is_dir()]
    if len(names) != 20 or set(names) != known.keys():
        raise ValueError("ZIP member inventory differs from the first observed local package")
    found = []
    for name in sorted(names):
        with archive.open(name) as stream:
            actual = hashlib.file_digest(stream, "sha256").hexdigest()
        if actual != known[name]:
            raise ValueError(f"ZIP member differs from initial local file: {name}")
        found.append({"member": name, "sha256": actual, "bytes": archive.getinfo(name).file_size})
    return found


def zip_materialize(archive, member, files):
    path = OUT / "zip_validation" / member
    path.parent.mkdir(parents=True, exist_ok=True)
    with archive.open(member) as src, path.open("xb") as dest:
        while data := src.read(1024 * 1024):
            dest.write(data)
    if sha(path) != files[member]:
        raise ValueError(f"Restored member differs: {member}")
    return path


def review_coverage():
    def marks(name):
        with (REVIEW / name).open(encoding="utf-8-sig", newline="") as stream:
            return {r["audit_key"]: r for r in csv.DictReader(stream) if r["overall_verdict"]}
    first, second = marks("reviewer_1.csv"), marks("reviewer_2.csv")
    if set(first) != set(second):
        raise ValueError("Reviewer packet coverage differs")
    return {
        (r["dataset"], r["arm"], int(r["seed"]), r["id"], r["prompt_sha256"])
        for key, r in first.items() if r["split"] == "validation"
        and r["prompt_sha256"] == second[key]["prompt_sha256"]
    }


def check_set(path, dataset, arm, seed, expected, bank, reviewed, candidates, details=None):
    metrics = Counter()
    hash_by_id = {}
    for row in rows(path):
        uid = row["id"]
        text = row["prompt"]
        actual = digest(text)
        if uid in hash_by_id or actual != row["prompt_sha256"]:
            raise ValueError(f"Duplicate ID or bad prompt hash: {dataset} {arm} {uid}")
        if (row["dataset"], row["split"], row["arm"], row.get("seed", 42)) != (dataset, "validation", arm, seed):
            raise ValueError(f"Unexpected row identity for {uid}")
        hash_by_id[uid] = actual
        evidence = row["evidence"]
        tokens = evidence["tokens"]
        demos = evidence["demo"].get("demos", [])
        if (
            tokens["approx"] or tokens["total"] + BUDGET["reserve"] > BUDGET["total"]
            or tokens["code"] > BUDGET["target_code"] or tokens["graph"] > BUDGET["graph"]
            or any(d.get("tokens", 0) > BUDGET["demo"] for d in demos)
        ):
            metrics["budget_violations"] += 1
        if evidence["prompt_sha256"] != actual:
            raise ValueError(f"Evidence hash mismatch for {uid}")
        for demo in demos:
            did = demo["function_uid"]
            metrics["donor_id_not_in_frozen_bank"] += did not in bank
            if did in bank and "true_label" in demo and demo["true_label"] != bank[did]:
                metrics["wrong_donor_labels"] += 1
        if arm == "B2-rep" and not evidence.get("repeat"):
            metrics["repeat_flag_missing"] += 1
        _, open_hits = resolve_hits(text)
        metrics["unresolved_label_prompts"] += bool(open_hits)
        metrics["historically_reviewed_exact_prompts"] += (dataset, arm, seed, uid, actual) in reviewed
        flat = audit_rows([row])["rows"][0]
        for key in ("demo_empty", "graph_missing", "code_truncated", "graph_truncated", "demo_truncated"):
            metrics[key] += flat[key]
        if details is not None:
            details[uid] = {
                "demos": [d["function_uid"] for d in demos],
                "h2": evidence.get("h2"),
                "hash": actual,
                "generic": "Key difference: Differences in bounds validation conditions and control flow constraints" in text,
            }
        candidates.append({
            **flat, "dataset": dataset, "split": "validation", "phase": "hieu_zip_step34",
            "audit_key": f"{dataset}/validation/{arm}/{seed}/{uid}",
            "prompt_source": path.relative_to(ROOT).as_posix(),
        })
    if hash_by_id.keys() != expected:
        raise ValueError(f"Frozen validation coverage mismatch: {dataset} {arm} seed {seed}")
    count = len(hash_by_id)
    result = {
        "dataset": dataset, "split": "validation", "arm": arm, "seed": seed,
        "rows": count, "prompt": artifact(path), "checks": dict(metrics),
        "empty_demo_rate": metrics["demo_empty"] / count,
        "missing_graph_rate": metrics["graph_missing"] / count,
        "passes_prereg_automatic_thresholds": (
            metrics["demo_empty"] / count <= .01 and metrics["graph_missing"] / count <= .05
            and not metrics["unresolved_label_prompts"] and not metrics["budget_violations"]
        ),
    }
    return result, hash_by_id


def audit_dataset(archive, dataset, files, reviewed, candidates):
    snapshot = read(FREEZE / "freeze_manifest.json")
    raw = FREEZE / dataset / "validation_raw.jsonl"
    if sha(raw) != snapshot["datasets"][dataset]["files_sha256"]["validation_raw.jsonl"]:
        raise ValueError(f"Frozen split hash differs for {dataset}")
    ids = {row["id"] for row in rows(raw)}
    donor_dir = RUNS / "donor_reconciliation_20261101"
    bank_file = donor_dir / "cache" / f"{dataset}_new_bank.jsonl"
    donor_proof = read(donor_dir / f"{dataset}_retrieval_provenance.json")
    if sha(bank_file) != donor_proof["new"]["cache_sha256"]:
        raise ValueError(f"Frozen bank hash differs for {dataset}")
    bank = {r["id"]: int(r["target"]) for r in rows(bank_file)}
    results = []
    selected = [e for e in read(DRY / "final_status.json")["sets"] if e["dataset"] == dataset]
    ref_member = f"prompts/reference_B2/{dataset}/validation/prompts.jsonl"
    b2_file = zip_materialize(archive, ref_member, files)
    reference = {r["id"]: r["prompt_sha256"] for r in rows(b2_file)}
    b2_ids = {r["id"]: r["demo_ids"] for r in rows(b2_file)}
    if reference.keys() != ids or any(d not in bank for donors in b2_ids.values() for d in donors):
        raise ValueError(f"ZIP B2 donor or ID mismatch: {dataset}")
    for e in selected:
        arm, seed = e["arm"], e["seed"]
        src = DRY / dataset / "validation" / arm / str(seed) / "prompts.jsonl"
        src_meta = read(src.with_name("manifest.json"))
        if sha(src) != src_meta["prompts_sha256"]:
            raise ValueError(f"Dry-run manifest mismatch: {src}")
        result, hashes = check_set(src, dataset, arm, seed, ids, bank, reviewed, candidates)
        if arm in {"B2", "B2-rep"} and reference != hashes:
            raise ValueError(f"{arm} prompt text differs from ZIP B2 in {dataset}")
        result["blockers"] = []
        if not result["passes_prereg_automatic_thresholds"]:
            result["blockers"].append("Automatic audit stop criterion failed.")
        if any(result["checks"].get(k) for k in (
            "donor_id_not_in_frozen_bank", "wrong_donor_labels", "repeat_flag_missing",
        )):
            result["blockers"].append("Frozen donor or repeat contract mismatch.")
        result["historical_dry_run_status"] = e["final_status"]
        if arm == "B2":
            result["zip_reference"] = artifact(b2_file)
            result["prompt_identity_to_zip"] = "exact_text_by_validation_id"
        results.append(result)

    old_specs = f"specs/{dataset}_validation_15arms.jsonl"
    pair_ids = {}
    for row in zip_rows(archive, old_specs):
        uid = row.get("original_id", row["id"])
        if uid in pair_ids:
            raise ValueError(f"Duplicate ZIP spec ID {uid}")
        pair_ids[uid] = [d["function_uid"] for d in row["demonstrations_pair"]]
    if pair_ids.keys() != ids:
        raise ValueError(f"ZIP specs validation ID mismatch for {dataset}")
    for arm in B3:
        member = f"prompts/dry_run_validation_20261102/{dataset}/validation/{arm}/42/prompts.jsonl"
        src = zip_materialize(archive, member, files)
        detail = {}
        result, _ = check_set(src, dataset, arm, 42, ids, bank, reviewed, candidates, detail)
        result["same_pair_ids_as_zip_specs"] = sum(
            (d["demos"][::-1] if arm == "B3-swap" else d["demos"]) == pair_ids[uid]
            for uid, d in detail.items()
        )
        result["generic_difference_rows"] = sum(d["generic"] for d in detail.values())
        result["blockers"] = [
            "ZIP rendered donor identity disagrees with ZIP specs; frozen original full-selection provenance is unresolved.",
        ]
        results.append(result)
    h2 = H2 / dataset / "validation/B1-H2/42/prompts.jsonl"
    detail = {}
    result, _ = check_set(h2, dataset, "B1-H2", 42, ids, bank, reviewed, candidates, detail)
    result["h2_no_usable_guard"] = sum(d["h2"]["no_usable_evidence"] for d in detail.values())
    result["h2_nodes_outside_closed_prefix"] = sum(
        d["h2"]["nodes_outside_closed_prefix"] > 0 for d in detail.values()
    )
    result["blockers"] = ["Current evidence review is incomplete; prefix-selection scope must match the submitted protocol."]
    results.append(result)
    print(dataset, len(results), flush=True)
    return results


def main():
    OUT.mkdir(exist_ok=False)
    candidates = []
    with ZipFile(ZIP) as archive:
        files = source_files(archive)
        by_name = {x["member"]: x["sha256"] for x in files}
        dump(OUT / "zip_inventory.json", {"zip": artifact(ZIP), "members": files, "matches_initial_local_files": 20})
        reviewed = review_coverage()
        inputs = [item for dataset in ("devign", "reveal")
                  for item in audit_dataset(archive, dataset, by_name, reviewed, candidates)]
    make_manual(OUT, candidates)
    ready = [e for e in inputs if not e["blockers"]]
    audit = {
        "schema": "grace_hieu_zip_step34_audit_v1", "split": "validation", "allow_test": False,
        "original_zip": artifact(ZIP), "zip_inventory": artifact(OUT / "zip_inventory.json"),
        "protocol": artifact(ROOT / "configs/protocol.yaml"),
        "preregistration": artifact(ROOT / "preregistration.md"),
        "backend_smoke_manifest": artifact(RUNS / "step1_backend_smoke/backend_manifest.json"),
        "tokenizer_revision": REV, "budget": BUDGET,
        "manual_sample": artifact(OUT / "manual_sample.jsonl"),
        "formal_two_reviewer_status": "Historical reviewed sample has exact matches in scope; new 60-prompt packet awaits independent review.",
        "osf_submission": "Submitted according to user; submitted artifact identity not verified locally.",
        "total_sets": len(inputs), "total_rows": sum(e["rows"] for e in inputs),
        "technical_validation_sets": len(ready), "inputs": inputs,
    }
    dump(OUT / "audit_manifest.json", audit)
    dump(OUT / "validation_only_inputs.json", {
        "schema": "grace_validation_only_input_list_v1", "allow_test": False,
        "scope": "Technical input checks passed. See audit_manifest for study acceptance and reviewer scope.",
        "audit_manifest": artifact(OUT / "audit_manifest.json"),
        "backend_smoke_manifest": audit["backend_smoke_manifest"],
        "tokenizer_revision": REV, "sets": ready,
    })
    print(len(inputs), len(ready), sum(e["rows"] for e in ready), flush=True)


if __name__ == "__main__":
    main()
