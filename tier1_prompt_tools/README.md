# Chuẩn bị prompt các arm còn lại của Tầng 1

- [B1](../03_Arm_B1_Graph_Only/README.md): graph target tối đa 40 nút/80 cạnh, 1.500 token; để trống mã/nhãn demo, giữ câu dẫn demo như B0 đã yêu cầu.
- [B2-flip](../04_Arm_B2_Flip/README.md): cùng B2 target/graph/demo, chỉ đảo nhãn demo.
- [B2-rep](../05_Arm_B2_Rep/README.md): cùng prompt B2 từng ký tự; inference sau này phải gọi mới.

Mỗi folder chỉ có notebook sinh prompt. Không tạo inference notebook hoặc chạy sinh prompt toàn bộ trong đợt này. Các notebook có bốn split Devign/REVEAL validation/test. B2 baseline đã có folder 01; B0 đã có folder 02.

## Tái sử dụng cache

Đọc specs và prompts B2 đã hoàn thành trong `01_Author_Baseline_Unified/output/local_full/bundles_recovered_joern_final_20261031/<dataset>/<split>/`. Specs là cache kết quả Joern và chọn demo qua CodeT5. Do đã có kết quả truy hồi, không load encoder, không tạo vector, không refit whitening và không chạy lại Joern. Các notebook cũng kiểm tra sáu manifest cache CodeT5 và sự tồn tại vectors.npy tại chỗ, không copy cache lớn sang các folder arm.

Không dùng `export_diagnostic_specs.py` vì script đó chạy chọn demo lại. Việc giữ nguyên lựa chọn B2 giúp các phép so flip/rep ghép cặp chính xác với B2 đang chạy. Kiểm hash specs/prompts theo manifest, kiểm ID/label/demo, tái dựng B2 bằng đúng tokenizer revision và trần 40/80 để đối chiếu từng prompt. Sai khác sẽ dừng, không âm thầm đổi graph/demo/renderer. Nhãn target được tách khỏi renderer; dữ liệu audit có nhãn chỉ nằm ngoài prompt.

Mỗi split xuất prompt, audit ghép cặp, preview, manifest và ZIP; một ZIP tổng chứa bốn bundle. Chưa đảm bảo tương thích với notebook inference B0 vì notebook đó chủ động từ chối các arm khác; inference riêng sẽ được tạo sau.

## Phạm vi của bằng chứng

Bộ tham chiếu là B2 lịch sử, có thể có demo không còn trong kho donor `research_freeze_20261101`. Notebook thống kê số này khi có snapshot mới. Không thay demo vì sẽ làm B2-flip/B2-rep khác B2 gốc ngoài tác động cần đo. Artifact được gắn `retrieval_scope: paired_to_existing_B2_not_reselected`; không ghi rằng đã đạt nghiên cứu xác nhận trên kho mới. Khi tạo B2 mới cho snapshot mới, trỏ REFERENCE_ROOT của cả ba notebook tới cùng B2 mới.

B1 giữ câu dẫn demo trống theo quy ước scaffold B0 đã yêu cầu; graph thực vẫn từ cache B2. Nếu target thiếu graph thì giữ header node/edge trống và gắn cờ. Đây là variant `b1_b2_empty_demo_v1`, khác B1 bỏ hẳn khối demo trong PDF. B2-flip/B2-rep giữ đúng cấu trúc B2 gốc.

## Kiểm tra đã thực hiện

Tối ưu sau khi phát hiện notebook B1 chậm: dùng graph đã cắt và token metadata B2 thay cho vòng lặp bỏ từng cạnh/tokenize lại. Vẫn đối chiếu chính xác code/demo và graph với prompt B2, kiểm trần 40/80 và hash nguồn. Cache SHA-256 trong phiên theo path/size/mtime/ctime để tránh đọc lại specs lớn ở nhiều cell. Khi xuất prompt, in tiến độ mỗi 100 mẫu và ETA; split đã hoàn tất có manifest/hash/bundle khớp được dùng lại. Split dở được tạo lại. Kernel đang chạy mã cũ cần Interrupt rồi Restart Kernel/Run All để nạp bản mới; không tự ngắt tiến trình người dùng.

Đo trên 5 mẫu thật Devign validation với tokenizer Qwen đã cache: dựng B1 cũ 2,811 giây, mới 0,019 giây (khoảng 146× cho riêng phần renderer). Cả 5 prompt khớp từng ký tự. Thời gian toàn notebook còn gồm đọc/hash JSONL, token hóa tổng và nén ZIP; không suy ra toàn notebook nhanh 146×. Bộ kiểm tra sau sửa: 10 test đạt, gồm fast/slow parity và tái sử dụng split hoàn tất.

Đối chiếu thêm notebook 04/05: cell preview cũng truyền `reference=reference`; cell thiết lập/xuất prompt nạp lại helper để không dùng module cũ trong kernel. Giữ output và metadata notebook đã có khi sửa source cell. Đã quét 10.011 dòng prompt B2 của bốn split: tất cả có đủ metadata cho đường tối ưu, không dòng nào phải fallback sang dựng graph chậm. Bộ kiểm tra mở rộng hiện có 13 test đạt, gồm cả flip/rep không gọi đường graph fitting cũ.

Sáu test offline đạt, gồm kiểm B1 không lộ demo, flip chỉ đổi nhãn, rep giống B2, xuất bundle từ cache và cú pháp notebook. Đã đối chiếu SHA-256 specs/prompts của bốn cache B2 thật và sáu manifest cache CodeT5. Trong WSL, đã dùng tokenizer Qwen revision được khóa (local cache, không tải mới) kiểm một target thật trên mỗi dataset/split: renderer B2 khớp cache và cả B1/flip/rep đạt kiểm tra ngân sách; rep giữ nguyên prompt. Chưa chạy sinh prompt toàn bộ hoặc inference.
