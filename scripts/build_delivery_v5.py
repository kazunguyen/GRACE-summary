#!/usr/bin/env python3
"""
Build Delivery Package for B3 Release v5 (Devign Validation Locked).

Deliverables created under Runs-management/b3_verified_patch_v1/release_20261108_v5/delivery/:
1. input_bundle/ and b3_devign_val_input.zip:
   - bundle_manifest.json
   - prompts.jsonl (2,732 Devign validation prompts)
   - inputs_manifest.json
   - pool_manifest.json
   - validation_prompt_manifest.json
   - scope_decision.json
2. inference_input_manifest.json
3. notebook.ipynb (Canonical 9-cell runtime-locked notebook)
4. kernel-metadata.json
5. delivery_manifest.json
"""

import hashlib
import json
import os
import shutil
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
RELEASE_V5_DIR = ROOT / "Runs-management" / "b3_verified_patch_v1" / "release_20261108_v5"
DELIVERY_DIR = RELEASE_V5_DIR / "delivery"
INPUT_BUNDLE_DIR = DELIVERY_DIR / "input_bundle"
BUNDLE_ZIP_PATH = DELIVERY_DIR / "b3_devign_val_input.zip"

RUNTIME_LOCK_PATH = ROOT / "configs" / "inference_runtime_lock.json"
DEVIGN_CENSUS_PATH = RELEASE_V5_DIR / "validation" / "devign" / "validation_census.jsonl"


