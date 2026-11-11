"""Recompute the Phase 1 paired analyses from the existing local test records."""

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
KIT = "docs/20261111/grace_diag_kit.zip"
sys.path.insert(0, str(ROOT / KIT) + "/grace_diag_kit/src")
from grace_diag import stats


N_BOOT = 5000
BOOT_SEED = 20261117
ARM_SEED = 42
RUNS = "Runs-management"
AUTHOR = "01_Author_Baseline_Unified"
HANDOFF = f"{RUNS}/run_handoff_20261108/completed_results"
ANCHOR = "STEP6_supervised_anchors/runs/anchor/locked_step6_20261108"
STEP6 = "STEP6_supervised_anchors"
META_RUN = f"{STEP6}/runs/complementarity_step6/step6_lock_64fb2c99d904_44f00d19"
PAIRS = [
    ("B0", "B2", 0.03, 0.02, "registered"),
    ("B0", "B1", 0.03, 0.02, "registered"),
    ("B1-shuf", "B1", 0.03, 0.02, "registered"),
    ("B2-rand", "B2", 0.03, 0.02, "registered"),
    ("B1", "B2-nolabel", 0.03, 0.02, "registered"),
    ("B2", "B2-flip", 0.03, 0.02, "registered"),
    ("B2-labelonly", "B2", 0.03, 0.02, "registered"),
    ("B2", "SUP-LR", 0.15, 0.05, "registered"),
    ("B2", "B3", 0.03, 0.02, "registered_pair_exploratory_run"),
    ("B1", "B1-H2", 0.03, 0.02, "registered_pair_exploratory_run"),
    ("P-PRE", "P-POST", 0.02, 0.02, "registered"),
    ("B1", "B2", 0.03, 0.02, "gap_component"),
    ("B1", "B2-labelonly", 0.03, 0.02, "gap_component"),
]


def read_input(path, audit):
    raw = (ROOT / path).read_bytes()
    audit[path] = hashlib.sha256(raw).hexdigest()
    return raw.decode("utf-8-sig")


def load_json(path, audit):
    return json.loads(read_input(path, audit))


def load_records(path, audit):
    return [json.loads(line) for line in read_input(path, audit).splitlines() if line.strip()]


def load_csv(path, audit):
    return list(csv.DictReader(read_input(path, audit).splitlines()))


def by_id(rows, source):
    keyed = {r["id"]: r for r in rows}
    if len(keyed) != len(rows):
        raise ValueError(f"Duplicate IDs in {source}")
    return keyed


def load_meta_scores(ds, ids, labels, groups, audit):
    sys.path.insert(0, str(ROOT / STEP6 / "src"))
    import step6_complementarity as step6

    source = f"{STEP6}/src/step6_complementarity.py"
    audit[source] = hashlib.sha256((ROOT / source).read_bytes()).hexdigest()
    original = load_json(f"{META_RUN}/analysis_manifest.json", audit)
    result_path = f"{ds}/complementarity_step6.json"
    previous = load_json(f"{META_RUN}/{result_path}", audit)["p_pre_vs_p_post"]
    if audit[f"{META_RUN}/{result_path}"] != original["output_hashes"][result_path]:
        raise ValueError(f"Original Step 6 result hash mismatch: {ds}")
    inputs = []
    for split in ("validation", "test"):
        joined = f"{ds}/joined_{split}.csv"
        rows = load_csv(f"{META_RUN}/{joined}", audit)
        if audit[f"{META_RUN}/{joined}"] != original["output_hashes"][joined]:
            raise ValueError(f"Original Step 6 join hash mismatch: {ds}/{split}")
        h3b = original["inputs"][f"{ds}/{split}"]["h3b"]
        path = f"{STEP6}/{original['h3b_export_root']}/{h3b['xpre_path']}"
        audit[path] = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        if audit[path] != h3b["xpre_sha256"]:
            raise ValueError(f"Original Step 6 feature hash mismatch: {ds}/{split}")
        with np.load(ROOT / path, allow_pickle=False) as archive:
            pos = {str(i): n for n, i in enumerate(archive["ids"])}
            X = np.asarray(archive["X"][[pos[r["id"]] for r in rows]], dtype=np.float64)
        inputs.extend([X, np.array([int(r["y"]) for r in rows]),
                       np.array([float(r["s_llm"]) for r in rows]),
                       np.array([bool(int(r["valid"])) for r in rows]),
                       np.array([float(r["p_gate"]) for r in rows]),
                       np.array([r["group"] for r in rows])])
    keyed = by_id(rows, f"{META_RUN}/{joined}")
    if set(keyed) != set(ids) or any(
        (int(keyed[i]["y"]), keyed[i]["group"]) != (label, str(group))
        for i, label, group in zip(ids, labels, groups)
    ):
        raise ValueError(f"Step 6 test IDs, labels or clusters differ from paired-analysis inputs: {ds}")
    fitted = {}
    result = step6._fit_paired_meta(stats, *inputs, test_scores=fitted)
    taus = result["thresholds_selected_on_validation_oof"]
    for original_name in ("P_pre", "P_post"):
        if taus[original_name] != previous["thresholds_selected_on_validation_oof"][original_name]:
            raise ValueError(f"Step 6 OOF threshold was not reproduced: {ds}/{original_name}")
        for metric in ("mcc", "balanced_accuracy", "f1"):
            if not np.isclose(result["test"][original_name]["metrics"][metric],
                              previous["test"][original_name]["metrics"][metric], atol=1e-10, rtol=0):
                raise ValueError(f"Step 6 test metric was not reproduced: {ds}/{original_name}/{metric}")
        if not np.isclose(result["test"][original_name]["auroc"],
                          previous["test"][original_name]["auroc"], atol=1e-10, rtol=0):
            raise ValueError(f"Step 6 test AUROC was not reproduced: {ds}/{original_name}")
    pos = {r["id"]: n for n, r in enumerate(rows)}
    order = [pos[i] for i in ids]
    print(f"{ds}: Step 6 validation thresholds and test metrics reproduced", flush=True)
    return {k: v[order] for k, v in fitted.items()}, {"P-PRE": taus["P_pre"], "P-POST": taus["P_post"]}


