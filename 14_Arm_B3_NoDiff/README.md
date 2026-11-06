# Arm B3-nodiff — Contrastive Demonstration Without Key Difference (Validation & Test)

Arm chẩn đoán kiểm tra tác động của việc giữ nguyên cặp demonstration tương phản (1 hàm dễ bị tổn thương và 1 hàm an toàn) nhưng **lược bỏ hoàn toàn khối giải thích Key difference**.

## 1. Dữ liệu & Cấu hình
- **Mã định danh arm**: `B3-nodiff` (Base: `B3`, RQ liên quan: `RQ2`).
- **Khác biệt cốt lõi**: `demo: contrastive, label: true, diff: false, order: normal`.
- **Phạm vi chạy Validation**: Census toàn bộ tập validation đã chuẩn hóa (Devign: 2.732 target, REVEAL: 2.273 target; tổng cộng 5.005 prompt).
- **Phạm vi chạy Test**: Census toàn bộ tập test đã chuẩn hóa sau khi khóa ngưỡng $\tau^*$.
- **Model**: `Qwen/Qwen3-Coder-30B-A3B-Instruct` (GGUF Q4_K_M, SHA-256: `f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335`).
- **Tokenizer revision**: `b2cff646eb4bb1d68355c01b18ae02e7cf42d120`.
- **Ngân sách token tối đa**: 8.192 tokens.

## 2. Notebook Inference trên Kaggle
- File notebook: Chạy song song trong batch bundle với B3 tại kernel [`thanhduy9a4tv/grace-b3-validation`](../13_Arm_B3_Contrastive/notebooks/02_kaggle_qwen_q4_b3_validation.ipynb).
- Bundle đầu vào: Tích hợp trong dataset `thanhduy9a4tv/grace-b3-validation-inputs-v2`.
- Cấu hình runtime: GPU T4 x2, Internet Enabled, `llama-cpp-python==0.3.16`.

## 3. Đầu ra kiểm định
- Thư mục đầu ra dự kiến: `output/` (hoặc `runs/final/{devign,reveal}/validation/B3-nodiff/42/`).
- Artifacts: `records.jsonl`, `run_manifest.json`, `evaluation.json`.
