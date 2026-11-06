"""Resume B2-flip on frozen donor prompts, repairing changed requests first.

The migration and scheduler run on CPU and are independently testable; only
run_batch loads the GPU model. Original checkpoint bytes remain in history/.
"""
import argparse
import hashlib
import json
import math
import os
import platform
import sys
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path

try:
    import validation_lock as locks
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'Runs-management'))
    import validation_lock as locks

VARIANT = 'b2_flip_frozen_donor_v1'
THRESHOLD_POLICY = 'inherit_base_B2_prereg_v1'
BASE_B2_INFERENCE_IDENTITY = {
    'model_sha256': 'f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335',
    'tokenizer': 'Qwen/Qwen3-Coder-30B-A3B-Instruct',
    'tokenizer_revision': 'b2cff646eb4bb1d68355c01b18ae02e7cf42d120',
    'quantization': 'Q4_K_M',
    'backend': 'llama-cpp-python',
    'backend_version': '0.3.16',
    'scoring': 'unconstrained_first_token_logits_v1',
    'seed_recorded': 42,
    'context_tokens': 8192,
}
# These are the locked B2 thresholds. B2-flip inherits them under prereg-v1;
# this runner validates complete B2-flip validation but never re-optimizes tau.
BASE_B2_THRESHOLDS = {
    'devign': {
        'tau': 0.7,
        'source_path': '01_Author_Baseline_Unified/output/local_full/inference_qwen_q4_b2_frozen_donor_20261102/thresholds_devign.json',
        'source_sha256': 'c4273120a64489f38217e73e673afbf2969486248774eb2c0e33cddb6447eb52',
        'source_validation_prompt_set_sha256': '5e98719dc82fea3a2115c41922cfce14e1e7265801623adb98839ccbdb214f9c',
        'source_validation_evidence_sha256': 'bc8ad02bd40dfc5a94dfc6317aef37346765baa64b7a40ee32686f2b011d3c42',
    },
    'reveal': {
        'tau': 0.12,
        'source_path': 'Runs-management/thresholds.json',
        'source_sha256': '96b864a3a91edf6a578ec853028d9c9cfe714addce21a6af399334ecfa1af6e5',
        'source_validation_prompt_set_sha256': '531b274808e0435ce47c6d1831903e4421486a034c6884a2a67ba01e779b3e42',
        'source_validation_evidence_sha256': '502717ef4431e1aa99dfc92dc100525d70678f68ee2693301fd07bc88dcf297b',
    },
}
STABLE = ('model_sha256', 'model_repo', 'quantization', 'llama_cpp_python', 'tokenizer',
          'tokenizer_revision', 'gpu_layers', 'context_tokens', 'scoring', 'limit')


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write_json_atomic(path, obj):
    locks.write_json(path, obj)


def read_rows(path):
    if not Path(path).exists():
        return []
    with Path(path).open(encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]


def write_rows_atomic(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    with tmp.open('w', encoding='utf-8', newline='\n') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + '\n')
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def load_bundle(path, snapshot=None):
    with zipfile.ZipFile(path) as z:
        manifest = json.loads(z.read('bundle_manifest.json'))
        payload = z.read('prompts.jsonl')
    if hashlib.sha256(payload).hexdigest() != manifest['prompts_sha256']:
        raise ValueError('Bundle prompt hash mismatch')
    if manifest.get('arm') != 'B2-flip' or manifest.get('prompt_variant') != VARIANT:
        raise ValueError('Use B2-flip bundles generated from the frozen donor reference')
    if snapshot and manifest['donor_snapshot_sha256'] != snapshot:
        raise ValueError('Wrong frozen donor snapshot')
    rows = [json.loads(line) for line in payload.splitlines() if line.strip()]
    if len(rows) != manifest['count'] or len({r['id'] for r in rows}) != len(rows):
        raise ValueError('Bundle count/unique ID mismatch')
    for row in rows:
        if (row['arm'], row['dataset'], row['split'], row['seed'], row['donor_snapshot_sha256']) != (
                'B2-flip', manifest['dataset'], manifest['split'], 42, manifest['donor_snapshot_sha256']):
            raise ValueError('Prompt identity mismatch')
        if hashlib.sha256(row['prompt'].encode()).hexdigest() != row['prompt_sha256']:
            raise ValueError('Prompt text/hash mismatch')
        if row['tokens']['total'] + 64 > manifest['prompt_budget_tokens']:
            raise ValueError('Prompt exceeds context budget')
    return manifest, rows


