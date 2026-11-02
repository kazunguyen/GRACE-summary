---
id: "step4-20261102-13"
title: "Kiểm toán Toàn diện Độc lập & Phản biện Sẵn sàng Nộp OSF từ Bước 0 đến Bước 4"
author: "Antigravity (AI Lead Coordinator & Independent Audit Pipeline)"
author_type: "AI assistant"
requested_by: "HuuHieu03 (Hiếu)"
recorded_at: "2026-11-02T23:25:00+07:00"
timezone: "Asia/Bangkok"
work_date: "2026-11-02"
record_type: "official_audit_and_adversarial_debate"
status: "audit_completed_blocked_for_fixes"
audit_decision: "not_ready_for_raw_osf_submission_pending_5_fixes"
repository: "kazunguyen/GRACE-summary"
branch: "hieu"
evidence_verified_at: "2026-11-02T23:25:00+07:00"
---

# Báo cáo Kiểm toán Toàn diện Độc lập & Phản biện Tính sẵn sàng Nộp OSF (Bước 0 đến Bước 4)

## 1. Mục đích & Nguyên tắc thực thi phiên Kiểm toán
Thực hiện chỉ đạo của người dùng (`HuuHieu03`) về việc:
1. Rà soát độc lập, đa góc nhìn và tổ chức tranh luận phản biện đối đầu (*Adversarial Debate*) giữa các Sub-agent (Skeptical Worker L0 vs Improvement Worker).
2. Tuyệt đối không thiên vị, không "làm đẹp số liệu để qua test" trong khi thực tế còn tồn đọng lỗ hổng (*Anti-Bias, Anti-Hallucination, Evidence-Grounded*).
3. Đối chiếu chi tiết với [Đề cương nghiên cứu GRACE hợp nhất](../../De_cuong_nghien_cuu_GRACE_hop_nhat.pdf) (Bảng 4.3 Mục 4.3, Mục 6, Mục 7 và Phụ lục C trang 39–40).
4. Xác định cụ thể các tài liệu và quy trình chi tiết để đưa hồ sơ lên nền tảng **OSF Registries** (https://osf.io/registries).

---

## 2. Phán quyết Kiểm toán Tổng thể

> ### ⚠️ PHÁN QUYẾT: CHƯA SẴN SÀNG ĐỂ NỘP NGUYÊN TRẠNG LÊN OSF NGAY BÂY GIỜ
> 
> Mặc dù toàn bộ bộ kiểm thử tự động đang đạt **108/108 PASS (100% Green)** và nền tảng kỹ thuật đạt độ hoàn thiện rất cao, cuộc kiểm toán đối đầu đã bóc tách được **5 điểm nghẽn kỹ thuật cốt tử**. Nếu nộp nguyên trạng ngay lúc này, hồ sơ sẽ bị hội đồng hoặc reviewer quốc tế đặt nghi vấn về tính nhất quán dữ liệu và vi phạm định danh mô hình (model provenance).

---

## 3. Bảng đối chiếu từ Bước 0 đến Bước 4 theo Phụ lục C của Đề cương

| Hạng mục Phụ lục C (trang 39–40) | Yêu cầu Đề cương | Hiện trạng Artifact thực tế trên đĩa | Đánh giá Kỹ thuật | Trạng thái OSF |
| :--- | :--- | :--- | :---: | :---: |
| **Bước 0: Diagnostic Offline** | - Tái hiện metric lịch sử sai lệch $\le 0,001$<br>- Bảng sửa–hỏng có hàng `ALL-0/ALL-1/RANDOM`<br>- Trần Oracle<br>- $\Delta\text{MCC}(P_\text{post} - P_\text{pre})$ Paired Cluster Bootstrap. | Đã có thư mục `Runs-management/step0_diagnostic/`; sai khác lịch sử $= 0,00000000$; đủ hàng đối chứng Section B.5; gom cụm 2.068 commit (Devign) & 646 file hash (REVEAL).<br>⚠️ *Điểm lệch*: JSON chạy 1.000 reps thay vì 5.000 reps. | **ĐẠT 95%** | Sẵn sàng kèm ghi chú kỹ thuật |
| **Bước 1: Backend Smoke Test** | - Model Checkpoint & SHA-256<br>- Top-5 unconstrained logprobs<br>- Valid token rate $\ge 99\%$<br>- Repeat agreement $\ge 98\%$<br>- Đo thông lượng phần cứng thật. | Đã có `Runs-management/step1_backend_smoke/`; Valid rate 100%; Repeat 100%; Kaggle 2×T4 đạt 6,69s/prompt.<br>⚠️ **LỖ HỔNG CRITICAL**: Mâu thuẫn định danh mô hình giữa 3 file (xem Mục 4). | ⚠️ **MÂU THUẪN DANH TÍNH MÔ HÌNH** | **CHẶN NỘP** |
| **Bước 2: Freeze Data, Donor & Specs** | - Manifest có mã băm SHA-256<br>- Kiểm toán trùng lặp duy nhất<br>- Kho donor đã khử trùng<br>- Specs validation & test. | Dữ liệu freeze nằm tại `01_Author_Baseline_Unified/output/research_freeze_20261101/`.<br>⚠️ **LỖ HỔNG HIGH**: Bảng 7.1 trong `preregistration.md` ghi đường dẫn `data/manifests/` không có thật và lệch số lượng donor (21.711 vs 21.691 Devign; 17.620 vs 17.636 REVEAL). | ⚠️ **LỆCH MÃ BĂM & SAI ĐƯỜNG DẪN** | **CHẶN NỘP** |
| **Bước 3: Prompt Integrity & Dry-run** | - 10/15 arms dry-run validation<br>- Rò rỉ nhãn $= 0$<br>- Demo rỗng $\le 1\%$<br>- Graph thiếu gắn cờ<br>- Chấm mù 60 prompt (2 người) có $\kappa \ge 0,80$ kèm biên bản<br>- 5 arm Tầng 3 định vị rõ. | Đã dry-run **70.070 prompt** validation cho 10 arm tại `Runs-management/dry_run_validation_20261102/`; rò rỉ nhãn $= 0$; demo rỗng $\le 0,88\%$; graph thiếu có cờ; Chấm mù 2 người hoàn tất có $\kappa = 0,8507$ và `BIEN_BAN_PHAN_XU.md`; 5 arm Tầng 3 định vị trung thực là extension. | **ĐẠT 100%** | **SẴN SÀNG** |
| **Bước 4: Pre-registration & Threshold Lock** | - `protocol.yaml` điền đủ<br>- `preregistration.md` tag `prereg-v1` tại commit `cc64124`<br>- Khóa 14 ngưỡng $\tau^*$ trên validation trước khi chạy test<br>- Gate `require_test_lock()`<br>- Pytest suite xanh (108/108 pass). | Commit HEAD `cc64124` đã gắn tag `prereg-v1`; Pytest **108/108 pass**; `configs/thresholds.json` khóa 14 ngưỡng.<br>⚠️ **LỖ HỔNG HIGH**: Văn bản `preregistration.md` (dòng 63-64) ghi sai ngưỡng B2 thành $0,98$ và $0,99$ (thực tế khóa là $0,70$ và $0,12$); Gói draft PDF/ZIP bị lỗi thời (stale). | ⚠️ **LỆCH NGƯỠNG TRONG TEXT & STALE ZIP/PDF** | **CHẶN NỘP** |

---

## 4. Giải trình Chi tiết về Bước 3: Phạm vi Dry-run 10 Arms vs 15 Arms

Một câu hỏi quan trọng được đặt ra trong phiên kiểm toán: *"Liệu Bước 3 có cần phải sinh prompt cho toàn bộ 15 arms để audit không?"*

**Kết luận chuyên môn**: **KHÔNG CẦN và KHÔNG THỂ sinh prompt cho cả 15 arms ở thời điểm hiện tại trước khi nộp OSF.**
1. **Thiết kế phân tầng theo Đề cương**:
   - **Tầng 1 (5 arms)**: `B0`, `B1`, `B2`, `B2-flip`, `B2-rep`. (Đã hoàn thành 100%).
   - **Tầng 2 (5 arms)**: `B1-shuf` (3 seed), `B2-rand` (3 seed), `B2-nolabel`, `B2-labelonly`, `B1-full`. (Đã hoàn thành 100%).
   - **Tầng 3 (5 arms)**: Họ Contrastive ICL `B3` (`B3`, `B3-nodiff`, `B3-swap`, `B3-flip`) và `B1-H2`.
2. **Lý do 5 arm Tầng 3 bị chặn (`blocked_missing_inputs`)**:
   - Họ `B3` đòi hỏi đầu vào là **cặp mẫu tương phản** (1 hàm lỗi, 1 hàm an toàn từ cùng một commit/diff) và đoạn phân tích khác biệt an ninh (`security_difference`).
   - Đây là phương pháp đề xuất mới của bài báo, thuộc giai đoạn thực nghiệm tiếp theo. Tại thời điểm nộp OSF, mã nguồn renderer `render_arm_B3` đã sẵn sàng trong `grace_diag/probes.py`, nhưng dữ liệu cặp đối chứng chưa được trích xuất.
   - Việc không tự ý bịa dữ liệu giả để render B3 là minh chứng cho tính trung thực khoa học.
3. **Tuân thủ quy chuẩn Phụ lục C**:
   - Phụ lục C chỉ yêu cầu dry-run và kiểm toán prompt với các tiêu chí định lượng (rò rỉ nhãn $= 0$, demo rỗng $\le 1\%$, graph thiếu $\le 5\%$, chấm mù 60 mẫu đạt $\kappa \ge 0,80$).
   - 10 arm đã dry-run với **70.070 prompts** đã bao phủ toàn bộ các tình huống phức tạp nhất của prompt template. Việc khai báo 10 arm đã nghiệm thu và 5 arm Tầng 3 là khối mở rộng đang chờ bộ sinh cặp đối chứng là hoàn toàn minh bạch và chuẩn mực học thuật.

---

## 5. Danh mục 5 Điểm nghẽn Kỹ thuật Cốt tử cần Khắc phục trước khi Nộp OSF

1. **Mâu thuẫn Danh tính Mô hình (Model Provenance - CRITICAL)**:
   - Mô hình thực tế chạy trên Kaggle và 30.000+ record: `Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf` (Repo: `ggml-org/Qwen3-Coder-30B-A3B-Instruct-GGUF`, SHA-256: `f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335`).
   - Điểm lệch: `backend_manifest.json` ghi nhầm `Qwen2.5`, trong khi `preregistration.md`/`protocol.yaml` ghi `UD-Q4_K_XL`.
   - *Khắc phục*: Thống nhất 100% văn bản và manifest về `Qwen3-Coder-30B-A3B-Instruct GGUF Q4_K_M` kèm mã SHA `f6050b...`.
2. **Lệch Ngưỡng Quyết định trong Văn bản `preregistration.md` (HIGH)**:
   - Dòng 63–64 trong `preregistration.md` ghi nhầm: `devign|B2|42 = 0.98` và `reveal|B2|42 = 0.99`.
   - Ngưỡng thực tế được khóa trong `configs/thresholds.json`: `0.70` (Devign) và `0.12` (REVEAL).
   - *Khắc phục*: Sửa lại đúng $0,70$ và $0,12$ trong văn bản markdown.
3. **Số lượng Donor và Đường dẫn trong Bảng 7.1 của `preregistration.md` (HIGH)**:
   - Bảng 7.1 ghi 21.711 Devign và 17.620 REVEAL, đường dẫn `data/manifests/`.
   - Số lượng thực tế trong `freeze_manifest.json`: 21.691 Devign và 17.636 REVEAL, đường dẫn `01_Author_Baseline_Unified/output/research_freeze_20261101/`.
   - *Khắc phục*: Cập nhật số liệu và đường dẫn chuẩn xác.
4. **Số lượt Bootstrap ở Báo cáo Bước 0 (MEDIUM)**:
   - Báo cáo JSON ghi `n_boot: 1000`, trong khi Đề cương quy định 5.000 lượt.
   - *Khắc phục*: Chạy lại runner với `n_boot=5000` để tái lập báo cáo JSON/MD chuẩn 5.000 lượt.
5. **Gói Artifact OSF Draft PDF và ZIP bị lỗi thời (HIGH)**:
   - File `GRACE_OSF_DRAFT_20261102.pdf` và `GRACE_OSF_DRAFT_20261102.zip` được tạo trước khi hoàn tất chấm mù 2 người và dry-run 10 arm.
   - Mã băm SHA-256 trong `attachment_sha256.json` bị lệch so với commit `cc64124`.
   - *Khắc phục*: Biên dịch lại PDF, cập nhật mã băm và nén lại file ZIP.

---

## 6. Cẩm nang Hướng dẫn Thao tác Nộp Hồ sơ trên OSF Registries

### 6.1. Biểu mẫu đăng ký bắt buộc
- **Bắt buộc chọn**: **"Secondary Data Analysis Preregistration"** (hoặc **"Open-Ended Registration"**).
- *Lý do*: Nghiên cứu có sử dụng benchmark đã được khám phá trước đó (Test exposure in-flight data). Việc chọn biểu mẫu này kèm văn bản tuyên bố minh bạch (Disclosure) giúp tránh hoàn toàn cáo buộc HARKing (Hypothesizing After Results are Known).

### 6.2. Các trường thông tin chính cần điền (Copy/Paste)
- **Title**: `A Diagnostic and Mechanistic Replication of GRACE on Open-Weight Code LLMs`
- **Description**: Tóm tắt nghiên cứu tập trung vào tái lập chẩn đoán cơ chế đồ thị và demo của GRACE trên mô hình mã nguồn mở Qwen-Coder 30B, sử dụng ma trận sửa–hỏng, trần Oracle, meta-model phân tầng và các probe kiểm toán.
- **Data Disclosure**: Khai báo rõ 14 ngưỡng $\tau^*$ được tối ưu hóa thuần túy trên tập Validation, zero-test-exposure.
- **Hypotheses**: 11 giả thuyết từ H1.1 đến H6.1 theo Bảng 4.3 Đề cương.
- **Analysis Plan**: Kiểm định Paired Cluster Bootstrap 5.000 lượt (2.068 cụm commit trên Devign, 646 cụm file hash trên REVEAL), hiệu chỉnh Holm-Bonferroni, quy tắc phán quyết 4 nhánh (`benefit`, `harm`, `no_meaningful_benefit`, `inconclusive`) với biên thực chất $\delta = 0,02$.

### 6.3. Danh mục Tệp đính kèm nộp lên OSF
Gói tệp đính kèm `GRACE_OSF_SUBMISSION_BUNDLE.zip` gồm:
1. `1_PREREGISTRATION_DOCUMENT.pdf` (Bản PDF chính thức hoàn thiện).
2. `2_PROTOCOL_SPECIFICATION.yaml` (`configs/protocol.yaml`).
3. `3_LOCKED_THRESHOLDS.json` & `4_LOCKED_THRESHOLDS_FLAT.json` (14 ngưỡng tối ưu từ Validation).
4. `5_STEP0_OFFICIAL_REPORTS/` (Báo cáo chẩn đoán Bước 0).
5. `6_STEP1_BACKEND_SMOKE/` (Manifest, smoke test, throughput benchmark Bước 1).
6. `7_STEP3_AUDIT_AND_HUMAN_REVIEW/` (`BIEN_BAN_PHAN_XU.md` có chữ ký Hiếu & Dũng, `manual_sample.jsonl`, dry-run summary 70k).
7. `8_CHECKSUMS_AND_MANIFEST.json` (Danh mục mã băm SHA-256 toàn bộ các file trên).

---

## 7. Kết luận & Cam kết
Hồ sơ nghiên cứu hiện đã hội đủ toàn bộ cơ sở dữ liệu và bằng chứng thực nghiệm từ Bước 0 đến Bước 4. Sau khi hoàn thành việc chỉnh trang 5 điểm nghẽn kỹ thuật nêu trên, nhóm nghiên cứu sẽ tiến hành gắn tag `prereg-v2` (hoặc chốt commit hoàn thiện) và đệ trình chính thức lên OSF.io.
