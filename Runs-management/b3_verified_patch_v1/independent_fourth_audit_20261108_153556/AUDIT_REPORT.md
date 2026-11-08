# Audit lần 4 — release B3 v3, 08/11/2026

**Kết luận: có thể chuyển sang bước tìm/xác minh nguồn và tạo candidate thật (G1). Chấp nhận v3 làm mốc phần mềm để tiếp tục công việc đó, với trạng thái safe pause. Chưa đủ điều kiện kích hoạt pool thật hoặc chạy notebook/GPU. Không xác nhận tuyên bố “G0 đã khắc phục triệt để mọi điều kiện”.**

## Phạm vi kiểm tra vừa đủ

Đọc báo cáo remediation mới, mã sửa liên quan T3-01…T3-07, manifest và report v3. Tính lại seal/hash, đối chiếu census, chạy **một lần bộ test B3 bị ảnh hưởng**: **35 passed, 0 failed, 0 skipped, 14,66 giây**. Không chạy lại ba bộ test không liên quan; report Step 7 v3 lưu kết quả 72 tests trên bốn bộ, được đối chiếu như bằng chứng do bên triển khai cung cấp, không gọi là 72 tests được chạy độc lập trong lần audit này.

Không chạy lại builders vào release, không mở rộng fuzz/performance testing và không chạy GPU. Test Step 7 trong bộ B3 có mock subprocess; bằng chứng end-to-end do triển khai lưu tại `release_20261108_v3/acceptance/step7_selector_renderer_report.json` được xem riêng, không đánh đồng hai loại kiểm tra.

## Kết quả đã kiểm chứng

| Hạng mục | Kết quả và phạm vi xác nhận |
|---|---|
| T3-01 Step 7 | Biến report đã sửa; test xây report qua. Report v3 ghi end-to-end PASS và CPU check PAUSED đúng hai dataset |
| T3-02 reject mới | Test pool cũ + hai approve + một reject giữ bytes lịch sử và chuyển manifest BLOCKED_DISAGREEMENT; runner sample từ chối sử dụng pool đó |
| T3-03 source fallback | Thiếu before/after bị chặn trong test; không còn lấy donor code để điền nguồn thiếu |
| T3-04 recorded commits | Test candidate source payload đầy đủ không còn bị loại chỉ vì recorded commits không trực tiếp nối nhau. Việc xác thực upstream thật vẫn thuộc G1 |
| T3-05 timestamp | Test production chặn timestamp synthetic đã qua |
| T3-06 release | Cả ba seal v3 tính lại đều khớp; 6 module/config/checker, 8 scripts, 2 authority docs, 6 tokenizer files đều khớp manifest; freeze files đúng hash |
| T3-07 gates | Đã có kiểm inputs seal/source/tokenizer/freeze/specs và Step 7 report; test sửa freeze file bị chặn. Còn giới hạn kiểm đầy đủ danh sách tham chiếu bên dưới |
| Dữ liệu thật | 0 candidate admitted, 0 review con người, 0 pair ở cả hai pool; 12 ca triage máy. Không có bằng chứng pair thật đã đạt G1 |
| Validation census | 2.732 Devign + 2.273 REVEAL = 5.005 ID; đúng tập/raw/specs, code sau strip khớp; hash census đúng manifest. Tất cả PAUSED, không có prompt, các cờ chưa đánh giá là null |

Manifest thật ghi đúng `BLOCKED_EMPTY_POOL_NO_PROMPTS_RENDERED` và `INFERENCE_PAUSED_EMPTY_POOL`. Câu trong mục 6 báo cáo remediation rằng trạng thái đã là `PROMPT_AUDIT_PASSED_PENDING_RUNTIME_ACCEPTANCE` cần sửa lại: đó chỉ là trạng thái dành cho nhánh **render đạt trong tương lai**, không phải kết quả hiện tại.

## Điểm còn lại — xử lý đúng thời điểm, không chặn điều tra nguồn

### 1. Trước khi phát hành/kích hoạt pool thật

Trong `scripts/b3_step6_packet_tool.py`, trường hợp form lỗi đang in ERROR rồi `return` nếu thấy pool/manifest tồn tại. Điều này bảo toàn bytes nhưng không báo thất bại bằng exception/return code khác 0; caller `run_step6` có thể kết thúc thành công. Lỗi parse cũng chưa được ghi đầy đủ vào ledger vì ledger chỉ ghi `submitted_reviews`.

