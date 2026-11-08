import math

ARM = 'B2-rand'
KAGGLE_INPUT_ROOT = Path('/kaggle/input')
OUT_ROOT = Path('/kaggle/working/b2_rand_three_seed_test_tail')
BUNDLE_WORK = Path('/kaggle/working/b2_rand_three_seed_tail_inputs')
CHECKPOINT_NAME = 'grace_b2_rand_three_seed_test_tail_checkpoint.zip'
CHECKPOINT_RESERVE_SECONDS = 300
MODEL_FILENAME = RUNTIME['model']['filename']
MODEL_SHA256 = RUNTIME['model']['sha256']
GPU_LAYERS = RUNTIME['constructor']['n_gpu_layers']

def input_file(name):
    matches = sorted(p for p in KAGGLE_INPUT_ROOT.rglob(name) if p.is_file())
    if len(matches) > 1:
        raise ValueError(f'Multiple attached copies of {name}. Keep exactly one.')
    return matches[0] if matches else None

def hash_bytes(data):
    return hashlib.sha256(data).hexdigest()

packed = input_file(BUNDLE_NAME)
if packed:
    if hash_bytes(packed.read_bytes()) != BUNDLE_SHA256:
        raise ValueError('Tail bundle SHA-256 mismatch')
    with zipfile.ZipFile(packed) as z:
        if sorted(z.namelist()) != sorted(MEMBERS):
            raise ValueError('Unexpected tail bundle members')
        data = {name: z.read(name) for name in MEMBERS}
else:
    manifest_path = input_file('b2_rand_tail_delivery.json')
    if manifest_path is None:
        raise FileNotFoundError(f'Attach {BUNDLE_NAME} or its Kaggle-extracted contents')
    data = {name: (manifest_path.parent / name).read_bytes() for name in MEMBERS}
for name, digest in MEMBERS.items():
    if hash_bytes(data[name]) != digest:
        raise ValueError(f'Input hash mismatch: {name}')

