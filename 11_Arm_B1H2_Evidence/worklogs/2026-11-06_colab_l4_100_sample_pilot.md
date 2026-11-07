# 06/11/2026 — Chuẩn bị pilot B1-H2 100 mẫu trên Colab L4

## Mục tiêu

Kiểm tra khả năng nạp model Qwen Q4_K_M đầy đủ lên một GPU L4 và lưu log offload cùng logprob cho 100 prompt B1-H2 gốc. Đây là pilot thăm dò phần cứng, không phải inference xác nhận, không dùng để chốt ngưỡng và không đưa vào bảng kết quả confirmatory.

## Đầu vào và mẫu

- Dùng đúng `D:/JUNIOR/LabThayTho/grace_15arms_prompts_and_clean_specs (1).zip`, SHA-256 `9db0d3eebb66a2f83c1f9803ceb0192954a3dfe2c3de9515188a996ede84ed7b`.
- Lấy 50 prompt Devign và 50 prompt ReVeal từ `prompts/dry_run_validation_20261102/{dataset}/validation/B1-H2/42/prompts.jsonl`.
- Chọn ngẫu nhiên không hoàn lại bằng seed `20261106`, giữ prompt gốc và xác minh từng `prompt_sha256`.
- Không thêm 100 dòng này vào specs 15-arm đã đóng băng.

## Cấu hình trong notebook

- GPU yêu cầu: Colab L4; notebook dừng nếu `nvidia-smi` báo loại khác.
- Model: `ggml-org/Qwen3-Coder-30B-A3B-Instruct-GGUF`, Q4_K_M; SHA-256 khóa theo preregistration `f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335`.
- Tokenizer: `Qwen/Qwen3-Coder-30B-A3B-Instruct`, revision `b2cff646eb4bb1d68355c01b18ae02e7cf42d120`.
- `llama-cpp-python==0.3.16`, build CUDA SM 8.9; `n_ctx=8192`, `n_batch=256`, `n_gpu_layers=-1`, `logits_all=True`, seed 42.
- Các package inference ghim theo lock/notebook hiện hành: NumPy 1.26.4, Hugging Face Hub 0.36.2, tokenizers 0.22.2, Transformers 4.57.1, scikit-learn 1.5.2.
- Ghi log `logprob_0`, `logprob_1`, `s`, greedy token và thời gian từng mẫu; lưu native stdout/stderr của llama.cpp để kiểm tra số layer offload và kích thước buffer CPU/GPU.
- Giới hạn phiên: 10 giờ; ghi từng record xuống Google Drive để có thể tiếp tục nếu runtime dừng.

## Trạng thái

Đã tạo notebook và bundle tại arm B1H2. Bundle SHA-256 là `500b523dfe05623dc5d866c218f6100048527283f92c078ec486be928cb79b59`; payload prompt SHA-256 là `7f77494714d279220f31698062ced5efa852105770959861ca2160d6777ad1fc`.

Đã upload vào folder Drive `GRACE_B1H2_COLAB_L4_PILOT_20261106` (folder ID `1EXnwBz9s1kkqKs2jchHzAiw5LaTr9Q9x`). Bundle file ID `1LWGkH3tmNgWml8s_JTR7A-0ynYb0__L_`; link https://drive.google.com/file/d/1LWGkH3tmNgWml8s_JTR7A-0ynYb0__L_/view?usp=drivesdk. Tải ngược bản Drive và xác nhận 55,894 bytes cùng SHA-256 `500b523dfe05623dc5d866c218f6100048527283f92c078ec486be928cb79b59`; sau đó đã xóa bundle local và file tải kiểm chứng. Notebook đã được cập nhật với link Drive và đường dẫn mount chính xác.

Chưa chạy trên Colab; chưa có output inference hoặc log offload thực tế.

Khi chạy: nếu L4 nạp đủ model, giữ nguyên log và xem đây là kết quả pilot riêng. Nếu không load hoặc không offload đủ layer, chuyển runtime sang A100/G4 rồi chạy lại cùng bundle; không gộp kết quả giữa cấu hình GPU.


## Run-readiness correction (2026-11-06)

The current Colab default runtime can use Python 3.13.18, which is incompatible with the pinned NumPy 1.26.4. Updated the notebook and its builder to require Colab Runtime Version 2026.07 / Python 3.12.13 and GPU L4, with a preflight before Drive mount and package installation. The later runtime cell records system RAM and GPU/compiler details. No package/model/prompt pins or uploaded bundle contents changed. Colab’s official past-runtime FAQ lists 2026.07 as Python 3.12.13 and says past runtimes can be selected from Runtime → Change runtime type.


## Kaggle environment comparison correction (2026-11-06)

A direct inspection of the executed B2-flip/B2-rand Kaggle notebook showed Python 3.13.15 and, after install, `llama-cpp-python==0.3.16`, `transformers==4.57.1`, `huggingface_hub==0.36.2`, `scikit-learn==1.5.2`, `numpy==2.1.3`. The earlier 2026.07/Python 3.12.13 + NumPy 1.26.4 recommendation did not match the recorded Kaggle runtime and has been corrected. The Colab pilot now targets 2026.10/Python 3.13.18 and NumPy 2.1.3, with other pinned packages retained. Python patch version differs because Colab and Kaggle publish different runtime images; package versions and model/data/prompt hashes remain locked.


