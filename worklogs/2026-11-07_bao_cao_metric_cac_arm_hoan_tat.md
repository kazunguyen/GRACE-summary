# Báo cáo kết quả các arm GRACE đã hoàn tất — cập nhật 10/11/2026

**Ngày lập ban đầu:** 08/11/2026<br>
**Cập nhật:** 10/11/2026<br>
**Phạm vi:** B0, B1, B1-full, B1-shuf (seed 42/43/44), B2, B2-flip, B1-H2, B2-rand seed 42/43/44 và ba arm B2-rep, B2-nolabel, B2-labelonly có test đủ trên cả hai dataset; bổ sung kết quả Bước 6 (SUP-LR/MLP/METRIC, P_pre/P_post, sửa–hỏng và routing). B1-full corrected seed42 có 5.006 record và runtime `PASS_LAUNCH_CONTRACT`; B1-shuf đủ 15.018 record và được nghiệm thu runtime theo contract khóa. B2-rand seed44 đã ghép head/tail đủ 5.006; ba arm B2 bàn giao mỗi arm cũng đủ 5.006 nhưng chưa có đủ provenance source/build/native full-offload để chứng nhận theo runtime lock mới. **B3-nodiff test seed42 đã hoàn tất 5.006/5.006** dưới runtime lock, với ngưỡng validation cố định Devign 0,92/ReVeal 0,01; kết quả được thêm ở các bảng dưới và là kết quả của biến thể không có `Key difference`. B3 verified-patch đầy đủ vẫn là run riêng: snapshot status 10/11 00:16 UTC ghi v6 `RUNNING`, 0 record quan sát được; v5 đã dừng trước inference do lỗi notebook. Không gộp hai arm này. Các arm còn lại chưa có đủ output test được xác minh.

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

**Ghi chú metric/provenance B3-nodiff:** các metric @τ được đối soát trực tiếp từ 5.006 record tại τ=0,92/0,01 và khớp MCC/BA/F1/PPR trong shared evaluator. Cột `TP/FP/TN/FN` ở cuối `table_A_metrics.csv` của evaluator hiện là confusion tại **0,5** (code gán từ `m05`), không phải tại τ; vì vậy không dùng các cột đó làm confusion @τ. Confusion đã tính lại từ record tại τ: Devign `TP=714, FP=762, TN=715, FN=541`; ReVeal `TP=167, FP=1.288, TN=756, FN=63`. Devign có một raw response không hợp lệ nhưng score vẫn hợp lệ; cả 5.006 score đều hữu hạn. Không thay ngưỡng sau khi xem test. Threshold được seal từ validation có source runtime SHA `85d877…c5bd6`, trong khi test chạy runtime SHA `bf1f…0ac2e`; audit runtime ghi core inference settings khớp và lock mới thêm pin SciPy. Giữ khác biệt nguồn threshold/runtime này trong provenance, không gọi hai lock là cùng một hash.


Metric từng mẫu, ma trận nhầm lẫn, kiểm tra ID/nhãn, nguồn record và các chênh lệch ghép cặp của các arm đã tích hợp trước đó được lưu trong [workbook metric](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/outputs/metrics_completed_arms_20261107/GRACE_completed_arms_metrics.xlsx). B3-nodiff mới được thêm vào báo cáo này; records, manifests và shared-evaluator output của nó hiện lưu riêng trong `Runs-management/kaggle_outputs_20261110/b3_nodiff_test_runtime_locked/`, chưa được nhập vào workbook. Chênh lệch trong workbook là point estimate; chưa gồm paired bootstrap CI, McNemar hay hiệu chỉnh Holm.

B1-shuf được tính lại từ toàn bộ sáu nhóm records đã tải (15.018/15.018). ID và nhãn khớp frozen test manifest; mọi score hợp lệ và `pred_tau` khớp `s ≥ τ`. Có 2 raw response không hợp lệ trong mỗi seed ReVeal, nhưng score số vẫn hợp lệ và được giữ trong metric. Runtime acceptance và giới hạn provenance được ghi trong [báo cáo nghiệm thu B1-shuf](../Runs-management/b1_shuf_kaggle_output_20261109/RUNTIME_ACCEPTANCE_20261109.md). Các metric trên là descriptive point estimates, không thay thế kiểm định ghép cặp.

