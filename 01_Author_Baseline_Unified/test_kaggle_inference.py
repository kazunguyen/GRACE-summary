import json
import hashlib
import sys
import zipfile
from types import ModuleType

import numpy as np
import pytest

from kaggle_inference import binary_scores, run


def test_graph_conversion_preserves_edge_label():
    from export_diagnostic_specs import graph_convert
    _, edges = graph_convert({'nodes': [{'id': 'a'}, {'id': 'b'}],
                              'edges': [{'src': 'a', 'dst': 'b', 'label': 'AST'}]})
    assert edges[0]['type'] == 'AST'


def test_joern_graphml_source_function_ownership(tmp_path):
    from prepare_joern_cpg import parse_graphml
    graph = tmp_path / 'graph.graphml'
    graph.write_text('''<graphml xmlns="http://graphml.graphdrawing.org/xmlns">
      <key id="l" attr.name="labelV"/><key id="e" attr.name="labelE"/>
      <key id="n" attr.name="NAME"/>
      <graph><node id="m"><data key="l">METHOD</data><data key="n">f</data></node>
      <node id="x"><data key="l">CALL</data></node>
      <node id="outside"><data key="l">CALL</data></node>
      <edge source="m" target="x"><data key="e">AST</data></edge>
      <edge source="outside" target="x"><data key="e">CFG</data></edge></graph></graphml>''', encoding='utf-8')
    nodes, edges = parse_graphml(graph)
    assert {n['id'] for n in nodes} == {'m', 'x'}
    assert edges == [{'start': 'm', 'end': 'x', 'type': 'AST'}]


def test_binary_scores_use_unconstrained_logits():
    result = binary_scores(np.array([9.0, -1002.0, -1000.0]), [1, 2])
    assert result['greedy_token_id'] == 0
    assert result['s'] == pytest.approx(0.880797, rel=1e-5)
    assert result['logprob_0'] == pytest.approx(-1011)


def test_bundle_inference_checkpoint_and_identity(tmp_path, monkeypatch):
    class Tokenizer:
        def encode(self, label, add_special_tokens=False): return {'0': [1], '1': [2]}[label]
        def apply_chat_template(self, *args, tokenize=True, **kwargs): return [10, 11] if tokenize else 'chat'
    class Llama:
        def __init__(self, **kwargs): self.scores = np.array([[9.0, 0.0, 1.0]])
        def tokenize(self, content, **kwargs): return {b'chat': [10, 11], b'0': [1], b'1': [2]}[content]
        def reset(self): self.n_tokens = 0
        def eval(self, tokens): self.n_tokens = 1
        def detokenize(self, tokens): return b'other'
    llama = ModuleType('llama_cpp'); llama.Llama = Llama; llama.__version__ = 'mock'
    transformers = ModuleType('transformers')
    transformers.AutoTokenizer = type('AutoTokenizer', (), {'from_pretrained': staticmethod(lambda *a, **k: Tokenizer())})
    monkeypatch.setitem(sys.modules, 'llama_cpp', llama)
    monkeypatch.setitem(sys.modules, 'transformers', transformers)
    text = 'target'; row = {'id': 'a', 'dataset': 'devign', 'split': 'validation', 'label': 1,
                            'prompt': text, 'prompt_sha256': hashlib.sha256(text.encode()).hexdigest(),
                            'demo_ids': ['d'], 'tokens': {}, 'graph_missing': False}
    content = (json.dumps(row) + '\n').encode()
    manifest = {'count': 1, 'prompts_sha256': hashlib.sha256(content).hexdigest(),
                'model_repo': 'repo', 'quantization': 'Q4_K_M', 'tokenizer': 'tok',
                'tokenizer_revision': 'rev', 'prompt_budget_tokens': 8192}
    bundle = tmp_path / 'bundle.zip'
    with zipfile.ZipFile(bundle, 'w') as z:
        z.writestr('bundle_manifest.json', json.dumps(manifest)); z.writestr('prompts.jsonl', content)
    model = tmp_path / 'model.gguf'; model.write_bytes(b'model')
    out = tmp_path / 'out'
    run(bundle, model, out)
    run(bundle, model, out)
    records = [json.loads(x) for x in (out / 'records.jsonl').read_text().splitlines()]
    assert len(records) == 1
    assert records[0]['response_valid'] is False
    assert records[0]['valid'] is True
    assert records[0]['logprob_distribution'] == 'unconstrained_first_token'


def test_preparation_bundle_records_prompt_hash_and_missing_graph_guard(tmp_path, monkeypatch):
    import prepare_kaggle_bundle as prep
    from tokenizers_support import MockTokenizer
    row = {'id': 'target', 'func': 'int f() { return 0; }', 'target': 0,
           'nodes': [{'id': 'a', 'type': 'METHOD'}], 'edges': []}
    for name in ('train', 'validation', 'test'):
        (tmp_path / (name + '.jsonl')).write_text(json.dumps(row) + '\n', encoding='utf-8')
    transformer = ModuleType('transformers')
    transformer.AutoTokenizer = type('AutoTokenizer', (), {'from_pretrained': staticmethod(lambda *a, **k: MockTokenizer())})
    monkeypatch.setitem(sys.modules, 'transformers', transformer)
    def export(cmd, check):
        output = tmp_path / 'out' / 'specs.jsonl'
        spec = {'id': 'target', 'query_code': row['func'], 'nodes': row['nodes'], 'edges': [],
                'label': 0, 'graph_missing': False,
                'demonstrations': [{'function_uid': 'd', 'func': 'int g() {}', 'target': 1}]}
        output.write_text(json.dumps(spec) + '\n', encoding='utf-8')
        output.with_suffix('.jsonl.manifest.json').write_text('{}', encoding='utf-8')
    monkeypatch.setattr(prep.subprocess, 'run', export)
    argv = ['prepare', '--dataset', 'devign', '--split', 'validation', '--out', str(tmp_path / 'out')]
    for name in ('train', 'validation', 'test'):
        argv += ['--' + name, str(tmp_path / (name + '.jsonl'))]
    monkeypatch.setattr(sys, 'argv', argv)
    prep.main()
    bundle = tmp_path / 'out' / 'devign_validation_b2_kaggle.zip'
    with zipfile.ZipFile(bundle) as z:
        manifest = json.loads(z.read('bundle_manifest.json'))
        assert hashlib.sha256(z.read('prompts.jsonl')).hexdigest() == manifest['prompts_sha256']
        assert manifest['count'] == 1
