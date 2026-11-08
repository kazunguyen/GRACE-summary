# Báo cáo kết quả các arm GRACE đã hoàn tất — cập nhật 08/11/2026

**Ngày:** 08/11/2026<br>
**Phạm vi:** B0, B1, B2, B2-flip, B1-H2, B2-rand seed 42/43/44 và ba arm B2-rep, B2-nolabel, B2-labelonly có đủ validation/test trên cả hai dataset. B2-rand seed44 đã ghép head/tail đủ 5.006 test record; ba arm B2 mới mỗi arm cũng đủ 5.006. Tính toàn vẹn tính toán, ID/nhãn, logprob/score, ngưỡng và manifest đã được kiểm tra; tuy nhiên provenance source/build/native full-offload của ba arm bàn giao còn thiếu nên chưa chứng nhận đầy đủ theo runtime lock mới. Các arm còn lại chưa có đủ output được xác minh để đưa vào bảng.

## 1. Ngưỡng và metric của các arm đã hoàn tất

### 1.1. Ngưỡng áp dụng

| Arm | Dataset | Ngưỡng τ | Cơ sở chọn ngưỡng |
|---|---|---:|---|
| B0 | Devign | 0,98 | Tối ưu MCC trên full validation; hiệu chỉnh hồi cứu |
| B0 | ReVeal | 0,30 | Tối ưu MCC trên full validation; hiệu chỉnh hồi cứu |
| B1 | Devign | 0,98 | Tối ưu MCC trên full validation; hiệu chỉnh hồi cứu |
| B1 | ReVeal | 0,63 | Tối ưu MCC trên full validation; hiệu chỉnh hồi cứu |
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
| Devign | B2-rand s44 | 2.732 | 0 | 0,0589 | 0,5327 | 0,5006 | 0,3295 | 0,5243 | 0,5153 | 0,2422 | 0,2160 |
| ReVeal | B2-rand s44 | 2.274 | 0 | 0,0665 | 0,5748 | 0,1235 | 0,1959 | 0,5495 | 0,1332 | 0,3696 | 0,2806 |


Metric từng mẫu, ma trận nhầm lẫn, kiểm tra ID/nhãn, nguồn record và các chênh lệch ghép cặp được lưu trong [workbook metric](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/outputs/metrics_completed_arms_20261107/GRACE_completed_arms_metrics.xlsx). Chênh lệch trong workbook là point estimate; chưa gồm paired bootstrap CI, McNemar hay hiệu chỉnh Holm.

## 2. Các câu hỏi ở mục 4 có thể trả lời từ kết quả hiện có

### RQ1 — Với LLM open-weight và giao thức chuẩn, GRACE có hơn zero-shot/đối chứng hằng và đạt mức bài gốc không?

**Trả lời mô tả:** Trong các kết quả Qwen hiện có, B2 không vượt B0 trên MCC hoặc AUROC ở cả hai dataset. MCC của B2 cũng dưới 0,15 trên cả hai dataset. F1 Devign của B2 là 0,5485, thấp hơn mốc luôn đoán vulnerable 0,6295 được nêu trong đề cương. Kết quả này phù hợp với nhận định rằng cấu hình GRACE đang xét không cải thiện zero-shot theo các metric này.

| Dataset | ΔMCC (B2 − B0) | ΔAUROC (B2 − B0) | MCC B2 | F1 B2 | Đối chiếu F1 luôn đoán vulnerable |
|---|---:|---:|---:|---:|---:|
| Devign | −0,0325 | −0,0100 | 0,0597 | 0,5485 | 0,6295 |
| ReVeal | −0,0229 | −0,0079 | 0,0645 | 0,2005 | 0,1837 |

Kết quả hiện có chỉ trả lời trên backbone Qwen của lượt này; chưa đại diện cho yêu cầu tái lập trên ba backbone trong câu hỏi. So sánh với F1 bài gốc cũng chỉ nên dùng làm tham chiếu vì model và giao thức không đồng nhất.

### RQ2 — Demonstration tác động qua nội dung mã hay qua nhãn đi kèm?

**Trả lời một phần:** Đảo nhãn demo trong B2-flip làm thay đổi dự đoán của **20,3%** mẫu Devign test và **10,7%** mẫu ReVeal test so với B2; MCC giảm 0,0260/0,0273 và AUROC giảm 0,0065/0,0401. Điều này cho thấy dự đoán nhạy với nhãn demo trong phép thử đảo nhãn.

