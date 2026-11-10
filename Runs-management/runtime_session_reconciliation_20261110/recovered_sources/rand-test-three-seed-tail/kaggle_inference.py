import argparse
import hashlib
import json
import math
import os
import platform
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from grace_runtime_contract import load_contract, provenance, load_locked_model, EXPECTED_CONTRACT_SHA256
RUNTIME = load_contract()

EXPECTED_LOCK_SEAL = '48c12066bbddabc8ef674a70f6f9ac68cb74cbeecc2a5ebbbda3cb4cb6498735'


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def write_json_atomic(path, payload):
    path = Path(path)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(payload, indent=2), encoding='utf-8')
    os.replace(tmp, path)


def binary_scores(logits, label_ids):
    values = np.asarray(logits, dtype=np.float64).reshape(-1)
    if not np.all(np.isfinite(values)):
        raise ValueError('Non-finite logits')
    maximum = np.max(values)
    normalizer = float(maximum + np.log(np.exp(values - maximum).sum()))
    lp0 = float(values[label_ids[0]] - normalizer)
    lp1 = float(values[label_ids[1]] - normalizer)
    score = float(np.exp(lp1 - np.logaddexp(lp0, lp1)))
    best = int(np.argmax(values))
    top = np.argsort(values)[-5:][::-1]
    return {'logprob_0': lp0, 'logprob_1': lp1, 'p0': math.exp(lp0), 'p1': math.exp(lp1),
            's': score, 'pred_argmax': int(score >= 0.5), 'greedy_token_id': best,
            'top5': [{'token_id': int(i), 'logprob': float(values[i] - normalizer)} for i in top]}


