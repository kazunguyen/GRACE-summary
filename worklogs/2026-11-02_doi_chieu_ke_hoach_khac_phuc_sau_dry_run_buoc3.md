---
id: "plan-review-20261102-01"
title: "Đối chiếu kế hoạch khắc phục GRACE với hiện trạng sau dry-run Bước 3"
author: "Codex (trợ lý AI)"
author_type: "AI assistant"
requested_by: "Người dùng trong chat"
recorded_at: "2026-11-02T18:22:02.145+07:00"
timezone: "Asia/Bangkok"
work_date: "2026-11-02"
record_type: "current_state_assessment"
status: "completed_assessment_with_pending_remediation"
overall_step3_status: "incomplete"
evidence_verified_at: "2026-11-02T18:22:02.145+07:00"
artifact_verification_at: "2026-11-02T17:52:40.257851+07:00"
compared_plan: "ke_hoach_tong_hop_va_khac_phuc_grace.md"
compared_plan_sha256: "e7d3602cbc9a1d54d5fbfd47ab172d15082e46b8ccd411816b03a27a1c151164"
repository: "kazunguyen/GRACE-summary"
branch: "baseline-unified"
git_head_at_review: "5377871a6341470b64bf0adeb1609a930374de0d"
working_tree_state: "dirty; includes local audit/dry-run and documentation not committed at review"
scope: "Local code and artifacts; compare plan, Step 3 evidence and remaining readiness gates"
verification_method: "Read source/artifacts; compare stored hashes; inspect notebook gate calls; reproduce McNemar edge case; count blank review sheets"
new_inference_performed: false
new_thresholds_fitted: false
historical_snapshots_modified: false
---

# Đối chiếu kế hoạch khắc phục GRACE với hiện trạng sau dry-run Bước 3

recorded_at là thời điểm lập báo cáo; evidence_verified_at là thời điểm kiểm tra nguồn trong lượt này. artifact_verification_at là mốc verifier của dry-run đã lưu, không phải thời gian bắt đầu/kết thúc inference. Đây là báo cáo đối chiếu hiện trạng, không phải biên bản xác nhận đã thực hiện các hành động đề xuất trong kế hoạch.

## 1. Kết luận tại thời điểm kiểm tra

[Kế hoạch tổng hợp](../ke_hoach_tong_hop_va_khac_phuc_grace.md) chưa phản ánh đủ phần kỹ thuật Bước 3 vừa hoàn tất. Hiện đã có hậu kiểm 100.110 dòng prompt/40 tập và dry-run mới 70.070 dòng full validation/28 tập cho **10 arm**. Kết luận cuối là **28/28 tập đạt trong phạm vi kiểm tự động**. Adapter, bộ dựng/dry-run chung, kiểm token, donor/random và hồ sơ chấm tay đã được làm; không còn đúng nếu coi toàn bộ những phần này là chưa bắt đầu.

Tuy nhiên, **hoàn thành lượt audit/dry-run hiện có không đồng nghĩa hoàn thành toàn bộ Bước 3**. Artifact mới vẫn ghi step3_complete=false: thiếu B1-H2 và bốn arm B3, chưa có hai người đọc/chấm thật. Mười arm mới đạt dry-run validation không có nghĩa đã có bundle test/runner GPU/score/ngưỡng cho mọi arm đó.

Những lỗi McNemar, evaluator tự fit lại ngưỡng, notebook B1/B2 thiếu gate, thiếu score rep/meta và chưa đăng ký OSF vẫn còn. Không có GPU inference hoặc khóa ngưỡng mới phát sinh từ đợt dry-run. Các số 30.691 output và bốn khóa lịch sử vẫn là mốc local hiện có, không suy ra tiến độ cloud chưa được nhập.

## 2. Những tiến triển mới của Bước 3 so với kế hoạch

