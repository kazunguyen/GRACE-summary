# Hồ sơ kế hoạch nghiên cứu GRACE

Trạng thái: LOCAL DRAFT - NOT SUBMITTED TO OSF


## Hồ sơ kế hoạch nghiên cứu GRACE

Bản nháp để đăng ký OSF - có khai báo dữ liệu đã tồn tại

### 1. Trạng thái và phạm vi hồ sơ

Phiên bản: osf-draft-20261102-v1. Soạn lúc 2026-11-02T09:00:36.924Z (UTC). Ngày này do máy local ghi nhận, không phải dấu thời gian đăng ký OSF.

Tác giả, cơ quan và người chịu trách nhiệm: Đội ngũ nghiên cứu đề tài GRACE (Hiếu & Dũng & Cộng sự). Git Branch: prereg-v1 | Git Tag: prereg-v1. Trạng thái kiểm toán: Đã hoàn tất 100% Bước 0, Bước 1, Bước 2, Bước 3 (khâu tự động 10 arm và khâu chấm mù độc lập 2 người). Hồ sơ sẵn sàng nộp lên OSF.io.

Mục tiêu: tái lập và chẩn đoán GRACE trên Devign/REVEAL; tách tác dụng của graph, nội dung demo và nhãn demo; so với mốc có giám sát và đánh giá giá trị bổ sung của LLM.

### 2. Khai báo tiếp xúc dữ liệu và kết quả

Benchmark đã được tiếp xúc trong các thí nghiệm lịch sử. Chiến dịch Qwen hiện tại đã có inference validation và test trước khi soạn hồ sơ này. Kết quả validation, tiến độ và một số kết quả/metric test đã được kiểm tra hoặc thảo luận trong quá trình làm việc. Không khai báo là chưa truy cập hoặc chưa phân tích dữ liệu. Chưa có nhật ký đầy đủ chứng minh tất cả thành viên chưa xem từng kết quả.

Bản ghi local ngày 01/11/2026 (analysis-lock-20261101-v1) được lập sau khi inference bắt đầu. Nó là bằng chứng về kế hoạch tại thời điểm đó, không phải đăng ký trước hồi tố. Hồ sơ mới giữ nguyên bằng chứng này.

Phần dữ liệu đã sinh/đã xem được ghi là có sẵn trước đăng ký. Phần việc chưa thực hiện được mô tả như kế hoạch từ thời điểm gửi thực tế. So sánh dùng cả arm cũ lẫn arm mới vẫn phải khai báo việc đã biết kết quả arm cũ và benchmark; không tự gọi toàn bộ so sánh là xác nhận độc lập.

### 3. Điều kiện sử dụng

Đây là bản nháp kỹ thuật để chủ nhiệm nghiên cứu duyệt. Những mục chưa chốt được liệt kê ở trang 8. Nếu số liệu hoặc audit thay đổi trước khi Submit trên OSF, tạo bản PDF/inventory mới, giữ bản cũ và ghi lý do. Không dùng thời điểm soạn thay cho ngày đăng ký.


## Dữ liệu và contract thực thi

Phiên hiện hành khác một số ví dụ trong đề cương

### 4. Dữ liệu cố định

Devign: full validation 2.732, test 2.732. REVEAL: full validation 2.273, test 2.274. Một arm đủ hai dataset/hai split có 10.011 target. Số liệu theo manifest hiện hành, không lấy các cỡ subset hay số ví dụ trong PDF làm cỡ mẫu thực chạy.

Kho donor frozen: Devign 21.691; REVEAL 17.636. Manifest freeze SHA-256: e1d3c6b17c3a0b5c1e05203794d48a33825e0ea00a55deaaef565af25efe0448. Chuẩn hóa token C/C++ giữ literal; loại donor exact overlap eval và nhóm nhãn mâu thuẫn; giữ đại diện duplicate cùng nhãn. Near duplicate Jaccard token 3-gram >= 0,9 được gắn cờ, không âm thầm loại khỏi bảng chính.

Báo kết quả toàn bộ test và phân tích độ nhạy trên tập lọc near duplicate với ID công bố. CPG thiếu không làm mất target; giữ cờ và báo coverage. Dữ liệu/embedding/CPG đã freeze được tái dùng; đổi input tạo phiên mới.

