"""Progress scans must not mutate locks or silently accept stale/duplicate outputs."""
import json
from pathlib import Path
import subprocess
import sys

import pytest
import refresh_current_status as status


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding='utf-8')


def fixture_tree(tmp_path, monkeypatch):
    root = tmp_path/'repo'
    here = root/'Runs-management'
    put(here/'thresholds.json', {'entries': {}})
    monkeypatch.setattr(status, 'FOLDERS', {'B1': 'arm'})
    monkeypatch.setattr(status, 'SOURCES', {'B1': 'arm/output/imported'})
    monkeypatch.setattr(status, 'SPLITS', [('devign', 'validation', 2), ('devign', 'test', 1)])
    expected = [{'id': str(i), 'label': i, 'prompt_sha256': str(i)} for i in range(2)]
    path = root/'arm/output/bundles/devign/validation/prompts.jsonl'
    path.parent.mkdir(parents=True)
    path.write_text('\n'.join(map(json.dumps, expected)), encoding='utf-8')
    records = [dict(r, arm='B1', dataset='devign', split='validation', model_sha256='model',
                    s=.2+i*.6, valid=True, response_valid=i==0) for i,r in enumerate(expected)]
    path = root/'arm/output/imported/devign/validation/records.jsonl'
    path.parent.mkdir(parents=True)
    path.write_text('\n'.join(map(json.dumps, records)), encoding='utf-8')
    put(path.with_name('run_manifest.json'), {'model_sha256': 'model'})
    return root, here, path, records


def test_full_validation_is_unlocked_and_scores_survive_invalid_raw(tmp_path, monkeypatch):
    root, here, path, records = fixture_tree(tmp_path, monkeypatch)
    before = (here/'thresholds.json').read_bytes()
    result = status.collect(root, here)['arms'][0]
    assert result['completed'] == 2
    assert result['splits'][0]['threshold_state'] == 'validation_complete_unlocked'
    assert result['splits'][0]['invalid_response'] == 1
    assert result['splits'][0]['invalid_score'] == 0
    assert result['splits'][1]['completed'] == 0
    assert (here/'thresholds.json').read_bytes() == before
    assert not (here/'threshold_lock_status.json').exists()


@pytest.mark.parametrize('change', ['duplicate', 'prompt', 'model'])
def test_bad_import_is_rejected(tmp_path, monkeypatch, change):
    root, here, path, records = fixture_tree(tmp_path, monkeypatch)
    if change == 'duplicate':
        records.append(records[0])
    else:
        records[0]['prompt_sha256' if change=='prompt' else 'model_sha256'] = 'changed'
    path.write_text('\n'.join(map(json.dumps, records)), encoding='utf-8')
    with pytest.raises(ValueError):
        status.collect(root, here)


def test_regenerators_preserve_progress_and_historical_json(tmp_path):
    here = Path(__file__).resolve().parent
    names = ['write_tier1_audit_report.py', 'write_threshold_explanation.py', 'refresh_current_status.py',
             'KIEM_TOAN_DIEU_KIEN_TANG_1.json', 'current_status.json', 'thresholds.json']
    for name in names:
        (tmp_path/name).write_bytes((here/name).read_bytes())
    snapshots = {n:(tmp_path/n).read_bytes() for n in names if n.endswith('.json')}
    for script, output in [('write_tier1_audit_report.py', 'KIEM_TOAN_DIEU_KIEN_TANG_1.md'),
                           ('write_threshold_explanation.py', 'KET_QUA_CHOT_NGUONG.md')]:
        subprocess.run([sys.executable, '-B', str(tmp_path/script)], check=True, capture_output=True)
        first = (tmp_path/output).read_bytes()
        text = first.decode('utf-8')
        assert '| B1 | 2732/2732 | 429/2732 | 2273/2273 | 0/2274 | 5434/10011 |' in text
        assert '| B2-flip | 2732/2732 | 230/2732 |' in text
        assert 'B2: chưa có lời gọi khóa trước test' in text
        subprocess.run([sys.executable, '-B', str(tmp_path/script)], check=True, capture_output=True)
        assert (tmp_path/output).read_bytes() == first
    for name, original in snapshots.items():
        assert (tmp_path/name).read_bytes() == original