| Nội dung | Kế hoạch đang ghi/đề xuất | Hiện trạng được kiểm | Trạng thái chính xác |
|---|---|---|---|
| Adapter evidence | Còn phải sửa lỗi KeyError trong prompt_audit.py | Có adapt_evidence trong audit_prompt_integrity.py để đưa bundle phẳng vào schema kit | Đã có giải pháp; không cần sửa module kit chỉ để đáp ứng đúng đường dẫn đề xuất |
| Audit prompt hiện hữu | Đề cập adapter và 60 mẫu nhưng chưa có kết quả đầy đủ | Hậu kiểm 100.110 dòng/40 tập của sáu arm, 30.691 output được đối chiếu | Hoàn thành audit tự động trong phạm vi artifact cũ; không chứng minh audit trước inference |
| Dựng probe/dry-run chung | Chưa ghi nhận bộ chạy full validation mới | dry_run_full_validation.py dùng render_arm/audit_rows, tokenizer pin và graph 40/80 | Đã triển khai CPU; chưa thay runtime notebook |
| Phạm vi arm đã dựng | Không ghi nhận mở rộng từ sáu lên mười | B0, B1, B1-full, B1-shuf, B2, B2-rand, B2-nolabel, B2-labelonly, B2-flip, B2-rep | Đã có dry-run validation 10/15 arm |
| Seed và cỡ mẫu | Kế hoạch nêu full validation nhưng chưa có artifact dry-run này | B1-shuf/rand ba seed 42/43/44, arm còn lại seed42; 14 tổ hợp arm/seed × hai dataset =28 tập; 14×5.005=70.070 dòng | Không phải 70.070 target khác nhau; đây cũng không phải14 khóa ngưỡng |
| Kết quả cuối | Chưa có | 0 lỗi dựng; raw27 pass+1 needs_review; sau truy nguồn thành28 pass, không còn cờ nhãn chưa giải quyết | Giữ detector gốc và kết luận nguồn riêng; không xóa cờ để báo xanh |
| Cảnh báo Label ở shuf REVEAL seed44 | Chưa đề cập | Truy donor frozen reveal:train:664, CALL30064771247 cho target reveal:validation:1629; chuỗi hiển thị Label bị cắt ở node preview | Đã giải quyết cảnh báo tự động bằng bằng chứng nguồn, không thay người chấm |
| Demo/graph | Yêu cầu demo không bị cắt cụt quá đơn giản | 176 dòng cờ demo,390 dòng thiếu graph trong dry-run; danh sách hợp nhất562 do bốn dòng giao nhau | Giữ cờ từng mẫu; mọi tập có tỷ lệ demo rỗng theo quy ước ≤1%, cao nhất24/2.732=0,878% |
| Chính sách graph thiếu ở shuf | Chưa mô tả rõ | Giữ3 Devign+27 REVEAL target thiếu graph, graph trống/cờ missing ở cả ba seed | Không drop ID hoặc âm thầm thay graph; đã được ghi trong USER_DECISIONS |
| Kiểm thử | Chỉ nêu test gate còn fail | Verifier ghi20 test probe+4 test bộ chạy pass | Chỉ là các bộ test này; chưa tuyên bố toàn bộ test suite xanh |
| Chấm tay | Đề xuất tạo mẫu | Đã có60 prompt đúng phiên mới,30/dataset, packet/rubric và hai CSV trống | Chuẩn bị xong; kiểm thực tế mỗi CSV60 dòng,0 tên reviewer và0 verdict |
| Năm arm còn thiếu | Chưa nêu blocker cụ thể | B1-H2 thiếu evidence và bằng chứng giới hạn nguồn; B3/nodiff/swap/flip thiếu cặp demo và Key difference khi cần | Vẫn blocked, không dựng đầu vào giả |

Nguồn: [báo cáo dry-run](../Runs-management/dry_run_validation_20261102/KET_QUA.md), [summary gốc](../Runs-management/dry_run_validation_20261102/summary.json), [final status](../Runs-management/dry_run_validation_20261102/final_status.json), [verification](../Runs-management/dry_run_validation_20261102/verification.json), [blocked arms](../Runs-management/dry_run_validation_20261102/blocked_arms.json), [quyết định phạm vi](../Runs-management/dry_run_validation_20261102/USER_DECISIONS.json).

Không cộng 100.110 dòng hậu kiểm với70.070 dòng dry-run thành số lượt inference. Hai bộ có mục tiêu và phạm vi khác nhau; các con số403 cờ demo/68 đã inference thuộc bộ hậu kiểm cũ,176 cờ demo thuộc dry-run validation mới, không phải các số mâu thuẫn hay số lượt GPU cần chạy lại.

