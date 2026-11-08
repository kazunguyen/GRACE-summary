"""Package both accepted B3 validation inputs locally; do not publish ZIP to git."""
import hashlib
import importlib.util
import json
from pathlib import Path
from zipfile import ZipFile

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'Runs-management/b3_verified_patch_v1'
TARGET=ROOT/'Runs-management/local_deliveries/B3_NEW_ALGORITHM_PROMPTS_DEVIGN_REVEAL_20261108.zip'


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    if TARGET.exists():raise ValueError('Handoff ZIP exists; preserve it and version any replacement')
    members={};datasets={}
    for ds,version in [('devign','release_20261108_v6'),('reveal','release_20261108_v7_reveal')]:
        folder=BASE/version/'delivery'
        manifest=json.loads((folder.parent/'release_manifest.json').read_text(encoding='utf-8'))
        for name,h in manifest['files_sha256'].items():
            raw=(folder/name).read_bytes()
            if sha(raw)!=h:raise ValueError('Release hash mismatch: '+name)
            members[ds+'/'+name]=raw
        spec=importlib.util.spec_from_file_location('handoff_'+ds,folder/'b3_delivery_runtime.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        root=module.load_input_root(folder/'inference_input_manifest.json',manifest['files_sha256']['inference_input_manifest.json'])
        _,rows,verified=module.validate_bundle(folder/root['bundle_filename'],root)
        members[ds+'/preview/prompts.jsonl']=verified['prompts.jsonl']
        datasets[ds]={'input_release':version,'count':len(rows),'scope':root['scope'],
            'input_root_sha256':manifest['files_sha256']['inference_input_manifest.json'],
            'runtime_contract_sha256':root['runtime_contract_sha256'],'bundle_filename':root['bundle_filename']}
    members['README.md']=(
        '# B3 new algorithm: local prompt handoff\n\n'
        'Devign validation2732 + REVEAL validation2273; B3 seed42 only. '
        'Both have genuine admitted reviews and CPU preflight. Native GPU acceptance, '
        'full validation scores, new thresholds and test remain pending.\n\n'
        'This is a LOCAL HANDOFF archive, not a single combined Kaggle input dataset. '
        'Use each dataset-specific original ZIP and its own notebook/input root. '
        'Do not mount both input roots into a notebook that expects exactly one. '
        'preview/prompts.jsonl is for inspection, not a replacement runtime input.\n\n'
        'Use the prepared official SDK launch requests in repository acceptance reports. '
        'The Devign base metadata template needs the model source/shape overlay. '
        'Check current quota; no native GPU run has been launched for these releases.\n'
    ).encode('utf-8')
    inventory={'method_id':'b3-verified-patch-v1','datasets':datasets,
        'files_sha256':{name:sha(raw) for name,raw in sorted(members.items())},
        'not_for_git':True,'native_runtime':'NOT_EVALUATED','scores':'NOT_STARTED'}
    members['HANDOFF_MANIFEST.json']=(json.dumps(inventory,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    TARGET.parent.mkdir(parents=True,exist_ok=True)
    module.write_zip(TARGET,members)
    with ZipFile(TARGET) as z:
        if z.testzip() is not None:raise ValueError('ZIP CRC failure')
        for name,raw in members.items():
            if z.read(name)!=raw:raise ValueError('ZIP member mismatch')
    receipt={'local_zip':str(TARGET.relative_to(ROOT)),'zip_sha256':sha(TARGET.read_bytes()),
        'bytes':TARGET.stat().st_size,'datasets':datasets,'zip_crc_and_all_members':'PASS','push_zip_to_git':False}
    (BASE/'B3_PROMPT_HANDOFF_MANIFEST_20261108.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt,ensure_ascii=True,indent=2))


if __name__=='__main__':main()
