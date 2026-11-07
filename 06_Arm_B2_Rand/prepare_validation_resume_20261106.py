"""Update active B2-rand notebooks for validation-only continuation after I-11."""
import hashlib,json,zipfile
from pathlib import Path
from datetime import datetime,timezone

ROOT=Path(__file__).resolve().parents[1]
TARGETS=[ROOT/'Runs-management/kaggle_validation_6arms_20261104/02_kaggle_qwen_q4_b2_rand.ipynb',
         ROOT/'06_Arm_B2_Rand/notebooks/02_kaggle_qwen_q4_b2_rand.ipynb']
checkpoint=ROOT/'06_Arm_B2_Rand/output/kaggle_run_02/grace_b2_rand_checkpoint.zip'
if hashlib.sha256(checkpoint.read_bytes()).hexdigest()!='96ad982e681a1c910be5290d4454e67899cae934421b8b648fd6e387e32052a3':
    raise ValueError('I-11 source checkpoint hash changed')
pins={}
with zipfile.ZipFile(checkpoint) as z:
    for name in ('seed_42/devign/validation/records.jsonl','seed_42/reveal/validation/records.jsonl',
                 'seed_43/devign/validation/records.jsonl','seed_43/reveal/validation/records.jsonl'):
        raw=z.read(name);pins[name]=(len(raw),hashlib.sha256(raw).hexdigest())
nb=json.loads(TARGETS[0].read_text(encoding='utf-8'))
if 'PINNED_I11 =' in ''.join(nb['cells'][11]['source']):
    if TARGETS[0].read_bytes()!=TARGETS[1].read_bytes(): raise ValueError('Active notebook mirrors differ')
    print('I-11 validation-only update already applied; leaving the active notebooks unchanged')
    raise SystemExit(0)
