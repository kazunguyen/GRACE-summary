# I-18 — B2-rand test seed 42 dừng theo giới hạn thời gian

Đã tải output bằng `kaggle kernels output quangdung1111/02-kaggle-qwen-q4-b2-rand-seed42-test-ipynb -p <dest>`. [Thư mục output](../Runs-management/kaggle_outputs_20261107/b2_rand_seed42_test_latest/).

| Dataset | Đã lưu | Tổng | Còn |
|---|---:|---:|---:|
| Devign | 2.732 | 2.732 | 0 |
| REVEAL | 2.017 | 2.274 | 257 |
| Tổng seed 42 | 4.749 | 5.006 | 257 |

Status ghi `timed_out` và lưu checkpoint cuối lúc **19:44:17 ICT (12:44:17 UTC), 07/11/2026**. Setup bắt đầu lúc 10:49:46 ICT, worker bắt đầu 11:07:40 ICT. Lũy kế B2-rand đã xác minh 15.015/15.015 validation và 4.749/15.018 test. Chưa nhập output test seed 43/44 trong lần này.

- Kiểm CRC checkpoint và đối chiếu records của cả hai dataset byte theo byte với file output tải rời. Đếm ID duy nhất, đối chiếu label và prompt SHA với bundle xuất từ Kaggle, kiểm model SHA, runtime SHA, score hữu hạn và ngưỡng validation cố định Devign 0,99 / REVEAL 0,89.
- Checkpoint `grace_b2_rand_seed42_test_checkpoint.zip` có SHA-256 `af7f41c10a779db82237d309ad2397f8e37d054751082fd56b5337f3d19b53ff`. Log xác nhận **49/49** layer offload.
- Phiên dùng lock `85d8770839f80260cdc7c27b27b6cce6bf8815675c8593db68fb102589c5cbd6`. Log sau cài đặt ghi SciPy 1.16.3, phiên bản này chưa được pin trong lock của phiên. Notebook đã cập nhật sau đó dùng SHA lock khác. Để tiếp tục checkpoint này, dùng đúng notebook/lock của I-18. Checkpoint kiểm runtime SHA theo record.
