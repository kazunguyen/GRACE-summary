"""Read-only re-audit of v2 artifacts; writes this independent directory only."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = ROOT / "Runs-management/b3_verified_patch_v1"
REL = BASE / "release_20261108_v2"


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def read(p):
    return json.loads(p.read_text(encoding="utf-8-sig"))


def rows(p):
    return [json.loads(x) for x in p.read_text(encoding="utf-8-sig").splitlines() if x.strip()]


def inventory():
    paths = []
    for folder in (BASE / "release_20261108", REL, BASE / "remediation_audit_20261108"):
        paths.extend(p for p in folder.rglob("*") if p.is_file())
    paths.extend((ROOT / "scripts").glob("b3_step*.py"))
    paths.extend([ROOT / "tests/test_amended_b3.py", ROOT / "CHANGES_AFTER_PREREG.md"])
    paths.extend((ROOT / "Runs-management/b3_amended_20261106" / x)
                 for x in ("synthetic_smoke_prompts.json", "synthetic_smoke_preview.txt", "check_b3.py"))
    return {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(set(paths))}


def main():
    if (OUT / "state_check.json").exists():
        raise FileExistsError("Use a new audit directory")
    before = inventory()
    (OUT / "source_inventory.json").write_text(json.dumps(before, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result = {"checked_at_utc": datetime.now(timezone.utc).isoformat(), "seals": {}}
    previous = read(BASE / "independent_audit_20261108_122320/submitted_artifact_hashes.json")
    original = {k: v for k, v in previous.items() if k.startswith("Runs-management/b3_verified_patch_v1/release_20261108/")}
    changed = [k for k, v in original.items() if sha(ROOT / k) != v]
    result["v1_preservation"] = {"files": len(original), "changed": changed}
    for path, field in [("inputs_manifest.json", "seal_sha256"),
                        ("pools/pool_manifest.json", "manifest_seal_sha256"),
                        ("validation/validation_prompt_manifest.json", "prompt_manifest_seal_sha256")]:
        d = read(REL / path)
        body = {k: v for k, v in d.items() if k != field}
        actual = hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False, indent=2).encode()).hexdigest()
        result["seals"][path] = {"stored": d[field], "calculated": actual, "match": actual == d[field]}
    inputs = read(REL / "inputs_manifest.json")
    result["source_hashes"] = {}
    for section in ("modules_sha256", "execution_scripts_sha256", "authority_documents_sha256"):
        refs = inputs.get(section, {})
        result["source_hashes"][section] = {"entries": len(refs), "mismatches": [k for k, v in refs.items() if sha(ROOT / k) != v]}
    tok = ROOT / inputs["tokenizer"]["path"]
    result["tokenizer_hashes_pass"] = all(sha(tok / k) == v for k, v in inputs["tokenizer"]["files_sha256"].items())
    freeze = ROOT / "01_Author_Baseline_Unified/output/research_freeze_20261101"
    result["freeze_manifest_hash_pass"] = sha(freeze / "freeze_manifest.json") == "e1d3c6b17c3a0b5c1e05203794d48a33825e0ea00a55deaaef565af25efe0448"
    f = read(freeze / "freeze_manifest.json")
    result["freeze_file_hashes_pass"] = all(sha(freeze / ds / k) == v for ds, d in f["datasets"].items() for k, v in d["files_sha256"].items())
    result["human_review_count"] = len(rows(REL / "reviews/review_ledger.jsonl"))
    triage = rows(REL / "reviews/triage_ledger.jsonl")
    result["triage"] = dict(Counter(r["status"] for r in triage))
    result["all_triage_labeled_automated"] = all(r["evaluation_type"] == "AUTOMATED_TECHNICAL_TRIAGE" for r in triage)
    result["pool_counts"] = {ds: len(rows(REL / f"pools/eligible_pairs.{ds}.jsonl")) for ds in ("devign", "reveal")}
    recon = REL / "discovery/devign/source_recon"
    logs = rows(recon / "request_log.jsonl")
    result["source_request_sources"] = dict(Counter(r.get("source") for r in logs))
    result["cached_responses_pass"] = all(
        sha(recon / "cache" / (r["url"].rsplit("/", 1)[-1] + ".json")) == r["sha256"]
        and read(recon / "cache" / (r["url"].rsplit("/", 1)[-1] + ".json"))["sha"] == r["url"].rsplit("/", 1)[-1]
        for r in logs)
    cases = [read(p) for p in (REL / "source_archive/devign").glob("case_*/case_manifest.json")]
    result["source_cases"] = {"count": len(cases), "both_responses": sum(r["source_investigation"].get("has_both_commit_responses", False) for r in cases)}
    result["packet_hashes_pass"] = True
    for p in (REL / "review_packets").glob("case_*.json"):
        if p.name.endswith("_review_form_template.json"):
            continue
        d = read(p)
        actual = hashlib.sha256(json.dumps({k: v for k, v in d.items() if k != "payload_sha256"}, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()
        result["packet_hashes_pass"] &= actual == d["payload_sha256"]
    manifest = read(REL / "validation/validation_prompt_manifest.json")
    result["validation"] = {}
    with ZipFile(ROOT / "Runs-management/grace_15arms_prompts_and_clean_specs.zip") as z:
        for ds in ("devign", "reveal"):
            census_path = REL / f"validation/{ds}/validation_census.jsonl"
            c = rows(census_path)
            specs = {r["id"]: r for r in [json.loads(x) for x in z.read(f"specs/{ds}_validation_15arms.jsonl").splitlines() if x.strip()]}
            raw = {r["id"]: r for r in rows(freeze / ds / "validation_raw.jsonl")}
            result["validation"][ds] = {
                "rows": len(c), "unique_ids": len({r["target_id"] for r in c}),
                "ID_set_pass": {r["target_id"] for r in c} == set(specs) == set(raw),
                "code_hashes_pass": all(r["query_code_sha256"] == hashlib.sha256(specs[r["target_id"]]["query_code"].strip().encode()).hexdigest() == hashlib.sha256(raw[r["target_id"]]["func"].strip().encode()).hexdigest() for r in c),
                "census_hash_pass": sha(census_path) == manifest["datasets"][ds]["census_sha256"],
                "paused": sum(r["status"] == "PAUSED" for r in c),
                "nonempty_prompts": sum(bool(r.get("prompt")) for r in c),
                "null_flags_on_null_prompts": all(r.get("figure6_order_compliant") is None and r.get("target_label_in_prompt") is None for r in c if r.get("prompt") is None)}
    result["source_inventory_unchanged_during_check"] = inventory() == before
    (OUT / "state_check.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
