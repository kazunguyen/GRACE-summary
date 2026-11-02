# Tiến độ các bước theo Phương án 2

**Hiện trạng sau đối chiếu 02/11/2026:** xem [HIEN_TRANG.md](HIEN_TRANG.md) và [current_status.json](current_status.json). Hai file này bổ sung các snapshot kiểm toán/ngưỡng ngày 01/11; không tạo khóa mới. B2 hiện chưa tích hợp helper vào notebook; watcher chưa được xác minh đang chạy. B2-rand đã có 12 bundle và notebook chạy kèm B2 rerun-66, chưa có output inference.

**Cập nhật B1 ngày 02/11/2026:** đã xác minh output `kaggle_run_01`, ghi bổ sung là **I-07** (ID theo thứ tự nhập sổ, không phải thời gian chạy): **5.434/10.011 mẫu (54,28%)**, gồm Devign validation 2.732, REVEAL validation 2.273, Devign test 429, REVEAL test 0; còn **4.577** mẫu. Dừng do hết ngân sách thời gian. Đã đối chiếu toàn bộ record: không trùng ID, đúng arm/dataset/split/model và hash prompt; **0 invalid score, 3 invalid raw response** ở REVEAL validation. Hai validation đã đủ score; chưa có bằng chứng khóa ngưỡng B1 trước 429 test. Xem [bằng chứng B1](b1_I07_20261102.json) và [sổ run](RUNS.md). Các nhận định chưa có inference B1 trong snapshot cũ chỉ mô tả thời điểm kiểm toán.

<!-- donor-rerun-risk-note -->
**Theo dõi thống nhất donor, cập nhật 02/11/2026:** đã đối chiếu toàn bộ prompt. B2 Devign đã chạy cần inference mới 66 mẫu; B2-flip I-06 cần chạy lại 33 mẫu đã có output (28 validation + 5 test Devign), thêm 33 Devign test đổi prompt còn chưa chạy. B0/B1 không trực tiếp phụ thuộc donor. B2-flip đã có bundle và notebook chuyển checkpoint sang phiên donor mới; chưa có kết quả GPU của phiên mới. Chi tiết: [NGUY_CO_CHAY_LAI_DO_DONOR.md](NGUY_CO_CHAY_LAI_DO_DONOR.md).
<!-- /donor-rerun-risk-note -->

## Cập nhật B2-flip — 02/11/2026

Đã nhập checkpoint **I-06**, đạt **5.235/10.011 mẫu (52,29%)**, còn **4.776** mẫu chưa chạy: Devign validation 2.732/2.732, REVEAL validation 2.273/2.273, Devign test 230/2.732, REVEAL test 0/2.274. Run dừng do ngân sách thời gian. Raw CM: **TP=913, TN=1.887, FP=1.819, FN=616; invalid response=0, invalid score=0**. Xem [báo cáo I-06](b2_flip_I06_20261102/KET_QUA_I06_B2_FLIP.md) và [sổ run](RUNS.md).

Đã sửa cả notebook tạo prompt và notebook inference; đã sinh **bundle mới đủ 10.011 prompt** ghép cặp với B2 tham chiếu của kho donor thống nhất. So phiên cũ, Devign đổi 28 validation và 38 test, REVEAL không đổi. Với output I-06, giữ được **5.202** record và cần inference lại **33** record; 33 test đổi prompt còn chưa chạy dùng input mới cho lượt đầu.

Luồng phiên mới ưu tiên 28 validation, ghép đủ 2.732 để khóa ngưỡng mới, rồi chạy lại 5 test; sau đó tiếp tục 4.776 mẫu thiếu. Tổng bổ sung **4.809 lượt LLM**. Đây là code/input đã chuẩn bị và đã kiểm thử CPU, **chưa thực hiện inference GPU phiên mới, chưa có run B2-flip phiên donor mới hoặc ngưỡng mới từ score sửa**. Hướng dẫn, bundle và checkpoint: [B2_FLIP_DONOR_MOI_RESUME.md](B2_FLIP_DONOR_MOI_RESUME.md).

Các đoạn ghi ngày 01/11 bên dưới giữ lịch sử thời điểm đánh giá; phần cập nhật này và bảng tiến độ là trạng thái mới cho B2-flip. Các yêu cầu chấm prompt bằng người, đăng ký trước và OSF vẫn cần nghiệm thu riêng.

