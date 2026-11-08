# BÁO CÁO KHẮC PHỤC KIỂM TOÁN LẦN 3 (THIRD AUDIT REMEDIATION REPORT)
**Dự án:** GRACE Diagnostic Replication & Contrastive Evaluation (`grace_diag_replication_v1`)  
**Mục tiêu:** Khắc phục toàn diện 7 phát hiện (T3-01 đến T3-07) từ bản kiểm toán độc lập lần 3 (`Runs-management/b3_verified_patch_v1/independent_third_audit_20261108_143650/AUDIT_REPORT.md`).  
**Ngày hoàn thành:** 08/11/2026  
**Phiên bản phát hành nghiệm thu:** `release_20261108_v3` (`v3_remediated`)  
**Parent Release:** `release_20261108_v2` (`v2_remediated`)  
**Trạng thái bảo toàn:** `release_20261108` (v1, 103 files) và `release_20261108_v2` (v2, 118 files) nguyên vẹn 100%.

---

## 1. BẢNG ÁNH XẠ KHẮC PHỤC CÁC PHÁT HIỆN T3-01 ĐẾN T3-07

| Mã phát hiện | Tên & Mức độ | File / Hàm sửa đổi | Lệnh & Thử nghiệm tái hiện | Kết quả trước (Observed) vs Kỳ vọng (Expected) | Artifact / Hash tạo ra | Trạng thái |
|---|---|---|---|---|---|---|
| **T3-01** | Step 7 NameError biến report (Cao) | `scripts/b3_step7_verify_selector_renderer.py`<br>`run_step7()` | `pytest tests/test_amended_b3.py -k test_step7_report_construction_no_nameerror`<br>`python scripts/b3_step7_verify_selector_renderer.py` | **Trước:** `NameError: name 'safe_pause_confirmed' is not defined` khi tạo report JSON.<br>**Sau:** Khởi tạo và gán thống nhất `safe_pause_confirmed` và `safe_pause_or_render_confirmed`. Bổ sung `encoding="utf-8", errors="replace"` cho tất cả subprocess execution trên Windows. | `release_20261108_v3/acceptance/step7_selector_renderer_report.json`<br>Report status: `STEP7_VERIFICATION_PASSED` | **PASS** |
| **T3-02** | Xử lý bất đồng review & bảo toàn pool (Cao) | `scripts/b3_step6_packet_tool.py`<br>`ingest_human_reviews_and_seal_pools()`<br>`Runs-management/b3_amended_20261106/check_b3.py`<br>`scripts/b3_step7_verify_selector_renderer.py` | `pytest tests/test_amended_b3.py -k test_existing_pool_with_new_reject_blocks_pool`<br>`pytest tests/test_amended_b3.py -k test_check_b3_pauses_on_blocked_pool_manifest` | **Trước:** Pool cũ giữ 2 approvals trên disk vẫn kích hoạt `ACTIVE_VERIFIED_POOL` khi có reject mới; runner nhận pair bất đồng.<br>**Sau:** Giữ nguyên lịch sử file trên đĩa; khi có reject/disagreement, pool manifest chuyển thành `BLOCKED_DISAGREEMENT`, `admitted_pairs_count = 0`. Mọi runner (`check_b3.py`, Step 7, Step 8) kiểm tra pool manifest và dừng an toàn (`PAUSED`), từ chối nạp pair bất đồng. Form lỗi bảo toàn file và không phát hành manifest ACTIVE mới. | `release_20261108_v3/pools/pool_manifest.json`<br>Seal: `191d1aec159b58e3ddd704e48dd982d1d90bd22c0799283aebbfc9bac223e82e` | **PASS** |
| **T3-03** | Bắt buộc hàm nguồn before/after, bỏ fallback donor (Cao) | `scripts/b3_step5_make_candidates.py`<br>`run_step5()` | `pytest tests/test_amended_b3.py -k test_sidecar_without_before_after_rejected`<br>`python scripts/b3_step5_make_candidates.py` | **Trước:** Step 5 dùng `ev.get('before', v_code)` tự động lấy code donor bank khi sidecar thiếu.<br>**Sau:** Bắt buộc sidecar phải có đủ `before` và `after` trích xuất từ source archive; thiếu thì dừng tại `candidate_ineligibility_records.jsonl`. Loại bỏ hoàn toàn fallback sang code donor bank. | `release_20261108_v3/candidates/candidates_summary.json`<br>`candidates_admitted: 0`, `ineligible_cases_count: 12`, `dummy_fixtures_used: false` | **PASS** |
| **T3-04** | Triage kỹ thuật đánh giá candidate source payload (Cao) | `scripts/b3_step6_packet_tool.py`<br>`run_automated_technical_triage()`<br>`scripts/b3_step5_make_candidates.py` | `pytest tests/test_amended_b3.py -k test_source_candidate_vs_recorded_commit_triage`<br>`python scripts/b3_step6_packet_tool.py` | **Trước:** Triage Step 6 loại candidate hợp lệ nếu 2 commit donor ban đầu không nối trực tiếp cha-con.<br>**Sau:** Phân biệt commit reconnaissance với actual source fix/parent payload. Triage đánh giá trực tiếp candidate source payload (`has_candidate_payload`, required source fields). Đồng bộ điều kiện giữa Step 3, 5, 6. | `release_20261108_v3/reviews/triage_ledger.jsonl`<br>12 ca đánh giá kỹ thuật tự động minh bạch | **PASS** |
| **T3-05** | Chặn triệt để synthetic timestamp trong production (Trung bình) | `scripts/b3_step6_packet_tool.py`<br>`validate_review_form()` | `pytest tests/test_amended_b3.py -k test_validate_review_form_rejects_synthetic_timestamp_in_production` | **Trước:** `TEST-FIXTURE` được chấp nhận ngay cả khi `allow_synthetic=False`.<br>**Sau:** Mặc định production (`allow_synthetic=False`) từ chối chuỗi chứa `TEST-FIXTURE`, bắt buộc parse ISO-8601 có timezone UTC, chặn ngày không tồn tại và thời gian tương lai. Cờ `allow_synthetic=True` chỉ dành riêng cho test cô lập. | `scripts/b3_step6_packet_tool.py`<br>Rejection: `REJECTED_SYNTHETIC_TIMESTAMP_IN_PRODUCTION` | **PASS** |
| **T3-06** | Phát hành release v3 đồng bộ code & hash (Cao) | `scripts/b3_step1_snapshot.py`<br>`release_20261108_v3/` | `python Runs-management/b3_verified_patch_v1/remediation_third_audit_20261108/audit_third_remediation.py` | **Trước:** Release v2 có hash lệch so với code đã sửa của các scripts và check_b3.<br>**Sau:** Phát hành gói sạch `release_20261108_v3`, bảo toàn nguyên vẹn v1 và v2; chạy lại toàn bộ quy trình Steps 1–8 với mã nguồn hiện tại, niêm phong toàn bộ chuỗi hashes/seals. | `release_20261108_v3/inputs_manifest.json`<br>Seal: `e32acbccbfeb32b49296a50526db8999bc189fe71950f5e6acab2572ee5b7ea5` | **PASS** |
| **T3-07** | Khóa cổng đầu vào, phân biệt pool state & báo cáo động (Cao) | `scripts/b3_step8_validation_census_builder.py`<br>`run_step8()`<br>`Runs-management/b3_amended_20261106/check_b3.py` | `pytest tests/test_amended_b3.py -k test_step8_entrypoint_rejects_freeze_file_tampering`<br>`python scripts/b3_step8_validation_census_builder.py` | **Trước:** Step 8 bỏ sót kiểm tra inputs manifest seal, module/script hashes, authority docs, tokenizer, và freeze files; trạng thái gán vội `READY_FOR_GPU_INFERENCE`; check_b3 gộp invalid pool vào PAUSED; báo cáo Markdown hardcode text.<br>**Sau:** Cổng Step 8 xác minh bắt buộc tất cả inputs, modules, scripts, authority docs, tokenizer, freeze manifest & data files, Step 7 report; phân biệt `EMPTY_POOL` với `INVALID_POOL`; trạng thái nghiệm thu: `PROMPT_AUDIT_PASSED_PENDING_RUNTIME_ACCEPTANCE`; báo cáo Markdown dựng động từ dữ liệu kiểm toán. | `release_20261108_v3/acceptance/VALIDATION_DATA_AUDIT_REPORT.md`<br>`release_20261108_v3/validation/validation_prompt_manifest.json`<br>Seal: `0cd3293f34cd436725d047f038cd44ae5c8f6e1ec00d6e3369efeb9ac9609ee8` | **PASS** |