## Colab GPU detection correction (2026-11-06)

The first Colab launch passed the Python 3.13.18 check but failed because `nvidia-smi` was not found on PATH. Updated the setup preflight to locate `nvidia-smi` at standard CUDA paths and fall back to `torch.cuda` for GPU detection. Runtime diagnostics now save GPU details from PyTorch if `nvidia-smi` is absent, and fail early with a clear message if no L4/CUDA compiler is available. Notebook JSON and all code cells parse; the revised preflight has not yet been executed on Colab.


## CUDA package import correction (2026-11-06)

A Colab run reached the model-load cell with `ModuleNotFoundError: llama_cpp`. Added an explicit package-presence guard with a message to run the preceding CUDA build/install cell after a runtime reset. README/notebook startup text now says to rerun cells from the top after reconnect; plain CPU `pip install` is not the intended setup.


## Colab Python patch preflight correction (2026-11-06)

The user selected Colab Runtime Version 2026.10, but the actual kernel reported Python 3.13.16. Earlier Colab metadata indicating 3.13.18 was stale/did not match that live session. Relaxed the notebook guard to require Python 3.13.x rather than the exact patch, and the runtime log still records the observed exact version. Package pins, including NumPy 2.1.3, remain enforced.


## Colab L4 pilot output and Kaggle comparison (2026-11-06)

### Downloaded output

- Drive folder: `GRACE_B1H2_COLAB_L4_PILOT_20261106` (ID `1EXnwBz9s1kkqKs2jchHzAiw5LaTr9Q9x`).
- Downloaded `l4_pilot_output.zip` (Drive file ID `1mzdAquFnSIOr38n4W5nZJGKFQtuiq3kK`) to `colab_l4_pilot_20261106/downloaded_output/l4_pilot_output.zip`.
- Local SHA-256: `9da2c0c67d382c769f0db735bb73211592605c329a02f8800a81ba2fe3c301f8`.
- Status: 100/100 records complete, 50 Devign + 50 ReVeal. Model SHA-256 matches the registered Q4_K_M model. Runtime recorded Python 3.13.16, one NVIDIA L4 (23,034 MiB), driver 580.82.07, CUDA 13.0, `llama-cpp-python==0.3.16` and pinned inference packages.
- 96 records have raw `0`/`1`; 4 raw responses are `Looking`, so `response_valid=false` for those rows although logprob scores were produced.
- **GPU offload is not independently verified by this output:** `load_summary.json` reports `all_layers_offloaded=false`, no parsed layer reports, and `llama_cpp_model_load_offload.log` is empty (0 bytes). The run requested `n_gpu_layers=-1` and completed all records, but the retained artifacts do not prove the actual layer placement.

### Comparison against available Kaggle results

The available overlapping Kaggle validation records are arm B2/B2-flip/B2-rand, not B1-H2. Across the 100 pilot IDs, the local B2 validation output contains all 100 IDs and the same model SHA, but **0/100 prompt hashes match** the Colab B1-H2 pilot. Example `devign:validation:1091`: pilot prompt hash starts `b697a578…`, Kaggle B2 hash starts `d54289dc…`.

For orientation only, a descriptive comparison with the downloaded Kaggle B2 run (`downloaded_output_20261101_run3`) gives 73/100 `pred_argmax` agreements, median absolute `s` difference 0.0552, mean 0.2405, and 43/100 differences above 0.1. These numbers mix B1-H2 and B2 prompts; they **cannot measure GPU-induced drift** or support a claim that L4 and 2×T4 disagree. A valid hardware comparison requires rerunning the exact same 100 B1-H2 prompts (same `prompt_sha256`) on Kaggle 2×T4, then comparing outputs by ID/hash.


### Exact sample-set verification

Re-downloaded the uploaded 100-prompt bundle temporarily and compared it row-by-row with the Colab `records.jsonl`: 100/100 IDs match and 100/100 `prompt_sha256` values match. The output manifest prompt-set SHA also equals the source bundle manifest SHA (`7f77494714d279220f31698062ced5efa852105770959861ca2160d6777ad1fc`). The temporary bundle copy was removed after verification. Thus the Colab run used the requested exact 100-prompt sample; the nonmatching hashes are only when compared against Kaggle B2 outputs.

## Correction: the pilot used the wrong arm for the requested GPU comparison (2026-11-06)

The earlier statement that the 100-row B1-H2 pilot was the "requested exact" comparison set was wrong. The user asked for a 100-sample pilot from `01_Author_Baseline_Unified`, which is the B2 arm. The bundle builder instead hard-coded the B1-H2 seed-42 validation prompt members. The Colab output matches its own bundle, but does not match B2 prompts on Kaggle. The earlier descriptive comparison statistics between those outputs are withdrawn and must not be interpreted as GPU-induced drift. This pilot does not answer the requested L4-vs-Kaggle comparison.

