"""Generate function-level whole CPGs from labeled JSONL using Linux Joern."""
import argparse
import hashlib
import json
import os
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from export_diagnostic_specs import read_rows, digest


def parse_graphml(path):
    root = ET.parse(path).getroot()
    ns = {'g': 'http://graphml.graphdrawing.org/xmlns'}
    keys = {k.attrib['id']: k.attrib.get('attr.name', k.attrib['id']) for k in root.findall('g:key', ns)}
    def props(element):
        return {keys[d.attrib['key']]: d.text or '' for d in element.findall('g:data', ns)}
    nodes = []
    for n in root.findall('.//g:node', ns):
        p = props(n)
        nodes.append({'id': n.attrib['id'], 'type': p.get('labelV', p.get('_label', p.get('label', ''))),
                      'code': p.get('CODE', p.get('code', '')), 'name': p.get('NAME', p.get('name', '')),
                      'external': p.get('IS_EXTERNAL', p.get('isExternal', 'false')).lower() == 'true'})
    edges = []
    for e in root.findall('.//g:edge', ns):
        p = props(e)
        edges.append({'start': e.attrib['source'], 'end': e.attrib['target'],
                      'type': p.get('labelE', p.get('_label', p.get('label', '')))})
    if not nodes or not any(n['type'] for n in nodes):
        raise ValueError('No typed nodes in Joern GraphML')
    children = {}
    for e in edges:
        if e['type'] == 'AST':
            children.setdefault(e['start'], []).append(e['end'])
    roots = [n['id'] for n in nodes if n['type'] == 'METHOD' and not n['external']
             and n['name'] != '<global>' and n['id'] in children]
    owned, stack = set(), list(roots)
    while stack:
        node = stack.pop()
        if node not in owned:
            owned.add(node)
            stack.extend(children.get(node, []))
    nodes = [n for n in nodes if n['id'] in owned]
    edges = [e for e in edges if e['start'] in owned and e['end'] in owned]
    if not nodes:
        raise ValueError('No source-function AST in Joern output')
    return nodes, edges


def extract(row, home):
    with tempfile.TemporaryDirectory(prefix='grace-joern-') as temp:
        root = Path(temp)
        code, binary, export = root / 'target.c', root / 'target.bin', root / 'export'
        code.write_text(row['func'], encoding='utf-8')
        for cmd in ([str(home / 'joern-parse'), str(code), '--output', str(binary)],
                    [str(home / 'joern-export'), '--repr', 'all', '--format', 'graphml', '--out', str(export), str(binary)]):
            subprocess.run(cmd, check=True, timeout=300, capture_output=True, text=True)
        graph_files = list(export.glob('*.xml')) + list(export.glob('*.graphml'))
        if len(graph_files) != 1:
            raise ValueError(f'Expected one whole GraphML graph, got {len(graph_files)}')
        nodes, edges = parse_graphml(graph_files[0])
        return {**row, 'nodes': nodes, 'edges': edges}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input', required=True, type=Path)
    ap.add_argument('--output', required=True, type=Path)
    ap.add_argument('--dataset', required=True)
    ap.add_argument('--joern-home', required=True, type=Path)
    args = ap.parse_args()
    if os.name == 'nt':
        raise RuntimeError('Run Joern preparation from a Linux/WSL Jupyter kernel')
    rows = read_rows(args.input, args.dataset)
    tools = [args.joern_home / 'joern-parse', args.joern_home / 'joern-export']
    if not all(p.is_file() for p in tools):
        raise FileNotFoundError('joern-parse and joern-export are required')
    identity = {'input_sha256': digest(args.input), 'tools_sha256': {p.name: digest(p) for p in tools},
                'script_sha256': digest(Path(__file__)),
                'dataset': args.dataset, 'schema': 'source_function_graphml_v2'}
    manifest = args.output.with_suffix(args.output.suffix + '.manifest.json')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if manifest.exists():
        if json.loads(manifest.read_text(encoding='utf-8')) != identity:
            raise ValueError('Joern checkpoint input/tool mismatch')
    else:
        if args.output.exists():
            raise ValueError('Existing output has no manifest; choose another path')
        manifest.write_text(json.dumps(identity, indent=2), encoding='utf-8')
    # Fail early for a broken Joern installation; failures for individual functions are recorded.
    extract({'id': 'joern_preflight', 'func': 'int joern_preflight(int x) { return x + 1; }', 'target': 0}, args.joern_home)
    done = {}
    if args.output.exists():
        for line in args.output.read_text(encoding='utf-8').splitlines():
            r = json.loads(line)
            if r['id'] in done:
                raise ValueError('Duplicate checkpoint ID')
            done[r['id']] = hashlib.sha256(r['func'].encode()).hexdigest()
    with args.output.open('a', encoding='utf-8', newline='\n') as f:
        for row in rows:
            code_hash = hashlib.sha256(row['func'].encode()).hexdigest()
            if row['id'] in done:
                if done[row['id']] != code_hash:
                    raise ValueError('Checkpoint code mismatch')
                continue
            try:
                graph = extract(row, args.joern_home)
                graph['graph_error'] = None
            except (subprocess.SubprocessError, OSError, ValueError, ET.ParseError) as exc:
                graph = {**row, 'nodes': [], 'edges': [], 'graph_error': f'{type(exc).__name__}: {str(exc)[:500]}'}
                print('GRAPH_MISSING', row['id'], graph['graph_error'], flush=True)
            f.write(json.dumps(graph, ensure_ascii=False) + '\n')
            f.flush(); os.fsync(f.fileno())
            print(row['id'], len(graph['nodes']), len(graph['edges']), flush=True)
    print('CPG:', args.output, 'sha256:', digest(args.output))


if __name__ == '__main__':
    main()