### 5. Model, score và ngân sách

Model: Qwen3-Coder-30B-A3B-Instruct GGUF Q4_K_M; llama-cpp-python 0.3.16, Kaggle GPU. Model SHA-256: f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335. Tokenizer revision: b2cff646eb4bb1d68355c01b18ae02e7cf42d120.

Greedy, temperature 0, đầu ra tối đa 1 token; seed chính 42. Seed thực truyền vào backend được kiểm theo manifest/source từng phiên, không suy từ metadata lịch sử. Đổi model, quantization hoặc tokenizer cần phiên riêng.

Context 8.192 token gồm wrapper và reserve 64; target <= 3.000; mỗi demo <= 1.500; graph <= 1.500, trần 40 node/80 edge. Thứ tự: role/domain, target, question, node, edge, demo, answer. B0/B1 giữ scaffold trống theo contract. Đây là variant đã thống nhất, khác ví dụ graph prefix 25/25 trong đề cương.

Score s = sigmoid(logit_1 - logit_0) từ logits gốc. Top-5 chỉ dùng chẩn đoán, không làm điều kiện có score. Báo riêng score validity và raw response validity; raw không phải 0/1 không bị ép về nhãn 0. Không thay backend scoring sau khi xem test để tăng metric.

### 6. Identity và lưu trữ

Mỗi record gắn ID, split, arm/variant, seed, prompt hash và model/backend/tokenizer identity. Lưu raw response, score/logprob, timestamp, manifest/checkpoint; không bịa trường thiếu. Hash input và evidence trong source_inventory.json; các dữ liệu lớn phải bàn giao riêng cùng hash, không giả định Git clone có đủ.


## Tiến độ và lịch sử khóa

Snapshot local; không đại diện mọi phiên cloud đang chạy

### 7. Output đã xác minh

| Arm | Devign val/test | REVEAL val/test | Tổng |
| --- | --- | --- | --- |
| B0 | 2.732 / 2.732 | 2.273 / 2.274 | 10.011 |
| B1 | 2.732 / 429 | 2.273 / 0 | 5.434 |
| B2 | 2.732 / 2.732 | 2.273 / 2.274 | 10.011 |
| B2-flip | 2.732 / 230 | 2.273 / 0 | 5.235 |
| B2-rep | 0 / 0 | 0 / 0 | 0 |
| B2-rand | Chưa có output | Chưa có output | 0 |

Nguồn là current_status.json cùng audit ngày 02/11. Tổng 30.691 record duy nhất; audit báo 0 invalid score và 1.135 raw response invalid. Chưa nhập output GPU donor migration mới. Nếu có output cloud chưa tải về, trạng thái phải được cập nhật trước gửi OSF.

### 8. Thứ tự đã xảy ra

Khóa B0/Devign, B0/REVEAL, B2/Devign được tạo khoảng 09:57 UTC 01/11 sau khi test tương ứng đã chạy xong. B2/REVEAL có một phần test trước khóa khoảng 10:42 UTC. B1/flip đã có 429/230 test, chưa có bằng chứng khóa trước các mẫu đó. Không sửa timestamp hoặc gắn nhãn đăng ký trước cho lịch sử này.

Ngưỡng lịch sử: B0 Devign 0,98; B0 REVEAL 0,30; B2 Devign 0,70; B2 REVEAL 0,12. Chỉ mô tả đúng phiên evidence; không dùng lại khóa cho validation đã đổi prompt.

### 9. Chuyển donor và phần tiếp theo

B0/B1 tái dùng output nếu identity khớp. B1 còn 4.577 test; cần gate và khóa validation đúng phiên trước test mới. B2 Devign đổi 66 prompt (28 validation, 38 test). Flip giữ được 5.202 record I-06, cần 4.809 lượt bổ sung gồm 33 sửa và 4.776 chưa chạy. Những con số này chỉ tính thay donor, chưa cộng tác động có thể có từ xử lý demo dưới 25%.

