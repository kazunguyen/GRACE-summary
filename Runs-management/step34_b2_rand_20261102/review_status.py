"""Report completeness of actual human review without modifying or inventing ratings."""
import csv,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent; AUDIT=HERE.parent/'prompt_audit_20261102'
FIELDS=('target_code_intact','graph_valid','demo_valid','no_target_label_leak','variant_correct','truncation_acceptable')
ALLOWED={'pass','fail','unclear','not_applicable'}
def read_csv(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def main():
 sample=[json.loads(x) for x in (AUDIT/'manual_sample.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
 expected={x['audit_key']:x for x in sample}
 if len(expected)!=60 or {d:sum(x['dataset']==d for x in sample) for d in ('devign','reveal')}!={'devign':30,'reveal':30}:raise ValueError('Manual sample count or uniqueness mismatch')
 reports=[]; maps=[]
 for filename in ('reviewer_1.csv','reviewer_2.csv'):
  rows=read_csv(AUDIT/filename);by_key={x['audit_key']:x for x in rows}
  if len(rows)!=60 or len(by_key)!=60 or set(by_key)!=set(expected):raise ValueError(f'Review sample IDs mismatch: {filename}')
  empty=[];bad=[]
  for key,row in by_key.items():
   ref=expected[key]
   if row['prompt_sha256']!=ref['prompt_sha256'] or row['dataset']!=ref['dataset'] or row['arm']!=ref['arm'] or row['id']!=ref['id']:raise ValueError(f'Sample identity mismatch: {key}')
   if not row['reviewer_name'].strip() or not row['reviewed_at'].strip() or any(not row[x].strip() for x in FIELDS+('overall_verdict',)):empty.append(key);continue
   if any(row[x].strip() not in ALLOWED for x in FIELDS) or row['overall_verdict'].strip() not in {'pass','fail','unclear'}:bad.append(key)
   if any(row[x].strip() in {'fail','unclear'} for x in FIELDS+('overall_verdict',)) and not row['comments'].strip():bad.append(key)
  names=sorted({x['reviewer_name'].strip() for x in rows if x['reviewer_name'].strip()})
  reports.append({'file':filename,'rows':len(rows),'incomplete':len(empty),'invalid':len(set(bad)),'reviewer_names':names});maps.append(by_key)
 distinct=bool(len(reports[0]['reviewer_names'])==len(reports[1]['reviewer_names'])==1 and reports[0]['reviewer_names'][0]!=reports[1]['reviewer_names'][0])
 disagreements=[]
 if all(x['incomplete']==x['invalid']==0 for x in reports):
  for key in expected:
   diffs=[f for f in FIELDS+('overall_verdict',) if maps[0][key][f].strip()!=maps[1][key][f].strip()]
   if diffs:disagreements.append({'audit_key':key,'fields':diffs})
 print(json.dumps({'sample_count':60,'reviewers':reports,'distinct_names':distinct,'disagreements':disagreements,'status':'pending' if not distinct or any(x['incomplete'] or x['invalid'] for x in reports) else 'awaiting_documented_adjudication','note':'Completeness and different names do not prove independent human review. Keep source forms and adjudication evidence.'},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