def source(i):return ''.join(nb['cells'][i]['source'])
def put(i,value):nb['cells'][i]['source']=value.splitlines(keepends=True)
put(0,'''# B2-rand — chạy nốt validation từ checkpoint I-11

Add Input: bundle `grace_b2_rand_inputs.zip`, GGUF Q4_K_M đã pin và **checkpoint I-11 hoặc bản mới hơn cùng lineage**.
Checkpoint I-11 tại local: `06_Arm_B2_Rand/output/kaggle_run_02/grace_b2_rand_checkpoint.zip`.
I-11 có **7.789/15.015 validation record**: seed 42 đủ; seed 43 còn 2.221 ReVeal; seed 44 còn 5.005.
Notebook kiểm hash lịch sử, bỏ qua mẫu đã hoàn tất và chỉ chạy phần còn thiếu.

**Giới hạn tổng phiên 9 giờ, tính từ cell khởi tạo đầu tiên (bao gồm setup/build/model load).**
Dừng nhận mẫu mới trước hạn 10 phút để đóng gói. Watchdog dừng process con trước hạn 5 phút nếu cần.
Sau khi đủ validation, trạng thái là `validation_complete`, `awaiting_threshold_lock=true`.
**Dừng để người dùng chốt ngưỡng; không tự fit/khóa ngưỡng và không chạy test.**
Prompt seed 42/43/44 và seed inference mặc định của backend giữ đúng phiên B2-rand đang resume.
Chọn GPU **2×T4**; dùng cùng tài khoản/bundle/model như phiên Kaggle trước.
''')
s=source(1)
s=s.replace('from datetime import datetime, timezone','from datetime import datetime, timezone\nimport threading, signal\n\n# Re-running setup in the same session must not restart the time budget.\nif "SESSION_STARTED_EPOCH" not in globals(): SESSION_STARTED_EPOCH=time.time()\nSESSION_DEADLINE_EPOCH=SESSION_STARTED_EPOCH+9*3600')
s=s.replace("text=True, encoding='utf-8', errors='replace', bufsize=1, env=env)","text=True, encoding='utf-8', errors='replace', bufsize=1, env=env, start_new_session=True)\n        def stop_process_group():\n            if proc.poll() is not None: return\n            note(f'Watchdog: stopping {name}; preserving time for checkpoint export')\n            try:\n                os.killpg(proc.pid, signal.SIGKILL)\n            except ProcessLookupError: pass\n        watchdog=threading.Timer(max(0,SESSION_DEADLINE_EPOCH-300-time.time()),stop_process_group)\n        watchdog.daemon=True\n        watchdog.start()")
s=s.replace('        code = proc.wait()','        code = proc.wait()\n        watchdog.cancel()')
put(1,s)
s=source(3)
s=s.replace('# Bắt buộc tiếp tục từ I-09 hoặc checkpoint mới hơn có cùng lịch sử.','# Bắt buộc tiếp tục từ I-11 hoặc bản mới hơn chứa nguyên lịch sử I-09/I-11.')
s=s.replace('MAX_RUNTIME_HOURS = 6','MAX_RUNTIME_HOURS = 9')
s=s.replace('MAX_RUNTIME_HOURS = 9','MAX_RUNTIME_HOURS = 9\nRUN_DEADLINE_EPOCH = SESSION_STARTED_EPOCH + MAX_RUNTIME_HOURS * 3600')
s=s.replace("EXPECTED_RUNS = [('devign', 'validation'), ('reveal', 'validation'),\n                 ('devign', 'test'), ('reveal', 'test')]","EXPECTED_RUNS = [('devign', 'validation'), ('reveal', 'validation')]")
put(3,s)
s=source(4).replace('# Đọc đúng ZIP tổng hoặc 12 ZIP split;','# Đọc bundle lịch sử; chỉ materialize 6 tập validation;')
s=s.replace('12 tập đã audit','6 tập validation đã audit').replace('12 tập prompt khớp','6 tập validation khớp')
put(4,s)
s=source(6).replace("'transformers==4.57.1', 'huggingface_hub', 'scikit-learn==1.5.2'", "'numpy==2.1.3', 'transformers==4.57.1', 'huggingface_hub==0.36.2', 'tokenizers==0.22.2', 'scikit-learn==1.5.2'")
put(6,s)
s=source(10)
needle='    from llama_cpp import Llama, __version__ as llama_version'
assert needle in s
s=s.replace(needle,"    # Hard gate: a direct CLI invocation must also refuse test before model loading.\n    if arm != 'B2-rand' or any(split != 'validation' for _,split,_,_ in runs):\n        raise ValueError('Validation-only runner: test is blocked; stop and lock thresholds separately')\n"+needle,1)
s=s.replace("choices=['B2', 'B2-rand']","choices=['B2-rand']")
put(10,s)
s=source(11)
s=s.replace('# Khôi phục checkpoint I-09 (ZIP hoặc thư mục Kaggle đã giải nén) và kiểm tra lineage.','# Khôi phục checkpoint I-11 hoặc descendant; xác minh đầy đủ lịch sử I-09 và I-11.')
s=s.replace("raise ValueError('Notebook này chỉ tiếp tục I-09; phải bật RESUME_FROM_CHECKPOINT')","raise ValueError('Notebook này chỉ resume I-11 hoặc bản mới hơn; phải bật RESUME_FROM_CHECKPOINT')")
s=s.replace("raise FileNotFoundError('Add Input checkpoint I-09: grace_b2_rand_checkpoint.zip hoặc output đã giải nén.')","raise FileNotFoundError('Add Input checkpoint I-11: grace_b2_rand_checkpoint.zip hoặc output đã giải nén.')")
old="""if any(x[2] != loaded[0][2] for x in loaded[1:]):
    raise ValueError(f'Có nhiều checkpoint khác nội dung: {[str(x[0]) for x in loaded]}; đặt CHECKPOINT_INPUT_PATH chọn bản mới nhất.')
source, checkpoint_files, _ = loaded[0]"""
new="""# Choose a verified descendant rather than file mtime. Older attached Inputs may coexist.
def record_count(files):
    return sum(sum(bool(line.strip()) for line in raw.splitlines()) for name,raw in files.items()
               if name.endswith('/records.jsonl'))
loaded.sort(key=lambda item:record_count(item[1]),reverse=True)
source, checkpoint_files, _ = loaded[0]
for candidate,files,_ in loaded[1:]:
    for name,raw in files.items():
        if name.endswith('/records.jsonl') and not checkpoint_files.get(name,b'').startswith(raw):
            raise ValueError(f'Conflicting checkpoint history: {candidate} vs {source}; choose CHECKPOINT_INPUT_PATH explicitly')
note(f'Chosen checkpoint {source}: {record_count(checkpoint_files)} records including preserved donor history')"""
assert old in s;s=s.replace(old,new)
needle="note('Đã xác nhận 4.798 record I-09 và output donor; không inference lại donor')"
addition="\n\n# I-11 is the minimum resumable checkpoint: preserve all 7,789 existing validation rows.\nPINNED_I11 = "+repr(pins)+"\nfor name,(size,expected_hash) in PINNED_I11.items():\n    path=OUT_ROOT/name\n    if not path.is_file(): raise ValueError(f'Checkpoint lacks I-11 data: {name}; attach the latest I-11 checkpoint')\n    with path.open('rb') as f: prefix=f.read(size)\n    if len(prefix)!=size or hashlib.sha256(prefix).hexdigest()!=expected_hash:\n        raise ValueError(f'Checkpoint older than/conflicting with I-11: {name}; attach kaggle_run_02/grace_b2_rand_checkpoint.zip')\nnote('Verified all 7,789 I-11 validation records; skip completed IDs, resume remaining validation only')\n# B2 donor legacy test data is preserved, but B2-rand test records are forbidden.\nfor seed in SEEDS:\n    for dataset in ('devign','reveal'):\n        if (OUT_ROOT/f'seed_{seed}'/dataset/'test'/'records.jsonl').exists():\n            raise ValueError('B2-rand test records already present; use a separate workflow after threshold locking')\n"
assert needle in s;s=s.replace(needle,needle+addition)
s=s.replace('RUN_DEADLINE_EPOCH = time.time() + MAX_RUNTIME_HOURS * 3600',"# The deadline was established in setup; do not grant another nine hours here.\nRUN_DEADLINE_EPOCH = SESSION_STARTED_EPOCH + MAX_RUNTIME_HOURS * 3600")
s=s.replace("'budget_hours':MAX_RUNTIME_HOURS,'validation_only':True,","'budget_hours':MAX_RUNTIME_HOURS,'session_started_epoch':SESSION_STARTED_EPOCH,'validation_only':True,\n             'awaiting_threshold_lock':state=='validation_complete','thresholds_fitted':False,'test_started':False,")
put(11,s)
put(12,"print('DỪNG: tải grace_b2_rand_checkpoint.zip và grace_diagnostics.zip từ Kaggle Output. Đủ 15.015 validation record thì chốt ngưỡng ở bước riêng; notebook này không fit ngưỡng và không chạy test.')\n")
for i,cell in enumerate(nb['cells']):
    if cell['cell_type']=='code':
        cell['outputs']=[];cell['execution_count']=None
        code=''.join(cell['source'])
        if code.startswith('%%writefile '):code=code.split('\n',1)[1]
        compile(code,f'cell_{i}','exec')
    cell['metadata']={}
nb['metadata'].pop('widgets',None)
raw=(json.dumps(nb,ensure_ascii=False,indent=1)+'\n').encode()
for p in TARGETS:p.write_bytes(raw)
out=ROOT/'06_Arm_B2_Rand/validation_resume_20261106';out.mkdir(exist_ok=True)
manifest=dict(created_utc=datetime.now(timezone.utc).isoformat(),scope='validation-only continuation after I-11',
              notebooks=[str(p.relative_to(ROOT)).replace('\\','/') for p in TARGETS],notebook_sha256=hashlib.sha256(raw).hexdigest(),
              checkpoint=str(checkpoint.relative_to(ROOT)).replace('\\','/'),checkpoint_sha256=hashlib.sha256(checkpoint.read_bytes()).hexdigest(),
              existing_validation=7789,expected_validation=15015,remaining_validation=7226,
              remaining_by_seed_dataset={'43/reveal':2221,'44/devign':2732,'44/reveal':2273},
              budget_hours=9,budget_includes_setup=True,reserve_seconds=600,inference_seed='backend default (unchanged)',prompt_seeds=[42,43,44],
              auto_fit_threshold=False,auto_test=False)
(out/'delivery_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(manifest,ensure_ascii=False,indent=2))
