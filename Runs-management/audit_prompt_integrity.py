"""Post-run CPU audit. Never rewrites prompts, inference records, thresholds or sealed snapshots."""
import argparse
import csv
import hashlib
import json
import math
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KIT = ROOT/'01_Author_Baseline_Unified/diagnostic_kit/src'
sys.path.insert(0, str(KIT))
from grace_diag.prompt_audit import audit_rows, stratified_manual_sample, LEAK_PATTERNS
from grace_diag.probes import ROLE, QUESTION, NODE_HEAD, EDGE_HEAD, ANSWER, format_nodes, format_edges

REVISION = 'b2cff646eb4bb1d68355c01b18ae02e7cf42d120'
MODEL_SHA = 'f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335'
OLD = ROOT/'01_Author_Baseline_Unified/output/local_full/bundles_recovered_joern_final_20261031'
NEW = ROOT/'Runs-management/donor_reconciliation_20261101/new_reference/B2'
FREEZE = ROOT/'01_Author_Baseline_Unified/output/research_freeze_20261101'
MATRIX = ['B0','B1','B2','B2-flip','B2-rep','B2-rand','B2-nolabel','B2-labelonly','B1-shuf',
          'B1-full','B1-H2','B3','B3-nodiff','B3-swap','B3-flip']
SPLITS = [('devign','validation'),('devign','test'),('reveal','validation'),('reveal','test')]
SOURCES = {'B0':'02_Arm_B0_Source_Only/output/kaggle_20261101_duchuynguyen1802/grace_b0_runs',
           'B1':'03_Arm_B1_Graph_Only/output/kaggle_run_01/grace_b1_runs',
           'B2':'01_Author_Baseline_Unified/output/local_full/inference_qwen_q4_b2_20261101/grace_b2_four_split_8h',
           'B2-flip':'04_Arm_B2_Flip/output/kaggle_20261102_quangdung1111_run1/grace_b2_flip_four_split_9h35'}


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(4*1024*1024),b''): h.update(block)
    return h.hexdigest()


