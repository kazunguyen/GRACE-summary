"""Verify the completed Kaggle B1-H2 validation lock and adopt its tau values.

This keeps the earlier Colab lock as a separately named historical entry.
It does not read test records or use the Colab threshold values for fitting.
"""
from __future__ import annotations

import hashlib
import io
import json
import math
import re
import sys
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "Runs-management"))
from validation_lock import RULES_SHA256, pick_threshold  # noqa: E402

ARM = "B1-H2"
SEED = 42
MODEL_SHA256 = "f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335"
BASE = ROOT / "11_Arm_B1H2_Evidence/kaggle_b1h2_validation_20261106"
OUTPUT = BASE / "downloaded_output"
INPUT_BUNDLE = BASE / "grace_b1_h2_validation_inputs.zip"
LOCK_SOURCE = OUTPUT / "b1_h2_validation/kaggle_threshold_lock.json"
STATUS_SOURCE = OUTPUT / "b1_h2_validation/seed_42_status.json"
SUMMARY_SOURCE = OUTPUT / "b1_h2_validation/batch_summary.json"
KERNEL_LOG = OUTPUT / "02-kaggle-qwen-q4-b1-h2-validation-20261106-ipynb.log"
AUDIT_PATH = ROOT / "Runs-management/b1h2_kaggle_validation_audit_20261106.json"
LOCK_COPY = ROOT / "Runs-management/b1h2_kaggle_validation_threshold_lock_20261106.json"
EVIDENCE_ZIP = BASE / "b1h2_kaggle_validation_evidence_20261106.zip"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def digest_json(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return sha256_bytes(raw)


def frozen_labels(dataset: str) -> dict[str, int]:
    path = ROOT / f"01_Author_Baseline_Unified/output/local_full/{dataset}/bundles/validation/specs.jsonl"
    found: dict[str, int] = {}
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            if not line.strip():
                continue
            row = json.loads(line)
            uid = str(row["id"])
            if uid.startswith(f"{dataset}:validation:"):
                if uid in found:
                    raise ValueError(f"Duplicate frozen label ID: {uid}")
                found[uid] = int(row["label"])
    return found


def log_lock_time() -> tuple[str, str]:
    """Derive the logged lock-cell wall time from Kaggle UTC anchor + runtime offset."""
    text = KERNEL_LOG.read_text(encoding="utf-8", errors="replace")
    anchor = re.search(r"UTC: (\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d+\+00:00)", text)
    event = re.search(r'"time":([0-9.]+),"data":"Kaggle validation thresholds locked:', text)
    if not anchor or not event:
        raise ValueError("Cannot recover Kaggle lock event time from kernel log")
    started = datetime.fromisoformat(anchor.group(1))
    observed = started + timedelta(seconds=float(event.group(1)))
    return observed.isoformat(), "Kaggle kernel UTC anchor plus lock-cell runtime offset; source is downloaded kernel log"


def score_from_logits(row: dict) -> float:
    delta = float(row["logprob_1"]) - float(row["logprob_0"])
    if delta >= 0:
        return 1.0 / (1.0 + math.exp(-delta))
    exp_delta = math.exp(delta)
    return exp_delta / (1.0 + exp_delta)


def main() -> None:
    for required in (INPUT_BUNDLE, LOCK_SOURCE, STATUS_SOURCE, SUMMARY_SOURCE, KERNEL_LOG):
        if not required.is_file():
            raise FileNotFoundError(required)

    lock = read_json(LOCK_SOURCE)
    status = read_json(STATUS_SOURCE)
    summary = read_json(SUMMARY_SOURCE)
    if lock["schema"] != "b1h2_kaggle_validation_threshold_lock_v1":
        raise ValueError(f"Unexpected lock schema: {lock.get('schema')}")
    if lock["arm"] != ARM or lock["seed"] != SEED or lock["split"] != "validation":
        raise ValueError("Wrong arm/seed/split in Kaggle lock")
    unsigned_lock = {k: v for k, v in lock.items() if k != "locked_sha256"}
    if digest_json(unsigned_lock) != lock["locked_sha256"]:
        raise ValueError("Kaggle lock self-checksum does not match")
    if status.get("state") != "complete" or status.get("timed_out"):
        raise ValueError("Kaggle validation status is not complete")
    if summary.get("state") != "validation_complete":
        raise ValueError("Kaggle batch summary does not report validation_complete")
    if lock.get("bundle_sha256") != sha256_file(INPUT_BUNDLE):
        raise ValueError("Input bundle SHA-256 differs from lock")
    if lock.get("model_sha256") != MODEL_SHA256:
        raise ValueError("Unexpected model SHA-256")

    outer = zipfile.ZipFile(INPUT_BUNDLE)
    checked = {}
    lock_time, lock_time_basis = log_lock_time()
    for dataset, expected_count in (("devign", 2732), ("reveal", 2273)):
        nested_name = f"seed_42/{dataset}_validation.zip"
        nested = zipfile.ZipFile(io.BytesIO(outer.read(nested_name)))
        prompt_rows = [json.loads(line) for line in nested.read("prompts.jsonl").splitlines() if line.strip()]
        expected = {str(row["id"]): row for row in prompt_rows}
        if len(expected) != expected_count:
            raise ValueError(f"{dataset}: expected input count {expected_count}, got {len(expected)}")
        labels = frozen_labels(dataset)
        if set(expected) != set(labels):
            raise ValueError(f"{dataset}: input IDs differ from frozen validation label IDs")

        records_path = OUTPUT / f"b1_h2_validation/seed_42/{dataset}/validation/records.jsonl"
        raw = records_path.read_bytes()
        records = [json.loads(line) for line in raw.splitlines() if line.strip()]
        record_by_id = {str(row["id"]): row for row in records}
        if len(records) != expected_count or len(record_by_id) != expected_count:
            raise ValueError(f"{dataset}: incomplete or duplicate Kaggle records")
        if set(record_by_id) != set(expected):
            raise ValueError(f"{dataset}: Kaggle record IDs differ from complete prompt set")

        for uid, row in record_by_id.items():
            prompt = expected[uid]
            if row.get("arm") != ARM or row.get("dataset") != dataset or row.get("split") != "validation":
                raise ValueError(f"{dataset}: incorrect arm/dataset/split for {uid}")
            if row.get("seed") != SEED or row.get("model_sha256") != MODEL_SHA256:
                raise ValueError(f"{dataset}: incorrect seed/model identity for {uid}")
            if int(row.get("label", -1)) != int(prompt["label"]) or int(row["label"]) != labels[uid]:
                raise ValueError(f"{dataset}: validation label mismatch for {uid}")
            if row.get("prompt_sha256") != prompt.get("prompt_sha256"):
                raise ValueError(f"{dataset}: prompt hash mismatch for {uid}")
            if row.get("valid") is not True:
                raise ValueError(f"{dataset}: invalid threshold score for {uid}")
            for key in ("s", "logprob_0", "logprob_1"):
                if not isinstance(row.get(key), (int, float)) or not math.isfinite(row[key]):
                    raise ValueError(f"{dataset}: non-finite {key} for {uid}")
            if not 0 <= float(row["s"]) <= 1 or abs(float(row["s"]) - score_from_logits(row)) > 1e-10:
                raise ValueError(f"{dataset}: score does not match binary logprobs for {uid}")

        fitted = pick_threshold(records)
        result = lock["results"][dataset]
        if fitted["tau"] != result["tau_star"] or abs(fitted["validation_mcc"] - result["mcc_at_tau"]) > 1e-12:
            raise ValueError(f"{dataset}: independent validation lock does not match Kaggle lock")
        if len(result["grid"]) != 99:
            raise ValueError(f"{dataset}: expected all 99 threshold grid results")
        for got, expected_grid in zip(fitted["grid_results"], result["grid"]):
            if got["threshold"] != expected_grid["tau"]:
                raise ValueError(f"{dataset}: threshold grid ordering mismatch")
            if abs(got["mcc"] - expected_grid["mcc"]) > 1e-12:
                raise ValueError(f"{dataset}: MCC grid differs at tau={got['threshold']}")

        manifest = read_json(OUTPUT / f"b1_h2_validation/seed_42/{dataset}/validation/run_manifest.json")
        per_run = status["runs"][f"{dataset}/validation"]
        if per_run.get("state") != "complete" or per_run.get("completed") != expected_count:
            raise ValueError(f"{dataset}: batch status is not complete")
        if manifest.get("bundle_sha256") != per_run.get("bundle_sha256"):
            raise ValueError(f"{dataset}: run manifest and batch status bundle differ")

        evidence_rows = [
            {k: row.get(k) for k in ("id", "label", "prompt_sha256", "model_sha256", "seed", "s", "valid")}
            for row in (record_by_id[uid] for uid in sorted(record_by_id))
        ]
        checked[dataset] = {
            "n_expected": expected_count,
            "n_records": len(records),
            "n_unique_ids": len(record_by_id),
            "n_valid_scores": sum(bool(row.get("valid")) for row in records),
            "n_response_valid": sum(bool(row.get("response_valid")) for row in records),
            "prompt_set_sha256": manifest["prompt_set_sha256"],
            "records_sha256": sha256_bytes(raw),
            "records_sha256_matches_kaggle_lock": sha256_bytes(raw) == result["records_sha256"],
            "validation_evidence_sha256": digest_json(evidence_rows),
            "tau_star": result["tau_star"],
            "mcc_at_tau": result["mcc_at_tau"],
            "grid_points": len(result["grid"]),
            "independent_reproduction_matches": True,
            "manifest": manifest,
            "evaluation": read_json(OUTPUT / f"b1_h2_validation/seed_42/{dataset}/validation/evaluation.json"),
        }
        if checked[dataset]["records_sha256"] != result["records_sha256"]:
            raise ValueError(f"{dataset}: output records hash differs from Kaggle lock")

    if summary.get("progress") != {"42/devign": 2732, "42/reveal": 2273}:
        raise ValueError("Kaggle batch summary does not show the complete validation census")
    if summary.get("bundle_sha256") != lock.get("bundle_sha256"):
        raise ValueError("Kaggle batch summary bundle does not match lock")

    # Preserve the exact Kaggle-generated lock JSON as a stable project artifact.
    LOCK_COPY.write_bytes(LOCK_SOURCE.read_bytes())

    # Package only validation inputs/outputs and runtime provenance; no test records are included.
    members = {
        "input/grace_b1_h2_validation_inputs.zip": INPUT_BUNDLE,
        "output/kaggle_threshold_lock.json": LOCK_SOURCE,
        "output/batch_summary.json": SUMMARY_SOURCE,
        "output/seed_42_status.json": STATUS_SOURCE,
        "output/devign_records.jsonl": OUTPUT / "b1_h2_validation/seed_42/devign/validation/records.jsonl",
        "output/devign_run_manifest.json": OUTPUT / "b1_h2_validation/seed_42/devign/validation/run_manifest.json",
        "output/devign_evaluation.json": OUTPUT / "b1_h2_validation/seed_42/devign/validation/evaluation.json",
        "output/reveal_records.jsonl": OUTPUT / "b1_h2_validation/seed_42/reveal/validation/records.jsonl",
        "output/reveal_run_manifest.json": OUTPUT / "b1_h2_validation/seed_42/reveal/validation/run_manifest.json",
        "output/reveal_evaluation.json": OUTPUT / "b1_h2_validation/seed_42/reveal/validation/evaluation.json",
        "runtime/events.log": OUTPUT / "grace_diagnostics/events.log",
        "runtime/gpu.log": OUTPUT / "grace_diagnostics/gpu.log",
        "runtime/validation_seed_42.log": OUTPUT / "grace_diagnostics/validation_seed_42.log",
        "runtime/kaggle_kernel_output.log": KERNEL_LOG,
    }
    with zipfile.ZipFile(EVIDENCE_ZIP, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for member, source in members.items():
            archive.write(source, member)

    # Adopt the new Kaggle lock in the active, self-signing config while leaving the 14
    # non-B1-H2 values untouched. The old configuration checksum is retained as predecessor.
    config_paths = [
        ROOT / "configs/thresholds.json",
        ROOT / "01_Author_Baseline_Unified/diagnostic_kit/configs/thresholds.json",
    ]
    flat_paths = [
        ROOT / "configs/thresholds_flat.json",
        ROOT / "01_Author_Baseline_Unified/diagnostic_kit/configs/thresholds_flat.json",
    ]
    config = read_json(config_paths[0])
    previous_checksum = config["locked_sha256"]
    if previous_checksum != lock.get("previous_config_checksum", previous_checksum):
        # The Kaggle lock is independent of the previous config file and intentionally
        # does not claim a checksum relationship; this branch only guards empty values.
        if not previous_checksum:
            raise ValueError("Missing previous active config checksum")
    if previous_checksum != "eedb783ebba986cec772bde2bdcca1cb95a2cd9db4bebd8141a44f49342178e5":
        raise ValueError(f"Unexpected active config predecessor: {previous_checksum}")
    old_14 = {k: v for k, v in config["thresholds"].items() if "B1-H2" not in k}
    for dataset in ("devign", "reveal"):
        result = lock["results"][dataset]
        key = f"{dataset}|{ARM}|{SEED}"
        config["thresholds"][key] = result["tau_star"]
        config["details"][key] = {
            "arm": ARM,
            "dataset": dataset,
            "mcc_at_tau": result["mcc_at_tau"],
            "n_total": result["n_total"],
            "n_valid": result["n_valid"],
            "prompt_set_sha256": checked[dataset]["prompt_set_sha256"],
            "seed": SEED,
            "split": "validation",
            "tau_star": result["tau_star"],
            "validation_evidence_sha256": checked[dataset]["validation_evidence_sha256"],
            "validation_records_sha256": checked[dataset]["records_sha256"],
            "validation_bundle_sha256": status["runs"][f"{dataset}/validation"]["bundle_sha256"],
            "threshold_lock_sha256": lock["locked_sha256"],
            "platform": "Kaggle",
            "gpu": "2x NVIDIA Tesla T4",
            "gpu_offload_verified": True,
            "runtime_python": checked[dataset]["manifest"]["python"],
            "supersedes": "Colab exploratory lock; see historical commit 846279676b60ca1185210642e75699b914e36a4d",
        }
    if len(config["thresholds"]) != 16 or old_14 != {k: v for k, v in config["thresholds"].items() if "B1-H2" not in k}:
        raise ValueError("The 14 preceding threshold values must remain unchanged")
    config["metadata"]["locked_utc"] = lock_time
    config["metadata"]["previous_locked_sha256"] = previous_checksum
    config["metadata"]["previous_b1h2_colab_lock_sha256"] = previous_checksum
    config["metadata"]["total_thresholds_locked"] = len(config["thresholds"])
    config["metadata"]["reseal_reason"] = (
        "Replaced B1-H2 entries using complete Kaggle 2xT4 validation inference and exact-ID frozen-label join; "
        "Colab values are retained as exploratory history and not reused. Existing other 14 values unchanged."
    )
    unsigned_config = {k: v for k, v in config.items() if k != "locked_sha256"}
    config["locked_sha256"] = hashlib.sha256(
        json.dumps(unsigned_config, indent=2, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    for path in config_paths:
        path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

    flat = dict(sorted(config["thresholds"].items()))
    for path in flat_paths:
        path.write_text(json.dumps(flat, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

    # Maintain the runtime lock ledger: the canonical B1-H2 keys now resolve to the
    # Kaggle lock; the former entries are retained under explicit historical names.
    run_locks_path = ROOT / "Runs-management/thresholds.json"
    run_locks = read_json(run_locks_path)
    old_entries = {}
    for dataset in ("devign", "reveal"):
        old_key = f"{ARM}/{dataset}"
        old = run_locks["entries"].pop(old_key)
        old["lock_variant"] = "colab-exploratory-superseded"
        old_entries[f"{ARM}-Colab-20261106/{dataset}"] = old
    run_locks["entries"].update(old_entries)
    for dataset in ("devign", "reveal"):
        result = lock["results"][dataset]
        manifest = checked[dataset]["manifest"]
        per_run = status["runs"][f"{dataset}/validation"]
        identity = {
            "model_sha256": MODEL_SHA256,
            "tokenizer": manifest["tokenizer"],
            "tokenizer_revision": manifest["tokenizer_revision"],
            "quantization": manifest["quantization"],
            "backend": "llama-cpp-python",
            "backend_version": manifest["llama_cpp_python"],
            "scoring": manifest["scoring"],
            "seed_recorded": SEED,
            "context_tokens": manifest["context_tokens"],
        }
        grid = [{"threshold": item["tau"], "mcc": item["mcc"]} for item in result["grid"]]
        run_locks["entries"][f"{ARM}/{dataset}"] = {
            "arm": ARM,
            "dataset": dataset,
            "split_used": "validation",
            "locked_at_utc": lock_time,
            "rules_sha256": RULES_SHA256,
            "identity": identity,
            "validation_prompt_set_sha256": checked[dataset]["prompt_set_sha256"],
            "n_expected": result["n_total"],
            "validation_evidence_sha256": checked[dataset]["validation_evidence_sha256"],
            "source_evidence": [
                {"kind": "kaggle_input_bundle", "path": "11_Arm_B1H2_Evidence/kaggle_b1h2_validation_20261106/grace_b1_h2_validation_inputs.zip", "sha256": lock["bundle_sha256"]},
                {"kind": "kaggle_output_lock", "path": "Runs-management/b1h2_kaggle_validation_threshold_lock_20261106.json", "sha256": sha256_file(LOCK_SOURCE)},
                {"kind": "records", "path": f"{dataset}/validation/records.jsonl", "sha256": checked[dataset]["records_sha256"]},
            ],
            "temporal_claim": "Selected from complete Kaggle validation only. A prior exploratory Colab test inference existed; this lock precedes any new confirmatory Kaggle B1-H2 test inference.",
            "tau": result["tau_star"],
            "validation_mcc": result["mcc_at_tau"],
            "n_valid": result["n_valid"],
            "n_invalid": result["n_total"] - result["n_valid"],
            "score_coverage": result["n_valid"] / result["n_total"],
            "degenerate": False,
            "grid_results": grid,
            "platform": "Kaggle 2x NVIDIA Tesla T4",
            "runtime_python": manifest["python"],
            "gpu_offload_verified": True,
            "output_lock_sha256": lock["locked_sha256"],
        }
        run_locks.setdefault("thresholds", {})[f"{dataset}|{ARM}|{SEED}"] = result["tau_star"]
    run_locks_path.write_text(json.dumps(run_locks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

    files = {}
    for member, source in members.items():
        files[member] = {"sha256": sha256_file(source), "size_bytes": source.stat().st_size}
    audit = {
        "schema": "b1h2_kaggle_validation_lock_audit_v1",
        "kernel": "duchuynguyen1802/02-kaggle-qwen-q4-b1-h2-validation-20261106-ipynb",
        "arm": ARM,
        "seed": SEED,
        "split": "validation",
        "validation_state": "complete",
        "counts": {"devign": 2732, "reveal": 2273, "total": 5005},
        "kaggle_validation_completed_at_utc": status["completed_at"],
        "threshold_lock_event_at_utc_from_kernel_log": lock_time,
        "threshold_lock_time_basis": lock_time_basis,
        "source_colab_lock_sha256": "eedb783ebba986cec772bde2bdcca1cb95a2cd9db4bebd8141a44f49342178e5",
        "colab_thresholds_superseded": {"devign": 0.09, "reveal": 0.67},
        "kaggle_lock_source": str(LOCK_SOURCE.relative_to(ROOT)).replace("\\", "/"),
        "kaggle_lock_file_sha256": sha256_file(LOCK_SOURCE),
        "kaggle_lock_embedded_sha256": lock["locked_sha256"],
        "input_bundle_sha256": lock["bundle_sha256"],
        "model_sha256": MODEL_SHA256,
        "runtime": {
            "gpu": "2x NVIDIA Tesla T4",
            "gpu_offload_verified": "offloaded 49/49 layers to GPU",
            "python": "3.13.16",
            "cuda": "13.0",
            "driver": "580.178.04",
            "llama_cpp_python": "0.3.16",
            "transformers": "4.57.1",
            "huggingface_hub": "0.36.2",
            "scikit_learn": "1.5.2",
            "numpy": "2.1.3",
        },
        "threshold_rule": "MCC over tau=0.01..0.99 in 0.01 increments; prediction score >= tau; tie closest to 0.5 then lower tau",
        "independent_reproduction": "Runs-management/validation_lock.py pick_threshold on downloaded Kaggle records after exact ID/label/prompt-hash comparison against the Kaggle input bundles and frozen validation specs",
        "all_5005_record_checks_passed": True,
        "test_data_read_for_threshold_selection": False,
        "results": checked,
        "evidence_archive": {
            "path": str(EVIDENCE_ZIP.relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha256_file(EVIDENCE_ZIP),
            "size_bytes": EVIDENCE_ZIP.stat().st_size,
            "members": files,
        },
    }
    AUDIT_PATH.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

    # Re-open the active config copies and fail if any mirror was not updated consistently.
    active = read_json(config_paths[0])
    if active["thresholds"].get("devign|B1-H2|42") != 0.09 or active["thresholds"].get("reveal|B1-H2|42") != 0.21:
        raise ValueError("Active B1-H2 thresholds do not match the independently reproduced Kaggle lock")
    if any(path.read_bytes() != config_paths[0].read_bytes() for path in config_paths[1:]):
        raise ValueError("Threshold JSON mirrors are not byte-identical")
    if any(path.read_bytes() != flat_paths[0].read_bytes() for path in flat_paths[1:]):
        raise ValueError("Flat threshold mirrors are not byte-identical")
    print(json.dumps({
        "active_thresholds": {"devign|B1-H2|42": 0.09, "reveal|B1-H2|42": 0.21},
        "validation_mcc": {"devign": checked["devign"]["mcc_at_tau"], "reveal": checked["reveal"]["mcc_at_tau"]},
        "active_config_locked_sha256": active["locked_sha256"],
        "kaggle_threshold_lock_sha256": lock["locked_sha256"],
        "audit": str(AUDIT_PATH.relative_to(ROOT)).replace("\\", "/"),
        "evidence_archive": str(EVIDENCE_ZIP.relative_to(ROOT)).replace("\\", "/"),
        "lock_time_utc": lock_time,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