## 3. Đối chiếu sáu thành phần khắc phục của kế hoạch

### 3.1. Full validation,14 ngưỡng và hồ sơ OSF

- Dùng đủ validation đúng phiên là yêu cầu đã có trong validation_lock.py, không phải khả năng mới chỉ xuất hiện sau khi tạo script lock_full_validation_thresholds.py. Bốn khóa B0/B2 hiện tại đã dùng full validation.
- Hiện chưa có scripts/lock_full_validation_thresholds.py hay configs/thresholds.json ở root. Khóa canonical thực tế nằm tại [Runs-management/thresholds.json](../Runs-management/thresholds.json), chứa bốn entry; không đổi schema/vị trí một phía vì helper/notebook đang phụ thuộc.
- Chưa thể khóa14 tổ hợp mà kế hoạch liệt kê: rep chưa có score; P_pre/P_post chưa có output của chiến dịch này. Full validation5.005 là số target của **một arm** qua hai dataset, không phải một bộ score chung dùng cho mọi arm.
- B1 đã đủ validation có thể tính khóa khi được thực hiện có chủ đích và identity khớp. B2/flip donor mới phải cập nhật score của validation đổi prompt trước khóa đúng phiên. Dry-run không sinh score nên không thay thế bước này.
- Không dùng tau B2 gán cho rep, hoặc chép tau từ subset600/cấu hình Hiếu sang full-validation Q4_K_M. Bảng JSON trong kế hoạch chỉ là minh họa trộn nguồn, chưa phải kết quả tính.

| Khóa thực có | tau | Validation expected | Giờ khóa UTC |
|---|---:|---:|---|
| B0/Devign | 0,98 |2.732|2026-11-01T09:57:16.195324+00:00|
| B0/REVEAL |0,30|2.273|2026-11-01T09:57:16.444338+00:00|
| B2/Devign |0,70|2.732|2026-11-01T09:57:17.272790+00:00|
| B2/REVEAL |0,12|2.273|2026-11-01T10:42:29.297068+00:00|

Kế hoạch dùng0,08/0,44 cho B0 và0,88/0,74 cho B1 không được coi là ngưỡng full validation đã xác minh ở repo này. Đoạn pick_tau_mcc đề xuất cũng chưa giữ đầy đủ kiểm coverage/identity, tie tolerance1e-9 và degenerate=null mà helper hiện có đã xử lý. Không thay helper tốt hơn bằng đoạn minh họa giản lược.

Đã có [hồ sơ OSF nháp](../Runs-management/osf_registration_draft_20261102/README.md) cùng PDF/Markdown/inventory, nhưng chưa có bằng chứng gửi đăng ký OSF. PDF nháp được soạn trước dry-run mới, vẫn mô tả sáu arm và chín arm thiếu: **cần tạo phiên nháp cập nhật10 arm/năm arm blocked trước Submit**; không sửa snapshot lịch sử cho giống hiện trạng. Trong lượt báo cáo này chưa cập nhật PDF hoặc gửi OSF.

Tuyên bố Zero-Test-Exposure trong kế hoạch cần đổi thành mô tả chính xác: fit tau không đọc test, nhưng lịch sử có test đã chạy/đã xem. B1/flip cũng đã có test; không chỉ B0/B2 là có dữ liệu trước đăng ký. Đăng trước khi hoàn tất ma trận không đồng nghĩa đăng trước lượt test đầu tiên. Cụm “Preregistration with In-flight Baseline Data” trong kế hoạch là mô tả dự kiến, không phải bằng chứng trạng thái đăng ký hay tên mẫu OSF đã được dùng.

Các biên không đồng loạtδ=0,02: MCC0,03; AUROC0,02; BA0,01; meta-MCC0,02 theo hồ sơ đang dùng. Không chép nguyên bản Hiếu nếu model/graph/score/hypothesis mapping khác contract này. Dòng “quyết định đã chốt” trong tài liệu không tự chứng minh đã thực thi hoặc cho phép ghi đè khóa lịch sử; USER_DECISIONS của dry-run ghi rõ không fit tau.

### 3.2. McNemar và evaluator

