"""Ext20 context-interaction logistic stack, preflight plus explicitly gated validation run."""
from __future__ import annotations
import hashlib, inspect, json, sys
from pathlib import Path

import numpy as np
import pandas as pd
import scipy, sklearn
from scipy.linalg import cho_factor, cho_solve
from scipy.special import expit
from sklearn.preprocessing import StandardScaler

import ext05_runner as ext5
import ext16_focal_loss_mm_runner as ext16
ext3=ext5.ext3
HOME=Path(__file__).resolve().parent
OUT=HOME/"runs/independent-post-ext20-context-interaction-validation/attempt-1"
PRE=OUT/"preflight";FULL=OUT/"full"
PROTOCOL=HOME/"ext20_context_interaction_protocol_vi.md"
EXT18_PRE=HOME/"runs/independent-post-ext18-constrained-logistic-stack-validation/attempt-1/preflight"
EXT19_PRE=HOME/"runs/independent-post-ext19-partial-gam-validation/attempt-1/preflight"
EXT03=HOME/"runs/independent-post-ext03-multisignal-validation/full";EXT03_PRE=HOME/"runs/independent-post-ext03-multisignal-validation/preflight"
EXT04=HOME/"runs/independent-post-ext04-decision-aware-validation/full";EXT04_PRE=HOME/"runs/independent-post-ext04-decision-aware-validation/preflight"
BASE=20261123;CS=(.001,.01,.05,.1,1.0)
BASE_WIDTH,FAMILY_WIDTH,SIGNAL_WIDTH=34,11,3;RAW_WIDTH=48;DESIGN_WIDTH=150;SIGNAL_EPS=1e-6;INTERACTION_PENALTY=10.0
SINGLETONS=("B0","B1","B1-full","B1-H2","B2","B2-flip","B2-labelonly","B2-nolabel","B3")
ARMS=tuple(ext5.ARMS)
MM_MAX=100000;GRAD_L2_TOL=1e-8;GRAD_INF_TOL=1e-6;BACKWARD_TOL=1e-12;DESCENT_ULPS=64;OBJ_GUARD_REL=1e-10
SIGNAL_NAMES=("B2_logodds","B2_minus_flip_logodds","B2_minus_nolabel_logodds")

def sha(path):
 h=hashlib.sha256()
 with open(path,"rb") as f:
  for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
 return h.hexdigest()
def atomic_json(path,obj):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix(path.suffix+".tmp")
 tmp.write_text(json.dumps(obj,indent=2,allow_nan=False),encoding="utf-8");tmp.replace(path)

def feature_matrix(data,rows):
 rows=np.asarray(rows,dtype=int);x=np.asarray(data["x"][rows],dtype=np.float64);P=data["arms"]
 if x.ndim!=2 or x.shape[1]!=34 or data["names"][5]!="p_gate":raise ValueError("H3-B schema/p_gate mismatch")
 required=set(SINGLETONS)|{f"B1-shuf-{s}" for s in (42,43,44)}|{f"B2-rand-{s}" for s in (42,43,44)}
 if set(P)!=set(ARMS) or not required.issubset(P):raise ValueError("15 raw arm roster mismatch")
 cols=[np.asarray(P[a][rows],float) for a in SINGLETONS]
 cols += [np.mean(np.column_stack([P[f"B1-shuf-{s}"][rows] for s in (42,43,44)]),axis=1),
          np.mean(np.column_stack([P[f"B2-rand-{s}"][rows] for s in (42,43,44)]),axis=1)]
 family=np.column_stack(cols)
 def logit_score(p):
  q=np.clip(np.asarray(p,dtype=np.float64),SIGNAL_EPS,1.-SIGNAL_EPS)
  return np.log(q)-np.log1p(-q)
 b2=logit_score(P["B2"][rows])
 signals=np.column_stack([b2,b2-logit_score(P["B2-flip"][rows]),b2-logit_score(P["B2-nolabel"][rows])])
 z=np.column_stack([x,family,signals])
 if family.shape!=(len(rows),FAMILY_WIDTH) or not np.isfinite(family).all() or np.any((family<0)|(family>1)):
  raise ValueError("bounded LLM family-score assertion failed")
 if signals.shape!=(len(rows),SIGNAL_WIDTH) or not np.isfinite(signals).all() or z.shape!=(len(rows),RAW_WIDTH):
  raise ValueError("Ext20 raw feature schema/nonfinite signal assertion failed")
 return z

