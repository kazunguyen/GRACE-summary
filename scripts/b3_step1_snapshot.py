#!/usr/bin/env python3
"""Step 1: Snapshot sources, verify frozen contracts, banks, tokenizers, and governance."""

import argparse
import datetime
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
SPECS_ARCHIVE = ROOT / "Runs-management" / "grace_15arms_prompts_and_clean_specs.zip"
FREEZE_DIR = ROOT / "01_Author_Baseline_Unified" / "output" / "research_freeze_20261101"
EXPECTED_FREEZE_SHA = "e1d3c6b17c3a0b5c1e05203794d48a33825e0ea00a55deaaef565af25efe0448"
EXPECTED_TOKENIZER_REV = "b2cff646eb4bb1d68355c01b18ae02e7cf42d120"
TOKENIZER_DIR = (
    ROOT
    / "11_Arm_B1H2_Evidence"
    / "tokenizer_cache_v6"
    / "models--Qwen--Qwen3-Coder-30B-A3B-Instruct"
    / "snapshots"
    / EXPECTED_TOKENIZER_REV
)


def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def compute_bytes_sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def run_step1(release_dir: Path = DEFAULT_RELEASE_DIR):
    print(f"=== Step 1: Source Snapshot and Constraint Audit (Target: {release_dir.name}) ===")
    release_dir.mkdir(parents=True, exist_ok=True)
    (release_dir / "governance").mkdir(exist_ok=True)
    (release_dir / "discovery" / "devign").mkdir(parents=True, exist_ok=True)
    (release_dir / "discovery" / "reveal").mkdir(parents=True, exist_ok=True)
    (release_dir / "source_archive").mkdir(exist_ok=True)
    (release_dir / "candidates").mkdir(exist_ok=True)
    (release_dir / "review_packets").mkdir(exist_ok=True)
    (release_dir / "reviews").mkdir(exist_ok=True)
    (release_dir / "pools").mkdir(exist_ok=True)
    (release_dir / "validation" / "devign").mkdir(parents=True, exist_ok=True)
    (release_dir / "validation" / "reveal").mkdir(parents=True, exist_ok=True)
    (release_dir / "acceptance").mkdir(exist_ok=True)

    # 1. Environment & Git Snapshot
    git_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    git_status = subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True).strip()
    python_ver = sys.version
    timestamp_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
    timestamp_local = datetime.datetime.now().isoformat()

    print(f"Git HEAD: {git_head}")
    print(f"Python: {python_ver}")
    print(f"Timestamp UTC: {timestamp_utc}")

    # 2. Module Hashes
    modules_to_hash = [
        "01_Author_Baseline_Unified/diagnostic_kit/src/grace_diag/amended_b3.py",
        "01_Author_Baseline_Unified/diagnostic_kit/src/grace_diag/contrastive_pair_builder.py",
        "01_Author_Baseline_Unified/diagnostic_kit/src/grace_diag/probes.py",
        "01_Author_Baseline_Unified/diagnostic_kit/src/grace_diag/token_budget.py",
        "configs/inference_runtime_lock.json",
        "Runs-management/b3_amended_20261106/check_b3.py",
    ]
    module_hashes = {}
    for rel_path in modules_to_hash:
        full_path = ROOT / rel_path
        if not full_path.is_file():
            raise FileNotFoundError(f"Missing required module: {rel_path}")
        h = compute_sha256(full_path)
        module_hashes[rel_path] = h
        print(f"Module {rel_path}: {h}")

    # 3. Authority Documents Hashes
    authority_docs = [
        "docs/OSF_response/De_cuong_nghien_cuu_GRACE_hop_nhat.docx",
        "docs/OSF-update-20261107.pdf",
    ]
    authority_hashes = {}
    for rel_path in authority_docs:
        full_path = ROOT / rel_path
        if full_path.is_file():
            h = compute_sha256(full_path)
            authority_hashes[rel_path] = h
            print(f"Authority doc {rel_path}: {h}")

    # 4. Step Execution Scripts Hashes
    step_scripts = [
        "scripts/b3_step1_snapshot.py",
        "scripts/b3_step2_https_recon.py",
        "scripts/b3_step3_devign_investigation.py",
        "scripts/b3_step4_reveal_provenance.py",
        "scripts/b3_step5_make_candidates.py",
        "scripts/b3_step6_packet_tool.py",
        "scripts/b3_step7_verify_selector_renderer.py",
        "scripts/b3_step8_validation_census_builder.py",
    ]
    script_hashes = {}
    for rel_path in step_scripts:
        full_path = ROOT / rel_path
        if full_path.is_file():
            h = compute_sha256(full_path)
            script_hashes[rel_path] = h

    # 5. Verify Freeze Manifest
    freeze_manifest_path = FREEZE_DIR / "freeze_manifest.json"
    actual_freeze_sha = compute_sha256(freeze_manifest_path)
    print(f"freeze_manifest.json SHA256: {actual_freeze_sha}")
    if actual_freeze_sha != EXPECTED_FREEZE_SHA:
        raise ValueError(f"Freeze manifest mismatch! Expected {EXPECTED_FREEZE_SHA}, got {actual_freeze_sha}")

    with open(freeze_manifest_path, "r", encoding="utf-8") as f:
        freeze_data = json.load(f)

    # Check internal files in freeze manifest
    verified_freeze_files = {}
    for ds in ["devign", "reveal"]:
        ds_info = freeze_data["datasets"][ds]
        for fname, exp_hash in ds_info["files_sha256"].items():
            fpath = FREEZE_DIR / ds / fname
            if not fpath.is_file():
                raise FileNotFoundError(f"Missing freeze file: {ds}/{fname}")
            act_hash = compute_sha256(fpath)
            if act_hash != exp_hash:
                raise ValueError(f"Hash mismatch for {ds}/{fname}: expected {exp_hash}, got {act_hash}")
            verified_freeze_files[f"{ds}/{fname}"] = act_hash

    for gkey, ginfo in freeze_data.get("graph_sources", {}).items():
        verified_freeze_files[f"declared_graph_source:{gkey}"] = {
            "path": ginfo["path"],
            "declared_sha256": ginfo["sha256"]
        }

    print("All declared freeze manifest files verified successfully.")

    # 6. Verify train_raw.jsonl and train_manifest.jsonl for devign & reveal
    donor_counts = {}
    for ds, exp_count in [("devign", 21691), ("reveal", 17636)]:
        manifest_p = FREEZE_DIR / ds / "train_manifest.jsonl"
        raw_p = FREEZE_DIR / ds / "train_raw.jsonl"

        manifest_rows = {}
        with open(manifest_p, "r", encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                manifest_rows[r["id"]] = r

        bank_rows = []
        with open(raw_p, "r", encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                uid = r["id"]
                if uid not in manifest_rows:
                    raise ValueError(f"Row {uid} not in manifest")
                m = manifest_rows[uid]
                if m["keep_in_bank"]:
                    if r["split"] != "train":
                        raise ValueError(f"Non-train donor {uid}")
                    if r["dataset"] != ds:
                        raise ValueError(f"Dataset mismatch {uid}")
                    if r["target"] != m["label"]:
                        raise ValueError(f"Label mismatch {uid}")
                    code_sha = hashlib.sha256(r["func"].encode("utf-8")).hexdigest()
                    if code_sha != m["code_sha256"]:
                        raise ValueError(f"Code hash mismatch {uid}")
                    bank_rows.append(r)

        donor_counts[ds] = len(bank_rows)
        print(f"Dataset {ds}: verified {len(bank_rows)} clean train donors (expected {exp_count})")
        if len(bank_rows) != exp_count:
            raise ValueError(f"Census mismatch for {ds}: expected {exp_count}, got {len(bank_rows)}")

    # 7. Verify Tokenizer Snapshot
    if not TOKENIZER_DIR.is_dir():
        raise FileNotFoundError(f"Missing tokenizer snapshot dir: {TOKENIZER_DIR}")
    tokenizer_files = {}
    for fname in ["chat_template.jinja", "config.json", "merges.txt", "tokenizer.json", "tokenizer_config.json", "vocab.json"]:
        tpath = TOKENIZER_DIR / fname
        if not tpath.is_file():
            raise FileNotFoundError(f"Missing tokenizer file: {fname}")
        thash = compute_sha256(tpath)
        tokenizer_files[fname] = thash
        print(f"Tokenizer file {fname}: {thash}")

    # 8. Governance Record (truthful, addressing audit finding F07 & F01)
    gov_record = {
        "amendment_method": "b3-verified-patch-v1",
        "governance_authority": "Lead PI & Advisory Directives (De_cuong_nghien_cuu_GRACE_hop_nhat.docx, OSF Amendment Submission 2026-11-07)",
        "protocol_decisions": {
            "method_classification": {
                "decision": "Amended B3 verified patch-pair (b3-verified-patch-v1) proposed in OSF amendment update (docs/OSF-update-20261107.pdf).",
                "osf_registration_status": "SUBMITTED_AMENDMENT_PENDING_REGISTRATION_STAMP",
                "status_clarification": "The document docs/OSF-update-20261107.pdf reflects an amendment submitted to OSF on 2026-11-07 requesting a transparent transition to same-function verified patch pair. It is tracked as an amended experimental track distinct from the permanently frozen prereg-v1 baseline registration (https://osf.io/fqgh2).",
                "threshold_policy": "New threshold tau* must be independently selected on fresh B3 validation census (argmax MCC on 0.01..0.99 grid). No inheritance from historical B3 heuristic thresholds.",
                "probe_inheritance": "B3-swap and B3-flip will inherit tau* directly from amended B3; B3-nodiff requires separate validation tau*.",
                "review_separation_policy": "Strict operational separation between Automated Technical Triage (automated code/commit checks) and Independent Dual Human Review. No autogenerated review opinions, simulated quotes, or fabricated signatures are permitted."
            },
            "demonstration_budget": {
                "decision": "Each demonstration is capped at <= 1,500 tokens (budget_each=1500), query code <= 3,000 tokens, graph <= 1,500 tokens, 64 reserved tokens, total prompt <= 8,192 tokens.",
                "authority_reference": "De_cuong_nghien_cuu_GRACE_hop_nhat.docx paragraph 88 ('code target <= 3.000 token, moi demo <= 1.500 token, graph <= 1.500 token, tong <= 8.192 token').",
                "audit_gate": "Strict verification that each demo function and diff block are complete and within context budget."
            }
        },
        "reviewers_designated": {
            "reviewer_1": "Hiếu (Lead PI / Author)",
            "reviewer_2": "Dũng (Teammate / Co-author)"
        },
        "timestamp_utc": timestamp_utc
    }
    with open(release_dir / "governance" / "governance_record.json", "w", encoding="utf-8") as f:
        json.dump(gov_record, f, indent=2, ensure_ascii=False)

    decision_protocol_md = f"""# Protocol Decisions & Governance Record for Amended B3 (v2 Remediated)

**Date:** {timestamp_local} (UTC: {timestamp_utc})  
**Mốc mã nguồn:** Git commit `{git_head}`  
**Tài liệu thẩm quyền:** `docs/OSF_response/De_cuong_nghien_cuu_GRACE_hop_nhat.docx`, `docs/OSF-update-20261107.pdf`  

## 1. Phân loại phương pháp và Trạng thái OSF
- **Phương pháp B3 mới:** Thuật toán ghép cặp có kiểm chứng `b3-verified-patch-v1` (`VerifiedPairSelector`), thay thế toàn bộ cơ chế heuristic bề mặt cũ.
- **Trạng thái OSF:** Bản cập nhật minh bạch đã được nộp lên OSF vào ngày 07/11/2026 (`docs/OSF-update-20261107.pdf`). Tại thời điểm phát hành này, bản nộp đang ở trạng thái `SUBMITTED_AMENDMENT_PENDING_REGISTRATION_STAMP` (chờ đóng dấu xét duyệt chính thức của OSF). Phương pháp được theo dõi dưới nhánh thực nghiệm điều chỉnh (amended track), tách biệt hoàn toàn khỏi bản đăng ký gốc đóng băng `prereg-v1` (https://osf.io/fqgh2).
- **Ngưỡng quyết định (tau*):** Ngưỡng tối ưu của B3 mới BẮT BUỘC phải được tính độc lập trên tập full validation của chính run mới (argmax MCC trên lưới 99 điểm tau in [0.01, 0.99]). TUYỆT ĐỐI không kế thừa hay tái sử dụng ngưỡng lịch sử của B3 cũ.
- **Kế thừa cho Probes:** B3-swap và B3-flip sẽ kế thừa trực tiếp tau* từ B3 mới. B3-nodiff tính ngưỡng riêng trên validation của chính nó.

## 2. Phân tách rõ ràng giữa Triage tự động và Thẩm định con người
- **Automated Technical Triage:** Do script tự động thực hiện nhằm kiểm tra các tiêu chí cơ học (commit hash hợp lệ, quan hệ cha-con trong git, danh sách file thay đổi, diff thực tế). Kết quả triage được ghi nhận rõ là triage kỹ thuật tự động (`AUTOMATED_TECHNICAL_TRIAGE`), tuyệt đối KHÔNG gán tên con người hay sinh bình luận/chữ ký giả lập.
- **Independent Dual Human Review:** Khi ứng viên vượt qua các cổng kỹ thuật và có đầy đủ bằng chứng mã nguồn gốc, hai thẩm định viên (Hiếu & Dũng) sẽ độc lập điền phiếu duyệt riêng, ký xác nhận trên mã băm bằng chứng (`payload_sha256`).

## 3. Ngân sách Demonstration
- Căn cứ văn bản đề cương hợp nhất (`De_cuong_nghien_cuu_GRACE_hop_nhat.docx`, Đoạn 88):
  * Code target <= 3.000 tokens.
  * **Mỗi demonstration <= 1.500 tokens** (`budget_each = 1500`).
  * Đồ thị CPG <= 1.500 tokens.
  * Ngăn dự phòng: 64 tokens.
  * Tổng prompt sau chat template <= 8.192 tokens.
"""
    with open(release_dir / "governance" / "DECISION_PROTOCOL.md", "w", encoding="utf-8") as f:
        f.write(decision_protocol_md)

    # 9. Inputs Manifest with Seal
    inputs_manifest = {
        "created_at_utc": timestamp_utc,
        "release_version": "v3_remediated",
        "parent_release": "v2_remediated",
        "git_commit": git_head,
        "git_status": git_status,
        "python_version": python_ver,
        "freeze_manifest": {
            "path": str(freeze_manifest_path.relative_to(ROOT)),
            "sha256": actual_freeze_sha,
            "status": "SEAL_VERIFIED"
        },
        "specs_archive_sha256": compute_sha256(SPECS_ARCHIVE) if SPECS_ARCHIVE.is_file() else None,
        "modules_sha256": module_hashes,
        "authority_documents_sha256": authority_hashes,
        "execution_scripts_sha256": script_hashes,
        "verified_freeze_files": verified_freeze_files,
        "tokenizer": {
            "revision": EXPECTED_TOKENIZER_REV,
            "path": str(TOKENIZER_DIR.relative_to(ROOT)),
            "files_sha256": tokenizer_files
        },
        "clean_train_donors": donor_counts,
        "status": "STEP1_PASSED_SEALED"
    }

    manifest_bytes = json.dumps(inputs_manifest, sort_keys=True, ensure_ascii=False, indent=2).encode("utf-8")
    manifest_seal = compute_bytes_sha256(manifest_bytes)
    inputs_manifest["seal_sha256"] = manifest_seal

    with open(release_dir / "inputs_manifest.json", "w", encoding="utf-8") as f:
        json.dump(inputs_manifest, f, indent=2, ensure_ascii=False)

    print(f"Step 1 Complete! Inputs manifest written to {release_dir / 'inputs_manifest.json'} with seal: {manifest_seal}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Step 1: Snapshot sources and contracts")
    parser.add_argument("--release-dir", type=Path, default=DEFAULT_RELEASE_DIR, help="Output release directory")
    args = parser.parse_args()
    run_step1(args.release_dir)
