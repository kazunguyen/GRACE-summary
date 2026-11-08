import zipfile
import json
import sys
import difflib

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

zip_path = r'Runs-management/grace_hieu_5arms_runtime_locked_20261107.zip'
with zipfile.ZipFile(zip_path) as z:
    for name in z.namelist():
        arm = name.replace('02_kaggle_qwen_q4_', '').replace('_validation_runtime_locked.ipynb', '')
        nb_lock = json.loads(z.read(name).decode('utf-8'))
        exec_path = f'Runs-management/downloaded_executed_notebooks/02_kaggle_qwen_q4_{arm}_validation_executed.ipynb'
        with open(exec_path, 'r', encoding='utf-8') as f:
            nb_exec = json.load(f)
            
        print(f"==================== ARM: {arm} ====================")
        print(f"Lock cells: {len(nb_lock['cells'])}, Exec cells: {len(nb_exec['cells'])}")
        for idx in range(len(nb_lock['cells'])):
            c_lock = "".join(nb_lock['cells'][idx].get('source', []))
            c_exec = "".join(nb_exec['cells'][idx].get('source', []))
            if c_lock.strip() != c_exec.strip():
                print(f"--- Cell {idx} differs (Lock {len(c_lock)} chars vs Exec {len(c_exec)} chars) ---")
                lines_lock = c_lock.splitlines()
                lines_exec = c_exec.splitlines()
                diff = list(difflib.unified_diff(lines_exec, lines_lock, lineterm='', n=1))
                for line in diff[:10]:
                    print(" ", line)
                if len(diff) > 10:
                    print(f"  ... ({len(diff)-10} more diff lines)")
            else:
                print(f"    Cell {idx} identical")
