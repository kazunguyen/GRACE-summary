# 2026-11-07 — B2-rand test Input correction and configuration audit

Both seed42/seed43 notebooks accept the original ZIP, preserved inner ZIPs, or Kaggle's recursive extraction of the inner ZIPs into `seed_N/{dataset}_test/{bundle_manifest.json,prompts.jsonl,threshold_lock.json}`. Recursive extraction mode verifies each file's SHA-256 against hashes derived from the original frozen bundle before parsing. The notebook also verifies threshold integrity, row count, prompt hashes, model hash and tokenizer. Missing or mismatched members produce diagnostics listing candidates and visible files. No Kaggle GPU execution was performed.

The first Kaggle rerun confirmed extraction and prompt verification but then failed in the runner with `FileNotFoundError` because the unzipped bytes had not been materialized back to the temporary ZIP path passed to the inference script. Both notebooks now write a local temporary ZIP from the already hash-verified members and use the parsed threshold map in finalization, avoiding another fragile ZIP open. This exact Kaggle mount layout was replayed locally through the runner-input handoff for both seeds; GPU inference remains unverified.

Compared with 06_Arm_B2_Rand/notebooks/02_kaggle_qwen_q4_b2_rand.ipynb and 04_Arm_B2_Flip/notebooks/02_kaggle_qwen_q4_b2_flip.ipynb:

| Item | Finding |
|---|---|
| Model | B2-rand validation/test use GGUF SHA f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335, Q4_K_M |
| Backend source release | llama-cpp-python 0.3.16; same CUDA SM75 build flags in the three inspected notebooks. Compiler/CUDA image and source distribution hashes are not fully pinned, so exact build identity across platforms is not guaranteed. |
| Python packages in test | numpy 2.1.3, transformers 4.57.1, huggingface_hub 0.36.2, tokenizers 0.22.2, scikit-learn 1.5.2; matches B2-rand validation pins |
| Tokenizer/prompts | Frozen tokenizer repo+revision from inner manifest; prompt bytes, per-row prompt hashes, HF/GGUF chat-token equivalence checked. Different arms intentionally have different prompt contents. |
| Scoring | Direct last-position unconstrained logits; float64 normalization; s=exp(lp1-logaddexp(lp0,lp1)); greedy raw token; no sampled generation |
| Context/batch | n_ctx=8192, n_batch=256, logits_all=True, n_gpu_layers=-1; matches inspected Kaggle constructors |
| Inference seed | B2-rand validation/test retain llama.cpp default 4294967295. B2-flip explicitly uses 42. Not globally identical; changing B2-rand test alone would break its validation configuration. |
| Other-arm package gap | B2-flip source inspected does not explicitly pin huggingface_hub, tokenizers or NumPy in its dependency installation. No claim that every arm has identical full environments. |
| Checkpoint | Resume must use this arm and prompt seed; verifies model hash, prompt hash/label, threshold seal, tau and inference_seed. Weight checkpoint remains the pinned GGUF. |
| Test threshold | Inherits completed validation lock; no test fitting |

The delivery ZIP is unchanged. Exact cross-platform numerical equivalence is not established by this static audit; matched prompts and execution manifests are needed for that claim.
