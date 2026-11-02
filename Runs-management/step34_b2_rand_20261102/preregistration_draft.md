# Hồ sơ chuẩn bị bước 3–4 cho B2-rand — chờ duyệt

Trạng thái: DỰ THẢO LOCAL, chưa ký duyệt, chưa commit/tag, chưa gửi OSF. Không phải đăng ký trước hồi tố. Mục đích: cố định bằng chứng đã có và các việc cần chốt trước khi tiếp tục I-09.

## Lịch sử thực tế

- Benchmark và một số kết quả B2/B0 test đã được tiếp xúc trước đây; không khẳng định zero test exposure. B2 donor rerun I-09 đã chạy 28 validation và 38 test.
- B2-rand I-09: validation seed 42 Devign 2.732, REVEAL 2.066; chưa thấy test B2-rand hoặc seed 43/44 trong checkpoint đã nhập. Không suy ra mọi phiên cloud khác hoặc ai đã xem kết quả nào.
- Validation B2-rand đã bắt đầu 2026-11-02 00:17 UTC; audit prompt hoàn thành 08:56 UTC cùng ngày, khi lượt inference đã bắt đầu. Không tuyên bố audit toàn bộ đã thực hiện trước inference.
- Analysis lock 01/11 là tài liệu sau khi đã bắt đầu inference. Hồ sơ này không hồi tố timestamp hay thay thế hồ sơ đó.

## Dữ liệu và identity

- Donor train frozen Devign 21.691, REVEAL 17.636; freeze manifest SHA-256 e1d3c6b17c3a0b5c1e05203794d48a33825e0ea00a55deaaef565af25efe0448.
- Qwen3-Coder-30B-A3B-Instruct GGUF Q4_K_M, model SHA-256 f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335; tokenizer revision b2cff646eb4bb1d68355c01b18ae02e7cf42d120; llama-cpp-python 0.3.16.
- Context 8.192, dự trữ 64, target 3.000 token, demo và graph mỗi phần tối đa 1.500; graph 40 nút/80 cạnh. Score từ logits gốc; seed donor 42, 43, 44.
- Input ZIP B2-rand SHA-256: 684167868f69b55c62409eb1c97802a9bda10a8bac613404b527096933ef0014; checkpoint I-09 SHA-256: 9b8f1e3c365085a684490928a200b6a4cd065f12dcf0dcf90d5a9f59738d6e92. Hash từng tập prompt, checkpoint record và nguồn B2 tham chiếu ở checkpoint_verification.json.
- Random demo giữ nhãn thật, khác demo B2; selector/seed đã audit, 30.033/30.033 lựa chọn khác demo B2 theo tham chiếu donor mới. Không lấy kết quả test để chọn donor.

## Bước 3: audit và giới hạn

Audit tự động 12 tập B2-rand trong ZIP khớp hash với audit 100.110 dòng/40 tập; 30.033 lựa chọn selector khớp, 0 cờ rò rỉ chưa giải quyết theo quy tắc tự động. 4.798 record validation khớp ID/label/prompt/model và checkpoint; không tìm thấy B2-rand test trong checkpoint đã nhập. Audit là kiểm tra kỹ thuật, không chứng minh không có rò rỉ ngữ nghĩa.

Giữ cờ demo dưới 25%, cờ graph thiếu, audit source và kết quả phân loại; mỗi tập phải được báo riêng theo ngưỡng Bước 3, không sửa input đã chạy để đạt chỉ tiêu. Tham chiếu: ../prompt_audit_20261102/KET_QUA.md, ../dry_run_validation_20261102/KET_QUA.md. Dry-run 10/15 arm; 5 arm H2/B3 còn thiếu input.

Hai người thật cần đọc độc lập 30 prompt mỗi dataset, ghi reviewer_1.csv và reviewer_2.csv, đối chiếu bất đồng, lập biên bản và kết luận; packet, mẫu và rubric ở ../prompt_audit_20261102/. Không dùng đánh giá AI thay cho người.

## Kế hoạch tiếp tục sau duyệt

Tiếp tục từ checkpoint theo identity và hash, không chạy lại ID đã hoàn tất; validation cả ba seed trước test. Khóa ngưỡng theo đủ validation, riêng dataset/arm/seed, theo protocol validation_mcc_grid_v1. Không chọn ngưỡng từ test. Giữ status/thời gian và không gọi resume là run độc lập.

Ngân sách 9 giờ/phiên tính từ cell inference, 5 phút dự phòng đóng gói; timeout chỉ dừng bắt đầu mẫu mới, không bảo đảm ngắt cứng. Có thể cần nhiều phiên, bảo toàn checkpoint gốc.

## Quyết định chưa chốt — không tự thay bằng giả định

1. H2.2 label-only 80%: metric, chiều, mẫu số bằng 0/âm.
2. Định nghĩa họ kiểm định Holm, các endpoint và quy tắc CI suy biến.
3. Chính sách xử lý demo bị cắt dưới 25%: giữ cờ/loại/sửa và tác động ghép cặp.
4. Xác nhận ai đã xem validation/test, trạng thái các phiên Kaggle khác, bằng chứng người chấm, tác giả và người chịu trách nhiệm.
5. Hoàn tất 5 arm H2/B3 còn thiếu input trước khi tuyên bố Bước 3 hoàn thành cho toàn bộ 15 arm.

Không chốt kết quả hay khẳng định xác nhận cho so sánh có B2 đã tiếp xúc test. Trạng thái Bước 4 theo đề cương còn thiếu phần duyệt/chốt và commit/tag; OSF nằm ngoài phạm vi yêu cầu hiện tại.
