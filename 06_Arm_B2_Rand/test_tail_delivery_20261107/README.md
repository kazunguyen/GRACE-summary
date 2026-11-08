# B2-rand test seed 42, 43 và 44 trong một phiên Kaggle

| Seed | Dataset | Prompt trong bundle | Cách chọn |
|---|---|---:|---|
| 42 | REVEAL | 257 | ID chưa có trong checkpoint I-18 |
| 43 | REVEAL | 246 | ID chưa có trong checkpoint I-19 |
| 44 | REVEAL | 374 | Vị trí 1.901–2.274 trong thứ tự bundle gốc, theo mốc giả định 1.900 |

Tổng cộng **877 prompt test**. Mốc seed 44 giả định Devign hoàn tất và REVEAL đã có 1.900 record. Khi có output thực tế, kiểm tra ID trùng hoặc còn thiếu trước khi ghép kết quả.

1. Upload [bundle mới](grace_b2_rand_three_seed_test_tail_inputs.zip) lên Kaggle. Nếu đã gắn bundle ở bản trước, thay bằng ZIP mới vì SHA-256 đã đổi.
2. Gắn bundle và Input GGUF đã pin vào [notebook mới](03_kaggle_qwen_q4_b2_rand_three_seed_test_tail.ipynb). Chọn **T4 ×2**, bật Internet và Run All.
3. Nếu cần resume chính phiên chạy bù này, gắn thêm `grace_b2_rand_three_seed_test_tail_checkpoint.zip` từ Kaggle Output.

Bundle hỗ trợ ZIP nguyên và thư mục Kaggle đã giải nén. Notebook nạp model một lần, chạy ba nhóm trong một phiên và áp dụng runtime lock hiện tại. Ngân sách 9 giờ gồm setup, có 5 phút dự phòng để xuất checkpoint. Record chạy bù giữ provenance riêng vì seed 42/43 chạy trước đó với SHA runtime cũ. Các ngưỡng validation giữ nguyên. [Manifest](delivery_manifest.json).