def prepare_partition(X):
 X=np.asarray(X,dtype=np.float64)
 if X.ndim!=2 or X.shape[1]!=RAW_WIDTH or not np.isfinite(X).all():raise ValueError("invalid raw training matrix")
 h3_scaler=StandardScaler().fit(X[:,:BASE_WIDTH])
 family_scaler=StandardScaler().fit(X[:,BASE_WIDTH:BASE_WIDTH+FAMILY_WIDTH])
 signal_scaler=StandardScaler().fit(X[:,BASE_WIDTH+FAMILY_WIDTH:])
 xh=np.asarray(h3_scaler.transform(X[:,:BASE_WIDTH]),dtype=np.float64)
 xf=np.asarray(family_scaler.transform(X[:,BASE_WIDTH:BASE_WIDTH+FAMILY_WIDTH]),dtype=np.float64)
 xs=np.asarray(signal_scaler.transform(X[:,BASE_WIDTH+FAMILY_WIDTH:]),dtype=np.float64)
 interaction_raw=np.einsum("ni,nj->nij",xh,xs).reshape(len(X),BASE_WIDTH*SIGNAL_WIDTH)
 interaction_mean=interaction_raw.mean(axis=0)
 interaction_scale=interaction_raw.std(axis=0)
 if not np.isfinite(interaction_raw).all() or not np.isfinite(interaction_mean).all() or not np.isfinite(interaction_scale).all():
  raise FloatingPointError("nonfinite interaction block")
 interaction_scale=np.where(interaction_scale>1e-12,interaction_scale,1.0)
 interactions=(interaction_raw-interaction_mean)/interaction_scale
 design=np.column_stack([xh,xf,xs,interactions])
 if design.shape!=(len(X),DESIGN_WIDTH) or not np.isfinite(design).all():
  raise FloatingPointError("Ext20 design schema/finiteness failure")
 main_width=BASE_WIDTH+FAMILY_WIDTH+SIGNAL_WIDTH
 penalty=np.diag(np.r_[np.ones(main_width),np.full(BASE_WIDTH*SIGNAL_WIDTH,INTERACTION_PENALTY)])
 if penalty.shape!=(DESIGN_WIDTH,DESIGN_WIDTH):raise AssertionError("interaction penalty layout mismatch")
 return {"h3_scaler":h3_scaler,"family_scaler":family_scaler,"signal_scaler":signal_scaler,
         "interaction_mean":interaction_mean,"interaction_scale":interaction_scale,
         "train_design":design,"penalty":penalty,"n":len(X),"width":int(design.shape[1]),
         "interaction_width":BASE_WIDTH*SIGNAL_WIDTH,"interaction_penalty":INTERACTION_PENALTY,
         "main_width":main_width}

def transform_partition(X,prep):
 X=np.asarray(X,dtype=np.float64)
 if X.ndim!=2 or X.shape[1]!=RAW_WIDTH or not np.isfinite(X).all():raise ValueError("invalid transform matrix")
 xh=np.asarray(prep["h3_scaler"].transform(X[:,:BASE_WIDTH]),dtype=np.float64)
 f0=BASE_WIDTH;f1=f0+FAMILY_WIDTH
 xf=np.asarray(prep["family_scaler"].transform(X[:,f0:f1]),dtype=np.float64)
 xs=np.asarray(prep["signal_scaler"].transform(X[:,f1:]),dtype=np.float64)
 interaction_raw=np.einsum("ni,nj->nij",xh,xs).reshape(len(X),BASE_WIDTH*SIGNAL_WIDTH)
 interactions=(interaction_raw-prep["interaction_mean"])/prep["interaction_scale"]
 out=np.column_stack([xh,xf,xs,interactions])
 if out.shape[1]!=prep["width"] or not np.isfinite(out).all():raise FloatingPointError("heldout interaction design mismatch")
 return out

def objective_grad_hess(theta,U,y,C,penalty):
 theta=np.asarray(theta,float);U=np.asarray(U,float);y=np.asarray(y,float)
 eta=U@theta;p=expit(eta);slopes=theta[1:]
 value=float(np.sum(np.logaddexp(0.,eta)-y*eta)+.5*(slopes@penalty@slopes)/C)
 grad=U.T@(p-y);grad[1:]+=penalty@slopes/C
 hess=U.T@((p*(1-p))[:,None]*U);hess[1:,1:]+=penalty/C
 if not np.isfinite(value) or not np.isfinite(grad).all() or not np.isfinite(hess).all():raise FloatingPointError("nonfinite objective/derivatives")
 return value,grad,hess
def value_grad(theta,U,y,C,penalty):
 eta=U@theta;p=expit(eta);slopes=theta[1:]
 value=float(np.sum(np.logaddexp(0.,eta)-y*eta)+.5*(slopes@penalty@slopes)/C)
 grad=U.T@(p-y);grad[1:]+=penalty@slopes/C
 if not np.isfinite(value) or not np.isfinite(grad).all():raise FloatingPointError("nonfinite objective/gradient")
 return value,grad

