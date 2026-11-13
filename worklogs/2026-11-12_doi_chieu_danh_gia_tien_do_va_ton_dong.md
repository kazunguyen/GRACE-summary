# Đối chiếu "Đánh giá tiến độ 11/11" với hiện trạng repo — tồn đọng và hướng xử lý

- Ngày lập và cập nhật: 12/11/2026.
- Căn cứ: Phụ lục A của Option 1 ngày 11/11, [báo cáo metric 12/11](2026-11-12_bao_cao_metric_cac_arm_hoan_tat.md), [worklog đính chính](2026-11-12_chinh_sua_bao_cao_metric_grace.md), sổ chạy và nhật ký thay đổi sau đăng ký.
- Ký hiệu: ✅ đã đáp ứng · ⚠️ đáp ứng một phần · ❌ chưa làm hoặc trái quyết định.

> **Cập nhật cùng ngày:** phần lớn việc offline của Đợt 1–2 đã xử lý. Trạng thái mới và tồn đọng còn lại ở [2026-11-12_xu_ly_offline_theo_danh_gia_tien_do.md](2026-11-12_xu_ly_offline_theo_danh_gia_tien_do.md).

---

## 1. Tóm tắt

- Đã có số liệu M1, gồm B1-shuf ba seed, các mốc SUP, cặp P_pre/P_post, bảng sửa–hỏng có đối chứng và các phép so ghép cặp theo hai bộ ngưỡng.
- Báo cáo đã bổ sung đối soát số cũ, kiểm tra B2-rep/B2-flip, ppr tại 0,5, CI ΔAUPRC, phép so trực tiếp B2−B2-nolabel và phân tầng B1-H2. Đính chính B1-full rút đề xuất chạy lại validation vì renderer.
- Còn mở file ngưỡng hiệu chỉnh tổng hợp có hash, lượt đánh giá đầy đủ theo kit v1.2, bảng sai lệch gọn trong `CHANGES_AFTER_PREREG.md` và đối soát độc lập trước khi đưa số vào bản thảo.
- B3-swap và B3-flip vẫn chạy ngày 11/11 sau quyết định dừng. Báo cáo đã ghi các kết quả này ở mức thăm dò.

---

## 2. Đối chiếu hạng mục M1 / M2 / Giai đoạn 2

