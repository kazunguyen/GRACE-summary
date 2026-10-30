# Chạy GRACE B2 và Qwen3-Coder Q4_K_M

Hai notebook tách chuẩn bị prompt và inference. Model được chọn là `ggml-org/Qwen3-Coder-30B-A3B-Instruct-GGUF`, biến thể `Q4_K_M`, chạy bằng `llama-cpp-python`; đây là thay đổi so với các lượt BF16 cũ. Notebook sẽ xác định revision Hugging Face, tải đúng file và lưu SHA-256 trong run manifest. Ghim revision thu được trước lượt xác nhận.

## 1. Chuẩn bị đầu vào có CPG

Notebook 01 cần ba file JSONL `train`, `validation`, `test` của cùng dataset đã khóa. Mỗi dòng cần ID ổn định, mã C/C++, nhãn 0/1 và danh sách node/edge Joern, chẳng hạn:

```json
{"id":"devign:validation:8","func":"int f(void) { return 0; }","target":0,"nodes":[{"id":"n1","type":"METHOD","code":"int f(void)"}],"edges":[]}
```

Đây là ví dụ schema, không phải CPG thật. `edges` dùng `start`/`end`/`type`; ID cạnh phải tham chiếu tới node. Cần cùng phiên bản Joern và xác minh nguồn/hash CPG. Nếu chưa có CPG, chạy notebook 01 bằng kernel Linux/WSL, đặt `EXTRACT_CPG=True`, đường dẫn `JOERN_HOME` chứa `joern-parse` và `joern-export`, cùng ba file thô có `id`, `func`, `target`. Script `prepare_joern_cpg.py` gọi Joern, xuất GraphML, lọc CPG theo hàm và ghi checkpoint/manifest cho từng split. Cần tự cài Joern trước; script dừng nếu Joern lỗi hoặc không thấy AST hàm. Chưa kiểm thử Joern thật trong môi trường này, vì vậy phải thử trên vài mẫu và kiểm tra graph trước khi trích đầy đủ. Nguồn graph prefix khôi phục từ prompt lịch sử chỉ dùng để thử, không thay cho CPG đầy đủ. Mặc định notebook dừng nếu thiếu graph; `ALLOW_MISSING_GRAPHS=True` chỉ để chạy thăm dò và manifest ghi lại điều đó.

Không thay split hoặc lọc test theo kết quả. Công cụ loại trùng chính xác theo code đã strip và nhóm nhãn xung đột; kiểm toán gần trùng và tính toàn vẹn nhãn/split vẫn phải hoàn thành riêng trước xác nhận.

## 2. Tạo bundle trên máy chuẩn bị

Mở `notebooks/01_prepare_grace_b2.ipynb` trong Jupyter. Cài các phụ thuộc trong `requirements.in` hoặc môi trường đã khóa; cần truy cập/tải CodeT5 và tokenizer theo revision trong contract. Sửa `ROOT`, `TRAIN`, `VALIDATION`, `TEST`, `DATASET`, `SPLIT`. Nếu trích Joern, thiết lập thêm `EXTRACT_CPG`, `JOERN_HOME`, `RAW_TRAIN`, `RAW_VALIDATION`, `RAW_TEST`; `LIMIT` chỉ giới hạn số prompt, không giới hạn bước trích CPG. Bắt đầu `LIMIT=20`; chạy các cell. Notebook dùng CodeT5, whitening, retrieval và prompt Figure 6; tạo `specs.jsonl`, `prompts.jsonl`, manifest và ZIP tại `OUT`. Sau khi kiểm tra, đặt `LIMIT=None` để tạo bundle toàn bộ split. Mỗi lần chạy chọn thư mục riêng để giữ provenance.

File prompt chứa mã nguồn và nhãn phục vụ đánh giá: chỉ upload lên Kaggle Dataset riêng được phép sử dụng. ZIP không chứa model, khóa hay source repository.

## 3. Inference trên Kaggle

Tạo Kaggle Dataset riêng từ ZIP, mở `notebooks/02_kaggle_qwen_q4_b2.ipynb`, bật GPU và Internet, Add Input dataset. Sửa `BUNDLE_PATH`. Ban đầu giữ `LIMIT=20`, chạy theo thứ tự. Notebook cài `llama-cpp-python` với CUDA, tải Q4_K_M từ Hugging Face, ghi revision model và tính SHA-256 file. Một model Kaggle khác không được tự coi là cùng checkpoint; chỉ dùng file Add Input sau khi kiểm tra đúng repository/revision/hash.

Notebook dùng tokenizer Qwen theo revision của bundle, đối chiếu ID token toàn bộ prompt với tokenizer GGUF và dừng nếu khác. Lấy logits gốc của token đầu cho `0` và `1`, không ràng buộc grammar; lưu `records.jsonl`, `run_manifest.json` và `evaluation.json`. Metric có ngưỡng dùng token greedy hợp lệ; AUROC/AUPRC dùng score `s` khi đủ hai lớp. `s` tính từ hai logits; `raw` là token greedy toàn vocab, có thể không phải 0/1. Mỗi dòng lưu prompt hash, nhãn, ID demo và token counts. Checkpoint chống trộn model/bundle. `B2` là baseline duy nhất trong notebook này; các arm khác, B3 và ngưỡng chưa được chạy.

`logits_all=True` có thể dùng khoảng 5 GiB RAM CPU cho ma trận 8192 × 151936, ngoài 18 GB trọng số, KV cache và overhead. 2×T4 không được bảo đảm đủ và Kaggle có thể ngắt phiên. Nếu OOM hoặc CUDA build lỗi, lưu log và điều chỉnh phần cứng trước khi chốt protocol; không âm thầm đổi quantization hay context. Đầu ra trong `/kaggle/working` có thể mất khi phiên kết thúc: tải ZIP và records sớm.

Sau smoke test, kiểm tra số dòng, `valid`, `response_valid`, hai logprob hữu hạn, score, tỉ lệ graph thiếu, thời gian và kiểm tra prompt thủ công. Đặt `LIMIT=None` và thư mục output mới để chạy đầy đủ. Test xác nhận chỉ chạy sau khi protocol và ngưỡng đã khóa trên validation. Chưa có kết quả GPU hay model Qwen thật được xác nhận trong repo.
