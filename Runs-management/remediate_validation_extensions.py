
"""Build a separately versioned validation candidate for B1-H2 and B3."""
import argparse
import csv
import json
import sys
from collections import Counter
from contextlib import ExitStack
from pathlib import Path

import yaml

from build_validation_input_manifest import PACKAGE, ROOT, RUNS, artifact, read, rows, sha
from dry_run_full_validation import (
    BUDGET, PREFIX, REV, ExactCounter, OLD, digest, project_renderer, render_project, resolve_hits,
)
from audit_prompt_integrity import make_manual, split_prompt
from grace_diag import probes
from grace_diag.prompt_audit import audit_rows
from grace_diag.token_budget import TokenCounter

H2 = ROOT.parent / "GRACE-H2-GuardedEvidence"
sys.path.insert(0, str(H2))
from grace_h2.evidence import GuardedGraph, operation_score
from visible_demo_difference import describe

OUT = RUNS / "validation_extensions_remediation_v4_20261104"
ARMS = ("B1-H2", "B3", "B3-nodiff", "B3-swap", "B3-flip")
MARKER = "\n\nKey difference: "
ANSWER = "\n\nAnswer (0 or 1):"


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")



def h2_input(spec):
    nodes, edges = probes.closed_prefix(
        spec["nodes"], spec["edges"], PREFIX["nodes"], PREFIX["edges"],
    )
    return {
        "nodes": [
            {"id": str(node["id"]), "kind": node["type"],
             "properties": {**node.get("properties", {}),
                            "CODE": node.get("code", ""), "NAME": node.get("name", "")}}
            for node in nodes
        ],
        "edges": [
            {"src": str(edge["start"]), "dst": str(edge["end"]), "kind": edge["type"],
             "properties": edge.get("properties", {})}
            for edge in edges
        ],
    }


def pack_h2(graph, counter, config):
    if not graph["nodes"]:
        return "", {"status": "missing_cpg", "selected_operations": 0, "no_usable_evidence": True}
    engine = GuardedGraph(graph, config)
    # Within the identical closed prefix, prefer operations with observed control edges.
    engine.seeds.sort(key=lambda node: not any(
        edge["kind"].upper() == "CDG" for edge in engine.inc[str(node["id"])]
    ))
    budget = 8192
    while True:
        text, audit = engine.pack(budget)
        tokens = counter.count(text)
        if tokens <= BUDGET["graph"]:
            audit["no_usable_evidence"] = not audit.get("guards", 0)
            audit["algorithm"] = "direct_cdg_cfg_checked_v3_cdg_priority"
            audit["bytes"] = len(text.encode("utf-8"))
            return text, audit
        budget = budget * BUDGET["graph"] // tokens


def demo_parts(prompt):
    before, vulnerable, rest = prompt.partition("\n\nThe following example is Vulnerable.\n")
    first, safe, rest = rest.partition("\n\nThe following example is Non-vulnerable.\n")
    second, difference, tail = rest.rpartition(MARKER)
    explanation, answer, end = tail.partition(ANSWER)
    if not all((vulnerable, safe, difference, answer)) or end:
        raise ValueError("Unexpected contrastive prompt delimiters")
    return before, vulnerable, first, safe, second, difference, explanation, answer


