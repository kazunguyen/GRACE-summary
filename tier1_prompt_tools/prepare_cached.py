"""Prepare paired tier-1 arms from completed B2 prompt/spec caches; no encoder/Joern."""
import hashlib
import json
import sys
import zipfile
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASELINE=ROOT/'01_Author_Baseline_Unified'
sys.path.insert(0,str(BASELINE/'diagnostic_kit/src'))
from grace_diag.probes import render_arm,render_graph,ROLE,QUESTION,NODE_HEAD,EDGE_HEAD,ANSWER,closed_prefix,format_nodes,format_edges
from grace_diag.token_budget import TokenCounter

BUDGET={'total':8192,'target_code':3000,'demo':1500,'graph':1500,'reserve':64}
PREFIX={'nodes':40,'edges':80}
VARIANTS={'B1':'b1_b2_empty_demo_v1','B2-flip':'b2_flip_paired_baseline_v1','B2-rep':'b2_repeat_paired_baseline_v1'}
DEMO_EMPTY='The following is an example, and it is .\n'
_HASH_CACHE={}

def sha256(path):
    path=Path(path)
    st=path.stat(); identity=(str(path.resolve()),st.st_size,st.st_mtime_ns,st.st_ctime_ns)
    if identity in _HASH_CACHE: return _HASH_CACHE[identity]
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    after=path.stat()
    if (after.st_size,after.st_mtime_ns,after.st_ctime_ns)!=(st.st_size,st.st_mtime_ns,st.st_ctime_ns):
        raise ValueError(f'File changed while hashing: {path}')
    _HASH_CACHE[identity]=h.hexdigest()
    return h.hexdigest()

def rows(path):
    with Path(path).open(encoding='utf-8') as f:
        for line in f:
            if line.strip(): yield json.loads(line)

def convert_graph(spec):
    clean={k:v for k,v in spec.items() if k not in ('label','target','target_label','ground_truth','group','graph_missing','graph_error','retrieval_metadata')}
    clean['edges']=[]
    for e in spec.get('edges') or []:
        a=e.get('start',e.get('source',e.get('src'))); b=e.get('end',e.get('target',e.get('dst')))
        if a is None or b is None: raise ValueError('CPG edge missing endpoint')
        clean['edges'].append(dict(e,start=a,end=b,type=e.get('type',e.get('label','CONNECTED_TO'))))
    return clean

def render_paired_slow(arm,spec,b2_prompt,counter):
    clean=convert_graph(spec)
    b2=render_arm(clean,'B2',counter=counter,budget=BUDGET,graph_prefix=PREFIX)
    if b2.prompt!=b2_prompt:
        raise ValueError(f"B2 renderer/cache mismatch at {spec['id']}; use matching B2 specs/prompts/tokenizer, do not silently regenerate")
    if arm=='B2-rep':
        return b2_prompt,b2.evidence
    if arm=='B2-flip':
        flipped=render_arm(clean,'B2-flip',counter=counter,budget=BUDGET,graph_prefix=PREFIX)
        return flipped.prompt,flipped.evidence
    if arm!='B1': raise ValueError('Unknown tier-1 arm')
    fitted=counter.fit(clean['query_code'].strip(),3000,marker='\n/* [TRUNCATED TARGET] */')
    graph,info=render_graph('prefix',clean,counter,1500,PREFIX,42,None)
    # Same scaffold as the requested B0; retain headings even for absent CPG.
    if not graph: graph=f'{NODE_HEAD}\n\n{EDGE_HEAD}\n'
    prompt='\n\n'.join([ROLE,fitted.text,QUESTION,graph,DEMO_EMPTY,ANSWER])
    evidence={'tokens':{'total':counter.count_chat(prompt),'code':fitted.tokens,'graph':info.get('tokens',0),'demo':0},
              'truncated':{'code':fitted.truncated,'graph':info.get('truncated',False),'demo':False},
              'graph':info,'demo':{'demos':[]}}
    if evidence['tokens']['total']+64>8192: raise ValueError('Context overflow')
    return prompt,evidence

