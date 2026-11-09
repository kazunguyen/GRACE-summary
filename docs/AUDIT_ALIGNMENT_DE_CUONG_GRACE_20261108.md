# Đối chiếu tiến độ GRACE với đề cương nghiên cứu hợp nhất

**Ngày audit:** 08/11/2026, khoảng 17:27 GMT+7. **Mốc Git:** `68b7bf1`, kèm working tree B3 chưa commit tại lúc đọc. **Kết luận:** hướng nghiên cứu và phần lớn hạ tầng đang bám mục tiêu tái lập có chẩn đoán; chưa thể kết luận toàn bộ triển khai tuân thủ nguyên trạng đề cương hoặc đủ điều kiện phân tích xác nhận cuối. Có các điều chỉnh phương pháp cần đối chiếu amendment, các điểm chưa nhất quán giữa tài liệu–config–artifact, và deliverable RQ5/RQ6 còn thiếu.

**Điểm cần dừng ngay ở phạm vi nghiệm thu:** chủ dự án xác nhận trong cuộc trao đổi audit này rằng hai review B3 đang được đánh giá, **chưa có kết quả cuối**. Do đó hai file approve hiện có và `ACTIVE_VERIFIED_POOL` trong v4 chưa được coi là hai review thật đã hoàn tất. Không dùng trạng thái đó để cho phép inference B3.

## 1. Nguồn và phạm vi kết luận

Nguồn chuẩn để đối chiếu nội dung là [De_cuong_nghien_cuu_GRACE_hop_nhat.docx](OSF_response/De_cuong_nghien_cuu_GRACE_hop_nhat.docx), bản đề ngày 28/10, cập nhật 03/11/2026. SHA-256 đọc trực tiếp: `a55b3992696f69bd2c05e360e76827071396b5a9b5dec5a75bc6512cac9d0d40`.

Đã đọc cả paragraph và 31 bảng của DOCX, cùng [phản hồi về đăng ký OSF](OSF_response/PhanhoiHieuDungVeDangKyOsf.pdf), [PDF amendment local](OSF-update-20261107.pdf), protocol/arms/preregistration, code renderer/scorer/evaluator, freeze manifest, threshold audit, run handoff, worklogs và hồ sơ B3 mới nhất. Các số thứ tự “bảng” dưới đây chủ yếu dùng tên/nội dung bảng và mục trong đề cương để tránh phụ thuộc cách Word dàn trang.

Đây là audit đối chiếu phương pháp và chứng cứ hiện có. Không chạy lại inference, không sửa config/bank/threshold, không tính lại toàn bộ threshold hoặc bootstrap trong lượt này, không chạy thêm test không liên quan. Kết quả kiểm toán số học trước được dẫn đúng phạm vi. Không kiểm tra trạng thái OSF trực tuyến; PDF local thể hiện nội dung đề xuất cập nhật, không tự chứng minh amendment đã có registration stamp công khai.

Trạng thái Kaggle trong báo cáo dựa trên snapshot gần nhất đã thu **khoảng 16:08 GMT+7**, không phải truy vấn live mới ở 17:27. Hồ sơ v4 đang được triển khai trong working tree nên không suy từ artifact trung gian thành một release đã nghiệm thu.

## 2. Đánh giá tổng thể

