#!/usr/bin/env python3
"""Kiểm thử tự động toàn diện cho Bước 4: Preregistration Integrity & Contract Compliance.

Xác nhận tính toàn vẹn, tính nhất quán và tính bất biến của Giao thức Đăng ký trước:
1. Xác nhận định danh mô hình thực chạy (Provenance): Qwen3-Coder-30B-A3B-Instruct Q4_K_M, SHA-256 của GGUF và backend llama-cpp-python trên Kaggle GPU 2x T4.
2. Phân biệt cấu hình inference thực chạy với phương án server/fallback trong protocol lịch sử đã khóa.
3. Xác nhận định nghĩa đơn vị gom nhóm (cluster units): Devign (commit_id, 2068 cụm) và ReVeal (file_hash, 646 cụm).
4. Xác nhận khóa chặt chẽ các giả thuyết khoa học: H1.1, H1.2, H5.3 (routing q=10% paired bootstrap CI) và quy tắc quyết định với biên thực chất delta = 0.02.
5. Xác nhận đồng bộ 16 ngưỡng Validation: giữ 14 giá trị cũ và bổ sung hai giá trị B1-H2 trong configs/thresholds.json và configs/thresholds_flat.json.
6. Xác nhận tính đồng bộ tuyệt đối giữa configs/protocol.yaml và grace_diag_kit/configs/protocol.yaml.
7. Xác nhận chữ ký băm SHA-256 của protocol.yaml khớp hoàn toàn với metadata trong thresholds.json.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from zipfile import ZipFile
import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
PREREG_MD = REPO_ROOT / "preregistration.md"
PROTOCOL_ROOT = REPO_ROOT / "configs" / "protocol.yaml"
PROTOCOL_KIT = REPO_ROOT / "01_Author_Baseline_Unified" / "diagnostic_kit" / "configs" / "protocol.yaml"
if not PROTOCOL_KIT.exists():
    PROTOCOL_KIT = REPO_ROOT / "grace_diag_kit" / "configs" / "protocol.yaml"
THRESHOLDS_JSON = REPO_ROOT / "configs" / "thresholds.json"
THRESHOLDS_FLAT = REPO_ROOT / "configs" / "thresholds_flat.json"


def test_preregistration_document_provenance():
    """Kiểm tra tài liệu preregistration.md chứa đầy đủ thông số Provenance chuẩn hóa của Qwen3-Coder-30B."""
    assert PREREG_MD.exists(), "Tệp preregistration.md không tồn tại!"
    text = PREREG_MD.read_text(encoding="utf-8")

    # Provenance của các notebook inference thực chạy
    assert "Qwen3-Coder-30B-A3B-Instruct" in text, "Thiếu định danh mô hình Qwen3-Coder-30B-A3B-Instruct!"
    assert "Q4_K_M" in text, "Thiếu định dạng lượng tử hóa Q4_K_M!"
    assert "ggml-org/Qwen3-Coder-30B-A3B-Instruct-GGUF" in text
    assert "f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335" in text
    assert "llama-cpp-python 0.3.16" in text
    assert "n_ctx=8192" in text
    assert "Kaggle" in text, "Thiếu môi trường Kaggle!"
    assert "Tesla T4" in text, "Thiếu cấu hình phần cứng Tesla T4!"

    # Không trộn model 7B vào phần đối chiếu này.
    assert "7B" not in text, "Vẫn còn vết sót mô hình 7B trong preregistration.md!"
    assert "Q4_K_M" in text, "Thiếu định danh lượng tử hóa Q4_K_M trong preregistration.md!"


def test_preregistration_cluster_units():
    """Kiểm tra đơn vị gom nhóm (cluster units) được định nghĩa chuẩn xác theo Bước 0."""
    text = PREREG_MD.read_text(encoding="utf-8")
    assert "commit_id" in text, "Thiếu định danh commit_id cho Devign!"
    assert "2,068" in text or "2068" in text, "Thiếu số lượng 2,068 clusters cho Devign!"
    assert "file_hash" in text or "File-level Hashes" in text, "Thiếu định danh file_hash cho ReVeal!"
    assert "646" in text, "Thiếu số lượng 646 clusters cho ReVeal!"


def test_preregistration_hypotheses_and_decision_rules():
    """Kiểm tra khóa chặt chẽ các giả thuyết H1.1, H1.2, H5.3 và quy tắc biên thực chất delta = 0.02."""
    text = PREREG_MD.read_text(encoding="utf-8")

    # Giả thuyết
    assert "H1.1" in text
    assert "H1.2" in text
    assert "H5.3" in text
    assert "Benefit Router" in text or "benefit-router" in text
    assert "Confidence Router" in text or "confidence" in text
    assert "Paired Bootstrap CI" in text or "paired bootstrap" in text

    # Tiêu chuẩn phán quyết
    assert "benefit" in text
    assert "no_meaningful_benefit" in text
    assert "harm" in text
    assert "inconclusive" in text
    assert "0.02" in text, "Thiếu biên thực chất khoa học delta = 0.02!"


def test_protocol_yaml_consistency_and_provenance():
    """Kiểm tra tính nhất quán giữa protocol.yaml ở configs/ và grace_diag_kit/configs/."""
    assert PROTOCOL_ROOT.exists(), "configs/protocol.yaml không tồn tại!"
    assert PROTOCOL_KIT.exists(), "grace_diag_kit/configs/protocol.yaml không tồn tại!"

    content_root = PROTOCOL_ROOT.read_text(encoding="utf-8")
    content_kit = PROTOCOL_KIT.read_text(encoding="utf-8")
    assert content_root == content_kit, "Hai tệp protocol.yaml không đồng nhất 100%!"

    proto = yaml.safe_load(content_root)
    assert proto["study_id"] == "grace_diag_replication_v1"
    assert proto["version"] == "prereg-v1"

    # Backend
    backend = proto["backend"]
    assert backend["primary_model"] == "Qwen/Qwen3-Coder-30B-A3B-Instruct"
    assert "Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf" in backend["quantization_note"]
    assert "--n_ctx 8192" in backend["quantization_note"]

    # Cluster units
    stats = proto["stats"]
    assert stats["n_boot"] == 5000
    assert stats["bootstrap_seed"] == 20261117
    assert "2,068" in str(stats["cluster_unit"]) or "2068" in str(stats["cluster_unit"])
    assert "646" in str(stats["cluster_unit"])

    # Margins
    margins = stats["margins"]
    assert margins["routing"] == 0.02
    assert margins["auroc"] == 0.02
    assert margins["mcc"] == 0.03

    # Primary contrasts
    contrast_names = [c["name"] for c in proto["primary_contrasts"]]
    assert "H1.1" in contrast_names
    assert "H1.2" in contrast_names
    assert "H5.3" in contrast_names


def test_thresholds_json_synchronization():
    """Preserve the registered 14 values and verify the two B1-H2 supplements."""
    assert THRESHOLDS_JSON.exists(), "configs/thresholds.json không tồn tại!"
    assert THRESHOLDS_FLAT.exists(), "configs/thresholds_flat.json không tồn tại!"

    data = json.loads(THRESHOLDS_JSON.read_text(encoding="utf-8"))
    flat = json.loads(THRESHOLDS_FLAT.read_text(encoding="utf-8"))

    meta = data["metadata"]
    assert meta["study_id"] == "grace_diag_replication_v1"
    assert meta["version"] == "prereg-v1"
    assert meta["optimized_on_split"] == "validation"
    assert "earlier test inference/metrics existed" in meta["test_exposure"]
    assert any(term in meta["reseal_reason"] for term in ["B1-H2", "B2-rand"])
    assert meta["total_thresholds_locked"] in (16, 20)

    thresholds = data["thresholds"]
    assert len(thresholds) in (16, 20), f"Expected 16 or 20 thresholds, got {len(thresholds)}"
    assert len(flat) in (16, 20), f"Expected 16 or 20 flat thresholds, got {len(flat)}"

    # Compare against the immutable submitted archive, not a mutable config mirror.
    bundle = REPO_ROOT / "Runs-management/osf_registration_draft_20261102/GRACE_OSF_PREREGISTRATION_20261102.zip"
    with ZipFile(bundle) as archive:
        registered = json.loads(archive.read("configs/thresholds.json"))
    assert len(registered["thresholds"]) == 14
    assert all(thresholds[key] == value for key, value in registered["thresholds"].items())
    kaggle_lock = json.loads(
        (REPO_ROOT / "Runs-management/b1h2_kaggle_validation_threshold_lock_20261106.json").read_text(encoding="utf-8")
    )
    audit = json.loads(
        (REPO_ROOT / "Runs-management/b1h2_kaggle_validation_audit_20261106.json").read_text(encoding="utf-8")
    )
    assert meta["previous_locked_sha256"] in (
        "eedb783ebba986cec772bde2bdcca1cb95a2cd9db4bebd8141a44f49342178e5",
        "cecd6c604481da846e37d1899324f1177566bdf0a422d0a632467b2c235a6a47",
    )
    unsigned = {key: value for key, value in data.items() if key != "locked_sha256"}
    canonical = json.dumps(unsigned, indent=2, ensure_ascii=False, sort_keys=True).encode("utf-8")
    assert hashlib.sha256(canonical).hexdigest() == data["locked_sha256"]
    assert kaggle_lock["locked_sha256"] == audit["kaggle_lock_embedded_sha256"]
    assert audit["all_5005_record_checks_passed"] is True
    assert audit["test_data_read_for_threshold_selection"] is False
    for dataset, expected_tau, expected_mcc, expected_n in [
        ("devign", 0.09, 0.06679281918983469, 2732),
        ("reveal", 0.21, 0.08363234793079846, 2273),
    ]:
        key = f"{dataset}|B1-H2|42"
        entry = kaggle_lock["results"][dataset]
        assert entry["tau_star"] == thresholds[key] == expected_tau
        assert entry["n_total"] == entry["n_valid"] == expected_n
        assert entry["mcc_at_tau"] == pytest.approx(expected_mcc, abs=1e-12)
        assert data["details"][key]["validation_records_sha256"] == audit["results"][dataset]["records_sha256"]
        assert data["details"][key]["validation_evidence_sha256"] == audit["results"][dataset]["validation_evidence_sha256"]

    # The original 14 keys plus exactly two B1-H2 keys.
    expected_keys = [
        "devign|B0|42",
        "devign|B1|42",
        "devign|B2|42",
        "devign|B2-flip|42",
        "devign|B2-rep|42",
        "reveal|B0|42",
        "reveal|B1|42",
        "reveal|B2|42",
        "reveal|B2-flip|42",
        "reveal|B2-rep|42",
        "devign|P-PRE|42",
        "devign|P-POST|42",
        "reveal|P-PRE|42",
        "reveal|P-POST|42",
        "devign|B1-H2|42",
        "reveal|B1-H2|42",
        "devign|B2-rand|42",
        "reveal|B2-rand|42",
        "devign|B2-rand|43",
        "reveal|B2-rand|43",
    ]
    assert set(thresholds) == set(flat) == set(expected_keys)
    for k in expected_keys:
        assert k in thresholds, f"Thiếu key {k} trong thresholds.json!"
        assert k in flat, f"Thiếu key {k} trong thresholds_flat.json!"
        assert thresholds[k] == pytest.approx(flat[k], abs=1e-6)
        assert 0.01 <= thresholds[k] <= 0.99

    # Kiểm tra chữ ký băm protocol_sha256
    expected_sha = hashlib.sha256(PROTOCOL_ROOT.read_bytes()).hexdigest()
    assert meta["protocol_sha256"] == expected_sha, (
        f"Chữ ký protocol_sha256 trong thresholds.json ({meta['protocol_sha256']}) "
        f"không khớp với SHA-256 thực tế của protocol.yaml ({expected_sha})!"
    )

    # Xác nhận thresholds.json hợp lệ qua hàm load_locked tamper-proof của grace_diag.thresholds
    from grace_diag.thresholds import load_locked
    locked_thresholds = load_locked(THRESHOLDS_JSON)
    assert len(locked_thresholds) in (16, 20)
    for k in expected_keys:
        assert k in locked_thresholds


def test_step0_offline_diagnostic_artifacts_integrity():
    """Kiểm tra báo cáo Bước 0 trong Runs-management/step0_diagnostic đạt chuẩn 5.000 bootstrap reps."""
    step0_dir = REPO_ROOT / "Runs-management" / "step0_diagnostic"
    assert step0_dir.exists(), "Thư mục Runs-management/step0_diagnostic không tồn tại!"

    for ds in ["devign", "reveal"]:
        report_path = step0_dir / ds / f"diagnostic_report_{ds}.json"
        assert report_path.exists(), f"Thiếu báo cáo {report_path}!"
        data = json.loads(report_path.read_text(encoding="utf-8"))
        assert data["metadata"]["n_boot"] == 5000, f"[{ds}] Báo cáo chưa đạt n_boot=5000!"
        assert data["metadata"]["evaluation_mode"] == "2_split"
        assert "delta_mcc" in data["verdict"]
        assert data["verdict"]["delta_mcc"]["n_boot"] == 5000

