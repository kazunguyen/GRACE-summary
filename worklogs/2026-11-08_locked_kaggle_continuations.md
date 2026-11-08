# Authorized continuation of unfinished Kaggle arms — 2026-11-08

PI authorized continuing unfinished arms with runtime locks and fixing B1-full before restarting. Three **new private** kernels and private input datasets were created. Existing kernels/results and frozen protocol files were preserved.

| Work | Account / new kernel | Census | Imported | New target |
|---|---|---:|---:|---:|
| B1-shuf test, seeds 42/43/44 | [tomandjerry223/grace-b1-shuf-locked-20261108](https://www.kaggle.com/code/tomandjerry223/grace-b1-shuf-locked-20261108) | 15,018 | 0 | 15,018 |
| B3 + B3-nodiff validation | [lznt123/grace-b3-locked-resume-20261108](https://www.kaggle.com/code/lznt123/grace-b3-locked-resume-20261108) | 10,010 | 4,029 | 5,981 |
| B1-full corrected test | [huuhieu3333/grace-b1-full-budgetfix-20261108](https://www.kaggle.com/code/huuhieu3333/grace-b1-full-budgetfix-20261108) | 5,006 | 0 | 5,006 |

Launches were accepted as version 1 at 08:04 GMT+7. Status snapshots at 08:04–08:05 report `KernelWorkerStatus.RUNNING`, without a failure message. Remote-source readback at 08:05:53 confirms **every cell source matches local**, each kernel is private, its input/model sources are correct, and the saved machine shape is `NvidiaTeslaT4` (T4×2).

This is launch/source verification, not proof that the model has already loaded or that inference has begun. Kaggle output download returned no live files at the initial check. Native full-offload and per-session provenance must be accepted from actual outputs; do not upgrade a RUNNING API status to full-runtime certification.

## What changed

- B1-shuf: same frozen prompt bytes and seed-specific validation thresholds; GPU log guard accepts actual native CUDA0/CUDA1 T4 lines and retains 49/49/context/batch requirements. Six previous real-log replay checks cover rejection cases.
- B3: imports exactly the 4,029 accepted historical records unchanged in value. Every row has a migration checksum. The new runtime contract applies to newly inferred records only. Historical B3 pairing is not certified as the amended verified patch-pair method. Continue remaining 976 B3 REVEAL plus 5,005 B3-nodiff validation. No new threshold fitting/test launch.
- B1-full: fixed graph compaction and target-code budgeting. Reconstructed all 5,005 validation prompts exactly before preparing test. Of 5,006 test prompts, 4,753 change (2,590 Devign, 2,163 REVEAL). Fresh full test census avoids blending the historical over-budget run with the corrected renderer. Code ≤3,000, graph ≤1,500, chat maxima 4,572/4,576 plus 64-token reserve. Preserve the earlier 2,850 records and disclose the operational correction after test exposure. Thresholds remain Devign 0.99 / REVEAL 0.01.

## Lock enforcement and recovery

The manifest pins prompt files, threshold snapshots/self-seals, worker source, runtime contract and model. The exact package/source archive checks run before inference. Model loading requires the correct tokenizer/model hashes, explicit constructor values, two T4 IDs, 49/49 native offload and context/batch/microbatch values. Per-session evidence includes build log, native model log, compiled-library hashes, toolchain, pip freeze, GPU UUIDs/free VRAM and constructor settings.

Each new row references a hash-pinned provenance file. Resume rejects changed input/runtime identity, unproven new rows and altered imported historical records. Checkpoints include provenance/build/native evidence, are refreshed approximately every 60 seconds and at exit, and reserve 300 seconds before the nine-hour wall-clock limit. Future continuation must attach the matching `<kind>_locked_20261108_checkpoint.zip`; a checkpoint from another input/runtime identity is rejected. No test metric controls stopping.

Verification: 15 predeployment adversarial/parity/scoring checks passed. Required project suites: 37 passed. Full validation parity and test component budgets are in `Runs-management/locked_continuations_20261108/b1_full_corrected_v4/audit.json`. Delivery hashes, accepted launches, source readback and statuses are under each arm directory. No Git commit/push performed.

Operational tooling notes: the old CLI omits `machine_shape`; an isolated official `kagglesdk` 0.1.28 request explicitly sets T4×2 and remote readback verifies it. New `KGAT_` credentials use bearer authentication; legacy credentials use username/key. Initial 401 upload attempts occurred before this token-mode correction and did not create datasets. Credentials are not copied into notebooks or delivery reports.
