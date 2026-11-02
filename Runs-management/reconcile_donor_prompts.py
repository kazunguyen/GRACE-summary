"""Reconcile downloaded inference against newly retrieved demos from the frozen bank.
CPU/cache only. Never overwrites active prompts, scores, thresholds or calls an LLM.
"""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
os.environ.setdefault('OMP_NUM_THREADS','4')
import csv,hashlib,json,platform,sys,time
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
from threadpoolctl import threadpool_limits

ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'01_Author_Baseline_Unified'
sys.path.insert(0,str(BASE));sys.path.insert(0,str(BASE/'diagnostic_kit/src'))
from retrieval_engine import DemonstrationRetriever,compute_hybrid_score
from embedding_engine import apply_whitening
from graph_extractor import serialize_ast_representation
from grace_diag.token_budget import TokenCounter

OUT=ROOT/'Runs-management/donor_reconciliation_20261101'
REF=BASE/'output/local_full/bundles_recovered_joern_final_20261031'
FROZEN=BASE/'output/research_freeze_20261101'
PIN='Salesforce/codet5-base@02cd2d31bb7c6d0e4d91156167b2de044989c733'
def sha_text(s):return hashlib.sha256(s.encode()).hexdigest()
def file_sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def rows(p):
 # Large binary buffer avoids thousands of tiny /mnt/d reads through WSL.
 with Path(p).open('rb',buffering=4*1024*1024) as f:
  for l in f:
   if l.strip():yield json.loads(l)
def write(p,obj):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
def append(f,obj):f.write(json.dumps(obj,ensure_ascii=False,allow_nan=False)+'\n')
def compact_bank(path,dataset,kind,expected_sha):
 cache=OUT/'cache'/f'{dataset}_{kind}_bank.jsonl';mp=cache.with_suffix('.manifest.json')
 actual=file_sha(path)
 if actual!=expected_sha:raise ValueError(f'Donor SHA mismatch: {path}')
 if cache.exists() and mp.exists() and read(mp).get('input_sha256')==actual:
  bank=list(rows(cache));m=read(mp)
  if file_sha(cache)==m['cache_sha256']:
   print(dataset,kind,'reuse compact bank',len(bank),flush=True);return bank,m
 cache.parent.mkdir(parents=True,exist_ok=True);bank=[];h=hashlib.sha256();seen=set()
 with cache.open('w',encoding='utf-8',newline='\n') as f:
  for r in rows(path):
   uid=str(r['function_uid']);assert uid not in seen;seen.add(uid)
   code=r['func'].strip();ast=serialize_ast_representation(r.get('nodes') or [],r.get('edges') or [])
   item={'id':uid,'func':code,'target':int(r['target']),'ast_repr':ast}
   signature=[uid,sha_text(code),item['target'],sha_text(ast)]
   h.update((json.dumps(signature,separators=(',',':'))+'\n').encode())
   append(f,item);bank.append(item)
   if len(bank)%3000==0:print(dataset,kind,'bank',len(bank),flush=True)
 m={'input_sha256':actual,'ordered_retrieval_fingerprint':h.hexdigest(),'count':len(bank),'cache_sha256':file_sha(cache)}
 write(mp,m);return bank,m

class CachedEncoder:
 def __init__(self,dataset):
  self.lookup={};self.arrays=[];self.provenance=[]
  for split in ('train','validation','test'):
   folder=BASE/f'output/local_full/{dataset}/embedding_cache/{split}';m=read(folder/'manifest.json')
   if m['model']!=PIN or m['completed']!=len(m['rows']):raise ValueError('Incomplete or wrong CodeT5 cache')
   x=np.load(folder/'vectors.npy',mmap_mode='r')
   if x.shape!=(len(m['rows']),768) or x.dtype!=np.float32:raise ValueError('Wrong CodeT5 vector shape/dtype')
   self.arrays.append(x)
   for i,r in enumerate(m['rows']):self.lookup.setdefault(r['code_sha256'],(x,i))
   self.provenance.append({'split':split,'manifest_sha256':file_sha(folder/'manifest.json'),'vectors_sha256':file_sha(folder/'vectors.npy')})
 def encode(self,codes,batch_size=16):
  out=[]
  for code in codes:
   key=sha_text(code)
   if key not in self.lookup:raise ValueError(f'Missing CodeT5 cache for code {key}; no encoder fallback allowed')
   x,i=self.lookup[key];out.append(x[i])
  return np.asarray(out,dtype=np.float32)

