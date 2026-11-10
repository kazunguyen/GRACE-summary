"""Build B3-new test prompts from the frozen specs, with no target labels in the runner bundle."""
import hashlib
import json
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "01_Author_Baseline_Unified/diagnostic_kit/src"))
sys.path.insert(0, str(ROOT / "scripts"))
from grace_diag.amended_b3 import VerifiedPairSelector, digest, validate_pair
from grace_diag.probes import ANSWER, QUESTION, ROLE, split_blocks
from grace_diag.token_budget import TokenCounter

OUT = ROOT / "Runs-management/b3_verified_patch_v1/test_release_20261109_v1"
ARCHIVE = ROOT / "Runs-management/grace_15arms_prompts_and_clean_specs.zip"
FREEZE = ROOT / "01_Author_Baseline_Unified/output/research_freeze_20261101"
TOKENIZER = ROOT / "11_Arm_B1H2_Evidence/tokenizer_cache_v6/models--Qwen--Qwen3-Coder-30B-A3B-Instruct/snapshots/b2cff646eb4bb1d68355c01b18ae02e7cf42d120"
POOLS = {"devign": ROOT / "Runs-management/b3_verified_patch_v1/release_20261108_v5/pools/eligible_pairs.devign.jsonl",
         "reveal": ROOT / "Runs-management/b3_verified_patch_v1/reveal_reviewed_pool_20261108/eligible_pairs.reveal.jsonl"}
EXPECTED = {"devign": 2732, "reveal": 2274}


def sha(raw): return hashlib.sha256(raw).hexdigest()


def read_jsonl(raw): return [json.loads(x) for x in raw.decode("utf-8").splitlines() if x.strip()]


def get_member(z, filename):
    matches = [n for n in z.namelist() if n == filename or n.endswith("/" + filename)]
    if len(matches) != 1: raise ValueError(f"Expected one {filename} in frozen specs ZIP; found {len(matches)}")
    return matches[0], z.read(matches[0])


def ordered(prompt, evidence):
    blocks = split_blocks(prompt)
    positions = [prompt.find(ROLE), prompt.find(blocks["code"]), prompt.find(QUESTION)]
    if blocks["graph"]: positions.append(prompt.find(blocks["graph"]))
    if blocks["demo"]: positions.append(prompt.find(blocks["demo"]))
    positions.append(prompt.rfind(ANSWER))
    return evidence.get("order") == ["role", "code", "question", "graph", "demonstration", "answer"] and all(p >= 0 for p in positions) and positions == sorted(positions)


