# B1 — notebook sinh prompt

Có graph 40/80; không mã/nhãn demo; giữ câu dẫn demo trống như B0.

Mở [notebook](notebooks/01_prepare_b1_prompts.ipynb) và chạy các cell theo thứ tự. Kernel local/WSL, không cần GPU. Bật INSTALL_DEPENDENCIES nếu cần. Default đọc specs/prompt đã hoàn tất từ B2 tại `01_Author_Baseline_Unified/output/local_full/bundles_recovered_joern_final_20261031` và xuất cả bốn dataset/split vào `output/bundles/` của folder này.

Graph Joern và lựa chọn demo CodeT5 được dùng trực tiếp từ specs B2, không parse/encode/retrieve lại. Code dùng chung ở [tier1_prompt_tools](../tier1_prompt_tools/README.md). Notebook kiểm hash nguồn, dựng lại B2 để đối chiếu prompt, rồi mới tạo arm. Không sửa cache B2, không sao chép response B2 và notebook inference B1 được mô tả bên dưới.

Đầu ra ghép cặp với B2 gốc. Các demo không thuộc kho donor mới được thống kê trong manifest/audit; không âm thầm thay demo vì như vậy sẽ phá phép so flip/rep. Muốn chạy nghiên cứu trên kho donor mới, cần bộ B2 tham chiếu mới dùng chung cho các arm.

## Inference Kaggle B1

Mở [notebook inference Kaggle](notebooks/02_kaggle_qwen_q4_b1.ipynb), bật Internet và 2×T4. Add Input chứa `grace_b1_inputs.zip` từ notebook sinh prompt và model Q4_K_M nếu có. Notebook tự tìm input/model/checkpoint, không phụ thuộc username; kiểm SHA-256 model đã khóa. Mặc định chạy Devign/REVEAL validation/test, tối đa 7 giờ tính từ cell inference và chừa 5 phút checkpoint. Tải `grace_b1_checkpoint.zip` và `grace_b1_diagnostics.zip` từ Output; phiên sau gắn checkpoint làm Input để resume. Các kết quả giữ thông tin graph thiếu và không chứa demo.
