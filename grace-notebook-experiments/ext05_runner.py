"""Ext05 validation-only marginalized-block P_post runner.

Only D1 and D2 are implemented. All validation parquet reads use Ext03's
audited validation-predicate helper.
"""
from __future__ import annotations

import hashlib, json, shutil, sys, platform
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import expit, logit
from sklearn.metrics import (average_precision_score, roc_auc_score,
    matthews_corrcoef, balanced_accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix)
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

import ext03_runner as ext3

HOME=Path(__file__).resolve().parent
ROOT=HOME.parent
OUT=HOME/'runs/independent-post-ext05-llm-block-marginalization-validation'
PRE=OUT/'preflight'
FULL=OUT/'full'
PROTOCOL=HOME/'ext05_protocol_vi.md'
EXT03=HOME/'runs/independent-post-ext03-multisignal-validation/full'
EXT03_PREF=HOME/'runs/independent-post-ext03-multisignal-validation/preflight'
EXT04=HOME/'runs/independent-post-ext04-decision-aware-validation/full'
EXT04_PREF=HOME/'runs/independent-post-ext04-decision-aware-validation/preflight'
BASE=20261123
CS=(0.001,0.01,0.05,0.1,1.0)
CANDS=('D1','D2')
ARMS=list(ext3.ARMS)
WIDTHS={'D1':41,'D2':41}
MODEL_SHA=ext3.MODEL_SHA

