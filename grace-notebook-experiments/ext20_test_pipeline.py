"""Ext20 validation-locked test extension; score and label phases are separate."""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.special import expit
from sklearn.metrics import (average_precision_score, roc_auc_score,
    matthews_corrcoef, balanced_accuracy_score, confusion_matrix)
import ext03_runner as ext3
import ext05_runner as ext5
import ext16_focal_loss_mm_runner as ext16
import ext20_context_interaction_runner as ext20

HOME = Path(__file__).resolve().parent
OUT = HOME / "runs/independent-post-ext20-context-interaction-test-20261125/attempt-1"
PRED = OUT / "frozen_test_predictions.csv"
SCORE_MANIFEST = OUT / "score_manifest.json"
LOCK = OUT / "validation_lock.json"
PARAMS = OUT / "locked_model_parameters.npz"
RESULTS = OUT / "test_metrics.json"
REPORT = OUT / "test_report.md"
DATASETS = ("devign", "reveal")
EXPECTED_N = {"devign": 2732, "reveal": 2274}
DRAWS, BOOT_SEED, FINAL_CV_INDEX = 5000, 20261117, 3
FINAL_CV_SEED = ext20.BASE + 100000 + 1000 * FINAL_CV_INDEX
PARQUET_ARMS = ("B0", "B1", "B1-H2", "B2", "B2-flip", "B2-nolabel")
RECORD_ARMS = {"B1-full": (42,), "B1-shuf": (42, 43, 44),
               "B2-labelonly": (42,), "B2-rand": (42, 43, 44)}
B3_TEST = (ext3.ROOT / "artifact-packaging/05_exploratory_and_blind_review/b3/"
           "test_outputs/I28_verified_patch/b3_test_release_20261110/seed_42")
ACCESS_DEVIATION = {"pre_run_test_jsonl_schema_count_audit": {
    "label_fields_present": True, "label_values_deserialized": True,
    "label_values_inspected_or_used": False, "occurred_before_prediction_freeze": True},
    "classification": "exploratory; strict no-access boundary breached before prediction freeze"}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, allow_nan=False), encoding="utf-8")
    tmp.replace(path)


def safe(v):
    if isinstance(v, dict): return {str(k): safe(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)): return [safe(x) for x in v]
    if isinstance(v, np.ndarray): return v.tolist()
    if isinstance(v, np.generic): return v.item()
    if isinstance(v, Path): return str(v)
    return v


def scan_string(s, i):
    if s[i] != '"': raise ValueError("expected string")
    i += 1
    while i < len(s):
        if s[i] == "\\": i += 2
        elif s[i] == '"': return i + 1
        else: i += 1
    raise ValueError("unterminated string")


def skip_value(s, i):
    while s[i].isspace(): i += 1
    if s[i] == '"': return scan_string(s, i)
    if s[i] in "[{":
        stack = ["]" if s[i] == "[" else "}"]
        i += 1
        while i < len(s) and stack:
            c = s[i]
            if c == '"':
                i = scan_string(s, i)
                continue
            if c == "[": stack.append("]")
            elif c == "{": stack.append("}")
            elif c in "]}":
                if c != stack[-1]: raise ValueError("unbalanced JSON")
                stack.pop()
            i += 1
        if stack: raise ValueError("unterminated JSON container")
        return i
    while i < len(s) and s[i] not in ",}": i += 1
    return i


def selected_fields(line, wanted):
    """Decode selected top-level fields only; skip all other values (including labels)."""
    i = 0
    while line[i].isspace(): i += 1
    if line[i] != "{": raise ValueError("expected JSON object")
    i += 1
    out = {}
    while True:
        while i < len(line) and (line[i].isspace() or line[i] == ","): i += 1
        if i >= len(line) or line[i] == "}": break
        j = scan_string(line, i)
        key = json.loads(line[i:j])
        i = j
        while line[i].isspace(): i += 1
        if line[i] != ":": raise ValueError("missing colon")
        i += 1
        while line[i].isspace(): i += 1
        a, b = i, skip_value(line, i)
        if key in wanted: out[key] = json.loads(line[a:b])
        i = b
    return out


def get_test_ids(ds):
    m = pd.read_parquet(ext3.SOURCE / "inputs.parquet",
        columns=["split", "dataset", "id"],
        filters=[("split", "==", "test")], engine="pyarrow")
    if set(m.split.astype(str)) != {"test"}: raise ValueError("test split projection mismatch")
    ids = m[m.dataset == ds].sort_values("id").id.astype(str).tolist()
    if len(ids) != EXPECTED_N[ds] or len(ids) != len(set(ids)):
        raise ValueError(f"{ds}: test ID census failure")
    return ids


