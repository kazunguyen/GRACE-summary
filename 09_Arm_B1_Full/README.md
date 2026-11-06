# Arm B1-full — Graph đầy đủ không cắt tỉa (Validation)

Arm chẩn đoán kiểm tra tác động của việc giữ toàn bộ đồ thị ngữ cảnh (Full CPG graph) thay vì cắt tỉa 40 nodes / 80 edges như trong B1 gốc.

## 1. Dữ liệu & Cấu hình
- **Phạm vi chạy**: Validation census (Devign 2.732 target, REVEAL 2.273 target, tổng cộng 5.005 prompt).
- **Bundle đầu vào**: `grace_b1_full_validation_inputs.zip` (SHA-256: `010a57de6966c6093f47d487f3e5627ecdb3142e857abe7e5ed6db1a3147d13c`).
- **Model**: `Qwen/Qwen3-Coder-30B-A3B-Instruct` (GGUF Q4_K_M, SHA-256: `f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335`).
- **Tokenizer revision**: `b2cff646eb4bb1d68355c01b18ae02e7cf42d120`.
- **Ngân sách token**: 8.192 tokens.

## 2. Notebook Inference trên Kaggle
- File notebook: [`notebooks/02_kaggle_qwen_q4_b1_full_validation.ipynb`](notebooks/02_kaggle_qwen_q4_b1_full_validation.ipynb).
- Cấu hình Kaggle runtime: GPU T4 x2, Internet Enabled, backend `llama-cpp-python==0.3.16` (CUDA SM75).
- Input gắn trên Kaggle:
  1. Prompt bundle dataset: `tomandjerry223/grace-b1-full-validation-inputs`
  2. Model kernel source: `quangdung1111/qwen3coder30b-prepare-notebook`
- Đầu ra kiểm định: `records.jsonl`, `run_manifest.json`, `evaluation.json`, đóng gói thành `grace_b1_full_validation_checkpoint.zip`.
