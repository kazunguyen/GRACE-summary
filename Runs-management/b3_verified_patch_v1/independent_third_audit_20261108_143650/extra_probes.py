"""Synthetic probes only; production inputs and releases are read-only."""
from contextlib import redirect_stdout
from copy import deepcopy
import ast
import io
import json
from pathlib import Path
import runpy
import sys
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'01_Author_Baseline_Unified/diagnostic_kit/src')]
import b3_step6_packet_tool as tool
import b3_step7_verify_selector_renderer as step7
import b3_step5_make_candidates as step5
from grace_diag.amended_b3 import payload_hash
fixture = runpy.run_path(str(ROOT/'tests/test_amended_b3.py'))['fixture_pair']
pair, bank = fixture('case_probe')
candidate = {k:deepcopy(v) for k,v in pair.items() if k != 'reviews'}
sandbox = OUT/'probe_sandbox/extra'
sandbox.mkdir(parents=True, exist_ok=False)
def dump(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def rows(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in v),encoding='utf-8')
def review(name,decision='approve'):
    return dict(case_id='case_probe',reviewer=name,reviewed_at='2026-11-08T06:00:00Z',
        payload_sha256=payload_hash(candidate), decision=decision,comments='SYNTHETIC SOFTWARE CHECK ONLY',
        same_function_verified=True,security_fix_verified=True,source_revisions_verified=True,explanation_supported=True)
known={'case_probe':dict(case_id='case_probe',payload_sha256=payload_hash(candidate))}
triage={'case_probe':dict(case_id='case_probe',status='AUTOMATED_TRIAGE_PASS')}
result={'scope':'SYNTHETIC SOFTWARE ONLY; NO REAL HUMAN REVIEW OR SOURCE CLAIM'}
badtime=review('SYNTHETIC-1');badtime['reviewed_at']='TEST-FIXTURE-NOT-A-DATE'
result['test_fixture_timestamp_default_validation']=tool.validate_review_form(badtime,known,triage)

# Existing admitted pair followed by two approvals and a third rejection.
fake_root=sandbox/'mini_repo'
for ds in ('devign','reveal'):
    rr=list(bank.values()) if ds=='devign' else []
    f=fake_root/'01_Author_Baseline_Unified/output/research_freeze_20261101'/ds
    rows(f/'train_raw.jsonl',rr)
    rows(f/'train_manifest.jsonl',[dict(id=r['id'],keep_in_bank=True) for r in rr])
release=sandbox/'existing_pool_reject'
pool=release/'pools/eligible_pairs.devign.jsonl';rows(pool,[pair])
dump(release/'review_packets/case_probe.json',known['case_probe'])
rows(release/'reviews/triage_ledger.jsonl',list(triage.values()))
rows(release/'candidates/candidates.jsonl',[candidate])
for i,rev in enumerate([review('SYNTHETIC-1'),review('SYNTHETIC-2'),review('SYNTHETIC-3','reject')]):
    dump(release/f'reviews/submitted/review_{i}.json',rev)
before=pool.read_bytes(); log=io.StringIO()
with patch.object(tool,'ROOT',fake_root),redirect_stdout(log):
    tool.ingest_human_reviews_and_seal_pools(release)
manifest=json.loads((release/'pools/pool_manifest.json').read_text(encoding='utf-8'))
result['existing_pool_with_new_reject']={
    'pool_bytes_preserved':pool.read_bytes()==before,
    'manifest_devign':manifest['pools']['devign'],
    'log':log.getvalue()}

# Run actual Step 7 body; external subprocess calls are stubs. Actual local
# tokenizer, synthetic selector and report construction remain unchanged.
# This isolates report-construction errors without rerunning tests or altering previews.
try:
    with patch.object(step7.subprocess,'run',return_value=SimpleNamespace(returncode=0,stdout='SYNTHETIC SUBPROCESS STUB',stderr='')),redirect_stdout(io.StringIO()):
        step7.run_step7(sandbox/'step7')
    result['step7_report_construction']={'exception':None}
except Exception as exc:
    result['step7_report_construction']={'exception':type(exc).__name__,'message':str(exc)}

# Missing before/after source evidence defaults silently to frozen donor bodies.
case=sandbox/'source_missing_functions/source_archive/devign/case_probe'
cm=dict(case_id='case_probe',project='SYNTHETIC',function_hint=candidate['source']['function'],
    vulnerable_donor=dict(id=candidate['vulnerable_id'],commit_id='a'*40),
    patched_candidate_donor=dict(id=candidate['patched_id'],commit_id='b'*40),
    source_investigation=dict(has_both_commit_responses=True,is_direct_parent_edge=False,shared_files=[]),decision={})
dump(case/'case_manifest.json',cm)
ev={k:v for k,v in candidate['source'].items() if k not in ('before','after','fix_diff','diff')}
dump(case/'evidence_sidecar.json',ev)
(case/'actual_fix.diff').write_text(candidate['source']['fix_diff'],encoding='utf-8')
with patch.object(step5,'FREEZE_DIR',fake_root/'01_Author_Baseline_Unified/output/research_freeze_20261101'),redirect_stdout(io.StringIO()):
    step5.run_step5(sandbox/'source_missing_functions')
result['sidecar_without_before_after']={
    'before_in_submitted_sidecar':'before' in ev,'after_in_submitted_sidecar':'after' in ev,
    'summary':json.loads((sandbox/'source_missing_functions/candidates/candidates_summary.json').read_text(encoding='utf-8'))}

# Original recorded-commit triage rejects an otherwise valid candidate even
# when its actual source fix and parent differ from recorded donor metadata.
dump(case/'candidate.json',candidate)
packets=tool.generate_review_packets(sandbox/'source_missing_functions',candidates=[candidate])
tr=tool.run_automated_technical_triage(sandbox/'source_missing_functions')
result['source_candidate_vs_recorded_commit_triage']={
    'candidate_payload_available':packets[0]['has_candidate_payload'],
    'triage':tr,
    'approval_validation':tool.validate_review_form(review('SYNTHETIC-1'),{'case_probe':packets[0]},{'case_probe':tr[0]})}

# Reach actual overall-verdict expression with individual input checks failed.
tree=ast.parse((ROOT/'Runs-management/b3_verified_patch_v1/remediation_audit_20261108/audit_remediated_release.py').read_text(encoding='utf-8'))
assign=next(n for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='all_remediations_passed' for t in n.targets))
mock={'prior_v1_release_preservation':{'intact':True},'freeze_and_inputs':dict(module_hashes_pass=True,scripts_hashes_pass=True,freeze_manifest_hash_pass=False,freeze_files_pass=False,authority_hashes_pass=False,tokenizer_files_pass=False)}
for k,s in [('finding_f01_remediation','PASS_CLEAN_SEPARATION'),('finding_f02_remediation','PASS_BOUNDED_AND_COMPLETE_PROVENANCE'),('finding_f03_remediation','PASS_TRUTHFUL_CENSUS_EVALUATION'),('finding_f04_remediation','PASS_REAL_SOURCE_ONLY'),('finding_f05_remediation','PASS_FACTUAL_UNRESOLVED_PROVENANCE'),('finding_f06_and_f07_remediation','PASS_GATES_AND_GOVERNANCE_HONEST')]:mock[k]={'status':s}
scope={'all_seals_pass':True,'result':mock}
exec(compile(ast.Module(body=[assign],type_ignores=[]),'actual_overall_gate','exec'),scope)
result['overall_gate_ignores_four_input_checks']=scope['all_remediations_passed']
(OUT/'extra_probe_results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