def h3_test(ds, ids):
    path = ext3.H3 / ds / "xpre_test.npz"
    with np.load(path, allow_pickle=False) as z:
        srcids = z["ids"].astype(str)
        names = z["feature_names"].astype(str).tolist()
        X = np.asarray(z["X"], dtype=np.float64)
    pos = pd.Index(srcids).get_indexer(ids)
    if (pos < 0).any() or len(srcids) != len(ids) or len(set(srcids)) != len(srcids):
        raise ValueError(f"{ds}: H3 test IDs mismatch")
    X = X[pos]
    if len(names) != 34 or names[5] != "p_gate" or X.shape != (len(ids), 34):
        raise ValueError(f"{ds}: H3 test schema mismatch")
    if not np.isfinite(X).all(): raise ValueError(f"{ds}: nonfinite H3 feature")
    return X, names, sha(path)


def parquet_arms(ds, ids):
    path = ext3.SOURCE / "scores.parquet"
    cols = ["split", "dataset", "id", "arm", "backend", "model", "log_odds", "score_valid"]
    df = pd.read_parquet(path, columns=cols,
        filters=[("split", "==", "test")], engine="pyarrow")
    q = df[(df.dataset == ds) & df.arm.isin(PARQUET_ARMS)]
    if set(q.split.astype(str)) != {"test"} or q.duplicated(["id", "arm"]).any():
        raise ValueError(f"{ds}: test score parquet identity/uniqueness failure")
    if set(q.model.astype(str)) != {ext3.MODEL_SHA} or set(q.backend.astype(str)) != {"qwen"}:
        raise ValueError(f"{ds}: raw score model/backend mismatch")
    if q.score_valid.isna().any() or not q.score_valid.astype(bool).all():
        raise ValueError(f"{ds}: invalid raw score")
    if not np.isfinite(q.log_odds.to_numpy(float)).all():
        raise ValueError(f"{ds}: nonfinite raw logits")
    arms = {}
    for arm in PARQUET_ARMS:
        a = q[q.arm == arm].set_index("id").reindex(ids)
        if a.log_odds.isna().any() or len(a) != len(ids):
            raise ValueError(f"{ds} {arm}: test score coverage failure")
        arms[arm] = expit(a.log_odds.to_numpy(float))
    return arms, {"path": str(path), "sha256": sha(path), "rows": len(q),
                  "label_column_present": False}


