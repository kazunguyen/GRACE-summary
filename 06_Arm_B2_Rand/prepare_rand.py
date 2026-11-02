from pathlib import Path
import hashlib, json, zipfile, time, sys
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'tier1_prompt_tools'))
from prepare_cached import cache_paths, rows, render_paired, sha256, BUDGET, PREFIX
from grace_diag.token_budget import TokenCounter
from grace_diag.probes import stable_seed

SEEDS=(42,43,44)
RUNS=(('devign','validation'),('reveal','validation'),('devign','test'),('reveal','test'))
VARIANT='b2_rand_paired_frozen_bank_v1'

def load_donors(dataset, frozen):
    path=frozen/dataset/'donors.jsonl'
    freeze=json.loads((frozen/'freeze_manifest.json').read_text(encoding='utf-8'))
    entry=freeze['datasets'][dataset]
    if sha256(path)!=entry['files_sha256']['donors.jsonl']: raise ValueError('Donor hash mismatch')
    # Keep order exactly as frozen: random_demo indexes this order; omit large unused graphs.
    donors=[{'function_uid':r['function_uid'],'func':r['func'],'target':int(r['target'])} for r in rows(path)]
    if len(donors)!=entry['donor_count'] or len({r['function_uid'] for r in donors})!=len(donors): raise ValueError('Invalid donor bank')
    if any(r['target'] not in (0,1) or not r['function_uid'].startswith(dataset+':train:') for r in donors): raise ValueError('Invalid donor identity/label')
    return donors,entry['files_sha256']['donors.jsonl']

def select(donors,uid,seed,excluded):
    rng=np.random.default_rng(stable_seed(uid,seed))
    for _ in range(10):
        row=donors[int(rng.integers(0,len(donors)))]
        if row['function_uid']!=excluded: return row
    raise ValueError(f'Unable to select donor distinct from retrieved demo: {uid}')

