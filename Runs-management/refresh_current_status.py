"""Refresh local progress without fitting thresholds or changing historical snapshots."""
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = '01_Author_Baseline_Unified'
FOLDERS = {'B0': '02_Arm_B0_Source_Only', 'B1': '03_Arm_B1_Graph_Only',
           'B2': BASE, 'B2-flip': '04_Arm_B2_Flip', 'B2-rep': '05_Arm_B2_Rep',
           'B2-rand': '06_Arm_B2_Rand'}
SOURCES = {'B0': '02_Arm_B0_Source_Only/output/kaggle_20261101_duchuynguyen1802/grace_b0_runs',
           'B1': '03_Arm_B1_Graph_Only/output/kaggle_run_02/grace_b1_runs',
           'B2': BASE + '/output/local_full/inference_qwen_q4_b2_frozen_donor_20261102',
           'B2-flip': '04_Arm_B2_Flip/output/kaggle_20261105_quangdung1111_run2/grace_b2_flip_frozen_donor_20261104_inherit_b2_9h30',
           'B2-rand': '06_Arm_B2_Rand/output/kaggle_run_02/grace_b2_rand_three_seed_11h'}
SPLITS = [('devign', 'validation', 2732), ('devign', 'test', 2732),
          ('reveal', 'validation', 2273), ('reveal', 'test', 2274)]

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def rows(path):
    with path.open(encoding='utf-8') as stream:
        return [json.loads(line) for line in stream if line.strip()]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def collect(root=ROOT, here=HERE):
    locks = read(here / 'thresholds.json')['entries']
    result = {'schema': 'local_progress_v1', 'checked_at_utc': datetime.now(timezone.utc).isoformat(),
              'scope': 'Known imported outputs only; no cloud status inferred',
              'thresholds_fitted': False, 'historical_snapshots_modified': False,
              'watcher': {'state': 'not_verified_running', 'pid_file_present': (here/'threshold_watch.pid').exists(),
                          'note': 'Log/PID alone do not establish a live process; watcher was not started.'},
              'arms': []}
    for arm, folder in FOLDERS.items():
        source = root / SOURCES[arm] if arm in SOURCES else None
        prompt_root = root / folder / 'output/bundles'
        if arm == 'B2':
            prompt_root = here / 'donor_reconciliation_20261101/new_reference/B2'
        elif arm == 'B2-flip':
            prompt_root = root / folder / 'output/bundles_frozen_donor_20261101'
        entry = {'arm': arm, 'source': SOURCES.get(arm), 'splits': [], 'notebooks': []}
        for dataset, split, expected_count in SPLITS:
            if arm == 'B2-rand':
                seed_details = []
                for seed in (42, 43, 44):
                    record_path = root / SOURCES[arm] / f'seed_{seed}' / dataset / split / 'records.jsonl'
                    actual = rows(record_path) if record_path.exists() else []
                    expected_path = prompt_root / f'seed_{seed}' / dataset / split / 'prompts.jsonl'
                    expected = {str(r['id']): r for r in rows(expected_path)} if actual else {}
                    manifest = read(record_path.with_name('run_manifest.json')) if actual else {}
                    seen = set()
                    for row in actual:
                        uid = str(row['id']); ref = expected.get(uid)
                        if uid in seen or ref is None or row['arm'] != arm or row['dataset'] != dataset or row['split'] != split:
                            raise ValueError(f'Unexpected or duplicate record: {arm}/{seed}/{dataset}/{split}/{uid}')
                        if row['label'] != ref['label'] or row['prompt_sha256'] != ref['prompt_sha256'] or row['model_sha256'] != manifest['model_sha256']:
                            raise ValueError(f'Prompt/label/model mismatch: {arm}/{seed}/{uid}')
                        seen.add(uid)
                    detail = {'seed': seed, 'completed': len(actual), 'expected': expected_count,
                              'invalid_response': sum(r.get('response_valid') is not True for r in actual),
                              'invalid_score': sum(not (r.get('valid') and isinstance(r.get('s'), (int, float)) and math.isfinite(r['s']) and 0 <= r['s'] <= 1) for r in actual)}
                    if actual:
                        detail.update(records_sha256=sha(record_path), records_path=record_path.relative_to(root).as_posix())
                    seed_details.append(detail)
                completed = sum(d['completed'] for d in seed_details)
                item = {'dataset': dataset, 'split': split, 'expected': expected_count*3, 'completed': completed,
                        'missing': expected_count*3-completed, 'invalid_response': sum(d['invalid_response'] for d in seed_details),
                        'invalid_score': sum(d['invalid_score'] for d in seed_details), 'seeds': seed_details}
                if split == 'validation': item.update(threshold_state='waiting_validation_records', tau=None)
                entry['splits'].append(item)
                continue
            record_path = source/dataset/split/'records.jsonl' if source else None
            actual = rows(record_path) if record_path and record_path.exists() else []
            expected_path = prompt_root/dataset/split/'prompts.jsonl'
            expected = {r['id']: r for r in rows(expected_path)} if actual else {}
            manifest = read(record_path.with_name('run_manifest.json')) if actual else {}
            seen = set()
            for row in actual:
                uid = row['id']
                ref = expected.get(uid)
                if uid in seen or ref is None or row['arm'] != arm or row['dataset'] != dataset or row['split'] != split:
                    raise ValueError(f'Unexpected or duplicate record: {arm}/{dataset}/{split}/{uid}')
                if (row['label'] != ref['label'] or row['prompt_sha256'] != ref['prompt_sha256']
                        or row['model_sha256'] != manifest['model_sha256']):
                    raise ValueError(f'Prompt/label mismatch: {arm}/{uid}')
                seen.add(uid)
            locked = locks.get(f'{arm}/{dataset}')
            if arm == 'B2' and dataset == 'devign':
                lock_path = source / 'thresholds_devign.json'
                locked = read(lock_path)['entries']['B2/devign']
                if locked['validation_prompt_set_sha256'] != sha(prompt_root/dataset/'validation'/'prompts.jsonl'):
                    raise ValueError('B2 Devign threshold prompt set mismatch')
            if arm == 'B2-flip' and split == 'validation':
                lock_path = source / dataset / 'validation' / 'threshold_lock.json'
                locked = read(lock_path)
                expected_tau = {'devign': 0.70, 'reveal': 0.12}[dataset]
                if (locked.get('threshold_policy') != 'inherit_base_B2_prereg_v1'
                        or locked.get('tau') != expected_tau
                        or locked.get('n_expected') != expected_count
                        or locked.get('validation_prompt_set_sha256') != sha(prompt_root/dataset/'validation'/'prompts.jsonl')):
                    raise ValueError(f'B2-flip inherited threshold provenance mismatch: {dataset}')
            item = {'dataset': dataset, 'split': split, 'expected': expected_count,
                    'completed': len(actual), 'missing': expected_count-len(actual),
                    'invalid_response': sum(r.get('response_valid') is not True for r in actual),
                    'invalid_score': sum(not (r.get('valid') and isinstance(r.get('s'), (int, float))
                                             and math.isfinite(r['s']) and 0 <= r['s'] <= 1) for r in actual)}
            if actual:
                item.update(records_sha256=sha(record_path), records_path=record_path.relative_to(root).as_posix())
            if split == 'validation':
                if arm == 'B2-flip' and locked:
                    item['threshold_state'] = 'inherited_base_B2_prereg_v1'
                else:
                    item['threshold_state'] = ('locked_frozen_donor_version' if arm == 'B2' and dataset == 'devign' else 'locked_historical_prompt_version') if locked else ('validation_complete_unlocked' if len(actual)==expected_count else 'waiting_validation_records')
                item['tau'] = locked['tau'] if locked else None
            entry['splits'].append(item)
        notebook_paths = sorted((root/folder/'notebooks').glob('02_*kaggle*.ipynb'))
        if arm == 'B2-rand':
            notebook_paths = [here/'kaggle_validation_6arms_20261104/02_kaggle_qwen_q4_b2_rand.ipynb']
        for path in notebook_paths:
            notebook = read(path)
            code = '\n'.join(''.join(c.get('source', [])) for c in notebook['cells'] if c['cell_type']=='code')
            entry['notebooks'].append({'path': path.relative_to(root).as_posix(), 'sha256': sha(path),
                                      'source_contains_make_lock_call': 'make_lock(' in code,
                                      'source_contains_test_lock_call': 'require_test_lock(' in code})
        entry['completed'] = sum(s['completed'] for s in entry['splits'])
        entry['expected'] = 30033 if arm == 'B2-rand' else 10011
        entry['missing'] = entry['expected']-entry['completed']
        entry['prompt_bundle_count'] = len(list(prompt_root.rglob('manifest.json' if arm == 'B2' else 'bundle_manifest.json')))
        if arm == 'B2-rand':
            entry['note'] = 'Latest imported checkpoint is in kaggle_run_02; validation only. B2 donor rerun-66 is part of B2, not another arm.'
        result['arms'].append(entry)
    return result

