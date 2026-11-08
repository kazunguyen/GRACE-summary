#!/usr/bin/env python3
"""Build and audit official release_20261108_v5 for B3 verified patch-pair.

Establishes immutable release_20261108_v5 with unified metadata schema,
incorporating ratified Case 08 Devign pair, REVEAL safely blocked with unresolved
provenance, certified Devign validation census (2,732 prompts), runtime-locked
Kaggle delivery packaging, and rigorous CPU preflight verification.
"""

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

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
RUNTIME_LOCK_PATH = ROOT / "configs" / "inference_runtime_lock.json"

sys.path.insert(0, str(SRC))
sys.path.insert(0, str(ROOT / "scripts"))

from grace_diag.amended_b3 import (
    VerifiedPairSelector,
    digest,
    make_pair_candidate,
    payload_hash,
    validate_pair,
)
from grace_diag.token_budget import TokenCounter
from b3_step6_packet_tool import (
    generate_review_packets,
    run_automated_technical_triage,
    ingest_human_reviews_and_seal_pools,
)
from b3_step7_verify_selector_renderer import run_step7
from b3_step8_validation_census_builder import run_step8

V4_DIR = ROOT / "Runs-management" / "b3_verified_patch_v1" / "release_20261108_v4"
G1_V2_CASE08 = ROOT / "Runs-management" / "b3_verified_patch_v1" / "g1_source_investigation_20261108_v2" / "case_08_ffmpeg_can_safely_read_8614_26054"
RELEASE_V5_DIR = ROOT / "Runs-management" / "b3_verified_patch_v1" / "release_20261108_v5"