Nhánh giữ existing pool còn tự tính latest reviews riêng, chưa xử lý xung đột cùng timestamp như `determine_eligible_pairs`. Nhánh có pair mới được admit ghi lại pool chỉ bằng `admitted_ds`, chưa có kiểm membership diff để bảo đảm không vô tình bỏ pair cũ.

**Việc cần làm trước G2:** trả trạng thái thất bại tường minh khi form không hợp lệ; ghi lỗi vào hồ sơ ingest; dùng chung quyết định consensus cho pair mới và pair giữ lại; kiểm membership diff trước publish. Đây là kết quả đọc code, chưa bổ sung probe mới để tránh mở rộng kiểm thử không cần thiết. Ca reject mới thông thường đã được test và đã sửa đúng.

### 2. Trước khi nghiệm thu release dùng để freeze prompt/GPU

Step 8 duyệt hash bằng các map `.get(..., {})`: map thiếu/rỗng sẽ không có phần tử để kiểm. Step 7 prerequisite hiện được nhận bằng `overall_passed`, chưa ràng buộc hash/source identity của chính report với release. Vì vậy không nên gọi gate đã bao phủ đầy đủ mọi trường hợp manifest thiếu.

**Việc cần làm trước G3/G4:** bắt buộc schema và tập file tham chiếu cần có, từ chối nhóm hash thiếu/rỗng; ràng buộc report Step 7 đúng release/source/input. V3 hiện có đủ các nhóm được kiểm và tất cả hash đều đúng; không có mismatch thực tế trong lần này.

### 3. Khi bắt đầu có candidate nguồn thật

Step 5 hiện đòi before/after nhưng vẫn cần archive độc lập chứng minh repository, revision/path, actual diff và hàm nguồn. Triage mới chỉ xét sự hiện diện trường source, chưa tự xác thực Git parentage. Không được coi `AUTOMATED_TRIAGE_PASS` hay schema pass là đã chứng minh upstream fix thật.

**Việc cần làm tại G1:** lưu source file/response trước và sau, actual fix và parent, hash bytes, diff liên quan hàm, mapping vào hai donor clean train cùng dataset và security rationale cụ thể. Dòng thông báo “byte-for-byte” trong Step 5 còn so sau strip; cần phân biệt rõ chuẩn hóa với exact bytes. Thiếu bằng chứng thì giữ UNRESOLVED; không cần tìm cách ép pool khác rỗng.

### 4. Báo cáo tự động cần diễn đạt theo chứng cứ

`remediation_third_audit_20261108/audit_third_remediation.py` vẫn gán `intact=True` khi mới đếm file và gán timestamp-validation PASS cố định. Một số kết luận chỉ suy từ pool rỗng, không kiểm hành vi sửa lỗi. Không dùng output này một mình để tuyên bố mọi lỗi đã khắc phục triệt để.

Audit độc lập lần này kiểm hash/preservation và chạy test thực để bù phạm vi đó. Cần sửa auto-report khi chuẩn bị hồ sơ nghiệm thu chính thức; không cần trì hoãn tìm nguồn chỉ để làm lại báo cáo.

## Bước tiếp theo cụ thể

1. **Tiếp tục ngay G1:** tìm actual fix/parent và source functions cho Devign; khôi phục mapping nguồn REVEAL. Mở rộng điều tra có log, giữ nguyên bank/specs; 12 ca chưa đủ kết luận không tồn tại pair.
2. Khi có **một candidate thật đủ hồ sơ**, kiểm source/mapping rồi mới gửi hai reviewer độc lập. Hoàn thiện các điều kiện ingest/pool tại mục 1 trước khi activate pool đó.
3. Sau G2 mới dựng full validation prompt, kiểm đủ census và ngân sách, seal release mới. Hoàn thiện schema/hash chain ở mục 2 trước nghiệm thu G3.
4. Sau đó mới đóng gói B3-only và nghiệm thu runtime Kaggle trước full validation. Hiện không có cơ sở launch GPU B3 mới.

Không yêu cầu thêm một vòng audit toàn bộ trước khi bắt đầu tìm nguồn. Mốc kiểm tra hữu ích tiếp theo là **candidate thật đầu tiên cùng source archive**, rồi pool được duyệt và prompt census; chỉ kiểm lại các phần có thay đổi.