def render_paired(arm,spec,b2_prompt,counter,reference=None):
    """Reuse the already fitted B2 graph; never repeat its per-edge token trimming.

    Validate exact target/demo strings and reconstruct the cached graph from its
    recorded node/edge counts. Fall back only for old caches without these counts.
    """
    meta=(reference or {}).get('tokens',{})
    required=('graph_nodes_used','graph_edges_used','target_tokens_used','graph_tokens_used','demo_tokens_used')
    if not all(k in meta for k in required):
        return render_paired_slow(arm,spec,b2_prompt,counter)
    code=spec['query_code'].strip()
    if meta.get('target_truncated'):
        code=counter.fit(code,3000,marker='\n/* [TRUNCATED TARGET] */').text
    demo=spec['demonstrations'][0]; demo_code=demo['func'].strip()
    if meta.get('demo_truncated'):
        demo_code=counter.fit(demo_code,1500).text
    label=int(demo['target'])
    if label not in (0,1): raise ValueError('Invalid demo label')
    word='Vulnerable' if label else 'Non-vulnerable'
    demo_text=f'The following is an example, and it is {word}.\n{demo_code}'
    nodes=spec.get('nodes') or []
    n=int(meta['graph_nodes_used']); k=int(meta['graph_edges_used'])
    if not (0<=n<=40 and 0<=k<=80 and 0<=meta['graph_tokens_used']<=1500):
        raise ValueError('Cached B2 graph exceeds contract')
    # Edge conversion is limited to the first 80 eligible edges, rather than copying the entire CPG.
    selected=nodes[:n]; ids={str(v.get('id',i)) for i,v in enumerate(selected)}; edges=[]
    if k:
        for e in spec.get('edges') or []:
            a=e.get('start',e.get('source',e.get('src'))); b=e.get('end',e.get('target',e.get('dst')))
            if str(a) in ids and str(b) in ids:
                edges.append(dict(e,start=a,end=b,type=e.get('type',e.get('label','CONNECTED_TO'))))
                if len(edges)==k: break
    if n>len(nodes) or len(edges)!=k: raise ValueError('Cached B2 graph counts differ from specs')
    graph=f'{NODE_HEAD}\n{format_nodes(selected)}\n{EDGE_HEAD}\n{format_edges(edges)}' if nodes else ''
    parts=[ROLE,code,QUESTION]+([graph] if graph else [])+[demo_text,ANSWER]
    if '\n\n'.join(parts)!=b2_prompt:
        raise ValueError(f"B2 renderer/cache mismatch at {spec['id']}; cached graph/code/demo no longer agree")
    missing=not bool(nodes)
    initial_ids={str(v.get('id',i)) for i,v in enumerate(nodes[:40])}
    initial_edges=0
    for edge in spec.get('edges') or []:
        a=edge.get('start',edge.get('source',edge.get('src'))); b=edge.get('end',edge.get('target',edge.get('dst')))
        if str(a) in initial_ids and str(b) in initial_ids:
            initial_edges+=1
            if initial_edges==80: break
    info={'policy':'prefix','available_nodes':len(nodes),'available_edges':len(spec.get('edges') or []),
          'rendered_nodes':n,'rendered_edges':k,'tokens':meta['graph_tokens_used'],
          'truncated':n<min(len(nodes),40) or k<initial_edges,
          'missing':missing,'reused_b2_fitted_graph':True}
    evidence={'tokens':{'code':meta['target_tokens_used'],'graph':meta['graph_tokens_used'],'demo':meta['demo_tokens_used'],
                        'total':meta['prompt_tokens']},
              'truncated':{'code':meta.get('target_truncated',False),'graph':info['truncated'],'demo':meta.get('demo_truncated',False)},
              'graph':info,'demo':{'demos':[{'function_uid':demo['function_uid']}]}}
    if arm=='B2-rep': return b2_prompt,evidence
    if arm=='B2-flip':
        flipped='Non-vulnerable' if label else 'Vulnerable'
        parts[-2]=f'The following is an example, and it is {flipped}.\n{demo_code}'
    elif arm=='B1':
        parts=[ROLE,code,QUESTION,graph or f'{NODE_HEAD}\n\n{EDGE_HEAD}\n',DEMO_EMPTY,ANSWER]
        evidence['tokens']['demo']=0; evidence['demo']={'demos':[]}; evidence['truncated']['demo']=False
    else: raise ValueError('Unknown tier-1 arm')
    prompt='\n\n'.join(parts)
    evidence['tokens']['total']=counter.count_chat(prompt)
    if evidence['tokens']['total']+64>8192: raise ValueError('Context overflow')
    return prompt,evidence