| Mảng | Đánh giá | Ý nghĩa |
|---|---|---|
| Mục tiêu nghiên cứu | Bám sát | Đang đo vai trò graph/demo/nhãn và khả năng phân biệt bằng score, không chỉ đuổi F1 hay “cải tiến GRACE” |
| LLM tự host, logprob, artifact từng mẫu | Bám mục đích; có thay cách thực hiện | Qwen GGUF/Kaggle phù hợp phương án đề cương cho phép; direct full logits khác đường server top-20 được mô tả |
| Data freeze và clean donor | Có nền tảng phù hợp | Có manifest, lexical dedup, loại conflict, near-duplicate flags; số split/source khác bảng dữ liệu đề cương cần giải trình |
| Prompt và probe | Phù hợp nhiều nguyên tắc; có sai khác cấu hình | Thứ tự Figure 6/token budget đúng định hướng; prefix 40/80 khác 25/25; coverage/retention cần báo cáo theo artifact thực |
| Threshold | Quy tắc đúng; nguồn giá trị chưa thống nhất hoàn toàn | Audit đã tính lại từ validation; B0/B1 trong config tổng vẫn là bốn giá trị cũ; P-pre/P-post lịch sử chưa chứng minh được đầy đủ |
| Runtime | Một số run được chứng minh tốt hơn run khác | B1-full đạt contract lúc launch; không đồng nghĩa mọi arm có cùng mức chứng nhận hoặc tất cả đã nạp contract hiện tại |
| B3 mới | Có tiến bộ source; là nhánh điều chỉnh phương pháp | Verified same-function patch pool và selector mới không phải nguyên xi retrieval ban đầu của đề cương; review cuối chưa hoàn tất |
| Statistics và giả thuyết | Cần đối soát trước chạy bảng cuối | Danh sách contrast, tên H5.2/H5.3, routing và họ Holm chưa biểu diễn thống nhất giữa các nguồn |
| RQ5 supervised/complementarity | Chưa hoàn tất chiến dịch hiện tại | Có Step 0 lịch sử; chưa thay được ba-seed anchors và Qwen P-pre/P-post/routing cần cho lượt cuối |
| RQ6 human review/label audit | Chưa hoàn tất | Packet/prompt review cũ không thay chấm relevance, error packets và label audit đầy đủ |
| Gói tái lập/bài báo | Đã có thành phần; chưa nghiệm thu toàn bộ | Cần evaluator thống nhất, bảng/hình sinh lại, provenance/deviation/exposure rõ và các deliverable còn thiếu |

Không nên gán một tỷ lệ “đã hoàn tất X% đề cương”: các hạng mục không có trọng số được khai báo và việc có code không đồng nghĩa có kết quả được nghiệm thu.

## 3. Những việc đang làm đúng hướng

1. **Giữ trọng tâm diagnostic replication.** B0/B1/B2 và các phép bỏ nhãn, chỉ nhãn, đảo nhãn, random demo, shuffle graph cho phép trả lời đúng RQ1–RQ4. Runtime lock và source audit phục vụ tính hợp lệ của các phép so đó, không phải đóng góp hiệu năng độc lập.
2. **Dùng model tự host có score liên tục.** Qwen3-Coder-30B-A3B-Instruct GGUF Q4_K_M trên Kaggle T4×2 nằm trong lựa chọn phần cứng/backend của Mục 6.2 và Bước 1. AUROC/AUPRC có thể được tính từ score từng mẫu thay vì suy từ nhãn 0/1.
3. **Giữ danh tính dữ liệu và ngưỡng.** Frozen clean bank, ID sets, model/tokenizer hashes, per-arm locks, cache isolation B2-rep, lưu legacy output nguyên vẹn và không tune bằng test đều phù hợp nguyên tắc đề cương.
4. **Dừng khi nguồn B3 chưa đủ.** Việc chấp nhận REVEAL unresolved thay vì ghép cặp giả là đúng. Phần nguồn case FFmpeg đã được audit độc lập với upstream; bản v2 bổ sung raw evidence/mapping trong payload giúp truy vết tốt hơn.
5. **Sửa B1-full vì lỗi prompt thật.** Chạy mới census sau khi sửa ngân sách/renderer có lý do vận hành cụ thể và đã ghi exposure/deviation; phù hợp hướng dẫn “chạy lại khi cấu hình sai”, không phải chạy lại để đổi ngày sang sau đăng ký.
6. **Tách hoàn tất inference khỏi nghiệm thu.** B1-full đã đủ 5.006 test và có acceptance riêng; B3 lịch sử chỉ là validation; B1-shuf còn chạy. Cách diễn đạt này đúng hơn gọi mọi arm là “đã xong test”.

## 4. Các sai khác so với đề cương cần ghi rõ

### A1. Split/dataset source và validation census

**Đề cương, Mục 6.1:** bảng dữ liệu nêu Devign validation 2.724 và REVEAL validation 2.196, nguồn REVEAL `SensorLLM/reveal`. Bước 2 cho phép subset 600 hoặc toàn validation nếu đủ GPU.

**Thực tế:** freeze sử dụng Devign train 21.854 / validation **2.732** / test 2.732; REVEAL `claudios/ReVeal` train 18.187 / validation **2.273** / test 2.274. Clean donor bank tương ứng **21.691** và **17.636**. Full validation 5.005 là lựa chọn phù hợp với phương án full-validation, nhưng không được chép các số cũ của bảng đề cương vào Methods như thể cùng dữ liệu.

