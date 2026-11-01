"""Auto-lock complete local validation artifacts. Does not open test records/metrics.

python Runs-management/auto_lock_validation.py
python Runs-management/auto_lock_validation.py --watch --interval 60
"""
import argparse,json,time
from datetime import datetime,timezone
from pathlib import Path
from validation_lock import (RULES_SHA256,digest_json,file_sha256,read_jsonl,validate_validation,
                             inference_identity,make_lock,persist_lock,write_json)

ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'01_Author_Baseline_Unified';HERE=Path(__file__).parent
FOLDERS={'B0':'02_Arm_B0_Source_Only','B1':'03_Arm_B1_Graph_Only','B2-flip':'04_Arm_B2_Flip','B2-rep':'05_Arm_B2_Rep'}

def scan_once():
    sources={}
    roots=[BASE/'kaggle_qwen_q4_b2']+[ROOT/f for f in FOLDERS.values()]
    for root in roots:
        for p in root.rglob('records.jsonl'):
            if p.parent.name!='validation' or any(x in str(p) for x in ('offline_test','pytest','test_prepare','threshold_pipeline_tests')):continue
            mp=p.parent/'run_manifest.json'
            if not mp.exists():continue
            rows=read_jsonl(p);manifest=json.loads(mp.read_text(encoding='utf-8'))
            if not rows:continue
            key=(rows[0].get('arm'),rows[0].get('dataset'))
            if key[0] not in ('B0','B1','B2','B2-flip','B2-rep') or key[1] not in ('devign','reveal'):continue
            sources.setdefault(key,[]).append((p,rows,manifest))
    statuses=[]
    for arm in ('B0','B1','B2','B2-flip','B2-rep'):
        for dataset in ('devign','reveal'):
            folder=(BASE/'output/local_full/bundles_recovered_joern_final_20261031' if arm=='B2' else ROOT/FOLDERS[arm]/'output/bundles')/dataset/'validation'
            p=folder/'prompts.jsonl';mp=folder/'bundle_manifest.json'
            status={'arm':arm,'dataset':dataset,'state':'waiting_validation_records','complete':False}
            if not p.exists() or not mp.exists():status['state']='waiting_prompt_bundle';statuses.append(status);continue
            expected=read_jsonl(p);bm=json.loads(mp.read_text(encoding='utf-8'))
            if file_sha256(p)!=bm['prompts_sha256']:raise ValueError('Validation prompt bundle hash mismatch')
            status['expected']=len(expected);merged={};identity=None;manifest=None;evidence=[]
            for record_path,records,current in sources.get((arm,dataset),[]):
                _,validated=validate_validation(expected,records,arm,dataset,current['model_sha256'])
                current_identity=inference_identity(current)
                if identity is not None and current_identity!=identity:raise ValueError(f'Conflicting model identities for {arm}/{dataset}')
                identity=current_identity;manifest=current
                for uid,r in validated.items():
                    critical={k:r.get(k) for k in ('id','label','s','valid','prompt_sha256','model_sha256','seed')}
                    if uid in merged:
                        previous={k:merged[uid].get(k) for k in critical}
                        if digest_json(previous)!=digest_json(critical):raise ValueError(f'Conflicting validation scores for {arm}/{dataset}/{uid}')
                    merged[uid]=r
                evidence.append({'path':str(record_path.relative_to(ROOT)),'records_sha256':file_sha256(record_path),'rows':len(records)})
            status.update(completed=len(merged),missing=len(expected)-len(merged),source_files=len(evidence))
            if len(merged)==len(expected):
                entry=make_lock(expected,list(merged.values()),arm,dataset,manifest,bm['prompts_sha256'],evidence)
                locked=persist_lock(HERE/'thresholds.json',entry)
                status.update(state='locked',complete=True,tau=locked['tau'],validation_mcc=locked['validation_mcc'],locked_at_utc=locked['locked_at_utc'])
            statuses.append(status)
            print(arm,dataset,status['state'],f"{len(merged)}/{len(expected)}",'tau',status.get('tau'),flush=True)
    write_json(HERE/'threshold_lock_status.json',{'checked_at_utc':datetime.now(timezone.utc).isoformat(),'rules_sha256':RULES_SHA256,'entries':statuses})
    return statuses

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--watch',action='store_true');ap.add_argument('--interval',type=float,default=60)
    args=ap.parse_args()
    while True:
        status=scan_once()
        if not args.watch or all(r['complete'] for r in status):break
        time.sleep(max(1,args.interval))
