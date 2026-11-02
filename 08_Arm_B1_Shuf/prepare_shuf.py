"""Prepare B1-shuf prompts only. Never load an LLM or run inference.

Use the existing B1 scaffold and frozen train CPGs; see README.md for scope.
"""
from __future__ import annotations

import argparse
from collections import Counter, OrderedDict
from contextlib import ExitStack
import hashlib
import json
import os
from pathlib import Path
import sys
import zipfile

import numpy as np

HERE = Path(__file__).resolve().parent
SEEDS = (42, 43, 44)
RUNS = (("devign", "validation"), ("reveal", "validation"),
        ("devign", "test"), ("reveal", "test"))
REVISION = "b2cff646eb4bb1d68355c01b18ae02e7cf42d120"
VARIANT = "b1_shuf_paired_40_80_v1"
WIDTHS = (0.1, 0.2, 0.4, 0.8, 1.6, 3.2)
MISSING_POLICY = "retain_B1_unchanged_no_donor_flag_target_graph_missing"


def project_root():
    candidates = ([Path(os.environ["GRACE_SUMMARY_ROOT"])] if os.environ.get("GRACE_SUMMARY_ROOT")
                  else [HERE.parent, *HERE.parents, Path("D:/JUNIOR/LabThayTho/GRACE-summary"),
                        Path("/mnt/d/JUNIOR/LabThayTho/GRACE-summary")])
    for root in candidates:
        if (root / "tier1_prompt_tools/prepare_cached.py").is_file():
            return root.resolve()
    raise FileNotFoundError("Set GRACE_SUMMARY_ROOT to the GRACE-summary folder")


ROOT = project_root()
sys.path.insert(0, str(ROOT / "tier1_prompt_tools"))
from prepare_cached import (BUDGET, PREFIX, DEMO_EMPTY, cache_paths, convert_graph,
                            render_paired, rows, sha256)
from grace_diag.probes import (ANSWER, EDGE_HEAD, NODE_HEAD, QUESTION, ROLE,
                               closed_prefix, render_graph, stable_seed)
from grace_diag.token_budget import TokenCounter


def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def indexed_rows(path):
    result = {}
    for row in rows(path):
        uid = str(row["id"])
        if uid in result:
            raise ValueError(f"Duplicate ID in {path}: {uid}")
        result[uid] = row
    return result


