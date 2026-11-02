# Bản ghi giao thức và kế hoạch phân tích sau khi đã bắt đầu inference

Thời điểm thực tế: 2026-11-01T17:02:28.614281+07:00 (Asia/Bangkok), tương ứng 2026-11-01T10:02:28.614281+00:00 UTC.

Đây là bản ghi phân tích có thời điểm, **không phải đăng ký trước hồi tố**. Người dùng xác nhận inference đã chạy trước thời điểm này. Kết quả validation B2 đã được xem trong giai đoạn trước; hiện có thêm B0 validation. Tiến độ test trên các tài khoản Kaggle ngoài bản sao local không được xác nhận. Những run đã bắt đầu trước bản ghi giữ trạng thái thăm dò/đã tiếp xúc; không sửa timestamp, không gọi chúng đã được preregistered.

## Phạm vi và cấu hình

Tầng 1 gồm B0, B1, B2, B2-flip, B2-rep trên Devign/REVEAL; full official validation và test. Chạy Kaggle GPU, Qwen3-Coder-30B-A3B-Instruct Q4_K_M, model SHA-256 `f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335`, tokenizer revision `b2cff646eb4bb1d68355c01b18ae02e7cf42d120`, llama-cpp-python 0.3.16. Graph trần 40/80, ngân sách 1.500 token; code 3.000; demo 1.500; tổng 8.192 gồm chat template và dự trữ 64. B0/B1 giữ scaffold B2 trống theo yêu cầu; flip chỉ đảo nhãn, rep giữ nguyên prompt và gọi model mới. Danh sách hash prompt/variant của 20 tập nằm trong protocol.analysis.json.

Giữ bộ B2 ghép cặp hiện đang chạy; không thay donor/model/prompt trong phiên inference. Đã biết B2 Devign có 5 prompt validation và 16 prompt test dùng demo ngoài kho donor mới trong protocol template. Vì vậy không tuyên bố toàn bộ run hiện tại đã tuân thủ kho mới. Nếu tạo B2 mới từ kho mới, phải tạo phiên giao thức khác và dùng lại đúng B2 đó cho flip/rep. Chưa nghiệm thu thay thế metadata seed bằng backend seed ở các run lịch sử; notebook B2 mới truyền seed=42, logits/greedy không lấy mẫu.

## Quy tắc chọn ngưỡng đã cố định

Score từ logits gốc là sigmoid(logit_1-logit_0), không dựa vào việc nhãn có nằm trong top-5. Tự chọn tau trên đủ ID validation của đúng arm/dataset, chỉ dùng score valid hữu hạn, grid 0,01–0,99 bước 0,01, tối đa MCC. Hòa trong 1e-9: gần 0,5 nhất, sau đó ngưỡng nhỏ hơn. Nếu mọi MCC không xác định do predictor hằng: tau=0,5, MCC=null và đánh dấu degenerate. Báo coverage/invalid; không gán invalid về nhãn 0. Không khóa trên validation dở; phải khớp ID, label, prompt hash, model, seed và tokenizer/backend identity. Ngưỡng đã khóa không được ghi đè bằng kết quả đẹp hơn.

Việc chọn ngưỡng chỉ đọc file records của split validation; không mở test records hoặc metric test. Tính ngưỡng và lưu JSON là công việc CPU, độc lập với GPU inference. Nếu test đã được suy luận trước khi khóa ngưỡng, có thể chấm lại score bằng tau cố định mà không chạy lại GPU, nhưng phải công khai thứ tự thực tế. Thay đổi tiêu chí vì đã xem test phải được đánh dấu thăm dò.

## Phân tích đã có trong đề cương

Giữ contrasts, biên tác dụng, 5.000 bootstrap và Holm trong protocol template; không chọn lại model/arm hoặc seed từ test. Báo riêng metric raw greedy, score tại 0,5, score tại tau validation và AUROC/AUPRC. Rep là lượt gọi mới, checkpoint resume cùng run không phải một expert độc lập. Những bước prompt audit bằng người, donor và preregistration còn thiếu trong kiểm toán không tự được hoàn thành bởi file này.

## Công bố và phiên sau

Gói này được tạo local và có thể niêm phong bằng commit/tag riêng. Chưa đăng lên OSF: không có kết nối/tài khoản OSF trong phiên công cụ này. Không điền ngày local này thành ngày OSF. Nếu đăng sau, ghi thời điểm công bố thực tế và phân biệt phần nào được cố định trước/sau khi có kết quả. Các sửa đổi sau bản ghi phải thêm vào CHANGES_AFTER_ANALYSIS_LOCK.md, không sửa ngầm bản ghi này.
