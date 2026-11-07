"""
Independent verification and census check of all validation thresholds.
Strictly recalculates tau* from raw validation records using the pre-registered formula
and compares with registered thresholds on OSF (original and amendment).
"""
import sys
import json
import math
from pathlib import Path
import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]

def mcc(y, p):
    tp = float(((y == 1) & (p == 1)).sum())
    tn = float(((y == 0) & (p == 0)).sum())
    fp = float(((y == 0) & (p == 1)).sum())
    fn = float(((y == 1) & (p == 0)).sum())
    den = math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    return (tp * tn - fp * fn) / den if den > 0 else None

def balanced_accuracy(y, p):
    tp = ((y == 1) & (p == 1)).sum()
    tn = ((y == 0) & (p == 0)).sum()
    fp = ((y == 0) & (p == 1)).sum()
    fn = ((y == 1) & (p == 0)).sum()
    tpr = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    tnr = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    return (tpr + tnr) / 2.0

def f1_score(y, p):
    tp = ((y == 1) & (p == 1)).sum()
    fp = ((y == 0) & (p == 1)).sum()
    fn = ((y == 1) & (p == 0)).sum()
    den = 2 * tp + fp + fn
    return (2.0 * tp / den) if den > 0 else 0.0

def auroc(y, s):
    from scipy.stats import rankdata
    n1 = int(y.sum())
    n0 = len(y) - n1
    if n1 == 0 or n0 == 0:
        return None
    r = rankdata(s)
    return float((r[y == 1].sum() - n1 * (n1 + 1) / 2.0) / (n1 * n0))

def pick_threshold(y_val, s_val, grid=None):
    if grid is None:
        grid = [i / 100.0 for i in range(1, 100)]
    best_t = 0.5
    best_m = None
    all_grid = []
    for t in grid:
        pred = (s_val >= t).astype(int)
        val = mcc(y_val, pred)
        all_grid.append((t, val))
        if val is None:
            continue
        if best_m is None or val > best_m + 1e-9 or (abs(val - best_m) <= 1e-9 and (abs(t - 0.5), t) < (abs(best_t - 0.5), best_t)):
            best_t, best_m = t, val
    return best_t, best_m, all_grid

def load_records(path):
    rows = []
    seen = set()
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            uid = str(r["id"])
            if uid in seen:
                raise ValueError(f"Duplicate ID {uid} in {path}")
            seen.add(uid)
            rows.append(r)
    return rows

SOURCES = [
    # (Arm, Dataset, Seed, Path, Expected_N, Inherit_From)
    ("B0", "devign", 42, "02_Arm_B0_Source_Only/output/kaggle_20261101_duchuynguyen1802/grace_b0_runs/devign/validation/records.jsonl", 2732, None),
    ("B0", "reveal", 42, "02_Arm_B0_Source_Only/output/kaggle_20261101_duchuynguyen1802/grace_b0_runs/reveal/validation/records.jsonl", 2273, None),
    ("B1", "devign", 42, "03_Arm_B1_Graph_Only/output/kaggle_run_02/grace_b1_runs/devign/validation/records.jsonl", 2732, None),
    ("B1", "reveal", 42, "03_Arm_B1_Graph_Only/output/kaggle_run_02/grace_b1_runs/reveal/validation/records.jsonl", 2273, None),
    ("B1-H2", "devign", 42, "11_Arm_B1H2_Evidence/kaggle_b1h2_validation_20261106/downloaded_output/b1_h2_validation/seed_42/devign/validation/records.jsonl", 2732, None),
    ("B1-H2", "reveal", 42, "11_Arm_B1H2_Evidence/kaggle_b1h2_validation_20261106/downloaded_output/b1_h2_validation/seed_42/reveal/validation/records.jsonl", 2273, None),
    ("B2", "devign", 42, "runs/final/devign/validation/B2/42/records.jsonl", 2732, None),
    ("B2", "reveal", 42, "runs/final/reveal/validation/B2/42/records.jsonl", 2273, None),
    ("B2-rep", "devign", 42, "runs/final/devign/validation/B2-rep/42/records.jsonl", 2732, "B2"),
    ("B2-rep", "reveal", 42, "runs/final/reveal/validation/B2-rep/42/records.jsonl", 2273, "B2"),
    ("B2-rand", "devign", 42, "Runs-management/kaggle_outputs_20261107/b2_rand_latest/grace_b2_rand_three_seed_11h/seed_42/devign/validation/records.jsonl", 2732, None),
    ("B2-rand", "reveal", 42, "Runs-management/kaggle_outputs_20261107/b2_rand_latest/grace_b2_rand_three_seed_11h/seed_42/reveal/validation/records.jsonl", 2273, None),
    ("B2-rand", "devign", 43, "Runs-management/kaggle_outputs_20261107/b2_rand_latest/grace_b2_rand_three_seed_11h/seed_43/devign/validation/records.jsonl", 2732, None),
    ("B2-rand", "reveal", 43, "Runs-management/kaggle_outputs_20261107/b2_rand_latest/grace_b2_rand_three_seed_11h/seed_43/reveal/validation/records.jsonl", 2273, None),
    ("B1-shuf", "devign", 42, "runs/final/devign/validation/B1-shuf/42/records.jsonl", 2732, None),
    ("B1-shuf", "reveal", 42, "runs/final/reveal/validation/B1-shuf/42/records.jsonl", 2273, None),
    ("B1-shuf", "devign", 43, "runs/final/devign/validation/B1-shuf/43/records.jsonl", 2732, None),
    ("B1-shuf", "reveal", 43, "runs/final/reveal/validation/B1-shuf/43/records.jsonl", 2273, None),
    ("B1-shuf", "devign", 44, "runs/final/devign/validation/B1-shuf/44/records.jsonl", 2732, None),
    ("B1-shuf", "reveal", 44, "runs/final/reveal/validation/B1-shuf/44/records.jsonl", 2273, None),
    ("B1-full", "devign", 42, "runs/final/devign/validation/B1-full/42/records.jsonl", 2732, None),
    ("B1-full", "reveal", 42, "runs/final/reveal/validation/B1-full/42/records.jsonl", 2273, None),
    ("B2-nolabel", "devign", 42, "runs/final/devign/validation/B2-nolabel/42/records.jsonl", 2732, None),
    ("B2-nolabel", "reveal", 42, "runs/final/reveal/validation/B2-nolabel/42/records.jsonl", 2273, None),
    ("B2-labelonly", "devign", 42, "runs/final/devign/validation/B2-labelonly/42/records.jsonl", 2732, None),
    ("B2-labelonly", "reveal", 42, "runs/final/reveal/validation/B2-labelonly/42/records.jsonl", 2273, None),
]