class FrozenDonors:
    """Byte-offset index: scan/hash once; keep large CPGs on disk, not all in RAM."""

    def __init__(self, dataset, frozen_root, freeze):
        self.path = Path(frozen_root) / dataset / "donors.jsonl"
        self.entry = freeze["datasets"][dataset]
        self.uids, self.offsets, counts = [], [], []
        h = hashlib.sha256()
        with self.path.open("rb") as stream:
            while True:
                offset = stream.tell()
                line = stream.readline()
                if not line:
                    break
                h.update(line)
                if not line.strip():
                    continue
                row = json.loads(line)
                uid = row["function_uid"]
                if not uid.startswith(dataset + ":train:") or row.get("target") not in (0, 1):
                    raise ValueError("Invalid frozen donor identity/label")
                nodes = row.get("nodes") or []
                if row.get("n_nodes", len(nodes)) != len(nodes):
                    raise ValueError("Donor n_nodes disagrees with full CPG")
                self.uids.append(uid)
                self.offsets.append(offset)
                counts.append(len(nodes))
                if len(counts) % 2000 == 0:
                    print(f"[donor index {dataset}] {len(counts)} rows", flush=True)
        self.file_sha256 = h.hexdigest()
        if self.file_sha256 != self.entry["files_sha256"]["donors.jsonl"]:
            raise ValueError("Frozen donor SHA256 mismatch")
        if len(counts) != self.entry["donor_count"] or len(set(self.uids)) != len(counts):
            raise ValueError("Frozen donor count/uniqueness mismatch")
        self.counts = np.asarray(counts, dtype=np.int64)
        self.stamp = self._stamp()
        self.cache = OrderedDict()
        print(f"[donor index {dataset}] verified {len(counts)} donors", flush=True)

    def _stamp(self):
        s = self.path.stat()
        return s.st_size, s.st_mtime_ns, s.st_ctime_ns

    def check_unchanged(self):
        if self.stamp != self._stamp():
            raise ValueError("Donor file changed after verification")

    def select(self, target_id, seed, n_target):
        if n_target <= 0:
            raise ValueError("Missing target CPG must use the explicit missing policy")
        rng = np.random.default_rng(stable_seed(target_id, seed) ^ 0x5F3759DF)
        for width in WIDTHS:
            # Match DonorPool.shuffle_graph: outward-rounded integer bounds.
            lo = max(1, int(np.floor(n_target * (1 - width))))
            hi = max(1, int(np.ceil(n_target * (1 + width))))
            candidates = np.flatnonzero((self.counts >= lo) & (self.counts <= hi))
            candidates = [int(i) for i in candidates if self.uids[i] != target_id]
            if candidates:
                index = int(rng.choice(candidates))
                return index, {"donor_uid": self.uids[index], "donor_cpg_nodes": int(self.counts[index]),
                               "tolerance_used": width, "candidate_count": len(candidates),
                               "match_low": lo, "match_high": hi,
                               "matching_status": "matched_10pct" if width == 0.1 else "relaxed"}
        raise ValueError(f"No donor with nonempty CPG for {target_id}; refusing arbitrary fallback")

    def graph(self, index, counter):
        self.check_unchanged()
        if index not in self.cache:
            with self.path.open("rb") as stream:
                stream.seek(self.offsets[index])
                donor = json.loads(stream.readline())
            if donor["function_uid"] != self.uids[index] or len(donor.get("nodes") or []) != self.counts[index]:
                raise ValueError("Indexed donor no longer matches")
            # No code/label from the donor enters the renderer. Normalize endpoints,
            # then keep only the source ceiling; fitting is the exact B1 policy.
            clean = convert_graph({"nodes": donor["nodes"], "edges": donor.get("edges") or []})
            ns, es = closed_prefix(clean["nodes"], clean["edges"], PREFIX["nodes"], PREFIX["edges"])
            text, info = render_graph("prefix", {"nodes": ns, "edges": es}, counter,
                                      BUDGET["graph"], PREFIX, 42, None)
            if not info["rendered_nodes"]:
                raise ValueError("Selected donor CPG rendered no nodes")
            info.update(available_nodes=len(donor["nodes"]), available_edges=len(donor.get("edges") or []))
            self.cache[index] = text, info
            if len(self.cache) > 2048:
                self.cache.popitem(last=False)
        self.cache.move_to_end(index)
        text, info = self.cache[index]
        return text, dict(info)


def b1_scaffold(prompt, spec, counter):
    """Locate only the graph block using the known target and exact B1 suffix."""
    code = counter.fit(spec["query_code"].strip(), BUDGET["target_code"],
                       marker="\n/* [TRUNCATED TARGET] */").text
    prefix = "\n\n".join([ROLE, code, QUESTION]) + "\n\n"
    suffix = "\n\n" + DEMO_EMPTY + "\n\n" + ANSWER
    if not prompt.startswith(prefix) or not prompt.endswith(suffix):
        raise ValueError("B1 scaffold/code differs from the locked reference")
    graph = prompt[len(prefix):-len(suffix)]
    if not graph.startswith(NODE_HEAD + "\n") or EDGE_HEAD not in graph:
        raise ValueError("B1 graph headers missing")
    return prefix, graph, suffix


