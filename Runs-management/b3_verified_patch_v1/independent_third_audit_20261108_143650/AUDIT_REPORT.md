# Audit lần 3 — B3 verified patch, 08/11/2026

**Kết luận: CHƯA ĐẠT để đóng gói notebook/chạy GPU hoặc nghiệm thu đầy đủ bước 1–8.** Có thể tiếp tục điều tra nguồn Devign/REVEAL. Các sửa đổi đã cải thiện luồng phần mềm, nhưng còn lỗi tái hiện được và release v2 chưa phản ánh mã hiện tại.

Phạm vi: mã và artifact hiện có tại thời điểm audit; không tra cứu trạng thái đăng ký OSF trực tuyến. Không chạy GPU, sửa threshold hay tạo phiếu duyệt con người. Fixture/probe đều là dữ liệu tổng hợp, nằm riêng trong `probe_sandbox/` và không được đưa vào pool thật.

## Kết quả đã xác minh

- **65 tests passed, 0 skipped** trên bốn bộ: amended B3, preregistration integrity, probes, stats/complementarity. Xem [pytest.log](pytest.log). Hai lần ghi preview của test được chuyển vào thư mục audit; assertion của test giữ nguyên.
- Luồng thực tế `generate_review_packets(candidate)` → hai form hợp lệ → `determine_eligible_pairs` đã nạp được **1 pair tổng hợp**. Hash packet trùng `payload_hash(candidate)`.
- Khối render/audit thật của Step 8 nhận prompt chuẩn và trả `RENDERED_AUDITED`, Figure 6=true, target-label=false. Không còn phụ thuộc literal `Question:` ở nhánh này.
- Hai approve + một reject không còn được nạp mới. Timestamp placeholder `YYYY-MM-DD...` bị từ chối. Form lỗi không còn xóa bytes pool đang có.
- Cổng tổng hợp hiện từ chối khi preservation hoặc module/script hash thất bại.
- 103/103 artifact v1 nguyên vẹn; bank, freeze, tokenizer, tài liệu authority khớp hash. Ba seal nội bộ v2 còn hợp lệ.
- V2 thật vẫn có **0 human reviews, 0 Devign pairs, 0 REVEAL pairs**; census 2.732 + 2.273 = 5.005 ID đúng, code khớp sau strip; toàn bộ `PAUSED`, không có prompt.

Các điểm tích cực này không chứng minh toàn bộ 5.005 prompt đã render thành công: release vẫn có pool rỗng.

## T3-01 — Cao: Step 7 hiện không chạy hết vì biến chưa định nghĩa

Trong [b3_step7_verify_selector_renderer.py](../../../scripts/b3_step7_verify_selector_renderer.py), dòng 261 vẫn dùng `safe_pause_confirmed`; phần tính toán đã đổi thành `safe_pause_or_render_confirmed`.

Probe gọi **thân hàm Step 7 hiện tại**, giữ tokenizer/selector thật, chỉ stub các subprocess để tránh chạy lại tests và ghi preview lịch sử. Kết quả: `NameError: name 'safe_pause_confirmed' is not defined` khi tạo report. Đây là lỗi xác định ở nhánh tạo report, không phụ thuộc kết quả subprocess. Chưa chạy end-to-end Step 7 vào release thật.

**Cần sửa:** thống nhất tên biến, thêm kiểm tra tích hợp gọi hàm tới lúc xuất report, rồi chạy lại Step 7 vào release mới. Không dùng report PASS cũ làm bằng chứng cho script mới.

## T3-02 — Cao: bảo toàn pool đang vô hiệu hóa việc xử lý reject mới

`determine_eligible_pairs` đã từ chối hai approve + một reject, nhưng `ingest_human_reviews_and_seal_pools` sau đó giữ pair cũ có hai chữ approve trong chính payload cũ, validate pair cũ, rồi đánh dấu **`ACTIVE_VERIFIED_POOL`**. Phiếu reject mới không tham gia validation của pool giữ lại.

Probe tích hợp tái hiện: log báo disagreement, pair cũ vẫn còn trong file, manifest báo ACTIVE nhưng `admitted_pairs_count=0`. Step 8 đọc pair file và chỉ kiểm tra seal/hash cùng review nằm trong pair, nên chưa có chốt chặn disagreement mới ở luồng này.

**Cần sửa:** bảo toàn bytes lịch sử nhưng đánh dấu release/pool mới BLOCKED khi có disagreement chưa phân xử. Đối chiếu toàn bộ review ledger hiện hành trước khi kích hoạt pool. Phân biệt số pair thực tế trong file với số mới nạp. Trường hợp invalid form phải báo lỗi rõ và không tự phát hành manifest ACTIVE mới; hiện manifest vẫn được ghi lại vô điều kiện. Nếu có pair mới được admit, nhánh ghi file cũng cần quy tắc rõ cho các pair cũ không nằm trong tập mới.

## T3-03 — Cao: Step 5 tự điền bằng chứng nguồn còn thiếu

[b3_step5_make_candidates.py](../../../scripts/b3_step5_make_candidates.py), dòng 132–137 dùng `ev.get('before', v_code)` / `ev.get('after', p_code)` và so `.strip()`. Vì vậy sidecar không có bản hàm upstream before/after vẫn lấy ngược từ bank rồi được coi là đối chiếu nguồn thành công.

