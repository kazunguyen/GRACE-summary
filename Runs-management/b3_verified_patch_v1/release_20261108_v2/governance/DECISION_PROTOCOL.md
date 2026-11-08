# Protocol Decisions & Governance Record for Amended B3 (v2 Remediated)

**Date:** 2026-11-08T13:03:58.677256 (UTC: 2026-11-08T06:03:58.677256+00:00)  
**Mốc mã nguồn:** Git commit `46e6f4ab9d0ff2c9ecac124d3a6f2bdb72524bd9`  
**Tài liệu thẩm quyền:** `docs/OSF_response/De_cuong_nghien_cuu_GRACE_hop_nhat.docx`, `docs/OSF-update-20261107.pdf`  

## 1. Phân loại phương pháp và Trạng thái OSF
- **Phương pháp B3 mới:** Thuật toán ghép cặp có kiểm chứng `b3-verified-patch-v1` (`VerifiedPairSelector`), thay thế toàn bộ cơ chế heuristic bề mặt cũ.
- **Trạng thái OSF:** Bản cập nhật minh bạch đã được nộp lên OSF vào ngày 07/11/2026 (`docs/OSF-update-20261107.pdf`). Tại thời điểm phát hành này, bản nộp đang ở trạng thái `SUBMITTED_AMENDMENT_PENDING_REGISTRATION_STAMP` (chờ đóng dấu xét duyệt chính thức của OSF). Phương pháp được theo dõi dưới nhánh thực nghiệm điều chỉnh (amended track), tách biệt hoàn toàn khỏi bản đăng ký gốc đóng băng `prereg-v1` (https://osf.io/fqgh2).
- **Ngưỡng quyết định (tau*):** Ngưỡng tối ưu của B3 mới BẮT BUỘC phải được tính độc lập trên tập full validation của chính run mới (argmax MCC trên lưới 99 điểm tau in [0.01, 0.99]). TUYỆT ĐỐI không kế thừa hay tái sử dụng ngưỡng lịch sử của B3 cũ.
- **Kế thừa cho Probes:** B3-swap và B3-flip sẽ kế thừa trực tiếp tau* từ B3 mới. B3-nodiff tính ngưỡng riêng trên validation của chính nó.

## 2. Phân tách rõ ràng giữa Triage tự động và Thẩm định con người
- **Automated Technical Triage:** Do script tự động thực hiện nhằm kiểm tra các tiêu chí cơ học (commit hash hợp lệ, quan hệ cha-con trong git, danh sách file thay đổi, diff thực tế). Kết quả triage được ghi nhận rõ là triage kỹ thuật tự động (`AUTOMATED_TECHNICAL_TRIAGE`), tuyệt đối KHÔNG gán tên con người hay sinh bình luận/chữ ký giả lập.
- **Independent Dual Human Review:** Khi ứng viên vượt qua các cổng kỹ thuật và có đầy đủ bằng chứng mã nguồn gốc, hai thẩm định viên (Hiếu & Dũng) sẽ độc lập điền phiếu duyệt riêng, ký xác nhận trên mã băm bằng chứng (`payload_sha256`).

## 3. Ngân sách Demonstration
- Căn cứ văn bản đề cương hợp nhất (`De_cuong_nghien_cuu_GRACE_hop_nhat.docx`, Đoạn 88):
  * Code target <= 3.000 tokens.
  * **Mỗi demonstration <= 1.500 tokens** (`budget_each = 1500`).
  * Đồ thị CPG <= 1.500 tokens.
  * Ngăn dự phòng: 64 tokens.
  * Tổng prompt sau chat template <= 8.192 tokens.