def shuffle_one(spec, b1, pool, counter, seed):
    # Labels stay outside this function's renderer inputs.
    if any(k in spec for k in ("label", "target", "target_label", "ground_truth")):
        raise ValueError("Remove target labels before rendering")
    uid = str(spec["id"])
    prefix, original_graph, suffix = b1_scaffold(b1["prompt"], spec, counter)
    n_target = len(spec.get("nodes") or [])
    if n_target == 0:
        prompt = b1["prompt"]
        graph_tokens = counter.count(original_graph)
        graph_info = {"rendered_nodes": 0, "rendered_edges": 0, "tokens": graph_tokens, "truncated": False}
        match = {"donor_uid": None, "donor_cpg_nodes": None, "tolerance_used": None,
                 "candidate_count": 0, "matching_status": "target_graph_missing"}
    else:
        index, match = pool.select(uid, seed, n_target)
        graph, graph_info = pool.graph(index, counter)
        prompt = prefix + graph + suffix
    code_fit = counter.fit(spec["query_code"].strip(), BUDGET["target_code"], marker="\n/* [TRUNCATED TARGET] */")
    tokens = {"code": code_fit.tokens,
              "graph": graph_info["tokens"], "demo": 0, "total": counter.count_chat(prompt)}
    if counter.approx or tokens["total"] + BUDGET["reserve"] > BUDGET["total"]:
        raise ValueError("Approximate tokenizer or context overflow")
    if tokens["code"] > BUDGET["target_code"] or tokens["graph"] > BUDGET["graph"]:
        raise ValueError("Component budget overflow")
    # Check the complete non-graph portions after replacement, including scaffold.
    p2, _, s2 = b1_scaffold(prompt, spec, counter)
    if (prefix, suffix) != (p2, s2):
        raise ValueError("A non-graph block changed")
    audit = {"id": uid, "seed": seed, "reference_b1_prompt_sha256": b1["prompt_sha256"],
             "prompt_sha256": digest(prompt), "target_cpg_nodes": n_target, **match,
             "rendered_nodes": graph_info["rendered_nodes"], "rendered_edges": graph_info["rendered_edges"],
             "tokens": tokens, "code_unchanged": True, "non_graph_blocks_unchanged": True,
             "target_graph_missing": n_target == 0, "graph_truncated": graph_info.get("truncated", False),
             "same_prompt_as_b1": prompt == b1["prompt"]}
    truncated = dict(b1["truncated"], graph=audit["graph_truncated"], demo=False)
    return prompt, audit, truncated


def manual_sample(items, n=30):
    """Exact min(n,N), stratified by seed, length tertile, truncation; no repeats."""
    if not items:
        return []
    q1, q2 = np.percentile([r["tokens"]["total"] for r in items], [33.3, 66.7])
    cells = {}
    for row in items:
        total = row["tokens"]["total"]
        key = (row["seed"], int(total > q1) + int(total > q2), bool(row["graph_truncated"]))
        cells.setdefault(key, []).append(row)
    rng = np.random.default_rng(42)
    for cell in cells.values():
        rng.shuffle(cell)
    selected = []
    while len(selected) < min(n, len(items)):
        for key in sorted(cells):
            if cells[key] and len(selected) < min(n, len(items)):
                selected.append({**cells[key].pop(), "stratum": list(key)})
    return selected


def summary(items):
    result = {}
    duplicates = Counter((r["id"], r["prompt_sha256"]) for r in items)
    for seed in sorted({r["seed"] for r in items}):
        part = [r for r in items if r["seed"] == seed]
        result[str(seed)] = {"n": len(part), "tokens_p50": float(np.percentile([r["tokens"]["total"] for r in part], 50)),
                             "tokens_p95": float(np.percentile([r["tokens"]["total"] for r in part], 95)),
                             "matching_status": dict(Counter(r["matching_status"] for r in part)),
                             "n_same_prompt_as_b1": sum(r["same_prompt_as_b1"] for r in part),
                             "n_same_prompt_as_another_seed": sum(duplicates[(r["id"], r["prompt_sha256"])] > 1 for r in part),
                             "n_graph_truncated": sum(r["graph_truncated"] for r in part),
                             "rate_graph_truncated": sum(r["graph_truncated"] for r in part) / len(part),
                             "rate_target_graph_missing": sum(r["target_graph_missing"] for r in part) / len(part),
                             "non_graph_blocks_unchanged": all(r["non_graph_blocks_unchanged"] for r in part),
                             "demo_content": "not_applicable_no_demo", "target_label_passed_to_renderer": False}
        for component in ("code", "graph"):
            for percentile in (50, 95):
                result[str(seed)][f"tokens_{component}_p{percentile}"] = float(np.percentile(
                    [r["tokens"][component] for r in part], percentile))
    return result


