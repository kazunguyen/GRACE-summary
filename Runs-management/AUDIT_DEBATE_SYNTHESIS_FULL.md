The following is a <SYSTEM_MESSAGE> not actually sent by the user. It is provided by the system as important information to pay attention to.

<SYSTEM_MESSAGE>
[Message] timestamp=2026-11-02T16:12:51Z sender=f80b83c5-570f-4392-a109-2d779b9b0f42 priority=MESSAGE_PRIORITY_HIGH content=# BÁO CÁO KIỂM TOÁN ĐỘC LẬP & PHẢN BIỆN CHUYÊN SÂU TỪ BƯỚC 0 ĐẾN BƯỚC 4
**Dự án**: Tái lập & Chẩn đoán Cơ chế GRACE trên LLM Open-Weight  
**Tài liệu đối chiếu căn bản**: [De_cuong_nghien_cuu_GRACE_hop_nhat.pdf](file:///d:/tai%20lieu%20hoc%20tap/%C4%90%E1%BB%81%20t%C3%A0i%20nghi%C3%AAn%20c%E1%BB%A9u%20khoa%20h%E1%BB%8Dc/papers%20source%20code/GRACE-summary/De_cuong_nghien_cuu_GRACE_hop_nhat.pdf) (Bảng 4.3 Mục 4.3, Mục 6, Mục 7, Phụ lục C trang 39–40)  
**Thời điểm kiểm toán**: 2026-11-02T23:15:00+07:00 (Commit HEAD: [`cc64124`](file:///d:/tai%20lieu%20hoc%20tap/%C4%90%E1%BB%81%20t%C3%A0i%20nghi%C3%AAn%20c%E1%BB%A9u%20khoa%20h%E1%BB%8Dc/papers%20source%20code/GRACE-summary), Git Tag: `prereg-v1`)  
**Nguyên tắc thực thi**: *Strictly Unbiased, Anti-Hallucination, Evidence-Grounded*. Không thiên vị, không báo cáo hình thức, đối chiếu tận mắt từng byte artifact và mã nguồn thực tế.

---

## I. TỔNG KẾT NGHIỆM THU & PHÁN QUYẾT SẴN SÀNG NỘP OSF

### 1. Phán quyết tổng thể: ⚠️ **CHƯA SẴN SÀNG ĐỂ NỘP NGUYÊN TRẠNG LÊN OSF**
Mặc dù toàn bộ bộ kiểm thử tự động đạt kết quả **108/108 PASS (100%)** và nhiều phân hệ đã đạt độ hoàn thiện kỹ thuật rất xuất sắc (Bước 0 phân tích 2-split chuẩn hóa, Bước 3 dry-run thành công 70.070 prompt validation, Bước 3 chấm mù độc lập đạt $\kappa = 0,8507$), hồ sơ hiện tại **CÒN 5 ĐIỂM NGHẼN KỸ THUẬT & DỮ LIỆU CỐT TỬ**. 

Nếu nộp nguyên trạng lên OSF ngay lúc này, hồ sơ sẽ bị reviewer quốc tế hoặc hội đồng phản biện bắt bẻ vì **bất nhất dữ liệu nội bộ**, **sai lệch mã băm manifest**, **mâu thuẫn danh tính mô hình (model provenance)** và **lỗi thời hóa gói tệp đính kèm**.

---

### 2. Bảng tổng hợp đối chiếu Bước 0 đến Bước 4 theo Phụ lục C (Trang 39–40)

| Hạng mục Phụ lục C | Yêu cầu Đề cương | Hiện trạng Artifact thực tế trên đĩa | Đánh giá Kỹ thuật | Trạng thái OSF |
| :--- | :--- | :--- | :---: | :---: |
| **Bước 0: Diagnostic Offline** | - Sai khác metric $\le 0,001$<br>- Bảng sửa–hỏng có hàng `ALL-0/ALL-1/RANDOM`<br>- Trần Oracle<br>- $\Delta\text{MCC}(P_\text{post} - P_\text{pre})$ Bootstrap cụm phân tầng. | Đã có thư mục [`Runs-management/step0_diagnostic/`](file:///d:/tai%20lieu%20hoc%20tap/%C4%90%E1%BB%81%20t%C3%A0i%20nghi%C3%AAn%20c%E1%BB%A9u%20khoa%20h%E1%BB%8Dc/papers%20source%20code/GRACE-summary/Runs-management/step0_diagnostic/); sai khác lịch sử $= 0,00000000$; đủ hàng đối chứng Section B.5; gom cụm 2.068 (Devign) & 646 (REVEAL).<br>⚠️ **Điểm nghẽn**: Chạy 1.000 reps thay vì 5.000 reps theo đề cương. | **ĐẠT 95%**<br>(Cần nâng lên 5.000 reps để khớp text đề cương) | Sẵn sàng kèm ghi chú kỹ thuật |
| **Bước 1: Backend Smoke Test** | - Model Checkpoint & SHA-256<br>- Top-5 unconstrained logprobs<br>- Valid token rate $\ge 99\%$<br>- Repeat agreement $\ge 98\%$<br>- Đo thông lượng phần cứng thật. | Đã có [`Runs-management/step1_backend_smoke/`](file:///d:/tai%20lieu%20hoc%20tap/%C4%90%E1%BB%81%20t%C3%A0i%20nghi%C3%AAn%20c%E1%BB%A9u%20khoa%20h%E1%BB%8Dc/papers%20source%20code/GRACE-summary/Runs-management/step1_backend_smoke/); Valid rate 100%; Repeat 100%; Kaggle 2×T4 (6,69s/prompt).<br>⚠️ **LỖ HỔNG CRITICAL**: Mâu thuẫn 3 bên về định danh mô hình: `backend_manifest.json` ghi nhầm `Qwen2.5`, `preregistration.md` ghi `UD-Q4_K_XL`, trong khi toàn bộ 30k+ run Kaggle thật chạy `Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf`! | ⚠️ **MÂU THUẪN ĐỊNH DANH MÔ HÌNH (CRITICAL)** | **CHẶN NỘP** |
| **Bước 2: Freeze Data, Donor & Specs** | - Manifest có hash SHA-256<br>- Kiểm toán trùng lặp duy nhất (exact & near-dup)<br>- Kho donor đã khử trùng<br>- Specs validation & test. | Dữ liệu freeze nằm tại [`01_Author_Baseline_Unified/output/research_freeze_20261101/`](file:///d:/tai%20lieu%20hoc%20tap/%C4%90%E1%BB%81%20t%C3%A0i%20nghi%C3%AAn%20c%E1%BB%A9u%20khoa%20h%E1%BB%8Dc/papers%20source%20code/GRACE-summary/01_Author_Baseline_Unified/output/research_freeze_20261101/).<br>⚠️ **LỖ HỔNG HIGH**: Toàn bộ đường dẫn `data/manifests/` và `data/specs/` trong `preregistration.md` không tồn tại; mã băm trong Bảng 7.1 bị lệch hoàn toàn so với file freeze thực tế; số lượng donor lệch (21.711 vs 21.691 tại Devign; 17.620 vs 17.636 tại REVEAL). | ⚠️ **LỆCH MÃ BĂM & SAI ĐƯỜNG DẪN ĐĨA (HIGH)** | **CHẶN NỘP** |
| **Bước 3: Prompt Integrity & Dry-run** | - 10/15 arms dry-run validation<br>- Rò rỉ nhãn $= 0$<br>- Demo rỗng $\le 1\%$<br>- Graph thiếu gắn cờ<br>- Chấm mù 60 prompt (2 người) có $\kappa \ge 0,80$ kèm biên bản<br>- 5 arm Tầng 3 định vị rõ. | Đã dry-run **70.070 prompt** validation cho 10 arm tại [`Runs-management/dry_run_validation_20261102/`](file:///d:/tai%20lieu%20hoc%20tap/%C4%90%E1%BB%81%20t%C3%A0i%20nghi%C3%AAn%20c%E1%BB%A9u%20khoa%20h%E1%BB%8Dc/papers%20source%20code/GRACE-summary/Runs-management/dry_run_validation_20261102/); rò rỉ nhãn $= 0$; demo rỗng $\le 0,88\%$; graph thiếu có cờ; Chấm mù 2 người hoàn tất có $\kappa = 0,8507$ và [`BIEN_BAN_PHAN_XU.md`](file:///d:/tai%20lieu%20hoc%20tap/%C4%90%E1%BB%81%20t%C3%A0i%20nghi%C3%AAn%20c%E1%BB%A9u%20khoa%20h%E1%BB%8Dc/papers%20source%20code/GRACE-summary/Runs-management/prompt_audit_20261102/BIEN_BAN_PHAN_XU.md); 5 arm Tầng 3 định vị trung thực là extension. | **ĐẠT 100%** | Sẵn sàng |
| **Bước 4: Pre-registration & Threshold Lock** | - `protocol.yaml` điền đủ<br>- `preregistration.md` tag `prereg-v1` tại commit `cc64124`<br>- Khóa 14 ngưỡng $\tau^*$ trên validation trước khi chạy test<br>- Gate `require_test_lock()`<br>- Pytest suite xanh (108/108 pass). | Commit [`cc64124`](file:///d:/tai%20lieu%20hoc%20tap/%C4%90%E1%BB%81%20t%C3%A0i%20nghi%C3%AAn%20c%E1%BB%A9u%20khoa%20h%E1%BB%8Dc/papers%20source%20code/GRACE-summary) đã tag `prereg-v1`; Pytest **108/108 pass**; [`configs/thresholds.json`](file:///d:/tai%20lieu%20hoc%20tap/%C4%90%E1%BB%81%20t%C3%A0i%20nghi%C3%AAn%20c%E1%BB%A9u%20khoa%20h%E1%BB%8Dc/papers%20source%20code/GRACE-summary/configs/thresholds.json) khóa 14 ngưỡng.<br>⚠️ **LỖ HỔNG HIGH**: Văn bản `preregistration.md` (dòng 63-64) ghi sai ngưỡng B2 thành $0,98$ và $0,99$ (thực tế khóa là $0,70$ và $0,12$); Gói draft PDF/ZIP bị lỗi thời (stale) so với commit `cc64124`. | ⚠️ **LỆCH NGƯỠNG TRONG TEXT & STALE PDF/ZIP (HIGH)** | **CHẶN NỘP** |

---

## II. ĐỐI CHIẾU CHI TIẾT TỪNG BƯỚC (BƯỚC 0 ĐẾN BƯỚC 4)

### 1. Bước 0: Phân tích chẩn đoán Offline (Offline Diagnostic Pipeline)
- **Tái tạo metric lịch sử (Historical Reproduction)**:
  - File đối chứng: [`data/b0_offline_dungs_data/section2_1_full_reproduction.json`](file:///d:/tai%20lieu%20hoc%20tap/%C4%90%E1%BB%81%20t%C3%A0i%20nghi%C3%AAn%20c%E1%BB%A9u%20khoa%20h%E1%BB%8Dc/papers%20source%20code/GRACE-summary/data/b0_offline_dungs_data/section2_1_full_reproduction.json) và [`metric_reproduction_historical_36.json`](file:///d:/tai%20lieu%20hoc%20tap/%C4%90%E1%BB%81%20t%C3%A0i%20nghi%C3%AAn%20c%E1%BB%A9u%20khoa%20h%E1%BB%8Dc/papers%20source%20code/GRACE-summary/data/b0_offline_dungs_data/metric_reproduction_historical_36.json).
  - Tái tạo 36 run lịch sử (90.108 lượt dự đoán từng mẫu). Sai khác so với công bố Mục 2.1: $\Delta = 0,00000000 \le 0,001$ (**PASS TUYỆT ĐỐI**).
- **Bảng sửa – hỏng (Repair / Harm Matrix)**:
  - Tại [`Runs-management/step0_diagnostic/devign/diagnostic_report_devign.json`](file:///d:/tai%20lieu%20hoc%20tap/%C4%90%E1%BB%81%20t%C3%A0i%20nghi%C3%AAn%20c%E1%BB%A9u%20khoa%20h%E1%BB%8Dc/papers%20source%20code/GRACE-summary/Runs-management/step0_diagnostic/devign/diagnostic_report_devign.json) (dòng 110–139):
    - Lớp an toàn ($y=0$): Sửa $R_0 = 678$, Hỏng $H_0 = 24$.
    - Lớp lỗ hổng ($y=1$): Sửa $R_1 = 16$, Hỏng $H_1 = 834$.
    - Tổng cộng: Sửa $R = 694$, Hỏng $H = 858$, Sửa ròng $R - H = -164$.
  - Hàng đối chứng bắt buộc theo Section B.5 (dòng 140–165):
    - `ALL-0`: Repair $= 884$, Harm $= 1078$, Oracle $= 0,9352$.
    - `ALL-1`: Repair $= 177$, Harm $= 593$, Oracle $= 0,6764$.
    - `RANDOM` (rate $= 0,179$, 20 seed): Repair mean $= 757,0$ $[739,3, 770,0]$, Harm mean $= 986,4$ $[963,9, 1005,0]$, Oracle mean $= 0,8887$.
  - Đồng thời, artifact [`runs/complementarity_devign.json`](file:///d:/tai%20lieu%20hoc%20tap/%C4%90%E1%BB%81%20t%C3%A0i%20nghi%C3%AAn%20c%E1%BB%A9u%20khoa%20h%E1%BB%8Dc/papers%20source%20code/GRACE-summary/runs/complementarity_devign.json) (dòng 19-20) tái hiện chính xác con số 303 ca sửa đúng lịch sử được nêu tại trang 16 dòng 24 của Đề cương nghiên cứu.
- **Trần Oracle (Oracle Ceiling)**:
  - Devign: Oracle Accuracy $= 86,57\%$, Oracle MCC $= 0,7307$ (vượt Gate standalone $+0,4422$).
  - REVEAL: Oracle Accuracy $= 94,06\%$, Oracle MCC $= 0,6439$ (vượt Gate standalone $+0,2881$).
- **Mô hình ghép cặp Meta-Model $\Delta\text{MCC}(P_\text{post} - P_\text{pre})$**:
  - Devign Test ($N=2.732$): $\tau_\text{pre}^* = 0,34$, $\tau_\text{post}^* = 0,56$. $\Delta\text{MCC} = +0,0053$ (95% CI: $[-0,0384, +0,0493]$). Phán quyết theo $\delta = 0,02$: `INCONCLUSIVE`.
  - REVEAL Test ($N=2.274$): $\tau_\text{pre}^* = 0,22$, $\tau_\text{post}^* = 0,19$. $\Delta\text{MCC} = -0,0274$ (95% CI: $[-0,0536, -0,0001]$). Phán quyết: `HARM`.
  - Phân cụm Cluster Bootstrap: Devign gom theo `commit_id` (**2.068 cụm** trên Test); REVEAL gom theo `file_hash` (**646 cụm** trên Test).
  - ⚠️ **Khoảng trống**: Trong báo cáo JSON/MD của Bước 0, số lượt bootstrap chỉ chạy **1.000 lượt** (`n_boot: 1000`), trong khi Đề cương (Mục 6.6), `protocol.yaml` (dòng 55) và `preregistration.md` (dòng 67) đều quy định chuẩn là **5.000 lượt** (`n_boot: 5000`).

---

### 2. Bước 1: Môi trường Backend & Smoke Test
- **Định lượng độ chính xác & Tất định**:
  - File kiểm chứng: [`Runs-management/step1_backend_smoke/smoke_test_report.json`](file:///d:/tai%20lieu%20hoc%20tap/%C4%90%E1%BB%81%20t%C3%A0i%20nghi%C3%AAn%20c%E1%BB%A9u%20khoa%20h%E1%BB%8Dc/papers%20source%20code/GRACE-summary/Runs-management/step1_backend_smoke/smoke_test_report.json).
  - Tỷ lệ token 0/1 xuất hiện tự nhiên trong top-5 logprobs: **100,0%** ($\ge 99\%$). Không cần ép ngữ pháp (`guided_choice: false`).
  - Độ trùng lặp tất định (Repeat Agreement với seed 42): **100,0%** ($\ge 98\%$).
- **Đo lường Thông lượng trên phần cứng thực tế**:
  - File: [`Runs-management/step1_backend_smoke/throughput_benchmark.json`](file:///d:/tai%20lieu%20hoc%20tap/%C4%90%E1%BB%81%20t%C3%A0i%20nghi%C3%AAn%20c%E1%BB%A9u%20khoa%20h%E1%BB%8Dc/papers%20source%20code/GRACE-summary/Runs-management/step1_backend_smoke/throughput_benchmark.json).
  - Phần cứng: Kaggle Linux GPU 2× Tesla T4 (16GB × 2).
  - Độ trễ trung bình: **6,69 giây / prompt** (Trung vị: 5,61s). Thông lượng: **~8,97 prompts / phút**.
- ⚠️ **PHÁT HIỆN GỐC RỄ VỀ DANH TÍNH MÔ HÌNH (MODEL PROVENANCE)**:
  - Qua kiểm tra chéo toàn diện giữa các file thực thi và manifest gốc:
    1. Trong [`01_Author_Baseline_Unified/kaggle_qwen_q4_b2/downloaded_output_20261101/grace_b2_four_split_8h/reveal/validation/run_manifest.json`](file:///d:/tai%20lieu%20hoc%20tap/%C4%90%E1%BB%81%20t%C3%A0i%20nghi%C3%AAn%20c%E1%BB%A9u%20khoa%20h%E1%BB%8Dc/papers%20source%20code/GRACE-summary/01_Author_Baseline_Unified/kaggle_qwen_q4_b2/downloaded_output_20261101/grace_b2_four_split_8h/reveal/validation/run_manifest.json) (dòng 3–6), [`evaluation_contract.yaml`](file:///d:/tai%20lieu%20hoc%20tap/%C4%90%E1%BB%81%20t%C3%A0i%20nghi%C3%AAn%20c%E1%BB%A9u%20khoa%20h%E1%BB%8Dc/papers%20source%20code/GRACE-summary/01_Author_Baseline_Unified/evaluation_contract.yaml) (dòng 54–60), và [`RUN_GUIDE_KAGGLE.md`](file:///d:/tai%20lieu%20hoc%20tap/%C4%90%E1%BB%81%20t%C3%A0i%20nghi%C3%AAn%20c%E1%BB%A9u%20khoa%20h%E1%BB%8Dc/papers%20source%20code/GRACE-summary/01_Author_Baseline_Unified/RUN_GUIDE_KAGGLE.md) (dòng 5):
       Mô hình thực tế đã tải và chạy trên Kaggle là: **`ggml-org/Qwen3-Coder-30B-A3B-Instruct-GGUF`**, file **`Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf`**, mã băm SHA-256: **`f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335`**, runtime `llama-cpp-python 0.3.16`.
    2. Tuy nhiên, trong [`Runs-management/step1_backend_smoke/backend_manifest.json`](file:///d:/tai%20lieu%20hoc%20tap/%C4%90%E1%BB%81%20t%C3%A0i%20nghi%C3%AAn%20c%E1%BB%A9u%20khoa%20h%E1%BB%8Dc/papers%20source%20code/GRACE-summary/Runs-management/step1_backend_smoke/backend_manifest.json) dòng 2: Tác giả gõ nhầm tên thành `"Qwen2.5-Coder-30B-Instruct-Q4_K_M.gguf"` (lỗi sơ suất đánh máy tiền tố "2.5").
    3. Ngược lại, trong [`preregistration.md`](file:///d:/tai%20lieu%20hoc%20tap/%C4%90%E1%BB%81%20t%C3%A0i%20nghi%C3%AAn%20c%E1%BB%A9u%20khoa%20h%E1%BB%8Dc/papers%20source%20code/GRACE-summary/preregistration.md) (dòng 155–161) và [`configs/protocol.yaml`](file:///d:/tai%20lieu%20hoc%20tap/%C4%90%E1%BB%81%20t%C3%A0i%20nghi%C3%AAn%20c%E1%BB%A9u%20khoa%20h%E1%BB%8Dc/papers%20source%20code/GRACE-summary/configs/protocol.yaml) (dòng 24–28): Lại sao chép kế hoạch ban đầu từ Đề cương là `UD-Q4_K_XL` (16.45 GB) và thêm assertion chặn `assert "Q4_K_M" not in text` trong [`test_preregistration_integrity.py`](file:///d:/tai%20lieu%20hoc%20tap/%C4%90%E1%BB%81%20t%C3%A0i%20nghi%C3%AAn%20c%E1%BB%A9u%20khoa%20h%E1%BB%8Dc/papers%20source%20code/GRACE-summary/tests/test_preregistration_integrity.py) (dòng 47)!
  - **Kết luận**: Mô hình chạy thật là `Qwen3-Coder-30B-A3B-Instruct` dạng `Q4_K_M`. Cần sửa cả `backend_manifest.json` (bỏ chữ "2.5") và `preregistration.md`/`protocol.yaml` (ghi đúng `Q4_K_M` kèm mã SHA-256 `f6050b...`).

---

### 3. Bước 2: Dữ liệu, Kho Retrieval & Specs
- **Hiện trạng kho freeze thực tế**:
  - Dữ liệu freeze thực tế nằm tại [`01_Author_Baseline_Unified/output/research_freeze_20261101/freeze_manifest.json`](file:///d:/tai%20lieu%20hoc%20tap/%C4%90%E1%BB%81%20t%C3%A0i%20nghi%C3%AAn%20c%E1%BB%A9u%20khoa%20h%E1%BB%8Dc/papers%20source%20code/GRACE-summary/01_Author_Baseline_Unified/output/research_freeze_20261101/freeze_manifest.json):
    - Chuẩn hóa token C/C++, bỏ chú thích và khoảng trắng, giữ literal.
    - Loại bỏ mẫu trùng lặp chính xác với eval: Devign loại 22 mẫu, REVEAL loại 125 mẫu.
    - Loại bỏ nhóm donor mâu thuẫn nhãn: Devign loại 138 mẫu, REVEAL loại 426 mẫu.
    - Gắn cờ gần trùng (Jaccard token 3-gram $\ge 0,9$): Devign 260 test flags, REVEAL 296 test flags.
    - **Kho donor thực tế sau khử trùng**: Devign $= \mathbf{21.691}$ mẫu; REVEAL $= \mathbf{17.636}$ mẫu.
- ⚠️ **Lệch số liệu và sai lệch mã băm trong Pre-registration (HIGH)**:
  1. Trong [`preregistration.md`](file:///d:/tai%20lieu%20hoc%20tap/%C4%90%E1%BB%81%20t%C3%A0i%20nghi%C3%AAn%20c%E1%BB%A9u%20khoa%20h%E1%BB%8Dc/papers%20source%20code/GRACE-summary/preregistration.md) Bảng 7.1 (dòng 141 & 148):
     - Ghi Devign Clean Donors Bank là $\mathbf{21.711}$ (lệch 20 mẫu so với con số thực $21.691$).
     - Ghi REVEAL Clean Donors Bank là $\mathbf{17.620}$ (lệch 16 mẫu so với con số thực $17.636$).
  2. Toàn bộ các đường dẫn file kê khai trong `preregistration.md` Section 7.1 như:
     `data/raw/devign_train.jsonl`, `data/manifests/devign_donor_clean.jsonl`, `data/specs/devign_test.jsonl`
     **KHÔNG TỒN TẠI VẬT LÝ** trong thư mục `data/` trên đĩa (thư mục `data/` hiện chỉ có `data/b0_offline_dungs_data/`).
  3. Mã băm SHA-256 kê khai trong Bảng 7.1 (ví dụ `e456e20d...` cho raw train) không khớp với mã SHA-256 của các tệp freeze thực tế trong `01_Author_Baseline_Unified/output/research_freeze_20261101/devign/stats.json` (mã thực tế: `e9b8df66...`).

---

### 4. Bước 3: Bộ dựng Prompt, Probe Audit & Đánh giá Chấm mù
- **Dry-run 10/15 Arms trên toàn bộ 5.005 mẫu Validation**:
  - Dữ liệu vật lý: Thư mục [`Runs-management/dry_run_validation_20261102/`](file:///d:/tai%20lieu%20hoc%20tap/%C4%90%E1%BB%81%20t%C3%A0i%20nghi%C3%AAn%20c%E1%BB%A9u%20khoa%20h%E1%BB%8Dc/papers%20source%20code/GRACE-summary/Runs-management/dry_run_validation_20261102/) gồm 28 cấu hình (10 arm × 2 dataset + thêm seed 43, 44 cho B1-shuf và B2-rand).
  - Tổng số prompt được render thực tế: **$\mathbf{70.070}$ prompts** (khớp $100\%$ kiểm toán).
  - Rò rỉ nhãn ground-truth: $0$ mẫu ($0,0\%$).
  - Demo rỗng: $0,0\%$ trên B0, B1; $0,55\%$ trên Devign B2; $0,26\%$ trên REVEAL B2 (thỏa mãn tiêu chuẩn $\le 1\%$).
  - Graph thiếu: $0,11\%$ trên Devign; $1,19\%$ trên REVEAL (thỏa mãn tiêu chuẩn $\le 5\%$, đều được gắn cờ cảnh báo an toàn).
  - Sự cố cờ rò rỉ `reveal:validation:1629` (B1-shuf seed 44) do chuỗi `proto_item_append_text ( item , " Label: ` trong parser Wireshark đã được script [`verify_full_validation_dry_run.py`](file:///d:/tai%20lieu%20hoc%20tap/%C4%90%E1%BB%81%20t%C3%A0i%20nghi%C3%AAn%20c%E1%BB%A9u%20khoa%20h%E1%BB%8Dc/papers%20source%20code/GRACE-summary/Runs-management/verify_full_validation_dry_run.py) truy vết nguồn gốc C, xác nhận là false positive regex, không phải rò rỉ nhãn target.
- **Đánh giá Chấm mù 60 Prompt độc lập (Blind Human Review)**:
  - Tài liệu đối chiếu: [`Runs-management/prompt_audit_20261102/BIEN_BAN_PHAN_XU.md`](file:///d:/tai%20lieu%20hoc%20tap/%C4%90%E1%BB%81%20t%C3%A0i%20nghi%C3%AAn%20c%E1%BB%A9u%20khoa%20h%E1%BB%8Dc/papers%20source%20code/GRACE-summary/Runs-management/prompt_audit_20261102/BIEN_BAN_PHAN_XU.md) và [`manual_sample.jsonl`](file:///d:/tai%20lieu%20hoc%20tap/%C4%90%E1%BB%81%20t%C3%A0i%20nghi%C3%AAn%20c%E1%BB%A9u%20khoa%20h%E1%BB%8Dc/papers%20source%20code/GRACE-summary/Runs-management/prompt_audit_20261102/manual_sample.jsonl).
  - Chấm mù độc lập bởi 2 chuyên gia: HuuHieu03 (Hiếu) và Dung (Dũng) trên 60 mẫu phân tầng (30 Devign + 30 REVEAL).
  - Hệ số tương quan liên đánh giá (Inter-Rater Reliability):
    $$\text{Multiclass Cohen's Kappa } \kappa = \mathbf{0,8507} \ge 0,80$$
    $$\text{Binary Cohen's Kappa } \kappa = \mathbf{0,8485} \ge 0,80$$
  - Biên bản phân xử hòa giải chi tiết 4 trường hợp đặc thù (Mẫu 20 trùng tên hàm, Mẫu 39 demo dài chạm trần, Mẫu 45 Joern rỗng, Mẫu 35 demo cắt dưới 25% giữ trong `remediation_final.csv`). Biên bản có đầy đủ chữ ký điện tử xác nhận của 2 chuyên gia.
- **Định vị 5 Arm Tầng 3 (Contrastive Pair & Graph Extension)**:
  - 5 arm: `B1-full`, `B1-H2`, `B3`, `B3-nodiff`, `B3-swap`, `B3-flip`.
  - Được định vị trung thực, chuẩn xác trong mọi tài liệu: Là khối mở rộng đang chờ bộ trích xuất cặp tương phản (chưa sinh prompt, chưa inference, không ngụy tạo kết quả).

---

### 5. Bước 4: Đăng ký trước (Pre-registration) & Khóa ngưỡng Quyết định
- **Tình trạng Commit và Tag Git**:
  - Commit HEAD: [`cc64124`](file:///d:/tai%20lieu%20hoc%20tap/%C4%90%E1%BB%81%20t%C3%A0i%20nghi%C3%AAn%20c%E1%BB%A9u%20khoa%20h%E1%BB%8Dc/papers%20source%20code/GRACE-summary) (*"docs(osf): synchronize OSF preregistration draft with 10-arm dry-run, human review kappa 0.8507 and step 0/1 acceptance"*).
  - Git Tag: `prereg-v1` được gắn trực tiếp vào commit `cc64124`.
  - ⚠️ *Lưu ý*: Tồn tại đồng thời cả nhánh `prereg-v1` và tag `prereg-v1` dẫn đến cảnh báo git `refname 'prereg-v1' is ambiguous`.
- **Khóa 14 Ngưỡng Tối ưu $\tau^*$ từ Validation**:
  - File khóa: [`configs/thresholds.json`](file:///d:/tai%20lieu%20hoc%20tap/%C4%90%E1%BB%81%20t%C3%A0i%20nghi%C3%AAn%20c%E1%BB%A9u%20khoa%20h%E1%BB%8Dc/papers%20source%20code/GRACE-summary/configs/thresholds.json), [`configs/thresholds_flat.json`](file:///d:/tai%20lieu%20hoc%20tap/%C4%90%E1%BB%81%20t%C3%A0i%20nghi%C3%AAn%20c%E1%BB%A9u%20khoa%20h%E1%BB%8Dc/papers%20source%20code/GRACE-summary/configs/thresholds_flat.json) và [`Runs-management/thresholds.json`](file:///d:/tai%20lieu%20hoc%20tap/%C4%90%E1%BB%81%20t%C3%A0i%20nghi%C3%AAn%20c%E1%BB%A9u%20khoa%20h%E1%BB%8Dc/papers%20source%20code/GRACE-summary/Runs-management/thresholds.json).
  - Tối ưu hóa MCC trên lưới 99 điểm $[0,01; 0,99]$ hoàn toàn trên 5.005 mẫu Validation. Zero-Test-Exposure.
  - Mã băm `protocol_sha256` trong metadata khớp hoàn toàn với SHA-256 của `configs/protocol.yaml` (`791f3bd77975857e9e0db44545c25ea582817d3d0d3e46f64017c4358a3f2e29`).
- **Cơ chế Kiểm soát Gate `require_test_lock()`**:
  - Đã được triển khai tại [`Runs-management/validation_lock.py`](file:///d:/tai%20lieu%20hoc%20tap/%C4%90%E1%BB%81%20t%C3%A0i%20nghi%C3%AAn%20c%E1%BB%A9u%20khoa%20h%E1%BB%8Dc/papers%20source%20code/GRACE-summary/Runs-management/validation_lock.py) dòng 110. Chặn đứng mọi lời gọi suy luận trên tập Test nếu thiếu file khóa ngưỡng tương ứng với phiên dữ liệu và model identity.
- ⚠️ **Hai Lỗ hổng Cốt tử của Bước 4 (HIGH DEFECTS)**:
  1. **Lệch ngưỡng ngay trong văn bản `preregistration.md`**:
     - Trong [`configs/thresholds_flat.json`](file:///d:/tai%20lieu%20hoc%20tap/%C4%90%E1%BB%81%20t%C3%A0i%20nghi%C3%AAn%20c%E1%BB%A9u%20khoa%20h%E1%BB%8Dc/papers%20source%20code/GRACE-summary/configs/thresholds_flat.json):
       `devign|B2|42 = 0.70`, `devign|B2-rep|42 = 0.70`, `reveal|B2|42 = 0.12`, `reveal|B2-rep|42 = 0.12`.
     - Nhưng tại dòng 63–64 của [`preregistration.md`](file:///d:/tai%20lieu%20hoc%20tap/%C4%90%E1%BB%81%20t%C3%A0i%20nghi%C3%AAn%20c%E1%BB%A9u%20khoa%20h%E1%BB%8Dc/papers%20source%20code/GRACE-summary/preregistration.md):
       Vẫn ghi nhầm thành: `devign|B2|42 = 0.98`, `devign|B2-rep|42 = 0.98`, `reveal|B2|42 = 0.99`, `reveal|B2-rep|42 = 0.99`!
       *(Sở dĩ Pytest vẫn PASS là do unit test `test_thresholds_json_synchronization()` chỉ so sánh `thresholds.json` với `thresholds_flat.json` mà chưa assert trực tiếp nội dung văn bản markdown!)*
  2. **Gói Artifact OSF Draft PDF và ZIP bị lỗi thời (Stale Artifacts)**:
     - Thư mục [`Runs-management/osf_registration_draft_20261102/`](file:///d:/tai%20lieu%20hoc%20tap/%C4%90%E1%BB%81%20t%C3%A0i%20nghi%C3%AAn%20c%E1%BB%A9u%20khoa%20h%E1%BB%8Dc/papers%20source%20code/GRACE-summary/Runs-management/osf_registration_draft_20261102/) chứa `GRACE_OSF_DRAFT_20261102.pdf` và `GRACE_OSF_DRAFT_20261102.zip`.
     - Khi commit `cc64124` cập nhật `OSF_DRAFT.md` (đồng bộ trạng thái 10-arm dry-run và kappa 0.8507), **PDF và file ZIP đã không được re-build**!
     - Mã băm SHA-256 của `OSF_DRAFT.md` hiện tại (`728e4d3b...`, 21.761 bytes) không còn khớp với mã băm trong `attachment_sha256.json` (`81d055e1...`, 21.006 bytes). Bản PDF hiện tại vẫn in nội dung cũ: *"Phiếu reviewer_1/reviewer_2 hiện để trống"*!

---

## III. TRANH LUẬN PHẢN BIỆN (ADVERSARIAL DEBATE: L0 AUDITOR VS IMPROVEMENT WORKER)

Phiên tranh luận phản biện giả định đặt câu hỏi hoài nghi cao nhất: *"Liệu có điều gì làm cho kết quả nhìn thì đẹp nhưng thực tế còn lỗ hổng nghiêm trọng khiến reviewer quốc tế hoặc hội đồng bác bỏ hồ sơ OSF không?"*:

### Vòng 1: "Pytest đang 108/108 Pass xanh lè, sao lại bảo chưa sẵn sàng nộp OSF?"
- 🔴 **Skeptical L0 Auditor**: "108 test pass là một 'vỏ bọc hoàn hảo' nhưng che giấu sự phân mảnh dữ liệu. Ví dụ: `test_step0_offline_diagnostic.py` pass 13 test vì nó chạy trên mock dữ liệu tự sinh 50 dòng trong thư mục tạm `temp/`, hoàn toàn không kiểm tra tính hợp lệ của các file artifact chính thức trong `Runs-management/step0_diagnostic/`. Test `test_thresholds_json_synchronization` pass vì nó kiểm tra JSON khớp với JSON, nhưng không hề kiểm tra file `preregistration.md` đang ghi sai ngưỡng B2 là 0.98/0.99. Một reviewer mở file markdown đọc thấy 0.98, mở code thấy 0.70, họ sẽ kết luận nhóm nghiên cứu thiếu trung thực hoặc cẩu thả!"
- 🟢 **Improvement Worker**: "Đồng ý rằng có lỗi sơ suất trong việc đồng bộ text markdown sau khi chạy `lock_full_validation_thresholds.py`. Nhưng hãy nhìn vào bản chất: 14 ngưỡng trong `thresholds.json` là thật, được fit từ 5.005 mẫu Validation thật. Dữ liệu Bước 0 trên Devign và REVEAL là 2.732 và 2.274 mẫu thật, không phải mock! Đây là lỗi đánh máy tài liệu (documentation sync), không phải ngụy tạo số liệu (scientific fabrication). Chỉ cần sửa vài dòng text trong markdown và re-build PDF là giải quyết triệt để."

### Vòng 2: "Rốt cuộc mô hình dùng để đăng ký là Qwen2.5 hay Qwen3 MoE?"
- 🔴 **Skeptical L0 Auditor**: "Đây là tử huyệt của hồ sơ! Trong `backend_manifest.json`, bạn ghi rõ `Qwen2.5-Coder-30B-Instruct-Q4_K_M.gguf`. Nhưng trong `preregistration.md`, bạn lại huênh hoang ghi `Qwen3-Coder-30B-A3B-Instruct UD-Q4_K_XL` (MoE 48 experts). Qwen2.5 Dense 32B và Qwen3 MoE 3.3B active là hai mô hình hoàn toàn khác nhau về dung lượng, kiến trúc và suy luận! Nếu hội đồng tra cứu mã băm SHA `f6050b...` và thấy đó là file Qwen2.5 Q4_K_M của Kaggle, toàn bộ bài báo sẽ bị bác bỏ vì sai lệch định danh mô hình (model provenance violation)."
- 🟢 **Improvement Worker**: "Thực chất file mang mã SHA-256 `f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335` chính là `Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf` tải từ repo `ggml-org/Qwen3-Coder-30B-A3B-Instruct-GGUF` trên Kaggle (được ghi nhận nhất quán trong `evaluation_contract.yaml`, `RUN_GUIDE_KAGGLE.md`, `prepare_b0.py` và tất cả `run_manifest.json` của 30k+ record inference). `backend_manifest.json` chỉ bị gõ nhầm tiền tố `Qwen2.5`, còn `preregistration.md` thì sao chép nhầm tên `UD-Q4_K_XL` từ đề cương ban đầu. Cả hai codebase đều dùng chung một file vật lý duy nhất. Giải pháp chuẩn mực là: **Đồng bộ hóa 100% tên mô hình thành `Qwen3-Coder-30B-A3B-Instruct GGUF Q4_K_M` kèm mã SHA-256 `f6050b...`** trên toàn bộ văn bản."

### Vòng 3: "Test đã chạy trước trên Kaggle rồi, đăng ký trước có còn giá trị không?"
- 🔴 **Skeptical L0 Auditor**: "Theo `current_status.json`, bạn đã có 10.011 record Test của B0 và 10.011 record Test của B2. B0/B2 Test đã chạy từ 01/11, trong khi hôm nay 02/11 mới soạn OSF. Reviewer quốc tế sẽ chất vấn: 'Làm sao tôi tin được các bạn không nhìn vào Test rồi mới đi chỉnh prompt và chọn ngưỡng?'"
- 🟢 **Improvement Worker**: "Đề cương nghiên cứu và cộng đồng Open Science đã lường trước điều này:
  1. Chúng tôi không hề giấu giếm hay backdate! Tại Mục 1 của `preregistration.md`, Mục 2 của `protocol.yaml` và Section 2 của `OSF_DRAFT.md`, nhóm đưa ra **Test Exposure Disclosure** cực kỳ minh bạch: thừa nhận benchmark đã được thăm dò trước đó.
  2. Bằng chứng toán học chứng minh không có data snooping: Ngưỡng $\tau^*$ được tìm kiếm thuần túy bằng hàm cực đại hóa MCC trên Validation, có script `lock_full_validation_thresholds.py` ghi log `test_exposure: STRICTLY_NONE`.
  3. Để hợp thức hóa 100% trên OSF, chúng tôi **KHÔNG** chọn form 'Preregistration' tiêu chuẩn (dành cho nghiên cứu chưa thu thập dữ liệu), mà sẽ chọn form **'Secondary Data Analysis Preregistration'** hoặc **'Open-Ended Registration'** với lời tuyên thệ minh bạch dữ liệu."

### Vòng 4: "Tại sao thư mục `data/manifests/` và `data/specs/` lại không có trên đĩa?"
- 🔴 **Skeptical L0 Auditor**: "`preregistration.md` kê khai một danh mục mã băm rất đẹp từ dòng 136 đến 151, trỏ vào `data/raw/`, `data/manifests/`, `data/specs/`. Nhưng khi gõ lệnh kiểm tra, các thư mục này hoàn toàn biến mất! Người khác clone mã nguồn về không thể chạy lại được gì."
- 🟢 **Improvement Worker**: "Dữ liệu thô và specs không bị mất, mà đang nằm trong cây thư mục cấu trúc của repo tại `01_Author_Baseline_Unified/output/research_freeze_20261101/` và `01_Author_Baseline_Unified/output/local_full/`. Tuy nhiên, việc để đường dẫn trong `preregistration.md` lệch với cây thư mục thực tế là một thiếu sót nghiêm trọng về tính đóng gói. Chúng ta cần cập nhật đường dẫn chính xác và mã băm tương ứng từ `freeze_manifest.json` vào `preregistration.md` trước khi nộp OSF."

---

## IV. HƯỚNG DẪN CHI TIẾT CÁC BƯỚC NỘP HỒ SƠ LÊN OSF REGISTRIES

### 1. Chuẩn bị tài liệu trước khi bấm nút (Pre-submission Checklist)
Trước khi truy cập website OSF, bắt buộc phải hoàn tất 4 hành động chỉnh sửa cục bộ:
1. **Sửa text ngưỡng trong [`preregistration.md`](file:///d:/tai%20lieu%20hoc%20tap/%C4%90%E1%BB%81%20t%C3%A0i%20nghi%C3%AAn%20c%E1%BB%A9u%20khoa%20h%E1%BB%8Dc/papers%20source%20code/GRACE-summary/preregistration.md)**: Sửa dòng 63–64 thành:
   `devign|B2|42 = 0.70`, `devign|B2-rep|42 = 0.70`, `reveal|B2|42 = 0.12`, `reveal|B2-rep|42 = 0.12` (đồng bộ $100\%$ với `configs/thresholds.json`).
2. **Thống nhất định danh mô hình**: Đồng bộ tên mô hình trong `protocol.yaml`, `preregistration.md` và `backend_manifest.json` thành: `Qwen3-Coder-30B-A3B-Instruct GGUF Q4_K_M` kèm mã SHA-256 `f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335`.
3. **Đồng bộ số liệu donor Bước 2**: Cập nhật số liệu donor trong `preregistration.md` thành $21.691$ (Devign) và $17.636$ (REVEAL), trỏ đường dẫn đúng vào `01_Author_Baseline_Unified/output/research_freeze_20261101/`.
4. **Re-build gói OSF Draft**: Sinh lại file `output/pdf/GRACE_OSF_DRAFT_20261102.pdf`, cập nhật lại `attachment_sha256.json` và đóng gói lại `GRACE_OSF_DRAFT_20261102.zip`.

---

### 2. Các bước thao tác trực tiếp trên OSF (https://osf.io/registries)

#### Bước 1: Khởi tạo Registration
1. Truy cập: **https://osf.io/registries**.
2. Đăng nhập tài khoản OSF của Chủ nhiệm đề tài / Thành viên đại diện (Hiếu hoặc Dũng).
3. Bấm vào nút **"Add New"** $\rightarrow$ chọn **"Add New Registration"**.
4. Chọn project nguồn OSF (nếu đã tạo OSF Project trước đó) hoặc chọn **"Register a project from scratch"**.

#### Bước 2: Lựa chọn Biểu mẫu Đăng ký (Registration Template) — CỰC KỲ QUAN TRỌNG!
- ❌ **KHÔNG CHỌN**: "OSF Preregistration" mặc định nếu không khai báo tiếp xúc dữ liệu (vì mẫu này mặc định nghiên cứu chưa có dữ liệu).
- ✅ **KHUYẾN NGHỊ LỰA CHỌN 1 TRONG 2 MẪU SAU**:
  - **Lựa chọn A (Tốt nhất & Minh bạch nhất)**: Chọn mẫu **"Secondary Data Analysis Preregistration"** (Mẫu chuẩn quốc tế cho việc sử dụng lại benchmark hoặc dữ liệu đã có).
  - **Lựa chọn B (Nhanh & Linh hoạt)**: Chọn mẫu **"Open-Ended Registration"** (Cho phép đính kèm toàn văn tài liệu PDF tiền đăng ký và tóm tắt đề cương).

---

### 3. Hướng dẫn điền từng trường thông tin (Field-by-Field Guide)

#### A. Metadata chung (General Information)
- **Title (Tiêu đề)**:
  `A Diagnostic and Mechanistic Replication of GRACE on Open-Weight Code LLMs`
- **Description (Tóm tắt ngắn gọn)**:
  `This preregistered study investigates whether the GRACE vulnerability detection framework (graph augmentation + retrieved in-context demonstrations) replicates on open-weight LLMs (Qwen-Coder 30B family) across the Devign and ReVeal benchmarks. Through an offline diagnostic suite (repair/harm matrices, oracle ceilings, matched meta-models) and systematic ablation probes (graph shuffling, label flipping, label removal), we evaluate the true mechanistic contribution of graphs and demonstrations versus cheap supervised baselines (CodeT5 logistic regression). All validation thresholds and analysis protocols are pre-locked prior to confirmatory testing.`
- **Contributors (Tác giả & Cộng sự)**:
  Thêm email/tài khoản OSF của các thành viên: HuuHieu03 (Hiếu), Dung (Dũng) và các cộng sự/GVHD.
- **License**: Creative Commons Attribution 4.0 International (CC-BY 4.0).
- **Category**: Project / Pre-registration.

#### B. Khai báo Dữ liệu & Tiếp xúc (Data Disclosure & Sampling Plan)
- **Data Collection / Existing Data Status**:
  Chọn option: **"Registration prior to analysis of the data"** HOẶC **"Data exist, but have not been accessed/analyzed"** (đối với confirmatory split mới), đồng thời đính kèm văn bản giải trình:
  > *"The benchmark datasets (Devign and ReVeal) were explored in preliminary/historical experiments (API runs and dev subsets). Confirmatory model decisions, prompt templates, and the 14 optimal classification thresholds (tau*) are strictly fitted on the official Validation set prior to unblinding/evaluating the confirmatory Test runs. Test exposure history is fully disclosed in Section 1 of the attached protocol."*
- **Datasets & Sample Sizes**:
  - Devign: 2,732 Validation samples, 2,732 Test samples.
  - ReVeal: 2,273 Validation samples, 2,274 Test samples.
  - Total Target Volume per arm: 10,011 samples.
  - Frozen Clean Donors: 21,691 (Devign), 17,636 (ReVeal).

#### C. Kế hoạch Thống kê & Phán quyết (Analysis Plan)
- **Primary Hypotheses (Bảng 4.3)**:
  Điền danh sách 11 giả thuyết từ H1.1 đến H6.1 (Copy nguyên văn từ Mục 2 của [`preregistration.md`](file:///d:/tai%20lieu%20hoc%20tap/%C4%90%E1%BB%81%20t%C3%A0i%20nghi%C3%AAn%20c%E1%BB%A9u%20khoa%20h%E1%BB%8Dc/papers%20source%20code/GRACE-summary/preregistration.md)).
- **Statistical Significance & Decision Rules**:
  - Biểu quyết 4 nhánh: `benefit` ($\text{CI} > 0$ và $\Delta \ge \delta$), `no_meaningful_benefit` ($\text{cận trên} < \delta$), `harm` ($\text{CI} < 0$), `inconclusive` (chứa 0 và $\ge \delta$).
  - Biên thực chất: $\delta_\text{MCC} = 0,03$, $\delta_\text{AUROC} = 0,02$, $\delta_\text{BA} = 0,01$, $\delta_\text{meta} = 0,02$.
  - Kiểm định: Paired Cluster Bootstrap 5.000 lượt lặp (seed 20261117).
  - Đơn vị gom cụm: `commit_id` (Devign, 2.068 cụm Test), `file_hash` (REVEAL, 646 cụm Test).
  - Hiệu chỉnh đa kiểm định: Holm-Bonferroni.

---

### 4. Danh mục Hồ sơ & Tệp đính kèm nộp lên OSF (OSF Bundle Inventory)

Nhóm cần upload gói tệp đính kèm (hoặc đính kèm file ZIP) gồm các thành phần sau:

```
GRACE_OSF_SUBMISSION_BUNDLE/
├── 1_PREREGISTRATION_DOCUMENT.pdf        # Bản PDF chính thức biên dịch từ preregistration.md
├── 2_PROTOCOL_SPECIFICATION.yaml         # configs/protocol.yaml (chứa đầy đủ parameters)
├── 3_LOCKED_THRESHOLDS.json              # configs/thresholds.json (14 ngưỡng tau* khóa từ Validation)
├── 4_LOCKED_THRESHOLDS_FLAT.json         # configs/thresholds_flat.json
├── 5_STEP0_OFFICIAL_REPORTS/             # Báo cáo nghiệm thu Bước 0 (JSON + MD + Canonical CSV)
│   ├── devign/ (diagnostic_report_devign.json, diagnostic_summary_devign.md)
│   └── reveal/ (diagnostic_report_reveal.json, diagnostic_summary_reveal.md)
├── 6_STEP1_BACKEND_SMOKE/                # Báo cáo nghiệm thu Bước 1
│   ├── backend_manifest.json
│   ├── smoke_test_report.json
│   └── throughput_benchmark.json
├── 7_STEP3_AUDIT_AND_HUMAN_REVIEW/       # Báo cáo nghiệm thu Bước 3
│   ├── BIEN_BAN_PHAN_XU.md               # Biên bản hòa giải có chữ ký Hiếu & Dũng (kappa=0.8507)
│   ├── manual_sample.jsonl               # 60 prompt chấm mù
│   └── dry_run_summary_70k.json          # Tóm tắt dry-run 70.070 prompt
└── 8_CHECKSUMS_AND_MANIFEST.json         # Danh mục mã băm SHA-256 toàn bộ các tệp trên
```

#### Bước 5: Xem trước (Review) và Đệ trình (Submit)
1. Chọn chế độ hiển thị:
   - **Public Immediately** (Công khai ngay lập tức và cấp mã DOI).
   - HOẶC **Enter an embargo period** (Bảo lưu bí mật tối đa 4 năm, phù hợp nếu muốn bảo mật trước khi gửi bài hội thảo).
2. Kiểm tra lại toàn bộ form tại trang **Review Preview**.
3. Bấm **"Submit"**. Toàn bộ tác giả có tên trong danh sách Contributors sẽ nhận email thông báo xác nhận từ OSF trong vòng 48 giờ.

---

## V. CÁC CÂU HỎI CÒN LẠI & KHOẢNG TRỐNG KỸ THUẬT (REMAINING QUESTIONS & GAPS)

1. **Các câu hỏi vẫn chưa được giải quyết dứt điểm**:
   - Tên mô hình chính thức đăng ký: Thống nhất loại bỏ tiền tố `Qwen2.5` trong `backend_manifest.json` và loại bỏ `UD-Q4_K_XL` trong `preregistration.md`/`protocol.yaml` để quy về chuẩn duy nhất: `Qwen3-Coder-30B-A3B-Instruct GGUF Q4_K_M` (file SHA `f6050b...`).
   - Đường dẫn thư mục dữ liệu: Quy định rõ vị trí lưu trữ chính thức của dữ liệu freeze là `01_Author_Baseline_Unified/output/research_freeze_20261101/` hay tạo symlink vào `data/manifests/` và `data/specs/`.

2. **Các khía cạnh của bài toán cần điều tra sâu hơn**:
   - Chạy lại phân tích Bootstrap Bước 0 với $B = 5.000$ lượt lặp (thay vì 1.000 lượt) để xuất lại báo cáo JSON/MD khớp 100% với thông số quy định trong Đề cương.
   - Thêm unit test trong `tests/test_preregistration_integrity.py` để assert trực tiếp các con số ngưỡng $\tau^*$ in trong văn bản Markdown `preregistration.md`, tránh việc sửa file JSON nhưng quên cập nhật tài liệu văn bản.

3. **Trọng tâm mà cuộc điều tra / nhóm thực hiện tiếp theo cần ưu tiên trước nhất**:
   - **Ưu tiên 1**: Sửa text ngưỡng tại dòng 63–64 của `preregistration.md` ($0,98 \rightarrow 0,70$ và $0,99 \rightarrow 0,12$).
   - **Ưu tiên 2**: Cập nhật `backend_manifest.json` và `preregistration.md` để thống nhất 100% định danh `Qwen3-Coder-30B-A3B-Instruct GGUF Q4_K_M`.
   - **Ưu tiên 3**: Cập nhật lại Bảng 7.1 của `preregistration.md` khớp số liệu $21.691$ và $17.636$ donor kèm mã băm thực tế.
   - **Ưu tiên 4**: Re-build file PDF và ZIP tại `Runs-management/osf_registration_draft_20261102/` rồi nộp lên OSF theo form Secondary Data Analysis.

---
*Báo cáo được kiểm toán độc lập và lập bởi Antigravity Sub-agent theo cơ chế Anti-Hallucination & Evidence-Grounded.*
</SYSTEM_MESSAGE>