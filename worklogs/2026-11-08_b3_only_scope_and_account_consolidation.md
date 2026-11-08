# B3-only scope correction and consolidation

PI clarified B3 only; carrying over B3-nodiff from the historical combined notebook was an agent scope error.

Prepared `Runs-management/locked_continuations_20261108/b3_only/`:

- 5,005 B3 validation prompts; 0 B3-nodiff prompts.
- Exact prior B3 prompt bytes; worker/model/runtime identities unchanged.
- All 4,029 approved historical B3 rows retained unchanged; 976 REVEAL rows remain.
- Target account: huuhieu3333, alongside its B1-full run. B1-shuf stays on tomandjerry223. Thus two accounts instead of three, with separate T4×2 sessions per run.
- New input/worker/hash/census/legacy/syntax checks pass. Dataset and notebook hashes are in `b3_only/delivery.json`; this is a different identity from the old combined run. No combined-run checkpoint can silently bypass that identity check.

At 08:22 GMT+7, official quota API reported 40,377.5 seconds (~11.22 hours) remaining on huuhieu3333 and 30,866.7 seconds (~8.57 hours) on tomandjerry223. Two simultaneous runs consume the account-wide quota; this arrangement does not create additional GPU hours.

The old `lznt123/grace-b3-locked-resume-20261108` remains RUNNING at the latest 08:23 snapshot. Public GetKernel/status/output readbacks returned no current session ID; web readback was denied. Cancellation requires that ID. This limitation is also documented in [Kaggle CLI issue 1169](https://github.com/Kaggle/kaggle-cli/issues/1169). Requested PI cancel the exact old run or provide its session ID. Do not infer a session ID from the notebook ID or version number, and do not delete the notebook.

B3-only launch is gated on confirming old status COMPLETE, ERROR or CANCEL_ACKNOWLEDGED. Dataset staging can finish independently; no duplicate run is launched while waiting. After cancellation, retrieve any available checkpoint/output before deciding whether new B3 records can be migrated. Old historical pairing remains explicitly outside amended patch-pair certification.

## Resolution after PI cancellation

At 08:29 GMT+7, the official API confirmed `CANCEL_ACKNOWLEDGED` for the old combined run. Downloaded loose outputs contain 4,058 B3 rows: 2,732 Devign and 1,326 REVEAL. There are 29 newly inferred B3 rows and zero inferred B3-nodiff rows. The downloaded checkpoint ZIP is zero bytes and is not used for recovery.

`scripts/migrate_b3_only_checkpoint_20261108.py` validates the exact source input/worker/runtime identity, every row against its prompt/label/model, all original 4,029 row values unchanged, the 29 new rows' provenance and native/build log hashes, exact packages/constructor, two T4 IDs, 49/49 native offload and score/logprob consistency. It preserves the original evidence files and individual row identities. The original 4,029 historical rows remain outside full runtime-lock certification; the 29 locked rows retain their original input-manifest provenance.

The distinct delivery `Runs-management/locked_continuations_20261108/b3_only_migrated/` has 5,005 B3 prompts, 4,058 preserved records and 947 remaining REVEAL rows. It contains no B3-nodiff prompts. Hash-pinned source migration evidence is restored into the output/checkpoint tree by the notebook. Frozen integrity tests: 6 passed.

Private input dataset `huuhieu3333/grace-b3-only-resume-20261108-inputs-v2` became ready, and [B3-only](https://www.kaggle.com/code/huuhieu3333/grace-b3-only-resume-20261108) version 1 was accepted at 08:31 GMT+7 with requested `NvidiaTeslaT4`. The earlier non-migrated B3-only staging was not launched. B1-full and B1-shuf were still RUNNING at 08:31. Final statuses and exact remote cell/GPU-shape readback are saved in the migrated delivery directory; RUNNING does not alone establish a passed model-load gate.
