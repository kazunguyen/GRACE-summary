"""B2 baseline: same Figure 6 renderer used by the diagnostic kit."""
from pathlib import Path
import sys
KIT_SRC = Path(__file__).resolve().parent / 'diagnostic_kit' / 'src'
sys.path.insert(0, str(KIT_SRC))
from grace_diag.probes import render_arm
from grace_diag.token_budget import TokenCounter

class PromptBuilder:
    def __init__(self, template_path=None, tokenizer=None, context_limit_tokens=8192, graph_nodes_max=40,
                 graph_edges_max=80, target_code_max_tokens=3000, standard_demo_max_tokens=1500, graph_max_tokens=1500):
        if tokenizer is None: raise ValueError('The model tokenizer is required')
        self.counter=TokenCounter(None)
        self.counter.tok=tokenizer
        self.counter.approx=False
        self.budget={'total':context_limit_tokens,'target_code':target_code_max_tokens,
                     'demo':standard_demo_max_tokens,'graph':graph_max_tokens,'reserve':64}
        self.prefix={'nodes':graph_nodes_max,'edges':graph_edges_max}

    def build_prompt(self, target_sample, demonstration_sample=None):
        if not demonstration_sample or demonstration_sample.get('target') not in (0,1):
            raise ValueError('B2 requires a labeled demonstration')
        edges=[]
        for e in target_sample.get('edges') or []:
            if not isinstance(e, dict): raise ValueError('CPG edge must be an object')
            a=e.get('start',e.get('source',e.get('src'))); b=e.get('end',e.get('target',e.get('dst')))
            if a is None or b is None: raise ValueError('CPG edge missing endpoint')
            edges.append(dict(e,start=a,end=b))
        spec={'id':str(target_sample.get('id','unknown')), 'query_code':target_sample.get('func',''),
              'nodes':target_sample.get('nodes') or [], 'edges':edges,
              'demonstrations':[{'function_uid':str(demonstration_sample.get('id','unknown')),
                'func':demonstration_sample.get('func',''),'target':demonstration_sample['target']}]}
        rendered=render_arm(spec,'B2',counter=self.counter,budget=self.budget,graph_prefix=self.prefix)
        e=rendered.evidence; d=e['demo']['demos'][0]; g=e['graph']
        return rendered.prompt, {'context_limit_tokens':self.budget['total'], 'prompt_tokens':e['tokens']['total'],
            'target_tokens_used':e['tokens']['code'], 'graph_tokens_used':e['tokens']['graph'], 'demo_tokens_used':d.get('tokens',0),
            'target_truncated':e['truncated']['code'], 'demo_truncated':d.get('truncated',False),
            'demo_below_25_percent':bool(d.get('original_tokens') and d.get('tokens',0)<0.25*d['original_tokens']),
            'graph_nodes_used':g.get('rendered_nodes',0),'graph_edges_used':g.get('rendered_edges',0),
            'graph_missing':g.get('missing',False),'prompt_utf8_bytes':len(rendered.prompt.encode('utf-8'))}
