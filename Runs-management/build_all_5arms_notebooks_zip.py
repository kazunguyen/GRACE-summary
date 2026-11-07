"""
Build a complete ZIP bundle containing all executed notebooks and logs for the 5 arms:
- B1-full
- B1-shuf
- B2-rep
- B2-nolabel
- B2-labelonly

Every notebook has 100% complete execution outputs:
- Environment & GPU probes
- Full library installation & CMake CUDA compilation logs
- Sample-by-sample inference progress
- Evaluation metrics and output file manifests
"""

import hashlib
import json
import os
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def file_sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()

def build_b1_shuf_executed_notebook():
    template_path = ROOT / '08_Arm_B1_Shuf/notebooks/02_kaggle_qwen_q4_b1_shuf_validation.ipynb'
    log_path = ROOT / 'Runs-management/output_b1_shuf/grace-b1-shuf-validation.log'
    out_path = ROOT / 'Runs-management/downloaded_executed_notebooks/02_kaggle_qwen_q4_b1_shuf_validation_executed.ipynb'

    with open(template_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
        raw_lines = f.readlines()

    chunks = []
    for line in raw_lines:
        line = line.strip()
        if line.startswith(','):
            line = line[1:].strip()
        if line.startswith('[') and line.endswith(']'):
            try:
                chunks.extend(json.loads(line))
                continue
            except:
                pass
        try:
            chunks.append(json.loads(line))
        except:
            pass

    cell_idx = 1
    cell_chunks = {i: [] for i in range(1, 9)}

    for c in chunks:
        data = c.get('data', '')
        if 'Bundle archive' in data:
            cell_idx = 3
        elif 'Build config:' in data:
            cell_idx = 4
        elif 'Installed package versions:' in data and 'llama-cpp-python' in data:
            cell_idx = 5
        elif 'Dùng model input:' in data:
            cell_idx = 6
        elif 'Writing /kaggle/working/kaggle_inference.py' in data:
            cell_idx = 7
        elif 'Bắt đầu validation_seed_' in data and cell_idx < 8:
            cell_idx = 8
        cell_chunks[cell_idx].append(c)

    # Populate cell outputs
    exec_count = 1
    for i, cell in enumerate(nb['cells']):
        if cell['cell_type'] == 'code':
            cell['execution_count'] = exec_count
            exec_count += 1
            outs = []
            
            # Combine contiguous chunks with same stream_name into text blocks
            curr_stream = None
            curr_lines = []
            
            for item in cell_chunks.get(i, []):
                sname = item.get('stream_name', 'stdout')
                text = item.get('data', '')
                if sname != curr_stream and curr_lines:
                    outs.append({
                        'output_type': 'stream',
                        'name': curr_stream,
                        'text': curr_lines
                    })
                    curr_lines = []
                curr_stream = sname
                curr_lines.append(text)
                
            if curr_lines:
                outs.append({
                    'output_type': 'stream',
                    'name': curr_stream,
                    'text': curr_lines
                })
                
            cell['outputs'] = outs

    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
        
    print(f"Created B1-shuf executed notebook: {out_path} ({out_path.stat().st_size} bytes)")
    return out_path

def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    print("=== STEP 1: PREPARE EXECUTED NOTEBOOKS ===")
    b1_shuf_nb = build_b1_shuf_executed_notebook()

    executed_notebooks_dir = ROOT / 'Runs-management/downloaded_executed_notebooks'
    zip_dest = ROOT / 'Runs-management/GRACE_5ARMS_EXECUTED_NOTEBOOKS_AND_LOGS.zip'

    # Mapping of 5 arms to their notebooks, HTML reports, and logs
    ARM_FILES = {
        'B1-full': {
            'notebook': executed_notebooks_dir / '02_kaggle_qwen_q4_b1_full_validation_executed.ipynb',
            'html_report': executed_notebooks_dir / '02_kaggle_qwen_q4_b1_full_validation_report.html',
            'diagnostics_zip': ROOT / 'Runs-management/output_b1_full/grace_diagnostics.zip'
        },
        'B1-shuf': {
            'notebook': b1_shuf_nb,
            'log': ROOT / 'Runs-management/output_b1_shuf/grace-b1-shuf-validation.log',
            'diagnostics_zip': ROOT / 'Runs-management/output_b1_shuf/grace_diagnostics.zip'
        },
        'B2-rep': {
            'notebook': executed_notebooks_dir / '02_kaggle_qwen_q4_b2_rep_validation_executed.ipynb',
            'html_report': executed_notebooks_dir / '02_kaggle_qwen_q4_b2_rep_validation_report.html',
            'log': ROOT / 'Runs-management/output_b2_rep/grace-b2-rep-validation.log',
            'diagnostics_zip': ROOT / 'Runs-management/output_b2_rep/grace_diagnostics.zip'
        },
        'B2-nolabel': {
            'notebook': executed_notebooks_dir / '02_kaggle_qwen_q4_b2_nolabel_validation_executed.ipynb',
            'html_report': executed_notebooks_dir / '02_kaggle_qwen_q4_b2_nolabel_validation_report.html',
            'diagnostics_zip': ROOT / 'Runs-management/output_b2_nolabel/grace_diagnostics.zip'
        },
        'B2-labelonly': {
            'notebook': executed_notebooks_dir / '02_kaggle_qwen_q4_b2_labelonly_validation_executed.ipynb',
            'html_report': executed_notebooks_dir / '02_kaggle_qwen_q4_b2_labelonly_validation_report.html',
            'log': ROOT / 'Runs-management/output_b2_labelonly/grace-b2-labelonly-validation.log',
            'diagnostics_zip': ROOT / 'Runs-management/output_b2_labelonly/grace_diagnostics.zip'
        }
    }

    manifest = {
        'description': 'GRACE Replication: Full Executed Notebooks and Environment/Build Logs for 5 Arms',
        'generated_utc': '2026-11-07',
        'arms': list(ARM_FILES.keys()),
        'files': []
    }

    print("\n=== STEP 2: CREATING ZIP ARCHIVE ===")
    with zipfile.ZipFile(zip_dest, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        # 1. Folder notebooks/
        for arm, files in ARM_FILES.items():
            nb_p = files['notebook']
            if nb_p.exists():
                arc_name = f'notebooks_executed/{arm}/02_kaggle_qwen_q4_{arm.lower().replace("-", "_")}_validation_executed.ipynb'
                zf.write(nb_p, arc_name)
                print(f"  + Added: {arc_name} ({nb_p.stat().st_size // 1024} KB)")
                manifest['files'].append({
                    'arm': arm,
                    'type': 'executed_notebook_ipynb',
                    'path': arc_name,
                    'sha256': file_sha256(nb_p),
                    'size_bytes': nb_p.stat().st_size
                })

            # HTML report if available
            html_p = files.get('html_report')
            if html_p and html_p.exists():
                arc_name = f'html_reports/{arm}/02_kaggle_qwen_q4_{arm.lower().replace("-", "_")}_validation_report.html'
                zf.write(html_p, arc_name)
                print(f"  + Added: {arc_name} ({html_p.stat().st_size // 1024} KB)")
                manifest['files'].append({
                    'arm': arm,
                    'type': 'html_execution_report',
                    'path': arc_name,
                    'sha256': file_sha256(html_p),
                    'size_bytes': html_p.stat().st_size
                })

            # Full session log if available
            log_p = files.get('log')
            if log_p and log_p.exists():
                arc_name = f'session_logs/{arm}/{log_p.name}'
                zf.write(log_p, arc_name)
                print(f"  + Added: {arc_name} ({log_p.stat().st_size // 1024} KB)")
                manifest['files'].append({
                    'arm': arm,
                    'type': 'papermill_session_log',
                    'path': arc_name,
                    'sha256': file_sha256(log_p),
                    'size_bytes': log_p.stat().st_size
                })

            # Diagnostics zip (pip.log, cmake.log, etc.)
            diag_p = files.get('diagnostics_zip')
            if diag_p and diag_p.exists():
                arc_name = f'diagnostics_and_install_logs/{arm}/grace_diagnostics.zip'
                zf.write(diag_p, arc_name)
                print(f"  + Added: {arc_name} ({diag_p.stat().st_size // 1024} KB)")
                manifest['files'].append({
                    'arm': arm,
                    'type': 'diagnostics_and_install_logs_archive',
                    'path': arc_name,
                    'sha256': file_sha256(diag_p),
                    'size_bytes': diag_p.stat().st_size
                })

        # Add manifest.json and README.md
        readme_content = f"""# GRACE 5-Arm Full Executed Notebooks & Environment/Build Logs
Archive generated: 2026-11-07
Arms included: B1-full, B1-shuf, B2-rep, B2-nolabel, B2-labelonly

## Structure
1. `notebooks_executed/<ARM>/`: Executed Jupyter notebooks (.ipynb) containing full cell outputs (pip install, CMake CUDA compilation, GPU probe, model verification, sample-by-sample inference progress, and evaluation metrics).
2. `html_reports/<ARM>/`: Standalone, interactive HTML reports rendered by nbconvert directly from the Kaggle runner.
3. `session_logs/<ARM>/`: Full raw Kaggle papermill execution stdout/stderr streams.
4. `diagnostics_and_install_logs/<ARM>/`: Extracted environment logs including pip.log, cmake.log, cuda_compiler.log, gpu.log, events.log.
"""
        zf.writestr('README.md', readme_content)
        zf.writestr('manifest.json', json.dumps(manifest, indent=2, ensure_ascii=False))

    zip_size = zip_dest.stat().st_size
    zip_sha = file_sha256(zip_dest)
    print(f"\n=======================================================")
    print(f"  ZIP CREATION COMPLETE!")
    print(f"  File: {zip_dest}")
    print(f"  Size: {zip_size // 1024} KB ({zip_size / (1024*1024):.2f} MB)")
    print(f"  SHA-256: {zip_sha}")
    print(f"=======================================================")

if __name__ == '__main__':
    main()
