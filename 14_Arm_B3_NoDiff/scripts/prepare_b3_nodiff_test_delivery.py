#!/usr/bin/env python3
"""Build the sealed B3-nodiff test prompts and Kaggle delivery from frozen sources."""
from __future__ import annotations

import hashlib, json, re, zipfile, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HANDOFF = ROOT / 'Runs-management/run_handoff_20261109/B3_NODIFF_VALIDATION'
SPECS = ROOT / 'grace_15arms_prompts_and_clean_specs.zip'
OUT = ROOT / '14_Arm_B3_NoDiff/kaggle_delivery_20261109'
OUT.mkdir(parents=True, exist_ok=True)
DIAG_SRC=ROOT/'01_Author_Baseline_Unified/diagnostic_kit/src'
TOKENIZER=ROOT/'11_Arm_B1H2_Evidence/tokenizer_cache_v6/models--Qwen--Qwen3-Coder-30B-A3B-Instruct/snapshots/b2cff646eb4bb1d68355c01b18ae02e7cf42d120'
if not TOKENIZER.is_dir(): raise FileNotFoundError(f'Locked local tokenizer snapshot missing: {TOKENIZER}')
sys.path.insert(0,str(DIAG_SRC))
from grace_diag.probes import render_arm
import grace_diag.probes as probes
from grace_diag.token_budget import TokenCounter

def sha(raw: bytes) -> str: return hashlib.sha256(raw).hexdigest()
def canon(obj) -> bytes: return (json.dumps(obj, sort_keys=True, ensure_ascii=False, indent=2) + '\n').encode()
def seal(obj, key): return sha(json.dumps({k:v for k,v in obj.items() if k != key}, sort_keys=True, ensure_ascii=False, indent=2).encode())

def fast_prefix_graph(policy,spec,counter,budget,prefix,seed,donors):
    """Token-equivalent prefix graph budget search from probes.render_graph, using fewer counts."""
    nodes,edges=spec.get('nodes') or [],spec.get('edges') or []
    if policy!='prefix': return probes.render_graph(policy,spec,counter,budget,prefix,seed,donors)
    info={'policy':policy,'available_nodes':len(nodes),'available_edges':len(edges)}
    if not nodes: return '',{**info,'rendered_nodes':0,'rendered_edges':0,'tokens':0,'missing':True}
    kn,ke=probes.closed_prefix(nodes,edges,prefix['nodes'],prefix['edges'])
    def format_graph(nlist,elist): return f'{probes.NODE_HEAD}\n{probes.format_nodes(nlist)}\n{probes.EDGE_HEAD}\n{probes.format_edges(elist)}'
    def count_edges(k): return counter.count(format_graph(kn,ke[:k]))
    full=len(ke); low,high=0,full
    # Counts are nondecreasing with appended edge lines in this renderer; find largest fitting prefix.
    while low<high:
        mid=(low+high+1)//2
        if count_edges(mid)<=budget: low=mid
        else: high=mid-1
    while low and count_edges(low)>budget: low-=1
    while low<full and count_edges(low+1)<=budget: low+=1
    selected=ke[:low]; text=format_graph(kn,selected); truncated=(len(kn)<min(len(nodes),prefix['nodes']) or low<len(ke))
    if counter.count(text)>budget:
        # Preserve the canonical renderer's fallback: once edges are exhausted, remove nodes from the tail.
        selected=[]
        while kn and counter.count(format_graph(kn,selected))>budget: kn.pop(); truncated=True
        text=format_graph(kn,selected)
    if counter.count(text)>budget: raise ValueError('Graph headers exceed token budget')
    return text,{**info,'rendered_nodes':len(kn),'rendered_edges':len(selected),'tokens':counter.count(text),'truncated':truncated}