def load_dataset(ds, expected_n, expected_groups, core, frozen, correction, audit):
    manifest = by_id(load_records(
        f"{AUTHOR}/output/research_freeze_20261101/{ds}/test_manifest.jsonl", audit
    ), ds)
    ids = sorted(manifest)
    if len(ids) != expected_n:
        raise ValueError(f"Unexpected {ds} census: {len(ids)}")
    labels = np.array([manifest[i]["label"] for i in ids])
    if ds == "devign":
        groups = [manifest[i].get("commit_id") or f"missing:{i}" for i in ids]
    else:
        raw = by_id(load_records(f"{AUTHOR}/output/local_full/reveal/raw/test.jsonl", audit), ds)
        canonical = load_csv(f"{RUNS}/step0_diagnostic/reveal/canonical_reveal_test.csv", audit)
        if set(raw) != set(ids) or any(raw[i]["target"] != manifest[i]["label"] for i in ids):
            raise ValueError("ReVeal raw labels or IDs differ from frozen manifest")
        groups = [str(raw[i]["source_id"]) for i in ids]
        if Counter(zip(groups, labels)) != Counter((r["group"], int(r["y"])) for r in canonical):
            raise ValueError("ReVeal group/label counts differ from the canonical inventory")
    if len(set(groups)) != expected_groups:
        raise ValueError(f"Unexpected number of clusters for {ds}: {len(set(groups))}")
    clean = np.array([not (manifest[i]["exact_train"] or manifest[i]["near_train"]) for i in ids])
    paths = {arm: core[ds, arm] for arm in ("B0", "B1", "B2", "B2-flip")}
    paths["B1-shuf"] = (
        f"{RUNS}/b1_shuf_kaggle_output_20261109/b1_shuf_locked_20261108/"
        f"B1-shuf/seed_42/{ds}/test/records.jsonl"
    )
    paths["B2-rand"] = f"06_Arm_B2_Rand/test_results_20261107/seed_42/{ds}/test/records.jsonl"
    for arm in ("B2-rep", "B2-nolabel", "B2-labelonly"):
        paths[arm] = f"{HANDOFF}/{arm}/seed_42/{ds}/test/records.jsonl"
    scores, thresholds, runtime = {}, {}, {}
    lock_paths = {
        "B1-shuf": "08_Arm_B1_Shuf/config/threshold.json",
        "B2-rand": "06_Arm_B2_Rand/config/threshold.json",
        "B2-nolabel": "10_Arm_B2_NoLabel/config/threshold.json",
        "B2-labelonly": "12_Arm_B2_LabelOnly/config/threshold.json",
    }
    for arm, path in paths.items():
        records = by_id(load_records(path, audit), path)
        if set(records) != set(ids):
            raise ValueError(f"Missing or extra test IDs in {path}")
        for i in ids:
            r = records[i]
            if (r["dataset"], r["split"], r["arm"], int(r.get("seed", ARM_SEED)), r["label"]) != (
                ds, "test", arm, ARM_SEED, manifest[i]["label"]
            ):
                raise ValueError(f"Record identity or label mismatch in {path}: {i}")
        scores[arm] = np.array([
            float(records[i]["s"]) if records[i]["valid"] and not records[i].get("s_bounded")
            else np.nan for i in ids
        ])
        if np.any((scores[arm] < 0) | (scores[arm] > 1)):
            raise ValueError(f"Out of range scores in {path}")
        runtime[arm] = dict(Counter(r.get("runtime_contract_sha256") or "not_in_record" for r in records.values()))
        key = f"{ds}|{arm}|{ARM_SEED}"
        if arm in lock_paths:
            lock = load_json(lock_paths[arm], audit)
            tau = float(lock["entries"][f"{arm}/{ARM_SEED}/{ds}"]["tau_star"])
        else:
            tau = float(frozen[key])
        thresholds[arm] = {
            "registered_B0_B1": tau,
            "corrected_B0_B1": float(correction.get(f"{ds}|{arm}", {}).get("tau", tau))
            if arm in ("B0", "B1") else tau,
        }
        if arm in lock_paths or arm == "B2-rep":
            for i, s in zip(ids, scores[arm]):
                r = records[i]
                if np.isfinite(s) and ("tau" in r and not np.isclose(float(r["tau"]), tau)
                    or "pred_tau" in r and int(r["pred_tau"]) != int(s >= tau)):
                    raise ValueError(f"Threshold or prediction mismatch in {path}: {i}")
    for probe in ("B2-flip", "B2-rep"):
        if thresholds[probe] != thresholds["B2"]:
            raise ValueError(f"{probe} does not inherit the B2 threshold")
    anchor_path = f"{ANCHOR}/{ds}/anchor_scores.csv"
    anchors = by_id([
        r for r in load_csv(anchor_path, audit)
        if r["dataset"] == ds and r["split"] == "test" and r["arm"] == "SUP-LR"
        and int(r["seed"]) == ARM_SEED
    ], anchor_path)
    if set(anchors) != set(ids):
        raise ValueError(f"Missing or extra anchor IDs in {anchor_path}")
    scores["SUP-LR"] = np.array([float(anchors[i]["score"]) for i in ids])
    summaries = load_json(f"{ANCHOR}/{ds}/anchor_summary.json", audit)
    anchor_tau, = [r["tau"] for r in summaries if r["arm"] == "SUP-LR" and r["seed"] == ARM_SEED]
    thresholds["SUP-LR"] = dict.fromkeys(("registered_B0_B1", "corrected_B0_B1"), float(anchor_tau))
    h2_lock = load_json(f"{RUNS}/b1h2_kaggle_validation_threshold_lock_20261106.json", audit)
    b3_lock = load_json(
        f"{RUNS}/b3_verified_patch_v1/threshold_release_20261109_v1/{ds}_threshold_lock.json", audit
    )
    for arm, base, tau, tau_key, pred_key in (
        ("B1-H2", f"{RUNS}/kaggle_outputs_20261107/b1h2_test_latest/b1_h2_test",
         float(h2_lock["results"][ds]["tau_star"]), "tau", "pred_tau"),
        ("B3", f"{RUNS}/kaggle_outputs_20261111/b3_verified_patch_test_10h/b3_test_release_20261110",
         float(b3_lock["tau_star"]), "threshold_tau", "threshold_prediction"),
    ):
        path = f"{base}/seed_42/{ds}/test/records.jsonl"
        records = by_id(load_records(path, audit), path)
        if set(records) != set(ids):
            raise ValueError(f"Missing or extra test IDs in {path}")
        values = []
        for i in ids:
            r = records[i]
            score = float(r["s"])
            if (str(r["dataset"]).lower(), r["split"], r["arm"], int(r["seed"])) != (ds, "test", arm, ARM_SEED):
                raise ValueError(f"Record identity mismatch in {path}: {i}")
            if "label" in r and int(r["label"]) != manifest[i]["label"]:
                raise ValueError(f"Label mismatch in {path}: {i}")
            if not r["valid"] or r.get("s_bounded") or not 0 <= score <= 1:
                raise ValueError(f"Unusable score in {path}: {i}")
            if not np.isclose(float(r[tau_key]), tau) or int(r[pred_key]) != int(score >= tau):
                raise ValueError(f"Locked threshold mismatch in {path}: {i}")
            values.append(score)
        scores[arm] = np.array(values)
        thresholds[arm] = dict.fromkeys(("registered_B0_B1", "corrected_B0_B1"), tau)
        runtime[arm] = dict(Counter(r.get("runtime_contract_sha256") or "not_in_record" for r in records.values()))
    meta_scores, meta_taus = load_meta_scores(ds, ids, labels, groups, audit)
    scores.update(meta_scores)
    for arm, tau in meta_taus.items():
        thresholds[arm] = dict.fromkeys(("registered_B0_B1", "corrected_B0_B1"), tau)
    return labels, np.array(groups), clean, scores, thresholds, runtime


