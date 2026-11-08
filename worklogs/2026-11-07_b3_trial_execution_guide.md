# Hướng dẫn Thử nghiệm B3 (Contrastive Demonstration) trên Kaggle GPU — 07/11/2026

## 1. Khái quát và Trạng thái Nghiên cứu

Thuật toán B3 nguyên bản đối mặt với thách thức không có cặp mẫu patch đối chứng (vulnerable vs patched diff) tự nhiên trong kho donor của Devign và ReVeal (do Devign gom các commit riêng lẻ, còn ReVeal là các lát cắt Debian không liên kết). Để tuân thủ đúng cam kết OSF Pre-registration:
1. **Điều kiện dừng (Pause Condition):** Nếu không có ngân hàng cặp mẫu được duyệt bởi 2 thẩm định viên độc lập (dual-reviewer approved), pipeline B3 bắt buộc phải dừng và không được suy diễn dữ liệu ngẫu nhiên.
2. **Thuật toán Amended B3 (`VerifiedPairSelector`):** Khi có ngân hàng cặp patch được thẩm định, thuật toán tính độ tương đồng Mean Jaccard Token giữa code target và hai phiên bản (vulnerable và patched) của cặp demo, trích xuất đoạn khác biệt bảo mật (`diff_text`), dựng prompt theo đúng chuẩn Hình 6 của bài báo GRACE cho cả 4 nhánh:
   - `B3`: Vulnerable demo trước -> Patched demo sau -> Key difference.
   - `B3-nodiff`: Vulnerable demo trước -> Patched demo sau -> Không kèm Key difference.
   - `B3-swap`: Patched demo trước -> Vulnerable demo sau -> Key difference.
   - `B3-flip`: Đảo ngược nhãn và nội dung mô tả trong Key difference (`Vulnerable` <-> `Non-vulnerable`, `safe` <-> `unsafe`).

---

## 2. Các Bước Thực thi Thử nghiệm B3 trên Kaggle

### Bước 1: Xác nhận và Kiểm thử Pipeline Local
Chạy kiểm tra tự động toàn diện thuật toán B3:
```powershell
python scripts/test_b3_amended_pipeline.py
python -m pytest tests/test_amended_b3.py
```
Toàn bộ 20 tests của bộ kiểm thử B3 và 5 tests tích hợp của `test_b3_amended_pipeline.py` phải PASS 100%.

### Bước 2: Chuẩn bị Notebook và Staging
Script `Runs-management/build_and_launch_b3_amended_kaggle.py` tự động xuất bản notebook:
- `13_Arm_B3_Contrastive/notebooks/02_kaggle_qwen_q4_b3_amended_validation.ipynb`
- Staging tại: `Runs-management/kaggle_staging_lznt123/b3_amended_test_run/`
- Metadata: `lznt123/grace-b3-validation`

### Bước 3: Đẩy và Chạy trên Kaggle GPU (2x Tesla T4)
- **Tài khoản Kaggle:** `lznt123`
- **Môi trường:** GPU Tesla T4 x2, Internet ON.
- **Dữ liệu gắn vào Notebook (Inputs):**
  1. `lznt123/qwen3coder30b-prepare-notebook`: Chứa mô hình `Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf` (SHA-256 `f6050b4da...`).
  2. `lznt123/grace-b3-validation-inputs` hoặc bộ specs test/validation.
- **Khởi chạy:**
  ```powershell
  python Runs-management/build_and_launch_b3_amended_kaggle.py
  ```
  Hoặc truy cập trực tiếp Kaggle web UI và chọn **Save Version -> Run All**.

### Bước 4: Kiểm tra Cơ chế Scoring Chuẩn xác
Notebook đã được sửa đổi và kiểm định để **loại bỏ hoàn toàn lỗi thoái hóa điểm về 0.5000** của `create_completion(logprobs=20)`:
- Chuyển sang cơ chế canonical `llm.eval` trên full-vocabulary logits vị trí cuối (`binary_scores`).
- Tính điểm continuous $s = \frac{p(1)}{p(0) + p(1)}$ bằng `logaddexp` số thực kép `float64`.
- Điểm số không bị kẹt ở 0.5000 và phản ánh chính xác phân phối xác suất của mô hình.

### Bước 5: Thu thập Báo cáo và Đóng gói Artifacts
Khi phiên Kaggle hoàn tất:
- File kết quả: `/kaggle/working/grace_b3_amended_validation_output.zip`
- Chẩn đoán: `/kaggle/working/grace_diagnostics.zip`
- Tải về và đặt trong `13_Arm_B3_Contrastive/output/` để phục vụ đối chiếu và kiểm định.
