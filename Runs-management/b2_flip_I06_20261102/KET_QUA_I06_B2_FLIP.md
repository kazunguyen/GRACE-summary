# I-06 — B2-flip Kaggle, checkpoint nhập ngày 02/11/2026

Nguồn: `quangdung1111/02-kaggle-qwen-q4-b2-flip-ipynb`. Output gốc lưu tại `04_Arm_B2_Flip/output/kaggle_20261102_quangdung1111_run1/`.

Chạy từ **01/11/2026 21:46:02** đến **02/11/2026 07:15:49 Asia/Bangkok**, 9.4964 giờ theo timestamp trong checkpoint. Trạng thái `timed_out`, dừng sau Devign test. Đã tải checkpoint và log; kiểm tra CRC, hash và đối chiếu nội dung ZIP checkpoint với các file output tải riêng.

**Hoàn thành 5,235/10,011 (52.29%), còn 4,776 mẫu chưa chạy.**

## Kết quả trên các mẫu đã inference

TP/TN/FP/FN dưới đây tính từ `raw` token 0/1 của mô hình, cùng cách `evaluation.json` gốc. Đây là thống kê hiện trạng, không phải kết quả tại ngưỡng tối ưu validation. `invalid response` là raw không hợp lệ; `invalid score` là thiếu/không hữu hạn/sai miền score hoặc `valid=false`. Mẫu chưa chạy không được tính vào invalid.

| Dataset | Split | Đã chạy / dự kiến | TP | TN | FP | FN | Invalid response | Invalid score |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| devign | validation | 2,732/2,732 | 746 | 585 | 960 | 441 | 0 | 0 |
| reveal | validation | 2,273/2,273 | 85 | 1261 | 802 | 125 | 0 | 0 |
| devign | test | 230/2,732 | 82 | 41 | 57 | 50 | 0 | 0 |
| reveal | test | 0/2,274 | 0 | 0 | 0 | 0 | 0 | 0 |
| **Tổng** | | **5,235/10,011** | **913** | **1887** | **1819** | **616** | **0** | **0** |

## Ảnh hưởng khi chuyển sang kho donor thống nhất

**33 mẫu đã có output phải inference lại** vì hash prompt cuối thay đổi. **33 mẫu đổi prompt còn chưa chạy** chỉ cần dùng prompt mới khi chạy lần đầu. Giữ được 5,202 output đã tải khi giữ inference identity. Tổng số target đổi prompt của toàn bộ B2-flip là 66, tất cả ở Devign.

Để hoàn tất toàn bộ B2-flip theo donor mới cần thêm **4,809 lượt LLM**: 4,776 mẫu chưa chạy + 33 mẫu phải chạy lại. 33 mẫu đổi prompt chưa chạy nằm trong phần 4,776 này.

| Dataset | Split | Đã chạy: cần inference lại | Đã chạy: giữ kết quả | Chưa chạy: cần dùng prompt mới | Tổng prompt thay đổi |
|---|---|---:|---:|---:|---:|
| devign | validation | 28 | 2704 | 0 | 28 |
| reveal | validation | 0 | 2273 | 0 | 0 |
| devign | test | 5 | 225 | 33 | 38 |
| reveal | test | 0 | 0 | 0 | 0 |

Năm Devign test đã chạy cần inference lại: `devign:test:321`, `devign:test:1426`, `devign:test:1473`, `devign:test:2195`, `devign:test:2246`.

- [Các mẫu đã chạy cần inference lại (CSV)](mau_da_chay_can_inference_lai.csv).
- [Các mẫu chưa chạy cần đổi prompt (CSV)](mau_chua_chay_can_doi_prompt.csv).
- [Quyết định cho toàn bộ output tải về (CSV)](downloaded_record_decisions.csv).
- [Đối chiếu toàn bộ 10.011 prompt (CSV)](all_prompt_comparison.csv).
- `changed_prompt_text_review.jsonl`: nội dung prompt mới của 66 target đổi, để đọc/so hash; chưa phải bundle inference, cần metadata token đúng trước khi đóng gói.

## Cách đối chiếu

1. Dùng đúng bốn ZIP prompt nằm trong output Kaggle làm nguồn prompt gốc; kiểm tra manifest, hash archive và từng record ID/label/hash prompt/demo/model/seed.
2. Kiểm tra toàn bộ 10.011 prompt B2-flip cũ bằng cách đảo đúng câu nhãn demo của B2 cũ; phải giống từng ký tự với bundle Kaggle.
3. Tái dùng bộ B2 tham chiếu donor thống nhất đã được kiểm toán trước đó. Kiểm tra hash bộ tham chiếu và cache bank; đảo nhãn thật của demo mới để dựng B2-flip mới, giữ nguyên code target, graph, câu dẫn và code demo từ B2 phiên mới.
4. So hash toàn bộ prompt cuối, rồi giao danh sách thay đổi với ID thực có output. Không suy ra số rerun chỉ từ donor bị loại hoặc chỉ từ số 66 của B2.

## Thứ tự validation/test và giữ lịch sử

Hai validation đã đủ, nhưng output tải về không kèm `thresholds.json`/`threshold_lock.json`; vì vậy checkpoint này không cung cấp bằng chứng đã khóa ngưỡng trước 230 mẫu Devign test. Giữ nguyên thông tin thứ tự khi báo cáo. CM ở trên dùng raw; không lấy nhãn/score test để chọn ngưỡng trong kiểm toán này.

Khi chuyển donor, validation Devign B2-flip đổi 28 prompt: inference lại 28, ghép với 2.704 score validation còn khớp, rồi tính/khóa ngưỡng riêng cho phiên mới trên đủ 2.732 validation trước test mới. Không ghi đè ngưỡng/kết quả lịch sử.

Muốn tiếp tục đúng phiên donor cũ: dùng `grace_b2_flip_checkpoint.zip` đã tải để resume phần còn thiếu. Muốn chuyển donor mới: tạo phiên input/output riêng, chỉ tái dùng các record còn khớp prompt và runtime; checkpoint cũ chứa hash cũ của các target đổi nên không được coi chúng là đã hoàn thành prompt mới.

Kiểm toán chỉ chạy CPU, không gọi LLM, không ghi đè prompt/output cũ hoặc các khóa ngưỡng. [Tóm tắt máy đọc được](summary.json), [danh sách/hash file tải về](download_inventory.json).
