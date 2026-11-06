---
id: "dong-bo-baseline-va-chuan-hoa-15-arms-20261106"
title: "Đồng bộ baseline-unified, chuẩn hóa cấu trúc 15 Diagnostic Arms và quản lý cụm Kaggle"
author: "Hữu Hiệu & Antigravity (AI Assistant)"
author_type: "Human researcher & AI assistant"
requested_by: "Người dùng trong chat"
recorded_at: "2026-11-06T08:35:00+07:00"
timezone: "Asia/Bangkok"
work_date: "2026-11-06"
record_type: "repository_harmonization_and_execution_status"
status: "completed"
---

# Đồng bộ Nhánh Baseline, Chuẩn hóa Cấu trúc Thư mục 15 Arms và Tiến độ Thực thi

## 1. Đồng bộ và Hợp nhất Git (Baseline Synchronization)
- Đã kéo (pull) và hợp nhất toàn bộ 8 commit mới từ nhánh `origin/baseline-unified` (PR #12 do đồng đội Quang Dũng nạp lên) vào nhánh làm việc cục bộ `hieu`.
- Xử lý xung đột merge conflict trong file `.gitignore` một cách an toàn và triệt để: bảo toàn phân lập bí mật (secrets isolation), không để lọt các file token Kaggle (`*kaggle*.json`, `Runs-management/kaggle_*_config/`) hoặc các checkpoint nhị phân dung lượng lớn vào Git index.
- Tất cả các kiểm định tính toàn vẹn tiền đăng ký OSF (`tests/test_preregistration_integrity.py`) và bộ test chẩn đoán (`test_probes.py`, `test_stats_and_complementarity.py`) đều đạt **100% PASS** (47/47 tests).

## 2. Giải quyết Trùng lặp Chỉ mục 11 và Chuẩn hóa Thư mục 15 Arms
### 2.1. Giải quyết xung đột số thứ tự 11
- Sau khi hợp nhất PR #12, xuất hiện hai thư mục mang cùng tiền tố số `11_`:
  1. `11_Arm_B1H2_Evidence` (nhập từ `baseline-unified` chứa toàn bộ hồ sơ, audit và pipeline của arm B1-H2).
  2. `11_Arm_B2_LabelOnly` (thư mục cục bộ cho arm B2-labelonly).
- **Hành động xử lý**: Đã thực hiện `git mv 11_Arm_B2_LabelOnly 12_Arm_B2_LabelOnly`, bảo toàn 100% lịch sử commit và nội dung không hề bị gián đoạn hay sửa đổi.

### 2.2. Khởi tạo đầy đủ thư mục cho gia đình B3
Để đảm bảo cấu trúc dự án chuẩn hóa, trực quan và bao phủ toàn diện 15 Diagnostic Arms theo hợp đồng OSF (`configs/arms.yaml` và `AGENTS.md`), đã bổ sung 4 thư mục chuyên biệt cho họ B3:
- `13_Arm_B3_Contrastive`: Chẩn đoán Contrastive Demonstration + Key difference (Base: B1, RQ2 & RQ4).
- `14_Arm_B3_NoDiff`: Chẩn đoán Contrastive Demonstration lược bỏ khối Key difference (Base: B3, RQ2).
- `15_Arm_B3_Swap`: Probe đảo ngược thứ tự 2 mẫu demonstration tương phản (kế thừa $\tau^*$ từ B3).
- `16_Arm_B3_Flip`: Probe đảo ngược nhãn cả 2 mẫu demonstration tương phản (kế thừa $\tau^*$ từ B3).

---

## 3. Bảng Kiểm kê và Trạng thái Thực thi Toàn diện 15 Diagnostic Arms

| STT | Thư mục Dự án | Tên Arm | Khác biệt Cốt lõi | Trạng thái Validation ($N=5.005$) | Trạng thái Test ($N=5.006$) | Tính hợp lệ Chạy Test ngay |
| :---: | :--- | :---: | :--- | :--- | :--- | :---: |
| 01 | `01_Author_Baseline_Unified` | **B2** | GRACE đầy đủ (Prefix graph + retrieved demo) | **Hoàn thành** (Census $5.005$) | **Hoàn thành** (Census $5.006$) | Đã xong |
| 02 | `02_Arm_B0_Source_Only` | **B0** | Zero-shot mã nguồn thuần | **Hoàn thành** (Census $5.005$) | **Hoàn thành** (Census $5.006$) | Đã xong |
| 03 | `03_Arm_B1_Graph_Only` | **B1** | Graph prefix (không demonstration) | **Hoàn thành** (Census $5.005$) | **Hoàn thành** (Census $5.006$) | Đã xong |
| 04 | `04_Arm_B2_Flip` | **B2-flip** | Đảo nhãn demonstration | **Hoàn thành** (Census $5.005$) | Đang dở dang (Devign 230/2.732) | **ĐỦ ĐIỀU KIỆN CHẠY NGAY** (Dùng $\tau^*$ từ B2) |
| 05 | `05_Arm_B2_Rep` | **B2-rep** | Lặp truy vấn không cache | **Hoàn thành** (Census $5.005$) | Chưa chạy | **ĐỦ ĐIỀU KIỆN CHẠY NGAY** (Dùng $\tau^*$ từ B2) |
| 06 | `06_Arm_B2_Rand` | **B2-rand** | Demonstration chọn ngẫu nhiên | Đang chạy (Đã có 4.798 samples) | Chưa chạy | Chờ xong Val & khóa $\tau^*$ |
| 07 | `07_Arm_B2_Donor_Rerun_66` | **B2-clean** | Khắc phục 66 ca nhiễm bẩn donor B2 | **Hoàn thành** (66/66) | **Hoàn thành** | Đã xong |
| 08 | `08_Arm_B1_Shuf` | **B1-shuf** | Tráo topo đồ thị CPG | **Hoàn thành** (Seed 42 & 43: $10.010$ samples; Seed 44: $2.113$) | Chưa chạy | Chờ khóa $\tau^*$ chính thức |
| 09 | `09_Arm_B1_Full` | **B1-full** | Giữ đồ thị CPG đầy đủ (lấp đầy $1.500$ token) | **Hoàn thành** (Census $5.005$) | Chưa chạy | Chờ khóa $\tau^*$ chính thức |
| 10 | `10_Arm_B2_NoLabel` | **B2-nolabel** | Bỏ nhãn demonstration | **Hoàn thành** (Census $5.005$) | Chưa chạy | Chờ khóa $\tau^*$ chính thức |
| 11 | `11_Arm_B1H2_Evidence` | **B1-H2** | Cụm evidence đồ thị H2 | Đã chuẩn bị specs v5/v6, sẵn sàng nạp Colab/Kaggle | Chưa chạy | Chờ chạy Val & khóa $\tau^*$ |
| 12 | `12_Arm_B2_LabelOnly` | **B2-labelonly** | Chỉ câu gợi ý nhãn, không demo code | **Hoàn thành** (Census $5.005$) | Chưa chạy | Chờ khóa $\tau^*$ chính thức |
| 13 | `13_Arm_B3_Contrastive` | **B3** | Cặp tương phản + Key difference | **Đang chạy GPU Kaggle** (`thanhduy9a4tv`) | Chưa chạy | Chờ xong Val & khóa $\tau^*$ |
| 14 | `14_Arm_B3_NoDiff` | **B3-nodiff** | Cặp tương phản bỏ Key difference | **Đang chạy GPU Kaggle** (`thanhduy9a4tv`) | Chưa chạy | Chờ xong Val & khóa $\tau^*$ |
| 15 | `15_Arm_B3_Swap` | **B3-swap** | Đảo thứ tự 2 demo tương phản | Không cần (Probe dành cho Test) | Chưa chạy | Chờ B3 khóa $\tau^*$ để kế thừa |
| 16 | `16_Arm_B3_Flip` | **B3-flip** | Đảo nhãn cả 2 demo tương phản | Không cần (Probe dành cho Test) | Chưa chạy | Chờ B3 khóa $\tau^*$ để kế thừa |

---

## 4. Tình trạng Quản lý và Điều phối Tài nguyên Kaggle
Nhóm hiện đang quản lý song song 4 tài khoản Kaggle phục vụ chạy batch song song:
1. **`thanhduy9a4tv`**:
   - Đang chạy kernel `thanhduy9a4tv/grace-b3-validation` (GPU T4 x2) cho cặp B3 và B3-nodiff validation ($5.005 \times 2 = 10.010$ prompt).
   - Tiến độ: Đang ở giai đoạn chạy các giờ cuối của chu kỳ batch 9 giờ. Script daemon tự động kiểm tra định kỳ mỗi 1 tiếng.
2. **`huuhieu3333`**:
   - Kernel chuẩn bị mô hình `huuhieu3333/qwen3coder30b-prepare-notebook` đã kết thúc thành công (`COMPLETE`).
   - Đã lưu sẵn 18.5 GB checkpoint GGUF Qwen3-Coder-30B trong cache cục bộ, bảo lưu nguyên vẹn **30 giờ GPU T4 x2 miễn phí**, sẵn sàng khởi chạy ngay bất kỳ arm nào tiếp theo.
3. **`lznt123`**:
   - Đã cấu hình xác thực thành công qua API token mới (`KGAT_107f...`).
   - Notebook prepare model `lznt123/qwen3coder30b-prepare-notebook` đang chạy trên CPU để nạp sẵn model cache vào tài khoản. Bảo toàn nguyên vẹn **30 giờ GPU**.
4. **`tomandjerry223`**:
   - Đã hoàn tất xuất sắc toàn bộ nhiệm vụ chạy B1-shuf đa hạt giống (Seed 42, 43 và một phần 44) và arm B2-rep validation.
   - Hạn mức GPU tuần này còn ~40 phút, đóng vai trò dự phòng sau khi reset chu kỳ.

---

## 5. Kế hoạch Hành động Tiếp theo
1. Theo dõi kernel B3 trên `thanhduy9a4tv` qua script tự động, tải về trích xuất số liệu và nghiệm thu khi kết thúc.
2. Chọn arm tiếp theo cho tài khoản `huuhieu3333` (ưu tiên: chạy Test cho `B2-rep` hoặc chạy tiếp Test `B2-flip` vốn đã có $\tau^*$ sẵn theo hợp đồng OSF).
3. Sau khi `lznt123` hoàn thành nạp cache, kích hoạt chạy validation cho arm `B1-H2` hoặc `B2-rand` còn thiếu.