Lỗi McNemar **còn tồn tại** ở [stats.py](../01_Author_Baseline_Unified/diagnostic_kit/src/grace_diag/stats.py): stat=(abs(b-c)-1)^2/(b+c). Trong lượt này đã gọi đúng hàm với y=[1]×30, A=[1]×15+[0]×15, B=[0]×15+[1]×15: b=c=15,p=0,8551321405847059. Chặn max(0,abs(b-c)-1) cho thống kê0 vàp=1. Lệnh test trong kế hoạch cho A=B tạo b=c=0, đi vào nhánh trả1 sẵn có; **không bắt được lỗi cần sửa**.

[evaluate_final.py](../01_Author_Baseline_Unified/diagnostic_kit/src/grace_diag/evaluate_final.py) vẫn gọi S.pick_threshold trong table_a rồi xuất thresholds.json ở output. Chưa có chế độ nạp/kiểm khóa bất biến thay luồng này. Chọn lại từ validation không tự chứng minh leakage test, nhưng không đáp ứng quy trình dùng khóa đã lưu trước test và chưa bảo đảm đủ validation/identity khi chạy evaluator. Đây là việc chưa được giải quyết bởi audit prompt.

### 3.3. Tích hợp Bước0

Nhận định “trống100%” cần sửa: tài liệu tiến độ ghi đã tái tạo36 run và phân tích lịch sử tại workspace nguồn; chưa tích hợp đầy đủ cho repo bàn giao/chiến dịch Qwen mới. Không có scripts/run_step0_offline_diagnostic.py ở root hiện tại. Có complementarity.py trong kit không chứng minh đã chạy báo cáo của chiến dịch này.

Không copy nguyên xi code Hiếu để xem như nghiệm thu: phải nối ID/cache/label/model đúng và kiểm tính độc lập nhóm. Lượt đối chiếu trước đã xác định nguồn Hiếu mặc định3-fold, không phải5-fold; code có fallback sang StratifiedKFold khi group split không khả thi, nên không bảo đảm mọi đường chạy giữ nhóm. Bản kế hoạch gọi H5.3 là benefit-confidence cũng chưa khớp dự đoán benefit-random trong đề cương; confidence là đối chứng bổ sung. Mục này chưa được chạy lại toàn bộ ở lượt lập worklog, không xác nhận lại con số669 test của repo Hiếu.

### 3.4. Bước3

Phần adapter/audit/dry-run đã tiến triển như mục2; nên đổi từ mục “cần tạo” sang “đã có, còn nghiệm thu5 arm và hai người đọc”. Cắt demo là có chủ đích theo budget; yêu cầu chấm tay là xác nhận nội dung/variant/cờ cắt theo rubric, không bắt mọi demo phải nguyên vẹn hoặc mọi cờ bằng0. Ngưỡng nghiệm thu tổng hợp≤1% không xóa cờ từng prompt.

Bộ chấm mới cần dùng packet của dry_run_validation_20261102. Không trộn phiếu của bộ hậu kiểm cũ với prompt/hash của bộ dry-run mới.

### 3.5. Bước6

Có supervised_anchor.py/complementarity.py trong kit, nhưng chưa có bằng chứng đủ SUP-LR/MLP/METRIC ba seed và score P_pre/P_post của chiến dịch này trong hồ sơ hiện kiểm. Cần adapter vectors.npy+manifest sang input learner, cùng ID/fold/scaler và fallback đối xứng. Chưa thể khóa bốn tau meta-model chỉ vì bảng minh họa có số.

### 3.6. Bước8

60 prompt chấm toàn vẹn của Bước3 **khác**60 ca sửa/hỏng SUP-LR/B2 của Bước8. Việc tạo packet đầu tiên không hoàn thành packet thứ hai. Kế hoạch Bước8 còn cần review relevance100 target/dataset, hai người chấm/phân xử và audit nhãn100 ca/dataset (50FN+50FP) theo đề cương. Tính kappa trên phiếu độc lập trước phân xử; sau phân xử báo kết quả/qui trình, không dùng độ đồng thuận sau hòa giải để thay bằng chứng độc lập.

## 4. Gate/runtime và tiến độ inference chưa đổi

Kiểm source notebook hiện tại tìm lời gọi require_test_lock cho kết quả:

| Runtime | Có lời gọi gate trong source? | Giới hạn |
|---|---|---|
| B0 |Có|Không chứng minh lịch sử I-03 đã khóa trước test|
| B1 |Không|Phải tích hợp/kiểm trước test mới|
| B2 notebook cũ |Không|Có helper riêng không thay cho tích hợp vào notebook|
| B2-flip phiên mới |Có|Không khôi phục thứ tự khóa của I-06 cũ|
| B2-rand/rerun66 |Có|Chưa có output GPU mới để nghiệm thu luồng thực|

Đây là kiểm tĩnh lời gọi, không phải test end-to-end GPU. Không tuyên bố lỗi test_validation_lock.py đã sửa chỉ vì24 test probe/dry-run khác pass. Lượt lập báo cáo không chạy lại toàn bộ suite.

| Arm | Output local đã xác minh | Việc tiếp theo theo dữ liệu hiện có |
|---|---:|---|
| B0 |10.011|Giữ, báo raw invalid và lịch sử khóa|
| B1 |5.434|Còn4.577 test; gate và khóa đúng phiên trước test mới|
| B2 |10.011 phiên cũ|Donor Devign mới cần28val+38test=66|
| B2-flip |5.235 phiên cũ|Giữ5.202; sửa28val+5test rồi chạy4.776 thiếu:4.809 lượt|
| B2-rep |0|Runner gọi model độc lập, đúng prompt B2 cuối|
| B2-rand |0|Đúng seed/identity, notebook hiện có bước rerun66 trước rand|
| B1-full/shuf/nolabel/labelonly |Chưa có output inference xác nhận|Mới có dry-run validation, không đổi thành completed inference|

Con số99 trong kế hoạch là66B2+33flip cần sửa **trong những record đã sinh**. 30.691-99=30.592 là số record có thể giữ theo đối chiếu donor tại thời điểm đó, không phải toàn bộ khối lượng còn chạy và không bảo đảm bất biến nếu có lỗi input mới được xác nhận. Không cộng33 test flip đổi prompt chưa chạy vào33 record sửa rồi đếm hai lần. Đợt dry-run này không tự yêu cầu chạy lại tất cả403/176 cờ demo.

## 5. Cập nhật đánh giá12 tiêu chí checklist

| # | Tiêu chí | Hiện trạng sau dry-run | Điều kiện còn lại |
|---|---|---|---|
|1|Metric lịch sử/đối chứng|Có công việc lịch sử ngoài repo; chưa phải0%|Tích hợp, tái lập và đối chiếu output đúng phạm vi|
|2|Smoke/top5/repeat/throughput|Có inference/log; chưa đủ bằng chứng tách từng tiêu chí|Không suy greedy=deterministic; tách valid score/raw/top5 và kiểm hai lượt độc lập|
|3|Manifest/dedup/donor|Freeze và audit membership đã có|Áp dụng donor đúng phiên cho inference B2/flip và khóa mới|
|4|Test/audit/chấm tay|Adapter+hậu kiểm; dry-run10arm/28tập đạt;20+4test theo verifier|5arm blocked, hai người đọc; lỗi gate notebook còn nguyên|
|5|Protocol/OSF|Có analysis-lock và hồ sơ OSF nháp|Cập nhật nháp đã lỗi phạm vi, chốt lựa chọn phân tích/metadata và gửi thật; giữ lịch sử|
|6|Tau validation trước test|Bốn khóa full validation cũ|Score rep/meta còn thiếu; migration validation và gate; không sửa thứ tự lịch sử|
|7|Records/manifest/identity|30.691record được hậu kiểm, native score khớp logprob theo audit trước|Chưa đồng nghĩa đủ mọi trường schemaB.2 trên mọi run; kiểm adapter/export và metadata thiếu|
|8|SUP/meta/routing|Module có, output chiến dịch chưa đủ|SUP ba seed, folds/group/fallback, routing random20seed và oracle|
|9|Bảng/hình/script chung|Evaluator có, lỗi McNemar/refit còn|Sửa luồng nạp khóa, thống kê, dữ liệu đầu vào rồi sinh bảng đúng phiên|
|10|Đối chiếu giả thuyết|Chưa có bảng cuối|Giữ mãH1.1-H6.1, biên từng metric, phân biệt đã biết/chưa làm|
|11|Chấm mù/kappa/audit nhãn|Packet Bước3 đã sẵn sàng, chưa chấm|Không nhầm với Bước8; đủ relevance/case packets/label audit|
|12|Gói tái lập máy sạch|README/nhật ký tốt hơn, input lớn ngoàiGit|Kiểm máy sạch, bàn giao hash/data cần thiết và rà log trước công bố|