## Remaining B1-H2 validation inference bundle (2026-11-06)

Created a continuation bundle from the same frozen source archive and B1-H2 seed-42 validation prompt members. The source contains 5,005 validation prompts (2,732 Devign; 2,273 ReVeal). The completed L4 pilot has 100 unique IDs; all 100 IDs and prompt hashes were verified against the frozen source and excluded exactly once. The continuation bundle contains the other **4,905** prompts: 2,682 Devign and 2,223 ReVeal. The frozen source/specs were not changed. This continuation completes validation; threshold selection happens only after full validation inference is complete.

- Bundle: `colab_l4_b1h2_remaining_validation_20261106/bundles/b1h2_l4_remaining_validation_bundle.zip`
- Bundle SHA-256: `b696143190173b118f89b5f7e0dccbf90fc9411d019db4de719be2e30cf98137`
- Prompt payload SHA-256: `e4f2765732c1c02c344ca9839cd2230e696f24079c7a54ccf4e7c42fbab09fb7`
- Source archive SHA-256: `9db0d3eebb66a2f83c1f9803ceb0192954a3dfe2c3de9515188a996ede84ed7b`
- Notebook: `notebooks/colab_l4_b1h2_remaining_validation_20261106.ipynb`
- Drive folder `GRACE_B1H2_COLAB_L4_REMAINING_20261106`: ID `1_46x-8eoPasQwYy7jFWKqA6sf43yFqSi`
- Bundle Drive file ID: `1FuYcMkEuMBAFYexmg0c1HL5BxPB_L_Vg`; link: https://drive.google.com/file/d/1FuYcMkEuMBAFYexmg0c1HL5BxPB_L_Vg/view
- Notebook Drive file ID: `1jtFT0xstyBFX3dgRUp2RorKiRtd8AAxz`; link: https://drive.google.com/file/d/1jtFT0xstyBFX3dgRUp2RorKiRtd8AAxz/view

The notebook uses Colab Runtime Version 2026.10 / Python 3.13.x and L4, with the established model and package versions. It caps each inference session at 9 hours, writes each completed row to the mounted Drive output, skips checkpoint IDs already written after checking their prompt hashes, and can be rerun after a disconnect. The 9-hour limit starts after model loading, so setup/download time is not counted. The bundle and notebook were uploaded to the new Drive folder. The notebook has not yet been run on Colab.

Final notebook review: cleared all copied pilot cell outputs, confirmed all code cells compile, added the true validation `label` to each row, and marked continuation records `validation_only=true` / `pilot_only=false`. Updated the Drive notebook file in place after these corrections. Bundle Drive MD5 `fd477ebdf4c920dbf3457c24fbe52aa0` matches the local bundle; Drive reports 2,480,678 bytes.

## Colab CUDA build logging fix (2026-11-06)

The user reported `OSError: [Errno 107] Transport endpoint is not connected` at `log.write(line)` while compiling `llama-cpp-python` (nvcc source `cpy.cu`, build line 39/183). The failure was the setup cell writing verbose pip/compiler output to `OUT/install_llama_cpp_cuda.log` on mounted Google Drive; the trace does not show a CUDA compiler error. Updated the Drive notebook so dependency/build logs stay on `/content/b1h2_l4_setup_logs`, compiler progress is printed periodically, and logs are copied to Drive only after each subprocess exits, with local copies retained if Drive is unavailable. Cleaned inherited outputs, recompiled all notebook code cells, and updated the notebook file in Drive (same file ID). On the user's current runtime, first remount Drive and check whether `llama_cpp` finished installing; if installed and CUDA offload is available, continue without rebuilding. Otherwise restart from the top using the updated notebook so the build no longer depends on Drive FUSE.

## B1-H2 remaining-validation cell fix: missing label key (2026-11-06)

The first edited inference cell treated `label` as mandatory in each prompt object and raised `KeyError: 'label'`. The frozen inference bundle does not promise a label field; labels are joined later for evaluation. Replaced the cell so it writes the standard provenance and prompt hash fields, copies `label` only if present, and continues scoring without it. The replacement cell compiled with the notebook. Updated the same notebook file in Drive. User can paste the replacement into the current live runtime and rerun the cell; prior model setup remains in memory.

## Remaining validation output downloaded and audited (2026-11-06)

See `worklogs/2026-11-06_b1h2_remaining_validation_results.md` for the full report. The downloaded ZIP contains 4,905/4,905 records; all IDs and prompt hashes match the bundle. Together with the separate 100-row B1-H2 pilot, the two outputs cover 5,005 unique validation IDs with no overlap. 291 raw greedy responses are `Looking` (scores are still finite). The model ran on L4 with the pinned model hash, but full GPU layer offload cannot be confirmed because the retained offload log is empty and `all_layers_offloaded=false`. Records omit labels; threshold fitting remains pending a join to the frozen validation labels.
