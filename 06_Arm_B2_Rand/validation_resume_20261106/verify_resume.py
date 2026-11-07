"""Exercise notebook orchestration with real I-11/input files and a simulated inference process."""
import ast,hashlib,io,json,os,shutil,sys,tempfile,time,types,zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
NB=ROOT/'Runs-management/kaggle_validation_6arms_20261104/02_kaggle_qwen_q4_b2_rand.ipynb'
nb=json.loads(NB.read_text(encoding='utf-8'))
cells=[''.join(c.get('source',[])) for c in nb['cells']]
for i,c in enumerate(nb['cells']):
    if c['cell_type']=='code':compile(cells[i].split('\n',1)[1] if cells[i].startswith('%%writefile') else cells[i],f'cell_{i}','exec')
found={}
with zipfile.ZipFile(ROOT/'Runs-management/kaggle_validation_6arms_20261104/grace_b2_rand_inputs.zip') as z:
    for name in z.namelist():
        if not name.endswith('.zip'):continue
        with zipfile.ZipFile(io.BytesIO(z.read(name))) as inner:
            m=inner.read('bundle_manifest.json');d=json.loads(m)
            if d['split']!='validation':continue
            found[(d['seed'],d['dataset'],d['split'])]={'manifest':m,'prompts':inner.read('prompts.jsonl')}