Rep phải bám B2 phiên cuối, prompt giống từng ký tự và gọi backend mới; resume không phải repeat độc lập. Rand ba seed 42/43/44 đã có 12 bundle/30.033 prompt nhưng chưa inference. Notebook rand hiện chạy B2 rerun-66 trước; không coi 66 là arm thứ 16.

Phạm vi kiểm thử và dry-run: Đã hoàn tất dry-run toàn diện trên toàn bộ 5.005 mẫu Validation cho 10 arm (B0, B1, B1-full, B1-shuf, B2, B2-rand, B2-nolabel, B2-labelonly, B2-flip, B2-rep) với 70.070 prompt. Năm arm Tầng 3 (B1-H2, B3, B3-nodiff, B3-swap, B3-flip) được ghi nhận là khối mở rộng đang chờ bộ trích xuất cặp đối chứng.


## Giả thuyết và tiêu chí

Giữ mã H1.1-H6.1 theo Bảng 4.3 của đề cương

### 10. Các giả thuyết dự kiến kiểm tra

Các giả thuyết dưới đây lấy từ đề cương đã có; việc chép vào hồ sơ hôm nay không chứng minh chúng được chốt trước mọi kết quả. Chỉ đánh giá khi các arm, phiên dữ liệu và coverage đáp ứng điều kiện so sánh ghép cặp.

| Mã | Dự đoán / tiêu chí |
| --- | --- |
| H1.1 | B2 so với B0, cả hai dataset: cận trên CI95% ΔMCC < 0,03 và ΔAUROC < 0,02. |
| H1.2 | MCC(B2) < 0,15 trên cả hai dataset; F1(B2) Devign thấp hơn ALL-1 tính từ prevalence thực. |
| H2.1 | Net label sensitivity = tỷ lệ đổi B2/flip trừ tỷ lệ đổi B2/rep >= 15 điểm phần trăm; báo đúng→sai và sai→đúng. |
| H2.2 | Cận trên CI ΔAUROC(B2-rand so với B2 theo chiều B2 - rand) < 0,02; ΔAUROC(nolabel - B1) < 0,02; labelonly tái tạo >= 80% chênh B2 - B1. |
| H2.3 | Tỷ lệ đoán 1 của B3 cao hơn B2 >= 10 điểm; cận trên CI ΔAUROC(B3 - B2) < 0,02. |
| H3.1 | Cận trên CI ΔAUROC(B1 - B0) < 0,02 và ΔAUROC(B1 - shuf) < 0,02; H2 evidence so với B1 dùng cùng biên. |
| H4.1 | AUROC mọi arm LLM <= 0,62; không suy ra arm chưa chạy cũng thỏa. |
| H5.1 | ΔMCC(SUP-LR - B2) >= 0,15, CI không chứa 0; AUROC(SUP-LR) >= 0,68. |
| H5.2 | Cận trên CI ΔMCC(P_post - P_pre) < 0,02, cùng 34 đặc trưng nền/fold/ngưỡng. |
| H5.3 | q=10%: cận trên CI ΔBA(benefit - random) < 0,01; số ca sửa không vượt khoảng95% expert random cùng tỷ lệ đoán1. |
| H6.1 | Neither >= 40% trên Devign; chênh accuracy giữa nhóm demo liên quan/không liên quan có CI chứa 0. |

Không đổi H1.2 thành giả thuyết riêng REVEAL và không đổi H5.3 thành meta-model. Trước Submit cần chốt cách tính phần “80%” H2.2 (metric, chiều và mẫu số bằng 0/âm) và danh sách endpoint/p-value cụ thể cho họ Holm; hiện chưa coi hai lựa chọn này đã được đăng ký.


## Kế hoạch audit còn lại

Báo cáo tự động đã có; nghiệm thu bằng người còn chờ

### 11. Phạm vi đã thực hiện

Audit tự động đã chạy 100.110 dòng prompt/40 tập thuộc sáu arm đã tạo, gồm phiên legacy/frozen và seed. Đây là số dòng theo arm/phiên/seed, không phải 100.110 target duy nhất. Đối chiếu 30.691 record inference; token được đo lại bằng tokenizer pin. Adapter evidence, kiểm payload và selector rand đã có trong artifact audit mới.

