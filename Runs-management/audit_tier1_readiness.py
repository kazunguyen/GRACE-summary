"""Read-only artifact audit; writes only this audit's JSON/Markdown summaries."""
import hashlib,json,statistics,subprocess
from collections import Counter
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]; BASE=ROOT/'01_Author_Baseline_Unified'
OUT=Path(__file__).parent
FOLDERS={'B0':'02_Arm_B0_Source_Only','B1':'03_Arm_B1_Graph_Only','B2-flip':'04_Arm_B2_Flip','B2-rep':'05_Arm_B2_Rep'}
REF=BASE/'output/local_full/bundles_recovered_joern_final_20261031'
FREEZE=BASE/'output/research_freeze_20261101'
RUNS=[(d,s) for d in ('devign','reveal') for s in ('validation','test')]
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def rows(p):
    with p.open(encoding='utf-8') as f:
        for line in f:
            if line.strip():yield json.loads(line)
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def stats(v):
    if not v:return None
    return {'p50':statistics.median(v),'p95':sorted(v)[int((len(v)-1)*.95)],'max':max(v)}
def small_files():
    names=('thresholds.json','preregistration.md','CHANGES_AFTER_PREREG.md','audit_summary.json','manual_sample.jsonl')
    found=[]
    for folder in [BASE/'diagnostic_kit',ROOT/'Runs-management']+[ROOT/f for f in FOLDERS.values()]:
        for name in names:
            found.extend(str(p.relative_to(ROOT)) for p in folder.rglob(name) if 'offline_test' not in str(p))
    return sorted(set(found))

protocol=yaml.safe_load((BASE/'diagnostic_kit/configs/protocol.yaml').read_text(encoding='utf-8'))
summary={'scope':'Steps 1-4 and Tier1 state; self-host requirement replaced by Kaggle GPU; Step0 excluded',
         'protocol_registered_at':protocol['registered_at'],'tags':subprocess.check_output(['git','tag','--list'],cwd=ROOT,text=True).splitlines(),
         'special_files':small_files(),'freeze_manifest_matches_protocol':sha(FREEZE/'freeze_manifest.json')==protocol['dedup']['manifest_sha256'],
         'prompt_sets':[],'inference_sets':[],'notebooks':[]}
freeze_manifest=load(FREEZE/'freeze_manifest.json')
summary['frozen_file_checks']=[]
for d,ds in freeze_manifest['datasets'].items():
    for name,expected in ds['files_sha256'].items():
        p=FREEZE/d/name
        summary['frozen_file_checks'].append({'path':str(p.relative_to(ROOT)),'matches':sha(p)==expected})
    print('Frozen files hash checked:',d,flush=True)
baseline={};frozen_ids={};eligible={}
for d in ('devign','reveal'):
    eligible[d]={r['id'] for r in rows(FREEZE/d/'train_manifest.jsonl') if r['keep_in_bank']}