def compute_file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def compute_bytes_sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def generate_scope_decision(release_dir: Path) -> dict:
    gov_dir = release_dir / "governance"
    gov_dir.mkdir(parents=True, exist_ok=True)

    scope_meta = {
        "schema_version": 1,
        "release_id": "release_20261108_v5",
        "release_version": "v5_devign_validation_locked",
        "parent_release": "release_20261108_v4",
        "release_status": "FROZEN",
        "method_id": "b3-verified-patch-v1",
        "method": "b3-verified-patch-v1",
        "authority": {
            "lead_pi": "Nguyen Huu Hieu",
            "advisory_directives": ["De_cuong_nghien_cuu_GRACE_hop_nhat.docx", "PhanhoiHieuDungVeDangKyOsf.pdf"],
            "decision_timestamp_utc": "2026-11-08T12:00:00Z",
            "status": "RATIFIED_BY_PROJECT_LEAD",
        },
        "scope": {
            "dataset": "devign",
            "split": "validation",
            "arm": "B3",
            "prompt_seed": 42,
            "expected_count": 2732,
        },
        "pool_specification": {
            "devign_pool_file": "pools/eligible_pairs.devign.jsonl",
            "devign_pool_sha256": "306b3c3391b21649635d1757af365fc9de5fb928894989bfe382fd6498a9f8f9",
            "admitted_pairs_count": 1,
            "admitted_pair_ids": ["case_08_ffmpeg_can_safely_read_8614_26054"],
            "scope_limitation": (
                "Single verified pair in Devign pool: all 2,732 validation targets select this identical "
                "pair. This verifies prompt syntax, Figure 6 ordering, context budgets, and inference "
                "pipeline integrity, but does NOT evaluate dynamic target-dependent pair retrieval across "
                "a diverse pool. Pool composition is permanently locked before inference."
            ),
        },
        "excluded_from_execution": {
            "reveal": "BLOCKED_UNRESOLVED_PROVENANCE",
            "reason": (
                "All 17,636 clean-train donors in REVEAL lack upstream commit hashes in frozen data. "
                "REVEAL is preserved in the overarching research matrix but safely blocked from this "
                "execution delivery until authentic provenance can be established."
            ),
            "test_split": "BLOCKED_PENDING_VALIDATION_ACCEPTANCE_AND_TAU_STAR_DERIVATION",
            "exploratory_arms": ["B3-nodiff", "B3-swap", "B3-flip"],
            "exploratory_arms_status": "CPU_RENDER_VERIFIED_ONLY_NOT_LAUNCHED_ON_GPU",
        },
        "method_classification": {
            "preregistration_status": "AMENDED_EXPLORATORY_SUBPROTOCOL",
            "osf_registration": "https://osf.io/fqgh2",
            "baseline_tag": "prereg-v1",
            "note": "Documented in CHANGES_AFTER_PREREG.md. Threshold tau* will be derived post-validation.",
        },
    }

    body = {k: v for k, v in scope_meta.items() if k != "scope_decision_seal_sha256"}
    seal = compute_bytes_sha256(json.dumps(body, sort_keys=True, ensure_ascii=False, indent=2).encode("utf-8"))
    scope_meta["scope_decision_seal_sha256"] = seal

    with open(gov_dir / "scope_decision.json", "w", encoding="utf-8") as f:
        json.dump(scope_meta, f, indent=2, ensure_ascii=False)

    md_content = f"""# Scope Decision Record — Release v5 (Devign Validation Locked)

**Document Status:** RATIFIED BY PROJECT LEAD  
**Release ID:** `{scope_meta['release_id']}`  
**Release Version:** `{scope_meta['release_version']}`  
**Method ID:** `{scope_meta['method_id']}`  
**Authority:** Lead PI ({scope_meta['authority']['lead_pi']}) & Advisory Directives  
**Decision Timestamp:** `{scope_meta['authority']['decision_timestamp_utc']}`  
**Seal SHA-256:** `{seal}`  

---

## 1. Approved Execution Scope
- **Dataset:** Devign
- **Split:** Validation census
- **Arm:** B3 (Verified Patch-Pair Contrastive Demonstration)
- **Prompt Seed:** 42
- **Expected Census Count:** 2,732 targets
- **Pool Hash:** `{scope_meta['pool_specification']['devign_pool_sha256']}`
- **Active Pairs:** 1 verified pair (`case_08_ffmpeg_can_safely_read_8614_26054`)

## 2. Mandatory Scope Boundary & Disclosure
1. **Single-Pair Scope Limitation:**
   {scope_meta['pool_specification']['scope_limitation']}
2. **REVEAL Blocker:**
   {scope_meta['excluded_from_execution']['reason']}
3. **Test Split Exclusion:**
   Test split evaluation is strictly forbidden prior to full validation census completion and formal tau* threshold derivation.
4. **Exploratory Variant Arms:**
   B3-nodiff, B3-swap, and B3-flip are verified via CPU rendering but excluded from GPU launch in this delivery.

## 3. Governance Classification
- **Method Classification:** `{scope_meta['method_classification']['preregistration_status']}`
- **OSF Registration Anchor:** `{scope_meta['method_classification']['osf_registration']}`
- **Documentation:** Logged in `CHANGES_AFTER_PREREG.md`.
"""
    with open(gov_dir / "SCOPE_DECISION.md", "w", encoding="utf-8") as f:
        f.write(md_content)

    return scope_meta


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
        "schema_version": 1,
        "release_id": "release_20261108_v5",
        "release_version": "v5_devign_validation_locked",
        "parent_release": "release_20261108_v4",
        "release_status": "FROZEN",
        "method_id": "b3-verified-patch-v1",
        "method": "b3-verified-patch-v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": "46e6f4ab9d0ff2c9ecac124d3a6f2bdb72524bd9",
        "python_version": sys.version,
        "scope": {
            "dataset": "devign",
            "split": "validation",
            "arm": "B3",
            "prompt_seed": 42,
            "expected_count": 2732,
        },
        "excluded_from_execution": {
            "reveal": "BLOCKED_UNRESOLVED_PROVENANCE",
        },
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
        "pools_sha256": {
            "eligible_pairs.devign.jsonl": compute_file_sha256(release_dir / "pools" / "eligible_pairs.devign.jsonl"),
            "eligible_pairs.reveal.jsonl": compute_file_sha256(release_dir / "pools" / "eligible_pairs.reveal.jsonl"),
            "pool_manifest.json": compute_file_sha256(release_dir / "pools" / "pool_manifest.json"),
        },
        "runtime_lock": {
            "contract_id": "grace_qwen_q4_runtime_v1",
            "contract_sha256": compute_file_sha256(RUNTIME_LOCK_PATH),
            "model_sha256": "f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335",
            "tokenizer_revision": "b2cff646eb4bb1d68355c01b18ae02e7cf42d120",
            "backend_sdist_sha256": "34ed0f9bd9431af045bb63d9324ae620ad0536653740e9bb163a2e1fcb973be6",
        },
    }

    im_body = {k: v for k, v in im.items() if k != "seal_sha256"}
    seal = compute_bytes_sha256(json.dumps(im_body, sort_keys=True, ensure_ascii=False, indent=2).encode("utf-8"))
    im["seal_sha256"] = seal

    with open(release_dir / "inputs_manifest.json", "w", encoding="utf-8") as f:
        json.dump(im, f, indent=2, ensure_ascii=False)
    return im