---

## 2. SNAPSHOT VÀ THAY ĐỔI MÃ NGUỒN (CHANGE LOG & INTEGRITY)

- **Git Commit Baseline:** `46e6f4ab9d0ff2c9ecac124d3a6f2bdb72524bd9`
- **Các file mã nguồn sửa đổi:**
  * `Runs-management/b3_amended_20261106/check_b3.py` (SHA256: `9574add29b27d84faf6f9c7c74bf12b1b4bb2ea9deed5a2ba44d8ad409206046`)
  * `scripts/b3_step7_verify_selector_renderer.py` (SHA256: `ec693bb4b87c7e0cce06c271b305fe75d45d6563e77f98e09f2b8764b85c1c01`)
  * `scripts/b3_step8_validation_census_builder.py` (SHA256: `97f960f4eb7802b55b55e3474619ba04aee8be6f663eece8df2c0211a7f6fba5`)
  * `scripts/b3_step5_make_candidates.py` (SHA256: `8d3f1bd2ef9aa6123557da91b21c4498a91093ce875d4d1411abd2804f244007`)
  * `scripts/b3_step6_packet_tool.py` (SHA256: `2f3b3b194e0ae24a933408143a096b6ab8a01e8ca51a1c166e0b0a0083514eb5`)
  * `tests/test_amended_b3.py` (35 targeted tests passing)
  * `CHANGES_AFTER_PREREG.md` (Ghi nhận đầy đủ thay đổi, phân loại và nhật ký kiểm toán)
