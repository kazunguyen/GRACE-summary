# B3 thuật toán mới — chuẩn bị release, version và tiêu chuẩn nghiệm thu

**Ngày lập:** 08/11/2026, GMT+7. **Method:** `b3-verified-patch-v1`. **Đợt triển khai tiếp theo:** B3, Devign validation, seed42. **Trạng thái tài liệu:** kế hoạch thực hiện và tiêu chí chấp nhận; không phải chứng nhận đã launch GPU hoặc tự phê chuẩn mọi thay đổi phương pháp.

Tài liệu này tổng hợp các việc còn lại sau audit prompt v4, dùng cùng [kế hoạch B3 ban đầu](B3_NEW_ALGORITHM_EXECUTION_PLAN_20261108.md), [đối chiếu đề cương](AUDIT_ALIGNMENT_DE_CUONG_GRACE_20261108.md) và các điều khoản đóng băng trong AGENTS.md. Khi khác nhau về trạng thái tiến độ, dùng snapshot và bằng chứng có thời điểm mới hơn; giữ nguyên lịch sử cũ.

## 1. Điểm xuất phát đã có bằng chứng

| Hạng mục | Trạng thái đã xác minh | Hệ quả |
|---|---|---|
| Source case08 FFmpeg | Actual fix/parent, raw files/diff và clean-train mapping đã kiểm | Có nền để dùng candidate Devign; không thay donor bằng code ngoài bank |
| Hai review cuối | Chủ dự án đã xác nhận Hiếu/Dũng ký riêng trên payload cuối; form validator và pool hash khớp | Không cần tự tạo lại approve hoặc hỏi lại cùng xác nhận nếu payload không đổi |
| Payload đã duyệt | `0ced77fefccbcef797c3c01abfa0d139d5611e2d562e8f5ec01089ff05168ee1` | Bất kỳ thay đổi candidate payload nào cần review lại |
| Devign validation prompts | **2.732/2.732**, dựng lại bằng canonical renderer khớp, hashes/token caps đạt | Có thể tái sử dụng đúng prompt bytes đã audit |
| Ngân sách Devign | Max chat tokens4.983; cộng reserve64 =5.047 | Không cần cắt thêm prompt chỉ để đóng gói |
| Pool Devign | Một pair case08 | Mọi target chọn cùng pair; phải công bố giới hạn phạm vi này |
| REVEAL | Pool0, 2.273 census rows PAUSED/null prompt | Chưa thể chạy B3 mới trên REVEAL |
| Version metadata v4 | Inputs v4 nhưng pool/prompt còn nhãn v3 | Phải phát hành metadata nhất quán trước delivery |
| Notebook/runtime B3 mới | Chưa được nghiệm thu bởi audit prompt | Đạt prompt không đồng nghĩa được phép chạy full inference ngay |

Nguồn: [audit prompt](../Runs-management/b3_verified_patch_v1/independent_prompt_audit_20261108_190936/AUDIT_REPORT.md), [kết quả máy đọc được](../Runs-management/b3_verified_patch_v1/independent_prompt_audit_20261108_190936/audit.json), [xác nhận review](../Runs-management/b3_verified_patch_v1/independent_prompt_audit_20261108_190936/review_confirmation.json).

**Không nhập bất kỳ score/checkpoint inference B3 lịch sử vào B3 mới.** Checkpoint B1-shuf đang chạy tiếp là công việc khác, không cung cấp score hoặc runtime acceptance cho B3.

## 2. Phạm vi phải chốt trước inference

1. Phạm vi release tiếp theo là **Devign validation, B3, prompt seed42, N=2.732**, không phải5.005 prompt hai dataset và không phải test.
2. REVEAL ghi riêng `BLOCKED_UNRESOLVED_PROVENANCE`. Việc loại REVEAL khỏi lịch thực thi đợt này phải được PI xác nhận trong scope record; không xóa dataset khỏi ma trận nghiên cứu hoặc gọi hai-dataset complete.
3. GPU đợt này chỉ B3. B3-nodiff/swap/flip còn trong ma trận nhưng không tự launch; render các biến thể ở CPU để kiểm có thể được giữ riêng.
4. Chốt một-pair scope hoặc tiêu chí tiếp tục xây pool **trước khi có score**. Một pair không làm selector sai, nhưng không đo được lựa chọn pair thay đổi theo target. Không đặt thêm/bớt pair sau khi nhìn metric để tối ưu kết quả.
5. Ghi phân loại amended/exploratory/confirmatory theo authority và bằng chứng OSF thực có. Không suy registration stamp từ PDF đề xuất. Thiếu bằng chứng trạng thái đăng ký thì báo đúng giới hạn, không tự ghi “đã đăng ký trước”.

