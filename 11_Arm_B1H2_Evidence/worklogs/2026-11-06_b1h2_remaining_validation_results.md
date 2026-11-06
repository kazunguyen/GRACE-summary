# B1-H2 remaining validation inference — Colab L4

## Run result

- Run completed on 2026-11-06. The last record timestamp is 06:37:54 UTC (13:37:54 GMT+7).
- Output status: `complete`, 4,905 expected and 4,905 written.
- Dataset counts: 2,682 Devign and 2,223 ReVeal; all records identify arm `B1-H2` and GPU `NVIDIA L4, 23034 MiB`.
- Compared with the continuation bundle: all 4,905 IDs match; zero duplicate, missing, or extra IDs; zero prompt hash mismatches.
- Compared with the earlier 100-row B1-H2 pilot: 100 + 4,905 = 5,005 unique IDs, zero overlap. Together they cover the original 5,005 validation prompts.
- Output records contain finite `logprob_0`, `logprob_1`, and `s` for all 4,905 rows.

## Raw greedy response note

The saved `raw` token was not `0` or `1` for 291/4,905 rows (5.93%): 142 Devign and 149 ReVeal. These rows still have finite binary label logprob scores and `s`; their raw greedy token was `Looking`. This is flagged by `response_valid=false` and should be retained in review rather than silently removed.

## GPU offload evidence limitation

- `llama-cpp-python==0.3.16` CUDA build completed successfully; the model file hash matched the pinned SHA-256 and the model loaded and produced all scores on the L4 runtime.
- `n_gpu_layers=-1` was requested, but `llama_cpp_model_load_offload.log` is 0 bytes, `layer_reports` is empty, and `all_layers_offloaded=false` in `load_summary.json`. Therefore this artifact does **not** verify that every model layer was placed on the GPU. `runtime_nvidia_smi.txt` was captured before model load and shows 0 MiB, so it cannot establish post-load GPU memory use either.

## Threshold status

The prompt bundle and inference records contain no ground-truth `label` field. This run completes validation inference but does not calculate validation metrics or freeze a threshold. Join the predictions to the preregistered validation labels by sample ID, then apply the preregistered threshold procedure. Do not use test labels for threshold selection.

## Artifacts

- Downloaded output ZIP: `colab_l4_b1h2_remaining_validation_20261106/downloaded_output/l4_remaining_validation_output.zip`
- Output ZIP SHA-256: `efd111b3a961687796a6018042db89a2da80deedecb786ccfa17c4e5b636e8d2`
- Output ZIP Drive file ID: `1RTJraQc3H5piI8V56y4pcNvGhYLiFM7v` — https://drive.google.com/file/d/1RTJraQc3H5piI8V56y4pcNvGhYLiFM7v/view
- Bundle SHA-256: `b696143190173b118f89b5f7e0dccbf90fc9411d019db4de719be2e30cf98137`
- Prompt payload SHA-256: `e4f2765732c1c02c344ca9839cd2230e696f24079c7a54ccf4e7c42fbab09fb7`
- Local integrity analysis: `colab_l4_b1h2_remaining_validation_20261106/output_analysis.json`

## Platform/runtime deviation from preregistration

The preregistered Kaggle execution uses 2×T4; both B1-H2 Colab runs used Google Colab Runtime Version 2026.10 with a single NVIDIA L4 (23,034 MiB), driver 580.82.07, CUDA toolkit 13.0.88, Python 3.13.16 and observed system RAM 52.96 GiB. The audited Kaggle runtime recorded Python 3.13.15. Model and tokenizer hashes, llama-cpp-python 0.3.16, Transformers 4.57.1, Hub 0.36.2, tokenizers 0.22.2, NumPy 2.1.3, scikit-learn 1.5.2, context, batch, seed and first-token logprob method matched. Python patch version, CUDA image and GPU architecture differ; treat the Colab work as platform-deviant exploratory validation, not a controlled L4-vs-2×T4 comparison. Actual full layer offload remains unverified because the captured llama.cpp load/offload log is empty (`all_layers_offloaded=false`).

The first 100 prompts were B1-H2, selected by mistake when the intended hardware comparison had been B2; they do not provide a valid cross-arm hardware comparison. These 100 plus the 4,905 continuation records cover the 5,005 original B1-H2 validation IDs, with no overlap. The prompt specs were not modified. No ground-truth labels are included in the inference rows, so threshold selection remains pending a join to the frozen validation labels. See `Runs-management/RUNS.md` I-12/I-13 and `CHANGES_AFTER_PREREG.md` for the deviation record.
