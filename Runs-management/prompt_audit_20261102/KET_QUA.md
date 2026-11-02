# Audit prompt và output đã có — 02/11/2026

## Raw response và score được kiểm riêng

- B0: 1132/10011 raw response không phải token nhãn, 0 score không hợp lệ.
- B1: 3/5434 raw response không phải token nhãn, 0 score không hợp lệ.
- B2: 0/10011 raw response không phải token nhãn, 0 score không hợp lệ.
- B2-flip: 0/5235 raw response không phải token nhãn, 0 score không hợp lệ.

Đã tính lại score từ hai logprob: 30.691/30.691 khớp, không chọn ngưỡng hoặc cấu hình từ test. Raw response không hợp lệ vẫn được báo coverage riêng; không phải bằng chứng score hỏng. [Chi tiết](raw_response_coverage.json), [ID/raw token](invalid_raw_responses.csv).


## Kết luận sau phân loại cảnh báo

Đã hoàn tất thực thi audit tự động trên 100,110 dòng prompt/40 tập và đối chiếu 30,691 record inference.
Kiểm hash/ID/nhãn metadata/payload target-graph-demo/variant/token: ĐẠT sau phân loại cảnh báo cú pháp C/C++ có bằng chứng.
Cảnh báo nhãn còn chưa giải quyết: 0 prompt. Toàn bộ cờ regex gốc được giữ, xem [phân loại](leak_review.json).
Có 403 dòng prompt có demo dưới 25% gốc (đếm riêng arm/phiên/seed); trong đó 68 dòng thuộc output đã inference. Giữ tiêu chí, chưa sửa prompt hoặc inference lại.
B2 legacy vẫn có 21 target Devign dùng donor ngoài kho mới (10 do label conflict, 10 overlap eval exact, 1 duplicate train); đây là chênh lệch lịch sử đã biết, chưa được xóa bởi audit payload. 66 prompt đổi khi chuyển donor vẫn cần xử lý theo sổ run.
Kho frozen: code/nhãn/ID của 21,691 donor Devign và 17,636 donor REVEAL đã khớp train manifest. 30.033 lựa chọn random khớp selector ba seed.

| Arm | Phiên | Dataset | Split | Cần xử lý | Đã inference |
|---|---|---|---|---:|---:|
| B2 | frozen | devign | test | 13 | 0 |
| B2 | frozen | devign | validation | 15 | 0 |
| B2 | frozen | reveal | test | 12 | 0 |
| B2 | frozen | reveal | validation | 6 | 0 |
| B2 | legacy | devign | test | 13 | 13 |
| B2 | legacy | devign | validation | 15 | 15 |
| B2 | legacy | reveal | test | 12 | 12 |
| B2 | legacy | reveal | validation | 6 | 6 |
| B2-flip | frozen | devign | test | 13 | 0 |
| B2-flip | frozen | devign | validation | 15 | 0 |
| B2-flip | frozen | reveal | test | 12 | 0 |
| B2-flip | frozen | reveal | validation | 6 | 0 |
| B2-flip | legacy | devign | test | 13 | 1 |
| B2-flip | legacy | devign | validation | 15 | 15 |
| B2-flip | legacy | reveal | test | 12 | 0 |
| B2-flip | legacy | reveal | validation | 6 | 6 |
| B2-rand | frozen | devign | test | 47 | 0 |
| B2-rand | frozen | devign | validation | 58 | 0 |
| B2-rand | frozen | reveal | test | 34 | 0 |
| B2-rand | frozen | reveal | validation | 34 | 0 |
| B2-rep | legacy | devign | test | 13 | 0 |
| B2-rep | legacy | devign | validation | 15 | 0 |
| B2-rep | legacy | reveal | test | 12 | 0 |
| B2-rep | legacy | reveal | validation | 6 | 0 |

### Việc đã hoàn thành và việc còn lại

