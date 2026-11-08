---
id: "step6-supervised-anchors-start-20261108"
title: "Bắt đầu triển khai Bước 6: anchor có giám sát và phân tích bổ sung"
recorded_at: "2026-11-08"
timezone: "Asia/Bangkok"
status: "step2_complete_anchor_training_pending"
---

# Bắt đầu Bước 6

## Mục tiêu

Triển khai Bước 6 theo protocol đã đăng ký: huấn luyện SUP-LR, SUP-MLP và SUP-METRIC trên dữ liệu đã làm sạch, theo ba seed 42/43/44; chọn ngưỡng trên validation; sau đó ghép điểm B2 tương thích để chạy P_pre/P_post, phân tích sửa–hỏng, expert và routing.

## Lock và phạm vi

- Lock vận hành: [step6_lock.json](../step6_supervised_anchors/step6_lock.json).
- Commit lock: `e8f3cdc` (`docs:lock-step6-anchor-inputs`), chỉ commit một file lock.
- Notebook bước 2 (WSL, NPZ adapter không encode lại): [02_export_locked_codet5_cache_to_npz_wsl.ipynb](../step6_supervised_anchors/02_export_locked_codet5_cache_to_npz_wsl.ipynb).
- Protocol tham chiếu: `configs/protocol.yaml`, SHA-256 `273f750ff2323d7f2bd842223a02c36dc49c69bead396333ab78dade7a125116`.
- Freeze dữ liệu: `01_Author_Baseline_Unified/output/research_freeze_20261101/freeze_manifest.json`, SHA-256 `e1d3c6b17c3a0b5c1e05203794d48a33825e0ea00a55deaaef565af25efe0448`.
- Không sửa preregistration, protocol, threshold lock hay ma trận arm đã đăng ký.

## Đã kiểm tra

- Có raw train/validation/test, manifest tương ứng và donor bank frozen cho cả Devign lẫn ReVeal trong `research_freeze_20261101`; hash của từng artifact được ghi trong lock.
- Cache CodeT5 ReVeal có đủ ba split, 768 chiều; audit ngày 31/10 kết luận khớp đầy đủ code frozen và đã kiểm encoder revision/recipe.
- Pipeline cache được xác nhận qua `Runs-management/reconcile_donor_prompts.py::CachedEncoder`, retrieval provenance của cả hai dataset và `grace_15arms_prompts_and_clean_specs/validation_active_manifest.json`.
- Cả sáu manifest/vector hiện có tại `output/local_full/{devign,reveal}/embedding_cache/{train,validation,test}` khớp SHA-256 được ghi trong retrieval provenance. Kiểm trực tiếp ID và SHA-256 của `func.strip()` trên raw freeze đạt 21.854/21.854 + 2.732/2.732 + 2.732/2.732 Devign; 18.187/18.187 + 2.273/2.273 + 2.274/2.274 ReVeal.
- Cache dùng CodeT5 `Salesforce/codet5-base@02cd2d31bb7c6d0e4d91156167b2de044989c733`, đủ ba split và hoàn tất; không cần encode lại. Runner anchor hiện nhận NPZ (`ids`, `X`), trong khi cache là `vectors.npy` + manifest; chỉ cần adapter có kiểm ID nếu runner đó được dùng.
- Chưa huấn luyện anchor; chưa tạo `anchor_scores.csv` hay `anchor_summary.json`.
- Notebook bước 2 đã chạy trên WSL; đọc lock commit `e8f3cdc`, kiểm tra hash/provenance/ID và xuất đủ sáu NPZ adapter. Kiểm tra độc lập xác nhận NPZ IDs và vector khớp cache nguồn; không có cell lỗi.

## Lưu ý huấn luyện theo đề cương

- Ba seed cho anchor: 42, 43, 44; seed headline là 42.
- Huấn luyện trên train; chọn ngưỡng trên validation theo MCC; nhãn test không tham gia fit hoặc chọn ngưỡng.
- SUP-LR/SUP-MLP dùng embedding CodeT5 đóng băng 768 chiều; SUP-METRIC dùng 26 đặc trưng code.
- P_pre/P_post phải dùng cùng fold; 3-fold StratifiedGroupKFold theo commit_id/file_hash, fallback đối xứng khi LLM invalid. Routing cần báo ngân sách 5%, 10%, 25%, Random Router 20 seed và Oracle.

## Thứ tự công việc đã khóa

