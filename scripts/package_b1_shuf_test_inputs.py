import hashlib
import json
from pathlib import Path
import zipfile

prompts_root = Path('08_Arm_B1_Shuf/output/test_shuf_prompts')
staging_dir = Path('08_Arm_B1_Shuf/staging_test_inputs')
staging_dir.mkdir(parents=True, exist_ok=True)

sets = []
frozen_manifests = {}

for seed in [42, 43, 44]:
    for ds in ['devign', 'reveal']:
        inner_zip_name = f'seed_{seed}/{ds}_test.zip'
        src_dir = prompts_root / f'seed_{seed}' / ds / 'test'

        manifest_file = src_dir / 'bundle_manifest.json'
        prompts_file = src_dir / 'prompts.jsonl'

        manifest_bytes = manifest_file.read_bytes()
        prompts_bytes = prompts_file.read_bytes()

        manifest_hash = hashlib.sha256(manifest_bytes).hexdigest()
        frozen_manifests[(seed, ds)] = manifest_hash

        # Build normalized inner zip
        inner_zip_path = staging_dir / f'seed_{seed}_{ds}_test.zip'
        with zipfile.ZipFile(
            inner_zip_path, 'w', compression=zipfile.ZIP_DEFLATED
        ) as iz:
            iz.writestr('bundle_manifest.json', manifest_bytes)
            iz.writestr('prompts.jsonl', prompts_bytes)

        inner_bytes = inner_zip_path.read_bytes()
        inner_hash = hashlib.sha256(inner_bytes).hexdigest()

        sets.append({
            'name': inner_zip_name,
            'sha256': inner_hash,
            'seed': seed,
            'dataset': ds,
            'path': inner_zip_path,
        })
        print(f'{inner_zip_name}: hash={inner_hash}, manifest={manifest_hash}')

# Now package into grace_b1_shuf_test_inputs.zip
bundle_zip_path = staging_dir / 'grace_b1_shuf_test_inputs.zip'
with zipfile.ZipFile(bundle_zip_path, 'w', compression=zipfile.ZIP_STORED) as bz:
    for s in sets:
        bz.write(s['path'], arcname=s['name'])

bundle_bytes = bundle_zip_path.read_bytes()
bundle_hash = hashlib.sha256(bundle_bytes).hexdigest()
print(f'BUNDLE_SHA256 = {bundle_hash}, size = {len(bundle_bytes)} bytes')

# Output configuration snippet
print('\n=== CONFIGURATION FOR NOTEBOOK CELL 2 ===')
sets_clean = [
    {'name': s['name'], 'sha256': s['sha256'], 'seed': s['seed'], 'dataset': s['dataset']}
    for s in sets
]
print(f"BUNDLE_SHA256 = '{bundle_hash}'")
print(f'SETS = {json.dumps(sets_clean, indent=None)}')
frozen_str = '{' + ', '.join(f"({k[0]}, '{k[1]}'): '{v}'" for k, v in frozen_manifests.items()) + '}'
print(f'FROZEN_MANIFEST_SHA256 = {frozen_str}')
