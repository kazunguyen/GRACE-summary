"""Recompute the Phase 1 paired analyses from the existing local test records."""

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

import numpy as np


OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
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
PAIRS = [
    ("B0", "B2", 0.03, 0.02, "registered"),
    ("B0", "B1", 0.03, 0.02, "registered"),
    ("B1-shuf", "B1", 0.03, 0.02, "registered"),
    ("B2-rand", "B2", 0.03, 0.02, "registered"),
    ("B1", "B2-nolabel", 0.03, 0.02, "registered"),
    ("B2", "B2-flip", 0.03, 0.02, "registered"),
    ("B2-labelonly", "B2", 0.03, 0.02, "registered"),
    ("B2", "SUP-LR", 0.15, 0.05, "registered"),
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
    write_csv(OUT / "contrasts.csv", contrasts)
    write_csv(OUT / "sensitivity.csv", sensitivity)
    (OUT / "provenance.json").write_text(json.dumps({
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
