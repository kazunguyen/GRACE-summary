"""Render the Git handoff from fresh API snapshots and checked result artifacts."""
from datetime import datetime,timezone,timedelta
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'Runs-management/run_handoff_20261108'
snapshots=[json.loads(p.read_text(encoding='utf-8')) for p in sorted((OUT/'snapshot_0912').glob('*/snapshot.json'))]
results=json.loads((OUT/'completed_results_summary.json').read_text(encoding='utf-8'))
latest=max(datetime.fromisoformat(s['finished_at_utc']) for s in snapshots)
local=latest.astimezone(timezone(timedelta(hours=7))).strftime('%Y-%m-%d %H:%M:%S GMT+7')
notes={
'grace-b1-full-budgetfix-20261108':'Fresh corrected B1-full test, target 5,006; all validation prompts reproduced exactly. Live output unavailable; current record count not observable.',
'grace-b3-only-resume-20261108':'B3 ONLY, historical algorithm. Starts from 4,058 accepted rows (4,029 historical + 29 source-locked); 947 REVEAL rows remaining at launch. Current live count unavailable.',
'grace-b1-shuf-locked-20261108':'Fresh seed 42/43/44 test, target 15,018; fixed GPU-log parser and locked gates. Current live count unavailable.',
'grace-b1-full-test':'Historical failed test: 2,850 rows, prompt-budget violations. Preserve for audit; superseded operationally by corrected fresh census.',
'grace-b2-rep-test':'5,006/5,006, repeat cache tags checked; computational integrity passes, full new runtime lock not certified.',
'grace-b2-labelonly-test':'5,006/5,006; computational integrity passes, full new runtime lock not certified.',
'grace-b2-nolabel-test':'5,006/5,006; computational integrity passes, full new runtime lock not certified.',
'grace-b1-shuf-test':'Historical error before first inference record: native GPU-log parsing mismatch. Replaced by locked run on tomandjerry223.',
'grace-b3-locked-resume-20261108':'Cancelled by PI; 4,058 B3 rows exported and migrated; zero B3-nodiff rows inferred.',
'grace-b3-validation':'Kernel finished, NOT full validation census: 4,029 B3 rows; wall-clock interruption. Historical input/pairing, not amended B3.'}
lines=['# Kaggle run handoff — 8 November 2026','',f'Latest API snapshot completed: **{local}**. Read-only collection from the three configured accounts; no additional GPU run was started for this handoff.','',
'## Completed test arms published in Git','',
'The following exact records, original evaluation/run manifests and validation threshold-lock snapshots are in `completed_results/`. All 15,018 records were rechecked against frozen test IDs/labels, score/logprob math, locked predictions and original manifest hashes. Metrics were recomputed and match original evaluations. These are descriptive full-census results; no new significance test or threshold optimization was performed.','',
'**Runtime limitation:** these three historical runs are not certified as fully compliant with the newer runtime lock. Package/model/core constructor evidence passes, but verified source/build/native full-offload provenance is incomplete. Completion and numerical acceptance must not be presented as full runtime certification.','',
'| Arm | Dataset | N | Locked τ | AUROC | MCC | BA | F1 |','|---|---|---:|---:|---:|---:|---:|---:|']
for arm in results['arms']:
    for d in arm['datasets']:
        m=d['metrics'];lines.append(f"| {arm['arm']} | {d['dataset']} | {m['n']:,} | {m['tau']:.2f} | {m['auroc']:.6f} | {m['mcc_at_tau']:.6f} | {m['ba_at_tau']:.6f} | {m['f1_at_tau']:.6f} |")
lines+=['','## Current and historical kernel status','','| Account / kernel | API status | Interpretation |','|---|---|---|']
for s in snapshots:
    for r in s['kernels']:
        slug=r['ref'].split('/')[1]
        lines.append(f"| [{r['ref']}](https://www.kaggle.com/code/{r['ref']}) | {r.get('status','UNKNOWN')} | {notes.get(slug,r.get('error','Needs review'))} |")
