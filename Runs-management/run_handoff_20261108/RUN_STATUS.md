# Kaggle run handoff — 8 November 2026

Latest status snapshot: **2026-11-08 approximately 16:08 GMT+7** (see `status_snapshot_1608/`). Read-only collection; no inference session was started/stopped by this handoff. B1-full runtime acceptance was completed later from its downloaded output.

## Previously published completed test arms

The following exact records, original evaluation/run manifests and validation threshold-lock snapshots are in `completed_results/`. All 15,018 records were rechecked against frozen test IDs/labels, score/logprob math, locked predictions and original manifest hashes. Metrics were recomputed and match original evaluations. These are descriptive full-census results; no new significance test or threshold optimization was performed.

**Runtime limitation:** these three historical runs are not certified as fully compliant with the newer runtime lock. Package/model/core constructor evidence passes, but verified source/build/native full-offload provenance is incomplete. Completion and numerical acceptance must not be presented as full runtime certification.

| Arm | Dataset | N | Locked τ | AUROC | MCC | BA | F1 |
|---|---|---:|---:|---:|---:|---:|---:|
| B2-labelonly | devign | 2,732 | 0.99 | 0.546233 | 0.084851 | 0.532157 | 0.301275 |
| B2-labelonly | reveal | 2,274 | 0.02 | 0.600540 | 0.119907 | 0.598596 | 0.230958 |
| B2-nolabel | devign | 2,732 | 0.98 | 0.526898 | 0.051784 | 0.525001 | 0.436444 |
| B2-nolabel | reveal | 2,274 | 0.21 | 0.572084 | 0.083533 | 0.569242 | 0.210291 |
| B2-rep | devign | 2,732 | 0.70 | 0.530473 | 0.059708 | 0.529326 | 0.548465 |
| B2-rep | reveal | 2,274 | 0.12 | 0.566158 | 0.064484 | 0.553065 | 0.200531 |

## Current and historical kernel status