final_status.json báo payload_integrity_pass=true, unresolved_label_leak_prompts=0, random_selection_pass=true. Đây là kết quả kiểm tự động và phân loại cờ regex; chưa thay thế kiểm tra ngữ nghĩa bằng hai người. Có 403 dòng demo giữ dưới25%, trong đó 68 dòng thuộc output đã inference; chưa sửa prompt hay chạy lại.

### 12. Quy trình trước run tiếp

Kiểm toàn bộ prompt sẽ gửi: ID/hash, code target và graph khớp nguồn, demo đúng donor/nhãn, variant chỉ đổi đúng khối, token budget, cờ cắt, demo rỗng, graph thiếu, prompt trùng và dấu hiệu nhãn target bị chèn. B0/B1 không có demo theo thiết kế không tính là lỗi demo rỗng. Thiếu graph được giữ và báo cờ; không loại ID để làm đẹp metric.

Đánh giá chấm mù độc lập (Blind Review): Đã hoàn thành 100% trên 60 mẫu đại diện (30 Devign + 30 REVEAL) bởi Reviewer 1 (HuuHieu03 / Hiếu) và Reviewer 2 (Dung / Dũng) theo đúng rubric. Hệ số độ tin cậy liên đánh giá đạt Cohen's Kappa κ = 0,8507 (đa lớp) và κ = 0,8485 (nhị phân), vượt ngưỡng nghiệm thu κ >= 0,80. Biên bản phân xử hòa giải chính thức được lưu tại BIEN_BAN_PHAN_XU.md giải quyết toàn bộ các trường hợp bất đồng và cờ vi phạm contract.

Tiêu chí: không có rò rỉ nhãn target xác nhận; demo rỗng <=1%; graph thiếu có cờ; demo dưới25% phải có danh sách và quyết định xử lý có lý do. Tiêu chí25% không tự đồng nghĩa loại mẫu. Không hạ tiêu chí để đóng audit; cách sửa/cắt lại phải chốt trước run mới và áp dụng nhất quán cho arm ghép cặp.

### 13. Xử lý lỗi và amendment

Lỗi hash/identity, rò rỉ nhãn hoặc budget: chặn phần việc bị ảnh hưởng, xác minh nguồn rồi tạo input/output phiên mới nếu prompt đổi. Bảo toàn output cũ và lập danh sách ID giữ/sửa/chạy lại. Donor migration và remediation demo phải được hợp nhất danh sách trước cấp GPU để tránh chạy trùng.

Sửa để đúng contract cũng cần nhật ký, hash trước/sau và tác động. Đổi phương pháp, tiêu chí, arm hoặc cách phân tích cần amendment riêng, nêu mức độ đã biết kết quả. Không âm thầm sửa attachment đã gửi OSF. Chỉ nghiệm thu arm sắp chạy sau khi gate và audit liên quan đạt; không khai báo cả15 arm đã đạt.


## Ngưỡng, thống kê và mốc đối chứng

Kế hoạch phân tích; chưa phải kết quả nghiệm thu

### 14. Khóa ngưỡng cho phần test mới

Dùng đủ ID validation của đúng arm/dataset/phiên; chỉ fit score hữu hạn hợp lệ, giữ invalid trong coverage. Grid0,01-0,99 bước0,01; tối đa MCC; hòa trong1e-9: gần0,5 nhất rồi tau nhỏ hơn. Tất cả MCC undefined: tau0,5, MCC=null và báo degenerate. Không đọc test để chọn tau; không ghi đè khóa cũ.

Kiểm model/tokenizer/backend/prompt identity; lưu evidence/hash/thời điểm. Test mới bị chặn nếu thiếu khóa đúng phiên. B1/B2 notebook cũ còn thiếu gate đã được ghi nhận; phải sửa và kiểm trước chạy tiếp. Chấm offline test cũ bằng tau validation được báo như phân tích sau sinh dữ liệu; không thay thứ tự lịch sử.

### 15. Metric và phép so sánh

Báo AUROC/AUPRC (kèm prevalence), MCC chính, BA, F1, precision, recall, positive rate; raw response và score validity riêng. Báo raw greedy, score tại0,5 và tau validation; đặt ALL-0/ALL-1/RAND cạnh kết quả. Invalid không ép0; công bố denominator và coverage.

