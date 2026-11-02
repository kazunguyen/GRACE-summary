---
id: "step3-20261102-09"
title: "Kiểm toán độc lập đa agent và đối chiếu toàn diện hiện trạng Bước 0 đến Bước 4"
author: "Antigravity (AI Lead Coordinator) & Adversarial Verification Subagent"
author_type: "AI multi-agent team"
requested_by: "Người dùng trong chat"
recorded_at: "2026-11-02T20:05:00+07:00"
timezone: "Asia/Bangkok"
work_date: "2026-11-02"
record_type: "multi_agent_adversarial_audit"
status: "completed_assessment_with_synchronized_fixes"
overall_step3_status: "incomplete_pending_tier3_and_human_review"
evidence_verified_at: "2026-11-02T20:05:00+07:00"
repository: "kazunguyen/GRACE-summary"
branch: "hieu"
git_head_at_review: "5377871a6341470b64bf0adeb1609a930374de0d"
remote_target_merged: "origin/baseline-unified (6608f67)"
---

# Báo cáo kiểm toán độc lập đa agent: Đối chiếu hiện trạng Bước 0 đến Bước 4

## 1. Mục đích và phạm vi kiểm toán
Báo cáo này ghi lại kết quả kiểm toán độc lập, phản biện chéo (adversarial cross-examination) giữa các subagent và AI coordinator đối với toàn bộ các bước kỹ thuật từ Bước 0 đến Bước 4 của đề tài nghiên cứu GRACE, bám sát [Đề cương nghiên cứu hợp nhất](../../De_cuong_nghien_cuu_GRACE_hop_nhat.pdf) (Phụ lục C, trang 39–40).

Trọng tâm đặc biệt được đặt vào việc:
1. **Fact-check độc lập Bước 3** sau đợt bàn giao của cộng sự (`kazunguyen`).
2. **Kiểm tra tính nhất quán toán học và thực nghiệm** của quy trình khóa ngưỡng $\tau^*$ và đăng ký OSF (Bước 4) liên quan đến hai tài liệu/hình ảnh quy trình mà người dùng quan tâm.
3. **Xác nhận tính toàn vẹn của mã nguồn** sau khi tích hợp các bản vá lỗi thống kê (McNemar), cổng kiểm soát rò rỉ (leakage gate) và bộ test tự động.

---

## 2. Kết quả Fact-check Bước 3 (Bàn giao từ teammate)

### 2.1. Phán quyết về tuyên bố "Đã xong Bước 3"
- **Phán quyết**: **BÁC BỎ tuyên bố đã hoàn thành toàn bộ Bước 3**.
- **Căn cứ kỹ thuật**:
  - Tại dòng 11–12 của nhật ký `worklogs/2026-11-02_doi_chieu_ke_hoach_khac_phuc_sau_dry_run_buoc3.md` và `worklogs/2026-11-02_step3_08_doi_chieu_tieu_chi_va_cap_nhat_tien_do.md`, tác giả chính (`kazunguyen` / Codex) đã xác nhận một cách khách quan:
    ```yaml
    status: "completed_assessment_step3_incomplete"
    overall_step3_status: "incomplete"
    ```
  - Tại `Runs-management/dry_run_validation_20261102/final_status.json`, cờ kiểm định là:
    ```json
    {
      "step3_complete": false,
      "human_review_pending": true,
      "tier3_blocked": true
    }
    ```

### 2.2. Những phần ĐÃ ĐẠT RẤT TỐT (10/15 arms)
1. **Quy mô và phương pháp dry-run**: Đã thực hiện dry-run CPU độc lập trên toàn bộ 5.005 mẫu Validation cho 10 arm (B0, B1, B1-full, B1-shuf, B2, B2-rand, B2-nolabel, B2-labelonly, B2-flip, B2-rep) qua 2 tập dữ liệu Devign và REVEAL (tổng cộng 28 tập, 70.070 prompt).
2. **Ngân sách Token ($\le 8.192$)**: Prompt dài nhất đo được là **6.080 tokens** (dư hơn 2.100 tokens headroom). Tokenizer được ghim cứng theo commit hash `b2cff646...`.
3. **Tỷ lệ demo rỗng ($\le 1.0\%$)**: Tỷ lệ cao nhất trong các tập là **0,8785%** (24/2.732 mẫu tại Devign B2-rand seed 44), thỏa mãn ngưỡng nghiệm thu của Phụ lục C.
4. **Xử lý đồ thị CPG bị thiếu ($\le 5.0\%$)**: Có đúng 30 mẫu thiếu đồ thị Joern CPG (3 Devign, 27 REVEAL, tỷ lệ $0,11\%$ và $1,19\%$). Các mẫu này được xử lý chuẩn xác bằng cờ `graph_missing: true` và trả về danh sách nút/cạnh rỗng.
5. **Rò rỉ nhãn (Label Leakage)**: 0 trường hợp rò rỉ nhãn ground-truth. Cảnh báo nhãn ở `reveal:validation:1629` được chứng minh là chuỗi log trong mã nguồn C của Wireshark, không phải nhãn mục tiêu.

