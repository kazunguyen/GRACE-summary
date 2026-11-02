# B2-flip — donor thống nhất và resume checkpoint I-06

## Sinh prompt

Chạy [01_prepare_b2_flip_prompts.ipynb](notebooks/01_prepare_b2_flip_prompts.ipynb) trên local/WSL. Notebook dùng **bộ B2 tham chiếu của kho donor mới** tại `Runs-management/donor_reconciliation_20261101/new_reference/B2/`. Kho dùng để truy hồi là `research_freeze_20261101`; whitening trên kho mới đã được fit và kiểm toán trong bước đối chiếu B2.

Giữ nguyên code target, graph 40 nút/80 cạnh, code demo đã lấy từ kho mới và scaffold B2; chỉ đảo **nhãn thật của demo mới**. Không gọi LLM, chạy Joern, encode CodeT5 hoặc retrieval lại. Tokenizer Qwen đã pin dùng để đếm chính xác toàn bộ prompt flip.

Bundle mới để upload Kaggle:

`output/bundles_frozen_donor_20261101/grace_b2_flip_frozen_donor_inputs.zip`

Bundle có đủ **10.011 prompt**, trong đó Devign validation đổi 28, Devign test đổi 38, REVEAL không đổi. `previous_prompt_sha256` và `previous_demo_ids` ghi đúng phiên cũ để runtime kiểm tra checkpoint; hash không thuộc phiên cũ hoặc phiên mới sẽ bị từ chối. `output/bundles/` cũ và output I-06 được giữ nguyên.

## Inference và tiếp tục checkpoint

Notebook [02_kaggle_qwen_q4_b2_flip.ipynb](notebooks/02_kaggle_qwen_q4_b2_flip.ipynb) tự tìm Input, không hardcode username. Gắn ba đầu vào:

1. **Bundle frozen_donor mới** ở trên.
2. **`grace_b2_flip_checkpoint.zip` của I-06**, hiện lưu trong `output/kaggle_20261102_quangdung1111_run1/`.
3. Model **Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf** có SHA-256 `f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335`.

`RESUME_FROM_CHECKPOINT=True` mặc định. Nếu gắn nhiều checkpoint cùng tên, đặt `CHECKPOINT_INPUT_PATH` chỉ rõ bản muốn dùng. Bundle cũ trong Input được lọc bằng `prompt_variant` và hash donor; notebook chỉ dùng phiên mới.

Với checkpoint I-06, runtime thực hiện:

1. Xác minh model/tokenizer/backend/seed, ID/nhãn/hash từng record và nguồn prompt. **Giữ 5.202 output còn tương thích**, đưa 33 output cũ đã đổi prompt sang lịch sử.
2. Inference lại **28 Devign validation**; ghép đủ **2.732 validation** và khóa ngưỡng phiên mới tại output mới. REVEAL validation đã đủ nên được khóa từ dữ liệu đầy đủ tương thích của chính arm B2-flip.
3. Inference lại **5 Devign test** đã đổi prompt. Toàn bộ **33 lượt sửa** hoàn thành trước khi chạy phần test còn thiếu.
4. Tiếp tục **4.776 mẫu chưa chạy** bằng prompt mới, trong đó có 33 Devign test đổi demo chưa từng inference. Tổng số lượt LLM bổ sung là **4.809**.

Output mới: `/kaggle/working/grace_b2_flip_frozen_donor_20261101_9h35/`. Có `migration_plan.json`, bản checkpoint I-06 trong `history/original_checkpoint.zip`, record cũ bị thay trong `history/stale_records.jsonl`, `records.jsonl` hiện hành, run manifests và `thresholds.json` riêng. Không ghép response của B2 vào B2-flip.

Hết ngân sách **9 giờ 35 phút** (chừa 5 phút đóng gói), hoặc backend báo lỗi, notebook vẫn đóng gói những record đã lưu thành `grace_b2_flip_checkpoint.zip`. Một mẫu đang chạy có thể vượt thời điểm dừng. Phiên Kaggle sau gắn checkpoint mới này: hàng đợi sửa được giữ, mẫu đã hoàn thành đúng prompt mới được bỏ qua, rồi tiếp tục phần còn thiếu.

## Kiểm tra local

`python test_frozen_resume.py` kiểm tra trên CPU bằng checkpoint I-06 thật và score giả trong thư mục tạm: đủ 10.011 hash prompt mới khớp kiểm toán độc lập; chỉ giữ 5.202 record; đúng thứ tự 33 lượt sửa; dừng giữa chừng và resume không chạy lại phần đã sửa; từ chối model/hash lạ. Không gọi LLM trong các kiểm tra này.

Hai notebook nhúng runtime/helper cần thiết để chạy độc lập trên Kaggle. Sau khi sửa file Python, chạy `python update_frozen_notebooks.py` để cập nhật phần nhúng và xóa output notebook cũ. Dấu vết I-06 và danh sách phải chạy lại nằm tại [Runs-management](../Runs-management/b2_flip_I06_20261102/KET_QUA_I06_B2_FLIP.md).