lines+=['','The active arrangement is **huuhieu3333: B1-full + B3-only**, **tomandjerry223: B1-shuf**. Each notebook requests a separate T4×2 runtime. RUNNING indicates a live Kaggle session, not a proven inference count or passed GPU model-load gate. All three active output APIs returned no published files in this snapshot; do not substitute historical checkpoint counts for current progress.','',
'## B3 algorithm and AGY discovery status','',
'The active B3-only notebook uses the historical 2 November prompt generation, not `b3-verified-patch-v1`; all 5,005 prompts were checked against the original dry-run texts. The new algorithm still requires authenticated before/after source pairs and two genuine human reviews. Runtime lock fixes do not change demonstration selection.','',
'AGY-only workers generated the local indexer, independent tests, source fetcher and corrected review guide. No GPT subagents were spawned. The coordinator rejected the first guide for unsupported protocol changes and verified the revised one. The indexer passed 12 synthetic integrity/determinism tests and was then run locally over both frozen train banks:','',
'| Dataset | Clean train donors | Heuristic opposite-label name-match combinations | Missing commit IDs | Verified/reviewed pairs |','|---|---:|---:|---:|---:|',
'| Devign | 21,691 | 26,700 | 0 | 0 / 0 |','| REVEAL | 17,636 | 33,947 | 17,636 | 0 / 0 |','',
'These combinations are **not eligible patch pairs**. Full donor indexes/candidate inventories remain local and were not sent to model workers or included in this Git handoff. AGY received generic schemas/code-generation instructions only in the accepted workflow. An initial full-bank Devign delegation was rejected by automatic review; the safer schema-only route replaced it. Earlier headless attempts returned SUCCESS with denied commands and no artifacts; they are recorded as rejected/blocked, not completed work.','',
'The bounded source recon attempted 16 public commit GETs for eight Devign candidates, but TLS issuer verification failed for every request. No source relationship can be inferred from those failures. Next step: fix the trusted CA configuration without disabling TLS validation, resume source collection, recover REVEAL provenance, then create genuine human-review packets. No pair approvals or new B3 inference bundle were fabricated.','',
'## Evidence and validation','',
'- `completed_results_summary.json` and per-arm `ACCEPTANCE.json`: original file hashes and recomputed metrics.','- `snapshot_0912/*/snapshot.json`: API status and selected remote artifact hashes; signed download URLs are not published.','- `../acceptance_6arms_20261108/`: full prior computational/prompt/cache acceptance evidence.','- `../locked_continuations_20261108/`: corrected renderer audit, exact notebook sources, launch/source/GPU-shape readbacks, B3 migration and prompt-origin evidence.','- `../agy_b3_safe_codegen_20261108/`: worker-generated code, task/conversation ledgers, accepted corrected guide and local discovery summaries.','- Frozen data/specs/thresholds, OSF artifacts, protected branches/tags and historical inference bytes were not modified.','']
(OUT/'RUN_STATUS.md').write_text('\n'.join(lines),encoding='utf-8')
(ROOT/'worklogs/2026-11-08_run_results_and_agy_handoff.md').write_text('# Worklog — completed results, active runs and AGY handoff\n\n'+
    f'Snapshot: {local}. See [full run handoff](../Runs-management/run_handoff_20261108/RUN_STATUS.md) for the status table, metrics, limitations and next steps.\n\n'+
    'Published checked, byte-preserved B2-labelonly, B2-nolabel and B2-rep test results (15,018 records total) with original manifests/evaluations and threshold-lock snapshots. Fresh API queries confirm those three COMPLETE; B1-full corrected, B1-shuf locked and B3-only remain RUNNING, with no live files exposed. Old combined B3 is CANCEL_ACKNOWLEDGED, and old B3 validation is kernel-COMPLETE but incomplete in sample census.\n\n'+
    'The user requested AGY as the worker backend and explicitly prohibited GPT multiagent workers. Added the scoped AGY CLI controller and recorded actual task outcomes. Automatic review blocked an initial full-bank Devign delegation; it was not retried indirectly. The successful replacement sends schema-only code-generation tasks and executes reviewed code locally. No data-dependent stopping or inference/threshold changes were introduced by this discovery work.\n\n'+
    'AGY produced local scanner/test/fetcher/checklist artifacts; coordinator rejected and corrected unsupported guide changes. Twelve independent scanner tests passed, and frozen-bank scans reproduce 21,691/17,636 eligible donors and 26,700/33,947 unverified name-match combinations. There are no newly admitted pairs. Source recon hit certificate issuer verification errors; preserve this blocker rather than treating missing responses as negative security evidence.\n\n'+
    'Git handoff excludes credentials, full train snapshots, donor indexes, installed tooling, temporary files, raw download duplicates and model weights. Only accepted completed result copies plus relevant scripts, notebooks, audit metadata and worklogs are staged. Protected preregistration files and anchors remain untouched.\n',encoding='utf-8')
print(json.dumps({'report':'Runs-management/run_handoff_20261108/RUN_STATUS.md','snapshot':local,'kernels':sum(len(s['kernels']) for s in snapshots),'completed_test_records':15018}),flush=True)
