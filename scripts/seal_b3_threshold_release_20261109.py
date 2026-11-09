"""Reaudit B3 validation/runtime and seal the separately authorized threshold release.

Only validation inputs/records are read. Never modifies prior candidates or locks.
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
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "Runs-management"))
import b3_delivery_runtime as delivery
import validation_lock as optimizer
from b3_threshold_lock import canonical_hash, load_threshold
from calculate_b3_verified_patch_threshold_candidates_20261109 import mcc_counts

RUN = ROOT / "Runs-management/b3_lznt_resume_retry_20261109/b3-new-dual-resume-v2-retry1"
SOURCE = ROOT / "Runs-management/b3_lznt_linuxfix_20261109/b3_dual"
REMOTE = RUN / "remote_output/b3_new_dual_validation_resume_v2_20261109"
CANDIDATES = RUN / "threshold_candidates_20261109"
OUT = ROOT / "Runs-management/b3_verified_patch_v1/threshold_release_20261109_v1"
ZIP = ROOT / "Runs-management/grace_hieu_5arms_runtime_locked_20261107.zip"
FROZEN = [ROOT / "configs/thresholds.json", ROOT / "configs/thresholds_flat.json"]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)
                    + "\n", encoding="utf-8", newline="\n")


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def embedded_contracts():
    result = {}
    with zipfile.ZipFile(ZIP) as archive:
        require(archive.testzip() is None, "Original runtime ZIP CRC failure")
        for name in archive.namelist():
            notebook = json.loads(archive.read(name))
            found = []
            for cell in notebook["cells"]:
                source = "".join(cell["source"])
                if cell["cell_type"] != "code" or "RUNTIME_LOCK_BYTES = " not in source:
                    continue
                for node in ast.walk(ast.parse(source)):
                    if isinstance(node, ast.Assign) and any(
                            isinstance(t, ast.Name) and t.id == "RUNTIME_LOCK_BYTES"
                            for t in node.targets):
                        found.append(json.loads(ast.literal_eval(node.value)))
            require(len(found) == 1, "Ambiguous/missing embedded contract: " + name)
            result[name] = found[0]
    require(len(result) == 5, "Expected original five notebook contracts")
    return result


def audit_session(path, count, contract, root):
    p = json.loads(path.read_text(encoding="utf-8"))
    require(p["runtime_contract_sha256"] == root["runtime_contract_sha256"], "Session contract mismatch")
    require(p["runtime_contract_integrity"] == contract["integrity"]["sha256"], "Session seal mismatch")
    require(p["packages"] == contract["packages"], "Session package mismatch")
    require(p["constructor"] == contract["constructor"], "Session constructor mismatch")
    require(p["runner_sha256"] == root["code_sha256"]["kaggle_inference.py"], "Runner mismatch")
    require(p["backend_sdist_sha256"] == contract["backend_source"]["sdist_sha256"], "Backend source mismatch")
    require(p["python"].startswith("3.13.") and p["platform"].startswith("Linux-"), "Platform mismatch")
    require(p["n_threads"] == max(p["cpu_count"] // 2, 1)
            and p["n_threads_batch"] == p["cpu_count"], "Thread formula mismatch")
    for field in ("gpu_before_load", "gpu_after_load"):
        rows = [s.split(",") for s in p[field].splitlines() if s.strip()]
        require(len(rows) == 2 and {s[0].strip() for s in rows} == {"0", "1"}
                and all("T4" in s[2] and "GPU-" in s[1] and len(s) == 6 for s in rows),
                "Missing two-T4 UUID/memory/driver evidence")
    pins = {}
    for line in p["pip_freeze"].splitlines():
        if "==" in line:
            k, v = line.split("==", 1)
            pins[re.sub(r"[-_.]+", "-", k).lower()] = v
    for k, v in contract["packages"].items():
        if k != "llama-cpp-python":
            require(pins.get(k) == v, "pip freeze pin mismatch: " + k)
    require("#sha256=" + p["backend_sdist_sha256"] in p["pip_freeze"], "Missing installed archive receipt")
    binaries = p["compiled_backend_sha256"]
    require(binaries and all(re.fullmatch(r"[a-f0-9]{64}", v) for v in binaries.values()),
            "Missing compiled backend hashes")
    for k, v in binaries.items():
        if k.startswith("llama_cpp/"):
            require(binaries.get(k[len("llama_cpp/"):]) == v, "Compiled library alias mismatch")
    log = path.parent / "model_load_offload.log"
    require(sha(log) == p["offload_log_sha256"], "Native log checksum mismatch")
    text = log.read_text(encoding="utf-8")
    delivery.native_log_check(text, contract)
    assigned = re.findall(r"load_tensors: layer\s+(\d+) assigned to device CUDA(\d+)", text)
    require(len(assigned) == 49 and {int(x[0]) for x in assigned} == set(range(49)),
            "Missing/duplicate native layer assignments")
    layer_counts = dict(Counter("CUDA" + device for _, device in assigned))
    require(set(layer_counts) == {"CUDA0", "CUDA1"}, "Model not spread over two GPUs")
    require(re.search(r"flash_attn\s*=\s*0\b", text), "Flash attention mismatch")
    build_logs = [SOURCE / "remote_output/grace_diagnostics/install_llama_cuda.log",
                  RUN / "remote_output/grace_diagnostics/install_llama_cuda.log"]
    matched = [f for f in build_logs if f.is_file() and sha(f) == p["backend_build_log_sha256"]]
    require(len(matched) == 1, "Build log not uniquely matched to provenance")
    build_text = matched[0].read_text(encoding="utf-8", errors="replace")
    require("Using CUDA architectures: 75" in build_text
            and "Successfully built llama" in build_text, "Build success/SM75 not evidenced")
    expected_env = {"CMAKE_ARGS": "-DGGML_CUDA=on -DCMAKE_CUDA_ARCHITECTURES=75 -DCMAKE_LIBRARY_PATH=/usr/local/nvidia/lib64",
                    "CMAKE_BUILD_PARALLEL_LEVEL": "2", "FORCE_CMAKE": "1"}
    require(p["build_environment"] == expected_env, "Build environment mismatch")
    require(all(line.strip() in build_text for line in p["backend_build_report"]), "Build report differs from log")
    for k in ("nvcc", "compiler", "cxx_compiler", "cmake", "libc"):
        require(bool(p[k]), "Missing toolchain provenance: " + k)
    return {"provenance_path": path.relative_to(ROOT).as_posix(), "records": count,
            "provenance_sha256": sha(path), "native_log_sha256": sha(log),
            "build_log_path": matched[0].relative_to(ROOT).as_posix(),
            "build_log_sha256": sha(matched[0]), "layer_assignments": layer_counts,
            "compiled_backend_sha256": binaries, "packages": p["packages"],
            "constructor": p["constructor"], "cpu_count": p["cpu_count"],
            "n_threads": p["n_threads"], "n_threads_batch": p["n_threads_batch"],
            "python": p["python"], "nvcc": p["nvcc"].splitlines()[-2],
            "build_cmake_report": p["backend_build_report"], "postinstall_cmake": p["cmake"].splitlines()[0],
            "verdict": "PASS_APPROVED_PLATFORM_BUILD_POLICY"}


def main():
    require(not OUT.exists(), "Preserve the existing threshold release")
    frozen_before = {p.relative_to(ROOT).as_posix(): sha(p) for p in FROZEN}
    now = datetime.now(timezone.utc).isoformat()
    contract_path = SOURCE / "code/inference_runtime_lock.json"
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    require(canonical_hash({k: v for k, v in contract.items() if k != "integrity"})
            == contract["integrity"]["sha256"], "Contract canonical seal mismatch")
    policies = ("model", "tokenizer", "backend_source", "constructor", "gpu", "threads", "build", "scoring", "resume")
    original_comparison = {}
    for name, old in embedded_contracts().items():
        require(all(old[k] == contract[k] for k in policies), "Original ZIP core policy mismatch: " + name)
        require(all(contract["packages"].get(k) == v for k, v in old["packages"].items()), "Original package changed")
        extra = {k: v for k, v in contract["packages"].items() if k not in old["packages"]}
        require(extra == {"scipy": "1.16.3"}, "Unexpected extra package pin")
        original_comparison[name] = {"core_policies_equal": list(policies), "additional_pin": extra}
    runtime = {"status": "PASS", "checked_at_utc": now, "original_zip_sha256": sha(ZIP),
               "original_zip_comparison": original_comparison,
               "contract_file_sha256": sha(contract_path), "contract_canonical_sha256": contract["integrity"]["sha256"],
               "policy": contract["build"]["policy"], "datasets": {},
               "limitations": ["Backend library hashes are recorded by the pinned worker; remote binary files were not retained for independent rehashing.",
                               "CMake used inside isolated build is 4.4.4; postinstall cmake probe is 3.31.10. Both are recorded; exact toolchain versions are not pinned by the approved policy.",
                               "This certifies the user-approved Kaggle llama-cpp-python contract, not literal execution with the older llama-server b3920 reference."]}
    locks = {}
    summary = json.loads((CANDIDATES / "candidate_summary.json").read_text(encoding="utf-8"))
    for ds, n in (("devign", 2732), ("reveal", 2273)):
        root_path = SOURCE / f"roots/{ds}.json"
        root = json.loads(root_path.read_text(encoding="utf-8"))
        require(root["runtime_contract_sha256"] == sha(contract_path), "Root contract mismatch")
        for name, digest in root["code_sha256"].items():
            require(sha(SOURCE / "code" / name) == digest, "Pinned source mismatch: " + name)
        rows = delivery.validate_bundle(delivery.discover_bundle(SOURCE.parent / "datasets" / ds, root), root)[1]
        require(delivery.checked_records(REMOTE / ds, root, rows) == n == len(rows), "Incomplete validation")
        rec_path = next((REMOTE / ds).rglob("records.jsonl"))
        records = [json.loads(s) for s in rec_path.read_text(encoding="utf-8").splitlines() if s.strip()]
        candidate_path = CANDIDATES / f"{ds}_threshold_candidate.json"
        require(sha(candidate_path) == summary["candidate_files"][ds], "Candidate file changed")
        candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
        require(sha(rec_path) == candidate["identity"]["validation_records_sha256"], "Candidate records changed")
        require(sha(root_path) == candidate["identity"]["input_root_sha256"], "Candidate root changed")
        require(candidate["rules"] == optimizer.RULES and candidate["rules_sha256"] == optimizer.RULES_SHA256,
                "Threshold rule mismatch")
        labels, scores = [r["label"] for r in records], [r["s"] for r in records]
        grid = [mcc_counts(labels, scores, i / 100) for i in range(1, 100)]
        require(grid == candidate["grid"], "Full candidate grid mismatch")
        second = optimizer.pick_threshold(records)
        require(len(second["grid_results"]) == 99, "Incomplete optimizer grid")
        for a, b in zip(grid, second["grid_results"]):
            require(a["threshold"] == b["threshold"] and
                    ((a["mcc"] is None and b["mcc"] is None) or
                     (a["mcc"] is not None and b["mcc"] is not None and abs(a["mcc"]-b["mcc"]) <= 1e-12)),
                    "Independent optimizer grid mismatch")
        require(second["tau"] == candidate["tau_star_candidate"], "Optimizer winner mismatch")
        sessions = Counter(r["runtime_provenance"] for r in records)
        for r in records:
            require(r["token_ids"] == {"0": 15, "1": 16}
                    and r["inference_seed"] == contract["constructor"]["seed"]
                    and r["logprob_distribution"] == "unconstrained_first_token", "Record scoring mismatch")
        runtime["datasets"][ds] = {"records": n, "sessions": [
            audit_session(REMOTE / ds / ref, count, contract, root) for ref, count in sessions.items()]}
        application = {"method_id": root["method_id"], "pool_sha256": root["pool_sha256"],
                       "model_sha256": root["model_sha256"], "tokenizer_revision": root["tokenizer_revision"],
                       "runtime_contract_sha256": root["runtime_contract_sha256"], "scoring": root["scoring"],
                       "worker_sha256": root["code_sha256"]["kaggle_inference.py"]}
        lock = {"schema": "grace_b3_verified_patch_threshold_lock_v1", "release_id": OUT.name,
                "status": "LOCKED", "locked_at_utc": now, "arm": "B3", "method_id": root["method_id"],
                "dataset": ds, "seed": 42, "fit_split": "validation", "n_expected": n, "n_valid": n,
                "tau_star": candidate["tau_star_candidate"], "validation_mcc": candidate["validation_mcc"],
                "application_identity": application, "validation_identity": candidate["identity"],
                "candidate_sha256": sha(candidate_path), "rules_sha256": optimizer.RULES_SHA256,
                "tie_thresholds_within_1e-9": candidate["tie_thresholds_within_1e-9"],
                "classification": "AMENDED_EXPLORATORY_SUBPROTOCOL",
                "governance_record": "governance_record.json",
                "test_data_used_for_selection": False,
                "probe_policy": "B3-flip/B3-swap inherit this B3 threshold; B3-nodiff requires its own validation.",
                "application_requirements": ["Pin raw lock SHA-256 in test delivery.",
                    "Verify canonical seal and application identity before test inference/evaluation.",
                    "Audit and seal fresh test prompts with unchanged pool/selector/renderer/runtime.",
                    "No threshold refit or method changes based on test scores."]}
        locks[ds] = lock
    require(frozen_before == {p.relative_to(ROOT).as_posix(): sha(p) for p in FROZEN}, "Frozen threshold changed")
    # Publish only after every census, grid and referenced runtime session passes.
    OUT.mkdir(parents=True)
    governance = {"schema": "grace_b3_threshold_authority_record_v1", "recorded_at_utc": now,
                  "authority_source": "Direct user instruction in the current Codex conversation",
                  "verbatim_instruction": "vậy thực hiện nốt các yêu cầu để chốt threshold đi, check kỹ runtime xem đã đúng cả chưa nhé",
                  "scope": "Finalize the separate thresholds for completed Devign and REVEAL B3-new seed42 validation, following full-grid review and runtime audit.",
                  "technical_review": "Codex reran both full grids and optimizer comparison, identity/coverage and every score-referenced runtime session.",
                  "human_signatures_created": False, "new_pair_reviews_claimed": False,
                  "osf_amendment_or_preregistration_change_claimed": False,
                  "historical_roots_preserved": True, "classification": "AMENDED_EXPLORATORY_SUBPROTOCOL",
                  "frozen_thresholds_before_and_after": frozen_before}
    write(OUT / "governance_record.json", governance)
    write(OUT / "runtime_acceptance.json", runtime)
    for ds, lock in locks.items():
        lock["governance_record_sha256"] = sha(OUT / "governance_record.json")
        lock["runtime_acceptance_sha256"] = sha(OUT / "runtime_acceptance.json")
        lock["seal_sha256"] = canonical_hash(lock)
        write(OUT / f"{ds}_threshold_lock.json", lock)
        (OUT / f"{ds}_full_grid.json").write_bytes((CANDIDATES / f"{ds}_threshold_candidate.json").read_bytes())
    # Positive readback and meaningful rejection checks on temporary copies only.
    checks = {}
    for ds, lock in locks.items():
        path = OUT / f"{ds}_threshold_lock.json"
        digest = sha(path)
        require(load_threshold(path, digest, ds, lock["application_identity"]) == lock["tau_star"], "Lock readback failure")
        with tempfile.TemporaryDirectory(prefix="b3_lock_gate_") as folder:
            bad = Path(folder) / "bad.json"
            bad.write_bytes(path.read_bytes() + b" ")
            for name, p, h, identity in [
                    ("changed_bytes_rejected", bad, digest, lock["application_identity"]),
                    ("changed_pool_rejected", path, digest, dict(lock["application_identity"], pool_sha256="0"*64)),
                    ("changed_runtime_rejected", path, digest, dict(lock["application_identity"], runtime_contract_sha256="0"*64))]:
                try:
                    load_threshold(p, h, ds, identity)
                except ValueError:
                    checks[ds + ":" + name] = "PASS"
                else:
                    raise AssertionError("Gate accepted invalid input: " + name)
            changed = dict(lock, tau_star=0.5)
            write(bad, changed)
            try:
                load_threshold(bad, sha(bad), ds, lock["application_identity"])
            except ValueError:
                checks[ds + ":changed_payload_seal_rejected"] = "PASS"
            else:
                raise AssertionError("Gate accepted invalid canonical seal")
        checks[ds + ":valid_lock_readback"] = "PASS"
    write(OUT / "verification.json", {"status": "PASS", "checks": checks, "test_data_read": False,
                                       "frozen_thresholds_unchanged": frozen_before == {p.relative_to(ROOT).as_posix(): sha(p) for p in FROZEN}})
    sources = [Path(__file__), ROOT / "scripts/b3_threshold_lock.py"]
    manifest = {"release_id": OUT.name, "status": "LOCKED", "created_at_utc": now,
                "thresholds": {ds: {"tau_star": lock["tau_star"], "path": f"{ds}_threshold_lock.json",
                                    "file_sha256": sha(OUT / f"{ds}_threshold_lock.json")} for ds, lock in locks.items()},
                "files_sha256": {p.name: sha(p) for p in sorted(OUT.iterdir()) if p.is_file()},
                "source_sha256": {p.relative_to(ROOT).as_posix(): sha(p) for p in sources},
                "test_stage": "THRESHOLDS_READY_TEST_DELIVERY_NOT_YET_AUDITED_OR_LAUNCHED"}
    manifest["seal_sha256"] = canonical_hash(manifest)
    write(OUT / "release_manifest.json", manifest)
    (OUT / "release_manifest.sha256").write_text(sha(OUT / "release_manifest.json") + "  release_manifest.json\n", encoding="utf-8")
    print(json.dumps({"release": str(OUT.relative_to(ROOT)), "status": "LOCKED", "thresholds": manifest["thresholds"],
                      "runtime": "PASS", "gate_checks": len(checks), "manifest_sha256": sha(OUT / "release_manifest.json")}, indent=2))


if __name__ == "__main__":
    main()
