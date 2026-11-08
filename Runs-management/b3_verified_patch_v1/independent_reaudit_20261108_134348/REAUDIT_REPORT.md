# Audit lại bản khắc phục B3 v2 — 08/11/2026

**Kết luận:** bản v2 đã khắc phục nhiều sai lệch trong hồ sơ và phản ánh đúng tình trạng dừng do pool rỗng. Tuy nhiên chưa thể đóng toàn bộ phát hiện hoặc dùng pipeline cho review thật, prompt freeze và notebook. Các nhánh xử lý khi có candidate/pool hợp lệ vẫn có lỗi đã tái hiện được.

**Có thể tiếp tục:** tìm và xác minh nguồn ở bước 3–4, sửa công cụ trong phiên bản mới, chuẩn bị source evidence. **Chưa được chuyển sang:** coi bước 1–8 hoàn tất, phát hành eligible pool bằng tool hiện tại, khóa prompt validation hoặc khởi chạy inference B3 mới.

Phạm vi đọc: release v1/v2, `REMEDIATION_REPORT.md`, công cụ tự kiểm tra khắc phục, mã bước 1–8 và tests. Audit không sửa chúng; các probe chỉ dùng dữ liệu synthetic trong thư mục thử riêng. Không có review người thật hoặc pair thực nào được tạo bởi lượt audit này.

## 1. Những thay đổi đã được xác nhận đúng

| Nội dung | Kết quả kiểm tra độc lập |
|---|---|
| Bảo tồn release v1 | 103/103 file release khớp hash trước khắc phục |
| Ba seal v2 | Inputs, pool và census seal đều tính lại khớp |
| Nguồn và dữ liệu đóng băng | Hash 6 module, 8 execution scripts, 2 tài liệu thẩm quyền, tokenizer và freeze files đều khớp manifest |
| Tách triage khỏi human review | Ledger v2 có 0 human review; 12 record được ghi nhãn triage tự động; không có biên bản giả dưới tên Hiếu/Dũng trong v2 |
| Source coverage | 17 response commit có hash khớp; 12/12 case có response cả hai phía |
| Logging hiện tại | 17 cache replay, 0 network call trong log lượt hiện tại; không nhầm số này thành 17 request HTTPS mới |
| Census validation | Đúng 2.732 Devign + 2.273 REVEAL, ID/code hash khớp; cả 5.005 PAUSED, prompt rỗng và cờ đánh giá null đúng |
| Ngân sách demo | Cách hiểu mỗi demo ≤1.500 có căn cứ từ DOCX paragraph 88 đã xác nhận ở audit trước |
| Governance | V2 bỏ claim đã có confirmatory stamp, ghi trạng thái amendment theo báo cáo người thực hiện; audit này không xác thực OSF trực tuyến |
| Tests hiện có | Chạy lại độc lập: **60 passed, 0 skipped** |

Việc sửa null flags và loại bỏ attribution review giả là sửa đúng. Hai pool vẫn có 0 pair; đây là trạng thái dữ liệu chưa sẵn sàng, không phải một lỗi cần vượt qua bằng fallback.

## 2. Các lỗi còn tồn tại, đã tái hiện hoặc đối chiếu trực tiếp

### R1 — Cao: packet và pair dùng hai payload hash khác nhau; review đúng theo form không admit được

Nguồn: [b3_step6_packet_tool.py](../../../scripts/b3_step6_packet_tool.py), dòng 66–94, 235–237 và 295–300.

`generate_review_packets` hash packet metadata gồm donor/parent/file/message. Template và `validate_review_form` yêu cầu review ký hash đó. Nhưng `validate_pair` yêu cầu hash **toàn pair trừ reviews**, bao gồm source functions, actual fix diff, changed lines, rationale và key difference.

Probe chạy đúng generator → triage → form validator → admission bằng một candidate synthetic hợp lệ cho thấy:

- Triage PASS; cả hai form đều được validator đầu vào nhận.
- Packet hash `bd0c7b58…` khác pair payload hash `20f0cb6e…`.
- Admission trả 0 pair với lỗi `Unresolved, stale or incomplete pair review`.

Test admission hiện có dựng `known_packets['payload_sha256'] = payload_hash(candidate)` thủ công, nên không đi qua generator thật và bỏ sót lỗi tích hợp này.

