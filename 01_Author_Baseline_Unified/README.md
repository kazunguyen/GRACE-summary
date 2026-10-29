# GRACE Author Baseline Unified

Baseline đối chứng được nhóm thống nhất từ mã GRACE, với hợp đồng đánh giá 8.192 byte. Đây là bản phục dựng, không khẳng định giống nguyên trạng toàn bộ môi trường tác giả.

- [Hướng dẫn cài đặt và chạy](RUN_GUIDE.md)
- [Hợp đồng đánh giá](evaluation_contract.yaml)
- [Quyết định kiến trúc](ARCHITECTURE_DECISIONS.md)
- `requirements.in`: các phụ thuộc trực tiếp; `requirements.lock`: toàn bộ phụ thuộc Python đã giải và hash.
- `run_pipeline.py`: điều phối; `test_baseline.py`: kiểm thử offline.

Model sinh: [Qwen3-Coder-30B-A3B-Instruct](https://huggingface.co/Qwen/Qwen3-Coder-30B-A3B-Instruct/tree/b2cff646eb4bb1d68355c01b18ae02e7cf42d120), BF16, revision `b2cff646eb4bb1d68355c01b18ae02e7cf42d120`. Model embedding: [CodeT5-base](https://huggingface.co/Salesforce/codet5-base/tree/02cd2d31bb7c6d0e4d91156167b2de044989c733), revision `02cd2d31bb7c6d0e4d91156167b2de044989c733`.
