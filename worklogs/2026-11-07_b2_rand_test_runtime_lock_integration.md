# 2026-11-07 — Tích hợp runtime lock vào B2-rand test seed 42 và 43

## Thay đổi

- Hai notebook trong 06_Arm_B2_Rand/test_delivery_20261107 nhúng nguyên byte configs/inference_runtime_lock.json cùng SHA-256, ghi bản đó ra /kaggle/working và kiểm tra cả hash file lẫn checksum canonical. Không cần thêm JSON vào Kaggle Input; đổi contract phải tái tạo notebook, không tự lấy cấu hình mới qua mạng.
- Cài sáu phiên bản từ contract; tải source archive llama-cpp-python 0.3.16 qua metadata PyPI, xác minh SHA-256 trước build. Cài lại source đã xác minh với --no-deps để bước build không tự nâng các package đã khóa.
- Kiểm tra package thực tế và nguồn cài backend trước scoring. Áp dụng n_ctx=8192, n_batch=n_ubatch=256, seed=4294967295, split_mode=layer, tensor_split=None, các đối số khác từ contract. CPU threads dùng công thức default đã chốt và ghi giá trị hiệu dụng.
- Giữ nguyên phương pháp eval/logits cuối, float64 normalization, greedy argmax; không sampling, không đổi prompt hoặc threshold lock.
- Ghi runtime_provenance.json: contract/source/runner/compiled-library hashes, package versions và pip freeze, Python/OS/libc, GPU UUID/order/VRAM/driver, compiler/CMake/nvcc, CPU threads, constructor. Ghi GPU VRAM trước/sau load và hash log offload.
- Dùng redirect_stderr bắt logger Python của backend vào file model_load_offload.log trên ổ Kaggle local; in lại nội dung và dừng nếu không xác minh được 49/49 layer offload.
- Run manifest, record và batch summary mang runtime_contract_sha256. Checkpoint thiếu hoặc khác contract bị từ chối; không tự gộp output lịch sử vào phiên mới.
- Giữ hỗ trợ bundle ZIP và Input Kaggle đã giải nén, kiểm tra hash thành phần như trước. Bundle prompt ZIP không thay đổi.
- Cập nhật generator để tái tạo notebook có tích hợp runtime lock; cập nhật hash notebook trong delivery_manifest.json.

## Phát hiện thêm khi kiểm tra resume

- Runner cũ yêu cầu len(runs)==2, trong khi bộ điều phối chỉ truyền dataset chưa hoàn tất. Nếu một dataset đã xong, resume sẽ lỗi. Cho phép 1–2 dataset chưa xong, vẫn giữ kiểm kê đầy đủ hai dataset ở notebook và xác minh từng bundle/ID.
- Hàm snapshot kế thừa tên grace_b1_h2_test_checkpoint.zip. Đổi tên theo output root thành grace_b2_rand_seed42_test_checkpoint.zip hoặc seed43 tương ứng.

## Kiểm tra

- Parse JSON và compile mọi code cell, kể cả runner viết bằng %%writefile và module helper nhúng.
- Kiểm tra bằng stub local: constructor áp dụng đúng seed/batch/microbatch/auto split; package lệch và contract bị sửa byte đều bị từ chối; log offload thiếu hoặc chỉ 24/49 bị từ chối.
- Kiểm tra resume cho cả seed 42 và 43: record có đúng contract được đếm để skip; record thiếu contract bị từ chối.
- Không chạy inference GPU hoặc build CUDA trên Kaggle trong lượt này. Các kiểm tra constructor/offload dùng stub, chưa chứng nhận runtime Kaggle thực tế.

## Cách dùng

Tải lại đúng notebook seed lên Kaggle, chọn T4×2 và Internet, chạy từ đầu. Giữ nguyên Input model và prompt bundle. Không dùng checkpoint phiên cũ không có runtime contract identity để resume tự động; giữ nguyên output cũ nếu cần đối chiếu/migration riêng.

## Sửa Input Kaggle sau lỗi thực tế — 2026-11-07

Người dùng gửi traceback seed 43. Output cho thấy Kaggle đã giải nén cả ZIP con: thay vì `seed_43/devign_test.zip`, mount có `seed_43/devign_test/bundle_manifest.json`, `prompts.jsonl`, `threshold_lock.json` (tương tự ReVeal và seed 42). Bản sửa trước chỉ cho phép các tệp ZIP con còn nguyên, nên vẫn thất bại. Đây là lỗi giả định cấu trúc Input trong notebook, không phải do người dùng thiếu Input.

Đã cập nhật cả hai notebook và helper tạo notebook để hỗ trợ ba dạng: bundle ZIP gốc; ZIP con được giữ nguyên trong dataset; hoặc Kaggle bung tiếp ZIP con thành các thư mục `seed_N/{dataset}_test/`. Ở dạng cuối, notebook xác minh SHA-256 của từng `bundle_manifest.json`, `prompts.jsonl` và `threshold_lock.json` khớp byte gốc bên trong ZIP đã đóng băng; sau đó vẫn kiểm tra threshold seal, định danh split/seed, số lượng ID, prompt hash và model. Không đổi bundle, prompt, threshold hay runtime lock.

Đã chạy kiểm tra bằng chính bundle trên local với cấu trúc y hệt traceback Kaggle (`/datasets/<owner>/<slug>/seed_N/{dataset}_test/...`) và dạng giữ ZIP con, cho cả notebook seed 42 và 43. Cả hai đều đọc đúng hai bộ prompt của seed mình, xác minh hash và số lượng mẫu. JSON/cú pháp code cells được compile lại và hash notebook trong delivery manifest được cập nhật. Chưa chạy inference trên Kaggle; cần thay notebook trong Kaggle bằng bản local đã sửa rồi Run All lại.

### Lỗi còn sót trong lần chạy Kaggle tiếp theo

Người dùng gửi notebook đã chạy thật. Input discovery và xác minh prompt đã thành công, nhưng runner báo `FileNotFoundError: /kaggle/working/b2_rand_test_bundles/devign_test.zip`: nhánh xử lý thư mục bung sẵn giữ member bytes trong bộ nhớ nhưng không dựng lại ZIP cục bộ mà runner nhận làm đối số. Ngoài ra, khối `finally` còn mở lại ZIP để lấy tau, có thể che lỗi gốc khi ZIP cục bộ chưa tồn tại.

Đã sửa cả hai nhánh: khi Kaggle đã bung ZIP con, tạo ZIP tạm local từ member bytes đã qua kiểm tra hash; ghi ngưỡng đã đọc vào `locked_thresholds` để khối tổng kết không phải mở ZIP lần nữa. Giữ nguyên các hash dữ liệu và runtime contract. Đã replay đoạn Input thật trên cả hai notebook với layout y hệt Kaggle, xác nhận hai bundle runner tồn tại, mở được bằng `zipfile`, có đủ ba member và hash nội dung khớp byte gốc; kiểm tra luôn khối summary. Chưa chạy inference GPU trên Kaggle.