def run_verification():
    # Load configs/thresholds.json
    cfg_thresh = {}
    cfg_p = ROOT / "configs/thresholds.json"
    if cfg_p.exists():
        cfg_data = json.loads(cfg_p.read_text(encoding="utf-8"))
        cfg_thresh = cfg_data.get("thresholds", {})

    print("=" * 100)
    print(f"{'Arm':<12} {'Dataset':<8} {'Seed':<5} {'N_rows':<8} {'N_valid':<8} {'tau*':<6} {'MCC':<8} {'AUROC':<8} {'BA(%)':<8} {'F1':<8} {'Inherit':<8} {'OSF_Orig':<9} {'OSF_Amend':<10}")
    print("=" * 100)

    results = []

    # Map of original OSF submitted thresholds
    osf_orig = {
        ("B0", "devign"): 0.08,
        ("B0", "reveal"): 0.44,
        ("B1", "devign"): 0.88,
        ("B1", "reveal"): 0.74,
        ("B2", "devign"): 0.70,
        ("B2", "reveal"): 0.12,
        ("B2-flip", "devign"): 0.70,
        ("B2-flip", "reveal"): 0.12,
        ("B2-rep", "devign"): 0.70,
        ("B2-rep", "reveal"): 0.12,
        ("P-PRE", "devign"): 0.54,
        ("P-PRE", "reveal"): 0.38,
        ("P-POST", "devign"): 0.60,
        ("P-POST", "reveal"): 0.10,
    }

    # Map of OSF amended thresholds (2026-11-06)
    osf_amend = {
        ("B0", "devign"): 0.98,
        ("B0", "reveal"): 0.30,
        ("B1", "devign"): 0.98,
        ("B1", "reveal"): 0.63,
        ("B1-H2", "devign"): 0.09,
        ("B1-H2", "reveal"): 0.21,
        ("B2", "devign"): 0.70,
        ("B2", "reveal"): 0.12,
        ("B2-flip", "devign"): 0.70,
        ("B2-flip", "reveal"): 0.12,
        ("B2-rep", "devign"): 0.70,
        ("B2-rep", "reveal"): 0.12,
        ("B2-rand", "devign", 42): 0.99,
        ("B2-rand", "reveal", 42): 0.89,
        ("B2-rand", "devign", 43): 0.99,
        ("B2-rand", "reveal", 43): 0.62,
    }

    for arm, ds, seed, rel_p, exp_n, inherit in SOURCES:
        full_p = ROOT / rel_p
        if not full_p.exists():
            print(f"MISSING: {full_p}")
            continue

        rows = load_records(full_p)
        n_rows = len(rows)
        valid_rows = [r for r in rows if r.get("valid") and r.get("s") is not None and math.isfinite(r["s"])]
        n_valid = len(valid_rows)

        y = np.array([r["label"] for r in valid_rows], dtype=int)
        s = np.array([r["s"] for r in valid_rows], dtype=float)

        tau_opt, mcc_opt, _ = pick_threshold(y, s)
        roc = auroc(y, s)
        
        # Determine actual tau according to protocol
        tau_used = tau_opt
        inherit_note = "-"
        if inherit == "B2":
            tau_used = 0.70 if ds == "devign" else 0.12
            inherit_note = f"B2({tau_used})"

        pred = (s >= tau_used).astype(int)
        mcc_used = mcc(y, pred)
        ba_used = balanced_accuracy(y, pred)
        f1_used = f1_score(y, pred)

        orig_val = osf_orig.get((arm, ds), "-")
        amend_val = osf_amend.get((arm, ds, seed), osf_amend.get((arm, ds), "-"))

        print(f"{arm:<12} {ds:<8} {seed:<5} {n_rows:<8} {n_valid:<8} {tau_used:<6.2f} {mcc_used:<8.4f} {roc:<8.4f} {ba_used*100:<8.2f} {f1_used:<8.4f} {inherit_note:<8} {str(orig_val):<9} {str(amend_val):<10}")

        results.append({
            "arm": arm, "dataset": ds, "seed": seed,
            "n_rows": n_rows, "n_valid": n_valid, "expected_n": exp_n,
            "tau_optimal": tau_opt, "mcc_optimal": mcc_opt,
            "tau_protocol": tau_used, "mcc_protocol": mcc_used,
            "auroc": roc, "balanced_acc": ba_used, "f1": f1_used,
            "inherit": inherit,
            "osf_original": orig_val,
            "osf_amendment": amend_val,
            "configs_thresholds": cfg_thresh.get(f"{ds}|{arm}|{seed}"),
        })

    print("=" * 100)
    out_file = ROOT / "Runs-management/verification_independent_all_thresholds.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nSaved independent verification result to: {out_file}")

if __name__ == "__main__":
    run_verification()
