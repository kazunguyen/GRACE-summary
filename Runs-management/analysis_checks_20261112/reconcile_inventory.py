"""Inventory and reconciliation of every test records file behind the published metrics.

For each (arm, seed, dataset) it records the canonical records path, raw and LF-normalised SHA-256,
N, census match with the frozen test manifest, score-valid and raw-invalid counts, AUROC and AUPRC
(labels from the frozen manifest), and compares them with the values printed in the metric report
`worklogs/2026-11-07_bao_cao_metric_cac_arm_hoan_tat.md` (table 1.3).

It also reproduces the figures that drifted between the 05/11 summary
(`docs/TONG_HOP_VAN_DE_CONTRASTIVE_ICL_VA_TIEN_DO_OSF.md`) and the 08/11 report, and lists superseded
B1-full records files that must not be used.

Usage: python reconcile_inventory.py --out <dir>
"""

import argparse
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "docs/20261111/grace_diag_kit.zip") + "/grace_diag_kit/src")
from grace_diag import stats  # noqa: E402

REPORT = "worklogs/2026-11-07_bao_cao_metric_cac_arm_hoan_tat.md"
B2_OLD = "01_Author_Baseline_Unified/output/local_full/inference_qwen_q4_b2_20261101/grace_b2_four_split_8h/{ds}/test/records.jsonl"
B1FULL_STALE = "Runs-management/kernel_outputs_harvest/huuhieu3333_grace-b1-full-test/b1_full_test/seed_42/{ds}/test/records.jsonl"


def canonical_paths():
    status = json.loads((ROOT / "Runs-management/current_status.json").read_text(encoding="utf-8"))
    paths = {}
    for arm in status["arms"]:
        if arm["arm"] in ("B0", "B1", "B2", "B2-flip"):
            for sp in arm["splits"]:
                if sp["split"] == "test":
                    paths[arm["arm"], 42, sp["dataset"]] = sp["records_path"]
    handoff = "Runs-management/run_handoff_20261108/completed_results"
    k11 = "Runs-management/kaggle_outputs_20261111"
    for ds in ("devign", "reveal"):
        for arm in ("B2-rep", "B2-nolabel", "B2-labelonly"):
            paths[arm, 42, ds] = f"{handoff}/{arm}/seed_42/{ds}/test/records.jsonl"
        for seed in (42, 43, 44):
            paths["B2-rand", seed, ds] = f"06_Arm_B2_Rand/test_results_20261107/seed_{seed}/{ds}/test/records.jsonl"
            paths["B1-shuf", seed, ds] = (f"Runs-management/b1_shuf_kaggle_output_20261109/b1_shuf_locked_20261108/"
                                          f"B1-shuf/seed_{seed}/{ds}/test/records.jsonl")
        paths["B1-full", 42, ds] = f"{handoff}/b1_full_test_completed_20261108/B1-full/seed_42/{ds}/test/records.jsonl"
        paths["B1-H2", 42, ds] = f"Runs-management/kaggle_outputs_20261107/b1h2_test_latest/b1_h2_test/seed_42/{ds}/test/records.jsonl"
        paths["B3", 42, ds] = f"{k11}/b3_verified_patch_test_10h/b3_test_release_20261110/seed_42/{ds}/test/records.jsonl"
        paths["B3-nodiff", 42, ds] = (f"Runs-management/kaggle_outputs_20261110/b3_nodiff_test_runtime_locked/b3_nodiff_test/"
                                      f"{ds}/seed_42/{ds}/test/records.jsonl")
        paths["B3-swap", 42, ds] = f"{k11}/b3_swap_test_resume_latest/b3_swap_test_release_20261110/seed_42/{ds}/test/records.jsonl"
        paths["B3-flip", 42, ds] = f"{k11}/b3_flip_test_20261110_v1/b3_flip_test_release_20261110/seed_42/{ds}/test/records.jsonl"
    return paths


def report_table():
    """Parse table 1.3 of the metric report: (dataset, arm label) -> numbers."""
    out = {}
    text = (ROOT / REPORT).read_text(encoding="utf-8")
    section = text.split("### 1.3.")[1].split("### 1.4.")[0]
    num = lambda x: float(x.replace(".", "").replace(",", "."))  # noqa: E731
    for line in section.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 12 and cells[0] in ("Devign", "ReVeal"):
            out[cells[0].lower(), cells[1]] = dict(n=num(cells[2]), raw_invalid=num(cells[3]), mcc=num(cells[4]),
                                                    auroc=num(cells[5]), auprc=num(cells[6]))
    return out


