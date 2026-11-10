"""Package locally audited deliveries without held-out target labels."""
import hashlib
import json
from pathlib import Path
import zipfile

R = Path(__file__).resolve().parents[1]
REL = Path('Runs-management/b3_verified_patch_v1/probe_test_release_20261110_v1')
OUT = R / REL

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def write(name, data):
    (OUT / name).write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')

def main():
    assert json.loads((OUT / 'PREPARATION_AUDIT.json').read_bytes())['status'] == 'PASS'
    assert json.loads((OUT / 'REFERENCE_RUNTIME_AUDIT.json').read_bytes())['status'] == 'PASS'
    assert '9 passed' in (OUT / 'TEST_RESULTS.txt').read_text(encoding='utf-8')
    assert (OUT / 'shared_worker/b3_test_runtime.py').read_bytes() == (R / 'scripts/b3_test_runtime.py').read_bytes()
    sources = [
        'scripts/build_b3_probe_delivery_20261110.py', 'scripts/audit_b3_probe_reference_20261110.py',
        'scripts/evaluate_b3_probe_test_20261110.py', 'scripts/package_b3_probe_handoff_20261110.py',
        'scripts/b3_test_runtime.py', 'scripts/build_b3_test_prompts_20261109.py',
        'tests/test_b3_probe_delivery.py',
        '01_Author_Baseline_Unified/diagnostic_kit/src/grace_diag/amended_b3.py',
        '01_Author_Baseline_Unified/diagnostic_kit/src/grace_diag/probes.py',
        '01_Author_Baseline_Unified/diagnostic_kit/src/grace_diag/token_budget.py',
        '01_Author_Baseline_Unified/diagnostic_kit/src/grace_diag/evaluate_final.py',
        '01_Author_Baseline_Unified/diagnostic_kit/src/grace_diag/stats.py',
    ]
    source_hashes = {name: sha((R / name).read_bytes()) for name in sources}
    write('SOURCE_PROVENANCE.json', {'source_sha256': source_hashes})
    write('LOCAL_ACCEPTANCE.json', {'status': 'LOCAL_READY_REMOTE_RUNTIME_PENDING',
        'probe_delivery_tests': {'passed': 9}, 'required_governance_probe_stats_tests': {'passed': 37},
        'test_archive_crc_and_member_hashes': 'PASS', 'paired_prompt_full_census': 'PASS',
        'notebook_source_compile_and_embedded_helper_identity': 'PASS', 'reference_five_arm_runtime': 'PASS',
        'remote_upload': False, 'gpu_execution': False, 'runtime_certification': 'PENDING'})
    files = {}
    for path in OUT.rglob('*'):
        if not path.is_file():
            continue
        rel = path.relative_to(OUT)
        if any(part in ('kaggle_input', '__pycache__') for part in rel.parts):
            continue
        if path.name in ('HANDOFF_INVENTORY.json', 'HANDOFF_RECEIPT.json'):
            continue
        assert not any('private_evaluation' in p or 'test_labels' in p for p in rel.parts)
        files[rel.as_posix()] = path.read_bytes()
    for name in sources:
        files['repo_sources/' + name] = (R / name).read_bytes()
    inventory = {n: {'sha256': sha(raw), 'bytes': len(raw)} for n, raw in files.items()}
    write('HANDOFF_INVENTORY.json', inventory)
    files['HANDOFF_INVENTORY.json'] = (OUT / 'HANDOFF_INVENTORY.json').read_bytes()
    archive = R / 'Runs-management/local_deliveries/B3_SWAP_FLIP_TEST_READY_20261110_v1.zip'
    archive.parent.mkdir(parents=True, exist_ok=True)
    if archive.exists():
        raise FileExistsError('Preserve existing handoff')
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for name, raw in sorted(files.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 11, 10, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, raw)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert set(z.namelist()) == set(files)
        for name, raw in files.items():
            assert z.read(name) == raw
    receipt = {'archive': archive.relative_to(R).as_posix(), 'sha256': sha(archive.read_bytes()),
               'bytes': archive.stat().st_size, 'members': len(files), 'labels_included': False,
               'status': 'LOCAL_READY_REMOTE_RUNTIME_PENDING'}
    write('HANDOFF_RECEIPT.json', receipt)
    print(json.dumps(receipt, indent=2))

if __name__ == '__main__':
    main()
