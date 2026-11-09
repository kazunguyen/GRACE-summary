import hashlib, json
from pathlib import Path

root=Path(__file__).resolve().parents[2]
base=root/'14_Arm_B3_NoDiff/notebooks/02_kaggle_qwen_q4_b3_nodiff_validation_runtime_locked_20261109.ipynb'
out=root/'14_Arm_B3_NoDiff/notebooks/03_kaggle_qwen_q4_b3_nodiff_test_runtime_locked_20261109.ipynb'
nb=json.loads(base.read_text(encoding='utf-8'))
def get(i): return ''.join(nb['cells'][i]['source'])
def setsrc(i,s): nb['cells'][i]['source']=s.splitlines(keepends=True)

md=get(0).replace('Kaggle validation','Kaggle test').replace('census validation, seed 42: Devign 2.732 + ReVeal 2.273','full test census, seed 42: Devign 2,732 + ReVeal 2,274').replace('validation inference','test inference').replace('Chỉ đọc validation; sau khi đủ toàn bộ validation IDs, notebook chọn và khóa ngưỡng MCC riêng cho Devign/ReVeal theo quy tắc `validation_mcc_grid_v1`. Không đọc test.','Chỉ đọc test; không tối ưu ngưỡng trên test. Áp dụng nguyên ngưỡng validation đã khóa: Devign 0.92, ReVeal 0.01.').replace('grace_b3_nodiff_devign_validation_checkpoint.zip`, `grace_b3_nodiff_reveal_validation_checkpoint.zip`, `grace_diagnostics.zip','grace_b3_nodiff_devign_test_checkpoint.zip`, `grace_b3_nodiff_reveal_test_checkpoint.zip`, `grace_diagnostics.zip')
md=md.replace('grace_b3_nodiff_validation_inputs.zip','grace_b3_nodiff_test_inputs.zip')
md += '\n\nTest prompts dùng code và graph của từng mẫu test; demo là cặp vulnerable/patched nguồn train đã được Dung và Hiếu duyệt, giữ nguyên như validation. Label test chỉ nằm trong metadata, không nằm trong prompt.\n'
setsrc(0,md)

cell=get(2)
cell=cell.replace("SPLIT='validation'", "SPLIT='test'")
cell=cell.replace("BUNDLE_NAME='grace_b3_nodiff_validation_inputs.zip'", "BUNDLE_NAME='grace_b3_nodiff_test_inputs.zip'")
cell=cell.replace("BUNDLE_SHA256='6e8a5ff58b4e09bb826abcd0037b6f5f6933b3754212fc830422c41651ff0ee3'", "BUNDLE_SHA256='1b8e1e7e45da033a753cf24b4338233b3c99cf59b6aaa8110a17f178c74a0d26'")
cell=cell.replace("if delivery.get('arm')!=ARM or delivery.get('split')!=SPLIT or delivery.get('seed')!=SEED:", "if delivery.get('arm')!=ARM or delivery.get('split')!=SPLIT or delivery.get('seed')!=SEED:")
cell=cell.replace("expected_count=2732 if ds=='devign' else 2273", "expected_count=2732 if ds=='devign' else 2274")
cell=cell.replace("print('Verified validation rows:'", "print('Verified test rows:'")
needle="RUNTIME=load_contract(WORK/'inference_runtime_lock.json')"
insert="""RUNTIME=load_contract(WORK/'inference_runtime_lock.json')
THRESHOLD_RAW=payloads['validation_threshold_lock.json']
THRESHOLD_RAW_SHA256='c4c438a413ffafcbcac993be49c12963497a3290a8dc679f2c3e6fee763bdebf'
if sha_bytes(THRESHOLD_RAW)!=THRESHOLD_RAW_SHA256: raise ValueError('Validation threshold lock bytes changed')
THRESHOLD_LOCK=json.loads(THRESHOLD_RAW.decode('utf-8'))
if THRESHOLD_LOCK.get('locked_sha256')!='64dde9b94a44ae56b3abe0b7e6abd6ced2a5320d7fee2785a961c5da225a786c': raise ValueError('Validation threshold lock seal mismatch')
if THRESHOLD_LOCK.get('arm')!=ARM or THRESHOLD_LOCK.get('split')!='validation' or THRESHOLD_LOCK.get('runtime_contract_sha256')!=RUNTIME_LOCK_SHA256: raise ValueError('Threshold lock does not match arm/runtime')
"""
cell=cell.replace(needle,insert)
cell=cell.replace("if len(rows)!=root['scope']['count']:","if root.get('threshold_lock_sha256')!=THRESHOLD_RAW_SHA256 or root.get('threshold')!=THRESHOLD_LOCK['entries'][ds]['tau_star']: raise ValueError(f'{ds} validation threshold lock mismatch')\n    if len(rows)!=root['scope']['count']:")
setsrc(2,cell)

