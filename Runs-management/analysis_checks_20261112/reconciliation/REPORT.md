# Bảng đối soát số liệu và inventory records test — 12/11/2026

Đáp ứng mục 2.2h và mục M1 "bảng đối soát số liệu" của *Đánh giá tiến độ 11/11*.

Tái lập:

```
python -X utf8 Runs-management/analysis_checks_20261112/reconcile_inventory.py --out Runs-management/analysis_checks_20261112/reconciliation
```

Nhãn lấy từ `01_Author_Baseline_Unified/output/research_freeze_20261101/{ds}/test_manifest.jsonl`. AUROC/AUPRC tính bằng `grace_diag.stats` của kit v1.2.

## 1. Inventory

Chi tiết từng file ở `inventory.csv`. Mỗi dòng gồm: đường dẫn records chuẩn, SHA-256 thô và SHA-256 sau chuẩn hóa LF, N, khớp census, số điểm hợp lệ, số raw lỗi, số nhãn lệch, AUROC, AUPRC, số runtime hash và trạng thái so với bảng 1.3 của báo cáo metric.

- **38 file records test**:
  - B0, B1, B2, B2-flip, B2-rep, B2-nolabel, B2-labelonly, B1-full, B1-H2, B3, B3-nodiff, B3-swap, B3-flip: seed 42, hai dataset.
  - B2-rand và B1-shuf: seed 42/43/44, hai dataset.
- Mọi file **đủ census** (ID trùng khớp tuyệt đối với test manifest), **100% điểm s hợp lệ** và **0 nhãn lệch** so với manifest.
- **36/36 file có trong bảng 1.3 khớp báo cáo.** AUROC và AUPRC lệch dưới 5e-5 (chỉ do làm tròn); N và số raw lỗi trùng hoàn toàn.
- **B2-rand seed 44** (hai dataset) có records hợp lệ nhưng không có dòng trong bảng 1.3. Cần bổ sung, hoặc ghi rõ là chỉ dùng trong phân tích robustness theo seed.
- **Runtime hash trong record**:
  - B2-rand ReVeal seed 42/43 có **2 hash**. Đây là phần trộn runtime đã biết (2.017 + 257 và 2.028 + 246 record).
  - B0, B1, B2, B2-flip, B2-rep, B2-nolabel, B2-labelonly và B1-H2 **không ghi `runtime_contract_sha256` trong record**. Provenance của các arm này dựa vào nhật ký phiên (mức PARTIAL như đã ghi trong `runtime_session_reconciliation_20261110`).

## 2. Giải thích các số liệu trôi giữa báo cáo 05/11 và 08/11

Nguồn số 05/11: `docs/TONG_HOP_VAN_DE_CONTRASTIVE_ICL_VA_TIEN_DO_OSF.md`, bảng mục 2.1. Số tái lập nằm ở `b2_snapshot_drift.csv`.

| Số liệu | 05/11 | 08/11 trở đi | Nguyên nhân (đã tái lập) |
|---|---|---|---|
| B2 Devign test MCC | 0,0441 | 0,0597 | Bản 05/11 tính MCC tại **ngưỡng 0,5**; bản 08/11 tính tại **τ\* = 0,70** đã khóa. BA 52,11% và F1 0,5571 của bản 05/11 cũng khớp ngưỡng 0,5. |
| B2 ReVeal test MCC | 0,0562 | 0,0645 | Như trên: 0,5 so với τ\* = 0,12. |
| B2 Devign test AUROC | 0,5292 | 0,5305 | Bản 05/11 dùng file records **trước khi ghép donor rerun-66** (`inference_qwen_q4_b2_20261101/...`, sha256-LF `0dbcf384bd…`), dù bảng ghi "ghép rerun-66 I-09". Bản chuẩn `inference_qwen_q4_b2_frozen_donor_20261102` (`d0a61bfa6c…`) thay **38 prompt Devign test** bằng donor đã làm sạch; 28 prompt còn lại của tổng 66 thuộc validation. |
| B2 ReVeal test AUROC | 0,5662 | 0,5662 | Không đổi: hai file trùng hash (`dcdaf0d0b5…`) vì rerun-66 chỉ chạm Devign. |
| B0 raw response lỗi | 1.132 | 302 | 1.132 là **tổng cả bốn split** (Devign validation 284 + test 302, ReVeal validation 261 + test 285) nhưng bị đặt vào dòng Devign. 302 là riêng Devign test. Cả bốn split có 0 điểm logprob không hợp lệ. |

Hệ quả: AUROC của B2 Devign trong bài phải là **0,5305** (file frozen-donor). Mọi MCC/F1/BA phải ghi rõ tính tại ngưỡng nào.

## 3. File records cũ cần tránh

B1-full có 9 bản records test rải trong `Runs-management/`. Chỉ bản trong `run_handoff_20261108/completed_results/b1_full_test_completed_20261108/` (renderer đã sửa) khớp báo cáo: AUROC 0,5311 / 0,5782.

Sáu bản còn lại thuộc renderer cũ:
- Devign: AUROC 0,5309.
- ReVeal: chỉ có 118 record.
- Vị trí: `kernel_outputs_harvest/`, `kaggle_status_20261108_*/…/grace-b1-full-test/`, `acceptance_6arms_20261108/`, `run_handoff_20261108/snapshot_0912/`.

Các bản này **không được dùng** cho bài.

B2 Devign cũng có 3 bản cũ trước rerun-66: `inference_qwen_q4_b2_20261101/` và hai thư mục `kaggle_qwen_q4_b2/downloaded_output_20261101_run{2,3}/`.

## 4. Quy ước từ nay

Mọi số trong bản thảo phải truy được về một dòng của `inventory.csv` (đường dẫn và SHA-256). Khi một file records thay đổi, chạy lại script và ghi lý do vào bảng sai lệch.
