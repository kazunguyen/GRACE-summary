---
id: "step3-20261102-02"
title: "Kiểm donor frozen và tính tái lập của B2-rand"
author: "Codex (trợ lý AI)"
author_type: "AI assistant"
requested_by: "Người dùng trong chat"
recorded_at: "2026-11-02T18:13:39+07:00"
timezone: "Asia/Bangkok"
work_date: "2026-11-02"
record_type: "retrospective_worklog"
status: "completed"
overall_step3_status: "incomplete"
evidence_verified_at: "2026-11-02T15:38:26.033159+07:00"
---

# Kiểm donor frozen và tính tái lập của B2-rand

Ghi lại công việc đã thực hiện trước đó. recorded_at là thời điểm lập worklog; evidence_verified_at (nếu có) là mốc kiểm chứng của artifact, không phải thời gian bắt đầu/kết thúc chạy.

## Việc đã làm

- Đối chiếu ID, code và nhãn của 21.691 donor Devign, 17.636 donor REVEAL với snapshot frozen và train manifest.
- Chạy lại phép chọn donor B2-rand theo seed 42/43/44 trên 30.033 dòng, kiểm đúng quy tắc loại donor retrieved của B2.
- Phân biệt donor/prompt phiên cũ với phiên frozen mới.

## Thay đổi đã thực hiện

Thêm [audit_frozen_donor_scope.py](../Runs-management/audit_frozen_donor_scope.py), [audit_random_selection.py](../Runs-management/audit_random_selection.py) và các JSON đối chiếu.

## Kết quả và bằng chứng

- Code/label/ID donor frozen đạt kiểm tra; 30.033 lựa chọn random đều khớp, không có mismatch.
- Phát hiện 21 target Devign phiên B2 cũ dùng donor ngoài bank frozen mới; giữ bằng chứng và phân biệt phiên, không ghi lại lịch sử thành đã dùng bank mới.
- [Donor scope](../Runs-management/prompt_audit_20261102/donor_scope.json), [random selection](../Runs-management/prompt_audit_20261102/random_selection.json).

## Giới hạn

Không chạy retrieval hoặc inference mới trong việc kiểm này. Kết quả không thay thế kế hoạch chuyển donor và score bổ sung ở các run tương ứng.