preflight=get(4)
preflight += '''
from transformers import AutoTokenizer
tokenizer=AutoTokenizer.from_pretrained(RUNTIME['tokenizer']['repo'],revision=RUNTIME['tokenizer']['revision'])
for ds in ('devign','reveal'):
    rows=DATASETS[ds]['rows']; budget=DATASETS[ds]['manifest']['prompt_budget_tokens']
    for index,item in enumerate(rows,1):
        encoded=tokenizer.apply_chat_template([{'role':'user','content':item['prompt']}],tokenize=True,add_generation_prompt=True,return_dict=False)
        if len(encoded)>budget: raise ValueError(f'{ds}/{item["id"]}: prompt uses {len(encoded)} tokens, exceeds locked context {budget}')
        if index%250==0 or index==len(rows): note(f'Token budget preflight {ds}: {index}/{len(rows)} checked; all <= {budget}')
'''
setsrc(4,preflight)

# Replace validation threshold fitting with a fixed-threshold test runner and post-run scoring.
test_cell='''MAX_RUNTIME_HOURS=10.5
import math
CHECKPOINT_RESERVE_SECONDS=300
OUT_ROOT=Path('/kaggle/working/b3_nodiff_test')
CHECKPOINT_PATHS={'devign':None,'reveal':None}  # Set an explicit Kaggle checkpoint input path only when resuming.
OUT_ROOT.mkdir(parents=True,exist_ok=True)
deadline=SESSION_STARTED+MAX_RUNTIME_HOURS*3600
summary={'arm':ARM,'seed':SEED,'split':SPLIT,'runtime_contract_sha256':RUNTIME_LOCK_SHA256,
         'threshold_lock_sha256':THRESHOLD_RAW_SHA256,'thresholds':{},'datasets':{},'state':'running'}
for ds in ('devign','reveal'):
    data=DATASETS[ds]; root=data['root']; tau=float(THRESHOLD_LOCK['entries'][ds]['tau_star'])
    if float(root['threshold'])!=tau: raise ValueError(f'{ds}: delivered threshold differs from validation lock')
    summary['thresholds'][ds]={'tau_star':tau,'source':'locked validation_threshold_lock.json','comparison':'score >= threshold'}
    ds_out=OUT_ROOT/ds; status_path=ds_out/f'seed_{SEED}_status.json'
    checkpoint=Path('/kaggle/working')/f'grace_b3_nodiff_{ds}_test_checkpoint.zip'
    try:
        if CHECKPOINT_PATHS[ds] is not None: restore_checkpoint(Path(CHECKPOINT_PATHS[ds]),ds_out,root,data['rows'])
        elif ds_out.exists(): raise ValueError(f'Fresh output directory already exists: {ds_out}; set explicit checkpoint path to resume')
        else: ds_out.mkdir(parents=True)
        done=checked_records(ds_out,root,data['rows'])
        note(f'{ds} test inference start/resume: {done}/{len(data["rows"])} complete; locked tau={tau:.2f}')
        if done<len(data['rows']) and time.time()<deadline-CHECKPOINT_RESERVE_SECONDS:
            (Path('/kaggle/working')/'inference_input_manifest.json').write_bytes(data['root_path'].read_bytes())
            env=os.environ.copy(); env['B3_INPUT_ROOT_SHA256']=data['root_sha256']
            env['PYTHONPATH']='/kaggle/working'+os.pathsep+env.get('PYTHONPATH','')
            command=[sys.executable,'-u','/kaggle/working/kaggle_inference.py','--model',str(MODEL_PATH),
                '--model-revision','local-input','--seed',str(SEED),'--arm',ARM,
                '--expected-model-sha256',RUNTIME['model']['sha256'],'--gpu-layers',str(RUNTIME['constructor']['n_gpu_layers']),
                '--deadline-epoch',str(deadline),'--checkpoint-reserve-seconds',str(CHECKPOINT_RESERVE_SECONDS),
                '--status',str(status_path),'--run',ds,SPLIT,str(data['bundle']),str(ds_out/'seed_42'/ds/SPLIT)]
            run_logged(command,f'inference_{ds}_seed_{SEED}',env=env)
        done=checked_records(ds_out,root,data['rows'])
        make_checkpoint(ds_out,checkpoint,root,data['rows'])
        records_path=ds_out/'seed_42'/ds/SPLIT/'records.jsonl'
        records=[json.loads(line) for line in records_path.read_text(encoding='utf-8').splitlines() if line.strip()]
        by_id={r['id']:r for r in records}; predictions=[]
        for item in data['rows']:
            rec=by_id.get(item['id'])
            if rec is None: continue
            predictions.append({'id':item['id'],'dataset':ds,'split':'test','label':item['label'],'score':rec['s'],
                'threshold':tau,'prediction':int(rec['s']>=tau),'prompt_sha256':item['prompt_sha256']})
        pred_path=ds_out/'test_predictions_at_validation_threshold.jsonl'
        pred_path.write_text(''.join(json.dumps(x,ensure_ascii=False)+'\\n' for x in predictions),encoding='utf-8')
        valid=[p for p in predictions if isinstance(p['score'],(int,float)) and math.isfinite(p['score'])]
        tn=sum(p['label']==0 and p['prediction']==0 for p in valid); fp=sum(p['label']==0 and p['prediction']==1 for p in valid)
        fn=sum(p['label']==1 and p['prediction']==0 for p in valid); tp=sum(p['label']==1 and p['prediction']==1 for p in valid)
        summary['datasets'][ds]={'expected':len(data['rows']),'completed':done,'scored':len(valid),'checkpoint':str(checkpoint),
            'predictions':str(pred_path),'tau_star':tau,'confusion_matrix':[[tn,fp],[fn,tp]],
            'accuracy':(tn+tp)/len(valid) if valid else None,'state':'complete' if done==len(data['rows']) else 'checkpointed_or_incomplete'}
        note(f'{ds} test progress complete: {done}/{len(data["rows"])}; scored={len(valid)}; tau={tau:.2f}; checkpoint={checkpoint}')
    except Exception as exc:
        summary['datasets'][ds]={'state':'error','error':repr(exc),'status_path':str(status_path)}
        note(f'{ds} test run error: {exc}')
        raise
summary['state']='complete' if all(summary['datasets'].get(ds,{}).get('completed')==len(DATASETS[ds]['rows']) for ds in ('devign','reveal')) else 'checkpointed_or_incomplete'
(OUT_ROOT/'batch_summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
note('Test run summary: '+json.dumps(summary,ensure_ascii=False))
diagnostics_zip()
'''
setsrc(5,test_cell)

