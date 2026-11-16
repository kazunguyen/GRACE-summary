# Rà soát gói artifact Option1 ngày 16/11/2026

Trả lời thư nhờ rà gói `GRACE_artifact-packaging_2026-11-16.tar.gz` (Drive, bản review riêng tư). Đối chiếu ngày 16/11/2026 với nhánh `origin/dung` (`ccdee86`) và nhánh `docs/run-code-provenance-20261115`.

**Kiểm gói:** SHA-256 `af43cdf1c43ce93927f87ebdf9d39222286ada5618fe8e559a537af8290c8b18` khớp file `.sha256`. Archive có 1.257 file thường và 1.146 hard link (đủ 2.403 file), giải nén ra khoảng 14 GB. Đợt rà chỉ giải nén các file văn bản ≤ 3 MB, cùng `runs/final`, `runs/anchor`, `configs`, `analysis/analysis_code` và `runs/tables` của `Option1_Reproducibility_Package`.

## Tóm tắt

| Mục | Kết quả | Cần sửa |
|---|---|---|
| 1. B1-H2 I-16, B3 (nodiff, verified-patch, swap, flip) | Output, records, worker và notebook đủ cho cả 6 lượt (I-16, I-27…I-31). 10/10 dòng Table A addendum tính lại từ records khớp đến 4 chữ số. | Addendum thiếu các phép so phụ B3; thiếu file log offload của 3 lượt B3 (chỉ có hash). |
| 2. H2.3, H5.3 | H2.3 có số nhưng thiếu thành phần tỷ lệ dương đã đăng ký. **H5.3 trong addendum dùng P-PRE/P-POST, trong khi H5.3 đăng ký là tiêu chí routing**; Step 6 JSON đã tính đủ tiêu chí này. | Thêm dòng H5.3 routing và H2.3 tỷ lệ dương; ghi rõ Step 6 dùng B2 trước khi thay donor. |
| 3. Provenance B2 I-02/I-04/I-05; B0/I17 | **Worker đọc lại từ output Kaggle của cả ba phiên B2 đã có trên git từ 01/11** (`kaggle_qwen_q4_b2/downloaded_output_20261101*`). Bốn nhóm B2 nâng được lên cùng mức với 22 nhóm còn lại. | Cập nhật CSV/MD recheck. B0/I17 không có thêm bằng chứng từ phía Hiếu. |
| 4. Clean-environment, scaler | Kit đạt 32/32 test trong venv mới không kế thừa package hệ thống; bảng prereg và corrected dựng lại trong venv đó trùng byte 12/12 file số liệu. Scaler: không có scaler lưu riêng gắn với run inference. | GPU acceptance chưa làm (máy rà không có GPU). |

## 1. B1-H2 I-16 và các arm B3

### Evidence theo lượt (nhánh `origin/dung`)

| Lượt | Arm | Records test | Worker trong output | Nối với notebook |
|---|---|---|---|---|
| I-16 | B1-H2 | 2.732 + 2.274, ID không trùng | `kaggle_inference.py` `afb85a75…` | Nằm nguyên văn trong `11_Arm_B1H2_Evidence/kaggle_b1h2_test_20261106/02_kaggle_qwen_q4_b1_h2_test_20261106.ipynb` |
| I-27 | B3-nodiff | 2.732 + 2.274 | `kaggle_inference.py` `059c5fca…` | Worker lấy từ dataset input. `code_sha256` trong `inference_input_manifest.json` (đã niêm phong) và `runner_sha256` trong `runtime_provenance` đều là `059c5fca…`; notebook `14_Arm_B3_NoDiff/notebooks/03_…_test_runtime_locked_20261109.ipynb` kiểm hash này trước khi chạy |
| I-28 | B3 verified-patch | 2.732 + 2.274, không có nhãn trong output | `kaggle_inference_test.py` `e0bc63d7…` | Nhúng base64 trong `13_Arm_B3_Contrastive/notebooks/grace-b3-verified-patch-test-10h-ipynb.ipynb`; trùng `runner_sha256` |
| I-29 → I-30 | B3-swap | I-29: 2.732 + 1.865; I-30: 2.732 + 2.274 | `kaggle_inference_test.py` `7d21f95a…` | Nhúng base64 trong `15_Arm_B3_Swap/notebooks/b3-swap-test-latest-ipynb.ipynb`. ReVeal của I-29 là tiền tố đúng của I-30 |
| I-31 | B3-flip | 2.732 + 2.274 | `kaggle_inference_test.py` `7d21f95a…` | Nhúng base64 trong `16_Arm_B3_Flip/grace-b3-flip-test-20261110-v1.ipynb`; trùng `runner_sha256` |

