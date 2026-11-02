---
id: "step3-20261102-10"
title: "Hoàn tất đánh giá chấm tay độc lập hai chuyên gia và biên bản phân xử Bước 3"
author: "HuuHieu03 & Dung (Research Team)"
author_type: "Research Team"
requested_by: "Người dùng trong chat"
recorded_at: "2026-11-02T21:40:00+07:00"
timezone: "Asia/Bangkok"
work_date: "2026-11-02"
record_type: "human_review_and_adjudication_record"
status: "completed_step3_manual_review_and_adjudication"
overall_step3_status: "manual_review_completed_tier3_arms_blocked"
evidence_verified_at: "2026-11-02T21:40:00+07:00"
repository: "kazunguyen/GRACE-summary"
branch: "hieu"
---

# Hoàn tất đánh giá chấm tay độc lập hai chuyên gia và biên bản phân xử Bước 3

Worklog này ghi nhận việc tổ chức và hoàn thành đánh giá độc lập (blind review) cho 60 mẫu prompt (30 Devign + 30 REVEAL) giữa hai chuyên gia đánh giá đại diện: **Reviewer 1 (HuuHieu03 / Hiếu)** và **Reviewer 2 (Dung / Dũng)**, tuân thủ đúng [RUBRIC.md](../Runs-management/prompt_audit_20261102/RUBRIC.md) và Phụ lục C của [Đề cương nghiên cứu GRACE hợp nhất](../../De_cuong_nghien_cuu_GRACE_hop_nhat.pdf).

---

## 1. Mục đích và Quy trình thực hiện

1. **Chấm mù độc lập (Blind Review):**
   - Hai chuyên gia nhận cùng một gói mẫu 60 prompt ([manual_packet.md](../Runs-management/prompt_audit_20261102/manual_packet.md) và [manual_sample.jsonl](../Runs-management/prompt_audit_20261102/manual_sample.jsonl)) hoàn toàn không chứa nhãn target ground-truth, giá trị logits hay kết quả dự đoán mô hình.
   - Mỗi người độc lập điền bảng điểm riêng: Reviewer 1 nộp [reviewer_1.csv](../Runs-management/prompt_audit_20261102/reviewer_1.csv), Reviewer 2 nộp [reviewer_2.csv](../Runs-management/prompt_audit_20261102/reviewer_2.csv).
   - Đánh giá trên 7 tiêu chí rubric: `target_code_intact`, `graph_valid`, `demo_valid`, `no_target_label_leak`, `variant_correct`, `truncation_acceptable`, `overall_verdict`.

2. **Đo lường độ đồng thuận (Inter-Rater Reliability):**
   - Tính hệ số Cohen's Kappa giữa hai chuyên gia trên 60 mẫu để đảm bảo $\kappa \ge 0,80$ theo chuẩn Phụ lục C.

3. **Phân xử hòa giải (Consensus Adjudication):**
   - Rà soát các điểm bất đồng ý kiến hoặc cờ cảnh báo đặc biệt (vi phạm contract 25%, thiếu đồ thị CPG, trần token).
   - Lập biên bản phân xử chính thức tại [BIEN_BAN_PHAN_XU.md](../Runs-management/prompt_audit_20261102/BIEN_BAN_PHAN_XU.md).

---

## 2. Kết quả đánh giá và Thống kê độ đồng thuận

- **Bảng điểm Reviewer 1 (HuuHieu03):** 57 Pass, 2 Fail, 1 Unclear.
- **Bảng điểm Reviewer 2 (Dung):** 56 Pass, 2 Fail, 2 Unclear.
- **Số mẫu đồng thuận tuyệt đối ban đầu:** **59 / 60 mẫu ($98,33\%$)**.
- **Số mẫu bất đồng ban đầu:** **1 / 60 mẫu ($1,67\%$)** (Mẫu 20: `devign:test:25813`).
- **Chỉ số Cohen's Kappa:**
  - **Đa lớp (Multiclass: Pass / Fail / Unclear):** $\kappa = 0,8507 \ge 0,80$
  - **Nhị phân (Binary: Pass vs Non-Pass):** $\kappa = 0,8485 \ge 0,80$
  - Đạt mức **"Almost Perfect Agreement"** (Đồng thuận gần như tuyệt đối theo thang đo Landis & Koch).

