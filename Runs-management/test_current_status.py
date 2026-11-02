"""Progress scans must not mutate locks or silently accept stale/duplicate outputs."""
import json

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