def main():
    if OUT.exists():
        files = [p for p in OUT.rglob("*") if p.is_file()]
        expected_dirs = {OUT / "kaggle_input/prompts", OUT / "kaggle_input/pools", OUT / "private_evaluation_only"}
        if files or not expected_dirs.issubset({p for p in OUT.rglob("*") if p.is_dir()}):
            raise FileExistsError(f"Preserve non-empty/incomplete existing test release: {OUT}")
    if not ARCHIVE.is_file() or not TOKENIZER.is_dir(): raise FileNotFoundError("Frozen test specs or exact tokenizer snapshot missing")
    counter = TokenCounter(str(TOKENIZER))
    if counter.approx: raise ValueError("Exact tokenizer is mandatory")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "kaggle_input/prompts").mkdir(parents=True, exist_ok=True)
    (OUT / "kaggle_input/pools").mkdir(parents=True, exist_ok=True)
    (OUT / "private_evaluation_only").mkdir(exist_ok=True)
    with zipfile.ZipFile(ARCHIVE) as z:
        if z.testzip() is not None: raise ValueError("Frozen spec ZIP CRC failure")
        zip_hash = sha(ARCHIVE.read_bytes())
        dataset_reports = {}
        private_labels = {}
        input_manifest = {"schema": "grace_b3_test_prompts_v1", "method_id": "b3-verified-patch-v1",
                          "arm": "B3", "seed": 42, "fit_split": "validation", "inference_split": "test",
                          "model_sha256": "f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335",
                          "tokenizer_revision": "b2cff646eb4bb1d68355c01b18ae02e7cf42d120",
                          "runtime_contract_sha256": "4c9c3bcff5e9fd32532d7edf85df7a961e45ec9c64bee3df8833d986a2eb276e",
                          "threshold_release_id": "threshold_release_20261109_v1", "datasets": {}}
        for ds, n_expected in EXPECTED.items():
            spec_name, spec_raw = get_member(z, f"{ds}_test_15arms.jsonl")
            specs = read_jsonl(spec_raw)
            raw_path = FREEZE / ds / "test_raw.jsonl"
            raw_lookup = {}
            for line in raw_path.read_text(encoding="utf-8").splitlines():
                source = json.loads(line)
                item = {"id": source["id"], "func": source["func"]}
                if item["id"] in raw_lookup: raise ValueError(f"Duplicate raw test ID: {ds}/{item['id']}")
                raw_lookup[item["id"]] = item
                private_labels[item["id"]] = source["target"]
            if len(specs) != n_expected or len({x["id"] for x in specs}) != n_expected or set(raw_lookup) != {x["id"] for x in specs}:
                raise ValueError(f"Frozen spec/raw test census mismatch: {ds}")
            if any(type(v) is not int or v not in (0, 1) for v in private_labels.values()):
                raise ValueError("Invalid raw evaluation label")
            pool_path = POOLS[ds]
            pairs = read_jsonl(pool_path.read_bytes())
            train = FREEZE / ds
            kept = {x["id"] for line in (train / "train_manifest.jsonl").read_text(encoding="utf-8").splitlines()
                    if (x := json.loads(line))["keep_in_bank"]}
            bank = {}
            for line in (train / "train_raw.jsonl").read_text(encoding="utf-8").splitlines():
                x = json.loads(line)
                if x["id"] in kept:
                    x["function_uid"] = x["id"]
                    bank[x["id"]] = x
            for pair in pairs: validate_pair(pair, bank, ds)
            selector = VerifiedPairSelector(pairs, bank, ds)
            out_rows, census = [], []
            counts = Counter()
            max_chat = 0
            for i, spec in enumerate(specs):
                source = raw_lookup[spec["id"]]
                if digest(spec["query_code"].strip()) != digest(source["func"].strip()):
                    raise ValueError(f"Frozen spec code mismatch: {ds}/{spec['id']}")
                # Do not pass the spec or its label to selector/renderer.
                target = {k: spec.get(k, "") for k in ("id", "query_code", "nodes", "edges")}
                rendered = selector.render_family(target, counter)["B3"]
                prompt, ev = rendered["prompt"], rendered["evidence"]
                blocks, tokens = split_blocks(prompt), ev["tokens"]
                chat = counter.count_chat(prompt)
                max_chat = max(max_chat, chat)
                leak = bool(re.search(r"The following (?:example|code|target) is (?:Vulnerable|Non-vulnerable)",
                                      prompt[:prompt.find(QUESTION)], re.I))
                if not ordered(prompt, ev) or leak or chat + 64 > 8192 or tokens["code"] > 3000 or tokens["graph"] > 1500 or tokens["demo"] > 1500:
                    raise ValueError(f"Prompt audit failed: {ds}/{spec['id']}")
                if "label" in rendered or "label" in rendered.get("selection", {}):
                    raise ValueError("Renderer attempted to expose target label")
                row = {"id": spec["id"], "dataset": ds, "split": "test", "prompt": prompt,
                       "prompt_sha256": digest(prompt), "method_id": "b3-verified-patch-v1",
                       "pool_sha256": sha(pool_path.read_bytes()), "selection": rendered["selection"],
                       "token_audit": tokens, "chat_tokens": chat}
                if "label" in row or "target" in row: raise AssertionError("Label field in inference row")
                out_rows.append(row)
                census.append({"id": spec["id"], "query_code_sha256": digest(spec["query_code"].strip()),
                               "prompt_sha256": row["prompt_sha256"], "selection": row["selection"],
                               "token_audit": tokens, "chat_tokens": chat, "figure6_order_compliant": True,
                               "target_label_in_prompt": False})
                counts[str(row["selection"]["pair_id"])] += 1
                if (i + 1) % 250 == 0: print(f"{ds}: audited {i+1}/{n_expected}", flush=True)
            prompts_raw = b"".join((json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n").encode() for row in out_rows)
            census_raw = b"".join((json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n").encode() for row in census)
            prompt_path = OUT / "kaggle_input/prompts" / f"{ds}.jsonl"
            census_path = OUT / "audit" / f"{ds}_prompt_census.jsonl"
            census_path.parent.mkdir(exist_ok=True)
            prompt_path.write_bytes(prompts_raw); census_path.write_bytes(census_raw)
            pool_copy = OUT / "kaggle_input/pools" / f"{ds}_eligible_pairs.jsonl"
            pool_copy.write_bytes(pool_path.read_bytes())
            dataset_reports[ds] = {"expected": n_expected, "rows": len(out_rows), "ids_unique": True,
                "spec_archive_member": spec_name, "spec_sha256": sha(spec_raw), "pool_sha256": sha(pool_path.read_bytes()),
                "prompt_sha256": sha(prompts_raw), "census_sha256": sha(census_raw), "max_chat_tokens": max_chat,
                "selected_pair_counts": dict(counts), "exact_tokenizer": True,
                "all_labels_absent_from_prompt_rows": all("label" not in r and "target" not in r for r in out_rows),
                "all_prompts_figure6_and_budget_pass": True}
            input_manifest["datasets"][ds] = {k: dataset_reports[ds][k] for k in
                ("expected", "prompt_sha256", "census_sha256", "pool_sha256")}
            # Private labels are written outside kaggle_input and after prompt rendering only.
        labels_raw = (json.dumps(private_labels, sort_keys=True, separators=(",", ":")) + "\n").encode()
        label_path = OUT / "private_evaluation_only/test_labels.json"
        label_path.write_bytes(labels_raw)
        input_manifest["labels_evaluation_only_sha256"] = sha(labels_raw)
        input_manifest["runtime_contract_sha256"] = "4c9c3bcff5e9fd32532d7edf85df7a961e45ec9c64bee3df8833d986a2eb276e"
        input_manifest["threshold_lock_sha256"] = {ds: sha(ROOT / "Runs-management/b3_verified_patch_v1/threshold_release_20261109_v1" / f"{ds}_threshold_lock.json") for ds in EXPECTED}
        input_manifest["frozen_specs_zip_sha256"] = zip_hash
        input_manifest["status"] = "TEST_PROMPTS_RENDERED_LABELS_SEPARATED_NOT_YET_SEALED"
        (OUT / "kaggle_input/test_prompt_manifest.json").write_text(json.dumps(input_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (OUT / "audit/prompt_audit_report.json").write_text(json.dumps({"status": "PASS", "datasets": dataset_reports,
            "total": sum(EXPECTED.values()), "labels_in_kaggle_input": False, "labels_in_inference_rows": False,
            "native_runtime": "NOT_EVALUATED"}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "total": sum(EXPECTED.values()), "labels_separated": True,
                      "datasets": dataset_reports}, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__": main()
