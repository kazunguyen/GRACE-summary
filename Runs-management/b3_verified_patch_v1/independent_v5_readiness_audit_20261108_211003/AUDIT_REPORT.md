# Audit mức sẵn sàng B3 mới — release v5

Thời điểm ghi hồ sơ: 08/11/2026, 21:10–21:14, Asia/Saigon. Phạm vi kiểm tra: `release_20261108_v5`, hai script build v5 và notebook được đóng gói thực tế. Không launch GPU, không sửa release hoặc các file frozen.

**Kết luận: CHƯA SẴN SÀNG LAUNCH.** Dữ liệu/pool/review/prompt Devign có thể giữ lại. Delivery đang có lỗi tích hợp tái hiện được trước inference và thiếu một số gate khóa input/resume. Chưa đủ CPU preflight để chuyển sang kiểm kỹ thuật GPU, càng chưa đủ điều kiện chạy full validation.

**Bổ sung theo yêu cầu phạm vi hai dataset:** mục tiêu bàn giao cuối là B3 mới chạy được **cả Devign và REVEAL**. Lộ trình Devign ở mục4 là nhánh thực thi đã có dữ liệu sẵn; không đại diện cho việc hoàn tất mục tiêu hai tập. Mục6 bổ sung kế hoạch khắc phục REVEAL, tiêu chí chốt version và điều kiện nghiệm thu chung. Kết luận audit v5 ở trên được giữ nguyên.

## 1. Những gì đã đạt và có thể tái sử dụng

| Hạng mục | Kết quả kiểm trực tiếp |
|---|---|
| Identity | Các manifest chính đã dùng `release_20261108_v5`, `v5_devign_validation_locked`, parent v4, method `b3-verified-patch-v1` |
| Scope | B3 / Devign / validation / seed42 / 2.732; REVEAL và test bị loại khỏi execution scope |
| Review/source/pool | 58 artifact được so với inventory của audit trước đều giữ nguyên bytes, gồm hai phiếu cuối trong `reviews/submitted/`, source Case08 và pool Devign |
| Human review authority | Tái sử dụng xác nhận trực tiếp của người dùng rằng Hiếu/Dũng đã duyệt độc lập trên payload cuối `0ced77fefccbcef797c3c01abfa0d139d5611e2d562e8f5ec01089ff05168ee1`; không yêu cầu ký lại cùng payload |
| Prompt | Đủ 2.732 target ID duy nhất; mọi prompt hash đúng; SHA-256 toàn census trùng chính xác bản đã được re-render và audit độc lập trước |
| Manifest | Tính lại cả 7 seal theo đúng chuẩn `sort_keys=True, ensure_ascii=False, indent=2`, bỏ trường seal tương ứng: đều đúng |
| File/hash chain | Các file delivery, mọi member được kê trong bundle, external ZIP hash và ba upstream links của prompt manifest đều khớp |
| Code inventory | Hash modules, scripts Step1–8 và authority documents trong inputs manifest đều khớp file hiện tại |
| Runtime contract | Chuỗi contract nhúng trong notebook tái tạo đúng raw bytes/SHA `4c9c3bcf…`; có 7 package pins, model/tokenizer pins và backend sdist pin |
| Syntax/scoring | 8 code cells parse được; hàm score thật cho logits bằng nhau trả 0,5; ±1.000 trả 1/0 và từ chối NaN |

Fingerprint prompt: `dee4a33009f4ecbf42b96e6f18c5f4390d5f0a620370af925bae0f2cceeb7e59`.

Không re-render lại toàn bộ vì fingerprint trùng bản đã audit. Các tests Step7 ghi nhận 54 + 6 + 20 + 11 = 91 passed; đây là bằng chứng cho các suite tương ứng, không chứng minh notebook mới đã chạy CPU preflight. Các chuỗi `OK` xuất hiện trong test mock lồng nhau không được cộng thành lượt kiểm thật bổ sung.

## 2. Các vấn đề cần sửa trước launch

### R1 — Blocker: schema bundle không khớp consumer

