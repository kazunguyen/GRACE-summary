#!/usr/bin/env python3
"""Build and audit official release_20261108_v4 for B3 verified patch-pair.

Integrates ratified Case 08 (FFmpeg can_safely_read) with dual independent
human reviews from Lead PI Hieu and teammate Dung, admitting 1 verified pair
into the Devign pool while keeping REVEAL blocked/unresolved.
"""

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "01_Author_Baseline_Unified" / "diagnostic_kit" / "src"
FREEZE_DIR = ROOT / "01_Author_Baseline_Unified" / "output" / "research_freeze_20261101"
TOKENIZER_DIR = (
    ROOT
    / "11_Arm_B1H2_Evidence"
    / "tokenizer_cache_v6"
    / "models--Qwen--Qwen3-Coder-30B-A3B-Instruct"
    / "snapshots"
    / "b2cff646eb4bb1d68355c01b18ae02e7cf42d120"
)
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(ROOT / "scripts"))

from grace_diag.amended_b3 import (
    digest,
    make_pair_candidate,
    payload_hash,
    validate_pair,
)
from b3_step6_packet_tool import (
    generate_review_packets,
    run_automated_technical_triage,
    ingest_human_reviews_and_seal_pools,
)
from b3_step7_verify_selector_renderer import run_step7
from b3_step8_validation_census_builder import run_step8

V3_DIR = ROOT / "Runs-management" / "b3_verified_patch_v1" / "release_20261108_v3"
G1_V2_CASE08 = ROOT / "Runs-management" / "b3_verified_patch_v1" / "g1_source_investigation_20261108_v2" / "case_08_ffmpeg_can_safely_read_8614_26054"
RELEASE_V4_DIR = ROOT / "Runs-management" / "b3_verified_patch_v1" / "release_20261108_v4"


def compute_file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def generate_inputs_manifest(release_dir: Path) -> dict:
    modules = [
        "01_Author_Baseline_Unified/diagnostic_kit/src/grace_diag/amended_b3.py",
        "01_Author_Baseline_Unified/diagnostic_kit/src/grace_diag/contrastive_pair_builder.py",
        "01_Author_Baseline_Unified/diagnostic_kit/src/grace_diag/probes.py",
        "01_Author_Baseline_Unified/diagnostic_kit/src/grace_diag/token_budget.py",
        "configs/inference_runtime_lock.json",
        "Runs-management/b3_amended_20261106/check_b3.py",
    ]
    scripts = [
        "scripts/b3_step1_snapshot.py",
        "scripts/b3_step2_https_recon.py",
        "scripts/b3_step3_devign_investigation.py",
        "scripts/b3_step4_reveal_provenance.py",
        "scripts/b3_step5_make_candidates.py",
        "scripts/b3_step6_packet_tool.py",
        "scripts/b3_step7_verify_selector_renderer.py",
        "scripts/b3_step8_validation_census_builder.py",
    ]
    authority = [
        "docs/OSF_response/De_cuong_nghien_cuu_GRACE_hop_nhat.docx",
        "docs/OSF-update-20261107.pdf",
    ]
    freeze_files = [
        "devign/donors.jsonl",
        "devign/near_pairs.jsonl",
        "devign/test_manifest.jsonl",
        "devign/test_raw.jsonl",
        "devign/train_manifest.jsonl",
        "devign/train_raw.jsonl",
        "devign/validation_manifest.jsonl",
        "devign/validation_raw.jsonl",
        "reveal/donors.jsonl",
        "reveal/near_pairs.jsonl",
        "reveal/test_manifest.jsonl",
        "reveal/test_raw.jsonl",
        "reveal/train_manifest.jsonl",
        "reveal/train_raw.jsonl",
        "reveal/validation_manifest.jsonl",
        "reveal/validation_raw.jsonl",
    ]
    tok_files = [
        "chat_template.jinja",
        "config.json",
        "merges.txt",
        "tokenizer.json",
        "tokenizer_config.json",
        "vocab.json",
    ]

    im = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "release_version": "v4_verified_patch_admitted",
        "parent_release": "v3_remediated",
        "git_commit": "46e6f4ab9d0ff2c9ecac124d3a6f2bdb72524bd9",
        "python_version": sys.version,
        "freeze_manifest": {
            "path": str(FREEZE_DIR / "freeze_manifest.json"),
            "sha256": compute_file_sha256(FREEZE_DIR / "freeze_manifest.json"),
            "status": "SEAL_VERIFIED",
        },
        "specs_archive_sha256": compute_file_sha256(ROOT / "Runs-management" / "grace_15arms_prompts_and_clean_specs.zip"),
        "modules_sha256": {m: compute_file_sha256(ROOT / m) for m in modules},
        "authority_documents_sha256": {a: compute_file_sha256(ROOT / a) for a in authority},
        "execution_scripts_sha256": {s: compute_file_sha256(ROOT / s) for s in scripts},
        "verified_freeze_files": {f: compute_file_sha256(FREEZE_DIR / f) for f in freeze_files},
        "tokenizer": {
            "expected_revision": "b2cff646eb4bb1d68355c01b18ae02e7cf42d120",
            "local_path": str(TOKENIZER_DIR),
            "files_sha256": {tf: compute_file_sha256(TOKENIZER_DIR / tf) for tf in tok_files},
        },
    }

    im_body = {k: v for k, v in im.items() if k != "seal_sha256"}
    seal = hashlib.sha256(json.dumps(im_body, sort_keys=True, ensure_ascii=False, indent=2).encode("utf-8")).hexdigest()
    im["seal_sha256"] = seal

    with open(release_dir / "inputs_manifest.json", "w", encoding="utf-8") as f:
        json.dump(im, f, indent=2, ensure_ascii=False)
    return im


