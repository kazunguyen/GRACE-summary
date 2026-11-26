"""Ext16 validation-only fixed-curvature MM solver for Ext15's focal estimator."""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path

import numpy as np
import pandas as pd
import scipy
from scipy.linalg import cho_factor,cho_solve
from scipy.special import expit
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (average_precision_score, roc_auc_score, matthews_corrcoef,
    balanced_accuracy_score, precision_score, recall_score, f1_score, confusion_matrix)
from scipy.stats import norm

import ext05_runner as ext5
ext3=ext5.ext3
HOME=Path(__file__).resolve().parent
OUT=HOME/'runs/independent-post-ext16-focal-mm-validation/attempt-1'
PRE=OUT/'preflight'; FULL=OUT/'full'
PROTOCOL=HOME/'ext16_focal_loss_mm_protocol_vi.md'
EXT03=HOME/'runs/independent-post-ext03-multisignal-validation/full'
EXT03_PREF=HOME/'runs/independent-post-ext03-multisignal-validation/preflight'
EXT04=HOME/'runs/independent-post-ext04-decision-aware-validation/full'
EXT04_PREF=HOME/'runs/independent-post-ext04-decision-aware-validation/preflight'
BASE=20261123; CS=(.001,.01,.05,.1,1.0); ARMS=list(ext5.ARMS)
BASE_WIDTH=34; WIDTH=43; GAMMA=2.0
OBJECTIVE_GUARD_REL=1e-10
MM_MAX_UPDATES=100000; MM_GRAD_L2_TOL=1e-8; MM_GRAD_INF_TOL=1e-6
MM_LINEAR_BACKWARD_TOL=1e-12; MM_DESCENT_ULPS=64
CURVATURE_BOUND=4.0/np.e+135.0/256.0
EXT15=HOME/'runs/independent-post-ext15-focal-loss-posterior-validation/attempt-1'
EXT15_PRE=EXT15/'preflight'
EXT15_RUNNER=HOME/'ext15_focal_loss_posterior_runner.py'
EXT15_PROTOCOL=HOME/'ext15_focal_loss_posterior_protocol_vi.md'
ADDED=['log_odds_B0','log_odds_B2','log_odds_B2_nolabel',
       'B0_x_m','B2_x_m','B2_nolabel_x_m',
       'B0_x_abs_m','B2_x_abs_m','B2_nolabel_x_abs_m']

def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def atomic_json(path,obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(obj,indent=2,allow_nan=False),encoding='utf-8');tmp.replace(path)

def feature_matrix(data,rows):
    """Build exactly [H3-B34, a, a*m, a*abs(m)] with no P_pre state."""
    rows=np.asarray(rows,dtype=int);x=np.asarray(data['x'][rows],dtype=np.float64)
    if x.ndim!=2 or x.shape[1]!=34 or data['names'][5]!='p_gate':
        raise ValueError('frozen H3-B schema/p_gate index mismatch')
    p=np.clip(x[:,5],1e-6,1-1e-6)
    m=np.clip(np.log(p/(1-p)),-5.,5.)
    logits=data['logits']
    a=np.column_stack([logits['B0'][rows],logits['B2'][rows],logits['B2-nolabel'][rows]])
    z=np.column_stack([x,a,a*m[:,None],a*np.abs(m[:,None])]).astype(np.float64)
    if z.shape!=(len(rows),WIDTH) or not np.isfinite(z).all():
        raise ValueError('Ext16 43-column feature matrix width/finiteness failure')
    return z

def focal_loss_gradient_hessian(eta,y,need_hessian=True):
    """Per-row binary focal loss (gamma=2), eta gradient, and eta Hessian."""
    eta=np.asarray(eta,dtype=np.float64);y=np.asarray(y,dtype=np.float64)
    if eta.shape!=y.shape or not np.isfinite(eta).all() or not np.isin(y,[0.,1.]).all():
        raise ValueError('invalid focal-loss arguments')
    p=expit(eta);r=1.0-p
    logp=-np.logaddexp(0.0,-eta);logr=-np.logaddexp(0.0,eta)
    loss=-y*r*r*logp-(1.0-y)*p*p*logr
    g1=2.0*p*r*r*logp-r*r*r
    g0=-2.0*p*p*r*logr+p*p*p
    grad=y*g1+(1.0-y)*g0
    hess=None
    if need_hessian:
        h1=p*r*(2.0*r*(1.0-3.0*p)*logp+5.0*r*r)
        h0=p*r*(-2.0*p*(2.0-3.0*p)*logr+5.0*p*p)
        hess=y*h1+(1.0-y)*h0
    if not np.isfinite(loss).all() or not np.isfinite(grad).all() or (need_hessian and not np.isfinite(hess).all()):
        raise FloatingPointError('nonfinite focal loss/derivatives')
    return loss,grad,hess

def objective_value_gradient(theta,X,y,C):
    """Objective and gradient only; used by MM iterations without building a Hessian."""
    theta=np.asarray(theta,dtype=np.float64);X=np.asarray(X,dtype=np.float64);y=np.asarray(y,dtype=np.float64)
    if X.ndim!=2 or X.shape[1]!=WIDTH or theta.shape!=(WIDTH+1,) or len(X)!=len(y):
        raise ValueError('focal objective shape mismatch')
    if not np.isfinite(theta).all() or not np.isfinite(X).all() or not np.isfinite(y).all():
        raise ValueError('nonfinite focal objective input')
    D=np.column_stack([X,np.ones(len(X),dtype=np.float64)])
    beta=theta[:-1];eta=D@theta
    loss_i,g_i,_=focal_loss_gradient_hessian(eta,y,need_hessian=False)
    value=float(np.sum(loss_i)+np.dot(beta,beta)/(2.0*float(C)))
    grad=D.T@g_i;grad[:-1]+=beta/float(C)
    if not np.isfinite(value) or not np.isfinite(grad).all():raise FloatingPointError('nonfinite focal objective/gradient state')
    return value,grad

def objective_hessian(theta,X,y,C):
    theta=np.asarray(theta,dtype=np.float64);X=np.asarray(X,dtype=np.float64);y=np.asarray(y,dtype=np.float64)
    D=np.column_stack([X,np.ones(len(X),dtype=np.float64)]);eta=D@theta
    _,_,h_i=focal_loss_gradient_hessian(eta,y,need_hessian=True)
    hess=D.T@(h_i[:,None]*D);hess[:-1,:-1]+=np.eye(WIDTH,dtype=np.float64)/float(C)
    if not np.isfinite(hess).all():raise FloatingPointError('nonfinite focal Hessian')
    return hess

def objective_gradient_hessian(theta,X,y,C):
    """Complete objective state for derivative diagnostics and finite-difference checks."""
    value,grad=objective_value_gradient(theta,X,y,C);hess=objective_hessian(theta,X,y,C)
    return value,grad,hess

def log_softplus(x):
    x=np.asarray(x,dtype=np.float64)
    out=np.empty_like(x);small=x < -36.0;out[small]=x[small]
    with np.errstate(divide='ignore',invalid='ignore'):
        out[~small]=np.log(np.logaddexp(0.0,x[~small]))
    return out

def log_h_from_logit(eta):
    """Stable log h(sigmoid(eta)) for CVPR-2021 gamma=2 posterior recovery."""
    eta=np.asarray(eta,dtype=np.float64)
    logv=-np.logaddexp(0.0,-eta);log1mv=-np.logaddexp(0.0,eta)
    logden=np.logaddexp(2.0*log1mv,np.log(2.0)+logv+log1mv+log_softplus(-eta))
    out=logv-logden
    if not np.isfinite(out).all():raise FloatingPointError('nonfinite log posterior transform')
    return out