B0 có1.132 raw invalid, B1 có3; toàn bộ score hiện audit vẫn valid. Do đó câu “valid_rate>99,5% nên smoke đạt” cần chỉ rõ đang nói loại validity nào. Model/scoring/graph của Hiếu khác không được xem như cùng identity để dùng lại prediction/ngưỡng.

## 6. Những điều kiện có thể làm bù và thứ tự hợp lý

1. **Đóng phạm vi Bước3:** hai người chấm packet mới; chuẩn bị evidenceH2/cặpB3/Key difference và dry-run năm arm blocked nếu muốn nghiệm thu nguyên vẹn15arm. Có thể ghi hoàn thành riêng phạm vi10arm hiện tại, không nâng thành toàn bộ Bước3.
2. **Trước GPU tiếp:** sửa/kiểm gate B1/B2; chốt đúng prompt/donor/scoring identity và audit phần sẽ chạy. Dùng validation có thật của đúng phiên để khóa; B2/flip migration phải sửa validation ảnh hưởng trước test mới. Không phải đợi14 khóa có sẵn mới được soạn hồ sơ kế hoạch OSF.
3. **Cập nhật hồ sơ OSF ngay theo bằng chứng mới:**10arm dry-run,nămblocked,human pending; ghi mọi phần test đã chạy/đã xem. Chốt các lựa chọn phân tích còn mở và công bố thời điểm thật. Không gọi toàn bộ can thiệp đăng ký trước hồi tố.
4. **CPU song song:** sửa McNemar/evaluator, nối Bước0 và SUP/meta bằng test có ý nghĩa; không copy code hoặc ngưỡng của repo khác mà bỏ bước đối chiếu schema/ID/model/fold.
5. **Sau khi đủ output:** bảng/CI/đối chiếu giả thuyết, Bước8 và nghiệm thu máy sạch. Audit hậu kiểm và tau tính sau có thể bổ sung minh bạch; không khôi phục được điều kiện “đã audit/đăng ký/khóa trước test” cho run cũ.

Kế hoạch đặt toàn bộ khóa14ngưỡng trước sửa gate/audit là thứ tự chưa phù hợp: một số score chưa có, validation còn phải migration. Cần trình tự theo từng arm/dataset/phiên, không dùng một mốc14cho mọi điều kiện.

## 7. Kiểm chứng đã làm trong lượt báo cáo này

- Đọc kế hoạch gốc, mẫu metadata worklogs06-08 và log04-05; đối chiếu tiến độ mới.
- Đọc summary/final_status/verification và USER_DECISIONS; kiểm raw_summary_sha256 khớp summary.json và verifier_sha256 khớp source verifier hiện tại.
- Đối chiếu chín hash protected trong summary với file thực tế: **9/9 khớp** (thresholds, trạng thái khóa và snapshot analysis_lock). Không tính ngưỡng mới.
- Kiểm hai phiếu CSV bằng parser: mỗi phiếu60dòng,0tênreviewer,0verdict.
- Đọc source gate năm notebook; đọc công thức McNemar và luồng refit evaluator. Tái hiện edge case McNemar b=c=15 bằng hàm thật, không sửa source.
- Kiểm sự tồn tại: các đường dẫn scripts/lock_full_validation_thresholds.py,configs/thresholds.json,scripts/run_step0_offline_diagnostic.py,tests/test_preregistration_integrity.py,tests/test_step0_offline_diagnostic.py ở root đều **chưa có**. Lệnh Verification Plan của kế hoạch chưa chạy nguyên văn được ở repo này.
- Không dựng lại70.070prompt, không chạy lại toàn bộ test suite; các con số20+4pass là kết quả artifact đã lưu. Không kiểm live Kaggle/OSF, không thực hiện đăng ký hoặc xác nhận669test của Hiếu trong lượt này.
- Chỉ tạo worklog mới này; không sửa kế hoạch gốc, runtime, hồ sơ OSF, threshold hoặc evidence lịch sử. Không commit/push trong lượt này.

