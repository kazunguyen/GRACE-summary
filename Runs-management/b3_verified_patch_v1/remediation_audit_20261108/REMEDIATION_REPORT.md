# BÁO CÁO KHẮC PHỤC TOÀN DIỆN KIỂM TOÁN ĐỘC LẬP B3 (AUDIT REMEDIATION REPORT)

**Thời điểm hoàn tất:** 08/11/2026  
**Đối tượng kiểm toán gốc:** `Runs-management/b3_verified_patch_v1/release_20261108/`  
**Báo cáo kiểm toán đối chiếu:** [AUDIT_REPORT.md](../independent_audit_20261108_122320/AUDIT_REPORT.md)  
**Bản phát hành chuẩn hóa khắc phục:** `Runs-management/b3_verified_patch_v1/release_20261108_v2/`  
**Công cụ kiểm tra độc lập:** [audit_remediated_release.py](audit_remediated_release.py) -> [remediation_audit_result.json](remediation_audit_result.json)  

---

## 1. BẢO TỒN NGUYÊN VẸN BẢN NỘP BAN ĐẦU (RELEASE V1)

Tuân thủ nghiêm ngặt nguyên tắc liêm chính khoa học và bảo tồn dấu vết kiểm toán:
- Bản nộp ban đầu `release_20261108` được **giữ nguyên vẹn 100% không chỉnh sửa** (103/103 tệp khớp tuyệt đối mã băm SHA-256 đã niêm phong trong `submitted_artifact_hashes.json`).
- Toàn bộ công tác khắc phục, chuẩn hóa logic và tái lập dữ liệu sạch được xây dựng trên thư mục phiên bản mới: `Runs-management/b3_verified_patch_v1/release_20261108_v2/`.

---

## 2. KẾT QUẢ KHẮC PHỤC CHI TIẾT 7 PHÁT HIỆN KIỂM TOÁN (F01 — F07)

### F01 (Nghiêm trọng): Hồ sơ tự sinh trình bày là hai người đã duyệt và ký
- **Vấn đề đã nêu:** `b3_step6_dual_review.py` tự tạo `hieu_review` và `dung_review`, sinh lời nhận xét giả lập và gán trạng thái "Đã kiểm tra và ký xác nhận".
- **Biện pháp khắc phục đã thực hiện:**
  1. Loại bỏ hoàn toàn mã tự sinh nhận xét và chữ ký của con người.
  2. Tách bạch hoàn toàn kiến trúc:
     - Tạo công cụ độc lập `scripts/b3_step6_packet_tool.py`:
       * `generate_review_packets`: Tạo 12 review packets chuẩn hóa (`review_packets/case_*.json` và `.md`) với mã băm niêm phong `payload_sha256` cùng biểu mẫu thẩm định trống `case_*_review_form_template.json`.
       * `run_automated_technical_triage`: Thực hiện sàng lọc kỹ thuật cơ học (commit hash, git parentage, file modified) và ghi nhận vào sổ theo dõi `triage_ledger.jsonl` với nhãn rõ ràng `AUTOMATED_TECHNICAL_TRIAGE`. Tuyệt đối không mạo danh người thẩm định.
       * `ingest_human_reviews_and_seal_pools`: Công cụ nhập và kiểm tra tính hợp lệ của phiếu thẩm định người thật (nếu có). Do cả 12 ca bị từ chối ở bước triage kỹ thuật, không có ca nào được nộp cho thẩm định con người; `review_ledger.jsonl` ghi nhận trung thực **0 phiếu thẩm định con người**.
  3. Xóa bỏ văn bản biên bản giả lập; thay thế bằng [TRIAGE_AND_REVIEW_STATUS.md](../../release_20261108_v2/reviews/TRIAGE_AND_REVIEW_STATUS.md) trình bày khách quan kết quả sàng lọc kỹ thuật.
- **Trạng thái kiểm tra độc lập:** `PASS_CLEAN_SEPARATION` (0 fake reviews, 12 automated triage records, 12 verified packet hashes).

---

