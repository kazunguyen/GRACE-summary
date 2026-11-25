# Báo cáo tuần GRACE: 11/11–25/11/2026

Gộp hai tuần 11–17/11 và 18–24/11, cộng ngày 25/11. *[Nếu các tuần trước chưa gửi báo cáo: nhóm xin nhận thiếu sót. Bỏ câu này nếu đã báo cáo qua kênh khác.]*

## 1. Prompt test đã chạy / còn lại

- Đủ test cho mọi arm trong phạm vi Option 1: Devign 2.732, ReVeal 2.274 mỗi arm và mỗi seed. Tổng 30 nhóm test (75.090 records) và 30 nhóm validation (75.075 records). Không còn prompt nào chưa chạy.
- Lượt GPU cuối: B3-swap và B3-flip ngày 11/11, chạy sau quyết định dừng nhóm B3 (sai lệch D7). Hai lượt này chỉ dùng làm thăm dò, không vào Bảng B. Lý do không hủy kịp: *[nhóm bổ sung]*.
- Không chạy GPU sau 11/11.

## 2. Bảng và hình đã sinh

- **M1 đã đủ.** Bảng A/B/C với hai bộ ngưỡng: `runs/tables_prereg/`, `runs/tables_corrected/`. Sinh bằng chuỗi lệnh của kit v1.2 (`import_records → thresholds --compare → evaluate_final`). Ngưỡng có phiên bản: `configs/thresholds_corrected.json`.
- **Đối soát:**
  - Lê Anh Duy đối soát độc lập Bảng A–C, tự tính lại từ records (`worklogs/2026-11-13_pa1_doi_soat_doc_lap_le_anh_duy.md`).
  - Dựng lại bảng trong môi trường sạch (Python 3.10.11): 12/12 file số liệu trùng byte.
  - Bảng đối soát số giữa các báo cáo: `Runs-management/analysis_checks_20261112/reconciliation/REPORT.md`.
- **Kiểm chứng theo mục 2.2 của bản đánh giá 11/11:**
  - B2-rep: điểm trùng B2 ở 100% mẫu, là lượt gọi model mới, không lấy từ cache.
  - B2-rand ReVeal: không có mẫu nào được chấm dưới cả hai runtime; seed 44 cho cùng kết luận.
  - B1-full: không cần chạy lại validation (graph khớp 5.005/5.005 prompt).
  - Đã có phân tầng B1-H2, ppr@0,5, CI cho ΔAUPRC.
  - Bảng sai lệch ba dòng: 14 mục, D1–D14 (`Runs-management/analysis_checks_20261112/DEVIATIONS_TABLE.md`).
- **Step 6 chạy lại bằng B2 chuẩn (25/11):**
  - Lock Step 6 cũ dùng B2 trước khi đổi donor 66 dòng (Devign validation 28, test 38).
  - Bản đối chứng tái tạo đúng kết quả cũ (985/985 trường), nên script hiện tại tương đương bản đã chạy.
  - Với B2 chuẩn, Devign Bảng D ΔMCC đổi từ −0,0008 [−0,0095; 0,0080] thành −0,0016 [−0,0107; 0,0075]; sửa/gây thêm lỗi từ 397/718 thành 400/716. Mọi phán quyết không đổi; ReVeal không đổi.
  - Tiêu chí H5.3 tính theo phân vị 95 như văn bản đăng ký vẫn đạt (Devign 400 ≤ 464,0; ReVeal 164 ≤ 173,3).
  - **Dũng đối soát độc lập (25/11): 5/5 hạng mục đạt**, tái chạy trên WSL khớp đến 10 chữ số thập phân (`worklogs/2026-11-25_dung_doi_soat_doc_lap_step6_b2_chuan.md`).
  - Kết quả: `STEP6_supervised_anchors/runs/complementarity_step6/step6_lock_64fb2c99d904_rerun_canonical_b2_20261125/`.
- **Bước 8:** chấm mù thăm dò 30 ca, hai người chấm độc lập; κ = 1,00; 30/30 ca chọn demo truy hồi. Kết quả mô tả; H6.1 để Giai đoạn 2.
- **Bản thảo v1** xong ngày 13/11, kèm 4 hình và evidence (`[Official]-Paper/`).

## 3. Ba việc tuần tới (đến 03/12)

1. Sửa bản thảo theo góp ý của thầy; cập nhật Bảng D và §4.5 theo B2 chuẩn; chuyển sang template hội thảo.
2. Đóng gói artifact (records, ngưỡng, scripts, bảng) lên OSF/GitHub; merge nhánh tổng hợp `docs/phase1-consolidation-20261125` vào `baseline-unified`.
3. Đề cương chi tiết khóa luận, chương 1–5.

## 4. Cần thầy quyết định

1. Kết quả Step 6 bằng B2 chuẩn đã được hai người kiểm độc lập. Nhóm đề nghị dùng làm số chính trong bài, thay cho lock cũ.
2. Góp ý cho bản thảo v1 (đã gửi 14/11) để nhóm sửa kịp trước 03/12.
3. Venue và template cho bản nộp 03/12: *[điền tên hội thảo]*.
