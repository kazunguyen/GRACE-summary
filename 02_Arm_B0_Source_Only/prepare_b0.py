"""Build B0 with the B2 scaffolding retained and graph/demo payloads empty."""
import hashlib
import json
import sys
import zipfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
BASELINE=HERE.parent/'01_Author_Baseline_Unified'
sys.path.insert(0,str(BASELINE/'diagnostic_kit/src'))
from grace_diag.probes import ROLE, QUESTION, NODE_HEAD, EDGE_HEAD, ANSWER
from grace_diag.token_budget import TokenCounter

VARIANT='b0_b2_empty_blocks_v1'
DEMO_HEAD='The following is an example, and it is .'
TOKENIZER='Qwen/Qwen3-Coder-30B-A3B-Instruct'
REVISION='b2cff646eb4bb1d68355c01b18ae02e7cf42d120'
MODEL_SHA256='f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335'

def sha256(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def render_b0(code,counter):
    # Same target fitting, headings, question, ordering and separators as Figure-6 B2.
    # The demo label is also empty: there is no train/target label in this renderer.
    fitted=counter.fit(code.strip(),3000,marker='\n/* [TRUNCATED TARGET] */')
    graph=f'{NODE_HEAD}\n\n{EDGE_HEAD}\n'
    demo=f'{DEMO_HEAD}\n'
    prompt='\n\n'.join([ROLE,fitted.text,QUESTION,graph,demo,ANSWER])
    total=counter.count_chat(prompt)
    if total+64>8192: raise ValueError('B0 context overflow')
    return prompt,{'context_limit_tokens':8192,'prompt_tokens':total,
                   'target_tokens_used':fitted.tokens,'target_truncated':fitted.truncated,
                   'graph_tokens_used':0,'demo_tokens_used':0,'graph_nodes_used':0,'graph_edges_used':0,
                   'graph_missing':False,'graph_intentionally_empty':True,'demo_intentionally_empty':True,
                   'scaffolding_tokens':counter.count(graph+'\n\n'+demo),'prompt_utf8_bytes':len(prompt.encode())}

def prepare(freeze_root,out_root,runs,tokenizer):
    freeze_root=Path(freeze_root); out_root=Path(out_root)
    snapshot=freeze_root/'freeze_manifest.json'
    frozen=json.loads(snapshot.read_text(encoding='utf-8'))
    counter=TokenCounter(None); counter.tok=tokenizer; counter.approx=False
    bundles=[]
    for dataset,split in runs:
        if dataset not in ('devign','reveal') or split not in ('validation','test'): raise ValueError('Unknown split')
        src=freeze_root/dataset/f'{split}_raw.jsonl'
        source_hash=sha256(src)
        if source_hash!=frozen['datasets'][dataset]['files_sha256'][src.name]: raise ValueError('Frozen raw hash mismatch')
        folder=out_root/dataset/split; folder.mkdir(parents=True,exist_ok=True)
        path=folder/'prompts.jsonl'; seen=set(); truncated=0; sample=None
        with src.open(encoding='utf-8') as f,path.open('w',encoding='utf-8',newline='\n') as out:
            for line in f:
                r=json.loads(line); uid=str(r['id'])
                if uid in seen: raise ValueError('Duplicate target ID')
                seen.add(uid)
                if r['target'] not in (0,1): raise ValueError('Non-binary target')
                prompt,metadata=render_b0(r['func'],counter)
                row={'id':uid,'dataset':dataset,'split':split,'arm':'B0','prompt_variant':VARIANT,
                     'label':r['target'],'prompt':prompt,'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),
                     'code_sha256':hashlib.sha256(r['func'].encode()).hexdigest(),
                     'demo_ids':[],'tokens':metadata,'graph_missing':False,'graph_intentionally_empty':True}
                out.write(json.dumps(row,ensure_ascii=False)+'\n'); truncated+=metadata['target_truncated']
                if sample is None: sample=prompt
        assert len(seen)==frozen['datasets'][dataset]['per_split'][split]['n']
        manifest={'arm':'B0','prompt_variant':VARIANT,'dataset':dataset,'split':split,'count':len(seen),
                  'prompts_sha256':sha256(path),'frozen_raw_sha256':source_hash,'freeze_manifest_sha256':sha256(snapshot),
                  'tokenizer':TOKENIZER,'tokenizer_revision':REVISION,'model_repo':'ggml-org/Qwen3-Coder-30B-A3B-Instruct-GGUF',
                  'quantization':'Q4_K_M','expected_model_sha256':MODEL_SHA256,'prompt_budget_tokens':8192,
                  'target_code_max_tokens':3000,'target_truncated_count':truncated,'demo_ids':[],
                  'empty_fields':['graph_nodes','graph_edges','demo_code','demo_label'],
                  'source_sha256':{'prepare_b0.py':sha256(Path(__file__)),
                      'baseline_probes.py':sha256(BASELINE/'diagnostic_kit/src/grace_diag/probes.py'),
                      'baseline_token_budget.py':sha256(BASELINE/'diagnostic_kit/src/grace_diag/token_budget.py')}}
        mp=folder/'bundle_manifest.json'; mp.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
        (folder/'prompt_preview.txt').write_text(sample or '',encoding='utf-8')
        bundle=folder/f'{dataset}_{split}_b0_kaggle.zip'
        with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
            for p in (path,mp,folder/'prompt_preview.txt'): z.write(p,p.name)
        print(dataset,split,len(seen),'prompts;',truncated,'truncated;',bundle,flush=True)
        bundles.append(bundle)
    archive=out_root/'grace_b0_inputs.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_STORED) as z:
        for p in bundles: z.write(p,p.name)
    return bundles,archive
