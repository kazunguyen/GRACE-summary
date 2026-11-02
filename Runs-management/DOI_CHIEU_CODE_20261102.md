# Đối chiếu Runs-management với code — 02/11/2026

Người dùng đã chốt: ghi tài liệu đúng hiện trạng, không sửa runtime B2; giữ snapshot lịch sử, thêm trạng thái hiện tại và sửa generator, chưa tính khóa mới; commit chỉ code/tài liệu/bằng chứng nhỏ trong Runs-management.

Nguồn hiện tại: [HIEN_TRANG.md](HIEN_TRANG.md), [current_status.json](current_status.json). Chỉ xác nhận output đã nhập local; không suy ra trạng thái cloud.

| Phát hiện | Cập nhật đã thực hiện | Giới hạn còn giữ |
|---|---|---|
| Tài liệu nói notebook B2 đã nhúng helper | Sửa mô tả B2 hiện chưa có make_lock/require_test_lock; B0 có helper, flip phiên mới/rand có lời gọi trong source | Không sửa notebook B2 hoặc làm test tích hợp xanh giả |
| Generator readiness cố định 4.396 record và ghi đè cập nhật | Số record lịch sử lấy từ JSON; thêm bảng hiện tại từ current_status.json trước phần lịch sử | Nội dung kiểm toán 01/11 vẫn được đánh dấu snapshot |
| Generator ngưỡng nói B1 chưa có validation | Bảng hiện tại phân biệt đủ score và đã có khóa; bảng khóa đọc thresholds.json | Không fit ngưỡng B1/flip và không sửa khóa cũ |
| JSON kiểm toán và threshold_lock_status.json cũ | Giữ nguyên, thêm current_status.json; audit chạy mới xuất *_CURRENT.json | Không thay timestamp hoặc diễn giải lại lịch sử |
| Watcher bị mô tả đang hoạt động | Ghi chưa xác minh process; không có PID và log dừng 01/11 tại lần đối chiếu | Không bật watcher hoặc tự chạy auto_lock_validation.py |
| B2-rand chưa được ghi nhận | Bổ sung notebook và 12 bundle/30.033 prompt, ba seed; notebook ưu tiên rerun-66 của B2 | Chưa có output inference; rerun-66 không phải arm mới |
| Donor summarizer yêu cầu inventory khớp mọi output hiện tại | Kiểm nguồn lịch sử theo inventory; báo file mới ngoài phạm vi, xuất *_CURRENT | Export lịch sử B0/B2 giữ nguyên; B2-flip có kiểm toán I-06 riêng |
| Reconciliation có thể ghi dở inventory cũ trước khi fail với flip | Từ chối ghi đè export lịch sử ngay khi vào main | Muốn đối chiếu chiến dịch mới phải tạo phiên mới và hỗ trợ các arm tương ứng |
| RUNS.md trỏ script Joern đã xóa | Đổi thành tên script lịch sử, giữ link manifest còn tồn tại | Không khôi phục script tạm |

## Tái tạo báo cáo

Chạy từ GRACE-summary:

~~~powershell
python -B Runs-management/refresh_current_status.py
python -B Runs-management/write_tier1_audit_report.py
python -B Runs-management/write_threshold_explanation.py
~~~

refresh_current_status.py kiểm tra ID trùng, arm/dataset/split, nhãn, hash prompt và model record/manifest; chỉ ghi current_status.json và HIEN_TRANG.md. Map SOURCES chỉ định các output canonical đã nhập, tránh cộng bản sao checkpoint. Khi nhập run mới, cập nhật map nguồn có kiểm chứng trước khi refresh. B2-rand hiện chỉ ghi trạng thái chuẩn bị; chưa có nguồn inference được nhập.

Hai generator đọc current_status.json, không tự inference hoặc tạo khóa. Generator readiness giữ phần thân là snapshot kiểm toán 01/11; bảng hiện tại luôn ở đầu. audit_tier1_readiness.py và audit_arm_integration.py xuất JSON mới có hậu tố _CURRENT, không ghi đè hai JSON lịch sử. audit_b2_flip_I06_20261102.py xuất sang thư mục b2_flip_I06_20261102_CURRENT, giữ nguyên kiểm toán I-06 đã nhập. Các file _CURRENT là kết quả tái chạy khi cần; đợt này dùng current_status.json để ghi trạng thái hiện tại.

summarize_donor_reconciliation.py vẫn xác minh hash của mọi nguồn trong inventory lịch sử. Nó cho phép nguồn mới ngoài phạm vi, công bố danh sách đó và xuất KET_QUA_DOI_CHIEU_CURRENT.md/verification_CURRENT.json/CSV_CURRENT riêng. Không chạy lại retrieval hoặc ghi đè export lịch sử trong đợt này.

## Xác minh

- 5 kiểm thử mới pass: validation đủ vẫn chưa khóa; raw invalid vẫn có thể có score valid; từ chối ID trùng/hash prompt/model sai; hai generator giữ tiến độ B1/flip, không thay JSON và cho kết quả lặp lại giống nhau.
- Bộ test khóa hiện có: 4 core test pass; 1 test tích hợp notebook B2 fail vì thiếu helper. Giữ nguyên test và runtime theo quyết định người dùng.
- Bốn khóa B0/B2 đã đối chiếu sklearn ở lượt kiểm toán; hash các file nguồn của khóa khớp. Đợt sửa này kiểm lại byte/hash, không đổi thresholds.json.
- Sáu file trong analysis_lock_20261101 khớp SHA256SUMS.json. Các JSON lịch sử, trạng thái ngưỡng 01/11 và bằng chứng niêm phong không bị thay trong đợt sửa.
- Các script Python trong Runs-management đều compile. Liên kết local trong các Markdown được kiểm tra; artifact lớn có thể chỉ tồn tại local.

## Phạm vi Git

Chỉ stage Runs-management: code, tài liệu, manifest/provenance nhỏ, summary và CSV/JSONL danh sách mẫu cần chạy lại. .gitignore tại đây loại chính xác các thư mục cache/new_reference/rerun_inputs cùng bản sao prompt và bảng quyết định lớn; không xóa file khỏi máy. Không stage folder arm hoặc tier1_prompt_tools. Các link tới output/cache lớn mô tả artifact local, không cam kết các artifact đó có trong commit. Chưa publish OSF, push hoặc chạy inference mới.
