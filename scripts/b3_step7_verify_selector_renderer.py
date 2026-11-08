#!/usr/bin/env python3
"""Step 7: Verify selector, renderer, token budgets, and edge cases.

Executes test suites and verifies:
1. VerifiedPairSelector with empty pool correctly pauses with ValueError
2. Target interface safety (rejects target label leakage)
3. TokenCounter with pinned tokenizer
4. Context budgets: target <= 3000, graph <= 1500, demo <= 1500, reserve 64, total <= 8192
5. Test suites execution and report generation

Addresses audit finding F06:
- Synthetic fixtures use SYNTHETIC-TEST-REVIEWER-* names (no real reviewer names in fixtures)
- Fail-closed gate logic: figure6_order_verified strictly participates in passed determination
- Status is only STEP7_VERIFICATION_PASSED if all tests, edge cases, and CPU checks pass
"""

import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RELEASE_DIR = ROOT / "Runs-management" / "b3_verified_patch_v1" / "release_20261108_v3"
SRC = ROOT / "01_Author_Baseline_Unified" / "diagnostic_kit" / "src"
sys.path.insert(0, str(SRC))

from grace_diag.amended_b3 import (
    VerifiedPairSelector,
    changed_lines,
    difference_from_source,
    digest,
    function_hint,
    make_pair_candidate,
    patch_text,
    payload_hash,
    validate_pair,
)
from grace_diag.token_budget import TokenCounter

TOKENIZER_DIR = (
    ROOT
    / "11_Arm_B1H2_Evidence"
    / "tokenizer_cache_v6"
    / "models--Qwen--Qwen3-Coder-30B-A3B-Instruct"
    / "snapshots"
    / "b2cff646eb4bb1d68355c01b18ae02e7cf42d120"
)