**Sản phẩm:** `governance/scope_decision.json` và bản dễ đọc tương ứng, có người xác nhận/thời điểm, method, dataset/split/arm/seed/N, pool hash, giới hạn một-pair và REVEAL blocker. Công cụ chỉ chuẩn bị hồ sơ, không tạo chữ ký thay PI.

## 3. Quy ước version thống nhất

### 3.1. Tách rõ các loại danh tính

| Loại | Giá trị/qui tắc thống nhất | Khi nào thay |
|---|---|---|
| `method_id` | `b3-verified-patch-v1` | Khi đổi thuật toán có ý nghĩa: eligibility, selection/ranking/tie, nội dung contrast hoặc scoring policy ảnh hưởng kết quả; phải đánh giá governance, không chỉ đổi tên |
| `release_id` | `release_20261108_v5` | Mỗi gói đầu vào/phần mềm đã publish có danh tính bất biến mới |
| `release_version` | **`v5_devign_validation_locked`** cho bản v5 phát hành cuối | Tất cả manifest của bản phát hành dùng đúng một giá trị, không lẫn v3/v4 |
| `parent_release` | `release_20261108_v4` | Trỏ release cha thực; không dùng nhãn v3 đang bị ghi nhầm để nhận diện cha |
| `schema_version` | Ví dụ số nguyên1 cho schema manifest mới, được đặc tả trước | Khi định dạng dữ liệu thay đổi; không đồng nhất với v5 của release |
| `runtime_contract_id` | ID bên trong contract được chọn | Có thể giữ ID chung; phải nhận diện **thêm** hash byte/seal, không dùng ID này một mình |
| `runtime_contract_sha256` | Hash bytes contract giao thật | Contract bytes thay thì không còn là cùng runtime delivery |
| `payload_sha256` | Canonical hash candidate loại `reviews` | Payload đổi thì review cũ stale; không sửa hash trong form thay người duyệt |
| `run_id` | Ví dụ `b3_verified_patch_v1_devign_validation_s42_run01` | Một logical inference run có cùng immutable inputs/scoring/runtime policy |
| `session_id` | Kaggle account/kernel/version + session identifier nếu API cấp | Mỗi phiên Kaggle khác nhau; không giả lập session ID khi API không trả |
| `checkpoint_sha256` | Hash bytes checkpoint đã xuất | Mỗi checkpoint mới; lưu parent checkpoint và số ID xác minh |
| `threshold_release_id` | Release ngưỡng riêng, chỉ tạo sau validation accepted | Không gắn threshold test vào validation release khi chưa tính xong |

Tên v5 có hậu tố `locked` là **tên bản phát hành cuối được đề xuất**, không phải bằng chứng khóa. Trong quá trình chuẩn bị dùng workspace staging và trạng thái DRAFT. Chỉ cấp metadata cuối/FROZEN sau khi các cổng tương ứng đạt; runner phải kiểm trạng thái và hashes, không suy “đã khóa” từ tên thư mục.

### 3.2. Metadata chung ở mọi manifest thuộc release cuối

```json
{
  "schema_version": 1,
  "release_id": "release_20261108_v5",
  "release_version": "v5_devign_validation_locked",
  "parent_release": "release_20261108_v4",
  "release_status": "FROZEN",
  "method_id": "b3-verified-patch-v1",
  "scope": {
    "dataset": "devign",
    "split": "validation",
    "arm": "B3",
    "prompt_seed": 42,
    "expected_count": 2732
  },
  "excluded_from_execution": {
    "reveal": "BLOCKED_UNRESOLVED_PROVENANCE"
  }
}
```

Đây là **schema của bản phát hành cuối đề xuất để triển khai**, chưa tuyên bố code hiện tại hỗ trợ đầy đủ hoặc v5 hiện đã FROZEN. Nếu còn trường legacy `method`, phải map và kiểm nó bằng `method_id`; hai giá trị khác nhau phải lỗi. Trạng thái mỗi manifest cần phân biệt `DRAFT`, `VERIFIED`, `FROZEN`, `BLOCKED`; FROZEN xác nhận input release bất biến, readiness của prompt và readiness GPU là hai trường khác nhau.

Report Step7 và các gate phải bind bằng release ID, inputs seal và source hashes. Nếu build qua staging rồi đổi tên thư mục, không dùng basename staging làm identity cuối. Phải sửa/kiểm adapter đang ràng buộc `release_target` để final report không stale sau publish.

### 3.3. Quy tắc phát hành và thay đổi

