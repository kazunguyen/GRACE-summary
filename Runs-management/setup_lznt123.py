import os
import sys
import json
import time
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import builtins
orig_open = builtins.open
def utf8_open(file, mode='r', *args, **kwargs):
    if 'b' not in mode and 'encoding' not in kwargs:
        kwargs['encoding'] = 'utf-8'
    return orig_open(file, mode, *args, **kwargs)
builtins.open = utf8_open

def main():
    username = 'lznt123'
    key = 'KGAT_107f196b3b616d0d60398c64eb11f2bd'

    root = Path(__file__).resolve().parent.parent
    config_dir = root / 'Runs-management/kaggle_lznt123_config'
    config_dir.mkdir(parents=True, exist_ok=True)
    cfg_file = config_dir / 'kaggle.json'
    cfg_file.write_text(json.dumps({'username': username, 'key': key}, indent=2), encoding='utf-8')
    print(f'Config written: {cfg_file}')

    os.environ['KAGGLE_USERNAME'] = username
    os.environ['KAGGLE_KEY'] = key
    os.environ['KAGGLE_API_TOKEN'] = key

    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    api.authenticate()
    print(f'Authenticated successfully as {username}!')

    # Check user existing kernels & datasets
    try:
        kernels = api.kernels_list(user=username)
        print(f'Existing kernels for {username}: {len(kernels)}')
        for k in kernels[:5]:
            print(f'  Kernel: {k.ref}')
    except Exception as e:
        print(f'Could not list kernels: {e}')

    try:
        datasets = api.dataset_list(user=username)
        print(f'Existing datasets for {username}: {len(datasets)}')
        for d in datasets[:5]:
            print(f'  Dataset: {d.ref}')
    except Exception as e:
        print(f'Could not list datasets: {e}')

    # Create & push model preparation notebook (CPU only, 0 GPU quota used)
    prep_dir = root / 'Runs-management/kaggle_prepare_notebook_lznt123'
    prep_dir.mkdir(parents=True, exist_ok=True)

    meta = {
        'id': f'{username}/qwen3coder30b-prepare-notebook',
        'title': 'qwen3coder30b-prepare-notebook',
        'code_file': 'qwen3coder30b_prepare.ipynb',
        'language': 'python',
        'kernel_type': 'notebook',
        'is_private': True,
        'enable_gpu': False,
        'enable_tpu': False,
        'enable_internet': True,
        'keywords': [],
        'dataset_sources': [],
        'kernel_sources': [],
        'competition_sources': [],
        'model_sources': []
    }
    (prep_dir / 'kernel-metadata.json').write_text(json.dumps(meta, indent=2), encoding='utf-8')

    code_text = """!pip -q install huggingface_hub

from huggingface_hub import hf_hub_download

path = hf_hub_download(
    repo_id="ggml-org/Qwen3-Coder-30B-A3B-Instruct-GGUF",
    filename="Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf",
    revision="0ca51122012fe4a20dc82988ee58780b008ce4e3",
    local_dir="/kaggle/working/qwen_gguf",
)
print("Cached model path:", path)
"""

    nb = {
        'cells': [
            {
                'cell_type': 'code',
                'execution_count': None,
                'metadata': {},
                'outputs': [],
                'source': code_text.splitlines(keepends=True)
            }
        ],
        'metadata': {
            'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
            'language_info': {'name': 'python'}
        },
        'nbformat': 4,
        'nbformat_minor': 4
    }
    (prep_dir / 'qwen3coder30b_prepare.ipynb').write_text(json.dumps(nb, indent=2), encoding='utf-8')

    print(f'Pushing prepare notebook {username}/qwen3coder30b-prepare-notebook...')
    res = api.kernels_push(str(prep_dir))
    print('Push result:', res)

    time.sleep(5)
    st = api.kernels_status(f'{username}/qwen3coder30b-prepare-notebook')
    print('Initial status:', st)

if __name__ == '__main__':
    main()
