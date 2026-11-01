import json
import pytest
import ast
from pathlib import Path
from validation_lock import make_lock,persist_lock,require_test_lock,pick_threshold,RULES_SHA256

def manifest():
    return {'model_sha256':'model','tokenizer':'tok','tokenizer_revision':'rev','quantization':'Q4_K_M',
            'llama_cpp_python':'0.3.16','scoring':'unconstrained_first_token_logits_v1','context_tokens':8192}
def expected():return [{'id':'a','label':0,'prompt_sha256':'a'},{'id':'b','label':1,'prompt_sha256':'b'}]
def records():return [dict(r,dataset='devign',split='validation',arm='B0',model_sha256='model',seed=42,valid=True,s=v) for r,v in zip(expected(),(.1,.9))]

def test_complete_validation_only_and_immutable_lock(tmp_path):
    p=tmp_path/'thresholds.json';entry=make_lock(expected(),records(),'B0','devign',manifest(),'prompts')
    assert entry['tau']==.5
    persist_lock(p,entry)
    require_test_lock(p,'B0','devign',manifest(),'prompts')
    with pytest.raises(ValueError,match='immutable'):persist_lock(p,dict(entry,tau=.7))
    with pytest.raises(ValueError,match='no locked'):require_test_lock(p,'B2','devign',manifest())
    with pytest.raises(ValueError,match='differs'):require_test_lock(p,'B0','devign',dict(manifest(),model_sha256='other'))

def test_no_partial_or_test_data_can_choose_threshold():
    with pytest.raises(ValueError,match='Incomplete'):make_lock(expected(),records()[:1],'B0','devign',manifest(),'prompts')
    bad=records();bad[0]['split']='test'
    with pytest.raises(ValueError,match='validation'):make_lock(expected(),bad,'B0','devign',manifest(),'prompts')
    bad=records();bad[0]['prompt_sha256']='changed'
    with pytest.raises(ValueError,match='mismatch'):make_lock(expected(),bad,'B0','devign',manifest(),'prompts')

def test_degenerate_and_invalid_are_explicit():
    rr=records()
    for r in rr:r['s']=.5
    e=pick_threshold(rr)
    assert e['tau']==.5 and e['validation_mcc'] is None and e['degenerate']
    rr[0]['valid']=False
    with pytest.raises(ValueError,match='both classes'):pick_threshold(rr)

def test_ties_and_missing_lock(tmp_path):
    assert pick_threshold(records())['tau']==.5
    with pytest.raises(ValueError,match='missing'):require_test_lock(tmp_path/'absent.json','B0','devign',manifest())

def test_future_kaggle_notebooks_embed_rules_and_test_gate():
    root=Path(__file__).resolve().parents[1]
    core=(root/'Runs-management/validation_lock.py').read_text(encoding='utf-8').strip()
    for rel in ('01_Author_Baseline_Unified/notebooks/02_kaggle_qwen_q4_b2.ipynb','02_Arm_B0_Source_Only/notebooks/02_kaggle_qwen_q4_b0.ipynb'):
        n=json.loads((root/rel).read_text(encoding='utf-8'))
        helper=next(''.join(c['source']).split('\n',1)[1] for c in n['cells'] if c.get('id')=='validation-threshold-helper')
        assert helper.strip()==core
        source=next(''.join(c['source']).split('\n',1)[1] for c in n['cells'] if ''.join(c.get('source',[])).startswith('%%writefile /kaggle/working/kaggle_'))
        ast.parse(source)
        assert 'require_test_lock(thresholds_path' in source
        assert "if split == 'validation' and limit is None:" in source