## 2. Các câu hỏi ở mục 4 có thể trả lời từ kết quả hiện có

### RQ1 — Với LLM open-weight và giao thức chuẩn, GRACE có hơn zero-shot/đối chứng hằng và đạt mức bài gốc không?

**Trả lời mô tả:** Trong các kết quả Qwen hiện có, B2 không vượt B0 trên MCC hoặc AUROC ở cả hai dataset. MCC của B2 cũng dưới 0,15 trên cả hai dataset. F1 Devign của B2 là 0,5485, thấp hơn mốc luôn đoán vulnerable 0,6295 được nêu trong đề cương. B1-full corrected test cũng không cho cải thiện nhất quán so với B0: ΔMCC là −0,0226 Devign/−0,0025 ReVeal và ΔAUROC là −0,0094/+0,0042. Kết quả này tiếp tục không cho thấy GRACE cải thiện đồng đều theo dataset/metric; so sánh với B0 vẫn mang tính mô tả và các arm không giống nhau về đầu vào.

| Dataset | ΔMCC (B2 − B0) | ΔAUROC (B2 − B0) | MCC B2 | F1 B2 | Đối chiếu F1 luôn đoán vulnerable |
|---|---:|---:|---:|---:|---:|
| Devign | −0,0325 | −0,0100 | 0,0597 | 0,5485 | 0,6295 |
| ReVeal | −0,0229 | −0,0079 | 0,0645 | 0,2005 | 0,1837 |

Kết quả hiện có chỉ trả lời trên backbone Qwen của lượt này; chưa đại diện cho yêu cầu tái lập trên ba backbone trong câu hỏi. So sánh với F1 bài gốc cũng chỉ nên dùng làm tham chiếu vì model và giao thức không đồng nhất.

### RQ2 — Demonstration tác động qua nội dung mã hay qua nhãn đi kèm?

**Trả lời một phần:** Đảo nhãn demo trong B2-flip làm thay đổi dự đoán của **20,3%** mẫu Devign test và **10,7%** mẫu ReVeal test so với B2; MCC giảm 0,0260/0,0273 và AUROC giảm 0,0065/0,0401. Điều này cho thấy dự đoán nhạy với nhãn demo trong phép thử đảo nhãn.

Ba seed B2-rand bổ sung đối chứng demo ngẫu nhiên trên đủ hai dataset. So với B2, AUROC tăng +0,0013/+0,0032/+0,0022 trên Devign và +0,0143/+0,0086/+0,0087 trên ReVeal (s42/s43/s44); AUPRC tăng +0,0105/+0,0125/+0,0150 và +0,0006/+0,0014/+0,0014. Cả sáu ΔAUROC điểm đều nhỏ hơn 0,02 về trị tuyệt đối. Tỷ lệ dự đoán vulnerable giảm rõ: Devign từ 60,2% ở B2 xuống 22,5%/22,0%/21,6%; ReVeal từ 56,1% xuống 19,8%/28,1%/28,1%. Điều này gợi ý demo ngẫu nhiên làm đổi operating point mạnh hơn discrimination trong ba seed đã chạy; chưa có CI để kết luận tương đương thống kê. REVEAL s42/43 được ghép từ hai phiên runtime khác hash; s44 head/tail cùng runtime-lock hash.

Ba arm đã có thêm test. B2-rep trùng prediction B2 ở mọi ID ghép (flip rate 0%); các metric tổng hợp cũng trùng. B2-nolabel so với B1 có ΔAUROC −0,0066 Devign và −0,0120 ReVeal; B2-labelonly so với B1 là +0,0128 và +0,0165. Các độ lớn đều dưới 0,02 nhưng chưa chứng minh tương đương vì thiếu paired CI/kiểm định. Với B2-labelonly, hướng AUROC so với B1 trái dấu với chênh lệch B2−B1 trên cả hai dataset; do đó chưa thể nói arm này tái tạo chênh lệch B2−B1 theo hướng đăng ký trước. **B3-nodiff nay đã có test 5.006/5.006**; so với B2, ΔAUROC điểm là +0,0054 Devign và −0,0090 ReVeal, còn tỷ lệ đoán vulnerable thay đổi −6,15 và +7,87 điểm phần trăm. Đây là biến thể không có `Key difference`, nên chưa trả lời hiệu ứng của khối giải thích so với B3 đầy đủ. B3 verified-patch test v6 vẫn là run riêng; status snapshot 10/11 00:16 UTC ghi `RUNNING` nhưng chưa có record. B3 lịch sử chỉ có validation, không thay thế B3 verified-patch. Các kết quả test là full-census descriptive estimates, không thay thế kiểm định ghép cặp.

