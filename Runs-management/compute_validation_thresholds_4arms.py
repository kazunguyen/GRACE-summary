import json
import math
import sys
from pathlib import Path
import numpy as np

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / '01_Author_Baseline_Unified/diagnostic_kit/src'))
from grace_diag.stats import pick_threshold, mcc, auroc, balanced_accuracy, f1

ARMS = ['B1-full', 'B2-nolabel', 'B2-labelonly', 'B2-rep']
DATASETS = ['devign', 'reveal']
EXPECTED_COUNTS = {'devign': 2732, 'reveal': 2273}

def load_records(arm, dataset):
    path = ROOT / f'runs/final/{dataset}/validation/{arm}/42/records.jsonl'
    if not path.exists():
        raise FileNotFoundError(f"Missing records: {path}")
    
    rows = []
    seen_ids = set()
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            uid = r['id']
            if uid in seen_ids:
                raise ValueError(f"Duplicate ID in {path}: {uid}")
            seen_ids.add(uid)
            rows.append(r)
    
    expected = EXPECTED_COUNTS[dataset]
    if len(rows) != expected:
        raise ValueError(f"Count mismatch in {path}: expected {expected}, got {len(rows)}")
    
    return rows

def evaluate_arm(arm):
    results = {}
    print(f"\n=======================================================")
    print(f"  TÍNH TOÁN NGƯỠNG CHO ARM: {arm} (FULL VALIDATION CENSUS)")
    print(f"=======================================================")
    
    for ds in DATASETS:
        rows = load_records(arm, ds)
        n = len(rows)
        y = np.array([r['label'] for r in rows], dtype=int)
        s = np.array([r['s'] for r in rows], dtype=float)
        
        # 1. Tối ưu ngưỡng độc lập theo công thức argmax MCC
        tau_opt, mcc_opt = pick_threshold(y, s)
        
        # 2. Các chỉ số tại ngưỡng tối ưu
        pred_opt = (s >= tau_opt).astype(int)
        roc = auroc(y, s)
        ba_opt = balanced_accuracy(y, pred_opt)
        f1_opt = f1(y, pred_opt)
        
        results[ds] = {
            'n': n,
            'tau_optimal': tau_opt,
            'mcc_at_tau': mcc_opt,
            'auroc': roc,
            'ba_at_tau': ba_opt,
            'f1_at_tau': f1_opt,
            'y_pos': int(np.sum(y == 1)),
            'y_neg': int(np.sum(y == 0))
        }
        
        print(f"\n--- Dataset: {ds.upper()} (N = {n} mẫu đầy đủ: {results[ds]['y_pos']} Pos, {results[ds]['y_neg']} Neg) ---")
        print(f"  * AUROC (Validation):              {roc:.4f}")
        print(f"  * Ngưỡng tối ưu (tau* = argmax MCC): {tau_opt:.2f}")
        print(f"  * MCC tại tau*:                    {mcc_opt:.4f}")
        print(f"  * Balanced Accuracy tại tau*:      {ba_opt * 100:.2f}%")
        print(f"  * F1 tại tau*:                     {f1_opt:.4f}")
        
        # Với B2-rep: kiểm tra thêm giá trị tại ngưỡng kế thừa từ B2 (0.70 Devign / 0.12 ReVeal)
        if arm == 'B2-rep':
            tau_inherit = 0.70 if ds == 'devign' else 0.12
            pred_inh = (s >= tau_inherit).astype(int)
            mcc_inh = mcc(y, pred_inh)
            ba_inh = balanced_accuracy(y, pred_inh)
            f1_inh = f1(y, pred_inh)
            print(f"  [Quy tắc kế thừa từ B2 gốc]:")
            print(f"    - tau* kế thừa từ B2:            {tau_inherit:.2f}")
            print(f"    - MCC tại tau* kế thừa:          {mcc_inh:.4f}")
            print(f"    - Balanced Acc tại tau* kế thừa: {ba_inh * 100:.2f}%")
            print(f"    - F1 tại tau* kế thừa:           {f1_inh:.4f}")
            results[ds]['tau_inherited_from_B2'] = tau_inherit
            results[ds]['mcc_at_inherited_tau'] = mcc_inh
            results[ds]['ba_at_inherited_tau'] = ba_inh
            results[ds]['f1_at_inherited_tau'] = f1_inh

    return results

def main():
    all_res = {}
    for arm in ARMS:
        all_res[arm] = evaluate_arm(arm)
        
    out_path = ROOT / 'Runs-management/validation_thresholds_4arms_full_census.json'
    out_path.write_text(json.dumps(all_res, indent=2), encoding='utf-8')
    print(f"\n>>> Đã lưu kết quả chi tiết vào: {out_path}")

if __name__ == '__main__':
    main()