**Cần sửa:** packet phục vụ review phải đóng dấu đúng full pair payload mà core validator sử dụng, tham chiếu được archived source evidence đầy đủ; dùng cùng một hàm canonicalization tại mọi nơi. Thay bất kỳ nội dung evidence nào phải đổi payload và yêu cầu review lại. Không sửa hash của một phiếu đã được người thật xác nhận để làm nó khớp candidate khác.

### R2 — Cao: audit prompt có nội dung dùng sai marker và vẫn nhận trạng thái đã audit khi cờ lỗi

Nguồn: [b3_step8_validation_census_builder.py](../../../scripts/b3_step8_validation_census_builder.py), dòng 213–231; renderer chuẩn ở [probes.py](../../../01_Author_Baseline_Unified/diagnostic_kit/src/grace_diag/probes.py), dòng 32.

Builder tìm chuỗi `Question:`. Renderer chuẩn thực tế dùng câu bắt đầu `In the above code snippet...`, không có marker đó. Vì vậy trên prompt chuẩn:

- `.find('Question:')` trả -1 → cờ Figure 6 false.
- Không tách được prefix → regex quét toàn prompt, nhận nhầm nhãn demonstration là nhãn target.
- Dù vậy record vẫn được ghi `status=RENDERED`, `prompt_evaluation_status=RENDERED_AUDITED`.

Probe dùng actual render-and-audit AST block trong script, với selector chuẩn và tokenizer local đúng revision, tái hiện đủ ba hiện tượng. Block target được tách bằng parser chuẩn khớp code synthetic đầu vào; lỗi nằm ở phép audit.

**Cần sửa:** dùng constants/boundary hoặc parser block của renderer chuẩn; xét code hiển thị sau token fitting thay vì tìm nguyên chuỗi code gốc có thể bị cắt hợp lệ. Kiểm leakage theo đường dữ liệu/section, không quét nhãn demonstration thành nhãn target. Khi audit không đạt phải đánh dấu lỗi và chặn readiness. Tính lại manifest/status từ toàn bộ kết quả thực; `prompt_content_status` hiện còn gán cố định `BLOCKED_EMPTY_POOL_NO_PROMPTS_RENDERED` ngay cả khi sau này có render thành công.

### R3 — Cao: submitted form không hợp lệ vẫn có thể xóa pool đang tồn tại

Nguồn: [b3_step6_packet_tool.py](../../../scripts/b3_step6_packet_tool.py), dòng 349–377 và 419–438.

`submitted_reviews` chứa cả form bị reject. Khi có một form JSON sai schema, không admit pair mới và danh sách submitted vẫn khác rỗng. Điều kiện bảo tồn pool chỉ bảo vệ trường hợp không có submitted form; nhánh còn lại ghi `write_text('')`.

Probe trong sandbox với pool synthetic đã có và một file `{}` sai schema: pool từ **2.331 byte xuống 0 byte**. File release thật không bị tác động. Vì hai pool thật hiện rỗng nên chưa ghi nhận mất pair thực; rủi ro sẽ xuất hiện khi có pool được duyệt.

**Cần sửa:** lỗi nhập review phải giữ nguyên mọi artifact đã phát hành và trả lỗi; chỉ tạo release mới có manifest đầy đủ sau khi validation hoàn tất. Không mặc định ghi pool rỗng khi không admit được update. Nhánh bảo tồn pool cũ cũng phải kiểm nội dung/hash và count thật, không chỉ kiểm file khác rỗng rồi gán ACTIVE.

### R4 — Cao: có thể bỏ qua review reject để chọn hai approve; timestamp placeholder vẫn được nhận

Nguồn: [b3_step6_packet_tool.py](../../../scripts/b3_step6_packet_tool.py), dòng 281–295 và `validate_review_form`.

Probe tách riêng khỏi lỗi R1, dùng full pair payload hash nhất quán, cho kết quả:

- Hai reviewer approve và reviewer thứ ba reject → vẫn admit 1 pair; code lọc chỉ approve rồi lấy hai người đầu.
- `reviewed_at='YYYY-MM-DDTHH:MM:SSZ'` vẫn qua kiểm form.

Quy tắc hiện có yêu cầu xử lý bất đồng và hai review thật còn hiệu lực, không phải chọn một subset thuận lợi trong nhiều quyết định. Nếu chỉ hai người đã được chỉ định được quyền duyệt, tool cần kiểm reviewer ID theo danh sách đó và quy tắc supersession; hiện chưa có kiểm tra này.

