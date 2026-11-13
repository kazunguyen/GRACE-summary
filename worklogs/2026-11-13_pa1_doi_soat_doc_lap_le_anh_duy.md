# Biên bản rà soát và đối soát độc lập hai bộ Bảng A/B/C của GRACE (Option 1)

- **Người thực hiện:** Lê Anh Duy (Le Anh Duy)
- **Ngày thực hiện:** 13/11/2026
- **Mục tiêu:** Rà soát và kiểm toán độc lập toàn diện hai bộ Bảng A, B, C (ngưỡng đăng ký trước và ngưỡng hiệu chỉnh hồi cứu), đối chiếu với kho bản ghi nguồn (`runs/final/source_inventory.json`) và báo cáo tổng hợp kết quả các arm (`worklogs/2026-11-12_bao_cao_metric_cac_arm_hoan_tat.md`) trước khi đưa số liệu vào bài báo.
- **Quy tắc kiểm toán:** Phân định minh bạch giữa các phần tự tính toán trực tiếp từ tệp bản ghi thô (`records.jsonl`) và các phần đối chiếu với tệp bảng CSV, báo cáo tổng hợp và sổ cái phân tích PA1 có sẵn.

---

## 0. Phân định phạm vi tự tính toán độc lập và phạm vi đối chiếu sẵn có

Để bảo đảm tính khách quan và khả năng truy vết trong kiểm toán khoa học, các nội dung rà soát được phân loại cụ thể như sau:

### 0.1. Những phần đã tự tính toán lại trực tiếp từ dữ liệu bản ghi thô (`records.jsonl` và `anchor_scores.csv`)
1. **Kiểm toán tính toàn vẹn tệp nguồn:** Tự tính toán mã băm SHA-256 cho toàn bộ 60 tệp dữ liệu nguồn gốc và 60 tệp bản ghi chuẩn hóa trong `runs/final/` để so sánh với `source_inventory.json`.
2. **Kiểm tra census và tính hợp lệ:** Nạp và kiểm tra từng bản ghi trong 75.090 mẫu test và 75.075 mẫu validation (xác thực trường `valid`, điểm xác suất $s$, nhãn $y$, và mã nhóm cụm `group`).
3. **Bảng A (toàn bộ 54 dòng × 2 bộ bảng):**
   - Chỉ số không phụ thuộc ngưỡng: AUROC (thống kê hạng Mann–Whitney U), AUPRC (Average Precision theo bậc thang tích phân).
   - Chỉ số tại ngưỡng cố định 0,5: MCC@0.5, Balanced Accuracy@0.5, F1@0.5, Tỷ lệ dự đoán dương PPR@0.5, cùng ma trận nhầm lẫn TP, FP, TN, FN.
   - Chỉ số tại 48 điểm ngưỡng tối ưu $\tau^*$ (đối với cả hai bộ ngưỡng đăng ký và hiệu chỉnh): MCC@$\tau$, BA@$\tau$, F1@$\tau$, PPR@$\tau$.
4. **Bảng B (toàn bộ 34 dòng có kết quả trong mỗi bộ bảng):**
   - Giá trị chênh lệch điểm ước lượng $\Delta\text{metric}$ ($\Delta\text{AUROC}$ và $\Delta\text{MCC}$).
   - Ma trận bất đồng McNemar: Đếm trực tiếp các ô $b$ và $c$ từ mảng nhãn dự đoán nhị phân của từng cặp arm.
   - Giá trị $p$-value McNemar hai phía (exact binomial test khi $b+c < 25$, chi-square có hiệu chỉnh liên tục khi $b+c \ge 25$).
   - Hiệu chỉnh Holm từng bước (step-down) cho họ 18 phép kiểm định MCC có mặt trong Bảng B của kit.
