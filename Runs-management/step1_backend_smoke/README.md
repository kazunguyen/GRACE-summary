# Báo cáo Nghiệm thu Bước 1: Backend Smoke Test & Thông lượng Suy luận

## 1. Tổng quan
Thư mục này lưu trữ hồ sơ bằng chứng nghiệm thu của **Bước 1: Backend LLM, Môi trường Thực thi và Smoke Test** theo đúng [Đề cương nghiên cứu hợp nhất](../../De_cuong_nghien_cuu_GRACE_hop_nhat.pdf) (Phụ lục C, trang 39, tiêu chí 2):
> *"☐ Smoke test backend: $\ge 99\%$ prompt có token 0/1 trong top-5; hai lần chạy trùng $\ge 98\%$; thông lượng đã đo."*

---

## 2. Thông số kỹ thuật Backend & Mô hình
- **Model**: `Qwen3-Coder-30B-A3B-Instruct GGUF Q4_K_M` (file: `Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf`)
- **Mã băm SHA-256**: `f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335`
- **Runtime**: `llama-cpp-python == 0.3.16`
- **Cấu hình giải mã**:
  - `temperature = 0.0` (Greedy Sampling)
  - `seed = 42`
  - `n_ctx = 8192`
  - `max_tokens = 1`
  - `top_logprobs = 5`
  - Token IDs nhị phân: Token `0` (ID: 15), Token `1` (ID: 16)
- **Công thức tính điểm (Scoring Function)**:
  $$s = \frac{e^{\text{logit}(1)}}{e^{\text{logit}(0)} + e^{\text{logit}(1)}} = \sigma(\text{logit}(1) - \text{logit}(0))$$

---

## 3. Kết quả Smoke Test & Thông lượng
- **Tỷ lệ token hợp lệ (Valid Token Rate)**: **100.0%** (20/20 mẫu trong smoke test và 10.011/10.011 mẫu trong toàn bộ mẻ B2 thực nghiệm đều có token 0 và 1 xuất hiện trong top-5 logprobs).
- **Ràng buộc ngữ pháp (`guided_choice`)**: `False` (do tỷ lệ tự nhiên đạt $100\% \ge 99\%$, không cần can thiệp ép cú pháp).
- **Độ trùng lặp tất định (Repeat Agreement)**: **100.0%** trên các mẫu chạy lặp lại với cùng seed 42.
- **Hiệu năng & Thông lượng (đo trên phần cứng Kaggle 2×Nvidia T4)**:
  - Thời gian suy luận trung bình: **6,42 giây / prompt** (Trung vị: 5,30 giây).
  - Thông lượng trung bình: **~9,35 prompts / phút**.
  - Ước tính thời gian chạy cho 10.000 mẫu: ~17,8 giờ (chia làm 2–3 session 9h trên Kaggle).

---

## 4. Danh mục tệp
- [`backend_manifest.json`](backend_manifest.json): Đặc tả toàn bộ thông số mô hình và giao thức tính điểm.
- [`smoke_test_report.json`](smoke_test_report.json): Kết quả chi tiết của 20 mẫu smoke test đối chiếu logprobs top-5.
- [`throughput_benchmark.json`](throughput_benchmark.json): Số liệu thông lượng định lượng và độ trễ trên phần cứng GPU.
