# Chuẩn bị B3-swap và B3-flip — 10/11/2026

Theo yêu cầu người dùng, chuẩn bị hai arm test dùng chung selector, renderer/cắt tỉa, evaluator và runtime với B3 verified-patch. Người dùng xác nhận Dũng đã chạy B3-nodiff; đã sửa trạng thái trước đó từ excluded sang execution reported, chưa tự chứng nhận kết quả.

Đã đọc trực tiếp ZIP năm notebook runtime locked ngày 07/11 và worklogs runtime/package standardization, đối chiếu với B3 v6 và biên bản B1-full/B1-shuf. ZIP đúng hash bàn giao; cả năm hàm binary_scores giống AST với B3. Model/tokenizer/backend/constructor/GPU/scoring/threads/build/decoding/resume giống nhau. Lock B3 hiện tại bổ sung pin SciPy 1.16.3 theo amendment đã ghi.

Mỗi arm đủ 2.732 Devign + 2.274 REVEAL. Dựng lại base B3 phải khớp prompt và selection từng target. Các khối ngoài demonstration giống nguyên văn; biến đổi swap/flip được kiểm độc lập trên toàn census. Dùng exact tokenizer, chat tối đa 5.279 token; giữ reserve 64. Flip áp dụng `_flip_words` cho Key difference theo renderer chung; đã sửa mô tả cũ thiếu chi tiết này.

Hai notebook theo format B3 v6 (1 markdown +5 code cells), cùng cell setup/environment và cùng worker nhúng. Giữ bản sửa nested/symlink mounts, archive-only INPUT_DIR, model hash, helper hashes và manifest preflight. Threshold kế thừa nguyên byte B3 (0,99/0,01). Shared loader hỗ trợ arm-specific checkpoint identity. Adapter metrics local gọi evaluator table_a chung, không fit lại threshold hoặc đưa target labels lên Kaggle.

Kiểm tra: 37 governance/probe/statistics tests pass; 9 delivery tests pass. Lỗi quyền thư mục tmp hệ thống của lượt test đầu được xử lý bằng basetemp trong workspace. Source cells/modules parse được; archive/member/threshold hashes và record-loader scope pass. Agy CLI đã được thử nhưng sandbox không đọc được phiên đăng nhập; primary agent trực tiếp hoàn thiện, không gọi GPT subagents.

Bộ bàn giao: `Runs-management/b3_verified_patch_v1/probe_test_release_20261110_v1/`; xem README, PREPARATION_AUDIT.json, REFERENCE_RUNTIME_AUDIT.json và TEST_RESULTS.txt. Không upload/launch trong công việc này. Remote source readback, hai T4, 49/49 offload, effective constructor/packages/build provenance và full result census là các gate sau launch; kiểm tra local không thay thế nghiệm thu runtime.
