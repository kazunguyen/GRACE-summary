# Các điểm cần sửa trước khi nộp hồ sơ OSF

**Phạm vi:** ghi chú rà soát PDF `GRACE_OSF_PREREGISTRATION_20261102.pdf` và gói hồ sơ đi kèm. Đây là checklist chuẩn bị, chưa thay thế quyết định của nhóm nghiên cứu và không có nghĩa hồ sơ đã được gửi lên OSF.

## 1. Trạng thái đăng ký và mốc thời gian

- [ ] Đổi `Registration Date: 2026-10-31` thành trạng thái chính xác. Ngày này không phải ngày đăng ký OSF nếu chưa có hồ sơ/URL và timestamp do OSF cấp.
- [ ] Phân biệt rõ ngày soạn, ngày khóa giao thức nội bộ, ngày tạo Git tag và ngày Submit/Approved trên OSF.
- [ ] Đồng bộ phiên bản giữa PDF (`prereg-v1`), README/gói (`prereg-v2-15arms`) và tên tag. Không dùng tên phiên bản hoặc ngày nội bộ khiến người đọc hiểu rằng hồ sơ đã đăng ký trước khi chạy test.
- [ ] Chỉ điền OSF URL, ngày gửi, DOI hoặc trạng thái duyệt sau khi có bằng chứng thật từ OSF.

## 2. Khai báo lịch sử test và tiếp xúc kết quả

- [ ] Viết lại tuyên bố rằng mọi lựa chọn và ngưỡng đã được khóa trước test. Sổ RUNS và bản ghi analysis lock cho thấy một số test B2 đã chạy trước khi khóa ngưỡng; B1 I-07 cũng có 429 mẫu test trước khi có bằng chứng khóa ngưỡng.
- [ ] Chia rõ các arm/mẫu đã chạy hoặc đã xem với phần việc chưa chạy. Phần đã có phải được mô tả là dữ liệu có sẵn/đã tiếp xúc và phân tích hậu kiểm hoặc thăm dò khi phù hợp.
- [ ] Không backdate, không đổi nhãn lịch sử thành preregistered. Chạy lại chỉ khi có lý do phương pháp cụ thể; giữ output cũ và ghi quan hệ giữa phiên cũ/mới. Chạy lại không biến dữ liệu cũ thành kiểm định được preregister trước.
- [ ] Cập nhật ngày tạo và mô tả của analysis lock: bản ghi 01/11 được lập sau khi inference đã bắt đầu, không phải preregistration hồi tố.

## 3. Định danh model và scoring

- [ ] Thống nhất model chính, quantization và nguồn tải. PDF ghi GGUF `Q4_K_M` nhưng Kaggle model slug có `ud-q4_k_xl`; giải thích rõ đây là slug chứa artifact nào và đối chiếu SHA-256 của file thực chạy.
- [ ] Làm rõ Qwen2.5 trong mục fallback có phải lựa chọn được phép trong protocol hay chỉ là phương án ngoài nghiên cứu. Nếu là fallback, nêu rằng đổi model tạo phiên/arm riêng; không tuyên bố đồng thời đã loại bỏ mọi dấu vết model khác.
- [ ] Đồng bộ định nghĩa score với backend thực tế. Nêu rõ dùng logits/logprobs nào, công thức, và điều kiện score hợp lệ.
- [ ] Sửa câu nói score chỉ invalid khi “cả hai token vắng mặt”: nếu công thức cần cả token 0 và 1 thì thiếu một trong hai cũng không tính được score theo cách đó.
- [ ] Tách `score validity` khỏi `raw response validity`; mô tả đúng policy của từng inference backend và không gộp hai tỷ lệ.

## 4. Dữ liệu, đường dẫn, số lượng và hash