Freeze ghi normalization bằng lexical tokens có giữ literals; near-duplicate dùng token-3gram Jaccard ≥0,9 và chỉ gắn cờ. Có **260 Devign** và **296 REVEAL test** near flags theo manifest, nên báo cáo dual partition là yêu cầu thật, không phải một dòng checklist. Các số preliminary duplicate 108/52 trong đề cương cũng không phải số freeze cuối.

**Cần làm:** lập bảng lineage theo dataset revision/split/raw hash/clean bank count, giải thích thay nguồn REVEAL và khác validation census. Tính metric cả full test và clean near-deduplicated test bằng cùng ID filter đã khóa. Không sửa frozen manifest để khớp số in trong đề cương.

Nguồn: [freeze manifest](../01_Author_Baseline_Unified/output/research_freeze_20261101/freeze_manifest.json), [protocol hiện có](../configs/protocol.yaml).

### A2. Graph prefix 40/80 so với 25/25 và ý nghĩa B1-full

**Đề cương:** Mục 6.3 và bảng arm mô tả B1 prefix **25 nút/25 cạnh**; B1-full thêm nút đến ngân sách 1.500 token. Mục 7 yêu cầu shuffled graph giữ cùng chính sách cắt.

**Thực tế:** `DEFAULT_GRAPH_PREFIX` và `configs/protocol.yaml` là **40/80**; `graph_full` có source caps 40/80 và closed-node-prefix. `preregistration.md` đã mô tả B1 40/80, nhưng note trong `configs/arms.yaml` vẫn ghi 25/25.

**Đánh giá:** đây là khác biệt phương pháp đã xuất hiện trong giao thức thực thi, không chỉ lỗi tên. Có thể triển khai theo giao thức được khóa sau khi đối soát thẩm quyền; không được gọi là khớp nguyên trạng đề cương. B1-full có thể giống B1 khi graph vừa/cùng giới hạn nguồn; cần đo tỷ lệ prompt trùng để diễn giải RQ3.

**Cần làm:** ghi deviation 25/25 → 40/80, source cap của fill, xác nhận cùng policy cho B1/B1-shuf và xuất tỷ lệ graph/prompt trùng giữa B1/B1-full. Giữ frozen config; sửa diễn giải ở tài liệu bổ sung/version được phép thay vì sửa ngầm contract đã đăng ký.

Nguồn: [renderer](../01_Author_Baseline_Unified/diagnostic_kit/src/grace_diag/probes.py), [arms](../configs/arms.yaml), [preregistration](../preregistration.md).

### A3. Direct full logits, seed và backend khác đường server top-20

**Đề cương, Mục 6.4/Bước 1:** server vLLM/llama.cpp, top-20, greedy, seed42; xử lý digit vắng bằng cận trên, smoke ≥99% có cả hai digit và repeat agreement ≥98%.

**Thực tế:** `llama-cpp-python 0.3.16`, `llm.eval`, full-vocabulary logits, score float64; top5 chỉ chẩn đoán. Prompt seed42 tách khỏi constructor seed sentinel `4294967295`, không có sampling. Tokenizer/model được kiểm hash và token IDs. Smoke 20 mẫu ghi cả hai digit trong top5 và repeat agreement đều 100%.

**Đánh giá:** đáp ứng mục tiêu score liên tục và tránh mất xác suất khi digit ngoài top-k; đây vẫn là điều chỉnh implementation cần trình bày chính xác. Không áp quy tắc “digit vắng top5 ⇒ invalid” cho full-logits runner; không gọi sentinel là seed42. Ngược lại không mô tả đã lưu full top-20 dictionary khi artifact thực chỉ lưu top5 cùng hai digit logprobs.

Raw greedy không phải 0/1 phải báo riêng; score vẫn hợp lệ nếu hai digit logits đầy đủ, hữu hạn. Ví dụ B1-full có **2 raw invalid REVEAL nhưng 0 numeric invalid**. Điều này phù hợp score policy thực tế đã ghi, nhưng khác câu “đầu ra đúng một token 0/1” nếu được hiểu là mọi raw response đều binary.

**Cần làm:** đưa đường scoring/seed/tokenization thực vào Methods và deviation ledger; phân biệt smoke lịch sử với acceptance của từng runtime release. Không cần inference lại chỉ để tạo top20 khi hai digit scores chính xác đã có; nếu đổi serving/sampling thì cần danh tính/policy mới.

