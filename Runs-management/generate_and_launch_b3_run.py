import os
import sys
import json
import time
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import builtins
orig_open = builtins.open

def utf8_open(*args, **kwargs):
    if len(args) > 1 and 'b' in args[1]:
        return orig_open(*args, **kwargs)
    if 'mode' in kwargs and 'b' in kwargs['mode']:
        return orig_open(*args, **kwargs)
    if 'encoding' not in kwargs:
        kwargs['encoding'] = 'utf-8'
    return orig_open(*args, **kwargs)

builtins.open = utf8_open

def build_notebook():
    ref_nb_path = Path('Runs-management/kaggle_validation_6arms_20261104/02_kaggle_qwen_q4_b1_full_validation.ipynb')
    with open(ref_nb_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    # Cell 0: Markdown title
    nb['cells'][0]['source'] = [
        "# B3 & B3-nodiff — Kaggle Validation Arms\n",
        "\n",
        "Chạy 2 arm tương phản (contrastive) trên tập validation:\n",
        "- **B3**: Prompt gồm code mục tiêu + CPG graph prefix + cặp demo (safe & vuln) + Key difference explanation.\n",
        "- **B3-nodiff**: Prompt gồm code mục tiêu + CPG graph prefix + cặp demo (safe & vuln) KHÔNG có Key difference.\n",
        "\n",
        "Model: Qwen3-Coder-30B-A3B-Instruct Q4_K_M trên 2x Tesla T4 GPU."
    ]

    # Cell 1: Logging & diagnostics
    c1 = ''.join(nb['cells'][1]['source'])
    c1 = c1.replace(
        "is_inference = name.startswith('resume_seed_')",
        "is_inference = name.startswith('validation_') or name.startswith('resume_seed_')"
    )
    nb['cells'][1]['source'] = [c1]

    # Cell 2: Configuration constants
    cell_2_code = '''import math
KAGGLE_INPUT_ROOT = Path('/kaggle/input')
BUNDLE_WORK = Path('/kaggle/working/b3_bundles')
OUT_ROOT = Path('/kaggle/working/b3_validation')
BUNDLE_NAME = 'grace_b3_validation_inputs.zip'
BUNDLE_SHA256 = '87527ce21b8eff4d07cb8e979f16d312c7f336fe9382ed825a24767f592363d9'
CHECKPOINT_NAME = 'grace_b3_validation_checkpoint.zip'
CHECKPOINT_INPUT_PATH = None
MODEL_FILENAME = 'Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf'
MODEL_SHA256 = 'f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335'
MAX_RUNTIME_HOURS = 9
CHECKPOINT_RESERVE_SECONDS = 300
GPU_LAYERS = -1

RUN_SPECS = [
    {
        "arm": "B3",
        "seed": 42,
        "dataset": "devign",
        "member_path": "b3/seed_42/devign_validation.zip",
        "inner_sha256": "e840c8fe882e1be649da4ba9f878a19e6ef6abc88a4084b82ad8162980ea2f2a",
        "prompts_sha256": "17e7a38942e2d82d5e8f4695da235da4022c719fa88057bf7538bf14972b9f34",
        "count": 2732
    },
    {
        "arm": "B3",
        "seed": 42,
        "dataset": "reveal",
        "member_path": "b3/seed_42/reveal_validation.zip",
        "inner_sha256": "02d23be55b8653ce88fb7944def6180fb73ed91cdbd328133d39967f75416421",
        "prompts_sha256": "0b747c74ef58fe8b6edbdd0c8c8659905def1a39503811a1602193134b399753",
        "count": 2273
    },
    {
        "arm": "B3-nodiff",
        "seed": 42,
        "dataset": "devign",
        "member_path": "b3_nodiff/seed_42/devign_validation.zip",
        "inner_sha256": "63a5ec41df4e8c85600b49676e92f34fec29cfb36d864313778c5e8744d9a9d7",
        "prompts_sha256": "4a40f20bfebf1e0b607f72304430aec08e7221b91f47a85fd9211f03432afa43",
        "count": 2732
    },
    {
        "arm": "B3-nodiff",
        "seed": 42,
        "dataset": "reveal",
        "member_path": "b3_nodiff/seed_42/reveal_validation.zip",
        "inner_sha256": "4a5dd84f0632611cc4e5322ef3bf842bd827d70bee0542110d8e95af26a0d686",
        "prompts_sha256": "91c9f04212e2490fc7701118ee2d5c2870bb604fdde4c5b425894d819bfc9740",
        "count": 2273
    }
]
'''
    nb['cells'][2]['source'] = [cell_2_code]

    # Cell 3: Bundle loading & validation checking
    cell_3_code = '''def hash_bytes(data):
    return hashlib.sha256(data).hexdigest()

BUNDLE_WORK.mkdir(parents=True, exist_ok=True)
OUT_ROOT.mkdir(parents=True, exist_ok=True)
bundles = {}
expected = {}

bundle_candidates = sorted(KAGGLE_INPUT_ROOT.rglob(BUNDLE_NAME))
if not bundle_candidates:
    bundle_candidates = sorted(KAGGLE_INPUT_ROOT.rglob(BUNDLE_NAME + '.*'))

if bundle_candidates and len(bundle_candidates) == 1:
    bundle_path = bundle_candidates[0]
    if hash_bytes(bundle_path.read_bytes()) != BUNDLE_SHA256:
        raise ValueError(f'Unexpected input bundle SHA-256 for {bundle_path}')
    note(f'Loaded packed bundle: {bundle_path} (verified SHA-256 {BUNDLE_SHA256})')
    with zipfile.ZipFile(bundle_path) as bundle:
        for spec in RUN_SPECS:
            arm, seed, ds = spec['arm'], spec['seed'], spec['dataset']
            payload = bundle.read(spec['member_path'])
            if hash_bytes(payload) != spec['inner_sha256']:
                raise ValueError(f'SHA-256 mismatch for member {spec["member_path"]}')
            path = BUNDLE_WORK / f'{arm}_{seed}_{ds}.zip'
            path.write_bytes(payload)
            bundles[arm, seed, ds] = path
            with zipfile.ZipFile(path) as inner:
                records = [json.loads(line) for line in inner.read('prompts.jsonl').splitlines() if line.strip()]
            expected[arm, seed, ds] = {r['id']: (r['prompt_sha256'], r['label']) for r in records}
            note(f'Loaded bundle {arm} seed {seed} {ds}: {len(expected[arm, seed, ds])} prompts')
else:
    note(f'Bundle archive {BUNDLE_NAME} not found as single file; discovering Kaggle auto-unpacked files under {KAGGLE_INPUT_ROOT}')
    for spec in RUN_SPECS:
        arm, seed, ds = spec['arm'], spec['seed'], spec['dataset']
        arm_clean = arm.replace('-', '_').lower()
        manifest_candidates = sorted(p for p in KAGGLE_INPUT_ROOT.rglob('bundle_manifest.json')
                                     if f'/{arm_clean}/' in p.as_posix().lower() and f'seed_{seed}' in p.as_posix() and ds in p.as_posix())
        if len(manifest_candidates) != 1:
            raise FileNotFoundError(f'Expected 1 bundle_manifest.json for {arm} seed {seed} {ds}; found {manifest_candidates}')
        manifest_file = manifest_candidates[0]
        prompts_file = manifest_file.parent / 'prompts.jsonl'
        if not prompts_file.is_file():
            raise FileNotFoundError(f'Missing prompts.jsonl next to {manifest_file}')
        manifest = json.loads(manifest_file.read_text(encoding='utf-8'))
        prompts_bytes = prompts_file.read_bytes()
        if hash_bytes(prompts_bytes) != manifest['prompts_sha256']:
            raise ValueError(f'Prompt SHA256 mismatch for {prompts_file}: expected {manifest["prompts_sha256"]}')
        if (manifest.get('arm'), manifest.get('seed'), manifest.get('dataset'), manifest.get('split')) != (arm, seed, ds, 'validation'):
            raise ValueError(f'Manifest identity mismatch in {manifest_file}: {manifest}')
        path = BUNDLE_WORK / f'{arm}_{seed}_{ds}.zip'
        with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED) as z:
            z.writestr('bundle_manifest.json', manifest_file.read_bytes())
            z.writestr('prompts.jsonl', prompts_bytes)
        bundles[arm, seed, ds] = path
        records = [json.loads(line) for line in prompts_bytes.decode('utf-8').splitlines() if line.strip()]
        expected[arm, seed, ds] = {r['id']: (r['prompt_sha256'], r['label']) for r in records}
        note(f'Loaded auto-unpacked bundle for {arm} seed {seed} {ds}: {len(expected[arm, seed, ds])} prompts, verified SHA-256')

checkpoint = None
if CHECKPOINT_INPUT_PATH is not None:
    checkpoint = Path(CHECKPOINT_INPUT_PATH)
else:
    candidates = sorted(KAGGLE_INPUT_ROOT.rglob(CHECKPOINT_NAME))
    if len(candidates) > 1:
        raise ValueError('Set CHECKPOINT_INPUT_PATH to the intended checkpoint')
    checkpoint = candidates[0] if candidates else None

if checkpoint:
    note(f'Found existing checkpoint: {checkpoint}. Restoring prior completed records...')
    with zipfile.ZipFile(checkpoint) as source:
        for name in source.namelist():
            if name.endswith('records.jsonl') or name.endswith('run_manifest.json') or name.endswith('evaluation.json'):
                target = OUT_ROOT / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(source.read(name))
    note('Checkpoint restoration complete.')

def validate_records():
    progress = {}
    for (arm, seed, ds), prompts in expected.items():
        folder = OUT_ROOT / arm / f'seed_{seed}' / ds / 'validation'
        path = folder / 'records.jsonl'
        seen = set()
        if path.exists():
            if not (folder / 'run_manifest.json').is_file():
                raise ValueError(f'Missing run manifest: {path}')
            for line in path.read_text(encoding='utf-8').splitlines():
                if not line.strip(): continue
                row = json.loads(line)
                uid = row['id']
                identity = (row['arm'], row['seed'], row['dataset'], row['split'], row['model_sha256'])
                if (uid in seen or identity != (arm, seed, ds, 'validation', MODEL_SHA256)
                        or prompts.get(uid) != (row['prompt_sha256'], row['label'])
                        or not math.isfinite(row['s'])):
                    raise ValueError(f'Unexpected record: {path}/{uid}')
                seen.add(uid)
        progress[arm, seed, ds] = len(seen)
    return progress
'''
    nb['cells'][3]['source'] = [cell_3_code]

    # Cell 8: Multi-arm execution loop
    cell_8_code = '''deadline = time.time() + MAX_RUNTIME_HOURS * 3600
state = 'error'
progress = validate_records()
try:
    for arm in ['B3', 'B3-nodiff']:
        seed = 42
        needed = [ds for ds in ('devign', 'reveal')
                  if (arm, seed, ds) in bundles and progress.get((arm, seed, ds), 0) < len(expected[arm, seed, ds])]
        if not needed:
            note(f'Arm {arm} is already 100% complete. Skipping.')
            continue
        if time.time() >= deadline - CHECKPOINT_RESERVE_SECONDS:
            note('Watchdog deadline reached before starting next arm.')
            break
        status = OUT_ROOT / arm / f'seed_{seed}_status.json'
        status.parent.mkdir(parents=True, exist_ok=True)
        command = [sys.executable, '-u', '/kaggle/working/kaggle_inference.py',
                   '--model', str(model_files[0]), '--model-revision', 'b2cff646eb4bb1d68355c01b18ae02e7cf42d120',
                   '--seed', str(seed), '--arm', arm, '--expected-model-sha256', MODEL_SHA256,
                   '--gpu-layers', str(GPU_LAYERS), '--deadline-epoch', str(deadline),
                   '--checkpoint-reserve-seconds', str(CHECKPOINT_RESERVE_SECONDS), '--status', str(status)]
        for ds in needed:
            command += ['--run', ds, 'validation', str(bundles[arm, seed, ds]),
                        str(OUT_ROOT / arm / f'seed_{seed}' / ds / 'validation')]
        run_logged(command, f'validation_{arm}_seed_{seed}')
        progress = validate_records()
        if status.is_file():
            result = json.loads(status.read_text(encoding='utf-8'))
            if result.get('timed_out'):
                note(f'Arm {arm} encountered runtime limit. Stopping loop.')
                break
        if any(progress.get((arm, seed, ds), 0) != len(expected[arm, seed, ds]) for ds in needed):
            raise RuntimeError(f'Validation for {arm} stopped without a timeout or complete output')
    complete = all(progress.get(key, 0) == len(expected[key]) for key in expected)
    state = 'validation_complete' if complete else 'timed_out'
finally:
    summary = {'arms': ['B3', 'B3-nodiff'], 'state': state, 'split': 'validation', 'bundle_sha256': BUNDLE_SHA256,
               'progress': {f'{k[0]}/{k[1]}/{k[2]}': progress.get(k, 0) for k in expected}}
    (OUT_ROOT / 'batch_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    archive = shutil.make_archive(str(Path('/kaggle/working') / CHECKPOINT_NAME.removesuffix('.zip')),
                                  'zip', root_dir=OUT_ROOT)
    print(state, archive)
    diagnostics_zip()
'''
    nb['cells'][8]['source'] = [cell_8_code]

    return nb

def main():
    root = Path(__file__).resolve().parent.parent
    staging_dir = root / 'Runs-management/kaggle_staging_thanhduy/b3_validation_run'
    staging_dir.mkdir(parents=True, exist_ok=True)

    nb = build_notebook()
    nb_path = staging_dir / '02_kaggle_qwen_q4_b3_validation.ipynb'
    with open(nb_path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
    print(f'Wrote notebook: {nb_path}')

    meta = {
        "id": "thanhduy9a4tv/grace-b3-validation",
        "title": "grace-b3-validation",
        "code_file": "02_kaggle_qwen_q4_b3_validation.ipynb",
        "language": "python",
        "kernel_type": "notebook",
        "is_private": True,
        "enable_gpu": True,
        "enable_tpu": False,
        "enable_internet": True,
        "keywords": [],
        "dataset_sources": [
            "thanhduy9a4tv/grace-b3-validation-inputs"
        ],
        "kernel_sources": [
            "thanhduy9a4tv/qwen3coder30b-prepare-notebook"
        ],
        "competition_sources": [],
        "model_sources": []
    }
    meta_path = staging_dir / 'kernel-metadata.json'
    meta_path.write_text(json.dumps(meta, indent=2), encoding='utf-8')
    print(f'Wrote metadata: {meta_path}')

    os.environ['KAGGLE_USERNAME'] = 'thanhduy9a4tv'
    os.environ['KAGGLE_KEY'] = 'KGAT_47e27c5341b3301eea2f4e8f3d4743d6'
    os.environ['KAGGLE_API_TOKEN'] = 'KGAT_47e27c5341b3301eea2f4e8f3d4743d6'

    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    api.authenticate()

    print('Pushing B3 validation kernel (v3) to Kaggle as thanhduy9a4tv...')
    res = api.kernels_push(str(staging_dir))
    print('Kernels push response:', res)

    time.sleep(5)
    st = api.kernels_status('thanhduy9a4tv/grace-b3-validation')
    print('Initial status:', st)

if __name__ == '__main__':
    main()