## Bằng chứng

- [Hash/census check](state_check.json), [inventory trước kiểm tra](source_inventory.json).
- [Kết quả 35 tests độc lập](pytest.log), [runner result](pytest_result.json).
- [Kiểm bảo toàn và kết luận cuối](readiness.json).

Không sửa code triển khai, v1/v2/v3, threshold hay cấu hình Kaggle trong lần audit này. Test preview được chuyển vào thư mục riêng của audit; assertion không thay đổi.

## Hướng dẫn thực hiện sau audit và tiêu chuẩn testing bắt buộc

**Bổ sung ngày 08/11/2026 theo yêu cầu chủ dự án.** Nội dung dưới đây là các việc phải thực hiện và kiểm chứng ở lần triển khai tiếp theo, chưa phải kết quả đã đạt. Giữ kết luận của snapshot audit phía trên. Đây là tiêu chí vận hành để thực hiện [kế hoạch B3](../../../docs/B3_NEW_ALGORITHM_EXECUTION_PLAN_20261108.md), không thay đổi giao thức đóng băng hoặc tự cho phép đổi phương pháp.

### 1. Thứ tự làm việc và sản phẩm cần bàn giao

| Thứ tự | Cách thực hiện | Sản phẩm cần có | Đủ điều kiện chuyển bước khi |
|---|---|---|---|
| A — Tìm nguồn ngay | Điều tra Devign và mapping REVEAL theo hồ sơ dưới đây; lưu từng lần tìm/fetch, kể cả không thành công | Source archive + mapping + danh sách unresolved | Có candidate thật với bằng chứng G1 đầy đủ; chưa cần pool ACTIVE |
| B — Hoàn thiện ingest | Sửa báo lỗi form, ledger, consensus chung và quản lý membership; làm song song với A | Code, các test R01–R05, log kết quả | Các ca hợp lệ qua, ca bất hợp lệ bị chặn, lịch sử không đổi |
| C — Xác minh và review | Kiểm actual fix/parent, source functions, clean-train mapping; tạo packet rồi hai người duyệt độc lập | Case verification, packet, form gốc | Hai approve còn hiệu lực trên cùng payload, không còn bất đồng |
| D — Phát hành pool | Lập membership diff, kiểm toàn bộ pair, publish bản mới sau khi mọi gate đạt | Pool mới + manifest + review/source references | G2 đạt cho từng dataset thuộc phạm vi |
| E — Hoàn thiện release gate | Bắt buộc schema/tập hashes, ràng buộc report Step 7, sửa báo cáo tự động | Code, test R06–R08, manifest mới | Không thể bỏ qua kiểm tra bằng manifest thiếu/rỗng hoặc report khác release |
| F — Freeze validation prompts | Render/audit toàn census bằng pool đã khóa; không chạy LLM tại bước này | Prompt JSONL + audit + seal | G3 đạt theo mục 6 |
| G — Delivery/runtime | Đóng gói B3-only, kiểm source readback và môi trường Kaggle thực | Notebook/delivery hashes + runtime acceptance | G4 đạt rồi mới full validation inference |

Chưa có source thật thì tiếp tục A; không cần chạy lặp toàn bộ test hoặc dựng lại census PAUSED chỉ để tạo báo cáo mới. Khi có candidate đầu tiên, nghiệm thu hồ sơ đó trước khi mở rộng số lượng. Tiêu chí xây/dừng pool phải chốt trước inference, không chọn số pair dựa trên metric validation/test.

### 2. G1 — Cách tìm và xác minh một candidate thật

