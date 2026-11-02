"""CPU-only full-validation dry-run, with project variants and immutable inputs.

No inference backend is imported. Frozen donor graphs are indexed/lazily loaded to
avoid materializing multi-gigabyte JSONL banks in memory. H2/B3 stay blocked without inputs.
"""
import argparse
import csv
import hashlib
import json
import math
import sys
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'01_Author_Baseline_Unified/diagnostic_kit/src'))
sys.path.insert(0,str(ROOT/'tier1_prompt_tools'))
import grace_diag.probes as probes
from grace_diag.probes import ROLE,QUESTION,NODE_HEAD,EDGE_HEAD,ANSWER,DonorPool,stable_seed,closed_prefix,format_nodes,format_edges
from grace_diag.token_budget import TokenCounter
from grace_diag.prompt_audit import audit_rows
from prepare_cached import render_paired
from audit_prompt_integrity import split_prompt,leak_classification
from finalize_prompt_audit import known_cpp_ternary,known_channel_diagnostic,known_source_domain_label

REV='b2cff646eb4bb1d68355c01b18ae02e7cf42d120'
FROZEN_SHA='e1d3c6b17c3a0b5c1e05203794d48a33825e0ea00a55deaaef565af25efe0448'
BASE=ROOT/'01_Author_Baseline_Unified'
OLD=BASE/'output/local_full/bundles_recovered_joern_final_20261031'
REF=ROOT/'Runs-management/donor_reconciliation_20261101/new_reference/B2'
FREEZE=BASE/'output/research_freeze_20261101'
BUDGET={'total':8192,'target_code':3000,'graph':1500,'demo':1500,'reserve':64}
PREFIX={'nodes':40,'edges':80}
ARMS=list(probes.ARMS)
AVAILABLE=['B0','B1','B1-full','B1-shuf','B2','B2-rand','B2-nolabel','B2-labelonly','B2-flip','B2-rep']
BLOCKED={'B1-H2':['h2_evidence','h2_source_limits'],
         'B3':['demonstrations_pair','security_difference'],
         'B3-nodiff':['demonstrations_pair'],
         'B3-swap':['demonstrations_pair','security_difference'],
         'B3-flip':['demonstrations_pair','security_difference']}
ORIGINAL_GRAPH=probes.render_graph


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(4*1024*1024),b''):h.update(block)
    return h.hexdigest()


def digest(text):return hashlib.sha256(text.encode('utf-8')).hexdigest()


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))


def rows(path):
    with Path(path).open(encoding='utf-8',buffering=4*1024*1024) as f:
        for line in f:
            if line.strip():yield json.loads(line)


def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')


class ExactCounter(TokenCounter):
    def __init__(self):
        super().__init__(None)
        from transformers import AutoTokenizer
        self.tok=AutoTokenizer.from_pretrained('Qwen/Qwen3-Coder-30B-A3B-Instruct',revision=REV,
                                              local_files_only=True,trust_remote_code=False)
        self.approx=False;self.memo={};self.chat_memo={}
    def count(self,text):
        k=digest(text);v=self.memo.get(k)
        if v is None:
            # Same backend as tokenizer.encode(add_special_tokens=False), without per-call configuration changes.
            v=len(self.tok.backend_tokenizer.encode(text,add_special_tokens=False).ids)
            if len(self.memo)>200000:self.memo.clear()
            self.memo[k]=v
        return v
    def count_chat(self,prompt,system=None):
        k=digest((system or '')+'\0'+prompt);v=self.chat_memo.get(k)
        if v is None:
            v=super().count_chat(prompt,system)
            self.chat_memo[k]=v
        return v


def compact_graph(nodes,edges):
    normalized=[]
    for e in edges:
        a=e.get('start',e.get('source',e.get('src')));b=e.get('end',e.get('target',e.get('dst')))
        if a is None or b is None:raise ValueError('Graph edge endpoint missing')
        normalized.append(dict(e,start=a,end=b,type=e.get('type',e.get('label','CONNECTED_TO'))))
    n,k=closed_prefix(nodes,normalized,40,80)
    compact=[]
    for i,node in enumerate(n):
        text=str(node.get('code','')).strip().replace('\n',' ')
        if len(text)>40:text=text[:40]+'...'
        compact.append({'id':node.get('id',i),'type':node.get('type',node.get('label','Node')),'code':text})
    assert format_nodes(compact)==format_nodes(n)
    assert format_edges(k)==format_edges(closed_prefix(nodes,normalized,40,80)[1])
    return compact,k


