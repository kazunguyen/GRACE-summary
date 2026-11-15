# Liên kết code → records cho 20 nhóm records (15/11/2026)

Trả lời thư nháp [DRAFT_EMAIL_TO_HIEU_RUN_CODE_PROVENANCE.md](../docs/DRAFT_EMAIL_TO_HIEU_RUN_CODE_PROVENANCE.md). Thư hỏi notebook/worker đã tạo 20 nhóm records: B1-full validation, B1-shuf validation s42–44, B2-labelonly, B2-nolabel và B2-rep (validation và test). Trả lời: [REPLY_RUN_CODE_PROVENANCE_HIEU.md](../docs/REPLY_RUN_CODE_PROVENANCE_HIEU.md).

## Đã làm

- Đọc lại từ Kaggle (chỉ đọc, không chạy lại) các kernel trên `huuhieu3333`, `thanhduy9a4tv` và `tomandjerry223`. Kaggle CLI 1.7.4.5 chưa nhận token `KGAT_`, nên đã gọi API `kernels/pull` và `kernels/output` trực tiếp.
- Nối mỗi nhóm records với worker theo ba bước:
  1. records trong output/checkpoint của phiên trùng byte records chuẩn;
  2. lấy SHA-256 worker ghi ra `/kaggle/working`;
  3. kiểm worker nằm nguyên văn trong notebook của phiên.
- Kết quả: 20/20 nhóm nối được với worker. Có ba worker:
  - W-val `e8aecdce…`;
  - W-val-rep `c418ea67…`;
  - W-test `9a0e5c33…`.
- B1-shuf validation:
  - Tìm được output phiên 2 (`thanhduy9a4tv`, 05/11 04:15 → 13:29) đã tải về ngày 07/11 trong `Runs-management/check_b1_shuf_output`. "2.113 record ngoài cửa sổ phiên" là phần phiên 2 sinh ra.
  - Chuỗi ba phiên khớp: checkpoint cuối mỗi phiên là tiền tố đúng của records chuẩn; `run_manifest` trùng ở mọi trường ổn định; cùng 6 bundle prompt.
  - `prompt_sha256` tính lại từ bundle trùng ở 15.015/15.015 records. Khuôn trường record đúng W-val.
  - W-val kiểm `prompt_sha256`/`model_sha256` từng dòng checkpoint cũ khi resume, và phiên 3 chạy hết.
- Gom bằng chứng vào [Runs-management/run_code_provenance_20261115/](../Runs-management/run_code_provenance_20261115/README.md), kèm `verify_provenance.py`. Kết quả 78/78 kiểm tra đạt (có bundle) và 72/72 (không có bundle).

## Lưu ý

- Kaggle API chỉ trả version mới nhất của mỗi kernel.
  - Notebook đúng version của B1-shuf phiên 1 không đọc lại được.
  - Output phiên 2 trên Kaggle đã bị version 2 (`pause.ipynb`) thay thế.
  - Liên kết của hai phiên này dựa trên checkpoint, `run_manifest`, `prompt_sha256` và kiểm resume.
- `lastRunTime` ngày 12/11 trên các kernel `thanhduy9a4tv` và `huuhieu3333` không ứng với phiên inference nào. Output vẫn là của phiên 04/11 và 07/11.
- Notebook trong `05_Arm_B2_Rep/notebooks/` và `12_Arm_B2_LabelOnly/notebooks/` đã được sửa sau phiên chạy (thêm ghi chú package lock và cell runtime lock), nên không trùng bản chạy. Bản chạy là notebook đọc lại từ Kaggle, trùng `Runs-management/downloaded_executed_notebooks/` và commit `946a86b` / `5413e05`.
- Native/build log chưa đối chiếu lại trong đợt này.
- Các token Kaggle dùng để đọc lại cần được thu hồi.

## Còn cần

- Dũng xác nhận lại bằng `verify_provenance.py` trên máy có `runs/final/`.
- Nếu cần bằng chứng trực tiếp cho B1-shuf phiên 1–2: tải notebook/output version cũ qua giao diện web Kaggle (tab Versions).
