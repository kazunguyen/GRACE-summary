"""Read-only account/model-source checks. Never logs credentials or launches."""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Runs-management/locked_continuations_20261108/tooling'))
OUT=ROOT/'Runs-management/b3_verified_patch_v1/v6_account_check_20261108.json'


def main():
    config=ROOT/'Runs-management/kaggle_huuhieu_config'
    credentials=json.loads((config/'kaggle.json').read_text(encoding='utf-8'))
    if credentials['username']!='huuhieu3333':raise ValueError('Wrong account configuration')
    os.environ.update(KAGGLE_USERNAME=credentials['username'],KAGGLE_KEY=credentials['key'],KAGGLE_CONFIG_DIR=str(config))
    if credentials['key'].startswith('KGAT_'):os.environ['KAGGLE_API_TOKEN']=credentials['key']
    from kaggle.api.kaggle_api_extended import KaggleApi
    from kagglesdk.kernels.types.kernels_api_service import ApiGetKernelRequest,ApiGetAcceleratorQuotaStatisticsRequest
    result={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'owner':'huuhieu3333',
        'read_only':True,'model_source':'huuhieu3333/qwen3coder30b-prepare-notebook'}
    api=KaggleApi();api.authenticate()
    request=ApiGetKernelRequest();request.user_name='huuhieu3333';request.kernel_slug='qwen3coder30b-prepare-notebook'
    try:
        with api.build_kaggle_client() as client:
            response=client.kernels.kernels_api_client.get_kernel(request)
        result['model_source_accessible']=True
        result['model_source_version']=response.metadata.current_version_number
    except Exception as e:
        result['model_source_accessible']=False;result['model_check_error_type']=type(e).__name__
    quota={}
    try:
        with api.build_kaggle_client() as client:
            client._http_client._response_processor=lambda response:quota.update(response.json())
            try:client.kernels.kernels_api_client.get_accelerator_quota_statistics(ApiGetAcceleratorQuotaStatisticsRequest())
            except ValueError:
                if 'gpuQuota' not in quota:raise
        result['quota']=quota
    except Exception as e:result['quota_check_error_type']=type(e).__name__
    OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=True))


if __name__=='__main__':main()
