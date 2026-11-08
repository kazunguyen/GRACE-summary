# Khóa ngưỡng Validation và Chuẩn bị gói Test Census cho 4 Arm Nhóm 2 — 07/11/2026

## 1. Bối cảnh và Mục tiêu

Tiến hành chốt và khóa chính thức ngưỡng tối ưu $\tau^*$ trên 100% census Validation cho 4 arm thuộc Nhóm 2 (Group 2), đồng thời chuẩn bị trọn bộ bundles đầu vào và notebooks chạy Kaggle GPU 2x Tesla T4 trên toàn bộ census Test (5.006 mẫu: 2.732 Devign + 2.274 ReVeal).

Các arm bao gồm:
1. `B2-rep`: Kế thừa nguyên tắc từ B2 per OSF Preregistration Section 2.3; bắt buộc cách ly cache tuyệt đối (`repeat: true`, `tag="repeat"`).
2. `B1-full`: Biến thể Graph-only lấp đầy ngân sách graph 1.500 tokens từ CPG Joern.
3. `B2-nolabel`: Biến thể ICL giữ nguyên demonstration code nhưng loại bỏ nhãn trong prompt demo.
4. `B2-labelonly`: Biến thể ICL chỉ đưa câu thông báo nhãn của hàm tương đồng, không kèm code demo.

Tuân thủ nghiêm ngặt hợp đồng điều hành `AGENTS.md`:
- Không sửa đổi bất kỳ deliverables đã đăng ký trên OSF (`release/osf-preregistration`, `tag prereg-v1`, `osf_registration_draft_20261102/`).
- Không tìm kiếm hoặc tinh chỉnh lại ngưỡng trên tập test (strict no-test-refit policy).
- Toàn bộ hồ sơ khóa ngưỡng có chữ ký tự xác thực SHA-256 (`locked_sha256`).

---

## 2. Bảng tổng hợp Ngưỡng Validation đã khóa

Tất cả các giá trị được tối ưu hóa trên grid $\tau \in [0.01, 0.99]$ với bước nhảy 0.01 dựa trên chỉ số MCC từ các điểm số hợp lệ trên toàn bộ census Validation ($N=2.732$ Devign, $N=2.273$ ReVeal):

| Arm | Dataset | N Validation | $\tau^*$ | MCC tại $\tau^*$ | AUROC | Balanced Acc | F1 | Quy tắc khóa & Kế thừa |
|---|---|---:|---:|---:|---:|---:|---:|---|
| **B2-rep** | Devign | 2.732 | **0.70** | 0.0547 | 0.5256 | 52.70% | 0.5304 | Kế thừa trực tiếp từ B2 (OSF Prereg 2.3) |
| **B2-rep** | ReVeal | 2.273 | **0.12** | 0.0823 | 0.5544 | 57.09% | 0.1956 | Kế thừa trực tiếp từ B2 (OSF Prereg 2.3) |
| **B1-full** | Devign | 2.732 | **0.99** | 0.0746 | 0.5325 | 52.99% | 0.3169 | Tối ưu hóa trên full census Validation |
| **B1-full** | ReVeal | 2.273 | **0.01** | 0.0870 | 0.5790 | 57.49% | 0.1975 | Tối ưu hóa trên full census Validation |
| **B2-nolabel** | Devign | 2.732 | **0.98** | 0.0450 | 0.5247 | 52.17% | 0.4146 | Tối ưu hóa trên full census Validation |
| **B2-nolabel** | ReVeal | 2.273 | **0.21** | 0.0651 | 0.5547 | 55.60% | 0.1879 | Tối ưu hóa trên full census Validation |
| **B2-labelonly** | Devign | 2.732 | **0.99** | 0.0917 | 0.5474 | 53.44% | 0.2963 | Tối ưu hóa trên full census Validation |
| **B2-labelonly** | ReVeal | 2.273 | **0.02** | 0.0847 | 0.5798 | 57.16% | 0.1989 | Tối ưu hóa trên full census Validation |