Nguồn: [smoke](../Runs-management/step1_backend_smoke/smoke_test_report.json), [B1-full acceptance](../Runs-management/run_handoff_20261108/B1_FULL_RUNTIME_ACCEPTANCE.md), [runtime contract](../configs/inference_runtime_lock.json).

### A4. Runtime lock giúp kiểm soát điều kiện nhưng chưa tạo đồng nhất hồi tố

Mục tiêu đề cương là mọi đối chứng cùng điều kiện. B1-full mới có bằng chứng source/build/native/per-record đạt **contract sáu package lúc launch**; SciPy1.16.3 cũng được quan sát trong pip freeze. Điều đó không chứng minh notebook đã nạp contract bảy package ban hành sau. Một số arm lịch sử chưa có cùng độ đầy đủ provenance.

**Cần làm:** bảng runtime identity theo arm/seed/session, ghi model/backend/packages/constructor/shape và mức bằng chứng; chỉ rõ khác biệt nào là observed environment, khác biệt nào là thiếu chứng cứ. Không suy thiếu log = chắc chắn chạy sai, cũng không suy package giống nhau = runtime tương đương đầy đủ.

Không bắt buộc chạy lại mọi arm chỉ để đồng bộ tên version. Theo PDF phản hồi, rerun chỉ khi có mismatch quan trọng, thiếu score cần thiết hoặc B2-rep dùng cache; xử lý đúng arm bị ảnh hưởng, giữ lịch sử. Các so sánh nhạy với khác runtime cần được đánh giá ảnh hưởng và khai báo, không được bỏ qua vì tất cả đều dùng T4.

### A5. B3 mới là thay phương pháp; một pair chưa phải retrieval phong phú

Đề cương giữ B3 như cặp tương phản + difference; bảng model/retrieval mô tả CodeT5/whitening/top50/top5/rerank Jaccard–AST. Same-function verified patches còn được nhắc như mở rộng ở phần định hướng. Nhánh mới đang dùng pool patch thật, hai reviewer và exhaustive mean token-set Jaccard, bỏ B2-anchor và selector heuristic cũ. PDF amendment local nêu rõ đề xuất thay cách xây cặp/difference B3.

**Đánh giá:** đây là nhánh điều chỉnh minh bạch có giá trị, nhưng không phải chỉ “sửa runtime” hoặc triển khai nguyên xi đề cương. So B3 mới với B2 đồng thời thay nguồn demo/selection/pair count/explanation; không quy toàn bộ chênh lệch về “cân bằng nhãn” hay “sửa retrieval” nếu chưa có đối chứng phù hợp.

Pool v4 hiện chỉ có **một pair Devign**. Nếu sau review chỉ khóa đúng một pair, mọi query đều nhận cùng pair: vẫn có thể đánh giá cấu hình đó nếu scope được chốt, nhưng không chứng minh khả năng thích ứng truy hồi theo target. Không tự đặt số pair tối thiểu mới sau khi nhìn metric; chốt coverage/scope và quy tắc dừng xây pool trước inference. REVEAL còn unresolved thì không tuyên bố đã triển khai B3 mới trên hai dataset.

Hồ sơ v2 đã biểu diễn raw mapping và giới hạn caller hunk ngoài demo tốt hơn bản cũ. Cần hoàn tất review thật và phân loại amended/exploratory theo quyết định có bằng chứng; không dùng hai file approve chuẩn bị sẵn làm xác nhận độc lập.

## 5. Những điểm đang chặn nghiệm thu hoặc phân tích cuối

### B1. Review B3 chưa cuối nhưng pool đang ACTIVE — cần ưu tiên cao nhất

Quan sát trong v4: hai form Hiếu/Dũng có decision approve; pool manifest ghi một Devign pair `ACTIVE_VERIFIED_POOL`. Tuy nhiên **chủ dự án trả lời đang đánh giá và chuẩn bị kết quả cuối** trong cuộc trao đổi audit này. Vì thế chưa xác nhận được các file là hai review độc lập đã được hai người chốt trên payload cuối.

**Yêu cầu trước inference:** giữ nguyên hồ sơ draft làm lịch sử; ở trạng thái điều phối/release tiếp theo ghi PENDING_REVIEW/BLOCKED, chặn sử dụng pool. Chỉ sau khi mỗi reviewer thực sự xác nhận form/payload/hash, timestamp và phạm vi source evidence mới được nghiệm thu G2. Không tự sửa phiếu, tự gắn chữ ký hoặc suy approve từ một lần “đồng ý làm tiếp”.