def validate_record(row, expected, identity, allow_legacy=False):
    if (row.get('arm'), row.get('dataset'), row.get('split'), row.get('label'), row.get('seed'), row.get('model_sha256')) != (
            'B2-flip', expected['dataset'], expected['split'], expected['label'], 42, identity['model_sha256']):
        raise ValueError(f'Checkpoint record identity mismatch: {row.get("id")}')
    is_current = row.get('prompt_sha256') == expected['prompt_sha256']
    is_legacy = row.get('prompt_sha256') == expected['previous_prompt_sha256']
    if not is_current and not (allow_legacy and is_legacy):
        raise ValueError(f'Unknown checkpoint prompt hash: {row["id"]}')
    demo_ids = expected['demo_ids'] if is_current else expected['previous_demo_ids']
    if row.get('demo_ids') != demo_ids:
        raise ValueError(f'Checkpoint demo provenance mismatch: {row["id"]}')
    return is_current


def prepare_session(runs, root, checkpoint, identity, snapshot):
    """Import only compatible records; return the immutable repair queue plus current state."""
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    contexts = {}
    for dataset, split, bundle, output in runs:
        m, rr = load_bundle(bundle, snapshot)
        if (m['dataset'], m['split']) != (dataset, split):
            raise ValueError('Run/bundle identity mismatch')
        if identity['model_sha256'] != m['model_sha256'] or identity['llama_cpp_python'] != m['expected_llama_cpp_python']:
            raise ValueError('Model bytes/backend version differ from reusable scores')
        for runtime_key, manifest_key in (('tokenizer', 'tokenizer'), ('tokenizer_revision', 'tokenizer_revision'),
                                          ('context_tokens', 'prompt_budget_tokens'), ('quantization', 'quantization'),
                                          ('model_repo', 'model_repo')):
            if identity[runtime_key] != m[manifest_key]:
                raise ValueError('Bundle tokenizer/context/model identity differs between splits')
        contexts[dataset, split] = {'manifest': m, 'rows': rr, 'expected': {r['id']: r for r in rr},
            'out': Path(output), 'identity': dict(identity, dataset=dataset, split=split,
                prompt_set_sha256=m['prompts_sha256'], bundle_sha256=sha256(bundle),
                donor_snapshot_sha256=snapshot, prompt_variant=VARIANT)}
    prompt_sets = {f'{d}/{s}': c['manifest']['prompts_sha256'] for (d, s), c in contexts.items()}
    signature = {'snapshot': snapshot, 'prompt_sets': prompt_sets, 'identity': {k: identity[k] for k in STABLE},
                 'threshold_policy': THRESHOLD_POLICY,
                 'base_threshold_sources': {d: {'tau': v['tau'], 'sha256': v['source_sha256']}
                                            for d, v in BASE_B2_THRESHOLDS.items()}}
    ready = root / 'migration_ready.json'
    if ready.exists():
        if read_json(ready) != signature:
            raise ValueError('Existing working output belongs to different prompts/runtime; use a new OUT_ROOT')
        plan = read_json(root / 'migration_plan.json')
    else:
        intent = root / 'migration_in_progress.json'
        source_sha = sha256(checkpoint) if checkpoint else None
        intended = dict(signature, source_checkpoint_sha256=source_sha)
        if intent.exists():
            if read_json(intent) != intended:
                raise ValueError('Interrupted migration used different inputs')
        elif any(root.rglob('records.jsonl')):
            raise ValueError('Unrecognized existing output; use a separate OUT_ROOT')
        else:
            write_json_atomic(intent, intended)
        retained = {key: [] for key in contexts}
        stale = []
        repair = []
        source_completed = 0
        thresholds = None
        original_archive = None
        if checkpoint:
            with zipfile.ZipFile(checkpoint) as z:
                if z.testzip() is not None or len(z.namelist()) != len(set(z.namelist())):
                    raise ValueError('Invalid or duplicate checkpoint ZIP members')
                native = 'migration_plan.json' in z.namelist()
                if native:
                    plan = json.loads(z.read('migration_plan.json'))
                    if plan['signature'] != signature:
                        raise ValueError('Native checkpoint belongs to a different frozen prompt/runtime version')
                    repair = plan['repair_requests']
                    if 'thresholds.json' in z.namelist():
                        thresholds = json.loads(z.read('thresholds.json'))
                    if 'history/original_checkpoint.zip' in z.namelist():
                        original_archive = z.read('history/original_checkpoint.zip')
                    if 'history/stale_records.jsonl' in z.namelist():
                        stale = [json.loads(line) for line in z.read('history/stale_records.jsonl').splitlines() if line.strip()]
                else:
                    original_archive = Path(checkpoint).read_bytes()
                allowed_records = {f'{d}/{s}/records.jsonl' for d, s in contexts}
                if any(n.endswith('/records.jsonl') and n not in allowed_records for n in z.namelist()):
                    raise ValueError('Checkpoint includes unexpected records paths')
                for key, c in contexts.items():
                    d, s = key
                    member = f'{d}/{s}/records.jsonl'
                    if member not in z.namelist():
                        continue
                    previous = json.loads(z.read(f'{d}/{s}/run_manifest.json'))
                    if any(previous.get(k) != identity[k] for k in STABLE):
                        raise ValueError(f'Checkpoint runtime differs for {d}/{s}')
                    expected_set = c['manifest']['prompts_sha256'] if native else c['manifest']['previous_prompts_sha256']
                    if previous.get('prompt_set_sha256') != expected_set:
                        raise ValueError(f'Unexpected checkpoint prompt set: {d}/{s}')
                    seen = set()
                    for line in z.read(member).splitlines():
                        if not line.strip():
                            continue
                        row = json.loads(line)
                        uid = row['id']
                        if uid in seen or uid not in c['expected']:
                            raise ValueError('Duplicate/unexpected checkpoint ID')
                        seen.add(uid)
                        source_completed += 1
                        item = c['expected'][uid]
                        current = validate_record(row, item, identity, allow_legacy=not native)
                        if current:
                            retained[key].append(row)
                        else:
                            stale.append(row)
                            repair.append({'dataset': d, 'split': s, 'id': uid,
                                           'old_prompt_sha256': row['prompt_sha256'], 'new_prompt_sha256': item['prompt_sha256']})
        if not checkpoint or not native:
            plan = {'schema': 'b2_flip_frozen_migration_v1', 'signature': signature,
                    'source_checkpoint_sha256': source_sha, 'source_completed': source_completed,
                    'initial_reused': sum(len(rr) for rr in retained.values()),
                    'repair_requests': repair, 'created_utc': datetime.now(timezone.utc).isoformat()}
        for request in repair:
            item = contexts[request['dataset'], request['split']]['expected'][request['id']]
            if request['new_prompt_sha256'] != item['prompt_sha256']:
                raise ValueError('Repair queue/new prompt mismatch')
        if len({(r['dataset'], r['split'], r['id']) for r in repair}) != len(repair):
            raise ValueError('Duplicate repair requests')
        history = root / 'history'
        history.mkdir(exist_ok=True)
        if original_archive:
            (history / 'original_checkpoint.zip').write_bytes(original_archive)
        write_rows_atomic(history / 'stale_records.jsonl', stale)
        write_json_atomic(root / 'migration_plan.json', plan)
        for key, c in contexts.items():
            c['out'].mkdir(parents=True, exist_ok=True)
            write_rows_atomic(c['out'] / 'records.jsonl', retained[key])
            write_json_atomic(c['out'] / 'run_manifest.json', c['identity'])
        if thresholds is not None:
            write_json_atomic(root / 'thresholds.json', thresholds)
        write_json_atomic(ready, signature)
    if plan.get('schema') != 'b2_flip_frozen_migration_v1' or plan.get('signature') != signature:
        raise ValueError('Migration plan version/signature mismatch')
    for request in plan['repair_requests']:
        item = contexts[request['dataset'], request['split']]['expected'][request['id']]
        if request['new_prompt_sha256'] != item['prompt_sha256']:
            raise ValueError('Persisted repair request differs from current prompt')
    for key, c in contexts.items():
        rr = read_rows(c['out'] / 'records.jsonl')
        c['done'] = {}
        for row in rr:
            uid = row['id']
            if uid in c['done'] or uid not in c['expected']:
                raise ValueError('Duplicate/unexpected working checkpoint ID')
            validate_record(row, c['expected'][uid], identity)
            c['done'][uid] = row
        previous = read_json(c['out'] / 'run_manifest.json')
        if any(previous.get(k) != c['identity'][k] for k in STABLE + ('prompt_set_sha256', 'donor_snapshot_sha256')):
            raise ValueError('Working run manifest changed')
    return {'root': root, 'contexts': contexts, 'plan': plan}


