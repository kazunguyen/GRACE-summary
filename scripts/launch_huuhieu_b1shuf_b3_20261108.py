"""Authorized two-job HU launch. No client-side quota veto or model fallback."""
import argparse
import ast
import base64
import hashlib
import importlib.util
import json
import os
import shutil
import sys
from datetime import datetime,timezone
from pathlib import Path
from zipfile import ZipFile

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'Runs-management/huuhieu_b1shuf_b3_launch_20261108'
OWNER='huuhieu3333'


def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,data):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def prepare():
    if BASE.exists():raise ValueError('Preserve existing launch stage')
    latest=ROOT/'Runs-management/b1_shuf_download_20261108_231129'
    audit=read(latest/'checkpoint_audit.json')
    assert audit['total_done']==6416 and audit['continuation_integrity']=='PASS_LAUNCH_CONTRACT'
    checkpoint=latest/'b1_shuf_locked_20261108_checkpoint.zip'
    assert sha(checkpoint)==audit['checkpoint_sha256']
    # Reuse the reviewed worker/helper and replace only checkpoint pins/timebox.
    previous=ROOT/'Runs-management/locked_continuations_20261108/b1_shuf_resume_huuhieu3333_20261108_v2'
    nb=read(previous/'kernel/notebook.ipynb')
    with ZipFile(checkpoint) as z:
        assert z.testzip() is None
        members={n:hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if not n.endswith('/')}
    source=''.join(nb['cells'][3]['source']);tree=ast.parse(source)
    replacements={'EXPECTED_CHECKPOINT_FILES':repr(members),'EXPECTED_CHECKPOINT_SHA':repr(sha(checkpoint))}
    lines=source.splitlines(keepends=True)
    for node in reversed(tree.body):
        if isinstance(node,ast.Assign) and isinstance(node.targets[0],ast.Name) and node.targets[0].id in replacements:
            name=node.targets[0].id;lines[node.lineno-1:node.end_lineno]=[name+' = '+replacements[name]+'\n']
    nb['cells'][3]['source']=''.join(lines).splitlines(keepends=True)
    nb['cells'][2]['source']=''.join(nb['cells'][2]['source']).replace('MAX_RUNTIME_HOURS = 1.5','MAX_RUNTIME_HOURS = 9').splitlines(keepends=True)
    install=''.join(nb['cells'][4]['source'])
    install=install.replace("packages += ['typing-extensions", "packages += ['scipy==1.16.3', 'typing-extensions")
    nb['cells'][4]['source']=install.splitlines(keepends=True)
    nb['cells'][5]['source'] += ["\nassert importlib.metadata.version('scipy') == '1.16.3', 'SciPy differs from both prior sessions'\n"]
    nb['cells'][0]['source']=['# B1-shuf: resume verified 6416 records\n',
        'Same input/worker/launch contract; 9h deadline; SciPy1.16.3 matches both prior sessions.\n']
    stage=BASE/'b1_shuf';data=stage/'dataset';data.mkdir(parents=True)
    shutil.copy2(checkpoint,data/checkpoint.name)
    original=ROOT/'Runs-management/locked_continuations_20261108/b1_shuf/dataset/grace_locked_b1_shuf_20261108.zip'
    assert sha(original)=='f803e8c5d73985cb4857c203311e71333eb57f9a3a04230182371b4563c867f8'
    shutil.copy2(original,data/original.name)
    dataset=OWNER+'/grace-b1-shuf-checkpoint-6416-20261108'
    dump(data/'dataset-metadata.json',{'id':dataset,'title':'GRACE B1 shuf checkpoint6416','isPrivate':True,'licenses':[{'name':'other'}]})
    meta=read(previous/'kernel/kernel-metadata.json')
    meta.update(id=OWNER+'/grace-b1-shuf-resume-6416-20261108',title='GRACE B1 shuf resume6416',
        dataset_sources=[dataset],session_timeout_seconds=32400,machine_shape='NvidiaTeslaT4')
    finalize(stage,nb,meta,{'resume_count':6416,'remaining':8602,'checkpoint_sha256':sha(checkpoint),
        'runtime_contract_sha256':audit['runtime_contract_sha256'],'worker_sha256':read(previous/'delivery.json')['worker_sha256'],
        'supplemental_scipy_pin':'1.16.3: observed in both parent session pip_freeze; historical contract identity retained'})

    # B3: same pinned worker/runtime for both independently validated inputs.
    b3base=ROOT/'Runs-management/b3_verified_patch_v1'
    dv=b3base/'release_20261108_v6/delivery';rv=b3base/'release_20261108_v7_reveal/delivery'
    assert read(b3base/'v6_acceptance_verified_20261108/acceptance.json')['cpu_verdict']=='PASS'
    assert read(b3base/'v7_reveal_acceptance_20261108/acceptance.json')['cpu_verdict']=='PASS'
    for name in ['kaggle_inference.py','b3_delivery_runtime.py','grace_runtime_contract.py','inference_runtime_lock.json']:
        assert (dv/name).read_bytes()==(rv/name).read_bytes()
    definitions={};extra=''
    for ds,folder in [('devign',dv),('reveal',rv)]:
        manifest=read(folder.parent/'release_manifest.json')
        for name,h in manifest['files_sha256'].items():assert sha(folder/name)==h
        raw=(folder/'inference_input_manifest.json').read_bytes();pin=hashlib.sha256(raw).hexdigest()
        path='/kaggle/working/b3_input_'+ds+'.json';definitions[ds]={'path':path,'sha256':pin}
        extra+=f"Path({path!r}).write_bytes(base64.b64decode({base64.b64encode(raw).decode()!r}))\n"
    coordinator=ROOT/'scripts/b3_dual_runtime_coordinator.py';raw=coordinator.read_bytes()
    extra+=f"Path('/kaggle/working/b3_dual_runtime_coordinator.py').write_bytes(base64.b64decode({base64.b64encode(raw).decode()!r}))\n"
    extra+=f"assert digest('/kaggle/working/b3_dual_runtime_coordinator.py') == {sha(coordinator)!r}\n"
    nb=read(dv/'notebook.ipynb')
    nb['cells'][0]['source']=['# New B3: Devign then REVEAL, fixed order\n',
        'Independent approved input roots; native gates before score; no historical threshold/test/extra arm.\n']
    nb['cells'][2]['source'] += extra.splitlines(keepends=True)
    nb['cells'][3]['source']=(f"DEFINITIONS = {definitions!r}\n"+'''
KAGGLE_INPUT_ROOT = Path('/kaggle/input')
OUT_ROOT = Path('/kaggle/working/b3_new_dual_validation_20261108')
MAX_RUNTIME_HOURS = 9
if OUT_ROOT.exists(): raise ValueError('Existing output; explicit verified resume is required')
''').splitlines(keepends=True)
    nb['cells'][4]['source']='''import b3_dual_runtime_coordinator as dual
PREPARED = dual.prepare(KAGGLE_INPUT_ROOT, Path('/kaggle/working/b3_verified_bundles'), DEFINITIONS)
models = sorted(KAGGLE_INPUT_ROOT.rglob(RUNTIME['model']['filename']))
if len(models) != 1: raise ValueError('Need exactly one locked model input')
MODEL_PATH = models[0]
note('Both dataset input roots verified before model/build; fixed order Devign then REVEAL')
'''.splitlines(keepends=True)
    nb['cells'][8]['source']='''try:
    result = dual.run(PREPARED, MODEL_PATH, OUT_ROOT, SESSION_STARTED + MAX_RUNTIME_HOURS*3600,
        Path('/kaggle/working/kaggle_inference.py'), Path('/kaggle/working/inference_input_manifest.json'), DIAG)
    note('B3 dual status: '+json.dumps(result))
finally:
    if OUT_ROOT.exists():
        shutil.make_archive('/kaggle/working/b3_new_dual_validation_checkpoint', 'zip', root_dir=OUT_ROOT)
    diagnostics_zip()
'''.splitlines(keepends=True)
    meta=read(rv/'kernel-metadata.json')
    meta.update(id=OWNER+'/grace-b3-new-dual-validation-20261108',title='GRACE B3 new Devign and REVEAL validation',
        dataset_sources=[OWNER+'/grace-b3-v6-devign-inputs',OWNER+'/grace-b3-v7-reveal-inputs'],
        session_timeout_seconds=32400,machine_shape='NvidiaTeslaT4')
    finalize(BASE/'b3_dual',nb,meta,{'datasets':definitions,'coordinator_sha256':sha(coordinator),
        'runtime_contract_sha256':sha(dv/'inference_runtime_lock.json'),'fixed_order':['devign','reveal'],
        'scope':'B3 validation seed42 only; no threshold fit or test','counts':{'devign':2732,'reveal':2273}})
    print('Prepared two notebooks. Private B1 dataset publication and CPU preflight still required.')


