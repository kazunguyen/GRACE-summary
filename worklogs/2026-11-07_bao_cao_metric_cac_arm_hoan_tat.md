# Báo cáo kết quả các arm GRACE đã hoàn tất — cập nhật 11/11/2026

**Bản gửi thầy:** 08/11/2026<br>
**Bản cập nhật:** 11/11/2026 — bổ sung kết quả Step 6 và phân tích ghép cặp cho Phương án 1<br>
**Phạm vi:** Báo cáo metric test cho 15 arm chẩn đoán (B0, B1, B1-full, B1-H2, B1-shuf, B2, B2-rand, B2-nolabel, B2-labelonly, B2-flip, B2-rep, B3, B3-nodiff, B3-swap, B3-flip) và Step 6 (SUP-LR/SUP-MLP/SUP-METRIC, P_pre/P_post, sửa–hỏng, routing). Các kết quả B3/B3-swap/B3-flip mới bổ sung dùng seed 42, đủ 5.006 test record và ngưỡng B3 kế thừa từ validation: Devign 0,99; ReVeal 0,01. B0/B1 chính dùng ngưỡng hiệu chỉnh hồi cứu; báo cáo giữ riêng điều này và không gọi các phép hiệu chỉnh đó là preregistered.

**Bổ sung sau bản gửi ngày 08/11.** Bản đó chưa trình bày các mốc SUP-LR/SUP-MLP/SUP-METRIC và cặp P_pre/P_post. Bản hiện tại đã có kết quả ba anchor trên Devign và ReVeal ở mục 1.4, kết quả P_pre/P_post kèm CI và đối chiếu routing ở mục 1.5. Yêu cầu bổ sung các bảng này đã được xử lý. Phần cần rà tiếp là cách gom cụm ReVeal trong Step 6, nêu ở mục 1.5.

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
| B1-H2 | ReVeal | 0,21 | Khóa riêng từ validation |
| B3-nodiff | Devign | 0,92 | Khóa riêng trên validation B3-nodiff; giữ nguyên khi đánh giá test |
| B3-nodiff | ReVeal | 0,01 | Khóa riêng trên validation B3-nodiff; giữ nguyên khi đánh giá test |
| B3 (verified-patch-v1) | Devign | 0,99 | Khóa validation của B3; không fit lại trên test |
| B3 (verified-patch-v1) | ReVeal | 0,01 | Khóa validation của B3; không fit lại trên test |
| B3-swap | Devign | 0,99 | Kế thừa ngưỡng B3; không fit riêng cho probe |
| B3-swap | ReVeal | 0,01 | Kế thừa ngưỡng B3; không fit riêng cho probe |
| B3-flip | Devign | 0,99 | Kế thừa ngưỡng B3; không fit riêng cho probe |
| B3-flip | ReVeal | 0,01 | Kế thừa ngưỡng B3; không fit riêng cho probe |


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

| Dataset | Arm | N | Raw lỗi | MCC | AUROC | AUPRC (AP) | F1 | Balanced accuracy | Precision | Recall | Tỷ lệ dự đoán 1 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Devign | B0 | 2.732 | 302 | 0,0922 | 0,5405 | 0,5153 | 0,3343 | 0,5370 | 0,5513 | 0,2398 | 0,1999 |
| Devign | B1 | 2.732 | 0 | 0,0788 | 0,5335 | 0,5023 | 0,3457 | 0,5328 | 0,5332 | 0,2558 | 0,2204 |
| Devign | B2 | 2.732 | 0 | 0,0597 | 0,5305 | 0,4856 | 0,5485 | 0,5293 | 0,4836 | 0,6335 | 0,6018 |
| Devign | B2-flip | 2.732 | 0 | 0,0337 | 0,5240 | 0,4857 | 0,5355 | 0,5166 | 0,4731 | 0,6167 | 0,5988 |
| Devign | B1-H2 | 2.732 | 150 | 0,0655 | 0,5477 | 0,5165 | 0,5454 | 0,5324 | 0,4869 | 0,6199 | 0,5849 |
| ReVeal | B0 | 2.274 | 285 | 0,0874 | 0,5740 | 0,1260 | 0,2129 | 0,5700 | 0,1356 | 0,4957 | 0,3698 |
| ReVeal | B1 | 2.274 | 2 | 0,0523 | 0,5841 | 0,1238 | 0,1816 | 0,5370 | 0,1294 | 0,3043 | 0,2379 |
| ReVeal | B2 | 2.274 | 0 | 0,0645 | 0,5662 | 0,1221 | 0,2005 | 0,5531 | 0,1183 | 0,6565 | 0,5611 |
| ReVeal | B2-flip | 2.274 | 0 | 0,0372 | 0,5261 | 0,1051 | 0,1875 | 0,5308 | 0,1118 | 0,5826 | 0,5273 |
| ReVeal | B1-H2 | 2.274 | 156 | 0,1093 | 0,5956 | 0,1348 | 0,2263 | 0,5876 | 0,1439 | 0,5304 | 0,3729 |
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
| Devign | B3-nodiff | 2.732 | 1 | 0,0530 | 0,5359 | 0,5007 | 0,5229 | 0,5265 | 0,4837 | 0,5689 | 0,5403 |
| ReVeal | B3-nodiff | 2.274 | 0 | 0,0603 | 0,5572 | 0,1189 | 0,1982 | 0,5480 | 0,1148 | 0,7261 | 0,6398 |
| Devign | B3 (verified-patch-v1) | 2.732 | 0 | 0,0735 | 0,5351 | 0,5024 | 0,4576 | 0,5358 | 0,5063 | 0,4175 | 0,3788 |
| ReVeal | B3 (verified-patch-v1) | 2.274 | 0 | 0,0400 | 0,5292 | 0,1130 | 0,1897 | 0,5231 | 0,1060 | 0,9000 | 0,8584 |
| Devign | B3-swap | 2.732 | 0 | 0,0728 | 0,5328 | 0,5048 | 0,4469 | 0,5351 | 0,5076 | 0,3992 | 0,3613 |
| ReVeal | B3-swap | 2.274 | 0 | 0,0752 | 0,5613 | 0,1208 | 0,2029 | 0,5576 | 0,1163 | 0,7957 | 0,6922 |
| Devign | B3-flip | 2.732 | 0 | 0,0880 | 0,5389 | 0,5095 | 0,4284 | 0,5411 | 0,5236 | 0,3625 | 0,3181 |
| ReVeal | B3-flip | 2.274 | 0 | 0,0767 | 0,5644 | 0,1224 | 0,2036 | 0,5591 | 0,1168 | 0,7913 | 0,6851 |

