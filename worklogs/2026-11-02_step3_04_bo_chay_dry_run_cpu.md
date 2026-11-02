---
id: "step3-20261102-04"
title: "Xây dựng bộ chạy dry-run CPU cho phiên prompt hiện tại"
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

# Xây dựng bộ chạy dry-run CPU cho phiên prompt hiện tại

Ghi lại công việc đã thực hiện trước đó. recorded_at là thời điểm lập worklog; evidence_verified_at (nếu có) là mốc kiểm chứng của artifact, không phải thời gian bắt đầu/kết thúc chạy.

## Việc đã làm

- Tạo bộ chạy dùng render_arm và audit_rows chung, tokenizer Qwen pinned offline, ngân sách context 8.192 và graph 40 node/80 edge, tối đa 1.500 token.
- Giữ scaffold trống B0/B1; tái dùng prefix graph đã kiểm hash/tái dựng; đọc graph donor bằng lazy index để tránh nạp toàn bank CPG vào RAM.
- Dừng lượt worker thread dở vì chậm, lưu riêng bằng chứng rồi chuyển sang các process CPU. Giữ nguyên thuật toán renderer/tokenizer.

## Thay đổi đã thực hiện

Thêm [dry_run_full_validation.py](../Runs-management/dry_run_full_validation.py), [test_full_validation_dry_run.py](../Runs-management/test_full_validation_dry_run.py) và [verify_full_validation_dry_run.py](../Runs-management/verify_full_validation_dry_run.py).

## Kết quả và bằng chứng

- Bộ test probe đạt 20/20; bốn test bổ sung cho bộ chạy đạt 4/4.
- Kiểm scaffold, chặn nhãn target, compact graph, selector và chính sách graph thiếu; lượt chạy thật được ghi ở log 05.
- [Kết quả test trong verification](../Runs-management/dry_run_validation_20261102/verification.json), [lượt thread dở](../Runs-management/dry_run_validation_20261102_interrupted_threads/ATTEMPT_STATUS.json), [lệnh tái tạo](../Runs-management/dry_run_validation_20261102/README.md).

## Giới hạn

Đây là adapter CPU cho phạm vi đầu vào hiện có. Không sửa runtime notebook B2 hoặc tính ngưỡng; kết quả test này không có nghĩa toàn bộ test notebook đã xanh.
