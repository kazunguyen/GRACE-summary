# B3 verified-patch validation census completed

- Date/status snapshot: 2026-11-09 18:00 Asia/Saigon (11:00 UTC), Kaggle kernel version3 COMPLETE.
- Devign validation seed42: 2,732/2,732; REVEAL validation seed42: 2,273/2,273; total 5,005. The 560 REVEAL records pending from the checkpoint were completed.
- Independently checked each dataset's sealed input root/bundle, run identity, census IDs, prompt hashes, record identities and score/logprob consistency with `b3_delivery_runtime.checked_records`. Evaluation reports 100% valid score/response coverage.
- Runtime sessions referenced by records passed exact seven-package contract and runner checks, native load/offload log checks (two Tesla T4, 49/49 layers, locked context/batch settings), and build-log SHA match against runtime provenance. Contract SHA-256 `4c9c3bcff5e9fd32532d7edf85df7a961e45ec9c64bee3df8833d986a2eb276e`.
- Raw-score AUROC: Devign0.5304264374; REVEAL0.5418507490. Packaged default evaluation metrics are not threshold tuning. New B3 validation-derived thresholds still need to be computed using the registered formula and then locked separately by dataset. No test inference or threshold changes were made.
- Audit details: `Runs-management/b3_lznt_resume_retry_20261109/b3-new-dual-resume-v2-retry1/execution_audit.json`; status: adjacent `STATUS.md`.
