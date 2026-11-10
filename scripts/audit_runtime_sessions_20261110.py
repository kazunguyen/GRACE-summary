"""Read-only retrospective runtime reconciliation; never alters historical outputs.

Reports observed evidence separately from configured settings and earlier reports.
Does not fit thresholds, run GPU inference or certify missing provenance.
"""
import ast
from collections import Counter, defaultdict
from datetime import datetime, timezone, timedelta
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import zipfile
import math

R = Path(__file__).resolve().parents[1]
OUT = R / 'Runs-management/runtime_session_reconciliation_20261110'
MODEL = 'f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335'
EXPECTED = {'devign/test': 2732, 'devign/validation': 2732,
            'reveal/test': 2274, 'reveal/validation': 2273}
MEMO = {}

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def file_sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def relative(p):
    return p.relative_to(R).as_posix()

def artifact(p, member=None):
    p = Path(p)
    key = (str(p), member)
    if key not in MEMO:
        if member:
            with zipfile.ZipFile(p) as z:
                raw = z.read(member)
            MEMO[key] = {'path': relative(p), 'member': member, 'sha256': sha(raw), 'bytes': len(raw)}
        else:
            MEMO[key] = {'path': relative(p), 'sha256': file_sha(p), 'bytes': p.stat().st_size}
    return MEMO[key]