def corrected_score_probability(eta):
    eta=np.asarray(eta,dtype=np.float64)
    # h(1-q) is h(sigmoid(-eta)); score stays in log-odds space for AP stability.
    score=log_h_from_logit(eta)-log_h_from_logit(-eta)
    probability=expit(score)
    if not np.isfinite(score).all() or not np.isfinite(probability).all() or np.any((probability<0)|(probability>1)):
        raise FloatingPointError('invalid posterior-recovered output')
    return score,probability

def fit_post(X,y,C):
    """Fixed global-curvature MM fit; only X, y, C enter—never P_pre state or tau."""
    X=np.asarray(X,dtype=np.float64);y=np.asarray(y,dtype=np.int8);C=float(C)
    if X.ndim!=2 or X.shape[1]!=WIDTH or len(X)!=len(y) or not np.isfinite(X).all() or not np.isfinite(C) or C<=0:
        raise ValueError('fit_post shape/finiteness/C failure')
    if set(np.unique(y))!={0,1}:raise ValueError('fit_post requires both classes')
    scaler=StandardScaler().fit(X);Xs=np.asarray(scaler.transform(X),dtype=np.float64)
    U=np.column_stack([Xs,np.ones(len(Xs),dtype=np.float64)])
    R=np.diag(np.r_[np.full(WIDTH,1.0/C,dtype=np.float64),0.0])
    M=2.0*(U.T@U)+R
    try:
        factor=cho_factor(M,lower=True,check_finite=True)
    except Exception as exc:
        diag={'C':C,'n':int(len(y)),'width':WIDTH,'usable':False,'failure':'majorizer_cholesky_failure',
            'error':type(exc).__name__+': '+str(exc)}
        return {'scaler':scaler,'theta':np.zeros(WIDTH+1),'C':C,'usable':False},diag
    theta=np.zeros(WIDTH+1,dtype=np.float64)
    init_obj,_=objective_value_gradient(theta,Xs,y,C);current_obj=init_obj
    iterations=0;max_backward_error=0.0;minimum_descent_margin=0.0;max_objective_increase=0.0;unchanged=False;failure=None
    grad_l2=float('inf');grad_inf=float('inf')
    while iterations<MM_MAX_UPDATES:
        current_obj,grad=objective_value_gradient(theta,Xs,y,C)
        grad_l2=float(np.linalg.norm(grad,ord=2));grad_inf=float(np.linalg.norm(grad,ord=np.inf))
        if grad_l2<=MM_GRAD_L2_TOL:break
        try:
            direction=cho_solve(factor,-grad,check_finite=True)
        except Exception as exc:
            failure='majorizer_solve_failure:'+type(exc).__name__+': '+str(exc);break
        residual=M@direction+grad
        denom=float(np.linalg.norm(M,ord=np.inf)*np.linalg.norm(direction,ord=np.inf)+np.linalg.norm(grad,ord=np.inf))
        backward_error=float(np.linalg.norm(residual,ord=np.inf)/denom) if denom>0 else (0.0 if not np.any(residual) else float('inf'))
        max_backward_error=max(max_backward_error,backward_error)
        if not np.isfinite(direction).all() or not np.isfinite(backward_error) or backward_error>MM_LINEAR_BACKWARD_TOL:
            failure='nonfinite_or_inaccurate_majorizer_solve';break
        updated=theta+direction
        if np.array_equal(updated,theta):unchanged=True;failure='update_unchanged_before_convergence';break
        new_obj,new_grad=objective_value_gradient(updated,Xs,y,C)
        guard_step=MM_DESCENT_ULPS*np.finfo(np.float64).eps*max(1.0,abs(current_obj),abs(new_obj))
        max_objective_increase=max(max_objective_increase,float(new_obj-current_obj))
        predicted_drop=.5*float(grad@direction*-1.0)
        descent_margin=float(new_obj-(current_obj-predicted_drop))
        minimum_descent_margin=min(minimum_descent_margin,descent_margin)
        if not np.isfinite(updated).all() or not np.isfinite(new_obj) or not np.isfinite(new_grad).all():
            failure='nonfinite_MM_update';break
        if new_obj>current_obj+guard_step:
            failure='objective_increased_beyond_floating_guard';break
        if descent_margin>guard_step:
            failure='majorization_descent_bound_violated';break
        theta=updated;iterations+=1;current_obj=new_obj
        grad_l2=float(np.linalg.norm(new_grad,ord=2));grad_inf=float(np.linalg.norm(new_grad,ord=np.inf))
        if grad_l2<=MM_GRAD_L2_TOL:break
    converged=bool(grad_l2<=MM_GRAD_L2_TOL and iterations<MM_MAX_UPDATES and failure is None)
    final_obj,final_grad=objective_value_gradient(theta,Xs,y,C)
    grad_l2=float(np.linalg.norm(final_grad,ord=2));grad_inf=float(np.linalg.norm(final_grad,ord=np.inf))
    finite=bool(np.isfinite(theta).all() and np.isfinite(final_obj) and np.isfinite(final_grad).all())
    guard=OBJECTIVE_GUARD_REL*max(1.0,abs(init_obj));no_worse=bool(finite and final_obj<=init_obj+guard)
    usable=bool(converged and finite and grad_l2<=MM_GRAD_L2_TOL and grad_inf<=MM_GRAD_INF_TOL and no_worse)
    model={'scaler':scaler,'theta':theta,'C':C,'usable':usable}
    diag={'C':C,'n':int(len(y)),'width':WIDTH,'scaler':'StandardScaler','solver':'fixed global-curvature MM with Cholesky majorizer',
        'gamma':GAMMA,'iterations':iterations,'maximum_updates':MM_MAX_UPDATES,'converged_before_cap':converged,
        'failure':failure,'update_unchanged_before_convergence':unchanged,'initial_objective':float(init_obj),
        'final_objective':float(final_obj),'objective_guard':float(guard),'objective_no_worse_than_zero_init':no_worse,
        'loss_reduction':float(init_obj-final_obj),'gradient_l2':grad_l2,'gradient_l2_tolerance':MM_GRAD_L2_TOL,
        'gradient_inf':grad_inf,'gradient_inf_tolerance':MM_GRAD_INF_TOL,'max_linear_backward_error':max_backward_error,
        'linear_backward_tolerance':MM_LINEAR_BACKWARD_TOL,'minimum_descent_majorization_margin':minimum_descent_margin,
        'max_observed_objective_increase':max_objective_increase,'descent_floating_guard_ulps':MM_DESCENT_ULPS,
        'majorizer_cholesky_once_per_fit':True,'curvature_bound':CURVATURE_BOUND,'majorizer_coefficient':2.0,
        'finite_state':finite,'usable':usable}
    return model,diag

def predict_post(model,X):
    X=np.asarray(X,dtype=np.float64)
    if not model['usable']:raise RuntimeError('focal solver fit failed locked usability criteria')
    Xs=model['scaler'].transform(X);eta=np.asarray(Xs,dtype=np.float64)@model['theta'][:-1]+model['theta'][-1]
    q=expit(eta);score,p=corrected_score_probability(eta)
    if not np.isfinite(eta).all() or not np.isfinite(q).all() or not np.isfinite(p).all() or not np.isfinite(score).all():
        raise FloatingPointError('nonfinite P_post heldout prediction')
    return q,p,score,eta

def frozen_pre(data,Q,seed): return ext5.frozen_pre(data,Q,seed)
def group_folds(y,g,seed): return ext5.group_folds(np.asarray(y),np.asarray(g).astype(str),int(seed))