def queries(dataset):
 out=[];provenance=[]
 for split in ('validation','test'):
  p=REF/dataset/split/'specs.jsonl';bm=read(p.parent/'bundle_manifest.json')
  assert file_sha(p)==bm['spec_sha256']
  for s in rows(p):
   out.append({'id':str(s['id']),'func':s['query_code'].strip(),'ast_repr':serialize_ast_representation(s['nodes'],s['edges']),
               'split':split,'old_demo':s['demonstrations'][0]['function_uid'],'old_demo_label':int(s['demonstrations'][0]['target'])})
  provenance.append({'split':split,'specs_sha256':bm['spec_sha256']})
 return out,provenance

def direct(retriever,q):
 # Baseline AST serializer only reads the ordered type tokens; edges are unused.
 target={'func':q['func'],'nodes':[{'type':t} for t in q['ast_repr'].split()],'edges':[]}
 return retriever.retrieve_single(target)

def retrieve_many(bank,encoder,qq,dataset,kind):
 result_path=OUT/'cache'/f'{dataset}_{kind}_retrieval.json'
 inputs={'bank_sha256':file_sha(OUT/'cache'/f'{dataset}_{kind}_bank.jsonl'),
         'queries_sha256':sha_text(json.dumps(qq,ensure_ascii=False,sort_keys=True)),
         'retrieval_engine_sha256':file_sha(BASE/'retrieval_engine.py'),
         'embedding_engine_sha256':file_sha(BASE/'embedding_engine.py'),
         'embedding_cache':encoder.provenance}
 if result_path.exists():
  saved=read(result_path)
  if saved.get('inputs')==inputs:
   print(dataset,kind,'reuse verified retrieval',len(saved['selected_ids']),flush=True)
   return saved['selected_ids'],saved['performance']
 retriever=DemonstrationRetriever(encoder,profile='code');retriever.fit(bank)
 np.savez_compressed(OUT/'cache'/f'{dataset}_{kind}_whitening.npz',mu=retriever.mu,w=retriever.w)
 qx=apply_whitening(encoder.encode([q['func'] for q in qq]),retriever.mu,retriever.w)
 selected=[];ambiguous=0;verified=0;began=time.monotonic()
 for start in range(0,len(qq),64):
  qs=qq[start:start+64];similarity=retriever.train_vecs @ qx[start:start+64].T
  top=np.argpartition(-similarity,5,axis=0)[:6,:]
  for j,q in enumerate(qs):
   order=top[:,j][np.argsort(-similarity[top[:,j],j])]
   # Batched BLAS can differ in last bits. Near ties use the baseline scalar path.
   gaps=np.abs(np.diff(similarity[order,j]));near=bool(np.any(gaps<=1e-10))
   if near:
    result=direct(retriever,q);best_id=result['demo']['id'];ambiguous+=1
   else:
    best_id=None;best_score=-1
    for idx in order[:5]:
     cand=bank[int(idx)]
     if sha_text(cand['func'])==sha_text(q['func']):raise ValueError('Exact target duplicate survived donor sanitation')
     score,_,_=compute_hybrid_score(q['func'],q['ast_repr'],cand['func'],cand['ast_repr'])
     if score>best_score:best_score=score;best_id=cand['id']
   # Verify every changed demo against the unmodified baseline scalar method.
   if best_id!=q['old_demo']:
    baseline=direct(retriever,q);verified+=1
    if best_id!=baseline['demo']['id']:best_id=baseline['demo']['id']
   selected.append(best_id)
  elapsed=time.monotonic()-began
  print(dataset,kind,'retrieval',len(selected),'/',len(qq),f'{len(selected)/max(elapsed,1e-9):.1f}/s',flush=True)
 performance={'ambiguous_scalar_fallbacks':ambiguous,'changed_demo_scalar_checks':verified,'seconds':time.monotonic()-began}
 write(result_path,{'inputs':inputs,'selected_ids':selected,'performance':performance})
 return selected,performance

