# Dry-run validation — 02/11/2026

Entry point: [KET_QUA.md](KET_QUA.md), [summary.json](summary.json), [verification.json](verification.json).
Đã hoàn tất và kiểm bàn giao: 70.070 dòng/28 tập. Sau đối chiếu nguồn, 28/28 tập đạt audit tự động. Bước 3 còn năm arm blocked và chấm tay.

- Phạm vi: đủ validation Devign 2.732 và REVEAL 2.273; 10 tên arm, 14 tổ hợp arm/seed mỗi dataset; dự kiến 70.070 dòng prompt/28 tập.
- B1-shuf và B2-rand chạy seed 42/43/44; các arm còn lại seed 42.
- B1-H2 cùng B3/B3-nodiff/B3-swap/B3-flip bị blocked vì thiếu đầu vào, không điền dữ liệu giả.
- [USER_DECISIONS.json](USER_DECISIONS.json) ghi các lựa chọn phạm vi và 30 target thiếu graph. Mỗi target vẫn xuất hiện ở từng seed B1-shuf với graph trống và cờ missing.
- Đây là dựng prompt và audit CPU. Không gọi LLM, không sinh score hoặc tính tau.

## Cách chạy lại

Dùng một thư mục output mới dưới Runs-management; không ghi đè hồ sơ này. Cần có toàn bộ snapshot frozen, specs cũ, donor cache và B2 new_reference ở local, cùng tokenizer Qwen pinned trong cache Hugging Face. Clone Git không tự có các dữ liệu này.

Trong WSL, từ thư mục GRACE-summary:

~~~bash
USE_TORCH=0 USE_TF=0 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false \
.venv-wsl/bin/python -u -B Runs-management/dry_run_full_validation.py \
  --missing-target-graph empty --threads 4 \
  --out Runs-management/dry_run_validation_NEW
~~~

Bộ chạy gọi render_arm dùng chung và audit_rows, bổ sung adapter scaffold trống B0/B1 theo contract hiện tại; sử dụng graph prefix cache đã kiểm hash/tái dựng, lazy index graph donor và các process CPU độc lập và tokenizer chính xác offline. Đây không phải chạy nguyên xi run_matrix.py: CLI gốc nạp toàn bộ donor CPG vào RAM và không giữ scaffold phiên hiện tại. Manifest ghi rõ prompt_variant project_frozen_donor_dryrun_v1. Không coi bundle này là output inference hay bản thay thế tự động cho các ZIP Kaggle cũ.

Kiểm tra hồ sơ sau khi chạy xong:

~~~bash
python -B Runs-management/verify_full_validation_dry_run.py Runs-management/dry_run_validation_NEW
~~~

Lượt thread dở được giữ ở [interrupted_threads](../dry_run_validation_20261102_interrupted_threads/ATTEMPT_STATUS.json); không tính là kết quả hoàn thành.

## Đọc kết quả

Mỗi dataset/validation/arm/seed có prompts.jsonl, manifest.json, audit_summary.json, audit_rows.csv và raw_label_flags.json. summary.json tổng hợp token p50/p95, tỷ lệ cắt, demo rỗng và graph thiếu; blocked_arms.json ghi các đầu vào thiếu; source_hashes.json ghi provenance. verification.json kiểm hash prompt, ID validation, context và bộ mẫu.

60 prompt và hai phiếu chấm để trống được sinh cho đúng phiên dry-run này. Phải dùng RUBRIC.md đã cập nhật cho cả 10 arm. Hai người đọc độc lập rồi lập biên bản phân xử; chưa có chấm thực tế thì không ghi Bước 3 hoàn thành. Audit này cũng không thay đổi lịch sử các run đã inference trước audit/khóa ngưỡng.

Kết luận cuối: [final_status.json](final_status.json). summary.json và các audit_summary giữ kết quả bộ dò gốc: 27 pass, 1 needs_review. Cảnh báo nhầm do node code bị cắt được truy về frozen donor tại [leak_review.json](leak_review.json). Danh sách cờ từng mẫu: [review_flags.csv](review_flags.csv).