### Hồ sơ khóa ngưỡng per-arm:
- `05_Arm_B2_Rep/config/threshold.json` (Lock SHA-256: `6fe63a18e001c37ad18caea7493630f65306be5009da238549925b44fa73eef1`)
- `09_Arm_B1_Full/config/threshold.json` (Lock SHA-256: `cf2b4bc3f15b8109bfcf99e525ae2003c4f74d0e74f141444983a9a149c41793`)
- `10_Arm_B2_NoLabel/config/threshold.json` (Lock SHA-256: `789ba85be196e85c8e3100ba705295796df104eb0a69a341e97cfc1573516ff9`)
- `12_Arm_B2_LabelOnly/config/threshold.json` (Lock SHA-256: `9478f7e914eb13df426c19f5d14df9cfd0c0d80e12d46e310bf85bb4dfd60e7f`)

---

## 3. Chuẩn bị gói Test Census trên Kaggle

Đã hoàn thành sinh gói input bundle và notebook chạy Kaggle cho cả 4 arm tại `Runs-management/kaggle_test_4arms_20261107/`:

### 3.1. Input Bundles
Mỗi outer zip chứa 2 inner zips (`seed_42/devign_test.zip` và `seed_42/reveal_test.zip`), bao gồm đầy đủ `bundle_manifest.json`, `prompts.jsonl`, và `threshold_lock.json`:
- `grace_b2_rep_test_inputs.zip` (SHA-256: `6bef9c79d2a3802b43d9d79d56112253ef23faa9b48c4080a085328e3b01ee0e`)
- `grace_b1_full_test_inputs.zip` (SHA-256: `0c6653730e068473926391a00ddf5ad721105a583ad840fabd35546f47093814`)
- `grace_b2_nolabel_test_inputs.zip` (SHA-256: `a1cdd31345de7fe4f95a592adc583e021427a288327850cf837fcef65ebcae1c`)
- `grace_b2_labelonly_test_inputs.zip` (SHA-256: `84093323c3dbbe3fec7052e5f76e1332f8fcc3a27e886806c5895974f4d88004`)

### 3.2. Notebooks thực thi
Các notebook được cấu hình theo chuẩn `configs/inference_runtime_lock.json`:
- Ngân sách 9 giờ wall-clock, dành 300s xuất checkpoint.
- Tự động kiểm tra GPU 2x Tesla T4, ghim phiên bản môi trường (`transformers==4.57.1`, `huggingface_hub==0.36.2`, `tokenizers==0.22.2`, `scikit-learn==1.5.2`, `numpy==2.1.3`, `llama-cpp-python==0.3.16`).
- Ghi nhận `tau` và `pred_tau = int(s >= tau)` cho từng mẫu; tính toán chỉ số test chính thức tự động.
- Riêng B2-rep ghi nhận `repeat: true` và `tag: "repeat"` vào từng record để ngăn ngừa tuyệt đối việc đọc đè cache B2.

Notebooks được xuất bản vào:
- `Runs-management/kaggle_test_4arms_20261107/notebooks/`
- Thư mục riêng của từng arm:
  - `05_Arm_B2_Rep/notebooks/02_kaggle_qwen_q4_b2_rep_test.ipynb`
  - `09_Arm_B1_Full/notebooks/02_kaggle_qwen_q4_b1_full_test.ipynb`
  - `10_Arm_B2_NoLabel/notebooks/02_kaggle_qwen_q4_b2_nolabel_test.ipynb`
  - `12_Arm_B2_LabelOnly/notebooks/02_kaggle_qwen_q4_b2_labelonly_test.ipynb`

### 3.3. Kiểm tra bàn giao (Delivery Verification)
Đã chạy script `Runs-management/kaggle_test_4arms_20261107/verify_delivery.py`:
- 100% kiểm tra khớp SHA-256 gói outer zip, inner zips, manifests và prompt counts.
- 100% số lượng mẫu khớp chuẩn Test census (2.732 Devign, 2.274 ReVeal).
