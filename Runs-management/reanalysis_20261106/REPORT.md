# Tính lại kết quả GRACE từ records ngày 06/11/2026

Phân tích hậu nghiệm theo yêu cầu người dùng. B0/B1/B2/B2-flip đã đủ validation và test trên Devign và ReVeal. Dùng 40.044 records; không chọn ngưỡng từ test và không dùng các giá trị của file ngưỡng preregistration để fit.

B0/B1/B2 chọn ngưỡng riêng từ toàn bộ validation bằng grace_diag.stats.pick_threshold, lưới 0,01–0,99 bước 0,01, MCC không xác định bị bỏ qua, hòa thì gần 0,5. B2-flip kế thừa ngưỡng vừa tính lại của B2. Chỉ lọc score valid; raw greedy không phải 0/1 được đếm riêng và không loại score hữu hạn.

Đã kiểm tra đủ ID duy nhất, nhãn khớp manifest, score hữu hạn và s khớp sigmoid(logprob_1-logprob_0) với sai số <1e-10 cho từng record. AP dùng sklearn.average_precision_score để xử lý đồng hạng score.

## Ngưỡng validation

| Dataset | Arm | n validation | tau | MCC validation tại tau | Chính sách |
|---|---|---:|---:|---:|---|
| devign | B0 | 2732 | 0.98 | 0.076010 | full_validation_argmax_MCC_grid_0.01_0.99 |
| devign | B1 | 2732 | 0.98 | 0.074755 | full_validation_argmax_MCC_grid_0.01_0.99 |
| devign | B2 | 2732 | 0.70 | 0.054734 | full_validation_argmax_MCC_grid_0.01_0.99 |
| devign | B2-flip | 2732 | 0.70 | 0.002455 | inherit_recomputed_B2 |
| reveal | B0 | 2273 | 0.30 | 0.080120 | full_validation_argmax_MCC_grid_0.01_0.99 |
| reveal | B1 | 2273 | 0.63 | 0.083264 | full_validation_argmax_MCC_grid_0.01_0.99 |
| reveal | B2 | 2273 | 0.12 | 0.082299 | full_validation_argmax_MCC_grid_0.01_0.99 |
| reveal | B2-flip | 2273 | 0.12 | 0.032660 | inherit_recomputed_B2 |

## Test full

| Dataset | Arm | n | tau | AUROC | AP | MCC | BA | Precision | Recall | F1 | Tỷ lệ đoán 1 | TP | FP | TN | FN | Raw invalid |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| devign | B0 | 2732 | 0.9800 | 0.5405 | 0.5153 | 0.0922 | 0.5370 | 0.5513 | 0.2398 | 0.3343 | 0.1999 | 301 | 245 | 1232 | 954 | 302 |
| devign | B1 | 2732 | 0.9800 | 0.5335 | 0.5023 | 0.0788 | 0.5328 | 0.5332 | 0.2558 | 0.3457 | 0.2204 | 321 | 281 | 1196 | 934 | 0 |
| devign | B2 | 2732 | 0.7000 | 0.5305 | 0.4856 | 0.0597 | 0.5293 | 0.4836 | 0.6335 | 0.5485 | 0.6018 | 795 | 849 | 628 | 460 | 0 |
| devign | B2-flip | 2732 | 0.7000 | 0.5240 | 0.4857 | 0.0337 | 0.5166 | 0.4731 | 0.6167 | 0.5355 | 0.5988 | 774 | 862 | 615 | 481 | 0 |
| devign | ALL-0 | 2732 | NA | 0.5000 | 0.4594 | NA | 0.5000 | NA | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 1477 | 1255 | NA |
| devign | ALL-1 | 2732 | NA | 0.5000 | 0.4594 | NA | 0.5000 | 0.4594 | 1.0000 | 0.6295 | 1.0000 | 1255 | 1477 | 0 | 0 | NA |
| reveal | B0 | 2274 | 0.3000 | 0.5740 | 0.1260 | 0.0874 | 0.5700 | 0.1356 | 0.4957 | 0.2129 | 0.3698 | 114 | 727 | 1317 | 116 | 285 |
| reveal | B1 | 2274 | 0.6300 | 0.5841 | 0.1238 | 0.0523 | 0.5370 | 0.1294 | 0.3043 | 0.1816 | 0.2379 | 70 | 471 | 1573 | 160 | 2 |
| reveal | B2 | 2274 | 0.1200 | 0.5662 | 0.1221 | 0.0645 | 0.5531 | 0.1183 | 0.6565 | 0.2005 | 0.5611 | 151 | 1125 | 919 | 79 | 0 |
| reveal | B2-flip | 2274 | 0.1200 | 0.5261 | 0.1051 | 0.0372 | 0.5308 | 0.1118 | 0.5826 | 0.1875 | 0.5273 | 134 | 1065 | 979 | 96 | 0 |
| reveal | ALL-0 | 2274 | NA | 0.5000 | 0.1011 | NA | 0.5000 | NA | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 2044 | 230 | NA |
| reveal | ALL-1 | 2274 | NA | 0.5000 | 0.1011 | NA | 0.5000 | 0.1011 | 1.0000 | 0.1837 | 1.0000 | 230 | 2044 | 0 | 0 | NA |