# The child may be silent while a row is processing; drain output asynchronously and emit a 60s heartbeat from status.json.
runner=get(1)
old="""    with log.open('w', encoding='utf-8') as f:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, encoding='utf-8', errors='replace', bufsize=1, env=env)
        is_inference = name.startswith('inference_')
        for line in proc.stdout:
            f.write(line); f.flush()
            if is_inference:
                match = re.search(r'^(\\S+).*\\((\\d+)/(\\d+)\\)\\s*$', line.strip())
                if match:
                    key, done, total = match.group(1), int(match.group(2)), int(match.group(3))
                    if done % 100 == 0 or done == total:
                        print(f'{key}: {done}/{total}', flush=True)
                elif line.strip():
                    print(line, end='', flush=True)
            elif line.strip():
                print(line, end='', flush=True)
        code = proc.wait()
"""
new="""    with log.open('w', encoding='utf-8') as f:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, encoding='utf-8', errors='replace', bufsize=1, env=env)
        is_inference = name.startswith('inference_')
        import queue, threading
        q=queue.Queue()
        def drain():
            for item in proc.stdout: q.put(item)
            q.put(None)
        threading.Thread(target=drain,daemon=True).start()
        status_arg=Path(cmd[cmd.index('--status')+1]) if is_inference and '--status' in cmd else None
        while True:
            try: line=q.get(timeout=60 if is_inference else 1)
            except queue.Empty:
                snapshot={}
                try: snapshot=json.loads(status_arg.read_text(encoding='utf-8')) if status_arg and status_arg.is_file() else {}
                except Exception as exc: snapshot={'status_read_error':repr(exc)}
                runs=snapshot.get('runs',{})
                run_state=next(iter(runs.values()),{}) if runs else {}
                output_path=Path(run_state.get('output',''))/'records.jsonl' if run_state.get('output') else None
                records_n=sum(1 for _ in output_path.open(encoding='utf-8')) if output_path and output_path.is_file() else 0
                total=run_state.get('expected_records') or run_state.get('count') or '?'
                note(f'HEARTBEAT {name}: pid={proc.pid}, state={snapshot.get("state","starting")}, records={records_n}/{total}, status={status_arg}')
                continue
            if line is None: break
            f.write(line); f.flush()
            if line.strip(): print(line,end='',flush=True)
        code = proc.wait()
"""
if old not in runner: raise RuntimeError('Cannot locate original run_logged body for replacement')
runner=runner.replace(old,new)
setsrc(1,runner)

nb['metadata'].setdefault('kaggle',{})
nb['metadata']['kaggle'].update({'is_gpu_enabled':True,'is_internet_enabled':True})
with out.open('w',encoding='utf-8',newline='\n') as stream:
    stream.write(json.dumps(nb,ensure_ascii=False,indent=1)+'\n')
print(out)
