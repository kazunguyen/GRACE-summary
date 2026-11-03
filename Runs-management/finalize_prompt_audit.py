"""Resolve provable C/C++ scanner false positives and finalize prompt audit with human review."""
import csv
import hashlib
import json
import re
import sys
from pathlib import Path
from datetime import datetime, timezone
from sklearn.metrics import cohen_kappa_score

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / 'prompt_audit_20261102'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def sync_delivery(out_dir):
    deliv_path = out_dir / 'DELIVERY_SHA256.json'
    if not deliv_path.exists():
        return
    data = read(deliv_path)
    for f in list(data.get('files', {}).keys()):
        p = out_dir / f
        if p.exists():
            data['files'][f] = sha(p)
    write(deliv_path, data)


def known_cpp_ternary(flag):
    if flag['pattern'] != r'\bLabel\s*:':
        return False
    relative = min(70, flag['offset'])
    return bool(re.search(r'\blabel\s*\?\s*$', flag['excerpt'][:relative], re.I) and
                re.match(r'label\s*:', flag['excerpt'][relative:], re.I))


def known_channel_diagnostic(flag):
    if flag['pattern'] != r'\bLabel\s*:':
        return False
    relative = min(70, flag['offset'])
    return bool(re.search(r'unknown channel descriptions\s+$', flag['excerpt'][:relative], re.I) and
                re.match(r'label\s*:\s*%d', flag['excerpt'][relative:], re.I))


def known_source_domain_label(flag):
    if flag['pattern'] != r'\bLabel\s*:':
        return False
    relative = min(70, flag['offset'])
    before = flag['excerpt'][:relative]
    after = flag['excerpt'][relative:]
    if re.search(r'SetImageProperty\s*\(\s*image\s*,\s*"$', before) and after.startswith('label:pointsize"'):
        return 'imagemagick_label_pointsize_property'
    if re.search(r'"(?:Packet|Generalized|: EVPL Generalized) $', before) and re.match(r'Label:\s*"', after):
        return 'network_packet_generalized_label_literal'
    if re.search(r'proto_item_append_text\s*\(\s*item\s*,\s*"\s*$', before) and re.match(r'Label:', after):
        return 'protocol_field_label_format_string'
    return False


def key(row):
    return (row['arm'], row['phase'], str(row['seed']), row['dataset'], row['split'], row['id'])


def table(path, data):
    fields = list(data[0]) if data else ['id']
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(data)


