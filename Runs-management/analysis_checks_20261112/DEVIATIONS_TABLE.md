# Bảng sai lệch so với đăng ký — dạng ba dòng (cho bản thảo)

- Theo Phụ lục A và mục 7 của *Đánh giá tiến độ 11/11*.
- Mỗi mục ghi ba dòng: ngày, lý do, phân tích bị ảnh hưởng.
- Nhật ký vận hành chi tiết vẫn ở `CHANGES_AFTER_PREREG.md`. Bảng này không thay thế hay xóa nhật ký đó; nó là bảng rút gọn để đưa vào bài.
- Số liệu kiểm chứng ở `Runs-management/analysis_checks_20261112/`.

| # | Sai lệch | Ngày | Lý do | Phân tích bị ảnh hưởng |
|---|---|---|---|---|
| D1 | Ngưỡng B0/B1 đã đăng ký không thỏa quy tắc full-validation. Giá trị hiệu chỉnh: B0 0,98/0,30, B1 0,98/0,63, tính sau khi test đã được xem. | 06–08/11 | Lỗi khi tính ngưỡng trước đăng ký. | Metric theo ngưỡng của B0/B1 không còn chỉ định trước; báo cả hai bộ, bộ hiệu chỉnh ghi là hồi cứu. AUROC/AUPRC và metric tại 0,5 không đổi. ΔMCC(B2 − B0) Devign đổi dấu giữa hai bộ (+0,031 so với −0,033). |
| D2 | B2-flip: 230 mẫu Devign test đã xem nhãn thô trước khi đăng ký. | 03/11 | Lượt I-06 chạy trước đăng ký. | Khai báo trong `exposure_ledger`; không đổi phân tích. |
| D3 | B1-full: renderer được sửa sau khi có test (4.753/5.006 prompt đổi); validation chạy bằng renderer cũ. | 08/11 | Lỗi trình dựng prompt. | Chỉ báo AUROC/AUPRC; MCC/F1 chờ validation bằng renderer mới. Số validation cũ không dùng. Repo còn 6 bản records test renderer cũ, đã liệt kê để loại trừ. |
| D4 | B1-H2: validation trên Colab L4, test trên Kaggle. 3.664/5.006 prompt test không có evidence H2. Ngưỡng ReVeal ghi 0,67 và 0,21 ở hai nơi; records, delivery và lock đều dùng 0,21. | 06–07/11 | Chạy ngoài lộ trình và ngoài cấu hình tham chiếu. | Thăm dò; báo AUROC và phân tầng có/không evidence; không có trong Bảng B. |
| D5 | B2-rand ReVeal seed 42/43 ghép từ hai runtime contract (2.017 + 257; 2.028 + 246 record). Không có ID hay prompt nào được chấm dưới cả hai. | 07/11 | Tiếp nối checkpoint qua hai phiên. | Cặp B2 − B2-rand ReVeal mang giới hạn môi trường; cần chạy lại ≥ 200 ID phần thiểu số dưới runtime tham chiếu nếu được duyệt. |
| D6 | Nhóm B3 không đạt kiểm toán đầu vào. Bản "verified patch-pair" chỉ có **một cặp được duyệt mỗi dataset**, dùng chung cho mọi target. | 08–10/11 | Bản cũ: 3.418/5.005 câu mặc định, 0% cặp cùng nguồn. Bản mới: kho cặp chỉ có một cặp. | H2.3 không có kết luận xác nhận; mọi số B3 là thăm dò; thiết kế lại ở Giai đoạn 2. |
| D7 | B3-swap (I-29/I-30) và B3-flip (I-31) chạy test ngày 11/11, sau quyết định dừng nhóm B3 trong Đánh giá 11/11. | 11/11 | Các phiên đã xếp hàng từ 10/11 vẫn được chạy đến hết; lý do không hủy cần nhóm bổ sung. | Kết quả giữ ở mức thăm dò; không vào Bảng B; không chạy thêm lượt B3 nào. |
| D8 | Bảng tổng hợp 05/11 công bố MCC B2 tại ngưỡng 0,5 và AUROC B2 Devign từ file records trước khi ghép donor rerun (38 prompt test); số raw lỗi B0 1.132 là tổng bốn split. | 05/11 | Tính số ở nhiều nơi, không từ một file records chuẩn. | Không đổi phân tích. Số chuẩn: AUROC B2 Devign 0,5305; MCC 0,0597/0,0645 tại τ*; B0 Devign test 302 raw lỗi. |
| D9 | Ngưỡng bổ sung cho B2-nolabel, B2-labelonly, B2-rand, B1-shuf và SUP-* theo đúng quy tắc đã đăng ký; file ngưỡng đăng ký giữ nguyên. | 06–09/11 | Quy tắc chọn ngưỡng yêu cầu. | Không có. |
| D10 | Họ Holm: giữ 11 cặp đã đăng ký × 2 dataset (22 p-value McNemar), kể cả hai cặp có lượt chạy thăm dò (B2 − B3, B1 − B1-H2). | 11/11 | Bỏ hai cặp sẽ làm Holm bớt chặt, tức là điều chỉnh hồi cứu có lợi. | Hai hàng đó đánh dấu thăm dò, không trình bày trong Bảng B chính. p McNemar không phải p của ΔMCC/ΔAUROC. |
| D11 | Phân tích bổ sung sau đăng ký: CI cho ΔAUPRC; so trực tiếp B2 − B2-nolabel; chiều đổi dự đoán của B2-flip; ppr@0,5; phân tầng B1-H2. | 12/11 | Yêu cầu trong Đánh giá 11/11. | Báo cáo là phân tích bổ sung, ngoài họ Holm đăng ký. |
| D12 | Provenance runtime một phần: records của B0, B1, B2, B2-flip, B2-rep, B2-nolabel, B2-labelonly và B1-H2 không ghi `runtime_contract_sha256`; nhiều phiên thiếu native/build log. | 01–08/11 | Runner trước 07/11 chưa ghi trường này. | Ghi "partial provenance" trong Methods; không dựng lại log hồi tố. |
