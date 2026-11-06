"""Reproduce thresholds with the existing optimizer and an enforced read allowlist.

Run from any directory: python -B <path to this file>
This verifier does not change the existing optimizer or threshold locks.
"""
import hashlib
import json
import math
import os
import sys
import types
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OPTIMIZER = ROOT / 'Runs-management/validation_lock.py'
OUTPUT = HERE / 'validation_threshold_verification.json'
MODEL = 'f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335'
SOURCES = [
    ('B0', 'devign', 2732, ROOT / '02_Arm_B0_Source_Only/output/kaggle_20261101_duchuynguyen1802/grace_b0_runs/devign/validation/records.jsonl'),
    ('B0', 'reveal', 2273, ROOT / '02_Arm_B0_Source_Only/output/kaggle_20261101_duchuynguyen1802/grace_b0_runs/reveal/validation/records.jsonl'),
    ('B1', 'devign', 2732, ROOT / '03_Arm_B1_Graph_Only/output/kaggle_run_02/grace_b1_runs/devign/validation/records.jsonl'),
    ('B1', 'reveal', 2273, ROOT / '03_Arm_B1_Graph_Only/output/kaggle_run_02/grace_b1_runs/reveal/validation/records.jsonl'),
]


def normalized(path):
    return os.path.normcase(os.path.abspath(os.fspath(path)))


# Dependencies above are imported before the I/O audit. Below, only these exact
# source/input files may be opened for reading. No directory scan is performed.
ALLOWED_READS = {normalized(OPTIMIZER), normalized(__file__)}
ALLOWED_READS.update(normalized(p) for _, _, _, p in SOURCES)
read_events = []
blocked_events = []


def enforce_file_access(event, args):
    if event != 'open':
        return
    path, mode, flags = args
    if isinstance(path, int):
        blocked_events.append({'path': str(path), 'reason': 'file descriptor open'})
        raise PermissionError('Verifier does not permit opening file descriptors')
    resolved = normalized(path)
    writing = bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
    if writing:
        if resolved != normalized(OUTPUT):
            blocked_events.append({'path': resolved, 'reason': 'write outside evidence output'})
            raise PermissionError('Only the evidence JSON output may be written')
    else:
        if resolved not in ALLOWED_READS:
            blocked_events.append({'path': resolved, 'reason': 'read outside exact allowlist'})
            raise PermissionError('Read rejected outside exact validation/source allowlist: ' + resolved)
        read_events.append(resolved)


sys.addaudithook(enforce_file_access)

# Load the EXISTING module byte-for-byte; do not reimplement threshold fitting.
optimizer_bytes = OPTIMIZER.read_bytes()
verifier_bytes = Path(__file__).read_bytes()
optimizer = types.ModuleType('audited_original_validation_lock')
exec(compile(optimizer_bytes, str(OPTIMIZER), 'exec'), optimizer.__dict__)

results = []
for arm, dataset, count, path in SOURCES:
    raw = path.read_bytes()
    rows = [json.loads(line) for line in raw.decode('utf-8').splitlines() if line.strip()]
    if len(rows) != count or len({r['id'] for r in rows}) != count:
        raise ValueError('Wrong census or duplicate IDs: ' + str(path))
    for row in rows:
        if (row.get('arm'), row.get('dataset'), row.get('split')) != (arm, dataset, 'validation'):
            raise ValueError('Input is not exclusively the requested validation split')
        if row.get('model_sha256') != MODEL or row.get('seed') != 42:
            raise ValueError('Unexpected model or seed')
        if row.get('label') not in (0, 1):
            raise ValueError('Nonbinary label')
        if row.get('valid'):
            if not isinstance(row.get('s'), (float, int)) or not math.isfinite(row['s']) or not 0 <= row['s'] <= 1:
                raise ValueError('Invalid numeric score marked valid')
            z = row['logprob_1'] - row['logprob_0']
            sigmoid = 1 / (1 + math.exp(-z)) if z >= 0 else math.exp(z) / (1 + math.exp(z))
            if abs(sigmoid - row['s']) > 1e-10:
                raise ValueError('Score does not match binary logprobs')
    # Input to the original optimizer consists ONLY of the validation rows above.
    computed = optimizer.pick_threshold(sorted(rows, key=lambda r: str(r['id'])))
    results.append({
        'arm': arm, 'dataset': dataset, 'split': 'validation',
        'path': path.relative_to(ROOT).as_posix(),
        'records_sha256': hashlib.sha256(raw).hexdigest(),
        'n_rows': len(rows), **computed,
    })

# Expected values are checked AFTER all fits and are never passed to the optimizer.
expected = {('B0', 'devign'): 0.98, ('B0', 'reveal'): 0.30,
            ('B1', 'devign'): 0.98, ('B1', 'reveal'): 0.63}
for result in results:
    if abs(result['tau'] - expected[result['arm'], result['dataset']]) > 1e-12:
        raise ValueError('Computed threshold differs from the proposed amendment')
if blocked_events:
    raise ValueError('Unexpected I/O was attempted')
if set(read_events) != ALLOWED_READS:
    raise ValueError('Unexpected set of files read')

report = {
    'checked_at_utc': datetime.now(timezone.utc).isoformat(),
    'scope': 'Computational provenance of this execution; not a claim about historical human test exposure',
    'optimizer_path': OPTIMIZER.relative_to(ROOT).as_posix(),
    'optimizer_sha256': hashlib.sha256(optimizer_bytes).hexdigest(),
    'verifier_sha256': hashlib.sha256(verifier_bytes).hexdigest(),
    'rules': optimizer.RULES, 'rules_sha256': optimizer.RULES_SHA256,
    'file_access_enforcement': 'Python open audit hook: only four exact validation records and two source files may be read; only this report may be written',
    'opened_read_paths': sorted(set(read_events)),
    'blocked_events': blocked_events,
    'test_files_read': [],
    'all_four_thresholds_match_amendment': True,
    'results': results,
}
OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
for result in results:
    print(f"{result['arm']:2} {result['dataset']:6} validation n={result['n_rows']} valid={result['n_valid']} tau={result['tau']:.2f} MCC={result['validation_mcc']:.12f}")
print('PASS: all four thresholds match; four validation inputs; zero test files read.')
print('Optimizer SHA256:', report['optimizer_sha256'])
print('Evidence:', OUTPUT)