Tất cả score nằm trong [0, 1] và mỗi lượt chỉ dùng một `model_sha256`.

### Table A addendum

Tính lại AUROC, AUPRC, MCC, BA, F1 và tỷ lệ dương tại ngưỡng khóa từ records (nhãn lấy từ records B2 chuẩn): **10/10 dòng khớp `table_A_exploratory_arms.csv`** đến 4 chữ số thập phân. Hiện addendum ghi "values transcribed from report"; có thể đổi thành "recomputed from records" kèm đường dẫn records.

### Còn thiếu

1. **Phép so phụ của B3.** Sổ đính chính yêu cầu giữ "contrast B2–B3 và các phép so phụ", nhưng `table_B_exploratory_contrasts.csv` chỉ có B2–B3 và B1–B1-H2. Báo cáo 12/11 §4.5 có B3-nodiff−B2, B3-swap−B3, B3-flip−B3 nhưng chỉ ở dạng ước lượng điểm.
   - Đã tính CI: [b3_secondary_contrasts.csv](../Runs-management/package_review_20261116/b3_secondary/b3_secondary_contrasts.csv), script [compute_b3_secondary.py](../Runs-management/package_review_20261116/b3_secondary/compute_b3_secondary.py).
   - Cách tính: `grace_diag.stats.paired_bootstrap`, 5.000 lượt, seed 20261117, cụm theo `runs/final/groups.csv`.
   - Kiểm chéo: dòng B3−B2 tái tạo đúng CI trong addendum; ước lượng điểm khớp báo cáo 12/11.

   | Phép so | Dataset | ΔAUROC [CI 95%] | ΔMCC tại ngưỡng khóa [CI 95%] | Δ tỷ lệ dương [CI 95%] |
   |---|---|---:|---:|---:|
   | B3-nodiff − B2 | Devign | +0,0054 [−0,0122; +0,0231] | −0,0067 [−0,0430; +0,0278] | −0,0615 [−0,0785; −0,0443] |
   | B3-nodiff − B2 | ReVeal | −0,0090 [−0,0331; +0,0164] | −0,0042 [−0,0392; +0,0312] | +0,0787 [+0,0594; +0,0980] |
   | B3-swap − B3 | Devign | −0,0023 [−0,0110; +0,0062] | −0,0007 [−0,0270; +0,0250] | −0,0176 [−0,0303; −0,0049] |
   | B3-swap − B3 | ReVeal | +0,0321 [+0,0143; +0,0491] | +0,0352 [−0,0003; +0,0708] | −0,1662 [−0,1855; −0,1466] |
   | B3-flip − B3 | Devign | +0,0038 [−0,0052; +0,0133] | +0,0145 [−0,0120; +0,0412] | −0,0608 [−0,0732; −0,0481] |
   | B3-flip − B3 | ReVeal | +0,0352 [+0,0193; +0,0507] | +0,0367 [−0,0001; +0,0737] | −0,1733 [−0,1932; −0,1530] |

   Các dòng này là exploratory, chưa hiệu chỉnh Holm và không thuộc họ 22 phép so.

2. **Log offload của I-27, I-28, I-31.** `runtime_provenance.json` có `offload_log_sha256`, nhưng file log chỉ có trong output I-29/I-30 (`model_load_offload.log`). RUNS.md ghi "offload 49/49" cho cả ba lượt. Nếu còn file log trong output Kaggle đã tải thì nên thêm vào gói; nếu không, ghi bằng chứng hiện có là hash log cùng VRAM trước/sau khi nạp model trên cả hai T4.

## 2. H2.3 và H5.3

Định nghĩa đăng ký lấy từ `preregistration.md` tại tag `prereg-v1`.

### H2.3

> B3 positive prediction rate is higher than B2 by ≥ 10 percentage points while upper bound of 95% CI for ΔAUROC(B3 − B2) < 0.02.

