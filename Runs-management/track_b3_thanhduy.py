import os
import sys
import json
import shutil
import zipfile
import builtins
from datetime import datetime, timezone

if hasattr(sys.stdout, 'reconfigure'):
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

slug = 'thanhduy9a4tv/grace-b3-validation'
out_dir = 'Runs-management/output_b3_thanhduy'
os.makedirs(out_dir, exist_ok=True)

now_str = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
print(f"[{now_str}] Checking Kaggle B3 run...")

status = api.kernels_status(slug)
st_val = str(getattr(status, 'status', status))
failure_msg = getattr(status, 'failure_message', '') or ''
print(f"B3 (thanhduy9a4tv) Status: {st_val} {failure_msg}")

if 'COMPLETE' in st_val.upper():
    print(f"Kernel completed! Downloading B3 outputs to {out_dir}...")
    api.kernels_output(slug, path=out_dir)

    for fname in os.listdir(out_dir):
        if fname.endswith('.zip') and 'checkpoint' in fname:
            zip_path = os.path.join(out_dir, fname)
            print(f"Unpacking checkpoint {zip_path}...")
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(out_dir)

    base_results = out_dir
    # Check both B3 and B3-nodiff
    for arm in ['B3', 'B3-nodiff']:
        seed = 42
        for ds in ['devign', 'reveal']:
            src = os.path.join(base_results, arm, f'seed_{seed}', ds, 'validation')
            dst = os.path.join('runs', 'final', ds, 'validation', arm, str(seed))
            if os.path.exists(src):
                os.makedirs(dst, exist_ok=True)
                for f in ['evaluation.json', 'records.jsonl', 'run_manifest.json']:
                    sf = os.path.join(src, f)
                    df = os.path.join(dst, f)
                    if os.path.exists(sf):
                        shutil.copy2(sf, df)
                        print(f"Ingested {sf} -> {df}")
                eval_file = os.path.join(dst, 'evaluation.json')
                if os.path.exists(eval_file):
                    with open(eval_file, 'r', encoding='utf-8') as ef:
                        metrics = json.load(ef)
                    print(f"  [{arm} - {ds}] AUROC: {metrics.get('auroc'):.4f}, MCC: {metrics.get('mcc'):.4f}, BA: {metrics.get('balanced_accuracy'):.4f}")

# Also check huuhieu3333 prepare notebook
try:
    os.environ['KAGGLE_USERNAME'] = 'huuhieu3333'
    os.environ['KAGGLE_KEY'] = 'KGAT_00cce839fd4e42e96de63ac19f06f316'
    os.environ['KAGGLE_API_TOKEN'] = 'KGAT_00cce839fd4e42e96de63ac19f06f316'
    api_hieu = KaggleApi()
    api_hieu.authenticate()
    st_hieu = api_hieu.kernels_status('huuhieu3333/qwen3coder30b-prepare-notebook')
    print(f"huuhieu3333/qwen3coder30b-prepare-notebook Status: {getattr(st_hieu, 'status', st_hieu)}")
except Exception as e:
    print(f"Could not check huuhieu3333: {e}")
