# Bằng chứng tính ngưỡng chỉ từ validation

Ngày đối chiếu: 06/11/2026. Phạm vi: dữ liệu đầu vào và kết quả của phép tính ngưỡng; không xác nhận lịch sử mọi người đã hoặc chưa xem test.

## Mã tính ngưỡng gốc

`Runs-management/validation_lock.py`, hàm `pick_threshold(rows)`.

Hàm nhận nhãn và score từ các records truyền vào, tối đa hóa MCC trên lưới 0,01-0,99; bỏ MCC không xác định, hòa trong 1e-9 thì ưu tiên gần 0,5 rồi ngưỡng nhỏ hơn. Hàm không mở tệp hay nhận metrics test. Trong luồng khóa gốc, `validate_validation` và `make_lock` kiểm tra split/ID/nhãn/model và độ đầy đủ trước khi gọi hàm này.

Mã module hiện tại khớp từng byte với mã trong commit `282033d3ed30b9f91392fec063bd2b2ce10266f4` ngày 01/11/2026. SHA-256 của cả hai:

`9d83acbe5a1767d0e91c6e5950ab73e92c6b4d05980422486a1876564e4db711`

Đây là chạy lại thuật toán lịch sử, không phải viết một thuật toán tối ưu mới để thu được các số mong muốn.

## Lệnh tái lập

Chạy tại thư mục repository:

```powershell
python -B Runs-management/osf_amendment_20261106/verify_validation_thresholds.py
```

Verifier tải nguyên byte module gốc và gọi trực tiếp `pick_threshold`. Nó không gọi `auto_lock_validation.scan_once` hay `persist_lock`, không thay đổi các file khóa ngưỡng hiện hành.

## Đầu ra thực tế đã quan sát

```text
B0 devign validation n=2732 valid=2732 tau=0.98 MCC=0.076009780320
B0 reveal validation n=2273 valid=2273 tau=0.30 MCC=0.080119877888
B1 devign validation n=2732 valid=2732 tau=0.98 MCC=0.074754926497
B1 reveal validation n=2273 valid=2273 tau=0.63 MCC=0.083264067697
PASS: all four thresholds match; four validation inputs; zero test files read.
```

## Kiểm tra đầu vào và truy cập tệp

- Chỉ định tường minh bốn tệp records validation: hai dataset của B0 I-03 và hai dataset của B1 I-08. Không quét thư mục để chọn nguồn theo kết quả.
- Mỗi record phải đúng arm/dataset/split validation, ID duy nhất, model SHA-256 đã đăng ký và seed 42; số mẫu phải đủ 2.732/2.273. Score valid phải hữu hạn và khớp sigmoid của hai logprob trong sai số 1e-10.
- Python audit hook kiểm soát mọi sự kiện `open` sau khi tải các phụ thuộc chuẩn. Chỉ cho đọc đúng bốn tệp validation, module tối ưu và mã verifier; đọc tệp khác bị từ chối. Chỉ cho ghi tệp kết quả bằng chứng mới.
- Lần chạy thành công ghi nhận đúng sáu tệp được mở đọc: bốn validation JSONL và hai mã nguồn. Không đọc test records, test metrics, file cấu hình ngưỡng hay báo cáo phân tích lại.
- Verifier không truyền ngưỡng mong đợi vào hàm tối ưu. Chỉ sau khi tính xong cả bốn kết quả, nó mới so sánh với bốn số trong bản đính chính.
- `validation_threshold_verification.json` lưu SHA-256 mã nguồn, từng tệp validation, số mẫu, toàn bộ MCC tại 99 điểm lưới và danh sách đường dẫn đã đọc. `test_files_read=[]`, `blocked_events=[]`, `all_four_thresholds_match_amendment=true` trong lần chạy thành công.

Mã kiểm chứng này được tạo ngày 06/11; chức năng của nó là tái lập và kiểm soát I/O cho lần xác minh hiện tại. Bằng chứng thời điểm lịch sử là artifact Git ngày 01/11, không phải thời điểm tạo verifier.

## Dữ liệu kèm theo và lần chạy cô lập

`validation_records.zip` chứa nguyên byte bốn tệp validation; `validation_input_inventory.json` lưu đường dẫn gốc, SHA-256 và số record. SHA-256 của ZIP: `4737fc0ac8685dc0c70cdc5493e10dbc468ad5097753d19a4532a0237af17596`.

Đã giải nén và chạy lại trong một thư mục tạm chỉ chứa optimizer, verifier và bốn tệp validation. Không sao chép test hoặc cấu hình ngưỡng sang thư mục này. Lần chạy thành công, tái lập cả bốn ngưỡng. Output và audit được lưu ở `isolated_verification_stdout.txt` và `isolated_validation_verification.json`. Người đọc có thể làm lại từ checkout sạch theo README; không cần có các output local khác của nhóm.

## Diễn đạt đề nghị cho OSF

> The corrected thresholds were reproduced by executing the original threshold-selection implementation, byte-identical to the version recorded on 1 November 2026, using exclusively the four complete validation record files. An enforced file-read allowlist restricted the verification run to those validation files and the two source files. The run reproduced B0 thresholds of 0.98/0.30 and B1 thresholds of 0.98/0.63 for Devign/ReVeal, without reading test records, test metrics, or the submitted threshold values. Source/input SHA-256 hashes, the complete 99-point MCC sweeps and the file-read audit are provided. This supports the computational provenance of the correction as application of the stated validation-only rule. Historical test exposure is disclosed separately.

## Phân biệt với script phân tích kết quả

`Runs-management/reanalysis_20261106/recompute.py` có đọc test để tính metrics/bootstrap, dù lời gọi chọn ngưỡng trong script đó nhận validation. Không được mô tả toàn bộ script phân tích lại là không đọc test. Hồ sơ bằng chứng không-đọc-test ở đây dùng module tối ưu gốc và verifier độc lập nêu trên.
