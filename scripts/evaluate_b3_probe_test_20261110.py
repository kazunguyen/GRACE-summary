"""Local-only adapter to the project's common table-A evaluator.

Never fits a threshold. Labels must be the exact private B3 test-label artifact.
Metrics computation does not substitute for per-session runtime acceptance.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

R = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(R / 'scripts'), str(R / '01_Author_Baseline_Unified/diagnostic_kit/src')]
from b3_test_runtime import load_manifest, validate_archive, read_dataset_rows, load_threshold, checked_records
from grace_diag.evaluate_final import table_a

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--release', type=Path, required=True, help='Arm release directory containing kaggle_dataset/')
    ap.add_argument('--output-root', type=Path, required=True, help='Downloaded worker root containing seed_42/')
    ap.add_argument('--labels', type=Path, required=True, help='Local private_evaluation_only/test_labels.json')
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    mp = args.release / 'kaggle_dataset/test_release_manifest.json'
    root = load_manifest(mp, hashlib.sha256(mp.read_bytes()).hexdigest())
    members = validate_archive(mp.parent / 'kaggle_input.zip', root)
    label_raw = args.labels.read_bytes()
    if hashlib.sha256(label_raw).hexdigest() != root['private_label_sha256']:
        raise ValueError('Private label artifact differs from sealed B3 test release')
    labels = json.loads(label_raw)
    data, locked = {}, {}
    for ds in ('devign', 'reveal'):
        rows = read_dataset_rows(members, root, ds)
        n = checked_records(args.output_root, root, rows, ds)
        if n != len(rows):
            raise ValueError(f'Incomplete {ds} test census: {n}/{len(rows)}')
        records = {}
        path = args.output_root / 'seed_42' / ds / 'test/records.jsonl'
        for line in path.read_text(encoding='utf-8').splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            label = labels[record['id']]
            if type(label) is not int or label not in (0, 1):
                raise ValueError('Invalid private target label')
            records[record['id']] = dict(record, label=label)
        data[(ds, root['arm'], 42, 'test')] = records
        locked[f"{ds}|{root['arm']}|42"] = {'tau': load_threshold(root, members, ds), 'policy': 'inherit_B3_amended_validation_lock'}
    if args.out.exists():
        raise FileExistsError('Preserve existing metrics; choose a new output directory')
    args.out.mkdir(parents=True)
    table_a(data, args.out, locked)
    (args.out / 'evaluation_identity.json').write_text(json.dumps({
        'release_id': root['release_id'], 'arm': root['arm'], 'threshold_from': 'B3',
        'classification': 'AMENDED_EXPLORATORY_SUBPROTOCOL', 'evaluator': 'grace_diag.evaluate_final.table_a',
        'manifest_sha256': hashlib.sha256(mp.read_bytes()).hexdigest(),
        'threshold_lock_sha256': root['threshold_lock_sha256'],
        'runtime_acceptance': 'REQUIRES_SEPARATE_SESSION_PROVENANCE_REVIEW', 'test_refit': False,
    }, indent=2) + '\n', encoding='utf-8')

if __name__ == '__main__':
    main()
