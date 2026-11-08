"""Validate ALL submitted final forms before publishing a new REVEAL pool.

No rendering or GPU inference; templates/absent reviews never count as approvals.
"""
import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
sys.path.insert(0,str(ROOT/'01_Author_Baseline_Unified/diagnostic_kit/src'))
from b3_step6_packet_tool import validate_review_form, resolve_review_consensus
from grace_diag.amended_b3 import validate_pair, payload_hash
from b3_delivery_runtime import encoded, seal, sha
from build_reveal_curl_review_packet import verify_patch
from grace_diag.amended_b3 import digest

CASE=ROOT/'Runs-management/b3_verified_patch_v1/reveal_recovery_20261108/case_reveal_curl_alloc_addbyter_16061_17887'


def admit(reviews_dir,output):
    output=Path(output).resolve()
    base=(ROOT/'Runs-management/b3_verified_patch_v1').resolve()
    if not output.is_relative_to(base) or output.exists():raise ValueError('Use a new B3 output directory')
    candidate=json.loads((CASE/'candidate.json').read_text(encoding='utf-8'))
    h=payload_hash(candidate)
    verified=json.loads((CASE/'technical_verification.json').read_text(encoding='utf-8'))
    if verified['payload_sha256']!=h:raise ValueError('Technical report/payload mismatch')
    packets={candidate['pair_id']:{'payload_sha256':h}}
    triage={candidate['pair_id']:{'status':'AUTOMATED_TRIAGE_PASS'}}
    forms=[];sources={}
    paths=sorted(Path(reviews_dir).glob('*.json'))
    if not paths:raise ValueError('No final human review forms submitted')
    for path in paths:
        form=json.loads(path.read_text(encoding='utf-8'))
        valid,reason=validate_review_form(form,packets,triage)
        if not valid:raise ValueError(path.name+': '+str(reason))
        forms.append(form);sources[path.name]=path.read_bytes()
    verdict,active,reason=resolve_review_consensus(candidate['pair_id'],forms)
    if verdict!='ADMITTED':raise ValueError(reason)
    freeze=ROOT/'01_Author_Baseline_Unified/output/research_freeze_20261101/reveal'
    keep={r['id'] for l in (freeze/'train_manifest.jsonl').read_text(encoding='utf-8').splitlines() if (r:=json.loads(l))['keep_in_bank']}
    bank={}
    for line in (freeze/'train_raw.jsonl').read_text(encoding='utf-8').splitlines():
        r=json.loads(line)
        if r['id'] in keep:r['function_uid']=r['id'];bank[r['id']]=r
    candidate['reviews']=active
    validate_pair(candidate,bank,'reveal')
    before=(CASE.parent/'curl_before.c').read_text(encoding='utf-8')
    after=(CASE.parent/'curl_after.c').read_text(encoding='utf-8')
    mapping=candidate['source']['mapping']
    if (digest(before)!=mapping['upstream_full_before_sha256'] or
            digest(after)!=mapping['upstream_full_after_sha256']):
        raise ValueError('Archived full source changed after review')
    if before.count(mapping['upstream_before'])!=1 or after.count(mapping['upstream_after'])!=1:
        raise ValueError('Mapped function is not unique in archived source')
    verify_patch(before,after,candidate['source']['fix_diff'])
    pool=(json.dumps(candidate,ensure_ascii=False)+'\n').encode('utf-8')
    manifest={'dataset':'reveal','split':'train','method_id':'b3-verified-patch-v1',
        'pool_status':'ACTIVE_VERIFIED_POOL','pairs_count':1,'payload_sha256':h,
        'pool_sha256':sha(pool),'review_forms_sha256':{k:sha(v) for k,v in sources.items()},
        'downstream_state':'FULL_REVEAL_VALIDATION_PROMPT_AUDIT_REQUIRED',
        'scope_limitation':'Single verified pair; no adaptive retrieval claim'}
    manifest['seal_sha256']=seal(manifest)
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='pool_publish_',dir=output.parent) as temp:
        stage=Path(temp)
        (stage/'eligible_pairs.reveal.jsonl').write_bytes(pool)
        (stage/'pool_manifest.json').write_bytes(encoded(manifest))
        (stage/'submitted_reviews').mkdir()
        for name,raw in sources.items():(stage/'submitted_reviews'/name).write_bytes(raw)
        os.replace(stage,output)
    print('Human forms validated. New REVEAL pool published; prompt/runtime gates remain required.')


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--reviews-dir',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();admit(args.reviews_dir,args.output)