- **Bảo toàn Release Lịch sử:**
  * `release_20261108` (v1): 103 files verified intact.
  * `release_20261108_v2` (v2): 118 files verified intact.
- **Niêm phong Ba Manifest của Release v3:**
  1. `inputs_manifest.json`: `e32acbccbfeb32b49296a50526db8999bc189fe71950f5e6acab2572ee5b7ea5`
  2. `pools/pool_manifest.json`: `191d1aec159b58e3ddd704e48dd982d1d90bd22c0799283aebbfc9bac223e82e`
  3. `validation/validation_prompt_manifest.json`: `0cd3293f34cd436725d047f038cd44ae5c8f6e1ec00d6e3369efeb9ac9609ee8`

---

## 3. KIỂM CHỨNG PHẦN MỀM (SOFTWARE VERIFICATION & INTEGRATION TESTS)

### 3.1. Kết quả Toàn bộ 4 Bộ Test Suite Chính thức (72 passed, 0 failed, 0 skipped):
- `tests/test_amended_b3.py`: **35 passed** (bổ sung test kiểm tra dừng an toàn khi pool bất đồng và cổng kiểm tra tính toàn vẹn của freeze data files).
- `tests/test_preregistration_integrity.py`: **6 passed** (toàn bộ hợp đồng đóng băng OSF, ngưỡng τ*, checksum, và quy tắc Holm được bảo toàn).
- `01_Author_Baseline_Unified/diagnostic_kit/tests/test_probes.py`: **20 passed** (cấu trúc Figure 6, token budget, contrastive pairs, prompt renderer).
- `01_Author_Baseline_Unified/diagnostic_kit/tests/test_stats_and_complementarity.py`: **11 passed** (cluster bootstrap, OOF CV, meta-models).

### 3.2. Kiểm thử Tích hợp Độc lập (B1–B5):
- **B1 (Step 7):** Chạy thực tế end-to-end trên Windows, returncode 0, report JSON và Markdown không còn bất kỳ NameError hay lỗi encoding charmap.
- **B2 (Disagreement Handling):** Khi có phiếu reject mới đối với pair lịch sử, pool manifest chuyển sang `BLOCKED_DISAGREEMENT`, `admitted_pairs_count = 0`, cả `check_b3.py` và Step 7/8 đều an toàn dừng tại `PAUSED`, từ chối nhận pair bất đồng. Form lỗi bảo toàn file trên đĩa và không phát hành manifest ACTIVE mới.
- **B3 (Source Functions):** Sidecar thiếu trường `before`/`after` bị loại ngay tại Step 5, không tự động fallback sang donor code trong bank.
- **B4 (Timestamp):** Production từ chối chuỗi timestamp chứa `TEST-FIXTURE`, bắt buộc ISO-8601 có timezone.
- **B5 (Entrypoint Gates):** Sửa đổi bất kỳ file freeze data, script, module, authority doc, tokenizer hay specs archive đều làm Step 8 fail-closed trước khi render.

---

## 4. HỒ SƠ NGUỒN VÀ PROVENANCE (SOURCE & PROVENANCE DOSSIER)

- **Devign Scope:** 12 ca ứng viên được điều tra độc lập (`case_manifest.json`, `request_log.jsonl`, `actual_fix.diff`). Không có ca nào có quan hệ commit cha-con cùng hàm trong kho git upstream. Trạng thái: `BLOCKED_NO_AUTHENTIC_PAIRS_IN_INVESTIGATED_SCOPE`.
- **REVEAL Scope:** Khảo sát toàn bộ 17.636 clean train donors; 100% thiếu commit hash và file path trong bản xuất upstream `claudios/ReVeal@71f62e1e`. Trạng thái: `BLOCKED_UNRESOLVED_PROVENANCE`.
- **Cam kết Liêm chính:** Không suy đoán commit ID, không lấy donor chéo dataset, không dùng dummy diff trong luồng dữ liệu thật.

---

## 5. HỒ SƠ REVIEW VÀ QUẢN LÝ POOL (REVIEW & POOL DOSSIER)