def process_session(session, infer, stop_at, clock=time.time):
    root, contexts, plan = session['root'], session['contexts'], session['plan']
    status_path = root / 'checkpoint_status.json'
    thresholds = root / 'thresholds.json'
    repairs = plan['repair_requests']
    locked = {}
    status = {'state': 'running', 'timed_out': False, 'phase': 'repair_changed_prompts',
              'started_at': datetime.now(timezone.utc).isoformat(), 'stop_new_records_at_epoch': stop_at,
              'source_completed': plan['source_completed'], 'initial_reused': plan['initial_reused'],
              'repair_total': len(repairs), 'inferred_this_session': 0, 'runs': {}}

    def persist():
        status['repair_remaining'] = sum(r['id'] not in contexts[r['dataset'], r['split']]['done'] for r in repairs)
        status['repair_completed'] = len(repairs) - status['repair_remaining']
        for (d, s), c in contexts.items():
            status['runs'][f'{d}/{s}'] = {'count': len(c['rows']), 'completed': len(c['done']),
                'state': 'complete' if len(c['done']) == len(c['rows']) else 'checkpointed', 'output': str(c['out'])}
        status['completed_records_total'] = sum(len(c['done']) for c in contexts.values())
        write_json_atomic(status_path, status)

    def lock_completed_validation(dataset):
        if dataset in locked:
            return
        c = contexts[dataset, 'validation']
        if len(c['done']) != len(c['rows']):
            return
        expected, seen = locks.validate_validation(
            c['rows'], list(c['done'].values()), 'B2-flip', dataset,
            c['identity']['model_sha256'])
        if set(expected) != set(seen):
            raise ValueError(f'Cannot inherit B2 threshold before complete validation: {dataset}')
        identity = locks.inference_identity(c['identity'])
        if identity != BASE_B2_INFERENCE_IDENTITY:
            raise ValueError(f'B2 threshold identity differs from B2-flip run: {dataset}')
        base = BASE_B2_THRESHOLDS[dataset]
        ordered = [seen[uid] for uid in sorted(seen)]
        evidence = [{k: r.get(k) for k in
                     ('id', 'label', 'prompt_sha256', 'model_sha256', 'seed', 's', 'valid')}
                    for r in ordered]
        for row in evidence:
            if row['s'] is not None and not math.isfinite(row['s']):
                row['s'] = None
        valid_scores = [r for r in ordered if r.get('valid') and
                        isinstance(r.get('s'), (int, float)) and math.isfinite(r['s'])]
        entry = {
            'arm': 'B2-flip', 'dataset': dataset, 'split_used': 'validation',
            'locked_at_utc': datetime.now(timezone.utc).isoformat(),
            'rules_sha256': locks.RULES_SHA256, 'identity': identity,
            'validation_prompt_set_sha256': c['manifest']['prompts_sha256'],
            'n_expected': len(expected),
            'validation_evidence_sha256': locks.digest_json(evidence),
            'source_evidence': [{
                'path': base['source_path'], 'sha256': base['source_sha256'],
                'base_arm': 'B2', 'threshold_key': f'B2/{dataset}',
                'tau': base['tau'],
                'validation_prompt_set_sha256': base['source_validation_prompt_set_sha256'],
                'validation_evidence_sha256': base['source_validation_evidence_sha256'],
            }],
            'threshold_policy': THRESHOLD_POLICY,
            'inherited_from': f'B2/{dataset}', 'tau': base['tau'],
            'n_valid': len(valid_scores), 'n_invalid': len(ordered) - len(valid_scores),
            'score_coverage': len(valid_scores) / len(ordered) if ordered else 0.0,
        }
        locked[dataset] = locks.persist_lock(thresholds, entry)
        if locked[dataset].get('threshold_policy') != THRESHOLD_POLICY or \
                locked[dataset].get('inherited_from') != f'B2/{dataset}':
            raise ValueError(f'Existing B2-flip lock does not follow preregistered inheritance: {dataset}')
        write_json_atomic(c['out'] / 'threshold_lock.json', locked[dataset])
        print(f'Validation complete: {dataset}; inherited B2 tau={base["tau"]}; '
              f'n={entry["n_expected"]}, score_valid={entry["n_valid"]}', flush=True)

    def run_one(d, s, uid, phase):
        c = contexts[d, s]
        if uid in c['done']:
            return True
        if clock() >= stop_at:
            status.update(state='timed_out', timed_out=True, stopped_after_run=f'{d}/{s}',
                          timed_out_at=datetime.now(timezone.utc).isoformat())
            persist()
            return False
        if s == 'test':
            lock_completed_validation(d)
            locks.require_test_lock(thresholds, 'B2-flip', d, c['identity'],
                                    contexts[d, 'validation']['manifest']['prompts_sha256'])
        status['phase'] = phase
        persist()
        item = c['expected'][uid]
        row = infer(item, c)
        validate_record(row, item, c['identity'])
        row.update(donor_snapshot_sha256=c['manifest']['donor_snapshot_sha256'], prompt_variant=VARIANT,
                   inference_phase=phase)
        path = c['out'] / 'records.jsonl'
        with path.open('a', encoding='utf-8', newline='\n') as f:
            f.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + '\n')
            f.flush()
            os.fsync(f.fileno())
        c['done'][uid] = row
        status['inferred_this_session'] += 1
        status['last_checkpoint_at'] = datetime.now(timezone.utc).isoformat()
        if s == 'validation':
            lock_completed_validation(d)
        persist()
        print(f'{d}/{s} {uid}: s={row["s"]:.4f}, raw={row["raw"]!r} ({len(c["done"])}/{len(c["rows"])}); phase={phase}', flush=True)
        return True

    persist()
    try:
        for dataset, split in contexts:
            if split == 'validation':
                lock_completed_validation(dataset)
        # Repair all validation requests, then satisfy validation dependencies for repaired test requests.
        for r in repairs:
            if r['split'] == 'validation' and not run_one(r['dataset'], r['split'], r['id'], 'repair_changed_prompts'):
                return status
        for (d, s), c in contexts.items():
            if s == 'validation':
                for row in c['rows']:
                    if not run_one(d, s, row['id'], 'complete_validation_before_test'):
                        return status
        for r in repairs:
            if r['split'] == 'test' and not run_one(r['dataset'], r['split'], r['id'], 'repair_changed_prompts'):
                return status
        for (d, s), c in contexts.items():
            for row in c['rows']:
                if not run_one(d, s, row['id'], 'continue_missing_prompts'):
                    return status
        for (d, s), c in contexts.items():
            rr = list(c['done'].values())
            metrics = evaluate_output(c['out'] / 'records.jsonl')
            metrics['score_threshold_validation_locked'] = locks.evaluate_at_locked_threshold(rr, locked[d])
            write_json_atomic(c['out'] / 'evaluation.json', metrics)
        status.update(state='complete', phase='complete', completed_at=datetime.now(timezone.utc).isoformat())
        persist()
        return status
    except Exception as exc:
        status.update(state='error', error=f'{type(exc).__name__}: {exc}')
        persist()
        raise


