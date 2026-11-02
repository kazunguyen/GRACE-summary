"""Merge verified B2 donor reruns into a separate frozen-donor output; retain source records."""
import hashlib, json, math, sys, shutil, zipfile
from datetime import datetime, timezone
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
OLD=ROOT/'01_Author_Baseline_Unified/output/local_full/inference_qwen_q4_b2_20261101/grace_b2_four_split_8h'
REFERENCE=HERE/'donor_reconciliation_20261101/new_reference/B2'
RERUN=ROOT/'06_Arm_B2_Rand/output/kaggle_run_01/grace_b2_rand_three_seed_11h/b2_donor_rerun_66'
BUNDLE=ROOT/'07_Arm_B2_Donor_Rerun_66/output/grace_b2_devign_donor_rerun_66_20261102.zip'
OUT=ROOT/'01_Author_Baseline_Unified/output/local_full/inference_qwen_q4_b2_frozen_donor_20261102'
MODEL='f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335'
SPLITS=(('devign','validation',2732),('devign','test',2732),('reveal','validation',2273),('reveal','test',2274))

def read(p):return json.loads(p.read_text(encoding='utf-8'))
def rows(p):
 with p.open(encoding='utf-8') as f:return [json.loads(line) for line in f if line.strip()]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def identity(m):
 keys=('model_sha256','model_repo','quantization','model_file','llama_cpp_python','model_repo_revision','tokenizer','tokenizer_revision','gpu_layers','context_tokens','scoring','limit')
 return {k:m[k] for k in keys}
