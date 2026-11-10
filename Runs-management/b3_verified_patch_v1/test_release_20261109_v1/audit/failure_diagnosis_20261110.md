# B3 new-test failures and version 6 correction - 2026-11-10

## Version 2 and version 4

Versions 2 and 4 stopped in preflight before package installation, model loading, GPU/offload attestation, or inference. Version 4 printed no manifest candidates because it only searched immediate `/kaggle/input` children.

## Version 5: actual failure

The downloaded Kaggle log shows that the earlier diagnosis was incomplete: version 5 **did find the nested mount**. Preflight passed with manifest `/kaggle/input/datasets/lznt123/grace-b3-test-release-20261109-v1/test_release_manifest.json`, validated the expanded input, loaded all 2,732 Devign and 2,274 REVEAL rows with thresholds 0.99 and 0.01, and verified the pinned model path/hash. The locked seven package versions matched, and `nvidia-smi` reported two Tesla T4 GPUs.

The actual fatal error was `NameError: name 'INPUT_DIR' is not defined` in notebook cell `In [5]`. Preflight stored the validated input as `INPUT_SOURCE` but the worker launch passed `INPUT_DIR`. The worker never started; no model was loaded by the worker, no 49/49 layer placement was observed, no runtime provenance was written, and zero test records were produced. The two-GPU listing and CUDA backend availability are partial environment evidence only, not runtime acceptance.

## Version 6 local correction

The worker input directory is now explicitly defined from the validated expanded dataset. If Kaggle supplies only the pinned archive, the notebook validates archive and member hashes, extracts only safe relative paths into a fresh working directory, then re-reads and validates the complete member inventory before invoking the worker. Manifest lookup first checks the exact pinned Kaggle dataset mount and uses a symlink-following walk of the datasets mount only as fallback.

The notebook's runtime contract, model pin, package pins, worker, prompts, retrieval pools, thresholds, and inference command are unchanged. Code cells for runtime setup/build, GPU contract, and worker invocation remain identical to remote v5 except for the corrected input-directory binding in the preflight cell; no tests or scores were produced by v5. Version 6 was pushed to the same canonical kernel, Kaggle reports `RUNNING`, and remote readback confirms all five executable code cells match local. This does not certify worker startup, model loading, 49/49 GPU layer placement, runtime provenance, or inference; those gates remain pending live output.

Evidence: `live_output_v5/grace-b3-new-test-20261109-v1.log`, `remote_source_readback_v5/`, `kaggle_kernel/notebook.ipynb`, and `execution_manifest.json`.
