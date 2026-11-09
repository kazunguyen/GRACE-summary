"""Private Kaggle deployments authorized by PI on 2026-11-08; no old run edits."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'Runs-management/locked_continuations_20261108'
sys.path.insert(0,str(BASE/'tooling'))

def dump(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main(kind,action):
    stage=BASE/kind
    delivery=json.loads((stage/'delivery.json').read_text(encoding='utf-8'))
    owner=delivery['owner']
    config={'huuhieu3333':'kaggle_huuhieu_config','tomandjerry223':'kaggle_tomandjerry223_config','lznt123':'kaggle_lznt123_config'}[owner]
    credentials=json.loads((ROOT/'Runs-management'/config/'kaggle.json').read_text(encoding='utf-8'))
    assert credentials['username']==owner
    os.environ['KAGGLE_USERNAME']=credentials['username']
    os.environ['KAGGLE_KEY']=credentials['key']
    os.environ['KAGGLE_CONFIG_DIR']=str(ROOT/'Runs-management'/config)
    if credentials['key'].startswith('KGAT_'):
        os.environ['KAGGLE_API_TOKEN']=credentials['key']
    else:
        os.environ.pop('KAGGLE_API_TOKEN',None)
    from kaggle.api.kaggle_api_extended import KaggleApi
    from kagglesdk.kernels.types.kernels_api_service import ApiSaveKernelRequest
    api=KaggleApi();api.authenticate()
    now=datetime.now(timezone.utc).isoformat()
    if action=='dataset':
        marker=stage/'dataset_created.json'
        if marker.exists(): raise ValueError('Dataset creation already recorded; inspect status instead')
        response=api.dataset_create_new(str(stage/'dataset'),public=False,quiet=True,convert_to_csv=False)
        result={'at_utc':now,'dataset':delivery['dataset'],'status':str(getattr(response,'status','')),'url':str(getattr(response,'url','')),'error':str(getattr(response,'error',''))}
        dump(marker,result);print(json.dumps(result),flush=True)
    elif action=='dataset-status':
        response=api.dataset_status(delivery['dataset'])
        result={'at_utc':now,'dataset':delivery['dataset'],'status':str(response)}
        dump(stage/'dataset_status.json',result);print(json.dumps(result),flush=True)
    elif action=='launch':
        marker=stage/'launch.json'
        if marker.exists(): raise ValueError('Launch already recorded; inspect status instead')
        if kind in ('b3_only','b3_only_migrated'):
            from kagglesdk import KaggleClient
            from kagglesdk.kernels.types.kernels_api_service import ApiGetKernelSessionStatusRequest
            prior=json.loads((ROOT/'Runs-management/kaggle_lznt123_config/kaggle.json').read_text(encoding='utf-8'))
            with KaggleClient(username=prior['username'],password=prior['key'],api_token=prior['key']) as client:
                check=ApiGetKernelSessionStatusRequest();check.user_name='lznt123';check.kernel_slug='grace-b3-locked-resume-20261108'
                state=client.kernels.kernels_api_client.get_kernel_session_status(check)
            if state.status.name not in ('COMPLETE','ERROR','CANCEL_ACKNOWLEDGED'):
                raise ValueError('Old combined B3 run is not confirmed stopped; refusing duplicate GPU execution: '+state.status.name)
        meta=json.loads((stage/'kernel/kernel-metadata.json').read_text(encoding='utf-8'))
        payload=(stage/'kernel/notebook.ipynb').read_bytes()
        if hashlib.sha256(payload).hexdigest()!=delivery['notebook_sha256']:raise ValueError('Notebook changed after review')
        notebook=json.loads(payload)
        for cell in notebook['cells']:
            cell['source']=''.join(cell['source'])
        request=ApiSaveKernelRequest()
        request.slug=meta['id'];request.new_title=meta['title'];request.text=json.dumps(notebook,ensure_ascii=False)
        request.language='python';request.kernel_type='notebook';request.is_private=True
        request.enable_gpu=True;request.enable_tpu=False;request.enable_internet=True
        request.machine_shape='NvidiaTeslaT4';request.session_timeout_seconds=meta.get('session_timeout_seconds',32400)
        request.dataset_data_sources=meta['dataset_sources'];request.kernel_data_sources=meta['kernel_sources']
        request.competition_data_sources=[];request.model_data_sources=[];request.category_ids=[]
        # The installed old CLI drops machine_shape; use the official newer SDK request.
        with api.build_kaggle_client() as client:
            response=client.kernels.kernels_api_client.save_kernel(request)
        result={'at_utc':now,'ref':response.ref,'url':response.url,'version':response.version_number,'error':response.error,
            'invalid_dataset_sources':response.invalid_dataset_sources,'invalid_kernel_sources':response.invalid_kernel_sources,
            'requested_machine_shape':request.machine_shape,'notebook_sha256':delivery['notebook_sha256']}
        dump(marker,result);print(json.dumps(result),flush=True)
        if result['error'] or result['invalid_dataset_sources'] or result['invalid_kernel_sources']:raise ValueError('Kaggle rejected launch or sources')
    elif action=='verify-source':
        from kagglesdk.kernels.types.kernels_api_service import ApiGetKernelRequest
        request=ApiGetKernelRequest();request.user_name=owner;request.kernel_slug=delivery['ref'].split('/')[1]
        with api.build_kaggle_client() as client:
            response=client.kernels.kernels_api_client.get_kernel(request)
        local=json.loads((stage/'kernel/notebook.ipynb').read_text(encoding='utf-8'))
        remote=json.loads(response.blob.source)
        source=lambda n:[(c['cell_type'],''.join(c['source'])) for c in n['cells']]
        result={'at_utc':now,'ref':delivery['ref'],'all_cell_sources_match':source(local)==source(remote),
            'machine_shape':response.metadata.machine_shape,'version':response.metadata.current_version_number,
            'is_private':response.metadata.is_private,'enable_gpu':response.metadata.enable_gpu,
            'dataset_sources':response.metadata.dataset_data_sources,'kernel_sources':response.metadata.kernel_data_sources}
        dump(stage/'remote_source_verification.json',result)
        dump(stage/'remote_notebook.json',remote)
        print(json.dumps(result),flush=True)
        if not result['all_cell_sources_match'] or result['machine_shape']!='NvidiaTeslaT4':
            raise ValueError('Remote source or machine shape mismatch')
    elif action=='quota':
        from kagglesdk.kernels.types.kernels_api_service import ApiGetAcceleratorQuotaStatisticsRequest
        result={'at_utc':now,'owner':owner}
        with api.build_kaggle_client() as client:
            client._http_client._response_processor=lambda response:result.update(response.json())
            try:client.kernels.kernels_api_client.get_accelerator_quota_statistics(ApiGetAcceleratorQuotaStatisticsRequest())
            except ValueError:
                if 'gpuQuota' not in result:raise
        dump(stage/'quota.json',result);print(json.dumps(result),flush=True)
    elif action=='inspect-internal':
        result={'at_utc':now,'ref':delivery['ref']}
        with api.build_kaggle_client() as client:
            http=client._http_client;http._init_session()
            for host in ['https://www.kaggle.com','https://api.kaggle.com']:
                response=http._session.post(host+'/api/i/kernels.KernelsService/GetKernel',json={'kernelId':json.loads((stage/'session_inspection.json').read_text(encoding='utf-8'))['responses'][0]['metadata.id']},timeout=30)
                result[host]={'status':response.status_code,'body':response.text[:500] if not response.ok else ''}
                if response.ok:
                    payload=response.json()
                    dump(stage/'internal_kernel_readback.json',payload)
                    result[host]['keys']=list(payload)
        print(json.dumps(result),flush=True)
    elif action=='inspect-page':
        import re
        with api.build_kaggle_client() as client:
            http=client._http_client;http._init_session()
            response=http._session.get('https://www.kaggle.com/code/'+delivery['ref'],timeout=30)
            result={'http_status':response.status_code,'matches':re.findall(r'.{0,60}(?:kernelSessionId|kernelVersionId|kernelId).{0,90}',response.text)[:20]}
            if response.ok:
                body=response.text
                (stage/'session_page.html').write_text(body,encoding='utf-8')
            print(json.dumps(result),flush=True)
    elif action=='inspect-session':
        from kagglesdk.kernels.types.kernels_api_service import ApiGetKernelRequest, ApiGetKernelSessionStatusRequest, ApiListKernelSessionOutputRequest
        result={'at_utc':now,'ref':delivery['ref']}
        def collect(value,path=''):
            found={}
            if isinstance(value,dict):
                for k,v in value.items():
                    if any(s in k.lower() for s in ('session','version','status','id','url','error','fail')) and not isinstance(v,(dict,list)) and len(str(v))<500:
                        found[path+k]=v
                    if isinstance(v,(dict,list)):found.update(collect(v,path+k+'.'))
            elif isinstance(value,list):
                for i,v in enumerate(value[:3]):found.update(collect(v,path+str(i)+'.'))
            return found
        with api.build_kaggle_client() as client:
            def processor(response):
                try: result.setdefault('responses',[]).append(collect(response.json()))
                except ValueError:pass
            client._http_client._response_processor=processor
            request=ApiGetKernelRequest();request.user_name=owner;request.kernel_slug=delivery['ref'].split('/')[1]
            client.kernels.kernels_api_client.get_kernel(request)
            request=ApiGetKernelSessionStatusRequest();request.user_name=owner;request.kernel_slug=delivery['ref'].split('/')[1]
            client.kernels.kernels_api_client.get_kernel_session_status(request)
            request=ApiListKernelSessionOutputRequest();request.user_name=owner;request.kernel_slug=delivery['ref'].split('/')[1]
            client.kernels.kernels_api_client.list_kernel_session_output(request)
        dump(stage/'session_inspection.json',result);print(json.dumps(result),flush=True)
    elif action=='status':
        response=api.kernels_status(delivery['ref'])
        result={'at_utc':now,'ref':delivery['ref'],'status':str(response.status),'failure_message':str(response.failure_message)}
        dump(stage/'remote_status.json',result);print(json.dumps(result),flush=True)
    elif action=='output':
        target=stage/'remote_output';target.mkdir(exist_ok=True)
        api.kernels_output(delivery['ref'],path=str(target),force=True,quiet=True)
        print(json.dumps({'ref':delivery['ref'],'output':str(target.relative_to(ROOT))}),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('kind',choices=['b1_shuf','b3','b1_full','b3_only','b3_only_migrated'])
    parser.add_argument('action',choices=['dataset','dataset-status','launch','verify-source','quota','inspect-internal','inspect-page','inspect-session','status','output'])
    args=parser.parse_args()
    try:main(args.kind,args.action)
    except Exception as exc:
        # Never print credential-bearing request/header objects or entire SDK responses.
        print(f'{type(exc).__name__}: {str(exc)[:600]}',file=sys.stderr)
        sys.exit(1)
