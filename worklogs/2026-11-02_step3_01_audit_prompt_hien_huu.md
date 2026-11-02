---
id: "step3-20261102-01"
title: "Hậu kiểm toàn vẹn các prompt đã có"
author: "Codex (trợ lý AI)"
author_type: "AI assistant"
requested_by: "Người dùng trong chat"
recorded_at: "2026-11-02T18:13:39+07:00"
timezone: "Asia/Bangkok"
work_date: "2026-11-02"
record_type: "retrospective_worklog"
status: "completed"
overall_step3_status: "incomplete"
evidence_verified_at: "2026-11-02T15:56:40.397715+07:00"
---

# Hậu kiểm toàn vẹn các prompt đã có

Ghi lại công việc đã thực hiện trước đó. recorded_at là thời điểm lập worklog; evidence_verified_at (nếu có) là mốc kiểm chứng của artifact, không phải thời gian bắt đầu/kết thúc chạy.

## Việc đã làm

- Audit 100.110 dòng prompt/40 tập thuộc B0, B1, B2, B2-flip, B2-rep và B2-rand; tách phiên donor cũ/mới và seed.
- Kiểm ID, hash, payload code/graph/demo, biến thể, token chính xác, mức cắt và các cờ nhãn.
- Giữ cảnh báo regex gốc; phân loại theo ngữ cảnh C/C++ thay vì xóa cảnh báo.

## Thay đổi đã thực hiện

Thêm các công cụ audit/finalize/verify và hồ sơ tại [prompt_audit_20261102](../Runs-management/prompt_audit_20261102/README.md). Xuất bảng từng prompt, danh sách cờ và bằng chứng nguồn/hash.

## Kết quả và bằng chứng

- Kiểm tra payload đạt; không còn cờ nhãn chưa giải quyết trong phạm vi kiểm tra tự động.
- Giữ 403 dòng demo dưới 25% gốc, gồm 68 dòng đã inference. Tiêu chí nghiệm thu cấp tập là demo rỗng ≤1%; các cờ từng dòng không tự động làm cả tập trượt.
- [Verification](../Runs-management/prompt_audit_20261102/verification.json), [kết luận](../Runs-management/prompt_audit_20261102/KET_QUA.md), [đối chiếu tiêu chí Bước 3](../Runs-management/prompt_audit_20261102/BUOC_3_DOI_CHIEU.md).

## Giới hạn

Đây là hậu kiểm, không thay đổi thứ tự các run lịch sử. Phạm vi sáu arm tại thời điểm này được mở rộng trong [lượt dry-run tiếp theo](2026-11-02_step3_05_dry_run_toan_validation.md); không cộng số dòng audit thành số lượt inference.
