import ast
import importlib.util
import json
import zipfile
from pathlib import Path
import pytest
from prepare_b0 import render_b0,VARIANT,MODEL_SHA256,ROLE,QUESTION,NODE_HEAD,EDGE_HEAD,DEMO_HEAD,ANSWER
from kaggle_b0_runtime import discover_bundles,restore_checkpoint,load_bundle,binary_scores

ROOT=Path(__file__).parent

class Counter:
    def count(self,text): return len(text)
    def count_chat(self,text): return len(text)+20
    def fit(self,text,budget,marker):
        from types import SimpleNamespace
        cut=text if len(text)<=budget else text[:budget-len(marker)]+marker
        return SimpleNamespace(text=cut,tokens=len(cut),truncated=cut!=text)

def test_b0_keeps_scaffolding_but_no_payload():
    code='int f(){ return 123; }'
    prompt,meta=render_b0(code,Counter())
    expected='\n\n'.join([ROLE,code,QUESTION,f'{NODE_HEAD}\n\n{EDGE_HEAD}\n',DEMO_HEAD+'\n',ANSWER])
    assert prompt==expected
    assert meta['graph_nodes_used']==meta['graph_edges_used']==meta['demo_tokens_used']==0
    assert 'Vulnerable' not in prompt.split(DEMO_HEAD)[1]
    assert meta['graph_intentionally_empty'] and not meta['graph_missing']

def test_same_target_truncation_contract():
    from grace_diag.probes import render_arm
    from grace_diag.token_budget import TokenCounter
    # Compare actual B2 target fit (same counter/marker), without model download.
    c=TokenCounter(None)
    code='int f() { return 0; }\n'*1000
    b0,m=render_b0(code,c)
    b2=render_arm({'id':'t','query_code':code,'nodes':[],'edges':[],
                  'demonstrations':[{'function_uid':'d','func':'int g(){}','target':0}]},'B2',counter=c)
    fit=c.fit(code.strip(),3000,marker='\n/* [TRUNCATED TARGET] */')
    assert fit.text in b0 and fit.text in b2.prompt
    assert m['target_truncated']

def bundle(path,score_hash='a',arm='B0'):
    path.parent.mkdir(parents=True,exist_ok=True)
    import hashlib
    row={'id':'x','dataset':'devign','split':'test','arm':arm,'prompt_variant':VARIANT,
         'demo_ids':[],'label':0,'prompt':score_hash,'prompt_sha256':hashlib.sha256(score_hash.encode()).hexdigest()}
    payload=(json.dumps(row)+'\n').encode()
    m={'dataset':'devign','split':'test','arm':arm,'prompt_variant':VARIANT,'count':1,
       'prompts_sha256':hashlib.sha256(payload).hexdigest(),'freeze_manifest_sha256':'frozen'}
    with zipfile.ZipFile(path,'w') as z:
        z.writestr('bundle_manifest.json',json.dumps(m)); z.writestr('prompts.jsonl',payload)

def test_discovery_nested_other_account_and_wrapper(tmp_path):
    direct=tmp_path/'input/notebooks/different-account/unrelated-slug/outputs/devign_test_b0_kaggle.zip'
    bundle(direct)
    master=tmp_path/'input/datasets/another-owner/anything/grace_b0_inputs.zip'
    master.parent.mkdir(parents=True)
    with zipfile.ZipFile(master,'w') as z: z.write(direct,direct.name)
    found=discover_bundles(tmp_path/'input',tmp_path/'work',[('devign','test')])
    assert load_bundle(found['devign','test'])[0]['arm']=='B0'
    other=tmp_path/'input/another/devign_test_b0_kaggle.zip'; bundle(other,'different')
    with pytest.raises(ValueError,match='Conflicting'): discover_bundles(tmp_path/'input',tmp_path/'work',[('devign','test')])

def test_reject_b2_and_checkpoint_zip_traversal(tmp_path):
    b2=tmp_path/'input/b2.zip'; bundle(b2,arm='B2')
    with pytest.raises(ValueError): load_bundle(b2)
    checkpoint=tmp_path/'input/account/any-slug/grace_b0_checkpoint.zip'; checkpoint.parent.mkdir(parents=True)
    with zipfile.ZipFile(checkpoint,'w') as z: z.writestr('../outside.txt','bad')
    with pytest.raises(ValueError,match='Unsafe'): restore_checkpoint(tmp_path/'input',tmp_path/'output')
    assert not (tmp_path/'outside.txt').exists()

