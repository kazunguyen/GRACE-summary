# Kiểm tra tích hợp grace_diag_kit vào các arm 01–05

**Hiện trạng sau đối chiếu 02/11/2026:** xem [HIEN_TRANG.md](HIEN_TRANG.md) và [current_status.json](current_status.json). Hai file này bổ sung các snapshot kiểm toán/ngưỡng ngày 01/11; không tạo khóa mới. B2 hiện chưa tích hợp helper vào notebook; watcher chưa được xác minh đang chạy. B2-rand đã có 12 bundle và notebook chạy kèm B2 rerun-66, chưa có output inference.

**Cập nhật B1 ngày 02/11/2026:** đã xác minh output `kaggle_run_01`, ghi bổ sung là **I-07** (ID theo thứ tự nhập sổ, không phải thời gian chạy): **5.434/10.011 mẫu (54,28%)**, gồm Devign validation 2.732, REVEAL validation 2.273, Devign test 429, REVEAL test 0; còn **4.577** mẫu. Dừng do hết ngân sách thời gian. Đã đối chiếu toàn bộ record: không trùng ID, đúng arm/dataset/split/model và hash prompt; **0 invalid score, 3 invalid raw response** ở REVEAL validation. Hai validation đã đủ score; chưa có bằng chứng khóa ngưỡng B1 trước 429 test. Xem [bằng chứng B1](b1_I07_20261102.json) và [sổ run](RUNS.md). Các nhận định chưa có inference B1 trong snapshot cũ chỉ mô tả thời điểm kiểm toán.

## Bổ sung B2-flip — 02/11/2026

Đã nhập **I-06: 5.235/10.011 prediction (52,29%)**, gồm Devign validation 2.732, REVEAL validation 2.273, Devign test 230; REVEAL test chưa chạy. Raw CM: TP=913, TN=1.887, FP=1.819, FN=616; invalid response/score=0. [Báo cáo, hash và danh sách target](b2_flip_I06_20261102/KET_QUA_I06_B2_FLIP.md).

**Trạng thái mới của arm 04:** [notebook tạo prompt](../04_Arm_B2_Flip/notebooks/01_prepare_b2_flip_prompts.ipynb) đã dùng `prepare_frozen_flip.py` để ghép cặp với **B2 tham chiếu từ kho donor thống nhất**; bundle mới đủ 10.011 prompt, graph 40/80 và tokenizer đã pin. [Notebook inference](../04_Arm_B2_Flip/notebooks/02_kaggle_qwen_q4_b2_flip.ipynb) đã nhúng `kaggle_flip_frozen_runtime.py` và `validation_lock.py`, gọi `make_lock`/`persist_lock` trên validation đầy đủ và `require_test_lock` trước test.

Với checkpoint I-06: giữ **5.202** record còn khớp; ưu tiên inference lại **28 Devign validation + 5 Devign test**, rồi tiếp tục **4.776** mẫu thiếu bằng prompt mới. Tổng bổ sung **4.809 lượt LLM**. Có 33 Devign test đổi prompt còn chưa chạy, nằm trong phần 4.776 mẫu này. [Bundle, cách chạy và kiểm thử CPU](B2_FLIP_DONOR_MOI_RESUME.md).

Phần code/input mới đã được kiểm thử CPU; **chưa có inference GPU phiên mới**. Việc nối audit chuyên dụng/evidence và chấm tay vẫn cần nghiệm thu riêng. Các Mục 1–7 bên dưới và JSON đi kèm giữ snapshot kiểm tra **01/11/2026**; nhận định flip dùng donor cũ/chưa có khóa ngưỡng mô tả source tại mốc đó, được thay bằng cập nhật 02/11 ở trên cho phiên mới. Cập nhật này không chứng nhận lại các arm khác.

<!-- donor-rerun-risk-note -->
**Ghi chú donor/rerun:** trạng thái tích hợp không tự quyết định inference lại. B2/flip/rep cần đối chiếu khi đổi bộ donor tham chiếu; B0/B1 giữ prompt/identity thì giữ kết quả. Xem [NGUY_CO_CHAY_LAI_DO_DONOR.md](NGUY_CO_CHAY_LAI_DO_DONOR.md).
<!-- /donor-rerun-risk-note -->

Kiểm tra ngày 01/11/2026 trên file hiện có trong GRACE-summary. Đây là kiểm tra đường gọi notebook/script và thử đọc một prompt thật mỗi arm bằng audit_rows của kit, không chạy inference hoặc thay đổi source các arm. [Bằng chứng JSON](KIEM_TRA_TICH_HOP_TUNG_ARM.json), [script kiểm tra](audit_arm_integration.py).