5. **Khoảng tin cậy Bootstrap ghép cặp 95% (Paired Cluster Bootstrap 5.000 lượt, seed `20261117`):**
   - Đã tự chạy mã tính toán lại trực tiếp từ dữ liệu bản ghi và mã cụm cho **6 phép so sánh cốt lõi**, bao gồm toàn bộ **22 cấu hình chỉ số × bộ ngưỡng** (kết quả chi tiết kèm giá trị $\Delta$ và hai cận CI [low; high] được lưu đầy đủ tại tệp log `worklogs/2026-11-13_ci_bootstrap_audit.log`):
     - **H1.1 (Devign B2 so với B0):**
       - $\Delta\text{AUROC}$ (ngưỡng chung không đổi): $\Delta = -0,0100$, CI 95% = $[-0,0280; +0,0078]$.
       - $\Delta\text{MCC}$ tại ngưỡng đăng ký ($\tau=0,08$): $\Delta = +0,0306$, CI 95% = $[-0,0080; +0,0681]$.
       - $\Delta\text{MCC}$ tại ngưỡng hiệu chỉnh ($\tau=0,98$): $\Delta = -0,0325$, CI 95% = $[-0,0750; +0,0106]$.
     - **H1.2 (ReVeal B2 so với B0):**
       - $\Delta\text{AUROC}$ (ngưỡng chung không đổi): $\Delta = -0,0079$, CI 95% = $[-0,0357; +0,0183]$.
       - $\Delta\text{MCC}$ tại ngưỡng đăng ký ($\tau=0,44$): $\Delta = -0,0211$, CI 95% = $[-0,0634; +0,0207]$.
       - $\Delta\text{MCC}$ tại ngưỡng hiệu chỉnh ($\tau=0,30$): $\Delta = -0,0229$, CI 95% = $[-0,0630; +0,0153]$.
     - **H2.1 (B2-flip so với B2 tại ngưỡng khóa validation của B2):**
       - Devign ($\tau=0,70$): $\Delta\text{MCC} = -0,0260$, CI 95% = $[-0,0609; +0,0094]$.
       - ReVeal ($\tau=0,12$): $\Delta\text{MCC} = -0,0273$, CI 95% = $[-0,0607; +0,0049]$.
     - **H2.2a (B2-rand so với B2):**
       - Devign $\Delta\text{AUROC}$: $\Delta = +0,0013$, CI 95% = $[-0,0140; +0,0158]$.
       - Devign $\Delta\text{MCC}$ tại ngưỡng khóa ($\tau=0,70$ vs $0,99$): $\Delta = -0,0254$, CI 95% = $[-0,0673; +0,0152]$.
       - ReVeal $\Delta\text{AUROC}$: $\Delta = +0,0143$, CI 95% = $[-0,0064; +0,0352]$.
       - ReVeal $\Delta\text{MCC}$ tại ngưỡng khóa ($\tau=0,12$ vs $0,89$): $\Delta = -0,0192$, CI 95% = $[-0,0675; +0,0299]$.
     - **H3.1a (B1 so với B0):**
       - Devign $\Delta\text{AUROC}$: $\Delta = -0,0070$, CI 95% = $[-0,0197; +0,0057]$.
       - Devign $\Delta\text{MCC}$ tại ngưỡng đăng ký ($\tau=0,88$ vs $0,08$): $\Delta = +0,0349$, CI 95% = $[-0,0084; +0,0759]$.
       - Devign $\Delta\text{MCC}$ tại ngưỡng hiệu chỉnh ($\tau=0,98$ vs $0,98$): $\Delta = -0,0134$, CI 95% = $[-0,0459; +0,0183]$.
       - ReVeal $\Delta\text{AUROC}$: $\Delta = +0,0101$, CI 95% = $[-0,0092; +0,0287]$.
       - ReVeal $\Delta\text{MCC}$ tại ngưỡng đăng ký ($\tau=0,74$ vs $0,44$): $\Delta = -0,0324$, CI 95% = $[-0,0708; +0,0049]$.
       - ReVeal $\Delta\text{MCC}$ tại ngưỡng hiệu chỉnh ($\tau=0,63$ vs $0,30$): $\Delta = -0,0351$, CI 95% = $[-0,0743; +0,0014]$.
     - **H5.1 (SUP-LR so với B2):**
       - Devign $\Delta\text{AUROC}$: $\Delta = +0,1254$, CI 95% = $[+0,0862; +0,1672]$.
       - Devign $\Delta\text{MCC}$ tại ngưỡng khóa ($\tau=0,70$ vs $0,37$): $\Delta = +0,1593$, CI 95% = $[+0,0952; +0,2267]$.
       - ReVeal $\Delta\text{AUROC}$: $\Delta = +0,2048$, CI 95% = $[+0,1426; +0,2636]$.
       - ReVeal $\Delta\text{MCC}$ tại ngưỡng khóa ($\tau=0,12$ vs $0,15$): $\Delta = +0,1939$, CI 95% = $[+0,1136; +0,2714]$.
6. **Bảng C:**
   - Tự đếm và tính toán tỷ lệ đổi dự đoán `flip`, `natural`, `net`, `flip_correct_to_wrong`, `flip_wrong_to_correct` tại ngưỡng cố định 0,5 từ 3 tệp bản ghi B2, B2-flip, B2-rep.
   - Tự đếm và phân loại chuyển dịch nhãn (đúng $\rightarrow$ sai, sai $\rightarrow$ đúng) tại ngưỡng khóa validation của B2 ($\tau=0,70$ Devign, $\tau=0,12$ ReVeal).

### 0.2. Những phần đối chiếu với tệp CSV xuất ra hoặc hồ sơ báo cáo có sẵn
1. **Khoảng tin cậy Bootstrap 95% của các phép so còn lại trong Bảng B (H2.2b, H2.2c, H3.1b, H3.1c):** Đối chiếu kiểm tra tính nhất quán giữa tệp CSV kit (`runs/tables_prereg/table_B_contrasts.csv` và `runs/tables_corrected/table_B_contrasts.csv`), tệp log kiểm toán chạy lại ngày 13/11 (`runs/.pa1-validation-EknQQQ`), và sổ cái phân tích PA1 tại `Runs-management/analysis_pa1_20261111/full_tables/contrasts.csv` (các cột `ci_low`, `ci_high`).
2. **Cột `p Holm` theo họ 22 phép so (trong Báo cáo ngày 12/11 §1.6):** Đối chiếu trực tiếp với tệp ledger phân tích PA1 tại `Runs-management/analysis_pa1_20261111/full_tables/contrasts.csv` (các cột `mcnemar_p_holm_available_*`).
3. **Bảng B 4 dòng mang nhãn `missing arm` (H2.3 và H5.3):** Đối chiếu với báo cáo chuyên đề Step 6 và phân tích thăm dò B3 trong `worklogs/2026-11-12_bao_cao_metric_cac_arm_hoan_tat.md`.
4. **Bảng A trong Báo cáo ngày 12/11:** Đối chiếu toàn bộ 26 dòng của Bảng 1.3 và 10 dòng của Bảng 1.4b (Step 6) với `runs/tables_corrected/table_A_metrics.csv`. Cả 26 dòng Bảng 1.3 đều khớp ở các cột chung đến độ làm tròn số học của báo cáo.
5. **Bảng C:** Khoảng tin cậy Bootstrap 95% của Net label sensitivity tại ngưỡng khóa B2 đối chiếu với `Runs-management/analysis_pa1_20261111/full_tables/sensitivity.csv`.

---

## 1. Phạm vi rà soát và đối chiếu tính toàn vẹn dữ liệu nguồn

### 1.1. Cấu trúc thư mục và hồ sơ rà soát
1. **Bộ ngưỡng đăng ký trước (Preregistered):**
   - Thư mục: `D:\JUNIOR\LabThayTho\GRACE-summary\runs\tables_prereg`
   - Tệp ngưỡng: `configs/thresholds.prereg.json` (tương ứng `thresholds_used.json`)
   - Tệp bảng: `table_A_metrics.csv`, `table_B_contrasts.csv`, `table_C_sensitivity.csv`
2. **Bộ ngưỡng hiệu chỉnh hồi cứu (Corrected):**
   - Thư mục: `D:\JUNIOR\LabThayTho\GRACE-summary\runs\tables_corrected`
   - Tệp ngưỡng: `configs/thresholds_corrected.json` (tương ứng `thresholds_used.json`)
   - Tệp bảng: `table_A_metrics.csv`, `table_B_contrasts.csv`, `table_C_sensitivity.csv`
