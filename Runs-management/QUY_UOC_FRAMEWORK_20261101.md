# Quy ước dữ liệu, graph và score cho ma trận

<!-- donor-rerun-risk-note -->
**Lưu ý phiên dữ liệu đang chạy:** snapshot donor mới đã tồn tại nhưng cache B2 hiện tại chưa tự chuyển sang kho đó. Phân biệt chiến dịch B2 cũ với phiên dùng kho thống nhất; đánh giá nguy cơ chạy lại theo [NGUY_CO_CHAY_LAI_DO_DONOR.md](NGUY_CO_CHAY_LAI_DO_DONOR.md). Không sửa ngầm prompt hoặc dùng ghi chú này để kích hoạt inference lại.
<!-- /donor-rerun-risk-note -->

Ngày chốt kỹ thuật: 01/11/2026. Đây là quyết định kỹ thuật chuẩn bị; chưa phải đăng ký trước và chưa nghiệm thu prompt/GPU. Không thay thế artifact lịch sử.

## Dữ liệu và retrieval

Snapshot chính thức dùng cho các notebook arm tiếp theo: `../01_Author_Baseline_Unified/output/research_freeze_20261101/`. `freeze_manifest.json` chứa hash đầu vào, hash các file đầu ra và hash script. Mỗi dataset có raw train/validation/test, manifest từng split, danh sách cặp gần trùng, `donors.jsonl` và `stats.json`.

Chuẩn hóa bằng token C/C++: bỏ comment và khoảng trắng định dạng, giữ nguyên literal chuỗi/ký tự; băm danh sách token để tránh nhập nhằng khi nối token. Không sửa mã dùng cho inference. Trùng chính xác: loại train trùng validation/test; loại toàn bộ nhóm train có nhãn mâu thuẫn; nhóm trùng cùng nhãn giữ một đại diện theo ID tăng dần. Validation/test giữ nguyên. Gần trùng: Jaccard tập token 3-gram >=0,9, tính chính xác với prefix join, chỉ đánh dấu. Hàm dưới ba token dùng cả chuỗi token làm một shingle. Cờ eval đối chiếu toàn train gốc, kể cả donor đã bị loại; báo cáo đầy đủ và subset không gần trùng. Không dùng MinHash làm kết luận.

Mọi arm phải truy hồi/chọn donor từ snapshot mới này. Giữ full official validation (Devign 2.732, REVEAL 2.273), không lấy subset 600. Những demo/prompt cũ cần dựng lại hoặc đối chiếu với donor snapshot trước khi được tính vào ma trận xác nhận. Cache CodeT5 có thể tái sử dụng theo ID/hash code. Graph donor lấy từ snapshot CPG Joern cuối ngày 31/10; graph thiếu được giữ và phải gắn cờ ở giai đoạn tạo prompt.

## Graph

Mọi arm graph dùng trần 40 nút / 80 cạnh và 1.500 token. B1/B2 và các biến thể prefix dùng cùng cách cắt. B1-shuf áp dụng trần cho graph donor.

B1-full tìm prefix nút lớn nhất vừa ngân sách và giữ các cạnh nội bộ đủ điều kiện trong trần 80. B1 prefix giảm cạnh trước khi giảm nút khi quá token. Vì cùng trần 40/80, hai arm có thể tạo prompt giống nhau nếu graph đã vừa ngân sách. Khi tạo notebook phải báo tỷ lệ prompt trùng B1/B1-full; nếu trùng toàn bộ thì ghi rõ đây là đối chứng dư thừa, không diễn giải là thử graph lớn hơn.

H2 phải chọn graph nguồn <=40 nút / 80 cạnh trước khi trích evidence; specs phải có `h2_source_limits: {nodes: 40, edges: 80}` (hoặc số nhỏ hơn), kèm evidence tối đa 1.500 token. Renderer từ chối evidence không khai báo giới hạn nguồn. Metadata là ràng buộc giao diện; notebook H2 tương lai còn phải lưu và kiểm chứng node/cạnh nguồn. Chưa tạo evidence H2 trong công việc này.

## Score và backend

Chọn `llama-cpp-python 0.3.16`, Qwen3-Coder-30B-A3B-Instruct GGUF Q4_K_M, cùng model SHA-256 đã ghi ở lượt Kaggle: `f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335`. Tokenizer revision: `b2cff646eb4bb1d68355c01b18ae02e7cf42d120`. Greedy, seed 42, context 8.192 token, không grammar/guided choice. Model path trong backend config được chỉnh theo vị trí file, hash phải giữ đúng.

Score chung là `sigmoid(logit_1-logit_0)` từ logits gốc tại vị trí đầu ra đầu tiên. Hai nhãn phải là hai token đơn khác nhau, tokenizer HF/GGUF khớp cả nhãn lẫn toàn chat prompt. Top-5 chỉ để chẩn đoán: token nhãn ngoài top-5 không làm mất score. `valid` là score hợp lệ; `response_valid` là token greedy toàn vocab có phải 0/1. Lưu cả hai logprob, score, raw và `pred_argmax=s>=0.5`. Metric theo raw greedy phải kèm coverage và tách khỏi metric theo score/ngưỡng validation. Không đổi invalid thành nhãn 0.

Hàm canonical ở `diagnostic_kit/src/grace_diag/native_scoring.py`, được Kaggle B2 và runner ma trận dùng chung. Runner từ chối API top-k cho lượt nghiên cứu này; các backend API cũ vẫn được giữ cho công việc lịch sử. Native scorer đánh giá mới mỗi prompt (không cache phản hồi), do đó B2-rep luôn gọi model lại. Resume vẫn dựa trên records của từng arm. **Cập nhật 01/11/2026:** backend Qwen Q4_K_M/llama-cpp-python 0.3.16 đã chạy inference Kaggle B2 trên đủ bốn split (10.011 records; xem I-05 trong [RUNS.md](RUNS.md)); điều này xác nhận lượt B2 đã thực thi trên GPU Kaggle, không phải kiểm thử mọi backend/arm của ma trận.