- Giữ v1/v2/v3/v4 và các dossier/audit cũ nguyên vẹn. V5 là bản mới, không chạy builder có `rmtree`/ghi đè vào release đã phát hành.
- Metadata-only correction không cần đổi method ID nếu selection/prompt/scoring không đổi; vẫn cần manifest/seal/binding mới. Prompt bytes đã audit có thể copy nguyên và kiểm hash thay vì render lại chỉ để đổi version label.
- Build staging có thể sửa; bản FROZEN không sửa. Bug fix sau publish tạo release mới và đánh giá những output nào bị ảnh hưởng; không tự gắn provenance mới cho record cũ.
- Nếu đổi pool/renderer/scoring làm prompt hoặc score contract thay đổi sau inference, không append vào cùng run một cách im lặng. Cần quyết định version/method, run mới và phần validation/threshold phải làm lại theo ảnh hưởng.
- Test Devign là input release riêng sau threshold acceptance, dùng số version kế tiếp còn trống; giữ pool/algorithm đã khóa. REVEAL khi sẵn sàng cũng có release riêng. Không dành cùng một v6 cho hai gói khác nhau hoặc bổ sung REVEAL âm thầm vào v5.

## 4. Các bước chuẩn bị cụ thể

### Bước 1 — Snapshot và quyết định phạm vi

1. Ghi commit thực tế, trạng thái working tree và diff/hash cho code chưa commit; không ghi cố định commit cũ như thể mọi code mới đã ở đó.
2. Inventory v4: inputs/pool/prompts, candidate, source/mapping/evidence manifests, review forms và code dependencies. Kiểm hashes khớp audit gần nhất; phần thay đổi phải xác định rõ.
3. Lập scope decision theo Mục2. Giữ REVEAL trong trạng thái pending của toàn nghiên cứu nhưng không đưa null prompts vào delivery Devign.

**Qua bước khi:** có phạm vi/authority rõ, source inventory có thể truy ngược; không có unknown change trong artifact được tái sử dụng.

### Bước 2 — Đóng hồ sơ source và review của case08

1. Giữ raw upstream files ở đúng fix/parent/path, raw function hashes, donor hashes, actual diff và rule mapping dòng trống riêng case08.
2. Phân biệt `source raw` với `donor text` dùng trong demo. Không sửa frozen bank; không gọi khớp sau chuẩn hóa là khớp exact bytes.
3. Giữ rationale đúng mức chứng cứ. Demo chỉ thể hiện helper `can_safely_read`; caller change `size * 34L` nằm ngoài demo và phải được nói rõ.
4. Đối chiếu hai form gốc, reviewer khác nhau, timestamp hợp lệ, approve, bốn tiêu chí true, cùng payload cuối. Evidence mapping/raw manifests phải được bind vào payload đã duyệt.
5. Chỉ tái sử dụng review nếu payload hash không đổi. Nếu phải chỉnh rationale hoặc evidence binding trong payload, phát packet mới và lấy review mới; không tự cập nhật hash trong form cũ.

**Qua bước khi:** payload `0ced77…68ee1` và các tham chiếu nguồn vẫn đúng, hoặc payload mới đã được duyệt thật; không có unresolved rejection/supersession. Xác nhận người dùng đã có được lưu với nguồn/thời điểm, không giả thành chữ ký số do công cụ xác minh.

### Bước 3 — Tạo v5 và đồng bộ metadata/hash chain

1. Tạo staging mới; copy artifact đã audit bằng bytes, không normalize newline trong artifact có hash.
2. Tạo pool manifest Devign, scope/mapping records và inputs manifest dùng metadata cuối thống nhất theo Mục3.
3. Tạo reports theo đúng dependency và kiểm code/inputs/tokenizer/runtime contract. Nếu chỉ đổi metadata, lưu chứng cứ các prompt/candidate bytes được giữ nguyên.
4. Chuẩn bị inventory phát hành, code hashes và các report cần thiết; verify trước publish; final release không có file nửa chừng hoặc thiếu artifact tham chiếu.
5. Ghi `CHANGES_AFTER_PREREG.md`: ngày, lý do version correction/Devign-only scope, source method, runtime được chọn, ảnh hưởng và việc chưa dùng score/test để quyết định.

**Qua bước khi:** zero mismatch và mọi final manifest cùng release/method/scope/parent. Không có report v3/v4 bị dùng như report v5 chỉ vì copy tên file.

### Bước 4 — Nghiệm thu prompt Devign trước delivery

1. Xác minh đúng official validation ID set2.732, không trùng/thiếu/ngoài tập; query code nối đúng frozen raw/specs.
2. Kiểm pool/candidate/review identities, canonical prompt bytes/hash và pair selection.
3. Kiểm Figure6, absence của label target trong luồng renderer, demo/difference đầy đủ và token caps bằng tokenizer đã khóa.
4. Prompt không đổi so audit190936 thì dùng fingerprint equality và report tham chiếu; chỉ re-render/count lại phần bị thay. Nếu renderer/tokenizer/pool thay, kiểm full2.732 tương ứng.
5. Seal prompt manifest mới; cấp trạng thái **prompt đạt/chờ runtime acceptance**, không cấp GPU-ready từ việc render thành công.

