# Nộp bản cập nhật cho đăng ký GRACE trên OSF

Soạn ngày 06/11/2026. Tài liệu này hướng dẫn tác giả tự nộp; việc chuẩn bị/commit không đồng nghĩa đã nộp hoặc được duyệt trên OSF.

## Các tệp dùng khi nộp

- [OSF_JUSTIFICATION_EN.txt](OSF_JUSTIFICATION_EN.txt): sao chép toàn bộ vào ô Justification.
- [OSF_UPDATE_EN.md](OSF_UPDATE_EN.md): mục 2 là toàn bộ phương pháp và khai báo cập nhật; mục 3 là các liên kết bằng chứng theo commit cố định. Đây là bản tiếng Anh dùng để điền form.
- [BANG_CHUNG_NGUONG_VALIDATION.md](BANG_CHUNG_NGUONG_VALIDATION.md): giải thích bằng chứng bằng tiếng Việt để nhóm đối chiếu.

Phần phương pháp đã có bảng ngưỡng cũ/mới, thiết kế B3 thay thế và các probe, Colab L4/runtime, điều kiện thực nghiệm giữ nguyên và khai báo công việc đã thực hiện. Không cần dán bản kế hoạch do người khác gửi vào OSF.

## Thao tác trên OSF

1. Đăng nhập tài khoản có quyền **Admin** đối với [đăng ký gốc](https://osf.io/fqgh2/overview).
2. Trên trang đăng ký, chọn **Updates > Update**. Nếu không thấy, vào **My Registrations > Submitted**, tìm đăng ký GRACE và chọn **Update**. Nút chỉ hiện với Admin.
3. Trong tab **Justification**, dán toàn bộ `OSF_JUSTIFICATION_EN.txt`. Văn bản này đã dẫn commit `d9127fc7b12a128d8499012454ad134733f810ff` chứa mã và bằng chứng validation-only.
4. Mở các câu hỏi có nội dung cần sửa. Form sẽ điền sẵn câu trả lời cũ. Áp dụng nội dung mục 2 của `OSF_UPDATE_EN.md`, rồi bổ sung các liên kết chứng cứ ở mục 3. Có thể phân vào các câu hỏi tương ứng theo bảng dưới; không tự giả định form có những tên trường cụ thể.

| Nội dung trên form | Phần của bản tiếng Anh |
|---|---|
| Phương pháp phân tích hoặc ngưỡng quyết định | B1. Threshold correction and analysis status |
| Thiết kế thí nghiệm, demonstration hoặc B3 | B2. Replacement of the B3 method |
| Quy trình inference, nền tảng/phần cứng hoặc môi trường | B3. Additional compute platform, GPU and runtime |
| Dữ liệu đã có, tiến độ hoặc lịch sử phân tích | B4. Retrospective disclosure of work already completed |
| Nguồn mã, tài liệu hỗ trợ hoặc phần bổ sung | 3. Immutable evidence references |

5. Nếu template ban đầu chỉ có một câu trả lời văn bản dẫn PDF, giữ dẫn chiếu bản gốc và bổ sung toàn bộ mục 2-3 vào câu trả lời văn bản đó. Ghi rằng các phần được chỉ định trong PDF được đính chính bởi update hiện tại. Không chỉ đổi Description/metadata rồi coi là đã cập nhật phương pháp. OSF yêu cầu thay ít nhất một trường câu trả lời ngoài Justification.
6. Mở từng liên kết GitHub E1-E13 để chắc chắn người xem truy cập được. Đọc lại ngưỡng `B0: 0.98/0.30`, `B1: 0.98/0.63`, B2 giữ `0.70/0.12`; xác nhận B3 mới được mô tả là phương pháp sắp triển khai, không phải bộ cặp đã nghiệm thu. Các dữ liệu/trạng thái là snapshot ngày 06/11; cập nhật nếu đã có thêm lượt chạy trước lúc Submit.
7. Chọn **Review**, kiểm tra phần hiển thị thay đổi rồi **Submit**. Ngày hiệu lực phải là thời điểm OSF thực tế ghi nhận, không tự đặt lùi về ngày soạn tài liệu.
8. Các Admin nhận email phê duyệt hoặc từ chối. Theo hướng dẫn OSF, update tự phê duyệt sau 48 giờ nếu không có phản đối, với ngoại lệ registry có kiểm duyệt. Trong thời gian chờ, trạng thái có thể là **Update in progress**.
9. Sau khi công khai, lưu URL/version/thời điểm của update, bản sao câu trả lời đã nộp và email biên nhận. Ghi thêm vào `CHANGES_AFTER_PREREG.md`; chỉ khi đó mới ghi update đã nộp/đã duyệt theo trạng thái thực tế.

## Giới hạn về tệp đính kèm

OSF **không cho thêm, xóa hay thay tệp trong một Update**. PDF/ZIP gốc được giữ nguyên. Các liên kết GitHub theo commit cố định trong bản tiếng Anh cung cấp mã, dữ liệu validation và output kiểm chứng. Có thể lưu thêm một bản đính chính trên OSF Project liên kết và dẫn URL, nhưng tệp trên Project không tự trở thành tệp đính kèm bất biến của registration.

Nếu template gốc chỉ có trường upload tệp và hoàn toàn không có câu trả lời văn bản sửa được, không thể giả định thêm PDF qua Update. Phương án thay thế là tạo một registration bổ sung cho amendment, dẫn đăng ký gốc, khai báo dữ liệu/phân tích đã có và liên kết hai hồ sơ; giữ nguyên đăng ký gốc. Chọn phương án này chỉ khi đã xác nhận giới hạn thực tế của form.

## Dẫn chứng và khả năng chạy lại

Commit bằng chứng: [d9127fc7b12a128d8499012454ad134733f810ff](https://github.com/kazunguyen/GRACE-summary/commit/d9127fc7b12a128d8499012454ad134733f810ff).

- Hàm tối ưu gốc khớp từng byte với commit ngày 01/11, SHA-256 được ghi trong hồ sơ.
- Mã verifier ngày 06/11 chỉ gọi lại hàm gốc; không viết lại quy tắc tối ưu.
- Gói ZIP chứa đúng bốn tệp validation nguyên byte và inventory SHA-256, tổng 10.010 records. Không chứa test.
- Đã chạy thành công trong thư mục cô lập chỉ có hai mã nguồn và bốn validation. Log và audit ghi đúng bốn ngưỡng, không mở đọc test.
- Bộ kiểm tra theo AGENTS.md đạt **37 passed**; đây là kiểm tra tính toàn vẹn và code, không xác nhận B3 mới đã được triển khai.

Nguồn quy trình: [OSF Support - Update a Registration](https://help.osf.io/article/330-welcome-to-registrations#Update-a-Registration). Hướng dẫn dựa trên tài liệu chính thức; form thực tế của tài khoản chưa được thao tác trong lần chuẩn bị này.