**Kết luận: đã tích hợp phần tạo prompt/ngân sách token và phần lớn inference, nhưng chưa tích hợp trọn bộ công cụ thành một luồng thống nhất.** Các chức năng dùng chung không cần được sao chép vào từng folder; cần bảo đảm mỗi arm gọi đúng chức năng và xuất dữ liệu tương thích.

## 1. Bảng từng arm tại thời điểm kiểm tra 01/11/2026

| Folder / arm | Tạo prompt, token budget | Audit chuyên dụng của kit | Dữ liệu/manifest dùng chung | Inference, journal/resume | Tự khóa tau và kiểm tra trước test trong notebook hiện tại |
|---|---|---|---|---|---|
| 01 / B2 | Có: PromptBuilder → render_arm B2 và TokenCounter; graph 40/80 | Chưa nối; chỉ có kiểm tra/hash và metadata | Có bundle/spec manifest; B2 Devign đang dùng kho donor cũ, chưa nhất quán với snapshot mới | Có notebook Kaggle, logprob/logits, ghi records và fsync/resume | Không thấy trong source notebook hiện tại; runtime có threshold riêng vẫn nằm ở file khác |
| 02 / B0 | Có: renderer riêng, dùng constants và TokenCounter baseline, graph/demo payload trống theo yêu cầu | Chưa nối; có hash/token/ID checks | Đọc frozen raw và kiểm hash snapshot | Có notebook Kaggle và runtime riêng, fsync/resume | Có make_lock/persist_lock và require_test_lock trong notebook/runtime |
| 03 / B1 | Có: helper chung tier1_prompt_tools, dùng graph B2 đã cắt; trần 40/80 | Chưa nối; có đối chiếu B2, hash và token budget | Dùng lại specs/CPG B2; không có donor trong prompt B1 | Có notebook Kaggle và kaggle_b1_runtime.py | Chưa thấy make_lock/require_test_lock |
| 04 / B2-flip | Có: helper chung, chỉ đảo nhãn demo, giữ code/graph/demo B2 | Chưa nối; có đối chiếu cặp/hash/token | Cùng demo B2; kế thừa phạm vi donor cũ | Có notebook Kaggle nhúng runtime | Chưa thấy make_lock/require_test_lock |
| 05 / B2-rep | Có: helper chung, prompt giống B2 từng ký tự | Chưa nối; có đối chiếu cặp/hash/token | Cùng demo B2; kế thừa phạm vi donor cũ | Chưa có notebook inference trong folder tại thời điểm kiểm tra | Chưa có runner để nghiệm thu lần gọi mới, không lấy response B2 |

Tất cả năm arm đều đã có bốn manifest prompt tương ứng Devign/ReVeal validation/test. Có artifact prompt không đồng nghĩa mọi chức năng audit/inference đã được nối và nghiệm thu. B2-rep còn chờ notebook inference phù hợp với giai đoạn trước người dùng chỉ yêu cầu sinh prompt.

## 2. Tạo prompt và ngân sách token: đã nối theo các cách phù hợp

- B2: [prompt_builder.py](../01_Author_Baseline_Unified/prompt_builder.py) gọi renderer ở diagnostic_kit.
- B0: [prepare_b0.py](../02_Arm_B0_Source_Only/prepare_b0.py) giữ scaffold B2 theo yêu cầu, dùng TokenCounter của kit.
- B1/flip/rep: [prepare_cached.py](../tier1_prompt_tools/prepare_cached.py) dùng chung renderer/helper, tái sử dụng graph đã cắt và metadata B2. Đây là tích hợp qua thư viện chung, không cần copy probes.py vào ba folder.

Các variant scaffold B0/B1 là quyết định người dùng đã yêu cầu; không coi việc khác renderer canonical của PDF là lỗi triển khai, nhưng phải mô tả đúng variant khi tổng hợp kết quả.

## 3. Audit prompt: mới tích hợp một phần kiểm tra, chưa nối đủ prompt_audit

Không tìm thấy lời gọi audit_rows/stratified_manual_sample trong luồng sinh prompt các folder 01–05. Không tìm thấy artifact audit_summary.json hoặc manual_sample.jsonl trong phạm vi output kiểm tra (đã loại test giả lập).

Thử đưa một dòng prompt thật của mỗi arm vào `grace_diag.prompt_audit.audit_rows` đều gặp **KeyError: 'evidence'**. Lý do: kit yêu cầu dòng có dạng `{id, arm, seed, prompt, evidence}`, trong khi các notebook hiện xuất tokens/truncated/graph_missing trực tiếp ở cấp ngoài. Vì vậy không thể chỉ trỏ CLI audit của kit vào prompts.jsonl hiện có rồi coi đã tích hợp.

