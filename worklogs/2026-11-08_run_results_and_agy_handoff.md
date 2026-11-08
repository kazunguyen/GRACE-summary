# Worklog — completed results, active runs and AGY handoff

Snapshot: 2026-11-08 09:11:33 GMT+7. See [full run handoff](../Runs-management/run_handoff_20261108/RUN_STATUS.md) for the status table, metrics, limitations and next steps.

Published checked, byte-preserved B2-labelonly, B2-nolabel and B2-rep test results (15,018 records total) with original manifests/evaluations and threshold-lock snapshots. Fresh API queries confirm those three COMPLETE; B1-full corrected, B1-shuf locked and B3-only remain RUNNING, with no live files exposed. Old combined B3 is CANCEL_ACKNOWLEDGED, and old B3 validation is kernel-COMPLETE but incomplete in sample census.

The user requested AGY as the worker backend and explicitly prohibited GPT multiagent workers. Added the scoped AGY CLI controller and recorded actual task outcomes. Automatic review blocked an initial full-bank Devign delegation; it was not retried indirectly. The successful replacement sends schema-only code-generation tasks and executes reviewed code locally. No data-dependent stopping or inference/threshold changes were introduced by this discovery work.

AGY produced local scanner/test/fetcher/checklist artifacts; coordinator rejected and corrected unsupported guide changes. Twelve independent scanner tests passed, and frozen-bank scans reproduce 21,691/17,636 eligible donors and 26,700/33,947 unverified name-match combinations. There are no newly admitted pairs. Source recon hit certificate issuer verification errors; preserve this blocker rather than treating missing responses as negative security evidence.

Git handoff excludes credentials, full train snapshots, donor indexes, installed tooling, temporary files, raw download duplicates and model weights. Only accepted completed result copies plus relevant scripts, notebooks, audit metadata and worklogs are staged. Protected preregistration files and anchors remain untouched.
