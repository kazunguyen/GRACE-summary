# Báo cáo kết quả các arm GRACE đã hoàn tất — cập nhật 10/11/2026

**Ngày lập ban đầu:** 08/11/2026<br>
**Cập nhật:** 10/11/2026<br>
**Phạm vi:** B0, B1, B1-full, B1-shuf (seed 42/43/44), B2, B2-flip, B1-H2, B2-rand (seed 42/43/44), B2-rep, B2-nolabel, B2-labelonly, B3-nodiff; bổ sung Step 6 gồm SUP-LR/SUP-MLP/SUP-METRIC, P_pre/P_post, đối chứng sửa–hỏng và routing. B3-nodiff là test seed 42 đủ 5.006 record với ngưỡng khóa validation 0,92/0,01; không đại diện cho B3 đầy đủ. Các run B0/B1 cũ dùng ngưỡng hiệu chỉnh hồi cứu; giữ rõ exposure khi báo cáo.

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
| Devign | B2-rand s44 | 2.732 | 0 | 0,0589 | 0,5327 | 0,5006 | 0,3295 | 0,5243 | 0,5153 | 0,2422 | 0,2160 |
| ReVeal | B2-rand s44 | 2.274 | 0 | 0,0665 | 0,5748 | 0,1235 | 0,1959 | 0,5495 | 0,1332 | 0,3696 | 0,2806 |

**Ghi chú metric/provenance B3-nodiff:** metric @τ được đối soát trực tiếp từ 5.006 record tại τ=0,92/0,01 và khớp MCC/BA/F1/tỷ lệ dự đoán 1 trong shared evaluator. Các cột confusion trong `table_A_metrics.csv` của evaluator là tại 0,5, không phải tại τ; confusion tính lại tại τ: Devign `TP=714, FP=762, TN=715, FN=541`; ReVeal `TP=167, FP=1.288, TN=756, FN=63`. Devign có một raw response lỗi nhưng score vẫn hợp lệ; cả 5.006 score hữu hạn. Threshold được khóa trên validation và không đổi sau khi xem test. Runtime SHA của nguồn seal validation và runtime test khác nhau do test lock bổ sung pin SciPy; audit ghi core inference settings khớp, nhưng hai SHA không được coi là cùng một lock.

Metric từng mẫu, ma trận nhầm lẫn, kiểm tra ID/nhãn, nguồn record và các chênh lệch ghép cặp của các arm đã tích hợp trước đó được lưu trong [workbook metric](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/outputs/metrics_completed_arms_20261107/GRACE_completed_arms_metrics.xlsx). B3-nodiff chưa được nhập vào workbook. Chênh lệch trong workbook là point estimate; chưa gồm paired bootstrap CI, McNemar hay hiệu chỉnh Holm.

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

Hai meta-model logistic dùng cùng 34 đặc trưng nền, cùng 3 fold StratifiedGroupKFold, cùng scaler và fallback đối xứng khi expert invalid. Ngưỡng chọn từ validation OOF. CI là paired cluster bootstrap 5.000 lượt (Devign nhóm theo commit_id; ReVeal theo file_hash/code_sha256 fallback).

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

Ở ngân sách 10%, BA benefit-router cao hơn trung bình Random ở Devign (+0,0204) nhưng thấp hơn ở ReVeal (−0,0487). Output hiện lưu phân phối metric của từng loại router, không lưu CI paired cho `benefit − random`; vì vậy chưa áp dụng được đúng tiêu chí cận trên CI < 0,01 của H5.3. Số repair 55/68 cũng cần đặt cạnh RANDOM expert ở mục 0: 433,85 [411,28; 465,05] trên Devign và 161,35 [150,85; 176,15] trên ReVeal. Đây là so sánh mô tả theo protocol; số ca router được gọi chỉ bằng 10% test nên không diễn giải chênh lệch thô như một phép thử paired.

## 2. Trả lời câu hỏi nghiên cứu tại mục 4

