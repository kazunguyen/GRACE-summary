"""Frozen Ext03 validation-only multi-arm feature fusion runner.

Reads only validation rows from parquet via PyArrow predicates and validation
record files. The three candidate bundles and all split/selection rules are
locked in ext03_protocol_vi.md.
"""
from __future__ import annotations

import hashlib, json, shutil, sys, platform
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from scipy.special import expit
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (average_precision_score, roc_auc_score,
    matthews_corrcoef, balanced_accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix)
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

HOME=Path(__file__).resolve().parent
ROOT=HOME.parent
SOURCE=HOME/'runs/grace-research-offline-v2'
H3=ROOT/'STEP6_supervised_anchors/runs/h3b_locked/step6_lock_64fb2c99d904'
OUT=HOME/'runs/independent-post-ext03-multisignal-validation'
PROTOCOL=HOME/'ext03_protocol_vi.md'
BASE=20261123
CS=(0.001,0.01,0.05,0.1,1.0)
CORE=('B0','B1','B1-H2','B2','B2-flip','B2-nolabel','B2-rep')
EXTRA={'B1-full':[42],'B1-shuf':[42,43,44],'B2-labelonly':[42],'B2-rand':[42,43,44]}
B3_ROOT=ROOT/'Runs-management/b3_lznt_resume_retry_20261109/b3-new-dual-resume-v2-retry1/remote_output/b3_new_dual_validation_resume_v2_20261109'
MODEL_SHA='f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335'
ARMS=['B0','B1','B1-full','B1-H2','B1-shuf-42','B1-shuf-43','B1-shuf-44','B2','B2-flip','B2-labelonly','B2-nolabel','B2-rand-42','B2-rand-43','B2-rand-44','B3']
CANDS=('T1','T2','T3')
WIDTHS={'T1':41,'T2':44,'T3':43}

def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def read_validation(path, columns):
    """Predicate read; assert no nonvalidation record escaped the filter."""
    if 'split' not in columns: columns=['split',*columns]
    d=pd.read_parquet(path,columns=list(dict.fromkeys(columns)),filters=[('split','==','validation')],engine='pyarrow')
    if set(d.split.dropna().astype(str).unique())!={'validation'}:
        raise ValueError(f'validation predicate returned nonvalidation data: {path}')
    return d

def read_records(path,ds,arm,seed):
    rows=[]
    with open(path,encoding='utf-8') as f:
        for line in f:
            r=json.loads(line)
            if r.get('split')!='validation' or r.get('dataset')!=ds or r.get('arm')!=arm:
                raise ValueError(f'validation source contract mismatch {path}')
            if int(r.get('seed',seed))!=seed: raise ValueError(f'seed mismatch {path}')
            l0=float(r['logprob_0']);l1=float(r['logprob_1']);ell=l1-l0
            if not np.isfinite([l0,l1,ell]).all(): raise ValueError(f'nonfinite logprob in {path}')
            model=r.get('model_sha256')
            if model!=MODEL_SHA:raise ValueError(f'model hash mismatch in {path}: {model}')
            rows.append({'id':str(r['id']),'label':int(r['label']),'logprob0':l0,'logprob1':l1,'ell':ell,
                'prompt_sha256':r.get('prompt_sha256'),'demo_ids':r.get('demo_ids',[]),'tokens':r.get('tokens',{}),
                'group':r.get('group'),'valid_flag':r.get('valid'),'response_valid':r.get('response_valid'),
                'backend':r.get('backend'),'quantization':r.get('quantization'),'model_repo_revision':r.get('model_repo_revision'),
                'arm':arm,'seed':seed})
    d=pd.DataFrame(rows)
    if d.empty or d.id.duplicated().any():raise ValueError(f'empty or duplicate IDs in {path}')
    return d

def flag_counts(s):
    return {str(k):int(v) for k,v in s.value_counts(dropna=False).items()}