1. **Chọn phạm vi điều tra từ clean train.** Lấy donor ID, dataset, nhãn, code hash và metadata từ bank đóng băng. Cặp khác nhãn cùng tên hàm chỉ là đầu mối. Ghi tiêu chí ưu tiên tìm kiếm; không dùng target validation/test, nhãn target hay score mô hình để chọn pair.
2. **Tìm upstream thật.** Xác định repository chính xác, path và actual security-fix commit. Với REVEAL, tìm mapping/source release gốc; source ID chưa có mapping thì ghi chưa giải được. Không suy repository theo tên project hay bịa commit/path.
3. **Xác minh revision.** Lưu full SHA 40 hex của fix và parent; dùng Git object/API response để chứng minh parent của actual fix. Với merge, chỉ rõ parent được dùng. Hai commit ghi trong donor không bắt buộc chính là actual fix/parent; không yêu cầu commit cha tự nó cũng sửa cùng file.
4. **Lưu chứng cứ nguồn độc lập.** Lấy file trước tại parent và file sau tại fix, đúng path từng revision; lưu raw bytes, SHA-256, source URL, thời gian và trạng thái fetch/cache. Nếu rename, lưu bằng chứng mapping path. Không tắt xác minh TLS để lấy dữ liệu.
5. **Trích hàm trước/sau.** Ghi file/span hoặc cách trích đủ để tái tạo. Before/after phải đến từ source archive; không điền từ donor khi nguồn thiếu. Lưu actual upstream diff và function diff riêng, kiểm changed lines nằm trong hàm được xác minh.
6. **Đối chiếu với bank.** Hai hàm phải map vào donor clean train cùng dataset, nhãn vulnerable=1, patched=0, code trong pair khớp donor. Lưu exact-byte hashes; nếu chỉ khớp sau strip/chuẩn hóa, ghi riêng mức khớp và chặn việc tuyên bố exact bytes. Không sửa bank/code để ép khớp; chuẩn hóa mới chỉ được áp dụng sau quyết định phương pháp có ghi nhận.
7. **Giải thích security fix.** Nêu lỗi cụ thể, thay đổi khắc phục và dòng bằng chứng hỗ trợ. Commit message hay khác nhãn không đủ chứng minh bản vá an ninh. Trường hợp ambiguous vẫn UNRESOLVED.
8. **Kiểm và lập packet.** Chạy schema/local validation rồi kiểm source archive thực. Packet phải chứa đầy đủ thông tin cho người duyệt và ràng buộc canonical `payload_hash(candidate)` loại trường reviews. Schema PASS chỉ chứng minh cấu trúc, không chứng minh Git/source có thật.

**Hồ sơ tối thiểu cho một case:** donor IDs/labels/hashes; repository/path; actual fix/parent; response/Git evidence; hai source files; hàm trích và mapping; actual diff; security rationale; source/candidate/packet hashes; verification result và danh sách còn thiếu. Tên file có thể khác, nhưng nội dung và liên kết hash phải đầy đủ.

**G1 đạt khi:** người kiểm tra độc lập có thể dựng lại before/after và kiểm mapping từ hồ sơ, mọi revision/path/diff/hash khớp, không còn trường nguồn suy đoán/fallback. Nếu không tìm được thì báo phạm vi đã tìm và blocker, không kết luận không tồn tại pair ngoài phạm vi đó.

### 3. Cách sửa ingest/pool trước G2

1. **Tách validate khỏi publish.** Đọc/validate tất cả form vào staging; ghi ledger riêng cho lần ingest, gồm form hợp lệ, form thiếu/sai trường và lỗi parse. Có lỗi thì return code khác 0 hoặc exception có xử lý tại CLI; không chỉ in ERROR rồi kết thúc thành công.
2. **Dùng một hàm quyết định review chung.** Cả pair mới và pair giữ lại phải qua cùng quy tắc reviewer normalization, timestamp UTC, supersession, conflict và số người duyệt. Không viết hai phiên bản consensus có hành vi khác nhau.
3. **Giữ nhận xét gốc.** Hai reviewer phải thực sự độc lập, có danh tính truy được, timestamp có timezone, decision và rationale. Bốn xác nhận same-function/security-fix/source-revisions/explanation phải true để approve. Tool/AGY không tự sinh quyết định, chữ ký hay phân xử dưới tên người thật.
4. **Chặn bất đồng.** Reject còn hiệu lực, hai phiếu cùng timestamp mâu thuẫn, hoặc hơn hai reviewer chưa phân xử đều không được kích hoạt pair. Cần biên bản phân xử thật nếu muốn giải quyết; không chọn hai approve thuận lợi. Đổi payload phải review lại, không tự sửa hash trong phiếu.
5. **Lập pool đề xuất bằng quy tắc membership rõ.** Phân loại pair giữ/thêm/bỏ, lưu lý do và hash trước/sau. Không ghi pool chỉ từ số pair mới admit rồi vô tình bỏ pair cũ. Mọi pair giữ lại phải được đối chiếu ledger hiện hành, không chỉ tin hai review nhúng trong payload cũ.
6. **Publish có kiểm tra toàn vẹn.** Chỉ xuất version mới khi toàn bộ pool đề xuất hợp lệ; count phải bằng nội dung file. Lỗi giữa chừng không để manifest ACTIVE trỏ vào file dở dang. Giữ nguyên release đã phát hành; không sửa v1/v2/v3 để thêm review mới.

