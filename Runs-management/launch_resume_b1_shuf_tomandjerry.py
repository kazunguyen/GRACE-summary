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

def main():
    root = Path(__file__).resolve().parent.parent
    user = 'tomandjerry223'

    for k in ['KAGGLE_USERNAME', 'KAGGLE_KEY', 'KAGGLE_API_TOKEN', 'KAGGLE_CONFIG_DIR']:
        if k in os.environ:
            del os.environ[k]

    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    api.authenticate()
    print(f'Authenticated successfully as {user}!')

    staging = root / 'Runs-management/kaggle_staging_tomandjerry/b1_shuf_resume_run'
    slug = f'{user}/grace-b1-shuf-validation'

    print(f'Pushing B1-shuf resume kernel from {staging}...')
    os.chdir(staging)
    res_k = api.kernels_push(str(staging))
    print('Kernels push response:', res_k)

    print('Waiting 5s for kernel queue...')
    time.sleep(5)
    st = api.kernels_status(slug)
    print(f'{slug} status: {getattr(st, "status", st)}')

if __name__ == '__main__':
    main()
