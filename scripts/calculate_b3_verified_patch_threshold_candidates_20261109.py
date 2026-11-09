"""Compute, cross-check and preserve B3-new validation threshold candidates only.

Reads only the sealed Devign/REVEAL validation inputs and B3 validation records.
Does not read test artifacts and does not modify frozen threshold files.
"""
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "Runs-management"))
import b3_delivery_runtime as io
import validation_lock as optimizer

RUN = ROOT / "Runs-management/b3_lznt_resume_retry_20261109/b3-new-dual-resume-v2-retry1"
SOURCE = ROOT / "Runs-management/b3_lznt_linuxfix_20261109/b3_dual"
REMOTE = RUN / "remote_output"
OUT = RUN / "threshold_candidates_20261109"
EXPECTED = {"devign": 2732, "reveal": 2273}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def digest_json(value):
    return sha(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))


def mcc_counts(labels, scores, threshold):
    tp = tn = fp = fn = 0
    for y, score in zip(labels, scores):
        pred = score >= threshold
        if y == 1 and pred: tp += 1
        elif y == 0 and not pred: tn += 1
        elif y == 0 and pred: fp += 1
        else: fn += 1
    den = math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    value = (tp * tn - fp * fn) / den if den else None
    return {"threshold": threshold, "mcc": value, "tp": tp, "tn": tn, "fp": fp, "fn": fn}