Probe gọi Step 5 thật với mini-bank tổng hợp, sidecar **thiếu cả hai trường**, có diff fixture: **1 candidate được tạo, 0 lỗi**. Điều này chưa chứng minh độc lập rằng nội dung hàm đã lấy từ revision nguồn. Thông báo “byte-for-byte” cũng không đúng với so sánh sau strip.

**Cần sửa:** bắt buộc bằng chứng hàm từ source archive, revision/path và hash file nguồn; thiếu trường thì UNRESOLVED. Không thay dữ liệu nguồn thiếu bằng code donor. Phân biệt exact bytes với chuẩn hóa có quy tắc và lưu cả hai hash nếu cần. `actual_fix.diff` có mặt cùng metadata không tự chứng minh file đó được lấy từ đúng repository/revision; cần đối chiếu với archive đã xác thực.

## T3-04 — Cao: Step 6 vẫn dùng quan hệ commit ghi trong donor để loại candidate nguồn hợp lệ

Step 3 đã đổi các ca không có direct edge thành UNRESOLVED; Step 5 đã nhận sidecar độc lập với direct edge của recorded commits. Tuy nhiên `run_automated_technical_triage` ở Step 6 vẫn gán REJECT nếu hai recorded commits không có direct parent hoặc không cùng changed file. Form approve sau đó bị từ chối vì triage.

Probe: candidate schema hợp lệ với before/after và fix/parent trong payload, recorded donor commits không trực tiếp nối nhau → packet có payload nhưng triage REJECT và form approve bị chặn.

**Cần sửa:** phân biệt recorded donor metadata với actual fix/parent nguồn đã xác minh. Triage quyết định dựa trên bằng chứng actual fix, source functions và mapping vào bank. Quan hệ recorded commits là tín hiệu điều tra; commit cha của fix không bắt buộc tự nó sửa cùng file.

Ngoài ra Step 5 còn kiểm tra `has_both_commit_responses` trước khi đọc sidecar, nên sidecar đầy đủ vẫn bị chặn nếu reconnaissance của recorded commits chưa đủ. Cần thống nhất điều kiện dữ liệu nguồn giữa Step 3/5/6.

## T3-05 — Trung bình: timestamp fixture vẫn qua validator production

`validate_review_form` có nhánh `if 'TEST-FIXTURE' in ts: ... pass`, ngay cả khi `allow_synthetic=False` mặc định. Probe `TEST-FIXTURE-NOT-A-DATE` trả `(True, None)`.

**Cần sửa:** production luôn yêu cầu parse timestamp thực có timezone; fixture chỉ được chấp nhận khi cờ thử nghiệm tường minh và không thể vào luồng dữ liệu thật. Không chỉ chặn chuỗi `YYYY...`.

## T3-06 — Cao đối với nghiệm thu: release chưa được phát hành lại theo code đã sửa

Ba seal v2 hợp lệ **với nội dung manifest cũ**, nhưng hash thực tế đã lệch ở:

- Module `Runs-management/b3_amended_20261106/check_b3.py`.
- Năm script Step 3, 5, 6, 7, 8 trong execution manifest.

V2 không thay đổi so với inventory audit trước; các report, packet, triage và seal cũ chưa phải sản phẩm chạy lại bằng code hiện tại. Đây là mismatch thật, không phải tình huống giả lập. Xem [state_check.json](state_check.json).

**Cần sửa:** sau khi xử lý lỗi, tạo release phiên bản mới từ input đã kiểm hash, chạy lại các bước bị ảnh hưởng và phát hành hash/seal/report mới. Giữ v1/v2 để bảo toàn lịch sử; không chỉ thay hash trong manifest để khớp code mà bỏ qua việc tái tạo artifact.

## T3-07 — Trung bình/Cao: cổng hash và readiness còn thiếu điều kiện

- Audit tổng hợp đã thêm preservation/module/scripts, nhưng chưa đưa `freeze_manifest_hash_pass`, `freeze_files_pass`, `authority_hashes_pass`, `tokenizer_files_pass` vào verdict. Probe biểu thức verdict thật trả True khi bốn nhóm này False và các nhóm khác PASS. Trong dữ liệu thật lần này bốn nhóm đều đúng; đây là lỗi logic được tái hiện, không phải bằng chứng freeze hiện bị sửa.
- Step 8 kiểm seal pool và hash pool, nhưng chưa validate seal `inputs_manifest`, toàn bộ hash input/code/tokenizer/specs hoặc hash chain tới Step 7. Hash specs chỉ được in, chưa so với giá trị đăng ký. Inputs seal cuối hàm chỉ được đọc để in báo cáo.
- Khi tất cả record RENDERED, Step 8 tự gán `READY_FOR_GPU_INFERENCE` chỉ từ trạng thái record. Prompt render đạt chưa đủ chứng minh đã khóa release notebook/runtime hoặc qua mọi điều kiện triển khai. Nên dùng trạng thái “prompt audit đạt/chờ runtime release acceptance”.
- `check_b3.py` vẫn gom mọi lỗi khởi tạo selector thành PAUSED; cần phân biệt INVALID_POOL với EMPTY_POOL để report và gate phản ánh đúng nguyên nhân.
- Một số đoạn báo cáo Markdown còn mô tả cố định mọi ca bị loại và mọi pool rỗng; cần làm động cùng với JSON khi có pair hợp lệ.

## Đối chiếu R1–R6