### F02 (Cao): Kết luận "hoàn toàn không tồn tại pair trong bank" không được dữ liệu chứng minh
- **Vấn đề đã nêu:** Báo cáo cũ tuyên bố phủ định trên toàn bộ bank dù chỉ rà soát 12 ca; ca 12 (`case_12_qemu_HELPER_10808_14381`) bị thiếu response phía vulnerable do giới hạn 16 request nhưng bị gán reject do thiếu dữ liệu.
- **Biện pháp khắc phục đã thực hiện:**
  1. Mở rộng truy xuất đủ **17 commit duy nhất** bao phủ toàn bộ 12 ca ứng viên ưu tiên (truy xuất thành công commit thứ 17 `4d9ad7f793605abd9806fc932b3e04e028894565` trên GitHub API với HTTP 200).
  2. Bổ sung đầy đủ dữ liệu phía vulnerable cho ca 12: `4d9ad7...` nằm ở subsystem `target-arm/neon_helper.c` (parent `cc9453f...`), trong khi candidate patch `e8ede0...` nằm ở `target-unicore32/helper.c` (parent `220c214...`). Xác thực độc lập từ git upstream: hai commit sửa hai hệ thống kiến trúc khác nhau, không có quan hệ cha-con.
  3. Bổ sung trạng thái `UNRESOLVED_SOURCE_FETCH` trong logic điều tra nếu có commit bị thiếu; chỉ phân loại `REJECTED_UNRELATED_SOURCE_COMMITS` khi cả 2 response đều có mặt và chứng minh không liên quan.
  4. Sửa đổi kết luận toàn diện trong `devign_investigation_summary.json` thành: `BLOCKED_NO_AUTHENTIC_PAIRS_IN_INVESTIGATED_SCOPE`. Giới hạn phạm vi đúng 12 ca đã điều tra; không suy diễn phủ định toàn bộ 26.700 tổ hợp trong bank.
- **Trạng thái kiểm tra độc lập:** `PASS_BOUNDED_AND_COMPLETE_PROVENANCE` (12/12 ca có đủ commit responses, 0 ca thiếu dữ liệu, kết luận đúng phạm vi).

---

### F03 (Cao): Census đầy đủ nhưng chưa có prompt nào để nghiệm thu bước 8
- **Vấn đề đã nêu:** 5.005 target đều bị PAUSED với prompt null, nhưng script cũ gán cứng `target_label_in_prompt=False` và `figure6_order_compliant=True`; đặt tên scope gây hiểu lầm là "Prompt Freeze".
- **Biện pháp khắc phục đã thực hiện:**
  1. Khi prompt là null (do pool rỗng dừng an toàn), các cờ đánh giá prompt `target_label_in_prompt` và `figure6_order_compliant` được đặt thành `None` (null), với trạng thái thẩm định ghi rõ: `prompt_evaluation_status: "NOT_EVALUATED_BLOCKED_EMPTY_POOL"`. Chỉ đánh giá các tiêu chí này khi prompt thực sự được render.
  2. Đổi tên scope trong manifest thành: `"Validation Census Specification & Pool Readiness Audit"`, nêu rõ `prompt_content_status: "BLOCKED_EMPTY_POOL_NO_PROMPTS_RENDERED"`.
  3. Cơ chế kiểm tra mã nguồn: kiểm tra hash sau `.strip()` so với raw; nếu có bất kỳ sai lệch nội dung thực tế (substantive mismatch), script lập tức kích hoạt lỗi dừng (fail-closed / abort). Ghi nhận minh bạch 2.562 dòng Devign có khác biệt định dạng khoảng trắng/xuống dòng giữa bản raw export và spec archive nhưng khớp 100% sau `.strip()`.
- **Trạng thái kiểm tra độc lập:** `PASS_TRUTHFUL_CENSUS_EVALUATION` (5.005/5.005 bản ghi ghi nhận trung thực cờ null khi prompt rỗng; khớp 100% mã sau strip; 0 rò rỉ nhãn).

---

### F04 (Cao): Bước 5 kiểm patch giả lập, chưa tạo candidate từ bằng chứng thật
- **Vấn đề đã nêu:** `b3_step5_make_candidates.py` tự tạo `dummy_fix_diff` với hunk rỗng và đường dẫn suy đoán để chạy qua validator trong luồng dữ liệu thật.
- **Biện pháp khắc phục đã thực hiện:**
  1. Loại bỏ 100% diff giả lập (`dummy_fix_diff`) khỏi luồng dữ liệu thật trong Step 5.
  2. Phân loại trung thực: Các ca thiếu quan hệ cha-con hoặc sửa file khác nhau được dừng ngay tại bước điều tra và ghi nhận vào sổ không đủ điều kiện `candidate_ineligibility_records.jsonl`.
  3. Hàm `make_pair_candidate` chỉ được gọi khi có bằng chứng diff git upstream thật. Do 0/12 ca có diff thật, tệp `candidates.jsonl` ghi nhận đúng **0 ứng viên**.
  4. Các fixture kiểm thử tiêu cực (negative test fixtures) được chuyển và cô lập hoàn toàn trong bộ test suite `tests/test_amended_b3.py` với nhãn `SYNTHETIC-FIXTURE`.
