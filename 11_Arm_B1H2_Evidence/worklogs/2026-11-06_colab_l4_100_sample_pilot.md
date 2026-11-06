# 06/11/2026 — Chuẩn bị pilot B1-H2 100 mẫu trên Colab L4

## Mục tiêu

Kiểm tra khả năng nạp model Qwen Q4_K_M đầy đủ lên một GPU L4 và lưu log offload cùng logprob cho 100 prompt B1-H2 gốc. Đây là pilot thăm dò phần cứng, không phải inference xác nhận, không dùng để chốt ngưỡng và không đưa vào bảng kết quả confirmatory.

## Đầu vào và mẫu

- Dùng đúng `D:/JUNIOR/LabThayTho/grace_15arms_prompts_and_clean_specs (1).zip`, SHA-256 `9db0d3eebb66a2f83c1f9803ceb0192954a3dfe2c3de9515188a996ede84ed7b`.
- Lấy 50 prompt Devign và 50 prompt ReVeal từ `prompts/dry_run_validation_20261102/{dataset}/validation/B1-H2/42/prompts.jsonl`.
- Chọn ngẫu nhiên không hoàn lại bằng seed `20261106`, giữ prompt gốc và xác minh từng `prompt_sha256`.
- Không thêm 100 dòng này vào specs 15-arm đã đóng băng.

## Cấu hình trong notebook

- GPU yêu cầu: Colab L4; notebook dừng nếu `nvidia-smi` báo loại khác.
- Model: `ggml-org/Qwen3-Coder-30B-A3B-Instruct-GGUF`, Q4_K_M; SHA-256 khóa theo preregistration `f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335`.
- Tokenizer: `Qwen/Qwen3-Coder-30B-A3B-Instruct`, revision `b2cff646eb4bb1d68355c01b18ae02e7cf42d120`.
- `llama-cpp-python==0.3.16`, build CUDA SM 8.9; `n_ctx=8192`, `n_batch=256`, `n_gpu_layers=-1`, `logits_all=True`, seed 42.
- Các package inference ghim theo lock/notebook hiện hành: NumPy 1.26.4, Hugging Face Hub 0.36.2, tokenizers 0.22.2, Transformers 4.57.1, scikit-learn 1.5.2.
- Ghi log `logprob_0`, `logprob_1`, `s`, greedy token và thời gian từng mẫu; lưu native stdout/stderr của llama.cpp để kiểm tra số layer offload và kích thước buffer CPU/GPU.
- Giới hạn phiên: 10 giờ; ghi từng record xuống Google Drive để có thể tiếp tục nếu runtime dừng.

## Trạng thái

Đã tạo notebook và bundle tại arm B1H2. Bundle SHA-256 là `500b523dfe05623dc5d866c218f6100048527283f92c078ec486be928cb79b59`; payload prompt SHA-256 là `7f77494714d279220f31698062ced5efa852105770959861ca2160d6777ad1fc`.

Chưa upload lên Google Drive và chưa chạy trên Colab. Máy hiện tại không có `gdrive`/`rclone` CLI; `gcloud auth list` không truy cập được cấu hình thông tin xác thực do quyền ghi sandbox vào `%APPDATA%\gcloud` bị từ chối. Vì thế chưa có link Drive để nhúng vào notebook và chưa xóa bản local. Giữ bundle local cho đến khi xác minh upload hoàn tất.

Khi chạy: nếu L4 nạp đủ model, giữ nguyên log và xem đây là kết quả pilot riêng. Nếu không load hoặc không offload đủ layer, chuyển runtime sang A100/G4 rồi chạy lại cùng bundle; không gộp kết quả giữa cấu hình GPU.
