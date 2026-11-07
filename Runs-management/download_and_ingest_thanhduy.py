import os
import sys
import json
import shutil
import zipfile
import builtins

# UTF-8 stdout
sys.stdout.reconfigure(encoding='utf-8')

# Ensure builtins.open defaults to UTF-8
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

runs_to_check = [
    {
        'arm': 'B2-labelonly',
        'kernel': 'thanhduy9a4tv/grace-b2-labelonly-validation',
        'out_dir': 'Runs-management/output_b2_labelonly',
        'sub_folder': 'b2_labelonly_validation',
        'final_arm_dir': '11_Arm_B2_LabelOnly',
        'runs_final_name': 'B2-labelonly'
    },
    {
        'arm': 'B2-rep',
        'kernel': 'thanhduy9a4tv/grace-b2-rep-validation',
        'out_dir': 'Runs-management/output_b2_rep',
        'sub_folder': 'b2_rep_validation',
        'final_arm_dir': '05_Arm_B2_Rep',
        'runs_final_name': 'B2-rep'
    }
]

print("=== CHECKING THANHDUY9A4TV RUNS ===")
for r in runs_to_check:
    slug = r['kernel']
    arm = r['arm']
    status = api.kernels_status(slug)
    st_val = str(getattr(status, 'status', status))
    print(f"Arm: {arm} | Kernel: {slug} | Status: {st_val}")

    if 'COMPLETE' in st_val:
        out_dir = r['out_dir']
        os.makedirs(out_dir, exist_ok=True)
        print(f"Downloading output for {arm} to {out_dir}...")
        api.kernels_output(slug, path=out_dir)

        # Unpack checkpoint if present
        for fname in os.listdir(out_dir):
            if fname.endswith('.zip') and 'checkpoint' in fname:
                zip_path = os.path.join(out_dir, fname)
                print(f"Unpacking checkpoint {zip_path}...")
                with zipfile.ZipFile(zip_path, 'r') as zf:
                    zf.extractall(out_dir)

        # Ingest to runs/final/ and arm output directory
        sub_path = os.path.join(out_dir, r['sub_folder'], 'seed_42')
        if os.path.exists(sub_path):
            print(f"Found validation results in {sub_path}")
            for ds in ['devign', 'reveal']:
                src = os.path.join(sub_path, ds, 'validation')
                dst = os.path.join('runs', 'final', ds, 'validation', r['runs_final_name'], '42')
                if os.path.exists(src):
                    os.makedirs(dst, exist_ok=True)
                    for f in ['evaluation.json', 'records.jsonl', 'run_manifest.json']:
                        sf = os.path.join(src, f)
                        df = os.path.join(dst, f)
                        if os.path.exists(sf):
                            shutil.copy2(sf, df)
                            print(f"Copied {sf} -> {df}")
            
            # Copy to arm folder
            arm_out = os.path.join(r['final_arm_dir'], 'output')
            os.makedirs(arm_out, exist_ok=True)
            shutil.copytree(os.path.join(out_dir, r['sub_folder']), arm_out, dirs_exist_ok=True)
            print(f"Copied to {arm_out}")

print("=== CHECK FINISHED ===")
