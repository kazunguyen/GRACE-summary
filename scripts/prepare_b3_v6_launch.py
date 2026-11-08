"""Prepare a concrete Kaggle SDK request; never pushes or consumes GPU quota."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RELEASE=ROOT/'Runs-management/b3_verified_patch_v1/release_20261108_v6'
OUT=ROOT/'Runs-management/b3_verified_patch_v1/v6_acceptance_verified_20261108'


def main():
    acceptance=json.loads((OUT/'acceptance.json').read_text(encoding='utf-8'))
    if acceptance['cpu_verdict']!='PASS':raise ValueError('CPU acceptance required')
    release=json.loads((RELEASE/'release_manifest.json').read_text(encoding='utf-8'))
    for name,h in release['files_sha256'].items():
        if hashlib.sha256((RELEASE/'delivery'/name).read_bytes()).hexdigest()!=h:
            raise ValueError('Delivery changed after seal')
    meta=json.loads((RELEASE/'delivery/kernel-metadata.json').read_text(encoding='utf-8'))
    meta.update(machine_shape='NvidiaTeslaT4',session_timeout_seconds=32400,
        kernel_sources=['huuhieu3333/qwen3coder30b-prepare-notebook'])
    request={'metadata':meta,'notebook_sha256':release['files_sha256']['notebook.ipynb'],
        'input_root_sha256':release['files_sha256']['inference_input_manifest.json'],
        'private_input_dataset_to_publish':'huuhieu3333/grace-b3-v6-devign-inputs',
        'input_dataset_files':['b3_devign_validation_v6.zip'],
        'status':'PREPARED_NOT_SUBMITTED','required_checks':[
            'Verify model kernel source and dataset accessibility as huuhieu3333',
            'Check current account quota before setting session timeout',
            'Official SDK request must retain machine_shape and timeout; old CLI drops shape',
            'Read back all cell sources and machine_shape after push',
            'Native runtime acceptance required; this request is not runtime PASS'],
        'reveal':'BLOCKED_EMPTY_VERIFIED_POOL'}
    check_path=ROOT/'Runs-management/b3_verified_patch_v1/v6_account_check_20261108.json'
    if check_path.is_file():
        account=json.loads(check_path.read_text(encoding='utf-8'))
        request['model_source_accessible']=account.get('model_source_accessible')
        request['model_source_version']=account.get('model_source_version')
        quota=account.get('quota',{}).get('gpuQuota',{})
        if quota:
            seconds=lambda v:float(v.rstrip('s'))
            remaining=seconds(quota['totalTimeAllowed'])-seconds(quota['timeUsed'])-seconds(quota['timeReserved'])
            request['observed_quota_remaining_seconds']=remaining
            request['quota_refresh_time']=account['quota'].get('quotaRefreshTime')
            # Do not submit a 9h notebook into an account with only minutes left.
            if remaining<meta['session_timeout_seconds']+300:
                request['status']='BLOCKED_INSUFFICIENT_CURRENT_QUOTA'
    (OUT/'prepared_launch_request.json').write_text(json.dumps(request,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Prepared request saved. No upload or GPU session started.')


if __name__=='__main__':main()
