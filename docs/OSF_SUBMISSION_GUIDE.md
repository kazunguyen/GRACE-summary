# Cẩm Nang Từng Bước Nộp Hồ Sơ Đăng Ký Trước Lên OSF Registries
## (Step-by-Step OSF Registries Submission Guide for GRACE Replication)

> **Mã hồ sơ:** `grace_diag_replication_v1`  
> **Phiên bản:** `prereg-v1`  
> **Tài liệu nộp chính:** `Runs-management/osf_registration_draft_20261102/output/pdf/GRACE_OSF_PREREGISTRATION_20261102.pdf`  
> **Tệp nén độc lập đính kèm:** `Runs-management/osf_registration_draft_20261102/GRACE_OSF_PREREGISTRATION_20261102.zip`  
> **Bảng mã băm kiểm toán:** `Runs-management/osf_registration_draft_20261102/attachment_sha256.json`  

---

## 1. Chuẩn Bị Trước Khi Nộp (Pre-Submission Checklist)

Trước khi truy cập cổng OSF Registries, người nộp cần đảm bảo:
1. Đã cài đặt Git và xác nhận repository ở trạng thái sạch:
   ```powershell
   git status
   ```
2. Đã chạy kiểm thử tự động toàn diện và kiểm toán dry-run 15 arm thành công (100% pass):
   ```powershell
   python -m pytest 01_Author_Baseline_Unified/diagnostic_kit/tests/test_probes.py
   python -m pytest 01_Author_Baseline_Unified/diagnostic_kit/tests/test_stats_and_complementarity.py
   python -m pytest tests/test_preregistration_integrity.py
   python Runs-management/dry_run_full_validation.py --all-15-arms --missing-target-graph empty
   ```
3. Đã biên dịch bộ tài liệu nộp hoàn chỉnh:
   ```powershell
   python scripts/build_osf_preregistration_bundle.py
   ```
4. Đã đối chiếu các tệp đầu ra tại `Runs-management/osf_registration_draft_20261102/`:
   - `output/pdf/GRACE_OSF_PREREGISTRATION_20261102.pdf` (~365 KB)
   - `GRACE_OSF_PREREGISTRATION_20261102.zip` (~420 KB)
   - `attachment_sha256.json` (chứa SHA-256 của 39 tệp cốt lõi)

---

## 2. Quy Trình Nộp Từng Bước Trên Giao Diện Web OSF Registries

