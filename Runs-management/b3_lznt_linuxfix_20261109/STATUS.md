# B3 thuật toán mới — Linux payload fix và chuyển lznt123

**Kernel mới:** [lznt123/grace-b3-new-dual-linuxfix-20261109](https://www.kaggle.com/code/lznt123/grace-b3-new-dual-linuxfix-20261109), version1. API nhận launch09/11/2026 **06:25:29 GMT+7**, sau24 tests PASS. Source readback exact, PRIVATE/GPU enabled, shape NvidiaTeslaT4, đúng2 input datasets và model source thuộc lznt123. API hiện RUNNING; native runtime evidence chưa quan sát.

## Đây là B3 thuật toán mới

Method `b3-verified-patch-v1`; cùng pool người thật đã duyệt, selector/ranking/renderer và prompts Devign v6 / REVEAL v7. Fixed order Devign2732 → REVEAL2273, validation seed42, một child model active. Không chạy B3 lịch sử, không lấy historical score/τ*, không mở test/nodiff/swap/flip.

Chỉ tạo **execution revision** `b3_linux_member_directory_v1_20261109` cho vận chuyển dữ liệu và worker metadata. Logical source input releases giữ nguyên, root mới trỏ parent root hashes và ghi riêng source-input Git metadata với execution Git/source hashes. Mọi code/input/root pin của revision mới được lưu tại `b3_dual/`.

## Lỗi cũ và nguyên nhân chính xác

HU kernel đã ERROR trong `dual.prepare`: `Prepared ZIP differs from independent pin`. Dừng trước install/build/model; **0 records, không có score bị ảnh hưởng**.

Đã so từng member giữa ZIP originalWindows và ZIP Kaggle tạo lại: **mọi payload bytes giống nhau**. Khác biệt metadata `ZipInfo.create_system` là Windows0 so với Linux3, làm hash cả archive khác dù payload không đổi. [Diagnosis](zip_failure_diagnosis.json). Bằng chứng lỗi và source cũ giữ tại HU `remote_output`; source coordinator trước sửa lưu trong `previous_coordinator.py`.

Đây là thiếu sót kiểm tra cross-platform của delivery, không phải lỗi model/scoring hoặc pair/algorithm.

## Sửa đúng nguyên nhân, không bỏ hash gate

- Packed ZIP nguyên gốc vẫn phải khớp external archive SHA như trước.
- Input đã unpack được kiểm **toàn bộ member set + SHA từng file** từ independent pinned input root; không tin self-declared prompt hash đơn lẻ. Missing/extra/tampered member bị từ chối.
- Coordinator chép payload đã xác minh vào thư mục riêng theo dataset và kiểm lại inventory, không nén lại để so ZIP bytes.
- Worker chỉ đổi trường metadata identity: giữ original archive SHA như source identity và thêm transport mode directory; không gọi file-hash trên thư mục. Load/scoring/model/tokenizer functions giữ nguyên AST; không đổi numeric inference.
- Đã kiểm bằng chính ZIP lỗi tải từ Kaggle và case ZIP_STORED khác byte: payload unpack đúng được nhận; packed transport sai hash vẫn reject; member sai hash vẫn reject.

## Chuyển account đã thực hiện

Theo yêu cầu trực tiếp của người dùng, hai input archives nguyên bytes được đưa vào PRIVATE datasets của LZ:

- `lznt123/grace-b3-devign-v6-inputs-20261109`.
- `lznt123/grace-b3-reveal-v7-inputs-20261109`.

Model source `lznt123/qwen3coder30b-prepare-notebook` đọc được, version2; **model file thực vẫn bắt buộc đúng SHA** trước load/inference, không coi tên/version kernel source là bằng chứng model hash. Source readback xác nhận mounts. Không sửa hoặc mở lại HU B3 đã failed; không can thiệp B1-shuf trong lần chuyển B3 này.

## Runtime settings và thời điểm chứng nhận

Settings giữ nguyên: Qwen3-Coder-30B-A3B-Instruct GGUF Q4_K_M/hash đã khóa; llama-cpp-python0.3.16 và sdist đã khóa;7 package pins; exact tokenizer revision; T4x2, layer split, tensor_split=None, n_gpu_layers=-1; context8192, batch/ubatch256; full49/49, reset/KV, direct logits/float64 scoring, không sampling hoặc CPU fallback. Tỷ lệ layer theo free VRAM, không cam kết25/24 cố định. Build/platform variation được phép theo contract nhưng phải ghi exact provenance.

**Setting đúng chưa đồng nghĩa actual native runtime đã được chứng nhận.** Notebook tự kiểm trước score và abort nếu sai. Nghiệm thu độc lập cần:

1. Root/source pins và actual model hash/tokenizer equality.
2. `runtime_provenance.json`: packages, constructor, runner, binaries/toolchain/GPU identities.
3. `model_load_offload.log`:2 T4,49/49 layers và effective ctx/batch/ubatch.
4. Full backend build log (`grace_diagnostics/install_llama_cuda.log` hoặc diagnostics ZIP), khớp hash trong provenance.
5. Run manifest và record/scoring evidence khớp đúng input/worker/runtime identity.

Có thể chứng nhận ngay khi có bộ bằng chứng này sau model load/first valid inference; **không phải chờ đủ validation5005**. Nhưng API live-output có thể chỉ cung cấp artifact sau phiên dừng/hoàn tất; lúc đó thu toàn bộ output/checkpoint **và diagnostics** để đối chiếu. Không gán PASS chỉ vì API RUNNING. Hiện mới PASS CPU24 tests + server readback; native evidence PENDING.

## Bằng chứng

`cpu_preflight.json/log`, `zip_failure_diagnosis.json`, `model_source_check.json`, `upload_*.json`, `b3_dual/delivery.json`, `roots/`, `code/`, `launch.json`, `source_readback.json`, `status.json`. Draft trước khi tách rõ execution provenance được giữ riêng; bản launch dùng revision cuối, không ghi đè data releases v6/v7 hoặc frozen assets.