**Ý nghĩa cho phần RQ2 trong đề cương:** B3-nodiff cung cấp kết quả test toàn bộ cho biến thể cặp vulnerable/patched nhưng bỏ khối `Key difference`. Kết quả này có thể được báo cáo như một nhánh trong ma trận demonstration; nó chưa cho phép kết luận khối `Key difference` có tác dụng hay không. Phép đối chiếu cần thiết là B3 đầy đủ với B3-nodiff trên cùng target/pair, sau khi có test records của B3 đầy đủ và paired CI.

### RQ3 — LLM có dùng thông tin graph dưới các ngân sách context thực tế không?

**Trả lời một phần:** So với B0, B1 không cho mức cải thiện nhất quán: ΔMCC (B1 − B0) là −0,0134 trên Devign và −0,0351 trên ReVeal; ΔAUROC lần lượt −0,0070 và +0,0101. B1-H2 so với B1 có ΔMCC −0,0133 trên Devign và +0,0569 trên ReVeal; ΔAUROC +0,0142 và +0,0115. B1-full corrected so với B1 cho ΔMCC −0,0092/+0,0326 và ΔAUROC −0,0024/−0,0059 (Devign/ReVeal); AUROC không tăng ở cả hai dataset dù tỷ lệ dự đoán 1 trên ReVeal tăng 33,2 điểm phần trăm. B1-shuf nay đã đủ test ba seed. So với B1, ΔAUROC (B1 − B1-shuf) lần lượt là −0,0096/−0,0008/−0,0016 trên Devign và +0,0064/+0,0043/+0,0158 trên ReVeal (seed 42/43/44); mọi point estimate đều nằm trong ±0,02. Đây là so sánh mô tả; chưa có paired cluster-bootstrap CI và seed B1-shuf được chọn ngưỡng riêng trên validation. B1-full cũng là corrected renderer thay prompt ở 4.753/5.006 mẫu và dùng tau khác B1, nên không cô lập riêng tác dụng của ngân sách graph. Chưa thể kết luận H3.1 theo tiêu chí đăng ký nếu thiếu CI.

Đã có kết quả test B1-shuf làm đối chứng graph nhiễu; các chênh lệch AUROC điểm so với B1 nhỏ (|Δ| ≤0,0158). Tuy vậy B1-full dùng corrected renderer và các seed B1-shuf có tau riêng theo validation. Cần paired cluster-bootstrap CI theo protocol trước khi kết luận liệu nội dung graph có đóng góp hay không.

### RQ4 — Các biến thể khác nhau về khả năng phân biệt hay chỉ dịch chuyển điểm hoạt động?

**Trả lời mô tả cho các arm hiện có:** Với B1→B2 trên Devign, AUROC giảm 0,0030 và AUPRC giảm 0,0167, trong khi tỷ lệ dự đoán vulnerable tăng 38,1 điểm phần trăm. Trên ReVeal, AUROC giảm 0,0179 và AUPRC giảm 0,0018, còn tỷ lệ dự đoán vulnerable tăng 32,3 điểm phần trăm. Mẫu này gợi ý rằng thêm demo truy hồi làm thay đổi mạnh điểm hoạt động nhưng không cải thiện khả năng phân biệt trong các phép so này.

Trong các arm có test, AUROC cao nhất vẫn là 0,6005 (B2-labelonly trên ReVeal), thấp hơn 0,62. B2-rand seed42/43/44 đều ≤0,5805 trên cả hai dataset. B1-full so với B1 cũng cho AUROC giảm nhẹ ở cả hai dataset (−0,0024 Devign; −0,0059 ReVeal), trong khi tỷ lệ dự đoán 1 giảm 2,9 điểm phần trăm ở Devign và tăng 33,2 điểm ở ReVeal. B2-rand và B1-full đều gợi ý operating point có thể thay đổi mà không có cải thiện discrimination rõ; đây vẫn là point estimate, không thay thế phép đánh giá toàn ma trận và cần CI ghép cặp.

