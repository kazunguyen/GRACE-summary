# Bước 3–4: hồ sơ chuẩn bị cho B2-rand

Trạng thái: **chưa nghiệm thu**. Đã xác minh checkpoint, chạy lại kiểm thử/kiểm hash và soạn hồ sơ kế hoạch. Chưa có hai người chấm; các quyết định phân tích vẫn chờ chủ nhiệm; chưa commit/tag prereg-v1 và không thực hiện OSF.

- [Bằng chứng checkpoint](checkpoint_verification.json): 12 tập prompt khớp audit, 4.798 record validation khớp checkpoint, không có test B2-rand trong checkpoint; 30.033 demo khác demo B2 tham chiếu donor mới. Script [verify_checkpoint.py](verify_checkpoint.py) tạo file này và từ chối ghi đè.
- [Bản nháp kế hoạch](preregistration_draft.md) và [protocol nháp](protocol_draft.yaml): khai báo lịch sử đã chạy/xem; các mục chưa chốt để nguyên pending. Không tự gọi là đăng ký trước.
- [Mẫu 60 prompt](../prompt_audit_20261102/manual_packet.md), [rubric](../prompt_audit_20261102/RUBRIC.md), [phiếu 1](../prompt_audit_20261102/reviewer_1.csv), [phiếu 2](../prompt_audit_20261102/reviewer_2.csv). Hai người thật đọc độc lập 30 prompt mỗi dataset, điền hai phiếu, sau đó lưu biên bản đối chiếu và phân xử. Đừng sửa phiếu gốc của nhau.
- Chạy `python review_status.py` để kiểm tra hình thức phiếu. Script không tự đánh giá prompt và không chứng minh người chấm độc lập; cần biên bản thật.
- Xem [audit B2-rand](../prompt_audit_20261102/KET_QUA.md) và [dry-run 10 arm](../dry_run_validation_20261102/KET_QUA.md). Không gộp dry-run với bundle inference. Bước 3 toàn bộ 15 arm còn 5 arm thiếu input.

Lượt test B2 lịch sử đã tiếp xúc; không backdate, không đổi nhãn sang xác nhận. Nếu hoàn tất review và các quyết định phân tích, kiểm lại identity, ghi amendment có thời điểm thực và chốt hồ sơ trước khi tiếp tục; OSF được để ngoài phạm vi này.