def inventory():
 unique={};sources=[];conflicts=[]
 for folder in sorted(ROOT.glob('[0-9][0-9]_*')):
  for p in folder.rglob('records.jsonl'):
   if any(t in str(p) for t in ('offline_test','pytest','threshold_pipeline_tests')):continue
   rr=list(rows(p))
   if not rr:continue
   mp=p.parent/'run_manifest.json'
   if not mp.exists():raise ValueError(f'No run manifest for {p}')
   m=read(mp);sources.append({'path':p.relative_to(ROOT).as_posix(),'count':len(rr),'sha256':file_sha(p),'manifest':m})
   for r in rr:
    key=(r['arm'],r['dataset'],r['split'],int(r.get('seed',42)),str(r['id']),r['prompt_sha256'],r.get('model_sha256'))
    if r.get('model_sha256')!=m.get('model_sha256'):raise ValueError('Record/manifest model mismatch')
    if key not in unique:unique[key]={'record':r,'manifest':m,'paths':[]}
    elif any(unique[key]['record'].get(k)!=r.get(k) for k in ('s','valid','label')):conflicts.append(list(key))
    unique[key]['paths'].append(p.relative_to(ROOT).as_posix())
 write(OUT/'downloaded_output_inventory.json',{'created_utc':datetime.now(timezone.utc).isoformat(),'sources':sources,
                                               'unique_records':len(unique),'score_conflicts':conflicts})
 if conflicts:raise ValueError('Conflicting scores for duplicate inference identities; inspect inventory')
 print('Downloaded inference:',dict(Counter(k[0] for k in unique)),flush=True)
 return unique

def render_new_b2(old,spec,new_demo,counter):
 from grace_diag.probes import ANSWER
 previous=spec['demonstrations'][0];meta=old['tokens']
 old_code=previous['func'].strip()
 if meta.get('demo_truncated'):old_code=counter.fit(old_code,1500).text
 old_word='Vulnerable' if int(previous['target']) else 'Non-vulnerable'
 suffix=f'\n\nThe following is an example, and it is {old_word}.\n{old_code}\n\n{ANSWER}'
 if not old['prompt'].endswith(suffix):raise ValueError(f'Cannot identify exact old B2 demo payload {old["id"]}')
 fitted=counter.fit(new_demo['func'].strip(),1500)
 word='Vulnerable' if int(new_demo['target']) else 'Non-vulnerable'
 new_prompt=old['prompt'][:-len(suffix)]+f'\n\nThe following is an example, and it is {word}.\n{fitted.text}\n\n{ANSWER}'
 metadata=dict(meta);metadata.update(demo_tokens_used=fitted.tokens,demo_truncated=fitted.truncated,
        demo_below_25_percent=bool(fitted.original_tokens and fitted.tokens<.25*fitted.original_tokens),
        prompt_tokens=counter.count_chat(new_prompt),prompt_utf8_bytes=len(new_prompt.encode()))
 if metadata['prompt_tokens']+64>8192:raise ValueError('New B2 prompt overflow')
 return dict(old,prompt=new_prompt,prompt_sha256=sha_text(new_prompt),demo_ids=[new_demo['id']],tokens=metadata)

