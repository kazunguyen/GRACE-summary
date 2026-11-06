
"""Apply source-verifiable B3 explanation corrections without replacing any pairs."""
import csv
import json
import sys
from collections import Counter
from contextlib import ExitStack
from itertools import zip_longest
from pathlib import Path

import numpy as np
from transformers import PreTrainedTokenizerFast

from build_validation_input_manifest import ROOT, RUNS, artifact, read, rows, sha
from remediate_validation_extensions import demo_parts, write
from dry_run_full_validation import REV, resolve_hits, digest
from grace_diag import probes

SOURCE = RUNS / "b3_zip_specs_candidate_20261104"
OUT = RUNS / "b3_zip_specs_explanation_fix_20261104"
ARCHIVE = ROOT.parent / "tmp/grace_b3_withdrawn_20261104/Runs-management"
ARMS = ("B3", "B3-nodiff", "B3-swap", "B3-flip")


def expected_parts(before, h1, d1, h2, d2, mark, explanation, answer):
    return (
        before + h1 + d1 + h2 + d2 + mark + explanation + answer,
        before + h1 + d1 + h2 + d2 + answer,
        before + h2 + d2 + h1 + d1 + mark + explanation + answer,
        before + h2 + d1 + h1 + d2 + mark + probes._flip_words(explanation) + answer,
    )


def build(dataset, tokenizer, contrast, facts, output, reviewed):
    ds = dataset["dataset"]
    entries = {e["arm"]: e for e in dataset["sets"]}
    paths = {a: ROOT / entries[a]["prompt"]["path"] for a in ARMS}
    if any(sha(p) != entries[a]["prompt"]["sha256"] for a, p in paths.items()):
        raise ValueError("Source prompt hash mismatch")
    dests = {a: output / ds / "validation" / a / "42" for a in ARMS}
    for folder in dests.values():
        folder.mkdir(parents=True)
    counts = Counter()
    fixes = []
    hashes = {a: {} for a in ARMS}
    changed_tokens = {a: {} for a in ARMS}
    seen = set()
    with ExitStack() as stack:
        outputs = {a: stack.enter_context((p / "prompts.jsonl").open("x", encoding="utf-8", newline="\n")) for a, p in dests.items()}
        flags = stack.enter_context((output / ds / "difference_audit.jsonl").open("x", encoding="utf-8", newline="\n"))
        for original in zip_longest(*(rows(paths[a]) for a in ARMS)):
            if any(r is None for r in original):
                raise ValueError("Unequal arm coverage")
            base = original[0]
            uid = base["id"]
            if uid in seen:
                raise ValueError(uid)
            seen.add(uid)
            before, h1, d1, h2, d2, mark, prior, answer = demo_parts(base["prompt"])
            original_expected = expected_parts(before, h1, d1, h2, d2, mark, prior, answer)
            proof = contrast(list(facts(d1)), list(facts(d2)))
            if uid in reviewed:
                item = reviewed[uid]
                left, right = item["snippets"]
                if left not in d1 or right not in d2:
                    raise ValueError(f"Reviewed evidence missing: {uid}")
                proof = (item["text"], left, right, item["rule"])
            status = "verified_visible_contrast" if proof else (
                "no_supported_difference" if base["evidence"]["difference"]["status"] == "no_supported_difference"
                else "security_relevance_not_verified"
            )
            counts[status] += 1
            text = proof[0] if proof else prior
            updated = expected_parts(before, h1, d1, h2, d2, mark, text, answer)
            change = {}
            pair = [d["function_uid"] for d in base["evidence"]["demo"]["demos"]]
            for a, row, old, new in zip(ARMS, original, original_expected, updated):
                if row["id"] != uid or row["arm"] != a or row["prompt"] != old or row["prompt_sha256"] != digest(old):
                    raise ValueError(f"Input variant mismatch: {uid} {a}")
                shown = [d["function_uid"] for d in row["evidence"]["demo"]["demos"]]
                if shown != (pair[::-1] if a == "B3-swap" else pair):
                    raise ValueError(f"Donor pair mismatch: {uid} {a}")
                if new != old:
                    _, unresolved = resolve_hits(new)
                    total = len(tokenizer.apply_chat_template([{"role": "user", "content": new}], tokenize=True,
                                                               add_generation_prompt=True)["input_ids"])
                    if unresolved or total + 64 > 8192:
                        raise ValueError(f"Prompt contract regression: {uid} {a}")
                    prior_diff = old.rsplit(mark, 1)[1].removesuffix(answer)
                    updated_diff = new.rsplit(mark, 1)[1].removesuffix(answer)
                    tokens = lambda s: len(tokenizer.encode("Key difference: " + s, add_special_tokens=False))
                    if tokens(updated_diff) > 500:
                        raise ValueError(f"Difference over budget: {uid}")
                    row["evidence"]["tokens"]["demo"] += tokens(updated_diff) - tokens(prior_diff)
                    row["evidence"]["demo"]["diff_block"]["tokens"] = tokens(updated_diff)
                    row["evidence"]["tokens"]["total"] = total
                    row["evidence"]["difference"] = {"status": status, "rule": proof[3], "snippets": list(proof[1:3])}
                    old_hash = row["prompt_sha256"]
                    row["prompt"] = new
                    row["prompt_sha256"] = digest(new)
                    row["evidence"]["prompt_sha256"] = row["prompt_sha256"]
                    changed_tokens[a][uid] = (total, row["evidence"]["tokens"]["demo"])
                    change[a] = [old_hash, row["prompt_sha256"]]
                hashes[a][uid] = row["prompt_sha256"]
                outputs[a].write(json.dumps(row, ensure_ascii=False) + "\n")
            item = {"id": uid, "donor_pair": pair, "status": status}
            if change:
                item.update(rule=proof[3], snippets=list(proof[1:3]), old_explanation=prior,
                            new_explanation=text, hashes_before_after=change)
                fixes.append(item)
            flags.write(json.dumps(item, ensure_ascii=False) + "\n")
    if len(seen) != dataset["verified_pairs"]:
        raise ValueError("Validation coverage mismatch")
    sets = []
    for a in ARMS:
        prior_summary = read(ROOT / entries[a]["audit"]["path"])
        audit_path = dests[a] / "audit_rows.csv"
        sizes = []
        with paths[a].with_name("audit_rows.csv").open(encoding="utf-8", newline="") as src, audit_path.open("x", encoding="utf-8", newline="") as dst:
            reader = csv.DictReader(src)
            writer = csv.DictWriter(dst, fieldnames=reader.fieldnames)
            writer.writeheader()
            for row in reader:
                if row["id"] in changed_tokens[a]:
                    row["tokens_total"], row["tokens_demo"] = changed_tokens[a][row["id"]]
                row["prompt_sha256"] = hashes[a][row["id"]]
                sizes.append(int(row["tokens_total"]))
                writer.writerow(row)
        result = {"dataset": ds, "arm": a, "rows": len(seen),
                  "changed_prompt_texts": len(changed_tokens[a]),
                  "prompt": artifact(dests[a] / "prompts.jsonl"), "source_audit": entries[a]["audit"],
                  "audit_rows": artifact(audit_path), "tokens_p50": float(np.percentile(sizes, 50)),
                  "tokens_p95": float(np.percentile(sizes, 95)), "tokens_max": max(sizes),
                  "rate_demo_empty": prior_summary["rate_demo_empty"],
                  "rate_graph_missing": prior_summary["rate_graph_missing"],
                  "unresolved_label_flags": 0}
        write(dests[a] / "audit_summary.json", result)
        sets.append(result)
    return {"dataset": ds, "counts": dict(counts), "corrections": fixes, "sets": sets}


