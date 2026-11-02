# B2-rand — 3 seed

Mỗi prompt giữ nguyên target và CPG của B2 tham chiếu, thay demo truy hồi bằng một donor ngẫu nhiên lấy từ train kèm nhãn thật. Seed 42, 43, 44; chọn theo `stable_seed` và `DonorPool.random_demo` của diagnostic kit, loại demo B2 tham chiếu. Nếu không chọn được sau 10 lần thì dừng. Ngân sách graph tối đa 40 nút / 80 cạnh và 1.500 token; demo tối đa 1.500 token, tổng 8.192 bao gồm 64 token dự phòng.

Dùng donor đã khử trùng tại `01_Author_Baseline_Unified/output/research_freeze_20261101`. B2 đã chạy với kho truy hồi trước đó: có 5 demo Devign validation và 16 Devign test ngoài kho mới. Đối chiếu này giữ nguyên B2 gốc; khác biệt kho phải được công bố khi diễn giải, không khẳng định B2 dùng cùng kho donor mới. Manifest ghi hash hai nguồn, số demo tham chiếu ngoài kho, seed và phiên bản NumPy; audit ghi donor, nhãn và hash từng mẫu.

1. Mở [notebook sinh prompt](notebooks/01_prepare_b2_rand_prompts.ipynb) trong môi trường local/WSL có numpy và transformers 4.57.1. Chạy lần lượt để tạo 12 bundle và `output/bundles/grace_b2_rand_inputs.zip`; tokenizer tải từ Hugging Face theo revision đã khóa. Kho donor lớn, cần đủ RAM và dung lượng trống.
2. Upload ZIP vào Kaggle Dataset, rồi Add Input bundle B2-rand, model GGUF Q4_K_M và checkpoint `grace_b2_rand_checkpoint.zip`. Import [notebook inference](notebooks/02_kaggle_qwen_q4_b2_rand.ipynb), bật GPU T4 và Internet. Notebook nhận checkpoint ZIP hoặc thư mục đã giải nén, tìm Input không phụ thuộc username và kiểm tra SHA256 model. Không cần gắn bundle donor rerun để tiếp tục I-09.
3. Giới hạn **9 giờ chung cho ba seed** tính từ cell inference, gồm 5 phút dự phòng; cài đặt ở ngoài giới hạn. Một mẫu đang xử lý có thể vượt hạn; giới hạn không phải ngắt cứng thời gian session Kaggle. Nếu hết hạn, tải `grace_b2_rand_checkpoint.zip` trong Output và Add Input cho phiên mới; resume đã bật mặc định. Phiên tiếp theo có ngân sách 9 giờ mới.

Notebook chỉ chạy validation còn thiếu cho cả ba seed, rồi dừng và đóng gói checkpoint. Không tự chọn ngưỡng hoặc chạy test; người dùng chốt ngưỡng riêng sau khi đủ validation. Log `evaluation.json` giữ đánh giá greedy trên validation, không thay thế việc khóa ngưỡng theo protocol.

## Chạy kèm B2 donor rerun 66

Lượt I-09 đã chạy 28 B2 validation và 38 B2 test, khóa ngưỡng B2 và ghép vào phiên B2 donor mới. Notebook resume giữ nguyên output và khóa trong `b2_donor_rerun_66/`, kiểm hash lịch sử rồi bỏ qua 66 mẫu; không cần gắn lại bundle donor.

Kaggle có thể tự giải nén checkpoint; notebook nhận cả ZIP lẫn thư mục, so hash phần I-09 và kiểm tra record còn lại. Nếu có nhiều checkpoint khác nội dung, đặt `CHECKPOINT_INPUT_PATH` tới checkpoint mong muốn.

## Bundle và checkpoint trên Drive

[Google Drive — dữ liệu B2-rand](https://drive.google.com/drive/folders/17VoIiqOO0yArU4_bWYCzkLA2f20rbGzH?usp=sharing) chứa bản bàn giao output theo thông tin người dùng cung cấp. File prompt, bundle và checkpoint được liệt kê cùng SHA-256 trong [manifest](../Runs-management/b2_rand_drive_manifest_20261102.json). Bundle Kaggle có SHA-256 `684167868f69b55c62409eb1c97802a9bda10a8bac613404b527096933ef0014`; checkpoint I-09 có SHA-256 `9b8f1e3c365085a684490928a200b6a4cd065f12dcf0dcf90d5a9f59738d6e92`. Nội dung Drive chưa được tải lại để kiểm tra.
