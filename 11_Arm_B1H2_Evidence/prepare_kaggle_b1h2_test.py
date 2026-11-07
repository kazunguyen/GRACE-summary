"""Package original B1-H2 test inputs against the completed Kaggle validation lock.

CPU-only preparation. Historical Colab deliveries and frozen registrations are read-only.
"""
from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / '11_Arm_B1H2_Evidence'
OUT = BASE / 'kaggle_b1h2_test_20261106'
LOCK_PATH = ROOT / 'Runs-management/b1h2_kaggle_validation_threshold_lock_20261106.json'
AUDIT_PATH = ROOT / 'Runs-management/b1h2_kaggle_validation_audit_20261106.json'
SOURCE_SHA = '9db0d3eebb66a2f83c1f9803ceb0192954a3dfe2c3de9515188a996ede84ed7b'
LOCK_SEAL = 'b5dc7e0da070f75cfabc10c366a08675d1c3f471f1e11fb86ee826a22ce674f8'
EXPECTED = {'devign': 2732, 'reveal': 2274}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encoded(obj):
    return (json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode('utf-8')


def sealed(payload):
    return digest(json.dumps({k: v for k, v in payload.items() if k != 'locked_sha256'},
                             sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode())


def zip_bytes(members):
    target = io.BytesIO()
    with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(members.items()):
            info = zipfile.ZipInfo(name, (2026, 11, 6, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)
    return target.getvalue()


def replace_once(text, before, after):
    if text.count(before) != 1:
        raise ValueError('Source runtime has changed: ' + before[:100])
    return text.replace(before, after, 1)


def build_runtime():
    source = BASE / 'kaggle_b1h2_validation_20261106/downloaded_output/kaggle_inference.py'
    text = source.read_text(encoding='utf-8')
    text = replace_once(text, 'import numpy as np',
                        'import numpy as np\n\nEXPECTED_LOCK_SEAL = ' + repr(LOCK_SEAL))
    text = replace_once(text, "        prompt_bytes = z.read('prompts.jsonl')", """        prompt_bytes = z.read('prompts.jsonl')
        lock = json.loads(z.read('threshold_lock.json'))
    seal = lock.get('locked_sha256')
    unsigned = {k: v for k, v in lock.items() if k != 'locked_sha256'}
    actual = hashlib.sha256(json.dumps(unsigned, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()
    if seal != actual or seal != EXPECTED_LOCK_SEAL or manifest.get('threshold_lock_sha256') != seal:
        raise ValueError('Wrong or modified Kaggle validation lock')
    if (lock.get('arm'), lock.get('seed'), lock.get('split'), lock.get('counts')) != (
            'B1-H2', 42, 'validation', {'devign': 2732, 'reveal': 2273}):
        raise ValueError('Wrong threshold lock scope')
    ds = manifest['dataset']
    tau = lock['results'][ds]['tau_star']
    if (manifest.get('arm'), manifest.get('seed'), manifest.get('split')) != ('B1-H2', 42, 'test'):
        raise ValueError('This runner accepts B1-H2 test only')
    if tau != {'devign': 0.09, 'reveal': 0.21}[ds] or manifest.get('tau_star') != tau:
        raise ValueError('Fixed validation threshold mismatch')
    if lock.get('model_sha256') != manifest.get('model_sha256'):
        raise ValueError('Threshold and input model identities differ')""")
    text = replace_once(text, "    # Execution metadata follows", """    for row in rows:
        if (row.get('arm'), row.get('seed'), row.get('dataset'), row.get('split')) != ('B1-H2', 42, ds, 'test'):
            raise ValueError('Wrong test row identity')
        if hashlib.sha256(row['prompt'].encode()).hexdigest() != row['prompt_sha256']:
            raise ValueError('Changed test prompt')
    # Execution metadata follows""")
    start, end = text.index('def evaluate_output('), text.index('def run_batch(')
    text = text[:start] + '''def evaluate_output(output):
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
    target = root.parent / 'grace_b1_h2_test_checkpoint.zip'
    temporary = target.with_suffix('.zip.tmp')
    with zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(root.rglob('*')):
            if path.is_file() and not path.name.endswith('.tmp'):
                archive.write(path, path.relative_to(root).as_posix())
    os.replace(temporary, target)


''' + text[end:]
    text = replace_once(text, "    started = time.time()", """    if arm != 'B1-H2' or prompt_seed != 42 or limit is not None or not runs or any(r[1] != 'test' for r in runs):
        raise ValueError('Only the complete B1-H2 test census is allowed')
    started = time.time()
    durations = []
    last_snapshot = started""")
    text = replace_once(text, "                    'inference_seed': inference_seed, 'inference_seed_policy': 'llama_cpp_default'}", """                    'inference_seed': inference_seed, 'inference_seed_policy': 'llama_cpp_default',
                    'threshold_lock_sha256': EXPECTED_LOCK_SEAL, 'tau_star': manifest['tau_star'],
                    'n_batch': 256, 'tensor_split': [1.0,1.0], 'split_mode': 'layer'}""")
    text = replace_once(text, "                if done[row_id].get('model_sha256') != model_digest:", """                saved = done[row_id]
                if (saved.get('threshold_lock_sha256') != EXPECTED_LOCK_SEAL or saved.get('tau') != manifest['tau_star']
                        or saved.get('label') != item['label'] or not saved.get('valid')
                        or not all(math.isfinite(saved[k]) for k in ('s','logprob_0','logprob_1'))
                        or saved.get('pred_tau') != int(saved['s'] >= manifest['tau_star'])):
                    raise ValueError('Invalid test checkpoint identity or score: ' + row_id)
                if done[row_id].get('model_sha256') != model_digest:""")
    text = replace_once(text, "                if time.time() >= stop_at:\n                    progress.update", """                if time.time() + max(30, 2 * max(durations[-20:], default=30)) >= stop_at:
                    progress.update""")
    text = replace_once(text, "                f.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + '\\n')", """                row.update(tau=manifest['tau_star'], pred_tau=int(scores['s'] >= manifest['tau_star']),
                           threshold_lock_sha256=EXPECTED_LOCK_SEAL)
                durations.append(row['elapsed_s'])
                f.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + '\\n')""")
    text = replace_once(text, "                print(f'{key} {row_id}:", """                if len(done) % 100 == 0 or time.time() - last_snapshot >= 120:
                    snapshot(status_path)
                    last_snapshot = time.time()
                print(f'{key} {row_id}:""")
    text = replace_once(text, "    ap.add_argument('--limit', type=int)", "    ap.set_defaults(limit=None)")
    compile(text, 'kaggle_b1h2_test_runtime.py', 'exec')
    return text, digest(source.read_bytes())


def main():
    OUT.mkdir(exist_ok=True)
    lock_bytes = LOCK_PATH.read_bytes()
    lock = json.loads(lock_bytes)
    audit = json.loads(AUDIT_PATH.read_bytes())
    if sealed(lock) != LOCK_SEAL or lock['locked_sha256'] != LOCK_SEAL:
        raise ValueError('Kaggle threshold self-checksum mismatch')
    if not audit['all_5005_record_checks_passed'] or digest(lock_bytes) != audit['kaggle_lock_file_sha256']:
        raise ValueError('Validation audit does not authenticate this lock')
    for ds, tau in [('devign', .09), ('reveal', .21)]:
        if lock['results'][ds]['tau_star'] != tau:
            raise ValueError('Wrong validation thresholds')
    original = ROOT / 'grace_15arms_prompts_and_clean_specs.zip'
    if digest(original.read_bytes()) != SOURCE_SHA:
        raise ValueError('Original archive changed')
    old_test = BASE / 'colab_l4_b1h2_test_20261106/b1h2_original_test_bundle.zip'
    with zipfile.ZipFile(old_test) as source:
        prompts = [json.loads(line) for line in source.read('prompts.jsonl').splitlines()]
    if len(prompts) != 5006 or len({r['id'] for r in prompts}) != 5006:
        raise ValueError('Original test census mismatch')
    sets, members, extracted, checks = [], {}, {}, {}
    val_bundle = BASE / 'kaggle_b1h2_validation_20261106/grace_b1_h2_validation_inputs.zip'
    if digest(val_bundle.read_bytes()) != lock['bundle_sha256']:
        raise ValueError('Kaggle validation bundle mismatch')
    with zipfile.ZipFile(original) as archive, zipfile.ZipFile(val_bundle) as validation:
        for ds, count in EXPECTED.items():
            val_member = f'prompts/dry_run_validation_20261102/{ds}/validation/B1-H2/42/prompts.jsonl'
            original_val = {r['id']: r for r in map(json.loads, archive.read(val_member).splitlines())}
            with zipfile.ZipFile(io.BytesIO(validation.read(f'seed_42/{ds}_validation.zip'))) as z:
                kaggle_val = [json.loads(line) for line in z.read('prompts.jsonl').splitlines()]
            if len(kaggle_val) != lock['counts'][ds] or set(original_val) != {r['id'] for r in kaggle_val}:
                raise ValueError('Validation ID provenance mismatch')
            for row in kaggle_val:
                if row['prompt'] != original_val[row['id']]['prompt'] or digest(row['prompt'].encode()) != row['prompt_sha256']:
                    raise ValueError('Original prompt method differs from Kaggle validation')
            spec_member = f'specs/{ds}_test_15arms.jsonl'
            spec_bytes = archive.read(spec_member)
            specs = {r['id']: r for r in map(json.loads, spec_bytes.splitlines())}
            rows = [dict(r) for r in prompts if r['dataset'] == ds]
            if len(rows) != count or set(specs) != {r['id'] for r in rows}:
                raise ValueError('Test ID/spec coverage mismatch')
            for row in rows:
                if (row['arm'], row['seed'], row['split']) != ('B1-H2',42,'test'):
                    raise ValueError('Wrong original test scope')
                if digest(row['prompt'].encode()) != row['prompt_sha256']:
                    raise ValueError('Original test prompt changed')
                tokens = row['evidence']['tokens']
                if tokens['approx'] or tokens['total'] + 64 > 8192 or tokens['code'] > 3000 or tokens['graph'] > 1500:
                    raise ValueError('Original prompt token metadata violates budget')
                row['label'] = int(specs[row['id']]['label'])
                if row['label'] not in (0,1): raise ValueError('Invalid frozen test label')
            payload = b''.join((json.dumps(r,ensure_ascii=False,allow_nan=False)+'\n').encode() for r in rows)
            manifest = dict(dataset=ds,split='test',arm='B1-H2',seed=42,count=count,
                            prompts_sha256=digest(payload),source_archive_sha256=SOURCE_SHA,
                            model_sha256=lock['model_sha256'],threshold_lock_sha256=LOCK_SEAL,
                            tau_star=lock['results'][ds]['tau_star'],test_labels_usage='offline evaluation only; never interpolated into prompt')
            inner_members = {'prompts.jsonl':payload,'bundle_manifest.json':encoded(manifest),'threshold_lock.json':lock_bytes}
            name = f'seed_42/{ds}_test.zip'
            data = zip_bytes(inner_members)
            sets.append(dict(name=name,sha256=digest(data),seed=42,dataset=ds))
            members[name] = data
            extracted[name] = {k:digest(v) for k,v in inner_members.items()}
            checks[ds] = dict(test_count=count,validation_prompt_method_matches=len(kaggle_val),
                              original_test_prompt_text_preserved=True,test_specs_sha256=digest(spec_bytes),
                              max_prompt_tokens=max(r['evidence']['tokens']['total'] for r in rows))
    data = zip_bytes(members)
    bundle = OUT / 'grace_b1_h2_test_inputs.zip'
    bundle.write_bytes(data)
    runtime, source_runtime_sha = build_runtime()
    (OUT/'kaggle_b1h2_test_runtime.py').write_text(runtime,encoding='utf8',newline='\n')
    template_path = BASE/'notebooks/02_kaggle_qwen_q4_b1_h2_validation_20261106.ipynb'
    notebook = json.loads(template_path.read_bytes())
    notebook['cells'] = notebook['cells'][:9]
    def set_cell(i, value): notebook['cells'][i]['source'] = value.splitlines(keepends=True)
    set_cell(0, '''# B1-H2 - Kaggle test, 9-hour session budget

Upload `grace_b1_h2_test_inputs.zip` as a Kaggle Dataset and attach the same Q4_K_M model as validation.
Select GPU T4 x2 and Internet ON. Run All.
The first code cell prints PING immediately; a heartbeat repeats every 30 seconds with the active stage.
PING confirms that the notebook kernel can execute Python, not that GPU inference is progressing.
Fixed thresholds from completed Kaggle validation: Devign 0.09; ReVeal 0.21.
Prompt-set seed 42; inference RNG uses llama_cpp.LLAMA_DEFAULT_SEED (4294967295), matching validation.
The 9-hour wall-clock budget starts in the first code cell and includes setup; 5 minutes are reserved for checkpoint export.
Download grace_b1_h2_test_checkpoint.zip and grace_diagnostics.zip from Output. Reattach that test checkpoint to resume.
Test labels are evaluation metadata; only item['prompt'] is sent to the model. No threshold fitting is performed.
''')
    cell = ''.join(notebook['cells'][1]['source'])
    cell = cell.replace("DIAG = Path('/kaggle/working/grace_diagnostics')", "SESSION_START_EPOCH = _heartbeat_session_start\nSESSION_DEADLINE_EPOCH = SESSION_START_EPOCH + 9 * 3600\nDIAG = Path('/kaggle/working/grace_diagnostics')")
    cell = replace_once(cell, "_gpu_probe = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'],\n                            check=True, capture_output=True, text=True)", """heartbeat_stage('checking GPU with nvidia-smi; timeout 30s')
try:
    _gpu_probe = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'],
                                check=True, capture_output=True, text=True, timeout=30)
except Exception as exc:
    _b1h2_heartbeat_cleanup(f'GPU check failed: {type(exc).__name__}: {exc}')
    raise""")
    cell = replace_once(cell, "    text = str(message)\n    print(text, flush=True)", "    text = str(message)\n    _heartbeat_state['stage'] = text[:180]\n    print(text, flush=True)")
    cell = cell.replace("is_inference = name.startswith('resume_seed_')", "is_inference = name.startswith('test_seed_')")
    cell = cell.replace("        for line in proc.stdout:", """        import threading
        def terminate_at_deadline():
            if proc.poll() is None: proc.terminate()
        watchdog = threading.Timer(max(1, SESSION_DEADLINE_EPOCH-time.time()-120), terminate_at_deadline)
        watchdog.daemon = True
        watchdog.start()
        for line in proc.stdout:""")
    cell = cell.replace('        code = proc.wait()', '        code = proc.wait()\n        watchdog.cancel()')
    bootstrap = (OUT/'heartbeat_bootstrap.py').read_text(encoding='utf-8')
    set_cell(1, bootstrap + '\n\n' + cell)
    config = f'''import math
ARM = 'B1-H2'
KAGGLE_INPUT_ROOT = Path('/kaggle/input')
BUNDLE_WORK = Path('/kaggle/working/b1_h2_test_bundles')
OUT_ROOT = Path('/kaggle/working/b1_h2_test')
BUNDLE_NAME = 'grace_b1_h2_test_inputs.zip'
BUNDLE_SHA256 = {digest(data)!r}
CHECKPOINT_NAME = 'grace_b1_h2_test_checkpoint.zip'
CHECKPOINT_INPUT_PATH = None
MODEL_FILENAME = 'Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf'
MODEL_SHA256 = {lock['model_sha256']!r}
MAX_RUNTIME_HOURS = 9
CHECKPOINT_RESERVE_SECONDS = 300
GPU_LAYERS = -1
THRESHOLD_LOCK_SHA256 = {LOCK_SEAL!r}
SETS = {sets!r}
'''
    set_cell(2, config)
    cell = ''.join(notebook['cells'][3]['source']).replace("'validation'", "'test'").replace('/validation/', '/test/')
    begin = cell.index('EXTRACTED_MEMBER_HASHES = ')
    finish = cell.index('\narchives = ',begin)
    cell = cell[:begin] + 'EXTRACTED_MEMBER_HASHES = ' + repr(extracted) + cell[finish:]
    cell = cell.replace("        if hash_bytes(prompt_bytes) != manifest['prompts_sha256']:", """        lock_payload = json.loads(inner.read('threshold_lock.json'))
        actual_seal = hash_bytes(json.dumps({k:v for k,v in lock_payload.items() if k!='locked_sha256'}, sort_keys=True, separators=(',',':'), ensure_ascii=False).encode())
        if actual_seal != THRESHOLD_LOCK_SHA256 or lock_payload.get('locked_sha256') != actual_seal:
            raise ValueError('Threshold lock changed')
        if manifest['threshold_lock_sha256'] != actual_seal or manifest['tau_star'] != {'devign':0.09,'reveal':0.21}[ds]:
            raise ValueError('Wrong threshold for test')
        if hash_bytes(prompt_bytes) != manifest['prompts_sha256']:""")
    cell = cell.replace("or not math.isfinite(row['s'])):", """or not math.isfinite(row['s']) or row.get('threshold_lock_sha256') != THRESHOLD_LOCK_SHA256
                        or row.get('tau') != {'devign':0.09,'reveal':0.21}[ds]
                        or row.get('pred_tau') != int(row['s'] >= row['tau'])
                        or row.get('inference_seed') != 4294967295):""")
    # Persist the immutable validation lock with all output checkpoints.
    cell += "\n(OUT_ROOT/'threshold_lock.json').write_bytes(json.dumps(lock_payload,indent=2,ensure_ascii=False).encode())\n"
    set_cell(3, cell)
    cell = ''.join(notebook['cells'][4]['source']).replace("'huggingface_hub'", "'huggingface_hub==0.36.2', 'numpy==2.1.3', 'tokenizers==0.22.2'")
    set_cell(4,cell)
    set_cell(7,'%%writefile /kaggle/working/kaggle_inference.py\n'+runtime)
    cell = ''.join(notebook['cells'][8]['source'])
    cell = cell.replace('deadline = time.time() + MAX_RUNTIME_HOURS * 3600','deadline = SESSION_DEADLINE_EPOCH')
    cell = cell.replace("'validation'", "'test'").replace("'validation_complete'", "'test_complete'").replace("f'validation_seed_{seed}'", "f'test_seed_{seed}'")
    cell = cell.replace('Validation stopped', 'Test stopped')
    cell = cell.replace("    state = 'test_complete' if complete else 'timed_out'", """    import runpy
    evaluation_helper = runpy.run_path('/kaggle/working/kaggle_inference.py')['evaluate_output']
    for (seed, ds), count in progress.items():
        if count == len(expected[seed, ds]):
            folder = OUT_ROOT / f'seed_{seed}' / ds / 'test'
            metrics = evaluation_helper(folder / 'records.jsonl')
            (folder/'evaluation.json').write_text(json.dumps(metrics, indent=2, allow_nan=False), encoding='utf-8')
            print(ds, 'fixed-validation-threshold metrics:', metrics)
    state = 'test_complete' if complete else 'timed_out'""")
    cell = cell.replace("    summary = {'arm': ARM", "    progress = validate_records()\n    summary = {'threshold_lock_sha256': THRESHOLD_LOCK_SHA256, 'thresholds': {'devign':0.09,'reveal':0.21}, 'arm': ARM")
    cell += "\n_b1h2_heartbeat_cleanup('test session finished: ' + state)\n"
    set_cell(8,cell)
    stages = {2:'loading fixed test configuration',3:'verifying input bundles and checkpoints',
              4:'installing dependencies and building CUDA backend',5:'checking CUDA backend',
              6:'finding attached GGUF model',8:'running test inference and exporting checkpoints'}
    for i,stage in stages.items():
        set_cell(i, 'heartbeat_stage(' + repr(stage) + ')\n' + ''.join(notebook['cells'][i]['source']))
    notebook['metadata'] = {'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},
                           'language_info':{'name':'python','version':'3.13.16'},
                           'kaggle':{'accelerator':'nvidiaTeslaT4','dataSources':[{'sourceType':'kernelVersion','sourceId':364416463}],
                                     'isInternetEnabled':True,'language':'python','sourceType':'notebook','isGpuEnabled':True}}
    for i,c in enumerate(notebook['cells']):
        c['metadata'] = {}
        if c['cell_type']=='code':
            c['outputs'] = []; c['execution_count'] = None
            text=''.join(c['source'])
            compile(text.split('\n',1)[1] if text.startswith('%%writefile') else text,f'cell_{i}','exec')
    notebook_path = OUT/'02_kaggle_qwen_q4_b1_h2_test_20261106.ipynb'
    notebook_path.write_bytes(encoded(notebook))
    delivery = dict(schema='b1h2_kaggle_test_delivery_v1',arm='B1-H2',split='test',seed=42,
                    inference_seed=4294967295,inference_seed_policy='llama_cpp_default_matching_Kaggle_validation',
                    counts=EXPECTED,thresholds={'devign':.09,'reveal':.21},threshold_lock_sha256=LOCK_SEAL,
                    input_bundle_sha256=digest(data),input_bundle_bytes=len(data),
                    notebook_sha256=digest(notebook_path.read_bytes()),runtime_sha256=digest(runtime.encode()),
                    source_validation_runtime_sha256=source_runtime_sha,source_validation_bundle_sha256=lock['bundle_sha256'],
                    checks=checks,session_budget_hours=9,checkpoint_reserve_seconds=300,
                    preparation_only=True,gpu_inference_executed=False)
    delivery['heartbeat_interval_seconds'] = 30
    delivery['gpu_probe_timeout_seconds'] = 30
    delivery['heartbeat_bootstrap_sha256'] = digest(bootstrap.encode())
    (OUT/'delivery_manifest.json').write_bytes(encoded(delivery))
    print(json.dumps(delivery,indent=2))


if __name__ == '__main__':
    main()