B3-nodiff so với B2 cho ΔAUROC **+0,0054** ở Devign và **−0,0090** ở ReVeal; cả hai point estimate nằm trong ±0,02. Tuy nhiên, tỷ lệ đoán vulnerable @ngưỡng đã khóa là **54,03% so với 60,18%** ở Devign (−6,15 điểm) và **63,98% so với 56,11%** ở ReVeal (+7,87 điểm). Hướng thay đổi khác nhau theo dataset và không đạt mức tăng ≥10 điểm ở dataset nào. Đây là so sánh mô tả với B2 lịch sử, chưa được chứng nhận theo runtime lock hiện hành. Chưa thể kết luận “chỉ dịch chuyển operating point”: chưa có paired cluster-bootstrap CI, ngưỡng riêng của mỗi arm ảnh hưởng PPR, và B3 đầy đủ vẫn chưa có test output.

### RQ5 — Mốc có giám sát và giá trị bổ sung của LLM (Step 6)

**Tiến độ:** Đã chạy xong notebook huấn luyện ba anchor SUP-LR, SUP-MLP, SUP-METRIC trên hai dataset, ba seed (42/43/44), chọn ngưỡng trên validation và xuất `anchor_scores.csv` cùng `anchor_summary.json`. Đã chạy phân tích offline ghép B2, H3-B và SUP-LR theo ID/nhãn; các đầu ra đã được khóa dưới `STEP6_supervised_anchors/runs/complementarity_step6/step6_lock_64fb2c99d904_bba04c65/`. Kết quả định lượng bên dưới là trên test, dùng ngưỡng chọn từ validation; paired cluster bootstrap dùng 5.000 lượt, đơn vị cụm là commit_id (Devign) và file/code hash (ReVeal).

**P_pre/P_post — H5.2:** Trên test, ΔMCC (P_post−P_pre) là **−0,0015**, CI 95% [−0,0122; 0,0093] ở Devign và **−0,0242**, CI 95% [−0,0550; 0,0047] ở ReVeal. Cận trên CI ở cả hai dataset thấp hơn δ=0,02; kết quả hiện có không cho thấy lợi ích đạt biên ý nghĩa đã đăng ký. AUROC cũng gần như không đổi: 0,7136→0,7120 ở Devign và 0,8094→0,8089 ở ReVeal. Diễn giải là chưa có bằng chứng về mức tăng MCC ≥0,02, không phải chứng minh tác động bằng không.

**Điểm cần chốt về giao thức H5.2:** đề cương mô tả “cùng ngưỡng”, trong khi `complementarity_step6.json` ghi ngưỡng validation OOF riêng cho hai meta-model: Devign P_pre=0,53/P_post=0,52; ReVeal cả hai=0,15. Vì vậy CI hiện tại trả lời phép so cặp theo ngưỡng đã chọn riêng; nếu “cùng ngưỡng” trong preregistration yêu cầu một ngưỡng dùng chung cho P_pre/P_post, cần bổ sung phép chạy đó trước khi tuyên bố H5.2 đã được adjudicate hoàn toàn theo đúng protocol.

**Sửa–hỏng:** Khi so B2 với H3-B gate, Devign có 397 ca sửa và 718 ca hỏng; ReVeal có 164 ca sửa và 875 ca hỏng. Theo lớp, Devign: y=0 sửa/hỏng 255/422, y=1 là 142/296; ReVeal: y=0 là 99/819, y=1 là 65/56. Số ca sửa riêng lẻ không chứng minh phối hợp có ích vì số ca hỏng cũng lớn. H3-B gate đạt MCC 0,2895 Devign và 0,3534 ReVeal ở ngưỡng khóa; đây là đối chứng mạnh để định vị kết quả LLM.

