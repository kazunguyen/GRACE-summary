# Kiểm toán điều kiện trước chạy Tầng 1

<!-- current-status:start -->
## Trạng thái hiện tại — đối chiếu artifact local

Nguồn: [current_status.json](current_status.json), kiểm tra UTC 2026-11-02T03:39:30.129091+00:00.
Snapshot kiểm toán/ngưỡng ngày 01/11 được giữ lịch sử; bảng này cập nhật tiến độ, không tạo khóa mới.

| Arm | Devign val | Devign test | REVEAL val | REVEAL test | Tổng |
|---|---:|---:|---:|---:|---:|
| B0 | 2732/2732 | 2732/2732 | 2273/2273 | 2274/2274 | 10011/10011 |
| B1 | 2732/2732 | 429/2732 | 2273/2273 | 0/2274 | 5434/10011 |
| B2 | 2732/2732 | 2732/2732 | 2273/2273 | 2274/2274 | 10011/10011 |
| B2-flip | 2732/2732 | 230/2732 | 2273/2273 | 0/2274 | 5235/10011 |
| B2-rep | 0/2732 | 0/2732 | 0/2273 | 0/2274 | 0/10011 |
| B2-rand | Chưa có output | Chưa có output | Chưa có output | Chưa có output | 0/30033 |

Validation đủ nhưng chưa có khóa local: B1/devign, B1/reveal, B2-flip/devign, B2-flip/reveal.

Source notebook (kiểm tra tĩnh): B0: có lời gọi khóa trước test; B1: chưa có lời gọi khóa trước test; B2: chưa có lời gọi khóa trước test; B2-flip: có lời gọi khóa trước test; B2-rand: có lời gọi khóa trước test. Không chứng minh thứ tự khóa của các run lịch sử.

Bằng chứng lịch sử [B1 I-07](b1_I07_20261102.json): 5.434 record, 0 invalid score, 3 invalid raw response; [B2-flip I-06](b2_flip_I06_20261102/KET_QUA_I06_B2_FLIP.md): 5.235 record, 0 invalid. Flip Devign donor mới cần sửa 28 validation trước khóa; xem [resume](B2_FLIP_DONOR_MOI_RESUME.md).

B2 Devign donor mới cần 66 lượt; B2-flip cần 4.809 lượt bổ sung. Chưa có output GPU phiên donor mới. B2-rand đã có 12 bundle và notebook chạy kèm B2 rerun-66; chưa có output inference.

Watcher chưa được xác minh đang chạy; không tự khởi động. Các lỗi nghiệm thu prompt/protocol/OSF và lịch sử test trước khóa vẫn giữ nguyên.
<!-- current-status:end -->

## Snapshot lịch sử kiểm toán 01/11/2026

Các mục bên dưới mô tả lúc kiểm toán, không phải trạng thái hiện tại.

<!-- donor-rerun-risk-note -->
**Theo dõi donor/rerun:** B2/flip/rep có nguy cơ khi đổi prompt tham chiếu; B0/B1 không trực tiếp phụ thuộc donor. Chưa chốt danh sách cần inference lại; phải so hash toàn bộ trước. Xem [NGUY_CO_CHAY_LAI_DO_DONOR.md](NGUY_CO_CHAY_LAI_DO_DONOR.md).
<!-- /donor-rerun-risk-note -->

Kiểm tra ngày 01/11/2026 trong GRACE-summary. Tiêu chí: [Phương án 2](../../REPORT_TO_TEACHER/20261029/PhuongAn2_De_cuong_nghien_cuu_GRACE_hop_nhat.pdf), Bước 1–4 và yêu cầu Bước 5 trang 20. Chấp nhận inference Kaggle GPU thay server tự host; không coi thiếu server/API endpoint là lỗi. Bước 0 không được đánh giá theo phạm vi trước đó. B3, H2 và đối chứng Tầng 2/3 không được coi là thiếu để bắt đầu riêng Tầng 1. Việc người dùng đã yêu cầu bỏ qua smoke test không bị đổi thành điều kiện chặn mới trong báo cáo này.

