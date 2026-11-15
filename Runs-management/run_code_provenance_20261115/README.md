# Bằng chứng liên kết code → records (15/11/2026)

Bằng chứng cho [docs/REPLY_RUN_CODE_PROVENANCE_HIEU.md](../../docs/REPLY_RUN_CODE_PROVENANCE_HIEU.md): 20 nhóm records của B1-full, B1-shuf, B2-nolabel, B2-labelonly, B2-rep (validation và test). Không chứa token hay cấu hình Kaggle.

## Kiểm lại

```powershell
python Runs-management/run_code_provenance_20261115/verify_provenance.py
# nếu có bundle prompt B1-shuf ở local:
python Runs-management/run_code_provenance_20261115/verify_provenance.py --bundles <thư mục chứa 42_devign.zip ... 44_reveal.zip>
```

Kết quả ngày 15/11: 78/78 kiểm tra đạt với `--bundles`, 72/72 khi không có bundle. Records chuẩn: validation lấy từ `runs/final/`, test từ `Runs-management/run_handoff_20261108/completed_results/`.

Script kiểm:
- SHA-256 của ba worker (sau chuẩn hóa LF);
- mã nguồn worker nằm nguyên văn trong cell của notebook từng phiên;
- records trong output/checkpoint của từng phiên khớp byte records chuẩn;
- riêng B1-shuf: chuỗi ba phiên, `run_manifest`, khuôn trường record và `prompt_sha256`.

## Nội dung

| Thư mục / file | Nội dung |
|---|---|
| `workers/` | W-val `e8aecdce…`, W-val-rep `c418ea67…`, W-test `9a0e5c33…` (lấy từ output phiên Kaggle) |
| `tomandjerry223_validation_20261108/` | Notebook, `kernel-metadata.json`, `events.log` của B1-full, B1-shuf (phiên 3), B2-nolabel validation; tải ngày 08/11 (`runtime_audit_20261108`, không có trên git) |
| `kaggle_readback_20261115/` | Đọc lại từ Kaggle ngày 15/11: notebook bản hiện tại, metadata version, danh sách file output, `events.log`, `run_manifest` |
| `b1_shuf_chain/` | Checkpoint cuối phiên 1, 2, 3; notebook phiên 2 (`thanhduy9a4tv`); `events.log` phiên 2, 3; `bundle_manifest.json` của 6 bundle prompt |
| `local_only_files.json` | SHA-256 các file lớn giữ ở local (bundle prompt, output/checkpoint zip) và hash records bên trong |

- File `events.log` được đổi đuôi thành `events.log.txt` vì `.gitignore` bỏ qua `*.log`.
- Ba checkpoint B1-shuf (khoảng 6 MB) được thêm bằng `git add -f` vì `.gitignore` bỏ qua `*.zip`.

## Chuỗi B1-shuf validation

| Phiên | Kernel | Thời gian (UTC) | Kết thúc ở | Nguồn checkpoint cuối phiên |
|---|---|---|---|---|
| 1 | `tomandjerry223/grace-b1-shuf-validation` | 04/11 19:14 → 05/11 04:06 | s43 Devign #1125 | `kaggle_staging_thanhduy/dataset_b1_shuf` (dataset input của phiên 2) |
| 2 | `thanhduy9a4tv/grace-b1-shuf-validation` (version 1) | 05/11 04:15 → 13:29 | s44 Devign #2113 | `check_b1_shuf_output` (tải ngày 07/11, có trên git từ `005dabe` trừ zip) |
| 3 | `tomandjerry223/grace-b1-shuf-validation` | 07/11 00:41 → 04:47 | đủ 6/6 file | `runtime_audit_20261108/.../grace-b1-shuf-validation/output` |

Kết quả kiểm:
- Records cuối mỗi phiên là tiền tố đúng hoặc trùng nguyên file records chuẩn. Phần phiên sau nối tiếp đúng phần phiên trước.
- `run_manifest` của cả ba phiên trùng bản chuẩn ở mọi trường ổn định: model, llama-cpp-python, tokenizer, scoring, seed, ngân sách token. `prompt_set_sha256` trùng `prompts_sha256` của bundle. Ba phiên dùng cùng 6 bundle prompt.
- Tính lại SHA-256 từng prompt trong bundle: trùng `prompt_sha256` ở toàn bộ 15.015 records (lệch 0).
- Mọi record có đúng thứ tự trường do W-val ghi, một `model_sha256`, `arm = B1-shuf`, đúng seed.
- Khi resume, W-val kiểm `prompt_sha256` và `model_sha256` của từng dòng checkpoint cũ so với bundle, và từ chối chạy nếu `run_manifest` cũ khác cấu hình. Phiên 3 (W-val, notebook đã đối chiếu) chạy hết, tức mọi records của phiên 1 và 2 đã qua kiểm tra này.
- Worker của phiên 2: notebook phiên 2 chứa W-val. File `check_b1_shuf_output/kaggle_inference.py` (`169fefa7…`) là bản CRLF của W-val, diff sau chuẩn hóa LF rỗng.

Giới hạn:
- Không đọc lại được notebook đúng version của phiên 1, vì Kaggle API chỉ trả bản mới nhất.
- Output phiên 2 trên Kaggle đã bị version 2 (`pause.ipynb`) thay thế.
- Liên kết của hai phiên này dựa trên checkpoint, `run_manifest`, `prompt_sha256` và cơ chế kiểm khi resume của W-val như trên.
