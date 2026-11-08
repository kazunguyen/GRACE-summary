import sys
import json
from pathlib import Path
import numpy as np

# Load specs
devign_spec = [json.loads(line) for line in open('data/specs/devign_validation_15arms.jsonl', encoding='utf-8')]
reveal_spec = [json.loads(line) for line in open('data/specs/reveal_validation_15arms.jsonl', encoding='utf-8')]

devign_ids = [str(r['id']) for r in devign_spec]
reveal_ids = [str(r['id']) for r in reveal_spec]

devign_labels = {str(r['id']): int(r['label']) for r in devign_spec}
reveal_labels = {str(r['id']): int(r['label']) for r in reveal_spec}

print(f"Devign validation ground truth: N={len(devign_ids)}, pos={sum(devign_labels.values())} ({sum(devign_labels.values())/len(devign_ids)*100:.2f}%)")
print(f"ReVeal validation ground truth: N={len(reveal_ids)}, pos={sum(reveal_labels.values())} ({sum(reveal_labels.values())/len(reveal_ids)*100:.2f}%)")

arms_to_check = [
    ("B0", 
     "02_Arm_B0_Source_Only/output/kaggle_20261101_duchuynguyen1802/grace_b0_runs/devign/validation/records.jsonl",
     "02_Arm_B0_Source_Only/output/kaggle_20261101_duchuynguyen1802/grace_b0_runs/reveal/validation/records.jsonl"),
    ("B1",
     "03_Arm_B1_Graph_Only/output/kaggle_run_02/grace_b1_runs/devign/validation/records.jsonl",
     "03_Arm_B1_Graph_Only/output/kaggle_run_02/grace_b1_runs/reveal/validation/records.jsonl"),
    ("B1-H2",
     "11_Arm_B1H2_Evidence/kaggle_b1h2_validation_20261106/downloaded_output/b1_h2_validation/seed_42/devign/validation/records.jsonl",
     "11_Arm_B1H2_Evidence/kaggle_b1h2_validation_20261106/downloaded_output/b1_h2_validation/seed_42/reveal/validation/records.jsonl"),
    ("B2",
     "runs/final/devign/validation/B2/42/records.jsonl",
     "runs/final/reveal/validation/B2/42/records.jsonl"),
    ("B2-rep",
     "runs/final/devign/validation/B2-rep/42/records.jsonl",
     "runs/final/reveal/validation/B2-rep/42/records.jsonl"),
    ("B1-full",
     "runs/final/devign/validation/B1-full/42/records.jsonl",
     "runs/final/reveal/validation/B1-full/42/records.jsonl"),
    ("B2-nolabel",
     "runs/final/devign/validation/B2-nolabel/42/records.jsonl",
     "runs/final/reveal/validation/B2-nolabel/42/records.jsonl"),
    ("B2-labelonly",
     "runs/final/devign/validation/B2-labelonly/42/records.jsonl",
     "runs/final/reveal/validation/B2-labelonly/42/records.jsonl"),
]

def extract_score(r):
    for k in ['s', 'score', 'prob_1', 'p1']:
        if k in r and r[k] is not None:
            return float(r[k])
    return None

def compute_mcc(y, p):
    tp = float(((y == 1) & (p == 1)).sum())
    tn = float(((y == 0) & (p == 0)).sum())
    fp = float(((y == 0) & (p == 1)).sum())
    fn = float(((y == 1) & (p == 0)).sum())
    den = np.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    return (tp * tn - fp * fn) / den if den > 0 else 0.0

for arm, p_dev, p_rev in arms_to_check:
    print("\n" + "="*80)
    print(f"AUDITING ARM: {arm}")
    for name, path_str, exp_ids, exp_labels in [("Devign", p_dev, devign_ids, devign_labels), ("ReVeal", p_rev, reveal_ids, reveal_labels)]:
        p = Path(path_str)
        if not p.exists():
            print(f"  [{name}] File not found: {p}")
            continue
        
        recs = [json.loads(line) for line in open(p, encoding='utf-8') if line.strip()]
        rec_ids = [str(r['id']) for r in recs]
        
        # 1. Row count & Uniqueness
        n_rows = len(recs)
        n_unique_ids = len(set(rec_ids))
        row_check = (n_rows == len(exp_ids) and n_unique_ids == len(exp_ids))
        
        # 2. Exact ID matching
        id_order_match = (rec_ids == exp_ids)
        id_set_match = (set(rec_ids) == set(exp_ids))
        
        # 3. Label matching
        labels_in_rec = []
        labels_from_spec = []
        for r in recs:
            rid = str(r['id'])
            rec_y = r.get('label', r.get('target', r.get('ground_truth')))
            if rec_y is not None:
                labels_in_rec.append(int(rec_y))
            labels_from_spec.append(exp_labels[rid])
        
        labels_in_rec = np.array(labels_in_rec)
        labels_from_spec = np.array(labels_from_spec)
        labels_match = (len(labels_in_rec) == len(labels_from_spec) and np.array_equal(labels_in_rec, labels_from_spec))
        
        # 4. Score distribution
        scores = [extract_score(r) for r in recs]
        scores_arr = np.array([s for s in scores if s is not None])
        n_valid_scores = len(scores_arr)
        
        p10, p25, p50, p75, p90 = np.percentile(scores_arr, [10, 25, 50, 75, 90])
        
        # 5. Grid search MCC
        grid = [i / 100.0 for i in range(1, 100)]
        mccs = []
        for t in grid:
            pred = (scores_arr >= t).astype(int)
            mccs.append((t, compute_mcc(labels_from_spec, pred)))
        
        best_t, best_mcc = max(mccs, key=lambda x: (x[1], -abs(x[0] - 0.5)))
        
        # Top 5 thresholds by MCC
        top5 = sorted(mccs, key=lambda x: x[1], reverse=True)[:5]
        top5_str = ", ".join([f"tau={t:.2f}: MCC={m:.4f}" for t, m in top5])
        
        # Also check MCC at standard tau=0.5
        mcc_05 = compute_mcc(labels_from_spec, (scores_arr >= 0.5).astype(int))
        
        print(f"  [{name}] N={n_rows} (Expected {len(exp_ids)}). IDs match: {id_order_match} (Set: {id_set_match}). Labels match Spec: {labels_match}")
        print(f"         Scores: min={scores_arr.min():.4f}, p25={p25:.4f}, median={p50:.4f}, p75={p75:.4f}, max={scores_arr.max():.4f}")
        print(f"         At tau=0.50: MCC={mcc_05:.4f} | Optimal: tau*={best_t:.2f} with MCC={best_mcc:.4f}")
        print(f"         Top 5 candidate taus: {top5_str}")
