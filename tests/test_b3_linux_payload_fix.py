"""Regress actual Kaggle ZIP failure without weakening independent member pins."""
import ast
import importlib.util
import json
import sys
from pathlib import Path
from zipfile import ZipFile,ZIP_STORED

import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import b3_delivery_runtime as io
import b3_dual_runtime_coordinator as dual
import deploy_b3_lznt_linuxfix_20261109 as deploy


def definitions():
    d=json.loads((deploy.BASE/'b3_dual/delivery.json').read_text(encoding='utf-8'))
    result={}
    for ds,v in d['datasets'].items():
        result[ds]={'path':str(deploy.BASE/'b3_dual/roots'/f'{ds}.json'),'sha256':v['sha256']}
    return result


def unpack(target,members):
    target.mkdir(parents=True)
    for name,raw in members.items():
        p=target/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)


def test_actual_kaggle_recompression_is_not_a_payload_change(tmp_path,monkeypatch):
    definitions_=definitions();inputs=tmp_path/'input';inputs.mkdir()
    real=ROOT/'Runs-management/huuhieu_b1shuf_b3_launch_20261108/b3_dual/remote_output/b3_verified_bundles/b3_devign_validation_v6.zip'
    root=io.load_input_root(definitions_['devign']['path'],definitions_['devign']['sha256'])
    assert io.sha(real.read_bytes())!=root['bundle_sha256']
    members=io.read_members(real);io.verify_inventory(members,root['members_sha256'])
    unpack(inputs/'devign',members)
    rvroot=io.load_input_root(definitions_['reveal']['path'],definitions_['reveal']['sha256'])
    original=deploy.BASE/'datasets/reveal'/rvroot['bundle_filename']
    unpack(inputs/'reveal',io.read_members(original))
    def no_rezip(*a,**kw):raise AssertionError('prepare must not recompress')
    monkeypatch.setattr(io,'write_zip',no_rezip)
    prepared=dual.prepare(inputs,tmp_path/'work',definitions_)
    assert [(ds,len(rows)) for ds,_,rows,_,_ in prepared]==[('devign',2732),('reveal',2273)]
    for ds,r,rows,folder,ref in prepared:
        assert folder.is_dir();io.validate_bundle(folder,r)


def test_packed_transport_pin_and_unpacked_member_pins_still_enforced(tmp_path):
    ref=definitions()['devign'];root=io.load_input_root(ref['path'],ref['sha256'])
    original=deploy.BASE/'datasets/devign'/root['bundle_filename'];members=io.read_members(original)
    differently_packed=tmp_path/'different.zip'
    with ZipFile(differently_packed,'w',compression=ZIP_STORED) as z:
        for name,raw in members.items():z.writestr(name,raw)
    assert io.sha(differently_packed.read_bytes())!=root['bundle_sha256']
    with pytest.raises(ValueError,match='External bundle pin'):io.validate_bundle(differently_packed,root)
    members['prompts.jsonl']+=b'\n';unpack(tmp_path/'bad',members)
    with pytest.raises(ValueError,match='SHA-256'):io.validate_bundle(tmp_path/'bad',root)


def test_shipped_worker_directory_loader_and_scoring_unchanged(tmp_path):
    code=(deploy.BASE/'b3_dual/code/kaggle_inference.py').read_text(encoding='utf-8')
    original=(ROOT/'Runs-management/b3_verified_patch_v1/release_20261108_v6/delivery/kaggle_inference.py').read_text(encoding='utf-8')
    transform="'bundle_sha256': INPUT_ROOT['bundle_sha256'],\n            'bundle_transport': 'verified_member_directory_v1',"
    assert code==original.replace("'bundle_sha256': sha256(bundle),",transform,1)
    before={n.name:ast.dump(n,include_attributes=False) for n in ast.parse(original).body if isinstance(n,ast.FunctionDef)}
    after={n.name:ast.dump(n,include_attributes=False) for n in ast.parse(code).body if isinstance(n,ast.FunctionDef)}
    for name in before:
        if name!='run_batch':assert before[name]==after[name]
    ref=definitions()['devign'];root=io.load_input_root(ref['path'],ref['sha256'])
    members=io.read_members(deploy.BASE/'datasets/devign'/root['bundle_filename']);unpack(tmp_path/'verified',members)
    func=next(n for n in ast.parse(code).body if isinstance(n,ast.FunctionDef) and n.name=='load_bundle')
    env={'INPUT_ROOT':root,'validate_bundle':io.validate_bundle};exec(ast.get_source_segment(code,func),env)
    assert len(env['load_bundle'](tmp_path/'verified')[1])==2732


def test_roots_method_review_payload_and_runtime_are_preserved():
    for ds,ref in definitions().items():
        root=io.load_input_root(ref['path'],ref['sha256'])
        folder=deploy.BASE/'datasets'/ds
        _,rows,members=io.validate_bundle(folder/root['bundle_filename'],root)
        assert root['method_id']=='b3-verified-patch-v1'
        pair=json.loads(members[f'evidence/eligible_pairs.{ds}.jsonl'])
        assert len(pair['reviews'])==2 and all(r['decision']=='approve' for r in pair['reviews'])
        assert len(rows)=={'devign':2732,'reveal':2273}[ds]
        code=deploy.BASE/'b3_dual/code'
        for name,h in root['code_sha256'].items():assert io.sha((code/name).read_bytes())==h
        assert json.loads((code/'inference_runtime_lock.json').read_bytes())['constructor']['tensor_split'] is None