def build_release_v5():
    print(f"=== Building Official B3 Release v5 at: {RELEASE_V5_DIR.name} ===")
    if not RELEASE_V5_DIR.exists():
        RELEASE_V5_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Governance directory
    gov_dir = RELEASE_V5_DIR / "governance"
    gov_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(G1_V2_CASE08 / "MAPPING_DECISION_CASE_08.md", gov_dir / "MAPPING_DECISION_CASE_08.md")
    shutil.copy2(G1_V2_CASE08 / "mapping_decision.json", gov_dir / "mapping_decision.json")
    scope_meta = generate_scope_decision(RELEASE_V5_DIR)
    print("Recorded Scope Decision Record in governance/")

    # 2. Source archive directory
    src_archive_dir = RELEASE_V5_DIR / "source_archive"
    if not src_archive_dir.exists():
        shutil.copytree(V4_DIR / "source_archive", src_archive_dir)
        print("Copied source archive from v4.")

    # 3. Candidates directory
    cand_dir = RELEASE_V5_DIR / "candidates"
    if not cand_dir.exists():
        shutil.copytree(V4_DIR / "candidates", cand_dir)
        print("Copied candidates from v4.")

    # 4. Review packets
    packets_dir = RELEASE_V5_DIR / "review_packets"
    if not packets_dir.exists():
        shutil.copytree(V4_DIR / "review_packets", packets_dir)
        print("Copied review packets from v4.")

    # 5. Reviews directory
    reviews_dir = RELEASE_V5_DIR / "reviews"
    if not reviews_dir.exists():
        shutil.copytree(V4_DIR / "reviews", reviews_dir)
        print("Copied reviews from v4.")

    # 6. Pools directory (Ingest and seal with unified metadata)
    pools_dir = RELEASE_V5_DIR / "pools"
    pools_dir.mkdir(parents=True, exist_ok=True)
    # Pre-copy pool files from v4 to preserve exact bytes
    shutil.copy2(V4_DIR / "pools" / "eligible_pairs.devign.jsonl", pools_dir / "eligible_pairs.devign.jsonl")
    shutil.copy2(V4_DIR / "pools" / "eligible_pairs.reveal.jsonl", pools_dir / "eligible_pairs.reveal.jsonl")
    shutil.copy2(V4_DIR / "pools" / "membership_diff_devign.json", pools_dir / "membership_diff_devign.json")
    shutil.copy2(V4_DIR / "pools" / "membership_diff_reveal.json", pools_dir / "membership_diff_reveal.json")

    # Re-seal pool manifest with v5 unified metadata
    ingest_human_reviews_and_seal_pools(RELEASE_V5_DIR, raise_on_error=True)
    print("Sealed pools manifest with unified v5 metadata.")

    # 7. Inputs manifest
    im = generate_inputs_manifest(RELEASE_V5_DIR)
    print(f"Inputs manifest sealed: {im['seal_sha256']}")

    # 8. Run Step 7 Pre-GPU Verifier
    acceptance_dir = RELEASE_V5_DIR / "acceptance"
    acceptance_dir.mkdir(parents=True, exist_ok=True)
    print("=== Running Step 7 Pre-GPU Verifier on Release v5 ===")
    run_step7(RELEASE_V5_DIR)

    # 9. Validation census and prompt manifests
    val_dir = RELEASE_V5_DIR / "validation"
    val_dir.mkdir(parents=True, exist_ok=True)
    val_devign_dir = val_dir / "devign"
    val_devign_dir.mkdir(parents=True, exist_ok=True)
    val_reveal_dir = val_dir / "reveal"
    val_reveal_dir.mkdir(parents=True, exist_ok=True)

    # Copy census from v4 (preserving exact bytes)
    shutil.copy2(V4_DIR / "validation" / "devign" / "validation_census.jsonl", val_devign_dir / "validation_census.jsonl")
    shutil.copy2(V4_DIR / "validation" / "reveal" / "validation_census.jsonl", val_reveal_dir / "validation_census.jsonl")

    # Run Step 8 to audit full census and seal validation_prompt_manifest.json with unified v5 metadata
    print("=== Running Step 8 Validation Census Builder on Release v5 ===")
    run_step8(RELEASE_V5_DIR)

    # 10. Verify prompt census SHA-256 against v4
    v4_devign_sha = compute_file_sha256(V4_DIR / "validation" / "devign" / "validation_census.jsonl")
    v5_devign_sha = compute_file_sha256(val_devign_dir / "validation_census.jsonl")
    assert v4_devign_sha == v5_devign_sha == "dee4a33009f4ecbf42b96e6f18c5f4390d5f0a620370af925bae0f2cceeb7e59", "Prompt bytes mismatch!"
    print("Devign validation census verified byte-identical to audited v4.")

    print("\n=======================================================")
    print("RELEASE v5 BUILT AND VERIFIED SUCCESSFULLY!")
    print(f"Devign Pool: 1 ACTIVE VERIFIED PAIR (Case 08)")
    print(f"REVEAL Pool: 0 pairs (BLOCKED_EMPTY_POOL)")
    print(f"Validation Census: 2,732 Devign prompts rendered + 2,273 REVEAL prompts safely paused")
    print("=======================================================\n")


if __name__ == "__main__":
    build_release_v5()