def cache_paths(dataset,split,reference_root):
    folder=Path(reference_root)/dataset/split
    files={k:folder/v for k,v in {'specs':'specs.jsonl','prompts':'prompts.jsonl','manifest':'bundle_manifest.json'}.items()}
    for p in files.values():
        if not p.is_file(): raise FileNotFoundError(f'Missing completed B2 cache: {p}. Set REFERENCE_ROOT to matching four-split B2 output.')
    m=json.loads(files['manifest'].read_text(encoding='utf-8'))
    if (m.get('arm'),m.get('dataset'),m.get('split'))!=('B2',dataset,split): raise ValueError('B2 manifest identity mismatch')
    if sha256(files['prompts'])!=m['prompts_sha256']: raise ValueError('B2 prompt file SHA256 mismatch')
    if sha256(files['specs'])!=m['spec_sha256']: raise ValueError('B2 spec file SHA256 mismatch')
    if m['tokenizer_revision']!='b2cff646eb4bb1d68355c01b18ae02e7cf42d120': raise ValueError('Tokenizer revision mismatch')
    return files,m

def completed_bundle(folder,arm,files,reference):
    mp=folder/'bundle_manifest.json'
    bundle=folder/f'{reference["dataset"]}_{reference["split"]}_{arm.lower().replace("-","_")}_kaggle.zip'
    if not (mp.is_file() and bundle.is_file()): return None
    m=json.loads(mp.read_text(encoding='utf-8'))
    if m.get('arm')!=arm or m.get('prompt_variant')!=VARIANTS[arm] or m.get('count')!=reference['count']: return None
    if m.get('reference_b2_sha256')!={k:sha256(p) for k,p in files.items()}: return None
    for name,key in [('prompts.jsonl','prompts_sha256'),('pairing_audit.jsonl','pairing_audit_sha256')]:
        p=folder/name
        if not p.is_file() or sha256(p)!=m.get(key): return None
    try:
        with zipfile.ZipFile(bundle) as z:
            if json.loads(z.read('bundle_manifest.json'))!=m: return None
            for name,key in [('prompts.jsonl','prompts_sha256'),('pairing_audit.jsonl','pairing_audit_sha256')]:
                h=hashlib.sha256()
                with z.open(name) as f:
                    for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
                if h.hexdigest()!=m[key]: return None
    except (zipfile.BadZipFile,KeyError,OSError,ValueError):
        return None  # An interrupted ZIP write is rebuilt, never treated as complete.
    return bundle