assert len(found)==6
latest=ROOT/'06_Arm_B2_Rand/output/kaggle_run_02/grace_b2_rand_checkpoint.zip'
older=ROOT/'Runs-management/kaggle_validation_6arms_20261104/grace_b2_rand_checkpoint.zip'
hashmodel='f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335'
report={}
with tempfile.TemporaryDirectory(prefix='resume_verification_',dir=Path(__file__).parent) as name:
    temp=Path(name).resolve()
    assert temp.parent==Path(__file__).resolve().parent
    input_dir=temp/'input';input_dir.mkdir()
    for tag,src in [('old',older),('latest',latest)]:
        d=input_dir/tag;d.mkdir();shutil.copy2(src,d/'grace_b2_rand_checkpoint.zip')

    def exercise(case,expired=False,force_old=False):
        work=temp/case;work.mkdir();calls=[];scheduled=[]
        env=dict(Path=Path,zipfile=zipfile,hashlib=hashlib,json=json,sys=sys,time=time,
                 platform=types.SimpleNamespace(python_version=lambda:'3.13.15'),note=lambda *a:None,
                 RESUME_FROM_CHECKPOINT=True,CHECKPOINT_INPUT_PATH=input_dir/'old/grace_b2_rand_checkpoint.zip' if force_old else None,
                 KAGGLE_INPUT_ROOT=input_dir,OUT_ROOT=work,found=found,SEEDS=(42,43,44),EXPECTED_RUNS=[('devign','validation'),('reveal','validation')],
                 MODEL_SHA256=hashmodel,MODEL_FILENAME='Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf',GPU_LAYERS=-1,LIMIT=None,
                 MAX_RUNTIME_HOURS=9,SESSION_STARTED_EPOCH=time.time()-(9*3600-590) if expired else time.time(),CHECKPOINT_RESERVE_SECONDS=600,
                 model_path='unused-model.gguf',revision='local-sha256:'+hashmodel,
                 BUNDLE_PATHS={k:Path('_'.join(map(str,k))+'.zip') for k in found},diagnostics_zip=lambda:None)
        env['shutil']=types.SimpleNamespace(make_archive=lambda prefix,fmt,root_dir:shutil.make_archive(str(temp/(case+'_export')),fmt,root_dir=root_dir))
        def fake_inference(cmd,logname):
            seed=int(cmd[cmd.index('--seed')+1]);calls.append(seed);runs={}
            template=json.loads((work/'seed_42/devign/validation/run_manifest.json').read_text())
            for i,arg in enumerate(cmd):
                if arg!='--run':continue
                ds,split,bundle,out=cmd[i+1:i+5]
                assert split=='validation'
                key=(seed,ds,split);manifest=json.loads(found[key]['manifest'])
                rows=[json.loads(x) for x in found[key]['prompts'].decode().splitlines() if x.strip()]
                folder=Path(out);folder.mkdir(parents=True,exist_ok=True);path=folder/'records.jsonl'
                done={json.loads(x)['id'] for x in path.read_text(encoding='utf-8').splitlines() if x.strip()} if path.exists() else set()
                with path.open('a',encoding='utf-8',newline='\n') as f:
                    for row in rows:
                        if row['id'] in done:continue
                        scheduled.append((seed,ds,row['id']))
                        r={k:row[k] for k in ('id','label','prompt_sha256')}
                        r.update(arm='B2-rand',dataset=ds,split=split,seed=seed,model_sha256=hashmodel)
                        f.write(json.dumps(r)+'\n')
                if not (folder/'run_manifest.json').exists():
                    identity=dict(template,arm='B2-rand',prompt_seed=seed,dataset=ds,split=split,prompt_set_sha256=manifest['prompts_sha256'])
                    (folder/'run_manifest.json').write_text(json.dumps(identity))
                runs[f'{ds}/{split}']={'state':'complete','count':len(rows),'completed':len(rows)}
            status={'state':'complete','timed_out':False,'runs':runs}
            Path(cmd[cmd.index('--status')+1]).write_text(json.dumps(status))
        env['run_logged']=fake_inference
        exec(compile(cells[11],'orchestrator','exec'),env)
        return env,calls,scheduled,json.loads((work/'batch_summary.json').read_text())

    env,calls,scheduled,summary=exercise('complete')
    assert calls==[43,44],calls
    assert len(scheduled)==7226
    counts={}
    for seed,ds,uid in scheduled:counts[f'{seed}/{ds}']=counts.get(f'{seed}/{ds}',0)+1
    assert counts=={'43/reveal':2221,'44/devign':2732,'44/reveal':2273},counts
    assert summary['state']=='validation_complete' and summary['awaiting_threshold_lock'] is True
    assert summary['thresholds_fitted'] is False and summary['test_started'] is False
    assert sum(summary['progress'].values())==15015
    assert not list(env['OUT_ROOT'].glob('seed_*/**/test/records.jsonl'))
    with zipfile.ZipFile(latest) as z:
        for key in z.namelist():
            if key.endswith(('thresholds.json','threshold_lock.json')):
                assert (env['OUT_ROOT']/key).read_bytes()==z.read(key)
    report['i11_plus_old_checkpoint_auto_select']='pass'
    report['exact_missing_validation_schedule']=counts
    report['existing_7789_rows_preserved']='pass'
    report['completion_stops_for_threshold_lock']='pass'
    report['threshold_files_unchanged']='pass'

    env,calls,scheduled,summary=exercise('expired',expired=True)
    assert calls==[] and scheduled==[] and summary['state']=='timed_out'
    assert sum(summary['progress'].values())==7789
    report['setup_time_counts_against_budget']='pass'
    try:exercise('old_only',force_old=True)
    except ValueError as e:assert 'I-11' in str(e)
    else:raise AssertionError('I-09-only checkpoint was accepted')
    report['older_checkpoint_rejected']='pass'

    runner=ast.parse(cells[10].split('\n',1)[1])
    node=next(n for n in runner.body if isinstance(n,ast.FunctionDef) and n.name=='run_batch')
    namespace={}
    exec(compile(ast.Module(body=[node],type_ignores=[]),'runner','exec'),namespace)
    try:namespace['run_batch']([('devign','test','unused','unused')],'unused','unused',-1,None,0,600,'unused',42,hashmodel,'B2-rand')
    except ValueError as e:assert 'test is blocked' in str(e)
    else:raise AssertionError('Direct test invocation was accepted')
    report['direct_cli_test_blocked_before_model_import']='pass'
report['all_notebook_code_cells_compile']='pass'
report['actual_gpu_inference']='not performed; subprocess was simulated for orchestration checks'
Path(__file__).with_name('verification_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
