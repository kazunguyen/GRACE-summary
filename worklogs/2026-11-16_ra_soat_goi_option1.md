# Rà soát gói artifact Option1 (16/11/2026)

Rà gói `GRACE_artifact-packaging_2026-11-16.tar.gz` theo bốn điểm Dũng nhờ. Chi tiết, bảng số và đường dẫn ở [REVIEW_OPTION1_PACKAGE_20261116.md](../docs/REVIEW_OPTION1_PACKAGE_20261116.md).

## Đã làm

- Tải archive từ Drive (chỉ đọc). SHA-256 `af43cdf1…8b18` khớp; 1.257 file thường cộng 1.146 hard link, đủ 2.403 file. Chỉ giải nén phần văn bản, records, configs và bảng.
- **B1-H2 I-16 và B3 I-27…I-31:**
  - Đủ output, records và worker cho cả sáu lượt.
  - Worker nối với notebook: nguyên văn với B1-H2; base64 với B3 verified-patch, swap và flip; `code_sha256` trong manifest niêm phong với B3-nodiff. Worker cũng trùng `runner_sha256` trong `runtime_provenance`.
  - Tính lại 10 dòng Table A addendum từ records: khớp 10/10.
- **Phép so phụ B3:** tính CI cho B3-nodiff−B2, B3-swap−B3 và B3-flip−B3 (5.000 lượt bootstrap cụm, seed 20261117). Dòng B3−B2 tái tạo đúng CI trong addendum. Kết quả ở `Runs-management/package_review_20261116/b3_secondary/`.
- **H2.3 và H5.3:** đối chiếu với `preregistration.md` tại tag `prereg-v1`.
  - H2.3 thiếu thành phần tỷ lệ dương. Đã tính: Devign −22,3 điểm %, ReVeal +29,7 điểm %.
  - H5.3 trong addendum dùng P-PRE/P-POST, trong khi H5.3 đăng ký là tiêu chí routing. Step 6 JSON đã tính đủ tiêu chí routing: Devign không đạt tất cả, ReVeal đạt tất cả.
- **Provenance B2:**
  - Tìm thấy worker đọc lại từ output Kaggle của I-02 (`c4e5d888…`), I-04 và I-05 (`c901d1c3…`) trong `01_Author_Baseline_Unified/kaggle_qwen_q4_b2/downloaded_output_20261101*`, có trên git từ commit `31a37a3`.
  - Viết `verify_b2_session_chain.py`: 38/38 kiểm tra đạt.
- **Nhánh provenance 20 nhóm:**
  - Sửa `verify_provenance.py` để chạy được trên `runs/final` mới (có trường `group`, không còn `run_manifest.json`).
  - Thêm sáu bundle prompt B1-shuf.
  - Kết quả 78/78 trên `runs/final` của gói Option1.
- **Clean-environment:**
  - Venv mới, không kế thừa package hệ thống, Python 3.10.11: kit đạt 32/32 test.
  - Dựng lại bảng prereg và corrected: 12/12 file số liệu trùng byte. Tám PNG trùng pixel, chỉ khác metadata Matplotlib.
- **Scaler:** inference LLM không dùng scaler. Step 6 fit `StandardScaler` trong pipeline theo từng fold, không lưu file. H3B_GATE có cache model `.joblib` kèm manifest hash, nhưng không có trong gói.

## Lưu ý

- Step 6 (cả hai lock) dùng B2 từ `downloaded_output_20261101_run3`, tức trước khi thay 66 dòng donor. Devign test có 38 record khác prompt so với B2 chuẩn của Bảng A/B, làm đổi 8 dự đoán tại τ = 0,70. ReVeal không bị ảnh hưởng.
- Code H5.3 kiểm repair theo phân vị 97,5, còn văn bản đăng ký ghi phân vị 95.
- Ba lượt B3 (I-27, I-28, I-31) chỉ có hash log offload, không có file log.
- Chưa kiểm được 28 dòng donor ở Devign validation vì `frozen_donor_20261102/*/validation` chỉ có ở máy Dũng.

## Còn cần

- Dũng quyết định cách xử lý Step 6 B2: chạy lại Devign với B2 chuẩn, hoặc ghi deviation.
- Cập nhật addendum (H5.3 routing, H2.3 tỷ lệ dương, phép so phụ B3) và CSV recheck provenance B2 trong gói.
- GPU acceptance (cần máy có GPU) và rà quyền/sanitization trước khi phát hành.
