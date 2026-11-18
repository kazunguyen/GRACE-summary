"""Clean-environment run of REPRODUCTION_RUNBOOK.md part A, with full command logging.

python -I run_clean_env.py <package root> <base python 3.10.11> <evidence dir> <tools dir>
"""
import datetime as dt
import hashlib
import json
import os
import platform
import subprocess
import sys
from pathlib import Path

PKG, BASEPY, EV, TOOLS = (Path(a).resolve() for a in sys.argv[1:5])
LOG = EV / 'logs'
LOG.mkdir(parents=True, exist_ok=True)
OUTREL = 'runs/reproduced_20261118_py31011'
VENV = PKG / '.venv-repro'
VPY = VENV / 'Scripts' / 'python.exe'

# Environment: drop variables that could leak user/system packages into the run.
ENV = {k: v for k, v in os.environ.items() if not k.upper().startswith(('PYTHON', 'PIP_', 'CONDA', 'VIRTUAL_ENV'))}
ENV['PYTHONIOENCODING'] = 'utf-8'
ENV['PYTHONNOUSERSITE'] = '1'
idx = [0]


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def run(name, argv, cwd=PKG, check=True):
    idx[0] += 1
    stem = f'{idx[0]:02d}_{name}'
    t0 = now()
    p = subprocess.run([str(a) for a in argv], cwd=str(cwd), env=ENV, capture_output=True)
    t1 = now()
    (LOG / f'{stem}.stdout.txt').write_bytes(p.stdout)
    (LOG / f'{stem}.stderr.txt').write_bytes(p.stderr)
    rec = {'step': stem, 'cwd': str(cwd).replace(str(PKG), '<PKG>'),
           'argv': [str(a).replace(str(PKG), '<PKG>').replace(str(TOOLS), '<TOOLS>').replace(str(EV), '<EV>') for a in argv],
           'started_utc': t0, 'finished_utc': t1, 'exit_code': p.returncode,
           'stdout_sha256': hashlib.sha256(p.stdout).hexdigest(), 'stderr_sha256': hashlib.sha256(p.stderr).hexdigest()}
    with open(EV / 'commands.jsonl', 'a', encoding='utf-8') as f:
        f.write(json.dumps(rec, ensure_ascii=False) + '\n')
    print(f'[{stem}] exit={p.returncode} {t0} -> {t1}', flush=True)
    if check and p.returncode != 0:
        raise SystemExit(f'{stem} failed; see logs')
    return p


if (EV / 'commands.jsonl').exists():
    raise SystemExit('evidence dir already has commands.jsonl; use a new dir')

# 0. host + base interpreter
run('host_platform', [BASEPY, '-I', '-c', 'import platform,sys;print(sys.version);print(sys.executable);print(platform.platform());print(platform.machine());print(platform.processor())'])
run('base_python_version', [BASEPY, '-I', '-VV'])
run('windows_ver', ['cmd', '/c', 'ver'])

# 1. integrity of the extracted package subset against MANIFEST_SHA256.json
run('verify_extracted_against_manifest', [BASEPY, '-I', TOOLS / 'verify_manifest.py', PKG, EV / 'manifest_check.json'])

# 2. runbook A: venv + installs (Activate.ps1 replaced by calling the venv interpreter directly)
if VENV.exists():
    raise SystemExit('.venv-repro already exists')
run('venv_create', [BASEPY, '-I', '-m', 'venv', '.venv-repro'])
run('venv_cfg', ['cmd', '/c', 'type', r'.venv-repro\pyvenv.cfg'])
run('venv_python_version', [VPY, '-VV'])
run('venv_site_check', [VPY, '-c', 'import sys,site;print(sys.prefix);print(sys.base_prefix);print(site.ENABLE_USER_SITE);print(sys.path)'])
run('pip_freeze_empty_venv', [VPY, '-m', 'pip', 'freeze', '--all'])
run('pip_upgrade', [VPY, '-m', 'pip', 'install', '--upgrade', 'pip'])
run('pip_install_kit', [VPY, '-m', 'pip', 'install', '-e', r'.\grace_diag_kit'])
run('pip_install_matplotlib_pytest', [VPY, '-m', 'pip', 'install', 'matplotlib', 'pytest'])
run('pip_freeze_after_install', [VPY, '-m', 'pip', 'freeze', '--all'])
run('pip_list_json', [VPY, '-m', 'pip', 'list', '--format', 'json'])
run('pip_check', [VPY, '-m', 'pip', 'check'], check=False)

# 3. kit tests
run('pytest_kit', [VPY, '-m', 'pytest', r'.\grace_diag_kit\tests', '-v', '-p', 'no:cacheprovider'])

# 4. table rebuilds (5,000 bootstrap draws each, per protocol)
for name, thr in (('tables_prereg', r'configs\thresholds.prereg.json'), ('tables_corrected', r'configs\thresholds_corrected.json')):
    out = PKG / OUTREL / name
    if out.exists():
        raise SystemExit(f'{out} exists')
    run(f'rebuild_{name}', [VPY, r'.\analysis\analysis_code\evaluate_final_cached_bootstrap.py',
                            '--protocol', r'configs\protocol.yaml', '--thresholds', thr, '--out', rf'.\{OUTREL}\{name}'.replace('/', '\\')])

# 5. comparison with the archived tables (bytes + PNG pixels)
run('compare_tables', [VPY, TOOLS / 'compare_tables.py', PKG / 'runs/tables', PKG / OUTREL, EV / 'table_comparison.csv'])
print('done')
