# Hồ Sơ Đăng Ký Trước OSF (OSF Preregistration Pack)

**Trạng thái:** SẴN SÀNG NỘP LÊN OSF REGISTRIES (READY FOR OSF REGISTRY SUBMISSION)  
**Mã hồ sơ:** `grace_diag_replication_v1`  
**Phiên bản:** `prereg-v2-15arms`  
**Ngày hoàn thiện gói nộp:** 2026-11-02 (UTC)  

Bản Markdown nháp cũ `OSF_DRAFT.md` đã được chuyển vào `../osf_drafts_pending_delete_20261103/` để chờ xóa. PDF/ZIP preregistration chính là deliverable; trạng thái ở đây là sẵn sàng nộp, chưa phải hồ sơ đã được OSF xác nhận.

---

## 1. Danh Mục Tệp Nộp Chính (Submission Deliverables)

1. **Tệp PDF văn bản đăng ký chính thức:**
   - Đường dẫn: `output/pdf/GRACE_OSF_PREREGISTRATION_20261102.pdf` (bản copy tương thích ngược đã được chuyển vào `../osf_drafts_pending_delete_20261103/GRACE_OSF_DRAFT_20261102.pdf` để chờ xóa).
   - Được biên dịch tự động từ `preregistration.md` qua ReportLab với font Arial Unicode đầy đủ, có tiêu đề đầu trang và đánh số trang.
2. **Gói ZIP mã nguồn & cấu hình độc lập (Stand-alone Reproducible Archive):**
   - Đường dẫn: `GRACE_OSF_PREREGISTRATION_20261102.zip` (và bản copy tương thích ngược `GRACE_OSF_DRAFT_20261102.zip`).
   - Chứa toàn bộ 30 tệp: tài liệu đăng ký, cấu hình protocol, 14 ngưỡng tối ưu đã khóa, manifest phân tích, báo cáo chẩn đoán Bước 0 (5.000 bootstrap reps), kết quả audit dry-run 15 arm (95.095 prompts rendered, 0 rò rỉ nhãn, 0 LLM calls), và mã nguồn kiểm định.
3. **Bảng mã băm kiểm toán (Audit Hash Table):**
   - Đường dẫn: `attachment_sha256.json`.
   - Ghi nhận kích thước bytes và mã băm SHA-256 của từng tệp trong gói nộp.
4. **Cẩm nang hướng dẫn nộp từng bước:**
   - Đường dẫn: `docs/OSF_SUBMISSION_GUIDE.md`.

---

## 2. Hướng Dẫn Thao Tác Trên OSF Registries

1. Đăng nhập vào: **[https://osf.io/registries](https://osf.io/registries)**
2. Tạo mới Registration, chọn template **OSF Preregistration**.
3. Điền các mục thông tin, giả thuyết H1–H6, và kế hoạch phân tích theo chỉ dẫn chi tiết trong `docs/OSF_SUBMISSION_GUIDE.md`.
4. Đính kèm tệp PDF `output/pdf/GRACE_OSF_PREREGISTRATION_20261102.pdf` và tệp ZIP `GRACE_OSF_PREREGISTRATION_20261102.zip`.
5. Sau khi gửi (Submit), xác nhận phê duyệt qua email của các tác giả.
6. Sau khi hồ sơ được OSF phê duyệt (Approved/Active), tạo git tag `prereg-v2-15arms`.
7. **Cam kết Zero-Test-Exposure:** Tuyệt đối không chạy suy luận trên tập Test trước khi nhận email xác nhận chính thức từ OSF Registries.
