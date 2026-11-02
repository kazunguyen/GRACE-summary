# B2-flip — chuyển donor và tiếp tục I-06, cập nhật 02/11/2026

Đã sửa hai notebook của `04_Arm_B2_Flip` và sinh sẵn bundle mới đầy đủ. Đây là chuẩn bị code/input; **chưa chạy inference GPU, chưa phát sinh lượt GPU B2-flip phiên donor mới**.

## Artifact dùng trên Kaggle

1. Notebook đã sửa: [02_kaggle_qwen_q4_b2_flip.ipynb](../04_Arm_B2_Flip/notebooks/02_kaggle_qwen_q4_b2_flip.ipynb).
2. Bundle mới: [grace_b2_flip_frozen_donor_inputs.zip](../04_Arm_B2_Flip/output/bundles_frozen_donor_20261101/grace_b2_flip_frozen_donor_inputs.zip).
3. Checkpoint I-06: [grace_b2_flip_checkpoint.zip](../04_Arm_B2_Flip/output/kaggle_20261102_quangdung1111_run1/grace_b2_flip_checkpoint.zip).
4. Model GGUF Q4_K_M đúng SHA-256 `f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335`.

Gắn bundle mới, checkpoint và model vào Kaggle Input; notebook mặc định `RESUME_FROM_CHECKPOINT=True`, tự tìm đường dẫn và không phụ thuộc username. Nếu nhiều checkpoint cùng tên thì chỉ định `CHECKPOINT_INPUT_PATH`. Phiên Kaggle tiếp theo dùng checkpoint mới xuất ra để tiếp tục cùng cơ chế.

Muốn tái sinh input, chạy [01_prepare_b2_flip_prompts.ipynb](../04_Arm_B2_Flip/notebooks/01_prepare_b2_flip_prompts.ipynb). Notebook lấy demo từ bộ **B2 đã truy hồi bằng kho donor thống nhất**, đảo nhãn demo mới, giữ nguyên code target/CPG/scaffold và đếm token bằng tokenizer đã pin. Không rerun Joern/CodeT5/retrieval.

## Thứ tự chạy với I-06

| Bước | Số mẫu / hành động |
|---|---|
| Chuyển checkpoint | Giữ 5.202 output còn khớp hash/runtime; tách 33 output cũ đã đổi prompt vào lịch sử. |
| Ưu tiên 1 | Inference lại 28 Devign validation; ghép với 2.704 score B2-flip validation còn dùng được để khóa ngưỡng phiên mới từ đủ 2.732 mẫu. |
| Ưu tiên 2 | Inference lại 5 Devign test sau khi kiểm tra khóa ngưỡng mới. |
| Tiếp tục | Inference 4.776 mẫu chưa chạy bằng prompt mới; 33 Devign test đổi demo nhưng chưa inference nằm trong nhóm này. |
| Tổng LLM bổ sung | **4.809 = 33 lượt sửa + 4.776 lượt còn thiếu**. |

REVEAL validation đã đủ và prompt không đổi: khóa ngưỡng mới từ score B2-flip của đủ 2.273 mẫu; không lấy ngưỡng hoặc response B2 thay cho B2-flip. Mỗi test đều được kiểm tra khóa của đúng dataset, arm, phiên validation và runtime.

Nếu hết giờ giữa hàng đợi 33 mẫu, checkpoint giữ `migration_plan.json` và record mới đã fsync. Lượt sau chỉ sửa phần chưa hoàn tất rồi tiếp tục phần thiếu. Model/tokenizer/backend/seed hoặc hash ngoài hai phiên đã biết bị từ chối. Bundle cũ có thể còn gắn trong Input nhưng không được chọn làm input mới.

## Phiên và lịch sử

- Variant: `b2_flip_frozen_donor_v1`.
- Donor: `research_freeze_20261101`; snapshot SHA-256 `e1d3c6b17c3a0b5c1e05203794d48a33825e0ea00a55deaaef565af25efe0448`.
- Bundle đầy đủ: **10.011** prompt; thay đổi 28 Devign validation và 38 Devign test; REVEAL 0.
- Output mới: `/kaggle/working/grace_b2_flip_frozen_donor_20261101_9h35/`.
- Ngưỡng mới: `OUT_ROOT/thresholds.json`, tách khỏi khóa lịch sử local.
- Bản gốc: `history/original_checkpoint.zip`; record cũ bị thay: `history/stale_records.jsonl`.
- Hết giờ/lỗi backend: notebook đóng gói checkpoint mới thành `grace_b2_flip_checkpoint.zip`. Ngân sách vẫn 9 giờ 35 phút, dự phòng 5 phút; mẫu đang chạy có thể vượt mốc dừng tạo record.

## Kiểm tra đã thực hiện

Đã chạy 6 kiểm thử CPU bằng `04_Arm_B2_Flip/test_frozen_resume.py`: đối chiếu toàn bộ hash prompt mới với kiểm toán độc lập; chuyển checkpoint I-06 và đúng thứ tự 33 mẫu; timeout/resume qua checkpoint mới; giữ bản gốc không thay đổi; không gọi lại record đã sửa; khóa validation đầy đủ trước test; hoàn tất/evaluate một fixture tạm; từ chối model/hash lạ; kiểm tra cấu trúc/cú pháp notebook và phần helper nhúng; tự tìm bundle mới khi Input có cả bundle cũ và tên account khác.

Score giả trong kiểm thử chỉ nằm trong thư mục tạm, được dọn sau test. Đây là kiểm thử luồng CPU, **chưa phải xác minh backend GPU trên Kaggle**. Bundle đã được sinh bằng tokenizer thật đã pin và 10.011 hash khớp kết quả kiểm toán trước đó.

Chi tiết code và cách dùng: [README B2-flip](../04_Arm_B2_Flip/README.md). Kết quả I-06 giữ nguyên tại [báo cáo nhập output](b2_flip_I06_20261102/KET_QUA_I06_B2_FLIP.md).