- [ ] Thay các đường dẫn không tồn tại trong repo như `data/raw/...`, `data/manifests/...`, `data/specs/...`, `grace_diag_kit/...` và `00_Reports_and_Docs/...` bằng đường dẫn thực tế hoặc hướng dẫn truy cập nguồn ngoài repo.
- [ ] Cập nhật bảng hash theo đúng manifest/freeze hiện hành; ghi rõ tệp nào không được đóng gói trong ZIP và cách người đọc lấy chúng.
- [ ] Sửa mâu thuẫn donor count ngay trong PDF: bảng dữ liệu ghi Devign 21.691 / REVEAL 17.636; checklist lại ghi 21.711 / 17.620. Freeze manifest hiện hành khớp với cặp số ở bảng.
- [ ] Ghi rõ phiên bản/snapshot dữ liệu, manifest SHA-256, ngày khóa và quy tắc loại trùng; không dùng hash không có tệp/đường dẫn để kiểm chứng.

## 5. Trạng thái audit và ngưỡng

- [ ] Phân biệt kết quả dry-run tự động với chấm prompt bằng người. Báo cáo dry-run hiện ghi 95.095 prompt, 15/15 arm, 0 LLM calls và không có label leak; trạng thái hai reviewer thật vẫn pending. Chỉ gọi phần tự động là hoàn tất cho tới khi có phiếu và biên bản người chấm.
- [ ] Viết rõ phạm vi của checklist `669/669 tests`: đây là test phần mềm hay prompt audit; dẫn đến báo cáo, commit hoặc artifact có thể kiểm tra.
- [ ] Kiểm tra tuyên bố `14/14 thresholds` và danh sách ngưỡng: nêu arm/dataset/seed nào đã có ngưỡng, ngưỡng nào còn phải fit trên validation đúng phiên. Không nói tất cả arm đã khóa trước test nếu bằng chứng không hỗ trợ.
- [ ] Đánh dấu các mục chưa hoàn tất là pending, không tick hoàn thành chỉ vì đã tạo packet hoặc mã nguồn audit.

## 6. Giả thuyết và kế hoạch phân tích

- [ ] Định nghĩa phép tính “labelonly tái tạo >= 80% chênh lệch” ở H2.2, gồm chiều so sánh, metric, mẫu số và xử lý mẫu số bằng 0/âm.
- [ ] Chốt trước endpoint/metric và họ giả thuyết áp dụng Holm; nêu cách xử lý CI/metric suy biến và ngưỡng tối thiểu để coi CI hợp lệ.
- [ ] Chốt cách grouping/fold cho REVEAL và mô tả phần nào đã nghiệm thu, phần nào chỉ là kế hoạch.
- [ ] Kiểm tra ma trận arm và các seed khớp với dry-run, dữ liệu inference, ngưỡng và phạm vi đăng ký hiện tại.

## 7. Trình bày và đóng gói

- [ ] Render lại công thức thay vì để nguyên LaTeX thô như `\\Delta\\text{MCC}` hoặc `\\tau^*` trong PDF.
- [ ] Thống nhất tiêu đề, version, footer và cách gọi “draft / ready for submission”. Tránh footer “Strict Confidentiality & Integrity Lock” nếu trạng thái public/embargo chưa được quyết định.
- [ ] Sau khi chốt nội dung, sinh lại PDF, README, source inventory, attachment SHA-256 và ZIP từ cùng một nguồn; mở lại PDF để kiểm tra toàn bộ trang.
- [ ] Lưu bản cũ riêng, ghi lý do/version của bản mới. Không ghi đè attachment đã gửi OSF nếu sau này có amendment.

## Trước khi Submit

- [ ] Tác giả, cơ quan, người chịu trách nhiệm và quyền sở hữu.
- [ ] Public hay embargo.
- [ ] Cập nhật đầy đủ output cloud, tình trạng inference và mọi kết quả đã xem.
- [ ] Chốt các mục phương pháp pending ở trên hoặc giới hạn đăng ký vào phần đã xác định.
- [ ] Người phụ trách nghiên cứu duyệt PDF/ZIP cuối; sau Submit mới ghi OSF URL và timestamp thật.

## Bằng chứng nên đối chiếu

- `Runs-management/RUNS.md`
- `Runs-management/analysis_lock_20261101/preregistration.md`
- `Runs-management/dry_run_validation_20261102/KET_QUA.md`
- `Runs-management/dry_run_validation_20261102/summary.json`
- `01_Author_Baseline_Unified/output/research_freeze_20261101/freeze_manifest.json`
- `01_Author_Baseline_Unified/diagnostic_kit/configs/backend_manifest.json`