def current_section(here=HERE):
    state = read(here/'current_status.json')
    lines = ['<!-- current-status:start -->', '## Trạng thái hiện tại — đối chiếu artifact local', '',
             'Nguồn: [current_status.json](current_status.json), kiểm tra UTC ' + state['checked_at_utc'] + '.',
             'Snapshot kiểm toán/ngưỡng ngày 01/11 được giữ lịch sử; bảng này cập nhật tiến độ, không tạo khóa mới.', '',
             '| Arm | Devign val | Devign test | REVEAL val | REVEAL test | Tổng |',
             '|---|---:|---:|---:|---:|---:|']
    for arm in state['arms']:
        values = [str(s['completed'])+'/'+str(s['expected']) for s in arm['splits']]
        lines.append('| '+arm['arm']+' | '+' | '.join(values)+' | '+str(arm['completed'])+'/'+str(arm['expected'])+' |')
    unlocked = [a['arm']+'/'+s['dataset'] for a in state['arms'] for s in a['splits']
                if s.get('threshold_state') == 'validation_complete_unlocked']
    lines += ['', 'Validation đủ nhưng chưa có khóa local: '+(', '.join(unlocked) or 'Không có')+'.']
    gates = [a['arm']+': '+('có lời gọi khóa trước test' if a['notebooks'][0]['source_contains_test_lock_call'] else 'chưa có lời gọi khóa trước test')
             for a in state['arms'] if a['notebooks']]
    lines += ['', 'Source notebook (kiểm tra tĩnh): '+'; '.join(gates)+'. Không chứng minh thứ tự khóa của các run lịch sử.']
    lines += ['', 'Bằng chứng lịch sử [B1 I-07](b1_I07_20261102.json): 5.434 record, 0 invalid score, 3 invalid raw response; [B2-flip I-06](b2_flip_I06_20261102/KET_QUA_I06_B2_FLIP.md): 5.235 record. '
              'Run I-10 đã hoàn tất B2-flip donor mới đủ 10.011/10.011; ngưỡng kế thừa B2 là Devign 0,70 và ReVeal 0,12. '
              'B2 donor rerun 66 record thuộc B2, giữ lịch sử B2 riêng.',
              '', 'Run I-11 B2-rand chỉ chạy validation: seed 42 đủ 5.005/5.005; seed 43 được 2.784/5.005; seed 44 chưa chạy. Tổng 7.789/15.015 validation, chưa fit ngưỡng và chưa chạy test. Xem hai run mới trong RUNS.md.',
              '', 'Watcher chưa được xác minh đang chạy; không tự khởi động. Các lỗi nghiệm thu prompt/protocol/OSF và lịch sử test trước khóa vẫn giữ nguyên.',
              '<!-- current-status:end -->', '']
    return '\n'.join(lines)


if __name__ == '__main__':
    state = collect()
    (HERE/'current_status.json').write_text(json.dumps(state, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    (HERE/'HIEN_TRANG.md').write_text('# Hiện trạng runs và code\n\n'+current_section(), encoding='utf-8')
    print('Refreshed current_status.json and HIEN_TRANG.md; no threshold or historical snapshot changed')
