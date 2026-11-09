# B3 validation and threshold publication — 2026-11-09

Current result: B3 `b3-verified-patch-v1`, prompt seed42, completed validation Devign2732/2732 and REVEAL2273/2273. Separate threshold release: Devign0.99; REVEAL0.01. Runtime acceptance covers every score-referenced session, including resumed REVEAL. Classification remains amended/exploratory. Test delivery still requires preparation and audit before launch.

- [Result summary at locked thresholds](validation_results_summary.json). Bundled worker `evaluation.json` files use the earlier default decision threshold; do not confuse those metrics with this summary.
- [Acceptance report](../b3_verified_patch_v1/THRESHOLD_LOCK_ACCEPTANCE_20261109.md) and [sealed threshold release](../b3_verified_patch_v1/threshold_release_20261109_v1/release_manifest.json).
- [Final raw records and runtime provenance](../b3_lznt_resume_retry_20261109/b3-new-dual-resume-v2-retry1/remote_output/b3_new_dual_validation_resume_v2_20261109/).
- [Selection and publication scope](selection.json), [required CPU checks](tests.json), [full test output](required_checks.log).

Fetched origin and fast-forwarded `hieu` from40d49d4 to origin/baseline-unified daa1a25 (PR#25). No merge conflicts arose. Subsequent publication commit/push is recorded in Git history.

Prompt/checkpoint ZIPs, backend source archives and duplicate extracted prompt bundles stay local. Replaying input-dependent checks requires the frozen validation bundles and original runtime ZIP in the documented locations. No Kaggle credential/config is published. Historical preregistration files and thresholds are unchanged.
