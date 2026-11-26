from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix

HOME = Path(r"D:\JUNIOR\LabThayTho\GRACE-summary\grace-notebook-experiments")
sys.path.insert(0, str(HOME))
import ext20_test_pipeline as testio
import ext20_uniform_ridge_pre_c_runner as uniform

PRED, LOCK, SCORE_MANIFEST = uniform.PRED, uniform.LOCK, uniform.SCORE_MANIFEST
import hashlib
def sha(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

sm=json.loads(SCORE_MANIFEST.read_text(encoding="utf-8"))
if sm["predictions_sha256"]!=sha(PRED) or sm["validation_lock_sha256"]!=sha(LOCK):
    raise RuntimeError("hash mismatch; refusing truth read")
pred=pd.read_csv(PRED,dtype={"id":str})
truth=pd.read_parquet(testio.ext3.SOURCE/"inputs.parquet",
    columns=["split","dataset","id","target_label","group_id"],
    filters=[("split","==","test")],engine="pyarrow")
lock=json.loads(LOCK.read_text(encoding="utf-8"))
out={"phase":"truth_read_after_frozen_hash_check","datasets":{}}
for ds in testio.DATASETS:
    t=truth[truth.dataset==ds].copy();t["id"]=t.id.astype(str)
    p=pred[pred.dataset==ds]
    z=t.merge(p,on=["dataset","id"],how="outer",validate="one_to_one",indicator=True)
    if not z._merge.eq("both").all(): raise RuntimeError(f"{ds}: id join mismatch")
    y=z.target_label.to_numpy(int);tau=float(lock["datasets"][ds]["P_pre_tau"])
    pp=z.P_pre.to_numpy(float)>=tau;po=z.P_post.to_numpy(float)>=tau;truthp=y.astype(bool)
    cm={}
    for name,predp in (("P_pre",pp),("P_post",po)):
        tn,fp,fn,tp=confusion_matrix(y,predp,labels=[0,1]).ravel()
        cm[name]={"TP":int(tp),"FP":int(fp),"FN":int(fn),"TN":int(tn)}
    out["datasets"][ds]={"n":len(y),"tau":tau,"confusion":cm,
        "repairs":int(np.sum((pp!=truthp)&(po==truthp))),
        "harms":int(np.sum((pp==truthp)&(po!=truthp)))}
path=uniform.OUT/"test_confusion_summary.json"
path.write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
print(json.dumps(out,indent=2))
