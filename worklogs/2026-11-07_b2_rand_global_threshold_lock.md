# B2-rand: khóa ngưỡng vào config tổng — 07/11/2026

## Thay đổi

Đã đưa các ngưỡng validation B2-rand cho hai prompt seed hoàn tất vào `configs/thresholds.json`, là config khóa ngưỡng tổng của dự án. Trước đó, các giá trị chỉ được lưu trong `06_Arm_B2_Rand/config/threshold.json`; config tổng chưa có các khóa này.

| Prompt seed | Dataset | Tau | MCC validation | Hợp lệ |
|---:|---|---:|---:|---:|
| 42 | Devign | 0.99 | 0.06620373237126373 | 2.732/2.732 |
| 42 | REVEAL | 0.89 | 0.08081883313753434 | 2.273/2.273 |
| 43 | Devign | 0.99 | 0.061035892718704646 | 2.732/2.732 |
| 43 | REVEAL | 0.62 | 0.07706375271838951 | 2.273/2.273 |

Các tau được chọn trên grid 0,01–0,99 theo MCC của score validation hợp lệ, với quy tắc tie-break ghi trong hồ sơ arm. Không dùng test records hoặc test metrics để chọn ngưỡng. `seed` trong khóa là prompt seed; `inference_seed=4294967295` là giá trị mặc định của llama.cpp và được ghi riêng trong chi tiết khóa.

## Đồng bộ và xác minh

- Thêm bốn keys `devign|B2-rand|42`, `reveal|B2-rand|42`, `devign|B2-rand|43`, `reveal|B2-rand|43` vào `configs/thresholds.json` và `configs/thresholds_flat.json`.
- Đồng bộ hai file đó vào `01_Author_Baseline_Unified/diagnostic_kit/configs/`.
- Thêm grid, hash records, bundle, prompt set, model/backend/runtime và bằng chứng validation vào `Runs-management/thresholds.json`.
- Đối chiếu SHA-256 của bốn `records.jsonl` với hồ sơ khóa của arm trước khi ghi. Mỗi tập đủ mẫu và không có score-invalid.
- Giữ nguyên 16 tau cũ; tổng hiện có 20 khóa. Tự xác thực `locked_sha256` thành công: `269ebf781c026d2002b4577769c112d4d5ad7d04795782fed2b435b9f3902e4f`.

## Nguồn

- Hồ sơ khóa đầy đủ, gồm MCC theo từng điểm grid: [`06_Arm_B2_Rand/config/threshold.json`](../06_Arm_B2_Rand/config/threshold.json).
- Output validation I-15: [`Runs-management/kaggle_outputs_20261107/b2_rand_latest/`](../Runs-management/kaggle_outputs_20261107/b2_rand_latest/).
- Bảng trạng thái runs: [`Runs-management/RUNS.md`](../Runs-management/RUNS.md).