Ba seed B2-rand bổ sung đối chứng demo ngẫu nhiên trên đủ hai dataset. So với B2, AUROC tăng +0,0013/+0,0032/+0,0022 trên Devign và +0,0143/+0,0086/+0,0087 trên ReVeal (s42/s43/s44); AUPRC tăng +0,0105/+0,0125/+0,0150 và +0,0006/+0,0014/+0,0014. Cả sáu ΔAUROC điểm đều nhỏ hơn 0,02 về trị tuyệt đối. Tỷ lệ dự đoán vulnerable giảm rõ: Devign từ 60,2% ở B2 xuống 22,5%/22,0%/21,6%; ReVeal từ 56,1% xuống 19,8%/28,1%/28,1%. Điều này gợi ý demo ngẫu nhiên làm đổi operating point mạnh hơn discrimination trong ba seed đã chạy; chưa có CI để kết luận tương đương thống kê. REVEAL s42/43 được ghép từ hai phiên runtime khác hash; s44 head/tail cùng runtime-lock hash.

Ba arm đã có thêm test. B2-rep trùng prediction B2 ở mọi ID ghép (flip rate 0%); các metric tổng hợp cũng trùng. B2-nolabel so với B1 có ΔAUROC −0,0066 Devign và −0,0120 ReVeal; B2-labelonly so với B1 là +0,0128 và +0,0165. Các độ lớn đều dưới 0,02 nhưng chưa chứng minh tương đương vì thiếu paired CI/kiểm định. Với B2-labelonly, hướng AUROC so với B1 trái dấu với chênh lệch B2−B1 trên cả hai dataset; do đó chưa thể nói arm này tái tạo chênh lệch B2−B1 theo hướng đăng ký trước. Chưa có B3 hoàn tất. Các kết quả mới là full-census mô tả nhưng có giới hạn runtime provenance nêu trên.

### RQ3 — LLM có dùng thông tin graph dưới các ngân sách context thực tế không?

**Trả lời một phần:** So với B0, B1 không cho mức cải thiện nhất quán: ΔMCC (B1 − B0) là −0,0134 trên Devign và −0,0351 trên ReVeal; ΔAUROC lần lượt −0,0070 và +0,0101. B1-H2 so với B1 có ΔMCC −0,0133 trên Devign và +0,0569 trên ReVeal; ΔAUROC +0,0142 và +0,0115.

Các kết quả cho biết hiệu năng của những cách đóng gói graph đã chạy, nhưng chưa cô lập tác dụng của **nội dung graph**. Cần B1-shuf làm đối chứng graph nhiễu; B1-full cũng cần để đánh giá cách dùng đầy ngân sách. Vì vậy chưa thể trả lời dứt điểm liệu LLM có đọc và dùng graph hay không.

### RQ4 — Các biến thể khác nhau về khả năng phân biệt hay chỉ dịch chuyển điểm hoạt động?

**Trả lời mô tả cho các arm hiện có:** Với B1→B2 trên Devign, AUROC giảm 0,0030 và AUPRC giảm 0,0167, trong khi tỷ lệ dự đoán vulnerable tăng 38,1 điểm phần trăm. Trên ReVeal, AUROC giảm 0,0179 và AUPRC giảm 0,0018, còn tỷ lệ dự đoán vulnerable tăng 32,3 điểm phần trăm. Mẫu này gợi ý rằng thêm demo truy hồi làm thay đổi mạnh điểm hoạt động nhưng không cải thiện khả năng phân biệt trong các phép so này.

Trong các arm có test, AUROC cao nhất vẫn là 0,6005 (B2-labelonly trên ReVeal), thấp hơn 0,62. B2-rand seed42/43/44 đều ≤0,5805 trên cả hai dataset. B2-rand củng cố quan sát rằng discrimination gần B2 trong khi thresholded operating point thay đổi mạnh. Đây là kết quả của các arm hiện có, không thay thế phép đánh giá toàn ma trận; các kết luận vẫn là mô tả và cần CI ghép cặp.

## 3. Đối chiếu các giả thuyết đăng ký trước ở mục 4.3