def build_dataset(dataset, counter, config, inventory, manual):
    dataset_manifest = next(item for item in inventory["datasets"] if item["dataset"] == dataset)
    graph_file = OLD / dataset / "validation/specs.jsonl"
    reference_file = PACKAGE / "prompts/reference_B2" / dataset / "validation/prompts.jsonl"
    baseline_file = RUNS / "dry_run_validation_20261102" / dataset / "validation/B1/42/prompts.jsonl"
    packed_file = ROOT / dataset_manifest["packaged_specs"]["path"]
    bank_file = ROOT / dataset_manifest["donor_bank"]["path"]
    bank = {row["id"]: (row["func"].strip(), int(row["target"])) for row in rows(bank_file)}
    references = {row["id"]: row for row in rows(reference_file)}
    baseline = {row["id"]: row["evidence"] for row in rows(baseline_file)}
    expected_ids = set(dataset_manifest["ids"])
    if set(references) != expected_ids or set(baseline) != expected_ids:
        raise ValueError(f"Reference IDs disagree for {dataset}")
    pairs = {}
    for row in rows(packed_file):
        uid = row.get("original_id", row["id"])
        pair = row["demonstrations_pair"]
        if uid in pairs or [demo["target"] for demo in pair] != [1, 0]:
            raise ValueError(f"Invalid frozen pair for {uid}")
        for demo in pair:
            if bank[demo["function_uid"]] != (demo["func"].strip(), demo["target"]):
                raise ValueError(f"Donor text or label mismatch for {uid}")
        pairs[uid] = pair
    if set(pairs) != expected_ids:
        raise ValueError(f"Spec IDs disagree for {dataset}")

    folders = {arm: OUT / dataset / "validation" / arm / "42" for arm in ARMS}
    for folder in folders.values():
        folder.mkdir(parents=True, exist_ok=False)
    prompts = {arm: folder / "prompts.jsonl" for arm, folder in folders.items()}
    stored = {arm: [] for arm in ARMS}
    unresolved = Counter()
    raw_flags = {arm: [] for arm in ARMS}
    h2_status = Counter()
    difference_status = Counter()
    h2_diagnostics = Counter()
    h2_diagnostic_rows = []
    seen = set()
    sources = {
        "joern_specs": artifact(graph_file), "b2_reference": artifact(reference_file),
        "b1_evidence": artifact(baseline_file), "contrastive_specs": artifact(packed_file),
        "donor_bank": artifact(bank_file),
    }

    with ExitStack() as stack:
        streams = {
            arm: stack.enter_context(path.open("w", encoding="utf-8", newline="\n"))
            for arm, path in prompts.items()
        }
        for original in rows(graph_file):
            uid = original["id"]
            if uid in seen:
                raise ValueError(f"Duplicate Joern spec {uid}")
            seen.add(uid)
            pair = pairs[uid]
            if not set(references[uid]["demo_ids"]) & {d["function_uid"] for d in pair}:
                raise ValueError(f"Missing frozen B2 donor anchor for {uid}")
            excerpts = [counter.fit(demo["func"].strip(), BUDGET["demo"]).text for demo in pair]
            difference, difference_audit = describe(*excerpts)
            difference_status[difference_audit["status"]] += 1
            b2 = split_prompt(references[uid]["prompt"])
            h2_graph = h2_input(original)
            h2_text, h2_audit = pack_h2(h2_graph, counter, config)
            h2_status[h2_audit["status"]] += 1
            if h2_audit["no_usable_evidence"]:
                full_cdg = sum(edge["type"].upper() == "CDG" for edge in original["edges"])
                prefix_cdg = sum(edge["kind"].upper() == "CDG" for edge in h2_graph["edges"])
                prefix_operations = sum(bool(operation_score(node)) for node in h2_graph["nodes"])
                if not h2_graph["nodes"]:
                    cause = "missing_cpg"
                elif not full_cdg:
                    cause = "no_cdg_in_source"
                elif not prefix_cdg:
                    cause = "cdg_outside_closed_prefix"
                elif not prefix_operations:
                    cause = "no_recognized_operation_in_prefix"
                else:
                    cause = "no_supported_operation_guard_in_prefix"
                h2_audit["diagnostic"] = cause
                h2_diagnostics[cause] += 1
                h2_diagnostic_rows.append({"id": uid, "diagnostic": cause, "full_cdg": full_cdg, "prefix_cdg": prefix_cdg, "prefix_operations": prefix_operations})
            h2_audit["source_nodes"] = len(h2_graph["nodes"])
            h2_audit["source_edges"] = len(h2_graph["edges"])
            probes.render_graph = project_renderer(
                {uid: (b2["graph"], baseline[uid]["graph"])}, {}, {}, "empty",
            )
            spec = {
                "id": uid, "query_code": original["query_code"],
                "nodes": original["nodes"], "edges": original["edges"],
                "demonstrations_pair": pair, "security_difference": difference,
                "h2_evidence": h2_text, "h2_source_limits": PREFIX,
            }
            rendered = {arm: render_project(spec, arm, 42, counter, None) for arm in ARMS}
            b3 = rendered["B3"].prompt
            before, vulnerable, first, safe, second, marker, explanation, answer = demo_parts(b3)
            if [first, second] != excerpts or explanation != difference:
                raise ValueError(f"Explanation or displayed excerpt changed during render for {uid}")
            if rendered["B3-nodiff"].prompt != before + vulnerable + first + safe + second + answer:
                raise ValueError(f"B3-nodiff pairing failed for {uid}")
            if rendered["B3-swap"].prompt != before + safe + second + vulnerable + first + marker + explanation + answer:
                raise ValueError(f"B3-swap pairing failed for {uid}")
            if rendered["B3-flip"].prompt != (
                before + safe + first + vulnerable + second + marker + probes._flip_words(explanation) + answer
            ):
                raise ValueError(f"B3-flip pairing failed for {uid}")
            for arm, result in rendered.items():
                ev = result.evidence
                if ev["tokens"]["approx"] or ev["tokens"]["total"] + BUDGET["reserve"] > BUDGET["total"]:
                    raise ValueError(f"Token budget failure for {uid} {arm}")
                blocks = probes.split_blocks(result.prompt)
                if blocks["code"] != b2["code"].strip():
                    raise ValueError(f"Target code differs from B2 for {uid} {arm}")
                if arm != "B1-H2" and blocks["graph"].strip() != b2["graph"].strip():
                    raise ValueError(f"Target graph differs from B2 for {uid} {arm}")
                if arm == "B1-H2":
                    ev["h2"] = h2_audit
                elif arm != "B3-nodiff":
                    ev["difference"] = difference_audit
                row = {
                    "dataset": dataset, "split": "validation", "arm": arm, "seed": 42,
                    "id": uid, "prompt_variant": OUT.name,
                    "prompt_sha256": digest(result.prompt), "prompt": result.prompt,
                    "evidence": ev,
                }
                if row["prompt_sha256"] != ev["prompt_sha256"]:
                    raise ValueError(f"Evidence hash differs from prompt for {uid} {arm}")
                hits, open_hits = resolve_hits(result.prompt)
                raw_flags[arm].extend({"id": uid, **hit} for hit in hits)
                unresolved[arm] += bool(open_hits)
                streams[arm].write(json.dumps(row, ensure_ascii=False) + "\n")
                stored[arm].append(audit_rows([row])["rows"][0])
            if len(seen) % 250 == 0:
                print(dataset, len(seen), flush=True)
    if seen != expected_ids:
        raise ValueError(f"Rendered IDs disagree for {dataset}")

    results = []
    for arm, folder in folders.items():
        flat = stored[arm]
        import numpy as np
        sizes = [row["tokens_total"] for row in flat]
        summary = {
            "rows": len(flat), "tokens_p50": float(np.percentile(sizes, 50)),
            "tokens_p95": float(np.percentile(sizes, 95)), "tokens_max": max(sizes),
            "raw_regex_flagged_prompts": sum(row["label_leak"] for row in flat),
            "unresolved_label_flags": unresolved[arm],
            "prompt": artifact(prompts[arm]),
            "llm_calls": 0, "manual_review_status": "awaiting_two_independent_reviewers",
        }
        for key in ("code_truncated", "graph_truncated", "demo_truncated", "demo_empty", "graph_missing"):
            summary["rate_" + key] = sum(row[key] for row in flat) / len(flat)
        if arm == "B1-H2":
            summary["h2_evidence_status_counts"] = dict(h2_status)
            summary["h2_no_usable_evidence_by_cause"] = dict(h2_diagnostics)
            write(folder / "no_usable_evidence.json", h2_diagnostic_rows)
        elif arm != "B3-nodiff":
            summary["difference_status_counts"] = dict(difference_status)
        summary["automatic_audit_pass"] = (
            not unresolved[arm] and summary["rate_demo_empty"] <= 0.01
            and summary["rate_graph_missing"] <= 0.05
        )
        write(folder / "audit_summary.json", summary)
        write(folder / "raw_label_flags.json", raw_flags[arm])
        with (folder / "audit_rows.csv").open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(flat[0]))
            writer.writeheader()
            writer.writerows(flat)
        results.append({
            "dataset": dataset, "split": "validation", "arm": arm, "seed": 42,
            "sources": sources, **summary,
        })
        for row in flat:
            manual.append({
                **row, "dataset": dataset, "split": "validation", "phase": "candidate",
                "audit_key": f"{dataset}/validation/{arm}/42/{row['id']}",
                "prompt_source": summary["prompt"]["path"],
            })
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tokenizer", type=Path, help="Local snapshot directory for the pinned tokenizer")
    args = parser.parse_args()
    inventory_file = PACKAGE / "validation_input_manifest.json"
    inventory = read(inventory_file)
    tokenizer_hashes = {}
    if args.tokenizer is None:
        counter = ExactCounter()
    else:
        from transformers import PreTrainedTokenizerFast

        if args.tokenizer.name != REV:
            raise ValueError("Tokenizer snapshot must use the pinned revision")
        counter = ExactCounter.__new__(ExactCounter)
        TokenCounter.__init__(counter, None)
        counter.tok = PreTrainedTokenizerFast.from_pretrained(args.tokenizer, local_files_only=True)
        counter.approx = False
        counter.memo = {}
        counter.chat_memo = {}
        for name in ("tokenizer.json", "tokenizer_config.json"):
            tokenizer_hashes[name] = sha(args.tokenizer / name)
    if not counter.tok.chat_template:
        raise ValueError("Pinned chat template is missing")
    config_file = H2 / "configs/h2.yaml"
    config = yaml.safe_load(config_file.read_text(encoding="utf-8"))
    config.update(max_nodes=PREFIX["nodes"], max_edges=PREFIX["edges"])
    OUT.mkdir(exist_ok=False)
    manual = []
    results = [
        entry for dataset in ("devign", "reveal")
        for entry in build_dataset(dataset, counter, config, inventory, manual)
    ]
    make_manual(OUT, manual)
    source_files = [
        H2 / "grace_h2/evidence.py", config_file,
        ROOT / "Runs-management/remediate_validation_extensions.py",
        ROOT / "Runs-management/visible_demo_difference.py",
        ROOT / "Runs-management/dry_run_full_validation.py",
        ROOT / "01_Author_Baseline_Unified/diagnostic_kit/src/grace_diag/probes.py",
    ]
    write(OUT / "manifest.json", {
        "schema": "grace_validation_extensions_candidate_v1",
        "source_inventory": artifact(inventory_file),
        "implementation": [{"path": str(path), "sha256": sha(path)} for path in source_files],
        "tokenizer_revision": REV, "tokenizer_file_sha256": tokenizer_hashes,
        "budget": BUDGET, "graph_prefix": PREFIX,
        "h2_graph_projection": "Joern cache closed prefix. Ranks operations with observed CDG first inside the identical prefix. Preserves available graph properties.",
        "h2_config": config,
        "difference_policy": "Two directly quoted observations from rendered donor excerpts. Otherwise use an explicit abstention; report its coverage.", "input_sets": results,
        "manual_packet": artifact(OUT / "manual_packet.md"),
        "status": "awaiting_two_independent_reviewers",
    })


if __name__ == "__main__":
    main()