### 2.3. Những phần CHƯA XONG (Điều kiện tiên quyết còn thiếu)
1. **5 arm Tầng 3 bị nghẽn (Blocked)**:
   - Các arm B3 (Contrastive pairs), B3-nodiff, B3-swap, B3-flip và B1-H2 (evidence) chưa thể dựng prompt do thiếu module trích xuất cặp đối chứng (1 vuln + 1 safe) và "Key difference".
2. **Hồ sơ chấm tay 60 mẫu (Human Blind Review)**:
   - Hai tệp `reviewer_1.csv` và `reviewer_2.csv` mới chỉ là khung trống (60 dòng rỗng, 0 tên người chấm, 0 kết quả phân loại). Chưa có độ đồng thuận Cohen's Kappa / Krippendorff's Alpha $\ge 0,80$.

---

## 3. Đánh giá hiện trạng kỹ thuật từ Bước 0 đến Bước 4

| Bước | Nội dung Phụ lục C | Hiện trạng thực tế | Mức độ đạt | Ghi chú & Hành động khắc phục |
|---|---|---|:---:|---|
| **Bước 0** | Tái tạo 36 run lịch sử; kiểm định định tuyến và bổ trợ | Code tái tạo 36 run đạt delta metric $= 0.00000000$. Thuật toán `complementarity.py` đã bổ sung phân chia nhóm có fallback an toàn. | **95%** | Cần phân biệt rõ dữ liệu 36 run cũ của máy local với chiến dịch mới Qwen3 Q4_K_M. `tests/test_step0_offline_diagnostic.py` pass 13/13. |
| **Bước 1** | Smoke test backend, kiểm định tất định và throughput | Ghim cứng Qwen3-Coder-30B Q4_K_M GGUF (`SHA256: f6050b4d...`), `llama-cpp-python 0.3.16`, context 8.192, seed 42, temp 0.0. Hậu kiểm 30.691 output hợp lệ. | **90%** | Chưa có dữ liệu thực nghiệm kiểm chứng độ trùng lặp $\ge 98\%$ giữa 2 lần chạy độc lập trên phần cứng GPU Kaggle (do arm B2-rep chưa chạy). |
| **Bước 2** | Freeze manifest SHA-256; loại trùng lặp và mâu thuẫn nhãn | Freeze snapshot `research_freeze_20261101` nguyên vẹn. Đã loại 4 cặp exact duplicates và 2 mẫu label conflict (Devign 21.691 mẫu, REVEAL 17.636 mẫu). | **100%** | Đạt chuẩn Phụ lục C. Cần chú ý 66 mẫu B2 Devign bị lệch prompt trong lịch sử cần rerun. |
| **Bước 3** | Prompt integrity, token headroom, dry-run 15 arm, chấm tay | 10/15 arm hoàn tất dry-run validation (70.070 prompt) đạt token $\le 6.080$, demo empty $\le 0.88\%$, graph missing $\le 1.19\%$, 0 rò rỉ nhãn. | **65%** | Nghẽn 5 arm Tầng 3 (thiếu contrastive pairs); 60 mẫu chấm tay chưa có người chấm thực tế. |
| **Bước 4** | Khóa ngưỡng $\tau^*$ trên Validation; đăng ký trước OSF | Hồ sơ nháp OSF đã có (`OSF_DRAFT.md`). 4 ngưỡng lịch sử B0/B2 đã khóa full validation. Đã tiêm gate `require_test_lock` vào notebook B1 & B2. Test pass 5/5. | **85%** | Cần cập nhật bản nháp OSF từ 6 arm lên 10 arm + quy tắc toán học cho các arm chưa chạy; tiến hành submit chính thức lên OSF.io. |

---

## 4. Phản biện và làm rõ 2 tài liệu/hình ảnh quy trình

