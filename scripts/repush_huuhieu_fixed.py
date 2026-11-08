import os
import sys
import json
import time
from pathlib import Path
import builtins

# Monkey-patch builtins.open to use utf-8 by default on Windows
_orig_open = builtins.open
def _utf8_open(file, *args, **kwargs):
    mode = args[0] if args else kwargs.get('mode', 'r')
    if 'b' not in mode and 'encoding' not in kwargs:
        kwargs['encoding'] = 'utf-8'
    return _orig_open(file, *args, **kwargs)
builtins.open = _utf8_open

from kaggle.api.kaggle_api_extended import KaggleApi

user = "huuhieu3333"
token = "KGAT_00cce839fd4e42e96de63ac19f06f316"
os.environ["KAGGLE_API_TOKEN"] = token
os.environ["KAGGLE_USERNAME"] = user
os.environ["KAGGLE_KEY"] = token

api = KaggleApi()
api.authenticate()

runs = [
    ("grace-b2-rep-test", Path("Runs-management/kaggle_staging_huuhieu3333/grace-b2-rep-test_run")),
    ("grace-b1-full-test", Path("Runs-management/kaggle_staging_huuhieu3333/grace-b1-full-test_run"))
]

for slug, stage_dir in runs:
    print(f"\n==================== Pushing {user}/{slug} ====================")
    meta_path = stage_dir / "kernel-metadata.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    
    # Ensure kernel_sources is correct
    meta["kernel_sources"] = ["huuhieu3333/qwen3coder30b-prepare-notebook"]
    meta["dataset_sources"] = [f"huuhieu3333/{slug}-inputs"]
    meta["enable_gpu"] = True
    meta["enable_internet"] = True
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    
    print(f"Metadata verified:\n{meta_path.read_text(encoding='utf-8')}")
    
    # Push kernel
    res = api.kernels_push(str(stage_dir))
    print(f"Push response for {slug}:", res)
    
    # Wait 5 seconds and check status
    time.sleep(5)
    st = api.kernels_status(f"{user}/{slug}")
    print(f"Status for {slug}: {st}")
    
    # Verify metadata saved on Kaggle
    check_dir = Path(f"Runs-management/verify_push_{slug}")
    check_dir.mkdir(parents=True, exist_ok=True)
    api.kernels_pull(f"{user}/{slug}", path=str(check_dir), metadata=True)
    pulled_meta = json.loads((check_dir / "kernel-metadata.json").read_text(encoding="utf-8"))
    print(f"Kaggle saved kernel_sources: {pulled_meta.get('kernel_sources')}")
    assert pulled_meta.get("kernel_sources") == ["huuhieu3333/qwen3coder30b-prepare-notebook"], f"Kaggle failed to attach prepare notebook for {slug}!"
    print(f"SUCCESS: {slug} verified on Kaggle with correct model kernel source!")
