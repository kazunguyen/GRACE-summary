---
id: "threshold-lock-identity-and-test-exposure-20261103"
title: "Đối chiếu chữ ký khóa ngưỡng và lịch sử tiếp xúc test trước OSF"
author: "Codex (trợ lý AI)"
author_type: "AI assistant"
requested_by: "Người dùng"
recorded_at: "2026-11-03T21:10:06+07:00"
timezone: "Asia/Bangkok"
work_date: "2026-11-03"
record_type: "osf_threshold_provenance_correction"
status: "local_documents_corrected_osf_not_submitted"
---

# Định danh phiên khóa ngưỡng và cách diễn giải test lịch sử

## Phát hiện

- Hai bản [thresholds.json](../configs/thresholds.json) và [bản trong diagnostic kit](../01_Author_Baseline_Unified/diagnostic_kit/configs/thresholds.json) có byte giống nhau. Trường `locked_sha256` hiện hành là `9252aadebf19b0f86bd9da8e59992e2adebd87d386ab6600302b9ac10a2914a3`; `load_locked()` kiểm được cả 14 mục. SHA-256 của **toàn bộ file** là `fcb4ae11ffdabad304cd3c6f614c8a133fee409f9076d122888958bbb5e3d1bc`, khác với chữ ký tự xác thực bên trong file.
- `a0108431ad859aacc3dab29ca7e88a7eb404428b4d60fc251e3bbae7d350c831` nằm đúng trong `metadata.previous_locked_sha256`, không phải chữ ký hiện hành. Giữ nguyên trường này để truy lịch sử; **không sửa hai file ngưỡng và không fit lại giá trị nào**. Metadata ghi niêm phong lại lúc `2026-11-03T08:57:36Z` sau khi sửa khai báo tiếp xúc test.
- [Exposure ledger](../configs/protocol.yaml) ghi các lượt test Tầng 1 đã thực hiện/xem metric trước OSF, 230 nhãn raw B2-flip Devign test đã xem và B2-rand đã bắt đầu validation. Bản khóa ngày 03/11 không chứng minh ngưỡng đã khóa trước các lượt test cũ. Chạy lại về sau không xóa lịch sử tiếp xúc. `registered_at` vẫn là `null` vì chưa có xác nhận OSF.

## Chỉnh sửa tài liệu

1. Ghi rõ `locked_sha256` hiện hành, `previous_locked_sha256`, ngày reseal và việc **không refit** trong [preregistration.md](../preregistration.md), [preregistration_en.md](../preregistration_en.md), [preregistration_vi.md](../preregistration_vi.md), [hướng dẫn OSF tiếng Anh](../docs/OSF_SUBMISSION_GUIDE_EN.md), [hướng dẫn OSF tiếng Việt](../docs/OSF_SUBMISSION_GUIDE.md) và [README gói OSF](../Runs-management/osf_registration_draft_20261102/README.md). Không thay chữ ký cũ trong metadata lịch sử.
2. Trong ba bản preregistration, ghi B2-flip/B2-rand và việc rerun không xóa tiếp xúc; sửa câu Bảng B thành yêu cầu **khi bảng được tạo**, vì bảng cuối chưa có. Bỏ gói 60 prompt hai người đã chấm khỏi danh sách phân tích “chưa làm”; chỉ từng phân tích chưa thực hiện lúc nộp OSF mới có thể được phân loại tiến cứu. Tier 1 đã xem test/metric vẫn là existing data following analysis.
3. Đồng bộ hai hướng dẫn và README với báo cáo dry-run hiện hành: **70.070 prompt, 10 arm, 5 arm bị chặn**, không còn mô tả 95.095 prompt/15 arm như đã hoàn tất.

## Kiểm tra và giới hạn

- `load_locked(configs/thresholds.json)` đọc thành công 14 mục; hai bản threshold giống byte. Không đổi `configs/thresholds.json`, `configs/thresholds_flat.json`, protocol hay output inference.
- Dựng lại [PDF](../Runs-management/osf_registration_draft_20261102/output/pdf/GRACE_OSF_PREREGISTRATION_20261102.pdf) 11 trang, SHA-256 `0f705db32fa2a820d7d9cb676cb446d79ee5f90d411ddf0bc67281217c6f0579`. Kiểm text có chữ ký hiện hành, lịch sử tiếp xúc, câu Bảng B mới; không có khối chữ tràn trang. [ZIP](../Runs-management/osf_registration_draft_20261102/GRACE_OSF_PREREGISTRATION_20261102.zip) chứa 40 artifact và bảng hash, SHA-256 `9f4e58bdd6d697a3b25a47a27d287206719e1fdb469599f1fd3b489c79db159c`; giải nén và đối chiếu hash đạt. `tests/test_preregistration_integrity.py`: **6 passed**.
- Các chỉnh sửa đang ở local, chưa nằm trong commit/tag `prereg-v1` trên origin; link theo tag chỉ mở bản đã push trước đó cho tới khi có commit/tag mới. Chưa nộp OSF. Việc trình bày minh bạch không biến test lịch sử thành kết quả xác nhận tiến cứu.
