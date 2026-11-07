import builtins
import os
import sys
from pathlib import Path

# Monkeypatch builtins.open to force UTF-8 on Windows for Kaggle CLI/SDK
orig_open = builtins.open


def utf8_open(file, *args, **kwargs):
  if len(args) > 0 and 'b' in args[0]:
    return orig_open(file, *args, **kwargs)
  if 'mode' in kwargs and 'b' in kwargs['mode']:
    return orig_open(file, *args, **kwargs)
  if 'encoding' not in kwargs:
    kwargs['encoding'] = 'utf-8'
  return orig_open(file, *args, **kwargs)


builtins.open = utf8_open

sys.stdout.reconfigure(encoding='utf-8')

os.environ['KAGGLE_API_TOKEN'] = 'KGAT_107f196b3b616d0d60398c64eb11f2bd'
os.environ['KAGGLE_USERNAME'] = 'lznt123'
os.environ['KAGGLE_KEY'] = 'KGAT_107f196b3b616d0d60398c64eb11f2bd'

from kaggle.api.kaggle_api_extended import KaggleApi

api = KaggleApi()
api.authenticate()

staging_dir = str(
    Path('Runs-management/kaggle_staging_lznt123/b1_shuf_test_run').resolve()
)
print('Pushing kernel from staging dir:', staging_dir)

res = api.kernels_push(staging_dir)
print('kernels_push response:', res)

# Check status
status = api.kernels_status('lznt123/grace-b1-shuf-test')
print('Kernel status:', status)
