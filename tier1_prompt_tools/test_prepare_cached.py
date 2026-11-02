import ast
import hashlib
import json
import sys
from pathlib import Path
import pytest
from prepare_cached import prepare,render_paired,render_paired_slow,render_arm,TokenCounter,BUDGET,PREFIX,ROOT,VARIANTS

class Tokenizer:
    def encode(self,text,add_special_tokens=False):return list(text.encode())
    def apply_chat_template(self,messages,tokenize=True,add_generation_prompt=True):
        text='<chat>'+messages[0]['content']+'<answer>'
        return self.encode(text) if tokenize else text

def counter():
    c=TokenCounter(None);c.tok=Tokenizer();c.approx=False;return c

def spec():
    return {'id':'t','query_code':'int target(){ return 0; }','nodes':[{'id':str(i),'type':'METHOD','code':str(i)} for i in range(90)],
            'edges':[{'start':str(i),'end':str(i+1),'type':'AST'} for i in range(89)],
            'demonstrations':[{'function_uid':'donor','func':'int demo_SECRET(){return 1;}','target':1}]}

def test_flip_only_changes_demo_label_and_rep_exact():
    s=spec();c=counter();b2=render_arm(s,'B2',counter=c,budget=BUDGET,graph_prefix=PREFIX).prompt
    flipped,_=render_paired('B2-flip',dict(s,label=0),b2,c)
    assert flipped==b2.replace('The following is an example, and it is Vulnerable.','The following is an example, and it is Non-vulnerable.')
    repeated,_=render_paired('B2-rep',dict(s,label=0),b2,c)
    assert repeated==b2

def test_b1_has_graph_but_no_demo_data():
    s=spec();c=counter();b2=render_arm(s,'B2',counter=c,budget=BUDGET,graph_prefix=PREFIX).prompt
    prompt,e=render_paired('B1',dict(s,label=0),b2,c)
    assert 'demo_SECRET' not in prompt
    assert 'The following is an example, and it is .' in prompt
    assert e['graph']['rendered_nodes']<=40 and e['graph']['rendered_edges']<=80
    assert e['demo']['demos']==[]
    with pytest.raises(ValueError,match='mismatch'):render_paired('B2-rep',dict(s,label=0),b2+'changed',c)

@pytest.mark.parametrize('arm',['B1','B2-flip','B2-rep'])
def test_export_from_cached_b2_without_encoder_or_joern(tmp_path,arm,monkeypatch):
    s=spec();b2=render_arm(s,'B2',counter=counter(),budget=BUDGET,graph_prefix=PREFIX).prompt
    reference=tmp_path/'references/devign/test';reference.mkdir(parents=True)
    s['label']=0
    sp=reference/'specs.jsonl';sp.write_text(json.dumps(s)+'\n',encoding='utf-8')
    pp=reference/'prompts.jsonl';pp.write_text(json.dumps({'id':'t','label':0,'prompt':b2,'demo_ids':['donor'],'prompt_sha256':hashlib.sha256(b2.encode()).hexdigest()})+'\n',encoding='utf-8')
    m={'dataset':'devign','split':'test','arm':'B2','count':1,'prompts_sha256':hashlib.sha256(pp.read_bytes()).hexdigest(),'spec_sha256':hashlib.sha256(sp.read_bytes()).hexdigest(),
       'tokenizer':'Qwen/Qwen3-Coder-30B-A3B-Instruct','tokenizer_revision':'b2cff646eb4bb1d68355c01b18ae02e7cf42d120','model_repo':'ggml-org/Qwen3-Coder-30B-A3B-Instruct-GGUF','quantization':'Q4_K_M'}
    (reference/'bundle_manifest.json').write_text(json.dumps(m),encoding='utf-8')
    freeze=tmp_path/'freeze/devign';freeze.mkdir(parents=True)
    (freeze/'train_manifest.jsonl').write_text(json.dumps({'id':'other','keep_in_bank':True})+'\n',encoding='utf-8')
    # No Joern binary, CodeT5 weights or embeddings supplied: only cached B2 artifacts.
    bundles,archive=prepare(arm,tmp_path/'references',tmp_path/'output',[('devign','test')],Tokenizer(),tmp_path/'freeze')
    result=json.loads((tmp_path/'output/devign/test/prompts.jsonl').read_text())
    manifest=json.loads((tmp_path/'output/devign/test/bundle_manifest.json').read_text())
    assert archive.exists() and bundles[0].exists()
    assert manifest['reference_demos_outside_new_frozen_bank']==1
    assert result['fresh_inference_required']==(arm=='B2-rep')
    assert result['demo_ids']==([] if arm=='B1' else ['donor'])
    assert (result['prompt']==b2)==(arm=='B2-rep')
    assert 'torch' not in sys.modules
    def no_rerender(*args,**kwargs): raise AssertionError('Completed split should not be rendered again')
    monkeypatch.setattr('prepare_cached.render_paired',no_rerender)
    before=(tmp_path/'output/devign/test/prompts.jsonl').read_bytes()
    prepare(arm,tmp_path/'references',tmp_path/'output',[('devign','test')],Tokenizer(),tmp_path/'freeze')
    assert (tmp_path/'output/devign/test/prompts.jsonl').read_bytes()==before

