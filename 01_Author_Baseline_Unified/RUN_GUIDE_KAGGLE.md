# Chạy GRACE B2 và Qwen3-Coder Q4_K_M

Hai notebook tách chuẩn bị prompt và inference. Model được chọn là `ggml-org/Qwen3-Coder-30B-A3B-Instruct-GGUF`, biến thể `Q4_K_M`, chạy bằng `llama-cpp-python`; đây là thay đổi so với các lượt BF16 cũ. Notebook sẽ xác định revision Hugging Face, tải đúng file và lưu SHA-256 trong run manifest. Ghim revision thu được trước lượt xác nhận.

## 1. Chuẩn bị đầu vào có CPG

Notebook 01 tự tải Devign và ReVeal theo revision ghi trong `evaluation_contract.yaml`, sau đó trích lại CPG cho ba split. Không cần tự chuẩn bị ba file JSONL. File trung gian có ID ổn định, mã C/C++, nhãn 0/1 và danh sách node/edge Joern, chẳng hạn:

```json
{"id":"devign:validation:8","func":"int f(void) { return 0; }","target":0,"nodes":[{"id":"n1","type":"METHOD","code":"int f(void)"}],"edges":[]}
```

Đây là ví dụ schema, không phải CPG thật. `edges` dùng `start`/`end`/`type`; ID cạnh phải tham chiếu tới node. Notebook mặc định dùng Joern WSL đã xác minh tại `/home/yungn/tools/joern/y/joern-cli`; `prepare_joern_cpg.py` gọi Joern, xuất GraphML và ghi checkpoint/manifest theo từng split. Nếu Joern không hoạt động, bước preflight sẽ dừng. Nếu một hàm riêng lẻ không trích được, mẫu vẫn được giữ với graph rỗng, cờ thiếu và lý do lỗi. Cần kiểm tra tỷ lệ lỗi và provenance CPG trước khi đánh giá. Devign dùng ID nguồn; ReVeal dùng vị trí dòng trong split cố định vì hash nguồn không duy nhất, không tự coi ID này khớp run lịch sử.

Không thay split hoặc lọc test theo kết quả. Công cụ loại trùng chính xác theo code đã strip và nhóm nhãn xung đột; kiểm toán gần trùng và tính toàn vẹn nhãn/split vẫn phải hoàn thành riêng trước xác nhận.

## 2. Tạo bundle trên máy chuẩn bị

Mở `notebooks/01_prepare_grace_b2.ipynb` bằng Jupyter kernel Python chạy trong WSL. Cài các phụ thuộc trong `requirements.in` hoặc môi trường đã khóa; cần Internet để tải dữ liệu, CodeT5 và tokenizer theo revision trong contract. Notebook đã điền sẵn repo và Joern; chạy lần lượt tất cả cell. Mặc định xử lý đầy đủ cả Devign/ReVeal và tạo bundle validation/test, không giới hạn mẫu. Output và checkpoint nằm tại `output/local_full/<dataset>/`; chạy lại cell để tiếp tục sau khi ngắt. Khối lượng trích CPG và embedding rất lớn, có thể kéo dài nhiều giờ hoặc nhiều ngày; theo dõi CPU, RAM và dung lượng đĩa.

File prompt chứa mã nguồn và nhãn phục vụ đánh giá: chỉ upload lên Kaggle Dataset riêng được phép sử dụng. ZIP không chứa model, khóa hay source repository.

## 3. Inference trên Kaggle

Tạo Kaggle Dataset riêng từ ZIP, mở `notebooks/02_kaggle_qwen_q4_b2.ipynb`, bật GPU và Internet, Add Input dataset. Sửa `BUNDLE_PATH`. Ban đầu giữ `LIMIT=20`, chạy theo thứ tự. Notebook cài `llama-cpp-python` với CUDA, tải Q4_K_M từ Hugging Face, ghi revision model và tính SHA-256 file. Một model Kaggle khác không được tự coi là cùng checkpoint; chỉ dùng file Add Input sau khi kiểm tra đúng repository/revision/hash.

Notebook dùng tokenizer Qwen theo revision của bundle, đối chiếu ID token toàn bộ prompt với tokenizer GGUF và dừng nếu khác. Lấy logits gốc của token đầu cho `0` và `1`, không ràng buộc grammar; lưu `records.jsonl`, `run_manifest.json` và `evaluation.json`. Metric có ngưỡng dùng token greedy hợp lệ; AUROC/AUPRC dùng score `s` khi đủ hai lớp. `s` tính từ hai logits; `raw` là token greedy toàn vocab, có thể không phải 0/1. Mỗi dòng lưu prompt hash, nhãn, ID demo và token counts. Checkpoint chống trộn model/bundle. `B2` là baseline duy nhất trong notebook này; các arm khác, B3 và ngưỡng chưa được chạy.

`logits_all=True` có thể dùng khoảng 5 GiB RAM CPU cho ma trận 8192 × 151936, ngoài 18 GB trọng số, KV cache và overhead. 2×T4 không được bảo đảm đủ và Kaggle có thể ngắt phiên. Nếu OOM hoặc CUDA build lỗi, lưu log và điều chỉnh phần cứng trước khi chốt protocol; không âm thầm đổi quantization hay context. Đầu ra trong `/kaggle/working` có thể mất khi phiên kết thúc: tải ZIP và records sớm.

Sau smoke test, kiểm tra số dòng, `valid`, `response_valid`, hai logprob hữu hạn, score, tỉ lệ graph thiếu, thời gian và kiểm tra prompt thủ công. Đặt `LIMIT=None` và thư mục output mới để chạy đầy đủ. Test xác nhận chỉ chạy sau khi protocol và ngưỡng đã khóa trên validation. Chưa có kết quả GPU hay model Qwen thật được xác nhận trong repo.