- **Review Packets:** 12 packets được sinh với canonical `payload_sha256` tại `release_20261108_v3/review_packets/`.
- **Triage Ledger:** 12 ca được đánh giá tự động bởi `AUTOMATED_TECHNICAL_TRIAGE` tại `release_20261108_v3/reviews/triage_ledger.jsonl`.
- **Human Review Ledger:** 0 phiếu review nộp (`release_20261108_v3/reviews/review_ledger.jsonl`). Tuyệt đối không tự sinh chữ ký hay nhận xét giả lập.
- **Pool Manifest:** Niêm phong tại `release_20261108_v3/pools/pool_manifest.json` với số lượng pair admitted = 0 cho cả Devign và REVEAL.

---

## 6. NGHIỆM THU PROMPT VALIDATION CENSUS (G3 VERIFICATION)

- Quét đủ 100% census validation chính thức: **2.732 Devign + 2.273 REVEAL = 5.005 targets**.
- 100% target IDs khớp tuyệt đối giữa `validation_raw.jsonl` và specs archive.
- Khớp mã nguồn query code sau `.strip()` đạt 100% (0 substantive mismatch).
- Do pool rỗng, toàn bộ 5.005 bản ghi ghi nhận trạng thái dừng an toàn trung thực: `status: PAUSED`, `prompt_evaluation_status: NOT_EVALUATED_BLOCKED_EMPTY_POOL`. Không gán cờ Figure 6 hay target label khi prompt rỗng.
- Trạng thái nghiệm thu chuyển thành: `PROMPT_AUDIT_PASSED_PENDING_RUNTIME_ACCEPTANCE` (thay cho `READY_FOR_GPU_INFERENCE`).

---

## 7. ĐÁNH GIÁ MA TRẬN CỔNG NGHIỆM THU (G0–G7 GATE EVALUATION)

| Cổng Nghiệm thu | Nội dung đánh giá | Kết quả Đánh giá | Ghi chú & Điều kiện tiếp theo |
|---|---|---|---|
| **G0 — Sửa phần mềm** | Khắc phục T3-01 đến T3-07, kiểm thử tích hợp đạt | **PASS** | Hoàn thành và kiểm chứng độc lập trên release `v3_remediated`. |
| **G1 — Bằng chứng nguồn** | Candidate có before/after, actual fix/parent, diff xác thực | **BLOCKED** | Chưa có cặp bản vá nguồn xác thực trong 12 ca Devign và 17.636 donor REVEAL. |
| **G2 — Review và Pool** | Pool có candidate đạt G1 và 2 review độc lập đồng thuận | **BLOCKED** | Pool Devign (0 pair) và REVEAL (0 pair) đều rỗng; không có human review. |
| **G3 — Full Validation Prompt** | Census prompt được dựng, audit và đóng băng đầy đủ | **BLOCKED (PAUSED)** | 5.005 census records dừng an toàn có kiểm soát (`PAUSED`). Chưa có pool đạt để render prompt thật. |
| **G4 — Notebook/Runtime** | Môi trường GPU Kaggle T4x2, package lock, scoring | **NOT_EVALUATED** | Chưa chạy GPU; inference được tạm dừng có kiểm soát. |
| **G5 — Validation Scores** | Điểm số validation chính thức của phương pháp mới | **NOT_EVALUATED** | Bắt đầu từ 0 score mới sau khi G4 đạt. |
| **G6 — Ngưỡng mới (τ*)** | Quét 99 ngưỡng độc lập trên validation score mới | **NOT_EVALUATED** | Ngưỡng cũ frozen bảo toàn tuyệt đối. |
| **G7 — Test và Báo cáo** | Đủ census test (5.006 target), bootstrap, Table B | **NOT_EVALUATED** | Chỉ thực hiện sau khi có threshold lock mới. |

---

## 8. KẾT LUẬN & ĐỀ XUẤT VẬN HÀNH

1. **Nghiệm thu phần mềm (G0):** Toàn bộ 7 phát hiện T3-01 đến T3-07 từ đợt kiểm toán độc lập lần 3 đã được khắc phục triệt để và kiểm chứng bằng các bài test tự động cũng như chạy thực tế end-to-end trên Windows.
2. **Trạng thái an toàn được duy trì (Safe Pause Confirmed):** Do chưa tìm thấy cặp bản vá lỗi nhân quả cùng hàm có đầy đủ bằng chứng nguồn, pool Arm B3 tiếp tục được tạm dừng an toàn có kiểm soát (`SAFE_PAUSE_MAINTAINED`). Tuyệt đối không bịa đặt dữ liệu hay hạ chuẩn để vượt cổng.
3. **Phát hành Release v3:** Toàn bộ artifact, ledger, và ba manifest đã được niêm phong mật mã tại `Runs-management/b3_verified_patch_v1/release_20261108_v3/` với dữ liệu và mã nguồn hoàn toàn đồng bộ, sẵn sàng cho đợt kiểm toán độc lập tiếp theo.
