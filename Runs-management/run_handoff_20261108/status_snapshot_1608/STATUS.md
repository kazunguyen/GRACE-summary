# Kaggle status - 08/11/2026

Read-only live API snapshot. No kernels started, stopped or modified.

| Kernel | Status | Visible records | Checked (GMT+7) |
|---|---|---|---|
| huuhieu3333/grace-b1-full-budgetfix-20261108 | COMPLETE | 2732 + 2274 | 16:07:50 |
| huuhieu3333/grace-b1-full-test | ERROR | 2732 + 118 | 16:08:00 |
| huuhieu3333/grace-b2-rep-test | COMPLETE | 2732 + 2274 | 16:08:06 |
| huuhieu3333/grace-b3-only-resume-20261108 | COMPLETE | 2732 + 2273 | 16:08:14 |
| lznt123/grace-b1-shuf-test | ERROR | No published records | 16:08:45 |
| lznt123/grace-b3-locked-resume-20261108 | CANCEL_ACKNOWLEDGED | 2732 + 1326 | 16:08:48 |
| lznt123/grace-b3-validation | COMPLETE | 2732 + 1297 | 16:08:57 |
| tomandjerry223/grace-b1-shuf-locked-20261108 | RUNNING | No published records | 16:08:27 |
| tomandjerry223/grace-b2-labelonly-test | COMPLETE | 2732 + 2274 | 16:08:28 |
| tomandjerry223/grace-b2-nolabel-test | COMPLETE | 2732 + 2274 | 16:08:36 |

B1-full budgetfix is newly COMPLETE: 5,006 unique-per-group records (Devign 2,732; REVEAL 2,274). The downloaded status file reports 5,006 new records and zero legacy records. Completion timestamp: 2026-11-08 15:35:51 GMT+7. Records, identities, runtime contract, provenance and model offload log have been downloaded into this snapshot. This status check does not constitute a full semantic/runtime acceptance audit.

B1-shuf locked is RUNNING with zero published files. Its live inference count, checkpoint health and remaining time cannot be determined from this API snapshot; this is not evidence that zero samples have been processed.

B3-only is the historical algorithm validation run (5,005 rows), not b3-verified-patch-v1. Historical B2 runs remain COMPLETE; old ERROR/CANCELLED kernels are separate from current continuations.

Evidence: per-account snapshot.json and selected artifacts in account subfolders.
