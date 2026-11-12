# Hướng dẫn chấm mù độ liên quan của demo

Mở [gói 30 ca](cases.md). Mỗi người điền phiếu được giao và gửi riêng cho người điều phối. Chấm độc lập trước khi trao đổi.

## Cách chấm từng ca

1. Đọc **Target** để xác định cơ chế cần đối chiếu. Đọc từng demo A và B theo đúng phần mã hiển thị.
2. Với từng demo, điền bốn cột: `sink` là thao tác liên quan đến cơ chế, `variable` là biến hoặc dữ liệu, `guard` là điều kiện kiểm tra, `evidence` là dòng mã củng cố nhận định. Dùng `khop`, `khong_khop`, `khong_ap_dung` hoặc `thieu_ngu_canh`. Dùng `khong_ap_dung` khi tiêu chí không có ý nghĩa với cơ chế đang xét.
3. Ở cột `ket_luan`, điền `A`, `B`, `Both` hoặc `Neither` theo demo nào có căn cứ liên quan về cơ chế. Nếu ngữ cảnh không đủ để quyết định, dùng `Unclear`. Không ép `Unclear` thành `Neither`.
4. Ghi dòng và lý do ngắn vào `can_cu_a` và `can_cu_b`, ví dụ `T12–18, A7–10: cùng dữ liệu đi qua điều kiện kiểm tra tương ứng`. T là Target. Các số dòng thuộc từng khối trong gói. Dùng cột `ghi_chu` cho phần mã bị thiếu hoặc trường hợp khó phân loại.

## Phiếu chấm

- [Phiếu người chấm 1](reviewer_1.csv)
- [Phiếu người chấm 2](reviewer_2.csv)

Mỗi phiếu đã có mã ca theo thứ tự trong gói. Giữ nguyên cột `ma_ca`. Hai người gửi phiếu riêng sau khi hoàn thành.
