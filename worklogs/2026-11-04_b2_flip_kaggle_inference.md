# Kế hoạch inference Kaggle — 04/11/2026

## B2-flip: resume donor thống nhất

Notebook đã sửa: [`02_kaggle_qwen_q4_b2_flip.ipynb`](../04_Arm_B2_Flip/notebooks/02_kaggle_qwen_q4_b2_flip.ipynb).

Gắn vào Kaggle Input:

1. [`grace_b2_flip_frozen_donor_inputs.zip`](../04_Arm_B2_Flip/output/bundles_frozen_donor_20261101/grace_b2_flip_frozen_donor_inputs.zip), chứa đủ bốn split validation/test cho Devign và ReVeal.
2. [`grace_b2_flip_checkpoint.zip` I-06](../04_Arm_B2_Flip/output/kaggle_20261102_quangdung1111_run1/grace_b2_flip_checkpoint.zip).
3. Qwen3-Coder-30B-A3B-Instruct GGUF Q4_K_M, SHA-256 `f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335`.

Runner giữ 5.202 record I-06 còn khớp, chuyển các record có prompt cũ vào lịch sử, inference lại 28 Devign validation, rồi hoàn tất bước validation của cả hai dataset trước khi vào test. Sau validation, chạy 5 Devign test đã đổi prompt trước, rồi tiếp tục các test còn thiếu. Migration plan ước tính **4.809 lời gọi mới** tổng cộng (33 lượt sửa, gồm 28 validation + 5 test, và 4.776 prompt chưa có output). REVEAL validation được giữ vì prompt không đổi.

## Ngưỡng theo prereg-v1

`preregistration.md` mục 2, quy tắc threshold inheritance, yêu cầu B2-flip thừa kế tau B2 và cấm fit ngưỡng độc lập cho probe đảo nhãn/lặp. Runner xác minh đủ validation và identity trước khi ghi khóa B2-flip kế thừa; test bị chặn cho tới khi entry đó tồn tại. Không dùng score B2-flip để chọn lại tau.

| Dataset | Tau kế thừa | Nguồn khóa B2 | SHA-256 file nguồn | B2 validation prompt-set SHA-256 |
|---|---:|---|---|---|
| Devign | 0.70 | `01_Author_Baseline_Unified/output/local_full/inference_qwen_q4_b2_frozen_donor_20261102/thresholds_devign.json` | `c4273120a64489f38217e73e673afbf2969486248774eb2c0e33cddb6447eb52` | `5e98719dc82fea3a2115c41922cfce14e1e7265801623adb98839ccbdb214f9c` |
| ReVeal | 0.12 | `Runs-management/thresholds.json` | `96b864a3a91edf6a578ec853028d9c9cfe714addce21a6af399334ecfa1af6e5` | `531b274808e0435ce47c6d1831903e4421486a034c6884a2a67ba01e779b3e42` |

Nguồn quy tắc: [`preregistration.md`](../preregistration.md), nhất là quy tắc chọn ngưỡng và inheritance ở mục 2. Các file ngưỡng preregistered không bị sửa.

## Giới hạn Kaggle và checkpoint