def choose_feasible_c(diagnostics):
    """Require the complete frozen 5x3 solver grid; never use a reduced C subgrid."""
    if not diagnostics or not all(r.get('complete',False) for r in diagnostics):return None
    feasible=[r for r in diagnostics if r.get('AP_feasible_vs_all_15',False)]
    return max(feasible,key=lambda r:(float(r['AP']),-float(r['C'])))['C'] if feasible else None

def select_c(data,Q,seed):
    """Three-fold grouped OOF C selection: AP feasibility then max pooled AP."""
    Q=np.asarray(Q,dtype=int);y=data['y'];g=data['g']; yy=y[Q]
    folds=group_folds(yy,g[Q],seed)
    oof={float(c):np.full(len(Q),np.nan) for c in CS}; fold_info=[];solver={float(c):[] for c in CS}
    for fi,(tr,va) in enumerate(folds):
        A=Q[tr];B=Q[va];Za=feature_matrix(data,A);Zb=feature_matrix(data,B);detail={}
        for c in CS:
            try:
                model,diag=fit_post(Za,y[A],c)
                if not diag['usable']:
                    solver[float(c)].append(diag);detail[str(c)]={'status':'solver_not_usable','diagnostic':diag};continue
                q,p,s,eta=predict_post(model,Zb)
                if not np.isfinite(q).all() or not np.isfinite(p).all() or not np.isfinite(s).all() or not np.isfinite(eta).all():raise RuntimeError('focal posterior score/probability check failed')
                oof[float(c)][va]=s;solver[float(c)].append(diag)
                detail[str(c)]={'status':'complete','iterations':diag['iterations'],'gradient_inf':diag['gradient_inf']}
            except Exception as exc:
                solver[float(c)].append({'failure':type(exc).__name__+': '+str(exc)})
                detail[str(c)]={'status':'fit_failure','error':type(exc).__name__+': '+str(exc)}
        fold_info.append({'fold':fi,'train_n':len(A),'heldout_n':len(B),'solver_by_C':detail})
    if len(data['arms'])!=15 or set(data['arms'])!=set(ARMS):raise ValueError('raw-arm registry not exactly 15')
    arm_ap={a:float(average_precision_score(yy,p[Q])) for a,p in data['arms'].items()}
    diagnostics=[]
    for c in CS:
        score=oof[float(c)];complete=bool(np.isfinite(score).all() and len(solver[float(c)])==3 and all(q.get('usable',False) for q in solver[float(c)]))
        ap=float(average_precision_score(yy,score)) if complete else None
        feasible=bool(complete and all(ap>v for v in arm_ap.values()))
        diagnostics.append({'C':float(c),'complete':complete,'AP':ap,'AP_scoring':'posterior-recovered corrected logit s','AP_feasible_vs_all_15':feasible,
            'solver_by_fold':solver[float(c)]})
    grid_complete=all(r['complete'] for r in diagnostics)
    selected=choose_feasible_c(diagnostics)
    reason='selected' if selected is not None else ('incomplete_required_C_grid' if not grid_complete else 'no_AP_feasible_C')
    return {'C':selected,'folds':fold_info,'C_diagnostics':diagnostics,'arm_AP':arm_ap,'reason':reason,
        'oof_score':None if selected is None else oof[float(selected)],'complete':grid_complete}

def metric(y,p,s,tau):
    decision=p>=tau;tn,fp,fn,tp=confusion_matrix(y,decision,labels=[0,1]).ravel()
    pc=np.clip(np.asarray(p,dtype=np.float64),1e-15,1-1e-15)
    nll=float(np.mean(-np.asarray(y)*np.log(pc)-(1-np.asarray(y))*np.log1p(-pc)))
    return {'AP':float(average_precision_score(y,s)),'AUROC':float(roc_auc_score(y,s)),
        'MCC':float(matthews_corrcoef(y,decision)),'balanced_accuracy':float(balanced_accuracy_score(y,decision)),
        'Brier':float(np.mean((np.asarray(p)-np.asarray(y))**2)),'NLL':nll,
        'precision':float(precision_score(y,decision,zero_division=0)),'recall':float(recall_score(y,decision,zero_division=0)),
        'F1':float(f1_score(y,decision,zero_division=0)),
        'confusion':{'tn':int(tn),'fp':int(fp),'fn':int(fn),'tp':int(tp)},'positive_rate':float(decision.mean())}

def holm(pvalues):
    p=np.asarray(pvalues,dtype=float);m=len(p);order=np.argsort(p);adj=np.empty(m);running=0.
    for rank,idx in enumerate(order):
        running=max(running,(m-rank)*p[idx]);adj[idx]=min(1.,running)
    return adj

def bootstrap(y,g,tau,pre,post,postscore,arms,ds_index,draw_count=5000):
    draws=ext5.group_draws(g,draw_count,BASE+9000+ds_index)
    diffs={a:{'ap':[],'mcc':[]} for a in arms};dm=[];valid=0
    for w in draws:
        ix=ext5.idx_from_weights(w)
        if not len(ix) or np.unique(y[ix]).size<2:continue
        valid+=1;postm=matthews_corrcoef(y[ix],post[ix]>=tau[ix]);prem=matthews_corrcoef(y[ix],pre[ix]>=tau[ix]);dm.append(postm-prem)
        for a,ref in arms.items():
            diffs[a]['ap'].append(average_precision_score(y[ix],postscore[ix])-average_precision_score(y[ix],ref[ix]))
            diffs[a]['mcc'].append(postm-matthews_corrcoef(y[ix],ref[ix]>=tau[ix]))
    out={}
    for a,ref in arms.items():
        da=np.asarray(diffs[a]['ap']);mm=np.asarray(diffs[a]['mcc'])
        out[a]={'delta_AP':float(average_precision_score(y,postscore)-average_precision_score(y,ref)),
            'AP_CI95':np.percentile(da,[2.5,97.5]).tolist(),
            'AP_p_raw':min(1.,2*min(float(np.mean(da<=0)),float(np.mean(da>=0)))),
            'delta_MCC':float(matthews_corrcoef(y,post>=tau)-matthews_corrcoef(y,ref>=tau)),
            'MCC_CI95':np.percentile(mm,[2.5,97.5]).tolist()}
    pre_delta=matthews_corrcoef(y,post>=tau)-matthews_corrcoef(y,pre>=tau)
    return {'comparisons':out,'delta_MCC_P_post_minus_P_pre':float(pre_delta),
        'MCC_P_post_minus_P_pre_CI95':np.percentile(dm,[2.5,97.5]).tolist(),
        'attempted_draws':int(draw_count),'valid_draws':valid,'seed':BASE+9000+ds_index}

