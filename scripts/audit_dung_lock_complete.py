import json
import os
import sys
import zipfile
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

zip_path = r'Runs-management/grace_hieu_5arms_runtime_locked_20261107.zip'
with zipfile.ZipFile(zip_path) as z:
    nb = json.loads(z.read(z.namelist()[0]).decode('utf-8'))
    c1 = "".join(nb['cells'][1]['source'])

# Find RUNTIME_LOCK_BYTES
for line in c1.splitlines():
    if line.startswith('RUNTIME_LOCK_BYTES = b'):
        raw_bytes = eval(line.split(' = ', 1)[1])
        contract = json.loads(raw_bytes.decode('utf-8'))
        print("Contract ID:", contract.get('contract_id'))
        print("Status:", contract.get('status'))
        print("Packages:")
        for pkg, ver in contract.get('packages', {}).items():
            print(f"  {pkg} == {ver}")
        print("Backend source:")
        for k, v in contract.get('backend_source', {}).items():
            print(f"  {k}: {v}")
        print("Constructor:")
        for k, v in contract.get('constructor', {}).items():
            print(f"  {k}: {v}")
        print("GPU:")
        for k, v in contract.get('gpu', {}).items():
            print(f"  {k}: {v}")
        print("Threads:")
        for k, v in contract.get('threads', {}).items():
            print(f"  {k}: {v}")
        print("Build:")
        for k, v in contract.get('build', {}).items():
            print(f"  {k}: {v}")