Tài liệu Kaggle hiện hành ghi tối đa **12 giờ mỗi session CPU/GPU** (TPU 9 giờ): [Kaggle Notebooks documentation](https://www.kaggle.com/docs/notebooks). Notebook đặt `MAX_RUNTIME_HOURS = 9.5` và `CHECKPOINT_RESERVE_SECONDS = 600`; runtime ngừng nhận mẫu mới trước 10 phút cuối để đóng gói checkpoint. Deadline runner bắt đầu khi inference process chạy, tạo khoảng 2 giờ 30 phút dưới hard limit cho thời gian khởi động notebook, nạp model và hoàn tất output. Ngân sách 9 giờ 30 phút cũng nhỉnh hơn ước lượng khoảng 8 giờ 43 phút nếu giữ tốc độ I-06 (5.235 mẫu trong khoảng 9 giờ 29 phút), nhưng throughput GPU có thể dao động.

Nếu validation/test chưa đủ khi hết ngân sách, runner ghi checkpoint từ các record đã fsync. Tải `grace_b2_flip_checkpoint.zip` trong Kaggle Output rồi gắn làm checkpoint ở session sau; resume tiếp tục các ID chưa hoàn tất. Output mới được ghi ở `/kaggle/working/grace_b2_flip_frozen_donor_20261104_inherit_b2_9h30/`, tách khỏi checkpoint I-06 gốc.

## Các notebook validation khác trong lượt hôm nay
## Các notebook validation khác trong lượt hôm nay

Năm arm đã giao Hiếu chạy là B1-full, B1-shuf, B2-nolabel, B2-labelonly và B2-rep. Trạng thái Kaggle của Hiếu cần xác nhận bằng checkpoint/output tải về; bảng này ghi đúng notebook và bundle cần dùng:

| Arm | Notebook | Prompt bundle |
|---|---|---|
| B1-full | [`02_kaggle_qwen_q4_b1_full_validation.ipynb`](../Runs-management/kaggle_validation_6arms_20261104/02_kaggle_qwen_q4_b1_full_validation.ipynb) | [`grace_b1_full_validation_inputs.zip`](../Runs-management/kaggle_validation_6arms_20261104/grace_b1_full_validation_inputs.zip) |
| B1-shuf | [`02_kaggle_qwen_q4_b1_shuf_validation.ipynb`](../Runs-management/kaggle_validation_6arms_20261104/02_kaggle_qwen_q4_b1_shuf_validation.ipynb) | [`grace_b1_shuf_validation_inputs.zip`](../Runs-management/kaggle_validation_6arms_20261104/grace_b1_shuf_validation_inputs.zip) |
| B2-nolabel | [`02_kaggle_qwen_q4_b2_nolabel_validation.ipynb`](../Runs-management/kaggle_validation_6arms_20261104/02_kaggle_qwen_q4_b2_nolabel_validation.ipynb) | [`grace_b2_nolabel_validation_inputs.zip`](../Runs-management/kaggle_validation_6arms_20261104/grace_b2_nolabel_validation_inputs.zip) |
| B2-labelonly | [`02_kaggle_qwen_q4_b2_labelonly_validation.ipynb`](../Runs-management/kaggle_validation_6arms_20261104/02_kaggle_qwen_q4_b2_labelonly_validation.ipynb) | [`grace_b2_labelonly_validation_inputs.zip`](../Runs-management/kaggle_validation_6arms_20261104/grace_b2_labelonly_validation_inputs.zip) |
| B2-rep | [`02_kaggle_qwen_q4_b2_rep_validation.ipynb`](../Runs-management/kaggle_validation_6arms_20261104/02_kaggle_qwen_q4_b2_rep_validation.ipynb) | [`grace_b2_rep_validation_inputs.zip`](../Runs-management/kaggle_validation_6arms_20261104/grace_b2_rep_validation_inputs.zip) |
| B2-rand | [`02_kaggle_qwen_q4_b2_rand.ipynb`](../Runs-management/kaggle_validation_6arms_20261104/02_kaggle_qwen_q4_b2_rand.ipynb) | [`grace_b2_rand_inputs.zip`](../Runs-management/kaggle_validation_6arms_20261104/grace_b2_rand_inputs.zip) |

Mỗi lượt Kaggle cũng cần model GGUF đã pin theo README của gói sáu arm. B2-rep phải gọi model mới và dùng checkpoint riêng; theo prereg-v1, B2-rep thừa kế tau B2, không fit riêng. B2-rand không nằm trong năm arm đã giao Hiếu: resume validation còn thiếu với checkpoint I-09 [`grace_b2_rand_checkpoint.zip`](../Runs-management/kaggle_validation_6arms_20261104/grace_b2_rand_checkpoint.zip). Notebook B2-rand chỉ chạy validation; đủ validation theo seed/dataset thì mới khóa tau, rồi mới chạy test ở lượt sau.

B1-H2 và B3/B3-nodiff/B3-swap/B3-flip vẫn ngoài lượt confirmatory hiện tại theo hồ sơ audit; không đưa vào hàng inference hôm nay.