Addendum hiện có ΔAUROC và ΔMCC B3−B2 (theo margin trong `protocol.yaml`), chưa có thành phần tỷ lệ dương. Tính từ cùng records (B2 τ 0,70/0,12; B3 τ 0,99/0,01):

| Dataset | Δ tỷ lệ dương B3−B2 [CI 95%] | ΔAUROC B3−B2 [CI 95%] | Hai điều kiện đăng ký |
|---|---:|---:|---|
| Devign | −22,29 điểm % [−24,30; −20,33] | +0,0047 [−0,0135; +0,0228] | Không đạt cả hai (B3 đoán dương ít hơn; cận trên 0,0228 ≥ 0,02) |
| ReVeal | +29,73 điểm % [+27,18; +32,16] | −0,0369 [−0,0650; −0,0079] | Đạt cả hai |

Lý do giữ H2.3 ở mức exploratory (một cặp demo cố định cho mỗi dataset) là hợp lý và nên giữ. Đề xuất bổ sung hai dòng tỷ lệ dương này vào addendum, ghi rõ là mô tả theo tiêu chí đăng ký, không phải kết luận xác nhận.

### H5.3

> At expert call budget q=10%, Ridge Benefit Router does not outperform Confidence Router: Paired Bootstrap CI for ΔBA(benefit − confidence) and ΔMCC have upper bounds < δ = 0.02; additionally ΔBA(benefit − random) CI upper bound < 0.01; LLM error repairs do not exceed the 95th percentile of an equal-positive-rate random expert (20 seeds).

- `table_B_step6_H53.csv` trong addendum chỉ có P-PRE với P-POST theo MCC. So sánh này là thành phần "LLM không bổ sung tín hiệu sau truy vấn" của `protocol.yaml`, **không phải tiêu chí routing** trong văn bản đăng ký.
- `complementarity_step6.json` (lock `step6_lock_64fb2c99d904_42212811`) đã có khối `h5_3_registered_checks` với baseline chính `H3B_GATE`:

| Dataset | ΔBA benefit−confidence [CI] | ΔMCC benefit−confidence [CI] | ΔBA benefit−random [CI] | Repair LLM / khoảng random | Tất cả tiêu chí |
|---|---:|---:|---:|---|---|
| Devign | +0,0095 [−0,0010; +0,0199] ✓ | +0,0148 [−0,0062; +0,0357] ✗ | +0,0204 [+0,0138; +0,0270] ✗ | 397 / [411,3; 465,1] ✓ | **false** |
| ReVeal | −0,0644 [−0,0991; −0,0307] ✓ | −0,0509 [−0,1106; +0,0058] ✓ | −0,0487 [−0,0748; −0,0249] ✓ | 164 / [150,9; 176,2] ✓ | **true** |

Đề xuất cho addendum H5.3:
1. Đưa khối `h5_3_registered_checks` (H3B_GATE chính, SUP-LR bổ sung) làm các dòng H5.3 chính, giữ P-PRE/P-POST làm thành phần phụ.
2. **Ngưỡng repair:** code kiểm `llm_repairs_not_above_random_expert_97_5_percentile`, còn văn bản đăng ký ghi "95th percentile". Với ReVeal, 164 repair nằm dưới phân vị 97,5 (176,2) nhưng chưa chắc dưới phân vị 95. Cần tính lại phân vị 95 từ 20 seed random, hoặc ghi rõ độ lệch này trong `CHANGES_AFTER_PREREG.md`.
3. **B2 dùng trong Step 6 khác B2 chuẩn.** Cả hai lock Step 6 ghi `b2_source_root = 01_Author_Baseline_Unified/kaggle_qwen_q4_b2/downloaded_output_20261101_run3/grace_b2_four_split_8h`, tức records B2 trước khi thay 66 dòng donor (I-09).
   - Bảng A/B dùng `inference_qwen_q4_b2_frozen_donor_20261102`.
   - Ở Devign test có 38 record khác prompt (`|Δs|` trung bình 0,183), làm đổi 8 dự đoán tại τ = 0,70. Devign validation có thêm 28 dòng thay donor.
   - ReVeal không bị ảnh hưởng.
   - Cần chạy lại Step 6 Devign với B2 chuẩn, hoặc ghi rõ đây là deviation và ước lượng ảnh hưởng.