| # | Yêu cầu trong đánh giá | Hiện trạng | Mức |
|---|---|---|---|
| 1 | B1-shuf test seed 42 (M1); seed 43/44 (M2) | Đủ 15.018/15.018, cả 3 seed | ✅ |
| 2 | SUP-LR/SUP-MLP/SUP-METRIC, 3 seed, ngưỡng khóa trên validation | Báo cáo mục 1.4 | ✅ |
| 3 | P_pre/P_post; sửa–hỏng với đối chứng ALL-0/ALL-1/RANDOM; trần oracle | Báo cáo mục 0 và 1.5. Đã sửa cách nhóm file của ReVeal cho Step 6 (CHANGES 11/11) | ✅ |
| 4 | CI ghép cặp, McNemar, Holm cho mọi arm có test; **hai bộ ngưỡng** (đăng ký và hiệu chỉnh) | Có trong `analysis_pa1_20261111/full_tables/contrasts.csv` và `sensitivity.csv` | ✅ về số liệu |
| 5 | Chuỗi kit v1.2 (`import_records → thresholds → evaluate_final`) | Kết quả PA1 hiện có từ `recompute.py`. Ba script đã có trong kit và trong đợt kiểm tra offline của Hiếu. Notebook hình đã dùng importer cho 18 file test, nhưng lượt đánh giá đầy đủ để xuất bảng vẫn còn mở | ⚠️ |
| 6 | File ngưỡng theo phiên bản có hash và kết quả `thresholds --compare` | Có các khóa validation theo từng arm. Chưa có file ngưỡng hiệu chỉnh tổng hợp có hash cho lượt đánh giá đầy đủ | ❌ |
| 7 | Đối soát số liệu giữa các báo cáo (mục 2.2h) | Đã có ở báo cáo §4.6. MCC B2 Devign đổi do ngưỡng, AUROC đổi sau cập nhật donor, và số raw invalid B0 1.132/302 có phạm vi đếm khác nhau | ✅ |
| 8 | `compare_records` B2 với B2-rep | Đã có ở báo cáo §1.6. Score trùng trên 5.006 ID, timestamp khác, `elapsed_s > 0` và tag `repeat`. Provenance runtime đầy đủ vẫn còn thiếu | ✅ về đối chiếu records |
| 9 | Đối chiếu B2-rand ReVeal seed 42/43 qua hai runtime | Đã giải thích hash khóa khác nhau và kiểm tra độ nhạy bằng seed 44. Chưa có phép so score trực tiếp trên cùng ID và prompt qua hai runtime | ⚠️ |
| 10 | ppr@0.5 cho các cặp so sánh và diễn giải RQ4 | Đã bổ sung bảng ppr@0.5 và sửa cách đọc RQ4 theo ngưỡng chung. Kết quả B3 được ghi là thăm dò | ✅ |
| 11 | Quy tắc gap suy biến cho H2.2c | Đã áp dụng ở báo cáo mục 4.1 | ✅ |
| 12 | B1-H2: phân tầng evidence và làm rõ ngưỡng ReVeal | Báo cáo §4.3 và §4.5 đã phân tầng, dùng 0,21 từ validation Kaggle và ghi rõ 0,67 là của lượt Colab I-13 | ✅ |
| 13 | B1-full: kiểm tra renderer giữa validation và test | Audit tái tạo đúng graph của 5.005/5.005 prompt validation. Báo cáo §4.3 đính chính và bỏ đề xuất chạy lại validation vì renderer | ✅ |
| 14 | Dừng GPU cho B3 và B1-H2; hủy B3-swap/B3-flip đang xếp hàng | I-29/I-30 (B3-swap) và I-31 (B3-flip) chạy hoàn tất ngày 11/11 | ❌ trái quyết định |
| 15 | B3 và B1-H2 trình bày ở mức thăm dò | Các hàng chuyển sang §4.5 của báo cáo. p Holm vẫn lấy từ họ 22 phép so đã tính trong PA1 | ✅ về trình bày |
| 16 | Phụ lục A: các mục sai lệch dạng 3 dòng | `CHANGES_AFTER_PREREG.md` có nhiều mục dài; chưa có bảng sai lệch gọn | ⚠️ |
| 17 | Rút gọn `CHANGES_AFTER_PREREG.md` thành bảng sai lệch; tách nhật ký vận hành | Tăng từ ~115k lên ~127k ký tự | ❌ |
| 18 | Hai người đối soát độc lập trước khi đưa số vào bản thảo | Đã tái lập độc lập `contrasts.csv`/`sensitivity.csv` bằng bản vá CRLF; chưa có biên bản của người thứ hai | ⚠️ |
| 19 | Báo cáo tuần 1 trang (thứ Hai) | Chưa thấy trong repo | ❓ |
| 20 | Routing (M2) | Có benefit-router của H3-B gate (mục 1.5) | ✅ |
| 21 | Chấm mù 30 ca (M3) | Đã xong phiếu thứ nhất và đang chờ Hiếu nộp phiếu thứ hai. Bước 8 đầy đủ thuộc Giai đoạn 2 | ⚠️ đang chấm |

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
- Báo cáo §4.5 trình bày kết quả B3 ở phần thăm dò. §4.2 ghi mỗi dataset dùng một cặp demo cố định.
- Kết luận H2.3: **không có kết luận** ở phần xác nhận; nêu lý do trong Limitations; thiết kế lại ở Giai đoạn 2 theo mục 6 của đánh giá:
  - Kho cặp ≥ vài trăm cặp lấy từ PrimeVul hoặc Big-Vul.
  - Tiêu chí nghiệm thu đăng ký trước: câu mặc định ≤ 10%, cặp cùng nguồn ≥ 90%.
- Không diễn giải kết quả ReVeal B3 (ΔAUROC −0,037 [−0,065; −0,008]) là "demo đối chứng gây hại". Chỉ ghi là quan sát thăm dò.
- Ghi một mục sai lệch ba dòng: lượt B3-swap/B3-flip ngày 11/11 chạy sau quyết định dừng; được giữ ở mức thăm dò; không ảnh hưởng Bảng B.
- Báo thầy điều này trong báo cáo tuần.

### 3.3. Họ Holm

- Không bỏ B2 với B3 và B1 với B1-H2 ra khỏi họ 22 phép so đã đăng ký. Bỏ đi sẽ làm Holm bớt chặt, tức là điều chỉnh hồi cứu theo hướng có lợi.
- Báo cáo §1.6 dùng p Holm từ họ 22 phép so đã lưu, còn hai hàng thăm dò được trình bày ở §4.5.
- Ghi một câu lý giải trong Methods.

---

## 4. Đối chiếu bảy mục trong Phụ lục A

