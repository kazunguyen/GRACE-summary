import os
import sys
import json
import shutil
import zipfile
import builtins

sys.stdout.reconfigure(encoding='utf-8')

orig_open = builtins.open
def utf8_open(file, mode='r', *args, **kwargs):
    if 'b' not in mode and 'encoding' not in kwargs:
        kwargs['encoding'] = 'utf-8'
    return orig_open(file, mode, *args, **kwargs)
builtins.open = utf8_open

os.environ['KAGGLE_USERNAME'] = 'thanhduy9a4tv'
os.environ['KAGGLE_KEY'] = 'KGAT_47e27c5341b3301eea2f4e8f3d4743d6'
os.environ['KAGGLE_API_TOKEN'] = 'KGAT_47e27c5341b3301eea2f4e8f3d4743d6'

from kaggle.api.kaggle_api_extended import KaggleApi
api = KaggleApi()
api.authenticate()

slug = 'thanhduy9a4tv/grace-b1-shuf-validation'
out_dir = 'Runs-management/output_b1_shuf_thanhduy'
os.makedirs(out_dir, exist_ok=True)

status = api.kernels_status(slug)
st_val = str(getattr(status, 'status', status))
print(f"B1-shuf (thanhduy9a4tv) status: {st_val}")

if 'COMPLETE' in st_val.upper():
    print(f"Downloading B1-shuf output to {out_dir}...")
    api.kernels_output(slug, path=out_dir)

    for fname in os.listdir(out_dir):
        if fname.endswith('.zip') and 'checkpoint' in fname:
            zip_path = os.path.join(out_dir, fname)
            print(f"Unpacking checkpoint {zip_path}...")
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(out_dir)

    # Ingest for each seed (42, 43, 44)
    base_results = os.path.join(out_dir, 'b1_shuf_validation')
    if os.path.exists(base_results):
        for seed in [42, 43, 44]:
            sub_path = os.path.join(base_results, f'seed_{seed}')
            if os.path.exists(sub_path):
                for ds in ['devign', 'reveal']:
                    src = os.path.join(sub_path, ds, 'validation')
                    dst = os.path.join('runs', 'final', ds, 'validation', 'B1-shuf', str(seed))
                    if os.path.exists(src):
                        os.makedirs(dst, exist_ok=True)
                        for f in ['evaluation.json', 'records.jsonl', 'run_manifest.json']:
                            sf = os.path.join(src, f)
                            df = os.path.join(dst, f)
                            if os.path.exists(sf):
                                shutil.copy2(sf, df)
                                print(f"Copied {sf} -> {df}")
