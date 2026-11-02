import json
from pathlib import Path

import pytest
import audit_prompt_integrity as audit


def test_adapter_preserves_original_demo_length_and_policy():
    row={'id':'t','prompt':'x','prompt_sha256':'h','demo_ids':['d'],
         'tokens':{'total':100,'code':10,'graph':20,'demo':30},
         'truncated':{'code':False,'graph':True,'demo':True}}
    adapted=audit.adapt_evidence(row,'B2',{'missing':False,'rendered_nodes':2},200)
    assert adapted['evidence']['demo']['demos'][0]['original_tokens']==200
    result=audit.audit_rows([adapted])
    assert result['rows'][0]['demo_empty']
    assert adapted['evidence']['demo']['policy']=='retrieved'
    assert 'evidence' not in row


def test_intentionally_absent_demo_is_not_a_failure():
    row={'id':'t','prompt':'x','prompt_sha256':'h','demo_ids':[],
         'tokens':{'prompt_tokens':10,'target_tokens_used':2,'demo_tokens_used':0}}
    adapted=audit.adapt_evidence(row,'B0',{'missing':False,'intentionally_empty':True})
    result=audit.audit_rows([adapted])
    assert not result['rows'][0]['demo_empty']
    assert not result['rows'][0]['graph_missing']
    assert adapted['evidence']['demo']['policy']=='none'


def test_leak_scanner_does_not_silence_real_annotations():
    ordinary=audit.leak_classification('x->label : fallback')
    assert ordinary and all(x['classification']=='cpp_member_label' for x in ordinary)
    actual=audit.leak_classification('TARGET LABEL: 1')
    assert any(x['classification']=='needs_review' for x in actual)
    actual=audit.leak_classification('// ground truth vulnerable')
    assert any(x['classification']=='needs_review' for x in actual)


def test_prefix_check_rejects_modified_source():
    assert audit.full_source_prefix('int f(){}','  int f(){}  ','<CUT>')
    assert audit.full_source_prefix('int f<CUT>','int f(){}','<CUT>')
    assert not audit.full_source_prefix('changed<CUT>','int f(){}','<CUT>')
    assert not audit.full_source_prefix('<CUT>','int f(){}','<CUT>')


def test_manual_packets_exactly_thirty_per_dataset_and_blank_ratings(tmp_path,monkeypatch):
    monkeypatch.setattr(audit,'ROOT',tmp_path)
    candidates=[]; original=[]
    for ds in ('devign','reveal'):
      for i in range(80):
        uid=f'{ds}:{i}';prompt=f'int f{i}(){{return 0;}}'
        original.append({'id':uid,'prompt':prompt,'prompt_sha256':audit.digest(prompt),'label':i%2})
        candidates.append({'audit_key':uid,'id':uid,'dataset':ds,'split':'validation','arm':'B1' if i%2 else 'B0',
           'phase':'legacy','seed':42,'prompt_sha256':audit.digest(prompt),'prompt_source':'source.jsonl',
           'tokens_total':i+1,'code_truncated':bool(i%3),'graph_truncated':False,'demo_truncated':False})
    (tmp_path/'source.jsonl').write_text('\n'.join(map(json.dumps,original)),encoding='utf-8')
    assert audit.make_manual(tmp_path,candidates)==60
    sample=[json.loads(l) for l in (tmp_path/'manual_sample.jsonl').read_text(encoding='utf-8').splitlines()]
    assert len({r['audit_key'] for r in sample})==60
    assert all('label' not in r and 's' not in r for r in sample)
    assert sum(r['dataset']=='devign' for r in sample)==30
    assert sum(r['dataset']=='reveal' for r in sample)==30
    import csv
    for name in ('reviewer_1.csv','reviewer_2.csv'):
        with (tmp_path/name).open(encoding='utf-8-sig') as f: sheet=list(csv.DictReader(f))
        assert len(sheet)==60
        assert all(not r['reviewer_name'] and not r['overall_verdict'] for r in sheet)


def test_ternary_resolution_is_bound_to_the_exact_flag_location():
    import re
    from finalize_prompt_audit import known_cpp_ternary
    text='x'*90+' label ? label : "";\nLabel: 1'
    matches=list(re.finditer(r'\bLabel\s*:',text,re.I))
    flags=[{'pattern':r'\bLabel\s*:','offset':m.start(),
            'excerpt':text[max(0,m.start()-70):m.end()+100]} for m in matches]
    assert len(flags)==2
    assert known_cpp_ternary(flags[0])
    assert not known_cpp_ternary(flags[1])


def test_channel_label_resolution_does_not_accept_class_annotations():
    import re
    from finalize_prompt_audit import known_channel_diagnostic
    for text,expected in [('error_line("warning: unknown channel descriptions label: %d", clabel);',True),
                          ('TARGET LABEL: 1',False),
                          ('unknown channel descriptions label: vulnerable',False)]:
        m=re.search(r'\bLabel\s*:',text,re.I)
        flag={'pattern':r'\bLabel\s*:','offset':m.start(),
              'excerpt':text[max(0,m.start()-70):m.end()+100]}
        assert known_channel_diagnostic(flag)==expected


def test_domain_label_strings_are_narrowly_classified():
    import re
    from finalize_prompt_audit import known_source_domain_label
    cases=[(r'proto_item_append_text ( item , " Label: \"%s\"" , label ) ;',True),('SetImageProperty ( image , "label:pointsize" , pointsize );',True),
           ('proto_item_append_text(ti, ", %s", label_type ? "Packet Label: " : "Generalized Label: ");',True),
           ('proto_item_append_text(ti, ": EVPL Generalized Label: " "VLAN ID = %u", vlan_id);',True),
           ('TARGET LABEL: 1',False),('"Label: vulnerable"',False)]
    for text,expected in cases:
        m=re.search(r'\bLabel\s*:',text,re.I)
        flag={'pattern':r'\bLabel\s*:','offset':m.start(),'excerpt':text[max(0,m.start()-70):m.end()+100]}
        assert bool(known_source_domain_label(flag))==expected