**Vị trí:** `delivery/input_bundle/prompts.jsonl`; notebook cell4 và worker cell7 (`load_bundle`, vòng inference).

Census hiện có `target_id`, `prompt`, `prompt_sha256`, selection/token audit, nhưng **0/2.732 dòng có `id`, 0/2.732 dòng có `label`**. Cell4 dùng `r['id']`, `r['label']`; worker cũng yêu cầu `id` và sử dụng label khi đánh giá.

**Tái hiện:** chạy nguyên cell4 với ZIP phát hành, chỉ chuyển đường dẫn Kaggle sang sandbox và thay hàm ghi log bằng no-op: `KeyError: 'id'`. Lỗi xảy ra trước build/model/inference. Worker cũng chưa tương thích schema này.

**Cách sửa:** tạo inference adapter rõ ràng: `id = target_id`; nối label từ đúng frozen Devign validation manifest/raw theo ID, kiểm đủ ID và nhãn 0/1. Label chỉ là metadata ngoài prompt; không đưa vào selector hoặc renderer. Giữ prompt text và `prompt_sha256` nguyên vẹn; lưu mapping một-một, hash nguồn nhãn, hash output và lineage từ census gốc. Bundle inference mới có thể có SHA khác census gốc, phải ghi riêng hai hash thay vì khẳng định chúng luôn bằng nhau.

**Đạt khi:** loader notebook và worker đều đọc được cùng bundle thật; đúng 2.732 ID/label đối chiếu freeze; missing/duplicate/unknown ID hoặc nhãn sai bị chặn; mọi prompt vẫn trùng fingerprint nội dung đã audit.

### R2 — Cao: manifest đã niêm phong nhưng notebook chưa cưỡng chế pin độc lập

**Vị trí:** cell4 và `load_bundle` cell7. `inference_input_manifest.json` có external hashes nhưng notebook không đọc/pin nó. Loader tin `prompts_sha256` từ chính manifest đi cùng prompt; không xác minh seal của manifest hoặc toàn bộ support files. Khi có nhiều input root, lấy phần tử đầu tiên. Nhánh unpacked chỉ đóng lại hai file, bỏ các support manifests.

**Tái hiện có giới hạn:** trong sandbox, đổi prompt bytes và trường self-declared `prompts_sha256`, giữ external pins/seal cũ. Phần loader trước dòng lỗi schema vẫn nhận gói này. Đây là kiểm gate input riêng; không phải chứng minh đã tạo được score từ gói bị đổi.

**Cách sửa:** notebook pin SHA của inference input manifest độc lập; xác minh manifest và identity trước cài/model. ZIP: kiểm external hash và các member bắt buộc. Unpacked: kiểm toàn bộ required members theo external manifest; không phụ thuộc hash ZIP được nén lại. Cả hai nhánh phải tạo cùng stable input identity, không chọn ngầm root đầu tiên. Pin worker/helper bằng cấu trúc không tạo vòng tự-hash; có thể lưu hash source nhúng trong delivery manifest bên ngoài và đối chiếu source readback trước launch.

**Đạt khi:** ZIP và unpacked đúng đều được nhận; sửa prompt + sửa self-hash vẫn bị từ chối; thiếu/corrupt support file, sai pool/method/release/runtime hoặc nhiều root đều abort trước model.

### R3 — Cao: lỗi notebook/runtime có thể làm hỏng nghiệm thu dù package/model đúng

1. **Thiếu `math` trong namespace notebook:** chỉ worker import `math`; import trong subprocess không cung cấp cho notebook. `validate_records()` gọi `math.isfinite`. Tái hiện trên một record giả lập hợp lệ về các trường được kiểm: `NameError: name 'math' is not defined`. Sau inference có record cũng sẽ gặp nhánh này, không chỉ lúc resume.
2. **Parser thiết bị GPU quay về regex cũ:** helper tìm `Device <n>: … T4`. Log native backend đang dùng trong dự án là `using device CUDA0 (Tesla T4)` và CUDA1. Áp chính regex helper lên log B1-full đã tải: **0 match**, trong khi có **2 dòng using-device**. Đây là bằng chứng regression tương thích format, không phải runtime acceptance cho B3.

