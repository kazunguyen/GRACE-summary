"""Rà soát độc lập 28 dòng B2 / Devign / validation / seed 42 inference lại sau khi đổi donor.

Chạy:
    python verify_donor28.py <csv phiếu của Dũng> <runs/final của gói Option1> <worker I09 trong gói> <csv đầu ra>

Không dùng script tạo phiếu của Dũng, mà tự đọc lại từ nguồn gốc:
- Donor cũ: demonstrations[0] trong specs.jsonl của bundle legacy (bundles_recovered_joern_final_20261031),
  tức nguồn mà reconcile_donor_prompts.py dùng để dựng kho donor cũ.
- Donor mới: research_freeze_20261101/devign/donors.jsonl và cache/devign_new_bank.jsonl.
- Prompt cũ/mới: prompts.jsonl của bundle legacy và new_reference/B2/devign/validation/prompts.jsonl; hash lại văn bản prompt.
- Score: records run3 (cũ) và b2_donor_rerun_66 (mới); tính lại s = sigmoid(logprob_1 - logprob_0).
- Canonical: runs/final/devign/validation/B2/42/records.jsonl của gói.
- Ngưỡng: khóa lại MCC trên lưới validation từ bản canonical và so với thresholds.json của lượt rerun.
"""
import csv
import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parents[3]
PACKET, FINAL, WORKER, OUT = (Path(a) for a in sys.argv[1:5])

LEG = ROOT / '01_Author_Baseline_Unified/output/local_full/bundles_recovered_joern_final_20261031/devign/validation'
NEWREF = ROOT / 'Runs-management/donor_reconciliation_20261101/new_reference/B2/devign/validation/prompts.jsonl'
FROZEN = ROOT / '01_Author_Baseline_Unified/output/research_freeze_20261101/devign/donors.jsonl'
NEWBANK = ROOT / 'Runs-management/donor_reconciliation_20261101/cache/devign_new_bank.jsonl'
RECON = ROOT / 'Runs-management/donor_reconciliation_20261101/mau_can_inference_lai_CURRENT.csv'
REGISTERED = ROOT / 'configs/thresholds.json'
DRIVE_MANIFEST = 'Runs-management/b2_rand_drive_manifest_20261102.json'
RUN_MANIFEST = 'Runs-management/kaggle_outputs_20261105/b2_rand/grace_b2_rand_three_seed_11h/b2_donor_rerun_66/devign/validation/run_manifest.json'
TAU = 0.70


def sha_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def sha_text(s):
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