class LazyDonors(DonorPool):
    def __init__(self,dataset,out,source_hashes):
        self.path=FREEZE/dataset/'donors.jsonl';self.index={};self.dataset=dataset
        frozen=read(FREEZE/'freeze_manifest.json')['datasets'][dataset]
        cache=ROOT/f'Runs-management/donor_reconciliation_20261101/cache/{dataset}_new_bank.jsonl'
        proof=read(cache.parent.parent/f'{dataset}_retrieval_provenance.json')
        if sha(cache)!=proof['new']['cache_sha256']:raise ValueError('Frozen compact cache hash mismatch')
        bank=list(rows(cache));by_id={r['id']:r for r in bank}
        tm=FREEZE/dataset/'train_manifest.jsonl'
        if sha(tm)!=frozen['files_sha256']['train_manifest.jsonl']:raise ValueError('Train manifest hash mismatch')
        eligible={r['id']:r for r in rows(tm) if r['keep_in_bank']}
        h=hashlib.sha256();ordered=[];node_counts=[];offset=0
        print(dataset,'index donor CPG stream',flush=True)
        with self.path.open('rb',buffering=8*1024*1024) as stream:
            for line in stream:
                h.update(line)
                if not line.strip():offset+=len(line);continue
                r=json.loads(line);uid=r['function_uid'];n=len(r.get('nodes') or [])
                if uid in self.index or uid not in eligible:raise ValueError('Frozen donor ID mismatch')
                if r['target']!=eligible[uid]['label'] or digest(r['func'].strip())!=eligible[uid]['code_sha256']:
                    raise ValueError('Frozen donor code/label mismatch')
                if by_id[uid]['target']!=r['target'] or by_id[uid]['func']!=r['func'].strip():raise ValueError('Donor cache disagrees')
                self.index[uid]=(offset,len(line),n,len(r.get('edges') or []))
                ordered.append(uid);node_counts.append(n);offset+=len(line)
                if len(ordered)%2000==0:print(dataset,'indexed',len(ordered),'/',frozen['donor_count'],flush=True)
        if h.hexdigest()!=frozen['files_sha256']['donors.jsonl']:raise ValueError('Frozen donor source hash mismatch')
        if ordered!=[r['id'] for r in bank] or set(ordered)!=set(eligible):raise ValueError('Frozen donor order mismatch')
        self.rows=[{'function_uid':r['id'],'func':r['func'],'target':r['target'],'n_nodes':n} for r,n in zip(bank,node_counts)]
        self.n_nodes=np.asarray(node_counts,dtype=int)
        self.by_id={r['function_uid']:r for r in self.rows}
        self.stream=self.path.open('rb',buffering=4*1024*1024)
        with (out/f'{dataset}_donor_graph_index.csv').open('w',encoding='utf-8',newline='') as f:
            w=csv.writer(f);w.writerow(['id','offset_bytes','length_bytes','nodes','edges'])
            for uid,data in self.index.items():w.writerow([uid,*data])
        source_hashes[str(self.path.relative_to(ROOT))]=h.hexdigest()
        source_hashes[str(cache.relative_to(ROOT))]=sha(cache)
        source_hashes[str(tm.relative_to(ROOT))]=sha(tm)
    def selected_graph(self,uid,seed,n):
        rng=np.random.default_rng(stable_seed(uid,seed)^0x5F3759DF);width=.1
        while True:
            lo,hi=int(np.floor(n*(1-width))),int(np.ceil(n*(1+width)))
            candidates=np.flatnonzero((self.n_nodes>=max(lo,1))&(self.n_nodes<=max(hi,1)))
            candidates=[int(i) for i in candidates if self.n_nodes[i]>0 and self.rows[i]['function_uid']!=uid]
            if candidates or width>2:break
            width*=2
        if not candidates:raise ValueError('No donor graph for '+uid)
        row=self.rows[int(rng.choice(candidates))]
        return row['function_uid'],{'donor_uid':row['function_uid'],'donor_nodes':row['n_nodes'],'tolerance_used':width}
    def graph(self,uid):
        offset,length,n,k=self.index[uid];self.stream.seek(offset)
        row=json.loads(self.stream.read(length))
        if row['function_uid']!=uid:raise ValueError('Donor index seek mismatch')
        nodes,edges=compact_graph(row.get('nodes') or [],row.get('edges') or [])
        return nodes,edges,n,k
    def close(self):self.stream.close()


