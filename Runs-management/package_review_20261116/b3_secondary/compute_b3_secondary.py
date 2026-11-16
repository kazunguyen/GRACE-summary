"""Paired cluster bootstrap cho các phép so phụ nhóm B3 (exploratory).

Chạy:
    python compute_b3_secondary.py <gốc gói Option1> <repo có origin/dung> <file csv đầu ra>

- <gốc gói Option1>: chứa runs/final (records B2 test, groups.csv) và grace_diag_kit/src.
- Records B3 đọc từ origin/dung (Runs-management/kaggle_outputs_2026111*/...).
- Bootstrap: grace_diag.stats.paired_bootstrap, 5.000 lượt, seed 20261117, cụm theo groups.csv
  (commit_id Devign, file_hash ReVeal). Danh sách thành viên cụm được cache một lần; mỗi lượt
  vẫn gọi rng.integers như stats._resample_indices nên chuỗi lấy mẫu giữ nguyên.
- Ngưỡng: B2 0,70/0,12; B3, B3-swap, B3-flip 0,99/0,01; B3-nodiff 0,92/0,01 (đều khóa trên validation).
"""
import csv
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

RP = Path(sys.argv[1])          # extracted package subset (runs/final, kit)
REPO = Path(sys.argv[2])        # git checkout with origin/dung
OUT = Path(sys.argv[3])
sys.path.insert(0, str(RP / 'grace_diag_kit' / 'src'))
from grace_diag import stats  # noqa: E402

sys.stdout.reconfigure(encoding='utf-8')

# Cache cluster membership once; draws stay identical to stats._resample_indices
# (same rng.integers call per replicate), only the per-replicate rebuild is skipped.
_cache = {}


def _cached_resample(rng, n, groups):
    if groups is None:
        return rng.integers(0, n, n)
    key = (len(groups), hash('\x1f'.join(map(str, groups.tolist()))))
    if key not in _cache:
        uniq, inv = np.unique(groups, return_inverse=True)
        _cache[key] = (len(uniq), [np.flatnonzero(inv == g) for g in range(len(uniq))])
    k, members = _cache[key]
    picked = rng.integers(0, k, k)
    return np.concatenate([members[g] for g in picked])


stats._resample_indices = _cached_resample


def git_recs(path):
    raw = subprocess.run(['git', '-C', str(REPO), 'show', f'origin/dung:{path}'], capture_output=True, check=True).stdout
    return {str(r['id']): r for r in (json.loads(l) for l in raw.decode('utf-8').splitlines() if l.strip())}


def file_recs(path):
    return {str(r['id']): r for r in (json.loads(l) for l in open(path, encoding='utf-8') if l.strip())}


groups = {}
with open(RP / 'runs' / 'final' / 'groups.csv', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        groups[row['id']] = row['group']

SRC = {
    'B3-nodiff': ('Runs-management/kaggle_outputs_20261110/b3_nodiff_test_runtime_locked/b3_nodiff_test/{ds}/seed_42/{ds}/test/records.jsonl', {'devign': 0.92, 'reveal': 0.01}),
    'B3': ('Runs-management/kaggle_outputs_20261111/b3_verified_patch_test_10h/b3_test_release_20261110/seed_42/{ds}/test/records.jsonl', {'devign': 0.99, 'reveal': 0.01}),
    'B3-swap': ('Runs-management/kaggle_outputs_20261111/b3_swap_test_resume_latest/b3_swap_test_release_20261110/seed_42/{ds}/test/records.jsonl', {'devign': 0.99, 'reveal': 0.01}),
    'B3-flip': ('Runs-management/kaggle_outputs_20261111/b3_flip_test_20261110_v1/b3_flip_test_release_20261110/seed_42/{ds}/test/records.jsonl', {'devign': 0.99, 'reveal': 0.01}),
}
B2_TAU = {'devign': 0.70, 'reveal': 0.12}
PAIRS = [('B2', 'B3'), ('B2', 'B3-nodiff'), ('B3', 'B3-swap'), ('B3', 'B3-flip')]

rows_out = []
for ds in ('devign', 'reveal'):
    b2 = file_recs(RP / 'runs' / 'final' / ds / 'test' / 'B2' / '42' / 'records.jsonl')
    ids = list(b2)
    y = np.array([int(b2[i]['label']) for i in ids])
    g = np.array([groups.get(i) for i in ids], dtype=object)
    if any(x is None for x in g):
        raise SystemExit(f'missing cluster ids for {ds}')
    arms = {'B2': (np.array([b2[i]['s'] for i in ids]), B2_TAU[ds])}
    for arm, (p, tau) in SRC.items():
        r = git_recs(p.format(ds=ds))
        if set(r) != set(ids):
            raise SystemExit(f'{arm} {ds}: ID set differs from B2')
        arms[arm] = (np.array([r[i]['s'] for i in ids]), tau[ds])
    for a, b in PAIRS:
        sa, ta = arms[a]
        sb, tb = arms[b]
        pa, pb = (sa >= ta).astype(int), (sb >= tb).astype(int)
        for metric, fn, xa, xb in (('AUROC', stats.auroc, sa, sb), ('MCC', stats.mcc, pa, pb),
                                   ('positive_rate', lambda yy, p: float(np.mean(p)), pa, pb)):
            ci = stats.paired_bootstrap(y, xa, xb, fn, n_boot=5000, seed=20261117, groups=g)
            rows_out.append({'dataset': ds, 'arm_a': a, 'arm_b': b, 'metric': metric,
                             'threshold_policy': 'threshold_free' if metric == 'AUROC' else f'locked tau_a={ta}, tau_b={tb}',
                             'n_paired': len(ids), 'n_clusters': len(set(g)), 'delta_b_minus_a': ci.delta,
                             'ci95_lo': ci.lo, 'ci95_hi': ci.hi, 'n_boot': ci.n_boot, 'n_degenerate': ci.n_degenerate,
                             'seed': ci.seed, 'unit': ci.unit, 'reporting_scope': 'exploratory'})
            print(f'{ds:6} {b:9}-{a:4} {metric:13} {ci.delta:+.4f} [{ci.lo:+.4f}; {ci.hi:+.4f}]', flush=True)

OUT.parent.mkdir(parents=True, exist_ok=True)
with open(OUT, 'w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows_out[0]))
    w.writeheader()
    w.writerows(rows_out)
print('wrote', OUT)
