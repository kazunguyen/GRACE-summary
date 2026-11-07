"""
Generate canonical threshold.json files for:
- B1-full: 09_Arm_B1_Full/config/threshold.json
- B2-nolabel: 10_Arm_B2_NoLabel/config/threshold.json
- B2-labelonly: 12_Arm_B2_LabelOnly/config/threshold.json
- B2-rep: 05_Arm_B2_Rep/config/threshold.json

Strict compliance:
- Uses validation_lock.pick_threshold (validation_mcc_grid_v1)
- Computed on 100% full validation census: Devign N=2,732, ReVeal N=2,273
- Zero use of 600-sample exploratory subset
- Self-signing SHA-256 for integrity verification
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

ARMS = {
    'B1-full': '09_Arm_B1_Full',
    'B2-nolabel': '10_Arm_B2_NoLabel',
    'B2-labelonly': '12_Arm_B2_LabelOnly',
    'B2-rep': '05_Arm_B2_Rep'
}
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
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        
    summary = {}

    for arm, arm_dir in ARMS.items():
        print(f"\n=======================================================")
        print(f"  LOCKING THRESHOLDS: {arm}")
        print(f"=======================================================")
        entries = {}
        arm_slug = arm.lower().replace('-', '_')

        for ds in DATASETS:
            rec_path = ROOT / f'runs/final/{ds}/validation/{arm}/42/records.jsonl'
            man_path = ROOT / f'runs/final/{ds}/validation/{arm}/42/run_manifest.json'

            if not rec_path.exists():
                raise FileNotFoundError(f"Missing records: {rec_path}")
            if not man_path.exists():
                raise FileNotFoundError(f"Missing manifest: {man_path}")

            rows = validation_lock.read_jsonl(rec_path)
            if len(rows) != EXPECTED[ds]:
                raise ValueError(f"Count mismatch for {arm} {ds}: got {len(rows)}, expected {EXPECTED[ds]}")

            manifest = json.loads(man_path.read_text(encoding='utf-8'))
            rec_sha256 = file_sha256(rec_path)

            # Pick threshold via canonical validation_lock rule
            res = validation_lock.pick_threshold(rows)

            # Evidence digest
            ordered = sorted(rows, key=lambda r: str(r['id']))
            evidence = [{k: r.get(k) for k in ('id', 'label', 'prompt_sha256', 'model_sha256', 'seed', 's', 'valid')} for r in ordered]
            evidence_sha256 = digest_json(evidence)

            entry_key = f"{arm}/42/{ds}"
            entry = {
                'arm': arm,
                'seed': 42,
                'dataset': ds,
                'split_used': 'validation',
                'tau_star': res['tau'],
                'validation_mcc': res['validation_mcc'],
                'n_total': len(rows),
                'n_valid': res['n_valid'],
                'tie_rule': 'within 1e-9: closest to 0.5, then lower tau',
                'validation_prompt_set_sha256': manifest.get('prompt_set_sha256'),
                'validation_bundle_sha256': manifest.get('bundle_sha256'),
                'validation_records_sha256': rec_sha256,
                'validation_evidence_sha256': evidence_sha256,
                'model_sha256': manifest.get('model_sha256'),
                'backend': f"llama-cpp-python=={manifest.get('llama_cpp_python', '0.3.16')}",
                'source_run_manifest': manifest,
                'grid': res['grid_results']
            }

            if arm == 'B2-rep':
                tau_inherit = 0.70 if ds == 'devign' else 0.12
                entry['inherited_rule'] = 'Inherited from B2 parent arm per OSF preregistration Section 2.3'
                entry['tau_inherited_from_B2'] = tau_inherit
                entry['is_identical_to_inherited'] = (res['tau'] == tau_inherit)

            entries[entry_key] = entry
            print(f"  [{ds.upper()}] N={len(rows)} (valid={res['n_valid']}) -> tau* = {res['tau']}, MCC = {res['validation_mcc']:.4f}")

        cfg_dir = ROOT / arm_dir / 'config'
        cfg_dir.mkdir(parents=True, exist_ok=True)
        out_file = cfg_dir / 'threshold.json'

        lock_doc = {
            'schema': f"{arm_slug}_validation_threshold_lock_v1",
            'arm': arm,
            'split': 'validation',
            'locked_at_utc': datetime.now(timezone.utc).isoformat(),
            'rules': validation_lock.RULES,
            'rules_sha256': validation_lock.RULES_SHA256,
            'model_sha256': manifest.get('model_sha256'),
            'context_tokens': 8192,
            'seed_policy': 'seed 42 full validation census (2,732 Devign / 2,273 ReVeal)',
            'entries': entries
        }

        # Self-signing hash
        doc_for_hash = {k: v for k, v in lock_doc.items() if k != 'locked_sha256'}
        lock_doc['locked_sha256'] = digest_json(doc_for_hash)

        validation_lock.write_json(out_file, lock_doc)
        print(f"  -> Saved: {out_file}")
        print(f"  -> Lock SHA-256: {lock_doc['locked_sha256']}")
        
        summary[arm] = {
            'file': str(out_file.relative_to(ROOT)),
            'locked_sha256': lock_doc['locked_sha256'],
            'devign_tau': entries[f'{arm}/42/devign']['tau_star'],
            'devign_mcc': entries[f'{arm}/42/devign']['validation_mcc'],
            'reveal_tau': entries[f'{arm}/42/reveal']['tau_star'],
            'reveal_mcc': entries[f'{arm}/42/reveal']['validation_mcc']
        }

    print("\n=======================================================")
    print("  SUMMARY OF LOCKED THRESHOLDS")
    print("=======================================================")
    print(json.dumps(summary, indent=2))

if __name__ == '__main__':
    main()
