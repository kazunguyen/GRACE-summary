---
author: [Dũng, Hiếu]
reviewer: Codex
date: 2026-11-05
---

# Rà nội dung prompt B2-rand

Dũng và Hiếu đứng tên chủ hồ sơ. Nguồn verdict là lượt chấm nội dung của Codex ngày 04/11 trong [phiếu 10 arm](../11_Arm_B1H2_Evidence/audit/hieu_zip_step34_20261104/validation_manual_review_10arms/reviewer_codex.csv). Ngày 05/11, Codex đối chiếu lại trực tiếp từng prompt theo dataset, seed, ID và SHA-256 của nội dung trong bundle Kaggle. Cả 10 mẫu đều khớp.

## Kết quả trên mẫu

9 pass, 1 unclear. Phiếu nguồn ghi cả 10 mẫu pass tiêu chí không rò nhãn target. Đây là kết quả trên mẫu, khác với audit tự động toàn bộ 15.015 prompt validation.

| Dataset | Seed | ID | Verdict | Nhận xét từ phiếu nguồn |
|---|---:|---|---|---|
| reveal | 42 | reveal:validation:19 | pass | Demo macro HB đến từ donor random, nhãn hiển thị 0 khớp evidence. |
| reveal | 44 | reveal:validation:1240 | unclear | Demo random hiển thị nhãn thật 0. Target cắt ngay sau nhánh fallback LMBCS, chưa xác nhận phần sau không thiết yếu. |
| devign | 43 | devign:validation:9198 | pass | Demo random có code hoàn chỉnh tới nhánh fill_buffer và nhãn hiển thị 0 khớp evidence. |
| reveal | 42 | reveal:validation:1307 | pass | Code target khớp frozen validation. Kiểm khối prefix và demo random theo arm. |
| reveal | 44 | reveal:validation:1587 | pass | Code target khớp frozen validation. Kiểm khối prefix và demo random theo arm. |
| devign | 42 | devign:validation:20472 | pass | Code target khớp frozen validation. Kiểm khối prefix và demo random theo arm. |
| devign | 44 | devign:validation:11343 | pass | Code target khớp frozen validation. Kiểm khối prefix và demo random theo arm. |
| devign | 43 | devign:validation:6202 | pass | Code target khớp frozen validation. Kiểm khối prefix và demo random theo arm. |
| reveal | 43 | reveal:validation:1880 | pass | Code target khớp frozen validation. Kiểm khối prefix và demo random theo arm. |
| reveal | 44 | reveal:validation:1215 | pass | Code target khớp frozen validation. Kiểm khối prefix và demo random theo arm. |

Codex đọc lại phần target của mẫu LMBCS seed 44. Phần code hiển thị dừng giữa điều kiện ở nhánh chuyển đổi. Giữ verdict unclear vì chưa đủ căn cứ đánh giá phần bị cắt có làm mất ngữ cảnh thiết yếu hay không.

Hồ sơ này là rà nội dung do AI thực hiện. Xác nhận của hai người đánh giá độc lập cho bộ mẫu hiện hành vẫn cần phiếu do từng người tự điền.
