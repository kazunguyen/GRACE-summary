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

# Shared validation-only analysis; helper is embedded by the Kaggle notebook.
import sys
if str(Path(__file__).resolve().parent.parent / 'Runs-management') not in sys.path:
    sys.path.insert(0,str(Path(__file__).resolve().parent.parent / 'Runs-management'))
from validation_lock import make_lock,persist_lock,require_test_lock,evaluate_at_locked_threshold,read_jsonl,file_sha256


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
    import numpy as np
    values=np.asarray(logits,dtype=np.float64).reshape(-1)
    if len(label_ids)!=2 or label_ids[0]==label_ids[1] or min(label_ids)<0 or max(label_ids)>=len(values):
        raise ValueError('Invalid binary token IDs')
    if not np.all(np.isfinite(values)):
        raise ValueError('Non-finite logits')
    normalizer=float(np.max(values)+np.log(np.exp(values-np.max(values)).sum()))
    lp0=float(values[label_ids[0]]-normalizer); lp1=float(values[label_ids[1]]-normalizer)
    s=float(np.exp(lp1-np.logaddexp(lp0,lp1)))
    top=np.argsort(values)[-5:][::-1]
    return {'logprob_0':lp0,'logprob_1':lp1,'p0':math.exp(lp0),'p1':math.exp(lp1),'s':s,
            'pred_argmax':int(s>=0.5),'greedy_token_id':int(np.argmax(values)),
            'top5':[{'token_id':int(i),'logprob':float(values[i]-normalizer)} for i in top]}


def load_bundle(bundle):
    with zipfile.ZipFile(bundle) as z:
        manifest = json.loads(z.read('bundle_manifest.json'))
        prompt_bytes = z.read('prompts.jsonl')
    if hashlib.sha256(prompt_bytes).hexdigest() != manifest['prompts_sha256']:
        raise ValueError(f'Prompt bundle hash mismatch: {bundle}')
    if manifest.get('arm') != 'B0' or manifest.get('prompt_variant') != 'b0_b2_empty_blocks_v1':
        raise ValueError('Expected B0 empty-B2-scaffolding bundle')
    rows = [json.loads(line) for line in prompt_bytes.decode('utf-8').splitlines() if line.strip()]
    if len(rows) != manifest['count'] or len({str(r['id']) for r in rows}) != len(rows):
        raise ValueError(f'Prompt count or unique ID check failed: {bundle}')
    for row in rows:
        if row.get('demo_ids') or row.get('arm') != 'B0' or row.get('prompt_variant') != manifest['prompt_variant']:
            raise ValueError('Bundle contains non-B0 payload/identity')
        if row.get('label') not in (0,1) or hashlib.sha256(row['prompt'].encode()).hexdigest() != row['prompt_sha256']:
            raise ValueError('Invalid prompt hash/label')
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
    if score_rows:
        y=[r['label'] for r in score_rows]; pred=[r['pred_argmax'] for r in score_rows]
        metrics['score_threshold_0_5']={'n':len(y),'mcc':float(matthews_corrcoef(y,pred)),
            'f1':float(f1_score(y,pred,zero_division=0)), 'accuracy':float(accuracy_score(y,pred))}
    return metrics