**Routing — H5.3:** Ở ngân sách 10%, benefit-router của H3-B so với confidence-router có ΔMCC **+0,0148** (CI 95% [−0,0062; 0,0357]) trên Devign, chưa phân biệt được lợi ích; trên ReVeal ΔMCC **−0,0509** (CI 95% [−0,1049; −0,0002]), bất lợi so với confidence trong phép chạy này. So với 20 lượt random, balanced accuracy benefit-router là 0,648 ở Devign (random mean 0,628; khoảng min–max 0,621–0,634) và 0,640 ở ReVeal (random mean 0,689; 0,676–0,700). Đây là đối chiếu mô tả: preregistration H5.3 yêu cầu CI của Δbalanced accuracy (benefit−random) có cận trên <0,01 và đối chiếu số ca sửa với expert ngẫu nhiên; verdict hiện có trong JSON lại là ΔMCC benefit−confidence. Chưa đủ để kết luận H5.3 theo đúng tiêu chí đăng ký.

**H5.1 — mốc có giám sát thắng rõ:** Các anchor đã được huấn luyện và có điểm số test. Phân tích hiện có cho thấy SUP-LR trên Devign có MCC 0,2190 và AUROC 0,6559; AUROC thấp hơn ngưỡng 0,68 của H5.1. Tuy nhiên, đầu ra đang ghi không có CI ghép cặp ΔMCC(SUP-LR−B2) theo đúng định nghĩa giả thuyết, nên chưa adjudicate H5.1 trên cả hai dataset. Không kết luận “SUP-LR thắng rõ” chỉ từ so sánh point estimate.

**Phạm vi RQ:** Step 6 cung cấp bằng chứng cho RQ5/H5.1–H5.3. Nó không tự trả lời RQ1–RQ4 về backbone, demonstration, graph hay phân biệt/ngưỡng. RQ6 còn cần chấm mù relevance của demo và các gói audit thủ công; bảng sửa–hỏng không thay thế những đánh giá đó. Các kiểm định toàn chiến dịch (mọi arm, McNemar, Holm và CI theo protocol chung) cũng chưa hoàn tất.

## 3. Đối chiếu các giả thuyết đăng ký trước ở mục 4.3

