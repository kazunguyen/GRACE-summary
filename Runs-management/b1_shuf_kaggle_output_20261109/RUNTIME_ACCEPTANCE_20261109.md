# B1-shuf Runtime Acceptance

**Audit date:** 2026-11-09  
**Kernel:** `lznt123/grace-b1-shuf-resume-12290-20261109` (version 1)  
**Result:** **PASS under the B1-shuf locked runtime contract**

## Scope and evidence

The audit used the latest output pulled from Kaggle into this directory, the launch and remote-source readback records in `Runs-management/locked_continuations_20261108/b1_shuf_resume_lznt123_12290_20261109_v1/`, and the frozen `inference_runtime_lock.json` bundled with the output.

The Kaggle readback records `all_cell_sources_match: true`, private kernel, GPU enabled, `NvidiaTeslaT4`, and the intended checkpoint dataset as the only dataset source. The latest remote status is `KernelWorkerStatus.COMPLETE`, with no failure message. The downloaded `status.json` says `complete` and the final inference process exited with code 0.

## Census and output integrity

All six seed/dataset groups reached their frozen census counts. The 15,018 records were present in the downloaded JSONL files, with unique IDs within every group and each record carrying the expected seed, dataset, split, model hash, and runtime-contract hash.

| Seed | Devign test | REVEAL test |
|---|---:|---:|
| 42 | 2,732 / 2,732 | 2,274 / 2,274 |
| 43 | 2,732 / 2,732 | 2,274 / 2,274 |
| 44 | 2,732 / 2,732 | 2,274 / 2,274 |

## Runtime contract checks

- `inference_runtime_lock.json` SHA-256 matches the pinned contract: `85d8770839f80260cdc7c27b27b6cce6bf8815675c8593db68fb102589c5cbd6`; its canonical integrity seal also verifies.
- All four provenance sessions referenced by the final records match the contract and runner: `locked_1unwzglu` (665 records), `locked_7y4i70yp` (5,751), `locked_jm9x9thz` (2,728), and `locked_pynny8ji` (5,874).
- Each session records the six pinned packages at their exact versions, Python 3.13 on Kaggle Linux, the exact model SHA-256, the same runner and runtime-helper hashes, and the pinned `llama-cpp-python` source archive SHA-256.
- Each session records two Tesla T4 devices before and after model load. The native load/offload logs pass the contract checker: 49/49 layers offloaded, both T4 devices observed, and `n_ctx=8192`, `n_batch=256`, `n_ubatch=256` match the lock.
- Constructor settings match the lock, including `n_gpu_layers=-1`, `LLAMA_SPLIT_MODE_LAYER`, `main_gpu=0`, and `tensor_split=null`. This is the approved layer-splitting/free-VRAM policy; the contract does not promise a fixed layer ratio between GPUs.
- Build evidence records CUDA 13.0, driver 580.178.04, GCC 13.3, CMake 3.31.10, and the locked CUDA build flags.

## Acceptance boundary

The runtime passes the B1-shuf contract and has the provenance required for this run. The contract explicitly permits a Kaggle platform build and does not claim a bit-identical binary environment. Provenance records SHA-256 values for the compiled backend libraries, but Kaggle did not expose those installed shared libraries as downloadable output, so those binary hashes could not be independently recomputed locally. This limitation does not fail the contract; it means the result must not be described as an independently reproduced, bit-for-bit backend build.

## Verdict

**B1-shuf is runtime-accepted and complete for the registered 3-seed test census.** The earlier 12,290/15,018 checkpoint acceptance referred to the state before this final resume and is superseded by the output audited here.