def finalize(stage,nb,meta,details):
    for i,cell in enumerate(nb['cells']):
        if cell['cell_type']=='code':
            ast.parse(''.join(cell['source']),filename=f'{stage.name}:cell{i}')
            cell['execution_count']=None;cell['outputs']=[]
    dump(stage/'kernel/notebook.ipynb',nb);dump(stage/'kernel/kernel-metadata.json',meta)
    dump(stage/'delivery.json',dict(details,owner=OWNER,ref=meta['id'],notebook_sha256=sha(stage/'kernel/notebook.ipynb'),
        quota_policy='User explicitly authorized launch without client quota veto; server limits still apply',
        requested_machine_shape='NvidiaTeslaT4',requested_session_timeout_seconds=32400))


def api_client():
    sys.path.insert(0,str(ROOT/'Runs-management/locked_continuations_20261108/tooling'))
    config=ROOT/'Runs-management/kaggle_huuhieu_config';credentials=read(config/'kaggle.json')
    assert credentials['username']==OWNER
    os.environ.update(KAGGLE_USERNAME=OWNER,KAGGLE_KEY=credentials['key'],KAGGLE_CONFIG_DIR=str(config))
    if credentials['key'].startswith('KGAT_'):os.environ['KAGGLE_API_TOKEN']=credentials['key']
    from kaggle.api.kaggle_api_extended import KaggleApi
    api=KaggleApi();api.authenticate();return api


