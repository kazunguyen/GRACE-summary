# B2-rand seed 44: hoàn tất validation, khóa tau và chuẩn bị test

Ngày ghi nhận: 07/11/2026 (Asia/Bangkok)

## Kết quả validation

Đã tải output của `duchuynguyen1802/02-kaggle-qwen-q4-b2-rand-ipynb` bằng Kaggle CLI về `Runs-management/kaggle_outputs_20261107/b2_rand_seed44_validation_latest/`.

| Prompt seed | Dataset | Validation | tau khóa | MCC validation |
|---:|---|---:|---:|---:|
| 44 | Devign | 2.732/2.732 | 0,99 | 0,055851 |
| 44 | REVEAL | 2.273/2.273 | 0,64 | 0,089166 |

Notebook papermill ghi thời gian **10:58:12–15:34:03 ICT** (03:58:12–08:34:03 UTC); worker seed44 chạy 11:16:41–15:33:56 ICT và hoàn thành 5.005/5.005. Không timeout. Checkpoint SHA-256 `a9e8245b47e859dfb6267d439f5225394396edf51b2eecb43187637e87325904`.

Đã đối chiếu đủ 15.015 validation record của ba seed 42/43/44 với frozen input: tập ID, nhãn, prompt SHA-256, arm, seed, split, model SHA, tokenizer revision và scoring khớp; mọi score đều finite và valid. Không có test record trong output validation. Checkpoint ZIP mở/kiểm tra được.

## Khóa ngưỡng

Chỉ dùng score và nhãn validation, quét tau 0,01–0,99 theo MCC, quy tắc hòa trong `1e-9` chọn gần 0,5 nhất rồi tau thấp hơn. Không đọc nhãn, score hay metric test khi chọn tau.

- Cấu hình canonical: `configs/thresholds.json`, đã thêm `devign|B2-rand|44 = 0.99` và `reveal|B2-rand|44 = 0.64`; chữ ký `locked_sha256`: `a86846df65b2f91c9acf9c27c74e9aa2895fd6604bf7e20116021bc8c230fe92`.
- Đồng bộ `configs/thresholds_flat.json`, diagnostic kit và `Runs-management/thresholds.json`.
- Khóa chi tiết arm: `06_Arm_B2_Rand/config/threshold.json`; SHA-256 chữ ký `48c12066bbddabc8ef674a70f6f9ac68cb74cbeecc2a5ebbbda3cb4cb6498735`.

## Kiểm tra runtime lock

Notebook Kaggle seed44 mới nhất ghi runtime contract SHA-256 `85d8770839f80260cdc7c27b27b6cce6bf8815675c8593db68fb102589c5cbd6`, đúng với `configs/inference_runtime_lock.json`. Run manifest cho biết package versions khớp lock: NumPy 2.1.3, huggingface-hub 0.36.2, tokenizers 0.22.2, Transformers 4.57.1, llama-cpp-python 0.3.16, scikit-learn 1.5.2; backend source archive SHA khớp `34ed0f9bd9431af045bb63d9324ae620ad0536653740e9bb163a2e1fcb973be6`. GPU log ghi 2×Tesla T4 và `offloaded 49/49 layers to GPU`.

Phạm vi lịch sử cần giữ rõ: trong 2.732 record Devign validation của seed44, **2.426 record** đã được kế thừa từ I-15 trước khi notebook tích hợp runtime lock. Manifest đánh dấu `reviewed_legacy_resume` và giữ nguyên provenance cũ, không đóng dấu hồi tố. **306 record Devign còn lại** và toàn bộ **2.273 REVEAL record** thuộc run mới có runtime lock; REVEAL manifest là `fresh_locked_run`. Vì vậy notebook/run mới và phần inference mới tuân thủ lock, còn Devign seed44 validation tổng hợp có provenance kế thừa một phần. Ngưỡng được fit trên toàn bộ 2.732 Devign validation record đã xác minh; giới hạn provenance này được lưu trong manifest/config, không che như một run hoàn toàn mới.

## Bundle và notebook test

Tạo bundle riêng cho seed44 từ nguyên các frozen test ZIP trong `grace_b2_rand_inputs.zip`; prompt bytes không thay đổi. Bundle SHA-256 `e8bf81b3d5355a19221f7e61bbe19af81a31c953fd929c8e642918f67659590d`.

- [Test bundle](../06_Arm_B2_Rand/test_delivery_seed44_20261107/grace_b2_rand_test_seed44_bundle.zip)
- [Notebook Kaggle seed44 test](../06_Arm_B2_Rand/test_delivery_seed44_20261107/02_kaggle_qwen_q4_b2_rand_seed44_test.ipynb)
- [README chạy](../06_Arm_B2_Rand/test_delivery_seed44_20261107/README.md)
- [Delivery manifest](../06_Arm_B2_Rand/test_delivery_seed44_20261107/delivery_manifest.json)

Notebook chỉ chạy seed44 test, dùng tau đã khóa, giữ resume per-ID và giới hạn 9 giờ với 5 phút dự phòng. Nó kiểm tra/applies runtime lock, package/source/model/tokenizer hashes, constructor và yêu cầu log 49/49 offload. Bộ dò input xử lý cả bundle ZIP nguyên, Kaggle bung lớp ZIP ngoài nhưng giữ ZIP con, và Kaggle bung cả ZIP con; từng file/member phải khớp SHA-256 trước khi đọc. Đã kiểm tra cú pháp notebook và mô phỏng hai trường hợp bundle nguyên/đã bung: cả hai tải được đúng 2.732 Devign + 2.274 REVEAL prompts. Notebook chưa được chạy trên Kaggle; chưa có test output.

Để chạy: upload `grace_b2_rand_test_seed44_bundle.zip` thành Kaggle Dataset; attach bundle và đúng model Q4_K_M, chọn T4×2 + Internet; mở notebook seed44 và Run All. Khi resume, attach `grace_b2_rand_seed44_test_checkpoint.zip` từ lần Kaggle Output trước.
