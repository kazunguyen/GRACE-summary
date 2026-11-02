"""Offline tests with synthetic data; no model download, inference or full export."""
import hashlib
import json
from pathlib import Path
import sys
import zipfile

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import prepare_shuf as sh
from grace_diag.probes import DonorPool, render_arm


class TinyTokenizer:
    chat_template = "synthetic-test-template"

    def encode(self, text, add_special_tokens=False):
        return list(text.encode("utf-8"))

    def apply_chat_template(self, messages, tokenize=True, add_generation_prompt=True):
        return self.encode(messages[-1]["content"]) + [0, 1, 2]


def graph(n, prefix="g"):
    nodes = [{"id": f"{prefix}{i}", "type": "CALL", "code": f"f{i}(x)"} for i in range(n)]
    edges = [{"start": f"{prefix}{i}", "end": f"{prefix}{i+1}", "type": "CFG"} for i in range(n - 1)]
    return nodes, edges


def jsonl(path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r) + "\n" for r in records), encoding="utf-8")


@pytest.fixture
def counter():
    c = sh.TokenCounter(None)
    c.tok, c.approx = TinyTokenizer(), False
    return c


@pytest.fixture
def bank(tmp_path):
    donors = []
    for i, n in enumerate([0, 20, 22, 40, 200]):
        nodes, edges = graph(n, f"d{i}_")
        donors.append({"function_uid": f"devign:train:{i}", "func": "int d(){return 0;}",
                       "target": i % 2, "nodes": nodes, "edges": edges})
    root = tmp_path / "frozen"
    path = root / "devign/donors.jsonl"
    jsonl(path, donors)
    freeze = {"datasets": {"devign": {"donor_count": len(donors),
                                          "files_sha256": {"donors.jsonl": sh.sha256(path)}}}}
    sh.write_json(root / "freeze_manifest.json", freeze)
    return root, freeze, donors


def reference(spec, counter):
    clean = sh.convert_graph(spec)
    b2 = render_arm(clean, "B2", counter=counter, budget=sh.BUDGET, graph_prefix=sh.PREFIX)
    prompt, evidence = sh.render_paired("B1", spec, b2.prompt, counter)
    return {"prompt": prompt, "prompt_sha256": sh.digest(prompt), "truncated": evidence["truncated"]}, b2


def spec(uid="devign:validation:0", n=20):
    nodes, edges = graph(n, "target_")
    return {"id": uid, "query_code": "int target(){return 7;}", "nodes": nodes, "edges": edges,
            "demonstrations": [{"function_uid": "devign:train:3", "func": "int d(){return 0;}", "target": 0}],
            "label": 1}


def clean(s):
    return {k: s[k] for k in ("id", "query_code", "nodes", "edges")}


@pytest.mark.parametrize("seed", sh.SEEDS)
def test_sampling_matches_existing_pool_and_repeats(bank, seed):
    root, freeze, donors = bank
    pool = sh.FrozenDonors("devign", root, freeze)
    index, info = pool.select("devign:validation:0", seed, 20)
    _, _, expected = DonorPool(donors).shuffle_graph("devign:validation:0", seed, 20,
                                                   exclude_uid="devign:validation:0")
    assert info["donor_uid"] == expected["donor_uid"] == pool.uids[index]
    assert pool.select("devign:validation:0", seed, 20) == (index, info)
    assert 18 <= info["donor_cpg_nodes"] <= 22


def test_matching_uses_full_graph_size_and_relaxes(bank):
    root, freeze, _ = bank
    pool = sh.FrozenDonors("devign", root, freeze)
    index, info = pool.select("devign:validation:0", 42, 200)
    assert pool.counts[index] == 200  # not the rendered 40-node ceiling
    _, info = pool.select("devign:validation:0", 42, 100)
    assert info["matching_status"] == "relaxed" and info["tolerance_used"] > 0.1
    with pytest.raises(ValueError, match="Missing target"):
        pool.select("x", 42, 0)


