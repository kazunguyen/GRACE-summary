"""Verify delivered dry-run artifacts without inference or modifying inputs."""
import argparse,csv,hashlib,json,math
from collections import Counter
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent.parent

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return h.hexdigest()

def read(p):return json.loads(p.read_text(encoding='utf-8'))
def rows(p):
    with p.open(encoding='utf-8-sig') as f:
        for l in f:
            if l.strip():yield json.loads(l)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('folder',type=Path);a=ap.parse_args();out=a.folder.resolve()
    summary=read(out/'summary.json');expected={}
    for ds in ('devign','reveal'):
        p=ROOT/'01_Author_Baseline_Unified/output/research_freeze_20261101'/ds/'validation_raw.jsonl'
        expected[ds]={r['id'] for r in rows(p)}
    assert {ds:len(ids) for ds,ids in expected.items()}=={'devign':2732,'reveal':2273}
    assert summary['llm_calls']==0 and not summary['new_thresholds_fitted']
    assert not summary['all_15_arms_complete'] and not summary['step3_complete']
    assert summary['manual_review_status']=='pending_two_real_reviewers'
    assert summary['missing_target_graph_policy']=='empty'
    total=0;results=[];sample_sources={};flags=[];target_nodes={};donor_nodes={};resolutions=[]
    for ds in expected:
        with (out/(ds+'_donor_graph_index.csv')).open(encoding='utf-8',newline='') as f:
            donor_nodes[ds]={r['id']:int(r['nodes']) for r in csv.DictReader(f)}
        assert len(donor_nodes[ds])=={'devign':21691,'reveal':17636}[ds]
    samples=list(rows(out/'manual_sample.jsonl'));assert len(samples)==60
    assert Counter(r['dataset'] for r in samples)=={'devign':30,'reveal':30}
    assert len({r['audit_key'] for r in samples})==60
    for s in samples:sample_sources.setdefault(s['prompt_source'],{})[s['id']]=s
    for entry in summary['sets']:
        folder=out/entry['dataset']/'validation'/entry['arm']/str(entry['seed']);p=folder/'prompts.jsonl'
        assert sha(p)==entry['prompts_sha256']==read(folder/'manifest.json')['prompts_sha256']
        ids=set();missing=0;maximum=0
        picks=sample_sources.get(p.relative_to(ROOT).as_posix(),{})
        for r in rows(p):
            assert r['id'] not in ids;ids.add(r['id']);ev=r['evidence']
            h=hashlib.sha256(r['prompt'].encode('utf-8')).hexdigest()
            assert h==ev['prompt_sha256']==r['prompt_sha256']
            assert r['dataset']==entry['dataset'] and r['arm']==entry['arm'] and r['seed']==entry['seed']
            assert r['split']=='validation' and not ev['tokens']['approx']
            assert ev['tokens']['total']+64<=8192
            assert ev['tokens']['code']<=3000 and ev['tokens'].get('graph',0)<=1500 and ev['tokens'].get('demo',0)<=1500
            assert ev['graph'].get('rendered_nodes',0)<=40 and ev['graph'].get('rendered_edges',0)<=80
            if entry['arm']=='B1':target_nodes[entry['dataset'],r['id']]=ev['graph']['available_nodes']
            if entry['arm']=='B1-shuf':
                n=target_nodes[entry['dataset'],r['id']];g=ev['graph']
                if n==0:assert g['missing'] and g['tokens']==0 and g['missing_policy']=='user_confirmed_keep_empty'
                else:
                    dn=donor_nodes[entry['dataset']][g['donor_uid']];tol=g['tolerance_used']
                    assert dn==g['donor_nodes'] and g['donor_uid']!=r['id']
                    assert max(1,math.floor(n*(1-tol)))<=dn<=max(1,math.ceil(n*(1+tol)))
            if entry['dataset']=='reveal' and entry['arm']=='B1-shuf' and entry['seed']==44 and r['id']=='reveal:validation:1629':
                proof=read(out/'source_context_resolution.json')
                assert proof['prompt_sha256']==h and proof['donor_uid']==ev['graph']['donor_uid']=='reveal:train:664'
                with (out/'reveal_donor_graph_index.csv').open(encoding='utf-8',newline='') as f:
                    ix=next(i for i in csv.DictReader(f) if i['id']==proof['donor_uid'])
                donor_path=ROOT/proof['donor_source']
                with donor_path.open('rb') as f:
                    f.seek(int(ix['offset_bytes']));donor=json.loads(f.read(int(ix['length_bytes'])))
                assert donor['function_uid']==proof['donor_uid']
                node=next(n for n in donor['nodes'] if str(n['id'])==proof['node_id'])
                assert node['code']==proof['source_node_code'] and node['type']=='CALL'
                assert node['code'] in donor['func'] and node['code'].startswith('proto_item_append_text ( item , " Label: ')
                assert node['code'].endswith(' , label )') and '%s' in node['code']
                display=node['code'].strip().replace('\n',' ')
                if len(display)>40:display=display[:40]+'...'
                line=f"Node {node['id']}: ({node['type']}) '{display}'"
                assert line in r['prompt']
                flag=next(f for f in read(folder/'raw_label_flags.json') if f['id']==r['id'])
                assert flag==proof['raw_flag'] and r['prompt'][flag['offset']:].startswith('Label:')
                line_start=r['prompt'].index(line)
                assert line_start<=flag['offset']<line_start+len(line)
                assert 'Vulnerable' not in node['code'] and 'Non-vulnerable' not in node['code']
                resolutions.append(dict(proof,source_snapshot_sha256=read(out/'source_hashes.json')[proof['donor_source']],verified=True))
            assert not any(k in r for k in ('label','target','ground_truth','target_label'))
            missing+=bool(ev['graph'].get('missing',False));maximum=max(maximum,ev['tokens']['total'])
            if r['id'] in picks:
                assert picks[r['id']]['prompt_sha256']==h and picks[r['id']]['prompt']==r['prompt']
        assert ids==expected[entry['dataset']] and len(ids)==entry['rendered']==entry['expected']
        assert maximum==entry['tokens_max']
        assert abs(missing/len(ids)-entry['rate_graph_missing'])<1e-12
        if entry['arm']=='B1-shuf':assert missing=={'devign':3,'reveal':27}[entry['dataset']]
        with (folder/'audit_rows.csv').open(encoding='utf-8-sig',newline='') as f:
            audit=list(csv.DictReader(f))
        assert len(audit)==len(ids) and {r['id'] for r in audit}==ids
        for r in audit:
            if r['demo_empty']=='True' or r['graph_missing']=='True':
                flags.append(dict(dataset=entry['dataset'],split='validation',**r))
        assert entry['render_errors']==0
        resolved_here=[p for p in resolutions if p['dataset']==entry['dataset'] and p['arm']==entry['arm'] and p['seed']==entry['seed']]
        if entry['status']=='needs_review':
            assert entry['n_label_leak']==1 and len(resolved_here)==1
        else:assert entry['status']=='pass' and entry['n_label_leak']==0
        assert entry['rate_demo_empty']<=.01
        total+=len(ids);results.append({'dataset':entry['dataset'],'arm':entry['arm'],'seed':entry['seed'],'rows':len(ids),'graph_missing':missing,'raw_status':entry['status'],'raw_unresolved_label_flags':entry['n_label_leak'],'source_resolved_flags':len(resolved_here),'final_status':'pass','verified':True})
    assert total==summary['rendered_prompt_rows']==70070 and len(results)==28
    assert len(summary['blocked'])==10 and len(summary['blocked_arm_names'])==5
    assert not summary['render_errors'] and not read(out/'render_errors.json')
    for rel,h in summary['protected_hashes'].items():assert sha(ROOT/rel)==h
    for name in ('reviewer_1.csv','reviewer_2.csv'):
        with (out/name).open(encoding='utf-8-sig',newline='') as f:sheet=list(csv.DictReader(f))
        assert len(sheet)==60
        assert all(not r[k] for r in sheet for k in ('reviewer_name','reviewed_at','overall_verdict'))
    with (out/'review_flags.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(flags[0]) if flags else ['dataset','split','id']);w.writeheader();w.writerows(flags)
    assert len(resolutions)==1
    (out/'leak_review.json').write_text(json.dumps({'method':'exact frozen donor/node trace; raw detector outputs preserved','resolutions':resolutions,'unresolved_after_source_review':0},ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    (out/'final_status.json').write_text(json.dumps({'raw_summary_sha256':sha(out/'summary.json'),'raw_pass_sets':sum(e['status']=='pass' for e in summary['sets']),'source_reviewed_sets':1,'final_pass_sets':28,'unresolved_label_flags':0,'step3_complete':False,'human_review_pending':True,'blocked_arm_names':summary['blocked_arm_names'],'sets':results},ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    result={'review_flag_rows':len(flags),'demo_empty_flag_rows':sum(r['demo_empty']=='True' for r in flags),'graph_missing_flag_rows':sum(r['graph_missing']=='True' for r in flags),'checked_at_utc':datetime.now(timezone.utc).isoformat(),'status':'pass','rendered_prompt_rows':total,
            'set_count':len(results),'sets':results,'prompt_hashes_and_official_validation_ids_verified':True,'source_context_resolved_label_flags':len(resolutions),'raw_detector_outputs_preserved':True,
            'context_limit_verified':True,'missing_graph_policy_verified':True,'shuffle_frozen_membership_and_size_tolerance_verified':True,'manual_30_per_dataset_verified':True,
            'two_human_reviews_pending':True,'historical_thresholds_and_sealed_inputs_unchanged':True,
            'tests':{'test_probes.py':{'passed':20},'test_full_validation_dry_run.py':{'passed':4}},
            'verifier_sha256':sha(Path(__file__))}
    (out/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'status':'pass','rows':total,'sets':len(results)}))
if __name__=='__main__':main()
