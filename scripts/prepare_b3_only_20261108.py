"""Narrow the authorized continuation to B3; stage it alongside B1-full."""
import ast
import copy
import importlib.util
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from prepare_locked_continuations_20261108 import ROOT, BASE, sha, dump

old=BASE/'b3'
stage=BASE/'b3_only'
if (stage/'launch.json').exists():raise ValueError('Do not overwrite a launched delivery')
data=stage/'dataset';data.mkdir(parents=True,exist_ok=True)
kernel=stage/'kernel';kernel.mkdir(exist_ok=True)
with ZipFile(next((old/'dataset').glob('*.zip'))) as z:
    original=json.loads(z.read('input_manifest.json'))
    manifest=copy.deepcopy(original)
    manifest['groups']=[g for g in original['groups'] if g['arm']=='B3']
    assert sum(g['count'] for g in manifest['groups'])==5005
    manifest['method']='Historical B3 pairing unchanged; B3 ONLY; runtime migration for new records'
    manifest['scope_correction']='PI explicitly excluded B3-nodiff on 2026-11-08. No B3-nodiff prompts are included.'
    members={g['member']:z.read(g['member']) for g in manifest['groups']}
    members['legacy_records.jsonl']=z.read('legacy_records.jsonl')
    members['input_manifest.json']=dump(manifest)
bundle='grace_locked_b3_only_20261108.zip'
with ZipFile(data/bundle,'w',ZIP_DEFLATED) as z:
    for name,raw in members.items():z.writestr(name,raw)
owner='huuhieu3333';slug='grace-b3-only-resume-20261108'
dm=dict(id=f'{owner}/{slug}-inputs',title=slug+' inputs',licenses=[{'name':'CC0-1.0'}],isPrivate=True)
(data/'dataset-metadata.json').write_bytes(dump(dm))
n=json.loads((old/'kernel/notebook.ipynb').read_text(encoding='utf-8'))
n['cells'][0]['source']=['# B3 ONLY — locked continuation\n\nB3-nodiff is excluded. Imported historical B3 records retain their original provenance.\n']
s=''.join(n['cells'][2]['source']).replace('b3_locked_20261108','b3_only_locked_20261108')
s=s.replace('grace_locked_b3_20261108.zip',bundle).replace(sha(dump(original)),sha(members['input_manifest.json']))
assert sha(members['input_manifest.json']) in s
n['cells'][2]['source']=s.splitlines(keepends=True)
for c in n['cells']:
    if c['cell_type']=='code':ast.parse(''.join(c['source']))
(kernel/'notebook.ipynb').write_bytes(dump(n))
km=json.loads((old/'kernel/kernel-metadata.json').read_text(encoding='utf-8'))
km.update(id=f'{owner}/{slug}',title=slug,dataset_sources=[dm['id']],kernel_sources=[f'{owner}/qwen3coder30b-prepare-notebook'])
(kernel/'kernel-metadata.json').write_bytes(dump(km))
spec=importlib.util.spec_from_file_location('worker',ROOT/'scripts/locked_continuation_runtime_20261108.py')
w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
m,groups,legacy=w.load_inputs(data,bundle,sha(members['input_manifest.json']))
assert len(legacy)==4029 and all(g['arm']=='B3' for g,ps in groups)
assert sha(members['legacy_records.jsonl'])==original['legacy_records_sha256']
delivery=dict(kind='b3_only',owner=owner,ref=km['id'],dataset=dm['id'],stage=str(stage.relative_to(ROOT)),
    input_manifest_sha256=sha(members['input_manifest.json']),bundle_sha256=sha((data/bundle).read_bytes()),
    notebook_sha256=sha((kernel/'notebook.ipynb').read_bytes()),worker_sha256=manifest['worker_sha256'],
    total=5005,legacy_count=4029,new_target=976,
    launch_precondition='Old lznt123/grace-b3-locked-resume-20261108 must be confirmed stopped; harvest any available B3 checkpoint first.')
(stage/'delivery.json').write_bytes(dump(delivery))
(stage/'checks.json').write_bytes(dump(dict(b3_only=True,census=5005,unchanged_legacy=4029,remaining_reveal=976,
    exact_B3_prompt_bytes=True,worker_unchanged=True,notebook_syntax=True)))
print(json.dumps(delivery),flush=True)