**Ma trận nhầm lẫn mới tính tại ngưỡng validation (TN, FP, FN, TP):** B3 Devign `966, 511, 731, 524`; B3 ReVeal `299, 1.745, 23, 207`; B3-swap Devign `991, 486, 754, 501`; B3-swap ReVeal `653, 1.391, 47, 183`; B3-flip Devign `1.063, 414, 800, 455`; B3-flip ReVeal `668, 1.376, 48, 182`.

**Kiểm tra B3/B3-swap/B3-flip:** Join theo ID với frozen test manifest đạt census đầy đủ, không trùng ID, nhãn khớp; mọi score hữu hạn trong [0,1]. Metrics tính bằng score `s` cho AUROC/AP và quyết định `s ≥ τ` cho metric phân loại; τ là 0,99/0,01 theo khóa validation B3. Probe kế thừa nguyên ngưỡng. Không có raw response lỗi trong ba run mới. Test labels không có trong Kaggle output; chúng được ghép cục bộ sau khi tải output. B3-nodiff giữ ngưỡng riêng 0,92/0,01 và có 1 raw response lỗi ở Devign nhưng score vẫn hợp lệ.
| Devign | B2-rand s44 | 2.732 | 0 | 0,0589 | 0,5327 | 0,5006 | 0,3295 | 0,5243 | 0,5153 | 0,2422 | 0,2160 |
| ReVeal | B2-rand s44 | 2.274 | 0 | 0,0665 | 0,5748 | 0,1235 | 0,1959 | 0,5495 | 0,1332 | 0,3696 | 0,2806 |

**Ghi chú metric/provenance B3-nodiff:** metric @τ được đối soát trực tiếp từ 5.006 record tại τ=0,92/0,01 và khớp MCC/BA/F1/tỷ lệ dự đoán 1 trong shared evaluator. Các cột confusion trong `table_A_metrics.csv` của evaluator là tại 0,5, không phải tại τ; confusion tính lại tại τ: Devign `TP=714, FP=762, TN=715, FN=541`; ReVeal `TP=167, FP=1.288, TN=756, FN=63`. Devign có một raw response lỗi nhưng score vẫn hợp lệ; cả 5.006 score hữu hạn. Threshold được khóa trên validation và không đổi sau khi xem test. Runtime SHA của nguồn seal validation và runtime test khác nhau do test lock bổ sung pin SciPy; audit ghi core inference settings khớp, nhưng hai SHA không được coi là cùng một lock.

Metric từng mẫu, ma trận nhầm lẫn, kiểm tra ID/nhãn, nguồn record và các chênh lệch ghép cặp của các arm đã tích hợp trước đó được lưu trong [workbook metric](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/outputs/metrics_completed_arms_20261107/GRACE_completed_arms_metrics.xlsx). B3-nodiff/B3/B3-swap/B3-flip mới tính trong báo cáo chưa nhập vào workbook. Các metric B3 ở đây là kết quả mô tả. Phạm vi Holm của các cặp Phương án 1 được ghi ở mục 1.6.