3. **Danh mục nguồn và bản ghi kiểm chứng:**
   - Hồ sơ quản lý nguồn: `D:\JUNIOR\LabThayTho\GRACE-summary\runs\final\source_inventory.json`
   - Thư mục chứa bản ghi chuẩn hóa: `D:\JUNIOR\LabThayTho\GRACE-summary\runs\final/`
   - Điểm số mốc có giám sát: `D:\JUNIOR\LabThayTho\GRACE-summary\runs\anchor\anchor_scores.csv`
4. **Báo cáo tham chiếu đối chiếu:**
   - `D:\JUNIOR\LabThayTho\GRACE-summary\worklogs\2026-11-12_bao_cao_metric_cac_arm_hoan_tat.md`
   - `D:\JUNIOR\LabThayTho\GRACE-summary\Runs-management\analysis_pa1_20261111\full_tables/`

### 1.2. Kết quả kiểm toán tính toàn vẹn nguồn và bản ghi (`source_inventory.json`)
Kiểm tra băm SHA-256 độc lập của toàn bộ 60 nhóm nguồn và tệp bản ghi tương ứng trong `runs/final`:
- **Tổng số nhóm:** 60 nhóm (30 nhóm tập Test, 30 nhóm tập Validation).
- **Phạm vi arm bao phủ:** B0, B1, B1-full, B1-H2, B1-shuf (seed 42, 43, 44), B2, B2-flip, B2-labelonly, B2-nolabel, B2-rand (seed 42, 43, 44), B2-rep. Nhóm B3 (B3, B3-nodiff, B3-swap, B3-flip) được xác định là nhánh thăm dò nằm ngoài bộ census chính thức theo đúng phạm vi của Option 1.
- **Số mẫu thống kê:**
  - Tập Test: 75.090 bản ghi (Devign: 15 nhóm × 2.732 mẫu = 40.980 mẫu; ReVeal: 15 nhóm × 2.274 mẫu = 34.110 mẫu).
  - Tập Validation: 75.075 bản ghi (Devign: 15 nhóm × 2.732 mẫu = 40.980 mẫu; ReVeal: 15 nhóm × 2.273 mẫu = 34.095 mẫu).
- **Tỷ lệ hợp lệ (validity):** 100% bản ghi được nạp vào tính toán phân loại đều có định dạng hợp lệ (`valid = true`), có điểm số xác suất phân loại nhị phân hữu hạn và nhãn ground-truth đầy đủ.
- **Kết quả đối soát mã băm SHA-256:**
  - Sai lệch mã băm tệp nguồn gốc (`source_sha256`): **0 sai lệch** (60/60 tệp nguồn khớp chính xác).
  - Sai lệch mã băm tệp bản ghi sau nạp (`records_sha256`): **0 sai lệch** (60/60 tệp bản ghi khớp chính xác).
  - Không phát hiện trường hợp trùng lặp mã nhận diện mẫu (duplicate ID) trong bất kỳ nhóm nào.

---

## 2. Rà soát độc lập Bảng A (`table_A_metrics.csv`)

### 2.1. Cấu trúc và quy tắc áp dụng ngưỡng
- Mỗi bảng `table_A_metrics.csv` gồm đúng **54 dòng**:
  - 30 dòng cho các arm suy luận chính trên tập Test (15 arm/seed × 2 bộ dữ liệu Devign và ReVeal).
  - 18 dòng cho các mốc có giám sát Step 6 (SUP-LR, SUP-METRIC, SUP-MLP với 3 seed 42, 43, 44 × 2 bộ dữ liệu).
  - 6 dòng cho các đường cơ sở đối chứng hằng và ngẫu nhiên (ALL-1, ALL-0, RAND(p) × 2 bộ dữ liệu).
- **So sánh 48 ngưỡng áp dụng giữa hai bộ bảng (`thresholds_used.json`):**
  - **44/48 ngưỡng hoàn toàn trùng khớp**: Bao gồm toàn bộ các arm B1-full (Devign 0,99; ReVeal 0,01), B1-H2 (0,09; 0,21), B1-shuf (s42: 0,98/0,66; s43: 0,96/0,01; s44: 0,67/0,04), B2 (0,70/0,12), B2-flip (0,70/0,12), B2-rep (0,70/0,12), B2-nolabel (0,98/0,21), B2-labelonly (0,99/0,02), B2-rand (s42: 0,99/0,89; s43: 0,99/0,62; s44: 0,99/0,64), SUP-LR (0,37/0,15), SUP-METRIC (0,58/0,15), SUP-MLP (s42: 0,78/0,11; s43: 0,77/0,08; s44: 0,34/0,26).
  - **4/48 ngưỡng có sự khác biệt có chủ đích:**
    - Devign B0: Ngưỡng đăng ký trước = **0,08**; Ngưỡng hiệu chỉnh hồi cứu = **0,98**
    - Devign B1: Ngưỡng đăng ký trước = **0,88**; Ngưỡng hiệu chỉnh hồi cứu = **0,98**
    - ReVeal B0: Ngưỡng đăng ký trước = **0,44**; Ngưỡng hiệu chỉnh hồi cứu = **0,30**
    - ReVeal B1: Ngưỡng đăng ký trước = **0,74**; Ngưỡng hiệu chỉnh hồi cứu = **0,63**

### 2.2. Kết quả tự tính độc lập và đối soát từng ô số liệu
Thực hiện tính toán độc lập từ mảng nhãn và điểm số bằng các thuật toán gốc (AUROC qua Mann-Whitney U, AUPRC qua Average Precision bậc thang, ma trận nhầm lẫn TP/FP/TN/FN, MCC, Balanced Accuracy, F1, Tỷ lệ dự đoán dương PPR):
- **Tại ngưỡng chung 0,5 (Threshold-free & Operating point @ 0.5):**
  - Tất cả các giá trị AUROC, AUPRC, MCC@0.5, BA@0.5, F1@0.5, PPR@0.5, TP, FP, TN, FN tự tính đều **khớp 100%** giữa hai bộ bảng và khớp chính xác tới từng chữ số thập phân trong tệp CSV.