def prepare(reference_root,frozen_root,out_root,tokenizer,runs=RUNS,seeds=SEEDS):
    reference_root=Path(reference_root); frozen_root=Path(frozen_root); out_root=Path(out_root)
    counter=TokenCounter(None); counter.tok=tokenizer; counter.approx=False
    loaded={}; bundles={s:[] for s in seeds}
    for ds,split in runs:
        if ds not in loaded: loaded[ds]=load_donors(ds,frozen_root)
        donors,donor_hash=loaded[ds]
        files,ref=cache_paths(ds,split,reference_root)
        originals={str(r['id']):r for r in rows(files['prompts'])}
        if len(originals)!=ref['count']: raise ValueError('Duplicate or missing reference IDs')
        specs=rows(files['specs']); seen=set(); writers={}; counts={s:0 for s in seeds}; outside=0
        try:
            for seed in seeds:
                folder=out_root/f'seed_{seed}'/ds/split; folder.mkdir(parents=True,exist_ok=True)
                writers[seed]=(folder,(folder/'prompts.jsonl').open('w',encoding='utf-8',newline='\n'),(folder/'pairing_audit.jsonl').open('w',encoding='utf-8',newline='\n'))
            eligible={r['function_uid'] for r in donors}
            for spec in specs:
                uid=str(spec['id']); old=originals.get(uid)
                if uid in seen or old is None or old['label']!=spec['label']: raise ValueError(f'Unmatched target {uid}')
                seen.add(uid)
                if hashlib.sha256(old['prompt'].encode()).hexdigest()!=old['prompt_sha256']: raise ValueError('B2 prompt hash mismatch')
                demos=spec['demonstrations'];
                if len(demos)!=1 or old['demo_ids']!=[demos[0]['function_uid']]: raise ValueError('B2 demo mismatch')
                original=old['prompt']; verified,evidence=render_paired('B2-rep',spec,original,counter,reference=old)
                if verified!=original: raise ValueError('Reference reconstruction mismatch')
                demo=demos[0]; fitted=counter.fit(demo['func'].strip(),1500).text
                marker='The following is an example, and it is '+('Vulnerable' if int(demo['target']) else 'Non-vulnerable')+'.\n'+fitted
                suffix='\n\nAnswer:'
                # Identify the complete B2 demo block at the end, without touching target/graph.
                pos=original.rfind(marker)
                if pos<0: raise ValueError(f'Cannot locate original demo {uid}')
                end=pos+len(marker)
                if 'Answer' not in original[end:]: raise ValueError(f'Unexpected prompt suffix {uid}')
                outside+=demo['function_uid'] not in eligible
                for seed in seeds:
                    d=select(donors,uid,seed,demo['function_uid']); fit=counter.fit(d['func'].strip(),1500)
                    replacement='The following is an example, and it is '+('Vulnerable' if d['target'] else 'Non-vulnerable')+'.\n'+fit.text
                    prompt=original[:pos]+replacement+original[end:]; total=counter.count_chat(prompt)
                    if total+64>8192: raise ValueError(f'Context overflow {uid} seed={seed}')
                    h=hashlib.sha256(prompt.encode()).hexdigest()
                    tokens=dict(evidence['tokens']); tokens.update(demo=fit.tokens,total=total)
                    truncated=dict(evidence['truncated']); truncated['demo']=fit.truncated
                    row={'id':uid,'dataset':ds,'split':split,'arm':'B2-rand','prompt_variant':VARIANT,'seed':seed,'label':spec['label'],'prompt':prompt,'prompt_sha256':h,'reference_b2_prompt_sha256':old['prompt_sha256'],'demo_ids':[d['function_uid']],'graph_missing':not bool(spec.get('nodes')),'tokens':tokens,'truncated':truncated}
                    audit={'id':uid,'reference_b2_prompt_sha256':old['prompt_sha256'],'prompt_sha256':h,'reference_demo_id':demo['function_uid'],'random_demo_id':d['function_uid'],'true_demo_label':d['target'],'displayed_demo_label':d['target'],'reference_demo_outside_new_frozen_bank':demo['function_uid'] not in eligible}
                    _,out,log=writers[seed]; out.write(json.dumps(row,ensure_ascii=False)+'\n'); log.write(json.dumps(audit,ensure_ascii=False)+'\n'); counts[seed]+=1
                if len(seen)%100==0: print(ds,split,len(seen),'/',ref['count'],flush=True)
            if seen!=set(originals): raise ValueError('Reference ID sets differ')
        finally:
            for folder,out,log in writers.values(): out.close(); log.close()
        for seed in seeds:
            folder=writers[seed][0]; pp=folder/'prompts.jsonl'; ap=folder/'pairing_audit.jsonl'
            manifest={'arm':'B2-rand','prompt_variant':VARIANT,'dataset':ds,'split':split,'seed':seed,'count':counts[seed],'prompts_sha256':sha256(pp),'pairing_audit_sha256':sha256(ap),'reference_b2_sha256':{k:sha256(p) for k,p in files.items()},'donor_sha256':donor_hash,'donor_count':len(donors),'donor_sampling':'numpy.default_rng(stable_seed(id,seed)); reject original B2 demo, fail after 10','numpy_version':np.__version__,'reference_demos_outside_new_frozen_bank':outside,'donor_scope':'frozen sanitized train bank; B2 reference retains original retrieved demos','graph_prefix':PREFIX,'token_budget':BUDGET,'tokenizer':ref['tokenizer'],'tokenizer_revision':ref['tokenizer_revision'],'model_repo':ref['model_repo'],'quantization':ref['quantization'],'prompt_budget_tokens':8192,'source_sha256':sha256(Path(__file__))}
            mp=folder/'bundle_manifest.json'; mp.write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
            dest=folder/f'{ds}_{split}_b2_rand_seed_{seed}_kaggle.zip'
            with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
                for p in (pp,ap,mp): z.write(p,p.name)
            bundles[seed].append(dest)
        print(ds,split,'complete',len(seen),'reference demos outside bank',outside,flush=True)
    out_root.mkdir(parents=True,exist_ok=True)
    archive=out_root/'grace_b2_rand_inputs.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_STORED) as z:
        for seed in seeds:
            for p in bundles[seed]: z.write(p,f'seed_{seed}/{p.name}')
    return archive
