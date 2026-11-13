# Bước 8 chấm mù thăm dò 30 ca ngày 12/11/2026

Gói chấm mù thăm dò cho RQ6 gồm 15 ca Devign và 15 ca ReVeal. Mỗi ca có mã ẩn danh, mã nguồn target và hai demo A/B đã tráo thứ tự. Hai nguồn demo là B2 và B2-rand seed 42. Prompt được đối chiếu với hash trong records đã chạy, và phần prompt trước demo khớp theo từng target. Bản phát cho người chấm ẩn nguồn demo, nhãn benchmark, dự đoán và score. [Gói STEP8](../STEP8_blind_review/README.md)

Nguyen Quang Dung đã điền phiếu người chấm 2 đủ **30/30 ca**. Kiểm tra xác nhận mã ca khớp gói, các giá trị rubric và kết luận hợp lệ, và mỗi ca có căn cứ cho cả hai demo. Năm trích dẫn vượt số dòng hiển thị ở CA-09, CA-12, CA-14, CA-15 và CA-18 đã được sửa và kiểm tra lại. Phiếu và gói chấm được đưa lên `dung` trong commit `cbd611f` với message “Nguyen Quang Dung hoàn thành việc chấm mù”. [Phiếu người chấm 2](../STEP8_blind_review/reviewer_packet/reviewer_2.csv)

## Cập nhật 12/11/2026: phiếu người chấm 1

- Đã hoàn thành [phiếu người chấm 1](../STEP8_blind_review/reviewer_packet/reviewer_1.csv) (Nguyễn Hữu Hiếu), đủ **30/30 ca**, chấm độc lập.
- Lưu ý: phiếu 2 đã có trong repo từ commit `cbd611f` (21:11) trước khi điền phiếu 1. Phiếu 2 không được mở trong lúc chấm phiếu 1.
- Đã kiểm tra cả hai phiếu: mã ca khớp gói; mọi giá trị rubric và kết luận nằm trong danh mục cho phép; mọi trích dẫn dòng trong `can_cu_a` và `can_cu_b` nằm trong phạm vi khối Target/Demo A/Demo B tương ứng của `cases.md`.

## Đồng thuận trước hòa giải

| Cột | Tỷ lệ trùng | Cohen’s κ |
|---|---:|---:|
| `ket_luan` | 30/30 | 1,00 |
| 8 tiêu chí thành phần (`sink`, `variable`, `guard`, `evidence` của demo A và B) | 30/30 mỗi cột | 1,00 |

- Phân bố kết luận: 15 ca A, 15 ca B; không ca nào chọn `Both`, `Neither` hay `Unclear`.
- Không có ca bất đồng nên không cần người phân xử.

## Cách đọc kết quả và giới hạn

- **Khuôn kết quả tất định.** Ở cả 60 dòng (30 ca × 2 người chấm), demo được chọn nhận `khop` ở mọi tiêu chí áp dụng, còn demo kia nhận `khong_khop` ở mọi tiêu chí. Vì vậy κ của các tiêu chí thành phần lặp lại κ của cột kết luận, không cho thêm thông tin độc lập.
- **Thiết kế gói đặt một demo truy hồi (B2) cạnh một demo ngẫu nhiên (B2-rand).** Theo căn cứ ghi trong phiếu, demo được chọn ở mọi ca thuộc cùng họ hàm, cùng API hoặc cùng module với target, còn demo kia thuộc dự án hoặc chức năng khác. Như vậy kết quả cho thấy độ tương đồng về mã và chức năng giữa target và demo, chưa đánh giá độ liên quan về **cơ chế lỗ hổng**. Một số ca là mã test hoặc khởi tạo (ví dụ CA-05, CA-25) vẫn được chấm `guard = khop`.
- **Còn cần đối chiếu bảng khóa A/B** (`coordinator_only/answer_key.csv`, Dũng giữ riêng ở máy) để xác nhận demo được chọn có luôn là demo B2 hay không. Nếu đúng, có thể viết ở mức mô tả: "demo truy hồi cùng họ hàm với target ở 30/30 ca; demo ngẫu nhiên không cùng họ ở ca nào".
- **Gói này không kiểm định H6.1.** H6.1 đánh giá chính demo truy hồi có liên quan cơ chế với target hay không (tỷ lệ "Neither" ≥ 40% trên Devign), cùng phần audit nhãn. Gói 30 ca là đợt thăm dò; phần chấm đầy đủ của RQ6/H6.1 vẫn thuộc Giai đoạn 2. [Trạng thái RQ6 trong báo cáo](2026-11-12_bao_cao_metric_cac_arm_hoan_tat.md)
