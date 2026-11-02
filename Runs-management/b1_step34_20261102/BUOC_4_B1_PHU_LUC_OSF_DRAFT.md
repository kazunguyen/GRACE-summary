# B1 — phụ lục hồ sơ đăng ký, bản nháp chờ duyệt

**BẢN NHÁP LOCAL; CHƯA GỬI OSF.** Soạn sau inference, không phải preregistration hồi tố. Phụ lục này cập nhật riêng B1 và phải được đọc cùng hồ sơ nghiên cứu [OSF_DRAFT.md](../osf_registration_draft_20261102/OSF_DRAFT.md). Hồ sơ cũ có số B1/B2-rand đã lỗi thời; cần cập nhật toàn văn và inventory trước khi gửi, không thay số ngầm trong bản snapshot cũ.

## Phạm vi và lịch sử đã biết

B1 gồm code target + graph 40 node/80 edge theo budget và scaffold demo trống; không dùng demo. Qwen3-Coder-30B-A3B-Instruct GGUF Q4_K_M, model SHA-256 `f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335`; tokenizer revision `b2cff646eb4bb1d68355c01b18ae02e7cf42d120`; llama-cpp-python 0.3.16. B1 đã sinh đủ 10.011 record: Devign validation/test 2.732/2.732 và REVEAL validation/test 2.273/2.274. Năm raw response không hợp lệ; score đều hợp lệ. Hash input/output ghi trong `b1_posthoc_audit.json`.

Lượt I-07 bắt đầu inference ngày 01/11 17:17:36 Asia/Bangkok và đã chứa 429 Devign test; I-08 hoàn thành ngày 02/11 13:32:01. Bản analysis-lock local được lập sau khi inference nghiên cứu bắt đầu; chưa có bằng chứng B1 khóa tau trước test. B1 test và một số kết quả đã được tiếp xúc; không tuyên bố kết quả này là đánh giá xác nhận được preregister trước test. Các đánh giá và giả thuyết so sánh chứa B1 cần công bố mức tiếp xúc và coi là hậu kiểm/thăm dò khi thích hợp.

## Audit và cách xử lý sau này

Audit tự động B1 là hậu kiểm; hai phiếu chấm còn trống, chờ hai người thật và phân xử. Graph thiếu giữ cờ. Chưa có bằng chứng đánh giá bằng người hoặc OSF registration. Không đổi prompt/output hoặc viết lại lịch sử.

Quy tắc tau đã có trong analysis lock: grid 0,01–0,99, chọn MCC validation cao nhất, hòa chọn gần 0,5 rồi thấp hơn; dùng đủ validation đúng identity, không dùng test để chọn. Nếu tính sau khi test đã chạy, ghi ngày thật và báo là khóa hậu kỳ; không gọi là đã khóa trước test. Score raw, score-valid và raw-valid được báo riêng. Việc chỉ tính lại trên validation không khôi phục tính mù đối với kết quả test đã tiếp xúc.

## Chờ chủ nhiệm quyết định trước khi gửi

Tác giả/cơ quan/quyền và người chịu trách nhiệm; lựa chọn public/embargo; xác nhận đầy đủ lịch sử đã xem; các endpoint H2.2, họ Holm, quy tắc CI suy biến và REVEAL grouping đang pending trong hồ sơ tổng. Cập nhật tiến độ tất cả arm và provenance trước khi tạo attachment gửi OSF. Phân định dữ liệu/phân tích đã biết với phần tương lai đủ điều kiện xác nhận; không suy từ thời điểm soạn hoặc hash là thời điểm đăng ký. Phải có URL/trạng thái xác nhận OSF thực tế mới ghi đã đăng ký.
