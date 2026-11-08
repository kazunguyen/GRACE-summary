# B2-rand seed 44 test: head + tail consolidation — 2026-11-08

## Run and output checked

- Kaggle kernel: `duchuynguyen1802/02-kaggle-qwen-q4-b2-rand-seed44-test-ipynb`.
- Output downloaded with `kaggle kernels output duchuynguyen1802/02-kaggle-qwen-q4-b2-rand-seed44-test-ipynb -p ...` to `Runs-management/kaggle_outputs_20261108/b2_rand_seed44_test_latest/`.
- Notebook metadata reports Papermill start `2026-11-07T11:14:47.974588Z`, end `2026-11-07T20:09:30.268931Z`, Python 3.13.16, GPU accelerator Tesla T4, runtime lock SHA-256 `bf1f859dc786e206a3c11d655b04b528dc68f59a15a82d4db894ac5944b0ac2e`, and threshold-lock SHA-256 `48c12066bbddabc8ef674a70f6f9ac68cb74cbeecc2a5ebbbda3cb4cb6498735`.
- The run stopped at its nine-hour safety cap. Head checkpoint SHA-256: `0d34c9cdf28e611f9b28b086a93f2cd15730680dfcd7641ce1cbc63138d1a427`.
- Head output has 4,661/5,006 records: Devign 2,732/2,732 and REVEAL 1,929/2,274.

## Merge with the earlier tail

The earlier I-20 tail output contains 374 REVEAL seed44 records. The head and tail overlap on 29 IDs. Following the instruction for this merge, the head record wins on all overlaps; the tail supplies 345 tail-only IDs. The merged outputs now contain Devign 2,732/2,732 and REVEAL 2,274/2,274, for 5,006/5,006 seed44 test IDs.

### Đối chiếu kết quả của 29 ID overlap

Đã join theo ID giữa REVEAL seed44 trong output head I-21 (`Runs-management/kaggle_outputs_20261108/b2_rand_seed44_test_latest/b2_rand_seed44_test/seed_44/reveal/test/records.jsonl`) và output tail I-20 (`Runs-management/kaggle_outputs_20261107/b2_rand_three_seed_test_tail_latest/grace_b2_rand_three_seed_test_tail_checkpoint.zip`, member `seed_44/reveal/test/records.jsonl`). Có đúng 29 ID chung. **Cả 29 record khớp toàn bộ trường kết quả và provenance**: nhãn, prompt SHA-256, demo IDs, số token, logprob hai lớp, xác suất hai lớp, `s`, token greedy/top-5, raw output, validity, `pred_argmax`, `pred_tau`, threshold, model SHA, inference seed, backend, quantization, tokenizer/model revision và runtime/threshold-lock SHA. Chỉ `elapsed_s` và `timestamp` khác nhau, do hai lần chạy riêng.

Kết luận: ưu tiên record head cho 29 ID không làm thay đổi score, prediction hay metric; tail chỉ đóng góp 345 ID chưa có trong head. So sánh trực tiếp head/tail ở đây, không chỉ dựa vào file đã merge.

The merged files and metrics are in `06_Arm_B2_Rand/test_results_20261107/seed_44/`. Dataset records were validated and scored using the already locked validation thresholds: Devign τ=0.99 and REVEAL τ=0.64. No threshold was selected or changed using test data. Head and tail use the same runtime-lock SHA; GPU logs report 49/49 layers offloaded.

| Dataset | n | τ | MCC | AUROC | Average precision | Accuracy |
|---|---:|---:|---:|---:|---:|---:|
| Devign | 2,732 | 0.99 | 0.058853 | 0.532716 | 0.500571 | 0.547218 |
| REVEAL | 2,274 | 0.64 | 0.066453 | 0.574830 | 0.123473 | 0.693052 |

Final records SHA-256: Devign `d0ee0cd44d5dda471481c2d8dacfae02ef6834eafcc61a1ef0d8a7de95f5b344`; REVEAL `ba1ce1a45574432676c1a57da5e5b54a1a2e89b38fe9a5bcfc10b7621eb0092e`. Full merge counts and run provenance are in `06_Arm_B2_Rand/test_results_20261107/seed_44/provenance.json` and `evaluation_summary.json`.

## Progress update

B2-rand test is now complete for all three prompt seeds: 15,018/15,018 IDs. `Runs-management/RUNS.md` records this as I-21. Across six Kaggle arms with outputs, the cumulative number of unique imported records is 65,056.
