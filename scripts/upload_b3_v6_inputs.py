"""Publish only the accepted Devign input ZIP as a private HU dataset. No GPU."""
import json
import os
import shutil
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Runs-management/locked_continuations_20261108/tooling'))
OUT=ROOT/'Runs-management/b3_verified_patch_v1/v6_acceptance_verified_20261108'
DELIVERY=ROOT/'Runs-management/b3_verified_patch_v1/release_20261108_v6/delivery'


def main():
    marker=OUT/'private_dataset_upload.json'
    if marker.exists():raise ValueError('Upload already recorded; inspect existing receipt')
    request=json.loads((OUT/'prepared_launch_request.json').read_text(encoding='utf-8'))
    if request['private_input_dataset_to_publish']!='huuhieu3333/grace-b3-v6-devign-inputs':raise ValueError('Wrong destination')
    if json.loads((OUT/'acceptance.json').read_text(encoding='utf-8'))['cpu_verdict']!='PASS':raise ValueError('CPU acceptance missing')
    import hashlib
    root=json.loads((DELIVERY/'inference_input_manifest.json').read_text(encoding='utf-8'))
    bundle=DELIVERY/root['bundle_filename']
    if hashlib.sha256(bundle.read_bytes()).hexdigest()!=root['bundle_sha256']:raise ValueError('Input bytes changed')
    stage=OUT/'private_dataset_upload_staging';stage.mkdir(exist_ok=False)
    shutil.copy2(bundle,stage/bundle.name)
    shutil.copy2(DELIVERY/'dataset-metadata.json',stage/'dataset-metadata.json')
    config=ROOT/'Runs-management/kaggle_huuhieu_config'
    credentials=json.loads((config/'kaggle.json').read_text(encoding='utf-8'))
    if credentials['username']!='huuhieu3333':raise ValueError('Wrong authenticated account')
    os.environ.update(KAGGLE_USERNAME=credentials['username'],KAGGLE_KEY=credentials['key'],KAGGLE_CONFIG_DIR=str(config))
    if credentials['key'].startswith('KGAT_'):os.environ['KAGGLE_API_TOKEN']=credentials['key']
    from kaggle.api.kaggle_api_extended import KaggleApi
    api=KaggleApi();api.authenticate()
    response=api.dataset_create_new(str(stage),public=False,quiet=True,convert_to_csv=False)
    receipt={'dataset':request['private_input_dataset_to_publish'],'requested_private':True,
        'bundle_sha256':root['bundle_sha256'],'status':str(getattr(response,'status','')),
        'error':str(getattr(response,'error','')),'url':str(getattr(response,'url','')),
        'gpu_launched':False}
    marker.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt))
    if receipt['error']:raise ValueError('Dataset creation error; inspect receipt')


if __name__=='__main__':main()