**Qua bước khi:** 100% prompt thuộc scope là `RENDERED_AUDITED`, zero PAUSED/RENDER_FAILED/AUDIT_FAILED; max context cộng reserve không vượt; input hashes và audit source hợp lệ. REVEAL null rows không được tính vào2.732 hoặc gọi là prompt đã dựng.

### Bước 5 — Đóng gói notebook B3-only

1. Notebook dùng đúng prompt đã freeze; không nhúng selector giản lược hoặc dựng demo lại trên Kaggle.
2. Input parser nhận ZIP/thư mục Kaggle đã giải nén với cùng mức xác minh hash. Thiếu/nhiều input phù hợp hoặc file sai phải abort trước model.
3. Pin input root manifest, runtime contract bytes/seal, worker/helper/tokenizer/model identities. Validation chạy chưa có τ* mới; không tự đọc threshold B3 cũ.
4. Worker ghi ID, score/logprobs, raw/score-valid riêng, method/pool/prompt/model/runtime identities, session provenance, timing và checkpoint durable.
5. Resume chỉ được phép nhận checkpoint thuộc đúng run identity. Fresh run đầu tiên phải bắt đầu từ0; các lần resume sau phải bắt buộc checkpoint và chặn silent fresh restart khi mount thiếu file.
6. Có deadline theo quota thực và export reserve; API timeout phải phù hợp notebook deadline. Không hứa hoàn tất full census chỉ vì Kaggle báo RUNNING.

**Qua bước khi:** notebook syntax/source hashes đúng, delivery manifest đầy đủ, code không có đường launch các arm khác hoặc đọc test/threshold cũ; dry preflight input/restore/scoring đạt trước submit.

### Bước 6 — Kiểm runtime GPU, rồi mới full validation

1. Kiểm quota/machine slots; chọn tài khoản theo chỉ định/quyền đã có. Chuyển private data giữa tài khoản chỉ trong phạm vi được cho phép; nếu auto-review chặn phải giải quyết theo thông báo, không đi vòng.
2. Submit notebook kỹ thuật/validation phù hợp scope được chốt; đọc lại source/metadata/version/input từ Kaggle và so với delivery.
3. Kiểm runtime thật theo Mục7: install/build, model, native GPU log, tokenizer token IDs và scoring. Smoke synthetic/replay tách khỏi census; nếu dùng validation target thật thì policy phải chốt trước và không thay phương pháp theo score.
4. Chỉ sau runtime gate đạt mới cho full validation tiếp tục. Output test kỹ thuật không được nhập như score benchmark nếu identity/policy không cho phép.
5. Thu log, records, status, checkpoint; kiểm CRC/hash và số ID sau mỗi phiên. Giới hạn thời gian được phép checkpoint/resume; không dừng theo metric trung gian.

**Qua bước khi:** có native runtime acceptance và source readback thực; không chỉ request T4×2 hoặc trạng thái RUNNING.

## 5. Hash chain và cấu trúc artifact đề xuất

Thứ tự dưới đây tránh manifest tham chiếu vòng hoặc notebook chứa hash của chính nó:

```text
raw source + mapping + candidate payload + reviews
    -> pool_manifest
    -> inputs_manifest (pool/code/frozen inputs/tokenizer/runtime references)
    -> step7_report (bind inputs seal + release/source identities)
    -> validation_prompt_manifest (prompt files + upstream manifest/report hashes)
    -> inference_input_manifest + input bundle
    -> notebook (pin inference_input_manifest SHA + worker/helper/runtime hashes)
    -> delivery_manifest (notebook + input bundle + kernel metadata hashes)
    -> publish/acceptance record (root delivery hash, release state)
```

- Mỗi self-seal có canonicalization định nghĩa rõ, loại đúng trường seal; **hash bytes file** và **canonical seal** là hai giá trị khác nhau.
- Notebook không embed hash `delivery_manifest` nếu manifest đó lại chứa notebook hash. Nó pin input root độc lập; controller kiểm delivery/notebook source readback.
- Input ZIP không chứa chính hash của toàn ZIP như một trường tự tham chiếu. Hash ZIP nằm trong manifest bên ngoài tạo sau khi đóng gói.
- `release_id`/`run_id` ổn định không thay thế cryptographic hashes. Mọi file cần thiết phải có mục tham chiếu bắt buộc; map thiếu/rỗng không được pass.
- Không đưa timestamp thay đổi theo mỗi lần đọc vào prompt/candidate payload nếu điều đó làm nội dung khoa học không đổi nhưng review hash tự thay. Audit/session timestamps nằm trong record phù hợp.
- Dùng đường dẫn tương đối trong artifact chia sẻ; không đưa key/token/signed download URLs. Hash và giữ bytes gốc trước khi tạo bản log đã redacted; bản redacted có hash riêng.

