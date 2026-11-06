"""Exploratory feasibility check: derive control dependence from frozen CFGs."""
from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
ARM = ROOT / "11_Arm_B1H2_Evidence"
RUNS = ROOT / "Runs-management"
H2 = ROOT.parent / "GRACE-H2-GuardedEvidence"
sys.path.insert(0, str(RUNS))
sys.path.insert(0, str(H2))
from remediate_validation_extensions import operation_score

SOURCE = ROOT / "01_Author_Baseline_Unified/output/local_full/bundles_recovered_joern_final_20261031"
CANDIDATE = ARM / "validation_h2_cluster_v5_20261104"
OUT = ARM / "audit/b1_h2_derived_cdg_feasibility_20261105.json"


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


def derive_cdg(nodes: dict[str, dict], edges: list[dict]):
    ids = set(nodes)
    exit_node = "__VIRTUAL_EXIT__"
    cfg = nx.DiGraph()
    cfg.add_nodes_from(ids)
    explicit = set()
    for edge in edges:
        src, dst = str(edge["start"]), str(edge["end"])
        kind = str(edge["type"]).upper()
        if kind == "CDG" and src in ids and dst in ids:
            explicit.add((src, dst))
        if kind == "CFG" and src in ids and dst in ids:
            cfg.add_edge(src, dst)
    terminals = [node for node in ids if cfg.out_degree(node) == 0]
    if not terminals:
        return set(), explicit, {"status": "no_cfg_terminal", "nodes": len(ids)}
    cfg.add_node(exit_node)
    cfg.add_edges_from((node, exit_node) for node in terminals)
    reverse_cfg = cfg.reverse(copy=False)
    reachable = nx.descendants(reverse_cfg, exit_node) | {exit_node}
    if len(reachable) != len(ids) + 1:
        return set(), explicit, {"status": "nodes_without_path_to_exit", "nodes": len(ids), "live_nodes": len(reachable)-1}
    # Immediate dominators in the reversed CFG are immediate post-dominators.
    ipdom = nx.immediate_dominators(reverse_cfg, exit_node)
    tree = nx.DiGraph()
    tree.add_nodes_from(ipdom)
    tree.add_edges_from((parent, child) for child, parent in ipdom.items() if child != exit_node)
    tin, tout = {}, {}
    clock = 0
    stack = [(exit_node, False)]
    while stack:
        node, leaving = stack.pop()
        if leaving:
            tout[node] = clock
            continue
        tin[node] = clock
        clock += 1
        stack.append((node, True))
        stack.extend((child, False) for child in tree.successors(node))
    def postdominates(a, b):
        return tin[b] <= tin[a] and tout[a] <= tout[b]
    derived = set()
    for branch in ids:
        stop = ipdom.get(branch)
        if stop is None:
            continue
        for first in cfg.successors(branch):
            if first == exit_node or postdominates(first, branch):
                continue
            runner, seen = first, set()
            while runner != stop and runner != exit_node and runner not in seen:
                seen.add(runner)
                derived.add((branch, runner))
                runner = ipdom.get(runner, exit_node)
    return derived, explicit, {
        "status": "ok", "nodes": len(ids), "cfg_edges": cfg.number_of_edges() - len(terminals),
        "terminals": len(terminals),
    }

def main():
    aggregate = Counter()
    examples = defaultdict(list)
    skipped = Counter()
    samples = {}
    for dataset in ("devign", "reveal"):
        candidate_rows = list(rows(CANDIDATE / dataset / "validation/B1-H2/42/prompts.jsonl"))
        no_guard = {r["id"] for r in candidate_rows if r["evidence"]["h2"].get("no_usable_evidence")}
        source_by_id = {r["id"]: r for r in rows(SOURCE / dataset / "validation/specs.jsonl")}
        chosen = sorted(no_guard)
        sample_metrics = Counter()
        for uid in chosen:
            original = source_by_id[uid]
            nodes = {str(node["id"]): node for node in original["nodes"]}
            derived, explicit, stats = derive_cdg(nodes, original["edges"])
            if stats["status"] != "ok":
                skipped[(dataset, stats["status"])] += 1
                continue
            operations = {nid for nid, node in nodes.items() if recognized(node)}
            derived_op = {(a, b) for a, b in derived if b in operations}
            explicit_op = {(a, b) for a, b in explicit if b in operations}
            sample_metrics["rows_analyzed"] += 1
            sample_metrics["rows_with_derived_guard_to_operation"] += bool(derived_op)
            sample_metrics["rows_with_explicit_guard_to_operation"] += bool(explicit_op)
            sample_metrics["derived_guard_to_operation_edges"] += len(derived_op)
            sample_metrics["explicit_guard_to_operation_edges"] += len(explicit_op)
            if len(examples[(dataset, "derived_guard_to_operation")]) < 12 and derived_op:
                examples[(dataset, "derived_guard_to_operation")].append({
                    "id": uid, "derived_guard_to_operation_edges": len(derived_op),
                    "explicit_guard_to_operation_edges": len(explicit_op), "stats": stats,
                })
        # Independently compare derived relations with Joern's explicit CDG on
        # a stable calibration sample from rows that already have CDG.
        calibration_ids = sorted(
            r["id"] for r in candidate_rows
            if r["id"] not in no_guard
            and any(str(e["type"]).upper() == "CDG" for e in source_by_id[r["id"]]["edges"])
        )[:100]
        tp = derived_n = explicit_n = calibration_ok = 0
        for uid in calibration_ids:
            original = source_by_id[uid]
            nodes = {str(node["id"]): node for node in original["nodes"]}
            derived, explicit, stats = derive_cdg(nodes, original["edges"])
            if stats["status"] != "ok":
                skipped[(dataset, "calibration_" + stats["status"])] += 1
                continue
            calibration_ok += 1
            tp += len(derived & explicit)
            derived_n += len(derived)
            explicit_n += len(explicit)
        samples[dataset] = {
            "no_usable_evidence_total": len(no_guard),
            "derived_cdg_analysis": dict(sample_metrics),
            "explicit_cdg_calibration": {
                "rows_selected": len(calibration_ids), "rows_analyzed": calibration_ok,
                "derived_edges": derived_n, "explicit_edges": explicit_n,
                "overlap_edges": tp,
                "precision_vs_explicit": tp / derived_n if derived_n else None,
                "recall_vs_explicit": tp / explicit_n if explicit_n else None,
            },
            "sample_examples": examples[(dataset, "derived_guard_to_operation")],
        }
        aggregate.update({f"{dataset}/{k}": v for k, v in sample_metrics.items()})

    result = {
        "schema": "b1_h2_derived_cdg_feasibility_v2",
        "candidate_manifest_sha256": hashlib.sha256((CANDIDATE / "manifest.json").read_bytes()).hexdigest(),
        "scope": "All validation rows with no usable H2 evidence; calibration against up to 100 rows per dataset with explicit CDG; no labels, scores, thresholds, or test data used.",
        "algorithm": "Compute post-dominators from CFG with a virtual exit; derive control-dependence edges using the standard post-dominator-tree path rule; skip graphs not connected to a terminal.",
        "datasets": samples,
        "skipped_graphs": {f"{d}/{reason}": n for (d, reason), n in skipped.items()},
        "warning": "Exploratory feasibility only. Derived edges are not present in the frozen CPG and are not a registered-prompt candidate or inference.",
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
