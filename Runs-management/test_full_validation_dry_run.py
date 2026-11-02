import numpy as np
import pytest
import dry_run_full_validation as dry


def make_nodes(n):return [{'id':str(i),'type':'CALL','code':' a(1);\n'+'x'*80} for i in range(n)]


def test_graph_compaction_keeps_exact_display_and_source_order():
    nodes=make_nodes(60);edges=[{'source':str(i),'target':str(i+1),'type':'AST'} for i in range(59)]
    cn,ce=dry.compact_graph(nodes,edges)
    assert len(cn)==40 and len(ce)==39
    assert dry.format_nodes(cn)==dry.format_nodes(nodes[:40])
    assert all(e['start'] in {n['id'] for n in cn} and e['end'] in {n['id'] for n in cn} for e in ce)


def test_project_scaffold_and_no_gold_target_label():
    spec={'id':'validation:x','query_code':'int f(){return 0;}','nodes':[],'edges':[],
          'demonstrations':[{'function_uid':'train:x','func':'int g(){}','target':0}]}
    counter=dry.TokenCounter(None)
    rendered=dry.render_project(spec,'B0',42,counter,None)
    assert dry.NODE_HEAD+'\n\n'+dry.EDGE_HEAD in rendered.prompt
    assert 'The following is an example, and it is .\n' in rendered.prompt
    assert not rendered.evidence['demo']['demos']
    with pytest.raises(ValueError,match='Target label'):
        dry.render_project(dict(spec,label=1),'B0',42,counter,None)


def test_lazy_graph_selector_matches_original_selector():
    rows=[{'function_uid':f'train:{i}','func':'int f(){}','target':i%2,'nodes':make_nodes(10+i),'n_nodes':10+i,'edges':[]} for i in range(30)]
    base=dry.DonorPool(rows)
    lazy=object.__new__(dry.LazyDonors);lazy.rows=rows;lazy.n_nodes=np.array([len(r['nodes']) for r in rows])
    for seed in (42,43,44):
        uid,info=lazy.selected_graph('validation:1',seed,20)
        _,_,original=base.shuffle_graph('validation:1',seed,20)
        assert uid==original['donor_uid']
        assert info==original


def test_missing_target_graph_policy_does_not_fabricate_graph():
    renderer=dry.project_renderer({}, {}, {},'empty')
    text,info=renderer('shuffle',{'id':'missing','source_node_count':0},None,1500,dry.PREFIX,42,None)
    assert text=='' and info['missing'] and info['tokens']==0
    renderer=dry.project_renderer({}, {}, {},'blocked')
    with pytest.raises(ValueError,match='Missing target graph'):
        renderer('shuffle',{'id':'missing','source_node_count':0},None,1500,dry.PREFIX,42,None)