| Mục | Kết quả lần này |
|---|---|
| R1 canonical payload hash | Đạt trong probe tạo packet → form → admission; artifact release cần rebuild |
| R2 parser và prompt fail-closed | Probe prompt chuẩn đạt; chưa có full census prompt thật; còn input/runtime gate T3-07 |
| R3 bảo toàn pool | Không xóa bytes khi form lỗi; chưa đạt xử lý disagreement, manifest và versioning |
| R4 consensus/timestamp | Chặn reject ở admission mới, chuẩn hóa reviewer và chặn placeholder; còn bypass pool cũ và timestamp fixture |
| R5 gates | Cải thiện verdict/module/script và phân biệt nhánh render; Step 7 NameError, input gate và release mismatch vẫn chặn nghiệm thu |
| R6 provenance | Step 3 UNRESOLVED tốt hơn; còn fallback before/after, triage recorded commits và kiểm chứng archive |
| Console encoding | Runner có UTF-8; 65 tests chạy xong. Lỗi Step 7 hiện là NameError, không phải encoding |

## Bước tiếp theo được phép thực hiện

1. Tiếp tục thu thập source evidence Devign và khôi phục mapping REVEAL; chưa cần GPU cho các việc này.
2. Sửa T3-01 đến T3-05 và cổng T3-07. Bổ sung kiểm thử tích hợp cho existing-pool + reject, missing source functions, timestamp fixture và Step 7 xuất report.
3. Tạo release mới, chạy lại chuỗi liên quan và chứng minh input hash/code hash/artifact hash thống nhất. Dữ liệu chưa giải được vẫn ghi UNRESOLVED, không tự sinh quyết định con người.
4. Khi có candidate thật đủ bằng chứng, cho hai người duyệt độc lập. Chỉ sau khi có pool được duyệt và full validation prompt census đạt mới đóng gói notebook/runtime; qua nghiệm thu runtime rồi mới chạy validation GPU.

**Chưa có bằng chứng dữ liệu thật bị mất hoặc run GPU B3 mới đã bị ảnh hưởng trong lần audit này.** Các lỗi tích hợp được thử trên sandbox; pool thật hiện vẫn rỗng.

## Bằng chứng

- [State/hash checks](state_check.json), [inventory đầu vào](source_inventory.json).
- [Probe sửa đổi R1–R5](positive_path_probes.json), [probe tích hợp bổ sung](extra_probe_results.json).
- [Entry-point Step 8 probe](entrypoint_probe.json), [pytest result](pytest_result.json).
- Mã tái hiện: `check_state.py`, `probe_positive_paths.py`, `extra_probes.py`, `entrypoint_probe.py`, `run_required_checks.py` trong thư mục này. Probe Step 8 đầu dùng AST khối render thật; probe Step 8 thứ hai gọi entry point thật với pool thật rỗng được sao chép vào sandbox. Không sửa assertion hoặc code production.

## Phụ lục triển khai và tiêu chuẩn nghiệm thu — bổ sung ngày 08/11/2026

Phụ lục này cụ thể hóa việc xử lý **sau audit lần 3** theo yêu cầu của chủ dự án. Các phát hiện và kết quả kiểm chứng bên trên vẫn là snapshot tại thời điểm audit; nội dung dưới đây là **yêu cầu cho lần triển khai/kiểm chứng tiếp theo, chưa phải công việc đã hoàn tất**. Đối chiếu với [kế hoạch B3](../../../docs/B3_NEW_ALGORITHM_EXECUTION_PLAN_20261108.md) và governance record áp dụng. Phụ lục không tự sửa giao thức đăng ký, không cấp quyền đổi frozen inputs hoặc phương pháp để vượt cổng kiểm tra.

### A. Cách đánh giá “đạt” và thứ tự chuyển bước

Không dùng một chữ PASS chung để thay thế các mức nghiệm thu sau:

| Cổng | Ý nghĩa chính xác khi đạt | Điều kiện để chuyển tiếp |
|---|---|---|
| G0 — Sửa phần mềm | T3-01 đến T3-07 có bằng chứng xử lý, kiểm thử tích hợp đạt | Được tạo candidate/release mới; chưa chứng minh có pair thật |
| G1 — Bằng chứng nguồn | Candidate cụ thể có before/after, actual fix/parent, diff và mapping clean train được xác minh | Được gửi packet đó cho hai reviewer thật |
| G2 — Review và pool | Pool phiên bản mới chỉ chứa candidate đạt G1 và hai review độc lập còn hiệu lực | Được dựng prompt validation của dataset có pool đạt |
| G3 — Full validation prompt | Toàn bộ census thuộc phạm vi khai báo có prompt được audit, đóng băng và truy vết được | Được đóng gói delivery B3-only; chưa đủ điều kiện chạy inference đầy đủ |
| G4 — Notebook/runtime | Source delivery, môi trường GPU thực, scoring và resume đều qua kiểm tra kỹ thuật | Được chạy full validation với đúng release đã nghiệm thu |
| G5 — Validation scores | Full validation đủ ID, score/provenance hợp lệ theo policy đã chốt | Được tính và review threshold mới |
| G6 — Threshold mới | Tính lại độc lập từ score G5, full grid và lock riêng được duyệt | Được dựng/audit test rồi chạy test bằng lock mới |
| G7 — Test và báo cáo | Đủ census test, metric và provenance kiểm lại được, phân loại phương pháp đúng | Được báo cáo kết quả tương ứng với phạm vi thực sự đã hoàn tất |

Quy tắc bắt buộc cho mỗi cổng:

- Kết quả phải được tính từ dữ liệu/log thật của **cùng phiên bản release**. Report cũ hoặc test với mock không chứng minh entry point mới chạy end-to-end.
- Mỗi điều kiện bắt buộc là phép AND: thiếu bằng chứng, lỗi đọc dữ liệu, hash mismatch, test fail/skip ở phần bắt buộc hoặc trạng thái UNKNOWN đều **không được coi là đạt**.
- Tách `PASS`, `FAIL`, `BLOCKED`, `NOT_EVALUATED`; ghi dataset, nguyên nhân, artifact và phạm vi tác động. Pool rỗng là BLOCKED cho inference, không phải lỗi cần che và không chứng minh thuật toán đã được triển khai thành công.
- Verdict phải có thể tính lại từ report chi tiết; không hardcode PASS hoặc tự ghi “đã duyệt/đã ký”. Một kết quả test tốt không bù cho bằng chứng nguồn thiếu.
- Đánh giá riêng Devign và REVEAL. Dataset chưa có pool đạt phải tiếp tục BLOCKED. Nếu muốn triển khai riêng một dataset, cần quyết định phạm vi bằng văn bản trước inference, dùng manifest riêng và không tuyên bố đã đạt full hai dataset.
- Không đặt thêm mục tiêu số pair tùy tiện để ép hoàn thành. Pool phải không rỗng cho dataset triển khai và tuân thủ quy tắc xây pool đã chốt; số lượng, phạm vi tìm kiếm và quy tắc dừng xây pool phải công bố trước inference, không chọn theo metric validation/test.

### B. Việc làm ngay: sửa lỗi và chứng minh từng sửa đổi

**Thứ tự thực hiện:** lưu snapshot hiện tại → sửa T3-01/T3-05 → sửa cơ chế review/pool T3-02 → sửa provenance/triage T3-03/T3-04 → hoàn thiện gate T3-07 → chạy kiểm chứng → phát hành release mới T3-06. Điều tra nguồn có thể tiếp tục song song, nhưng không nạp vào pool ACTIVE trước khi các cổng liên quan đạt.

#### B1. T3-01 — Chạy Step 7 tới cuối và xuất report hợp lệ

1. Thống nhất tên biến tính kết quả CPU sample check với tên dùng khi tạo JSON; rà các nhánh tạo report để không còn tên biến chưa khởi tạo.
2. Kiểm tra riêng các trạng thái: hai pool rỗng, có pool hợp lệ trong fixture, pool hỏng, CPU sample check lỗi, subprocess test lỗi, tokenizer không chính xác.
3. Chạy entry point thật vào thư mục mới trên Windows, không stub subprocess trong lần nghiệm thu end-to-end. Output console/file phải UTF-8 đọc được; không ghi đè preview/report lịch sử.

**Đạt khi:** nhánh hợp lệ return code 0, report được ghi đầy đủ, số liệu khớp log và mọi Boolean tham gia verdict; nhánh bắt buộc thất bại return code khác 0, report nêu đúng nguyên nhân và không còn artifact “PASS” cũ gây hiểu nhầm. CPU sample render chỉ là kiểm tra mẫu, không thay G3.

**Bằng chứng:** command, thời gian, source hashes, return code, stdout/stderr, report Step 7 và log test tương ứng. Probe dùng mock chỉ bổ trợ, phải ghi rõ giới hạn.

#### B2. T3-02 — Giữ lịch sử nhưng chặn pool có disagreement hiện hành

1. Giữ nguyên pool/manifest đã phát hành; xử lý review mới trong vùng staging/release mới.
2. Validate toàn bộ form trước khi phát hành: lỗi JSON, thiếu trường, sai hash, reviewer không hợp lệ hoặc timestamp lỗi phải được ghi rõ và chặn lần phát hành đó. Không bỏ form lỗi rồi báo lần ingest đã thành công.
3. Chuẩn hóa danh tính reviewer bằng quy tắc công bố trước; không coi viết hoa/viết thường hoặc thêm khoảng trắng là hai người. Danh sách reviewer/ID phải truy về người thật hoặc nguồn xác nhận được chủ dự án chấp nhận.
4. Chọn review còn hiệu lực theo timestamp đã parse UTC và quy tắc supersession tường minh. Timestamp trùng nhưng nội dung mâu thuẫn, reject chưa giải quyết hoặc hơn hai reviewer mà chưa có phân xử phải BLOCKED; không chọn hai approve thuận lợi rồi bỏ phiếu khác.
5. Đối chiếu ledger mới với **mọi pair được giữ lại** trong pool cũ. Pair có reject/disagreement mới không được tiếp tục kích hoạt chỉ vì payload cũ chứa hai approve.
6. Nếu cần phân xử, lưu biên bản thật với người quyết định, case/payload hash, các phiếu liên quan và lý do; không tự sinh quyết định phân xử. Nếu thay payload, phải lấy review lại trên payload mới.
7. Trước publish, validate toàn bộ pool đề xuất và so với pool cũ: pair giữ/thêm/bỏ, lý do, số thực trong file, số mới nạp, hash, trạng thái. Chỉ publish sau khi tất cả điều kiện đạt; lỗi giữa chừng không để manifest ACTIVE trỏ tới file nửa chừng.

**Đạt khi kiểm thử tích hợp chứng minh đồng thời:**

