"""Freeze raw IDs/code, exact duplicate groups, exact token-3gram near flags and CPG donors.
No prompts or embeddings are generated. Output is immutable: refuses an existing directory.
"""
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'output/research_freeze_20261101'
TOKEN = re.compile(r'R"(?P<delim>[^ ()\\\t\r\n]{0,16})\(.*?\)(?P=delim)"|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|//[^\n]*|/\*.*?\*/|[A-Za-z_][A-Za-z_0-9]*|\d+(?:\.\d+)?|[^\s]', re.S)

def tokens(code):
    # Preserve string/character literals (including whitespace and comment-like text).
    return [m.group() for m in TOKEN.finditer(code) if not m.group().startswith(('//', '/*'))]

def digest(data):
    return hashlib.sha256(data).hexdigest()

def filehash(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''): h.update(chunk)
    return h.hexdigest()

def rows(path):
    with path.open(encoding='utf-8') as f:
        for line in f:
            if line.strip(): yield json.loads(line)

def write(path, data):
    with path.open('w',encoding='utf-8',newline='\n') as f:
        for r in data: f.write(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n')

def freeze(dataset):
    folder=OUT/dataset; folder.mkdir()
    paths={s:ROOT/f'output/local_full/{dataset}/raw/{s}.jsonl' for s in ('train','validation','test')}
    data={s:list(rows(p)) for s,p in paths.items()}
    allrows=[r for rr in data.values() for r in rr]
    assert len({r['id'] for r in allrows})==len(allrows)
    sets={}; hashes={}
    for r in allrows:
        assert r['target'] in (0,1)
        t=tokens(r['func']); hashes[r['id']]=digest(json.dumps(t,ensure_ascii=False,separators=(',',':')).encode())
        # Short functions use their complete token sequence as one shingle.
        sets[r['id']]={tuple(t[i:i+3]) for i in range(len(t)-2)} if len(t)>=3 else {tuple(t)}
    train_groups=defaultdict(list)
    for r in data['train']: train_groups[hashes[r['id']]].append(r)
    evalrows=data['validation']+data['test']; evalhash={hashes[r['id']] for r in evalrows}
    keep=set(); reasons={}
    for h,group in train_groups.items():
        conflict=len({r['target'] for r in group})>1
        for i,r in enumerate(sorted(group,key=lambda r:r['id'])):
            reason='overlap_eval_exact' if h in evalhash else 'label_conflict' if conflict else 'duplicate_train' if i else None
            reasons[r['id']]=reason
            if reason is None: keep.add(r['id'])
    # Exact Jaccard join via globally ordered prefixes: any pair >=.9 must share a prefix item.
    freq=Counter(x for ss in sets.values() for x in ss)
    order={x:i for i,x in enumerate(sorted(freq,key=lambda x:(freq[x],x)))}
    index=defaultdict(set)
    for r in data['train']:
        ss=sets[r['id']]; prefix=sorted(ss,key=order.__getitem__)[:len(ss)-(9*len(ss)+9)//10+1]
        for x in prefix: index[x].add(r['id'])
    near_train=set(); near_eval=set(); pairs=[]
    for j,r in enumerate(evalrows):
        ss=sets[r['id']]; prefix=sorted(ss,key=order.__getitem__)[:len(ss)-(9*len(ss)+9)//10+1]
        cand=set().union(*(index[x] for x in prefix))
        for tid in sorted(cand):
            ts=sets[tid]
            if 10*min(len(ts),len(ss))<9*max(len(ts),len(ss)): continue
            inter=len(ts & ss); union=len(ts)+len(ss)-inter
            if 10*inter>=9*union:
                near_train.add(tid); near_eval.add(r['id'])
                pairs.append({'train_id':tid,'eval_id':r['id'],'eval_split':r['split'],'jaccard':inter/union,'exact':hashes[tid]==hashes[r['id']],'retained_donor':tid in keep})
        if j%1000==0: print(dataset,'near',j,len(pairs),flush=True)
    stats={'dataset':dataset,'normalization':'C/C++ lexical tokens; comments/format whitespace removed; literals preserved; token list SHA256',
           'near_method':'exact token-3gram set Jaccard >= 0.9; complete prefix join; short code uses whole token sequence',
           'near_policy':'flag only; eval flags compare with original train, including removed donors',
           'per_split':{},'bank_removals':dict(Counter(v for v in reasons.values() if v)), 'donor_count':len(keep)}
    for split,rr in data.items():
        manifest=[]
        for r in rr:
            manifest.append({'id':r['id'],'label':r['target'],'code_sha256':digest(r['func'].encode()),'norm_sha256':hashes[r['id']],
                             'near_train' if split!='train' else 'near_eval':r['id'] in (near_eval if split!='train' else near_train),
                             'exact_train':hashes[r['id']] in train_groups if split!='train' else None,
                             'keep_in_bank':r['id'] in keep if split=='train' else None,'removal_reason':reasons.get(r['id']),
                             'commit_id':r.get('commit_id'),'project':r.get('project')})
        write(folder/f'{split}_manifest.jsonl',manifest)
        write(folder/f'{split}_raw.jsonl',rr)
        stats['per_split'][split]={'n':len(rr),'positive':sum(r['target'] for r in rr),'negative':sum(1-r['target'] for r in rr),
                                 'near_flags':sum(r['id'] in (near_train if split=='train' else near_eval) for r in rr),
                                 'exact_overlap':sum(hashes[r['id']] in (evalhash if split=='train' else train_groups) for r in rr)}
    write(folder/'near_pairs.jsonl',pairs)
    cpg=ROOT/f'output/local_full/cpg_recovered_joern_final_20261031/{dataset}/cpg/train.jsonl'
    originals={r['id']:r for r in data['train']}; seen=set(); missing=0
    def donors():
        nonlocal missing
        for g in rows(cpg):
            uid=g['id']
            if uid not in keep: continue
            assert uid not in seen; seen.add(uid)
            r=originals[uid]
            if 'func' in g: assert r['func']==g['func']
            missing+=not bool(g.get('nodes'))
            yield {'function_uid':uid,'func':r['func'],'target':r['target'],'nodes':g.get('nodes') or [],'edges':g.get('edges') or []}
    write(folder/'donors.jsonl',donors())
    assert seen==keep, (len(seen),len(keep))
    stats['donor_missing_graphs']=missing
    stats['donor_positive']=sum(originals[x]['target'] for x in keep)
    stats['input_sha256']={s:filehash(p) for s,p in paths.items()}; stats['cpg_train_sha256']=filehash(cpg)
    stats['files_sha256']={p.name:filehash(p) for p in sorted(folder.glob('*.jsonl'))}
    (folder/'stats.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf-8')
    print(dataset,'DONE',stats['donor_count'],stats['bank_removals'],flush=True)
    return stats

if __name__=='__main__':
    OUT.mkdir(exist_ok=False)
    summary={d:freeze(d) for d in ('devign','reveal')}
    (OUT/'freeze_manifest.json').write_text(json.dumps({'created_local_date':'2026-11-01','script_sha256':filehash(Path(__file__)), 'datasets':summary},ensure_ascii=False,indent=2),encoding='utf-8')
