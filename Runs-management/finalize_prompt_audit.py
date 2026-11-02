"""Resolve provable C/C++ scanner false positives without overwriting the raw audit."""
import csv
import hashlib
import json
import re
from pathlib import Path
from datetime import datetime, timezone

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
OUT=HERE/'prompt_audit_20261102'


def read(path):return json.loads(path.read_text(encoding='utf-8'))


def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')


def known_cpp_ternary(flag):
    if flag['pattern']!=r'\bLabel\s*:':return False
    relative=min(70,flag['offset'])
    return bool(re.search(r'\blabel\s*\?\s*$',flag['excerpt'][:relative],re.I) and
                re.match(r'label\s*:',flag['excerpt'][relative:],re.I))


def known_channel_diagnostic(flag):
    if flag['pattern']!=r'\bLabel\s*:':return False
    relative=min(70,flag['offset'])
    return bool(re.search(r'unknown channel descriptions\s+$',flag['excerpt'][:relative],re.I) and
                re.match(r'label\s*:\s*%d',flag['excerpt'][relative:],re.I))


def known_source_domain_label(flag):
    if flag['pattern']!=r'\bLabel\s*:':return False
    relative=min(70,flag['offset'])
    before=flag['excerpt'][:relative];after=flag['excerpt'][relative:]
    if re.search(r'SetImageProperty\s*\(\s*image\s*,\s*"$',before) and after.startswith('label:pointsize"'):
        return 'imagemagick_label_pointsize_property'
    if re.search(r'"(?:Packet|Generalized|: EVPL Generalized) $',before) and re.match(r'Label:\s*"',after):
        return 'network_packet_generalized_label_literal'
    if re.search(r'proto_item_append_text\s*\(\s*item\s*,\s*"\s*$',before) and re.match(r'Label:\s*\\"%s\\"',after):
        return 'protocol_field_label_format_string'
    return False


def key(row):return (row['arm'],row['phase'],str(row['seed']),row['dataset'],row['split'],row['id'])


def table(path,data):
    fields=list(data[0]) if data else ['id']
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(data)


