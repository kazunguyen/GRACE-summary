"""Read-only full-census B3 prompt audit; no builders or inference are run."""
from collections import Counter
from datetime import datetime, timezone
import hashlib,json,sys
from pathlib import Path
from zipfile import ZipFile
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
REL=ROOT/'Runs-management/b3_verified_patch_v1/release_20261108_v4'
FREEZE=ROOT/'01_Author_Baseline_Unified/output/research_freeze_20261101'
sys.path.insert(0,str(ROOT/'01_Author_Baseline_Unified/diagnostic_kit/src'))
from grace_diag.amended_b3 import VerifiedPairSelector,payload_hash
from grace_diag.probes import render_arm,split_blocks
from grace_diag.token_budget import TokenCounter
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def rows(p):return [json.loads(x) for x in p.read_bytes().splitlines() if x.strip()]
inventory={p.relative_to(ROOT).as_posix():sha(p) for p in REL.rglob('*') if p.is_file()}
(OUT/'source_inventory.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2),encoding='utf-8')
im=read(REL/'inputs_manifest.json');pm=read(REL/'pools/pool_manifest.json');vm=read(REL/'validation/validation_prompt_manifest.json')
def seal(obj,field):return obj[field]==hashlib.sha256(json.dumps({k:v for k,v in obj.items() if k!=field},sort_keys=True,ensure_ascii=False,indent=2).encode()).hexdigest()
tokenizer=ROOT/'11_Arm_B1H2_Evidence/tokenizer_cache_v6/models--Qwen--Qwen3-Coder-30B-A3B-Instruct/snapshots/b2cff646eb4bb1d68355c01b18ae02e7cf42d120'
counter=TokenCounter(str(tokenizer));assert not counter.approx
result={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'seals':{'inputs':seal(im,'seal_sha256'),'pool':seal(pm,'manifest_seal_sha256'),'prompts':seal(vm,'prompt_manifest_seal_sha256')},'input_hash_mismatches':{},'datasets':{},'review_authenticity':'PENDING_USER_CONFIRMATION_FINAL_REVIEW_NOT_INFERRED_FROM_JSON'}
for section in ('modules_sha256','execution_scripts_sha256','authority_documents_sha256'):
 result['input_hash_mismatches'][section]=[p for p,h in im[section].items() if sha(ROOT/p)!=h]
result['version_labels']={'inputs':im.get('release_version'),'pool':pm.get('release_version'),'prompt':vm.get('release_version')}
with ZipFile(ROOT/'Runs-management/grace_15arms_prompts_and_clean_specs.zip') as z:
 for ds,n in [('devign',2732),('reveal',2273)]:
  path=REL/'validation'/ds/'validation_census.jsonl';census=rows(path)
  specs={r['id']:r for r in (json.loads(x) for x in z.read(f'specs/{ds}_validation_15arms.jsonl').splitlines() if x.strip())}
  raw={r['id']:r for r in rows(FREEZE/ds/'validation_raw.jsonl')}
  pairs=rows(REL/'pools'/f'eligible_pairs.{ds}.jsonl')
  rr={'count':len(census),'expected':n,'unique_ids':len({r['target_id'] for r in census}),'exact_id_set':{r['target_id'] for r in census}==set(specs)==set(raw),'statuses':dict(Counter(r['status'] for r in census)),'census_hash_matches_manifest':sha(path)==vm['datasets'][ds]['census_sha256'],'pool_hash_matches_manifest':sha(REL/'pools'/f'eligible_pairs.{ds}.jsonl')==pm['pools'][ds]['pool_sha256'],'eligible_pairs':len(pairs),'errors':[]}
  if not pairs:
   rr['all_null_prompts_and_flags']=all(r.get('prompt') is None and r.get('prompt_sha256') is None and r.get('figure6_order_compliant') is None and r.get('target_label_in_prompt') is None for r in census)
  else:
   keep={r['id'] for r in rows(FREEZE/ds/'train_manifest.jsonl') if r['keep_in_bank']}
   bank={r['id']:{**r,'function_uid':r['id']} for r in rows(FREEZE/ds/'train_raw.jsonl') if r['id'] in keep}
   selector=VerifiedPairSelector(pairs,bank,ds);tokens=[];selected=set();payloads=set()
   for i,r in enumerate(census):
    q=specs[r['target_id']];target={k:q[k] for k in ('id','query_code','nodes','edges')}
    pair,demos,selection=selector.select(target['query_code'])
    expected=render_arm({**target,'demonstrations_pair':demos,'security_difference':pair['key_difference']},'B3',counter=counter)
    prompt=r['prompt'];blocks=split_blocks(prompt);total=counter.count_chat(prompt)
    ok=(prompt==expected.prompt and r['prompt_sha256']==hashlib.sha256(prompt.encode()).hexdigest() and r['status']=='RENDERED' and r['prompt_evaluation_status']=='RENDERED_AUDITED' and r['figure6_order_compliant'] is True and r['target_label_in_prompt'] is False and total+64<=8192 and counter.count(blocks['code'])<=3000 and counter.count(blocks['graph'])<=1500 and all(counter.count(d['func'])<=1500 and d['func'].strip() in prompt for d in demos) and ('Key difference: '+pair['key_difference']) in prompt and r['selection']==selection)
    ok &= hashlib.sha256(q['query_code'].strip().encode()).hexdigest()==r['query_code_sha256']==hashlib.sha256(raw[q['id']]['func'].strip().encode()).hexdigest()
    if not ok:rr['errors'].append(q['id'])
    selected.add(pair['pair_id']);payloads.add(payload_hash(pair));tokens.append(total)
    if i%500==0:print(ds,i,'checked',flush=True)
   rr.update(all_canonical_B3_prompts_reproduced=not rr['errors'],max_chat_tokens=max(tokens),selected_pair_ids=sorted(selected),selected_payload_hashes=sorted(payloads))
  result['datasets'][ds]=rr
result['source_files_changed_during_audit']=[p for p,h in inventory.items() if sha(ROOT/p)!=h]
result['prompt_math_scope_pass']=all(result['seals'].values()) and all(d['exact_id_set'] and d['census_hash_matches_manifest'] and d['pool_hash_matches_manifest'] and d['count']==d['expected'] and not d['errors'] for d in result['datasets'].values())
result['full_two_dataset_prompt_release_ready']=False
result['GPU_release_ready']=False
(OUT/'audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