def main():
 if (OUT / "summary.json").exists():
  raise SystemExit("Historical reconciliation already exists; do not overwrite it. Use a new version/output directory and add support for newly imported arms first. B2-flip I-06 is audited separately.")
 OUT.mkdir(parents=True,exist_ok=True)
 downloaded=inventory()
 from transformers import AutoTokenizer
 tokenizer=AutoTokenizer.from_pretrained('Qwen/Qwen3-Coder-30B-A3B-Instruct',revision='b2cff646eb4bb1d68355c01b18ae02e7cf42d120',local_files_only=True)
 counter=TokenCounter(None);counter.tok=tokenizer;counter.approx=False
 audit=[];bank_summaries={};new_rows={};demo_changes=[];rerun_rows=defaultdict(dict)
 snapshot_sha=file_sha(FROZEN/'freeze_manifest.json')
 datasets=sorted({k[1] for k in downloaded if k[0] in ('B2','B2-flip','B2-rep')})
 for dataset in datasets:
  old_path=REF/dataset/'validation/specs.jsonl.donors.jsonl';old_m=read(REF/dataset/'validation/specs.jsonl.manifest.json')
  test_m=read(REF/dataset/'test/specs.jsonl.manifest.json')
  assert old_m['donor_sha256']==test_m['donor_sha256'],'Legacy val/test did not use same donor bank'
  old_bank,om=compact_bank(old_path,dataset,'old',old_m['donor_sha256'])
  fs=read(FROZEN/dataset/'stats.json')
  new_bank,nm=compact_bank(FROZEN/dataset/'donors.jsonl',dataset,'new',fs['files_sha256']['donors.jsonl'])
  same=om['ordered_retrieval_fingerprint']==nm['ordered_retrieval_fingerprint']
  qq,qproof=queries(dataset);encoder=CachedEncoder(dataset)
  if same:
   ids=[q['old_demo'] for q in qq];repro={'method':'identical ordered donor IDs/code/labels/AST and same cached vector lookup; retrieval unchanged'}
   print(dataset,'ordered bank identical: no donor-induced demo changes',flush=True)
  else:
   old_ids,old_perf=retrieve_many(old_bank,encoder,qq,dataset,'old')
   failures=[{'id':q['id'],'cached_demo':q['old_demo'],'recomputed_old_demo':uid} for q,uid in zip(qq,old_ids) if q['old_demo']!=uid]
   write(OUT/'cache'/f'{dataset}_old_reproduction.json',{'n':len(qq),'mismatches':failures,'performance':old_perf})
   if failures:raise ValueError(f'{dataset}: {len(failures)} old demo reproduction mismatches; cannot attribute changes purely to donor yet')
   ids,perf=retrieve_many(new_bank,encoder,qq,dataset,'new')
   repro={'old_demo_reproduced':len(qq),'old_performance':old_perf,'new_performance':perf}
  choice={q['id']:uid for q,uid in zip(qq,ids)};bank={r['id']:r for r in new_bank}
  bank_summaries[dataset]={'old':om,'new':nm,'ordered_retrieval_bank_identical':same,'reproduction':repro,
                           'codet5_cache':encoder.provenance,'query_specs':qproof}
  write(OUT/f'{dataset}_retrieval_provenance.json',bank_summaries[dataset])
  for split in ('validation','test'):
   folder=OUT/'new_reference/B2'/dataset/split;folder.mkdir(parents=True,exist_ok=True)
   original={r['id']:r for r in rows(REF/dataset/split/'prompts.jsonl')};bm=read(REF/dataset/split/'bundle_manifest.json')
   assert file_sha(REF/dataset/split/'prompts.jsonl')==bm['prompts_sha256']
   changed=0
   with (folder/'prompts.jsonl').open('w',encoding='utf-8',newline='\n') as f:
    for spec in rows(REF/dataset/split/'specs.jsonl'):
     uid=spec['id'];old=original[uid];demo=bank[choice[uid]];previous=spec['demonstrations'][0]
     if sha_text(old['prompt'])!=old['prompt_sha256']:raise ValueError('Old prompt hash mismatch')
     if demo['id']==previous['function_uid'] and demo['func'].strip()==previous['func'].strip() and demo['target']==int(previous['target']):
      new=dict(old)
     else:new=render_new_b2(old,spec,demo,counter)
     new.update(arm='B2',prompt_variant='b2_frozen_donor_reconciled_v1',donor_snapshot_sha256=snapshot_sha)
     append(f,new);new_rows[dataset,split,uid]=new
     row={'dataset':dataset,'split':split,'id':uid,'old_demo_id':previous['function_uid'],'new_demo_id':demo['id'],
          'demo_id_changed':demo['id']!=previous['function_uid'],'old_demo_removed_from_new_bank':previous['function_uid'] not in bank,
          'demo_code_changed':demo['func'].strip()!=previous['func'].strip(),'demo_label_changed':demo['target']!=int(previous['target']),
          'old_prompt_sha256':old['prompt_sha256'],'new_prompt_sha256':new['prompt_sha256'],'prompt_changed':new['prompt_sha256']!=old['prompt_sha256']}
     demo_changes.append(row);changed+=row['prompt_changed']
   write(folder/'manifest.json',{'arm':'B2','dataset':dataset,'split':split,'count':len(original),'prompt_changes':changed,
        'prompts_sha256':file_sha(folder/'prompts.jsonl'),'review_only':True,'active_original_bundle_unchanged':True})
   print('Prompt comparison',dataset,split,'changed',changed,'/',len(original),flush=True)
 # Match the exact downloaded request, not only the current arm name/target ID.
 prompt_cache={}
 for key,item in downloaded.items():
  arm,dataset,split,seed,uid,old_hash,model=key
  if (arm,dataset,split) not in prompt_cache:
   if arm=='B2':p=REF/dataset/split/'prompts.jsonl'
   else:
    folders={'B0':'02_Arm_B0_Source_Only','B1':'03_Arm_B1_Graph_Only','B2-flip':'04_Arm_B2_Flip','B2-rep':'05_Arm_B2_Rep'}
    if arm not in folders:raise ValueError(f'Additional downloaded arm {arm} requires its donor selector to be audited')
    p=ROOT/folders[arm]/'output/bundles'/dataset/split/'prompts.jsonl'
   prompt_cache[arm,dataset,split]={r['id']:r for r in rows(p)}
  original=prompt_cache[arm,dataset,split].get(uid)
  if original is None or original['prompt_sha256']!=old_hash:raise ValueError(f'Cannot match exact original request {arm}/{dataset}/{split}/{uid}')
  if item['record']['label']!=original['label']:raise ValueError('Output label differs from original prompt metadata')
  if arm in ('B0','B1'):
   new=original;decision='keep_no_donor_dependency'
  elif arm=='B2':
   new=new_rows[dataset,split,uid];decision='rerun_changed_prompt' if new['prompt_sha256']!=old_hash else 'keep_identical_prompt'
  else:raise ValueError(f'{arm} downloaded now: need paired derivative export before finishing')
  audit.append({'arm':arm,'dataset':dataset,'split':split,'seed':seed,'id':uid,'decision':decision,
                'old_prompt_sha256':old_hash,'new_prompt_sha256':new['prompt_sha256'],'model_sha256':model,
                'old_demo_ids':original.get('demo_ids',[]),'new_demo_ids':new.get('demo_ids',[]),
                'source_record_paths':item['paths']})
  if decision.startswith('rerun'):
   rerun_rows[arm,dataset,split][uid]=new
 # Final exports written only after every matched input passes validation.
 for (arm,dataset,split),rr in rerun_rows.items():
  p=OUT/'rerun_inputs'/arm/dataset/split/'prompts.jsonl';p.parent.mkdir(parents=True,exist_ok=True)
  with p.open('w',encoding='utf-8',newline='\n') as f:
   for uid in sorted(rr):append(f,rr[uid])
  write(p.parent/'manifest.json',{'arm':arm,'dataset':dataset,'split':split,'count':len(rr),
        'prompts_sha256':file_sha(p),'review_only':True,'is_full_split':False,'llm_calls':0})
 for name,rr in [('demo_comparison',demo_changes),('downloaded_record_decisions',audit)]:
  with (OUT/f'{name}.jsonl').open('w',encoding='utf-8',newline='\n') as f:
   for r in rr:append(f,r)
  if rr:
   with (OUT/f'{name}.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader()
    for r in rr:w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in r.items()})
 counts=Counter((r['arm'],r['dataset'],r['split'],r['decision']) for r in audit)
 result={'created_utc':datetime.now(timezone.utc).isoformat(),'numpy':np.__version__,'python':platform.python_version(),
         'unique_downloaded_records':len(downloaded),'banks':bank_summaries,'decisions':[{'arm':a,'dataset':d,'split':s,'decision':decision,'n':n} for (a,d,s,decision),n in sorted(counts.items())],
         'llm_calls':0,'active_prompts_modified':False,'thresholds_modified':False,
         'instruction':'Only changed prompts require new inference under the same model/settings. Rerun inputs are review JSONL, not a full validation bundle; do not fit thresholds on the rerun subset.'}
 write(OUT/'summary.json',result)
 print('DONE',json.dumps(result['decisions']),flush=True)

if __name__=='__main__':
 with threadpool_limits(limits=4):main()