**Cách sửa:** import `math` trong notebook; parser nhận format native đã quan sát và xác minh hai CUDA device phân biệt, đồng thời giữ gate 49/49 offload và effective context/batch/ubatch. Không bỏ assertion để chạy qua.

**Đạt khi:** validate record mới/resume chạy được; fixture từ log native thật được nhận; thiếu GPU, thiếu offload hoặc context sai vẫn bị chặn. Sau đó cần log native của chính phiên B3 mới để nghiệm thu runtime.

### R4 — Cao: checkpoint/resume chưa đạt quy tắc đã đặt

**Vị trí:** cell4 restore và `validate_records`; worker cell7 run identity/provenance.

- Restore chỉ lấy `records.jsonl`/`run_manifest.json`, không kiểm checkpoint manifest/member hashes và không giữ runtime provenance của record lịch sử.
- Unpacked checkpoint chưa có nhánh tương đương ZIP; khi không tìm thấy ZIP có thể đi theo fresh run thay vì fail rõ nếu người dùng yêu cầu resume.
- Tên member được nối thẳng vào `OUT_ROOT`; thiếu kiểm absolute path/`..`/resolved containment trước ghi.
- Worker cho phép records tồn tại khi không có run manifest; kiểm từng record chưa đủ method/pool/runtime/scoring/provenance. Run manifest chưa ràng buộc method/release/pool/input-root một cách độc lập. Notebook cũng không kiểm toàn bộ các trường này.

**Cách sửa:** checkpoint có inventory và stable run identity; restore atomic trong thư mục tạm, kiểm hash/path/record identity, mang theo provenance và log được records tham chiếu. Yêu cầu resume phải tìm thấy đúng checkpoint; không tự restart mới. Record cũ phải giữ nguyên bytes/score, thiếu manifest/provenance hoặc khác contract phải từ chối.

**Đạt khi:** fixture checkpoint nhỏ cùng identity resume được và bỏ qua đúng IDs; sai method/pool/prompt/model/runtime, missing manifest/member, duplicate conflict, ambiguous root và path traversal đều bị chặn. Chỉ cần kiểm các ca trực tiếp này, không cần stress/fuzz hay chạy đủ 2.732 mẫu để thử resume.

### R5 — Cao: metadata triển khai và provenance chưa thể dùng như hồ sơ launch cuối

**Vị trí:** `delivery/kernel-metadata.json`, `inputs_manifest.json`, hai script build v5.

- Kernel/dataset owner đang hardcode `huuhieu/...`; account được chỉ định trước đó trong dự án là `huuhieu3333`. Chưa có bằng chứng các dataset slug hiện tại tồn tại/quyền truy cập đúng. Đây chưa phải kết luận API đã từ chối: audit này không gửi yêu cầu launch.
- `enable_gpu` chưa khóa shape T4x2 trong metadata/request được bàn giao. Dùng đường deploy đã hỗ trợ request `machine_shape='NvidiaTeslaT4'`, rồi đọc lại server response. Chuẩn hóa Boolean theo schema client được dùng; không chỉ dựa vào chuỗi `"true"` để kết luận request đúng.
- `inputs_manifest.git_commit` hardcode `46e6f4ab…`, trong khi HEAD lúc audit là `68b7bf137bb9b957051c46a86d53ec41a528731c`. Code chưa commit phải có dirty-source hashes, không coi commit cũ là toàn bộ executable snapshot. Hai builders v5 chưa nằm trong inventory scripts chính; audit này đã lưu hash riêng của chúng và worker/helper nhúng.
- Scope decision ghi `RATIFIED_BY_PROJECT_LEAD`, timestamp `2026-11-08T12:00:00Z` bằng literal trong builder. Nội dung scope đã rõ, nhưng trường tự sinh không tự chứng minh có sự kiện phê chuẩn đúng thời điểm đó. Cần dẫn xác nhận thật hoặc ghi trung thực là prepared/pending; không yêu cầu hai người ký lại review payload không đổi.
- Builder có thể ghi vào release đã tồn tại; cần fail nếu đích frozen đã có và publish staging sau khi kiểm đạt.

