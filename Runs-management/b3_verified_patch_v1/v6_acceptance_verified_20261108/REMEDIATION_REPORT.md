# B3 mới — kết quả khắc phục và trạng thái bàn giao

Ngày08/11/2026. Phạm vi: sửa delivery thực, kiểm source REVEAL, chuẩn bị chạy trên account đã chỉ định. Không chỉnh OSF/frozen configs/spec/banks, không sửa release v5 và không launch GPU.

**Phần kỹ thuật delivery Devign đã sửa và đạt CPU integration. REVEAL đã phục hồi được một candidate có bằng chứng nguồn; hiện chờ hai review thật. Chưa thể tuyên bố full validation hai dataset READY.** Ngoài gate review, account huuhieu3333 hiện không đủ quota cho request9h.

## 1. Bản nào dùng tiếp?

- Delivery mới: [release v6](../release_20261108_v6/release_manifest.json), [notebook](../release_20261108_v6/delivery/notebook.ipynb), [input root](../release_20261108_v6/delivery/inference_input_manifest.json).
- `method_id=b3-verified-patch-v1`; parent input là v5, scope B3/Devign/validation/seed42/N2.732. v5 chỉ còn là lịch sử/evidence, không dùng notebook v5 để chạy tiếp.
- Trạng thái v6 là `CPU_PREPARED_NATIVE_PENDING`, không phải native runtime PASS. Prompt fingerprint giữ nguyên `dee4a33009f4ecbf42b96e6f18c5f4390d5f0a620370af925bae0f2cceeb7e59`; inference rows có hash riêng sau nối label metadata.
- REVEAL cần release/input mới sau admission; không chèn ngầm vào v6 Devign. Native/model/scoring/runtime profile phải giữ cùng contract.
- Input Devign đã được upload và server xác nhận **ready, PRIVATE**: [huuhieu3333/grace-b3-v6-devign-inputs](https://www.kaggle.com/datasets/huuhieu3333/grace-b3-v6-devign-inputs). [Receipt](private_dataset_upload.json), [visibility readback](private_dataset_visibility.json). Không upload candidate REVEAL chưa được duyệt.
- Khi launch phải dùng [prepared SDK request](prepared_launch_request.json), có model kernel source và T4 shape đầy đủ. `kernel-metadata.json` trong snapshot delivery là base template, không dùng trực tiếp bằng CLI cũ vốn bỏ trường shape. Source notebook và input root vẫn đúng SHA trong release manifest.

## 2. Các lỗi delivery đã xử lý

| Finding | Sửa thực tế và kiểm tra |
|---|---|
| R1 schema | Adapter tạo `id=target_id`, nối nhãn frozen validation theo đúng ID; kiểm population một-một. Không thay prompt/selector, không đưa nhãn vào prompt |
| R2 input pin | Notebook pin SHA input-root độc lập, kiểm seal/root, external ZIP hash và toàn bộ member hashes. Unpacked kiểm cùng inventory và tái tạo đúng ZIP bytes; ambiguous roots/tamper bị từ chối |
| R3 math/parser | Kiểm record dùng module chung import `math` thật; parser chung nhận native CUDA0/CUDA1 và kiểm hai device phân biệt,49/49 layers, effective context/batch/ubatch |
| R4 resume | Checkpoint inventory, path containment, method/pool/model/prompt/runtime/code identity, duplicate IDs, score/logprob consistency và provenance/log hashes. Restore atomic; explicit resume không tìm thấy input sẽ fail; record cũ giữ nguyên bytes |
| R5 deployment | Request chuẩn bị riêng cho huuhieu3333, T4 shape, timeout và model kernel source đúng account; lưu actual commit/dirty-source hashes. Model source đọc được version1. Source readback/server shape/native evidence chỉ có thể nghiệm thu sau launch thật |

Mã nguồn dùng chung: `scripts/b3_delivery_runtime.py`; bản byte-exact được nhúng trong notebook và đóng kèm delivery. Các tests gọi consumer thật hoặc code đã phát hành, không chỉ mô phỏng logic trong test.

## 3. Verification vừa đủ

| Suite | Passed |
|---|---:|
| Delivery v6 integration | 7 |
| Explicit REVEAL source-mapping boundary | 3 |
| Amended B3 | 54 |
| Preregistration integrity | 6 |
| Probes | 20 |
| Statistics/complementarity | 11 |
| **Tổng** | **101** |

[Acceptance JSON](acceptance.json) và `suite_0.log`…`suite_5.log` là kết quả chạy thật trên source ổn định cuối. Có thêm [negative admission check](admission_negative_check.log): hai template trống bị chặn trước tạo pool. Các fixture provenance/log trong kiểm resume là fixture được ghi rõ, không phải bằng chứng GPU.

Các lần thử trước được giữ ở các thư mục acceptance riêng. Không tính các lượt fail trước sửa là PASS; không rerender prompt Devign vì nội dung giữ nguyên. REVEAL chưa render census vì review chưa đạt.

## 4. REVEAL: đã vượt qua việc chỉ thống kê thiếu metadata

Đã truy tìm [repository tác giả ReVeal](https://github.com/VulDetProject/ReVeal) và archive các scripts tại revision `ca31b783384b4cdb09b69950e48f79fa0748ef1d`. Script nguồn trỏ tới CSV Google Drive1.448.744.816 bytes. Chỉ tải range đầu1MiB, giữ response range và trạng thái partial; không tuyên bố đã tải/audit toàn bộ CSV.

Hai dòng CSV hoàn chỉnh cho `mprintf.c`, hash distribution `-8228664527580018723`, nối được với hai donor **đều keep_in_bank=true**:

- `reveal:train:16061`, label1 — `alloc_addbyter` trước sửa.
- `reveal:train:17887`, label0 — cùng hàm sau sửa.

Actual security fix: `curl/curl`, `lib/mprintf.c`, commit `8732ec40db652c53fa58cd13e2acb8eab6e40874`; parent trực tiếp `ee4f76606cfa4ee068bf28edd37c8dae7e8db317`. [Advisory chính thức CVE-2016-8618](https://curl.se/docs/CVE-2016-8618.html) trỏ tới fix này. Đã lưu full before/after/diff và kiểm áp toàn patch với context nguyên vẹn tái tạo đúng after-file.

Donor đã token hóa formatting/comments, khác raw upstream. Bổ sung mapping **tường minh** `c_lexical_tokens_v1`: chuỗi C tokens phải khớp tuyệt đối; giữ nguyên literals/strings/compound operators, không nhận directives hoặc comment hỏng. Raw upstream changed lines vẫn phải được actual diff gốc hỗ trợ. Không viết lại actual diff, không áp ngoại lệ dòng trống Devign sang REVEAL. Mapping nằm trong payload mà hai reviewer phải duyệt.

Packet: [REVIEW_PACKET.md](../reveal_recovery_20261108/case_reveal_curl_alloc_addbyter_16061_17887/REVIEW_PACKET.md).

Payload cuối: `537b1732aa7cc6dbc3821044275e1364568c6a0893999262b9e5f1264a1c71a7`.

**Trạng thái: TECHNICALLY_VERIFIED_UNREVIEWED.** Phiếu [Hiếu](../reveal_recovery_20261108/case_reveal_curl_alloc_addbyter_16061_17887/review_hieu.template.json) và [Dũng](../reveal_recovery_20261108/case_reveal_curl_alloc_addbyter_16061_17887/review_dung.template.json) đều trống quyết định/criteria/nhận xét/thời gian. Không dùng review Case08 Devign cho pair mới.

## 5. Điều kiện ngoài mã nguồn đang chặn

### Hai review REVEAL thật

Hai người duyệt độc lập packet/payload/mapping, điền final forms vào một thư mục riêng chỉ gồm các phiếu cuối và mọi phiếu bất đồng liên quan. Sau đó nạp bằng:

```powershell
python scripts/admit_reveal_curl_reviews.py --reviews-dir <thu-muc-phieu-that> --output Runs-management/b3_verified_patch_v1/reveal_reviewed_pool_20261108
```

CLI kiểm mọi form, timestamp, payload, consensus, bank/source/mapping/patch; không ghi pool khi thiếu phiếu hoặc còn reject/disagreement, và không ghi đè output cũ. Sau admission còn phải dựng/audit full REVEAL validation2.273 và delivery REVEAL mới; không coi admission là runtime PASS.

### Quota account

[Kiểm tra read-only](../v6_account_check_20261108.json) lúc15:45UTC: model source `huuhieu3333/qwen3coder30b-prepare-notebook` đọc được, version1. GPU quota còn **1.417,606 giây ≈23,6 phút**, refresh được API trả về là `2026-11-14T00:00:00Z`. Đây là quota API, không bảo đảm cùng số phút wall time với mọi accelerator/session.

[Request đã chuẩn bị](prepared_launch_request.json) khóa T4 shape/source, nhưng trạng thái là **BLOCKED_INSUFFICIENT_CURRENT_QUOTA** cho request9h. Không submit request dài vào account này ngay lúc kiểm. Cần quota đủ ở account được chốt hoặc quyết định account khác rõ ràng; không tự chuyển private artifacts sang account khác. Không tự đổi MAX_RUNTIME_HOURS/contract/checkpoint identity để che giới hạn.

## 6. Thứ tự hoàn tất tiếp

1. Hai review cuối cho REVEAL; nạp pool bằng CLI trên. Nếu có reject, giữ blocked và xử lý nội dung, không chọn bỏ phiếu từ chối.
2. Pool hợp lệ → full prompt census REVEAL2.273, adapter labels ngoài prompt, audit và đóng input/delivery release mới. Dùng cùng runtime/scoring và ghi rõ single-pair scope.
3. Chốt account có quota đủ; kiểm dataset/model mounts; dùng official SDK request giữ `machine_shape`, đọc lại source và server shape sau launch. Chưa có server readback thì không ghi launch đã nghiệm thu.
4. Native GPU technical acceptance → full validation Devign2.732 và REVEAL2.273. Không gộp historical scores hoặc dùng outputs kỹ thuật có run identity khác để bù census.
5. Đủ validation từng tập → tính/kiểm τ* riêng theo grid/rule đã khóa, lưu lock mới riêng → dựng/audit test delivery. Chưa chạy test trong giai đoạn này.

| Phạm vi | Trạng thái thật sau khắc phục |
|---|---|
| Devign CPU delivery | **PASS** |
| Devign native runtime / full validation | **PENDING; account9h request blocked by quota** |
| REVEAL source candidate | **TECHNICALLY VERIFIED; human review pending** |
| REVEAL admitted pool / full prompt / runtime | **PENDING REVIEW AND DOWNSTREAM GATES** |
| Full validation hai tập | **CHƯA READY**, vì còn hai review thật và quota/native gates |

Không có fake human review, fake native log hoặc kết quả inference mới trong hồ sơ này. Các thay đổi đã được ghi trong `CHANGES_AFTER_PREREG.md` và worklog riêng.
