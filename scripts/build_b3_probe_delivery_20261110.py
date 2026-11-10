"""Build both probe deliveries from the sealed B3 census and canonical renderer.

Does not upload or launch kernels. Never opens held-out test labels.
"""
import ast
import base64
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import zipfile
from functools import lru_cache

R = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(R / 'scripts'), str(R / '01_Author_Baseline_Unified/diagnostic_kit/src')]
from b3_test_runtime import load_manifest, validate_archive, read_dataset_rows, load_threshold
from build_b3_test_prompts_20261109 import TOKENIZER, POOLS, FREEZE, ARCHIVE, get_member, read_jsonl, ordered
from grace_diag.amended_b3 import VerifiedPairSelector
from grace_diag.probes import split_blocks
from grace_diag.token_budget import TokenCounter

BASE = R / 'Runs-management/b3_verified_patch_v1/test_release_20261109_v1'
OUT = R / 'Runs-management/b3_verified_patch_v1/probe_test_release_20261110_v1'
ARMS = ('B3-swap', 'B3-flip')

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def js(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def main():
    if OUT.exists() and any(p.name != 'shared_worker' for p in OUT.iterdir()):
        raise FileExistsError('Preserve existing release; select a new version instead')
    base_sha = sha((BASE / 'test_release_manifest.json').read_bytes())
    if base_sha != (BASE / 'test_release_manifest.sha256').read_text(encoding='ascii').split()[0]:
        raise ValueError('Base B3 manifest differs from its published seal')
    root = load_manifest(BASE / 'test_release_manifest.json', base_sha)
    members = validate_archive(BASE / 'kaggle_input.zip', root)
    counter = TokenCounter(str(TOKENIZER))
    if counter.approx:
        raise ValueError('Exact tokenizer required')
    # The same donor functions and target blocks occur in all four family arms.
    # Cache exact counts only; no approximation or alternative trimming policy.
    counter.count = lru_cache(maxsize=50000)(counter.count)
    counter.count_chat = lru_cache(maxsize=15000)(counter.count_chat)
    template = json.loads((BASE / 'kaggle_kernel/notebook.ipynb').read_text(encoding='utf-8'))
    if len(template['cells']) != 6 or [x['cell_type'] for x in template['cells']] != ['markdown'] + ['code'] * 5:
        raise ValueError('Unexpected canonical notebook format')
    shared = {
        n: (BASE / 'worker' / n).read_bytes()
        for n in ('grace_runtime_contract.py', 'b3_native_runtime.py', 'kaggle_inference_test.py')
    }
    worker = shared['kaggle_inference_test.py'].decode('utf-8')
    old = "return ({'arm':'B3','seed':42,'dataset':dataset,'split':'test',"
    if worker.count(old) != 1:
        raise ValueError('Unexpected canonical worker')
    worker = worker.replace(old, "return ({'arm':INPUT_ROOT['arm'],'seed':42,'dataset':dataset,'split':'test',")
    shared['kaggle_inference_test.py'] = worker.encode('utf-8')
    shared['b3_test_runtime.py'] = (R / 'scripts/b3_test_runtime.py').read_bytes()
    shared['inference_runtime_lock.json'] = members['inference_runtime_lock.json']
    for n, raw in shared.items():
        if n.endswith('.py'):
            ast.parse(raw.decode('utf-8'))
        (OUT / 'shared_worker').mkdir(parents=True, exist_ok=True)
        (OUT / 'shared_worker' / n).write_bytes(raw)
    outputs = {arm: {} for arm in ARMS}
    reports = {arm: {} for arm in ARMS}
    with zipfile.ZipFile(ARCHIVE) as z:
        for ds in ('devign', 'reveal'):
            originals = read_dataset_rows(members, root, ds)
            specs = read_jsonl(get_member(z, ds + '_test_15arms.jsonl')[1])
            specs = {s['id']: s for s in specs}
            train = FREEZE / ds
            kept = {x['id'] for x in read_jsonl((train / 'train_manifest.jsonl').read_bytes()) if x['keep_in_bank']}
            bank = {x['id']: dict(x, function_uid=x['id']) for x in read_jsonl((train / 'train_raw.jsonl').read_bytes()) if x['id'] in kept}
            if sha(POOLS[ds].read_bytes()) != root['datasets'][ds]['pool_sha256']:
                raise ValueError('Pool changed after B3 lock')
            selector = VerifiedPairSelector(read_jsonl(POOLS[ds].read_bytes()), bank, ds)
            for arm in ARMS:
                outputs[arm][ds] = []
            for i, original in enumerate(originals):
                spec = specs[original['id']]
                target = {k: spec.get(k, '') for k in ('id', 'query_code', 'nodes', 'edges')}
                family = selector.render_family(target, counter)
                if family['B3']['prompt'] != original['prompt'] or family['B3']['selection'] != original['selection']:
                    raise ValueError('Re-rendered B3 differs from sealed baseline: ' + original['id'])
                base_blocks = split_blocks(original['prompt'])
                for arm in ARMS:
                    rendered = family[arm]
                    prompt, ev = rendered['prompt'], rendered['evidence']
                    blocks = split_blocks(prompt)
                    if any(blocks[k] != base_blocks[k] for k in base_blocks if k != 'demo'):
                        raise ValueError('Probe changed a non-demonstration block')
                    tokens = ev['tokens']
                    chat = counter.count_chat(prompt)
                    if not ordered(prompt, ev) or chat + 64 > 8192 or any(tokens[k] > cap for k, cap in [('code', 3000), ('graph', 1500), ('demo', 1500)]):
                        raise ValueError('Prompt order/token budget failure')
                    row = dict(original, arm=arm, prompt=prompt, prompt_sha256=sha(prompt.encode('utf-8')),
                               token_audit=tokens, chat_tokens=chat, threshold_from='B3',
                               base_prompt_sha256=original['prompt_sha256'])
                    outputs[arm][ds].append(row)
                if (i + 1) % 250 == 0:
                    print(f'{ds}: {i + 1}/{len(originals)} paired probes verified', flush=True)
            for arm in ARMS:
                reports[arm][ds] = {'rows': len(originals), 'max_chat_tokens': max(r['chat_tokens'] for r in outputs[arm][ds]),
                    'base_prompt_and_selection_match': True, 'non_demo_blocks_identical': True,
                    'canonical_render_family': True, 'exact_tokenizer': True, 'target_label_fields_absent': True}
    inventory = {}
    for arm in ARMS:
        slug = arm.lower().replace('-', '_')
        dest = OUT / slug
        payload = {n: raw for n, raw in members.items() if not n.startswith('prompts/')}
        variant = deepcopy(root)
        variant.update(arm=arm, release_id=slug + '_test_release_20261110_v1', threshold_from='B3',
                       base_release_manifest_sha256=base_sha, test_worker_sha256=sha(shared['kaggle_inference_test.py']))
        variant['shared_worker_sha256'] = {n: sha(raw) for n, raw in shared.items()}
        for ds in ('devign', 'reveal'):
            raw = ''.join(json.dumps(row, ensure_ascii=False, separators=(',', ':')) + '\n' for row in outputs[arm][ds]).encode('utf-8')
            payload[f'prompts/{ds}.jsonl'] = raw
            variant['datasets'][ds]['prompts_sha256'] = sha(raw)
            variant['datasets'][ds]['base_prompts_sha256'] = root['datasets'][ds]['prompts_sha256']
            # The base census is historical, not a probe census.
            variant['datasets'][ds].pop('census_sha256', None)
            load_threshold(variant, payload, ds)
        for n, raw in payload.items():
            p = dest / 'kaggle_dataset/kaggle_input' / n
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(raw)
        archive = dest / 'kaggle_dataset/kaggle_input.zip'
        with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
            for n, raw in sorted(payload.items()):
                info = zipfile.ZipInfo(n, date_time=(2026, 11, 10, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(info, raw)
        variant['kaggle_input_members_sha256'] = {n: sha(raw) for n, raw in payload.items()}
        variant['kaggle_input_archive_sha256'] = sha(archive.read_bytes())
        manifest = dest / 'kaggle_dataset/test_release_manifest.json'
        js(manifest, variant)
        msha = sha(manifest.read_bytes())
        (manifest.parent / 'test_release_manifest.sha256').write_text(msha + '  test_release_manifest.json\n', encoding='ascii')
        check = load_manifest(manifest, msha)
        checked = validate_archive(archive, check)
        for ds in ('devign', 'reveal'):
            read_dataset_rows(checked, check, ds)
            load_threshold(check, checked, ds)
        nb = deepcopy(template)
        nb['cells'][0]['source'] = [f'# {arm} verified-patch v1 — test-only Devign + REVEAL\n',
            'Shared evaluator and locked runtime; B3 validation thresholds inherited. Test labels remain local.\n']
        source1 = ''.join(nb['cells'][1]['source'])
        node = ast.parse(source1)
        loop = next(n for n in node.body if isinstance(n, ast.For))
        assignment = loop.iter
        if not isinstance(assignment, ast.Call) or not isinstance(assignment.func, ast.Attribute):
            raise ValueError('Unknown embedded-worker notebook format')
        literal = assignment.func.value
        lines = source1.splitlines(keepends=True)
        start = sum(len(l) for l in lines[:literal.lineno - 1]) + literal.col_offset
        end = sum(len(l) for l in lines[:literal.end_lineno - 1]) + literal.end_col_offset
        embeds = {n: base64.b64encode(raw).decode('ascii') for n, raw in shared.items()}
        source1 = source1[:start] + repr(embeds) + source1[end:]
        nb['cells'][1]['source'] = source1.splitlines(keepends=True)
        pre = ''.join(nb['cells'][2]['source']).replace(base_sha, msha)
        dataset_slug = 'grace-' + arm.lower() + '-test-release-20261110-v1'
        pre = pre.replace('grace-b3-test-release-20261109-v1', dataset_slug)
        pre += "\nfor name, expected in ROOT['shared_worker_sha256'].items():\n if digest(WORK/name)!=expected: raise RuntimeError('Shared worker hash mismatch: '+name)\n"
        pre += f"if ROOT['arm'] != {arm!r}: raise RuntimeError('Notebook arm differs from manifest')\n"
        nb['cells'][2]['source'] = pre.splitlines(keepends=True)
        launch = ''.join(nb['cells'][5]['source']).replace('b3_test_release_20261109', slug + '_test_release_20261110')
        launch = launch.replace("'--arm','B3'", "'--arm'," + repr(arm))
        if "'--arm'," + repr(arm) not in launch:
            raise ValueError('Launch arm not bound')
        nb['cells'][5]['source'] = launch.splitlines(keepends=True)
        for cell in nb['cells']:
            if cell['cell_type'] == 'code':
                cell.update(execution_count=None, outputs=[])
                ast.parse(''.join(cell['source']))
        for i in (3, 4):
            if nb['cells'][i]['source'] != template['cells'][i]['source']:
                raise ValueError('Setup cells diverged')
        js(dest / 'kaggle_kernel/notebook.ipynb', nb)
        meta = json.loads((BASE / 'kaggle_kernel/kernel-metadata.json').read_text(encoding='utf-8'))
        meta.update(id='lznt123/grace-' + arm.lower() + '-test-20261110-v1',
                    title='grace-' + arm.lower() + '-test-20261110-v1', dataset_sources=['lznt123/' + dataset_slug])
        js(dest / 'kaggle_kernel/kernel-metadata.json', meta)
        js(dest / 'kaggle_dataset/dataset-metadata.json', {'id': 'lznt123/' + dataset_slug,
            'title': arm + ' test release 20261110 v1', 'licenses': [{'name': 'other'}]})
        inventory[arm] = {'manifest_sha256': msha, 'notebook_sha256': sha((dest / 'kaggle_kernel/notebook.ipynb').read_bytes()),
                          'datasets': reports[arm], 'status': 'LOCAL_READY_REMOTE_RUNTIME_PENDING'}
    js(OUT / 'PREPARATION_AUDIT.json', {'status': 'PASS', 'base_manifest_sha256': base_sha,
        'shared_worker_sha256': {n: sha(raw) for n, raw in shared.items()}, 'arms': inventory,
        'remote_upload': False, 'runtime_certified': False})
    print(json.dumps(inventory, indent=2), flush=True)

if __name__ == '__main__':
    main()