def binary_scores(logits, label_ids):
    import numpy as np
    values = np.asarray(logits, dtype=np.float64).reshape(-1)
    if not np.all(np.isfinite(values)):
        raise ValueError('Non-finite logits')
    maximum = np.max(values)
    normalizer = float(maximum + np.log(np.exp(values - maximum).sum()))
    lp0, lp1 = (float(values[i] - normalizer) for i in label_ids)
    score = float(np.exp(lp1 - np.logaddexp(lp0, lp1)))
    best = int(np.argmax(values))
    top = np.argsort(values)[-5:][::-1]
    return {'logprob_0': lp0, 'logprob_1': lp1, 'p0': math.exp(lp0), 'p1': math.exp(lp1),
            's': score, 'pred_argmax': int(score >= .5), 'greedy_token_id': best,
            'top5': [{'token_id': int(i), 'logprob': float(values[i]-normalizer)} for i in top]}


def evaluate_output(path):
    from sklearn.metrics import (accuracy_score, average_precision_score, balanced_accuracy_score,
        confusion_matrix, f1_score, matthews_corrcoef, precision_score, recall_score, roc_auc_score)
    rr = read_rows(path)
    actual = [r for r in rr if r.get('response_valid') and r.get('raw') in ('0', '1')]
    scores = [r for r in rr if r.get('valid') and isinstance(r.get('s'), (int, float)) and math.isfinite(r['s'])]
    metrics = {'n_total': len(rr), 'n_score_valid': len(scores), 'n_response_valid': len(actual),
        'response_coverage': len(actual)/len(rr) if rr else None, 'accuracy': None,
        'balanced_accuracy': None, 'precision': None, 'recall': None, 'f1': None, 'mcc': None,
        'confusion_matrix': None, 'auroc': None, 'auprc': None}
    if actual:
        y, p = [r['label'] for r in actual], [int(r['raw']) for r in actual]
        metrics.update(accuracy=accuracy_score(y, p), balanced_accuracy=balanced_accuracy_score(y, p),
            precision=precision_score(y, p, zero_division=0), recall=recall_score(y, p, zero_division=0),
            f1=f1_score(y, p, zero_division=0), mcc=matthews_corrcoef(y, p),
            confusion_matrix=confusion_matrix(y, p, labels=[0, 1]).tolist())
    if len({r['label'] for r in scores}) == 2:
        metrics.update(auroc=roc_auc_score([r['label'] for r in scores], [r['s'] for r in scores]),
            auprc=average_precision_score([r['label'] for r in scores], [r['s'] for r in scores]))
    return metrics


