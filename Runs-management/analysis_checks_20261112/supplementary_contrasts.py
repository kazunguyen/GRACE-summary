"""Supplementary paired analyses requested by the 11/11 progress assessment.

Reuses the loaders, cluster resampling (5,000 draws, seed 20261117) and kit statistics of
`Runs-management/analysis_pa1_20261111/recompute.py`, so every interval below shares the exact
resample indices of `full_tables/contrasts.csv`. Thresholds are the locked ones; nothing is refit.

Outputs (in --out):
  auprc_contrasts.csv      : Delta AUPRC with 95% CI for every PA1 pair plus B2 vs B2-nolabel.
  b2_vs_b2nolabel.csv      : Direct B2 - B2-nolabel contrast (AUROC, AUPRC, MCC at locked tau).
  ppr.csv                  : Predicted-positive rate per arm at s >= 0.5 and at the locked tau.
  b1h2_evidence_strata.csv : B1-H2 vs B1 inside the with/without H2 evidence strata (exploratory).
  provenance.json

Usage:
  python supplementary_contrasts.py --out <dir> [--recompute <path to recompute.py>]

--recompute defaults to the PA1 script. On a Windows CRLF checkout that script's raw-byte hash
checks for Step 6 inputs fail; pass a copy whose hash checks accept the LF-normalised bytes.
"""

import argparse
import csv
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
FALLBACK = "No guarded sink evidence detected."


