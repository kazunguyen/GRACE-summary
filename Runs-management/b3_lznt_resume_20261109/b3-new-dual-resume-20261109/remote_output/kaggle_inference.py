import argparse
import hashlib
import json
import math
import os
import platform
import time
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from grace_runtime_contract import (
    EXPECTED_CONTRACT_SHA256, command, digest, load_contract, load_locked_model, provenance,
)

RUNTIME = load_contract()
from b3_delivery_runtime import load_input_root, validate_bundle, run_identity, checked_records
INPUT_ROOT = load_input_root('/kaggle/working/inference_input_manifest.json', os.environ['B3_INPUT_ROOT_SHA256'])



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
    manifest, rows, _ = validate_bundle(bundle, INPUT_ROOT)
    return manifest, rows



def evaluate_output(output):
    from sklearn.metrics import (
        accuracy_score, average_precision_score, balanced_accuracy_score,
        confusion_matrix, f1_score, matthews_corrcoef, precision_score,
        recall_score, roc_auc_score
    )
    records = [json.loads(line) for line in output.read_text(encoding='utf-8').splitlines() if line.strip()]
    actual = [r for r in records if r.get('response_valid', True)]
    truth = [r['label'] for r in actual]
    predicted = [int(r['raw']) for r in actual if str(r.get('raw', '')).strip() in ('0', '1')]
    metrics = {
        'n_total': len(records),
        'n_score_valid': sum(bool(r['valid']) for r in records),
        'n_response_valid': len(actual),
        'response_coverage': len(actual) / len(records) if records else None,
        'accuracy': None, 'balanced_accuracy': None, 'precision': None, 'recall': None,
        'f1': None, 'mcc': None, 'confusion_matrix': None, 'auroc': None, 'auprc': None
    }
    if actual and len(predicted) == len(truth):
        metrics.update(
            accuracy=float(accuracy_score(truth, predicted)),
            balanced_accuracy=float(balanced_accuracy_score(truth, predicted)),
            precision=float(precision_score(truth, predicted, zero_division=0)),
            recall=float(recall_score(truth, predicted, zero_division=0)),
            f1=float(f1_score(truth, predicted, zero_division=0)),
            mcc=float(matthews_corrcoef(truth, predicted)),
            confusion_matrix=confusion_matrix(truth, predicted, labels=[0, 1]).tolist()
        )
    score_rows = [r for r in records if r['valid']]
    if score_rows and len({r['label'] for r in score_rows}) == 2:
        labels = [r['label'] for r in score_rows]
        scores = [r['s'] for r in score_rows]
        metrics.update(
            auroc=float(roc_auc_score(labels, scores)),
            auprc=float(average_precision_score(labels, scores))
        )
    return metrics


