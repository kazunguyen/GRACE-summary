from __future__ import annotations

import hashlib
import json
import math
import sys
import zipfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "Runs-management"))
from validation_lock import make_lock, persist_lock  # noqa: E402

ARM = "B1-H2"
SEED = 42
MODEL_SHA256 = "f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335"
TOKENIZER = "Qwen/Qwen3-Coder-30B-A3B-Instruct"
TOKENIZER_REVISION = "b2cff646eb4bb1d68355c01b18ae02e7cf42d120"
PILOT_OUTPUT = ROOT / "11_Arm_B1H2_Evidence/colab_l4_pilot_20261106/downloaded_output/l4_pilot_output.zip"
REMAINING_OUTPUT = ROOT / "11_Arm_B1H2_Evidence/colab_l4_b1h2_remaining_validation_20261106/downloaded_output/l4_remaining_validation_output.zip"
REMAINING_BUNDLE = ROOT / "11_Arm_B1H2_Evidence/colab_l4_b1h2_remaining_validation_20261106/bundles/b1h2_l4_remaining_validation_bundle.zip"
OUTPUT_ANALYSIS = ROOT / "11_Arm_B1H2_Evidence/colab_l4_b1h2_remaining_validation_20261106/output_analysis.json"
CONFIG_PATH = ROOT / "configs/thresholds.json"
FLAT_PATH = ROOT / "configs/thresholds_flat.json"
RUNS_LOCK_PATH = ROOT / "Runs-management/thresholds.json"
DIAGNOSTIC_CONFIG = ROOT / "01_Author_Baseline_Unified/diagnostic_kit/configs"
REPORT_PATH = ROOT / "Runs-management/b1h2_threshold_lock_20261106.json"