for d,s in RUNS:
    raw={r['id']:r for r in rows(FREEZE/d/f'{s}_raw.jsonl')};frozen_ids[d,s]=set(raw)
    folder=REF/d/s;m=load(folder/'bundle_manifest.json')
    refs={r['id']:r for r in rows(folder/'prompts.jsonl')};baseline[d,s]=refs
    outside=[];changed_code=[];wrong_label=[]
    for sp in rows(folder/'specs.jsonl'):
        uid=sp['id'];demo=sp['demonstrations'][0]
        if demo['function_uid'] not in eligible[d]:outside.append({'target_id':uid,'demo_id':demo['function_uid']})
        if sp['query_code'].strip()!=raw[uid]['func'].strip():changed_code.append(uid)
        if sp['label']!=raw[uid]['target']:wrong_label.append(uid)
    counts=Counter(); totals=[];graphs=[];codes=[];demos=[]
    for r in refs.values():
        t=r['tokens'];totals.append(t['prompt_tokens']);graphs.append(t['graph_tokens_used']);codes.append(t['target_tokens_used']);demos.append(t['demo_tokens_used'])
        counts['target_truncated']+=bool(t.get('target_truncated'));counts['demo_truncated']+=bool(t.get('demo_truncated'))
        counts['empty_demo']+=t.get('demo_tokens_used',0)==0
        counts['missing_graph']+=bool(r.get('graph_missing'))
        counts['graph_cap_violation']+=t.get('graph_nodes_used',0)>40 or t.get('graph_edges_used',0)>80
        counts['budget_violation']+=t['prompt_tokens']+64>8192 or t['graph_tokens_used']>1500 or t['target_tokens_used']>3000 or t['demo_tokens_used']>1500
    summary['prompt_sets'].append({'arm':'B2','dataset':d,'split':s,'count':len(refs),'complete':set(refs)==set(raw),
        'source_hash_valid':sha(folder/'prompts.jsonl')==m['prompts_sha256'] and sha(folder/'specs.jsonl')==m['spec_sha256'],
        'outside_frozen_bank_count':len(outside),'outside_frozen_bank_examples':outside[:10],
        'target_code_diff_from_frozen':changed_code,'label_diff_from_frozen':wrong_label,'flags':dict(counts),
        'tokens_total':stats(totals),'tokens_code':stats(codes),'tokens_graph':stats(graphs),'tokens_demo':stats(demos)})
    print('B2',d,s,len(refs),'outside frozen bank',len(outside),flush=True)

DEMO_EMPTY='The following is an example, and it is .\n'
ANSWER='Answer (0 or 1):'
NODE='The node information of the code snippet is as follows:'
EDGE='The edge information of the code snippet is as follows:'
for arm,folder_name in FOLDERS.items():
    for d,s in RUNS:
        folder=ROOT/folder_name/'output/bundles'/d/s; p=folder/'prompts.jsonl';mp=folder/'bundle_manifest.json'
        entry={'arm':arm,'dataset':d,'split':s,'path':str(folder.relative_to(ROOT)),'exists':p.exists(),'manifest_exists':mp.exists()}
        if p.exists():
            initial=p.stat()
            try: rr=list(rows(p))
            except json.JSONDecodeError:
                entry['read_error']='Incomplete JSONL line; may be an active write'
                summary['prompt_sets'].append(entry)
                continue
            stable=p.stat().st_size==initial.st_size and p.stat().st_mtime_ns==initial.st_mtime_ns
            ids=[r['id'] for r in rr];flags=Counter();totals=[]
            for r in rr:
                uid=r['id'];ref=baseline[d,s].get(uid)
                flags['bad_prompt_hash']+=hashlib.sha256(r['prompt'].encode()).hexdigest()!=r['prompt_sha256']
                if not ref:flags['unknown_id']+=1;continue
                flags['wrong_label']+=r['label']!=ref['label']
                if arm=='B2-rep':flags['pairing_mismatch']+=r['prompt']!=ref['prompt'] or r['demo_ids']!=ref['demo_ids']
                if arm=='B2-flip':
                    old=ref['prompt'];new=r['prompt'];matches=False
                    for a,b in [('Vulnerable','Non-vulnerable'),('Non-vulnerable','Vulnerable')]:
                        needle=f'The following is an example, and it is {a}.\n'; replacement=f'The following is an example, and it is {b}.\n'
                        pos=old.find(needle)
                        while pos>=0:
                            if old[:pos]+replacement+old[pos+len(needle):]==new:matches=True;break
                            pos=old.find(needle,pos+1)
                    flags['pairing_mismatch']+=not matches or r['demo_ids']!=ref['demo_ids']
                if arm in ('B0','B1'):
                    flags['unexpected_demo_id']+=bool(r['demo_ids'])
                    tail='\n\n'+DEMO_EMPTY+'\n\n'+ANSWER
                    flags['scaffold_mismatch']+=not r['prompt'].endswith(tail)
                    if r['prompt'].endswith(tail):
                        prefix=r['prompt'][:-len(tail)]
                        empty_graph=f'{NODE}\n\n{EDGE}\n'
                        if arm=='B0' or r.get('graph_missing'):
                            suffix='\n\n'+empty_graph
                            flags['empty_graph_scaffold_mismatch']+=not prefix.endswith(suffix)
                            if prefix.endswith(suffix):prefix=prefix[:-len(suffix)]
                        flags['target_or_graph_prefix_mismatch']+=not ref['prompt'].startswith(prefix+'\n\n')
                t=r['tokens'];total=t.get('total',t.get('prompt_tokens'));totals.append(total)
                flags['budget_violation']+=total+64>8192
                flags['missing_graph']+=bool(r.get('graph_missing'))
                trunc=r.get('truncated',{})
                flags['target_truncated']+=bool(trunc.get('code',t.get('target_truncated',False)))
                flags['demo_truncated']+=bool(trunc.get('demo',t.get('demo_truncated',False)))
            entry.update(count=len(rr),stable=stable,complete=set(ids)==frozen_ids[d,s] and len(ids)==len(set(ids)),flags=dict(flags),tokens_total=stats(totals))
            if mp.exists():
                m=load(mp);entry['manifest_count']=m['count'];entry['manifest_prompt_hash_matches']=sha(p)==m['prompts_sha256']
                entry['retrieval_scope']=m.get('retrieval_scope');entry['outside_frozen_bank_count']=m.get('reference_demos_outside_new_frozen_bank')
            print(arm,d,s,entry['count'],'complete',entry['complete'],flush=True)
        summary['prompt_sets'].append(entry)

