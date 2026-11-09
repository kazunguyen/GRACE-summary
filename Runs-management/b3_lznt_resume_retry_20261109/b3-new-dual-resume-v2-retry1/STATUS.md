# B3 new algorithm validation resume ? current status

## Current update: thresholds LOCKED, 2026-11-09

Separate release: `../../b3_verified_patch_v1/threshold_release_20261109_v1/`. Devign tau*=0.99; REVEAL tau*=0.01. Full validation grids and all three score-referenced runtime sessions were rechecked. Original five-notebook ZIP core policies match; the current contract adds scipy==1.16.3. Runtime: two T4, CUDA0:25/CUDA1:24, 49/49 GPU layers, n_ctx8192, batch/ubatch256. Direct user instruction authorizes this threshold seal. Test delivery remains to be prepared/audited; no test launched. See `../../b3_verified_patch_v1/THRESHOLD_LOCK_ACCEPTANCE_20261109.md`. The candidate-only text below is the earlier snapshot.

- Kernel: [lznt123/grace-b3-checkpoint-resume-v2](https://www.kaggle.com/code/lznt123/grace-b3-checkpoint-resume-v2), version 3, `COMPLETE` at 2026-11-09T11:00:00Z (18:00 Asia/Saigon).
- Method: `b3-verified-patch-v1`; seed 42; fixed Devign then REVEAL order.
- Census: Devign 2,732/2,732; REVEAL 2,273/2,273; total 5,005/5,005. All records have valid scores and responses; response coverage 100% on both.
- Independent record/input/run-identity checks: PASS. Native two-T4/49-of-49 offload and 7-package runtime checks: PASS for all runtime sessions referenced by records. Runtime contract SHA-256: `4c9c3bcff5e9fd32532d7edf85df7a961e45ec9c64bee3df8833d986a2eb276e`. Build-log hashes match provenance.
- Validation AUROC (raw score): Devign 0.530426; REVEAL 0.541851. The bundled `evaluation.json` metrics use the worker's existing default evaluation. New validation threshold candidates have now been computed from the raw B3 validation records and independently cross-checked; official lock remains pending PI/governance review. No test inference was run.
- Full audit receipt: [execution_audit.json](execution_audit.json). Raw records, manifests, checkpoints and runtime evidence are in `remote_output/`.

## Validation threshold candidates

- Devign candidate: `tau*=0.99`, validation MCC `0.0501474890867987`, TP/TN/FP/FN `491/982/563/696` (unique tie).
- REVEAL candidate: `tau*=0.01`, validation MCC `0.06487856711606896`, TP/TN/FP/FN `189/383/1680/21` (unique tie).
- Both candidates use the prescribed grid `0.01..0.99`, score comparison `s >= tau`, and MCC tie rule. The independent sweep matched the existing optimizer on all 99 grid points for each dataset. Full grids and identity hashes are stored in `threshold_candidates_20261109/`.
- Candidate only; it is not a test lock. Per plan Step 12, PI/governance review and confirmation to apply the amended B3 scope must precede sealing a separate lock. Frozen threshold files were not changed.