| Mục sai lệch | Kết quả đối chiếu |
|---|---|
| B0/B1 hiệu chỉnh ngưỡng sau khi xem test | Báo cáo §1.1, §1.6 và §4.4 ghi cả hai bộ. Bộ hiệu chỉnh là B0 0,98/0,30 và B1 0,98/0,63, tính lại trên toàn bộ validation. Các metric test dùng bộ này được ghi là hồi cứu. Theo ngưỡng đăng ký, H1.1 được hỗ trợ một phần vì cận trên CI ΔMCC Devign là 0,0681, vượt biên 0,03. |
| B2-flip đã xem 230 nhãn thô Devign test | Đã khai báo trong [exposure ledger](../preregistration.md#12-exposure-ledger--3-condition-audit-for-keep-vs-rerun) và sổ chạy I-06. Báo cáo metric ghi đã tiếp xúc test, chưa nhắc riêng số 230. Đưa con số và nguồn vào bảng sai lệch cho bài. |
| B1-full sửa renderer sau khi có test | Báo cáo §4.3 đính chính rằng 4.753/5.006 là số prompt khác giữa hai bản test. Audit tái tạo đúng phần graph của 5.005/5.005 prompt validation. Test hiện tại dùng prompt đã sửa và ngưỡng validation đã khóa 0,99/0,01. Bỏ đề xuất chạy lại validation chỉ vì renderer. |
| B1-H2 thiếu evidence và có hai ngưỡng ReVeal | Phụ lục A ghi 3.697/5.005 prompt thiếu evidence. Báo cáo §4.3 và §4.5 làm rõ 0,67 là từ validation Colab I-13, còn 0,21 là ngưỡng Kaggle dùng trong báo cáo. Đã có kết quả phân tầng có và thiếu evidence ở mức thăm dò. |
| B2-rand ReVeal seed 42/43 có hai khóa runtime | Báo cáo §1.6 giải thích khóa mới pin SciPy 1.16.3, đúng phiên bản lượt cũ đã dùng. Kiểm tra seed 44 dùng một khóa cho toàn test và cho cùng kết luận theo biên AUROC. Đối chiếu score trên cùng ID và prompt qua hai runtime vẫn chưa có. |
| Nhóm B3 chỉ dùng thăm dò | Mục 3 ghi bằng chứng về một cặp cố định mỗi dataset. Báo cáo §4.2 và §4.5 ghi H2.3 chưa có kết luận xác nhận. Khi lập bảng sai lệch, ghi cả việc I-29/I-30 và I-31 vẫn diễn ra sau quyết định dừng. |
| Ngưỡng bổ sung có file theo phiên bản và hash | Đã có số và nguồn khóa validation theo từng arm, xem báo cáo §1.1 và §1.4. Chưa có file hiệu chỉnh tổng hợp có hash cho lượt đánh giá đầy đủ. |

Ngoài Phụ lục A, tên hàng H4.1 trong báo cáo vẫn dùng cụm “gần ngẫu nhiên”. Khi đưa vào bài, ghi trực tiếp tiêu chí AUROC ≤ 0,62.

---

## 5. Tồn đọng kỹ thuật ngoài văn bản đánh giá

1. Lượt tái lập `recompute.py` trên Windows từng vướng hash khi checkout đổi LF thành CRLF và dung sai khi dùng phiên bản sklearn khác. Ghim môi trường và giữ byte đầu vào theo hash đã công bố khi đóng gói.
2. Báo cáo §1.6 đã bổ sung chiều đổi nhãn B2-flip. Báo cáo §4.6 đã bổ sung CI ΔAUPRC và phép so trực tiếp B2−B2-nolabel. Dẫn các bảng bổ sung khi dùng những kết quả này.
3. Một số arm vẫn có provenance runtime một phần. Ghi đúng mức xác nhận của từng nguồn trong Methods.

---

## 6. Công việc còn lại

| Việc | Đầu ra |
|---|---|
| Hoàn tất chuỗi đánh giá bằng kit v1.2 | Gom records theo nguồn đã chọn và lưu `import_manifest.json`. Xuất file ngưỡng hiệu chỉnh riêng có hash, ghi chênh lệch bằng `thresholds --compare`, rồi chạy `evaluate_final` cho hai bộ ngưỡng. Đối chiếu bảng xuất với số PA1 đã có. |
| Chốt hồ sơ sai lệch | Tập hợp đủ bảy mục Phụ lục A trong `CHANGES_AFTER_PREREG.md`, mỗi mục ghi ngày, lý do và phân tích bị ảnh hưởng. Dẫn exposure ledger cho 230 mẫu B2-flip và sổ chạy cho B3-swap/B3-flip. |
| Chốt số trước khi đưa vào bài | Hai người đối soát độc lập. Nếu có cùng ID và cùng prompt qua hai runtime của B2-rand ReVeal, lưu thêm kết quả đối chiếu score. |
| Viết bản thảo và gói nộp | Dùng báo cáo đã cập nhật cho K1–K5. Bổ sung kết quả 30 ca nếu kịp sau khi có đủ hai phiếu và tính κ trước hòa giải. Mốc bản thảo v1 là 26/11, bản nộp là 03/12. |

---

## 7. Những việc không làm

Theo mục 7 của đánh giá và `AGENTS.md`:

- Không khởi tạo thêm arm hoặc phiên GPU ngoài M1/M2, nhất là B3 và B1-H2.
- Không chọn lại ngưỡng cho probe; không sửa `configs/thresholds.json`, `arms.yaml`, data specs hay hồ sơ OSF.
- Không chạy thêm để "cứu" một so sánh. Kết quả không có ý nghĩa thống kê vẫn được ghi và viết vào bài.
- Không ghép số từ workbook hoặc notebook. Mọi số trong bài phải truy được về records có hash.
- AI agent chỉ chạy các lệnh trong danh sách; không tự thay đổi thiết kế hay tạo hồ sơ quản trị mới.