## Test no_exact_or_near_train

| Dataset | Arm | n | tau | AUROC | AP | MCC | BA | Precision | Recall | F1 | Tỷ lệ đoán 1 | TP | FP | TN | FN | Raw invalid |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| devign | B0 | 2472 | 0.9800 | 0.5334 | 0.5014 | 0.0843 | 0.5333 | 0.5380 | 0.2283 | 0.3206 | 0.1917 | 255 | 219 | 1136 | 862 | 288 |
| devign | B1 | 2472 | 0.9800 | 0.5237 | 0.4886 | 0.0762 | 0.5314 | 0.5246 | 0.2480 | 0.3368 | 0.2136 | 277 | 251 | 1104 | 840 | 0 |
| devign | B2 | 2472 | 0.7000 | 0.5131 | 0.4665 | 0.0345 | 0.5170 | 0.4660 | 0.6141 | 0.5299 | 0.5955 | 686 | 786 | 569 | 431 | 0 |
| devign | B2-flip | 2472 | 0.7000 | 0.5241 | 0.4821 | 0.0307 | 0.5152 | 0.4645 | 0.6097 | 0.5273 | 0.5930 | 681 | 785 | 570 | 436 | 0 |
| reveal | B0 | 1978 | 0.3000 | 0.6064 | 0.0806 | 0.0927 | 0.5990 | 0.0811 | 0.5429 | 0.1411 | 0.3554 | 57 | 646 | 1227 | 48 | 264 |
| reveal | B1 | 1978 | 0.6300 | 0.6025 | 0.0798 | 0.0685 | 0.5643 | 0.0811 | 0.3524 | 0.1319 | 0.2305 | 37 | 419 | 1454 | 68 | 2 |
| reveal | B2 | 1978 | 0.1200 | 0.5822 | 0.0764 | 0.0589 | 0.5653 | 0.0650 | 0.6762 | 0.1185 | 0.5526 | 71 | 1022 | 851 | 34 | 0 |
| reveal | B2-flip | 1978 | 0.1200 | 0.5956 | 0.0741 | 0.0765 | 0.5853 | 0.0697 | 0.6762 | 0.1264 | 0.5147 | 71 | 947 | 926 | 34 | 0 |

Tập sensitivity bỏ các mẫu exact_train hoặc near_train theo manifest đóng băng; còn 2.472 Devign và 1.978 ReVeal. Giữ cùng ngưỡng full validation, không fit lại trên test đã lọc. CSV metrics.csv có thêm toàn bộ kết quả tại ngưỡng cố định 0,5. MCC của predictor hằng là không xác định, không ép bằng 0.

