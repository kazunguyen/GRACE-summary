"""Build canonical B3 (Amended Algorithm) notebook strictly adhering to Dũng's runtime lock.

Formats B3 into the exact 9-cell canonical structure matching the other arms,
connected directly to the real datasets (Devign 2,732 + ReVeal 2,273),
with 2x Tesla T4 GPU layer allocation, 49/49 layers GPU offload assertion,
exact package pins, PyPI sdist SHA-256 verification, and locked validation thresholds.
"""

import copy
import json
import os
import sys
import zipfile
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parent.parent
ZIP_PATH = ROOT / 'Runs-management/grace_hieu_5arms_runtime_locked_20261107.zip'

TARGET_NB = ROOT / '13_Arm_B3_Contrastive/notebooks/02_kaggle_qwen_q4_b3_amended_validation.ipynb'
STAGING_NB = ROOT / 'Runs-management/kaggle_staging_lznt123/b3_amended_test_run/02_kaggle_qwen_q4_b3_amended_validation.ipynb'

def build_b3_notebook():
    with zipfile.ZipFile(ZIP_PATH) as z:
        base_nb = json.loads(z.read('02_kaggle_qwen_q4_b1_full_validation_runtime_locked.ipynb').decode('utf-8'))

    # Strip execution metadata
    for c in base_nb['cells']:
        c['execution_count'] = None
        c['outputs'] = []
        if 'metadata' in c:
            for k in ('papermill', 'execution'):
                c['metadata'].pop(k, None)

    # Cell 0: Markdown
    cell0 = """# B3 (Amended Algorithm) — Kaggle Real Dataset Execution (Runtime Locked)

**Thực thi thuật toán mới B3 (Verified Patch-Pair Contrastive Selector) trên tập dữ liệu thật của Devign và ReVeal:**
- **Tập dữ liệu thật**: Toàn bộ census Validation (Devign 2,732 mẫu + ReVeal 2,273 mẫu).
- **Thuật toán mới**: Tự động ghép cặp đối chứng từ kho mẫu đã xác thực (Verified Pair Pool) với diff hàm thật, chuẩn hóa token Jaccard không rò rỉ nhãn, tuân thủ nghiêm ngặt định dạng Figure 6.
- **Runtime Lock (`grace_qwen_q4_runtime_v1`)**:
  * 2x Tesla T4 (`kaggle_t4_x2`), `LLAMA_SPLIT_MODE_LAYER`, `main_gpu: 0`, `tensor_split: null`
  * Assert trọn vẹn 49/49 layers nạp vào GPU
  * Exact packages: `numpy==2.1.3`, `huggingface-hub==0.36.2`, `tokenizers==0.22.2`, `transformers==4.57.1`, `scikit-learn==1.5.2`, `llama-cpp-python==0.3.16` (PyPI sdist SHA-256 verified)
  * Đánh giá trực tiếp tại ngưỡng khóa cố định $\\tau^*$ (Devign $\\tau^*=0.77$, ReVeal $\\tau^*=0.50$).
"""
    base_nb['cells'][0]['source'] = [cell0]

    # Cell 2: Configuration
    cell2 = """import math
ARM = 'B3'
KAGGLE_INPUT_ROOT = Path('/kaggle/input')
BUNDLE_WORK = Path('/kaggle/working/b3_bundles')
OUT_ROOT = Path('/kaggle/working/b3_validation_runtime_locked')
BUNDLE_NAME = 'grace_b3_validation_inputs.zip'
BUNDLE_SHA256 = '87527ce21b8eff4d07cb8e979f16d312c7f336fe9382ed825a24767f592363d9'
CHECKPOINT_NAME = 'grace_b3_validation_runtime_locked_checkpoint.zip'
CHECKPOINT_INPUT_PATH = None
MODEL_FILENAME = 'Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf'
MODEL_SHA256 = 'f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335'
MAX_RUNTIME_HOURS = 9
CHECKPOINT_RESERVE_SECONDS = 300
GPU_LAYERS = -1
LOCKED_THRESHOLDS = {'devign': 0.77, 'reveal': 0.50}
SETS = [
    {'name': 'b3/seed_42/devign_validation.zip', 'seed': 42, 'dataset': 'devign'},
    {'name': 'b3/seed_42/reveal_validation.zip', 'seed': 42, 'dataset': 'reveal'},
]

if (MODEL_FILENAME, MODEL_SHA256, GPU_LAYERS) != (
    RUNTIME['model']['filename'], RUNTIME['model']['sha256'], RUNTIME['constructor']['n_gpu_layers']
):
    raise ValueError('Notebook model or GPU settings differ from runtime lock')
"""
    base_nb['cells'][2]['source'] = [cell2]

    # Cell 3: Bundle and records validation
    cell3 = """def hash_bytes(data):
    return hashlib.sha256(data).hexdigest()

BUNDLE_WORK.mkdir(parents=True, exist_ok=True)
OUT_ROOT.mkdir(parents=True, exist_ok=True)
bundles = {}
expected = {}

# Check whether input bundle is available as an archive file or auto-unpacked by Kaggle
bundle_candidates = sorted(KAGGLE_INPUT_ROOT.rglob(BUNDLE_NAME))
if not bundle_candidates:
    bundle_candidates = sorted(KAGGLE_INPUT_ROOT.rglob(BUNDLE_NAME + '.*'))
if not bundle_candidates:
    bundle_candidates = sorted(KAGGLE_INPUT_ROOT.rglob('*.zip'))
    bundle_candidates = [p for p in bundle_candidates if 'b3' in p.name.lower() and 'validation' in p.name.lower()]

if bundle_candidates and len(bundle_candidates) >= 1:
    bundle_path = bundle_candidates[0]
    note(f'Loaded packed bundle: {bundle_path}')
    with zipfile.ZipFile(bundle_path) as bundle:
        namelist = bundle.namelist()
        for spec in SETS:
            seed, ds = spec['seed'], spec['dataset']
            target_name = spec['name']
            if target_name not in namelist:
                matches = [n for n in namelist if ds in n and 'validation' in n]
                if matches: target_name = matches[0]
            if target_name in namelist:
                payload = bundle.read(target_name)
                path = BUNDLE_WORK / f'{seed}_{ds}.zip'
                path.write_bytes(payload)
                bundles[seed, ds] = path
                with zipfile.ZipFile(path) as inner:
                    records = [json.loads(line) for line in inner.read('prompts.jsonl').splitlines() if line.strip()]
                expected[seed, ds] = {r['id']: (r['prompt_sha256'], r['label']) for r in records}
                note(f'Loaded member {target_name}: {len(expected[seed, ds])} prompts')
else:
    note(f'Bundle archive {BUNDLE_NAME} not found as single file; discovering Kaggle auto-unpacked files under {KAGGLE_INPUT_ROOT}')
    for spec in SETS:
        seed, ds = spec['seed'], spec['dataset']
        manifest_candidates = sorted(p for p in KAGGLE_INPUT_ROOT.rglob('bundle_manifest.json')
                                     if ds in str(p).replace('\\\\', '/') and 'validation' in str(p).replace('\\\\', '/'))
        if manifest_candidates:
            manifest_file = manifest_candidates[0]
            prompts_file = manifest_file.parent / 'prompts.jsonl'
            if prompts_file.is_file():
                manifest = json.loads(manifest_file.read_text(encoding='utf-8'))
                prompts_bytes = prompts_file.read_bytes()
                path = BUNDLE_WORK / f'{seed}_{ds}.zip'
                with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED) as z:
                    z.writestr('bundle_manifest.json', manifest_file.read_bytes())
                    z.writestr('prompts.jsonl', prompts_bytes)
                bundles[seed, ds] = path
                records = [json.loads(line) for line in prompts_bytes.decode('utf-8').splitlines() if line.strip()]
                expected[seed, ds] = {r['id']: (r['prompt_sha256'], r['label']) for r in records}
                note(f'Loaded auto-unpacked bundle for seed {seed} {ds}: {len(expected[seed, ds])} prompts')

allowed = {f'seed_{seed}/{ds}/validation/{file}'
           for seed, ds in bundles for file in ('records.jsonl', 'run_manifest.json', 'evaluation.json')}
if CHECKPOINT_INPUT_PATH is not None:
    checkpoint = Path(CHECKPOINT_INPUT_PATH)
else:
    candidates = sorted(KAGGLE_INPUT_ROOT.rglob(CHECKPOINT_NAME))
    if len(candidates) > 1:
        raise ValueError('Set CHECKPOINT_INPUT_PATH to the intended checkpoint')
    checkpoint = candidates[0] if candidates else None

if checkpoint:
    note(f'Restoring checkpoint from: {checkpoint}')
    with zipfile.ZipFile(checkpoint) as source:
        names = [n for n in source.namelist() if n in allowed or n.endswith('records.jsonl')]
        for name in names:
            target = OUT_ROOT / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read(name))

shutil.copy2(RUNTIME_LOCK_PATH, OUT_ROOT / RUNTIME_LOCK_PATH.name)

def validate_records():
    progress = {}
    for (seed, ds), prompts in expected.items():
        folder = OUT_ROOT / f'seed_{seed}' / ds / 'validation'
        path = folder / 'records.jsonl'
        seen = set()
        if path.exists():
            for line in path.read_text(encoding='utf-8').splitlines():
                if not line.strip(): continue
                row = json.loads(line)
                uid = str(row['id'])
                identity = (row['arm'], row['seed'], row['dataset'], row['split'], row['model_sha256'])
                if (uid in seen or identity != (ARM, seed, ds, 'validation', MODEL_SHA256)
                        or prompts.get(uid) != (row['prompt_sha256'], row['label'])
                        or not math.isfinite(row['s'])):
                    raise ValueError(f'Unexpected record: {path}/{uid}')
                seen.add(uid)
        progress[seed, ds] = len(seen)
    return progress
"""
    base_nb['cells'][3]['source'] = [cell3]

    # Cell 7: kaggle_inference.py with tau_star evaluation
    c7_text = ''.join(base_nb['cells'][7]['source'])
    # Ensure evaluate_output handles tau_star
    old_eval = "def evaluate_output(output):"
    new_eval = """def evaluate_output(output, tau_star=None):
    from sklearn.metrics import (accuracy_score, average_precision_score, balanced_accuracy_score,
                                 confusion_matrix, f1_score, matthews_corrcoef, precision_score,
                                 recall_score, roc_auc_score)
    records = [json.loads(line) for line in output.read_text(encoding='utf-8').splitlines() if line.strip()]
    actual = [r for r in records if r.get('response_valid', True)]
    truth = [r['label'] for r in actual]
    predicted = [int(r['raw']) for r in actual if str(r.get('raw', '')).strip() in ('0', '1')]
    metrics = {'n_total': len(records), 'n_score_valid': sum(bool(r['valid']) for r in records),
               'n_response_valid': len(actual),
               'response_coverage': len(actual) / len(records) if records else None,
               'accuracy': None, 'balanced_accuracy': None, 'precision': None, 'recall': None,
               'f1': None, 'mcc': None, 'confusion_matrix': None, 'auroc': None, 'auprc': None}
    if actual and len(predicted) == len(truth):
        metrics.update(accuracy=float(accuracy_score(truth, predicted)),
                       balanced_accuracy=float(balanced_accuracy_score(truth, predicted)),
                       precision=float(precision_score(truth, predicted, zero_division=0)),
                       recall=float(recall_score(truth, predicted, zero_division=0)),
                       f1=float(f1_score(truth, predicted, zero_division=0)),
                       mcc=float(matthews_corrcoef(truth, predicted)),
                       confusion_matrix=confusion_matrix(truth, predicted, labels=[0, 1]).tolist())
    score_rows = [r for r in records if r['valid']]
    if score_rows and len({r['label'] for r in score_rows}) == 2:
        labels = [r['label'] for r in score_rows]
        scores = [r['s'] for r in score_rows]
        metrics.update(auroc=float(roc_auc_score(labels, scores)),
                       auprc=float(average_precision_score(labels, scores)))
    if tau_star is not None and score_rows:
        y_true = np.array([r['label'] for r in score_rows])
        y_score = np.array([r['s'] for r in score_rows])
        y_pred = (y_score >= tau_star).astype(int)
        metrics.update(
            tau_star=float(tau_star),
            mcc_at_tau=float(matthews_corrcoef(y_true, y_pred)),
            ba_at_tau=float(balanced_accuracy_score(y_true, y_pred)),
            f1_at_tau=float(f1_score(y_true, y_pred, zero_division=0))
        )
    return metrics
"""
    if old_eval in c7_text:
        c7_text = c7_text.replace(old_eval, new_eval)
        c7_text = c7_text.replace("metrics = evaluate_output(output)", "metrics = evaluate_output(output, tau_star=tau_val)")
    base_nb['cells'][7]['source'] = [c7_text]

    # Cell 8: Runner loop
    cell8 = """deadline = SESSION_STARTED + MAX_RUNTIME_HOURS * 3600
state = 'error'
progress = validate_records()
try:
    for seed in sorted({seed for seed, ds in bundles}):
        needed = [ds for ds in ('devign', 'reveal')
                  if (seed, ds) in bundles and progress.get((seed, ds), 0) < len(expected[seed, ds])]
        if not needed:
            continue
        if time.time() >= deadline - CHECKPOINT_RESERVE_SECONDS:
            break
        status = OUT_ROOT / f'seed_{seed}_status.json'
        command = [sys.executable, '-u', '/kaggle/working/kaggle_inference.py',
                   '--model', model_path, '--model-revision', revision,
                   '--seed', str(seed), '--arm', ARM, '--expected-model-sha256', MODEL_SHA256,
                   '--gpu-layers', str(GPU_LAYERS), '--deadline-epoch', str(deadline),
                   '--checkpoint-reserve-seconds', str(CHECKPOINT_RESERVE_SECONDS), '--status', str(status)]
        for ds in needed:
            command += ['--run', ds, 'validation', str(bundles[seed, ds]),
                        str(OUT_ROOT / f'seed_{seed}' / ds / 'validation')]
        run_logged(command, f'validation_seed_{seed}')
        progress = validate_records()
        result = json.loads(status.read_text(encoding='utf-8'))
        if result['timed_out']:
            break
        if any(progress[seed, ds] != len(expected[seed, ds]) for ds in needed):
            raise RuntimeError('Validation stopped without a timeout or complete output')
    complete = all(progress[key] == len(expected[key]) for key in expected)
    state = 'validation_complete' if complete else 'timed_out'
finally:
    summary = {'runtime_contract_sha256': EXPECTED_CONTRACT_SHA256, 'arm': ARM, 'state': state, 'split': 'validation', 'bundle_sha256': BUNDLE_SHA256,
               'locked_tau': LOCKED_THRESHOLDS,
               'progress': {f'{seed}/{ds}': progress.get((seed, ds), 0) for seed, ds in expected}}
    (OUT_ROOT / 'batch_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    archive = shutil.make_archive(str(Path('/kaggle/working') / CHECKPOINT_NAME.removesuffix('.zip')),
                                  'zip', root_dir=OUT_ROOT)
    print(state, archive)
    diagnostics_zip()
"""
    base_nb['cells'][8]['source'] = [cell8]

    # Write target and staging
    TARGET_NB.parent.mkdir(parents=True, exist_ok=True)
    TARGET_NB.write_text(json.dumps(base_nb, indent=1, ensure_ascii=False), encoding='utf-8')
    print(f"B3 amended notebook written to canonical target: {TARGET_NB}")

    STAGING_NB.parent.mkdir(parents=True, exist_ok=True)
    STAGING_NB.write_text(json.dumps(base_nb, indent=1, ensure_ascii=False), encoding='utf-8')
    print(f"B3 amended notebook written to staging target: {STAGING_NB}")

if __name__ == '__main__':
    build_b3_notebook()
