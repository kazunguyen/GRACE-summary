# Đối chiếu Bước 3 với đề cương — 02/11/2026

Nguồn: PhuongAn2_De_cuong_nghien_cuu_GRACE_hop_nhat.pdf, trang PDF 18–19. Kết luận: **CHƯA HOÀN THÀNH TOÀN BỘ BƯỚC 3**. Audit tự động đã hoàn thành cho artifact đang có; điều đó không thay thế đầy đủ nghiệm thu Bước 3.

| Tiêu chí của Bước 3 | Bằng chứng hiện tại | Kết luận |
|---|---|---|
| Bộ dựng/probe và pytest tests/test_probes.py | 20 test pass, 0 fail trong lượt kiểm tra này | Đạt riêng bộ test probe được PDF chỉ định; không tuyên bố mọi test notebook khác đều xanh |
| Dry-run mọi arm trên validation, mục tiêu đủ 15 arm | Đã audit 6 arm có prompt, gồm các phiên/seed; 9 arm chưa chuẩn bị | Chưa đủ toàn bộ 15 arm |
| Audit p50/p95, cờ cắt code/graph/demo, graph thiếu, rò rỉ nhãn | Có summary/CSV, đối chiếu hash/payload/variant và đếm lại token; không còn cờ nhãn chưa giải quyết sau phân loại có bằng chứng | Đạt phần kiểm tự động trên 40 tập đã có; phát hiện ngữ nghĩa vẫn cần người đọc |
| Demo rỗng ≤1% | Cả 40 tập đều ≤1%; cao nhất 24/2.732 = 0,878% ở B2-rand seed44 Devign validation | Đạt tỷ lệ; không yêu cầu tỷ lệ bằng 0 |
| Hai người đọc 30 prompt mỗi dataset | Đã hoàn thành chấm mù độc lập (Reviewer 1: HuuHieu03, Reviewer 2: Dung); Cohen's Kappa đạt κ = 0.8507; đã lập biên bản phân xử hòa giải tại [BIEN_BAN_PHAN_XU.md](BIEN_BAN_PHAN_XU.md) | Đạt tiêu chuẩn Phụ lục C |
| Mọi prompt được kiểm trước khi gọi LLM | Hồ sơ mới là audit hậu kiểm của các run đã chạy | Không được ghi hồi tố rằng đã audit trước inference |

## Đính chính cách diễn giải 403 cờ demo

Bộ audit định nghĩa demo bị cắt còn dưới 25% độ dài gốc là thiếu nội dung. Đây là định nghĩa ở cấp từng prompt. Tuy nhiên, ngưỡng nghiệm thu tổng hợp của Bước 3 trong PDF là **demo rỗng ≤1%**, không phải 0%.

Vì vậy, 403 dòng bị gắn cờ (đếm riêng arm/phiên/seed; 68 dòng thuộc output đã inference) vẫn được giữ trong danh sách để kiểm tra, nhưng không tự động làm toàn bộ arm trượt Bước 3 hoặc buộc inference lại. Không có tập nào trong 40 tập vượt 1%. Các nhãn needs_remediation và nội dung cần xử lý trong báo cáo audit ban đầu là danh sách cờ từng dòng; khi kết luận nghiệm thu Bước 3 phải đọc cùng giới hạn 1% này.

Quyết định giữ định nghĩa 25% của người dùng vẫn được giữ. Đợt đối chiếu này không sửa prompt, không xóa cờ gốc, không inference lại và không chọn ngưỡng mới.

## Phần còn lại

1. Để nghiệm thu toàn Bước 3 theo nguyên văn đề cương: chuẩn bị và dry-run validation cho 9 arm còn thiếu. Theo phạm vi người dùng đã chốt, chưa mở việc này trong đợt audit hiện tại.
2. Khâu chấm tay 60 mẫu (30 Devign + 30 REVEAL): ĐÃ HOÀN THÀNH. Reviewer 1 (HuuHieu03) và Reviewer 2 (Dung) đã chấm độc lập, đạt hệ số Cohen's Kappa κ = 0.8507 (đa lớp) và κ = 0.8485 (nhị phân), lập [Biên bản phân xử](BIEN_BAN_PHAN_XU.md) thống nhất 100% các trường hợp.
3. Với run tiếp theo, thực hiện và lưu audit đúng phiên trước inference; giữ khai báo hậu kiểm và lịch sử của run cũ.

Cách ghi tiến độ chính xác: **Hoàn thành audit tự động và khâu chấm tay độc lập 2 người; hoàn thành các tiêu chí chất lượng Bước 3 trên các arm đã dựng; bảo lưu cờ ghi nhận 5 arm Tầng 3 bị nghẽn.** Các sai khác contract đã chốt của B0/B1, graph và scoring phải tiếp tục được khai báo; không gắn thêm trạng thái preregistered.

Xem [kết luận audit](KET_QUA.md), [bộ mẫu và rubric](README.md), [đối chiếu máy đọc](step3_assessment.json).
