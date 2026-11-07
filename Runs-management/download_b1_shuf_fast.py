import os
import sys
import json
import requests
import zipfile
import shutil

for k in ['KAGGLE_USERNAME', 'KAGGLE_KEY', 'KAGGLE_API_TOKEN', 'KAGGLE_CONFIG_DIR']:
    if k in os.environ:
        del os.environ[k]

from kaggle.api.kaggle_api_extended import KaggleApi
from kagglesdk.kernels.types.kernels_api_service import ApiListKernelSessionOutputRequest

api = KaggleApi()
api.authenticate()

out_dir = 'Runs-management/output_b1_shuf'
os.makedirs(out_dir, exist_ok=True)

with api.build_kaggle_client() as kaggle:
    req = ApiListKernelSessionOutputRequest()
    req.user_name = 'tomandjerry223'
    req.kernel_slug = 'grace-b1-shuf-validation'
    resp = kaggle.kernels.kernels_api_client.list_kernel_session_output(req)
    print(f"Total files to download: {len(resp.files)}", flush=True)

    for i, item in enumerate(resp.files, 1):
        target = os.path.join(out_dir, item.file_name)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        r = requests.get(item.url, timeout=30)
        with open(target, 'wb') as f:
            f.write(r.content)
        print(f"[{i}/{len(resp.files)}] Downloaded: {item.file_name} ({len(r.content)} bytes)", flush=True)

    # Save log with utf-8 encoding
    if resp.log:
        log_path = os.path.join(out_dir, 'grace-b1-shuf-validation.log')
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(resp.log)
        print(f"Saved session log: {log_path} ({len(resp.log)} chars)", flush=True)

print("\n=== ALL FILES DOWNLOADED SUCCESSFULLY! ===", flush=True)
