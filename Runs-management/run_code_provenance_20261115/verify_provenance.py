"""Kiểm lại liên kết worker -> notebook -> records cho 20 nhóm records trong
docs/REPLY_RUN_CODE_PROVENANCE_HIEU.md.

Chạy từ gốc repo:
    python Runs-management/run_code_provenance_20261115/verify_provenance.py
    python Runs-management/run_code_provenance_20261115/verify_provenance.py --bundles <thư mục 42_devign.zip ...>

Cần `runs/final/` (records chuẩn validation, gitignored) ở local; records test
lấy từ `runs/final/` nếu có, nếu không thì từ
`Runs-management/run_handoff_20261108/completed_results/` (có trên git). `--bundles` là tùy chọn:
khi có bundle prompt B1-shuf, script tính lại SHA-256 của từng prompt và so với
`prompt_sha256` trong records.
"""
import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORKERS = {
    'W-val': ('workers/W-val_kaggle_inference.py',
              'e8aecdce40bfadcd98f272318af0df0127b7fb1d41ef78541c7474114840fec3'),
    'W-val-rep': ('workers/W-val-rep_kaggle_inference.py',
                  'c418ea6774a9cd24852b4b408143b559fd7f1562ef8eca44e38c60877f772e40'),
    'W-test': ('workers/W-test_kaggle_test_inference.py',
               '9a0e5c3363817b7f8ce49032286994d1da0e176e2cfc85e002c3785bf92e14b6'),
}
NOTEBOOK_WORKER = {
    'tomandjerry223_validation_20261108/grace-b1-full-validation/notebook.ipynb': 'W-val',
    'tomandjerry223_validation_20261108/grace-b1-shuf-validation/notebook.ipynb': 'W-val',
    'tomandjerry223_validation_20261108/grace-b2-nolabel-validation/notebook.ipynb': 'W-val',
    'b1_shuf_chain/session2_notebook_thanhduy9a4tv.ipynb': 'W-val',
    'kaggle_readback_20261115/thanhduy9a4tv__grace-b2-labelonly-validation/notebook.ipynb': 'W-val',
    'kaggle_readback_20261115/thanhduy9a4tv__grace-b2-rep-validation/notebook.ipynb': 'W-val-rep',
    'kaggle_readback_20261115/tomandjerry223__grace-b2-nolabel-test/notebook.ipynb': 'W-test',
    'kaggle_readback_20261115/tomandjerry223__grace-b2-labelonly-test/notebook.ipynb': 'W-test',
    'kaggle_readback_20261115/huuhieu3333__grace-b2-rep-test/notebook.ipynb': 'W-test',
}
# Records nằm trong output/checkpoint không đưa lên git; local_only_files.json giữ hash.
LOCAL_RECORDS = {
    'grace_b1_full_validation_checkpoint.zip': 'B1-full',
    'grace_b2_nolabel_validation_checkpoint.zip': 'B2-nolabel',
    'grace_b2_rep_test_final_output.zip': 'B2-rep',
    'grace_b2_rep_validation_checkpoint.zip': 'B2-rep',
    'grace_b2_labelonly_validation_checkpoint.zip': 'B2-labelonly',
    'grace_b2_nolabel_test_final_output.zip': 'B2-nolabel',
    'grace_b2_labelonly_test_final_output.zip': 'B2-labelonly',
}
# Thứ tự trường do W-val ghi (dict `row` trong run_batch).
W_VAL_ROW_KEYS = ['id', 'dataset', 'split', 'label', 'prompt_sha256', 'demo_ids', 'tokens', 'graph_missing',
                  'logprob_0', 'logprob_1', 'p0', 'p1', 's', 'pred_argmax', 'greedy_token_id', 'top5',
                  'arm', 'raw', 'response_valid', 'valid', 'token_ids', 'model_sha256', 'backend',
                  'quantization', 'model_repo', 'model_repo_revision', 'seed', 'timestamp',
                  'logprob_distribution', 'elapsed_s']
IGNORED_MANIFEST = {'bundle_sha256', 'prompt_set_sha256'}


def lf(b):
    return b.replace(b'\r\n', b'\n')


def sha(b):
    return hashlib.sha256(b).hexdigest()


