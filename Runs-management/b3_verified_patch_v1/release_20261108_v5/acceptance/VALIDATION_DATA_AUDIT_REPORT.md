# BÁO CÁO NGHIỆM THU DỮ LIỆU B3 (REMEDIATED VALIDATION DATA AUDIT REPORT)

**Ngày nghiệm thu:** 08/11/2026  
**Phiên bản phát hành:** `v5_devign_validation_locked` (Kế thừa từ `release_20261108_v4`)  
**Giao thức thực thi:** `docs/B3_NEW_ALGORITHM_EXECUTION_PLAN_20261108.md` (Bước 1 đến Bước 8)  
**Tài liệu kiểm toán & nghiệm thu:** `release_20261108_v5/acceptance/PUBLISH_ACCEPTANCE_REPORT.md` | `Runs-management/b3_verified_patch_v1/independent_v5_readiness_audit_20261108_211003/AUDIT_REPORT.md`  
**Mã băm niêm phong đầu vào (Inputs Seal):** `1f1ccd0dc3f2b74ffe162a0aea2fc094e4b0533c79cc2dac93a9d888ba8fefd8`  
**Mã băm niêm phong Pool (Pool Seal):** `73426c738d6c7bbfc176b070bff0e72cc09baee584523d9eeff80c75d38b9ad3`  
**Mã băm niêm phong Prompt Manifest (Prompt Seal):** `bdeabdccbc2fb48d6201a79756d93424215e123c4055a73127d525c4afad1a01`  

---

## 1. TỔNG HỢP TIẾN ĐỘ VÀ KẾT QUẢ THỰC TẾ (BƯỚC 1 ĐẾN BƯỚC 8)

| Bước | Nội dung công việc | Trạng thái thực tế | Đánh giá kiểm toán & Ghi chú |
|---|---|---|---|
| **Bước 1** | Lập snapshot nguồn, kiểm tra ràng buộc ngân sách & hợp đồng đóng băng | **PASS** | Đã kiểm tra đúng 21.691 Devign và 17.636 REVEAL clean train donors. Tokenizer `b2cff6...` đúng hash. Niêm phong đầy đủ mã module, script thực thi và tài liệu thẩm quyền. Ghi nhận trung thực tình trạng nộp cập nhật OSF (`SUBMITTED_AMENDMENT_PENDING_REGISTRATION_STAMP`). |
| **Bước 2** | Khắc phục TLS (certifi) và rà soát commit git upstream | **PASS** | Cấu hình CA bundle `certifi.where()`. Thực hiện rà soát đủ 17 commit duy nhất cho 12 cặp ứng viên Devign. Tách biệt rõ ràng log cache replay và network call. |
| **Bước 3** | Điều tra cặp Devign candidate, lập hồ sơ bằng chứng git | **PASS** | Điều tra các ca ứng viên ưu tiên. Đã trích xuất commit cha, danh sách file thay đổi và commit message. Cặp Devign (Case 08 `ffmpeg_can_safely_read_8614_26054`) được xác thực upstream git và hoàn thành hồ sơ bằng chứng. |
| **Bước 4** | Khảo sát phục hồi provenance REVEAL | **BLOCKED** | Toàn bộ 17.636 donor trong clean train export thiếu commit ID và file path. Hồ sơ ghi nhận trạng thái `BLOCKED_UNRESOLVED_PROVENANCE` với phạm vi kiểm kê cụ thể; không dùng nhận định chưa kiểm chứng. |
| **Bước 5** | Tạo pair candidate từ bằng chứng nguồn thật | **PASS** | Tạo pair candidate từ bằng chứng nguồn thật (Case 08). Bỏ hoàn toàn dummy fix diff trong luồng dữ liệu thật. Bắt buộc có bằng chứng before/after và diff nguồn xác thực; không fallback sang code donor bank (T3-03). |
| **Bước 6** | Triage kỹ thuật tự động và niêm phong eligible pool | **ACTIVE_VERIFIED_POOL** | Tách bạch hoàn toàn triage kỹ thuật tự động khỏi thẩm định con người. Triage đánh giá trực tiếp candidate payload (T3-04). Phiếu duyệt kiểm tra nghiêm ngặt timestamp production (T3-05). Pool Devign: 1 pairs (ACTIVE_VERIFIED_POOL); REVEAL: 0 pairs (BLOCKED_EMPTY_POOL). Số phiếu human review: 2. Bất đồng/reject mới chặn kích hoạt pool (T3-02). |
| **Bước 7** | Kiểm tra `VerifiedPairSelector`, renderer và các cổng an toàn | **STEP7_VERIFICATION_PASSED** | Chạy toàn bộ 4 bộ test suites (91 passed, 0 failed). Thống nhất tên biến báo cáo Step 7 (T3-01). Kiểm tra cổng an toàn: cơ chế dừng khi pool rỗng, cấm rò rỉ nhãn, exact rational Fraction, và Figure 6 prompt ordering. |
| **Bước 8** | Dựng và kiểm toán census validation (5.005 target) | **DEVIGN_RENDERED_REVEAL_PAUSED** | Quét đủ 2.732 Devign + 2.273 REVEAL targets. 100% ID duy nhất, khớp tuyệt đối code validation raw sau `.strip()`, 0 rò rỉ nhãn. Đã dựng thành công 2,732 prompts Devign tuân thủ Figure 6 và ngân sách token <= 8.192. Nhánh REVEAL tiếp tục dừng an toàn có kiểm soát (PAUSED, `NOT_EVALUATED_BLOCKED_EMPTY_POOL`) do chưa có pool. Cổng đầu vào kiểm tra toàn diện hash module, script, tài liệu authority, freeze data files và tokenizer (T3-07). Trạng thái nghiệm thu: `INFERENCE_PAUSED`. |