**Đạt khi:** owner/dataset/version/request shape đúng, input mounts được kiểm, source readback khớp notebook đã audit; manifest ghi đúng commit + WIP inventory; authority có nguồn xác nhận thật; release cũ giữ nguyên.

## 3. Trạng thái gate sau audit

| Gate | Kết luận |
|---|---|
| G0 | Phần selector/renderer có bằng chứng suite đạt; delivery mới chưa đạt integration preflight |
| G1 | Tái sử dụng PASS source Case08 vì bytes không đổi |
| G2 | Review/pool hợp lệ; scope specification rõ; ratification timestamp chưa được chứng minh chỉ bằng literal builder |
| G3 | PASS nội dung prompt Devign; metadata v5/hash chain tính lại đúng |
| G4 | **BLOCKED CPU DELIVERY PREFLIGHT**, chưa được chuyển sang technical GPU launch |
| G5–G7 | NOT EVALUATED: chưa có score mới/threshold mới/test mới |

`FROZEN` chỉ được hiểu là snapshot input đã niêm phong; không đồng nghĩa GPU-ready. Báo cáo publish v5 ghi “CPU preflight PASSED” hiện rộng hơn bằng chứng thực tế và bị hai lỗi runtime tái hiện ở trên bác bỏ.

REVEAL tiếp tục BLOCKED vì chưa có pair có provenance hợp lệ. Pool Devign một pair được phép đánh giá đúng scope đã mô tả; không được trình bày là đã đánh giá adaptive retrieval trên nhiều pair.

## 4. Thứ tự xử lý tối thiểu để chạy được

1. Giữ v5 nguyên bytes như bản audit. Tạo release sửa metadata mới (ví dụ v6, parent v5), cùng `method_id=b3-verified-patch-v1`. Không cần đổi thuật toán hoặc dựng lại review/source/prompt. Nếu chỉ đổi delivery sau khi input đã chuẩn, dùng delivery revision riêng và pin đúng input release.
2. Sửa adapter R1, pins/loader R2, math/parser R3, resume R4 và deployment/provenance R5. Ghi deviation/bug fix trong `CHANGES_AFTER_PREREG.md`; không sửa frozen threshold/spec/bank.
3. Chạy một lượt integration CPU **từ notebook thực tế và bundle thực tế**, gồm fresh ZIP, unpacked, tiny checkpoint resume, input tamper và pure scoring. Reuse prompt audit khi text/hash giữ nguyên. Chạy suites ảnh hưởng bởi code sửa; trước release/commit/push hoàn tất bốn suites bắt buộc theo kế hoạch, ghi log thật. Không đặt mục tiêu tăng số test.
4. Khi CPU preflight đạt, mới đủ điều kiện kiểm kỹ thuật GPU: đọc lại source/shape/mount, ghi packages/build/native offload/tokenizer/HF–GGUF equality, score/provenance và checkpoint. Mẫu kỹ thuật phải ấn định trước theo ID, không chọn theo kết quả; nếu dùng `--limit`, giữ output kỹ thuật tách khỏi full-run identity hiện có trường `limit`.
5. G4 có bằng chứng thật đạt thì chạy full Devign validation 2.732 mới; chưa thêm REVEAL, nodiff, swap, flip hoặc test. Deadline/quota chỉ checkpoint, không dừng theo metric.
6. Full validation nghiệm thu đủ census rồi mới tính τ* mới theo grid/tie rule đã quy định, khóa riêng; sau đó mới dựng delivery test. Không dùng threshold/score B3 lịch sử để bù.

## 5. Hồ sơ và giới hạn kiểm tra

