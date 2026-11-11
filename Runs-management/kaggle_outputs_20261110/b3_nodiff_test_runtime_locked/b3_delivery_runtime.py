"""Fail-closed B3 delivery IO. No network, backend or frozen-data mutations."""
import hashlib
import json
import math
import os
import re
import shutil
import tempfile
import zipfile
from pathlib import Path, PurePosixPath


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(obj):
    return (json.dumps(obj, sort_keys=True, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def seal(obj, key='seal_sha256'):
    body = {k: v for k, v in obj.items() if k != key}
    return sha(json.dumps(body, sort_keys=True, ensure_ascii=False, indent=2).encode('utf-8'))


def checked_name(name):
    if not name or '\\' in name or ':' in name or '\x00' in name:
        raise ValueError('Unsafe member path')
    p = PurePosixPath(name)
    if p.is_absolute() or any(s in ('', '.', '..') for s in name.split('/')):
        raise ValueError('Unsafe member path')
    return name


def read_members(source):
    source = Path(source)
    if source.is_file():
        with zipfile.ZipFile(source) as z:
            names = z.namelist()
            if len(names) != len(set(names)):
                raise ValueError('Duplicate archive member')
            result = {}
            for info in z.infolist():
                if info.is_dir():
                    continue
                name = checked_name(info.filename)
                if (info.external_attr >> 16) & 0o170000 == 0o120000:
                    raise ValueError('Symlink archive member')
                result[name] = z.read(info)
            return result
    if not source.is_dir() or source.is_symlink():
        raise ValueError('Missing input root')
    result = {}
    for p in source.rglob('*'):
        if p.is_symlink():
            raise ValueError('Symlink input member')
        if p.is_file():
            result[checked_name(p.relative_to(source).as_posix())] = p.read_bytes()
    return result


def verify_inventory(members, expected):
    if set(members) != set(expected):
        raise ValueError('Missing/unexpected members')
    for name, h in expected.items():
        checked_name(name)
        if sha(members[name]) != h:
            raise ValueError('Member SHA-256 mismatch: ' + name)


def load_input_root(path, expected_sha):
    raw = Path(path).read_bytes()
    if sha(raw) != expected_sha:
        raise ValueError('Independent input root pin mismatch')
    root = json.loads(raw)
    if root.get('seal_sha256') != seal(root):
        raise ValueError('Input root seal mismatch')
    if root['scope']['arm'] != 'B3-nodiff' or root['scope']['split'] not in ('validation','test'):
        raise ValueError('Only B3 validation supported by this delivery')
    return root


def validate_bundle(source, root):
    if Path(source).is_file() and sha(Path(source).read_bytes()) != root['bundle_sha256']:
        raise ValueError('External bundle pin mismatch')
    members = read_members(source)
    verify_inventory(members, root['members_sha256'])
    bm = json.loads(members['bundle_manifest.json'])
    if bm.get('manifest_seal_sha256') != seal(bm, 'manifest_seal_sha256'):
        raise ValueError('Bundle seal mismatch')
    if bm['scope'] != root['scope'] or bm['method_id'] != root['method_id']:
        raise ValueError('Bundle scope/method mismatch')
    rows = [json.loads(l) for l in members['prompts.jsonl'].decode('utf-8').splitlines() if l.strip()]
    if len(rows) != root['scope']['count'] or len({r['id'] for r in rows}) != len(rows):
        raise ValueError('Census count/ID mismatch')
    for row in rows:
        if (not isinstance(row['id'], str) or row['label'] not in (0, 1)
                or type(row['label']) is not int or not row['id'].startswith(root['scope']['dataset']+':'+root['scope']['split']+':')
                or (row['dataset'], row['split']) != (root['scope']['dataset'], root['scope']['split'])
                or sha(row['prompt'].encode('utf-8')) != row['prompt_sha256']):
            raise ValueError('Invalid inference row')
    return bm, rows, members


def discover_bundle(input_dir, root):
    input_dir = Path(input_dir)
    packed = sorted(input_dir.rglob(root['bundle_filename']))
    unpacked = sorted(p.parent for p in input_dir.rglob('bundle_manifest.json'))
    candidates = packed + unpacked
    if len(candidates) != 1:
        raise ValueError('Expected exactly one packed or unpacked input root')
    validate_bundle(candidates[0], root)
    return candidates[0]


def write_zip(path, members):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for name, raw in sorted(members.items()):
            info = zipfile.ZipInfo(checked_name(name), date_time=(2026, 11, 8, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, raw)


def run_identity(root):
    return {k: root[k] for k in ('method_id', 'release_id', 'scope', 'model_sha256',
        'runtime_contract_sha256', 'tokenizer_revision', 'pool_sha256', 'prompt_content_sha256',
        'members_sha256', 'scoring', 'code_sha256')}


def checked_records(out_root, root, rows):
    out_root = Path(out_root)
    scope = root['scope']
    folder = out_root / ('seed_'+str(scope['seed'])) / scope['dataset'] / scope['split']
    records = folder/'records.jsonl'
    if not records.exists():
        return 0
    manifest = folder/'run_manifest.json'
    if not manifest.is_file():
        raise ValueError('Records without run manifest')
    identity = json.loads(manifest.read_text(encoding='utf-8'))
    if identity.get('b3_input_identity') != run_identity(root):
        raise ValueError('Checkpoint method/input/runtime identity mismatch')
    lookup = {r['id']: r for r in rows}
    seen = set()
    for line in records.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        uid = r['id']
        if uid in seen or uid not in lookup:
            raise ValueError('Duplicate/unexpected checkpoint ID')
        item = lookup[uid]
        expected = {'arm':scope['arm'], 'dataset':scope['dataset'], 'split':scope['split'],
            'seed':scope['seed'], 'model_sha256':root['model_sha256'],
            'runtime_contract_sha256':root['runtime_contract_sha256'],
            'prompt_sha256':item['prompt_sha256'], 'label':item['label'], 'valid':True}
        if any(r.get(k) != v for k,v in expected.items()):
            raise ValueError('Checkpoint row identity mismatch')
        s, lp0, lp1 = r['s'], r['logprob_0'], r['logprob_1']
        if not all(type(x) in (int, float) and math.isfinite(x) for x in (s,lp0,lp1)) or not 0 <= s <= 1:
            raise ValueError('Invalid numeric checkpoint score')
        diff = lp1-lp0
        exp_s = 1/(1+math.exp(-diff)) if diff >= 0 else math.exp(diff)/(1+math.exp(diff))
        if abs(s-exp_s) > 1e-12:
            raise ValueError('Score/logprob mismatch')
        ref = checked_name(r['runtime_provenance'])
        prov_path = out_root/ref
        if not prov_path.is_file():
            raise ValueError('Missing referenced runtime provenance')
        prov = json.loads(prov_path.read_text(encoding='utf-8'))
        if (prov.get('runtime_contract_sha256') != root['runtime_contract_sha256']
                or prov.get('runner_sha256') != root['code_sha256']['kaggle_inference.py']):
            raise ValueError('Invalid provenance identity')
        log = prov_path.parent/'model_load_offload.log'
        if not log.is_file() or sha(log.read_bytes()) != prov.get('offload_log_sha256'):
            raise ValueError('Missing/changed native evidence')
        seen.add(uid)
    return len(seen)


def make_checkpoint(out_root, target, root, rows):
    checked_records(out_root, root, rows)
    members = read_members(out_root)
    members.pop('checkpoint_manifest.json', None)
    manifest = {'identity':run_identity(root), 'files_sha256':{k:sha(v) for k,v in members.items()}}
    manifest['seal_sha256'] = seal(manifest)
    members['checkpoint_manifest.json'] = encoded(manifest)
    write_zip(target, members)


def restore_checkpoint(source, out_root, root, rows):
    out_root = Path(out_root)
    if out_root.exists():
        raise ValueError('Resume destination already exists')
    members = read_members(source)
    if 'checkpoint_manifest.json' not in members:
        raise ValueError('Missing checkpoint manifest')
    manifest = json.loads(members.pop('checkpoint_manifest.json'))
    if manifest.get('seal_sha256') != seal(manifest) or manifest['identity'] != run_identity(root):
        raise ValueError('Checkpoint seal/identity mismatch')
    verify_inventory(members, manifest['files_sha256'])
    out_root.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix='restore_', dir=out_root.parent))
    try:
        for name,raw in members.items():
            dest = staging/checked_name(name)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(raw)
        checked_records(staging, root, rows)
        os.replace(staging, out_root)
    finally:
        if staging.exists():
            shutil.rmtree(staging)


def native_log_check(text, contract):
    required = contract['gpu']['required_offloaded_layers']
    pairs = re.findall(r'offloaded\s+(\d+)\s*/\s*(\d+)\s+layers?\s+to\s+GPU', text, re.I)
    if not any(int(a) == int(b) == required for a,b in pairs):
        raise ValueError('Full GPU offload not verified')
    for field in ('n_ctx','n_batch','n_ubatch'):
        values = re.findall(r'\b'+field+r'\s*=\s*(\d+)\b', text)
        if not values or int(values[-1]) != contract['constructor'][field]:
            raise ValueError('Effective '+field+' differs from contract')
    devices = set(re.findall(r'using device CUDA(\d+)\s*\([^\n)]*\bT4\b[^\n)]*\)', text, re.I))
    devices.update(re.findall(r'Device\s+(\d+):\s+[^\n]*\bT4\b', text))
    if devices != set(map(str, range(contract['gpu']['device_count']))):
        raise ValueError('Two distinct T4 devices not verified')
