"""Audit the proposed Git index without printing credentials or file bodies."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]
GIT=['git','-c','safe.directory='+ROOT.as_posix()]
def git(*args):return subprocess.check_output(GIT+list(args),cwd=ROOT)
assert git('branch','--show-current').decode().strip()=='hieu','Refuse commit on an unexpected/protected branch'
names=[p.decode('utf-8') for p in git('diff','--cached','--name-only','-z').split(b'\0') if p]
keys=[]
for p in (ROOT/'Runs-management').glob('kaggle_*_config/kaggle.json'):
    value=json.loads(p.read_text(encoding='utf-8')).get('key')
    if value:keys.append(value.encode())
forbidden=[];secrets=[];oversized=[]
patterns=[rb'KGAT_[A-Za-z0-9_-]{25,}',rb'ghp_[A-Za-z0-9]{30,}',rb'github_pat_[A-Za-z0-9_]{40,}',rb'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----',rb'X-Goog-Signature=[A-Za-z0-9]+',rb'X-Amz-Signature=[A-Za-z0-9]+']
for name in names:
    if (name.startswith(('configs/','data/specs/','Runs-management/osf_registration_draft_20261102/')) or name=='preregistration.md'
        or '/tooling/' in name or '/inputs/' in name or '/remote_output/' in name or '/local_test_tmp/' in name
        or name.endswith(('train_raw.jsonl','train_manifest.jsonl','candidate_pairs.jsonl','donor_index.jsonl','kaggle.json'))):forbidden.append(name)
    raw=git('show',':'+name)
    if any(key in raw for key in keys) or any(re.search(pattern,raw) for pattern in patterns):secrets.append(name)
    if len(raw)>=50*1024*1024:oversized.append({'path':name,'bytes':len(raw)})
summary=json.loads((ROOT/'Runs-management/run_handoff_20261108/completed_results_summary.json').read_text(encoding='utf-8'))
checked=0
for arm in summary['arms']:
    for dataset in arm['datasets']:
        for ref in dataset['files']:
            assert ref['path'].replace('\\','/') in names,'Missing result file in Git index'
            assert hashlib.sha256(git('show',':'+ref['path'].replace('\\','/'))).hexdigest()==ref['sha256'],'Git index changed result bytes'
            checked+=1
assert not forbidden, 'Forbidden paths staged: '+str(forbidden)
assert not secrets, 'Potential credentials/signed download URL found in staged paths: '+str(secrets)
assert not oversized, 'Oversized staged files: '+str(oversized)
print(json.dumps({'branch':'hieu','staged_files':len(names),'exact_result_files_checked':checked,'result_records':15018,
    'known_credential_values_checked':len(keys),'forbidden_paths':forbidden,'credential_hits':secrets,'oversized_files':oversized,'passed':True}),flush=True)