def resamples(groups):
    """Use the kit's sorted cluster sampling with the membership lookup cached."""
    _, inv = np.unique(groups, return_inverse=True)
    members = [np.flatnonzero(inv == g) for g in range(int(inv.max()) + 1)]
    rng = np.random.default_rng(BOOT_SEED)
    return [
        np.concatenate([members[g] for g in rng.integers(0, len(members), len(members))])
        for _ in range(N_BOOT)
    ]


def interval(delta, draws):
    finite = draws[np.isfinite(draws)]
    lo, hi = np.percentile(finite, [2.5, 97.5]) if len(finite) else (np.nan, np.nan)
    return stats.PairedCI(float(delta), float(lo), float(hi), N_BOOT,
                          N_BOOT - len(finite), BOOT_SEED, "cluster")


def analyze(ds, labels, groups, clean, scores, thresholds):
    rows, sensitivity = [], []
    for partition, include in [("full", np.ones(len(labels), dtype=bool)), ("no_exact_or_near_train", clean)]:
        ok = include & np.logical_and.reduce([np.isfinite(s) for s in scores.values()])
        y, g = labels[ok], groups[ok]
        if ok.sum() != include.sum():
            raise ValueError(f"{ds}/{partition}: incomplete exact score census; review missing scores")
        ix = resamples(g)
        s = {arm: v[ok] for arm, v in scores.items()}
        preds = {(arm, tau): values >= tau for arm, values in s.items()
                 for tau in set(thresholds[arm].values())}

        def metrics(values, function):
            return function(y, values), np.array([function(y[i], values[i]) for i in ix], dtype=float)

        rank = {arm: metrics(values, stats.auroc) for arm, values in s.items()}
        mcc = {key: metrics(values, stats.mcc) for key, values in preds.items()}
        for a, b, mcc_margin, auc_margin, role in PAIRS:
            modes = ("registered_B0_B1", "corrected_B0_B1") if {"B0", "B1"} & {a, b} else ("unchanged",)
            for metric in ("AUROC", "MCC"):
                for mode in ("threshold_free",) if metric == "AUROC" else modes:
                    ta = thresholds[a].get(mode, thresholds[a]["registered_B0_B1"])
                    tb = thresholds[b].get(mode, thresholds[b]["registered_B0_B1"])
                    av, ad = rank[a] if metric == "AUROC" else mcc[a, ta]
                    bv, bd = rank[b] if metric == "AUROC" else mcc[b, tb]
                    draws = bd - ad
                    ci = interval(bv - av, draws)
                    margin = auc_margin if metric == "AUROC" else mcc_margin
                    row = dict(dataset=ds, partition=partition, arm_a=a, arm_b=b, seed=ARM_SEED,
                               comparison_role=role, metric=metric, threshold_policy=mode,
                               n_paired=int(ok.sum()), n_clusters=len(set(g)), delta=ci.delta,
                               ci95_lo=ci.lo, ci95_hi=ci.hi, margin=margin,
                               interval_verdict=stats.verdict(ci, margin),
                               n_degenerate=ci.n_degenerate)
                    if a == "B2-labelonly" and b == "B2" and metric == "AUROC":
                        row["abs_delta_ci95_upper"] = float(np.nanpercentile(np.abs(draws), 97.5))
                    if metric == "MCC":
                        mc = stats.mcnemar_test(y, preds[a, ta], preds[b, tb])
                        row.update(tau_a=ta, tau_b=tb, mcnemar_b=mc["b"], mcnemar_c=mc["c"],
                                   mcnemar_p=mc["p_value"], mcnemar_method=mc["method"])
                    rows.append(row)
        for mode, tau in [("locked_B2", thresholds["B2"]["registered_B0_B1"]), ("fixed_0.5", 0.5)]:
            pb, pf, pr = (s[arm] >= tau for arm in ("B2", "B2-flip", "B2-rep"))
            flip, repeat = pb != pf, pb != pr
            per_id = flip.astype(int) - repeat
            ci = interval(per_id.mean(), np.array([per_id[i].mean() for i in ix]))
            sensitivity.append(dict(dataset=ds, partition=partition, mode=mode, tau=tau,
                                    n_paired=len(y), n_clusters=len(set(g)),
                                    flip_changed=int(flip.sum()), repeat_changed=int(repeat.sum()),
                                    net=ci.delta, ci95_lo=ci.lo, ci95_hi=ci.hi))
    return rows, sensitivity