def load_module(path):
    spec = importlib.util.spec_from_file_location("pa1_recompute", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_csv(path, rows):
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--recompute", type=Path, default=HERE.parent / "analysis_pa1_20261111" / "recompute.py")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    R = load_module(args.recompute)
    stats, ROOT = R.stats, R.ROOT

    audit = {R.KIT: hashlib.sha256((ROOT / R.KIT).read_bytes()).hexdigest()}
    status = R.load_json(f"{R.RUNS}/current_status.json", audit)
    core = {(sp["dataset"], arm["arm"]): sp["records_path"]
            for arm in status["arms"] if arm["arm"] in ("B0", "B1", "B2", "B2-flip")
            for sp in arm["splits"] if sp["split"] == "test"}
    frozen_raw = subprocess.check_output(["git", "show", "prereg-v1:configs/thresholds.json"], cwd=ROOT)
    audit["prereg-v1:configs/thresholds.json"] = hashlib.sha256(frozen_raw).hexdigest()
    frozen = json.loads(frozen_raw)["thresholds"]
    correction = R.load_json(f"{R.RUNS}/reanalysis_20261106/results.json", audit)["thresholds"]

    pairs = [(a, b, role) for a, b, _, _, role in R.PAIRS] + [("B2-nolabel", "B2", "supplementary_direct")]
    auprc_rows, nolabel_rows, ppr_rows, strata_rows = [], [], [], []

    for ds, n, k in [("devign", 2732, 2068), ("reveal", 2274, 646)]:
        labels, groups, clean, scores, thresholds, _ = R.load_dataset(ds, n, k, core, frozen, correction, audit)
        manifest_path = f"{R.AUTHOR}/output/research_freeze_20261101/{ds}/test_manifest.jsonl"
        ids = sorted(R.by_id(R.load_records(manifest_path, audit), ds))
        spec_path = f"data/specs/{ds}_test_15arms.jsonl"
        spec = R.by_id(R.load_records(spec_path, audit), spec_path)
        has_evidence = np.array([(spec[i].get("h2_evidence") or "").strip() not in ("", FALLBACK) for i in ids])

        for partition, include in [("full", np.ones(len(labels), dtype=bool)), ("no_exact_or_near_train", clean)]:
            ok = include & np.logical_and.reduce([np.isfinite(s) for s in scores.values()])
            if ok.sum() != include.sum():
                raise ValueError(f"{ds}/{partition}: incomplete exact score census")
            y, g = labels[ok], groups[ok]
            ix = R.resamples(g)
            s = {arm: v[ok] for arm, v in scores.items()}

            def boot(values, function, y=y, ix=ix):
                return function(y, values), np.array([function(y[i], values[i]) for i in ix], dtype=float)

            pr = {arm: boot(v, stats.auprc) for arm, v in s.items()}
            for a, b, role in pairs:
                (av, ad), (bv, bd) = pr[a], pr[b]
                ci = R.interval(bv - av, bd - ad)
                auprc_rows.append(dict(dataset=ds, partition=partition, arm_a=a, arm_b=b, comparison_role=role,
                                       metric="AUPRC", auprc_a=av, auprc_b=bv, delta=ci.delta, ci95_lo=ci.lo,
                                       ci95_hi=ci.hi, n_paired=int(ok.sum()), n_clusters=len(set(g)),
                                       n_degenerate=ci.n_degenerate))

            a, b = "B2-nolabel", "B2"
            ta, tb = thresholds[a]["registered_B0_B1"], thresholds[b]["registered_B0_B1"]
            for metric, (av, ad), (bv, bd), margin in [
                ("AUROC", boot(s[a], stats.auroc), boot(s[b], stats.auroc), 0.02),
                ("AUPRC", pr[a], pr[b], None),
                ("MCC", boot(s[a] >= ta, stats.mcc), boot(s[b] >= tb, stats.mcc), 0.03),
            ]:
                ci = R.interval(bv - av, bd - ad)
                nolabel_rows.append(dict(dataset=ds, partition=partition, arm_a=a, arm_b=b, metric=metric,
                                         tau_a=ta if metric == "MCC" else "", tau_b=tb if metric == "MCC" else "",
                                         value_a=av, value_b=bv, delta=ci.delta, ci95_lo=ci.lo, ci95_hi=ci.hi,
                                         margin=margin if margin is not None else "",
                                         interval_verdict=stats.verdict(ci, margin) if margin is not None else "",
                                         n_paired=int(ok.sum()), n_clusters=len(set(g))))

            for arm, v in s.items():
                for policy, tau in sorted(set(thresholds[arm].items()), key=lambda x: x[0]):
                    ppr_rows.append(dict(dataset=ds, partition=partition, arm=arm, threshold_policy=policy, tau=tau,
                                         ppr_at_tau=float((v >= tau).mean()), ppr_at_0_5=float((v >= 0.5).mean()),
                                         n=int(ok.sum())))

            if partition != "full":
                continue
            for stratum, mask in [("with_h2_evidence", has_evidence), ("without_h2_evidence", ~has_evidence)]:
                ys, gs = labels[mask], groups[mask]
                ixs = R.resamples(gs)
                for metric, function in [("AUROC", stats.auroc), ("AUPRC", stats.auprc)]:
                    av, ad = boot(scores["B1"][mask], function, ys, ixs)
                    bv, bd = boot(scores["B1-H2"][mask], function, ys, ixs)
                    ci = R.interval(bv - av, bd - ad)
                    strata_rows.append(dict(dataset=ds, stratum=stratum, arm_a="B1", arm_b="B1-H2", metric=metric,
                                            value_a=av, value_b=bv, delta=ci.delta, ci95_lo=ci.lo, ci95_hi=ci.hi,
                                            n=int(mask.sum()), n_positive=int(ys.sum()), n_clusters=len(set(gs)),
                                            ppr_0_5_b1=float((scores["B1"][mask] >= 0.5).mean()),
                                            ppr_0_5_b1h2=float((scores["B1-H2"][mask] >= 0.5).mean()),
                                            status="exploratory"))
        print(f"{ds}: done", flush=True)

    write_csv(args.out / "auprc_contrasts.csv", auprc_rows)
    write_csv(args.out / "b2_vs_b2nolabel.csv", nolabel_rows)
    write_csv(args.out / "ppr.csv", ppr_rows)
    write_csv(args.out / "b1h2_evidence_strata.csv", strata_rows)
    (args.out / "provenance.json").write_text(json.dumps({
        "n_boot": R.N_BOOT, "bootstrap_seed": R.BOOT_SEED, "headline_arm_seed": R.ARM_SEED,
        "delta_direction": "arm_b minus arm_a", "recompute_module": str(args.recompute.name),
        "inputs_sha256": audit,
        "notes": [
            "Resample indices are identical to analysis_pa1_20261111 for the full and clean partitions.",
            "AUPRC has no registered margin; only intervals are reported.",
            "B2 vs B2-nolabel is a supplementary direct contrast, outside the registered Holm family.",
            "Evidence strata use data/specs h2_evidence; the fallback sentence counts as missing evidence.",
            "Strata resample clusters within each stratum with the same seed; B1-H2 rows are exploratory.",
        ],
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
