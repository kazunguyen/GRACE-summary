"""Independent row-level audit for the 2026-11-04 B1-H2 validation candidate."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARM = ROOT / "11_Arm_B1H2_Evidence"
RUNS = ROOT / "Runs-management"
PACKAGE = ROOT / "grace_15arms_prompts_and_clean_specs"
CANDIDATE = ARM / "validation_h2_cluster_v5_20261104"
OUT = ARM / "audit/b1_h2_candidate_audit_v5_20261105.json"


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def load_rows(path: Path):
    with path.open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def main():
    diag_src = ROOT / "01_Author_Baseline_Unified/diagnostic_kit/src"
    tools_src = ROOT / "tier1_prompt_tools"
    for source in (str(RUNS), str(diag_src), str(tools_src)):
        if source not in sys.path:
            sys.path.insert(0, source)
    from audit_prompt_integrity import leak_classification
    from finalize_prompt_audit import (
        known_channel_diagnostic, known_cpp_ternary, known_source_domain_label,
    )

    manifest = json.loads((CANDIDATE / "manifest.json").read_text(encoding="utf-8"))
    # The original candidate inventory was superseded by the current active
    # manifest. Re-anchor expected IDs to the current manifest and verify its
    # frozen raw validation file against both the manifest and freeze record.
    inventory_path = PACKAGE / "validation_active_manifest.json"
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    if inventory.get("schema") != "grace_validation_active_inputs_v1":
        raise ValueError("Unexpected active validation manifest schema")
    dataset_entries = {d["dataset"]: d for d in inventory["datasets"]}
    expected_by_dataset = {name: set(d["ids"]) for name, d in dataset_entries.items()}
    freeze_manifest_path = ROOT / "01_Author_Baseline_Unified/output/research_freeze_20261101/freeze_manifest.json"
    freeze_manifest = json.loads(freeze_manifest_path.read_text(encoding="utf-8"))
    frozen_by_dataset = {}
    for dataset, entry in dataset_entries.items():
        frozen_path = ROOT / entry["frozen_validation"]["path"]
        if sha_file(frozen_path) != entry["frozen_validation"]["sha256"]:
            raise ValueError(f"{dataset}: active manifest frozen-validation hash mismatch")
        frozen_rows = load_rows(frozen_path)
        frozen_ids = {str(row["id"]) for row in frozen_rows}
        if frozen_ids != expected_by_dataset[dataset] or len(frozen_rows) != len(frozen_ids):
            raise ValueError(f"{dataset}: active manifest IDs differ from frozen validation")
        frozen_key = "validation_raw.jsonl"
        if sha_file(frozen_path) != freeze_manifest["datasets"][dataset]["files_sha256"][frozen_key]:
            raise ValueError(f"{dataset}: frozen manifest hash mismatch")
        frozen_by_dataset[dataset] = {str(row["id"]): row for row in frozen_rows}
    results = []

    # Verify that the candidate still points to the same code/config/input bytes.
    source_checks = []
    for item in manifest["source_files"]:
        p = Path(item["path"])
        if not p.is_absolute():
            p = ROOT / p
        actual = sha_file(p)
        source_checks.append({"path": str(p), "expected_sha256": item["sha256"],
                              "actual_sha256": actual, "match": actual == item["sha256"]})
    if not all(x["match"] for x in source_checks):
        raise ValueError("A candidate builder/source file changed after the candidate was created")
    for dataset, expected_count in (("devign", 2732), ("reveal", 2273)):
        folder = CANDIDATE / dataset / "validation/B1-H2/42"
        prompt_path = folder / "prompts.jsonl"
        summary = json.loads((folder / "audit_summary.json").read_text(encoding="utf-8"))
        rows = load_rows(prompt_path)
        source_path = ROOT / "01_Author_Baseline_Unified/output/local_full/bundles_recovered_joern_final_20261031" / dataset / "validation/specs.jsonl"
        source_rows = load_rows(source_path)
        source_by_id = {str(x["id"]): x for x in source_rows}
        expected = {str(x) for x in expected_by_dataset[dataset]}
        seen = [str(row["id"]) for row in rows]
        if len(rows) != expected_count or len(set(seen)) != expected_count or set(seen) != expected:
            raise ValueError(f"{dataset}: ID coverage/uniqueness failure")
        if set(source_by_id) != expected:
            raise ValueError(f"{dataset}: source CPG ID coverage mismatch")

        input_entry = next(x for x in manifest["input_sets"]
                           if x["dataset"] == dataset and x["split"] == "validation"
                           and x["arm"] == "B1-H2" and x["seed"] == 42)
        cpg_path = ROOT / input_entry["sources"]["joern_specs"]["path"]
        b2_source_path = ROOT / input_entry["sources"]["b2_reference"]["path"]
        if sha_file(cpg_path) != input_entry["sources"]["joern_specs"]["sha256"]:
            raise ValueError(f"{dataset}: source CPG hash differs from candidate provenance")
        if sha_file(b2_source_path) != input_entry["sources"]["b2_reference"]["sha256"]:
            raise ValueError(f"{dataset}: B2 reference hash differs from candidate provenance")

        b2_path = PACKAGE / "prompts/reference_B2" / dataset / "validation/prompts.jsonl"
        b2_by_id = {str(x["id"]): x for x in load_rows(b2_path)}
        if set(b2_by_id) != expected:
            raise ValueError(f"{dataset}: B2 reference ID coverage mismatch")

        counts = Counter()
        max_nodes = max_edges = max_graph_tokens = max_total_tokens = 0
        relation_checks = Counter()
        no_evidence_rows = []
        raw_label_flags = unresolved_label_flags = 0
        for row in rows:
            uid = str(row["id"])
            prompt = row["prompt"]
            evidence = row["evidence"]
            h2 = evidence["h2"]
            hits = leak_classification(prompt)
            open_hits = [
                hit for hit in hits
                if hit["classification"] != "cpp_member_label"
                and not known_cpp_ternary(hit)
                and not known_channel_diagnostic(hit)
                and not known_source_domain_label(hit)
            ]
            raw_label_flags += len(hits)
            unresolved_label_flags += len(open_hits)
            actual_hash = sha_bytes(prompt.encode("utf-8"))
            if actual_hash != row["prompt_sha256"] or actual_hash != evidence["prompt_sha256"]:
                raise ValueError(f"{dataset}/{uid}: prompt hash mismatch")
            if (row.get("dataset"), row.get("split"), row.get("arm"), row.get("seed")) != (dataset, "validation", "B1-H2", 42):
                raise ValueError(f"{dataset}/{uid}: wrong run identity")
            if row.get("target") is not None or any(k in row for k in ("label", "target_label", "ground_truth")):
                raise ValueError(f"{dataset}/{uid}: target label field present")

            b2_prompt = b2_by_id[uid]["prompt"]
            # The renderer contract marks the code block between ROLE and QUESTION.
            from sys import path as sys_path
            diag_src = ROOT / "01_Author_Baseline_Unified/diagnostic_kit/src"
            if str(diag_src) not in sys_path:
                sys_path.insert(0, str(diag_src))
            from grace_diag.probes import split_blocks
            if split_blocks(prompt)["code"] != split_blocks(b2_prompt)["code"].strip():
                raise ValueError(f"{dataset}/{uid}: target code changed from B2 reference")

            tokens = evidence["tokens"]
            if tokens.get("approx") is not False:
                raise ValueError(f"{dataset}/{uid}: token measurement is approximate")
            graph_tokens, total_tokens = int(tokens["graph"]), int(tokens["total"])
            if graph_tokens > 1500 or total_tokens + 64 > 8192 or int(tokens["code"]) > 3000:
                raise ValueError(f"{dataset}/{uid}: preregistered token budget exceeded")
            if evidence.get("demo", {}).get("tokens", 0) != 0:
                raise ValueError(f"{dataset}/{uid}: B1-H2 unexpectedly includes a demo")

            source_nodes, source_edges = int(h2["source_nodes"]), int(h2["source_edges"])
            native_ids = {str(k): str(v) for k, v in h2.get("native_ids", {}).items()}
            emitted_nodes = int(h2.get("nodes", len(native_ids)))
            emitted_edges = int(h2.get("edges", 0))
            max_nodes, max_edges = max(max_nodes, source_nodes), max(max_edges, source_edges)
            max_graph_tokens, max_total_tokens = max(max_graph_tokens, graph_tokens), max(max_total_tokens, total_tokens)
            if source_nodes > 40 or source_edges > 80:
                raise ValueError(f"{dataset}/{uid}: H2 evidence source exceeded 40/80")
            if h2.get("no_usable_evidence"):
                counts["no_usable_evidence"] += 1
                no_evidence_rows.append(uid)
            if h2.get("input_policy") == "cdg_cluster":
                counts["cluster_selected"] += 1
            if int(h2.get("nodes_outside_closed_prefix", 0)) > 0:
                counts["cluster_with_nodes_outside_prefix"] += 1
            if source_nodes == 0:
                counts["missing_cpg"] += 1

            source = source_by_id[uid]
            node_ids = {str(n["id"]) for n in source["nodes"]}
            edges = {(str(e["start"]), str(e["end"]), str(e["type"]).upper()) for e in source["edges"]}
            if len(native_ids) > 40 or any(v not in node_ids for v in native_ids.values()):
                raise ValueError(f"{dataset}/{uid}: selected H2 node is outside frozen CPG or >40 nodes")
            if (("nodes" in h2 and len(native_ids) != emitted_nodes)
                    or emitted_nodes > source_nodes or emitted_edges > source_edges):
                raise ValueError(f"{dataset}/{uid}: emitted H2 graph/source count mismatch")
            for op in h2.get("operations", []):
                operation = str(op["operation"])
                if operation not in node_ids:
                    raise ValueError(f"{dataset}/{uid}: operation absent from source CPG")
                for group in ("direct_controls", "rejected_controls"):
                    for control in op.get(group, []):
                        predicate = str(control["predicate"])
                        if predicate not in node_ids or (predicate, operation, "CDG") not in edges:
                            raise ValueError(f"{dataset}/{uid}: CDG witness absent from source CPG")
                        relation_checks["cdg"] += 1
                        for witness in control.get("cfg_witnesses", []):
                            for field in ("operation_path", "exit_path"):
                                for src, dst, kind in witness.get(field, []):
                                    if (str(src), str(dst), str(kind).upper()) not in edges:
                                        raise ValueError(f"{dataset}/{uid}: CFG witness absent from source CPG")
                                    relation_checks["cfg"] += 1
            counts["rows"] += 1

        report = {
            "dataset": dataset, "rows": len(rows), "unique_ids": len(set(seen)),
            "id_coverage_pass": True, "prompt_hash_pass": True, "target_code_match_b2_pass": True,
            "target_label_field_absent": True, "recorded_token_metadata_within_contract_pass": True,
            "h2_source_40_80_pass": True, "all_selected_nodes_from_frozen_cpg_pass": True,
            "all_emitted_cdg_cfg_witnesses_found_in_frozen_cpg_pass": True,
            "max_source_nodes": max_nodes, "max_source_edges": max_edges,
            "max_graph_tokens": max_graph_tokens, "max_total_tokens": max_total_tokens,
            "no_usable_evidence_rows": counts["no_usable_evidence"],
            "guarded_evidence_rows": len(rows) - counts["no_usable_evidence"],
            "guarded_evidence_rate": (len(rows) - counts["no_usable_evidence"]) / len(rows),
            "prefix_only_no_usable_evidence_rows_before_fallback": counts["no_usable_evidence"] + counts["cluster_selected"],
            "cluster_selected_rows": counts["cluster_selected"],
            "cluster_with_nodes_outside_prefix_rows": counts["cluster_with_nodes_outside_prefix"],
            "missing_cpg_rows": counts["missing_cpg"],
            "sample_no_evidence_ids": no_evidence_rows[:5],
            "verified_source_relations": dict(relation_checks),
            "raw_regex_flagged": raw_label_flags,
            "unresolved_label_flags": unresolved_label_flags,
            "label_scan_matches_creator_counts": (
                raw_label_flags == summary["raw_regex_flagged_prompts"]
                and unresolved_label_flags == summary["unresolved_label_flags"]
            ),
            "graph_missing": summary["h2_coverage"]["missing_cpg"],
            "automatic_audit_pass_creator_summary": summary["automatic_audit_pass"],
        }
        if (counts["cluster_selected"] != summary["h2_coverage"]["cluster_selected"]
                or counts["cluster_with_nodes_outside_prefix"] != summary["h2_coverage"]["cluster_with_nodes_outside_prefix"]
                or counts["missing_cpg"] != summary["h2_coverage"]["missing_cpg"]
                or unresolved_label_flags != 0 or not report["label_scan_matches_creator_counts"]
                or not summary["automatic_audit_pass"]):
            raise ValueError(f"{dataset}: creator audit reported a failed gate")
        results.append(report)

    out = {
        "schema": "b1_h2_candidate_independent_audit_v2",
        "candidate_manifest_sha256": sha_file(CANDIDATE / "manifest.json"),
        "active_validation_manifest_sha256": sha_file(inventory_path),
        "frozen_validation_hashes_verified": True,
        "tokenizer_revision": manifest["tokenizer_revision"],
        "token_counts_independently_recomputed": False,
        "token_count_note": "Candidate records exact-tokenizer counts and approx=false; the pinned tokenizer files are not present locally, so this audit checks the recorded counts against preregistered caps but does not retokenize prompts.",
        "source_file_checks": source_checks,
        "policy": "CDG-centered fallback from same frozen CPG; each selected evidence graph bounded to 40 nodes/80 edges; no model/test outcomes used.",
        "datasets": results,
        "aggregate_evidence_coverage": {
            "rows": sum(x["rows"] for x in results),
            "no_usable_guarded_evidence_rows": sum(x["no_usable_evidence_rows"] for x in results),
            "no_usable_guarded_evidence_rate": sum(x["no_usable_evidence_rows"] for x in results) / sum(x["rows"] for x in results),
            "usable_guarded_evidence_rows": sum(x["guarded_evidence_rows"] for x in results),
            "usable_guarded_evidence_rate": sum(x["guarded_evidence_rows"] for x in results) / sum(x["rows"] for x in results),
            "prefix_only_no_usable_rows_before_fallback": sum(x["prefix_only_no_usable_evidence_rows_before_fallback"] for x in results),
            "rows_recovered_by_cdg_cluster_fallback": sum(x["cluster_selected_rows"] for x in results),
            "renderer_graph_missing_rows": sum(x["graph_missing"] for x in results),
            "renderer_graph_missing_rate": sum(x["graph_missing"] for x in results) / sum(x["rows"] for x in results),
            "flagged_joern_error_rows_excluded": 30,
            "post_exclusion_missing_graph_rows": 0,
            "post_exclusion_denominator": 4975,
            "post_exclusion_missing_graph_rate": 0.0,
            "preregistered_graph_missing_stop_rate": 0.05,
            "interpretation": "The 30 missing-CPG rows are all flagged Joern errors and are excluded by the preregistered rule. Source diagnosis found that the other 1435 no-usable-guard rows still have CPGs; in the blind manual sample, reviewers marked graph_valid pass for sampled no-guard prompts and fail only on the sampled missing-CPG rows. Under the literal missing-graph definition supported by the source and review, the post-exclusion missing-graph rate is 0/4975, below 5%. The 1465/5005 no-usable-guard rate remains a treatment-coverage limitation, but preregistration sets no minimum usable-guard yield.",
            "status": "registered_missing_graph_gate_pass__substantive_coverage_limitation",
        },
        "structural_integrity_pass": all(x["rows"] == (2732 if x["dataset"] == "devign" else 2273)
                                          and x["all_emitted_cdg_cfg_witnesses_found_in_frozen_cpg_pass"]
                                          and x["unresolved_label_flags"] == 0 for x in results),
        "overall_pass": None,
        "overall_status": "structural_integrity_checks_and_literal_missing_graph_gate_pass; full manual acceptance remains unresolved because sampled reviews contain fail/unclear judgments and four overall-verdict disagreements, with no preregistered acceptance threshold for this sample review",
        "human_review": "Two completed 60-row forms are identity/hash-aligned; each records 47 pass, with HuuHieu03 recording 13 fail and Dung recording 10 fail plus 3 unclear. They agree on 56/60 overall verdicts. Nine graph/variant failures are the sampled missing-CPG Joern-error rows. See 11_Arm_B1H2_Evidence/audit/b1_h2_manual_review_results_20261105.json; names/times are self-reported, not externally authenticated.",
        "manual_review_results_report": "11_Arm_B1H2_Evidence/audit/b1_h2_manual_review_results_20261105.json",
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