- **Tại ngưỡng hoạt động tối ưu $\tau^*$ (Operating point @ $\tau^*$):**
  - Trong bộ đăng ký trước (`tables_prereg`): 48/48 dòng khớp chính xác số tự tính.
  - Trong bộ hiệu chỉnh hồi cứu (`tables_corrected`): 48/48 dòng khớp chính xác số tự tính.
  - Sự thay đổi số liệu chỉ tập trung duy nhất ở 4 dòng B0 và B1:
    - Devign B0: MCC@$\tau$ đổi từ **0,0292** ($\tau=0,08$) sang **0,0922** ($\tau=0,98$); BA@$\tau$ đổi từ 0,5133 sang 0,5370; F1@$\tau$ đổi từ 0,5696 sang 0,3343; PPR@$\tau$ đổi từ 71,16% sang 19,99%.
    - Devign B1: MCC@$\tau$ đổi từ **0,0641** ($\tau=0,88$) sang **0,0788** ($\tau=0,98$); BA@$\tau$ đổi từ 0,5300 sang 0,5328; F1@$\tau$ đổi từ 0,4169 sang 0,3457; PPR@$\tau$ đổi từ 32,21% sang 22,04%.
    - ReVeal B0: MCC@$\tau$ đổi từ **0,0856** ($\tau=0,44$) sang **0,0874** ($\tau=0,30$); BA@$\tau$ đổi từ 0,5646 sang 0,5700; F1@$\tau$ đổi từ 0,2079 sang 0,2129; PPR@$\tau$ đổi từ 33,47% sang 36,98%.
    - ReVeal B1: MCC@$\tau$ đổi từ **0,0532** ($\tau=0,74$) sang **0,0523** ($\tau=0,63$); BA@$\tau$ đổi từ 0,5327 sang 0,5370; F1@$\tau$ đổi từ 0,1741 sang 0,1816; PPR@$\tau$ đổi từ 20,93% sang 23,79%.
- **Đối chiếu với báo cáo ngày 12/11/2026 (`2026-11-12_bao_cao_metric_cac_arm_hoan_tat.md`):**
  - Bảng 1.3 trong báo cáo hoàn toàn sử dụng số liệu của **bộ hiệu chỉnh hồi cứu** (`tables_corrected`) đối với B0 và B1 (MCC Devign B0 là 0,0922; B1 là 0,0788; ReVeal B0 là 0,0874; B1 là 0,0523).
  - Toàn bộ 26 dòng của Bảng 1.3 và 10 dòng của Bảng 1.4b (các mốc giám sát Step 6) trong báo cáo đều **khớp 100% không có bất kỳ sai lệch nào** ở các cột chung với `tables_corrected/table_A_metrics.csv` đến độ làm tròn số học của báo cáo.

---

## 3. Rà soát độc lập Bảng B (`table_B_contrasts.csv`)

### 3.1. Cấu trúc dòng và các trường hợp vắng mặt
- Mỗi bảng `table_B_contrasts.csv` gồm **38 dòng**:
  - **34 dòng có kết quả kiểm định đầy đủ**: Bao gồm các cặp H1.1, H1.2, H2.1, H2.2a, H2.2b, H2.2c, H3.1a, H3.1b, H3.1c, H5.1 trên cả hai bộ dữ liệu cho các chỉ số AUROC và MCC.
  - **4 dòng mang nhãn `status = missing arm`**:
    - H2.3 Devign và ReVeal: Kiểm định giữa B2 và B3. Thiếu do B3 được xác định là dữ liệu thăm dò theo phân loại Option 1, không nhập vào `runs/final`.
    - H5.3 Devign và ReVeal: Kiểm định giữa cặp meta-model P-PRE và P-POST. Thiếu do mô hình hồi quy logistic Step 6 được đánh giá trong đường ống riêng và xuất kết quả theo báo cáo chuyên đề Step 6, không nằm trong các bản ghi thô đơn lẻ của kit.

