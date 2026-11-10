"""Kaggle worker: verified inputs, explicit legacy migration, locked new inference.

The notebook supplies the byte-verified grace_runtime_contract helper. Old rows
remain unchanged and are explicitly excluded from new-runtime certification.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import tempfile
import time
from zipfile import ZIP_DEFLATED, ZipFile

import numpy as np


def digest_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(row):
    return digest_bytes(json.dumps(row, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode())


def jsonl(raw):
    return [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]


def atomic(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(value, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(temporary, path)


def binary_scores(logits, label_ids):
    values = np.asarray(logits, dtype=np.float64).reshape(-1)
    if not np.all(np.isfinite(values)):
        raise ValueError("Non-finite logits")
    maximum = np.max(values)
    normalizer = float(maximum + np.log(np.exp(values - maximum).sum()))
    lp0 = float(values[label_ids[0]] - normalizer)
    lp1 = float(values[label_ids[1]] - normalizer)
    score = float(np.exp(lp1 - np.logaddexp(lp0, lp1)))
    best = int(np.argmax(values))
    top = np.argsort(values)[-5:][::-1]
    return {"logprob_0": lp0, "logprob_1": lp1, "p0": math.exp(lp0), "p1": math.exp(lp1),
            "s": score, "pred_argmax": int(score >= .5), "greedy_token_id": best,
            "top5": [{"token_id": int(i), "logprob": float(values[i] - normalizer)} for i in top]}


def load_inputs(root, bundle_name, manifest_sha):
    root = Path(root)
    packed = sorted(root.rglob(bundle_name))
    if len(packed) > 1:
        raise ValueError("Ambiguous input bundle")
    if packed:
        archive = ZipFile(packed[0])
        read = archive.read
    else:
        candidates = sorted(root.rglob("input_manifest.json"))
        if len(candidates) != 1:
            raise ValueError("Expected exactly one input manifest")
        folder = candidates[0].parent
        read = lambda name: (folder / name).read_bytes()
        archive = None
    try:
        raw = read("input_manifest.json")
        if digest_bytes(raw) != manifest_sha:
            raise ValueError("Input manifest hash mismatch")
        manifest = json.loads(raw)
        locked_values = {}
        for ref in manifest.get("threshold_locks", []):
            payload = read(ref["member"])
            if digest_bytes(payload) != ref["sha256"]:
                raise ValueError("Threshold lock file hash mismatch")
            lock = json.loads(payload)
            body = {k: v for k, v in lock.items() if k != "locked_sha256"}
            checks = [digest_bytes(json.dumps(body, sort_keys=True, ensure_ascii=False, indent=2).encode()), canonical(body)]
            if lock.get("locked_sha256") not in checks:
                raise ValueError("Threshold self-seal mismatch")
            for entry in lock["entries"].values():
                locked_values[entry["arm"], entry.get("seed", 42), entry["dataset"]] = entry["tau_star"]
        groups = []
        for group in manifest["groups"]:
            if group["split"] == "test" and locked_values.get((group["arm"], group["seed"], group["dataset"])) != group.get("tau"):
                raise ValueError("Test threshold is not the frozen validation lock")
            payload = read(group["member"])
            if digest_bytes(payload) != group["sha256"]:
                raise ValueError("Frozen prompt-file hash mismatch")
            prompts = jsonl(payload)
            if len(prompts) != group["count"] or len({str(r["id"]) for r in prompts}) != len(prompts):
                raise ValueError("Prompt census/duplicates mismatch")
            for r in prompts:
                if (r["arm"], r["seed"], r["dataset"], r["split"]) != (group["arm"], group["seed"], group["dataset"], group["split"]):
                    raise ValueError("Prompt group identity mismatch")
                if digest_bytes(r["prompt"].encode()) != r["prompt_sha256"]:
                    raise ValueError("Individual prompt text hash mismatch")
            groups.append((group, prompts))
        legacy_raw = read("legacy_records.jsonl")
        if digest_bytes(legacy_raw) != manifest["legacy_records_sha256"]:
            raise ValueError("Legacy migration payload mismatch")
        legacy = jsonl(legacy_raw)
        expected = {(g["arm"], g["seed"], g["dataset"], g["split"], str(r["id"])): r for g, rs in groups for r in rs}
        by_key = {}
        for r in legacy:
            key = (r["arm"], r["seed"], r["dataset"], r["split"], str(r["id"]))
            if key in by_key or key not in expected:
                raise ValueError("Legacy record ID is duplicate or absent from current inputs")
            p = expected[key]
            if (r["prompt_sha256"], r["label"], r["model_sha256"]) != (p["prompt_sha256"], p["label"], manifest["model_sha256"]):
                raise ValueError("Legacy record prompt/label/model differs")
            if not r.get("valid") or not math.isfinite(r["s"]) or not 0 <= r["s"] <= 1:
                raise ValueError("Invalid legacy score")
            by_key[key] = r
        if len(by_key) != manifest["legacy_count"]:
            raise ValueError("Legacy migration count mismatch")
        return manifest, groups, by_key
    finally:
        if archive:
            archive.close()


def key_for(g, row):
    return g["arm"], g["seed"], g["dataset"], g["split"], str(row["id"])


def validate_saved(row, prompt, group, manifest, legacy, contract_sha, root=None):
    key = key_for(group, row)
    if (row.get("arm"), row.get("seed"), row.get("dataset"), row.get("split")) != key[:4]:
        raise ValueError("Saved row identity mismatch")
    if (row.get("prompt_sha256"), row.get("label"), row.get("model_sha256")) != (prompt["prompt_sha256"], prompt["label"], manifest["model_sha256"]):
        raise ValueError("Saved row input identity mismatch")
    if key in legacy:
        if canonical(row) != canonical(legacy[key]):
            raise ValueError("Historical record changed during migration")
    elif row.get("runtime_contract_sha256") != contract_sha or row.get("inference_seed") != 4294967295 or row.get("record_origin") != "fresh_locked":
        raise ValueError("Non-legacy row lacks runtime-lock evidence")
    elif root is not None:
        evidence = (Path(root) / row['runtime_provenance']).resolve()
        if not evidence.is_relative_to(Path(root).resolve()):
            raise ValueError('Unsafe provenance path')
        payload = evidence.read_bytes()
        if digest_bytes(payload) != row.get('runtime_provenance_sha256'):
            raise ValueError('Saved provenance hash mismatch')
        info = json.loads(payload)
        if (info['runtime_contract_sha256'], info['input_manifest_sha256'], info['runner_sha256']) != (contract_sha, manifest['_manifest_sha256'], manifest['worker_sha256']):
            raise ValueError('Saved provenance identity mismatch')
        for filename, field in [('model_load_offload.log','offload_log_sha256'),('backend_build.log','backend_build_log_sha256')]:
            if digest_bytes((evidence.parent / filename).read_bytes()) != info[field]:
                raise ValueError('Saved native/build evidence hash mismatch')
    if not row.get("valid") or not math.isfinite(row["s"]) or not 0 <= row["s"] <= 1:
        raise ValueError("Invalid saved score")


def main(args):
    from grace_runtime_contract import load_contract, assert_runtime, provenance, load_locked_model, digest, command, EXPECTED_CONTRACT_SHA256
    from transformers import AutoTokenizer
    runtime = load_contract()
    assert_runtime(runtime)
    manifest, groups, legacy = load_inputs(args.input_root, args.bundle, args.manifest_sha)
    manifest['_manifest_sha256'] = args.manifest_sha
    if digest(__file__) != manifest['worker_sha256']:
        raise ValueError('Worker source differs from pinned input manifest')
    if manifest["runtime_contract_sha256"] != EXPECTED_CONTRACT_SHA256:
        raise ValueError("Input is for a different runtime contract")
    root = Path(args.out)
    root.mkdir(parents=True, exist_ok=True)
    identity = {"input_manifest_sha256": args.manifest_sha, "runtime_contract_sha256": EXPECTED_CONTRACT_SHA256,
                "model_sha256": manifest["model_sha256"], "constructor": runtime["constructor"],
                "legacy_records_sha256": manifest["legacy_records_sha256"], "legacy_count": len(legacy),
                "runtime_lock_scope": "newly inferred records only; imported historical records are byte/value preserved", "method": manifest["method"]}
    previous = root / "run_identity.json"
    if previous.exists() and json.loads(previous.read_text(encoding="utf-8")) != identity:
        raise ValueError("Refusing checkpoint from a different input/runtime/migration identity")
    atomic(previous, identity)
    Path(root / "inference_runtime_lock.json").write_bytes(Path("/kaggle/working/inference_runtime_lock.json").read_bytes())
    atomic(root / "legacy_migration.json", {"classification": manifest["legacy_classification"], "records": [{"key": list(k), "sha256": canonical(r)} for k, r in legacy.items()]})
    saved = {}
    for group, prompts in groups:
        name = f"{group['arm']}/seed_{group['seed']}/{group['dataset']}/{group['split']}"
        target = root / name / "records.jsonl"
        target.parent.mkdir(parents=True, exist_ok=True)
        existing = jsonl(target.read_bytes()) if target.exists() else []
        lookup = {str(p["id"]): p for p in prompts}
        done = {}
        for row in existing:
            uid = str(row["id"])
            if uid in done or uid not in lookup:
                raise ValueError("Unexpected or duplicate saved ID")
            validate_saved(row, lookup[uid], group, manifest, legacy, EXPECTED_CONTRACT_SHA256, root)
            done[uid] = row
        imported = [r for k, r in legacy.items() if k[:4] == (group["arm"], group["seed"], group["dataset"], group["split"]) and str(r["id"]) not in done]
        if imported:
            with target.open("a", encoding="utf-8", newline="\n") as f:
                for row in imported:
                    f.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")
                    done[str(row["id"])] = row
                f.flush(); os.fsync(f.fileno())
        saved[name] = done
    status = {"state": "setup", "groups": {name: len(rs) for name, rs in saved.items()}, "new_records_this_session": 0, "legacy_count": len(legacy)}
    checkpoint = Path(args.checkpoint)
    last_export = 0.0

    def export(force=False):
        nonlocal last_export
        atomic(root / "status.json", status)
        if force or time.monotonic() - last_export > 60:
            temp = checkpoint.with_suffix(".zip.tmp")
            with ZipFile(temp, "w", compression=ZIP_DEFLATED) as archive:
                for path in sorted(root.rglob("*")):
                    if path.is_file() and not path.name.endswith(".tmp"):
                        archive.write(path, path.relative_to(root).as_posix())
            os.replace(temp, checkpoint)
            last_export = time.monotonic()

    export(True)
    stop_at = args.deadline - 300
    try:
        if all(len(saved[f"{g['arm']}/seed_{g['seed']}/{g['dataset']}/{g['split']}"]) == len(rs) for g, rs in groups):
            status["state"] = "complete"
            return
        if time.time() >= stop_at:
            status["state"] = "timed_out_before_model"
            return
        model_path = Path(args.model)
        model_sha = digest(model_path)
        if model_sha != runtime["model"]["sha256"] or model_sha != manifest["model_sha256"]:
            raise ValueError("Model hash mismatch")
        tokenizer = AutoTokenizer.from_pretrained(runtime["tokenizer"]["repo"], revision=runtime["tokenizer"]["revision"])
        session = Path(tempfile.mkdtemp(prefix="locked_", dir=root))
        provenance_file = session / "runtime_provenance.json"
        info = provenance(runtime, __file__, provenance_file)
        info["runtime_helper_sha256"] = digest(Path("/kaggle/working/grace_runtime_contract.py"))
        info["input_manifest_sha256"] = args.manifest_sha
        info["model_sha256"] = model_sha
        build_log = session / 'backend_build.log'
        shutil.copyfile('/kaggle/working/grace_diagnostics/install_llama_cuda.log', build_log)
        info["backend_build_log_sha256"] = digest(build_log)
        load_log = session / "model_load_offload.log"
        tm = {"tokenizer": runtime["tokenizer"]["repo"], "tokenizer_revision": runtime["tokenizer"]["revision"], "prompt_budget_tokens": 8192}
        llm = load_locked_model(runtime, model_path, tm, -1, load_log, model_sha)
        info["offload_log_sha256"] = digest(load_log)
        info["gpu_after_load"] = command(["nvidia-smi", "--query-gpu=index,uuid,name,memory.free,memory.total,driver_version", "--format=csv,noheader"])
        atomic(provenance_file, info)
        provenance_sha = digest(provenance_file)
        label_ids = []
        for label in ["0", "1"]:
            hf = tokenizer.encode(label, add_special_tokens=False)
            gguf = llm.tokenize(label.encode(), add_bos=False, special=False)
            if len(hf) != 1 or hf != gguf:
                raise ValueError("Binary token identity mismatch")
            label_ids.append(hf[0])
        status["state"] = "running"
        for group, prompts in groups:
            name = f"{group['arm']}/seed_{group['seed']}/{group['dataset']}/{group['split']}"
            done = saved[name]
            atomic(root / name / "group_identity.json", {**group, "runtime_lock_scope": identity["runtime_lock_scope"]})
            with (root / name / "records.jsonl").open("a", encoding="utf-8", newline="\n") as output:
                for item in prompts:
                    uid = str(item["id"])
                    if uid in done:
                        continue
                    if time.time() >= stop_at:
                        status["state"] = "timed_out"
                        return
                    messages = [{"role": "user", "content": item["prompt"]}]
                    chat = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                    hf_ids = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True, return_dict=False)
                    ids = llm.tokenize(chat.encode(), add_bos=False, special=True)
                    if ids != list(hf_ids) or len(ids) + 64 > 8192:
                        raise ValueError(f"Tokenizer/context check failed at {uid}")
                    start = time.monotonic()
                    llm.reset()
                    llm.eval(ids)
                    score = binary_scores(llm.scores[llm.n_tokens - 1], label_ids)
                    raw = llm.detokenize([score["greedy_token_id"]]).decode("utf-8", errors="replace").strip()
                    row = {k: item[k] for k in ["id", "dataset", "split", "label", "prompt_sha256", "demo_ids", "tokens", "graph_missing"]}
                    row.update(score, arm=group["arm"], seed=group["seed"], raw=raw, response_valid=raw in ("0", "1"), valid=True,
                               model_sha256=model_sha, tokenizer_revision=runtime["tokenizer"]["revision"], token_ids={"0": label_ids[0], "1": label_ids[1]},
                               runtime_contract_sha256=EXPECTED_CONTRACT_SHA256, inference_seed=runtime["constructor"]["seed"],
                               runtime_provenance=provenance_file.relative_to(root).as_posix(), runtime_provenance_sha256=provenance_sha, record_origin="fresh_locked",
                               elapsed_s=time.monotonic() - start, timestamp=datetime.now(timezone.utc).isoformat())
                    if group["split"] == "test":
                        row.update(tau=group["tau"], pred_tau=int(row["s"] >= group["tau"]))
                    output.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")
                    output.flush(); os.fsync(output.fileno())
                    done[uid] = row
                    status["groups"][name] = len(done)
                    status["new_records_this_session"] += 1
                    export()
                    print(f"PROGRESS {name}: {len(done)}/{len(prompts)} id={uid}", flush=True)
        status["state"] = "complete"
    except BaseException as exc:
        status.update(state="error", error_type=type(exc).__name__, error=str(exc))
        raise
    finally:
        status["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
        export(True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for name in ["input-root", "bundle", "manifest-sha", "out", "checkpoint", "model"]:
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--deadline", type=float, required=True)
    main(parser.parse_args())