def compute_file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def compute_bytes_sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def build_input_bundle():
    print("=== Step 1: Building Delivery Input Bundle ===")
    INPUT_BUNDLE_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Read devign census records
    assert DEVIGN_CENSUS_PATH.is_file(), f"Missing devign census: {DEVIGN_CENSUS_PATH}"
    prompts_rows = []
    with open(DEVIGN_CENSUS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                prompts_rows.append(json.loads(line))

    assert len(prompts_rows) == 2732, f"Expected 2732 prompts, got {len(prompts_rows)}"
    prompts_sha = compute_file_sha256(DEVIGN_CENSUS_PATH)
    assert prompts_sha == "dee4a33009f4ecbf42b96e6f18c5f4390d5f0a620370af925bae0f2cceeb7e59", "Prompt census sha mismatch!"

    # Copy prompts.jsonl into bundle
    bundle_prompts_path = INPUT_BUNDLE_DIR / "prompts.jsonl"
    shutil.copy2(DEVIGN_CENSUS_PATH, bundle_prompts_path)

    # Copy supporting metadata manifests
    shutil.copy2(RELEASE_V5_DIR / "inputs_manifest.json", INPUT_BUNDLE_DIR / "inputs_manifest.json")
    shutil.copy2(RELEASE_V5_DIR / "pools" / "pool_manifest.json", INPUT_BUNDLE_DIR / "pool_manifest.json")
    shutil.copy2(RELEASE_V5_DIR / "validation" / "validation_prompt_manifest.json", INPUT_BUNDLE_DIR / "validation_prompt_manifest.json")
    shutil.copy2(RELEASE_V5_DIR / "governance" / "scope_decision.json", INPUT_BUNDLE_DIR / "scope_decision.json")

    # Generate bundle_manifest.json
    bundle_manifest = {
        "schema_version": 1,
        "release_id": "release_20261108_v5",
        "release_version": "v5_devign_validation_locked",
        "parent_release": "release_20261108_v4",
        "release_status": "FROZEN",
        "method_id": "b3-verified-patch-v1",
        "arm": "B3",
        "dataset": "devign",
        "split": "validation",
        "seed": 42,
        "count": 2732,
        "prompts_sha256": prompts_sha,
        "model_repo": "ggml-org/Qwen3-Coder-30B-A3B-Instruct-GGUF",
        "model_filename": "Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf",
        "model_sha256": "f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335",
        "quantization": "Q4_K_M",
        "tokenizer": "Qwen/Qwen3-Coder-30B-A3B-Instruct",
        "tokenizer_revision": "b2cff646eb4bb1d68355c01b18ae02e7cf42d120",
        "prompt_budget_tokens": 8192,
        "created_at_utc": "2026-11-08T14:49:37.411777+00:00",
        "files": {
            "prompts.jsonl": prompts_sha,
            "inputs_manifest.json": compute_file_sha256(INPUT_BUNDLE_DIR / "inputs_manifest.json"),
            "pool_manifest.json": compute_file_sha256(INPUT_BUNDLE_DIR / "pool_manifest.json"),
            "validation_prompt_manifest.json": compute_file_sha256(INPUT_BUNDLE_DIR / "validation_prompt_manifest.json"),
            "scope_decision.json": compute_file_sha256(INPUT_BUNDLE_DIR / "scope_decision.json"),
        },
    }

    bm_body = {k: v for k, v in bundle_manifest.items() if k != "manifest_seal_sha256"}
    bundle_seal = compute_bytes_sha256(json.dumps(bm_body, sort_keys=True, ensure_ascii=False, indent=2).encode("utf-8"))
    bundle_manifest["manifest_seal_sha256"] = bundle_seal

    with open(INPUT_BUNDLE_DIR / "bundle_manifest.json", "w", encoding="utf-8") as f:
        json.dump(bundle_manifest, f, indent=2, ensure_ascii=False)

    # 2. Package into zip archive (using deterministic zip timestamps)
    print("Packing b3_devign_val_input.zip...")
    if BUNDLE_ZIP_PATH.exists():
        BUNDLE_ZIP_PATH.unlink()

    with zipfile.ZipFile(BUNDLE_ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for fname in sorted(os.listdir(INPUT_BUNDLE_DIR)):
            fpath = INPUT_BUNDLE_DIR / fname
            if fpath.is_file():
                # Write with fixed timestamp for reproducibility
                zinfo = zipfile.ZipInfo(fname, date_time=(2026, 11, 8, 12, 0, 0))
                zinfo.compress_type = zipfile.ZIP_DEFLATED
                zf.writestr(zinfo, fpath.read_bytes())

    zip_sha = compute_file_sha256(BUNDLE_ZIP_PATH)
    print(f"Bundle archive created: {BUNDLE_ZIP_PATH.name} (SHA256: {zip_sha})")
    return zip_sha, bundle_manifest


def build_inference_input_manifest(zip_sha: str, bundle_manifest: dict):
    print("=== Step 2: Sealing Inference Input Manifest ===")
    im = {
        "schema_version": 1,
        "release_id": "release_20261108_v5",
        "release_version": "v5_devign_validation_locked",
        "parent_release": "release_20261108_v4",
        "release_status": "FROZEN",
        "method_id": "b3-verified-patch-v1",
        "scope": {
            "dataset": "devign",
            "split": "validation",
            "arm": "B3",
            "prompt_seed": 42,
            "expected_count": 2732,
        },
        "bundle": {
            "filename": "b3_devign_val_input.zip",
            "sha256": zip_sha,
            "contents": bundle_manifest["files"],
            "bundle_manifest_seal_sha256": bundle_manifest["manifest_seal_sha256"],
        },
        "census_sha256": "dee4a33009f4ecbf42b96e6f18c5f4390d5f0a620370af925bae0f2cceeb7e59",
        "model": {
            "model_repo": "ggml-org/Qwen3-Coder-30B-A3B-Instruct-GGUF",
            "filename": "Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf",
            "sha256": "f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335",
            "quantization": "Q4_K_M",
        },
        "tokenizer": {
            "repo": "Qwen/Qwen3-Coder-30B-A3B-Instruct",
            "revision": "b2cff646eb4bb1d68355c01b18ae02e7cf42d120",
        },
        "runtime_lock": {
            "contract_id": "grace_qwen_q4_runtime_v1",
            "contract_sha256": compute_file_sha256(RUNTIME_LOCK_PATH),
            "backend_sdist_sha256": "34ed0f9bd9431af045bb63d9324ae620ad0536653740e9bb163a2e1fcb973be6",
            "packages": {
                "huggingface-hub": "0.36.2",
                "llama-cpp-python": "0.3.16",
                "numpy": "2.1.3",
                "scikit-learn": "1.5.2",
                "scipy": "1.16.3",
                "tokenizers": "0.22.2",
                "transformers": "4.57.1",
            },
        },
        "inputs_manifest_sha256": compute_file_sha256(RELEASE_V5_DIR / "inputs_manifest.json"),
        "inputs_manifest_seal_sha256": json.loads((RELEASE_V5_DIR / "inputs_manifest.json").read_text(encoding="utf-8")).get("seal_sha256"),
        "validation_prompt_manifest_sha256": compute_file_sha256(RELEASE_V5_DIR / "validation" / "validation_prompt_manifest.json"),
        "validation_prompt_manifest_seal_sha256": json.loads((RELEASE_V5_DIR / "validation" / "validation_prompt_manifest.json").read_text(encoding="utf-8")).get("prompt_manifest_seal_sha256"),
        "created_at_utc": "2026-11-08T14:49:37.830712+00:00",
    }

    body = {k: v for k, v in im.items() if k != "seal_sha256"}
    seal = compute_bytes_sha256(json.dumps(body, sort_keys=True, ensure_ascii=False, indent=2).encode("utf-8"))
    im["seal_sha256"] = seal

    out_path = DELIVERY_DIR / "inference_input_manifest.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(im, f, indent=2, ensure_ascii=False)

    # Also copy to release root per suggested tree
    shutil.copy2(out_path, RELEASE_V5_DIR / "inference_input_manifest.json")
    shutil.copy2(RELEASE_V5_DIR / "validation" / "validation_prompt_manifest.json", RELEASE_V5_DIR / "validation_prompt_manifest.json")
    print(f"Inference input manifest sealed: {seal}")
    return out_path, seal


def build_canonical_notebook() -> Path:
    print("=== Step 3: Generating Canonical 9-Cell Runtime-Locked Notebook ===")
    runtime_lock_bytes_str = RUNTIME_LOCK_PATH.read_bytes().decode("utf-8")
    runtime_lock_escaped = json.dumps(runtime_lock_bytes_str)

    cells = [
        # Cell 1: Markdown header
        {
            "cell_type": "markdown",
            "id": "c01_header",
            "metadata": {},
            "source": [
                "# B3 (Amended Algorithm) — Kaggle Devign Validation Execution (Runtime Locked)\n",
                "\n",
                "**Thực thi thuật toán mới B3 (Verified Patch-Pair Contrastive Selector) trên tập Validation Devign:**\n",
                "- **Scope**: Devign validation census B3 seed 42 (N=2,732). REVEAL safely paused pending provenance resolution.\n",
                "- **Thuật toán mới**: Tự động ghép cặp đối chứng từ kho mẫu đã xác thực (Verified Pair Pool) với diff hàm thật, chuẩn hóa token Jaccard không rò rỉ nhãn, tuân thủ nghiêm ngặt định dạng Figure 6.\n",
                "- **Runtime Lock (`grace_qwen_q4_runtime_v1`)**:\n",
                "  * 2x Tesla T4 (`kaggle_t4_x2`), `LLAMA_SPLIT_MODE_LAYER`, `main_gpu: 0`, `tensor_split: null`\n",
                "  * Assert trọn vẹn 49/49 layers nạp vào GPU\n",
                "  * Exact 7 packages: `llama-cpp-python==0.3.16`, `transformers==4.57.1`, `huggingface-hub==0.36.2`, `tokenizers==0.22.2`, `numpy==2.1.3`, `scipy==1.16.3`, `scikit-learn==1.5.2` (PyPI sdist SHA-256 verified)\n",
                "  * Validation inference tạo phân phối score mới để xác định $\\tau^*$. Tuyệt đối không đọc ngưỡng lịch sử hoặc áp ngưỡng cố định từ trước.\n"
            ]
        },
        # Cell 2: Diagnostics & System Logging
        {
            "cell_type": "code",
            "execution_count": None,
            "id": "c02_diag_setup",
            "metadata": {},
            "outputs": [],
            "source": [
                "from pathlib import Path\n",
                "import sys, os, json, subprocess, traceback, shutil, platform, importlib.metadata, zipfile, hashlib, time, re\n",
                "from datetime import datetime, timezone\n",
                "\n",
                "SESSION_STARTED = time.time()\n",
                "DIAG = Path('/kaggle/working/grace_diagnostics')\n",
                "DIAG.mkdir(parents=True, exist_ok=True)\n",
                "EVENTS = DIAG / 'events.log'\n",
                "\n",
                "def note(message):\n",
                "    text = str(message)\n",
                "    print(text, flush=True)\n",
                "    with EVENTS.open('a', encoding='utf-8') as f:\n",
                "        f.write(f'[{datetime.now(timezone.utc).isoformat()}] {text}\\n')\n",
                "\n",
                "def diagnostics_zip():\n",
                "    archive = shutil.make_archive('/kaggle/working/grace_diagnostics', 'zip', root_dir=DIAG)\n",
                "    print('Tải log chẩn đoán từ Kaggle Output:', archive, flush=True)\n",
                "    return archive\n",
                "\n",
                "def run_logged(cmd, name, env=None):\n",
                "    log = DIAG / f'{name}.log'\n",
                "    note(f'Bắt đầu {name}: {cmd!r} | log đầy đủ: {log}')\n",
                "    is_inference = name.startswith('inference_seed_')\n",
                "    with log.open('w', encoding='utf-8') as f:\n",
                "        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,\n",
                "                                text=True, encoding='utf-8', errors='replace', bufsize=1, env=env)\n",
                "        for line in proc.stdout:\n",
                "            f.write(line); f.flush()\n",
                "            if re.search(r'\\b(?:Found|Skip(?:ping)?) link\\b', line, flags=re.IGNORECASE):\n",
                "                continue\n",
                "            if is_inference:\n",
                "                match = re.search(r'^(\\S+).*\\((\\d+)/(\\d+)\\)\\s*$', line.strip())\n",
                "                if match:\n",
                "                    run_key, done, total = match.group(1), int(match.group(2)), int(match.group(3))\n",
                "                    if done % 100 == 0 or done == total:\n",
                "                        print(f'Inference {run_key}: {done}/{total}', flush=True)\n",
                "                elif line.strip():\n",
                "                    print(line, end='', flush=True)\n",
                "            else:\n",
                "                print(line, end='', flush=True)\n",
                "        code = proc.wait()\n",
                "    if is_inference and '--status' in cmd:\n",
                "        status_path = Path(cmd[cmd.index('--status') + 1])\n",
                "        if status_path.is_file():\n",
                "            status = json.loads(status_path.read_text(encoding='utf-8'))\n",
                "            print(f\"Inference summary: {status.get('completed_records_total', 0)} records; state={status.get('state')}\", flush=True)\n",
                "            for run_key, progress in status.get('runs', {}).items():\n",
                "                print(f\"  {run_key}: {progress.get('completed', 0)}/{progress.get('count', '?')} [{progress.get('state', 'pending')}]\")\n",
                "    note(f'{name} kết thúc với mã {code}')\n",
                "    if code:\n",
                "        raise subprocess.CalledProcessError(code, cmd)\n",
                "\n",
                "def versions():\n",
                "    result = {}\n",
                "    for name in ('llama-cpp-python', 'transformers', 'huggingface_hub', 'scikit-learn', 'numpy', 'scipy', 'tokenizers'):\n",
                "        try: result[name] = importlib.metadata.version(name)\n",
                "        except importlib.metadata.PackageNotFoundError: result[name] = 'not installed'\n",
                "    note('Installed package versions: ' + json.dumps(result))\n",
                "    return result\n",
                "\n",
                "def capture_failure(shell, etype, evalue, tb, tb_offset=None):\n",
                "    trace = ''.join(traceback.format_exception(etype, evalue, tb))\n",
                "    try:\n",
                "        with (DIAG / 'exceptions.log').open('a', encoding='utf-8') as f:\n",
                "            f.write(f'\\n[{datetime.now(timezone.utc).isoformat()}]\\n{trace}\\n')\n",
                "        note(f'Lỗi: {etype.__name__}: {evalue}')\n",
                "        versions()\n",
                "        diagnostics_zip()\n",
                "    except Exception as diagnostic_error:\n",
                "        print('Không thể ghi đầy đủ chẩn đoán:', diagnostic_error, flush=True)\n",
                "    shell.showtraceback((etype, evalue, tb), tb_offset=tb_offset)\n",
                "    return []\n",
                "\n",
                "get_ipython().set_custom_exc((Exception,), capture_failure)\n",
                "note('UTC: ' + datetime.now(timezone.utc).isoformat())\n",
                "note('Python: ' + sys.version)\n",
                "note('Executable: ' + sys.executable)\n",
                "note('Platform: ' + platform.platform())\n",
                "for loc in ('/kaggle/working', '/kaggle/input'):\n",
                "    try:\n",
                "        usage = shutil.disk_usage(loc)\n",
                "        note(f'Disk {loc}: total={usage.total} free={usage.free} bytes')\n",
                "    except OSError as exc: note(f'Disk {loc}: {exc}')\n",
                "versions()\n",
                "for name, cmd in [('gpu', ['nvidia-smi']), ('cuda_compiler', ['nvcc', '--version']), ('cmake', ['cmake', '--version']), ('pip', [sys.executable, '-m', 'pip', '--version'])]:\n",
                "    try: run_logged(cmd, name)\n",
                "    except (OSError, subprocess.CalledProcessError) as exc: note(f'{name}: {type(exc).__name__}: {exc}')\n",
                "try:\n",
                "    input_entries = [p.name for p in Path('/kaggle/input').glob('*')]\n",
                "    note(f'Input entries: {input_entries}')\n",
                "    gguf_files = [str(p) for p in Path('/kaggle/input').rglob('*.gguf')]\n",
                "    note(f'Input GGUF files: {gguf_files}')\n",
                "except Exception as exc: note(f'Input inspection error: {exc}')\n",
                "diagnostics_zip()\n"
            ]
        },
        # Cell 3: Embed Runtime Lock and Write Runtime Contract Helper
        {
            "cell_type": "code",
            "execution_count": None,
            "id": "c03_runtime_contract",
            "metadata": {},
            "outputs": [],
            "source": [
                f"RUNTIME_LOCK_RAW = {runtime_lock_escaped}\n",
                "RUNTIME_LOCK_PATH = Path('/kaggle/working/inference_runtime_lock.json')\n",
                "RUNTIME_LOCK_PATH.write_text(RUNTIME_LOCK_RAW, encoding='utf-8')\n",
                "\n",
                "CONTRACT_HELPER_CODE = '''import contextlib\n",
                "import hashlib\n",
                "import importlib.metadata\n",
                "import json\n",
                "import multiprocessing\n",
                "import os\n",
                "import platform\n",
                "import re\n",
                "import shutil\n",
                "import subprocess\n",
                "import sys\n",
                "from pathlib import Path\n",
                "\n",
                "EXPECTED_CONTRACT_SHA256 = '4c9c3bcff5e9fd32532d7edf85df7a961e45ec9c64bee3df8833d986a2eb276e'\n",
                "CONTRACT_PATH = Path('/kaggle/working/inference_runtime_lock.json')\n",
                "\n",
                "def digest(path):\n",
                "    h = hashlib.sha256()\n",
                "    with Path(path).open('rb') as f:\n",
                "        for block in iter(lambda: f.read(1024 * 1024), b''): h.update(block)\n",
                "    return h.hexdigest()\n",
                "\n",
                "def load_contract(path=CONTRACT_PATH):\n",
                "    raw = Path(path).read_bytes()\n",
                "    if hashlib.sha256(raw).hexdigest() != EXPECTED_CONTRACT_SHA256:\n",
                "        raise ValueError('Runtime contract file SHA-256 mismatch')\n",
                "    c = json.loads(raw.decode('utf-8'))\n",
                "    unsigned = {k: v for k, v in c.items() if k != 'integrity'}\n",
                "    seal = hashlib.sha256(json.dumps(unsigned, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')).hexdigest()\n",
                "    if seal != c['integrity']['sha256']:\n",
                "        raise ValueError('Runtime contract canonical integrity mismatch')\n",
                "    return c\n",
                "\n",
                "def command(args):\n",
                "    p = subprocess.run(args, check=True, text=True, capture_output=True)\n",
                "    return p.stdout + p.stderr\n",
                "\n",
                "def assert_runtime(c):\n",
                "    actual = {name: importlib.metadata.version(name) for name in c['packages']}\n",
                "    if actual != c['packages']: raise RuntimeError(f'Package mismatch: {actual}')\n",
                "    if platform.system() != 'Linux' or '.'.join(map(str, sys.version_info[:2])) != c['build']['python_family']:\n",
                "        raise RuntimeError('Contract requires Kaggle Linux/Python 3.13')\n",
                "    gpu = command(['nvidia-smi', '--query-gpu=index,uuid,name,memory.free,memory.total,driver_version', '--format=csv,noheader'])\n",
                "    lines = [s for s in gpu.splitlines() if s.strip()]\n",
                "    if len(lines) != c['gpu']['device_count'] or any('T4' not in s for s in lines):\n",
                "        raise RuntimeError(f'Contract requires 2 T4 GPUs: {gpu}')\n",
                "    dist = importlib.metadata.distribution('llama-cpp-python')\n",
                "    origin = json.loads(dist.read_text('direct_url.json') or '{}')\n",
                "    if origin.get('archive_info', {}).get('hashes', {}).get('sha256') != c['backend_source']['sdist_sha256']:\n",
                "        raise RuntimeError('Backend installation is not from the verified source archive')\n",
                "    return actual, gpu\n",
                "\n",
                "def provenance(c, runner, target):\n",
                "    packages, gpu = assert_runtime(c)\n",
                "    dist = importlib.metadata.distribution('llama-cpp-python')\n",
                "    binaries = {}\n",
                "    for entry in dist.files or []:\n",
                "        if str(entry).endswith(('.so', '.dll', '.dylib')):\n",
                "            p = Path(dist.locate_file(entry)); binaries[str(entry)] = digest(p)\n",
                "    if not binaries: raise RuntimeError('No compiled backend library found for provenance')\n",
                "    result = dict(runtime_contract_sha256=EXPECTED_CONTRACT_SHA256,\n",
                "        runtime_contract_integrity=c['integrity']['sha256'], packages=packages,\n",
                "        python=sys.version, platform=platform.platform(), libc=platform.libc_ver(),\n",
                "        gpu_before_load=gpu, cpu_count=multiprocessing.cpu_count(),\n",
                "        n_threads=max(multiprocessing.cpu_count() // 2, 1), n_threads_batch=multiprocessing.cpu_count(),\n",
                "        constructor=c['constructor'], runner_sha256=digest(runner),\n",
                "        cuda_device_order=os.environ.get('CUDA_DEVICE_ORDER'),\n",
                "        cuda_visible_devices=os.environ.get('CUDA_VISIBLE_DEVICES'),\n",
                "        backend_sdist_sha256=c['backend_source']['sdist_sha256'], compiled_backend_sha256=binaries,\n",
                "        build_environment={k: os.environ.get(k) for k in ('CMAKE_ARGS', 'CMAKE_BUILD_PARALLEL_LEVEL', 'FORCE_CMAKE')})\n",
                "    for name, args in [('nvcc', ['nvcc', '--version']), ('compiler', ['cc', '--version']),\n",
                "                      ('cxx_compiler', ['c++', '--version']), ('cmake', ['cmake', '--version']),\n",
                "                      ('pip_freeze', [sys.executable, '-m', 'pip', 'freeze', '--all'])]:\n",
                "        result[name] = command(args)\n",
                "    target = Path(target); target.parent.mkdir(parents=True, exist_ok=True)\n",
                "    target.write_text(json.dumps(result, indent=2), encoding='utf-8')\n",
                "    return result\n",
                "\n",
                "def load_locked_model(c, model_path, tokenizer_manifest, gpu_layers, log_path, model_digest):\n",
                "    import llama_cpp\n",
                "    if model_digest != c['model']['sha256']: raise ValueError('Frozen model SHA-256 mismatch')\n",
                "    if gpu_layers != c['constructor']['n_gpu_layers']: raise ValueError('GPU layers differ from lock')\n",
                "    if (tokenizer_manifest['tokenizer'], tokenizer_manifest['tokenizer_revision'], tokenizer_manifest['prompt_budget_tokens']) != (\n",
                "        c['tokenizer']['repo'], c['tokenizer']['revision'], c['constructor']['n_ctx']):\n",
                "        raise ValueError('Tokenizer/context differ from runtime lock')\n",
                "    if not llama_cpp.llama_supports_gpu_offload(): raise RuntimeError('CUDA backend unavailable')\n",
                "    kwargs = dict(c['constructor'])\n",
                "    kwargs['split_mode'] = getattr(llama_cpp, kwargs['split_mode'])\n",
                "    kwargs.update(n_threads=max(multiprocessing.cpu_count() // 2, 1), n_threads_batch=multiprocessing.cpu_count())\n",
                "    path = Path(log_path)\n",
                "    with path.open('w', encoding='utf-8') as log, contextlib.redirect_stderr(log):\n",
                "        model = llama_cpp.Llama(model_path=str(model_path), verbose=True, **kwargs)\n",
                "    text = path.read_text(encoding='utf-8', errors='replace')\n",
                "    print(text, flush=True)\n",
                "    reports = re.findall(r'offloaded\\\\s+(\\\\d+)\\\\s*/\\\\s*(\\\\d+)\\\\s+layers?\\\\s+to\\\\s+GPU', text, re.I)\n",
                "    required = c['gpu']['required_offloaded_layers']\n",
                "    if not any(int(a) == int(b) == required for a, b in reports):\n",
                "        model.close()\n",
                "        raise RuntimeError(f'Full {required}/{required} GPU offload not verified; inspect {path}')\n",
                "    for field in ('n_ctx', 'n_batch', 'n_ubatch'):\n",
                "        observed = re.findall(rf'\\\\b{field}\\\\s*=\\\\s*(\\\\d+)\\\\b', text)\n",
                "        if not observed or int(observed[-1]) != c['constructor'][field]:\n",
                "            model.close()\n",
                "            raise RuntimeError(f'Effective {field} differs from contract; inspect {path}')\n",
                "    gpu_devices = re.findall(r'Device\\\\s+\\\\d+:\\\\s+[^\\\\n]*\\\\bT4\\\\b', text)\n",
                "    if len(gpu_devices) != c['gpu']['device_count']:\n",
                "        model.close()\n",
                "        raise RuntimeError(f'Expected two visible T4 devices in backend log; inspect {path}')\n",
                "    return model\n",
                "'''\n",
                "\n",
                "Path('/kaggle/working/grace_runtime_contract.py').write_text(CONTRACT_HELPER_CODE, encoding='utf-8')\n",
                "if '/kaggle/working' not in sys.path:\n",
                "    sys.path.insert(0, '/kaggle/working')\n",
                "from grace_runtime_contract import assert_runtime, digest, load_contract, EXPECTED_CONTRACT_SHA256\n",
                "RUNTIME = load_contract()\n",
                "shutil.copy2(RUNTIME_LOCK_PATH, DIAG / RUNTIME_LOCK_PATH.name)\n",
                "note('Runtime lock verified and loaded. Integrity: ' + RUNTIME['integrity']['sha256'])\n"
            ]
        },
        # Cell 4: Scope Configuration & B3 Devign Validation Guard (NO HISTORICAL THRESHOLDS)
        {
            "cell_type": "code",
            "execution_count": None,
            "id": "c04_scope_config",
            "metadata": {},
            "outputs": [],
            "source": [
                "ARM = 'B3'\n",
                "DATASET = 'devign'\n",
                "SPLIT = 'validation'\n",
                "SEED = 42\n",
                "EXPECTED_COUNT = 2732\n",
                "\n",
                "KAGGLE_INPUT_ROOT = Path('/kaggle/input')\n",
                "BUNDLE_WORK = Path('/kaggle/working/b3_bundles')\n",
                "OUT_ROOT = Path('/kaggle/working/b3_devign_validation_runtime_locked')\n",
                "BUNDLE_NAME = 'b3_devign_val_input.zip'\n",
                "CHECKPOINT_NAME = 'grace_b3_devign_val_checkpoint.zip'\n",
                "CHECKPOINT_INPUT_PATH = None\n",
                "\n",
                "MODEL_FILENAME = 'Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf'\n",
                "MODEL_SHA256 = 'f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335'\n",
                "MAX_RUNTIME_HOURS = 9\n",
                "CHECKPOINT_RESERVE_SECONDS = 300\n",
                "GPU_LAYERS = -1\n",
                "\n",
                "# STRICT METHODOLOGICAL GUARD: Validation determines tau* post-inference.\n",
                "# DO NOT apply or read historical test thresholds (e.g. LOCKED_THRESHOLDS or tau*=0.77).\n",
                "HISTORICAL_THRESHOLDS_APPLIED = None\n",
                "\n",
                "if (MODEL_FILENAME, MODEL_SHA256, GPU_LAYERS) != (\n",
                "    RUNTIME['model']['filename'], RUNTIME['model']['sha256'], RUNTIME['constructor']['n_gpu_layers']\n",
                "):\n",
                "    raise ValueError('Notebook model or GPU settings differ from runtime lock')\n",
                "\n",
                "note(f'Configured scope: ARM={ARM}, DATASET={DATASET}, SPLIT={SPLIT}, SEED={SEED}, COUNT={EXPECTED_COUNT}')\n"
            ]
        },
        # Cell 5: Input Bundle Loading & Checkpoint Restorer
        {
            "cell_type": "code",
            "execution_count": None,
            "id": "c05_input_bundle_loader",
            "metadata": {},
            "outputs": [],
            "source": [
                "BUNDLE_WORK.mkdir(parents=True, exist_ok=True)\n",
                "OUT_ROOT.mkdir(parents=True, exist_ok=True)\n",
                "\n",
                "# Discover input bundle: supports both packed ZIP and auto-unpacked directory\n",
                "bundle_candidates = sorted(KAGGLE_INPUT_ROOT.rglob(BUNDLE_NAME))\n",
                "if not bundle_candidates:\n",
                "    bundle_candidates = sorted(KAGGLE_INPUT_ROOT.rglob('*.zip'))\n",
                "    bundle_candidates = [p for p in bundle_candidates if 'b3' in p.name.lower() and 'devign' in p.name.lower()]\n",
                "\n",
                "bundle_file = None\n",
                "prompts_records = None\n",
                "bundle_manifest = None\n",
                "\n",
                "if bundle_candidates:\n",
                "    bundle_file = bundle_candidates[0]\n",
                "    note(f'Found packed bundle ZIP: {bundle_file}')\n",
                "    with zipfile.ZipFile(bundle_file) as z:\n",
                "        bundle_manifest = json.loads(z.read('bundle_manifest.json').decode('utf-8'))\n",
                "        raw_prompts = z.read('prompts.jsonl')\n",
                "        prompts_sha = hashlib.sha256(raw_prompts).hexdigest()\n",
                "        if prompts_sha != bundle_manifest['prompts_sha256']:\n",
                "            raise ValueError(f'Prompt bytes sha256 mismatch: expected {bundle_manifest[\"prompts_sha256\"]}, got {prompts_sha}')\n",
                "        prompts_records = [json.loads(line) for line in raw_prompts.decode('utf-8').splitlines() if line.strip()]\n",
                "else:\n",
                "    note(f'Bundle archive {BUNDLE_NAME} not found as single file; searching auto-unpacked directories under {KAGGLE_INPUT_ROOT}')\n",
                "    manifest_candidates = sorted(KAGGLE_INPUT_ROOT.rglob('bundle_manifest.json'))\n",
                "    if manifest_candidates:\n",
                "        manifest_file = manifest_candidates[0]\n",
                "        prompts_file = manifest_file.parent / 'prompts.jsonl'\n",
                "        if prompts_file.is_file():\n",
                "            bundle_manifest = json.loads(manifest_file.read_text(encoding='utf-8'))\n",
                "            raw_prompts = prompts_file.read_bytes()\n",
                "            prompts_sha = hashlib.sha256(raw_prompts).hexdigest()\n",
                "            if prompts_sha != bundle_manifest['prompts_sha256']:\n",
                "                raise ValueError(f'Prompt bytes sha256 mismatch in unpacked directory: {prompts_sha}')\n",
                "            prompts_records = [json.loads(line) for line in raw_prompts.decode('utf-8').splitlines() if line.strip()]\n",
                "            # Pack to local bundle work directory for execution\n",
                "            bundle_file = BUNDLE_WORK / BUNDLE_NAME\n",
                "            with zipfile.ZipFile(bundle_file, 'w', compression=zipfile.ZIP_DEFLATED) as z:\n",
                "                z.write(manifest_file, arcname='bundle_manifest.json')\n",
                "                z.write(prompts_file, arcname='prompts.jsonl')\n",
                "\n",
                "if not bundle_file or not prompts_records:\n",
                "    raise FileNotFoundError(f'Cannot load input bundle {BUNDLE_NAME} or auto-unpacked equivalent from {KAGGLE_INPUT_ROOT}')\n",
                "\n",
                "if len(prompts_records) != EXPECTED_COUNT:\n",
                "    raise ValueError(f'Expected {EXPECTED_COUNT} prompts, got {len(prompts_records)}')\n",
                "\n",
                "expected_prompts = {r['id']: (r['prompt_sha256'], r['label']) for r in prompts_records}\n",
                "note(f'Loaded bundle manifest and {len(expected_prompts)} prompts. Target census: {EXPECTED_COUNT}')\n",
                "\n",
                "# Checkpoint restore logic\n",
                "if CHECKPOINT_INPUT_PATH is not None:\n",
                "    checkpoint = Path(CHECKPOINT_INPUT_PATH)\n",
                "else:\n",
                "    candidates = sorted(KAGGLE_INPUT_ROOT.rglob(CHECKPOINT_NAME))\n",
                "    if len(candidates) > 1:\n",
                "        raise ValueError('Multiple checkpoint candidates found; specify CHECKPOINT_INPUT_PATH explicitly')\n",
                "    checkpoint = candidates[0] if candidates else None\n",
                "\n",
                "if checkpoint:\n",
                "    note(f'Restoring checkpoint from: {checkpoint}')\n",
                "    with zipfile.ZipFile(checkpoint) as source:\n",
                "        for name in source.namelist():\n",
                "            if name.endswith('records.jsonl') or name.endswith('run_manifest.json'):\n",
                "                target = OUT_ROOT / name\n",
                "                target.parent.mkdir(parents=True, exist_ok=True)\n",
                "                target.write_bytes(source.read(name))\n",
                "\n",
                "shutil.copy2(RUNTIME_LOCK_PATH, OUT_ROOT / RUNTIME_LOCK_PATH.name)\n",
                "\n",
                "def validate_records():\n",
                "    records_path = OUT_ROOT / f'seed_{SEED}' / DATASET / SPLIT / 'records.jsonl'\n",
                "    seen = set()\n",
                "    if records_path.exists():\n",
                "        for line in records_path.read_text(encoding='utf-8').splitlines():\n",
                "            if not line.strip(): continue\n",
                "            row = json.loads(line)\n",
                "            uid = str(row['id'])\n",
                "            identity = (row['arm'], row['seed'], row['dataset'], row['split'], row['model_sha256'])\n",
                "            if (uid in seen or identity != (ARM, SEED, DATASET, SPLIT, MODEL_SHA256)\n",
                "                    or expected_prompts.get(uid) != (row['prompt_sha256'], row['label'])\n",
                "                    or not math.isfinite(row['s'])):\n",
                "                raise ValueError(f'Unexpected or corrupted record: {records_path}/{uid}')\n",
                "            seen.add(uid)\n",
                "    return len(seen)\n"
            ]
        },
        # Cell 6: Dependencies Installation & CUDA llama-cpp-python Build
        {
            "cell_type": "code",
            "execution_count": None,
            "id": "c06_deps_install",
            "metadata": {},
            "outputs": [],
            "source": [
                "import urllib.request\n",
                "build = RUNTIME['build']\n",
                "os.environ['CMAKE_ARGS'] = (\n",
                "    f\"-DGGML_CUDA={'on' if build['GGML_CUDA'] else 'off'}\"\n",
                "    f\" -DCMAKE_CUDA_ARCHITECTURES={build['CMAKE_CUDA_ARCHITECTURES']}\"\n",
                "    f\" -DCMAKE_LIBRARY_PATH={build['CMAKE_LIBRARY_PATH']}\"\n",
                ")\n",
                "for key in ('CMAKE_BUILD_PARALLEL_LEVEL', 'FORCE_CMAKE'):\n",
                "    os.environ[key] = build[key]\n",
                "\n",
                "packages = [f'{name}=={version}' for name, version in RUNTIME['packages'].items()\n",
                "            if name != RUNTIME['backend_source']['name']]\n",
                "packages += ['typing-extensions>=4.5.0', 'diskcache>=5.6.1', 'jinja2>=2.11.3']\n",
                "run_logged([sys.executable, '-m', 'pip', 'install', '--no-cache-dir', *packages], 'install_dependencies')\n",
                "\n",
                "source = RUNTIME['backend_source']\n",
                "with urllib.request.urlopen(f\"https://pypi.org/pypi/{source['name']}/{source['version']}/json\", timeout=60) as response:\n",
                "    metadata = json.load(response)\n",
                "artifact = next(item for item in metadata['urls'] if item['filename'] == source['sdist_filename'])\n",
                "if artifact['digests']['sha256'] != source['sdist_sha256']:\n",
                "    raise ValueError('Backend source registry SHA-256 mismatch')\n",
                "archive_path = Path('/kaggle/working') / source['sdist_filename']\n",
                "with urllib.request.urlopen(artifact['url'], timeout=120) as response, archive_path.open('wb') as target:\n",
                "    shutil.copyfileobj(response, target)\n",
                "if digest(archive_path) != source['sdist_sha256']:\n",
                "    raise ValueError('Backend source file SHA-256 mismatch')\n",
                "run_logged([sys.executable, '-m', 'pip', 'install', '-v', '--no-cache-dir', '--no-deps',\n",
                "            '--force-reinstall', str(archive_path)], 'install_llama_cuda')\n",
                "note('Locked packages: ' + json.dumps(assert_runtime(RUNTIME)[0], sort_keys=True))\n",
                "diagnostics_zip()\n"
            ]
        },
        # Cell 7: Runtime Verification & GPU Offload Smoke
        {
            "cell_type": "code",
            "execution_count": None,
            "id": "c07_runtime_smoke",
            "metadata": {},
            "outputs": [],
            "source": [
                "assert_runtime(RUNTIME)\n",
                "import llama_cpp\n",
                "versions()\n",
                "note('llama-cpp-python GPU offload: ' + str(llama_cpp.llama_supports_gpu_offload()))\n",
                "assert llama_cpp.llama_supports_gpu_offload(), 'llama-cpp-python CUDA backend unavailable'\n",
                "diagnostics_zip()\n"
            ]
        },
        # Cell 8: Inference Engine Script (kaggle_inference.py)
        {
            "cell_type": "code",
            "execution_count": None,
            "id": "c08_write_inference_script",
            "metadata": {},
            "outputs": [],
            "source": [
                "%%writefile /kaggle/working/kaggle_inference.py\n",
                "import argparse\n",
                "import hashlib\n",
                "import json\n",
                "import math\n",
                "import os\n",
                "import platform\n",
                "import time\n",
                "import tempfile\n",
                "import zipfile\n",
                "from datetime import datetime, timezone\n",
                "from pathlib import Path\n",
                "\n",
                "import numpy as np\n",
                "from grace_runtime_contract import (\n",
                "    EXPECTED_CONTRACT_SHA256, command, digest, load_contract, load_locked_model, provenance,\n",
                ")\n",
                "\n",
                "RUNTIME = load_contract()\n",
                "\n",
                "\n",
                "def sha256(path):\n",
                "    h = hashlib.sha256()\n",
                "    with Path(path).open('rb') as f:\n",
                "        for chunk in iter(lambda: f.read(1024 * 1024), b''):\n",
                "            h.update(chunk)\n",
                "    return h.hexdigest()\n",
                "\n",
                "\n",
                "def write_json_atomic(path, payload):\n",
                "    path = Path(path)\n",
                "    tmp = path.with_suffix(path.suffix + '.tmp')\n",
                "    tmp.write_text(json.dumps(payload, indent=2), encoding='utf-8')\n",
                "    os.replace(tmp, path)\n",
                "\n",
                "\n",
                "def binary_scores(logits, label_ids):\n",
                "    values = np.asarray(logits, dtype=np.float64).reshape(-1)\n",
                "    if not np.all(np.isfinite(values)):\n",
                "        raise ValueError('Non-finite logits')\n",
                "    maximum = np.max(values)\n",
                "    normalizer = float(maximum + np.log(np.exp(values - maximum).sum()))\n",
                "    lp0 = float(values[label_ids[0]] - normalizer)\n",
                "    lp1 = float(values[label_ids[1]] - normalizer)\n",
                "    score = float(np.exp(lp1 - np.logaddexp(lp0, lp1)))\n",
                "    best = int(np.argmax(values))\n",
                "    top = np.argsort(values)[-5:][::-1]\n",
                "    return {'logprob_0': lp0, 'logprob_1': lp1, 'p0': math.exp(lp0), 'p1': math.exp(lp1),\n",
                "            's': score, 'pred_argmax': int(score >= 0.5), 'greedy_token_id': best,\n",
                "            'top5': [{'token_id': int(i), 'logprob': float(values[i] - normalizer)} for i in top]}\n",
                "\n",
                "\n",
                "def load_bundle(bundle):\n",
                "    with zipfile.ZipFile(bundle) as z:\n",
                "        manifest = json.loads(z.read('bundle_manifest.json'))\n",
                "        prompt_bytes = z.read('prompts.jsonl')\n",
                "    if hashlib.sha256(prompt_bytes).hexdigest() != manifest['prompts_sha256']:\n",
                "        raise ValueError(f'Prompt bundle hash mismatch: {bundle}')\n",
                "    rows = [json.loads(line) for line in prompt_bytes.decode('utf-8').splitlines() if line.strip()]\n",
                "    if len(rows) != manifest['count'] or len({str(r['id']) for r in rows}) != len(rows):\n",
                "        raise ValueError(f'Prompt count or unique ID check failed: {bundle}')\n",
                "    return manifest, rows\n",
                "\n",
                "\n",
                "def evaluate_output(output):\n",
                "    from sklearn.metrics import (\n",
                "        accuracy_score, average_precision_score, balanced_accuracy_score,\n",
                "        confusion_matrix, f1_score, matthews_corrcoef, precision_score,\n",
                "        recall_score, roc_auc_score\n",
                "    )\n",
                "    records = [json.loads(line) for line in output.read_text(encoding='utf-8').splitlines() if line.strip()]\n",
                "    actual = [r for r in records if r.get('response_valid', True)]\n",
                "    truth = [r['label'] for r in actual]\n",
                "    predicted = [int(r['raw']) for r in actual if str(r.get('raw', '')).strip() in ('0', '1')]\n",
                "    metrics = {\n",
                "        'n_total': len(records),\n",
                "        'n_score_valid': sum(bool(r['valid']) for r in records),\n",
                "        'n_response_valid': len(actual),\n",
                "        'response_coverage': len(actual) / len(records) if records else None,\n",
                "        'accuracy': None, 'balanced_accuracy': None, 'precision': None, 'recall': None,\n",
                "        'f1': None, 'mcc': None, 'confusion_matrix': None, 'auroc': None, 'auprc': None\n",
                "    }\n",
                "    if actual and len(predicted) == len(truth):\n",
                "        metrics.update(\n",
                "            accuracy=float(accuracy_score(truth, predicted)),\n",
                "            balanced_accuracy=float(balanced_accuracy_score(truth, predicted)),\n",
                "            precision=float(precision_score(truth, predicted, zero_division=0)),\n",
                "            recall=float(recall_score(truth, predicted, zero_division=0)),\n",
                "            f1=float(f1_score(truth, predicted, zero_division=0)),\n",
                "            mcc=float(matthews_corrcoef(truth, predicted)),\n",
                "            confusion_matrix=confusion_matrix(truth, predicted, labels=[0, 1]).tolist()\n",
                "        )\n",
                "    score_rows = [r for r in records if r['valid']]\n",
                "    if score_rows and len({r['label'] for r in score_rows}) == 2:\n",
                "        labels = [r['label'] for r in score_rows]\n",
                "        scores = [r['s'] for r in score_rows]\n",
                "        metrics.update(\n",
                "            auroc=float(roc_auc_score(labels, scores)),\n",
                "            auprc=float(average_precision_score(labels, scores))\n",
                "        )\n",
                "    return metrics\n",
                "\n",
                "\n",
                "def run_batch(runs, model_path, model_revision, gpu_layers, limit, deadline_epoch,\n",
                "              checkpoint_reserve_seconds, status_path, seed, expected_model_sha256, arm):\n",
                "    from llama_cpp import __version__ as llama_version\n",
                "    from transformers import AutoTokenizer\n",
                "    if llama_version != RUNTIME['backend_source']['version']:\n",
                "        raise ValueError(f'Backend version mismatch: {llama_version}')\n",
                "\n",
                "    started = time.time()\n",
                "    stop_at = deadline_epoch - checkpoint_reserve_seconds\n",
                "    status_path = Path(status_path)\n",
                "    status_path.parent.mkdir(parents=True, exist_ok=True)\n",
                "    status = {\n",
                "        'state': 'starting', 'timed_out': False,\n",
                "        'started_at': datetime.fromtimestamp(started, timezone.utc).isoformat(),\n",
                "        'deadline_at': datetime.fromtimestamp(deadline_epoch, timezone.utc).isoformat(),\n",
                "        'stop_new_records_at': datetime.fromtimestamp(stop_at, timezone.utc).isoformat(),\n",
                "        'max_runtime_hours': (deadline_epoch - started) / 3600,\n",
                "        'checkpoint_reserve_seconds': checkpoint_reserve_seconds,\n",
                "        'runs': {}, 'completed_records_total': 0\n",
                "    }\n",
                "    for dataset, split, bundle, out in runs:\n",
                "        key = f'{dataset}/{split}'\n",
                "        status['runs'][key] = {'state': 'pending', 'bundle': bundle, 'output': out}\n",
                "    write_json_atomic(status_path, status)\n",
                "\n",
                "    def stop_for_deadline(current=None):\n",
                "        status['state'] = 'timed_out'\n",
                "        status['timed_out'] = True\n",
                "        status['timed_out_at'] = datetime.now(timezone.utc).isoformat()\n",
                "        status['stopped_after_run'] = current\n",
                "        write_json_atomic(status_path, status)\n",
                "\n",
                "    if time.time() >= stop_at:\n",
                "        stop_for_deadline(None)\n",
                "        return\n",
                "\n",
                "    model_path = Path(model_path)\n",
                "    model_digest = sha256(model_path)\n",
                "    if model_digest != expected_model_sha256:\n",
                "        raise ValueError('Model SHA256 mismatch with runtime contract')\n",
                "    if model_revision == 'local-input':\n",
                "        model_revision = f'local-sha256:{model_digest}'\n",
                "\n",
                "    first_manifest, _ = load_bundle(runs[0][2])\n",
                "    tokenizer = AutoTokenizer.from_pretrained(first_manifest['tokenizer'], revision=first_manifest['tokenizer_revision'])\n",
                "\n",
                "    provenance_root = status_path.parent / 'runtime_provenance'\n",
                "    provenance_root.mkdir(exist_ok=True)\n",
                "    session = Path(tempfile.mkdtemp(prefix=f'seed_{seed}_', dir=provenance_root))\n",
                "    provenance_file = session / 'runtime_provenance.json'\n",
                "    offload_log = session / 'model_load_offload.log'\n",
                "    runtime_info = provenance(RUNTIME, __file__, provenance_file)\n",
                "    build_log = Path('/kaggle/working/grace_diagnostics/install_llama_cuda.log')\n",
                "    if build_log.exists():\n",
                "        runtime_info['backend_build_log_sha256'] = digest(build_log)\n",
                "        build_lines = build_log.read_text(encoding='utf-8', errors='replace').splitlines()\n",
                "        runtime_info['backend_build_report'] = [\n",
                "            line.strip() for line in build_lines\n",
                "            if any(key in line for key in ('using CMake', 'compiler identification', 'Created wheel for llama-cpp-python'))\n",
                "        ]\n",
                "\n",
                "    llm = load_locked_model(RUNTIME, model_path, first_manifest, gpu_layers, offload_log, model_digest)\n",
                "    runtime_info['gpu_after_load'] = command([\n",
                "        'nvidia-smi', '--query-gpu=index,uuid,name,memory.free,memory.total,driver_version', '--format=csv,noheader',\n",
                "    ])\n",
                "    runtime_info['offload_log_sha256'] = digest(offload_log)\n",
                "    write_json_atomic(provenance_file, runtime_info)\n",
                "    provenance_ref = provenance_file.relative_to(status_path.parent).as_posix()\n",
                "\n",
                "    if time.time() >= stop_at:\n",
                "        stop_for_deadline(None)\n",
                "        return\n",
                "\n",
                "    label_ids = []\n",
                "    for label in ('0', '1'):\n",
                "        hf_ids = tokenizer.encode(label, add_special_tokens=False)\n",
                "        gguf_ids = llm.tokenize(label.encode(), add_bos=False, special=False)\n",
                "        if len(hf_ids) != 1 or hf_ids != gguf_ids:\n",
                "            raise ValueError(f'Label token mismatch for {label}: HF={hf_ids}, GGUF={gguf_ids}')\n",
                "        label_ids.append(hf_ids[0])\n",
                "    if label_ids[0] == label_ids[1]:\n",
                "        raise ValueError('Label token IDs must differ')\n",
                "\n",
                "    status['state'] = 'running'\n",
                "    write_json_atomic(status_path, status)\n",
                "\n",
                "    for dataset, split, bundle, out_text in runs:\n",
                "        key = f'{dataset}/{split}'\n",
                "        out = Path(out_text)\n",
                "        out.mkdir(parents=True, exist_ok=True)\n",
                "        manifest, rows = load_bundle(bundle)\n",
                "        if (manifest.get('arm'), manifest.get('seed'), manifest['dataset'], manifest['split']) != (arm, seed, dataset, split):\n",
                "            raise ValueError(f'Bundle identity mismatch for {key}: {manifest[\"dataset\"]}/{manifest[\"split\"]}')\n",
                "        if limit is not None:\n",
                "            rows = rows[:limit]\n",
                "        identity = {\n",
                "            'bundle_sha256': sha256(bundle),\n",
                "            'prompt_set_sha256': manifest['prompts_sha256'],\n",
                "            'model_sha256': model_digest,\n",
                "            'model_repo': manifest['model_repo'],\n",
                "            'quantization': manifest['quantization'],\n",
                "            'model_file': model_path.name,\n",
                "            'llama_cpp_python': llama_version,\n",
                "            'model_repo_revision': model_revision,\n",
                "            'tokenizer': manifest['tokenizer'],\n",
                "            'tokenizer_revision': manifest['tokenizer_revision'],\n",
                "            'gpu_layers': gpu_layers,\n",
                "            'context_tokens': manifest['prompt_budget_tokens'],\n",
                "            'scoring': RUNTIME['scoring']['name'],\n",
                "            'limit': limit,\n",
                "            'runtime_contract_sha256': EXPECTED_CONTRACT_SHA256,\n",
                "            'constructor': RUNTIME['constructor'],\n",
                "            'backend_sdist_sha256': RUNTIME['backend_source']['sdist_sha256'],\n",
                "            'python': platform.python_version(),\n",
                "            'dataset': dataset,\n",
                "            'split': split,\n",
                "            'arm': arm,\n",
                "            'prompt_seed': seed\n",
                "        }\n",
                "        identity_file = out / 'run_manifest.json'\n",
                "        previous_identity = json.loads(identity_file.read_text(encoding='utf-8')) if identity_file.exists() else None\n",
                "        if previous_identity is not None:\n",
                "            ignored = {'bundle_sha256', 'prompt_set_sha256', 'python'}\n",
                "            previous_stable = {k: v for k, v in previous_identity.items() if k not in ignored}\n",
                "            current_stable = {k: v for k, v in identity.items() if k not in ignored}\n",
                "            if previous_stable != current_stable:\n",
                "                raise ValueError(f'Existing output has different model/run settings for {key}; use a new OUT_ROOT')\n",
                "            if ('prompt_set_sha256' in previous_identity and\n",
                "                    previous_identity['prompt_set_sha256'] != identity['prompt_set_sha256']):\n",
                "                raise ValueError(f'Prompt bundle content changed for {key}; refusing to resume')\n",
                "\n",
                "        output = out / 'records.jsonl'\n",
                "        done = {}\n",
                "        if output.exists():\n",
                "            for line in output.read_text(encoding='utf-8').splitlines():\n",
                "                if line.strip():\n",
                "                    row = json.loads(line)\n",
                "                    row_id = str(row['id'])\n",
                "                    if row_id in done:\n",
                "                        raise ValueError(f'Duplicate checkpoint ID in {key}: {row_id}')\n",
                "                    done[row_id] = row\n",
                "        expected_ids = {str(item['id']) for item in rows}\n",
                "        unexpected_ids = set(done) - expected_ids\n",
                "        if unexpected_ids:\n",
                "            raise ValueError(f'Checkpoint contains IDs absent from current bundle {key}: {sorted(unexpected_ids)[:10]}')\n",
                "        for item in rows:\n",
                "            row_id = str(item['id'])\n",
                "            if row_id in done:\n",
                "                if done[row_id].get('prompt_sha256') != item['prompt_sha256']:\n",
                "                    raise ValueError(f'Checkpoint prompt mismatch: {key}/{row_id}')\n",
                "                if done[row_id].get('model_sha256') != model_digest:\n",
                "                    raise ValueError(f'Checkpoint model hash mismatch: {key}/{row_id}')\n",
                "\n",
                "        identity_file.write_text(json.dumps(identity, indent=2), encoding='utf-8')\n",
                "        progress = status['runs'][key]\n",
                "        progress.update(state='running', count=len(rows), completed=len(done),\n",
                "                        records_path=str(output), bundle_sha256=identity['bundle_sha256'])\n",
                "        status['completed_records_total'] = sum(x.get('completed', 0) for x in status['runs'].values())\n",
                "        write_json_atomic(status_path, status)\n",
                "\n",
                "        with output.open('a', encoding='utf-8', newline='\\n') as f:\n",
                "            for item in rows:\n",
                "                row_id = str(item['id'])\n",
                "                if row_id in done:\n",
                "                    continue\n",
                "                if time.time() >= stop_at:\n",
                "                    progress.update(state='checkpointed', completed=len(done))\n",
                "                    status['completed_records_total'] = sum(x.get('completed', 0) for x in status['runs'].values())\n",
                "                    stop_for_deadline(key)\n",
                "                    return\n",
                "                prompt = item['prompt']\n",
                "                if hashlib.sha256(prompt.encode('utf-8')).hexdigest() != item['prompt_sha256']:\n",
                "                    raise ValueError(f'Prompt hash mismatch: {key}/{row_id}')\n",
                "                messages = [{'role': 'user', 'content': prompt}]\n",
                "                chat = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)\n",
                "                hf_ids = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True, return_dict=False)\n",
                "                gguf_ids = llm.tokenize(chat.encode('utf-8'), add_bos=False, special=True)\n",
                "                if list(hf_ids) != gguf_ids:\n",
                "                    raise ValueError(f'Tokenizer mismatch at {key}/{row_id}; abort')\n",
                "                if len(gguf_ids) > manifest['prompt_budget_tokens']:\n",
                "                    raise ValueError(f'Token budget exceeded at {key}/{row_id}: {len(gguf_ids)} > {manifest[\"prompt_budget_tokens\"]}')\n",
                "\n",
                "                start = time.monotonic()\n",
                "                llm.reset()\n",
                "                llm.eval(gguf_ids)\n",
                "                scores = binary_scores(llm.scores[llm.n_tokens - 1], label_ids)\n",
                "                raw = llm.detokenize([scores['greedy_token_id']]).decode('utf-8', errors='replace').strip()\n",
                "                row = {k: item[k] for k in ('id', 'dataset', 'split', 'label', 'prompt_sha256') if k in item}\n",
                "                row.update(scores, arm=arm, raw=raw, response_valid=raw in ('0', '1'), valid=True,\n",
                "                           token_ids={'0': label_ids[0], '1': label_ids[1]}, model_sha256=model_digest,\n",
                "                           backend='llama-cpp-python', quantization='Q4_K_M', model_repo=manifest['model_repo'],\n",
                "                           model_repo_revision=model_revision, seed=seed, timestamp=datetime.now(timezone.utc).isoformat(),\n",
                "                           logprob_distribution='unconstrained_first_token', elapsed_s=time.monotonic() - start)\n",
                "                row.update(runtime_contract_sha256=EXPECTED_CONTRACT_SHA256,\n",
                "                           inference_seed=RUNTIME['constructor']['seed'], runtime_provenance=provenance_ref)\n",
                "                f.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + '\\n')\n",
                "                f.flush()\n",
                "                os.fsync(f.fileno())\n",
                "                done[row_id] = row\n",
                "                progress['completed'] = len(done)\n",
                "                status['completed_records_total'] = sum(x.get('completed', 0) for x in status['runs'].values())\n",
                "                status['last_checkpoint_at'] = datetime.now(timezone.utc).isoformat()\n",
                "                write_json_atomic(status_path, status)\n",
                "                if time.time() >= stop_at:\n",
                "                    progress['state'] = 'checkpointed'\n",
                "                    stop_for_deadline(key)\n",
                "                    return\n",
                "\n",
                "        metrics = evaluate_output(output)\n",
                "        (out / 'evaluation.json').write_text(json.dumps(metrics, indent=2, allow_nan=False), encoding='utf-8')\n",
                "        progress.update(state='complete', completed=len(rows), evaluation=str(out / 'evaluation.json'))\n",
                "        status['completed_records_total'] = sum(x.get('completed', 0) for x in status['runs'].values())\n",
                "        write_json_atomic(status_path, status)\n",
                "\n",
                "    status['state'] = 'complete'\n",
                "    status['timed_out'] = False\n",
                "    status['completed_at'] = datetime.now(timezone.utc).isoformat()\n",
                "    write_json_atomic(status_path, status)\n",
                "\n",
                "\n",
                "if __name__ == '__main__':\n",
                "    ap = argparse.ArgumentParser()\n",
                "    ap.add_argument('--model', required=True)\n",
                "    ap.add_argument('--seed', type=int, required=True)\n",
                "    ap.add_argument('--arm', required=True)\n",
                "    ap.add_argument('--expected-model-sha256', required=True)\n",
                "    ap.add_argument('--model-revision', required=True)\n",
                "    ap.add_argument('--gpu-layers', type=int, default=-1)\n",
                "    ap.add_argument('--limit', type=int)\n",
                "    ap.add_argument('--deadline-epoch', type=float, required=True)\n",
                "    ap.add_argument('--checkpoint-reserve-seconds', type=int, default=300)\n",
                "    ap.add_argument('--status', required=True)\n",
                "    ap.add_argument('--run', action='append', nargs=4, metavar=('DATASET', 'SPLIT', 'BUNDLE', 'OUT'), required=True)\n",
                "    args = ap.parse_args()\n",
                "    run_batch(args.run, args.model, args.model_revision, args.gpu_layers, args.limit,\n",
                "              args.deadline_epoch, args.checkpoint_reserve_seconds, args.status, args.seed, args.expected_model_sha256, args.arm)\n"
            ]
        },
        # Cell 9: Main Execution Loop & Artifact Sealing
        {
            "cell_type": "code",
            "execution_count": None,
            "id": "c09_execute_batch",
            "metadata": {},
            "outputs": [],
            "source": [
                "deadline = SESSION_STARTED + MAX_RUNTIME_HOURS * 3600\n",
                "status = OUT_ROOT / f'seed_{SEED}_status.json'\n",
                "\n",
                "# Search model path\n",
                "model_files = sorted(path for path in KAGGLE_INPUT_ROOT.rglob(MODEL_FILENAME) if path.is_file())\n",
                "if len(model_files) != 1:\n",
                "    raise FileNotFoundError(f'Need exactly one {MODEL_FILENAME} in Kaggle Input; found: {list(map(str, model_files))}')\n",
                "model_path = str(model_files[0])\n",
                "revision = 'local-input'\n",
                "note(f'Using model input: {model_path}')\n",
                "\n",
                "records_done = validate_records()\n",
                "note(f'Records already done in checkpoint: {records_done}/{EXPECTED_COUNT}')\n",
                "\n",
                "state = 'error'\n",
                "try:\n",
                "    if records_done < EXPECTED_COUNT:\n",
                "        command = [\n",
                "            sys.executable, '-u', '/kaggle/working/kaggle_inference.py',\n",
                "            '--model', model_path, '--model-revision', revision,\n",
                "            '--seed', str(SEED), '--arm', ARM, '--expected-model-sha256', MODEL_SHA256,\n",
                "            '--gpu-layers', str(GPU_LAYERS), '--deadline-epoch', str(deadline),\n",
                "            '--checkpoint-reserve-seconds', str(CHECKPOINT_RESERVE_SECONDS), '--status', str(status),\n",
                "            '--run', DATASET, SPLIT, str(bundle_file), str(OUT_ROOT / f'seed_{SEED}' / DATASET / SPLIT)\n",
                "        ]\n",
                "        run_logged(command, f'inference_seed_{SEED}')\n",
                "    records_done = validate_records()\n",
                "    complete = (records_done == EXPECTED_COUNT)\n",
                "    state = 'validation_complete' if complete else 'timed_out'\n",
                "finally:\n",
                "    summary = {\n",
                "        'runtime_contract_sha256': EXPECTED_CONTRACT_SHA256,\n",
                "        'arm': ARM,\n",
                "        'state': state,\n",
                "        'split': SPLIT,\n",
                "        'bundle_sha256': bundle_manifest.get('manifest_seal_sha256'),\n",
                "        'records_completed': records_done,\n",
                "        'expected_total': EXPECTED_COUNT,\n",
                "        'historical_threshold_applied': False,\n",
                "    }\n",
                "    (OUT_ROOT / 'batch_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')\n",
                "    archive = shutil.make_archive(str(Path('/kaggle/working') / CHECKPOINT_NAME.removesuffix('.zip')),\n",
                "                                  'zip', root_dir=OUT_ROOT)\n",
                "    print(state, archive)\n",
                "    diagnostics_zip()\n"
            ]
        }
    ]

    nb_payload = {
        "cells": cells,
        "metadata": {
            "kaggle": {
                "accelerator": "nvidiaTeslaT4",
                "isGpuEnabled": True,
                "isInternetEnabled": True,
                "language": "python",
                "sourceType": "notebook"
            },
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {
                    "name": "ipython",
                    "version": 3
                },
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.13"
            },
            "grace_runtime_lock": {
                "contract_id": "grace_qwen_q4_runtime_v1",
                "sha256": "4c9c3bcff5e9fd32532d7edf85df7a961e45ec9c64bee3df8833d986a2eb276e",
                "source": "configs/inference_runtime_lock.json"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }

    nb_path = DELIVERY_DIR / "notebook.ipynb"
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb_payload, f, indent=1, ensure_ascii=False)

    print(f"Canonical notebook written: {nb_path} ({len(cells)} cells)")
    return nb_path


def build_kernel_metadata(account: str = "huuhieu") -> Path:
    print(f"=== Step 4: Generating kernel-metadata.json (Target Account: {account}) ===")
    meta = {
        "id": f"{account}/grace-b3-amended-devign-val",
        "title": "grace-b3-amended-devign-val",
        "code_file": "notebook.ipynb",
        "language": "python",
        "kernel_type": "notebook",
        "is_private": "true",
        "enable_gpu": "true",
        "enable_internet": "true",
        "dataset_sources": [
            f"{account}/qwen3-coder-30b-a3b-instruct-q4-k-m",
            f"{account}/grace-b3-devign-val-inputs"
        ],
        "competition_sources": [],
        "kernel_sources": []
    }
    km_path = DELIVERY_DIR / "kernel-metadata.json"
    with open(km_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    return km_path


def build_dataset_metadata(account: str = "huuhieu") -> Path:
    print(f"=== Step 4b: Generating dataset-metadata.json (Target Account: {account}) ===")
    dataset_dir = DELIVERY_DIR / "dataset"
    dataset_dir.mkdir(parents=True, exist_ok=True)
    accounts_dir = DELIVERY_DIR / "accounts"
    accounts_dir.mkdir(parents=True, exist_ok=True)

    slug = "grace-b3-devign-val-inputs"
    title = "grace-b3-devign-val-inputs"

    meta = {
        "id": f"{account}/{slug}",
        "title": title,
        "licenses": [
            {
                "name": "CC0-1.0"
            }
        ],
        "isPrivate": True
    }

    # 1. Main dataset metadata in delivery/dataset/
    dm_path = dataset_dir / "dataset-metadata.json"
    with open(dm_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    # 2. Also place directly in delivery/ root for flat dataset deploy
    with open(DELIVERY_DIR / "dataset-metadata.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    # 3. Pre-configure per-account variant metadata for flexible switching
    for acc in ("huuhieu", "huuhieu3333", "tomandjerry223"):
        acc_meta = {
            "id": f"{acc}/{slug}",
            "title": title,
            "licenses": [{"name": "CC0-1.0"}],
            "isPrivate": True
        }
        with open(accounts_dir / f"dataset-metadata.{acc}.json", "w", encoding="utf-8") as f:
            json.dump(acc_meta, f, indent=2, ensure_ascii=False)

    # 4. Copy bundle zip to dataset folder for direct 'kaggle datasets create -p delivery/dataset' compatibility
    if BUNDLE_ZIP_PATH.is_file():
        dest_zip = dataset_dir / "b3_devign_val_input.zip"
        if not dest_zip.exists() or dest_zip.stat().st_size != BUNDLE_ZIP_PATH.stat().st_size:
            shutil.copy2(BUNDLE_ZIP_PATH, dest_zip)

    # 5. Staging directories for supported target accounts
    for acc in ("huuhieu", "huuhieu3333", "tomandjerry223"):
        stg_dir = ROOT / "Runs-management" / f"kaggle_staging_{acc}" / "dataset_b3_devign_val_inputs"
        stg_dir.mkdir(parents=True, exist_ok=True)
        acc_meta = {
            "id": f"{acc}/{slug}",
            "title": title,
            "licenses": [{"name": "CC0-1.0"}],
            "isPrivate": True
        }
        with open(stg_dir / "dataset-metadata.json", "w", encoding="utf-8") as f:
            json.dump(acc_meta, f, indent=2, ensure_ascii=False)
        if BUNDLE_ZIP_PATH.is_file():
            stg_zip = stg_dir / "b3_devign_val_input.zip"
            if not stg_zip.exists() or stg_zip.stat().st_size != BUNDLE_ZIP_PATH.stat().st_size:
                shutil.copy2(BUNDLE_ZIP_PATH, stg_zip)

    print(f"Dataset metadata created: {dm_path} (ID: {meta['id']})")
    return dm_path


def build_delivery_manifest():
    print("=== Step 5: Sealing Delivery Manifest ===")
    artifacts = {
        "notebook.ipynb": compute_file_sha256(DELIVERY_DIR / "notebook.ipynb"),
        "b3_devign_val_input.zip": compute_file_sha256(DELIVERY_DIR / "b3_devign_val_input.zip"),
        "kernel-metadata.json": compute_file_sha256(DELIVERY_DIR / "kernel-metadata.json"),
        "inference_input_manifest.json": compute_file_sha256(DELIVERY_DIR / "inference_input_manifest.json"),
    }

    dm = {
        "schema_version": 1,
        "release_id": "release_20261108_v5",
        "release_version": "v5_devign_validation_locked",
        "parent_release": "release_20261108_v4",
        "release_status": "FROZEN",
        "method_id": "b3-verified-patch-v1",
        "scope": {
            "dataset": "devign",
            "split": "validation",
            "arm": "B3",
            "prompt_seed": 42,
            "count": 2732,
        },
        "artifacts_sha256": artifacts,
        "created_at_utc": "2026-11-08T14:49:37.899940+00:00",
    }

    dm_body = {k: v for k, v in dm.items() if k != "delivery_seal_sha256"}
    seal = compute_bytes_sha256(json.dumps(dm_body, sort_keys=True, ensure_ascii=False, indent=2).encode("utf-8"))
    dm["delivery_seal_sha256"] = seal

    dm_path = DELIVERY_DIR / "delivery_manifest.json"
    with open(dm_path, "w", encoding="utf-8") as f:
        json.dump(dm, f, indent=2, ensure_ascii=False)

    print(f"Delivery manifest sealed: {seal}")
    return dm_path, seal


def main(account: str = "huuhieu"):
    import argparse
    parser = argparse.ArgumentParser(description="Build delivery bundle for B3 Release v5.")
    parser.add_argument("--account", default=account, choices=["huuhieu", "huuhieu3333", "tomandjerry223"],
                        help="Target Kaggle account (default: huuhieu)")
    args, unknown = parser.parse_known_args()
    target_account = args.account

    DELIVERY_DIR.mkdir(parents=True, exist_ok=True)
    zip_sha, bundle_manifest = build_input_bundle()
    build_inference_input_manifest(zip_sha, bundle_manifest)
    build_canonical_notebook()
    build_kernel_metadata(account=target_account)
    build_dataset_metadata(account=target_account)
    build_delivery_manifest()
    print("\n=======================================================")
    print("B3 RELEASE v5 DELIVERY BUNDLE SEALED SUCCESSFULLY!")
    print(f"Target Kaggle Account: {target_account}")
    print("=======================================================\n")


if __name__ == "__main__":
    main()
