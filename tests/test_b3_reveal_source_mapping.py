"""Exact mapping boundary; fixtures do not stand in for human review."""
import copy
import json
import sys
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'01_Author_Baseline_Unified/diagnostic_kit/src'))
from grace_diag.amended_b3 import digest, source_mapping_tokens, validate_pair


@pytest.fixture(scope='module')
def actual():
    case=ROOT/'Runs-management/b3_verified_patch_v1/reveal_recovery_20261108/case_reveal_curl_alloc_addbyter_16061_17887'
    candidate=json.loads((case/'candidate.json').read_text(encoding='utf-8'))
    raw=ROOT/'01_Author_Baseline_Unified/output/research_freeze_20261101/reveal/train_raw.jsonl'
    ids={candidate['vulnerable_id'],candidate['patched_id']}
    bank={r['id']:r for l in raw.read_text(encoding='utf-8').splitlines() if (r:=json.loads(l))['id'] in ids}
    return candidate,bank


def test_actual_recovered_source_accepted_only_without_reviews(actual):
    candidate,bank=actual
    assert len(validate_pair(candidate,bank,'reveal',require_reviews=False))==2
    with pytest.raises(ValueError,match='Two distinct reviewers'):validate_pair(candidate,bank,'reveal')


def test_c_tokens_preserve_semantic_details():
    assert source_mapping_tokens('a -> b /* comment */ + 1')==source_mapping_tokens('a->b+1')
    assert source_mapping_tokens('a++')!=source_mapping_tokens('a + +b')
    assert source_mapping_tokens('"a b"')!=source_mapping_tokens('"ab"')
    assert source_mapping_tokens('1U')!=source_mapping_tokens('1')
    assert source_mapping_tokens('x > y')!=source_mapping_tokens('x >= y')
    with pytest.raises(ValueError):source_mapping_tokens('#define A 1\nA')
    with pytest.raises(ValueError):source_mapping_tokens('/* unterminated')


def test_mapping_cannot_hide_token_or_patch_changes(actual):
    candidate,bank=actual
    bad=copy.deepcopy(candidate)
    mapping=bad['source']['mapping']
    mapping['upstream_after']=mapping['upstream_after'].replace('newsize > infop->alloc','newsize >= infop->alloc')
    mapping['upstream_after_sha256']=digest(mapping['upstream_after'])
    with pytest.raises(ValueError,match='changes C tokens'):validate_pair(bad,bank,'reveal',require_reviews=False)
    bad=copy.deepcopy(candidate);bad['source']['fix_diff']=bad['source']['fix_diff'].replace('+    size_t newsize = infop->alloc*2;','+    size_t newsize = 0;')
    with pytest.raises(ValueError,match='supported by archived'):validate_pair(bad,bank,'reveal',require_reviews=False)
    bad=copy.deepcopy(candidate);bad['source'].pop('mapping')
    with pytest.raises(ValueError,match='supported by archived'):validate_pair(bad,bank,'reveal',require_reviews=False)