- Hoàn thành: adapter evidence, audit tự động toàn bộ artifact của 6 arm, kiểm lại token bằng tokenizer đã pin, đối chiếu output đã chạy, xác minh donor và selector random, hoàn thành chấm mù độc lập 60 mẫu bởi hai chuyên gia (Reviewer 1: HuuHieu03, Reviewer 2: Dung) với Cohen's Kappa κ = 0.8507; lập biên bản phân xử hòa giải tại [BIEN_BAN_PHAN_XU.md](BIEN_BAN_PHAN_XU.md).
- Đang nghẽn / Còn lại: 5 arm Tầng 3 (B1-H2, B3, B3-nodiff, B3-swap, B3-flip) thiếu khối trích xuất đối chứng; 403 cờ demo dưới 25% được theo dõi trong [remediation_final.csv](remediation_final.csv) (toàn tập đạt tỷ lệ demo rỗng ≤ 1.0% theo Phụ lục C).
- 9 arm chưa có prompt được ghi chưa chuẩn bị theo quyết định người dùng; không mở thêm arm trong đợt này.
- [Kết luận máy đọc](final_status.json), [danh sách cuối](remediation_final.csv), [output đã chạy cần xem](executed_needing_review.csv), [donor scope](donor_scope.json), [selector random](random_selection.json).


## Kết quả quét thô trước phân loại cảnh báo

Đã audit 100,110 dòng prompt, 40 tập; đối chiếu 30,691 output inference local.
Audit chạy sau inference; giữ nguyên timestamp, prompt/output, khóa ngưỡng và snapshot lịch sử. Chưa gọi LLM hoặc tính khóa mới.

**Đã hoàn tất audit tự động và khâu chấm tay độc lập hai người theo Phụ lục C. Năm arm Tầng 3 được ghi nhận bảo lưu nghẽn đầu vào.**

| Arm | Phiên | Seed | Dataset | Split | N | Demo dưới 25% | Cờ khác | Kết luận |
|---|---|---:|---|---|---:|---:|---|---|
| B0 | legacy | 42 | devign | validation | 2732 | 0 | {} | pass_automatic_checks |
| B1 | legacy | 42 | devign | validation | 2732 | 0 | {} | pass_automatic_checks |
| B2 | legacy | 42 | devign | validation | 2732 | 15 | {} | needs_remediation |
| B2-flip | legacy | 42 | devign | validation | 2732 | 15 | {} | needs_remediation |
| B2-rep | legacy | 42 | devign | validation | 2732 | 15 | {} | needs_remediation |
| B2 | frozen | 42 | devign | validation | 2732 | 15 | {} | needs_remediation |
| B2-flip | frozen | 42 | devign | validation | 2732 | 15 | {} | needs_remediation |
| B2-rand | frozen | 42 | devign | validation | 2732 | 15 | {} | needs_remediation |
| B2-rand | frozen | 43 | devign | validation | 2732 | 19 | {} | needs_remediation |
| B2-rand | frozen | 44 | devign | validation | 2732 | 24 | {"label_leak_needs_review": 1} | needs_remediation |
| B0 | legacy | 42 | devign | test | 2732 | 0 | {} | pass_automatic_checks |
| B1 | legacy | 42 | devign | test | 2732 | 0 | {} | pass_automatic_checks |
| B2 | legacy | 42 | devign | test | 2732 | 13 | {} | needs_remediation |
| B2-flip | legacy | 42 | devign | test | 2732 | 13 | {} | needs_remediation |
| B2-rep | legacy | 42 | devign | test | 2732 | 13 | {} | needs_remediation |
| B2 | frozen | 42 | devign | test | 2732 | 13 | {} | needs_remediation |
| B2-flip | frozen | 42 | devign | test | 2732 | 13 | {} | needs_remediation |
| B2-rand | frozen | 42 | devign | test | 2732 | 15 | {} | needs_remediation |
| B2-rand | frozen | 43 | devign | test | 2732 | 12 | {} | needs_remediation |
| B2-rand | frozen | 44 | devign | test | 2732 | 20 | {} | needs_remediation |
| B0 | legacy | 42 | reveal | validation | 2273 | 0 | {"label_leak_needs_review": 1} | needs_remediation |
| B1 | legacy | 42 | reveal | validation | 2273 | 0 | {"label_leak_needs_review": 1} | needs_remediation |
| B2 | legacy | 42 | reveal | validation | 2273 | 6 | {"label_leak_needs_review": 1} | needs_remediation |
| B2-flip | legacy | 42 | reveal | validation | 2273 | 6 | {"label_leak_needs_review": 1} | needs_remediation |
| B2-rep | legacy | 42 | reveal | validation | 2273 | 6 | {"label_leak_needs_review": 1} | needs_remediation |
| B2 | frozen | 42 | reveal | validation | 2273 | 6 | {"label_leak_needs_review": 1} | needs_remediation |
| B2-flip | frozen | 42 | reveal | validation | 2273 | 6 | {"label_leak_needs_review": 1} | needs_remediation |
| B2-rand | frozen | 42 | reveal | validation | 2273 | 14 | {"label_leak_needs_review": 3} | needs_remediation |
| B2-rand | frozen | 43 | reveal | validation | 2273 | 13 | {"label_leak_needs_review": 2} | needs_remediation |
| B2-rand | frozen | 44 | reveal | validation | 2273 | 7 | {"label_leak_needs_review": 2} | needs_remediation |
| B0 | legacy | 42 | reveal | test | 2274 | 0 | {} | pass_automatic_checks |
| B1 | legacy | 42 | reveal | test | 2274 | 0 | {} | pass_automatic_checks |
| B2 | legacy | 42 | reveal | test | 2274 | 12 | {"label_leak_needs_review": 1} | needs_remediation |
| B2-flip | legacy | 42 | reveal | test | 2274 | 12 | {"label_leak_needs_review": 1} | needs_remediation |
| B2-rep | legacy | 42 | reveal | test | 2274 | 12 | {"label_leak_needs_review": 1} | needs_remediation |
| B2 | frozen | 42 | reveal | test | 2274 | 12 | {"label_leak_needs_review": 1} | needs_remediation |
| B2-flip | frozen | 42 | reveal | test | 2274 | 12 | {"label_leak_needs_review": 1} | needs_remediation |
| B2-rand | frozen | 42 | reveal | test | 2274 | 9 | {} | needs_remediation |
| B2-rand | frozen | 43 | reveal | test | 2274 | 13 | {} | needs_remediation |
| B2-rand | frozen | 44 | reveal | test | 2274 | 12 | {"label_leak_needs_review": 2} | needs_remediation |

