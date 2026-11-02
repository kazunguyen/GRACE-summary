# Kết quả chốt ngưỡng validation — Tầng 1

<!-- current-status:start -->
## Trạng thái hiện tại — đối chiếu artifact local

Nguồn: [current_status.json](current_status.json), kiểm tra UTC 2026-11-02T03:39:30.129091+00:00.
Snapshot kiểm toán/ngưỡng ngày 01/11 được giữ lịch sử; bảng này cập nhật tiến độ, không tạo khóa mới.

| Arm | Devign val | Devign test | REVEAL val | REVEAL test | Tổng |
|---|---:|---:|---:|---:|---:|
| B0 | 2732/2732 | 2732/2732 | 2273/2273 | 2274/2274 | 10011/10011 |
| B1 | 2732/2732 | 429/2732 | 2273/2273 | 0/2274 | 5434/10011 |
| B2 | 2732/2732 | 2732/2732 | 2273/2273 | 2274/2274 | 10011/10011 |
| B2-flip | 2732/2732 | 230/2732 | 2273/2273 | 0/2274 | 5235/10011 |
| B2-rep | 0/2732 | 0/2732 | 0/2273 | 0/2274 | 0/10011 |
| B2-rand | Chưa có output | Chưa có output | Chưa có output | Chưa có output | 0/30033 |

Validation đủ nhưng chưa có khóa local: B1/devign, B1/reveal, B2-flip/devign, B2-flip/reveal.

Source notebook (kiểm tra tĩnh): B0: có lời gọi khóa trước test; B1: chưa có lời gọi khóa trước test; B2: chưa có lời gọi khóa trước test; B2-flip: có lời gọi khóa trước test; B2-rand: có lời gọi khóa trước test. Không chứng minh thứ tự khóa của các run lịch sử.

Bằng chứng lịch sử [B1 I-07](b1_I07_20261102.json): 5.434 record, 0 invalid score, 3 invalid raw response; [B2-flip I-06](b2_flip_I06_20261102/KET_QUA_I06_B2_FLIP.md): 5.235 record, 0 invalid. Flip Devign donor mới cần sửa 28 validation trước khóa; xem [resume](B2_FLIP_DONOR_MOI_RESUME.md).

B2 Devign donor mới cần 66 lượt; B2-flip cần 4.809 lượt bổ sung. Chưa có output GPU phiên donor mới. B2-rand đã có 12 bundle và notebook chạy kèm B2 rerun-66; chưa có output inference.

Watcher chưa được xác minh đang chạy; không tự khởi động. Các lỗi nghiệm thu prompt/protocol/OSF và lịch sử test trước khóa vẫn giữ nguyên.
<!-- current-status:end -->

<!-- donor-rerun-risk-note -->
**Phạm vi donor:** ngưỡng hiện tại gắn với bộ validation/prompt/model đã dùng. Chỉ tạo thêm kho donor mới không làm mất hiệu lực các khóa này. Nếu validation đổi khi thống nhất donor thì tạo khóa phiên mới, không ghi đè khóa cũ. Theo dõi arm có nguy cơ chạy lại tại [NGUY_CO_CHAY_LAI_DO_DONOR.md](NGUY_CO_CHAY_LAI_DO_DONOR.md).
<!-- /donor-rerun-risk-note -->

Cập nhật ngày 01/11/2026. Nguồn khóa máy đọc được: [thresholds.json](thresholds.json); trạng thái các arm chưa đủ dữ liệu: [threshold_lock_status.json](threshold_lock_status.json). Các khóa cũ được giữ nguyên; B2 REVEAL đã đủ 2.273 validation và được watcher khóa ở tau=0,12. Đã chạy lại kiểm tra ID/label/prompt/model/seed và đối chiếu độc lập bằng sklearn, không dùng test records/metrics để chọn tau.

| Arm | Dataset | Validation đủ | tau khóa | MCC validation tại tau | MCC validation tại 0,5 |
|---|---|---:|---:|---:|---:|
| B0 | devign | 2,732 | 0.98 | 0.076010 | 0.033945 |
| B0 | reveal | 2,273 | 0.30 | 0.080120 | 0.068718 |
| B2 | devign | 2,732 | 0.70 | 0.053226 | 0.031745 |
| B2 | reveal | 2,273 | 0.12 | 0.082299 | 0.045980 |

Đủ score validation không đồng nghĩa đã khóa ngưỡng. Trạng thái từng arm nằm ở bảng đầu báo cáo; khóa đã lưu đọc từ thresholds.json. Không suy ra ngưỡng arm khác từ B2; mỗi arm/dataset/phiên prompt có khóa riêng.

## Chốt ngưỡng là gì?

