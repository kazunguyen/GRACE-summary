# Bổ sung B1-shuf: bản nháp, chưa đăng ký

Trạng thái: CHƯA đăng OSF; CHƯA commit/tag; CHƯA có review prompt thật hoặc smoke test backend của lượt này. Không dùng file này làm bằng chứng đã đăng ký trước.

- Ngày/giờ đăng ký: [điền thời điểm thật].
- Commit nguồn và hash artifact: [điền sau chuẩn bị/audit].
- Lịch sử tiếp xúc test và kết quả đã có trước đăng ký: [liệt kê trung thực].
- B1 tham chiếu: [đường artifact + hash manifest/prompt thực tế]. Scaffold `b1_b2_empty_demo_v1`, giữ câu dẫn demo trống; graph 40/80, <=1.500 token. Đây là điều chỉnh so với prefix 25/25 và scaffold trong PDF.
- Donor: train cùng dataset, snapshot `research_freeze_20261101`, hash donor/snapshot từ manifest đầu ra. Số nút ghép cỡ là CPG đầy đủ. Chọn theo `(id,seed)` bằng thuật toán, mức nới và làm tròn biên ghi trong manifest; không ép donor khác nhau giữa seed.
- Seed chọn graph: 42 (chính), 43, 44 (độ nhạy). Seed inference: 42, không đổi model/quant/scoring/template giữa B1 và B1-shuf.
- Thiếu graph target: giữ B1 nguyên trạng, donor null, gắn cờ; báo tỷ lệ toàn bộ và phân tích coverage. Không diễn giải các mẫu này như đã nhận graph donor. Graph thiếu >5%: xử lý trước khi kết luận.
- Phép so ghép cặp: `delta = AUROC(B1) - AUROC(B1-shuf)`; metric chính AUROC, biên tác dụng 0,02; MCC bổ sung, biên 0,03 theo protocol chung. Seed 42 chính, báo đủ ba seed; không chọn seed đẹp nhất. Không gộp ba lần cùng target như ba mẫu độc lập.
- Cách chọn tau* trên validation (từng dataset/seed), tie-break, invalid, bootstrap/cluster, Holm và cách báo biến thiên seed: [ghi chính xác theo protocol đã khóa]. Khóa ngưỡng trước inference test.
- Backend thực dùng và kiểm tra tương thích B1: [model SHA-256, quant, phiên bản, tokenizer revision, logits/scoring]. Nếu dùng native logits như protocol hiện tại, nêu rõ thay đổi so với scoring top-5 trong PDF.
- Audit: [hash báo cáo, số lượng, phạm vi], hai người đọc: [tên, ngày, kết quả]. Smoke test backend: [artifact và kết quả].
- Sau đăng ký: ghi mọi thay đổi vào `CHANGES_AFTER_PREREG.md`, không ghi lùi ngày. Các lượt đã chạy trước đăng ký không chuyển thành xác nhận bằng việc thêm tag.

Chỉ hoàn tất và đưa vào protocol nghiên cứu sau khi kiểm tra các trường còn trống; file này không tự sửa protocol chung và không tạo đăng ký OSF.
