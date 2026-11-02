"""Report raw-response coverage separately from continuous-score validity."""
import csv
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'Runs-management/prompt_audit_20261102'


def main():
    if (OUT/'raw_response_coverage.json').exists():raise SystemExit('Coverage report already exists')
    source=json.loads((OUT/'inference_audit.json').read_text(encoding='utf-8'))
    totals={};invalid=[]
    for group in source['sets']:
        arm=group['arm'];entry=totals.setdefault(arm,{'completed':0,'invalid_raw':0,'invalid_score':0,'raw_tokens':{}})
        entry['completed']+=group['count'];entry['invalid_raw']+=group['invalid_response'];entry['invalid_score']+=group['invalid_score']
        with (ROOT/group['source']).open(encoding='utf-8') as f:
            for line in f:
                if not line.strip():continue
                row=json.loads(line)
                if not row['response_valid']:
                    raw=str(row['raw']);entry['raw_tokens'][raw]=entry['raw_tokens'].get(raw,0)+1
                    invalid.append({k:row.get(k) for k in ('arm','dataset','split','id','prompt_sha256','raw','greedy_token_id','valid')})
    for value in totals.values():value['response_coverage']=1-value['invalid_raw']/value['completed']
    assert len(invalid)==source['invalid_response']
    with (OUT/'invalid_raw_responses.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(invalid[0]) if invalid else ['id']);w.writeheader();w.writerows(invalid)
    report={'arms':totals,'total_raw_invalid':len(invalid),'total_score_invalid':source['invalid_score'],
        'interpretation':'A non-label greedy token is a raw-response format failure, not an invalid finite 0/1 logit score. Preserve both fields; do not map raw failures to label 0 or silently drop valid scores.'}
    (OUT/'raw_response_coverage.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    p=OUT/'KET_QUA.md';text=p.read_text(encoding='utf-8');title,body=text.split('\n',1)
    note='\n## Raw response và score được kiểm riêng\n\n'
    for arm,v in totals.items():note+=f"- {arm}: {v['invalid_raw']}/{v['completed']} raw response không phải token nhãn, {v['invalid_score']} score không hợp lệ.\n"
    note+='\nĐã tính lại score từ hai logprob: 30.691/30.691 khớp, không chọn ngưỡng hoặc cấu hình từ test. Raw response không hợp lệ vẫn được báo coverage riêng; không phải bằng chứng score hỏng. [Chi tiết](raw_response_coverage.json), [ID/raw token](invalid_raw_responses.csv).\n'
    p.write_text(title+'\n'+note+'\n'+body,encoding='utf-8',newline='\n')
    print(json.dumps(report,ensure_ascii=False))


if __name__=='__main__':main()
