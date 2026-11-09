"""Integration checks against shipped B3 v6 code and actual input bundle."""
import ast
import copy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[1]
DELIVERY=ROOT/'Runs-management/b3_verified_patch_v1/release_20261108_v6/delivery'
spec=importlib.util.spec_from_file_location('b3_v6_io',DELIVERY/'b3_delivery_runtime.py')
io=importlib.util.module_from_spec(spec)
spec.loader.exec_module(io)


@pytest.fixture(scope='module')
def actual():
    release=json.loads((DELIVERY.parent/'release_manifest.json').read_text(encoding='utf-8'))
    root=io.load_input_root(DELIVERY/'inference_input_manifest.json',release['files_sha256']['inference_input_manifest.json'])
    bm,rows,members=io.validate_bundle(DELIVERY/root['bundle_filename'],root)
    return root,bm,rows,members


def unpack(folder,members):
    folder.mkdir(parents=True)
    for name,raw in members.items():
        p=folder/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)


def test_actual_notebook_loader_zip_and_unpacked(actual,tmp_path):
    root,bm,rows,members=actual
    notebook=json.loads((DELIVERY/'notebook.ipynb').read_text(encoding='utf-8'))
    source=''.join(notebook['cells'][4]['source'])
    for mode in ['zip','unpacked']:
        base=tmp_path/mode;inputs=base/'input';inputs.mkdir(parents=True)
        if mode=='zip':(inputs/root['bundle_filename']).write_bytes((DELIVERY/root['bundle_filename']).read_bytes())
        else:unpack(inputs/'dataset',members)
        env={k:getattr(io,k) for k in ['discover_bundle','validate_bundle','write_zip','restore_checkpoint','checked_records']}
        env.update(Path=Path,INPUT_ROOT=root,KAGGLE_INPUT_ROOT=inputs,BUNDLE_WORK=base/'bundle',
            BUNDLE_NAME=root['bundle_filename'],OUT_ROOT=base/'output',CHECKPOINT_INPUT_PATH=None,
            RESUME_REQUIRED=False,note=lambda *a:None,digest=lambda p:io.sha(Path(p).read_bytes()))
        exec(compile(source,'actual_notebook_cell4','exec'),env)
        assert env['records_done']==0 and len(env['prompts_records'])==2732
        assert io.sha(env['bundle_file'].read_bytes())==root['bundle_sha256']
    labels=json.loads(members['labels.json'])
    census=[json.loads(l) for l in members['audited_census.jsonl'].decode().splitlines()]
    assert all((r['id'],r['label'],r['prompt'])==(c['target_id'],labels[c['target_id']],c['prompt']) for r,c in zip(rows,census))


def test_external_pin_tamper_and_ambiguous_roots(actual,tmp_path):
    root,bm,rows,members=actual
    changed=copy.deepcopy(members)
    changed['prompts.jsonl']+=b'\n'
    fake=dict(bm);fake['prompts_sha256']=io.sha(changed['prompts.jsonl'])
    fake['manifest_seal_sha256']=io.seal(fake,'manifest_seal_sha256')
    changed['bundle_manifest.json']=io.encoded(fake)
    unpack(tmp_path/'bad',changed)
    with pytest.raises(ValueError,match='SHA-256'):io.validate_bundle(tmp_path/'bad',root)
    with pytest.raises(ValueError,match='pin mismatch'):io.load_input_root(DELIVERY/'inference_input_manifest.json','0'*64)
    unpack(tmp_path/'a',members);unpack(tmp_path/'b',members)
    with pytest.raises(ValueError,match='exactly one'):io.discover_bundle(tmp_path,root)
    (tmp_path/'a/evidence/review_hieu.json').unlink()
    with pytest.raises(ValueError,match='members'):io.validate_bundle(tmp_path/'a',root)


def fixture_records(folder,root,rows):
    scope=root['scope'];run=folder/'seed_42/devign/validation';run.mkdir(parents=True)
    prov=folder/'runtime_provenance/session';prov.mkdir(parents=True)
    log=b'fixture native log, not actual GPU evidence'
    (prov/'model_load_offload.log').write_bytes(log)
    (prov/'runtime_provenance.json').write_bytes(io.encoded({'runtime_contract_sha256':root['runtime_contract_sha256'],
        'runner_sha256':root['code_sha256']['kaggle_inference.py'],'offload_log_sha256':io.sha(log)}))
    (run/'run_manifest.json').write_bytes(io.encoded({'b3_input_identity':io.run_identity(root)}))
    row={k:rows[0][k] for k in ['id','dataset','split','label','prompt_sha256']}
    row.update(arm='B3',seed=42,model_sha256=root['model_sha256'],runtime_contract_sha256=root['runtime_contract_sha256'],
        s=0.5,logprob_0=-1.,logprob_1=-1.,valid=True,runtime_provenance='runtime_provenance/session/runtime_provenance.json')
    (run/'records.jsonl').write_bytes((json.dumps(row)+'\n').encode('utf-8'))
    return run