def fit_post(X,y,C,prepared=None):
 """Fit accepts X/y/C and optional current-fold transform only; no P_pre/tau."""
 X=np.asarray(X,dtype=np.float64);y=np.asarray(y,dtype=np.int8);C=float(C)
 if X.ndim!=2 or X.shape[1]!=RAW_WIDTH or len(X)!=len(y) or not np.isfinite(X).all() or set(np.unique(y))!={0,1} or C<=0:
  raise ValueError("invalid fit inputs; both classes required")
 if prepared is None:prepared=prepare_partition(X)
 if prepared["n"]!=len(X):raise ValueError("prepared transform partition-size mismatch")
 design=prepared["train_design"];U=np.column_stack([np.ones(len(design)),design]);P=prepared["penalty"]
 R=np.zeros((U.shape[1],U.shape[1]));R[1:,1:]=P/C
 M=.25*(U.T@U)+R;fac=cho_factor(M,lower=True,check_finite=True)
 theta=np.zeros(U.shape[1],dtype=np.float64);f0,_=value_grad(theta,U,y,C,P);current=f0
 iterations=0;failure=None;maxback=0.;maxincrease=0.;maxmajor=0.;gL=gI=np.inf
 while iterations<MM_MAX:
  current,g=value_grad(theta,U,y,C,P);gL=float(np.linalg.norm(g,2));gI=float(np.linalg.norm(g,np.inf))
  if gL<=GRAD_L2_TOL:break
  d=cho_solve(fac,-g,check_finite=True);res=M@d+g
  den=float(np.linalg.norm(M,np.inf)*np.linalg.norm(d,np.inf)+np.linalg.norm(g,np.inf));back=float(np.linalg.norm(res,np.inf)/den) if den else 0.
  maxback=max(maxback,back)
  if not np.isfinite(d).all() or not np.isfinite(back) or back>BACKWARD_TOL:failure="majorizer_solve_residual_failure";break
  new=theta+d
  if np.array_equal(new,theta):failure="unchanged_update_before_convergence";break
  fn,gn=value_grad(new,U,y,C,P);step=new-theta;quad=float(g@step+.5*step@M@step)
  guard=DESCENT_ULPS*np.finfo(float).eps*max(1.,abs(current),abs(fn));inc=float(fn-current)
  maxincrease=max(maxincrease,inc);maxmajor=max(maxmajor,quad)
  if not np.isfinite(new).all() or not np.isfinite(fn) or not np.isfinite(gn).all():failure="nonfinite_MM_update";break
  if inc>guard:failure="objective_increased_beyond_guard";break
  if quad>guard:failure="majorizer_quadratic_not_decreased";break
  theta=new;current=fn;iterations+=1;gL=float(np.linalg.norm(gn,2));gI=float(np.linalg.norm(gn,np.inf))
  if gL<=GRAD_L2_TOL:break
 converged=bool(gL<=GRAD_L2_TOL and iterations<MM_MAX and failure is None)
 final,grad=value_grad(theta,U,y,C,P);gL=float(np.linalg.norm(grad,2));gI=float(np.linalg.norm(grad,np.inf))
 finite=bool(np.isfinite(theta).all() and np.isfinite(final) and np.isfinite(grad).all())
 objguard=OBJ_GUARD_REL*max(1.,abs(f0));no_worse=bool(finite and final<=f0+objguard)
 usable=bool(converged and finite and gL<=GRAD_L2_TOL and gI<=GRAD_INF_TOL and no_worse)
 model={"prepared":prepared,"theta":theta,"width":prepared["width"],"usable":usable}
 diag={"usable":usable,"C":C,"n":len(y),"design_width":prepared["width"],
    "interaction_width":prepared["interaction_width"],"interaction_penalty":prepared["interaction_penalty"],"iterations":iterations,"converged_before_cap":converged,"failure":failure,
   "initial_objective":float(f0),"final_objective":float(final),"objective_guard":objguard,"objective_no_worse_than_zero":no_worse,
   "gradient_l2":gL,"gradient_inf":gI,"gradient_l2_tolerance":GRAD_L2_TOL,"gradient_inf_tolerance":GRAD_INF_TOL,
   "max_linear_backward_error":maxback,"backward_error_tolerance":BACKWARD_TOL,"max_objective_increase":maxincrease,
   "max_quadratic_majorizer_change":maxmajor,"finite_state":finite}
 return model,diag

def predict_post(model,X):
 if not model["usable"]:raise RuntimeError("unusable Ext20 fit")
 Z=transform_partition(X,model["prepared"])
 eta=np.column_stack([np.ones(len(Z)),Z])@model["theta"];p=expit(eta)
 if not np.isfinite(eta).all() or not np.isfinite(p).all():raise FloatingPointError("nonfinite heldout score")
 return eta,p

def group_folds(y,g,seed):return ext5.group_folds(np.asarray(y),np.asarray(g).astype(str),int(seed))
def select_c(data,Q,oi):
 Q=np.asarray(Q,int);y=data["y"];g=data["g"];yy=y[Q];seed=BASE+100000+1000*int(oi)
 folds=group_folds(yy,g[Q],seed);oof={float(c):np.full(len(Q),np.nan) for c in CS};solver={float(c):[] for c in CS};fr=[]
 for k,(tr,va) in enumerate(folds):
  A,B=Q[tr],Q[va];X=feature_matrix(data,A);XV=feature_matrix(data,B)
  try:prep=prepare_partition(X);prep_error=None
  except Exception as e:prep=None;prep_error=type(e).__name__+":"+str(e)
  row={"inner_fold":k,"train_n":len(A),"heldout_n":len(B),"preprocessing_failure":prep_error}
  for c in CS:
   try:
    if prep is None:raise RuntimeError(prep_error)
    model,diag=fit_post(X,y[A],float(c),prep)
    if not diag["usable"]:solver[float(c)].append({"usable":False,**diag});row[str(c)]={"status":"solver_not_usable","diag":diag};continue
    eta,p=predict_post(model,XV);oof[float(c)][va]=eta;solver[float(c)].append({"usable":True,**diag});row[str(c)]={"status":"complete","iterations":diag["iterations"]}
   except Exception as e:solver[float(c)].append({"usable":False,"failure":type(e).__name__+":"+str(e)});row[str(c)]={"status":"fit_failure","error":type(e).__name__+":"+str(e)}
  fr.append(row)
 arm_ap={a:float(ext16.average_precision_score(yy,p[Q])) for a,p in data["arms"].items()};ds=[]
 for c in CS:
  complete=bool(np.isfinite(oof[float(c)]).all() and len(solver[float(c)])==3 and all(z.get("usable",False) for z in solver[float(c)]))
  ap=float(ext16.average_precision_score(yy,oof[float(c)])) if complete else None;feas=bool(complete and all(ap>v for v in arm_ap.values()))
  ds.append({"C":float(c),"complete":complete,"AP":ap,"AP_feasible_vs_all_15":feas,"solver_by_fold":solver[float(c)]})
 grid=all(z["complete"] for z in ds);ok=[z for z in ds if z["complete"] and z["AP_feasible_vs_all_15"]]
 chosen=max(ok,key=lambda z:(z["AP"],-z["C"]))["C"] if grid and ok else None
 return {"C":chosen,"complete":grid,"reason":"selected" if chosen is not None else ("incomplete_required_C_grid" if not grid else "no_AP_feasible_C"),"inner_seed":seed,"folds":fr,"C_diagnostics":ds,"arm_AP":arm_ap,"oof_score":None if chosen is None else oof[float(chosen)]}

