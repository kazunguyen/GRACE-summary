"""Build an UNREVIEWED REVEAL evidence packet from archived upstream sources."""
import csv
import difflib
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'01_Author_Baseline_Unified/diagnostic_kit/src'))
from grace_diag.amended_b3 import make_pair_candidate, validate_pair, payload_hash, digest

RECOVERY=ROOT/'Runs-management/b3_verified_patch_v1/reveal_recovery_20261108'
CASE=RECOVERY/'case_reveal_curl_alloc_addbyter_16061_17887'


def verify_patch(before,after,patch):
    """Apply a single-file unified patch with exact context; no normalization."""
    old=before.splitlines(keepends=True);lines=patch.splitlines(keepends=True)
    result=[];position=0;i=0;hunks=0
    while i<len(lines):
        match=re.match(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@',lines[i])
        if not match:i+=1;continue
        start=int(match[1])-1
        if start<position:raise ValueError('Overlapping patch hunks')
        result.extend(old[position:start]);position=start;i+=1;hunks+=1
        while i<len(lines) and not lines[i].startswith(('@@ ','diff --git')):
            line=lines[i]
            if line.startswith((' ','-')):
                if position>=len(old) or old[position]!=line[1:]:raise ValueError('Actual patch context mismatch')
                if line.startswith(' '):result.append(line[1:])
                position+=1
            elif line.startswith('+'):result.append(line[1:])
            elif line.startswith('\\'):raise ValueError('Unsupported no-newline patch marker')
            else:break
            i+=1
    result.extend(old[position:])
    if not hunks or ''.join(result)!=after:raise ValueError('Full upstream patch does not reproduce after-file')


def main():
    if CASE.exists():raise ValueError('Evidence packet exists; refusing overwrite')
    freeze=ROOT/'01_Author_Baseline_Unified/output/research_freeze_20261101/reveal'
    manifest={r['id']:r for l in (freeze/'train_manifest.jsonl').read_text(encoding='utf-8').splitlines() if (r:=json.loads(l))['keep_in_bank']}
    bank={}
    for line in (freeze/'train_raw.jsonl').read_text(encoding='utf-8').splitlines():
        r=json.loads(line)
        if r['id'] in manifest:r['function_uid']=r['id'];bank[r['id']]=r
    before=(RECOVERY/'curl_before.c').read_text(encoding='utf-8')
    after=(RECOVERY/'curl_after.c').read_text(encoding='utf-8')
    patch=(RECOVERY/'curl_actual_fix.diff').read_text(encoding='utf-8')
    verify_patch(before,after,patch)
    meta=json.loads((RECOVERY/'curl_fix_metadata.json').read_text(encoding='utf-8'))
    if len(meta['parents'])!=1 or meta['sha']!='8732ec40db652c53fa58cd13e2acb8eab6e40874':raise ValueError('Unexpected upstream parentage')
    functions={}
    for name,text in [('before',before),('after',after)]:
        start=text.index('static int alloc_addbyter(')
        functions[name]=text[start:text.index('\n}',start)+2]
    vulnerable=bank['reveal:train:16061'];patched=bank['reveal:train:17887']
    for donor in [vulnerable,patched]:
        if donor['source_id']!='-8228664527580018723':raise ValueError('Distribution source ID mismatch')
    csv.field_size_limit(100000000)
    with (RECOVERY/'debian_data.first_1MiB.partial').open(encoding='utf-8',newline='') as f:
        source_rows=[r for r in csv.DictReader(f) if r.get('hash')=='-8228664527580018723']
    if len(source_rows)!=2 or {r['label'] for r in source_rows}!={'True','False'}:raise ValueError('Missing complete distribution rows')
    source={
        'repository':'curl/curl','path':'lib/mprintf.c','function':'alloc_addbyter',
        'fix_commit':meta['sha'],'parent_commit':meta['parents'][0]['sha'],
        'source_url':'https://github.com/curl/curl/commit/'+meta['sha'],
        'before':vulnerable['func'],'after':patched['func'],'fix_diff':patch,
        'security_rationale':(
            'CVE-2016-8618: on 32-bit size_t, doubling infop->alloc may wrap to zero. '
            'realloc(buffer, 0) may free the allocation and return NULL, leaving error cleanup '
            'able to free the stale pointer again. The actual upstream fix initializes newptr '
            'to NULL, computes newsize, calls realloc only if newsize > the old allocation, '
            'and assigns the checked size. This helper is the changed function in the full fix. '
            'Upstream advisory: https://curl.se/docs/CVE-2016-8618.html. '
            'Donor formatting is tokenized; explicit C lexical mapping is part of this payload '
            'and must be independently reviewed, not treated as a previously ratified mapping.'),
        'mapping':{'type':'c_lexical_tokens_v1',
            'upstream_before':functions['before'],'upstream_after':functions['after'],
            'upstream_before_sha256':digest(functions['before']),'upstream_after_sha256':digest(functions['after']),
            'distribution_source_id':'-8228664527580018723',
            'upstream_full_before_sha256':digest(before),'upstream_full_after_sha256':digest(after),
            'mapping_decision_status':'PENDING_INDEPENDENT_HUMAN_REVIEW'},
    }
    candidate=make_pair_candidate('reveal','case_reveal_curl_alloc_addbyter_16061_17887',vulnerable,patched,source)
    validate_pair(candidate,bank,'reveal',require_reviews=False)
    # Admission must still fail: do not fabricate human approvals.
    try:validate_pair(candidate,bank,'reveal')
    except ValueError as e:
        if 'Two distinct reviewers' not in str(e):raise
    else:raise AssertionError('Unreviewed candidate was admitted')
    CASE.mkdir()
    write=lambda name,obj:(CASE/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    h=payload_hash(candidate)
    write('candidate.json',candidate)
    write('technical_verification.json',{'status':'TECHNICALLY_VERIFIED_UNREVIEWED',
        'payload_sha256':h,'frozen_bank_membership':True,'full_actual_patch_reproduces_after':True,
        'exact_c_lexical_tokens_before_after':True,'human_review_status':'PENDING',
        'pool_admission':'BLOCKED_TWO_INDEPENDENT_REVIEWS_REQUIRED','upstream_commit':meta['sha'],
        'upstream_parent':meta['parents'][0]['sha'],
        'distribution_mapping':'Numeric source_id matches original CSV hash field; not a Git commit',
        'csv_download':'First 1 MiB only, NOT full 1448744816-byte artifact; selected CSV rows complete'})
    for reviewer in ['Hieu','Dung']:
        # Empty fields deliberately rejected by review validator until filled by reviewer.
        write('review_'+reviewer.lower()+'.template.json',{'case_id':candidate['pair_id'],
            'reviewer':reviewer,'payload_sha256':h,'reviewed_at':None,'decision':None,
            'same_function_verified':None,'security_fix_verified':None,
            'source_revisions_verified':None,'explanation_supported':None,'comments':None})
    inventory={str(p.relative_to(RECOVERY)):hashlib.sha256(p.read_bytes()).hexdigest()
        for p in RECOVERY.iterdir() if p.is_file()}
    write('acquisition_inventory.json',inventory)
    (CASE/'REVIEW_PACKET.md').write_text(
        '# REVEAL — review required, not admitted\n\n'
        f'Payload SHA-256: `{h}`\n\n'
        'Candidate: reveal:train:16061 (label1) -> reveal:train:17887 (label0). Both keep_in_bank=true.\n\n'
        'Source: curl/curl, lib/mprintf.c, alloc_addbyter, CVE-2016-8618.\n\n'
        f'Fix: {meta["sha"]}; parent: {meta["parents"][0]["sha"]}.\n\n'
        'Read candidate.json, technical_verification.json, ../curl_before.c, ../curl_after.c, '
        '../curl_actual_fix.diff and https://curl.se/docs/CVE-2016-8618.html. '
        'The original CSV rows are archived as ../source_-8228664527580018723_{True,False}.c; '
        'CSV source_id is a distribution identifier, not commit evidence.\n\n'
        'Check function identity, security mechanism and exact C token mapping independently. '
        'Formatting/comments differ; do not apply the old Devign empty-line exception. '
        'The full patch is applied with exact context and reproduces the upstream after-file.\n\n'
        'Use the two template JSON files independently. Fill real decision, criteria, comments '
        'and UTC timestamp. They contain no prefilled decisions or signature. '
        'Both approvals must bind this exact payload, including mapping. '
        'If either reviewer rejects, retain disagreement and do not admit to pool.\n\n'
        '## Displayed donor diff\n\n```diff\n'+candidate['source']['diff']+'\n```\n',encoding='utf-8')
    print(json.dumps({'packet':str(CASE),'payload_sha256':h,'status':'PENDING_HUMAN_REVIEW'}))


if __name__=='__main__':main()