- Pool cũ + form hỏng: bytes pool và manifest đã phát hành không đổi; lần ingest mới báo lỗi; không phát hành ACTIVE mới.
- Pool cũ + reject mới hợp lệ: lịch sử giữ nguyên; phiên bản đề xuất BLOCKED và runner không nhận pair đang bất đồng.
- Hai approve độc lập đúng payload: nạp thành công; tên biến thể của cùng một reviewer không đủ hai người.
- Hai approve + reject, ba approve chưa phân xử, timestamp trùng mâu thuẫn: đều không kích hoạt pair.
- Lần cập nhật thêm một case không làm mất case đã được giữ hợp lệ; mọi thay đổi membership có lý do trong diff.
- Manifest count bằng số dòng pair hợp lệ thực tế; không có ACTIVE/0 count trong khi file còn pair được sử dụng.

**Bằng chứng:** form đầu vào nguyên bản, ingestion ledger gồm cả parse failures, canonical reviewer mapping, quyết định supersession/adjudication, diff pool và manifest mới. Fixture tổng hợp phải tách khỏi dữ liệu con người thật.

#### B3. T3-03/T3-04 — Bằng chứng nguồn đủ và triage đúng đối tượng

1. Với mỗi candidate, lấy repository thực, full commit SHA 40 hex của actual fix và parent thực; xác minh quan hệ parent từ Git object hoặc API response đã lưu. Với merge commit, phải chỉ rõ parent được dùng và lý do.
2. Lưu source file trước/sau đúng revision, path thực ở từng revision, URL nguồn, thời gian lấy, hash bytes và trạng thái fetch/cache. Nếu rename, lưu mapping path và bằng chứng rename.
3. Trích hàm trước/sau từ source archive độc lập với donor bank; lưu vị trí/span hoặc quy tắc trích đủ để người khác làm lại. Thiếu before/after hoặc source file thì UNRESOLVED, không fallback sang donor code.
4. Đối chiếu hai hàm với hai donor trong clean train cùng dataset, nhãn lần lượt 1/0. Theo hợp đồng hiện tại, code trong pair phải khớp nội dung donor; không sửa donor/bank để tạo khớp. Nếu upstream export khác định dạng, lưu raw hashes và báo mismatch; chỉ dùng chuẩn hóa khi có quy tắc được duyệt trước và ghi rõ deviation, không gọi `.strip()` là byte-for-byte.
5. Lưu actual fix diff từ đúng cặp revision/path và kiểm chứng changed lines liên quan chính hàm đó. Function diff tự tạo chỉ là bằng chứng bổ sung, không thay actual upstream diff.
6. Viết security rationale cụ thể: lỗi gì, thay đổi nào khắc phục, evidence lines nào hỗ trợ. Cùng tên hàm/khác nhãn hoặc commit message chung chung không đủ chứng minh security fix.
7. Step 3/5/6 dùng chung kết quả source verification. Recorded donor commits chỉ hỗ trợ tìm kiếm/mapping; không yêu cầu chính chúng là actual fix/parent hoặc đều có thao tác sửa cùng file.
8. Với REVEAL, tiếp tục tìm nguồn/mapping gốc, ghi phạm vi đã khảo sát, ambiguous/missing và căn cứ loại. Không suy source repository, path hay bản chất `source_id`; không lấy donor dataset khác để lấp chỗ trống.

**Đạt G1 khi:** toàn bộ trường bằng chứng bắt buộc có thể truy về archive đã kiểm hash, source revisions/diff khớp, before/after và clean-train mapping đúng, không còn trường nguồn suy đoán hoặc fallback. Test phải từ chối thiếu code nguồn, diff sai path/revision, code mismatch, donor ngoài bank/sai dataset/sai label, hash file sai. Test cũng phải cho phép trường hợp actual fix hợp lệ nhưng recorded donor commits không trực tiếp nối nhau.

**Bằng chứng:** case manifest, evidence sidecar, source responses/files nguyên byte, actual diff, bản trích hàm, mapping donor, hashes, verification report và rationale. Việc schema validator chấp nhận candidate chưa tự chứng minh nguồn upstream có thật.

#### B4. T3-05 — Timestamp và fixture không lọt vào production

1. Loại đường cho phép timestamp chứa `TEST-FIXTURE` qua validator mặc định.
2. Production chỉ nhận timestamp parse được, có timezone, chuyển UTC trước khi so sánh; không tự gắn UTC vào ngày giờ thiếu timezone. Quy tắc kiểm timestamp tương lai phải công bố, thống nhất giữa validator và supersession.
3. Cờ synthetic chỉ phục vụ test; artifact synthetic có nhãn rõ, `inference_allowed=False` và bị từ chối ở entry point tạo pool/delivery dữ liệu thật.

**Đạt khi:** `YYYY...`, `TEST-FIXTURE-NOT-A-DATE`, ngày không tồn tại, timestamp thiếu timezone và timestamp tương lai ngoài policy đều bị chặn trong production; `Z` và `+07:00` cùng thời điểm được so sánh bằng nhau; không dùng lexical string order để chọn review mới nhất.

#### B5. T3-07 — Mọi gate phải kiểm đủ đầu vào và phản ánh lỗi thật