def test_checkpoint_zip_unpacked_and_identity(actual,tmp_path):
    root,_,rows,_=actual
    run=fixture_records(tmp_path/'original',root,rows)
    original=(run/'records.jsonl').read_bytes()
    checkpoint=tmp_path/'checkpoint.zip'
    io.make_checkpoint(tmp_path/'original',checkpoint,root,rows)
    io.restore_checkpoint(checkpoint,tmp_path/'restored',root,rows)
    assert io.checked_records(tmp_path/'restored',root,rows)==1
    assert (tmp_path/'restored/seed_42/devign/validation/records.jsonl').read_bytes()==original
    unpack(tmp_path/'unpacked',io.read_members(checkpoint))
    io.restore_checkpoint(tmp_path/'unpacked',tmp_path/'restored2',root,rows)
    assert io.checked_records(tmp_path/'restored2',root,rows)==1
    for key,value in [('method_id','old-method'),('pool_sha256','wrong'),('runtime_contract_sha256','wrong'),('model_sha256','wrong')]:
        wrong=dict(root);wrong[key]=value
        with pytest.raises(ValueError,match='identity'):io.restore_checkpoint(checkpoint,tmp_path/'reject',wrong,rows)
        assert not (tmp_path/'reject').exists()
    (run/'run_manifest.json').unlink()
    with pytest.raises(ValueError,match='without run manifest'):io.checked_records(tmp_path/'original',root,rows)


def test_checkpoint_corruption_and_paths(actual,tmp_path):
    root,_,rows,_=actual
    run=fixture_records(tmp_path/'original',root,rows)
    raw=(run/'records.jsonl').read_bytes()
    (run/'records.jsonl').write_bytes(raw+raw)
    with pytest.raises(ValueError,match='Duplicate'):io.checked_records(tmp_path/'original',root,rows)
    (run/'records.jsonl').write_bytes(raw)
    checkpoint=tmp_path/'good.zip';io.make_checkpoint(tmp_path/'original',checkpoint,root,rows)
    members=io.read_members(checkpoint);members['seed_42/devign/validation/records.jsonl']+=b' '
    io.write_zip(tmp_path/'bad.zip',members)
    with pytest.raises(ValueError,match='SHA-256'):io.restore_checkpoint(tmp_path/'bad.zip',tmp_path/'badout',root,rows)
    for bad in ['../escape','/absolute','a/../../escape','C:/escape','a\\b']:
        with pytest.raises(ValueError):io.checked_name(bad)


def test_cross_dataset_and_scoring(actual,tmp_path):
    root,_,rows,_=actual
    wrong=copy.deepcopy(root);wrong['scope']['dataset']='reveal'
    with pytest.raises(ValueError,match='scope'):io.validate_bundle(DELIVERY/root['bundle_filename'],wrong)
    run=fixture_records(tmp_path/'original',root,rows)
    row=json.loads((run/'records.jsonl').read_text(encoding='utf-8'));row['s']=0.9
    (run/'records.jsonl').write_bytes((json.dumps(row)+'\n').encode('utf-8'))
    with pytest.raises(ValueError,match='Score/logprob'):io.checked_records(tmp_path/'original',root,rows)
    # Test actual shipped worker function, not a reimplementation.
    import numpy as np
    import math
    worker=(DELIVERY/'kaggle_inference.py').read_text(encoding='utf-8')
    node=next(n for n in ast.parse(worker).body if isinstance(n,ast.FunctionDef) and n.name=='binary_scores')
    ns={'np':np,'math':math};exec(ast.get_source_segment(worker,node),ns)
    assert ns['binary_scores']([0.,0.],[0,1])['s']==0.5
    assert ns['binary_scores']([-1000.,1000.],[0,1])['s']==1.
    with pytest.raises(ValueError):ns['binary_scores']([float('nan'),0.],[0,1])


def test_shipped_helper_parser_on_native_log(actual):
    contract=json.loads((DELIVERY/'inference_runtime_lock.json').read_text(encoding='utf-8'))
    log=next((ROOT/'Runs-management/locked_continuations_20261108/b1_full/remote_output').rglob('model_load_offload.log'))
    text=log.read_text(encoding='utf-8')
    io.native_log_check(text,contract)
    assert 'native_log_check(text, c)' in (DELIVERY/'grace_runtime_contract.py').read_text(encoding='utf-8')
    for broken in [text.replace('CUDA1','CUDA0'),text.replace('49/49','40/49'),text.replace('n_ctx = 8192','n_ctx = 4096')]:
        with pytest.raises(ValueError):io.native_log_check(broken,contract)


def test_shipped_code_hashes_and_syntax(actual):
    root,_,_,_=actual
    for name,h in root['code_sha256'].items():
        raw=(DELIVERY/name).read_bytes();assert io.sha(raw)==h
        if name.endswith('.py'):ast.parse(raw.decode('utf-8'))
    n=json.loads((DELIVERY/'notebook.ipynb').read_text(encoding='utf-8'))
    for c in n['cells']:
        if c['cell_type']=='code':ast.parse(''.join(c['source']))
