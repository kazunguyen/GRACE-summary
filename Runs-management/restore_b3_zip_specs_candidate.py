
"""Verify and restore the B3 candidate built from the ZIP's exact pair specs."""
import csv
import hashlib
import io
import json
import shutil
from collections import Counter
from itertools import zip_longest
from pathlib import Path
from zipfile import ZipFile

from build_validation_input_manifest import ROOT, RUNS, artifact, read, rows, sha
from remediate_validation_extensions import demo_parts
from grace_diag import probes

ARCHIVE = ROOT.parent / "tmp/grace_b3_withdrawn_20261104/Runs-management"
OLD = ARCHIVE / "validation_extensions_remediation_v4_20261104"
OLD_REVIEW = ARCHIVE / "validation_remediated_review_20261104/reviewer_codex.csv"
ZIP = ROOT / "grace_15arms_prompts_and_clean_specs.zip"
OUT = RUNS / "b3_zip_specs_candidate_20261104"
ARMS = ("B3", "B3-nodiff", "B3-swap", "B3-flip")


def digest(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def zip_member_hash(z, member):
    with z.open(member) as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def zip_rows(z, member):
    with io.TextIOWrapper(z.open(member), encoding="utf-8-sig") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def validate(z, dataset, metadata, reviewed):
    spec_member = f"specs/{dataset}_validation_15arms.jsonl"
    b2_member = f"prompts/reference_B2/{dataset}/validation/prompts.jsonl"
    spec_hash = zip_member_hash(z, spec_member)
    b2_hash = zip_member_hash(z, b2_member)
    bank = ROOT / metadata["B3"]["sources"]["donor_bank"]["path"]
    bank_proof = read(RUNS / "donor_reconciliation_20261101" / f"{dataset}_retrieval_provenance.json")
    if sha(bank) != bank_proof["new"]["cache_sha256"]:
        raise ValueError(f"Frozen bank hash mismatch: {dataset}")
    donors = {r["id"]: (int(r["target"]), r["func"].strip()) for r in rows(bank)}
    b2 = {r["id"]: r for r in zip_rows(z, b2_member)}
    specs = {}
    for spec in zip_rows(z, spec_member):
        uid = spec.get("original_id", spec["id"])
        pair = spec["demonstrations_pair"]
        if uid in specs or [int(d["target"]) for d in pair] != [1, 0]:
            raise ValueError(f"Invalid pair in ZIP: {uid}")
        for d in pair:
            if donors.get(d["function_uid"]) != (int(d["target"]), d["func"].strip()):
                raise ValueError(f"Frozen donor mismatch: {uid}")
        specs[uid] = [d["function_uid"] for d in pair]
    if specs.keys() != b2.keys() or any(not set(b2[uid]["demo_ids"]) & set(pair) for uid, pair in specs.items()):
        raise ValueError(f"ZIP target coverage or B2 anchor mismatch: {dataset}")

    paths = {}
    for arm in ARMS:
        e = metadata[arm]
        src = OLD / dataset / "validation" / arm / "42/prompts.jsonl"
        if (
            e["sources"]["contrastive_specs"]["sha256"] != spec_hash
            or e["sources"]["b2_reference"]["sha256"] != b2_hash
            or e["sources"]["donor_bank"]["sha256"] != sha(bank)
            or e["prompt"]["sha256"] != sha(src)
            or not e["automatic_audit_pass"]
        ):
            raise ValueError(f"Archived candidate provenance mismatch: {dataset} {arm}")
        paths[arm] = src

    states = Counter()
    seen = set()
    for base, nodiff, swap, flip in zip_longest(*(rows(paths[arm]) for arm in ARMS)):
        if any(r is None for r in (base, nodiff, swap, flip)):
            raise ValueError(f"Row counts disagree for {dataset}")
        uid = base["id"]
        if uid in seen:
            raise ValueError(f"Duplicate ID: {uid}")
        seen.add(uid)
        before, h1, d1, h2, d2, mark, explanation, answer = demo_parts(base["prompt"])
        reference_prefix, sep, _ = b2[uid]["prompt"].rpartition("The following is an example, and it is ")
        if not sep or reference_prefix.rstrip() != before.rstrip():
            raise ValueError(f"Target or graph differs from B2: {uid}")
        candidate = [d["function_uid"] for d in base["evidence"]["demo"]["demos"]]
        if candidate != specs[uid]:
            raise ValueError(f"Pair differs from ZIP specs: {uid}")
        for donor, visible, ev in zip(candidate, (d1, d2), base["evidence"]["demo"]["demos"]):
            raw = donors[donor][1]
            if ev["truncated"]:
                marker = "\n/* [TRUNCATED] */"
                if not visible.endswith(marker) or not raw.startswith(visible.removesuffix(marker)):
                    raise ValueError(f"Truncated code differs from donor: {uid}")
            elif visible != raw:
                raise ValueError(f"Code differs from donor: {uid}")
        diff = base["evidence"]["difference"]
        states[diff["status"]] += 1
        if diff["status"] == "visible_code_contrast":
            a, b = diff["vulnerable_snippet"], diff["non_vulnerable_snippet"]
            if a not in d1 or b not in d2 or a not in explanation or b not in explanation:
                raise ValueError(f"Unsupported literal quote: {uid}")
        expected = (
            base["prompt"], before + h1 + d1 + h2 + d2 + answer,
            before + h2 + d2 + h1 + d1 + mark + explanation + answer,
            before + h2 + d1 + h1 + d2 + mark + probes._flip_words(explanation) + answer,
        )
        for arm, row, text in zip(ARMS, (base, nodiff, swap, flip), expected):
            if row["id"] != uid or row["arm"] != arm or row["prompt"] != text or row["prompt_sha256"] != digest(text):
                raise ValueError(f"Variant or hash differs: {uid} {arm}")
            tok = row["evidence"]["tokens"]
            if tok["approx"] or tok["total"] + 64 > 8192 or tok["code"] > 3000 or tok["graph"] > 1500 or any(
                d["tokens"] > 1500 for d in row["evidence"]["demo"]["demos"]
            ):
                raise ValueError(f"Budget mismatch: {uid} {arm}")
            key = (dataset, arm, uid)
            if key in reviewed and row["prompt_sha256"] != reviewed[key]["prompt_sha256"]:
                raise ValueError(f"Historical review does not match this candidate: {uid} {arm}")
    if seen != specs.keys():
        raise ValueError(f"Coverage differs from ZIP: {dataset}")

    outputs = []
    for arm, src in paths.items():
        dest = OUT / dataset / "validation" / arm / "42"
        dest.mkdir(parents=True, exist_ok=True)
        for name in ("prompts.jsonl", "audit_summary.json", "audit_rows.csv", "raw_label_flags.json"):
            original, output = src.with_name(name), dest / name
            if output.exists():
                if sha(output) != sha(original):
                    raise ValueError(f"Existing copy differs: {output}")
            else:
                shutil.copyfile(original, output)
        if sha(dest / "prompts.jsonl") != metadata[arm]["prompt"]["sha256"]:
            raise ValueError(f"Copy changed bytes: {dataset} {arm}")
        outputs.append({
            "dataset": dataset, "arm": arm, "seed": 42, "split": "validation",
            "rows": len(seen), "prompt": artifact(dest / "prompts.jsonl"),
            "audit": artifact(dest / "audit_summary.json"),
            "automatic_audit_pass": True,
        })
    return {
        "dataset": dataset, "verified_pairs": len(seen), "spec_member": spec_member,
        "spec_sha256": spec_hash, "b2_member": b2_member, "b2_sha256": b2_hash,
        "difference_counts": dict(states), "sets": outputs,
    }


def main():
    meta = read(OLD / "manifest.json")
    by_ds = {ds: {e["arm"]: e for e in meta["input_sets"] if e["dataset"] == ds}
             for ds in ("devign", "reveal")}
    with OLD_REVIEW.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames
        review = {(r["dataset"], r["arm"], r["id"]): r for r in reader if r["arm"] in ARMS}
    OUT.mkdir(exist_ok=True)
    with ZipFile(ZIP) as z:
        datasets = [validate(z, ds, by_ds[ds], review) for ds in by_ds]
    with (OUT / "reviewer_codex_same_hash.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(review.values())
    result = {
        "schema": "grace_b3_zip_specs_provisional_v1",
        "status": "candidate_not_confirmatory_ready",
        "pair_source_decision": "User instructed to proceed as if ZIP specs were confirmed. No independent evidence of pre-freeze approval was provided.",
        "source_zip": artifact(ZIP),
        "reused_candidate": {"path": str(OLD / "manifest.json"), "sha256": sha(OLD / "manifest.json")},
        "pair_reselection": False, "llm_calls": 0, "allow_test": False,
        "datasets": datasets,
        "same_hash_codex_review": dict(Counter(r["overall_verdict"] for r in review.values())),
        "remaining_gates": [
            "Obtain evidence identifying these exact pair specs as the pre-freeze selections.",
            "Resolve unsupported explanations or agree an explicit handling rule consistent with the submitted protocol.",
            "Complete the independent-review requirement for formal acceptance.",
        ],
    }
    (OUT / "manifest.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print([(d["dataset"], d["verified_pairs"], d["difference_counts"]) for d in datasets],
          result["same_hash_codex_review"], flush=True)


if __name__ == "__main__":
    main()