def evaluate(path, labels):
    raw = (ROOT / path).read_bytes()
    records = {}
    for line in raw.decode("utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            records[str(r["id"])] = r
    ids = sorted(labels)
    census = set(records) == set(labels)
    common = [i for i in ids if i in records]
    usable = [i for i in common if records[i].get("valid", True) and not records[i].get("s_bounded")]
    y = np.array([labels[i] for i in usable])
    s = np.array([float(records[i]["s"]) for i in usable])
    label_mismatch = sum(1 for i in common if "label" in records[i] and int(records[i]["label"]) != labels[i])
    return dict(sha256_raw=hashlib.sha256(raw).hexdigest(),
                sha256_lf=hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest(),
                n_records=len(records), census_match=census, n_score_valid=len(usable),
                n_raw_invalid=sum(1 for i in common if records[i].get("response_valid") is False),
                label_mismatch=label_mismatch,
                auroc=stats.auroc(y, s) if len(set(y)) == 2 else float("nan"),
                auprc=stats.auprc(y, s) if len(set(y)) == 2 else float("nan"),
                runtime_hashes=len({r.get("runtime_contract_sha256") for r in records.values()
                                    if r.get("runtime_contract_sha256")})), records


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, required=True)
    out = parser.parse_args().out
    out.mkdir(parents=True, exist_ok=True)
    labels = {}
    for ds in ("devign", "reveal"):
        man = f"01_Author_Baseline_Unified/output/research_freeze_20261101/{ds}/test_manifest.jsonl"
        labels[ds] = {str(json.loads(l)["id"]): int(json.loads(l)["label"])
                      for l in (ROOT / man).read_text(encoding="utf-8").splitlines() if l.strip()}
    published = report_table()

    rows = []
    for (arm, seed, ds), path in sorted(canonical_paths().items(), key=lambda x: (x[0][2], x[0][0], x[0][1])):
        if not (ROOT / path).exists():
            rows.append(dict(dataset=ds, arm=arm, seed=seed, records_path=path, status="MISSING"))
            continue
        info, _ = evaluate(path, labels[ds])
        label = arm if arm not in ("B2-rand", "B1-shuf") else f"{arm} s{seed}"
        pub = published.get((ds, label))
        row = dict(dataset=ds, arm=arm, seed=seed, records_path=path, **info)
        if pub:
            row.update(report_n=pub["n"], report_raw_invalid=pub["raw_invalid"], report_auroc=pub["auroc"],
                       report_auprc=pub["auprc"])
            ok = (abs(info["auroc"] - pub["auroc"]) < 5e-5 and abs(info["auprc"] - pub["auprc"]) < 5e-5
                  and info["n_records"] == pub["n"] and info["n_raw_invalid"] == pub["raw_invalid"])
            row["status"] = "MATCH_REPORT" if ok else "DIFFERS_FROM_REPORT"
        else:
            row["status"] = "NOT_IN_REPORT_TABLE_1_3"
        rows.append(row)
    fields = sorted({k for r in rows for k in r}, key=lambda k: list(rows[0]).index(k) if k in rows[0] else 99)
    with open(out / "inventory.csv", "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    drift = []
    for ds, tau in (("devign", 0.70), ("reveal", 0.12)):
        for name, path in (("superseded_pre_donor_rerun_20261101", B2_OLD.format(ds=ds)),
                           ("canonical_frozen_donor_20261102", canonical_paths()["B2", 42, ds])):
            info, records = evaluate(path, labels[ds])
            ids = sorted(labels[ds])
            y = np.array([labels[ds][i] for i in ids])
            s = np.array([float(records[i]["s"]) for i in ids])
            for t in (0.5, tau):
                m = stats.thresholded_metrics(y, (s >= t).astype(int))
                drift.append(dict(dataset=ds, arm="B2", records=name, sha256_lf=info["sha256_lf"], tau=t,
                                  auroc=info["auroc"], mcc=m["mcc"], balanced_accuracy=m["balanced_accuracy"],
                                  f1=m["f1"]))
    with open(out / "b2_snapshot_drift.csv", "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(drift[0]))
        writer.writeheader()
        writer.writerows(drift)

    b0 = {}
    for ds in ("devign", "reveal"):
        for split in ("validation", "test"):
            p = f"02_Arm_B0_Source_Only/output/kaggle_20261101_duchuynguyen1802/grace_b0_runs/{ds}/{split}/records.jsonl"
            if not (ROOT / p).exists():
                # B0 validation records are git-ignored; a fresh checkout only has the test files.
                b0[f"{ds}/{split}"] = dict(status="missing_untracked", path=p)
                continue
            recs = [json.loads(l) for l in (ROOT / p).read_text(encoding="utf-8").splitlines() if l.strip()]
            b0[f"{ds}/{split}"] = dict(n=len(recs), raw_invalid=sum(1 for r in recs if r.get("response_valid") is False),
                                       score_invalid=sum(1 for r in recs if not r.get("valid", True)))
    counted = [v for v in b0.values() if "raw_invalid" in v]
    b0["total_raw_invalid"] = sum(v["raw_invalid"] for v in counted)
    b0["all_four_splits_counted"] = len(counted) == 4

    old = B2_OLD.format(ds="devign")
    _, a = evaluate(old, labels["devign"])
    _, b = evaluate(canonical_paths()["B2", 42, "devign"], labels["devign"])
    changed = sorted(i for i in a if a[i].get("prompt_sha256") != b[i].get("prompt_sha256"))
    stale = {}
    for ds in ("devign", "reveal"):
        info, _ = evaluate(B1FULL_STALE.format(ds=ds), labels[ds])
        stale[ds] = dict(path=B1FULL_STALE.format(ds=ds), n_records=info["n_records"], auroc=info["auroc"],
                         sha256_lf=info["sha256_lf"])
    (out / "drift_explanations.json").write_text(json.dumps({
        "b0_raw_invalid_by_split": b0,
        "b2_devign_test_ids_with_new_prompt": len(changed),
        "b2_devign_changed_ids": changed,
        "b1_full_superseded_old_renderer_example": stale,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    bad = [r for r in rows if r.get("status") not in ("MATCH_REPORT", "NOT_IN_REPORT_TABLE_1_3")]
    print(f"{len(rows)} records files; {len(bad)} not matching the report")
    for r in bad:
        print(" ", r["dataset"], r["arm"], r["seed"], r["status"])


if __name__ == "__main__":
    main()
