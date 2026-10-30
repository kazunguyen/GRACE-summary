"""Prepare frozen B2 specs and prompts for the separate Kaggle inference notebook."""
import argparse
import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path

from config import config
from export_diagnostic_specs import read_rows
from prompt_builder import PromptBuilder


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset', required=True, choices=['devign', 'reveal'])
    parser.add_argument('--split', required=True, choices=['validation', 'test'])
    parser.add_argument('--train', required=True, type=Path)
    parser.add_argument('--validation', required=True, type=Path)
    parser.add_argument('--test', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--limit', type=int, help='Smoke test only; omit for full split')
    parser.add_argument('--allow-missing-graphs', action='store_true', help='Explicit exploratory opt-in')
    args = parser.parse_args()
    inputs = {'train': args.train, 'validation': args.validation, 'test': args.test}
    for name, path in inputs.items():
        rows = read_rows(path, args.dataset)
        missing = sum(not r['nodes'] for r in rows)
        print(f'{name}: {len(rows)} rows, missing graph {missing}')
        if missing and not args.allow_missing_graphs:
            raise ValueError(f'{name} contains {missing} missing graphs; supply CPG or explicitly opt in')
    args.out.mkdir(parents=True, exist_ok=True)
    spec = args.out / 'specs.jsonl'
    other = 'test' if args.split == 'validation' else 'validation'
    cmd = [sys.executable, str(Path(__file__).with_name('export_diagnostic_specs.py')),
           '--dataset', args.dataset, '--split', args.split, '--train', str(args.train),
           '--targets', str(inputs[args.split]), '--other-targets', str(inputs[other]), '--out', str(spec)]
    if args.limit is not None:
        if args.limit < 1:
            raise ValueError('limit must be positive')
        cmd += ['--max-targets', str(args.limit)]
    subprocess.run(cmd, check=True)
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(config.model_name, revision=config.model_revision)
    builder = PromptBuilder(tokenizer=tokenizer, context_limit_tokens=config.context_limit_tokens,
                            graph_nodes_max=config.graph_nodes_max, graph_edges_max=config.graph_edges_max,
                            target_code_max_tokens=config.target_code_max_tokens,
                            standard_demo_max_tokens=config.standard_demo_max_tokens, graph_max_tokens=config.graph_max_tokens)
    records = [json.loads(line) for line in spec.read_text(encoding='utf-8').splitlines() if line.strip()]
    prompts = args.out / 'prompts.jsonl'
    with prompts.open('w', encoding='utf-8', newline='\n') as f:
        for row in records:
            d = row['demonstrations'][0]
            target = {'id': row['id'], 'func': row['query_code'], 'nodes': row['nodes'], 'edges': row['edges']}
            demo = {'id': d['function_uid'], 'func': d['func'], 'target': d['target']}
            prompt, metadata = builder.build_prompt(target, demo)
            f.write(json.dumps({'id': row['id'], 'dataset': args.dataset, 'split': args.split,
                                'label': row['label'], 'prompt': prompt,
                                'prompt_sha256': hashlib.sha256(prompt.encode()).hexdigest(),
                                'demo_ids': [d['function_uid']], 'tokens': metadata,
                                'graph_missing': row['graph_missing']}, ensure_ascii=False) + '\n')
    manifest = {'dataset': args.dataset, 'split': args.split, 'arm': 'B2', 'count': len(records),
                'limit': args.limit, 'exploratory': args.limit is not None or args.allow_missing_graphs,
                'input_sha256': {name: sha256(path) for name, path in inputs.items()},
                'spec_sha256': sha256(spec), 'prompts_sha256': sha256(prompts),
                'tokenizer': config.model_name, 'tokenizer_revision': config.model_revision,
                'model_repo': 'ggml-org/Qwen3-Coder-30B-A3B-Instruct-GGUF', 'quantization': 'Q4_K_M',
                'prompt_budget_tokens': config.context_limit_tokens,
                'source_sha256': {name: sha256(Path(__file__).parent / name) for name in (
                    'prepare_kaggle_bundle.py', 'prepare_joern_cpg.py', 'export_diagnostic_specs.py', 'embedding_engine.py',
                    'retrieval_engine.py', 'prompt_builder.py', 'diagnostic_kit/src/grace_diag/probes.py',
                    'diagnostic_kit/src/grace_diag/token_budget.py', 'evaluation_contract.yaml')},
                'note': 'Exact dedup only; complete near-duplicate and CPG provenance audits before confirmation.'}
    manifest_path = args.out / 'bundle_manifest.json'
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    bundle = args.out / f'{args.dataset}_{args.split}_b2_kaggle.zip'
    with zipfile.ZipFile(bundle, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for path in (spec, prompts, manifest_path, spec.with_suffix('.jsonl.manifest.json')):
            z.write(path, path.name)
    print('Bundle:', bundle, 'SHA256:', sha256(bundle))


if __name__ == '__main__':
    main()
