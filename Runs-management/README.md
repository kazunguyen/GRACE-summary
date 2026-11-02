# Runs-management — giữ gì và cập nhật ở đâu?

Thư mục này lưu **sổ chạy, trạng thái, ngưỡng và bằng chứng cần để tiếp tục run**. Code .py không mặc nhiên là rác; JSON sinh tự động vẫn quan trọng nếu ghi identity, hash, ngưỡng hoặc nguồn kiểm toán. Prediction/embedding/ZIP inference lớn nằm ở output của từng arm, chỉ liên kết từ đây.

## Người chạy thường xuyên đọc/cập nhật

| File | Vai trò | Khi nào ghi? |
|---|---|---|
| [RUNS.md](RUNS.md) | Sổ duy nhất cho mọi lượt Joern, CodeT5, prompt, inference | Trước khi nhận/chạy và sau mỗi lần hoàn tất, timeout, lỗi, resume |
| [HIEN_TRANG.md](HIEN_TRANG.md) | Bảng record đã kiểm local; sinh từ [current_status.json](current_status.json) | Dùng refresh_current_status.py sau khi cập nhật nguồn đúng phiên; không sửa tay |
| [MA_TRAN_RUN.md](MA_TRAN_RUN.md) | Định nghĩa arm/tầng/seed, ghi chú cấu hình | Khi chốt kế hoạch hoặc đổi trạng thái/variant của arm |
| [TIEN_DO_PHUONG_AN_2.md](TIEN_DO_PHUONG_AN_2.md) | Tiến độ 10 bước, điều kiện nghiệm thu, audit đã gộp, mốc cải tiến | Khi hoàn tất một điều kiện/milestone hoặc phát hiện hạn chế mới |
| [QUY_UOC_FRAMEWORK_20261101.md](QUY_UOC_FRAMEWORK_20261101.md) | Quy ước dữ liệu, graph, score chung | Đọc trước chạy; mọi sửa đổi cần phiên/amendment, không tự thay khi resume |
| [CHANGES_AFTER_ANALYSIS_LOCK.md](CHANGES_AFTER_ANALYSIS_LOCK.md) | Nhật ký sửa protocol/code sau analysis lock | Khi thay protocol, pipeline hoặc cách diễn giải; không backdate |
| [TU_DONG_KHOA_NGUONG.md](TU_DONG_KHOA_NGUONG.md) | Khóa validation, phương pháp tau, căn cứ PDF, vận hành helper | Khi quy trình/ngưỡng có thay đổi được nghiệm thu |
| [NGUY_CO_CHAY_LAI_DO_DONOR.md](NGUY_CO_CHAY_LAI_DO_DONOR.md) | Tác động donor và danh sách B2/flip cần score mới | Khi chuyển phiên donor hoặc đã có kết quả migration |
| [B2_FLIP_DONOR_MOI_RESUME.md](B2_FLIP_DONOR_MOI_RESUME.md) | Đầu vào và thứ tự resume I-06 sang donor mới | Khi bàn giao/tiếp tục B2-flip |

Mẫu ghi run, notebook và đường dẫn input/output: xem [README gốc](../README.md), mục4–6. Các báo cáo kiểm toán Markdown trùng đã gộp vào TIEN_DO_PHUONG_AN_2.md; giải thích ngưỡng gộp vào TU_DONG_KHOA_NGUONG.md. Không còn generator tạo lại các báo cáo trùng này.

## Code đang dùng — giữ nguyên vị trí

| Nhóm | File | Vì sao giữ? |
|---|---|---|
| Runtime khóa | validation_lock.py | Được B0, helper B2, flip và builder rerun-66 import/nhúng; xóa sẽ làm hỏng luồng |
| Khóa local theo dõi | auto_lock_validation.py, watch_validation.py, start_validation_watch.ps1 | Chọn khóa từ đủ validation và vận hành watcher khi chủ động bật; không có kết nối tải Kaggle |
| Kiểm khóa | check_locked_thresholds.py | Đối chiếu ngưỡng đã lưu bằng sklearn, chỉ đọc validation |
| Trạng thái | refresh_current_status.py | Đọc các nguồn canonical trong SOURCES, kiểm record và sinh current_status.json/HIEN_TRANG.md |
| Audit | audit_tier1_readiness.py, audit_arm_integration.py, audit_b2_flip_I06_20261102.py | Tái kiểm điều kiện, đường gọi và hash/migration; xuất bản CURRENT riêng |
| Tái tạo donor | reconcile_donor_prompts.py, summarize_donor_reconciliation.py | Dấu vết retrieval/prompt thay đổi và kiểm export; không chạy chúng chỉ để resume |
| Test | test_current_status.py, test_validation_lock.py | Kiểm import/coverage/identity/khóa; lỗi tích hợp B2 vẫn cần sửa, không xóa test để báo xanh |

Script tạo/niêm phong analysis lock đã chạy một lần và installer/generator Markdown cũ không có caller vận hành được bỏ. Có thể tra lại bản cũ trong Git; snapshot đã tạo vẫn được giữ.

## JSON/snapshot/input quan trọng — không xóa vì “được sinh ra”

| Nhóm | Vai trò |
|---|---|
| thresholds.json | Bốn khóa B0/B2 lịch sử, identity và hash evidence; không ghi đè bằng phiên donor mới |
| threshold_lock_status.json | Snapshot watcher ngày 01/11; không phải số mới nhất của B1/flip, xem current_status.json |
| analysis_lock_20261101/, analysis_git_seal.json, analysis_record_for_OSF_20261101.zip | Bản ghi phân tích niêm phong sau khi inference bắt đầu, không phải prereg hồi tố/OSF đã công bố; giữ bytes/hash |
| KIEM_TOAN_DIEU_KIEN_TANG_1.json, KIEM_TRA_TICH_HOP_TUNG_ARM.json | Snapshot kiểm toán gốc, giữ lịch sử thay vì sửa thành tiến độ mới |
| b1_I07_20261102.json | Count/hash/nguồn của B1 đã chạy một phần |
| b2_flip_I06_20261102/ | Bằng chứng I-06, hash nguồn, CSV/JSONL33 mẫu cần sửa/33 test chưa chạy; all_prompt_comparison còn được test frozen resume dùng |
| donor_reconciliation_20261101/ | B2 donor cũ/mới, inventory/provenance và66 ID. new_reference/B2 là input trực tiếp của flip và builder07; cache dùng cho tái kiểm retrieval, không phải cache Python tạm |

Một số dữ liệu lớn trong hai thư mục bằng chứng bị .gitignore; Git clone không mang theo chúng. Xem gói bàn giao ở README gốc; người chỉ inference có thể dùng ZIP prompt đã kiểm, người tái tạo prompt cần các nguồn tương ứng.

## File tạm đã dọn

Đã xóa .pytest_cache/, __pycache__/, hai .offline_test_thresholds*/ chứa score test giả, log watcher cũ/empty stderr, năm script một lần và bốn báo cáo Markdown trùng. Đã thêm ignore cho file tạm tái sinh. Không xóa prediction/checkpoint, donor reference, cache CodeT5/CPG, ngưỡng hoặc snapshot thật. Tài liệu lịch sử còn trong Git và CHANGES_AFTER_ANALYSIS_LOCK.md.

Không chạy auto_lock_validation.py hoặc bật watcher chỉ để refresh bảng tiến độ: chúng có thể tạo khóa khi validation đã đủ. Đợt dọn này chỉ kiểm/cập nhật trạng thái, chưa tạo khóa hoặc sửa runtime B1/B2.
