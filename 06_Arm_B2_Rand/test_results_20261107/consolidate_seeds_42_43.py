"""Consolidate B2-rand test seeds 42 and 43 from the verified Kaggle exports."""
import ast
from datetime import datetime, timedelta, timezone
import hashlib
import io
import json
import math
from pathlib import Path
import zipfile

import sklearn

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUTPUTS = ROOT / 'Runs-management/kaggle_outputs_20261107'
TAIL = OUTPUTS / 'b2_rand_three_seed_test_tail_latest'
TAIL_RUN = TAIL / 'b2_rand_three_seed_test_tail'
KERNEL = 'quangdung1111/03-kaggle-qwen-q4-b2-rand-three-seed-test-tail-ipy'
sha = lambda raw: hashlib.sha256(raw).hexdigest()
read = lambda p: json.loads(p.read_bytes())
write = lambda p, obj: p.write_bytes((json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode())

def by_id(raw):
    result = {}
    for line in raw.splitlines(keepends=True):
        if not line.strip():
            continue
        row = json.loads(line)
        uid = str(row['id'])
        if uid in result:
            raise ValueError(f'Duplicate ID: {uid}')
        result[uid] = (row, line.rstrip(b'\r\n') + b'\n')
    return result

def threshold_lock(raw):
    lock = json.loads(raw)
    payload = {k:v for k,v in lock.items() if k != 'locked_sha256'}
    assert sha(json.dumps(payload, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()) == lock['locked_sha256']
    return lock

def checked_records(raw, prompts, seed, ds, manifest, runtime_sha, lock):
    entry = lock['entries'][f'B2-rand/{seed}/{ds}']
    tau = entry['tau_star']
    assert manifest['runtime_contract_sha256'] == runtime_sha and manifest['tau_star'] == tau
    assert manifest['threshold_lock_sha256'] == lock['locked_sha256']
    assert manifest['model_sha256'] == lock['model_sha256']
    records = by_id(raw)
    for uid, (row, _) in records.items():
        prompt = prompts[uid][0]
        assert (row['seed'], row['dataset'], row['split'], row['arm']) == (seed, ds, 'test', 'B2-rand')
        assert (row['label'], row['prompt_sha256']) == (prompt['label'], prompt['prompt_sha256'])
        assert sha(prompt['prompt'].encode()) == row['prompt_sha256']
        assert (row['runtime_contract_sha256'], row['threshold_lock_sha256'], row['tau']) == (runtime_sha, lock['locked_sha256'], tau)
        assert row['model_sha256'] == manifest['model_sha256']
        assert row['inference_seed'] == manifest['inference_seed']
        assert row['valid'] and all(math.isfinite(row[k]) for k in ('s', 'logprob_0', 'logprob_1'))
        assert 0 <= row['s'] <= 1 and row['pred_tau'] == int(row['s'] >= tau)
    return records

def run():
    summary = read(TAIL_RUN / 'batch_summary.json')
    status = read(TAIL_RUN / 'tail_status.json')
    assert summary['state'] == 'test_tail_complete' and status['state'] == 'complete'
    assert summary['new_records'] == {'42/reveal':257,'43/reveal':246,'44/reveal':374}
    assert status['completed_records_total'] == 877
    offload = (TAIL_RUN / 'model_load_offload.log').read_bytes()
    assert b'offloaded 49/49 layers to GPU' in offload
    tail_runtime = (TAIL_RUN / 'inference_runtime_lock.json').read_bytes()
    tail_runtime_sha = sha(tail_runtime)
    tail_threshold = (TAIL_RUN / 'threshold_lock.json').read_bytes()
    new_lock = threshold_lock(tail_threshold)
    assert summary['runtime_contract_sha256'] == tail_runtime_sha
    assert json.loads(tail_runtime)['packages']['scipy'] == '1.16.3'
    checkpoint = TAIL / 'grace_b2_rand_three_seed_test_tail_checkpoint.zip'
    tail_zip_bytes = checkpoint.read_bytes()
    scope = {'json':json, 'math':math, 'EXPECTED_LOCK_SEAL': new_lock['locked_sha256']}
    runner = (TAIL / 'kaggle_inference.py').read_text(encoding='utf-8')
    fn, = [node for node in ast.parse(runner).body if isinstance(node, ast.FunctionDef) and node.name == 'evaluate_output']
    exec(compile(ast.Module(body=[fn],type_ignores=[]), 'Kaggle evaluate_output','exec'), scope)
    evaluate = scope['evaluate_output']

    results = {}
    payloads = {}
    evidence = dict(tail_kernel=KERNEL, tail_checkpoint_sha256=sha(tail_zip_bytes),
        tail_runtime_sha256=tail_runtime_sha, tail_threshold_lock_sha256=new_lock['locked_sha256'],
        tail_started_at=status['started_at'],tail_completed_at=status['completed_at'],
        tail_output_counts=summary['new_records'],tail_offload_sha256=sha(offload),
        scoring='fixed_validation_threshold_no_test_fit', sklearn_version=sklearn.__version__, seeds={})
    with zipfile.ZipFile(io.BytesIO(tail_zip_bytes)) as tail_zip:
        assert tail_zip.testzip() is None
        assert tail_zip.read('inference_runtime_lock.json') == tail_runtime
        assert tail_zip.read('threshold_lock.json') == tail_threshold
        for seed, expected_tail in ((42,257),(43,246)):
            base = OUTPUTS / f'b2_rand_seed{seed}_test_latest'
            run_path = base / f'b2_rand_seed{seed}_test'
            old_runtime = (run_path / 'inference_runtime_lock.json').read_bytes()
            old_runtime_sha = sha(old_runtime)
            old_threshold = (run_path / 'threshold_lock.json').read_bytes()
            old_lock = threshold_lock(old_threshold)
            checkpoint_bytes = (base / f'grace_b2_rand_seed{seed}_test_checkpoint.zip').read_bytes()
            old_run = f'I-{18 if seed == 42 else 19}'
            seed_evidence = dict(original_run=old_run, original_checkpoint_sha256=sha(checkpoint_bytes),
                original_runtime_sha256=old_runtime_sha, original_threshold_lock_sha256=old_lock['locked_sha256'], datasets={})
            evidence['seeds'][str(seed)] = seed_evidence
            with zipfile.ZipFile(io.BytesIO(checkpoint_bytes)) as original:
                assert original.testzip() is None
                assert original.read('inference_runtime_lock.json') == old_runtime
                assert original.read('threshold_lock.json') == old_threshold
                for ds, n in (('devign',2732),('reveal',2274)):
                    rel = f'seed_{seed}/{ds}/test/records.jsonl'
                    mp = Path(rel).with_name('run_manifest.json').as_posix()
                    old_raw = original.read(rel)
                    assert old_raw == (run_path / rel).read_bytes()
                    manifest = json.loads(original.read(mp))
                    input_zip = (base / 'b2_rand_test_bundles' / f'{ds}_test.zip').read_bytes()
                    assert sha(input_zip) == manifest['bundle_sha256']
                    with zipfile.ZipFile(io.BytesIO(input_zip)) as z:
                        prompts = by_id(z.read('prompts.jsonl'))
                    assert len(prompts) == n
                    key = f'B2-rand/{seed}/{ds}'
                    for field in ('tau_star','validation_records_sha256','validation_prompt_set_sha256','model_sha256','split_used'):
                        assert old_lock['entries'][key][field] == new_lock['entries'][key][field]
                    old_rows = checked_records(old_raw, prompts, seed, ds, manifest, old_runtime_sha, old_lock)
                    missing = prompts.keys() - old_rows.keys()
                    sources = [dict(run=old_run, n=len(old_rows), records_sha256=sha(old_raw), manifest=manifest)]
                    added = {}
                    if ds == 'reveal':
                        tail_raw = tail_zip.read(rel)
                        assert tail_raw == (TAIL_RUN / rel).read_bytes()
                        tail_manifest = json.loads(tail_zip.read(mp))
                        added = checked_records(tail_raw, prompts, seed, ds, tail_manifest, tail_runtime_sha, new_lock)
                        assert len(added) == expected_tail and added.keys() == missing
                        for field in ('model_sha256','tokenizer_revision','inference_seed','scoring','context_tokens','runtime_constructor','backend_sdist_sha256'):
                            assert manifest[field] == tail_manifest[field], field
                        sources.append(dict(run='I-20', n=len(added), records_sha256=sha(tail_raw), manifest=tail_manifest))
                    else:
                        assert not missing
                    merged = old_rows | added
                    assert merged.keys() == prompts.keys()
                    data = b''.join(merged[uid][1] for uid in prompts)
                    seed_evidence['datasets'][ds] = dict(records_sha256=sha(data), n=len(merged), sources=sources)
                    payloads[rel] = data

    for rel,data in payloads.items():
        target = HERE / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        seed, ds = Path(rel).parts[:2]
        detail = evidence['seeds'][seed.removeprefix('seed_')]['datasets'][ds]
        metrics = evaluate(target)
        assert metrics['n_score_valid'] == metrics['n_total'] == detail['n']
        metrics.pop('threshold_lock_sha256')
        metrics['threshold_lock_sha256_by_run'] = {x['run']:x['manifest']['threshold_lock_sha256'] for x in detail['sources']}
        metrics['runtime_contract_sha256_by_run'] = {x['run']:x['manifest']['runtime_contract_sha256'] for x in detail['sources']}
        metrics['records_sha256'] = detail['records_sha256']
        write(target.with_name('evaluation.json'), metrics)
        results[f'{seed}/{ds}'] = metrics
    write(HERE/'provenance.json', evidence)
    write(HERE/'evaluation_summary.json', results)
    ict = timezone(timedelta(hours=7))
    for k in ('started_at','completed_at'):
        print(k, datetime.fromisoformat(status[k]).astimezone(ict).isoformat())
    print('checkpoint',evidence['tail_checkpoint_sha256'])
    print('runtime',tail_runtime_sha)
    for key,metrics in results.items():
        print(key, metrics['n_total'], metrics['tau'], {k:round(metrics[k],6) for k in ('mcc','auroc','average_precision','f1','balanced_accuracy')})

if __name__ == '__main__':
    run()
