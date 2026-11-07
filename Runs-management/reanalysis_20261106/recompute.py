import json,hashlib,csv,sys,math
from pathlib import Path
import numpy as np
from sklearn.metrics import roc_auc_score,average_precision_score
ROOT=Path(__file__).resolve().parents[2]; OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'01_Author_Baseline_Unified/diagnostic_kit/src'))
from grace_diag import stats as S
status=json.loads((ROOT/'Runs-management/current_status.json').read_text(encoding='utf-8'))
inputs=[]; data={}; thresholds={}; metrics=[]; contrasts=[]; sensitivity=[]; diagnostics=[]
def read(p):
 p=ROOT/p; raw=p.read_bytes(); inputs.append({'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest()})
 return [json.loads(x) for x in raw.decode('utf-8-sig').splitlines() if x.strip()]
for arm in status['arms']:
 if arm['arm'] not in ['B0','B1','B2','B2-flip']: continue
 for sp in arm['splits']:
  rs=read(sp['records_path']); assert len(rs)==sp['expected']; assert len({r['id'] for r in rs})==len(rs)
  for r in rs:
   assert r['arm']==arm['arm'] and r['split']==sp['split'] and r['dataset']==sp['dataset']
   assert r['valid'] and math.isfinite(r['s']) and r['label'] in [0,1]
   z=r['logprob_1']-r['logprob_0']; expected=1/(1+math.exp(-z))
   assert abs(expected-r['s'])<1e-10
  data[(sp['dataset'],arm['arm'],sp['split'])]={r['id']:r for r in rs}
for ds in ['devign','reveal']:
 manifests={r['id']:r for r in read(f'01_Author_Baseline_Unified/output/research_freeze_20261101/{ds}/test_manifest.jsonl')}
 ids=sorted(data[ds,'B0','test']); assert set(ids)==set(manifests)
 y=np.array([data[ds,'B0','test'][i]['label'] for i in ids]); scores={}; preds={}
 for arm in ['B0','B1','B2','B2-flip']:
  val=data[ds,arm,'validation']; test=data[ds,arm,'test']; assert set(test)==set(ids)
  vi=sorted(val); vy=np.array([val[i]['label'] for i in vi]); vs=np.array([val[i]['s'] for i in vi])
  assert all(test[i]['label']==manifests[i]['label']==int(y[k]) for k,i in enumerate(ids))
  if arm=='B2-flip': tau=thresholds[f'{ds}|B2']['tau']; vm=S.mcc(vy,(vs>=tau).astype(int)); policy='inherit_recomputed_B2'
  else: tau,vm=S.pick_threshold(vy,vs); policy='full_validation_argmax_MCC_grid_0.01_0.99'
  thresholds[f'{ds}|{arm}']={'tau':tau,'validation_mcc':vm,'n_validation':len(val),'policy':policy}
  scores[arm]=np.array([test[i]['s'] for i in ids]); preds[arm]=(scores[arm]>=tau).astype(int)
  for part in ['full','no_exact_or_near_train']:
   mask=np.ones(len(ids),dtype=bool) if part=='full' else np.array([not(manifests[i].get('exact_train') or manifests[i].get('near_train')) for i in ids])
   yy=y[mask]; ss=scores[arm][mask]
   for mode,t in [('validation_tau',tau),('fixed_0.5',.5)]:
    pp=(ss>=t).astype(int); m=S.thresholded_metrics(yy,pp)
    metrics.append({'dataset':ds,'arm':arm,'partition':part,'mode':mode,'tau':t,'auroc':float(roc_auc_score(yy,ss)),'auprc_AP':float(average_precision_score(yy,ss)),'prevalence':float(yy.mean()),'invalid_score':0,'raw_invalid':sum(not test[i].get('response_valid',True) for k,i in enumerate(ids) if mask[k]),**m})
  diagnostics.append({'dataset':ds,'arm':arm,'n':len(ids),'excluded_exact_or_near':sum(manifests[i].get('exact_train') or manifests[i].get('near_train') for i in ids)})
 for name,pp in [('ALL-0',np.zeros(len(y),dtype=int)),('ALL-1',np.ones(len(y),dtype=int))]:
  metrics.append({'dataset':ds,'arm':name,'partition':'full','mode':'constant','tau':None,'auroc':.5,'auprc_AP':float(y.mean()),'prevalence':float(y.mean()),**S.thresholded_metrics(y,pp)})
 # Freeze thresholds while resampling test; validation threshold uncertainty is not included.
 if ds=='devign':
  groups=[manifests[i].get('commit_id') or ('missing:'+i) for i in ids]; unit='commit_id; missing IDs treated as singleton'
 else:
  from collections import Counter
  raw={r['id']:r for r in read('01_Author_Baseline_Unified/output/local_full/reveal/raw/test.jsonl')}
  old=list(csv.DictReader((ROOT/'Runs-management/step0_diagnostic/reveal/canonical_reveal_test.csv').open(encoding='utf-8')))
  inputs.append({'path':'Runs-management/step0_diagnostic/reveal/canonical_reveal_test.csv','sha256':hashlib.sha256((ROOT/'Runs-management/step0_diagnostic/reveal/canonical_reveal_test.csv').read_bytes()).hexdigest()})
  assert set(raw)==set(ids)
  assert all(raw[i]['target']==int(y[k]) for k,i in enumerate(ids))
  assert Counter((str(r['source_id']),int(r['target'])) for r in raw.values())==Counter((r['group'],int(r['y'])) for r in old)
  groups=[str(raw[i]['source_id']) for i in ids]; assert len(set(groups))==646
  unit='source_id file-hash clusters; mapped through raw test IDs and matched against historical canonical group-label counts'
 uniq,inv=np.unique(groups,return_inverse=True); G=len(uniq); rng=np.random.default_rng(20261117)
 # Use multiplicities to resample entire clusters, preserving score ties.
 def auc_weighted(s,w):
  order=np.argsort(s,kind='stable'); st=s[order]; yy=y[order]; ww=w[order]
  starts=np.r_[0,np.flatnonzero(st[1:]!=st[:-1])+1]
  pos=np.add.reduceat(ww*yy,starts); neg=np.add.reduceat(ww*(1-yy),starts)
  den=pos.sum()*neg.sum()
  return float(np.sum(pos*(np.cumsum(neg)-neg+.5*neg))/den) if den else float('nan')
 def mcc_weighted(p,w):
  tp=np.sum(w*((y==1)&(p==1))); tn=np.sum(w*((y==0)&(p==0))); fp=np.sum(w*((y==0)&(p==1))); fn=np.sum(w*((y==1)&(p==0)))
  den=float((tp+fp)*(tp+fn)*(tn+fp)*(tn+fn))**.5
  return float((tp*tn-fp*fn)/den) if den else float('nan')
 pairs=[('B0','B2'),('B0','B1'),('B1','B2'),('B2','B2-flip')]
 draws={(a,b,k):[] for a,b in pairs for k in ['auroc','mcc']}
 for rep in range(5000):
  counts=np.bincount(rng.integers(0,G,G),minlength=G); w=counts[inv].astype(float)
  av={a:auc_weighted(s,w) for a,s in scores.items()}; mv={a:mcc_weighted(p,w) for a,p in preds.items()}
  for a,b in pairs:
   draws[a,b,'auroc'].append(av[b]-av[a]); draws[a,b,'mcc'].append(mv[b]-mv[a])
 for a,b in pairs:
  for metric in ['auroc','mcc']:
   vals=np.array(draws[a,b,metric]); finite=vals[np.isfinite(vals)]; lo,hi=np.percentile(finite,[2.5,97.5]); margin=.02 if metric=='auroc' else .03
   delta=float(roc_auc_score(y,scores[b])-roc_auc_score(y,scores[a])) if metric=='auroc' else S.mcc(y,preds[b])-S.mcc(y,preds[a])
   verdict='harm' if hi<0 else ('benefit' if lo>0 and delta>=margin else ('no_meaningful_benefit' if hi<margin else 'inconclusive'))
   contrasts.append({'dataset':ds,'a':a,'b':b,'direction':'b minus a','metric':metric,'delta':delta,'ci95_lo':float(lo),'ci95_hi':float(hi),'margin':margin,'verdict':verdict,'n_boot':5000,'degenerate':5000-len(finite),'resampling_unit':unit,'n_groups':G,'status':'posthoc_reanalysis; unadjusted CI; not full preregistered family'})
 for mode,pa,pb in [('validation_tau',preds['B2'],preds['B2-flip']),('fixed_0.5',(scores['B2']>=.5),(scores['B2-flip']>=.5))]:
  sensitivity.append({'dataset':ds,'mode':mode,'n':len(y),'changed':int(np.sum(pa!=pb)),'fraction':float(np.mean(pa!=pb)),'net_label_sensitivity':None,'reason':'B2-rep absent; cannot subtract natural variability'})
 print(ds,'done',len(y),'groups',G,flush=True)
result={'analysis':'Requested posthoc recalculation from validation and test records; no frozen threshold file read for fitting','seed':20261117,'thresholds':thresholds,'metrics':metrics,'contrasts':contrasts,'sensitivity':sensitivity,'diagnostics':diagnostics,'inputs':inputs,'limitations':['95% CIs are unadjusted; full preregistered contrast family incomplete','Thresholds fixed during test bootstrap; validation selection uncertainty excluded','AP computed using sklearn average_precision_score with score ties handled','No new supervised anchor/meta-model inference; RQ5/RQ6 not established by these four arms']}
(OUT/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
for name,rows in [('metrics',metrics),('contrasts',contrasts),('sensitivity',sensitivity)]:
 keys=list(dict.fromkeys(k for row in rows for k in row))
 with (OUT/(name+'.csv')).open('w',encoding='utf-8-sig',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=keys); writer.writeheader();writer.writerows(rows)
print(json.dumps(thresholds,indent=2),flush=True)
