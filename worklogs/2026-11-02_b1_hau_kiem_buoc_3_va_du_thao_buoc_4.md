---
id: "b1-step34-20261102"
title: "Hậu kiểm B1 và chuẩn bị hồ sơ bước 3–4 sau inference"
author: "Codex (trợ lý AI)"
author_type: "AI assistant"
requested_by: "Người dùng trong chat"
recorded_at: "2026-11-02T22:46:24+07:00"
timezone: "Asia/Bangkok"
work_date: "2026-11-02"
record_type: "retrospective_worklog"
status: "automatic_checks_complete_human_review_and_registration_pending"
---

# Hậu kiểm B1 và chuẩn bị hồ sơ bước 3–4 sau inference

Thời điểm trên là lúc lập artifact, không phải ngày inference hay ngày đăng ký OSF. Phạm vi yêu cầu là arm B1; người dùng đã bỏ yêu cầu sửa notebook.

## Bước 3 — việc đã làm

- Đối chiếu toàn bộ 10.011 prompt với hash của audit token pin đã có; kiểm lại từng prompt, ID/nhãn/hash, scaffold demo, checkpoint ZIP, record và score so với hai logprob. So 5.434 record lượt I-07 với I-08; không có thay đổi.
- 0 mẫu chứa demo theo metadata và scaffold, 0 score/logprob sai, 5 raw response không hợp lệ; các graph thiếu được gắn cờ. Kiểm tra tự động không thay thế đánh giá ngữ nghĩa bằng người và là hậu kiểm.
- Chuẩn bị 60 prompt B1 validation, 30/dataset, phân tầng độ dài và ưu tiên cờ graph thiếu/code cắt; tạo hai phiếu trống và hướng dẫn. Bộ này bổ sung, không thay bộ mẫu toàn nghiên cứu trước đó.
- [Báo cáo](../Runs-management/b1_step34_20261102/BUOC_3_B1_HAU_KIEM.md), [kết quả và hash](../Runs-management/b1_step34_20261102/b1_posthoc_audit.json), [packet](../Runs-management/b1_step34_20261102/manual_packet_b1.md), [phiếu 1](../Runs-management/b1_step34_20261102/reviewer_1.csv), [phiếu 2](../Runs-management/b1_step34_20261102/reviewer_2.csv).

## Bước 4 — việc đã làm

- Soạn [phụ lục B1 dự thảo OSF](../Runs-management/b1_step34_20261102/BUOC_4_B1_PHU_LUC_OSF_DRAFT.md), ghi cấu hình, số lượng và thời điểm thật, kiểm toán hậu kỳ, thiếu bằng chứng khóa ngưỡng trước test và tiếp xúc dữ liệu.
- Giữ nguyên snapshot/hồ sơ niêm phong và bản OSF cũ; ghi rõ bản OSF tổng cần cập nhật vì tiến độ cũ đã lạc hậu. Không gửi OSF, không tạo ngày/URL đăng ký, không tính/ghi khóa tau mới.

## Còn lại và giới hạn

Người dùng sẽ bổ sung hai người đánh giá; hai phiếu chưa được điền và chưa có phân xử. Bước 3 toàn nghiên cứu còn phụ thuộc các arm và nghiệm thu đã ghi ở tài liệu hiện hành. Bước 4 cần chủ nhiệm duyệt và chốt thông tin/endpoint đang pending, cập nhật hồ sơ nghiên cứu tổng, rồi đăng ký OSF theo quyết định của người dùng. Không thể biến hậu kiểm/thời điểm hiện tại thành audit, khóa hay đăng ký đã xảy ra trước inference/test.