def load_bundle(bundle):
    with zipfile.ZipFile(bundle) as z:
        manifest = json.loads(z.read('bundle_manifest.json'))
        prompt_bytes = z.read('prompts.jsonl')
        lock = json.loads(z.read('threshold_lock.json'))
    seal = lock.get('locked_sha256')
    unsigned = {k:v for k,v in lock.items() if k!='locked_sha256'}
    actual = hashlib.sha256(json.dumps(unsigned,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
    if seal != actual or seal != EXPECTED_LOCK_SEAL or manifest.get('threshold_lock_sha256') != seal:
        raise ValueError('B2-rand validation lock integrity mismatch')
    ds, seed = manifest['dataset'], manifest['seed']
    entry = lock['entries'][f"B2-rand/{seed}/{ds}"]
    if (manifest.get('arm'), manifest.get('split')) != ('B2-rand','test'):
        raise ValueError('Only B2-rand test bundles are accepted')
    if manifest.get('tau_star') != entry['tau_star'] or lock.get('model_sha256') != manifest.get('model_sha256'):
        raise ValueError('Test bundle does not use its locked validation threshold/model')
    if hashlib.sha256(prompt_bytes).hexdigest() != manifest['prompts_sha256']:
        raise ValueError(f'Prompt bundle hash mismatch: {bundle}')
    rows = [json.loads(line) for line in prompt_bytes.decode('utf-8').splitlines() if line.strip()]
    if len(rows) != manifest['count'] or len({str(r['id']) for r in rows}) != len(rows):
        raise ValueError('Prompt count/unique ID mismatch')
    for row in rows:
        if (row.get('arm'),row.get('seed'),row.get('dataset'),row.get('split')) != ('B2-rand',seed,ds,'test'):
            raise ValueError('Wrong test prompt identity')
        if hashlib.sha256(row['prompt'].encode('utf-8')).hexdigest() != row['prompt_sha256']:
            raise ValueError('Test prompt hash mismatch')
    manifest['model_repo'] = 'ggml-org/Qwen3-Coder-30B-A3B-Instruct-GGUF'
    manifest['prompt_budget_tokens'] = 8192
    return manifest, rows


def evaluate_output(output):
    from sklearn.metrics import (accuracy_score, average_precision_score, balanced_accuracy_score,
                                 confusion_matrix, f1_score, matthews_corrcoef, precision_score,
                                 recall_score, roc_auc_score)
    records = [json.loads(line) for line in output.read_text(encoding='utf-8').splitlines() if line.strip()]
    rows = [r for r in records if r['valid'] and math.isfinite(r['s'])]
    if not rows: raise ValueError('No valid test scores')
    y = [r['label'] for r in rows]
    pred = [r['pred_tau'] for r in rows]
    scores = [r['s'] for r in rows]
    # Score-valid rows remain included even when the raw greedy token is not 0/1.
    return dict(n_total=len(records), n_score_valid=len(rows),
                n_response_valid=sum(r['response_valid'] for r in records),
                tau=rows[0]['tau'], threshold_lock_sha256=EXPECTED_LOCK_SEAL,
                accuracy=accuracy_score(y,pred), balanced_accuracy=balanced_accuracy_score(y,pred),
                precision=precision_score(y,pred,zero_division=0), recall=recall_score(y,pred,zero_division=0),
                f1=f1_score(y,pred,zero_division=0),
                mcc=matthews_corrcoef(y,pred) if len(set(y))==2 and len(set(pred))==2 else None,
                confusion_matrix=confusion_matrix(y,pred,labels=[0,1]).tolist(),
                auroc=roc_auc_score(y,scores) if len(set(y))==2 else None,
                average_precision=average_precision_score(y,scores) if len(set(y))==2 else None,
                threshold_policy='inherit_completed_Kaggle_validation_no_test_fit')


def snapshot(status_path):
    root = Path(status_path).parent
    target = root.parent / ('grace_' + root.name + '_checkpoint.zip')
    temporary = target.with_suffix('.zip.tmp')
    with zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(root.rglob('*')):
            if path.is_file() and not path.name.endswith('.tmp'):
                archive.write(path, path.relative_to(root).as_posix())
    os.replace(temporary, target)


def run_batch(runs, model_path, model_revision, gpu_layers, limit, deadline_epoch,
              checkpoint_reserve_seconds, status_path, expected_model_sha256, arm):
    import llama_cpp
    from llama_cpp import Llama, __version__ as llama_version, LLAMA_DEFAULT_SEED
    from transformers import AutoTokenizer
    if llama_version != '0.3.16': raise ValueError(f'Backend version mismatch: {llama_version}')
    inference_seed = RUNTIME['constructor']['seed']

    if arm != 'B2-rand' or limit is not None or not (1 <= len(runs) <= 6) or any(s not in (42, 43, 44) or d not in ('devign', 'reveal') or split != 'test' for s, d, split, _, _ in runs):
        raise ValueError('Only B2-rand test tails for seeds 42, 43 and 44 are allowed')
    if len({(s,d) for s,d,_,_,_ in runs}) != len(runs):
        raise ValueError('Duplicate seed/dataset run')
    started = time.time()
    durations = []
    last_snapshot = started
    stop_at = deadline_epoch - checkpoint_reserve_seconds
    status_path = Path(status_path)
    status_path.parent.mkdir(parents=True, exist_ok=True)
    status = {'state': 'starting', 'timed_out': False,
              'started_at': datetime.fromtimestamp(started, timezone.utc).isoformat(),
              'deadline_at': datetime.fromtimestamp(deadline_epoch, timezone.utc).isoformat(),
              'stop_new_records_at': datetime.fromtimestamp(stop_at, timezone.utc).isoformat(),
              'max_runtime_hours': (deadline_epoch - started) / 3600,
              'checkpoint_reserve_seconds': checkpoint_reserve_seconds,
              'runs': {}, 'completed_records_total': 0}
    for prompt_seed, dataset, split, bundle, out in runs:
        key = f'{prompt_seed}/{dataset}/{split}'
        status['runs'][key] = {'state': 'pending', 'bundle': bundle, 'output': out}
    write_json_atomic(status_path, status)

    def stop_for_deadline(current=None):
        status['state'] = 'timed_out'
        status['timed_out'] = True
        status['timed_out_at'] = datetime.now(timezone.utc).isoformat()
        status['stopped_after_run'] = current
        write_json_atomic(status_path, status)

    if time.time() >= stop_at:
        stop_for_deadline(None)
        return

    model_path = Path(model_path)
    model_digest = sha256(model_path)
    if model_digest != expected_model_sha256: raise ValueError('Model SHA256 không khớp contract')
    if model_revision == 'local-input':
        model_revision = f'local-sha256:{model_digest}'
    first_manifest, _ = load_bundle(runs[0][3])
    for prompt_seed, dataset, split, bundle, out in runs:
        current_manifest, _ = load_bundle(bundle)
        if (current_manifest['tokenizer'], current_manifest['tokenizer_revision'],
            current_manifest['prompt_budget_tokens']) != (first_manifest['tokenizer'],
            first_manifest['tokenizer_revision'], first_manifest['prompt_budget_tokens']):
            raise ValueError('All bundles must use the same tokenizer revision and context budget')
    tokenizer = AutoTokenizer.from_pretrained(first_manifest['tokenizer'],
                                                revision=first_manifest['tokenizer_revision'])
    runtime_info = provenance(RUNTIME, __file__, status_path.parent / 'runtime_provenance.json')
    llm = load_locked_model(RUNTIME, model_path, first_manifest, gpu_layers, status_path.parent / 'model_load_offload.log')
    runtime_info['gpu_after_load'] = __import__('grace_runtime_contract').command(['nvidia-smi','--query-gpu=index,uuid,name,memory.free,memory.total,driver_version','--format=csv,noheader'])
    runtime_info['offload_log_sha256'] = sha256(status_path.parent / 'model_load_offload.log')
    (status_path.parent / 'runtime_provenance.json').write_text(json.dumps(runtime_info,indent=2),encoding='utf-8')
    if time.time() >= stop_at:
        stop_for_deadline(None)
        return
    label_ids = []
    for label in ('0', '1'):
        hf_ids = tokenizer.encode(label, add_special_tokens=False)
        gguf_ids = llm.tokenize(label.encode(), add_bos=False, special=False)
        if len(hf_ids) != 1 or hf_ids != gguf_ids:
            raise ValueError(f'Label token mismatch for {label}: HF={hf_ids}, GGUF={gguf_ids}')
        label_ids.append(hf_ids[0])
    if label_ids[0] == label_ids[1]:
        raise ValueError('Label token IDs must differ')

    status['state'] = 'running'
    write_json_atomic(status_path, status)
    for prompt_seed, dataset, split, bundle, out_text in runs:
        key = f'{prompt_seed}/{dataset}/{split}'
        out = Path(out_text)
        out.mkdir(parents=True, exist_ok=True)
        manifest, rows = load_bundle(bundle)
        if (manifest.get('arm'), manifest.get('seed'), manifest['dataset'], manifest['split']) != (arm, prompt_seed, dataset, split):
            raise ValueError(f'Bundle identity mismatch for {key}: {manifest["dataset"]}/{manifest["split"]}')
        if limit is not None:
            rows = rows[:limit]
        identity = {'bundle_sha256': sha256(bundle),
                    'prompt_set_sha256': manifest['prompts_sha256'], 'model_sha256': model_digest,
                    'model_repo': manifest['model_repo'], 'quantization': manifest['quantization'],
                    'model_file': model_path.name, 'llama_cpp_python': llama_version,
                    'model_repo_revision': model_revision, 'tokenizer': manifest['tokenizer'],
                    'tokenizer_revision': manifest['tokenizer_revision'], 'gpu_layers': gpu_layers,
                    'context_tokens': manifest['prompt_budget_tokens'],
                    'scoring': 'unconstrained_first_token_logits_v1', 'limit': limit,
                    'python': platform.python_version(), 'dataset': dataset, 'split': split, 'arm': arm, 'prompt_seed': prompt_seed,
                    'inference_seed': inference_seed, 'inference_seed_policy': 'llama_cpp_default',
                    'threshold_lock_sha256': EXPECTED_LOCK_SEAL, 'tau_star': manifest['tau_star'],
                    'n_batch': RUNTIME['constructor']['n_batch'], 'runtime_contract_sha256':EXPECTED_CONTRACT_SHA256, 'runtime_constructor':RUNTIME['constructor'], 'runtime_packages':RUNTIME['packages'], 'backend_sdist_sha256':RUNTIME['backend_source']['sdist_sha256']}
        identity_file = out / 'run_manifest.json'
        previous_identity = (json.loads(identity_file.read_text(encoding='utf-8'))
                             if identity_file.exists() else None)
        if previous_identity is not None:
            # Ignore only archive-byte hashes: ZIP timestamps/compression metadata may change.
            # Prompt identity is verified below against every checkpoint row's prompt_sha256.
            ignored = {'bundle_sha256', 'prompt_set_sha256'}
            previous_stable = {k: v for k, v in previous_identity.items() if k not in ignored}
            current_stable = {k: v for k, v in identity.items() if k not in ignored}
            if previous_stable != current_stable:
                raise ValueError(f'Existing output has different model/run settings for {key}; use a new OUT_ROOT')
            if ('prompt_set_sha256' in previous_identity and
                    previous_identity['prompt_set_sha256'] != identity['prompt_set_sha256']):
                raise ValueError(f'Prompt bundle content changed for {key}; refusing to resume')
        output = out / 'records.jsonl'
        done = {}
        if output.exists():
            for line in output.read_text(encoding='utf-8').splitlines():
                if line.strip():
                    row = json.loads(line)
                    row_id = str(row['id'])
                    if row_id in done:
                        raise ValueError(f'Duplicate checkpoint ID in {key}: {row_id}')
                    done[row_id] = row
        expected_ids = {str(item['id']) for item in rows}
        unexpected_ids = set(done) - expected_ids
        if unexpected_ids:
            raise ValueError(f'Checkpoint contains IDs absent from current bundle {key}: {sorted(unexpected_ids)[:10]}')
        for item in rows:
            row_id = str(item['id'])
            if row_id in done:
                if done[row_id].get('prompt_sha256') != item['prompt_sha256']:
                    raise ValueError(f'Checkpoint prompt mismatch: {key}/{row_id}')
                saved = done[row_id]
                if (saved.get('threshold_lock_sha256') != EXPECTED_LOCK_SEAL or saved.get('tau') != manifest['tau_star']
                        or saved.get('label') != item['label'] or not saved.get('valid')
                        or not all(math.isfinite(saved[k]) for k in ('s','logprob_0','logprob_1'))
                        or saved.get('pred_tau') != int(saved['s'] >= manifest['tau_star'])):
                    raise ValueError('Invalid test checkpoint identity or score: ' + row_id)
                if done[row_id].get('model_sha256') != model_digest:
                    raise ValueError(f'Checkpoint model hash mismatch: {key}/{row_id}')
        # Persist the refreshed archive hash only after checkpoint IDs and prompt hashes pass.
        identity_file.write_text(json.dumps(identity, indent=2), encoding='utf-8')
        progress = status['runs'][key]
        progress.update(state='running', count=len(rows), completed=len(done),
                        records_path=str(output), bundle_sha256=identity['bundle_sha256'])
        status['completed_records_total'] = sum(x.get('completed', 0) for x in status['runs'].values())
        write_json_atomic(status_path, status)
        if len(done) > len(rows):
            raise ValueError(f'Checkpoint has more rows than this bundle: {key}')
        print(f'{key}: verified checkpoint IDs={len(done)}; skipping these; remaining={len(rows) - len(done)}', flush=True)

        with output.open('a', encoding='utf-8', newline='\n') as f:
            for item in rows:
                row_id = str(item['id'])
                if row_id in done:
                    if done[row_id]['prompt_sha256'] != item['prompt_sha256']:
                        raise ValueError(f'Checkpoint prompt mismatch: {key}/{row_id}')
                    continue
                if time.time() + max(30, 2 * max(durations[-20:], default=30)) >= stop_at:
                    progress.update(state='checkpointed', completed=len(done))
                    status['completed_records_total'] = sum(x.get('completed', 0) for x in status['runs'].values())
                    stop_for_deadline(key)
                    return
                prompt = item['prompt']
                if hashlib.sha256(prompt.encode()).hexdigest() != item['prompt_sha256']:
                    raise ValueError(f'Prompt hash mismatch: {key}/{row_id}')
                messages = [{'role': 'user', 'content': prompt}]
                chat = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                hf_ids = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True, return_dict=False)
                gguf_ids = llm.tokenize(chat.encode('utf-8'), add_bos=False, special=True)
                if list(hf_ids) != gguf_ids:
                    raise ValueError(f'Tokenizer mismatch at {key}/{row_id}; abort rather than alter prompt')
                if len(gguf_ids) > manifest['prompt_budget_tokens']:
                    raise ValueError(f'Token budget exceeded at {key}/{row_id}')
                start = time.monotonic()
                llm.reset()
                llm.eval(gguf_ids)
                scores = binary_scores(llm.scores[llm.n_tokens - 1], label_ids)
                raw = llm.detokenize([scores['greedy_token_id']]).decode('utf-8', errors='replace').strip()
                row = {k: item[k] for k in ('id', 'dataset', 'split', 'label', 'prompt_sha256')}
                row.update({k: item[k] for k in ('demo_ids', 'tokens', 'graph_missing', 'prompt_variant') if k in item})
                row.update(scores, arm=arm, raw=raw, response_valid=raw in ('0', '1'), valid=True,
                           token_ids={'0': label_ids[0], '1': label_ids[1]}, model_sha256=model_digest,
                           backend='llama-cpp-python', quantization='Q4_K_M', model_repo=manifest['model_repo'],
                           model_repo_revision=model_revision, seed=prompt_seed, inference_seed=inference_seed, timestamp=datetime.now(timezone.utc).isoformat(),
                           logprob_distribution='unconstrained_first_token', elapsed_s=time.monotonic()-start)
                row.update(runtime_contract_sha256=EXPECTED_CONTRACT_SHA256)
                row.update(tau=manifest['tau_star'], pred_tau=int(scores['s'] >= manifest['tau_star']),
                           threshold_lock_sha256=EXPECTED_LOCK_SEAL)
                durations.append(row['elapsed_s'])
                f.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + '\n')
                f.flush()
                os.fsync(f.fileno())
                done[row_id] = row
                progress['completed'] = len(done)
                status['completed_records_total'] = sum(x.get('completed', 0) for x in status['runs'].values())
                status['last_checkpoint_at'] = datetime.now(timezone.utc).isoformat()
                write_json_atomic(status_path, status)
                if len(done) % 100 == 0 or time.time() - last_snapshot >= 120:
                    snapshot(status_path)
                    last_snapshot = time.time()
                if len(done) % 25 == 0 or len(done) == len(rows):
                    print(f'{key}: {len(done)}/{len(rows)}', flush=True)
                if time.time() >= stop_at:
                    progress['state'] = 'checkpointed'
                    stop_for_deadline(key)
                    return

        progress.update(state='complete', completed=len(rows))
        status['completed_records_total'] = sum(x.get('completed', 0) for x in status['runs'].values())
        write_json_atomic(status_path, status)

    status['state'] = 'complete'
    status['timed_out'] = False
    status['completed_at'] = datetime.now(timezone.utc).isoformat()
    write_json_atomic(status_path, status)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', required=True)
    ap.add_argument('--arm', required=True)
    ap.add_argument('--expected-model-sha256', required=True)
    ap.add_argument('--model-revision', required=True)
    ap.add_argument('--gpu-layers', type=int, default=-1)
    ap.set_defaults(limit=None)
    ap.add_argument('--deadline-epoch', type=float, required=True)
    ap.add_argument('--checkpoint-reserve-seconds', type=int, default=300)
    ap.add_argument('--status', required=True)
    ap.add_argument('--run', action='append', nargs=5, metavar=('SEED', 'DATASET', 'SPLIT', 'BUNDLE', 'OUT'), required=True)
    args = ap.parse_args()
    runs = [(int(seed), ds, split, bundle, out) for seed, ds, split, bundle, out in args.run]
    run_batch(runs, args.model, args.model_revision, args.gpu_layers, args.limit,
              args.deadline_epoch, args.checkpoint_reserve_seconds, args.status, args.expected_model_sha256, args.arm)
