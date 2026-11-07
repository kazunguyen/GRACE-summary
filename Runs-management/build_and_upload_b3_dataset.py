import os
import sys
import json
import hashlib
import zipfile
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import builtins
orig_open = builtins.open
def utf8_open(file, mode='r', *args, **kwargs):
    if 'b' not in mode and 'encoding' not in kwargs:
        kwargs['encoding'] = 'utf-8'
    return orig_open(file, mode, *args, **kwargs)
builtins.open = utf8_open

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def load_labels(path: Path) -> dict:
    labels = {}
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                labels[r['id']] = r['label']
    return labels

def main():
    root = Path(__file__).resolve().parent.parent
    dry_run_root = root / 'Runs-management/dry_run_validation_20261102'
    staging_dir = root / 'Runs-management/kaggle_staging_thanhduy/dataset_b3'
    staging_dir.mkdir(parents=True, exist_ok=True)

    labels = {
        'devign': load_labels(root / 'data/specs/devign_validation_15arms.jsonl'),
        'reveal': load_labels(root / 'data/specs/reveal_validation_15arms.jsonl')
    }
    print(f'Loaded labels: Devign={len(labels["devign"])}, Reveal={len(labels["reveal"])}')

    zip_path = staging_dir / 'grace_b3_validation_inputs.zip'
    
    runs = [
        ('B3', 'devign', 42, 2732),
        ('B3', 'reveal', 42, 2273),
        ('B3-nodiff', 'devign', 42, 2732),
        ('B3-nodiff', 'reveal', 42, 2273),
    ]

    bundle_manifests = {}
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as outer_zip:
        for arm, ds, seed, expected_count in runs:
            src_dir = dry_run_root / ds / 'validation' / arm / str(seed)
            prompts_path = src_dir / 'prompts.jsonl'
            manifest_path = src_dir / 'manifest.json'

            if not prompts_path.is_file() or not manifest_path.is_file():
                raise FileNotFoundError(f'Missing files in {src_dir}')

            formatted_lines = []
            with open(prompts_path, 'r', encoding='utf-8') as pf:
                for line in pf:
                    if not line.strip():
                        continue
                    row = json.loads(line)
                    uid = row['id']
                    if uid not in labels[ds]:
                        raise KeyError(f'Missing label for ID {uid} in {ds}')
                    
                    demos = row['evidence']['demo'].get('demos', [])
                    demo_ids = [d['function_uid'] for d in demos] if demos else []
                    
                    rec = {
                        'id': uid,
                        'dataset': ds,
                        'split': 'validation',
                        'arm': arm,
                        'seed': seed,
                        'label': labels[ds][uid],
                        'prompt_sha256': row['prompt_sha256'],
                        'prompt': row['prompt'],
                        'demo_ids': demo_ids,
                        'tokens': row['evidence']['tokens'],
                        'graph_missing': row['evidence']['graph'].get('missing', False)
                    }
                    formatted_lines.append(json.dumps(rec, ensure_ascii=False))

            if len(formatted_lines) != expected_count:
                raise ValueError(f'Count mismatch for {arm} {ds}: {len(formatted_lines)} != {expected_count}')

            prompts_bytes = ('\n'.join(formatted_lines) + '\n').encode('utf-8')
            prompts_sha = sha256_bytes(prompts_bytes)

            inner_manifest = {
                'arm': arm,
                'seed': seed,
                'dataset': ds,
                'split': 'validation',
                'count': expected_count,
                'prompts_sha256': prompts_sha,
                'tokenizer': 'Qwen/Qwen3-Coder-30B-A3B-Instruct',
                'tokenizer_revision': 'b2cff646eb4bb1d68355c01b18ae02e7cf42d120',
                'prompt_budget_tokens': 8192,
                'model_repo': 'ggml-org/Qwen3-Coder-30B-A3B-Instruct-GGUF',
                'quantization': 'Q4_K_M'
            }

            inner_buffer = staging_dir / f'{arm}_{ds}_tmp.zip'
            with zipfile.ZipFile(inner_buffer, 'w', compression=zipfile.ZIP_DEFLATED) as inner_zip:
                inner_zip.writestr('bundle_manifest.json', json.dumps(inner_manifest, indent=2).encode('utf-8'))
                inner_zip.writestr('prompts.jsonl', prompts_bytes)
            
            inner_bytes = inner_buffer.read_bytes()
            inner_buffer.unlink()

            arm_key = arm.replace('-', '_').lower()
            inner_arcname = f'{arm_key}/seed_{seed}/{ds}_validation.zip'
            outer_zip.writestr(inner_arcname, inner_bytes)
            print(f'Added {inner_arcname} ({len(inner_bytes):,} bytes, inner_sha256: {sha256_bytes(inner_bytes)[:16]}...)')
            
            bundle_manifests[f'{arm}/{seed}/{ds}'] = {
                'member_path': inner_arcname,
                'inner_zip_sha256': sha256_bytes(inner_bytes),
                'prompts_sha256': prompts_sha,
                'count': expected_count
            }

    outer_sha256 = sha256_file(zip_path)
    print(f'Successfully built {zip_path.name} ({zip_path.stat().st_size:,} bytes)')
    print(f'Outer bundle SHA-256: {outer_sha256}')

    bundle_info = {
        'bundle_name': zip_path.name,
        'bundle_sha256': outer_sha256,
        'size_bytes': zip_path.stat().st_size,
        'runs': bundle_manifests
    }
    (staging_dir / 'bundle_info.json').write_text(json.dumps(bundle_info, indent=2), encoding='utf-8')

    meta = {
        'title': 'grace-b3-validation-inputs',
        'id': 'thanhduy9a4tv/grace-b3-validation-inputs',
        'licenses': [{'name': 'CC0-1.0'}]
    }
    (staging_dir / 'dataset-metadata.json').write_text(json.dumps(meta, indent=2), encoding='utf-8')

    print('Uploading new version to Kaggle as thanhduy9a4tv...')
    os.environ['KAGGLE_USERNAME'] = 'thanhduy9a4tv'
    os.environ['KAGGLE_KEY'] = 'KGAT_47e27c5341b3301eea2f4e8f3d4743d6'
    os.environ['KAGGLE_API_TOKEN'] = 'KGAT_47e27c5341b3301eea2f4e8f3d4743d6'

    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    api.authenticate()

    target_ref = 'thanhduy9a4tv/grace-b3-validation-inputs'
    api.dataset_create_version(str(staging_dir), version_notes='Full schema prompts with labels and evidence tokens', dir_mode='zip')
    print('Dataset version created successfully!')

if __name__ == '__main__':
    main()
