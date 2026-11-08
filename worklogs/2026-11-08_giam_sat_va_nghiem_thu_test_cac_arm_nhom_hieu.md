# Báo cáo Giám sát, Nghiệm thu Test & Vận hành Checkpoint Nhóm Hiếu — 08/11/2026

**Thời điểm cập nhật**: `01:45:00+07:00` (`18:45:00 UTC`), ngày `08/11/2026`  
**Người thực hiện**: Nhóm Hiếu & AI Assistant (Antigravity)  
**Phạm vi**: 6 Arm chẩn đoán phụ trách (`B1-full`, `B2-rep`, `B2-labelonly`, `B2-nolabel`, `B1-shuf`, `B3`).

---

## 1. TỔNG QUAN TIẾN ĐỘ THỰC TẾ 6 KERNEL (EXECUTIVE DASHBOARD)

| STT | Arm | Loại tập | Tài khoản / Kernel Slug | Tình trạng Hiện tại (Live Status) | Chi tiết Tiến độ & Nghiệm thu |
| :---: | :--- | :---: | :--- | :---: | :--- |
| 1 | **`B2-labelonly`** | **Test** | `tomandjerry223/grace-b2-labelonly-test` | **COMPLETE** 🏆 (100% Census) | **ĐÃ HOÀN TẤT & TẢI VỀ TOÀN BỘ OUTPUT**:<br>- Tổng số mẫu: $5.006/5.006$ ($2.732$ Devign + $2.274$ ReVeal), 100% valid.<br>- Devign Test ($\tau^*=0.99$): $\text{AUROC}=0.5462, \text{MCC}=0.0849, \text{BA}=0.5322, \text{F1}=0.3013$.<br>- ReVeal Test ($\tau^*=0.02$): $\text{AUROC}=0.6005, \text{MCC}=0.1199, \text{BA}=0.5986, \text{F1}=0.2310$.<br>- Archive: `grace_b2_labelonly_test_final_output.zip` ($881.820$ bytes). |
| 2 | **`B2-nolabel`** | **Test** | `tomandjerry223/grace-b2-nolabel-test` | **RUNNING** 🟢 (~7h 45m) | - Tiến trình suy luận đang ở những batch cuối cùng sát ngưỡng hoàn tất.<br>- Khóa ngưỡng: Devign $\tau^*=0.98$, ReVeal $\tau^*=0.21$. |
| 3 | **`B1-full`** | **Test** | `huuhieu3333/grace-b1-full-test` | **RUNNING** 🟢 (~6h 55m) | - Chạy liên tục ổn định trên 2x T4 GPU.<br>- Khóa ngưỡng: Devign $\tau^*=0.99$, ReVeal $\tau^*=0.01$. |
| 4 | **`B2-rep`** | **Test** | `huuhieu3333/grace-b2-rep-test` | **RUNNING** 🟢 (~6h 42m) | - Chạy liên tục ổn định với thiết lập cách ly cache (`repeat: true`, `tag="repeat"`).<br>- Kế thừa ngưỡng từ B2: Devign $\tau^*=0.70$, ReVeal $\tau^*=0.12$. |
| 5 | **`B3`** | **Validation** | `lznt123/grace-b3-validation` | **RUNNING** 🟢 (~6h 09m) | - Chạy trên dataset $10.010$ mẫu validation (`grace_b3_validation_inputs.zip`). |
| 6 | **`B1-shuf`** | **Test** | `lznt123/grace-b1-shuf-test` | **QUEUED** ⏳ (v2 Runtime-Locked) | - Đã nạp trọn bộ $15.018$ prompts Test (3 seeds: 42, 43, 44) qua Dataset `lznt123/grace-b1-shuf-test-inputs`.<br>- Khóa chuẩn 9-cell runtime `grace_qwen_q4_runtime_v1` (49/49 GPU offload, seeds 4294967295, split_mode LAYER).<br>- Đang chờ bộ lập lịch Kaggle cấp phát node GPU. |

---

## 2. CÔNG TÁC NGHIỆM THU & BẢO ĐẢM TOÀN VẸN DỮ LIỆU

