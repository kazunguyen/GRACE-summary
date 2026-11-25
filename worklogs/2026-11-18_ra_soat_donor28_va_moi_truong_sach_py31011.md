# Rà soát 28 dòng donor B2 và chạy lại môi trường sạch Python 3.10.11 (18/11/2026)

Tiếp nối [rà soát gói Option1 ngày 16/11](2026-11-16_ra_soat_goi_option1.md). Commit `d0c1c66`. Worklog này được bổ sung ngày 25/11; bằng chứng gốc nằm trong hai README dưới đây và không thay đổi.

## Đã làm

- **Donor-28** ([README](../Runs-management/package_review_20261116/donor28/README.md)):
  - Kiểm 28 dòng B2 / Devign / validation / seed 42 được chạy lại sau khi đổi donor, theo phiếu Dũng gửi (`docs/hieu_review_28_devign_validation.csv`). Phiếu đã điền: `hieu_review_28_devign_validation_filled.csv`.
  - Kết quả **28/28 PASS**, 0 FAIL, 0 UNVERIFIABLE; đạt 19/19 kiểm tra cấp file.
  - Đối chiếu donor cũ/mới, prompt cũ/mới, score tính lại từ logprob, quyết định tại τ = 0,70: đổi score 28/28, đổi quyết định 6/28, đổi argmax 3/28, đúng như phiếu.
  - Khóa lại ngưỡng trên validation chuẩn: τ vẫn 0,70 (MCC 0,054734); score cũ cũng cho τ = 0,70, nên đổi donor không làm dời ngưỡng.
  - Script: `verify_donor28.py`, chỉ đọc nguồn gốc, không dùng script dựng phiếu của Dũng.
- **Môi trường sạch Python 3.10.11** ([README](../Runs-management/package_review_20261116/clean_env_20261118/README.md)):
  - Chạy phần A của `REPRODUCTION_RUNBOOK.md` trong gói Option1 (SHA-256 `af43cdf1…8b18`), venv mới không kế thừa package hệ thống.
  - 345 file giải nén khớp manifest. Test kit **32/32 passed**.
  - Dựng lại `tables_prereg` và `tables_corrected`: **12/12 file số liệu trùng byte**, **8/8 PNG trùng pixel**.
  - Log 20 bước, lệnh và hash stdout/stderr lưu trong `commands.jsonl` và `logs/`.

## Lưu ý

- PNG không trùng byte vì metadata Matplotlib (3.10.1 trong gói, 3.10.9 khi dựng lại). Runbook không ghim Matplotlib; muốn trùng byte thì cài `matplotlib==3.10.1`.
- `devign_old_bank.jsonl` chỉ có ở máy Dũng (thư mục cache bị `.gitignore`); donor cũ được kiểm qua `specs.jsonl` legacy.
- Trên Windows, checkout đổi CRLF làm lệch hash; script băm blob git (LF).
- 5/28 donor cũ không còn trong kho mới; 13/28 dòng có nhãn donor mới khác nhãn donor cũ.

## Còn cần

- Đề xuất ghim `matplotlib==3.10.1` trong runbook của gói.
- Kết quả donor-28 được dùng tiếp trong việc chạy lại Step 6 ngày 25/11 ([worklog](2026-11-25_gom_nhanh_va_chay_lai_step6_b2_chuan.md)).
