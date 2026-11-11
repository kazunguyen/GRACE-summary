# B3-flip test seed 42 hoàn tất — 11/11/2026

## Kernel và tải output

- Notebook thực thi: [grace-b3-flip-test-20261110-v1.ipynb](../16_Arm_B3_Flip/grace-b3-flip-test-20261110-v1.ipynb).
- Kaggle kernel truy cập được: `quangdung1111/grace-b3-flip-test-20261110-v1`. Slug `quangdungnguyen/...` được đưa ban đầu trả về `kernels.get` permission denied; notebook/input metadata chỉ tới tài khoản `quangdung1111`, và dùng slug này tải output thành công.
- Lệnh tải: `kaggle kernels output quangdung1111/grace-b3-flip-test-20261110-v1 -p Runs-management/kaggle_outputs_20261111/b3_flip_test_20261110_v1`.
- Output lưu tại `Runs-management/kaggle_outputs_20261111/b3_flip_test_20261110_v1/`; gồm records, run manifests, status, runtime provenance, native offload log, inference/runtime source và log cài dựng backend.

## Census và threshold

| Dataset | N test | ID duy nhất | Khớp frozen test ID theo thứ tự | Score hợp lệ | τ kế thừa B3 | Label trong record |
|---|---:|---:|---:|---:|---:|---|
| Devign | 2.732 | 2.732 | Có | 2.732/2.732 | 0,99 | Không |
| ReVeal | 2.274 | 2.274 | Có | 2.274/2.274 | 0,01 | Không |

Kernel status là `complete`, `timed_out=false`, tổng 5.006/5.006 records. Không có raw response hoặc score invalid. Thresholds được kế thừa nguyên trạng từ validation B3; test không dùng để chọn lại ngưỡng. Chưa join test labels và chưa tính metric test.

## Runtime evidence

- Worker bắt đầu `2026-11-11T00:00:48.936440Z`, hoàn tất `2026-11-11T09:12:18.508894Z` (07:00:48–16:12:18 Asia/Bangkok).
- Runtime contract SHA-256: `4c9c3bcff5e9fd32532d7edf85df7a961e45ec9c64bee3df8833d986a2eb276e`; canonical integrity seal: `d79396de5d37ca6c3123ac05ea122d665f5f9b252aa0b32ac2b5c464b68e338f`.
- Model SHA-256 `f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335`; Python 3.13.16; pinned package versions khớp runtime provenance.
- Hai Tesla T4 được nhận diện; native `model_load_offload.log` ghi `offloaded 49/49 layers to GPU`.
- Status bundle SHA-256: `2b6f9fc0063b3905025c7e4ebab7000833639310ca9c906c357b18381861690f`.
- SHA-256 `records.jsonl`: Devign `5839ef22d4c2207c6bb48dab57b43bfc1ae734aa97789509043516554d964177`; ReVeal `72995122fcd76dc5e1e244214d3a234f197398eee35e1885568a83591942dee0`.
- SHA-256 `run_manifest.json`: Devign `2da513a526680dc33d1532530ad5c5ff92929785785254a8b1aed58b29a793be`; ReVeal `77a11c59448ddc14d438a4222fb2cf774abe35cd9363db6667624c703c8945c2`.

## Ledger

Đã ghi run này thành I-31 trong [RUNS.md](../Runs-management/RUNS.md). B3-flip là probe dùng cặp contrastive B3 nhưng đảo nhãn hai demo; validation riêng không chạy và test dùng đúng threshold B3 đã khóa. Kết quả hiện là inference census/runtime evidence, chưa phải bảng metric test vì labels vẫn được giữ ngoài output Kaggle.
