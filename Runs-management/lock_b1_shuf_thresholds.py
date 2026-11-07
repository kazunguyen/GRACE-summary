"""
Generate canonical threshold.json for 08_Arm_B1_Shuf/config/threshold.json
covering all 3 seeds: 42, 43, 44 on both Devign and ReVeal.
"""

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'Runs-management'))
import validation_lock

SEEDS = [42, 43, 44]
DATASETS = ['devign', 'reveal']
EXPECTED = {'devign': 2732, 'reveal': 2273}

def file_sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()

def digest_json(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()

def main():
    entries = {}
    arm = 'B1-shuf'
    
    for seed in SEEDS:
        for ds in DATASETS:
            rec_path = ROOT / f'runs/final/{ds}/validation/{arm}/{seed}/records.jsonl'
            man_path = ROOT / f'runs/final/{ds}/validation/{arm}/{seed}/run_manifest.json'
            
            rows = validation_lock.read_jsonl(rec_path)
            if len(rows) != EXPECTED[ds]:
                raise ValueError(f"Count mismatch: {len(rows)} != {EXPECTED[ds]}")
                
            manifest = json.loads(man_path.read_text(encoding='utf-8'))
            rec_sha = file_sha256(rec_path)
            res = validation_lock.pick_threshold(rows)
            
            ordered = sorted(rows, key=lambda r: str(r['id']))
            evidence = [{k: r.get(k) for k in ('id', 'label', 'prompt_sha256', 'model_sha256', 'seed', 's', 'valid')} for r in ordered]
            evidence_sha256 = digest_json(evidence)
            
            entry_key = f"{arm}/{seed}/{ds}"
            entries[entry_key] = {
                'arm': arm,
                'seed': seed,
                'dataset': ds,
                'split_used': 'validation',
                'tau_star': res['tau'],
                'validation_mcc': res['validation_mcc'],
                'n_total': len(rows),
                'n_valid': res['n_valid'],
                'tie_rule': 'within 1e-9: closest to 0.5, then lower tau',
                'validation_prompt_set_sha256': manifest.get('prompt_set_sha256'),
                'validation_bundle_sha256': manifest.get('bundle_sha256'),
                'validation_records_sha256': rec_sha,
                'validation_evidence_sha256': evidence_sha256,
                'model_sha256': manifest.get('model_sha256'),
                'backend': f"llama-cpp-python=={manifest.get('llama_cpp_python', '0.3.16')}",
                'source_run_manifest': manifest,
                'grid': res['grid_results']
            }
            print(f"Seed {seed} {ds.upper()}: tau* = {res['tau']}, MCC = {res['validation_mcc']:.4f}")

    cfg_dir = ROOT / '08_Arm_B1_Shuf/config'
    cfg_dir.mkdir(parents=True, exist_ok=True)
    out_file = cfg_dir / 'threshold.json'

    lock_doc = {
        'schema': 'b1_shuf_seed_validation_threshold_lock_v1',
        'arm': arm,
        'split': 'validation',
        'locked_at_utc': datetime.now(timezone.utc).isoformat(),
        'rules': validation_lock.RULES,
        'rules_sha256': validation_lock.RULES_SHA256,
        'model_sha256': manifest.get('model_sha256'),
        'context_tokens': 8192,
        'seed_policy': 'independent threshold selection for 3 seeds: 42, 43, 44',
        'entries': entries
    }

    doc_for_hash = {k: v for k, v in lock_doc.items() if k != 'locked_sha256'}
    lock_doc['locked_sha256'] = digest_json(doc_for_hash)

    validation_lock.write_json(out_file, lock_doc)
    print(f"\nSaved {out_file}")
    print(f"SHA-256: {lock_doc['locked_sha256']}")

if __name__ == '__main__':
    main()
