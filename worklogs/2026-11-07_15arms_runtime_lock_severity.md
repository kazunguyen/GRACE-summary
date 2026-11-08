# Đánh giá sai khác runtime lock cho 15 arm — 07/11/2026

Phạm vi đối chiếu là inference Qwen Q4 trên Kaggle theo configs/inference_runtime_lock.json, không gồm notebook tạo prompt, Colab/Vast hay prototype API cũ. Dấu * nghĩa là giá trị thực lấy từ log/metadata lần chạy đã có, vì notebook không ghim hoặc không đủ pin cứng giá trị đó. Giá trị có * chỉ xác nhận phiên tương ứng.

Đây là đối chiếu notebook và evidence hiện có trong repository cùng ZIP/log Hiếu đã nhập, không phải chứng nhận lại toàn bộ lần inference lịch sử. Notebook có bản bàn giao mới nhưng chưa chạy được ghi riêng để tránh nhầm cấu hình dự kiến với provenance đã quan sát.

| Arm | Notebook và trạng thái | Khác biệt liên quan lock | Đánh giá |
|---|---|---|---|
| B0 | Kaggle runner; inference đã có | *Log: sáu package khớp lock. Source cũ có seed 42, thiếu pin NumPy/hub/tokenizers. | Seed: thấp với scoring hiện hành. Package cũ đã khớp theo log, nhưng pin source chưa cứng. |
| B1 | Kaggle runner và I08; inference đã có | *Log I08: package khớp lock. Source cũ có seed 42, thiếu pin NumPy/hub/tokenizers. | Seed: thấp với scoring hiện hành. Package cũ khớp theo log, pin source chưa cứng. |
| B1-full | Kaggle validation đã chạy; notebook runtime-locked mới trong ZIP đã push, chưa chạy | *Log cũ khớp sáu package. Bản cũ không đọc runtime lock. Bản mới nhúng lock và dùng cấu hình theo lock. | Lần cũ có thiếu gate/provenance. Bản mới khớp source, cần log chạy để xác nhận. |
| B1-H2 | Kaggle validation/test đã chạy; Colab L4 validation/test cũng có run | *Log Kaggle xác nhận package và 8192/256/256. Source Kaggle cố định tensor_split=[1,1], lock yêu cầu None và tự chia layer theo VRAM. Colab L4 ngoài profile lock. | Khác cấu hình phân phối layer và provenance. Không có bằng chứng hiện tại rằng riêng thay đổi split làm logits lệch đáng kể trên 2×T4. Colab L4 là khác profile và cần tách khi so sánh. |
| B1-shuf | Validation seed 43/44 có log; seed 44 dở dang. Notebook runtime-locked mới đã push, chưa chạy | *Log seed 43/44 khớp package. Notebook source cũ thiếu pin ba package. Metadata cũ và log phiên mới khác Python patch; log phiên 05/11 trực tiếp ghi 3.13.16. Thiếu log seed 42 và checkpoint resume cũ. | Pin source/provenance cũ chưa đủ; log resume thiếu nên một phần chưa xác minh. Bản mới chờ run theo lock. |
| B2 | Kaggle validation/test đã chạy | *Log: sáu package và cấu hình scoring/batch đã audit khớp. Notebook cũ thiếu pin trực tiếp NumPy/hub/tokenizers. | Không thấy package sai ở run có log. Khả năng tái lập phiên mới chưa được đảm bảo chỉ bằng source cũ. |
| B2-rand | Validation cũ đã chạy; validation notebook hiện tại đã tích hợp lock nhưng chưa chạy lại; hai test notebook mới đã tích hợp lock, chưa chạy | *Log validation cũ: sáu package khớp. Notebook mới nhúng lock, xác minh package và source archive. | Bản cũ thiếu enforcement. Bản mới khớp lock theo source, chờ log thực thi. |
| B2-nolabel | Kaggle validation đã chạy; notebook runtime-locked mới đã push, chưa chạy | *Log cũ khớp sáu package; source cũ thiếu pin ba package và enforcement runtime lock. | Run cũ không quan sát thấy package sai. Bản source cũ không khóa chặt lần chạy tương lai. |
| B2-labelonly | Kaggle validation đã chạy; notebook runtime-locked mới đã push, chưa chạy | *Log cũ khớp sáu package; source cũ thiếu pin ba package và enforcement runtime lock. | Như B2-nolabel. |
| B2-flip | Kaggle validation/test đã chạy | *Log khớp sáu package. Source cũ có seed 42 và thiếu pin ba package. | Seed: thấp với scoring hiện hành. Pin package cũ chưa cứng cho run tương lai. |
| B2-rep | Kaggle validation đã chạy; notebook runtime-locked mới đã push, chưa chạy | *Log cũ khớp sáu package. Source giữ repeat=True và tag=repeat. Bản mới áp dụng runtime lock. | Không thấy package sai trong run có log. Điều kiện repeat quan trọng về isolation arm, và được giữ trong notebook mới. |
| B3 | Chưa thấy notebook Kaggle Qwen hiện hành riêng với log run | Không đủ artifact thực thi để đối chiếu. | Chưa đánh giá được lock compliance. |
| B3-nodiff | Notebook riêng có trên nhánh hieu, chưa thấy log inference hiện hành | Không có log phiên bản cài/run để gắn dấu *. | Chưa đánh giá được runtime thực chạy. |
| B3-swap | Chưa thấy notebook Kaggle Qwen hiện hành riêng hoặc log run | Không đủ artifact thực thi để đối chiếu. | Chưa đánh giá được lock compliance. |
| B3-flip | Chưa thấy notebook Kaggle Qwen hiện hành riêng hoặc log run | Không đủ artifact thực thi để đối chiếu. | Chưa đánh giá được lock compliance. |