| Câu hỏi | Trả lời từ kết quả hiện có | Mức kết luận |
|---|---|---|
| **RQ1 – Tái lập:** GRACE có vượt zero-shot và đối chứng hằng không? | B2 không vượt B0 theo point estimate trên hai test: Devign ΔMCC = −0,0325, ΔAUROC = −0,0100; ReVeal ΔMCC = −0,0229, ΔAUROC = −0,0078. MCC B2 là 0,0597/0,0645, đều dưới 0,15; F1 B2 Devign 0,5485 thấp hơn ALL-1 (0,6295). | Kết quả mô tả nhất quán với “không vượt”; chưa xác nhận H1.1 bằng CI paired. H1.2 đạt tiêu chí số học đã nêu. |
| **RQ2 – Cơ chế demonstration:** ảnh hưởng đến từ mã demo hay nhãn? | B2-rand AUROC gần B2, chênh lệch B2-rand−B2 lần lượt +0,0013 đến +0,0031 Devign và +0,0085 đến +0,0143 ReVeal qua ba seed. B2-nolabel thấp hơn B1 về AUROC (−0,0066/−0,0120); B2-labelonly cao hơn B1 (+0,0127/+0,0164), trong khi B2 thấp hơn B1 (−0,0030/−0,0179). | Chưa chứng minh cơ chế bằng CI. Point estimate không cho thấy nội dung demo tạo lợi thế; label-only không tái tạo “lợi thế B2 so với B1” vì B2 vốn không cao hơn B1. Net label sensitivity theo cặp cần bảng prediction từng mẫu/đối chứng repeat. |
| **RQ3 – Graph:** LLM có dùng thông tin graph không? | B1−B0 về AUROC là −0,0070 Devign và +0,0101 ReVeal. B1-H2−B1 là +0,0142/+0,0115. So với B1-shuf seed 42, B1−B1-shuf là −0,0096 Devign và +0,0064 ReVeal. | Chỉ mô tả point estimate; chưa kết luận graph có/không được dùng vì H3.1 yêu cầu CI và B1-shuf có nhiều seed. |
| **RQ4 – Phân biệt hay dịch chuyển ngưỡng:** khác biệt prompt có đổi AUROC hay chỉ operating point? | B3-nodiff−B2: ΔAUROC +0,0054 Devign và −0,0090 ReVeal, nhưng tỷ lệ dự đoán 1 đổi −6,15 và +7,87 điểm phần trăm. Đây là ví dụ AUROC khá gần trong khi operating point dịch chuyển rõ. | Có thể mô tả sự tách biệt giữa ranking và operating point ở cặp B3-nodiff/B2; không suy rộng sang B3 đầy đủ. Các arm khác cũng cần CI để khẳng định “chỉ” dịch chuyển ngưỡng. |
| **RQ5 – Mốc có giám sát:** anchor thắng LLM và LLM có bổ sung tín hiệu không? | Cả SUP-LR, SUP-MLP và SUP-METRIC đều cao hơn B2 về MCC và AUROC theo point estimate trên cả hai dataset. Riêng SUP-LR, ΔMCC là +0,1593 Devign và +0,1939 ReVeal; AUROC là 0,6559/0,7709. P_post không tăng MCC đáng kể so với P_pre: Δ=−0,0015 [−0,0122; 0,0093] và −0,0242 [−0,0550; 0,0047]. Routing q=10% có kết quả trái nhau giữa dataset: BA benefit-router cao hơn Random trên Devign, thấp hơn trên ReVeal. | Mốc có giám sát thắng theo point estimate. H5.2 được ủng hộ theo biên δ. H5.1 chưa được ủng hộ toàn bộ: AUROC Devign không đạt 0,68 và CI ΔMCC chưa có. H5.3 chưa adjudicate vì thiếu CI paired benefit−random. |
| **RQ6 – Truy hồi và lỗi:** demo có liên quan cơ chế không, và lỗi có phải nhãn nhiễu? | Worklog Step 6 xác nhận chấm relevance demo, packet 60 ca và audit nhãn vẫn là việc tiếp theo; báo cáo hiện chưa có metric cho các phân tích này. | Chưa trả lời được từ kết quả hiện có. |

## 3. Đối chiếu giả thuyết đăng ký trước tại mục 4.3

