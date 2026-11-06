# Arm B2-labelonly — Demonstration chỉ có nhãn (Validation)

Arm chẩn đoán kiểm tra tác động của việc chỉ giữ nhãn demonstration (Label-only) mà lược bỏ toàn bộ mã nguồn và đồ thị demonstration.

## 1. Dữ liệu & Cấu hình
- **Phạm vi chạy**: Validation census (Devign 2.732 target, REVEAL 2.273 target, tổng cộng 5.005 prompt).
- **Bundle đầu vào**: `grace_b2_labelonly_validation_inputs.zip` (SHA-256: `785d0e2e92cbb4ae29ea1ae9492193b2a2491fa9a5e8e3f9a7c3ce97f6c2e361`).
- **Model**: `Qwen/Qwen3-Coder-30B-A3B-Instruct` (GGUF Q4_K_M, SHA-256: `f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335`).
- **Tokenizer revision**: `b2cff646eb4bb1d68355c01b18ae02e7cf42d120`.
- **Ngân sách token**: 8.192 tokens.

## 2. Notebook Inference trên Kaggle
- File notebook: [`notebooks/02_kaggle_qwen_q4_b2_labelonly_validation.ipynb`](notebooks/02_kaggle_qwen_q4_b2_labelonly_validation.ipynb).
- Cấu hình Kaggle runtime: GPU T4 x2, Internet Enabled, backend `llama-cpp-python==0.3.16` (CUDA SM75).
- Input gắn trên Kaggle:
  1. Prompt bundle dataset: `tomandjerry223/grace-b2-labelonly-validation-inputs`
  2. Model kernel source: `quangdung1111/qwen3coder30b-prepare-notebook`
- Đầu ra kiểm định: `records.jsonl`, `run_manifest.json`, `evaluation.json`, đóng gói thành `grace_b2_labelonly_validation_checkpoint.zip`.