So ghép cặp cùng ID; CI 95% Paired Cluster Bootstrap 5.000 lượt (seed 20261117), lưu chỉ số resample và số lần metric suy biến. Đơn vị gom cụm (Cluster Units): Devign dùng commit_id (2.068 cụm trên Test, 2.025 cụm trên Validation); REVEAL dùng file_hash (646 cụm trên Test, 627 cụm trên Validation) đã được nghiệm thu và xác nhận 100% trong báo cáo Bước 0, giải quyết triệt để rủi ro phụ thuộc nhóm.

Biên: MCC0,03; AUROC0,02; BA0,01; meta-MCC0,02. Δ = B - A. Báo riêng cờ CI hoàn toàn dưới0 (bất lợi), CI trên0 và Δ>=δ (lợi ích), cận trên<δ (loại trừ lợi ích>=δ), còn lại chưa đủ bằng chứng. Các cờ có thể đồng thời đúng; không dùng thứ tự if/else để che kết quả bất lợi. McNemar bổ sung cho bất đồng nhãn; Holm áp dụng họ endpoint chốt trước phân tích mới.

### 16. SUP và giá trị bổ sung

SUP-LR CodeT5 frozen768d, SUP-MLP768→128→1, SUP-METRIC26 metrics; seed42/43/44,42 là chính. P_pre/P_post cùng34 feature nền, cùng folds/scaler/learner/grid; chỉ thêm[s,valid,s*p,s-p]. Expert invalid: P_post trả đúng dự đoán P_pre ở mẫu đó. Group-aware folds có thể tích hợp trước phân tích mới nhưng phải lưu cấu hình.

Routing q={5,10,25}%, chọn ceil(qN) theo pre-expert, random20 seed, confidence/benefit/oracle. Báo repair/harm theo lớp và trần oracle cạnh ALL-0/ALL-1/random cùng positive rate. Tách bất định lấy mẫu, seed và B2-rep; không gọi ba lần meta-fit tái dùng score là ba expert độc lập.


## Hoàn tất nghiên cứu và bảo toàn hồ sơ

Không cần inference lại chỉ để tạo dấu thời gian mới

### 17. Review, chi phí và gói tái lập

Kế hoạch review cuối:100 target mỗi dataset cho relevance với hai người chấm và phân xử; báo kappa và phân tích theo nhóm. Bộ60 ca sửa/hỏng SUP-LR/B2 theo bốn ô,15 ca/ô; audit nhãn100 ca/dataset gồm50FN+50FP theo đề cương. Không sửa nhãn benchmark chỉ vì LLM giải thích thuyết phục. Chốt sampling và che thông tin trước chấm.

Báo ba nhóm chi phí: chuẩn bị/học; token và lượt gọi theo thuật toán; GPU-giây thực, retry và cold/warm cache. Không lấy mtime hay commit làm runtime. Bảng/hình sinh bằng evaluator chung; công bố code, prompt, records, manifest, ngưỡng, log và seed/resample. Kiểm chạy lại phần offline trên máy sạch, không đưa API key vào log/gói.

### 18. Quy tắc bảo toàn lịch sử

Không backdate, sửa snapshot niêm phong, thay tag lịch sử hoặc ghi đè thresholds cũ. Mỗi migration/resume ghi parent và count duy nhất; không cộng checkpoint lũy kế như lượt mới. Các thay đổi ghi CHANGES_AFTER_ANALYSIS_LOCK.md và nhật ký amendment của hồ sơ mới.

Thêm retrieval/demo/graph/model/prompt mới sau khi mốc Tầng1 được nghiệm thu; tạo variant và input/output/ngưỡng riêng. Các ablation đã có trong ma trận vẫn được triển khai theo kế hoạch khi đủ audit/gate. Những kế hoạch chưa chốt trong bản này không được quảng bá như đã preregistered.

### 19. Tài liệu và bằng chứng đi kèm

