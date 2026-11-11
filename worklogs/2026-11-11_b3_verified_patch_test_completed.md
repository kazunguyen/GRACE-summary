# B3 verified-patch-v1 test completed — 2026-11-11

## Run

- Kaggle notebook: `duchuynguyen1802/grace-b3-verified-patch-test-10h-ipynb`.
- Arm/method: ordinary B3, `b3-verified-patch-v1`, seed 42; this is not B3-nodiff.
- Kaggle worker state: `complete`; `timed_out=false`.
- Runner status timestamps: start `2026-11-10T09:51:12.384806Z`, completed `2026-11-10T19:10:43.007144Z`; local Asia/Bangkok `2026-11-10 16:51:12` to `2026-11-11 02:10:43`. Elapsed runner time 9h19m30.6s. Notebook session deadline was 10h from session start; 300 seconds reserved for checkpointing.
- Census: Devign 2,732/2,732; REVEAL 2,274/2,274; total 5,006/5,006.
- Both datasets are marked complete in `status.json`; both output manifests match their frozen B3 test identities. IDs are unique, every score is finite and in [0,1], and records contain no target-label fields.
- Validation-fitted thresholds were applied without refitting: Devign τ=0.99; REVEAL τ=0.01. Sealed threshold lock files were not changed.

## Runtime evidence

- Active lock SHA-256: `bf1f859dc786e206a3c11d655b04b528dc68f59a15a82d4db894ac5944b0ac2e`.
- Canonical runtime integrity SHA-256: `d79396de5d37ca6c3123ac05ea122d665f5f9b252aa0b32ac2b5c464b68e338f`.
- Runtime provenance records Python 3.13.16, all pinned package versions, 2×Tesla T4, and the locked Qwen3-Coder-30B-A3B-Instruct Q4_K_M model hash.
- `model_load_offload.log` confirms 49/49 layers offloaded to GPU.
- The sealed validation threshold identities retain the previous raw runtime lock SHA `4c9c3bcff5e9fd32532d7edf85df7a961e45ec9c64bee3df8833d986a2eb276e`. Its parsed contents and canonical seal are identical to the active lock above; the run manifests separately record the active runtime SHA and the validation-identity SHA.

## Output artifacts and checks

- Downloaded using `kaggle kernels output duchuynguyen1802/grace-b3-verified-patch-test-10h-ipynb -p Runs-management/kaggle_outputs_20261111/b3_verified_patch_test_10h`.
- `status.json`: `Runs-management/kaggle_outputs_20261111/b3_verified_patch_test_10h/b3_test_release_20261110/status.json`.
- Devign records SHA-256: `20a31d31e7ae066babe85d0e458f0ccbec16c73ea118c4b9e6779c70df5735b4`.
- REVEAL records SHA-256: `b832b007c27a2b42d5e72a61215cf98f2662ef2e013a034f97c6ab111915f047`.
- Independent local audit checked manifest identity, frozen prompt/member hashes, threshold-lock seals/values, record counts, unique IDs, valid score range, and no label leakage. All checks passed.
- Test metrics were not calculated in this run; labels remain local and the shared final evaluator was not run. Do not infer AUROC/MCC from this inference-only output.