| Giả thuyết | Tiêu chí đăng ký trước | Kết quả | Đối chiếu |
|---|---|---|---|
| **H1.1** | Cận trên CI ΔMCC(B2−B0) < 0,03 và ΔAUROC < 0,02 | Point estimate: ΔMCC −0,0325/−0,0229; ΔAUROC −0,0100/−0,0078 (Devign/ReVeal). | Chưa adjudicate: CI paired chưa có; point estimate phù hợp hướng dự đoán. |
| **H1.2** | MCC B2 < 0,15 trên cả hai; F1 B2 Devign thấp hơn ALL-1 | MCC 0,0597/0,0645; F1 B2 0,5485 so với ALL-1 0,6295. | Đạt tiêu chí số học trên các kết quả hiện có. |
| **H2.1** | Net label sensitivity ≥ 15 điểm | Chưa có phép tính paired đảo nhãn trừ biến động tự nhiên trong bảng kết quả hiện tại. | Chưa adjudicate. |
| **H2.2** | Cận trên CI AUROC(B2−B2-rand) < 0,02 và AUROC(B2-nolabel−B1) < 0,02; label-only tái tạo ≥80% chênh B2−B1 | Chênh lệch AUROC point estimate nhỏ nhưng CI chưa có. B2 thấp hơn B1 ở cả hai dataset nên label-only không tái tạo được một lợi thế dương B2−B1. | Chưa đủ bằng chứng cho các điều kiện CI; điều kiện label-only không được hỗ trợ bởi kết quả hiện có. |
| **H2.3** | Tỷ lệ dự đoán 1 của B3 cao hơn B2 ≥10 điểm; cận trên CI ΔAUROC(B3−B2)<0,02 | Có B3-nodiff, chưa có B3 đầy đủ; B3-nodiff không tăng tỷ lệ dự đoán 1 ≥10 điểm trên cả hai dataset. | Chưa adjudicate H2.3 vì arm B3 đầy đủ chưa có kết quả test. |
| **H3.1** | Cận trên CI ΔAUROC(B1−B0), ΔAUROC(B1−B1-shuffle) <0,02; B1-H2 không khác B1 theo cùng tiêu chí | Các chênh AUROC điểm đều nhỏ (RQ3); CI chưa có. | Chưa adjudicate. |
| **H4.1** | AUROC mọi arm LLM ≤0,62 | Trong các arm LLM có test metric trong báo cáo, lớn nhất là 0,6005 (B2-labelonly, ReVeal). | Đạt trên nhóm arm đã có metric test; chưa khẳng định cho arm chưa hoàn tất/chưa có test. |
| **H5.1** | ΔMCC(SUP-LR−B2) ≥0,15, CI không chứa 0; AUROC SUP-LR ≥0,68 | ΔMCC +0,1593/+0,1939; AUROC 0,6559/0,7709. Chưa có CI paired ΔMCC. | Một phần: point MCC đạt cả hai dataset; AUROC Devign không đạt ngưỡng, và điều kiện CI chưa kiểm tra. Không kết luận H5.1 được ủng hộ toàn bộ. |
| **H5.2** | Cận trên CI ΔMCC(P_post−P_pre) <0,02 trên cùng đặc trưng/fold/ngưỡng | Devign −0,0015, CI [−0,0122; 0,0093]; ReVeal −0,0242, CI [−0,0550; 0,0047]. | Đạt tiêu chí ở cả hai dataset: loại trừ mức tăng MCC ≥0,02 trong phân tích này. |
| **H5.3** | q=10%: cận trên CI ΔBA(benefit−random)<0,01; số repair LLM không vượt khoảng 95% của expert random cùng tỷ lệ dự đoán 1 | ΔBA điểm +0,0204 Devign và −0,0487 ReVeal; random-router chỉ có phân vị riêng từng nhóm, không có paired CI delta. Benefit-router repair 55/68; random-expert repair khoảng [411,28;465,05]/[150,85;176,15]. | Chưa adjudicate tiêu chí CI; điểm Devign không phù hợp hướng “<0,01”. Số repair router thấp hơn khoảng tham chiếu, nhưng đối chiếu thô không thay cho CI theo đúng ngân sách. |
| **H6.1** | “Neither” ≥40% Devign; CI accuracy giữa demo liên quan/không liên quan chứa 0 | Chưa có kết quả chấm relevance demo và ghép với đúng/sai. | Chưa adjudicate; chờ phần chấm mù/audit đã nêu trong worklog. |