def preflight_smoke():
    OUT.mkdir(parents=True,exist_ok=True);PRE.mkdir(parents=True,exist_ok=True)
    if scipy.__version__!='1.15.2':raise RuntimeError(f'Ext16 freezes SciPy 1.15.2; found {scipy.__version__}')
    (OUT/PROTOCOL.name).write_text(PROTOCOL.read_text(encoding='utf-8'),encoding='utf-8',newline='\n')
    # Hash/schema preflight reads validation H3 feature-name metadata only.
    schema={};sources={}
    for ds in ('devign','reveal'):
        path=ext3.H3/ds/'xpre_validation.npz'
        z=np.load(path,allow_pickle=False);names=z['feature_names'].astype(str).tolist();z.close()
        if len(names)!=34 or names[5]!='p_gate':raise AssertionError(f'{ds}: p_gate index/schema failed')
        schema[ds]={'n_features':len(names),'feature_names':names,'p_gate_index':5,'p_gate_name':names[5],'sha256':sha(path)}
        sources[str(path)]={'sha256':sha(path),'role':'validation H3-B feature cache/schema'}
    ext15_manifest=json.loads((EXT15_PRE/'frozen_manifest.json').read_text(encoding='utf-8'))
    ext15_smoke=json.loads((EXT15_PRE/'smoke.json').read_text(encoding='utf-8'))
    ext15_registry_path=EXT15_PRE/'source_registry.json'
    if ext15_manifest.get('fit_started') is not False or ext15_smoke.get('status')!='passed':
        raise AssertionError('Ext15 reference preflight is not the frozen pre-fit snapshot')
    if ext15_manifest.get('runner_sha256')!=sha(EXT15_RUNNER) or ext15_manifest.get('protocol_sha256')!=sha(EXT15_PROTOCOL):
        raise AssertionError('Ext15 reference runner/protocol hash mismatch')
    if ext15_manifest.get('source_registry_sha256')!=sha(ext15_registry_path):
        raise AssertionError('Ext15 source registry hash mismatch')
    ext15_registry=json.loads(ext15_registry_path.read_text(encoding='utf-8'))
    for p,meta in ext15_registry['sources'].items():
        if not Path(p).is_file() or sha(p)!=meta['sha256']:raise AssertionError(f'Ext15 frozen source mismatch: {p}')
    for path in [Path(__file__),PROTOCOL,HOME/'ext03_runner.py',HOME/'ext03_protocol_vi.md',HOME/'ext05_runner.py',HOME/'ext05_protocol_vi.md',
        EXT15_RUNNER,EXT15_PROTOCOL,EXT15_PRE/'frozen_manifest.json',EXT15_PRE/'smoke.json',ext15_registry_path,
        EXT03/'outer_predictions.csv',EXT03/'results.json',EXT03/'manifest.json',EXT03_PREF/'source_registry.json',
        EXT04/'outer_predictions.csv',EXT04/'results.json',EXT04/'manifest.json',EXT04_PREF/'source_registry.json']:
        if not path.is_file():raise FileNotFoundError(path)
        sources[str(path)]={'sha256':sha(path),'role':'runner/protocol or frozen validation parity/comparator artifact'}
    # Synthetic formula, feature width, formula order and model smoke (no benchmark rows).
    rng=np.random.default_rng(20261125);n=180;x=rng.normal(size=(n,34));x[:,5]=rng.uniform(.03,.97,n)
    ll={k:rng.normal(size=n) for k in ('B0','B2','B2-nolabel')}
    fake_names=[f'f{i}' for i in range(34)];fake_names[5]='p_gate'
    fake={'x':x,'names':fake_names,'logits':ll}
    z=feature_matrix(fake,np.arange(n));m=np.clip(np.log(np.clip(x[:,5],1e-6,1-1e-6)/(1-np.clip(x[:,5],1e-6,1-1e-6))),-5,5)
    a=np.column_stack([ll[k] for k in ('B0','B2','B2-nolabel')])
    if z.shape!=(n,43) or not np.allclose(z[:,34:37],a) or not np.allclose(z[:,37:40],a*m[:,None]) or not np.allclose(z[:,40:43],a*np.abs(m[:,None])):
        raise AssertionError('synthetic feature formula/order check failed')
    # Analytic objective derivatives are checked against central finite differences.
    Xfd=rng.normal(size=(24,WIDTH))*.25;yfd=np.tile([0,1],12).astype(np.int8)
    thetafd=rng.normal(size=WIDTH+1)*.08;Cfd=.1;v,gfd,hfd=objective_gradient_hessian(thetafd,Xfd,yfd,Cfd)
    eps=2e-5;gnum=np.empty_like(thetafd);hnum=np.empty_like(hfd)
    for j in range(len(thetafd)):
        ej=np.zeros_like(thetafd);ej[j]=eps
        vp=objective_gradient_hessian(thetafd+ej,Xfd,yfd,Cfd)[0];vm=objective_gradient_hessian(thetafd-ej,Xfd,yfd,Cfd)[0]
        gnum[j]=(vp-vm)/(2*eps)
        gp=objective_gradient_hessian(thetafd+ej,Xfd,yfd,Cfd)[1];gm=objective_gradient_hessian(thetafd-ej,Xfd,yfd,Cfd)[1]
        hnum[:,j]=(gp-gm)/(2*eps)
    grad_err=float(np.max(np.abs(gfd-gnum)));hess_err=float(np.max(np.abs(hfd-hnum)))
    if grad_err>2e-5 or hess_err>3e-5 or not np.allclose(hfd,hfd.T,atol=1e-11,rtol=1e-11):
        raise AssertionError(f'focal gradient/Hessian finite-difference failure: {grad_err}/{hess_err}')
    # Posterior recovery is checked directly, including tails, symmetry, and monotonicity.
    grid=np.linspace(-30,30,601);score_grid,prob_grid=corrected_score_probability(grid)
    if np.any(np.diff(score_grid)<0) or not np.allclose(score_grid,-score_grid[::-1],atol=2e-10,rtol=2e-12):
        raise AssertionError('fixed posterior transform monotonicity/symmetry failed')
    tail_score,tail_prob=corrected_score_probability(np.array([-1000.,0.,1000.]))
    if not np.isfinite(tail_score).all() or not np.array_equal(tail_prob,np.array([0.,.5,1.])):
        raise AssertionError('posterior transform tail/boundary check failed')
    qgrid=np.array([1e-6,.01,.2,.5,.8,.99,1-1e-6])
    den=(1-qgrid)**2-2*qgrid*(1-qgrid)*np.log(qgrid)
    hq=qgrid/den;qr=1-qgrid;denr=(1-qr)**2-2*qr*(1-qr)*np.log(qr);hr=qr/denr
    p_direct=hq/(hq+hr);_,p_stable=corrected_score_probability(np.log(qgrid/(1-qgrid)))
    if not np.allclose(p_stable,p_direct,rtol=2e-10,atol=2e-12):raise AssertionError('posterior recovery formula mismatch')
    # The locked focal curvature bound and resulting global Hessian majorization.
    eta_grid=np.linspace(-60,60,2401)
    _,_,h0=focal_loss_gradient_hessian(eta_grid,np.zeros_like(eta_grid))
    _,_,h1=focal_loss_gradient_hessian(eta_grid,np.ones_like(eta_grid))
    max_abs_curvature=float(max(np.max(np.abs(h0)),np.max(np.abs(h1))))
    if CURVATURE_BOUND>=2.0 or max_abs_curvature>CURVATURE_BOUND+2e-12:
        raise AssertionError('gamma-2 focal curvature bound check failed')
    Ufd=np.column_stack([Xfd,np.ones(len(Xfd))]);Rfd=np.diag(np.r_[np.full(WIDTH,1/Cfd),0.])
    Mfd=2*(Ufd.T@Ufd)+Rfd;Hfd=objective_hessian(thetafd,Xfd,yfd,Cfd)
    min_majorizer_eig=float(np.linalg.eigvalsh(Mfd-Hfd).min())
    if min_majorizer_eig < -1e-9*max(1.,float(np.linalg.norm(Mfd,ord=2))):raise AssertionError('MM Hessian majorization failed')
    factorfd=cho_factor(Mfd,lower=True,check_finite=True);theta0fd=np.zeros(WIDTH+1)
    f0fd,g0fd=objective_value_gradient(theta0fd,Xfd,yfd,Cfd);directionfd=cho_solve(factorfd,-g0fd,check_finite=True)
    residualfd=Mfd@directionfd+g0fd;denomfd=float(np.linalg.norm(Mfd,ord=np.inf)*np.linalg.norm(directionfd,ord=np.inf)+np.linalg.norm(g0fd,ord=np.inf))
    backwardfd=float(np.linalg.norm(residualfd,ord=np.inf)/denomfd)
    f1fd,_=objective_value_gradient(theta0fd+directionfd,Xfd,yfd,Cfd)
    pred_dropfd=.5*float(-g0fd@directionfd);round_guardfd=MM_DESCENT_ULPS*np.finfo(float).eps*max(1.,abs(f0fd),abs(f1fd))
    if backwardfd>MM_LINEAR_BACKWARD_TOL or f1fd>f0fd+round_guardfd or f1fd>f0fd-pred_dropfd+round_guardfd:
        raise AssertionError('MM linear solve / monotone descent / majorization step failed')
    beta=rng.normal(size=43)*.08;y=(rng.random(n)<expit(np.clip(z@beta/3,-10,10))).astype(np.int8)
    if len(np.unique(y))!=2:raise AssertionError('synthetic labels need both classes')
    model,diag=fit_post(z,y,.1);model2,diag2=fit_post(z,y,.1);q,p,s,eta=predict_post(model,z);q2,p2,s2,eta2=predict_post(model2,z)
    if not diag['usable'] or not np.isfinite(q).all() or not np.isfinite(p).all() or not np.isfinite(s).all() or not np.isfinite(eta).all():raise AssertionError('synthetic MM focal fit/predict failed')
    if not diag2['usable'] or not np.array_equal(model['theta'],model2['theta']) or not np.array_equal(p,p2) or not np.array_equal(s,s2):
        raise AssertionError('deterministic MM fit did not reproduce exactly')
    descent_tol=MM_DESCENT_ULPS*np.finfo(float).eps*max(1.,abs(diag['initial_objective']),abs(diag['final_objective']))
    if diag['max_linear_backward_error']>MM_LINEAR_BACKWARD_TOL or diag['max_observed_objective_increase']>descent_tol or \
       diag['minimum_descent_majorization_margin']>descent_tol or diag['gradient_l2']>MM_GRAD_L2_TOL:
        raise AssertionError('MM solver diagnostics violate convergence/solve/descent guards')
    synthetic_metrics=metric(y,p,s,np.full(n,.5))
    raw_q_brier=float(np.mean((q-y)**2));raw_q_nll=float(np.mean(np.logaddexp(0.0,eta)-y*eta))
    if not np.isfinite([synthetic_metrics['Brier'],synthetic_metrics['NLL'],raw_q_brier,raw_q_nll]).all():
        raise AssertionError('raw focal q/corrected probability diagnostics are nonfinite')
    fake_cdiag=[{'C':.001,'complete':True,'AP':.8,'AP_feasible_vs_all_15':True},
        {'C':.01,'complete':False,'AP':None,'AP_feasible_vs_all_15':False}]
    if choose_feasible_c(fake_cdiag) is not None:raise AssertionError('incomplete C grid incorrectly allowed reduced-subgrid selection')
    boot_groups=np.repeat(np.arange(45),4);boot_y=np.tile([0,1,0,1],45);boot_tau=np.full(n,.5)
    boot_refs={f'arm_{i}':rng.uniform(.05,.95,n) for i in range(15)}
    boot_result=bootstrap(boot_y,boot_groups,boot_tau,rng.uniform(.05,.95,n),rng.uniform(.05,.95,n),
        rng.normal(size=n),boot_refs,0,draw_count=25)
    if boot_result['attempted_draws']!=25 or any(len(boot_result['comparisons'][k]['AP_CI95'])!=2 for k in boot_refs):
        raise AssertionError('paired AP bootstrap indexed-resample smoke failed')
    groups=np.repeat(np.arange(45),4);labels=np.tile([0,1,0,1],45);f1=group_folds(labels,groups,BASE+8100);f2=group_folds(labels,groups,BASE+8100)
    if len(f1)!=3 or any(not np.array_equal(a[0],b[0]) or not np.array_equal(a[1],b[1]) for a,b in zip(f1,f2)):raise AssertionError('grouped split determinism failed')
    if any(set(groups[a])&set(groups[b]) for a,b in f1):raise AssertionError('group leakage in synthetic folds')
    # Ensure no P_pre/tau input is accepted by P_post fit API.
    import inspect
    fit_params=set(inspect.signature(fit_post).parameters)
    if fit_params & {'pre','p_pre','tau','threshold','frozenpre'}:raise AssertionError('P_pre/tau leaked into fit_post signature')
    # Verify the frozen registry is validation-only by checking names, without opening test data.
    extreg=json.loads((EXT03_PREF/'source_registry.json').read_text(encoding='utf-8'))
    registry_names=json.dumps(extreg).lower()
    if 'test_' in registry_names or 'test/' in registry_names or 'test\\' in registry_names:raise AssertionError('Ext03 source registry contains test-named entry')
    # Validation-only integrity pass through the audited predicate loaders.
    meta=ext5.load_inputs(); donor_audit,_=ext3.verify_donors(meta); validation_audit={}
    for ds in ('devign','reveal'):
        data=ext5.build_sources(meta,ds); ids=data['ids']; y=data['y']; g=data['g']
        zval=feature_matrix(data,np.arange(len(ids)))
        if len(data['arms'])!=15 or set(data['arms'])!=set(ARMS):raise AssertionError(f'{ds}: expected exact 15 raw vectors')
        # Source loader enforces exact B2-rep equality before excluding duplicate from its vector family.
        validation_audit[ds]={'validation_rows':len(ids),'unique_ids':len(set(ids)),'groups':int(pd.Series(g).nunique()),
            'positive_labels':int(y.sum()),'candidate_width':int(zval.shape[1]),'finite':bool(np.isfinite(zval).all()),
            'unique_raw_arms':len(data['arms']),'B2_rep_duplicate':'verified by ext03.load_arms','source_provenance':data['provenance']}
        for path in (ext3.SOURCE/'inputs.parquet',ext3.SOURCE/'scores.parquet'):
            sources[str(path)]={'sha256':sha(path),'role':'mixed-split parquet; rows accessed only with split == validation predicate'}
    reg={'sources':sources,'frozen_validation_registry_sha256':sha(EXT03_PREF/'source_registry.json'),
        'validation_registry_source_paths':list(extreg.get('sources',{})),
        'ext15_reference':{'runner_sha256':ext15_manifest['runner_sha256'],'protocol_sha256':ext15_manifest['protocol_sha256'],
            'source_registry_sha256':ext15_manifest['source_registry_sha256'],'fit_started':False}}
    regpath=PRE/'source_registry.json';atomic_json(regpath,reg)
    source_names=[str(x).lower() for x in sources]
    test_named=sum(('test_' in p or '\\test\\' in p or '/test/' in p) for p in source_names)
    html_named=sum('.html' in p for p in source_names)
    if test_named or html_named:raise AssertionError('test-named or HTML source path entered Ext16 registry')
    frozen={'registered':False,'post_cap_extension':True,'validation_only':True,'test_labels_scores_predictions_read':False,
        'candidate':'Ext16 solver-only fixed-curvature MM variation for Ext15 focal objective/posterior recovery',
        'historical_hypothesis_count':'at least 41 after this candidate','feature_width':WIDTH,
        'feature_order':['34 ordered H3-B features',*ADDED],'p_gate_index':5,'C_grid':list(CS),'gamma':GAMMA,
        'selector':'AP-only grouped OOF on outer T; strict AP superiority over all 15 raw vectors; highest feasible pooled AP, tie smaller C',
        'solver':'fixed global-curvature MM; zero start; one Cholesky per fit; no acceleration/line search/restarts/jitter',
        'MM_max_updates':MM_MAX_UPDATES,'MM_grad_l2_tol':MM_GRAD_L2_TOL,'MM_grad_inf_tol':MM_GRAD_INF_TOL,
        'MM_linear_backward_tol':MM_LINEAR_BACKWARD_TOL,'MM_descent_guard_ulps':MM_DESCENT_ULPS,'curvature_bound':CURVATURE_BOUND,
        'objective_guard':'final <= zero-init + 1e-10*max(1,abs(zero-init objective))','gradient_inf_tolerance':1e-6,
        'P_pre_separation':'hash guard may verify frozen Ext03/04 files as opaque bytes; no P_pre records/values/state/tau are parsed or materialized until AP-only selection and P_post predictions are complete; fit_post accepts X,y,C only',
        'scipy':scipy.__version__,'numpy':np.__version__,'validation_source_count':len(sources),'test_named_paths':test_named,'html_paths':html_named,
        'ext15_reference_hashes':{'runner_sha256':ext15_manifest['runner_sha256'],'protocol_sha256':ext15_manifest['protocol_sha256'],
            'source_registry_sha256':ext15_manifest['source_registry_sha256']},
        'simulator_html':'not read, hashed, sourced, or used','fit_started':False,
        'runner_sha256':sha(Path(__file__)),'protocol_sha256':sha(PROTOCOL),'source_registry_sha256':sha(regpath),
        'smoke_command':r"& 'C:\Users\yungn\AppData\Local\Programs\Python\Python311\python.exe' ext16_focal_loss_mm_runner.py --smoke"}
    atomic_json(PRE/'frozen_manifest.json',frozen)
    smoke={'status':'passed','validation_predicate_integrity':'passed; only validation rows materialized','validation_datasets':validation_audit,
        'donor_audit':donor_audit,'schema':schema,'formula':'passed: [H3-B34,a,a*m,a*abs(m)] width 43',
        'synthetic_MM_fit':diag,'MM_reproducibility':'passed','incomplete_C_grid_no_subgrid_fallback':'passed',
        'MM_curvature_bound_and_hessian_majorization':{'curvature_bound':CURVATURE_BOUND,'max_abs_synthetic_curvature':max_abs_curvature,
            'minimum_eigenvalue_M_minus_H':min_majorizer_eig},
        'MM_step_checks':{'relative_linear_backward_error':backwardfd,'objective_before':f0fd,'objective_after':f1fd,
            'predicted_decrease':pred_dropfd,'descent_roundoff_guard':round_guardfd},
        'synthetic_probability_diagnostics':{'corrected_probability_Brier':synthetic_metrics['Brier'],
            'corrected_probability_NLL':synthetic_metrics['NLL'],'raw_focal_q_Brier':raw_q_brier,'raw_focal_q_NLL':raw_q_nll},
        'derivative_finite_difference':{'gradient_max_abs_error':grad_err,'hessian_max_abs_error':hess_err},
        'posterior_transform':{'tail_boundary_symmetry_monotonicity':'passed','direct_formula_max_abs_error':float(np.max(np.abs(p_stable-p_direct)))},
        'scipy_version':scipy.__version__,'grouped_fold_determinism_disjointness':'passed','P_pre_fit_signature_audit':'passed',
        'test_named_registry_entries':test_named,'html_registry_entries':html_named,'no_test_rows_labels_scores_predictions_read':True,
        'simulator_html_accessed':False,'runner_sha256':frozen['runner_sha256'],
        'protocol_sha256':frozen['protocol_sha256'],'source_registry_sha256':frozen['source_registry_sha256']}
    atomic_json(PRE/'smoke.json',smoke);return smoke