| Giả thuyết | Tiêu chí chính trong đề cương | Đối chiếu với kết quả hiện có | Trạng thái |
|---|---|---|---|
| **H1.1** — B2 không vượt B0 | Cận trên CI của ΔMCC (B2−B0) < 0,03 và ΔAUROC < 0,02 trên cả hai dataset | Point estimate ΔMCC là −0,0325/−0,0229; ΔAUROC là −0,0100/−0,0079 (Devign/ReVeal). Chưa có CI ghép cặp nên chưa kiểm tra được tiêu chí cận trên. | **Chưa kết luận theo quy tắc đăng ký; point estimate phù hợp hướng dự đoán.** |
| **H1.2** — GRACE không đạt mức bài gốc | MCC B2 < 0,15 trên cả hai dataset; F1 Devign thấp hơn luôn đoán vulnerable | MCC B2: 0,0597 Devign và 0,0645 ReVeal. F1 Devign: 0,5485 so với mốc 0,6295. | **Các điều kiện số học của giả thuyết đạt trên kết quả test hiện có.** |
| **H2.1** — Demo tác động qua nhãn | Net label sensitivity (B2 so với B2-flip trừ biến động B2-rep) ≥ 15 điểm phần trăm | B2-rep/B2 có tỷ lệ đổi prediction 0% ở cả hai dataset. B2/B2-flip đổi 20,3% Devign và 10,7% ReVeal; net point estimate vì vậy là 20,3 và 10,7 điểm phần trăm. | **Đạt ngưỡng point estimate ở Devign nhưng không ở ReVeal; chưa có CI và không đồng nhất giữa hai dataset.** |
| **H2.2** — Nội dung demo không mang tín hiệu | Cận trên CI của ΔAUROC B2−B2-rand và B2-nolabel−B1 <0,02; B2-labelonly tái tạo ≥80% chênh lệch B2−B1 | B2-rand s42/43/44, B2-nolabel và B2-labelonly đều đủ test. Các ΔAUROC điểm B2−B2-rand và B2-nolabel−B1 nằm trong ±0,02 trên từng dataset. Tuy nhiên B2-labelonly−B1 mang dấu ngược với B2−B1 trên cả Devign lẫn ReVeal, nên không tái tạo gap theo hướng dự đoán. Chưa có CI; REVEAL s42/43 vẫn có khác runtime hash giữa các phiên ghép. | **Chưa kết luận giả thuyết: một số point estimate nhỏ, nhưng thiếu CI và vế tái tạo gap không được hỗ trợ theo hướng.** |
| **H2.3** — Cặp tương phản chỉ dịch chuyển điểm hoạt động | Tỷ lệ dự đoán 1 của B3 cao hơn B2 ≥10 điểm; cận trên CI của ΔAUROC B3−B2 <0,02 | B3-nodiff test đầy đủ. So với B2, PPR @τ thay đổi −6,15 điểm Devign (54,03%−60,18%) và +7,87 điểm ReVeal (63,98%−56,11%); không đạt tăng ≥10 điểm trên điểm ước lượng ở dataset nào. ΔAUROC (B3-nodiff−B2) là +0,0054/−0,0090. Chưa có CI ghép cặp; B3 đầy đủ có `Key difference` là run riêng, hiện chưa có record test. B2 là kết quả lịch sử, chưa được chứng nhận theo runtime lock hiện hành. | **Chưa adjudicate H2.3: điều kiện PPR không đạt ở point estimate của B3-nodiff; điều kiện CI chưa kiểm tra và kết quả này không thay cho B3 đầy đủ.** |
| **H3.1** — LLM không đọc graph | Cận trên CI của ΔAUROC B1−B0 và B1−B1-shuf <0,02; B1-H2 không khác B1 theo cùng tiêu chí | Point estimate ΔAUROC B1−B0 là −0,0070 Devign và +0,0101 ReVeal; B1-H2−B1 là +0,0142/+0,0115; B1-full−B1 là −0,0024/−0,0059. B1-shuf đã đủ ba seed; ΔAUROC B1−B1-shuf là −0,0096/−0,0008/−0,0016 Devign và +0,0064/+0,0043/+0,0158 ReVeal. Chưa có CI ghép cặp. | **Chưa kết luận theo tiêu chí đăng ký; cần paired cluster-bootstrap CI.** |
| **H4.1** — Pipeline LLM gần ngẫu nhiên khi đo không ngưỡng | AUROC mọi arm LLM ≤0,62 | Các arm đã có test, nay gồm cả B3-nodiff (0,5359 Devign; 0,5572 ReVeal), đều có AUROC ≤0,6006. Nhiều arm trong toàn ma trận chưa có kết quả. | **Phù hợp trong phạm vi arm đã có test; chưa xác nhận toàn ma trận.** |
| **H5.1** — Mốc có giám sát thắng rõ | ΔMCC (SUP-LR−B2) ≥0,15 với CI không chứa 0; AUROC SUP-LR ≥0,68 | Anchor đã chạy. SUP-LR Devign có AUROC 0,6559 (<0,68); đầu ra hiện có chưa báo CI ghép cặp ΔMCC theo tiêu chí H5.1. | **Chưa được ủng hộ trên Devign; chưa adjudicate đầy đủ trên cả hai dataset do thiếu CI đúng phép so.** |
| **H5.2** — LLM không bổ sung tín hiệu sau truy vấn | Cận trên CI của ΔMCC (P_post−P_pre) <0,02; cùng đặc trưng nền, fold và ngưỡng | ΔMCC test: −0,0015 [−0,0122; 0,0093] Devign; −0,0242 [−0,0550; 0,0047] ReVeal. Cả hai cận trên <0,02. Ngưỡng hiện được chọn riêng cho P_pre/P_post (0,53/0,52 Devign; 0,15/0,15 ReVeal), cần đối chiếu yêu cầu “cùng ngưỡng” trong đề cương. | **Ủng hộ theo biên δ với giao thức đang chạy; cần làm rõ/chạy phép cùng ngưỡng để xác nhận khớp hoàn toàn preregistration.** |
| **H5.3** — Không biết trước khi nào nên gọi LLM | Ở ngân sách 10%, cận trên CI của Δbalanced accuracy (benefit-router−random) <0,01; đối chiếu số ca sửa đúng với expert ngẫu nhiên | Có routing 5/10/25%, random 20 seed và so sánh benefit−confidence. Tuy nhiên CI/verdict hiện có là ΔMCC benefit−confidence; chưa thấy kiểm định CI Δbalanced accuracy benefit−random và tiêu chí số ca sửa theo đúng H5.3. | **Có kết quả chẩn đoán nhưng chưa adjudicate theo tiêu chí đăng ký.** |
| **H6.1** — Demo hiếm khi đúng cơ chế; liên quan không kéo theo đúng | Tỷ lệ “Neither” Devign ≥40%; CI chênh lệch accuracy giữa nhóm liên quan/không liên quan chứa 0 | Cần kết quả chấm mù và phân tích theo nhóm liên quan; các metric inference không thay thế được dữ liệu này. | **Chưa đánh giá.** |