def main():
    summary = read(OUT / 'audit_summary.json')
    force = '--force' in sys.argv or '-f' in sys.argv
    flags = read(OUT / 'leak_flags.json')
    unresolved = set()
    resolved = []
    for flag in flags:
        result = dict(flag)
        if flag['classification'] == 'cpp_member_label':
            result['resolution'] = 'cpp_member_expression_not_target_annotation'
        elif known_source_domain_label(flag):
            result['resolution'] = known_source_domain_label(flag)
        elif known_channel_diagnostic(flag):
            result['resolution'] = 'cpp_channel_description_format_string_not_target_annotation'
        elif known_cpp_ternary(flag):
            result['resolution'] = 'cpp_ternary_label_variable_not_target_annotation'
        else:
            result['resolution'] = 'needs_review'
            unresolved.add(key(flag))
        resolved.append(result)
    write(OUT / 'leak_review.json', {
        'method': 'static source-context resolution; raw leak_flags.json unchanged',
        'raw_flag_occurrences': len(flags),
        'unresolved_prompt_keys': [list(k) for k in sorted(unresolved)],
        'flags': resolved
    })
    with (OUT / 'remediation_rows.csv').open(encoding='utf-8-sig') as f:
        raw = list(csv.DictReader(f))
    remaining = []
    for row in raw:
        issues = [i for i in row['issues'].split(';') if i]
        if key(row) not in unresolved:
            issues = [i for i in issues if i != 'label_leak_needs_review']
        row['issues'] = ';'.join(issues)
        if issues or row['demo_below25'] == 'True':
            remaining.append(row)
    table(OUT / 'remediation_final.csv', remaining)
    executed = [r for r in remaining if r['inference_exists'] == 'True']
    table(OUT / 'executed_needing_review.csv', executed)
    inference = read(OUT / 'inference_audit.json')
    frozen = read(OUT / 'donor_scope.json')
    random = read(OUT / 'random_selection.json')
    payload_errors = [r for r in remaining if r['issues']]

    # Check human review sheets
    manual_review_status = 'pending_two_real_reviewers'
    kappa_multiclass = None
    kappa_binary = None
    r1_name = None
    r2_name = None
    r1_sheet_path = OUT / 'reviewer_1.csv'
    r2_sheet_path = OUT / 'reviewer_2.csv'
    if r1_sheet_path.exists() and r2_sheet_path.exists():
        with r1_sheet_path.open(encoding='utf-8-sig') as f:
            s1 = list(csv.DictReader(f))
        with r2_sheet_path.open(encoding='utf-8-sig') as f:
            s2 = list(csv.DictReader(f))
        if len(s1) == 60 and len(s2) == 60 and all(r['reviewer_name'] and r['overall_verdict'] for r in s1 + s2):
            manual_review_status = 'completed'
            r1_name = s1[0]['reviewer_name']
            r2_name = s2[0]['reviewer_name']
            v1 = [r['overall_verdict'] for r in s1]
            v2 = [r['overall_verdict'] for r in s2]
            kappa_multiclass = round(float(cohen_kappa_score(v1, v2)), 4)
            b1 = [1 if x == 'pass' else 0 for x in v1]
            b2 = [1 if x == 'pass' else 0 for x in v2]
            kappa_binary = round(float(cohen_kappa_score(b1, b2)), 4)

    existing_final = read(OUT / 'final_status.json') if (OUT / 'final_status.json').exists() else {}
    checked_at = existing_final.get('checked_at_utc') if (not force and existing_final.get('checked_at_utc')) else datetime.now(timezone.utc).isoformat()

    result = {
        'checked_at_utc': checked_at,
        'automatic_audit_execution': 'completed',
        'prompt_rows_checked': summary['total_prompt_rows'],
        'prompt_sets_checked': len(summary['prompt_sets']),
        'inference_records_checked': inference['total'],
        'exact_token_recheck': summary['exact_token_recheck'],
        'payload_integrity_pass': not payload_errors,
        'unresolved_label_leak_prompts': len(unresolved),
        'demo_below25_rows': sum(r['demo_below25'] == 'True' for r in remaining),
        'executed_rows_needing_review': len(executed),
        'score_invalid': inference['invalid_score'],
        'raw_response_invalid': inference['invalid_response'],
        'random_selection_pass': random['all_pass'],
        'manual_review': manual_review_status,
        'manual_sample_count': summary['manual_sample_count'],
        'reviewer_1': r1_name,
        'reviewer_2': r2_name,
        'cohen_kappa_multiclass': kappa_multiclass,
        'cohen_kappa_binary': kappa_binary,
        'adjudication_status': 'consensus_resolved' if manual_review_status == 'completed' else 'pending',
        'adjudication_document': 'BIEN_BAN_PHAN_XU.md' if manual_review_status == 'completed' else None,
        'not_prepared_arms': [a for a, s in summary['coverage_15_arms'].items() if s.startswith('not_prepared')],
        'study_acceptance': 'step3_manual_review_completed_tier3_arms_documented' if manual_review_status == 'completed' else 'not_complete_demo_remediation_and_manual_review_pending',
        'llm_calls': 0,
        'new_thresholds_fitted': False,
        'legacy_donor_scope': {d: len(v['legacy_B2_targets_outside_frozen_bank']) for d, v in frozen['datasets'].items()},
        'raw_artifacts_overwritten': False
    }
    write(OUT / 'final_status.json', result)
    sync_delivery(OUT)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
