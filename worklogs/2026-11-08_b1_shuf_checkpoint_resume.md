# B1-shuf — checkpoint và chuẩn bị resume, 08/11/2026

Yêu cầu: kiểm checkpoint và tiếp tục B1-shuf; giữ prompt, validation thresholds và runtime lock, không chạy lại phần đã có.

## Checkpoint đã xác minh

Kernel cha: `tomandjerry223/grace-b1-shuf-locked-20261108`. Kaggle báo COMPLETE cho phiên notebook nhưng worker ghi **timed_out**, chưa đủ census. Worker status cập nhật lúc **16:59:25 GMT+7**.

| Seed | Devign test | REVEAL test | Còn thiếu |
|---|---:|---:|---:|
| 42 | 2.732/2.732 | 2.274/2.274 | 0 |
| 43 | 745/2.732 | 0/2.274 | 4.261 |
| 44 | 0/2.732 | 0/2.274 | 5.006 |
| Tổng | | **5.751/15.018** | **9.267** |

Full output/checkpoint đã tải local. Đối chiếu CRC ZIP, records trong ZIP với loose files, unique IDs, prompt/label/model/ngưỡng/score, input identity, provenance/log hashes, package/constructor, native two-T4/full-offload checks đạt trên 5.751 records. Checkpoint SHA-256: `6b4defda65f63c1704689d1a425d72983cac7e4f3d168370d6fae6f7093003e4`.

Input manifest giữ `1f008abc6f0d9928fca6c5684d9b49f508182a733acb12f0d8bbb03d11d3a70c`; runtime contract giữ `85d8770839f80260cdc7c27b27b6cce6bf8815675c8593db68fb102589c5cbd6`. Không chuyển record thành legacy không chứng nhận; đây là tiếp tục cùng run identity, với provenance riêng cho session mới.

## Quota và điều phối

Quota API khoảng **17:38 GMT+7**:

- `tomandjerry223`: đã dùng 108.158,682/108.000 GPU-giây, hết quota.
- `huuhieu3333`: còn 6.566,591 giây, khoảng 1 giờ 49 phút.
- `lznt123`: còn 56.504,654 giây, khoảng 15 giờ 42 phút.
- API báo quota refresh `2026-11-14T00:00:00Z` (07:00 GMT+7); không coi đây là bảo đảm thời điểm tài khoản có thể thực thi nếu điều kiện nền tảng đổi.

Đã tạo dataset checkpoint PRIVATE trên tài khoản gốc `tomandjerry223`, chưa launch tiếp vì không đủ quota. Chuẩn bị phương án chuyển đúng byte checkpoint + frozen prompt bundle sang PRIVATE `lznt123/grace-b1-shuf-checkpoint-20261108`, notebook `lznt123/grace-b1-shuf-resume-20261108`, T4×2.

**Tại lúc lập worklog: chưa upload sang lznt123 và chưa launch.** Hệ thống automatic approval review chặn upload giữa hai tài khoản vì cần xác nhận cụ thể cho payload/đích. Đã hỏi chủ dự án qua công cụ; không thử đường vòng vượt chặn.

## Kiểm delivery local

[Script điều phối](../scripts/resume_b1_shuf_checkpoint_20261108.py) chuẩn bị notebook từ source đã khóa, giữ nguyên worker/hash, input/thresholds/model/runtime identity. Khối restore mới bắt buộc đúng một checkpoint và pin SHA byte; thiếu checkpoint sẽ fail thay vì khởi chạy fresh census.

Đã thực thi chính cell restore của notebook vào thư mục tạm: khôi phục đúng 5.751 records, từ chối input thiếu checkpoint. Không gọi model hoặc GPU để thử restore. Bằng chứng local tại `Runs-management/locked_continuations_20261108/b1_shuf_resume_lznt123_20261108/checkpoint_acceptance.json` và `restore_check.json`.

Sau khi có xác nhận chuyển tài khoản: upload private dataset → kiểm readiness → launch một phiên → đọc lại source/machine shape/input → xác nhận trạng thái thực và ghi kết quả bổ sung. Nếu phiên tiếp tục lại chạm giới hạn, giữ checkpoint và tiếp tục phần ID còn thiếu; không bảo đảm 9.267 mẫu sẽ xong trong một phiên 9 giờ.

## Cập nhật theo chỉ định chủ dự án — khoảng 19:10 GMT+7

Chủ dự án chỉ định **`huuhieu3333`**, không chấp thuận phương án `lznt123`. Vì vậy không upload hay launch trên lznt123. Đã chuẩn bị delivery riêng `b1_shuf_resume_huuhieu3333_20261108`, giữ nguyên checkpoint/input/worker/model/threshold/runtime identity.

