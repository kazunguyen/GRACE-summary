# Rà soát 28 dòng B2 / Devign / validation / seed 42 sau khi đổi donor (18/11/2026)

Phiếu Dũng gửi: `docs/hieu_review_28_devign_validation.csv`. Phiếu đã điền: `hieu_review_28_devign_validation_filled.csv`, cùng cột với phiếu gốc, chỉ điền thêm hai cột verdict và ghi chú. Tóm tắt máy đọc: `hieu_review_28_devign_validation_filled.summary.json`.

Kết quả: **28/28 PASS**, 0 FAIL, 0 UNVERIFIABLE. Đạt cả 19 kiểm tra cấp file.

## Cách chạy

```
python verify_donor28.py <phiếu csv> <Option1 runs/final> <Option1 .../user_run_output_workers_20261115/I09_B2_rand_validation/kaggle_inference.py> <csv đầu ra>
```

Script không dùng `build_independent_review_packet_28.py` của Dũng, vì file này không có trong repo hay trong gói. Mọi giá trị đều đọc lại từ nguồn gốc.

## Đã kiểm

| Hạng mục | Nguồn đối chiếu |
|---|---|
| Donor cũ: id, nhãn, sha256(func) | `demonstrations[0]` trong `bundles_recovered_joern_final_20261031/devign/validation/specs.jsonl` (nguồn mà `reconcile_donor_prompts.py` dùng dựng kho cũ) và `demo_ids` của run3 |
| Donor mới: id, nhãn, sha256(func) | `research_freeze_20261101/devign/donors.jsonl`, `cache/devign_new_bank.jsonl`, `demo_ids` của rerun và canonical |
| Prompt cũ | sha256 văn bản trong `prompts.jsonl` legacy = `old_prompt_sha256` = run3 |
| Prompt mới | sha256 văn bản trong `new_reference/B2/devign/validation/prompts.jsonl` = `new_prompt_sha256` = rerun = canonical. Phần trước demonstration giữ nguyên, chỉ đoạn donor đổi |
| Input lượt rerun | Dựng lại `prompt_set_sha256` `690ef401…` của bundle `donor_rerun_devign_validation.zip` từ 28 prompt new_reference theo thứ tự records: khớp |
| Score | logprob/s cũ khớp run3, logprob/s mới khớp rerun. s tính lại bằng sigmoid(logprob_1 − logprob_0) |
| Quyết định, argmax | Tính lại tại τ = 0,70 (`configs/thresholds.json` `devign\|B2\|42`). Đổi score 28/28, đổi quyết định 6/28, đổi argmax 3/28, đúng như phiếu |
| Năm bản output cũ | 28 dòng có cùng prompt hash, s và logprob trong cả năm nguồn ghi ở `mau_can_inference_lai_CURRENT.csv` |
| Canonical | Gói `runs/final/devign/validation/B2/42`: 28 dòng trùng record rerun; 2.704 dòng còn lại trùng run3; tổng 2.732 |
| Hash file | `old_records_sha256`, `new_rerun_records_sha256`, `rerun_threshold_lock_sha256` khớp blob trong git (xem lưu ý CRLF). `rerun_worker_sha256` khớp file worker I09 trong gói |
| Ràng buộc worker | `Runs-management/b2_rand_drive_manifest_20261102.json` (commit `c245664`, 02/11) ghi cùng output `kaggle_run_01` có: worker `7519872…`, records rerun `794aa82b…`, thresholds `c4273120…`, bundle `1bf8d837…` (= `bundle_sha256` trong `run_manifest`) |
| Ngưỡng | Khóa lại MCC trên lưới validation từ canonical: τ = 0,70, MCC 0,054734 (bằng lock rerun). Từ score cũ (run3) cũng ra τ = 0,70 (MCC 0,053226), nên đổi donor không làm dời τ |

## Lưu ý

- `Runs-management/donor_reconciliation_20261101/cache/` bị `.gitignore`, nên `devign_old_bank.jsonl` chỉ có ở máy Dũng. Donor cũ được kiểm qua `specs.jsonl` legacy, cũng là nguồn tạo ra kho cũ.
- Trên Windows, bản checkout bị đổi CRLF nên hash bản trên đĩa khác phiếu. Script băm blob `git show HEAD:<path>` (LF), và các blob này khớp phiếu.
- File `kaggle_inference.py` trong `kaggle_outputs_20261107/b2_rand_seed44_validation_latest/` có hash `8bf6c450…`. Đây là worker của version 07/11, không phải worker chạy rerun 02/11. Worker rerun được ràng buộc qua manifest Drive ngày 02/11.
- Trong 28 donor cũ, 5 donor không còn trong kho mới (đã loại khi làm sạch). 23 donor còn lại đổi do thứ tự retrieval trên kho mới thay đổi. Có 13/28 dòng mà nhãn donor mới khác nhãn donor cũ.