### 4. Testing bắt buộc cho các sửa đổi còn lại

Các test dưới đây là **tiêu chí phải có khi sửa phần tương ứng**, không yêu cầu viết lại test đã bao phủ đúng hành vi. Chạy trong sandbox/tmp; tuyệt đối không sửa freeze hoặc release thật để thử corruption. Không ấn định số test phải tăng: đánh giá bằng hành vi được chứng minh.

| Mã | Tình huống tối thiểu | Kết quả bắt buộc |
|---|---|---|
| R01 — Invalid forms | Pool/manifest đã phát hành + JSON lỗi, thiếu trường hoặc sai payload hash; thử cả release mới chưa có pool | CLI báo thất bại, ledger ghi đúng lỗi/file, không phát hành ACTIVE mới; bytes lịch sử không đổi |
| R02 — Review consensus | Hai approve độc lập; cùng người khác case/whitespace; reject; cùng timestamp mâu thuẫn; hơn hai reviewer | Chỉ ca đồng thuận hợp lệ được nạp; những ca còn lại BLOCKED. Cùng quy tắc cho pair mới và pair giữ lại |
| R03 — Supersession/time | Phiếu cũ/mới theo UTC; `Z` và `+07:00` cùng thời điểm; timestamp thiếu timezone, giả lập hoặc không hợp lệ | So theo thời điểm đã parse; tie mâu thuẫn không phụ thuộc thứ tự đọc file. Production từ chối timestamp lỗi/fixture |
| R04 — Membership | Pool có A; thêm B hợp lệ; cập nhật một case; chủ động loại A theo quyết định | A không mất ngầm khi thêm B; mọi thêm/bỏ có diff/lý do; counts và hashes phản ánh file thật |
| R05 — Source | Case đầy đủ; thiếu before/after; revision/path/hash/diff hoặc donor mapping sai; actual fix đúng nhưng recorded donor commits khác | Case nguồn đầy đủ đi tiếp; thiếu/sai bị chặn; không fallback; không loại chỉ vì recorded commits khác actual fix/parent |
| R06 — Required inputs | Thiếu/rỗng từng nhóm bắt buộc: modules, scripts, authority docs, tokenizer, freeze references/specs | Gate fail trước khi dùng artifact; không qua nhờ `.get(...,{})` hoặc `all([])`. Thiếu file bắt buộc cũng fail |
| R07 — Hash/report binding | Sai một hash; inputs seal sai; report Step 7 từ release khác hoặc source/input khác dù có `overall_passed=true` | Gate fail, nêu nhóm lỗi; report đúng danh tính mới được dùng. Self-seal không thay expected hash từ mốc được khóa |
| R08 — Verdict/report | Một điều kiện bắt buộc false/unknown/missing; pool rỗng; chưa render; nguồn chưa rõ | Verdict không PASS; JSON/Markdown/exit code thống nhất. Preservation phải so hash, không chỉ đếm file; timestamp PASS phải từ kiểm tra thật |

**Chuẩn test bắt buộc:**

- Dùng fixture tổng hợp có nhãn rõ cho các nhánh lỗi. Mock chỉ dùng khi cần cô lập subprocess/network và phải khai báo; không gọi mock PASS là upstream verification hay end-to-end thật.
- Kiểm cả giá trị kết quả lẫn tác động: exit code, trạng thái, nội dung ledger, hashes/counts và file nào được giữ/sửa. Assert “file tồn tại” hoặc “không raise” không đủ chứng minh sửa đúng lỗi.
- Mỗi sửa đổi chạy test bị ảnh hưởng và test tích hợp liên quan **một lần**; chỉ chạy lại khi có sửa tiếp, lỗi hoặc kết quả chưa giải thích. Không yêu cầu benchmark, fuzz diện rộng hay thử nhiều GPU/account cho các lỗi này.
- Không disable assertion, sửa expected value theo output sai, skip/xfail test bắt buộc hoặc đổi dữ liệu thật để đạt. Test lỗi do môi trường phải ghi BLOCKED; không gán PASS.
- Trước nghiệm thu bản phần mềm/release mới hoặc commit/push, chạy bốn bộ kiểm tra theo repo một lần sau khi code ổn định. Lưu command, source/input hashes, timestamp, return code và stdout/stderr. Nếu phát hành qua Step 7 thì dùng log thật của Step 7, không chạy lặp riêng cùng bộ chỉ để tăng số lần.

