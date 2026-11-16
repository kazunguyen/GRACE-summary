"""Kiểm liên kết worker -> records cho bốn nhóm B2 chính (I-02, I-04, I-05).

Chạy từ gốc repo:
    python Runs-management/package_review_20261116/verify_b2_session_chain.py

Chỉ dùng file đã có trên git:
- 01_Author_Baseline_Unified/kaggle_qwen_q4_b2/downloaded_output_20261101*/ : output Kaggle
  tải về của từng phiên (checkpoint_status, run_manifest, records, kaggle_inference.py);
- 01_Author_Baseline_Unified/output/local_full/inference_qwen_q4_b2_20261101/ : run_history
  I-02/I-04/I-05, checkpoint I-02/I-04 và records hợp nhất bốn split;
- 01_Author_Baseline_Unified/output/local_full/inference_qwen_q4_b2_frozen_donor_20261102/ :
  records test chuẩn (nguồn import runs/final cho B2 test).
"""
import argparse
import hashlib
import io
import json
import re
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
DL = Path('01_Author_Baseline_Unified/kaggle_qwen_q4_b2')
HIST = Path('01_Author_Baseline_Unified/output/local_full/inference_qwen_q4_b2_20261101')
DONOR = Path('01_Author_Baseline_Unified/output/local_full/inference_qwen_q4_b2_frozen_donor_20261102')
SESSIONS = {  # thư mục output tải về -> phiên trong RUNS.md
    'downloaded_output_20261101': 'I-02',
    'downloaded_output_20261101_run2': 'I-04',
    'downloaded_output_20261101_run3': 'I-05',
}
EXPECTED_WORKER = {
    'I-02': 'c4e5d888c8a8556593fb3b61c96583e68d8493b54b9b0ba9305f215ac5390ac2',
    'I-04': 'c901d1c34e031b4d593555fe559b82b531b5bb19375d115947d8b6b2666cabe7',
    'I-05': 'c901d1c34e031b4d593555fe559b82b531b5bb19375d115947d8b6b2666cabe7',
}
SPLITS = [(d, s) for d in ('devign', 'reveal') for s in ('validation', 'test')]


def lf(b):
    return b.replace(b'\r\n', b'\n')


def sha(b):
    return hashlib.sha256(lf(b)).hexdigest()


def identity_keys(worker_text):
    block = re.search(r"identity = \{(.*?)\}\n", worker_text, re.S).group(1)
    return sorted(re.findall(r"'([a-z_0-9]+)':", block))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', default=str(HERE.parents[1]))
    root = Path(ap.parse_args().repo)
    sys.stdout.reconfigure(encoding='utf-8')
    report, failures = [], []

    def check(name, ok, detail=''):
        report.append((ok, name, detail))
        if not ok:
            failures.append(name)

    final = {k: lf((root / HIST / 'grace_b2_four_split_8h' / k[0] / k[1] / 'records.jsonl').read_bytes()) for k in SPLITS}
    hist = {r: json.loads((root / HIST / 'run_history' / r / 'checkpoint_status.json').read_text(encoding='utf-8'))
            for r in ('I-02', 'I-04', 'I-05')}

    for d, run in SESSIONS.items():
        base = root / DL / d
        st = json.loads((base / 'grace_b2_four_split_8h' / 'checkpoint_status.json').read_text(encoding='utf-8'))
        check(f'{run}: started_at của output tải về trùng run_history', st['started_at'] == hist[run]['started_at'],
              st['started_at'])
        check(f'{run}: số record lũy kế trùng run_history',
              st.get('completed_records_total') == hist[run].get('completed_records_total'),
              str(st.get('completed_records_total')))
        w = (base / 'kaggle_inference.py').read_bytes()
        h = sha(w)
        check(f'{run}: worker trong output', h == EXPECTED_WORKER[run], h)
        keys = identity_keys(lf(w).decode('utf-8'))
        for ds, sp in SPLITS:
            rp = base / 'grace_b2_four_split_8h' / ds / sp / 'records.jsonl'
            if not rp.exists():
                continue
            part = lf(rp.read_bytes())
            n = len(part.splitlines())
            check(f'{run}: {ds}/{sp} records ({n}) là tiền tố/trùng records hợp nhất', final[(ds, sp)].startswith(part))
            m = json.loads((rp.parent / 'run_manifest.json').read_text(encoding='utf-8'))
            check(f'{run}: {ds}/{sp} run_manifest có đúng bộ trường mà worker ghi', sorted(m) == keys,
                  f'{len(m)} trường')

    # Checkpoint I-02/I-04 lưu riêng cũng là tiền tố của records hợp nhất
    for name in ('grace_b2_checkpoint_I02_partial.zip', 'grace_b2_checkpoint_I04_partial.zip'):
        z = zipfile.ZipFile(io.BytesIO((root / HIST / name).read_bytes()))
        for member in z.namelist():
            if member.endswith('records.jsonl'):
                ds, sp = member.split('/')[-3], member.split('/')[-2]
                check(f'{name}: {ds}/{sp} là tiền tố records hợp nhất', final[(ds, sp)].startswith(lf(z.read(member))))

    # Worker I-04/I-05 nằm nguyên văn trong notebook B2 được commit cùng output
    nb_path = root / DL / 'downloaded_output_20261101_run3' / 'kaggle_inference.py'
    w45 = lf(nb_path.read_bytes()).decode('utf-8').strip()
    check('Worker I-04/I-05 có cơ chế resume bỏ qua bundle_sha256 và kiểm prompt/model từng dòng',
          "ignored = {'bundle_sha256'" in w45 and 'Checkpoint prompt mismatch' in w45 and 'Checkpoint model hash mismatch' in w45)

    # Test chuẩn = records hợp nhất + dòng donor chạy lại (I-09)
    for ds in ('devign', 'reveal'):
        a = {str(r['id']): r for r in (json.loads(x) for x in final[(ds, 'test')].decode('utf-8').splitlines() if x.strip())}
        b = {str(r['id']): r for r in (json.loads(x) for x in lf((root / DONOR / ds / 'test' / 'records.jsonl').read_bytes()).decode('utf-8').splitlines() if x.strip())}
        changed = [i for i in b if a.get(i) != b[i]]
        ts = sorted(b[i]['timestamp'] for i in changed)
        check(f'{ds}/test chuẩn = records I-02/I-04/I-05 trừ {len(changed)} dòng donor chạy lại',
              set(a) == set(b) and all(t.startswith('2026-11-02') for t in ts),
              f'{ts[0][:19]} → {ts[-1][:19]}' if ts else 'không có dòng thay')

    for ok, name, detail in report:
        print(('OK   ' if ok else 'FAIL ') + name + (f'  [{detail}]' if detail else ''))
    print(f'\n{len(report) - len(failures)}/{len(report)} kiểm tra đạt')
    sys.exit(1 if failures else 0)


if __name__ == '__main__':
    main()
