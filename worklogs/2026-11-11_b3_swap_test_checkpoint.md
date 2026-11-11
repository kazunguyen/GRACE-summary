# B3-swap test seed42 — checkpoint sau deadline

Ngày ghi: 11/11/2026 (Asia/Bangkok)

## Kernel và output

- Kaggle kernel: `duchuynguyen1802/b3-swap-test-latest-ipynb`.
- Notebook đã tải: [b3-swap-test-latest-ipynb.ipynb](../15_Arm_B3_Swap/notebooks/b3-swap-test-latest-ipynb.ipynb).
- Output tải bằng `kaggle kernels output duchuynguyen1802/b3-swap-test-latest-ipynb -p Runs-management/kaggle_outputs_20261111/b3_swap_test_latest_ipynb`.
- Artifact lưu tại [kaggle_outputs_20261111/b3_swap_test_latest_ipynb](../Runs-management/kaggle_outputs_20261111/b3_swap_test_latest_ipynb/).
- Release: `b3_swap_test_release_20261110_v1`, arm B3-swap, seed 42. SHA-256 của embedded release manifest là `3598bf9d005e552690c11cb1e2ae5dd1f4af2a9ac2459e061f5110f04c53952f`; input bundle SHA-256 là `8b9458dfabf56906bbbf2341c0f7c8fc9e85676e7c1f063305a956205dca4cc0`. Cả Devign và REVEAL run manifest đều khớp release, prompt, pool, threshold, model, worker và runtime-lock identities.

## Kết quả census

Run status ghi `state=timed_out`, `timed_out=true`, tổng 4.597 record. Đây là checkpoint theo deadline/reserve của runner; cell cuối trả về mã 0 vì runner checkpoint an toàn. Không diễn giải mã 0 của cell thành hoàn thành census.

| Dataset | Yêu cầu | Có trong checkpoint | Trạng thái | Ngưỡng validation kế thừa B3 |
|---|---:|---:|---|---:|
| Devign test | 2.732 | 2.732 | complete | 0,99 |
| REVEAL test | 2.274 | 1.865 | checkpointed; còn 409 | 0,01 |
| Tổng | 5.006 | 4.597 | incomplete | không fit lại |

Các record đã lưu có ID duy nhất; audit tại chỗ cho thấy 0 score invalid/out-of-range và 0 record chứa label. Devign đủ census; REVEAL chưa đủ. Vì toàn bộ B3-swap test chưa xong và test labels không nằm trong output, worklog này không công bố metric hay kết luận so sánh với B3. Thresholds được giữ nguyên từ validation, không fit trên test.

## Runtime và thời gian

- Notebook session bắt đầu 2026-11-10 17:38:55 UTC (11/11 00:38:55 GMT+7); inference runner bắt đầu 17:59:41 UTC (11/11 00:59:41 GMT+7).
- Runner deadline: 2026-11-11 02:38:57 UTC (09:38:57 GMT+7); dừng nhận record ở 02:33:57 UTC với 300 giây checkpoint reserve. Checkpoint/timed out lúc 02:34:02 UTC (09:34:02 GMT+7); Kaggle notebook hoàn tất ghi output lúc khoảng 09:34:08 GMT+7.
- Runtime provenance: Python 3.13.16; package pins khớp lock (huggingface-hub 0.36.2, llama-cpp-python 0.3.16, numpy 2.1.3, scikit-learn 1.5.2, scipy 1.16.3, tokenizers 0.22.2, transformers 4.57.1); 2 Tesla T4; log loader xác nhận offload 49/49 layers. Runtime-lock SHA-256 `4c9c3bcff5e9fd32532d7edf85df7a961e45ec9c64bee3df8833d986a2eb276e`; model SHA-256 `f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335`; worker SHA-256 `7d21f95a646d562bfa124b8f1898fef9dc85fba26bec89dc3d88753ee6824272`.
- Cell sequence: preflight passed; Devign census completed; REVEAL checkpoint saved at 1.865/2.274; session ended at its bounded deadline. No evidence of model/load failure in this run.

## Tiếp tục

Cần resume cùng release/arm/seed/model/runtime/threshold identity, nhập 1.865 REVEAL records đã checkpoint, và chỉ chạy 409 REVEAL IDs còn thiếu. Sau resume phải kiểm tra đủ 2.274 REVEAL IDs và 5.006 toàn bộ trước khi công bố metric test. Không chạy lại Devign đã đủ và không dò ngưỡng trên test.

## Notebook tiếp tục checkpoint

Notebook [b3-swap-test-latest-ipynb.ipynb](../15_Arm_B3_Swap/notebooks/b3-swap-test-latest-ipynb.ipynb) đã được sửa để dò checkpoint từ input của Kaggle, xác minh status, run identity, IDs, score và threshold bằng validator dùng chung, rồi chép checkpoint vào output làm việc. Runner hiện có sẽ bỏ qua ID đã lưu và xử lý các ID còn thiếu; notebook báo rõ census checkpoint trước khi chạy. Khi khởi chạy, cần gắn version notebook trước (version có output checkpoint này) làm input. Notebook không tạo hay yêu cầu một checkpoint bundle riêng.