def record_arm(path, ds, arm, seed, ids):
    wanted = {"id", "dataset", "split", "arm", "seed",
              "logprob_0", "logprob_1", "model_sha256"}
    values = {}
    with Path(path).open(encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            r = selected_fields(line, wanted)
            if (r.get("dataset") != ds or r.get("split") != "test"
                or r.get("arm") != arm or int(r.get("seed", seed)) != seed
                or r.get("model_sha256") != ext3.MODEL_SHA):
                raise ValueError(f"{ds} {arm}-{seed}: record provenance mismatch")
            rid = str(r["id"])
            ell = float(r["logprob_1"]) - float(r["logprob_0"])
            if not np.isfinite(ell) or rid in values:
                raise ValueError(f"{ds} {arm}-{seed}: invalid/duplicate score")
            values[rid] = float(expit(ell))
    if set(values) != set(ids): raise ValueError(f"{ds} {arm}-{seed}: ID set mismatch")
    return np.asarray([values[i] for i in ids], dtype=float)


def b3_source(ds):
    tm_path = B3_TEST / ds / "test" / "run_manifest.json"
    vm_path = ext3.B3_ROOT / ds / "seed_42" / ds / "validation" / "run_manifest.json"
    tm, vm = (json.loads(p.read_text(encoding="utf-8")) for p in (tm_path, vm_path))
    a, b = tm.get("b3_test_identity") or {}, vm.get("b3_input_identity") or {}
    if (tm.get("arm") != "B3" or tm.get("dataset") != ds or tm.get("split") != "test"
        or a.get("method_id") != "b3-verified-patch-v1"
        or a.get("model_sha256") != ext3.MODEL_SHA or a.get("count") != EXPECTED_N[ds]
        or a.get("runtime_contract_sha256") != b.get("runtime_contract_sha256")
        or a.get("tokenizer_revision") != b.get("tokenizer_revision")
        or a.get("pool_sha256") != b.get("pool_sha256")
        or tm.get("scoring") != vm.get("scoring")):
        raise ValueError(f"{ds}: B3 test identity is not validation-compatible")
    records = B3_TEST / ds / "test" / "records.jsonl"
    return records, {"manifest": str(tm_path), "manifest_sha256": sha(tm_path),
        "records": str(records), "records_sha256": sha(records),
        "method_id": a["method_id"], "release_id": a.get("release_id"),
        "runtime_contract_sha256": a["runtime_contract_sha256"],
        "model_sha256": a["model_sha256"], "pool_sha256": a["pool_sha256"],
        "prompt_set_sha256": tm.get("prompt_set_sha256"), "rows": a["count"]}


def all_test_arms(ds, ids):
    arms, pqsrc = parquet_arms(ds, ids)
    records = []
    for arm, seeds in RECORD_ARMS.items():
        for seed in seeds:
            path = ext3.ROOT / f"runs/final/{ds}/test/{arm}/{seed}/records.jsonl"
            key = f"{arm}-{seed}" if len(seeds) > 1 else arm
            arms[key] = record_arm(path, ds, arm, seed, ids)
            records.append({"arm": arm, "seed": seed, "path": str(path),
                            "sha256": sha(path), "label_values_decoded": False})
    b3path, b3prov = b3_source(ds)
    arms["B3"] = record_arm(b3path, ds, "B3", 42, ids)
    records.append({"arm": "B3", **b3prov, "label_values_decoded": False})
    if set(arms) != set(ext20.ARMS) or len(arms) != 15:
        raise ValueError(f"{ds}: Ext20 15-arm roster mismatch")
    if any(not np.isfinite(v).all() or (v < 0).any() or (v > 1).any()
           for v in arms.values()):
        raise ValueError(f"{ds}: invalid probability in test arms")
    return arms, {"parquet": pqsrc, "records": records}


def score_only():
    OUT.mkdir(parents=True, exist_ok=True)
    frozen = ext20.assert_frozen_hashes()
    vmeta = ext5.load_inputs()
    ext3.verify_donors(vmeta)
    locks, models, params = {}, {}, {}
    for ds in DATASETS:
        print(f"validation-only selection and fitting: {ds}", flush=True)
        d = ext5.build_sources(vmeta, ds)
        Q = np.arange(len(d["y"]), dtype=int)
        pre = ext16.frozen_pre(d, Q, FINAL_CV_SEED)
        selection = ext20.select_c(d, Q, FINAL_CV_INDEX)
        if not selection["complete"] or selection["C"] is None:
            raise RuntimeError(f"{ds}: locked Ext20 selector unavailable")
        Xv = ext20.feature_matrix(d, Q)
        prep = ext20.prepare_partition(Xv)
        post, diag = ext20.fit_post(Xv, d["y"], selection["C"], prep)
        if not diag["usable"]: raise RuntimeError(f"{ds}: final P_post solver unusable")
        locks[ds] = {"validation_n": len(Q),
            "validation_groups": int(pd.Series(d["g"]).nunique()),
            "shared_group_cv_seed": int(FINAL_CV_SEED),
            "P_pre_C": float(pre["C"]), "P_pre_tau": float(pre["tau"]),
            "P_pre_OOF_AP_by_C": pre["AP_by_C"],
            "P_post_C": float(selection["C"]),
            "P_post_selector": safe({k:v for k,v in selection.items() if k != "oof_score"}),
            "P_post_final_solver": safe(diag)}
        lr = pre["model"].named_steps["logisticregression"]
        sc = pre["model"].named_steps["standardscaler"]
        params.update({f"{ds}_pre_mean":sc.mean_, f"{ds}_pre_scale":sc.scale_,
            f"{ds}_pre_coef":lr.coef_, f"{ds}_pre_intercept":lr.intercept_,
            f"{ds}_post_theta":post["theta"],
            f"{ds}_post_h3_mean":prep["h3_scaler"].mean_,
            f"{ds}_post_h3_scale":prep["h3_scaler"].scale_,
            f"{ds}_post_family_mean":prep["family_scaler"].mean_,
            f"{ds}_post_family_scale":prep["family_scaler"].scale_,
            f"{ds}_post_signal_mean":prep["signal_scaler"].mean_,
            f"{ds}_post_signal_scale":prep["signal_scaler"].scale_,
            f"{ds}_post_interaction_mean":prep["interaction_mean"],
            f"{ds}_post_interaction_scale":prep["interaction_scale"]})
        models[ds] = (pre["model"], post)
    # Persist every cohort's validation-selected model and threshold before test scoring.
    atomic_json(LOCK, {"protocol":"Ext20 validation-locked final-fit test extension",
        "selection_rule":"existing grouped 3-fold Ext20 selector on all validation rows, oi=3",
        "threshold_rule":"P_pre OOF threshold from same group folds; shared by all test MCC",
        "datasets":locks, "validation_runner_sha256":frozen["runner_sha256"],
        "validation_protocol_sha256":frozen["protocol_sha256"],
        "validation_source_registry_sha256":frozen["source_registry_sha256"],
        "validation_inputs_sha256":sha(ext3.SOURCE/"inputs.parquet"),
        "validation_scores_sha256":sha(ext3.SOURCE/"scores.parquet"),
        "test_labels_or_groups_read":False})
    np.savez_compressed(PARAMS, **params)

    frames, test_sources = [], {}
    for ds in DATASETS:
        ids = get_test_ids(ds)
        Xt, names, h3hash = h3_test(ds, ids)
        arms, sources = all_test_arms(ds, ids)
        Xtest = ext20.feature_matrix({"x":Xt, "names":names, "arms":arms},
                                     np.arange(len(ids), dtype=int))
        pre_model, post_model = models[ds]
        ppre = pre_model.predict_proba(Xt)[:,1]
        post_eta, ppost = ext20.predict_post(post_model, Xtest)
        if not np.isfinite(ppre).all() or not np.isfinite(ppost).all():
            raise FloatingPointError(f"{ds}: nonfinite frozen test prediction")
        frame = pd.DataFrame({"dataset":ds, "id":ids, "P_pre":ppre,
                              "P_post":ppost, "P_post_logit":post_eta})
        for arm in ext20.ARMS: frame[f"arm_{arm}"] = arms[arm]
        frames.append(frame)
        test_sources[ds] = {"n":len(ids), "h3_sha256":h3hash,
                            "arms":sources, "label_values_decoded":False}
        print(f"frozen label-free predictions: {ds}, n={len(ids)}", flush=True)

    pred = pd.concat(frames, ignore_index=True)
    if {"target_label","group_id"} & set(pred.columns):
        raise AssertionError("labels/groups in frozen predictions")
    pred.to_csv(PRED, index=False)
    atomic_json(SCORE_MANIFEST, {"phase":"score_only_completed",
        "predictions_path":str(PRED), "predictions_sha256":sha(PRED),
        "validation_lock_path":str(LOCK), "validation_lock_sha256":sha(LOCK),
        "model_parameters_path":str(PARAMS), "model_parameters_sha256":sha(PARAMS),
        "test_sources":test_sources, "rows":len(pred), "columns":list(pred.columns),
        "test_label_values_decoded_or_used":False,
        "test_label_values_decoded_or_used_scope":"score-only phase; a separate earlier JSONL schema/count audit deserialized labels without inspecting or using values",
        "pre_run_data_access_deviation":ACCESS_DEVIATION,
        "ready_for_separate_label_evaluation":True})
    print(json.dumps({"state":"score_only_completed","rows":len(pred),
                      "predictions_sha256":sha(PRED)}, indent=2))

def metric(y, p, tau):
    d = p >= tau
    tn, fp, fn, tp = confusion_matrix(y, d, labels=[0,1]).ravel()
    return {"AP":float(average_precision_score(y,p)),
        "AUROC":float(roc_auc_score(y,p)),
        "MCC":float(matthews_corrcoef(y,d)),
        "balanced_accuracy":float(balanced_accuracy_score(y,d)),
        "confusion":{"tn":int(tn),"fp":int(fp),"fn":int(fn),"tp":int(tp)},
        "positive_rate":float(d.mean())}


def ci(v): return np.percentile(np.asarray(v,float), [2.5,97.5]).tolist()
def p_two_sided(v):
    a=np.asarray(v,float)
    return min(1., 2*min(float(np.mean(a<=0)),float(np.mean(a>=0))))


def evaluate():
    if not PRED.is_file() or not LOCK.is_file() or not SCORE_MANIFEST.is_file():
        raise FileNotFoundError("run score-only phase first")
    sm=json.loads(SCORE_MANIFEST.read_text(encoding="utf-8"))
    if sm["predictions_sha256"] != sha(PRED): raise RuntimeError("prediction hash mismatch")
    pred=pd.read_csv(PRED,dtype={"id":str})
    if {"target_label","group_id"} & set(pred.columns): raise ValueError("labels in frozen predictions")
    lock=json.loads(LOCK.read_text(encoding="utf-8"))
    # First test target/group projection occurs here, after the prediction hash check.
    test=pd.read_parquet(ext3.SOURCE/"inputs.parquet",
        columns=["split","dataset","id","target_label","group_id"],
        filters=[("split","==","test")],engine="pyarrow")
    if set(test.split.astype(str)) != {"test"} or test.group_id.isna().any():
        raise ValueError("test label/group integrity failure")
    if set(test.target_label.astype(int).unique()) != {0,1}:
        raise ValueError("test target label classes invalid")
    results={"phase":"labels_evaluated_after_frozen_predictions",
        "bootstrap_draws":DRAWS,"bootstrap_seed":BOOT_SEED,"datasets":{}}
    holm=[]
    for ds in DATASETS:
        t=test[test.dataset==ds].copy()
        p=pred[pred.dataset==ds].copy()
        if len(t)!=EXPECTED_N[ds] or len(p)!=EXPECTED_N[ds]:
            raise ValueError(f"{ds}: test census mismatch")
        t["id"]=t.id.astype(str)
        if t.id.duplicated().any() or p.id.duplicated().any():
            raise ValueError(f"{ds}: duplicate test IDs")
        z=t.merge(p,on=["dataset","id"],how="outer",validate="one_to_one",indicator=True)
        if not z._merge.eq("both").all(): raise ValueError(f"{ds}: ID join mismatch")
        z=z.drop(columns="_merge").sort_values("id").reset_index(drop=True)
        y=z.target_label.to_numpy(np.int8); g=z.group_id.astype(str).to_numpy()
        tau=float(lock["datasets"][ds]["P_pre_tau"])
        arms={a:z[f"arm_{a}"].to_numpy(float) for a in ext20.ARMS}
        pre=z.P_pre.to_numpy(float); post=z.P_post.to_numpy(float)
        models={"P_pre":pre,"P_post":post,**{f"arm_{a}":v for a,v in arms.items()}}
        metrics={k:metric(y,v,tau) for k,v in models.items()}
        refs={"P_pre":pre,"B2":arms["B2"],**arms}
        draws={k:{"AP":[],"AUROC":[],"MCC":[]} for k in refs}
        valid=0
        for w in ext5.group_draws(g,DRAWS,BOOT_SEED):
            ix=ext5.idx_from_weights(w)
            if not len(ix) or np.unique(y[ix]).size<2: continue
            valid+=1
            ap=average_precision_score(y[ix],post[ix])
            auc=roc_auc_score(y[ix],post[ix])
            mcc=matthews_corrcoef(y[ix],post[ix]>=tau)
            for k,ref in refs.items():
                draws[k]["AP"].append(ap-average_precision_score(y[ix],ref[ix]))
                draws[k]["AUROC"].append(auc-roc_auc_score(y[ix],ref[ix]))
                draws[k]["MCC"].append(mcc-matthews_corrcoef(y[ix],ref[ix]>=tau))
        if valid < int(DRAWS*.99): raise RuntimeError(f"{ds}: insufficient valid bootstrap draws")
        comps={}
        for k, vals in draws.items():
            metric_ref="P_pre" if k=="P_pre" else f"arm_{k}"
            comps[k]={m:{"delta":float(metrics["P_post"][m]-metrics[metric_ref][m]),
                         "CI95":ci(vals[m]),"bootstrap_p_two_sided":p_two_sided(vals[m])}
                      for m in ("AP","AUROC","MCC")}
            if k not in ("P_pre","B2"): holm.append((ds,k,comps[k]["AP"]["bootstrap_p_two_sided"]))
        primary=comps["P_pre"]["MCC"]
        result={"n":len(y),"groups":int(pd.Series(g).nunique()),
            "threshold_shared_from_validation":tau,"metrics":metrics,
            "comparisons_P_post_minus":comps,"valid_bootstrap_draws":valid,
            "MCC_rule_point_gt_0_02_and_positive_CI":
                bool(primary["delta"]>.02 and primary["CI95"][0]>0),
            "classification":"exploratory_test_extension"}
        results["datasets"][ds]=result
        print(f"labels evaluated after freeze: {ds}; groups={result['groups']}",flush=True)
    adj=ext16.holm([x[2] for x in holm])
    for (ds,arm,_),p in zip(holm,adj):
        a=results["datasets"][ds]["comparisons_P_post_minus"][arm]["AP"]
        a["p_holm_30"]=float(p)
        a["holm_pass"]=bool(p<.05 and a["CI95"][0]>0)
    results["AP_Holm_family_size"]=len(holm)
    results["test_exposure_caveat"]=(
        "This benchmark test split appeared in earlier exploratory candidate analyses; "
        "results are not independent confirmatory evidence.")
    atomic_json(RESULTS,safe(results))
    lines=["# Ext20 test extension results","",
        "Exploratory: the benchmark test split appeared in earlier candidate analyses.",
        "Models and threshold were locked on validation before test predictions were frozen.",
        "MCC uses the validation-locked P_pre threshold shared by P_pre, P_post, and arms.",""]
    for ds in DATASETS:
        d=results["datasets"][ds]; c=d["comparisons_P_post_minus"]
        lines += [f"## {ds}",
            f"n={d['n']}; groups={d['groups']}; threshold={d['threshold_shared_from_validation']:.2f}.",
            f"P_pre: AP={d['metrics']['P_pre']['AP']:.6f}, AUROC={d['metrics']['P_pre']['AUROC']:.6f}, MCC={d['metrics']['P_pre']['MCC']:.6f}.",
            f"P_post: AP={d['metrics']['P_post']['AP']:.6f}, AUROC={d['metrics']['P_post']['AUROC']:.6f}, MCC={d['metrics']['P_post']['MCC']:.6f}.",
            f"Δ P_post−P_pre: AP={c['P_pre']['AP']['delta']:+.6f} CI {c['P_pre']['AP']['CI95']}; AUROC={c['P_pre']['AUROC']['delta']:+.6f} CI {c['P_pre']['AUROC']['CI95']}; MCC={c['P_pre']['MCC']['delta']:+.6f} CI {c['P_pre']['MCC']['CI95']}.",
            f"Δ P_post−B2: AP={c['B2']['AP']['delta']:+.6f} CI {c['B2']['AP']['CI95']}; AUROC={c['B2']['AUROC']['delta']:+.6f} CI {c['B2']['AUROC']['CI95']}; MCC={c['B2']['MCC']['delta']:+.6f} CI {c['B2']['MCC']['CI95']}.",
            f"ΔMCC rule (mean > +0.02 and positive CI): {'PASS' if d['MCC_rule_point_gt_0_02_and_positive_CI'] else 'FAIL'}.",""]
    lines += ["## P_post vs 15 raw arms","","Paired group-bootstrap AP; Holm correction across 30 cohort-arm comparisons.",""]
    for ds in DATASETS:
        lines.append(f"### {ds}")
        for arm in ext20.ARMS:
            a=results["datasets"][ds]["comparisons_P_post_minus"][arm]["AP"]
            lines.append(f"- {arm}: ΔAP={a['delta']:+.6f}, CI {a['CI95']}, Holm p={a['p_holm_30']:.6g}, gate={'PASS' if a['holm_pass'] else 'FAIL'}.")
        lines.append("")
    REPORT.write_text("\n".join(lines)+"\n",encoding="utf-8")
    atomic_json(OUT/"evaluation_manifest.json",{
        "phase":"completed_after_score_freeze","prediction_sha256":sha(PRED),
        "metrics_sha256":sha(RESULTS),"report_sha256":sha(REPORT),
        "bootstrap_draws":DRAWS,"bootstrap_seed":BOOT_SEED,
        "test_labels_loaded_after_predictions_frozen":True,
        "classification":"exploratory_test_extension"})
    print(json.dumps({"state":"evaluation_completed","results":str(RESULTS),
                      "report":str(REPORT)},indent=2))


def make_rank_plan(scores):
    order = np.argsort(-np.asarray(scores, dtype=float), kind="mergesort")
    s = np.asarray(scores, dtype=float)[order]
    starts = np.r_[0, np.flatnonzero(s[1:] != s[:-1]) + 1]
    return order, starts


def weighted_rank_metrics(y, weights, plan):
    order, starts = plan
    ys = y[order].astype(float)
    ws = weights[order].astype(float)
    pos_group = np.add.reduceat(ws * ys, starts)
    neg_group = np.add.reduceat(ws * (1.0 - ys), starts)
    total_pos, total_neg = float(pos_group.sum()), float(neg_group.sum())
    if total_pos <= 0 or total_neg <= 0:
        return float("nan"), float("nan")
    tp = np.cumsum(pos_group)
    total = np.cumsum(pos_group + neg_group)
    contributes = pos_group > 0
    ap = float(np.sum((pos_group[contributes] / total_pos)
                      * (tp[contributes] / total[contributes])))
    neg_after = total_neg - np.cumsum(neg_group)
    auc = float(np.sum(pos_group * (neg_after + 0.5 * neg_group))
                / (total_pos * total_neg))
    return ap, auc


def weighted_mcc(y, scores, weights, tau):
    decision = np.asarray(scores) >= tau
    tp = float(np.sum(weights[(y == 1) & decision]))
    fp = float(np.sum(weights[(y == 0) & decision]))
    fn = float(np.sum(weights[(y == 1) & ~decision]))
    tn = float(np.sum(weights[(y == 0) & ~decision]))
    denom = np.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    return float((tp * tn - fp * fn) / denom) if denom > 0 else 0.0


def evaluate_weighted():
    if not PRED.is_file() or not LOCK.is_file() or not SCORE_MANIFEST.is_file():
        raise FileNotFoundError("run score-only phase first")
    sm = json.loads(SCORE_MANIFEST.read_text(encoding="utf-8"))
    if sm["predictions_sha256"] != sha(PRED):
        raise RuntimeError("prediction hash mismatch")
    pred = pd.read_csv(PRED, dtype={"id":str})
    if {"target_label","group_id"} & set(pred.columns):
        raise ValueError("labels in frozen predictions")
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    # First test target/group projection occurs after the prediction hash check.
    test = pd.read_parquet(ext3.SOURCE/"inputs.parquet",
        columns=["split","dataset","id","target_label","group_id"],
        filters=[("split","==","test")], engine="pyarrow")
    if set(test.split.astype(str)) != {"test"} or test.group_id.isna().any():
        raise ValueError("test label/group integrity failure")
    if set(test.target_label.astype(int).unique()) != {0,1}:
        raise ValueError("test target label classes invalid")

    results = {"phase":"labels_evaluated_after_frozen_predictions",
        "bootstrap_draws":DRAWS,"bootstrap_seed":BOOT_SEED,"datasets":{},
        "pre_run_data_access_deviation":ACCESS_DEVIATION}
    holm = []
    for ds in DATASETS:
        t = test[test.dataset==ds].copy()
        p = pred[pred.dataset==ds].copy()
        if len(t)!=EXPECTED_N[ds] or len(p)!=EXPECTED_N[ds]:
            raise ValueError(f"{ds}: test census mismatch")
        t["id"] = t.id.astype(str)
        if t.id.duplicated().any() or p.id.duplicated().any():
            raise ValueError(f"{ds}: duplicate test IDs")
        z = t.merge(p,on=["dataset","id"],how="outer",validate="one_to_one",indicator=True)
        if not z._merge.eq("both").all():
            raise ValueError(f"{ds}: prediction/label ID join mismatch")
        z = z.drop(columns="_merge").sort_values("id").reset_index(drop=True)
        y = z.target_label.to_numpy(np.int8)
        groups = z.group_id.astype(str).to_numpy()
        tau = float(lock["datasets"][ds]["P_pre_tau"])
        arms = {a:z[f"arm_{a}"].to_numpy(float) for a in ext20.ARMS}
        ppre, ppost = z.P_pre.to_numpy(float), z.P_post.to_numpy(float)
        metrics_by_name = {"P_pre":ppre,"P_post":ppost,**{f"arm_{a}":v for a,v in arms.items()}}
        metrics = {k:metric(y,v,tau) for k,v in metrics_by_name.items()}

        # AP is bootstrapped against P_pre and all 15 raw arms; AUC/MCC are
        # needed for the two headline comparisons P_post-P_pre and P_post-B2.
        ap_refs = {"P_pre":ppre, **arms}
        ap_plans = {k:make_rank_plan(v) for k,v in {"P_post":ppost,**ap_refs}.items()}
        direct = {"P_pre":ppre,"B2":arms["B2"]}
        direct_plans = {k:make_rank_plan(v) for k,v in direct.items()}
        ap_draws = {k:[] for k in ap_refs}
        auc_draws = {k:[] for k in direct}
        mcc_draws = {k:[] for k in direct}
        valid = 0
        sanity_checked = False
        for weights in ext5.group_draws(groups,DRAWS,BOOT_SEED):
            weights = np.asarray(weights,dtype=np.int64)
            if weights.shape != y.shape:
                raise ValueError("group bootstrap weight vector has wrong shape")
            pos_n = int(np.sum(weights[y==1]))
            neg_n = int(np.sum(weights[y==0]))
            if pos_n == 0 or neg_n == 0:
                continue
            valid += 1
            post_ap, post_auc = weighted_rank_metrics(y,weights,ap_plans["P_post"])
            post_mcc = weighted_mcc(y,ppost,weights,tau)
            if not sanity_checked:
                ix = ext5.idx_from_weights(weights)
                for k,score in (("P_post",ppost),("P_pre",ppre),("B2",arms["B2"])):
                    fast_ap,fast_auc = weighted_rank_metrics(y,weights,ap_plans[k])
                    ref_ap = average_precision_score(y[ix],score[ix])
                    ref_auc = roc_auc_score(y[ix],score[ix])
                    if abs(fast_ap-ref_ap)>1e-12 or abs(fast_auc-ref_auc)>1e-12:
                        raise RuntimeError(f"weighted bootstrap parity failed for {k}: "
                            f"AP {fast_ap} vs {ref_ap}; AUROC {fast_auc} vs {ref_auc}")
                ref_mcc = matthews_corrcoef(y[ix],ppost[ix]>=tau)
                if abs(post_mcc-ref_mcc)>1e-12:
                    raise RuntimeError("weighted MCC parity assertion failed")
                sanity_checked = True
            for k in ap_refs:
                ref_ap,_ = weighted_rank_metrics(y,weights,ap_plans[k])
                ap_draws[k].append(post_ap-ref_ap)
            for k,ref in direct.items():
                _,ref_auc = weighted_rank_metrics(y,weights,direct_plans[k])
                auc_draws[k].append(post_auc-ref_auc)
                mcc_draws[k].append(
                    post_mcc-weighted_mcc(y,ref,weights,tau))
        if valid < int(DRAWS*.99) or not sanity_checked:
            raise RuntimeError(f"{ds}: insufficient valid bootstrap draws ({valid})")

        comparisons = {}
        for k in ap_refs:
            ref_name = "P_pre" if k=="P_pre" else f"arm_{k}"
            ap_delta = metrics["P_post"]["AP"] - metrics[ref_name]["AP"]
            ap_result = {"delta":float(ap_delta),"CI95":ci(ap_draws[k]),
                         "bootstrap_p_two_sided":p_two_sided(ap_draws[k])}
            comparisons[k] = {"AP":ap_result}
            if k in direct:
                auc_delta = metrics["P_post"]["AUROC"] - metrics[ref_name]["AUROC"]
                mcc_delta = metrics["P_post"]["MCC"] - metrics[ref_name]["MCC"]
                comparisons[k]["AUROC"] = {"delta":float(auc_delta),
                    "CI95":ci(auc_draws[k]),"bootstrap_p_two_sided":p_two_sided(auc_draws[k])}
                comparisons[k]["MCC"] = {"delta":float(mcc_delta),
                    "CI95":ci(mcc_draws[k]),"bootstrap_p_two_sided":p_two_sided(mcc_draws[k])}
            if k != "P_pre":
                holm.append((ds,k,ap_result["bootstrap_p_two_sided"]))
        primary = comparisons["P_pre"]["MCC"]
        results["datasets"][ds] = {
            "n":len(y),"groups":int(pd.Series(groups).nunique()),
            "threshold_shared_from_validation":tau,"metrics":metrics,
            "comparisons_P_post_minus":comparisons,"valid_bootstrap_draws":valid,
            "MCC_rule_point_gt_0_02_and_positive_CI":
                bool(primary["delta"]>.02 and primary["CI95"][0]>0),
            "classification":"exploratory_test_extension"}
        print(f"labels evaluated after freeze: {ds}; groups={results['datasets'][ds]['groups']}",
              flush=True)

    adjusted = ext16.holm([x[2] for x in holm])
    for (ds,arm,_),pval in zip(holm,adjusted):
        a = results["datasets"][ds]["comparisons_P_post_minus"][arm]["AP"]
        a["p_holm_30"] = float(pval)
        a["holm_pass"] = bool(pval<.05 and a["CI95"][0]>0)
    results["AP_Holm_family_size"] = len(holm)
    results["test_exposure_caveat"] = (
        "This benchmark test split appeared in earlier exploratory candidate analyses; "
        "results are not independent confirmatory evidence.")
    atomic_json(RESULTS,safe(results))
    lines = ["# Ext20 test extension results","",
        "Exploratory: this benchmark test split appeared in earlier candidate analyses.",
        "Data-access note: a pre-run schema/count audit deserialized label fields in test JSONL records before prediction freeze; those values were not inspected or used.",
        "Models and threshold were locked on validation before test predictions were frozen.",
        "MCC uses the validation-locked P_pre threshold shared by P_pre, P_post, and arms.",""]
    for ds in DATASETS:
        d=results["datasets"][ds]; c=d["comparisons_P_post_minus"]
        lines += [f"## {ds}",
            f"n={d['n']}; groups={d['groups']}; threshold={d['threshold_shared_from_validation']:.2f}.",
            f"P_pre: AP={d['metrics']['P_pre']['AP']:.6f}, AUROC={d['metrics']['P_pre']['AUROC']:.6f}, MCC={d['metrics']['P_pre']['MCC']:.6f}.",
            f"P_post: AP={d['metrics']['P_post']['AP']:.6f}, AUROC={d['metrics']['P_post']['AUROC']:.6f}, MCC={d['metrics']['P_post']['MCC']:.6f}.",
            f"Δ P_post−P_pre: AP={c['P_pre']['AP']['delta']:+.6f} CI {c['P_pre']['AP']['CI95']}; AUROC={c['P_pre']['AUROC']['delta']:+.6f} CI {c['P_pre']['AUROC']['CI95']}; MCC={c['P_pre']['MCC']['delta']:+.6f} CI {c['P_pre']['MCC']['CI95']}.",
            f"Δ P_post−B2: AP={c['B2']['AP']['delta']:+.6f} CI {c['B2']['AP']['CI95']}; AUROC={c['B2']['AUROC']['delta']:+.6f} CI {c['B2']['AUROC']['CI95']}; MCC={c['B2']['MCC']['delta']:+.6f} CI {c['B2']['MCC']['CI95']}.",
            f"ΔMCC rule (mean > +0.02 and positive CI): {'PASS' if d['MCC_rule_point_gt_0_02_and_positive_CI'] else 'FAIL'}.",""]
    lines += ["## P_post vs 15 raw arms","","Paired group-bootstrap AP; Holm correction across 30 cohort-arm comparisons.",""]
    for ds in DATASETS:
        lines.append(f"### {ds}")
        for arm in ext20.ARMS:
            a=results["datasets"][ds]["comparisons_P_post_minus"][arm]["AP"]
            lines.append(f"- {arm}: ΔAP={a['delta']:+.6f}, CI {a['CI95']}, Holm p={a['p_holm_30']:.6g}, gate={'PASS' if a['holm_pass'] else 'FAIL'}.")
        lines.append("")
    REPORT.write_text("\n".join(lines)+"\n",encoding="utf-8")
    atomic_json(OUT/"evaluation_manifest.json",{
        "phase":"completed_after_score_freeze","prediction_sha256":sha(PRED),
        "metrics_sha256":sha(RESULTS),"report_sha256":sha(REPORT),
        "bootstrap_draws":DRAWS,"bootstrap_seed":BOOT_SEED,
        "test_labels_loaded_after_predictions_frozen":True,
        "pre_run_data_access_deviation":ACCESS_DEVIATION,
        "test_classification":"exploratory_test_extension"})
    print(json.dumps({"state":"evaluation_completed","results":str(RESULTS),
                      "report":str(REPORT)},indent=2))
if __name__ == "__main__":
    if "--score-only" in sys.argv: score_only()
    elif "--evaluate-test-labels" in sys.argv: evaluate_weighted()
    else: raise SystemExit("Use --score-only or --evaluate-test-labels")