## Các mốc và tiến độ theo đề cương

**Giải thích/chốt lại ngưỡng từ kết quả đầy đủ:** B0 Devign 0,98, B0 ReVeal 0,30, B2 Devign 0,70, B2 ReVeal 0,12. Đã đối chiếu đủ validation và kiểm tra độc lập bằng sklearn. Xem [KET_QUA_CHOT_NGUONG.md](KET_QUA_CHOT_NGUONG.md) để biết phương pháp và nguồn PDF theo trang; trạng thái chờ ReVeal trong các đoạn cũ là lịch sử trước khi đủ dữ liệu.

**Cập nhật khóa ngưỡng/phân tích khi inference đang chạy:** xem [TU_DONG_KHOA_NGUONG.md](TU_DONG_KHOA_NGUONG.md). Đã khóa B0 Devign 0,98, B0 ReVeal 0,30, B2 Devign 0,70 từ validation đầy đủ; watcher có khả năng xử lý kết quả khi chạy, nhưng hiện chưa xác minh process đang hoạt động. Notebook B0 có tự khóa/chặn test; notebook B2 hiện tại chưa nhúng helper hoặc gọi make_lock/require_test_lock. Đã có bản ghi phân tích có thời điểm + commit/tag local, không coi là preregistration hồi tố; OSF chưa đăng. Những thiếu sót donor và chấm tay trong kiểm toán trước vẫn còn nguyên.

Cập nhật B0 Kaggle 01/11/2026: devign validation: 2732 (complete); devign test: 2732 (complete); reveal validation: 2273 (complete); reveal test: 2274 (complete); trạng thái complete. Xem [I-03](RUNS.md) và [output](../02_Arm_B0_Source_Only/output/kaggle_20261101_duchuynguyen1802/grace_b0_runs/). Chưa suy ra đăng ký trước hoặc tính xác nhận từ việc có output.

Cập nhật B2 Kaggle 01/11/2026, sau khi nhập lượt I-05: đủ **10.011/10.011** prediction cho Devign/REVEAL × validation/test; 0 invalid. Tổng confusion matrix raw prediction: TP=1.868, TN=3.413, FN=1.014, FP=3.716. Kết quả và provenance chi tiết ở [I-05](RUNS.md). Đây là trạng thái inference đã chạy; không tự xóa các hạn chế donor/protocol và điều kiện nghiệm thu nghiên cứu ghi trong báo cáo kiểm toán.

**Kết quả kiểm toán cập nhật ngày 01/11/2026:** cả năm arm Tầng 1 đã có đủ 20 tập prompt, tổng 50.055 prompt. [Báo cáo điều kiện Tầng 1](KIEM_TOAN_DIEU_KIEN_TANG_1.md) và [bằng chứng JSON](KIEM_TOAN_DIEU_KIEN_TANG_1.json) thay thế các nhận định cũ bên dưới về việc chưa sinh đủ prompt. Báo cáo ghi nhận thời điểm kiểm toán ban đầu; bổ sung inference I-05 ở trên cập nhật rằng B0/B2 đã có output và khóa ngưỡng cho B0, B2/Devign, B2/ReVeal. Các điều kiện donor Devign, chấm tay 30 prompt/dataset, OSF, cùng thứ tự B2/ReVeal test chạy một phần trước khóa vẫn chưa được giải quyết. Thay server bằng Kaggle GPU được chấp nhận trong kiểm toán này.

Cập nhật notebook prompt Tầng 1 ngày 01/11/2026: đã tạo folder riêng [B1](../03_Arm_B1_Graph_Only/README.md), [B2-flip](../04_Arm_B2_Flip/README.md) và [B2-rep](../05_Arm_B2_Rep/README.md), mỗi folder một notebook sinh prompt. Dùng lại specs/prompt B2 đã có (CPG Joern và demo đã chọn bằng CodeT5); không chạy parse/encoder/retrieval. Hash bốn cache B2 và sáu manifest cache CodeT5 đã kiểm tra. Đây là phép ghép cặp với B2 tham chiếu; các demo nằm ngoài kho donor mới được thống kê, không âm thầm đổi demo. Sau đó đã sinh đủ 20 tập prompt Tầng 1 theo kiểm toán; tại snapshot ban đầu chưa có run inference thật được xác nhận cho B1, B2-flip và B2-rep. Cập nhật 02/11: B1 I-07 đã có 5.434 record, B2-flip I-06 đã có 5.235 record; B2-rep vẫn chưa có output được xác nhận.