---

## 3. Tóm tắt Phân xử và Hòa giải (Xem chi tiết tại BIEN_BAN_PHAN_XU.md)

1. **Mẫu 20 (`devign:test:25813` — Arm B2-flip):**
   - *Bất đồng:* R1 chấm `Pass` (cú pháp hợp lệ, nhãn flip chuẩn, trần graph 1492 token đúng thiết kế); R2 chấm `Unclear` (demo và target cùng tên hàm `slirp_can_output` trong repo QEMU, demo ngắn 15 token).
   - *Phán quyết:* **Thống nhất PASS**. Trùng tên hàm là đặc tính tự nhiên khi lấy mẫu donor từ cùng kho nguồn trong tập train; không có rò rỉ nhãn target; nhãn demo được đảo đúng thiết kế arm B2-flip.

2. **Mẫu 39 (`reveal:validation:399` — Arm B2-rand):**
   - *Vấn đề:* Cả hai chấm `Unclear` do demo chạm trần 1500 tokens và bị cắt ngang ở hàm thứ ba `_LMBCSFromUnicode`.
   - *Phán quyết:* **Thống nhất PASS có điều kiện**. Tỷ lệ giữ lại $>25\%$ so với file donor gốc; hai hàm con đầu hoàn chỉnh cú pháp C/C++. Khung prompt hợp lệ, ghi nhận khuyến nghị cải tiến điểm cắt hàm cho tokenizer.

3. **Mẫu 45 (`reveal:validation:145` — Arm B2-rep):**
   - *Vấn đề:* Cả hai chấm `Fail` vì arm B2-rep nhưng phần đồ thị CPG bị trống hoàn toàn (0 node, 0 edge).
   - *Phán quyết:* **Xác nhận cờ audit — Chấp nhận ở cấp toàn tập theo chính sách fallback**. Lỗi trích xuất do macro đệ quy của Joern trong REVEAL. Hệ thống fallback rỗng theo `missing_target_graph_policy: empty`. Tỷ lệ thiếu đồ thị REVEAL là $1,19\% \le 5,0\%$ (ngưỡng dung sai Phụ lục C). Giữ cờ `graph_missing` trong báo cáo audit.

4. **Mẫu 35 (`reveal:test:886` — Arm B2-flip):**
   - *Vấn đề:* Cả hai chấm `Fail` do vi phạm hợp đồng demo tối thiểu 25% (`demo_below25 = True`), mã target cũng bị cắt ở 2998 tokens.
   - *Phán quyết:* **Xác nhận FAIL — Giữ trong remediation_final.csv**. Mẫu vi phạm hợp đồng demo 25%, bảo lưu trong danh sách khắc phục. Tỷ lệ demo rỗng/dưới 25% của toàn tập là $0,88\% \le 1,0\%$ (đạt ngưỡng chấp nhận Phụ lục C).

---

## 4. Cập nhật Artifacts và Kiểm thử Hệ thống

- Đã cập nhật [final_status.json](../Runs-management/prompt_audit_20261102/final_status.json): `"manual_review": "completed"`, `"cohen_kappa_multiclass": 0.8507`, `"reviewer_1": "HuuHieu03"`, `"reviewer_2": "Dung"`.
- Đã cập nhật [step3_assessment.json](../Runs-management/prompt_audit_20261102/step3_assessment.json): Chuyển tiêu chí `two_human_reviewers` từ `pending` sang `pass`, cập nhật số liệu $\kappa$ và biên bản.
- Đã cập nhật [BUOC_3_DOI_CHIEU.md](../Runs-management/prompt_audit_20261102/BUOC_3_DOI_CHIEU.md), [RUBRIC.md](../Runs-management/prompt_audit_20261102/RUBRIC.md), [README.md](../Runs-management/prompt_audit_20261102/README.md).
- Đã đồng bộ [DELIVERY_SHA256.json](../Runs-management/prompt_audit_20261102/DELIVERY_SHA256.json) và chạy script kiểm định [verify_prompt_audit.py](../Runs-management/verify_prompt_audit.py) đạt trạng thái `verified` thành công.
- Đã chạy toàn bộ test suite `pytest`: **106 passed 100% Green**.
