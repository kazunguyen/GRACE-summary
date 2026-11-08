# Chuẩn bị chạy bù test B2-rand ba seed

Log seed 44 ở mốc 800/2.732 Devign tại 6.912,6 giây. Deadline từ tham số worker là 03:14:50 GMT+7 ngày 08/11/2026. Mốc ngừng nhận mẫu mới là 03:09:50, với kiểm tra dự phòng từng mẫu có thể dừng sớm khoảng 30 giây. So với đường tiến độ seed 42 và 43, dự kiến seed 44 hoàn tất Devign và dừng quanh **1.900–2.000/2.274 REVEAL**. Đây là dự báo từ tốc độ hiện có. Số thực tế lấy từ checkpoint cuối.

Chuẩn bị [bộ chạy bù](../06_Arm_B2_Rand/test_tail_delivery_20261107/README.md). Dùng checkpoint I-18/I-19 đối chiếu ID, label, prompt hash và ngưỡng cố định trước khi loại các mẫu đã chạy. Seed 44 lấy chính xác phần chưa có record khi nạp checkpoint cuối. Các record mới giữ provenance riêng dưới runtime lock hiện tại. Các ngưỡng 42/43 đối chiếu khớp giá trị và hash dữ liệu nguồn giữa hai khóa validation đã có.

Kiểm tra local đã biên dịch các code cell và chạy phần nạp input với cả ZIP nguyên và thư mục đã giải nén, dùng checkpoint seed 44 giả lập chỉ trong thư mục tạm. Chưa chạy CUDA hoặc inference notebook mới trên Kaggle.

## Điều chỉnh theo yêu cầu: cắt seed 44 ở vị trí 1.900

Thay phương án nạp checkpoint cuối seed 44 bằng mốc cố định. Bundle mới chọn 374 prompt REVEAL từ vị trí 1.901 đến 2.274 của seed 44, cộng 257 của seed 42 và 246 của seed 43, tổng 877. Vị trí là thứ tự trong bundle gốc. Notebook bắt đầu được với bundle mới và GGUF. Khi có output thật của seed 44, đối chiếu ID trước khi ghép để phát hiện thiếu hoặc trùng.
