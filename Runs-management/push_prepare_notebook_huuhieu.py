import os
import json
from pathlib import Path
from kaggle.api.kaggle_api_extended import KaggleApi

os.environ['KAGGLE_USERNAME'] = 'huuhieu3333'
os.environ['KAGGLE_KEY'] = 'KGAT_00cce839fd4e42e96de63ac19f06f316'
os.environ['KAGGLE_API_TOKEN'] = 'KGAT_00cce839fd4e42e96de63ac19f06f316'

api = KaggleApi()
api.authenticate()

prep_dir = Path('Runs-management/kaggle_prepare_notebook_huuhieu')
prep_dir.mkdir(parents=True, exist_ok=True)

meta = {
    'id': 'huuhieu3333/qwen3coder30b-prepare-notebook',
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
print(path)
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

res = api.kernels_push(str(prep_dir))
print('Push prepare notebook result on huuhieu3333:', res)