def main():
    snapshot = Path(sys.argv[1])
    if snapshot.name != REV:
        raise ValueError("Incorrect tokenizer revision")
    tokenizer = PreTrainedTokenizerFast.from_pretrained(snapshot, local_files_only=True)
    if not tokenizer.chat_template:
        raise ValueError("Pinned chat template missing")
    implementation = ARCHIVE / "b3_security_pairing.py"
    evidence_manifest = read(ARCHIVE / "validation_b3_reselected_20261104/manifest.json")
    proof = next(x for x in evidence_manifest["sources"] if x["path"].endswith("b3_security_pairing.py"))
    if sha(implementation) != proof["sha256"]:
        raise ValueError("Archived contrast rule hash mismatch")
    sys.path.insert(0, str(ARCHIVE))
    from b3_security_pairing import contrast, facts

    source = SOURCE / "manifest.json"
    review_path = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else None
    reviewed = read(review_path) if review_path else {}
    output = RUNS / "b3_zip_specs_guard_fix_20261104" if review_path else OUT
    output.mkdir(exist_ok=False)
    result = [build(dataset, tokenizer, contrast, facts, output, reviewed) for dataset in read(source)["datasets"]]
    applied = {entry["id"] for dataset in result for entry in dataset["corrections"]}
    if not reviewed.keys() <= applied:
        raise ValueError("Reviewed rows missing from output")
    write(output / "manifest.json", {"status": "candidate_not_confirmatory_ready",
          "source": artifact(source), "guard_review": artifact(review_path) if review_path else None, "only_key_difference_changed": True,
          "pair_reselection": False, "llm_calls": 0, "datasets": result,
          "contrast_rule": {"path": str(implementation), "sha256": sha(implementation)},
          "tokenizer_revision": REV,
          "tokenizer_file_sha256": {name: sha(snapshot / name) for name in ("tokenizer.json", "tokenizer_config.json")}})
    for d in result:
        print(d["dataset"], d["counts"], len(d["corrections"]), flush=True)


if __name__ == "__main__":
    main()