def emit(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')

def git_blob(p):
    result = subprocess.run(['git', '-c', 'safe.directory=' + R.as_posix(), 'show', 'HEAD:' + relative(p)],
                            cwd=R, capture_output=True)
    return result.stdout if result.returncode == 0 else None

def exact_identity(p, expected, dest):
    raw = p.read_bytes()
    blob = git_blob(p)
    matched = raw if sha(raw) == expected else blob if blob is not None and sha(blob) == expected else None
    info = {'checkout_sha256': sha(raw), 'expected_sha256': expected,
            'lf_normalization_diagnostic_sha256': sha(raw.replace(b'\r\n', b'\n')),
            'git_blob_sha256': sha(blob) if blob is not None else None,
            'exact_original_bytes_recovered': matched is not None}
    info['git_commit'] = subprocess.run(['git', '-c', 'safe.directory=' + R.as_posix(), 'rev-parse', 'HEAD'],
                                        cwd=R, capture_output=True, text=True, check=True).stdout.strip()
    if matched is not None:
        target = OUT / 'recovered_sources' / dest
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(matched)
        info['preserved_original'] = artifact(target)
    return info

def records(p):
    return [json.loads(s) for s in p.read_text(encoding='utf-8').splitlines() if s.strip()]

def check_records(p):
    rows = records(p)
    first = rows[0]
    errors = Counter()
    stamps = []
    for x in rows:
        if (x.get('arm'), x.get('seed'), x.get('dataset'), x.get('split')) != (
                first.get('arm'), first.get('seed'), first.get('dataset'), first.get('split')):
            errors['scope'] += 1
        if x.get('model_sha256') != MODEL:
            errors['model'] += 1
        try:
            delta = x['logprob_1'] - x['logprob_0']
            s = 1 / (1 + math.exp(-delta)) if delta >= 0 else math.exp(delta) / (1 + math.exp(delta))
            if not math.isfinite(x['s']) or abs(s - x['s']) > 1e-12:
                errors['score'] += 1
        except (KeyError, TypeError, ValueError, OverflowError):
            errors['score_uncheckable'] += 1
        if x.get('timestamp'):
            stamps.append(x['timestamp'])
    ids = [x['id'] for x in rows]
    return {'artifact': artifact(p), 'arm': first.get('arm'), 'dataset': first.get('dataset'),
            'split': first.get('split'), 'seed': first.get('seed'), 'n': len(rows),
            'unique_ids': len(set(ids)), 'expected': EXPECTED.get(first['dataset'] + '/' + first['split']),
            'errors': dict(errors), 'first_timestamp': min(stamps) if stamps else None,
            'last_timestamp': max(stamps) if stamps else None,
            'runtime_hash_counts': dict(Counter(x.get('runtime_contract_sha256', x.get('runtime_lock_sha256', 'ABSENT')) for x in rows)),
            'runtime_reference_count': sum(bool(x.get('runtime_provenance')) for x in rows)}, rows

def time_value(s):
    return datetime.fromisoformat(s.replace('Z', '+00:00'))

def event_window(text, name):
    start = re.search(r'^\[([^\]]+)\] Bắt đầu ' + re.escape(name) + r':', text, re.M)
    end = re.search(r'^\[([^\]]+)\] ' + re.escape(name) + r' kết thúc với mã (\d+)', text, re.M)
    return {'start_utc': start.group(1) if start else None, 'end_utc': end.group(1) if end else None,
            'exit_code': int(end.group(2)) if end else None}

def bound(rows, window):
    if not window['start_utc'] or not window['end_utc']:
        return None
    lo, hi = time_value(window['start_utc']), time_value(window['end_utc'])
    return sum(lo <= time_value(x['timestamp']) <= hi for x in rows if x.get('timestamp'))

def log_facts(text):
    full = re.findall(r'offloaded\s+(\d+)/(\d+)\s+layers', text, re.I)
    gpu = sorted(set(re.findall(r'using device CUDA(\d+) \(([^)]+)\)', text)))
    batches = {k: sorted(set(re.findall(r'\b' + k + r'\s*=\s*(\d+)', text)))
               for k in ('n_ctx', 'n_batch', 'n_ubatch')}
    return {'native_offload_counts': full, 'native_devices': gpu, 'native_context': batches,
            'wheel_sha256': sorted(set(re.findall(r'Created wheel for llama-cpp-python:.*?sha256=([a-f0-9]{64})', text))),
            'build_cmake': sorted(set(re.findall(r'using CMake\s+([\d.]+)', text))),
            't4_probe_present': "['Tesla T4', 'Tesla T4']" in text,
            'post_install_package_snapshots': [json.loads(x) for x in re.findall(r'Installed package versions:\s*(\{[^\n]+\})', text)
                                              if '"0.3.16"' in x]}

def notebook_output(nb):
    return '\n'.join(''.join(o.get('text', [])) for c in nb['cells'] for o in c.get('outputs', []))

def reference_inventory():
    old = json.loads((R / 'worklogs/2026-11-07_inference_runtime_log_evidence.json').read_bytes())
    checked = []
    for run in old['runs']:
        items = []
        for a in run.get('artifacts', []):
            p = Path(a['path'])
            p = p if p.is_absolute() else R / p
            exists = p.is_file()
            current = file_sha(p) if exists else None
            items.append({'path': a['path'], 'recorded_sha256': a.get('sha256'), 'exists_now': exists,
                          'sha256_now': current, 'same_snapshot_now': current == a.get('sha256') if exists else None})
        checked.append({'prior_run': run['run'], 'artifacts': items})
    emit('PRIOR_ARTIFACT_AVAILABILITY.json', checked)

def candidate_inventory():
    cli = subprocess.run(['rg', '--files', '-uu', '-g', 'records.jsonl'], cwd=R,
                         capture_output=True, text=True, encoding='utf-8', check=True)
    result = []
    for line in cli.stdout.splitlines():
        p = R / line
        if any(part.startswith('.') or part in ('tests', '__pycache__') for part in p.relative_to(R).parts):
            continue
        try:
            raw = p.read_bytes()
            lines = raw.splitlines()
            head = json.loads(next(x for x in lines if x.strip()))
            result.append({'path': relative(p), 'sha256': sha(raw), 'bytes': len(raw),
                'n': sum(bool(x.strip()) for x in lines),
                'scope': {k: head.get(k) for k in ('arm', 'seed', 'dataset', 'split', 'runtime_contract_sha256')}})
        except (OSError, ValueError, StopIteration) as e:
            result.append({'path': relative(p), 'read_error': type(e).__name__})
    emit('RECORD_ARTIFACT_INVENTORY.json', result)
    return result

def priority_tests():
    sessions = []
    cases = [('B2-nolabel', 'tomandjerry223', 'b2_nolabel'),
             ('B2-labelonly', 'tomandjerry223', 'b2_labelonly'), ('B2-rep', 'huuhieu3333', 'b2_rep')]
    for arm, account, slug in cases:
        base = R / 'Runs-management/acceptance_6arms_20261108/network_verified' / account / ('grace-' + arm.lower() + '-test')
        events_p = base / 'output/grace_diagnostics/events.log'
        events = events_p.read_text(encoding='utf-8')
        stream_p = base / 'session.log'
        stream = ''.join(e.get('data', '') for e in json.loads(stream_p.read_bytes()))
        worker = base / 'output/kaggle_test_inference.py'
        source = worker.read_text(encoding='utf-8')
        constructor = [ast.get_source_segment(source, n) for n in ast.walk(ast.parse(source))
                       if isinstance(n, ast.Call) and ast.unparse(n.func) in ('Llama', 'llama_cpp.Llama')]
        diag = R / 'Runs-management/kernel_outputs_harvest' / (account + '_grace-' + arm.lower() + '-test') / 'grace_diagnostics.zip'
        with zipfile.ZipFile(diag) as z:
            crc = z.testzip() is None
            for ds in ('devign', 'reveal'):
                name = 'test_' + slug + '_' + ds
                win = event_window(events, name)
                path = base / 'output' / (slug + '_test/seed_42') / ds / 'test/records.jsonl'
                summary, rows = check_records(path)
                log = z.read(name + '.log').decode('utf-8', errors='replace')
                pattern = re.compile(re.escape(arm + '/' + ds) + r' (.+?): s=([\d.]+), raw=')
                shown = dict(pattern.findall(log))
                matching = sum(shown.get(x['id']) == format(x['s'], '.4f') for x in rows)
                manifest_p = path.parent / 'run_manifest.json'
                manifest = json.loads(manifest_p.read_bytes())
                core = log_facts(stream)
                sessions.append({'session_id': arm + '/test/seed42/' + ds, 'arm': arm, 'split': 'test', 'seed': 42,
                    'dataset': ds, 'kernel': account + '/grace-' + arm.lower() + '-test', 'window': win,
                    'records': summary, 'records_in_process_window': bound(rows, win),
                    'progress_log_unique_ids': len(shown), 'progress_rounded_score_matches': matching,
                    'record_file_hash_matches_manifest': summary['artifact']['sha256'] == manifest.get('records_sha256'),
                    'record_repeat_isolation': all(x.get('repeat') is True and x.get('tag') == 'repeat' for x in rows) if arm == 'B2-rep' else None,
                    'source_constructor': constructor, 'source_verbose_false': 'verbose=False' in source.replace(' ', ''),
                    'source_enforces_contract': 'assert_runtime(' in source,
                    'native_log': log_facts(log), 'session_install_and_build': core,
                    'artifacts': [artifact(events_p), artifact(stream_p), artifact(worker), artifact(manifest_p), artifact(diag, name + '.log')],
                    'diagnostics_crc': crc, 'verdict': 'PARTIAL_CORE_MATCH_NOT_FULL_LOCK',
                    'missing': ['native 49/49 placement for this process', 'source archive verified before build',
                                'loaded backend library hashes', 'GPU UUID/order/free VRAM at load',
                                'effective constructor/thread attestation', 'post-install dependency freeze/contract-bound provenance']})
    return sessions

def validation_archives():
    sessions = []
    executed_zip = R / 'Runs-management/GRACE_5ARMS_EXECUTED_NOTEBOOKS_AND_LOGS.zip'
    with zipfile.ZipFile(executed_zip) as executed:
        for arm, slug in [('B1-full', 'b1_full'), ('B1-shuf', 'b1_shuf'), ('B2-nolabel', 'b2_nolabel'),
                          ('B2-labelonly', 'b2_labelonly'), ('B2-rep', 'b2_rep')]:
            diag = R / ('Runs-management/output_' + slug + '/grace_diagnostics.zip')
            nbname = next(n for n in executed.namelist() if n.startswith('notebooks_executed/' + arm + '/') and n.endswith('.ipynb'))
            nb = json.loads(executed.read(nbname))
            output = notebook_output(nb)
            with zipfile.ZipFile(diag) as z:
                events = z.read('events.log').decode('utf-8')
                seed = 44 if arm == 'B1-shuf' else 42
                logname = 'validation_seed_' + str(seed)
                log = z.read(logname + '.log').decode('utf-8', errors='replace')
                win = event_window(events, logname)
                recordgroups = []
                for ds in ('devign', 'reveal'):
                    p = R / f'runs/final/{ds}/validation/{arm}/{seed}/records.jsonl'
                    summary, rows = check_records(p)
                    summary['records_in_this_process_window'] = bound(rows, win)
                    summary['carried_or_unbound_records'] = len(rows) - (bound(rows, win) or 0)
                    recordgroups.append(summary)
                sessions.append({'session_id': arm + '/validation/seed' + str(seed), 'arm': arm, 'split': 'validation',
                    'seed': seed, 'window': win, 'record_groups': recordgroups, 'native_log': log_facts(log),
                    'notebook_console': log_facts(output), 'artifacts': [artifact(diag), artifact(diag, logname + '.log'),
                        artifact(diag, 'events.log'), artifact(executed_zip, nbname)],
                    'verdict': 'HISTORICAL_NATIVE_MATCH_NOT_FULL_LOCK',
                    'missing': ['contract-bound per-record provenance', 'pre-build source archive verification',
                                'loaded library hashes and full dependency/thread/UUID attestation'],
                    'warning': 'A native log here does not certify another seed or test process.'})
    return sessions

def rand_test_sessions():
    specs = [
        ('rand-test-seed42-head', 'Runs-management/kaggle_outputs_20261107/b2_rand_seed42_test_latest', 'b2_rand_seed42_test'),
        ('rand-test-seed43-head', 'Runs-management/kaggle_outputs_20261107/b2_rand_seed43_test_latest', 'b2_rand_seed43_test'),
        ('rand-test-seed44-head', 'Runs-management/kaggle_outputs_20261108/b2_rand_seed44_test_latest', 'b2_rand_seed44_test'),
        ('rand-test-three-seed-tail', 'Runs-management/kaggle_outputs_20261107/b2_rand_three_seed_test_tail_latest', 'b2_rand_three_seed_test_tail'),
    ]
    rows_by_session, sessions = {}, []
    for sid, path, name in specs:
        base = R / path
        pro_p = base / name / 'runtime_provenance.json'
        pro = json.loads(pro_p.read_bytes())
        lock_p = base / 'inference_runtime_lock.json'
        lock = json.loads(lock_p.read_bytes())
        worker_p = base / 'kaggle_inference.py'
        log_p = base / name / 'model_load_offload.log'
        rows_by_session[sid] = {}
        counts, timestamps = {}, []
        for p in (base / name).glob('seed_*/*/test/records.jsonl'):
            summary, rs = check_records(p)
            key = str(summary['seed']) + '/' + summary['dataset']
            counts[key] = summary['n']
            timestamps.extend(x['timestamp'] for x in rs)
            for r in rs:
                rows_by_session[sid][(r['seed'], r['dataset'], r['id'])] = r
        freeze = pro.get('pip_freeze', '')
        original_lock = exact_identity(lock_p, pro['runtime_contract_sha256'], sid + '/inference_runtime_lock.json')
        original_worker = exact_identity(worker_p, pro['runner_sha256'], sid + '/kaggle_inference.py')
        unsigned = {k: v for k, v in lock.items() if k != 'integrity'}
        checks = {'contract_byte_hash_checkout': file_sha(lock_p) == pro.get('runtime_contract_sha256'),
            'contract_original_byte_identity': original_lock['exact_original_bytes_recovered'],
            'contract_canonical_seal': sha(json.dumps(unsigned, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()) == lock['integrity']['sha256'],
            'packages': all(pro['packages'].get(k) == v for k, v in lock['packages'].items()),
            'constructor': pro.get('constructor') == lock['constructor'],
            'runner_source_hash_checkout': file_sha(worker_p) == pro.get('runner_sha256'),
            'runner_original_byte_identity': original_worker['exact_original_bytes_recovered'],
            'backend_source_claim': pro.get('backend_sdist_sha256') == lock['backend_source']['sdist_sha256'],
            'two_t4_uuid_before_after': all(len(pro.get(k, '').strip().splitlines()) == 2 and pro.get(k, '').count('Tesla T4') == 2 for k in ('gpu_before_load', 'gpu_after_load')),
            'threads': pro.get('n_threads') == max(pro['cpu_count'] // 2, 1) and pro.get('n_threads_batch') == pro['cpu_count'],
            'compiled_backend_hashes_recorded': bool(pro.get('compiled_backend_sha256')),
            'dependency_freeze_recorded': bool(freeze), 'native_offload_log_available': log_p.is_file(),
            'native_offload_hash_replayed': file_sha(log_p) == pro.get('offload_log_sha256') if log_p.is_file() else None}
        sessions.append({'session_id': sid, 'arm': 'B2-rand', 'split': 'test', 'raw_counts': counts,
            'first_record_timestamp': min(timestamps), 'last_record_timestamp': max(timestamps),
            'runtime_contract_sha256': pro.get('runtime_contract_sha256'), 'checks': checks,
            'source_identity': {'contract': original_lock, 'worker': original_worker},
            'artifacts': [artifact(pro_p), artifact(lock_p), artifact(worker_p)],
            'verdict': 'PROVENANCE_MATCH_NATIVE_LOG_NOT_REPLAYABLE',
            'missing': ['native model-load log matching recorded SHA', 'build/install log chain for this exact session']})
    contributions, final_groups = Counter(), []
    for seed in (42, 43, 44):
        for ds in ('devign', 'reveal'):
            p = R / f'06_Arm_B2_Rand/test_results_20261107/seed_{seed}/{ds}/test/records.jsonl'
            summary, rows = check_records(p)
            assignments = Counter()
            for r in rows:
                key = (seed, ds, r['id'])
                matched = [sid for sid, lookup in rows_by_session.items() if lookup.get(key) == r]
                sid = matched[0] if len(matched) == 1 else ('UNMATCHED' if not matched else 'AMBIGUOUS')
                assignments[sid] += 1
                contributions[sid] += 1
            summary['source_session_counts_full_record_equality'] = dict(assignments)
            final_groups.append(summary)
    for x in sessions:
        x['records_used_in_final_merge'] = contributions[x['session_id']]
    return sessions, final_groups

def legacy_b3_sessions():
    base = R / 'Runs-management/run_handoff_20261108/completed_results/b3_historical_validation_completed_20261108'
    lock_p = base / 'inference_runtime_lock.json'
    lock = json.loads(lock_p.read_bytes())
    paths = subprocess.run(['rg', '--files', '-uu', '-g', 'install_llama_cuda.log', '-g', 'kaggle_inference.py',
                            '-g', 'grace_runtime_contract.py'], cwd=R, capture_output=True, text=True, encoding='utf-8', check=True).stdout.splitlines()
    by_sha = defaultdict(list)
    for value in paths:
        p = R / value
        if OUT in p.parents or any(part.startswith('.') for part in p.relative_to(R).parts):
            continue
        by_sha[file_sha(p)].append(p)
    all_rows = []
    for p in (base / 'B3/seed_42').glob('*/validation/records.jsonl'):
        all_rows.extend(records(p))
    result = []
    for pro_p in sorted(base.glob('locked_*/runtime_provenance.json')):
        pro = json.loads(pro_p.read_bytes())
        name = pro_p.parent.name
        selected = [r for r in all_rows if r.get('runtime_provenance') == name + '/runtime_provenance.json']
        native_p = pro_p.parent / 'model_load_offload.log'
        text = native_p.read_text(encoding='utf-8')
        facts = log_facts(text)
        checks = {'record_provenance_hashes': all(r.get('runtime_provenance_sha256') == file_sha(pro_p) for r in selected),
            'record_contract_and_model': all(r.get('runtime_contract_sha256') == pro['runtime_contract_sha256'] and r.get('model_sha256') == MODEL for r in selected),
            'launch_contract_bytes': file_sha(lock_p) == pro['runtime_contract_sha256'],
            'packages': pro['packages'] == lock['packages'], 'constructor': pro['constructor'] == lock['constructor'],
            'native_log_hash': file_sha(native_p) == pro['offload_log_sha256'],
            'native_full_offload': ['49', '49'] in facts['native_offload_counts'] or ('49', '49') in facts['native_offload_counts'],
            'native_two_t4': len(facts['native_devices']) == 2 and all('T4' in dev[1] for dev in facts['native_devices']),
            'native_context_batch': all(str(n) in facts['native_context'][k] for k, n in [('n_ctx', 8192), ('n_batch', 256), ('n_ubatch', 256)]),
            'two_t4_uuid_before_after': all(len(pro[k].strip().splitlines()) == 2 and pro[k].count('Tesla T4') == 2 for k in ('gpu_before_load', 'gpu_after_load')),
            'threads': pro['n_threads'] == max(pro['cpu_count'] // 2, 1) and pro['n_threads_batch'] == pro['cpu_count'],
            'backend_source': pro['backend_sdist_sha256'] == lock['backend_source']['sdist_sha256'],
            'compiled_hashes_and_freeze_recorded': bool(pro['compiled_backend_sha256']) and bool(pro['pip_freeze'])}
        matched = {}
        for key, filename in [('runner_sha256', 'kaggle_inference.py'), ('runtime_helper_sha256', 'grace_runtime_contract.py'),
                              ('backend_build_log_sha256', 'build_output.txt')]:
            candidates = by_sha.get(pro[key], [])
            checks[key + '_matched'] = bool(candidates)
            if candidates:
                # Byte equality permits source copies from another artifact; native/build logs
                # still must match the exact hash recorded by THIS session.
                source = candidates[0]
                dest = OUT / 'verified_legacy_b3_evidence' / name / filename
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(source.read_bytes())
                matched[key] = {'source': artifact(source), 'published_copy': artifact(dest)}
        result.append({'session_id': 'B3-historical/' + name, 'arm': 'B3-historical', 'split': 'validation',
            'records_referenced': len(selected), 'first_record_timestamp': min(r['timestamp'] for r in selected),
            'last_record_timestamp': max(r['timestamp'] for r in selected), 'checks': checks,
            'evidence': [artifact(pro_p), artifact(native_p), artifact(lock_p)], 'matched_sources_and_build': matched,
            'verdict': 'PASS_LAUNCH_RUNTIME_REFERENCED_SUBSET' if all(checks.values()) else 'PARTIAL_REFERENCED_SUBSET',
            'boundary': 'Applies only to this session\'s referenced records; 4,029 legacy carried rows remain uncertified. This is the historical algorithm, not amended B3.'})
    diag = R / 'Runs-management/kernel_outputs_harvest/lznt123_grace-b3-validation/grace_diagnostics.zip'
    with zipfile.ZipFile(diag) as z:
        events = z.read('events.log').decode('utf-8', errors='replace')
        win = event_window(events, 'validation_B3_seed_42')
        native = z.read('validation_B3_seed_42.log').decode('utf-8', errors='replace')
    legacy = [r for r in all_rows if not r.get('runtime_provenance')]
    legacy_session = {'session_id': 'B3-historical/original-validation-process', 'window': win,
        'records': len(legacy), 'records_in_process_window': bound(legacy, win), 'native_log': log_facts(native),
        'artifacts': [artifact(diag), artifact(diag, 'events.log'), artifact(diag, 'validation_B3_seed_42.log')],
        'verdict': 'HISTORICAL_NATIVE_MATCH_NOT_FULL_LOCK'}
    return {'sessions': result, 'legacy_without_session_provenance': len(legacy),
            'legacy_native_session': legacy_session, 'total': len(all_rows)}

def report_window_history():
    """Time matching to earlier RUNS.md is diagnostic, never native-log certification."""
    specs = [
        ('B1/I07', 'B1', '2026-11-01T10:17:36+00:00', '2026-11-01T18:12:21+00:00',
         '03_Arm_B1_Graph_Only/output/kaggle_run_02/grace_b1_runs'),
        ('B2/I02', 'B2', '2026-10-31T17:05:34+00:00', '2026-11-01T01:00:25+00:00',
         '01_Author_Baseline_Unified/output/local_full/inference_qwen_q4_b2_20261101/grace_b2_four_split_8h'),
        ('B2/I04', 'B2', '2026-11-01T02:12:23+00:00', '2026-11-01T10:07:11+00:00',
         '01_Author_Baseline_Unified/output/local_full/inference_qwen_q4_b2_20261101/grace_b2_four_split_8h'),
        ('B2/donor-correction-I09', 'B2', '2026-11-02T00:04:23+00:00', '2026-11-02T08:59:13+00:00',
         'Runs-management/kaggle_outputs_20261107/b2_rand_seed44_validation_latest/grace_b2_rand_three_seed_11h/b2_donor_rerun_66'),
        ('B2-rand/validation-I09', 'B2-rand', '2026-11-02T00:04:23+00:00', '2026-11-02T08:59:13+00:00',
         'Runs-management/kaggle_outputs_20261107/b2_rand_seed44_validation_latest/grace_b2_rand_three_seed_11h'),
        ('B2-rand/validation-I11', 'B2-rand', '2026-11-05T00:55:46+00:00', '2026-11-05T06:45:32+00:00',
         'Runs-management/kaggle_outputs_20261107/b2_rand_seed44_validation_latest/grace_b2_rand_three_seed_11h'),
        ('B2-rand/validation-I15', 'B2-rand', '2026-11-06T15:22:02+00:00', '2026-11-07T00:12:11+00:00',
         'Runs-management/kaggle_outputs_20261107/b2_rand_seed44_validation_latest/grace_b2_rand_three_seed_11h'),
    ]
    result = []
    for sid, arm, lo, hi, folder in specs:
        group_rows = []
        for p in (R / folder).rglob('records.jsonl'):
            for r in records(p):
                if r.get('arm') == arm:
                    group_rows.append(r)
        window = {'start_utc': lo, 'end_utc': hi}
        # RUNS.md gives seconds, whereas records retain fractional seconds. Include
        # the recorded final second; this is a diagnostic match, not process proof.
        n = sum(time_value(lo) <= time_value(r['timestamp']) < time_value(hi) + timedelta(seconds=1)
                for r in group_rows if r.get('timestamp'))
        result.append({'session_id': sid, 'arm': arm, 'reported_window': window,
            'records_within_reported_window': n, 'reported_time_resolution_seconds': 1,
            'window_evidence': artifact(R / 'Runs-management/RUNS.md'),
            'verdict': 'REPORTED_WINDOW_MATCH_ONLY_NATIVE_SESSION_LOG_PENDING'})
    return result

def saved_notebooks():
    inputs = [
        ('B0/I03', 'B0', '02_Arm_B0_Source_Only/notebooks/02_kaggle_qwen_q4_b0.ipynb', '02_Arm_B0_Source_Only/output/kaggle_20261101_duchuynguyen1802/grace_b0_runs'),
        ('B1/I08', 'B1', '03_Arm_B1_Graph_Only/notebooks/02_kaggle_qwen_q4_b1_executed_I08.ipynb', '03_Arm_B1_Graph_Only/output/kaggle_run_02/grace_b1_runs'),
        ('B2/I05', 'B2', '01_Author_Baseline_Unified/notebooks/02_kaggle_qwen_q4_b2.ipynb', '01_Author_Baseline_Unified/output/local_full/inference_qwen_q4_b2_20261101/grace_b2_four_split_8h'),
        ('B2-flip/I10', 'B2-flip', '04_Arm_B2_Flip/notebooks/02_kaggle_qwen_q4_b2_flip.ipynb', '04_Arm_B2_Flip/output/kaggle_20261105_quangdung1111_run2'),
        ('B1-H2/Kaggle-validation', 'B1-H2', '11_Arm_B1H2_Evidence/notebooks/02_kaggle_qwen_q4_b1_h2_validation_20261106.ipynb', '11_Arm_B1H2_Evidence/kaggle_b1h2_validation_20261106/downloaded_output/b1_h2_validation'),
        ('B1-H2/Kaggle-test', 'B1-H2', '11_Arm_B1H2_Evidence/kaggle_b1h2_test_20261106/02_kaggle_qwen_q4_b1_h2_test_20261106.ipynb', 'Runs-management/kaggle_outputs_20261107/b1h2_test_latest/b1_h2_test'),
        ('B2-rand/validation', 'B2-rand', '06_Arm_B2_Rand/notebooks/02_kaggle_qwen_q4_b2_rand.ipynb', 'Runs-management/kaggle_outputs_20261107/b2_rand_seed44_validation_latest/grace_b2_rand_three_seed_11h'),
    ]
    result = []
    for sid, arm, path, recordroot in inputs:
        p = R / path
        nb = json.loads(p.read_bytes())
        text = notebook_output(nb)
        pm = nb.get('metadata', {}).get('papermill', {})
        win = {'start_utc': pm.get('start_time'), 'end_utc': pm.get('end_time')}
        groups = []
        for f in (R / recordroot).rglob('records.jsonl'):
            summary, rows = check_records(f)
            summary['within_saved_notebook_window'] = bound(rows, win)
            groups.append(summary)
        # The saved notebook source may have been edited after the recorded output.
        result.append({'session_id': sid, 'arm': arm, 'saved_notebook_window': win,
            'saved_output_chars': len(text), 'console': log_facts(text), 'record_groups': groups,
            'artifact': artifact(p), 'verdict': 'HISTORICAL_EVIDENCE_PARTIAL_NOT_FULL_LOCK',
            'warning': 'Saved output is evidence for its own session only; carried records outside this window are unbound. Current source alone is not runtime attestation.'})
    return result

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    inventory = candidate_inventory()
    reference_inventory()
    priority = priority_tests()
    validation = validation_archives()
    rand, merged = rand_test_sessions()
    saved = saved_notebooks()
    historical_b3 = legacy_b3_sessions()
    unbound_shuf = []
    for seed in (42, 43):
        for ds in ('devign', 'reveal'):
            summary, _ = check_records(R / f'runs/final/{ds}/validation/B1-shuf/{seed}/records.jsonl')
            summary['verdict'] = 'NO_MATCHING_SEED_SESSION_LOG_IN_REVIEWED_PACKAGE'
            unbound_shuf.append(summary)
    result = {'checked_at_utc': datetime.now(timezone.utc).isoformat(), 'scope': 'Local session artifacts; no cloud mutation, inference or threshold fitting',
        'priority_test_processes': priority, 'legacy_validation_processes': validation,
        'b2_rand_test_sessions': rand, 'b2_rand_final_groups': merged, 'historical_saved_notebooks': saved,
        'historical_b3': historical_b3, 'b1_shuf_validation_unbound_groups': unbound_shuf,
        'historical_report_windows': report_window_history(),
        'existing_acceptance_not_replaced': [
            'Runs-management/run_handoff_20261108/b1_full_runtime_acceptance.json',
            'Runs-management/b1_shuf_kaggle_output_20261109/RUNTIME_ACCEPTANCE_20261109.md',
            'Runs-management/b3_verified_patch_v1/threshold_release_20261109_v1/runtime_acceptance.json'],
        'pending_result_delivery': ['B3-new test: Dũng assigned, no new result accepted by this audit',
            'B3-nodiff: user reports executed, exact session artifacts not supplied locally',
            'B3-swap: deployed on thanhduy9a4tv; see b3_swap_launch_20261110 for live status, no runtime acceptance yet',
            'B3-flip: local preparation only, no score-producing session'],
        'inventory_files': len(inventory), 'inventory_distinct_file_hashes': len({x.get('sha256') for x in inventory if x.get('sha256')})}
    emit('SESSION_RECONCILIATION.json', result)
    emit('ARTIFACT_HASHES.json', list(MEMO.values()))
    print(json.dumps({'priority_processes': len(priority), 'priority_records': sum(x['records']['n'] for x in priority),
        'priority_binding': [(x['session_id'], x['records_in_process_window'], x['progress_rounded_score_matches'], x['session_install_and_build']['wheel_sha256']) for x in priority],
        'validation_binding': [(x['session_id'], [(g['dataset'], g['n'], g['records_in_this_process_window']) for g in x['record_groups']]) for x in validation],
        'rand_final_sources': [(x['session_id'], x['records_used_in_final_merge'], x['checks']) for x in rand],
        'inventory_files': len(inventory)}, indent=2))

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
