# Báo cáo kết quả các arm GRACE đã hoàn tất — cập nhật 12/11/2026

**Bản gửi thầy:** 08/11/2026<br>
**Bản cập nhật 11/11:** Bổ sung kết quả Step 6 và phân tích ghép cặp cho Phương án 1.<br>
**Bản cập nhật 12/11:** Sửa diễn giải RQ4 tại ngưỡng chung 0,5, trình bày B3 và B1-H2 ở mức thăm dò, và bổ sung các kết quả kiểm tra offline của Hiếu. Xem [worklog chỉnh sửa](2026-11-12_chinh_sua_bao_cao_metric_grace.md).<br>
**Phạm vi:** Báo cáo metric test cho 15 arm chẩn đoán (B0, B1, B1-full, B1-H2, B1-shuf, B2, B2-rand, B2-nolabel, B2-labelonly, B2-flip, B2-rep, B3, B3-nodiff, B3-swap, B3-flip) và Step 6 (SUP-LR/SUP-MLP/SUP-METRIC, P_pre/P_post, sửa–hỏng, routing). Các kết quả B3/B3-swap/B3-flip mới bổ sung dùng seed 42, đủ 5.006 test record và ngưỡng B3 kế thừa từ validation: Devign 0,99; ReVeal 0,01. B0/B1 chính dùng ngưỡng hiệu chỉnh hồi cứu; báo cáo giữ riêng điều này và không gọi các phép hiệu chỉnh đó là preregistered.

**Bổ sung sau bản gửi ngày 08/11.** Bản hiện tại có kết quả SUP-LR/SUP-MLP/SUP-METRIC trên Devign và ReVeal ở mục 1.4, cùng kết quả P_pre/P_post và routing từ lượt Step 6 hoàn tất ngày 11/11 ở mục 1.5.

## 0. Đối chứng expert hằng và ngẫu nhiên trên test

Theo mục 7/B.5 của đề cương, ALL-0, ALL-1 và RANDOM là **expert tham chiếu trong phân tích sửa–hỏng/oracle**, không phải các arm GRACE độc lập. Với mỗi expert `g`, so với dự đoán của bộ phân loại nền `h`: *repair* = `h` sai, `g` đúng; *harm* = `h` đúng, `g` sai. H3-B gate là nền chính; SUP-LR là phân tích bổ sung. Các số ALL-0/ALL-1 bên dưới tính trên toàn bộ test đã khóa của từng dataset. RANDOM dùng 20 vector Bernoulli, với tỷ lệ dự đoán 1 bằng tỷ lệ B2 score `s ≥ 0,5` (`p=0,649707` Devign; `p=0,459982` ReVeal); báo trung bình và phân vị 2,5–97,5% giữa 20 lượt theo đúng quy tắc trong đề cương.

| Dataset | Nền `h` | Expert `g` | p(1) của g | Repair (ALL-0/1: tổng [y=0/y=1]; RANDOM: TB [P2,5; P97,5]) | Harm (ALL-0/1: tổng [y=0/y=1]; RANDOM: TB [P2,5; P97,5]) | Cả hai đúng | Cả hai sai |
|---|---|---|---:|---:|---:|---:|---:|
| Devign | H3-B gate | ALL-0 | 0 | 764 (764 / 0) | 998 (0 / 998) | 713 | 257 |
| Devign | H3-B gate | ALL-1 | 1 | 257 (0 / 257) | 713 (713 / 0) | 998 | 764 |
| Devign | H3-B gate | RANDOM, n=20, seed=42 | 0,649707 | 433,85 [411,28; 465,05] | 812,55 [775,85; 841,05] | 898,45 | 587,15 |
| Devign | SUP-LR | ALL-0 | 0 | 826 (826 / 0) | 964 (0 / 964) | 651 | 291 |
| Devign | SUP-LR | ALL-1 | 1 | 291 (0 / 291) | 651 (651 / 0) | 964 | 826 |
| Devign | SUP-LR | RANDOM, n=20, seed=42 | 0,649707 | 480,80 [461,90; 498,00] | 763,50 [723,35; 791,15] | 851,50 | 636,20 |
| ReVeal | H3-B gate | ALL-0 | 0 | 201 (201 / 0) | 116 (0 / 116) | 1.843 | 114 |
| ReVeal | H3-B gate | ALL-1 | 1 | 114 (0 / 114) | 1.843 (1.843 / 0) | 116 | 201 |
| ReVeal | H3-B gate | RANDOM, n=20, seed=42 | 0,459982 | 161,35 [150,85; 176,15] | 904,25 [862,93; 952,20] | 1.054,75 | 153,65 |
| ReVeal | SUP-LR | ALL-0 | 0 | 360 (360 / 0) | 121 (0 / 121) | 1.684 | 109 |
| ReVeal | SUP-LR | ALL-1 | 1 | 109 (0 / 109) | 1.684 (1.684 / 0) | 121 | 360 |
| ReVeal | SUP-LR | RANDOM, n=20, seed=42 | 0,459982 | 245,05 [230,90; 263,58] | 833,95 [800,50; 872,05] | 971,05 | 223,95 |

Với ALL-0/ALL-1, cột repair/harm ghi tổng và phần tách theo lớp y=0/y=1; summary RANDOM lưu tổng thể giữa 20 lượt, chưa lưu phân rã theo lớp. ALL-0 sửa chủ yếu lỗi dương tính giả của nền nhưng làm hỏng nhiều ca dương tính thật; ALL-1 có chiều ngược lại. Vì ReVeal mất cân bằng mạnh, ALL-0 có số ca cả hai đúng lớn, nhưng không thể diễn giải đó là năng lực phát hiện lớp 1. RANDOM cho thấy số ca sửa tự nhiên có thể lớn chỉ nhờ tỷ lệ dự đoán 1; do đó số repair của B2/LLM phải được đọc cạnh đối chứng này, không đứng riêng. Khoảng trong ngoặc vuông của RANDOM là phân vị thực nghiệm giữa 20 lượt, **không phải CI của chênh lệch**.

## 1. Ngưỡng và metric của các arm đã hoàn tất

### 1.1. Ngưỡng áp dụng

Các hàng B0 và B1 dưới đây dùng bộ ngưỡng hiệu chỉnh theo quy tắc chọn ngưỡng trên toàn bộ validation. Lý do hiệu chỉnh và vai trò của bộ ngưỡng gốc được giải thích ở mục 1.6.

| Arm | Dataset | Ngưỡng τ | Cơ sở chọn ngưỡng |
|---|---|---:|---|
| B0 | Devign | 0,98 | Tối ưu MCC trên full validation; hiệu chỉnh hồi cứu |
| B0 | ReVeal | 0,30 | Tối ưu MCC trên full validation; hiệu chỉnh hồi cứu |
| B1 | Devign | 0,98 | Tối ưu MCC trên full validation; hiệu chỉnh hồi cứu |
| B1 | ReVeal | 0,63 | Tối ưu MCC trên full validation; hiệu chỉnh hồi cứu |
| B1-full | Devign | 0,99 | Khóa validation đã đóng băng và nạp trong input test Kaggle |
| B1-full | ReVeal | 0,01 | Khóa validation đã đóng băng và nạp trong input test Kaggle |
| B1-shuf s42 | Devign | 0,98 | Ngưỡng đã chọn trên validation của seed 42 |
| B1-shuf s42 | ReVeal | 0,66 | Ngưỡng đã chọn trên validation của seed 42 |
| B1-shuf s43 | Devign | 0,96 | Ngưỡng đã chọn trên validation của seed 43 |
| B1-shuf s43 | ReVeal | 0,01 | Ngưỡng đã chọn trên validation của seed 43 |
| B1-shuf s44 | Devign | 0,67 | Ngưỡng đã chọn trên validation của seed 44 |
| B1-shuf s44 | ReVeal | 0,04 | Ngưỡng đã chọn trên validation của seed 44 |
| B2 | Devign | 0,70 | Ngưỡng B2 trong khóa hiện có |
| B2 | ReVeal | 0,12 | Ngưỡng B2 trong khóa hiện có |
| B2-rand s42 | Devign | 0,99 | Khóa Kaggle từ validation, seed 42 |
| B2-rand s42 | ReVeal | 0,89 | Khóa Kaggle từ validation, seed 42 |
| B2-rand s43 | Devign | 0,99 | Khóa Kaggle từ validation, seed 43 |
| B2-rand s43 | ReVeal | 0,62 | Khóa Kaggle từ validation, seed 43 |
| B2-rand s44 | Devign | 0,99 | Khóa Kaggle từ validation, seed 44 |
| B2-rand s44 | ReVeal | 0,64 | Khóa Kaggle từ validation, seed 44 |
| B2-rep | Devign | 0,70 | Khóa validation B2 kế thừa |
| B2-rep | ReVeal | 0,12 | Khóa validation B2 kế thừa |
| B2-nolabel | Devign | 0,98 | Khóa riêng từ validation |
| B2-nolabel | ReVeal | 0,21 | Khóa riêng từ validation |
| B2-labelonly | Devign | 0,99 | Khóa riêng từ validation |
| B2-labelonly | ReVeal | 0,02 | Khóa riêng từ validation |
| B2-flip | Devign | 0,70 | Kế thừa ngưỡng B2, không fit riêng cho arm đảo nhãn |
| B2-flip | ReVeal | 0,12 | Kế thừa ngưỡng B2, không fit riêng cho arm đảo nhãn |
| B1-H2 | Devign | 0,09 | Khóa riêng từ validation |
| B1-H2 | ReVeal | 0,21 | Khóa validation Kaggle |
| B3-nodiff | Devign | 0,92 | Khóa riêng trên validation B3-nodiff; giữ nguyên khi đánh giá test |
| B3-nodiff | ReVeal | 0,01 | Khóa riêng trên validation B3-nodiff; giữ nguyên khi đánh giá test |
| B3 (verified-patch-v1) | Devign | 0,99 | Khóa validation của B3; không fit lại trên test |
| B3 (verified-patch-v1) | ReVeal | 0,01 | Khóa validation của B3; không fit lại trên test |
| B3-swap | Devign | 0,99 | Kế thừa ngưỡng B3; không fit riêng cho probe |
| B3-swap | ReVeal | 0,01 | Kế thừa ngưỡng B3; không fit riêng cho probe |
| B3-flip | Devign | 0,99 | Kế thừa ngưỡng B3; không fit riêng cho probe |
| B3-flip | ReVeal | 0,01 | Kế thừa ngưỡng B3; không fit riêng cho probe |

#### Nguồn, ngày và commit khóa ngưỡng validation

Ngày khóa dưới đây trình bày theo giờ Bangkok (UTC+7). Link ở cột nguồn mở đúng artifact/commit đã ghi ngưỡng. Với các arm kế thừa, ngày và commit trỏ về khóa của arm gốc; probe không được chọn ngưỡng riêng.

