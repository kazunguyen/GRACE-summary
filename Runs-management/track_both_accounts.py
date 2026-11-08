import os
import sys
from datetime import datetime, timezone

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

def check():
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{now_str}] Checking Kaggle Runs Across Accounts...")

    # 1. Check B3 on lznt123
    try:
        os.environ['KAGGLE_USERNAME'] = 'lznt123'
        os.environ['KAGGLE_KEY'] = 'KGAT_107f196b3b616d0d60398c64eb11f2bd'
        os.environ['KAGGLE_API_TOKEN'] = 'KGAT_107f196b3b616d0d60398c64eb11f2bd'
        from kaggle.api.kaggle_api_extended import KaggleApi
        api_lznt = KaggleApi()
        api_lznt.authenticate()
        st_b3 = api_lznt.kernels_status('lznt123/grace-b3-validation')
        print(f"B3 (lznt123) Status: {getattr(st_b3, 'status', st_b3)}")
    except Exception as e:
        print(f"B3 (lznt123) Status check failed: {e}")

    # 2. Check B1-shuf on tomandjerry223
    try:
        for k in ['KAGGLE_USERNAME', 'KAGGLE_KEY', 'KAGGLE_API_TOKEN', 'KAGGLE_CONFIG_DIR']:
            if k in os.environ:
                del os.environ[k]
        from kaggle.api.kaggle_api_extended import KaggleApi
        api_tj = KaggleApi()
        api_tj.authenticate()
        st_shuf = api_tj.kernels_status('tomandjerry223/grace-b1-shuf-validation')
        print(f"B1-shuf (tomandjerry223) Status: {getattr(st_shuf, 'status', st_shuf)}")
    except Exception as e:
        print(f"B1-shuf (tomandjerry223) Status check failed: {e}")

if __name__ == '__main__':
    check()
