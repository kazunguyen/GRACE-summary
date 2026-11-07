# Báo cáo Cập nhật Tiến độ Thực thi Test & Kiểm toán Runtime Nhóm Hiếu — 07/11/2026

**Thời điểm cập nhật**: `23:45:00+07:00` (`16:45:00 UTC`), ngày `07/11/2026`  
**Người thực hiện**: Hiếu & AI Assistant (Antigravity)  
**Phạm vi**: 6 Arm chẩn đoán được giao quản lý thực thi (`B1-full`, `B2-rep`, `B2-labelonly`, `B2-nolabel`, `B1-shuf`, `B3`).

---

## 1. TỔNG QUAN HIỆN TRẠNG 6 ARM CHẨN ĐOÁN (EXECUTIVE SUMMARY)

| Arm | Giai đoạn | Tài khoản Kaggle / Kernel Slug | Tình trạng Hiện tại (Live Status) | Bằng chứng Kỹ thuật & Output |
| :--- | :---: | :--- | :---: | :--- |
| **`B1-full`** | **Test** | `huuhieu3333/grace-b1-full-test` | **RUNNING** 🟢 (~5h 30m) | - Validation $5.005/5.005$ đã hoàn tất, $\tau^*$ locked: Devign $0.99$, ReVeal $0.01$.<br>- Test $5.006$ target đang chạy trên 2x T4 GPU, compilation CUDA SM75 pass. |
| **`B2-rep`** | **Test** | `huuhieu3333/grace-b2-rep-test` | **RUNNING** 🟢 (~5h 17m) | - Validation $5.005/5.005$ đã hoàn tất. Kế thừa nghiêm ngặt $\tau^*$ từ B2: Devign $0.70$, ReVeal $0.12$.<br>- Cấu hình cách ly cache `repeat: true`, `tag="repeat"`.<br>- Test $5.006$ target đang chạy trên 2x T4 GPU. |
| **`B2-labelonly`** | **Test** | `tomandjerry223/grace-b2-labelonly-test` | **RUNNING** 🟢 (~6h 21m) | - Validation $5.005/5.005$ đã hoàn tất, $\tau^*$ locked: Devign $0.99$, ReVeal $0.02$.<br>- Test $5.006$ target đang ở chặng cuối suy luận (>95%). |
| **`B2-nolabel`** | **Test** | `tomandjerry223/grace-b2-nolabel-test` | **RUNNING** 🟢 (~6h 21m) | - Validation $5.005/5.005$ đã hoàn tất, $\tau^*$ locked: Devign $0.98$, ReVeal $0.21$.<br>- Test $5.006$ target đang ở chặng cuối suy luận (>95%). |
| **`B1-shuf`** | **Test Prep** | `lznt123/grace-b1-shuf-test` | **READY TO RUN** 🚀 | - Đã tải bù thành công toàn bộ `reveal/donors.jsonl` ($17.636$ donor, SHA-256 `6bf44ab8...`).<br>- Đã sinh hoàn tất $15.018$ prompt Test (3 seeds: 42, 43, 44).<br>- Đã tạo và upload dataset Kaggle: `lznt123/grace-b1-shuf-test-inputs` ($15.4$ MB, SHA-256 `a6b2be70...`).<br>- Notebook chuẩn 9-cell khóa exact runtime lock đã sẵn sàng. |
| **`B3`** | **Validation** | `lznt123/grace-b3-validation` | **RUNNING** 🟢 (~4h 44m) | - Đang chạy vòng lặp validation trên dataset `lznt123/grace-b3-validation-inputs` ($10.010$ mẫu B3 + B3-nodiff, $12.7$ MB, SHA-256 `87527ce2...`).<br>- Đã chuẩn hóa notebook B3 Amended 9-cell chuẩn `grace_qwen_q4_runtime_v1` ở repo local. |

---

## 2. CHI TIẾT CÁC CÔNG VIỆC ĐÃ THỰC HIỆN TRONG CA LÀM VIỆC

### 2.1. Kiểm toán Tư pháp (Forensic Audit) Khóa Version & Tham số GPU
- Thực hiện kiểm tra 3 chiều đối chiếu giữa: (A) Chuẩn runtime lock của Dũng (`Runs-management/grace_hieu_5arms_runtime_locked_20261107.zip`), (B) Repo Local Git commit `167262a`, và (C) Code thực tế kéo từ Kaggle (`api.kernels_pull`).
- **Kết quả đối soát**:
  * 4 Arm Test (`B1-full`, `B2-rep`, `B2-labelonly`, `B2-nolabel`) bảo đảm 99.9% tính toàn vẹn toán học và thuật toán: Model SHA-256 `f6050b4da...`, tokenizer revision `b2cff646...`, `split_mode=LAYER`, `seed=4294967295`, `n_batch=256`, `n_ubatch=256`, `n_ctx=8192`, `n_gpu_layers=-1`, `logits_all=True`. Ngưỡng $\tau^*$ được khóa cố định theo điều khoản 2.3 của `AGENTS.md`.
  * Arm B3 validation live đang chạy phiên bản staging trung gian (thiếu `split_mode` và `seed`). Đã chuẩn hóa file `13_Arm_B3_Contrastive/notebooks/02_kaggle_qwen_q4_b3_amended_validation.ipynb` lên chuẩn 9-cell khóa cứng đầy đủ tham số để nạp lại sau khi slot trống.
