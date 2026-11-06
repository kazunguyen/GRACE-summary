# Hướng dẫn chấm prompt độc lập

Trạng thái: CHƯA CHẤM. Hai phiếu đang để trống; không thay cho hai người đánh giá thực tế.
Mỗi người đọc cùng 60 prompt trong manual_packet.md, tự điền phiếu riêng trước khi trao đổi.
Không dùng kết quả model hoặc nhãn target để lựa chọn mẫu/đánh giá prompt.

Mỗi tiêu chí điền pass / fail / unclear / not_applicable và ghi lý do, vị trí cụ thể khi fail/unclear:
- target_code_intact: code target đúng mẫu, cắt ngắn có làm mất ngữ cảnh thiết yếu không.
- graph_valid: graph đúng target, có nội dung hợp lý; B0 chủ động không có graph là not_applicable.
- demo_valid: code demo và nhãn theo đúng biến thể; B0/B1 không có demo là not_applicable.
- no_target_label_leak: không có đáp án target bị chèn từ metadata; nhãn demo đúng thiết kế không phải rò rỉ.
- variant_correct: B0 khung trống; B1 graph + demo trống; B2 có demo; flip đảo nhãn demo; rep giống B2; rand donor ngẫu nhiên.
- truncation_acceptable: phần còn lại có thể hiểu được; demo dưới 25% gốc là cờ vi phạm contract cần xử lý.
- overall_verdict: pass / fail / unclear. Điền reviewer_name và thời điểm chấm thực tế.

Sau khi cả hai nộp phiếu, đối chiếu từng bất đồng và lập biên bản phân xử riêng. Không ghi đè phiếu ban đầu.
Bộ mẫu chọn không dựa metric test: bảo đảm arm/phiên/seed, phân tầng độ dài và cờ cắt bằng kit, seed 42, bù đủ 30 mỗi dataset.
Các mẫu lỗi tự động nằm trong remediation_rows.csv, không thay đổi bộ mẫu chỉ để loại bỏ ví dụ xấu.