Audit này chỉ báo phát hiện, **không tự sửa trạng thái pool hoặc hủy tiến trình của người dùng**. Việc có chữ “ratified” trong mapping JSON cũng chưa thay được xác nhận thẩm quyền nếu vẫn đang duyệt.

### B2. Threshold B0/B1: toán đúng ở amendment nhưng nguồn dùng cuối chưa thống nhất

Mục 6.6 và PDF phản hồi yêu cầu tính τ* từ validation, khóa trước test tương lai, evaluator chỉ đọc đúng lock. Audit độc lập trước đã quét validation đầy đủ và ghi:

| Dataset/arm | Giá trị trong config gốc/tổng | Giá trị tính lại và amendment local |
|---|---:|---:|
| Devign B0 | 0,08 | 0,98 |
| REVEAL B0 | 0,44 | 0,30 |
| Devign B1 | 0,88 | 0,98 |
| REVEAL B1 | 0,74 | 0,63 |

Config tổng hiện vẫn chứa bộ cũ. Điều này không phủ nhận amendment đã tính đúng, nhưng evaluator đọc nhầm nguồn sẽ tạo điểm hoạt động không theo quy tắc đề cương. Bốn lock P-PRE/P-POST gốc cũng chưa được audit tính lại đầy đủ vì thiếu saved validation probabilities của đúng fit đó; không được thay bằng threshold của fit khác.

**Cần làm:** tạo lock amendment/adapter riêng được phê chuẩn, với source validation/hash/full grid và precedence rõ; evaluator cuối pin file đó cho đúng method. Không sửa frozen configs gốc hoặc lấy tau lịch sử B3 cho B3 mới. Giữ exposure/timing gốc; audit toán học sau này không chứng minh đã khóa trước mọi test lịch sử.

Nguồn: [threshold audit đã tính từ validation](../Runs-management/threshold_audit_20261108/final/audit.json), [amendment local](../Runs-management/osf_amendment_20261106/OSF_UPDATE_EN.md), [threshold config gốc](../configs/thresholds.json).

### B3. “11 phép so sánh” chưa trùng danh sách máy đọc được và mục tiêu H5

Đề cương Mục 4.3/6.6 có 11 giả thuyết định danh; một số giả thuyết gồm nhiều phép so, nên cần định nghĩa họ kiểm định cụ thể, không suy số p-values từ số hàng giả thuyết. `configs/protocol.yaml` hiện có **12 mục primary_contrasts**, gồm tách H1.1/H1.2 theo dataset; không có mục tên H5.2 và gộp P-PRE/P-POST vào H5.3. Đây là kết quả đếm config hiện tại, không phải đề xuất tự đổi họ kiểm định.

Một số ý nghĩa cũng không đồng nhất trực tiếp:

- Đề cương H1.2 là mức tuyệt đối MCC/F1 so bài gốc/mốc hằng; config H1.2 lại là B0–B2 trên REVEAL.
- Đề cương H2.2c cần kiểm labelonly tái tạo ≥80% chênh lệch B2−B1; một Δ labelonly–B2 đơn lẻ không tự đánh giá điều kiện tỷ lệ đó.
- Đề cương H5.2 là ΔMCC(P-post−P-pre)<0,02; H5.3 là benefit−random q10 BA margin0,01 cùng đối chứng repair. Config routing thêm benefit−confidence margin0,02; preregistration có diễn giải mở rộng, cần mapping tới amendment/authority, không thay âm thầm estimand gốc.

**Cần làm trước bảng B:** một bảng crosswalk đề cương → registered protocol/amendment → estimand/dataset/metric/δ/chiều Δ/loại kiểm định/family member. Chốt cách kiểm absolute/ratio/sensitivity/routing riêng, bên cạnh generic paired contrasts. Nếu khác đã được duyệt, ghi là khác biệt có thẩm quyền; nếu chưa có căn cứ, giữ pending. Không sửa frozen YAML/preregistration để làm cho số hàng bằng 11 sau khi đã xem kết quả.

### B4. Evaluator cuối cần chặn ID intersection thiếu và chứng minh Holm đúng họ

