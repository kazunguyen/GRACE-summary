"""CPU checks for archive layouts, fixed thresholds and interrupted-run handling.

Uses a synthetic inference backend; never loads a model or examines real test scores.
"""
import contextlib
import hashlib
import importlib.util
import io
import json
import math
from pathlib import Path
import shutil
import sys
import tempfile
import time
import types
import zipfile

import numpy as np

HERE = Path(__file__).resolve().parent


def digest(data):
    return hashlib.sha256(data).hexdigest()


def check(condition, message):
    if not condition: raise AssertionError(message)


def expect_error(call):
    try: call()
    except (ValueError, RuntimeError): return
    raise AssertionError('Expected rejection')


def main():
    checks = []
    report = json.loads((HERE/'delivery_manifest.json').read_bytes())
    nb = json.loads((HERE/'02_kaggle_qwen_q4_b1_h2_test_20261106.ipynb').read_bytes())
    for i,c in enumerate(nb['cells']):
        if c['cell_type']=='code':
            source=''.join(c['source'])
            compile(source.split('\n',1)[1] if source.startswith('%%writefile') else source, f'cell{i}', 'exec')
            check(c['outputs']==[] and c['execution_count'] is None,'Notebook contains execution output')
    source=''.join(nb['cells'][7]['source']).split('\n',1)[1]
    check(source.encode()==(HERE/'kaggle_b1h2_test_runtime.py').read_bytes(),'Embedded helper changed')
    check(digest((HERE/'grace_b1_h2_test_inputs.zip').read_bytes())==report['input_bundle_sha256'],'Archive hash')
    checks.append('all_code_cells_compile_and_embed_exact_helper')
    # Real heartbeat thread while the foreground is blocked, without GPU/network I/O.
    class Events:
        def __init__(self): self.callbacks=[]
        def register(self,name,callback): self.callbacks.append(callback)
        def unregister(self,name,callback): self.callbacks.remove(callback)
    shell=types.SimpleNamespace(events=Events())
    heartbeat_env={'get_ipython':lambda:shell}
    bootstrap=(HERE/'heartbeat_bootstrap.py').read_text(encoding='utf8')
    check(''.join(nb['cells'][1]['source']).startswith(bootstrap),'Bootstrap is not first in notebook')
    fast=bootstrap.replace('HEARTBEAT_INTERVAL_SECONDS = 30','HEARTBEAT_INTERVAL_SECONDS = 0.02')
    captured=io.StringIO()
    with contextlib.redirect_stdout(captured):
        exec(fast,heartbeat_env)
        heartbeat_env['heartbeat_stage']('simulated slow GPU check')
        time.sleep(.12)
        check('kernel_alive' in captured.getvalue(),'No heartbeat while foreground waits')
        check('stage=simulated slow GPU check' in captured.getvalue(),'Heartbeat lost stage')
        old_thread=heartbeat_env['_heartbeat_thread']
        exec(fast,heartbeat_env)
        check(not old_thread.is_alive() and len(shell.events.callbacks)==1,'Rerun duplicates heartbeats/hooks')
        shell.events.callbacks[0](types.SimpleNamespace(error_in_exec=RuntimeError('synthetic cell failure')))
        check(not heartbeat_env['_heartbeat_thread'].is_alive() and not shell.events.callbacks,'Failed cell keeps pinging')
        stopped_size=len(captured.getvalue());time.sleep(.06)
        check(len(captured.getvalue())==stopped_size,'Heartbeat continued after cleanup')
    check(captured.getvalue().startswith('[PING] B1-H2 notebook: Python execution started'),'Startup ping is not first')
    checks.append('immediate_ping_periodic_heartbeat_rerun_and_error_cleanup')
    # Exercise the actual first cell's GPU-timeout path without a real GPU.
    import subprocess
    original_run=subprocess.run
    def fake_gpu_run(*args,**kwargs):
        check(kwargs.get('timeout')==30,'GPU probe has no 30-second timeout')
        raise subprocess.TimeoutExpired(args[0],30)
    shell=types.SimpleNamespace(events=Events())
    gpu_env={'get_ipython':lambda:shell}
    with tempfile.TemporaryDirectory() as temp:
        startup=''.join(nb['cells'][1]['source']).replace("Path('/kaggle/working/grace_diagnostics')",'Path('+repr(temp)+')')
        subprocess.run=fake_gpu_run
        try:
            with contextlib.redirect_stdout(io.StringIO()) as gpu_output:
                try: exec(startup,gpu_env)
                except subprocess.TimeoutExpired: pass
                else: raise AssertionError('GPU timeout was not raised')
            check('checking GPU' in gpu_output.getvalue() and 'GPU check failed' in gpu_output.getvalue(),'GPU timeout not visible')
            check(not gpu_env['_heartbeat_thread'].is_alive(),'GPU timeout left heartbeat running')
        finally:
            subprocess.run=original_run
            if gpu_env.get('_heartbeat_thread') and gpu_env['_heartbeat_thread'].is_alive():gpu_env['_b1h2_heartbeat_cleanup']('test cleanup')
    checks.append('actual_startup_cell_gpu_timeout_reports_and_stops')
    spec=importlib.util.spec_from_file_location('b1h2_test_runtime',HERE/'kaggle_b1h2_test_runtime.py')
    runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
    with tempfile.TemporaryDirectory(prefix='b1h2_test_checks_') as temp:
        root=Path(temp)
        # Exercise the actual notebook's input loader for all three Kaggle archive representations.
        for layout in ('outer_zip','inner_zips','fully_extracted'):
            inputs=root/layout;inputs.mkdir()
            with zipfile.ZipFile(HERE/'grace_b1_h2_test_inputs.zip') as archive:
                if layout=='outer_zip':shutil.copyfile(HERE/'grace_b1_h2_test_inputs.zip',inputs/'grace_b1_h2_test_inputs.zip')
                else:
                    for name in archive.namelist():
                        if layout=='inner_zips':(inputs/Path(name).name).write_bytes(archive.read(name))
                        else:
                            with zipfile.ZipFile(io.BytesIO(archive.read(name))) as inner:
                                folder=inputs/Path(name).stem;folder.mkdir()
                                for entry in inner.namelist():(folder/entry).write_bytes(inner.read(entry))
            env=dict(Path=Path,json=json,hashlib=hashlib,zipfile=zipfile,math=math,note=lambda *a:None,heartbeat_stage=lambda *a:None)
            exec(''.join(nb['cells'][2]['source']),env)
            env.update(KAGGLE_INPUT_ROOT=inputs,BUNDLE_WORK=root/(layout+'_work'),OUT_ROOT=root/(layout+'_out'),DIAG=root)
            exec(''.join(nb['cells'][3]['source']),env)
            check(sum(map(len,env['expected'].values()))==5006,'Wrong census from loader')
            for path in env['bundles'].values():runner.load_bundle(path)
            checks.append('actual_notebook_input_loader_'+layout)
        lock_path=env['OUT_ROOT']/'threshold_lock.json'
        lock=json.loads(lock_path.read_bytes())
        model=root/'model.gguf';model.write_bytes(b'synthetic model for CPU checks')
        model_hash=digest(model.read_bytes())
        calls=[]
        class FakeTokenizer:
            def encode(self,label,**kw):return [int(label)]
            def apply_chat_template(self,messages,tokenize=False,**kw):return [0,1] if tokenize else 'chat'
        class FakeLlama:
            def __init__(self,**kw):
                check(kw['seed']==4294967295 and kw['tensor_split']==[1.,1.] and kw['n_batch']==256,'Validation settings changed')
                self.n_tokens=2;self.scores=np.asarray([[0.,0.,0.],[0.,1.,2.]])
            def tokenize(self,text,**kw):return [int(text)] if text in (b'0',b'1') else [0,1]
            def reset(self):pass
            def eval(self,tokens):calls.append(tokens)
            def detokenize(self,tokens):return b'Looking'  # Non-binary raw must keep its finite score.
        llama=types.ModuleType('llama_cpp');llama.Llama=FakeLlama;llama.__version__='0.3.16';llama.LLAMA_DEFAULT_SEED=4294967295;llama.LLAMA_SPLIT_MODE_LAYER=1
        transformers=types.ModuleType('transformers');transformers.AutoTokenizer=types.SimpleNamespace(from_pretrained=lambda *a,**k:FakeTokenizer())
        saved={name:sys.modules.get(name) for name in ('llama_cpp','transformers')}
        sys.modules.update(llama_cpp=llama,transformers=transformers)
        # Small synthetic fixtures use the authentic validation seal, but no real test outputs.
        runlist=[]
        for ds in ('devign','reveal'):
            p=root/(ds+'_fixture.zip')
            rows=[dict(id=f'{ds}:test:{i}',dataset=ds,split='test',arm='B1-H2',seed=42,label=i,
                       prompt='synthetic',prompt_sha256=digest(b'synthetic')) for i in range(2)]
            payload=b''.join((json.dumps(r)+'\n').encode() for r in rows)
            manifest=dict(dataset=ds,split='test',arm='B1-H2',seed=42,count=2,prompts_sha256=digest(payload),
                          model_sha256=lock['model_sha256'],threshold_lock_sha256=lock['locked_sha256'],tau_star={'devign':.09,'reveal':.21}[ds])
            with zipfile.ZipFile(p,'w') as z:
                z.writestr('prompts.jsonl',payload);z.writestr('bundle_manifest.json',json.dumps(manifest));z.writestr('threshold_lock.json',lock_path.read_bytes())
            runlist.append((ds,'test',str(p),str(root/'run/seed_42'/ds/'test')))
        status=root/'run/seed_42_status.json'
        def run(deadline=None):
            with contextlib.redirect_stdout(io.StringIO()):
                runner.run_batch(runlist,model,'local-input',-1,None,deadline or time.time()+120,5,status,42,model_hash,'B1-H2')
        try:
            run()
            check(len(calls)==4,'Initial inference count')
            for ds,_,_,out in runlist:
                records=[json.loads(x) for x in (Path(out)/'records.jsonl').read_text().splitlines()]
                check(all(r['tau']=={'devign':.09,'reveal':.21}[ds] and r['pred_tau']==1 for r in records),'Fixed tau not applied')
                metrics=json.loads((Path(out)/'evaluation.json').read_bytes())
                check(metrics['n_score_valid']==2 and metrics['n_response_valid']==0 and metrics['confusion_matrix']==[[0,1],[0,1]],'Raw-invalid finite scores excluded')
            checks.append('fixed_validation_thresholds_applied_to_all_score_valid_rows')
            run();check(len(calls)==4,'Resume recomputed saved records');checks.append('resume_skips_all_completed_ids')
            record_path=Path(runlist[0][3])/'records.jsonl'
            good=record_path.read_bytes();rows=[json.loads(x) for x in good.splitlines()];rows[0]['tau']=.67
            record_path.write_text(''.join(json.dumps(r)+'\n' for r in rows));expect_error(run);record_path.write_bytes(good)
            checks.append('wrong_Colab_threshold_checkpoint_rejected')
            original_manifest=Path(runlist[0][3])/'run_manifest.json'
            good_manifest=original_manifest.read_bytes();wrong=json.loads(good_manifest);wrong['inference_seed']=42
            original_manifest.write_text(json.dumps(wrong));expect_error(run);original_manifest.write_bytes(good_manifest)
            checks.append('wrong_inference_seed_checkpoint_rejected')
            tampered=root/'tampered.zip'
            with zipfile.ZipFile(runlist[0][2]) as original,zipfile.ZipFile(tampered,'w') as z:
                for name in original.namelist():
                    data=original.read(name)
                    if name=='threshold_lock.json':
                        bad=json.loads(data);bad['results']['reveal']['tau_star']=.67;data=json.dumps(bad).encode()
                    z.writestr(name,data)
            expect_error(lambda:runner.load_bundle(tampered));checks.append('tampered_threshold_lock_rejected')
            before=len(calls);run(time.time()-1);check(len(calls)==before,'Expired deadline still called model')
            check(json.loads(status.read_bytes())['timed_out'],'Deadline not recorded');checks.append('expired_budget_prevents_inference')
            runner.snapshot(status)
            with zipfile.ZipFile(root/'grace_b1_h2_test_checkpoint.zip') as z:
                check('seed_42/devign/test/records.jsonl' in z.namelist(),'Checkpoint layout not resumable')
            checks.append('periodic_checkpoint_zip_has_resumable_layout')
        finally:
            for name,value in saved.items():
                if value is None:sys.modules.pop(name,None)
                else:sys.modules[name]=value
    result=dict(status='pass',checks=checks,real_gpu_inference=False,real_test_scores_read=False)
    (HERE/'verification_report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