**Cần sửa:** xác định hai reviewer ID ổn định, chuẩn hóa identity, kiểm timestamp thật và payload hiện hành; bất đồng hoặc nhiều phiên bản chưa adjudicate phải dừng. Không suy tính độc lập của người duyệt chỉ từ hai chuỗi tên khác nhau.

### R5 — Trung bình/Cao: một số cổng tổng hợp vẫn chưa kiểm điều kiện mà chúng tuyên bố

1. [audit_remediated_release.py](../remediation_audit_20261108/audit_remediated_release.py), dòng 175, 198, 247, 261, 275, 290 gán sẵn các chuỗi PASS. Biểu thức tổng hợp dòng 295–303 chủ yếu so lại những chuỗi đó và seal; không bắt buộc preservation, module/script hashes hay các boolean nội bộ đều đúng. Probe chạy actual verdict expression với preservation/hash flags false vẫn trả `all_remediations_passed=True`. **Các hash thực ở lượt audit này đều đúng**; probe chỉ chứng minh cổng sẽ không bảo vệ đúng khi input sai.
2. [b3_step7_verify_selector_renderer.py](../../../scripts/b3_step7_verify_selector_renderer.py), dòng 199–231, chỉ truyền pool Devign vào sample checker và bắt buộc mọi dataset report là PAUSED. Đây là kiểm tra hành vi dừng của pool rỗng; khi có pool hợp lệ và render thành công, cùng gate này sẽ đánh fail. Chưa phải cổng sẵn sàng cho pool không rỗng.
3. Step 8 đọc manifest/pool/spec nhưng chưa xác minh đầy đủ seal/hash chain trong chính entry point trước sử dụng. Constructor exception được quy về nhãn EMPTY_POOL dù có thể là một pool không rỗng bị hỏng. Cần phân biệt EMPTY, INVALID và RENDER_FAILED.

**Cần sửa:** mỗi status phải suy từ điều kiện tính được và trả exit code tương ứng; tách software negative test với real-data readiness check. Kiểm cả pool của dataset đang đánh giá, không cấp readiness khi chỉ một dataset đã sẵn sàng.

### R6 — Cao đối với bước source tiếp theo: vẫn dùng recorded commit/file overlap và trường nguồn suy đoán

Nguồn: [b3_step3_devign_investigation.py](../../../scripts/b3_step3_devign_investigation.py), phần status sau khi có hai response; [b3_step5_make_candidates.py](../../../scripts/b3_step5_make_candidates.py), dòng 120–148; triage trong packet tool.

V2 đã bỏ dummy diff và đã giới hạn kết luận về 12 case. Tuy nhiên pipeline vẫn yêu cầu hai recorded donor commits phải trực tiếp cha–con và cả hai commit đều sửa chung file; step 3 còn gán nhãn reject kể cả khi không tìm thấy lý do phủ định. Đây chưa thay thế việc xác minh code thực ở actual fix và parent. Commit trước đó chứa code before có thể không phải direct parent, và parent cũng không bắt buộc sửa cùng file trong chính commit của nó.

Nếu có `actual_fix.diff`, step 5 vẫn tự dựng repository `<project>/<project>`, chọn `shared_files[0]`, gán recorded commit vào fix/parent và tạo rationale chung `Authentic fix for...`. Ví dụ cách dựng repository này không cho ra đúng `FFmpeg/FFmpeg` khi project là `ffmpeg`. Source before/after được lấy lại từ bank, chưa có kiểm chứng độc lập rằng đúng hàm trích từ revision nguồn.

**Cần sửa:** tạo evidence sidecar với repo/path/function/fix/parent và lý do bảo mật có nguồn; archive file/hàm ở actual revisions, so byte/hash với hai donor. Chỉ dùng direct-parent/file overlap của recorded commits làm tín hiệu điều tra, không coi nó là bằng chứng đủ hoặc điều kiện loại tuyệt đối thay cho source mapping. Giữ unresolved khi chưa xác thực được quan hệ.

## 3. Đánh giá lại các phát hiện cũ

