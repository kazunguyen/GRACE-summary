# Worklog — hoàn tất B1-full, cập nhật B3 lịch sử và nghiệm thu runtime

Ngày lập: 08/11/2026. Nhánh làm việc: `hieu`. Nguồn trạng thái Kaggle: snapshot khoảng **16:08 GMT+7**, không phải trạng thái live tại lúc đọc tài liệu.

## Kết quả cập nhật

- **B1-full test seed 42 COMPLETE:** Devign 2.732 + REVEAL 2.274 = **5.006/5.006**, toàn bộ chạy mới, không nhập legacy records. Worker status hoàn tất **15:35:51 GMT+7**. Không có seed 43/44 bắt buộc cho arm này.
- **B3-only validation lịch sử COMPLETE:** Devign 2.732 + REVEAL 2.273 = **5.005/5.005**; status hoàn tất **10:40:57 GMT+7**. Phiên cuối thêm 947 REVEAL, giữ 4.058 record nhập (4.029 lịch sử + 29 đã có source-lock evidence). Không phải `b3-verified-patch-v1`, không công bố như B3 test hoàn tất.
- **B1-shuf locked:** RUNNING trên `tomandjerry223` ở snapshot, mục tiêu 15.018 test trên seed 42/43/44; chưa có output công bố, số mẫu hiện tại chưa quan sát được.
- **B2-rep, B2-labelonly, B2-nolabel:** vẫn COMPLETE 5.006 mỗi arm; kết quả/giới hạn runtime đã công bố trước giữ nguyên.

Không suy “chỉ còn B1-shuf” thành toàn nghiên cứu đã xong test. B2-rand còn phạm vi seed44 riêng theo ledger cũ; B3 mới chưa inference, các probe B3 không tự được thêm vào lịch GPU.

## B1-full runtime acceptance

Theo yêu cầu bổ sung của chủ dự án, đã tải **toàn bộ output B1-full** về `Runs-management/locked_continuations_20261108/b1_full/remote_output/`, gồm checkpoint/build log/backend source archive. Bản Git giữ records, identity, contract, native/build provenance logs và các input/threshold manifests cần thiết; model, backend archive, checkpoint ZIP và bản download lặp giữ local. Hash checkpoint được lưu trong report.

Kết luận **PASS_LAUNCH_CONTRACT** trên toàn bộ 5.006 record. Đã đối chiếu contract bytes/canonical seal; notebook cell text/readback; input bundle/worker/helper/model identities; backend sdist hash; sáu package pinned; constructor; build provenance; native log hai T4, 49/49 offloaded layers, context 8.192, batch/ubatch 256; CPU thread formulas; từng provenance reference, prompt/label/score/ngưỡng; checkpoint CRC và loose-record equality.

Contract lúc launch SHA-256 `85d8770839f80260cdc7c27b27b6cce6bf8815675c8593db68fb102589c5cbd6`. Contract hiện tại bổ sung SciPy có danh tính khác. Pip freeze của phiên thật có `scipy==1.16.3`, khớp pin hiện tại; không ghi hồi tố run đã nạp contract mới. Compiled backend hashes và model hash được runner đã kiểm source ghi trên Kaggle, không tuyên bố đã tải model để hash lại local hoặc dùng binary giống hệt mọi phiên.

| Dataset | N | τ đã khóa | AUROC | MCC | BA | F1 | Raw invalid |
|---|---:|---:|---:|---:|---:|---:|---:|
| Devign | 2.732 | 0,99 | 0,531096 | 0,069566 | 0,527480 | 0,312535 | 0 |
| REVEAL | 2.274 | 0,01 | 0,578215 | 0,084902 | 0,569695 | 0,209561 | 2 |

Metric được tính từ records và ngưỡng validation đã khóa, không fit lại. Hai raw invalid REVEAL vẫn có numeric score hợp lệ; không loại chúng khỏi census. Không chạy significance/bootstrap trong công việc này.

## Bảo toàn và kiểm tra trước push

- Công bố bản sao nguyên bytes trong `Runs-management/run_handoff_20261108/completed_results/`; `.gitattributes` hiện có giữ nguyên bytes ở thư mục này.
- Không sửa frozen configs/specs/banks, protected OSF branch/tag hoặc lịch sử. Code và dossier B3 đang làm dở được giữ ngoài commit công việc cập nhật run này.
- Ba bộ test bắt buộc: **37 passed**. Lượt đầu có 36 passed/1 setup error vì quyền truy cập Windows TEMP; chạy lại với `--basetemp` trong workspace cho 37 passed. Đây là sửa đường dẫn test tạm, không bỏ assertion.
- Bộ nghiệm thu ban đầu so cell source dạng list và string thành khác nhau; đã sửa verifier theo định dạng notebook hợp lệ bằng cách nối fragments **không strip nội dung**. Cả 9 cell khớp text chính xác; audit sau sửa đạt mọi gate.

## Bằng chứng và công việc tiếp theo

- [Run handoff cập nhật](../Runs-management/run_handoff_20261108/RUN_STATUS.md).
- [Runtime acceptance B1-full](../Runs-management/run_handoff_20261108/B1_FULL_RUNTIME_ACCEPTANCE.md), [machine-readable report](../Runs-management/run_handoff_20261108/b1_full_runtime_acceptance.json).
- [Completion/file hashes](../Runs-management/run_handoff_20261108/completion_update_20261108.json), [snapshot Kaggle](../Runs-management/run_handoff_20261108/status_snapshot_1608/STATUS.md).

Tiếp tục theo dõi B1-shuf, tải và nghiệm thu từng seed khi output xuất hiện. Với B3 mới, tiếp tục source/mapping/rationale và hai review thật theo audit; kết quả B3 lịch sử không thay bằng chứng của phương pháp mới.