def test_selected_graph_matches_b1_fitter(bank, counter):
    root, freeze, donors = bank
    pool = sh.FrozenDonors("devign", root, freeze)
    for index in range(1, len(donors)):
        text, info = pool.graph(index, counter)
        expected, original = sh.render_graph("prefix", donors[index], counter, 1500, sh.PREFIX, 42, None)
        assert text == expected
        assert info["rendered_nodes"] == original["rendered_nodes"] <= 40
        assert info["rendered_edges"] == original["rendered_edges"] <= 80
        assert counter.count(text) <= 1500


def test_only_graph_changes_and_no_input_mutation(bank, counter):
    root, freeze, _ = bank
    pool = sh.FrozenDonors("devign", root, freeze)
    s = spec()
    b1, _ = reference(s, counter)
    before = json.dumps(s, sort_keys=True)
    for seed in sh.SEEDS:
        prompt, audit, truncated = sh.shuffle_one(clean(s), b1, pool, counter, seed)
        p, _, suffix = sh.b1_scaffold(prompt, s, counter)
        old_p, _, old_suffix = sh.b1_scaffold(b1["prompt"], s, counter)
        assert (p, suffix) == (old_p, old_suffix)
        assert prompt != b1["prompt"]
        assert audit["code_unchanged"] and audit["non_graph_blocks_unchanged"]
        assert audit["tokens"]["total"] == counter.count_chat(prompt)
        assert audit["tokens"]["code"] == counter.count(s["query_code"])
        assert audit["tokens"]["demo"] == 0 and not truncated["demo"]
    assert before == json.dumps(s, sort_keys=True)
    with pytest.raises(ValueError, match="labels"):
        sh.shuffle_one(s, b1, pool, counter, 42)


def test_missing_target_preserved_and_never_samples(counter):
    s = spec(n=0)
    b1, _ = reference(s, counter)
    class ForbiddenPool:
        def select(self, *args):
            raise AssertionError("Missing target must not sample")
    prompt, audit, _ = sh.shuffle_one(clean(s), b1, ForbiddenPool(), counter, 42)
    assert prompt == b1["prompt"]
    assert audit["matching_status"] == "target_graph_missing"
    assert audit["donor_uid"] is None


def test_bank_tamper_detected(bank):
    root, freeze, _ = bank
    path = root / "devign/donors.jsonl"
    with path.open("a", encoding="utf-8") as out:
        out.write("\n")
    with pytest.raises(ValueError, match="SHA256"):
        sh.FrozenDonors("devign", root, freeze)


def test_manual_sample_exact_even_with_sparse_strata():
    items = [{"id": str(i), "seed": sh.SEEDS[i % 3], "tokens": {"total": i + 100},
              "graph_truncated": i % 17 == 0} for i in range(61)]
    chosen = sh.manual_sample(items)
    assert len(chosen) == len({(r["id"], r["seed"]) for r in chosen}) == 30
    assert {r["seed"] for r in chosen} == set(sh.SEEDS)
    assert sh.manual_sample(items) == chosen
    assert len(sh.manual_sample(items[:5])) == 5