1. Dùng hàm verify chung ở đầu entry point: inputs seal, source/module/script hashes, freeze manifest và file hashes, authority documents, tokenizer files, spec archive, pool manifest/files, review ledger/source archive được tham chiếu và report Step 7 cùng release.
2. Manifest có self-seal chưa đủ tin cậy: các hash cần đối chiếu với mốc đã khóa/được duyệt độc lập; notebook phải pin đúng hash delivery. Không chỉ tính lại seal của file vừa bị đổi rồi coi là hợp lệ.
3. Verdict tổng hợp phải AND mọi nhóm bắt buộc, bao gồm cả bốn nhóm từng bị bỏ sót: freeze manifest, freeze files, authority documents và tokenizer files. Danh sách hash bắt buộc không được thiếu/rỗng rồi qua nhờ `all([])`.
4. Tách `EMPTY_POOL`, `INVALID_POOL`, `SOURCE_UNRESOLVED`, `REVIEW_DISAGREEMENT`, `RENDER_FAILED`, `PROMPT_AUDIT_FAILED`, `HASH_MISMATCH`. Empty pool cho phép báo PAUSED trung thực; pool hỏng và gate mismatch phải fail, không đổi thành pause bình thường.
5. Renderer đạt chỉ được cấp trạng thái tương đương `PROMPT_AUDIT_PASSED_PENDING_RUNTIME_ACCEPTANCE`. Trạng thái READY cho full inference phải kiểm thêm delivery và runtime thật tại G4.
6. Markdown, JSON, manifest và return code phải phản ánh cùng kết quả; bỏ các câu cố định “100% reject”, “không có pair” khi dữ liệu đã thay đổi.

**Đạt khi:** kiểm thử lần lượt thay/sửa/thiếu một artifact ở mỗi nhóm bắt buộc trong sandbox đều làm gate fail trước khi dùng artifact hoặc nạp model; run hợp lệ qua end-to-end; report nhận diện đúng nhóm lỗi. Đồng thời kiểm trường hợp inputs manifest bị xóa, manifest đúng seal nhưng file được tham chiếu sai, manifest thiếu danh sách hashes, report Step 7 thuộc release khác và pool có unresolved reject.

#### B6. T3-06 — Phát hành release mới sau khi code đạt

1. Chọn thư mục/version mới, ghi parent release v2 và lý do phát hành. Lưu inventory v1/v2 và audit trước; không chạy builder ghi đè các thư mục đó.
2. Chốt mã sử dụng cho lần build: Git commit cộng diff/hash cho file chưa commit nếu có. Ghi đầy đủ script/module thực sự được gọi, kể cả wrapper/dependency liên quan; không chỉ các script có tên “step”.
3. Tạo inputs manifest từ bytes thực; pin authority/freeze/tokenizer/specs. Tái dùng source cache chỉ khi verify hash và ghi rõ cache hit; không bịa network fetch mới.
4. Chạy lại các bước bị tác động theo dependency: điều tra/triage → candidate → packet/review ingestion → pool → Step 7 → census/audit. Nguồn chưa giải được vẫn giữ UNRESOLVED. Không sao chép report PASS cũ như kết quả build mới.
5. Seal artifact theo thứ tự dependency; manifest sau tham chiếu hash/seal chính xác của manifest trước. Sau build, tính hash lần nữa, so với inventory và kiểm toàn bộ link.
6. Ghi thay đổi vào `CHANGES_AFTER_PREREG.md`: ngày, lỗi, cách sửa, version bị ảnh hưởng, phân loại/deviation và việc có/không dùng score. Report nghiệm thu nêu trạng thái từng dataset, không gọi safe pause là hoàn tất triển khai.

**Đạt khi:** zero hash mismatch, zero artifact không rõ nguồn/version, v1/v2 nguyên vẹn, report tái tạo được từ command/log/input đã lưu. Nếu chưa có pool thật, chỉ được nghiệm thu phần sửa phần mềm/safe pause, không nghiệm thu G2–G4.

### C. Điều kiện nghiêm ngặt cho review và thuật toán B3

- Hai reviewer phải thực sự duyệt độc lập cùng một payload; giữ form gốc với reviewer ID, timestamp, decision, rationale và bốn xác nhận `same_function_verified`, `security_fix_verified`, `source_revisions_verified`, `explanation_supported`. Approve chỉ hợp lệ khi cả bốn là true.
- Packet JSON, Markdown và form phải ràng buộc cùng canonical `payload_hash(candidate)` loại trường `reviews`. Đổi source/rationale/code/diff hay trường khác trong payload làm review cũ stale; không tự cập nhật hash trong form thay người duyệt.
- Tool/AGY chỉ hỗ trợ thu thập, lập hồ sơ và triage máy; không tự tạo chữ ký, danh tính hoặc quyết định human review. Báo cáo phải phân biệt kiểm tra tự động với nhận xét con người.
- Selector xét toàn bộ pool đã freeze của **đúng dataset**, dùng exact mean token-set Jaccard theo implementation được chốt; tie bằng pair ID từ điển. Không top-k heuristic, B2 anchor, chọn theo label target hoặc fallback khi pool rỗng.
- Target API chỉ nhận ID/code/nodes/edges. Target labels nằm trong đường đánh giá riêng, không đi vào selector, renderer, prompt hoặc tiêu chí chọn pair.
- Pair đã chọn không vừa ngân sách phải báo lỗi theo policy đã duyệt; không đổi sang pair xếp sau, bỏ explanation, rút gọn demo trái hợp đồng hoặc bỏ target để hoàn tất census.
- Pool/selection/rendering policy phải chốt trước inference. Phát hiện cần thay đổi sau đó phải tạo version/deviation mới và đánh giá phần validation/threshold phải làm lại; không chọn theo điểm số thuận lợi.