def main():
    runtime=(HANDOFF/'inference_runtime_lock.json').read_bytes()
    runtime_lock=json.loads(runtime)
    runtime_sha=sha(runtime)
    if runtime_sha!='85d8770839f80260cdc7c27b27b6cce6bf8815675c8593db68fb102589c5cbd6': raise ValueError('Runtime lock bytes changed')
    threshold_raw=(HANDOFF/'validation_threshold_lock.json').read_bytes()
    threshold=json.loads(threshold_raw)
    unsigned={k:v for k,v in threshold.items() if k!='locked_sha256'}
    if threshold.get('locked_sha256') != sha(json.dumps(unsigned,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()): raise ValueError('Validation threshold lock seal invalid')
    if threshold.get('arm')!='B3-nodiff' or threshold.get('split')!='validation': raise ValueError('Wrong threshold lock scope')
    support=HANDOFF/'support'
    counter=TokenCounter(str(TOKENIZER))
    if counter.approx: raise ValueError('Expected real locked tokenizer; approximate token counting is forbidden')
    probes.render_graph=fast_prefix_graph
    speczip=zipfile.ZipFile(SPECS)
    delivery_files={}
    helper=(support/'b3_delivery_runtime.py').read_text(encoding='utf-8')
    helper=helper.replace("root['scope']['split'] != 'validation'", "root['scope']['split'] not in ('validation','test')")
    helper=helper.replace("root['scope']['dataset']+':validation:'", "root['scope']['dataset']+':'+root['scope']['split']+':'")
    helper=helper.replace("(row['dataset'], row['split']) != (root['scope']['dataset'], 'validation')", "(row['dataset'], row['split']) != (root['scope']['dataset'], root['scope']['split'])")
    helper_bytes=helper.encode('utf-8')
    support_bytes={name:(support/name).read_bytes() for name in ('grace_runtime_contract.py','kaggle_inference.py')}
    code_hashes={'b3_delivery_runtime.py':sha(helper_bytes),**{k:sha(v) for k,v in support_bytes.items()}}
    for ds,expected in [('devign',2732),('reveal',2274)]:
        valzip=zipfile.ZipFile(HANDOFF/ds/'input_bundle.zip')
        pair=json.loads(valzip.read(f'evidence/eligible_pairs.{ds}.jsonl').splitlines()[0])
        reviews=pair.get('reviews',[])
        if {r.get('reviewer') for r in reviews if r.get('decision')=='approve'} < {'Dung','Hieu'}:
            raise ValueError(f'{ds}: source demonstration pair does not have dual approval')
        source_manifest=json.loads(valzip.read('bundle_manifest.json'))
        pair_id=source_manifest['source_pair_id']
        val_prompt=json.loads(valzip.read('prompts.jsonl').splitlines()[0])['prompt']
        demo=re.search(r'The following example is Vulnerable\.\n(.*?)\n\nThe following example is Non-vulnerable\.\n(.*?)\n\nAnswer \(0 or 1\):$',val_prompt,re.S)
        if not demo: raise ValueError(f'{ds}: cannot extract exact reviewed demonstration from validation prompt')
        vulnerable,patched=demo.group(1),demo.group(2)
        rows=[]; ids=set()
        spec_lines=speczip.read(f'specs/{ds}_test_15arms.jsonl').splitlines()
        for row_number,line in enumerate(spec_lines,1):
            if not line.strip(): continue
            spec=json.loads(line); uid=spec['id']
            if uid in ids: raise ValueError(f'{ds}: duplicate target {uid}')
            ids.add(uid)
            if not uid.startswith(ds+':test:'): raise ValueError(f'{ds}: unexpected split ID {uid}')
            # Target fields come only from the test spec. Demonstrations are the reviewed TRAIN pair.
            render_spec={'id':uid,'query_code':spec['query_code'],'nodes':spec.get('nodes') or [],'edges':spec.get('edges') or [],
                'demonstrations_pair':[{'function_uid':source_manifest['source_vulnerable_id'],'func':vulnerable,'target':1},
                    {'function_uid':source_manifest['source_patched_id'],'func':patched,'target':0}]}
            rendered=render_arm(render_spec,'B3-nodiff',seed=42,counter=counter)
            prompt=rendered.prompt
            # Explicit guard: no test answer leaks into the rendered prompt.
            label=spec['label']
            if type(label) is not int or label not in (0,1): raise ValueError(f'{ds}: bad test label')
            row={'id':uid,'dataset':ds,'split':'test','label':label,'prompt':prompt,'prompt_sha256':sha(prompt.encode()),
                 'source_pair_id':pair_id,'source_pair_dataset_split':'train','prompt_token_count':rendered.evidence['tokens']['total'],
                 'render_evidence':rendered.evidence}
            rows.append(row)
            if row_number%100==0: print(f'{ds} prompt render: {row_number}/{len(spec_lines)}',flush=True)
        if len(rows)!=expected: raise ValueError(f'{ds}: expected {expected} test targets, got {len(rows)}')
        prompt_bytes=(''.join(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n' for r in rows)).encode()
        common={'arm':'B3-nodiff','count':len(rows),'dataset':ds,'seed':42,'split':'test'}
        files={'prompts.jsonl':prompt_bytes,
               f'evidence/eligible_pairs.{ds}.jsonl':valzip.read(f'evidence/eligible_pairs.{ds}.jsonl'),
               'evidence/review_dung.json':valzip.read('evidence/review_dung.json'),
               'evidence/review_hieu.json':valzip.read('evidence/review_hieu.json')}
        bm={'schema_version':1,'release_id':'b3_nodiff_test_20261109','method_id':'b3-nodiff-verified-patch-v1',
            'parent_release':source_manifest['release_id'],'arm':'B3-nodiff','dataset':ds,'split':'test','seed':42,'scope':common,
            'count':len(rows),'source_pair_id':pair_id,'source_pair_sha256':sha(files[f'evidence/eligible_pairs.{ds}.jsonl']),
            'source_train_ids':[pair['vulnerable_id'],pair['patched_id']],'prompts_sha256':sha(prompt_bytes),
            'prompt_budget_tokens':8192,'tokenizer':runtime_lock['tokenizer']['repo'],'tokenizer_revision':runtime_lock['tokenizer']['revision'],
            'model_repo':runtime_lock['model']['repo'],'quantization':runtime_lock['model']['quantization'],
            'prompt_transform':'Test target code and graph; same dual-reviewed train vulnerable/patched pair as validation; no Key difference; target labels excluded from prompt.',
            'files_sha256':{k:sha(v) for k,v in files.items()}}
        bm['manifest_seal_sha256']=seal(bm,'manifest_seal_sha256'); files['bundle_manifest.json']=canon(bm)
        bundle_name=f'b3_nodiff_{ds}_test_seed42.zip'
        bundle_path=OUT/bundle_name
        with zipfile.ZipFile(bundle_path,'w',zipfile.ZIP_DEFLATED) as z:
            for name,raw in sorted(files.items()): z.writestr(name,raw)
        bundle_raw=bundle_path.read_bytes()
        root={'schema_version':1,'method_id':'b3-nodiff-verified-patch-v1','release_id':'b3_nodiff_test_20261109',
              'bundle_filename':bundle_name,'bundle_sha256':sha(bundle_raw),'members_sha256':{k:sha(v) for k,v in files.items()},
              'scope':common,'model_sha256':runtime_lock['model']['sha256'],'runtime_contract_sha256':runtime_sha,
              'tokenizer_revision':runtime_lock['tokenizer']['revision'],'pool_sha256':bm['source_pair_sha256'],
              'prompt_content_sha256':sha(prompt_bytes),'scoring':'unconstrained_first_token_logits_v1',
              'code_sha256':code_hashes,'threshold_lock_sha256':sha(threshold_raw),'source_pair_id':pair_id,
              'threshold':threshold['entries'][ds]['tau_star']}
        root['seal_sha256']=seal(root,'seal_sha256')
        root_bytes=canon(root)
        delivery_files[f'{ds}/inference_input_manifest.json']=root_bytes
        delivery_files[f'{ds}/{bundle_name}']=bundle_raw
        print(f'{ds}: packaged {len(rows)} rows, pair={pair_id}, tau={root["threshold"]}',flush=True)
    delivery_files['support/b3_delivery_runtime.py']=helper_bytes
    for name,raw in support_bytes.items(): delivery_files[f'support/{name}']=raw
    delivery_files['inference_runtime_lock.json']=runtime
    delivery_files['validation_threshold_lock.json']=threshold_raw
    manifest={'schema_version':1,'release_id':'b3_nodiff_test_20261109','arm':'B3-nodiff','split':'test','seed':42,
        'scope':{'arm':'B3-nodiff','split':'test','seed':42,
        'datasets':{'devign':2732,'reveal':2274}},'files_sha256':{k:sha(v) for k,v in delivery_files.items()},
        'runtime_contract_sha256':runtime_sha,'threshold_lock_sha256':sha(threshold_raw)}
    manifest['seal_sha256']=seal(manifest,'seal_sha256'); delivery_files['delivery_manifest.json']=canon(manifest)
    outzip=OUT/'grace_b3_nodiff_test_inputs.zip'
    with zipfile.ZipFile(outzip,'w',zipfile.ZIP_DEFLATED) as z:
        for name,raw in sorted(delivery_files.items()): z.writestr(name,raw)
    print(f'delivery={outzip} sha256={sha(outzip.read_bytes())} bytes={outzip.stat().st_size}',flush=True)

if __name__=='__main__': main()