## Cách hiểu mức độ

- **Thấp với kết quả scoring hiện hành:** inference seed 42 ở source B0, B1 và B2-flip khác sentinel 4294967295 trong lock, nhưng runner dùng llm.reset(), llm.eval(prompt_ids) rồi đọc logits để tính score. Không gọi sampling/generation API. Vì vậy seed chưa được chứng minh là làm thay đổi score ở đường chạy này. Đây là lệch tham số khai báo, không nên gọi là sai khác nghiêm trọng với kết quả scoring. Nếu sau này bật sampling hoặc generation, seed trở thành yếu tố quan trọng.
- **Đáng kể cho provenance và tái lập:** thiếu pin cứng package hoặc không xác minh runtime lock. Log cũ của B0, B1, B1-full, B1-shuf, B1-H2, B2, B2-flip, B2-rep, B2-nolabel và B2-labelonly có xác nhận package trực tiếp khớp bộ lock trong các phiên log được audit. Điều đó không khóa lần chạy tương lai và không chứng nhận toàn bộ dependency transitives.
- **Khác chính sách runtime nhưng chưa chứng minh ảnh hưởng lớn đến logits:** B1-H2 cố định GPU split 1:1 trong khi lock để llama.cpp tự phân layer theo VRAM tại lúc nạp model. Đây là khác biệt về layer placement và provenance, không phải sampling hay cách tính score. Với hai T4 giống nhau và VRAM trống tương đương lúc load, automatic split có thể gần với 1:1. Giá trị VRAM được đọc ở thời điểm load nên không đảm bảo hai phiên luôn chia đúng như nhau. Chưa có kiểm tra logits đối đầu giữa hai cách chia; hiện không có căn cứ xem khác biệt này là nghiêm trọng với score. Colab L4 vẫn là khác profile phần cứng/nền tảng và cần tách khi so sánh kết quả.
- **Chưa thể kết luận:** các arm B3 chưa có bộ notebook/log inference hiện hành để xác nhận package, constructor, split hay scoring thực chạy. Thiếu log không đồng nghĩa đã chạy sai lock.

## Sửa kết luận trước

Bảng trả lời liền trước worklog này xếp seed 42 của B0/B1/B2-flip là “nghiêm trọng”. Phân loại đó không đúng với code path scoring đã audit. Thay bằng mức thấp đối với score hiện tại, đồng thời giữ lại sự thật rằng source seed khác khai báo trong lock. Bảng 15 arm ở trên là bản phân loại đã sửa.

Đính chính thêm về B1-H2: tensor_split=[1,1] so với tự chia theo VRAM là khác biệt cấu hình phân bố layer. Auto split không ngẫu nhiên; llama.cpp lấy free VRAM lúc nạp model làm tỷ lệ. Nếu hai GPU báo VRAM trống bằng nhau thì tỷ lệ split là bằng nhau, còn số layer nguyên có thể làm ranh giới lệch một layer. Chưa có so sánh logits trực tiếp chứng minh sai khác đáng kể. Phân loại là runtime provenance khác nhau, ảnh hưởng logits chưa được xác định và không có căn cứ hiện tại để yêu cầu chạy lại chỉ vì giả định logits đã lệch.

## Bằng chứng

- worklogs/2026-11-07_inference_runtime_lock_and_notebook_differences.md — contract, inventory source và đối chiếu log.
- worklogs/2026-11-07_inference_runtime_log_evidence.json — bằng chứng package/batch/offload cho các phiên có log.
- worklogs/2026-11-07_hieu_5arms_runtime_audit.md — ZIP Hiếu, năm arm, phiên bản sau cài, khác biệt build và giới hạn log.
- worklogs/2026-11-07_hieu_5arms_runtime_locked_delivery.md — năm notebook mới, SHA ZIP và tình trạng chưa chạy.
- worklogs/2026-11-07_b2_rand_notebook_package_lock.md và worklogs/2026-11-07_b2_rand_test_runtime_lock_integration.md — cập nhật enforcement B2-rand.
- worklogs/2026-11-07_phan_cong_va_trang_thai_15_arm.md — tình trạng inference và họ B3.