def run_step7(release_dir: Path = DEFAULT_RELEASE_DIR):
    print(f"=== Step 7: Selector and Renderer Pre-GPU Verification (Target: {release_dir.name}) ===")
    acceptance_dir = release_dir / "acceptance"
    acceptance_dir.mkdir(parents=True, exist_ok=True)

    # 1. Run the 4 Pytest Suites
    test_suites = [
        "tests/test_amended_b3.py",
        "tests/test_preregistration_integrity.py",
        "01_Author_Baseline_Unified/diagnostic_kit/tests/test_probes.py",
        "01_Author_Baseline_Unified/diagnostic_kit/tests/test_stats_and_complementarity.py",
    ]

    pytest_results = {}
    for suite in test_suites:
        print(f"Running pytest on {suite}...")
        res = subprocess.run(
            [sys.executable, "-m", "pytest", suite, "-q"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        stdout_txt = (res.stdout or "").strip()
        stderr_txt = (res.stderr or "").strip()
        print(f"Result for {suite}: returncode={res.returncode}")
        print(f"Stdout:\n{stdout_txt}")
        if res.returncode != 0:
            print(f"Stderr:\n{stderr_txt}")
        pytest_results[suite] = {
            "returncode": res.returncode,
            "stdout": stdout_txt,
            "passed": (res.returncode == 0),
        }

    # 2. Verify Edge Cases Directly on VerifiedPairSelector
    edge_cases = {}

    # Case A: Empty pool pause
    try:
        VerifiedPairSelector([], {}, "devign")
        edge_cases["empty_pool_pause"] = {"passed": False, "error": "Did not raise ValueError"}
    except ValueError as exc:
        expected_msg = "No verified pair pool: B3 must pause"
        edge_cases["empty_pool_pause"] = {
            "passed": str(exc) == expected_msg,
            "observed_message": str(exc),
            "expected_message": expected_msg,
        }

    # Case B: Tokenizer exactness requirement
    counter = TokenCounter(str(TOKENIZER_DIR))
    print(f"Loaded exact tokenizer from {TOKENIZER_DIR}. Approx flag: {counter.approx}")
    edge_cases["tokenizer_exactness"] = {
        "passed": counter.approx is False,
        "approx_flag": counter.approx,
        "revision": "b2cff646eb4bb1d68355c01b18ae02e7cf42d120",
    }

    # Case C: Target interface label leakage guard
    # Construct a synthetic pair for interface guard testing (named SYNTHETIC-TEST-REVIEWER-*)
    before = "int foo(char *dst, const char *src, unsigned n) {\n    memcpy(dst, src, n);\n    return 0;\n}\n"
    after = "int foo(char *dst, const char *src, unsigned n) {\n    if (n > 16) return -1;\n    memcpy(dst, src, n);\n    return 0;\n}\n"
    v_uid = "synth:v"
    p_uid = "synth:p"
    synth_bank = {
        v_uid: {"id": v_uid, "function_uid": v_uid, "dataset": "devign", "split": "train", "target": 1, "func": before},
        p_uid: {"id": p_uid, "function_uid": p_uid, "dataset": "devign", "split": "train", "target": 0, "func": after},
    }
    diff_text = patch_text(before, after)
    fix_diff_text = diff_text.replace("--- vulnerable", "--- a/foo.c").replace("+++ patched", "+++ b/foo.c")
    synth_source = {
        "repository": "test/test", "path": "foo.c", "function": "foo",
        "fix_commit": "1" * 40, "parent_commit": "0" * 40,
        "source_url": "https://example.com/fix", "security_rationale": "Add bounds check on n",
        "before": before, "after": after,
        "diff": diff_text,
        "fix_diff": fix_diff_text,
    }
    synth_pair = {
        "dataset": "devign", "pair_id": "synth_pair_01",
        "vulnerable_id": v_uid, "patched_id": p_uid,
        "test_fixture": True,
        "inference_allowed": False,
        "before_sha256": digest(before), "after_sha256": digest(after),
        "source": synth_source,
        "changed_lines": changed_lines(before, after),
        "key_difference": difference_from_source(synth_source),
    }
    p_hash = payload_hash(synth_pair)
    synth_pair["reviews"] = [
        {"reviewer": "SYNTHETIC-TEST-REVIEWER-1", "reviewed_at": "2026-11-08T00:00:00Z", "decision": "approve", "payload_sha256": p_hash,
         "same_function_verified": True, "security_fix_verified": True, "source_revisions_verified": True, "explanation_supported": True},
        {"reviewer": "SYNTHETIC-TEST-REVIEWER-2", "reviewed_at": "2026-11-08T00:00:00Z", "decision": "approve", "payload_sha256": p_hash,
         "same_function_verified": True, "security_fix_verified": True, "source_revisions_verified": True, "explanation_supported": True},
    ]

    synth_selector = VerifiedPairSelector([synth_pair], synth_bank, "devign")

    # Target with forbidden key (target label leakage attempt)
    leaky_target = {
        "id": "devign:val:1",
        "query_code": "int bar() { return 0; }",
        "nodes": "",
        "edges": "",
        "target": 1,  # Forbidden key!
    }
    try:
        synth_selector.render_family(leaky_target, counter)
        edge_cases["target_label_leakage_guard"] = {"passed": False, "error": "Did not reject target with label"}
    except ValueError as exc:
        expected_substr = "Target accepts only ID, code and graph, never labels/demo hints"
        edge_cases["target_label_leakage_guard"] = {
            "passed": expected_substr in str(exc),
            "observed_message": str(exc),
        }

    # Valid target interface check with strict Figure 6 ordering participation
    clean_target = {
        "id": "devign:val:1",
        "query_code": "int bar(int y) { return foo(y); }",
        "nodes": [{"id": 0, "label": "bar"}],
        "edges": [],
    }
    rendered_family = synth_selector.render_family(clean_target, counter)
    arms_rendered_ok = all(arm in rendered_family for arm in ("B3", "B3-nodiff", "B3-swap", "B3-flip"))
    figure6_order_ok = all(
        r["evidence"].get("order") == ["role", "code", "question", "graph", "demonstration", "answer"]
        and r["prompt"].find("You are now an excellent programmer") < r["prompt"].find(clean_target["query_code"])
        for r in rendered_family.values()
    )
    edge_cases["clean_target_render"] = {
        "passed": bool(arms_rendered_ok and figure6_order_ok),
        "arms_rendered": list(rendered_family.keys()),
        "figure6_order_verified": figure6_order_ok,
    }

    # 3. Run check_b3.py Real-Data Sample Check
    cpu_check_out = acceptance_dir / "cpu_sample_check"
    if cpu_check_out.exists():
        import shutil
        shutil.rmtree(cpu_check_out)

    check_b3_script = ROOT / "Runs-management" / "b3_amended_20261106" / "check_b3.py"
    pools_dir = release_dir / "pools"
    devign_pool_file = pools_dir / "eligible_pairs.devign.jsonl"
    reveal_pool_file = pools_dir / "eligible_pairs.reveal.jsonl"
    print(f"Running check_b3.py CPU sample check against pools in: {pools_dir}...")
    check_res = subprocess.run(
        [
            sys.executable,
            str(check_b3_script),
            "--pairs", str(pools_dir),
            "--tokenizer", str(TOKENIZER_DIR),
            "--samples", "3",
            "--out", str(cpu_check_out),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    print(f"check_b3.py returncode: {check_res.returncode}")
    check_report_file = cpu_check_out / "report.json"
    safe_pause_or_render_confirmed = False
    dataset_statuses = {}
    if check_report_file.is_file():
        try:
            check_report = json.loads(check_report_file.read_text(encoding="utf-8"))
            dataset_statuses = {ds: d.get("status") for ds, d in check_report.get("datasets", {}).items()}

            pool_manifest_file = pools_dir / "pool_manifest.json"
            pm_data = {}
            if pool_manifest_file.is_file():
                try:
                    pm_data = json.loads(pool_manifest_file.read_text(encoding="utf-8"))
                except Exception:
                    pass

            devign_pm_status = pm_data.get("pools", {}).get("devign", {}).get("status")
            reveal_pm_status = pm_data.get("pools", {}).get("reveal", {}).get("status")

            devign_has_pairs = devign_pool_file.is_file() and devign_pool_file.stat().st_size > 0
            reveal_has_pairs = reveal_pool_file.is_file() and reveal_pool_file.stat().st_size > 0

            devign_active = (devign_pm_status == "ACTIVE_VERIFIED_POOL" if devign_pm_status else devign_has_pairs) and devign_has_pairs
            reveal_active = (reveal_pm_status == "ACTIVE_VERIFIED_POOL" if reveal_pm_status else reveal_has_pairs) and reveal_has_pairs

            devign_exp_status = "PROMPT_AUDIT_REQUIRED" if devign_active else "PAUSED"
            reveal_exp_status = "PROMPT_AUDIT_REQUIRED" if reveal_active else "PAUSED"

            status_ok = (
                dataset_statuses.get("devign") == devign_exp_status
                and dataset_statuses.get("reveal") == reveal_exp_status
            )
            safe_pause_or_render_confirmed = (
                check_report.get("inference_performed") is False
                and check_report.get("thresholds_changed") is False
                and check_report.get("test_inputs_read") is False
                and status_ok
            )
        except Exception:
            pass

    check_b3_passed = (check_res.returncode == 0) and check_report_file.is_file() and safe_pause_or_render_confirmed

    # Fail-closed gate logic (finding F06)
    all_pytest_passed = all(r["passed"] for r in pytest_results.values())
    all_edge_cases_passed = all(e["passed"] for e in edge_cases.values())
    overall_passed = bool(all_pytest_passed and all_edge_cases_passed and check_b3_passed)
    im_path = release_dir / "inputs_manifest.json"
    im_data = {}
    if im_path.is_file():
        try:
            im_data = json.loads(im_path.read_text(encoding="utf-8"))
        except Exception:
            im_data = {}

    gate_status = "STEP7_VERIFICATION_PASSED" if overall_passed else "STEP7_VERIFICATION_FAILED"
    report = {
        "release_target": release_dir.name,
        "release_version": im_data.get("release_version"),
        "inputs_manifest_seal": im_data.get("seal_sha256"),
        "pytest_suites": pytest_results,
        "all_pytest_passed": all_pytest_passed,
        "edge_cases": edge_cases,
        "all_edge_cases_passed": all_edge_cases_passed,
        "check_b3_cpu_sample_check": {
            "passed": check_b3_passed,
            "returncode": check_res.returncode,
            "output_folder": cpu_check_out.relative_to(release_dir).as_posix(),
            "report_file_exists": check_report_file.is_file(),
            "safe_pause_confirmed": safe_pause_or_render_confirmed,
            "safe_pause_or_render_confirmed": safe_pause_or_render_confirmed,
            "dataset_statuses": dataset_statuses,
            "stdout": check_res.stdout.strip(),
        },
        "overall_passed": overall_passed,
        "status": gate_status,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }

    with open(acceptance_dir / "step7_selector_renderer_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"Step 7 Complete! Status: {gate_status}")
    print(json.dumps(report, indent=2))

    if not overall_passed:
        raise RuntimeError(f"Step 7 pre-GPU verification failed: {report}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Step 7: Selector and renderer verification")
    parser.add_argument("--release-dir", type=Path, default=DEFAULT_RELEASE_DIR, help="Output release directory")
    args = parser.parse_args()
    run_step7(args.release_dir)