@pytest.fixture
def sources(tmp_path, bank, counter):
    frozen, freeze, _ = bank
    b1_root, b2_root = tmp_path / "b1", tmp_path / "b2"
    specs = [spec(), spec("devign:validation:1", n=0)]
    b1_rows, b2_rows = [], []
    for s in specs:
        b1, b2 = reference(s, counter)
        b1_rows.append({"id": s["id"], "label": s["label"], **b1})
        b2_rows.append({"id": s["id"], "label": s["label"], "prompt": b2.prompt, "prompt_sha256": sh.digest(b2.prompt)})
    f2 = b2_root / "devign/validation"
    jsonl(f2 / "specs.jsonl", specs)
    jsonl(f2 / "prompts.jsonl", b2_rows)
    meta = {"arm": "B2", "dataset": "devign", "split": "validation", "count": 2,
            "tokenizer": "synthetic", "tokenizer_revision": sh.REVISION,
            "model_repo": "synthetic-model", "quantization": "test",
            "spec_sha256": sh.sha256(f2 / "specs.jsonl"), "prompts_sha256": sh.sha256(f2 / "prompts.jsonl")}
    sh.write_json(f2 / "bundle_manifest.json", meta)
    f1 = b1_root / "devign/validation"
    jsonl(f1 / "prompts.jsonl", b1_rows)
    sh.write_json(f1 / "bundle_manifest.json", {**meta, "arm": "B1", "prompt_variant": "b1_b2_empty_demo_v1",
        "prompts_sha256": sh.sha256(f1 / "prompts.jsonl"), "graph_prefix": sh.PREFIX, "token_budget": sh.BUDGET,
        "reference_b2_sha256": {k: sh.sha256(f2 / v) for k, v in
                                  {"specs": "specs.jsonl", "prompts": "prompts.jsonl", "manifest": "bundle_manifest.json"}.items()}})
    target_path = frozen / "devign/validation_manifest.jsonl"
    jsonl(target_path, [{"id": s["id"], "label": s["label"], "code_sha256": sh.digest(s["query_code"])} for s in specs])
    freeze["datasets"]["devign"]["files_sha256"][target_path.name] = sh.sha256(target_path)
    sh.write_json(frozen / "freeze_manifest.json", freeze)
    return b1_root, b2_root, frozen


def test_export_pipeline_and_bundle_provenance(sources, tmp_path):
    b1, b2, frozen = sources
    out = tmp_path / "out"
    archive = sh.prepare(b1, b2, frozen, out, TinyTokenizer(), runs=[("devign", "validation")])
    assert archive.is_file() and not (out / "INCOMPLETE.txt").exists()
    assert len(list(sh.rows(out / "audit/devign/validation/manual_sample.jsonl"))) == 6
    for seed in sh.SEEDS:
        folder = out / f"seed_{seed}/devign/validation"
        records = list(sh.rows(folder / "prompts.jsonl"))
        assert len(records) == 2 and all(r["inference_seed"] == 42 for r in records)
        manifest = json.loads((folder / "bundle_manifest.json").read_text())
        assert manifest["preparation_only"] and not manifest["inference_ready"]
        assert manifest["count"] == 2 and manifest["missing_target_policy"] == sh.MISSING_POLICY
        assert manifest["stop_rule_graph_missing_over_5pct"]
        for name, checksum in manifest["artifact_sha256"].items():
            assert sh.sha256(folder / name) == checksum
        with zipfile.ZipFile(next(folder.glob("*.zip"))) as z:
            assert z.read("prompts.jsonl") == (folder / "prompts.jsonl").read_bytes()
    with pytest.raises(FileExistsError):
        sh.prepare(b1, b2, frozen, out, TinyTokenizer(), runs=[("devign", "validation")])


def test_reference_tamper_stops_export(sources, tmp_path):
    b1, b2, frozen = sources
    path = b1 / "devign/validation/prompts.jsonl"
    path.write_text(path.read_text() + "\n")
    with pytest.raises(ValueError, match="B1 prompts SHA256"):
        sh.prepare(b1, b2, frozen, tmp_path / "out", TinyTokenizer(), runs=[("devign", "validation")])


def test_notebook_is_unexecuted_and_code_compiles():
    notebook = json.loads((Path(__file__).parent / "notebooks/01_prepare_b1_shuf_prompts.ipynb").read_text(encoding="utf-8"))
    for cell in notebook["cells"]:
        if cell["cell_type"] == "code":
            assert cell["execution_count"] is None and cell["outputs"] == []
            compile("".join(cell["source"]), "notebook-cell", "exec")