def run_batch(runs, model_path, model_revision, gpu_layers, limit, deadline_epoch,
              checkpoint_reserve_seconds, status_path, seed, expected_model_sha256, arm):
    from llama_cpp import __version__ as llama_version
    from transformers import AutoTokenizer
    if llama_version != RUNTIME['backend_source']['version']:
        raise ValueError(f'Backend version mismatch: {llama_version}')

    started = time.time()
    stop_at = deadline_epoch - checkpoint_reserve_seconds
    status_path = Path(status_path)
    status_path.parent.mkdir(parents=True, exist_ok=True)
    status = {
        'state': 'starting', 'timed_out': False,
        'started_at': datetime.fromtimestamp(started, timezone.utc).isoformat(),
        'deadline_at': datetime.fromtimestamp(deadline_epoch, timezone.utc).isoformat(),
        'stop_new_records_at': datetime.fromtimestamp(stop_at, timezone.utc).isoformat(),
        'max_runtime_hours': (deadline_epoch - started) / 3600,
        'checkpoint_reserve_seconds': checkpoint_reserve_seconds,
        'runs': {}, 'completed_records_total': 0
    }
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
    if model_digest != expected_model_sha256:
        raise ValueError('Model SHA256 mismatch with runtime contract')
    if model_revision == 'local-input':
        model_revision = f'local-sha256:{model_digest}'

    first_manifest, _ = load_bundle(runs[0][2])
    tokenizer = AutoTokenizer.from_pretrained(first_manifest['tokenizer'], revision=first_manifest['tokenizer_revision'])

    provenance_root = status_path.parent / 'runtime_provenance'
    provenance_root.mkdir(exist_ok=True)
    session = Path(tempfile.mkdtemp(prefix=f'seed_{seed}_', dir=provenance_root))
    provenance_file = session / 'runtime_provenance.json'
    offload_log = session / 'model_load_offload.log'
    runtime_info = provenance(RUNTIME, __file__, provenance_file)
    build_log = Path('/kaggle/working/grace_diagnostics/install_llama_cuda.log')
    if build_log.exists():
        runtime_info['backend_build_log_sha256'] = digest(build_log)
        build_lines = build_log.read_text(encoding='utf-8', errors='replace').splitlines()
        runtime_info['backend_build_report'] = [
            line.strip() for line in build_lines
            if any(key in line for key in ('using CMake', 'compiler identification', 'Created wheel for llama-cpp-python'))
        ]

    llm = load_locked_model(RUNTIME, model_path, first_manifest, gpu_layers, offload_log, model_digest)
    runtime_info['gpu_after_load'] = command([
        'nvidia-smi', '--query-gpu=index,uuid,name,memory.free,memory.total,driver_version', '--format=csv,noheader',
    ])
    runtime_info['offload_log_sha256'] = digest(offload_log)
    write_json_atomic(provenance_file, runtime_info)
    provenance_ref = provenance_file.relative_to(status_path.parent).as_posix()

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
        identity = {
            'bundle_sha256': INPUT_ROOT['bundle_sha256'],
            'bundle_transport': 'verified_member_directory_v1',
            'b3_input_identity': run_identity(INPUT_ROOT),
            'prompt_set_sha256': manifest['prompts_sha256'],
            'model_sha256': model_digest,
            'model_repo': manifest['model_repo'],
            'quantization': manifest['quantization'],
            'model_file': model_path.name,
            'llama_cpp_python': llama_version,
            'model_repo_revision': model_revision,
            'tokenizer': manifest['tokenizer'],
            'tokenizer_revision': manifest['tokenizer_revision'],
            'gpu_layers': gpu_layers,
            'context_tokens': manifest['prompt_budget_tokens'],
            'scoring': RUNTIME['scoring']['name'],
            'limit': limit,
            'runtime_contract_sha256': EXPECTED_CONTRACT_SHA256,
            'constructor': RUNTIME['constructor'],
            'backend_sdist_sha256': RUNTIME['backend_source']['sdist_sha256'],
            'python': platform.python_version(),
            'dataset': dataset,
            'split': split,
            'arm': arm,
            'prompt_seed': seed
        }
        checked_records(status_path.parent, INPUT_ROOT, rows)
        identity_file = out / 'run_manifest.json'
        previous_identity = json.loads(identity_file.read_text(encoding='utf-8')) if identity_file.exists() else None
        if previous_identity is not None:
            ignored = {'bundle_sha256', 'prompt_set_sha256', 'python'}
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
                if done[row_id].get('model_sha256') != model_digest:
                    raise ValueError(f'Checkpoint model hash mismatch: {key}/{row_id}')

        identity_file.write_text(json.dumps(identity, indent=2), encoding='utf-8')
        progress = status['runs'][key]
        progress.update(state='running', count=len(rows), completed=len(done),
                        records_path=str(output), bundle_sha256=identity['bundle_sha256'])
        status['completed_records_total'] = sum(x.get('completed', 0) for x in status['runs'].values())
        write_json_atomic(status_path, status)

        with output.open('a', encoding='utf-8', newline='\n') as f:
            for item in rows:
                row_id = str(item['id'])
                if row_id in done:
                    continue
                if time.time() >= stop_at:
                    progress.update(state='checkpointed', completed=len(done))
                    status['completed_records_total'] = sum(x.get('completed', 0) for x in status['runs'].values())
                    stop_for_deadline(key)
                    return
                prompt = item['prompt']
                if hashlib.sha256(prompt.encode('utf-8')).hexdigest() != item['prompt_sha256']:
                    raise ValueError(f'Prompt hash mismatch: {key}/{row_id}')
                messages = [{'role': 'user', 'content': prompt}]
                chat = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                hf_ids = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True, return_dict=False)
                gguf_ids = llm.tokenize(chat.encode('utf-8'), add_bos=False, special=True)
                if list(hf_ids) != gguf_ids:
                    raise ValueError(f'Tokenizer mismatch at {key}/{row_id}; abort')
                if len(gguf_ids) > manifest['prompt_budget_tokens']:
                    raise ValueError(f'Token budget exceeded at {key}/{row_id}: {len(gguf_ids)} > {manifest["prompt_budget_tokens"]}')

                start = time.monotonic()
                llm.reset()
                llm.eval(gguf_ids)
                scores = binary_scores(llm.scores[llm.n_tokens - 1], label_ids)
                raw = llm.detokenize([scores['greedy_token_id']]).decode('utf-8', errors='replace').strip()
                row = {k: item[k] for k in ('id', 'dataset', 'split', 'label', 'prompt_sha256') if k in item}
                row.update(scores, arm=arm, raw=raw, response_valid=raw in ('0', '1'), valid=True,
                           token_ids={'0': label_ids[0], '1': label_ids[1]}, model_sha256=model_digest,
                           backend='llama-cpp-python', quantization='Q4_K_M', model_repo=manifest['model_repo'],
                           model_repo_revision=model_revision, seed=seed, timestamp=datetime.now(timezone.utc).isoformat(),
                           logprob_distribution='unconstrained_first_token', elapsed_s=time.monotonic() - start)
                row.update(runtime_contract_sha256=EXPECTED_CONTRACT_SHA256,
                           inference_seed=RUNTIME['constructor']['seed'], runtime_provenance=provenance_ref)
                f.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + '\n')
                f.flush()
                os.fsync(f.fileno())
                done[row_id] = row
                progress['completed'] = len(done)
                status['completed_records_total'] = sum(x.get('completed', 0) for x in status['runs'].values())
                status['last_checkpoint_at'] = datetime.now(timezone.utc).isoformat()
                write_json_atomic(status_path, status)
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
    ap.add_argument('--arm', required=True)
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
