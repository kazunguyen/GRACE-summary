"""Run a prepared B2 prompt bundle using a Q4_K_M GGUF and raw first-token logits."""
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


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def binary_scores(logits, label_ids):
    values = np.asarray(logits, dtype=np.float64).reshape(-1)
    if not np.all(np.isfinite(values)):
        raise ValueError('Non-finite logits')
    normalizer = float(np.max(values) + np.log(np.exp(values - np.max(values)).sum()))
    lp0 = float(values[label_ids[0]] - normalizer)
    lp1 = float(values[label_ids[1]] - normalizer)
    s = float(np.exp(lp1 - np.logaddexp(lp0, lp1)))
    best = int(np.argmax(values))
    top = np.argsort(values)[-5:][::-1]
    return {'logprob_0': lp0, 'logprob_1': lp1, 'p0': math.exp(lp0), 'p1': math.exp(lp1),
            's': s, 'pred_argmax': int(s >= 0.5), 'greedy_token_id': best,
            'top5': [{'token_id': int(i), 'logprob': float(values[i] - normalizer)} for i in top]}


def run(bundle, model_path, out, gpu_layers=-1, limit=None, model_revision=None):
    from llama_cpp import Llama, __version__ as llama_version
    from transformers import AutoTokenizer
    bundle, model_path, out = Path(bundle), Path(model_path), Path(out)
    out.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(bundle) as z:
        manifest = json.loads(z.read('bundle_manifest.json'))
        prompt_bytes = z.read('prompts.jsonl')
    if hashlib.sha256(prompt_bytes).hexdigest() != manifest['prompts_sha256']:
        raise ValueError('Prompt bundle hash mismatch')
    rows = [json.loads(line) for line in prompt_bytes.decode('utf-8').splitlines() if line.strip()]
    if len(rows) != manifest['count'] or len({str(r['id']) for r in rows}) != len(rows):
        raise ValueError('Prompt count or unique ID check failed')
    if limit is not None:
        rows = rows[:limit]
    identity = {'bundle_sha256': sha256(bundle), 'model_sha256': sha256(model_path),
                'model_repo': manifest['model_repo'], 'quantization': manifest['quantization'],
                'model_file': model_path.name, 'llama_cpp_python': llama_version,
                'model_repo_revision': model_revision,
                'tokenizer': manifest['tokenizer'], 'tokenizer_revision': manifest['tokenizer_revision'],
                'gpu_layers': gpu_layers, 'context_tokens': manifest['prompt_budget_tokens'],
                'scoring': 'unconstrained_first_token_logits_v1', 'limit': limit,
                'python': platform.python_version()}
    identity_file = out / 'run_manifest.json'
    if identity_file.exists() and json.loads(identity_file.read_text(encoding='utf-8')) != identity:
        raise ValueError('Existing output has a different identity; choose a new output directory')
    identity_file.write_text(json.dumps(identity, indent=2), encoding='utf-8')
    tokenizer = AutoTokenizer.from_pretrained(manifest['tokenizer'], revision=manifest['tokenizer_revision'])
    # logits_all stores a vocab-sized vector per context position (~5 GiB CPU RAM at 8192 tokens).
    llm = Llama(model_path=str(model_path), n_ctx=manifest['prompt_budget_tokens'], n_batch=256,
                n_gpu_layers=gpu_layers, logits_all=True, verbose=True)
    ids = []
    for label in ('0', '1'):
        a = tokenizer.encode(label, add_special_tokens=False)
        b = llm.tokenize(label.encode(), add_bos=False, special=False)
        if len(a) != 1 or a != b:
            raise ValueError(f'Label token mismatch for {label}: HF={a}, GGUF={b}')
        ids.append(a[0])
    if ids[0] == ids[1]:
        raise ValueError('Label token IDs must differ')
    output = out / 'records.jsonl'
    done = {}
    if output.exists():
        for line in output.read_text(encoding='utf-8').splitlines():
            if line.strip():
                row = json.loads(line)
                if row['id'] in done:
                    raise ValueError('Duplicate ID in checkpoint')
                done[row['id']] = row
    with output.open('a', encoding='utf-8', newline='\n') as f:
        for item in rows:
            if item['id'] in done:
                if done[item['id']]['prompt_sha256'] != item['prompt_sha256']:
                    raise ValueError('Checkpoint prompt mismatch')
                continue
            prompt = item['prompt']
            if hashlib.sha256(prompt.encode()).hexdigest() != item['prompt_sha256']:
                raise ValueError('Prompt hash mismatch')
            messages = [{'role': 'user', 'content': prompt}]
            chat = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            hf_ids = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True)
            gguf_ids = llm.tokenize(chat.encode('utf-8'), add_bos=False, special=True)
            if list(hf_ids) != gguf_ids:
                raise ValueError(f"Tokenizer mismatch at ID {item['id']}; abort rather than alter prompt")
            if len(gguf_ids) > manifest['prompt_budget_tokens']:
                raise ValueError('Token budget exceeded')
            start = time.monotonic()
            llm.reset()
            llm.eval(gguf_ids)
            scores = binary_scores(llm.scores[llm.n_tokens - 1], ids)
            raw = llm.detokenize([scores['greedy_token_id']]).decode('utf-8', errors='replace').strip()
            row = {k: item[k] for k in ('id', 'dataset', 'split', 'label', 'prompt_sha256', 'demo_ids', 'tokens', 'graph_missing')}
            row.update(scores, arm='B2', raw=raw, response_valid=raw in ('0', '1'), valid=True,
                       token_ids={'0': ids[0], '1': ids[1]}, model_sha256=identity['model_sha256'],
                       backend='llama-cpp-python', quantization='Q4_K_M',
                       model_repo=identity['model_repo'], model_repo_revision=identity['model_repo_revision'],
                       seed=42, timestamp=datetime.now(timezone.utc).isoformat(),
                       logprob_distribution='unconstrained_first_token', elapsed_s=time.monotonic()-start)
            f.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + '\n')
            f.flush()
            os.fsync(f.fileno())
            print(f"{item['id']}: s={scores['s']:.4f}, raw={raw!r}", flush=True)
    from sklearn.metrics import (accuracy_score, average_precision_score, balanced_accuracy_score,
                                 confusion_matrix, f1_score, matthews_corrcoef, precision_score,
                                 recall_score, roc_auc_score)
    records = [json.loads(line) for line in output.read_text(encoding='utf-8').splitlines() if line.strip()]
    actual = [r for r in records if r['response_valid']]
    truth = [r['label'] for r in actual]
    predicted = [int(r['raw']) for r in actual]
    metrics = {'n_total': len(records), 'n_score_valid': sum(bool(r['valid']) for r in records),
               'n_response_valid': len(actual), 'response_coverage': len(actual) / len(records) if records else None,
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
        labels, scores = [r['label'] for r in score_rows], [r['s'] for r in score_rows]
        metrics.update(auroc=roc_auc_score(labels, scores), auprc=average_precision_score(labels, scores))
    (out / 'evaluation.json').write_text(json.dumps(metrics, indent=2, allow_nan=False), encoding='utf-8')
    print('Records:', output)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--bundle', required=True)
    ap.add_argument('--model', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--gpu-layers', type=int, default=-1)
    ap.add_argument('--limit', type=int)
    ap.add_argument('--model-revision', required=True, help='Pinned Hub commit, or explicitly recorded local artifact revision')
    args = ap.parse_args()
    run(args.bundle, args.model, args.out, args.gpu_layers, args.limit, args.model_revision)
