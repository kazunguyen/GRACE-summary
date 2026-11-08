"""Adversarial predeployment checks using the actual staged prompts/legacy rows."""
import ast
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
from zipfile import ZipFile

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'Runs-management/locked_continuations_20261108'
spec=importlib.util.spec_from_file_location('worker',ROOT/'scripts/locked_continuation_runtime_20261108.py')
w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
passed=[]
def rejects(name,fn):
    try:fn()
    except (ValueError,FileNotFoundError,KeyError):passed.append(name);return
    raise AssertionError('Expected rejection: '+name)

for kind in ('b1_shuf','b3','b1_full'):
    stage=BASE/kind
    delivery=json.loads((stage/'delivery.json').read_text(encoding='utf-8'))
    archive=next((stage/'dataset').glob('*.zip'))
    m,groups,legacy=w.load_inputs(stage/'dataset',archive.name,delivery['input_manifest_sha256'])
    rejects(kind+': wrong input hash',lambda:w.load_inputs(stage/'dataset',archive.name,'0'*64))
    with tempfile.TemporaryDirectory() as td:
        with ZipFile(archive) as z:members={n:z.read(n) for n in z.namelist()}
        changed=dict(members);changed[groups[0][0]['member']]+=b'\n'
        with ZipFile(Path(td)/archive.name,'w') as z:
            for n,raw in changed.items():z.writestr(n,raw)
        rejects(kind+': corrupted prompts',lambda:w.load_inputs(td,archive.name,delivery['input_manifest_sha256']))
    for g,ps in groups:
        assert len(ps)==g['count']
        if kind=='b3':
            for p in ps:
                key=w.key_for(g,p)
                if key in legacy:w.validate_saved(legacy[key],p,g,m,legacy,m['runtime_contract_sha256'])
        else:
            assert g['tau'] in [e['tau_star'] for e in json.loads(members['threshold_lock.json'])['entries'].values()]
    if legacy:
        key=next(iter(legacy)); row=legacy[key];g,ps=next((g,ps) for g,ps in groups if (g['arm'],g['seed'],g['dataset'],g['split'])==key[:4])
        p=next(p for p in ps if str(p['id'])==key[4]);bad=copy.deepcopy(row);bad['s']=1-row['s']
        rejects('B3: modified historical score',lambda:w.validate_saved(bad,p,g,m,legacy,m['runtime_contract_sha256']))
    g,ps=groups[-1];p=ps[-1]
    new=dict(p,model_sha256=m['model_sha256'],valid=True,s=.5)
    rejects(kind+': unproven new record',lambda:w.validate_saved(new,p,g,m,legacy,m['runtime_contract_sha256']))
    notebook=json.loads((stage/'kernel/notebook.ipynb').read_text(encoding='utf-8'))
    for i,c in enumerate(notebook['cells']):
        if c['cell_type']=='code':ast.parse(''.join(c['source']))
    # Test the exact embedded source, not just the external worker file.
    cell=ast.parse(''.join(notebook['cells'][7]['source']))
    embedded=next(n.args[0].value for n in ast.walk(cell) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='write_text')
    assert w.digest_bytes(embedded.encode())==delivery['worker_sha256']==m['worker_sha256']
    passed.append(kind+': census, locks, exact worker source, notebook syntax and legacy equality')

score=w.binary_scores([10000.,9999.,-10000.],[0,1])
assert abs(score['s']-.2689414213699951)<1e-12
assert score['pred_argmax']==0
passed.append('Stable score calculation on extreme logits')
audit=json.loads((BASE/'b1_full_corrected_v4/audit.json').read_text(encoding='utf-8'))
assert sum(r['n'] for r in audit['validation'])==5005
assert all(not r['graph_mismatches'] for r in audit['validation'])
assert sum(r['n'] for r in audit['test'])==5006
assert all(r['max_code_tokens']<=3000 and r['max_graph_tokens']<=1500 and r['max_chat_tokens']+64<=8192 for r in audit['test'])
passed.append('B1-full exact validation prompt parity and full test component budgets')
(BASE/'predeployment_checks.json').write_text(json.dumps({'passed':passed,'count':len(passed)},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'passed':len(passed),'checks':passed}),flush=True)