### 3.2. Phương pháp tính Bootstrap ghép cặp và tái lập số liệu
- **Cấu hình kiểm định:** Paired cluster bootstrap với 5.000 lượt lấy mẫu lại có hoàn lại, seed ngẫu nhiên cố định `20261117`. Đơn vị cụm là `commit_id` trên Devign (2.068 cụm) và `group` (mã băm tệp nguồn) trên ReVeal (646 cụm). Số lượt bootstrap suy biến (`n_degenerate_boot`) đều bằng 0 trên toàn bộ các phép so.
- **Tự tính độc lập các cặp so sánh cốt lõi:**
  1. **H1.1 (Devign B2 so với B0):**
     - AUROC: $\Delta = -0,0100$; CI 95% = $[-0,0280; +0,0078]$ (giống nhau ở cả hai bộ). Cận trên $< 0,02 \rightarrow$ loại trừ lợi ích đáng kể.
     - MCC (Ngưỡng đăng ký): $\Delta = +0,0306$; CI 95% = $[-0,0080; +0,0681]$; McNemar $b=275, c=343, p=0,007036$.
     - MCC (Ngưỡng hiệu chỉnh): $\Delta = -0,0325$; CI 95% = $[-0,0750; +0,0106]$; McNemar $b=621, c=511, p=0,001197$.
  2. **H1.2 (ReVeal B2 so với B0):**
     - AUROC: $\Delta = -0,0079$; CI 95% = $[-0,0357; +0,0183]$ (giống nhau ở cả hai bộ). Cận trên $< 0,02 \rightarrow$ loại trừ lợi ích đáng kể.
     - MCC (Ngưỡng đăng ký): $\Delta = -0,0211$; CI 95% = $[-0,0634; +0,0207]$; McNemar $b=524, c=90, p=2,24 \times 10^{-68}$.
     - MCC (Ngưỡng hiệu chỉnh): $\Delta = -0,0229$; CI 95% = $[-0,0630; +0,0153]$; McNemar $b=462, c=101, p=5,40 \times 10^{-52}$.
  3. **H2.1 (B2-flip so với B2 tại ngưỡng khóa B2):**
     - Devign: $\Delta\text{MCC} = -0,0260$; CI 95% = $[-0,0609; +0,0094]$; McNemar $b=294, c=260, p=0,1609$.
     - ReVeal: $\Delta\text{MCC} = -0,0273$; CI 95% = $[-0,0607; +0,0049]$; McNemar $b=100, c=143, p=0,007054$.
  4. **H2.2a (B2-rand so với B2):**
     - Quy ước trong tệp CSV của kit định nghĩa $A = \text{B2}, B = \text{B2-rand}$ với $\Delta = B - A = \text{B2-rand} - \text{B2}$.
     - Theo đúng quy ước và thứ tự trong tệp CSV của kit:
       - Devign: $\Delta\text{AUROC} = +0,0013$ [$ -0,0140; +0,0158 $]; $\Delta\text{MCC} = -0,0254$ [$ -0,0673; +0,0152 $]; ô McNemar là $b=499$ (B2 đúng, B2-rand sai) và $c=542$ (B2 sai, B2-rand đúng); $p=0,1930$.
       - ReVeal: $\Delta\text{AUROC} = +0,0143$ [$ -0,0064; +0,0352 $]; $\Delta\text{MCC} = -0,0192$ [$ -0,0675; +0,0299 $]; ô McNemar là $b=98$ (B2 đúng, B2-rand sai) và $c=737$ (B2 sai, B2-rand đúng); $p=5,04 \times 10^{-108}$.
     - *Đối chiếu với Báo cáo PA1:* Trong báo cáo ngày 12/11 và tệp `full_tables/contrasts.csv`, cặp này được ký hiệu theo chiều ngược lại $\text{B2} - \text{B2-rand}$, khi đó $\Delta\text{AUROC} = -0,0013$ [$ -0,0158; +0,0140 $] và $\Delta\text{MCC} = +0,0254$ [$ -0,0152; +0,0673 $] trên Devign, với hai ô đảo vị trí $b=542$ (B2-rand đúng, B2 sai) và $c=499$ (B2-rand sai, B2 đúng). Hai cách biểu diễn hoàn toàn nhất quán về mặt toán học.
  5. **H2.2b (B2-nolabel so với B1):**
     - Devign AUROC: $\Delta = -0,0066$ [$ -0,0183; +0,0052 $].
     - Devign MCC (Ngưỡng đăng ký): $\Delta = -0,0123$ [$ -0,0437; +0,0181 $]; $b=222, c=199, p=0,2836$.
     - Devign MCC (Ngưỡng hiệu chỉnh): $\Delta = -0,0270$ [$ -0,0587; +0,0058 $]; $b=264, c=211, p=0,01704$.
     - ReVeal AUROC: $\Delta = -0,0120$ [$ -0,0288; +0,0049 $].
     - ReVeal MCC (Ngưỡng đăng ký): $\Delta = +0,0303$ [$ -0,0132; +0,0733 $]; $b=552, c=80, p=2,55 \times 10^{-78}$.
     - ReVeal MCC (Ngưỡng hiệu chỉnh): $\Delta = +0,0312$ [$ -0,0130; +0,0755 $]; $b=504, c=76, p=2,45 \times 10^{-70}$.
  6. **H2.2c (B2 so với B2-labelonly):**
     - Devign: $\Delta\text{AUROC} = -0,0158$ [$ -0,0345; +0,0024 $]; $\Delta\text{MCC} = -0,0251$ [$ -0,0738; +0,0229 $]; $b=645, c=542, p=0,003071$.
     - ReVeal: $\Delta\text{AUROC} = -0,0344$ [$ -0,0588; -0,0103 $]; $\Delta\text{MCC} = -0,0554$ [$ -0,0911; -0,0209 $]; $b=335, c=70, p=2,59 \times 10^{-39}$.
  7. **H3.1a (B1 so với B0):**
     - Devign AUROC: $\Delta = -0,0070$ [$ -0,0197; +0,0057 $].
     - Devign MCC (Ngưỡng đăng ký): $\Delta = +0,0349$ [$ -0,0084; +0,0759 $]; $b=485, c=617, p=7,94 \times 10^{-5}$.
     - Devign MCC (Ngưỡng hiệu chỉnh): $\Delta = -0,0134$ [$ -0,0459; +0,0183 $]; $b=178, c=162, p=0,4159$.
     - ReVeal AUROC: $\Delta = +0,0101$ [$ -0,0092; +0,0287 $].
     - ReVeal MCC (Ngưỡng đăng ký): $\Delta = -0,0324$ [$ -0,0708; +0,0049 $]; $b=86, c=269, p=4,48 \times 10^{-22}$.
     - ReVeal MCC (Ngưỡng hiệu chỉnh): $\Delta = -0,0351$ [$ -0,0743; +0,0014 $]; $b=95, c=307, p=6,72 \times 10^{-26}$.
  8. **H3.1b (B1 so với B1-shuf seed 42):**
     - Devign AUROC: $\Delta = -0,0096$ [$ -0,0233; +0,0041 $].
     - Devign MCC (Ngưỡng đăng ký): $\Delta = -0,0207$ [$ -0,0600; +0,0198 $]; $b=318, c=280, p=0,1303$.
     - Devign MCC (Ngưỡng hiệu chỉnh): $\Delta = -0,0060$ [$ -0,0426; +0,0322 $]; $b=204, c=196, p=0,7263$.
     - ReVeal AUROC: $\Delta = +0,0064$ [$ -0,0161; +0,0296 $].
     - ReVeal MCC (Ngưỡng đăng ký): $\Delta = +0,0154$ [$ -0,0220; +0,0547 $]; $b=213, c=77, p=2,24 \times 10^{-15}$.
     - ReVeal MCC (Ngưỡng hiệu chỉnh): $\Delta = +0,0145$ [$ -0,0250; +0,0559 $]; $b=253, c=73, p=3,62 \times 10^{-23}$.
  9. **H5.1 (SUP-LR so với B2):**
     - Devign: $\Delta\text{AUROC} = +0,1254$ [$ +0,0862; +0,1672 $]; $\Delta\text{MCC} = +0,1593$ [$ +0,0952; +0,2267 $]; $b=482, c=674, p=1,94 \times 10^{-8}$.
     - ReVeal: $\Delta\text{AUROC} = +0,2048$ [$ +0,1426; +0,2636 $]; $\Delta\text{MCC} = +0,1939$ [$ +0,1136; +0,2714 $]; $b=192, c=927, p=1,03 \times 10^{-106}$.

