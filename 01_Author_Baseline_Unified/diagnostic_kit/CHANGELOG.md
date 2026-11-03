# Thay đổi của bộ công cụ

## v1.1 — 2026-11-03 (trước khi khóa giao thức)

Ba sửa đổi bắt buộc trước khi đăng ký trước; cả ba đều ảnh hưởng đến tính hợp lệ của điểm số và ngưỡng,
không chỉ là tiện ích.

1. **Ngưỡng τ\* tách khỏi bước đánh giá test.** Mô-đun mới `grace_diag.thresholds` đọc *chỉ* records
   `validation` (+ `anchor_scores.csv`), chọn τ\* = argmax MCC trên lưới 0,01..0,99 (hòa → gần 0,5), ghi
   `runs/thresholds.json` kèm sha256 của mọi file đầu vào và của chính nội dung (`locked_sha256`); ghi lại
   khi nội dung đổi sẽ sao lưu bản cũ và cảnh báo. `evaluate_final.py` nay **bắt buộc** `--thresholds`, chỉ
   đọc file đã khóa, từ chối chạy nếu một arm có test mà không có ngưỡng (không còn mặc định 0,5), và không
   ghi `thresholds.json` nữa (chỉ ghi `thresholds_used.json` để đối chiếu). Thứ tự bắt buộc:
   validation → `thresholds` → commit → test → `evaluate_final`.
2. **Probe lặp/đảo thừa kế ngưỡng của arm gốc.** `arms.yaml` thêm `threshold_from`: B2-rep, B2-flip dùng
   τ\* của B2; B3-flip, B3-swap dùng τ\* của B3. Chọn lại ngưỡng cho một arm đã bị đảo nhãn hay lặp sẽ
   "sửa" chính hiệu ứng cần đo và trộn thêm biến động do chọn ngưỡng.
3. **B2-rep luôn gọi model mới.** Trước đây B2-rep dựng cùng prompt với B2 nên runner đọc lại cache của
   B2 — lượt "lặp" chỉ sao chép câu trả lời cũ. Nay arm `repeat: true` gọi `score(..., use_cache=False,
   tag="repeat")`; khóa cache gồm `tag` nên không bao giờ trùng với arm gốc; records ghi `cache_tag`.
   Lượt B2-rep nào trước đây được phục vụ từ cache phải chạy lại (ghi vào bảng kê tiếp xúc).
4. **Token vắng trong top-k không còn nhận p = 0.** `parse_top_logprobs` gán cho token 0/1 vắng mặt cận
   trên p ≤ p(token thấp nhất trong top-k), trả thêm `both_in_topk`, `s_bounded`; `top_logprobs` mặc định
   20 (vLLM: `--max-logprobs 20`); smoke test đạt khi ≥ 99 % prompt có **cả hai** token và ≥ 98 % trùng
   nhãn giữa hai lần gọi. Bảng A báo `s_bounded_rate`. Lượt cũ đã lưu nguyên dict top-k thì tính lại
   offline được; lượt chỉ còn nhãn 0/1 thì không dùng được cho τ\*/AUROC.
5. `protocol.yaml`: thêm `thresholds.{rule,tie_break,inherit,order,locked_file}` và khối `exposure_ledger`
   (bảng kê arm × split × ngày chạy × chỉ số đã xem × hành động) để điền trước khi tag `prereg-v1`.

Kiểm thử: `pytest -q` → 31 passed; chạy thử với server giả: B2 và B2-rep cùng prompt_sha256, 12 request
mới cho 6 target × 2 arm, cache chỉ có 6 mục của B2; `evaluate_final` không có `--thresholds` → lỗi tham số.

## v1.0 — 2026-10-28

Bản đầu kèm đề cương hợp nhất.
