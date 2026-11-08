"""Read-only account status/artifact snapshot for the requested Git handoff."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Runs-management/locked_continuations_20261108/tooling'))
CONFIG={'huuhieu3333':'kaggle_huuhieu_config','tomandjerry223':'kaggle_tomandjerry223_config','lznt123':'kaggle_lznt123_config'}
KNOWN={'huuhieu3333':['grace-b1-full-test','grace-b2-rep-test','grace-b1-full-budgetfix-20261108','grace-b3-only-resume-20261108'],
       'tomandjerry223':['grace-b2-labelonly-test','grace-b2-nolabel-test','grace-b1-shuf-locked-20261108'],
       'lznt123':['grace-b3-validation','grace-b1-shuf-test','grace-b3-locked-resume-20261108']}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def dump(p,value):p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main(owner,out):
    out=(ROOT/out).resolve()
    if not out.is_relative_to(ROOT/'Runs-management'):raise ValueError('Unsafe snapshot path')
    target=out/owner
    if target.exists():raise FileExistsError('Preserve earlier snapshot')
    target.mkdir(parents=True)
    auth=json.loads((ROOT/'Runs-management'/CONFIG[owner]/'kaggle.json').read_text(encoding='utf-8'))
    for name in ('KAGGLE_USERNAME','KAGGLE_KEY','KAGGLE_API_TOKEN'):os.environ.pop(name,None)
    os.environ.update(KAGGLE_CONFIG_DIR=str(ROOT/'Runs-management'/CONFIG[owner]),KAGGLE_USERNAME=owner,KAGGLE_KEY=auth['key'])
    if auth['key'].startswith('KGAT_'):os.environ['KAGGLE_API_TOKEN']=auth['key']
    from kaggle.api.kaggle_api_extended import KaggleApi
    from kagglesdk.kernels.types.kernels_api_service import ApiListKernelsRequest,ApiListKernelSessionOutputRequest
    from kagglesdk.kernels.types.kernels_enums import KernelsListViewType,KernelsListSortType
    import requests
    api=KaggleApi();api.authenticate()
    result=dict(owner=owner,checked_at_utc=datetime.now(timezone.utc).isoformat(),read_only=True,kernels=[])
    slugs=set(KNOWN[owner])
    try:
        with api.build_kaggle_client() as client:
            req=ApiListKernelsRequest();req.user=owner;req.page=1;req.page_size=100
            req.group=KernelsListViewType.PUBLIC_AND_USERS_PRIVATE;req.sort_by=KernelsListSortType.DATE_RUN
            response=client.kernels.kernels_api_client.list_kernels(req)
        found=response.kernels or []
        result['listed_kernel_count']=len(found)
        for item in found:
            slug=item.slug
            if slug.startswith('grace-'):slugs.add(slug)
    except Exception as exc:result['list_error']=str(exc).replace(auth['key'],'[REDACTED]')[:300]
    for slug in sorted(slugs):
        ref=owner+'/'+slug
        entry=dict(ref=ref,checked_at_utc=datetime.now(timezone.utc).isoformat(),artifacts=[])
        try:
            status=api.kernels_status(ref);entry.update(status=status.status.name,failure_message=status.failure_message)
            with api.build_kaggle_client() as client:
                req=ApiListKernelSessionOutputRequest();req.user_name=owner;req.kernel_slug=slug
                response=client.kernels.kernels_api_client.list_kernel_session_output(req)
            entry['remote_file_count']=len(response.files)
            for item in response.files:
                name=item.file_name;p=Path(name)
                if p.is_absolute() or '..' in p.parts:raise ValueError('Unsafe remote path')
                if p.name not in ('records.jsonl','evaluation.json','run_manifest.json','status.json','batch_summary.json',
                    'run_identity.json','group_identity.json','runtime_provenance.json','inference_runtime_lock.json','model_load_offload.log','source_migration_acceptance.json'):
                    continue
                data=requests.get(item.url,timeout=(15,90));data.raise_for_status();raw=data.content
                dest=target/slug/'artifacts'/p;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
                record=dict(path=name,bytes=len(raw),sha256=sha(raw))
                if p.name=='records.jsonl':
                    rows=[json.loads(line) for line in raw.splitlines() if line.strip()]
                    record.update(count=len(rows),unique_ids=len({str(r['id']) for r in rows}))
                prior=ROOT/'Runs-management/kernel_outputs_harvest'/f'{owner}_{slug}'/p
                record.update(prior_harvest_exists=prior.exists(),matches_prior_harvest=prior.exists() and sha(prior.read_bytes())==sha(raw))
                entry['artifacts'].append(record)
        except Exception as exc:entry['error']=str(exc).replace(auth['key'],'[REDACTED]')[:500]
        result['kernels'].append(entry);dump(target/'snapshot.json',result)
        print(ref,entry.get('status'),[(x['path'],x.get('count')) for x in entry['artifacts'] if 'count' in x],entry.get('error',''),flush=True)
    result['finished_at_utc']=datetime.now(timezone.utc).isoformat();dump(target/'snapshot.json',result)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('owner',choices=list(CONFIG));p.add_argument('--out',required=True,type=Path)
    a=p.parse_args();main(a.owner,a.out)