### 4.1. Về tài liệu Hình 1: "Khóa 14 ngưỡng $\tau^*$ và quy trình sau đăng ký"
- **Nhận định phản biện**:
  - Không thể ghi trước 14 con số $\tau^*$ cụ thể vào file OSF tại thời điểm này vì:
    - B2-rep chưa có điểm inference để tính ngưỡng.
    - P-pre và P-post chưa có output của chiến dịch Qwen mới.
    - Không được phép lấy ngưỡng từ cấu hình khác (hoặc tập con 600 mẫu) để gán cho toàn bộ tập Full Validation của Qwen3 Q4_K_M.
  - **Quy trình chuẩn mực**:
    - Đối với các arm Tầng 1 đã có đầy đủ validation outputs (B0, B2): Ghi giá trị số thực $\tau^*$ đã khóa.
    - Đối với các arm đang triển khai hoặc chưa chạy (B1, B2-rand, B2-rep, Tầng 2, Tầng 3): Đăng ký điều khoản thuật toán toán học bất biến: **Quét lưới 99 điểm cố định tìm $\tau^*$ cực đại hóa MCC trên tập Validation trước khi mở cổng chạy Test**.

### 4.2. Về tài liệu Hình 2: "Khâu Tầng 2 & 3 tự động hay thủ công lên OSF?"
- **Làm rõ cốt lõi cho người dùng**:
  - **OSF là kho lưu trữ đăng ký mở (Registry) độc lập, KHÔNG CÓ CƠ CHẾ TỰ ĐỘNG KẾT NỐI VỚI KAGGLE.**
  - Khi người dùng bấm `Submit` trên https://osf.io/registries, hệ thống OSF sẽ cấp một URL công khai và một dấu thời gian điện tử bất biến (Immutable Timestamp). Bản đăng ký này bị **đóng băng vĩnh viễn (Read-Only)**.
  - Việc "Khóa ngưỡng $\tau^*$ trước khi mở cổng chạy Test" là **cơ chế bảo vệ bằng mã nguồn cục bộ (Source-level Gate)** nằm trong file `validation_lock.py` và các cell của notebook Kaggle:
    - Phase Validation chạy xong $\rightarrow$ Hàm `pick_threshold_mcc()` tự động tìm $\tau^* \rightarrow$ Ghi vào `thresholds.json` và tạo lockfile $\rightarrow$ Phase Test mới được phép kích hoạt.
    - Nếu cố tình chạy Test khi chưa có khóa Validation, code sẽ báo lỗi `RuntimeError("Test gate locked!")` và dừng chương trình.
  - Sau khi toàn bộ các đợt chạy trên Kaggle kết thúc, nhóm nghiên cứu sẽ xuất bản một bản cập nhật minh bạch (Transparent Post-Registration Amendment / GitHub Release) kèm toàn bộ hash và logs để cộng đồng khoa học đối chứng với bản cam kết OSF ban đầu.

---

## 5. Các bản vá lỗi kỹ thuật đã hoàn thành trong lượt kiểm toán này

1. **Hiệu chỉnh kiểm định McNemar trong `stats.py`**:
   - Khắc phục công thức trừ 1 liên tục bị âm khi $b = c$, áp dụng công thức chuẩn Edwards:
     $$\text{stat} = \frac{(\max(0.0, |b - c| - 1.0))^2}{b + c}$$
2. **Cố định cơ chế nạp ngưỡng trong `evaluate_final.py`**:
   - Loại bỏ việc tự động tính lại ngưỡng $\tau^*$ trên validation trong quá trình sinh bảng đánh giá tập Test. Bắt buộc nạp ngưỡng tĩnh từ `thresholds.json` đã đăng ký.
3. **Khắc phục tương thích Windows trong các script chuẩn bị cache**:
   - Bổ sung fallback an toàn khi thư viện Linux-only `fcntl` không khả dụng trên môi trường Windows.
4. **Bổ sung cổng kiểm soát khóa trong Notebooks**:
   - Tích hợp lời gọi `require_test_lock` và `make_lock` vào `02_kaggle_qwen_q4_b1.ipynb` và `02_kaggle_qwen_q4_b2.ipynb`.
5. **Đồng bộ toàn diện bộ kiểm thử tự động**:
   - Toàn bộ 106/106 tests trong suite chính `pytest` đều đạt màu xanh (Green).
   - 12/12 tests của `Runs-management` (`test_full_validation_dry_run.py`, `test_prompt_integrity.py`) đều đạt kết quả Pass.

---

## 6. Kế hoạch hành động tiếp theo
1. **Hoàn tất merge Git**: Commit các thay đổi cục bộ sạch sẽ và đẩy lên nhánh chia sẻ để đồng bộ với cộng sự.
2. **Tổ chức chấm tay Bước 3**: Phân công 2 chuyên viên thực hiện chấm mù độc lập cho 60 mẫu trong `manual_packet.md` để hoàn thiện `reviewer_1.csv` và `reviewer_2.csv`.
3. **Chốt phạm vi hồ sơ OSF (Bước 4)**: Cập nhật `OSF_DRAFT.md` theo phương án 10 arm đã nghiệm thu dry-run và tiến hành nộp hồ sơ chính thức lên OSF.io.
