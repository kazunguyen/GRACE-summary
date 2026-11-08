"""Preserve and authenticate B3 rows obtained before the combined run was cancelled."""
import ast
import copy
import importlib.util
import json
import math
import re
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from prepare_locked_continuations_20261108 import ROOT, BASE, sha, dump

source=BASE/'b3/remote_output/b3_locked_20261108'
prior=BASE/'b3'
template=BASE/'b3_only'
stage=BASE/'b3_only_migrated'
if stage.exists():raise ValueError('Preserve prior staged migration')
data=stage/'dataset';data.mkdir(parents=True)
kernel=stage/'kernel';kernel.mkdir()
spec=importlib.util.spec_from_file_location('worker',ROOT/'scripts/locked_continuation_runtime_20261108.py')
w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
delivery=json.loads((prior/'delivery.json').read_text(encoding='utf-8'))
m,groups,legacy=w.load_inputs(prior/'dataset','grace_locked_b3_20261108.zip',delivery['input_manifest_sha256'])
m['_manifest_sha256']=delivery['input_manifest_sha256']
contract=json.loads((source/'inference_runtime_lock.json').read_text(encoding='utf-8'))
assert sha((source/'inference_runtime_lock.json').read_bytes())==m['runtime_contract_sha256']
records=[];new=[];evidence={}
for g,ps in groups:
    if g['arm']!='B3':continue
    lookup={str(p['id']):p for p in ps}
    path=source/f"B3/seed_42/{g['dataset']}/validation/records.jsonl"
    rr=w.jsonl(path.read_bytes())
    assert len({str(r['id']) for r in rr})==len(rr)
    for row in rr:
        w.validate_saved(row,lookup[str(row['id'])],g,m,legacy,m['runtime_contract_sha256'],source)
        expected_score=1/(1+math.exp(row['logprob_0']-row['logprob_1']))
        assert abs(expected_score-row['s'])<1e-12
        if w.key_for(g,row) not in legacy:
            proof=source/row['runtime_provenance']
            info=json.loads(proof.read_text(encoding='utf-8'))
            assert info['constructor']==contract['constructor'] and info['packages']==contract['packages']
            log=(proof.parent/'model_load_offload.log').read_text(encoding='utf-8')
            assert re.search(r'offloaded\s+49/49\s+layers?\s+to\s+GPU',log,re.I)
            assert set(re.findall(r'using device CUDA(\d+)\s+\([^\n)]*T4[^\n)]*\)',log))=={'0','1'}
            for filename in ('runtime_provenance.json','backend_build.log','model_load_offload.log'):
                p=proof.parent/filename;evidence[p.relative_to(source).as_posix()]=p.read_bytes()
            new.append(row)
    records.extend(rr)
assert len(records)==4058 and len(new)==29
for row in legacy.values():
    assert any(w.canonical(row)==w.canonical(r) for r in records if r['id']==row['id'] and r['dataset']==row['dataset'])
with ZipFile(next((template/'dataset').glob('*.zip'))) as z:
    members={name:z.read(name) for name in z.namelist()}
manifest=json.loads(members['input_manifest.json'])
old_sha=sha(members['input_manifest.json'])
members['legacy_records.jsonl']=b''.join((json.dumps(r,ensure_ascii=False,allow_nan=False)+'\n').encode() for r in records)
manifest.update(legacy_count=4058,legacy_records_sha256=sha(members['legacy_records.jsonl']),
    legacy_classification='4029 historical rows retain uncertified historical runtime; 29 source-runtime-locked B3 rows authenticated against original source manifest/native/build evidence and preserved unchanged. Remaining 947 records use the current manifest/runtime lock.')
index=[]
for relative,raw in evidence.items():
    member='migration_evidence/'+relative;members[member]=raw
    index.append(dict(member=member,output_relative=relative,sha256=sha(raw)))
migration=dict(original_input_manifest_sha256=delivery['input_manifest_sha256'],historical_rows=4029,
    verified_source_locked_rows=29,total_imported=4058,remaining=947,
    row_evidence=[{'id':r['id'],'sha256':w.canonical(r),'runtime_provenance':r['runtime_provenance'],'runtime_provenance_sha256':r['runtime_provenance_sha256']} for r in new])