Gợi ý cây artifact, **chưa phải khẳng định các file đã có**:

```text
Runs-management/b3_verified_patch_v1/release_20261108_v5/
  governance/          scope decision, mapping decision, method classification
  source_archive/      source files/API/diffs/evidence manifests
  candidates/          candidate payload được review
  reviews/             form gốc, ledger, consensus/adjudication references
  pools/               pool bytes, membership diff, pool manifest
  validation/devign/   frozen prompts/census và prompt audit
  acceptance/          Step7, full prompt audit, release verification
  inputs_manifest.json
  validation_prompt_manifest.json
  inference_input_manifest.json
  delivery/            notebook, metadata, delivery_manifest
```

Đường dẫn thực có thể khác nhưng schema phải định nghĩa chính xác; không tạo hai prompt manifest “canonical” cạnh tranh nhau. Runtime observations và results/checkpoints mới lưu ở vùng run/session riêng, không ghi vào release FROZEN.

## 6. Tiêu chí bắt buộc cho thuật toán, prompt và review

- Eligibility: cả hai donor trong **clean train cùng dataset**, nhãn1/0, source thật cùng hàm có actual fix/parent và actual diff. Nguồn ngoài bank chỉ làm evidence, không được thêm làm donor để lấp thiếu pair.
- Selector: exhaustive exact mean token-set Jaccard toàn pool được khóa, tie pair ID từ điển. Không top200/B2-anchor/fallback theo target label hoặc chọn lại pair xếp sau khi quá dài.
- Target API chỉ ID/code/nodes/edges; label đánh giá giữ đường riêng. Không dùng test code/label/metric để chọn pool hoặc sửa phương pháp.
- Figure6: role/domain → target code → question → node info → edge info → demonstrations → answer. Kiểm nội dung thật, không chỉ tin một cờ order.
- Exact tokenizer; target ≤3.000, graph ≤1.500, **mỗi demo ≤1.500**, chat prompt +reserve64 ≤8.192. Demo/difference không bị cắt mất evidence; prompt quá dài phải fail theo policy đã chốt.
- Hết pool thì BLOCKED; lỗi pool/hash/review thì FAIL/BLOCKED với nguyên nhân cụ thể. Không đổi invalid pool thành “empty bình thường” để pass report.
- Hai reviewer độc lập, normalized identity không trùng, timestamp parse được có timezone, hai approve đúng payload với bốn xác nhận true. Reject/conflict/thiếu review hoặc >2 reviewers chưa adjudicate thì chưa activate.
- Form lỗi/parse lỗi phải có ledger và CLI thất bại; pool cũ giữ bytes nhưng không được ACTIVE khi ledger hiện hành có bất đồng.
- Membership giữ/thêm/cập nhật/bỏ đều có diff và lý do; count bằng file thực. Không drop pair ngầm khi nạp case khác.

## 7. Runtime lock dùng cho B3 mới

Dùng bản contract hiện hành đã được chọn và kiểm lại khi phát hành, gồm **bảy pins**: llama-cpp-python0.3.16, transformers4.57.1, huggingface-hub0.36.2, tokenizers0.22.2, numpy2.1.3, scipy1.16.3, scikit-learn1.5.2. Không copy hash contract sáu package từ B1-full/B1-shuf rồi gọi là contract mới.

Model GGUF Q4_K_M SHA-256: `f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335`. Tokenizer revision: `b2cff646eb4bb1d68355c01b18ae02e7cf42d120`. Backend source sdist SHA-256: `34ed0f9bd9431af045bb63d9324ae620ad0536653740e9bb163a2e1fcb973be6`. Phải tính/kiểm thực, không chỉ ghi các chuỗi này vào JSON.

Constructor/build/thread settings lấy nguyên từ [contract](../configs/inference_runtime_lock.json): context8192, batch/ubatch256, layers−1, layer split, tensor_split=None và các cờ còn lại. Scoring full logits không sampling; seed constructor sentinel khác prompt seed42, ghi riêng. Native log phải chứng minh **hai T4,49/49 layer offload**, context/batch đúng. CPU thread formulas, exact Python/OS/libc/CUDA/driver/compiler/CMake/flags và compiled backend hashes phải được ghi.

