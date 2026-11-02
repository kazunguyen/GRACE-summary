"""Package the 66 already-reconciled prompts; no retrieval, encoding or LLM."""
import hashlib
import json
import shutil
import sys
from collections import Counter
from pathlib import Path
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
AUDIT = ROOT / 'Runs-management/donor_reconciliation_20261101'
BASE = ROOT / '01_Author_Baseline_Unified'
OUT = HERE / 'output'
PAYLOAD = OUT / 'grace_b2_devign_donor_rerun_66_20261102'
BUNDLE_ID = 'grace_b2_devign_donor_rerun_66_20261102'


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def rows(path):
    with path.open('rb') as f:
        return [json.loads(line) for line in f if line.strip()]


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def write_rows(path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='\n') as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False, allow_nan=False) + '\n')


def main():
    verification = read(AUDIT / 'verification.json')
    for name, sha in verification['exports_sha256'].items():
        assert digest(AUDIT / name) == sha, f'Reconciliation export changed: {name}'
    assert verification['rerun_prompts'] == 66
    decisions = [r for r in rows(AUDIT / 'downloaded_record_decisions.jsonl') if r['decision'] == 'rerun_changed_prompt']
    assert len(decisions) == 66
    assert {(r['arm'], r['dataset']) for r in decisions} == {('B2', 'devign')}
    changed = {r['id']: r for r in decisions}
    prompt_rows = []
    sources = {}
    for split, count in [('validation', 28), ('test', 38)]:
        path = AUDIT / f'rerun_inputs/B2/devign/{split}/prompts.jsonl'
        sm = read(path.with_name('manifest.json'))
        assert digest(path) == sm['prompts_sha256']
        rr = rows(path)
        assert len(rr) == count
        for r in rr:
            a = changed[r['id']]
            assert r['split'] == a['split'] == split
            assert r['prompt_sha256'] == a['new_prompt_sha256'] != a['old_prompt_sha256']
            assert hashlib.sha256(r['prompt'].encode('utf-8')).hexdigest() == r['prompt_sha256']
        prompt_rows.extend(rr)
        dest = PAYLOAD / f'splits/devign/{split}/prompts.jsonl'
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, dest)
        sources[path.relative_to(ROOT).as_posix()] = digest(path)
    assert len({r['id'] for r in prompt_rows}) == 66 and set(changed) == {r['id'] for r in prompt_rows}
    snapshot_sha = digest(BASE / 'output/research_freeze_20261101/freeze_manifest.json')
    assert {r['donor_snapshot_sha256'] for r in prompt_rows} == {snapshot_sha}, 'Donor snapshot changed since reconciliation'
    write_rows(PAYLOAD / 'prompts.jsonl', prompt_rows)
    write_rows(PAYLOAD / 'rerun_audit.jsonl', decisions)
    old_folder = BASE / 'output/local_full/inference_qwen_q4_b2_20261101/grace_b2_four_split_8h/devign/validation'
    old_records_path = old_folder / 'records.jsonl'
    old_records = rows(old_records_path)
    old_runtime = read(old_folder / 'run_manifest.json')
    assert old_runtime['model_sha256'] == 'f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335'
    assert len(old_records) == 2732 and len({r['id'] for r in old_records}) == 2732
    original_folder = BASE / 'output/local_full/bundles_recovered_joern_final_20261031/devign/validation'
    original_manifest = read(original_folder / 'bundle_manifest.json')
    assert digest(original_folder / 'prompts.jsonl') == original_manifest['prompts_sha256']
    original = {r['id']: r for r in rows(original_folder / 'prompts.jsonl')}
    full_new_path = AUDIT / 'new_reference/B2/devign/validation/prompts.jsonl'
    full_manifest = read(full_new_path.with_name('manifest.json'))
    assert digest(full_new_path) == full_manifest['prompts_sha256']
    full_new = rows(full_new_path)
    new_by_id = {r['id']: r for r in full_new}
    assert len(full_new) == len(new_by_id) == 2732
    reusable = []
    for r in old_records:
        before = original[r['id']]
        assert r['prompt_sha256'] == before['prompt_sha256'] and r['label'] == before['label']
        assert r['model_sha256'] == old_runtime['model_sha256'] and r['seed'] == 42
        if r['id'] not in changed:
            assert r['prompt_sha256'] == new_by_id[r['id']]['prompt_sha256']
            reusable.append(r)
    assert len(reusable) == 2704
    write_rows(PAYLOAD / 'validation_support/reusable_records.jsonl', reusable)
    write_rows(PAYLOAD / 'validation_support/expected_full_validation.jsonl',
               [{k: r[k] for k in ('id', 'dataset', 'split', 'label', 'prompt_sha256')} for r in full_new])
    write(PAYLOAD / 'validation_support/original_run_manifest.json', old_runtime)
    sys.path.insert(0, str(ROOT / 'Runs-management'))
    from validation_lock import inference_identity
    copied = {
        'README.md': HERE / 'README.md',
        'verify_bundle.py': HERE / 'verify_bundle.py',
        'validation_lock.py': ROOT / 'Runs-management/validation_lock.py',
        'mau_can_inference_lai.csv': AUDIT / 'mau_can_inference_lai.csv',
        'provenance/devign_retrieval_provenance.json': AUDIT / 'devign_retrieval_provenance.json',
        'provenance/reconciliation_verification.json': AUDIT / 'verification.json',
    }
    for relative, source in copied.items():
        dest = PAYLOAD / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, dest)
        sources[source.relative_to(ROOT).as_posix()] = digest(source)
    sources[old_records_path.relative_to(ROOT).as_posix()] = digest(old_records_path)
    sources[full_new_path.relative_to(ROOT).as_posix()] = digest(full_new_path)
    write(PAYLOAD / 'provenance/source_artifacts.json', sources)
    payload_files = [PAYLOAD / 'prompts.jsonl', PAYLOAD / 'rerun_audit.jsonl',
                     PAYLOAD / 'splits/devign/validation/prompts.jsonl', PAYLOAD / 'splits/devign/test/prompts.jsonl',
                     PAYLOAD / 'validation_support/reusable_records.jsonl',
                     PAYLOAD / 'validation_support/expected_full_validation.jsonl',
                     PAYLOAD / 'validation_support/original_run_manifest.json',
                     PAYLOAD / 'provenance/source_artifacts.json'] + [PAYLOAD / p for p in copied]
    manifest = {
        'schema': 'grace_donor_rerun_bundle_v1', 'bundle_id': BUNDLE_ID, 'prepared_date': '2026-11-02',
        'arm': 'B2', 'dataset': 'devign', 'split': 'mixed', 'count': 66,
        'counts_by_split': {'validation': 28, 'test': 38}, 'seed': 42,
        'is_partial_split': True, 'purpose': 'replace only donor-changed prompts; retain compatible previous scores',
        'prompt_variant': 'b2_frozen_donor_reconciled_v1',
        'prompts_sha256': digest(PAYLOAD / 'prompts.jsonl'),
        'tokenizer': old_runtime['tokenizer'], 'tokenizer_revision': old_runtime['tokenizer_revision'],
        'model_repo': old_runtime['model_repo'], 'quantization': old_runtime['quantization'],
        'model_file': old_runtime['model_file'], 'model_sha256': old_runtime['model_sha256'],
        'prompt_budget_tokens': 8192, 'graph_limits': {'nodes': 40, 'edges': 80, 'max_tokens': 1500},
        'expected_inference_identity': inference_identity(old_runtime),
        'runtime_parameters': {'seed': 42, 'n_ctx': 8192, 'n_batch': 256, 'n_gpu_layers': -1, 'logits_all': True,
                               'chat_template': 'pinned tokenizer: user prompt + assistant generation prefix'},
        'donor_snapshot_sha256': snapshot_sha,
        'donor_bank_sha256': read(AUDIT / 'devign_retrieval_provenance.json')['new']['input_sha256'],
        'full_validation_prompt_set_sha256': full_manifest['prompts_sha256'],
        'validation_support': {'reusable_count': 2704, 'new_inference_count': 28, 'expected_full_count': 2732,
                               'thresholds_included': False, 'fit_on_partial_validation_allowed': False,
                               'test_requires_new_full_validation_threshold': True},
        'output_contract': {'arm': 'B2', 'dataset': 'devign', 'keep_target_ids': True,
                            'keep_original_split': True, 'use_new_prompt_sha256': True,
                            'use_separate_output_directory': True},
        'files_sha256': {p.relative_to(PAYLOAD).as_posix(): digest(p) for p in payload_files},
        'llm_calls_during_preparation': 0,
    }
    write(PAYLOAD / 'bundle_manifest.json', manifest)
    archive = OUT / f'{BUNDLE_ID}.zip'
    # An explicit allowlist keeps old or unrelated files out of a rebuilt ZIP.
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in [PAYLOAD / 'bundle_manifest.json'] + sorted(payload_files):
            z.write(p, p.relative_to(PAYLOAD).as_posix())
    from verify_bundle import load_bundle
    checked_manifest, checked_rows = load_bundle(archive)
    assert checked_manifest == manifest and checked_rows == prompt_rows
    checksum = digest(archive)
    archive.with_suffix('.zip.sha256').write_text(f'{checksum}  {archive.name}\n', encoding='ascii')
    write(OUT / 'build_report.json', {'bundle': archive.name, 'bundle_sha256': checksum,
                                     'bundle_bytes': archive.stat().st_size, 'count': len(checked_rows),
                                     'split_counts': dict(Counter(r['split'] for r in checked_rows)),
                                     'reusable_validation_count': len(reusable), 'verified': True, 'llm_calls': 0})
    print(json.dumps(read(OUT / 'build_report.json'), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
