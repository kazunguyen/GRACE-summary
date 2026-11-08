"""Publish byte-preserved completed outputs and recomputed descriptive metrics."""
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import shutil

import numpy as np
from sklearn.metrics import roc_auc_score,matthews_corrcoef,balanced_accuracy_score,f1_score

ROOT=Path(__file__).resolve().parents[1]
HANDOFF=ROOT/'Runs-management/run_handoff_20261108'
SNAPSHOT=HANDOFF/'snapshot_0912'
OUT=HANDOFF/'completed_results'
ARMS={'B2-labelonly':('tomandjerry223','grace-b2-labelonly-test','b2_labelonly_test','12_Arm_B2_LabelOnly'),
      'B2-nolabel':('tomandjerry223','grace-b2-nolabel-test','b2_nolabel_test','10_Arm_B2_NoLabel'),
      'B2-rep':('huuhieu3333','grace-b2-rep-test','b2_rep_test','05_Arm_B2_Rep')}
sha=lambda raw:hashlib.sha256(raw).hexdigest()
def rows(raw):return [json.loads(x) for x in raw.splitlines() if x.strip()]
def dump(p,value):p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    if OUT.exists():raise FileExistsError('Preserve earlier published evidence')
    accepted=json.loads((ROOT/'Runs-management/acceptance_6arms_20261108/acceptance.json').read_text(encoding='utf-8'))
    prior={r['arm']:r for r in accepted['results']}
    report={'created_at_utc':datetime.now(timezone.utc).isoformat(),'metric_scope':'descriptive full official test census; no new hypothesis test or threshold tuning',
        'runtime_classification':'historical runs; computational integrity accepted; full new runtime lock NOT certified', 'arms':[]}
    verified=[]
    for arm,(owner,slug,folder,config) in ARMS.items():
        snapshot=json.loads((SNAPSHOT/owner/'snapshot.json').read_text(encoding='utf-8'))
        entry=next(r for r in snapshot['kernels'] if r['ref']==owner+'/'+slug)
        assert entry['status']=='COMPLETE' and not entry.get('error')
        lock_path=ROOT/config/'config/threshold.json';lock=json.loads(lock_path.read_text(encoding='utf-8'))
        body={k:v for k,v in lock.items() if k!='locked_sha256'}
        assert lock['locked_sha256'] in [sha(json.dumps(body,sort_keys=True,ensure_ascii=False,indent=2).encode()),sha(json.dumps(body,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode())]
        thresholds={e['dataset']:e['tau_star'] for e in lock['entries'].values() if e.get('seed',42)==42}
        arm_report=dict(arm=arm,source_kernel=owner+'/'+slug,remote_status='COMPLETE',runtime_lock_fully_certified=False,
            runtime_limitations='Six package/core model/constructor checks passed; missing verified source/build/native full-offload provenance. No retrospective full-lock certification.',
            threshold_source=str(lock_path.relative_to(ROOT)),threshold_source_sha256=sha(lock_path.read_bytes()),datasets=[])
        for ds,n in [('devign',2732),('reveal',2274)]:
            source=SNAPSHOT/owner/slug/'artifacts'/folder/'seed_42'/ds/'test'
            payload=(source/'records.jsonl').read_bytes();rr=rows(payload)
            audit=next(r for r in prior[arm]['datasets'] if r['dataset']==ds)
            assert sha(payload)==audit['records_sha256'] and audit['complete_record_integrity']
            assert len(rr)==n==len({r['id'] for r in rr})
            labels={r['id']:r['label'] for r in rows((ROOT/f'01_Author_Baseline_Unified/output/research_freeze_20261101/{ds}/test_manifest.jsonl').read_bytes())}
            assert set(labels)=={r['id'] for r in rr}
            tau=thresholds[ds]
            for r in rr:
                assert (r['arm'],r['seed'],r['dataset'],r['split'],r['label'])==(arm,42,ds,'test',labels[r['id']])
                assert r['valid'] and math.isfinite(r['s']) and 0<=r['s']<=1
                expected=float(np.exp(r['logprob_1']-np.logaddexp(r['logprob_0'],r['logprob_1'])))
                assert abs(r['s']-expected)<1e-12
                assert r['tau']==tau and r['pred_tau']==int(r['s']>=tau)
            y=np.array([r['label'] for r in rr]);s=np.array([r['s'] for r in rr]);p=(s>=tau).astype(int)
            metrics=dict(tau=tau,n=n,auroc=float(roc_auc_score(y,s)),mcc_at_tau=float(matthews_corrcoef(y,p)),
                ba_at_tau=float(balanced_accuracy_score(y,p)),f1_at_tau=float(f1_score(y,p,zero_division=0)))
            evaluation=json.loads((source/'evaluation.json').read_text(encoding='utf-8'))
            manifest=json.loads((source/'run_manifest.json').read_text(encoding='utf-8'))
            assert manifest['records_sha256']==sha(payload)
            assert all(abs(evaluation[k]-metrics[k])<1e-12 for k in ('auroc','mcc_at_tau','ba_at_tau','f1_at_tau'))
            files=[(source/name,OUT/arm/'seed_42'/ds/'test'/name) for name in ('records.jsonl','evaluation.json','run_manifest.json')]
            verified.extend(files)
            arm_report['datasets'].append(dict(dataset=ds,metrics=metrics,records_sha256=sha(payload),raw_invalid=sum(not r.get('response_valid',True) for r in rr),
                files=[dict(path=str(dest.relative_to(ROOT)),sha256=sha(src.read_bytes()),bytes=src.stat().st_size) for src,dest in files]))
        verified.append((lock_path,OUT/arm/'validation_threshold_lock.json'))
        report['arms'].append(arm_report)
    # Write only after every arm has passed the acceptance gates.
    for source,dest in verified:
        dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
        assert sha(source.read_bytes())==sha(dest.read_bytes())
    for arm in report['arms']:dump(OUT/arm['arm']/'ACCEPTANCE.json',arm)
    dump(HANDOFF/'completed_results_summary.json',report)
    print(json.dumps({'arms':[a['arm'] for a in report['arms']],'total_records':sum(d['metrics']['n'] for a in report['arms'] for d in a['datasets']),'files':len(verified),'all_passed':True}),flush=True)

if __name__=='__main__':main()