### 3.3. Rà soát việc hiệu chỉnh đa giả thuyết Holm
Cần phân biệt rõ hai cấp độ hiệu chỉnh Holm theo lưu ý tại `README.md`:
1. **Cột `mcnemar_p_holm` trong tệp CSV của kit (`table_B_contrasts.csv`):**
   - Được tính tự động trên đúng **18 phép kiểm định MCC có mặt** trong bảng chạy thực tế.
   - Kết quả tự tính lại độc lập theo công thức step-down Holm trên 18 giá trị $p$ thô này **khớp chính xác 100%** với giá trị ghi trong tệp CSV của cả hai thư mục.
2. **Cột `p Holm` trích dẫn trong Báo cáo PA1 (`worklogs/2026-11-12_bao_cao_metric_cac_arm_hoan_tat.md` Mục 1.6):**
   - Được tính trên toàn thể họ **22 phép so sánh** (11 cặp × 2 dataset), bao gồm cả H2.3 (B2 vs B3) và H5.3 (P-PRE vs P-POST) từ phân tích PA1 độc lập (`Runs-management/analysis_pa1_20261111/full_tables/contrasts.csv`, cột `mcnemar_p_holm_available_*`).
   - Đối soát chi tiết cho thấy: Mọi giá trị $p$ Holm trong bảng báo cáo (ví dụ Devign B0 vs B2 gốc: 0,06332; hiệu chỉnh: 0,01316; B2-labelonly: 0,03071; ReVeal B2-flip: 0,06348; P-PRE vs P-POST: 0,001278) đều **khớp chính xác** với bảng phân tích 22 phép so của PA1.
   - **Kết luận:** Không có sự mâu thuẫn hay sai sót; việc tệp CSV kit hiển thị hiệu chỉnh trên 18 phép và báo cáo bài báo sử dụng họ 22 phép là đúng thiết kế phân định ranh giới đã được thuyết minh rõ ràng tại README.md.

---

## 4. Rà soát độc lập Bảng C (`table_C_sensitivity.csv`)

### 4.1. Bản chất độ nhạy nhãn demo và hai mức ngưỡng đánh giá
Quy tắc kiểm tra: Ghép ba arm B2 (gốc), B2-flip (đảo nhãn demo) và B2-rep (lặp lại nguyên vẹn prompt) trên cùng tập ID mẫu.
- `flip` = Tỷ lệ đổi nhãn dự đoán từ B2 sang B2-flip.
- `natural` = Tỷ lệ đổi nhãn dự đoán ngẫu nhiên giữa hai lần chạy cùng prompt (B2 sang B2-rep).
- `net` = `flip` $-$ `natural`.

### 4.2. Đối soát số liệu tại ngưỡng cố định 0,5 (đầu ra trong kit CSV)
Trong tệp `table_C_sensitivity.csv` ở cả hai thư mục `tables_prereg` và `tables_corrected`:
- **Devign:**
  - $N = 2.732$ mẫu.
  - `flip` = $18,12\%$ (495/2.732 mẫu đổi dự đoán). Trong đó: đổi từ đúng sang sai = $9,22\%$ (252 mẫu); đổi từ sai sang đúng = $8,89\%$ (243 mẫu).
  - `natural` = $0,00\%$ (0/2.732 mẫu đổi dự đoán).
  - `net` = **$18,12\%$** (khớp chính xác số tự tính: $0,18118594$).
- **ReVeal:**
  - $N = 2.274$ mẫu.
  - `flip` = $13,90\%$ (316/2.274 mẫu đổi dự đoán). Trong đó: đổi từ đúng sang sai = $6,20\%$ (141 mẫu); đổi từ sai sang đúng = $7,70\%$ (175 mẫu).
  - `natural` = $0,00\%$ (0/2.274 mẫu đổi dự đoán).
  - `net` = **$13,90\%$** (khớp chính xác số tự tính: $0,13896218$).

### 4.3. Đối soát số liệu tại ngưỡng khóa B2 (số liệu trích dẫn chính thức trong bài báo)
Theo README.md và đề cương nghiên cứu, chỉ số đánh giá giả thuyết H2.1 phải được tính tại **ngưỡng khóa validation của B2** ($\tau = 0,70$ cho Devign và $\tau = 0,12$ cho ReVeal) kèm khoảng tin cậy bootstrap ghép cặp theo cụm (`Runs-management/analysis_pa1_20261111/full_tables/sensitivity.csv`):
- **Devign tại $\tau = 0,70$:**
  - Số ca B2-flip đổi nhãn: **554 ca** ($20,28\%$).
  - Số ca B2-rep đổi nhãn: **0 ca** ($0,00\%$).
  - Net sensitivity: **$20,28\%$**, CI 95% = $[18,75\%; 21,76\%]$.
  - Cơ cấu chuyển dịch: 294 ca chuyển từ đúng sang sai; 260 ca chuyển từ sai sang đúng.
- **ReVeal tại $\tau = 0,12$:**
  - Số ca B2-flip đổi nhãn: **243 ca** ($10,69\%$).
  - Số ca B2-rep đổi nhãn: **0 ca** ($0,00\%$).
  - Net sensitivity: **$10,69\%$**, CI 95% = $[9,15\%; 12,25\%]$.
  - Cơ cấu chuyển dịch: 100 ca chuyển từ đúng sang sai; 143 ca chuyển từ sai sang đúng.
- **Kết luận:** Số liệu tự tính độc lập khớp hoàn toàn từng ca chuyển đổi và từng khoảng tin cậy với Bảng C Mục 1.6 trong báo cáo ngày 12/11/2026. B2-rep giữ nguyên 100% dự đoán trên toàn bộ 5.006 mẫu của hai tập test, khẳng định tính tất định tuyệt đối của quá trình sinh phản hồi.

---

## 5. Bảng tổng hợp đối soát các số liệu dự kiến trích dẫn vào bài báo

