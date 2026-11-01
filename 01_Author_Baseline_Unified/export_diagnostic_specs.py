"""Export diagnostic specs from explicit, frozen train and validation/test JSON/JSONL/GZ files."""
import argparse, gzip, hashlib, json
from collections import Counter
from pathlib import Path
from data_loader import standardize_sample
from embedding_engine import CodeT5Embedder
from retrieval_engine import DemonstrationRetriever
from prepare_embedding_cache import CachedEmbedder
from graph_extractor import serialize_ast_representation

def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''): h.update(block)
    return h.hexdigest()
def iter_rows(path, dataset):
    """Validate rows while streaming JSONL; retain array JSON/GZ compatibility."""
    path = Path(path)
    seen = set()

    def validated(items):
        for i, item in enumerate(items):
            if not any(item.get(k) is not None and str(item.get(k)).strip()
                       for k in ('record_id', 'id', 'idx')):
                raise ValueError(f'{path}: every sample needs a stable explicit id')
            row = standardize_sample(item, i, dataset)
            if row['id'] in seen:
                raise ValueError(f'{path}: duplicate ids')
            seen.add(row['id'])
            if not row['func']:
                raise ValueError(f'{path}: empty code')
            yield row

    if path.suffix == '.jsonl':
        with path.open(encoding='utf-8') as f:
            yield from validated(json.loads(line) for line in f if line.strip())
    else:
        opener = gzip.open if path.suffix == '.gz' else open
        with opener(path, 'rt', encoding='utf-8') as f:
            raw = json.load(f)
        if not isinstance(raw, list):
            raise ValueError(f'{path}: expected a list of samples')
        yield from validated(raw)


def read_rows(path, dataset):
    return list(iter_rows(path, dataset))

def graph_convert(rows):
    nodes=[]
    for i,n in enumerate(rows.get('nodes') or []):
        if not isinstance(n,dict): raise ValueError('CPG node is not an object')
        nodes.append(dict(n, id=n.get('id',i)))
    edges=[]
    for e in rows.get('edges') or []:
        if not isinstance(e,dict): raise ValueError('CPG edge is not an object')
        a=e.get('start', e.get('source',e.get('src'))); b=e.get('end',e.get('target',e.get('dst')))
        if a is None or b is None: raise ValueError('CPG edge has no endpoint')
        edges.append(dict(e, start=a, end=b, type=e.get('type', e.get('label', 'CONNECTED_TO'))))
    return nodes,edges

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--dataset',required=True); ap.add_argument('--split',choices=['validation','test'],required=True)
    ap.add_argument('--train',required=True); ap.add_argument('--targets',required=True); ap.add_argument('--other-targets',required=True,help='Full other evaluation split for shared donor sanitation'); ap.add_argument('--out',required=True)
    ap.add_argument('--embedding-cache', type=Path, help='Completed stage-1 cache; required for real retrieval')
    ap.add_argument('--mock-embedding',action='store_true',help='Development-only TF-IDF embedding, not scientific baseline')
    ap.add_argument('--max-targets',type=int); args=ap.parse_args()
    if not args.mock_embedding and args.embedding_cache is None:
        ap.error('Run prepare_embedding_cache.py first and supply --embedding-cache')
    train=[]
    for row in iter_rows(args.train,args.dataset):
        row['ast_repr']=serialize_ast_representation(row['nodes'],row['edges'])
        row.pop('nodes'); row.pop('edges')
        train.append(row)
    targets=read_rows(args.targets,args.dataset)
    query_hashes={hashlib.sha256(row['func'].encode()).hexdigest() for row in targets}
    for row in iter_rows(args.other_targets,args.dataset):
        query_hashes.add(hashlib.sha256(row['func'].encode()).hexdigest())
    del row
    if args.max_targets is not None: targets=targets[:args.max_targets]
    # Remove train groups with conflicting labels and identical code from target pool.
    groups={}
    for row in train: groups.setdefault(hashlib.sha256(row['func'].encode()).hexdigest(),[]).append(row)
    clean=[]; conflicts=0; overlap=0
    for h,group in groups.items():
        if len({r['target'] for r in group})>1: conflicts+=len(group); continue
        if h in query_hashes: overlap+=len(group); continue
        clean.append(group[0])
    if len(clean)<2: raise ValueError('Too few eligible train samples after deduplication')
    retriever=DemonstrationRetriever((CodeT5Embedder(force_fallback=True) if args.mock_embedding else CachedEmbedder(args.embedding_cache)),profile='code'); retriever.fit(clean)
    out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True)
    records=[]
    for target in targets:
        result=retriever.retrieve_single(target); demo=result['demo']; nodes,edges=graph_convert(target)
        records.append({'id':target['id'],'query_code':target['func'],'nodes':nodes,'edges':edges,
                        'demonstrations':[{'function_uid':demo['id'],'func':demo['func'],'target':demo['target']}],
                        'demonstrations_pair':None,'security_difference':'','label':target['target'],
                        'retrieval_metadata':result['metadata'],'graph_missing':not bool(nodes),
                        'graph_error':target.get('graph_error'),'group':target.get('commit_id') or target.get('project')})
    with out.open('w',encoding='utf-8',newline='\n') as f:
        for row in records: f.write(json.dumps(row,ensure_ascii=False)+'\n')
    donor_path=out.with_suffix(out.suffix+'.donors.jsonl')
    with donor_path.open('w',encoding='utf-8',newline='\n') as f:
        donor_ids={row['id'] for row in clean}
        for row in iter_rows(args.train,args.dataset):
            if row['id'] not in donor_ids: continue
            nodes,edges=graph_convert(row)
            f.write(json.dumps({'function_uid':row['id'],'func':row['func'],'target':row['target'],'nodes':nodes,'edges':edges},ensure_ascii=False)+'\n')
    manifest={'dataset':args.dataset,'split':args.split,'train_path':str(Path(args.train).resolve()),'train_sha256':digest(args.train),
      'target_path':str(Path(args.targets).resolve()),'target_sha256':digest(args.targets),'other_target_sha256':digest(args.other_targets),'spec_sha256':digest(out),'donor_sha256':digest(donor_path),
      'train_count':len(train),'donor_count':len(clean),'excluded_conflict_rows':conflicts,'excluded_target_overlap_rows':overlap,
      'target_count':len(targets),'label_counts':dict(Counter(str(x['target']) for x in targets)),
      'graph_missing':sum(not x['nodes'] for x in targets),'embedding':'mock_tfidf' if args.mock_embedding else 'Salesforce/codet5-base@02cd2d31bb7c6d0e4d91156167b2de044989c733',
      'note':'Exact dedup uses stripped source text; normalize and near-duplicate audit must be completed before confirmatory runs.'}
    out.with_suffix(out.suffix+'.manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(manifest,indent=2))
if __name__=='__main__': main()