- [Kết quả máy đọc được](audit.json), [inventory bytes tại thời điểm audit](source_inventory.json), [script tái hiện](audit_delivery.py), [log thực thi](console.log).
- Chạy `python Runs-management/b3_verified_patch_v1/independent_v5_readiness_audit_20261108_211003/audit_delivery.py` từ repo root. Exit0 nghĩa script audit chạy xong; verdict trong JSON là `BLOCKED_DELIVERY_PREFLIGHT`, không phải acceptance PASS.
- Không thực thi build/install/network/GPU; không rerun các builder vào release v5. Thử đổi input chỉ trên bản sao sandbox đã được dọn; test record dùng fixture rõ ràng, không tạo kết quả nghiên cứu.
- Không yêu cầu audit nguồn/review hoặc full prompt lại khi bytes không đổi. Cần kiểm lại đúng delivery sau sửa và native evidence lần launch thực tế.

## 6. Phương án bổ sung để B3 mới chạy cả Devign và REVEAL

### 6.1. Chẩn đoán đúng điểm thiếu

REVEAL đang thiếu **pool patch-pair được xác minh**, không phải thiếu target validation/test hay không hỗ trợ thuật toán. Sửa notebook R1–R5 là cần thiết cho cả hai tập nhưng không tự tạo được provenance/pair REVEAL.

Đối chiếu trực tiếp `scripts/b3_step4_reveal_provenance.py`: `run_step4()` đọc raw data manifest, frozen train raw và train manifest; thống kê donor thiếu metadata rồi xuất sidecar/summary. Nó **không có bước tải upstream, đọc lịch sử Git hoặc đối chiếu actual fix**; các trường `mappable_to_commit_sha=0` và `authentic_before_after_pairs_recovered=0` được gán trực tiếp. Vì vậy, kết luận hợp lệ là **chưa phục hồi được pair từ phạm vi cục bộ đã khảo sát**, không phải đã chứng minh upstream không có pair.

Manifest nguồn cục bộ ghi `claudios/ReVeal@71f62e1e6e2053173e7de31a342d2c38b3fe2dcc`, `id_policy=split_row_index`. Chuỗi này là identity của bản phân phối dữ liệu được ghi trong repo, chưa tự chứng minh đó là Git repository/revision của source code sửa lỗi. Không dùng `source_id` số hoặc nhãn `debian`/`chrome` làm commit, tên repo hay patch relation.

`reveal_retrieval_provenance.json` trong donor reconciliation chỉ chứng minh ordered retrieval bank/vector lookup không đổi; không thay thế bằng chứng source before/after của B3.

### 6.2. Lộ trình xử lý và đầu ra bắt buộc