`table_b` hiện dùng `sorted(set(A) & set(B))`, lọc cả hai valid; chưa thấy trong chính hàm này kiểm hai arm có đủ cùng official census/labels. Vì thế một bảng vẫn có CI dù đầu vào arm thiếu mẫu, nếu thiếu gate trước đó. Code có paired cluster bootstrap khi group có sẵn, nhưng sự hiện diện code không chứng minh report cuối đã dùng đúng cluster map và ghi đủ số cụm/degenerate draws.

Holm trong hàm hiện áp trên các p-value McNemar của metric MCC. Đề cương nhấn mạnh McNemar là kiểm bất đồng lỗi, **không phải p-value cho ΔMCC hoặc ΔAUROC**. Khi công bố phải giữ đúng ý nghĩa này; không lấy McNemar p để tuyên bố mọi metric đã có p-value được hiệu chỉnh.

**Cần làm:** gate exact IDs/labels/official N trước join, báo invalid coverage và policy, groups/cluster counts, số bootstrap suy biến và seed; định nghĩa family trước chạy bảng. Table A có guard thiếu threshold tại entry point; không bỏ guard đó hoặc dựa vào fallback 0,5 ở lời gọi bảng riêng.

Nguồn: [evaluate_final.py](../01_Author_Baseline_Unified/diagnostic_kit/src/grace_diag/evaluate_final.py), [stats.py](../01_Author_Baseline_Unified/diagnostic_kit/src/grace_diag/stats.py).

## 6. Những phần đề cương còn chưa hoàn tất

### C1. RQ5 chưa được thay bằng việc chạy xong các arm LLM

Đề cương Mục 6.3, 6.5–6.6, Bước 6 yêu cầu:

- SUP-LR/SUP-MLP/SUP-METRIC trên CodeT5 768d/26 metrics, ba seed42/43/44, cùng frozen split/ID và validation-only thresholds.
- Qwen expert B2 scores join với 34 base features, P-pre/P-post 34 vs38, cùng folds/scaler/threshold-selection policy, OOF theo group và fallback đối xứng khi expert invalid.
- Repair/harm theo lớp bên cạnh ALL-0/ALL-1/random cùng positive rate; confidence/benefit/random20seed/oracle ở q5/10/25%; đo chi phí CPU/GPU/chuẩn bị/cold-warm.

Có [Step 0 diagnostic lịch sử](../Runs-management/step0_diagnostic/README.md), đã được ghi nhận theo phạm vi DeepSeek/historical expert. [Checklist preregistration](../preregistration.md) cũng nêu rõ chưa có artifact ba-seed anchors và kết quả Qwen P-pre/P-post/routing hoàn chỉnh cho chiến dịch này. Không được dùng threshold fit lịch sử khác hoặc số dev-100 làm kết quả xác nhận cuối.

**Ưu tiên:** tiến hành chuẩn bị/join/kiểm dữ liệu offline song song với review nguồn B3; không cần chờ toàn bộ patch-pair REVEAL mới bắt đầu RQ5. Mọi fit/scaler/OOF phải tránh test leakage. Không chọn lại winner hoặc tăng model depth vì thấy test không đẹp.

### C2. RQ6 không được thay bằng review hai source-pair forms

Đề cương Bước 8 yêu cầu 100 retrieval targets **mỗi dataset**, rubric sink/variable/guard/evidence line, hai người độc lập và κ trước hòa giải; 60 ca sửa/hỏng bốn ô; 100 label-audit cases mỗi dataset và phân tích conditional accuracy có CI.

Review 30 prompt mỗi dataset để kiểm toàn vẹn (đã được checklist ghi nhận) khác các bộ chấm này; review hai phiếu source case B3 cũng khác. Chưa có hồ sơ hoàn tất các bộ kết quả Qwen trên trong nguồn được đối chiếu; checklist vẫn để pending. Không khẳng định chưa từng có bất kỳ review lịch sử nào của nhóm.

**Cần làm:** lập sampling/answer-key/blinding/rater ledger thật, giữ bất đồng/không đủ ngữ cảnh, tính κ trước adjudication; không sửa benchmark labels vì lời giải thích LLM. Không tự sinh nhận xét hoặc chữ ký để lấp checklist.

### C3. Prompt coverage và H2 treatment coverage cần báo riêng

Đề cương không chỉ yêu cầu số token tổng: còn retained code/demo fraction, demo <25%, graph_missing, duplicate prompt và manual review. Các audit lịch sử đã ghi cờ truncation/no-guard; không dùng số cũ như thể vẫn là tỷ lệ cuối của run đã sửa.

