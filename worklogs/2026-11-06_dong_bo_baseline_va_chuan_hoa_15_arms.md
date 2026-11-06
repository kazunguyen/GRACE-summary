---
id: "dong-bo-baseline-va-chuan-hoa-15-arms-20261106"
title: "Đồng bộ baseline-unified, chuẩn hóa cấu trúc 15 Diagnostic Arms và kiểm toán tiến độ thực thi"
author: "Hữu Hiệu & Antigravity (AI Assistant)"
author_type: "Human researcher & AI assistant"
requested_by: "Người dùng trong chat"
recorded_at: "2026-11-06T09:15:00+07:00"
timezone: "Asia/Bangkok"
work_date: "2026-11-06"
record_type: "repository_harmonization_and_execution_status"
status: "completed"
---

# Đồng bộ Nhánh Baseline, Chuẩn hóa Cấu trúc 15 Arms và Kiểm toán Hiện trạng Thực nghiệm

## 1. Đồng bộ Git & Nghiệm thu Dữ liệu từ PR #12 (Baseline Unified)
- Đã kéo và hợp nhất toàn bộ 8 commit từ nhánh `origin/baseline-unified` (PR #12 do đồng đội Quang Dũng nạp lên) vào nhánh làm việc cục bộ `hieu`.
- Giải quyết xung đột merge conflict trong `.gitignore`: bảo toàn phân lập bí mật (secrets isolation), không để lọt các file token Kaggle (`*kaggle*.json`, `Runs-management/kaggle_*_config/`) hoặc các checkpoint nhị phân dung lượng lớn vào Git index.
- Vượt qua 100% các kiểm toán tự động của OSF: `tests/test_preregistration_integrity.py` (6/6 pass) và toàn bộ 31 test bộ công cụ chẩn đoán (`test_probes.py`, `test_stats_and_complementarity.py`).

### Kết quả Thực nghiệm Quan trọng Thu nhận từ PR #12:
1. **Arm `B2-flip` (Đảo nhãn demonstration) — Hoàn thành 100% Census cả Val & Test ($10.011$ mẫu)**:
   - Kernel thực thi: `quangdung1111/02-kaggle-qwen-q4-b2-flip-ipynb` (chạy 8h16m).
   - Thừa kế trực tiếp $\tau^*$ từ B2 (`policy: inherit_from:B2`, Devign $\tau^*=0.70$, ReVeal $\tau^*=0.12$).
   - Kết quả đo lường:
     * Devign Test ($2.732$ mẫu): **AUROC = 0.5240** | MCC = 0.0395 | Balanced Acc = 51.90% | F1 = 0.5528
     * Devign Validation ($2.732$ mẫu): **AUROC = 0.5137** | MCC = 0.0073 | Balanced Acc = 50.36% | F1 = 0.5157
     * ReVeal Test ($2.274$ mẫu): **AUROC = 0.5261** | MCC = 0.0009 | Balanced Acc = 50.07% | F1 = 0.1636
     * ReVeal Validation ($2.273$ mẫu): **AUROC = 0.5256** | MCC = 0.0095 | Balanced Acc = 50.80% | F1 = 0.1550
   - *Ý nghĩa khoa học*: Khi đảo nhãn demo, toàn bộ hiệu năng sụp đổ về mức ngẫu nhiên ($\approx 0.50$ và MCC $\approx 0$), chứng minh LLM phụ thuộc sâu sắc vào nhãn demo thay vì chỉ phân tích cú pháp mã nguồn.

2. **Arm `B2-rand` (Random Demonstration Donor Probe) — Thu nhận $7.789 / 15.015$ mẫu Validation**:
   - Kernel thực thi: `duchuynguyen1802/02-kaggle-qwen-q4-b2-rand-ipynb`.
   - Seed 42 ($5.005$ mẫu — 100% census Validation):
     * Devign Val ($2.732$ mẫu): **AUROC = 0.5307** | MCC = 0.0321 | Balanced Acc = 51.62%
     * ReVeal Val ($2.273$ mẫu): **AUROC = 0.5638** | MCC = 0.0575 | Balanced Acc = 54.52%
   - Seed 43: Đã chạy xong 100% Devign Val ($2.732$ mẫu, **AUROC = 0.5289**) và 52 mẫu ReVeal Val.

3. **`B2 Donor Rerun 66` (Khắc phục 66 ca ô nhiễm donor cho baseline tác giả)**:
   - Hoàn thành trọn vẹn 100% cả 28 ca Devign validation (AUROC = 0.6875, MCC = 0.3500) và 38 ca Devign test (AUROC = 0.5938, MCC = 0.2753).

4. **Tài sản Khoa học cho Arm `B1-H2`**:
   - Nạp toàn bộ dữ liệu ứng viên v5 và v6 ($5.005$ prompt đầy đủ nhãn).
   - Bổ sung bộ cache Tokenizer Qwen chuẩn (`merges.txt`, `tokenizer.json`).
   - Bổ sung hồ sơ kiểm toán thủ công 60 ca đối chiếu double-blind và notebook pilot 100 mẫu trên Colab L4.

---

## 2. Giải quyết Trùng lặp Chỉ mục 11 và Chuẩn hóa Thư mục 15 Arms
### 2.1. Giải quyết xung đột số thứ tự 11
- Sau khi hợp nhất PR #12, xuất hiện hai thư mục mang cùng tiền tố số `11_`:
  1. `11_Arm_B1H2_Evidence` (nhập từ `baseline-unified` chứa toàn bộ hồ sơ, audit và pipeline của arm B1-H2).
  2. `11_Arm_B2_LabelOnly` (thư mục cục bộ cho arm B2-labelonly).
- **Hành động xử lý**: Đã thực hiện `git mv 11_Arm_B2_LabelOnly 12_Arm_B2_LabelOnly`, bảo toàn 100% lịch sử commit và nội dung không hề bị gián đoạn hay sửa đổi.

### 2.2. Khởi tạo đầy đủ thư mục cho gia đình B3
Để đảm bảo cấu trúc dự án chuẩn hóa, trực quan và bao phủ toàn diện 15 Diagnostic Arms theo hợp đồng OSF (`configs/arms.yaml` và `AGENTS.md`), đã bổ sung 4 thư mục chuyên biệt cho họ B3:
- [`13_Arm_B3_Contrastive`](../13_Arm_B3_Contrastive/): Chẩn đoán Contrastive Demonstration + Key difference (Base: B1, RQ2 & RQ4).
- [`14_Arm_B3_NoDiff`](../14_Arm_B3_NoDiff/): Chẩn đoán Contrastive Demonstration lược bỏ khối Key difference (Base: B3, RQ2).
- [`15_Arm_B3_Swap`](../15_Arm_B3_Swap/): Probe đảo ngược thứ tự 2 mẫu demonstration tương phản (kế thừa $\tau^*$ từ B3).
- [`16_Arm_B3_Flip`](../16_Arm_B3_Flip/): Probe đảo ngược nhãn cả 2 mẫu demonstration tương phản (kế thừa $\tau^*$ từ B3).

---

## 3. Bảng Kiểm kê Chính xác Toàn diện Hiện trạng 15 Diagnostic Arms

| STT | Thư mục Dự án | Tên Arm | Khác biệt Cốt lõi | Trạng thái Validation ($N=5.005$) | Trạng thái Test ($N=5.006$) | Quy tắc Ngưỡng $\tau^*$ theo Hợp đồng OSF |
| :---: | :--- | :---: | :--- | :--- | :--- | :--- |
| 01 | `01_Author_Baseline_Unified` | **B2** | GRACE đầy đủ (Prefix graph + retrieved demo) | **Hoàn thành** (Census $5.005$) | **Hoàn thành** (Census $5.006$) | Đã khóa: Devign $\tau^*=0.70$, ReVeal $\tau^*=0.12$ |
| 02 | `02_Arm_B0_Source_Only` | **B0** | Zero-shot mã nguồn thuần | **Hoàn thành** (Census $5.005$) | **Hoàn thành** (Census $5.006$) | Đã khóa: Devign $\tau^*=0.08$, ReVeal $\tau^*=0.44$ |
| 03 | `03_Arm_B1_Graph_Only` | **B1** | Graph prefix (không demonstration) | **Hoàn thành** (Census $5.005$) | **Hoàn thành** (Census $5.006$) | Đã khóa: Devign $\tau^*=0.88$, ReVeal $\tau^*=0.74$ |
| 04 | `04_Arm_B2_Flip` | **B2-flip** | Đảo nhãn demonstration | **Hoàn thành** (Census $5.005$) | **Hoàn thành** (Census $5.006$) | Thừa kế từ B2 (Đã hoàn thành 100% 10.011 mẫu) |
| 05 | `05_Arm_B2_Rep` | **B2-rep** | Lặp truy vấn không cache | **Hoàn thành** (Census $5.005$) | Chưa chạy ($0/5.006$) | Thừa kế từ B2 -> **ĐỦ ĐIỀU KIỆN CHẠY TEST NGAY** |
| 06 | `06_Arm_B2_Rand` | **B2-rand** | Demonstration chọn ngẫu nhiên | Đã có $7.789 / 15.015$ mẫu (Seed 42 100%, Seed 43 Devign 100%) | Chưa chạy | Chờ đủ 3 seed Validation để khóa $\tau^*$ |
| 07 | `07_Arm_B2_Donor_Rerun_66` | **B2-clean** | Khắc phục 66 ca nhiễm bẩn donor B2 | **Hoàn thành** (28/28) | **Hoàn thành** (38/38) | Đã khóa và tích hợp vào baseline |
| 08 | `08_Arm_B1_Shuf` | **B1-shuf** | Tráo topo đồ thị CPG | **Hoàn thành** (Seed 42 & 43: $10.010$ mẫu 100%; Seed 44: $2.113$) | Chưa chạy | Chờ khóa $\tau^*$ chính thức |
| 09 | `09_Arm_B1_Full` | **B1-full** | Giữ đồ thị CPG đầy đủ (lấp đầy $1.500$ token) | **Hoàn thành** (Census $5.005$) | Chưa chạy | Chờ khóa $\tau^*$ chính thức |
| 10 | `10_Arm_B2_NoLabel` | **B2-nolabel** | Bỏ nhãn demonstration | **Hoàn thành** (Census $5.005$) | Chưa chạy | Chờ khóa $\tau^*$ chính thức |
| 11 | `11_Arm_B1H2_Evidence` | **B1-H2** | Cụm evidence đồ thị H2 | Đã chuẩn bị specs v5/v6, sẵn sàng nạp Colab/Kaggle | Chưa chạy | Chờ chạy Val & khóa $\tau^*$ |
| 12 | `12_Arm_B2_LabelOnly` | **B2-labelonly** | Chỉ câu gợi ý nhãn, không demo code | **Hoàn thành** (Census $5.005$) | Chưa chạy | Chờ khóa $\tau^*$ chính thức |
| 13 | `13_Arm_B3_Contrastive` | **B3** | Cặp tương phản + Key difference | **Devign 100% ($2.732$), ReVeal $1.276/2.273$** | Chưa chạy | Khóa $\tau^*$ riêng trên Validation |
| 14 | `14_Arm_B3_NoDiff` | **B3-nodiff** | Cặp tương phản bỏ Key difference | Đã nạp bundle, chuẩn bị chạy nối tiếp | Chưa chạy | Khóa $\tau^*$ riêng trên Validation (không dùng chung) |
| 15 | `15_Arm_B3_Swap` | **B3-swap** | Đảo thứ tự 2 demo tương phản | Không cần (Probe dành cho Test) | Chưa chạy | Thừa kế $\tau^*$ từ B3 |
| 16 | `16_Arm_B3_Flip` | **B3-flip** | Đảo nhãn cả 2 demo tương phản | Không cần (Probe dành cho Test) | Chưa chạy | Thừa kế $\tau^*$ từ B3 |

---

## 4. Nghiệm thu Đợt chạy B3 trên `thanhduy9a4tv` và Hiện trạng Tài nguyên Kaggle
### 4.1. Kết quả Đợt chạy Batch 9h `thanhduy9a4tv/grace-b3-validation`
- Kernel kết thúc an toàn đúng deadline timer (`COMPLETE`), xuất file checkpoint `grace_b3_validation_checkpoint.zip` (846 KB).
- Script theo dõi tự động đã tải về và nạp vào thư mục `runs/final/`:
  * **B3 Devign Validation**: Hoàn tất 100% census ($2.732 / 2.732$ mẫu) -> **AUROC: 0.5267**, MCC: 0.0022, Balanced Acc: 50.10%.
  * **B3 ReVeal Validation**: Đạt **1.276 / 2.273 mẫu** (còn 997 mẫu).
  * **B3-nodiff**: Chưa kịp chạy trong phiên này ($0 / 5.005$ mẫu).

### 4.2. Hiện trạng Hạn mức Cụm 4 Tài khoản Kaggle
1. **`thanhduy9a4tv`**:
   - Sau khi kết thúc batch B3, tài khoản đã chạm trần tối đa **30.00 / 30.00 giờ GPU/tuần** (`Maximum weekly GPU quota reached`).
   - Tạm thời không thể nhận thêm job GPU trong tuần này.
2. **`huuhieu3333`**:
   - Model prepare notebook `huuhieu3333/qwen3coder30b-prepare-notebook` đã lưu sẵn 18.5GB GGUF trong cache CPU (`COMPLETE`).
   - Nguyên vẹn **30.00 / 30.00 giờ GPU T4 x2 miễn phí**.
   - Sẵn sàng nhận job nối tiếp ngay lập tức.
3. **`lznt123`**:
   - Đã cấu hình và kích hoạt thành công API key.
   - Notebook prepare model đang chạy nạp cache trên CPU (`RUNNING`).
   - Bảo toàn nguyên vẹn **30.00 / 30.00 giờ GPU T4 x2**.
4. **`tomandjerry223`**:
   - Đã hoàn tất B1-shuf đa hạt giống và B2-rep validation; GPU tuần này còn ~40 phút dự phòng.

---

## 5. Kế hoạch Hành động Ngay (Immediate Execution Plan)
1. **Chuyển tiếp chạy B3 & B3-nodiff sang `huuhieu3333`**:
   - Đã tạo kịch bản `Runs-management/launch_resume_b3_huuhieu.py`.
   - Nạp dataset inputs (12.7 MB) và checkpoint (846 KB) lên `huuhieu3333`.
   - Khởi chạy kernel resume: tự động bỏ qua 2.732 Devign B3, chạy tiếp 997 ReVeal B3 (~45 phút), sau đó chạy toàn bộ B3-nodiff ($5.005$ mẫu, ~3.5 giờ). Dự kiến tổng thời gian ~4.1 giờ GPU.
2. **Chạy song song hoặc kế tiếp**:
   - Dùng tài khoản `lznt123` (sau khi cache xong) để khởi chạy `B1-H2` validation hoặc chạy census Test cho `B2-rep`.
