# Trả lời: xác nhận notebook/worker của các run được giao Hiếu

Trả lời thư nháp [DRAFT_EMAIL_TO_HIEU_RUN_CODE_PROVENANCE.md](DRAFT_EMAIL_TO_HIEU_RUN_CODE_PROVENANCE.md). Đối chiếu ngày 15/11/2026.

- Tất cả các phiên trong bảng của thư do Hiếu chạy qua Kaggle CLI, trên các tài khoản `tomandjerry223`, `thanhduy9a4tv` và `huuhieu3333`.
- Records không có trường hash code (chỉ có `prompt_sha256`, `model_sha256`). Vì vậy mỗi nhóm được nối qua phiên Kaggle theo ba bước:
  1. records chuẩn trùng từng byte (sau chuẩn hóa LF) với records trong checkpoint hoặc final output của phiên;
  2. lấy SHA-256 của worker mà phiên đó ghi ra `/kaggle/working`;
  3. kiểm mã nguồn worker có nằm nguyên văn trong notebook của phiên.
- Kết quả: **20/20 nhóm nối được với worker**. Riêng B1-shuf có kiểm thêm theo chuỗi ba phiên, `run_manifest` và `prompt_sha256` (mục 2). Giới hạn ở số version Kaggle nêu ở mục 3; bằng chứng và script kiểm lại ở mục 4.

## 1. Worker và notebook

| Mã | File | SHA-256 |
|---|---|---|
| W-val | `kaggle_inference.py` (validation, B1-full / B1-shuf / B2-nolabel / B2-labelonly) | `e8aecdce40bfadcd98f272318af0df0127b7fb1d41ef78541c7474114840fec3` |
| W-val-rep | `kaggle_inference.py` (validation B2-rep: khác W-val ở chỗ chỉ chạy cho arm B2-rep, ghi `repeat=True`, `tag=repeat` vào record và kiểm tra hai trường này khi resume checkpoint) | `c418ea6774a9cd24852b4b408143b559fd7f1562ef8eca44e38c60877f772e40` |
| W-test | `kaggle_test_inference.py` (test B2-nolabel / B2-labelonly / B2-rep) | `9a0e5c3363817b7f8ce49032286994d1da0e176e2cfc85e002c3785bf92e14b6` |

Mỗi worker nằm nguyên văn trong notebook tương ứng ở bảng dưới. Notebook ghi worker ra `/kaggle/working`, và `events.log` của phiên chạy `/kaggle/working/kaggle_inference.py`.

## 2. Ánh xạ 20 nhóm records