def assert_frozen_hashes():
    f=json.loads((PRE/'frozen_manifest.json').read_text(encoding='utf-8'));s=json.loads((PRE/'smoke.json').read_text(encoding='utf-8'));rpath=PRE/'source_registry.json'
    if f.get('fit_started') is not False:raise RuntimeError('preflight freeze must record fit_started=false')
    if scipy.__version__!=f.get('scipy') or scipy.__version__!=s.get('scipy_version'):
        raise RuntimeError(f'frozen SciPy version mismatch: current={scipy.__version__}, manifest={f.get("scipy")}')
    if f['runner_sha256']!=sha(Path(__file__)) or s['runner_sha256']!=sha(Path(__file__)):raise RuntimeError('runner hash changed after smoke')
    if f['protocol_sha256']!=sha(PROTOCOL) or s['protocol_sha256']!=sha(PROTOCOL):raise RuntimeError('protocol hash changed after smoke')
    if f['source_registry_sha256']!=sha(rpath) or s['source_registry_sha256']!=sha(rpath):raise RuntimeError('registry hash changed after smoke')
    reg=json.loads(rpath.read_text(encoding='utf-8'))
    registered_paths=[str(p).lower() for p in reg['sources']]
    if any(('test_' in p or '\\test\\' in p or '/test/' in p or '.html' in p) for p in registered_paths):
        raise RuntimeError('test-named or HTML source path in Ext16 registry')
    for path,info in reg['sources'].items():
        if not Path(path).is_file() or sha(path)!=info['sha256']:raise RuntimeError(f'source hash mismatch: {path}')
    return f

