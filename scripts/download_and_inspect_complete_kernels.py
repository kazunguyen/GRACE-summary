import builtins
import json
import os
import sys
from pathlib import Path

# Monkeypatch builtins.open to force UTF-8 on Windows for Kaggle CLI/SDK
orig_open = builtins.open


def utf8_open(file, mode='r', *args, **kwargs):
  if 'b' not in mode and 'encoding' not in kwargs:
    kwargs['encoding'] = 'utf-8'
  return orig_open(file, mode, *args, **kwargs)


builtins.open = utf8_open

sys.stdout.reconfigure(encoding='utf-8')

from kaggle.api.kaggle_api_extended import KaggleApi

# 1. Download B2-labelonly complete output
print('=== 1. Downloading B2-labelonly Complete Output ===')
os.environ['KAGGLE_USERNAME'] = 'tomandjerry223'
os.environ['KAGGLE_KEY'] = 'c78b44e56259c2bb09962d5d1806ddf1'
os.environ.pop('KAGGLE_API_TOKEN', None)
api_tom = KaggleApi()
api_tom.authenticate()

out_dir_b2_labelonly = Path('Runs-management/output_b2_labelonly_test_complete')
out_dir_b2_labelonly.mkdir(parents=True, exist_ok=True)
api_tom.kernels_output(
    'tomandjerry223/grace-b2-labelonly-test', path=str(out_dir_b2_labelonly)
)
print('Downloaded files for B2-labelonly:')
for p in out_dir_b2_labelonly.glob('*'):
  print(f'  -> {p.name} ({p.stat().st_size} bytes)')

# 2. Download B1-shuf error log on lznt123
print('\n=== 2. Downloading B1-shuf Error Log on lznt123 ===')
os.environ['KAGGLE_API_TOKEN'] = 'KGAT_107f196b3b616d0d60398c64eb11f2bd'
os.environ['KAGGLE_USERNAME'] = 'lznt123'
os.environ['KAGGLE_KEY'] = 'KGAT_107f196b3b616d0d60398c64eb11f2bd'
api_lznt = KaggleApi()
api_lznt.authenticate()

out_dir_b1_shuf_err = Path('Runs-management/err_lznt123_b1_shuf_test')
out_dir_b1_shuf_err.mkdir(parents=True, exist_ok=True)
try:
  api_lznt.kernels_output(
      'lznt123/grace-b1-shuf-test', path=str(out_dir_b1_shuf_err)
  )
  print('Downloaded files for B1-shuf error:')
  for p in out_dir_b1_shuf_err.glob('*'):
    print(f'  -> {p.name} ({p.stat().st_size} bytes)')
except Exception as e:
  print('Error downloading B1-shuf output:', e)