def prepare_specs(dataset,counter,pool,source_hashes):
    p=OLD/dataset/'validation';old={r['id']:r for r in rows(p/'prompts.jsonl')}
    new={r['id']:r for r in rows(REF/dataset/'validation/prompts.jsonl')}
    raw_path=FREEZE/dataset/'validation_raw.jsonl';raw={r['id']:r for r in rows(raw_path)}
    for f in [p/'specs.jsonl',p/'prompts.jsonl',REF/dataset/'validation/prompts.jsonl',raw_path]:
        source_hashes[str(f.relative_to(ROOT))]=sha(f)
    if sha(raw_path)!=read(FREEZE/'freeze_manifest.json')['datasets'][dataset]['files_sha256']['validation_raw.jsonl']:raise ValueError('Frozen validation raw hash mismatch')
    bm=read(p/'bundle_manifest.json');nm=read(REF/dataset/'validation/manifest.json')
    if sha(p/'specs.jsonl')!=bm['spec_sha256'] or sha(p/'prompts.jsonl')!=bm['prompts_sha256'] or sha(REF/dataset/'validation/prompts.jsonl')!=nm['prompts_sha256']:
        raise ValueError('Reference manifest mismatch')
    if set(old)!=set(new) or set(old)!=set(raw):raise ValueError('Reference target ID mismatch')
    specs=[];prefix_cache={};missing=Counter();parity=[]
    for original in rows(p/'specs.jsonl'):
        uid=original['id'];reference=old[uid]
        if original['label']!=raw[uid]['target'] or original['query_code'].strip()!=raw[uid]['func'].strip():raise ValueError('Frozen validation target mismatch')
        verified,ev=render_paired('B2-rep',original,reference['prompt'],counter,reference=reference)
        if verified!=reference['prompt']:raise ValueError('Cached B2 reconstruction mismatch')
        text=split_prompt(reference['prompt'])['graph']
        if len(parity)<20:
            expected,info=ORIGINAL_GRAPH('prefix',original,counter,1500,PREFIX,42,None)
            if expected!=text:raise ValueError('Cached/original graph renderer mismatch')
            parity.append(uid)
        prefix_cache[uid]=(text,dict(ev['graph'],cached_verified_B2_prefix=True))
        for key in ('h2_evidence','h2_source_limits','demonstrations_pair','security_difference'):
            missing[key]+=not bool(original.get(key))
        nodes,edges=compact_graph(original.get('nodes') or [],original.get('edges') or [])
        donor=pool.by_id[new[uid]['demo_ids'][0]]
        spec={'id':uid,'query_code':original['query_code'],'nodes':nodes,'edges':edges,
              'source_node_count':len(original.get('nodes') or []),'source_edge_count':len(original.get('edges') or []),
              'demonstrations':[dict(donor)],'demonstrations_pair':original.get('demonstrations_pair') or [],
              'security_difference':original.get('security_difference') or ''}
        specs.append(spec)
        if len(specs)%500==0:print(dataset,'verified validation specs',len(specs),'/',len(raw),flush=True)
    if len(specs)!=len(raw) or {r['id'] for r in specs}!=set(raw):raise ValueError('Full validation specs incomplete/duplicate')
    return specs,old,new,prefix_cache,dict(missing),parity


SHUFFLE_COUNTER=None

def fit_shuffle_graph(item):
    uid,nodes,edges,n,k=item
    text,info=ORIGINAL_GRAPH('prefix',{'nodes':nodes,'edges':edges},SHUFFLE_COUNTER,1500,PREFIX,42,None)
    info.update(available_nodes=n,available_edges=k)
    return uid,(text,info)


