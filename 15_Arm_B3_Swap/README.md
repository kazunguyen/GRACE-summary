# Arm B3-swap — Order Swapping Probe for Contrastive Demonstration (Test Split)

Probe kiểm định độ nhạy với thứ tự trình bày của cặp demonstration tương phản. Arm này đảo ngược thứ tự hai mẫu demonstration (ví dụ: đưa mẫu Benign lên trước Vuln hoặc ngược lại) trong khi vẫn giữ nguyên giải thích Key difference.

## 1. Dữ liệu & Cấu hình
- **Mã định danh arm**: `B3-swap` (Base: `B3`, RQ liên quan: `RQ2`).
- **Khác biệt cốt lõi**: `demo: contrastive, label: true, diff: true, order: swap`.
- **Ràng buộc ngưỡng OSF**: `threshold_from: B3` — Bắt buộc kế thừa trực tiếp ngưỡng tối ưu $\tau^*$ từ Arm B3 (Nghiêm cấm dò lại ngưỡng riêng nhằm loại bỏ rủi ro p-hacking theo hợp đồng OSF).
- **Phạm vi chạy**: Test census (Devign: 2.732 target, REVEAL: 2.274 target) sau khi hoàn tất kiểm định B3 validation và khóa $\tau^*$.
- **Model**: `Qwen/Qwen3-Coder-30B-A3B-Instruct` (GGUF Q4_K_M, SHA-256: `f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335`).
- **Ngân sách token tối đa**: 8.192 tokens.

## 2. Kế hoạch Thực thi trên Kaggle
- Bundle prompt sẽ được tạo bằng cách đảo thứ tự vị trí demo 1 và demo 2 trong prompt B3.
- Chạy inference greedy (temperature 0.0, seed 42) trên backend GPU T4 x2.
- Đánh giá chẩn đoán: Đo độ suy giảm hiệu năng so với B3 để chứng minh LLM có bị thiên lệch bởi hiệu ứng vị trí (recency bias / primacy bias) hay không.