| Arm/ngưỡng dùng trong báo cáo | Ngày khóa (Bangkok) | Artifact khóa trên GitHub | Commit khóa |
|---|---|---|---|
| B0 — ngưỡng trong bảng là bản hiệu chỉnh hồi cứu trên full validation, Devign 0,98 / ReVeal 0,30; không phải ngưỡng preregistered | 06/11/2026 (phân tích hậu kiểm) | [Kết quả tính lại validation](https://github.com/kazunguyen/GRACE-summary/blob/90c5b3ff5f5e86927ab2a8b451c99c458fcddcaf/Runs-management/reanalysis_20261106/results.json). Ngưỡng khóa gốc là 0,08/0,44 trong [ledger tại lần khóa](https://github.com/kazunguyen/GRACE-summary/blob/31a37a3d3e11af249a620f1cf68dcd1724c6a592/Runs-management/thresholds.json#L115). | [90c5b3f](https://github.com/kazunguyen/GRACE-summary/commit/90c5b3ff5f5e86927ab2a8b451c99c458fcddcaf) (hậu kiểm); [31a37a3](https://github.com/kazunguyen/GRACE-summary/commit/31a37a3d3e11af249a620f1cf68dcd1724c6a592) (khóa gốc, 01/11) |
| B1 — ngưỡng trong bảng là bản hiệu chỉnh hồi cứu trên full validation, Devign 0,98 / ReVeal 0,63; không phải ngưỡng preregistered | 06/11/2026 (phân tích hậu kiểm) | [Kết quả tính lại validation](https://github.com/kazunguyen/GRACE-summary/blob/90c5b3ff5f5e86927ab2a8b451c99c458fcddcaf/Runs-management/reanalysis_20261106/results.json). Ngưỡng khóa gốc là 0,88/0,74 trong [ledger tại lần khóa](https://github.com/kazunguyen/GRACE-summary/blob/c2e10e47b75fe7a57866e2b8509c3111fb504130/Runs-management/thresholds.json#L1862). | [90c5b3f](https://github.com/kazunguyen/GRACE-summary/commit/90c5b3ff5f5e86927ab2a8b451c99c458fcddcaf) (hậu kiểm); [c2e10e4](https://github.com/kazunguyen/GRACE-summary/commit/c2e10e47b75fe7a57866e2b8509c3111fb504130) (khóa gốc, 02/11) |
| B1-full | 07/11/2026 09:03 | [Threshold lock: Devign + ReVeal](https://github.com/kazunguyen/GRACE-summary/blob/68b7bf137bb9b957051c46a86d53ec41a528731c/Runs-management/run_handoff_20261108/completed_results/b1_full_test_completed_20261108/threshold_lock.json) | [68b7bf1](https://github.com/kazunguyen/GRACE-summary/commit/68b7bf137bb9b957051c46a86d53ec41a528731c) |
| B1-H2 | 06/11/2026 22:04 (Kaggle lock thay bản Colab trước đó) | [Kaggle validation threshold lock](https://github.com/kazunguyen/GRACE-summary/blob/4838a55135e2d9a5b19292815e3c4b5a12467ed9/Runs-management/b1h2_kaggle_validation_threshold_lock_20261106.json) | [4838a55](https://github.com/kazunguyen/GRACE-summary/commit/4838a55135e2d9a5b19292815e3c4b5a12467ed9) |
| B1-shuf — seeds 42/43/44 | 07/11/2026 13:05 | [Threshold lock cả ba seed, hai dataset](https://github.com/kazunguyen/GRACE-summary/blob/acf41fe88de95adfa41b3fcb82ace3e8d5eb512f/08_Arm_B1_Shuf/config/threshold.json) | [acf41fe](https://github.com/kazunguyen/GRACE-summary/commit/acf41fe88de95adfa41b3fcb82ace3e8d5eb512f) |
| B2 | 01/11/2026 (Devign 16:57; ReVeal 17:42) | [Ledger khóa validation](https://github.com/kazunguyen/GRACE-summary/blob/31a37a3d3e11af249a620f1cf68dcd1724c6a592/Runs-management/thresholds.json#L981) | [31a37a3](https://github.com/kazunguyen/GRACE-summary/commit/31a37a3d3e11af249a620f1cf68dcd1724c6a592) |
| B2-flip, B2-rep — kế thừa τ của B2 | 02/11/2026 18:01 (ghi nhận policy kế thừa) | [Ledger B2-flip](https://github.com/kazunguyen/GRACE-summary/blob/c2e10e47b75fe7a57866e2b8509c3111fb504130/Runs-management/thresholds.json#L1881) · [B2-rep](https://github.com/kazunguyen/GRACE-summary/blob/c2e10e47b75fe7a57866e2b8509c3111fb504130/Runs-management/thresholds.json#L1900) | [c2e10e4](https://github.com/kazunguyen/GRACE-summary/commit/c2e10e47b75fe7a57866e2b8509c3111fb504130) |
| B2-rand — seeds 42/43 | 07/11/2026 08:24 | [Threshold lock seeds 42/43](https://github.com/kazunguyen/GRACE-summary/blob/ad67f3035b6389334198893e189c2e26cca1b069/06_Arm_B2_Rand/config/threshold.json) | [ad67f30](https://github.com/kazunguyen/GRACE-summary/commit/ad67f3035b6389334198893e189c2e26cca1b069) |
| B2-rand — seed 44 | 07/11/2026 16:13 | [Threshold lock ba seed](https://github.com/kazunguyen/GRACE-summary/blob/7c9dbbf87d650758d501ac129cf157cd0d1095cd/06_Arm_B2_Rand/config/threshold.json) | [7c9dbbf](https://github.com/kazunguyen/GRACE-summary/commit/7c9dbbf87d650758d501ac129cf157cd0d1095cd) |
| B2-nolabel | 07/11/2026 09:03 | [Threshold lock](https://github.com/kazunguyen/GRACE-summary/blob/005dabeb4d303f52f7f34479aa67845336eeaf3f/10_Arm_B2_NoLabel/config/threshold.json) | [005dab](https://github.com/kazunguyen/GRACE-summary/commit/005dabeb4d303f52f7f34479aa67845336eeaf3f) |
| B2-labelonly | 07/11/2026 09:03 | [Threshold lock](https://github.com/kazunguyen/GRACE-summary/blob/005dabeb4d303f52f7f34479aa67845336eeaf3f/12_Arm_B2_LabelOnly/config/threshold.json) | [005dab](https://github.com/kazunguyen/GRACE-summary/commit/005dabeb4d303f52f7f34479aa67845336eeaf3f) |
| B3 (verified-patch-v1) | 09/11/2026 19:50 | [Devign lock](https://github.com/kazunguyen/GRACE-summary/blob/b58ca2e1115d3d076818fd4f4c32f25520eee904/Runs-management/b3_verified_patch_v1/threshold_release_20261109_v1/devign_threshold_lock.json) · [ReVeal lock](https://github.com/kazunguyen/GRACE-summary/blob/b58ca2e1115d3d076818fd4f4c32f25520eee904/Runs-management/b3_verified_patch_v1/threshold_release_20261109_v1/reveal_threshold_lock.json) | [b58ca2e](https://github.com/kazunguyen/GRACE-summary/commit/b58ca2e1115d3d076818fd4f4c32f25520eee904) |
| B3-swap, B3-flip — kế thừa τ của B3 | 09/11/2026 19:50 (khóa B3 gốc) | [Devign lock](https://github.com/kazunguyen/GRACE-summary/blob/b58ca2e1115d3d076818fd4f4c32f25520eee904/Runs-management/b3_verified_patch_v1/threshold_release_20261109_v1/devign_threshold_lock.json) · [ReVeal lock](https://github.com/kazunguyen/GRACE-summary/blob/b58ca2e1115d3d076818fd4f4c32f25520eee904/Runs-management/b3_verified_patch_v1/threshold_release_20261109_v1/reveal_threshold_lock.json) | [b58ca2e](https://github.com/kazunguyen/GRACE-summary/commit/b58ca2e1115d3d076818fd4f4c32f25520eee904) |
| B3-nodiff | 09/11/2026 17:17 | [Validation threshold lock](https://github.com/kazunguyen/GRACE-summary/blob/f5a94dc1464ac572126c01013e289fede217cf23/Runs-management/run_handoff_20261109/B3_NODIFF_VALIDATION/validation_threshold_lock.json) | [f5a94dc](https://github.com/kazunguyen/GRACE-summary/commit/f5a94dc1464ac572126c01013e289fede217cf23) |



### 1.2. Kết quả trên validation

Các metric phân loại dùng quy tắc `dự đoán vulnerable nếu s ≥ τ`. Tất cả các hàng có đủ số score hợp lệ; cột “raw lỗi” đếm phản hồi thô không hợp lệ nhưng score số vẫn được giữ và đưa vào tính metric.

| Dataset | Arm | N | Raw lỗi | MCC | AUROC | AUPRC (AP) | F1 | Balanced accuracy | Precision | Recall | Tỷ lệ dự đoán 1 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Devign | B0 | 2.732 | 284 | 0,0760 | 0,4654 | 0,4743 | 0,3202 | 0,5306 | 0,5101 | 0,2334 | 0,1988 |
| Devign | B1 | 2.732 | 0 | 0,0748 | 0,5318 | 0,4632 | 0,3354 | 0,5310 | 0,5051 | 0,2511 | 0,2160 |
| Devign | B2 | 2.732 | 0 | 0,0547 | 0,5256 | 0,4501 | 0,5304 | 0,5270 | 0,4565 | 0,6327 | 0,6021 |
| Devign | B2-flip | 2.732 | 0 | 0,0025 | 0,5137 | 0,4433 | 0,4945 | 0,5012 | 0,4355 | 0,5720 | 0,5706 |
| Devign | B1-H2 | 2.732 | 146 | 0,0668 | 0,5348 | 0,4608 | 0,5279 | 0,5333 | 0,4629 | 0,6142 | 0,5765 |
| Devign | B2-rand s42 | 2.732 | 0 | 0,0662 | 0,5307 | 0,4640 | 0,3356 | 0,5278 | 0,4959 | 0,2536 | 0,2222 |
| Devign | B2-rand s43 | 2.732 | 0 | 0,0610 | 0,5289 | 0,4597 | 0,3330 | 0,5256 | 0,4910 | 0,2519 | 0,2229 |
| ReVeal | B0 | 2.273 | 261 | 0,0801 | 0,5644 | 0,1138 | 0,1962 | 0,5657 | 0,1245 | 0,4619 | 0,3427 |
| ReVeal | B1 | 2.273 | 3 | 0,0833 | 0,5879 | 0,1178 | 0,1952 | 0,5611 | 0,1357 | 0,3476 | 0,2367 |
| ReVeal | B2 | 2.273 | 0 | 0,0823 | 0,5544 | 0,1050 | 0,1956 | 0,5709 | 0,1149 | 0,6571 | 0,5284 |
| ReVeal | B2-flip | 2.273 | 0 | 0,0327 | 0,5256 | 0,0946 | 0,1715 | 0,5282 | 0,1022 | 0,5333 | 0,4822 |
| ReVeal | B1-H2 | 2.273 | 153 | 0,0836 | 0,5669 | 0,1213 | 0,1984 | 0,5687 | 0,1256 | 0,4714 | 0,3467 |
| ReVeal | B2-rand s42 | 2.273 | 2 | 0,0808 | 0,5638 | 0,1103 | 0,1899 | 0,5553 | 0,1400 | 0,2952 | 0,1949 |
| ReVeal | B2-rand s43 | 2.273 | 0 | 0,0771 | 0,5743 | 0,1150 | 0,1921 | 0,5587 | 0,1296 | 0,3714 | 0,2648 |

### 1.3. Kết quả trên test

**Bảng: Metric test theo từng arm và dataset tại ngưỡng đang áp dụng**

| Dataset | Arm | N | Raw lỗi | MCC | AUROC | AUPRC (AP) | F1 | Balanced accuracy | Precision | Recall | Tỷ lệ dự đoán 1 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Devign | B0 | 2.732 | 302 | 0,0922 | 0,5405 | 0,5153 | 0,3343 | 0,5370 | 0,5513 | 0,2398 | 0,1999 |
| Devign | B1 | 2.732 | 0 | 0,0788 | 0,5335 | 0,5023 | 0,3457 | 0,5328 | 0,5332 | 0,2558 | 0,2204 |
| Devign | B2 | 2.732 | 0 | 0,0597 | 0,5305 | 0,4856 | 0,5485 | 0,5293 | 0,4836 | 0,6335 | 0,6018 |
| Devign | B2-flip | 2.732 | 0 | 0,0337 | 0,5240 | 0,4857 | 0,5355 | 0,5166 | 0,4731 | 0,6167 | 0,5988 |
| ReVeal | B0 | 2.274 | 285 | 0,0874 | 0,5740 | 0,1260 | 0,2129 | 0,5700 | 0,1356 | 0,4957 | 0,3698 |
| ReVeal | B1 | 2.274 | 2 | 0,0523 | 0,5841 | 0,1238 | 0,1816 | 0,5370 | 0,1294 | 0,3043 | 0,2379 |
| ReVeal | B2 | 2.274 | 0 | 0,0645 | 0,5662 | 0,1221 | 0,2005 | 0,5531 | 0,1183 | 0,6565 | 0,5611 |
| ReVeal | B2-flip | 2.274 | 0 | 0,0372 | 0,5261 | 0,1051 | 0,1875 | 0,5308 | 0,1118 | 0,5826 | 0,5273 |
| Devign | B1-shuf s42 | 2.732 | 0 | 0,0847 | 0,5431 | 0,5079 | 0,2288 | 0,5270 | 0,5774 | 0,1426 | 0,1135 |
| Devign | B1-shuf s43 | 2.732 | 0 | 0,0497 | 0,5343 | 0,4988 | 0,2413 | 0,5172 | 0,5212 | 0,1570 | 0,1384 |
| Devign | B1-shuf s44 | 2.732 | 0 | 0,0661 | 0,5351 | 0,5002 | 0,3674 | 0,5289 | 0,5159 | 0,2853 | 0,2540 |
| ReVeal | B1-shuf s42 | 2.274 | 2 | 0,0378 | 0,5777 | 0,1238 | 0,1474 | 0,5212 | 0,1304 | 0,1696 | 0,1315 |
| ReVeal | B1-shuf s43 | 2.274 | 2 | 0,0945 | 0,5798 | 0,1228 | 0,2157 | 0,5784 | 0,1297 | 0,6391 | 0,4982 |
| ReVeal | B1-shuf s44 | 2.274 | 2 | 0,0604 | 0,5683 | 0,1185 | 0,1955 | 0,5478 | 0,1258 | 0,4391 | 0,3531 |
| Devign | B1-full | 2.732 | 0 | 0,0696 | 0,5311 | 0,4979 | 0,3125 | 0,5275 | 0,5305 | 0,2215 | 0,1918 |
| ReVeal | B1-full | 2.274 | 2 | 0,0849 | 0,5782 | 0,1227 | 0,2096 | 0,5697 | 0,1234 | 0,6957 | 0,5704 |
| Devign | B2-rand s42 | 2.732 | 0 | 0,0343 | 0,5318 | 0,4961 | 0,3230 | 0,5144 | 0,4911 | 0,2406 | 0,2251 |
| Devign | B2-rand s43 | 2.732 | 0 | 0,0664 | 0,5336 | 0,4980 | 0,3382 | 0,5276 | 0,5216 | 0,2502 | 0,2204 |
| ReVeal | B2-rand s42 | 2.274 | 0 | 0,0453 | 0,5805 | 0,1227 | 0,1703 | 0,5300 | 0,1286 | 0,2522 | 0,1983 |
| ReVeal | B2-rand s43 | 2.274 | 0 | 0,0596 | 0,5747 | 0,1235 | 0,1910 | 0,5444 | 0,1299 | 0,3609 | 0,2810 |
| Devign | B2-rep | 2.732 | 0 | 0,0597 | 0,5305 | 0,4856 | 0,5485 | 0,5293 | 0,4836 | 0,6335 | 0,6018 |
| ReVeal | B2-rep | 2.274 | 0 | 0,0645 | 0,5662 | 0,1221 | 0,2005 | 0,5531 | 0,1183 | 0,6565 | 0,5611 |
| Devign | B2-nolabel | 2.732 | 0 | 0,0518 | 0,5269 | 0,4856 | 0,4364 | 0,5250 | 0,4935 | 0,3912 | 0,3642 |
| ReVeal | B2-nolabel | 2.274 | 1 | 0,0835 | 0,5721 | 0,1219 | 0,2103 | 0,5692 | 0,1269 | 0,6130 | 0,4886 |
| Devign | B2-labelonly | 2.732 | 0 | 0,0849 | 0,5462 | 0,5132 | 0,3013 | 0,5322 | 0,5520 | 0,2072 | 0,1724 |
| ReVeal | B2-labelonly | 2.274 | 0 | 0,1199 | 0,6005 | 0,1308 | 0,2310 | 0,5986 | 0,1423 | 0,6130 | 0,4358 |


### 1.4. Các mốc phân loại có giám sát (Step 6)

**Ảnh hưởng của seed đến ngưỡng validation.** Runner gọi `.fit()` riêng cho từng seed 42, 43 và 44. SUP-LR dùng embedding CodeT5, còn SUP-METRIC dùng 26 đặc trưng mã nguồn. Cả hai dùng `StandardScaler` và `LogisticRegression` của scikit-learn. Runner truyền `random_state=seed` cho `LogisticRegression`, nhưng để solver mặc định là `lbfgs`. Tham số này được nhận khi khởi tạo model, còn `lbfgs` không sử dụng nó để tối ưu. Với cùng tập train và cấu hình, ba lượt fit cho cùng điểm validation theo từng ID ở độ chính xác lưu trong `anchor_scores.csv`.

Với mỗi bộ điểm validation, runner thử các ngưỡng từ 0,01 đến 0,99 và chọn ngưỡng có MCC cao nhất. Khi MCC bằng nhau, runner ưu tiên ngưỡng gần 0,5 nhất. Vì điểm và nhãn validation giống nhau giữa các seed, phép chọn ngưỡng trả về cùng `τ*`. Trên Devign, cả ba seed cho `τ* = 0,37` với SUP-LR và `τ* = 0,58` với SUP-METRIC. Trên ReVeal, cả hai anchor đều cho `τ* = 0,15` ở cả ba seed. Dòng `42/43/44` trong bảng gộp ba lượt có cùng kết quả. Với SUP-MLP, seed ảnh hưởng đến khởi tạo trọng số và quá trình huấn luyện, nên điểm validation và ngưỡng có thể thay đổi theo seed. Ví dụ, ba ngưỡng SUP-MLP trên Devign lần lượt là 0,78, 0,77 và 0,34.

**Bảng 1.4a. Ngưỡng τ* và kết quả của các mốc có giám sát trên validation**

| Dataset | Arm | Seed | τ validation | MCC validation | AUROC validation |
|---|---|---:|---:|---:|---:|
| Devign | SUP-LR | 42/43/44 | 0,37 | 0,2262 | 0,6527 |
| Devign | SUP-MLP | 42 | 0,78 | 0,2456 | 0,6702 |
| Devign | SUP-MLP | 43 | 0,77 | 0,2499 | 0,6680 |
| Devign | SUP-MLP | 44 | 0,34 | 0,2438 | 0,6572 |
| Devign | SUP-METRIC | 42/43/44 | 0,58 | 0,1348 | 0,5476 |
| ReVeal | SUP-LR | 42/43/44 | 0,15 | 0,3086 | 0,7894 |
| ReVeal | SUP-MLP | 42 | 0,11 | 0,3257 | 0,8014 |
| ReVeal | SUP-MLP | 43 | 0,08 | 0,3128 | 0,7955 |
| ReVeal | SUP-MLP | 44 | 0,26 | 0,3416 | 0,7869 |
| ReVeal | SUP-METRIC | 42/43/44 | 0,15 | 0,2483 | 0,7124 |

Các giá trị validation là MCC tại τ đã chọn và AUROC trên validation, trích từ summary khóa. Metric test ở dưới được tính độc lập từ score và nhãn frozen.

**Bảng 1.4b. Kết quả của các mốc có giám sát trên test với ngưỡng τ* từ validation**

| Dataset | Arm | Seed | N | τ | MCC | AUROC | AUPRC (AP) | F1 | Balanced accuracy | Precision | Recall | Tỷ lệ dự đoán 1 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Devign | SUP-LR | 42/43/44 | 2.732 | 0,37 | 0,2190 | 0,6559 | 0,6321 | 0,6332 | 0,6044 | 0,5385 | 0,7681 | 0,6552 |
| Devign | SUP-MLP | 42 | 2.732 | 0,78 | 0,1829 | 0,6737 | 0,6449 | 0,1781 | 0,5417 | 0,8389 | 0,0996 | 0,0545 |
| Devign | SUP-MLP | 43 | 2.732 | 0,77 | 0,2219 | 0,6647 | 0,6519 | 0,4074 | 0,5881 | 0,6842 | 0,2900 | 0,1947 |
| Devign | SUP-MLP | 44 | 2.732 | 0,34 | 0,1907 | 0,6497 | 0,6251 | 0,6280 | 0,5885 | 0,5231 | 0,7857 | 0,6900 |
| Devign | SUP-METRIC | 42/43/44 | 2.732 | 0,58 | 0,1298 | 0,5668 | 0,5420 | 0,1625 | 0,5306 | 0,7188 | 0,0916 | 0,0586 |
| ReVeal | SUP-LR | 42/43/44 | 2.274 | 0,15 | 0,2584 | 0,7709 | 0,2841 | 0,3404 | 0,6750 | 0,2516 | 0,5261 | 0,2115 |
| ReVeal | SUP-MLP | 42 | 2.274 | 0,11 | 0,3015 | 0,7809 | 0,3147 | 0,3728 | 0,7078 | 0,2713 | 0,5957 | 0,2221 |
| ReVeal | SUP-MLP | 43 | 2.274 | 0,08 | 0,2641 | 0,7688 | 0,2713 | 0,3356 | 0,6975 | 0,2276 | 0,6391 | 0,2841 |
| ReVeal | SUP-MLP | 44 | 2.274 | 0,26 | 0,2492 | 0,7481 | 0,2843 | 0,3300 | 0,6330 | 0,3071 | 0,3565 | 0,1174 |
| ReVeal | SUP-METRIC | 42/43/44 | 2.274 | 0,15 | 0,1760 | 0,6733 | 0,2098 | 0,2735 | 0,6085 | 0,2202 | 0,3609 | 0,1658 |

### 1.5. Giá trị bổ sung sau truy vấn và định tuyến theo ngân sách (Step 6)

#### Cặp meta-model P_pre/P_post

Hai meta-model logistic dùng cùng 34 đặc trưng nền, cùng 3 fold StratifiedGroupKFold, cùng scaler và fallback đối xứng khi expert invalid. Ngưỡng của từng model được chọn từ validation OOF. CI dùng paired cluster bootstrap 5.000 lượt.

**Đơn vị cụm của Step 6.** Devign dùng `commit_id` (2.025 cụm validation và 2.068 cụm test). ReVeal dùng mã file `source_id` (627 cụm validation và 646 cụm test). Cả chia fold OOF lẫn bootstrap dùng cùng định nghĩa cụm cho từng dataset. Số cụm test khớp giao thức và Bảng B.

**Bảng 1.5a. Ngưỡng chọn từ dự đoán OOF trên validation và kết quả test của P_pre và P_post**

| Dataset | Model | τ OOF | MCC test | AUROC test | AP test | BA test | F1 test | Precision | Recall | Tỷ lệ dự đoán 1 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Devign | P_pre | 0,53 | 0,2866 | 0,7136 | 0,6787 | 0,6307 | 0,5300 | 0,6817 | 0,4335 | 0,2921 |
| Devign | P_post | 0,52 | 0,2851 | 0,7120 | 0,6780 | 0,6321 | 0,5398 | 0,6722 | 0,4510 | 0,3082 |
| ReVeal | P_pre | 0,20 | 0,3769 | 0,8094 | 0,3491 | 0,7170 | 0,4444 | 0,3824 | 0,5304 | 0,1403 |
| ReVeal | P_post | 0,25 | 0,3758 | 0,8089 | 0,3512 | 0,6993 | 0,4422 | 0,4144 | 0,4739 | 0,1157 |

**Bảng 1.5b. Chênh lệch MCC và AUROC trên test giữa P_post và P_pre khi dùng hai ngưỡng OOF riêng, kèm khoảng tin cậy 95%**

| Dataset | ΔMCC (P_post − P_pre) | CI 95% | ΔAUROC | CI 95% | Kết luận theo δ MCC=0,02 |
|---|---:|---:|---:|---:|---|
| Devign | −0,0015 | [−0,0122; 0,0093] | −0,0016 | [−0,0041; 0,0009] | Cận trên < 0,02: loại trừ mức tăng MCC có ý nghĩa đã định trước |
| ReVeal | −0,0011 | [−0,0290; 0,0260] | −0,0004 | [−0,0017; 0,0009] | Cận trên vượt 0,02: chưa đủ bằng chứng loại trừ mức tăng MCC 0,02 |

**Bảng 1.5c. H5.2 khi áp cùng ngưỡng cho P_pre và P_post**

Trên mỗi dataset, lấy ngưỡng tối đa hóa MCC trên dự đoán validation OOF của P_pre và áp ngưỡng đó cho cả hai bộ score test. Cách chọn này giữ điểm hoạt động của model tham chiếu P_pre. Hai model dùng cùng fold, cùng 34 đặc trưng nền và cùng quy tắc fallback đã mô tả ở trên. CI của ΔMCC dùng paired cluster bootstrap 5.000 lượt, seed `20261117`, với cùng cụm được rút cho cả hai model. Cả hai dataset đều có 0 lượt bootstrap suy biến. [Mã chạy](../Runs-management/analysis_pa1_20261111/h52_shared_threshold.py) · [Kết quả và SHA-256 đầu vào](../Runs-management/analysis_pa1_20261111/full_tables/h52_shared_threshold.json)

| Dataset | Ngưỡng chung | MCC P_pre | MCC P_post | ΔMCC P_post − P_pre [CI 95%] | Cận trên < 0,02 |
|---|---:|---:|---:|---:|---|
| Devign | 0,53 | 0,2866 | 0,2858 | −0,0008 [−0,0095; 0,0080] | Đạt |
| ReVeal | 0,20 | 0,3769 | 0,3690 | −0,0078 [−0,0169; −0,0010] | Đạt |

Với ngưỡng chung, cả hai dataset đều loại trừ mức tăng MCC từ 0,02 trở lên. Trên ReVeal, CI nằm dưới 0, cho thấy P_post giảm MCC tại ngưỡng chung đã chọn. Kết quả theo hai ngưỡng OOF riêng ở Bảng 1.5b vẫn được báo riêng. Với cách dùng hai ngưỡng, cận trên CI trên ReVeal là 0,0260.

#### Benefit-router của H3-B gate theo ngân sách

`Random` là 20 router chọn ngẫu nhiên đúng `ceil(qN)` mẫu; các khoảng là phân vị 2,5–97,5% của 20 lượt, không phải CI paired của chênh lệch. `Repair/harm` so với H3-B gate trước routing.

| Dataset | Ngân sách | Số truy vấn | BA benefit | BA random: TB [P2,5; P97,5] | MCC benefit | MCC random: TB [P2,5; P97,5] | Repair / harm benefit |
|---|---:|---:|---:|---:|---:|---:|---:|
| Devign | 5% | 137 | 0,6448 | 0,6336 [0,6286; 0,6365] | 0,2991 | 0,2781 [0,2680; 0,2839] | 34 / 15 |
| Devign | 10% | 274 | 0,6482 | 0,6279 [0,6211; 0,6338] | 0,3049 | 0,2666 [0,2530; 0,2791] | 55 / 25 |
| Devign | 25% | 683 | 0,6444 | 0,6104 [0,6016; 0,6203] | 0,2908 | 0,2301 [0,2122; 0,2507] | 128 / 97 |
| ReVeal | 5% | 114 | 0,6643 | 0,6943 [0,6856; 0,7042] | 0,3178 | 0,3239 [0,3089; 0,3423] | 47 / 24 |
| ReVeal | 10% | 228 | 0,6402 | 0,6888 [0,6756; 0,6996] | 0,2871 | 0,3017 [0,2813; 0,3196] | 68 / 41 |
| ReVeal | 25% | 569 | 0,6065 | 0,6651 [0,6529; 0,6869] | 0,2143 | 0,2403 [0,2235; 0,2717] | 85 / 93 |

**Đối chiếu H5.3 tại ngân sách 10%.** Lần chạy notebook 06 bổ sung đã xuất CI ghép cặp với 5.000 lượt bootstrap. Phép Benefit−Random lấy mẫu lại theo cụm test và lấy lại có hoàn lại từ 20 seed của random router. Dùng H3-B gate làm nền chính.

| Dataset | ΔBA Benefit−Confidence [CI 95%] | ΔMCC Benefit−Confidence [CI 95%] | ΔBA Benefit−Random [CI 95%] | Ca B2 sửa đúng / phân vị 97,5% của random expert | Kết quả theo lần chạy Step 6 |
|---|---:|---:|---:|---:|---|
| Devign | +0,0095 [−0,0010; 0,0199] | +0,0148 [−0,0062; 0,0357] | +0,0204 [0,0138; 0,0270] | 397 / 465,05 | Chưa đạt hai điều kiện cận trên cho MCC Benefit−Confidence và BA Benefit−Random |
| ReVeal | −0,0644 [−0,0991; −0,0307] | −0,0509 [−0,1106; 0,0058] | −0,0487 [−0,0748; −0,0249] | 164 / 176,15 | Đạt các điều kiện H5.3 |

Tiêu chí gồm cận trên CI Benefit−Confidence dưới 0,02 cho BA và MCC, cận trên CI BA Benefit−Random dưới 0,01, và số ca B2 sửa đúng không vượt phân vị 97,5% của expert ngẫu nhiên có cùng tỷ lệ dự đoán dương. Cột số ca sửa dùng toàn bộ test cho cả B2 và random expert. Bảng ngân sách phía trên ghi riêng 55/68 ca sửa của benefit router khi chỉ gọi B2 trên khoảng 10% test.

Nguồn là [manifest lượt chạy Step 6 ngày 11/11](../STEP6_supervised_anchors/runs/complementarity_step6/step6_lock_64fb2c99d904_44f00d19/analysis_manifest.json) và kết quả theo dataset [Devign](../STEP6_supervised_anchors/runs/complementarity_step6/step6_lock_64fb2c99d904_44f00d19/devign/complementarity_step6.json), [ReVeal](../STEP6_supervised_anchors/runs/complementarity_step6/step6_lock_64fb2c99d904_44f00d19/reveal/complementarity_step6.json).

### 1.6. CI ghép cặp, McNemar và độ nhạy nhãn

**Chú thích về ngưỡng B0/B1.** Do sai sót khi lập bảng ngưỡng đăng ký, bốn giá trị gốc của B0 và B1 được ghi vào `thresholds.json` dưới dạng giá trị cố định, trong khi giao thức yêu cầu chọn ngưỡng tối đa hóa MCC trên toàn bộ validation. Bộ ngưỡng hiệu chỉnh là bộ ngưỡng đúng theo quy tắc này. Ngày 06/11, các ngưỡng được tính lại từ score inference và nhãn của toàn bộ validation. Nhãn test không tham gia chọn ngưỡng. Vì việc hiệu chỉnh diễn ra sau khi nhóm đã xem kết quả test, các metric test tính theo bộ ngưỡng này là **kết quả hồi cứu**. [Hồ sơ hiệu chỉnh và kiểm chứng trên validation](https://github.com/kazunguyen/GRACE-summary/blob/d9127fc7b12a128d8499012454ad134733f810ff/Runs-management/osf_amendment_20261106/README.md) · [Kết quả tính lại ngày 06/11](https://github.com/kazunguyen/GRACE-summary/blob/90c5b3ff5f5e86927ab2a8b451c99c458fcddcaf/Runs-management/reanalysis_20261106/REPORT.md)

Theo yêu cầu của đề cương, báo cáo vẫn trình bày kết quả theo ngưỡng gốc để đối chiếu với hồ sơ đăng ký. Theo đánh giá của em, các kết quả đó chỉ có giá trị đối chiếu lịch sử. Để diễn giải chênh lệch giữa các arm có B0 hoặc B1 tại ngưỡng tối ưu trên validation, báo cáo dựa vào bộ ngưỡng hiệu chỉnh và ghi rõ tính hồi cứu.

**Bảng A. Chênh lệch AUROC và MCC trên test, kèm khoảng tin cậy ghép cặp 95%**

Các chênh lệch lấy arm đứng trước dấu trừ trừ arm đứng sau. CI dùng paired cluster bootstrap 5.000 lượt với seed 20261117 và giữ ngưỡng cố định. Hai cột MCC chỉ khác nhau khi cặp có B0 hoặc B1. Cột MCC sau hiệu chỉnh để trống ở các cặp không có B0 hoặc B1 vì hai arm giữ nguyên ngưỡng. Test Devign có 2.732 mẫu trong 2.068 cụm commit và test ReVeal có 2.274 mẫu trong 646 cụm file.

| Phép so | Dataset | ΔAUROC [CI 95%] | ΔMCC [CI 95%] theo ngưỡng gốc hoặc ngưỡng arm | ΔMCC [CI 95%] sau hiệu chỉnh B0/B1 |
|---|---|---:|---:|---:|
| B2 − B0 | Devign | −0,0100 [−0,0280; 0,0078] | 0,0306 [−0,0080; 0,0681] | −0,0325 [−0,0750; 0,0106] |
| B2 − B0 | ReVeal | −0,0079 [−0,0357; 0,0183] | −0,0211 [−0,0634; 0,0207] | −0,0229 [−0,0630; 0,0153] |
| B1 − B0 | Devign | −0,0070 [−0,0197; 0,0057] | 0,0349 [−0,0084; 0,0759] | −0,0134 [−0,0459; 0,0183] |
| B1 − B0 | ReVeal | 0,0101 [−0,0092; 0,0287] | −0,0324 [−0,0708; 0,0049] | −0,0351 [−0,0743; 0,0014] |
| B1 − B1-shuf | Devign | −0,0096 [−0,0233; 0,0041] | −0,0207 [−0,0600; 0,0198] | −0,0060 [−0,0426; 0,0322] |
| B1 − B1-shuf | ReVeal | 0,0064 [−0,0161; 0,0296] | 0,0154 [−0,0220; 0,0547] | 0,0145 [−0,0250; 0,0559] |
| B2 − B2-rand | Devign | −0,0013 [−0,0158; 0,0140] | 0,0254 [−0,0152; 0,0673] | |
| B2 − B2-rand | ReVeal | −0,0143 [−0,0352; 0,0064] | 0,0192 [−0,0299; 0,0675] | |
| B2-nolabel − B1 | Devign | −0,0066 [−0,0183; 0,0052] | −0,0123 [−0,0437; 0,0181] | −0,0270 [−0,0587; 0,0058] |
| B2-nolabel − B1 | ReVeal | −0,0120 [−0,0288; 0,0049] | 0,0303 [−0,0132; 0,0733] | 0,0312 [−0,0130; 0,0755] |
| B2-flip − B2 | Devign | −0,0065 [−0,0233; 0,0105] | −0,0260 [−0,0609; 0,0094] | |
| B2-flip − B2 | ReVeal | −0,0401 [−0,0648; −0,0155] | −0,0273 [−0,0607; 0,0049] | |
| B2 − B2-labelonly | Devign | −0,0158 [−0,0345; 0,0024] | −0,0251 [−0,0738; 0,0229] | |
| B2 − B2-labelonly | ReVeal | −0,0344 [−0,0588; −0,0103] | −0,0554 [−0,0911; −0,0209] | |
| SUP-LR − B2 | Devign | 0,1254 [0,0862; 0,1672] | 0,1593 [0,0952; 0,2267] | |
| SUP-LR − B2 | ReVeal | 0,2048 [0,1426; 0,2636] | 0,1939 [0,1136; 0,2714] | |
| P_post − P_pre | Devign | −0,0016 [−0,0041; 0,0009] | −0,0015 [−0,0122; 0,0093] | |
| P_post − P_pre | ReVeal | −0,0004 [−0,0017; 0,0009] | −0,0011 [−0,0290; 0,0260] | |
| B2 − B1 | Devign | −0,0030 [−0,0186; 0,0122] | −0,0044 [−0,0412; 0,0332] | −0,0191 [−0,0605; 0,0227] |
| B2 − B1 | ReVeal | −0,0179 [−0,0400; 0,0041] | 0,0113 [−0,0337; 0,0560] | 0,0121 [−0,0339; 0,0568] |
| B2-labelonly − B1 | Devign | 0,0128 [0,0050; 0,0204] | 0,0208 [−0,0139; 0,0557] | 0,0061 [−0,0235; 0,0366] |
| B2-labelonly − B1 | ReVeal | 0,0165 [0,0041; 0,0294] | 0,0667 [0,0233; 0,1094] | 0,0676 [0,0251; 0,1085] |

#### Bảng B — McNemar và Holm trên full test

Mỗi hàng ghép dự đoán theo cùng ID và dùng nhãn từ manifest. `b` đếm A đúng, B sai. `c` đếm A sai, B đúng. McNemar hai phía kiểm tra chênh lệch tỷ lệ lỗi tại ngưỡng của hàng đó. P_pre và P_post dùng hai ngưỡng riêng, được chọn trên validation OOF. Runner Step 6 tái tạo các ngưỡng và kết quả test đã lưu trước khi tính McNemar.

Holm được tính riêng cho từng phiên bản ngưỡng B0/B1, mỗi phiên bản gồm 11 cặp trên hai dataset (22 p-value). Ô phiên bản ngưỡng để trống khi cặp không có B0 hoặc B1. Các cặp này dùng chung dự đoán và p thô giữa hai lần đánh giá. Holm dùng toàn bộ 22 p thô trong mỗi phiên bản, nên p Holm của một cặp có thể đổi khi p thô của các cặp B0/B1 đổi. Với các hàng để trống phiên bản ngưỡng, bảng hiển thị một p Holm lấy từ lần đánh giá theo bộ ngưỡng hiệu chỉnh. CSV lưu giá trị của cả hai lần đánh giá. Phân tích PA1 đã tính cả B2/B3 và B1/B1-H2 trong họ 22 phép so. Các hàng thăm dò được trình bày ở mục 4.5. Các p Holm dưới đây lấy từ phép hiệu chỉnh PA1 đã lưu. Hai cặp dùng để đọc chênh lệch demo (B2−B1, B2-labelonly−B1) có p thô trong CSV.

| Dataset | A | B | Phiên bản ngưỡng B0/B1 | b | c | p thô | p Holm |
|---|---|---|---|---:|---:|---:|---|
| Devign | B0 | B2 | Gốc | 275 | 343 | 0,007036 | 0,06332 |
| Devign | B0 | B2 | Hiệu chỉnh hồi cứu | 621 | 511 | 0,001197 | 0,01316 |
| Devign | B0 | B1 | Gốc | 485 | 617 | < 10⁻⁴ | 0,0009528 |
| Devign | B0 | B1 | Hiệu chỉnh hồi cứu | 178 | 162 | 0,4159 | 1,000 |
| Devign | B1-shuf | B1 | Gốc | 318 | 280 | 0,1303 | 0,6513 |
| Devign | B1-shuf | B1 | Hiệu chỉnh hồi cứu | 204 | 196 | 0,7263 | 1,000 |
| Devign | B2-rand | B2 | | 542 | 499 | 0,1930 | 0,8045 |
| Devign | B1 | B2-nolabel | Gốc | 222 | 199 | 0,2836 | 0,6513 |
| Devign | B1 | B2-nolabel | Hiệu chỉnh hồi cứu | 264 | 211 | 0,01704 | 0,1193 |
| Devign | B2 | B2-flip | | 294 | 260 | 0,1609 | 0,8045 |
| Devign | B2-labelonly | B2 | | 645 | 542 | 0,003071 | 0,03071 |
| Devign | B2 | SUP-LR | | 482 | 674 | < 10⁻⁴ | < 10⁻⁴ |
| Devign | P_pre | P_post | | 24 | 24 | 0,8852 | 1,000 |
| ReVeal | B0 | B2 | Gốc | 524 | 90 | < 10⁻⁴ | < 10⁻⁴ |
| ReVeal | B0 | B2 | Hiệu chỉnh hồi cứu | 462 | 101 | < 10⁻⁴ | < 10⁻⁴ |
| ReVeal | B0 | B1 | Gốc | 86 | 269 | < 10⁻⁴ | < 10⁻⁴ |
| ReVeal | B0 | B1 | Hiệu chỉnh hồi cứu | 95 | 307 | < 10⁻⁴ | < 10⁻⁴ |
| ReVeal | B1-shuf | B1 | Gốc | 213 | 77 | < 10⁻⁴ | < 10⁻⁴ |
| ReVeal | B1-shuf | B1 | Hiệu chỉnh hồi cứu | 253 | 73 | < 10⁻⁴ | < 10⁻⁴ |
| ReVeal | B2-rand | B2 | | 737 | 98 | < 10⁻⁴ | < 10⁻⁴ |
| ReVeal | B1 | B2-nolabel | Gốc | 552 | 80 | < 10⁻⁴ | < 10⁻⁴ |
| ReVeal | B1 | B2-nolabel | Hiệu chỉnh hồi cứu | 504 | 76 | < 10⁻⁴ | < 10⁻⁴ |
| ReVeal | B2 | B2-flip | | 100 | 143 | 0,007054 | 0,06348 |
| ReVeal | B2-labelonly | B2 | | 335 | 70 | < 10⁻⁴ | < 10⁻⁴ |
| ReVeal | B2 | SUP-LR | | 192 | 927 | < 10⁻⁴ | < 10⁻⁴ |
| ReVeal | P_pre | P_post | | 13 | 43 | 0,0001065 | 0,001278 |

Trong toàn bộ họ 22 phép so của PA1, gồm các hàng thăm dò ở mục 4.5, có **13/22** phép so với ngưỡng gốc và **13/22** với ngưỡng hiệu chỉnh có p Holm dưới 0,05. Giá trị p đầy đủ và số lượt bootstrap suy biến có trong CSV kết quả.

#### Bảng C — Độ nhạy nhãn trên full test

Ghép B2, B2-flip và B2-rep seed 42 trên cùng ID. Tính lại nhãn dự đoán từ score theo quy tắc `s ≥ τ`, áp cùng ngưỡng cho cả ba arm ở mỗi hàng. Net là tỷ lệ dự đoán đổi từ B2 sang B2-flip trừ tỷ lệ đổi từ B2 sang B2-rep. Mỗi lượt bootstrap lấy cùng các cụm ID cho cả ba arm. Toàn bộ records B2-rep có cờ và tag repeat, với prompt hash khớp B2 theo từng ID. Kiểm tra `compare_records` cho thấy score trùng trên cả **5.006 ID** và không có dự đoán đổi tại ngưỡng khóa. B2-flip có **294** mẫu đổi đúng→sai và **260** đổi sai→đúng trên Devign, tương ứng **100** và **143** trên ReVeal. [Đầu ra B2-rep Devign](https://github.com/kazunguyen/GRACE-summary/blob/65fa20efe71e04f45396879eaeb256a5f29d8bac/Runs-management/analysis_checks_20261112/compare_records/b2_vs_b2rep_devign.json) · [B2-rep ReVeal](https://github.com/kazunguyen/GRACE-summary/blob/65fa20efe71e04f45396879eaeb256a5f29d8bac/Runs-management/analysis_checks_20261112/compare_records/b2_vs_b2rep_reveal.json) · [B2-flip Devign](https://github.com/kazunguyen/GRACE-summary/blob/65fa20efe71e04f45396879eaeb256a5f29d8bac/Runs-management/analysis_checks_20261112/compare_records/b2_vs_b2flip_devign.json) · [B2-flip ReVeal](https://github.com/kazunguyen/GRACE-summary/blob/65fa20efe71e04f45396879eaeb256a5f29d8bac/Runs-management/analysis_checks_20261112/compare_records/b2_vs_b2flip_reveal.json)

| Dataset | Cách đặt ngưỡng | Ngưỡng τ | ID ghép | Flip đổi, số ca (%) | Repeat đổi, số ca (%) | Net [CI 95%], điểm phần trăm |
|---|---|---:|---:|---:|---:|---:|
| Devign | B2 đã khóa | 0,70 | 2.732 | 554 (20,28%) | 0 (0,00%) | 20,28 [18,75; 21,76] |
| ReVeal | B2 đã khóa | 0,12 | 2.274 | 243 (10,69%) | 0 (0,00%) | 10,69 [9,15; 12,25] |
| Devign | 0,5 đối chiếu | 0,50 | 2.732 | 495 (18,12%) | 0 (0,00%) | 18,12 [16,66; 19,56] |
| ReVeal | 0,5 đối chiếu | 0,50 | 2.274 | 316 (13,90%) | 0 (0,00%) | 13,90 [12,10; 15,80] |

H2.1 được đánh giá ở ngưỡng B2 đã khóa. CI của Devign nằm trên mốc 15 điểm phần trăm và CI của ReVeal nằm dưới mốc này. Ở ngưỡng đối chiếu 0,5, CI của ReVeal chứa mốc 15. Trên tập đã loại trùng/gần trùng với train, net ở ngưỡng khóa lần lượt là 19,66 [18,12; 21,24] và 9,56 [8,04; 11,12] điểm phần trăm.

[CSV các phép so](../Runs-management/analysis_pa1_20261111/full_tables/contrasts.csv) ghi N, số cụm, CI, số lượt suy biến, hai ô bất đồng McNemar và p thô. Các cột Holm của họ 22 phép so dùng hậu tố `holm_available`. [CSV độ nhạy](../Runs-management/analysis_pa1_20261111/full_tables/sensitivity.csv) có thêm ngưỡng 0,5 và tập đã loại trùng/gần trùng với train (2.472 Devign, 1.978 ReVeal). Kết quả được tái tạo bằng [script](../Runs-management/analysis_pa1_20261111/recompute.py), dùng các hàm thống kê trong ZIP đi kèm đề cương 11/11. [Provenance và SHA-256 đầu vào](../Runs-management/analysis_pa1_20261111/full_tables/provenance.json).

Đây là phân tích trên test đã tiếp xúc. Các CI là CI riêng lẻ, có điều kiện trên records và ngưỡng đã dùng. B2-rand ReVeal seed 42 ghép 2.017 và 257 records từ hai lượt dùng hai khóa runtime. Seed 43 tương ứng có 2.028 và 246 records. Khóa mới bổ sung pin `scipy==1.16.3`. Log cài đặt và `pip freeze` xác nhận các lượt dùng khóa cũ đã chạy SciPy 1.16.3. Việc bổ sung pin giữ nguyên phiên bản SciPy đã dùng. Kết luận về biên lợi ích AUROC trên ReVeal vẫn giữ khi kiểm tra bằng seed 44, dùng cùng một khóa runtime trên toàn bộ test (mục 4.1). Với các nguồn thiếu hash runtime trong từng record, giữ trạng thái provenance của run trong hồ sơ nguồn. B3 và B1-H2 được báo riêng theo diện thăm dò của Phương án 1. [Log seed 42](../Runs-management/kaggle_outputs_20261107/b2_rand_seed42_test_latest/grace_diagnostics/install_dependencies.log) · [Log seed 43](../Runs-management/kaggle_outputs_20261107/b2_rand_seed43_test_latest/grace_diagnostics/install_dependencies.log) · [Khóa bổ sung pin SciPy](../Runs-management/kaggle_outputs_20261107/b2_rand_three_seed_test_tail_latest/inference_runtime_lock.json)

## 2. Trả lời sáu câu hỏi nghiên cứu tại mục 4

Các câu trả lời dưới đây dựa trên test đầy đủ của các arm, với seed 42 làm lượt so sánh chính; B2-rand và B1-shuf có thêm ba seed để mô tả độ biến thiên. CI ghép cặp đã tính được dùng paired cluster bootstrap 5.000 lượt, seed 20261117. Point estimate không được xem là bằng chứng tương đương nếu CI chưa thỏa biên δ.

| Câu hỏi trong đề cương | Trả lời theo số liệu | Kết luận và giới hạn |
|---|---|---|
| **RQ1 – Tái lập:** Với LLM open-weight và giao thức chuẩn, GRACE có vượt zero-shot và đối chứng hằng không, có đạt mức bài gốc không? | B2−B0 về AUROC: Devign −0,0100 [−0,0280; 0,0078], ReVeal −0,0079 [−0,0357; 0,0183]; cận trên cả hai dưới δ=0,02. Với ngưỡng gốc, ΔMCC là +0,0306 [−0,0080; 0,0681] và −0,0211 [−0,0634; 0,0207]; Devign chưa loại trừ lợi ích 0,03. Với ngưỡng hiệu chỉnh hồi cứu, ΔMCC lần lượt −0,0325 [−0,0750; 0,0106] và −0,0229 [−0,0630; 0,0153]. MCC B2 là 0,0597/0,0645; F1 Devign 0,5485 so với ALL-1 là 0,6295. | Trong backbone Qwen được đánh giá, AUROC không cho thấy B2 vượt B0 ở mức lợi ích δ; MCC phụ thuộc bộ ngưỡng. H1.2 đạt tiêu chí số học. Mức của bài gốc với backbone/model khác không được kiểm định bằng 15 arm này. |
| **RQ2 – Cơ chế demonstration:** Tác động qua nội dung mã demo hay nhãn đi kèm? | Net label sensitivity của B2-flip trừ B2-rep tại ngưỡng B2 là +20,28 điểm [18,75; 21,76] Devign và +10,69 [9,15; 12,25] ReVeal. ΔAUROC B2−B2-rand có CI [−0,0158; 0,0140] Devign và [−0,0352; 0,0064] ReVeal. ΔAUROC B2-nolabel−B1 có CI [−0,0183; 0,0052] và [−0,0288; 0,0049]. B2-labelonly AUROC 0,5462/0,6005; B2 là 0,5305/0,5662; B1 là 0,5335/0,5841. | Đảo nhãn ảnh hưởng rõ trên Devign và yếu hơn trên ReVeal. Các phép so demo ngẫu nhiên/bỏ nhãn loại trừ mức tăng AUROC 0,02 theo cận trên đã tính, nhưng label-only không tái tạo lợi thế B2−B1 dương (B2 vốn thấp hơn B1). Kết quả phù hợp với tác động lên operating point hơn lợi thế ranking ổn định, nhưng không chứng minh đó là cơ chế duy nhất. B2-rand ReVeal có hai runtime segment; xem giới hạn ở mục 1.6. |
| **RQ3 – Graph:** LLM có dùng thông tin graph dưới ngân sách context thực tế không? | AUROC B1−B0: Devign −0,0070 [−0,0197; 0,0057], ReVeal +0,0101 [−0,0092; 0,0287]. B1−B1-shuf seed42: Devign −0,0096 [−0,0233; 0,0041], ReVeal +0,0064 [−0,0161; 0,0296]. | Trên Devign, cả hai cận trên đều dưới 0,02. Trên ReVeal, cả hai CI vẫn cho phép mức tăng từ 0,02. Hai phép so này chưa cho thấy lợi ích nhất quán của graph đối với khả năng phân biệt. Kết quả B1-H2 theo nhóm có và thiếu evidence được trình bày ở mức thăm dò (mục 4.3 và 4.5). |
| **RQ4 – Phân biệt hay dịch chuyển điểm hoạt động:** Các biến thể prompt đổi AUROC/AUPRC hay tỷ lệ dự đoán 1? | Tại ngưỡng chung s ≥ 0,5, tỷ lệ dự đoán 1 từ B1 sang B2 tăng 46,6% → 65,1% trên Devign và 27,1% → 46,0% trên ReVeal. Từ B2-rand seed 42 sang B2, tỷ lệ tăng 50,5% → 65,1% và 31,7% → 46,0%. Phép so thăm dò B3−B2 cho −1,10/+17,02 điểm phần trăm (mục 4.2). | B2 dự đoán 1 thường xuyên hơn B1 và B2-rand ở ngưỡng chung. Các CI ΔAUROC tương ứng chứa 0 (mục 1.6 và 4.1). Với cấu hình B3 thăm dò trên ReVeal, tỷ lệ dự đoán 1 tăng và AUROC giảm. [Bảng ppr@0,5](https://github.com/kazunguyen/GRACE-summary/blob/65fa20efe71e04f45396879eaeb256a5f29d8bac/Runs-management/analysis_checks_20261112/supplementary_tables/ppr.csv) |
| **RQ5 – Mốc có giám sát:** Anchor tuyến tính/code metrics so với LLM ra sao, và LLM có thêm tín hiệu sau/trước truy vấn không? | SUP-LR−B2 ΔMCC +0,1593 [0,0952; 0,2267] Devign và +0,1939 [0,1136; 0,2714] ReVeal; AUROC SUP-LR 0,6559/0,7709. Tại ngưỡng chung, P_post−P_pre ΔMCC −0,0008 [−0,0095; 0,0080] và −0,0078 [−0,0169; −0,0010]. Routing q=10%: ΔBA Benefit−Random +0,0204 [0,0138; 0,0270] Devign và −0,0487 [−0,0748; −0,0249] ReVeal; repairs trên toàn test là 397/164, so với P97,5 random expert 465,05/176,15. | SUP-LR vượt B2 về MCC theo δ và CI ở cả hai; AUROC tuyệt đối đạt 0,68 chỉ trên ReVeal. H5.2 đạt trên cả hai dataset khi dùng ngưỡng chung (Bảng 1.5c). H5.3 đạt trên ReVeal và không đạt trên Devign. |
| **RQ6 – Truy hồi và lỗi:** Demo có liên quan cơ chế không, liên quan có kéo theo dự đoán đúng không, và bao nhiêu “lỗi” thực ra là nhãn nhiễu? | Chưa có bộ chấm mù 200 target, phân tích accuracy theo nhóm relevance, hay audit/adjudication 100 ca sai. | Chưa thể trả lời từ inference arm. Đây là một thí nghiệm riêng đã ghi trong đề cương. |

## 3. Đối chiếu giả thuyết đăng ký trước tại mục 4.3

| Giả thuyết | Tiêu chí đăng ký | Kết quả đầy đủ hiện có | Kết luận |
|---|---|---|---|
| **H1.1 – B2 không vượt B0** | Cận trên CI ΔMCC(B2−B0)<0,03 và ΔAUROC<0,02 trên cả hai dataset | AUROC cận trên 0,0078/0,0183. MCC ngưỡng gốc cận trên 0,0681/0,0207; ngưỡng hiệu chỉnh hồi cứu 0,0106/0,0153 (Devign/ReVeal). | **Một phần.** AUROC đạt cả hai; MCC đạt ReVeal nhưng không đạt Devign theo ngưỡng gốc. Không gộp kết quả hồi cứu với phân tích đăng ký. |
| **H1.2 – B2 yếu theo MCC/F1** | MCC B2<0,15 cả hai; F1 Devign thấp hơn ALL-1 | MCC 0,0597/0,0645; F1 Devign 0,5485<0,6295. | **Đạt.** |
| **H2.1 – Demo tác động qua nhãn** | Net label sensitivity ≥15 điểm | Devign 20,28 [18,75; 21,76]; ReVeal 10,69 [9,15; 12,25]. | **Một phần.** Đạt Devign, không đạt ReVeal. |
| **H2.2 – Nội dung demo không mang tín hiệu** | Cận trên CI AUROC(B2−B2-rand)<0,02; AUROC(B2-nolabel−B1)<0,02; B2-labelonly tái tạo ≥80% gap B2−B1 | Hai cận trên đầu là 0,0140/0,0064 và 0,0052/0,0049 (Devign/ReVeal). B2−B1 point gap −0,0030/−0,0179 nên không có lợi thế dương để label-only tái tạo. | **Một phần; giả thuyết gộp chưa đạt trọn vẹn.** Hai điều kiện CI đạt; điều kiện tái tạo 80% không được hỗ trợ. |
| **H2.3 – Cặp tương phản chỉ dịch chuyển điểm hoạt động** | Tỷ lệ dự đoán 1 của B3 cao hơn B2 ≥10 điểm phần trăm tại ngưỡng chung 0,5. Cận trên CI ΔAUROC(B3−B2)<0,02. | Các kết quả B3 hiện có thuộc phân tích thăm dò (mục 4.2 và 4.5). | **Chưa có kết luận xác nhận.** |
| **H3.1 – LLM không đọc graph** | Cận trên CI B1−B0 và B1−B1-shuffle <0,02. B1-H2 được xem xét thăm dò theo cùng biên và phân tầng evidence. | Hai so sánh chính có cận trên Devign 0,0057/0,0041 và ReVeal 0,0287/0,0296. | **Được hỗ trợ một phần.** Devign đạt hai điều kiện chính. ReVeal chưa loại trừ khác biệt ≥0,02. B1-H2 được báo theo nhóm evidence ở mức thăm dò (mục 4.5). |
| **H4.1 – Mọi arm LLM gần ngẫu nhiên theo AUROC** | AUROC mọi arm LLM ≤0,62 | AUROC cao nhất trong 15 arm là 0,6005 (B2-labelonly, ReVeal); nhóm B3 cao nhất 0,5644. | **Đạt** trên hai test census. |
| **H5.1 – Mốc có giám sát thắng rõ** | ΔMCC(SUP-LR−B2)≥0,15, CI không chứa 0; AUROC SUP-LR≥0,68 | Devign ΔMCC +0,1593 [0,0952; 0,2267], AUROC 0,6559. ReVeal +0,1939 [0,1136; 0,2714], AUROC 0,7709. | **Một phần.** MCC đạt ở cả hai; AUROC đạt ReVeal, không đạt Devign. |
| **H5.2 – LLM không thêm giá trị sau truy vấn** | Cận trên CI ΔMCC(P_post−P_pre)<0,02 khi dùng cùng ngưỡng | Ngưỡng chung lấy từ validation OOF của P_pre. Devign −0,0008 [−0,0095; 0,0080]. ReVeal −0,0078 [−0,0169; −0,0010]. | **Đạt trên cả hai dataset tại ngưỡng chung**. Trên ReVeal, CI nằm hoàn toàn dưới 0. Xem Bảng 1.5c. |
| **H5.3 – Không biết trước khi nào nên gọi LLM** | q=10%: cận trên CI Benefit−Confidence <0,02 cho BA và MCC; cận trên CI ΔBA Benefit−Random <0,01; repairs không vượt P97,5 expert random | Devign: CI ΔBA Benefit−Random [0,0138; 0,0270], repairs 397 < 465,05. ReVeal: CI [−0,0748; −0,0249], repairs 164 < 176,15. CI Benefit−Confidence ở mục 1.5. | **ReVeal đạt** các tiêu chí. **Devign không đạt** do cận trên của MCC Benefit−Confidence và BA Benefit−Random vượt biên tương ứng. |
| **H6.1 – Relevance demo và nhãn nhiễu** | “Neither”≥40% Devign; CI accuracy giữa nhóm demo liên quan/không liên quan chứa 0 | Chưa có nhãn chấm mù relevance và adjudication ca sai. | **Chưa adjudicate.** Cần hoàn tất chấm mù/audit; inference không cung cấp biến outcome này. |

### Kết luận tổng hợp

Đủ 15 arm inference cho phép tính và đối chiếu metric của arm, nhưng không tự hoàn tất các nghiên cứu Step 6/Step 8. Bằng chứng hiện tại cho thấy AUROC B2 không vượt B0 theo biên 0,02; MCC B2 thấp hơn 0,15 và F1 Devign thấp hơn ALL-1. Đảo nhãn tác động mạnh trên Devign nhưng dưới mốc đăng ký trên ReVeal. H2.3 chưa có kết luận xác nhận. Nhóm B3 và B1-H2 được trình bày ở mức thăm dò. SUP-LR vượt B2 về MCC trên cả hai dataset, AUROC đạt mốc 0,68 chỉ trên ReVeal. H5.2 đạt trên cả hai dataset tại ngưỡng chung. H5.3 đạt trên ReVeal và không đạt trên Devign. H4.1 đạt; H3.1 chỉ được hỗ trợ một phần; H6.1 chờ chấm mù/audit nhãn.

**Giới hạn và tính toàn vẹn:** Test đã được tiếp xúc trong quá trình nghiên cứu; các lần chạy lại không biến test này thành tập chưa từng xem. B0/B1 có thêm bộ ngưỡng hiệu chỉnh hồi cứu, được tách khỏi ngưỡng preregistered. B3/B3-swap/B3-flip là test seed42 đủ census; metric mới được tính bằng join với frozen labels tại local, không có nhãn gửi lên Kaggle. CI thăm dò B3−B2 dùng paired cluster bootstrap. Hiệu chỉnh Holm áp dụng cho p-value McNemar ở mục 1.6. Không suy diễn hoàn tất toàn bộ mục tiêu nghiên cứu chỉ từ việc 15 arm inference đã chạy xong.

## 4. Cập nhật câu trả lời theo đề cương Option 1 ngày 11/11/2026

Sáu câu hỏi RQ1–RQ6 và 11 giả thuyết giữ nguyên về nội dung. H2.2c là tiêu chí duy nhất được bổ sung trực tiếp trong Mục 4.3. Mục 6.6 bổ sung quy tắc so tỷ lệ đoán 1 tại cùng ngưỡng, cách báo hai bộ ngưỡng B0/B1 và yêu cầu phân tầng B1-H2 theo evidence. Phụ lục D chuyển nhóm B3, B1-H2 và chấm mù đầy đủ sang Giai đoạn 2. Các kết luận dưới đây áp dụng những điều chỉnh đó cho dữ liệu hiện có. [Đề cương Option 1 ngày 11/11](https://github.com/kazunguyen/GRACE-summary/blob/dung/docs/20261111/De_cuong_nghien_cuu_GRACE_hop_nhat.docx)

### 4.1. RQ2 và H2.2 — kiểm tra tương đương khi chênh lệch B2 − B1 chưa rõ

Bản cũ yêu cầu B2-labelonly tái tạo ít nhất 80% chênh lệch B2 − B1. Bản mới quy định nếu CI của ΔAUROC(B2 − B1) chứa 0, thay điều kiện đó bằng kiểm tra tương đương: cận trên CI của trị tuyệt đối ΔAUROC(B2-labelonly − B2) phải dưới 0,02. Báo thêm ΔAUROC(B2-labelonly − B1). Cả hai dataset đều thuộc trường hợp dùng tiêu chí thay thế.

| Dataset | ΔAUROC B2 − B1 [CI 95%] | Cận trên CI 95% của chênh lệch tuyệt đối giữa B2-labelonly và B2 | ΔAUROC B2-labelonly − B1 [CI 95%] | Kết luận H2.2c |
|---|---:|---:|---:|---|
| Devign | −0,0030 [−0,0186; 0,0122] | 0,0345 | +0,0128 [0,0050; 0,0204] | Chưa chứng minh tương đương trong biên 0,02 |
| ReVeal | −0,0179 [−0,0400; 0,0041] | 0,0588 | +0,0165 [0,0041; 0,0294] | Chưa chứng minh tương đương trong biên 0,02 |

**Câu trả lời cập nhật cho RQ2.** Hai điều kiện đầu của H2.2 vẫn đạt trên các đầu vào đã phân tích. Cận trên CI của B2 − B2-rand lần lượt là 0,0140 và 0,0064. Cận trên của B2-nolabel − B1 là 0,0052 và 0,0049. Điều kiện tương đương H2.2c chưa đạt trên cả hai dataset, nên H2.2 chỉ được hỗ trợ một phần. Trên ReVeal, label-only có AUROC cao hơn B2 với ΔAUROC +0,0344 [0,0103; 0,0588]. Phép so chính với B2-rand dùng seed 42 và có giới hạn runtime trên ReVeal như mục 1.6. Cận trên của chênh lệch tuyệt đối lấy từ phân vị 97,5% của trị tuyệt đối các chênh lệch trong 5.000 lượt bootstrap ghép cặp theo cụm. [CSV các phép so](../Runs-management/analysis_pa1_20261111/full_tables/contrasts.csv)

**Phân tích độ nhạy theo seed trên ReVeal.** B2-rand seed 44 dùng cùng một khóa runtime trên toàn bộ 2.274 mẫu test. So với B2, ΔAUROC(B2−B2-rand) là **−0,0087**, với CI 95% **[−0,0304; +0,0142]** từ 5.000 lượt bootstrap ghép cặp theo 646 cụm file. Cận trên vẫn dưới biên **+0,02**, nên kết luận về biên lợi ích AUROC giữ nguyên khi dùng seed 44. [Kết quả B2-rand seed 44](../06_Arm_B2_Rand/test_results_20261107/seed_44/reveal/test/evaluation.json)

### 4.2. RQ4 và H2.3 — so tỷ lệ đoán 1 ở cùng ngưỡng 0,5

Mốc tăng 10 điểm phần trăm và biên AUROC 0,02 của H2.3 giữ nguyên. Mục 6.6 yêu cầu tính tỷ lệ đoán 1 của cả B2 và B3 tại cùng ngưỡng 0,5. Bảng sau đếm trực tiếp các score test seed 42 thỏa `s ≥ 0,5` trên cùng danh sách ID.

| Dataset | B2 đoán 1 tại 0,5 | B3 đoán 1 tại 0,5 | B3 − B2 (điểm phần trăm) | ΔAUROC B3 − B2 [CI 95%] |
|---|---:|---:|---:|---:|
| Devign | 1.778/2.732 (65,08%) | 1.748/2.732 (63,98%) | −1,10 | +0,0047 [−0,0135; 0,0228] |
| ReVeal | 1.046/2.274 (46,00%) | 1.433/2.274 (63,02%) | +17,02 | −0,0369 [−0,0650; −0,0079] |

**Diễn giải thăm dò.** Trên Devign, chênh lệch tỷ lệ đoán 1 và cận trên CI ΔAUROC đều nằm ngoài các mốc của H2.3. Trên ReVeal, cấu hình B3 đã chạy làm tỷ lệ đoán 1 tăng tại ngưỡng 0,5, đồng thời AUROC thấp hơn B2. Theo đối chiếu ngày 12/11, mỗi dataset dùng một cặp demo cố định cho các target. Kết quả chỉ mô tả cấu hình đó. H2.3 về demo truy hồi theo từng target chưa có kết luận xác nhận.

### 4.3. RQ3 và H3.1 — giới hạn bằng chứng từ B1-H2

Tiêu chí H3.1 trong Mục 4.3 giữ nguyên. Option 1 yêu cầu đọc B1-H2 theo hai nhóm có và thiếu evidence, ở mức thăm dò. Hai phép so chính B1 − B0 và B1 − B1-shuf đều có cận trên CI ΔAUROC dưới 0,02 trên Devign (0,0057 và 0,0041), còn ReVeal có hai cận trên 0,0287 và 0,0296. Các hàng B1-H2 gộp toàn test ở mục 4.5 là số mô tả. Kết quả phân tầng B1-H2 được trình bày ở mục 4.5. Trên ReVeal, báo cáo dùng ngưỡng 0,21 từ khóa validation Kaggle. Ngưỡng 0,67 thuộc lượt validation Colab I-13.

**B1-full.** Lần sửa trình dựng prompt thay đổi **4.753/5.006 prompt giữa hai bản test**. Audit tái tạo đúng phần graph của **5.005/5.005 prompt validation**, kể cả khung graph rỗng. Lượt test hiện tại chạy đủ **5.006 mẫu** trên bộ prompt test đã sửa và dùng ngưỡng validation đã khóa (Devign 0,99, ReVeal 0,01). Không cần chạy lại validation vì lý do renderer. [Audit dựng prompt](../Runs-management/locked_continuations_20261108/b1_full_corrected_v4/audit.json) · [Nhật ký sửa test](2026-11-08_locked_kaggle_continuations.md) · [Nghiệm thu B1-full](../Runs-management/run_handoff_20261108/B1_FULL_RUNTIME_ACCEPTANCE.md)

### 4.4. RQ1 và H1.1 — đọc riêng hai bộ ngưỡng B0/B1

Option 1 yêu cầu báo cả ngưỡng gốc và ngưỡng hiệu chỉnh hồi cứu. Tiêu chí H1.1 giữ nguyên. Theo bộ gốc, cận trên CI ΔMCC(B2 − B0) trên Devign là 0,0681, vượt biên 0,03. Với bộ ngưỡng đúng theo quy tắc validation, cận trên ΔMCC trên Devign và ReVeal lần lượt là 0,0106 và 0,0153, đều dưới 0,03. Hai cận trên ΔAUROC là 0,0078 và 0,0183, đều dưới 0,02. Như vậy, **H1.1 đạt cả hai biên trên hai dataset trong phân tích hồi cứu**. Kết quả theo bộ gốc được giữ để đối chiếu lịch sử như chú thích mục 1.6.

RQ5 giữ nguyên tiêu chí trong Mục 4.3. Kết quả H5.2 tại ngưỡng chung nằm ở Bảng 1.5c. RQ6/H6.1 cũng giữ nguyên, với phần chấm mù đầy đủ chuyển sang Giai đoạn 2. Trạng thái kết luận RQ6/H6.1 vẫn là chờ dữ liệu chấm mù và kiểm toán nhãn.

### 4.5. Kết quả thăm dò của nhóm B3 và B1-H2

Các bảng dưới đây giữ metric đã báo cáo cho nhóm B3 và B1-H2. Tỷ lệ dự đoán 1 trong bảng metric là tỷ lệ tại ngưỡng riêng của từng arm. So sánh tỷ lệ giữa B3 và B2 tại ngưỡng chung nằm ở mục 4.2. Bảng metric trình bày B1-H2 gộp toàn test. Bảng dưới đây so B1-H2 với B1 theo cờ `h2_evidence` trên cùng danh sách ID. Các CI là kết quả thăm dò.

| Dataset | Nhóm | N | ΔAUROC(B1-H2−B1) [CI 95%] |
|---|---|---:|---:|
| Devign | Có evidence | 934 | +0,031 [−0,004; +0,065] |
| Devign | Thiếu evidence | 1.798 | +0,002 [−0,014; +0,019] |
| ReVeal | Có evidence | 408 | +0,061 [−0,008; +0,127] |
| ReVeal | Thiếu evidence | 1.866 | +0,002 [−0,020; +0,024] |

Ước lượng điểm cao hơn trong nhóm có evidence, với CI chứa 0 trên cả hai dataset. [Bảng phân tầng B1-H2](https://github.com/kazunguyen/GRACE-summary/blob/65fa20efe71e04f45396879eaeb256a5f29d8bac/Runs-management/analysis_checks_20261112/supplementary_tables/b1h2_evidence_strata.csv)

**Metric test theo arm và dataset**

| Dataset | Arm | N | Raw lỗi | MCC | AUROC | AUPRC (AP) | F1 | Balanced accuracy | Precision | Recall | Tỷ lệ dự đoán 1 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Devign | B1-H2 | 2.732 | 150 | 0,0655 | 0,5477 | 0,5165 | 0,5454 | 0,5324 | 0,4869 | 0,6199 | 0,5849 |
| ReVeal | B1-H2 | 2.274 | 156 | 0,1093 | 0,5956 | 0,1348 | 0,2263 | 0,5876 | 0,1439 | 0,5304 | 0,3729 |
| Devign | B3-nodiff | 2.732 | 1 | 0,0530 | 0,5359 | 0,5007 | 0,5229 | 0,5265 | 0,4837 | 0,5689 | 0,5403 |
| ReVeal | B3-nodiff | 2.274 | 0 | 0,0603 | 0,5572 | 0,1189 | 0,1982 | 0,5480 | 0,1148 | 0,7261 | 0,6398 |
| Devign | B3 | 2.732 | 0 | 0,0735 | 0,5351 | 0,5024 | 0,4576 | 0,5358 | 0,5063 | 0,4175 | 0,3788 |
| ReVeal | B3 | 2.274 | 0 | 0,0400 | 0,5292 | 0,1130 | 0,1897 | 0,5231 | 0,1060 | 0,9000 | 0,8584 |
| Devign | B3-swap | 2.732 | 0 | 0,0728 | 0,5328 | 0,5048 | 0,4469 | 0,5351 | 0,5076 | 0,3992 | 0,3613 |
| ReVeal | B3-swap | 2.274 | 0 | 0,0752 | 0,5613 | 0,1208 | 0,2029 | 0,5576 | 0,1163 | 0,7957 | 0,6922 |
| Devign | B3-flip | 2.732 | 0 | 0,0880 | 0,5389 | 0,5095 | 0,4284 | 0,5411 | 0,5236 | 0,3625 | 0,3181 |
| ReVeal | B3-flip | 2.274 | 0 | 0,0767 | 0,5644 | 0,1224 | 0,2036 | 0,5591 | 0,1168 | 0,7913 | 0,6851 |

So với B2, B3 có ΔAUPRC +0,0168 trên Devign và −0,0091 trên ReVeal. B3-nodiff−B2 có ΔAUROC +0,0054/−0,0090 và ΔAUPRC +0,0151/−0,0032. B3-swap−B3 có ΔAUROC −0,0023/+0,0321 và B3-flip−B3 có ΔAUROC +0,0038/+0,0352 (Devign/ReVeal). Đây là các ước lượng điểm.

**Chênh lệch ghép cặp và CI 95%**

| Phép so | Dataset | ΔAUROC [CI 95%] | ΔMCC [CI 95%] theo ngưỡng gốc hoặc ngưỡng arm | ΔMCC [CI 95%] sau hiệu chỉnh B0/B1 |
|---|---|---:|---:|---:|
| B3 − B2 | Devign | 0,0047 [−0,0135; 0,0228] | 0,0138 [−0,0259; 0,0534] | |
| B3 − B2 | ReVeal | −0,0369 [−0,0650; −0,0079] | −0,0245 [−0,0767; 0,0293] | |
| B1-H2 − B1 | Devign | 0,0142 [−0,0012; 0,0301] | 0,0014 [−0,0376; 0,0416] | −0,0133 [−0,0553; 0,0295] |
| B1-H2 − B1 | ReVeal | 0,0115 [−0,0105; 0,0342] | 0,0561 [0,0128; 0,0994] | 0,0569 [0,0158; 0,0990] |

**McNemar và Holm từ phân tích PA1**

| Dataset | A | B | Phiên bản ngưỡng B0/B1 | b | c | p thô | p Holm |
|---|---|---|---|---:|---:|---:|---|
| Devign | B2 | B3 | | 369 | 436 | 0,02001 | 0,1200 |
| Devign | B1 | B1-H2 | Gốc | 451 | 399 | 0,08024 | 0,4815 |
| Devign | B1 | B1-H2 | Hiệu chỉnh hồi cứu | 580 | 498 | 0,01362 | 0,1090 |
| ReVeal | B2 | B3 | | 638 | 74 | < 10⁻⁴ | < 10⁻⁴ |
| ReVeal | B1 | B1-H2 | Gốc | 357 | 110 | < 10⁻⁴ | < 10⁻⁴ |
| ReVeal | B1 | B1-H2 | Hiệu chỉnh hồi cứu | 324 | 121 | < 10⁻⁴ | < 10⁻⁴ |

Các p Holm lấy từ họ 22 phép so đã tính trong PA1 cho từng bộ ngưỡng. Việc chuyển vị trí các hàng giữ nguyên các giá trị đó.

### 4.6. Phân tích bổ sung và đối soát số liệu

- **ΔAUPRC.** Trên Devign, B2−B0 = −0,0297 [−0,0489; −0,0101], B2−B2-labelonly = −0,0276 [−0,0466; −0,0078] và B2−B1 = −0,0167 [−0,0328; −0,0006]. Trên ReVeal, B2-flip−B2 = −0,0170 [−0,0294; −0,0061]. Các CI này thuộc phân tích bổ sung, chưa có biên AUPRC đăng ký. [Bảng CI ΔAUPRC](https://github.com/kazunguyen/GRACE-summary/blob/65fa20efe71e04f45396879eaeb256a5f29d8bac/Runs-management/analysis_checks_20261112/supplementary_tables/auprc_contrasts.csv)
- **B2−B2-nolabel.** Trên toàn bộ test, ΔAUROC là +0,0036 [−0,0081; +0,0154] trên Devign và −0,0059 [−0,0234; +0,0117] trên ReVeal. Trên tập ReVeal đã loại trùng và gần trùng với train, ΔAUROC là −0,0255 [−0,0492; −0,0008]. [Bảng so B2 với B2-nolabel](https://github.com/kazunguyen/GRACE-summary/blob/65fa20efe71e04f45396879eaeb256a5f29d8bac/Runs-management/analysis_checks_20261112/supplementary_tables/b2_vs_b2nolabel.csv)
- **Đối soát số cũ.** MCC B2 Devign **0,0441 → 0,0597** do chuyển từ ngưỡng 0,5 sang ngưỡng khóa 0,70. AUROC B2 Devign **0,5292 → 0,5305** do dùng records sau khi cập nhật donor cho 38 prompt test. Số **1.132** phản hồi thô sai định dạng của B0 là tổng bốn split, còn **302** thuộc riêng Devign test. Inventory có 38 file test. 36 file có dòng trong bảng 1.3 của bản dùng để đối soát đều khớp về N, số raw lỗi, AUROC và AUPRC. Hai file còn lại là B2-rand seed 44. [Bảng đối soát số liệu](https://github.com/kazunguyen/GRACE-summary/blob/65fa20efe71e04f45396879eaeb256a5f29d8bac/Runs-management/analysis_checks_20261112/reconciliation/REPORT.md)

## Nguồn và khả năng truy xuất

- [Đề cương nghiên cứu, mục 4 và 4.3](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/docs/OSF_response/De_cuong_nghien_cuu_GRACE_hop_nhat.docx)
- [Workbook metric và paired deltas](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/outputs/metrics_completed_arms_20261107/GRACE_completed_arms_metrics.xlsx)
- [Ledger các lượt inference](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/Runs-management/RUNS.md)
- [Khóa threshold validation B1-H2 trên Kaggle](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/Runs-management/b1h2_kaggle_validation_threshold_lock_20261106.json)
- [Báo cáo hoàn tất B1-H2 test và trạng thái B2-rand](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/worklogs/2026-11-07_b1h2_b2rand_kaggle_progress_and_delivery.md)
- [Worklog hoàn tất test B2-rand seed 42/43](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/worklogs/2026-11-07_b2_rand_seed42_seed43_test_complete.md)
- [B2-rand seed44 merged evaluation](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/06_Arm_B2_Rand/test_results_20261107/seed_44/evaluation_summary.json)
- [Hồ sơ nghiệm thu và metric test B2-rep/B2-nolabel/B2-labelonly](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/Runs-management/run_handoff_20261108/RUN_STATUS.md)
- [B1-full runtime acceptance và full test metrics](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/Runs-management/run_handoff_20261108/B1_FULL_RUNTIME_ACCEPTANCE.md)
- [B1-full completion worklog](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/worklogs/2026-11-08_b1_full_completion_runtime_acceptance.md)
- [Worklog tiếp tục và nghiệm thu B1-shuf](https://github.com/kazunguyen/GRACE-summary/blob/dung/worklogs/2026-11-08_b1_shuf_checkpoint_resume.md)
- [B3-nodiff test completion worklog](https://github.com/kazunguyen/GRACE-summary/blob/dung/worklogs/2026-11-09_b3_nodiff_test_kaggle_delivery.md)
- [B3 verified-patch-v1 test completion worklog](https://github.com/kazunguyen/GRACE-summary/blob/dung/worklogs/2026-11-11_b3_verified_patch_test_completed.md) · [B3 Devign test records](https://github.com/kazunguyen/GRACE-summary/blob/dung/Runs-management/kaggle_outputs_20261111/b3_verified_patch_test_10h/b3_test_release_20261110/seed_42/devign/test/records.jsonl) · [B3 ReVeal test records](https://github.com/kazunguyen/GRACE-summary/blob/dung/Runs-management/kaggle_outputs_20261111/b3_verified_patch_test_10h/b3_test_release_20261110/seed_42/reveal/test/records.jsonl)
- [B3-swap completion evidence in RUNS.md](https://github.com/kazunguyen/GRACE-summary/blob/dung/Runs-management/RUNS.md#i-30) · [B3-swap test records](https://github.com/kazunguyen/GRACE-summary/blob/dung/Runs-management/kaggle_outputs_20261111/b3_swap_test_resume_latest/b3_swap_test_release_20261110/seed_42/devign/test/records.jsonl)
- [B3-flip test completion worklog](https://github.com/kazunguyen/GRACE-summary/blob/dung/worklogs/2026-11-11_b3_flip_test_completed.md) · [B3-flip Devign test records](https://github.com/kazunguyen/GRACE-summary/blob/dung/Runs-management/kaggle_outputs_20261111/b3_flip_test_20261110_v1/b3_flip_test_release_20261110/seed_42/devign/test/records.jsonl) · [B3-flip ReVeal test records](https://github.com/kazunguyen/GRACE-summary/blob/dung/Runs-management/kaggle_outputs_20261111/b3_flip_test_20261110_v1/b3_flip_test_release_20261110/seed_42/reveal/test/records.jsonl)
- [RUNS.md — lượt I-20 và tình trạng đủ 5.006 test record mỗi seed](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/Runs-management/RUNS.md)
- [B2-rand merged evaluation summary](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/06_Arm_B2_Rand/test_results_20261107/evaluation_summary.json) · [Provenance và runtime hashes](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/06_Arm_B2_Rand/test_results_20261107/provenance.json)
- [Step 6 lock](https://github.com/kazunguyen/GRACE-summary/blob/dung/STEP6_supervised_anchors/step6_lock.json) · [Worklog Step 6, gồm protocol, hash và trạng thái đầu ra](https://github.com/kazunguyen/GRACE-summary/blob/dung/worklogs/2026-11-08_step6_supervised_anchors_start.md) · [Mã phân tích complementarity](https://github.com/kazunguyen/GRACE-summary/blob/dung/STEP6_supervised_anchors/src/step6_complementarity.py)
- [B2-rand test records — seed 42 Devign](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/06_Arm_B2_Rand/test_results_20261107/seed_42/devign/test/records.jsonl) · [seed 42 ReVeal](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/06_Arm_B2_Rand/test_results_20261107/seed_42/reveal/test/records.jsonl)
- [B2-rand test records — seed 43 Devign](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/06_Arm_B2_Rand/test_results_20261107/seed_43/devign/test/records.jsonl) · [seed 43 ReVeal](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/06_Arm_B2_Rand/test_results_20261107/seed_43/reveal/test/records.jsonl)
- B3-nodiff runtime-locked test outputs remain in local ignored run storage; the completion summary and test protocol are documented in the [B3-nodiff worklog](https://github.com/kazunguyen/GRACE-summary/blob/dung/worklogs/2026-11-09_b3_nodiff_test_kaggle_delivery.md).
- [Lịch sử thay đổi sau đăng ký](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/CHANGES_AFTER_PREREG.md)
