"""Independent read-only audit of the submitted B3 preparation release.

Only writes this audit directory. Does not run the eight release builders,
contact a service, fabricate review decisions, or modify the submitted release.
"""
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RELEASE = ROOT / "Runs-management/b3_verified_patch_v1/release_20261108"
FREEZE = ROOT / "01_Author_Baseline_Unified/output/research_freeze_20261101"


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def rows(path):
    with Path(path).open(encoding="utf-8-sig") as f:
        return [json.loads(line) for line in f if line.strip()]


def seal(path, field):
    obj = read(path)
    unsigned = {k: v for k, v in obj.items() if k != field}
    calculated = digest(json.dumps(unsigned, sort_keys=True, ensure_ascii=False, indent=2))
    return {"stored": obj[field], "calculated": calculated, "matches": obj[field] == calculated}


def source_inventory():
    paths = list(RELEASE.rglob("*"))
    paths += list((ROOT / "scripts").glob("b3_step*.py"))
    paths += [ROOT / "Runs-management/b3_amended_20261106/check_b3.py",
              ROOT / "CHANGES_AFTER_PREREG.md"]
    return {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(paths) if p.is_file()}


def main():
    if (OUT / "audit.json").exists():
        raise FileExistsError("Preserve previous independent audit")
    before = source_inventory()
    (OUT / "submitted_artifact_hashes.json").write_text(
        json.dumps(before, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result = {"checked_at_utc": datetime.now(timezone.utc).isoformat(),
              "scope": "Local evidence, all clean donors and full validation census; no inference",
              "submitted_files_hashed": len(before)}
    inputs = read(RELEASE / "inputs_manifest.json")
    freeze = read(FREEZE / "freeze_manifest.json")
    result["seals"] = {
        "inputs": seal(RELEASE / "inputs_manifest.json", "seal_sha256"),
        "pool": seal(RELEASE / "pools/pool_manifest.json", "manifest_seal_sha256"),
        "validation_census": seal(RELEASE / "validation/validation_prompt_manifest.json",
                                  "prompt_manifest_seal_sha256"),
    }
    result["freeze_manifest_hash_pass"] = sha(FREEZE / "freeze_manifest.json") == inputs["freeze_manifest"]["sha256"] == "e1d3c6b17c3a0b5c1e05203794d48a33825e0ea00a55deaaef565af25efe0448"
    result["freeze_file_hashes"] = {
        ds + "/" + name: sha(FREEZE / ds / name) == expected
        for ds, entry in freeze["datasets"].items()
        for name, expected in entry["files_sha256"].items()
    }
    result["module_hashes"] = {name: sha(ROOT / name) == expected
                               for name, expected in inputs["modules_sha256"].items()}
    tokdir = ROOT / inputs["tokenizer"]["path"]
    result["tokenizer_file_hashes"] = {name: sha(tokdir / name) == expected
                                      for name, expected in inputs["tokenizer"]["files_sha256"].items()}
    banks, validations = {}, {}
    result["banks"] = {}
    for ds in ("devign", "reveal"):
        raw = rows(FREEZE / ds / "train_raw.jsonl")
        metas = rows(FREEZE / ds / "train_manifest.jsonl")
        meta = {r["id"]: r for r in metas}
        kept = [r for r in raw if meta[r["id"]]["keep_in_bank"]]
        banks[ds] = {r["id"]: r for r in kept}
        groups = defaultdict(Counter)
        for r in kept:
            names = re.findall(r"([A-Za-z_]\w*)\s*\(", r["func"].split("{", 1)[0])
            if names:
                groups[r.get("project"), names[0]][r["target"]] += 1
        result["banks"][ds] = {
            "clean_donors": len(kept),
            "unique_clean_ids": len(banks[ds]),
            "raw_ids_unique": len(raw) == len({r["id"] for r in raw}),
            "manifest_ids_unique": len(metas) == len(meta),
            "membership_labels_code_hashes_pass": all(
                r["split"] == "train" and r["dataset"] == ds
                and r["target"] == meta[r["id"]]["label"]
                and digest(r["func"]) == meta[r["id"]]["code_sha256"] for r in kept),
            "missing_commit_ids": sum(not r.get("commit_id") for r in kept),
            "heuristic_combinations": sum(c[0] * c[1] for c in groups.values()),
        }
        validations[ds] = {r["id"]: r for r in rows(FREEZE / ds / "validation_raw.jsonl")}
    recon = RELEASE / "discovery/devign/source_recon"
    logs = rows(recon / "request_log.jsonl")
    checks = rows(recon / "source_checks.jsonl")
    requests = []
    for log in logs:
        commit = log["url"].rsplit("/", 1)[-1]
        cache = recon / "cache" / (commit + ".json")
        requests.append({"commit": commit, "http_status": log["http_status"],
                         "cache_exists": cache.exists(),
                         "hash_matches": cache.exists() and sha(cache) == log["sha256"],
                         "length_matches": cache.exists() and cache.stat().st_size == log["bytes"],
                         "response_commit_matches": cache.exists() and read(cache).get("sha") == commit})
    result["source_requests"] = requests
    result["case_source_coverage"] = []
    for sc in checks:
        missing = [side for side in ("vulnerable", "patched") if not sc.get(side + "_cache_reference")]
        result["case_source_coverage"].append({
            "vulnerable_id": sc["vulnerable_id"], "patched_id": sc["patched_candidate_id"],
            "function_hint": sc["function_hint"], "missing_sides": missing,
            "direct_parent_edge": sc["is_direct_parent_edge"],
            "both_donors_in_clean_bank": all(
                uid in banks["devign"] for uid in (sc["vulnerable_id"], sc["patched_candidate_id"]))})
    result["source_summary"] = {
        "archived_commit_responses": len(requests), "candidate_cases": len(checks),
        "cases_with_both_responses": sum(not r["missing_sides"] for r in result["case_source_coverage"]),
        "cases_with_missing_responses": sum(bool(r["missing_sides"]) for r in result["case_source_coverage"]),
        "global_nonexistence_proven": False,
        "archived_case_file_extensions": dict(Counter(p.suffix for p in (RELEASE / "source_archive").rglob("*") if p.is_file()))}
    sidecar = rows(RELEASE / "discovery/reveal/provenance_sidecar.jsonl")
    result["reveal_sidecar"] = {
        "rows": len(sidecar), "unique_ids": len({r["donor_id"] for r in sidecar}),
        "exact_clean_ids": {r["donor_id"] for r in sidecar} == set(banks["reveal"]),
        "code_hashes_match": all(digest(banks["reveal"][r["donor_id"]]["func"]) == r["code_sha256"] for r in sidecar),
        "statuses": dict(Counter(r["provenance_status"] for r in sidecar)),
        "donors_with_project_debian": sum(r.get("project") == "debian" for r in sidecar),
    }
    ledger = rows(RELEASE / "reviews/review_ledger.jsonl")
    reviews = [r for entry in ledger for r in entry["reviews"]]
    packet_matches = []
    for entry in ledger:
        packet = read(RELEASE / "review_packets" / (entry["case_id"] + ".json"))
        unsigned = {k: v for k, v in packet.items() if k != "payload_sha256"}
        h = digest(json.dumps(unsigned, sort_keys=True, ensure_ascii=False, separators=(",", ":")))
        packet_matches.append(h == packet["payload_sha256"] == entry["payload_sha256"])
    result["review_ledger"] = {
        "case_entries": len(ledger), "review_entries": len(reviews),
        "reviewer_names": sorted({r["reviewer"] for r in reviews}),
        "distinct_review_timestamps": len({r["reviewed_at"] for r in reviews}),
        "decisions": dict(Counter(r["decision"] for r in reviews)),
        "packet_payload_hashes_match": all(packet_matches),
        "user_confirmation": "No independent original human review forms exist; opinions/signatures were generated by step6 script.",
        "human_review_valid": False,
    }
    poolmanifest = read(RELEASE / "pools/pool_manifest.json")
    result["pools"] = {
        ds: {"pairs": len(rows(RELEASE / entry["pool_file"])),
             "hash_matches": sha(RELEASE / entry["pool_file"]) == entry["pool_sha256"]}
        for ds, entry in poolmanifest["pools"].items()}
    archive = ROOT / "Runs-management/grace_15arms_prompts_and_clean_specs.zip"
    result["spec_archive_hash"] = sha(archive)
    result["spec_archive_hash_matches_expected"] = result["spec_archive_hash"] == "9db0d3eebb66a2f83c1f9803ceb0192954a3dfe2c3de9515188a996ede84ed7b"
    promptmanifest = read(RELEASE / "validation/validation_prompt_manifest.json")
    result["validation"] = {}
    with ZipFile(archive) as z:
        for ds in ("devign", "reveal"):
            specs = [json.loads(line) for line in z.read(f"specs/{ds}_validation_15arms.jsonl").splitlines() if line.strip()]
            byid = {r["id"]: r for r in specs}
            p = RELEASE / "validation" / ds / "validation_census.jsonl"
            census = rows(p)
            result["validation"][ds] = {
                "rows": len(census), "unique_ids": len({r["target_id"] for r in census}),
                "exact_ID_set_against_raw_and_specs": {r["target_id"] for r in census} == set(validations[ds]) == set(byid),
                "code_hashes_match_specs_and_stripped_raw": all(
                    r["query_code_sha256"] == digest(byid[r["target_id"]]["query_code"].strip())
                    == digest(validations[ds][r["target_id"]]["func"].strip()) for r in census),
                "spec_code_not_byte_identical_to_raw": sum(s["query_code"] != validations[ds][s["id"]]["func"] for s in specs),
                "census_hash_matches_manifest": sha(p) == promptmanifest["datasets"][ds]["census_sha256"],
                "states": dict(Counter(r["status"] for r in census)),
                "nonempty_prompt_count": sum(bool(r.get("prompt")) for r in census),
                "nonnull_prompt_hash_count": sum(bool(r.get("prompt_sha256")) for r in census),
                "figure6_flag_true_without_prompt": sum(r.get("figure6_order_compliant") is True and not r.get("prompt") for r in census),
            }
    result["candidate_errors"] = dict(Counter(r.get("validation_error", r.get("error")) for r in rows(RELEASE / "candidates/candidate_validation_errors.jsonl")))
    result["submitted_step7_test_results"] = {
        suite: {"returncode": r["returncode"], "stdout": r["stdout"]}
        for suite, r in read(RELEASE / "acceptance/step7_selector_renderer_report.json")["pytest_suites"].items()}
    after = source_inventory()
    result["submitted_artifacts_unchanged"] = before == after
    result["release_readiness"] = "NOT_READY_FOR_NEW_B3_GPU_INFERENCE"
    (OUT / "audit.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("seals", "source_summary", "review_ledger", "validation", "submitted_artifacts_unchanged", "release_readiness")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