### D. G3 — Tiêu chuẩn nghiệm thu full validation prompt

Với phạm vi hai dataset, phải có **2.732 Devign + 2.273 REVEAL = 5.005 prompt**, không phải chỉ 5.005 dòng census PAUSED. Với phạm vi một dataset đã được phê chuẩn riêng, phải đủ toàn bộ census dataset đó và ghi rõ dataset còn BLOCKED.

Mỗi record phải có target ID, method, dataset/split/seed, query code hash, selected pair ID, pool hash, source/review binding, prompt/hash và token audit. ID phải đúng tập chính thức, không thiếu/trùng/ngoài tập. Prompt hash tính lại từ đúng UTF-8 bytes giao cho runner phải khớp.

**100% prompt thuộc phạm vi phải đạt đồng thời:**

- Thứ tự Figure 6: role → target code → question → node info → edge info → demonstrations → answer. Dùng marker/parser chuẩn và đối chiếu nội dung thực; không chỉ tin cờ `evidence.order`.
- Không có target label được chèn; label của demo ở đúng demo section. Việc kiểm leak phải xét nguồn dữ liệu/khối render, không chỉ dựa vào một regex hẹp hoặc nhầm nội dung comment vốn có trong target code thành label do pipeline thêm.
- Exact tokenizer revision đã khóa, `approx=False`; code target ≤3.000 token, graph ≤1.500, **mỗi demo ≤1.500**, toàn prompt sau chat template + reserve 64 ≤8.192. Giải thích/diff phải đầy đủ theo hợp đồng và nằm trong audit tổng ngân sách.
- Demo và explanation đúng candidate đã được duyệt; không đổi nhãn/vị trí đối với arm B3. Cắt target/graph chỉ theo policy có sẵn, ghi truncation; không âm thầm thay demo.
- Zero `PAUSED`, `RENDER_FAILED`, `AUDIT_FAILED` hoặc cờ chưa đánh giá trong tập tuyên bố đã freeze. Oversized/invalid làm G3 fail cho phạm vi đó; không hạ mẫu số.
- Rebuild cùng inputs/code/tokenizer/pool cho cùng prompt bytes/hash và selection; mọi sai khác phải giải thích trước khi freeze.

**Bằng chứng G3:** prompt JSONL/bytes, per-record token report, ID-set diff rỗng, source/pair mapping, aggregate audit tính lại được và prompt manifest đã seal. CPU kiểm vài mẫu chỉ hỗ trợ debug, không thay full census.

### E. G4 — Notebook và runtime trước khi cho full validation chạy

1. Delivery chỉ lên lịch **B3**; không tự thêm B3-nodiff/swap/flip. Tạo kernel/version mới, ghi account/slug/version/input dataset version và source readback từ Kaggle.
2. Notebook phải dùng prompt đã freeze; pin hash bundle, worker/helper, prompt/pool và runtime contract. Sai/thiếu/nhiều input phù hợp phải abort trước inference. Không nhúng selector rút gọn để dựng lại demo khác trên GPU.
3. Dùng đúng contract đã chọn trong kế hoạch: `llama-cpp-python 0.3.16`, `transformers 4.57.1`, `huggingface-hub 0.36.2`, `tokenizers 0.22.2`, `numpy 2.1.3`, `scipy 1.16.3`, `scikit-learn 1.5.2`. Verify version cài thực, model SHA, backend source/build hashes và constructor theo contract; không chỉ kiểm nội dung cell cài đặt.
4. Model GGUF SHA-256 kỳ vọng: `f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335`. Backend sdist: `34ed0f9bd9431af045bb63d9324ae620ad0536653740e9bb163a2e1fcb973be6`. Giá trị contract canonical và delivery bytes phải được tính lại; không chép hash lịch sử để gắn nhãn runtime mới.
5. Ghi Python/platform/CUDA/driver/compiler/build flags, thread settings, backend binary hash và native load log. Với delivery Kaggle đã chọn, phải chứng minh **T4×2, offload 49/49 layer, context 8.192, batch/ubatch 256**, cùng các constructor settings trong contract. Parser chấp nhận format log tương ứng nhưng không bỏ điều kiện GPU/layer khi format thay đổi.
6. Kiểm prompt bytes/token IDs và chat template giữa CPU preparation và GPU runner. Scoring dùng full logits của label token `0`/`1` đúng vị trí: `s = sigmoid(logit_1 - logit_0)`, tính ổn định; lưu logprobs/score để kiểm lại. Không lấy số từ câu trả lời sinh tự do; phân biệt seed prompt và seed constructor theo contract.
7. Chạy kiểm tra kỹ thuật bằng fixture/replay riêng; kiểm checkpoint, graceful exit, download, CRC/hash và resume. Fixture output không nhập vào census thật. Nếu dùng validation target thật để kiểm vận hành, phải có policy trước và không thay phương pháp dựa trên score.
8. Resume chỉ nhận record có cùng method/pool/prompt/model/tokenizer/scoring/runtime release. Thử sai từng identity phải bị từ chối; duplicate ID khác score phải được phát hiện.

**Đạt G4 khi:** source readback khớp delivery, mọi runtime gate có log thật, scoring kiểm lại được và checkpoint/resume đã thử thành công. Kaggle `RUNNING`, request T4×2 hoặc setup không báo lỗi chưa đủ. Nếu chỉ có một dataset đạt G3, delivery phải khóa đúng phạm vi đó theo quyết định đã ghi.

