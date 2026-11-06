# B1-H2 L4 100-sample pilot

This is an exploratory hardware/loadability pilot only. It does not fit a threshold, alter frozen prompt files, or contribute to confirmatory results.

## Inputs and artifacts

- Source: `D:/JUNIOR/LabThayTho/grace_15arms_prompts_and_clean_specs (1).zip`
- Source SHA-256: `9db0d3eebb66a2f83c1f9803ceb0192954a3dfe2c3de9515188a996ede84ed7b`
- Selection: 50 Devign + 50 ReVeal original Hiếu B1-H2 validation prompts, seed 42, sampled without replacement using selection seed `20261106`.
- Bundle: `bundles/b1h2_l4_100_sample_bundle.zip`
- Bundle SHA-256: `500b523dfe05623dc5d866c218f6100048527283f92c078ec486be928cb79b59`
- Prompt payload SHA-256: `7f77494714d279220f31698062ced5efa852105770959861ca2160d6777ad1fc`
- Notebook: `../notebooks/colab_l4_b1h2_100_sample_pilot_20261106.ipynb`

The original ZIP records were retained as-is for selected prompts. The 100-row sample is saved only in this pilot bundle. It is not added to the frozen 15-arm specs.

## Runtime configuration

- In Runtime → Change runtime type, select Runtime Version **2026.10 (Python 3.13.x)** and GPU **L4**, then reconnect. The first setup cell rejects a wrong Python major/minor or GPU before mounting Drive or installing packages. Colab 2026.10 is selected to match Kaggle’s Python 3.13 runtime family. Kaggle’s executed notebook recorded Python 3.13.15 and NumPy 2.1.3; The user-selected Colab 2026.10 runtime reported Python 3.13.16 and NumPy 2.1.3 in the observed session; the notebook accepts Python 3.13.x and records the exact patch. System RAM is recorded in `system_memory_gib.txt` when available.
- The notebook pins `llama-cpp-python==0.3.16`, `transformers==4.57.1`, `huggingface-hub==0.36.2`, `tokenizers==0.22.2`, `numpy==2.1.3`, and `scikit-learn==1.5.2`.
- It compiles llama.cpp CUDA for L4 compute capability 8.9 and requests all model layers on GPU with `n_gpu_layers=-1`.
- It preserves the Q4_K_M model SHA, tokenizer revision, 8,192 context, batch 256, seed 42, and canonical unconstrained first-token logprob scoring.
- The native llama.cpp load/offload report, runtime GPU details, package installation logs, load summary, and 100 per-row logprob records are written under `My Drive/GRACE-summary/B1H2-L4-pilot/l4_pilot_output/`.
- The session safety cap is 10 hours. Each completed row is flushed to Drive so an interrupted run can resume.

## Pending external steps

The bundle has been uploaded to `GRACE_B1H2_COLAB_L4_PILOT_20261106` in the user's Google Drive.

- Drive folder ID: `1EXnwBz9s1kkqKs2jchHzAiw5LaTr9Q9x`
- Bundle file ID: `1LWGkH3tmNgWml8s_JTR7A-0ynYb0__L_`
- Link: https://drive.google.com/file/d/1LWGkH3tmNgWml8s_JTR7A-0ynYb0__L_/view?usp=drivesdk
- The downloaded Drive copy matched the local bundle byte-for-byte at SHA-256 `500b523dfe05623dc5d866c218f6100048527283f92c078ec486be928cb79b59` (55,894 bytes). The local bundle was removed after this verification.

Colab execution is still pending; no L4 inference has run yet.

The Colab runtime is expected to report the offloaded layer count and GPU buffer sizes. If L4 cannot load all layers, switch the runtime to A100 or G4 and rerun; do not mix its outputs with confirmatory B1-H2 results.