def verify_reference(dataset, split, b1_root, b2_root, frozen_root, freeze):
    files, b2_manifest = cache_paths(dataset, split, b2_root)
    folder = Path(b1_root) / dataset / split
    b1_manifest = json.loads((folder / "bundle_manifest.json").read_text(encoding="utf-8"))
    if (b1_manifest["arm"], b1_manifest["dataset"], b1_manifest["split"],
        b1_manifest["prompt_variant"]) != ("B1", dataset, split, "b1_b2_empty_demo_v1"):
        raise ValueError("B1 reference identity/scaffold mismatch")
    if b1_manifest["graph_prefix"] != PREFIX or b1_manifest["token_budget"] != BUDGET:
        raise ValueError("B1 reference is not the locked 40/80 contract")
    if b1_manifest["tokenizer_revision"] != REVISION or b1_manifest["reference_b2_sha256"] != {k: sha256(p) for k, p in files.items()}:
        raise ValueError("B1/B2 references or tokenizer revision differ")
    if sha256(folder / "prompts.jsonl") != b1_manifest["prompts_sha256"]:
        raise ValueError("B1 prompts SHA256 mismatch")
    mp = Path(frozen_root) / dataset / f"{split}_manifest.jsonl"
    if sha256(mp) != freeze["datasets"][dataset]["files_sha256"][mp.name]:
        raise ValueError("Frozen split SHA256 mismatch")
    b1, b2, expected = indexed_rows(folder / "prompts.jsonl"), indexed_rows(files["prompts"]), indexed_rows(mp)
    if set(b1) != set(b2) or set(b1) != set(expected) or len(b1) != b1_manifest["count"] or len(b2) != b2_manifest["count"]:
        raise ValueError("B1/B2/frozen split ID sets differ")
    for uid, row in b1.items():
        if row["label"] != expected[uid]["label"] or digest(row["prompt"]) != row["prompt_sha256"]:
            raise ValueError("B1 label/prompt hash mismatch")
    provenance = {"reference_b1_sha256": {"manifest": sha256(folder / "bundle_manifest.json"),
                                          "prompts": sha256(folder / "prompts.jsonl")},
                  "reference_b2_sha256": {k: sha256(p) for k, p in files.items()},
                  "frozen_split_sha256": sha256(mp)}
    return files, b1_manifest, b1, b2, expected, provenance


