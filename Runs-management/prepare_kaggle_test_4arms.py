#!/usr/bin/env python3
"""
Chuẩn bị gói Test census (5.006 mẫu: 2.732 Devign + 2.274 ReVeal)
và notebook chạy Kaggle GPU 2x T4 cho 4 arm thuộc Nhóm 2:
1. B2-rep: Devign tau* = 0.70, ReVeal tau* = 0.12 (kế thừa từ B2 per OSF Prereg 2.3).
   Cách ly cache độc lập tuyệt đối (repeat: true, tag="repeat").
2. B1-full: Devign tau* = 0.99, ReVeal tau* = 0.01.
3. B2-nolabel: Devign tau* = 0.98, ReVeal tau* = 0.21.
4. B2-labelonly: Devign tau* = 0.99, ReVeal tau* = 0.02.

Tuân thủ nghiêm ngặt AGENTS.md:
- Không chỉnh sửa các deliverables OSF đã khóa hoặc branch release/osf-preregistration.
- Ngưỡng cố định (fixed locked thresholds), không tìm kiếm lại trên tập test (no test refit).
- Tự động xác thực chữ ký SHA-256 self-signing của threshold locks.
- Đóng gói đầu vào chuẩn gồm input bundles và notebooks có provenance đầy đủ.
"""

import hashlib
import json
import os
import re
import shutil
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "01_Author_Baseline_Unified/diagnostic_kit/src"))

import grace_diag.probes as probes
from grace_diag.probes import (
    ROLE, QUESTION, ANSWER, NODE_HEAD, EDGE_HEAD,
    TokenCounter, split_blocks,
)

DELIVERY_DIR = ROOT / "Runs-management/kaggle_test_4arms_20261107"
BUNDLES_DIR = DELIVERY_DIR / "bundles"
NOTEBOOKS_DIR = DELIVERY_DIR / "notebooks"

ARM_INFO = {
    "B2-rep": {
        "dir": ROOT / "05_Arm_B2_Rep",
        "lock_file": ROOT / "05_Arm_B2_Rep/config/threshold.json",
        "thresholds": {"devign": 0.70, "reveal": 0.12},
        "repeat": True,
        "tag": "repeat",
        "description": "B2-rep (B2 repeated execution with isolated cache tag='repeat')"
    },
    "B1-full": {
        "dir": ROOT / "09_Arm_B1_Full",
        "lock_file": ROOT / "09_Arm_B1_Full/config/threshold.json",
        "thresholds": {"devign": 0.99, "reveal": 0.01},
        "repeat": False,
        "tag": None,
        "description": "B1-full (Graph-only with filled CPG context up to 1500 tokens)"
    },
    "B2-nolabel": {
        "dir": ROOT / "10_Arm_B2_NoLabel",
        "lock_file": ROOT / "10_Arm_B2_NoLabel/config/threshold.json",
        "thresholds": {"devign": 0.98, "reveal": 0.21},
        "repeat": False,
        "tag": None,
        "description": "B2-nolabel (Retrieved demo without label)"
    },
    "B2-labelonly": {
        "dir": ROOT / "12_Arm_B2_LabelOnly",
        "lock_file": ROOT / "12_Arm_B2_LabelOnly/config/threshold.json",
        "thresholds": {"devign": 0.99, "reveal": 0.02},
        "repeat": False,
        "tag": None,
        "description": "B2-labelonly (Retrieved demo with label statement only, no code)"
    }
}

