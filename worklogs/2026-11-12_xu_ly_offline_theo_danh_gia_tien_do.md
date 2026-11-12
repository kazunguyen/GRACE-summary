# Xử lý offline theo Đánh giá tiến độ 11/11 — 12/11/2026

- Căn cứ: `docs/111126_response_v01/Danh_gia_tien_do_va_lo_trinh_GRACE_2026-11-11.docx` (Phương án 1) và kit `grace_diag_kit` v1.2 đi kèm. Bản đối chiếu tồn đọng trước khi xử lý: [2026-11-12_doi_chieu_danh_gia_tien_do_va_ton_dong.md](2026-11-12_doi_chieu_danh_gia_tien_do_va_ton_dong.md).
- Phạm vi:
  - Chỉ chạy CPU trên records đã có.
  - Không chọn lại ngưỡng nào.
  - Không sửa `configs/thresholds*.json`, `configs/arms.yaml`, data specs, hồ sơ OSF hay records.
- Các phân tích mới dùng lại loader, chỉ số bootstrap (5.000 lượt, seed 20261117) và hàm thống kê của `analysis_pa1_20261111/recompute.py`, nên dùng chung mẫu resample với `full_tables/contrasts.csv`.

## 1. Việc đã làm

| # | Việc | Thay đổi | Lý do (mục trong Đánh giá 11/11) | Kết quả chính |
|---|---|---|---|---|
| 1 | Đưa kit v1.2 vào repo | Thêm `import_records.py`, `compare_records.py`, `subset_metrics.py` vào `01_Author_Baseline_Unified/diagnostic_kit/scripts/`, trùng từng byte với zip của thầy. Không ghi đè module lõi đã tùy biến (`evaluate_final`, `thresholds`, `stats`...). | Mục 7 và Phụ lục B yêu cầu dùng các công cụ của kit v1.2. | Chạy được trên Windows với `python -X utf8` (in tiếng Việt). |
| 2 | Kiểm chứng B2-rep | `analysis_checks_20261112/compare_records/b2_vs_b2rep_{devign,reveal}.json` | Mục 2.2g | Điểm s trùng bit ở 100% ID; 0% đổi nhãn tại τ. Toàn bộ timestamp và elapsed khác B2 (chạy 07/11, còn B2 chạy 01–02/11). `repeat=true`, `tag="repeat"`. Đây là lời gọi mới, không phải cache. **Đóng mục.** |
| 3 | Chiều đổi dự đoán của B2-flip | `compare_records/b2_vs_b2flip_*.json` | Yêu cầu báo hướng đổi của độ nhạy nhãn | Devign: 554 mẫu đổi; đúng → sai 294, sai → đúng 260. ReVeal: 243 mẫu đổi; đúng → sai 100, sai → đúng 143. Tỷ lệ đổi 20,28% / 10,69%, khớp `sensitivity.csv`. |
| 4 | Kiểm tra trộn runtime B2-rand ReVeal | Đối chiếu với `runtime_session_reconciliation_20261110/REPORT.md` và quét `prompt_sha256` của 15.018 record | Mục 2.2f | 29 record chồng lấn chỉ thuộc seed 44, và cả hai bên đều dùng contract bảy package. Seed 42/43: **0 ID và 0 prompt** được chấm dưới cả hai runtime, nên không so điểm trực tiếp được. Theo đính chính của Dũng (mục 4 bên dưới), hai khóa chỉ khác pin SciPy 1.16.3, và seed 44 cho cùng kết luận AUROC. **Không cần chạy lại; so điểm trực tiếp chỉ còn là tùy chọn.** |
| 5 | Phân tầng B1-H2 theo evidence | `b1h2_evidence_strata/` (danh sách ID); `supplementary_tables/b1h2_evidence_strata.csv` | Mục 2.2d | Cờ evidence lấy từ `h2_evidence` trong `data/specs/*_test_15arms.jsonl`; hash khớp `test_specs_sha256` của delivery B1-H2. Thiếu evidence: Devign 1.798/2.732, ReVeal 1.866/2.274. ΔAUROC(B1-H2 − B1) nhóm có evidence: +0,031 [−0,004; 0,065] Devign, +0,061 [−0,009; 0,127] ReVeal; nhóm thiếu evidence: +0,002. Ngưỡng ReVeal dùng cho test là 0,21 (khóa validation Kaggle). 0,67 là ngưỡng của lượt validation Colab I-13 đã bị thay thế, không phải ghi chép lệch. |
| 6 | CI cho ΔAUPRC | `supplementary_contrasts.py` → `supplementary_tables/auprc_contrasts.csv` | Kit v1.2 coi AUROC/AUPRC là cơ sở kết luận về phân biệt | Devign: B2 − B0 = −0,030 [−0,049; −0,010]; B2 − labelonly = −0,028 [−0,047; −0,008]; B2 − B1 = −0,017 [−0,033; −0,001]. ReVeal: flip − B2 = −0,017 [−0,029; −0,006]. SUP-LR − B2 = +0,147 / +0,162. AUPRC không có biên đăng ký nên chỉ báo CI. |
| 7 | So trực tiếp B2 với B2-nolabel | `supplementary_tables/b2_vs_b2nolabel.csv` | Thiếu cặp này để đọc vai trò nhãn demo | Full test: mọi chỉ số có CI chứa 0. Tập sạch ReVeal: ΔAUROC −0,026 [−0,049; −0,001]. Kiểm tra chéo: ΔAUROC trùng với hiệu hai cặp tương ứng trong `contrasts.csv`. |
| 8 | Tỷ lệ đoán 1 tại cùng ngưỡng 0,5 | `supplementary_tables/ppr.csv` | Mục 2.2a | B1 → B2: 46,6% → 65,1% (Devign), 27,1% → 46,0% (ReVeal). B2-rand → B2: 50,5% → 65,1% và 31,7% → 46,0%. B3 − B2: −1,10 / +17,02 điểm (bản trước ghi −22,29 / +29,73, tính tại τ* khác nhau). |
| 9 | Tách điều kiện kết luận | `verdict_components.py` → `supplementary_tables/contrasts_verdict_components.csv` | Báo riêng điều kiện "cận dưới CI ≥ δ" | 16 hàng đạt "benefit" theo quy tắc đăng ký; chỉ 5 hàng có cận dưới ≥ δ (SUP-LR − B2 về AUROC; labelonly − B1 ReVeal tập sạch). |
| 10 | Bảng đối soát số liệu và inventory | `reconcile_inventory.py` → `reconciliation/` (`inventory.csv`, `b2_snapshot_drift.csv`, `drift_explanations.json`, `REPORT.md`) | Mục 2.2h; M1 "bảng đối soát" | 38 file records test đều đủ census, 100% điểm hợp lệ, 0 nhãn lệch; 36 file khớp bảng 1.3. B2-rand seed 44 chưa có trong bảng 1.3. Giải thích các số trôi: (1) MCC B2 0,044 → 0,060 vì bản 05/11 tính tại 0,5; (2) AUROC B2 Devign 0,5292 → 0,5305 vì bản 05/11 dùng file trước khi ghép donor rerun (38 prompt test); (3) 1.132 raw lỗi B0 là tổng bốn split. Liệt kê 6 bản records B1-full renderer cũ và 3 bản B2 trước rerun cần tránh. |
| 11 | Sửa báo cáo metric | Dũng tạo báo cáo mới [2026-11-12_bao_cao_metric_cac_arm_hoan_tat.md](2026-11-12_bao_cao_metric_cac_arm_hoan_tat.md) và giữ nguyên bản 07/11. Các chỉnh sửa trực tiếp trên bản 07/11 ở commit `65fa20e` **không** được đưa vào nhánh này. | Mục 2.2a; Phụ lục D (B3 thăm dò) | Báo cáo 12/11 đã đổi tỷ lệ đoán 1 sang 0,5, chuyển B3/H2.3 và B1-H2 sang phần thăm dò, và đưa vào các kết quả bổ sung ở trên. Đã kiểm trên `test_release_20261109_v1/kaggle_input`: B3 đã chạy chỉ có một cặp demo cố định cho mọi target. |
| 12 | Bảng sai lệch ba dòng | `analysis_checks_20261112/DEVIATIONS_TABLE.md` (D1–D12) | Phụ lục A; mục 7 | Bảng rút gọn để đưa vào bài; `CHANGES_AFTER_PREREG.md` giữ nguyên. |
| 13 | `recompute.py` chạy được trên Windows | `analysis_pa1_20261111/recompute.py`: kiểm tra hash chấp nhận bản chuẩn hóa LF; thêm `--step6-atol` (mặc định vẫn 1e-10) và in độ lệch. Thêm `requirements.txt` ghim scikit-learn 1.5.2, numpy 2.1.3, scipy 1.15.3. | Tái lập một lệnh; hai người đối soát độc lập | Với scikit-learn 1.5.2, Step 6 tái lập ở dung sai 1e-10; `contrasts.csv` và `sensitivity.csv` sinh lại **trùng từng ô** với bản đã push. Lệch khoảng 1e-3 trước đây là do môi trường local dùng scikit-learn 1.3.2. |

