import os
import json
import sys
import time
from pathlib import Path

# Ensure UTF-8 decoding for notebook json reading on Windows
os.environ['PYTHONUTF8'] = '1'
os.environ['KAGGLE_USERNAME'] = 'thanhduy9a4tv'
os.environ['KAGGLE_KEY'] = 'KGAT_47e27c5341b3301eea2f4e8f3d4743d6'
os.environ['KAGGLE_API_TOKEN'] = 'KGAT_47e27c5341b3301eea2f4e8f3d4743d6'

from kaggle.api.kaggle_api_extended import KaggleApi

api = KaggleApi()
api.authenticate()

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

prep_status = api.kernels_status('thanhduy9a4tv/qwen3coder30b-prepare-notebook')
status_val = str(getattr(prep_status, 'status', prep_status))
print(f'Model Prepare Notebook Status: {status_val}', flush=True)

if 'COMPLETE' not in status_val.upper():
    print('Prepare notebook is still downloading/running. Waiting for COMPLETE status.', flush=True)
    sys.exit(1)

# Check B2-labelonly status
st_label = api.kernels_status('thanhduy9a4tv/grace-b2-labelonly-validation')
print(f'B2-labelonly status: {st_label}', flush=True)

# Now retry pushing B2-rep until the previous batch GPU session frees up
max_retries = 20
delay_sec = 20
pushed = False

for attempt in range(1, max_retries + 1):
    print(f'[{time.strftime("%H:%M:%S")}] Attempt {attempt}/{max_retries}: Pushing B2-rep...', flush=True)
    res_rep = api.kernels_push('05_Arm_B2_Rep/notebooks')
    print('B2-rep push result:', res_rep, flush=True)
    err = getattr(res_rep, 'error', '') or (res_rep.get('error') if isinstance(res_rep, dict) else '')
    if not err:
        print('SUCCESS: B2-rep has been successfully queued/started!', flush=True)
        pushed = True
        break
    if 'maximum batch gpu session count' in err.lower():
        print(f'Waiting {delay_sec}s for batch GPU session slot to be released by Kaggle cluster...', flush=True)
        time.sleep(delay_sec)
    else:
        print(f'Encountered unexpected error: {err}', flush=True)
        time.sleep(delay_sec)

if pushed:
    time.sleep(5)
    st_rep = api.kernels_status('thanhduy9a4tv/grace-b2-rep-validation')
    print(f'B2-rep confirmed status: {st_rep}', flush=True)
else:
    print('WARNING: B2-rep could not be pushed within retry limit.', flush=True)
