"""Verify the new REVEAL bundle with the actual pinned consumers."""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DELIVERY=ROOT/'Runs-management/b3_verified_patch_v1/release_20261108_v7_reveal/delivery'


def actual():
    spec=importlib.util.spec_from_file_location('reveal_io',DELIVERY/'b3_delivery_runtime.py')
    io=importlib.util.module_from_spec(spec);spec.loader.exec_module(io)
    manifest=json.loads((DELIVERY.parent/'release_manifest.json').read_text(encoding='utf-8'))
    for name,h in manifest['files_sha256'].items():assert hashlib.sha256((DELIVERY/name).read_bytes()).hexdigest()==h
    root=io.load_input_root(DELIVERY/'inference_input_manifest.json',manifest['files_sha256']['inference_input_manifest.json'])
    bm,rows,members=io.validate_bundle(DELIVERY/root['bundle_filename'],root)
    return io,root,rows,members


def test_full_reveal_labels_prompts_and_budgets():
    io,root,rows,members=actual()
    assert root['scope']=={'arm':'B3','dataset':'reveal','split':'validation','seed':42,'count':2273}
    raw=ROOT/'01_Author_Baseline_Unified/output/research_freeze_20261101/reveal/validation_raw.jsonl'
    labels={r['id']:r['target'] for l in raw.read_text(encoding='utf-8').splitlines() if (r:=json.loads(l))}
    assert len(rows)==2273 and {r['id'] for r in rows}==set(labels)
    census=[json.loads(l) for l in members['audited_census.jsonl'].decode('utf-8').splitlines()]
    assert len(census)==2273
    for r,c in zip(rows,census):
        assert r['id']==c['target_id'] and r['label']==labels[r['id']]
        assert r['prompt']==c['prompt'] and io.sha(r['prompt'].encode('utf-8'))==r['prompt_sha256']
        assert c['status']=='RENDERED' and c['figure6_order_compliant'] is True and c['target_label_in_prompt'] is False
        assert c['chat_tokens']+64<=8192
        assert c['token_audit']['code']<=3000 and c['token_audit']['graph']<=1500 and c['token_audit']['demo']<=1500


def test_actual_reveal_notebook_loader_both_modes(tmp_path):
    io,root,rows,members=actual()
    n=json.loads((DELIVERY/'notebook.ipynb').read_text(encoding='utf-8'))
    for mode in ['zip','unpacked']:
        base=tmp_path/mode;inputs=base/'input';inputs.mkdir(parents=True)
        if mode=='zip':(inputs/root['bundle_filename']).write_bytes((DELIVERY/root['bundle_filename']).read_bytes())
        else:
            folder=inputs/'dataset';folder.mkdir()
            for name,raw in members.items():
                p=folder/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
        env={k:getattr(io,k) for k in ['discover_bundle','validate_bundle','write_zip','restore_checkpoint','checked_records']}
        env.update(Path=Path,INPUT_ROOT=root,KAGGLE_INPUT_ROOT=inputs,BUNDLE_WORK=base/'work',BUNDLE_NAME=root['bundle_filename'],
            OUT_ROOT=base/'output',CHECKPOINT_INPUT_PATH=None,RESUME_REQUIRED=False,note=lambda *a:None,digest=lambda p:io.sha(Path(p).read_bytes()))
        exec(compile(''.join(n['cells'][4]['source']),'actual_reveal_notebook_cell4','exec'),env)
        assert len(env['prompts_records'])==2273 and env['records_done']==0
        assert io.sha(env['bundle_file'].read_bytes())==root['bundle_sha256']


def test_config_and_shared_runtime_identity():
    io,root,rows,members=actual()
    v6=ROOT/'Runs-management/b3_verified_patch_v1/release_20261108_v6/delivery'
    for name in ['b3_delivery_runtime.py','grace_runtime_contract.py','inference_runtime_lock.json']:
        assert (DELIVERY/name).read_bytes()==(v6/name).read_bytes()
    n=json.loads((DELIVERY/'notebook.ipynb').read_text(encoding='utf-8'))
    env={'Path':Path,'RUNTIME':json.loads((DELIVERY/'inference_runtime_lock.json').read_text(encoding='utf-8')),'note':lambda *a:None}
    exec(''.join(n['cells'][3]['source']),env)
    assert (env['ARM'],env['DATASET'],env['SPLIT'],env['SEED'],env['EXPECTED_COUNT'])==('B3','reveal','validation',42,2273)
    assert env['BUNDLE_NAME']==root['bundle_filename'] and 'reveal' in str(env['OUT_ROOT'])
    metadata=json.loads((DELIVERY/'kernel-metadata.json').read_text(encoding='utf-8'))
    assert metadata['machine_shape']=='NvidiaTeslaT4' and metadata['kernel_sources']==['huuhieu3333/qwen3coder30b-prepare-notebook']
