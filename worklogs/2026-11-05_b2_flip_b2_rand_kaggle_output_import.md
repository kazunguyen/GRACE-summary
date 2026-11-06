# Nhập output Kaggle B2-flip và B2-rand — 05/11/2026

## Việc đã làm

Đã tải lại output trực tiếp từ hai kernel Kaggle bằng Kaggle CLI 2.2.5:

```cmd
kaggle kernels output duchuynguyen1802/02-kaggle-qwen-q4-b2-rand-ipynb -p Runs-management\kaggle_outputs_20261105\b2_rand
kaggle kernels output quangdung1111/02-kaggle-qwen-q4-b2-flip-ipynb -p Runs-management\kaggle_outputs_20261105\b2_flip
```

Output thô được giữ tại `Runs-management/kaggle_outputs_20261105/`. Checkpoint và records hiện hành được sao vào thư mục output tương ứng của từng arm. Checkpoint cũ I-06/I-09 được giữ nguyên.

## I-10 — B2-flip

- Kernel: `quangdung1111/02-kaggle-qwen-q4-b2-flip-ipynb`.
- Theo `checkpoint_status.json`, bắt đầu 2026-11-04 14:51:46 UTC, hoàn tất 2026-11-04 23:07:52 UTC; giờ Bangkok là 21:51:46 ngày 04/11 đến 06:07:52 ngày 05/11, khoảng 8 giờ 16 phút. `state=complete`, `timed_out=false`.
- Tổng cuối 10.011/10.011: Devign validation 2.732, ReVeal validation 2.273, Devign test 2.732, ReVeal test 2.274. Inference phiên này thêm 4.809 lượt; sửa 33 output cũ đã đổi prompt (28 validation + 5 test) và chạy 4.776 mẫu còn thiếu. 0 invalid response, 0 invalid score.
- Hai threshold lock validation xác nhận policy `inherit_base_B2_prereg_v1`, không fit ngưỡng riêng: Devign tau=0,70; ReVeal tau=0,12. Nguồn B2 và hash được ghi trong từng `threshold_lock.json`; run manifest dùng model SHA-256 `f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335`.
- Checkpoint ZIP SHA-256: `9ef9672db4c8b0c40a1e8f1034b3f3f1ec993357f1e0b06558ffbc38bab87019`.
- Bản đã nhập: `04_Arm_B2_Flip/output/kaggle_20261105_quangdung1111_run2/`; bản tải thô gồm log, bundle và checkpoint ở `Runs-management/kaggle_outputs_20261105/b2_flip/`.

## I-11 — B2-rand

- Kernel: `duchuynguyen1802/02-kaggle-qwen-q4-b2-rand-ipynb`; tiếp tục từ I-09. Notebook chạy validation-only, không fit tau và không chạy test.
- Seed 42 resume bắt đầu 2026-11-05 00:55:46 UTC, hoàn tất 01:19:09 UTC. Seed 43 bắt đầu 01:19:20 UTC, dừng theo budget lúc 06:45:32 UTC (giờ Bangkok tương ứng 07:55:46–13:45:32). Status seed43 ghi timeout và đã checkpoint; reserve 10 phút được giữ trước deadline.
- Checkpoint cuối: seed42 Devign 2.732/2.732 và ReVeal 2.273/2.273; seed43 Devign 2.732/2.732 và ReVeal 52/2.273; seed44 chưa chạy. Lũy kế **7.789/15.015 validation**, test **0/15.018**. Phiên này thêm 207 mẫu ReVeal seed42 và 2.784 mẫu seed43.
- Validation seed42/ReVeal có 2 raw response không hợp lệ trên 2.273 hàng; cả hai vẫn có score hợp lệ. Tổng checkpoint kiểm được có 0 invalid score. Chưa fit threshold; chỉ chốt sau khi đủ validation ba seed.
- Checkpoint ZIP SHA-256: `96ad982e681a1c910be5290d4454e67899cae934421b8b648fd6e387e32052a3`.
- Bản đã nhập: `06_Arm_B2_Rand/output/kaggle_run_02/`; bản tải thô, gồm status từng giai đoạn, diagnostics, logs và ZIP theo split ở `Runs-management/kaggle_outputs_20261105/b2_rand/`.

## Tiến độ các arm theo output đã nhập local

| Arm | Trạng thái hiện biết |
|---|---|
| B0 | Hoàn tất 10.011/10.011. |
| B1 | Hoàn tất 10.011/10.011 theo I-08; lưu ý lịch sử chưa có bằng chứng khóa ngưỡng trước phần test. |
| B2 | Hoàn tất 10.011/10.011; lịch sử thứ tự test/khóa ReVeal cần giữ nguyên khi báo cáo. B2 donor rerun-66 đã ghép riêng. |
| B2-flip | I-10 hoàn tất 10.011/10.011; thừa kế ngưỡng B2. |
| B2-rand | I-11 có 7.789/15.015 validation, chưa fit tau/chạy test. |
| B2-rep | Chưa có inference output được nhập local. |
| B1-full, B1-shuf, B2-nolabel, B2-labelonly | Đã bàn giao Hiếu notebook/bundle; thư mục output Kaggle tương ứng chưa được nhập ở lần cập nhật này, nên trạng thái chạy trên cloud chưa được xác nhận. |
| B1-H2 và B3/B3-nodiff/B3-swap/B3-flip | Đang ở khâu chuẩn bị/audit validation; chưa được tính là arm inference xác nhận. |

`Runs-management/current_status.json` và `HIEN_TRANG.md` được làm mới từ records đã nhập. Bộ refresh kiểm tra ID không trùng, prompt hash, label, model hash và provenance tau B2-flip. `RUNS.md` có thêm I-10/I-11; `MA_TRAN_RUN.md` phản ánh trạng thái hiện hành. Không sửa preregistration hoặc khóa ngưỡng gốc.
