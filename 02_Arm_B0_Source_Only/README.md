# B0 — source code, giữ khung prompt B2

1. Chạy [notebook sinh prompt](notebooks/01_prepare_b0_prompts.ipynb) bằng Python local/WSL trong repo. Nó đọc snapshot `01_Author_Baseline_Unified/output/research_freeze_20261101`, tải đúng tokenizer revision và xuất bốn bundle Devign/REVEAL validation/test. Không cần CPG, donor, CodeT5 hoặc GPU cho bước này. Bật `INSTALL_DEPENDENCIES=True` nếu cần cài thư viện.
2. Upload `output/bundles/grace_b0_inputs.zip` vào Kaggle Dataset của account bạn muốn dùng. Có thể giữ nguyên ZIP hoặc giải nén qua Kaggle.
3. Import [notebook inference Kaggle](notebooks/02_kaggle_qwen_q4_b0.ipynb), bật Internet và GPU T4 ×2. Add Input dataset prompt và model Q4_K_M nếu đã có. Notebook tự tìm dưới `/kaggle/input`, không cố định username/slug; nếu chưa có model thì tải Hub và kiểm SHA-256.
4. Chạy các cell theo thứ tự. Mặc định xử lý bốn split, validation trước test; có thể sửa `EXPECTED_RUNS` để chỉ chạy validation. Ngân sách inference là 8 giờ, chừa 5 phút đóng checkpoint. Tải `grace_b0_checkpoint.zip` và `grace_b0_diagnostics.zip` từ Output.
5. Phiên/account sau: gắn lại input prompt/model và checkpoint B0 bằng Add Input. Bật `RESUME=True` (mặc định). Notebook tự tìm checkpoint, kiểm identity model/prompt/label và bỏ qua ID đã chạy. Nếu gắn các checkpoint/bundle khác nội dung cho cùng split thì notebook báo xung đột.

## Nội dung prompt

Biến thể `b0_b2_empty_blocks_v1`, arm `B0`: chỉ code target mang dữ liệu mẫu. Giữ đúng các câu ROLE, QUESTION, NODE_HEAD, EDGE_HEAD và ANSWER của renderer B2 trong baseline. Giữ khung câu dẫn demo nhưng xóa cả nhãn và mã demo:

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

[TARGET CODE: cùng cách cắt B2, tối đa 3.000 token]

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:

The edge information of the code snippet is as follows:

The following is an example, and it is .

Answer (0 or 1):
```

Khoảng xuống dòng thực tế được giữ theo cách ghép khối của B2; xem `prompt_preview.txt` sau khi sinh bundle. Không có ID/nhãn/mã demo, node hoặc edge trong payload. Nhãn target chỉ nằm trong metadata để chấm điểm, không truyền vào renderer. `graph_missing=False` vì graph được chủ động bỏ trống; có cờ `graph_intentionally_empty` riêng.

Biến thể này khác B0 bỏ hẳn cả khối graph/demo trong PDF. Nếu so với kết quả B0 khác, phải đối chiếu `prompt_variant` và hash. Đã ghi thay đổi theo yêu cầu trong sổ ma trận.

## Model, score và output

Giữ Qwen3-Coder-30B-A3B-Instruct Q4_K_M, llama-cpp-python 0.3.16, model SHA-256 `f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335`, tokenizer revision `b2cff646eb4bb1d68355c01b18ae02e7cf42d120`. Không ép grammar; tính score từ logits gốc bằng hàm canonical đã nhúng trong runtime. Top-5 chỉ để chẩn đoán. Mỗi record lưu arm, variant, prompt hash, seed, token counts, hai logprob, score, raw và cờ hợp lệ. Checkpoint fsync từng record, resume kiểm model/prompt/label.

Mỗi split có `records.jsonl`, `run_manifest.json`, `evaluation.json` khi hoàn tất. Metric raw greedy kèm coverage; metric score tại ngưỡng 0,5 được tách riêng; AUROC/AUPRC dùng score. Notebook không chọn ngưỡng từ test. Dữ liệu/prompt mới chưa được đánh dấu là lượt xác nhận đã đăng ký trước.

Ghi chú lịch sử lúc bàn giao notebook: hai notebook khi đó chưa chạy. Hiện B0 I-03 đã có đủ 10.011 output; xem [README chung](../README.md) và [RUNS.md](../Runs-management/RUNS.md), không suy ra nghiệm thu protocol từ số lượng output. Đã kiểm tra offline cú pháp notebook, scaffold/truncation, tìm input nhiều account, ZIP lồng, xung đột, checkpoint an toàn và luồng prepare → inference → resume với backend giả. Các kiểm tra đó không đại diện cho throughput hay nghiệm thu CUDA thực tế.
