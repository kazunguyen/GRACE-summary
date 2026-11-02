# B2-rand — 3 seed

Mỗi prompt giữ nguyên target và CPG của B2 tham chiếu, thay demo truy hồi bằng một donor ngẫu nhiên lấy từ train kèm nhãn thật. Seed 42, 43, 44; chọn theo `stable_seed` và `DonorPool.random_demo` của diagnostic kit, loại demo B2 tham chiếu. Nếu không chọn được sau 10 lần thì dừng. Ngân sách graph tối đa 40 nút / 80 cạnh và 1.500 token; demo tối đa 1.500 token, tổng 8.192 bao gồm 64 token dự phòng.

Dùng donor đã khử trùng tại `01_Author_Baseline_Unified/output/research_freeze_20261101`. B2 đã chạy với kho truy hồi trước đó: có 5 demo Devign validation và 16 Devign test ngoài kho mới. Đối chiếu này giữ nguyên B2 gốc; khác biệt kho phải được công bố khi diễn giải, không khẳng định B2 dùng cùng kho donor mới. Manifest ghi hash hai nguồn, số demo tham chiếu ngoài kho, seed và phiên bản NumPy; audit ghi donor, nhãn và hash từng mẫu.

1. Mở [notebook sinh prompt](notebooks/01_prepare_b2_rand_prompts.ipynb) trong môi trường local/WSL có numpy và transformers 4.57.1. Chạy lần lượt để tạo 12 bundle và `output/bundles/grace_b2_rand_inputs.zip`; tokenizer tải từ Hugging Face theo revision đã khóa. Kho donor lớn, cần đủ RAM và dung lượng trống.
2. Upload ZIP vào Kaggle Dataset, đồng thời Add Input `grace_b2_devign_donor_rerun_66_20261102.zip`. Import [notebook inference](notebooks/02_kaggle_qwen_q4_b2_rand.ipynb), Add Input Dataset và model GGUF Q4_K_M, bật GPU T4 và Internet. Notebook tìm Input theo tên, không hardcode username; kiểm tra SHA256 model theo contract.
3. Giới hạn **9 giờ chung cho ba seed** tính từ cell inference, gồm 5 phút dự phòng; cài đặt ở ngoài giới hạn. Một mẫu đang xử lý có thể vượt hạn; giới hạn không phải ngắt cứng thời gian session Kaggle. Nếu hết hạn, tải `grace_b2_rand_checkpoint.zip`, Add Input và bật `RESUME_FROM_CHECKPOINT`; phiên tiếp theo có ngân sách 9 giờ mới.

Notebook chạy validation cả ba seed trước test và khóa ngưỡng MCC theo validation cho từng dataset/seed trước khi chạy test. Log `evaluation.json` giữ đánh giá greedy từ baseline, không phải đánh giá test theo ngưỡng validation; dùng `threshold_lock.json` khi phân tích kết quả theo protocol. Đây là notebook chuẩn bị, chưa chứng nhận inference thực tế.

## Chạy kèm B2 donor rerun 66

Notebook inference kiểm tra bundle `07_Arm_B2_Donor_Rerun_66` rồi ưu tiên 28 validation của B2, ghép 2.704 score còn tương thích và khóa ngưỡng B2 từ đủ 2.732 mẫu trước khi chạy 38 test; sau đó mới chạy B2-rand. Tất cả chia sẻ hạn 9 giờ và checkpoint. Output B2 nằm trong `b2_donor_rerun_66/`, riêng khỏi `seed_*/` của B2-rand. Giữ `thresholds.json`, records và run manifest để ghép kết quả cũ.

Kaggle có thể tự giải nén Dataset donor rerun; notebook chấp nhận ZIP gốc hoặc thư mục đã giải nén và kiểm tra hash từng file.
