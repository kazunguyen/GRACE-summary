"""Authorized private B3-swap deployment on a configured account with GPU quota.

Credentials stay in process environment. Scope: B3-swap test only, no cancellation.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys

R = Path(__file__).resolve().parents[1]
STAGE = R / 'Runs-management/b3_swap_launch_20261110'
SOURCE = R / '15_Arm_B3_Swap'
RELEASE = R / 'Runs-management/b3_verified_patch_v1/probe_test_release_20261110_v1/b3_swap'
sys.path.insert(0, str(R / 'Runs-management/locked_continuations_20261108/tooling'))

def stamp():
    return datetime.now(timezone.utc).isoformat()

def save(name, data):
    (STAGE / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def auth(folder):
    config = R / 'Runs-management' / folder
    c = json.loads((config / 'kaggle.json').read_text(encoding='utf-8'))
    for k in ('KAGGLE_API_TOKEN', 'KAGGLE_USERNAME', 'KAGGLE_KEY'):
        os.environ.pop(k, None)
    os.environ.update(KAGGLE_USERNAME=c['username'], KAGGLE_KEY=c['key'], KAGGLE_CONFIG_DIR=str(config))
    if c['key'].startswith('KGAT_'):
        os.environ['KAGGLE_API_TOKEN'] = c['key']
    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    api.authenticate()
    return api, c['username']

def get_quota(api):
    from kagglesdk.kernels.types.kernels_api_service import ApiGetAcceleratorQuotaStatisticsRequest
    result = {}
    with api.build_kaggle_client() as client:
        client._http_client._response_processor = lambda response: result.update(response.json())
        try:
            client.kernels.kernels_api_client.get_accelerator_quota_statistics(ApiGetAcceleratorQuotaStatisticsRequest())
        except ValueError:
            if 'gpuQuota' not in result:
                raise
    return result

def sec(v):
    return float(str(v).rstrip('s'))

def get_model(api, owner):
    from kagglesdk.kernels.types.kernels_api_service import ApiGetKernelRequest
    req = ApiGetKernelRequest(); req.user_name = owner; req.kernel_slug = 'qwen3coder30b-prepare-notebook'
    with api.build_kaggle_client() as client:
        return client.kernels.kernels_api_client.get_kernel(req)

def main(action):
    STAGE.mkdir(parents=True, exist_ok=True)
    if action == 'inspect':
        found = []
        for config in sorted((R / 'Runs-management').glob('kaggle*config/kaggle.json')):
            row = {'config_folder': config.parent.name, 'checked_at_utc': stamp()}
            try:
                api, owner = auth(config.parent.name)
                row['owner'] = owner
                row['quota'] = get_quota(api)
                q = row['quota']['gpuQuota']
                row['remaining_seconds'] = sec(q['totalTimeAllowed']) - sec(q.get('timeUsed', '0s')) - sec(q.get('timeReserved', '0s'))
                for model_owner in dict.fromkeys([owner, 'lznt123', 'huuhieu3333']):
                    try:
                        model = get_model(api, model_owner)
                        row['model_source'] = model_owner + '/qwen3coder30b-prepare-notebook'
                        row['model_source_version'] = model.metadata.current_version_number
                        break
                    except Exception:
                        continue
            except Exception as e:
                row['error_type'] = type(e).__name__
            found.append(row)
        save('account_checks.json', found)
        print(json.dumps(found, ensure_ascii=True, indent=2))
        return
    if action == 'prepare':
        accounts = json.loads((STAGE / 'account_checks.json').read_bytes())
        eligible = [a for a in accounts if a.get('remaining_seconds', 0) > 0 and a.get('model_source')]
        if not eligible:
            raise RuntimeError('No configured account with verified positive available GPU quota and model access')
        choice = max(eligible, key=lambda a: a['remaining_seconds'])
        owner = choice['owner']
        slug = 'grace-b3-swap-test-20261110-v1'
        dataset = owner + '/grace-b3-swap-test-release-20261110-v1'
        original_nb = json.loads((SOURCE / 'kaggle_kernel/notebook.ipynb').read_bytes())
        nb = json.loads(json.dumps(original_nb))
        for c in nb['cells']:
            if c['cell_type'] == 'code':
                s = ''.join(c['source'])
                s = s.replace("DATASETS_ROOT/'lznt123'/", "DATASETS_ROOT/" + repr(owner) + "/")
                s = s.replace('/notebooks/lznt123/qwen3coder30b-prepare-notebook/', '/notebooks/' + choice['model_source'] + '/')
                c['source'] = s.splitlines(keepends=True)
        # Limit setup + inference to verified available account time with 5 minutes
        # account margin. The worker still reserves its own 5 minutes to save results.
        timeout = int(min(32400, choice['remaining_seconds'] - 300))
        if timeout < 1800:
            raise RuntimeError('Positive quota is below 30 minutes; cannot safely build CUDA and save checkpoint')
        nb['cells'][5]['source'] = ''.join(nb['cells'][5]['source']).replace('SESSION_STARTED+9*3600', 'SESSION_STARTED+' + str(timeout)).splitlines(keepends=True)
        for i in (1, 3, 4):
            if nb['cells'][i]['source'] != original_nb['cells'][i]['source']:
                raise ValueError('Shared bootstrap/setup/runtime cells changed')
        (STAGE / 'kernel').mkdir(exist_ok=True)
        (STAGE / 'dataset').mkdir(exist_ok=True)
        (STAGE / 'kernel/notebook.ipynb').write_text(json.dumps(nb, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
        meta = json.loads((SOURCE / 'kaggle_kernel/kernel-metadata.json').read_bytes())
        meta.update(id=owner + '/' + slug, dataset_sources=[dataset], kernel_sources=[choice['model_source']], session_timeout_seconds=timeout)
        save('kernel/kernel-metadata.json', meta)
        for name in ('test_release_manifest.json', 'test_release_manifest.sha256'):
            shutil.copyfile(SOURCE / 'kaggle_dataset' / name, STAGE / 'dataset' / name)
        shutil.copyfile(RELEASE / 'kaggle_dataset/kaggle_input.zip', STAGE / 'dataset/kaggle_input.zip')
        dm = json.loads((SOURCE / 'kaggle_dataset/dataset-metadata.json').read_bytes()); dm['id'] = dataset
        save('dataset/dataset-metadata.json', dm)
        manifest = json.loads((STAGE / 'dataset/test_release_manifest.json').read_bytes())
        if sha(STAGE / 'dataset/kaggle_input.zip') != manifest['kaggle_input_archive_sha256']:
            raise ValueError('Prompt input ZIP hash mismatch')
        save('deployment.json', {'prepared_at_utc': stamp(), 'owner': owner, 'config_folder': choice['config_folder'],
            'ref': meta['id'], 'dataset': dataset, 'model_source': choice['model_source'], 'quota_at_check': choice['remaining_seconds'],
            'session_timeout_seconds': timeout, 'arm': 'B3-swap', 'notebook_sha256': sha(STAGE / 'kernel/notebook.ipynb'),
            'base_notebook_sha256': sha(SOURCE / 'kaggle_kernel/notebook.ipynb'), 'manifest_sha256': sha(STAGE / 'dataset/test_release_manifest.json'),
            'runtime_contract_sha256': manifest['runtime_contract_sha256'], 'status': 'PREPARED_NOT_LAUNCHED'})
        print(json.dumps(json.loads((STAGE / 'deployment.json').read_bytes()), indent=2))
        return
    deploy = json.loads((STAGE / 'deployment.json').read_bytes())
    api, owner = auth(deploy['config_folder'])
    assert owner == deploy['owner']
    if action == 'dataset':
        if (STAGE / 'dataset_created.json').exists():
            raise RuntimeError('Dataset already created; query status')
        r = api.dataset_create_new(str(STAGE / 'dataset'), public=False, quiet=True, convert_to_csv=False)
        result = {'at_utc': stamp(), 'dataset': deploy['dataset'], 'status': str(r.status), 'url': str(r.url), 'error': str(r.error)}
        save('dataset_created.json', result)
    elif action == 'dataset-status':
        result = {'at_utc': stamp(), 'dataset': deploy['dataset'], 'status': str(api.dataset_status(deploy['dataset']))}
        save('dataset_status.json', result)
    elif action in ('launch', 'retry'):
        if action == 'launch' and (STAGE / 'launch.json').exists():
            raise RuntimeError('Launch already recorded; refuse duplicate')
        if action == 'retry':
            status = api.kernels_status(deploy['ref'])
            state = status.status.name
            if state == 'RUNNING':
                print(json.dumps({'ref': deploy['ref'], 'status': state, 'repushed': False}))
                return
            if state != 'QUEUED':
                raise RuntimeError('Retry scope is QUEUED only; observed ' + state)
        from kagglesdk.kernels.types.kernels_api_service import ApiSaveKernelRequest
        nbpath = STAGE / 'kernel/notebook.ipynb'
        assert sha(nbpath) == deploy['notebook_sha256']
        nb = json.loads(nbpath.read_bytes())
        for c in nb['cells']: c['source'] = ''.join(c['source'])
        meta = json.loads((STAGE / 'kernel/kernel-metadata.json').read_bytes())
        req = ApiSaveKernelRequest(); req.slug = deploy['ref']; req.new_title = meta['title']
        req.text = json.dumps(nb, ensure_ascii=False); req.language = 'python'; req.kernel_type = 'notebook'
        req.is_private = True; req.enable_gpu = True; req.enable_tpu = False; req.enable_internet = True
        req.machine_shape = 'NvidiaTeslaT4'; req.session_timeout_seconds = deploy['session_timeout_seconds']
        req.dataset_data_sources = meta['dataset_sources']; req.kernel_data_sources = meta['kernel_sources']
        req.competition_data_sources = []; req.model_data_sources = []; req.category_ids = []
        with api.build_kaggle_client() as client:
            r = client.kernels.kernels_api_client.save_kernel(req)
        result = {'at_utc': stamp(), 'ref': r.ref, 'url': r.url, 'version': r.version_number, 'error': r.error,
                  'invalid_dataset_sources': r.invalid_dataset_sources, 'invalid_kernel_sources': r.invalid_kernel_sources}
        if action == 'launch':
            save('launch.json', result)
        (STAGE / 'attempts').mkdir(exist_ok=True)
        receipt = ('launch_v' + str(r.version_number)) if r.version_number else ('rejected_' + datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S'))
        save('attempts/' + receipt + '.json', result)
        if result['error'] or result['invalid_dataset_sources'] or result['invalid_kernel_sources']:
            print(json.dumps(result, ensure_ascii=True, indent=2))
            raise RuntimeError('Kaggle rejected deployment: ' + str(result['error']))
    elif action == 'verify-source':
        from kagglesdk.kernels.types.kernels_api_service import ApiGetKernelRequest
        req = ApiGetKernelRequest(); req.user_name = owner; req.kernel_slug = deploy['ref'].split('/')[1]
        with api.build_kaggle_client() as client:
            r = client.kernels.kernels_api_client.get_kernel(req)
        remote = json.loads(r.blob.source); local = json.loads((STAGE / 'kernel/notebook.ipynb').read_bytes())
        cells = lambda n: [(c['cell_type'], ''.join(c['source'])) for c in n['cells']]
        result = {'at_utc': stamp(), 'ref': deploy['ref'], 'all_cell_sources_match': cells(local) == cells(remote),
            'machine_shape': r.metadata.machine_shape, 'version': r.metadata.current_version_number,
            'is_private': r.metadata.is_private, 'enable_gpu': r.metadata.enable_gpu,
            'dataset_sources': r.metadata.dataset_data_sources, 'kernel_sources': r.metadata.kernel_data_sources}
        save('remote_source_verification.json', result)
        if not result['all_cell_sources_match'] or result['machine_shape'] != 'NvidiaTeslaT4':
            raise RuntimeError('Remote notebook/source mismatch')
    elif action == 'status':
        r = api.kernels_status(deploy['ref'])
        result = {'at_utc': stamp(), 'ref': deploy['ref'], 'status': str(r.status), 'failure_message': str(r.failure_message)}
        save('status.json', result)
    else:
        raise ValueError(action)
    print(json.dumps(result, ensure_ascii=True, indent=2))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('action', choices=['inspect', 'prepare', 'dataset', 'dataset-status', 'launch', 'retry', 'verify-source', 'status'])
    args = parser.parse_args()
    main(args.action)