def digest_json(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_records(archive: Path) -> list[dict]:
    with zipfile.ZipFile(archive) as zf:
        members = [name for name in zf.namelist() if name.endswith("records.jsonl")]
        if len(members) != 1:
            raise ValueError(f"Expected one records.jsonl in {archive}; got {members}")
        return [json.loads(line) for line in zf.read(members[0]).decode("utf-8").splitlines() if line.strip()]


def read_labels(dataset: str) -> dict[str, int]:
    specs = ROOT / f"01_Author_Baseline_Unified/output/local_full/{dataset}/bundles/validation/specs.jsonl"
    labels: dict[str, int] = {}
    with specs.open(encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            sample_id = row.get("id", "")
            if sample_id.startswith(f"{dataset}:validation:"):
                if sample_id in labels:
                    raise ValueError(f"Duplicate frozen validation label: {sample_id}")
                labels[sample_id] = int(row["label"])
    return labels


def read_input_prompt_hashes() -> tuple[dict[str, str], dict[str, str]]:
    with zipfile.ZipFile(REMAINING_BUNDLE) as zf:
        remaining = {
            row["id"]: row["prompt_sha256"]
            for row in (json.loads(line) for line in zf.read("prompts.jsonl").decode("utf-8").splitlines() if line.strip())
        }
        excluded_rows = zf.read("excluded_pilot_ids_prompt_hashes.tsv").decode("utf-8").splitlines()
    pilot = {}
    for line in excluded_rows:
        sample_id, prompt_hash = line.split("\t")
        pilot[sample_id] = prompt_hash
    return pilot, remaining


def assert_run_identity(records: list[dict], *, expected_count: int, ids: set[str]) -> None:
    got_ids = [str(row["id"]) for row in records]
    if len(records) != expected_count or len(set(got_ids)) != expected_count:
        raise ValueError(f"Unexpected record count or duplicate IDs: {len(records)} expected {expected_count}")
    if set(got_ids) != ids:
        raise ValueError(f"Inference IDs differ from frozen input: {len(set(got_ids) ^ ids)} IDs")
    for row in records:
        if row.get("arm") != ARM or row.get("split") != "validation" or row.get("seed") != SEED:
            raise ValueError(f"Wrong run identity: {row.get('id')}")
        if row.get("model_sha256") != MODEL_SHA256:
            raise ValueError(f"Unexpected model hash: {row.get('id')}")


def main() -> None:
    pilot_records = read_records(PILOT_OUTPUT)
    remaining_records = read_records(REMAINING_OUTPUT)
    pilot_hashes, remaining_hashes = read_input_prompt_hashes()
    if set(pilot_hashes) & set(remaining_hashes):
        raise ValueError("Pilot and continuation input prompt IDs overlap")
    if len(pilot_hashes) != 100 or len(remaining_hashes) != 4905:
        raise ValueError("Pilot/continuation bundle coverage differs from expected counts")

    all_records = pilot_records + remaining_records
    records_by_id = {str(row["id"]): row for row in all_records}
    if len(records_by_id) != len(all_records):
        raise ValueError("Duplicate inference IDs across pilot and continuation")
    all_input_hashes = pilot_hashes | remaining_hashes
    if set(records_by_id) != set(all_input_hashes):
        raise ValueError("Inference IDs do not cover the complete frozen B1-H2 validation set")
    for sample_id, row in records_by_id.items():
        if row.get("prompt_sha256") != all_input_hashes[sample_id]:
            raise ValueError(f"Prompt hash mismatch: {sample_id}")
        scores = (row.get("logprob_0"), row.get("logprob_1"), row.get("s"))
        if not all(isinstance(x, (int, float)) and math.isfinite(x) for x in scores):
            raise ValueError(f"Non-finite binary scores: {sample_id}")
        if not 0 <= float(row["s"]) <= 1:
            raise ValueError(f"Score outside [0, 1]: {sample_id}")
        row["valid"] = True

    group_records: dict[str, list[dict]] = defaultdict(list)
    group_expected: dict[str, list[dict]] = defaultdict(list)
    prompt_identity = []
    for dataset in ("devign", "reveal"):
        labels = read_labels(dataset)
        dataset_ids = {sample_id for sample_id, row in records_by_id.items() if row.get("dataset") == dataset}
        if dataset_ids != set(labels):
            raise ValueError(f"Frozen label IDs differ from B1-H2 IDs for {dataset}")
        for sample_id in sorted(dataset_ids):
            row = records_by_id[sample_id]
            label = labels[sample_id]
            row["label"] = label
            group_records[dataset].append(row)
            group_expected[dataset].append({"id": sample_id, "label": label, "prompt_sha256": row["prompt_sha256"]})
            prompt_identity.append({"id": sample_id, "prompt_sha256": row["prompt_sha256"]})

    manifest = {
        "model_sha256": MODEL_SHA256,
        "tokenizer": TOKENIZER,
        "tokenizer_revision": TOKENIZER_REVISION,
        "quantization": "Q4_K_M",
        "llama_cpp_python": "0.3.16",
        "scoring": "unconstrained_first_token_logits_v1",
        "context_tokens": 8192,
    }
    prompt_set_sha256 = digest_json(prompt_identity)
    remaining_analysis = json.loads(OUTPUT_ANALYSIS.read_text(encoding="utf-8"))
    source_evidence = [
        {"kind": "prompt_archive", "path": "grace_15arms_prompts_and_clean_specs (1).zip", "sha256": "9db0d3eebb66a2f83c1f9803ceb0192954a3dfe2c3de9515188a996ede84ed7b"},
        {"kind": "pilot_input_bundle", "path": "b1h2_l4_100_sample_bundle.zip", "sha256": "500b523dfe05623dc5d866c218f6100048527283f92c078ec486be928cb79b59"},
        {"kind": "pilot_output", "path": PILOT_OUTPUT.name, "sha256": file_sha256(PILOT_OUTPUT)},
        {"kind": "remaining_bundle", "path": REMAINING_BUNDLE.name, "sha256": file_sha256(REMAINING_BUNDLE)},
        {"kind": "remaining_output", "path": REMAINING_OUTPUT.name, "sha256": remaining_analysis["output_zip_sha256"]},
        {"kind": "frozen_validation_labels", "paths": [
            "01_Author_Baseline_Unified/output/local_full/devign/bundles/validation/specs.jsonl",
            "01_Author_Baseline_Unified/output/local_full/reveal/bundles/validation/specs.jsonl",
        ], "join": "exact sample ID; both datasets cover every inferred validation ID"},
    ]

    locks = {}
    for dataset in ("devign", "reveal"):
        lock = make_lock(
            group_expected[dataset], group_records[dataset], ARM, dataset, manifest, prompt_set_sha256,
            source_evidence=source_evidence,
        )
        lock["platform_deviation"] = "Google Colab Runtime Version 2026.10, single NVIDIA L4; preregistered execution is Kaggle 2xT4. Treat as disclosed platform-deviant validation."
        lock["gpu_offload_verified"] = False
        locks[dataset] = lock

    # Append evidence-backed entries to the current run lock while preserving all prior entries.
    for dataset in ("devign", "reveal"):
        persist_lock(RUNS_LOCK_PATH, locks[dataset])
    run_lock = json.loads(RUNS_LOCK_PATH.read_text(encoding="utf-8"))
    for dataset in ("devign", "reveal"):
        locks[dataset] = run_lock["entries"][f"{ARM}/{dataset}"]
        run_lock["thresholds"][f"{dataset}|{ARM}|{SEED}"] = locks[dataset]["tau"]
    with RUNS_LOCK_PATH.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(run_lock, stream, indent=2, ensure_ascii=False)
        stream.write("\n")

    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    new_keys = [f"{dataset}|{ARM}|{SEED}" for dataset in ("devign", "reveal")]
    existing_count = sum(key in config["thresholds"] for key in new_keys)
    if existing_count:
        if existing_count != len(new_keys):
            raise ValueError("Partial B1-H2 threshold lock found; inspect before proceeding")
        for dataset, key in zip(("devign", "reveal"), new_keys):
            detail = config["details"][key]
            if config["thresholds"][key] != locks[dataset]["tau"] or detail.get("validation_evidence_sha256") != locks[dataset]["validation_evidence_sha256"]:
                raise ValueError(f"Existing config lock conflicts with validation evidence for {dataset}")
        previous_lock_hash = config["metadata"].get("previous_locked_sha256")
    else:
        previous_lock_hash = config["locked_sha256"]
        for dataset in ("devign", "reveal"):
            lock = locks[dataset]
            key = f"{dataset}|{ARM}|{SEED}"
            config["thresholds"][key] = lock["tau"]
            config["details"][key] = {
                "arm": ARM,
                "dataset": dataset,
                "mcc_at_tau": lock["validation_mcc"],
                "n_total": lock["n_expected"],
                "n_valid": lock["n_valid"],
                "platform_deviation": "Colab Runtime Version 2026.10 / single NVIDIA L4; preregistered Kaggle execution uses 2xT4",
                "prompt_set_sha256": prompt_set_sha256,
                "seed": SEED,
                "split": "validation",
                "tau_star": lock["tau"],
                "validation_evidence_sha256": lock["validation_evidence_sha256"],
            }
        config["metadata"]["locked_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        config["metadata"]["previous_locked_sha256"] = previous_lock_hash
        config["metadata"]["total_thresholds_locked"] = len(config["thresholds"])
        config["metadata"]["reseal_reason"] = (
            "Supplemented with B1-H2 validation-only thresholds after exact-ID join to frozen validation labels; "
            "Colab L4 platform deviation disclosed in CHANGES_AFTER_PREREG.md. Existing 14 threshold values unchanged."
        )
        payload = {key: value for key, value in config.items() if key != "locked_sha256"}
        config["locked_sha256"] = hashlib.sha256(
            json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True).encode("utf-8")
        ).hexdigest()
        with CONFIG_PATH.open("w", encoding="utf-8", newline="\n") as stream:
            json.dump(config, stream, indent=2, ensure_ascii=False, sort_keys=True)
            stream.write("\n")
    flat = json.loads(FLAT_PATH.read_text(encoding="utf-8"))
    if any(flat.get(key) != locks[dataset]["tau"] for dataset, key in zip(("devign", "reveal"), new_keys)):
        flat.update({f"{dataset}|{ARM}|{SEED}": locks[dataset]["tau"] for dataset in ("devign", "reveal")})
        flat = {
            f"{dataset}|{arm}|{SEED}": flat[f"{dataset}|{arm}|{SEED}"]
            for dataset in ("devign", "reveal")
            for arm in ("B0", "B1", "B1-H2", "B2-flip", "B2-rep", "B2", "P-POST", "P-PRE")
            if f"{dataset}|{arm}|{SEED}" in flat
        }
        with FLAT_PATH.open("w", encoding="utf-8", newline="\n") as stream:
            json.dump(flat, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
    if DIAGNOSTIC_CONFIG.exists():
        (DIAGNOSTIC_CONFIG / "thresholds.json").write_bytes(CONFIG_PATH.read_bytes())
        (DIAGNOSTIC_CONFIG / "thresholds_flat.json").write_bytes(FLAT_PATH.read_bytes())

    report = {
        "schema": "b1h2_validation_threshold_lock_v1",
        "arm": ARM,
        "seed": SEED,
        "split": "validation",
        "platform": "Google Colab Runtime Version 2026.10 / single NVIDIA L4",
        "platform_deviation": "Preregistered Kaggle environment uses 2xT4; see CHANGES_AFTER_PREREG.md",
        "gpu_offload_verified": False,
        "prompt_set_sha256": prompt_set_sha256,
        "source_evidence": source_evidence,
        "entries_path": "Runs-management/thresholds.json",
        "locks": {
            dataset: {
                key: lock[key]
                for key in (
                    "arm", "dataset", "tau", "validation_mcc", "n_expected", "n_valid",
                    "validation_evidence_sha256", "identity", "platform_deviation", "gpu_offload_verified",
                )
            }
            for dataset, lock in locks.items()
        },
        "config_lock_sha256": config["locked_sha256"],
        "previous_config_lock_sha256": previous_lock_hash,
    }
    with REPORT_PATH.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(report, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")
    print(json.dumps({
        "config_lock_sha256": config["locked_sha256"],
        "previous_config_lock_sha256": previous_lock_hash,
        "prompt_set_sha256": prompt_set_sha256,
        "locks": {ds: {k: lock[k] for k in ("tau", "validation_mcc", "n_expected", "n_valid", "validation_evidence_sha256")} for ds, lock in locks.items()},
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
