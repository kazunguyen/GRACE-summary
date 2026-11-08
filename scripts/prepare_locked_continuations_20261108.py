"""Stage immutable inputs and notebooks for the three authorized continuations."""
import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'Runs-management/locked_continuations_20261108'
HARVEST = ROOT / 'Runs-management/kernel_outputs_harvest'
RUNTIME_SHA = '85d8770839f80260cdc7c27b27b6cce6bf8815675c8593db68fb102589c5cbd6'
MODEL_SHA = 'f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335'

def sha(raw): return hashlib.sha256(raw).hexdigest()
def dump(value): return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n').encode()
def rows(raw): return [json.loads(x) for x in raw.splitlines() if x.strip()]

def prepare(kind):
    owner = {'b1_full':'huuhieu3333','b1_shuf':'tomandjerry223','b3':'lznt123'}[kind]
    slug = {'b1_full':'grace-b1-full-budgetfix-20261108','b1_shuf':'grace-b1-shuf-locked-20261108','b3':'grace-b3-locked-resume-20261108'}[kind]
    stage = BASE / kind
    stage.mkdir(exist_ok=True)
    data = stage / 'dataset'; data.mkdir(exist_ok=True)
    kernel = stage / 'kernel'; kernel.mkdir(exist_ok=True)
    members = {}
    groups = []
    locks = []
    if kind != 'b3':
        path = ROOT / ('09_Arm_B1_Full/config/threshold.json' if kind == 'b1_full' else '08_Arm_B1_Shuf/config/threshold.json')
        payload = path.read_bytes()
        members['threshold_lock.json'] = payload
        locks.append({'member':'threshold_lock.json','sha256':sha(payload)})
        lock = json.loads(payload)
        taus = {(e['seed'],e['dataset']): e['tau_star'] for e in lock['entries'].values()}
    if kind == 'b1_full':
        audit = json.loads((BASE/'b1_full_corrected_v4/audit.json').read_text(encoding='utf-8'))
        assert all(not x['graph_mismatches'] for x in audit['validation'])
        assert sum(x['n'] for x in audit['validation']) == 5005
        sources = [('B1-full',42,ds,'test',BASE/f'b1_full_corrected_v4/{ds}_test_prompts.jsonl') for ds in ('devign','reveal')]
        members['renderer_audit.json'] = dump(audit)
    elif kind == 'b1_shuf':
        sources = [('B1-shuf',seed,ds,'test',HARVEST/f'lznt123_grace-b1-shuf-test/b1_shuf_test_bundles/{seed}_{ds}.zip') for seed in (42,43,44) for ds in ('devign','reveal')]
    else:
        sources = [(arm,42,ds,'validation',HARVEST/f'lznt123_grace-b3-validation/b3_bundles/{arm}_42_{ds}.zip') for arm in ('B3','B3-nodiff') for ds in ('devign','reveal')]
    for arm,seed,ds,split,path in sources:
        if path.suffix == '.zip':
            with ZipFile(path) as z: payload = z.read('prompts.jsonl')
        else: payload = path.read_bytes()
        rr = rows(payload)
        expected = 2732 if ds == 'devign' else 2274 if split == 'test' else 2273
        assert len(rr) == expected and len({r['id'] for r in rr}) == expected
        member = f'{arm}_{seed}_{ds}_{split}.jsonl'
        members[member] = payload
        group = dict(arm=arm,seed=seed,dataset=ds,split=split,member=member,sha256=sha(payload),count=len(rr))
        if split == 'test': group['tau'] = taus[seed,ds]
        groups.append(group)
    legacy = b''
    if kind == 'b3':
        legacy = b''.join((HARVEST/f'lznt123_grace-b3-validation/b3_validation/B3/seed_42/{ds}/validation/records.jsonl').read_bytes().rstrip(b'\r\n') + b'\n' for ds in ('devign','reveal'))
        assert len(rows(legacy)) == 4029
    members['legacy_records.jsonl'] = legacy
    worker_source = (ROOT/'scripts/locked_continuation_runtime_20261108.py').read_text(encoding='utf-8')
    manifest = dict(schema='grace_locked_continuation_v1',runtime_contract_sha256=RUNTIME_SHA,model_sha256=MODEL_SHA,worker_sha256=sha(worker_source.encode()),
        groups=groups,threshold_locks=locks,legacy_records_sha256=sha(legacy),legacy_count=len(rows(legacy)),
        method='historical B3/B3-nodiff pairing unchanged; runtime migration only' if kind=='b3' else 'budget-corrected B1-full matching validation renderer' if kind=='b1_full' else 'frozen B1-shuf prompts; GPU-log guard correction',
        legacy_classification='Historical imported records are NOT retroactively certified under the new runtime lock. B3 historical pairing is NOT certified as amended patch-pair methodology.' if kind=='b3' else 'No historical inference imported; fresh fixed census.')
    members['input_manifest.json'] = dump(manifest)
    bundle = f'grace_locked_{kind}_20261108.zip'
    with ZipFile(data/bundle,'w',ZIP_DEFLATED) as z:
        for name,payload in members.items(): z.writestr(name,payload)
    # Exercise the exact worker verifier against the exact staged ZIP.
    spec = importlib.util.spec_from_file_location('locked_worker',ROOT/'scripts/locked_continuation_runtime_20261108.py')
    worker = importlib.util.module_from_spec(spec); spec.loader.exec_module(worker)
    checked = worker.load_inputs(data,bundle,sha(members['input_manifest.json']))
    assert len(checked[2]) == manifest['legacy_count']
    metadata = dict(id=f'{owner}/{slug}-inputs',title=slug+' inputs',licenses=[{'name':'CC0-1.0'}],isPrivate=True)
    (data/'dataset-metadata.json').write_bytes(dump(metadata))
    base = json.loads((ROOT/'Runs-management/acceptance_6arms_20261108/resume_delivery/02_kaggle_b1_shuf_test_gpu_log_guard_fixed.ipynb').read_text(encoding='utf-8'))
    cells = copy.deepcopy(base['cells'])
    def source(i,text): cells[i]['source']=text.splitlines(keepends=True)
    cells[0]['source']=[f'# {slug}\n\nNew inference is runtime locked. Historical B3 records retain their original provenance.\n']
    source(2,f'''KAGGLE_INPUT_ROOT = Path('/kaggle/input')
OUT_ROOT = Path('/kaggle/working/{kind}_locked_20261108')
BUNDLE_NAME = {bundle!r}
MANIFEST_SHA = {sha(members['input_manifest.json'])!r}
CHECKPOINT_NAME = {kind+'_locked_20261108_checkpoint.zip'!r}
MODEL_FILENAME = RUNTIME['model']['filename']
MAX_RUNTIME_HOURS = 9
''')
    source(3,'''# Only a checkpoint with this run's exact identity can be restored.
checkpoints = list(KAGGLE_INPUT_ROOT.rglob(CHECKPOINT_NAME))
if len(checkpoints) > 1: raise ValueError('Ambiguous checkpoint inputs')
if checkpoints:
    with zipfile.ZipFile(checkpoints[0]) as z:
        identity = json.loads(z.read('run_identity.json'))
        if identity['input_manifest_sha256'] != MANIFEST_SHA or identity['runtime_contract_sha256'] != EXPECTED_CONTRACT_SHA256:
            raise ValueError('Checkpoint identity mismatch')
        for name in z.namelist():
            target = (OUT_ROOT / name).resolve()
            if not target.is_relative_to(OUT_ROOT.resolve()): raise ValueError('Unsafe checkpoint path')
        if z.testzip() is not None: raise ValueError('Checkpoint CRC failure')
        z.extractall(OUT_ROOT)
print('Approved new input manifest:', MANIFEST_SHA)
''')
    worker_source = (ROOT/'scripts/locked_continuation_runtime_20261108.py').read_text(encoding='utf-8')
    source(7,"Path('/kaggle/working/kaggle_inference.py').write_text("+repr(worker_source)+", encoding='utf-8')\n")
    source(8,'''deadline = SESSION_STARTED + MAX_RUNTIME_HOURS * 3600
try:
    run_logged([sys.executable, '/kaggle/working/kaggle_inference.py',
        '--input-root', str(KAGGLE_INPUT_ROOT), '--bundle', BUNDLE_NAME,
        '--manifest-sha', MANIFEST_SHA, '--out', str(OUT_ROOT),
        '--checkpoint', '/kaggle/working/' + CHECKPOINT_NAME,
        '--model', model_path, '--deadline', str(deadline)], 'locked_inference')
finally:
    diagnostics_zip()
''')
    for i,c in enumerate(cells):
        if c['cell_type']=='code':
            c['outputs']=[];c['execution_count']=None
            ast.parse(''.join(c['source']),filename=f'{slug}:cell{i}')
    base['cells']=cells
    notebook=kernel/'notebook.ipynb'; notebook.write_bytes(dump(base))
    modelowner = 'quangdung1111' if owner == 'tomandjerry223' else owner
    km = dict(id=f'{owner}/{slug}',title=slug,code_file='notebook.ipynb',language='python',kernel_type='notebook',is_private=True,
        enable_gpu=True,enable_internet=True,machine_shape='NvidiaTeslaT4',dataset_sources=[metadata['id']],
        kernel_sources=[f'{modelowner}/qwen3coder30b-prepare-notebook'],competition_sources=[])
    (kernel/'kernel-metadata.json').write_bytes(dump(km))
    record = dict(kind=kind,owner=owner,ref=km['id'],dataset=metadata['id'],stage=str(stage.relative_to(ROOT)),
        input_manifest_sha256=sha(members['input_manifest.json']),bundle_sha256=sha((data/bundle).read_bytes()),
        notebook_sha256=sha(notebook.read_bytes()),worker_sha256=sha(worker_source.encode()),
        total=sum(g['count'] for g in groups),legacy_count=manifest['legacy_count'],new_target=sum(g['count'] for g in groups)-manifest['legacy_count'])
    (stage/'delivery.json').write_bytes(dump(record))
    print(json.dumps(record),flush=True)

if __name__ == '__main__':
    import sys
    for kind in sys.argv[1:] or ['b1_shuf','b3','b1_full']: prepare(kind)