def load_arms(ds,ids,y,groups):
    # The parquet selection predicate is applied before any row values are loaded.
    scores=read_validation(SOURCE/'scores.parquet',['id','dataset','arm','log_odds','score_valid','model','backend'])
    scores=scores[(scores.dataset==ds)&scores.arm.isin(CORE)].copy()
    if scores.empty or scores.model.nunique()!=1 or scores.model.iloc[0]!=MODEL_SHA or set(scores.backend)!={'qwen'}:
        raise ValueError(f'{ds}: core model/backend provenance mismatch')
    if scores.duplicated(['id','arm']).any():raise ValueError(f'{ds}: duplicate core arm rows')
    if scores.score_valid.isna().any() or not scores.score_valid.astype(bool).all():
        raise ValueError(f'{ds}: core score_valid schema/values conflict')
    if not np.isfinite(scores.log_odds.to_numpy(float)).all():raise ValueError(f'{ds}: nonfinite core log odds')
    wide=scores.pivot(index='id',columns='arm',values='log_odds').reindex(ids)
    if set(CORE)-set(wide.columns) or wide[list(CORE)].isna().any().any():raise ValueError(f'{ds}: core arm coverage failure')
    arms={a:wide[a].to_numpy(float) for a in CORE}
    if not np.array_equal(arms['B2'],arms['B2-rep']):raise ValueError(f'{ds}: B2-rep is not an exact duplicate')
    arms.pop('B2-rep')
    provenance=[];records={}
    for a,seeds in EXTRA.items():
        for seed in seeds:
            p=ROOT/f'runs/final/{ds}/validation/{a}/{seed}/records.jsonl'
            q=read_records(p,ds,a,seed).set_index('id')
            if not set(ids).issubset(set(q.index)) or (len(ids)>1000 and set(q.index)!=set(ids)):
                raise ValueError(f'{ds} {a}-{seed}: validation ID set mismatch')
            q=q.reindex(ids)
            if not np.array_equal(q.label.to_numpy(int),y):raise ValueError(f'{ds} {a}-{seed}: target label mismatch')
            group_join='exact validation-ID join to inputs.parquet canonical group'
            if q.group.isna().any():group_join='source group field absent; canonical group assigned via exact validation-ID join to inputs.parquet'
            elif not np.array_equal(q.group.astype(str).to_numpy(),groups):raise ValueError(f'{ds} {a}-{seed}: canonical group mismatch')
            key=f'{a}-{seed}' if a in ('B1-shuf','B2-rand') else a
            arms[key]=q.ell.to_numpy(float);records[key]=q
            provenance.append({'arm':a,'seed':seed,'path':str(p),'sha256':sha(p),'rows':len(q),'canonical_group_provenance':group_join,
                'valid_counts':flag_counts(q.valid_flag),'response_valid_counts':flag_counts(q.response_valid),
                'backend':q.backend.dropna().unique().tolist(),'quantization':q.quantization.dropna().unique().tolist(),'model_repo_revision':q.model_repo_revision.dropna().unique().tolist()})
    p=B3_ROOT/ds/'seed_42'/ds/'validation/records.jsonl';q=read_records(p,ds,'B3',42).set_index('id')
    if not set(ids).issubset(set(q.index)) or (len(ids)>1000 and set(q.index)!=set(ids)):
        raise ValueError(f'{ds} B3: validation ID set mismatch')
    q=q.reindex(ids)
    if not np.array_equal(q.label.to_numpy(int),y):raise ValueError(f'{ds} B3 label mismatch')
    group_join='exact validation-ID join to inputs.parquet canonical group'
    if q.group.isna().any():group_join='source group field absent; canonical group assigned via exact validation-ID join to inputs.parquet'
    elif not np.array_equal(q.group.astype(str).to_numpy(),groups):raise ValueError(f'{ds} B3 group mismatch')
    arms['B3']=q.ell.to_numpy(float);records['B3']=q
    provenance.append({'arm':'B3','seed':42,'path':str(p),'sha256':sha(p),'rows':len(q),'contract':'verified-patch fixed-pair',
        'canonical_group_provenance':group_join,'valid_counts':flag_counts(q.valid_flag),
        'response_valid_counts':flag_counts(q.response_valid),'backend':q.backend.dropna().unique().tolist(),
        'quantization':q.quantization.dropna().unique().tolist(),'model_repo_revision':q.model_repo_revision.dropna().unique().tolist()})
    if len(arms)!=15 or set(arms)!=set(ARMS):raise ValueError('Comparator registry must be exactly 15 unique raw vectors')
    for a,v in arms.items():
        if not np.isfinite(v).all():raise ValueError(f'{ds} nonfinite arm vector {a}')
    # Prompt perturbation donor contract, checked on validation-source records only.
    b2=read_records(ROOT/f'runs/final/{ds}/validation/B2/42/records.jsonl',ds,'B2',42).set_index('id').reindex(ids)
    bf=read_records(ROOT/f'runs/final/{ds}/validation/B2-flip/42/records.jsonl',ds,'B2-flip',42).set_index('id').reindex(ids)
    if not b2.demo_ids.map(lambda x:tuple(x or [])).equals(bf.demo_ids.map(lambda x:tuple(x or []))):
        raise ValueError(f'{ds}: B2/B2-flip donor assignment differs')
    provenance.append({'arm':'B2-vs-B2-flip-audit','same_donor_ids':True,'prompt_hashes_differ':bool((b2.prompt_sha256!=bf.prompt_sha256).all()),'prompt_text_available':False,
        'B2_source_sha256':sha(ROOT/f'runs/final/{ds}/validation/B2/42/records.jsonl'),'B2_flip_source_sha256':sha(ROOT/f'runs/final/{ds}/validation/B2-flip/42/records.jsonl')})
    if not (b2.prompt_sha256.to_numpy()!=bf.prompt_sha256.to_numpy()).all():raise ValueError(f'{ds}: B2-flip prompt hash did not change')
    return arms,provenance

