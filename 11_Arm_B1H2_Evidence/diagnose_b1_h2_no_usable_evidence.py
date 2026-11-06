"""Classify no-guard B1-H2 rows by same-CPG structural opportunities."""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
ARM = ROOT / "11_Arm_B1H2_Evidence"
RUNS = ROOT / "Runs-management"
H2 = ROOT.parent / "GRACE-H2-GuardedEvidence"
sys.path.insert(0, str(ROOT / "01_Author_Baseline_Unified/diagnostic_kit/src"))
sys.path.insert(0, str(RUNS))
sys.path.insert(0, str(H2))

from grace_diag import probes
from remediate_validation_extensions import H2 as H2_ROOT, h2_input, operation_score
from select_h2_cluster import select_cluster

CANDIDATE = ARM / "validation_h2_cluster_v5_20261104"
SOURCE = ROOT / "01_Author_Baseline_Unified/output/local_full/bundles_recovered_joern_final_20261031"
CONFIG_PATH = H2_ROOT / "configs/h2.yaml"
LIMITS = {"nodes": 40, "edges": 80}
OUT = ARM / "audit/b1_h2_no_usable_evidence_diagnosis_20261105.json"


def rows(path: Path):
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            if line.strip():
                yield json.loads(line)


def recognized(node: dict) -> bool:
    return bool(operation_score({
        "kind": node["type"],
        "properties": {"NAME": node.get("name", ""), "CODE": node.get("code", "")},
    }))


def main() -> None:
    config = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    cap = config["max_operations"]
    diagnoses = {}
    total_counts = Counter()
    no_guard_ids = {}
    for dataset in ("devign", "reveal"):
        prompt_file = CANDIDATE / dataset / "validation/B1-H2/42/prompts.jsonl"
        source_file = SOURCE / dataset / "validation/specs.jsonl"
        no_guard = {
            row["id"] for row in rows(prompt_file)
            if row["evidence"]["h2"].get("no_usable_evidence")
        }
        source_by_id = {row["id"]: row for row in rows(source_file)}
        if not no_guard.issubset(source_by_id):
            raise ValueError(f"{dataset}: candidate rows missing source CPG")
        local = Counter()
        examples = defaultdict(list)
        edge_types_without_cdg = Counter()
        error_markers = Counter()
        error_examples = []
        for uid in sorted(no_guard):
            original = source_by_id[uid]
            full_nodes = {str(node["id"]): node for node in original["nodes"]}
            full_edges = original["edges"]
            full_cdg = [edge for edge in full_edges if edge["type"].upper() == "CDG"]
            if not full_cdg:
                edge_types_without_cdg.update(str(edge["type"]).upper() for edge in full_edges)
            marker_values = {
                key: original[key] for key in original
                if any(tag in key.lower() for tag in ("error", "joern", "fail"))
                and original[key] not in (None, False, "", [], {})
            }
            if marker_values:
                for key in marker_values:
                    error_markers[key] += 1
                if len(error_examples) < 10:
                    error_examples.append({"id": uid, "markers": marker_values})
            full_ops = {uid_: node for uid_, node in full_nodes.items() if recognized(node)}
            full_cdg_to_op = [edge for edge in full_cdg if str(edge["end"]) in full_ops]

            prefix = h2_input(original)
            prefix_ids = {node["id"] for node in prefix["nodes"]}
            prefix_cdg = [edge for edge in prefix["edges"] if edge["kind"].upper() == "CDG"]
            prefix_ops = {
                node["id"] for node in prefix["nodes"]
                if operation_score(node)
            }
            prefix_cdg_to_op = [edge for edge in prefix_cdg if edge["dst"] in prefix_ops]
            selected = select_cluster(original, operation_score, LIMITS, cap) if original["nodes"] else None

            if not original["nodes"]:
                cause = "missing_cpg"
            elif not full_cdg:
                cause = "no_cdg_in_source"
            elif not full_ops:
                cause = "no_recognized_sink_operation_in_source"
            elif not full_cdg_to_op:
                cause = "no_cdg_to_recognized_sink_in_source"
            elif not prefix["nodes"]:
                cause = "empty_closed_prefix"
            elif not prefix_cdg:
                cause = "cdg_outside_closed_prefix"
            elif not prefix_ops:
                cause = "no_recognized_sink_operation_in_prefix"
            elif not prefix_cdg_to_op:
                cause = "no_cdg_to_recognized_sink_in_prefix"
            elif selected is None:
                cause = "selector_returned_none_despite_prefix_operation_guard"
            else:
                cause = "selector_returns_cluster_but_v5_still_no_usable_guard"
            local[cause] += 1
            total_counts[cause] += 1
            if len(examples[cause]) < 8:
                examples[cause].append(uid)
        no_guard_ids[dataset] = len(no_guard)
        diagnoses[dataset] = {
            "no_usable_guarded_evidence_rows": len(no_guard),
            "causes": dict(local), "example_ids": dict(examples),
            "source_row_fields": sorted(next(iter(source_by_id.values())).keys()) if source_by_id else [],
            "nonempty_joern_or_error_markers": dict(error_markers),
            "rows_with_nonempty_joern_or_error_markers_sample": error_examples,
            "edge_types_in_no_cdg_rows": dict(edge_types_without_cdg),
            "scope_note": "Static same-CPG opportunity classification; does not claim a selected cluster passes GuardedGraph feasibility checks or tokenizer budget.",
        }

    out = {
        "schema": "b1_h2_no_usable_evidence_diagnosis_v1",
        "candidate_manifest_sha256": __import__("hashlib").sha256((CANDIDATE / "manifest.json").read_bytes()).hexdigest(),
        "selection_limits": LIMITS,
        "max_operations": cap,
        "datasets": diagnoses,
        "cause_totals": dict(total_counts),
        "interpretation": "If recognized CDG-to-operation opportunities exist outside the prefix, a broader ranked cluster search may recover evidence. If the source lacks CDG, recognized operations, or CDG-to-operation edges, changing the selector cannot recover guarded evidence without changing the graph source or extractor semantics.",
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
