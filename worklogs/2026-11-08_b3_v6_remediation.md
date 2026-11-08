# B3 v6 — delivery fixes and REVEAL provenance recovery

User requested completing the fixes needed to run the new B3 algorithm on Devign and REVEAL. Work performed on `hieu`; no commit/push or GPU launch in this task.

## Completed

- New immutable delivery folder `Runs-management/b3_verified_patch_v1/release_20261108_v6/`; kept v5 and frozen assets unchanged.
- Fixed real loader schema with a one-to-one frozen-label join; prompt content fingerprint unchanged. Notebook embeds pinned runtime/helper/worker/shared IO code and pins the independent inference input manifest.
- Shared loader validates packed and unpacked inputs, all required members and scope; ambiguous/missing/corrupt inputs fail before model loading. Restore validates checkpoint manifest, safe paths, run identity, records and referenced provenance/native logs; preserves score bytes. Native GPU parser accepts actual `using device CUDA... (Tesla T4)` format while retaining full offload/context/batch gates.
- Final verification: **101 passed**, plus a negative admission check showing the actual empty review templates cannot publish a pool. Logs kept in `v6_acceptance_verified_20261108`. Earlier failed checks retained in separate acceptance logs: one new lexical boundary test exposed unterminated block-comment handling, then implementation was fixed and final suites passed.
- Acquired public upstream ReVeal scripts at pinned revision and a bounded CSV byte range, recovered source_id mapping for curl `alloc_addbyter`, and verified actual fix/parent/full patch against frozen REVEAL train16061/17887. Both donors have `keep_in_bank=true`. Original actual diff was not rewritten to fit tokenized donor formatting.
- Added explicit source lexical-mapping validation and a machine-verified but unreviewed packet. Payload: `537b1732aa7cc6dbc3821044275e1364568c6a0893999262b9e5f1264a1c71a7`. Two independent final human reviews are still required; requested them from the user with the exact packet path. No replacement of human reviewers by agents.
- Prepared private-account launch request with T4 shape and existing model kernel source. Read-only account check confirms accessible source version1. Account has approximately23.6min quota left, so a9h request is explicitly blocked.
- Uploaded only the accepted Devign input ZIP to PRIVATE dataset `huuhieu3333/grace-b3-v6-devign-inputs`; status ready and server metadata `is_private=true` confirmed. No kernel was pushed or GPU session opened. Canonical launch configuration is the prepared SDK request, which adds the model kernel source and shape to the base metadata template.

## Not yet complete

- REVEAL pool admission pending two genuine reviews bound to final payload and mapping. Admission CLI validates all submitted forms, consensus, clean bank/source evidence and atomically publishes into a new directory. It cannot render or launch an unreviewed pair.
- Full REVEAL validation prompt census2.273 and its input/delivery release follow successful admission. No reuse of the Devign prompt audit for REVEAL.
- Native B3 runtime acceptance and GPU validation have not run. Use sufficient quota on the intended account; do not silently switch account or send private data elsewhere.
- New per-dataset thresholds and test inference follow full validation acceptance. Frozen threshold configs stay unchanged.

The final readiness report is `Runs-management/b3_verified_patch_v1/v6_acceptance_verified_20261108/REMEDIATION_REPORT.md`.