**Kết luận: prompt Tầng 1 đã đầy đủ và ghép cặp đúng với B2 hiện có, nhưng chưa hoàn tất điều kiện để gọi các run test tiếp theo là ma trận xác nhận đúng protocol.** Những điểm cần xử lý là kho donor Devign chưa thống nhất, nghiệm thu prompt bằng người, đăng ký trước, và ngưỡng validation trước test. Không sửa dữ liệu/prompt/notebook inference hoặc chạy thêm LLM trong đợt kiểm toán này.

## 1. Tình trạng các bước

| Bước/điều kiện | Kết luận | Bằng chứng và giới hạn |
|---|---|---|
| B1: backend có điểm liên tục | Đã có thực thi Kaggle; framework chính đã chọn | B2 có 4.396 record validation duy nhất, cùng model hash, Q4_K_M, llama-cpp-python 0.3.16 và tokenizer revision. Hai logits gốc dùng tính score; top-5 chỉ chẩn đoán theo quyết định kỹ thuật đã thống nhất. Không đòi chuyển sang host server. |
| B1: mọi arm thực thi cùng điều kiện | Chưa nghiệm thu toàn bộ | B0 đã có notebook inference, B1/flip/rep mới có notebook prompt. Không thấy artifact inference thật của bốn arm ngoài B2 trong bản sao này. B2 ghi seed=42 trong records nhưng constructor Llama trong notebook chưa truyền seed; B0 truyền seed=42. Vì dùng eval logits/greedy không lấy mẫu, đây không phải bằng chứng score sai, nhưng cần đồng nhất cấu hình và ghi rõ provenance. |
| B2: raw/CPG/CodeT5 và snapshot kiểm toán | Đã có | Snapshot có manifest/hash, exact/near duplicate flags và donor đã loại nhóm nhãn mâu thuẫn. Hash snapshot khớp protocol; các file snapshot được kiểm lại trong đợt này. CPG Joern và cache CodeT5 được dùng lại, không parse/encode lại. |
| B2: thực sự dùng cùng kho donor đã khóa | Chưa đạt trên Devign | Protocol trỏ kho mới 21.691 donor Devign, nhưng B2 tham chiếu được tạo từ kho 21.750 donor. 5 target validation và 16 target test dùng demo không còn đủ điều kiện trong kho mới. ReVeal: 0 demo được chọn nằm ngoài kho mới; donor_count của hai manifest cùng 17.636. Có snapshot sạch chưa đồng nghĩa B2 đã được dựng từ snapshot đó. |
| B3: prompt năm arm Tầng 1 | Đã đủ artifact và đối chiếu tự động | 20 tập prompt, tổng 50.055 mẫu; đúng ID, nhãn, hash và ngân sách theo metadata. B2-rep khớp B2 từng ký tự; B2-flip chỉ thay một câu nhãn demo; B0/B1 không có demo ID và giữ khung trống theo yêu cầu. |
| B3: nghiệm thu prompt đầy đủ | Chưa đủ bằng chứng | Có kiểm tra tự động và test; chưa tìm thấy manual_sample/biên bản hai người đọc 30 prompt mỗi dataset, hoặc audit_summary cũ theo đủ rubric. JSON của đợt kiểm toán này cung cấp token p50/p95 và cờ cắt/graph thiếu, nhưng không thay kiểm tra con người hoặc chứng nhận mọi loại rò rỉ nhãn. |
| B4: đăng ký trước | Chưa có bằng chứng hoàn thành | registered_at còn fill: YYYY-MM-DD; không có tag Git; chưa tìm thấy preregistration.md, CHANGES_AFTER_PREREG.md hoặc liên kết OSF trong các artifact kiểm tra. Có cấu hình mang version prereg-v1 chưa phải đã đăng ký trước. |
| B5: validation → khóa ngưỡng → test | Chưa đạt | Chưa tìm thấy thresholds.json. Hai notebook inference B2/B0 mặc định xếp validation rồi test trong cùng batch nhưng không có đoạn chọn/lưu ngưỡng rồi kiểm tra trước test. Chạy validation trước trong danh sách chưa đủ điều kiện của PDF. |
| B5: record/manifest và cache/resume | Đã có một phần | B2 có record, model/tokenizer hash, prompt hash và checkpoint fsync; dữ liệu inference ghép đúng cache B2. Chưa có protocol_sha256 và specs_sha256 trong manifest Kaggle B2, chưa có bộ ghi schema chung được nghiệm thu cho toàn Tầng 1. Field backend/model có tên tương đương khác schema mẫu; cần adapter hoặc schema thống nhất, không phải mất thông tin model hoàn toàn. |

