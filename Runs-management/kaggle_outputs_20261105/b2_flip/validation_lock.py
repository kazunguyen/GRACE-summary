"""CPU-only, validation-only threshold locking. Portable into Kaggle notebooks."""
import hashlib
import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path

RULES={'version':'validation_mcc_grid_v1','grid':[i/100 for i in range(1,100)],
       'objective':'MCC on finite valid validation scores only','comparison':'score >= threshold',
       'tie_break':'within 1e-9: closest to 0.5, then lower threshold',
       'degenerate':'if every MCC is undefined, lock 0.5 with MCC=null; report explicitly',
       'coverage':'require every validation ID; invalid rows retained in coverage but excluded from fitting',
       'test_usage':'never read test records or metrics to choose threshold'}
def digest_json(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
RULES_SHA256=digest_json(RULES)

def file_sha256(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def read_jsonl(path):
    with Path(path).open(encoding='utf-8') as f:
        return [json.loads(l) for l in f if l.strip()]

def write_json(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.tmp')
    with tmp.open('w',encoding='utf-8',newline='\n') as f:
        json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(tmp,path)

def mcc(y,p):
    tp=sum(a==1 and b==1 for a,b in zip(y,p));tn=sum(a==0 and b==0 for a,b in zip(y,p))
    fp=sum(a==0 and b==1 for a,b in zip(y,p));fn=sum(a==1 and b==0 for a,b in zip(y,p))
    den=math.sqrt((tp+fp)*(tp+fn)*(tn+fp)*(tn+fn))
    return (tp*tn-fp*fn)/den if den else None

def pick_threshold(rows):
    valid=[]
    for r in rows:
        value=r.get('s')
        if r.get('valid') and isinstance(value,(int,float)) and math.isfinite(value):
            if not 0<=value<=1:raise ValueError('Score outside [0,1]')
            valid.append(r)
    if not valid:raise ValueError('No finite valid validation scores; cannot lock threshold')
    if {r['label'] for r in valid}!={0,1}:raise ValueError('Validation fitting needs both classes among valid scores')
    y=[r['label'] for r in valid];scores=[r['s'] for r in valid]
    best_t=.5;best_m=None;grid=[]
    for t in RULES['grid']:
        value=mcc(y,[int(v>=t) for v in scores]);grid.append({'threshold':t,'mcc':value})
        if value is None:continue
        if best_m is None or value>best_m+1e-9 or (abs(value-best_m)<=1e-9 and (abs(t-.5),t)<(abs(best_t-.5),best_t)):
            best_t,best_m=t,value
    return {'tau':best_t,'validation_mcc':best_m,'n_valid':len(valid),'n_invalid':len(rows)-len(valid),
            'score_coverage':len(valid)/len(rows),'degenerate':best_m is None,'grid_results':grid}

def inference_identity(manifest):
    return {'model_sha256':manifest['model_sha256'],'tokenizer':manifest['tokenizer'],
            'tokenizer_revision':manifest['tokenizer_revision'],'quantization':manifest['quantization'],
            'backend':'llama-cpp-python','backend_version':manifest['llama_cpp_python'],
            'scoring':manifest['scoring'],'seed_recorded':42,'context_tokens':manifest['context_tokens']}

def validate_validation(expected,records,arm,dataset,model_sha256):
    exp={str(r['id']):r for r in expected}
    if len(exp)!=len(expected):raise ValueError('Duplicate expected validation IDs')
    seen={}
    for r in records:
        uid=str(r['id'])
        if r.get('split')!='validation' or r.get('dataset')!=dataset or r.get('arm')!=arm:
            raise ValueError('Only the requested arm/dataset validation records may be fitted')
        if uid in seen:raise ValueError('Duplicate validation records')
        e=exp.get(uid)
        if e is None or r.get('label')!=e['label'] or r.get('prompt_sha256')!=e['prompt_sha256']:
            raise ValueError('Validation ID/label/prompt identity mismatch')
        if r.get('model_sha256')!=model_sha256 or r.get('seed')!=42:
            raise ValueError('Validation model/seed mismatch')
        seen[uid]=r
    return exp,seen

def make_lock(expected,records,arm,dataset,run_manifest,validation_prompt_set_sha256,source_evidence=None):
    exp,seen=validate_validation(expected,records,arm,dataset,run_manifest['model_sha256'])
    if set(exp)!=set(seen):raise ValueError(f'Incomplete validation: {len(seen)}/{len(exp)}; do not fit on partial data')
    ordered=[seen[uid] for uid in sorted(seen)]
    result=pick_threshold(ordered)
    evidence=[{k:r.get(k) for k in ('id','label','prompt_sha256','model_sha256','seed','s','valid')} for r in ordered]
    # Normalize invalid scores for strict JSON; their raw validity remains recorded.
    for r in evidence:
        if r['s'] is not None and not math.isfinite(r['s']):r['s']=None
    return {'arm':arm,'dataset':dataset,'split_used':'validation','locked_at_utc':datetime.now(timezone.utc).isoformat(),
            'rules_sha256':RULES_SHA256,'identity':inference_identity(run_manifest),
            'validation_prompt_set_sha256':validation_prompt_set_sha256,'n_expected':len(exp),
            'validation_evidence_sha256':digest_json(evidence),'source_evidence':source_evidence or [],
            'temporal_claim':'locked at actual time; does not certify that external test inference had not started',**result}

def persist_lock(path,entry):
    path=Path(path)
    data=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'schema':'thresholds_v1','rules':RULES,'rules_sha256':RULES_SHA256,'entries':{}}
    if data.get('rules_sha256')!=RULES_SHA256:raise ValueError('Threshold rules differ; create a new version')
    key=f"{entry['arm']}/{entry['dataset']}";old=data['entries'].get(key)
    if old:
        for k in ('rules_sha256','identity','validation_prompt_set_sha256','validation_evidence_sha256','tau'):
            if old.get(k)!=entry.get(k):raise ValueError(f'Locked threshold is immutable; conflicting {k} for {key}')
        return old
    data['entries'][key]=entry;write_json(path,data);return entry

def require_test_lock(path,arm,dataset,run_manifest,validation_prompt_set_sha256=None):
    path=Path(path)
    if not path.exists():raise ValueError('Test blocked: thresholds.json missing; complete validation first')
    data=json.loads(path.read_text(encoding='utf-8'));entry=data.get('entries',{}).get(f'{arm}/{dataset}')
    if not entry:raise ValueError(f'Test blocked: no locked threshold for {arm}/{dataset}')
    if data.get('rules_sha256')!=RULES_SHA256 or entry.get('rules_sha256')!=RULES_SHA256:
        raise ValueError('Test blocked: different threshold selection rules')
    if entry.get('identity')!=inference_identity(run_manifest):raise ValueError('Test blocked: model/tokenizer/backend differs from validation')
    if validation_prompt_set_sha256 and entry.get('validation_prompt_set_sha256')!=validation_prompt_set_sha256:
        raise ValueError('Test blocked: validation prompt set changed')
    return entry

def evaluate_at_locked_threshold(records,entry):
    valid=[r for r in records if r.get('valid') and isinstance(r.get('s'),(int,float)) and math.isfinite(r['s'])]
    y=[r['label'] for r in valid];pred=[int(r['s']>=entry['tau']) for r in valid]
    tp=sum(a==1 and b==1 for a,b in zip(y,pred));tn=sum(a==0 and b==0 for a,b in zip(y,pred))
    fp=sum(a==0 and b==1 for a,b in zip(y,pred));fn=sum(a==1 and b==0 for a,b in zip(y,pred))
    return {'tau':entry['tau'],'n':len(valid),'score_coverage':len(valid)/len(records) if records else 0,
            'mcc':mcc(y,pred),'accuracy':(tp+tn)/len(y) if y else None,
            'confusion_matrix':[[tn,fp],[fn,tp]],'threshold_locked_at_utc':entry['locked_at_utc'],
            'threshold_validation_evidence_sha256':entry['validation_evidence_sha256']}