| Giả thuyết | Tiêu chí chính trong đề cương | Đối chiếu với kết quả hiện có | Trạng thái |
|---|---|---|---|
| **H1.1** — B2 không vượt B0 | Cận trên CI của ΔMCC (B2−B0) < 0,03 và ΔAUROC < 0,02 trên cả hai dataset | Point estimate ΔMCC là −0,0325/−0,0229; ΔAUROC là −0,0100/−0,0079 (Devign/ReVeal). Chưa có CI ghép cặp nên chưa kiểm tra được tiêu chí cận trên. | **Chưa kết luận theo quy tắc đăng ký; point estimate phù hợp hướng dự đoán.** |
| **H1.2** — GRACE không đạt mức bài gốc | MCC B2 < 0,15 trên cả hai dataset; F1 Devign thấp hơn luôn đoán vulnerable | MCC B2: 0,0597 Devign và 0,0645 ReVeal. F1 Devign: 0,5485 so với mốc 0,6295. | **Các điều kiện số học của giả thuyết đạt trên kết quả test hiện có.** |
| **H2.1** — Demo tác động qua nhãn | Net label sensitivity (B2 so với B2-flip trừ biến động B2-rep) ≥ 15 điểm phần trăm | B2-rep/B2 có tỷ lệ đổi prediction 0% ở cả hai dataset. B2/B2-flip đổi 20,3% Devign và 10,7% ReVeal; net point estimate vì vậy là 20,3 và 10,7 điểm phần trăm. | **Đạt ngưỡng point estimate ở Devign nhưng không ở ReVeal; chưa có CI và không đồng nhất giữa hai dataset.** |
| **H2.2** — Nội dung demo không mang tín hiệu | Cận trên CI của ΔAUROC B2−B2-rand và B2-nolabel−B1 <0,02; B2-labelonly tái tạo ≥80% chênh lệch B2−B1 | B2-rand s42/43/44, B2-nolabel và B2-labelonly đều đủ test. Các ΔAUROC điểm B2−B2-rand và B2-nolabel−B1 nằm trong ±0,02 trên từng dataset. Tuy nhiên B2-labelonly−B1 mang dấu ngược với B2−B1 trên cả Devign lẫn ReVeal, nên không tái tạo gap theo hướng dự đoán. Chưa có CI; REVEAL s42/43 vẫn có khác runtime hash giữa các phiên ghép. | **Chưa kết luận giả thuyết: một số point estimate nhỏ, nhưng thiếu CI và vế tái tạo gap không được hỗ trợ theo hướng.** |
| **H2.3** — Cặp tương phản chỉ dịch chuyển điểm hoạt động | Tỷ lệ dự đoán 1 của B3 cao hơn B2 ≥10 điểm; cận trên CI của ΔAUROC B3−B2 <0,02 | Chưa có B3 hoàn tất. | **Chưa đánh giá.** |
| **H3.1** — LLM không đọc graph | Cận trên CI của ΔAUROC B1−B0 và B1−B1-shuf <0,02; B1-H2 không khác B1 theo cùng tiêu chí | Point estimate ΔAUROC B1−B0 là −0,0070 Devign và +0,0101 ReVeal; B1-H2−B1 là +0,0142 và +0,0115. Chưa có CI và chưa có B1-shuf hoàn tất. | **Chưa kết luận theo tiêu chí đăng ký.** |
| **H4.1** — Pipeline LLM gần ngẫu nhiên khi đo không ngưỡng | AUROC mọi arm LLM ≤0,62 | Tất cả arm có test trong báo cáo, gồm B2-rep/nolabel/labelonly và B2-rand s42/43/44, đều có AUROC ≤0,6006. Nhiều arm trong toàn ma trận chưa có kết quả. | **Phù hợp trong phạm vi arm đã có test; chưa xác nhận toàn ma trận.** |
| **H5.1** — Mốc có giám sát thắng rõ | ΔMCC (SUP-LR−B2) ≥0,15 với CI không chứa 0; AUROC SUP-LR ≥0,68 | Workbook này không có kết quả SUP-LR. | **Chưa đánh giá từ các arm trong báo cáo.** |
| **H5.2** — LLM không bổ sung tín hiệu sau truy vấn | Cận trên CI của ΔMCC (P_post−P_pre) <0,02 | Chưa có kết quả P_pre/P_post tương ứng trong bộ metric này. | **Chưa đánh giá.** |
| **H5.3** — Không biết trước khi nào nên gọi LLM | Ở ngân sách 10%, cận trên CI của Δbalanced accuracy (benefit-router−random) <0,01; đối chiếu số ca sửa đúng với expert ngẫu nhiên | Chưa có kết quả router và đối chứng ngẫu nhiên trong workbook. | **Chưa đánh giá.** |
| **H6.1** — Demo hiếm khi đúng cơ chế; liên quan không kéo theo đúng | Tỷ lệ “Neither” Devign ≥40%; CI chênh lệch accuracy giữa nhóm liên quan/không liên quan chứa 0 | Cần kết quả chấm mù và phân tích theo nhóm liên quan; các metric inference không thay thế được dữ liệu này. | **Chưa đánh giá.** |

