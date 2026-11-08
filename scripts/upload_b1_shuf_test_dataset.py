import os
import sys
from pathlib import Path
from kaggle.api.kaggle_api_extended import KaggleApi

sys.stdout.reconfigure(encoding='utf-8')

user = 'lznt123'
token = 'KGAT_107f196b3b616d0d60398c64eb11f2bd'
os.environ['KAGGLE_API_TOKEN'] = token
os.environ['KAGGLE_USERNAME'] = user
os.environ['KAGGLE_KEY'] = token

api = KaggleApi()
api.authenticate()

upload_dir = str(Path('08_Arm_B1_Shuf/kaggle_dataset_upload').resolve())
print('Uploading dataset from:', upload_dir)

try:
    api.dataset_create_new(upload_dir, public=False, quiet=False)
    print('SUCCESS: Dataset created on Kaggle (lznt123/grace-b1-shuf-test-inputs)!')
except Exception as e:
    print('dataset_create_new notification:', e)
    if 'already exists' in str(e).lower() or '409' in str(e) or 'conflict' in str(e).lower():
        print('Dataset exists, creating new version...')
        api.dataset_create_version(
            upload_dir, version_notes='Initial upload of B1-shuf test prompts', quiet=False
        )
        print('SUCCESS: Dataset version created!')
    else:
        raise
