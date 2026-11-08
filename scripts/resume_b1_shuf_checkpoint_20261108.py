"""Verify and resume B1-shuf with unchanged run identity on an available account."""
import argparse
import ast
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import shutil
import sys
from zipfile import ZipFile

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'Runs-management/locked_continuations_20261108'
PARENT=BASE/'b1_shuf'
OWNER='huuhieu3333'
KIND='b1_shuf_resume_huuhieu3333_20261108_v2'
STAGE=BASE/KIND
CHECKPOINT='b1_shuf_locked_20261108_checkpoint.zip'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,value):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_bytes((json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
def read(p):return json.loads(p.read_text(encoding='utf-8'))

def prepare():
    if STAGE.exists():raise FileExistsError('Preserve existing resume delivery; inspect it instead')
    parent_delivery=read(PARENT/'delivery.json')
    remote=PARENT/'remote_output';run=remote/'b1_shuf_locked_20261108'
    status=read(run/'status.json');identity=read(run/'run_identity.json')
    assert status['state'] in ('timed_out','complete')
    assert identity['input_manifest_sha256']==parent_delivery['input_manifest_sha256']
    contract=read(run/'inference_runtime_lock.json');contract_sha=sha(run/'inference_runtime_lock.json')
    assert identity['runtime_contract_sha256']==contract_sha
    source_spec=importlib.util.spec_from_file_location('frozen_shuf_worker',remote/'kaggle_inference.py')
    worker=importlib.util.module_from_spec(source_spec);source_spec.loader.exec_module(worker)
    assert sha(remote/'kaggle_inference.py')==parent_delivery['worker_sha256']
    bundle=next((PARENT/'dataset').glob('*.zip'))
    assert sha(bundle)==parent_delivery['bundle_sha256']
    manifest,groups,legacy=worker.load_inputs(PARENT/'dataset',bundle.name,parent_delivery['input_manifest_sha256'])
    manifest['_manifest_sha256']=parent_delivery['input_manifest_sha256']
    checkpoint=remote/CHECKPOINT
    result={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'parent_kernel':parent_delivery['ref'],
        'checkpoint_sha256':sha(checkpoint),'input_manifest_sha256':parent_delivery['input_manifest_sha256'],
        'runtime_contract_sha256':contract_sha,'groups':[],'provenances':{}}
    seen_prov=set();total=0
    with ZipFile(checkpoint) as z:
        assert z.testzip() is None
        assert json.loads(z.read('run_identity.json'))==identity
        for n in z.namelist():
            assert not Path(n).is_absolute() and '..' not in Path(n).parts
        for g,prompts in groups:
            group=f"{g['arm']}/seed_{g['seed']}/{g['dataset']}/{g['split']}"
            member=group+'/records.jsonl';p=run/member
            raw=p.read_bytes() if p.exists() else b''
            if member in z.namelist():assert z.read(member)==raw
            else:assert not raw
            saved=worker.jsonl(raw);lookup={r['id']:r for r in prompts}
            assert len(saved)==len({r['id'] for r in saved})==status['groups'][group]
            for row in saved:
                worker.validate_saved(row,lookup[row['id']],g,manifest,legacy,contract_sha,run)
                assert row['seed']==g['seed'] and row['tau']==g['tau'] and row['pred_tau']==int(row['s']>=g['tau'])
                a,b=row['logprob_0'],row['logprob_1'];mx=max(a,b)
                score=math.exp(b-mx)/(math.exp(a-mx)+math.exp(b-mx))
                assert abs(row['s']-score)<1e-12
                assert row['tokens']['total']+64<=8192 and row['tokenizer_revision']==contract['tokenizer']['revision']
                pp=run/row['runtime_provenance']
                if pp not in seen_prov:
                    info=read(pp);assert info['constructor']==contract['constructor']
                    assert info['model_sha256']==manifest['model_sha256']
                    assert all(info['packages'].get(k)==v for k,v in contract['packages'].items())
                    assert sha(remote/'grace_runtime_contract.py')==info['runtime_helper_sha256']
                    log=(pp.parent/'model_load_offload.log').read_text(encoding='utf-8')
                    assert 'offloaded 49/49 layers to GPU' in log
                    assert all(f'using device CUDA{i} (Tesla T4)' in log for i in (0,1))
                    result['provenances'][pp.relative_to(run).as_posix()]={'sha256':sha(pp),'runtime_checks_pass':True}
                    seen_prov.add(pp)
            total+=len(saved);result['groups'].append({'group':group,'done':len(saved),'target':len(prompts),'remaining':len(prompts)-len(saved)})
        result['total_done']=total;result['total_target']=sum(len(ps) for _,ps in groups)
        result['remaining']=result['total_target']-total
        assert result['remaining']>0
    STAGE.mkdir()
    data=STAGE/'dataset';data.mkdir();shutil.copyfile(checkpoint,data/CHECKPOINT)
    # Original private prompt dataset belongs to another account: republish the
    # exact same bundle bytes with the checkpoint under this authorized account.
    shutil.copyfile(bundle,data/bundle.name)
    assert sha(data/bundle.name)==parent_delivery['bundle_sha256']
    dataset=OWNER+'/grace-b1-shuf-checkpoint-20261108'
    dump(data/'dataset-metadata.json',{'id':dataset,'title':'GRACE B1 shuf locked checkpoint 20261108','licenses':[{'name':'CC0-1.0'}],'isPrivate':True})
    notebook=read(PARENT/'kernel/notebook.ipynb')
    assert sha(PARENT/'kernel/notebook.ipynb')==parent_delivery['notebook_sha256']
    notebook['cells'][0]['source']=['# B1-shuf checkpoint continuation\n\nResume the same locked run; skip verified saved IDs; no threshold/prompt changes.\n']
    # PI selected this account despite its short remaining quota. End the
    # session at 90 minutes, keeping the worker's five-minute export reserve.
    settings=''.join(notebook['cells'][2]['source'])
    assert 'MAX_RUNTIME_HOURS = 9' in settings
    notebook['cells'][2]['source']=settings.replace('MAX_RUNTIME_HOURS = 9','MAX_RUNTIME_HOURS = 1.5').splitlines(keepends=True)
    # Kaggle may unpack uploaded ZIPs. Pin every original checkpoint member so
    # directory delivery is accepted only with the same authenticated bytes.
    with ZipFile(checkpoint) as z:
        checkpoint_files={name:hashlib.sha256(z.read(name)).hexdigest() for name in z.namelist() if not name.endswith('/')}
    restore="EXPECTED_CHECKPOINT_FILES = "+repr(checkpoint_files)+"\nEXPECTED_CHECKPOINT_SHA = "+repr(result['checkpoint_sha256'])+"\n"+'''
checkpoints = list(KAGGLE_INPUT_ROOT.rglob(CHECKPOINT_NAME))
if len(checkpoints) > 1: raise ValueError('Ambiguous checkpoint ZIP inputs')
OUT_ROOT.mkdir(parents=True, exist_ok=True)
if checkpoints:
    if hashlib.sha256(checkpoints[0].read_bytes()).hexdigest() != EXPECTED_CHECKPOINT_SHA:
        raise ValueError('Checkpoint ZIP hash mismatch')
    with zipfile.ZipFile(checkpoints[0]) as z:
        if z.testzip() is not None: raise ValueError('Checkpoint CRC failure')
        if {n for n in z.namelist() if not n.endswith('/')} != set(EXPECTED_CHECKPOINT_FILES):
            raise ValueError('Checkpoint member set mismatch')
        for name, expected in EXPECTED_CHECKPOINT_FILES.items():
            target = (OUT_ROOT / name).resolve()
            if not target.is_relative_to(OUT_ROOT.resolve()): raise ValueError('Unsafe checkpoint path')
            if hashlib.sha256(z.read(name)).hexdigest() != expected: raise ValueError('Checkpoint member hash mismatch')
        identity = json.loads(z.read('run_identity.json'))
        if identity['input_manifest_sha256'] != MANIFEST_SHA or identity['runtime_contract_sha256'] != EXPECTED_CONTRACT_SHA256:
            raise ValueError('Checkpoint identity mismatch')
        z.extractall(OUT_ROOT)
    note('Restored approved checkpoint from ZIP; fresh restart forbidden')
else:
    roots = [p.parent for p in KAGGLE_INPUT_ROOT.rglob('run_identity.json')
             if hashlib.sha256(p.read_bytes()).hexdigest() == EXPECTED_CHECKPOINT_FILES['run_identity.json']]
    if len(roots) != 1: raise ValueError('Exactly one verified unpacked checkpoint is REQUIRED; fresh restart forbidden')
    checkpoint_root = roots[0]
    for name, expected in EXPECTED_CHECKPOINT_FILES.items():
        source = (checkpoint_root / name).resolve()
        if not source.is_relative_to(checkpoint_root.resolve()) or not source.is_file(): raise ValueError('Missing/unsafe checkpoint member')
        if hashlib.sha256(source.read_bytes()).hexdigest() != expected: raise ValueError('Unpacked checkpoint member hash mismatch: '+name)
    identity = json.loads((checkpoint_root / 'run_identity.json').read_bytes())
    if identity['input_manifest_sha256'] != MANIFEST_SHA or identity['runtime_contract_sha256'] != EXPECTED_CONTRACT_SHA256:
        raise ValueError('Unpacked checkpoint identity mismatch')
    for name in EXPECTED_CHECKPOINT_FILES:
        target = (OUT_ROOT / name).resolve()
        if not target.is_relative_to(OUT_ROOT.resolve()): raise ValueError('Unsafe checkpoint output')
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(checkpoint_root / name, target)
    note('Restored approved checkpoint from Kaggle-unpacked files; all member hashes match')
print('Approved checkpoint restored; input manifest:', MANIFEST_SHA)
'''
    notebook['cells'][3]['source']=restore.splitlines(keepends=True)
    for i,cell in enumerate(notebook['cells']):
        if cell['cell_type']=='code':
            ast.parse(''.join(cell['source']),filename=f'resume:cell{i}')
            cell['execution_count']=None;cell['outputs']=[]
    embedded=next(n.args[0].value for n in ast.walk(ast.parse(''.join(notebook['cells'][7]['source']))) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='write_text')
    assert hashlib.sha256(embedded.encode()).hexdigest()==parent_delivery['worker_sha256']
    kernel=STAGE/'kernel';kernel.mkdir();dump(kernel/'notebook.ipynb',notebook)
    metadata=deepcopy(read(PARENT/'kernel/kernel-metadata.json'))
    metadata.update(id=OWNER+'/grace-b1-shuf-resume-20261108',title='grace-b1-shuf-resume-20261108',dataset_sources=[dataset],kernel_sources=[OWNER+'/qwen3coder30b-prepare-notebook'],session_timeout_seconds=5400)
    dump(kernel/'kernel-metadata.json',metadata)
    delivery={**parent_delivery,'kind':KIND,'owner':OWNER,'ref':metadata['id'],'dataset':dataset,'stage':STAGE.relative_to(ROOT).as_posix(),
        'notebook_sha256':sha(kernel/'notebook.ipynb'),'bundle_sha256':sha(data/CHECKPOINT),
        'total':result['total_target'],'new_target':result['remaining'],'resume_count':total,
        'parent_ref':parent_delivery['ref'],'checkpoint_sha256':result['checkpoint_sha256'],
        'original_prompt_dataset':parent_delivery['dataset'],'legacy_count':0,
        'account_change_reason':'Original account GPU quota exhausted; PI explicitly selected huuhieu3333 and authorized transfer there. Short session fits remaining quota.',
        'max_runtime_hours':1.5,'requested_session_timeout_seconds':5400,
        'original_bundle_sha256':parent_delivery['bundle_sha256']}
    delivery['resume_parent_version']=1
    delivery['checkpoint_member_sha256']=checkpoint_files
    dump(STAGE/'delivery.json',delivery);dump(STAGE/'checkpoint_acceptance.json',result)
    print(json.dumps(result,indent=2))

def main(action):
    if action=='prepare':return prepare()
    sys.path.insert(0,str(ROOT/'scripts'))
    import deploy_locked_continuations_20261108 as deploy
    if action=='launch':
        deploy.main('b1_shuf','status')
        assert read(PARENT/'remote_status.json')['status'].endswith(('COMPLETE','ERROR','CANCEL_ACKNOWLEDGED')),'Parent still active; duplicate launch forbidden'
        if read(STAGE/'delivery.json').get('resume_parent_version'):
            deploy.main(KIND,'status')
            assert read(STAGE/'remote_status.json')['status'].endswith(('COMPLETE','ERROR','CANCEL_ACKNOWLEDGED')),'Earlier resume version still active; duplicate launch forbidden'
        assert sha(STAGE/'dataset'/CHECKPOINT)==read(STAGE/'delivery.json')['checkpoint_sha256']
        deploy.main(KIND,'quota')
        quota=read(STAGE/'quota.json')['gpuQuota']
        seconds=lambda v:float(v.rstrip('s'))
        remaining=seconds(quota['totalTimeAllowed'])-seconds(quota['timeUsed'])-seconds(quota.get('timeReserved','0s'))
        assert remaining>=5400,'Insufficient quota for requested 90-minute session; do not launch'
    deploy.main(KIND,action)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','dataset','dataset-status','quota','launch','verify-source','status','output'])
    main(p.parse_args().action)
