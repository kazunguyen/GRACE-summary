"""Generate function-level CPGs with batched Joern runs on native Linux."""
import argparse
import fcntl
import hashlib
import json
import os
import shlex
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from pathlib import Path

from export_diagnostic_specs import read_rows, digest

MAX_WORKERS = 10
DEFAULT_BATCH_SIZE = 10
BASELINE_SCRIPT_SHA256 = "dc3dd525d2ae95d553290cf21894026dffcdfcadeb961e89484ab260c0c38cf1"
PREVIOUS_NATIVE_SCRIPT_SHA256 = "0a11dc101bc974c55f35a0aa5db285e8d448163c95d768572d8c31ea004edd47"


def read_graphml(path):
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
                      'filename': p.get('FILENAME', ''),
                      'external': p.get('IS_EXTERNAL', p.get('isExternal', 'false')).lower() == 'true'})
    edges = []
    for e in root.findall('.//g:edge', ns):
        p = props(e)
        edges.append({'start': e.attrib['source'], 'end': e.attrib['target'],
                      'type': p.get('labelE', p.get('_label', p.get('label', '')))})
    if not nodes or not any(n['type'] for n in nodes):
        raise ValueError('No typed nodes in Joern GraphML')
    return nodes, edges


def source_function_graph(nodes, edges, source_filename=None):
    """Apply the original source-function AST ownership filter."""
    children = {}
    for e in edges:
        if e['type'] == 'AST':
            children.setdefault(e['start'], []).append(e['end'])
    roots = [n['id'] for n in nodes if n['type'] == 'METHOD' and not n['external']
             and n['name'] != '<global>' and n['id'] in children
             and (source_filename is None or Path(n['filename']).name == source_filename)]
    owned, stack = set(), list(roots)
    while stack:
        node = stack.pop()
        if node not in owned:
            owned.add(node)
            stack.extend(children.get(node, []))
    kept_nodes = [dict(n) for n in nodes if n['id'] in owned]
    kept_edges = [e for e in edges if e['start'] in owned and e['end'] in owned]
    if not kept_nodes:
        raise ValueError('No source-function AST in Joern output')
    # Preserve the original output schema; FILENAME is internal to batch ownership.
    for node in kept_nodes:
        node.pop('filename', None)
    return kept_nodes, kept_edges


def frontend_jvm_args(java_opts):
    args = []
    for option in shlex.split(java_opts):
        if option.startswith('-J') or option.startswith('-D'):
            args.append(option)
        else:
            args.append('-J' + option)
    return args


def run_joern_parse(source, binary, home, env, java_opts):
    cmd = [str(home / 'joern-parse'), str(source), '--output', str(binary),
           '--frontend-args', *frontend_jvm_args(java_opts)]
    subprocess.run(cmd, check=True, timeout=900, capture_output=True, text=True, env=env)


def run_joern_export(binary, export, home, env):
    cmd = [str(home / 'joern-export'), '--repr', 'all', '--format', 'graphml',
           '--out', str(export), str(binary)]
    subprocess.run(cmd, check=True, timeout=900, capture_output=True, text=True, env=env)


def extract_one(row, home, java_opts):
    with tempfile.TemporaryDirectory(prefix='grace-joern-') as temp:
        root = Path(temp)
        source, binary, export = root / 'src', root / 'target.bin', root / 'export'
        source.mkdir()
        code = source / 'sample.c'
        code.write_text(row['func'], encoding='utf-8')
        env = os.environ.copy()
        env['JAVA_OPTS'] = java_opts
        run_joern_parse(source, binary, home, env, java_opts)
        run_joern_export(binary, export, home, env)
        graph_files = list(export.glob('*.xml')) + list(export.glob('*.graphml'))
        if len(graph_files) != 1:
            raise ValueError(f'Expected one whole GraphML graph, got {len(graph_files)}')
        nodes, edges = read_graphml(graph_files[0])
        nodes, edges = source_function_graph(nodes, edges)
        return {**row, 'nodes': nodes, 'edges': edges}


