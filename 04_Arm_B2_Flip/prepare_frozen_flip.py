"""Build B2-flip using the audited B2 reference retrieved from the frozen donor bank."""
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / '01_Author_Baseline_Unified'
AUDIT = ROOT / 'Runs-management/donor_reconciliation_20261101'
REFERENCE_ROOT = AUDIT / 'new_reference/B2'
FROZEN_ROOT = BASE / 'output/research_freeze_20261101'
LEGACY_ROOT = ROOT / '04_Arm_B2_Flip/output/bundles'
OUT_ROOT = ROOT / '04_Arm_B2_Flip/output/bundles_frozen_donor_20261101'
RUNS = [('devign', 'validation'), ('reveal', 'validation'), ('devign', 'test'), ('reveal', 'test')]
VARIANT = 'b2_flip_frozen_donor_v1'
TOKENIZER = 'Qwen/Qwen3-Coder-30B-A3B-Instruct'
TOKENIZER_REVISION = 'b2cff646eb4bb1d68355c01b18ae02e7cf42d120'
MODEL_SHA = 'f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335'
HEAD = re.compile(r'\n\nThe following is an example, and it is (Vulnerable|Non-vulnerable)\.\n')
sys.path.insert(0, str(BASE / 'diagnostic_kit/src'))
from grace_diag.token_budget import TokenCounter


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def rows(path):
    with Path(path).open('rb', buffering=4 * 1024 * 1024) as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def swap_demo_label(prompt, true_label=None):
    matches = list(HEAD.finditer(prompt))
    if len(matches) != 1 or not prompt.endswith('\n\nAnswer (0 or 1):'):
        raise ValueError('Cannot identify the unique demo label in B2 prompt')
    m = matches[0]
    actual = int(m.group(1) == 'Vulnerable')
    if true_label is not None and actual != true_label:
        raise ValueError('Frozen donor label differs from B2 reference text')
    word = 'Non-vulnerable' if actual else 'Vulnerable'
    return prompt[:m.start(1)] + word + prompt[m.end(1):]


def inspect_sources(reference_root=REFERENCE_ROOT, frozen_root=FROZEN_ROOT):
    snapshot = sha(Path(frozen_root) / 'freeze_manifest.json')
    proofs = {}
    for dataset in ('devign', 'reveal'):
        p = read(AUDIT / f'{dataset}_retrieval_provenance.json')
        bank = AUDIT / f'cache/{dataset}_new_bank.jsonl'
        if sha(bank) != p['new']['cache_sha256']:
            raise ValueError('Audited frozen donor cache changed')
        stats = read(Path(frozen_root) / dataset / 'stats.json')
        if stats['files_sha256']['donors.jsonl'] != p['new']['input_sha256']:
            raise ValueError('Frozen donor version differs from audited B2 retrieval')
        proofs[dataset] = {'labels': {r['id']: int(r['target']) for r in rows(bank)}, 'proof': p}
    for dataset, split in RUNS:
        path = Path(reference_root) / dataset / split / 'prompts.jsonl'
        manifest = read(path.with_name('manifest.json'))
        if sha(path) != manifest['prompts_sha256']:
            raise ValueError(f'B2 reference hash mismatch: {dataset}/{split}')
        print(f'{dataset}/{split}: audited B2 reference {manifest["count"]}', flush=True)
    return snapshot, proofs


