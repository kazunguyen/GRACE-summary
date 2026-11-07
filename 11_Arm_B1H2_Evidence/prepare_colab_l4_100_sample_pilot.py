from __future__ import annotations

import hashlib
import json
import random
import zipfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARM = ROOT / "11_Arm_B1H2_Evidence"
SOURCE_ZIP = ROOT.parent / "grace_15arms_prompts_and_clean_specs (1).zip"
PILOT = ARM / "colab_l4_pilot_20261106"
BUNDLES = PILOT / "bundles"
NOTEBOOKS = ARM / "notebooks"
SEED = 20261106
PER_DATASET = 50
TOKENIZER_REVISION = "b2cff646eb4bb1d68355c01b18ae02e7cf42d120"
MODEL_SHA256 = "f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335"
MODEL_REPO = "ggml-org/Qwen3-Coder-30B-A3B-Instruct-GGUF"
MODEL_FILE = "Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf"

SOURCE_MEMBERS = {
    "devign": "prompts/dry_run_validation_20261102/devign/validation/B1-H2/42/prompts.jsonl",
    "reveal": "prompts/dry_run_validation_20261102/reveal/validation/B1-H2/42/prompts.jsonl",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def notebook_cell(cell_type: str, source: str) -> dict:
    base = {"cell_type": cell_type, "metadata": {}, "source": source.splitlines(keepends=True)}
    if cell_type == "code":
        base.update(execution_count=None, outputs=[])
    return base


def build_notebook() -> dict:
    cells = [
        notebook_cell("markdown", """# B1-H2 L4 pilot — 100 validation prompts\n\nThis is an **exploratory hardware and scoring pilot**, not a confirmatory result and not for threshold fitting. It samples 50 Devign and 50 ReVeal prompts from Hiếu's original B1-H2 validation packet (seed 42), preserving the prompts byte-for-byte. The model and tokenizer hashes, context and first-token scoring follow the registered Kaggle configuration.\n\nBefore running: in Runtime → Change runtime type select **Runtime Version 2026.10 (Python 3.13.x)** and **GPU L4**, then reconnect. Use Colab Runtime Version 2026.10 with Python 3.13.x; record the exact Python patch version because Colab may report a different patch from Kaggle (3.13.15). Kaggle recorded NumPy 2.1.3. The setup cell checks Python and GPU before mounting Drive or installing anything. After any runtime reconnect, run cells from the top: the dependency cell compiles and installs `llama-cpp-python` for CUDA before the model-load cell imports it. This notebook downloads the original Q4_K_M checkpoint, checks its SHA-256, builds `llama-cpp-python==0.3.16` for L4 (SM 8.9), captures native load/offload logs, and stores per-row `logprob_0`/`logprob_1`. If L4 cannot fully offload or load, use Runtime → Change runtime type and choose A100 or G4, keeping Runtime Version 2026.10, then rerun the notebook.\n\nBundle đã được tải lên Google Drive: [b1h2_l4_100_sample_bundle.zip](https://drive.google.com/file/d/1LWGkH3tmNgWml8s_JTR7A-0ynYb0__L_/view?usp=drivesdk). Notebook đọc file từ `My Drive/GRACE_B1H2_COLAB_L4_PILOT_20261106/` và ghi log/kết quả vào thư mục con `l4_pilot_output/`.\n"""),
        notebook_cell("code", """from pathlib import Path\nimport os, sys, json, hashlib, zipfile, subprocess, platform, time, re, shutil, math, contextlib, io, importlib.metadata\nfrom datetime import datetime, timezone\n\nif sys.version_info[:2] != (3, 13):\n    raise RuntimeError(f'Requires Colab Runtime Version 2026.10 / Python 3.13.x to match the Kaggle Python 3.13 runtime family; got {sys.version.split()[0]}. In Runtime → Change runtime type choose Runtime Version 2026.10, then reconnect and run from the top.')\n_nvidia_smi = shutil.which('nvidia-smi') or ( '/usr/local/cuda/bin/nvidia-smi' if Path('/usr/local/cuda/bin/nvidia-smi').is_file() else None)\nif _nvidia_smi:\n    _preflight_gpu = subprocess.run([_nvidia_smi, '--query-gpu=name', '--format=csv,noheader'], check=True, text=True, capture_output=True).stdout.strip()\nelse:\n    try:\n        import torch\n    except ImportError as exc:\n        raise RuntimeError('Cannot detect GPU: nvidia-smi is missing and PyTorch is unavailable. Select Runtime → Change runtime type → GPU L4, reconnect, then run again.') from exc\n    if not torch.cuda.is_available():\n        raise RuntimeError('Colab has not attached a CUDA GPU (nvidia-smi missing and torch.cuda.is_available() is False). Select GPU L4 in Runtime → Change runtime type, reconnect, then run again.')\n    _preflight_gpu = torch.cuda.get_device_name(0)\nif 'L4' not in _preflight_gpu.upper():\n    raise RuntimeError(f'This pilot is configured for L4; selected runtime reports {_preflight_gpu!r}. Select GPU L4 and reconnect.')\nprint(f'Preflight passed: Python {sys.version.split()[0]}, GPU {_preflight_gpu}')\n\nWORK = Path('/content/b1h2_l4_pilot')\nWORK.mkdir(parents=True, exist_ok=True)\nDRIVE_DIR = Path('/content/drive/MyDrive/GRACE_B1H2_COLAB_L4_PILOT_20261106')\nBUNDLE_DRIVE_URL = 'https://drive.google.com/file/d/1LWGkH3tmNgWml8s_JTR7A-0ynYb0__L_/view?usp=drivesdk'\nBUNDLE_PATH = DRIVE_DIR / 'b1h2_l4_100_sample_bundle.zip'\nOUT = DRIVE_DIR / 'l4_pilot_output'\nEVENTS = OUT / 'events.log'\nPILOT_START = time.monotonic()\nMAX_RUNTIME_SECONDS = 10 * 60 * 60\n\ndef note(msg):\n    line = f'[{datetime.now(timezone.utc).isoformat()}] {msg}'\n    print(line, flush=True)\n    with EVENTS.open('a', encoding='utf-8') as f: f.write(line + '\\n')\n\nfrom google.colab import drive\ndrive.mount('/content/drive')\nDRIVE_DIR.mkdir(parents=True, exist_ok=True)\nOUT.mkdir(parents=True, exist_ok=True)\nif not BUNDLE_PATH.is_file():\n    raise FileNotFoundError(f'Upload the bundle to Drive first: {BUNDLE_PATH}')\nnote(f'Bundle: {BUNDLE_PATH}; output: {OUT}')\n"""),
        notebook_cell("code", """# Record runtime facts; nvidia-smi is optional if torch can identify the assigned GPU.\n_nvidia_smi = shutil.which('nvidia-smi') or ('/usr/local/cuda/bin/nvidia-smi' if Path('/usr/local/cuda/bin/nvidia-smi').is_file() else None)\nif _nvidia_smi:\n    gpu = subprocess.run([_nvidia_smi, '--query-gpu=name,memory.total,driver_version', '--format=csv,noheader'], check=True, text=True, capture_output=True).stdout.strip()\n    (OUT / 'runtime_nvidia_smi.txt').write_text(subprocess.run([_nvidia_smi], check=True, text=True, capture_output=True).stdout, encoding='utf-8')\nelse:\n    import torch\n    if not torch.cuda.is_available(): raise RuntimeError('CUDA GPU unavailable; reconnect with GPU L4 selected.')\n    props = torch.cuda.get_device_properties(0)\n    gpu = f'{torch.cuda.get_device_name(0)}, {props.total_memory / (1024**2):.0f} MiB; nvidia-smi unavailable'\n    (OUT / 'runtime_nvidia_smi.txt').write_text(gpu + '\\n', encoding='utf-8')\nif 'L4' not in gpu.upper(): raise RuntimeError(f'Expected L4, got {gpu!r}; select GPU L4 and reconnect.')\nprint(gpu)\n_nvcc = shutil.which('nvcc') or ('/usr/local/cuda/bin/nvcc' if Path('/usr/local/cuda/bin/nvcc').is_file() else None)\nif not _nvcc: raise RuntimeError('CUDA GPU found but nvcc is missing. Reconnect to a Colab GPU runtime with the CUDA toolkit, then rerun.')\nfor cmd, name in [([_nvcc, '--version'], 'nvcc_version.txt'), ([sys.executable, '--version'], 'python_version.txt')]:\n    p = subprocess.run(cmd, text=True, capture_output=True)\n    (OUT / name).write_text(p.stdout + p.stderr, encoding='utf-8')\ntry:\n    memory_gib = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES') / (1024**3)\nexcept (AttributeError, OSError, ValueError):\n    memory_gib = None\nif memory_gib is not None:\n    (OUT / 'system_memory_gib.txt').write_text(f'{memory_gib:.2f} GiB\\n', encoding='utf-8')\n    print(f'System RAM: {memory_gib:.2f} GiB')\nnote(f'Confirmed Python {sys.version.split()[0]} and L4 runtime; GPU compute capability for this build is SM 8.9.')\n"""),
        notebook_cell("code", """# Pin Python inference dependencies to the registered/Kaggle versions, then compile CUDA for L4.\npackages = [\n    'numpy==2.1.3',\n    'huggingface-hub==0.36.2',\n    'tokenizers==0.22.2',\n    'transformers==4.57.1',\n    'scikit-learn==1.5.2',\n]\nwith (OUT / 'install_python_dependencies.log').open('w', encoding='utf-8') as log:\n    p = subprocess.Popen([sys.executable, '-m', 'pip', 'install', '--no-cache-dir', *packages], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)\n    for line in p.stdout:\n        log.write(line); log.flush(); print(line, end='', flush=True)\n    if p.wait() != 0: raise RuntimeError('Pinned Python dependency installation failed; see install_python_dependencies.log')\n\nos.environ['CMAKE_ARGS'] = '-DGGML_CUDA=on -DCMAKE_CUDA_ARCHITECTURES=89'\nos.environ['CMAKE_BUILD_PARALLEL_LEVEL'] = '2'\nos.environ['FORCE_CMAKE'] = '1'\nwith (OUT / 'install_llama_cpp_cuda.log').open('w', encoding='utf-8') as log:\n    cmd = [sys.executable, '-m', 'pip', 'install', '-v', '--no-cache-dir', '--no-binary', 'llama-cpp-python', 'llama-cpp-python==0.3.16']\n    log.write(f'Command: {cmd}\\nCMAKE_ARGS={os.environ["CMAKE_ARGS"]}\\n'); log.flush()\n    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, env=os.environ.copy())\n    for line in p.stdout:\n        log.write(line); log.flush(); print(line, end='', flush=True)\n    if p.wait() != 0: raise RuntimeError('CUDA build of llama-cpp-python failed; see install_llama_cpp_cuda.log')\n"""),
        notebook_cell("code", """# Verify archive, source prompts, fixed sample IDs, and registered checkpoint identity.\ndef sha256_file(path):\n    h = hashlib.sha256()\n    with open(path, 'rb') as f:\n        for b in iter(lambda: f.read(1024 * 1024), b''): h.update(b)\n    return h.hexdigest()\n\nwith zipfile.ZipFile(BUNDLE_PATH) as z:\n    bundle_manifest = json.loads(z.read('bundle_manifest.json'))\n    prompt_bytes = z.read('prompts.jsonl')\nif hashlib.sha256(prompt_bytes).hexdigest() != bundle_manifest['prompts_sha256']:\n    raise ValueError('Prompt bundle hash mismatch')\nrows = [json.loads(line) for line in prompt_bytes.decode('utf-8').splitlines() if line.strip()]\nif len(rows) != 100 or len({r['id'] for r in rows}) != 100:\n    raise ValueError('Expected 100 unique pilot prompts')\nif bundle_manifest['source_archive_sha256'] != 'SOURCE_ARCHIVE_SHA256':\n    raise ValueError('Unexpected source archive hash')\nfor row in rows:\n    if hashlib.sha256(row['prompt'].encode('utf-8')).hexdigest() != row['prompt_sha256']:\n        raise ValueError(f'Prompt hash mismatch: {row["id"]}')\nif {d: sum(r['dataset'] == d for r in rows) for d in ('devign','reveal')} != {'devign':50,'reveal':50}:\n    raise ValueError('Pilot sample must contain exactly 50 prompts per dataset')\nnote(f'Bundle verified: {len(rows)} prompts; prompts_sha256={bundle_manifest["prompts_sha256"]}')\n"""),
        notebook_cell("code", """# Download the registered GGUF and refuse a changed artifact.\nfrom huggingface_hub import hf_hub_download\nMODEL_REPO = 'ggml-org/Qwen3-Coder-30B-A3B-Instruct-GGUF'\nMODEL_FILE = 'Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf'\nMODEL_SHA256 = 'f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335'\nTOKENIZER_REPO = 'Qwen/Qwen3-Coder-30B-A3B-Instruct'\nTOKENIZER_REVISION = 'b2cff646eb4bb1d68355c01b18ae02e7cf42d120'\nmodel_path = Path(hf_hub_download(repo_id=MODEL_REPO, filename=MODEL_FILE, revision='main'))\nmodel_digest = sha256_file(model_path)\nif model_digest != MODEL_SHA256:\n    raise ValueError(f'GGUF SHA-256 mismatch: expected {MODEL_SHA256}, got {model_digest}')\nnote(f'Model verified: {model_path}; sha256={model_digest}; revision=local-sha256:{model_digest}')\n"""),
        notebook_cell("code", """# Capture native C/C++ stdout and stderr so the llama.cpp layer/buffer offload report is retained.\n@contextlib.contextmanager\ndef capture_native_fds(path):\n    path = Path(path)\n    with path.open('w', encoding='utf-8') as f:\n        sys.stdout.flush(); sys.stderr.flush()\n        saved = [os.dup(1), os.dup(2)]\n        try:\n            os.dup2(f.fileno(), 1); os.dup2(f.fileno(), 2)\n            yield\n        finally:\n            sys.stdout.flush(); sys.stderr.flush()\n            os.dup2(saved[0], 1); os.dup2(saved[1], 2)\n            os.close(saved[0]); os.close(saved[1])\n\ntry:\n    _llama_cpp_installed = importlib.metadata.version('llama-cpp-python')\nexcept importlib.metadata.PackageNotFoundError as exc:\n    raise RuntimeError('llama-cpp-python is not installed in this runtime. Run the earlier dependency/build cell (the one that compiles CUDA for L4) to completion, then rerun this cell. A runtime reconnect clears installed packages.') from exc\ntry:\n    _llama_cpp_installed = importlib.metadata.version('llama-cpp-python')\nexcept importlib.metadata.PackageNotFoundError as exc:\n    raise RuntimeError('llama-cpp-python is not installed in this runtime. Run the earlier dependency/build cell (the one that compiles CUDA for L4) to completion, then rerun this cell. A runtime reconnect clears installed packages.') from exc\nfrom transformers import AutoTokenizer\nfrom llama_cpp import Llama, __version__ as llama_cpp_version, llama_supports_gpu_offload\nif llama_cpp_version != '0.3.16': raise RuntimeError(f'Unexpected llama-cpp-python {llama_cpp_version}')\nif not llama_supports_gpu_offload(): raise RuntimeError('CUDA offload support is unavailable')\ntokenizer = AutoTokenizer.from_pretrained(TOKENIZER_REPO, revision=TOKENIZER_REVISION)\nlabel_ids = []\nfor label in ('0','1'):\n    ids = tokenizer.encode(label, add_special_tokens=False)\n    if len(ids) != 1: raise ValueError(f'Label {label} is not one token: {ids}')\n    label_ids.append(ids[0])\n\nload_started = time.monotonic()\nload_error = None\nllm = None\ntry:\n    with capture_native_fds(OUT / 'llama_cpp_model_load_offload.log'):\n        llm = Llama(model_path=str(model_path), n_ctx=8192, n_batch=256, n_gpu_layers=-1, logits_all=True, seed=42, verbose=True)\nexcept Exception as e:\n    load_error = repr(e)\n    note(f'Model load failed: {load_error}')\nif llm is None:\n    summary = {'status':'load_failed','error':load_error,'gpu':gpu,'model_sha256':model_digest,'llama_cpp_python':llama_cpp_version,'context_tokens':8192,'gpu_layers_requested':-1,'load_seconds':time.monotonic()-load_started}\n    (OUT / 'load_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')\n    shutil.make_archive(str(OUT), 'zip', root_dir=OUT)\n    raise RuntimeError('L4 could not load the model; inspect llama_cpp_model_load_offload.log, then retry on A100/G4.')\n\nfor label, hf_id in zip(('0','1'), label_ids):\n    gguf_ids = llm.tokenize(label.encode(), add_bos=False, special=False)\n    if gguf_ids != [hf_id]: raise ValueError(f'Label tokenizer mismatch for {label}: HF={hf_id}, GGUF={gguf_ids}')\n\nload_log = (OUT / 'llama_cpp_model_load_offload.log').read_text(encoding='utf-8', errors='replace')\noffload_lines = [line.strip() for line in load_log.splitlines() if 'offload' in line.lower() or 'buffer size' in line.lower()]\nlayer_reports = re.findall(r'offloaded\\s+(\\d+)\\s*/\\s*(\\d+)\\s+layers?\\s+to\\s+GPU', load_log, flags=re.I)\nall_layers_offloaded = bool(layer_reports) and any(int(a) >= int(b) for a,b in layer_reports)\nsummary = {'status':'loaded','gpu':gpu,'model_sha256':model_digest,'model_repo':MODEL_REPO,'model_revision':'local-sha256:'+model_digest,'quantization':'Q4_K_M','llama_cpp_python':llama_cpp_version,'transformers':importlib.metadata.version('transformers'),'huggingface_hub':importlib.metadata.version('huggingface-hub'),'tokenizers':importlib.metadata.version('tokenizers'),'numpy':importlib.metadata.version('numpy'),'tokenizer':TOKENIZER_REPO,'tokenizer_revision':TOKENIZER_REVISION,'context_tokens':8192,'n_batch':256,'gpu_layers_requested':-1,'logits_all':True,'layer_reports':layer_reports,'all_layers_offloaded':all_layers_offloaded,'offload_buffer_lines':offload_lines,'load_seconds':time.monotonic()-load_started,'source_archive_sha256':bundle_manifest['source_archive_sha256'],'bundle_sha256':sha256_file(BUNDLE_PATH),'bundle_drive_url':BUNDLE_DRIVE_URL,'prompts_sha256':bundle_manifest['prompts_sha256'],'n_prompts':100,'sample_seed':20261106,'pilot_only':True}\n(OUT / 'load_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')\nnote(f'Model loaded; all_layers_offloaded={all_layers_offloaded}; layer_reports={layer_reports}')\n"""),
        notebook_cell("code", """# Score 100 prompts with the canonical unconstrained first-token logprob method.\nimport numpy as np\n\ndef binary_scores(logits, ids):\n    values = np.asarray(logits, dtype=np.float64).reshape(-1)\n    if not np.all(np.isfinite(values)): raise ValueError('Non-finite logits')\n    m = float(np.max(values)); normalizer = m + float(np.log(np.exp(values-m).sum()))\n    lp0, lp1 = float(values[ids[0]]-normalizer), float(values[ids[1]]-normalizer)\n    s = float(np.exp(lp1-np.logaddexp(lp0,lp1)))\n    top = np.argsort(values)[-5:][::-1]\n    return {'logprob_0':lp0,'logprob_1':lp1,'p0':math.exp(lp0),'p1':math.exp(lp1),'s':s,'pred_argmax':int(s>=.5),'greedy_token_id':int(np.argmax(values)),'top5':[{'token_id':int(i),'logprob':float(values[i]-normalizer)} for i in top]}\n\nrecords_path = OUT / 'records.jsonl'\ndone = {}\nif records_path.exists():\n    for line in records_path.read_text(encoding='utf-8').splitlines():\n        if line.strip():\n            r = json.loads(line)\n            if r['id'] in done: raise ValueError(f'Duplicate checkpoint ID: {r["id"]}')\n            done[r['id']] = r\n\nwith records_path.open('a', encoding='utf-8', newline='\\n') as f:\n    for ix, item in enumerate(rows, 1):\n        if time.monotonic() - PILOT_START >= MAX_RUNTIME_SECONDS:\n            note('Reached the 10-hour safety limit; completed records are preserved for resume.')\n            break\n        if item['id'] in done:\n            if done[item['id']]['prompt_sha256'] != item['prompt_sha256']: raise ValueError('Checkpoint prompt mismatch')\n            continue\n        if hashlib.sha256(item['prompt'].encode('utf-8')).hexdigest() != item['prompt_sha256']: raise ValueError('Prompt hash mismatch')\n        chat = tokenizer.apply_chat_template([{'role':'user','content':item['prompt']}], tokenize=False, add_generation_prompt=True)\n        hf_ids = tokenizer.apply_chat_template([{'role':'user','content':item['prompt']}], tokenize=True, add_generation_prompt=True)\n        gguf_ids = llm.tokenize(chat.encode('utf-8'), add_bos=False, special=True)\n        if list(hf_ids) != gguf_ids: raise ValueError(f'Tokenizer mismatch at {item["id"]}')\n        if len(gguf_ids) > 8192: raise ValueError(f'Context overflow at {item["id"]}: {len(gguf_ids)}')\n        started = time.monotonic(); llm.reset(); llm.eval(gguf_ids)\n        scores = binary_scores(llm.scores[llm.n_tokens-1], label_ids)\n        raw = llm.detokenize([scores['greedy_token_id']]).decode('utf-8', errors='replace').strip()\n        row = {k:item[k] for k in ('id','dataset','split','arm','seed','prompt_variant','prompt_sha256')}\n        row.update(scores, raw=raw, response_valid=raw in ('0','1'), token_ids={'0':label_ids[0],'1':label_ids[1]}, prompt_tokens=len(gguf_ids), model_sha256=model_digest, model_repo=MODEL_REPO, model_repo_revision='local-sha256:'+model_digest, quantization='Q4_K_M', backend='llama-cpp-python', llama_cpp_python=llama_cpp_version, gpu=gpu, seed=42, elapsed_s=time.monotonic()-started, pilot_only=True)\n        f.write(json.dumps(row, ensure_ascii=False, allow_nan=False)+'\\n'); f.flush(); os.fsync(f.fileno())\n        note(f'[{ix}/100] {item["id"]}: logprob_0={scores["logprob_0"]:.6f} logprob_1={scores["logprob_1"]:.6f} s={scores["s"]:.6f} raw={raw!r}')\n\nstatus = {'status':'complete','expected':100,'gpu':gpu,'all_layers_offloaded':all_layers_offloaded,'runtime_cap_seconds':MAX_RUNTIME_SECONDS}\nstatus['records_written'] = sum(1 for line in records_path.read_text(encoding='utf-8').splitlines() if line.strip())\nstatus['status'] = 'complete' if status['records_written'] == 100 else 'incomplete_or_timed_out'\n(OUT / 'pilot_status.json').write_text(json.dumps(status, indent=2), encoding='utf-8')\narchive = shutil.make_archive(str(OUT), 'zip', root_dir=OUT)\nnote(f'Pilot output archive: {archive}')\n"""),
    ]
    return {
        "cells": cells,
        "metadata": {
            "colab": {"name": "colab_l4_b1h2_100_sample_pilot_20261106.ipynb", "provenance": []},
            "kernelspec": {"display_name": "Python 3", "name": "python3"},
            "language_info": {"name": "python", "version": "3.13"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def main() -> None:
    if not SOURCE_ZIP.is_file():
        raise FileNotFoundError(SOURCE_ZIP)
    archive_bytes = SOURCE_ZIP.read_bytes()
    archive_sha = sha256(archive_bytes)
    rng = random.Random(SEED)
    selected: list[dict] = []
    source_records = {}
    with zipfile.ZipFile(SOURCE_ZIP) as source:
        for dataset, member in SOURCE_MEMBERS.items():
            raw = source.read(member)
            records = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
            if len(records) != (2732 if dataset == "devign" else 2273):
                raise ValueError(f"Unexpected original prompt count for {dataset}: {len(records)}")
            for row in records:
                if row.get("dataset") != dataset or row.get("split") != "validation" or row.get("arm") != "B1-H2" or row.get("seed") != 42:
                    raise ValueError(f"Unexpected prompt provenance in {member}: {row.get('id')}")
                if hashlib.sha256(row["prompt"].encode("utf-8")).hexdigest() != row.get("prompt_sha256"):
                    raise ValueError(f"Original prompt hash mismatch: {row.get('id')}")
            chosen = sorted(rng.sample(records, PER_DATASET), key=lambda r: r["id"])
            selected.extend(chosen)
            source_records[dataset] = {"zip_member": member, "source_jsonl_sha256": sha256(raw), "source_count": len(records), "sample_count": len(chosen), "sample_ids": [r["id"] for r in chosen]}

    selected.sort(key=lambda r: (r["dataset"], r["id"]))
    prompt_bytes = ("\n".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) for r in selected) + "\n").encode("utf-8")
    manifest = {
        "schema": "grace_colab_pilot_bundle_v1",
        "purpose": "Exploratory 100-row B1-H2 L4 model-load/offload/logprob pilot; not confirmatory; not for threshold fitting",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_archive": SOURCE_ZIP.name,
        "source_archive_sha256": archive_sha,
        "source_prompt_members": source_records,
        "selection": {"method": "stratified random sample without replacement", "seed": SEED, "per_dataset": PER_DATASET, "total": len(selected)},
        "dataset": "validation",
        "arm": "B1-H2",
        "prompt_variant": "Hiếu original ZIP, dry_run_validation_20261102, seed 42",
        "model_repo": MODEL_REPO,
        "model_file": MODEL_FILE,
        "quantization": "Q4_K_M",
        "model_sha256": MODEL_SHA256,
        "model_repo_revision": "local-sha256:" + MODEL_SHA256,
        "tokenizer": "Qwen/Qwen3-Coder-30B-A3B-Instruct",
        "tokenizer_revision": TOKENIZER_REVISION,
        "backend": "llama-cpp-python 0.3.16",
        "context_tokens": 8192,
        "n_batch": 256,
        "seed": 42,
        "scoring": "unconstrained_first_token_logits_v1",
        "prompts_sha256": sha256(prompt_bytes),
        "count": len(selected),
    }
    BUNDLES.mkdir(parents=True, exist_ok=True)
    NOTEBOOKS.mkdir(parents=True, exist_ok=True)
    bundle_path = BUNDLES / "b1h2_l4_100_sample_bundle.zip"
    with zipfile.ZipFile(bundle_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        z.writestr("bundle_manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
        z.writestr("prompts.jsonl", prompt_bytes)
    nb = build_notebook()
    notebook_path = NOTEBOOKS / "colab_l4_b1h2_100_sample_pilot_20261106.ipynb"
    serialized = json.dumps(nb, indent=2, ensure_ascii=False)
    serialized = serialized.replace("SOURCE_ARCHIVE_SHA256", archive_sha)
    notebook_path.write_text(serialized + "\n", encoding="utf-8")
    print(json.dumps({"source_archive_sha256": archive_sha, "bundle": str(bundle_path), "bundle_sha256": sha256(bundle_path.read_bytes()), "prompts_sha256": manifest["prompts_sha256"], "notebook": str(notebook_path), "samples_by_dataset": {d: source_records[d]["sample_count"] for d in source_records}}, indent=2))


if __name__ == "__main__":
    main()