Chính sách platform build không hứa binary giống byte mọi session; cần đầy đủ provenance và source/build identity. Ghi rõ hash nào do verified runner đo remote và hash nào audit rehash local; không tự tuyên bố kiểm loaded GPU memory hoặc model bytes local nếu chưa làm.

Scoring: kiểm HF/GGUF tokenization equality, binary labels là hai single tokens riêng; reset mỗi prompt, logits vị trí cuối đúng, float64 stable `s = exp(lp1 - logaddexp(lp0,lp1))`. Raw greedy invalid và numeric score invalid là hai trạng thái. Không lấy số từ câu trả lời sinh tự do, không điền0,5 hoặc loại mẫu tùy tiện khi lỗi.

## 8. Testing bắt buộc — đúng phạm vi, không overtesting

| Nhóm | Ca tối thiểu phải chứng minh | Kết quả cần có |
|---|---|---|
| T1 Source/mapping | Case08 đầy đủ; thiếu raw function/diff, sai revision/path/hash/mapping | Case đầy đủ kiểm được; thiếu/sai chặn; không donor fallback; chỉ mapping dòng trống trong scope được duyệt |
| T2 Review | Hai approve; cùng người khác whitespace/case; reject; timestamp lỗi/tie conflict; >2 reviewers | Chỉ consensus hợp lệ đi tiếp; stale payload/hash và placeholder bị chặn |
| T3 Ingest/membership | Form JSON lỗi; pool A thêm B; pool cũ có reject mới | Nonzero exit/ledger khi lỗi; A không mất ngầm; lịch sử giữ bytes, release mới blocked nếu bất đồng |
| T4 Manifest/version | Thiếu/rỗng nhóm hashes, thiếu mandatory file, v3/v4 labels lẫn v5, report khác inputs seal | Fail trước render/model; không pass nhờ all([]), tên thư mục hay Boolean report cũ |
| T5 Selection | Ranking/tie; target label/demo hint; empty pool; selected pair quá dài | Đúng exhaustive mean Jaccard/tie; reject forbidden fields; pause/fail đúng; không rerank fallback |
| T6 Prompt census | Full ID set2.732, prompt hashes/text, Figure6, exact budgets/retention | Zero lỗi trong scope; REVEAL null không tính là prompt; fingerprint tương đương có thể tái sử dụng audit cũ |
| T7 Notebook/delivery | Syntax; scope chỉ B3/Devign/validation; input/worker/helper/contract bị đổi | Source/bundle identity khớp; sai input hoặc path không an toàn abort; không đọc historical test threshold |
| T8 ZIP và unpacked | Input/checkpoint nguyên ZIP; Kaggle đã giải nén; nhiều root; thiếu/corrupt member | Cả hai mode đúng được nhận, mọi file checkpoint kiểm hash; ambiguous/missing/corrupt chặn; resume không fresh restart |
| T9 Resume identity | Sai method/pool/prompt/model/tokenizer/scoring/runtime, ID duplicate khác score | Từ chối; checkpoint đúng bỏ qua ID đã có, records cũ không đổi |
| T10 Scoring | Logits thường/cực trị, sai binary token IDs, non-finite, raw token không binary | Score tính lại khớp; invalid đúng policy; raw invalid không tự làm mất numeric score hợp lệ |
| T11 Runtime log | Log native thực, format CUDA mới, thiếu GPU/layer/context hoặc package sai | Parser nhận format thật nhưng không bỏ gate; đủ provenance mới runtime pass |
| T12 Publish/verdict | Một gate false/unknown; lỗi giữa chừng; metadata-only correction | Không FROZEN/ACTIVE giả; không half-publish; version/references/hashes khớp sau sửa |

**Cách chạy vừa đủ:**

1. Tái sử dụng bằng chứng đã kiểm khi hashes không đổi; không re-render2.732 prompt mỗi lần sửa README.
2. Khi sửa một component, chạy tests component và integration liên quan **một lần**. Chỉ chạy lại khi sửa tiếp hoặc còn lỗi/chưa giải thích.
3. Mock chỉ cô lập network/subprocess; ghi rõ. Mock PASS không phải upstream authentication, human review hay GPU acceptance.
4. Trước release/commit/push chính thức, chạy bốn bộ sau một lần trên code đã ổn định, hoặc dùng đúng một lần Step7 thực sự gọi chúng. Không cộng mock subprocess outputs như test execution thật:

```powershell
python -m pytest tests/test_amended_b3.py
python -m pytest tests/test_preregistration_integrity.py
python -m pytest 01_Author_Baseline_Unified/diagnostic_kit/tests/test_probes.py
python -m pytest 01_Author_Baseline_Unified/diagnostic_kit/tests/test_stats_and_complementarity.py
```

