"""Verify the portable B2 donor rerun bundle; standard library only, no LLM."""
import hashlib
import json
from collections import Counter
from pathlib import Path
import zipfile


def parse_rows(data):
    return [json.loads(line) for line in data.decode('utf-8').splitlines() if line.strip()]


def load_bundle(archive):
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:
            raise ValueError('ZIP CRC check failed')
        if len(z.namelist()) != len(set(z.namelist())):
            raise ValueError('Duplicate ZIP members')
        m = json.loads(z.read('bundle_manifest.json'))
        if m['schema'] != 'grace_donor_rerun_bundle_v1' or m['count'] != 66:
            raise ValueError('Wrong bundle schema or size')
        if m['arm'] != 'B2' or m['dataset'] != 'devign' or not m['is_partial_split']:
            raise ValueError('Wrong experiment identity')
        for name, expected in m['files_sha256'].items():
            if hashlib.sha256(z.read(name)).hexdigest() != expected:
                raise ValueError(f'File hash mismatch: {name}')
        if m['prompts_sha256'] != m['files_sha256']['prompts.jsonl']:
            raise ValueError('Prompt manifest hashes disagree')
        rows = parse_rows(z.read('prompts.jsonl'))
        if Counter(r['split'] for r in rows) != Counter(validation=28, test=38):
            raise ValueError('Wrong split counts')
        if len(rows) != 66 or len({r['id'] for r in rows}) != 66:
            raise ValueError('Wrong count or duplicate ID')
        audit = parse_rows(z.read('rerun_audit.jsonl'))
        by_id = {r['id']: r for r in audit}
        if len(audit) != 66 or len(by_id) != 66 or set(by_id) != {r['id'] for r in rows}:
            raise ValueError('Audit IDs differ from rerun prompts')
        for r in rows:
            if r['arm'] != 'B2' or r['dataset'] != 'devign':
                raise ValueError('Wrong row identity')
            if r['donor_snapshot_sha256'] != m['donor_snapshot_sha256']:
                raise ValueError('Wrong donor snapshot')
            if hashlib.sha256(r['prompt'].encode('utf-8')).hexdigest() != r['prompt_sha256']:
                raise ValueError('Prompt hash mismatch')
            a = by_id[r['id']]
            if a['new_prompt_sha256'] != r['prompt_sha256'] or a['old_prompt_sha256'] == r['prompt_sha256']:
                raise ValueError('A rerun row does not contain the changed prompt')
            if a['split'] != r['split'] or a['model_sha256'] != m['expected_inference_identity']['model_sha256']:
                raise ValueError('Audit split/model mismatch')
            if r['tokens']['prompt_tokens'] + 64 > m['prompt_budget_tokens']:
                raise ValueError('Prompt exceeds context budget')
        for split in ('validation', 'test'):
            split_rows = parse_rows(z.read(f'splits/devign/{split}/prompts.jsonl'))
            if split_rows != [r for r in rows if r['split'] == split]:
                raise ValueError('Combined and split prompt files disagree')
        expected = parse_rows(z.read('validation_support/expected_full_validation.jsonl'))
        reusable = parse_rows(z.read('validation_support/reusable_records.jsonl'))
        expected_by_id = {r['id']: r for r in expected}
        if len(expected) != 2732 or len(expected_by_id) != 2732:
            raise ValueError('Wrong full validation size')
        new_validation = [r for r in rows if r['split'] == 'validation']
        if len(reusable) != 2704 or len({r['id'] for r in reusable}) != 2704:
            raise ValueError('Wrong reusable validation size')
        if {r['id'] for r in reusable} & {r['id'] for r in new_validation}:
            raise ValueError('Old scores overlap changed validation prompts')
        if {r['id'] for r in reusable + new_validation} != set(expected_by_id):
            raise ValueError('Validation merge would not cover the full set')
        for r in reusable + new_validation:
            e = expected_by_id[r['id']]
            if (r['split'], r['dataset'], r['label'], r['prompt_sha256']) != ('validation', 'devign', e['label'], e['prompt_sha256']):
                raise ValueError('Validation ID/label/hash mismatch')
        for r in reusable:
            if r['arm'] != 'B2' or r['seed'] != 42 or r['model_sha256'] != m['expected_inference_identity']['model_sha256']:
                raise ValueError('Reusable score inference identity mismatch')
    return m, rows


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bundle', type=Path)
    args = parser.parse_args()
    manifest, prompts = load_bundle(args.bundle)
    print(json.dumps({'bundle': str(args.bundle), 'verified': True,
                      'prompts': len(prompts), 'counts': dict(Counter(r['split'] for r in prompts)),
                      'reusable_validation_scores': 2704}, indent=2))
