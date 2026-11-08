import os
import sys
import tempfile
import json
from kaggle.api.kaggle_api_extended import KaggleApi

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

users = [
    ('huuhieu3333', 'KGAT_00cce839fd4e42e96de63ac19f06f316', 'grace-b1-full-test'),
    ('huuhieu3333', 'KGAT_00cce839fd4e42e96de63ac19f06f316', 'grace-b2-rep-test'),
    ('tomandjerry223', 'c78b44e56259c2bb09962d5d1806ddf1', 'grace-b2-labelonly-test'),
    ('tomandjerry223', 'c78b44e56259c2bb09962d5d1806ddf1', 'grace-b2-nolabel-test'),
    ('lznt123', 'KGAT_107f196b3b616d0d60398c64eb11f2bd', 'grace-b3-validation'),
]

for user, token, slug in users:
    if token.startswith('KGAT_'):
        os.environ['KAGGLE_API_TOKEN'] = token
    else:
        os.environ.pop('KAGGLE_API_TOKEN', None)
    os.environ['KAGGLE_USERNAME'] = user
    os.environ['KAGGLE_KEY'] = token
    api = KaggleApi()
    api.authenticate()
    temp_dir = tempfile.mkdtemp()
    try:
        api.kernels_pull(f'{user}/{slug}', path=temp_dir)
        files = os.listdir(temp_dir)
        print(f'=== {user}/{slug} pulled files: {files} ===')
        meta_file = os.path.join(temp_dir, 'kernel-metadata.json')
        if os.path.exists(meta_file):
            with open(meta_file, 'r', encoding='utf-8') as fh:
                print('  Metadata:', fh.read().strip())
        for f in files:
            if f.endswith('.ipynb'):
                with open(os.path.join(temp_dir, f), 'r', encoding='utf-8') as fh:
                    nb = json.load(fh)
                    print(f"  Notebook {f}: {len(nb['cells'])} cells")
                    print('  Cell 0:', repr(''.join(nb['cells'][0]['source'])[:100]))
                    if len(nb['cells']) > 6:
                        print('  Cell 6:', repr(''.join(nb['cells'][6]['source'])[:120]))
    except Exception as e:
        print(f'=== {user}/{slug}: {e} ===')
