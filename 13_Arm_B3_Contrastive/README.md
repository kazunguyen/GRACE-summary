# Arm B3 — Contrastive Demonstration + Key Difference (Validation & Test)

Arm chẩn đoán kiểm tra tác động của việc cung cấp cặp demonstration tương phản (1 hàm dễ bị tổn thương và 1 hàm an toàn có ngữ cảnh tương đồng) kèm theo khối giải thích sự khác biệt cốt lõi ("Key difference").

## 1. Dữ liệu & Cấu hình
- **Mã định danh arm**: `B3` (Base: `B1`, RQ liên quan: `RQ2`, `RQ4`).
- **Khác biệt cốt lõi**: `demo: contrastive, label: true, diff: true, order: normal`.
- **Phạm vi chạy Validation**: Census toàn bộ tập validation đã chuẩn hóa (Devign: 2.732 target, REVEAL: 2.273 target; tổng cộng 5.005 prompt).
- **Phạm vi chạy Test**: Census toàn bộ tập test đã chuẩn hóa (Devign: 2.732 target, REVEAL: 2.274 target; tổng cộng 5.006 prompt) sau khi khóa ngưỡng $\tau^*$.
- **Model**: `Qwen/Qwen3-Coder-30B-A3B-Instruct` (GGUF Q4_K_M, SHA-256: `f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335`).
- **Tokenizer revision**: `b2cff646eb4bb1d68355c01b18ae02e7cf42d120`.
- **Ngân sách token tối đa**: 8.192 tokens (Target code $\le 3.000$, Graph $\le 1.500$, Demo pair + Key diff $\le 1.500$, Reserve: 64 tokens).
- **Thứ tự prompt chuẩn (Figure 6)**:
  `[role_domain -> target_code -> question -> node_info -> edge_info -> demonstration -> answer]`.

## 2. Notebook Inference trên Kaggle
- File notebook: [`notebooks/02_kaggle_qwen_q4_b3_validation.ipynb`](notebooks/02_kaggle_qwen_q4_b3_validation.ipynb).
- Kernel Kaggle: `thanhduy9a4tv/grace-b3-validation`.
- Cấu hình Kaggle runtime: GPU T4 x2, Internet Enabled, backend `llama-cpp-python==0.3.16` (CUDA SM75).
- Input gắn trên Kaggle:
  1. Prompt bundle dataset: `thanhduy9a4tv/grace-b3-validation-inputs-v2` (chứa toàn bộ prompt Devign & REVEAL có nhãn và metadata).
  2. Model kernel source: `thanhduy9a4tv/qwen3coder30b-prepare-notebook` (đã nạp sẵn 18.5GB GGUF).

## 3. Đầu ra kiểm định
- Thư mục đầu ra dự kiến: `output/` (hoặc `runs/final/{devign,reveal}/validation/B3/42/`).
- Artifacts: `records.jsonl`, `run_manifest.json`, `evaluation.json`.
