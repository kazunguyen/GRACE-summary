# Đọc tay Bước 3 cho gói validation 10 arm

Trạng thái: bộ mẫu và phiếu đã sẵn sàng, chờ hai người đọc độc lập. Mỗi người đọc cùng 60 prompt, 30 Devign và 30 ReVeal, dùng rubric gốc. Nộp hai phiếu riêng trước khi đối chiếu và lập biên bản. Phiếu và packet không có nhãn target, kết quả inference hay verdict trước.

Giữ 45 mẫu trong packet ngày 04/11 thuộc đúng 10 arm, cộng 8 Devign và 7 ReVeal từ manifest validation-only. Chọn bổ sung tất định theo thứ tự SHA-256 của 42, dataset, arm, seed và ID. Ưu tiên phủ tập arm–seed chưa có mẫu, rồi bù vào tầng ít mẫu nhất theo độ dài (<2.000, 2.000–4.499, ≥4.500 token) và cờ cắt. Không dùng verdict để chọn. Bộ mẫu phủ đủ 28 tập và mọi prompt đã kiểm SHA-256.

Kết quả lịch sử ghi riêng trong historical_exact_matches.json. Có 31 prompt khớp đầu vào gói chạy, gồm 15 Devign và 16 ReVeal. Bộ 60 mới không trùng các mẫu lịch sử theo khóa đầy đủ. Không dùng phiếu lịch sử hoặc phiếu Codex thay thế hai lượt đọc bộ mới.

- [Bộ đọc](manual_packet.md)
- [Phiếu 1](reviewer_1.csv)
- [Phiếu 2](reviewer_2.csv)
- [Rubric gốc](../../prompt_audit_20261102/RUBRIC.md)

## Rà Codex

[Phiếu Codex](reviewer_codex.csv) ghi 58 pass, 2 unclear. Giữ 45 kết quả trước theo đúng hash và chấm thêm 15 mẫu. SHA-256 phiếu: `bfd87ce8473e13b281fe73de6098ec2e482663d1f8582559489cb15e058bfeb4`. Hai phiếu độc lập vẫn chờ người chấm.
