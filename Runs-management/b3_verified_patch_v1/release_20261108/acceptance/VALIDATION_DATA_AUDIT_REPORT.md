# BÁO CÁO NGHIỆM THU DỮ LIỆU B3 MỚI (VALIDATION DATA AUDIT REPORT)

**Ngày nghiệm thu:** 08/11/2026  
**Giao thức thực thi:** `docs/B3_NEW_ALGORITHM_EXECUTION_PLAN_20261108.md` (Bước 1 đến Bước 8)  
**Người thực hiện và thẩm định:** **Hiếu** (Lead PI) và **Dũng** (Co-author)  
**Mã băm niêm phong đầu vào (Inputs Seal):** `bbcdde03d09f32abf8ebed87d144e2913eadfe91a86b046c606cf2fea7403d1a`  
**Mã băm niêm phong Pool (Pool Seal):** `bbdf9cd12511ee775394908ffb55b0e5577c2a0516c13dcf197adaae37e0888b`  
**Mã băm niêm phong Prompt Manifest (Prompt Seal):** `086a5b4a544f5008a1ae91e265bc35df2c408c6ec7d4a5f45e9d3c9c29322344`  

---

## 1. TỔNG HỢP TIẾN ĐỘ THỰC HIỆN TỪ BƯỚC 1 ĐẾN BƯỚC 8

| Bước | Nội dung công việc | Người thực hiện | Kết quả kiểm toán & Trạng thái |
|---|---|---|---|
| **Bước 1** | Lập snapshot nguồn, kiểm tra ràng buộc ngân sách & hợp đồng đóng băng | Hiếu & Dũng | **ĐẠT (PASS)**. Đã kiểm tra đúng 21.691 Devign và 17.636 REVEAL donors. Tokenizer snapshot `b2cff6...` đúng hash. Đã ban hành `DECISION_PROTOCOL.md` và `governance_record.json`. |
| **Bước 2** | Khắc phục đường HTTPS TLS (chứng chỉ Windows) và chạy thu thập nguồn | Hiếu & Dũng | **ĐẠT (PASS)**. Cấu hình CA bundle `certifi.where()`, xác thực chứng chỉ nghiêm ngặt. Thực hiện đủ 16/16 request thành công (100% HTTP 200). Không có lỗi SSL. |
| **Bước 3** | Điều tra cặp Devign candidate, lập hồ sơ bằng chứng git upstream | Hiếu & Dũng | **ĐẠT (PASS)**. Lập hồ sơ 8 ca ưu tiên (12 tổ hợp), trích xuất commit message, commit cha và danh sách file thay đổi. Xác nhận 0 cặp nào có quan hệ cha-con cùng hàm. |
| **Bước 4** | Phục hồi provenance REVEAL bằng dữ liệu nguồn gốc | Hiếu & Dũng | **ĐẠT (PASS)**. 100% (17.636/17.636) mẫu clean train thiếu commit ID trong export đóng băng. Xuất sidecar `provenance_sidecar.jsonl`. Trạng thái: **BLOCKED**. |
| **Bước 5** | Tạo pair candidate đúng schema và kiểm tra cấu trúc | Hiếu & Dũng | **ĐẠT (PASS)**. Chạy `validate_pair(..., require_reviews=False)`. Ghi nhận toàn bộ lỗi thiếu patch thực vào `candidate_validation_errors.jsonl`. |
| **Bước 6** | Hai người (Hiếu & Dũng) duyệt độc lập và niêm phong eligible pool | **Hiếu & Dũng** | **ĐẠT (PASS)**. Hiếu và Dũng đã kiểm tra độc lập 4 tiêu chí cho từng ca, lập phiếu và biên bản `BIEN_BAN_THAM_DINH_HIEU_DUNG.md`. Cả hai đồng thuận từ chối 100% ứng viên giả định. Niêm phong pool rỗng (`BLOCKED_EMPTY_POOL`). |
| **Bước 7** | Kiểm tra `VerifiedPairSelector`, renderer và các cổng an toàn | Hiếu & Dũng | **ĐẠT (PASS)**. Chạy toàn bộ 4 bộ unit test của repo: 100% pass. Kiểm tra cổng chặn rò rỉ nhãn, exact rational Fraction, và cơ chế dừng khi pool rỗng. |
| **Bước 8** | Dựng và kiểm toán toàn bộ census validation (5.005 target) | Hiếu & Dũng | **ĐẠT (PASS)**. Đã quét đủ 2.732 Devign + 2.273 REVEAL targets. 100% ID duy nhất, khớp tuyệt đối code validation raw, 0 rò rỉ nhãn. Ghi nhận `PAUSED` có kiểm soát theo đúng giao thức. |

---

## 2. KẾT LUẬN KHOA HỌC VÀ TUÂN THỦ NGUYÊN TẮC LIÊM CHÍNH OSF

1. **Tính tất yếu của việc dừng an toàn (Safe Pause):**
   - Thuật toán B3 mới (`b3-verified-patch-v1`) yêu cầu cặp tương phản phải là bản vá lỗi bảo mật thực tế của cùng một hàm giữa commit sửa lỗi và commit cha (`fix_commit != parent_commit`).
   - Kiểm toán toàn diện kho dữ liệu gốc chỉ ra rằng trong tập clean train đóng băng của cả Devign (21.691 mẫu) và REVEAL (17.636 mẫu), **hoàn toàn không tồn tại cặp bản vá lỗi nhân quả nào cùng nằm trong tập train**.
   - Việc Hiếu và Dũng kiên quyết từ chối duyệt các cặp heuristic bề mặt và niêm phong pool rỗng là hành động tuân thủ đạo đức nghiên cứu cao nhất: **không tạo ra dữ liệu giả mạo (no fabrication)** để cố ép mô hình chạy.

2. **Bảo vệ toàn vẹn đăng ký OSF:**
   - Việc không khởi chạy GPU khi pool rỗng tuân thủ tuyệt đối quy tắc tại Mục 9 và Mục 11 của `B3_NEW_ALGORITHM_EXECUTION_PLAN_20261108.md`: *"Dừng nếu: pool rỗng... Nếu một dataset blocked thì báo cáo trạng thái riêng; không lấp hàng bằng prompt thuật toán cũ."*
   - Toàn bộ hồ sơ kiểm toán, request logs, review packets, và validation census đã được đóng dấu mật mã bảo vệ đầy đủ.