def verify_donors(meta):
    banks={ds:ROOT/f'artifact-packaging/03_data_prompts_records/frozen_inputs/cpg/{ds}/train.jsonl' for ds in ('devign','reveal')}
    ans={};hashes={}
    for ds,p in banks.items():
        wanted={str(r.donor_id):int(r.donor_label) for r in meta[meta.dataset==ds][['donor_id','donor_label']].drop_duplicates().itertuples(index=False)}
        found={};
        with open(p,encoding='utf-8') as f:
            for line in f:
                row=json.loads(line);rid=str(row.get('id'))
                if rid in wanted:found[rid]=int(row['target'])
        if set(found)!=set(wanted):raise ValueError(f'{ds}: donor membership missing/extra in frozen train bank')
        bad=[k for k in wanted if wanted[k]!=found[k]]
        if bad:raise ValueError(f'{ds}: donor label mismatch in train bank')
        if not all(k.startswith(ds+':train:') for k in wanted):raise ValueError(f'{ds}: donor namespace violation')
        ans[ds]={'donors':len(wanted),'all_present_in_train':True,'labels_match_train_target':True,'path':str(p)}
        hashes[ds]=sha(p)
    return ans,hashes

def folds(y,g,seed):
    splits=list(StratifiedGroupKFold(3,shuffle=True,random_state=int(seed)).split(np.zeros(len(y)),y,g))
    for tr,va in splits:
        if np.unique(y[tr]).size<2 or np.unique(y[va]).size<2:raise ValueError('group fold lacks class')
        if set(g[tr])&set(g[va]):raise ValueError('group leakage across fold')
    return splits

def threshold(y,p):
    ts=np.arange(.01,1,.01)
    return max(ts,key=lambda t:(matthews_corrcoef(y,p>=t),-abs(t-.5),-t))

def est(c):
    return make_pipeline(StandardScaler(),LogisticRegression(C=float(c),solver='lbfgs',max_iter=3000,penalty='l2'))

def make_z(cand,idx,tridx,x,logits,p,evidence,names):
    X=x[idx];L={k:v[idx] for k,v in logits.items()};P={k:v[idx] for k,v in p.items()}
    b=L['B2'];u=(2*donor_labels[idx]-1)*np.tanh((b-L['B2-flip'])/2)
    A=P['B2']-P['B2-labelonly'];R=P['B2']-np.mean(np.column_stack([P[f'B2-rand-{s}'] for s in (42,43,44)]),axis=1)
    G=P['B1']-np.mean(np.column_stack([P[f'B1-shuf-{s}'] for s in (42,43,44)]),axis=1)
    H=P['B1-H2']-P['B1'];D=P['B2']-P['B2-nolabel'];q=(evidence[idx]=='available').astype(float)
    if cand=='T1':add=[b,u,A,R,G,H,D]
    elif cand=='T2':
        def ch(v):
            c=np.clip(v,-12,12);h=np.logaddexp(0,c)-.5*c-np.log(2.)
            return c,h
        cb2,_=ch(L['B2']);_,hb2=ch(L['B2']);cl,hl=ch(L['B2-labelonly']);c1,h1=ch(L['B1-H2'])
        add=[b,u,hb2,cl,hl,c1,h1,R,G,D]
    elif cand=='T3':
        li=names.index('log_tokens');mu=float(x[tridx,li].mean());sd=float(x[tridx,li].std(ddof=0));sd=sd if sd>=1e-12 else 1.
        t=np.clip((X[:,li]-mu)/sd,-3,3);add=[b,u,A,R,G,H,D,q*G,t*R]
    else:raise ValueError(cand)
    z=np.column_stack([X,*add]).astype(float)
    if z.shape[1]!=WIDTHS[cand] or not np.isfinite(z).all():raise ValueError(f'{cand} derived matrix invalid')
    return z

def select_c_oof(kind,idx,yall,gall,x,logits,p,evidence,names,seed):
    yy=yall[idx];gg=gall[idx];preds={float(c):np.full(len(idx),np.nan) for c in CS}
    for si,(tr,va) in enumerate(folds(yy,gg,seed)):
        tri=idx[tr];vai=idx[va]
        for c in CS:
            if kind=='P_pre':ztr=x[tri];zva=x[vai]
            else:ztr=make_z(kind,tri,tri,x,logits,p,evidence,names);zva=make_z(kind,vai,tri,x,logits,p,evidence,names)
            preds[float(c)][va]=est(c).fit(ztr,yy[tr]).predict_proba(zva)[:,1]
    scores={c:average_precision_score(yy,v) for c,v in preds.items()}
    chosen=max(CS,key=lambda c:(scores[float(c)],-float(c)))
    return float(chosen),preds[float(chosen)],{str(c):float(scores[float(c)]) for c in CS}

def predict(kind,c,tr,va,yall,x,logits,p,evidence,names):
    y=yall[tr]
    if kind=='P_pre':ztr=x[tr];zva=x[va]
    else:ztr=make_z(kind,tr,tr,x,logits,p,evidence,names);zva=make_z(kind,va,tr,x,logits,p,evidence,names)
    return est(c).fit(ztr,y).predict_proba(zva)[:,1]

