# B1-full test — runtime acceptance, 08/11/2026

**PASS_LAUNCH_CONTRACT**, đủ **5.006/5.006 fresh records seed 42**, không còn seed bổ sung bắt buộc. Kernel `huuhieu3333/grace-b1-full-budgetfix-20261108`, version 1. Hoàn tất 15:35:51 GMT+7 theo worker status.

| Nhóm nghiệm thu | Kết quả |
|---|---|
| Model/worker/helper/input/contract identities | PASS |
| Sáu package pinned, constructor, CPU threads | PASS |
| Backend source archive/build provenance và log hashes | PASS |
| Hai T4, 49/49 layer offload, context 8.192, batch/ubatch 256 | PASS |
| 5.006 record: ID/label/prompt/model/tokenizer/runtime reference, score và locked prediction | PASS |
| Full census và checkpoint CRC/record equality | PASS |

Nguồn contract là **bản thật đã pin trước launch**: SHA-256 `85d8770839f80260cdc7c27b27b6cce6bf8815675c8593db68fb102589c5cbd6`. Đây là nghiệm thu contract sáu package đã dùng, không khẳng định run đã nạp contract bảy package được cập nhật sau. Pip freeze thật cũng ghi SciPy **1.16.3**; thông tin này được giữ riêng khỏi danh tính contract.

Backend dùng chính sách Kaggle platform build kèm provenance đầy đủ; không yêu cầu binary giống byte giữa các build. Model/compiled-library hashes do verified runner ghi ở remote; audit kiểm source, logs và hash chain, không rehash model lớn trên local hoặc đọc lại loaded GPU memory. Scoring direct full-vocabulary logits không sampling, seed constructor sentinel `4294967295` được tách khỏi prompt seed 42.

Numeric score hợp lệ đủ 5.006. REVEAL có 2 raw greedy response không phải `0/1`, nhưng policy giữ score logits hợp lệ; không loại mẫu hoặc điền score. Ngưỡng test **Devign 0,99 / REVEAL 0,01** khớp frozen validation lock trong input, không tối ưu lại.

| Dataset | N | AUROC | MCC | BA | F1 |
|---|---:|---:|---:|---:|---:|
| Devign | 2.732 | 0,531096 | 0,069566 | 0,527480 | 0,312535 |
| REVEAL | 2.274 | 0,578215 | 0,084902 | 0,569695 | 0,209561 |

[Chi tiết mọi gate và hashes](b1_full_runtime_acceptance.json), [verifier](accept_b1_full_completion.py), [bằng chứng source/deployment](b1_full_runtime_acceptance_evidence/), [artifact gốc đã sao chép](completed_results/b1_full_test_completed_20261108/).

Verifier dùng full download và input bundle giữ local để đối chiếu; bản Git công bố records, manifests và logs/provenance chọn lọc. Full output/checkpoint đã có local; hash/size checkpoint trong JSON. Công việc này không nghiệm thu hồi tố B2 hoặc B3 historical và không thay thế phân tích confirmatory theo protocol.