## 8. Nguồn và dấu vết kiểm tra

Git HEAD chỉ phản ánh commit đã có; working tree đang chứa audit/dry-run chưa commit. Khi bàn giao cần giữ các file local được dẫn, không giả định pull HEAD sẽ có tất cả bằng chứng. Bảng hash dưới ghi bytes nguồn tại thời điểm kiểm, không phải dấu thời gian OSF và không thay thế bản đăng ký.

| Nguồn | SHA-256 lúc kiểm |
|---|---|
| [ke_hoach_tong_hop_va_khac_phuc_grace.md](../ke_hoach_tong_hop_va_khac_phuc_grace.md) | e7d3602cbc9a1d54d5fbfd47ab172d15082e46b8ccd411816b03a27a1c151164 |
| [Runs-management/dry_run_validation_20261102/summary.json](../Runs-management/dry_run_validation_20261102/summary.json) | 1c2d4dbff2765b34297ea78ea581dcf50a25c66d5f547f272e2831aa52229fb1 |
| [Runs-management/dry_run_validation_20261102/final_status.json](../Runs-management/dry_run_validation_20261102/final_status.json) | 0ffbdbcc3a2a89a95439c7cc29b1d4a51d55dddee794e0b7e593fb6f75b502ae |
| [Runs-management/dry_run_validation_20261102/verification.json](../Runs-management/dry_run_validation_20261102/verification.json) | 409dbb6caeb6c79b6fd0c4a5edd0bba50e8e00c5901702eaca565e64719f45e2 |
| [Runs-management/dry_run_validation_20261102/USER_DECISIONS.json](../Runs-management/dry_run_validation_20261102/USER_DECISIONS.json) | 6206699f7253b0556a16724e6dcf29b9f6f043653446c430e08375a0d89b699a |
| [Runs-management/prompt_audit_20261102/final_status.json](../Runs-management/prompt_audit_20261102/final_status.json) | ff354e471d5c6b48386300512d7fab8f1394cb3800ca4fc94888c1748ecf2f49 |
| [Runs-management/current_status.json](../Runs-management/current_status.json) | 36c7cd92d513dba1d17c973c59ea19b0d29aacd30c36a9195cdb4388f178113c |
| [Runs-management/thresholds.json](../Runs-management/thresholds.json) | 4f26113168fad67b9fb573652bc1f96eabf8d5ce0173d972fda9bfb5a59d9172 |
| [Runs-management/TIEN_DO_PHUONG_AN_2.md](../Runs-management/TIEN_DO_PHUONG_AN_2.md) | 54bfa35c780b870953b330eda7b77a01b294718a523b5cca307cc1cc09a46ae4 |
| [Runs-management/osf_registration_draft_20261102/OSF_DRAFT.md](../Runs-management/osf_registration_draft_20261102/OSF_DRAFT.md) | 81d055e1f8f65b521e5a2ad1e764a85a42eeec9c142ade53f65167493d78c873 |
| [01_Author_Baseline_Unified/diagnostic_kit/src/grace_diag/stats.py](../01_Author_Baseline_Unified/diagnostic_kit/src/grace_diag/stats.py) | 13cf1bd681369f36d044c3ddb6c87ae3b2e3d5dd5c1e450f641eea776b7f5992 |
| [01_Author_Baseline_Unified/diagnostic_kit/src/grace_diag/evaluate_final.py](../01_Author_Baseline_Unified/diagnostic_kit/src/grace_diag/evaluate_final.py) | b43fc9dcfbe3fe90882848c11e432c98d5b9b1a38a80ec843fe5669d7157a664 |

Các worklog liên quan: [xây bộ chạy](2026-11-02_step3_04_bo_chay_dry_run_cpu.md), [dry-run toàn validation](2026-11-02_step3_05_dry_run_toan_validation.md), [truy cờ nhãn](2026-11-02_step3_06_doi_chieu_canh_bao_nhan.md), [hồ sơ chấm tay](2026-11-02_step3_07_chuan_bi_ho_so_cham_tay.md), [kết luận phạm vi](2026-11-02_step3_08_doi_chieu_tieu_chi_va_cap_nhat_tien_do.md).
