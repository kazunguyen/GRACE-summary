# Kaggle run handoff — 8 November 2026

Latest API snapshot completed: **2026-11-08 09:11:33 GMT+7**. Read-only collection from the three configured accounts; no additional GPU run was started for this handoff.

## Completed test arms published in Git

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
| [huuhieu3333/grace-b1-full-budgetfix-20261108](https://www.kaggle.com/code/huuhieu3333/grace-b1-full-budgetfix-20261108) | RUNNING | Fresh corrected B1-full test, target 5,006; all validation prompts reproduced exactly. Live output unavailable; current record count not observable. |
| [huuhieu3333/grace-b1-full-test](https://www.kaggle.com/code/huuhieu3333/grace-b1-full-test) | ERROR | Historical failed test: 2,850 rows, prompt-budget violations. Preserve for audit; superseded operationally by corrected fresh census. |
| [huuhieu3333/grace-b2-rep-test](https://www.kaggle.com/code/huuhieu3333/grace-b2-rep-test) | COMPLETE | 5,006/5,006, repeat cache tags checked; computational integrity passes, full new runtime lock not certified. |
| [huuhieu3333/grace-b3-only-resume-20261108](https://www.kaggle.com/code/huuhieu3333/grace-b3-only-resume-20261108) | RUNNING | B3 ONLY, historical algorithm. Starts from 4,058 accepted rows (4,029 historical + 29 source-locked); 947 REVEAL rows remaining at launch. Current live count unavailable. |
| [lznt123/grace-b1-shuf-test](https://www.kaggle.com/code/lznt123/grace-b1-shuf-test) | ERROR | Historical error before first inference record: native GPU-log parsing mismatch. Replaced by locked run on tomandjerry223. |
| [lznt123/grace-b3-locked-resume-20261108](https://www.kaggle.com/code/lznt123/grace-b3-locked-resume-20261108) | CANCEL_ACKNOWLEDGED | Cancelled by PI; 4,058 B3 rows exported and migrated; zero B3-nodiff rows inferred. |
| [lznt123/grace-b3-validation](https://www.kaggle.com/code/lznt123/grace-b3-validation) | COMPLETE | Kernel finished, NOT full validation census: 4,029 B3 rows; wall-clock interruption. Historical input/pairing, not amended B3. |
| [tomandjerry223/grace-b1-shuf-locked-20261108](https://www.kaggle.com/code/tomandjerry223/grace-b1-shuf-locked-20261108) | RUNNING | Fresh seed 42/43/44 test, target 15,018; fixed GPU-log parser and locked gates. Current live count unavailable. |
| [tomandjerry223/grace-b2-labelonly-test](https://www.kaggle.com/code/tomandjerry223/grace-b2-labelonly-test) | COMPLETE | 5,006/5,006; computational integrity passes, full new runtime lock not certified. |
| [tomandjerry223/grace-b2-nolabel-test](https://www.kaggle.com/code/tomandjerry223/grace-b2-nolabel-test) | COMPLETE | 5,006/5,006; computational integrity passes, full new runtime lock not certified. |

The active arrangement is **huuhieu3333: B1-full + B3-only**, **tomandjerry223: B1-shuf**. Each notebook requests a separate T4×2 runtime. RUNNING indicates a live Kaggle session, not a proven inference count or passed GPU model-load gate. All three active output APIs returned no published files in this snapshot; do not substitute historical checkpoint counts for current progress.

## B3 algorithm and AGY discovery status

The active B3-only notebook uses the historical 2 November prompt generation, not `b3-verified-patch-v1`; all 5,005 prompts were checked against the original dry-run texts. The new algorithm still requires authenticated before/after source pairs and two genuine human reviews. Runtime lock fixes do not change demonstration selection.

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