def prepare(b1_root, b2_root, frozen_root, out_root, tokenizer, runs=RUNS, seeds=SEEDS):
    runs, seeds = tuple(runs), tuple(seeds)
    if not runs or len(set(runs)) != len(runs) or any(r not in RUNS for r in runs):
        raise ValueError("Invalid/duplicate runs")
    if not seeds or len(set(seeds)) != len(seeds) or any(s not in SEEDS for s in seeds):
        raise ValueError("Seeds must be a nonempty unique subset of 42,43,44")
    out_root = Path(out_root).resolve()
    for source in (b1_root, b2_root, frozen_root):
        p = Path(source).resolve()
        if out_root == p or out_root in p.parents or p in out_root.parents:
            raise ValueError("Output must not overlap any input directory")
    if out_root.exists() and any(out_root.iterdir()):
        raise FileExistsError("Output is not empty; choose a new OUT_ROOT. No existing artifacts overwritten.")
    if not getattr(tokenizer, "chat_template", None):
        raise ValueError("Pinned tokenizer must provide the model chat template")
    counter = TokenCounter(None)
    counter.tok, counter.approx = tokenizer, False
    frozen_root = Path(frozen_root)
    freeze_path = frozen_root / "freeze_manifest.json"
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    source_hashes = {"prepare_shuf.py": sha256(Path(__file__)),
                     "prepare_cached.py": sha256(ROOT / "tier1_prompt_tools/prepare_cached.py"),
                     "probes.py": sha256(ROOT / "01_Author_Baseline_Unified/diagnostic_kit/src/grace_diag/probes.py"),
                     "token_budget.py": sha256(ROOT / "01_Author_Baseline_Unified/diagnostic_kit/src/grace_diag/token_budget.py")}
    out_root.mkdir(parents=True, exist_ok=True)
    (out_root / "INCOMPLETE.txt").write_text("Preparation in progress; bundles are not complete until this marker is gone.\n", encoding="utf-8")
    bundles = []
    for dataset in dict.fromkeys(d for d, _ in runs):
        pool = FrozenDonors(dataset, frozen_root, freeze)
        for ds, split in runs:
            if ds != dataset:
                continue
            print(f"[{ds}/{split}] verifying B1/B2/specs/split hashes", flush=True)
            files, ref, b1, b2, expected, provenance = verify_reference(ds, split, b1_root, b2_root, frozen_root, freeze)
            audits, seen = [], set()
            with ExitStack() as stack:
                writers = {}
                for seed in seeds:
                    folder = out_root / f"seed_{seed}" / ds / split
                    folder.mkdir(parents=True)
                    writers[seed] = (folder, stack.enter_context((folder / "prompts.jsonl").open("w", encoding="utf-8", newline="\n")),
                                     stack.enter_context((folder / "pairing_audit.jsonl").open("w", encoding="utf-8", newline="\n")))
                for spec in rows(files["specs"]):
                    uid = str(spec["id"])
                    if uid in seen or uid not in b1:
                        raise ValueError("Duplicate/unmatched specs ID")
                    seen.add(uid)
                    if spec["label"] != expected[uid]["label"] or digest(spec["query_code"]) != expected[uid]["code_sha256"]:
                        raise ValueError("Specs code/label differ from frozen target")
                    if digest(b2[uid]["prompt"]) != b2[uid]["prompt_sha256"]:
                        raise ValueError("B2 row hash mismatch")
                    reconstructed, _ = render_paired("B1", spec, b2[uid]["prompt"], counter, reference=b2[uid])
                    if reconstructed != b1[uid]["prompt"]:
                        raise ValueError("B1 reconstruction mismatch; refusing a different formatter/scaffold")
                    clean = {k: v for k, v in spec.items() if k in ("id", "query_code", "nodes", "edges")}
                    for seed in seeds:
                        prompt, audit, truncated = shuffle_one(clean, b1[uid], pool, counter, seed)
                        audit.update(dataset=ds, split=split)
                        record = {"id": uid, "dataset": ds, "split": split, "arm": "B1-shuf", "prompt_variant": VARIANT,
                                  "seed": seed, "inference_seed": 42, "label": spec["label"], "group": spec.get("group"),
                                  "prompt": prompt, "prompt_sha256": audit["prompt_sha256"],
                                  "reference_b1_prompt_sha256": b1[uid]["prompt_sha256"], "demo_ids": [],
                                  "graph_missing": audit["target_graph_missing"], "tokens": audit["tokens"],
                                  "truncated": truncated, "graph_donor": {k: audit[k] for k in
                                      ("donor_uid", "donor_cpg_nodes", "target_cpg_nodes", "tolerance_used", "matching_status")}}
                        _, out, log = writers[seed]
                        out.write(json.dumps(record, ensure_ascii=False) + "\n")
                        log.write(json.dumps(audit, ensure_ascii=False) + "\n")
                        audits.append(audit)
                    if len(seen) % 100 == 0:
                        print(f"[{ds}/{split}] {len(seen)}/{len(b1)} targets x {len(seeds)} seeds", flush=True)
                if seen != set(b1):
                    raise ValueError("Specs missing reference IDs")
            pool.check_unchanged()
            review_dir = out_root / "audit" / ds / split
            review_dir.mkdir(parents=True)
            selected = manual_sample(audits)
            wanted = {(r["id"], r["seed"]): r for r in selected}
            manual_path = review_dir / "manual_sample.jsonl"
            with manual_path.open("w", encoding="utf-8", newline="\n") as stream:
                for seed in seeds:
                    for row in rows(writers[seed][0] / "prompts.jsonl"):
                        key = (row["id"], seed)
                        if key in wanted:
                            stream.write(json.dumps({**wanted[key], "prompt": row["prompt"],
                                                     "reviewer_1": "", "reviewer_2": "", "review_notes": ""}, ensure_ascii=False) + "\n")
            reports = summary(audits)
            write_json(review_dir / "audit_summary.json", reports)
            for seed in seeds:
                folder = writers[seed][0]
                write_json(folder / "audit_summary.json", reports[str(seed)])
                missing = reports[str(seed)]["matching_status"].get("target_graph_missing", 0)
                manifest = {"arm": "B1-shuf", "prompt_variant": VARIANT, "dataset": ds, "split": split,
                            "seed": seed, "inference_seed": 42, "count": len(seen), **provenance,
                            "freeze_manifest_sha256": sha256(freeze_path), "donor_sha256": pool.file_sha256,
                            "donor_count": len(pool.uids), "missing_target_policy": MISSING_POLICY,
                            "sampling": {"algorithm": "numpy.default_rng(stable_seed(id,seed) XOR 0x5F3759DF)",
                                         "widths": list(WIDTHS), "bounds": "floor(n*(1-width))..ceil(n*(1+width)), min 1",
                                         "pool_order": "unchanged frozen donors.jsonl order", "count_basis": "full CPG before 40/80",
                                         "repeat_donor_across_seeds": "allowed"},
                            "numpy_version": np.__version__, "graph_prefix": PREFIX, "token_budget": BUDGET,
                            "tokenizer": ref["tokenizer"], "tokenizer_revision": ref["tokenizer_revision"],
                            "model_repo": ref["model_repo"], "quantization": ref["quantization"],
                            "source_sha256": source_hashes, "preparation_only": True,
                            "manual_review_status": "pending_two_reviewers", "registration_status": "not_registered",
                            "inference_ready": False, "stop_rule_graph_missing_over_5pct": missing / len(seen) > 0.05,
                            "artifact_sha256": {name: sha256(folder / name) for name in
                                                 ("prompts.jsonl", "pairing_audit.jsonl", "audit_summary.json")}}
                # Compatibility fields match sibling arm bundle conventions.
                manifest.update(prompts_sha256=manifest["artifact_sha256"]["prompts.jsonl"],
                                pairing_audit_sha256=manifest["artifact_sha256"]["pairing_audit.jsonl"])
                write_json(folder / "bundle_manifest.json", manifest)
                bundle = folder / f"{ds}_{split}_b1_shuf_seed_{seed}_prompts.zip"
                with zipfile.ZipFile(bundle, "w", zipfile.ZIP_DEFLATED) as archive:
                    for name in ("prompts.jsonl", "pairing_audit.jsonl", "audit_summary.json", "bundle_manifest.json"):
                        archive.write(folder / name, name)
                bundles.append(bundle)
            del b1, b2, expected
        del pool
    archive_path = out_root / "grace_b1_shuf_prompts.zip"
    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_STORED) as archive:
        for path in bundles:
            archive.write(path, path.relative_to(out_root))
        for path in sorted((out_root / "audit").rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(out_root))
    (out_root / "INCOMPLETE.txt").unlink()
    print("Preparation complete; manual review and preregistration remain:", archive_path, flush=True)
    return archive_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    baseline = ROOT / "01_Author_Baseline_Unified"
    parser.add_argument("--b1-root", type=Path, default=ROOT / "03_Arm_B1_Graph_Only/output/bundles")
    parser.add_argument("--b2-root", type=Path, default=baseline / "output/local_full/bundles_recovered_joern_final_20261031")
    parser.add_argument("--frozen-root", type=Path, default=baseline / "output/research_freeze_20261101")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--split", choices=("validation", "test", "all"), default="validation")
    parser.add_argument("--local-files-only", action="store_true")
    args = parser.parse_args()
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-Coder-30B-A3B-Instruct", revision=REVISION,
                                              trust_remote_code=False, local_files_only=args.local_files_only)
    prepare(args.b1_root, args.b2_root, args.frozen_root, args.out, tokenizer,
            runs=[r for r in RUNS if args.split == "all" or r[1] == args.split])


if __name__ == "__main__":
    main()
