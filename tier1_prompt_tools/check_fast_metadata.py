"""Check every real B2 row can take the optimized rendering path (no model load)."""
from prepare_cached import BASELINE,rows
required=('graph_nodes_used','graph_edges_used','target_tokens_used','graph_tokens_used','demo_tokens_used','prompt_tokens')
for d in ('devign','reveal'):
    for s in ('validation','test'):
        path=BASELINE/f'output/local_full/bundles_recovered_joern_final_20261031/{d}/{s}/prompts.jsonl'
        count=missing=0
        for r in rows(path):
            count+=1
            missing+=not all(k in r.get('tokens',{}) for k in required)
        print(d,s,'total',count,'slow-fallback rows',missing,flush=True)
        assert missing==0