def prepare(arm,reference_root,out_root,runs,tokenizer,frozen_root=None,reuse_completed=True):
    if arm not in VARIANTS: raise ValueError('Unknown arm')
    counter=TokenCounter(None); counter.tok=tokenizer; counter.approx=False
    out_root=Path(out_root); bundles=[]
    for dataset,split in runs:
        started=time.monotonic()
        print(f'[{arm} {dataset}/{split}] checking B2 source hashes...',flush=True)
        files,reference=cache_paths(dataset,split,reference_root)
        folder=out_root/dataset/split
        cached=completed_bundle(folder,arm,files,reference) if reuse_completed else None
        if cached:
            print(f'[{arm} {dataset}/{split}] verified completed bundle, reuse {reference["count"]} prompts',flush=True)
            bundles.append(cached)
            continue
        source={str(r['id']):r for r in rows(files['prompts'])}
        if len(source)!=reference['count']: raise ValueError('Incomplete/duplicate B2 prompt IDs')
        eligible=None
        if frozen_root:
            eligible={r['id'] for r in rows(Path(frozen_root)/dataset/'train_manifest.jsonl') if r['keep_in_bank']}
        folder.mkdir(parents=True,exist_ok=True)
        prompt_path=folder/'prompts.jsonl'; audit_path=folder/'pairing_audit.jsonl'
        seen=set(); same=missing=outside=0; example=None
        with prompt_path.open('w',encoding='utf-8',newline='\n') as out,audit_path.open('w',encoding='utf-8',newline='\n') as audit:
            for spec in rows(files['specs']):
                uid=str(spec['id'])
                if uid in seen or uid not in source: raise ValueError('Duplicate/unmatched B2 spec ID')
                seen.add(uid); original=source[uid]
                if original['label']!=spec['label']: raise ValueError('B2 target label mismatch')
                if hashlib.sha256(original['prompt'].encode()).hexdigest()!=original['prompt_sha256']: raise ValueError('B2 row prompt hash mismatch')
                demos=spec['demonstrations']
                if len(demos)!=1 or original['demo_ids']!=[demos[0]['function_uid']]: raise ValueError('B2 demonstration mismatch')
                prompt,e=render_paired(arm,spec,original['prompt'],counter,reference=original)
                h=hashlib.sha256(prompt.encode()).hexdigest(); same+=h==original['prompt_sha256']
                graph_missing=not bool(spec.get('nodes')); missing+=graph_missing
                outside_bank=eligible is not None and demos[0]['function_uid'] not in eligible
                outside+=outside_bank
                ds=[] if arm=='B1' else original['demo_ids']
                record={'id':uid,'dataset':dataset,'split':split,'arm':arm,'prompt_variant':VARIANTS[arm],'seed':42,
                        'label':spec['label'],'prompt':prompt,'prompt_sha256':h,'reference_b2_prompt_sha256':original['prompt_sha256'],
                        'demo_ids':ds,'graph_missing':graph_missing,'tokens':e['tokens'],'truncated':e['truncated'],
                        'fresh_inference_required':arm=='B2-rep'}
                out.write(json.dumps(record,ensure_ascii=False)+'\n')
                audit.write(json.dumps({'id':uid,'reference_b2_prompt_sha256':original['prompt_sha256'],'prompt_sha256':h,
                                       'same_as_b2':h==original['prompt_sha256'],'reference_demo_id':demos[0]['function_uid'],
                                       'true_demo_label':demos[0]['target'],'displayed_demo_label':None if arm=='B1' else 1-int(demos[0]['target']) if arm=='B2-flip' else demos[0]['target'],
                                       'reference_demo_outside_new_frozen_bank':outside_bank})+'\n')
                if example is None: example=prompt
                if len(seen)%100==0 or len(seen)==reference['count']:
                    elapsed=time.monotonic()-started
                    rate=len(seen)/max(elapsed,1e-9)
                    print(f'[{arm} {dataset}/{split}] {len(seen)}/{reference["count"]} | {rate:.1f} samples/s | ETA {(reference["count"]-len(seen))/max(rate,1e-9):.0f}s',flush=True)
        if seen!=set(source): raise ValueError('B2 specs/prompt ID sets differ')
        if arm=='B2-rep' and same!=len(seen): raise ValueError('B2-rep changed prompt')
        if arm=='B2-flip' and same: raise ValueError('B2-flip failed to change label')
        manifest={'arm':arm,'prompt_variant':VARIANTS[arm],'dataset':dataset,'split':split,'seed':42,'count':len(seen),
                  'prompts_sha256':sha256(prompt_path),'pairing_audit_sha256':sha256(audit_path),'reference_b2_sha256':{k:sha256(p) for k,p in files.items()},
                  'reference_root':str(Path(reference_root).resolve()),'same_prompt_as_b2':same,'missing_graphs':missing,
                  'reference_demos_outside_new_frozen_bank':outside,'retrieval_scope':'paired_to_existing_B2_not_reselected',
                  'cache_reuse':{'joern':'graph from B2 specs','codet5':'reuse B2 selected demo IDs; no encoder or retrieval rerun'},
                  'fresh_inference_required':arm=='B2-rep','graph_prefix':PREFIX,'token_budget':BUDGET,
                  'tokenizer':reference['tokenizer'],'tokenizer_revision':reference['tokenizer_revision'],
                  'model_repo':reference['model_repo'],'quantization':reference['quantization'],'prompt_budget_tokens':8192,
                  'source_sha256':sha256(Path(__file__))}
        mp=folder/'bundle_manifest.json'; mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
        (folder/'prompt_preview.txt').write_text(example or '',encoding='utf-8')
        bundle=folder/f'{dataset}_{split}_{arm.lower().replace("-","_")}_kaggle.zip'
        with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
            for p in (prompt_path,audit_path,mp,folder/'prompt_preview.txt'): z.write(p,p.name)
        bundles.append(bundle)
        print(arm,dataset,split,len(seen),'same B2:',same,'missing graph:',missing,'old demo outside new bank:',outside,flush=True)
    archive=out_root/f'grace_{arm.lower().replace("-","_")}_inputs.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_STORED) as z:
        for p in bundles:z.write(p,p.name)
    return bundles,archive