members['migration_evidence/acceptance.json']=dump(migration)
index.append(dict(member='migration_evidence/acceptance.json',output_relative='source_migration_acceptance.json',sha256=sha(members['migration_evidence/acceptance.json'])))
manifest['migration_evidence']=index
members['input_manifest.json']=dump(manifest)
bundle='grace_locked_b3_only_migrated_20261108.zip'
with ZipFile(data/bundle,'w',ZIP_DEFLATED) as z:
    for name,raw in members.items():z.writestr(name,raw)
dm=json.loads((template/'dataset/dataset-metadata.json').read_text(encoding='utf-8'))
dm['id']+='-v2';dm['title']+=' v2';(data/'dataset-metadata.json').write_bytes(dump(dm))
n=json.loads((template/'kernel/notebook.ipynb').read_text(encoding='utf-8'))
s=''.join(n['cells'][2]['source']).replace('grace_locked_b3_only_20261108.zip',bundle).replace(old_sha,sha(members['input_manifest.json']))
n['cells'][2]['source']=s.splitlines(keepends=True)
restore='''
# Preserve hash-pinned evidence for the 29 imported runtime-locked source rows.
archives=list(KAGGLE_INPUT_ROOT.rglob(BUNDLE_NAME))
if len(archives)>1:raise ValueError('Ambiguous migration bundle')
if archives:
    migration_zip=zipfile.ZipFile(archives[0]);read_member=migration_zip.read
else:
    manifests=list(KAGGLE_INPUT_ROOT.rglob('input_manifest.json'))
    if len(manifests)!=1:raise ValueError('Ambiguous migration manifest')
    read_member=lambda name:(manifests[0].parent/name).read_bytes()
    migration_zip=None
try:
    raw_manifest=read_member('input_manifest.json')
    if hashlib.sha256(raw_manifest).hexdigest()!=MANIFEST_SHA:raise ValueError('Migration manifest mismatch')
    for ref in json.loads(raw_manifest)['migration_evidence']:
        payload=read_member(ref['member'])
        if hashlib.sha256(payload).hexdigest()!=ref['sha256']:raise ValueError('Migration evidence hash mismatch')
        target=(OUT_ROOT/ref['output_relative']).resolve()
        if not target.is_relative_to(OUT_ROOT.resolve()):raise ValueError('Unsafe migration output path')
        if target.exists() and target.read_bytes()!=payload:raise ValueError('Changed saved migration evidence')
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(payload)
finally:
    if migration_zip:migration_zip.close()
'''
n['cells'][3]['source']+=restore.splitlines(keepends=True)
for c in n['cells']:
    if c['cell_type']=='code':ast.parse(''.join(c['source']))
(kernel/'notebook.ipynb').write_bytes(dump(n))
km=json.loads((template/'kernel/kernel-metadata.json').read_text(encoding='utf-8'));km['dataset_sources']=[dm['id']]
(kernel/'kernel-metadata.json').write_bytes(dump(km))
newdelivery=json.loads((template/'delivery.json').read_text(encoding='utf-8'))
newdelivery.update(kind='b3_only_migrated',dataset=dm['id'],stage=str(stage.relative_to(ROOT)),
    input_manifest_sha256=sha(members['input_manifest.json']),bundle_sha256=sha((data/bundle).read_bytes()),
    notebook_sha256=sha((kernel/'notebook.ipynb').read_bytes()),legacy_count=4058,new_target=947,
    historical_uncertified_count=4029,verified_source_runtime_count=29)
(stage/'delivery.json').write_bytes(dump(newdelivery))
(stage/'migration_acceptance.json').write_bytes(dump(migration))
checked=w.load_inputs(data,bundle,newdelivery['input_manifest_sha256'])
assert len(checked[2])==4058 and all(g['arm']=='B3' for g,ps in checked[1])
print(json.dumps(newdelivery),flush=True)
