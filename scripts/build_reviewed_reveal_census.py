"""Render/audit full REVEAL validation only after genuine pool admission."""
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path
from zipfile import ZipFile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'01_Author_Baseline_Unified/diagnostic_kit/src'))
from grace_diag.amended_b3 import VerifiedPairSelector, validate_pair, digest
from grace_diag.token_budget import TokenCounter
from grace_diag.probes import split_blocks, ROLE, QUESTION, ANSWER
from b3_delivery_runtime import encoded, seal, sha

BASE=ROOT/'Runs-management/b3_verified_patch_v1'
POOL=BASE/'reveal_reviewed_pool_20261108'
DEST=BASE/'reveal_prompt_release_20261108'


def main():
    if DEST.exists():raise ValueError('Prompt release exists; refusing overwrite')
    frozen=ROOT/'01_Author_Baseline_Unified/output/research_freeze_20261101/reveal'
    keep={r['id'] for l in (frozen/'train_manifest.jsonl').read_text(encoding='utf-8').splitlines() if (r:=json.loads(l))['keep_in_bank']}
    bank={}
    for line in (frozen/'train_raw.jsonl').read_text(encoding='utf-8').splitlines():
        r=json.loads(line)
        if r['id'] in keep:r['function_uid']=r['id'];bank[r['id']]=r
    pairs=[json.loads(l) for l in (POOL/'eligible_pairs.reveal.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()]
    for p in pairs:validate_pair(p,bank,'reveal')
    selector=VerifiedPairSelector(pairs,bank,'reveal')
    counter=TokenCounter(str(ROOT/'11_Arm_B1H2_Evidence/tokenizer_cache_v6/models--Qwen--Qwen3-Coder-30B-A3B-Instruct/snapshots/b2cff646eb4bb1d68355c01b18ae02e7cf42d120'))
    if counter.approx:raise ValueError('Exact tokenizer required')
    archive=ROOT/'Runs-management/grace_15arms_prompts_and_clean_specs.zip'
    with ZipFile(archive) as z:
        names=[n for n in z.namelist() if n.endswith('/reveal_validation_15arms.jsonl') or n=='reveal_validation_15arms.jsonl']
        if len(names)!=1:raise ValueError('Ambiguous/missing REVEAL specs archive member')
        specs=[json.loads(l) for l in z.read(names[0]).decode().splitlines()]
    targets={r['id']:r for l in (frozen/'validation_raw.jsonl').read_text(encoding='utf-8').splitlines() if (r:=json.loads(l))}
    if len(specs)!=2273 or len({r['id'] for r in specs})!=2273 or set(targets)!={r['id'] for r in specs}:raise ValueError('Validation census mismatch')
    pool_sha=sha((POOL/'eligible_pairs.reveal.jsonl').read_bytes())
    with tempfile.TemporaryDirectory(prefix='reveal_prompt_staging_',dir=BASE) as temp:
        stage=Path(temp);folder=stage/'validation/reveal';folder.mkdir(parents=True)
        max_chat=0
        with (folder/'validation_census.jsonl').open('w',encoding='utf-8',newline='\n') as out:
            for i,row in enumerate(specs):
                if digest(row['query_code'].strip())!=digest(targets[row['id']]['func'].strip()):raise ValueError('Target code mismatch')
                target={k:row.get(k,'') for k in ['id','query_code','nodes','edges']}
                rendered=selector.render_family(target,counter)['B3']
                prompt=rendered['prompt'];blocks=split_blocks(prompt)
                ev=rendered['evidence'];tokens=ev['tokens'];chat=counter.count_chat(prompt)
                max_chat=max(max_chat,chat)
                order=ev.get('order')==['role','code','question','graph','demonstration','answer']
                pos=[prompt.find(ROLE),prompt.find(blocks['code']),prompt.find(QUESTION)]
                if blocks['graph']:pos.append(prompt.find(blocks['graph']))
                if blocks['demo']:pos.append(prompt.find(blocks['demo']))
                pos.append(prompt.rfind(ANSWER))
                order=order and all(x>=0 for x in pos) and pos==sorted(pos)
                leakage=bool(re.search(r'The following (?:example|code|target) is (?:Vulnerable|Non-vulnerable)',prompt[:prompt.find(QUESTION)],re.I))
                if not order or leakage or chat+64>8192 or tokens['code']>3000 or tokens['graph']>1500 or tokens['demo']>1500:
                    raise ValueError('Prompt audit failed: '+row['id'])
                record={'method':'b3-verified-patch-v1','dataset':'reveal','split':'validation','seed':42,
                    'target_id':row['id'],'query_code_sha256':digest(row['query_code'].strip()),
                    'pool_sha256':pool_sha,'eligible_pairs_count':len(pairs),'status':'RENDERED',
                    'prompt':prompt,'prompt_sha256':digest(prompt),'selection':rendered['selection'],
                    'token_audit':tokens,'chat_tokens':chat,'target_label_in_prompt':False,
                    'figure6_order_compliant':True,'prompt_evaluation_status':'RENDERED_AUDITED'}
                out.write(json.dumps(record,ensure_ascii=False)+'\n')
                if (i+1)%100==0:print(f'REVEAL {i+1}/2273',flush=True)
        (stage/'pools').mkdir();shutil.copy2(POOL/'eligible_pairs.reveal.jsonl',stage/'pools/eligible_pairs.reveal.jsonl')
        shutil.copy2(POOL/'pool_manifest.json',stage/'pools/pool_manifest.json')
        (stage/'reviews/submitted').mkdir(parents=True)
        for name in ['review_hieu.json','review_dung.json']:shutil.copy2(POOL/'submitted_reviews'/name,stage/'reviews/submitted'/name)
        report={'release_id':DEST.name,'dataset':'reveal','split':'validation','method_id':'b3-verified-patch-v1',
            'count':2273,'pool_sha256':pool_sha,'pairs_count':len(pairs),
            'census_sha256':sha((folder/'validation_census.jsonl').read_bytes()),'max_chat_tokens':max_chat,
            'reserve':64,'verdict':'FULL_PROMPT_CPU_AUDIT_PASS','native_gpu':'NOT_EVALUATED',
            'single_pair_limitation':True}
        report['seal_sha256']=seal(report)
        (stage/'validation/validation_prompt_manifest.json').write_bytes(encoded(report))
        inventory={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in [archive,frozen/'validation_raw.jsonl',frozen/'train_raw.jsonl',frozen/'train_manifest.jsonl',Path(__file__),ROOT/'01_Author_Baseline_Unified/diagnostic_kit/src/grace_diag/amended_b3.py']}
        (stage/'inputs_manifest.json').write_bytes(encoded({'source_files_sha256':inventory,'method_id':'b3-verified-patch-v1'}))
        os.replace(stage,DEST)
    print(json.dumps(report),flush=True)


if __name__=='__main__':main()
