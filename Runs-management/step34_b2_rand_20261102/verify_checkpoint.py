"""Read-only verification for B2-rand checkpoint against audited inputs; no test scores."""
import hashlib, io, json, zipfile, math
from datetime import datetime, timezone
from pathlib import Path

HERE=Path(__file__).resolve().parent; ROOT=HERE.parent.parent
BUNDLE=ROOT/'06_Arm_B2_Rand/output/bundles/grace_b2_rand_inputs.zip'
OUT=ROOT/'06_Arm_B2_Rand/output/kaggle_run_01/grace_b2_rand_three_seed_11h'
CHECKPOINT=ROOT/'06_Arm_B2_Rand/output/kaggle_run_01/grace_b2_rand_checkpoint.zip'
AUDIT=ROOT/'Runs-management/prompt_audit_20261102/audit_summary.json'
REF=ROOT/'Runs-management/donor_reconciliation_20261101/new_reference/B2'
SEEDS=(42,43,44);RUNS=(('devign','validation'),('reveal','validation'),('devign','test'),('reveal','test'))
MODEL='f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335'

def digest(b):return hashlib.sha256(b).hexdigest()
def read_jsonl(b):return [json.loads(x) for x in b.decode('utf-8').splitlines() if x.strip()]
def main():
 audit=json.loads(AUDIT.read_text(encoding='utf-8')); existing={(e['seed'],e['dataset'],e['split']):e for e in audit['prompt_sets'] if e['arm']=='B2-rand'}
 if len(existing)!=12:raise ValueError('Expected 12 audited sets')
 summaries=[];scores=0;coincidences=[];record_hashes={}
 with zipfile.ZipFile(BUNDLE) as input_zip,zipfile.ZipFile(CHECKPOINT) as checkpoint:
  checkpoint_names=set(checkpoint.namelist())
  if checkpoint.testzip() is not None:raise ValueError('Checkpoint ZIP CRC failed')
  for dataset,split in RUNS:
   ref_path=REF/dataset/split/'prompts.jsonl'; ref={str(r['id']):r for r in read_jsonl(ref_path.read_bytes())}
   for seed in SEEDS:
    key=(seed,dataset,split);name=f'seed_{seed}/{dataset}_{split}_b2_rand_seed_{seed}_kaggle.zip'
    with zipfile.ZipFile(io.BytesIO(input_zip.read(name))) as z:
     raw=z.read('prompts.jsonl');m=json.loads(z.read('bundle_manifest.json'));items=read_jsonl(raw)
    if digest(raw)!=existing[key]['source_sha256'] or digest(raw)!=m['prompts_sha256']:raise ValueError(f'Audit/manifest hash mismatch {key}')
    prompts={str(r['id']):r for r in items}
    if len(prompts)!=len(items) or set(prompts)!=set(ref):raise ValueError(f'Input ID mismatch {key}')
    for uid,item in prompts.items():
     if (item['arm'],item['seed'],item['dataset'],item['split'])!=('B2-rand',seed,dataset,split):raise ValueError('Identity mismatch')
     if digest(item['prompt'].encode())!=item['prompt_sha256']:raise ValueError('Prompt row hash mismatch')
     if item['demo_ids']==ref[uid]['demo_ids']:coincidences.append({'id':uid,'dataset':dataset,'split':split,'seed':seed})
    member=f'seed_{seed}/{dataset}/{split}/records.jsonl';p=OUT/member; has=p.is_file(); included=member in checkpoint_names
    if has!=included:raise ValueError(f'Checkpoint/local record path mismatch {member}')
    records=[]
    if has:
     raw_records=p.read_bytes()
     if digest(raw_records)!=digest(checkpoint.read(member)):raise ValueError(f'Checkpoint/local hash mismatch {member}')
     manifest=json.loads(p.with_name('run_manifest.json').read_text(encoding='utf-8'))
     if manifest.get('model_sha256')!=MODEL or manifest.get('prompt_set_sha256')!=m['prompts_sha256']:raise ValueError('Run manifest mismatch')
     records=read_jsonl(raw_records);seen=set()
     for row in records:
      uid=str(row['id']); exp=prompts.get(uid)
      if uid in seen or exp is None or (row['arm'],row['seed'],row['dataset'],row['split'],row['label'],row['prompt_sha256'],row['model_sha256'])!=('B2-rand',seed,dataset,split,exp['label'],exp['prompt_sha256'],MODEL):raise ValueError(f'Invalid checkpoint record {uid}')
      if not(row.get('valid') and isinstance(row.get('s'),(int,float)) and math.isfinite(row['s']) and 0<=row['s']<=1):raise ValueError('Invalid score')
      seen.add(uid)
     record_hashes[member]=digest(raw_records)
    if split=='test' and records:raise ValueError('Unexpected B2-rand test records: inspect chronology before continuing')
    scores+=len(records)
    summaries.append({'seed':seed,'dataset':dataset,'split':split,'prompts':len(items),'completed':len(records),'audited_prompts_sha256':digest(raw),'reference_prompts_sha256':digest(ref_path.read_bytes())})
 if scores!=4798:raise ValueError(f'Unexpected count: {scores}')
 status={'verified_at_utc':datetime.now(timezone.utc).isoformat(),'scope':'Integrity and prompt provenance only; no test records/metrics read; no inference or threshold fitting','checkpoint_sha256':digest(CHECKPOINT.read_bytes()),'input_zip_sha256':digest(BUNDLE.read_bytes()),'audit_sha256':digest(AUDIT.read_bytes()),'model_sha256':MODEL,'validation_records_verified':scores,'b2_rand_test_records':0,'same_as_current_reference_donor_count':len(coincidences),'same_as_current_reference_donor_examples':coincidences[:30],'checkpoint_record_hashes':record_hashes,'sets':summaries,'human_review':'pending_two_real_reviewers','registration':'not_completed_not_osf'}
 target=HERE/'checkpoint_verification.json'
 if target.exists():raise FileExistsError(target)
 target.write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'verified':True,'validation_records':scores,'test_records':0,'same_as_current_reference_donor_count':len(coincidences),'output':str(target)},ensure_ascii=False))
if __name__=='__main__':main()