```powershell
python -m pytest tests/test_amended_b3.py
python -m pytest tests/test_preregistration_integrity.py
python -m pytest 01_Author_Baseline_Unified/diagnostic_kit/tests/test_probes.py
python -m pytest 01_Author_Baseline_Unified/diagnostic_kit/tests/test_stats_and_complementarity.py
```

Trong lần **audit độc lập**, có thể chỉ chạy bộ bị ảnh hưởng và đối chiếu log các bộ còn lại, như audit lần 4. Phải ghi rõ cái gì tự chạy, cái gì chỉ xem bằng chứng. Kiểm thử ghi preview/report phải chuyển sang thư mục mới để không thay artifact lịch sử.

### 5. Release gate và hồ sơ nghiệm thu phải có

- Bắt buộc schema của inputs manifest và tập tham chiếu cần thiết; kiểm nội dung đủ, không chỉ kiểu dict. Các script/module/dependency thực sự được gọi phải nằm trong phạm vi version/hash đã chốt.
- Pin expected hashes từ mốc đã được duyệt; validate freeze/tokenizer/specs/source code trước khi dùng. Không tính lại self-seal cho file đã thay rồi coi như vẫn cùng release.
- Step 7 report phải ràng buộc release ID, source/input identities và kết quả kiểm tra; manifest nghiệm thu sau phải tham chiếu hash report đó. Thay code/input sau khi tạo report làm bằng chứng bị stale cho phần ảnh hưởng.
- Source archive/review/pool/prompt có liên kết hash truy được từ record. Không tạo vòng hash: seal từng artifact theo dependency rồi seal manifest phía sau.
- Ghi công việc vào `CHANGES_AFTER_PREREG.md` với ngày, lý do, version và phân tích bị ảnh hưởng. Sửa report “PROMPT_AUDIT_PASSED…” nếu thực tế vẫn null/PAUSED; phân biệt prepared, verified, blocked, running, complete và accepted.
- Báo cáo remediation tiếp theo chỉ cần ánh xạ: lỗi → file/hàm sửa → test/command → expected/observed → artifact/hash → cổng còn thiếu. Không dùng chữ “triệt để” nếu vẫn chưa đánh giá nhánh dữ liệu thật.

### 6. Tiêu chuẩn bắt buộc trước prompt freeze và GPU

**G2 — Pool:** từng pair đạt G1, hai review độc lập còn hiệu lực trên cùng canonical payload, không còn disagreement, cùng dataset clean train, count/hash/version đúng. Không có synthetic pair hoặc reviewer giả trong dữ liệu thật.

**G3 — Prompt:** với phạm vi hai dataset, cần đủ **2.732 Devign + 2.273 REVEAL = 5.005 prompt thật**. Đúng ID set, không trùng/thiếu, prompt/hash tính lại khớp; zero PAUSED/RENDER_FAILED/AUDIT_FAILED trong phạm vi tuyên bố đạt. Kiểm 100% census, không chỉ CPU sample:

- Figure 6: role → target code → question → node info → edge info → demonstration → answer, đối chiếu nội dung thực và parser chuẩn.
- Target labels tách khỏi selector/renderer/prompt. Label demo phải đúng arm B3 và đúng section; không dựa riêng một regex để tuyên bố không leak.
- Exact tokenizer đã khóa, `approx=False`; target code ≤3.000 token, graph ≤1.500, **mỗi demo ≤1.500**; toàn prompt qua chat template + reserve 64 ≤8.192. Explanation/diff đầy đủ và được tính vào tổng budget.
- Selector xét toàn bộ pool theo exact mean token-set Jaccard và tie theo pair ID đã quy định. Không top-k heuristic/B2 anchor/fallback; pair được chọn không vừa thì báo lỗi, không rerank, cắt demo trái hợp đồng hoặc bỏ target.
- Rebuild cùng input/code/pool/tokenizer phải cho cùng selection/prompt bytes/hash. Có thay đổi phải version lại và kiểm phần ảnh hưởng trước inference.