## 2. Prompt hiện có: đã kiểm tra toàn bộ

| Arm | Devign validation | Devign test | ReVeal validation | ReVeal test | Tổng |
|---|---:|---:|---:|---:|---:|
| B0 | 2,732 | 2,732 | 2,273 | 2,274 | 10,011 |
| B1 | 2,732 | 2,732 | 2,273 | 2,274 | 10,011 |
| B2 | 2,732 | 2,732 | 2,273 | 2,274 | 10,011 |
| B2-flip | 2,732 | 2,732 | 2,273 | 2,274 | 10,011 |
| B2-rep | 2,732 | 2,732 | 2,273 | 2,274 | 10,011 |

- Từng tập đủ ID, không trùng ID; target code của specs B2 khớp frozen raw sau strip, nhãn khớp. B0/B1 giữ cùng prefix code và graph tương ứng B2.
- Hash prompt/manifest nguồn và đầu ra đều khớp; không phát hiện thay đổi ngoài tác động arm khi đối chiếu các biến thể.
- Không có vi phạm 8.192 token gồm dự trữ 64; graph B2 nằm trong 40 nút/80 cạnh và 1.500 token; code tối đa 3.000 và demo tối đa 1.500 theo metadata đã lưu. Đây là kiểm tra toàn bộ metadata và cấu trúc, không phải token hóa lại tất cả 50.055 prompt trong đợt này.
- B2 không có demo rỗng. Graph thiếu: Devign val/test 3/2; ReVeal val/test 27/23, tất cả được gắn cờ và dưới 5% ở từng split. B0 chủ động bỏ graph nên không tính là lỗi graph thiếu.
- Dùng full official validation: 5.005 validation + 5.006 test = 10.011 mẫu/arm. Tổng 50.055 prompt Tầng 1 khác ước tính khoảng 31.000 trong PDF vì PDF giả định chỉ lấy 600 validation mỗi dataset. Đề cương cho phép full validation khi đủ tài nguyên.

### Sai khác giao thức đã được người dùng yêu cầu

Graph 40/80 thay 25/25; B0/B1 giữ các câu dẫn trống thay vì bỏ toàn khối; Q4_K_M và raw label logits thay cách server/top-5 trong bản PDF. Đây là các quyết định đã được ghi ở tài liệu kỹ thuật, không tự coi là lỗi cần đảo ngược. Tuy nhiên, bản preregistration cuối phải mô tả đúng các variant đang chạy; protocol.yaml hiện vẫn trỏ arms.yaml canonical, chưa ghi variant B0/B1 giữ scaffold trống.

### Chênh lệch donor cần giải quyết trước ma trận xác nhận

5/2.732 Devign validation và 16/2.732 Devign test có demo B2 ngoài tập keep_in_bank của snapshot mới. Flip/rep cố ý dùng cùng demo với B2 nên kế thừa chênh lệch này. Không thể sửa riêng 21 demo rồi vẫn gọi là cùng pipeline truy hồi: kho dùng fit whitening/chọn ứng viên cũng là một phần giao thức. Cần thống nhất một bộ B2 tham chiếu đúng kho đã chốt, sau đó các arm ghép cặp bám bộ đó; CodeT5/CPG đã cache có thể tái dùng. Nếu tiếp tục bộ B2 cũ, phải mô tả rõ đây là bộ ghép cặp lịch sử/thăm dò, chưa đáp ứng kho sạch mà protocol mới khai báo.