def remote(kind,action):
    stage=BASE/kind;delivery=read(stage/'delivery.json');meta=read(stage/'kernel/kernel-metadata.json')
    effective_ref=meta['id']
    if (stage/'launch.json').is_file():
        from urllib.parse import urlsplit
        receipt=read(stage/'launch.json')
        path=urlsplit(receipt['url']).path
        effective_ref='/'.join(path.strip('/').split('/')[-2:])
        if effective_ref.split('/')[0]!=OWNER:raise ValueError('Unexpected launch owner')
    api=api_client();now=datetime.now(timezone.utc).isoformat()
    if action=='upload':
        assert kind=='b1_shuf'
        if (stage/'dataset_upload.json').exists():raise ValueError('Upload already recorded')
        response=api.dataset_create_new(str(stage/'dataset'),public=False,quiet=True,convert_to_csv=False)
        result={'at_utc':now,'dataset':meta['dataset_sources'][0],'status':str(getattr(response,'status','')),'error':str(getattr(response,'error','')),'private_requested':True}
        dump(stage/'dataset_upload.json',result)
        if result['error']:raise ValueError('Private dataset creation failed')
    elif action=='launch':
        assert read(BASE/'cpu_preflight.json')['verdict']=='PASS'
        if (stage/'launch.json').exists():raise ValueError('Launch already recorded; inspect status')
        from kagglesdk.kernels.types.kernels_api_service import ApiSaveKernelRequest,ApiGetKernelSessionStatusRequest
        if kind=='b1_shuf':
            old=ApiGetKernelSessionStatusRequest();old.user_name=OWNER;old.kernel_slug='grace-b1-shuf-resume-20261108'
            with api.build_kaggle_client() as client:state=client.kernels.kernels_api_client.get_kernel_session_status(old)
            if state.status.name not in ('COMPLETE','ERROR','CANCEL_ACKNOWLEDGED'):raise ValueError('Old B1-shuf session still active')
        for source in meta['dataset_sources']:
            if str(api.dataset_status(source)).lower()!='ready':raise ValueError('Input dataset not ready: '+source)
        assert sha(stage/'kernel/notebook.ipynb')==delivery['notebook_sha256']
        nb=read(stage/'kernel/notebook.ipynb')
        for c in nb['cells']:c['source']=''.join(c['source'])
        request=ApiSaveKernelRequest();request.slug=meta['id'];request.new_title=meta['title'];request.text=json.dumps(nb,ensure_ascii=False)
        request.language='python';request.kernel_type='notebook';request.is_private=True
        request.enable_gpu=True;request.enable_tpu=False;request.enable_internet=True
        request.machine_shape='NvidiaTeslaT4';request.session_timeout_seconds=32400
        request.dataset_data_sources=meta['dataset_sources'];request.kernel_data_sources=meta['kernel_sources']
        request.competition_data_sources=[];request.model_data_sources=[];request.category_ids=[]
        with api.build_kaggle_client() as client:response=client.kernels.kernels_api_client.save_kernel(request)
        result={'at_utc':now,'ref':response.ref,'url':response.url,'version':response.version_number,
            'error':response.error,'invalid_dataset_sources':response.invalid_dataset_sources,
            'invalid_kernel_sources':response.invalid_kernel_sources,'machine_shape_requested':request.machine_shape}
        dump(stage/'launch.json',result)
        if result['error'] or result['invalid_dataset_sources'] or result['invalid_kernel_sources']:raise ValueError('Kaggle rejected launch; inspect receipt')
    elif action=='verify':
        from kagglesdk.kernels.types.kernels_api_service import ApiGetKernelRequest
        request=ApiGetKernelRequest();request.user_name=OWNER;request.kernel_slug=effective_ref.split('/')[1]
        with api.build_kaggle_client() as client:response=client.kernels.kernels_api_client.get_kernel(request)
        nb=json.loads(response.blob.source);local=read(stage/'kernel/notebook.ipynb')
        source=lambda n:[(c['cell_type'],''.join(c['source'])) for c in n['cells']]
        result={'at_utc':now,'ref':effective_ref,'requested_ref':meta['id'],'all_cell_sources_match':source(nb)==source(local),
            'machine_shape':response.metadata.machine_shape,'private':response.metadata.is_private,
            'gpu_enabled':response.metadata.enable_gpu,'version':response.metadata.current_version_number,
            'datasets':response.metadata.dataset_data_sources,'kernel_sources':response.metadata.kernel_data_sources}
        dump(stage/'remote_source.json',nb);dump(stage/'source_readback.json',result)
        assert result['all_cell_sources_match'] and result['machine_shape']=='NvidiaTeslaT4' and result['private'] and result['gpu_enabled']
    elif action=='status':
        response=api.kernels_status(effective_ref);result={'at_utc':now,'ref':effective_ref,'status':str(response.status),'failure_message':str(response.failure_message)}
        dump(stage/'status.json',result)
    elif action=='output':
        out=stage/'remote_output';out.mkdir(exist_ok=True)
        api.kernels_output(effective_ref,path=str(out),force=True,quiet=True);result={'output':str(out)}
    else:raise ValueError('Unsupported remote action')
    print(json.dumps(result,ensure_ascii=True),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['prepare','upload','launch','verify','status','output'])
    parser.add_argument('--kind',choices=['b1_shuf','b3_dual'])
    args=parser.parse_args()
    if args.action=='prepare':prepare()
    else:remote(args.kind,args.action)