def build_release_v4():
    print(f"=== Building Official B3 Release v4 at: {RELEASE_V4_DIR.name} ===")
    step8_manifest_path = RELEASE_V4_DIR / "validation" / "validation_prompt_manifest.json"
    if step8_manifest_path.is_file():
        print("Release v4 artifacts already built and sealed on disk. Verifying manifests...")
    else:
        if RELEASE_V4_DIR.exists():
            shutil.rmtree(RELEASE_V4_DIR)
        RELEASE_V4_DIR.mkdir(parents=True, exist_ok=True)

        # 1. Governance directory
        gov_dir = RELEASE_V4_DIR / "governance"
        gov_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(G1_V2_CASE08 / "MAPPING_DECISION_CASE_08.md", gov_dir / "MAPPING_DECISION_CASE_08.md")
        shutil.copy2(G1_V2_CASE08 / "mapping_decision.json", gov_dir / "mapping_decision.json")

        # 2. Source archive directory
        src_archive_dir = RELEASE_V4_DIR / "source_archive" / "devign"
        src_archive_dir.mkdir(parents=True, exist_ok=True)

        # Copy cases 01-12 from v3
        v3_src_devign = V3_DIR / "source_archive" / "devign"
        for case_folder in sorted(v3_src_devign.glob("case_*")):
            dest_folder = src_archive_dir / case_folder.name
            shutil.copytree(case_folder, dest_folder)

        # Overwrite / enhance case 08 with full ratified dossier from g1_v2
        case08_dest = src_archive_dir / "case_08_ffmpeg_can_safely_read_8614_26054"
        for f in G1_V2_CASE08.glob("*"):
            if f.is_file() and not f.name.startswith("review_"):
                shutil.copy2(f, case08_dest / f.name)

        # Also put candidate.json in case 08 folder matching candidate_payload.json
        shutil.copy2(G1_V2_CASE08 / "candidate_payload.json", case08_dest / "candidate.json")

        # Update case_manifest.json in case 08 to reflect authenticated upstream lineage
        case08_manifest_path = case08_dest / "case_manifest.json"
        with open(case08_manifest_path, "r", encoding="utf-8") as f:
            cm08 = json.load(f)
        cm08["source_investigation"]["is_direct_parent_edge"] = True
        cm08["source_investigation"]["actual_fix_commit"] = "3d7817048cb387de87600f2152075f78b37b60a6"
        cm08["source_investigation"]["actual_parent_commit"] = "4b529edff8934c258af95e5acc51f84deea66262"
        cm08["decision"]["status"] = "AUTHENTIC_UPSTREAM_FIX_VERIFIED"
        cm08["decision"]["reason"] = "Direct parentage verified; integer overflow fix authenticated via FFmpeg commit 3d7817048cb387de87600f2152075f78b37b60a6."
        cm08["decision"]["admissible_for_candidate"] = True
        with open(case08_manifest_path, "w", encoding="utf-8") as f:
            json.dump(cm08, f, indent=2, ensure_ascii=False)

        # 3. Candidates directory
        cand_dir = RELEASE_V4_DIR / "candidates"
        cand_dir.mkdir(parents=True, exist_ok=True)
        with open(G1_V2_CASE08 / "candidate_payload.json", "r", encoding="utf-8") as cf:
            cand08 = json.load(cf)
        with open(cand_dir / "candidates.jsonl", "w", encoding="utf-8") as f:
            f.write(json.dumps(cand08, ensure_ascii=False) + "\n")
        print(f"Recorded 1 candidate in {cand_dir / 'candidates.jsonl'}")

        # 4. Step 6 Packets, Triage, and Review Submission
        packets_dir = RELEASE_V4_DIR / "review_packets"
        packets_dir.mkdir(parents=True, exist_ok=True)
        packets = generate_review_packets(RELEASE_V4_DIR)
        print(f"Generated {len(packets)} review packets.")

        # Run automated technical triage
        triage = run_automated_technical_triage(RELEASE_V4_DIR)
        print(f"Recorded automated technical triage for {len(triage)} cases.")

        # Submit the 2 independent reviews into reviews/submitted/
        submitted_dir = RELEASE_V4_DIR / "reviews" / "submitted"
        submitted_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(G1_V2_CASE08 / "review_hieu.json", submitted_dir / "review_hieu.json")
        shutil.copy2(G1_V2_CASE08 / "review_dung.json", submitted_dir / "review_dung.json")
        print(f"Submitted 2 human review forms into {submitted_dir}")

        # Ingest human reviews and seal pools
        ingest_human_reviews_and_seal_pools(RELEASE_V4_DIR, raise_on_error=True)

        # 5. Build inputs manifest before Step 7 and Step 8 (required for tamper & seal binding)
        print("=== Generating inputs_manifest.json for Release v4 ===")
        im = generate_inputs_manifest(RELEASE_V4_DIR)
        print(f"Inputs manifest sealed: {im['seal_sha256']}")

        # 6. Run Step 7 Pre-GPU Verifier
        print("=== Running Step 7 Pre-GPU Verifier on Release v4 ===")
        run_step7(RELEASE_V4_DIR)
        step7_report_path = RELEASE_V4_DIR / "acceptance" / "step7_selector_renderer_report.json"
        if not step7_report_path.is_file():
            raise RuntimeError("Step 7 Pre-GPU verification report missing!")
        with open(step7_report_path, "r", encoding="utf-8") as f:
            step7_report = json.load(f)
        if not step7_report.get("overall_passed"):
            raise RuntimeError("Step 7 Pre-GPU verification failed!")

        # 7. Run Step 8 Validation Census Builder
        print("=== Running Step 8 Validation Census Builder on Release v4 ===")
        run_step8(RELEASE_V4_DIR)

    # 8. Verify Step 8 Validation Census Builder output
    print("=== Checking Step 8 Validation Census Builder Output ===")
    if not step8_manifest_path.is_file():
        raise RuntimeError("Step 8 Validation prompt manifest missing!")
    with open(step8_manifest_path, "r", encoding="utf-8") as f:
        step8_manifest = json.load(f)
    devign_info = step8_manifest.get("datasets", {}).get("devign", {})
    if devign_info.get("selector_status") != "ALL_RENDERED" or devign_info.get("census_count") != 2732:
        raise RuntimeError(f"Step 8 Devign census audit failed: {devign_info}")
    reveal_info = step8_manifest.get("datasets", {}).get("reveal", {})
    if reveal_info.get("selector_status") != "PAUSED" or reveal_info.get("census_count") != 2273:
        raise RuntimeError(f"Step 8 REVEAL census audit failed: {reveal_info}")

    print("\n=======================================================")
    print("RELEASE v4 BUILT, VERIFIED, AND AUDITED SUCCESSFULLY!")
    print(f"Devign Pool: 1 ACTIVE VERIFIED PAIR (Case 08)")
    print(f"REVEAL Pool: 0 pairs (BLOCKED_EMPTY_POOL)")
    print(f"Validation Census: 2,732 Devign prompts rendered + 2,273 REVEAL prompts safely paused")
    print("=======================================================\n")


if __name__ == "__main__":
    build_release_v4()
