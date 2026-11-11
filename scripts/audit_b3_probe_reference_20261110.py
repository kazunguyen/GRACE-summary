"""Compare probe runtime and evaluator against the five-arm locked ZIP."""
import ast
import hashlib
import json
from pathlib import Path
import zipfile

R = Path(__file__).resolve().parents[1]
OUT = R / 'Runs-management/b3_verified_patch_v1/probe_test_release_20261110_v1'
ZIP = R / 'Runs-management/grace_hieu_5arms_runtime_locked_20261107.zip'

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def function(source, name):
    return ast.dump(next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == name), include_attributes=False)

def main():
    assert sha(ZIP.read_bytes()) == '76a49a770897b7d0832ee87aa7d7e308ebbca57fdd7aaaf02f0f07f2400f156c'
    current = json.loads((OUT / 'shared_worker/inference_runtime_lock.json').read_bytes())
    worker = (OUT / 'shared_worker/kaggle_inference_test.py').read_text(encoding='utf-8')
    comparisons = []
    with zipfile.ZipFile(ZIP) as z:
        assert z.testzip() is None
        for name in z.namelist():
            nb = json.loads(z.read(name))
            lock_bytes, runner = None, None
            for cell in nb['cells']:
                if cell['cell_type'] != 'code':
                    continue
                s = ''.join(cell['source'])
                if s.startswith('%%writefile'):
                    runner = '\n'.join(s.splitlines()[1:])
                    continue
                for n in ast.walk(ast.parse(s)):
                    if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'RUNTIME_LOCK_BYTES' for t in n.targets):
                        lock_bytes = ast.literal_eval(n.value)
            assert sha(lock_bytes) == '85d8770839f80260cdc7c27b27b6cce6bf8815675c8593db68fb102589c5cbd6'
            old = json.loads(lock_bytes)
            keys = ('model', 'tokenizer', 'backend_source', 'constructor', 'gpu', 'scoring', 'threads', 'build', 'decoding', 'resume')
            same = {k: old[k] == current[k] for k in keys}
            assert all(same.values()), (name, same)
            assert current['packages'] == dict(old['packages'], scipy='1.16.3')
            assert function(runner, 'binary_scores') == function(worker, 'binary_scores')
            comparisons.append({'notebook': name, 'same_core_contract': same,
                'binary_scores_ast_identical': True, 'package_difference': {'added': {'scipy': '1.16.3'}}})
    report = {'status': 'PASS', 'reference_zip_sha256': sha(ZIP.read_bytes()),
        'current_runtime_sha256': sha((OUT / 'shared_worker/inference_runtime_lock.json').read_bytes()),
        'comparisons': comparisons, 'amendment_reference': 'worklogs/2026-11-07_kaggle_package_lock_standardization.md',
        'notebook_format': 'B3 v6: 1 markdown + 5 executable cells; setup and environment cells unchanged',
        'historical_format_note': 'Five-arm validation ZIP has additional legacy bundle/checkpoint/diagnostic cells; its historical notebooks are preserved.',
        'runtime_certification': 'PENDING_GPU_EXECUTION'}
    (OUT / 'REFERENCE_RUNTIME_AUDIT.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
