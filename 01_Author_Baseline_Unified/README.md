# GRACE Author Baseline Unified

Baseline phục dựng thống nhất; không khẳng định trùng hoàn toàn với môi trường và kết quả tác giả. Contract hiện hành: [evaluation_contract.yaml](evaluation_contract.yaml).

- Tokenizer Qwen3-Coder-30B-A3B-Instruct, revision b2cff646eb4bb1d68355c01b18ae02e7cf42d120.
- Prompt bao gồm chat template: tối đa 8.192 token; target <= 3.000, demo <= 1.500, graph <= 1.500 token.
- Graph prefix tối đa 40 node và 80 edge, cạnh phải tham chiếu đến node được giữ. Prompt B2 dùng chung renderer Figure 6 với diagnostic kit được đóng gói.
- CodeT5-base revision 02cd2d31bb7c6d0e4d91156167b2de044989c733; profile code: whitening + rerank.
- Giữ phản hồi invalid, không tự gán nhãn; checkpoint cũ khác prompt bị từ chối.

Đọc [RUN_GUIDE.md](RUN_GUIDE.md), [DIAGNOSTIC_INTEGRATION.md](DIAGNOSTIC_INTEGRATION.md). Quyết định cũ tại [ARCHITECTURE_DECISIONS.md](ARCHITECTURE_DECISIONS.md) là lịch sử, trừ phần cập nhật đầu file. Không trộn kết quả hợp đồng byte cũ với hợp đồng token.

Model inference đã chọn là `ggml-org/Qwen3-Coder-30B-A3B-Instruct-GGUF` Q4_K_M qua llama.cpp; `backbone_llm` BF16 trong contract là nguồn tokenizer và đường chạy Transformers cũ. Xem [hướng dẫn hai notebook](RUN_GUIDE_KAGGLE.md). Chưa kiểm chứng model hay GPU trên Kaggle.