Kiểm thử trước khi commit: `tests/test_preregistration_integrity.py`, `diagnostic_kit/tests/test_probes.py`, `diagnostic_kit/tests/test_stats_and_complementarity.py`: 37 passed.

Tái lập:

```
pip install -r Runs-management/analysis_pa1_20261111/requirements.txt
python -X utf8 Runs-management/analysis_pa1_20261111/recompute.py --out <dir>
python -X utf8 Runs-management/analysis_checks_20261112/supplementary_contrasts.py --out Runs-management/analysis_checks_20261112/supplementary_tables
python -X utf8 Runs-management/analysis_checks_20261112/verdict_components.py --contrasts Runs-management/analysis_pa1_20261111/full_tables/contrasts.csv --out Runs-management/analysis_checks_20261112/supplementary_tables/contrasts_verdict_components.csv
python -X utf8 Runs-management/analysis_checks_20261112/reconcile_inventory.py --out Runs-management/analysis_checks_20261112/reconciliation
python -X utf8 01_Author_Baseline_Unified/diagnostic_kit/scripts/compare_records.py --a <B2 records> --b <B2-rep hoặc B2-flip records> --tau <0.70 | 0.12> --out <json>
```

## 2. Trạng thái so với Đánh giá 11/11

| Hạng mục | Trước | Sau |
|---|---|---|
| Bảng đối soát số liệu (2.2h) | ❌ | ✅ `reconciliation/REPORT.md` |
| compare_records B2 với B2-rep (2.2g) | ❌ | ✅ |
| B2-rand ReVeal trộn runtime (2.2f) | ❌ | ✅ Khóa chỉ khác pin SciPy; độ nhạy seed 44 cùng kết luận (Dũng). Không có ID chồng lấn để so điểm trực tiếp. |
| B1-full validation và renderer (2.2c) | ❌ | ✅ Validation khớp graph mới 5.005/5.005; không cần chạy lại (Dũng) |
| ppr@0.5 cho các cặp (2.2a) | ⚠️ | ✅ `ppr.csv`; đã vào báo cáo 12/11 |
| Phân tầng B1-H2 (2.2d) | ❌ | ✅ (thăm dò) |
| B3 khỏi phần xác nhận | ⚠️ | ✅ trong báo cáo 12/11 |
| Bảng sai lệch ba dòng (Phụ lục A) | ⚠️ | ✅ `DEVIATIONS_TABLE.md` |
| Kit v1.2 trong repo | ❌ | ✅ 3 script |
| Tái lập một lệnh, cross-platform | ⚠️ | ✅ với `requirements.txt` |