def prepare(tokenizer, reference_root=REFERENCE_ROOT, frozen_root=FROZEN_ROOT,
            legacy_root=LEGACY_ROOT, out_root=OUT_ROOT):
    snapshot, proofs = inspect_sources(reference_root, frozen_root)
    counter = TokenCounter(None)
    counter.tok = tokenizer
    counter.approx = False
    out_root = Path(out_root)
    archives = []
    summary = []
    expected_identity = read(BASE / 'output/local_full/inference_qwen_q4_b2_20261101/grace_b2_four_split_8h/devign/validation/run_manifest.json')
    for dataset, split in RUNS:
        source = Path(reference_root) / dataset / split / 'prompts.jsonl'
        legacy_folder = Path(legacy_root) / dataset / split
        legacy_manifest = read(legacy_folder / 'bundle_manifest.json')
        if sha(legacy_folder / 'prompts.jsonl') != legacy_manifest['prompts_sha256']:
            raise ValueError('Legacy flip prompt cache changed')
        legacy = {r['id']: r for r in rows(legacy_folder / 'prompts.jsonl')}
        folder = out_root / dataset / split
        folder.mkdir(parents=True, exist_ok=True)
        prompt_path = folder / 'prompts.jsonl'
        audit_path = folder / 'pairing_audit.jsonl'
        seen = set()
        changes = 0
        with prompt_path.open('w', encoding='utf-8', newline='\n') as pf, audit_path.open('w', encoding='utf-8', newline='\n') as af:
            for reference in rows(source):
                uid = reference['id']
                if uid in seen or reference['donor_snapshot_sha256'] != snapshot:
                    raise ValueError('Duplicate target or mismatching donor snapshot')
                seen.add(uid)
                if hashlib.sha256(reference['prompt'].encode()).hexdigest() != reference['prompt_sha256']:
                    raise ValueError('B2 row hash mismatch')
                before = legacy[uid]
                if before['label'] != reference['label']:
                    raise ValueError('Target label changed')
                donor = reference['demo_ids'][0]
                true_label = proofs[dataset]['labels'][donor]
                prompt = swap_demo_label(reference['prompt'], true_label)
                prompt_sha = hashlib.sha256(prompt.encode()).hexdigest()
                metadata = reference['tokens']
                if metadata['graph_nodes_used'] > 40 or metadata['graph_edges_used'] > 80:
                    raise ValueError('Graph exceeds 40/80 contract')
                total = counter.count_chat(prompt)
                if total + 64 > 8192:
                    raise ValueError('Flip prompt overflow')
                changed = prompt_sha != before['prompt_sha256']
                changes += changed
                record = {'id': uid, 'dataset': dataset, 'split': split, 'arm': 'B2-flip', 'seed': 42,
                          'prompt_variant': VARIANT, 'label': reference['label'], 'prompt': prompt,
                          'prompt_sha256': prompt_sha, 'reference_b2_prompt_sha256': reference['prompt_sha256'],
                          'demo_ids': [donor], 'donor_snapshot_sha256': snapshot,
                          'graph_missing': reference['graph_missing'],
                          'tokens': {'code': metadata['target_tokens_used'], 'graph': metadata['graph_tokens_used'],
                                     'demo': metadata['demo_tokens_used'], 'total': total},
                          'truncated': {'code': metadata.get('target_truncated', False),
                                        'demo': metadata.get('demo_truncated', False),
                                        'graph': before.get('truncated', {}).get('graph', False)},
                          'previous_prompt_sha256': before['prompt_sha256'], 'previous_demo_ids': before['demo_ids'],
                          'prompt_changed_from_legacy': changed, 'fresh_inference_required': False}
                audit = {k: record[k] for k in ('id', 'dataset', 'split', 'prompt_sha256', 'previous_prompt_sha256',
                                               'reference_b2_prompt_sha256', 'demo_ids', 'previous_demo_ids', 'prompt_changed_from_legacy')}
                audit.update(true_demo_label=true_label, displayed_demo_label=1-true_label)
                pf.write(json.dumps(record, ensure_ascii=False) + '\n')
                af.write(json.dumps(audit, ensure_ascii=False) + '\n')
        if seen != set(legacy):
            raise ValueError('Legacy and new target sets differ')
        manifest = {'arm': 'B2-flip', 'dataset': dataset, 'split': split, 'count': len(seen), 'seed': 42,
                    'prompt_variant': VARIANT, 'donor_snapshot_sha256': snapshot,
                    'donor_bank_sha256': proofs[dataset]['proof']['new']['input_sha256'],
                    'reference_b2_prompts_sha256': sha(source),
                    'previous_prompts_sha256': legacy_manifest['prompts_sha256'],
                    'prompts_sha256': sha(prompt_path), 'pairing_audit_sha256': sha(audit_path),
                    'changed_from_legacy': changes, 'tokenizer': TOKENIZER, 'tokenizer_revision': TOKENIZER_REVISION,
                    'model_repo': expected_identity['model_repo'], 'quantization': 'Q4_K_M',
                    'model_sha256': MODEL_SHA, 'expected_llama_cpp_python': '0.3.16', 'prompt_budget_tokens': 8192,
                    'graph_prefix': {'nodes': 40, 'edges': 80}, 'retrieval_scope': 'audited_frozen_donor_B2_reference',
                    'source_sha256': sha(Path(__file__))}
        (folder / 'bundle_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
        archive = folder / f'{dataset}_{split}_b2_flip_kaggle.zip'
        with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
            for p in (prompt_path, audit_path, folder / 'bundle_manifest.json'):
                z.write(p, p.name)
        archives.append(archive)
        summary.append({'dataset': dataset, 'split': split, 'count': len(seen), 'changed': changes})
        print(summary[-1], flush=True)
    archive = out_root / 'grace_b2_flip_frozen_donor_inputs.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_STORED) as z:
        for p in archives:
            z.write(p, p.name)
    (out_root / 'prepare_summary.json').write_text(json.dumps({'splits': summary, 'bundle': archive.name,
        'bundle_sha256': sha(archive), 'donor_snapshot_sha256': snapshot, 'llm_calls': 0}, indent=2), encoding='utf-8')
    return archives, archive


if __name__ == '__main__':
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(TOKENIZER, revision=TOKENIZER_REVISION, local_files_only=True)
    prepare(tokenizer)
