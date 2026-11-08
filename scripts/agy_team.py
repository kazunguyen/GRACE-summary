"""Run a scoped worker through AGY CLI and keep a reviewable local ledger.

No GPT subagents or fallback backend. Prompts are files, never shell strings.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

ROOT=Path(__file__).resolve().parents[1]
DEFAULT_BATCH=ROOT/'Runs-management/agy_b3_discovery_20261108'

def utc():return datetime.now(timezone.utc).isoformat()
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for raw in iter(lambda:stream.read(1024*1024),b''):h.update(raw)
    return h.hexdigest()
def write(path,value):
    path=Path(path);tmp=path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    os.replace(tmp,path)

def cli():
    found=shutil.which('agy') or shutil.which('agy.exe')
    path=Path(found) if found else Path(os.environ.get('LOCALAPPDATA','C:/Users/ADMIN/AppData/Local'))/'agy/bin/agy.exe'
    if not path.is_file():raise FileNotFoundError('AGY CLI not found; no fallback backend is allowed')
    return str(path)

def run(batch,task,timeout):
    batch=Path(batch).resolve();job=(batch/'workers'/task).resolve()
    if not job.is_relative_to(batch/'workers'):raise ValueError('Unsafe task path')
    prompt=job/'TASK.md';inputs=job/'input_manifest.json'
    spec=json.loads((batch/'team.json').read_text(encoding='utf-8'))
    if task not in spec['tasks']:raise ValueError('Unknown task')
    ledger=job/'execution.json'
    if ledger.exists():raise ValueError('Preserve prior execution; use a new task or explicit follow-up')
    inventory=json.loads(inputs.read_text(encoding='utf-8'))
    for ref in inventory:
        if sha(job/ref['path'])!=ref['sha256']:raise ValueError('Input snapshot changed')
    command=[cli(),'--new-project','--model',spec['model'],'--mode','plan','--disable-slash-commands',
        '--output-format','json','--print-timeout',str(timeout)+'s',
        '--log-file',str(job/'agy.cli.log'),'--print',prompt.read_text(encoding='utf-8')]
    state=dict(task=task,backend='agy',model=spec['model'],started_at=utc(),state='running',
        prompt_sha256=sha(prompt),input_manifest_sha256=sha(inputs),review_status='pending')
    write(ledger,state)
    started=time.monotonic()
    try:
        with (job/'stdout.json').open('w',encoding='utf-8') as out,(job/'stderr.log').open('w',encoding='utf-8') as err:
            proc=subprocess.Popen(command,cwd=job,stdout=out,stderr=err,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            state['pid']=proc.pid;write(ledger,state)
            try:state['returncode']=proc.wait(timeout=timeout+90)
            except subprocess.TimeoutExpired:
                proc.terminate()
                try:proc.wait(timeout=15)
                except subprocess.TimeoutExpired:proc.kill();proc.wait()
                state['state']='timed_out';raise
        raw=(job/'stdout.json').read_text(encoding='utf-8').strip()
        response=json.loads(raw)
        state.update(agy_status=response.get('status'),conversation_id=response.get('conversation_id'),usage=response.get('usage'))
        denied=response.get('denied_actions',[])
        state['denied_actions']=denied
        state['state']='completed' if response.get('status')=='SUCCESS' and not denied and response.get('response','').strip() else 'blocked_or_empty'
        if state['state']=='completed' and spec.get('delivery_mode')=='response_files':
            body=response['response'].strip()
            if body.startswith('```'):body='\n'.join(body.splitlines()[1:-1])
            package=json.loads(body)
            artifacts=package.get('files',[])
            if not artifacts:raise ValueError('No deliverable files in response')
            for artifact in artifacts:
                path=(job/'outputs'/artifact['path']).resolve()
                if not path.is_relative_to((job/'outputs').resolve()):raise ValueError('Unsafe response output path')
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_text(artifact['content'],encoding='utf-8')
            state['worker_summary']=package.get('summary','')
        if state['state']!='completed':state['error']='AGY did not return SUCCESS; inspect retained response/logs'
    except Exception as exc:
        if state['state']!='timed_out':state['state']='failed'
        state['error']=type(exc).__name__+': '+str(exc)[:300]
    finally:
        changed=[ref['path'] for ref in inventory if not (job/ref['path']).is_file() or sha(job/ref['path'])!=ref['sha256']]
        state.update(finished_at=utc(),elapsed_seconds=round(time.monotonic()-started,3),changed_inputs=changed,
            outputs=[dict(path=str(p.relative_to(job)),sha256=sha(p),bytes=p.stat().st_size) for p in sorted((job/'outputs').rglob('*')) if p.is_file()])
        if changed:state['state']='rejected_input_mutation'
        write(ledger,state)
    print(json.dumps(state,ensure_ascii=False),flush=True)
    return 0 if state['state']=='completed' else 1

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('task');parser.add_argument('--batch',type=Path,default=DEFAULT_BATCH)
    parser.add_argument('--timeout',type=int,default=1200)
    args=parser.parse_args();raise SystemExit(run(args.batch,args.task,args.timeout))