## Chênh lệch ghép cặp trên full test

5.000 lượt paired cluster bootstrap, seed 20261117. Devign: 2.068 commit_id. ReVeal: 646 source_id/file-hash; nối qua raw test ID và kiểm Counter(group,label) khớp canonical_reveal_test.csv lịch sử. Ngưỡng validation giữ cố định trong bootstrap, nên CI chưa bao gồm bất định do chọn ngưỡng. CI 95% dưới đây chưa hiệu chỉnh đa so sánh; không gọi là kết luận xác nhận Holm của toàn bộ họ giả thuyết preregistered.

| Dataset | So sánh (sau trừ trước) | Metric | Delta | CI95 thấp | CI95 cao | Biên delta | Nhận định theo CI đơn lẻ |
|---|---|---|---:|---:|---:|---:|---|
| devign | B2 - B0 | auroc | -0.0100 | -0.0280 | 0.0078 | 0.02 | no_meaningful_benefit |
| devign | B2 - B0 | mcc | -0.0325 | -0.0750 | 0.0106 | 0.03 | no_meaningful_benefit |
| devign | B1 - B0 | auroc | -0.0070 | -0.0197 | 0.0057 | 0.02 | no_meaningful_benefit |
| devign | B1 - B0 | mcc | -0.0134 | -0.0459 | 0.0183 | 0.03 | no_meaningful_benefit |
| devign | B2 - B1 | auroc | -0.0030 | -0.0186 | 0.0122 | 0.02 | no_meaningful_benefit |
| devign | B2 - B1 | mcc | -0.0191 | -0.0605 | 0.0227 | 0.03 | no_meaningful_benefit |
| devign | B2-flip - B2 | auroc | -0.0065 | -0.0233 | 0.0105 | 0.02 | no_meaningful_benefit |
| devign | B2-flip - B2 | mcc | -0.0260 | -0.0609 | 0.0094 | 0.03 | no_meaningful_benefit |
| reveal | B2 - B0 | auroc | -0.0079 | -0.0357 | 0.0183 | 0.02 | no_meaningful_benefit |
| reveal | B2 - B0 | mcc | -0.0229 | -0.0630 | 0.0153 | 0.03 | no_meaningful_benefit |
| reveal | B1 - B0 | auroc | 0.0101 | -0.0092 | 0.0287 | 0.02 | inconclusive |
| reveal | B1 - B0 | mcc | -0.0351 | -0.0743 | 0.0014 | 0.03 | no_meaningful_benefit |
| reveal | B2 - B1 | auroc | -0.0179 | -0.0400 | 0.0041 | 0.02 | no_meaningful_benefit |
| reveal | B2 - B1 | mcc | 0.0121 | -0.0339 | 0.0568 | 0.03 | inconclusive |
| reveal | B2-flip - B2 | auroc | -0.0401 | -0.0648 | -0.0155 | 0.02 | harm |
| reveal | B2-flip - B2 | mcc | -0.0273 | -0.0607 | 0.0049 | 0.03 | no_meaningful_benefit |

## Trả lời sáu RQ trong đề cương

RQ1 — Tái lập: B2 không vượt B0 trên point estimate ở cả MCC và AUROC trên cả hai dataset. Cận trên CI đơn lẻ của delta MCC đều <0,03 và delta AUROC đều <0,02, phù hợp H1.1 trong đề cương ở mức phân tích hậu nghiệm này. B2 MCC test 0,0597/0,0645 đều <0,15; F1 Devign 0,5485 thấp hơn ALL-1 0,6295, phù hợp tiêu chí H1.2. Trên ReVeal B2 F1 0,2005 cao hơn ALL-1 0,1837 nhưng vẫn chỉ AUROC 0,5662; không thể dùng F1 riêng để gọi là mạnh. Chỉ một backbone Qwen Q4 được tính lại, không phải tái tính ba backbone hay xác nhận trực tiếp hiệu năng GPT-4 bài gốc.

