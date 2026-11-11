# B3-swap test seed42 — hoàn tất sau resume

Ngày ghi: 11/11/2026 (Asia/Bangkok)

## Kernel và output

- Kaggle kernel: `duchuynguyen1802/b3-swap-test-latest-ipynb`.
- Notebook đã tải: [b3-swap-test-latest-ipynb.ipynb](../15_Arm_B3_Swap/notebooks/b3-swap-test-latest-ipynb.ipynb).
- Output tải bằng `kaggle kernels output duchuynguyen1802/b3-swap-test-latest-ipynb -p Runs-management/kaggle_outputs_20261111/b3_swap_test_latest_ipynb`.
- Artifact lưu tại [kaggle_outputs_20261111/b3_swap_test_latest_ipynb](../Runs-management/kaggle_outputs_20261111/b3_swap_test_latest_ipynb/).
- Release: `b3_swap_test_release_20261110_v1`, arm B3-swap, seed 42. SHA-256 của embedded release manifest là `3598bf9d005e552690c11cb1e2ae5dd1f4af2a9ac2459e061f5110f04c53952f`; input bundle SHA-256 là `8b9458dfabf56906bbbf2341c0f7c8fc9e85676e7c1f063305a956205dca4cc0`. Cả Devign và REVEAL run manifest đều khớp release, prompt, pool, threshold, model, worker và runtime-lock identities.

## Kết quả census cuối

Lần chạy ban đầu ghi `state=timed_out`, `timed_out=true`, với 4.597 record. Notebook được sửa để đọc version notebook trước làm input; lần resume xác minh checkpoint theo run identity rồi chạy các ID thiếu. Output mới ghi `state=complete`, `timed_out=false`, đủ 5.006 record.

| Dataset | Yêu cầu | Có trong checkpoint | Trạng thái | Ngưỡng validation kế thừa B3 |
|---|---:|---:|---|---:|
| Devign test | 2.732 | 2.732 | complete | 0,99 |
| REVEAL test | 2.274 | 2.274 | complete; đã resume thêm 409 | 0,01 |
| Tổng | 5.006 | 5.006 | complete | không fit lại |

Toàn bộ record có ID duy nhất; audit cho thấy 0 score invalid/out-of-range và 0 record chứa label. So sánh checkpoint ban đầu với output sau resume: cả 4.597 record cũ còn nguyên, không thay prompt hash, score hoặc logprob; resume bổ sung đủ 409 REVEAL ID còn thiếu. Vì test labels không nằm trong output, worklog này không công bố metric hay kết luận so sánh với B3. Thresholds được giữ nguyên từ validation, không fit trên test.

## Output lần resume

- Lệnh: `kaggle kernels output duchuynguyen1802/b3-swap-test-latest-ipynb -p Runs-management/kaggle_outputs_20261111/b3_swap_test_resume_latest`.
- Artifact mới: [kaggle_outputs_20261111/b3_swap_test_resume_latest](../Runs-management/kaggle_outputs_20261111/b3_swap_test_resume_latest/); checkpoint gốc I-29 vẫn lưu riêng.
- Resume runner: 2026-11-11 03:33:01 UTC đến 04:19:10 UTC (10:33:01–11:19:10 GMT+7); trạng thái complete, 5.006/5.006.
- Hai run manifest giữ release/input SHA `8b9458dfabf56906bbbf2341c0f7c8fc9e85676e7c1f063305a956205dca4cc0`, model SHA `f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335`, runtime lock `4c9c3bcff5e9fd32532d7edf85df7a961e45ec9c64bee3df8833d986a2eb276e`, worker SHA `7d21f95a646d562bfa124b8f1898fef9dc85fba26bec89dc3d88753ee6824272), arm B3-swap, seed 42 và thresholds 0,99 / 0,01.
- Runtime provenance ghi Python 3.13.16, pinned package versions khớp lock, 2 Tesla T4; model offload log xác nhận 49/49 layers trên GPU. Resume provenance giữ cùng model, runtime lock, worker và source archive hashes.

## Runtime và thời gian

- Notebook session bắt đầu 2026-11-10 17:38:55 UTC (11/11 00:38:55 GMT+7); inference runner bắt đầu 17:59:41 UTC (11/11 00:59:41 GMT+7).
- Lần chạy ban đầu: deadline 2026-11-11 02:38:57 UTC (09:38:57 GMT+7); dừng nhận record ở 02:33:57 UTC với 300 giây checkpoint reserve. Checkpoint lúc 02:34:02 UTC (09:34:02 GMT+7).
- Lần resume: runner bắt đầu 03:33:01 UTC (10:33:01 GMT+7), hoàn tất 04:19:10 UTC (11:19:10 GMT+7), trước deadline 12:11:36 UTC; không timeout.
- Runtime provenance: Python 3.13.16; package pins khớp lock (huggingface-hub 0.36.2, llama-cpp-python 0.3.16, numpy 2.1.3, scikit-learn 1.5.2, scipy 1.16.3, tokenizers 0.22.2, transformers 4.57.1); 2 Tesla T4; log loader xác nhận offload 49/49 layers. Runtime-lock SHA-256 `4c9c3bcff5e9fd32532d7edf85df7a961e45ec9c64bee3df8833d986a2eb276e`; model SHA-256 `f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335`; worker SHA-256 `7d21f95a646d562bfa124b8f1898fef9dc85fba26bec89dc3d88753ee6824272`.
- Cell sequence: preflight passed; Devign census completed; REVEAL checkpoint saved at 1.865/2.274; session ended at its bounded deadline. No evidence of model/load failure in this run.

## Tiếp tục

Không còn ID test nào thiếu. Nếu tính metric sau này, chỉ dùng test labels được giữ local và evaluator chung; không fit lại threshold trên test.

## Notebook tiếp tục checkpoint

Notebook [b3-swap-test-latest-ipynb.ipynb](../15_Arm_B3_Swap/notebooks/b3-swap-test-latest-ipynb.ipynb) đã dò checkpoint từ input của Kaggle, xác minh status, run identity, IDs, score và threshold bằng validator dùng chung, rồi resume các ID còn thiếu. Lần chạy đã hoàn tất. Không cần checkpoint bundle riêng.