### Kết luận ngắn

Trong phạm vi các kết quả hiện có, B2-rep trùng prediction B2, B2-nolabel/B2-labelonly có đủ test, và B2-rand đã đủ ba seed. B2-rand cả ba seed có AUROC gần B2 trong khi tỷ lệ dự đoán positive giảm đáng kể. Chênh lệch AUROC B2-nolabel/B2-labelonly so với B1 nhỏ về trị tuyệt đối, nhưng B2-labelonly trái hướng với gap B2−B1; chưa xác nhận H2.2 vì thiếu CI ghép cặp. B2 không vượt B0 trên MCC/AUROC; H1.2 đạt điều kiện số học trên kết quả test; H4.1 phù hợp trong phạm vi arm đã có test. H2.1 đạt ngưỡng point estimate ở Devign nhưng không ở ReVeal. Các giả thuyết cần B3, supervised/meta-model, router hoặc chấm mù vẫn để mở. Lưu ý ba arm mới có giới hạn provenance runtime như đã nêu.

**Giới hạn suy luận:** Bản này tổng hợp point estimates, không phải bảng xác nhận thống kê. Chưa tính paired cluster bootstrap CI, McNemar hoặc hiệu chỉnh Holm cho các đối chiếu. Kết quả B0/B1 dùng ngưỡng hiệu chỉnh hồi cứu; mọi mức độ tiếp xúc test cần được giữ trong báo cáo cuối.

## Nguồn và khả năng truy xuất

- [Đề cương nghiên cứu, mục 4 và 4.3](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/docs/OSF_response/De_cuong_nghien_cuu_GRACE_hop_nhat.docx)
- [Workbook metric và paired deltas](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/outputs/metrics_completed_arms_20261107/GRACE_completed_arms_metrics.xlsx)
- [Ledger các lượt inference](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/Runs-management/RUNS.md)
- [Khóa threshold validation B1-H2 trên Kaggle](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/Runs-management/b1h2_kaggle_validation_threshold_lock_20261106.json)
- [Báo cáo hoàn tất B1-H2 test và trạng thái B2-rand](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/worklogs/2026-11-07_b1h2_b2rand_kaggle_progress_and_delivery.md)
- [Worklog hoàn tất test B2-rand seed 42/43](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/worklogs/2026-11-07_b2_rand_seed42_seed43_test_complete.md)
- [B2-rand seed44 merged evaluation](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/06_Arm_B2_Rand/test_results_20261107/seed_44/evaluation_summary.json)
- [Hồ sơ nghiệm thu và metric test B2-rep/B2-nolabel/B2-labelonly](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/Runs-management/run_handoff_20261108/RUN_STATUS.md)
- [RUNS.md — lượt I-20 và tình trạng đủ 5.006 test record mỗi seed](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/Runs-management/RUNS.md)
- [B2-rand merged evaluation summary](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/06_Arm_B2_Rand/test_results_20261107/evaluation_summary.json) · [Provenance và runtime hashes](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/06_Arm_B2_Rand/test_results_20261107/provenance.json)
- [B2-rand test records — seed 42 Devign](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/06_Arm_B2_Rand/test_results_20261107/seed_42/devign/test/records.jsonl) · [seed 42 ReVeal](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/06_Arm_B2_Rand/test_results_20261107/seed_42/reveal/test/records.jsonl)
- [B2-rand test records — seed 43 Devign](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/06_Arm_B2_Rand/test_results_20261107/seed_43/devign/test/records.jsonl) · [seed 43 ReVeal](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/06_Arm_B2_Rand/test_results_20261107/seed_43/reveal/test/records.jsonl)
- [Lịch sử thay đổi sau đăng ký](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/CHANGES_AFTER_PREREG.md)
