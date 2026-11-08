import json
import os
import sys
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

configs = [
    {
        "user": "huuhieu3333",
        "token": "KGAT_00cce839fd4e42e96de63ac19f06f316",
        "runs": [
            ("grace-b1-full-test", Path("Runs-management/kaggle_staging_huuhieu3333/grace-b1-full-test_run")),
            ("grace-b2-rep-test", Path("Runs-management/kaggle_staging_huuhieu3333/grace-b2-rep-test_run"))
        ]
    },
    {
        "user": "tomandjerry223",
        "token": "c78b44e56259c2bb09962d5d1806ddf1",
        "runs": [
            ("grace-b2-labelonly-test", Path("Runs-management/kaggle_staging_tomandjerry223/grace-b2-labelonly-test_run")),
            ("grace-b2-nolabel-test", Path("Runs-management/kaggle_staging_tomandjerry223/grace-b2-nolabel-test_run"))
        ]
    },
    {
        "user": "lznt123",
        "token": "KGAT_107f196b3b616d0d60398c64eb11f2bd",
        "runs": [
            ("grace-b3-validation", Path("Runs-management/kaggle_staging_lznt123/b3_amended_test_run"))
        ]
    }
]

for cfg in configs:
    user = cfg["user"]
    token = cfg["token"]
    print(f"\n==================== Authenticating {user} ====================")
    if token.startswith("KGAT_"):
        os.environ["KAGGLE_API_TOKEN"] = token
    else:
        os.environ.pop("KAGGLE_API_TOKEN", None)
    os.environ["KAGGLE_USERNAME"] = user
    os.environ["KAGGLE_KEY"] = token
    
    api = KaggleApi()
    api.authenticate()
    
    for slug, stage_dir in cfg["runs"]:
        print(f"\n--- Pushing {user}/{slug} from {stage_dir} ---")
        meta_path = stage_dir / "kernel-metadata.json"
        print("Metadata:", meta_path.read_text(encoding="utf-8"))
        res = api.kernels_push(str(stage_dir))
        print("Push result:", res)
        time.sleep(3)
        st = api.kernels_status(f"{user}/{slug}")
        print(f"Status for {user}/{slug}:", st)

print("\nAll rebuilt kernels pushed to Kaggle successfully!")