def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def atomic_json(path,obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix(path.suffix+'.tmp')
    temp.write_text(json.dumps(obj,indent=2,allow_nan=False),encoding='utf-8')
    temp.replace(path)

def estimator(c):return ext3.est(c)
def group_folds(y,g,seed):return ext3.folds(np.asarray(y),np.asarray(g).astype(str),int(seed))

def threshold(y,p):
    ts=np.arange(.01,1,.01)
    return float(max(ts,key=lambda t:(matthews_corrcoef(y,p>=t),-abs(t-.5),-t)))

def load_inputs():
    m=ext3.read_validation(ext3.SOURCE/'inputs.parquet',[
        'id','dataset','target_label','group_id','donor_id','donor_label','donor_snapshot','evidence_status'])
    if m.duplicated(['dataset','id']).any():raise ValueError('duplicate validation IDs')
    return m

def build_sources(meta,ds):
    m=meta[meta.dataset==ds].sort_values('id').reset_index(drop=True)
    ids=m.id.astype(str).tolist();y=m.target_label.to_numpy(int);g=m.group_id.astype(str).to_numpy()
    if len(ids)!=len(set(ids)) or np.unique(y).size!=2 or m.group_id.isna().any():raise ValueError(f'{ds}: validation ID/label/group integrity failed')
    if not m.donor_id.astype(str).str.startswith(ds+':train:').all() or (m.id==m.donor_id).any():raise ValueError(f'{ds}: donor namespace/self-donor failure')
    if not np.isfinite(m.donor_label.to_numpy(float)).all() or not set(m.donor_label.astype(int).unique()).issubset({0,1}):raise ValueError(f'{ds}: donor label failure')
    if m.donor_snapshot.nunique()!=1:raise ValueError(f'{ds}: mixed donor snapshot')
    z=np.load(ext3.H3/ds/'xpre_validation.npz',allow_pickle=False)
    names=z['feature_names'].astype(str).tolist();pos=pd.Index(z['ids'].astype(str)).get_indexer(ids);x=z['X'][pos].astype(float);z.close()
    if (pos<0).any() or len(names)!=34 or names[5]!='p_gate' or x.shape!=(len(ids),34) or not np.isfinite(x).all():raise ValueError(f'{ds}: frozen H3-B schema/alignment failure')
    lg,prov=ext3.load_arms(ds,ids,y,g);probs={a:expit(v) for a,v in lg.items()}
    if set(probs)!=set(ARMS) or any(not np.isfinite(v).all() for v in probs.values()):raise ValueError(f'{ds}: raw arm registry/finite check failure')
    e=ext3.read_validation(ext3.SOURCE/'inputs.parquet',['id','dataset','evidence_status'])
    ev=e[e.dataset==ds].set_index('id').reindex(ids).evidence_status.to_numpy()
    if pd.isna(ev).any():raise ValueError(f'{ds}: evidence status missing')
    return {'meta':m,'ids':ids,'y':y,'g':g,'x':x,'names':names,'donor':m.donor_label.to_numpy(float),
            'logits':lg,'arms':probs,'evidence':ev,'provenance':prov}

def feature_matrix(data,cand,rows,train_rows):
    x=data['x'];L=data['logits'];P=data['arms'];d=data['donor']
    X=x[rows];b=L['B2'][rows]
    u=(2*d[rows]-1)*np.tanh((b-L['B2-flip'][rows])/2)
    A=P['B2'][rows]-P['B2-labelonly'][rows]
    r=np.mean(np.column_stack([P[f'B2-rand-{s}'][rows] for s in (42,43,44)]),axis=1)
    s=np.mean(np.column_stack([P[f'B1-shuf-{s}'][rows] for s in (42,43,44)]),axis=1)
    R=P['B2'][rows]-r;G=P['B1'][rows]-s;H=P['B1-H2'][rows]-P['B1'][rows];D=P['B2'][rows]-P['B2-nolabel'][rows]
    additions=[b,u,A,R,G,H,D]
    if cand not in CANDS:raise ValueError(f'unregistered candidate: {cand}')
    z=np.column_stack([X,*additions]).astype(float)
    if z.shape[1]!=WIDTHS[cand] or not np.isfinite(z).all():raise ValueError(f'{cand}: matrix width/finite assertion failed')
    return z,None

def prepare_masked_objective(data,cand,train_rows,predict_rows):
    """Scale unique unmasked rows once, then create the fixed two-copy objective."""
    ztr,_=feature_matrix(data,cand,train_rows,train_rows)
    zva,_=feature_matrix(data,cand,predict_rows,train_rows)
    scaler=StandardScaler().fit(ztr)
    st=scaler.transform(ztr);sv=scaler.transform(zva)
    xbase=st[:,:34];block=st[:,34:]
    if st.shape[1]!=41 or block.shape[1]!=7:raise ValueError('masked objective requires 34+7 scaled columns')
    if cand=='D1':
        copy0=np.column_stack([xbase,block[:,0],np.zeros_like(block[:,1:])])
        copy1=np.column_stack([xbase,block[:,0],2*block[:,1:]])
    elif cand=='D2':
        copy0=np.column_stack([xbase,np.zeros_like(block)])
        copy1=np.column_stack([xbase,2*block])
    else:raise ValueError(f'unregistered candidate: {cand}')
    yy=data['y'][train_rows];aug=np.vstack([copy0,copy1]);yaug=np.concatenate([yy,yy]);weights=np.full(2*len(yy),.5)
    if not np.isclose(weights.sum(),len(yy)):raise ValueError('weighted-copy total weight must equal unique training N')
    return {'augmented_X':aug,'augmented_y':yaug,'sample_weight':weights,'scaled_inference':sv,
        'audit':{'scaler_fit_rows':len(train_rows),'copies_per_row':2,'copy_weight':.5,
            'total_sample_weight':float(weights.sum()),'objective_mask':cand,'scaler_fit_on':'unique unmasked rows'}}

def fit_prepared_masked(prepared,C):
    lr=LogisticRegression(C=float(C),solver='lbfgs',max_iter=3000,penalty='l2')
    lr.fit(prepared['augmented_X'],prepared['augmented_y'],sample_weight=prepared['sample_weight'])
    return lr.predict_proba(prepared['scaled_inference'])[:,1]

def fit_masked_predict(data,cand,C,train_rows,predict_rows):
    prepared=prepare_masked_objective(data,cand,train_rows,predict_rows)
    return fit_prepared_masked(prepared,C),prepared['audit']

def frozen_pre(data,Q,seed):
    """Ext03 P_pre helper: grouped-OOF C and threshold, then fit all Q."""
    y=data['y'];g=data['g'];x=data['x'];yy=y[Q];gg=g[Q]
    splits=group_folds(yy,gg,seed);oof_by_c={float(c):np.full(len(Q),np.nan) for c in CS}
    for tr,va in splits:
        for c in CS:oof_by_c[float(c)][va]=estimator(c).fit(x[Q[tr]],yy[tr]).predict_proba(x[Q[va]])[:,1]
    if any(not np.isfinite(v).all() for v in oof_by_c.values()):raise ValueError('FrozenPre incomplete OOF predictions')
    aps={c:float(average_precision_score(yy,p)) for c,p in oof_by_c.items()}
    chosen=max(CS,key=lambda c:(aps[float(c)],-float(c)));poof=oof_by_c[float(chosen)];tau=threshold(yy,poof)
    model=estimator(chosen).fit(x[Q],yy)
    return {'C':float(chosen),'oof':poof,'tau':tau,'model':model,'AP_by_C':{str(c):aps[float(c)] for c in CS}}

def select_post_c(data,Q,cand,split_seed,child_seed_fn):
    """Nested, decision-aware candidate C selection; no held-out label leakage."""
    y=data['y'];g=data['g'];yy=y[Q];gg=g[Q];splits=group_folds(yy,gg,split_seed)
    pred={float(c):np.full(len(Q),np.nan) for c in CS};pre=np.full(len(Q),np.nan);tau=np.full(len(Q),np.nan);detail=[]
    for k,(tr,va) in enumerate(splits):
        A=Q[tr];B=Q[va];frozen=frozen_pre(data,A,child_seed_fn(k))
        pre[va]=frozen['model'].predict_proba(data['x'][B])[:,1];tau[va]=frozen['tau']
        prepared=prepare_masked_objective(data,cand,A,B)
        for c in CS:pred[float(c)][va]=fit_prepared_masked(prepared,c)
        detail.append({'fold':k,'train_n':len(A),'heldout_n':len(B),'child_seed':int(child_seed_fn(k)),
            'P_pre_C':frozen['C'],'tau_A':frozen['tau'],'mask_objective':prepared['audit']})
    if not np.isfinite(pre).all() or not np.isfinite(tau).all() or any(not np.isfinite(p).all() for p in pred.values()):
        raise ValueError(f'{cand}: SelectPostC OOF incomplete')
    aps={float(c):float(average_precision_score(yy,p)) for c,p in pred.items()}
    refap={arm:float(average_precision_score(yy,p[Q])) for arm,p in data['arms'].items()}
    rows=[]
    for c in CS:
        feasible=all(aps[float(c)]>v for v in refap.values())
        dm=float(matthews_corrcoef(yy,pred[float(c)]>=tau)-matthews_corrcoef(yy,pre>=tau))
        rows.append({'C':float(c),'AP':aps[float(c)],'AP_beats_all_15':bool(feasible),'delta_MCC_pooled':dm})
    feasible=[r for r in rows if r['AP_beats_all_15']]
    chosen=max(feasible,key=lambda r:(r['delta_MCC_pooled'],-r['C']))['C'] if feasible else None
    return {'C':chosen,'candidate':cand,'split_seed':int(split_seed),'folds':detail,'C_diagnostics':rows,
        'pre_oof':pre,'tau_oof':tau,'candidate_oof':pred.get(chosen) if chosen is not None else None,
        'candidate_oof_by_C':pred,'AP_by_C':aps,'complete':True}

def group_draws(g,B,seed):
    unique,inv=np.unique(g,return_inverse=True);rng=np.random.default_rng(seed)
    return np.asarray([np.bincount(rng.integers(0,len(unique),len(unique)),minlength=len(unique))[inv] for _ in range(B)],dtype=np.int32)

def idx_from_weights(w):return np.repeat(np.arange(len(w)),w)

def bootstrap_delta_mcc(y,g,tau,pre,cands,B,seed,draws=None):
    W=draws if draws is not None else group_draws(g,B,seed)
    out={name:[] for name in cands};valid=0
    for w in W:
        ix=idx_from_weights(w)
        if not len(ix) or np.unique(y[ix]).size<2:continue
        valid+=1;base=matthews_corrcoef(y[ix],pre[ix]>=tau[ix])
        for name,p in cands.items():out[name].append(matthews_corrcoef(y[ix],p[ix]>=tau[ix])-base)
    return {k:{'attempted':B,'valid':valid,'q025':float(np.quantile(v,.025)) if v else None} for k,v in out.items()}

def metrics(y,p,tau):
    pred=p>=tau;tn,fp,fn,tp=confusion_matrix(y,pred,labels=[0,1]).ravel()
    return {'AP':float(average_precision_score(y,p)),'AUROC':float(roc_auc_score(y,p)),
        'MCC':float(matthews_corrcoef(y,pred)),'balanced_accuracy':float(balanced_accuracy_score(y,pred)),
        'precision':float(precision_score(y,pred,zero_division=0)),'recall':float(recall_score(y,pred,zero_division=0)),
        'F1':float(f1_score(y,pred,zero_division=0)),'confusion':{'tn':int(tn),'fp':int(fp),'fn':int(fn),'tp':int(tp)},
        'positive_rate':float(pred.mean())}

def preflight_smoke():
    OUT.mkdir(parents=True,exist_ok=True);PRE.mkdir(parents=True,exist_ok=True)
    shutil.copy2(PROTOCOL,OUT/'ext05_protocol_vi.md')
    meta=load_inputs();donor_audit,donor_hashes=ext3.verify_donors(meta);registry={'sources':{},'datasets':{},'protocol_sha256':sha(PROTOCOL)}
    registry['sources'][str(ext3.SOURCE/'inputs.parquet')]={'sha256':sha(ext3.SOURCE/'inputs.parquet'),'read_filter':'split == validation'}
    registry['sources'][str(ext3.SOURCE/'scores.parquet')]={'sha256':sha(ext3.SOURCE/'scores.parquet'),'read_filter':'split == validation'}
    for path in [EXT03/'outer_predictions.csv',EXT03/'results.json',EXT03/'manifest.json',EXT03/'source_audit.json',EXT03/'provenance_hashes.json',
                 EXT03_PREF/'source_registry.json',EXT03_PREF/'smoke.json',HOME/'ext03_runner.py',HOME/'ext03_protocol_vi.md',
                 EXT04/'outer_predictions.csv',EXT04/'results.json',EXT04/'manifest.json',EXT04/'source_audit.json',EXT04/'provenance_hashes.json',
                 EXT04/'pre_p_pre_audit.json',EXT04_PREF/'source_registry.json',EXT04_PREF/'frozen_manifest.json',
                 EXT04_PREF/'smoke.json',HOME/'ext04_runner.py',HOME/'ext04_protocol_vi.md']:
        registry['sources'][str(path)]={'sha256':sha(path)}
    reg3=json.loads((EXT03_PREF/'source_registry.json').read_text(encoding='utf-8'))
    reg4=json.loads((EXT04_PREF/'source_registry.json').read_text(encoding='utf-8'))
    for path,info in reg4['sources'].items():registry['sources'][path]={'sha256':info['sha256'],'via':'Ext04 frozen registry'}
    mask_smoke={}
    for ds in ('devign','reveal'):
        data=build_sources(meta,ds)
        # Record all precise source paths/hashes already audited by Ext03.
        registry['datasets'][ds]={'n':len(data['y']),'groups':int(pd.Series(data['g']).nunique()),
            'validation_ids_sha256':hashlib.sha256('\n'.join(data['ids']).encode()).hexdigest(),
            'H3':{'path':str(ext3.H3/ds/'xpre_validation.npz'),'sha256':sha(ext3.H3/ds/'xpre_validation.npz')},
            'arms':data['provenance'],'donor_bank':donor_audit[ds]}
        for item in reg3['datasets'][ds]['arms']:
            if item.get('path'):
                path=Path(item['path']);registry['sources'][str(path)]={'sha256':item['sha256'],'dataset':ds,'arm':item['arm'],'seed':item.get('seed')}
            elif item.get('arm')=='B2-vs-B2-flip-audit':
                for arm,path,field in [('B2',ROOT/f'runs/final/{ds}/validation/B2/42/records.jsonl','B2_source_sha256'),
                                       ('B2-flip',ROOT/f'runs/final/{ds}/validation/B2-flip/42/records.jsonl','B2_flip_source_sha256')]:
                    registry['sources'][str(path)]={'sha256':item[field],'dataset':ds,'arm':arm,'seed':42}
        # No classifier fits in smoke. Exercise the exact training-only scaler
        # and deterministic weighted-copy design on a validation subset.
        take=np.arange(min(240,len(data['y'])));z,_=feature_matrix(data,'D1',take,take)
        if z.shape[1]!=41 or not np.isfinite(z).all():raise ValueError('T1 smoke matrix invalid')
        mask_smoke[ds]={}
        for cand in CANDS:
            prepared=prepare_masked_objective(data,cand,take,take)
            aug=prepared['augmented_X'];n=len(take)
            if aug.shape!=(2*n,41) or prepared['augmented_y'].shape!=(2*n,) or prepared['sample_weight'].shape!=(2*n,):
                raise ValueError(f'{ds}/{cand}: weighted-copy smoke dimensions failed')
            if not np.isclose(prepared['sample_weight'].sum(),n) or not np.all(prepared['sample_weight']==.5):
                raise ValueError(f'{ds}/{cand}: weighted-copy smoke weights failed')
            avg=(aug[:n]+aug[n:])/2
            if not np.allclose(avg,prepared['scaled_inference'],rtol=0,atol=1e-12):
                raise ValueError(f'{ds}/{cand}: two-copy expectation does not equal unmasked inference features')
            mask_smoke[ds][cand]={'status':'passed','rows':n,'augmented_rows':2*n,
                'sample_weight_sum':float(prepared['sample_weight'].sum()),
                'scaler_fit_rows':prepared['audit']['scaler_fit_rows'],
                'weighted_copy_expectation_matches_unmasked':True,'classifier_fit':'not run'}
    for ds in ('devign','reveal'):
        path=ROOT/f'artifact-packaging/03_data_prompts_records/frozen_inputs/cpg/{ds}/train.jsonl'
        registry['sources'][str(path)]={'sha256':donor_hashes[ds],'scope':'frozen training donor bank only'}
    regpath=PRE/'source_registry.json';atomic_json(regpath,registry)
    frozen={'registered':False,'post_cap_extension':True,'validation_only':True,'test_labels_scores_predictions_read':False,
        'historical_hypothesis_count':'at least 28 before Ext05; at least 30 after two candidates','candidates':list(CANDS),
        'candidate_widths':WIDTHS,'protocol':str(PROTOCOL),'protocol_sha256':sha(PROTOCOL),'runner_sha256':sha(Path(__file__)),
        'source_registry_sha256':sha(regpath),'frozen_Ext03_Ext04_P_pre_only_as_audit_target':True,
        'test_metadata_incident':'Earlier provenance work displayed test IDs/change metadata only; no test labels/scores/predictions were read.',
        'fit_started':False,'smoke_command':"& 'C:\\Users\\yungn\\AppData\\Local\\Programs\\Python\\Python311\\python.exe' ext05_runner.py --smoke",
        'mask_rule':'D1 and D2 use two deterministic whole-block copies at weights 0.5 each after unique-row StandardScaler fit; inference is unmasked'}
    atomic_json(PRE/'frozen_manifest.json',frozen)
    smoke={'status':'passed','datasets':{d:{'rows':registry['datasets'][d]['n'],'unique_arms':15,'D1_width':41,'D2_width':41,'weighted_copy_mask_smoke':mask_smoke[d]} for d in ('devign','reveal')},
        'donor_audit':donor_audit,'runner_sha256':frozen['runner_sha256'],'protocol_sha256':frozen['protocol_sha256'],'source_registry_sha256':frozen['source_registry_sha256']}
    atomic_json(PRE/'smoke.json',smoke)
    return smoke

def assert_frozen_hashes():
    """Must run before loading model inputs or fitting any model."""
    mf=PRE/'frozen_manifest.json';rp=PRE/'source_registry.json';sp=PRE/'smoke.json'
    if not (mf.is_file() and rp.is_file() and sp.is_file()):raise RuntimeError('Ext05 frozen smoke artifacts missing')
    frozen=json.loads(mf.read_text(encoding='utf-8'));sm=json.loads(sp.read_text(encoding='utf-8'))
    if frozen.get('runner_sha256')!=sha(Path(__file__)) or sm.get('runner_sha256')!=sha(Path(__file__)):
        raise RuntimeError('runner SHA changed after smoke; abort before fitting')
    if frozen.get('protocol_sha256')!=sha(PROTOCOL) or sm.get('protocol_sha256')!=sha(PROTOCOL):
        raise RuntimeError('protocol SHA changed after smoke; abort before fitting')
    if frozen.get('source_registry_sha256')!=sha(rp) or sm.get('source_registry_sha256')!=sha(rp):
        raise RuntimeError('source registry SHA changed after smoke; abort before fitting')
    reg=json.loads(rp.read_text(encoding='utf-8'))
    for path,info in reg['sources'].items():
        if not Path(path).is_file() or sha(Path(path))!=info['sha256']:
            raise RuntimeError(f'source hash mismatch before fitting: {path}')
    return frozen

def run(smoke=False):
    if smoke:return preflight_smoke()
    # Hash checks are intentionally the first full-run operation, before model data load/fits.
    frozen=assert_frozen_hashes()
    atomic_json(OUT/'run_state.json',{'state':'hashes_verified_fitting_started','runner_sha256':sha(Path(__file__)),
        'protocol_sha256':sha(PROTOCOL),'source_registry_sha256':sha(PRE/'source_registry.json')})
    meta=load_inputs();donor_audit,donor_hashes=ext3.verify_donors(meta);data_by_ds={d:build_sources(meta,d) for d in ('devign','reveal')}
    # Frozen Ext03/Ext04 P_pre outer-heldout vectors are audit targets only.
    ext3pred=pd.read_csv(EXT03/'outer_predictions.csv',low_memory=False)
    ext3res=json.loads((EXT03/'results.json').read_text(encoding='utf-8'))
    ext4pred=pd.read_csv(EXT04/'outer_predictions.csv',low_memory=False)
    ext4res=json.loads((EXT04/'results.json').read_text(encoding='utf-8'))
    result={};predframes=[];candidate_rows=[];pre_audit={};source_audit={};all_arm_probs={}
    for ds in ('devign','reveal'):
        d=data_by_ds[ds];y=d['y'];g=d['g'];ids=d['ids'];n=len(y);ixall=np.arange(n);outer=group_folds(y,g,BASE+8100)
        old=ext3pred[(ext3pred.dataset==ds)&(ext3pred.model=='P_pre')].set_index('id').reindex(ids)
        old4=ext4pred[(ext4pred.dataset==ds)&(ext4pred.model=='P_pre')].set_index('id').reindex(ids)
        if old.prediction.isna().any() or old4.prediction.isna().any() or not np.array_equal(old.target_label.to_numpy(int),y) or not np.array_equal(old4.target_label.to_numpy(int),y) or not np.array_equal(old.group_id.astype(str).to_numpy(),g) or not np.array_equal(old4.group_id.astype(str).to_numpy(),g):
            raise ValueError(f'{ds}: Ext03/Ext04 frozen P_pre OOF ID/label/group mismatch')
        if set(old.outer_fold.astype(int))!={0,1,2}:raise ValueError('Ext03 P_pre fold IDs invalid')
        pre=np.full(n,np.nan);post=np.full(n,np.nan);common=np.full(n,np.nan);tau=np.full(n,np.nan);fold_rows=[]
        for oi,(T,H) in enumerate(outer):
            inner_seed=BASE+100000+1000*oi
            frozenT=frozen_pre(d,T,inner_seed)
            held_pre=frozenT['model'].predict_proba(d['x'][H])[:,1]
            c_ext=ext3res['datasets'][ds]['outer_folds'][oi]['P_pre_C_outer_train']
            tau_ext=ext3res['datasets'][ds]['outer_folds'][oi]['tau_T']
            c_ext4=ext4res['datasets'][ds]['outer_folds'][oi]['P_pre_C']
            tau_ext4=ext4res['datasets'][ds]['outer_folds'][oi]['P_pre_tau']
            oldfold=old.iloc[H]
            old4fold=old4.iloc[H]
            if abs(frozenT['C']-float(c_ext))>1e-12 or abs(frozenT['tau']-float(tau_ext))>1e-12 or abs(frozenT['C']-float(c_ext4))>1e-12 or abs(frozenT['tau']-float(tau_ext4))>1e-12:
                raise ValueError(f'{ds} fold {oi}: Ext03/Ext04 P_pre C/cutoff audit failed')
            if not np.array_equal(oldfold.outer_fold.to_numpy(int),np.full(len(H),oi)):
                raise ValueError(f'{ds} fold {oi}: Ext03 outer fold membership differs')
            if not np.array_equal(old4fold.outer_fold.to_numpy(int),np.full(len(H),oi)):
                raise ValueError(f'{ds} fold {oi}: Ext04 outer fold membership differs')
            maxpred=float(np.max(np.abs(held_pre-oldfold.prediction.to_numpy(float))))
            maxpred4=float(np.max(np.abs(held_pre-old4fold.prediction.to_numpy(float))))
            if maxpred>1e-12 or maxpred4>1e-12:raise ValueError(f'{ds} fold {oi}: Ext03/Ext04 heldout P_pre probability differs')
            pre[H]=held_pre;tau[H]=frozenT['tau']
            preT=np.full(len(T),np.nan);tauTrows=np.full(len(T),np.nan);cand_oof={c:np.full(len(T),np.nan) for c in CANDS};cand_c_by_i={c:[] for c in CANDS};inner_diagnostics=[]
            for ii,(si,vi) in enumerate(group_folds(y[T],g[T],inner_seed)):
                S=T[si];V=T[vi];subseed=BASE+200000+1000*oi+10*ii
                pres=frozen_pre(d,S,subseed)
                preV=pres['model'].predict_proba(d['x'][V])[:,1]
                for cand in CANDS:
                    deep=lambda k,oi=oi,ii=ii:BASE+400000+10000*oi+100*ii+k
                    selected=select_post_c(d,S,cand,subseed,deep)
                    if selected['C'] is None:
                        cand_c_by_i[cand].append(None)
                        inner_diagnostics.append({'inner_fold':ii,'candidate':cand,'C':None,'status':'no_AP_feasible_C','SelectPostC':selected['C_diagnostics']})
                        continue
                    cand_oof[cand][vi],maskinfo=fit_masked_predict(d,cand,selected['C'],S,V)
                    cand_c_by_i[cand].append(selected['C'])
                    inner_diagnostics.append({'inner_fold':ii,'candidate':cand,'C':selected['C'],'status':'complete','SelectPostC':selected['C_diagnostics'],'mask_objective':maskinfo})
                # P_pre V prediction is separately regenerated per candidate's SelectPostC, but this is the common outer-inner row prediction.
                # Store it once after both candidate calls.
                if not np.isfinite(preV).all():raise ValueError('FrozenPre inner heldout prediction nonfinite')
                # V is indexed in outer-T local coordinates `vi`.
                preT[vi]=preV
                tauTrows[vi]=pres['tau']
            if not np.isfinite(preT).all() or not np.isfinite(tauTrows).all():raise ValueError('outer-training P_pre OOF/tau incomplete')
            refap={a:float(average_precision_score(y[T],p[T])) for a,p in d['arms'].items()}
            cand_diag=[];eligible=[]
            feasible_cands={}
            for cand in CANDS:
                complete=all(c is not None for c in cand_c_by_i[cand]) and np.isfinite(cand_oof[cand]).all()
                if not complete:
                    row={'candidate':cand,'complete':False,'AP_feasible':False,'AP_inner':None,'q025_delta_MCC':None,'selected_C_by_inner_fold':cand_c_by_i[cand]}
                    cand_diag.append(row);candidate_rows.append({'dataset':ds,'outer_fold':oi,**row});continue
                ap=float(average_precision_score(y[T],cand_oof[cand]));ok=all(ap>v for v in refap.values())
                boot=bootstrap_delta_mcc(y[T],g[T],tauTrows,preT,{cand:cand_oof[cand]},2000,BASE+300000+1000*oi)[cand]
                row={'candidate':cand,'complete':True,'AP_inner':ap,'AP_feasible_vs_all_15':bool(ok),'q025_delta_MCC':boot['q025'],'bootstrap_attempted':2000,'bootstrap_valid':boot['valid'],'selection_bootstrap_seed':BASE+300000+1000*oi,'selected_C_by_inner_fold':cand_c_by_i[cand]}
                cand_diag.append(row);candidate_rows.append({'dataset':ds,'outer_fold':oi,**row})
                if ok:eligible.append((boot['q025'],-(WIDTHS[cand]-34),-CANDS.index(cand),cand))
            selected_cand=max(eligible)[-1] if eligible else None
            fold={'outer_fold':oi,'outer_train_n':len(T),'heldout_n':len(H),'outer_seed':BASE+8100,'inner_seed':inner_seed,
                'P_pre_C':frozenT['C'],'P_pre_tau':frozenT['tau'],'P_pre_max_abs_Ext03_probability_diff':maxpred,'P_pre_max_abs_Ext04_probability_diff':maxpred4,
                'P_pre_C_match_Ext03':True,'P_pre_cutoff_match_Ext03':True,'P_pre_C_match_Ext04':True,'P_pre_cutoff_match_Ext04':True,'candidate_diagnostics':cand_diag,'selected_candidate':selected_cand,
                'inner_splits':inner_diagnostics}
            if selected_cand is None:
                fold['status']='no_complete_AP_feasible_candidate';fold_rows.append(fold);continue
            # P_post C selection on all outer-training rows using its specified child seeds.
            subchild=lambda k,oi=oi:BASE+200000+1000*oi+10*k
            postc=select_post_c(d,T,selected_cand,inner_seed,subchild)
            if postc['C'] is None:
                fold['status']='selected_candidate_outer_SelectPostC_none';fold['selected_candidate']=None;fold_rows.append(fold);continue
            prepared=prepare_masked_objective(d,selected_cand,T,H)
            post[H]=fit_prepared_masked(prepared,postc['C'])
            # Descriptive common-C diagnostic: same candidate at C_pre(T), no later selection.
            common[H]=fit_prepared_masked(prepared,frozenT['C'])
            fold.update({'status':'complete','P_post_C':postc['C'],'P_post_SelectPostC':postc['C_diagnostics'],
                'P_post_mask_objective':prepared['audit'],'common_C':frozenT['C'],'common_C_mask_objective':prepared['audit']})
            fold_rows.append(fold)
        complete=np.isfinite(post).all() and np.isfinite(common).all() and np.isfinite(pre).all() and np.isfinite(tau).all()
        all_arm_probs[ds]=d['arms']
        models={'P_pre':pre,**{f'arm_{a}':p for a,p in d['arms'].items()}}
        if complete:models.update({'P_post':post,'common_C':common})
        met={};repairs_harms={}
        for name,pv in models.items():
            met[name]=metrics(y,pv,tau)
            if name in ('P_pre','P_post','common_C'):
                for oi,(_,H) in enumerate(outer):
                    predframes.append(d['meta'].iloc[H][['id','group_id','target_label']].assign(dataset=ds,model=name,prediction=pv[H],threshold=tau[H],outer_fold=oi))
            else:
                armname=name[4:]
                for oi,(_,H) in enumerate(outer):predframes.append(d['meta'].iloc[H][['id','group_id','target_label']].assign(dataset=ds,model=name,prediction=pv[H],threshold=tau[H],outer_fold=oi))
        if complete:
            pp=post>=tau;pr=pre>=tau;truth=y.astype(bool)
            repairs_harms={'repairs':int(np.sum((pr!=truth)&(pp==truth))),'harms':int(np.sum((pr==truth)&(pp!=truth))),
                'P_pre_errors':int(np.sum(pr!=truth)),'P_post_errors':int(np.sum(pp!=truth))}
        result[ds]={'n':n,'groups':int(pd.Series(g).nunique()),'positive':int(y.sum()),'nested_complete':bool(complete),
            'metrics':met,'repairs_harms':repairs_harms,'outer_folds':fold_rows,'arm_count_unique':len(d['arms']),
            'B2-rep':'exact duplicate verified against B2 and excluded from comparator family'}
        pre_audit[ds]={'outer':[{k:r[k] for k in ('outer_fold','P_pre_C','P_pre_tau','P_pre_max_abs_Ext03_probability_diff','P_pre_max_abs_Ext04_probability_diff','P_pre_C_match_Ext03','P_pre_cutoff_match_Ext03','P_pre_C_match_Ext04','P_pre_cutoff_match_Ext04')} for r in fold_rows],
            'max_abs_Ext03_p_pre_probability_diff':max(r['P_pre_max_abs_Ext03_probability_diff'] for r in fold_rows),
            'max_abs_Ext04_p_pre_probability_diff':max(r['P_pre_max_abs_Ext04_probability_diff'] for r in fold_rows)}
        source_audit[ds]={'provenance':d['provenance'],'validation_ids_sha256':hashlib.sha256('\n'.join(ids).encode()).hexdigest(),
            'group_count':int(pd.Series(g).nunique()),'feature_names':d['names'],'p_post_training':'D1/D2 exact two-state weighted copies after StandardScaler fit on unique unmasked training rows; prediction unmasked',
            'donor_audit':donor_audit[ds],'validation_predicate':'split == validation via PyArrow; returned split asserted validation only'}
    # Final matched group bootstrap. One draw stream is shared by P_pre, P_post,
    # common-C and every raw arm. If nested P_post is incomplete, all 30 primary
    # AP contrasts are present and unavailable; no partial Holm adjustment.
    pvals=[];bootstrap_results={}
    for di,ds in enumerate(('devign','reveal')):
        d=data_by_ds[ds];y=d['y'];g=d['g'];tau=result[ds]['outer_folds']
        if not result[ds]['nested_complete']:
            result[ds]['MCC_gate']='fail_incomplete_nested_P_post';result[ds]['overall_gate']='fail'
            result[ds]['bootstrap_comparisons']={a:{'status':'unavailable: incomplete nested P_post','AP_CI95':None,'AP_p_holm':None,'AP_gate_pass':False,'MCC_CI95':None} for a in ['P_pre',*ARMS]}
            continue
        pre=np.concatenate([f[f.dataset==ds].set_index('id').reindex(d['ids']).prediction.to_numpy(float) for f in [pd.concat(predframes,ignore_index=True) if predframes else pd.DataFrame()]]) if False else None
        # Prediction arrays are already held in the dataset result's fold outputs; reconstruct from the emitted frame.
        dframe=pd.concat(predframes,ignore_index=True);dsub=dframe[dframe.dataset==ds]
        def get(model):
            q=dsub[dsub.model==model].set_index('id').reindex(d['ids'])
            if q.prediction.isna().any():raise ValueError(f'{ds} missing prediction rows for {model}')
            return q.prediction.to_numpy(float)
        pre=get('P_pre');post=get('P_post');common=get('common_C');thr=dsub[dsub.model=='P_pre'].set_index('id').reindex(d['ids']).threshold.to_numpy(float)
        th3=ext3pred[(ext3pred.dataset==ds)&(ext3pred.model=='P_pre')].set_index('id').reindex(d['ids']).threshold.to_numpy(float)
        th4=ext4pred[(ext4pred.dataset==ds)&(ext4pred.model=='P_pre')].set_index('id').reindex(d['ids']).threshold.to_numpy(float)
        if not np.allclose(thr,th3,rtol=0,atol=1e-12) or not np.allclose(thr,th4,rtol=0,atol=1e-12):raise ValueError('Ext03/Ext04 shared threshold changed')
        ext4post_df=ext4pred[(ext4pred.dataset==ds)&(ext4pred.model=='P_post')].set_index('id').reindex(d['ids'])
        if ext4post_df.prediction.isna().any() or not np.array_equal(ext4post_df.target_label.to_numpy(int),y):raise ValueError(f'{ds}: Ext04 P_post diagnostic ID/label mismatch')
        ext4post=ext4post_df.prediction.to_numpy(float)
        W=group_draws(g,5000,BASE+9000+di);arms=d['arms'];draw={a:{'ap':[],'mcc':[]} for a in ['P_pre',*ARMS]};common_draw={a:{'ap':[],'mcc':[]} for a in ['P_pre',*ARMS]};ext4_delta=[];valid=0
        for w in W:
            ix=idx_from_weights(w)
            if not len(ix) or np.unique(y[ix]).size<2:continue
            valid+=1;postm=matthews_corrcoef(y[ix],post[ix]>=thr[ix]);commonm=matthews_corrcoef(y[ix],common[ix]>=thr[ix]);prem=matthews_corrcoef(y[ix],pre[ix]>=thr[ix])
            ext4_delta.append(average_precision_score(y[ix],post[ix])-average_precision_score(y[ix],ext4post[ix]))
            refs={'P_pre':pre,**arms}
            for a,ref in refs.items():
                draw[a]['ap'].append(average_precision_score(y[ix],post[ix])-average_precision_score(y[ix],ref[ix]))
                draw[a]['mcc'].append(postm-matthews_corrcoef(y[ix],ref[ix]>=thr[ix]))
                common_draw[a]['ap'].append(average_precision_score(y[ix],common[ix])-average_precision_score(y[ix],ref[ix]))
                common_draw[a]['mcc'].append(commonm-matthews_corrcoef(y[ix],ref[ix]>=thr[ix]))
        comps={}
        for a in ['P_pre',*ARMS]:
            ref=pre if a=='P_pre' else arms[a];ap=np.asarray(draw[a]['ap']);mc=np.asarray(draw[a]['mcc']);pv=min(1.,2*min(float(np.mean(ap<=0)),float(np.mean(ap>=0))))
            comps[a]={'delta_AP':float(average_precision_score(y,post)-average_precision_score(y,ref)),'AP_CI95':np.percentile(ap,[2.5,97.5]).tolist(),'AP_p_raw':pv,
                'delta_MCC':float(matthews_corrcoef(y,post>=thr)-matthews_corrcoef(y,ref>=thr)),'MCC_CI95':np.percentile(mc,[2.5,97.5]).tolist(),'attempted_draws':5000,'valid_draws':valid}
        common_comp={}
        for a in ['P_pre',*ARMS]:
            ref=pre if a=='P_pre' else arms[a];ap=np.asarray(common_draw[a]['ap']);mc=np.asarray(common_draw[a]['mcc'])
            common_comp[a]={'delta_AP':float(average_precision_score(y,common)-average_precision_score(y,ref)),'AP_CI95':np.percentile(ap,[2.5,97.5]).tolist(),
                'delta_MCC':float(matthews_corrcoef(y,common>=thr)-matthews_corrcoef(y,ref>=thr)),'MCC_CI95':np.percentile(mc,[2.5,97.5]).tolist(),'attempted_draws':5000,'valid_draws':valid}
        result[ds]['bootstrap_comparisons']=comps;result[ds]['common_C_bootstrap_diagnostics']=common_comp
        result[ds]['Ext04_P_post_AP_diagnostic']={'delta_AP':float(average_precision_score(y,post)-average_precision_score(y,ext4post)),
            'CI95':np.percentile(ext4_delta,[2.5,97.5]).tolist(),'attempted_draws':5000,'valid_draws':valid}
        mcci=comps['P_pre']['MCC_CI95'];result[ds]['MCC_gate']='pass' if mcci[0]>.02 else ('fail' if mcci[1]<=.02 else 'inconclusive')
        for a in ARMS:pvals.append((comps[a]['AP_p_raw'],ds,a))
    if len(pvals)==30:
        ordered=sorted(pvals);runp=0.
        for i,(pval,ds,a) in enumerate(ordered):
            adj=max(runp,min(1.,(30-i)*pval));runp=adj;c=result[ds]['bootstrap_comparisons'][a]
            c['AP_p_holm']=adj if adj>=1/5000 else '<1/5000';c['AP_gate_pass']=c['AP_CI95'][0]>0 and adj<.05;c.pop('AP_p_raw',None)
    else:
        result['AP_family_status']='incomplete: all 30 planned comparisons unavailable/not-adjusted; partial Holm prohibited'
        for ds in ('devign','reveal'):
            if 'bootstrap_comparisons' in result[ds]:
                for a in ARMS:result[ds]['bootstrap_comparisons'][a]['AP_p_holm']=None;result[ds]['bootstrap_comparisons'][a]['AP_gate_pass']=False;result[ds]['bootstrap_comparisons'][a].pop('AP_p_raw',None)
    for ds in ('devign','reveal'):
        if 'bootstrap_comparisons' not in result[ds]:continue
        result[ds]['all_arm_AP_gate']=all(result[ds]['bootstrap_comparisons'][a]['AP_gate_pass'] for a in ARMS)
        result[ds]['overall_gate']='pass' if result[ds]['nested_complete'] and result[ds]['MCC_gate']=='pass' and result[ds]['all_arm_AP_gate'] else ('fail' if not result[ds]['nested_complete'] or result[ds]['MCC_gate']=='fail' else 'inconclusive')
    overall='pass' if all(result[d].get('overall_gate')=='pass' for d in ('devign','reveal')) else ('fail_incomplete_nested_P_post' if not all(result[d]['nested_complete'] for d in ('devign','reveal')) else 'fail_or_inconclusive')
    results={'protocol_sha256':sha(PROTOCOL),'runner_sha256':sha(Path(__file__)),'source_registry_sha256':sha(PRE/'source_registry.json'),
        'base_seed':BASE,'candidate_order':list(CANDS),'candidate_widths':WIDTHS,'datasets':result,'overall_gate':overall,
        'Ext03_Ext04_P_pre_audit':pre_audit}
    # write complete outputs only after the full validation statistics are computed.
    FULL.mkdir(parents=True,exist_ok=True)
    pd.concat(predframes,ignore_index=True).to_csv(FULL/'outer_predictions.csv',index=False)
    atomic_json(FULL/'results.json',results);atomic_json(FULL/'source_audit.json',source_audit)
    atomic_json(FULL/'candidate_diagnostics.json',{'rows':candidate_rows,'outer_selections':{d:result[d]['outer_folds'] for d in ('devign','reveal')}})
    atomic_json(FULL/'pre_p_pre_audit.json',pre_audit)
    atomic_json(FULL/'feature_manifest.json',{'base_feature_order':data_by_ds['devign']['names'],'candidate_features':{
        'D1':data_by_ds['devign']['names']+['b','u','A','R','G','H','D'],
        'D2':data_by_ds['devign']['names']+['b','u','A','R','G','H','D']},'widths':WIDTHS,
        'mask_objectives':{'D1':'copy0=[x,b,0*v], copy1=[x,b,2*v]','D2':'copy0=[x,0*z], copy1=[x,2*z]'},
        'sample_weight_each_copy':.5,'scaler':'fit once on unique unmasked training rows, never on copies','inference':'one original row, unmasked'})
    source_hashes={}
    reg=json.loads((PRE/'source_registry.json').read_text(encoding='utf-8'))
    for path,info in reg['sources'].items():source_hashes[path]=info['sha256']
    source_hashes[str(Path(__file__))]=sha(Path(__file__));source_hashes[str(PROTOCOL)]=sha(PROTOCOL)
    atomic_json(FULL/'provenance_hashes.json',source_hashes)
    manifest={**frozen,'run_status':'complete','fit_started':True,'run_command':"& 'C:\\Users\\yungn\\AppData\\Local\\Programs\\Python\\Python311\\python.exe' ext05_runner.py",
        'outer_folds':3,'inner_folds':3,'deep_folds':3,'selection_bootstrap_draws':2000,'final_bootstrap_draws':5000,'holm_family':30,
        'shared_P_pre_frozen_from_Ext03_Ext04':True,'P_pre_assert_tolerance':1e-12,'mask_rule':'D1/D2 deterministic two-copy expected loss; sample_weight 0.5 per copy; total weight equals unique N; scaler fit once on unique unmasked rows; inference unmasked','test_metadata_incident':'Earlier provenance work displayed test IDs/change metadata only; no test labels/scores/predictions were read.',
        'runtime_caveats':['B1-full legacy renderer','B1-shuf checkpoint/runtime per imported source manifest','Devign B2-rand-44 partial legacy runtime','B3 separate verified-patch fixed-pair source']}
    atomic_json(FULL/'manifest.json',manifest)
    report=['# Ext05 validation-only report','',f"Protocol SHA-256 `{sha(PROTOCOL)}`; runner SHA-256 `{sha(Path(__file__))}`.",'',
        'Finite post-registration/post-cap exploratory extension; not confirmatory. Ext03/Ext04 P_pre predictions are used only for audit equality and comparison, never as P_post features. Test labels, scores, and predictions were not read. Prior metadata-only exposure is disclosed in manifest.json.','',f'Overall gate: **{overall}**.','']
    for ds in ('devign','reveal'):
        q=result[ds];report += [f"## {ds}",'',f"N={q['n']}; groups={q['groups']}; complete={q['nested_complete']}; selected={[r.get('selected_candidate') for r in q['outer_folds']]}; MCC gate={q.get('MCC_gate')}.",'']
        if q['nested_complete']:
            mc=q['bootstrap_comparisons']['P_pre'];report.append(f"P_post vs fixed P_pre: ΔMCC={mc['delta_MCC']:.6f}, CI95={mc['MCC_CI95']}; gate requires lower > +0.02. AP Δ={mc['delta_AP']:.6f} (diagnostic).")
            report.append(f"P_pre AP={q['metrics']['P_pre']['AP']:.6f}; P_post AP={q['metrics']['P_post']['AP']:.6f}; common-C AP={q['metrics']['common_C']['AP']:.6f}.")
            failed=[a for a in ARMS if not q['bootstrap_comparisons'][a]['AP_gate_pass']]
            report.append(f"Failed AP arm contrasts: {failed or 'none'}; 15/15 AP arm gates passed={not failed}.")
            report.append(f"Ext04 P_post AP diagnostic: ΔAP={q['Ext04_P_post_AP_diagnostic']['delta_AP']:.6f}, CI95={q['Ext04_P_post_AP_diagnostic']['CI95']}.")
        else:report.append('Nested validation incomplete: no fallback was used; all 30 planned AP contrasts are unavailable and unadjusted.')
        report.append('')
    report += ['See `results.json`, `outer_predictions.csv`, `candidate_diagnostics.json`, `pre_p_pre_audit.json`, `source_audit.json`, and `provenance_hashes.json`.','']
    (FULL/'report.md').write_text('\n'.join(report),encoding='utf-8')
    # Final artifact hashes include source and code provenance, written last.
    outputs=[FULL/f for f in ('results.json','outer_predictions.csv','report.md','manifest.json','source_audit.json','candidate_diagnostics.json','pre_p_pre_audit.json','feature_manifest.json','provenance_hashes.json')]
    ah={str(p):sha(p) for p in outputs};ah[str(Path(__file__))]=sha(Path(__file__));ah[str(PROTOCOL)]=sha(PROTOCOL);ah[str(PRE/'source_registry.json')]=sha(PRE/'source_registry.json')
    atomic_json(FULL/'artifact_hashes.json',ah);atomic_json(OUT/'run_state.json',{'state':'complete','overall_gate':overall,'artifact_hashes_sha256':sha(FULL/'artifact_hashes.json')})
    return results

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--smoke',action='store_true');args=ap.parse_args();print(json.dumps(run(args.smoke),indent=2))
