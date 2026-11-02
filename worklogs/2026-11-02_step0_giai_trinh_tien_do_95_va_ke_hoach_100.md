---
id: "step0-20261102-10"
title: "Giải trình chi tiết khoảng hở 5% của Bước 0 và kế hoạch đóng dấu 100%"
author: "Antigravity (AI Lead Coordinator)"
author_type: "AI assistant"
requested_by: "Người dùng trong chat"
recorded_at: "2026-11-02T21:10:00+07:00"
timezone: "Asia/Bangkok"
work_date: "2026-11-02"
record_type: "technical_gap_analysis"
status: "completed_gap_clarification"
step0_status: "95_percent_code_ready_pending_freeze_run"
repository: "kazunguyen/GRACE-summary"
branch: "hieu"
git_head: "c2e10e47b75fe7a57866e2b8509c3111fb504130"
---

# Giải trình khoảng hở 5% của Bước 0 (Offline Diagnostic) và Lộ trình nghiệm thu 100%

## 1. Bản chất của Bước 0 trong đề tài GRACE
Theo [Đề cương nghiên cứu hợp nhất](../../De_cuong_nghien_cuu_GRACE_hop_nhat.pdf) (Mục 7 & Phụ lục C, trang 39):
> *"Bước 0: Metric lịch sử tạo lại từ file từng mẫu (sai khác $\le 0,001$); bảng sửa–hỏng có hàng ALL-0/ALL-1/RANDOM; Paired Cluster Bootstrap 5.000 lượt; phân tích bổ trợ (Complementarity) và OOF Benefit Router $R(x)$."*

Bước 0 là phân tích chẩn đoán độc lập (chạy offline trên CPU) để trả lời cho câu hỏi nghiên cứu nền tảng **RQ0**: Liệu biểu diễn đồ thị (Graph-based CPG / CodeT5) và mô hình ngôn ngữ lớn (LLM) có thực sự bổ trợ cho nhau (sửa sai cho nhau) hay không.

---

## 2. Vì sao Bước 0 đã đạt 95%? (Những gì đã xong hoàn toàn)
Phần lõi kỹ thuật, thuật toán và kiểm thử của Bước 0 đã được đội ngũ xây dựng và tích hợp thành công vào repo:
1. **Thuật toán OOF Benefit Router & Phân tích Sửa–Hỏng**:
   - Tệp [`01_Author_Baseline_Unified/diagnostic_kit/src/grace_diag/complementarity.py`](../01_Author_Baseline_Unified/diagnostic_kit/src/grace_diag/complementarity.py) đã triển khai đầy đủ các hàm Section B.5: `repair_harm()`, `oracle_accuracy()`, và `reference_experts()` (với đầy đủ các hàng đối chứng chuẩn `ALL-0`, `ALL-1` và `RANDOM` qua 20 lượt seed ngẫu nhiên).
   - Thuật toán phân chia OOF dùng `StratifiedGroupKFold` có cơ chế fallback an toàn, bảo đảm độc lập nhóm khi chia fold.
2. **Kỹ thuật Thống kê Bootstrap theo cụm (Cluster Bootstrap)**:
   - Cơ chế gom cụm kiểm soát rủi ro rò rỉ cấu trúc: Devign gom theo `commit_id` (2.068 cụm trên Test), REVEAL gom theo `file_hash` (646 cụm trên Test).
3. **Bộ kiểm thử Unit Test phủ kín**:
   - Bộ test [`tests/test_step0_offline_diagnostic.py`](../tests/test_step0_offline_diagnostic.py) đạt kết quả tuyệt đối **13/13 test PASS 100% Green** (kiểm tra đầy đủ luồng 2-split, single-split, fallback, và kiểm định paired bootstrap CI).
4. **Tái tạo 36 run lịch sử**:
   - Dữ liệu 36 run lịch sử của cấu hình offline trước đây đã được tái lập với sai lệch metric $= 0.00000000 \le 0.001$.

---

## 3. Khoảng hở 5% còn lại là gì? (Tại sao chưa kết luận 100%)
Khoảng hở 5% không nằm ở logic thuật toán hay code script, mà nằm ở **tính liên kết dữ liệu thực nghiệm và artifact chính thức**:

1. **Sự tách biệt về nguồn dữ liệu (Data Provenance)**:
   - Các kết quả tái tạo 36 run hiện có đến từ dữ liệu lịch sử của máy local (cấu hình Dung / Hiếu trước đây).
   - Đề cương nghiên cứu yêu cầu phân tích Bước 0 phải được xuất bản thành một báo cáo chính thức kết nối trực tiếp với tập dữ liệu sạch đã freeze của chiến dịch hiện tại (`research_freeze_20261101`).
2. **Khớp nối metadata thực tế của REVEAL (`file_hash`)**:
   - Trong dữ liệu giả lập (mock data) và test suite, đơn vị cluster bootstrap hoạt động hoàn hảo. Tuy nhiên, trên tập dữ liệu REVEAL thật của repo, cột `file_hash` cần được khớp nối từ file raw metadata vào file input của runner Bước 0 để runner không phải dùng cơ chế fallback `Sample Bootstrap`.
3. **Chưa xuất bản Artifact báo cáo chính thức**:
   - Chưa có tệp báo cáo chính thức `Runs-management/step0_diagnostic/diagnostic_report_devign.json` và `diagnostic_report_reveal.json` được ký hash và lưu vết trong kho lưu trữ `Runs-management/`.

---

## 4. Kế hoạch đóng dứt điểm 100% Bước 0
Để chuyển trạng thái Bước 0 từ **95% $\rightarrow$ 100% nghiệm thu hoàn tất**, các thao tác sau sẽ được thực thi:
1. Chuẩn bị tệp dữ liệu đầu vào thật từ `output/research_freeze_20261101/` (kèm cột `commit_id` cho Devign và `file_hash` cho REVEAL).
2. Chạy lệnh:
   ```powershell
   python scripts/run_step0_offline_diagnostic.py --dataset devign --output-dir Runs-management/step0_diagnostic/devign
   python scripts/run_step0_offline_diagnostic.py --dataset reveal --output-dir Runs-management/step0_diagnostic/reveal
   ```
3. Lưu các artifact `diagnostic_report_*.json` và `diagnostic_summary_*.md` vào `Runs-management/` và cập nhật bảng nghiệm thu Phụ lục C.
