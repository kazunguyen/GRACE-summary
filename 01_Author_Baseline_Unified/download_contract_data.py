"""Download and canonicalize every split of a contract-pinned HF dataset."""
import argparse
import hashlib
import json
from pathlib import Path

import yaml


def adapt(row, dataset, split, index):
    if dataset == 'devign':
        code, label, source_id = row.get('func'), row.get('target'), row.get('id')
        if source_id is None:
            raise ValueError('Devign source ID missing')
        rid = f'{dataset}:{split}:{source_id}'
    elif dataset == 'reveal':
        code, label, source_id = row.get('functionSource'), row.get('label'), row.get('hash')
        # ReVeal hashes are not unique; the pinned split order makes row index unambiguous.
        rid = f'{dataset}:{split}:{index}'
    else:
        raise ValueError(f'Unsupported dataset: {dataset}')
    if not isinstance(code, str) or not code.strip() or label not in (0, 1, False, True):
        raise ValueError(f'Invalid code or binary label in {rid}')
    return {'id': rid, 'func': code.strip(), 'target': int(label), 'source_id': str(source_id),
            'project': row.get('project'), 'commit_id': row.get('commit_id'),
            'dataset': dataset, 'split': split}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--dataset', required=True, choices=['devign', 'reveal'])
    ap.add_argument('--out', required=True, type=Path)
    ap.add_argument('--contract', type=Path, default=Path(__file__).with_name('evaluation_contract.yaml'))
    args = ap.parse_args()
    contract = yaml.safe_load(args.contract.read_text(encoding='utf-8'))
    spec = contract['dataset_split'][args.dataset]
    repo, sep, revision = spec['dataset_version'].rpartition('@')
    if not sep or revision != spec['source_revision'] or len(revision) != 40:
        raise ValueError('Dataset source/revision not pinned consistently in contract')
    from datasets import load_dataset
    args.out.mkdir(parents=True, exist_ok=True)
    manifest = {'dataset': args.dataset, 'repo': repo, 'revision': revision, 'splits': {}}
    for split in ('train', 'validation', 'test'):
        data = load_dataset(repo, split=split, revision=revision)
        path = args.out / (split + '.jsonl')
        tmp = path.with_suffix('.jsonl.tmp')
        seen = set()
        with tmp.open('w', encoding='utf-8', newline='\n') as f:
            for index, source in enumerate(data):
                row = adapt(source, args.dataset, split, index)
                if row['id'] in seen:
                    raise ValueError(f"Duplicate ID: {row['id']}")
                seen.add(row['id'])
                f.write(json.dumps(row, ensure_ascii=False) + '\n')
        digest = hashlib.sha256(tmp.read_bytes()).hexdigest()
        if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError(f'Existing split differs from pinned data: {path}; choose a new directory')
        tmp.replace(path)
        manifest['splits'][split] = {'count': len(seen), 'sha256': digest, 'id_policy': 'source_id' if args.dataset == 'devign' else 'split_row_index'}
        print(args.dataset, split, len(seen), digest, flush=True)
    (args.out / 'data_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
