"""Acceptance checks against the real, sealed probe deliveries (no GPU required)."""
import ast
import base64
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

import pytest

R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R / 'scripts'))
from b3_test_runtime import load_manifest, validate_archive, read_dataset_rows, load_threshold, checked_records

BASE = R / 'Runs-management/b3_verified_patch_v1/test_release_20261109_v1'
OUT = R / 'Runs-management/b3_verified_patch_v1/probe_test_release_20261110_v1'

@pytest.fixture(scope='module', params=['B3-swap', 'B3-flip'])
def delivery(request):
    path = OUT / request.param.lower().replace('-', '_')
    manifest = path / 'kaggle_dataset/test_release_manifest.json'
    root = load_manifest(manifest, hashlib.sha256(manifest.read_bytes()).hexdigest())
    return path, root, validate_archive(path / 'kaggle_dataset/kaggle_input.zip', root)

def test_exact_threshold_inheritance_and_tamper_rejection(delivery):
    _, root, members = delivery
    for ds, expected in [('devign', 2732), ('reveal', 2274)]:
        assert len(read_dataset_rows(members, root, ds)) == expected
        lock = f'threshold_locks/{ds}_threshold_lock.json'
        assert members[lock] == (BASE / 'kaggle_input' / lock).read_bytes()
        assert load_threshold(root, members, ds) == {'devign': .99, 'reveal': .01}[ds]
        altered = dict(members, **{lock: members[lock] + b' '})
        with pytest.raises(ValueError, match='checksum'):
            load_threshold(root, altered, ds)

def test_cross_arm_resume_and_prompt_contamination_rejected(delivery, tmp_path):
    _, root, members = delivery
    rows = read_dataset_rows(members, root, 'devign')
    with pytest.raises(ValueError, match='Resume arm'):
        checked_records(tmp_path, root, rows, 'devign', arm='B3')
    altered = dict(members)
    row = deepcopy(rows[0])
    row['arm'] = 'B3'
    raw = (json.dumps(row) + '\n').encode()
    altered['prompts/devign.jsonl'] = raw
    bad = deepcopy(root)
    bad['datasets']['devign'].update(expected=1, prompts_sha256=hashlib.sha256(raw).hexdigest())
    with pytest.raises(ValueError, match='arm mismatch'):
        read_dataset_rows(altered, bad, 'devign')

def test_notebook_shared_setup_and_identical_embedded_worker(delivery):
    path, root, _ = delivery
    nb = json.loads((path / 'kaggle_kernel/notebook.ipynb').read_text(encoding='utf-8'))
    base = json.loads((BASE / 'kaggle_kernel/notebook.ipynb').read_text(encoding='utf-8'))
    assert [c['cell_type'] for c in nb['cells']] == [c['cell_type'] for c in base['cells']]
    for i in (3, 4):
        assert nb['cells'][i]['source'] == base['cells'][i]['source']
    for cell in nb['cells'][1:]:
        assert cell['execution_count'] is None and cell['outputs'] == []
        ast.parse(''.join(cell['source']))
    tree = ast.parse(''.join(nb['cells'][1]['source']))
    loop = next(n for n in tree.body if isinstance(n, ast.For))
    embeds = ast.literal_eval(loop.iter.func.value)
    for name, encoded in embeds.items():
        raw = base64.b64decode(encoded)
        assert raw == (OUT / 'shared_worker' / name).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == root['shared_worker_sha256'][name]
    launch = ''.join(nb['cells'][5]['source'])
    assert repr(root['arm']) in launch and '--arm' in launch

def test_scoring_runtime_helpers_unchanged():
    for name in ('grace_runtime_contract.py', 'b3_native_runtime.py'):
        assert (OUT / 'shared_worker' / name).read_bytes() == (BASE / 'worker' / name).read_bytes()
    base = (BASE / 'worker/kaggle_inference_test.py').read_text(encoding='utf-8')
    probe = (OUT / 'shared_worker/kaggle_inference_test.py').read_text(encoding='utf-8')
    assert probe == base.replace("return ({'arm':'B3','seed':42,'dataset':dataset,'split':'test',",
                                "return ({'arm':INPUT_ROOT['arm'],'seed':42,'dataset':dataset,'split':'test',")

def test_full_census_probe_changes_only_intended_demonstration(delivery):
    sys.path.insert(0, str(R / '01_Author_Baseline_Unified/diagnostic_kit/src'))
    from grace_diag.probes import split_blocks, _flip_words
    _, root, members = delivery
    original_root = json.loads((BASE / 'test_release_manifest.json').read_bytes())
    original_members = validate_archive(BASE / 'kaggle_input.zip', original_root)
    h1, h0 = 'The following example is Vulnerable.\n', 'The following example is Non-vulnerable.\n'
    for ds in ('devign', 'reveal'):
        originals = read_dataset_rows(original_members, original_root, ds)
        variants = read_dataset_rows(members, root, ds)
        for original, row in zip(originals, variants):
            assert row['id'] == original['id'] and row['selection'] == original['selection']
            before, after = split_blocks(original['prompt']), split_blocks(row['prompt'])
            assert all(before[k] == after[k] for k in before if k != 'demo')
            pair, sep, diff = before['demo'].rpartition('\n\nKey difference: ')
            assert sep
            vulnerable, sep, safe = pair.partition('\n\n' + h0)
            assert sep and vulnerable.startswith(h1)
            if root['arm'] == 'B3-swap':
                expected = h0 + safe + '\n\n' + vulnerable + '\n\nKey difference: ' + diff
            else:
                expected = h0 + vulnerable[len(h1):] + '\n\n' + h1 + safe + '\n\nKey difference: ' + _flip_words(diff)
            assert after['demo'] == expected