Nếu chỉ một dataset đạt, dataset kia vẫn BLOCKED. Triển khai riêng dataset cần quyết định phạm vi bằng văn bản và manifest riêng trước inference; không suy thành full 5.005 đã đạt.

**G4 — Notebook/runtime:** chỉ B3 trong lịch GPU. Delivery pin input/prompt/pool/worker/helper/runtime hashes; Kaggle source readback khớp, dùng prompt đã freeze. Kiểm môi trường thật theo contract đã chọn trong kế hoạch: model SHA, bảy package sau cài, backend source/build, Python/CUDA/driver/thread/constructor. Native log phải chứng minh T4×2, offload 49/49, `n_ctx=8192`, batch/ubatch 256 và các settings còn lại đúng contract. `RUNNING` hay request T4×2 không phải acceptance.

Kiểm scoring/token IDs/chat template và tính lại `sigmoid(logit_1-logit_0)` từ full logits/logprobs; phân biệt seed prompt với seed constructor theo contract. Thử checkpoint/graceful exit/download/resume một lần có kiểm identity; sai method/pool/prompt/model/tokenizer/scoring/runtime phải bị từ chối. Fixture/replay output tách khỏi census. Chỉ sau G4 đạt mới full validation; không cần lặp test runtime vô hạn khi release không thay đổi.

### 7. Quy tắc bắt buộc xuyên suốt

1. Giữ nguyên protected branch/tag, OSF bundle, preregistration, frozen threshold/arms/specs/banks và lịch sử worklog theo AGENTS.md. Đề xuất thay phương pháp phải có quyết định/deviation rõ trước khi áp dụng, không tự sửa để vượt audit.
2. Giữ nguyên artifact v1/v2/v3 và audit trước; mọi ingest/build mới dùng version/thư mục mới. Test corruption chỉ trên bản sandbox; không sửa file thật rồi cố khôi phục.
3. Không chế source metadata, review con người, chữ ký, adjudication, log runtime hoặc bằng chứng OSF approval. Phân loại amended/confirmatory phải theo governance có bằng chứng; PDF đề xuất không tự chứng minh registration stamp.
4. Không trộn donor giữa dataset, không dùng target/test labels hoặc score để chọn pair/pool. Không tuyên bố không tồn tại pair từ phạm vi tìm kiếm hạn chế. Lỗi mạng, nguồn thiếu hay pool rỗng là trạng thái phải ghi nhận trung thực.
5. Không thêm B3-nodiff/swap/flip vào lịch GPU hiện tại. CPU helper render các biến thể để test không đồng nghĩa được phép launch chúng.
6. Phương pháp mới bắt đầu từ 0 score; không migrate score historical B3 hay gắn runtime provenance mới hồi tố. Resume chỉ nhận records cùng identity, phát hiện duplicate ID khác score.
7. Chỉ tính threshold sau validation đủ và accepted. Tính lại từ score mới theo grid/tie rules trong kế hoạch, lưu grid/confusion counts và lock riêng; không sửa frozen threshold configs hoặc lấy số từ tài liệu. Chỉ sau lock mới chạy test census **5.006** của hai dataset.
8. Không interim stopping theo metric, không giảm census cho vừa ngân sách, không bỏ invalid tùy tiện hay tự điền score. Dừng do giới hạn hạ tầng rồi resume được phép, nhưng phải lưu checkpoint/provenance và hoàn tất fixed census.
9. `PASS` cần bằng chứng thật cho mọi điều kiện bắt buộc. `BLOCKED`, `NOT_EVALUATED`, `FAIL` phải giữ đúng nghĩa; unit tests qua không thay source verification, human review hoặc runtime acceptance.

**Mốc nghiệm thu tiếp theo:** candidate thật đầu tiên với source archive đủ, kèm kết quả kiểm G1. Những test còn thiếu cho ingest/release hoàn thiện trước G2/G3 tương ứng; không trì hoãn tìm nguồn để chạy lại toàn bộ audit hiện tại.
