# Tự động khóa ngưỡng và bản ghi phân tích khi inference đang chạy

**Hiện trạng sau đối chiếu 02/11/2026:** xem [HIEN_TRANG.md](HIEN_TRANG.md) và [current_status.json](current_status.json). Hai file này bổ sung các snapshot kiểm toán/ngưỡng ngày 01/11; không tạo khóa mới. B2 hiện chưa tích hợp helper vào notebook; watcher chưa được xác minh đang chạy. B2-rand đã có 12 bundle và notebook chạy kèm B2 rerun-66, chưa có output inference.

<!-- donor-rerun-risk-note -->
**Nguy cơ do donor:** watcher/khóa ngưỡng không tự thay donor và không tự chạy lại LLM. Các run B2/flip/rep có thể cần phiên inference khác nếu prompt đổi khi thống nhất donor; ngưỡng mới chỉ được tính từ validation của đúng phiên. Theo dõi tại [NGUY_CO_CHAY_LAI_DO_DONOR.md](NGUY_CO_CHAY_LAI_DO_DONOR.md).
<!-- /donor-rerun-risk-note -->

Ngày thực hiện 01/11/2026. Có thể làm trên CPU độc lập với GPU inference: chọn ngưỡng chỉ cần score + nhãn validation. Không chạy lại LLM, không sửa prompt, không dùng test để chọn ngưỡng và không tự ngắt phiên Kaggle đang chạy.

## Kết quả đã khóa

| Arm / dataset | Validation đã đủ | tau | MCC validation |
|---|---:|---:|---:|
| B0 / Devign | 2.732/2.732 | 0,98 | 0,076010 |
| B0 / ReVeal | 2.273/2.273 | 0,30 | 0,080120 |
| B2 / Devign | 2.732/2.732 | 0,70 | 0,053226 |
| B2 / ReVeal | 2.273/2.273 | 0,12 | 0,082299 |

Nguồn chính: [thresholds.json](thresholds.json). Quy tắc grid 0,01–0,99, tối đa MCC, hòa thì gần 0,5 nhất rồi ngưỡng thấp hơn. Đây là ngưỡng của score, không thay nhãn raw greedy. Đã đối chiếu độc lập bằng sklearn. Khóa đã có không được ghi đè nếu evidence/model/prompt hoặc tau thay đổi; phải tạo phiên giao thức khác khi thay đầu vào.

B2 ReVeal đã đủ 2.273/2.273 validation và khóa tau=0,12 sau khi nhập output B2 I-04/I-05; MCC validation=0,082299. Cập nhật 02/11: B1 I-07 đã đủ 5.005 score validation; B2-flip I-06 cũng đủ validation phiên cũ, nhưng Devign donor mới cần sửa 28 score; B2-rep chưa có output. [threshold_lock_status.json](threshold_lock_status.json) là snapshot 01/11, chưa phản ánh B1/flip mới nhập và chưa có khóa cho hai arm này. Đợt sửa tài liệu chưa tính lại ngưỡng. Xem [bằng chứng B1](b1_I07_20261102.json). Lưu ý thứ tự thực tế: một phần test B2 đã chạy trong I-04 trước khi khóa B2/ReVeal; không mô tả toàn bộ B2 test là đã bắt đầu sau khóa.

## Helper tự động hóa và trạng thái vận hành

Giải thích ngưỡng, kết quả bốn khóa và trích dẫn trang 15, 16, 20, 38–39 của PDF: [KET_QUA_CHOT_NGUONG.md](KET_QUA_CHOT_NGUONG.md). Bốn khóa đã được đối chiếu lại độc lập bằng sklearn trong lần cập nhật này.

Bộ theo dõi local [watch_validation.py](watch_validation.py) có khả năng chạy ẩn, quét artifact mỗi 60 giây và tự dừng khi đủ 10 khóa arm/dataset. Tại đối chiếu 02/11/2026 chưa xác minh process đang chạy: không có PID và log dừng ngày 01/11. Đợt này không bật watcher. Khi checkpoint được tải/nhập về các folder arm hoặc folder Kaggle B2 như hiện tại, script tự kiểm ID/label/prompt/model/seed, gộp các bản checkpoint lặp mà không đếm hai lần, rồi khóa khi đủ validation. Không mở records/metrics test để chọn tau. Log ở threshold_watch.log và threshold_watch.stderr.log; PID ở threshold_watch.pid. Tạo file threshold_watch.stop để dừng; dùng start_validation_watch.ps1 để bật lại sau khi máy/process dừng. Đây là helper local, không phải dịch vụ tự tải output từ tài khoản Kaggle.