def extract_batch(batch, home, java_opts):
    """Parse/export one directory of snippets, then split ASTs by source filename."""
    with tempfile.TemporaryDirectory(prefix='grace-joern-batch-') as temp:
        root = Path(temp)
        source, binary, export = root / 'src', root / 'batch.bin', root / 'export'
        source.mkdir()
        source_names = {}
        for ordinal, row in batch:
            filename = f'sample_{ordinal:08d}.c'
            (source / filename).write_text(row['func'], encoding='utf-8')
            source_names[ordinal] = filename
        env = os.environ.copy()
        env['JAVA_OPTS'] = java_opts
        run_joern_parse(source, binary, home, env, java_opts)
        run_joern_export(binary, export, home, env)
        graph_files = list(export.glob('*.xml')) + list(export.glob('*.graphml'))
        if len(graph_files) != 1:
            raise ValueError(f'Expected one whole GraphML graph, got {len(graph_files)}')
        nodes, edges = read_graphml(graph_files[0])
        results = []
        for ordinal, row in batch:
            try:
                graph_nodes, graph_edges = source_function_graph(nodes, edges, source_names[ordinal])
                graph = {**row, 'nodes': graph_nodes, 'edges': graph_edges}
                results.append((ordinal, row, graph, None))
            except ValueError as exc:
                graph = {**row, 'nodes': [], 'edges': [],
                         'graph_error': f'{type(exc).__name__}: {str(exc)[:500]}'}
                results.append((ordinal, row, graph, f'{type(exc).__name__}: {str(exc)[:500]}'))
        return results


def caught_graph_error(exc):
    return isinstance(exc, (subprocess.SubprocessError, OSError, ValueError, ET.ParseError))


def process_batch(batch, home, java_opts):
    try:
        return extract_batch(batch, home, java_opts)
    except (subprocess.SubprocessError, OSError, ValueError, ET.ParseError) as batch_error:
        # Preserve per-sample failure handling if a batch-level parse/export fails.
        results = []
        for ordinal, row in batch:
            try:
                graph = extract_one(row, home, java_opts)
                results.append((ordinal, row, graph, None))
            except (subprocess.SubprocessError, OSError, ValueError, ET.ParseError) as exc:
                message = f'{type(exc).__name__}: {str(exc)[:500]}'
                graph = {**row, 'nodes': [], 'edges': [], 'graph_error': message}
                results.append((ordinal, row, graph, message))
        return results


def write_manifest(args, identity):
    manifest = args.output.with_suffix(args.output.suffix + '.manifest.json')
    if manifest.exists():
        previous = json.loads(manifest.read_text(encoding='utf-8'))
        if previous != identity:
            comparable_previous = dict(previous)
            comparable_current = dict(identity)
            previous_script = comparable_previous.pop('script_sha256', None)
            comparable_current.pop('script_sha256', None)
            resumable_scripts = {BASELINE_SCRIPT_SHA256, PREVIOUS_NATIVE_SCRIPT_SHA256}
            if comparable_previous != comparable_current or previous_script not in resumable_scripts:
                raise ValueError('Joern checkpoint input/tool mismatch; choose another output path')
    elif args.output.exists():
        raise ValueError('Existing output has no manifest; choose another path')
    manifest.write_text(json.dumps(identity, indent=2), encoding='utf-8')