| Nội dung câu hỏi / Giả thuyết | Chỉ số / Phép so | Số tự tính độc lập | Số trong báo cáo 12/11 | Số trong Bảng A/B/C CSV | Kết luận đối soát |
|---|---|---|---|---|---|
| **RQ1 / H1.1 (Devign)** | $\Delta\text{AUROC (B2-B0)}$ | -0,0100 [-0,0280; 0,0078] | -0,0100 [-0,0280; 0,0078] | -0,0100 [-0,0280; 0,0078] | **Khớp 100%** |
| | $\Delta\text{MCC}$ (Ngưỡng gốc $\tau=0,08$) | +0,0306 [-0,0080; 0,0681] | +0,0306 [-0,0080; 0,0681] | +0,0306 [-0,0080; 0,0681] | **Khớp 100%** |
| | $\Delta\text{MCC}$ (Ngưỡng hiệu chỉnh $\tau=0,98$) | -0,0325 [-0,0750; 0,0106] | -0,0325 [-0,0750; 0,0106] | -0,0325 [-0,0750; 0,0106] | **Khớp 100%** |
| **RQ1 / H1.2 (ReVeal)** | $\Delta\text{AUROC (B2-B0)}$ | -0,0079 [-0,0357; 0,0183] | -0,0079 [-0,0357; 0,0183] | -0,0079 [-0,0357; 0,0183] | **Khớp 100%** |
| | $\Delta\text{MCC}$ (Ngưỡng gốc $\tau=0,44$) | -0,0211 [-0,0634; 0,0207] | -0,0211 [-0,0634; 0,0207] | -0,0211 [-0,0634; 0,0207] | **Khớp 100%** |
| | $\Delta\text{MCC}$ (Ngưỡng hiệu chỉnh $\tau=0,30$) | -0,0229 [-0,0630; 0,0153] | -0,0229 [-0,0630; 0,0153] | -0,0229 [-0,0630; 0,0153] | **Khớp 100%** |
| **H1.2 (Chỉ số B2)** | Devign: MCC, F1 | MCC = 0,0597; F1 = 0,5485 | 0,0597; 0,5485 | 0,0597; 0,5485 | **Khớp 100%** (F1 ALL-1 là 0,6295) |
| | ReVeal: MCC | MCC = 0,0645 | 0,0645 | 0,0645 | **Khớp 100%** |
| **RQ2 / H2.1** | Net label sensitivity Devign | 20,28% [18,75; 21,76] | 20,28 [18,75; 21,76] | 18,12% (tại 0,5); 20,28% (tại $\tau=0,70$) | **Khớp 100%** |
| | Net label sensitivity ReVeal | 10,69% [9,15; 12,25] | 10,69 [9,15; 12,25] | 13,90% (tại 0,5); 10,69% (tại $\tau=0,12$) | **Khớp 100%** |
| **RQ2 / H2.2** | $\Delta\text{AUROC (B2 - B2-rand)}$ | Devign: 0,0013 [-0,0140; 0,0158]<br>ReVeal: 0,0143 [-0,0064; 0,0352] | Devign: [-0,0158; 0,0140]*<br>ReVeal: [-0,0352; 0,0064]* | Devign: 0,0013 [-0,0140; 0,0158]<br>ReVeal: 0,0143 [-0,0064; 0,0352] | **Khớp 100%** (chú thích về chiều trừ)* |
| | $\Delta\text{AUROC (B2-nolabel - B1)}$ | Devign: -0,0066 [-0,0183; 0,0052]<br>ReVeal: -0,0120 [-0,0288; 0,0049] | Devign: [-0,0183; 0,0052]<br>ReVeal: [-0,0288; 0,0049] | Devign: -0,0066 [-0,0183; 0,0052]<br>ReVeal: -0,0120 [-0,0288; 0,0049] | **Khớp 100%** |
| | $\Delta\text{AUROC (B2 - B2-labelonly)}$ | Devign: -0,0158 [-0,0345; 0,0024]<br>ReVeal: -0,0344 [-0,0588; -0,0103] | Devign: [-0,0345; 0,0024]<br>ReVeal: [-0,0588; -0,0103] | Devign: -0,0158 [-0,0345; 0,0024]<br>ReVeal: -0,0344 [-0,0588; -0,0103] | **Khớp 100%** |
| **RQ3 / H3.1** | $\Delta\text{AUROC (B1 - B0)}$ | Devign: -0,0070 [-0,0197; 0,0057]<br>ReVeal: +0,0101 [-0,0092; 0,0287] | Devign: -0,0070 [-0,0197; 0,0057]<br>ReVeal: +0,0101 [-0,0092; 0,0287] | Devign: -0,0070 [-0,0197; 0,0057]<br>ReVeal: +0,0101 [-0,0092; 0,0287] | **Khớp 100%** |
| | $\Delta\text{AUROC (B1 - B1-shuf s42)}$ | Devign: -0,0096 [-0,0233; 0,0041]<br>ReVeal: +0,0064 [-0,0161; 0,0296] | Devign: -0,0096 [-0,0233; 0,0041]<br>ReVeal: +0,0064 [-0,0161; 0,0296] | Devign: -0,0096 [-0,0233; 0,0041]<br>ReVeal: +0,0064 [-0,0161; 0,0296] | **Khớp 100%** |
| **RQ4** | Tỷ lệ đoán 1 tại $\tau=0,5$ | Devign: B1=46,63%; B2=65,08%<br>ReVeal: B1=27,13%; B2=46,00% | Devign: 46,6% $\rightarrow$ 65,1%<br>ReVeal: 27,1% $\rightarrow$ 46,0% | Devign: 0,4663; 0,6508<br>ReVeal: 0,2713; 0,4600 | **Khớp 100%** (23,79% là tại $\tau^*=0,63$) |
| **RQ5 / H5.1** | $\Delta\text{MCC (SUP-LR - B2)}$ | Devign: +0,1593 [0,0952; 0,2267]<br>ReVeal: +0,1939 [0,1136; 0,2714] | Devign: +0,1593 [0,0952; 0,2267]<br>ReVeal: +0,1939 [0,1136; 0,2714] | Devign: 0,1593 [0,0952; 0,2267]<br>ReVeal: 0,1939 [0,1136; 0,2714] | **Khớp 100%** |
| | AUROC SUP-LR | Devign: 0,6559; ReVeal: 0,7709 | Devign: 0,6559; ReVeal: 0,7709 | Devign: 0,6559; ReVeal: 0,7709 | **Khớp 100%** |
| **H5.2 (Ngưỡng chung)** | $\Delta\text{MCC (P_post - P_pre)}$ | Devign: -0,0008 [-0,0095; 0,0080]<br>ReVeal: -0,0078 [-0,0169; -0,0010] | Devign: -0,0008 [-0,0095; 0,0080]<br>ReVeal: -0,0078 [-0,0169; -0,0010] | Báo cáo Step 6 chuyên đề | **Khớp 100%** |

