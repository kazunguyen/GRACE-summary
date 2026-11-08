# Gói tiếp tục sau kiểm toán — 08/11/2026

Các file được chuẩn bị local, chưa upload và chưa khởi chạy GPU. Hash nằm trong `delivery_manifest.json`. Không thay prompt, threshold, model hay runtime contract.

## B1-shuf: sẵn sàng chạy lại từ đầu sau sửa bộ đọc log

Notebook: `02_kaggle_b1_shuf_test_gpu_log_guard_fixed.ipynb`.

- Dùng đúng notebook này cho một phiên mới, GPU T4×2 và Internet, gắn model Q4_K_M cùng dataset `lznt123/grace-b1-shuf-test-inputs` hiện có. Không gắn checkpoint lỗi cũ: chưa có record inference nào cần phục hồi.
- Input bundle giữ nguyên SHA-256 `a6b2be70b85462d96d531884085eb62d581e5863cb8897a86b23f326f284508b`. Đủ 15.018 prompt ba seed, đã kiểm tổng context/reserve và target code. Các threshold và contract đều giữ nguyên.
- Chỉ sửa helper nhận diện ID GPU từ cả định dạng `Device 0: ... T4` và `using device CUDA0 (Tesla T4)`. Khi có log model-load, ưu tiên ID GPU thực được dùng. Phải có chính xác CUDA0/CUDA1, vẫn bắt buộc 49/49 và context/batch/microbatch đúng.
- Sáu kiểm tra bằng fake model replay log thật đã lưu đạt: chấp nhận log thật hai T4; từ chối một GPU, hai dòng cùng CUDA0, 48/49, context sai và GPU không phải T4. Không coi đây là inference GPU mới.
- Theo dõi sau load: gate phải qua, rồi bắt đầu sinh record. Nếu lỗi khác, giữ diagnostics; không tắt assertion để tiếp tục.

## B3: có thể tiếp tục phiên validation lịch sử, không đổi âm thầm sang amended/runtime-locked

Notebook: `02_kaggle_b3_historical_validation_resume.ipynb`.
Checkpoint: `grace_b3_validation_checkpoint.zip`, byte-identical với checkpoint đã nghiệm thu.

- Dùng phiên mới với cùng model, bundle validation SHA-256 `87527ce21b8eff4d07cb8e979f16d312c7f336fe9382ed825a24767f592363d9`, GPU T4×2, và checkpoint trong gói này. Gắn checkpoint như một Kaggle Dataset riêng hoặc input mà notebook tìm được.
- `CHECKPOINT_INPUT_PATH=None` giữ auto-discovery của runner gốc: trong các input chỉ được có một file tên `grace_b3_validation_checkpoint.zip`. Nếu có nhiều file trùng tên, đặt biến này thành đúng đường dẫn file thuộc gói đã kiểm; không chọn checkpoint theo tên mơ hồ.
- Giữ 4.029 record: Devign B3 2.732, REVEAL B3 1.297. Còn 976 REVEAL B3 và toàn bộ 5.005 B3-nodiff. Runner đi tiếp cả hai arm, tổng đích 10.010 validation; chưa fit threshold hay chạy test.
- Chỉ clear output notebook để bàn giao; inference runner giữ nguyên phiên lịch sử. Có log 49/49, hai T4 và package đúng, nhưng provenance không đủ chứng nhận runtime lock đầy đủ. Không ghép dữ liệu này vào một run tự xưng fully runtime-locked mà không có migration được review.
- Việc đủ điều kiện nguồn/cặp patch cho B3 amended là vấn đề phương pháp riêng, chưa được xác nhận bởi gói resume này. Nếu mục tiêu bắt buộc là B3 amended, chưa dùng gói này để thay thế việc duyệt pair pool.

## B1-full: chỉ phục hồi checkpoint, chưa sẵn sàng resume inference

Archive: `grace_b1_full_test_recovered_2850.zip`.

- Giữ nguyên byte 2.850 record rời đã tải, gồm 2.732 Devign + 118 REVEAL. ZIP periodic gốc chỉ có 2.846 record (REVEAL 114); bốn record cuối được phục hồi từ file rời đã đối chiếu cloud và input.
- Đây là forensic recovery, không phải chứng nhận runtime lock; không tạo giả manifest REVEAL vốn không được xuất khi run lỗi.
- Không upload archive này để chạy lại cùng prompt rồi mong qua lỗi: `reveal:test:118` vẫn có 10.200 token context.
- Kiểm toán theo đúng block renderer còn phát hiện B1-full vượt cả budget graph/code ở nhiều ID. Danh sách trong `../b1_full_component_audit.json`. Cần quyết định sửa bộ dựng theo giao thức, lưu phiên prompt mới và xác định các ID đã chạy bị ảnh hưởng trước khi resume/rerun. Không tự skip mẫu, tăng context, cắt prompt thủ công hoặc chọn lại threshold theo test.
