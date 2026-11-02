---
id: "b2-rand-step34-20261102"
title: "Hậu kiểm B2-rand và chuẩn bị hồ sơ bước 3–4 trước khi tiếp tục"
author: "Codex (trợ lý AI)"
author_type: "AI assistant"
requested_by: "Người dùng trong chat"
recorded_at: "2026-11-02T23:05:09+07:00"
timezone: "Asia/Bangkok"
work_date: "2026-11-02"
record_type: "retrospective_worklog"
status: "automatic_checks_complete_human_review_and_registration_pending"
overall_step3_status: "incomplete"
overall_step4_status: "draft_pending_researcher_decisions_and_git_seal"
---

# Hậu kiểm B2-rand và chuẩn bị hồ sơ bước 3–4 trước khi tiếp tục

Ghi lại công việc đã thực hiện cho B2-rand sau lượt Kaggle I-09. Thời điểm trên là lúc lập worklog, không phải thời điểm inference, hoàn tất đánh giá bằng người hay đăng ký. Người dùng chọn ưu tiên B2-rand, giữ các quyết định nghiên cứu còn mơ hồ ở trạng thái chờ duyệt và không thực hiện OSF trong đợt này.

## Bước 3 — việc đã làm

- Đối chiếu hash 12 tập prompt trong bundle B2-rand với các tập đã qua audit tự động; xác minh identity, hash prompt và model của 4.798 record validation seed 42 trong checkpoint. Không có record B2-rand test trong checkpoint đã nhập. Không suy ra trạng thái những phiên Kaggle khác.
- Đối chiếu 30.033 lựa chọn donor của ba seed với demo B2 tham chiếu sau chuyển donor: không có demo ngẫu nhiên nào trùng demo tham chiếu tương ứng. Kết quả kiểm selector ngẫu nhiên theo seed được giữ trong audit riêng.
- Kiểm lại bằng chứng audit 100.110 dòng/40 tập, gồm 12 tập B2-rand, và dry-run validation 70.070 dòng/28 tập. Chạy lại 20 test probe, 4 test research contract và 16 test trạng thái/audit/dry-run; các kiểm tra này đều đạt.
- Giữ cờ demo dưới 25%, graph thiếu và kết quả phân loại cảnh báo; kiểm tra tự động không thay thế đánh giá ngữ nghĩa của người thật. Audit prompt hoàn thành sau khi inference B2-rand đã bắt đầu, không ghi hồi tố là đã kiểm toàn bộ trước inference.

### Bằng chứng bước 3

[Bằng chứng checkpoint và hash](../Runs-management/step34_b2_rand_20261102/checkpoint_verification.json), [script kiểm checkpoint](../Runs-management/step34_b2_rand_20261102/verify_checkpoint.py), [audit prompt](../Runs-management/prompt_audit_20261102/KET_QUA.md), [kiểm selector](../Runs-management/prompt_audit_20261102/random_selection.json), [dry-run validation](../Runs-management/dry_run_validation_20261102/KET_QUA.md).

Đã chuẩn bị sẵn [packet 60 prompt](../Runs-management/prompt_audit_20261102/manual_packet.md), [rubric](../Runs-management/prompt_audit_20261102/RUBRIC.md) và hai phiếu [reviewer 1](../Runs-management/prompt_audit_20261102/reviewer_1.csv), [reviewer 2](../Runs-management/prompt_audit_20261102/reviewer_2.csv). Mỗi người cần đọc độc lập 30 prompt mỗi dataset, điền phiếu và lưu biên bản xử lý bất đồng. Hai phiếu hiện còn trống; [review_status.py](../Runs-management/step34_b2_rand_20261102/review_status.py) chỉ kiểm hình thức, không thay thế việc chấm của người thật.

## Bước 4 — việc đã làm

- Soạn [bản nháp kế hoạch B2-rand](../Runs-management/step34_b2_rand_20261102/preregistration_draft.md) và [protocol nháp](../Runs-management/step34_b2_rand_20261102/protocol_draft.yaml), ghi cấu hình, ba seed, hash input/checkpoint, giới hạn 9 giờ và lịch sử inference thực tế.
- Ghi rõ benchmark và một số kết quả test của arm trước đã được tiếp xúc; B2 donor rerun trong I-09 đã chạy cả validation và test. Không khẳng định zero test exposure, không backdate và không coi bản ghi local trước đó là preregistration hồi tố.
- Giữ nguyên output, checkpoint, khóa ngưỡng và snapshot lịch sử; không chạy inference, không fit tau mới, không gửi OSF. Cập nhật [sổ chạy](../Runs-management/RUNS.md), [tiến độ](../Runs-management/TIEN_DO_PHUONG_AN_2.md) và [hồ sơ bước 3–4](../Runs-management/step34_b2_rand_20261102/README.md).

## Phần còn lại và giới hạn

- Hai reviewer thật chưa hoàn thành chấm 60 prompt; chưa có biên bản phân xử. Bước 3 cho B2-rand chưa nghiệm thu bằng người.
- Bước 3 toàn nghiên cứu còn năm arm H2/B3 thiếu đầu vào; dry-run mười arm không chứng nhận đủ 15 arm.
- Công thức H2.2 cho tiêu chí 80%, họ Holm/CI suy biến và cách xử lý demo dưới 25% chờ chủ nhiệm; không tự đưa giả định thành quyết định.
- Bước 4 là **draft local chưa được chủ nhiệm duyệt hoặc chốt, chưa commit/tag**. OSF được loại khỏi phạm vi yêu cầu hiện tại; không có ngày hoặc URL đăng ký mới.
- Phần đã kiểm là checkpoint local I-09; chưa đủ căn cứ khẳng định mọi phiên Kaggle khác hay ai đã xem kết quả nào. Tiếp tục giữ checkpoint và chốt các điều kiện còn thiếu trước khi chạy test B2-rand.