### Kết luận ngắn

Trong phạm vi các kết quả hiện có, B1-full corrected và B1-shuf đều đủ test; các so sánh graph vẫn cần CI ghép cụm. B3-nodiff nay cũng đủ test 5.006 mẫu. So với B2 lịch sử, AUROC điểm của B3-nodiff gần nhau (Δ=+0,0054 Devign/−0,0090 ReVeal), nhưng tỷ lệ vulnerable dự đoán thay đổi trái hướng giữa hai dataset (−6,15/+7,87 điểm) và không đạt mức tăng 10 điểm của H2.3. Vì chưa có CI và B3 đầy đủ chưa có test records, H2.3 chưa được adjudicate; kết quả không cô lập được tác dụng riêng của `Key difference`. B2-rep trùng prediction B2; B2-rand có AUROC gần B2 nhưng operating point khác; B2-labelonly không tái tạo chênh lệch B2−B1 theo hướng dự đoán. B2 không vượt B0 trên MCC/AUROC; điều kiện số học H1.2 đạt trên B2 và H4.1 tiếp tục phù hợp trong phạm vi arm có test, nay bao gồm cả B3-nodiff. H2.1 đạt point estimate ở Devign nhưng không ở ReVeal; H2.2 vẫn thiếu CI. **Step 6** giữ các giới hạn đã nêu cho H5.1–H5.3; RQ6 và các giả thuyết cần chấm mù vẫn để mở.

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
- [B1-shuf full-test runtime acceptance](../Runs-management/b1_shuf_kaggle_output_20261109/RUNTIME_ACCEPTANCE_20261109.md)
- [Current arm status and B3 test readiness](../Runs-management/ARM_STATUS_AND_REMAINING_WORK_20261110.md)
- [RUNS.md — lượt I-20 và tình trạng đủ 5.006 test record mỗi seed](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/Runs-management/RUNS.md)
- [B2-rand merged evaluation summary](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/06_Arm_B2_Rand/test_results_20261107/evaluation_summary.json) · [Provenance và runtime hashes](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/06_Arm_B2_Rand/test_results_20261107/provenance.json)
- [Step 6 lock và protocol](../STEP6_supervised_anchors/step6_lock.json) · [Anchor scores và summaries](../STEP6_supervised_anchors/runs/anchor/locked_step6_20261108/) · [Phân tích complementarity đã khóa](../STEP6_supervised_anchors/runs/complementarity_step6/step6_lock_64fb2c99d904_bba04c65/)
- [B2-rand test records — seed 42 Devign](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/06_Arm_B2_Rand/test_results_20261107/seed_42/devign/test/records.jsonl) · [seed 42 ReVeal](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/06_Arm_B2_Rand/test_results_20261107/seed_42/reveal/test/records.jsonl)
- [B2-rand test records — seed 43 Devign](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/06_Arm_B2_Rand/test_results_20261107/seed_43/devign/test/records.jsonl) · [seed 43 ReVeal](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/06_Arm_B2_Rand/test_results_20261107/seed_43/reveal/test/records.jsonl)
- [B3-nodiff test output and shared evaluator metrics](../Runs-management/kaggle_outputs_20261110/b3_nodiff_test_runtime_locked/b3_nodiff_test/shared_evaluator_output/table_A_metrics.csv) · [batch completion/locked thresholds](../Runs-management/kaggle_outputs_20261110/b3_nodiff_test_runtime_locked/b3_nodiff_test/batch_summary.json) · [completion worklog](2026-11-10_b3_nodiff_test_completed.md)
- [Lịch sử thay đổi sau đăng ký](https://github.com/kazunguyen/GRACE-summary/blob/baseline-unified/CHANGES_AFTER_PREREG.md)