LLM đã cho score s = p(1)/(p(0)+p(1)) từ logits gốc của hai token nhãn đầu ra. Ngưỡng tau là mốc đổi score thành nhãn: s >= tau → 1 (vulnerable); s < tau → 0 (non-vulnerable). Đây là bước quyết định nhãn từ score đã có, không huấn luyện lại model, không sửa prompt hoặc token raw, không cần inference lại.

Ví dụ với B2 REVEAL tau=0,12: s=0,20 cho nhãn 1, s=0,08 cho nhãn 0. Với ngưỡng 0,5, s=0,20 trước đó cho nhãn 0. Số 0,12 là điểm vận hành được chọn từ validation, không có nghĩa mẫu có xác suất lỗ hổng thực tế 12%; score hai token chưa được chứng minh là xác suất đã hiệu chuẩn.

## Tôi đã chọn thế nào?

1. Đòi đủ toàn bộ validation ID cho đúng arm/dataset, không fit trên checkpoint còn dở; khớp label, prompt hash, model hash và seed. Gộp checkpoint trùng bằng ID, không đếm hai lần; xung đột score thì từ chối khóa.
2. Với từng ngưỡng trong 0,01; 0,02; ...; 0,99, chuyển score validation thành nhãn bằng s >= tau rồi tính MCC so với nhãn thật validation. Chỉ dùng score valid hữu hạn; ghi coverage/invalid.
3. Chọn MCC lớn nhất. Nếu hòa trong 1e-9, chọn tau gần 0,5 nhất; nếu vẫn hòa, chọn ngưỡng nhỏ hơn. Quy tắc này đã có trước trong bản ghi analysis-lock, không chọn bằng kết quả test.
4. Lưu tau, toàn bộ grid MCC, số mẫu, thời điểm khóa, quy tắc và hash bằng chứng vào thresholds.json. Ngưỡng đã khóa không được âm thầm đổi sau khi nhìn test.

MCC trong bảng là chất lượng trên validation dùng để chọn tau, không phải kết quả test cuối. Thay ngưỡng có thể đổi precision/recall/MCC/F1 nhưng không thay score hoặc thứ hạng, nên bản thân việc đổi tau không cải thiện AUROC/AUPRC. Cần tiếp tục báo riêng raw greedy, ngưỡng 0,5 và tau validation.

## Nguồn trực tiếp trong PDF Phương án 2

PDF: [PhuongAn2_De_cuong_nghien_cuu_GRACE_hop_nhat.pdf](../../REPORT_TO_TEACHER/20261029/PhuongAn2_De_cuong_nghien_cuu_GRACE_hop_nhat.pdf). Số trang dưới đây theo số trang PDF (1–40), đã kiểm trực tiếp nội dung trang.

- **Trang 15, Mục 6.5 — Chỉ số:** bảng quy định chỉ số có ngưỡng tính ở hai mức, trích: “Tính ở hai ngưỡng: s ≥ 0,5 (câu trả lời của model) và τ* tối ưu MCC trên validation”. Đây là căn cứ cho mục tiêu tối đa MCC trên validation và việc vẫn phải báo kết quả ngưỡng 0,5.
- **Trang 16, Mục 6.7 — Đăng ký trước và kiểm soát tiếp xúc test:** trích: “Ngưỡng τ* và mọi lựa chọn cấu hình chốt trên validation.” Đây là căn cứ không dùng test để chọn tau và không chọn lại sau khi xem kết quả test.
- **Trang 20, Bước 5 — Chạy ma trận cấu hình:** mục tiêu ghi: “Validation trước để chọn τ* cho từng arm”; phần việc làm yêu cầu không chạy test của arm trước khi tau của arm được ghi trong thresholds.json. Đây là căn cứ có khóa riêng và lưu file trước test.
- **Trang 38–39, Phụ lục B.3, hàm pick_threshold:** `grid = np.linspace(0.01, 0.99, 99)` và chọn max theo MCC, rồi ưu tiên gần 0,5. Script triển khai cùng grid/mục tiêu; xử lý MCC không xác định tường minh bằng None, tránh lỗi truthiness của đoạn rút gọn `mcc(...) or -2` khi MCC bằng 0.

## Quan hệ với phiên inference đã bắt đầu

Chọn tau chỉ cần CPU và validation, nên làm độc lập với inference GPU. Các score test đã sinh có thể được chấm lại offline bằng tau cố định, không cần gọi LLM lại. Tuy nhiên, nếu test đã chạy trước thời điểm khóa thì thứ tự đó không trở thành đúng yêu cầu đăng ký trước của PDF một cách hồi tố; phải giữ khai báo thời điểm thật. Notebook B0 hiện có helper tự khóa và kiểm tra trước test; notebook B2 hiện tại chưa có các lời gọi này. Helper B2 riêng đã có nhưng chưa được notebook nhúng. Phiên cloud đã nạp mã cũ không tự nhận thay đổi từ file local.