def prepare_shuffle_graphs(specs,pool,counter,threads):
    selections={};unique=set()
    for spec in specs:
        for seed in (42,43,44):
            if not spec['source_node_count']:continue
            uid,info=pool.selected_graph(spec['id'],seed,spec['source_node_count'])
            selections[spec['id'],seed]=(uid,info);unique.add(uid)
    cache={}
    # Tokenizers' single-string encode holds the Python GIL. Separate processes
    # keep the unchanged renderer exact while allowing real CPU concurrency.
    # Fork after serial tokenization; Rayon is disabled by the offline command.
    global SHUFFLE_COUNTER
    SHUFFLE_COUNTER=counter
    with ProcessPoolExecutor(max_workers=threads,mp_context=multiprocessing.get_context('fork')) as executor:
        pending=[]
        for uid in sorted(unique):
            nodes,edges,n,k=pool.graph(uid)
            pending.append(executor.submit(fit_shuffle_graph,(uid,nodes,edges,n,k)))
            if len(pending)>=64:
                for future in as_completed(pending):
                    key,value=future.result();cache[key]=value
                pending=[]
                if len(cache)%256<64:print(pool.dataset,'fitted unique shuffled graphs',len(cache),'/',len(unique),flush=True)
        for future in as_completed(pending):
            key,value=future.result();cache[key]=value
    return selections,cache


def project_renderer(prefix_cache,selections,shuffle_cache,missing_policy):
    def graph(policy,spec,counter,budget,prefix,seed,donors):
        if policy=='prefix':return prefix_cache[spec['id']]
        if policy=='shuffle':
            if not spec['source_node_count']:
                if missing_policy!='empty':raise ValueError('Missing target graph, cannot size-match donor')
                return '',{'policy':'shuffle','missing':True,'rendered_nodes':0,'rendered_edges':0,'tokens':0,
                           'source_node_count':0,'missing_policy':'user_confirmed_keep_empty'}
            uid,selection=selections[spec['id'],seed];text,info=shuffle_cache[uid]
            return text,dict(info,policy='shuffle',**selection)
        text,info=ORIGINAL_GRAPH(policy,spec,counter,budget,prefix,seed,donors)
        info.update(available_nodes=spec.get('source_node_count',info.get('available_nodes',0)),
                    available_edges=spec.get('source_edge_count',info.get('available_edges',0)))
        return text,info
    return graph


def render_project(spec,arm,seed,counter,pool):
    if any(k in spec for k in ('label','target','ground_truth','target_label')):raise ValueError('Target label entered renderer')
    rendered=probes.render_arm(spec,arm,seed,counter,pool,BUDGET,PREFIX)
    if arm in ('B0','B1','B1-full','B1-shuf'):
        blocks=probes.split_blocks(rendered.prompt)
        graph=blocks['graph'] or f'{NODE_HEAD}\n\n{EDGE_HEAD}\n'
        prompt='\n\n'.join([ROLE,blocks['code'],QUESTION,graph,'The following is an example, and it is .\n',ANSWER])
        rendered.prompt=prompt;rendered.evidence['tokens']['total']=counter.count_chat(prompt)
        rendered.evidence['prompt_sha256']=digest(prompt)
        rendered.evidence['demo']['policy']='none'
    if rendered.evidence['tokens']['total']+64>8192:raise ValueError('Project scaffold context overflow')
    return rendered