def cells(path):
    nb = json.loads(Path(path).read_text(encoding='utf-8'))
    return [''.join(c['source']) if isinstance(c['source'], list) else c['source'] for c in nb['cells']]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', default=str(HERE.parents[1]))
    ap.add_argument('--bundles', default=None)
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    if not args.bundles and (HERE / 'b1_shuf_chain' / 'prompt_bundles').is_dir():
        args.bundles = str(HERE / 'b1_shuf_chain' / 'prompt_bundles')
    final = Path(args.repo) / 'runs' / 'final'
    if not final.exists():
        sys.exit(f'Không thấy {final}')
    failures, report = [], {}

    def check(name, ok, detail=''):
        report[name] = {'ok': bool(ok), 'detail': detail}
        if not ok:
            failures.append(name)

    text = {}
    for wid, (rel, expected) in WORKERS.items():
        b = lf((HERE / rel).read_bytes())
        text[wid] = b.decode('utf-8').strip()
        check(f'worker {wid} sha256', sha(b) == expected, sha(b))
    for rel, wid in NOTEBOOK_WORKER.items():
        check(f'notebook chứa {wid}: {rel}', any(text[wid] in c for c in cells(HERE / rel)))

    handoff = Path(args.repo) / 'Runs-management' / 'run_handoff_20261108' / 'completed_results'

    def canon(ds, split, arm, seed=42):
        p = final / ds / split / arm / str(seed) / 'records.jsonl'
        if not p.exists() and split == 'test':
            # records test chuẩn đã có trên git, là input của analysis_checks_20261112
            p = handoff / arm / f'seed_{seed}' / ds / 'test' / 'records.jsonl'
        b = lf(p.read_bytes())
        if b'"group"' in b:
            # runs/final do import_records tạo (từ 13/11) có thêm trường `group`.
            # Bỏ trường này rồi ghi lại đúng cách worker ghi record
            # (json.dumps(row, ensure_ascii=False)) để so byte với output phiên.
            rows = [json.loads(x) for x in b.decode('utf-8').splitlines() if x.strip()]
            b = ''.join(json.dumps({k: v for k, v in r.items() if k != 'group'}, ensure_ascii=False) + '\n'
                        for r in rows).encode('utf-8')
        return b

    def final_manifest(ds, seed, ckpts):
        # runs/final mới không còn run_manifest.json; khi thiếu thì lấy manifest của
        # checkpoint cuối cùng có file này làm mốc so cho các phiên trước.
        p = final / ds / 'validation' / 'B1-shuf' / str(seed) / 'run_manifest.json'
        if p.exists():
            return json.loads(p.read_text(encoding='utf-8')), 'runs/final'
        mn = f'seed_{seed}/{ds}/validation/run_manifest.json'
        for i in (3, 2, 1):
            if mn in ckpts[i - 1].namelist():
                return json.loads(ckpts[i - 1].read(mn)), f'session{i}'
        raise FileNotFoundError(mn)

    # B1-shuf: chuỗi ba phiên
    chain = HERE / 'b1_shuf_chain'
    ckpts = [zipfile.ZipFile(chain / f'session{i}_end_checkpoint.zip') for i in (1, 2, 3)]
    for seed in (42, 43, 44):
        for ds in ('devign', 'reveal'):
            can = canon(ds, 'validation', 'B1-shuf', seed)
            rows = [json.loads(x) for x in can.decode('utf-8').splitlines() if x.strip()]
            fin_m, fin_src = final_manifest(ds, seed, ckpts)
            bm = json.loads((chain / 'bundle_manifests' / f'{seed}_{ds}.json').read_text(encoding='utf-8'))
            states = []
            for i, z in enumerate(ckpts, 1):
                rn = f'seed_{seed}/{ds}/validation/records.jsonl'
                mn = f'seed_{seed}/{ds}/validation/run_manifest.json'
                if rn not in z.namelist():
                    states.append('-')
                    continue
                part = lf(z.read(rn))
                state = 'full' if part == can else ('prefix' if can.startswith(part) else 'MISMATCH')
                n_lines = part.count(b'\n')
                states.append(f'{state}:{n_lines}')
                check(f'B1-shuf s{seed} {ds} phiên {i} records là tiền tố/khớp bản chuẩn', state != 'MISMATCH')
                m = json.loads(z.read(mn))
                stable = {k: v for k, v in m.items() if k not in IGNORED_MANIFEST}
                check(f'B1-shuf s{seed} {ds} phiên {i} run_manifest khớp bản chuẩn',
                      stable == {k: v for k, v in fin_m.items() if k not in IGNORED_MANIFEST}
                      and m.get('prompt_set_sha256') == bm['prompts_sha256'], f'mốc={fin_src}')
            check(f'B1-shuf s{seed} {ds} phiên cuối đủ records', states[-1].startswith('full'), ' | '.join(states))
            check(f'B1-shuf s{seed} {ds} trường record đúng khuôn W-val',
                  all(list(r.keys()) == W_VAL_ROW_KEYS for r in rows)
                  and len({r['model_sha256'] for r in rows}) == 1
                  and {r['arm'] for r in rows} == {'B1-shuf'} and {r['seed'] for r in rows} == {seed})
            check(f'B1-shuf s{seed} {ds} số dòng = bundle', len(rows) == bm['count'])
            if args.bundles:
                with zipfile.ZipFile(Path(args.bundles) / f'{seed}_{ds}.zip') as z:
                    pb = z.read('prompts.jsonl')
                ok = sha(pb) == bm['prompts_sha256']
                prompts = {str(p['id']): p for p in map(json.loads, pb.decode('utf-8').splitlines()) if p}
                bad = sum(1 for r in rows if sha(prompts[str(r['id'])]['prompt'].encode()) != r['prompt_sha256'])
                check(f'B1-shuf s{seed} {ds} prompt_sha256 tính lại từ bundle', ok and bad == 0, f'lệch={bad}')

    # Các nhóm còn lại: hash records trong output/checkpoint đã tải về
    local = json.loads((HERE / 'local_only_files.json').read_text(encoding='utf-8'))
    for key, entry in local.items():
        arm = LOCAL_RECORDS.get(Path(key).name)
        if not arm:
            continue
        for name, rec in entry['records'].items():
            ds = 'devign' if '/devign/' in name else 'reveal'
            split = 'test' if '/test/' in name else 'validation'
            can = canon(ds, split, arm)
            check(f'{arm} {split} {ds} ({Path(key).name})', sha(can) == rec['sha256_lf'] and can.count(b'\n') == rec['lines'])

    for name, r in report.items():
        print(('OK   ' if r['ok'] else 'FAIL ') + name + (f'  [{r["detail"]}]' if r['detail'] else ''))
    print(f'\n{len(report) - len(failures)}/{len(report)} kiểm tra đạt')
    sys.exit(1 if failures else 0)


if __name__ == '__main__':
    main()
