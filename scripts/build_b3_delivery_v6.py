"""Create a new immutable B3 delivery from previously audited prompt bytes.

Never modifies v5 or frozen assets. Does not assert REVEAL readiness or GPU pass.
"""
import ast
import base64
import hashlib
import importlib.util
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('b3_delivery_runtime', ROOT/'scripts/b3_delivery_runtime.py')
io = importlib.util.module_from_spec(spec)
spec.loader.exec_module(io)
PARENT = ROOT/'Runs-management/b3_verified_patch_v1/release_20261108_v5'
DEST = ROOT/'Runs-management/b3_verified_patch_v1/release_20261108_v6'


def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def replace_function(source, name, replacement):
    node = next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name==name)
    lines = source.splitlines(keepends=True)
    return ''.join(lines[:node.lineno-1])+replacement+'\n\n'+''.join(lines[node.end_lineno:])


def create(destination=DEST):
    destination=Path(destination)
    if destination.exists():
        raise ValueError('Release exists; refusing overwrite')
    old = read(PARENT/'delivery/notebook.ipynb')
    cells={i:''.join(c['source']) for i,c in enumerate(old['cells']) if c['cell_type']=='code'}
    embedded=ast.parse(cells[2])
    helper=ast.literal_eval(next(n.value for n in embedded.body if isinstance(n,ast.Assign)
        and any(isinstance(t,ast.Name) and t.id=='CONTRACT_HELPER_CODE' for t in n.targets)))
    # Use the same parser that tests call; keep constructor/offload fail-closed.
    start=helper.index('    reports = re.findall(',helper.index('def load_locked_model'))
    end=helper.index('    return model',start)
    helper=helper[:start]+'''    from b3_delivery_runtime import native_log_check
    try:
        native_log_check(text, c)
    except Exception:
        model.close()
        raise
'''+helper[end:]
    worker=cells[7].split('\n',1)[1]
    marker='RUNTIME = load_contract()'
    worker=worker.replace(marker,marker+'''
from b3_delivery_runtime import load_input_root, validate_bundle, run_identity, checked_records
INPUT_ROOT = load_input_root('/kaggle/working/inference_input_manifest.json', os.environ['B3_INPUT_ROOT_SHA256'])
''',1)
    worker=replace_function(worker,'load_bundle', '''def load_bundle(bundle):
    manifest, rows, _ = validate_bundle(bundle, INPUT_ROOT)
    return manifest, rows''')
    worker=worker.replace("'bundle_sha256': sha256(bundle),", "'bundle_sha256': sha256(bundle),\n            'b3_input_identity': run_identity(INPUT_ROOT),",1)
    anchor="        identity_file = out / 'run_manifest.json'"
    worker=worker.replace(anchor,"        checked_records(status_path.parent, INPUT_ROOT, rows)\n"+anchor,1)
    code={'b3_delivery_runtime.py':(ROOT/'scripts/b3_delivery_runtime.py').read_bytes(),
        'grace_runtime_contract.py':helper.encode('utf-8'), 'kaggle_inference.py':worker.encode('utf-8'),
        'inference_runtime_lock.json':(ROOT/'configs/inference_runtime_lock.json').read_bytes()}
    for name,raw in code.items():
        if name.endswith('.py'):ast.parse(raw.decode('utf-8'))
    census_path=PARENT/'validation/devign/validation_census.jsonl'
    census_raw=census_path.read_bytes()
    if io.sha(census_raw)!='dee4a33009f4ecbf42b96e6f18c5f4390d5f0a620370af925bae0f2cceeb7e59':
        raise ValueError('Audited census fingerprint changed')
    census=[json.loads(l) for l in census_raw.decode('utf-8').splitlines() if l.strip()]
    freeze=ROOT/'01_Author_Baseline_Unified/output/research_freeze_20261101/devign'
    label_source=freeze/'validation_raw.jsonl'
    labels={}
    for line in label_source.read_text(encoding='utf-8').splitlines():
        row=json.loads(line)
        if row['id'] in labels or type(row['target']) is not int or row['target'] not in (0,1):
            raise ValueError('Invalid frozen label population')
        labels[row['id']]=row['target']
    if len(census)!=2732 or len({r['target_id'] for r in census})!=2732 or set(labels)!={r['target_id'] for r in census}:
        raise ValueError('Frozen/census population mismatch')
    rows=[]
    for r in census:
        if r['status']!='RENDERED' or io.sha(r['prompt'].encode())!=r['prompt_sha256']:
            raise ValueError('Prompt not audited')
        rows.append({'id':r['target_id'],'dataset':'devign','split':'validation',
            'label':labels[r['target_id']],'prompt':r['prompt'],'prompt_sha256':r['prompt_sha256']})
    runtime=json.loads(code['inference_runtime_lock.json'])
    scope={'arm':'B3','dataset':'devign','split':'validation','seed':42,'count':2732}
    now=datetime.now(timezone.utc).isoformat()
    members={'prompts.jsonl':b''.join((json.dumps(r,ensure_ascii=False)+'\n').encode('utf-8') for r in rows),
        'audited_census.jsonl':census_raw,'labels.json':io.encoded(labels)}
    # Source manifests are explicitly historical evidence, not rewritten v6 claims.
    for name,path in {
        'evidence/parent_inputs_manifest.json':PARENT/'inputs_manifest.json',
        'evidence/parent_pool_manifest.json':PARENT/'pools/pool_manifest.json',
        'evidence/parent_prompt_manifest.json':PARENT/'validation/validation_prompt_manifest.json',
        'evidence/eligible_pairs.devign.jsonl':PARENT/'pools/eligible_pairs.devign.jsonl',
        'evidence/review_hieu.json':PARENT/'reviews/submitted/review_hieu.json',
        'evidence/review_dung.json':PARENT/'reviews/submitted/review_dung.json',
    }.items():members[name]=path.read_bytes()
    bm={'schema_version':1,'release_id':'release_20261108_v6','parent_release':'release_20261108_v5',
        'method_id':'b3-verified-patch-v1','scope':scope,'arm':'B3','dataset':'devign','split':'validation','seed':42,
        'count':2732,'prompts_sha256':io.sha(members['prompts.jsonl']),
        'model_repo':runtime['model']['repo'],'quantization':runtime['model']['quantization'],
        'tokenizer':runtime['tokenizer']['repo'],'tokenizer_revision':runtime['tokenizer']['revision'],
        'prompt_budget_tokens':runtime['constructor']['n_ctx'],
        'files_sha256':{k:io.sha(v) for k,v in members.items()}}
    bm['manifest_seal_sha256']=io.seal(bm,'manifest_seal_sha256')
    members['bundle_manifest.json']=io.encoded(bm)
    # All calculations above are read-only. Publishing occurs in new destination only.
    destination.mkdir(parents=True)
    delivery=destination/'delivery';delivery.mkdir()
    for name,raw in code.items():(delivery/name).write_bytes(raw)
    bundle_name='b3_devign_validation_v6.zip'
    io.write_zip(delivery/bundle_name,members)
    try:head=subprocess.check_output(['git','-c','safe.directory=*','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    except subprocess.CalledProcessError:raise ValueError('Cannot establish git identity')
    root={'schema_version':1,'release_id':'release_20261108_v6','parent_release':'release_20261108_v5',
        'method_id':'b3-verified-patch-v1','release_status':'CPU_PREPARED_NATIVE_PENDING','scope':scope,
        'excluded':{'reveal':'BLOCKED_EMPTY_VERIFIED_POOL','test':'BLOCKED_VALIDATION_THRESHOLD'},
        'bundle_filename':bundle_name,'bundle_sha256':io.sha((delivery/bundle_name).read_bytes()),
        'members_sha256':{k:io.sha(v) for k,v in members.items()},
        'prompt_content_sha256':io.sha(census_raw),'inference_rows_sha256':io.sha(members['prompts.jsonl']),
        'labels_source_sha256':io.sha(label_source.read_bytes()),
        'pool_sha256':io.sha(members['evidence/eligible_pairs.devign.jsonl']),
        'model_sha256':runtime['model']['sha256'],'runtime_contract_sha256':io.sha(code['inference_runtime_lock.json']),
        'tokenizer_revision':runtime['tokenizer']['revision'],'scoring':runtime['scoring']['name'],
        'code_sha256':{k:io.sha(v) for k,v in code.items()},'git_commit':head,
        'dirty_source_inventory':{str(p.relative_to(ROOT)):io.sha(p.read_bytes()) for p in [Path(__file__),ROOT/'scripts/b3_delivery_runtime.py']},
        'created_at_utc':now,'authority':{'scope':'Existing reviewed Devign Case08; operational fixes requested by user',
            'new_human_review_claimed':False,'new_scope_ratification_timestamp_claimed':False}}
    root['seal_sha256']=io.seal(root)
    root_raw=io.encoded(root);root_sha=io.sha(root_raw)
    (delivery/'inference_input_manifest.json').write_bytes(root_raw)
    bootstrap='''from pathlib import Path
import base64, hashlib, os, sys
'''
    for name,raw in {**code,'inference_input_manifest.json':root_raw}.items():
        bootstrap+=f"raw = base64.b64decode({base64.b64encode(raw).decode()!r})\n"
        bootstrap+=f"assert hashlib.sha256(raw).hexdigest() == {io.sha(raw)!r}\n"
        bootstrap+=f"Path('/kaggle/working/{name}').write_bytes(raw)\n"
    bootstrap+=f"os.environ['B3_INPUT_ROOT_SHA256'] = {root_sha!r}\n"
    bootstrap+='''sys.path.insert(0, '/kaggle/working')
from b3_delivery_runtime import (load_input_root, discover_bundle, validate_bundle,
    checked_records, restore_checkpoint, make_checkpoint, write_zip)
from grace_runtime_contract import assert_runtime, digest, load_contract, EXPECTED_CONTRACT_SHA256
RUNTIME_LOCK_PATH = Path('/kaggle/working/inference_runtime_lock.json')
RUNTIME = load_contract()
INPUT_ROOT = load_input_root('/kaggle/working/inference_input_manifest.json', os.environ['B3_INPUT_ROOT_SHA256'])
note('Independent input root verified: '+os.environ['B3_INPUT_ROOT_SHA256'])
'''
    config=cells[3].replace("BUNDLE_NAME = 'b3_devign_val_input.zip'",f'BUNDLE_NAME = {bundle_name!r}')
    config=config.replace("CHECKPOINT_INPUT_PATH = None", "CHECKPOINT_INPUT_PATH = None\nRESUME_REQUIRED = False")
    loader='''source = discover_bundle(KAGGLE_INPUT_ROOT, INPUT_ROOT)
bundle_manifest, prompts_records, members = validate_bundle(source, INPUT_ROOT)
BUNDLE_WORK.mkdir(parents=True, exist_ok=True)
bundle_file = BUNDLE_WORK / BUNDLE_NAME
write_zip(bundle_file, members)
# Prepared ZIP must reproduce the independently pinned archive in either input mode.
if digest(bundle_file) != INPUT_ROOT['bundle_sha256']:
    raise ValueError('Prepared bundle identity differs from pin')
if CHECKPOINT_INPUT_PATH is not None:
    restore_checkpoint(Path(CHECKPOINT_INPUT_PATH), OUT_ROOT, INPUT_ROOT, prompts_records)
elif RESUME_REQUIRED:
    raise ValueError('Resume requested without explicit checkpoint path')
elif OUT_ROOT.exists():
    raise ValueError('Fresh destination already exists; set explicit checkpoint path to resume')
else:
    OUT_ROOT.mkdir(parents=True)
records_done = checked_records(OUT_ROOT, INPUT_ROOT, prompts_records)
note(f'Input verified: {len(prompts_records)} prompts, {records_done} existing records')
'''
    execute='''deadline = SESSION_STARTED + MAX_RUNTIME_HOURS * 3600
status = OUT_ROOT / f'seed_{SEED}_status.json'
models = sorted(KAGGLE_INPUT_ROOT.rglob(MODEL_FILENAME))
if len(models) != 1:
    raise ValueError('Need exactly one locked model input')
state = 'error'
try:
    if records_done < EXPECTED_COUNT:
        run_logged([sys.executable, '-u', '/kaggle/working/kaggle_inference.py',
            '--model', str(models[0]), '--model-revision', 'local-input',
            '--seed', str(SEED), '--arm', ARM, '--expected-model-sha256', MODEL_SHA256,
            '--gpu-layers', str(GPU_LAYERS), '--deadline-epoch', str(deadline),
            '--checkpoint-reserve-seconds', str(CHECKPOINT_RESERVE_SECONDS), '--status', str(status),
            '--run', DATASET, SPLIT, str(bundle_file), str(OUT_ROOT / f'seed_{SEED}' / DATASET / SPLIT)],
            f'inference_seed_{SEED}')
    records_done = checked_records(OUT_ROOT, INPUT_ROOT, prompts_records)
    state = 'complete' if records_done == EXPECTED_COUNT else 'checkpointed'
finally:
    # Always try to preserve a valid checkpoint, including an inference exception.
    make_checkpoint(OUT_ROOT, Path('/kaggle/working')/CHECKPOINT_NAME, INPUT_ROOT, prompts_records)
    (OUT_ROOT/'batch_summary.json').write_text(json.dumps({'state':state,
        'input_root_sha256':os.environ['B3_INPUT_ROOT_SHA256'], 'historical_threshold_applied':False}),encoding='utf-8')
    diagnostics_zip()
'''
    sources=[cells[1],bootstrap,config,loader,cells[5],cells[6],
        "note('Worker and helper bytes were pinned during bootstrap; no replacement cell is used.')\n",execute]
    notebook={'nbformat':4,'nbformat_minor':5,'metadata':old.get('metadata',{}),'cells':[
        {'cell_type':'markdown','metadata':{},'source':['# B3 v6 — Devign validation; REVEAL blocked\n',
            'CPU-prepared delivery. Native GPU acceptance is required before claiming runtime PASS.\n',
            'Account: huuhieu3333. Set explicit checkpoint path and RESUME_REQUIRED=True for resume.\n']}]}
    for i,s in enumerate(sources):
        ast.parse(s)
        notebook['cells'].append({'cell_type':'code','id':f'b3-v6-{i}', 'metadata':{},'execution_count':None,'outputs':[], 'source':s.splitlines(keepends=True)})
    (delivery/'notebook.ipynb').write_bytes(io.encoded(notebook))
    metadata={'id':'huuhieu3333/grace-b3-v6-devign-validation','title':'GRACE B3 v6 Devign validation',
        'code_file':'notebook.ipynb','language':'python','kernel_type':'notebook','is_private':True,
        'enable_gpu':True,'enable_internet':True,'dataset_sources':['huuhieu3333/grace-b3-v6-devign-inputs'],
        'kernel_sources':[],'competition_sources':[]}
    (delivery/'kernel-metadata.json').write_bytes(io.encoded(metadata))
    (delivery/'launch_requirements.json').write_bytes(io.encoded({'owner':'huuhieu3333',
        'machine_shape':'NvidiaTeslaT4','session_timeout_seconds':32400,'model_dataset_source':'PENDING_ACCOUNT_ASSET_CHECK',
        'source_readback_required':True,'native_acceptance_required':True,'launch_state':'NOT_LAUNCHED'}))
    (delivery/'dataset-metadata.json').write_bytes(io.encoded({'id':'huuhieu3333/grace-b3-v6-devign-inputs',
        'title':'GRACE B3 v6 Devign inputs','licenses':[{'name':'other'}],'isPrivate':True}))
    manifest={'release_id':'release_20261108_v6','parent_release':'release_20261108_v5',
        'status':'CPU_PREPARED_NATIVE_AND_MOUNTS_PENDING','scope':scope,'reveal':'BLOCKED_EMPTY_POOL',
        'created_at_utc':now,'files_sha256':{p.name:io.sha(p.read_bytes()) for p in delivery.iterdir() if p.is_file()}}
    manifest['seal_sha256']=io.seal(manifest)
    (destination/'release_manifest.json').write_bytes(io.encoded(manifest))
    print(json.dumps({'release':str(destination),'input_root_sha256':root_sha,'status':manifest['status']}))
    return destination


if __name__=='__main__':create()
