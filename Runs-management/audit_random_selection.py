"""Verify all prepared random-demo selections against the documented seeded selector."""
import json
import sys
from pathlib import Path
from datetime import datetime, timezone
import numpy as np

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'01_Author_Baseline_Unified/diagnostic_kit/src'))
from grace_diag.probes import stable_seed


def rows(path):
    with path.open(encoding='utf-8',buffering=4*1024*1024) as stream:
        for line in stream:
            if line.strip():yield json.loads(line)


def main():
    out=ROOT/'Runs-management/prompt_audit_20261102/random_selection.json'
    if out.exists():raise SystemExit('Random-selection audit already exists')
    results=[]
    for dataset in ('devign','reveal'):
        donors=[r['id'] for r in rows(ROOT/f'Runs-management/donor_reconciliation_20261101/cache/{dataset}_new_bank.jsonl')]
        for split in ('validation','test'):
            old={r['id']:r['demo_ids'][0] for r in rows(ROOT/f'01_Author_Baseline_Unified/output/local_full/bundles_recovered_joern_final_20261031/{dataset}/{split}/prompts.jsonl')}
            for seed in (42,43,44):
                path=ROOT/f'06_Arm_B2_Rand/output/bundles/seed_{seed}/{dataset}/{split}/prompts.jsonl'
                n=0;mismatches=[]
                for row in rows(path):
                    rng=np.random.default_rng(stable_seed(row['id'],seed)); selected=None
                    for _ in range(10):
                        candidate=donors[int(rng.integers(0,len(donors)))]
                        if candidate!=old[row['id']]:selected=candidate;break
                    assert selected is not None
                    if row['demo_ids']!=[selected] or row['seed']!=seed:
                        mismatches.append({'id':row['id'],'expected':selected,'actual':row['demo_ids']})
                    n+=1
                results.append({'dataset':dataset,'split':split,'seed':seed,'count':n,'mismatches':mismatches,
                                'status':'pass' if not mismatches else 'needs_review'})
    data={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'numpy_used_for_recheck':np.__version__,
          'source_policy':'default_rng(stable_seed(id,seed)), reject baseline B2 demo, maximum 10 draws',
          'total':sum(r['count'] for r in results),'sets':results,'all_pass':all(not r['mismatches'] for r in results)}
    out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'count':data['total'],'all_pass':data['all_pass']}))


if __name__=='__main__':main()