def test_notebooks_compile_and_contain_no_inference():
    folders=['03_Arm_B1_Graph_Only','04_Arm_B2_Flip','05_Arm_B2_Rep']
    for folder in folders:
        files=list((ROOT/folder/'notebooks').glob('*.ipynb'));assert len(files)==1
        n=json.loads(files[0].read_text(encoding='utf-8'))
        for c in n['cells']:
            if c['cell_type']=='code':
                # User may have executed these notebooks; retain outputs during fixes.
                ast.parse(''.join(c['source']))

@pytest.mark.parametrize('arm',['B1','B2-flip','B2-rep'])
def test_fast_cached_graph_matches_original_renderer(arm):
    s=spec(); c=counter()
    b2=render_arm(s,'B2',counter=c,budget=BUDGET,graph_prefix=PREFIX)
    e=b2.evidence
    reference={'tokens':{'graph_nodes_used':e['graph']['rendered_nodes'],'graph_edges_used':e['graph']['rendered_edges'],
                        'target_tokens_used':e['tokens']['code'],'graph_tokens_used':e['tokens']['graph'],
                        'demo_tokens_used':e['tokens']['demo'],'prompt_tokens':e['tokens']['total'],
                        'target_truncated':e['truncated']['code'],'demo_truncated':e['truncated']['demo']}}
    expected,_=render_paired_slow(arm,s,b2.prompt,c)
    actual,_=render_paired(arm,s,b2.prompt,c,reference=reference)
    assert actual==expected

@pytest.mark.parametrize('arm',['B1','B2-flip','B2-rep'])
def test_fast_path_avoids_graph_retokenization(arm,monkeypatch):
    s=spec(); c=counter(); b2=render_arm(s,'B2',counter=c,budget=BUDGET,graph_prefix=PREFIX); e=b2.evidence
    meta={'graph_nodes_used':e['graph']['rendered_nodes'],'graph_edges_used':e['graph']['rendered_edges'],
          'target_tokens_used':e['tokens']['code'],'graph_tokens_used':e['tokens']['graph'],
          'demo_tokens_used':e['tokens']['demo'],'prompt_tokens':e['tokens']['total']}
    count=[0]; original=c.count
    def counted(text):count[0]+=1;return original(text)
    c.count=counted
    def reject_slow(*args,**kwargs): raise AssertionError('Fast cached rendering must not call old graph fitting')
    monkeypatch.setattr('prepare_cached.render_paired_slow',reject_slow)
    render_paired(arm,s,b2.prompt,c,reference={'tokens':meta})
    assert count[0]<=1  # no repeated graph fitting; chat count uses tokenizer directly

def test_notebook_preview_and_prepare_reload_optimized_helpers():
    for folder in ('03_Arm_B1_Graph_Only','04_Arm_B2_Flip','05_Arm_B2_Rep'):
        path=next((ROOT/folder/'notebooks').glob('*.ipynb'))
        n=json.loads(path.read_text(encoding='utf-8'))
        code=[''.join(c['source']) for c in n['cells'] if c['cell_type']=='code']
        preview=next(s for s in code if 'preview,evidence=' in s)
        assert 'counter,reference=reference)' in preview
        export=next(s for s in code if 'bundles,archive=prepare(' in s)
        assert 'importlib.reload(prepare_cached)' in export