def group_draws(g,n,seed):
    u,inv=np.unique(g,return_inverse=True);rng=np.random.default_rng(seed);out=[]
    for _ in range(n):out.append(np.bincount(rng.integers(0,len(u),len(u)),minlength=len(u))[inv])
    return np.asarray(out,dtype=np.int32)

def resample_ix(w):return np.repeat(np.arange(len(w)),w)

def boot_mcc_diffs(y,g,tau,pre,cands,draws,seed):
    W=group_draws(g,draws,seed);res={c:[] for c in cands};valid=0
    for w in W:
        ix=resample_ix(w)
        if not len(ix) or np.unique(y[ix]).size<2:continue
        valid+=1;bm=matthews_corrcoef(y[ix],pre[ix]>=tau[ix])
        for c,pred in cands.items():res[c].append(matthews_corrcoef(y[ix],pred[ix]>=tau[ix])-bm)
    return {c:{'valid_draws':valid,'attempted_draws':draws,'q025':float(np.quantile(v,.025)),'samples':v} for c,v in res.items()}

def run(smoke=False):
    # Freeze artifacts and source hashes before model fitting or outer outcomes.
    OUT.mkdir(parents=True,exist_ok=True);(OUT/'preflight').mkdir(exist_ok=True)
    shutil.copy2(PROTOCOL,OUT/'ext03_protocol_vi.md')
    frozen={'registered':False,'post_cap_extension':True,'validation_only':True,
        'test_labels_scores_predictions_read':False,'historical_search_count':'at least 23 before Ext03; at least 26 after these three hypotheses',
        'hypotheses':['T1','T2','T3'],'protocol':str(PROTOCOL),'protocol_sha256':sha(PROTOCOL),
        'candidate_formulas':'exactly as written in ext03_protocol_vi.md; no additional candidates',
        'fit_started':False,'test_metadata_incident':'Earlier provenance inspection displayed test IDs/change metadata from a mixed-split prompt audit; no test labels, scores, or predictions were read.'}
    (OUT/'preflight'/'frozen_manifest.json').write_text(json.dumps(frozen,indent=2),encoding='utf-8')
    smoke_path=OUT/'preflight'/'smoke.json'
    if not smoke and not smoke_path.is_file():raise RuntimeError('Run --smoke preflight before full nested validation')
    premeta=['id','dataset','split','target_label','group_id','donor_id','donor_label','donor_snapshot','evidence_status']
    meta=read_validation(SOURCE/'inputs.parquet',premeta)
    if meta.duplicated(['dataset','id']).any():raise ValueError('duplicate validation IDs')
    donors,donor_hashes=verify_donors(meta)
    source_audit={};feature_manifest={};fold_audit={};predframes=[];dataset_results={};all_arms={}
    for ds in ('devign','reveal'):
        m=meta[meta.dataset==ds].sort_values('id').reset_index(drop=True)
        if smoke:
            m=m.groupby('target_label',group_keys=False).head(120).sort_values('id').reset_index(drop=True)
        ids=m.id.astype(str).tolist();y=m.target_label.to_numpy(int);g=m.group_id.astype(str).to_numpy()
        if not np.isin(y,[0,1]).all() or np.unique(y).size!=2 or m.group_id.isna().any():raise ValueError('validation labels/groups invalid')
        if not np.isfinite(m.donor_label.to_numpy(float)).all() or not set(m.donor_label.unique()).issubset({0,1}):raise ValueError('donor labels invalid')
        if not m.donor_id.astype(str).str.startswith(ds+':train:').all() or (m.id==m.donor_id).any():raise ValueError('validation donor not in frozen train namespace or self donor')
        if m.donor_snapshot.nunique()!=1:raise ValueError('mixed donor snapshot')
        zp=np.load(H3/ds/'xpre_validation.npz',allow_pickle=False)
        hi=pd.Index(zp['ids'].astype(str));names=zp['feature_names'].astype(str).tolist();pos=hi.get_indexer(ids);x=zp['X'][pos].astype(float);zp.close()
        if (pos<0).any() or len(names)!=34 or names[-1]!='assert' or 'log_tokens' not in names or not np.isfinite(x).all():raise ValueError('H3-B alignment/name/finite check failed')
        global donor_labels
        donor_labels=m.donor_label.to_numpy(float)
        lg,prov=load_arms(ds,ids,y,g);p={a:expit(v) for a,v in lg.items()}
        if not all(np.isfinite(v).all() for v in p.values()):raise ValueError('nonfinite arm probability')
        all_arms[ds]=p
        q=read_validation(SOURCE/'inputs.parquet',['id','dataset','evidence_status'])
        evidence=q[(q.dataset==ds)].set_index('id').reindex(ids).evidence_status.to_numpy()
        if pd.isna(evidence).any():raise ValueError('evidence status missing')
        # Recompute probabilities from log odds and verify these sigmoid fields are finite.
        zbase=np.column_stack([x,np.zeros((len(x),1))]);idx=np.arange(len(y))
        # Feature matrix smoke assertions, all definitions/widths before CV.
        for cand in CANDS:
            zz=make_z(cand,idx,idx,x,lg,p,evidence,names)
            feature_manifest[cand]={'base_feature_names':names,'added_feature_count':WIDTHS[cand]-34,'total_width':WIDTHS[cand]}
        source_audit[ds]={'n':len(y),'positive':int(y.sum()),'groups':int(pd.Series(g).nunique()),'ids_sha256':hashlib.sha256('\n'.join(ids).encode()).hexdigest(),'provenance':prov,'donor_bank':donors[ds],'donor_snapshot':str(m.donor_snapshot.iloc[0]),'validation_predicate':'PyArrow filter split == validation; returned values asserted validation only','H3_file':str(H3/ds/'xpre_validation.npz'),'H3_sha256':sha(H3/ds/'xpre_validation.npz')}
        if smoke:
            dataset_results[ds]={'smoke':'passed','n':len(y),'arm_vectors':len(lg),'bundles':{k:WIDTHS[k] for k in CANDS}}
            continue
        outer=folds(y,g,BASE+8100);pre=np.full(len(y),np.nan);post=np.full(len(y),np.nan);tau=np.full(len(y),np.nan);chosen_rows=[]
        for oi,(ot,oh) in enumerate(outer):
            yy=y[ot];gg=g[ot];inner_seed=BASE+100000+1000*oi;inner=folds(yy,gg,inner_seed)
            inner_pre=np.full(len(ot),np.nan);inner_tau=np.full(len(ot),np.nan);inner_cand={c:np.full(len(ot),np.nan) for c in CANDS};cvals={c:[] for c in CANDS};fold_details=[]
            for ii,(itr,iva) in enumerate(inner):
                S=ot[itr];V=ot[iva];S_y=y[S]
                sseed=BASE+200000+1000*oi+10*ii
                cpre,pre_oof,pre_scores=select_c_oof('P_pre',S,y,g,x,lg,p,evidence,names,sseed)
                tauS=threshold(S_y,pre_oof)
                inner_pre[iva]=predict('P_pre',cpre,S,V,y,x,lg,p,evidence,names)
                inner_tau[iva]=tauS
                cdiag={'inner_fold':ii,'subinner_seed':sseed,'P_pre_C':cpre,'P_pre_subinner_AP_by_C':pre_scores,'tau_S':float(tauS)}
                for cand in CANDS:
                    cc,coof,cscores=select_c_oof(cand,S,y,g,x,lg,p,evidence,names,sseed)
                    inner_cand[cand][iva]=predict(cand,cc,S,V,y,x,lg,p,evidence,names);cvals[cand].append(cc)
                    cdiag[cand]={'C':cc,'subinner_AP_by_C':cscores}
                fold_details.append(cdiag)
            if not np.isfinite(inner_pre).all() or not np.isfinite(inner_tau).all() or any(not np.isfinite(v).all() for v in inner_cand.values()):raise ValueError('inner held-out predictions incomplete')
            refs={a:average_precision_score(yy,v[ot]) for a,v in p.items()}
            feasible=[];diag=[]
            for cand in CANDS:
                ap=average_precision_score(yy,inner_cand[cand]);ok=all(ap>v for v in refs.values())
                seed=BASE+300000+1000*oi; boot=boot_mcc_diffs(yy,gg,inner_tau,inner_pre,{cand:inner_cand[cand]},2000,seed)[cand]
                row={'candidate':cand,'AP_inner':float(ap),'AP_beats_all_15':bool(ok),'q025_inner_delta_MCC':boot['q025'],'bootstrap_attempted':2000,'bootstrap_valid':boot['valid_draws'],'C_by_inner_fold':cvals[cand],'added_columns':WIDTHS[cand]-34}
                diag.append(row)
                if ok:feasible.append((boot['q025'],-(WIDTHS[cand]-34),-CANDS.index(cand),cand))
            selected=max(feasible)[-1] if feasible else None
            record={'outer_fold':oi,'train_n':len(ot),'heldout_n':len(oh),'outer_seed':BASE+8100,'inner_seed':inner_seed,'inner_folds':fold_details,'candidate_selection':diag,'selected':selected}
            if selected is None:
                chosen_rows.append(record);continue
            # Refit training-partition C and threshold using fixed-C grouped OOF.
            cpre,preT,pre_scores=select_c_oof('P_pre',ot,y,g,x,lg,p,evidence,names,inner_seed)
            tauT=threshold(yy,preT)
            cpost,postT,post_scores=select_c_oof(selected,ot,y,g,x,lg,p,evidence,names,inner_seed)
            pre[oh]=predict('P_pre',cpre,ot,oh,y,x,lg,p,evidence,names)
            post[oh]=predict(selected,cpost,ot,oh,y,x,lg,p,evidence,names);tau[oh]=tauT
            record.update({'P_pre_C_outer_train':cpre,'P_post_C_outer_train':cpost,'P_pre_OOF_AP_by_C':pre_scores,'P_post_OOF_AP_by_C':post_scores,'tau_T':float(tauT)})
            chosen_rows.append(record)
        complete=np.isfinite(pre).all() and np.isfinite(post).all() and np.isfinite(tau).all()
        models={'P_pre':pre,**{f'arm_{a}':v for a,v in p.items()}}
        if complete:models['nested_selected']=post
        mets={}
        for name,v in models.items():
            pred=v>=tau;tn,fp,fn,tp=confusion_matrix(y,pred,labels=[0,1]).ravel()
            mets[name]={'AP':float(average_precision_score(y,v)),'AUROC':float(roc_auc_score(y,v)),'MCC':float(matthews_corrcoef(y,pred)),'balanced_accuracy':float(balanced_accuracy_score(y,pred)),'precision':float(precision_score(y,pred,zero_division=0)),'recall':float(recall_score(y,pred,zero_division=0)),'F1':float(f1_score(y,pred,zero_division=0)),'confusion':{'tn':int(tn),'fp':int(fp),'fn':int(fn),'tp':int(tp)},'outer_fold_AP':[float(average_precision_score(y[oh],v[oh])) for _,oh in outer]}
            for oi,(_,oh) in enumerate(outer):predframes.append(m.iloc[oh][['id','group_id','target_label']].assign(dataset=ds,model=name,prediction=v[oh],threshold=tau[oh],outer_fold=oi))
        dataset_results[ds]={'n':len(y),'groups':int(pd.Series(g).nunique()),'positive':int(y.sum()),'metrics':mets,'nested_complete':bool(complete),'outer_folds':chosen_rows,'arm_count':len(lg),'B2-rep':'exact duplicate of B2; excluded from 15 unique comparator family'}
        fold_audit[ds]={'outer_train_test_group_overlap':False,'outer_fold_sizes':[{'train':len(a),'heldout':len(b)} for a,b in outer],'selected':[r['selected'] for r in chosen_rows]}
    if smoke:
        registry={'inputs_parquet':{'path':str(SOURCE/'inputs.parquet'),'sha256':sha(SOURCE/'inputs.parquet'),'read_filter':'split == validation'},
            'scores_parquet':{'path':str(SOURCE/'scores.parquet'),'sha256':sha(SOURCE/'scores.parquet'),'read_filter':'split == validation'},
            'datasets':{}}
        for d in ('devign','reveal'):
            registry['datasets'][d]={'H3':{'path':str(H3/d/'xpre_validation.npz'),'sha256':source_audit[d]['H3_sha256']},
                'arms':source_audit[d]['provenance'],'frozen_train_bank':source_audit[d]['donor_bank']}
        regpath=OUT/'preflight'/'source_registry.json';regpath.write_text(json.dumps(registry,indent=2),encoding='utf-8')
        sm={'status':'passed','datasets':dataset_results,'validation_source_audit':source_audit,'donor_audit':donors,'registry_sha256':sha(regpath),'runner_sha256':sha(Path(__file__))}
        smoke_path.write_text(json.dumps(sm,indent=2),encoding='utf-8')
        frozen.update({'preflight_passed':True,'source_registry_sha256':sm['registry_sha256'],'runner_sha256':sm['runner_sha256']})
        (OUT/'preflight'/'frozen_manifest.json').write_text(json.dumps(frozen,indent=2),encoding='utf-8')
        return {'smoke':'passed','datasets':list(dataset_results)}
    sm=json.loads(smoke_path.read_text(encoding='utf-8'))
    if sm.get('status')!='passed' or sm.get('runner_sha256')!=sha(Path(__file__)) or sm.get('registry_sha256')!=sha(OUT/'preflight'/'source_registry.json'):
        raise RuntimeError('Frozen smoke preflight does not match current runner/source registry; repeat smoke before fitting')
    # Final common paired group bootstrap, exactly 5,000 attempts per dataset.
    pvalues=[]
    for di,ds in enumerate(('devign','reveal')):
        m=meta[meta.dataset==ds].sort_values('id').reset_index(drop=True);y=m.target_label.to_numpy(int);g=m.group_id.astype(str).to_numpy()
        if not dataset_results[ds]['nested_complete']:
            dataset_results[ds]['MCC_gate']='fail_incomplete_nested_P_post';dataset_results[ds]['overall_gate']='fail'
            dataset_results[ds]['bootstrap_comparisons']={a:{'status':'unavailable: incomplete nested P_post','delta_AP':None,'AP_CI95':None,'AP_p_holm':None,'AP_gate_pass':False,'delta_MCC':None,'MCC_CI95':None,'attempted_draws':0,'valid_draws':0} for a in ['P_pre',*ARMS]}
            continue
        frame=pd.concat(predframes,ignore_index=True);dd=frame[frame.dataset==ds]
        def get(name):
            z=dd[dd.model==name].set_index('id').reindex(m.id)
            if z.prediction.isna().any():raise ValueError(f'missing OOF prediction {ds}/{name}')
            return z.prediction.to_numpy(float)
        post=get('nested_selected');pre=get('P_pre');th=dd[dd.model=='P_pre'].set_index('id').reindex(m.id).threshold.to_numpy(float)
        W=group_draws(g,5000,BASE+9000+di);draws={a:{'ap':[],'mcc':[]} for a in ['P_pre',*ARMS]}
        for w in W:
            ix=resample_ix(w)
            if not len(ix) or np.unique(y[ix]).size<2:continue
            post_m=matthews_corrcoef(y[ix],post[ix]>=th[ix])
            for a in ['P_pre',*ARMS]:
                ref=pre if a=='P_pre' else all_arms[ds][a]
                draws[a]['ap'].append(average_precision_score(y[ix],post[ix])-average_precision_score(y[ix],ref[ix]))
                draws[a]['mcc'].append(post_m-matthews_corrcoef(y[ix],ref[ix]>=th[ix]))
        comps={}
        for a,v in draws.items():
            ap=np.asarray(v['ap']);mc=np.asarray(v['mcc']);pv=min(1.,2*min(float(np.mean(ap<=0)),float(np.mean(ap>=0))))
            comps[a]={'delta_AP':float(average_precision_score(y,post)-average_precision_score(y,pre if a=='P_pre' else all_arms[ds][a])),'AP_CI95':np.percentile(ap,[2.5,97.5]).tolist(),'AP_p_raw':pv,'delta_MCC':float(matthews_corrcoef(y,post>=th)-matthews_corrcoef(y,(pre if a=='P_pre' else all_arms[ds][a])>=th)),'MCC_CI95':np.percentile(mc,[2.5,97.5]).tolist(),'attempted_draws':5000,'valid_draws':len(ap)}
        dataset_results[ds]['bootstrap_comparisons']=comps
        dataset_results[ds]['MCC_gate']='pass' if comps['P_pre']['MCC_CI95'][0]>.02 else ('fail' if comps['P_pre']['MCC_CI95'][1]<=.02 else 'inconclusive')
        for a in ARMS:pvalues.append((comps[a]['AP_p_raw'],ds,a))
    if len(pvalues)==30:
        ordered=sorted(pvalues);M=30;running=0.
        for i,(pv,ds,a) in enumerate(ordered):
            adj=max(running,min(1.,(M-i)*pv));running=adj;v=dataset_results[ds]['bootstrap_comparisons'][a]
            v['AP_p_holm']=adj if adj>=1/5000 else '<1/5000'
            v['AP_gate_pass']=v['AP_CI95'][0]>0 and adj<.05
            v.pop('AP_p_raw',None)
    else:
        # Keep all 30 planned contrasts explicit. Holm inference is not performed
        # over an incomplete family; no partial-family all-arm claim is allowed.
        for ds in ('devign','reveal'):
            for a in ARMS:
                v=dataset_results[ds].get('bootstrap_comparisons',{}).get(a)
                if v is not None:
                    v['AP_p_holm']=None;v['AP_gate_pass']=False;v.pop('AP_p_raw',None)
        dataset_results['AP_family_status']='unavailable: fewer than 30 computable planned contrasts; no partial Holm adjustment'
    for ds in ('devign','reveal'):
        if 'bootstrap_comparisons' not in dataset_results[ds]:continue
        c=dataset_results[ds]['bootstrap_comparisons'];dataset_results[ds]['all_arm_AP_gate']=all(c[a]['AP_gate_pass'] for a in ARMS)
        dataset_results[ds]['overall_gate']='pass' if dataset_results[ds]['MCC_gate']=='pass' and dataset_results[ds]['all_arm_AP_gate'] else ('fail' if dataset_results[ds]['MCC_gate']=='fail' or not dataset_results[ds]['nested_complete'] else 'inconclusive')
    out=OUT/'full';out.mkdir(exist_ok=True)
    pd.concat(predframes,ignore_index=True).to_csv(out/'outer_predictions.csv',index=False)
    all_nested=all(dataset_results[d]['nested_complete'] for d in ('devign','reveal'))
    results={'protocol_sha256':sha(PROTOCOL),'base_seed':BASE,'candidate_order':list(CANDS),'datasets':dataset_results,
        'overall_gate':'pass' if all(dataset_results[d].get('overall_gate')=='pass' for d in ('devign','reveal')) else ('fail_incomplete_nested_P_post' if not all_nested else 'fail_or_inconclusive')}
    (out/'results.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    (out/'source_audit.json').write_text(json.dumps({'datasets':source_audit,'donor_audit':donors,'donor_bank_hashes':donor_hashes,'split_audit':fold_audit},indent=2),encoding='utf-8')
    (out/'feature_manifest.json').write_text(json.dumps({'ordered_h3b_features':{d:feature_manifest for d in ('devign','reveal')},'candidate_widths':WIDTHS,'candidate_order':list(CANDS)},indent=2),encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({'registered':False,'post_cap_extension':True,'validation_only':True,'test_labels_scores_predictions_read':False,'historical_search_count':'at least 23 before Ext03; at least 26 after these three hypotheses','hypotheses':['T1','T2','T3'],'protocol':str(PROTOCOL),'protocol_sha256':sha(PROTOCOL),'test_metadata_incident':'Earlier provenance inspection displayed test IDs/change metadata from a mixed-split prompt audit; no test labels, scores, or predictions were read. Ext03 uses validation predicate reads only.','bootstrap_attempts_inner':2000,'bootstrap_attempts_final':5000,'holm_family':30,'zero_variance_scaling':'sklearn StandardScaler fixed behavior (scale=1 for zero variance)','seeds':'specified in frozen protocol','runtime':{'python':sys.version,'platform':platform.platform(),'numpy':np.__version__,'pandas':pd.__version__}},indent=2),encoding='utf-8')
    files=[Path(__file__),PROTOCOL,SOURCE/'inputs.parquet',SOURCE/'scores.parquet']+[H3/d/'xpre_validation.npz' for d in ('devign','reveal')]
    hashes={str(p):sha(p) for p in files};(out/'provenance_hashes.json').write_text(json.dumps(hashes,indent=2),encoding='utf-8')
    report=['# Ext03 validation-only results','',f"Protocol SHA-256: `{sha(PROTOCOL)}`.",'','This is a post-registration, post-cap exploratory extension. No test labels, scores, or predictions were read. A prior metadata-only test exposure is disclosed in manifest.json.','',f"Overall gate: **{results['overall_gate']}**.",'']
    for ds in ('devign','reveal'):
        d=dataset_results[ds];report += [f"## {ds}",'',f"N={d['n']}; groups={d['groups']}; selected bundles={[r.get('selected') for r in d['outer_folds']]}; MCC gate={d.get('MCC_gate')}; all-arm AP gate={d.get('all_arm_AP_gate')}.",'']
        if d.get('nested_complete') and 'bootstrap_comparisons' in d:
            c=d['bootstrap_comparisons']['P_pre'];report.append(f"Nested P_post vs P_pre: ΔAP={c['delta_AP']:.6f}; ΔMCC={c['delta_MCC']:.6f}, 95% CI={c['MCC_CI95']}.")
            failed=[a for a in ARMS if not d['bootstrap_comparisons'][a]['AP_gate_pass']]
            report.append(f"AP arm contrasts failing CI/Holm gate: {failed or 'none'}.")
            report.append('')
        else:
            report.append('Nested P_post incomplete because at least one outer fold selected no feasible candidate. This is a failure; no fallback was used, and all 30 planned AP comparisons are marked unavailable/not adjusted.')
            report.append('')
    report += ['See results.json, outer_predictions.csv, source_audit.json, feature_manifest.json and provenance_hashes.json.','Rerun command (PowerShell):',"`& 'C:\\Users\\yungn\\AppData\\Local\\Programs\\Python\\Python311\\python.exe' ext03_runner.py`",'']
    # Ext02 N3 is a validation-only historical diagnostic; it is never used in selection or gates.
    n3file=HOME/'runs/independent-post-ext02-validation/full/outer_predictions.csv'
    if n3file.is_file():
        n3=pd.read_csv(n3file);diagnostics={}
        for ds in ('devign','reveal'):
            if not dataset_results[ds]['nested_complete']:continue
            m=meta[meta.dataset==ds].sort_values('id').reset_index(drop=True);y=m.target_label.to_numpy(int)
            z=n3[(n3.dataset==ds)&(n3.model=='nested_selected')].set_index('id').reindex(m.id)
            if len(z)==len(m) and not z.prediction.isna().any() and np.array_equal(z.target_label.to_numpy(int),y):
                diagnostics[ds]={'Ext02_N3_AP':float(average_precision_score(y,z.prediction.to_numpy(float))),'N3_validation_ids_sha256':hashlib.sha256('\n'.join(m.id.astype(str)).encode()).hexdigest()}
                dataset_results[ds]['Ext02_N3_diagnostic']={'AP':diagnostics[ds]['Ext02_N3_AP'],'delta_AP_P_post_minus_Ext02_N3':dataset_results[ds]['metrics']['nested_selected']['AP']-diagnostics[ds]['Ext02_N3_AP']}
        if diagnostics:results['Ext02_N3_diagnostics']=diagnostics
    (out/'results.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    (out/'report.md').write_text('\n'.join(report),encoding='utf-8')
    return results

if __name__=='__main__':
    import argparse
    a=argparse.ArgumentParser();a.add_argument('--smoke',action='store_true');args=a.parse_args();print(json.dumps(run(args.smoke),indent=2))
