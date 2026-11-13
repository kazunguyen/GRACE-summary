# Option 1 — Bổ sung validation và đối chiếu bảng (13/11/2026)

Theo Phụ lục B, gom records bằng dry-run trước khi nhập, đối chiếu hai bộ ngưỡng và xác nhận Bảng A/B/C. Đợt này bổ sung 10 nhóm validation Hiếu đã đưa vào commit `9cea10c`, sau khi branch được nhập vào `baseline-unified`.

## 1. Rà nguồn

- 10 file khớp blob Git ở commit `9cea10c`. Sáu file B1-shuf seed 44, B2-nolabel và B2-labelonly khớp SHA-256 trong khóa validation đã ghi. Bốn file B2-rep và B1-full không có SHA-256 tham chiếu trong inventory cũ, nên dùng SHA-256 của nguồn và đối chiếu blob Git.
- Mỗi nhóm có đủ ID, nhãn và điểm hợp lệ: Devign 2.732 và ReVeal 2.273. So ID và nhãn theo bộ validation B0 đã gom. Các file bổ sung không có trường hash runtime trong records. B1-full vẫn mang sai lệch renderer cũ.
- 50 nguồn đã dùng lần trước đều khớp SHA-256. Đã đối chiếu 20 file Python của kit đang dùng với ZIP v1.2.

## 2. Gom và kiểm tra đầu ra

- Dry-run với đúng 60 nguồn đọc 150.165 records, không có xung đột. Hai cảnh báo trộn runtime của B2-rand ReVeal seed 42/43 vẫn xuất hiện như ở lần trước.
- Đã chạy nhập thật với mặc định dừng khi có xung đột. Đọc lại đủ 60 manifest, kiểm SHA-256 đầu ra. Cả 50 nhóm đã có giữ nguyên hash records. 10 nhóm mới giữ nguyên các trường gốc và có manifest riêng.

## 3. Đối chiếu ngưỡng

- Chạy `thresholds --compare` trên cả 30 nhóm validation và điểm SUP. 48 ngưỡng tái lập khớp bộ hiệu chỉnh (so với dung sai 1e-9 cho số thực). So với bộ đăng ký, chỉ lệch bốn ngưỡng B0/B1 đã ghi nhận. B2-rep vẫn kế thừa 0,70 (Devign) và 0,12 (ReVeal) từ B2.
- Bốn khóa P-PRE/P-POST thuộc phân tích Step 6. Lệnh này không có điểm validation từng mẫu của hai meta-model nên không tái lập bốn khóa đó. Bảng vẫn dùng hai bộ khóa hiện hành.
- Bắt đầu xuất lại hai bộ Bảng A/B/C trên đầu vào 60 nhóm, 5.000 lượt bootstrap theo cụm và seed 20261117. Dùng lại trình chạy đã đối chiếu chuỗi lấy mẫu ở lần trước, với mã kit nguyên bản.

| Nhóm validation | Devign N / τ | ReVeal N / τ |
|---|---:|---:|
| B2-rep, seed 42 | 2.732 / 0,70 | 2.273 / 0,12 |
| B2-nolabel, seed 42 | 2.732 / 0,98 | 2.273 / 0,21 |
| B2-labelonly, seed 42 | 2.732 / 0,99 | 2.273 / 0,02 |
| B1-full, seed 42 (renderer cũ) | 2.732 / 0,99 | 2.273 / 0,01 |
| B1-shuf, seed 44 | 2.732 / 0,67 | 2.273 / 0,04 |

Sau khi lưu vào `runs/final`, đã đọc lại và kiểm 60 cặp SHA-256 nguồn/đầu ra. Inventory có 30/30 nhóm validation (75.075 records), 30/30 nhóm test (75.090 records) trong phạm vi Option 1 ngoài B3 và 60 manifest. Hash từng file và commit nguồn của 10 nhóm bổ sung nằm trong [inventory](../runs/final/source_inventory.json). Xem [log dry-run](../runs/final/2026-11-13_import_dry_run.log), [log nhập](../runs/final/2026-11-13_import_run.log), [log so ngưỡng](../runs/final/2026-11-13_thresholds_compare.log) và [file ngưỡng kiểm toán](../runs/final/2026-11-13_thresholds_validation_audit.json).

Lệnh nhập dùng `scripts/import_records.py --src <60 file trong inventory> --dst <thư mục tạm>/final --groups-csv runs/final/groups.csv` với `--dry-run` ở lượt đầu. Nguồn mới đọc từ worktree `GRACE-summary-baseline-unified` vì worktree đang giữ bộ kết quả PA1 ở nhánh `dung`. Bước kiểm toán ngưỡng đọc `runs/final`, `configs/arms.yaml` và `runs/anchor/anchor_scores.csv`, ghi JSON kiểm toán riêng. Hai lượt xuất bảng dùng `configs/protocol.yaml`, cùng CSV điểm SUP và lần lượt hai file `configs/thresholds.prereg.json` và `configs/thresholds_corrected.json`.

## 4. Kết quả xuất lại bảng

- Cả hai lượt `evaluate_final` kết thúc với mã 0. Đối chiếu SHA-256 theo từng bộ với lần xuất 12/11: **10/10 file khớp trong mỗi bộ**, gồm CSV/TeX của Bảng A và B, CSV Bảng C, bốn PNG và `thresholds_used.json`. Mỗi bộ có 54 dòng A, 38 dòng B (34 dòng có kết quả và 4 dòng thiếu arm), 2 dòng C và 48 ngưỡng được áp dụng.
- Bảng A/B/C lấy kết quả từ test và các ngưỡng đã khóa. Lần bổ sung này hoàn thiện nguồn validation và tái lập ngưỡng, nên các số báo cáo giữ nguyên. Đã lưu log mới vào [bộ đăng ký](../runs/tables_prereg/2026-11-13_evaluate_final.log) và [bộ hiệu chỉnh](../runs/tables_corrected/2026-11-13_evaluate_final.log).
- Giới hạn của kit vẫn áp dụng: H2.3 (B3 thăm dò) và H5.3 (P-PRE/P-POST) được báo riêng. Bảng B của kit hiệu chỉnh Holm trên 18 phép có mặt, còn báo cáo PA1 dùng họ 22 phép đã đối soát. Bảng C của kit dùng ngưỡng 0,5, còn kết quả ở ngưỡng khóa B2 và CI lấy từ bảng độ nhạy PA1.
- Hai file khóa ngưỡng, giao thức và CSV điểm SUP khớp SHA-256 trước và sau khi chạy. Không phát sinh sai lệch mới trong đợt bổ sung này.