| Nhóm (seed 42 trừ khi ghi khác) | Kernel | Cửa sổ records (UTC) | Worker | Notebook (SHA-256, LF) | Records khớp |
|---|---|---|---|---|---|
| B1-full validation, Devign + ReVeal | `tomandjerry223/grace-b1-full-validation` | 04/11 09:56 → 16:54 | W-val | `0ec50247…01afc0` | checkpoint phiên, 2/2 |
| B1-shuf validation, phiên 1: s42 Devign + ReVeal, s43 Devign #1–1125 | `tomandjerry223/grace-b1-shuf-validation` | 04/11 19:14 → 05/11 04:06 | W-val (qua kiểm resume của phiên 3) | không đọc lại được version phiên 1 | checkpoint cuối phiên (dataset input của phiên 2): s42 2/2 khớp nguyên file; s43 Devign 1.125 dòng là tiền tố đúng |
| B1-shuf validation, phiên 2: s43 Devign #1126 → s44 Devign #2113 (gồm s43 ReVeal) | `thanhduy9a4tv/grace-b1-shuf-validation` (version 1) | 05/11 04:36 → 13:28 | W-val | `6279722d…48e4d7` (bản đẩy lên, `kaggle_staging_thanhduy/b1_shuf_run`) | output phiên tải ngày 07/11 (`Runs-management/check_b1_shuf_output`): s42, s43 4/4 khớp nguyên file; s44 Devign 2.113 dòng là tiền tố đúng |
| B1-shuf validation, phiên 3: s44 Devign #2114 → s44 ReVeal hết | `tomandjerry223/grace-b1-shuf-validation` | 07/11 00:43 → 04:47 | W-val | `8b0f76f7…c2c054` | checkpoint cuối chứa đủ 6/6 file s42–s44, khớp nguyên file |
| B2-nolabel validation | `tomandjerry223/grace-b2-nolabel-validation` | 04/11 09:55 → 18:39 | W-val | `aac49a43…af8270c` | checkpoint phiên, 2/2 |
| B2-labelonly validation | `thanhduy9a4tv/grace-b2-labelonly-validation` (version 2 hiện tại) | 04/11 16:12 → 23:40 | W-val | cell trùng `Runs-management/downloaded_executed_notebooks/02_kaggle_qwen_q4_b2_labelonly_validation_executed.ipynb` và commit `5413e05` | checkpoint và output đọc lại từ Kaggle ngày 15/11, 2/2 |
| B2-rep validation | `thanhduy9a4tv/grace-b2-rep-validation` (version 1 hiện tại) | 04/11 16:20 → 05/11 01:06 | W-val-rep | cell trùng `Runs-management/downloaded_executed_notebooks/02_kaggle_qwen_q4_b2_rep_validation_executed.ipynb` và commit `946a86b` | checkpoint và output đọc lại từ Kaggle ngày 15/11, 2/2 |
| B2-nolabel test | `tomandjerry223/grace-b2-nolabel-test` | 07/11 10:35 → 19:12 | W-test | `0d70ee5d…8d439b746` | final output và checkpoint, 2/2 |
| B2-labelonly test | `tomandjerry223/grace-b2-labelonly-test` | 07/11 10:36 → 17:58 | W-test | `2930dfcc…5e66c881` | final output và checkpoint, 2/2 |
| B2-rep test | `huuhieu3333/grace-b2-rep-test` (version 4 hiện tại) | 07/11 11:31 → 20:40 | W-test | `0efe3216…87356e2db` | final output và checkpoint, 2/2; output đọc lại từ Kaggle ngày 15/11 cũng khớp 2/2 |

Ghi chú:
- Ranh giới phiên của B1-shuf lấy từ các khoảng nghỉ > 10 phút giữa timestamp records liên tiếp; ba phiên cách nhau 0,5 giờ và 35,2 giờ.
- Phiên 2 chạy 05/11 04:15 → 13:29 và phiên 3 bắt đầu lúc 07/11 00:41, theo `events.log` của từng phiên. "2.113 record ngoài cửa sổ phiên" trong thư là phần do phiên 2 sinh ra.
- Kiểm thêm cho B1-shuf, chi tiết ở [README bằng chứng](../Runs-management/run_code_provenance_20261115/README.md):
  - `run_manifest` của cả ba phiên trùng bản chuẩn ở mọi trường ổn định. Ba phiên dùng cùng 6 bundle prompt.
  - `prompt_sha256` tính lại từ bundle trùng ở toàn bộ 15.015 records.
  - Mọi record có đúng khuôn trường do W-val ghi.
  - Khi resume, W-val kiểm `prompt_sha256`/`model_sha256` từng dòng checkpoint cũ và cấu hình `run_manifest`. Phiên 3 chạy hết, nên records của phiên 1 và 2 đã qua kiểm tra này.
- B2-rep test chạy trên `huuhieu3333`, đúng như thư ghi.

## 3. Giới hạn

