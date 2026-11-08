"""Correct B1-full TEST rendering without changing frozen specs or thresholds.

Require the graph algorithm to reproduce every existing validation graph before
building test candidates. Test code is copied exactly from the frozen B2 prompts.
"""
import hashlib
import io
import json
from pathlib import Path
import sys
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Runs-management/locked_continuations_20261108/b1_full_corrected_v4"
TOK = ROOT / "11_Arm_B1H2_Evidence/tokenizer_cache_v6/models--Qwen--Qwen3-Coder-30B-A3B-Instruct/snapshots/b2cff646eb4bb1d68355c01b18ae02e7cf42d120"
sys.path.insert(0, str(ROOT / "01_Author_Baseline_Unified/diagnostic_kit/src"))
from grace_diag.probes import render_graph, split_blocks, closed_prefix, format_nodes, NODE_HEAD, EDGE_HEAD
from grace_diag.token_budget import TokenCounter


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def rows(raw):
    return [json.loads(x) for x in raw.splitlines() if x.strip()]


def compact_graph(nodes, edges):
    normalized = []
    for e in edges:
        a = e.get("start", e.get("source", e.get("src")))
        b = e.get("end", e.get("target", e.get("dst")))
        if a is None or b is None:
            raise ValueError("Missing graph endpoint")
        normalized.append(dict(e, start=a, end=b, type=e.get("type", e.get("label", "CONNECTED_TO"))))
    selected, closed = closed_prefix(nodes, normalized, 40, 80)
    compact = []
    for i, node in enumerate(selected):
        text = str(node.get("code", "")).strip().replace("\n", " ")
        if len(text) > 40:
            text = text[:40] + "..."
        compact.append({"id": node.get("id", i), "type": node.get("type", node.get("label", "Node")), "code": text})
    assert format_nodes(compact) == format_nodes(selected)
    return compact, closed


def main():
    if OUT.exists():
        raise FileExistsError("Preserve previous candidate; use a new output version")
    OUT.mkdir(parents=True)
    counter = TokenCounter(str(TOK))
    inventory = []
    report = {"classification": "Post-registration operational correction of a test renderer; no frozen spec, threshold, arm, model or selection rule changes.", "validation": [], "test": []}
    validation_path = ROOT / "Runs-management/kaggle_validation_6arms_20261104/grace_b1_full_validation_inputs.zip"
    with ZipFile(validation_path) as outer:
        validation = {}
        for ds in ["devign", "reveal"]:
            with ZipFile(io.BytesIO(outer.read(f"seed_42/{ds}_validation.zip"))) as inner:
                validation[ds] = {r["id"]: r for r in rows(inner.read("prompts.jsonl"))}
    for split in ["validation", "test"]:
        for ds in ["devign", "reveal"]:
            path = ROOT / f"01_Author_Baseline_Unified/output/local_full/bundles_recovered_joern_final_20261031/{ds}/{split}/specs.jsonl"
            inventory.append({"path": str(path.relative_to(ROOT)), "sha256": sha(path.read_bytes())})
            if split == "test":
                directory = ROOT / "Runs-management/kernel_outputs_harvest"
                with ZipFile(directory / f"huuhieu3333_grace-b2-rep-test/b2_rep_test_bundles/42_{ds}_test.zip") as z:
                    reference = {r["id"]: r for r in rows(z.read("prompts.jsonl"))}
                with ZipFile(directory / f"huuhieu3333_grace-b1-full-test/b1_full_test_bundles/42_{ds}_test.zip") as z:
                    old = {r["id"]: r for r in rows(z.read("prompts.jsonl"))}
                output = []
                changes = []
            mismatches = []
            max_graph = max_code = max_context = 0
            n = 0
            with path.open(encoding="utf-8") as stream:
                for line in stream:
                    if not line.strip():
                        continue
                    spec = json.loads(line)
                    uid = str(spec["id"])
                    # No target label is passed to the graph renderer.
                    nodes, edges = compact_graph(spec.get("nodes", []), spec.get("edges", []))
                    graph, meta = render_graph("fill", {"id": uid, "nodes": nodes, "edges": edges},
                                               counter, 1500, {"nodes": 40, "edges": 80}, 42, None)
                    graph = graph or f"{NODE_HEAD}\n\n{EDGE_HEAD}\n"
                    max_graph = max(max_graph, counter.count(graph))
                    assert counter.count(graph) <= 1500
                    if split == "validation":
                        existing = split_blocks(validation[ds][uid]["prompt"])
                        reproduced = "\n\n".join([existing["role"], existing["code"], existing["question"], graph,
                                                   "The following is an example, and it is .\n", existing["answer"]])
                        if existing["graph"] != graph or reproduced != validation[ds][uid]["prompt"]:
                            mismatches.append(uid)
                        assert counter.count(existing["code"]) <= 3000
                    else:
                        original = old[uid]
                        blocks = split_blocks(original["prompt"])
                        code = split_blocks(reference[uid]["prompt"])["code"]
                        assert counter.count(code) <= 3000
                        parts = [blocks["role"], code, blocks["question"]]
                        if graph:
                            parts.append(graph)
                        if blocks["demo"]:
                            parts.append("The following is an example, and it is .\n")
                        parts.append(blocks["answer"])
                        prompt = "\n\n".join(parts)
                        count = counter.count_chat(prompt)
                        assert count + 64 <= 8192
                        new_blocks = split_blocks(prompt)
                        assert new_blocks["code"] == code and new_blocks["graph"] == graph
                        assert all(new_blocks[k] == blocks[k] for k in ["role", "question", "demo", "answer"])
                        row = dict(original)
                        row.update(prompt=prompt, prompt_sha256=sha(prompt.encode()),
                                   tokens={"code": counter.count(code), "graph": counter.count(graph), "demo": 0, "total": count, "approx": False},
                                   graph_missing=not bool(spec.get("nodes")))
                        output.append(row)
                        if row["prompt_sha256"] != original["prompt_sha256"]:
                            changes.append(uid)
                        max_code = max(max_code, counter.count(code))
                        max_context = max(max_context, count)
                    n += 1
            if split == "validation":
                r = {"dataset": ds, "n": n, "graph_mismatches": mismatches, "max_graph_tokens": max_graph}
                report["validation"].append(r)
                print("VALIDATION", ds, n, "graph mismatches", len(mismatches), flush=True)
                if mismatches:
                    (OUT / "validation_mismatch.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
                    raise ValueError("Graph renderer does not reproduce validation; do not launch test")
            else:
                assert n == len(reference) == len(old) == len(output)
                raw = ("\n".join(json.dumps(r, ensure_ascii=False, separators=(",", ":"), allow_nan=False) for r in output) + "\n").encode()
                (OUT / f"{ds}_test_prompts.jsonl").write_bytes(raw)
                report["test"].append({"dataset": ds, "n": n, "changed_prompt_ids": changes, "changed_count": len(changes),
                                       "prompts_sha256": sha(raw), "max_code_tokens": max_code, "max_graph_tokens": max_graph, "max_chat_tokens": max_context,
                                       "target_code_reference": "exact frozen-donor B2 prompt target block", "old_output_policy": "preserve all historical records; fresh runtime-locked census after renderer correction"})
                print("TEST", ds, n, "changed", len(changes), "max code/graph/chat", max_code, max_graph, max_context, flush=True)
    report["frozen_specs"] = inventory
    for source in inventory:
        assert sha((ROOT / source["path"]).read_bytes()) == source["sha256"]
    (OUT / "audit.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