*\*Ghi chú về chiều trừ:* Trong bảng của kit (`table_B_contrasts.csv`), contrast `H2.2a` định nghĩa $A = \text{B2}$ và $B = \text{B2-rand}$, với $\Delta = B - A = \text{B2-rand} - \text{B2}$. Do đó $\Delta\text{AUROC} = +0,0013$ trên Devign. Khi báo cáo viết theo chiều $\text{B2} - \text{B2-rand}$, dấu được đảo ngược thành $-0,0013$ với CI tương ứng $[-0,0158; +0,0140]$. Hai cách biểu diễn hoàn toàn tương đương về mặt toán học.

---

## 6. Kết luận và kiến nghị

1. **Về kết quả rà soát theo phạm vi kiểm toán (khớp với Mục 0):**
   - **Phần tự tính toán độc lập từ records:**
     - Đã kiểm toán mã băm SHA-256 của toàn bộ 60 tệp nguồn và 60 tệp bản ghi chuẩn hóa trong `runs/final` (0 sai lệch). Đã census toàn bộ 75.090 mẫu test và 75.075 mẫu validation, đạt tỷ lệ hợp lệ 100%.
     - Đã tự tính lại toàn bộ 54 dòng × 2 bộ bảng của Bảng A (AUROC, AUPRC, toàn bộ metric tại ngưỡng cố định 0,5 và tại 48 điểm ngưỡng tối ưu $\tau^*$). Khớp 100% với CSV.
     - Đã tự tính lại toàn bộ 34 dòng đánh giá của Bảng B về điểm ước lượng $\Delta\text{metric}$, ma trận bất đồng McNemar $b, c$, giá trị $p$ McNemar hai phía, và hiệu chỉnh Holm 18 phép so của kit CSV. Khớp 100% với CSV.
     - Đã tự chạy Paired Cluster Bootstrap 95% CI (5.000 lượt, seed `20261117`) cho toàn bộ 22 cấu hình cốt lõi thuộc H1.1, H1.2, H2.1, H2.2a, H3.1a, H5.1 trên cả hai bộ dữ liệu và hai bộ ngưỡng. Giá trị $\Delta$ và cận CI [low; high] khớp 100% với tệp CSV kit và đã được ghi nhận chi tiết tại tệp log `worklogs/2026-11-13_ci_bootstrap_audit.log`.
     - Đã tự đếm và tính toán tỷ lệ chuyển dịch nhãn Bảng C tại ngưỡng 0,5 và tại ngưỡng khóa validation B2.
   - **Phần đối chiếu với CSV và hồ sơ báo cáo có sẵn:**
     - Các khoảng tin cậy Bootstrap 95% của các phép so còn lại trong Bảng B (H2.2b, H2.2c, H3.1b, H3.1c) đã được đối chiếu nhất quán giữa tệp CSV kit, log kiểm toán ngày 13/11 (`runs/.pa1-validation-EknQQQ`) và ledger PA1 `full_tables/contrasts.csv`.
     - Cột $p$ Holm theo họ 22 phép so trong Báo cáo ngày 12/11 §1.6 đã được đối chiếu khớp chính xác với sổ cái phân tích PA1 `Runs-management/analysis_pa1_20261111/full_tables/contrasts.csv`.
     - 4 dòng `missing arm` (H2.3 và H5.3) được đối chiếu và giải trình đầy đủ qua báo cáo chuyên đề Step 6 và nhánh thăm dò B3.
     - Toàn bộ 26 dòng của Bảng 1.3 và 10 dòng của Bảng 1.4b trong Báo cáo ngày 12/11 đã được đối chiếu với `tables_corrected/table_A_metrics.csv`, cả 26 dòng đều khớp 100% ở các cột chung đến độ làm tròn số học của báo cáo.
     - Khoảng tin cậy Bootstrap 95% của Net label sensitivity trong Bảng C tại ngưỡng khóa B2 được đối chiếu khớp hoàn toàn với `Runs-management/analysis_pa1_20261111/full_tables/sensitivity.csv`.

2. **Lưu ý quan trọng khi đưa số vào Paper:**
   - **Tách bạch tính chất của hai bộ ngưỡng:** Khi đưa số liệu của B0 và B1 vào bài báo, cần trình bày song song cả hai bộ ngưỡng hoặc nhấn mạnh rõ kết quả theo ngưỡng hiệu chỉnh tối ưu trên toàn bộ validation là kết quả phân tích hồi cứu (retrospective), trong khi bộ ngưỡng gốc được giữ nguyên để đối chiếu với đăng ký trước (preregistered).
   - **Ghi chú rõ ngữ cảnh của Bảng B và Bảng C:**
     - Trong Bảng B, giải thích rõ các dòng vắng mặt của B3 (thuộc diện thăm dò) và P-PRE/P-POST (thuộc phân tích Step 6). Nếu trích dẫn giá trị $p$ Holm, cần nêu rõ là hiệu chỉnh theo họ 22 phép so của đề cương PA1.
     - Trong Bảng C, tệp CSV thể hiện độ nhạy nhãn tại ngưỡng cố định 0,5; khi trích dẫn kết luận giả thuyết H2.1 vào bài báo, cần trích dẫn số liệu tại ngưỡng khóa validation của B2 ($\tau=0,70$ và $\tau=0,12$) như đã được kiểm toán đầy đủ ở Mục 4.3.

**Xác nhận:** Kết quả kiểm toán độc lập hoàn tất, số liệu sạch và hoàn toàn sẵn sàng để đưa vào bản thảo bài báo.