## 3. Kết quả inference có thể xác nhận từ bản sao hiện tại

| Arm | Devign validation | ReVeal validation | Devign test | ReVeal test |
|---|---:|---:|---:|---:|
| B2 | 2.732/2.732 | 1.664/2.273 | Chưa có records local | Chưa có records local |
| B0/B1/flip/rep | Chưa có records thật local | Chưa có records thật local | Chưa có records thật local | Chưa có records thật local |

4.396 record B2 đều có score và raw hợp lệ, model hash và prompt hash khớp B2 tham chiếu. Các file trong downloaded_output_20261101_retry1 lặp lại cùng ID/timestamp; không cộng chúng như một lượt expert độc lập. Checkpoint retry1 ghi state=running với bộ đếm 0 chưa chứng minh đã chạy xong thêm mẫu. Artifact có thể còn ở Kaggle ngoài bản sao local; báo cáo này không kết luận về phần chưa nhập về.

Bản ghi Kaggle có model_repo/model_sha256/backend thay cho các tên model/backend_kind của schema mẫu; cần ghi mapping hoặc chuẩn hóa trước khi dùng script tổng hợp. Manifest hiện có model/tokenizer/prompt identity nhưng chưa ghi hash protocol/specs. B2-rep mới hoàn thành prompt: vẫn cần runner riêng thực sự gọi mới model, không lấy response B2 từ cache.

## 4. Công việc tối thiểu trước khi chạy test xác nhận

1. Thống nhất B2/flip/rep với kho donor đã chốt; ghi rõ mọi thay đổi scaffold, graph và scoring trong protocol cuối. Không thay silently demo giữa các arm.
2. Hoàn thành audit prompt Tầng 1 và việc hai người đọc 30 prompt/dataset; giữ rubric/biên bản có thể kiểm tra. B3/H2 của Tầng 3 chưa cần để nghiệm thu riêng Tầng 1.
3. Hoàn tất preregistration, commit/tag và bằng chứng đăng OSF theo đề cương, trước test xác nhận. Không gắn nhãn đã prereg cho kết quả cũ.
4. Chạy/hoàn tất validation của từng arm, chọn tau* theo lưới đã khai báo và lưu thresholds.json với identity nguồn; chỉ cho test chạy sau khi có ngưỡng arm/dataset phù hợp. Hiện ReVeal B2 validation còn thiếu 609 mẫu trong artifact local.
5. Nghiệm thu notebook inference B1/flip/rep, seed/scoring/model/tokenizer thống nhất và manifest protocol/specs. B2-rep phải là gọi mới. Resume chia phiên cùng run được phép; không phải chạy lại test để chọn cấu hình đẹp.

Có thể tiếp tục công việc validation/thăm dò, nhưng chưa có cơ sở đánh dấu các điều kiện trước test xác nhận là hoàn tất. Không cần làm lại Joern/CodeT5 để giải quyết những điểm này.

## 5. Bằng chứng tái kiểm tra

- Frozen snapshot: 16/16 file hash khớp; hash manifest tổng khớp protocol.

- `python -m pytest diagnostic_kit/tests test_logprobs.py -q`: 39 passed.
- `python -m pytest test_prepare_cached.py -q` trong tier1_prompt_tools: 13 passed.
- Chi tiết từng tập prompt, token p50/p95, flags, inference identity và ví dụ donor ngoài kho: [KIEM_TOAN_DIEU_KIEN_TANG_1.json](KIEM_TOAN_DIEU_KIEN_TANG_1.json).
- Script kiểm toán: [audit_tier1_readiness.py](audit_tier1_readiness.py); không gọi mạng/model và không sửa input. Kiểm toán chỉ xác minh dữ liệu hiện có, không tự tạo ngưỡng, preregistration hoặc chạy test.
