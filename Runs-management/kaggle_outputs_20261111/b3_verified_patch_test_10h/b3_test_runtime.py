"""Fail-closed B3 test package loader. Target labels never enter this module."""
import hashlib
import json
import math
import re
import zipfile
from pathlib import Path, PurePosixPath


def sha(raw):
    if isinstance(raw, (str, Path)):
        raw = Path(raw).read_bytes()
    return hashlib.sha256(raw).hexdigest()


def safe_name(name):
    if not name or "\\" in name or ":" in name or "\x00" in name:
        raise ValueError("Unsafe test package path")
    p = PurePosixPath(name)
    if p.is_absolute() or any(x in ("", ".", "..") for x in name.split("/")):
        raise ValueError("Unsafe test package path")
    return name


def read_zip(path):
    with zipfile.ZipFile(path) as archive:
        if archive.testzip() is not None: raise ValueError("Test package CRC failure")
        infos = archive.infolist()
        names = [safe_name(i.filename) for i in infos if not i.is_dir()]
        if len(names) != len(set(names)): raise ValueError("Duplicate test package member")
        if any((i.external_attr >> 16) & 0o170000 == 0o120000 for i in infos):
            raise ValueError("Symlink test package member")
        return {name: archive.read(name) for name in names}


def load_manifest(path, expected_sha256):
    raw = Path(path).read_bytes()
    if sha(raw) != expected_sha256: raise ValueError("Test prompt manifest hash mismatch")
    root = json.loads(raw)
    if root.get("status") != "SEALED_TEST_DELIVERY": raise ValueError("Test package not sealed")
    if (root.get("method_id"), root.get("arm"), root.get("seed"), root.get("inference_split")) != (
            "b3-verified-patch-v1", "B3", 42, "test"):
        raise ValueError("Test package scope mismatch")
    if root.get("labels_in_kaggle_input") is not False: raise ValueError("Target labels must be held out of Kaggle input")
    return root


def validate_archive(path, root):
    raw = Path(path).read_bytes()
    if sha(raw) != root["kaggle_input_archive_sha256"]: raise ValueError("Test input archive checksum mismatch")
    members = read_zip(path)
    if set(members) != set(root["kaggle_input_members_sha256"]): raise ValueError("Test input package inventory mismatch")
    for name, expected in root["kaggle_input_members_sha256"].items():
        if sha(members[name]) != expected: raise ValueError("Test input member hash mismatch: " + name)
    if any(re.search(r"(^|/)(?:labels(?:\.json|\.jsonl)?|test_labels\.json)$", n, re.I) for n in members):
        raise ValueError("Label artifact found in Kaggle inference package")
    return members


def read_input_directory(path):
    base = Path(path)
    if not base.is_dir(): raise ValueError("Expanded test input directory is missing")
    members = {}
    for item in sorted(base.rglob("*")):
        if item.is_symlink(): raise ValueError("Symlink in expanded test input")
        if item.is_file():
            name = item.relative_to(base).as_posix()
            safe_name(name)
            if name in members: raise ValueError("Duplicate expanded test input member")
            members[name] = item.read_bytes()
    return members


def validate_members(members, root):
    if set(members) != set(root["kaggle_input_members_sha256"]):
        raise ValueError("Test input member inventory mismatch")
    for name, expected in root["kaggle_input_members_sha256"].items():
        if sha(members[name]) != expected:
            raise ValueError("Test input member checksum mismatch: " + name)
    if any(re.search(r"(^|/)(?:labels(?:\.json|\.jsonl)?|test_labels\.json)$", n, re.I) for n in members):
        raise ValueError("Label artifact found in Kaggle inference package")
    return members


def read_dataset_rows(members, root, dataset):
    info = root["datasets"][dataset]
    name = f"prompts/{dataset}.jsonl"
    raw = members[name]
    if sha(raw) != info["prompts_sha256"]: raise ValueError("Prompt set hash mismatch")
    rows = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    if len(rows) != info["expected"] or len({r.get("id") for r in rows}) != len(rows):
        raise ValueError("Test census has missing/duplicate IDs")
    for row in rows:
        if any(k in row for k in ("label", "target", "target_label")):
            raise ValueError("Target label leaked into test prompt row")
        if (row.get("dataset"), row.get("split"), row.get("method_id")) != (dataset, "test", root["method_id"]):
            raise ValueError("Test prompt scope mismatch")
        if not row["id"].startswith(dataset + ":test:") or sha(row["prompt"].encode("utf-8")) != row["prompt_sha256"]:
            raise ValueError("Test prompt ID/hash mismatch")
    return rows


