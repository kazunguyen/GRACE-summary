---
id: "step3-20261102-07"
title: "Chuẩn bị bộ mẫu và phiếu cho hai người đọc độc lập"
author: "Codex (trợ lý AI)"
author_type: "AI assistant"
requested_by: "Người dùng trong chat"
recorded_at: "2026-11-02T18:13:39+07:00"
timezone: "Asia/Bangkok"
work_date: "2026-11-02"
record_type: "retrospective_worklog"
status: "prepared_pending_human_review"
overall_step3_status: "incomplete"
evidence_verified_at: "2026-11-02T17:52:40.257851+07:00"
---

# Chuẩn bị bộ mẫu và phiếu cho hai người đọc độc lập

Ghi lại công việc đã thực hiện trước đó. recorded_at là thời điểm lập worklog; evidence_verified_at (nếu có) là mốc kiểm chứng của artifact, không phải thời gian bắt đầu/kết thúc chạy.

## Việc đã làm

- Tạo bộ 60 prompt đúng phiên dry-run: 30 Devign và 30 REVEAL.
- Chọn mẫu seed 42, có đại diện từng arm/seed, phân tầng độ dài và cờ cắt; không chọn theo score/metric.
- Tạo packet đọc có hash/đường dẫn nguồn, rubric cho mười arm và hai phiếu CSV riêng để trống.
- Nêu rõ graph donor ở B1-shuf, scaffold trống và các biến thể nolabel/labelonly/flip/rep để người đọc chấm theo đúng thiết kế.

## Thay đổi và bằng chứng

- [Packet 60 prompt](../Runs-management/dry_run_validation_20261102/manual_packet.md), [mẫu JSONL](../Runs-management/dry_run_validation_20261102/manual_sample.jsonl).
- [Rubric](../Runs-management/dry_run_validation_20261102/RUBRIC.md), [phiếu người 1](../Runs-management/dry_run_validation_20261102/reviewer_1.csv), [phiếu người 2](../Runs-management/dry_run_validation_20261102/reviewer_2.csv).
- [Verification](../Runs-management/dry_run_validation_20261102/verification.json) xác nhận đủ 30 mẫu/dataset, đúng hash nguồn và chưa có đánh giá được điền.

## Trạng thái còn lại

Đã hoàn tất chuẩn bị hồ sơ; chưa có hai người đọc thực tế, chưa có verdict hoặc biên bản phân xử. Mỗi người cần đọc cùng 60 prompt và nộp phiếu độc lập trước khi đối chiếu bất đồng. Khi mở đủ 15 arm cần bảo đảm phạm vi mẫu tương ứng; bộ hiện tại chỉ bao phủ mười arm đã dựng.
