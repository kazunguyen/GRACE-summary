"""Audit frozen train eligibility and try amended B3 on validation-only samples.

No model/inference, test data, threshold writes or network access. Optional
--pairs supplies a reviewed evidence JSONL; absent that, report the actual pause.
"""
import argparse
from collections import defaultdict
import hashlib
from itertools import islice
import json
from pathlib import Path
import sys
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "01_Author_Baseline_Unified/diagnostic_kit/src"
sys.path.insert(0, str(SRC))
from grace_diag.amended_b3 import VerifiedPairSelector, digest, function_hint
from grace_diag.token_budget import TokenCounter

FREEZE = ROOT / "01_Author_Baseline_Unified/output/research_freeze_20261101"
FREEZE_SHA = "e1d3c6b17c3a0b5c1e05203794d48a33825e0ea00a55deaaef565af25efe0448"
REVISION = "b2cff646eb4bb1d68355c01b18ae02e7cf42d120"
ZIP_SHA = "9db0d3eebb66a2f83c1f9803ceb0192954a3dfe2c3de9515188a996ede84ed7b"


def sha(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def rows(path):
    with Path(path).open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def frozen_bank(dataset):
    manifest_path = FREEZE / "freeze_manifest.json"
    if sha(manifest_path) != FREEZE_SHA:
        raise ValueError("Historical freeze manifest changed")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))["datasets"][dataset]
    inputs = {}
    for name in ("train_raw.jsonl", "train_manifest.jsonl", "validation_raw.jsonl"):
        p = FREEZE / dataset / name
        inputs[str(p.relative_to(ROOT))] = sha(p)
        if inputs[str(p.relative_to(ROOT))] != manifest["files_sha256"][name]:
            raise ValueError("Frozen input hash mismatch: " + name)
    metadata = {d["id"]: d for d in rows(FREEZE / dataset / "train_manifest.jsonl")}
    bank = {}
    for d in rows(FREEZE / dataset / "train_raw.jsonl"):
        m = metadata[d["id"]]
        if m["keep_in_bank"]:
            if digest(d["func"]) != m["code_sha256"] or d["target"] != m["label"]:
                raise ValueError("Frozen donor content mismatch")
            if d["split"] != "train" or d["dataset"] != dataset or d["id"] in bank:
                raise ValueError("Invalid frozen donor identity")
            bank[d["id"]] = {**d, "function_uid": d["id"]}
    if len(bank) != manifest["donor_count"]:
        raise ValueError("Frozen donor census mismatch")
    return bank, inputs


def discover(bank):
    groups = defaultdict(list)
    for d in bank.values():
        hint = function_hint(d["func"])
        if hint:
            groups[(d.get("project"), hint)].append(d)
    same_commit = 0
    candidates = []
    for (project, name), group in groups.items():
        v = [d for d in group if d["target"] == 1]
        p = [d for d in group if d["target"] == 0]
        for a in v:
            for b in p:
                if a.get("commit_id") and a["commit_id"] == b.get("commit_id"):
                    same_commit += 1
                candidates.append({"project": project, "function_hint": name,
                                   "vulnerable_id": a["id"], "patched_candidate_id": b["id"],
                                   "vulnerable_commit": a.get("commit_id"),
                                   "patched_candidate_commit": b.get("commit_id"),
                                   "before_sha256": digest(a["func"]), "after_sha256": digest(b["func"]),
                                   "characters": len(a["func"]) + len(b["func"]),
                                   "status": "UNVERIFIED_NAME_MATCH_NOT_AN_ELIGIBLE_PAIR"})
    return {"clean_train_donors": len(bank),
            "donors_missing_commit_id": sum(not d.get("commit_id") for d in bank.values()),
            "same_commit_same_function_hint_opposite_label_candidates": same_commit,
            "same_project_function_hint_opposite_label_candidates": len(candidates)}, sorted(
                candidates, key=lambda d: (d["characters"], d["vulnerable_id"], d["patched_candidate_id"]))[:12]