Cập nhật notebook B0 ngày 01/11/2026: đã tạo [folder B0 riêng](../02_Arm_B0_Source_Only/README.md), gồm notebook sinh prompt và notebook inference Kaggle tự tìm input/model/checkpoint không phụ thuộc username. Biến thể giữ câu dẫn B2, bỏ trống payload graph/demo và nhãn demo (`b0_b2_empty_blocks_v1`). Sau đó đã nhập run I-03 đủ 10.011 inference trên bốn split; phần kiểm toán prompt/B3 và thứ tự khóa ngưỡng trước test vẫn được đánh giá độc lập trong báo cáo.

Cập nhật 01/11/2026. Nguồn: [đề cương Phương án 2](../../REPORT_TO_TEACHER/20261029/PhuongAn2_De_cuong_nghien_cuu_GRACE_hop_nhat.pdf), Mục 7 (Bước 0–9). Đánh giá dựa trên artifact trong GRACE-summary; không suy ra hoàn thành chỉ vì đã có script. Smoke test GPU không thuộc phạm vi lần cập nhật này. Phần 1/3/4 trong yêu cầu người dùng là các hạng mục kỹ thuật, không đồng nhất với số Bước trong PDF.

| Bước PDF | Tiến độ | Đã có | Phần còn lại / điều kiện nghiệm thu |
|---|---|---|---|
| B0 — Phân tích offline từ dự đoán cũ | Không đánh giá theo yêu cầu | Kho bằng chứng lịch sử được giữ nguyên. | Không làm hoặc xác nhận B0 trong đợt này. |
| B1 — LLM tự host có logprob | Đã chốt framework; chưa nghiệm thu runtime toàn ma trận | Qwen Q4_K_M, llama-cpp-python 0.3.16, model hash, tokenizer revision, hàm raw logits chung và config native; lượt B2 Kaggle đã có kết quả thật. | Notebook/runtime cho từng arm làm sau; smoke test không được tính thiếu trong đánh giá đợt này. |
| B2 — Đóng băng dữ liệu, retrieval, specs | Có snapshot donor và bộ B2 tham chiếu mới; specs toàn ma trận chưa hoàn tất | Raw/manifest/hash ba split, exact dedup/near flags; đã fit lại retrieval trên donor mới, đối chiếu B2 và sinh đủ prompt B2-flip ghép cặp với B2 mới. | Hoàn tất áp dụng phiên donor mới vào inference B2/flip/rep; cặp B3, Key difference, H2 evidence và specs các arm còn lại. Output lịch sử vẫn thuộc prompt cũ. |
| B3 — Renderer, probe, kiểm tra prompt | Có prompt Tầng 1; B2-flip đã chuyển nguồn donor, chưa nghiệm thu đầy đủ | Prefix/B1-full trần 40/80; H2 yêu cầu metadata nguồn; B2-rep gọi mới; B2-flip mới đủ 10.011 prompt, hash khớp kiểm toán độc lập và token hóa bằng tokenizer đã pin. | Kiểm chứng H2 source, audit chuyên dụng và người đọc prompt; tiếp tục notebook các arm còn lại theo phạm vi yêu cầu. |
| B4 — Đăng ký trước | Chưa hoàn tất | Protocol đã cập nhật model/hash/tokenizer, dữ liệu, graph và scoring. | Chờ prompt/audit để viết preregistration, điền ngày, commit/tag và OSF; không tự gắn trạng thái đã đăng ký. |
| B5 — Chạy ma trận | Đang thực hiện; B0/B2 đủ bốn split, B1 I-07 đạt 54,28%, B2-flip I-06 đạt 52,29% | B0 I-03 và B2 I-05 đủ 10.011 mẫu/arm. B1 I-07: 5.434/10.011; hai validation đủ, Devign test 429, REVEAL test 0; còn 4.577. B2-flip I-06: 5.235/10.011, 0 invalid; hai validation đủ, Devign test 230, REVEAL test 0. Notebook mới giữ 5.202 output, ưu tiên sửa 33 rồi chạy 4.776 mẫu thiếu. | B1 còn 4.577 mẫu; cần xử lý khóa ngưỡng từ validation đầy đủ và giữ lịch sử 429 test đã chạy chưa có bằng chứng khóa trước. Chạy GPU phiên donor mới: B2-flip cần thêm 4.809 lượt và khóa ngưỡng mới sau khi đủ validation; B2 có 66 prompt cần score mới. Hoàn tất các arm còn lại. Giữ lịch sử test B2 chạy một phần trước khóa REVEAL và việc I-06 không kèm bằng chứng khóa trước 230 test; các hạn chế protocol/audit vẫn còn. |
| B6 — Mốc giám sát, P_pre/P_post, routing | Có mã khung; chưa có nghiệm thu lượt mới | supervised_anchor.py, complementarity.py trong kit. | Fit/evaluate ba seed trên snapshot khóa, xuất đặc trưng chung, đối chứng và routing từ expert mới. |
| B7 — Thống kê, bảng và hình | Có mã khung; chưa hoàn tất đầu ra | stats.py, evaluate_final.py và cấu hình contrast/biên delta. | Sinh bảng/hình từ ma trận và anchor mới; kiểm tra ghép ID/CI/hiệu chỉnh đa kiểm định. |
| B8 — Chấm mù, gói ca và kiểm toán nhãn | Chưa xác nhận hoàn thành cho nghiên cứu mới | Có lịch sử chấm mù và make_case_packets.py. | Gói ca, hai người chấm, kappa, kiểm toán nhãn theo giao thức cuối. |
| B9 — Gói tái lập | Hoàn thành một phần | Snapshot hash, script tái tạo/kiểm tra, tài liệu framework, kit và sổ run. | Đóng gói notebook/đầu ra cuối, README và kiểm tra tái lập trên máy sạch. |

