"""Audit actual harvested records, bundles, checkpoints and runtime evidence.

No model inference, threshold refit on test, source-data edits or remote writes.
"""
import ast
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import sys
from zipfile import ZipFile

import numpy as np
from sklearn.metrics import balanced_accuracy_score, f1_score, matthews_corrcoef, roc_auc_score
from transformers import AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "Runs-management/acceptance_6arms_20261108"
HARVEST = ROOT / "Runs-management/kernel_outputs_harvest"
MODEL = "f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335"
TOK = ROOT / "11_Arm_B1H2_Evidence/tokenizer_cache_v6/models--Qwen--Qwen3-Coder-30B-A3B-Instruct/snapshots/b2cff646eb4bb1d68355c01b18ae02e7cf42d120"
ARMS = {
    "B2-labelonly": ("tomandjerry223_grace-b2-labelonly-test", "b2_labelonly_test", "b2_labelonly_test_bundles", "12_Arm_B2_LabelOnly"),
    "B2-nolabel": ("tomandjerry223_grace-b2-nolabel-test", "b2_nolabel_test", "b2_nolabel_test_bundles", "10_Arm_B2_NoLabel"),
    "B2-rep": ("huuhieu3333_grace-b2-rep-test", "b2_rep_test", "b2_rep_test_bundles", "05_Arm_B2_Rep"),
    "B1-full": ("huuhieu3333_grace-b1-full-test", "b1_full_test", "b1_full_test_bundles", "09_Arm_B1_Full"),
    "B3": ("lznt123_grace-b3-validation", "b3_validation/B3", "b3_bundles", None),
    "B1-shuf": ("lznt123_grace-b1-shuf-test", "b1_shuf_test_runtime_locked", "b1_shuf_test_bundles", "08_Arm_B1_Shuf"),
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read_rows(raw):
    return [json.loads(line) for line in raw.splitlines() if line.strip()]


def signed(lock):
    body = {k: v for k, v in lock.items() if k != "locked_sha256"}
    hashes = [sha(json.dumps(body, sort_keys=True, ensure_ascii=False, indent=2).encode()),
              sha(json.dumps(body, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode())]
    return lock.get("locked_sha256") in hashes


def session_text(directory):
    p = next(directory.glob("*.log"))
    text = p.read_text(encoding="utf-8", errors="replace")
    try:
        data = json.loads(text)
        text = "".join(str(r.get("data", "")) for r in data)
    except (ValueError, AttributeError):
        pass
    return text, p


def record_payload(r):
    return {k: r.get(k) for k in ["id", "arm", "dataset", "split", "seed", "label", "s", "valid", "prompt_sha256", "logprob_0", "logprob_1", "timestamp"]}


def main():
    BASE.mkdir(exist_ok=True, parents=True)
    tokenizer = AutoTokenizer.from_pretrained(str(TOK), local_files_only=True)
    labels = {}
    for ds in ["devign", "reveal"]:
        for split in ["test", "validation"]:
            p = ROOT / f"01_Author_Baseline_Unified/output/research_freeze_20261101/{ds}/{split}_manifest.jsonl"
            labels[ds, split] = {str(r["id"]): int(r["label"]) for r in read_rows(p.read_bytes())}
    lock = json.loads((ROOT / "configs/inference_runtime_lock.json").read_text(encoding="utf-8"))
    results = []
    token_results = []
    all_records = {}
    all_prompts = {}
    target_cache = {}

    for arm, (slug, folder, bundles_dir, config_folder) in ARMS.items():
        directory = HARVEST / slug
        thresholds = {}
        if config_folder:
            threshold_lock = json.loads((ROOT / config_folder / "config/threshold.json").read_text(encoding="utf-8"))
            assert signed(threshold_lock)
            thresholds = {(e["dataset"], e.get("seed", 42)): e["tau_star"] for e in threshold_lock["entries"].values()}
        text, log_path = session_text(directory)
        packages = {}
        for package, version in lock["packages"].items():
            spellings = [package, package.replace("-", "_")]
            installation = any(re.search(re.escape(name) + r"-" + re.escape(version) + r"(?:\s|$)", line)
                               for line in text.splitlines() if "Successfully installed" in line for name in spellings)
            already = any(re.search(r"Requirement already satisfied: " + re.escape(name) + r"==" + re.escape(version) + r"\b.*\(" + re.escape(version) + r"\)", text)
                          for name in spellings)
            packages[package] = {"expected": version, "installation_log_match": bool(installation or already)}
        native_files = list((directory / folder).rglob("model_load_offload.log"))
        native_text = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in native_files)
        # Also inspect true inference logs of this exact session, never borrow prior runs.
        inference_logs = [p for p in (directory / "grace_diagnostics").glob("*.log") if p.name.startswith(("test_", "validation_"))]
        infer_text = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in inference_logs)
        offload = bool(re.search(r"offloaded\s+49/49\s+layers to GPU", native_text + "\n" + infer_text + "\n" + text))
        runtime = {"packages": packages, "native_offload_49_49": offload,
                   "detected_two_t4": "Detected GPUs: ['Tesla T4', 'Tesla T4']" in text or len(set(re.findall(r"using device CUDA(\d+) \([^\n)]*T4", native_text + infer_text))) == 2,
                   "model_sha_guard_success": "Model SHA-256 verified successfully!" in text,
                   "log_path": str(log_path.relative_to(ROOT)), "log_sha256": sha(log_path.read_bytes()),
                   "runtime_provenance_files": [str(p.relative_to(ROOT)) for p in (directory / folder).rglob("runtime_provenance.json")]}
        arm_result = {"arm": arm, "source": str(directory.relative_to(ROOT)), "runtime": runtime, "datasets": [], "checkpoints": []}

        for bundle_path in sorted((directory / bundles_dir).glob("*.zip")):
            with ZipFile(bundle_path) as z:
                manifest = json.loads(z.read("bundle_manifest.json"))
                raw_prompts = z.read("prompts.jsonl")
            bundle_arm, ds, split, seed = manifest["arm"], manifest["dataset"], manifest["split"], manifest["seed"]
            prompts = read_rows(raw_prompts)
            expected_labels = labels[ds, split]
            prompt_map = {str(p["id"]): p for p in prompts}
            bundle_issues = []
            if sha(raw_prompts) != manifest["prompts_sha256"]:
                bundle_issues.append("prompt_file_hash")
            if len(prompts) != len(prompt_map) or set(prompt_map) != set(expected_labels):
                bundle_issues.append("prompt_census_ids")
            for p in prompts:
                if sha(p["prompt"].encode("utf-8")) != p["prompt_sha256"]:
                    bundle_issues.append("individual_prompt_hash")
                if expected_labels.get(str(p["id"])) != p["label"]:
                    bundle_issues.append("prompt_label")
            all_prompts[bundle_arm, ds, split, seed] = prompt_map
            counts = []
            violations = []
            for start in range(0, len(prompts), 32):
                batch = prompts[start:start + 32]
                chats = [tokenizer.apply_chat_template([{"role": "user", "content": p["prompt"]}], tokenize=False, add_generation_prompt=True) for p in batch]
                encodings = tokenizer.backend_tokenizer.encode_batch(chats, add_special_tokens=False)
                for p, encoding in zip(batch, encodings):
                    n = len(encoding.ids)
                    target = p["prompt"].split("\n\nIn the above code snippet,", 1)[0].split("\n\n", 1)[-1]
                    target_hash = sha(target.encode())
                    if target_hash not in target_cache:
                        target_cache[target_hash] = len(tokenizer.encode(target, add_special_tokens=False))
                    code_tokens = target_cache[target_hash]
                    counts.append(n)
                    if n > 8192 or n > 8128 or code_tokens > 3000:
                        violations.append({"id": p["id"], "chat_tokens": n, "target_tokens": code_tokens,
                                           "over_context": n > 8192, "over_with_reserve": n > 8128,
                                           "target_over_3000": code_tokens > 3000})
            tokens = {"arm": bundle_arm, "dataset": ds, "split": split, "seed": seed,
                      "bundle": str(bundle_path.relative_to(ROOT)), "bundle_sha256": sha(bundle_path.read_bytes()),
                      "n": len(prompts), "max_chat_tokens": max(counts),
                      "over_8192": sum(v["over_context"] for v in violations), "over_8128": sum(v["over_with_reserve"] for v in violations),
                      "target_over_3000": sum(v["target_over_3000"] for v in violations), "violations": violations,
                      "bundle_identity_issues": sorted(set(bundle_issues))}
            token_results.append(tokens)
            if bundle_arm != arm:
                continue
            record_path = directory / folder / (f"seed_{seed}/{ds}/{split}/records.jsonl")
            rows = read_rows(record_path.read_bytes()) if record_path.exists() else []
            by_id = {str(r["id"]): r for r in rows}
            all_records[arm, ds, split, seed] = by_id
            problems = Counter()
            if len(rows) != len(by_id):
                problems["duplicate_id"] += len(rows) - len(by_id)
            max_score_error = 0.0
            for r in rows:
                uid = str(r["id"])
                p = prompt_map.get(uid)
                if not p:
                    problems["extra_id"] += 1
                    continue
                if (r.get("arm"), r.get("dataset"), r.get("split"), r.get("seed")) != (arm, ds, split, seed):
                    problems["record_identity"] += 1
                if r.get("label") != expected_labels.get(uid):
                    problems["label"] += 1
                if r.get("prompt_sha256") != p["prompt_sha256"]:
                    problems["prompt_hash"] += 1
                if r.get("model_sha256") != MODEL:
                    problems["model_hash"] += 1
                if not r.get("valid") or not isinstance(r.get("s"), (int, float)) or not math.isfinite(r["s"]) or not 0 <= r["s"] <= 1:
                    problems["numeric_score"] += 1
                else:
                    difference = r["logprob_1"] - r["logprob_0"]
                    expected_score = 1 / (1 + math.exp(-difference)) if difference >= 0 else math.exp(difference) / (1 + math.exp(difference))
                    max_score_error = max(max_score_error, abs(r["s"] - expected_score))
                if arm == "B2-rep" and (r.get("repeat") is not True or r.get("tag") != "repeat"):
                    problems["repeat_tag"] += 1
                if (ds, seed) in thresholds:
                    tau = thresholds[ds, seed]
                    if r.get("tau") != tau or r.get("pred_tau") != int(r["s"] >= tau):
                        problems["threshold_prediction"] += 1
            if max_score_error > 1e-10:
                problems["score_logprob_consistency"] += 1
            partial = {"dataset": ds, "split": split, "seed": seed, "n": len(rows), "expected": len(prompts),
                       "missing": len(set(prompt_map) - set(by_id)), "problems": dict(problems),
                       "score_logprob_max_error": max_score_error, "raw_invalid": sum(not r.get("response_valid", True) for r in rows),
                       "records_path": str(record_path.relative_to(ROOT)), "records_sha256": sha(record_path.read_bytes()) if rows else None,
                       "total_elapsed_s": sum(r.get("elapsed_s", 0) for r in rows),
                       "start_utc": min((r.get("timestamp", "") for r in rows), default=None),
                       "end_utc": max((r.get("timestamp", "") for r in rows), default=None)}
            if rows and not problems:
                y = [r["label"] for r in rows]
                scores = [r["s"] for r in rows]
                tau = thresholds.get((ds, seed))
                if tau is not None:
                    preds = [int(s >= tau) for s in scores]
                    metric = {"tau": tau, "n": len(rows), "auroc": float(roc_auc_score(y, scores)), "mcc_at_tau": float(matthews_corrcoef(y, preds)),
                              "ba_at_tau": float(balanced_accuracy_score(y, preds)), "f1_at_tau": float(f1_score(y, preds))}
                    partial["computed_metrics"] = metric
                    evaluation = record_path.with_name("evaluation.json")
                    if evaluation.exists():
                        stored = json.loads(evaluation.read_text(encoding="utf-8"))
                        partial["evaluation_matches"] = all(abs(stored[k] - metric[k]) < 1e-9 for k in ["auroc", "mcc_at_tau", "ba_at_tau", "f1_at_tau"])
            partial["completed_records_over_8192"] = sum(v["id"] in by_id and v["over_context"] for v in violations)
            partial["completed_records_target_over_3000"] = sum(v["id"] in by_id and v["target_over_3000"] for v in violations)
            partial["complete_record_integrity"] = len(rows) == len(prompts) and not problems
            manifest_path = record_path.with_name("run_manifest.json")
            if manifest_path.exists():
                stored_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                partial["manifest_record_hash_matches"] = stored_manifest.get("records_sha256") in [None, partial["records_sha256"]]
                partial["manifest_has_runtime_contract"] = "runtime_contract_sha256" in stored_manifest
            arm_result["datasets"].append(partial)
            print(arm, ds, seed, len(rows), "/", len(prompts), "problems", dict(problems), "over_context", tokens["over_8192"], "target_over", tokens["target_over_3000"], flush=True)

        for archive in directory.glob("*.zip"):
            if "checkpoint" not in archive.name and "final_output" not in archive.name:
                continue
            with ZipFile(archive) as z:
                summary = {"path": str(archive.relative_to(ROOT)), "sha256": sha(archive.read_bytes()), "crc_ok": z.testzip() is None, "members": []}
                for name in z.namelist():
                    if not name.endswith("records.jsonl"):
                        continue
                    archived_rows = read_rows(z.read(name))
                    if not archived_rows:
                        continue
                    r = archived_rows[0]
                    fresh = all_records.get((r["arm"], r["dataset"], r["split"], r["seed"]), {})
                    equal = all(str(x["id"]) in fresh and record_payload(x) == record_payload(fresh[str(x["id"])]) for x in archived_rows)
                    summary["members"].append({"name": name, "n": len(archived_rows), "matches_loose_records": equal,
                                               "loose_rows_not_in_archive": len(fresh) - len(archived_rows)})
            arm_result["checkpoints"].append(summary)
        results.append(arm_result)

    report = {"checked_at_utc": datetime.now(timezone.utc).isoformat(), "results": results, "token_preflight": token_results,
              "tokenizer_path": str(TOK.relative_to(ROOT)), "tokenizer_json_sha256": sha((TOK / "tokenizer.json").read_bytes()),
              "scope": "Record-level and operational acceptance only; no new inference or test threshold fitting, no source data or remote state changes."}
    (BASE / "acceptance.json").write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print("Saved", BASE / "acceptance.json", flush=True)


if __name__ == "__main__":
    main()