- **Số version Kaggle chỉ lấy được bản mới nhất.** `kaggle kernels pull`/`output` chỉ trả bản mới nhất.
  - `tomandjerry223`: bản mới nhất của `grace-b2-nolabel-test` và `grace-b2-labelonly-test` tải ngày 15/11 trùng byte với bản lưu ngày 08/11.
  - `huuhieu3333/grace-b2-rep-test` đọc lại ngày 15/11:
    - Bản hiện tại là version 4. Cell source trùng bản 08/11 và chứa W-test.
    - Output hiện tại là của phiên 07/11 11:09 → 20:40 UTC theo `events.log`. `grace_b2_rep_test_final_output.zip` chứa records trùng byte với records chuẩn (2/2), worker trong output có SHA-256 `9a0e5c33…`.
    - Metadata ghi `lastRunTime` 12/11 06:58 UTC, nhưng output vẫn là của phiên 07/11.
  - `thanhduy9a4tv` đọc lại ngày 15/11 (token mới):
    - `grace-b2-labelonly-validation` (version 2) và `grace-b2-rep-validation` (version 1): cell source trùng bản executed notebook tải về trong `Runs-management/downloaded_executed_notebooks/` và trùng commit `5413e05` / `946a86b`; worker nằm nguyên văn trong cell. Output chứa worker `e8aecdce…` / `c418ea67…`, records trong output và checkpoint trùng byte với records chuẩn (2/2 mỗi arm), `events.log` từ 04/11 15:51 / 16:00 UTC.
    - Notebook trong `12_Arm_B2_LabelOnly/notebooks/` và `05_Arm_B2_Rep/notebooks/` ở bản hiện tại đã được sửa sau phiên chạy (thêm ghi chú package lock và cell runtime lock), nên không trùng cell với bản trên Kaggle; bản dùng để đối chiếu là executed notebook và commit nêu trên.
    - `grace-b1-shuf-validation` (version 2) là notebook một cell `pause.ipynb` (đẩy lên để dừng phiên 2, giữ quota GPU), output trống. Output gốc của phiên 2 không còn trên Kaggle; bằng chứng phiên 2 là bản notebook đẩy lên trong `kaggle_staging_thanhduy/b1_shuf_run` và checkpoint của phiên 3 kế thừa phần records phiên 2.
  - Cả ba kernel `thanhduy9a4tv` có `lastRunTime` 12/11 08:46 UTC, nhưng output của `grace-b2-*-validation` vẫn là phiên 04/11. Cùng hiện tượng với `huuhieu3333` (12/11 06:58); `lastRunTime` ngày 12/11 không ứng với phiên inference nào sinh records.
- **B1-shuf phiên 1:** notebook đúng version của phiên 1 không đọc lại được. Liên kết dựa trên checkpoint cuối phiên, `run_manifest`, `prompt_sha256` và kiểm resume của W-val ở phiên 3 (mục 2).
- **B1-shuf phiên 2:** output trên Kaggle đã bị version 2 (`pause.ipynb`) thay thế. Output phiên đã được tải về ngày 07/11 (`Runs-management/check_b1_shuf_output`), worker trong đó là bản CRLF của W-val.
- **Notebook trong thư mục arm:** `05_Arm_B2_Rep/notebooks/` và `12_Arm_B2_LabelOnly/notebooks/` đã được sửa sau phiên chạy. Bản dùng để đối chiếu là notebook đọc lại từ Kaggle, trùng executed notebook và commit `946a86b` / `5413e05`.
- **Native/build log:** chưa đối chiếu trong đợt này; trạng thái provenance runtime giữ như `runtime_session_reconciliation_20261110`.

## 4. Thư mục bằng chứng

- Bằng chứng đã gom vào [Runs-management/run_code_provenance_20261115/](../Runs-management/run_code_provenance_20261115/README.md), gồm:
  - worker, notebook từng phiên, `events.log`, metadata đọc lại từ Kaggle;
  - ba checkpoint của chuỗi B1-shuf;
  - SHA-256 các file lớn giữ ở local.
- Không chứa token hay cấu hình Kaggle.
- Script `verify_provenance.py` chạy lại toàn bộ kiểm tra: ngày 15/11 đạt 78/78 với bundle prompt B1-shuf, 72/72 khi không có bundle.
