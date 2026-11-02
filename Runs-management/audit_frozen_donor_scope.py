"""Verify frozen donor code/labels and disclose legacy selections outside the new bank."""
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parent.parent
FREEZE=ROOT/'01_Author_Baseline_Unified/output/research_freeze_20261101'
OUT=ROOT/'Runs-management/prompt_audit_20261102/donor_scope.json'
PIN='e1d3c6b17c3a0b5c1e05203794d48a33825e0ea00a55deaaef565af25efe0448'


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(4*1024*1024),b''):h.update(block)
    return h.hexdigest()


def rows(path):
    with path.open(encoding='utf-8',buffering=4*1024*1024) as stream:
        for line in stream:
            if line.strip():yield json.loads(line)


def main():
    if OUT.exists():raise SystemExit('Donor audit exists; do not overwrite it')
    assert sha(FREEZE/'freeze_manifest.json')==PIN
    frozen=json.loads((FREEZE/'freeze_manifest.json').read_text(encoding='utf-8'))
    report={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'snapshot_sha256':PIN,'datasets':{}}
    for dataset in ('devign','reveal'):
        manifest=FREEZE/dataset/'train_manifest.jsonl'
        assert sha(manifest)==frozen['datasets'][dataset]['files_sha256']['train_manifest.jsonl']
        train={r['id']:r for r in rows(manifest)}
        eligible={uid for uid,r in train.items() if r['keep_in_bank']}
        cache=ROOT/f'Runs-management/donor_reconciliation_20261101/cache/{dataset}_new_bank.jsonl'
        proof=json.loads((cache.parent.parent/f'{dataset}_retrieval_provenance.json').read_text(encoding='utf-8'))
        assert sha(cache)==proof['new']['cache_sha256']
        assert proof['new']['input_sha256']==frozen['datasets'][dataset]['files_sha256']['donors.jsonl']
        seen=set()
        for r in rows(cache):
            assert r['id'] in eligible and r['id'] not in seen
            assert r['id'].startswith(dataset+':train:')
            m=train[r['id']]
            assert r['target']==m['label']
            assert hashlib.sha256(r['func'].encode('utf-8')).hexdigest()==m['code_sha256']
            seen.add(r['id'])
        assert seen==eligible and len(seen)==frozen['datasets'][dataset]['donor_count']
        legacy=[]
        for split in ('validation','test'):
            p=ROOT/f'01_Author_Baseline_Unified/output/local_full/bundles_recovered_joern_final_20261031/{dataset}/{split}/prompts.jsonl'
            for row in rows(p):
                for donor in row['demo_ids']:
                    assert donor.startswith(dataset+':train:') and donor in train
                    if donor not in eligible:
                        legacy.append({'id':row['id'],'split':split,'donor_id':donor,
                                       'removal_reason':train[donor]['removal_reason']})
        report['datasets'][dataset]={'frozen_donors_verified':len(seen),'train_manifest_sha256':sha(manifest),
            'cache_sha256':sha(cache),'code_label_id_checks':'pass','legacy_B2_targets_outside_frozen_bank':legacy,
            'note':'Legacy B2/flip/rep remains a separate prompt version; not retroactively treated as using the frozen bank.'}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({d:{'donors_verified':s['frozen_donors_verified'],'legacy_outside':len(s['legacy_B2_targets_outside_frozen_bank'])} for d,s in report['datasets'].items()}))


if __name__=='__main__':main()