### 2.1. Nghiệm thu Toàn diện Arm B2-labelonly Test
- Tải về và xác minh tính toàn vẹn của thư mục output:
  * `grace_b2_labelonly_test_final_output.zip` ($881.820$ bytes)
  * `records.jsonl` Devign: Đủ $2.732$ dòng hợp lệ.
  * `records.jsonl` ReVeal: Đủ $2.274$ dòng hợp lệ.
  * `evaluation.json`: Đã đối soát khớp chính xác 100% với ngưỡng locked validation.
  * `events.log`: Xác nhận biên dịch CUDA SM75 thành công, nạp 49/49 layers vào 2 GPU Tesla T4.
- Đã lưu trữ an toàn tại: `Runs-management/kernel_outputs_harvest/tomandjerry223_grace-b2-labelonly-test/` và `Runs-management/output_b2_labelonly_test_complete/`.

### 2.2. Kiểm toán Cơ chế Checkpoint Resume & Vá lỗi Tiềm ẩn trong Test Notebooks
- **Phát hiện quan trọng**: Khi rà soát mã nguồn khôi phục checkpoint ở Cell 3 của các notebook Test, phát hiện đoạn mã:
  ```python
  allowed = {f'seed_{seed}/{ds}/validation/{file}'
             for seed, ds in bundles for file in ('records.jsonl', 'run_manifest.json')}
  ```
  Do các template test được kế thừa từ notebook validation, đường dẫn hardcoded `/validation/` thay vì `/test/`. Nếu một notebook test bị chạm trần thời gian (timeout) và sinh ra checkpoint zip với cấu trúc `seed_42/devign/test/records.jsonl`, khi nạp lại checkpoint này để resume thì Cell 3 sẽ lọc bỏ toàn bộ file và bắn ra lỗi: `ValueError: Checkpoint has no records for this run`.
- **Hành động khắc phục**: Đã chỉnh sửa toàn bộ các template test và file staging sang định dạng an toàn:
  ```python
  allowed = {f'seed_{seed}/{ds}/{split}/{file}'
             for seed, ds in bundles for file in ('records.jsonl', 'run_manifest.json')
             for split in ('test', 'validation')}
  ```
- Kiểm toán hồi quy: Chạy `pytest tests/test_preregistration_integrity.py` đạt 6/6 test passed.

### 2.3. Tự động hóa Giám sát và Thu hoạch (Automated Harvesting Pipeline)
- Script `scripts/handle_kernel_completion_or_resume.py` đã được nâng cấp:
  * Khắc phục triệt để lỗi mã hóa Windows `cp1252` bằng monkeypatch UTF-8 cho Kaggle SDK.
  * Tự động kiểm tra đồng thời cả 6 kernel trên 3 tài khoản (`huuhieu3333`, `tomandjerry223`, `lznt123`).
  * Khi phát hiện trạng thái `COMPLETE`, tự động tải artifact, giải nén và kiểm đếm census `records.jsonl`.
  * Nếu phát hiện trạng thái `TIMED_OUT` hoặc dừng trước census, tự động cảnh báo và sẵn sàng gói checkpoint để resume.

---

## 3. KẾ HOẠCH BÀN GIAO & BƯỚC TIẾP THEO

1. **Thu hoạch `B2-nolabel`**: Tiếp tục theo dõi `tomandjerry223/grace-b2-nolabel-test` (chuẩn bị kết thúc trong ít phút tới) để tải về và nghiệm thu census $5.006$ mẫu.
2. **Theo dõi 2 Kernel của `huuhieu3333`**: Dự kiến hoàn tất vào khoảng 02:00 - 02:30 sáng 08/11/2026. Nếu có kernel nào chạm mốc thời gian tối đa, sẽ kích hoạt ngay quy trình resume từ checkpoint đã vá.
3. **Theo dõi `lznt123/grace-b1-shuf-test`**: Đảm bảo kernel chuyển từ `QUEUED` sang `RUNNING` và xác nhận log nạp đủ 49/49 GPU layers.