5. Dùng temp/basetemp trong workspace khi Windows TEMP bị chặn; chuyển preview writes ra sandbox. Không thử corruption trên freeze/release thật. Test logs phải UTF-8 đọc được.
6. Lưu command, source/input hashes, thời gian, return code, stdout/stderr, scope và ảnh hưởng. Mốc “43/48/… tests” chỉ là số quan sát theo version; không đặt target tăng số test hoặc đòi số cũ mãi mãi. Test bắt buộc fail/skip không tính PASS.
7. Native GPU acceptance cần log phiên thật một lần cho delivery đang dùng; không mở benchmark/fuzz/nhiều account chỉ để tăng bằng chứng. Khi có failure, sửa đúng nguyên nhân, giữ output lỗi, version lại delivery và kiểm regression tương ứng.

## 9. Cổng nghiệm thu và điều kiện dừng

| Cổng | Bằng chứng cần có | Quyền chuyển bước |
|---|---|---|
| G0 Phần mềm | Các lỗi liên quan được sửa, tests và integration checks đạt | Được dùng công cụ để chuẩn bị candidate/release; chưa chứng minh nguồn thật |
| G1 Source | Actual fix/parent/source functions/diff/mapping và payload binding đúng | Được gửi candidate cho review độc lập |
| G2 Review/pool | Scope decision, hai review cuối hợp lệ, pool/membership/source identity rõ | Được dùng pool đó để dựng prompt theo dataset đã duyệt |
| G3 Prompt | 2.732 Devign prompt thật accepted; metadata/hash chain đúng; toàn census đạt | Được đóng gói notebook và preflight, sau đó kiểm kỹ thuật GPU theo scope/quota |
| G4 Notebook/runtime | Delivery pins, CPU restore/scoring checks, source readback và native/model/package/build/scoring/resume evidence thật | Được full validation inference |
| G5 Scores | Đủ2.732 IDs/score/provenance, invalid theo policy | Được tính threshold Devign mới |
| G6 Threshold | Full grid/independent verification/lock riêng accepted | Được dựng/audit test Devign và delivery test riêng |
| G7 Test/báo cáo | Full test scope, threshold áp đúng, metric/statistics/provenance truy vết được | Được báo cáo kết quả đúng phạm vi và phân loại |

Giữ đúng ý nghĩa **G0–G7 đã dùng trong các audit trước**. Metadata/release identity là điều kiện xuyên suốt, không đặt lại G1 thành một nghĩa khác. CPU delivery preflight là phần đầu của G4; chưa có native runtime evidence thì chỉ ghi G4 PARTIAL/NOT_EVALUATED, không ghi full validation GPU-ready.

Verdict phải AND mọi điều kiện bắt buộc. Thiếu bằng chứng = pending/blocked, không PASS. Sai model/input/label/hash/tokenization/source identity phải dừng trước khi tạo score. Lỗi thời gian/quota lưu checkpoint và tiếp tục; lỗi dữ liệu/phương pháp cần quyết định xử lý, không tiếp tục để lấy đủ N giả.

## 10. Sau validation: ngưỡng mới và test

1. Hoàn tất full validation trước; không tính τ* từ checkpoint thiếu. Không dùng score historical B3 hoặc fit khác để bù.
2. Tính Devign τ* chỉ từ score mới: grid `i/100`,i=1..99; positive `s>=τ`; MCC undefined bị loại; hòa trong1e−9 chọn gần0,5 nhất rồi τ thấp hơn. Lưu counts/TP/TN/FP/FN/full grid/tie set; đối chiếu cách tính độc lập.
3. Khóa threshold artifact riêng với hashes method/pool/prompts/model/runtime/validation records và governance authority. Không sửa frozen `configs/thresholds*.json`; evaluator test chỉ đọc đúng lock mới.
4. Sau lock, dựng test Devign2.732 với cùng pool/selector/renderer/tokenizer/runtime release; audit input rồi publish test delivery version mới. REVEAL test2.274 chưa được đưa vào scope nếu provenance chưa giải được.
5. Nếu sau này triển khai swap/flip, chúng kế thừa τ* của B3 cùng method; nodiff cần validation riêng. Lịch hiện tại không tự thêm các arm này.
6. Không interim stopping theo metric hoặc chọn lại seed/winner/pool sau test. Kết quả báo theo scope đã thực hiện và mức tiếp xúc test; không dùng rerun để đổi lịch sử đăng ký.

## 11. REVEAL: nhánh công việc riêng