def resolve_hits(prompt):
    hits=leak_classification(prompt);open_hits=[]
    for h in hits:
        if h['classification']=='cpp_member_label' or known_cpp_ternary(h) or known_channel_diagnostic(h) or known_source_domain_label(h):continue
        open_hits.append(h)
    return hits,open_hits


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out',type=Path,default=ROOT/'Runs-management/dry_run_validation_20261102')
    ap.add_argument('--threads',type=int,default=4)
    ap.add_argument('--missing-target-graph',required=True,choices=['empty','blocked'])
    args=ap.parse_args();out=args.out.resolve()
    if not out.is_relative_to(ROOT/'Runs-management') or out.exists():raise SystemExit('Use a new output directory under Runs-management')
    out.mkdir(parents=True)
    if sha(FREEZE/'freeze_manifest.json')!=FROZEN_SHA:raise ValueError('Frozen snapshot changed')
    protected=[ROOT/'Runs-management/thresholds.json',ROOT/'Runs-management/threshold_lock_status.json']
    protected+=list((ROOT/'Runs-management/analysis_lock_20261101').glob('*'))
    protected={str(p.relative_to(ROOT)):sha(p) for p in protected if p.is_file()}
    source_hashes={str(Path(__file__).relative_to(ROOT)):sha(__file__),
                   str((BASE/'diagnostic_kit/src/grace_diag/probes.py').relative_to(ROOT)):sha(BASE/'diagnostic_kit/src/grace_diag/probes.py'),
                   str((FREEZE/'freeze_manifest.json').relative_to(ROOT)):FROZEN_SHA}
    import yaml
    protocol_path=BASE/'diagnostic_kit/configs/protocol.yaml'
    protocol=yaml.safe_load(protocol_path.read_text(encoding='utf-8'))
    if protocol['token_budget']!=BUDGET or protocol['graph_prefix']!=PREFIX:raise ValueError('Project budget/prefix differs; review before dry-run')
    source_hashes[str(protocol_path.relative_to(ROOT))]=sha(protocol_path)
    for source in [ROOT/'tier1_prompt_tools/prepare_cached.py',ROOT/'Runs-management/audit_prompt_integrity.py',ROOT/'Runs-management/finalize_prompt_audit.py']:
        source_hashes[str(source.relative_to(ROOT))]=sha(source)
    counter=ExactCounter();summaries=[];blocked=[];errors=[];sample_pool=[];rendered_total=0
    print('Pinned tokenizer ready; no LLM backend imported',flush=True)
    for dataset in ('devign','reveal'):
      pool=LazyDonors(dataset,out,source_hashes)
      try:
        specs,old,new,prefix_cache,missing,parity=prepare_specs(dataset,counter,pool,source_hashes)
        expected=len(specs)
        for arm,required in BLOCKED.items():
            blocked.append({'dataset':dataset,'split':'validation','arm':arm,'seed':42,'expected':expected,
                            'status':'blocked_missing_inputs','missing_fields':{k:missing[k] for k in required},'llm_calls':0})
        selections,shuffle_cache=prepare_shuffle_graphs(specs,pool,counter,max(1,args.threads))
        probes.render_graph=project_renderer(prefix_cache,selections,shuffle_cache,args.missing_target_graph)
        for arm in AVAILABLE:
          for seed in ((42,43,44) if arm in ('B1-shuf','B2-rand') else (42,)):
            folder=out/dataset/'validation'/arm/str(seed);folder.mkdir(parents=True)
            data=[];counts=Counter();raw_flags=[];seen=set();same_B2=0;same_B1=0
            path=folder/'prompts.jsonl'
            with path.open('w',encoding='utf-8',newline='\n') as stream:
              for spec in specs:
                uid=spec['id']
                if arm=='B1-shuf' and not spec['source_node_count'] and args.missing_target_graph=='blocked':
                    errors.append({'arm':arm,'dataset':dataset,'seed':seed,'id':uid,'error':'missing_target_graph'});continue
                try:
                    result=render_project(spec,arm,seed,counter,pool)
                    ev=result.evidence
                    if ev['tokens']['approx']:raise ValueError('Approximate tokenizer forbidden')
                    if arm in ('B2','B2-rep') and result.prompt!=new[uid]['prompt']:raise ValueError('Frozen B2/rep exact pairing mismatch')
                    if arm=='B2-flip':
                        word='Vulnerable' if spec['demonstrations'][0]['target'] else 'Non-vulnerable'
                        swapped='Non-vulnerable' if word=='Vulnerable' else 'Vulnerable'
                        at=new[uid]['prompt'].rfind('The following is an example, and it is ')
                        expected_flip=new[uid]['prompt'][:at]+new[uid]['prompt'][at:].replace('The following is an example, and it is '+word+'.\n',
                                                              'The following is an example, and it is '+swapped+'.\n',1)
                        if result.prompt!=expected_flip:raise ValueError('Flip changed more than demo label')
                    if arm=='B1':
                        legacy=ROOT/f'03_Arm_B1_Graph_Only/output/bundles/{dataset}/validation/prompts.jsonl'
                        # Exact cache parity is verified once below via file lookup, not inferred from arm names.
                    row={'id':uid,'dataset':dataset,'split':'validation','arm':arm,'seed':seed,
                         'prompt_variant':'project_frozen_donor_dryrun_v1','prompt_sha256':ev['prompt_sha256'],'prompt':result.prompt,'evidence':ev}
                    stream.write(json.dumps(row,ensure_ascii=False)+'\n');data.append(row);seen.add(uid)
                    hits,open_hits=resolve_hits(result.prompt)
                    raw_flags.extend({'id':uid,**h} for h in hits);counts['unresolved_label_flags']+=bool(open_hits)
                    counts['source_label_fields_removed']+=1
                    same_B2+=result.prompt==new[uid]['prompt']
                    if arm in ('B1-full','B1-shuf'):
                        baseline=render_project(spec,'B1',42,counter,pool).prompt
                        same_B1+=result.prompt==baseline
                    if len(data)%250==0:print(dataset,arm,seed,len(data),'/',expected,flush=True)
                except Exception as exc:
                    errors.append({'arm':arm,'dataset':dataset,'seed':seed,'id':uid,'error':str(exc)})
            if arm in ('B0','B1'):
                root='02_Arm_B0_Source_Only' if arm=='B0' else '03_Arm_B1_Graph_Only'
                originals={r['id']:r for r in rows(ROOT/root/f'output/bundles/{dataset}/validation/prompts.jsonl')}
                if any(r['prompt']!=originals[r['id']]['prompt'] for r in data):raise ValueError('Existing project variant changed: '+arm)
            res=audit_rows(data) if data else {'summary':{},'rows':[]}
            kit=res['summary'].get(arm,{})
            initial_leaks=kit.get('n_label_leak',0)
            kit.update(dataset=dataset,split='validation',arm=arm,seed=seed,expected=expected,rendered=len(data),
                       raw_regex_flagged_prompts=initial_leaks,n_label_leak=counts['unresolved_label_flags'],
                       same_prompt_as_B2=same_B2,same_prompt_as_B1=same_B1,
                       prompts_sha256=sha(path),cached_prefix_parity_checked_ids=parity)
            faults=[e for e in errors if e['arm']==arm and e['dataset']==dataset and e['seed']==seed]
            kit['render_errors']=len(faults)
            kit['status']='pass' if len(data)==expected and not faults and not kit['n_label_leak'] and kit['rate_demo_empty']<=.01 and not kit['any_approx_tokens'] else 'needs_review'
            kit['llm_calls']=0
            write(folder/'audit_summary.json',kit);write(folder/'raw_label_flags.json',raw_flags)
            with (folder/'audit_rows.csv').open('w',encoding='utf-8-sig',newline='') as f:
                w=csv.DictWriter(f,fieldnames=list(res['rows'][0]) if res['rows'] else ['id']);w.writeheader();w.writerows(res['rows'])
            write(folder/'manifest.json',{'mode':'dry-run-only','arm':arm,'seed':seed,'dataset':dataset,'split':'validation',
                'count':len(data),'expected':expected,'tokenizer_revision':REV,'donor_snapshot_sha256':FROZEN_SHA,
                'graph_prefix':PREFIX,'budget':BUDGET,'prompt_variant':'project_frozen_donor_dryrun_v1',
                'preserves_empty_scaffold_B0_B1_family':True,'source_label_not_passed_to_renderer':True,
                'prompts_sha256':sha(path),'llm_calls':0})
            for r in data:
                sample_pool.append({'id':r['id'],'arm':arm,'phase':'full_validation_dryrun','seed':seed,'dataset':dataset,
                    'split':'validation','audit_key':f"{dataset}/{arm}/{seed}/{r['id']}",
                    'prompt_sha256':r['evidence']['prompt_sha256'],'prompt_source':str(path.relative_to(ROOT)),
                    'tokens_total':r['evidence']['tokens']['total'],
                    'code_truncated':r['evidence']['truncated']['code'],'graph_truncated':r['evidence']['truncated']['graph'],
                    'demo_truncated':r['evidence']['truncated']['demo']})
            summaries.append(kit);rendered_total+=len(data)
            print('COMPLETE',dataset,arm,seed,kit['status'],len(data),'/',expected,'demo_empty',kit.get('rate_demo_empty'),flush=True)
            del data,res
      finally:
        probes.render_graph=ORIGINAL_GRAPH;pool.close()
      del specs,prefix_cache,shuffle_cache,pool
    for rel,value in protected.items():
        if sha(ROOT/rel)!=value:raise ValueError('Protected historical file changed: '+rel)
    # Recheck source hashes after the complete dry-run, including the immutable large donor banks.
    for rel,value in source_hashes.items():
        if sha(ROOT/rel)!=value:raise ValueError('Input changed during dry-run: '+rel)
    from audit_prompt_integrity import make_manual
    manual_n=make_manual(out,sample_pool)
    write(out/'source_hashes.json',source_hashes);write(out/'blocked_arms.json',blocked);write(out/'render_errors.json',errors)
    report={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'mode':'full_validation_dry_run_no_inference',
        'rendered_prompt_rows':rendered_total,'sets':summaries,'blocked':blocked,'render_errors':errors,
        'available_arm_names':AVAILABLE,'blocked_arm_names':list(BLOCKED),'all_15_arms_complete':False,
        'missing_target_graph_policy':args.missing_target_graph,'manual_sample_count':manual_n,
        'manual_review_status':'pending_two_real_reviewers','step3_complete':False,'llm_calls':0,
        'new_thresholds_fitted':False,'historical_inputs_unchanged':True,'protected_hashes':protected}
    write(out/'summary.json',report)
    lines=['# Dry-run toàn validation — 02/11/2026','',
      f'Đã dựng {rendered_total:,} prompt trên đủ 2.732 Devign và 2.273 REVEAL validation cho các arm đủ dữ liệu. Không inference LLM, không tạo score, không fit tau.',
      'H2 và bốn arm B3 giữ trạng thái blocked vì thiếu evidence/cặp demo. Giữ target thiếu graph ở B1-shuf với graph trống và cờ missing theo xác nhận người dùng.',
      'Phiên donor frozen thống nhất. B0/B1 và các probe graph giữ scaffold demo trống; không thay prompt/output lịch sử. Prefix graph tái dùng cache đã kiểm hash và tái dựng chính xác; full/shuffle được dựng thật từ graph nguồn.', '',
      '| Dataset | Arm | Seed | Dựng/đủ | Demo rỗng | Graph thiếu | Cờ nhãn chưa giải quyết | Lỗi dựng | Trạng thái |',
      '|---|---|---:|---:|---:|---:|---:|---:|---|']
    for s in summaries:lines.append(f"| {s['dataset']} | {s['arm']} | {s['seed']} | {s['rendered']}/{s['expected']} | {s.get('rate_demo_empty',0):.3%} | {s.get('rate_graph_missing',0):.3%} | {s['n_label_leak']} | {s['render_errors']} | {s['status']} |")
    lines+=['','B1-full và B1-shuf có same_prompt_as_B1 trong summary; trùng do graph nhỏ/thiếu hoặc cùng trần 40/80 được báo, không coi đã tạo khác biệt khi prompt giống nhau.',
      '', '**Chưa hoàn thành toàn bộ Bước 3:** còn 5 arm blocked và hai người đọc mẫu chưa có kết quả. Lượt này là dry-run chuẩn bị cho tương lai, không thay audit trước inference của run lịch sử.',
      '', '[Summary](summary.json), [arm blocked](blocked_arms.json), [lỗi dựng](render_errors.json), [nguồn/hash](source_hashes.json), [60 mẫu chấm](manual_packet.md), [rubric](RUBRIC.md).','']
    (out/'KET_QUA.md').write_text('\n'.join(lines),encoding='utf-8',newline='\n')
    print('DONE',json.dumps({'rendered':rendered_total,'sets':len(summaries),'pass_sets':sum(s['status']=='pass' for s in summaries),
                            'blocked_arms':list(BLOCKED),'errors':len(errors),'manual':manual_n}),flush=True)


if __name__=='__main__':main()
