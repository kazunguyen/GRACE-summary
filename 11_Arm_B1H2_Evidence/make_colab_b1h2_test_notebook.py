import json, hashlib
from pathlib import Path

BASE=Path(__file__).parent
DELIVERY=BASE/'colab_l4_b1h2_test_20261106'
manifest=json.loads((DELIVERY/'bundle_manifest.json').read_text(encoding='utf-8'))
nb=json.loads((BASE/'notebooks/colab_l4_b1h2_remaining_validation_20261106.ipynb').read_text(encoding='utf-8'))
delivery=json.loads((DELIVERY/'drive_delivery.json').read_text(encoding='utf-8'))
url=delivery['bundle_url']
bundle_sha=delivery['bundle_sha256']
def setcell(i,s):
    nb['cells'][i]['source']=s.splitlines(keepends=True)
    if nb['cells'][i]['cell_type']=='code':
        nb['cells'][i]['outputs']=[]; nb['cells'][i]['execution_count']=None

setcell(0,'''# B1-H2 original test inference — Colab L4
Select Runtime Version **2026.10**, GPU **L4**, and run all cells. Mount the same Drive account on every session.
The notebook downloads its pinned input bundle automatically. Thresholds are fixed at Devign 0.09 and ReVeal 0.67.
This is the disclosed Colab platform deviation from preregistered Kaggle 2×T4.

Completed samples are saved individually on Drive. After disconnection, reconnect and run from the top:
matching checkpoint records are skipped automatically; an interrupted in-flight sample is scored again.
No artificial activity/keepalive is used. The session stops safely before its 9-hour budget.
Full setup/native logs remain in output files; progress is printed every 50 records.
Inference refuses to start unless the native log verifies every model layer was offloaded.
Bundle: '''+url+'\n')
s=''.join(nb['cells'][1]['source']).replace('b1h2_l4_remaining_validation','b1h2_l4_test').replace('GRACE_B1H2_COLAB_L4_REMAINING_20261106','GRACE_B1H2_COLAB_L4_TEST_20261106').replace('b1h2_l4_remaining_validation_bundle.zip','b1h2_original_test_bundle.zip').replace('l4_remaining_validation_output','l4_test_output')
s=s.replace("BUNDLE_DRIVE_URL = 'https://drive.google.com/file/d/1FuYcMkEuMBAFYexmg0c1HL5BxPB_L_Vg/view?usp=drivesdk'",f'BUNDLE_DRIVE_URL = {url!r}')
s=s.replace('b1h2_l4_test_bundle.zip','b1h2_original_test_bundle.zip')
s=s.replace("raise FileNotFoundError(f'Download the bundle from {BUNDLE_DRIVE_URL} into {BUNDLE_PATH}')",'''from urllib.request import urlopen
    # Download to local disk, then publish to Drive only after SHA verification.
    local_bundle = WORK / BUNDLE_PATH.name
    with urlopen('https://drive.google.com/uc?export=download&id=' + BUNDLE_DRIVE_URL.split('/d/')[1].split('/')[0]) as response:
        local_bundle.write_bytes(response.read())
    if hashlib.sha256(local_bundle.read_bytes()).hexdigest() != BUNDLE_EXPECTED_SHA256:
        raise ValueError('Downloaded bundle hash mismatch; place the bundle from the link in DRIVE_DIR manually.')
    shutil.copy2(local_bundle, BUNDLE_PATH)''')