Đặc biệt H2 có thể chứa fallback text mà `graph_missing=false` nhưng không có guarded evidence hữu ích. Đếm có CPG/khối text không đồng nghĩa đã cung cấp treatment H2. Cần báo source coverage, guarded-evidence yield và fallback riêng; không diễn giải “H2 không giúp” nếu phần lớn target không nhận evidence tương ứng.

Nếu graph/demo thật sự vắng vượt stop rule, xử lý theo điều kiện Mục 7 và ghi deviation; không xóa target khỏi census. Chỉ các arm/phần bị ảnh hưởng mới cần điều tra correction/rerun, không blanket rerun toàn bộ.

### C4. Thống kê, AUPRC và reproducibility package vẫn là công việc riêng

Các metric mô tả B1-full/B2 hiện có chưa phải full Bảng A–D. Cần thêm AUPRC kèm prevalence baseline, operating point0,5 và τ*, positive-rate, invalid/bounded/coverage, sensitivity flip−repeat, paired CI và contrasts đã được đối soát, hai partition full/clean. Không kết luận “không tác dụng” chỉ vì p>0,05 hoặc CI chứa0.

Bước 9 cần script/tài liệu tái tạo bảng/hình từ records, lock/scaler/vocabulary/model hashes, log đã loại credential, artifact version rõ và thử tái lập offline. Việc push một commit có records là tiến bộ về lưu trữ, chưa tự tạo acceptance toàn gói/DOI.

## 7. Trạng thái các run dùng để lập kế hoạch

| Arm/phạm vi | Bằng chứng gần nhất | Diễn giải hợp lệ |
|---|---|---|
| B1-full test seed42 | 5.006/5.006, PASS_LAUNCH_CONTRACT | Đã hoàn tất inference và acceptance có phạm vi; không cần thêm seed43/44 cho arm tất định này |
| B1-shuf test seed42/43/44 | RUNNING tại snapshot16:08, chưa có file công bố | Cần tiếp tục lấy output/kiểm từng seed; chưa có số live đáng tin |
| B2-rep/nolabel/labelonly | Mỗi arm đủ 5.006 test; đã công bố records | Hoàn tất không tự chứng minh mọi run đáp ứng contract mới nhất |
| B2-rand | Seed42/43 test đủ theo I-20; seed44 còn phạm vi partial riêng | Không ghi toàn ba seed đã hoàn tất chỉ từ hai seed/headline |
| B1-H2 Kaggle | Validation/test complete theo ledger; Colab giữ exploratory | Cần diễn giải source/evidence coverage và platform provenance đúng phiên |
| B3 lịch sử | Validation đủ 5.005; không phải B3 mới/test | Không migrate scores/tau vào verified-patch-v1 |
| B3 verified patch v4 | Một Devign pair trong manifest ACTIVE; review thực đang đánh giá | Chưa accepted G2; trạng thái ACTIVE đang đi trước xác nhận cuối |
| B3-nodiff/swap/flip | Không tự thêm vào lịch GPU hiện tại | Vẫn nằm trong ma trận nghiên cứu; nếu hoãn phải ghi partial-scope, không coi giả thuyết liên quan đã đủ |

Nguồn: [RUNS](../Runs-management/RUNS.md), [run handoff](../Runs-management/run_handoff_20261108/RUN_STATUS.md), [snapshot16:08](../Runs-management/run_handoff_20261108/status_snapshot_1608/STATUS.md).

## 8. Thứ tự xử lý để bám sát đề cương mà không kéo dài audit vô hạn