def main():
    if OUT.exists():
        raise FileExistsError(f"Preserve existing threshold evidence: {OUT}")
    OUT.mkdir(parents=True)
    contract_path = SOURCE / "code/inference_runtime_lock.json"
    contract_sha = sha(contract_path.read_bytes())
    entries = {}
    for ds, expected_n in EXPECTED.items():
        root_path = SOURCE / "roots" / f"{ds}.json"
        root_raw = root_path.read_bytes()
        root = json.loads(root_raw)
        rows = io.validate_bundle(io.discover_bundle(SOURCE.parent / "datasets" / ds, root), root)[1]
        record_path = next((REMOTE / "b3_new_dual_validation_resume_v2_20261109" / ds).rglob("records.jsonl"))
        records_raw = record_path.read_bytes()
        records = [json.loads(line) for line in records_raw.decode("utf-8").splitlines() if line.strip()]
        checked = io.checked_records(record_path.parents[3], root, rows)
        if len(rows) != expected_n or len(records) != expected_n or checked != expected_n:
            raise ValueError(f"Incomplete/invalid validation census for {ds}: {len(records)}/{expected_n}")
        expected = {r["id"]: r for r in rows}
        actual = {r["id"]: r for r in records}
        if len(actual) != len(records) or set(actual) != set(expected):
            raise ValueError(f"Validation ID set mismatch for {ds}")
        for uid, record in actual.items():
            prompt = expected[uid]
            if record.get("label") != prompt["label"] or record.get("prompt_sha256") != prompt["prompt_sha256"]:
                raise ValueError(f"Label/prompt identity mismatch: {ds}/{uid}")
            if record.get("seed") != 42 or record.get("arm") != "B3" or record.get("split") != "validation":
                raise ValueError(f"Run identity mismatch: {ds}/{uid}")
            if record.get("model_sha256") != root["model_sha256"]:
                raise ValueError(f"Model identity mismatch: {ds}/{uid}")

        valid = [r for r in records if r.get("valid") and isinstance(r.get("s"), (int, float))
                 and math.isfinite(r["s"]) and 0 <= r["s"] <= 1]
        if len(valid) != expected_n:
            raise ValueError(f"This validation census has invalid numeric scores: {ds} {len(valid)}/{expected_n}")
        labels = [r["label"] for r in valid]
        scores = [float(r["s"]) for r in valid]
        if set(labels) != {0, 1}:
            raise ValueError(f"Both classes are required: {ds}")

        # Independent full 99-point sweep with explicit confusion counts.
        grid = [mcc_counts(labels, scores, i / 100) for i in range(1, 100)]
        defined = [r for r in grid if r["mcc"] is not None]
        if not defined:
            raise ValueError(f"No defined MCC candidate: {ds}")
        maximum = max(r["mcc"] for r in defined)
        ties = [r for r in defined if abs(r["mcc"] - maximum) <= 1e-9]
        selected = min(ties, key=lambda r: (abs(r["threshold"] - 0.5), r["threshold"]))

        # Independent implementation cross-check: compare all 99 MCCs and winner.
        optimizer_result = optimizer.pick_threshold(records)
        if len(optimizer_result["grid_results"]) != 99:
            raise AssertionError("Optimizer did not return the full grid")
        for own, other in zip(grid, optimizer_result["grid_results"]):
            if own["threshold"] != other["threshold"]:
                raise AssertionError("Threshold grid ordering mismatch")
            if own["mcc"] is None:
                if other["mcc"] is not None: raise AssertionError("Undefined MCC mismatch")
            elif other["mcc"] is None or abs(own["mcc"] - other["mcc"]) > 1e-12:
                raise AssertionError(f"MCC grid mismatch at {ds}/{own['threshold']}")
        if selected["threshold"] != optimizer_result["tau"]:
            raise AssertionError(f"Selected tau mismatch for {ds}")
        if abs(selected["mcc"] - optimizer_result["validation_mcc"]) > 1e-12:
            raise AssertionError(f"Selected MCC mismatch for {ds}")

        ordered_evidence = [{k: actual[uid].get(k) for k in
                             ("id", "label", "prompt_sha256", "model_sha256", "seed", "s", "valid")}
                            for uid in sorted(actual)]
        candidate = {
            "schema": "grace_b3_verified_patch_validation_threshold_candidate_v1",
            "status": "CANDIDATE_PENDING_GOVERNANCE_REVIEW_AND_SEAL",
            "arm": "B3", "method_id": root["method_id"], "dataset": ds,
            "seed": 42, "split_used": "validation", "n_expected": expected_n,
            "n_valid": len(valid), "n_invalid_numeric": expected_n - len(valid),
            "tau_star_candidate": selected["threshold"], "validation_mcc": selected["mcc"],
            "tp": selected["tp"], "tn": selected["tn"], "fp": selected["fp"], "fn": selected["fn"],
            "tie_thresholds_within_1e-9": [r["threshold"] for r in ties],
            "rules": optimizer.RULES,
            "rules_sha256": optimizer.RULES_SHA256,
            "independent_full_grid_crosscheck": "PASS; all 99 MCCs equal within 1e-12 and selected threshold agrees",
            "identity": {
                "release_id": root["release_id"], "input_root_sha256": sha(root_raw),
                "bundle_sha256": root["bundle_sha256"], "pool_sha256": root["pool_sha256"],
                "prompt_content_sha256": root["prompt_content_sha256"],
                "prompt_member_sha256": root["members_sha256"]["prompts.jsonl"],
                "labels_member_sha256": root["members_sha256"]["labels.json"],
                "model_sha256": root["model_sha256"], "tokenizer_revision": root["tokenizer_revision"],
                "runtime_contract_sha256": root["runtime_contract_sha256"],
                "runtime_contract_file_sha256": contract_sha,
                "worker_sha256": root["code_sha256"]["kaggle_inference.py"],
                "validation_records_sha256": sha(records_raw),
                "validation_evidence_sha256": digest_json(ordered_evidence),
                "run_manifest_sha256": sha(next((record_path.parent).glob("run_manifest.json")).read_bytes()),
            },
            "grid": grid,
            "governance": {
                "frozen_threshold_files_modified": False,
                "requires_PI_review_before_lock": True,
                "requires_new_scope_threshold_application_confirmation": True,
                "test_data_read": False,
            },
        }
        target = OUT / f"{ds}_threshold_candidate.json"
        target.write_text(json.dumps(candidate, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
                          encoding="utf-8", newline="\n")
        entries[ds] = {k: candidate[k] for k in
                       ("tau_star_candidate", "validation_mcc", "tp", "tn", "fp", "fn", "tie_thresholds_within_1e-9")}

    summary = {"status": "CANDIDATES_COMPUTED_NOT_LOCKED", "arm": "B3",
               "method_id": "b3-verified-patch-v1", "seed": 42,
               "candidate_thresholds": entries,
               "candidate_files": {ds: sha((OUT / f"{ds}_threshold_candidate.json").read_bytes()) for ds in EXPECTED},
               "frozen_threshold_files_modified": False,
               "test_data_read": False,
               "reason_not_sealed": "Plan Step 12 requires PI/governance review and authority confirmation before sealing the separate test lock."}
    (OUT / "candidate_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
                                               encoding="utf-8", newline="\n")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