| Phát hiện trước | V2 đã sửa đúng | Phần còn mở |
|---|---|---|
| F01 — Review giả | Không còn tự sinh ý kiến/chữ ký người thật trong v2; 0 human reviews được ghi đúng | R1/R4: cơ chế nhận review thật chưa chạy đúng |
| F02 — Phủ định toàn bank/thiếu nguồn | Kết luận được giới hạn; 12 case đủ hai response | R6: mapping quan hệ actual source chưa hoàn chỉnh |
| F03 — Null prompt được báo đã audit | 5.005 null prompt có cờ null và scope đúng | R2: nhánh prompt có nội dung còn lỗi |
| F04 — Dummy diff | Đã bỏ dummy diff khỏi real-data pipeline | R6: repo/path/revisions/rationale vẫn suy đoán khi vào nhánh candidate |
| F05 — REVEAL thiếu provenance | Đã bỏ diễn giải source_id chưa có chứng cứ, ghi blocked | Phục hồi provenance vẫn là công việc chưa xong |
| F06 — Gate/logging/overwrite | Log cache/network rõ; test tokenizer chạy; Step 7 có Boolean gate | R3/R5: pool update và gate readiness còn lỗi |
| F07 — Confirmatory claim | Ghi trạng thái amendment có điều kiện, không giả định đã có stamp | Cần hồ sơ đăng ký/mốc áp dụng trước khi chứng nhận phân loại phân tích |

Không nên kết luận “đã giải quyết triệt để 7 phát hiện”. Có thể nghiệm thu các sửa đổi hồ sơ đã kiểm chứng và trạng thái safe pause hiện tại; chưa thể nghiệm thu toàn pipeline như công cụ sẵn sàng cho dữ liệu thật.

## 4. Bước tiếp theo cụ thể

**Ngay bây giờ có thể tiếp tục công việc CPU/source:**

1. Điều tra Devign bằng actual patch và file/hàm tại fix/parent; lập chỉ mục hash code trong bank để tìm counterpart đúng byte. Không thay bank hoặc mở rộng donor nguồn mà chưa có quyết định phương pháp riêng.
2. Phục hồi mapping repo/path/revision của REVEAL từ đúng phiên bản nguồn/pipeline dữ liệu. Giữ trạng thái unresolved cho mapping thiếu hoặc nhiều nghĩa.
3. Song song sửa R1–R6 trong phiên bản công cụ mới. Bổ sung kiểm thử tích hợp generator → form → admission → selector → render với dữ liệu synthetic được đánh dấu, bao gồm nhánh có pair hợp lệ, tamper, disagreement và update lỗi giữ nguyên pool.

**Trước khi chuyển sang prompt freeze/notebook phải có:** source pair hợp lệ trong clean train, hai phiếu review thật bind cùng full payload, pool được seal, builder nonempty qua kiểm thử tích hợp, và toàn census validation có prompt text/hash/content/token audit đạt. Sau đó mới thực hiện bước 9 chuẩn bị notebook B3-only cùng runtime lock đã chọn; inference và threshold mới đi sau các mốc đó.

## 5. Bằng chứng và cách kiểm

- [state_check.json](state_check.json): tính lại seal/hash, kiểm v1 preservation, source cache, census và trạng thái review/pool thực.
- [source_inventory.json](source_inventory.json): snapshot hash các release, remediation artifacts, scripts/tests và preview gốc trước khi chạy kiểm tra.
- [positive_path_probes.json](positive_path_probes.json): kết quả tái hiện R1–R5, chỉ dùng fixture synthetic.
- [probe_positive_paths.py](probe_positive_paths.py): gọi actual packet/review functions trong sandbox và actual AST block cho render/verdict; không thay assertions hay pipeline release thật.
- [pytest.log](pytest.log), [pytest_result.json](pytest_result.json): 60 passed. Harness [run_required_checks.py](run_required_checks.py) giữ nguyên assertions và chỉ chuyển hai lần ghi historical synthetic preview sang thư mục audit; tránh thay artifact cũ khi test tokenizer nay đã chạy được.
- [check_state.py](check_state.py): audit chỉ đọc; không chạy lại builder vào release đã nộp.

Các probe không phải evidence nguồn thật hoặc review của con người. Audit này không thực hiện source search toàn bank, không chứng nhận không tồn tại pair và không xác minh trạng thái OSF live. Không launch, hủy hay thay đổi kernel Kaggle nào.