def jsonl(p, ids=None, key='id'):
    out = {}
    with open(p, encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            if ids is not None and not any(f'"{i}"' in line for i in ids):
                continue
            r = json.loads(line)
            if ids is None or str(r[key]) in ids:
                out[str(r[key])] = r
    return out


def close(a, b, tol=1e-12):
    return abs(float(a) - float(b)) <= tol * max(1.0, abs(float(a)), abs(float(b)))


rows = list(csv.DictReader(open(PACKET, encoding='utf-8-sig')))
fields = list(rows[0])
ids = {r['target_id'] for r in rows}
assert len(rows) == 28 and len(ids) == 28, 'packet must have 28 distinct targets'

# --- file-level checks --------------------------------------------------------------------
r0 = rows[0]
file_checks = {}


def git_bytes(path):
    # Blob đã commit (LF). Bản checkout trên Windows có thể bị đổi CRLF nên không băm bản trên đĩa.
    return subprocess.run(['git', '-C', str(ROOT), 'show', f'HEAD:{path}'], capture_output=True, check=True).stdout


for col, path_col in (('old_records_sha256', 'old_record_source'), ('new_rerun_records_sha256', 'new_rerun_records_source'),
                      ('rerun_threshold_lock_sha256', 'rerun_threshold_lock_source')):
    assert len({r[col] for r in rows}) == 1 and len({r[path_col] for r in rows}) == 1
    file_checks[f'{col} (git blob)'] = hashlib.sha256(git_bytes(r0[path_col])).hexdigest() == r0[col]
file_checks['rerun_worker_sha256 (package I09 file)'] = len({r['rerun_worker_sha256'] for r in rows}) == 1 and sha_file(WORKER) == r0['rerun_worker_sha256']

# Manifest Drive B2-rand commit ngày 02/11 (c245664): worker, records rerun, lock và bundle cùng một output Kaggle kaggle_run_01
drive = {f['path'].split('kaggle_run_01/')[-1]: f['sha256'] for f in json.loads(git_bytes(DRIVE_MANIFEST))['files'] if 'kaggle_run_01/' in f['path']}
file_checks['drive_manifest: worker = rerun_worker_sha256'] = drive.get('kaggle_inference.py') == r0['rerun_worker_sha256']
file_checks['drive_manifest: rerun records = new_rerun_records_sha256'] = drive.get('grace_b2_rand_three_seed_11h/b2_donor_rerun_66/devign/validation/records.jsonl') == r0['new_rerun_records_sha256']
file_checks['drive_manifest: thresholds = rerun_threshold_lock_sha256'] = drive.get('grace_b2_rand_three_seed_11h/b2_donor_rerun_66/thresholds.json') == r0['rerun_threshold_lock_sha256']
runm = json.loads(git_bytes(RUN_MANIFEST))
file_checks['drive_manifest: bundle = run_manifest.bundle_sha256'] = drive.get('grace_b2_rand_bundles/donor_rerun_devign_validation.zip') == runm['bundle_sha256']
file_checks['run_manifest: B2 devign validation seed 42, model f6050b4d'] = (runm['arm'], runm['dataset'], runm['split'], runm['prompt_seed'], runm['model_sha256']) == ('B2', 'devign', 'validation', 42, 'f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335')
thr = json.load(open(ROOT / r0['rerun_threshold_lock_source'], encoding='utf-8'))['entries']['B2/devign']
file_checks['lock_tau_0.70'] = close(thr['tau'], TAU)
file_checks['lock_cites_rerun_records'] = thr['source_evidence'][0]['rerun_validation_records_sha256'] == r0['new_rerun_records_sha256']
reg = json.load(open(REGISTERED, encoding='utf-8'))
reg_tau = reg['thresholds'].get('devign|B2|42')
file_checks['registered_tau_0.70 (configs/thresholds.json devign|B2|42)'] = reg_tau is not None and close(reg_tau, TAU)

# --- load sources --------------------------------------------------------------------------
old_recs = jsonl(ROOT / r0['old_record_source'])
new_recs = jsonl(ROOT / r0['new_rerun_records_source'])
canon = jsonl(FINAL / 'devign/validation/B2/42/records.jsonl')
leg_specs = jsonl(LEG / 'specs.jsonl', ids)
leg_prompts = jsonl(LEG / 'prompts.jsonl', ids)
new_prompts = jsonl(NEWREF, ids)
new_ids = {r['new_donor_id'] for r in rows}
old_ids = {r['old_donor_id'] for r in rows}
frozen = jsonl(FROZEN, new_ids | old_ids, key='function_uid')
newbank = jsonl(NEWBANK, new_ids | old_ids)
recon = {r['id']: r for r in csv.DictReader(open(RECON, encoding='utf-8-sig')) if r['dataset'] == 'devign' and r['split'] == 'validation'}

file_checks['new_rerun_has_exactly_28_ids'] = set(new_recs) == ids
# prompts.jsonl trong bundle rerun = 28 dòng new_reference theo thứ tự records, json.dumps(...)+'\n'
newref_lines = {json.loads(l)['id']: l for l in git_bytes('Runs-management/donor_reconciliation_20261101/new_reference/B2/devign/validation/prompts.jsonl').decode('utf-8').splitlines() if l.strip()}
bundle_bytes = ''.join(json.dumps(json.loads(newref_lines[i])) + '\n' for i in new_recs).encode('utf-8')
file_checks['bundle prompt_set_sha256 rebuilt from new_reference'] = hashlib.sha256(bundle_bytes).hexdigest() == runm['prompt_set_sha256']

# Năm bản output cũ (theo mau_can_inference_lai_CURRENT.csv): cùng prompt và score cho 28 dòng
five_ok = True
for i in ids:
    srcs = json.loads(next(r for r in csv.DictReader(open(RECON, encoding='utf-8-sig')) if r['id'] == i and r['split'] == 'validation')['source_record_paths'])
    if i == next(iter(ids)):
        five_sources = srcs
    five_ok &= len(srcs) == 5
five = [jsonl(ROOT / p, ids) for p in five_sources]
file_checks['five legacy outputs agree on the 28 rows'] = five_ok and all(
    len({(f[i]['prompt_sha256'], f[i]['s'], f[i]['logprob_0'], f[i]['logprob_1']) for f in five}) == 1 for i in ids)
file_checks['canonical_n_2732'] = len(canon) == 2732 and set(canon) == set(old_recs)

# canonical: the other 2,704 rows must equal run3 (score + prompt), the 28 must equal the rerun
others_same = all(canon[i]['prompt_sha256'] == old_recs[i]['prompt_sha256'] and canon[i]['s'] == old_recs[i]['s']
                  for i in canon if i not in ids)
file_checks['canonical_other_2704_equal_run3'] = others_same

# threshold re-lock from canonical scores (validation MCC grid, ties -> lowest threshold)
y = np.array([int(canon[i]['label']) for i in canon])
s = np.array([float(canon[i]['s']) for i in canon])


def mcc(yy, pp):
    tp = int(((pp == 1) & (yy == 1)).sum()); tn = int(((pp == 0) & (yy == 0)).sum())
    fp = int(((pp == 1) & (yy == 0)).sum()); fn = int(((pp == 0) & (yy == 1)).sum())
    d = math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    return 0.0 if d == 0 else (tp * tn - fp * fn) / d


grid = [round(0.01 * k, 2) for k in range(1, 100)]
scores = [(mcc(y, (s >= t).astype(int)), t) for t in grid]
best = max(scores, key=lambda x: (x[0], -x[1]))
file_checks['relock_from_canonical_tau'] = close(best[1], TAU)
file_checks['relock_mcc_matches_lock'] = abs(best[0] - thr['validation_mcc']) < 1e-12

# code hash convention: find which normalisation reproduces packet's new_donor_code_sha256
conv = {'raw': lambda c: c, 'strip': lambda c: c.strip()}
conv_hit = {k: sum(sha_text(f(frozen[r['new_donor_id']]['func'])) == r['new_donor_code_sha256'] for r in rows if r['new_donor_id'] in frozen)
            for k, f in conv.items()}
code_norm = conv[max(conv_hit, key=conv_hit.get)]

# --- per-row checks ------------------------------------------------------------------------
out_rows = []
summary = {'PASS': 0, 'FAIL': 0, 'UNVERIFIABLE': 0}
for r in rows:
    i = r['target_id']; fails = []; notes = []
    o, n, c, sp = old_recs.get(i), new_recs.get(i), canon.get(i), leg_specs.get(i)
    lp, np_ = leg_prompts.get(i), new_prompts.get(i)
    if None in (o, n, c, sp, lp, np_):
        out_rows.append(dict(r, review_verdict_PASS_FAIL_UNVERIFIABLE='UNVERIFIABLE', reviewer_note_and_evidence='missing source row'))
        summary['UNVERIFIABLE'] += 1
        continue

    def chk(name, ok):
        if not ok:
            fails.append(name)

    # label
    chk('target_label', int(r['target_label']) == int(o['label']) == int(n['label']) == int(c['label']) == int(sp['label']))
    # old donor
    od = sp['demonstrations'][0]
    chk('old_donor_id', r['old_donor_id'] == od['function_uid'] == o['demo_ids'][0] == sp['retrieval_metadata']['demo_id'])
    chk('old_donor_label', int(r['old_donor_label']) == int(od['target']))
    chk('old_donor_code_sha256', sha_text(code_norm(od['func'])) == r['old_donor_code_sha256'])
    in_new = r['old_donor_id'] in newbank
    # new donor
    nd = frozen.get(r['new_donor_id']); nb = newbank.get(r['new_donor_id'])
    chk('new_donor_in_frozen_bank', nd is not None and nb is not None)
    if nd is not None:
        chk('new_donor_label', int(r['new_donor_label']) == int(nd['target']) == int(nb['target']))
        chk('new_donor_code_sha256', sha_text(code_norm(nd['func'])) == r['new_donor_code_sha256'] and nd['func'] == nb['func'])
    chk('new_donor_id_in_rerun', n['demo_ids'] == [r['new_donor_id']] and c['demo_ids'] == [r['new_donor_id']])
    # reconciliation table
    rc = recon.get(i)
    chk('reconciliation_row', rc is not None and rc['old_demo_id'] == r['old_donor_id'] and rc['new_demo_id'] == r['new_donor_id']
        and rc['old_prompt_sha256'] == r['old_prompt_sha256'] and rc['new_prompt_sha256'] == r['new_prompt_sha256'])
    # prompts
    chk('old_prompt_sha256', sha_text(lp['prompt']) == r['old_prompt_sha256'] == o['prompt_sha256'])
    chk('new_prompt_sha256', sha_text(np_['prompt']) == r['new_prompt_sha256'] == n['prompt_sha256'] == c['prompt_sha256'])
    ow = 'Vulnerable' if int(od['target']) else 'Non-vulnerable'
    nw = 'Vulnerable' if nd is not None and int(nd['target']) else 'Non-vulnerable'
    chk('old_prompt_contains_old_donor', f'it is {ow}.\n' in lp['prompt'] and od['func'].strip()[:120] in lp['prompt'])
    chk('new_prompt_contains_new_donor', nd is not None and f'it is {nw}.\n' in np_['prompt'] and nd['func'].strip()[:120] in np_['prompt'])
    # phần trước demonstration (role, target code, câu hỏi, node, edge) giữ nguyên; chỉ đoạn donor đổi
    chk('prompt_prefix_unchanged', lp['prompt'].split('\n\nThe following is an example')[0] == np_['prompt'].split('\n\nThe following is an example')[0])
    # scores
    for side, rec in (('old', o), ('new', n)):
        chk(f'{side}_logprob_0', close(r[f'{side}_logprob_0'], rec['logprob_0']))
        chk(f'{side}_logprob_1', close(r[f'{side}_logprob_1'], rec['logprob_1']))
        chk(f'{side}_s', close(r[f'{side}_s'], rec['s']))
        sig = 1.0 / (1.0 + math.exp(-(rec['logprob_1'] - rec['logprob_0'])))
        chk(f'{side}_s_recomputed', close(sig, rec['s'], 1e-9))
        chk(f'{side}_valid', rec.get('valid') is True and rec.get('model_sha256') == 'f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335')
        chk(f'{side}_decision', int(r[f'{side}_decision_at_registered_tau']) == int(rec['s'] >= TAU))
        chk(f'{side}_argmax', int(r[f'{side}_pred_argmax']) == int(rec['pred_argmax']) == int(rec['logprob_1'] > rec['logprob_0']))
    chk('delta_s', close(r['delta_s_new_minus_old'], n['s'] - o['s'], 1e-9))
    chk('decision_changed_flag', (r['threshold_decision_changed'] == 'True') == ((o['s'] >= TAU) != (n['s'] >= TAU)))
    chk('argmax_changed_flag', (r['argmax_changed'] == 'True') == (o['pred_argmax'] != n['pred_argmax']))
    chk('tau_columns', close(r['registered_threshold_tau'], TAU) and close(r['rerun_locked_threshold_tau'], TAU))
    # canonical = rerun record
    keys = ('prompt_sha256', 'logprob_0', 'logprob_1', 's', 'pred_argmax', 'demo_ids', 'model_sha256', 'raw')
    chk('canonical_equals_rerun', all(c.get(k) == n.get(k) for k in keys))
    chk('canonical_differs_from_run3', c['prompt_sha256'] != o['prompt_sha256'])

    if not in_new:
        notes.append('donor cũ không còn trong kho mới (đã loại khi làm sạch)')
    verdict = 'FAIL' if fails else 'PASS'
    summary[verdict] += 1
    ev = (f"Donor cũ {r['old_donor_id']} (nhãn {od['target']}): khớp id/nhãn/sha256(func) với demonstrations[0] trong "
          f"bundles_recovered_joern_final_20261031/devign/validation/specs.jsonl và demo_ids của run3. "
          f"Donor mới {r['new_donor_id']} (nhãn {nd['target'] if nd else '?'}): khớp research_freeze_20261101/devign/donors.jsonl, "
          f"cache/devign_new_bank.jsonl, demo_ids của rerun và canonical. "
          f"Prompt cũ: sha256 văn bản trong prompts.jsonl legacy = old_prompt_sha256 = run3. "
          f"Prompt mới: sha256 văn bản trong new_reference/B2/devign/validation/prompts.jsonl = new_prompt_sha256 = rerun = canonical; "
          f"phần trước demonstration giữ nguyên, chỉ thay đoạn donor. "
          f"Score: logprob/s cũ khớp run3, mới khớp rerun 794aa82b; s tính lại = sigmoid(logprob_1 - logprob_0). "
          f"Quyết định τ=0,70: {int(o['s'] >= TAU)}→{int(n['s'] >= TAU)}; argmax {o['pred_argmax']}→{n['pred_argmax']}. "
          f"Canonical runs/final/devign/validation/B2/42 trùng record rerun ở {len(keys)} trường.")
    if notes:
        ev += '; ' + '; '.join(notes)
    if fails:
        ev += '; SAI KHÁC: ' + ', '.join(fails)
    out_rows.append(dict(r, review_verdict_PASS_FAIL_UNVERIFIABLE=verdict, reviewer_note_and_evidence=ev))

print('code hash convention hits:', conv_hit)
print('file checks:'); [print(f'  {"OK " if v else "BAD"} {k}') for k, v in file_checks.items()]
print('relock:', best)
print('rows:', summary)
print('decision changed:', sum(r['threshold_decision_changed'] == 'True' for r in rows), 'argmax changed:', sum(r['argmax_changed'] == 'True' for r in rows),
      'score changed:', sum(not close(r['old_s'], r['new_s'], 0) for r in rows))
for r in out_rows:
    if r['review_verdict_PASS_FAIL_UNVERIFIABLE'] != 'PASS':
        print(r['target_id'], r['reviewer_note_and_evidence'][-300:])
OUT.parent.mkdir(parents=True, exist_ok=True)
with open(OUT, 'w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(out_rows)
json.dump({'file_checks': file_checks, 'relock': {'tau': best[1], 'mcc': best[0]}, 'rows': summary, 'code_hash_convention_hits': conv_hit},
          open(OUT.with_suffix('.summary.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('wrote', OUT)