# Inspect ignored artifact directories too; never treat synthetic unit-test output as real inference.
roots=[BASE/'kaggle_qwen_q4_b2']+[ROOT/f for f in FOLDERS.values()]
for root in roots:
    for p in root.rglob('records.jsonl'):
        if any(x in str(p) for x in ('offline_test','pytest','test_prepare','threshold_pipeline_tests')):continue
        rr=list(rows(p)); mp=p.parent/'run_manifest.json';m=load(mp) if mp.exists() else {}
        counts=Counter();dates=[];models=set();seeds=set();fields=set()
        for r in rr:
            fields.update(r);models.add(r.get('model_sha256'));seeds.add(r.get('seed'));dates.append(r.get('timestamp',''))
            d=r.get('dataset');s=r.get('split');ref=baseline.get((d,s),{}).get(r['id'])
            counts['score_valid']+=bool(r.get('valid'));counts['response_valid']+=bool(r.get('response_valid'))
            counts['matches_current_B2_prompt']+=ref is not None and r.get('prompt_sha256')==ref['prompt_sha256']
        summary['inference_sets'].append({'path':str(p.relative_to(ROOT)),'records_sha256':sha(p),'count':len(rr),'unique_ids':len({r['id'] for r in rr}),
            'manifest':m,'counts':dict(counts),'model_hashes':sorted(str(x) for x in models),'seeds':sorted(str(x) for x in seeds),
            'earliest_timestamp':min(dates) if dates else None,'latest_timestamp':max(dates) if dates else None,
            'missing_schema_B2_fields':sorted({'id','dataset','split','arm','seed','prompt_sha256','demo_ids','s','pred_argmax','valid','label','model','backend_kind','timestamp'}-fields)})
for folder in [BASE]+[ROOT/f for f in FOLDERS.values()]:
    for p in (folder/'notebooks').glob('*.ipynb'):
        n=load(p);texts=[''.join(c.get('source',[])) for c in n['cells'] if c['cell_type']=='code'];code='\n'.join(texts)
        if 'kaggle' in p.name:
            summary['notebooks'].append({'path':str(p.relative_to(ROOT)),'saved_executed_cells':sum(c.get('execution_count') is not None for c in n['cells'] if c['cell_type']=='code'),
                'mentions_thresholds_json':'thresholds.json' in code,'contains_test_runs':"'test'" in code,
                'mentions_prereg_gate':'preregistration' in code or 'registered_at' in code})
summary['status']='Audit complete; absence means not found locally, not proof about external Kaggle/OSF state.'
(OUT/'KIEM_TOAN_DIEU_KIEN_TANG_1.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print('Audit JSON written',flush=True)