| Account / kernel | API status | Interpretation |
|---|---|---|
| [huuhieu3333/grace-b1-full-budgetfix-20261108](https://www.kaggle.com/code/huuhieu3333/grace-b1-full-budgetfix-20261108) | COMPLETE | Fresh seed42 test: 5,006/5,006, zero legacy. Completion 15:35:51 GMT+7; PASS_LAUNCH_CONTRACT (six-package launch lock). Records and runtime/build evidence published. |
| [huuhieu3333/grace-b1-full-test](https://www.kaggle.com/code/huuhieu3333/grace-b1-full-test) | ERROR | Historical failed test: 2,850 rows, prompt-budget violations. Preserve for audit; superseded operationally by corrected fresh census. |
| [huuhieu3333/grace-b2-rep-test](https://www.kaggle.com/code/huuhieu3333/grace-b2-rep-test) | COMPLETE | 5,006/5,006, repeat cache tags checked; computational integrity passes, full new runtime lock not certified. |
| [huuhieu3333/grace-b3-only-resume-20261108](https://www.kaggle.com/code/huuhieu3333/grace-b3-only-resume-20261108) | COMPLETE | Historical B3 validation 5,005/5,005. Added 947 REVEAL to 4,058 imported rows; completion 10:40:57 GMT+7. No retrospective runtime certification for the original 4,029 rows. |
| [lznt123/grace-b1-shuf-test](https://www.kaggle.com/code/lznt123/grace-b1-shuf-test) | ERROR | Historical error before first inference record: native GPU-log parsing mismatch. Replaced by locked run on tomandjerry223. |
| [lznt123/grace-b3-locked-resume-20261108](https://www.kaggle.com/code/lznt123/grace-b3-locked-resume-20261108) | CANCEL_ACKNOWLEDGED | Cancelled by PI; 4,058 B3 rows exported and migrated; zero B3-nodiff rows inferred. |
| [lznt123/grace-b3-validation](https://www.kaggle.com/code/lznt123/grace-b3-validation) | COMPLETE | Kernel finished, NOT full validation census: 4,029 B3 rows; wall-clock interruption. Historical input/pairing, not amended B3. |
| [tomandjerry223/grace-b1-shuf-locked-20261108](https://www.kaggle.com/code/tomandjerry223/grace-b1-shuf-locked-20261108) | RUNNING | Fresh seed 42/43/44 test, target 15,018; fixed GPU-log parser and locked gates. Current live count unavailable. |
| [tomandjerry223/grace-b2-labelonly-test](https://www.kaggle.com/code/tomandjerry223/grace-b2-labelonly-test) | COMPLETE | 5,006/5,006; computational integrity passes, full new runtime lock not certified. |
| [tomandjerry223/grace-b2-nolabel-test](https://www.kaggle.com/code/tomandjerry223/grace-b2-nolabel-test) | COMPLETE | 5,006/5,006; computational integrity passes, full new runtime lock not certified. |

At the 16:08 snapshot, B1-shuf on tomandjerry223 is the only RUNNING kernel among these tracked jobs. No files are published for it, so live sample count/health remain unknown. This does not mean the entire study/test matrix is complete. B1-full needs only prompt seed42; seeds43/44 are required for B1-shuf.

## New completion and runtime acceptance

B1-full now has 2,732 Devign + 2,274 REVEAL fresh test records. All IDs, labels, frozen prompt hashes, per-record provenance, scores and locked predictions pass the recorded checks. Native logs confirm T4x2, 49/49 offload, context8192 and batch/ubatch256. The exact launch contract is `85d8770839f80260cdc7c27b27b6cce6bf8815675c8593db68fb102589c5cbd6`; SciPy1.16.3 is observed in pip freeze but the later seven-package contract was not loaded retroactively. Two REVEAL raw tokens are non-binary; all numeric scores remain valid under the declared scoring policy.

| Arm | Dataset | N | Locked tau | AUROC | MCC | BA | F1 |
|---|---|---:|---:|---:|---:|---:|---:|
| B1-full | devign | 2,732 | 0.99 | 0.531096 | 0.069566 | 0.527480 | 0.312535 |
| B1-full | reveal | 2,274 | 0.01 | 0.578215 | 0.084902 | 0.569695 | 0.209561 |

See [runtime acceptance](B1_FULL_RUNTIME_ACCEPTANCE.md), [machine-readable checks](b1_full_runtime_acceptance.json), [completion/file hashes](completion_update_20261108.json), and [worklog](../../worklogs/2026-11-08_b1_full_completion_runtime_acceptance.md). Original selected output copies for B1-full and historical B3 are in `completed_results/`. Full B1-full output/checkpoint was also downloaded locally; checkpoint bytes/hash are in the acceptance JSON. No threshold refitting or significance analysis was performed.

## Current B3 new-method milestone

Historical B3 completion is separate from the new verified-patch method. A real FFmpeg source case has been investigated locally; source formatting mapping, rationale/evidence binding and two genuine human reviews remain prerequisites before pool admission. No new-method inference has started. The detailed B3 code/dossier working tree is outside this run-completion publication.

## Historical B3/AGY discovery snapshot at 09:11 (preserved)

At that earlier snapshot the B3-only notebook used the historical 2 November prompt generation, not `b3-verified-patch-v1`; all 5,005 prompts were checked against the original dry-run texts. The new algorithm still requires authenticated before/after source pairs and two genuine human reviews. Runtime lock fixes do not change demonstration selection.

AGY-only workers generated the local indexer, independent tests, source fetcher and corrected review guide. No GPT subagents were spawned. The coordinator rejected the first guide for unsupported protocol changes and verified the revised one. The indexer passed 12 synthetic integrity/determinism tests and was then run locally over both frozen train banks:

| Dataset | Clean train donors | Heuristic opposite-label name-match combinations | Missing commit IDs | Verified/reviewed pairs |
|---|---:|---:|---:|---:|
| Devign | 21,691 | 26,700 | 0 | 0 / 0 |
| REVEAL | 17,636 | 33,947 | 17,636 | 0 / 0 |

These combinations are **not eligible patch pairs**. Full donor indexes/candidate inventories remain local and were not sent to model workers or included in this Git handoff. AGY received generic schemas/code-generation instructions only in the accepted workflow. An initial full-bank Devign delegation was rejected by automatic review; the safer schema-only route replaced it. Earlier headless attempts returned SUCCESS with denied commands and no artifacts; they are recorded as rejected/blocked, not completed work.

The bounded source recon attempted 16 public commit GETs for eight Devign candidates, but TLS issuer verification failed for every request. No source relationship can be inferred from those failures. Next step: fix the trusted CA configuration without disabling TLS validation, resume source collection, recover REVEAL provenance, then create genuine human-review packets. No pair approvals or new B3 inference bundle were fabricated.

## Evidence and validation

- `completed_results_summary.json` and per-arm `ACCEPTANCE.json`: original file hashes and recomputed metrics.
- `snapshot_0912/*/snapshot.json`: API status and selected remote artifact hashes; signed download URLs are not published.
- `../acceptance_6arms_20261108/`: full prior computational/prompt/cache acceptance evidence.
- `../locked_continuations_20261108/`: corrected renderer audit, exact notebook sources, launch/source/GPU-shape readbacks, B3 migration and prompt-origin evidence.
- `../agy_b3_safe_codegen_20261108/`: worker-generated code, task/conversation ledgers, accepted corrected guide and local discovery summaries.
- Frozen data/specs/thresholds, OSF artifacts, protected branches/tags and historical inference bytes were not modified.