## Snapshot dữ liệu đã kiểm tra

Các số loại là số dòng train, gán lý do theo thứ tự overlap eval → nhóm nhãn mâu thuẫn → bản sao cùng nhãn. Cờ gần trùng eval đối chiếu train gốc, bao gồm exact; chỉ gắn cờ, không loại khỏi eval.

| Dataset | Train gốc | Donor giữ | Loại trùng eval | Loại nhãn mâu thuẫn | Loại bản sao cùng nhãn | Eval gần trùng validation / test |
|---|---:|---:|---:|---:|---:|---:|
| devign | 21,854 | 21,691 | 22 | 138 | 3 | 240 / 260 |
| reveal | 18,187 | 17,636 | 125 | 426 | 0 | 285 / 296 |

Manifest tổng: [freeze_manifest.json](../01_Author_Baseline_Unified/output/research_freeze_20261101/freeze_manifest.json). SHA-256: `e1d3c6b17c3a0b5c1e05203794d48a33825e0ea00a55deaaef565af25efe0448`. Thống kê và hash từng file nằm trong manifest; donor IDs khớp chính xác tập keep_in_bank, không lặp ID/nhóm chuẩn hóa; nhãn/hash mã khớp manifest. Nguồn graph được khóa bằng hash tham chiếu, không tạo lại CPG.

Quy tắc và cách dùng: [QUY_UOC_FRAMEWORK_20261101.md](QUY_UOC_FRAMEWORK_20261101.md). Các notebook arm tiếp theo phải dùng snapshot mới và hàm scoring chung. Mô hình/API top-k lịch sử không tự động được coi tương thích.

## Kiểm tra mã

- `python -m pytest diagnostic_kit/tests test_logprobs.py -q`: 39 passed.
- Bộ bổ sung kiểm tra literal, logits ngoài top-5, underflow, graph cap và H2 guard: 4 passed.
- Lượt kiểm tra rộng ban đầu có ba lỗi import `fcntl` ở các script Joern/embedding chạy Linux khi gọi bằng Python Windows; không sửa các script đó trong đợt này. Một assertion B1-full cũ đã được cập nhật vì cùng trần 40/80 có thể tạo graph giống B1 khi không cần cắt. Bộ kit sau sửa đã xanh.
- Chưa chạy GPU/backend smoke test, không tạo prompt/notebook từng arm và không thực hiện đăng ký trước trong đợt này.