---

## 2. KẾT LUẬN KHOA HỌC VÀ TUÂN THỦ NGUYÊN TẮC LIÊM CHÍNH OSF

1. **Phạm vi kiểm toán và Dừng an toàn có kiểm soát (Scope & Controlled Pause):**
   - Thuật toán B3 mới (`b3-verified-patch-v1`) yêu cầu cặp tương phản phải là bản vá lỗi bảo mật thực tế của cùng một hàm giữa commit sửa lỗi và commit cha (`fix_commit != parent_commit`).
   - Đã xác thực thành công 1 cặp bản vá lỗi nhân quả cho Devign (Case 08 `ffmpeg_can_safely_read_8614_26054`, được phê duyệt độc lập bởi 2 kiểm toán viên Hiếu và Dũng).
   - Đã dựng và kiểm toán thành công 2,732 prompts Devign validation tuân thủ Figure 6 và ngân sách context (<= 8.192 tokens).
   - Với REVEAL (toàn bộ 17.636 clean-train donors thiếu commit ID upstream trong frozen export), nhánh REVEAL tiếp tục dừng an toàn có kiểm soát (`BLOCKED_EMPTY_POOL`, `NOT_EVALUATED_BLOCKED_EMPTY_POOL`): **tuyệt đối không bịa đặt dữ liệu (no fabrication)**, không dùng dữ liệu giả lập cho inference thật.
   - Toàn bộ quá trình chuẩn bị dừng lại trước khi chạy GPU inference (PAUSE) để bảo đảm quyền kiểm soát của người dùng.

2. **Khắc phục toàn diện các phát hiện kiểm toán lần 1 và 2 (Findings F01–F07):**
   - Đã loại bỏ toàn bộ hồ sơ tự sinh gán chữ ký người duyệt (F01).
   - Đã chuẩn hóa kết luận theo đúng phạm vi điều tra thực tế (F02).
   - Đã sửa trạng thái census validation thành `PAUSED` và `NOT_EVALUATED_BLOCKED_EMPTY_POOL` cho prompt rỗng (F03).
   - Đã loại bỏ diff giả lập khỏi luồng dữ liệu thật (F04).
   - Đã kiểm kê và ghi nhận trung thực hiện trạng provenance REVEAL (F05).
   - Đã thiết lập cổng nghiệm thu fail-closed và tách biệt logging cache/network (F06).
   - Đã cập nhật đúng trạng thái đề xuất cập nhật OSF (F07).

3. **Khắc phục triệt để các phát hiện kiểm toán độc lập lần 3 (Findings T3-01–T3-07):**
   - **T3-01 (Step 7 Report & Encoding):** Thống nhất tên biến tính toán `safe_pause_confirmed` và `safe_pause_or_render_confirmed` trong báo cáo; bổ sung `encoding="utf-8", errors="replace"` cho tất cả subprocess execution.
   - **T3-02 (Pool Preservation & Disagreement Blocking):** Lịch sử pool trên đĩa được bảo toàn, nhưng khi phát hiện bất đồng hoặc phiếu reject mới đối với pair đã có, pool được đánh dấu `BLOCKED_DISAGREEMENT`, `admitted_pairs_count = 0`, và tất cả runners (`check_b3.py`, Step 7, Step 8) lập tức từ chối nhận pair bất đồng. Form lỗi bảo toàn đĩa và không phát hành manifest ACTIVE mới.
   - **T3-03 (Bằng chứng nguồn Before/After):** Bắt buộc sidecar phải có đầy đủ hàm nguồn `before` và `after` trích xuất từ source archive; loại bỏ triệt để fallback âm thầm sang mã donor trong bank.
   - **T3-04 (Triage Tự động dựa trên Candidate Source Payload):** Tách bạch giữa quan hệ commit donor ban đầu với bằng chứng actual fix/parent nguồn đã xác minh; triage đánh giá trực tiếp candidate payload.
   - **T3-05 (Chặn triệt để Timestamp Synthetic trong Production):** `validate_review_form` từ chối `TEST-FIXTURE` trong production (`allow_synthetic=False`), bắt buộc parse ISO-8601 có timezone và kiểm tra thời gian tương lai.
   - **T3-06 (Phát hành Release v3 đồng bộ):** Tạo gói phát hành mới `release_20261108_v3`, bảo toàn nguyên vẹn `release_20261108` (v1) và `release_20261108_v2` (v2); tính toán lại và niêm phong toàn bộ chuỗi hashes/seals.
   - **T3-07 (Khóa Cổng Đầu vào Toàn diện & Báo cáo Động):** Step 8 kiểm tra niêm phong inputs manifest, module hashes, script hashes, authority docs hashes, freeze manifest và toàn bộ freeze data files, tokenizer files, specs archive, và report Step 7. Phân biệt `EMPTY_POOL` với `INVALID_POOL`. Trạng thái nghiệm thu chuyển thành `PROMPT_AUDIT_PASSED_PENDING_RUNTIME_ACCEPTANCE`. Báo cáo Markdown được dựng động từ dữ liệu kiểm toán thực tế.