Các kiểm tra đã có (hash, ID, ngân sách, ghép cặp B2; script kiểm toán trung tâm) vẫn có giá trị. Phần còn thiếu là adapter evidence đầy đủ cho từng arm, gọi audit trong luồng chuẩn bị hoặc một bước chung bắt buộc, xuất summary/CSV/mẫu đọc tay. Adapter cần giữ policy và thông tin demo bị cắt quá nhiều, không chỉ đổi tên trường tokens. B0/B1 chủ động không có demo phải được phân biệt với lỗi demo rỗng.

## 4. Đóng băng dữ liệu là bước dùng chung

Không cần chạy build_manifests.py riêng cho mỗi arm: điều đó có thể tạo các kho donor lệch nhau. Snapshot nghiên cứu đã được tạo bằng freeze_research_data.py và có hash dùng chung. B0 đang trực tiếp kiểm và dùng frozen raw.

B2 cũ chưa được tạo lại từ kho Devign mới (21.750 donor cũ so với 21.691 donor mới). Các helper flip/rep cố ý giữ lựa chọn B2 cũ để phép so ghép cặp đúng; audit ghi 5 prompt Devign validation và 16 prompt Devign test có demo ngoài kho mới. Đây là trạng thái đã khai báo, không tự coi việc có FROZEN_ROOT trong notebook là đã chuyển retrieval sang kho đó. B1 không đưa demo vào prompt nên các số demo tham chiếu trong manifest B1 không phải demo bị đưa vào B1.

## 5. Inference đã được thay bằng Kaggle; chưa đồng bộ giữa các notebook

Không bắt buộc các arm gọi run_matrix.py hoặc llm_backend.py server, vì workflow đã chuyển sang llama-cpp-python trong Kaggle. Các notebook 01/02/03/04 hiện có đường chạy Llama, binary_scores, evaluate_output, ghi records/fsync và batch/resume tương đương các chức năng cần thiết.

Tại lần kiểm tra **01/11/2026**, source notebook B2/B1/flip chưa gọi helper tự khóa và kiểm ngưỡng, còn B0 có. B2 có [kaggle_b2_threshold_runtime.py](../01_Author_Baseline_Unified/kaggle_b2_threshold_runtime.py) với khả năng kiểm ngưỡng, nhưng notebook B2 khi đó nhúng runtime khác không gọi require_test_lock. Đây là chênh lệch ghi nhận tại thời điểm kiểm tra; B2-flip đã nhúng helper/ngưỡng trong bản sửa 02/11 nêu ở đầu báo cáo.

Watcher/auto_lock_validation local có thể khóa ngưỡng sau khi nhập records về, nhưng việc đó không thay cho điều kiện runtime phải có khóa trước khi tự chuyển sang test. Kiểm toán này chỉ ghi nhận, không sửa notebook đang được người dùng vận hành.

## 6. SUP-LR / SUP-MLP / SUP-METRIC là đối chứng chung, không nằm bên trong mỗi arm LLM

[supervised_anchor.py](../01_Author_Baseline_Unified/diagnostic_kit/src/grace_diag/supervised_anchor.py) đã có code train trên train, chọn tau trên validation và xuất score validation/test, ba seed. Chúng là các arm đối chứng riêng của nghiên cứu. Nên tạo một workflow anchor dùng chung theo dataset/split/seed, rồi ghép ID để so với mọi arm B0/B1/B2; không train một SUP-LR khác cho từng arm LLM.

Hiện chưa tìm thấy notebook/script dự án gọi run_anchor để tạo kết quả anchor, cũng chưa có anchor_scores.csv hoặc anchor_summary.json trong output. CLI của kit đòi embedding NPZ `{ids, X}`, trong khi cache CodeT5 đang lưu vectors.npy + manifest.json. Cần adapter đọc trực tiếp hoặc xuất đúng NPZ, giữ kiểm ID/hash; không cần encode CodeT5 lại.

## 7. Phần còn thiếu để gọi là tích hợp đầy đủ

1. Nối adapter + prompt_audit vào luồng chuẩn bị chung cho cả năm arm; xuất summary và mẫu đọc tay tương thích variant.
2. Thống nhất dữ liệu/donor của B2 tham chiếu với phạm vi giao thức đã chọn; không thay demo riêng lẻ giữa các arm.
3. Đồng bộ các bản runtime nhúng trong B2/B1/flip với helper ngưỡng đang dùng; khi tạo inference rep phải bảo đảm đó là lần gọi mới, không dùng response cache B2.
4. Tạo workflow supervised anchor dùng cache CodeT5 chung và đầu ra anchor_scores/summary để so sánh các arm.

Chưa thực hiện các thay đổi tích hợp trên trong đợt kiểm tra này. Việc có module trong diagnostic_kit mới chứng minh có năng lực mã nguồn; bảng trên phân biệt rõ nơi đã gọi, nơi mới kiểm tra một phần và nơi chưa có workflow/đầu ra.