def run_batch(runs, model_path, model_revision, gpu_layers, deadline_epoch,
              checkpoint_reserve_seconds, status_path, checkpoint, snapshot):
    from llama_cpp import Llama, __version__ as llama_version
    from transformers import AutoTokenizer
    model_path = Path(model_path)
    model_digest = sha256(model_path)
    first, _ = load_bundle(runs[0][2], snapshot)
    identity = {'model_sha256': model_digest, 'model_repo': first['model_repo'],
                'quantization': first['quantization'], 'model_file': model_path.name,
                'llama_cpp_python': llama_version, 'model_repo_revision': f'local-sha256:{model_digest}',
                'tokenizer': first['tokenizer'], 'tokenizer_revision': first['tokenizer_revision'],
                'gpu_layers': gpu_layers, 'context_tokens': first['prompt_budget_tokens'],
                'scoring': 'unconstrained_first_token_logits_v1', 'limit': None, 'python': platform.python_version()}
    session = prepare_session(runs, Path(status_path).parent, checkpoint, identity, snapshot)
    stop_at = deadline_epoch - checkpoint_reserve_seconds
    print(f'Migration: initial compatible={session["plan"]["initial_reused"]}; repair queue={len(session["plan"]["repair_requests"])}', flush=True)
    # No new GPU work is started after the deadline.
    if time.time() >= stop_at or all(len(c['done']) == len(c['rows']) for c in session['contexts'].values()):
        return process_session(session, lambda *_: None, stop_at)
    tokenizer = AutoTokenizer.from_pretrained(first['tokenizer'], revision=first['tokenizer_revision'])
    llm = Llama(model_path=str(model_path), n_ctx=first['prompt_budget_tokens'], n_batch=256,
                n_gpu_layers=gpu_layers, logits_all=True, seed=42, verbose=True)
    label_ids = []
    for label in ('0', '1'):
        ids = tokenizer.encode(label, add_special_tokens=False)
        if len(ids) != 1 or ids != llm.tokenize(label.encode(), add_bos=False, special=False):
            raise ValueError('HF/GGUF label token mismatch')
        label_ids.append(ids[0])

    def infer(item, context):
        prompt = item['prompt']
        messages = [{'role': 'user', 'content': prompt}]
        chat = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        hf_ids = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True)
        gguf_ids = llm.tokenize(chat.encode(), add_bos=False, special=True)
        if list(hf_ids) != gguf_ids or len(gguf_ids) + 64 > context['manifest']['prompt_budget_tokens']:
            raise ValueError('HF/GGUF chat tokenizer mismatch or context overflow')
        start = time.monotonic()
        llm.reset()
        llm.eval(gguf_ids)
        scores = binary_scores(llm.scores[llm.n_tokens-1], label_ids)
        raw = llm.detokenize([scores['greedy_token_id']]).decode('utf-8', errors='replace').strip()
        row = {k: item[k] for k in ('id', 'dataset', 'split', 'label', 'prompt_sha256', 'demo_ids', 'tokens', 'graph_missing')}
        row.update(scores, arm='B2-flip', raw=raw, response_valid=raw in ('0', '1'), valid=True,
                   token_ids={'0': label_ids[0], '1': label_ids[1]}, model_sha256=model_digest,
                   backend='llama-cpp-python', quantization=first['quantization'], model_repo=first['model_repo'],
                   model_repo_revision=identity['model_repo_revision'], seed=42,
                   timestamp=datetime.now(timezone.utc).isoformat(), logprob_distribution='unconstrained_first_token',
                   elapsed_s=time.monotonic()-start)
        return row

    return process_session(session, infer, stop_at)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', required=True)
    ap.add_argument('--model-revision', default='local-input')
    ap.add_argument('--gpu-layers', type=int, default=-1)
    ap.add_argument('--deadline-epoch', type=float, required=True)
    ap.add_argument('--checkpoint-reserve-seconds', type=int, default=300)
    ap.add_argument('--status', required=True)
    ap.add_argument('--checkpoint')
    ap.add_argument('--snapshot-sha256', required=True)
    ap.add_argument('--run', action='append', nargs=4, required=True)
    args = ap.parse_args()
    run_batch(args.run, args.model, args.model_revision, args.gpu_layers, args.deadline_epoch,
              args.checkpoint_reserve_seconds, args.status, args.checkpoint, args.snapshot_sha256)
