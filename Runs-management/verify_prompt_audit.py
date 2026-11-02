"""Verify completed prompt-audit artifacts and confirm untouched historical inputs."""
import csv
import hashlib
import json
import math
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
OUT=HERE/'prompt_audit_20261102'


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(4*1024*1024),b''):h.update(block)
    return h.hexdigest()


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))


def main():
    summary=read(OUT/'audit_summary.json');final=read(OUT/'final_status.json')
    checked=0
    for rel,expected in read(OUT/'source_hashes.json').items():
        assert sha(ROOT/rel)==expected,rel
        checked+=1
    for source,expected in summary['historical_protected_hashes'].items():
        rel=source.replace('\\','/').split('/GRACE-summary/',1)[1]
        assert sha(ROOT/rel)==expected,rel
    with (OUT/'audit_rows.csv').open(encoding='utf-8-sig') as f:
        audited=list(csv.DictReader(f))
    assert len(audited)==summary['total_prompt_rows']
    assert len({r['audit_key'] for r in audited})==len(audited)
    assert summary['exact_token_recheck']
    assert all(r['token_check']=='exact_pinned_tokenizer' for r in audited)
    with (OUT/'remediation_final.csv').open(encoding='utf-8-sig') as f:remediation=list(csv.DictReader(f))
    for r in remediation:
        if r['demo_below25']=='True':
            assert r['demo_truncated']=='True'
            assert int(r['tokens_demo'])<.25*int(r['original_demo_tokens'])
    pending={r['audit_key'] for r in remediation}
    assert all(not (r['demo_empty']=='True') or r['audit_key'] in pending for r in audited)
    assert all(s['rate_graph_missing']<=.05 for s in summary['prompt_sets'])
    packet=[json.loads(l) for l in (OUT/'manual_sample.jsonl').read_text(encoding='utf-8').splitlines() if l]
    assert len(packet)==60 and len({r['audit_key'] for r in packet})==60
    assert sum(r['dataset']=='devign' for r in packet)==30
    assert sum(r['dataset']=='reveal' for r in packet)==30
    assert all(not {'label','s','pred_argmax','raw','valid'} & set(r) for r in packet)
    for name in ('reviewer_1.csv','reviewer_2.csv'):
        with (OUT/name).open(encoding='utf-8-sig') as f:sheet=list(csv.DictReader(f))
        assert len(sheet)==60
        assert all(not r['reviewer_name'] and not r['overall_verdict'] for r in sheet)
    inference=read(OUT/'inference_audit.json');identities=[];scores_checked=0
    for s in inference['sets']:
        path=(ROOT/s['source']).with_name('run_manifest.json');m=read(path)
        assert m['model_sha256']=='f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335'
        assert m['tokenizer_revision']=='b2cff646eb4bb1d68355c01b18ae02e7cf42d120'
        assert m['llama_cpp_python']=='0.3.16' and m['context_tokens']==8192
        assert m['quantization']=='Q4_K_M' and m['scoring']=='unconstrained_first_token_logits_v1'
        with (ROOT/s['source']).open(encoding='utf-8') as stream:
            for line in stream:
                if not line.strip():continue
                row=json.loads(line)
                if row['valid']:
                    delta=row['logprob_1']-row['logprob_0']
                    expected=(1/(1+math.exp(-delta))) if delta>=0 else (math.exp(delta)/(1+math.exp(delta)))
                    assert abs(expected-row['s'])<1e-10,row['id']
                    assert row['pred_argmax']==int(row['s']>=.5),row['id']
                    scores_checked+=1
                ids=row.get('token_ids',{})
                if ids and 'greedy_token_id' in row:
                    assert row['response_valid']==(row['greedy_token_id'] in (ids['0'],ids['1'])),row['id']
                else:
                    assert row['response_valid']==(str(row['raw']).strip() in ('0','1')),row['id']
        identities.append({'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'status':'pass'})
    result={'status':'verified','source_files_checked':checked,'prompt_rows':len(audited),
            'manual_packets':60,'scores_recomputed_from_logprobs':scores_checked,'human_ratings_still_blank':True,'historical_hashes_unchanged':True,
            'inference_manifest_checks':identities,'final_status_sha256':sha(OUT/'final_status.json'),
            'audit_summary_sha256':sha(OUT/'audit_summary.json')}
    (OUT/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:v for k,v in result.items() if k!='inference_manifest_checks'}))


if __name__=='__main__':main()
