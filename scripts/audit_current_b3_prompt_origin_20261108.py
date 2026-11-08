"""Read-only provenance check: actual B3-only delivery versus historical prompts."""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'Runs-management/locked_continuations_20261108'
stage=BASE/'b3_only_migrated'
sha=lambda raw:hashlib.sha256(raw).hexdigest()
report={'conclusion':'historical B3 prompts, not amended b3-verified-patch-v1','datasets':[]}
with ZipFile(next((stage/'dataset').glob('*.zip'))) as current:
    manifest=json.loads(current.read('input_manifest.json'))
    report['manifest_method']=manifest['method']
    for g in manifest['groups']:
        ds=g['dataset'];payload=current.read(g['member'])
        with ZipFile(ROOT/f'Runs-management/kernel_outputs_harvest/lznt123_grace-b3-validation/b3_bundles/B3_42_{ds}.zip') as historical:
            raw=historical.read('prompts.jsonl')
        rr=[json.loads(x) for x in payload.splitlines() if x.strip()]
        source=ROOT/f'Runs-management/dry_run_validation_20261102/{ds}/validation/B3/42/prompts.jsonl'
        old={str(r['id']):r for r in (json.loads(x) for x in source.read_bytes().splitlines() if x.strip())}
        mismatches=[r['id'] for r in rr if old[str(r['id'])]['prompt']!=r['prompt'] or old[str(r['id'])]['prompt_sha256']!=r['prompt_sha256']]
        result=dict(dataset=ds,count=len(rr),prompts_sha256=sha(payload),matches_historical_bundle_bytes=payload==raw,
            original_dry_run_source=str(source.relative_to(ROOT)),original_source_sha256=sha(source.read_bytes()),
            original_prompt_mismatches=mismatches)
        assert payload==raw and not mismatches and sha(payload)==g['sha256']
        report['datasets'].append(result)
remote=json.loads((stage/'remote_source_verification.json').read_text(encoding='utf-8'))
assert remote['all_cell_sources_match'] and remote['dataset_sources']==['huuhieu3333/grace-b3-only-resume-20261108-inputs-v2']
report['remote_readback']=remote
report['new_selector_source']='01_Author_Baseline_Unified/diagnostic_kit/src/grace_diag/amended_b3.py'
report['new_selector_used_by_current_prompt_inputs']=False
target=stage/'prompt_origin_audit.json'
target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False),flush=True)