- **Quyết định vận hành an toàn**: Giữ nguyên toàn bộ 5 kernel đang chạy để bảo toàn hạn ngạch GPU và dữ liệu suy luận quý giá đã chạy liên tục 5-6 tiếng qua.

### 2.2. Khôi phục Dữ liệu Donor ReVeal & Sinh $15.018$ Prompt Test B1-shuf
- Viết script `scripts/resume_reveal_donors.py` sử dụng HTTP Range Request tải bù thành công 795 MB còn thiếu từ Google Drive ID `162syKwALRE2EvMbP5bBHA4P9eis30hjA`.
- Khôi phục nguyên vẹn `01_Author_Baseline_Unified/output/research_freeze_20261101/reveal/donors.jsonl` ($1.887.092.268$ bytes, SHA-256 `6bf44ab86c8524d239e610fdccff5916cfc402fef7945d7cbe7f695e287abbce`), khớp 100% với freeze manifest.
- Chạy script `scripts/generate_b1_shuf_test_prompts.py` (4.703 giây), sinh trọn bộ $15.018$ prompt Test cho Devign ($8.196$ mẫu) và ReVeal ($6.822$ mẫu) qua 3 seeds 42, 43, 44.
- Đóng gói chuẩn hóa thành `grace_b1_shuf_test_inputs.zip` ($15.4$ MB, SHA-256 `a6b2be70b85462d96d531884085eb62d581e5863cb8897a86b23f326f284508b`).
- Tải lên thành công Kaggle Dataset: `lznt123/grace-b1-shuf-test-inputs`.
- Khóa toàn bộ mã băm xác thực vào notebook `08_Arm_B1_Shuf/notebooks/02_kaggle_qwen_q4_b1_shuf_test.ipynb`.

### 2.3. Trạng thái Prompt và Dữ liệu Arm B3
- **Tập Validation**: Đã có sẵn 100% tại `Runs-management/kaggle_staging_lznt123/dataset_b3_inputs/grace_b3_validation_inputs.zip` ($12.7$ MB, SHA-256 `87527ce21b8eff4d07cb8e979f16d312c7f336fe9382ed825a24767f592363d9`, gồm $10.010$ prompt có nhãn). File đã được tải lên Kaggle Dataset `lznt123/grace-b3-validation-inputs`.
- **Tập Test**: Dữ liệu spec gốc đã có sẵn trong `data/specs/*_test_15arms.jsonl`. Có thể sinh prompt test bất kỳ lúc nào; việc chạy suy luận test sẽ thực hiện sau khi có ngưỡng $\tau^*$ từ validation.

---

## 3. GIÁM SÁT ĐỊNH KỲ (SCHEDULED AUDIT LOG)

Đã thiết lập hệ thống giám sát định kỳ tự động 30 phút/lần (`scripts/audit_30m_progress.py`):
- **Chu kỳ 9 (22:56 GMT+7)**: Kiểm tra log chẩn đoán `events.log` từ kernel `huuhieu3333`, xác nhận CUDA compilation SM75 hoàn thành lúc 10:23 UTC và vòng lặp suy luận chạy liên tục không ngắt quãng.
- **Chu kỳ 10 (23:26 GMT+7)**: Xác nhận cả 5 kernel tiếp tục `RUNNING` ổn định, hai phiên của `tomandjerry223` đã vượt mốc 6 giờ 20 phút chạy, chuẩn bị kết thúc.
- **Chu kỳ 11 (23:56 GMT+7)**: Đang trong lịch hẹn đếm ngược để đón nhận kết quả nghiệm thu (`COMPLETE`).

---

## 4. KẾ HOẠCH BƯỚC TIẾP THEO

1. **Nghiệm thu 4 Arm Test**: Ngay khi các kernel chuyển sang `COMPLETE`, tải về trọn bộ checkpoint `records.jsonl`, `evaluation.json`, trích xuất các chỉ số $\text{AUROC}, \text{MCC}, \text{BA}, \text{F1}$ và log xác nhận 49/49 GPU layers.
2. **Kích hoạt B1-shuf Test**: Khi tài khoản `lznt123` kết thúc phiên B3 hiện tại (hoặc khi sẵn sàng quota), kích hoạt kernel `lznt123/grace-b1-shuf-test` với dataset `lznt123/grace-b1-shuf-test-inputs` đã nạp sẵn.
3. **Triển khai B3 Amended**: Nạp notebook chuẩn 9-cell `13_Arm_B3_Contrastive/notebooks/02_kaggle_qwen_q4_b3_amended_validation.ipynb` để chạy nghiệm thu thuật toán mới với đầy đủ ràng buộc runtime lock.
