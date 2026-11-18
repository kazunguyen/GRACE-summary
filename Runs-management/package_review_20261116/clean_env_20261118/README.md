# Clean-environment Python 3.10.11: kit tests và dựng lại bảng Option1 (18/11/2026)

Chạy phần A của `REPRODUCTION_RUNBOOK.md` trong gói `GRACE_artifact-packaging_2026-11-16.tar.gz` (SHA-256 `af43cdf1…8b18`), trên venv mới tạo bằng Python 3.10.11. Lượt này bổ sung bằng chứng cho lượt 18/11 trên Python 3.11.0. Không chạy inference hay GPU.

## Kết quả

| Bước | Kết quả |
|---|---|
| File giải nén so với `MANIFEST_SHA256.json` (manifest sha256 `27bf16b6…`) | 345 file đã giải nén khớp, 0 lệch. 915 file thuộc `data/`, `source/`, `supplementary/`, `provenance/` không giải nén vì phần A không dùng |
| Venv | `include-system-site-packages = false`, `ENABLE_USER_SITE = False`. Venv rỗng chỉ có pip 23.0.1 và setuptools 65.5.0 |
| Cài đặt theo runbook | Nâng pip lên 26.3. `pip install -e .\grace_diag_kit`, `pip install matplotlib pytest`. `pip check`: không có lỗi phụ thuộc |
| Test kit | **32/32 passed** (19,1 giây) |
| Dựng lại `tables_prereg` | exit 0, 26 phút. Sampler identity check PASS, 5.000 lượt bootstrap đọc từ protocol |
| Dựng lại `tables_corrected` | exit 0, 1,5 phút |
| So với `runs/tables/` của gói | Mỗi bộ: **6/6 file số liệu trùng byte** (3 CSV, 2 TeX, `thresholds_used.json`) và **4/4 PNG trùng pixel**. Tổng hai bộ: 12/12 trùng byte, 8/8 trùng pixel |

PNG không trùng byte vì metadata `Software` khác nhau: bản lưu ghi Matplotlib 3.10.1, bản dựng lại ghi Matplotlib 3.10.9. Runbook không ghim phiên bản Matplotlib, nên pip cài bản mới nhất. Muốn PNG trùng byte thì cài `matplotlib==3.10.1`.

Ba file chỉ có trong bản lưu (`README.md`, `evaluate_final.log`, `2026-11-13_evaluate_final.log`) là ghi chú của lần chạy cũ, evaluator không sinh ra. Bước 19 đánh dấu nhầm ba file này là DIFF (exit 1). Bước 20 chạy lại phép so sánh sau khi phân loại chúng là ghi chú lần chạy (exit 0). Log của cả hai bước đều được giữ nguyên.

## Môi trường

- Windows 11 (`Microsoft Windows [Version 10.0.26200.9974]`, `platform`: Windows-10-10.0.26200-SP0), AMD64, Intel64 Family 6 Model 186.
- Python 3.10.11 (tags/v3.10.11:7d4cc5a, Apr 5 2023) [MSC v.1929 64 bit (AMD64)].
- Phụ thuộc chính: numpy 2.2.6, scipy 1.15.3, scikit-learn 1.7.2, matplotlib 3.10.9, pillow 12.3.0, PyYAML 6.0.3, pytest 9.2.0. Danh sách đầy đủ ở `logs/13_pip_freeze_after_install.stdout.txt` và `logs/14_pip_list_json.stdout.txt`.

## Khác với runbook

- Runbook kích hoạt venv bằng `Activate.ps1`. Lượt này gọi thẳng `.venv-repro\Scripts\python.exe`, với các biến `PYTHON*`, `PIP_*`, `CONDA*`, `VIRTUAL_ENV` bị xóa khỏi môi trường và `PYTHONNOUSERSITE=1`.
- Bảng dựng lại được ghi vào `runs/reproduced_20261118_py31011/` của bản giải nén, không ghi đè `runs/tables/`.

## Nội dung thư mục

- `commands.jsonl`: mỗi bước một dòng, gồm argv (đường dẫn rút gọn thành `<PKG>`, `<TOOLS>`, `<EV>`), giờ bắt đầu/kết thúc UTC, exit code, SHA-256 của stdout và stderr.
- `logs/NN_<bước>.stdout.txt`, `logs/NN_<bước>.stderr.txt`: stdout/stderr nguyên văn của 20 bước.
- `manifest_check.json`: đối chiếu file đã giải nén với manifest của gói.
- `table_comparison.csv`: từng file gồm SHA-256 bản lưu/bản dựng lại, trùng byte, trùng pixel, kích thước ảnh, metadata Software của PNG.
- `rebuilt/tables_prereg/`, `rebuilt/tables_corrected/`: 10 file mỗi bộ, gồm cả 8 PNG.
- `tools/`: `run_clean_env.py` (bước 1–19), `verify_manifest.py`, `compare_tables.py`, `rerun_compare.py` (bước 20).

Chạy lại:

```
python -I tools/run_clean_env.py <gốc gói Option1> <python 3.10.11> <thư mục bằng chứng mới> <thư mục tools>
python -I tools/rerun_compare.py <gốc gói Option1> <thư mục bằng chứng> <thư mục tools>
```