def run_full_validation():
    # The frozen hash guard is the first full-run operation, before any benchmark read or fit.
    frozen=assert_frozen_hashes()
    FULL.mkdir(parents=True,exist_ok=True)
    atomic_json(FULL/'run_state.json',{'state':'hashes_verified_fitting_started','fit_started':True,
        'runner_sha256':frozen['runner_sha256'],'protocol_sha256':frozen['protocol_sha256'],
        'source_registry_sha256':frozen['source_registry_sha256']})
    meta=ext5.load_inputs();donor_audit,_=ext3.verify_donors(meta)
    data_by={ds:ext5.build_sources(meta,ds) for ds in ('devign','reveal')}

    # Phase 1 is P_pre-free: select on AP-only grouped OOF and make all P_post heldout scores.
    candidate={}
    for ds in ('devign','reveal'):
        d=data_by[ds];y=d['y'];g=d['g'];ids=d['ids'];arms=d['arms'];outer=group_folds(y,g,BASE+8100);n=len(y)
        if set(arms)!=set(ARMS) or len(arms)!=15:raise ValueError(f'{ds}: raw arm set mismatch')
        post=np.full(n,np.nan);postscore=np.full(n,np.nan);postq=np.full(n,np.nan);posteta=np.full(n,np.nan);folds=[]
        for oi,(T,H) in enumerate(outer):
            seed=BASE+100000+1000*oi
            selected=select_c(d,T,seed)
            row={'outer_fold':oi,'outer_train_n':len(T),'heldout_n':len(H),'inner_seed':seed,
                'selection':{k:v for k,v in selected.items() if k!='oof_score'}}
            if not selected['complete'] or selected['C'] is None:
                row['status']='incomplete_required_C_grid' if not selected['complete'] else 'no_AP_feasible_C';folds.append(row);continue
            try:
                model,diag=fit_post(feature_matrix(d,T),y[T],selected['C'])
                if not diag['usable']:raise RuntimeError('outer focal fit did not meet locked usability criteria')
                qh,ph,score,eta=predict_post(model,feature_matrix(d,H))
                post[H]=ph;postscore[H]=score;postq[H]=qh;posteta[H]=eta
                row.update({'status':'complete','selected_C':float(selected['C']),'fit':diag})
            except Exception as exc:
                row.update({'status':'outer_focal_fit_failure','error':type(exc).__name__+': '+str(exc)})
            folds.append(row)
        complete=bool(len(folds)==3 and all(f['status']=='complete' for f in folds) and np.isfinite(post).all() and np.isfinite(postscore).all() and np.isfinite(postq).all() and np.isfinite(posteta).all())
        if not complete:post[:]=np.nan;postscore[:]=np.nan;postq[:]=np.nan;posteta[:]=np.nan
        candidate[ds]={'n':n,'groups':int(pd.Series(g).nunique()),'outer':outer,'post':post,
            'postscore':postscore,'postq':postq,'posteta':posteta,'folds':folds,'nested_complete':complete}

    # Only after all AP-only selectors and P_post heldout predictions finish do we
    # load/finalize FrozenPre, thresholds, and prior P_pre validation artifacts.
    p3=pd.read_csv(EXT03/'outer_predictions.csv',low_memory=False);r3=json.loads((EXT03/'results.json').read_text(encoding='utf-8'))
    p4=pd.read_csv(EXT04/'outer_predictions.csv',low_memory=False);r4=json.loads((EXT04/'results.json').read_text(encoding='utf-8'))
    pre_audit={}
    for ds in ('devign','reveal'):
        d=data_by[ds];y=d['y'];g=d['g'];ids=d['ids'];info=candidate[ds];outer=info['outer']
        old=p3[(p3.dataset==ds)&(p3.model=='P_pre')].set_index('id').reindex(ids)
        old4=p4[(p4.dataset==ds)&(p4.model=='P_pre')].set_index('id').reindex(ids)
        for name,q in [('Ext03',old),('Ext04',old4)]:
            if q.prediction.isna().any() or not np.array_equal(q.target_label.to_numpy(int),y) or not np.array_equal(q.group_id.astype(str).to_numpy(),g):
                raise ValueError(f'{ds}: {name} FrozenPre ID/label/group mismatch')
        pre=np.full(len(y),np.nan);tau=np.full(len(y),np.nan);diff3=[];diff4=[]
        for oi,(T,H) in enumerate(outer):
            seed=BASE+100000+1000*oi;fp=frozen_pre(d,T,seed);pp=fp['model'].predict_proba(d['x'][H])[:,1]
            rec3=r3['datasets'][ds]['outer_folds'][oi];rec4=r4['datasets'][ds]['outer_folds'][oi]
            if abs(float(fp['C'])-float(rec3['P_pre_C_outer_train']))>1e-12 or abs(float(fp['tau'])-float(rec3['tau_T']))>1e-12:
                raise ValueError(f'{ds} outer {oi}: Ext03 FrozenPre C/tau parity failure')
            if abs(float(fp['C'])-float(rec4['P_pre_C']))>1e-12 or abs(float(fp['tau'])-float(rec4['P_pre_tau']))>1e-12:
                raise ValueError(f'{ds} outer {oi}: Ext04 FrozenPre C/tau parity failure')
            for name,q in [('Ext03',old.iloc[H]),('Ext04',old4.iloc[H])]:
                if not np.array_equal(q.outer_fold.to_numpy(int),np.full(len(H),oi)):
                    raise ValueError(f'{ds} outer {oi}: {name} outer-fold assignment mismatch')
            d3=float(np.max(np.abs(pp-old.iloc[H].prediction.to_numpy(float))))
            d4=float(np.max(np.abs(pp-old4.iloc[H].prediction.to_numpy(float))))
            if max(d3,d4)>1e-12:raise ValueError(f'{ds} outer {oi}: FrozenPre heldout probability parity failure')
            pre[H]=pp;tau[H]=fp['tau'];diff3.append(d3);diff4.append(d4)
            info['folds'][oi].update({'FrozenPre_seed':seed,'FrozenPre_C':float(fp['C']),'FrozenPre_tau':float(fp['tau']),
                'P_pre_Ext03_max_abs_diff':d3,'P_pre_Ext04_max_abs_diff':d4})
        info['pre']=pre;info['tau']=tau
        pre_audit[ds]={'max_abs_Ext03_probability_diff':max(diff3),'max_abs_Ext04_probability_diff':max(diff4),
            'outer_seed_by_fold':[BASE+100000+1000*o for o in range(3)],'outer_folds':3,
            'P_pre_started_after_P_post_selection_and_heldout_predictions':True}

    predictions=[];datasets={};pvalues=[];pkeys=[]
    for di,ds in enumerate(('devign','reveal')):
        d=data_by[ds];y=d['y'];g=d['g'];info=candidate[ds];pre=info['pre'];tau=info['tau'];post=info['post'];score=info['postscore'];rawq=info['postq'];raweta=info['posteta'];arms=d['arms'];outer=info['outer'];complete=info['nested_complete']
        models={'P_pre':(pre,pre)}
        if complete:models['P_post']=(post,score)
        models.update({f'arm_{a}':(v,v) for a,v in arms.items()})
        metrics={k:metric(y,*v,tau) for k,v in models.items()}
        if complete:
            metrics['P_post']['raw_focal_q_diagnostic']={'Brier':float(np.mean((rawq-y)**2)),
                'NLL':float(np.mean(np.logaddexp(0.0,raweta)-y*raweta)),
                'endpoint_rate':float(np.mean((rawq==0)|(rawq==1))),
                'tie_count':int(len(rawq)-len(np.unique(rawq)))}
        if complete:
            boot=bootstrap(y,g,tau,pre,post,score,arms,di,draw_count=5000)
            for a,res in boot['comparisons'].items():pvalues.append(res['AP_p_raw']);pkeys.append((ds,a))
            predpre=pre>=tau;predpost=post>=tau;truth=y.astype(bool)
            repair={'repairs':int(np.sum((predpre!=truth)&(predpost==truth))),
                'harms':int(np.sum((predpre==truth)&(predpost!=truth))),
                'P_pre_errors':int(np.sum(predpre!=truth)),'P_post_errors':int(np.sum(predpost!=truth))}
        else:
            boot={'unavailable':'incomplete nested P_post; all 30 AP/Holm comparisons unavailable','planned_draws':5000}
            repair={}
        for name,(prob,ap_score) in models.items():
            for oi,(_,H) in enumerate(outer):
                frame=d['meta'].iloc[H][['id','group_id','target_label']].copy()
                frame['dataset']=ds;frame['model']=name;frame['prediction']=prob[H];frame['ap_score']=ap_score[H]
                if name=='P_post':
                    frame['raw_focal_q']=rawq[H];frame['raw_focal_eta']=raweta[H]
                frame['threshold']=tau[H];frame['outer_fold']=oi;predictions.append(frame)
        datasets[ds]={'n':info['n'],'groups':info['groups'],'nested_complete':complete,'metrics':metrics,
            'primary_bootstrap':boot,'repair_harm_shared_threshold':repair,'outer_folds':info['folds'],
            'arm_count_unique':len(arms),'B2-rep':'duplicate of B2; verified by validation loader and excluded'}

    nested_all=all(v['nested_complete'] for v in datasets.values())
    if nested_all:
        if len(pvalues)!=30:raise AssertionError('Ext16 planned AP/Holm family must be exactly 30')
        adj=holm(pvalues)
        for (ds,a),p,pa in zip(pkeys,pvalues,adj):
            comp=datasets[ds]['primary_bootstrap']['comparisons'][a];comp['AP_p_Holm']=float(pa)
            comp['AP_p_Holm_report']='<1/5000' if pa==0 else float(pa)
            comp['AP_p_raw_report']='<1/5000' if p==0 else float(p)
    else:
        for record in datasets.values():
            for comp in record['primary_bootstrap'].get('comparisons',{}).values():
                comp['AP_p_Holm']=None;comp['AP_family_status']='unavailable; planned 30-comparison family incomplete'
    for ds,record in datasets.items():
        if not record['nested_complete']:
            record['objective_gates']={'MCC_P_post_minus_P_pre':{'status':'unavailable'},'AP_all_15_arms':{'status':'unavailable'},'overall':'unavailable'};continue
        ci=record['primary_bootstrap']['MCC_P_post_minus_P_pre_CI95']
        mcc='pass' if ci[0]>.02 else ('fail' if ci[1]<=.02 else 'inconclusive')
        comps=record['primary_bootstrap']['comparisons']
        for c in comps.values():c['AP_gate_pass']=bool(nested_all and c['AP_CI95'][0]>0 and c.get('AP_p_Holm') is not None and c['AP_p_Holm']<.05)
        n_pass=sum(c['AP_gate_pass'] for c in comps.values())
        ap=('pass' if len(comps)==15 and n_pass==15 else 'fail') if nested_all else 'unavailable'
        overall=('fail' if mcc=='fail' or ap=='fail' else ('inconclusive' if mcc=='inconclusive' else 'pass')) if nested_all else 'unavailable'
        record['objective_gates']={'MCC_P_post_minus_P_pre':{'status':mcc,'criterion':'95% paired group-bootstrap CI lower endpoint > +0.02','CI95':ci},
            'AP_all_15_arms':{'status':ap,'comparisons_passed':n_pass,'comparisons_planned':15,'criterion':'each AP CI lower > 0 and Holm p < .05',
                'reason':None if nested_all else 'full 30-comparison family unavailable because nested predictions are incomplete'},'overall':overall}
    if not nested_all:overall_status='unavailable'
    elif any(d['objective_gates']['overall']=='fail' for d in datasets.values()):overall_status='fail'
    elif any(d['objective_gates']['overall']=='inconclusive' for d in datasets.values()):overall_status='inconclusive'
    else:overall_status='pass'

    predpath=FULL/'outer_predictions.csv';pd.concat(predictions,ignore_index=True).to_csv(predpath,index=False)
    results={'run_completion':'completed','nested_predictions_complete_all_datasets':nested_all,'objective_gate_overall':overall_status,
        'datasets':datasets,'planned_AP_Holm_family_size':30,'actual_AP_Holm_family_size':30 if nested_all else 0,
        'candidate':'Ext16 fixed-curvature MM solver for Ext15 gamma-2 focal estimator','validation_only':True,
        'test_labels_scores_predictions_read':False,'P_pre_read_after_P_post_selection_and_predictions':True}
    atomic_json(FULL/'results.json',results);atomic_json(FULL/'pre_p_pre_audit.json',pre_audit)
    report=['# Ext16 validation report','',f"Nested predictions complete: `{nested_all}`; overall objective gate: **{overall_status}**. This is an exploratory solver variation, not confirmatory.",'']
    for ds,d in datasets.items():
        report += [f"## {ds}",f"Nested complete: `{d['nested_complete']}`; dataset gate: **{d['objective_gates']['overall']}**."]
        if d['nested_complete']:
            b=d['primary_bootstrap'];report += [f"P_post AP (corrected logit): {d['metrics']['P_post']['AP']:.6f}; P_pre AP: {d['metrics']['P_pre']['AP']:.6f}; P_post/P_pre corrected-probability Brier: {d['metrics']['P_post']['Brier']:.6f}/{d['metrics']['P_pre']['Brier']:.6f}; NLL: {d['metrics']['P_post']['NLL']:.6f}/{d['metrics']['P_pre']['NLL']:.6f}; P_post MCC: {d['metrics']['P_post']['MCC']:.6f}.",
                f"Raw focal q diagnostic: Brier={d['metrics']['P_post']['raw_focal_q_diagnostic']['Brier']:.6f}; NLL={d['metrics']['P_post']['raw_focal_q_diagnostic']['NLL']:.6f}; endpoints={d['metrics']['P_post']['raw_focal_q_diagnostic']['endpoint_rate']:.6f}; ties={d['metrics']['P_post']['raw_focal_q_diagnostic']['tie_count']}.",
                f"Delta MCC(P_post-P_pre): {b['delta_MCC_P_post_minus_P_pre']:+.6f}, 95% CI {b['MCC_P_post_minus_P_pre_CI95']}; gate: {d['objective_gates']['MCC_P_post_minus_P_pre']['status']} (lower endpoint > +0.02).",
                f"AP comparisons passing CI-lower>0 and Holm p<.05: {d['objective_gates']['AP_all_15_arms']['comparisons_passed']}/15; Holm family size 30.",
                f"Shared-threshold repairs={d['repair_harm_shared_threshold']['repairs']}; harms={d['repair_harm_shared_threshold']['harms']}; bootstrap draws={b['valid_draws']}/{b['attempted_draws']}."]
        else:report.append('Nested P_post incomplete; no effect-size verdict and full 30-comparison AP/Holm family unavailable.')
        for f in d['outer_folds']:
            report.append(f"Outer fold {f['outer_fold']} status={f['status']}; selected C={f.get('selected_C')}; AP feasibility={f['selection'].get('C_diagnostics')}; fit={f.get('fit')}.")
    (FULL/'report.md').write_text('\n'.join(report)+'\n',encoding='utf-8')
    manifest={'registered':False,'post_cap_extension':True,'validation_only':True,'candidate':'Ext16 fixed-curvature MM solver variation for Ext15 focal estimator',
        'historical_hypothesis_count':'at least 41 after this candidate','runner_sha256':sha(Path(__file__)),'protocol_sha256':sha(PROTOCOL),
        'source_registry_sha256':sha(PRE/'source_registry.json'),'validation_rows_only':True,'test_labels_scores_predictions_read':False,
        'fit_started':True,'run_completion':'completed','nested_predictions_complete_all_datasets':nested_all,
        'objective_gate_overall':overall_status,'scipy':scipy.__version__,'numpy':np.__version__,'gamma':GAMMA,'C_grid':list(CS),
        'solver':'fixed global-curvature MM, zero start, one Cholesky factor per fit','objective_guard_rel':OBJECTIVE_GUARD_REL,
        'MM_max_updates':MM_MAX_UPDATES,'MM_grad_l2_tol':MM_GRAD_L2_TOL,'MM_grad_inf_tol':MM_GRAD_INF_TOL,
        'MM_linear_backward_tol':MM_LINEAR_BACKWARD_TOL,'MM_descent_guard_ulps':MM_DESCENT_ULPS,
        'curvature_bound':CURVATURE_BOUND,'majorizer_coefficient':2.0,
        'p_pre_independence':'Ext03/04 artifact bytes are hash-verified before fitting; P_pre records/values are parsed and used only in evaluator parity after all AP-only selection and P_post outer predictions; no P_pre argument in fit_post',
        'test_boundary':'No test rows, labels, scores, or predictions read; simulator HTML not accessed.',
        'nested_complete':{ds:v['nested_complete'] for ds,v in datasets.items()},'planned_AP_Holm_family_size':30,'actual_AP_Holm_family_size':30 if nested_all else 0}
    atomic_json(FULL/'manifest.json',manifest)
    artifacts={name:sha(FULL/name) for name in ('outer_predictions.csv','results.json','report.md','pre_p_pre_audit.json','manifest.json')}
    artifacts.update({'runner_sha256':sha(Path(__file__)),'protocol_sha256':sha(PROTOCOL),'source_registry_sha256':sha(PRE/'source_registry.json')})
    artifactpath=FULL/'artifact_hashes.json';atomic_json(artifactpath,artifacts)
    atomic_json(FULL/'run_state.json',{'state':'completed','exit_status':0,'nested_complete':{ds:v['nested_complete'] for ds,v in datasets.items()},
        'objective_gate_overall':overall_status,'artifact_hashes_sha256':sha(artifactpath)})

if __name__=='__main__':
    if '--smoke' in sys.argv: print(json.dumps(preflight_smoke(),indent=2))
    elif '--assert-hashes' in sys.argv: print(json.dumps(assert_frozen_hashes(),indent=2))
    elif '--run-full-validation' in sys.argv: run_full_validation()
    else: raise SystemExit('Choose --smoke, --assert-hashes, or the explicitly authorized --run-full-validation flag.')