1. Kiểm hash raw, manifest và donor theo freeze.
2. Dùng lại sáu cache CodeT5 đã được xác nhận là cache retrieval của prompt cuối; không encode lại.
3. Chuẩn bị embedding đầu vào theo ID; tính 26 static metrics từ code frozen.
4. Huấn luyện ba anchor, ba seed, trên train.
5. Chọn ngưỡng theo MCC trên validation; không dùng nhãn test để fit/chọn.
6. Xuất score validation/test và summary kèm provenance/hash.
7. Khi có B2 score tương thích, chạy các phân tích meta-model và routing còn lại của Bước 6.

## Trạng thái hiện tại

Đã tạo thư mục `step6_supervised_anchors/`, ghi lock JSON và bắt đầu worklog. Bước 2 hoàn tất: sáu cache CodeT5 dùng cho retrieval prompt cuối được tái sử dụng nguyên trạng và xuất NPZ adapters có ID. Chưa bắt đầu fit anchor.

## Artifact tham chiếu

- `01_Author_Baseline_Unified/output/reusable_codet5_20261031/README.md` — SHA-256 `114ab923d6ff3e3bfd1a2da9853079fc22fdceeb3c31d4ab68125b41ef29f67b`.
- `01_Author_Baseline_Unified/output/reusable_codet5_20261031/codet5_cache_audit_20261031.json` — SHA-256 `67c763dbda12952328d79f458a8a870b276e0c0c4046eb3ef9e3ff4659e29e88`.
- `01_Author_Baseline_Unified/diagnostic_kit/src/grace_diag/supervised_anchor.py` — SHA-256 `c14f88919701675bf1a6f6a703d7a5e3c6a5c4d0e5f6205cdf0baa063543eff9`.

## Xác minh cache prompt cuối

- Active manifest trỏ tới retrieval provenance Devign/ReVeal và donor bank sạch đã chốt; các hash tham chiếu khớp hash file thực tế.
- Retrieval provenance ghi manifest/vector hash của sáu cache. Hash đó khớp chính xác sáu cache ở `output/local_full`.
- So sánh trực tiếp ID và `SHA256(func.strip())` giữa cache manifest và raw freeze đạt 100% ở cả sáu split. Model revision khớp lock.
- Vì vậy xác nhận đây chính là cache CodeT5 đã dùng để chọn demo cho B2 trong pipeline prompt cuối; arm phái sinh dùng lại demo/spec B2. Không tạo lại cache.
- README audit cache 31/10 có câu báo partial Devign match, mâu thuẫn với kiểm tra trực tiếp trên raw freeze đang khóa. Ghi nhận discrepancy; bằng chứng trực tiếp là cache manifests/vector hashes gắn trong retrieval provenance và kiểm tra ordered ID/code hash trên raw freeze.

## Nghiệm thu bước 2 — 2026-11-08

- Notebook đã chạy hoàn tất trên WSL; cả sáu tổ hợp dataset/split đều qua kiểm tra lock, frozen raw, cache provenance, row IDs, shape, dtype và giá trị hữu hạn.
- NPZ adapters: `STEP6_supervised_anchors/cache/anchor_npz/{devign,reveal}/{train,validation,test}.npz`; mỗi file có `ids` và `X` (768 chiều). Kích thước split: Devign 21.854/2.732/2.732; ReVeal 18.187/2.273/2.274.
- Đối chiếu độc lập sau khi chạy: ID khớp manifest cache; `X` bằng chính xác `vectors.npy` đã khóa ở cả sáu split; notebook không có output lỗi.
- Báo cáo provenance/hash: `STEP6_supervised_anchors/cache/anchor_npz/adapter_manifest.json`, SHA-256 `898ede843e4e8ff33ea7a2f55cdb4da27a3e3bb0dfcfda2697b83ebddb596de9`.
- Không gọi CodeT5 hoặc LLM; chưa fit anchor. Sáu NPZ là artifact cục bộ và không được commit vì kích thước lớn; notebook và manifest nhỏ được commit để tái lập/kiểm toán.

## Bước tiếp theo

Chạy anchor fitting riêng cho Devign và ReVeal bằng các NPZ này, raw frozen cùng dataset, ba seed 42/43/44. SUP-LR/SUP-MLP dùng `X`; SUP-METRIC được tính từ `func` bởi runner. Fit trên train, chọn ngưỡng MCC trên validation; không dùng nhãn test để fit/chọn. Kết quả cần tạo `anchor_scores.csv` và `anchor_summary.json` cho mỗi dataset trước khi ghép với B2.