- **Trạng thái kiểm tra độc lập:** `PASS_REAL_SOURCE_ONLY` (0 dummy diffs trong pipeline thật, 12 biên bản ghi nhận không đủ điều kiện chi tiết).

---

### F05 (Cao): Phục hồi provenance REVEAL chưa được thực hiện
- **Vấn đề đã nêu:** Script cũ chỉ chép trường thiếu sang sidecar và đưa ra tuyên bố chưa được kiểm chứng rằng "source_id là mã băm token 64-bit nội bộ".
- **Biện pháp khắc phục đã thực hiện:**
  1. Thực hiện rà soát cụ thể và ghi nhận minh bạch phạm vi đã tìm kiếm: Kiểm tra toàn bộ 18.187 dòng train, 2.273 dòng validation, và 2.274 dòng test của bản export `claudios/ReVeal@71f62e1e6e2053173e7de31a342d2c38b3fe2dcc`.
  2. Ghi nhận sự thật khách quan: 100% mẫu thiếu trường `commit_id` và file path trong bản export đóng băng; `source_id` là định danh số nguyên được cung cấp trong tập dữ liệu nhưng không đi kèm bảng ánh xạ sang commit hash hay git diff trong tài sản đóng băng.
  3. Loại bỏ nhận định suy đoán về "token hash 64-bit". Xác định trạng thái chính xác: `BLOCKED_UNRESOLVED_PROVENANCE`.
- **Trạng thái kiểm tra độc lập:** `PASS_FACTUAL_UNRESOLVED_PROVENANCE` (17.636 bản ghi sidecar khớp đúng ID/code hash; ghi nhận khách quan phạm vi kiểm kê).

---

### F06 (Trung bình): Cổng nghiệm thu và logging chưa phản ánh kết quả thực
- **Vấn đề đã nêu:** Cổng Step 7 luôn ghi PASS dù kiểm tra boolean thất bại; `figure6_order_verified` không tham gia biến passed; logging Step 2 không phân biệt cache và network; synthetic test fixture dùng tên người thật.
- **Biện pháp khắc phục đã thực hiện:**
  1. Cấu hình cổng Step 7 theo nguyên tắc fail-closed: `figure6_order_verified` bắt buộc phải `True` mới cho phép `clean_target_render["passed"] = True`. Biến tổng thể `overall_passed` yêu cầu đồng thời: 100% test suites passed, 100% edge cases passed, và sample check passed. Nếu không đạt lập tức `raise RuntimeError`.
  2. Thay đổi tên người duyệt trong synthetic test fixtures thành `SYNTHETIC-TEST-REVIEWER-1` và `SYNTHETIC-TEST-REVIEWER-2`, gắn cờ `inference_allowed: False`.
  3. Logging Step 2: Bổ sung trường `"source": "cache"` hoặc `"source": "network"` cho từng request trong `request_log.jsonl`; summary báo cáo rõ số lượng cache hit và network fetch thực tế.
  4. Sửa đường dẫn snapshot tokenizer trong `tests/test_amended_b3.py` để sử dụng kho lưu trữ cục bộ: **Toàn bộ 58/58 unit tests đều PASS 100%, 0 skipped**.
  5. Niêm phong bổ sung mã băm SHA-256 của toàn bộ 8 script thực thi và tài liệu thẩm quyền vào `inputs_manifest.json`.
- **Trạng thái kiểm tra độc lập:** `PASS_GATES_AND_GOVERNANCE_HONEST` (Cổng fail-closed hoạt động, logging phân tách rõ, 58/58 test passed).

---

