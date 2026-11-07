# I-19 — B2-rand test seed 43 dừng theo giới hạn thời gian

Đã tải output bằng `kaggle kernels output quangdung1111/02-kaggle-qwen-q4-b2-rand-seed43-test-ipynb -p <dest>`. [Thư mục output](../Runs-management/kaggle_outputs_20261107/b2_rand_seed43_test_latest/).

| Dataset | Đã lưu | Tổng | Còn |
|---|---:|---:|---:|
| Devign | 2.732 | 2.732 | 0 |
| REVEAL | 2.028 | 2.274 | 246 |
| Tổng seed 43 | 4.760 | 5.006 | 246 |

Metadata Papermill của notebook tải về ghi chạy **11:09:29–20:04:09 ICT ngày 07/11/2026**. Worker bắt đầu 11:27:28. Status ghi `timed_out` và lưu checkpoint cuối lúc **20:04:03 ICT (13:04:03 UTC)**.

- Kiểm CRC checkpoint, so byte records với output tải rời, đối chiếu ID duy nhất, label, prompt SHA, model SHA, runtime SHA và điểm hữu hạn. Ngưỡng cố định Devign 0,99 và REVEAL 0,62. Log xác nhận offload 49/49 layer.
- Checkpoint `grace_b2_rand_seed43_test_checkpoint.zip` có SHA-256 `de9f1ab66f39609b413cd6795dafecb7176dba0ac34526cb926788e14b7c9aeb`. Runtime lock của I-19 có SHA-256 `85d8770839f80260cdc7c27b27b6cce6bf8815675c8593db68fb102589c5cbd6`, trùng với bản notebook seed 43 đã chạy tải về và với I-18. Log sau cài đặt ghi SciPy 1.16.3. Resume cần đúng SHA runtime của phiên.
- Lũy kế B2-rand đã xác minh **15.015/15.015 validation** và **9.509/15.018 test**. Còn 257 REVEAL ở seed 42 và 246 REVEAL ở seed 43. Chưa xác minh output test seed 44 trong lần nhập này.
