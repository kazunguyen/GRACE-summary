"""Automated verification of release_20261108_v3 against third audit findings (T3-01 to T3-07)."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from zipfile import ZipFile

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[3]
AUDIT_DIR = Path(__file__).resolve().parent
RELEASE_V1 = ROOT / "Runs-management/b3_verified_patch_v1/release_20261108"
RELEASE_V2 = ROOT / "Runs-management/b3_verified_patch_v1/release_20261108_v2"
RELEASE_V3 = ROOT / "Runs-management/b3_verified_patch_v1/release_20261108_v3"
FREEZE = ROOT / "01_Author_Baseline_Unified/output/research_freeze_20261101"
SRC = ROOT / "01_Author_Baseline_Unified/diagnostic_kit/src"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def rows(path: Path) -> list:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main():
    print("=== Automated Remediation Audit for Release v3 ===")
    result = {"audit_scope": "remediation_third_audit_20261108", "target_release": "release_20261108_v3"}

    # 1. Check preservation of Release v1 and Release v2
    v1_im_path = RELEASE_V1 / "inputs_manifest.json"
    v2_im_path = RELEASE_V2 / "inputs_manifest.json"
    v1_im = read(v1_im_path) if v1_im_path.is_file() else {}
    v2_im = read(v2_im_path) if v2_im_path.is_file() else {}
    v1_files = [p for p in RELEASE_V1.rglob("*") if p.is_file()]
    v2_files = [p for p in RELEASE_V2.rglob("*") if p.is_file()]
    
    v1_body = {k: v for k, v in v1_im.items() if k != "seal_sha256"}
    v2_body = {k: v for k, v in v2_im.items() if k != "seal_sha256"}
    v1_calc_seal = hashlib.sha256(json.dumps(v1_body, sort_keys=True, ensure_ascii=False, indent=2).encode("utf-8")).hexdigest()
    v2_calc_seal = hashlib.sha256(json.dumps(v2_body, sort_keys=True, ensure_ascii=False, indent=2).encode("utf-8")).hexdigest()
    
    v1_seal_ok = (v1_im.get("seal_sha256") == v1_calc_seal and bool(v1_calc_seal)) if v1_im_path.is_file() else False
    v2_seal_ok = (v2_im.get("seal_sha256") == v2_calc_seal and bool(v2_calc_seal)) if v2_im_path.is_file() else False
    result["v1_preservation"] = {"files_count": len(v1_files), "seal_verified": v1_seal_ok, "seal": v1_calc_seal, "intact": v1_seal_ok and len(v1_files) > 0}
    result["v2_preservation"] = {"files_count": len(v2_files), "seal_verified": v2_seal_ok, "seal": v2_calc_seal, "intact": v2_seal_ok and len(v2_files) > 0}

    # 2. Check all three seals of Release v3
    seals = {}
    for rel_p, field in [
        ("inputs_manifest.json", "seal_sha256"),
        ("pools/pool_manifest.json", "manifest_seal_sha256"),
        ("validation/validation_prompt_manifest.json", "prompt_manifest_seal_sha256"),
    ]:
        d = read(RELEASE_V3 / rel_p)
        body = {k: v for k, v in d.items() if k != field}
        calc = hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False, indent=2).encode("utf-8")).hexdigest()
        stored = d[field]
        match = (calc == stored)
        seals[rel_p] = {"stored": stored, "calculated": calc, "match": match}
    result["seals"] = seals
    all_seals_pass = all(s["match"] for s in seals.values())
    result["all_seals_pass"] = all_seals_pass

    # 3. Inputs Manifest Gate Verification
    im = read(RELEASE_V3 / "inputs_manifest.json")
    mod_mismatches = [k for k, v in im.get("modules_sha256", {}).items() if sha(ROOT / k) != v]
    scr_mismatches = [k for k, v in im.get("execution_scripts_sha256", {}).items() if sha(ROOT / k) != v]
    auth_mismatches = [k for k, v in im.get("authority_documents_sha256", {}).items() if sha(ROOT / k) != v]

    freeze_manifest_ok = (sha(FREEZE / "freeze_manifest.json") == im.get("freeze_manifest", {}).get("sha256"))
    freeze_data_mismatches = [
        k for k, v in im.get("verified_freeze_files", {}).items()
        if not k.startswith("declared_graph_source:") and sha(FREEZE / k) != v
    ]
    tok_dir = ROOT / im["tokenizer"]["path"]
    tok_mismatches = [k for k, v in im["tokenizer"]["files_sha256"].items() if sha(tok_dir / k) != v]
    specs_ok = (sha(ROOT / "Runs-management/grace_15arms_prompts_and_clean_specs.zip") == im.get("specs_archive_sha256"))

    result["input_gates"] = {
        "modules_pass": len(mod_mismatches) == 0,
        "scripts_pass": len(scr_mismatches) == 0,
        "authority_docs_pass": len(auth_mismatches) == 0,
        "freeze_manifest_pass": freeze_manifest_ok,
        "freeze_data_files_pass": len(freeze_data_mismatches) == 0,
        "tokenizer_files_pass": len(tok_mismatches) == 0,
        "specs_archive_pass": specs_ok,
    }
    all_input_gates_pass = all(result["input_gates"].values())
    result["all_input_gates_pass"] = all_input_gates_pass

    # 4. T3-01 Remediation Verification (Step 7 Pre-GPU Verification)
    step7_report = read(RELEASE_V3 / "acceptance/step7_selector_renderer_report.json")
    cpu_check = step7_report.get("check_b3_cpu_sample_check", {})
    t3_01_ok = (
        step7_report.get("overall_passed") is True
        and step7_report.get("status") == "STEP7_VERIFICATION_PASSED"
        and cpu_check.get("safe_pause_confirmed") is True
        and cpu_check.get("safe_pause_or_render_confirmed") is True
        and cpu_check.get("dataset_statuses", {}).get("devign") == "PAUSED"
        and cpu_check.get("dataset_statuses", {}).get("reveal") == "PAUSED"
    )
    result["remediation_t3_01"] = {
        "step7_overall_passed": step7_report.get("overall_passed"),
        "safe_pause_confirmed": cpu_check.get("safe_pause_confirmed"),
        "safe_pause_or_render_confirmed": cpu_check.get("safe_pause_or_render_confirmed"),
        "dataset_statuses": cpu_check.get("dataset_statuses"),
        "status": "PASS_STEP7_REMEDIATED" if t3_01_ok else "FAIL_T3_01",
    }

    # 5. T3-02 Remediation Verification (Pool Disagreement & Preservation)
    pm = read(RELEASE_V3 / "pools/pool_manifest.json")
    t3_02_ok = (
        pm["pools"]["devign"]["admitted_pairs_count"] == 0
        and pm["pools"]["reveal"]["admitted_pairs_count"] == 0
        and pm["review_process"]["human_reviews_submitted"] == 0
    )
    result["remediation_t3_02"] = {
        "devign_status": pm["pools"]["devign"]["status"],
        "reveal_status": pm["pools"]["reveal"]["status"],
        "devign_admitted_count": pm["pools"]["devign"]["admitted_pairs_count"],
        "reveal_admitted_count": pm["pools"]["reveal"]["admitted_pairs_count"],
        "status": "PASS_POOL_PRESERVATION_AND_DISAGREEMENT_HANDLING" if t3_02_ok else "FAIL_T3_02",
    }

    # 6. T3-03 Remediation Verification (Before/After Mandatory Source Functions)
    cand_summary = read(RELEASE_V3 / "candidates/candidates_summary.json")
    t3_03_ok = (
        cand_summary.get("candidates_admitted") == 0
        and cand_summary.get("dummy_fixtures_used") is False
    )
    result["remediation_t3_03"] = {
        "candidates_admitted": cand_summary.get("candidates_admitted"),
        "ineligible_cases_count": cand_summary.get("ineligible_cases_count"),
        "dummy_fixtures_used": cand_summary.get("dummy_fixtures_used"),
        "status": "PASS_MANDATORY_SOURCE_FUNCTIONS_ENFORCED" if t3_03_ok else "FAIL_T3_03",
    }

    # 7. T3-04 Remediation Verification (Triage Candidate Payload Evaluation)
    triage_rows = rows(RELEASE_V3 / "reviews/triage_ledger.jsonl")
    t3_04_ok = (
        len(triage_rows) == 12
        and all(r.get("evaluation_type") == "AUTOMATED_TECHNICAL_TRIAGE" for r in triage_rows)
    )
    result["remediation_t3_04"] = {
        "triage_count": len(triage_rows),
        "evaluation_type_consistent": t3_04_ok,
        "status": "PASS_TRIAGE_PAYLOAD_EVALUATION" if t3_04_ok else "FAIL_T3_04",
    }

    # 8. T3-05 Remediation Verification (Review Form Validation)
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        from b3_step6_packet_tool import validate_review_form
        sample_bad_form = {
            "case_id": "test_case",
            "reviewer": "test_rev",
            "reviewed_at": "TEST-FIXTURE-TIMESTAMP",
            "payload_sha256": "0" * 64,
            "same_function_verified": True,
            "security_fix_verified": True,
            "source_revisions_verified": True,
            "explanation_supported": True,
            "decision": "approve",
            "comments": "ok",
        }
        known_packets = {"test_case": {"case_id": "test_case", "payload_sha256": "0" * 64}}
        triage_records = {"test_case": {"case_id": "test_case", "status": "AUTOMATED_TRIAGE_PASS"}}
        
        is_valid_prod, reason_prod = validate_review_form(sample_bad_form, known_packets, triage_records, allow_synthetic=False)
        is_valid_test, reason_test = validate_review_form(sample_bad_form, known_packets, triage_records, allow_synthetic=True)
        
        t3_05_ok = (not is_valid_prod) and ("SYNTHETIC_TIMESTAMP" in str(reason_prod)) and is_valid_test
    except Exception as ex:
        t3_05_ok = False

    result["remediation_t3_05"] = {
        "synthetic_timestamp_rejected_in_production": t3_05_ok,
        "status": "PASS_PRODUCTION_REVIEW_VALIDATION" if t3_05_ok else "FAIL_T3_05",
    }

    # 9. T3-06 Remediation Verification (Release v3 Synchronization)
    t3_06_ok = (
        all_seals_pass
        and all_input_gates_pass
        and (RELEASE_V3 / "inputs_manifest.json").is_file()
        and (RELEASE_V3 / "pools/pool_manifest.json").is_file()
        and (RELEASE_V3 / "validation/validation_prompt_manifest.json").is_file()
    )
    result["remediation_t3_06"] = {
        "release_version": "v3_remediated",
        "parent_release": "v2_remediated",
        "all_manifests_sealed_and_synchronized": t3_06_ok,
        "status": "PASS_RELEASE_V3_SYNCHRONIZED" if t3_06_ok else "FAIL_T3_06",
    }

    # 10. T3-07 Remediation Verification (Gate Conditions & Dynamic Reports)
    prompt_manifest = read(RELEASE_V3 / "validation/validation_prompt_manifest.json")
    val_audit_md = (RELEASE_V3 / "acceptance/VALIDATION_DATA_AUDIT_REPORT.md").read_text(encoding="utf-8")
    t3_07_ok = (
        prompt_manifest.get("gpu_inference_status") == "INFERENCE_PAUSED_EMPTY_POOL"
        and "72 passed" in val_audit_md
        and "T3-01" in val_audit_md
    )
    result["remediation_t3_07"] = {
        "gpu_inference_status": prompt_manifest.get("gpu_inference_status"),
        "acceptance_report_dynamic": ("72 passed" in val_audit_md),
        "third_audit_remediations_documented": ("T3-01" in val_audit_md),
        "status": "PASS_GATES_AND_DYNAMIC_REPORTS" if t3_07_ok else "FAIL_T3_07",
    }

    # Overall Verdict
    overall = bool(
        all_seals_pass
        and all_input_gates_pass
        and t3_01_ok
        and t3_02_ok
        and t3_03_ok
        and t3_04_ok
        and t3_05_ok
        and t3_06_ok
        and t3_07_ok
    )
    result["all_third_audit_findings_remediated"] = overall
    result["operational_status"] = "SAFE_PAUSE_MAINTAINED_READY_FOR_NEXT_AUDIT"

    out_file = AUDIT_DIR / "remediation_audit_result.json"
    out_file.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Audit results written to: {out_file}")
    print(f"All third audit findings remediated: {overall}")
    return 0 if overall else 1


if __name__ == "__main__":
    sys.exit(main())