B1-shuf được tính từ toàn bộ sáu nhóm records đã tải (15.018/15.018); ID/nhãn khớp frozen test manifest và `pred_tau` khớp quy tắc `s ≥ τ`. Mỗi seed ReVeal có hai raw response không hợp lệ nhưng score số vẫn hợp lệ và được giữ trong metric. Đây là descriptive point estimate; chưa thay thế kiểm định ghép cặp. Xem [worklog nghiệm thu B1-shuf](https://github.com/kazunguyen/GRACE-summary/blob/dung/worklogs/2026-11-08_b1_shuf_checkpoint_resume.md).

### 1.4. Các mốc phân loại có giám sát (Step 6)

Ba anchor được fit trên train; τ chọn theo MCC validation, không dùng nhãn test để chọn. SUP-LR/SUP-MLP dùng embedding CodeT5 đóng băng 768 chiều; SUP-METRIC dùng 26 code metrics. Bảng đầu ghi ngưỡng và metric validation trong summary đã khóa; bảng sau báo test theo đúng các ngưỡng đó. Metric test được tính lại bằng cách ghép `anchor_scores.csv` theo ID với nhãn trong frozen `test_raw.jsonl`; đối chiếu SUP-LR seed 42 khớp `test_baseline` trong output Step 6. SUP-LR và SUP-METRIC cho kết quả giống hệt giữa ba seed; không xem ba bản sao này là ba quan sát độc lập.

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

Hai meta-model logistic dùng cùng 34 đặc trưng nền, cùng 3 fold StratifiedGroupKFold, cùng scaler và fallback đối xứng khi expert invalid. Ngưỡng của từng model được chọn từ validation OOF. CI dùng paired cluster bootstrap 5.000 lượt. Các kết quả P_pre/P_post trong lần chạy Step 6 bổ sung routing khớp với lần chạy trước trên cả hai dataset.

**Đơn vị cụm của Step 6.** Devign dùng 2.068 cụm `commit_id` trên test. Với ReVeal, dữ liệu nguồn thiếu trường `file_hash` nên Step 6 rơi về `code_sha256` của từng hàm. Kết quả là 2.269 cụm trên 2.273 mẫu validation và 2.272 cụm trên 2.274 mẫu test. Ánh xạ file theo `source_id` cho 627 cụm validation và 646 cụm test. Con số 646 khớp giao thức và cách gom cụm của Bảng B. Khi tái lập cách chia 3 fold của Step 6 với seed 42, 340 nhóm file xuất hiện ở nhiều fold nếu chia theo hash hàm, gồm 1.927 mẫu thuộc các nhóm này. Chia theo `source_id` giữ mỗi nhóm file trong một fold. Với P_pre/P_post, khác biệt này ảnh hưởng cả fold validation OOF lẫn CI trên test. Với routing, nó ảnh hưởng CI trên test. Các kết quả ReVeal ở mục 1.5 là kết quả theo lần chạy Step 6 hiện có và cần đối soát lại theo cụm file trước khi chốt kết luận xác nhận.

| Dataset | Model | τ OOF | MCC test | AUROC test | AP test | BA test | F1 test | Precision | Recall | Tỷ lệ dự đoán 1 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Devign | P_pre | 0,53 | 0,2866 | 0,7136 | 0,6787 | 0,6307 | 0,5300 | 0,6817 | 0,4335 | 0,2921 |
| Devign | P_post | 0,52 | 0,2851 | 0,7120 | 0,6780 | 0,6321 | 0,5398 | 0,6722 | 0,4510 | 0,3082 |
| ReVeal | P_pre | 0,25 | 0,3769 | 0,8094 | 0,3491 | 0,6995 | 0,4431 | 0,4160 | 0,4739 | 0,1152 |
| ReVeal | P_post | 0,30 | 0,3527 | 0,8089 | 0,3512 | 0,6718 | 0,4161 | 0,4286 | 0,4043 | 0,0954 |

| Dataset | ΔMCC (P_post − P_pre) | CI 95% | ΔAUROC | CI 95% | Kết luận theo δ MCC=0,02 |
|---|---:|---:|---:|---:|---|
| Devign | −0,0015 | [−0,0122; 0,0093] | −0,0016 | [−0,0041; 0,0009] | Cận trên < 0,02: loại trừ mức tăng MCC có ý nghĩa đã định trước |
| ReVeal | −0,0242 | [−0,0550; 0,0047] | −0,0004 | [−0,0017; 0,0008] | Cận trên < 0,02: loại trừ mức tăng MCC có ý nghĩa đã định trước |

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
| ReVeal | −0,0644 [−0,0953; −0,0360] | −0,0509 [−0,1049; −0,0002] | −0,0487 [−0,0707; −0,0285] | 164 / 176,15 | Đạt các điều kiện theo cách gom cụm hiện tại. Cần đối soát theo cụm file |

Tiêu chí gồm cận trên CI Benefit−Confidence dưới 0,02 cho BA và MCC, cận trên CI BA Benefit−Random dưới 0,01, và số ca B2 sửa đúng không vượt phân vị 97,5% của expert ngẫu nhiên có cùng tỷ lệ dự đoán dương. Cột số ca sửa dùng toàn bộ test cho cả B2 và random expert. Bảng ngân sách phía trên ghi riêng 55/68 ca sửa của benefit router khi chỉ gọi B2 trên khoảng 10% test.

Nguồn là [manifest lần chạy Step 6 bổ sung](../STEP6_supervised_anchors/runs/complementarity_step6/step6_lock_64fb2c99d904_b5d441d3/analysis_manifest.json) và kết quả theo dataset [Devign](../STEP6_supervised_anchors/runs/complementarity_step6/step6_lock_64fb2c99d904_b5d441d3/devign/complementarity_step6.json), [ReVeal](../STEP6_supervised_anchors/runs/complementarity_step6/step6_lock_64fb2c99d904_b5d441d3/reveal/complementarity_step6.json).

### 1.6. CI ghép cặp, McNemar và độ nhạy nhãn cho Phương án 1

**Bổ sung ngày 11/11/2026.** Phân tích lại records test hiện có, seed arm chính 42. Kiểm tra đủ ID duy nhất, nhãn khớp manifest và điểm hợp lệ chung cho toàn bộ các cặp. Devign có 2.732 ID và 2.068 cụm theo `commit_id` (ID thiếu commit được giữ thành cụm riêng). ReVeal có 2.274 ID và 646 cụm theo `source_id` ánh xạ tới nhóm file của bảng canonical. CI percentile 95% dùng paired cluster bootstrap 5.000 lượt, seed 20261117, giữ ngưỡng cố định trong bootstrap. Không có lượt bootstrap suy biến trong các hàng đã tính.

Ngưỡng B0/B1 gốc lấy từ `prereg-v1:configs/thresholds.json`: Devign 0,08/0,88 và ReVeal 0,44/0,74. Cột hiệu chỉnh dùng ngưỡng full validation tính hồi cứu: Devign 0,98/0,98 và ReVeal 0,30/0,63. Các arm còn lại dùng ngưỡng validation có sẵn; AUROC dùng score và không phụ thuộc ngưỡng. “—” chỉ các cặp có cùng ngưỡng ở hai phiên bản. Mọi Δ có chiều ghi rõ ở tên cặp.

| Phép so | Dataset | ΔAUROC [CI 95%] | ΔMCC [CI 95%] theo ngưỡng gốc hoặc ngưỡng arm | ΔMCC [CI 95%] sau hiệu chỉnh B0/B1 |
|---|---|---:|---:|---:|
| B2 − B0 | Devign | −0,0100 [−0,0280; 0,0078] | 0,0306 [−0,0080; 0,0681] | −0,0325 [−0,0750; 0,0106] |
| B2 − B0 | ReVeal | −0,0079 [−0,0357; 0,0183] | −0,0211 [−0,0634; 0,0207] | −0,0229 [−0,0630; 0,0153] |
| B1 − B0 | Devign | −0,0070 [−0,0197; 0,0057] | 0,0349 [−0,0084; 0,0759] | −0,0134 [−0,0459; 0,0183] |
| B1 − B0 | ReVeal | 0,0101 [−0,0092; 0,0287] | −0,0324 [−0,0708; 0,0049] | −0,0351 [−0,0743; 0,0014] |
| B1 − B1-shuf | Devign | −0,0096 [−0,0233; 0,0041] | −0,0207 [−0,0600; 0,0198] | −0,0060 [−0,0426; 0,0322] |
| B1 − B1-shuf | ReVeal | 0,0064 [−0,0161; 0,0296] | 0,0154 [−0,0220; 0,0547] | 0,0145 [−0,0250; 0,0559] |
| B2 − B2-rand | Devign | −0,0013 [−0,0158; 0,0140] | 0,0254 [−0,0152; 0,0673] | — |
| B2 − B2-rand | ReVeal | −0,0143 [−0,0352; 0,0064] | 0,0192 [−0,0299; 0,0675] | — |
| B2-nolabel − B1 | Devign | −0,0066 [−0,0183; 0,0052] | −0,0123 [−0,0437; 0,0181] | −0,0270 [−0,0587; 0,0058] |
| B2-nolabel − B1 | ReVeal | −0,0120 [−0,0288; 0,0049] | 0,0303 [−0,0132; 0,0733] | 0,0312 [−0,0130; 0,0755] |
| B2-flip − B2 | Devign | −0,0065 [−0,0233; 0,0105] | −0,0260 [−0,0609; 0,0094] | — |
| B2-flip − B2 | ReVeal | −0,0401 [−0,0648; −0,0155] | −0,0273 [−0,0607; 0,0049] | — |
| B2 − B2-labelonly | Devign | −0,0158 [−0,0345; 0,0024] | −0,0251 [−0,0738; 0,0229] | — |
| B2 − B2-labelonly | ReVeal | −0,0344 [−0,0588; −0,0103] | −0,0554 [−0,0911; −0,0209] | — |
| SUP-LR − B2 | Devign | 0,1254 [0,0862; 0,1672] | 0,1593 [0,0952; 0,2267] | — |
| SUP-LR − B2 | ReVeal | 0,2048 [0,1426; 0,2636] | 0,1939 [0,1136; 0,2714] | — |
| B2 − B1 | Devign | −0,0030 [−0,0186; 0,0122] | −0,0044 [−0,0412; 0,0332] | −0,0191 [−0,0605; 0,0227] |
| B2 − B1 | ReVeal | −0,0179 [−0,0400; 0,0041] | 0,0113 [−0,0337; 0,0560] | 0,0121 [−0,0339; 0,0568] |
| B2-labelonly − B1 | Devign | 0,0128 [0,0050; 0,0204] | 0,0208 [−0,0139; 0,0557] | 0,0061 [−0,0235; 0,0366] |
| B2-labelonly − B1 | ReVeal | 0,0165 [0,0041; 0,0294] | 0,0667 [0,0233; 0,1094] | 0,0676 [0,0251; 0,1085] |

#### Bảng B — McNemar và Holm trên full test

Mỗi hàng ghép dự đoán theo cùng ID và dùng nhãn từ manifest. `b` đếm **A đúng, B sai**, còn `c` đếm **A sai, B đúng**. McNemar hai phía kiểm tra chênh lệch tỷ lệ lỗi tại ngưỡng dùng ở hàng đó. Các hàng full test dưới đây dùng χ² với hiệu chỉnh liên tục. Đọc kết luận về ΔMCC và ΔAUROC từ CI ở bảng trước.

Mỗi cột Holm hiệu chỉnh **16 p-value** (8 cặp × 2 dataset) trong cùng phiên bản ngưỡng B0/B1. “Cả hai” dùng cùng dự đoán ở hai phiên bản, nhưng p sau Holm vẫn có thể khác do các cặp còn lại thay đổi. Trong 22 đối chiếu theo dataset ở `prereg-v1:configs/protocol.yaml`, đợt này còn thiếu B2/B3, B1/B1-H2 và P_pre/P_post trên cả hai dataset. B3 và B1-H2 thuộc phần thăm dò của Phương án 1. Đầu vào Step 6 được dùng trong báo cáo hiện có CI tổng hợp, còn `joined_test.csv` không có score từng ID của P_pre/P_post để tính hai ô bất đồng. Hai cặp bổ sung để đọc gap demo có p thô trong CSV và nằm ngoài họ Holm. Cặp B2-rand/B2 giữ chiều của bảng Δ ở trên. Đảo thứ tự A/B hoán đổi `b` và `c` và cho cùng p hai phía.

| Dataset | A | B | Phiên bản ngưỡng B0/B1 | b | c | p thô | p Holm gốc | p Holm hiệu chỉnh |
|---|---|---|---|---:|---:|---:|---:|---:|
| Devign | B0 | B2 | Gốc | 275 | 343 | 0,007036 | 0,04222 | — |
| Devign | B0 | B2 | Hiệu chỉnh hồi cứu | 621 | 511 | 0,001197 | — | 0,009573 |
| Devign | B0 | B1 | Gốc | 485 | 617 | 7,940 × 10⁻⁵ | 0,0006352 | — |
| Devign | B0 | B1 | Hiệu chỉnh hồi cứu | 178 | 162 | 0,4159 | — | 0,8319 |
| Devign | B1-shuf | B1 | Gốc | 318 | 280 | 0,1303 | 0,5211 | — |
| Devign | B1-shuf | B1 | Hiệu chỉnh hồi cứu | 204 | 196 | 0,7263 | — | 0,8319 |
| Devign | B2-rand | B2 | Cả hai | 542 | 499 | 0,1930 | 0,5211 | 0,6436 |
| Devign | B1 | B2-nolabel | Gốc | 222 | 199 | 0,2836 | 0,5211 | — |
| Devign | B1 | B2-nolabel | Hiệu chỉnh hồi cứu | 264 | 211 | 0,01704 | — | 0,08518 |
| Devign | B2 | B2-flip | Cả hai | 294 | 260 | 0,1609 | 0,5211 | 0,6436 |
| Devign | B2-labelonly | B2 | Cả hai | 645 | 542 | 0,003071 | 0,02150 | 0,02150 |
| Devign | B2 | SUP-LR | Cả hai | 482 | 674 | 1,936 × 10⁻⁸ | 1,742 × 10⁻⁷ | 1,742 × 10⁻⁷ |
| ReVeal | B0 | B2 | Gốc | 524 | 90 | 2,243 × 10⁻⁶⁸ | 2,915 × 10⁻⁶⁷ | — |
| ReVeal | B0 | B2 | Hiệu chỉnh hồi cứu | 462 | 101 | 5,404 × 10⁻⁵² | — | 7,025 × 10⁻⁵¹ |
| ReVeal | B0 | B1 | Gốc | 86 | 269 | 4,478 × 10⁻²² | 4,926 × 10⁻²¹ | — |
| ReVeal | B0 | B1 | Hiệu chỉnh hồi cứu | 95 | 307 | 6,717 × 10⁻²⁶ | — | 7,388 × 10⁻²⁵ |
| ReVeal | B1-shuf | B1 | Gốc | 213 | 77 | 2,237 × 10⁻¹⁵ | 2,237 × 10⁻¹⁴ | — |
| ReVeal | B1-shuf | B1 | Hiệu chỉnh hồi cứu | 253 | 73 | 3,622 × 10⁻²³ | — | 3,622 × 10⁻²² |
| ReVeal | B2-rand | B2 | Cả hai | 737 | 98 | 5,042 × 10⁻¹⁰⁸ | 8,067 × 10⁻¹⁰⁷ | 8,067 × 10⁻¹⁰⁷ |
| ReVeal | B1 | B2-nolabel | Gốc | 552 | 80 | 2,548 × 10⁻⁷⁸ | 3,568 × 10⁻⁷⁷ | — |
| ReVeal | B1 | B2-nolabel | Hiệu chỉnh hồi cứu | 504 | 76 | 2,451 × 10⁻⁷⁰ | — | 3,432 × 10⁻⁶⁹ |
| ReVeal | B2 | B2-flip | Cả hai | 100 | 143 | 0,007054 | 0,04222 | 0,04232 |
| ReVeal | B2-labelonly | B2 | Cả hai | 335 | 70 | 2,588 × 10⁻³⁹ | 3,105 × 10⁻³⁸ | 3,105 × 10⁻³⁸ |
| ReVeal | B2 | SUP-LR | Cả hai | 192 | 927 | 1,027 × 10⁻¹⁰⁶ | 1,541 × 10⁻¹⁰⁵ | 1,541 × 10⁻¹⁰⁵ |

Ở mức 0,05 trong nhóm đã tính, có **12/16** hàng với ngưỡng gốc và **11/16** hàng với ngưỡng hiệu chỉnh. Trên Devign, B2 so với B0 có ít lỗi hơn với ngưỡng gốc (343 ca B2 đúng/B0 sai so với 275 ca ngược lại) và nhiều lỗi hơn với ngưỡng hiệu chỉnh (511 so với 621). Cả hai p Holm của cặp này đều dưới 0,05 trong nhóm 16. Các hàng tập bỏ trùng/gần trùng có họ Holm riêng trong [CSV các phép so](../Runs-management/analysis_pa1_20261111/contrasts.csv).

#### Bảng C — Độ nhạy nhãn trên full test

Ghép B2, B2-flip và B2-rep seed 42 trên cùng ID. Tính lại nhãn dự đoán từ score theo quy tắc `s ≥ τ`, áp cùng ngưỡng cho cả ba arm ở mỗi hàng. Net là tỷ lệ dự đoán đổi từ B2 sang B2-flip trừ tỷ lệ đổi từ B2 sang B2-rep. Mỗi lượt bootstrap lấy cùng các cụm ID cho cả ba arm. Toàn bộ records B2-rep có cờ và tag repeat, với prompt hash khớp B2 theo từng ID.

| Dataset | Cách đặt ngưỡng | Ngưỡng τ | ID ghép | Flip đổi, số ca (%) | Repeat đổi, số ca (%) | Net [CI 95%], điểm phần trăm |
|---|---|---:|---:|---:|---:|---:|
| Devign | B2 đã khóa | 0,70 | 2.732 | 554 (20,28%) | 0 (0,00%) | 20,28 [18,75; 21,76] |
| ReVeal | B2 đã khóa | 0,12 | 2.274 | 243 (10,69%) | 0 (0,00%) | 10,69 [9,15; 12,25] |
| Devign | 0,5 đối chiếu | 0,50 | 2.732 | 495 (18,12%) | 0 (0,00%) | 18,12 [16,66; 19,56] |
| ReVeal | 0,5 đối chiếu | 0,50 | 2.274 | 316 (13,90%) | 0 (0,00%) | 13,90 [12,10; 15,80] |

H2.1 được đánh giá ở ngưỡng B2 đã khóa. CI của Devign nằm trên mốc 15 điểm phần trăm và CI của ReVeal nằm dưới mốc này. Ở ngưỡng đối chiếu 0,5, CI của ReVeal chứa mốc 15. Trên tập đã loại trùng/gần trùng với train, net ở ngưỡng khóa lần lượt là 19,66 [18,12; 21,24] và 9,56 [8,04; 11,12] điểm phần trăm.

[Bảng CSV các cặp](../Runs-management/analysis_pa1_20261111/contrasts.csv) ghi N, số cụm, δ, nhận định theo CI, hai ô bất đồng McNemar và p thô. Các cột Holm chỉ hiệu chỉnh trong nhóm cặp có dữ liệu của từng partition và phiên bản ngưỡng; đây là nhóm chưa đầy đủ của bảng đăng ký. McNemar xét đúng/sai theo ngưỡng, còn CI ở bảng trên xét chênh lệch MCC hoặc AUROC. [CSV độ nhạy](../Runs-management/analysis_pa1_20261111/sensitivity.csv) có thêm ngưỡng 0,5 và tập đã loại trùng/gần trùng với train (2.472 Devign, 1.978 ReVeal). Tái tạo từ [script](../Runs-management/analysis_pa1_20261111/recompute.py), dùng các hàm thống kê trong ZIP Phương án 1, với [SHA-256 đầu vào và số records theo runtime](../Runs-management/analysis_pa1_20261111/provenance.json).

Đây là phân tích trên test đã tiếp xúc. Các CI là CI riêng lẻ, có điều kiện trên records và ngưỡng đã dùng. B2-rand ReVeal seed 42 có hai hash runtime (2.017 và 257 records); kết quả của cặp này mang giới hạn đó. Với các nguồn thiếu hash runtime trong từng record, giữ trạng thái provenance của run trong hồ sơ nguồn. B3 và B1-H2 được báo riêng theo diện thăm dò của Phương án 1.

## 2. Trả lời sáu câu hỏi nghiên cứu tại mục 4

Các câu trả lời dưới đây dựa trên test đầy đủ của các arm, với seed 42 làm lượt so sánh chính; B2-rand và B1-shuf có thêm ba seed để mô tả độ biến thiên. CI ghép cặp đã tính được dùng paired cluster bootstrap 5.000 lượt, seed 20261117. Point estimate không được xem là bằng chứng tương đương nếu CI chưa thỏa biên δ.

| Câu hỏi trong đề cương | Trả lời theo số liệu | Kết luận và giới hạn |
|---|---|---|
| **RQ1 – Tái lập:** Với LLM open-weight và giao thức chuẩn, GRACE có vượt zero-shot và đối chứng hằng không, có đạt mức bài gốc không? | B2−B0 về AUROC: Devign −0,0100 [−0,0280; 0,0078], ReVeal −0,0079 [−0,0357; 0,0183]; cận trên cả hai dưới δ=0,02. Với ngưỡng gốc, ΔMCC là +0,0306 [−0,0080; 0,0681] và −0,0211 [−0,0634; 0,0207]; Devign chưa loại trừ lợi ích 0,03. Với ngưỡng hiệu chỉnh hồi cứu, ΔMCC lần lượt −0,0325 [−0,0750; 0,0106] và −0,0229 [−0,0630; 0,0153]. MCC B2 là 0,0597/0,0645; F1 Devign 0,5485 so với ALL-1 là 0,6295. | Trong backbone Qwen được đánh giá, AUROC không cho thấy B2 vượt B0 ở mức lợi ích δ; MCC phụ thuộc bộ ngưỡng. H1.2 đạt tiêu chí số học. Mức của bài gốc với backbone/model khác không được kiểm định bằng 15 arm này. |
| **RQ2 – Cơ chế demonstration:** Tác động qua nội dung mã demo hay nhãn đi kèm? | Net label sensitivity của B2-flip trừ B2-rep tại ngưỡng B2 là +20,28 điểm [18,75; 21,76] Devign và +10,69 [9,15; 12,25] ReVeal. ΔAUROC B2−B2-rand có CI [−0,0158; 0,0140] Devign và [−0,0352; 0,0064] ReVeal. ΔAUROC B2-nolabel−B1 có CI [−0,0183; 0,0052] và [−0,0288; 0,0049]. B2-labelonly AUROC 0,5462/0,6005; B2 là 0,5305/0,5662; B1 là 0,5335/0,5841. | Đảo nhãn ảnh hưởng rõ trên Devign và yếu hơn trên ReVeal. Các phép so demo ngẫu nhiên/bỏ nhãn loại trừ mức tăng AUROC 0,02 theo cận trên đã tính, nhưng label-only không tái tạo lợi thế B2−B1 dương (B2 vốn thấp hơn B1). Kết quả phù hợp với tác động lên operating point hơn lợi thế ranking ổn định, nhưng không chứng minh đó là cơ chế duy nhất. B2-rand ReVeal có hai runtime segment; xem giới hạn ở mục 1.6. |
| **RQ3 – Graph:** LLM có dùng thông tin graph dưới ngân sách context thực tế không? | AUROC B1−B0: Devign −0,0070 [−0,0197; 0,0057], ReVeal +0,0101 [−0,0092; 0,0287]. B1−B1-shuf seed42: Devign −0,0096 [−0,0233; 0,0041], ReVeal +0,0064 [−0,0161; 0,0296]. B1-H2−B1: +0,0142 [−0,0012; 0,0301] Devign; +0,0115 [−0,0105; 0,0342] ReVeal. | Trên Devign, hai phép so graph chính có cận trên dưới 0,02; trên ReVeal thì không. B1-H2 cũng chưa loại trừ khác biệt ≥0,02 trên dataset nào. Chưa có bằng chứng nhất quán rằng graph cải thiện ranking, nhưng cũng chưa thể kết luận LLM hoàn toàn không đọc graph. |
| **RQ4 – Phân biệt hay dịch chuyển ngưỡng:** Các biến thể prompt đổi AUROC/AUPRC hay chỉ operating point? | B3−B2: ΔAUROC +0,0047 [−0,0135; 0,0228] Devign, −0,0369 [−0,0650; −0,0079] ReVeal; ΔAUPRC +0,0168/−0,0091. Tỷ lệ dự đoán 1 đổi −22,29/+29,73 điểm. B3-nodiff−B2 có ΔAUROC +0,0054/−0,0090, ΔAUPRC +0,0151/−0,0032, còn rate đổi −6,15/+7,87 điểm. B3-swap−B3 có ΔAUROC −0,0023/+0,0321 và rate −1,75/−16,62 điểm; B3-flip−B3 là +0,0038/+0,0352 và −6,07/−17,33 điểm (Devign/ReVeal). | Không thể nói mọi biến thể chỉ dịch chuyển ngưỡng: B3−B2 trên ReVeal giảm AUROC với CI không chứa 0; Devign có cận trên CI hơi vượt biên 0,02. B3-nodiff là trường hợp ranking gần hơn nhưng operating point vẫn đổi. ΔAUPRC và các probe B3 ngoài H2.3 là point estimates; hiệu ứng phụ thuộc dataset/prompt. |
| **RQ5 – Mốc có giám sát:** Anchor tuyến tính/code metrics so với LLM ra sao, và LLM có thêm tín hiệu sau/trước truy vấn không? | SUP-LR−B2 ΔMCC +0,1593 [0,0952; 0,2267] Devign và +0,1939 [0,1136; 0,2714] ReVeal; AUROC SUP-LR 0,6559/0,7709. P_post−P_pre ΔMCC −0,0015 [−0,0122; 0,0093] và −0,0242 [−0,0550; 0,0047]. Routing q=10%: ΔBA Benefit−Random +0,0204 [0,0138; 0,0270] Devign và −0,0487 [−0,0707; −0,0285] ReVeal; repairs trên toàn test là 397/164, so với P97,5 random expert 465,05/176,15. | SUP-LR vượt B2 về MCC theo δ và CI ở cả hai; AUROC tuyệt đối đạt 0,68 chỉ trên ReVeal. P_post chưa cho thấy mức tăng MCC ≥0,02; kết quả ReVeal còn phụ thuộc cách gom cụm Step 6, cần đối soát theo cụm file. H5.3 không đạt trên Devign; ReVeal tạm đạt theo phép tính hiện tại nhưng CI cần đối soát cụm file. |
| **RQ6 – Truy hồi và lỗi:** Demo có liên quan cơ chế không, liên quan có kéo theo dự đoán đúng không, và bao nhiêu “lỗi” thực ra là nhãn nhiễu? | Chưa có bộ chấm mù 200 target, phân tích accuracy theo nhóm relevance, hay audit/adjudication 100 ca sai. | Chưa thể trả lời từ inference arm. Đây là một thí nghiệm riêng đã ghi trong đề cương. |

## 3. Đối chiếu giả thuyết đăng ký trước tại mục 4.3

| Giả thuyết | Tiêu chí đăng ký | Kết quả đầy đủ hiện có | Kết luận |
|---|---|---|---|
| **H1.1 – B2 không vượt B0** | Cận trên CI ΔMCC(B2−B0)<0,03 và ΔAUROC<0,02 trên cả hai dataset | AUROC cận trên 0,0078/0,0183. MCC ngưỡng gốc cận trên 0,0681/0,0207; ngưỡng hiệu chỉnh hồi cứu 0,0106/0,0153 (Devign/ReVeal). | **Một phần.** AUROC đạt cả hai; MCC đạt ReVeal nhưng không đạt Devign theo ngưỡng gốc. Không gộp kết quả hồi cứu với phân tích đăng ký. |
| **H1.2 – B2 yếu theo MCC/F1** | MCC B2<0,15 cả hai; F1 Devign thấp hơn ALL-1 | MCC 0,0597/0,0645; F1 Devign 0,5485<0,6295. | **Đạt.** |
| **H2.1 – Demo tác động qua nhãn** | Net label sensitivity ≥15 điểm | Devign 20,28 [18,75; 21,76]; ReVeal 10,69 [9,15; 12,25]. | **Một phần.** Đạt Devign, không đạt ReVeal. |
| **H2.2 – Nội dung demo không mang tín hiệu** | Cận trên CI AUROC(B2−B2-rand)<0,02; AUROC(B2-nolabel−B1)<0,02; B2-labelonly tái tạo ≥80% gap B2−B1 | Hai cận trên đầu là 0,0140/0,0064 và 0,0052/0,0049 (Devign/ReVeal). B2−B1 point gap −0,0030/−0,0179 nên không có lợi thế dương để label-only tái tạo. | **Một phần; giả thuyết gộp chưa đạt trọn vẹn.** Hai điều kiện CI đạt; điều kiện tái tạo 80% không được hỗ trợ. |
| **H2.3 – Cặp tương phản chỉ dịch chuyển điểm hoạt động** | Tỷ lệ dự đoán 1 của B3 cao hơn B2 ≥10 điểm; cận trên CI ΔAUROC(B3−B2)<0,02 | Devign: rate Δ −22,29 điểm; ΔAUROC +0,0047, CI [−0,0135; 0,0228]. ReVeal: rate Δ +29,73 điểm; ΔAUROC −0,0369, CI [−0,0650; −0,0079]. Paired cluster bootstrap 5.000 lượt, seed 20261117. | **Một phần, phụ thuộc dataset.** ReVeal đạt cả hai; Devign không đạt điều kiện rate và CI AUROC vượt biên 0,02. |
| **H3.1 – LLM không đọc graph** | Cận trên CI B1−B0 và B1−B1-shuffle <0,02; B1-H2 không khác B1 theo cùng biên | Hai so sánh chính: cận trên Devign 0,0057/0,0041; ReVeal 0,0287/0,0296. B1-H2−B1 cận trên 0,0301/0,0342. | **Chưa được hỗ trợ đầy đủ.** Devign đạt hai điều kiện chính; ReVeal và B1-H2 chưa loại trừ khác biệt ≥0,02. |
| **H4.1 – Mọi arm LLM gần ngẫu nhiên theo AUROC** | AUROC mọi arm LLM ≤0,62 | AUROC cao nhất trong 15 arm là 0,6005 (B2-labelonly, ReVeal); nhóm B3 cao nhất 0,5644. | **Đạt** trên hai test census. |
| **H5.1 – Mốc có giám sát thắng rõ** | ΔMCC(SUP-LR−B2)≥0,15, CI không chứa 0; AUROC SUP-LR≥0,68 | Devign ΔMCC +0,1593 [0,0952; 0,2267], AUROC 0,6559. ReVeal +0,1939 [0,1136; 0,2714], AUROC 0,7709. | **Một phần.** MCC đạt ở cả hai; AUROC đạt ReVeal, không đạt Devign. |
| **H5.2 – LLM không thêm giá trị sau truy vấn** | Cận trên CI ΔMCC(P_post−P_pre)<0,02 | Devign −0,0015, cận trên 0,0093. ReVeal hiện −0,0242, cận trên 0,0047, nhưng CI được gom cụm theo code hash thay vì nhóm file `source_id`; 646 cụm file cần chạy/đối soát lại. | **Đạt Devign; tạm đạt ReVeal theo kết quả hiện tại.** Chưa chốt H5.2 cho cả hai dataset trước khi sửa đơn vị cụm ReVeal. |
| **H5.3 – Không biết trước khi nào nên gọi LLM** | q=10%: cận trên CI ΔBA(benefit−random)<0,01; repairs không vượt P97,5 expert random | Devign: CI ΔBA [0,0138; 0,0270], repairs 397 < 465,05. ReVeal: CI [−0,0707; −0,0285], repairs 164 < 176,15. ReVeal CI Step 6 hiện dùng code-hash groups; mapping theo source_id cho 646 file clusters vẫn cần đối soát theo lưu ý mục 1.5. | **Không đạt Devign** vì cận trên không dưới 0,01. **Tạm đạt ReVeal theo phép tính hiện tại**, nhưng chưa chốt trước khi đối soát CI theo cụm file đúng đơn vị đăng ký. |
| **H6.1 – Relevance demo và nhãn nhiễu** | “Neither”≥40% Devign; CI accuracy giữa nhóm demo liên quan/không liên quan chứa 0 | Chưa có nhãn chấm mù relevance và adjudication ca sai. | **Chưa adjudicate.** Cần hoàn tất chấm mù/audit; inference không cung cấp biến outcome này. |

### Kết luận tổng hợp

Đủ 15 arm inference cho phép tính và đối chiếu metric của arm, nhưng không tự hoàn tất các nghiên cứu Step 6/Step 8. Bằng chứng hiện tại cho thấy AUROC B2 không vượt B0 theo biên 0,02; MCC B2 thấp hơn 0,15 và F1 Devign thấp hơn ALL-1. Đảo nhãn tác động mạnh trên Devign nhưng dưới mốc đăng ký trên ReVeal. H2.3 chỉ đạt trên ReVeal; trên Devign B3 không tăng tỷ lệ dự đoán 1 và cận trên CI AUROC vượt 0,02. SUP-LR vượt B2 về MCC trên cả hai dataset, AUROC đạt mốc 0,68 chỉ trên ReVeal. H5.2 đạt trên Devign; H5.3 không đạt trên Devign; cả hai kết quả ReVeal cần đối soát lại theo cụm file. H4.1 đạt; H3.1 chỉ được hỗ trợ một phần; H6.1 chờ chấm mù/audit nhãn.

**Giới hạn và tính toàn vẹn:** Test đã được tiếp xúc trong quá trình nghiên cứu; các lần chạy lại không biến test này thành tập chưa từng xem. B0/B1 có thêm bộ ngưỡng hiệu chỉnh hồi cứu, được tách khỏi ngưỡng preregistered. B3/B3-swap/B3-flip là test seed42 đủ census; metric mới được tính bằng join với frozen labels tại local, không có nhãn gửi lên Kaggle. CI B3−B2 cho H2.3 là paired cluster bootstrap, chưa hiệu chỉnh Holm cho toàn bộ họ kiểm định. Không suy diễn hoàn tất toàn bộ mục tiêu nghiên cứu chỉ từ việc 15 arm inference đã chạy xong.

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