delivery = json.loads(data['b2_rand_tail_delivery.json'])
threshold_bytes = data['b2_rand_tail_threshold_lock.json']
threshold = json.loads(threshold_bytes)
unsigned = {k: v for k, v in threshold.items() if k != 'locked_sha256'}
if hash_bytes(json.dumps(unsigned, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()) != THRESHOLD_LOCK_SHA256:
    raise ValueError('Threshold lock integrity mismatch')
if threshold['locked_sha256'] != THRESHOLD_LOCK_SHA256 or threshold['model_sha256'] != MODEL_SHA256:
    raise ValueError('Threshold/model identity mismatch')

def checkpoint_source(zip_name, marker, required):
    path = input_file(zip_name)
    if path:
        with zipfile.ZipFile(path) as z:
            names = z.namelist()
            if len(names) != len(set(names)):
                raise ValueError(f'Duplicate archive members in {zip_name}')
            return {name: z.read(name) for name in required if name in names}
    marker_path = input_file(marker)
    if marker_path:
        root = marker_path.parent
        return {name: (root / name).read_bytes() for name in required if (root / name).is_file()}
    return None

def records(raw):
    return [json.loads(line) for line in raw.splitlines() if line.strip()]

def verify_records(raw, expected_rows, seed, ds, tau, runtime_sha, seal):
    found = set()
    for row in records(raw):
        uid = str(row['id'])
        item = expected_rows.get(uid)
        if uid in found or item is None:
            raise ValueError(f'Duplicate or unexpected checkpoint ID: {seed}/{ds}/{uid}')
        if (row['seed'], row['dataset'], row['split'], row['arm']) != (seed, ds, 'test', ARM):
            raise ValueError(f'Wrong checkpoint arm/seed/dataset/split for {uid}')
        if (row['label'], row['prompt_sha256']) != (item['label'], item['prompt_sha256']):
            raise ValueError(f'Checkpoint prompt mismatch for {uid}')
        if (row['model_sha256'], row['runtime_contract_sha256'], row['threshold_lock_sha256'], row['tau'],
                row['inference_seed']) != (MODEL_SHA256, runtime_sha, seal, tau, RUNTIME['constructor']['seed']):
            raise ValueError(f'Checkpoint model/runtime/threshold mismatch for {uid}')
        if (not row['valid'] or not all(math.isfinite(row[k]) for k in ('s', 'logprob_0', 'logprob_1'))
                or not 0 <= row['s'] <= 1 or row['pred_tau'] != int(row['s'] >= tau)):
            raise ValueError(f'Invalid saved score for {uid}')
        found.add(uid)
    return found

bundles = {}
expected = {}
plan_sets = []
BUNDLE_WORK.mkdir(parents=True, exist_ok=True)
for spec in delivery['inputs']:
    seed, ds = spec['seed'], spec['dataset']
    prefix = spec['prefix']
    manifest = json.loads(data[prefix + '_manifest.json'])
    raw = data[prefix + '_prompts.jsonl']
    items = records(raw)
    by_id = {str(row['id']): row for row in items}
    if len(by_id) != len(items) or hash_bytes(raw) != manifest['prompts_sha256']:
        raise ValueError(f'Wrong prompt list: {prefix}')
    entry = threshold['entries'][f'{ARM}/{seed}/{ds}']
    if (manifest['arm'], manifest['seed'], manifest['dataset'], manifest['split'], manifest['tau_star'],
            manifest['model_sha256'], manifest['tokenizer_revision']) != (
            ARM, seed, ds, 'test', entry['tau_star'], MODEL_SHA256, RUNTIME['tokenizer']['revision']):
        raise ValueError(f'Input identity mismatch: {prefix}')
    if spec['excluded_before'] + len(items) != spec['census_count']:
        raise ValueError(f'Count mismatch: {prefix}')
    manifest.update(count=len(items), threshold_lock_sha256=THRESHOLD_LOCK_SHA256)
    plan_sets.append(dict(spec, remaining=len(items), prompts_sha256=manifest['prompts_sha256']))
    if not items:
        continue
    bundle_path = BUNDLE_WORK / (prefix + '.zip')
    with zipfile.ZipFile(bundle_path, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr('bundle_manifest.json', json.dumps(manifest))
        z.writestr('prompts.jsonl', raw)
        z.writestr('threshold_lock.json', threshold_bytes)
    bundles[seed, ds] = bundle_path
    expected[seed, ds] = {str(row['id']): row for row in items}

plan = {
    'run_kind': 'remaining_test_ids_only',
    'runtime_contract_sha256': EXPECTED_CONTRACT_SHA256,
    'input_bundle_sha256': BUNDLE_SHA256,
    'threshold_lock_sha256': THRESHOLD_LOCK_SHA256,
    'sets': plan_sets,
}
plan_bytes = (json.dumps(plan, sort_keys=True, indent=2) + '\n').encode()
OUT_ROOT.mkdir(parents=True, exist_ok=True)
marker = 'b2_rand_tail_plan.json'
allowed = {f'seed_{seed}/{ds}/test/{name}' for seed, ds in expected
           for name in ('records.jsonl', 'run_manifest.json')}
resume = checkpoint_source(CHECKPOINT_NAME, marker, [marker, *sorted(allowed)])
if resume:
    if resume.get(marker) != plan_bytes:
        raise ValueError('Resume checkpoint does not match this exact ID plan/runtime')
    for name in sorted(allowed & resume.keys()):
        dest = OUT_ROOT / name
        if dest.exists() and dest.read_bytes() != resume[name]:
            raise ValueError(f'Local records and attached checkpoint differ: {name}')
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(resume[name])
if (OUT_ROOT / marker).exists() and (OUT_ROOT / marker).read_bytes() != plan_bytes:
    raise ValueError('Existing local output uses a different ID plan')
(OUT_ROOT / marker).write_bytes(plan_bytes)
(OUT_ROOT / 'inference_runtime_lock.json').write_bytes(RUNTIME_LOCK_BYTES)
(OUT_ROOT / 'threshold_lock.json').write_bytes(threshold_bytes)

def validate_records():
    counts = {}
    for (seed, ds), items in expected.items():
        root = OUT_ROOT / f'seed_{seed}' / ds / 'test'
        path = root / 'records.jsonl'
        tau = threshold['entries'][f'{ARM}/{seed}/{ds}']['tau_star']
        if path.exists():
            meta = json.loads((root / 'run_manifest.json').read_bytes())
            if meta['runtime_contract_sha256'] != EXPECTED_CONTRACT_SHA256:
                raise ValueError(f'Resume manifest has a different runtime: {seed}/{ds}')
        counts[seed, ds] = len(verify_records(path.read_bytes(), items, seed, ds, tau,
                                  EXPECTED_CONTRACT_SHA256, THRESHOLD_LOCK_SHA256)) if path.exists() else 0
    return counts

for p in plan_sets:
    print(f"Seed {p['seed']} {p['dataset']}: excluded {p['excluded_before']} ({p['exclusion_basis']}), scheduled {p['remaining']}")
print('Tail progress on this runtime:', validate_records())