def synthetic_preflight():
 rng=np.random.default_rng(20261125);n=112;x=rng.normal(size=(n,34));x[:,5]=rng.uniform(.03,.97,n)
 arms={a:rng.uniform(.02,.98,n) for a in ARMS}
 arms["B0"][:]=.5;arms["B1"][:]=np.tile([0.,1.],n//2)
 arms["B2"][:4]=[0.,1.,0.,1.];arms["B2-flip"][:4]=[1.,0.,1.,0.]
 arms["B2-nolabel"][:4]=[.25,.75,.25,.75]
 names=[f"h3_{j}" for j in range(34)];names[5]="p_gate"
 raw=feature_matrix({"x":x,"names":names,"arms":arms},np.arange(n))
 train=raw[:80];held=raw[80:];prep=prepare_partition(train)
 Z=prep["train_design"];Zv=transform_partition(held,prep)
 if Z.shape!=(80,DESIGN_WIDTH) or Zv.shape!=(len(held),DESIGN_WIDTH) or not np.isfinite(Zv).all():
  raise AssertionError("interaction transform dimensions/finiteness")
 if prep["interaction_width"]!=102 or prep["main_width"]!=48:
  raise AssertionError("context interaction block width mismatch")
 if np.max(np.abs(prep["h3_scaler"].mean_-train[:,:34].mean(axis=0)))>1e-12:
  raise AssertionError("H3 scaler was not training-local")
 if np.max(np.abs(prep["signal_scaler"].mean_-train[:,45:48].mean(axis=0)))>1e-12:
  raise AssertionError("signal scaler was not training-local")
 changed=held.copy();changed[:,5]=1000.;changed[:,45:]=500.
 Zv_extreme=transform_partition(changed,prep)
 if not np.isfinite(Zv_extreme).all():raise AssertionError("heldout transform altered/faulted frozen training transforms")
 y=np.tile([0,1],40).astype(np.int8);U=np.column_stack([np.ones(80),Z]);theta=rng.normal(size=U.shape[1])*.002;C=.1
 f,g,h=objective_grad_hess(theta,U,y,C,prep["penalty"]);eps=1e-5;gn=np.zeros_like(g);hn=np.zeros_like(h)
 for j in range(len(theta)):
  e=np.zeros_like(theta);e[j]=eps
  fp,gp,_=objective_grad_hess(theta+e,U,y,C,prep["penalty"])
  fm,gm,_=objective_grad_hess(theta-e,U,y,C,prep["penalty"])
  gn[j]=(fp-fm)/(2*eps);hn[:,j]=(gp-gm)/(2*eps)
 ge=float(np.max(np.abs(g-gn)));he=float(np.max(np.abs(h-hn)))
 if ge>5e-7 or he>5e-7:raise AssertionError("interaction objective derivative FD failed")
 M=.25*(U.T@U);M[1:,1:]+=prep["penalty"]/C
 if np.linalg.eigvalsh(M-h).min() < -1e-8*max(1.,np.linalg.norm(M,2)):
  raise AssertionError("MM Hessian majorization failed")
 yfit=(rng.random(80)<expit(np.clip(Z[:,:3]@np.array([.3,-.2,.1]),-8,8))).astype(np.int8)
 if len(np.unique(yfit))<2:yfit[:2]=[0,1]
 model,d=fit_post(train,yfit,.1,prep);model2,d2=fit_post(train,yfit,.1,prep)
 eta,p=predict_post(model,held);eta2,p2=predict_post(model2,held)
 if not d["usable"] or not d2["usable"] or not np.array_equal(model["theta"],model2["theta"]) or not np.array_equal(eta,eta2):
  raise AssertionError(f"synthetic context-interaction MM unusable: {d}")
 groups=np.repeat(np.arange(40),2);labels=np.tile([0,1],40);folds=group_folds(labels,groups,BASE+8100)
 if len(folds)!=3 or any(set(groups[a])&set(groups[b]) for a,b in folds):
  raise AssertionError("group folds overlap")
 sig=set(inspect.signature(fit_post).parameters)
 if sig&{"pre","p_pre","tau","threshold","frozenpre"}:raise AssertionError("P_pre/tau signature violation")
 return {"raw_feature_width":RAW_WIDTH,"design_width":DESIGN_WIDTH,"main_effect_width":48,
  "interaction_width":102,"interaction_penalty_multiplier":INTERACTION_PENALTY,
  "finite_logit_at_probability_0_or_1":"passed","train_only_scalers_and_interaction_center_scale":"passed",
  "heldout_transform":"passed","gradient_fd_max_abs":ge,"hessian_fd_max_abs":he,
  "MM_majorization_min_eig":float(np.linalg.eigvalsh(M-h).min()),"synthetic_solver":d,
  "repeatability":"passed","group_splits":"passed","P_pre_tau_signature":"passed"}

def preflight_smoke():
 OUT.mkdir(parents=True,exist_ok=True);PRE.mkdir(parents=True,exist_ok=True)
 if (scipy.__version__,sklearn.__version__)!=("1.15.2","1.5.2"):raise RuntimeError("frozen runtime mismatch")
 e18=EXT18_PRE;e19=EXT19_PRE
 e18paths=[e18/"frozen_manifest.json",e18/"smoke.json",e18/"source_registry.json"]
 e19paths=[e19/"frozen_manifest.json",e19/"smoke.json",e19/"source_registry.json"]
 for p in e18paths+e19paths:
  if not p.is_file():raise FileNotFoundError(p)
 m18=json.loads(e18paths[0].read_text(encoding="utf-8"));s18=json.loads(e18paths[1].read_text(encoding="utf-8"))
 m19=json.loads(e19paths[0].read_text(encoding="utf-8"));s19=json.loads(e19paths[1].read_text(encoding="utf-8"))
 r19=json.loads(e19paths[2].read_text(encoding="utf-8"))
 if m18.get("fit_started") is not False or s18.get("status")!="passed":raise AssertionError("Ext18 preflight lineage invalid")
 if m19.get("fit_started") is not False or s19.get("status")!="passed":raise AssertionError("Ext19 preflight lineage invalid")
 sources={}
 lineage=[Path(__file__),PROTOCOL,HOME/"ext19_partially_linear_logistic_gam_runner.py",
  HOME/"ext19_partially_linear_logistic_gam_protocol_vi.md",*e18paths,*e19paths,
  EXT03/"outer_predictions.csv",EXT03/"results.json",EXT03/"manifest.json",EXT03_PRE/"source_registry.json",
  EXT04/"outer_predictions.csv",EXT04/"results.json",EXT04/"manifest.json",EXT04_PRE/"source_registry.json"]
 for p in lineage:
  if not p.is_file():raise FileNotFoundError(p)
  sources[str(p)]={"sha256":sha(p),"role":"validation-only code/protocol lineage or frozen P_pre comparator artifact"}
 schema={};validation={}
 for ds in ("devign","reveal"):
  hp=ext3.H3/ds/"xpre_validation.npz";z=np.load(hp,allow_pickle=False);names=z["feature_names"].astype(str).tolist();z.close()
  if len(names)!=34 or names[5]!="p_gate":raise AssertionError("H3-B schema mismatch")
  schema[ds]={"features":34,"p_gate_index":5,"sha256":sha(hp)}
  sources[str(hp)]={"sha256":sha(hp),"role":"validation static features"}
 syn=synthetic_preflight();meta=ext5.load_inputs();donors,_=ext3.verify_donors(meta)
 for ds in ("devign","reveal"):
  d=ext5.build_sources(meta,ds);X=feature_matrix(d,np.arange(len(d["ids"])))
  if len(d["arms"])!=15 or set(d["arms"])!=set(ARMS):raise AssertionError("raw arm roster mismatch")
  aps={a:float(ext16.average_precision_score(d["y"],p)) for a,p in d["arms"].items()}
  if not np.isfinite(X).all() or len(aps)!=15 or not np.isfinite(list(aps.values())).all():
   raise AssertionError("validation matrix/AP family invalid")
  folds=group_folds(d["y"],d["g"],BASE+8100);g=np.asarray(d["g"]).astype(str);cov=np.concatenate([v for _,v in folds])
  if set(cov)!=set(range(len(d["ids"]))) or any(set(g[a])&set(g[b]) for a,b in folds):
   raise AssertionError("validation fold coverage/leakage")
  validation[ds]={"n":len(d["ids"]),"groups":int(pd.Series(g).nunique()),"raw_width":RAW_WIDTH,
   "design_width":DESIGN_WIDTH,"arms":15,"finite_AP_family":True,"group_folds":"passed","provenance":d["provenance"]}
  for q in (ext3.SOURCE/"inputs.parquet",ext3.SOURCE/"scores.parquet"):
   sources[str(q)]={"sha256":sha(q),"role":"mixed-split; ext5 loader applies validation predicate"}
  for q in d["provenance"]:
   if isinstance(q,dict) and q.get("path"):sources[q["path"]]={"sha256":q["sha256"],"role":"validation-only raw arm source"}
 for path,entry in r19.get("sources",{}).items():
  low=path.lower().replace("/","\\")
  if "test_" in low or ".html" in low or "changes_after_prereg" in low or (
   "independent-post-ext19" in low and "\\full\\" in low) or (
   "independent-post-ext18" in low and "\\full\\" in low):
   raise AssertionError("forbidden inherited lineage path")
  if not Path(path).is_file() or sha(path)!=entry["sha256"]:
   raise AssertionError("Ext19 preflight lineage source mismatch")
  sources[path]={"sha256":entry["sha256"],"role":"source inherited from Ext19 preflight registry"}
 low=[p.lower().replace("/","\\") for p in sources]
 bad={"test":sum("test_" in p or "\\test\\" in p or "/test/" in p for p in low),
      "html":sum(".html" in p for p in low),
      "ledger":sum("changes_after_prereg" in p for p in low),
      "ext18_full":sum("independent-post-ext18" in p and "\\full\\" in p for p in low),
      "ext19_full":sum("independent-post-ext19" in p and "\\full\\" in p for p in low),
      "ext20_full":sum("independent-post-ext20" in p and "\\full\\" in p for p in low)}
 if any(bad.values()):raise AssertionError(f"forbidden registry path: {bad}")
 reg={"sources":sources,"validation_only":True,"forbidden_path_counts":bad,
  "ext18_lineage_sha256":{str(p):sha(p) for p in e18paths},
  "ext19_preflight_lineage_sha256":{str(p):sha(p) for p in e19paths}}
 rp=PRE/"source_registry.json";atomic_json(rp,reg)
 frozen={"candidate":"Ext20 context-interaction logistic stack","fit_started":False,
  "validation_only":True,"full_fit_requires_explicit_flag_and_independent_release":True,
  "raw_features":RAW_WIDTH,"design_features":DESIGN_WIDTH,"H3_columns":BASE_WIDTH,
  "family_summaries":FAMILY_WIDTH,"prompt_signals":list(SIGNAL_NAMES),
  "interaction_width":BASE_WIDTH*SIGNAL_WIDTH,"interaction_penalty_multiplier":INTERACTION_PENALTY,
  "C_grid":list(CS),"signal":"logit(B2); logit(B2)-logit(B2-flip); logit(B2)-logit(B2-nolabel); probabilities clipped at 1e-6",
  "fold_local_transform":"StandardScaler on H3, 11 family scores, and 3 prompt signals; H3 x three prompt-signal products centered/scaled by training rows only",
  "MM_max_updates":MM_MAX,"gradient_tolerances":{"L2":GRAD_L2_TOL,"inf":GRAD_INF_TOL},
  "linear_backward_tol":BACKWARD_TOL,"objective_guard_rel":OBJ_GUARD_REL,"descent_ulps":DESCENT_ULPS,
  "scipy":scipy.__version__,"numpy":np.__version__,"scikit_learn":sklearn.__version__,
  "source_count":len(sources),**bad,"test_rows_labels_scores_predictions_read":False,
  "simulator_html_accessed":False,"ext18_full_outcomes_read_or_hashed":False,
  "ext19_full_outcomes_read_or_hashed":False,"runner_sha256":sha(Path(__file__)),
  "protocol_sha256":sha(PROTOCOL),"source_registry_sha256":sha(rp)}
 atomic_json(PRE/"frozen_manifest.json",frozen)
 smoke={"status":"passed","synthetic":syn,"validation":validation,"donor_audit":donors,
  "schema":schema,"source_count":len(sources),"forbidden_path_counts":bad,"fit_started":False,
  "test_rows_labels_scores_predictions_read":False,"simulator_html_accessed":False,
  "ext18_full_outcomes_read_or_hashed":False,"ext19_full_outcomes_read_or_hashed":False,
  "scipy_version":scipy.__version__,"numpy_version":np.__version__,"scikit_learn_version":sklearn.__version__,
  "runner_sha256":frozen["runner_sha256"],"protocol_sha256":frozen["protocol_sha256"],
  "source_registry_sha256":frozen["source_registry_sha256"]}
 atomic_json(PRE/"smoke.json",smoke)
 atomic_json(PRE/"run_state.json",{"state":"preflight_passed_full_fit_not_started","fit_started":False,
  "runner_sha256":frozen["runner_sha256"],"protocol_sha256":frozen["protocol_sha256"],
  "source_registry_sha256":frozen["source_registry_sha256"]})
 return smoke

def assert_frozen_hashes():
 f=json.loads((PRE/"frozen_manifest.json").read_text(encoding="utf-8"));s=json.loads((PRE/"smoke.json").read_text(encoding="utf-8"));reg=json.loads((PRE/"source_registry.json").read_text(encoding="utf-8"))
 if f.get("fit_started") is not False or f.get("full_fit_requires_explicit_flag_and_independent_release") is not True:raise RuntimeError("Ext20 preflight freeze invalid")
 for k,p in (("runner_sha256",Path(__file__)),("protocol_sha256",PROTOCOL),("source_registry_sha256",PRE/"source_registry.json")):
  if f.get(k)!=sha(p) or s.get(k)!=sha(p):raise RuntimeError("Ext20 frozen hash mismatch: "+k)
 if (scipy.__version__,np.__version__,sklearn.__version__)!=(f["scipy"],f["numpy"],f["scikit_learn"]):raise RuntimeError("runtime version mismatch")
 for p,m in reg["sources"].items():
  low=p.lower()
  norm=low.replace("/","\\")
  if "test_" in low or ".html" in low or "changes_after_prereg" in low or any(tag in norm for tag in (
   "independent-post-ext18\\full\\","independent-post-ext19\\full\\","independent-post-ext20\\full\\")):
   raise RuntimeError("forbidden registered path")
  if not Path(p).is_file() or sha(p)!=m["sha256"]:raise RuntimeError("registered source hash mismatch: "+p)
 return f

def run_full_validation():
 frozen=assert_frozen_hashes() # hash guard precedes every fitting/data read
 FULL.mkdir(parents=True,exist_ok=True);atomic_json(FULL/"run_state.json",{"state":"hashes_verified_fitting_started","fit_started":True,"runner_sha256":frozen["runner_sha256"],"protocol_sha256":frozen["protocol_sha256"],"source_registry_sha256":frozen["source_registry_sha256"]})
 meta=ext5.load_inputs();donors,_=ext3.verify_donors(meta);data_by={ds:ext5.build_sources(meta,ds) for ds in ("devign","reveal")};cand={}
 for ds in ("devign","reveal"):
  d=data_by[ds];y=d["y"];g=d["g"];outer=group_folds(y,g,BASE+8100);post=np.full(len(y),np.nan);score=np.full(len(y),np.nan);fr=[]
  for oi,(T,H) in enumerate(outer):
   sel=select_c(d,T,oi);rec={"outer_fold":oi,"selection":{k:v for k,v in sel.items() if k!="oof_score"}}
   if not sel["complete"] or sel["C"] is None:rec["status"]=sel["reason"];fr.append(rec);continue
   try:
    X=feature_matrix(d,T);prep=prepare_partition(X);model,diag=fit_post(X,y[T],sel["C"],prep)
    if not diag["usable"]:raise RuntimeError("outer solver unusable")
    eta,p=predict_post(model,feature_matrix(d,H));post[H]=p;score[H]=eta;rec.update({"status":"complete","selected_C":sel["C"],"fit":diag})
   except Exception as e:rec.update({"status":"outer_fit_failure","error":type(e).__name__+":"+str(e)})
   fr.append(rec)
  complete=bool(len(fr)==3 and all(r["status"]=="complete" for r in fr) and np.isfinite(post).all() and np.isfinite(score).all())
  if not complete:post[:]=np.nan;score[:]=np.nan
  cand[ds]={"n":len(y),"groups":int(pd.Series(g).nunique()),"outer":outer,"post":post,"score":score,"folds":fr,"complete":complete}
 p3=pd.read_csv(EXT03/"outer_predictions.csv",low_memory=False);r3=json.loads((EXT03/"results.json").read_text(encoding="utf-8"));p4=pd.read_csv(EXT04/"outer_predictions.csv",low_memory=False);r4=json.loads((EXT04/"results.json").read_text(encoding="utf-8"));pre_audit={}
 for ds in ("devign","reveal"):
  d=data_by[ds];info=cand[ds];y=d["y"];g=np.asarray(d["g"]).astype(str);ids=d["ids"];old3=p3[(p3.dataset==ds)&(p3.model=="P_pre")].set_index("id").reindex(ids);old4=p4[(p4.dataset==ds)&(p4.model=="P_pre")].set_index("id").reindex(ids)
  for q in (old3,old4):
   if q.prediction.isna().any() or not np.array_equal(q.target_label.to_numpy(int),y) or not np.array_equal(q.group_id.astype(str).to_numpy(),g):raise ValueError("FrozenPre ID/label/group mismatch")
  pre=np.full(len(y),np.nan);tau=np.full(len(y),np.nan);a3=[];a4=[]
  for oi,(T,H) in enumerate(info["outer"]):
   fp=ext16.frozen_pre(d,T,BASE+100000+1000*oi);pp=fp["model"].predict_proba(d["x"][H])[:,1];f3=r3["datasets"][ds]["outer_folds"][oi];f4=r4["datasets"][ds]["outer_folds"][oi]
   if abs(fp["C"]-f3["P_pre_C_outer_train"])>1e-12 or abs(fp["tau"]-f3["tau_T"])>1e-12 or abs(fp["C"]-f4["P_pre_C"])>1e-12 or abs(fp["tau"]-f4["P_pre_tau"])>1e-12:raise ValueError("FrozenPre C/tau parity mismatch")
   for q in (old3,old4):
    if not np.array_equal(q.iloc[H].outer_fold.to_numpy(int),np.full(len(H),oi)):raise ValueError("FrozenPre fold assignment mismatch")
   d3=float(np.max(np.abs(pp-old3.iloc[H].prediction.to_numpy(float))));d4=float(np.max(np.abs(pp-old4.iloc[H].prediction.to_numpy(float))))
   if max(d3,d4)>1e-12:raise ValueError("FrozenPre probability parity mismatch")
   pre[H]=pp;tau[H]=fp["tau"];a3.append(d3);a4.append(d4)
  info["pre"]=pre;info["tau"]=tau;pre_audit[ds]={"max_Ext03_abs_diff":max(a3),"max_Ext04_abs_diff":max(a4)}
 predictions=[];datasets={};pv=[];pk=[]
 for di,ds in enumerate(("devign","reveal")):
  d=data_by[ds];i=cand[ds];y=d["y"];g=d["g"];arms=d["arms"];pre=i["pre"];tau=i["tau"];models={"P_pre":(pre,pre)}
  if i["complete"]:models["P_post"]=(i["post"],i["score"])
  models.update({"arm_"+a:(p,p) for a,p in arms.items()});metrics={k:ext16.metric(y,p,s,tau) for k,(p,s) in models.items()}
  if i["complete"]:
   boot=ext16.bootstrap(y,g,tau,pre,i["post"],i["score"],arms,di,draw_count=5000)
   for arm,res in boot["comparisons"].items():pv.append(res["AP_p_raw"]);pk.append((ds,arm))
   pp=pre>=tau;po=i["post"]>=tau;truth=y.astype(bool);repairs=int(np.sum((pp!=truth)&(po==truth)));harms=int(np.sum((pp==truth)&(po!=truth)))
  else:boot={"unavailable":"planned 30 AP/Holm family unavailable"};repairs=harms=None
  for name,(prob,aps) in models.items():
   for oi,(_,H) in enumerate(i["outer"]):
    f=d["meta"].iloc[H][["id","group_id","target_label"]].copy();f["dataset"]=ds;f["model"]=name;f["prediction"]=prob[H];f["ap_score"]=aps[H];f["threshold"]=tau[H];f["outer_fold"]=oi;predictions.append(f)
  datasets[ds]={"nested_complete":i["complete"],"n":i["n"],"groups":i["groups"],"metrics":metrics,"primary_bootstrap":boot,"repairs":repairs,"harms":harms,"outer_folds":i["folds"]}
 nested=all(r["nested_complete"] for r in datasets.values())
 if nested:
  if len(pv)!=30:raise AssertionError("AP family planned size mismatch")
  adj=ext16.holm(pv)
  for (ds,a),p,pa in zip(pk,pv,adj):
   c=datasets[ds]["primary_bootstrap"]["comparisons"][a];c["AP_p_Holm"]=float(pa);c["AP_gate_pass"]=bool(c["AP_CI95"][0]>0 and pa<.05)
 overall="unavailable"
 if nested:
  for ds,r in datasets.items():
   ci=r["primary_bootstrap"]["MCC_P_post_minus_P_pre_CI95"];m="pass" if ci[0]>.02 else ("fail" if ci[1]<=.02 else "inconclusive");comps=r["primary_bootstrap"]["comparisons"];a="pass" if len(comps)==15 and all(v.get("AP_gate_pass") for v in comps.values()) else "fail";r["objective_gates"]={"MCC":m,"MCC_CI95":ci,"AP_all_15":a,"AP_pass_count":sum(v.get("AP_gate_pass",False) for v in comps.values()),"overall":"fail" if "fail" in (m,a) else ("inconclusive" if "inconclusive" in (m,a) else "pass")}
  overall="fail" if any(r["objective_gates"]["overall"]=="fail" for r in datasets.values()) else ("inconclusive" if any(r["objective_gates"]["overall"]=="inconclusive" for r in datasets.values()) else "pass")
 pd.concat(predictions,ignore_index=True).to_csv(FULL/"outer_predictions.csv",index=False);results={"run_completion":"completed","nested_complete_all":nested,"objective_gate_overall":overall,"datasets":datasets,"planned_AP_Holm_family_size":30,"actual_AP_Holm_family_size":30 if nested else 0,"validation_only":True,"test_rows_labels_scores_predictions_read":False,"simulator_html_accessed":False}
 atomic_json(FULL/"results.json",results);atomic_json(FULL/"pre_p_pre_audit.json",pre_audit)
 report=["# Ext20 context-interaction validation report","",f"Nested complete={nested}; overall gate={overall}.","Exploratory validation-only analysis.",""]
 for ds,r in datasets.items():
  report += [f"## {ds}",f"Complete={r['nested_complete']}; gates={r.get('objective_gates',{})}"]
  if r["nested_complete"]:
   b=r["primary_bootstrap"];report.append(f"AP post/pre={r['metrics']['P_post']['AP']:.6f}/{r['metrics']['P_pre']['AP']:.6f}; ΔMCC={b['delta_MCC_P_post_minus_P_pre']:+.6f}, CI={b['MCC_P_post_minus_P_pre_CI95']}; repairs={r['repairs']}; harms={r['harms']}.")
  else:report.append("Incomplete nested output; effect verdict and full AP family unavailable.")
 (FULL/"report.md").write_text("\n".join(report)+"\n",encoding="utf-8")
 manifest={"candidate":"Ext20 context-interaction logistic stack","fit_started":True,"validation_only":True,"nested_complete_all":nested,"objective_gate_overall":overall,"runner_sha256":sha(Path(__file__)),"protocol_sha256":sha(PROTOCOL),"source_registry_sha256":sha(PRE/"source_registry.json"),"test_rows_labels_scores_predictions_read":False,"simulator_html_accessed":False,"ext18_full_outcomes_read_or_hashed":False}
 atomic_json(FULL/"manifest.json",manifest);hashes={n:sha(FULL/n) for n in ("outer_predictions.csv","results.json","pre_p_pre_audit.json","report.md","manifest.json")};hashes.update({"runner_sha256":sha(Path(__file__)),"protocol_sha256":sha(PROTOCOL),"source_registry_sha256":sha(PRE/"source_registry.json")});atomic_json(FULL/"artifact_hashes.json",hashes);atomic_json(FULL/"run_state.json",{"state":"completed","exit_status":0,"nested_complete_all":nested,"objective_gate_overall":overall,"artifact_hashes_sha256":sha(FULL/"artifact_hashes.json")})

if __name__=="__main__":
 if "--smoke" in sys.argv:print(json.dumps(preflight_smoke(),indent=2))
 elif "--assert-hashes" in sys.argv:print(json.dumps(assert_frozen_hashes(),indent=2))
 elif "--run-full-validation" in sys.argv:run_full_validation()
 else:raise SystemExit("Use --smoke, --assert-hashes, or --run-full-validation")