4. Hai lock Step 6 (`…_42212811` và `…_44f00d19`) cho kết quả trùng ở cả 985 trường JSON; chỉ khác `analysis_script_sha256`. Addendum dùng `42212811`, còn nhánh `dung` mới có `44f00d19`. Nên ghi rõ lock nào là chính.

## 3. Provenance B2 I-02/I-04/I-05; B0/I17

### Worker của ba phiên B2 đã có trên git

`RUN_SOURCE_BINDING_RECHECK_20261115` ghi "I02/I04 worker bytes missing; I05 only candidate". Tuy vậy, commit `31a37a3` (01/11 21:15 +07, khoảng 50 phút sau khi I-05 xong; có trên `dung` và `baseline-unified`) đã lưu output Kaggle tải về của từng phiên:

| Thư mục output tải về | `started_at` (trùng `run_history`) | Phiên | Worker trong output | Khuôn `run_manifest` |
|---|---|---|---|---|
| `01_Author_Baseline_Unified/kaggle_qwen_q4_b2/downloaded_output_20261101/` | 2026-10-31T17:05:34 | I-02 | `c4e5d888c8a8556593fb3b61c96583e68d8493b54b9b0ba9305f215ac5390ac2` | 16 trường, đúng bộ trường worker này ghi |
| `…/downloaded_output_20261101_retry1/` | 2026-11-01T01:41:44 | lần thử, 0 record mới | `d7dee7df…` | — |
| `…/downloaded_output_20261101_run2/` | 2026-11-01T02:12:23 | I-04 | `c901d1c34e031b4d593555fe559b82b531b5bb19375d115947d8b6b2666cabe7` | 17 trường (thêm `prompt_set_sha256`, `dataset`, `split`) |
| `…/downloaded_output_20261101_run3/` | 2026-11-01T11:06:51 | I-05 | `c901d1c3…` (trùng I-04) | 17 trường |

- Worker `c901d1c3…` nằm nguyên văn trong `01_Author_Baseline_Unified/notebooks/02_kaggle_qwen_q4_b2.ipynb` tại commit `31a37a3`. Như vậy hash "candidate" của I-05 cũng chính là worker trong output I-04/I-05.
- Hai bản `01_Author_Baseline_Unified/kaggle_inference.py` (`23aa0f9e…` tại `bc07fd4`, `a388f02d…` tại `31a37a3`) **không** phải bản đã chạy: identity của chúng không có `prompt_set_sha256`/`dataset`/`split`, và chúng đòi `run_manifest` trùng tuyệt đối, trong khi `bundle_sha256` đổi giữa các phiên.
- Records của từng output là tiền tố đúng của records hợp nhất bốn split. Hai checkpoint `grace_b2_checkpoint_I02_partial.zip` và `…_I04_partial.zip` cũng vậy.
- Worker I-04/I-05 bỏ qua `bundle_sha256` khi resume nhưng kiểm `prompt_sha256` và `model_sha256` của từng dòng checkpoint cũ.
- B2 test chuẩn bằng records I-02/I-04/I-05 trừ 38 dòng Devign donor chạy lại (02/11 00:13 → 00:16 UTC, I-09); ReVeal test không thay dòng nào.

Script kiểm: [verify_b2_session_chain.py](../Runs-management/package_review_20261116/verify_b2_session_chain.py), chạy từ gốc repo, **38/38 đạt**. Script chỉ dùng file đã có trên git. Chưa kiểm được 28 dòng donor ở Devign validation, vì `frozen_donor_20261102/*/validation` chỉ có ở máy Dũng.

Đề xuất: bốn nhóm B2 chuyển từ "partial" sang "output worker file plus session trail", cùng mức với 22 nhóm còn lại. Ghi kèm phân đoạn: Devign validation I-02 2.704 + I-09 28; Devign test I-04 2.694 + I-09 38; ReVeal validation I-02 1.664 + I-04 609; ReVeal test I-04 977 + I-05 1.297.

### B0 và I17

Hai nhóm này chạy trên `duchuynguyen1802`; nhánh của Hiếu không có thêm bằng chứng. Caveat drift giữa notebook và output trong CSV recheck giữ nguyên.

### Cập nhật nhánh provenance 20 nhóm của Hiếu