def digest(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def rows(path):
    with Path(path).open(encoding='utf-8',buffering=4*1024*1024) as stream:
        for line in stream:
            if line.strip(): yield json.loads(line)


def write_json(path, value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')


def csv_write(path, data, fields=None):
    data=list(data)
    with path.open('w',encoding='utf-8-sig',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=fields or (list(data[0]) if data else ['id']))
        writer.writeheader(); writer.writerows(data)


def split_prompt(prompt):
    start=ROLE+'\n\n'
    if not prompt.startswith(start) or not prompt.endswith('\n\n'+ANSWER):
        raise ValueError('Unexpected role/answer scaffold')
    q='\n\n'+QUESTION
    if prompt.count(q)!=1: raise ValueError('Ambiguous question boundary')
    code_end=prompt.index(q)
    content_start=code_end+len(q)
    heading='The following is an example, and it is '
    at=prompt.rfind(heading,content_start)
    if at<0: raise ValueError('Missing demonstration heading')
    rest=prompt[at:-len('\n\n'+ANSWER)]
    match=re.fullmatch(re.escape(heading)+r'(Vulnerable|Non-vulnerable|)\.\n(.*)',rest,re.S)
    if not match: raise ValueError('Unexpected demo scaffold')
    graph=prompt[content_start:at].strip('\n')
    return {'code':prompt[len(start):code_end], 'graph':graph, 'word':match.group(1), 'demo':match.group(2),
            'demo_start':at,'code_start':len(start),'code_end':code_end}


def normalized_tokens(row):
    t=row['tokens']
    return {'total':t.get('total',t.get('prompt_tokens')),'code':t.get('code',t.get('target_tokens_used')),
            'graph':t.get('graph',t.get('graph_tokens_used',0)), 'demo':t.get('demo',t.get('demo_tokens_used',0))}


def adapt_evidence(row, arm, graph_info, original_demo_tokens=None):
    """Use measured/saved evidence; never invent missing original-token counts."""
    t=normalized_tokens(row)
    cut=row.get('truncated',{})
    truncated={'code':bool(cut.get('code',row['tokens'].get('target_truncated',False))),
               'graph':bool(cut.get('graph',graph_info.get('truncated',False))),
               'demo':bool(cut.get('demo',row['tokens'].get('demo_truncated',False)))}
    expected=arm not in ('B0','B1')
    demos=[]
    if expected:
        item={'id':row['demo_ids'][0],'tokens':t['demo'],'truncated':truncated['demo']}
        if original_demo_tokens is not None: item['original_tokens']=original_demo_tokens
        demos.append(item)
    ev={'tokens':dict(t,approx=False),'truncated':truncated,'graph':graph_info,
        'demo':{'policy':'random' if arm=='B2-rand' else 'retrieved' if expected else 'none','demos':demos},
        'prompt_sha256':row['prompt_sha256']}
    return {**row,'arm':arm,'seed':row.get('seed',42),'evidence':ev}


def full_source_prefix(rendered, source, marker):
    if rendered==source.strip(): return True
    if not rendered.endswith(marker): return False
    prefix=rendered[:-len(marker)].rstrip()
    return bool(prefix) and source.strip().startswith(prefix)


def leak_classification(prompt):
    hits=[]
    for pattern in LEAK_PATTERNS:
        for m in re.finditer(pattern,prompt,re.I):
            prefix=prompt[max(0,m.start()-3):m.start()]
            ordinary=(pattern==LEAK_PATTERNS[0] and (prefix.endswith('->') or prefix.endswith('.')))
            hits.append({'pattern':pattern,'offset':m.start(),'classification':'cpp_member_label' if ordinary else 'needs_review',
                         'excerpt':prompt[max(0,m.start()-70):m.end()+100]})
    return hits


class ExactCounter:
    def __init__(self):
        from transformers import AutoTokenizer
        self.tok=AutoTokenizer.from_pretrained('Qwen/Qwen3-Coder-30B-A3B-Instruct',revision=REVISION,
                                              local_files_only=True,trust_remote_code=False)
        self.cache={}
    def count(self,text):
        key=digest(text)
        if key not in self.cache: self.cache[key]=len(self.tok.encode(text,add_special_tokens=False))
        return self.cache[key]
    def chat(self,prompt):
        return len(self.tok.apply_chat_template([{'role':'user','content':prompt}],tokenize=True,add_generation_prompt=True))


def configurations():
    return [('B0','legacy',42,ROOT/'02_Arm_B0_Source_Only/output/bundles'),
            ('B1','legacy',42,ROOT/'03_Arm_B1_Graph_Only/output/bundles'),('B2','legacy',42,OLD),
            ('B2-flip','legacy',42,ROOT/'04_Arm_B2_Flip/output/bundles'),
            ('B2-rep','legacy',42,ROOT/'05_Arm_B2_Rep/output/bundles'),
            ('B2','frozen',42,NEW),
            ('B2-flip','frozen',42,ROOT/'04_Arm_B2_Flip/output/bundles_frozen_donor_20261101')]+[
            ('B2-rand','frozen',seed,ROOT/f'06_Arm_B2_Rand/output/bundles/seed_{seed}') for seed in (42,43,44)]


def baseline_specs(path, references, counter):
    info={}
    for spec in rows(path):
        ref=references[spec['id']]; meta=ref['tokens']; n=meta['graph_nodes_used']; k=meta['graph_edges_used']
        selected=spec['nodes'][:n]; ids={str(v.get('id',i)) for i,v in enumerate(selected)}; edges=[]
        for e in spec['edges']:
            a=e.get('start',e.get('source',e.get('src'))); b=e.get('end',e.get('target',e.get('dst')))
            if str(a) in ids and str(b) in ids and len(edges)<k:
                edges.append(dict(e,start=a,end=b,type=e.get('type',e.get('label','CONNECTED_TO'))))
        graph=f'{NODE_HEAD}\n{format_nodes(selected)}\n{EDGE_HEAD}\n{format_edges(edges)}' if spec['nodes'] else ''
        initial_ids={str(v.get('id',i)) for i,v in enumerate(spec['nodes'][:40])}
        initial_edges=sum(str(e.get('start',e.get('source',e.get('src')))) in initial_ids and
                          str(e.get('end',e.get('target',e.get('dst')))) in initial_ids for e in spec['edges'])
        d=spec['demonstrations'][0]
        info[spec['id']]={'graph_text':graph,'query':spec['query_code'],'demo':d,'label':spec['label'],
             'graph':{'missing':not bool(spec['nodes']),'rendered_nodes':n,'rendered_edges':k,
                      'truncated':n<min(40,len(spec['nodes'])) or k<min(80,initial_edges)}}
    return info


def make_manual(out, candidates):
    all_picked=[]
    for dataset in ('devign','reveal'):
        pool=[r for r in candidates if r['dataset']==dataset]
        # Ensure every arm/version/seed is represented, then retain kit length/cut strata.
        groups={}
        for r in pool: groups.setdefault((r['arm'],r['phase'],r['seed']),[]).append(r)
        picked=[]; used=set()
        for key, items in sorted(groups.items()):
            first=min(items,key=lambda r:digest('42|'+r['audit_key']))
            picked.append(first);used.add(first['audit_key'])
        for r in stratified_manual_sample(pool,30,42):
            if r['audit_key'] not in used and len(picked)<30:
                picked.append(r);used.add(r['audit_key'])
        for r in sorted(pool,key=lambda r:digest('42|topup|'+r['audit_key'])):
            if len(picked)==30: break
            if r['audit_key'] not in used: picked.append(r);used.add(r['audit_key'])
        if len(picked)!=30: raise ValueError('Manual sample must contain 30 prompts per dataset')
        all_picked.extend(picked)
    by_file={}
    for r in all_picked: by_file.setdefault(r['prompt_source'],{}).setdefault(r['id'],[]).append(r)
    for path,selected in by_file.items():
        for original in rows(ROOT/path):
            for picked in selected.get(original['id'],[]):
                if original['prompt_sha256']!=picked['prompt_sha256']: raise ValueError('Manual source changed')
                picked['prompt']=original['prompt']
    if any('prompt' not in r for r in all_picked): raise ValueError('Manual prompt missing')
    with (out/'manual_sample.jsonl').open('w',encoding='utf-8',newline='\n') as f:
        for r in all_picked: f.write(json.dumps(r,ensure_ascii=False)+'\n')
    fields=['audit_key','dataset','split','arm','phase','seed','id','prompt_sha256','reviewer_name',
            'reviewed_at','target_code_intact','graph_valid','demo_valid','no_target_label_leak',
            'variant_correct','truncation_acceptable','overall_verdict','comments']
    sheets=[{k:r.get(k,'') for k in fields} for r in all_picked]
    csv_write(out/'reviewer_1.csv',sheets,fields);csv_write(out/'reviewer_2.csv',sheets,fields)
    packet=['# Bộ prompt chấm độc lập — chờ hai người đánh giá','',
            '60 prompt: 30 Devign + 30 REVEAL. Không cung cấp nhãn target, score hoặc metric model.','']
    for i,r in enumerate(all_picked,1):
        packet += [f"## {i}. {r['audit_key']}",'',r['prompt'],'','---','']
    (out/'manual_packet.md').write_text('\n'.join(packet),encoding='utf-8',newline='\n')
    rubric='''# Hướng dẫn chấm prompt độc lập

Trạng thái: CHƯA CHẤM. Hai phiếu đang để trống; không thay cho hai người đánh giá thực tế.
Mỗi người đọc cùng 60 prompt trong manual_packet.md, tự điền phiếu riêng trước khi trao đổi.
Không dùng kết quả model hoặc nhãn target để lựa chọn mẫu/đánh giá prompt.

Mỗi tiêu chí điền pass / fail / unclear / not_applicable và ghi lý do, vị trí cụ thể khi fail/unclear:
- target_code_intact: code target đúng mẫu, cắt ngắn có làm mất ngữ cảnh thiết yếu không.
- graph_valid: graph đúng target, có nội dung hợp lý; B0 chủ động không có graph là not_applicable.
- demo_valid: code demo và nhãn theo đúng biến thể; B0/B1 không có demo là not_applicable.
- no_target_label_leak: không có đáp án target bị chèn từ metadata; nhãn demo đúng thiết kế không phải rò rỉ.
- variant_correct: B0 khung trống; B1 graph + demo trống; B2 có demo; flip đảo nhãn demo; rep giống B2; rand donor ngẫu nhiên.
- truncation_acceptable: phần còn lại có thể hiểu được; demo dưới 25% gốc là cờ vi phạm contract cần xử lý.
- overall_verdict: pass / fail / unclear. Điền reviewer_name và thời điểm chấm thực tế.

Sau khi cả hai nộp phiếu, đối chiếu từng bất đồng và lập biên bản phân xử riêng. Không ghi đè phiếu ban đầu.
Bộ mẫu chọn không dựa metric test: bảo đảm arm/phiên/seed, phân tầng độ dài và cờ cắt bằng kit, seed 42, bù đủ 30 mỗi dataset.
Các mẫu lỗi tự động nằm trong remediation_rows.csv, không thay đổi bộ mẫu chỉ để loại bỏ ví dụ xấu.
'''
    (out/'RUBRIC.md').write_text(rubric,encoding='utf-8',newline='\n')
    return len(all_picked)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out-dir',type=Path,default=ROOT/'Runs-management/prompt_audit_20261102')
    ap.add_argument('--metadata-only',action='store_true',help='Do not retokenize; report remaining token checks explicitly')
    args=ap.parse_args();out=args.out_dir.resolve()
    if not out.is_relative_to(ROOT/'Runs-management'): raise ValueError('Output must stay in Runs-management')
    if out.exists(): raise SystemExit('Audit directory exists; choose a new version, never overwrite reviews')
    out.mkdir(parents=True)
    counter=None if args.metadata_only else ExactCounter()
    sources={str(Path(__file__).relative_to(ROOT)):sha(__file__),
             str((KIT/'grace_diag/prompt_audit.py').relative_to(ROOT)):sha(KIT/'grace_diag/prompt_audit.py')}; sets=[]; candidates=[]; remediations=[]; leaks=[]; inference=[]
    protected=[ROOT/'Runs-management/thresholds.json',ROOT/'Runs-management/threshold_lock_status.json']
    protected += list((ROOT/'Runs-management/analysis_lock_20261101').glob('*'))
    protected={str(p):sha(p) for p in protected if p.is_file()}
    bank_cache={}
    all_row_fields=None
    audit_stream=(out/'audit_rows.csv').open('w',encoding='utf-8-sig',newline=''); audit_writer=None
    try:
      for dataset,split in SPLITS:
        frozen_file=FREEZE/dataset/f'{split}_raw.jsonl'
        frozen={r['id']:r for r in rows(frozen_file)}
        frozen_manifest=read(FREEZE/'freeze_manifest.json')
        if sha(frozen_file)!=frozen_manifest['datasets'][dataset]['files_sha256'][f'{split}_raw.jsonl']:
            raise ValueError('Frozen raw changed')
        sources[str(frozen_file.relative_to(ROOT))]=sha(frozen_file)
        old_folder=OLD/dataset/split; old={r['id']:r for r in rows(old_folder/'prompts.jsonl')}
        old_manifest=read(old_folder/'bundle_manifest.json')
        if sha(old_folder/'specs.jsonl')!=old_manifest['spec_sha256']: raise ValueError('B2 specs changed')
        sources[str((old_folder/'specs.jsonl').relative_to(ROOT))]=sha(old_folder/'specs.jsonl')
        specs=baseline_specs(old_folder/'specs.jsonl',old,counter)
        if dataset not in bank_cache:
            cache=ROOT/f'Runs-management/donor_reconciliation_20261101/cache/{dataset}_new_bank.jsonl'
            proof=read(cache.parent.parent/f'{dataset}_retrieval_provenance.json')
            if sha(cache)!=proof['new']['cache_sha256']: raise ValueError('Frozen donor cache changed')
            sources[str(cache.relative_to(ROOT))]=sha(cache)
            bank_cache[dataset]={r['id']:r for r in rows(cache)}
        bank=bank_cache[dataset]
        frozen_refs={r['id']:r for r in rows(NEW/dataset/split/'prompts.jsonl')}
        for arm,phase,seed,folder in configurations():
            path=folder/dataset/split/'prompts.jsonl'
            mp=path.with_name('bundle_manifest.json')
            if not mp.exists(): mp=path.with_name('manifest.json')
            manifest=read(mp); file_sha=sha(path)
            if file_sha!=manifest['prompts_sha256']: raise ValueError('Prompt manifest mismatch: '+str(path))
            sources[str(path.relative_to(ROOT))]=file_sha; sources[str(mp.relative_to(ROOT))]=sha(mp)
            rr=list(rows(path)); adapted=[]; diagnostics=[]; seen=set(); split_flags=Counter()
            records={}
            if phase=='legacy' and arm in SOURCES:
                rp=ROOT/SOURCES[arm]/dataset/split/'records.jsonl'
                if rp.exists():
                    records={r['id']:r for r in rows(rp)}
                    if len(records)!=sum(1 for _ in rows(rp)): raise ValueError('Duplicate inference IDs')
                    sources[str(rp.relative_to(ROOT))]=sha(rp)
                    for r in records.values():
                        if r.get('arm')!=arm or r.get('dataset')!=dataset or r.get('split')!=split or r.get('model_sha256')!=MODEL_SHA or r.get('seed')!=42:
                            raise ValueError('Inference identity mismatch')
                    inference.append({'arm':arm,'dataset':dataset,'split':split,'count':len(records),
                        'invalid_response':sum(not r.get('response_valid') for r in records.values()),
                        'invalid_score':sum(not(r.get('valid') and isinstance(r.get('s'),(float,int)) and math.isfinite(r['s']) and 0<=r['s']<=1) for r in records.values()),
                        'records_sha256':sha(rp),'source':str(rp.relative_to(ROOT))})
            for row in rr:
                uid=row['id']; issues=[]; source=specs[uid]; ref=old[uid]; parts=split_prompt(row['prompt'])
                if uid in seen: issues.append('duplicate_id')
                seen.add(uid)
                if row.get('dataset')!=dataset or row.get('split')!=split or row.get('arm',arm)!=arm or row.get('seed',seed)!=seed: issues.append('row_identity')
                if row['label']!=frozen[uid]['target'] or source['label']!=row['label']: issues.append('target_label_metadata')
                if source['query'].strip()!=frozen[uid]['func'].strip(): issues.append('target_source')
                if digest(row['prompt'])!=row['prompt_sha256']: issues.append('prompt_hash')
                if not full_source_prefix(parts['code'],frozen[uid]['func'],'\n/* [TRUNCATED TARGET] */'): issues.append('target_code_payload')
                old_parts=split_prompt(ref['prompt'])
                if parts['code']!=old_parts['code']: issues.append('target_differs_from_reference')
                graph=source['graph'].copy()
                if arm=='B0':
                    graph={'missing':False,'rendered_nodes':0,'rendered_edges':0,'truncated':False,'intentionally_empty':True}
                    if parts['graph']!=f'{NODE_HEAD}\n\n{EDGE_HEAD}': issues.append('B0_graph_payload')
                else:
                    expected_graph=source['graph_text'].strip('\n')
                    if not expected_graph and arm=='B1': expected_graph=f'{NODE_HEAD}\n\n{EDGE_HEAD}'
                    if parts['graph']!=expected_graph: issues.append('target_graph_payload')
                demo=None; orig_tokens=None
                if arm in ('B0','B1'):
                    if row.get('demo_ids') or parts['word'] or parts['demo']: issues.append('unexpected_demo_payload')
                else:
                    if len(row.get('demo_ids',[]))!=1: issues.append('demo_count')
                    donor=row['demo_ids'][0]
                    demo=source['demo'] if phase=='legacy' else bank[donor]
                    did=demo.get('id',demo.get('function_uid')); func=demo['func']; true=int(demo['target'])
                    if donor!=did: issues.append('demo_identity')
                    displayed=1-true if arm=='B2-flip' else true
                    if parts['word']!=('Vulnerable' if displayed else 'Non-vulnerable'): issues.append('demo_label_payload')
                    if not full_source_prefix(parts['demo'],func,'\n/* [TRUNCATED] */'): issues.append('demo_code_payload')
                    if arm=='B2-rep' and row['prompt']!=ref['prompt']: issues.append('repeat_prompt_changed')
                    if arm=='B2-flip':
                        paired=old_parts if phase=='legacy' else split_prompt(frozen_refs[uid]['prompt'])
                        if parts['demo']!=paired['demo'] or parts['graph']!=paired['graph'] or row['demo_ids']!=(ref if phase=='legacy' else frozen_refs[uid])['demo_ids']: issues.append('flip_not_paired')
                    if arm=='B2-rand' and donor==ref['demo_ids'][0]: issues.append('random_reuses_retrieved_demo')
                    if counter: orig_tokens=counter.count(func.strip())
                item=adapt_evidence(row,arm,graph,orig_tokens)
                t=item['evidence']['tokens']; cut=item['evidence']['truncated']
                if any(not isinstance(t[k],int) or t[k]<0 for k in ('total','code','graph','demo')): issues.append('invalid_token_metadata')
                if t['total']+64>8192 or t['code']>3000 or t['graph']>1500 or t['demo']>1500: issues.append('token_budget')
                if graph['rendered_nodes']>40 or graph['rendered_edges']>80: issues.append('graph_cap')
                if counter:
                    exact={'total':counter.chat(row['prompt']),'code':counter.count(parts['code']),
                           'demo':counter.count(parts['demo']) if demo else 0,
                           'graph':counter.count(parts['graph']) if graph['rendered_nodes'] else 0}
                    for k in exact:
                        if exact[k]!=t[k]: issues.append('token_count_'+k)
                    if exact['total']+64>8192: issues.append('exact_context_overflow')
                gutted=bool(demo and ((orig_tokens is not None and cut['demo'] and t['demo']<.25*max(1,orig_tokens)) or row['tokens'].get('demo_below_25_percent',False)))
                hits=leak_classification(row['prompt']); unresolved=any(h['classification']=='needs_review' for h in hits)
                for h in hits: leaks.append({'id':uid,'arm':arm,'phase':phase,'seed':seed,'dataset':dataset,'split':split,**h})
                if unresolved: issues.append('label_leak_needs_review')
                rec=records.get(uid)
                if rec and (rec['prompt_sha256']!=row['prompt_sha256'] or rec['label']!=row['label']): issues.append('inference_prompt_mismatch')
                diagnostics.append({'issues':issues,'demo_below25':gutted,'inference_exists':rec is not None,
                    'original_demo_tokens':orig_tokens,'regex_hits':len(hits),'unresolved_leak':unresolved})
                split_flags.update(issues)
                if gutted: split_flags['demo_below_25_percent']+=1
                adapted.append(item)
                if len(adapted)%250==0: print(f'{arm}/{phase}/{seed}/{dataset}/{split}: {len(adapted)}/{len(rr)}',flush=True)
            if seen!=set(frozen) or len(rr)!=manifest['count']: raise ValueError('Incomplete prompt ID set')
            if not set(records)<=seen: raise ValueError('Unknown inference ID')
            res=audit_rows(adapted)
            key=f'{arm}/{phase}/seed_{seed}/{dataset}/{split}'
            for original,flat,diag in zip(rr,res['rows'],diagnostics):
                flat.update(dataset=dataset,split=split,phase=phase,audit_key=key+'/'+str(original['id']),
                            original_demo_tokens=diag['original_demo_tokens'],demo_below25=diag['demo_below25'],
                            inference_exists=diag['inference_exists'],issues=';'.join(diag['issues']),
                            regex_label_leak=flat['label_leak'],label_leak=diag['unresolved_leak'],
                            token_check='exact_pinned_tokenizer' if counter else 'saved_metadata_only')
                # Preserve source below-25 evidence even when original count is unavailable in metadata-only mode.
                flat['demo_empty']=bool(flat['demo_empty'] or diag['demo_below25'])
                if audit_writer is None:
                    all_row_fields=list(flat);audit_writer=csv.DictWriter(audit_stream,fieldnames=all_row_fields);audit_writer.writeheader()
                audit_writer.writerow(flat)
                if diag['issues'] or diag['demo_below25']:
                    remediations.append({**flat,'demo_id':';'.join(original.get('demo_ids',[]))})
                candidates.append({k:v for k,v in flat.items() if k not in ('original_demo_tokens','inference_exists','issues','regex_label_leak','label_leak','demo_empty') } | {'prompt_source':str(path.relative_to(ROOT))})
            summary=res['summary'][arm]
            summary.update(arm=arm,phase=phase,seed=seed,dataset=dataset,split=split,source=str(path.relative_to(ROOT)),
                           source_sha256=file_sha,violations=dict(split_flags),n_regex_flags=sum(d['regex_hits']>0 for d in diagnostics),
                           n_unresolved_leak=sum(d['unresolved_leak'] for d in diagnostics),
                           n_demo_below25=sum(d['demo_below25'] for d in diagnostics),
                           n_executed_needing_demo_review=sum(d['demo_below25'] and d['inference_exists'] for d in diagnostics),
                           token_verification='exact_pinned_tokenizer' if counter else 'metadata_only',
                           status='needs_remediation' if split_flags else 'pass_automatic_checks')
            summary['n_label_leak']=summary['n_unresolved_leak']
            summary['rate_demo_empty']=sum(r['demo_empty'] for r in res['rows'])/len(rr)
            if not counter: summary['status']='limited_metadata_audit' if not split_flags else 'needs_remediation'
            sets.append(summary)
            print(key, len(rr),'flags',dict(split_flags),flush=True)
            del rr,adapted,res
        del specs,old,frozen,frozen_refs
    finally:
      audit_stream.close()
    for path,value in sources.items():
        if sha(ROOT/path)!=value: raise ValueError('Input changed during audit: '+path)
    for path,value in protected.items():
        if sha(path)!=value: raise ValueError('Protected historical artifact changed: '+path)
    csv_write(out/'remediation_rows.csv',remediations)
    write_json(out/'leak_flags.json',leaks)
    write_json(out/'inference_audit.json',{'sets':inference,'total':sum(x['count'] for x in inference),
        'invalid_score':sum(x['invalid_score'] for x in inference),'invalid_response':sum(x['invalid_response'] for x in inference),
        'note':'Raw-response validity and score validity are separate. Audit does not alter test-before-lock chronology.'})
    manual_n=make_manual(out,candidates)
    present={s['arm'] for s in sets}
    result={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'audit_kind':'post_run_CPU_integrity_audit',
        'automatic_audit_executed':True,'full_study_acceptance':False,'manual_review_status':'awaiting_two_real_reviewers',
        'manual_sample_count':manual_n,'manual_sample_per_dataset':30,'thresholds_fitted':False,'llm_calls':0,
        'source_prompt_or_inference_modified':False,'historical_protected_hashes':protected,
        'tokenizer_revision':REVISION,'exact_token_recheck':counter is not None,
        'total_prompt_rows':sum(s['n'] for s in sets),'prompt_sets':sets,
        'coverage_15_arms':{a:'audited_existing_prompt_artifacts' if a in present else 'not_prepared_no_prompt_artifacts' for a in MATRIX},
        'scope_note':'Passing post-run integrity checks does not certify prior preregistration, threshold chronology, human review, or donor reconciliation completion.'}
    write_json(out/'audit_summary.json',result);write_json(out/'source_hashes.json',sources)
    lines=['# Audit prompt và output đã có — 02/11/2026','',
        f"Đã audit {result['total_prompt_rows']:,} dòng prompt, {len(sets)} tập; đối chiếu {sum(x['count'] for x in inference):,} output inference local.",
        'Audit chạy sau inference; giữ nguyên timestamp, prompt/output, khóa ngưỡng và snapshot lịch sử. Chưa gọi LLM hoặc tính khóa mới.','',
        '**Chỉ ghi hoàn thành bước thực thi audit tự động. Nghiệm thu toàn nghiên cứu và chấm tay chưa hoàn thành.**','',
        '| Arm | Phiên | Seed | Dataset | Split | N | Demo dưới 25% | Cờ khác | Kết luận |',
        '|---|---|---:|---|---|---:|---:|---|---|']
    for s in sets:
        other={k:v for k,v in s['violations'].items() if k!='demo_below_25_percent'}
        lines.append(f"| {s['arm']} | {s['phase']} | {s['seed']} | {s['dataset']} | {s['split']} | {s['n']} | {s['n_demo_below25']} | {json.dumps(other)} | {s['status']} |")
    lines += ['', '## Tiêu chí và giới hạn','',
        'Tiêu chí 25% được giữ theo xác nhận người dùng: các mẫu dưới ngưỡng được liệt kê cần xử lý, chưa inference lại.',
        'B0/B1 chủ động không có demo không bị gắn lỗi demo rỗng. Metadata adapter giữ policy, cờ cắt, original_tokens khi đo được và thông tin graph.',
        'Cờ regex thô được giữ trong leak_flags.json; chỉ loại cảnh báo nhầm cú pháp thành viên C/C++ như ->label : khỏi số lỗi rò rỉ. Các trường hợp khác giữ cần xem xét.',
        'Nhãn target chỉ đối chiếu metadata; payload target/code/graph/demo được so với source, đồng thời kiểm đúng phép biến đổi từng variant.',
        'Không có prompt cho 9 arm còn lại; không ghi chúng đã qua dry-run. Rerun-66 thuộc B2, không phải arm thứ 16.',
        '', '## Hồ sơ cần xem','',
        '- [Tóm tắt máy đọc](audit_summary.json), [audit từng prompt](audit_rows.csv).',
        '- [Danh sách mẫu cần xử lý](remediation_rows.csv), [cờ rò rỉ và phân loại](leak_flags.json).',
        '- [Đối chiếu inference](inference_audit.json), [hash nguồn](source_hashes.json).',
        '- [Bộ prompt chấm](manual_packet.md), [mẫu JSONL](manual_sample.jsonl), [rubric](RUBRIC.md).',
        '- [Phiếu người 1](reviewer_1.csv), [phiếu người 2](reviewer_2.csv): để trống, chờ đánh giá thực tế.','']
    (out/'KET_QUA.md').write_text('\n'.join(lines),encoding='utf-8',newline='\n')
    print('DONE',json.dumps({'prompts':result['total_prompt_rows'],'sets':len(sets),'manual_n':manual_n,
                             'remediation_rows':len(remediations),'exact_tokens':counter is not None}),flush=True)


if __name__=='__main__': main()