## 3. Tồn đọng

### Online

Không còn việc GPU bắt buộc.

- **Tùy chọn:** chạy lại một nhóm ID B2-rand ReVeal seed 42 dưới khóa mới để so điểm trực tiếp trên cùng ID và prompt. Chỉ làm nếu thầy yêu cầu; phải ghi vào báo cáo tuần trước khi chạy.
- **Bỏ:** chạy lại validation B1-full.

### Offline còn lại

1. **Chuỗi `import_records → thresholds --compare → evaluate_final` của kit v1.2 chưa chạy.** Lý do: module `evaluate_final`/`thresholds` trong repo đã tùy biến khác v1.2. Số liệu hiện dùng `recompute.py`, đã tái lập độc lập và khớp từng ô. Cần nhóm thống nhất có chạy chuỗi v1.2 song song không, hoặc ghi lý do trong Methods.
2. **File ngưỡng theo phiên bản** (`thresholds_corrected.json` có hash) chưa tạo. Bộ hiệu chỉnh B0/B1 hiện nằm trong `Runs-management/reanalysis_20261106/results.json`. Không ghi đè `configs/thresholds.json`.
3. **D7 trong bảng sai lệch:** nhóm cần bổ sung lý do B3-swap/B3-flip vẫn chạy ngày 11/11 sau quyết định dừng.
4. **Bảng metric test của báo cáo 12/11** chưa có dòng B2-rand seed 44 (mới có ở bảng ngưỡng và phân tích độ nhạy).
4b. **Log cài đặt SciPy** của B2-rand seed 42/43 (`kaggle_outputs_20261107/b2_rand_seed{42,43}_test_latest/grace_diagnostics/install_dependencies.log`) mà worklog của Dũng dẫn tới chưa có trên git; cần commit để kiểm độc lập.
4c. **Records validation của B0** bị `02_Arm_B0_Source_Only/.gitignore` chặn, nên `reconcile_inventory.py` bỏ qua phần đếm raw lỗi theo split trên bản checkout mới. Nếu muốn tái lập đầy đủ con số 1.132 thì cần force-add bốn file đó.
5. **Chiều đổi "theo nhãn demo" của B2-flip** chưa tính được vì records không lưu nhãn từng demo; cần join với spec nếu muốn báo.
6. **Rút gọn `CHANGES_AFTER_PREREG.md`** (khoảng 127k ký tự) và tách nhật ký vận hành: chưa làm. `DEVIATIONS_TABLE.md` là bản rút gọn cho bài.
7. **Người thứ hai đối soát** bảng `reconciliation/` và `supplementary_tables/` trước khi đưa số vào bản thảo.
8. **Báo cáo tuần** (thứ Hai, 1 trang) gồm mục D7 và trạng thái các việc online (đều không còn bắt buộc).
9. **File local chưa commit** (monitor của B3-swap, `.pytest_tmp_*`, chỗ thụt dòng trong `AUDIT_REPORT.md`, các bản B1-full renderer cũ trong `kaggle_status_*`): dọn trước khi đóng gói artifact.
10. **Viết bản thảo** theo K1–K5 cho mốc v1 ngày 26/11.