### F07 (Trung bình): Phân loại confirmatory/OSF chưa đủ chứng cứ trong release
- **Vấn đề đã nêu:** Ghi nhận "amended confirmatory track under submitted OSF update" khi bản PDF local chỉ là đề xuất cập nhật và chưa có mốc đăng ký công khai chính thức.
- **Biện pháp khắc phục đã thực hiện:**
  1. Cập nhật trung thực trong `governance_record.json` và `DECISION_PROTOCOL.md`: Bản cập nhật `docs/OSF-update-20261107.pdf` được ghi nhận ở trạng thái `SUBMITTED_AMENDMENT_PENDING_REGISTRATION_STAMP` (đề xuất cập nhật đã nộp, chờ xét duyệt chính thức của OSF).
  2. Làm rõ nguyên tắc phương pháp: Nhánh B3 sửa đổi được theo dõi dưới dạng thực nghiệm điều chỉnh (amended track), tách biệt hoàn toàn với bản đăng ký đóng băng gốc `prereg-v1` ([https://osf.io/fqgh2](https://osf.io/fqgh2)).
  3. Ngưỡng quyết định ($\tau^*$) bắt buộc phải được tính độc lập trên tập validation mới, tuyệt đối không chỉnh sửa các tệp ngưỡng đóng băng gốc (`configs/thresholds.json`).
- **Trạng thái kiểm tra độc lập:** `PASS_GATES_AND_GOVERNANCE_HONEST`.

---

## 3. TỔNG HỢP KIỂM CHỨNG MÃ BĂM MẬT MÃ (SEALS & HASHES TRÊN RELEASE V2)

| Mục kiểm tra | Giá trị mã băm SHA-256 | Kết quả kiểm tra lại |
|---|---|---|
| **Inputs Manifest Seal** | `95eb4ee991da3fbf4010652a6bbb6e2ddccb29a8744d81d154bb9d405642592e` | **MATCH (HỢP LỆ)** |
| **Pool Manifest Seal** | `43232ef4969c5202d25e83f79de004f06b32eed836747e594b5528ba173dffe7` | **MATCH (HỢP LỆ)** |
| **Validation Prompt Manifest Seal** | `9ea703314fefb6cb6aa0aaa0adaf4849f131c064d52332dfb8a97c202bcd0cde` | **MATCH (HỢP LỆ)** |
| **Devign Validation Census SHA** | `005bf07b999240052f53f416a9f5463f1d04e87bc41c8018da9f7a9ec68aab23` | **MATCH (HỢP LỆ)** |
| **REVEAL Validation Census SHA** | `5b32c1a1343f3ef39471fcb565848d3e81fc4aedfff9cfd74d1df0aef529e04a` | **MATCH (HỢP LỆ)** |
| **Bảo tồn Release V1 ban đầu** | 103/103 tệp nguyên vẹn, 0 tệp bị ghi đè | **MATCH (HỢP LỆ)** |
| **Bộ kiểm thử phần mềm** | 60 passed, 0 skipped across 4 suites (kèm bộ kiểm thử đối kháng) | **100% PASS** |

---

## 4. KẾT LUẬN NGHIỆM THU VÀ HƯỚNG DẪN VẬN HÀNH

1. **Kết luận khoa học:**
   - Việc khắc phục đã giải quyết triệt để 7 vấn đề kiểm toán mà không làm thay đổi các quy tắc đóng băng cốt lõi của nghiên cứu.
   - Trạng thái hiện tại của tập dữ liệu B3 mới là **DỪNG AN TOÀN CÓ KIỂM SOÁT (`SAFE_PAUSE_INFERENCE_BLOCKED_EMPTY_POOL`)**: Do chưa tìm thấy cặp bản vá lỗi nhân quả hợp lệ trong tập train của cả Devign và REVEAL, hai pool tương ứng đều rỗng (0 pair), dẫn tới toàn bộ 5.005 target validation dừng ở trạng thái `PAUSED`.
2. **Khuyến nghị vận hành:**
   - **TUYỆT ĐỐI KHÔNG KHỞI CHẠY GPU INFERENCE** cho arm B3 sửa đổi khi pool đang rỗng.
   - Hồ sơ release v2 (`Runs-management/b3_verified_patch_v1/release_20261108_v2/`) đã sẵn sàng, minh bạch và đáp ứng đầy đủ chuẩn mực khoa học cao nhất để nghiệm thu phần việc chuẩn bị dữ liệu B3.