### Kết luận ngắn

Các kết quả hiện có cho thấy B2 không vượt B0 trên MCC/AUROC, còn MCC B2 thấp hơn 0,15 trên cả hai dataset và F1 Devign thấp hơn ALL-1. Với RQ5, SUP-LR có MCC cao hơn B2 theo point estimate, nhưng AUROC Devign không đạt tiêu chí H5.1 và chưa có CI paired cho chênh MCC. Cặp P_pre/P_post cho kết quả chắc nhất ở Step 6: cận trên CI ΔMCC thấp hơn 0,02 trên cả Devign lẫn ReVeal, nên loại trừ mức tăng có ý nghĩa đã định trước của P_post trong phép thử này. Routing q=10% có hướng khác nhau giữa hai dataset và chưa có CI paired benefit−random; không tuyên bố router tốt hơn/ngang random theo tiêu chí đăng ký. Các kết luận về RQ2/RQ3 hiện vẫn là mô tả point estimate; H2.1, H2.3 và RQ6 còn thiếu phân tích/arm cần thiết.

**Giới hạn suy luận:** Các metric arm trong workbook vẫn chủ yếu là point estimates, chưa có paired cluster bootstrap CI, McNemar hoặc hiệu chỉnh Holm cho toàn bộ đối chiếu. Riêng phân tích Step 6 đã có paired cluster bootstrap 5.000 lượt cho P_pre/P_post và routing benefit−confidence; các CI đó không tự thay thế phép kiểm định đúng tiêu chí H5.1/H5.3 nêu trên. So sánh B3-nodiff−B2 được bổ sung ở đây mới là point estimate, hơn nữa B2 chưa có chứng nhận theo runtime lock hiện hành; không dùng nó để kết luận tương đương hoặc xác nhận H2.3. Kết quả B0/B1 dùng ngưỡng hiệu chỉnh hồi cứu; mọi mức độ tiếp xúc test cần được giữ trong báo cáo cuối.

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
- [RUNS.md — lượt I-20 và tình trạng đủ 5.006 test record mỗi seed](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/Runs-management/RUNS.md)
- [B2-rand merged evaluation summary](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/06_Arm_B2_Rand/test_results_20261107/evaluation_summary.json) · [Provenance và runtime hashes](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/06_Arm_B2_Rand/test_results_20261107/provenance.json)
- [Step 6 lock](https://github.com/kazunguyen/GRACE-summary/blob/dung/STEP6_supervised_anchors/step6_lock.json) · [Worklog Step 6, gồm protocol, hash và trạng thái đầu ra](https://github.com/kazunguyen/GRACE-summary/blob/dung/worklogs/2026-11-08_step6_supervised_anchors_start.md) · [Mã phân tích complementarity](https://github.com/kazunguyen/GRACE-summary/blob/dung/STEP6_supervised_anchors/src/step6_complementarity.py)
- [B2-rand test records — seed 42 Devign](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/06_Arm_B2_Rand/test_results_20261107/seed_42/devign/test/records.jsonl) · [seed 42 ReVeal](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/06_Arm_B2_Rand/test_results_20261107/seed_42/reveal/test/records.jsonl)
- [B2-rand test records — seed 43 Devign](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/06_Arm_B2_Rand/test_results_20261107/seed_43/devign/test/records.jsonl) · [seed 43 ReVeal](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/06_Arm_B2_Rand/test_results_20261107/seed_43/reveal/test/records.jsonl)
- B3-nodiff runtime-locked test outputs remain in local ignored run storage; the completion summary and test protocol are documented in the [B3-nodiff worklog](https://github.com/kazunguyen/GRACE-summary/blob/dung/worklogs/2026-11-09_b3_nodiff_test_kaggle_delivery.md).
- [Lịch sử thay đổi sau đăng ký](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/CHANGES_AFTER_PREREG.md)