s=s.replace('from google.colab import drive',f'BUNDLE_EXPECTED_SHA256 = {bundle_sha!r}\nfrom google.colab import drive')
s += '''
LOCAL_OUT = WORK / 'session_logs'
LOCAL_OUT.mkdir(exist_ok=True)
SESSION_ID=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'_'+str(time.time_ns())
SESSION_LOG_DIR=OUT/'sessions'/SESSION_ID
SESSION_LOG_DIR.mkdir(parents=True,exist_ok=True)
CHECKPOINTS = OUT / 'checkpoints'
CHECKPOINTS.mkdir(exist_ok=True)
def atomic_json(path, value):
    path = Path(path)
    raw = (json.dumps(value, ensure_ascii=False, allow_nan=False) + '\\n').encode()
    temp = path.with_name(path.name + '.tmp')
    with temp.open('wb') as f:
        f.write(raw); f.flush(); os.fsync(f.fileno())
    os.replace(temp, path)
    if path.read_bytes() != raw: raise OSError('Drive checkpoint readback failed: '+str(path))
def note(msg, display=True):
    line=f'[{datetime.now(timezone.utc).isoformat()}] {msg}'
    with (LOCAL_OUT/'events.log').open('a',encoding='utf-8') as f: f.write(line+'\\n')
    if display: print(line,flush=True)
'''
setcell(1,s)
setcell(2,''.join(nb['cells'][2]['source']).replace('(OUT /','(SESSION_LOG_DIR /'))
# Full pip output stays on local disk and is copied to Drive; screen gets bounded summaries.
s=''.join(nb['cells'][3]['source'])
s=s.replace("line_count % 50 == 0", "line_count % 500 == 0").replace("line_count % 100 == 0", "line_count % 2000 == 0")
s=s.replace('OUT / name','SESSION_LOG_DIR / name')
setcell(3,s)
s=''.join(nb['cells'][4]['source'])
s=s.replace('Expected 100 unique pilot prompts','Expected complete unique test prompt IDs').replace('Pilot sample must contain exactly 50 prompts per dataset','Test dataset counts differ from manifest')
s=s.replace("'e4f2765732c1c02c344ca9839cd2230e696f24079c7a54ccf4e7c42fbab09fb7'",repr(manifest['prompts_sha256']))
s += '''
if sha256_file(BUNDLE_PATH) != BUNDLE_EXPECTED_SHA256: raise ValueError('Bundle archive changed')
with zipfile.ZipFile(BUNDLE_PATH) as z: locked_thresholds=json.loads(z.read('thresholds.json'))
seal=locked_thresholds.pop('locked_sha256')
computed=hashlib.sha256(json.dumps(locked_thresholds,indent=2,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
if seal != computed or seal != bundle_manifest['threshold_lock_sha256']: raise ValueError('Threshold seal mismatch')
THRESHOLDS=bundle_manifest['thresholds']
for ds in ('devign','reveal'):
    if THRESHOLDS[ds] != locked_thresholds['thresholds'][f'{ds}|B1-H2|42']: raise ValueError('Threshold mismatch')
for row in rows:
    if row['split']!='test' or row['arm']!='B1-H2' or row['seed']!=42: raise ValueError('Wrong input arm/split/seed')
RUN_IDENTITY=dict(model_sha256=bundle_manifest.get('model_sha256','f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335'),
                  prompts_sha256=bundle_manifest['prompts_sha256'],threshold_lock_sha256=seal,arm='B1-H2',split='test',seed=42)
identity_path=OUT/'checkpoint_identity.json'
if identity_path.exists() and json.loads(identity_path.read_text()) != RUN_IDENTITY:
    raise ValueError('Existing checkpoint belongs to different input/model/thresholds')
atomic_json(identity_path,RUN_IDENTITY)
'''
setcell(4,s)
setcell(6,'''# Capture the llama.cpp callback as well as native file descriptors, on LOCAL disk.
# Python redirect_stderr alone does not capture the llama.cpp C callback.
from transformers import AutoTokenizer
from llama_cpp import Llama, __version__ as llama_cpp_version, llama_supports_gpu_offload
from llama_cpp import llama_cpp as native
if llama_cpp_version != '0.3.16' or not llama_supports_gpu_offload(): raise RuntimeError('Pinned CUDA backend unavailable')
tokenizer=AutoTokenizer.from_pretrained(TOKENIZER_REPO,revision=TOKENIZER_REVISION)
label_ids=[tokenizer.encode(x,add_special_tokens=False)[0] for x in ('0','1')]
if any(len(tokenizer.encode(x,add_special_tokens=False))!=1 for x in ('0','1')): raise ValueError('Labels must be single tokens')
native_path=LOCAL_OUT/'llama_cpp_model_load_offload.log'
native_file=native_path.open('wb',buffering=0)
@native.llama_log_callback
def native_log_callback(level, text, user_data):
    try:
        if text: os.write(native_file.fileno(),text)
    except Exception: pass
# Keep callback and file alive for the lifetime of the model.
native.llama_log_set(native_log_callback,None)
saved=[os.dup(1),os.dup(2)]
try:
    sys.stdout.flush(); sys.stderr.flush()
    os.dup2(native_file.fileno(),1); os.dup2(native_file.fileno(),2)
    llm=Llama(model_path=str(model_path),n_ctx=8192,n_batch=256,n_gpu_layers=-1,logits_all=True,seed=42,verbose=True)
finally:
    sys.stdout.flush(); sys.stderr.flush()
    os.dup2(saved[0],1); os.dup2(saved[1],2)
    os.close(saved[0]); os.close(saved[1])
    os.fsync(native_file.fileno())
    shutil.copy2(native_path,OUT/native_path.name)
load_log=native_path.read_text(encoding='utf-8',errors='replace')
layer_reports=re.findall(r'offloaded\\s+(\\d+)\\s*/\\s*(\\d+)\\s+layers?\\s+to\\s+GPU',load_log,re.I)
all_layers_offloaded=bool(layer_reports) and any(int(a)==int(b) and int(b)>0 for a,b in layer_reports)
post_gpu=subprocess.run([_nvidia_smi],text=True,capture_output=True,check=True).stdout
(OUT/'nvidia_smi_after_model_load.txt').write_text(post_gpu,encoding='utf-8')
summary=dict(status='loaded',gpu=gpu,all_layers_offloaded=all_layers_offloaded,layer_reports=layer_reports,
             model_sha256=model_digest,python=sys.version,packages={p:importlib.metadata.version(p) for p in
             ('llama-cpp-python','transformers','huggingface-hub','tokenizers','numpy','scikit-learn')},
             context_tokens=8192,n_batch=256,n_gpu_layers=-1,native_log_bytes=native_path.stat().st_size)
atomic_json(OUT/'load_summary.json',summary)
if not all_layers_offloaded:
    raise RuntimeError('Test blocked: full GPU offload was not verified. Inspect native log and post-load nvidia-smi; do not infer or silently change GPU.')
for label,hf_id in zip(('0','1'),label_ids):
    if llm.tokenize(label.encode(),add_bos=False,special=False)!=[hf_id]: raise ValueError('Label tokenizer mismatch')
llm.verbose=False
note(f'Offload verified: {layer_reports}; full log saved to Drive.')
''')
old=''.join(nb['cells'][7]['source'])
scoring=old[:old.index("records_path = OUT")]
setcell(7,scoring+'''
expected={r['id']:r for r in rows}
done={}
def checkpoint_path(uid): return CHECKPOINTS/(hashlib.sha256(uid.encode()).hexdigest()+'.json')
def validate_record(r,item):
    for key in ('id','dataset','split','arm','seed','prompt_sha256'):
        if r.get(key)!=item[key]: raise ValueError('Checkpoint identity mismatch: '+item['id']+' '+key)
    if r.get('model_sha256')!=model_digest or r.get('threshold_lock_sha256')!=seal:
        raise ValueError('Checkpoint model/threshold seal mismatch: '+item['id'])
    if r.get('tau')!=THRESHOLDS[item['dataset']] or not r.get('all_layers_offloaded'):
        raise ValueError('Checkpoint threshold/offload mismatch: '+item['id'])
    if not all(math.isfinite(r[k]) for k in ('s','logprob_0','logprob_1')): raise ValueError('Invalid checkpoint scores')
available_checkpoints={p.name:p for p in CHECKPOINTS.glob('*.json')}
for uid,item in expected.items():
    p=checkpoint_path(uid)
    if p.name not in available_checkpoints: continue
    try: r=json.loads(p.read_text(encoding='utf-8'))
    except (json.JSONDecodeError,UnicodeDecodeError):
        quarantine=p.with_suffix('.corrupt.'+str(time.time_ns()))
        os.replace(p,quarantine)
        note('Quarantined incomplete checkpoint: '+uid)
        continue
    validate_record(r,item); done[uid]=r
note(f'Resume: {len(done)}/{len(rows)} saved; {len(rows)-len(done)} remaining')
durations=[]
try:
    for item in rows:
        if item['id'] in done: continue
        reserve=max(120,2*max(durations,default=60))
        if time.monotonic()-PILOT_START+reserve>=MAX_RUNTIME_SECONDS:
            note('Safety budget reached; rerun from top in next L4 session to resume.'); break
        chat=tokenizer.apply_chat_template([{'role':'user','content':item['prompt']}],tokenize=False,add_generation_prompt=True)
        hf_ids=tokenizer.apply_chat_template([{'role':'user','content':item['prompt']}],tokenize=True,add_generation_prompt=True)
        gguf_ids=llm.tokenize(chat.encode(),add_bos=False,special=True)
        if list(hf_ids)!=gguf_ids or len(gguf_ids)>8192: raise ValueError('Tokenizer/context mismatch: '+item['id'])
        started=time.monotonic(); llm.reset(); llm.eval(gguf_ids)
        scores=binary_scores(llm.scores[llm.n_tokens-1],label_ids)
        raw=llm.detokenize([scores['greedy_token_id']]).decode('utf-8',errors='replace').strip()
        tau=THRESHOLDS[item['dataset']]
        r={k:item[k] for k in ('id','dataset','split','arm','seed','prompt_variant','prompt_sha256')}
        r.update(scores,raw=raw,response_valid=raw in ('0','1'),valid=True,tau=tau,pred_tau=int(scores['s']>=tau),
                 threshold_lock_sha256=seal,model_sha256=model_digest,tokenizer_revision=TOKENIZER_REVISION,
                 backend='llama-cpp-python',llama_cpp_python=llama_cpp_version,gpu=gpu,all_layers_offloaded=True,
                 prompt_tokens=len(gguf_ids),token_ids={'0':label_ids[0],'1':label_ids[1]},elapsed_s=time.monotonic()-started,
                 completed_utc=datetime.now(timezone.utc).isoformat(),test_only=True)
        # Retain a local pending copy if Drive fails. Stop before evaluating another sample.
        atomic_json(LOCAL_OUT/'pending_record.json',r)
        atomic_json(checkpoint_path(item['id']),r)
        validate_record(json.loads(checkpoint_path(item['id']).read_text()),item)
        done[item['id']]=r; durations.append(r['elapsed_s'])
        note(f'{item["id"]}: s={scores["s"]:.8f}, pred_tau={r["pred_tau"]}, seconds={r["elapsed_s"]:.2f}',display=False)
        if len(done)%50==0:
            note(f'Progress {len(done)}/{len(rows)}; remaining {len(rows)-len(done)}')
            shutil.copy2(LOCAL_OUT/'events.log',OUT/'events_latest_session.log')
            os.fsync(native_file.fileno()); shutil.copy2(native_path,OUT/native_path.name)
finally:
    # Authoritative per-ID checkpoints survive even when an interrupted session cannot reach here.
    local_records=LOCAL_OUT/'records.jsonl'
    with local_records.open('w',encoding='utf-8') as f:
        for uid in sorted(done): f.write(json.dumps(done[uid],ensure_ascii=False,allow_nan=False)+'\\n')
    target=OUT/'records.jsonl'; temp=OUT/'records.jsonl.tmp'
    shutil.copy2(local_records,temp); os.replace(temp,target)
    atomic_json(OUT/'test_status.json',dict(status='complete' if len(done)==len(rows) else 'incomplete',
                expected=len(rows),records_written=len(done),thresholds=THRESHOLDS,threshold_lock_sha256=seal,
                all_layers_offloaded=all_layers_offloaded,runtime_cap_seconds=MAX_RUNTIME_SECONDS))
    os.fsync(native_file.fileno()); shutil.copy2(native_path,OUT/native_path.name)
    shutil.copy2(LOCAL_OUT/'events.log',OUT/'events_latest_session.log')
    archive=shutil.make_archive(str(WORK/'b1h2_test_output'),'zip',root_dir=OUT)
    shutil.copy2(archive,DRIVE_DIR/'b1h2_test_output.zip')
    note(f'Preserved {len(done)}/{len(rows)} records; Drive archive: {DRIVE_DIR / "b1h2_test_output.zip"}')
''')
for idx in (6,7):
    source=''.join(nb['cells'][idx]['source'])
    source=source.replace('OUT/native_path.name','SESSION_LOG_DIR/native_path.name').replace("OUT/'nvidia_smi_after_model_load.txt'","SESSION_LOG_DIR/'nvidia_smi_after_model_load.txt'").replace("OUT/'load_summary.json'","SESSION_LOG_DIR/'load_summary.json'").replace("OUT/'events_latest_session.log'","SESSION_LOG_DIR/'events.log'")
    setcell(idx,source)
for i,c in enumerate(nb['cells']):
    if c['cell_type']=='code': compile(''.join(c['source']),f'cell_{i}','exec')
nb['metadata']['colab']={'name':'colab_l4_b1h2_test_20261106.ipynb','provenance':[]}
nb['metadata'].pop('widgets',None)
for cell in nb['cells']: cell['metadata']={}
target=BASE/'notebooks/colab_l4_b1h2_test_20261106.ipynb'
target.write_text(json.dumps(nb,ensure_ascii=False,indent=1),encoding='utf-8')
print(target)