def dt(v):return datetime.fromisoformat(v.replace('Z','+00:00'))
def main():
 if OUT.exists():raise FileExistsError(f'Refusing to overwrite existing merged output: {OUT}')
 sys.path.insert(0,str(ROOT/'07_Arm_B2_Donor_Rerun_66'))
 from verify_bundle import load_bundle
 from validation_lock import make_lock, inference_identity, require_test_lock
 bundle, changed=load_bundle(BUNDLE)
 lock_file=RERUN/'thresholds.json'; lock=read(lock_file)['entries']['B2/devign']
 prepared={}; evidence=[]
 for ds,sp,count in SPLITS:
  reference=REFERENCE/ds/sp/'prompts.jsonl'; expected=rows(reference); manifest_path=reference.with_name('manifest.json'); ref_manifest=read(manifest_path)
  if sha(reference)!=ref_manifest['prompts_sha256']:raise ValueError(f'New reference hash mismatch: {ds}/{sp}')
  exp={str(r['id']):r for r in expected}
  if len(expected)!=count or len(exp)!=count:raise ValueError(f'Invalid expected IDs: {ds}/{sp}')
  original_path=OLD/ds/sp/'records.jsonl'; original=rows(original_path); old_manifest=read(original_path.with_name('run_manifest.json'))
  old_by_id={str(r['id']):r for r in original}
  if len(original)!=count or len(old_by_id)!=count or set(old_by_id)!=set(exp):raise ValueError(f'Old record IDs mismatch {ds}/{sp}')
  new_path=RERUN/ds/sp/'records.jsonl'; new=rows(new_path) if ds=='devign' else []
  if ds=='devign':
   new_manifest=read(new_path.with_name('run_manifest.json'))
   if identity(old_manifest)!=identity(new_manifest):raise ValueError(f'Inference config mismatch {ds}/{sp}')
   if inference_identity(new_manifest)!=bundle['expected_inference_identity']:raise ValueError('Rerun identity mismatch')
  changed_rows=[r for r in changed if r['dataset']==ds and r['split']==sp]; needed={str(r['id']):r for r in changed_rows}; new_by_id={str(r['id']):r for r in new}
  if len(new_by_id)!=len(new) or set(new_by_id)!=set(needed):raise ValueError(f'Rerun IDs mismatch {ds}/{sp}')
  merged=[]
  for ref in expected:
   uid=str(ref['id']); old=old_by_id[uid]; use=new_by_id.get(uid,old)
   if (use['id'],use['dataset'],use['split'],use['arm'],use['label'],use['prompt_sha256'],use['model_sha256'],use['seed'])!=(ref['id'],ds,sp,'B2',ref['label'],ref['prompt_sha256'],MODEL,42):raise ValueError(f'Merged identity mismatch {ds}/{sp}/{uid}')
   if uid in needed and old['prompt_sha256']==use['prompt_sha256']:raise ValueError('Rerun did not change prompt')
   if not (use.get('valid') and isinstance(use.get('s'),(int,float)) and math.isfinite(use['s']) and 0<=use['s']<=1):raise ValueError(f'Invalid score {uid}')
   merged.append(use)
  if ds=='devign' and len(new)!={'validation':28,'test':38}[sp]:raise ValueError('Wrong rerun count')
  paths=[original_path,original_path.with_name('run_manifest.json'),reference,manifest_path]+([new_path,new_path.with_name('run_manifest.json')] if new else [])
  evidence.append({'dataset':ds,'split':sp,'count':count,'reused_count':count-len(new),'rerun_count':len(new),'inputs':{rel(p):sha(p) for p in paths}})
  prepared[(ds,sp)]=(merged,old_manifest,ref_manifest)
 if [e['rerun_count'] for e in evidence]!=[28,38,0,0]:raise ValueError('Unexpected rerun distribution')
 val=prepared[('devign','validation')][0]; val_manifest=read(RERUN/'devign/validation/run_manifest.json');
 recomputed=make_lock(rows(REFERENCE/'devign/validation/prompts.jsonl'),val,'B2','devign',val_manifest,bundle['full_validation_prompt_set_sha256'])
 for k in ('identity','rules_sha256','validation_prompt_set_sha256','validation_evidence_sha256','tau','n_expected'):
  if recomputed[k]!=lock[k]:raise ValueError(f'Validation lock mismatch: {k}')
 require_test_lock(lock_file,'B2','devign',val_manifest,bundle['full_validation_prompt_set_sha256'])
 if any(dt(r['timestamp'])<=dt(lock['locked_at_utc']) for r in rows(RERUN/'devign/test/records.jsonl')):raise ValueError('A new test record predates the new lock')
 # Write only after all validations pass; never change the historical folders or lock.
 OUT.mkdir(parents=True)
 for ds,sp,count in SPLITS:
  merged,old_manifest,ref_manifest=prepared[(ds,sp)];folder=OUT/ds/sp;folder.mkdir(parents=True)
  with (folder/'records.jsonl').open('w',encoding='utf-8',newline='\n') as f:
   for r in merged:f.write(json.dumps(r,ensure_ascii=False,allow_nan=False)+'\n')
  m=dict(old_manifest, prompt_set_sha256=ref_manifest['prompts_sha256'], merged_from_multiple_runs=True, output_identity='B2_frozen_donor_20261102', source_evidence=next(e for e in evidence if e['dataset']==ds and e['split']==sp))
  m.pop('bundle_sha256',None)
  (folder/'run_manifest.json').write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
 shutil.copyfile(lock_file,OUT/'thresholds_devign.json')
 report={'schema':'b2_frozen_donor_merge_v1','created_at_utc':datetime.now(timezone.utc).isoformat(),'bundle':rel(BUNDLE),'bundle_sha256':sha(BUNDLE),'lock_sha256':sha(lock_file),'lock_validation_evidence_sha256':lock['validation_evidence_sha256'],'devign_new_test_after_lock':True,'historical_test_exposure':'Earlier B2 test records predate the new lock; no retrospective preregistration claim.','sets':evidence,'outputs':{f'{ds}/{sp}':sha(OUT/ds/sp/'records.jsonl') for ds,sp,_ in SPLITS}}
 (OUT/'merge_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'output':str(OUT),'sets':[{k:e[k] for k in ('dataset','split','count','reused_count','rerun_count')} for e in evidence]},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
