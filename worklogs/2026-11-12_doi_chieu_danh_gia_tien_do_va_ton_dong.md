# Đối chiếu "Đánh giá tiến độ 11/11" với hiện trạng repo — tồn đọng và hướng xử lý

- Ngày lập: 12/11/2026
- Căn cứ:
  - `docs/111126_response_v01/Danh_gia_tien_do_va_lo_trinh_GRACE_2026-11-11.docx`
  - Đề cương hợp nhất Option 1
  - `grace_diag_kit.zip` v1.2. Ba file này trùng từng byte với `docs/20261111/`.
- Hiện trạng repo lấy tại commit `ec864df` (merge PR #34): `RUNS.md`, `CHANGES_AFTER_PREREG.md`, báo cáo metric `worklogs/2026-11-07_bao_cao_metric_cac_arm_hoan_tat.md` (bản cập nhật 11/11) và `Runs-management/analysis_pa1_20261111/`.
- Ký hiệu: ✅ đã đáp ứng · ⚠️ đáp ứng một phần hoặc lệch cách làm · ❌ chưa làm hoặc trái quyết định.

> **Cập nhật cùng ngày:** phần lớn việc offline của Đợt 1–2 đã xử lý. Trạng thái mới và tồn đọng còn lại ở [2026-11-12_xu_ly_offline_theo_danh_gia_tien_do.md](2026-11-12_xu_ly_offline_theo_danh_gia_tien_do.md).

---

## 1. Tóm tắt

- Phần **dữ liệu và số liệu** của M1 đã gần đủ:
  - B1-shuf có đủ 3 seed.
  - SUP-LR, SUP-MLP, SUP-METRIC có 3 seed.
  - Đã có P_pre/P_post, bảng sửa–hỏng có đối chứng.
  - Đã có CI ghép cặp, McNemar và Holm với hai bộ ngưỡng.
- Phần còn hở là **quy trình và kiểm chứng** mà bản đánh giá yêu cầu:
  - Chưa dùng chuỗi kit v1.2 (`import_records → thresholds → evaluate_final`).
  - Chưa có file ngưỡng theo phiên bản.
  - Chưa có bảng đối soát số liệu.
  - Chưa chạy `compare_records` cho B2-rep và B2-rand ReVeal.
  - Chưa phân tầng B1-H2.
- **Một điểm trái quyết định:** đánh giá yêu cầu dừng nhóm B3 và hủy B3-swap/B3-flip đang xếp hàng. Ngày 11/11 cả hai vẫn được chạy hoàn tất (I-29, I-30, I-31).
- Báo cáo metric còn **một số diễn giải chưa sửa theo mục 2.2**, và vẫn đặt B3 trong phần trả lời RQ chính.
- Mọi việc còn lại đều chạy bằng CPU. **Không cần thêm GPU**, trừ việc M2 tùy chọn là validation B1-full bằng renderer mới.

---

## 2. Đối chiếu hạng mục M1 / M2 / Giai đoạn 2

| # | Yêu cầu trong đánh giá | Hiện trạng | Mức |
|---|---|---|---|
| 1 | B1-shuf test seed 42 (M1); seed 43/44 (M2) | Đủ 15.018/15.018, cả 3 seed | ✅ |
| 2 | SUP-LR/SUP-MLP/SUP-METRIC, 3 seed, ngưỡng khóa trên validation | Báo cáo mục 1.4 | ✅ |
| 3 | P_pre/P_post; sửa–hỏng với đối chứng ALL-0/ALL-1/RANDOM; trần oracle | Báo cáo mục 0 và 1.5. Đã sửa cách nhóm file của ReVeal cho Step 6 (CHANGES 11/11) | ✅ |
| 4 | CI ghép cặp, McNemar, Holm cho mọi arm có test; **hai bộ ngưỡng** (đăng ký và hiệu chỉnh) | Có trong `analysis_pa1_20261111/full_tables/contrasts.csv` và `sensitivity.csv` | ✅ về số liệu |
| 5 | Số liệu sinh từ `import_records → thresholds → evaluate_final` của kit v1.2 (mục 7, Phụ lục B) | Tính bằng `recompute.py` riêng. Ba script `import_records.py`, `compare_records.py`, `subset_metrics.py` **chưa có trong repo**. Không có `import_manifest.json` | ⚠️ |
| 6 | Một file ngưỡng theo phiên bản (prereg / corrected) có hash; `thresholds --compare` in khác biệt | `configs/` chỉ có `thresholds.json` và `thresholds_flat.json`. Bộ ngưỡng hiệu chỉnh nằm rải rác trong báo cáo và nhật ký | ❌ |
| 7 | Bảng đối soát số liệu giữa các báo cáo (mục 2.2h): B2 MCC 0,044→0,060; AUROC 0,529→0,531; B0 raw invalid 1.132→302 | Chưa có | ❌ |
| 8 | `compare_records` B2 với B2-rep: s trùng bit, timestamp độc lập, elapsed > 0, `cache_tag = repeat` | Chưa có kết quả | ❌ |
| 9 | `compare_records` cho B2-rand ReVeal s42/43 (trộn hai runtime); nếu sai khác thì chạy lại phần thiểu số | Báo cáo vẫn ghi "giới hạn do trộn runtime"; chưa kiểm tra | ❌ |
| 10 | ppr@0.5 cho các cặp so sánh; viết lại RQ4 | Chỉ có B2 với B3 (báo cáo mục 4.2). Dòng RQ4 trong bảng tổng (dòng 370) vẫn dùng tỷ lệ tại τ* riêng (−22,29/+29,73 điểm) | ⚠️ |
| 11 | Quy tắc gap suy biến cho H2.2c | Đã áp dụng ở báo cáo mục 4.1 | ✅ |
| 12 | B1-H2: báo AUROC và phân tầng có/không evidence; xếp thăm dò; giải quyết mâu thuẫn ngưỡng 0,67/0,21 | Phân tầng chưa làm (báo cáo tự ghi "còn cần"); mâu thuẫn ngưỡng chưa thấy ghi là đã giải quyết | ❌ |
| 13 | B1-full: metric theo ngưỡng chỉ hợp lệ sau validation bằng renderer mới (M2) | Chưa chạy lại validation | ❌ (M2) |
| 14 | Dừng GPU cho B3 và B1-H2; hủy B3-swap/B3-flip đang xếp hàng | I-29/I-30 (B3-swap) và I-31 (B3-flip) chạy hoàn tất ngày 11/11 | ❌ trái quyết định |
| 15 | B3 và B1-H2 không có mặt trong Bảng B; ghi thăm dò | Báo cáo đặt B3 trong bảng trả lời RQ4/H2.3 chính; Holm 22 phép so gồm cả B2 với B3 và B1 với B1-H2 | ⚠️ |
| 16 | Phụ lục A: các mục sai lệch dạng 3 dòng | `CHANGES_AFTER_PREREG.md` có nhiều mục dài; chưa có bảng sai lệch gọn | ⚠️ |
| 17 | Rút gọn `CHANGES_AFTER_PREREG.md` thành bảng sai lệch; tách nhật ký vận hành | Tăng từ ~115k lên ~127k ký tự | ❌ |
| 18 | Hai người đối soát độc lập trước khi đưa số vào bản thảo | Đã tái lập độc lập `contrasts.csv`/`sensitivity.csv` bằng bản vá CRLF; chưa có biên bản của người thứ hai | ⚠️ |
| 19 | Báo cáo tuần 1 trang (thứ Hai) | Chưa thấy trong repo | ❓ |
| 20 | Routing (M2) | Có benefit-router của H3-B gate (mục 1.5) | ✅ |
| 21 | Chấm mù 30 ca (M3 / GĐ2) | Chưa | — (không bắt buộc trước 03/12) |

---

## 3. Vấn đề riêng về B3

### 3.1. Kiểm chứng nhận xét "một cặp mỗi dataset"

Kiểm tra trực tiếp đầu vào test của B3 bản mới tại `Runs-management/b3_verified_patch_v1/test_release_20261109_v1/kaggle_input/`:

| Dataset | Cặp trong `*_eligible_pairs.jsonl` | Số prompt test | Số cặp khác nhau được dùng |
|---|---:|---:|---:|
| Devign | 1 (`case_08_ffmpeg_can_safely_read_8614_26054`) | 2.732 | **1**, mọi target dùng cùng cặp |
| ReVeal | 1 (`case_reveal_curl_alloc_addbyter_16061_17887`) | 2.274 | **1**, mọi target dùng cùng cặp |

Nhận xét của thầy là **đúng**. B3 bản mới là "prompt có một ví dụ vá/chưa vá cố định" chứ không phải demo đối chứng được truy hồi theo từng target. Vì vậy so B3 với B2 không đo đúng điều H2.3 hỏi.

### 3.2. Cách xử lý

- Giữ toàn bộ records của B3, B3-nodiff, B3-swap và B3-flip. **Không chạy thêm.**
- Đưa mọi số B3 ra khỏi phần trả lời RQ chính và vào mục *Exploratory analyses*. Mỗi bảng ghi rõ: "một cặp demo cố định cho mỗi dataset; không phải arm truy hồi".
- Kết luận H2.3: **không có kết luận** ở phần xác nhận; nêu lý do trong Limitations; thiết kế lại ở Giai đoạn 2 theo mục 6 của đánh giá:
  - Kho cặp ≥ vài trăm cặp lấy từ PrimeVul hoặc Big-Vul.
  - Tiêu chí nghiệm thu đăng ký trước: câu mặc định ≤ 10%, cặp cùng nguồn ≥ 90%.
- Không diễn giải kết quả ReVeal B3 (ΔAUROC −0,037 [−0,065; −0,008]) là "demo đối chứng gây hại". Chỉ ghi là quan sát thăm dò.
- Ghi một mục sai lệch ba dòng: lượt B3-swap/B3-flip ngày 11/11 chạy sau quyết định dừng; được giữ ở mức thăm dò; không ảnh hưởng Bảng B.
- Báo thầy điều này trong báo cáo tuần.

### 3.3. Họ Holm

- Không bỏ B2 với B3 và B1 với B1-H2 ra khỏi họ 22 phép so đã đăng ký. Bỏ đi sẽ làm Holm bớt chặt, tức là điều chỉnh hồi cứu theo hướng có lợi.
- Giữ họ đăng ký (thận trọng hơn). Hai hàng này chỉ đánh dấu "thăm dò" và không trình bày trong Bảng B chính.
- Ghi một câu lý giải trong Methods.

---

## 4. Diễn giải còn phải sửa trong báo cáo metric

Đối chiếu với mục 2.2 của đánh giá:

| Vị trí | Vấn đề | Sửa |
|---|---|---|
| Bảng RQ, dòng RQ4 (≈ dòng 370) | Tỷ lệ đoán 1 "−22,29/+29,73 điểm" tính tại τ* khác nhau (B2 0,70 so với B3 0,99); đúng lỗi 2.2a | Dùng số tại 0,5 (−1,10/+17,02) và chuyển cả dòng sang phụ lục thăm dò |
| Mọi chỗ so tỷ lệ đoán 1 giữa B1, B2, B2-rand, B1-full | Cùng lỗi 2.2a nếu còn tính tại τ* riêng | Tính lại ppr@0.5 cho mọi cặp trong Bảng B |
| H1.1 (mục 4.4): "đạt cả hai biên trên hai dataset trong phân tích hồi cứu" | Đúng với bộ ngưỡng hiệu chỉnh. Với bộ đăng ký, ΔMCC Devign = +0,031 [−0,008; 0,068] chưa loại trừ lợi ích 0,03 | Viết song song hai bộ ngay trong câu kết luận; bộ đăng ký là chỉ định trước, bộ hiệu chỉnh là hồi cứu |
| Metric theo ngưỡng của B1-full | Ngưỡng 0,99/0,01 lấy từ validation dùng renderer cũ | Chỉ báo AUROC/AUPRC; MCC/F1 ghi "chờ validation renderer mới" |
| B1-H2 trong bảng RQ3/H3.1 | Thăm dò; 74% prompt không có evidence | Chuyển ra phụ lục; thêm phân tầng |
| B2-rand ReVeal | Trộn runtime | Ghi kết quả `compare_records` hoặc phần chạy lại |
| H4.1 "mọi arm gần ngẫu nhiên" | Thầy giữ H4.1 trong Option 1, nhưng mốc ngẫu nhiên là AUROC 0,5 | Viết "AUROC mọi arm ≤ 0,62 (mức đăng ký)" thay vì "gần ngẫu nhiên" |

---

## 5. Tồn đọng kỹ thuật ngoài văn bản đánh giá

Phát hiện khi tái lập `analysis_pa1_20261111`:

1. **`recompute.py` không tái lập được trên Windows.**
   - Hash đầu vào so trên byte thô nên bị vỡ do CRLF/autocrlf.
   - Kiểm tra metric Step 6 dùng dung sai 1e-10, trong khi sklearn khác phiên bản lệch tới khoảng 1e-3.
   - Cách sửa:
     - Thêm `.gitattributes` để giữ LF cho `*.jsonl`, `*.csv` và `*.json` đầu vào. Lưu ý giữ nguyên các file đã khóa.
     - Ghim phiên bản sklearn.
     - Nới dung sai riêng cho phần refit Step 6 và ghi rõ lý do.
2. **`contrasts.csv` chưa có AP/AUPRC.** Kit v1.2 coi AUROC/AUPRC là cơ sở kết luận về phân biệt, nên cần thêm CI cho ΔAUPRC.
3. **`sensitivity.csv` chưa có chiều đổi nhãn** (đúng→sai, sai→đúng, đổi theo nhãn demo). `compare_records` của kit tính sẵn các cột này.
4. **Thiếu cặp B2 với B2-nolabel trực tiếp.** Hiện chỉ có B2-nolabel với B1.
5. **Provenance một phần ở nhiều arm** (`PARTIAL_CORE_MATCH_NOT_FULL_LOCK`; `inference_seed`). Nêu trong Methods đúng mức "partial"; không dựng lại log hồi tố.
6. **File local chưa commit.**
   - Các file monitor và `rejected_*.json` của B3-swap, cùng các thư mục `.pytest_tmp_*`.
   - Một chỗ thụt dòng lỡ tay trong `independent_third_audit_20261108_143650/AUDIT_REPORT.md`.
   - Dọn hoặc `git restore` trước khi đóng gói artifact.

---

## 6. Kế hoạch xử lý đề xuất

Tất cả chỉ chạy CPU trên records đã có, không sửa các file đã khóa (`thresholds.json`, `arms.yaml`, data specs, hồ sơ OSF).

### Đợt 1 — kiểm chứng và đồng bộ quy trình (12–14/11)

| Việc | Lệnh / đầu ra | Đóng mục |
|---|---|---|
| Đưa 3 script của kit v1.2 vào repo | `scripts/import_records.py`, `compare_records.py`, `subset_metrics.py` | 5 |
| Gom records | `import_records --dry-run`, rồi chạy thật → `runs/final/` và `import_manifest.json`. Xử lý mọi xung đột, không dùng `--on-conflict` | 5, 9 |
| Sinh file ngưỡng hiệu chỉnh mới, **không ghi đè** `thresholds.json` | `thresholds --compare configs/thresholds.json` → `configs/thresholds_corrected.json` kèm sha256 | 6 |
| Chạy `evaluate_final` hai lần (prereg, corrected) | `runs/tables_prereg/`, `runs/tables_corrected/` có ppr@0.5 và AUPRC | 4, 10, 5.2 |
| Đối chiếu với `contrasts.csv` của PA1 | Bảng chênh lệch từng ô. Nếu khớp, đây là bằng chứng tái lập độc lập (mục 18) | 18 |
| Kiểm chứng B2-rep | `compare_records` B2 với B2-rep, τ 0,70 (Devign) và 0,12 (ReVeal) | 8 |
| Kiểm chứng B2-rand ReVeal | `compare_records` trên ID chồng lấn giữa hai runtime. Nếu không có chồng lấn, đề xuất chạy lại ≥ 200 ID phần thiểu số; lượt GPU này phải được ghi vào báo cáo tuần và chờ xác nhận | 9 |
| Chiều đổi nhãn của flip | `compare_records` B2 với B2-flip | 5.3 |
| Phân tầng B1-H2 | `subset_metrics --field <cờ evidence>`; giải quyết ngưỡng 0,67/0,21 | 12 |

### Đợt 2 — đối soát và hồ sơ (14–17/11)

| Việc | Đầu ra | Đóng mục |
|---|---|---|
| Bảng đối soát số liệu | Mỗi dòng (arm, dataset, split): hash records, N, valid, AUROC, nguồn từng số đã công bố, lý do khác nhau; giải thích 0,044→0,060, 0,529→0,531, 1.132→302 | 7 |
| Bảng sai lệch 3 dòng theo Phụ lục A | Thêm các mục B3-swap/B3-flip ngày 11/11 và B3 bản mới chỉ có một cặp | 16, 17, 14 |
| Rút gọn `CHANGES_AFTER_PREREG.md` | Bảng sai lệch cho bài; nhật ký vận hành dài chuyển sang file riêng (giữ nguyên nội dung lịch sử, chỉ tách) | 17 |
| Người thứ hai đối soát | Ký xác nhận trên bảng đối soát | 18 |
| Báo cáo tuần | 1 trang: số prompt, bảng đã sinh, ba việc tuần tới, vướng mắc (gồm B3) | 19 |
| Sửa portability của `recompute.py` | `.gitattributes`, ghim sklearn, dung sai Step 6 | 5.1 |

### Đợt 3 — sửa báo cáo và viết bản thảo (18–26/11)

- Sửa các diễn giải ở mục 4 và chuyển B3/B1-H2 sang phụ lục thăm dò (mục 3).
- Viết theo khung K1–K5. Mỗi RQ mở đầu bằng câu trả lời kèm số và CI:
  - **K1 (RQ1):**
    - B2 so với B0: ΔAUROC chứa 0 ở cả hai dataset.
    - ΔMCC đổi dấu theo bộ ngưỡng ở Devign; báo cả hai bộ.
    - MCC của B2 < 0,15; F1 Devign < ALL-1.
  - **K2 (RQ2):**
    - Độ nhạy nhãn ròng 20,3 điểm (Devign) và 10,7 điểm (ReVeal).
    - labelonly ≥ B2; có ý nghĩa thống kê trên ReVeal.
    - nolabel ≈ B1; rand ≈ B2.
  - **K3 (RQ3/RQ4):**
    - B1 ≈ B0 và B1 ≈ B1-shuf trên Devign; ReVeal chưa loại trừ khác biệt.
    - Viết lại RQ4 bằng ppr@0.5.
  - **K4 (RQ5):** SUP-LR vượt B2 về MCC (+0,16 / +0,19, CI không chứa 0); P_pre/P_post.
  - **K5:** thảo luận và hạn chế. Gồm B3 (một cặp cố định), B1-H2 (thiếu evidence), B1-full (renderer), provenance partial, trộn runtime B2-rand.
- Mốc: **bản thảo v1 ngày 26/11**; 25/11–03/12 không chạy gì mới; **nộp ngày 03/12**.

### Tùy chọn M2 (chỉ khi Đợt 1–2 xong và còn quota)

- Validation B1-full bằng renderer mới, khoảng 5.000 prompt GPU, rồi khóa lại ngưỡng và đánh giá lại. Phải ghi vào báo cáo tuần trước khi chạy.

---

## 7. Những việc không làm

Theo mục 7 của đánh giá và `AGENTS.md`:

- Không khởi tạo thêm arm hoặc phiên GPU ngoài M1/M2, nhất là B3 và B1-H2.
- Không chọn lại ngưỡng cho probe; không sửa `configs/thresholds.json`, `arms.yaml`, data specs hay hồ sơ OSF.
- Không chạy thêm để "cứu" một so sánh. Kết quả không có ý nghĩa thống kê vẫn được ghi và viết vào bài.
- Không ghép số từ workbook hoặc notebook. Mọi số trong bài phải truy được về records có hash.
- AI agent chỉ chạy các lệnh trong danh sách; không tự thay đổi thiết kế hay tạo hồ sơ quản trị mới.