def run(args):
    args.output.parent.mkdir(parents=True, exist_ok=True)
    rows = read_rows(args.input, args.dataset)
    tools = [args.joern_home / 'joern-parse', args.joern_home / 'joern-export']
    if not all(p.is_file() and os.access(p, os.X_OK) for p in tools):
        raise FileNotFoundError('Executable joern-parse and joern-export are required')
    identity = {'input_sha256': digest(args.input), 'tools_sha256': {p.name: digest(p) for p in tools},
                'script_sha256': digest(Path(__file__)),
                'dataset': args.dataset, 'schema': 'source_function_graphml_v2'}
    write_manifest(args, identity)

    # Fail early for a broken Joern installation; use the same capped frontend as real jobs.
    extract_one({'id': 'joern_preflight', 'func': 'int joern_preflight(int x) { return x + 1; }', 'target': 0},
                args.joern_home, args.java_opts)

    done = {}
    if args.output.exists():
        with args.output.open(encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                r = json.loads(line)
                if r['id'] in done:
                    raise ValueError('Duplicate checkpoint ID')
                done[r['id']] = hashlib.sha256(r['func'].encode()).hexdigest()
    pending = []
    for row_index, row in enumerate(rows):
        code_hash = hashlib.sha256(row['func'].encode()).hexdigest()
        if row['id'] in done:
            if done[row['id']] != code_hash:
                raise ValueError('Checkpoint code mismatch')
        else:
            pending.append((row_index, row))

    batches = [pending[i:i + args.batch_size] for i in range(0, len(pending), args.batch_size)]
    print(f'Rows: {len(rows)}; checkpointed: {len(done)}; pending: {len(pending)}; '
          f'batches: {len(batches)}; batch_size: {args.batch_size}; workers: {args.workers}; '
          f'JAVA_OPTS: {args.java_opts}', flush=True)
    if not pending:
        print('CPG already complete:', args.output, 'sha256:', digest(args.output), flush=True)
        return

    with args.output.open('a', encoding='utf-8', newline='\n') as f, ThreadPoolExecutor(max_workers=args.workers) as pool:
        active = {}
        ready = {}
        submit_cursor = 0
        write_batch_cursor = 0

        def submit_window():
            nonlocal submit_cursor
            while submit_cursor < len(batches) and submit_cursor < write_batch_cursor + args.workers:
                batch = batches[submit_cursor]
                future = pool.submit(process_batch, batch, args.joern_home, args.java_opts)
                active[future] = submit_cursor
                submit_cursor += 1

        submit_window()
        while active:
            completed, _ = wait(active, return_when=FIRST_COMPLETED)
            for future in completed:
                batch_index = active.pop(future)
                ready[batch_index] = future.result()
            while write_batch_cursor in ready:
                for ordinal, row, graph, error in ready.pop(write_batch_cursor):
                    if error:
                        print('GRAPH_MISSING', row['id'], error, flush=True)
                    f.write(json.dumps(graph, ensure_ascii=False) + '\n')
                    f.flush()
                    os.fsync(f.fileno())
                    print(row['id'], len(graph['nodes']), len(graph['edges']), flush=True)
                write_batch_cursor += 1
            submit_window()
    print('CPG:', args.output, 'sha256:', digest(args.output), flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input', required=True, type=Path)
    ap.add_argument('--output', required=True, type=Path)
    ap.add_argument('--dataset', required=True)
    ap.add_argument('--joern-home', required=True, type=Path)
    ap.add_argument('--workers', type=int, default=MAX_WORKERS)
    ap.add_argument('--batch-size', type=int, default=DEFAULT_BATCH_SIZE)
    ap.add_argument('--java-opts', default=os.environ.get('JOERN_JAVA_OPTS', '-Xms128m -Xmx1536m'))
    args = ap.parse_args()
    args.joern_home = args.joern_home.expanduser().resolve()
    if os.name == 'nt':
        raise RuntimeError('Run Joern preparation from Linux/Ubuntu')
    if not 1 <= args.workers <= MAX_WORKERS:
        raise ValueError(f'--workers must be between 1 and {MAX_WORKERS}')
    if args.batch_size < 1:
        raise ValueError('--batch-size must be at least 1')
    lock_path = args.output.with_suffix(args.output.suffix + '.lock')
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open('a+') as lock:
        print('Waiting for exclusive output lock:', lock_path, flush=True)
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        print('Acquired exclusive output lock.', flush=True)
        run(args)


if __name__ == '__main__':
    main()
