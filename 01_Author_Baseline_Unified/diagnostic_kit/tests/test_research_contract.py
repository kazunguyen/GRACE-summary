import sys
from pathlib import Path
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from grace_diag.native_scoring import binary_scores
from grace_diag.probes import render_graph
from grace_diag.token_budget import TokenCounter
from freeze_research_data import tokens

def test_literal_preservation():
    assert tokens('int a=1; // comment\n')==tokens('int /* hi */ a = 1;')
    assert tokens('f("a b");')!=tokens('f("ab");')
    assert '"http://host"' in tokens('f("http://host");')

def test_scores_do_not_require_top5_or_greedy_binary():
    values=np.arange(10,dtype=float)
    result=binary_scores(values,[0,1])
    assert result['greedy_token_id']==9
    assert result['s']==pytest.approx(1/(1+np.exp(-1)))
    assert {x['token_id'] for x in result['top5']}.isdisjoint({0,1})
    result=binary_scores([-10000,-10001,0],[0,1])
    assert result['pred_argmax']==0 and result['s']>0

def test_bad_scores_rejected():
    with pytest.raises(ValueError): binary_scores([0,float('nan')],[0,1])
    with pytest.raises(ValueError): binary_scores([0,1],[0,0])

def test_full_graph_cap_and_h2_source_guard():
    nodes=[{'id':str(i),'code':str(i)} for i in range(100)]
    edges=[{'start':str(i%40),'end':str((i+1)%40),'label':'AST'} for i in range(200)]
    _,info=render_graph('fill',{'nodes':nodes,'edges':edges},TokenCounter(None),100000,{'nodes':40,'edges':80},42,None)
    assert info['rendered_nodes']<=40 and info['rendered_edges']<=80
    with pytest.raises(ValueError):
        render_graph('h2',{'h2_evidence':'text'},TokenCounter(None),1500,{'nodes':40,'edges':80},42,None)