def write_csv(path, rows):
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    out = parser.parse_args().out
    out.mkdir(parents=True, exist_ok=True)
    audit = {KIT: hashlib.sha256((ROOT / KIT).read_bytes()).hexdigest()}
    status = load_json(f"{RUNS}/current_status.json", audit)
    core = {(sp["dataset"], arm["arm"]): sp["records_path"]
            for arm in status["arms"] if arm["arm"] in ("B0", "B1", "B2", "B2-flip")
            for sp in arm["splits"] if sp["split"] == "test"}
    frozen_raw = subprocess.check_output(
        ["git", "show", "prereg-v1:configs/thresholds.json"], cwd=ROOT
    )
    audit["prereg-v1:configs/thresholds.json"] = hashlib.sha256(frozen_raw).hexdigest()
    frozen = json.loads(frozen_raw)["thresholds"]
    correction = load_json(f"{RUNS}/reanalysis_20261106/results.json", audit)["thresholds"]
    contrasts, sensitivity, runtime = [], [], {}
    for ds, n, k in [("devign", 2732, 2068), ("reveal", 2274, 646)]:
        labels, groups, clean, scores, thresholds, runtime[ds] = load_dataset(
            ds, n, k, core, frozen, correction, audit
        )
        rows, sens = analyze(ds, labels, groups, clean, scores, thresholds)
        contrasts.extend(rows)
        sensitivity.extend(sens)
        print(f"{ds}: {n} IDs, {k} full-test clusters, {len(rows)} contrasts", flush=True)
    for partition in ("full", "no_exact_or_near_train"):
        for policy in ("registered_B0_B1", "corrected_B0_B1"):
            family = {i: r["mcnemar_p"] for i, r in enumerate(contrasts)
                      if r["partition"] == partition and r["metric"] == "MCC"
                      and r["comparison_role"] == "registered"
                      and r["threshold_policy"] in (policy, "unchanged")}
            for i, p in stats.holm(family).items():
                contrasts[i][f"mcnemar_p_holm_partial_{policy}"] = p
            available = {i: r["mcnemar_p"] for i, r in enumerate(contrasts)
                         if r["partition"] == partition and r["metric"] == "MCC"
                         and r["comparison_role"] in ("registered", "registered_pair_exploratory_run")
                         and r["threshold_policy"] in (policy, "unchanged")}
            for i, p in stats.holm(available).items():
                contrasts[i][f"mcnemar_p_holm_available_{policy}"] = p
    write_csv(out / "contrasts.csv", contrasts)
    write_csv(out / "sensitivity.csv", sensitivity)
    (out / "provenance.json").write_text(json.dumps({
        "n_boot": N_BOOT, "bootstrap_seed": BOOT_SEED, "headline_arm_seed": ARM_SEED,
        "delta_direction": "arm_b minus arm_a", "kit": KIT, "inputs_sha256": audit,
        "runtime_contract_sha256_counts": runtime,
        "notes": [
            "Retrospective analysis on existing test records, with fixed thresholds during resampling.",
            "Registered_B0_B1 refers to the original B0/B1 thresholds, not the exposure status of the contrast.",
            "Holm covers only the listed eligible MCC McNemar comparisons in each output family.",
            "B2 minus B2-rand follows the prose estimand; the frozen YAML lists the inverse order.",
        ],
    }, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