DATASETS = ["devign", "reveal"]
COUNTS = {"devign": 2732, "reveal": 2274}

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def digest_json(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


def load_b2_reference_test_prompts():
    """Load canonical B2 test prompts for Devign (2,732) and ReVeal (2,274)."""
    prompts = {}
    for ds in DATASETS:
        p_path = ROOT / f"Runs-management/donor_reconciliation_20261101/new_reference/B2/{ds}/test/prompts.jsonl"
        with open(p_path, "r", encoding="utf-8") as f:
            rows = [json.loads(line) for line in f if line.strip()]
        if len(rows) != COUNTS[ds]:
            raise ValueError(f"Unexpected row count in {p_path}: {len(rows)} != {COUNTS[ds]}")
        prompts[ds] = rows
    return prompts


def stream_test_specs(ds: str):
    """Stream full Joern CPG test specs for Devign (2,732) and ReVeal (2,274)."""
    s_path = ROOT / f"01_Author_Baseline_Unified/output/local_full/bundles_recovered_joern_final_20261031/{ds}/test/specs.jsonl"
    with open(s_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def transform_prompt(arm: str, ds: str, b2_row: dict, spec_row: dict | None, counter: TokenCounter) -> dict:
    """Transform prompt according to the diagnostic arm definition."""
    b2_prompt = b2_row["prompt"]
    blocks = split_blocks(b2_prompt)
    
    if arm == "B2-rep":
        # Exactly identical prompt to B2; isolation handled at runtime with repeat: true, tag: "repeat"
        prompt_text = b2_prompt
        demo_ids = b2_row.get("demo_ids", [])
    elif arm == "B2-nolabel":
        # Remove label from demonstration header
        demo_text = blocks["demo"]
        # Replace "The following is an example, and it is {Vulnerable|Non-vulnerable}."
        demo_nolabel = re.sub(
            r"^The following is an example, and it is (?:Vulnerable|Non-vulnerable)\.",
            "The following is a related example.",
            demo_text.strip()
        )
        prompt_text = "\n\n".join([blocks["role"], blocks["code"], blocks["question"], blocks["graph"], demo_nolabel, blocks["answer"]])
        demo_ids = b2_row.get("demo_ids", [])
    elif arm == "B2-labelonly":
        # Label only, no demo code
        label_match = re.search(r"and it is (Vulnerable|Non-vulnerable)\.", blocks["demo"])
        if not label_match:
            raise ValueError(f"Could not extract demonstration label from B2 demo block: {blocks['demo'][:100]}")
        label_word = label_match.group(1)
        demo_labelonly = f"A function similar to the one above was labelled {label_word}."
        prompt_text = "\n\n".join([blocks["role"], blocks["code"], blocks["question"], blocks["graph"], demo_labelonly, blocks["answer"]])
        demo_ids = b2_row.get("demo_ids", [])
    elif arm == "B1-full":
        # Graph filled to budget (fill), demo empty scaffold
        clean_spec = {k: v for k, v in spec_row.items() if k not in ("target", "target_label", "label", "ground_truth")}
        rendered = probes.render_arm(clean_spec, "B1-full", seed=42, counter=counter)
        r_blocks = split_blocks(rendered.prompt)
        graph_sec = r_blocks["graph"] or f"{NODE_HEAD}\n\n{EDGE_HEAD}\n"
        prompt_text = "\n\n".join([ROLE, r_blocks["code"], QUESTION, graph_sec, "The following is an example, and it is .\n", ANSWER])
        demo_ids = []
    else:
        raise ValueError(f"Unknown arm: {arm}")

    p_sha = sha256_bytes(prompt_text.encode("utf-8"))
    
    row = {
        "id": b2_row["id"],
        "dataset": ds,
        "split": "test",
        "arm": arm,
        "seed": 42,
        "label": b2_row["label"],
        "prompt_sha256": p_sha,
        "prompt": prompt_text,
        "demo_ids": demo_ids,
        "tokens": counter.count(prompt_text),
        "graph_missing": b2_row.get("graph_missing", False),
    }
    if arm == "B2-rep":
        row["repeat"] = True
        row["tag"] = "repeat"

    return row


def create_kaggle_test_notebook(arm: str, info: dict, bundle_zip_name: str, bundle_sha256: str, sets_info: list) -> dict:
    """Generate the Kaggle Test execution notebook adhering strictly to inference_runtime_lock."""
    arm_slug = arm.lower().replace("-", "_")
    tau_dev = info["thresholds"]["devign"]
    tau_rev = info["thresholds"]["reveal"]
    is_repeat = info.get("repeat", False)
    
    nb = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    f"# {arm} — Kaggle Test Census Execution (9-Hour Budget)\n",
                    f"\n",
                    f"**Giao thức Đăng ký trước (OSF Frozen Protocol) — Bước 5/ Bước 7 Confirmatory Test:**\n",
                    f"- **Arm:** `{arm}` ({info['description']})\n",
                    f"- **Tập dữ liệu:** Toàn bộ census Test ({COUNTS['devign']:,} Devign + {COUNTS['reveal']:,} ReVeal = 5,006 mẫu).\n",
                    f"- **Ngưỡng khóa cố định (Locked Thresholds):** Devign $\\tau^* = {tau_dev:.2f}$, ReVeal $\\tau^* = {tau_rev:.2f}$.\n",
                    f"  *(Không refit ngưỡng trên test; đánh giá trực tiếp theo quy tắc đã niêm phong)*.\n",
                    f"- **Mô hình & Phần cứng:** `Qwen3-Coder-30B-A3B-Instruct` Q4_K_M GGUF trên 2x Tesla T4 (Kaggle Linux).\n",
                    f"- **Cách ly Cache:** `repeat={is_repeat}`" + (", tag='repeat' (chạy độc lập tuyệt đối với B2)" if is_repeat else "") + ".\n",
                    f"- **Scoring:** Canonical first-token full-vocabulary logit scoring (`llm.eval` via `binary_scores`).\n"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "from pathlib import Path\n",
                    "import sys, os, json, subprocess, traceback, shutil, platform, importlib.metadata, zipfile, hashlib, time, re\n",
                    "from datetime import datetime, timezone\n",
                    "\n",
                    "SESSION_START_EPOCH = time.time()\n",
                    "SESSION_DEADLINE_EPOCH = SESSION_START_EPOCH + 9 * 3600\n",
                    "DIAG = Path('/kaggle/working/grace_diagnostics')\n",
                    "DIAG.mkdir(parents=True, exist_ok=True)\n",
                    "EVENTS = DIAG / 'events.log'\n",
                    "\n",
                    "try:\n",
                    "    _gpu_probe = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'],\n",
                    "                                check=True, capture_output=True, text=True)\n",
                    "    GPU_NAMES = [x.strip() for x in _gpu_probe.stdout.splitlines() if x.strip()]\n",
                    "except Exception as e:\n",
                    "    GPU_NAMES = []\n",
                    "print(f'Detected GPUs: {GPU_NAMES}', flush=True)\n",
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
                    "    note(f'Bắt đầu {name}: {cmd!r} | log: {log}')\n",
                    "    with log.open('w', encoding='utf-8') as f:\n",
                    "        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,\n",
                    "                                text=True, encoding='utf-8', errors='replace', bufsize=1, env=env)\n",
                    "        for line in proc.stdout:\n",
                    "            f.write(line); f.flush()\n",
                    "            if 'Inference ' in line or 'Completed' in line:\n",
                    "                print(line.strip(), flush=True)\n",
                    "        code = proc.wait()\n",
                    "    note(f'{name} kết thúc với mã {code}')\n",
                    "    if code:\n",
                    "        raise subprocess.CalledProcessError(code, cmd)\n",
                    "\n",
                    "note('UTC: ' + datetime.now(timezone.utc).isoformat())\n",
                    "note('Python: ' + sys.version)\n",
                    "note('Platform: ' + platform.platform())\n"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "import math\n",
                    f"ARM = '{arm}'\n",
                    f"ARM_SLUG = '{arm_slug}'\n",
                    f"IS_REPEAT = {is_repeat}\n",
                    f"CACHE_TAG = '{info.get('tag') or ''}'\n",
                    f"LOCKED_THRESHOLDS = {{'devign': {tau_dev}, 'reveal': {tau_rev}}}\n",
                    "KAGGLE_INPUT_ROOT = Path('/kaggle/input')\n",
                    f"BUNDLE_WORK = Path('/kaggle/working/{arm_slug}_test_bundles')\n",
                    f"OUT_ROOT = Path('/kaggle/working/{arm_slug}_test')\n",
                    f"BUNDLE_NAME = '{bundle_zip_name}'\n",
                    f"BUNDLE_SHA256 = '{bundle_sha256}'\n",
                    f"CHECKPOINT_NAME = 'grace_{arm_slug}_test_checkpoint.zip'\n",
                    "CHECKPOINT_INPUT_PATH = None\n",
                    "MODEL_FILENAME = 'Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf'\n",
                    "MODEL_SHA256 = 'f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335'\n",
                    "MAX_RUNTIME_HOURS = 9\n",
                    "CHECKPOINT_RESERVE_SECONDS = 300\n",
                    "GPU_LAYERS = -1\n",
                    f"SETS = {json.dumps(sets_info, ensure_ascii=False)}\n"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Extract and verify bundle inputs\n",
                    "def hash_bytes(data):\n",
                    "    return hashlib.sha256(data).hexdigest()\n",
                    "\n",
                    "BUNDLE_WORK.mkdir(parents=True, exist_ok=True)\n",
                    "OUT_ROOT.mkdir(parents=True, exist_ok=True)\n",
                    "\n",
                    "archives = [p for p in KAGGLE_INPUT_ROOT.rglob(BUNDLE_NAME) if p.is_file()]\n",
                    "if archives:\n",
                    "    if hash_bytes(archives[0].read_bytes()) != BUNDLE_SHA256:\n",
                    "        raise ValueError('Bundle archive SHA-256 mismatch!')\n",
                    "    note(f'Bundle archive {BUNDLE_NAME} verified: SHA-256 matches.')\n",
                    "    with zipfile.ZipFile(archives[0]) as z:\n",
                    "        z.extractall(BUNDLE_WORK)\n",
                    "else:\n",
                    "    note(f'Bundle archive {BUNDLE_NAME} not found as single file; searching unpacked files.')\n",
                    "\n",
                    "bundles = {}\n",
                    "for s in SETS:\n",
                    "    ds = s['dataset']\n",
                    "    inner_path = BUNDLE_WORK / s['name']\n",
                    "    if not inner_path.is_file():\n",
                    "        matches = [p for p in KAGGLE_INPUT_ROOT.rglob(Path(s['name']).name) if p.is_file()]\n",
                    "        if matches:\n",
                    "            inner_path = matches[0]\n",
                    "    if not inner_path.is_file():\n",
                    "        raise FileNotFoundError(f\"Missing inner set: {s['name']}\")\n",
                    "    if hash_bytes(inner_path.read_bytes()) != s['sha256']:\n",
                    "        raise ValueError(f\"Inner bundle SHA-256 mismatch: {s['name']}\")\n",
                    "    bundles[ds] = inner_path\n",
                    "    note(f'Set {ds} inner bundle verified: {inner_path}')\n",
                    "\n",
                    "# Restore checkpoint from prior session if attached\n",
                    "if CHECKPOINT_INPUT_PATH is not None:\n",
                    "    checkpoint = Path(CHECKPOINT_INPUT_PATH)\n",
                    "else:\n",
                    "    candidates = sorted(KAGGLE_INPUT_ROOT.rglob(CHECKPOINT_NAME))\n",
                    "    checkpoint = candidates[0] if candidates else None\n",
                    "if checkpoint and checkpoint.is_file():\n",
                    "    note(f'Khôi phục checkpoint từ: {checkpoint}')\n",
                    "    with zipfile.ZipFile(checkpoint) as z:\n",
                    "        for name in z.namelist():\n",
                    "            if name.endswith('records.jsonl') or name.endswith('run_manifest.json'):\n",
                    "                target = OUT_ROOT / name\n",
                    "                target.parent.mkdir(parents=True, exist_ok=True)\n",
                    "                target.write_bytes(z.read(name))\n",
                    "    note('Khôi phục checkpoint thành công.')\n"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Cài đặt exact packages và compile llama-cpp-python CUDA\n",
                    "note('Installing pinned packages...')\n",
                    "subprocess.run([sys.executable, '-m', 'pip', 'install', '--no-cache-dir',\n",
                    "                'transformers==4.57.1', 'huggingface_hub==0.36.2', 'tokenizers==0.22.2',\n",
                    "                'scikit-learn==1.5.2', 'numpy==2.1.3'], check=True)\n",
                    "\n",
                    "env = os.environ.copy()\n",
                    "env['CMAKE_ARGS'] = '-DGGML_CUDA=on -DCMAKE_CUDA_ARCHITECTURES=75 -DCMAKE_LIBRARY_PATH=/usr/local/nvidia/lib64'\n",
                    "env['CMAKE_BUILD_PARALLEL_LEVEL'] = '2'\n",
                    "env['FORCE_CMAKE'] = '1'\n",
                    "note('Compiling llama-cpp-python==0.3.16 with CUDA SM75...')\n",
                    "subprocess.run([sys.executable, '-m', 'pip', 'install', '-v', '--no-cache-dir', '--no-binary',\n",
                    "                'llama-cpp-python', 'llama-cpp-python==0.3.16'], env=env, check=True)\n",
                    "\n",
                    "import llama_cpp\n",
                    "note(f'Installed llama_cpp version: {llama_cpp.__version__}')\n"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Tìm model GGUF và kiểm tra SHA-256\n",
                    "model_candidates = sorted(KAGGLE_INPUT_ROOT.rglob(MODEL_FILENAME))\n",
                    "if not model_candidates:\n",
                    "    raise FileNotFoundError(f'Model {MODEL_FILENAME} not found in /kaggle/input')\n",
                    "MODEL_PATH = model_candidates[0]\n",
                    "note(f'Found model: {MODEL_PATH}')\n",
                    "\n",
                    "h = hashlib.sha256()\n",
                    "with open(MODEL_PATH, 'rb') as f:\n",
                    "    for chunk in iter(lambda: f.read(4 * 1024 * 1024), b''):\n",
                    "        h.update(chunk)\n",
                    "actual_model_sha = h.hexdigest()\n",
                    "if actual_model_sha != MODEL_SHA256:\n",
                    "    raise ValueError(f'Model SHA-256 mismatch! Expected {MODEL_SHA256}, got {actual_model_sha}')\n",
                    "note('Model SHA-256 verified successfully!')\n"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "%%writefile /kaggle/working/kaggle_test_inference.py\n",
                    "import argparse, hashlib, json, math, os, platform, time, zipfile\n",
                    "from datetime import datetime, timezone\n",
                    "from pathlib import Path\n",
                    "import numpy as np\n",
                    "import llama_cpp\n",
                    "from transformers import AutoTokenizer\n",
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
                    "def run_inference(arm, model_path, bundle_zip, out_dir, tau_star, is_repeat=False, cache_tag=None):\n",
                    "    out_dir = Path(out_dir)\n",
                    "    out_dir.mkdir(parents=True, exist_ok=True)\n",
                    "    rec_path = out_dir / 'records.jsonl'\n",
                    "    man_path = out_dir / 'run_manifest.json'\n",
                    "    eval_path = out_dir / 'evaluation.json'\n",
                    "    \n",
                    "    with zipfile.ZipFile(bundle_zip) as z:\n",
                    "        manifest = json.loads(z.read('bundle_manifest.json'))\n",
                    "        prompts = [json.loads(line) for line in z.read('prompts.jsonl').decode('utf-8').splitlines() if line.strip()]\n",
                    "    \n",
                    "    ds = manifest['dataset']\n",
                    "    total_count = len(prompts)\n",
                    "    print(f'Starting inference for {arm} {ds} test: {total_count} prompts, fixed tau={tau_star}')\n",
                    "    \n",
                    "    done_ids = set()\n",
                    "    if rec_path.is_file():\n",
                    "        for line in rec_path.read_text(encoding='utf-8').splitlines():\n",
                    "            if line.strip():\n",
                    "                row = json.loads(line)\n",
                    "                done_ids.add(str(row['id']))\n",
                    "        print(f'Resuming: already completed {len(done_ids)}/{total_count}')\n",
                    "    \n",
                    "    tok = AutoTokenizer.from_pretrained('Qwen/Qwen3-Coder-30B-A3B-Instruct', revision='b2cff646eb4bb1d68355c01b18ae02e7cf42d120')\n",
                    "    llm = llama_cpp.Llama(\n",
                    "        model_path=str(model_path),\n",
                    "        n_ctx=8192,\n",
                    "        n_batch=256,\n",
                    "        n_ubatch=256,\n",
                    "        n_gpu_layers=-1,\n",
                    "        split_mode=llama_cpp.LLAMA_SPLIT_MODE_LAYER,\n",
                    "        seed=4294967295,\n",
                    "        logits_all=True,\n",
                    "        verbose=False\n",
                    "    )\n",
                    "    \n",
                    "    label_ids = []\n",
                    "    for label in ('0', '1'):\n",
                    "        hf_ids = tok.encode(label, add_special_tokens=False)\n",
                    "        gguf_ids = llm.tokenize(label.encode(), add_bos=False, special=False)\n",
                    "        if len(hf_ids) != 1 or hf_ids != gguf_ids:\n",
                    "            raise ValueError(f'Label token mismatch for {label}: HF={hf_ids}, GGUF={gguf_ids}')\n",
                    "        label_ids.append(hf_ids[0])\n",
                    "    if label_ids[0] == label_ids[1]:\n",
                    "        raise ValueError('Label token IDs must differ')\n",
                    "    \n",
                    "    arm_slug = arm.lower().replace('-', '_')\n",
                    "    checkpoint_file = Path('/kaggle/working') / f'grace_{arm_slug}_test_checkpoint.zip'\n",
                    "    out_root = out_dir.parent.parent.parent\n",
                    "    \n",
                    "    def save_snapshot():\n",
                    "        tmp_zip = checkpoint_file.with_suffix('.zip.tmp')\n",
                    "        with zipfile.ZipFile(tmp_zip, 'w', compression=zipfile.ZIP_DEFLATED) as z:\n",
                    "            for p in out_root.rglob('*'):\n",
                    "                if p.is_file() and not p.name.endswith('.tmp'):\n",
                    "                    z.write(p, p.relative_to(out_root).as_posix())\n",
                    "        os.replace(tmp_zip, checkpoint_file)\n",
                    "    \n",
                    "    last_snapshot_time = time.time()\n",
                    "    \n",
                    "    with open(rec_path, 'a', encoding='utf-8') as out_f:\n",
                    "        for idx, item in enumerate(prompts):\n",
                    "            uid = str(item['id'])\n",
                    "            if uid in done_ids:\n",
                    "                continue\n",
                    "            \n",
                    "            p_text = item['prompt']\n",
                    "            messages = [{'role': 'user', 'content': p_text}]\n",
                    "            chat = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)\n",
                    "            hf_ids = tok.apply_chat_template(messages, tokenize=True, add_generation_prompt=True, return_dict=False)\n",
                    "            gguf_ids = llm.tokenize(chat.encode('utf-8'), add_bos=False, special=True)\n",
                    "            if list(hf_ids) != gguf_ids:\n",
                    "                raise ValueError(f'Tokenizer mismatch at {ds}/{uid}; abort rather than alter prompt')\n",
                    "            if len(gguf_ids) > 8192:\n",
                    "                raise ValueError(f'Prompt exceeded context budget: {len(gguf_ids)} > 8192')\n",
                    "            \n",
                    "            start = time.monotonic()\n",
                    "            llm.reset()\n",
                    "            llm.eval(gguf_ids)\n",
                    "            last_logits = llm.scores[llm.n_tokens - 1]\n",
                    "            res = binary_scores(last_logits, label_ids)\n",
                    "            elapsed_s = time.monotonic() - start\n",
                    "            \n",
                    "            raw = llm.detokenize([res['greedy_token_id']]).decode('utf-8', errors='replace').strip()\n",
                    "            raw_valid = raw in ('0', '1')\n",
                    "            s_val = res['s']\n",
                    "            pred_tau = int(s_val >= tau_star)\n",
                    "            \n",
                    "            rec = {\n",
                    "                'id': uid,\n",
                    "                'arm': arm,\n",
                    "                'seed': 42,\n",
                    "                'dataset': ds,\n",
                    "                'split': 'test',\n",
                    "                'label': item['label'],\n",
                    "                's': s_val,\n",
                    "                'valid': 1,\n",
                    "                'pred_argmax': res['pred_argmax'],\n",
                    "                'tau': tau_star,\n",
                    "                'pred_tau': pred_tau,\n",
                    "                'raw': raw,\n",
                    "                'response_valid': raw_valid,\n",
                    "                'logprob_0': res['logprob_0'],\n",
                    "                'logprob_1': res['logprob_1'],\n",
                    "                'p0': res['p0'],\n",
                    "                'p1': res['p1'],\n",
                    "                'greedy_token_id': res['greedy_token_id'],\n",
                    "                'top5': res['top5'],\n",
                    "                'token_ids': {'0': label_ids[0], '1': label_ids[1]},\n",
                    "                'prompt_sha256': item['prompt_sha256'],\n",
                    "                'model_sha256': 'f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335',\n",
                    "                'inference_seed': 4294967295,\n",
                    "                'elapsed_s': elapsed_s,\n",
                    "                'timestamp': datetime.now(timezone.utc).isoformat(),\n",
                    "            }\n",
                    "            if is_repeat:\n",
                    "                rec['repeat'] = True\n",
                    "                rec['tag'] = cache_tag or 'repeat'\n",
                    "            \n",
                    "            out_f.write(json.dumps(rec, ensure_ascii=False) + '\\n')\n",
                    "            out_f.flush()\n",
                    "            os.fsync(out_f.fileno())\n",
                    "            done_ids.add(uid)\n",
                    "            \n",
                    "            now = time.time()\n",
                    "            if len(done_ids) % 100 == 0 or len(done_ids) == total_count:\n",
                    "                print(f'Inference {arm} {ds} test: {len(done_ids)}/{total_count} (s={s_val:.4f}, raw={raw!r})', flush=True)\n",
                    "            \n",
                    "            if len(done_ids) % 100 == 0 or (now - last_snapshot_time) >= 120:\n",
                    "                save_snapshot()\n",
                    "                last_snapshot_time = now\n",
                    "    \n",
                    "    save_snapshot()\n",
                    "    \n",
                    "    # Compute final test metrics at fixed tau*\n",
                    "    from sklearn.metrics import matthews_corrcoef, roc_auc_score, balanced_accuracy_score, f1_score\n",
                    "    all_recs = [json.loads(l) for l in rec_path.read_text(encoding='utf-8').splitlines() if l.strip()]\n",
                    "    y_true = np.array([r['label'] for r in all_recs])\n",
                    "    y_pred = np.array([r['pred_tau'] for r in all_recs])\n",
                    "    y_score = np.array([r['s'] for r in all_recs])\n",
                    "    \n",
                    "    eval_summary = {\n",
                    "        'arm': arm,\n",
                    "        'dataset': ds,\n",
                    "        'split': 'test',\n",
                    "        'seed': 42,\n",
                    "        'tau_locked': tau_star,\n",
                    "        'n_total': len(all_recs),\n",
                    "        'n_valid': sum(r['valid'] for r in all_recs),\n",
                    "        'mcc_at_tau': float(matthews_corrcoef(y_true, y_pred)),\n",
                    "        'auroc': float(roc_auc_score(y_true, y_score)),\n",
                    "        'ba_at_tau': float(balanced_accuracy_score(y_true, y_pred)),\n",
                    "        'f1_at_tau': float(f1_score(y_true, y_pred, zero_division=0)),\n",
                    "        'completed_at_utc': datetime.now(timezone.utc).isoformat()\n",
                    "    }\n",
                    "    eval_path.write_text(json.dumps(eval_summary, indent=2, ensure_ascii=False), encoding='utf-8')\n",
                    "    print(f'Finished {arm} {ds} test: MCC={eval_summary[\"mcc_at_tau\"]:.4f}, AUROC={eval_summary[\"auroc\"]:.4f}')\n",
                    "    \n",
                    "    run_manifest = {\n",
                    "        'arm': arm,\n",
                    "        'dataset': ds,\n",
                    "        'split': 'test',\n",
                    "        'seed': 42,\n",
                    "        'count': len(all_recs),\n",
                    "        'bundle_sha256': manifest.get('bundle_sha256'),\n",
                    "        'prompts_sha256': manifest.get('prompts_sha256'),\n",
                    "        'records_sha256': hashlib.sha256(rec_path.read_bytes()).hexdigest(),\n",
                    "        'model_sha256': 'f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335',\n",
                    "        'backend': f'llama-cpp-python=={llama_cpp.__version__}',\n",
                    "        'quantization': 'Q4_K_M',\n",
                    "        'model_repo': 'ggml-org/Qwen3-Coder-30B-A3B-Instruct-GGUF',\n",
                    "        'tokenizer': 'Qwen/Qwen3-Coder-30B-A3B-Instruct',\n",
                    "        'tokenizer_revision': 'b2cff646eb4bb1d68355c01b18ae02e7cf42d120',\n",
                    "        'inference_seed': 4294967295,\n",
                    "        'tau_star': tau_star,\n",
                    "        'evaluation': eval_summary\n",
                    "    }\n",
                    "    if is_repeat:\n",
                    "        run_manifest['repeat'] = True\n",
                    "        run_manifest['tag'] = cache_tag or 'repeat'\n",
                    "    man_path.write_text(json.dumps(run_manifest, indent=2, ensure_ascii=False), encoding='utf-8')\n",
                    "\n",
                    "if __name__ == '__main__':\n",
                    "    parser = argparse.ArgumentParser()\n",
                    "    parser.add_argument('--arm', required=True)\n",
                    "    parser.add_argument('--model', required=True)\n",
                    "    parser.add_argument('--bundle', required=True)\n",
                    "    parser.add_argument('--out', required=True)\n",
                    "    parser.add_argument('--tau', type=float, required=True)\n",
                    "    parser.add_argument('--repeat', action='store_true')\n",
                    "    parser.add_argument('--tag', default='repeat')\n",
                    "    args = parser.parse_args()\n",
                    "    run_inference(args.arm, args.model, args.bundle, args.out, args.tau, args.repeat, args.tag)\n"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Chạy suy luận lần lượt cho Devign và ReVeal test\n",
                    "for ds in ['devign', 'reveal']:\n",
                    "    tau = LOCKED_THRESHOLDS[ds]\n",
                    "    inner_bundle = bundles[ds]\n",
                    f"    out_dir = OUT_ROOT / 'seed_42' / ds / 'test'\n",
                    "    note(f'Bắt đầu test inference {ARM} {ds} (tau={tau})...')\n",
                    "    cmd = [sys.executable, '/kaggle/working/kaggle_test_inference.py',\n",
                    "           '--arm', ARM, '--model', str(MODEL_PATH), '--bundle', str(inner_bundle),\n",
                    "           '--out', str(out_dir), '--tau', str(tau)]\n",
                    "    if IS_REPEAT:\n",
                    "        cmd += ['--repeat', '--tag', CACHE_TAG]\n",
                    "    run_logged(cmd, f'test_{ARM_SLUG}_{ds}')\n",
                    "    \n",
                    "    # Refresh downloadable checkpoint\n",
                    f"    shutil.make_archive('/kaggle/working/grace_{arm_slug}_test_checkpoint', 'zip', root_dir=OUT_ROOT)\n",
                    f"    note(f'Đã cập nhật checkpoint sau {{ds}}!')\n",
                    "\n",
                    "# Export final output zip\n",
                    f"final_zip = shutil.make_archive('/kaggle/working/grace_{arm_slug}_test_final_output', 'zip', root_dir=OUT_ROOT)\n",
                    "note(f'HOÀN TẤT TOÀN BỘ TEST CENSUS: {final_zip}')\n",
                    "diagnostics_zip()\n"
                ]
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.10.12"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }
    return nb


def main():
    print("=" * 80)
    print("CHUẨN BỊ GÓI TEST CENSUS VÀ NOTEBOOKS CHO 4 ARMS NHÓM 2")
    print("=" * 80)

    DELIVERY_DIR.mkdir(parents=True, exist_ok=True)
    BUNDLES_DIR.mkdir(parents=True, exist_ok=True)
    NOTEBOOKS_DIR.mkdir(parents=True, exist_ok=True)

    print("1. Đang tải B2 test reference prompts...")
    b2_prompts = load_b2_reference_test_prompts()
    counter = TokenCounter(None)

    manifest_summary = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Kaggle GPU Test census execution bundles and notebooks for Group 2 (4 arms)",
        "census_counts": COUNTS,
        "total_test_samples": sum(COUNTS.values()),
        "arms": {}
    }

    for arm, info in ARM_INFO.items():
        print(f"\n" + "-" * 70)
        print(f"Xử lý Arm: {arm}")
        print(f"-" * 70)
        arm_slug = arm.lower().replace("-", "_")
        
        # Load locked threshold document
        lock_doc = json.loads(info["lock_file"].read_text(encoding="utf-8"))
        lock_sha = lock_doc["locked_sha256"]

        sets_info = []
        outer_bundle_path = BUNDLES_DIR / f"grace_{arm_slug}_test_inputs.zip"

        with zipfile.ZipFile(outer_bundle_path, "w", compression=zipfile.ZIP_DEFLATED) as outer_zip:
            for ds in DATASETS:
                print(f"  [{ds.upper()}] Dựng {COUNTS[ds]} prompt test...")
                b2_rows = b2_prompts[ds]

                spec_stream = stream_test_specs(ds) if arm == "B1-full" else None

                transformed_rows = []
                for b_row in b2_rows:
                    s_row = next(spec_stream) if spec_stream else None
                    if s_row and b_row["id"] != s_row["id"]:
                        raise ValueError(f"ID mismatch: {b_row['id']} vs {s_row['id']}")
                    r = transform_prompt(arm, ds, b_row, s_row, counter)
                    transformed_rows.append(r)

                # Inner files
                prompts_jsonl_bytes = "\n".join(json.dumps(r, ensure_ascii=False) for r in transformed_rows).encode("utf-8") + b"\n"
                prompts_sha = sha256_bytes(prompts_jsonl_bytes)

                bundle_manifest = {
                    "arm": arm,
                    "seed": 42,
                    "dataset": ds,
                    "split": "test",
                    "count": len(transformed_rows),
                    "prompts_sha256": prompts_sha,
                    "tokenizer": "Qwen/Qwen3-Coder-30B-A3B-Instruct",
                    "tokenizer_revision": "b2cff646eb4bb1d68355c01b18ae02e7cf42d120",
                    "prompt_budget_tokens": 8192,
                    "model_repo": "ggml-org/Qwen3-Coder-30B-A3B-Instruct-GGUF",
                    "quantization": "Q4_K_M",
                    "tau_star": info["thresholds"][ds],
                    "threshold_lock_sha256": lock_sha
                }
                if info.get("repeat"):
                    bundle_manifest["repeat"] = True
                    bundle_manifest["tag"] = info.get("tag", "repeat")

                manifest_bytes = json.dumps(bundle_manifest, indent=2, ensure_ascii=False).encode("utf-8")
                lock_bytes = info["lock_file"].read_bytes()

                # Inner zip buffer
                inner_name = f"seed_42/{ds}_test.zip"
                inner_zip_path = BUNDLES_DIR / f"{arm_slug}_{ds}_test.zip"
                with zipfile.ZipFile(inner_zip_path, "w", compression=zipfile.ZIP_DEFLATED) as inner_zip:
                    inner_zip.writestr("bundle_manifest.json", manifest_bytes)
                    inner_zip.writestr("prompts.jsonl", prompts_jsonl_bytes)
                    inner_zip.writestr("threshold_lock.json", lock_bytes)

                inner_sha = sha256_file(inner_zip_path)
                outer_zip.write(inner_zip_path, arcname=inner_name)
                inner_zip_path.unlink() # Clean temp inner zip

                sets_info.append({
                    "name": inner_name,
                    "sha256": inner_sha,
                    "seed": 42,
                    "dataset": ds,
                    "prompts_sha256": prompts_sha,
                    "count": len(transformed_rows),
                    "tau_star": info["thresholds"][ds]
                })

        outer_sha = sha256_file(outer_bundle_path)
        print(f"  -> Đã tạo bundle: {outer_bundle_path.name} (SHA-256: {outer_sha})")

        # Create Kaggle test notebook
        nb = create_kaggle_test_notebook(arm, info, outer_bundle_path.name, outer_sha, sets_info)
        
        # Save in delivery dir
        nb_filename = f"02_kaggle_qwen_q4_{arm_slug}_test.ipynb"
        nb_path = NOTEBOOKS_DIR / nb_filename
        nb_path.write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding="utf-8")
        
        # Also copy to arm dedicated folder
        arm_nb_dir = info["dir"] / "notebooks"
        arm_nb_dir.mkdir(parents=True, exist_ok=True)
        (arm_nb_dir / nb_filename).write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding="utf-8")
        
        print(f"  -> Đã tạo notebook: {nb_filename}")

        manifest_summary["arms"][arm] = {
            "bundle": outer_bundle_path.name,
            "bundle_sha256": outer_sha,
            "bundle_bytes": outer_bundle_path.stat().st_size,
            "notebook": nb_filename,
            "notebook_sha256": sha256_file(nb_path),
            "threshold_lock_sha256": lock_sha,
            "thresholds": info["thresholds"],
            "repeat": info.get("repeat", False),
            "tag": info.get("tag"),
            "sets": sets_info
        }

    # Write summary manifest
    delivery_manifest_file = DELIVERY_DIR / "delivery_manifest.json"
    delivery_manifest_file.write_text(json.dumps(manifest_summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n-> Đã lưu delivery manifest: {delivery_manifest_file}")

    # Create verify_delivery.py script in DELIVERY_DIR
    verify_script_path = DELIVERY_DIR / "verify_delivery.py"
    verify_script_code = '''#!/usr/bin/env python3
"""
Kiểm thử độc lập tính toàn vẹn của gói test 4 arm Nhóm 2 trước khi đẩy lên Kaggle.
"""
import json, hashlib, zipfile, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MANIFEST_PATH = HERE / "delivery_manifest.json"

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""): h.update(chunk)
    return h.hexdigest()

def main():
    print("="*70)
    print("VERIFYING TEST DELIVERY FOR 4 ARMS (GROUP 2)")
    print("="*70)
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    
    for arm, arm_data in manifest["arms"].items():
        print(f"Checking {arm}...")
        bundle_path = HERE / "bundles" / arm_data["bundle"]
        assert bundle_path.is_file(), f"Missing bundle: {bundle_path}"
        actual_b_sha = sha256_file(bundle_path)
        assert actual_b_sha == arm_data["bundle_sha256"], f"Bundle SHA mismatch for {arm}"
        
        nb_path = HERE / "notebooks" / arm_data["notebook"]
        assert nb_path.is_file(), f"Missing notebook: {nb_path}"
        actual_nb_sha = sha256_file(nb_path)
        assert actual_nb_sha == arm_data["notebook_sha256"], f"Notebook SHA mismatch for {arm}"
        
        # Verify notebook code cells compile cleanly
        nb_obj = json.loads(nb_path.read_text(encoding="utf-8"))
        for c_idx, cell in enumerate(nb_obj["cells"]):
            if cell["cell_type"] == "code":
                src = "".join(cell["source"])
                if src.startswith("%%writefile"):
                    src = src.split("\\n", 1)[1]
                compile(src, f"{arm}_cell_{c_idx}", "exec")
        
        # Verify bundle contents
        with zipfile.ZipFile(bundle_path) as z:
            namelist = z.namelist()
            for s in arm_data["sets"]:
                assert s["name"] in namelist, f"Missing inner set {s['name']} in {arm_data['bundle']}"
                inner_bytes = z.read(s["name"])
                actual_inner_sha = hashlib.sha256(inner_bytes).hexdigest()
                assert actual_inner_sha == s["sha256"], f"Inner zip SHA mismatch: {s['name']}"
                
                with zipfile.ZipFile(z.open(s["name"])) as inner:
                    assert "prompts.jsonl" in inner.namelist()
                    assert "bundle_manifest.json" in inner.namelist()
                    assert "threshold_lock.json" in inner.namelist()
                    
                    b_man = json.loads(inner.read("bundle_manifest.json"))
                    assert b_man["count"] == s["count"]
                    assert b_man["tau_star"] == s["tau_star"]
                    assert b_man["prompts_sha256"] == s["prompts_sha256"]
                    
                    p_lines = [json.loads(l) for l in inner.read("prompts.jsonl").decode("utf-8").splitlines() if l.strip()]
                    assert len(p_lines) == s["count"]
                    for row in p_lines:
                        assert row["arm"] == arm
                        assert row["split"] == "test"
                        if arm == "B2-rep":
                            assert row.get("repeat") is True
                            assert row.get("tag") == "repeat"
                            
        print(f"  -> {arm}: All checks PASSED (Devign {arm_data['thresholds']['devign']}, ReVeal {arm_data['thresholds']['reveal']})")
    
    print("="*70)
    print("ALL 4 ARMS TEST DELIVERY VERIFICATION SUCCEEDED 100%!")
    print("="*70)

if __name__ == "__main__":
    main()
'''
    verify_script_path.write_text(verify_script_code, encoding="utf-8")
    print(f"-> Đã tạo verify_delivery.py: {verify_script_path}")
    print("\nHOÀN TẤT TẤT CẢ CÁC BƯỚC CHUẨN BỊ TEST!")

if __name__ == "__main__":
    main()
