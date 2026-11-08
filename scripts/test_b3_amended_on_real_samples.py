import json
import sys
import zipfile
import io
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Check real Devign prompt from grace_b3_validation_inputs.zip
zpath = 'Runs-management/kaggle_staging_lznt123/dataset_b3_inputs/grace_b3_validation_inputs.zip'
with zipfile.ZipFile(zpath) as z:
    inner = zipfile.ZipFile(io.BytesIO(z.read('b3/seed_42/devign_validation.zip')))
    manifest = json.loads(inner.read('bundle_manifest.json'))
    print('Devign validation count:', manifest['count'])
    
    # Read first 3 prompts
    lines = inner.read('prompts.jsonl').decode('utf-8').splitlines()
    print('Total lines in prompts.jsonl:', len(lines))
    for i in range(min(3, len(lines))):
        row = json.loads(lines[i])
        print(f"Row {i}: id={row['id']}, label={row['label']}, prompt_len={len(row['prompt'])}")

print("Verified real Devign prompts are loaded and valid.")
