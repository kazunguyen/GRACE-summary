"""Reuse the previous auditor against current bytes; preserve previous evidence."""
import contextlib
import hashlib
import json
import runpy
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREVIOUS = HERE.parent / 'independent_v5_readiness_audit_20261108_211003'

def main():
    previous_inventory=json.loads((PREVIOUS/'source_inventory.json').read_text(encoding='utf-8'))
    delta={}
    for name,old in previous_inventory.items():
        p=ROOT/name
        current=hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None
        if current!=old:delta[name]={'previous':old,'current':current}
    (HERE/'changes_since_previous.json').write_text(json.dumps(delta,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    ns=runpy.run_path(str(PREVIOUS/'audit_delivery.py'))
    main_audit=ns['main']
    main_audit.__globals__['OUT']=HERE
    with (HERE/'console.log').open('w',encoding='utf-8',newline='\n') as log:
        with contextlib.redirect_stdout(log):main_audit()
    result=json.loads((HERE/'audit.json').read_text(encoding='utf-8'))
    pool=json.loads((ROOT/'Runs-management/b3_verified_patch_v1/release_20261108_v5/pools/pool_manifest.json').read_text(encoding='utf-8'))
    result['reveal_pool']=pool['pools']['reveal']
    result['changed_inventory_files']=len(delta)
    result['scope_verdicts']={'devign':'BLOCKED_DELIVERY_PREFLIGHT','reveal':'BLOCKED_EMPTY_POOL','both_datasets':'NOT_READY'}
    (HERE/'audit.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'changes':len(delta),'verdicts':result['scope_verdicts'],
        'loader':result['observations']['actual_cell4_original_input'],
        'records':result['observations']['notebook_existing_record_validation']},indent=2))

if __name__=='__main__':main()