| Bước | Công việc cụ thể | Artifact đầu ra đề xuất | Tiêu chí đạt/chuyển bước |
|---|---|---|---|
| RV1 — Khóa đầu vào điều tra | Ghi hash donor bank17.636, train raw/manifest, upstream distribution manifest và code điều tra; giữ nguyên các file frozen. Lập bảng ID, source ID, label, code hash, project từ clean-train | `reveal_recovery/input_inventory.json`, `clean_train_index.jsonl` | Đúng17.636 donor được phép; mọi record truy được về freeze; không sử dụng nhãn/score validation hoặc test để lựa pair |
| RV2 — Phục hồi lineage của bản phân phối | Tìm loader/exporter/cache/source mapping đã có; sau đó kiểm tài liệu và nguồn phát hành gốc liên quan tới bản phân phối này. Tải metadata/archives cần thiết vào thư mục điều tra mới, pin URL/revision/hash/thời điểm | `source_acquisition_manifest.json`, `distribution_lineage.json`, `search_ledger.jsonl` | Phân biệt distribution repo với upstream source repo; ghi kết quả cả thành công, không tìm thấy, lỗi truy cập và ambiguous; không điền repo/commit bằng suy đoán |
| RV3 — Tìm ứng viên có thể truy nguyên | Ưu tiên mapping có sẵn từ source ID/hash về repository/path/revision. Nếu thiếu mapping, dùng code hash/đoạn code đặc trưng, tên hàm và lịch sử upstream để tìm vị trí xuất hiện; similarity chỉ xếp hàng ứng viên điều tra | `candidate_mapping.jsonl`, `unresolved_candidates.jsonl` | Mỗi ứng viên nêu evidence pointer và mức xác minh. Không coi cùng tên hàm, cùng CVE, code giống hay nhãn đối lập là pair đã đạt |
| RV4 — Chứng minh actual fix và bank membership | Lấy actual fix, parent phù hợp, file trước/sau và full diff; xác định cùng hàm trước/sau. Map về hai donor clean-train REVEAL nhãn1/0 và kiểm code/hashes. Giải thích hunk nào khắc phục lỗi, có phụ thuộc hunk ngoài hàm không | Mỗi case có `evidence_sidecar.json`, full source files, `actual_fix.diff`, mapping decision, candidate payload và evidence hashes | Ít nhất một pair thỏa cùng chuẩn source/mapping của B3; không chèn patched function ngoài bank. Nếu merge/multiple parents hoặc nhiều mapping khả dĩ, giải quyết tường minh trước admission |
| RV5 — Duyệt người thật và đóng pool | Gửi packet cho hai reviewer duyệt độc lập trên final payload hash; nạp forms đầu vào thật, xử lý reject/disagreement và timestamp bằng validator hiện có. Chốt phạm vi tìm kiếm và quy tắc admission trước xem score | Hai forms, ledger, `eligible_pairs.reveal.jsonl`, pool/membership manifest | Hai approve hợp lệ cùng payload; không còn bất đồng; ít nhất một pair REVEAL ACTIVE. Không tự sinh nhận xét/ký tên, không chuyển phiếu Devign sang REVEAL |
| RV6 — Dựng và audit prompt | Chạy selector/renderer trên full REVEAL validation2.273 với pool REVEAL mới; giữ Figure6 và tokenizer/runtime contract chung. Nối labels ngoài prompt bằng adapter đã sửa R1 | Census2.273, selection/token audit, inference rows, prompt/input manifests | Đúng2.273 ID duy nhất, zero PAUSED, prompt hashes khớp, không leakage, mọi budget/retention đạt, pool/dataset identity đúng; prompt null không được tính là đã chạy |
| RV7 — Đóng delivery và preflight | Áp dụng toàn bộ R1–R5, pin input REVEAL; kiểm fresh ZIP/unpacked/resume/tamper/scoring. Tách ID/output/checkpoint theo dataset | Notebook/delivery manifest, CPU integration log, checkpoint fixture | Không trộn pool/input/records Devign–REVEAL; mọi gate sai hash/identity abort; đã đạt CPU preflight thực tế |
| RV8 — Runtime và validation | Nghiệm thu native runtime của delivery mới, rồi chạy full validation REVEAL2.273 và Devign2.732 theo scope đã khóa | Native/package/build logs, run manifests, records và checkpoint/provenance | Mỗi dataset đủ census và provenance. COMPLETE trên Kaggle hoặc tổng count chung không thay thế kiểm từng dataset |
| RV9 — Threshold và test | Tính τ* riêng từng dataset từ full validation mới; khóa artifacts mới; dựng và audit test deliveries | Hai threshold locks, full-grid/tie evidence, test input/delivery manifests | Đạt G5/G6 của từng dataset trước khi chạy test tương ứng: Devign2.732, REVEAL2.274. Không lấy τ* Devign cho REVEAL hoặc dùng score B3 cũ bù vào |

Các path đầu ra trong bảng là **đề xuất cần tạo**, không phải bằng chứng đã có. Audit bổ sung này chỉ đọc code/tài liệu cục bộ; chưa thực hiện truy tìm upstream hoặc xác nhận có pair REVEAL phục hồi được.

### 6.3. Quy tắc mapping/source không được hạ chuẩn

