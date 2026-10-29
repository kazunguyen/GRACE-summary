# Hướng Dẫn Vận Hành & Thực Nghiệm Baseline Thống Nhất

Tài liệu này cung cấp các kịch bản chạy thực nghiệm và kiểm thử mã nguồn baseline thống nhất cho GRACE tác giả tại `d:\JUNIOR\LabThayTho\GRACE-summary\01_Author_Baseline_Unified`.

---

## 1. Kiểm Thử Nhanh (Smoke Test & Unit Tests Offline)

Baseline được thiết kế để có thể **chạy lại được ngay lập tức** mà không cần GPU và không cần cấu hình mạng/API key.

### 1.1. Chạy bộ kiểm thử tự động (Unit & Integrity Tests)
```bash
python test_baseline.py
```
**Kết quả mong đợi**: Chạy hoàn tất 5 bài kiểm tra cốt lõi trong khoảng 15 giây:
1. `test_strict_parser_compliance`: Kiểm tra parser nghiêm ngặt dòng cuối 0/1, từ chối câu trả lời sai định dạng.
2. `test_prompt_budget_strictly_capped_at_8192_bytes`: Kiểm tra trần 8.192 bytes UTF-8 và thứ tự cắt xén.
3. `test_hybrid_reranker_formula`: Kiểm tra công thức 0.7 Jaccard + 0.3 AST.
4. `test_evaluator_metrics_on_valid_population`: Kiểm tra tính toán ma trận nhầm lẫn, MCC, Invalid rate.
5. `test_end_to_end_mock_pipeline`: Chạy luồng end-to-end hoàn chỉnh sinh toàn bộ artifacts.

### 1.2. Chạy thử nghiệm nhanh chế độ Mock qua CLI
```bash
python run_pipeline.py --mock --dataset mock --max-targets 10 --experiment-name dry_run_test
```
Sau khi chạy, kết quả được xuất ra thư mục `output/dry_run_test/`:
- `prompts.jsonl`: Danh sách prompt đã render và giới hạn dưới 8.192 bytes.
- `raw_responses.jsonl`: Phản hồi thô kèm số lượt retry và metadata model.
- `predictions.jsonl`: Kết quả bóc tách nhãn nghiêm ngặt.
- `evaluation.json`: Toàn bộ chỉ số benchmark dưới dạng JSON.
- `report.md`: Báo cáo nghiệm thu Markdown trực quan.

---

## 2. Chạy Thực Nghiệm Thật Qua API

### 2.1. Sử dụng FPT Cloud / FPT AI Factory
1. Đảm bảo file cấu hình tại `D:/JUNIOR/LabThayTho/.env` chứa các thông số:
   ```bash
   FPT_API=sk-xxxxxxxxxxxxxxxxxxxxxxxx
   FPT_MODEL=DeepSeek-V4-Flash
   FPT_BASE_URL=https://token-api.fpt.ai/v1
   ```
2. Thực thi pipeline với dataset mong muốn:
   ```bash
   # Chạy trên 100 mẫu thử nghiệm Devign
   python run_pipeline.py --dataset devign --max-targets 100 --experiment-name devign_fpt_run1

   # Hoặc chạy toàn bộ test set Devign (tỷ lệ 1.0)
   python run_pipeline.py --dataset devign --sample-ratio 1.0 --experiment-name devign_fpt_full
   ```
*(Lưu ý: Baseline tự động tắt thinking mode cho DeepSeek-V4-Flash để bảo vệ ngân sách 256 tokens).*

### 2.2. Sử dụng Google Vertex AI
1. Thiết lập biến môi trường dự án Google Cloud:
   ```powershell
   $env:VERTEX_PROJECT="your-gcp-project-id"
   $env:VERTEX_LOCATION="us-central1"
   ```
2. Thực thi pipeline:
   ```bash
   python run_pipeline.py --dataset devign --max-targets 50 --experiment-name devign_vertex_test
   ```

---

## 3. Cơ Chế Khôi Phục Tiến Trình (JSONL Checkpointing)

Trong quá trình gọi API hàng nghìn mẫu kiểm thử, nếu tiến trình bị gián đoạn (mất mạng, hết hạn mức quota, timeout máy tính):
- Hệ thống tự động lưu từng mẫu hoàn thành vào file `checkpoints/<experiment_name>_checkpoint.jsonl` và thực hiện `os.fsync()` ngay lập tức.
- Khi người dùng chạy lại lệnh ban đầu với cùng `--experiment-name`:
  ```bash
  python run_pipeline.py --dataset devign --sample-ratio 1.0 --experiment-name devign_fpt_full
  ```
- Hệ thống sẽ tự động phát hiện file checkpoint cũ, bỏ qua các mẫu đã hoàn thành và tiếp tục gọi các mẫu còn lại mà không tiêu tốn lại chi phí API.

---

## 4. Chuyển Đổi Hồ Sơ Tác Giả: Code-based vs Paper-based

- Mặc định là hồ sơ **Code-based** (CodeT5 768d + BERT-Whitening 256d + FAISS IP + Reranker 0.7 Jaccard / 0.3 AST Levenshtein):
  ```bash
  python run_pipeline.py --profile code ...
  ```
- Khi muốn so sánh đối chiếu với phương án **Paper-based** (CodeT5 + t-SNE 2D + khoảng cách L2):
  ```bash
  python run_pipeline.py --profile paper ...
  ```

---

## 5. Quy Trình Mở Rộng & Phát Triển Cải Tiến (C1 - C8)

Mã nguồn tại `01_Author_Baseline_Unified` được chuẩn hóa làm **nền tảng mốc gốc (Golden Baseline)**. Khi nhóm phát triển các cải tiến mới, hãy tuân thủ nguyên tắc:
1. Tạo thư mục hoặc branch mới dựa trên baseline này (ví dụ: `02_Enhancement_C1_HybridRetrieval`).
2. Giữ nguyên các hằng số bất biến của Contract:
   - `evaluation_contract.yaml` (8.192 bytes context limit).
   - Ngân hàng ứng viên `candidate_pool_size: 50`.
   - Parser nghiêm ngặt `parser.py` (không heuristic ép nhãn).
   - Quần thể đánh giá valid-only và theo dõi tỷ lệ invalid.
3. Thay thế độc lập từng module cải tiến để đo lường chính xác hiệu quả đóng góp (Ablation Study).