def load_threshold(root, members, dataset):
    """Verify validation-fitted threshold bytes and their frozen method identity."""
    name = f"threshold_locks/{dataset}_threshold_lock.json"
    raw = members[name]
    if sha(raw) != root["threshold_lock_sha256"][dataset]:
        raise ValueError("Threshold lock file checksum mismatch")
    lock = json.loads(raw.decode("utf-8"))
    unsigned = {k: v for k, v in lock.items() if k != "seal_sha256"}
    canonical = json.dumps(unsigned, sort_keys=True, separators=(",", ":"),
                           ensure_ascii=False, allow_nan=False).encode("utf-8")
    if sha(canonical) != lock.get("seal_sha256"):
        raise ValueError("Threshold lock canonical seal mismatch")
    if (lock.get("status"), lock.get("arm"), lock.get("method_id"),
        lock.get("seed"), lock.get("dataset"), lock.get("fit_split")) != (
        "LOCKED", "B3", root["method_id"], 42, dataset, "validation"):
        raise ValueError("Threshold scope mismatch")
    expected = {"method_id": root["method_id"],
        "pool_sha256": root["datasets"][dataset]["pool_sha256"],
        "model_sha256": root["model_sha256"],
        "tokenizer_revision": root["tokenizer_revision"],
        "runtime_contract_sha256": root["threshold_validation_runtime_contract_sha256"],
        "scoring": "unconstrained_first_token_logits_v1",
        "worker_sha256": root["threshold_application_worker_sha256"]}
    if any(lock["application_identity"].get(k) != v for k, v in expected.items()):
        raise ValueError("Threshold application identity mismatch")
    tau = lock.get("tau_star")
    if type(tau) not in (float, int) or not 0.01 <= tau <= 0.99:
        raise ValueError("Invalid locked threshold")
    if tau != root["datasets"][dataset]["tau_star"]:
        raise ValueError("Threshold value differs from sealed test delivery")
    return float(tau)


def run_identity(root, dataset):
    x = root["datasets"][dataset]
    return {"release_id": root["release_id"], "method_id": root["method_id"], "arm": "B3",
            "dataset": dataset, "split": "test", "seed": 42, "count": x["expected"],
            "prompts_sha256": x["prompts_sha256"], "pool_sha256": x["pool_sha256"],
            "model_sha256": root["model_sha256"], "tokenizer_revision": root["tokenizer_revision"],
            "runtime_contract_sha256": root["threshold_validation_runtime_contract_sha256"],
            "threshold_lock_sha256": root["threshold_lock_sha256"][dataset],
            "worker_sha256": root["test_worker_sha256"]}


def checked_records(output_root, root, rows, dataset, split="test", seed=42, arm="B3"):
    base = Path(output_root) / f"seed_{seed}" / dataset / split
    path = base / "records.jsonl"
    if not path.is_file(): return 0
    manifest_path = base / "run_manifest.json"
    if not manifest_path.is_file(): raise ValueError("Test records lack run identity manifest")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected_identity = run_identity(root, dataset)
    if manifest.get("b3_test_identity") != expected_identity: raise ValueError("Test resume identity mismatch")
    lookup = {r["id"]: r for r in rows}
    seen = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip(): continue
        record = json.loads(line)
        uid = record["id"]
        if uid in seen or uid not in lookup: raise ValueError("Duplicate/unexpected test ID")
        if any(k in record for k in ("label", "target", "target_label")):
            raise ValueError("Target label leaked into test prediction record")
        prompt = lookup[uid]
        if (record.get("prompt_sha256"), record.get("dataset"), record.get("split"),
                record.get("arm"), record.get("seed"), record.get("valid"),
                record.get("model_sha256"), record.get("runtime_contract_sha256")) != (
                prompt["prompt_sha256"], dataset, "test", arm, seed, True,
                root["model_sha256"], root["runtime_contract_sha256"]):
            raise ValueError("Test prediction identity mismatch")
        s, lp0, lp1 = record["s"], record["logprob_0"], record["logprob_1"]
        if any(type(x) not in (int, float) or not math.isfinite(x) for x in (s, lp0, lp1)) or not 0 <= s <= 1:
            raise ValueError("Invalid test score")
        # Use a stable branch-form sigmoid when the host math module lacks logaddexp.
        delta = lp1 - lp0
        expected = 1 / (1 + math.exp(-delta)) if delta >= 0 else math.exp(delta) / (1 + math.exp(delta))
        if abs(s - expected) > 1e-12: raise ValueError("Test score/logprob mismatch")
        tau = root["datasets"][dataset]["tau_star"]
        if record.get("threshold_tau") != tau or record.get("threshold_prediction") != int(s >= tau):
            raise ValueError("Test locked-threshold prediction mismatch")
        seen.add(uid)
    return len(seen)