def run_batch(runs, model_path, model_revision, gpu_layers, limit, deadline_epoch,
              checkpoint_reserve_seconds, status_path, thresholds_path=None):
    from llama_cpp import Llama, __version__ as llama_version
    from transformers import AutoTokenizer
    if llama_version != '0.3.16': raise ValueError('Pinned llama-cpp-python 0.3.16 required')

    thresholds_path = Path(thresholds_path) if thresholds_path else Path(status_path).parent / "thresholds.json"
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
    if model_revision == 'local-input':
        model_revision = f'local-sha256:{model_digest}'
    first_manifest, _ = load_bundle(runs[0][2])
    if model_digest != first_manifest['expected_model_sha256']:
        raise ValueError('GGUF SHA256 differs from frozen research model')
    for dataset, split, bundle, out in runs:
        current_manifest, _ = load_bundle(bundle)
        if current_manifest['expected_model_sha256'] != model_digest:
            raise ValueError('Model identity differs across bundles')
        if current_manifest['freeze_manifest_sha256'] != first_manifest['freeze_manifest_sha256']:
            raise ValueError('Frozen data snapshot differs across bundles')
        if (current_manifest['tokenizer'], current_manifest['tokenizer_revision'],
            current_manifest['prompt_budget_tokens']) != (first_manifest['tokenizer'],
            first_manifest['tokenizer_revision'], first_manifest['prompt_budget_tokens']):
            raise ValueError('All four bundles must use the same tokenizer revision and context budget')
    tokenizer = AutoTokenizer.from_pretrained(first_manifest['tokenizer'],
                                                revision=first_manifest['tokenizer_revision'])
    llm = Llama(model_path=str(model_path), n_ctx=first_manifest['prompt_budget_tokens'], n_batch=256,
                n_gpu_layers=gpu_layers, logits_all=True, seed=42, verbose=True)
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
        if (manifest['dataset'], manifest['split']) != (dataset, split):
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
                    'scoring': 'unconstrained_first_token_logits_v1', 'limit': limit, 'arm': 'B0', 'prompt_variant': 'b0_b2_empty_blocks_v1',
                    'python': platform.python_version(), 'dataset': dataset, 'split': split}
        locked_threshold = None
        if split == 'test':
            val_hash = None
            for vd,vs,vb,vo in runs:
                if vd == dataset and vs == 'validation':
                    val_hash = load_bundle(vb)[0]['prompts_sha256']
                    break
            locked_threshold = require_test_lock(thresholds_path,'B0',dataset,identity,val_hash)
            print(f'Test threshold locked: {dataset} tau={locked_threshold["tau"]}',flush=True)
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
                if done[row_id].get('label') != item['label'] or done[row_id].get('arm') != 'B0':
                    raise ValueError('Checkpoint label/arm mismatch')
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
                if len(gguf_ids) + 64 > manifest['prompt_budget_tokens']:
                    raise ValueError(f'Token budget exceeded at {key}/{row_id}')
                start = time.monotonic()
                llm.reset()
                llm.eval(gguf_ids)
                scores = binary_scores(llm.scores[llm.n_tokens - 1], label_ids)
                raw = llm.detokenize([scores['greedy_token_id']]).decode('utf-8', errors='replace').strip()
                row = {k: item[k] for k in ('id', 'dataset', 'split', 'label', 'prompt_sha256', 'demo_ids', 'tokens', 'graph_missing')}
                row.update(scores, arm='B0', prompt_variant='b0_b2_empty_blocks_v1', raw=raw, response_valid=raw in ('0', '1'), valid=True,
                           token_ids={'0': label_ids[0], '1': label_ids[1]}, model_sha256=model_digest,
                           backend='llama-cpp-python', quantization='Q4_K_M', model_repo=manifest['model_repo'],
                           model_repo_revision=model_revision, seed=42, timestamp=datetime.now(timezone.utc).isoformat(),
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

        if split == 'validation' and limit is None:
            locked_threshold = persist_lock(thresholds_path,make_lock(rows,list(done.values()),'B0',dataset,identity,
                manifest['prompts_sha256'],[{'path':str(output),'records_sha256':file_sha256(output)}]))
            write_json_atomic(out/'threshold_lock.json',locked_threshold)
            print(f'Validation threshold auto-locked: {dataset} tau={locked_threshold["tau"]}',flush=True)
        metrics = evaluate_output(output)
        if locked_threshold is not None:
            metrics['score_threshold_validation_locked'] = evaluate_at_locked_threshold(list(done.values()),locked_threshold)
        (out / 'evaluation.json').write_text(json.dumps(metrics, indent=2, allow_nan=False), encoding='utf-8')
        progress.update(state='complete', completed=len(rows), evaluation=str(out / 'evaluation.json'))
        status['completed_records_total'] = sum(x.get('completed', 0) for x in status['runs'].values())
        write_json_atomic(status_path, status)

    status['state'] = 'complete'
    status['timed_out'] = False
    status['completed_at'] = datetime.now(timezone.utc).isoformat()
    write_json_atomic(status_path, status)



def discover_bundles(input_root,work_root,expected_runs):
    """Find standalone bundle ZIPs, unpacked bundles, or a ZIP wrapping bundle ZIPs."""
    found={}; work_root=Path(work_root); work_root.mkdir(parents=True,exist_ok=True)
    def accept(path):
        try:
            with zipfile.ZipFile(path) as z:
                if 'bundle_manifest.json' not in z.namelist(): return
                m=json.loads(z.read('bundle_manifest.json'))
        except (zipfile.BadZipFile,KeyError,json.JSONDecodeError): return
        if m.get('arm')!='B0' or m.get('prompt_variant')!='b0_b2_empty_blocks_v1': return
        key=(m['dataset'],m['split'])
        if key not in expected_runs: return
        identity=(m['prompts_sha256'],m['freeze_manifest_sha256'])
        if key in found and found[key][0]!=identity: raise ValueError(f'Conflicting B0 bundles for {key}; detach old inputs')
        found[key]=(identity,Path(path))
    for path in sorted(Path(input_root).rglob('*.zip')):
        accept(path)
        try:
            with zipfile.ZipFile(path) as z:
                nested=[n for n in z.namelist() if n.endswith('_b0_kaggle.zip')]
                for name in nested:
                    # Never trust an archive member path: extract bytes to a chosen basename.
                    dest=work_root/(hashlib.sha256(str(path).encode()).hexdigest()[:12]+'_'+Path(name).name)
                    with z.open(name) as src,dest.open('wb') as dst:
                        import shutil
                        shutil.copyfileobj(src,dst)
                    accept(dest)
        except zipfile.BadZipFile: continue
    for mp in sorted(Path(input_root).rglob('bundle_manifest.json')):
        m=json.loads(mp.read_text(encoding='utf-8'))
        if m.get('arm')!='B0' or m.get('prompt_variant')!='b0_b2_empty_blocks_v1': continue
        dest=work_root/(hashlib.sha256(str(mp).encode()).hexdigest()[:12]+'_unpacked_b0.zip')
        with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
            z.write(mp,'bundle_manifest.json'); z.write(mp.parent/'prompts.jsonl','prompts.jsonl')
        accept(dest)
    missing=set(expected_runs)-set(found)
    if missing: raise FileNotFoundError(f'Missing B0 bundles {sorted(missing)}. Add Input: grace_b0_inputs.zip or the generated folder, under any account.')
    return {key:found[key][1] for key in expected_runs}

def discover_model(input_root,expected_sha256,override=None):
    paths=[Path(override)] if override else sorted(Path(input_root).rglob('*Q4_K_M.gguf'))
    for path in paths:
        if path.is_file() and sha256(path)==expected_sha256: return path
    if paths: raise ValueError('Attached Q4_K_M files differ from expected model SHA256; choose correct model')
    return None

def restore_checkpoint(input_root,out_root):
    out_root=Path(out_root)
    if any(out_root.rglob('records.jsonl')):
        print('Resume existing working output:',out_root); return
    candidates=sorted(Path(input_root).rglob('grace_b0_checkpoint.zip'))
    if not candidates:
        print('No B0 checkpoint attached: start new run'); return
    hashes={sha256(p) for p in candidates}
    if len(hashes)!=1: raise ValueError('Conflicting B0 checkpoints; attach only one version')
    out_root.mkdir(parents=True,exist_ok=True); root=out_root.resolve()
    with zipfile.ZipFile(candidates[0]) as z:
        for info in z.infolist():
            destination=(root/info.filename).resolve()
            if not destination.is_relative_to(root) or ((info.external_attr>>16)&0o170000)==0o120000:
                raise ValueError('Unsafe checkpoint member')
        z.extractall(root)
    print('Restored checkpoint:',candidates[0])


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--thresholds', help='Defaults to thresholds.json beside checkpoint_status.json')
    ap.add_argument('--model', required=True)
    ap.add_argument('--model-revision', required=True)
    ap.add_argument('--gpu-layers', type=int, default=-1)
    ap.add_argument('--limit', type=int)
    ap.add_argument('--deadline-epoch', type=float, required=True)
    ap.add_argument('--checkpoint-reserve-seconds', type=int, default=300)
    ap.add_argument('--status', required=True)
    ap.add_argument('--run', action='append', nargs=4, metavar=('DATASET', 'SPLIT', 'BUNDLE', 'OUT'), required=True)
    args = ap.parse_args()
    run_batch(args.run, args.model, args.model_revision, args.gpu_layers, args.limit,
              args.deadline_epoch, args.checkpoint_reserve_seconds, args.status, args.thresholds)
