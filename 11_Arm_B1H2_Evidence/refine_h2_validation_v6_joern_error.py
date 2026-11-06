
"""Build the bounded guard-centred B1-H2 candidate on frozen validation."""
import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import yaml
from transformers import PreTrainedTokenizerFast

ROOT = Path(__file__).resolve().parents[1]
ARM = ROOT / "11_Arm_B1H2_Evidence"
RUNS = ROOT / "Runs-management"
sys.path.insert(0, str(RUNS))

from build_validation_input_manifest import PACKAGE, ROOT, RUNS, artifact, read, rows, sha
from dry_run_full_validation import BUDGET, OLD, PREFIX, REV, ExactCounter, digest, render_project, resolve_hits
from grace_diag import probes
from grace_diag.prompt_audit import audit_rows
from grace_diag.token_budget import TokenCounter
from audit_prompt_integrity import split_prompt
from remediate_validation_extensions import H2, h2_input, operation_score, pack_h2, write
from select_h2_cluster import select_cluster

OUT = ARM / "validation_h2_cluster_v6_joern_error_20261105"


def build(dataset, ids, counter, config):
    root = OUT / dataset / "validation/B1-H2/42"
    root.mkdir(parents=True, exist_ok=False)
    joern = OLD / dataset / "validation/specs.jsonl"
    b2_path = PACKAGE / "prompts/reference_B2" / dataset / "validation/prompts.jsonl"
    b2 = {row["id"]: split_prompt(row["prompt"])["code"].strip() for row in rows(b2_path)}
    prompt_file = root / "prompts.jsonl"
    statuses = Counter()
    audit_data = []
    flags = []
    unresolved = 0
    seen = set()
    with prompt_file.open("w", encoding="utf-8", newline="\n") as stream:
        for original in rows(joern):
            uid = original["id"]
            if uid in seen:
                raise ValueError(f"Duplicate ID: {uid}")
            seen.add(uid)
            graph = h2_input(original)
            prefix_nodes = {node["id"] for node in graph["nodes"]}
            text, evidence = pack_h2(graph, counter, config)
            policy = "closed_prefix"
            if not graph["nodes"]:
                marker = str(original.get("graph_error", "")).strip()
                if "Joern" not in marker:
                    raise ValueError(f"Missing CPG without flagged Joern error: {uid}")
                text = "CPG_UNAVAILABLE: flagged Joern extraction error; no H2 graph evidence is available. Do not treat this as evidence that the code is safe."
                evidence.update(status="missing_cpg", no_usable_evidence=True, flagged_joern_error=True)
            if evidence["no_usable_evidence"] and graph["nodes"]:
                selection = select_cluster(original, operation_score, PREFIX, config["max_operations"])
                if selection:
                    alternative = h2_input(selection)
                    new_text, new_evidence = pack_h2(alternative, counter, config)
                    if not new_evidence["no_usable_evidence"]:
                        text, evidence, graph = new_text, new_evidence, alternative
                        policy = "cdg_cluster"
            evidence.update(
                input_policy=policy, source_nodes=len(graph["nodes"]), source_edges=len(graph["edges"]),
                nodes_outside_closed_prefix=sum(node["id"] not in prefix_nodes for node in graph["nodes"]),
            )
            statuses["no_usable_evidence"] += evidence["no_usable_evidence"]
            statuses["cluster_selected"] += policy == "cdg_cluster"
            statuses["cluster_with_nodes_outside_prefix"] += evidence["nodes_outside_closed_prefix"] > 0
            statuses["missing_cpg"] += not graph["nodes"]
            spec = {
                "id": uid, "query_code": original["query_code"], "nodes": original["nodes"],
                "edges": original["edges"], "h2_evidence": text, "h2_source_limits": PREFIX,
            }
            result = render_project(spec, "B1-H2", 42, counter, None)
            if evidence.get("flagged_joern_error"):
                result.evidence.setdefault("graph", {})["missing"] = True
            if probes.split_blocks(result.prompt)["code"] != b2[uid]:
                raise ValueError(f"Target differs from B2 for {uid}")
            if result.evidence["tokens"]["approx"] or result.evidence["tokens"]["total"] + BUDGET["reserve"] > BUDGET["total"]:
                raise ValueError(f"Token budget failure for {uid}")
            row = {
                "id": uid, "dataset": dataset, "split": "validation", "arm": "B1-H2", "seed": 42,
                "prompt_variant": OUT.name, "prompt_sha256": digest(result.prompt),
                "prompt": result.prompt, "evidence": {**result.evidence, "h2": evidence},
            }
            if row["prompt_sha256"] != result.evidence["prompt_sha256"]:
                raise ValueError(f"Evidence hash mismatch for {uid}")
            hits, open_hits = resolve_hits(result.prompt)
            flags.extend({"id": uid, **hit} for hit in hits)
            unresolved += bool(open_hits)
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
            audit_data.append(audit_rows([row])["rows"][0])
            if len(seen) % 500 == 0:
                print(dataset, "H2", len(seen), flush=True)
    if seen != ids:
        raise ValueError(f"Coverage mismatch for {dataset}")
    sizes = [row["tokens_total"] for row in audit_data]
    summary = {
        "dataset": dataset, "split": "validation", "arm": "B1-H2", "seed": 42,
        "sources": {"joern_specs": artifact(joern), "b2_reference": artifact(b2_path)},
        "rows": len(audit_data), "tokens_p50": float(np.percentile(sizes, 50)),
        "tokens_p95": float(np.percentile(sizes, 95)), "tokens_max": max(sizes),
        "raw_regex_flagged_prompts": sum(row["label_leak"] for row in audit_data),
        "unresolved_label_flags": unresolved, "prompt": artifact(prompt_file),
        "h2_coverage": dict(statuses), "llm_calls": 0,
        "manual_review_status": "awaiting_two_independent_reviewers",
    }
    for key in ("code_truncated", "graph_truncated", "demo_truncated", "demo_empty", "graph_missing"):
        summary["rate_" + key] = sum(row[key] for row in audit_data) / len(audit_data)
    summary["automatic_audit_pass"] = not unresolved and summary["rate_graph_missing"] <= 0.05
    write(root / "audit_summary.json", summary)
    write(root / "raw_label_flags.json", flags)
    with (root / "audit_rows.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(audit_data[0]))
        writer.writeheader()
        writer.writerows(audit_data)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tokenizer", type=Path, required=True)
    args = parser.parse_args()
    if args.tokenizer.name != REV:
        raise ValueError("Tokenizer snapshot must use the pinned revision")
    counter = ExactCounter.__new__(ExactCounter)
    TokenCounter.__init__(counter, None)
    counter.tok = PreTrainedTokenizerFast.from_pretrained(args.tokenizer, local_files_only=True)
    if not counter.tok.chat_template:
        raise ValueError("Pinned chat template is missing")
    counter.approx = False
    counter.memo = {}
    counter.chat_memo = {}
    config_path = H2 / "configs/h2.yaml"
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    config.update(max_nodes=PREFIX["nodes"], max_edges=PREFIX["edges"])
    inventory = PACKAGE / "validation_active_manifest.json"
    OUT.mkdir(exist_ok=False)
    result = [
        build(d["dataset"], set(d["ids"]), counter, config) for d in read(inventory)["datasets"]
    ]
    files = [
        Path(__file__), ROOT / "11_Arm_B1H2_Evidence/select_h2_cluster.py",
        ROOT / "Runs-management/remediate_validation_extensions.py",
        H2 / "grace_h2/evidence.py", config_path,
    ]
    write(OUT / "manifest.json", {
        "schema": "grace_validation_h2_cluster_candidate_v2",
        "source_inventory": artifact(inventory), "input_sets": result,
        "source_files": [{"path": str(path), "sha256": sha(path)} for path in files],
        "tokenizer_revision": REV, "source_limits": PREFIX, "budget": BUDGET,
        "policy": "Keep the original prefix if it yields a guard. Otherwise select a bounded CDG-centred cluster from the same frozen Joern CPG. For flagged Joern extraction errors, explicitly render CPG_UNAVAILABLE in the H2 evidence block and preserve graph-missing provenance.",
        "status": "awaiting_candidate_specific_review",
    })
    print(OUT / "manifest.json", flush=True)


if __name__ == "__main__":
    main()