def run(args):
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    supplied = list(rows(args.pairs)) if args.pairs else []
    if any(p.get("test_fixture") for p in supplied):
        raise ValueError("Synthetic fixtures cannot enter the real donor workflow")
    counter = TokenCounter(str(args.tokenizer)) if args.tokenizer else None
    report = {"method": "b3-verified-patch-v1", "scope": "CPU validation prompt construction only",
              "inference_performed": False, "test_inputs_read": False,
              "thresholds_changed": False, "datasets": {},
              "sources": {str(Path(__file__).relative_to(ROOT)): sha(__file__),
                          str((SRC / "grace_diag/amended_b3.py").relative_to(ROOT)): sha(SRC / "grace_diag/amended_b3.py")}}
    if args.pairs:
        report["pair_manifest_sha256"] = sha(args.pairs)
    if args.tokenizer:
        if args.tokenizer.name != REVISION:
            raise ValueError("Use the pinned tokenizer snapshot directory")
        report["tokenizer"] = {"expected_revision": REVISION, "local_path": str(args.tokenizer),
                               "files_sha256": {p.name: sha(p) for p in args.tokenizer.glob("*.json")}}
    if any(p.get("dataset") not in ("devign", "reveal") for p in supplied):
        raise ValueError("Unknown pair dataset")
    for ds in ("devign", "reveal"):
        bank, hashes = frozen_bank(ds)
        stats, candidates = discover(bank)
        report["sources"].update(hashes)
        (out / f"{ds}_candidate_discovery.json").write_text(json.dumps(candidates, indent=2), encoding="utf-8")
        pairs = [p for p in supplied if p["dataset"] == ds]
        archive = ROOT / "grace_15arms_prompts_and_clean_specs.zip"
        if sha(archive) != ZIP_SHA:
            raise ValueError("Frozen target spec archive changed")
        report["sources"][str(archive.relative_to(ROOT))] = ZIP_SHA
        with ZipFile(archive) as z, z.open(f"specs/{ds}_validation_15arms.jsonl") as f:
            samples = [json.loads(line) for line in islice(f, args.samples)]
        validation_codes = {d["id"]: digest(d["func"].strip()) for d in rows(FREEZE / ds / "validation_raw.jsonl")}
        for d in samples:
            if validation_codes.get(d["id"]) != digest(d["query_code"].strip()):
                raise ValueError("Target spec does not match frozen validation code")
        stats.update({"reviewed_pairs_supplied": len(pairs), "sample_attempts": []})
        try:
            selector = VerifiedPairSelector(pairs, bank, ds)
        except ValueError as exc:
            selector = None
            stats["blocker"] = str(exc)
        for d in samples:
            attempt = {"id": d["id"], "query_code_sha256": digest(d["query_code"])}
            if selector is None:
                attempt.update(status="PAUSED", reason=stats["blocker"])
            elif counter is None:
                attempt.update(status="PAUSED", reason="Exact tokenizer required via --tokenizer")
            else:
                target = {k: d[k] for k in ("id", "query_code", "nodes", "edges")}
                try:
                    family = selector.render_family(target, counter)
                    dest = out / ds / str(len(stats["sample_attempts"]))
                    dest.mkdir(parents=True)
                    for arm, record in family.items():
                        (dest / f"{arm}.json").write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
                        (dest / f"{arm}.txt").write_text(record["prompt"], encoding="utf-8")
                    attempt.update(status="RENDERED_PENDING_CONTENT_AUDIT", selection=family["B3"]["selection"])
                except ValueError as exc:
                    attempt.update(status="PAUSED", reason=str(exc))
            stats["sample_attempts"].append(attempt)
        stats["status"] = "PAUSED" if any(a["status"] == "PAUSED" for a in stats["sample_attempts"]) else "PROMPT_AUDIT_REQUIRED"
        report["datasets"][ds] = stats
    (out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report["datasets"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pairs", type=Path)
    parser.add_argument("--tokenizer", type=Path)
    parser.add_argument("--samples", type=int, default=3)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.samples < 1:
        parser.error("--samples must be positive")
    run(args)