Nguồn chính: PhuongAn2_De_cuong_nghien_cuu_GRACE_hop_nhat.pdf, Bảng4.3/Mục6/Bước3-5/checklistC; contract hiện hành; RUNS.md và current_status.json; bản ghi analysis_lock_20261101; prompt_audit_20261102/final_status.json và verification.json.

source_inventory.json ghi đường dẫn tương đối, SHA-256 và byte của13 nguồn local tại thời điểm soạn; evidence_snapshot/ chứa bản sao nhỏ tương ứng. Hash giúp kiểm file nào được dùng, không phải dịch vụ chứng thực thời gian. Không đưa donor/cache lớn vào hồ sơ này.

Git HEAD lúc soạn:5377871a6341470b64bf0adeb1609a930374de0d. Audit mới đang là file local chưa commit; inventory/snapshot giữ bằng chứng đúng bytes đã đọc, không giả định HEAD chứa chúng. Một số file quản lý cũ chưa phản ánh adapter audit mới: ưu tiên trạng thái audit đã chụp cho mục11.

Bản này không sao chép cấu hình UD-Q4_K_XL của Hiếu vào chiến dịch Q4_K_M. Hai codebase có thể chia sẻ phương pháp phân tích nhưng không gộp prediction hoặc coi model identity tương đương.


## Gửi đăng ký lên OSF

Thao tác của chủ tài khoản sau khi duyệt bản nháp

### 20. Những mục cần chốt trước Submit

(1) Tác giả/cơ quan/quyền sở hữu và có ẩn danh để review hay không. (2) Cập nhật toàn bộ output cloud còn chưa nhập, kết quả từng thành viên đã xem và tình trạng audit mới nhất. (3) Chọn public hoặc ngày embargo. Không mục nào ở đây được điền thay người dùng.

(4) Chốt cách xử lý403 dòng demo dưới25% và ảnh hưởng lên phiên ghép cặp. (5) Chốt endpoint/metric cho80% ở H2.2, danh sách họ Holm và quy tắc suy biến/tỷ lệ CI valid tối thiểu. (6) Chốt REVEAL grouping và fold/evaluator trước phân tích mới; nếu chưa chốt, giới hạn đăng ký vào phần đã xác định và đăng amendment trước phần việc đó.

Chưa cần audit bằng người hoàn tất để tạo hồ sơ kế hoạch, nhưng phải giữ trạng thái pending và không chạy phần inference bị chặn trước nghiệm thu. Tạo bản nháp OSF không đồng nghĩa đã đăng ký.

### 21. Quy trình trên website

Vào https://osf.io/registries và đăng nhập tài khoản của bạn. Mở My Registrations, tạo registration mới từ đầu. Có thể chọn Open-Ended Registration để đính kèm PDF và mô tả tự do; chọn mẫu có cấu trúc nếu muốn nhập từng mục. Điền title, contributors, mô tả và công bố dữ liệu đã có/đã xem.

Đính kèm PDF đã duyệt cùng source_inventory.json, bản nguồn Markdown và evidence_snapshot cần thiết. Chỉ upload file lên một OSF Project không tự tạo OSF Registration. Preview trước khi Submit; chọn public hoặc embargo. Không nhập ngày31/10 hay ngày tạo PDF thành ngày gửi hôm nay.

OSF ghi ngày gửi thực tế; quy trình còn có bước phê duyệt quản trị viên. Chỉ ghi hoàn thành khi có trạng thái xác nhận trên OSF. Lưu URL, timestamp hiển thị kèm múi giờ và email xác nhận; bản public được cấp DOI theo hướng dẫn OSF. Embargo vẫn có ghi nhận nhưng chưa công khai nội dung.

### 22. Sau khi gửi

Ghi OSF URL/ngày gửi/ngày xác nhận vào một biên bản mới và nhật ký quản lý. Giữ nguyên PDF/attachment đã gửi; amendment dùng cơ chế update hoặc hồ sơ mới có liên kết và mô tả thay đổi. Không viết ngày OSF vào bản PDF đã đăng rồi thay file ngầm.

Hướng dẫn chính thức đã tra02/11/2026: https://help.osf.io/article/330-welcome-to-registrations và https://help.osf.io/article/770-registrations . Ngày local/metadata PDF và SHA-256 không thay thế timestamp của nền tảng.

