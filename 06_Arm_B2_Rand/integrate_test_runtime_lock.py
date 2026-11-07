"""Embed the approved shared JSON and its enforcement helper in test notebooks."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HELPER = r'''import contextlib
import hashlib
import importlib.metadata
import json
import multiprocessing
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path

EXPECTED_CONTRACT_SHA256 = '__CONTRACT_SHA256__'
CONTRACT_PATH = Path('/kaggle/working/inference_runtime_lock.json')

def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''): h.update(block)
    return h.hexdigest()

def load_contract(path=CONTRACT_PATH):
    raw = Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != EXPECTED_CONTRACT_SHA256:
        raise ValueError('Runtime contract file SHA-256 mismatch')
    c = json.loads(raw)
    unsigned = {k:v for k,v in c.items() if k != 'integrity'}
    seal = hashlib.sha256(json.dumps(unsigned,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
    if seal != c['integrity']['sha256']:
        raise ValueError('Runtime contract canonical integrity mismatch')
    return c

def command(args):
    p = subprocess.run(args, check=True, text=True, capture_output=True)
    return p.stdout + p.stderr

def assert_runtime(c):
    actual = {name:importlib.metadata.version(name) for name in c['packages']}
    if actual != c['packages']: raise RuntimeError(f'Package mismatch: {actual}')
    if platform.system() != 'Linux' or '.'.join(map(str,sys.version_info[:2])) != c['build']['python_family']:
        raise RuntimeError('Contract requires Kaggle Linux/Python 3.13')
    gpu = command(['nvidia-smi','--query-gpu=index,uuid,name,memory.free,memory.total,driver_version','--format=csv,noheader'])
    lines = [s for s in gpu.splitlines() if s.strip()]
    if len(lines) != c['gpu']['device_count'] or any('T4' not in s for s in lines):
        raise RuntimeError(f'Contract requires 2 T4 GPUs: {gpu}')
    dist = importlib.metadata.distribution('llama-cpp-python')
    origin = json.loads(dist.read_text('direct_url.json') or '{}')
    if origin.get('archive_info',{}).get('hashes',{}).get('sha256') != c['backend_source']['sdist_sha256']:
        raise RuntimeError('Backend installation is not from the verified source archive')
    return actual, gpu

def provenance(c, runner, target):
    packages, gpu = assert_runtime(c)
    dist = importlib.metadata.distribution('llama-cpp-python')
    binaries = {}
    for entry in dist.files or []:
        if str(entry).endswith(('.so','.dll','.dylib')):
            p = Path(dist.locate_file(entry)); binaries[str(entry)] = digest(p)
    if not binaries: raise RuntimeError('No compiled backend library found for provenance')
    result = dict(runtime_contract_sha256=EXPECTED_CONTRACT_SHA256,
        runtime_contract_integrity=c['integrity']['sha256'], packages=packages,
        python=sys.version, platform=platform.platform(), libc=platform.libc_ver(),
        gpu_before_load=gpu, cpu_count=multiprocessing.cpu_count(),
        n_threads=max(multiprocessing.cpu_count()//2,1), n_threads_batch=multiprocessing.cpu_count(),
        constructor=c['constructor'], runner_sha256=digest(runner),
        backend_sdist_sha256=c['backend_source']['sdist_sha256'], compiled_backend_sha256=binaries,
        build_environment={k:os.environ.get(k) for k in ('CMAKE_ARGS','CMAKE_BUILD_PARALLEL_LEVEL','FORCE_CMAKE')})
    for name,args in [('nvcc',['nvcc','--version']),('compiler',['cc','--version']),
                      ('cxx_compiler',['c++','--version']),('cmake',['cmake','--version']),
                      ('pip_freeze',[sys.executable,'-m','pip','freeze','--all'])]:
        result[name] = command(args)
    target = Path(target); target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result

def load_locked_model(c, model_path, tokenizer_manifest, gpu_layers, log_path):
    import llama_cpp
    if digest(model_path) != c['model']['sha256']: raise ValueError('Frozen model SHA-256 mismatch')
    if gpu_layers != c['constructor']['n_gpu_layers']: raise ValueError('GPU layers differ from lock')
    if (tokenizer_manifest['tokenizer'],tokenizer_manifest['tokenizer_revision'],tokenizer_manifest['prompt_budget_tokens']) != (
        c['tokenizer']['repo'],c['tokenizer']['revision'],c['constructor']['n_ctx']):
        raise ValueError('Tokenizer/context differ from runtime lock')
    if not llama_cpp.llama_supports_gpu_offload(): raise RuntimeError('CUDA backend unavailable')
    kwargs = dict(c['constructor'])
    kwargs['split_mode'] = getattr(llama_cpp,kwargs['split_mode'])
    kwargs.update(n_threads=max(multiprocessing.cpu_count()//2,1), n_threads_batch=multiprocessing.cpu_count())
    # The pinned Python binding's logger writes through sys.stderr, so capture that stream directly.
    path = Path(log_path)
    with path.open('w',encoding='utf-8') as log, contextlib.redirect_stderr(log):
        model = llama_cpp.Llama(model_path=str(model_path),verbose=True,**kwargs)
    text = path.read_text(encoding='utf-8',errors='replace')
    print(text,flush=True)
    reports = re.findall(r'offloaded\s+(\d+)\s*/\s*(\d+)\s+layers?\s+to\s+GPU',text,re.I)
    required = c['gpu']['required_offloaded_layers']
    if not any(int(a)==int(b)==required for a,b in reports):
        model.close()
        raise RuntimeError(f'Full {required}/{required} GPU offload not verified; inspect {path}')
    return model
'''


def integrate(nb):
    if nb.get('metadata',{}).get('grace_runtime_lock'):
        raise ValueError('Notebook already integrated; regenerate from template before applying')
    raw = (ROOT / 'configs/inference_runtime_lock.json').read_bytes()
    c = json.loads(raw)
    sha = hashlib.sha256(raw).hexdigest()
    helper = HELPER.replace('__CONTRACT_SHA256__',sha)
    init = '\n# Approved shared runtime contract, embedded byte-for-byte for single-file Kaggle upload.\n'
    init += 'RUNTIME_LOCK_BYTES = ' + repr(raw) + '\n'
    init += "RUNTIME_LOCK_PATH = Path('/kaggle/working/inference_runtime_lock.json')\n"
    init += "if RUNTIME_LOCK_PATH.exists() and RUNTIME_LOCK_PATH.read_bytes() != RUNTIME_LOCK_BYTES:\n    raise RuntimeError('Working directory has a different runtime contract; use a fresh session')\n"
    init += "RUNTIME_LOCK_PATH.write_bytes(RUNTIME_LOCK_BYTES)\n"
    init += "Path('/kaggle/working/grace_runtime_contract.py').write_text(" + repr(helper) + ",encoding='utf-8')\n"
    init += "if '/kaggle/working' not in sys.path: sys.path.insert(0,'/kaggle/working')\n"
    init += "from grace_runtime_contract import load_contract, assert_runtime, EXPECTED_CONTRACT_SHA256\nRUNTIME = load_contract()\nshutil.copy2(RUNTIME_LOCK_PATH, DIAG / RUNTIME_LOCK_PATH.name)\n"
    nb['cells'][1]['source'] = (''.join(nb['cells'][1]['source']) + init).splitlines(keepends=True)
    src = ''.join(nb['cells'][2]['source'])
    src += "\nif MODEL_SHA256 != RUNTIME['model']['sha256'] or MODEL_FILENAME != RUNTIME['model']['filename'] or GPU_LAYERS != RUNTIME['constructor']['n_gpu_layers']:\n    raise ValueError('Notebook constants conflict with shared runtime contract')\nshutil.copy2(RUNTIME_LOCK_PATH, OUT_ROOT / RUNTIME_LOCK_PATH.name) if OUT_ROOT.exists() else None\n"
    nb['cells'][2]['source'] = src.splitlines(keepends=True)
    src = ''.join(nb['cells'][3]['source'])
    src = src.replace("or row.get('inference_seed') != 4294967295):", "or row.get('inference_seed') != RUNTIME['constructor']['seed']\n                    or row.get('runtime_contract_sha256') != EXPECTED_CONTRACT_SHA256):")
    src += "\nshutil.copy2(RUNTIME_LOCK_PATH, OUT_ROOT / RUNTIME_LOCK_PATH.name)\n"
    nb['cells'][3]['source'] = src.splitlines(keepends=True)
    install = '''# Install exactly the approved package set and hash-verified backend source.
import urllib.request
build = RUNTIME['build']
os.environ['CMAKE_ARGS'] = f"-DGGML_CUDA=on -DCMAKE_CUDA_ARCHITECTURES={build['CMAKE_CUDA_ARCHITECTURES']} -DCMAKE_LIBRARY_PATH={build['CMAKE_LIBRARY_PATH']}"
for key in ('CMAKE_BUILD_PARALLEL_LEVEL','FORCE_CMAKE'): os.environ[key] = build[key]
packages = [f'{k}=={v}' for k,v in RUNTIME['packages'].items() if k != 'llama-cpp-python']
packages += ['typing-extensions>=4.5.0','diskcache>=5.6.1','jinja2>=2.11.3']
run_logged([sys.executable,'-m','pip','install','--no-cache-dir',*packages], 'install_dependencies')
source = RUNTIME['backend_source']
with urllib.request.urlopen(f"https://pypi.org/pypi/llama-cpp-python/{source['version']}/json") as response:
    metadata = json.load(response)
artifact = next(x for x in metadata['urls'] if x['filename'] == source['sdist_filename'])
if artifact['digests']['sha256'] != source['sdist_sha256']: raise ValueError('Backend source registry hash mismatch')
archive_path = Path('/kaggle/working') / source['sdist_filename']
urllib.request.urlretrieve(artifact['url'], archive_path)
if hashlib.sha256(archive_path.read_bytes()).hexdigest() != source['sdist_sha256']: raise ValueError('Backend source bytes hash mismatch')
run_logged([sys.executable,'-m','pip','install','-v','--no-cache-dir','--no-deps','--force-reinstall',str(archive_path)], 'install_llama_cuda')
assert_runtime(RUNTIME)
versions()
diagnostics_zip()
'''
    nb['cells'][4]['source'] = install.splitlines(keepends=True)
    src = ''.join(nb['cells'][5]['source'])
    src = 'assert_runtime(RUNTIME)\n' + src
    nb['cells'][5]['source'] = src.splitlines(keepends=True)
    runner = ''.join(nb['cells'][7]['source'])
    runner = runner.replace('import numpy as np', 'import numpy as np\nfrom grace_runtime_contract import load_contract, provenance, load_locked_model, EXPECTED_CONTRACT_SHA256\nRUNTIME = load_contract()')
    runner = runner.replace("inference_seed = LLAMA_DEFAULT_SEED", "inference_seed = RUNTIME['constructor']['seed']")
    runner = runner.replace('len(runs) != 2', 'not (1 <= len(runs) <= 2)')
    old = "    llm = Llama(model_path=str(model_path), n_ctx=first_manifest['prompt_budget_tokens'], n_batch=256,\n                n_gpu_layers=gpu_layers, logits_all=True, verbose=True)"
    new = "    runtime_info = provenance(RUNTIME, __file__, status_path.parent / 'runtime_provenance.json')\n    llm = load_locked_model(RUNTIME, model_path, first_manifest, gpu_layers, status_path.parent / 'model_load_offload.log')\n    runtime_info['gpu_after_load'] = __import__('grace_runtime_contract').command(['nvidia-smi','--query-gpu=index,uuid,name,memory.free,memory.total,driver_version','--format=csv,noheader'])\n    runtime_info['offload_log_sha256'] = sha256(status_path.parent / 'model_load_offload.log')\n    (status_path.parent / 'runtime_provenance.json').write_text(json.dumps(runtime_info,indent=2),encoding='utf-8')"
    if old not in runner: raise ValueError('Expected constructor not found')
    runner = runner.replace(old,new)
    runner = runner.replace("'n_batch': 256}", "'n_batch': RUNTIME['constructor']['n_batch'], 'runtime_contract_sha256':EXPECTED_CONTRACT_SHA256, 'runtime_constructor':RUNTIME['constructor'], 'runtime_packages':RUNTIME['packages'], 'backend_sdist_sha256':RUNTIME['backend_source']['sdist_sha256']}")
    runner = runner.replace("row.update(tau=", "row.update(runtime_contract_sha256=EXPECTED_CONTRACT_SHA256)\n                row.update(tau=")
    runner = runner.replace("target = root.parent / 'grace_b1_h2_test_checkpoint.zip'", "target = root.parent / ('grace_' + root.name + '_checkpoint.zip')")
    nb['cells'][7]['source'] = runner.splitlines(keepends=True)
    src = ''.join(nb['cells'][8]['source'])
    src = src.replace("summary = {'threshold_lock_sha256'", "summary = {'runtime_contract_sha256':EXPECTED_CONTRACT_SHA256, 'threshold_lock_sha256'")
    nb['cells'][8]['source'] = src.splitlines(keepends=True)
    nb['cells'][0]['source'] += ('\nRuntime lock: embedded copy of configs/inference_runtime_lock.json, SHA-256 ' + sha + '. No extra Input upload is needed. Packages/source archive, model/tokenizer, constructor and full GPU offload are checked before scoring. Old checkpoints without the same contract identity are rejected.\n').splitlines(keepends=True)
    nb['metadata']['grace_runtime_lock'] = {'sha256':sha,'integrity':c['integrity']['sha256'],'source':'configs/inference_runtime_lock.json'}
    for cell in nb['cells']:
        if cell['cell_type']=='code': cell.update(execution_count=None,outputs=[])
    return nb


if __name__ == '__main__':
    delivery = ROOT / '06_Arm_B2_Rand/test_delivery_20261107'
    for p in delivery.glob('*.ipynb'):
        nb = integrate(json.loads(p.read_text(encoding='utf-8')))
        for i,cell in enumerate(nb['cells']):
            if cell['cell_type']=='code':
                src = ''.join(cell['source'])
                if src.startswith('%%writefile'): src = src.split('\n',1)[1]
                compile(src,f'{p.name}:cell{i}','exec')
        p.write_bytes((json.dumps(nb,ensure_ascii=False,indent=1)+'\n').encode())
        print(p.name)
    p = delivery / 'delivery_manifest.json'
    m = json.loads(p.read_text(encoding='utf-8'))
    m['notebooks'] = {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in delivery.glob('*.ipynb')}
    m['runtime_lock_sha256'] = hashlib.sha256((ROOT/'configs/inference_runtime_lock.json').read_bytes()).hexdigest()
    p.write_bytes((json.dumps(m,ensure_ascii=False,indent=2)+'\n').encode())