def test_notebooks_clean_and_all_code_compiles():
    for path in (ROOT/'notebooks').glob('*.ipynb'):
        n=json.loads(path.read_text(encoding='utf-8'))
        assert len(n['cells'])>=5
        for c in n['cells']:
            if c['cell_type']!='code': continue
            # Existing user execution outputs are preserved when notebook source is updated.
            s=''.join(c['source'])
            if s.startswith('%%writefile'): s=s.split('\n',1)[1]
            ast.parse(s)
            assert 'quangdung1111' not in s

def test_binary_score_matches_canonical():
    from grace_diag.native_scoring import binary_scores as canonical
    assert binary_scores([-100,0,1,2,3,4,5],[0,1])==canonical([-100,0,1,2,3,4,5],[0,1])

def test_prepare_inference_resume_end_to_end_without_gpu(tmp_path,monkeypatch):
    import hashlib,sys,time,types
    import numpy as np
    from prepare_b0 import prepare
    from kaggle_b0_runtime import run_batch
    class Tokenizer:
        def encode(self,text,add_special_tokens=False): return list(text.encode())
        def apply_chat_template(self,messages,tokenize=True,add_generation_prompt=True):
            text='<chat>'+messages[0]['content']+'<answer>'
            return self.encode(text) if tokenize else text
    class Llama:
        def __init__(self,**kwargs): assert kwargs['seed']==42
        def tokenize(self,text,**kwargs): return list(text)
        def detokenize(self,ids): return bytes(ids)
        def reset(self): pass
        def eval(self,ids):
            self.n_tokens=len(ids); scores=np.zeros(128); scores[49]=3
            self.scores=np.tile(scores,(len(ids),1))
    tokenizer=Tokenizer()
    monkeypatch.setitem(sys.modules,'llama_cpp',types.SimpleNamespace(Llama=Llama,__version__='0.3.16'))
    monkeypatch.setitem(sys.modules,'transformers',types.SimpleNamespace(AutoTokenizer=types.SimpleNamespace(from_pretrained=lambda *a,**k:tokenizer)))
    frozen=tmp_path/'freeze'; (frozen/'devign').mkdir(parents=True)
    hashes={}
    for split in ('validation','test'):
        raw=frozen/f'devign/{split}_raw.jsonl'
        raw.write_text(''.join(json.dumps({'id':f'{split}:{i}','func':f'int f{i}(){{ return {i}; }}','target':i})+'\n' for i in (0,1)),encoding='utf-8')
        hashes[raw.name]=hashlib.sha256(raw.read_bytes()).hexdigest()
    (frozen/'freeze_manifest.json').write_text(json.dumps({'datasets':{'devign':{'files_sha256':hashes,'per_split':{'validation':{'n':2},'test':{'n':2}}}}}),encoding='utf-8')
    bundles,_=prepare(frozen,tmp_path/'bundles',[('devign','validation'),('devign','test')],tokenizer)
    # Substitute only the fake-model hash in this test bundle, never production config.
    mp=tmp_path/'model.gguf'; mp.write_bytes(b'fake model for offline integration')
    for bundle_path in bundles:
        with zipfile.ZipFile(bundle_path) as z: contents={n:z.read(n) for n in z.namelist()}
        manifest=json.loads(contents['bundle_manifest.json']); manifest['expected_model_sha256']=hashlib.sha256(mp.read_bytes()).hexdigest()
        contents['bundle_manifest.json']=json.dumps(manifest).encode()
        with zipfile.ZipFile(bundle_path,'w') as z:
            for n,data in contents.items(): z.writestr(n,data)
    out=tmp_path/'runs/devign/test'; status=tmp_path/'runs/status.json'
    args=([('devign','validation',str(bundles[0]),str(out.parent/'validation')),('devign','test',str(bundles[1]),str(out))],str(mp),'local-input',-1,None,time.time()+100,1,status)
    run_batch(*args)
    before=(out/'records.jsonl').read_bytes()
    run_batch(*args)
    assert (out/'records.jsonl').read_bytes()==before
    row=json.loads(before.decode().splitlines()[0])
    assert row['arm']=='B0' and row['demo_ids']==[] and row['valid'] and row['response_valid']
    assert json.loads(status.read_text())['state']=='complete'
    assert (status.parent/'thresholds.json').exists()

def test_embedded_runtime_matches_module():
    n=json.loads((ROOT/'notebooks/02_kaggle_qwen_q4_b0.ipynb').read_text(encoding='utf-8'))
    embedded=next(''.join(c['source']).split('\n',1)[1] for c in n['cells'] if ''.join(c.get('source',[])).startswith('%%writefile /kaggle/working/kaggle_b0_runtime.py'))
    assert embedded.strip()==(ROOT/'kaggle_b0_runtime.py').read_text(encoding='utf-8').strip()
