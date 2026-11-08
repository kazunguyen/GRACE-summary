"""Read-only verification of the submitted G1 case and historical preservation."""
from pathlib import Path
import difflib
import hashlib
import json
import re
import sys
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
BASE=ROOT/'Runs-management/b3_verified_patch_v1'
CASE=BASE/'g1_source_investigation_20261108/case_08_ffmpeg_can_safely_read_8614_26054'
sys.path.insert(0,str(ROOT/'01_Author_Baseline_Unified/diagnostic_kit/src'))
from grace_diag.amended_b3 import payload_hash,validate_pair
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def rows(p):return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
paths=[p for name in ('release_20261108','release_20261108_v2','release_20261108_v3','g1_source_investigation_20261108') for p in (BASE/name).rglob('*') if p.is_file()]
paths+=list((ROOT/'scripts').glob('b3_step*.py'))+[ROOT/'scripts/build_g1_dossier.py',ROOT/'tests/test_amended_b3.py',ROOT/'CHANGES_AFTER_PREREG.md']
inventory={p.relative_to(ROOT).as_posix():sha(p) for p in paths}
(OUT/'source_inventory.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2),encoding='utf-8')
prior=read(BASE/'independent_fourth_audit_20261108_153556/source_inventory.json')
preservation={}
for name in ('release_20261108','release_20261108_v2','release_20261108_v3'):
    refs={k:v for k,v in prior.items() if k.startswith('Runs-management/b3_verified_patch_v1/'+name+'/')}
    preservation[name]={'files':len(refs),'mismatches':[k for k,v in refs.items() if sha(ROOT/k)!=v]}
candidate=read(CASE/'candidate_payload.json');packet=read(CASE/'packet.json');sidecar=read(CASE/'evidence_sidecar.json');report=read(CASE/'case_verification_report.json');api=read(CASE/'github_commit_3d7817048c.json')
freeze=ROOT/'01_Author_Baseline_Unified/output/research_freeze_20261101/devign'
meta={r['id']:r for r in rows(freeze/'train_manifest.jsonl')}
bank={r['id']:{**r,'function_uid':r['id']} for r in rows(freeze/'train_raw.jsonl') if meta[r['id']]['keep_in_bank']}
validate_pair(candidate,bank,'devign',require_reviews=False)
source=candidate['source']; before=(CASE/'parent_file_4b529edff8.c').read_text(encoding='utf-8');after=(CASE/'fix_file_3d7817048c.c').read_text(encoding='utf-8')
def extract(s):
    start=s.index('static int can_safely_read(');end=s.index('\n}',start)+2
    return s[start:end],s[:start].count('\n')+1,s[:end].count('\n')+1
comparisons={}
for key,text in [('before',before),('after',after)]:
    fn,start,end=extract(text);donor=source[key]
    comparisons[key]={'upstream_lines':[start,end],'upstream_matches_sidecar_raw':fn==sidecar['upstream_'+key+'_raw'],
        'donor_exact_match':fn==donor,'split_whitespace_equal':fn.split()==donor.split(),
        'remove_only_empty_lines_equal':'\n'.join(x for x in donor.splitlines() if x!='')==fn,
        'actual_upstream_sha256':hashlib.sha256(fn.encode()).hexdigest()}
f=next(f for f in api['files'] if f['filename']==source['path'])
diff='--- a/'+source['path']+'\n+++ b/'+source['path']+'\n'+f['patch']+'\n'
# Apply both real upstream hunks, verifying every old/context line first.
oldlines=before.splitlines(keepends=True);newlines=[];cursor=0;patchlines=f['patch'].splitlines();i=0
while i<len(patchlines):
    m=re.match(r'@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@',patchlines[i]);assert m,patchlines[i]
    start=int(m.group(1))-1;newlines.extend(oldlines[cursor:start]);cursor=start;i+=1
    while i<len(patchlines) and not patchlines[i].startswith('@@'):
        line=patchlines[i];i+=1
        if line.startswith('\\'):continue
        if line[:1] in (' ','-'):
            assert oldlines[cursor].rstrip('\n')==line[1:],(cursor,line)
            if line[0]==' ':newlines.append(oldlines[cursor])
            cursor+=1
        elif line.startswith('+'):newlines.append(line[1:]+'\n')
newlines.extend(oldlines[cursor:])
im=read(BASE/'release_20261108_v3/inputs_manifest.json')
result={'historical_preservation':preservation,'schema_candidate_pass':True,'candidate_has_no_reviews':candidate['reviews']==[],
    'candidate_packet_template_hash_match':payload_hash(candidate)==packet['payload_sha256']==read(CASE/'review_form_template.json')['payload_sha256']==report['evidence_verified']['candidate_payload_sha256'],
    'packet_payload_equal':packet['candidate_payload']==candidate,'actual_fix_identity_match':api['sha']==source['fix_commit'],
    'parent_in_response':source['parent_commit'] in [x['sha'] for x in api['parents']],
    'source_file_hashes_match':all(sha(CASE/n)==report['evidence_verified'][field] for n,field in [('parent_file_4b529edff8.c','parent_file_sha256'),('fix_file_3d7817048c.c','fix_file_sha256'),('actual_fix.diff','actual_fix_diff_sha256')]),
    'fix_blob_sha1_match':hashlib.sha1(b'blob '+str((CASE/'fix_file_3d7817048c.c').stat().st_size).encode()+b'\0'+(CASE/'fix_file_3d7817048c.c').read_bytes()).hexdigest()==f['sha'],
    'actual_diff_matches_api':(CASE/'actual_fix.diff').read_text(encoding='utf-8')==diff==source['fix_diff'],
    'actual_patch_applies_to_full_parent_and_equals_fix':''.join(newlines)==after,'function_comparisons':comparisons,
    'v3_source_hash_mismatches':{section:[k for k,v in im[section].items() if sha(ROOT/k)!=v] for section in ('modules_sha256','execution_scripts_sha256','authority_documents_sha256')},
    'note':'Source mapping has formatting differences; schema validation uses donor-format source fields. No human review or pool admission asserted.'}
(OUT/'dossier_checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
