"""Run required CPU checks once and keep evidence separate from release bytes."""
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DELIVERY=ROOT/'Runs-management/b3_verified_patch_v1/release_20261108_v6/delivery'
OUT=ROOT/'Runs-management/b3_verified_patch_v1/v6_acceptance_20261108'


def main():
    global OUT
    if len(sys.argv)>1:
        OUT=ROOT/sys.argv[1]
        if not OUT.resolve().is_relative_to((ROOT/'Runs-management/b3_verified_patch_v1').resolve()):
            raise ValueError('Acceptance output must stay within B3 workspace')
    OUT.mkdir(exist_ok=False)
    suites=['tests/test_b3_delivery_v6.py','tests/test_b3_reveal_source_mapping.py','tests/test_amended_b3.py',
        'tests/test_preregistration_integrity.py',
        '01_Author_Baseline_Unified/diagnostic_kit/tests/test_probes.py',
        '01_Author_Baseline_Unified/diagnostic_kit/tests/test_stats_and_complementarity.py']
    result={'started_at_utc':datetime.now(timezone.utc).isoformat(),'suites':[],
        'native_gpu_acceptance':'NOT_EVALUATED','reveal':'BLOCKED_EMPTY_VERIFIED_POOL'}
    env=dict(os.environ,PYTHONUTF8='1',PYTHONIOENCODING='utf-8')
    for i,suite in enumerate(suites):
        cmd=[sys.executable,'-m','pytest',suite,'-q','--basetemp='+str(OUT/f'tmp_{i}')]
        p=subprocess.run(cmd,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        text=p.stdout.decode('utf-8',errors='replace')
        (OUT/f'suite_{i}.log').write_text(text,encoding='utf-8')
        result['suites'].append({'command':cmd,'returncode':p.returncode,'stdout_log':f'suite_{i}.log'})
        print(suite,p.returncode,text.splitlines()[-1] if text.splitlines() else '',flush=True)
    result['files_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in DELIVERY.iterdir() if p.is_file()}
    result['cpu_verdict']='PASS' if all(x['returncode']==0 for x in result['suites']) else 'FAIL'
    result['full_validation_gpu_ready']=False
    result['finished_at_utc']=datetime.now(timezone.utc).isoformat()
    (OUT/'acceptance.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return 0 if result['cpu_verdict']=='PASS' else 1


if __name__=='__main__':raise SystemExit(main())
