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
from importlib import metadata as importlib_metadata

RUNTIME_LOCK_PATH = Path('/kaggle/working/inference_runtime_lock.json')
RUNTIME_LOCK_BYTES = RUNTIME_LOCK_PATH.read_bytes()
RUNTIME_LOCK_SHA256 = hashlib.sha256(RUNTIME_LOCK_BYTES).hexdigest()
EXPECTED_RUNTIME_LOCK_SHA256 = '85d8770839f80260cdc7c27b27b6cce6bf8815675c8593db68fb102589c5cbd6'
if RUNTIME_LOCK_SHA256 != EXPECTED_RUNTIME_LOCK_SHA256:
    raise RuntimeError('Runtime lock file SHA-256 differs from approved lock')
RUNTIME_LOCK = json.loads(RUNTIME_LOCK_BYTES)
_unsigned_lock = {k:v for k,v in RUNTIME_LOCK.items() if k != 'integrity'}
_integrity = hashlib.sha256(json.dumps(_unsigned_lock,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
if _integrity != RUNTIME_LOCK['integrity']['sha256']:
    raise RuntimeError('Runner runtime-lock integrity mismatch')
RUNTIME_PACKAGES = RUNTIME_LOCK['packages']
if {name:importlib_metadata.version(name) for name in RUNTIME_PACKAGES} != RUNTIME_PACKAGES:
    raise RuntimeError('Runner package versions no longer match inference_runtime_lock.json')


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
    if hashlib.sha256(prompt_bytes).hexdigest() != manifest['prompts_sha256']:
        raise ValueError(f'Prompt bundle hash mismatch: {bundle}')
    rows = [json.loads(line) for line in prompt_bytes.decode('utf-8').splitlines() if line.strip()]
    if len(rows) != manifest['count'] or len({str(r['id']) for r in rows}) != len(rows):
        raise ValueError(f'Prompt count or unique ID check failed: {bundle}')
    return manifest, rows


def evaluate_output(output):
    from sklearn.metrics import (accuracy_score, average_precision_score, balanced_accuracy_score,
                                 confusion_matrix, f1_score, matthews_corrcoef, precision_score,
                                 recall_score, roc_auc_score)
    records = [json.loads(line) for line in output.read_text(encoding='utf-8').splitlines() if line.strip()]
    actual = [r for r in records if r['response_valid']]
    truth = [r['label'] for r in actual]
    predicted = [int(r['raw']) for r in actual]
    metrics = {'n_total': len(records), 'n_score_valid': sum(bool(r['valid']) for r in records),
               'n_response_valid': len(actual),
               'response_coverage': len(actual) / len(records) if records else None,
               'accuracy': None, 'balanced_accuracy': None, 'precision': None, 'recall': None,
               'f1': None, 'mcc': None, 'confusion_matrix': None, 'auroc': None, 'auprc': None}
    if actual:
        metrics.update(accuracy=accuracy_score(truth, predicted),
                       balanced_accuracy=balanced_accuracy_score(truth, predicted),
                       precision=precision_score(truth, predicted, zero_division=0),
                       recall=recall_score(truth, predicted, zero_division=0),
                       f1=f1_score(truth, predicted, zero_division=0),
                       mcc=matthews_corrcoef(truth, predicted),
                       confusion_matrix=confusion_matrix(truth, predicted, labels=[0, 1]).tolist())
    score_rows = [r for r in records if r['valid']]
    if score_rows and len({r['label'] for r in score_rows}) == 2:
        labels = [r['label'] for r in score_rows]
        scores = [r['s'] for r in score_rows]
        metrics.update(auroc=roc_auc_score(labels, scores),
                       auprc=average_precision_score(labels, scores))
    return metrics


def run_batch(runs, model_path, model_revision, gpu_layers, limit, deadline_epoch,
              checkpoint_reserve_seconds, status_path, seed, expected_model_sha256, arm):
    # Hard gate: a direct CLI invocation must also refuse test before model loading.
    if arm != 'B2-rand' or any(split != 'validation' for _,split,_,_ in runs):
        raise ValueError('Validation-only runner: test is blocked; stop and lock thresholds separately')
    from llama_cpp import Llama, __version__ as llama_version
    from transformers import AutoTokenizer
    if llama_version != '0.3.16': raise ValueError(f'Backend version mismatch: {llama_version}')

    started = time.time()
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
    for dataset, split, bundle, out in runs:
        key = f'{dataset}/{split}'
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
    first_manifest, _ = load_bundle(runs[0][2])
    for dataset, split, bundle, out in runs:
        current_manifest, _ = load_bundle(bundle)
        if (current_manifest['tokenizer'], current_manifest['tokenizer_revision'],
            current_manifest['prompt_budget_tokens']) != (first_manifest['tokenizer'],
            first_manifest['tokenizer_revision'], first_manifest['prompt_budget_tokens']):
            raise ValueError('All four bundles must use the same tokenizer revision and context budget')
    tokenizer = AutoTokenizer.from_pretrained(first_manifest['tokenizer'],
                                                revision=first_manifest['tokenizer_revision'])
    llm = Llama(model_path=str(model_path), n_ctx=first_manifest['prompt_budget_tokens'], n_batch=256,
                n_gpu_layers=gpu_layers, logits_all=True, verbose=True)
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
    for dataset, split, bundle, out_text in runs:
        key = f'{dataset}/{split}'
        out = Path(out_text)
        out.mkdir(parents=True, exist_ok=True)
        manifest, rows = load_bundle(bundle)
        if (manifest.get('arm'), manifest.get('seed'), manifest['dataset'], manifest['split']) != (arm, seed, dataset, split):
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
                    'python': platform.python_version(), 'dataset': dataset, 'split': split, 'arm': arm, 'prompt_seed': seed}
        identity_file = out / 'run_manifest.json'
        previous_identity = (json.loads(identity_file.read_text(encoding='utf-8'))
                             if identity_file.exists() else None)
        legacy_runtime_adoption = None
        if previous_identity is not None:
            # Runtime-lock metadata is provenance, not a changed inference parameter.
            # Adopt only the one exact I-15 record/manifest pair whose Kaggle logs were
            # checked against all six locked package versions and the same model/scoring.
            if previous_identity.get('runtime_lock_sha256') is None:
                allow = (arm, seed, dataset, split) == ('B2-rand', 44, 'devign', 'validation')
                old_records = out / 'records.jsonl'
                if (not allow
                    or sha256(identity_file) != '1f7fa83e76b56e6a20179ebf4701dd0e83f26fe4dc00f9e9375007e5fc40c574'
                    or not old_records.is_file()
                    or sha256(old_records) != '2f5a5297d4060c7235f950c21355d4675dbc41b17b50e86bc72d300dc15dffd7'):
                    raise ValueError(f'Legacy output for {key} is not the reviewed I-15 checkpoint; keep it separate')
                legacy_runtime_adoption = {
                    'status':'reviewed_legacy_resume',
                    'legacy_run_manifest_sha256':sha256(identity_file),
                    'legacy_records_sha256':sha256(old_records),
                    'evidence':'I-15 Kaggle install/runtime logs; worklogs/2026-11-07_inference_runtime_log_evidence.json',
                    'note':'Historical records retain their original provenance and are not retroactively stamped with the runtime lock.'
                }
            elif previous_identity.get('runtime_lock_sha256') != RUNTIME_LOCK_SHA256:
                raise ValueError(f'Existing output for {key} uses another runtime lock; choose a separate OUT_ROOT')
            # Ignore archive-byte hashes and additive runtime provenance only.
            # Prompt identity is verified below against every checkpoint row's prompt_sha256.
            ignored = {'bundle_sha256', 'prompt_set_sha256', 'runtime_lock_sha256', 'runtime_packages', 'runtime_adoption'}
            previous_stable = {k: v for k, v in previous_identity.items() if k not in ignored}
            current_stable = {k: v for k, v in identity.items() if k not in ignored}
            if previous_stable != current_stable:
                changed = sorted(set(previous_stable) | set(current_stable))
                changed = [name for name in changed if previous_stable.get(name) != current_stable.get(name)]
                raise ValueError(f'Existing output has different model/run settings for {key}: {changed}; use a new OUT_ROOT')
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
                if done[row_id].get('model_sha256') != model_digest:
                    raise ValueError(f'Checkpoint model hash mismatch: {key}/{row_id}')
        # Add runtime provenance separately from stable inference settings so a reviewed
        # legacy validation checkpoint can resume without changing its historical rows.
        manifest_identity = dict(identity)
        manifest_identity['runtime_lock_sha256'] = RUNTIME_LOCK_SHA256
        manifest_identity['runtime_packages'] = RUNTIME_PACKAGES
        manifest_identity['runtime_adoption'] = (legacy_runtime_adoption or
            (previous_identity or {}).get('runtime_adoption') or {'status':'fresh_locked_run'})
        identity_file.write_text(json.dumps(manifest_identity, indent=2), encoding='utf-8')
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
                if time.time() >= stop_at:
                    progress.update(state='checkpointed', completed=len(done))
                    status['completed_records_total'] = sum(x.get('completed', 0) for x in status['runs'].values())
                    stop_for_deadline(key)
                    return
                prompt = item['prompt']
                if hashlib.sha256(prompt.encode()).hexdigest() != item['prompt_sha256']:
                    raise ValueError(f'Prompt hash mismatch: {key}/{row_id}')
                messages = [{'role': 'user', 'content': prompt}]
                chat = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                hf_ids = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True)
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
                row = {k: item[k] for k in ('id', 'dataset', 'split', 'label', 'prompt_sha256', 'demo_ids', 'tokens', 'graph_missing')}
                row.update(scores, runtime_lock_sha256=RUNTIME_LOCK_SHA256, runtime_packages=RUNTIME_PACKAGES, arm=arm, raw=raw, response_valid=raw in ('0', '1'), valid=True,
                           token_ids={'0': label_ids[0], '1': label_ids[1]}, model_sha256=model_digest,
                           backend='llama-cpp-python', quantization='Q4_K_M', model_repo=manifest['model_repo'],
                           model_repo_revision=model_revision, seed=seed, timestamp=datetime.now(timezone.utc).isoformat(),
                           logprob_distribution='unconstrained_first_token', elapsed_s=time.monotonic()-start)
                f.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + '\n')
                f.flush()
                os.fsync(f.fileno())
                done[row_id] = row
                progress['completed'] = len(done)
                status['completed_records_total'] = sum(x.get('completed', 0) for x in status['runs'].values())
                status['last_checkpoint_at'] = datetime.now(timezone.utc).isoformat()
                write_json_atomic(status_path, status)
                print(f'{key} {row_id}: s={scores["s"]:.4f}, raw={raw!r} ({len(done)}/{len(rows)})', flush=True)
                if time.time() >= stop_at:
                    progress['state'] = 'checkpointed'
                    stop_for_deadline(key)
                    return

        metrics = evaluate_output(output)
        (out / 'evaluation.json').write_text(json.dumps(metrics, indent=2, allow_nan=False), encoding='utf-8')
        progress.update(state='complete', completed=len(rows), evaluation=str(out / 'evaluation.json'))
        status['completed_records_total'] = sum(x.get('completed', 0) for x in status['runs'].values())
        write_json_atomic(status_path, status)

    status['state'] = 'complete'
    status['timed_out'] = False
    status['completed_at'] = datetime.now(timezone.utc).isoformat()
    write_json_atomic(status_path, status)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', required=True)
    ap.add_argument('--seed', type=int, required=True)
    ap.add_argument('--arm', choices=['B2-rand'], required=True)
    ap.add_argument('--expected-model-sha256', required=True)
    ap.add_argument('--model-revision', required=True)
    ap.add_argument('--gpu-layers', type=int, default=-1)
    ap.add_argument('--limit', type=int)
    ap.add_argument('--deadline-epoch', type=float, required=True)
    ap.add_argument('--checkpoint-reserve-seconds', type=int, default=300)
    ap.add_argument('--status', required=True)
    ap.add_argument('--run', action='append', nargs=4, metavar=('DATASET', 'SPLIT', 'BUNDLE', 'OUT'), required=True)
    args = ap.parse_args()
    run_batch(args.run, args.model, args.model_revision, args.gpu_layers, args.limit,
              args.deadline_epoch, args.checkpoint_reserve_seconds, args.status, args.seed, args.expected_model_sha256, args.arm)
