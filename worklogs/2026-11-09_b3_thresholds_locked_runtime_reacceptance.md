# B3 mới: khóa ngưỡng và nghiệm thu lại runtime — 2026-11-09

Theo yêu cầu trực tiếp của người dùng, hoàn tất Bước 12 cho B3 `b3-verified-patch-v1`, seed42, cả Devign và REVEAL. Đọc lại raw validation census 2.732 + 2.273, bundle/record/run identity, score-logprob; quét lại 99 ngưỡng và đối chiếu toàn grid với optimizer độc lập. Khóa riêng Devign τ*=0,99 và REVEAL τ*=0,01 trong `Runs-management/b3_verified_patch_v1/threshold_release_20261109_v1/`.

Đọc embedded runtime contract cả 5 notebook ZIP gốc. Core policy khớp; contract hiện hành bổ sung pin scipy1.16.3. Kiểm mọi session được records tham chiếu: Devign2.732; REVEAL1.713+560 resume. Native logs/hash, 7 package/pip freeze, constructor, CPU threads, SM75 build/toolchain và provenance đạt contract platform build. Phân bố thực 25/24 layer trên 2 T4, tổng49/49; context8192 và batch/ubatch256. Không khẳng định binary giống hệt hoặc chạy bằng llama-server b3920.

Thêm loader khóa ngưỡng có kiểm raw SHA, canonical seal và application identity. 10 kiểm tra readback/từ chối checksum, seal, pool và runtime sai đều PASS. File ngưỡng preregistration giữ nguyên. Không dùng test data hoặc chạy GPU mới trong lượt này.

User authorization được ghi nguyên văn với timestamp thật trong governance record; không tạo chữ ký người duyệt hay sửa hồ sơ lịch sử. Phân loại `AMENDED_EXPLORATORY_SUBPROTOCOL`, không tuyên bố cập nhật OSF. Còn dựng/audit delivery test và tích hợp gate khóa ngưỡng trước launch. Báo cáo: `Runs-management/b3_verified_patch_v1/THRESHOLD_LOCK_ACCEPTANCE_20261109.md`.