Theo các giới hạn ghi trong `2026-11-15_hieu_code_provenance_branch_audit.md`:
- `verify_provenance.py` nay chạy trực tiếp trên `runs/final` mới: bỏ trường `group` rồi ghi lại record đúng cách worker ghi; khi thiếu `run_manifest.json` thì lấy manifest của checkpoint cuối làm mốc. Kết quả **78/78** trên `runs/final` của gói Option1.
- Sáu bundle prompt B1-shuf (14 MB) đã đưa vào `Runs-management/run_code_provenance_20261115/b1_shuf_chain/prompt_bundles/`; SHA-256 trùng `local_only_files.json`. Script tự dùng thư mục này, nên chạy được đủ sáu kiểm tra prompt hash.

## 4. Clean-environment, GPU acceptance, scaler

### Clean-environment

Venv mới tạo bằng `python -m venv` không có `--system-site-packages`; Python 3.10.11, Windows 10.0.26200. Chi tiết trong [clean_env_20261116/](../Runs-management/package_review_20261116/clean_env_20261116/).

1. `pip install -e ".[test]"` từ bản sao `grace_diag_kit/` của gói. pip cài numpy 2.2.6, scipy 1.15.3, scikit-learn 1.7.2, PyYAML 6.0.3, openai 3.51.0, pytest 9.2.0 (`pip_freeze_kit_tests.txt`).
2. `python -m pytest -p no:cacheprovider tests`: **32 passed**.
3. Thêm `matplotlib` 3.10.9 (extra `figures`), rồi chạy `analysis/analysis_code/evaluate_final_cached_bootstrap.py` với `configs/protocol.yaml` và từng file ngưỡng `thresholds.prereg.json` / `thresholds_corrected.json`.
   - **12/12 file số liệu trùng byte** với `runs/tables/tables_prereg` và `tables_corrected`: CSV, TeX, `table_C_sensitivity.csv`, `thresholds_used.json`.
   - Tám file PNG khác hash nhưng **trùng từng pixel**; phần khác là metadata phiên bản Matplotlib nhúng trong PNG.
   - Bảng đối chiếu: `table_rebuild_comparison.csv`.

Phạm vi: đây là cài đặt sạch trên một máy Windows, chưa phải máy mới hoàn toàn hay Linux. Phiên bản numpy/scipy khác bản 15/11 (1.26.4) mà số liệu vẫn trùng byte.

### GPU acceptance

Chưa làm được: máy rà không có GPU. Phía Hiếu không có kết quả chạy GPU mới ngoài các phiên lịch sử đã liệt kê.

### Scaler

- **Inference LLM:** không dùng scaler; score là `sigmoid(logit_1 − logit_0)` từ logits.
- **Step 6** (`STEP6_supervised_anchors/src/step6_complementarity.py`; kit `complementarity.py`, `supervised_anchor.py`):
  - `StandardScaler` chỉ nằm trong `make_pipeline` và được fit lại ở từng fold (P-PRE, P-POST, router Ridge, SUP-LR, SUP-MLP).
  - Không có file scaler nào được lưu; JSON ghi `"scaler": "StandardScaler", "same_fold_assignments": true`.
  - Có thể ghi "not applicable as a separate artifact", căn cứ là `analysis_script_sha256`, phiên bản scikit-learn trong `runtime_versions` và seed.
- **H3B_GATE** (`export_locked_h3b.py`):
  - Các view được fit rồi lưu cache `fit_models/<dataset>/<fingerprint>.joblib`, kèm manifest JSON có SHA-256.
  - Các file cache này không có trong gói, và `h3b_export_manifest.json` không liệt kê hash của chúng.
  - Nếu Step 9 coi model fit là artifact, nên thêm các manifest `fit_models/*.json` (SHA-256 và fingerprint) vào gói, hoặc ghi rõ đây là cache tái tạo được từ fingerprint đầu vào.

## File thay đổi trong nhánh

- `docs/REVIEW_OPTION1_PACKAGE_20261116.md`: file này.
- `Runs-management/package_review_20261116/`:
  - `verify_b2_session_chain.py`;
  - `b3_secondary/` (CSV và script);
  - `clean_env_20261116/` (pip freeze, nền tảng, bảng đối chiếu dựng lại bảng).
- `Runs-management/run_code_provenance_20261115/`: `verify_provenance.py` (đọc được `runs/final` mới), `README.md`, `b1_shuf_chain/prompt_bundles/` (6 zip).
- `worklogs/2026-11-16_ra_soat_goi_option1.md`.
