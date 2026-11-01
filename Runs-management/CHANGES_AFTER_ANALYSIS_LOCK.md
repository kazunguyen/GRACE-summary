# Nhật ký sau analysis-lock-20261101-v1

## 01/11/2026 — Hoàn thiện vận hành helper và kiểm tra notebook

Sau tag local lúc 17:03:42 Asia/Bangkok, bổ sung watcher local (không đọc test), tài liệu vận hành và kiểm tra source hai notebook Kaggle đã nhúng đúng helper/kiểm tra ngưỡng. Test core tăng từ 4 lên 5, cộng 8 test B0. Không thay grid, objective, tie-break, điều kiện đủ validation, ba khóa ban đầu hoặc model/prompt inventory đã niêm phong. Watcher chỉ thêm khóa cho arm/dataset mới khi đủ kết quả tương ứng; khóa cũ vẫn bất biến.

Không sửa các file snapshot trong analysis_lock_20261101 hoặc viết lại tag. OSF vẫn chưa công bố; không đổi trạng thái thành preregistered. Bản checkpoint Git giữ nguyên source test tại thời điểm niêm phong; test bổ sung hiện ở working tree là kiểm tra vận hành sau đó.

## 01/11/2026 — Nhập hoàn tất inference B2 I-05

Đã nhập và hợp nhất output Kaggle I-05 với I-02/I-04: B2 đạt 10.011/10.011 prediction, 0 invalid, không có conflict; xem [I-05 và merge manifest](RUNS.md) cùng artifact canonical trong `01_Author_Baseline_Unified/output/local_full/inference_qwen_q4_b2_20261101/`. Watcher đã khóa B2/ReVeal tau=0,12 từ đủ validation (MCC=0,082299); ba khóa ban đầu và quy tắc chọn ngưỡng không đổi. Test REVEAL đã được chạy một phần trong I-04 trước thời điểm khóa B2/ReVeal; phần còn lại chạy trong I-05 sau khóa. Vì vậy không gắn nhãn toàn bộ run là tuân thủ thứ tự validation→khóa→test. Đây là cập nhật trạng thái đầu ra và lịch sử tiếp xúc test; không thay đổi protocol/template đã niêm phong, không sửa tag hoặc gói OSF.
