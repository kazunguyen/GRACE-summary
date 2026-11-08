# Re-audit B3 mới sau khắc phục — 08/11/2026

Mốc bắt đầu: 22:22:59 Asia/Saigon. Đối tượng: các artifact hiện có trong `release_20261108_v5`, notebook đóng gói, code build/Step8/tests và trạng thái pool REVEAL. Không chạy builder, cài backend, tải dữ liệu hoặc launch Kaggle; không chỉnh release của người dùng.

**Kết luận: CHƯA SẴN SÀNG CHẠY B3 MỚI.** Devign vẫn bị chặn ở delivery CPU preflight; REVEAL vẫn không có pair admitted. Mục tiêu chạy cả hai dataset chưa đạt. Không thể đóng các finding bằng số test PASS hoặc báo cáo publish khi notebook phát hành chưa được sửa.

## 1. Đối chiếu thay đổi thực tế

- So inventory lần trước: **19 file đã đổi**, gồm manifests/reports/ZIP và builder delivery. Có thêm dataset metadata và các biến thể account. Các thay đổi này là có thật.
- Nhưng **notebook vẫn nguyên SHA-256** `ca2c40b804cc4a2f3fe7938914bc82d674206901170cae1e3cf690c61d4fef70`, đúng notebook lần trước đã tái hiện lỗi. Kernel metadata chính cũng vẫn trỏ `huuhieu/...`.
- Pool/review/source cần thiết giữ nguyên: **58 artifact** so với inventory nguồn trước đều khớp. Không cần yêu cầu duyệt lại cùng payload Devign.
- Prompt Devign giữ đúng fingerprint `dee4a33009f4ecbf42b96e6f18c5f4390d5f0a620370af925bae0f2cceeb7e59`: 2.732 target duy nhất, mọi prompt hash đúng. Không cần re-render lại.
- Tính lại 7 seals: đúng; file hashes của delivery/ZIP members đúng; ba links upstream trong prompt manifest đúng; code inventories hiện tại khớp. Đây là tính toàn vẹn của snapshot hiện tại, chưa chứng minh consumer thực thi đúng.
- Step7 log ghi nhận 54 + 6 + 20 + 11 = **91 passed**. Audit này đọc và đối chiếu log, không chạy lại bốn suite vì đã có counterexample trực tiếp ở notebook thật và không cần tăng khối lượng testing.

## 2. Các finding còn mở

| Mã | Mức độ | Bằng chứng hiện tại | Điều kiện đóng |
|---|---|---|---|
| R1 | Blocker | Cả2.732 inference rows vẫn chỉ có `target_id`, không có `id`/`label`. Thực thi nguyên cell4 với ZIP thật trong sandbox tiếp tục báo **`KeyError: 'id'`** | Adapter nối ID/label từ frozen validation; notebook và worker cùng đọc được bundle thật; không đưa label vào prompt/selector |
| R2 | Cao | Notebook nguyên bytes; không pin/đọc inference input root độc lập. Thử sửa prompt + self-declared hash vẫn qua phần loader trước dòng lỗi R1 | Kiểm external manifest pin, seals và mọi required member; ZIP/unpacked/ambiguous/tampered inputs đều xử lý đúng trước model |
| R3 | Cao | `validate_records()` vẫn báo **`NameError: name 'math' is not defined`** với fixture record. Helper dùng regex `Device n: ... T4`; log native đang có cho backend chỉ cho **0 match**, dù có2 dòng `using device CUDA...` | Import notebook đúng; parser thật nhận format native, vẫn giữ gate2 GPU phân biệt/49 layers/context/batch |
| R4 | Cao | Restore/worker vẫn là source cũ: chưa đủ checkpoint inventory/path containment, missing-manifest/provenance gates và stable identity binding | ZIP/unpacked checkpoint đúng resume được; sai method/pool/runtime/input, thiếu manifest hoặc unsafe paths bị chặn; record/provenance cũ giữ nguyên |
| R5 | Cao, sửa một phần | Có thêm dataset/account metadata nhưng kernel chính vẫn `huuhieu/...`, chưa có request/readback shape trong hồ sơ launch được kiểm; notebook không thay. Các điểm commit/authority literal và release publishing của audit trước chưa được đóng bằng bằng chứng mới | Chốt account/dataset đúng, pin source/input, T4x2 request và readback; provenance/authority trung thực; version/publish không ghi đè release frozen |
| RV | Blocker cho hai tập | `pools/eligible_pairs.reveal.jsonl` vẫn rỗng; pool manifest ghi `admitted_pairs_count=0`, `BLOCKED_EMPTY_POOL`; execution scope loại REVEAL | Phục hồi actual source/fix/parent và mapping vào hai REVEAL clean-train donors, hai review thật cùng payload, seal pool rồi full prompt audit2.273 |

Các ca input tamper/record nói trên chạy trên bản sao sandbox; không sửa release thật và không sinh score nghiên cứu. Native log B1-full chỉ dùng kiểm regression format parser, không dùng thay runtime acceptance B3.

### Vì sao 91 tests PASS nhưng notebook vẫn lỗi?

Một số test delivery hiện kiểm logic viết lại ngay trong test thay vì gọi consumer thật:

- `test_t08_zip_and_unpacked_parser`: tự đọc ZIP/JSON; ca ambiguous chỉ kiểm `len(candidates)>1`, không gọi loader notebook để chứng minh nó từ chối. Fixture rows dùng `id`, trong khi bundle thật chỉ có `target_id`.
- `test_t09_checkpoint_resume_identity_rejection`: tự định nghĩa `validate_row()` và import `math` trong test, nên không phát hiện notebook thiếu import.
- `test_t11_runtime_log_native_parser`: tự định nghĩa parser và dùng fixture dạng cũ `Device 0: ...`; chưa kiểm helper thật trên format native thực tế.
- `test_t12_manifest_and_gate_verdict_integrity`: tự dựng dictionary `gates` toàn trạng thái mong muốn rồi assert dictionary đó; sự hiện diện của seal field không thay cho tính seal hoặc integration acceptance.

Các test này có thể PASS đúng theo assertions của chúng, nhưng **chưa chứng minh T8/T9/T11/T12 của delivery thực đã đạt**. Không có cơ sở gọi “CPU PREFLIGHT ACCEPTED” như báo cáo publish hiện tại. Cần đổi đúng vài kiểm tra integration sang gọi loader/validator/helper thực và bundle đóng gói, thay vì bổ sung thêm test mô phỏng cùng logic.

## 3. Tình trạng riêng REVEAL

Không thấy hồ sơ recovery mới trong release được kiểm. Step4 provenance script vẫn là bản chỉ kiểm assets cục bộ, không có bước acquisition/upstream recovery. Không suy từ đây rằng upstream không thể cung cấp pair; chỉ kết luận **chưa có bằng chứng khắc phục nhánh RV trong bộ hồ sơ hiện tại**.

Các file mới `dataset-metadata.*.json` là cấu hình upload dữ liệu Kaggle; chúng không phải source mapping, actual patch evidence, review hoặc pool pair cho REVEAL.

Để đủ hai dataset, phải thực hiện lộ trình RV1–RV7 ở [audit trước, mục6](../independent_v5_readiness_audit_20261108_211003/AUDIT_REPORT.md): inventory → phục hồi lineage distribution → tìm candidate → actual fix/parent/source mapping vào clean bank → hai reviewer → full2.273 prompt → delivery preflight. Không lấy pair Devign thay REVEAL; không tự thêm external donor hay thay bank frozen. Chưa có pair đạt chuẩn thì không thể mở run verified-patch REVEAL hợp lệ chỉ bằng sửa notebook.

## 4. Governance và version

Release v5 đã mang trạng thái `FROZEN` và có inventory tại lần audit trước, nhưng19 file nay khác bytes ngay trong cùng đường dẫn/identity. Hash chain mới đúng không bảo toàn identity snapshot cũ. Đây là điểm chưa tuân thủ nguyên tắc immutable release của kế hoạch, không phải lý do bác bỏ lại review/source Devign vốn không đổi.

Giữ inventory/audit cũ làm lịch sử; không sửa/xóa chúng để hợp thức hóa thay đổi. Ghi nhận việc rebuild v5 trong `CHANGES_AFTER_PREREG.md` với phạm vi/hash trước-sau; phát hành bản sửa dưới input release/delivery revision mới. Không tự thay đổi protected OSF assets, frozen bank/spec/threshold hoặc đổi method ID nếu thuật toán không đổi.

## 5. Việc cần làm tiếp, theo thứ tự

1. **Sửa executable artifact:** đóng R1–R4 trong source dùng để sinh notebook, rồi kiểm notebook sinh ra thực sự đổi và chứa bản sửa. Chốt R5; tránh tiếp tục chỉ cập nhật metadata/report.
2. **Chạy integration vừa đủ:** loader notebook + worker với bundle thật; ZIP/unpacked; tiny checkpoint đúng và sai identity; external-pin tamper; validator record; helper parser trên native log. Không cần rerun full prompt Devign. Các fixture phải được ghi rõ, không đóng vai review/source/GPU evidence.
3. **Triển khai recovery REVEAL:** thực hiện RV1–RV5 trước; khi có pool mới hợp lệ mới dựng và audit full prompt REVEAL2.273. Không đánh dấu đã hoàn tất nhánh này khi chưa có evidence.
4. **Publish version mới:** state/manifest/hash/authority/commit + dirty-source inventory phản ánh đúng artifact. Đạt CPU preflight mới chuyển kiểm kỹ thuật GPU; chưa gọi full validation READY trước native evidence.
5. **GPU và validation:** nghiệm thu runtime thật, chạy validation theo từng dataset đủ N; sau đó threshold riêng từng tập, rồi test deliveries riêng. Có thể chạy tuần tự trên cùng account, không yêu cầu hai tập cùng một session. Trước khi REVEAL đạt, Devign chỉ là nhánh triển khai một phần mục tiêu.

| Phạm vi | Verdict hiện tại | Có thể làm ngay |
|---|---|---|
| Devign | **BLOCKED_DELIVERY_PREFLIGHT** | Sửa/kiểm delivery; tái sử dụng source/review/prompt |
| REVEAL | **BLOCKED_EMPTY_POOL** | Recovery nguồn/pair từ đúng frozen clean-train bank |
| Full validation hai tập | **NOT_READY** | Hoàn tất cả hai nhánh, sau đó nghiệm thu runtime thực |

## 6. Bằng chứng tái lập

- [Kết quả audit JSON](audit.json), [delta19 file](changes_since_previous.json), [inventory hiện tại](source_inventory.json), [log](console.log), [script re-audit](reaudit.py).
- Lệnh: `python Runs-management/b3_verified_patch_v1/independent_v5_reaudit_20261108_222259/reaudit.py` từ repo root; tái sử dụng script audit trước, ghi vào thư mục mới. Exit0 chỉ nghĩa kiểm tra hoàn tất, không phải verdict PASS.
- Phạm vi kết luận là artifact trên đĩa tại thời điểm audit. Không có API readback/phiên GPU mới nào được gọi trong lần này.
