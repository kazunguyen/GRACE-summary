"""Accept Kaggle's nested extraction of the outer and inner test ZIPs."""
import hashlib
import io
import json
from pathlib import Path
import zipfile

HERE = Path(__file__).parent
DELIVERY = HERE / 'test_delivery_20261107'

def patch_notebook(nb):
    with zipfile.ZipFile(DELIVERY / 'grace_b2_rand_test_seeds_42_43_bundle.zip') as outer:
        hashes = {n: hashlib.sha256(outer.read(n)).hexdigest()
                  for n in outer.namelist() if not n.endswith('/')}
        unpacked_hashes = {}
        for name in outer.namelist():
            if name.endswith('.zip'):
                with zipfile.ZipFile(io.BytesIO(outer.read(name))) as inner:
                    unpacked_hashes[name] = {member: hashlib.sha256(inner.read(member)).hexdigest()
                                             for member in inner.namelist() if not member.endswith('/')}
    for cell in nb['cells']:
        text = ''.join(cell['source'])
        if 'archives = sorted(KAGGLE_INPUT_ROOT.rglob(BUNDLE_NAME))' not in text:
            continue
        start = text.rindex('# Kaggle may', 0, text.index('archives = sorted(KAGGLE_INPUT_ROOT.rglob(BUNDLE_NAME))'))
        end = text.index('\nbundles = {}', start)
        replacement = '''# Kaggle may retain the inner ZIPs or recursively expand them.
expected_member_hashes = EXPECTED_HASHES
expected_unpacked_hashes = EXPECTED_UNPACKED_HASHES
archives = sorted(KAGGLE_INPUT_ROOT.rglob(BUNDLE_NAME))
if len(archives) > 1:
    raise ValueError(f'Multiple delivery archives found: {archives}')
payloads_all = {}
if archives:
    if hash_bytes(archives[0].read_bytes()) != BUNDLE_SHA256:
        raise ValueError('Test bundle SHA-256 mismatch')
    with zipfile.ZipFile(archives[0]) as outer:
        payloads_all = {name: outer.read(name) for name in expected_member_hashes}
else:
    selected_paths = {}
    missing_or_mismatched = {}
    # These two outer-level files survive Kaggle extraction unchanged.
    for name in ('delivery_manifest.json', 'threshold_lock.json'):
        digest = expected_member_hashes[name]
        candidates = sorted({p for p in KAGGLE_INPUT_ROOT.rglob(name) if p.is_file()})
        valid = [p for p in candidates if hash_bytes(p.read_bytes()) == digest]
        if valid:
            payloads_all[name] = valid[0].read_bytes()
            selected_paths[name] = str(valid[0])
        else:
            missing_or_mismatched[name] = [str(p) for p in candidates]
    for name, member_hashes in expected_unpacked_hashes.items():
        candidates = sorted({p for p in KAGGLE_INPUT_ROOT.rglob(Path(name).name) if p.is_file()})
        zipped = [p for p in candidates if hash_bytes(p.read_bytes()) == expected_member_hashes[name]]
        if zipped:
            payloads_all[name] = zipped[0].read_bytes()
            selected_paths[name] = str(zipped[0])
            continue
        parts = Path(name).parts
        seed_dir, inner_dir = parts[0], Path(parts[-1]).stem
        manifests = [p for p in KAGGLE_INPUT_ROOT.rglob('bundle_manifest.json')
                     if p.parent.name == inner_dir and p.parent.parent.name == seed_dir]
        unpacked = []
        for manifest_path in manifests:
            folder = manifest_path.parent
            member_paths = {member: folder / member for member in member_hashes}
            if all(path.is_file() and hash_bytes(path.read_bytes()) == member_hashes[member]
                   for member, path in member_paths.items()):
                unpacked.append((folder, {member: path.read_bytes() for member, path in member_paths.items()}))
        if unpacked:
            payloads_all[name] = unpacked[0][1]
            selected_paths[name] = str(unpacked[0][0]) + ' (recursively extracted ZIP)'
        else:
            missing_or_mismatched[name] = [str(p) for p in candidates + manifests]
    if missing_or_mismatched:
        visible = sorted(str(p) for p in KAGGLE_INPUT_ROOT.rglob('*') if p.is_file())
        raise ValueError('Kaggle delivery is incomplete or does not match frozen hashes. '
                         f'Missing/mismatched members and candidates: {missing_or_mismatched}. '
                         f'Visible files (first 100): {visible[:100]}')
    print(f'Using Kaggle-mounted delivery members: {selected_paths}')
for name, digest in expected_member_hashes.items():
    if isinstance(payloads_all[name], bytes) and hash_bytes(payloads_all[name]) != digest:
        raise ValueError(f'Delivery member SHA-256 mismatch: {name}')
payloads = {spec['name']: payloads_all[spec['name']] for spec in SETS}
'''.replace('EXPECTED_HASHES', repr(hashes)).replace('EXPECTED_UNPACKED_HASHES', repr(unpacked_hashes))
        text = text[:start] + replacement + text[end:]
        text = text.replace('bundles = {}\nexpected = {}\nfor spec in SETS:',
                            'bundles = {}\nexpected = {}\nlocked_thresholds = {}\nfor spec in SETS:', 1)
        old_parser = '''    raw = payloads[spec['name']]
    if hash_bytes(raw) != spec['sha256']:
        raise ValueError(f'Inner test bundle hash mismatch: {spec["name"]}')
    bundle_path = BUNDLE_WORK / Path(spec['name']).name
    bundle_path.write_bytes(raw)
    with zipfile.ZipFile(bundle_path) as inner:
        prompt_bytes = inner.read('prompts.jsonl')
        manifest = json.loads(inner.read('bundle_manifest.json'))
        lock_payload = json.loads(inner.read('threshold_lock.json'))
'''
        new_parser = '''    raw = payloads[spec['name']]
    bundle_path = BUNDLE_WORK / Path(spec['name']).name
    if isinstance(raw, dict):
        # Kaggle recursively extracted this inner ZIP. The discovery cell already
        # checked every member byte against hashes from the original frozen ZIP.
        inner_members = raw
        with zipfile.ZipFile(bundle_path, 'w', compression=zipfile.ZIP_DEFLATED) as normalized:
            for member, member_bytes in inner_members.items():
                normalized.writestr(member, member_bytes)
    else:
        if hash_bytes(raw) != spec['sha256']:
            raise ValueError(f'Inner test bundle hash mismatch: {spec["name"]}')
        bundle_path.write_bytes(raw)
        with zipfile.ZipFile(bundle_path) as inner:
            inner_members = {member: inner.read(member) for member in expected_unpacked_hashes[spec['name']]}
    prompt_bytes = inner_members['prompts.jsonl']
    manifest = json.loads(inner_members['bundle_manifest.json'])
    lock_payload = json.loads(inner_members['threshold_lock.json'])
    seal = lock_payload.get('locked_sha256')
    actual = hash_bytes(json.dumps({k:v for k,v in lock_payload.items() if k!='locked_sha256'},sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())
    if seal != actual or seal != THRESHOLD_LOCK_SHA256 or manifest.get('threshold_lock_sha256') != seal:
        raise ValueError('Threshold lock integrity mismatch')
    lock_key = f'B2-rand/{seed}/{ds}'
    entry = lock_payload['entries'][lock_key]
    locked_thresholds[seed, ds] = entry['tau_star']
    if (manifest.get('arm'),manifest.get('seed'),manifest.get('split')) != ('B2-rand',seed,'test'):
        raise ValueError('Wrong test manifest identity')
    if manifest.get('tau_star') != entry['tau_star'] or manifest.get('model_sha256') != MODEL_SHA256:
        raise ValueError('Test bundle threshold/model does not match validation lock')
    if hash_bytes(prompt_bytes) != manifest['prompts_sha256']:
        raise ValueError('Prompt payload hash mismatch')
    rows = [json.loads(line) for line in prompt_bytes.decode('utf-8').splitlines() if line.strip()]
'''
        if old_parser in text:
            text = text.replace(old_parser, new_parser, 1)
            duplicate_tail = '''        seal = lock_payload.get('locked_sha256')
        actual = hash_bytes(json.dumps({k:v for k,v in lock_payload.items() if k!='locked_sha256'},sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())
        if seal != actual or seal != THRESHOLD_LOCK_SHA256 or manifest.get('threshold_lock_sha256') != seal:
            raise ValueError('Threshold lock integrity mismatch')
        lock_key = f'B2-rand/{seed}/{ds}'
        entry = lock_payload['entries'][lock_key]
        if (manifest.get('arm'),manifest.get('seed'),manifest.get('split')) != ('B2-rand',seed,'test'):
            raise ValueError('Wrong test manifest identity')
        if manifest.get('tau_star') != entry['tau_star'] or manifest.get('model_sha256') != MODEL_SHA256:
            raise ValueError('Test bundle threshold/model does not match validation lock')
        if hash_bytes(prompt_bytes) != manifest['prompts_sha256']:
            raise ValueError('Prompt payload hash mismatch')
        rows = [json.loads(line) for line in prompt_bytes.decode('utf-8').splitlines() if line.strip()]
'''
            if duplicate_tail not in text:
                raise ValueError('Expected old inner ZIP parsing tail not found')
            text = text.replace(duplicate_tail, '', 1)
        elif 'inner_members = raw' in text:
            text = text.replace('bundles = {}\nexpected = {}\nfor spec in SETS:',
                                'bundles = {}\nexpected = {}\nlocked_thresholds = {}\nfor spec in SETS:', 1)
            text = text.replace('        inner_members = raw\n',
                                '        inner_members = raw\n        with zipfile.ZipFile(bundle_path, \'w\', compression=zipfile.ZIP_DEFLATED) as normalized:\n            for member, member_bytes in inner_members.items():\n                normalized.writestr(member, member_bytes)\n', 1)
            text = text.replace("    entry = lock_payload['entries'][lock_key]\n",
                                "    entry = lock_payload['entries'][lock_key]\n    locked_thresholds[seed, ds] = entry['tau_star']\n", 1)
        else:
            raise ValueError('Expected inner bundle parser not found')
        cell['source'] = text.splitlines(keepends=True)
    for cell in nb['cells']:
        if cell['cell_type'] != 'code':
            continue
        text = ''.join(cell['source'])
        old_summary_thresholds = "'thresholds': {ds: json.loads(zipfile.ZipFile(bundles[PROMPT_SEED, ds]).read('threshold_lock.json'))['entries'][f'B2-rand/{PROMPT_SEED}/{ds}']['tau_star'] for ds in ('devign','reveal')}"
        new_summary_thresholds = "'thresholds': {ds: locked_thresholds.get((PROMPT_SEED, ds)) for ds in ('devign','reveal')}"
        if old_summary_thresholds in text:
            cell['source'] = text.replace(old_summary_thresholds, new_summary_thresholds, 1).splitlines(keepends=True)
    return nb

if __name__ == '__main__':
    for path in DELIVERY.glob('*.ipynb'):
        nb = patch_notebook(json.loads(path.read_text(encoding='utf-8')))
        for i, cell in enumerate(nb['cells']):
            if cell['cell_type'] == 'code':
                source = ''.join(cell['source'])
                if source.startswith('%%writefile'):
                    source = source.split('\n', 1)[1]
                elif source.startswith('%%') or any(line.startswith('!') for line in source.splitlines()):
                    continue
                compile(source, f'{path.name}:cell{i}', 'exec')
        path.write_text(json.dumps(nb, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        print(path.name)
    manifest_path = DELIVERY / 'delivery_manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    manifest['notebooks'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in DELIVERY.glob('*.ipynb')}
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
