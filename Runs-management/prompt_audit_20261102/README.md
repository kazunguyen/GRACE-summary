# Hồ sơ audit prompt/output hậu kiểm — 02/11/2026

[Kết luận](KET_QUA.md) và [trạng thái máy đọc](final_status.json) là điểm vào chính. Đây là audit sau inference, không phải chứng nhận đã preregister hoặc đã khóa ngưỡng trước test.

## Việc đã làm

- Đọc toàn bộ 100.110 dòng prompt/40 tập: 6 arm có artifact, bao gồm phiên lịch sử, phiên donor mới và ba seed B2-rand.
- Adapter evidence gọi prompt_audit thật, giữ demo policy, cờ cắt, độ dài gốc đo bằng tokenizer Qwen đúng revision và graph evidence; B0/B1 chủ động thiếu demo được phân biệt với lỗi demo rỗng.
- Kiểm ID/nhãn metadata/hash, payload target/graph/demo và đúng tác động variant; đếm lại token chính xác, kiểm ngân sách và graph 40/80.
- Đối chiếu 30.691 output đã nhập, tính lại score từ logprob và kiểm identity 14 manifest; 0 score lỗi. Raw response: B0 có 1.132 token Looking, B1 có 3; báo coverage riêng theo protocol, không gán chúng về nhãn 0.
- Xác minh code/nhãn/ID của 39.327 donor frozen và 30.033 lựa chọn B2-rand theo seed.
- Giữ 57 cờ regex thô và ghi riêng phân loại nhầm do biểu thức/chuỗi C/C++ có bằng chứng. Chưa thay thế việc người thật đọc để kiểm ngữ nghĩa/rò rỉ mà regex không phát hiện.
- Chuẩn bị 30 prompt mỗi dataset, tổng 60, không kèm nhãn target hoặc kết quả model; hai chuyên gia (HuuHieu03 và Dung) đã hoàn tất chấm mù độc lập.

## Còn phải xử lý

Có 403 dòng prompt có demo còn dưới 25% gốc (đếm riêng arm/phiên/seed), trong đó 68 dòng thuộc output đã chạy: B2 46, B2-flip 22. Theo quyết định người dùng, giữ tiêu chí, chỉ liệt kê; chưa sửa prompt hoặc inference lại. Xem [danh sách cuối](remediation_final.csv), [output đã chạy](executed_needing_review.csv), [ví dụ](VI_DU_CAN_XU_LY.md).

B2 lịch sử vẫn có 21 target Devign dùng donor bị loại khỏi kho mới; kế hoạch 66 prompt đổi khi chuyển donor vẫn giữ. Không gọi toàn bộ chiến dịch đã dùng kho sạch chỉ vì audit payload đạt.

5 arm Tầng 3 (B3, B3-nodiff, B3-swap, B3-flip, B1-H2) được bảo lưu trạng thái chưa dựng prompt. Khâu chấm tay 60 mẫu và phân xử hòa giải đã hoàn tất. Không thay thời gian test trước khóa, snapshot/tag, ngưỡng hoặc trạng thái OSF.

## Chấm bằng người

Đã hoàn thành đánh giá độc lập theo [rubric](RUBRIC.md) và [bộ prompt](manual_packet.md). Reviewer 1 (HuuHieu03) điền [reviewer_1.csv](reviewer_1.csv); Reviewer 2 (Dung) điền [reviewer_2.csv](reviewer_2.csv) độc lập. Độ đồng thuận Cohen's Kappa đạt κ = 0.8507 (đa lớp) và κ = 0.8485 (nhị phân), vượt ngưỡng nghiệm thu ≥ 0.80 của Phụ lục C. Các điểm bất đồng và trường hợp vi phạm contract 25% được ghi nhận và giải quyết chi tiết tại [Biên bản phân xử](BIEN_BAN_PHAN_XU.md).

## Tái tạo và kiểm tra

Các script nằm ở thư mục cha. Các bước sinh hồ sơ từ chối ghi đè hồ sơ đã có để tránh mất phiếu hoặc bằng chứng; riêng verify_prompt_audit.py có thể tạo lại báo cáo verification kỹ thuật, không sửa phiếu chấm. Muốn audit phiên mới phải chọn thư mục/phiên mới; không xóa hồ sơ này để chạy lại.

1. audit_frozen_donor_scope.py và audit_random_selection.py kiểm nguồn donor/selector.
2. audit_prompt_integrity.py chạy CPU; mặc định nạp tokenizer Qwen từ cache offline đúng revision. --metadata-only chỉ là kiểm tra có giới hạn, không thay bản đếm token thật.
3. finalize_prompt_audit.py giữ cờ thô, phân loại cảnh báo nhầm và tạo kết luận riêng.
4. verify_prompt_audit.py kiểm 106 nguồn hash, snapshot/khóa lịch sử, score và phiếu chấm trống. audit_response_coverage.py tách raw response khỏi score.

Các kiểm thử adapter, phân loại cảnh báo và bộ mẫu: 8 pass. [Verification](verification.json) lưu kiểm tra toàn bộ artifact. [Hash nguồn](source_hashes.json) trỏ đến cache/output local; những file lớn đó không được sao chép vào hồ sơ này. Không inference LLM, không chọn ngưỡng mới, chưa commit/push trong đợt này.