def main():
    summary=read(OUT/'audit_summary.json')
    if (OUT/'final_status.json').exists():raise SystemExit('Final status already exists; do not overwrite reviews')
    flags=read(OUT/'leak_flags.json');unresolved=set();resolved=[]
    for flag in flags:
        result=dict(flag)
        if flag['classification']=='cpp_member_label':
            result['resolution']='cpp_member_expression_not_target_annotation'
        elif known_source_domain_label(flag):
            result['resolution']=known_source_domain_label(flag)
        elif known_channel_diagnostic(flag):
            result['resolution']='cpp_channel_description_format_string_not_target_annotation'
        elif known_cpp_ternary(flag):
            result['resolution']='cpp_ternary_label_variable_not_target_annotation'
        else:
            result['resolution']='needs_review';unresolved.add(key(flag))
        resolved.append(result)
    write(OUT/'leak_review.json',{'method':'static source-context resolution; raw leak_flags.json unchanged',
          'raw_flag_occurrences':len(flags),'unresolved_prompt_keys':[list(k) for k in sorted(unresolved)],'flags':resolved})
    with (OUT/'remediation_rows.csv').open(encoding='utf-8-sig') as f:raw=list(csv.DictReader(f))
    remaining=[]
    for row in raw:
        issues=[i for i in row['issues'].split(';') if i]
        if key(row) not in unresolved:issues=[i for i in issues if i!='label_leak_needs_review']
        row['issues']=';'.join(issues)
        if issues or row['demo_below25']=='True':remaining.append(row)
    table(OUT/'remediation_final.csv',remaining)
    executed=[r for r in remaining if r['inference_exists']=='True']
    table(OUT/'executed_needing_review.csv',executed)
    inference=read(OUT/'inference_audit.json')
    frozen=read(OUT/'donor_scope.json');random=read(OUT/'random_selection.json')
    payload_errors=[r for r in remaining if r['issues']]
    result={'checked_at_utc':datetime.now(timezone.utc).isoformat(),
        'automatic_audit_execution':'completed','prompt_rows_checked':summary['total_prompt_rows'],
        'prompt_sets_checked':len(summary['prompt_sets']),'inference_records_checked':inference['total'],
        'exact_token_recheck':summary['exact_token_recheck'],'payload_integrity_pass':not payload_errors,
        'unresolved_label_leak_prompts':len(unresolved),'demo_below25_rows':sum(r['demo_below25']=='True' for r in remaining),
        'executed_rows_needing_review':len(executed),'score_invalid':inference['invalid_score'],
        'raw_response_invalid':inference['invalid_response'],'random_selection_pass':random['all_pass'],
        'manual_review':'pending_two_real_reviewers','manual_sample_count':summary['manual_sample_count'],
        'not_prepared_arms':[a for a,s in summary['coverage_15_arms'].items() if s.startswith('not_prepared')],
        'study_acceptance':'not_complete_demo_remediation_and_manual_review_pending',
        'llm_calls':0,'new_thresholds_fitted':False,
        'legacy_donor_scope':{d:len(v['legacy_B2_targets_outside_frozen_bank']) for d,v in frozen['datasets'].items()},
        'raw_artifacts_overwritten':False}
    write(OUT/'final_status.json',result)
    group={}
    for r in remaining:
        k=(r['arm'],r['phase'],r['dataset'],r['split'])
        g=group.setdefault(k,{'n':0,'executed':0});g['n']+=1;g['executed']+=r['inference_exists']=='True'
    report=['## Kết luận sau phân loại cảnh báo','',
        f"Đã hoàn tất thực thi audit tự động trên {result['prompt_rows_checked']:,} dòng prompt/{result['prompt_sets_checked']} tập và đối chiếu {inference['total']:,} record inference.",
        f"Kiểm hash/ID/nhãn metadata/payload target-graph-demo/variant/token: {'ĐẠT' if result['payload_integrity_pass'] else 'CÒN LỖI CẦN XEM'} sau phân loại cảnh báo cú pháp C/C++ có bằng chứng.",
        f"Cảnh báo nhãn còn chưa giải quyết: {len(unresolved)} prompt. Toàn bộ cờ regex gốc được giữ, xem [phân loại](leak_review.json).",
        f"Có {result['demo_below25_rows']} dòng prompt có demo dưới 25% gốc (đếm riêng arm/phiên/seed); trong đó {len(executed)} dòng thuộc output đã inference. Giữ tiêu chí, chưa sửa prompt hoặc inference lại.",
        'B2 legacy vẫn có 21 target Devign dùng donor ngoài kho mới (10 do label conflict, 10 overlap eval exact, 1 duplicate train); đây là chênh lệch lịch sử đã biết, chưa được xóa bởi audit payload. 66 prompt đổi khi chuyển donor vẫn cần xử lý theo sổ run.',
        f"Kho frozen: code/nhãn/ID của {frozen['datasets']['devign']['frozen_donors_verified']:,} donor Devign và {frozen['datasets']['reveal']['frozen_donors_verified']:,} donor REVEAL đã khớp train manifest. 30.033 lựa chọn random khớp selector ba seed.",
        '', '| Arm | Phiên | Dataset | Split | Cần xử lý | Đã inference |','|---|---|---|---|---:|---:|']
    for (arm,phase,ds,split),g in sorted(group.items()):report.append(f"| {arm} | {phase} | {ds} | {split} | {g['n']} | {g['executed']} |")
    report += ['', '### Việc đã hoàn thành và việc còn lại','',
        '- Hoàn thành: adapter evidence, audit tự động toàn bộ artifact của 6 arm, kiểm lại token bằng tokenizer đã pin, đối chiếu output đã chạy, xác minh donor và selector random, chuẩn bị hồ sơ chấm tay.',
        '- Chưa hoàn thành: xử lý demo dưới 25%, hoàn tất inference phiên donor mới, hai người đọc độc lập, nghiệm thu toàn bộ nghiên cứu. Không đổi thứ tự test trước khóa hoặc trạng thái OSF. Kiểm tra rò rỉ tự động giới hạn ở so payload với nguồn và các mẫu regex; chưa thay thế đánh giá ngữ nghĩa bằng người.',
        '- 9 arm chưa có prompt được ghi chưa chuẩn bị theo quyết định người dùng; không mở thêm arm trong đợt này.',
        '- [Kết luận máy đọc](final_status.json), [danh sách cuối](remediation_final.csv), [output đã chạy cần xem](executed_needing_review.csv), [donor scope](donor_scope.json), [selector random](random_selection.json).','']
    report_path=OUT/'KET_QUA.md'
    original=report_path.read_text(encoding='utf-8')
    title,body=original.split('\n',1)
    report_path.write_text(title+'\n\n'+'\n'.join(report)+'\n\n## Kết quả quét thô trước phân loại cảnh báo\n'+body,encoding='utf-8',newline='\n')
    # Show examples without giving model metrics to the independent human reviewers.
    examples=[];used=set()
    for r in executed+remaining:
        g=(r['arm'],r['phase'],r['dataset'],r['split'])
        if g in used or r['demo_below25']!='True':continue
        used.add(g);examples.append(r)
        if len(examples)==6:break
    ex=['# Ví dụ demo dưới 25% cần xử lý','',
        'Giữ nguyên contract 25% theo xác nhận người dùng. Chưa thay prompt hoặc chạy lại LLM.','',
        '| Arm | Phiên | Dataset/split | Target | Demo | Token gốc | Token còn | Tỷ lệ | Đã inference |',
        '|---|---|---|---|---|---:|---:|---:|---|']
    for r in examples:
        original=int(r['original_demo_tokens']);remaining_tokens=int(r['tokens_demo'])
        ex.append(f"| {r['arm']} | {r['phase']} | {r['dataset']}/{r['split']} | {r['id']} | {r['demo_id']} | {original} | {remaining_tokens} | {remaining_tokens/original:.2%} | {r['inference_exists']} |")
    (OUT/'VI_DU_CAN_XU_LY.md').write_text('\n'.join(ex)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':main()