1. Tìm mapping/source release gốc hoặc truy nguyên code tới upstream; ghi phạm vi truy tìm, URL/revision, kết quả thiếu/ambiguous. Export hiện thiếu metadata không chứng minh không tồn tại pair.
2. Với mỗi candidate, cần actual repository/path/fix/parent, source files và security diff; hai before/after phải map vào **hai donor clean train REVEAL** nhãn1/0. Không lấy Devign hoặc external patched function làm donor mới.
3. Kiểm source/mapping và hai human reviews như Devign; không giảm chuẩn để lấp dataset.
4. Có pool được duyệt thì phát hành release REVEAL riêng với source/code/runtime identities rõ, fresh validation2.273 → threshold riêng → test2.274. Không thêm vào v5 Devign đã freeze.
5. Chưa giải được thì tiếp tục BLOCKED và báo hạn chế/phạm vi đã khảo sát; không tự chuyển dataset mới hoặc mở arm khác trong confirmatory matrix.

## 12. Các điều khoản tuyệt đối không được vi phạm

- Không sửa protected OSF branch/tag, preregistration, frozen threshold/arms/specs/banks hoặc xóa lịch sử audit/worklog. Không force-push/rewrite public history.
- Không fabricate human reviews/signatures/adjudication, source metadata, native logs, OSF approval hoặc metric. AGY chỉ hỗ trợ công việc máy trong phạm vi dữ liệu được phép; không thay vai trò người duyệt thật.
- Không tắt assertion, sửa expected hash theo file sai, skip/xfail để che lỗi, lấy cache B2 cho B2-rep, hoặc retrofit runtime certification cho record lịch sử.
- Không đưa target label vào prompt/selection; không tune bằng test; không im lặng bỏ target/invalid hoặc cắt mất evidence để đủ census.
- Không gọi v5 chỉ-Devign là full hai dataset, một pair là retrieval thích ứng, prompt PASS là runtime PASS hoặc Kaggle COMPLETE là census COMPLETE.
- Không thay runtime giữa resume mà giữ nhãn cũ. Khác session build có provenance theo policy được phép; khác contract/scoring/input cần xử lý identity/deviation rõ.
- Không publish credential/signed URLs hoặc dữ liệu ngoài quyền được cấp. Giữ exact bytes cho artifact đã băm qua `.gitattributes`/cách lưu phù hợp, không sửa CRLF/LF trong lịch sử để làm hash khớp.

## 13. Bộ hồ sơ bàn giao và việc nên làm ngay

**Làm ngay theo thứ tự:** scope decision Devign-only → snapshot/review binding → metadata v5/hash chain → prompt fingerprint verification → B3-only notebook/restore/scoring preflight → runtime technical acceptance → full validation mới.

Bộ hồ sơ cần bàn giao gồm: final scope/version spec; candidate/source/mapping/reviews; pool/membership manifest; code/inputs/runtime manifests; full prompt audit và prompt hashes; tests/logs; notebook/delivery hashes; source readback/native runtime acceptance khi đã chạy; run/session/checkpoint ledger; change log và bảng các mục còn BLOCKED.

Người nghiệm thu phải trả lời được: **run nào, release nào, method nào, dataset/split/seed nào, đọc đúng prompt nào, dùng pool và review payload nào, runtime contract nào, có những record/threshold nào và còn thiếu gì**. Nếu câu trả lời phụ thuộc chỉ vào tên file hoặc một chữ PASS tự sinh, hồ sơ chưa đủ để đóng băng.

## Tài liệu nguồn

- [Đề cương hợp nhất](OSF_response/De_cuong_nghien_cuu_GRACE_hop_nhat.docx), [phản hồi quy tắc OSF/ngưỡng](OSF_response/PhanhoiHieuDungVeDangKyOsf.pdf).
- [Kế hoạch B3 gốc](B3_NEW_ALGORITHM_EXECUTION_PLAN_20261108.md), [đối chiếu đề cương](AUDIT_ALIGNMENT_DE_CUONG_GRACE_20261108.md).
- [Audit lần4 và tiêu chuẩn R01–R08](../Runs-management/b3_verified_patch_v1/independent_fourth_audit_20261108_153556/AUDIT_REPORT.md), [audit prompt v4](../Runs-management/b3_verified_patch_v1/independent_prompt_audit_20261108_190936/AUDIT_REPORT.md).
- [Selector/schema](../01_Author_Baseline_Unified/diagnostic_kit/src/grace_diag/amended_b3.py), [renderer](../01_Author_Baseline_Unified/diagnostic_kit/src/grace_diag/probes.py), [runtime contract](../configs/inference_runtime_lock.json).

Tài liệu này chưa tạo v5, chưa đổi metadata v4 và chưa launch B3. Các path/schema trong phần đề xuất là việc cần triển khai và kiểm; chỉ các liên kết nguồn cuối tài liệu là artifact hiện có.
