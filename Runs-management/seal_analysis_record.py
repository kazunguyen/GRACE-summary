"""Seal only the dated record and threshold code; leave branch HEAD/default index untouched."""
import json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];HERE=Path(__file__).parent
TAG='analysis-lock-20261101-v1'
def git(*args,env=None):
    return subprocess.check_output(['git','-C',str(ROOT),*args],text=True,env=env).strip()
existing=git('tag','--list',TAG)
if existing:raise SystemExit('Tag already exists; never rewrite the seal')
head=git('rev-parse','HEAD');index=HERE/'.analysis_seal.index'
if index.exists():raise SystemExit('Temporary seal index already exists; inspect before retrying')
env=os.environ.copy();env['GIT_INDEX_FILE']=str(index)
if not git('config','user.name'):
    env.update(GIT_AUTHOR_NAME='Codex',GIT_AUTHOR_EMAIL='codex@local.invalid',GIT_COMMITTER_NAME='Codex',GIT_COMMITTER_EMAIL='codex@local.invalid')
git('read-tree',head,env=env)
paths=['Runs-management/analysis_lock_20261101','Runs-management/validation_lock.py',
       'Runs-management/auto_lock_validation.py','Runs-management/test_validation_lock.py']
git('add','--',*paths,env=env)
tree=git('write-tree',env=env)
commit=git('commit-tree',tree,'-p',head,'-m','Record analysis plan after inference start; lock validation-only threshold rules',env=env)
git('tag','-a',TAG,commit,'-m','Dated analysis record after inference start; not retroactive preregistration',env=env)
assert git('rev-parse','HEAD')==head
if index.exists():index.unlink()
evidence={'tag':TAG,'commit':commit,'parent_head_unchanged':head,'sealed_at_utc':datetime.now(timezone.utc).isoformat(),
          'scope':paths,'registration_status':'local_dated_analysis_record_not_OSF_registration'}
(HERE/'analysis_git_seal.json').write_text(json.dumps(evidence,indent=2),encoding='utf-8')
print(json.dumps(evidence,indent=2))
