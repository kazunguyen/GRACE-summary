"""Read-only check of all four real B2 cache identities and six CodeT5 manifests."""
import json
from prepare_cached import BASELINE,cache_paths
root=BASELINE/'output/local_full/bundles_recovered_joern_final_20261031'
for d in ('devign','reveal'):
    for s in ('validation','test'):
        files,m=cache_paths(d,s,root)
        print(d,s,m['count'],'B2 specs/prompts SHA256 OK',flush=True)
    for s in ('train','validation','test'):
        folder=BASELINE/f'output/local_full/{d}/embedding_cache/{s}'
        m=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
        assert m['model']=='Salesforce/codet5-base@02cd2d31bb7c6d0e4d91156167b2de044989c733'
        assert m['completed']==len(m['rows']) and (folder/'vectors.npy').is_file()
        print(d,s,m['completed'],'CodeT5 cache complete',flush=True)