| Ưu tiên | Việc cụ thể | Tiêu chí xong |
|---|---|---|
| P0 — ngay trước B3 inference | Giữ review v4 ở trạng thái chưa nghiệm thu; chờ kết quả thật của Hiếu/Dũng | Hai xác nhận độc lập trên payload/evidence cuối; release gate không dùng draft approvals |
| P1 — trước bảng cuối | Crosswalk đề cương–protocol–amendment cho contrasts/δ/Holm và threshold precedence | Một danh sách estimands có thẩm quyền, machine-readable cho evaluator; không đổi theo kết quả |
| P1 — trước evaluator | Pin lock amendment đúng và chặn thiếu ID/labels/method identity | Full census + exact paired joins + thresholds_used có hash; không tự refit test |
| P1 — tiếp tục execution | Theo dõi B1-shuf, giải quyết phạm vi B2-rand seed44, quản lý B3 theo scope đã duyệt | Mỗi arm/seed có output và acceptance riêng hoặc ghi pending/partial rõ |
| P2 — song song, không chờ B3 | Chuẩn bị ba-seed anchors và Qwen complementarity/routing | Score/features/folds/thresholds/provenance; expert hằng/random và chi phí cùng bảng |
| P2 — song song khi có cases | Chấm mù retrieval/error/label audit theo đúng quota | Form thật, blinding/adjudication, κ và conditional-analysis outputs |
| P2 — trước viết Methods | Deviation register: data, graph, scoring/seed, model quantization, B3, runtime và test exposure | Mỗi thay đổi có ngày/lý do/ảnh hưởng/authority/phân loại; không gắn retrospective prospective status |
| P3 — sau input/result acceptance | Sinh Bảng A–D/hình/full-clean/cost và gói tái lập | Mọi số truy về record/version/lock, report không chỉnh tay |

Không mở một vòng GPU/rerun mới chỉ vì tài liệu chưa đồng nhất. Sửa diễn giải, provenance và evaluator offline trước; chỉ rerun đúng arm có lỗi cấu hình/score/cache thật được chứng minh. Không cần lặp lại tests toàn bộ cho việc sửa tài liệu này. Khi sửa implementation ảnh hưởng gate/renderer/stats, chạy tests targeted và bộ bắt buộc trước release theo quy trình repo.

## 9. Những tuyên bố nên dùng và nên tránh lúc này

**Có thể nói:** “Đang triển khai nghiên cứu tái lập có chẩn đoán theo đề cương, với một số điều chỉnh được ghi riêng. Đã có nhiều arm full-census và một số acceptance đầy đủ theo contract từng run; B3 mới và các phân tích offline/human-review còn đang hoàn thiện.”

**Chưa có cơ sở nói:** “Đã tuân thủ đầy đủ đề cương”, “mọi arm cùng runtime mới”, “hai review B3 đã xong”, “toàn bộ test đã xong”, “mọi kết quả là preregistered độc lập”, “B3 mới đã chứng minh retrieval/patch-pair hiệu quả”, hoặc “p>0,05 chứng minh không có lợi ích”.

**Đánh giá cuối:** tiếp tục công việc được; ưu tiên sửa điểm đi trước review thật, thống nhất giao thức phân tích và hoàn thành RQ5/RQ6. Những việc đang làm về source/runtime là cần thiết để có dữ liệu đáng tin, nhưng không nên để việc xây một pool B3 thay thế toàn bộ kế hoạch diagnostic replication.

## 10. Tài liệu đối chiếu trực tiếp

- [Đề cương DOCX](OSF_response/De_cuong_nghien_cuu_GRACE_hop_nhat.docx), [phản hồi OSF](OSF_response/PhanhoiHieuDungVeDangKyOsf.pdf), [PDF amendment](OSF-update-20261107.pdf).
- [Preregistration](../preregistration.md), [protocol](../configs/protocol.yaml), [arms](../configs/arms.yaml), [change log sau đăng ký](../CHANGES_AFTER_PREREG.md).
- [Threshold audit](../Runs-management/threshold_audit_20261108/final/audit.json), [B1-full acceptance](../Runs-management/run_handoff_20261108/b1_full_runtime_acceptance.json), [Step 0 lịch sử](../Runs-management/step0_diagnostic/README.md).
- [B3 execution plan](B3_NEW_ALGORITHM_EXECUTION_PLAN_20261108.md), [audit nguồn case đầu tiên](../Runs-management/b3_verified_patch_v1/independent_fifth_audit_20261108_162642/AUDIT_REPORT.md), [dossier case08 v2](../Runs-management/b3_verified_patch_v1/g1_source_investigation_20261108_v2/case_08_ffmpeg_can_safely_read_8614_26054/), [pool manifest v4 được quan sát](../Runs-management/b3_verified_patch_v1/release_20261108_v4/pools/pool_manifest.json).

Các báo cáo/hồ sơ trong working tree có thể được cập nhật sau snapshot; không xem việc thay đổi sau đó là bằng chứng audit này đã kiểm phiên bản mới. Báo cáo này không thay chữ ký người duyệt hoặc phê chuẩn thay đổi phương pháp.
