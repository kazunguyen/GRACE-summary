"""Run independently pinned B3 validation inputs in fixed Devign -> REVEAL order.

Each child retains its original worker/input/runtime identity. No threshold fit,
test split, quota decision or metric-based stopping is performed here.
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def sha(raw):return hashlib.sha256(raw).hexdigest()


def select_source(input_dir, root):
    from b3_delivery_runtime import validate_bundle
    candidates=list(Path(input_dir).rglob(root['bundle_filename']))
    expected=root['members_sha256']['bundle_manifest.json']
    candidates += [p.parent for p in Path(input_dir).rglob('bundle_manifest.json') if sha(p.read_bytes())==expected]
    if len(candidates)!=1:raise ValueError('Need exactly one input root for '+root['scope']['dataset'])
    validate_bundle(candidates[0],root)
    return candidates[0]


def snapshot(output, checkpoint, root, rows):
    """Snapshot complete JSONL prefix, never modify the live worker output.

    Status files use atomic replace. An in-flight final record is excluded only
    from the copy; older records and original live bytes remain untouched.
    """
    from b3_delivery_runtime import read_members, checked_records, make_checkpoint
    output,checkpoint=Path(output),Path(checkpoint)
    members=read_members(output)
    with tempfile.TemporaryDirectory(prefix='b3_snapshot_',dir=output.parent) as temp:
        stage=Path(temp)
        for name,raw in members.items():
            if name.endswith('.tmp'):continue
            if name.endswith('records.jsonl') and raw and not raw.endswith(b'\n'):
                raw=raw.rsplit(b'\n',1)[0]+b'\n' if b'\n' in raw else b''
            dest=stage/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
        count=checked_records(stage,root,rows)
        candidate=checkpoint.with_suffix('.zip.tmp')
        make_checkpoint(stage,candidate,root,rows)
        os.replace(candidate,checkpoint)
    return count


def prepare(input_dir,work,definitions):
    from b3_delivery_runtime import load_input_root,validate_bundle,checked_name
    work=Path(work);work.mkdir(parents=True,exist_ok=True)
    prepared=[]
    for ds in ('devign','reveal'):
        definition=definitions[ds]
        root=load_input_root(definition['path'],definition['sha256'])
        if root['scope']['dataset']!=ds:raise ValueError('Dataset root mismatch')
        source=select_source(input_dir,root)
        _,rows,members=validate_bundle(source,root)
        # ZIP byte identity is checked only for the original packed transport.
        # Deflate/ZipInfo bytes vary between Windows and Kaggle Linux. The
        # independently pinned complete member inventory is the payload identity.
        bundle=work/ds
        if bundle.exists():raise ValueError('Prepared input directory already exists')
        bundle.mkdir()
        for name,raw in members.items():
            target=bundle/checked_name(name)
            target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
        validate_bundle(bundle,root)
        prepared.append((ds,root,rows,bundle,definition))
    return prepared


def run(prepared,model,output,deadline,worker,active_root,diagnostics):
    from b3_delivery_runtime import checked_records,restore_checkpoint
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    diagnostics=Path(diagnostics);diagnostics.mkdir(parents=True,exist_ok=True)
    ledger={'state':'starting','fixed_order':['devign','reveal'],'datasets':{},'deadline_epoch':deadline}
    def save():
        target=output/'dual_status.json';tmp=target.with_suffix('.json.tmp')
        tmp.write_text(json.dumps(ledger,indent=2)+'\n',encoding='utf-8');os.replace(tmp,target)
    save()
    for ds,root,rows,bundle,definition in prepared:
        dest=output/ds
        if dest.exists():raise ValueError('Output exists; fresh restart must be explicit and safe')
        # Future continuation accepts ONLY explicitly named, verified checkpoints.
        resume=definition.get('checkpoint')
        if resume:restore_checkpoint(resume,dest,root,rows)
        else:dest.mkdir()
        if time.time()>=deadline-300:
            ledger['state']='checkpointed_before_next_dataset';save();return ledger
        Path(active_root).write_bytes(Path(definition['path']).read_bytes())
        env=dict(os.environ,B3_INPUT_ROOT_SHA256=definition['sha256'])
        status=dest/'seed_42_status.json'
        cmd=[sys.executable,'-u',str(worker),'--model',str(model),'--model-revision','local-input',
            '--seed','42','--arm','B3','--expected-model-sha256',root['model_sha256'],
            '--gpu-layers','-1','--deadline-epoch',str(deadline),'--checkpoint-reserve-seconds','300',
            '--status',str(status),'--run',ds,'validation',str(bundle),str(dest/'seed_42'/ds/'validation')]
        checkpoint=output/('B3_'+ds+'_validation_checkpoint.zip')
        ledger['state']='running';ledger['datasets'][ds]={'state':'running','input_root_sha256':definition['sha256']};save()
        with (diagnostics/('inference_'+ds+'.log')).open('w',encoding='utf-8') as log:
            proc=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,env=env)
            last=0
            while proc.poll() is None:
                if time.monotonic()-last>=60:
                    try:
                        count=snapshot(dest,checkpoint,root,rows)
                        ledger['datasets'][ds]['records']=count
                        print(f'B3 {ds}: {count}/{len(rows)}; verified checkpoint exported',flush=True)
                    except (ValueError,OSError,KeyError) as exc:
                        # A concurrent file write may be transient. Never overwrite a
                        # previous good checkpoint with a failing snapshot.
                        print('Checkpoint retry: '+type(exc).__name__+': '+str(exc),flush=True)
                    last=time.monotonic();save()
                if time.time()>=deadline-60:
                    proc.terminate()
                    try:proc.wait(timeout=30)
                    except subprocess.TimeoutExpired:proc.kill();proc.wait()
                    break
                time.sleep(5)
            code=proc.wait()
        count=snapshot(dest,checkpoint,root,rows)
        ledger['datasets'][ds].update(records=count,expected=len(rows),returncode=code,
            state='complete' if count==len(rows) and code==0 else ('checkpointed' if code==0 else 'error'))
        save()
        if code!=0:
            ledger['state']='error';save();raise RuntimeError('B3 '+ds+' failed; inspect native log, second dataset not started')
        if count!=len(rows):
            ledger['state']='checkpointed';save();return ledger
    ledger['state']='complete';save();return ledger
