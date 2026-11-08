# Protocol Decisions & Governance Record for Amended B3

**Date:** 2026-11-08T12:02:36.866282 (UTC: 2026-11-08T05:02:36.866282+00:00)  
**Mốc mã nguồn:** Git commit `46e6f4ab9d0ff2c9ecac124d3a6f2bdb72524bd9`  
**Tài liệu thẩm quyền:** `docs/OSF_response/De_cuong_nghien_cuu_GRACE_hop_nhat.docx`, `docs/OSF-update-20261107.pdf`  

## 1. Phân loại phương pháp và Ngưỡng mới (Decision on Method & Thresholds)
- **Phương pháp B3 mới:** Thuật toán ghép cặp có kiểm chứng `b3-verified-patch-v1` (`VerifiedPairSelector`), thay thế toàn bộ cơ chế heuristic bề mặt cũ.
- **Tình trạng OSF:** Bản cập nhật minh bạch đã được nộp chính thức lên OSF vào ngày 07/11/2026 (`docs/OSF-update-20261107.pdf`).
- **Ngưỡng quyết định (tau*):** Ngưỡng tối ưu của B3 mới BẮT BUỘC phải được tính độc lập trên tập full validation của chính run mới (argmax MCC trên lưới 99 điểm tau in [0.01, 0.99]). TUYỆT ĐỐI không kế thừa hay tái sử dụng ngưỡng lịch sử của B3 cũ.
- **Kế thừa cho Probes:** B3-swap và B3-flip sẽ kế thừa trực tiếp tau* từ B3 mới. B3-nodiff tính ngưỡng riêng trên validation của chính nó.

## 2. Ngân sách Demonstration (Demonstration Budget Interpretation)
- Căn cứ văn bản đề cương hợp nhất (`De_cuong_nghien_cuu_GRACE_hop_nhat.docx`, Đoạn 88):
  * Code target <= 3.000 tokens.
  * **Mỗi demonstration <= 1.500 tokens** (`budget_each = 1500`).
  * Đồ thị CPG <= 1.500 tokens.
  * Ngăn dự phòng: 64 tokens.
  * Tổng prompt sau chat template <= 8.192 tokens.
- Cổng audit kiểm tra nghiêm ngặt: hai hàm demo và khối `Key difference` không được phép bị cắt xén làm mất bằng chứng nhân quả.

## 3. Phân công thẩm định độc lập 2 người thật (Dual Reviewers)
- Người kiểm tra 1: **Hiếu**
- Người kiểm tra 2: **Dũng**
- Cả hai đánh giá độc lập 4 tiêu chí cốt lõi: `same_function_verified`, `security_fix_verified`, `source_revisions_verified`, `explanation_supported`.