Chạy một lần thủ công nếu cần: `python Runs-management/auto_lock_validation.py`. Helper không có kết nối Kaggle nên kết quả cloud phải được nhập về local trước khi watcher nhìn thấy.

## Notebook Kaggle đã được cập nhật cho phiên sau

- Notebook inference B0 đã nhúng validation_lock.py, tự khóa tau sau khi đủ validation và lưu thresholds.json cùng checkpoint. Notebook B2 hiện tại chưa nhúng helper và chưa gọi make_lock/require_test_lock; có module helper B2 riêng không đồng nghĩa notebook đã tích hợp.
- Với runtime đã tích hợp helper (B0, B2-flip phiên mới, B2-rand), test bị chặn nếu thiếu khóa đúng arm/dataset hoặc khác model/tokenizer/backend/validation prompt identity. Khi chạy test, metrics theo tau khóa được lưu riêng với raw greedy và ngưỡng 0,5.
- Thư mục output/checkpoint được giữ nguyên; resume validation đã hoàn thành tạo khóa từ records có sẵn, không cần GPU suy luận lại.
- Notebook hiện đang chạy trên Kaggle vẫn là phiên mã đã nạp; sửa file local không thay đổi tiến trình cloud. Dùng notebook cập nhật ở phiên sau để nhận cơ chế tự khóa/chặn test. Nếu test đã được suy luận bằng phiên cũ, có thể chấm score offline bằng tau validation nhưng phải giữ khai báo thứ tự thực tế.
- B1 và B2-flip đã có notebook và output inference (I-07/I-06); tích hợp helper khóa ngưỡng phải được kiểm riêng. B2-flip phiên donor mới đã có luồng khóa trước test; I-07 B1 chưa có bằng chứng khóa trước 429 test. B2-rep vẫn cần lượt gọi model độc lập.

## Bản ghi giao thức: đã niêm phong local, chưa đăng OSF

Đã tạo [bản ghi có thời điểm](analysis_lock_20261101/preregistration.md), [protocol phân tích](analysis_lock_20261101/protocol.analysis.json), danh mục hash 20 tập prompt, quy tắc ngưỡng và bản sao ba khóa đầu tiên. Niêm phong bằng tag **analysis-lock-20261101-v1**, commit `282033d3ed30b9f91392fec063bd2b2ce10266f4`. [Bằng chứng Git](analysis_git_seal.json). HEAD của branch và index mặc định giữ nguyên; commit checkpoint chỉ thêm các file được chọn trên nền HEAD, không gom toàn bộ thay đổi khác.

Do inference đã bắt đầu, đây là **bản ghi phân tích lập sau khi chạy**, không phải đăng ký trước hồi tố. Ghi rõ kết quả validation đã được xem, tiến độ test bên ngoài chưa xác nhận, sai khác donor Devign hiện biết và các variant scaffold. Không tự đánh dấu các thiếu sót donor/prompt audit trong kiểm toán là đã giải quyết.

Gói [analysis_record_for_OSF_20261101.zip](analysis_record_for_OSF_20261101.zip) đã sẵn sàng để đăng. **Chưa được đăng OSF**: không có tool/kết nối OSF trong phiên này, không tạo URL/ngày công bố giả. Nếu đăng sau, phải dùng thời điểm công bố thật và nói rõ phần nào được khóa trước/sau khi có kết quả. File canonical protocol template không bị điền một ngày OSF chưa tồn tại.

## Kiểm tra

- Tái kiểm tra 02/11: 4 test core pass; 1 test tích hợp notebook fail vì notebook B2 chưa có helper. Giữ nguyên test và runtime B2 theo quyết định người dùng; chưa nghiệm thu tích hợp B2.
- 8 test B0, gồm luồng validation → tự khóa → test → resume bằng backend giả. Giữ output notebook người dùng khi cập nhật source.
- 4 ngưỡng thật được kiểm tra độc lập với sklearn, không đọc test records/metrics.
- Không phải chạy lại Joern, CodeT5 hoặc inference để tính các ngưỡng này.
