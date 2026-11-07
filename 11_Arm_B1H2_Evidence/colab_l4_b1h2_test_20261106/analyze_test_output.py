import hashlib,json,math,re,zipfile
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path

base=Path(__file__).parent
archive=base/'downloaded_output/b1h2_test_output.zip'
with zipfile.ZipFile(base/'b1h2_original_test_bundle.zip') as z:
    expected={r['id']:r for r in map(json.loads,z.read('prompts.jsonl').splitlines())}
with zipfile.ZipFile(archive) as z:
    rows=[json.loads(l) for l in z.read('records.jsonl').decode().splitlines() if l.strip()]
    status=json.loads(z.read('test_status.json'))
    checkpoints=[json.loads(z.read(n)) for n in z.namelist() if n.startswith('checkpoints/') and n.endswith('.json')]
    loads={n:json.loads(z.read(n)) for n in z.namelist() if n.endswith('load_summary.json')}
    native={n:re.findall(r'offloaded\s+(\d+)\s*/\s*(\d+)\s+layers?\s+to\s+GPU',z.read(n).decode(errors='replace'),re.I)
            for n in z.namelist() if n.endswith('llama_cpp_model_load_offload.log')}
ids={r['id'] for r in rows}
bad_hash=[r['id'] for r in rows if r['id'] not in expected or r['prompt_sha256']!=expected[r['id']]['prompt_sha256']]
checkpoint_by_id={r['id']:r for r in checkpoints}
report=dict(checked_at_utc=datetime.now(timezone.utc).isoformat(),archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
            drive_file_id='1MDE2TAcK-XIuiXre8S6vWQyeILCujdRG',status=status,records=len(rows),unique_ids=len(ids),
            dataset_counts=dict(Counter(r['dataset'] for r in rows)),missing_ids=sorted(set(expected)-ids),extra_ids=sorted(ids-set(expected)),
            prompt_hash_mismatches=bad_hash,bad_numeric_scores=sum(not all(math.isfinite(r[k]) for k in ('s','logprob_0','logprob_1')) for r in rows),
            raw_invalid_counts=dict(Counter(r['dataset'] for r in rows if not r.get('response_valid'))),
            model_hash_counts=dict(Counter(r['model_sha256'] for r in rows)),checkpoint_count=len(checkpoints),
            checkpoint_ids_match=set(checkpoint_by_id)==ids,checkpoint_content_mismatches=sum(checkpoint_by_id.get(r['id'])!=r for r in rows),
            first_record_utc=min(r['completed_utc'] for r in rows),last_record_utc=max(r['completed_utc'] for r in rows),
            load_summaries=loads,native_layer_reports=native,test_metrics_computed=False)
(base/'test_output_analysis.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ('load_summaries','model_hash_counts')},ensure_ascii=False,indent=2))
