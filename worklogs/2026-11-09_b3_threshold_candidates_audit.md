# B3 new-algorithm validation and threshold candidate audit

- Validation census and runtime evidence were independently checked from local records/provenance: Devign2732/2732; REVEAL2273/2273; score/response coverage100%. Refer to `Runs-management/b3_lznt_resume_retry_20261109/b3-new-dual-resume-v2-retry1/execution_audit.json`.
- Recomputed thresholds from raw validation records using MCC over thresholds0.01..0.99, positive rule `s>=tau`, tie tolerance1e-9, nearest0.5 then lower. Full-grid second implementation agreed with `validation_lock.pick_threshold` on all99 MCC values per dataset.
- Candidates: Devign tau0.99, MCC0.0501474890867987, TP491 TN982 FP563 FN696; REVEAL tau0.01, MCC0.06487856711606896, TP189 TN383 FP1680 FN21. Both tie sets contain only the selected point.
- Candidate artifacts are not official locks. Per execution-plan Step12, full-grid review and PI/governance confirmation of applying a threshold to amended B3 scope precede sealing and test. Input roots do not claim a new scope-ratification timestamp.
- No test data were read, no test was run, and frozen `configs/thresholds*.json` were not modified. Report: `Runs-management/b3_lznt_resume_retry_20261109/b3-new-dual-resume-v2-retry1/threshold_candidates_20261109/THRESHOLD_CANDIDATE_AUDIT.md`.
