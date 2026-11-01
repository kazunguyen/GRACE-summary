# Tiến độ các bước theo Phương án 2

**Cập nhật khóa ngưỡng/phân tích khi inference đang chạy:** xem [TU_DONG_KHOA_NGUONG.md](TU_DONG_KHOA_NGUONG.md). Đã khóa B0 Devign 0,98, B0 ReVeal 0,30, B2 Devign 0,70 từ validation đầy đủ; watcher local tự xử lý kết quả còn lại khi nhập về. B0/B2 notebook phiên sau tự lưu ngưỡng và kiểm tra trước test. Đã có bản ghi phân tích có thời điểm + commit/tag local, không coi là preregistration hồi tố; OSF chưa đăng. Những thiếu sót donor và chấm tay trong kiểm toán trước vẫn còn nguyên.

Cập nhật B0 Kaggle 01/11/2026: devign validation: 2732 (complete); devign test: 2732 (complete); reveal validation: 2273 (complete); reveal test: 2274 (complete); trạng thái complete. Xem [I-03](RUNS.md) và [output](../02_Arm_B0_Source_Only/output/kaggle_20261101_duchuynguyen1802/grace_b0_runs/). Chưa suy ra đăng ký trước hoặc tính xác nhận từ việc có output.

**Kết quả kiểm toán cập nhật ngày 01/11/2026:** cả năm arm Tầng 1 đã có đủ 20 tập prompt, tổng 50.055 prompt. [Báo cáo điều kiện Tầng 1](KIEM_TOAN_DIEU_KIEN_TANG_1.md) và [bằng chứng JSON](KIEM_TOAN_DIEU_KIEN_TANG_1.json) thay thế các nhận định cũ bên dưới về việc chưa sinh đủ prompt. Điều kiện test xác nhận chưa hoàn tất: donor Devign của B2 chưa khớp snapshot mới; chưa có bằng chứng chấm tay 30 prompt/dataset, preregistration/tag/OSF hoặc thresholds.json; notebook B0/B2 chưa chặn test khi chưa khóa ngưỡng. Thay server bằng Kaggle GPU được chấp nhận trong kiểm toán này.

Cập nhật notebook prompt Tầng 1 ngày 01/11/2026: đã tạo folder riêng [B1](../03_Arm_B1_Graph_Only/README.md), [B2-flip](../04_Arm_B2_Flip/README.md) và [B2-rep](../05_Arm_B2_Rep/README.md), mỗi folder một notebook sinh prompt. Dùng lại specs/prompt B2 đã có (CPG Joern và demo đã chọn bằng CodeT5); không chạy parse/encoder/retrieval. Hash bốn cache B2 và sáu manifest cache CodeT5 đã kiểm tra. Đây là phép ghép cặp với B2 tham chiếu; các demo nằm ngoài kho donor mới được thống kê, không âm thầm đổi demo. Chưa sinh toàn bộ prompt và chưa viết/chạy inference cho ba arm này.

Cập nhật notebook B0 ngày 01/11/2026: đã tạo [folder B0 riêng](../02_Arm_B0_Source_Only/README.md), gồm notebook sinh prompt và notebook inference Kaggle tự tìm input/model/checkpoint không phụ thuộc username. Biến thể giữ câu dẫn B2, bỏ trống payload graph/demo và nhãn demo (`b0_b2_empty_blocks_v1`). Đã kiểm tra offline; chưa chạy sinh prompt đầy đủ hoặc inference thật, nên chưa nghiệm thu B3/B5 cho B0.

Cập nhật 01/11/2026. Nguồn: [đề cương Phương án 2](../../REPORT_TO_TEACHER/20261029/PhuongAn2_De_cuong_nghien_cuu_GRACE_hop_nhat.pdf), Mục 7 (Bước 0–9). Đánh giá dựa trên artifact trong GRACE-summary; không suy ra hoàn thành chỉ vì đã có script. Smoke test GPU không thuộc phạm vi lần cập nhật này. Phần 1/3/4 trong yêu cầu người dùng là các hạng mục kỹ thuật, không đồng nhất với số Bước trong PDF.

| Bước PDF | Tiến độ | Đã có | Phần còn lại / điều kiện nghiệm thu |
|---|---|---|---|
| B0 — Phân tích offline từ dự đoán cũ | Không đánh giá theo yêu cầu | Kho bằng chứng lịch sử được giữ nguyên. | Không làm hoặc xác nhận B0 trong đợt này. |
| B1 — LLM tự host có logprob | Đã chốt framework; chưa nghiệm thu runtime toàn ma trận | Qwen Q4_K_M, llama-cpp-python 0.3.16, model hash, tokenizer revision, hàm raw logits chung và config native; lượt B2 Kaggle đã có kết quả thật. | Notebook/runtime cho từng arm làm sau; smoke test không được tính thiếu trong đánh giá đợt này. |
| B2 — Đóng băng dữ liệu, retrieval, specs | Hoàn tất snapshot dữ liệu/donor; specs toàn ma trận chưa hoàn tất | Raw/manifest/hash ba split, exact dedup, near flags Jaccard chính xác, donor duy nhất đã kiểm tra, hash nguồn CPG sáu split. Chọn full official validation. | Dựng demo B2 từ donor mới; cặp B3, Key difference, H2 evidence và specs mỗi arm thuộc việc tạo prompt tiếp theo. Không dùng bundle cũ như đã tự động đạt snapshot mới. |
| B3 — Renderer, probe, kiểm tra prompt | Hoàn tất sửa framework graph/score; chưa nghiệm thu prompt | Prefix và B1-full trần 40/80; H2 yêu cầu metadata graph nguồn; B2-rep gọi mới; score gốc thống nhất. | Folder/notebook từng arm, kiểm chứng H2 source, dry-run/audit toàn validation và người đọc prompt sẽ làm theo yêu cầu sau. |
| B4 — Đăng ký trước | Chưa hoàn tất | Protocol đã cập nhật model/hash/tokenizer, dữ liệu, graph và scoring. | Chờ prompt/audit để viết preregistration, điền ngày, commit/tag và OSF; không tự gắn trạng thái đã đăng ký. |
| B5 — Chạy ma trận | Chưa hoàn tất | Ma trận 15 arm / 19 arm–seed. Lượt B2 cũ: Devign validation 2.732/2.732; REVEAL validation 1.664/2.273; test chưa chạy theo checkpoint đã nhập. | Dựng prompt theo snapshot mới, validation và ngưỡng từng arm trước test; chưa tái sử dụng số cũ làm xác nhận nếu chưa đối chiếu identity/donor. |
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
