# B2-rep — notebook sinh prompt

Giữ prompt B2 giống từng ký tự, gồm nhãn demo. Khi inference phải gọi model mới, không dùng response cache B2.

Mở [notebook](notebooks/01_prepare_b2_rep_prompts.ipynb) và chạy các cell theo thứ tự. Kernel local/WSL, không cần GPU. Bật INSTALL_DEPENDENCIES nếu cần. Default đọc specs/prompt đã hoàn tất từ B2 tại `01_Author_Baseline_Unified/output/local_full/bundles_recovered_joern_final_20261031` và xuất cả bốn dataset/split vào `output/bundles/` của folder này.

Graph Joern và lựa chọn demo CodeT5 được dùng trực tiếp từ specs B2, không parse/encode/retrieve lại. Code dùng chung ở [tier1_prompt_tools](../tier1_prompt_tools/README.md). Notebook kiểm hash nguồn, dựng lại B2 để đối chiếu prompt, rồi mới tạo arm. Không sửa cache B2, không sao chép response B2 và chưa có notebook inference cho arm này.

Đầu ra ghép cặp với B2 gốc. Các demo không thuộc kho donor mới được thống kê trong manifest/audit; không âm thầm thay demo vì như vậy sẽ phá phép so flip/rep. Muốn chạy nghiên cứu trên kho donor mới, cần bộ B2 tham chiếu mới dùng chung cho các arm.
