# Gom nhánh và chạy lại Step 6 với B2 chuẩn (25/11/2026)

Xử lý các điểm còn mở trong [rà soát gói Option1](2026-11-16_ra_soat_goi_option1.md): Step 6 dùng B2 trước khi đổi donor, phân vị H5.3, trích dẫn chưa xác minh. Nhánh làm việc: `docs/phase1-consolidation-20261125`.

## Đã làm

- **Gom nhánh:**
  - Merge `origin/dung` (đã gồm `main`) vào nhánh review: bản nháp paper v1, evidence, `runs/final` import manifest, `tables_prereg`/`tables_corrected`, `configs/thresholds_corrected.json`. Không có xung đột.
  - Bỏ qua `docs/offline-checks-20261112` (`65fa20e`): bản trước rebase của `63deb77`, bản v2 đã merge.
  - Các nhánh remote còn lại đã nằm trong lịch sử của nhánh này.
  - Test toàn vẹn: 37/37 đạt (`test_preregistration_integrity`, `test_probes`, `test_stats_and_complementarity`).
- **Dựng B2 chuẩn cho Step 6** (`STEP6_supervised_anchors/src/build_b2_canonical_root.py`):
  - Devign validation: run3 thay 28 dòng bằng records rerun-66 (blob git `794aa82b…`). Devign test, ReVeal test: copy từ `inference_qwen_q4_b2_frozen_donor_20261102`. ReVeal validation: run3.
  - Kiểm: ID đổi so với run3 đúng bằng ID rerun-66 (28 và 38) và trùng danh sách donor-28; ReVeal 0 dòng đổi.
  - Hash records khớp nguồn trong `runs/final/*/B2/42/import_manifest.json` (`fd40fb2c…`, `d0a61bfa…`).
  - Kết quả: `STEP6_supervised_anchors/inputs/b2_canonical_frozen_donor_20261102/`.
- **Chạy lại Step 6** (`STEP6_supervised_anchors/src/rerun_step6_canonical_b2.py`):
  - Dùng joined CSV của lock `44f00d19` (y, p_gate, group, SUP-LR) và `xpre` H3-B đã khóa (4/4 hash khớp manifest). Chỉ thay s/valid. Gọi nguyên hàm của `step6_complementarity.py`, không sửa script đã khóa.
  - Môi trường giống lock: numpy 1.26.4, scipy 1.17.1, scikit-learn 1.5.2 (venv Python 3.12). Với scikit-learn 1.3.2, P_pre/P_post lệch khoảng 1 dự đoán nên không dùng.
  - Đối chứng (B2 run3): trùng lock `44f00d19` 985/985 trường mỗi dataset; trùng số Bảng D trong `[Official]-Paper/evidence/h52_shared_threshold.json`.
  - Kết quả B2 chuẩn: Devign đổi ở chữ số thứ ba, mọi phán quyết giữ nguyên; ReVeal trùng tuyệt đối.

    | Devign | Cũ (run3) | Mới (B2 chuẩn) |
    |---|---|---|
    | Bảng D ΔMCC P_post − P_pre, τ chung 0,53 | −0,0008 [−0,0095; 0,0080] | −0,0016 [−0,0107; 0,0075] |
    | MCC P_post | 0,2858 | 0,2850 |
    | Sửa / gây thêm so với H3-B | 397 / 718 | 400 / 716 |
    | Phân vị 97,5 expert ngẫu nhiên | 465,05 | 464,0 |
    | ΔBA định tuyến lợi ích − ngẫu nhiên | +0,0204 [0,0138; 0,0270] | +0,0195 [0,0129; 0,0262] |
    | Oracle | 77,16% | 77,27% |

  - Output: `STEP6_supervised_anchors/runs/complementarity_step6/step6_lock_64fb2c99d904_rerun_canonical_b2_20261125/` và `…_rerun_control_b2_20261125/`; `rerun_summary.json` liệt kê từng trường khác. Hai lock cũ giữ nguyên.
- **Phân vị H5.3:** tính cả 95 (văn bản đăng ký) và 97,5 (code) từ cùng 20 expert ngẫu nhiên seed 42. Devign 400 ≤ 464,0 / 464,0; ReVeal 164 ≤ 173,3 / 176,15. Tiêu chí đạt ở cả hai mức.
- **Trích dẫn Kaniewski et al.:** arXiv 2609.37669 tồn tại (cs.SE, v1 ngày 29/09/2026). Tên bài và sáu tác giả khớp danh mục tham khảo của bản nháp.
- **Họ Holm:** đối chiếu D10 trong bảng sai lệch; họ 22 phép là lựa chọn có lý do ghi sẵn, không cần sửa.
- Ghi `CHANGES_AFTER_PREREG.md` (mục 25/11) và D13, D14 trong `Runs-management/analysis_checks_20261112/DEVIATIONS_TABLE.md`.

## Lưu ý

- `runs/final/devign/validation/B2/42/records.jsonl` ở máy này là bản ngày 03/11, trùng run3, không phải B2 chuẩn mà import manifest ghi. Không dùng file này.
- Bản checkout Windows đổi LF thành CRLF làm lệch hash `step6_lock.json` và script. Cần ghi lại hai file từ blob git (LF) trước khi chạy `step6_complementarity.py`.
- Máy này không có `campaign_manifest.json`/`h3b_export_manifest.json` và NPZ CodeT5, nên không chạy được `step6_complementarity.py` trọn vẹn; bản chạy lại dựa trên joined CSV và `xpre` của lock.
- Chưa sửa số trong bản nháp: bản nháp đang chờ thầy duyệt.

## Còn cần

- Ghi việc chạy lại Step 6 vào báo cáo tuần để thầy xác nhận trước khi đưa số mới vào bài.
- Chốt lock Step 6 chính. Đề xuất: bản chạy lại B2 chuẩn.
- ~~Dũng đối soát độc lập Bảng D và các số Devign ở bảng trên.~~ Đã xong cùng ngày: 5/5 hạng mục PASS, tái chạy trên WSL khớp đến 10 chữ số thập phân ([biên bản](2026-11-25_dung_doi_soat_doc_lap_step6_b2_chuan.md)).
- Sau khi thầy duyệt: cập nhật Bảng D, §4.5 và `h52_shared_threshold.json` trong bản nháp; thống nhất phần B1-full (§3.5, §4.3, §6).
- Mở PR từ `docs/phase1-consolidation-20261125` vào `baseline-unified`.
