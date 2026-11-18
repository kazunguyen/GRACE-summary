"""Step 20: rerun the comparison with archive-only run notes classified (step 19 log kept as is)."""
import datetime as dt, hashlib, json, os, subprocess, sys
from pathlib import Path
PKG, EV, TOOLS = (Path(a).resolve() for a in sys.argv[1:4])
VPY = PKG / '.venv-repro' / 'Scripts' / 'python.exe'
argv = [VPY, TOOLS / 'compare_tables.py', PKG / 'runs/tables', PKG / 'runs/reproduced_20261118_py31011', EV / 'table_comparison.csv']
env = {k: v for k, v in os.environ.items() if not k.upper().startswith(('PYTHON', 'PIP_', 'CONDA', 'VIRTUAL_ENV'))}
env['PYTHONIOENCODING'] = 'utf-8'; env['PYTHONNOUSERSITE'] = '1'
t0 = dt.datetime.now(dt.timezone.utc).isoformat()
p = subprocess.run([str(a) for a in argv], cwd=str(PKG), env=env, capture_output=True)
t1 = dt.datetime.now(dt.timezone.utc).isoformat()
stem = '20_compare_tables_classified'
(EV / 'logs' / f'{stem}.stdout.txt').write_bytes(p.stdout); (EV / 'logs' / f'{stem}.stderr.txt').write_bytes(p.stderr)
rec = {'step': stem, 'cwd': '<PKG>', 'argv': [str(a).replace(str(PKG), '<PKG>').replace(str(TOOLS), '<TOOLS>').replace(str(EV), '<EV>') for a in argv],
       'started_utc': t0, 'finished_utc': t1, 'exit_code': p.returncode,
       'stdout_sha256': hashlib.sha256(p.stdout).hexdigest(), 'stderr_sha256': hashlib.sha256(p.stderr).hexdigest(),
       'note': 'step 19 flagged archive-only README.md/*.log as DIFF; compare_tables.py now classifies them as run notes'}
open(EV / 'commands.jsonl', 'a', encoding='utf-8').write(json.dumps(rec, ensure_ascii=False) + '\n')
print(p.stdout.decode('utf-8'), p.stderr.decode('utf-8'), 'exit', p.returncode)