## Tiêu chí và giới hạn

Tiêu chí 25% được giữ theo xác nhận người dùng: các mẫu dưới ngưỡng được liệt kê cần xử lý, chưa inference lại.
B0/B1 chủ động không có demo không bị gắn lỗi demo rỗng. Metadata adapter giữ policy, cờ cắt, original_tokens khi đo được và thông tin graph.
Cờ regex thô được giữ trong leak_flags.json; chỉ loại cảnh báo nhầm cú pháp thành viên C/C++ như ->label : khỏi số lỗi rò rỉ. Các trường hợp khác giữ cần xem xét.
Nhãn target chỉ đối chiếu metadata; payload target/code/graph/demo được so với source, đồng thời kiểm đúng phép biến đổi từng variant.
Không có prompt cho 9 arm còn lại; không ghi chúng đã qua dry-run. Rerun-66 thuộc B2, không phải arm thứ 16.

## Hồ sơ cần xem

- [Tóm tắt máy đọc](audit_summary.json), [audit từng prompt](audit_rows.csv).
- [Danh sách mẫu cần xử lý](remediation_rows.csv), [cờ rò rỉ và phân loại](leak_flags.json).
- [Đối chiếu inference](inference_audit.json), [hash nguồn](source_hashes.json).
- [Bộ prompt chấm](manual_packet.md), [mẫu JSONL](manual_sample.jsonl), [rubric](RUBRIC.md).
- [Phiếu người 1](reviewer_1.csv): HuuHieu03 (Hiếu) đã chấm; [Phiếu người 2](reviewer_2.csv): Dung (Dũng) đã chấm.
- [Biên bản phân xử hòa giải](BIEN_BAN_PHAN_XU.md): đã giải quyết 1 điểm bất đồng và 3 trường hợp lưu ý, đạt đồng thuận 100%.