1. Cần **hai donor trong đúng clean-train REVEAL**, nhãn1 và0, thể hiện cùng hàm trước/sau actual security fix. Pair Devign, donor bị purge, validation/test hoặc function tạo mới không được thay thế.
2. Khớp code nguyên bytes là tuyến ưu tiên. Nếu nguồn và donor khác formatting, giữ cả raw hashes và đưa ra mapping decision riêng có phạm vi hẹp, bằng chứng không đổi ngữ nghĩa và review. Không tự mở rộng ngoại lệ dòng trống của Case08 thành quyền normalize mọi REVEAL code; validator hiện yêu cầu source function khớp bank, mọi mapping adapter phải minh bạch và được kiểm trước admission.
3. Similarity/AST/name/project/CVE chỉ phục vụ discovery. Phải xác minh repository/path/revisions/parentage/function/full diff trước khi cấp trạng thái verified. Không ghép hai commit độc lập thành fix pair vì label đối lập.
4. Pool admission theo bằng chứng và review, không theo score/metric của target. Chốt search scope/candidate disposition trước inference; không thử nhiều pool rồi giữ pool cho kết quả đẹp. Nếu chỉ có một pair, công bố giới hạn như Devign; một pair không chứng minh lợi ích của adaptive retrieval trên nhiều pair.
5. Không cần phục hồi metadata của toàn bộ17.636 donor mới được bắt đầu. Điều kiện kỹ thuật tối thiểu là có ít nhất một pair đạt chuẩn, scope được duyệt, đầy đủ prompt census và delivery/runtime đạt. Đây không phải bảo đảm có thể tìm được pair trong bank hiện tại.

### 6.4. Chốt version cho hai tập một cách tường minh

Khuyến nghị **giữ nguyên v5** và chuẩn bị release kế tiếp, ví dụ `release_20261108_v6`, parent v5, `method_id=b3-verified-patch-v1`, schema version giữ nguyên nếu schema thực sự tương thích. Tên thư mục v6 là đề xuất, phải kiểm chưa tồn tại trước tạo. Không gọi release mới là `v6_devign_validation_locked` khi scope đã gồm cả REVEAL; dùng tên có nghĩa rõ như `v6_dual_dataset_validation_locked` **sau khi cả hai nhánh đạt gate cần thiết**.

- Một scope manifest chung liệt kê riêng Devign/REVEAL, counts, seed, phân loại amended và điều kiện test; các entries phải có state thật của từng dataset. Trong lúc REVEAL đang điều tra, release mới vẫn là DRAFT/PREPARING, không gán dual-dataset READY/FROZEN bằng literal builder.
- Pool manifest có membership/hash/review/source riêng từng dataset. Devign giữ pool payload/review/prompt đã duyệt nếu bytes không đổi. REVEAL có pool và payload hashes mới; không đổi thuật toán chỉ vì bổ sung pair thuộc đúng protocol.
- Input/prompt/inference manifest và output identity riêng theo dataset, cùng model/tokenizer/scoring/runtime contract đã khóa. Hash census gốc và hash inference adapter output được ghi riêng. Delivery root tham chiếu hai input roots; tránh vòng tự-hash.
- Có thể dùng **cùng account và cùng mã notebook** để chạy hai split tuần tự hoặc hai session do quota; không bắt buộc cả hai nằm trong một phiên GPU. Mỗi run chỉ đọc pool/input đúng dataset, có deadline/checkpoint riêng và được đọc lại machine shape. Đổi account/quota không được âm thầm đổi runtime identity.
- Nếu muốn chạy Devign trước để tiết kiệm thời gian: phát hành Devign delivery revision riêng sau sửa R1–R5; về sau phát hành REVEAL input release/delivery riêng cùng method, và tạo experiment index tham chiếu đúng hai immutable input identities. Đây là triển khai theo giai đoạn, **chưa được gọi hoàn tất hai tập** khi REVEAL vẫn blocked.
- Sau validation có **hai τ* mới**, cùng rule chọn nhưng khác score population. Test từng tập chỉ được mở khi lock của chính tập đó accepted. Không sửa `configs/thresholds*.json` frozen.