## 4. Đính chính theo phản hồi của Dũng (16:05 12/11)

Nguồn: [2026-11-12_chinh_sua_bao_cao_metric_grace.md](2026-11-12_chinh_sua_bao_cao_metric_grace.md). Nhánh này được tạo lại từ `baseline-unified` sau PR #36, thay cho nhánh `docs/offline-checks-20261112` (commit `65fa20e`).

| Điểm | Trước | Sau đính chính | Kiểm tra |
|---|---|---|---|
| B1-full | Đề xuất chạy lại validation vì renderer | Bỏ. 4.753/5.006 là chênh lệch giữa test cũ và test đã sửa; validation khớp graph mới. | `b1_full_corrected_v4/audit.json`: 0 graph mismatch trên 2.732 + 2.273 prompt validation. |
| B2-rand ReVeal | Đề xuất chạy lại ≥ 200 ID | Không cần chạy lại vì SciPy; seed 44 cho cùng kết luận. So điểm trực tiếp chỉ còn là tùy chọn. | Khóa mới pin `scipy==1.16.3`. Log cài đặt seed 42/43 chưa có trên git (mục 3, 4b). |
| B1-H2 ReVeal 0,67 | Gọi là "ghi chép lệch" | 0,67 là ngưỡng validation Colab I-13 đã bị thay; 0,21 là khóa Kaggle dùng cho test. | Theo `RUNS.md` (I-13) và `b1h2_kaggle_validation_threshold_lock_20261106.json`. |
| Báo cáo metric | Sửa trực tiếp bản 07/11 | Giữ nguyên bản 07/11; báo cáo 12/11 của Dũng là bản chính. | Nhánh này không chạm bản 07/11. |
| `reconcile_inventory.py` | Dừng lỗi khi thiếu records validation B0 | Bỏ qua và ghi `missing_untracked` cho file không có. | Records validation B0 bị `.gitignore` chặn. |

`DEVIATIONS_TABLE.md` đã sửa các mục D3, D4 và D5 tương ứng.
