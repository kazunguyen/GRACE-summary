# B3-nodiff Kaggle validation delivery

Date: 2026-11-09 (Asia/Bangkok)
Status: Prepared; inference not launched.

## Scope

Prepared a Kaggle notebook and data package for B3-nodiff validation, seed 42, using the B3 prompts Hieu delivered on 2026-11-08. The scope is Devign validation (2,732) and ReVeal validation (2,273), 5,005 prompts total. No test prompts or labels are included in the run inputs.

## Prompt transform

For each prompt, removed the complete explanation block beginning at `Key difference:` and ending immediately before `Answer (0 or 1):`. This removes the associated `Security rationale` while preserving the vulnerable and non-vulnerable demonstrations. Target code, graph, examples, answer instruction, target labels, IDs, and order remain unchanged. Recomputed each prompt SHA-256. All 2,732 Devign and 2,273 ReVeal rows have the expected count and no remaining `Key difference:` or `Security rationale:` marker.

The bundle carries the reviewed demonstration evidence:
- Devign: `case_08_ffmpeg_can_safely_read_8614_26054`; two approval forms included.
- ReVeal: `case_reveal_curl_alloc_addbyter_16061_17887`; two approval forms included.

## Runtime lock integration

Used the exact user-designated lock bytes from `Runs-management/kaggle_outputs_20261107/b2_rand_seed42_test_latest/b2_rand_seed42_test/inference_runtime_lock.json`, SHA-256 `85d8770839f80260cdc7c27b27b6cce6bf8815675c8593db68fb102589c5cbd6`. The Kaggle notebook verifies the lock SHA and internal integrity seal. It derives the package pins/build flags/model SHA/tokenizer revision and full llama-cpp constructor from that lock, verifies the expected two-T4 profile and full 49-layer GPU offload, refuses prompt/tokenizer mismatches or silent truncation, and records the required runtime provenance. Inference uses first-token full-vocabulary logits and the locked unconstrained score; the constructor uses the lock's inference seed sentinel, distinct from prompt seed 42.

## Artifacts

- Notebook: `14_Arm_B3_NoDiff/notebooks/02_kaggle_qwen_q4_b3_nodiff_validation_runtime_locked_20261109.ipynb`
- Input archive: `14_Arm_B3_NoDiff/kaggle_delivery_20261109/grace_b3_nodiff_validation_inputs.zip`
- Input archive SHA-256: `6e8a5ff58b4e09bb826abcd0037b6f5f6933b3754212fc830422c41651ff0ee3`
- Notebook SHA-256: `87a7aa0669daea148d945aa0d2fd3f9c763ec00a759a281d351ddfb82522eaa4`

The notebook streams the GGUF file while calculating its SHA-256, avoiding a full model-sized RAM allocation. Its input loader accepts Kaggle auto-extracted dataset files by validating the sealed delivery manifest and all member hashes; it also accepts the original ZIP when available. This fixes the initial notebook error that required the outer ZIP to exist under `/kaggle/input`. The notebook streams the GGUF file while calculating its SHA-256, avoiding a full model-sized RAM allocation. Its input loader accepts Kaggle auto-extracted dataset files by validating the sealed delivery manifest and all member hashes; it also accepts the original ZIP when available. This fixes the initial notebook error that required the outer ZIP to exist under `/kaggle/input`. The archive contains independently sealed dataset bundles, the exact runtime lock, helper/runner code, pair review evidence, and manifests. Both inner dataset bundles were validated against their manifests; notebook code cells compile; prompt counts, prompt hashes, member hashes, seals, and lock checksum were verified. This was local artifact validation only. No Kaggle execution/GPU acceptance or threshold fitting has occurred. The notebook writes separate Devign and ReVeal validation checkpoints for Kaggle download/resume.


## Follow-up: 10.5-hour validation window and threshold lock

At the user's request, increased the notebook's inference wall-clock budget from 9 to 10.5 hours while retaining the 300-second checkpoint reserve. After inference, the notebook now fits separate Devign and ReVeal thresholds only if both complete validation censuses are present and every expected ID, label, prompt hash, model hash, seed, and split matches. It applies the existing `validation_mcc_grid_v1` rules from `Runs-management/kaggle_outputs_20261105/b2_flip/validation_lock.py`: thresholds 0.01–0.99, maximize MCC, classify with `score >= threshold`, tie within 1e-9 by closest to 0.5 then lower value; degenerate MCC locks 0.5. The output `validation_threshold_lock.json` includes complete grid scores, validation record/evidence hashes, confusion matrix and accuracy at the selected threshold. Partial validation is checkpointed and threshold fitting is skipped. The notebook code cells compile; no Kaggle inference was run. Final notebook SHA-256: `87a7aa0669daea148d945aa0d2fd3f9c763ec00a759a281d351ddfb82522eaa4`.


## Follow-up: Kaggle input mount discovery

After the first extracted-input correction, the user's Kaggle run still found zero verified manifests even though the Input pane showed the dataset's extracted files. Replaced `Path.rglob` with `os.walk(..., followlinks=True)` for delivery manifest, archive, model, and checkpoint discovery. The manifest scanner now reports candidate paths and whether scope/runtime, member presence, or SHA-256 checks rejected them. This avoids silently hiding the rejection cause. All notebook code cells compile. No Kaggle run was initiated by the change. Final notebook SHA-256: `c8f087d367a004601c5373ddd141273a753ae09dac15216a78dd04d335b401a0`.


## Follow-up: Kaggle recursively extracts nested prompt ZIPs

The user's Kaggle log showed the outer `delivery_manifest.json` was found, but its two nested dataset ZIPs were absent. Kaggle had recursively extracted those ZIPs into directories. The outer-manifest verifier now allows those exact missing archive members only, then independently verifies the extracted `bundle_manifest.json` and every prompt/evidence member against the sealed inference input manifest. It rebuilds transport ZIPs for the unchanged runner and derives a sealed runtime input-root manifest that records both the originally declared archive SHA-256 and reconstructed transport SHA-256; prompt/member hashes and runner/helper identities stay pinned. The packaged runner already accepts this form after reconstruction. All notebook code cells compile. No Kaggle inference was launched. Final notebook SHA-256: `c2d92301a2f22c05bca695173f28e3c9b0872b2262b9311d7e2b1fa7bdef3bd1`.