### Bước 2.1: Truy cập và khởi tạo Registration
1. Mở trình duyệt web, truy cập: **[https://osf.io/registries](https://osf.io/registries)**
2. Đăng nhập vào tài khoản OSF của tác giả / chủ nhiệm đề tài.
3. Nhấp vào nút **"Add New Registration"** (hoặc chọn project GRACE nếu đã tạo từ trước trên OSF -> chọn tab **Registrations** -> **New Registration**).
4. **Chọn Template Đăng Ký (Registration Form):**
   - Chọn template tiêu chuẩn: **OSF Preregistration** (hoặc *Open-Ended Registration*).
   - Nhấp **Create draft**.

---

### Bước 2.2: Điền Thông Tin Siêu Dữ Liệu (Metadata)

* **Title (Tiêu đề nghiên cứu):**
  ```text
  Diagnostic Replication of GRACE: Evaluating Graph Representations and In-Context Demonstration Retrieval for LLM-Based Vulnerability Detection
  ```

* **Contributors (Tác giả & Đơn vị công tác):**
  - Thêm đầy đủ tài khoản OSF / ORCID của các thành viên trong nhóm nghiên cứu đề tài GRACE.
  - Phân quyền (Permissions): Chủ nhiệm đề tài giữ quyền *Administrator*, các cộng sự giữ quyền *Read + Write*.

* **Description (Tóm tắt đề cương / Abstract):**
  ```text
  This preregistration outlines a diagnostic replication and ablation study of GRACE (Graph-based In-Context Learning for Vulnerability Detection). We systematically decompose the GRACE pipeline across 15 diagnostic arms on Devign (N=5,464) and REVEAL (N=4,547) benchmarks using Qwen3-Coder-30B-A3B-Instruct (GGUF Q4_K_M). The study investigates: (1) whether textualized Code Property Graphs (CPG) convey genuine structural signal over raw source code (B0 vs B1 vs B1-shuf vs B1-full vs B1-H2); (2) whether in-context demonstrations operate through semantic program logic or surface label biases (B2 vs B2-rand vs B2-nolabel vs B2-labelonly vs B2-flip vs B2-rep); (3) whether contrastive demonstration pairs with differential explanations provide operational improvements (B3 vs B3-nodiff vs B3-swap vs B3-flip); and (4) whether LLM representations offer orthogonal complementarity when routed alongside frozen CodeT5 embeddings and supervised baselines. All 14 decision thresholds are strictly locked on validation splits prior to test evaluation under a zero-test-exposure protocol.
  ```

* **License:**
  - Chọn **CC-By Attribution 4.0 International** hoặc **MIT License**.

* **Subject / Category:**
  - Computer Sciences -> Software Engineering -> Computer and Information Security.

* **Keywords:**
  ```text
  Vulnerability Detection, Large Language Models, In-Context Learning, Code Property Graph, Diagnostic Replication, Pre-registration, Software Security, Qwen3-Coder
  ```

---

### Bước 2.3: Điền Mục Hypotheses (Các Giả Thuyết Khoa Học)

Sao chép nguyên văn 11 giả thuyết từ Bảng 4.3 trong `preregistration.md`:

```text
- H1.1 (GRACE vs Zero-shot on Devign): Arm B2 does not outperform B0 on Devign Test: Upper bound of 95% CI for ΔMCC(B2 - B0) < 0.03 and ΔAUROC < 0.02 (practical equivalence margin δ = 0.02).
- H1.2 (GRACE vs Zero-shot on REVEAL & Published Benchmark): Arm B2 does not outperform B0 on REVEAL Test (ΔMCC < 0.03, ΔAUROC < 0.02). GRACE does not reproduce published MCC >= 0.15 on either benchmark; Devign B2 F1 is below always-vulnerable baseline (62.95%).
- H2.1 (Surface Label Sensitivity): Demonstrations act predominantly via surface label priming: Net label sensitivity >= 15 percentage points (|B2 - B2-flip| minus |B2 - B2-rep| natural variance).
- H2.2 (Code Invariance in Demos): Demo source code does not provide intrinsic logic signals: Upper bound of CI for ΔAUROC(B2 - B2-rand) < 0.02 and ΔAUROC(B2-nolabel - B1) < 0.02; B2-labelonly recovers >= 80% of (B2 - B1) delta.
- H2.3 (Contrastive Demonstration Operating Point): Contrastive pairs (B3) shift operating decision points without improving discriminative capacity: B3 positive prediction rate is >= 10 percentage points higher than B2 while upper bound of 95% CI for ΔAUROC(B3 - B2) < 0.02.
- H3.1 (LLM Graph Invariance): Textual CPG information does not provide additional discriminative signal: Upper bound of CI for ΔAUROC(B1 - B0) < 0.02 and ΔAUROC(B1 - B1-shuf) < 0.02; B1-H2 (guarded evidence) shows equivalent behavior.
- H4.1 (Threshold-Free Randomness): Across all LLM arms, AUROC <= 0.62 on both Devign and REVEAL.
- H5.1 (Supervised Baseline Superiority): Supervised classifier on frozen CodeT5 embeddings (SUP-LR) substantially outperforms LLM pipeline: ΔMCC(SUP-LR - B2) >= 0.15 with CI excluding 0; AUROC(SUP-LR) >= 0.68.
- H5.2 (No Orthogonal LLM Signal): LLM output scores do not add orthogonal predictive value over 34 base features: Upper bound of 95% CI for ΔMCC(P_post - P_pre) < 0.02 under identical StratifiedGroupKFold splits.
- H5.3 (Expert Routing Efficacy at q=10%): Benefit router (Ridge) does not outperform Confidence router: Paired Bootstrap CI upper bound for ΔBalanced_Accuracy(benefit - confidence) < 0.02; ΔBalanced_Accuracy(benefit - random) < 0.01; LLM error corrections do not exceed 95th percentile of equal-rate random expert across 20 seeds.
- H6.1 (Retrieval Mechanism Mismatch): Retrieved demonstrations rarely match true underlying vulnerability mechanisms: "Neither" rate >= 40% on Devign; accuracy difference between related and unrelated demos has CI containing 0.
```

---

### Bước 2.4: Điền Design Plan & Data Disclosure (Khai Báo Dữ Liệu)

* **Study Design:**
  ```text
  15-arm observational benchmark replication experiment. Fully factorial ablation across graph representations (B0, B1, B1-shuf, B1-full, B1-H2), demonstration content (B2, B2-rand, B2-nolabel, B2-labelonly, B2-flip, B2-rep), and contrastive pairs (B3, B3-nodiff, B3-swap, B3-flip), alongside 3 supervised frozen-embedding baselines (SUP-LR, SUP-MLP, SUP-METRIC) and meta-models (P-PRE, P-POST).
  ```

* **Data Exposure Disclosure (Minh bạch tiếp xúc dữ liệu):**
  ```text
  PRIOR DATA EXPOSURE DISCLOSURE:
  Validation sets of Devign (N=2,732) and REVEAL (N=2,273) have been accessed during exploratory pilot runs, threshold optimization, and offline dry-run verification.
  TEST SET COMMITMENT (ZERO-TEST-EXPOSURE):
  The test sets (Devign N=2,732; REVEAL N=2,274) have strictly NOT been subjected to model inference or threshold tuning for this preregistered protocol. All 14 decision thresholds (tau*) are frozen on validation splits and sealed in configs/thresholds.json prior to test execution. Any subsequent modification will be classified as exploratory post-hoc and documented in CHANGES_AFTER_PREREG.md.
  ```

* **Sample Sizes (Cỡ mẫu):**
  - Devign: 2,732 Validation, 2,732 Test (Total 5,464). Clean donor bank: 21,691.
  - REVEAL: 2,273 Validation, 2,274 Test (Total 4,547). Clean donor bank: 17,636.

---

### Bước 2.5: Điền Analysis Plan & Statistical Rules (Kế Hoạch Phân Tích)

* **Statistical Estimators & Bootstrap Specification:**
  ```text
  - Paired Cluster Bootstrap: B = 5,000 iterations, fixed random seed 20261117.
  - Cluster Units: Devign clustered by commit_id (2,068 clusters); REVEAL clustered by file_hash (646 clusters).
  - Multiple Testing Correction: Holm-Bonferroni step-down procedure (family_correction: holm).
  - Decision Rule Margins: Practical equivalence margin delta = 0.02 (delta_MCC = 0.03, delta_AUROC = 0.02, delta_BA = 0.01).
  - Verdict Classification:
    * 'benefit': CI lower bound > 0 and point estimate >= delta.
    * 'no_meaningful_benefit': CI upper bound < delta.
    * 'harm': CI upper bound < 0.
    * 'inconclusive': CI overlaps 0 and upper bound >= delta.
  - Threshold Fitting: 14 optimal thresholds tau* locked via argmax MCC on validation grid [0.01, 0.99] step 0.01.
  ```

---

### Bước 2.6: Tải Lên Tệp Đính Kèm (Upload Attachments)

Tại phần **Files / Attachments** của form OSF:
1. **Primary Registration Document:** Tải lên tệp:
   `Runs-management/osf_registration_draft_20261102/output/pdf/GRACE_OSF_PREREGISTRATION_20261102.pdf`
2. **Reproducible Code & Configuration Archive:** Tải lên tệp:
   `Runs-management/osf_registration_draft_20261102/GRACE_OSF_PREREGISTRATION_20261102.zip`
3. **Checksum Verification File:** Tải lên tệp:
   `Runs-management/osf_registration_draft_20261102/attachment_sha256.json`
4. Trong ô chú thích (File Description), ghi rõ:
   ```text
   Stand-alone reproducible preregistration pack containing protocol YAML, frozen threshold tables, analysis lock manifests, 15-arm validation dry-run audit summary (95,095 prompts rendered, 0 leaks, 0 LLM calls), and core diagnostic evaluation code. All files verified against SHA-256 digests in attachment_sha256.json. Permanent GitHub repository tag: https://github.com/kazunguyen/GRACE-summary/tree/prereg-v1
   ```

---

### Bước 2.7: Xem Trước, Chọn Chế Độ Công Khai & Gửi Hồ Sơ (Review & Submit)

1. Nhấp **Review / Preview** để xem lại toàn bộ các trường đã điền.
2. Kiểm tra kỹ:
   - Các bảng số liệu, đường link, mã hash SHA-256 không bị lỗi định dạng.
   - Tên và email của các tác giả đã chính xác.
3. **Lựa chọn Chế độ Công bố (Registration Visibility):**
   - **Public immediately (Công khai ngay):** Khuyến nghị chọn chế độ này nếu đề tài chuẩn bị chạy test set ngay lập tức.
   - **Embargo (Tạm khóa bảo mật):** Chọn thời gian embargo nếu đề tài cần bảo mật quyền ưu tiên công bố (tối đa 4 năm). Trong thời gian embargo, OSF cấp URL riêng tư để gửi ban biên tập / phản biện.
4. Nhấp nút **Submit**.
5. **Xác nhận qua Email:**
   - Mọi tác giả có tên trong danh sách Contributors sẽ nhận được email tự động từ OSF Registries để phê duyệt việc đăng ký.
   - Các tác giả cần nhấp vào liên kết xác nhận trong email trong vòng 48 giờ để hồ sơ chính thức được đóng dấu thời gian (Timestamped) và cấp mã định danh vĩnh viễn (DOI).

---

## 3. Lưu Trữ Biên Bản Sau Khi Nộp Thành Công (Post-Submission Archive)

Sau khi OSF Registries phê duyệt và cấp mã DOI / Registration URL:
1. **Ghi lại mã định danh:** Lưu lại URL đăng ký chính thức (dạng `https://osf.io/XXXXX`) và DOI.
2. **Xác nhận thẻ Git Tag chính thức (`prereg-v1`):**
   ```powershell
   git tag -a "prereg-v1" -m "Official OSF Preregistration v1: GRACE Diagnostic Replication (15 arms, Qwen3-Coder-30B, exposure ledger, self-signing locked thresholds)"
   git push origin prereg-v1
   ```
3. **Khóa Bất Biến Tuyệt Đối:**
   - Giữ nguyên toàn bộ tệp byte trong `Runs-management/osf_registration_draft_20261102/`.
   - Tuyệt đối không sửa lại file PDF hay ZIP cũ để chèn URL sau đăng ký (tất cả thông tin bổ sung sau khi gửi phải được ghi vào biên bản mới `OSF_CONFIRMATION_RECEIPT.md`).
4. **Tiến hành Bước 5 (Test Set Inference):** Chỉ sau khi hồ sơ trên OSF đã có trạng thái *Approved* / *Active*, nhóm nghiên cứu mới được phép bắt đầu chạy suy luận trên tập Test.