Quota huuhieu3333 đọc lại lúc **19:09:49 GMT+7** vẫn còn 6.566,591 GPU-giây. Phiên tiếp tục được cấu hình **90 phút (5.400 giây)** tính từ lúc notebook bắt đầu, worker giữ 300 giây dự phòng xuất checkpoint. Đây là thay đổi giới hạn thời gian vận hành, không thay tham số suy luận. Phần cài/build model cũng tính trong 90 phút; chỉ kỳ vọng tiến thêm một phần, không hứa hoàn tất 9.267 mẫu còn thiếu.

Đã upload đúng checkpoint + frozen prompt ZIP sang dataset **PRIVATE** `huuhieu3333/grace-b1-shuf-checkpoint-20261108`; API xác nhận `ready` lúc **19:13:25 GMT+7**. Upload này theo chỉ định tài khoản cụ thể của chủ dự án sau lần auto-review từ chối đích lznt123. Không dùng workaround vượt chặn cũ.

Khối restore thực tế của notebook huuhieu3333 đã được chạy trong sandbox và phục hồi đúng 5.751 records. Notebook yêu cầu đúng checkpoint SHA; thiếu file bị chặn. Source/shape và trạng thái launch sẽ ghi tiếp sau khi hoàn tất audit prompt B3 được yêu cầu kiểm trước.

## Đã launch tiếp trên huuhieu3333

- Kernel: `huuhieu3333/grace-b1-shuf-resume-20261108`, version1, private.
- Kaggle nhận launch lúc **19:15:30 GMT+7**; status **RUNNING** lúc **19:15:34 GMT+7**; parent tomandjerry223 xác nhận đã COMPLETE trước khi submit, không có duplicate run của cùng checkpoint.
- Source readback: toàn bộ cell text khớp; shape `NvidiaTeslaT4`, GPU enabled; dataset checkpoint và model source đúng tài khoản huuhieu3333.
- Notebook SHA-256: `5e14763a78b2f93c79487350bd98a60e47146c781de9d4b696a2b196e45c03ee`.
- API session timeout5400 giây; notebook `MAX_RUNTIME_HOURS=1.5`; worker dành300 giây export reserve. Runtime/constructor/prompt/threshold identity không đổi. New session provenance sẽ được ghi riêng.
- Mới xác minh đã launch/source đúng; chưa có native load log hoặc số record mới công bố của phiên này, không gọi RUNNING là model-offload acceptance. Checkpoint baseline vẫn5.751, phần thiếu9.267; worker xác minh rồi bỏ qua ID đã có.

Trước launch đã hoàn tất [audit prompt B3](../Runs-management/b3_verified_patch_v1/independent_prompt_audit_20261108_190936/AUDIT_REPORT.md) theo yêu cầu: Devign2.732 prompt đạt, REVEAL2.273 paused. Chủ dự án xác nhận hai review cuối trên payload `0ced77fefccbcef797c3c01abfa0d139d5611e2d562e8f5ec01089ff05168ee1`; validator/forms/pool khớp. Metadata v4 còn cần thống nhất version trước delivery; không launch B3 trong lượt này.

Bằng chứng launch/source/status và acceptance tại `Runs-management/locked_continuations_20261108/b1_shuf_resume_huuhieu3333_20261108/`. Phương án lznt123 vẫn chỉ là local prepared, không upload/launch.

## Sửa input Kaggle tự giải nén và launch version2

Version1 chuyển ERROR ngay cell restore (khoảng19:15:45), trước model/inference: dataset mount đã giải nén ZIP, không còn file tên checkpoint mà cell yêu cầu. Guard chặn fresh restart hoạt động đúng; không có records mới hoặc mất checkpoint. Output/log lỗi version1 được tải và bảo toàn.

Delivery sửa riêng tại `b1_shuf_resume_huuhieu3333_20261108_v2`: nhận cả ZIP nguyên byte hoặc thư mục Kaggle đã giải nén. Với ZIP phải khớp SHA/CRC/member set; với directory phải có đúng một run identity khớp và **tất cả checkpoint member hashes** khớp trước khi copy. Không tắt gate, không nhận checkpoint thiếu hoặc thay đổi.

Kiểm actual cell restore: ZIP và unpacked đều khôi phục5.751 records; loader nhận đủ15.018 frozen prompts trong mount unpacked; file bị sửa và checkpoint thiếu đều bị từ chối. Giữ nguyên worker/input/threshold/model/runtime identity và timeout90phút.

Đã launch **version2 lúc19:19:22 GMT+7**, source readback khớp và status RUNNING **19:19:26**. Notebook SHA `a4f56d6dc20b42fbac5f87c5a5b29fc15891538205ca7c93fea463c2ac3bb0e5`. Dataset private cũ được tái sử dụng; không upload sang tài khoản khác. Quota đọc trước lần2 còn6547,169 giây, lớn hơn timeout5400 giây. Bằng chứng version2 lưu ở delivery v2; không gọi trạng thái version1 là phiên đang chạy hiện tại.
