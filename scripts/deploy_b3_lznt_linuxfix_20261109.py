"""New B3 execution revision: exact member-pinned directories on lznt123."""
import argparse
import base64
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import b3_delivery_runtime as io
import launch_huuhieu_b1shuf_b3_20261108 as transport

BASE=ROOT/'Runs-management/b3_lznt_linuxfix_20261109'
OWNER='lznt123'


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def sha(raw):return hashlib.sha256(raw).hexdigest()
def dump(path,obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(io.encoded(obj))


def prepare():
    stage=BASE/'b3_dual'
    if stage.exists():raise ValueError('Preserve prepared revision; create a new revision for changes')
    oldstage=ROOT/'Runs-management/huuhieu_b1shuf_b3_launch_20261108/b3_dual'
    assert read(oldstage/'status.json')['status'].endswith('ERROR')
    assert not list((oldstage/'remote_output').rglob('records.jsonl'))
    releases=ROOT/'Runs-management/b3_verified_patch_v1'
    dv=releases/'release_20261108_v6/delivery';rv=releases/'release_20261108_v7_reveal/delivery'
    worker=(dv/'kaggle_inference.py').read_text(encoding='utf-8')
    oldline="'bundle_sha256': sha256(bundle),"
    assert worker.count(oldline)==1
    # Keep original archive hash as source identity; validate the directory's
    # entire member inventory. Never hash a directory as a compressed archive.
    worker=worker.replace(oldline,"'bundle_sha256': INPUT_ROOT['bundle_sha256'],\n            'bundle_transport': 'verified_member_directory_v1',",1)
    common={name:(dv/name).read_bytes() for name in ['b3_delivery_runtime.py','grace_runtime_contract.py','inference_runtime_lock.json']}
    common['kaggle_inference.py']=worker.encode('utf-8')
    common['b3_dual_runtime_coordinator.py']=(ROOT/'scripts/b3_dual_runtime_coordinator.py').read_bytes()
    definitions={};bootstrap="from pathlib import Path\nimport base64, hashlib, os, sys\n"
    for name,raw in common.items():
        bootstrap+=f"raw=base64.b64decode({base64.b64encode(raw).decode()!r})\nassert hashlib.sha256(raw).hexdigest()=={sha(raw)!r}\nPath('/kaggle/working/{name}').write_bytes(raw)\n"
        (stage/'code').mkdir(parents=True,exist_ok=True);(stage/'code'/name).write_bytes(raw)
    for ds,folder,version in [('devign',dv,'v6'),('reveal',rv,'v7')]:
        manifest=read(folder.parent/'release_manifest.json')
        for name,h in manifest['files_sha256'].items():assert sha((folder/name).read_bytes())==h
        original=(folder/'inference_input_manifest.json').read_bytes();root=json.loads(original)
        root['source_input_release']=root['release_id']
        root['parent_input_root_sha256']=sha(original)
        root['source_input_git_commit']=root.pop('git_commit')
        root['source_input_dirty_inventory']=root.pop('dirty_source_inventory')
        root['execution_git_commit']=subprocess.check_output(['git','-c','safe.directory=*','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        root['execution_source_sha256']={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in [Path(__file__),ROOT/'scripts/b3_dual_runtime_coordinator.py',ROOT/'scripts/launch_huuhieu_b1shuf_b3_20261108.py']}
        root['execution_revision']='b3_linux_member_directory_v1_20261109'
        root['code_sha256']={k:sha(v) for k,v in common.items()}
        root['transport_policy']='Packed original archive hash OR complete independently pinned member directory; no recompression identity'
        root['seal_sha256']=io.seal(root)
        raw=io.encoded(root);dump(stage/'roots'/f'{ds}.json',root)
        target='/kaggle/working/b3_input_'+ds+'.json';definitions[ds]={'path':target,'sha256':sha(raw)}
        bootstrap+=f"Path({target!r}).write_bytes(base64.b64decode({base64.b64encode(raw).decode()!r}))\n"
        data=BASE/'datasets'/ds;data.mkdir(parents=True,exist_ok=True)
        bundle=folder/root['bundle_filename']
        if (data/bundle.name).exists():assert sha((data/bundle.name).read_bytes())==sha(bundle.read_bytes())
        else:shutil.copy2(bundle,data/bundle.name)
        dump(data/'dataset-metadata.json',{'id':OWNER+f'/grace-b3-{ds}-{version}-inputs-20261109',
            'title':f'GRACE B3 {ds} reviewed inputs 20261109','licenses':[{'name':'other'}],'isPrivate':True})
    bootstrap+='''sys.path.insert(0,'/kaggle/working')
from grace_runtime_contract import assert_runtime, digest, load_contract, EXPECTED_CONTRACT_SHA256
from b3_delivery_runtime import load_input_root
RUNTIME_LOCK_PATH=Path('/kaggle/working/inference_runtime_lock.json')
RUNTIME=load_contract()
'''
    bootstrap+=f"Path('/kaggle/working/inference_input_manifest.json').write_bytes(Path({definitions['devign']['path']!r}).read_bytes())\nos.environ['B3_INPUT_ROOT_SHA256']={definitions['devign']['sha256']!r}\n"
    nb=read(oldstage/'kernel/notebook.ipynb')
    nb['cells'][0]['source']=['# B3 Linux member-directory execution revision\n',
        'lznt123; reviewed Devign -> REVEAL validation; no test or threshold fitting.\n']
    nb['cells'][2]['source']=bootstrap.splitlines(keepends=True)
    nb['cells'][3]['source']=(f'DEFINITIONS={definitions!r}\n'+'''
KAGGLE_INPUT_ROOT=Path('/kaggle/input')
OUT_ROOT=Path('/kaggle/working/b3_new_dual_validation_20261109')
MAX_RUNTIME_HOURS=9
if OUT_ROOT.exists():raise ValueError('Existing output requires explicit verified resume')
''').splitlines(keepends=True)
    # Final checkpoint basename also reflects this execution revision.
    nb['cells'][8]['source']=''.join(nb['cells'][8]['source']).replace('b3_new_dual_validation_checkpoint','b3_new_dual_validation_20261109_checkpoint').splitlines(keepends=True)
    meta=read(oldstage/'kernel/kernel-metadata.json')
    meta.update(id=OWNER+'/grace-b3-new-dual-linuxfix-20261109',title='grace-b3-new-dual-linuxfix-20261109',
        dataset_sources=[OWNER+'/grace-b3-devign-v6-inputs-20261109',OWNER+'/grace-b3-reveal-v7-inputs-20261109'],
        kernel_sources=[OWNER+'/qwen3coder30b-prepare-notebook'])
    transport.finalize(stage,nb,meta,{'execution_revision':'b3_linux_member_directory_v1_20261109',
        'datasets':definitions,'fixed_order':['devign','reveal'],'parent_failed_kernel':read(oldstage/'launch.json')['url'],
        'parent_scores':0,'scope':'B3 validation seed42 only; no historical scores/thresholds',
        'code_sha256':{k:sha(v) for k,v in common.items()},'runtime_contract_sha256':sha(common['inference_runtime_lock.json'])})
    details=read(stage/'delivery.json');details['owner']=OWNER;dump(stage/'delivery.json',details)
    print('Prepared Linux-safe execution revision and two private input dataset stages.')


def api_client():
    sys.path.insert(0,str(ROOT/'Runs-management/locked_continuations_20261108/tooling'))
    config=ROOT/'Runs-management/kaggle_lznt123_config';credentials=read(config/'kaggle.json')
    assert credentials['username']==OWNER
    os.environ.update(KAGGLE_USERNAME=OWNER,KAGGLE_KEY=credentials['key'],KAGGLE_CONFIG_DIR=str(config))
    if credentials['key'].startswith('KGAT_'):os.environ['KAGGLE_API_TOKEN']=credentials['key']
    from kaggle.api.kaggle_api_extended import KaggleApi
    api=KaggleApi();api.authenticate();return api


def upload():
    api=api_client()
    for ds in ['devign','reveal']:
        marker=BASE/f'upload_{ds}.json'
        if marker.exists():continue
        folder=BASE/'datasets'/ds;meta=read(folder/'dataset-metadata.json')
        response=api.dataset_create_new(str(folder),public=False,quiet=True,convert_to_csv=False)
        result={'dataset':meta['id'],'private_requested':True,'status':str(getattr(response,'status','')),'error':str(getattr(response,'error',''))}
        dump(marker,result);print(json.dumps(result),flush=True)
        if result['error']:raise ValueError('Dataset creation failed')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['prepare','upload','launch','verify','status','output'])
    args=parser.parse_args()
    if args.action=='prepare':prepare()
    elif args.action=='upload':upload()
    else:
        transport.BASE=BASE;transport.OWNER=OWNER;transport.api_client=api_client
        transport.remote('b3_dual',args.action)
