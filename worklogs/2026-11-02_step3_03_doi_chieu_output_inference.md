---
id: "step3-20261102-03"
title: "Đối chiếu output inference phục vụ hậu kiểm Bước 3"
author: "Codex (trợ lý AI)"
author_type: "AI assistant"
requested_by: "Người dùng trong chat"
recorded_at: "2026-11-02T18:13:39+07:00"
timezone: "Asia/Bangkok"
work_date: "2026-11-02"
record_type: "retrospective_worklog"
status: "completed"
overall_step3_status: "incomplete"
---

# Đối chiếu output inference phục vụ hậu kiểm Bước 3

Ghi lại công việc đã thực hiện trước đó. recorded_at là thời điểm lập worklog; evidence_verified_at (nếu có) là mốc kiểm chứng của artifact, không phải thời gian bắt đầu/kết thúc chạy.

## Việc đã làm

- Đối chiếu 30.691 record inference đã nhập với ID, prompt và các manifest liên quan.
- Tính lại score từ logprob và kiểm pred_argmax.
- Thống kê riêng lỗi định dạng raw response và lỗi score.

## Thay đổi đã thực hiện

Bổ sung công cụ [audit_response_coverage.py](../Runs-management/audit_response_coverage.py), bảng raw-response lỗi và kết quả kiểm chứng trong hồ sơ hậu kiểm.

## Kết quả và bằng chứng

- 30.691 score khớp phép tính lại từ logprob; không có score lỗi.
- Có 1.135 raw response không phải nhãn 0/1: B0 có 1.132, B1 có 3. Giữ raw response và score riêng, không ép token lỗi thành nhãn 0.
- [Verification](../Runs-management/prompt_audit_20261102/verification.json), [inference audit](../Runs-management/prompt_audit_20261102/inference_audit.json), [raw-response coverage](../Runs-management/prompt_audit_20261102/raw_response_coverage.json).

## Giới hạn

Chỉ kiểm kết quả đã có, không gọi model hoặc sửa prediction. Việc hậu kiểm không xác nhận hồi tố rằng các run cũ đã audit/khóa ngưỡng trước test.
