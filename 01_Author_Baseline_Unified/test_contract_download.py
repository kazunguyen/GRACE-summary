import pytest

from download_contract_data import adapt


def test_devign_id_and_boolean_label():
    row = adapt({'id': 8, 'func': 'int f() {}', 'target': True, 'commit_id': 'commit'}, 'devign', 'validation', 0)
    assert row['id'] == 'devign:validation:8'
    assert row['target'] == 1
    assert row['commit_id'] == 'commit'


def test_reveal_maps_function_source_and_disambiguates_duplicate_hashes():
    source = {'hash': 7, 'functionSource': 'int f() {}', 'label': 0}
    a = adapt(source, 'reveal', 'train', 0)
    b = adapt(source, 'reveal', 'train', 1)
    assert a['func'] == source['functionSource']
    assert a['id'] != b['id']
    assert a['source_id'] == b['source_id'] == '7'


@pytest.mark.parametrize('label', [None, 2, '0'])
def test_rejects_missing_or_invalid_label(label):
    with pytest.raises(ValueError):
        adapt({'id': 1, 'func': 'int f() {}', 'target': label}, 'devign', 'validation', 0)
