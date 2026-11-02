"""Inspect actual notebook call paths and prompt schema; do not run models or modify arm code."""
import ast,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];HERE=Path(__file__).parent
BASE=ROOT/'01_Author_Baseline_Unified'
sys.path.insert(0,str(BASE/'diagnostic_kit/src'))
from grace_diag.prompt_audit import audit_rows

FOLDERS={'B2':'01_Author_Baseline_Unified','B0':'02_Arm_B0_Source_Only','B1':'03_Arm_B1_Graph_Only','B2-flip':'04_Arm_B2_Flip','B2-rep':'05_Arm_B2_Rep'}
def source_text(p):
    if p.suffix=='.ipynb':
        n=json.loads(p.read_text(encoding='utf-8'))
        return '\n\n'.join(''.join(c.get('source',[])) for c in n['cells'] if c['cell_type']=='code')
    return p.read_text(encoding='utf-8')
def calls(p):
    if p.suffix=='.ipynb':
        n=json.loads(p.read_text(encoding='utf-8'));chunks=[''.join(c.get('source',[])) for c in n['cells'] if c['cell_type']=='code']
    else:chunks=[p.read_text(encoding='utf-8')]
    names=[]
    for text in chunks:
        if text.startswith('%%writefile'):text=text.split('\n',1)[1]
        try:tree=ast.parse(text)
        except SyntaxError:continue
        for node in ast.walk(tree):
            if isinstance(node,ast.Call):
                f=node.func;names.append(f.id if isinstance(f,ast.Name) else f.attr if isinstance(f,ast.Attribute) else '<dynamic>')
    return set(names)

summary={'scope':'01-05 active folders in GRACE-summary; static call-path audit plus first real prompt schema probe','arms':[]}
for arm,folder in FOLDERS.items():
    path=ROOT/folder
    notebooks=sorted((path/'notebooks').glob('*.ipynb'))
    prep=[p for p in notebooks if p.name.startswith('01_')]
    infer=[p for p in notebooks if p.name.startswith('02_') and 'kaggle' in p.name]
    sources=[p for p in path.glob('*.py') if not p.name.startswith(('test_','check_'))]+notebooks
    invoked=set().union(*(calls(p) for p in sources))
    inference_calls=set().union(*(calls(p) for p in infer)) if infer else set()
    prompt_root=BASE/'output/local_full/bundles_recovered_joern_final_20261031' if arm=='B2' else path/'output/bundles'
    probe=prompt_root/'devign/validation/prompts.jsonl'
    compat='no prompt artifact'
    if probe.exists():
        with probe.open(encoding='utf-8') as f:r=json.loads(next(f))
        try:audit_rows([r]);compat='accepted directly'
        except Exception as e:compat=f'{type(e).__name__}: {e}'
    entry={'arm':arm,'folder':folder,'prompt_notebooks':[p.relative_to(ROOT).as_posix() for p in prep],
        'inference_notebooks':[p.relative_to(ROOT).as_posix() for p in infer],
        'direct_prompt_audit_call':bool({'audit_rows','stratified_manual_sample'} & invoked),
        'direct_supervised_anchor_call':bool({'run_anchor','make_model'} & invoked),
        'inference_calls':sorted(inference_calls & {'run_batch','Llama','binary_scores','fsync','make_lock','persist_lock','require_test_lock','evaluate_output'}),
        'auto_threshold_lock':bool({'make_lock','persist_lock'}<=inference_calls),
        'test_threshold_gate':'require_test_lock' in inference_calls,
        'kit_prompt_audit_schema_probe':compat,
        'prompt_manifests':[]}
    for d in ('devign','reveal'):
        for s in ('validation','test'):
            mp=prompt_root/d/s/'bundle_manifest.json'
            if mp.exists():
                m=json.loads(mp.read_text(encoding='utf-8'))
                entry['prompt_manifests'].append({'dataset':d,'split':s,'count':m['count'],'variant':m.get('prompt_variant'),
                    'retrieval_scope':m.get('retrieval_scope'),'outside_new_frozen_bank':m.get('reference_demos_outside_new_frozen_bank'),
                    'freeze_manifest_sha256':m.get('freeze_manifest_sha256')})
    summary['arms'].append(entry)
    print(arm,'prep',len(prep),'inference',len(infer),'kit audit:',compat,'threshold gate',entry['test_threshold_gate'],flush=True)

found=[]
for folder in [BASE/'output',HERE]+[ROOT/f/'output' for a,f in FOLDERS.items() if a!='B2']:
    for name in ('audit_summary.json','manual_sample.jsonl','anchor_scores.csv','anchor_summary.json'):
        found.extend(p.relative_to(ROOT).as_posix() for p in folder.rglob(name) if not any(t in str(p) for t in ('offline_test','pytest','threshold_pipeline_tests')))
summary['audit_and_anchor_artifacts']=sorted(set(found))
summary['supervised_cli_input']='npz with ids and X; current CodeT5 cache stores vectors.npy + manifest.json; adapter/export required'
# Preserve the original dated integration audit.
(HERE/'KIEM_TRA_TICH_HOP_TUNG_ARM_CURRENT.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print('Artifacts:',summary['audit_and_anchor_artifacts'])