### F. G5–G7 — Các điều kiện sau khi được phép chạy GPU

- Validation bắt đầu từ **0 score của phương pháp mới**. Không nhập checkpoint/score historical B3 để bù census. Đủ 5.005 ID cho hai dataset; từng record có provenance đầy đủ, score/logprobs tính lại khớp, invalid được xử lý đúng policy đã chốt. Phân biệt raw-response-invalid với numeric-score-invalid; không tự điền 0,5 hoặc fit trên subset thuận tiện.
- Chỉ tính threshold sau nghiệm thu validation. Mỗi dataset quét 99 ngưỡng `i/100`, i=1..99, positive khi `s >= τ`; MCC undefined bị loại; hòa trong `1e-9` chọn gần 0,5 nhất rồi ngưỡng thấp hơn. Lưu TP/TN/FP/FN, toàn grid, tie candidates và đối chiếu tính độc lập. Không lấy threshold từ tài liệu.
- Threshold mới là artifact/lock riêng của method mới, ràng buộc hashes validation/pool/prompt/model/runtime; không sửa `configs/thresholds.json` hoặc `configs/thresholds_flat.json` đóng băng. Ghi thẩm quyền/phân loại áp dụng trong governance record trước khi test.
- Test chỉ sau lock: cùng release đã được duyệt, **2.732 Devign + 2.274 REVEAL = 5.006 ID** cho phạm vi hai dataset. Labels tách khỏi prompt; không tối ưu pool/renderer/threshold bằng test score. Dừng do giới hạn phiên rồi resume được phép; dừng theo metric trung gian bị cấm.
- Báo cáo full official census và clean near-deduplicated partition theo protocol. Nếu dùng cho Table B, phải áp dụng đúng contrasts, paired cluster bootstrap và Holm; không gọi mô tả metric là bằng chứng confirmatory khi chưa đủ governance/statistics.

### G. Các điều kiện không được nới để “qua audit”

1. Giữ nguyên protected branch/tag, OSF draft bundle, preregistration, frozen threshold/arms/specs/banks và lịch sử worklog theo AGENTS.md. Mọi sửa đổi vận hành/methodological deviation phải ghi ngày, lý do, version và phân tích bị ảnh hưởng.
2. Không tắt assertion, đổi expected hash cho khớp file sai, bỏ test bắt buộc, đánh dấu skip/xfail để che lỗi hoặc gắn PASS từ chuỗi cố định. Khi chính expected value sai, phải có quyết định correction/deviation truy vết được, không âm thầm sửa anchor.
3. Không chế source evidence, human review, chữ ký, runtime log hoặc OSF approval. Trạng thái amendment phải dựa trên bằng chứng tương ứng; PDF đề xuất/local review không tự chứng minh có public registration stamp. Nếu chưa có căn cứ, báo đúng trạng thái và phân loại phương pháp đã được chủ dự án chốt.
4. Không đẩy candidate chưa xác minh/synthetic vào pool thật; không dùng cross-dataset donor, target/test labels hoặc điểm số để chọn patch pair. Không kết luận “không tồn tại pair” từ 12 ca đã khảo sát.
5. Không trộn historical B3 với `b3-verified-patch-v1`, không gắn runtime lock mới hồi tố cho record thiếu provenance.
6. Không publish release ACTIVE nửa chừng; lỗi phải giữ bản đã phát hành nguyên vẹn và tạo báo cáo thất bại riêng. Khóa version là ràng buộc bytes thực tế và provenance, không phải tên thư mục/notebook.

### H. Bộ hồ sơ bắt buộc nộp cho lần audit kế tiếp

| Hồ sơ | Nội dung tối thiểu |
|---|---|
| Báo cáo remediation mới | Ánh xạ T3-01…T3-07 → file/hàm sửa → command tái hiện → expected/observed → artifact/hash → trạng thái |
| Snapshot và change log | Commit/diff, hashes code/input, inventory v1/v2 không đổi, CHANGES_AFTER_PREREG, parent release |
| Kiểm chứng phần mềm | Bốn bộ test theo repo, kết quả các tình huống tích hợp ở B1–B5, return codes/logs; tách mock khỏi end-to-end thật |
| Hồ sơ source | Case archive, revisions/files/diffs, hàm trích và mapping donor; missing/ambiguous/UNRESOLVED ghi rõ |
| Hồ sơ review/pool | Packet hash, form thật, ledger, consensus/adjudication, pool membership diff, count/hash/seal; chưa có human review thì ghi 0 |
| Nghiệm thu prompt | Full census report, ID/hash/token/ordering/leak checks và prompt manifest; pool rỗng thì ghi chưa đánh giá |
| Nghiệm thu delivery/runtime | Khi đã đến G4: source readback, contract/model/package/build/native logs, scoring và checkpoint/resume evidence |
| Verdict riêng từng cổng/dataset | Người/công cụ kiểm tra, thời gian, dữ liệu thực hay fixture, điều kiện còn thiếu và bước tiếp theo được phép |

Lần audit tiếp theo có thể nghiệm thu **G0 và trạng thái safe pause** ngay cả khi provenance thật vẫn chưa phục hồi được. Chỉ được tuyên bố “sẵn sàng full validation GPU” khi G0–G4 thực sự đạt cho phạm vi dataset được phê chuẩn; không suy rộng từ số lượng unit tests qua hoặc từ một pair tổng hợp.
