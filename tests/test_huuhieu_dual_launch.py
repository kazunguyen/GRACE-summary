"""Actual checkpoint restore/dual-input preflight. No network or GPU."""
import ast
import hashlib
import importlib.util
import json
import sys
import time
import zipfile
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import b3_dual_runtime_coordinator as dual
import b3_delivery_runtime as io
import launch_huuhieu_b1shuf_b3_20261108 as launch


def roots():
    base=ROOT/'Runs-management/b3_verified_patch_v1'
    return {ds:{'path':str(base/version/'delivery/inference_input_manifest.json'),
        'sha256':io.sha((base/version/'delivery/inference_input_manifest.json').read_bytes())}
        for ds,version in [('devign','release_20261108_v6'),('reveal','release_20261108_v7_reveal')]}


def test_b1_actual_restore_both_modes_and_worker_identity(tmp_path):
    stage=launch.BASE/'b1_shuf';n=json.loads((stage/'kernel/notebook.ipynb').read_text(encoding='utf-8'))
    assert 'MAX_RUNTIME_HOURS = 9' in ''.join(n['cells'][2]['source'])
    assert 'scipy==1.16.3' in ''.join(n['cells'][4]['source'])
    worker=next(node.args[0].value for node in ast.walk(ast.parse(''.join(n['cells'][7]['source'])))
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr=='write_text')
    assert hashlib.sha256(worker.encode()).hexdigest()==json.loads((stage/'delivery.json').read_text(encoding='utf-8'))['worker_sha256']
    source=''.join(n['cells'][3]['source'])
    checkpoint=stage/'dataset/b1_shuf_locked_20261108_checkpoint.zip'
    for mode in ['zip','unpacked']:
        base=tmp_path/mode;inputs=base/'input';inputs.mkdir(parents=True)
        if mode=='zip':(inputs/checkpoint.name).write_bytes(checkpoint.read_bytes())
        else:
            with zipfile.ZipFile(checkpoint) as z:z.extractall(inputs/'checkpoint')
        env={'Path':Path,'hashlib':hashlib,'json':json,'zipfile':zipfile,'shutil':__import__('shutil'),
            'KAGGLE_INPUT_ROOT':inputs,'OUT_ROOT':base/'out','CHECKPOINT_NAME':checkpoint.name,
            'MANIFEST_SHA':'1f008abc6f0d9928fca6c5684d9b49f508182a733acb12f0d8bbb03d11d3a70c',
            'EXPECTED_CONTRACT_SHA256':'85d8770839f80260cdc7c27b27b6cce6bf8815675c8593db68fb102589c5cbd6','note':lambda *a:None}
        exec(compile(source,'actual_b1_restore','exec'),env)
        with zipfile.ZipFile(checkpoint) as z:
            assert all((base/'out'/name).read_bytes()==z.read(name) for name in z.namelist() if not name.endswith('/'))
        assert sum(len(p.read_text(encoding='utf-8').splitlines()) for p in (base/'out').rglob('records.jsonl'))==6416


@pytest.mark.parametrize('mode',['zip','unpacked'])
def test_prepare_two_actual_input_roots(mode,tmp_path):
    definitions=roots();inputs=tmp_path/'inputs';inputs.mkdir()
    for ds,ref in definitions.items():
        folder=Path(ref['path']).parent;root=io.load_input_root(ref['path'],ref['sha256'])
        source=folder/root['bundle_filename']
        if mode=='zip':(inputs/source.name).write_bytes(source.read_bytes())
        else:
            with zipfile.ZipFile(source) as z:z.extractall(inputs/ds)
    prepared=dual.prepare(inputs,tmp_path/'prepared',definitions)
    assert [(ds,len(rows)) for ds,_,rows,_,_ in prepared]==[('devign',2732),('reveal',2273)]
    for ds,root,rows,bundle,ref in prepared:
        assert bundle.is_dir()
        io.validate_bundle(bundle,root)


def test_snapshot_preserves_live_bytes_and_complete_prefix(tmp_path):
    root=io.load_input_root(roots()['devign']['path'],roots()['devign']['sha256'])
    folder=Path(roots()['devign']['path']).parent
    _,rows,_=io.validate_bundle(folder/root['bundle_filename'],root)
    spec=importlib.util.spec_from_file_location('test_fixture',ROOT/'tests/test_b3_delivery_v6.py')
    fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)
    run=fixture.fixture_records(tmp_path/'live',root,rows)
    records=run/'records.jsonl';complete=records.read_bytes();live=complete+b'{"id":'
    records.write_bytes(live)
    checkpoint=tmp_path/'checkpoint.zip'
    assert dual.snapshot(tmp_path/'live',checkpoint,root,rows)==1
    assert records.read_bytes()==live
    io.restore_checkpoint(checkpoint,tmp_path/'restored',root,rows)
    assert (tmp_path/'restored/seed_42/devign/validation/records.jsonl').read_bytes()==complete


@pytest.mark.parametrize('exitcode',[0,1])
def test_incomplete_or_failed_first_child_does_not_start_second(tmp_path,monkeypatch,exitcode):
    definitions=roots();prepared=[]
    for ds,ref in definitions.items():
        root=io.load_input_root(ref['path'],ref['sha256'])
        folder=Path(ref['path']).parent
        _,rows,_=io.validate_bundle(folder/root['bundle_filename'],root)
        prepared.append((ds,root,rows,folder/root['bundle_filename'],ref))
    calls=[]
    class Child:
        def __init__(self,cmd,**kwargs):calls.append((cmd,kwargs))
        def poll(self):return exitcode
        def wait(self,**kwargs):return exitcode
    monkeypatch.setattr(dual.subprocess,'Popen',Child)
    args=(prepared,tmp_path/'unused.gguf',tmp_path/'out',time.time()+1000,tmp_path/'worker.py',tmp_path/'active_root.json',tmp_path/'logs')
    if exitcode:
        with pytest.raises(RuntimeError,match='failed'):dual.run(*args)
    else:assert dual.run(*args)['state']=='checkpointed'
    assert len(calls)==1 and 'devign' in calls[0][0] and not (tmp_path/'out/reveal').exists()


def test_notebooks_use_same_owner_shape_timeout_and_no_extra_arms():
    for name in ['b1_shuf','b3_dual']:
        stage=launch.BASE/name;meta=json.loads((stage/'kernel/kernel-metadata.json').read_text(encoding='utf-8'))
        assert meta['id'].startswith('huuhieu3333/') and meta['machine_shape']=='NvidiaTeslaT4'
        assert meta['session_timeout_seconds']==32400 and meta['kernel_sources']==['huuhieu3333/qwen3coder30b-prepare-notebook']
        for c in json.loads((stage/'kernel/notebook.ipynb').read_text(encoding='utf-8'))['cells']:
            if c['cell_type']=='code':ast.parse(''.join(c['source']))
