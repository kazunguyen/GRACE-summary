# B3-swap test — Thanh Duy, 10/11/2026

Kernel: [thanhduy9a4tv/grace-b3-swap-test-20261110-v1](https://www.kaggle.com/code/thanhduy9a4tv/grace-b3-swap-test-20261110-v1), private. Prompt test đủ 2.732 Devign + 2.274 REVEAL, kế thừa threshold B3 0,99/0,01; runtime lock `4c9c3bcff5e9fd32532d7edf85df7a961e45ec9c64bee3df8833d986a2eb276e`.

## Kiểm bốn tài khoản

Đã kiểm bằng đúng cấu hình của huuhieu3333, lznt123, tomandjerry223 và thanhduy9a4tv. Thanh Duy dùng access token. Tại snapshot khoảng **22:57 GMT+7**, chỉ Thanh Duy có GPU quota khả dụng dương: **107.975,848 giây**, gần 30 giờ. Ba account còn lại đã vượt tổng quota; không dùng chúng để launch. Chi tiết không chứa credential: `account_checks.json`.

## Chuẩn bị và launch

- Private dataset `thanhduy9a4tv/grace-b3-swap-test-release-20261110-v1` đã tạo và có trạng thái `ready`.
- Model source riêng `thanhduy9a4tv/qwen3coder30b-prepare-notebook` truy cập được; danh sách output có đúng tên GGUF đã pin. Model SHA sẽ được notebook rehash trước inference.
- Notebook đổi account/mount/model-source từ bản bàn giao; bootstrap/worker/setup/runtime cells giữ nguyên. Preflight local kiểm đủ census, ZIP/manifest hash, hai lock và Python cell syntax.
- Version 1 đã submit lúc **23:00:37 GMT+7**; source readback khớp toàn bộ cell, private/GPU/T4/dataset/model source đúng.
- Theo yêu cầu push lại khi queue, version 2 đã submit lúc **23:10:35 GMT+7**, cùng source và cấu hình. Không thay prompt/threshold/runtime để né queue.

## Trạng thái quan sát

**Latest observed: QUEUED**, chưa xác nhận RUNNING hoặc native runtime. Xem `status.json` để biết timestamp chính xác của lần kiểm gần nhất.

Các request push tiếp theo bị Kaggle từ chối: **`Maximum batch GPU session count of 2 reached.`** Các lần bị từ chối không tạo version mới. Biên nhận trong `attempts/` phân biệt version đã tạo và request bị từ chối.

Public API chỉ trả kernel ID và current version, không trả session ID cần cho `cancel-session`; không dùng kernel ID/version number để đoán session ID. Trang private trả 404 trong phiên API token; endpoint nội bộ không cung cấp ID hợp lệ. Người dùng chỉ có access token, không truy cập UI và đã chỉ đạo tiếp tục push. Chưa xác nhận cancellation của v1/v2; không khẳng định trạng thái hiện tại của version cũ từ status của version mới nhất.

Server đang từ chối request mới dù GPU quota còn. Phải chờ một slot được giải phóng hoặc lấy được session ID thật để hủy. Không đổi account sang account hết quota, không dùng CPU/P100 và không bỏ gate hai T4/49-of-49.

Tiến trình nền `scripts/monitor_b3_swap_until_running_20261110.py` đã được khởi động ẩn trên máy local theo yêu cầu tiếp tục push: kiểm tra/push cùng kernel mỗi 60 giây, ghi `monitor_status.json` và `monitor_events.jsonl`, tự dừng khi RUNNING hoặc có trạng thái/lỗi cần kiểm tra. Không tạo kernel khác, không đoán cancellation ID. Trạng thái monitor và version phải được đọc lại trước khi thao tác thủ công.

## Yêu cầu chia sẻ

Người dùng yêu cầu thêm `duchuynguyen1802` làm người xem. **Chưa cấp được quyền**: CLI/SDK hiện có không có notebook-collaborator mutation và token không truy cập được private UI/API nội bộ. Cần chủ tài khoản đăng nhập web rồi dùng Share để thêm người nhận. Xem `share_request.json`; notebook hiện vẫn private. Private input dataset có quyền riêng nếu người nhận cần chạy lại.

## Runtime acceptance còn chờ

Source readback và API status chưa phải chứng nhận runtime. Cần output của đúng version tạo record, model/tokenizer/source/package/build/native-offload provenance, hai T4 và 49/49 layer, constructor/threads, records identity và census. Không ghép output của các version trùng nhau mà chưa kiểm đầy đủ identity và duplicate IDs.

Credential/token và ZIP prompt không được push Git. Các file `kernel/`, metadata/manifest/checksum, receipts và script deployment được công bố để tái lập thao tác.
