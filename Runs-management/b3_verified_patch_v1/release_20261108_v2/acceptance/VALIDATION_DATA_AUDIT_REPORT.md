# BÁO CÁO NGHIỆM THU DỮ LIỆU B3 (REMEDIATED VALIDATION DATA AUDIT REPORT)

**Ngày nghiệm thu:** 08/11/2026  
**Phiên bản phát hành:** `v2_remediated`  
**Giao thức thực thi:** `docs/B3_NEW_ALGORITHM_EXECUTION_PLAN_20261108.md` (Bước 1 đến Bước 8)  
**Tài liệu khắc phục kiểm toán:** `Runs-management/b3_verified_patch_v1/independent_audit_20261108_122320/AUDIT_REPORT.md`  
**Mã băm niêm phong đầu vào (Inputs Seal):** `95eb4ee991da3fbf4010652a6bbb6e2ddccb29a8744d81d154bb9d405642592e`  
**Mã băm niêm phong Pool (Pool Seal):** `43232ef4969c5202d25e83f79de004f06b32eed836747e594b5528ba173dffe7`  
**Mã băm niêm phong Prompt Manifest (Prompt Seal):** `9ea703314fefb6cb6aa0aaa0adaf4849f131c064d52332dfb8a97c202bcd0cde`  

---

## 1. TỔNG HỢP TIẾN ĐỘ VÀ KẾT QUẢ THỰC TẾ (BƯỚC 1 ĐẾN BƯỚC 8)

| Bước | Nội dung công việc | Trạng thái thực tế | Đánh giá kiểm toán & Ghi chú |
|---|---|---|---|
| **Bước 1** | Lập snapshot nguồn, kiểm tra ràng buộc ngân sách & hợp đồng đóng băng | **PASS** | Đã kiểm tra đúng 21.691 Devign và 17.636 REVEAL clean train donors. Tokenizer `b2cff6...` đúng hash. Niêm phong đầy đủ mã module, script thực thi và tài liệu thẩm quyền. Ghi nhận trung thực tình trạng nộp cập nhật OSF (`SUBMITTED_AMENDMENT_PENDING_REGISTRATION_STAMP`). |
| **Bước 2** | Khắc phục TLS (certifi) và rà soát commit git upstream | **PASS** | Cấu hình CA bundle `certifi.where()`. Thực hiện rà soát đủ 17 commit duy nhất cho 12 cặp ứng viên Devign. Tách biệt rõ ràng log cache replay và network call. |
| **Bước 3** | Điều tra cặp Devign candidate, lập hồ sơ bằng chứng git | **BLOCKED** | Điều tra 12 ca ứng viên ưu tiên. Đã trích xuất commit cha, danh sách file thay đổi và commit message cho cả 2 phía. Xác nhận 0/12 ca có quan hệ cha-con cùng hàm; 0 cặp được chấp nhận. Bounded scope: không tuyên bố phủ định trên toàn bộ bank. |
| **Bước 4** | Khảo sát phục hồi provenance REVEAL | **BLOCKED** | Toàn bộ 17.636 donor trong clean train export thiếu commit ID và file path. Hồ sơ ghi nhận trạng thái `BLOCKED_UNRESOLVED_PROVENANCE` với phạm vi kiểm kê cụ thể; không dùng nhận định chưa kiểm chứng. |
| **Bước 5** | Tạo pair candidate từ bằng chứng nguồn thật | **BLOCKED** | Bỏ hoàn toàn dummy fix diff trong luồng dữ liệu thật. Do không có ca nào có git diff thực tế kết nối 2 hàm donor, 0 candidate được tạo (`candidates.jsonl` rỗng). Toàn bộ lý do không đủ điều kiện được ghi nhận tại `candidate_ineligibility_records.jsonl`. |
| **Bước 6** | Triage kỹ thuật tự động và niêm phong eligible pool | **BLOCKED** | Tách bạch hoàn toàn triage kỹ thuật tự động khỏi thẩm định con người. 12/12 ca bị loại ở bước triage tự động; 0 ca được gửi thẩm định con người; không tự sinh nhận xét hay chữ ký giả lập. Pool Devign và REVEAL đều rỗng (0 pair). |
| **Bước 7** | Kiểm tra `VerifiedPairSelector`, renderer và các cổng an toàn | **PASS** | Chạy toàn bộ 4 bộ test suites (58 passed, 0 skipped). Kiểm tra cổng an toàn: cơ chế dừng khi pool rỗng, cấm rò rỉ nhãn, exact rational Fraction, và Figure 6 prompt ordering. |
| **Bước 8** | Dựng và kiểm toán census validation (5.005 target) | **PAUSED** | Quét đủ 2.732 Devign + 2.273 REVEAL targets. 100% ID duy nhất, khớp tuyệt đối code validation raw sau `.strip()`, 0 rò rỉ nhãn. Ghi nhận trạng thái `PAUSED` có kiểm soát do pool rỗng; không gán cờ Figure 6 / không rò rỉ khi prompt rỗng. |

---

## 2. KẾT LUẬN KHOA HỌC VÀ TUÂN THỦ NGUYÊN TẮC LIÊM CHÍNH OSF

1. **Dừng an toàn có kiểm soát (Safe Pause):**
   - Thuật toán B3 mới (`b3-verified-patch-v1`) yêu cầu cặp tương phản phải là bản vá lỗi bảo mật thực tế của cùng một hàm giữa commit sửa lỗi và commit cha (`fix_commit != parent_commit`).
   - Rà soát trong phạm vi 12 ca ứng viên Devign và kiểm kê 17.636 donor REVEAL xác nhận hiện chưa xác thực được cặp bản vá lỗi nhân quả nào.
   - Việc không khởi chạy GPU inference khi pool rỗng là quyết định khoa học đúng đắn nhất: **tuyệt đối không bịa đặt dữ liệu (no fabrication)**, không dùng dữ liệu giả lập cho inference thật, không hạ chuẩn lựa chọn.

2. **Khắc phục toàn diện các phát hiện kiểm toán (Audit Findings F01–F07):**
   - Đã loại bỏ toàn bộ hồ sơ tự sinh gán chữ ký người duyệt (F01).
   - Đã chuẩn hóa kết luận theo đúng phạm vi điều tra thực tế (F02).
   - Đã sửa trạng thái census validation thành `PAUSED` và `NOT_EVALUATED_BLOCKED_EMPTY_POOL` cho prompt rỗng (F03).
   - Đã loại bỏ diff giả lập khỏi luồng dữ liệu thật (F04).
   - Đã kiểm kê và ghi nhận trung thực hiện trạng provenance REVEAL (F05).
   - Đã thiết lập cổng nghiệm thu fail-closed và tách biệt logging cache/network (F06).
   - Đã cập nhật đúng trạng thái đề xuất cập nhật OSF (F07).