### 6.5. Bộ kiểm tối thiểu bổ sung cho REVEAL

Tái sử dụng suite source/review/selector hiện có và bổ sung đúng các boundary mới; không cần tăng số test theo một chỉ tiêu tùy ý:

| Nhóm | Ca cần kiểm | Chuẩn đạt |
|---|---|---|
| Provenance mapping | Pair thật đúng bank; nguồn mơ hồ; khác hàm; sai parent; donor ngoài bank; code khác ngữ nghĩa | Chỉ pair có evidence và mapping hợp lệ được admission; mọi ca chưa rõ giữ unresolved |
| Review binding | Đúng hai review trên final REVEAL payload; stale hash; reject/disagreement | Chỉ consensus thật đúng payload đi tiếp; không dùng review Devign |
| Dataset separation | Gửi pool/input/checkpoint Devign vào run REVEAL và ngược lại | Abort trước model/score; không fallback cross-dataset |
| Census/adapter | Đủ2.273 ID validation; missing/duplicate ID hoặc label; prompt content hash | Đối chiếu frozen population và labels, zero mismatch; label không vào prompt/selection |
| Delivery/resume | ZIP, unpacked, checkpoint nhỏ đúng; tampered/missing/ambiguous files | Đúng identity mới resume; score/records cũ giữ nguyên; không silent fresh restart |
| Runtime/scoring | Package/model/tokenizer/native contract; logits; provenance per session | CPU mock chỉ là preflight; acceptance GPU cần native evidence thật, đủ gate chung R1–R5 |

Không rerun full prompt Devign nếu fingerprint giữ nguyên. REVEAL là prompt population mới nên cần **một lượt full-census audit thực sự**; không dùng audit Devign để suy ra PASS cho REVEAL.

### 6.6. Nếu chưa tìm được pair REVEAL thì xử lý thế nào?

- Ghi rõ phạm vi đã truy tìm, phiên bản nguồn, evidence links, lỗi truy cập, mapping ambiguous và lý do từng candidate chưa đạt. Có thể tiếp tục discovery theo nguồn mới; thiếu metadata trong frozen export không chứng minh vô vọng.
- Nếu chưa có pair đạt chuẩn, **không có cách sửa metadata/notebook nào để biến run thành B3 verified-patch hợp lệ trên REVEAL**. Không ghép pair ngẫu nhiên, không dùng Devign demos thay, không quay lại heuristic cũ mà giữ tên method mới.
- Nếu điều tra cho thấy bank hiện tại không cung cấp pair chứng minh được, phương án thay dataset/bank, dùng external donor hoặc đổi định nghĩa pair là **thay đổi phương pháp** cần Lead PI quyết định và ghi amendment/phân loại riêng trước chạy; không tự sửa frozen assets hoặc gộp vào kết quả protocol hiện tại.
- Khi chưa giải được, báo trung thực “Devign ready/completed, REVEAL provenance pending”; mục tiêu hai dataset **chưa đạt**. Không cam kết thời gian hay khả năng phục hồi pair khi chưa có evidence.

### 6.7. Điều kiện kết luận “B3 mới chạy được cả hai tập”

Chỉ kết luận đủ điều kiện full validation hai tập khi **đồng thời**: Devign và REVEAL đều có pair/pool/review hợp lệ; scope/version authority rõ; hai prompt censuses2.732/2.273 và adapters đúng; các lỗi R1–R5 được đóng; CPU delivery preflight đạt; source readback/input mounts/shape đúng; runtime technical acceptance của delivery thực đạt. Trước đó chỉ ghi trạng thái từng nhánh, không lấy gate Devign làm gate REVEAL.

Thứ tự ưu tiên tiếp theo: **RV1–RV4 truy nguyên pair REVEAL**, đồng thời sửa delivery R1–R5 độc lập; sau đó RV5 review → RV6 full prompt → RV7 preflight → RV8 runtime/validation → RV9 threshold/test. Cả hai luồng đều cần hoàn tất để đáp ứng mục tiêu hai dataset.