RQ2 — Cơ chế demonstration: thêm demo truy hồi vào B1 không tăng AUROC (delta -0,0030/-0,0179). B2-flip đổi 554/2732 (20,28%) nhãn Devign và 243/2274 (10,69%) nhãn ReVeal tại ngưỡng kế thừa; tại argmax 0,5 là 18,12%/13,90%. Đây là tỷ lệ bất đồng thô, chưa phải net sensitivity do B2-rep chưa có. ReVeal full test đảo nhãn làm giảm AUROC 0,0401 với CI cluster [-0,0648;-0,0155]; Devign CI chứa 0. Tuy nhiên trên tập bỏ trùng/gần trùng, delta AUROC flip-base đảo chiều: Devign +0,0110, ReVeal +0,0134. Do đó không kết luận ảnh hưởng nhãn là bền vững trên mọi partition hoặc chứng minh sao chép nhãn; cần rep, rand, nolabel, labelonly và CI theo partition.

RQ3 — Graph: B1-B0 delta AUROC -0,0070 Devign và +0,0101 ReVeal. Devign cận trên CI <0,02; ReVeal cận trên 0,0287 nên vẫn chưa đủ chứng cứ loại lợi ích >=0,02. MCC B1 thấp hơn B0 ở cả hai dataset tại ngưỡng validation. Chưa có shuf/full/H2 nên chưa thể kết luận LLM không đọc graph (toàn bộ H3.1).

RQ4 — Khả năng phân biệt hay điểm hoạt động: trong các arm đã chạy, không thấy tăng phân biệt từ B0->B1->B2 nhất quán; ở Devign B1->B2 recall tăng 25,58%->63,35%, tỷ lệ đoán 1 tăng 22,04%->60,18%, nhưng AUROC giảm 0,5335->0,5305 và MCC giảm 0,0788->0,0597. ReVeal B1->B2 recall tăng 30,43%->65,65%, tỷ lệ đoán 1 tăng 23,79%->56,11% nhưng AUROC giảm 0,5841->0,5662. Tăng recall/F1 không tự chứng minh tăng khả năng phân biệt. Chưa có B3 nên H2.3 về cặp tương phản chưa đánh giá. H4.1 AUROC <=0,62 đúng về point estimate cho bốn arm hiện có; chưa khái quát toàn bộ 15 arm.

RQ5 — Mốc có giám sát và giá trị bổ sung: bốn arm LLM không đủ trả lời. Chưa tính lại SUP-LR/MLP/METRIC, P-PRE/P-POST hoặc routing của chiến dịch này; không trộn metric lịch sử vào phép so mới. H5.1/H5.2/H5.3 còn thiếu dữ liệu.

RQ6 — Truy hồi và lỗi: records điểm số không cung cấp đánh giá liên quan cơ chế hoặc xác minh nhãn thật. Cần nối hai người chấm, audit nhãn và packet sửa/hỏng; chưa kết luận H6.1 từ phân tích này.

## Tái lập và giới hạn

Chạy từ thư mục repo: `python Runs-management/reanalysis_20261106/recompute.py`. results.json lưu ngưỡng, metric, CI, độ nhạy và đường dẫn/SHA-256 đầu vào. metrics.csv gồm full/clean, ngưỡng validation/0,5, confusion matrix và invalid raw. contrasts.csv và sensitivity.csv lưu số liệu chi tiết.

Các file preregistration/config khóa được giữ nguyên. Đây là phiên phân tích mới sau khi đã xem test, không được mô tả là ngưỡng đã khóa trước inference. Việc cập nhật CHANGES_AFTER_PREREG.md/worklog vẫn pending theo yêu cầu trước; báo cáo này không thay thế amendment đó.

SHA-256 đề cương: `a55b3992696f69bd2c05e360e76827071396b5a9b5dec5a75bc6512cac9d0d40`.
