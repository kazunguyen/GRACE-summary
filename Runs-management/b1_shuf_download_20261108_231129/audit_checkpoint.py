"""Read-only progress/continuation check against the frozen B1-shuf worker."""
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path
from zipfile import ZipFile

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
RUN=HERE/'b1_shuf_locked_20261108'
BASE=ROOT/'Runs-management/locked_continuations_20261108'


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))


def main():
    delivery=read(BASE/'b1_shuf_resume_huuhieu3333_20261108_v2/delivery.json')
    spec=importlib.util.spec_from_file_location('locked_shuf_worker',HERE/'kaggle_inference.py')
    worker=importlib.util.module_from_spec(spec);spec.loader.exec_module(worker)
    assert sha(HERE/'kaggle_inference.py')==delivery['worker_sha256']
    dataset=BASE/'b1_shuf/dataset';bundle=next(dataset.glob('*.zip'))
    manifest,groups,legacy=worker.load_inputs(dataset,bundle.name,delivery['input_manifest_sha256'])
    manifest['_manifest_sha256']=delivery['input_manifest_sha256']
    contract_sha=sha(RUN/'inference_runtime_lock.json')
    assert contract_sha=='85d8770839f80260cdc7c27b27b6cce6bf8815675c8593db68fb102589c5cbd6'
    old_checkpoint=BASE/'b1_shuf/remote_output/b1_shuf_locked_20261108_checkpoint.zip'
    checkpoint=HERE/'b1_shuf_locked_20261108_checkpoint.zip'
    result={'kernel':delivery['ref'],'worker_state':read(RUN/'status.json')['state'],
        'input_manifest_sha256':delivery['input_manifest_sha256'],'checkpoint_sha256':sha(checkpoint),
        'runtime_contract_sha256':contract_sha,'groups':[],'total_done':0,'total_target':0,
        'original_record_bytes_preserved':True,'new_records':0,'raw_invalid_but_score_valid':0}
    provenances=set()
    with ZipFile(old_checkpoint) as old,ZipFile(checkpoint) as latest:
        assert old.testzip() is None and latest.testzip() is None
        assert read(RUN/'run_identity.json')==json.loads(old.read('run_identity.json'))
        for name in latest.namelist():
            if not name.endswith('/'):
                assert (RUN/name).is_file() and latest.read(name)==(RUN/name).read_bytes(),name
        for group,prompts in groups:
            name=f"{group['arm']}/seed_{group['seed']}/{group['dataset']}/{group['split']}"
            record=RUN/name/'records.jsonl'
            rows=worker.jsonl(record.read_bytes()) if record.exists() else []
            lookup={str(r['id']):r for r in prompts};seen=set()
            for row in rows:
                uid=str(row['id']);assert uid in lookup and uid not in seen;seen.add(uid)
                worker.validate_saved(row,lookup[uid],group,manifest,legacy,contract_sha,RUN)
                delta=row['logprob_1']-row['logprob_0']
                expected=1/(1+math.exp(-delta)) if delta>=0 else math.exp(delta)/(1+math.exp(delta))
                assert abs(row['s']-expected)<1e-12
                provenances.add(row['runtime_provenance'])
                result['raw_invalid_but_score_valid']+=int(not row.get('response_valid',True))
            member=name+'/records.jsonl'
            previous=worker.jsonl(old.read(member)) if member in old.namelist() else []
            if previous:assert record.read_bytes().startswith(old.read(member))
            result['new_records']+=len(rows)-len(previous)
            result['groups'].append({'seed':group['seed'],'dataset':group['dataset'],'done':len(rows),
                'target':group['count'],'remaining':group['count']-len(rows),'new':len(rows)-len(previous)})
            result['total_done']+=len(rows);result['total_target']+=group['count']
    sys.path.insert(0,str(ROOT/'scripts'))
    from b3_delivery_runtime import native_log_check
    contract=read(RUN/'inference_runtime_lock.json')
    result['runtime_sessions']=[]
    for ref in sorted(provenances):
        p=RUN/ref;info=read(p)
        assert info['packages']==contract['packages'] and info['constructor']==contract['constructor']
        native_log_check((p.parent/'model_load_offload.log').read_text(encoding='utf-8'),contract)
        result['runtime_sessions'].append({'provenance':ref,'native_contract_checks':'PASS','package_count':len(info['packages'])})
    result['remaining']=result['total_target']-result['total_done']
    result['progress_percent']=100*result['total_done']/result['total_target']
    result['continuation_integrity']='PASS_LAUNCH_CONTRACT'
    result['newer_seven_package_contract_claimed']=False
    (HERE/'checkpoint_audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=True,indent=2))


if __name__=='__main__':main()
