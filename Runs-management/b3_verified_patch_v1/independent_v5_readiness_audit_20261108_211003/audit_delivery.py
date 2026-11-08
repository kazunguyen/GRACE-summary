"""Read-only release audit; notebook fragments execute only in temporary workspace."""
import ast
import hashlib
import json
import math
import re
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
REL = ROOT / 'Runs-management/b3_verified_patch_v1/release_20261108_v5'
OLD = ROOT / 'Runs-management/b3_verified_patch_v1/release_20261108_v4'

def digest(data):
    return hashlib.sha256(data).hexdigest()

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def seal(obj, key):
    return digest(json.dumps({k:v for k,v in obj.items() if k != key},
        sort_keys=True, indent=2, ensure_ascii=False).encode()) == obj[key]

def function(source, name):
    node = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == name)
    return ast.get_source_segment(source, node)

def main():
    result = {'scope': 'B3/devign/validation/seed42', 'observations': {}}
    obs = result['observations']
    notebook = read(REL / 'delivery/notebook.ipynb')
    cells = {i: ''.join(c['source']) for i,c in enumerate(notebook['cells']) if c['cell_type']=='code'}
    worker = cells[7].split('\n',1)[1]
    obs['syntax'] = {}
    for i,s in cells.items():
        ast.parse(worker if i == 7 else s)
        obs['syntax'][str(i)] = True
    tree = ast.parse(cells[2])
    literal = lambda name: ast.literal_eval(next(n.value for n in tree.body
        if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets)))
    raw = literal('RUNTIME_LOCK_RAW')
    helper = literal('CONTRACT_HELPER_CODE')
    obs['runtime_contract_embedded_bytes_match'] = raw.encode() == (ROOT/'configs/inference_runtime_lock.json').read_bytes()
    obs['embedded_code_sha256'] = {'worker':digest(worker.encode()), 'helper':digest(helper.encode())}
    specs = [('inputs_manifest.json','seal_sha256'),('pools/pool_manifest.json','pool_manifest_seal_sha256'),
        ('validation/validation_prompt_manifest.json','prompt_manifest_seal_sha256'),
        ('governance/scope_decision.json','scope_decision_seal_sha256'),
        ('delivery/input_bundle/bundle_manifest.json','manifest_seal_sha256'),
        ('delivery/inference_input_manifest.json','seal_sha256'),
        ('delivery/delivery_manifest.json','delivery_seal_sha256')]
    obs['seals'] = {}
    for name,key in specs:
        data = read(REL/name)
        if key not in data:
            choices=[k for k in data if 'seal' in k and 'sha256' in k]
            key=choices[0]
        obs['seals'][name]=seal(data,key)
    dm=read(REL/'delivery/delivery_manifest.json')
    obs['delivery_files']= {k:digest((REL/'delivery'/k).read_bytes())==v for k,v in dm['artifacts_sha256'].items()}
    fim=read(REL/'delivery/inference_input_manifest.json')
    obs['input_zip_external_hash_matches']=digest((REL/'delivery/b3_devign_val_input.zip').read_bytes())==fim['bundle']['sha256']
    pm=read(REL/'validation/validation_prompt_manifest.json')
    obs['upstream_prompt_manifest_links']={
        'inputs':digest((REL/'inputs_manifest.json').read_bytes())==pm['upstream_manifests']['inputs_manifest_file_sha256'],
        'step7':digest((REL/'acceptance/step7_selector_renderer_report.json').read_bytes())==pm['upstream_manifests']['step7_report_sha256'],
        'pool':digest((REL/'pools/pool_manifest.json').read_bytes())==pm['upstream_manifests']['pool_manifest_sha256']}
    bm=read(REL/'delivery/input_bundle/bundle_manifest.json')
    with zipfile.ZipFile(REL/'delivery/b3_devign_val_input.zip') as z:
        obs['zip_members']={k:digest(z.read(k))==v for k,v in bm['files'].items()}
        raw_prompts=z.read('prompts.jsonl')
    rows=[json.loads(l) for l in raw_prompts.decode().splitlines()]
    obs['census']={'count':len(rows),'unique_ids':len({r['target_id'] for r in rows}),
        'sha256':digest(raw_prompts),'matches_prior_audited_fingerprint':digest(raw_prompts)=='dee4a33009f4ecbf42b96e6f18c5f4390d5f0a620370af925bae0f2cceeb7e59',
        'all_prompt_hashes_valid':all(digest(r['prompt'].encode())==r['prompt_sha256'] for r in rows),
        'rows_with_id':sum('id' in r for r in rows),'rows_with_label':sum('label' in r for r in rows)}
    # Reuse previous source/review audit only for identical bytes.
    inv=read(ROOT/'Runs-management/b3_verified_patch_v1/independent_prompt_audit_20261108_190936/source_inventory.json')
    reused={}
    for path,h in inv.items():
        p=Path(path)
        prefix=OLD.relative_to(ROOT)
        if p.is_relative_to(prefix):
            suffix=p.relative_to(prefix)
            if suffix.parts[0] in ('candidates','source_archive','reviews') or str(suffix).replace('\\','/') in ('pools/eligible_pairs.devign.jsonl','pools/eligible_pairs.reveal.jsonl'):
                new=REL/suffix
                reused[str(suffix)]=new.exists() and digest(new.read_bytes())==h
    obs['reused_source_review_pool_bytes']=reused
    inp=read(REL/'inputs_manifest.json')
    obs['code_hash_inventory']={}
    for group in ['modules_sha256','execution_scripts_sha256','authority_documents_sha256']:
        obs['code_hash_inventory'][group]={p:digest((ROOT/p).read_bytes())==h for p,h in inp[group].items()}
    # Execute the actual input loader cell against the actual delivered ZIP.
    with tempfile.TemporaryDirectory(dir=OUT) as tmp:
        scratch=Path(tmp); inputs=scratch/'input'; inputs.mkdir()
        (inputs/'b3_devign_val_input.zip').write_bytes((REL/'delivery/b3_devign_val_input.zip').read_bytes())
        env={'Path':Path,'zipfile':zipfile,'json':json,'hashlib':hashlib,'shutil':__import__('shutil'),
            'KAGGLE_INPUT_ROOT':inputs,'BUNDLE_WORK':scratch/'work','OUT_ROOT':scratch/'out',
            'BUNDLE_NAME':'b3_devign_val_input.zip','EXPECTED_COUNT':2732,'note':lambda *a:None,
            'CHECKPOINT_INPUT_PATH':None,'CHECKPOINT_NAME':'checkpoint.zip'}
        try:
            exec(compile(cells[4],'<notebook cell 4>','exec'),env)
            obs['actual_cell4_original_input']='ACCEPTED'
        except Exception as e:
            obs['actual_cell4_original_input']=f'{type(e).__name__}: {e}'
        # Isolate loader verification before the known schema failure. Change bytes
        # and its self-declared hash, leaving all external pins/manifest seals stale.
        changed=[dict(r) for r in rows]
        changed[0]['prompt']+='\nAUDIT_ONLY_MUTATION'
        changed_bytes=('\n'.join(json.dumps(r) for r in changed)+'\n').encode()
        modified=dict(bm); modified['prompts_sha256']=digest(changed_bytes)
        with zipfile.ZipFile(inputs/'b3_devign_val_input.zip','w') as z:
            z.writestr('bundle_manifest.json',json.dumps(modified))
            z.writestr('prompts.jsonl',changed_bytes)
        exec(compile(cells[4].split('expected_prompts =',1)[0],'<loader prefix only>','exec'),env)
        obs['tampered_bundle_loader_prefix_accepted']=env['prompts_records'][0]['prompt'].endswith('AUDIT_ONLY_MUTATION')
        # Check notebook validation on one valid-looking existing record.
        uid='audit-id'; record={'id':uid,'arm':'B3','seed':42,'dataset':'devign',
            'split':'validation','model_sha256':'audit-model','prompt_sha256':'audit-prompt','label':0,'s':0.5}
        rp=scratch/'records/seed_42/devign/validation/records.jsonl';rp.parent.mkdir(parents=True)
        rp.write_text(json.dumps(record)+'\n',encoding='utf-8')
        ns={'OUT_ROOT':scratch/'records','SEED':42,'DATASET':'devign','SPLIT':'validation','ARM':'B3',
            'MODEL_SHA256':'audit-model','json':json,'expected_prompts':{uid:('audit-prompt',0)}}
        exec(function(cells[4],'validate_records'),ns)
        try:
            ns['validate_records']();obs['notebook_existing_record_validation']='ACCEPTED'
        except Exception as e:obs['notebook_existing_record_validation']=f'{type(e).__name__}: {e}'
    native=next((ROOT/'Runs-management/locked_continuations_20261108/b1_full/remote_output').rglob('model_load_offload.log'))
    text=native.read_text(encoding='utf-8',errors='replace')
    obs['native_log_format_regression']={'source':str(native.relative_to(ROOT)),
        'helper_device_matches':len(re.findall(r'Device\s+\d+:\s+[^\n]*\bT4\b',text)),
        'using_device_cuda_matches':len(re.findall(r'using device CUDA\d+ \(Tesla T4\)',text))}
    # Execute only the pure score function, no model/backend/network.
    import numpy as np
    ns={'np':np,'math':math};exec(function(worker,'binary_scores'),ns)
    obs['pure_scoring']={}
    for name,values in [('equal',[0.,0.]),('positive',[0.,1000.]),('negative',[1000.,0.])]:
        obs['pure_scoring'][name]=ns['binary_scores'](values,[0,1])['s']
    try:ns['binary_scores']([float('nan'),0.],[0,1])
    except ValueError:obs['pure_scoring']['nonfinite_rejected']=True
    snapshot={str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in REL.rglob('*') if p.is_file()}
    snapshot.update({str((ROOT/p).relative_to(ROOT)):digest((ROOT/p).read_bytes())
        for p in ['scripts/build_release_v5.py','scripts/build_delivery_v5.py']})
    (OUT/'source_inventory.json').write_text(json.dumps(snapshot,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    result['verdict']='BLOCKED_DELIVERY_PREFLIGHT'
    (OUT/'audit.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2,ensure_ascii=False))

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
