import contextlib
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

EXPECTED_CONTRACT_SHA256 = '85d8770839f80260cdc7c27b27b6cce6bf8815675c8593db68fb102589c5cbd6'
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
    c = json.loads(raw.decode('utf-8'))
    unsigned = {k: v for k, v in c.items() if k != 'integrity'}
    seal = hashlib.sha256(json.dumps(unsigned, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')).hexdigest()
    if seal != c['integrity']['sha256']:
        raise ValueError('Runtime contract canonical integrity mismatch')
    return c

def command(args):
    p = subprocess.run(args, check=True, text=True, capture_output=True)
    return p.stdout + p.stderr

def assert_runtime(c):
    actual = {name: importlib.metadata.version(name) for name in c['packages']}
    if actual != c['packages']: raise RuntimeError(f'Package mismatch: {actual}')
    if platform.system() != 'Linux' or '.'.join(map(str, sys.version_info[:2])) != c['build']['python_family']:
        raise RuntimeError('Contract requires Kaggle Linux/Python 3.13')
    gpu = command(['nvidia-smi', '--query-gpu=index,uuid,name,memory.free,memory.total,driver_version', '--format=csv,noheader'])
    lines = [s for s in gpu.splitlines() if s.strip()]
    if len(lines) != c['gpu']['device_count'] or any('T4' not in s for s in lines):
        raise RuntimeError(f'Contract requires 2 T4 GPUs: {gpu}')
    dist = importlib.metadata.distribution('llama-cpp-python')
    origin = json.loads(dist.read_text('direct_url.json') or '{}')
    if origin.get('archive_info', {}).get('hashes', {}).get('sha256') != c['backend_source']['sdist_sha256']:
        raise RuntimeError('Backend installation is not from the verified source archive')
    return actual, gpu

def provenance(c, runner, target):
    packages, gpu = assert_runtime(c)
    dist = importlib.metadata.distribution('llama-cpp-python')
    binaries = {}
    for entry in dist.files or []:
        if str(entry).endswith(('.so', '.dll', '.dylib')):
            p = Path(dist.locate_file(entry)); binaries[str(entry)] = digest(p)
    if not binaries: raise RuntimeError('No compiled backend library found for provenance')
    result = dict(runtime_contract_sha256=EXPECTED_CONTRACT_SHA256,
        runtime_contract_integrity=c['integrity']['sha256'], packages=packages,
        python=sys.version, platform=platform.platform(), libc=platform.libc_ver(),
        gpu_before_load=gpu, cpu_count=multiprocessing.cpu_count(),
        n_threads=max(multiprocessing.cpu_count() // 2, 1), n_threads_batch=multiprocessing.cpu_count(),
        constructor=c['constructor'], runner_sha256=digest(runner),
        cuda_device_order=os.environ.get('CUDA_DEVICE_ORDER'),
        cuda_visible_devices=os.environ.get('CUDA_VISIBLE_DEVICES'),
        backend_sdist_sha256=c['backend_source']['sdist_sha256'], compiled_backend_sha256=binaries,
        build_environment={k: os.environ.get(k) for k in ('CMAKE_ARGS', 'CMAKE_BUILD_PARALLEL_LEVEL', 'FORCE_CMAKE')})
    for name, args in [('nvcc', ['nvcc', '--version']), ('compiler', ['cc', '--version']),
                      ('cxx_compiler', ['c++', '--version']), ('cmake', ['cmake', '--version']),
                      ('pip_freeze', [sys.executable, '-m', 'pip', 'freeze', '--all'])]:
        result[name] = command(args)
    target = Path(target); target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2), encoding='utf-8')
    return result

def load_locked_model(c, model_path, tokenizer_manifest, gpu_layers, log_path, model_digest):
    import llama_cpp
    if model_digest != c['model']['sha256']: raise ValueError('Frozen model SHA-256 mismatch')
    if gpu_layers != c['constructor']['n_gpu_layers']: raise ValueError('GPU layers differ from lock')
    if (tokenizer_manifest['tokenizer'], tokenizer_manifest['tokenizer_revision'], tokenizer_manifest['prompt_budget_tokens']) != (
        c['tokenizer']['repo'], c['tokenizer']['revision'], c['constructor']['n_ctx']):
        raise ValueError('Tokenizer/context differ from runtime lock')
    if not llama_cpp.llama_supports_gpu_offload(): raise RuntimeError('CUDA backend unavailable')
    kwargs = dict(c['constructor'])
    kwargs['split_mode'] = getattr(llama_cpp, kwargs['split_mode'])
    kwargs.update(n_threads=max(multiprocessing.cpu_count() // 2, 1), n_threads_batch=multiprocessing.cpu_count())
    path = Path(log_path)
    with path.open('w', encoding='utf-8') as log, contextlib.redirect_stderr(log):
        model = llama_cpp.Llama(model_path=str(model_path), verbose=True, **kwargs)
    text = path.read_text(encoding='utf-8', errors='replace')
    print(text, flush=True)
    from b3_delivery_runtime import native_log_check
    try:
        native_log_check(text, c)
    except Exception:
        model.close()
        raise
    return model
