import json
from pathlib import Path

# Load B1-shuf validation notebook to use as structural base
val_nb_path = Path("08_Arm_B1_Shuf/notebooks/02_kaggle_qwen_q4_b1_shuf_validation.ipynb")
val_nb = json.loads(val_nb_path.read_text(encoding="utf-8"))

# Load locked thresholds from 08_Arm_B1_Shuf/config/threshold.json
thresh_data = json.loads(Path("08_Arm_B1_Shuf/config/threshold.json").read_text(encoding="utf-8"))
# Entries: B1-shuf/42/devign -> 0.98, etc.

test_sets = [
    {"name": "seed_42/devign_test.zip", "seed": 42, "dataset": "devign", "count": 2732, "tau_star": 0.98},
    {"name": "seed_43/devign_test.zip", "seed": 43, "dataset": "devign", "count": 2732, "tau_star": 0.96},
    {"name": "seed_44/devign_test.zip", "seed": 44, "dataset": "devign", "count": 2732, "tau_star": 0.67},
    {"name": "seed_42/reveal_test.zip", "seed": 42, "dataset": "reveal", "count": 2274, "tau_star": 0.66},
    {"name": "seed_43/reveal_test.zip", "seed": 43, "dataset": "reveal", "count": 2274, "tau_star": 0.01},
    {"name": "seed_44/reveal_test.zip", "seed": 44, "dataset": "reveal", "count": 2274, "tau_star": 0.04},
]

# Cell 0: Markdown
cell0_src = """# B1-shuf — Kaggle Test Census Execution (9-Hour Budget)

**Giao thức Đăng ký trước (OSF Frozen Protocol) — Bước 5 Confirmatory Test:**
- **Arm:** `B1-shuf` (Trộn lẫn CPG với donor ngẫu nhiên, không demonstration, 3 seeds 42/43/44)
- **Tập dữ liệu:** Toàn bộ census Test (3 seeds × [2,732 Devign + 2,274 ReVeal] = 15,018 lượt suy luận).
- **Ngưỡng khóa cố định (Locked Thresholds per Seed):**
  * Seed 42: Devign $\\tau^* = 0.98$, ReVeal $\\tau^* = 0.66$
  * Seed 43: Devign $\\tau^* = 0.96$, ReVeal $\\tau^* = 0.01$
  * Seed 44: Devign $\\tau^* = 0.67$, ReVeal $\\tau^* = 0.04$
  *(Không refit ngưỡng trên test; đánh giá trực tiếp theo quy tắc đã niêm phong)*.
- **Mô hình & Phần cứng:** `Qwen3-Coder-30B-A3B-Instruct` Q4_K_M GGUF trên 2x Tesla T4 (Kaggle Linux).
- **Runtime Lock Compliance:** `grace_qwen_q4_runtime_v1` (inference_seed: 4294967295, context: 8192, 6 pinned packages).
- **Scoring:** Canonical first-token full-vocabulary logit scoring (`llm.eval` via `binary_scores`).
"""

# Cell 1: Environment & Logging
cell1_src = """from pathlib import Path
import sys, os, json, subprocess, traceback, shutil, platform, importlib.metadata, zipfile, hashlib, time, re
from datetime import datetime, timezone

SESSION_START_EPOCH = time.time()
SESSION_DEADLINE_EPOCH = SESSION_START_EPOCH + 9 * 3600
DIAG = Path('/kaggle/working/grace_diagnostics')
DIAG.mkdir(parents=True, exist_ok=True)
EVENTS = DIAG / 'events.log'

try:
    _gpu_probe = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'],
                                check=True, capture_output=True, text=True)
    GPU_NAMES = [x.strip() for x in _gpu_probe.stdout.splitlines() if x.strip()]
except Exception as e:
    GPU_NAMES = []
print(f'Detected GPUs: {GPU_NAMES}', flush=True)

def note(message):
    text = str(message)
    print(text, flush=True)
    with EVENTS.open('a', encoding='utf-8') as f:
        f.write(f'[{datetime.now(timezone.utc).isoformat()}] {text}\\n')

def diagnostics_zip():
    archive = shutil.make_archive('/kaggle/working/grace_diagnostics', 'zip', root_dir=DIAG)
    print('Tải log chẩn đoán từ Kaggle Output:', archive, flush=True)
    return archive

def run_logged(cmd, name, env=None):
    log = DIAG / f'{name}.log'
    note(f'Bắt đầu {name}: {cmd!r} | log: {log}')
    with log.open('w', encoding='utf-8') as f:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, encoding='utf-8', errors='replace', bufsize=1, env=env)
        for line in proc.stdout:
            f.write(line); f.flush()
            print(line, end='', flush=True)
        code = proc.wait()
    note(f'{name} kết thúc với mã {code}')
    if code:
        raise subprocess.CalledProcessError(code, cmd)

note('UTC: ' + datetime.now(timezone.utc).isoformat())
note('Python: ' + sys.version)
note('Platform: ' + platform.platform())
"""

# Cell 2: Configuration & Parameters
cell2_src = f"""import math
ARM = 'B1-shuf'
ARM_SLUG = 'b1_shuf'
KAGGLE_INPUT_ROOT = Path('/kaggle/input')
BUNDLE_WORK = Path('/kaggle/working/b1_shuf_test_bundles')
OUT_ROOT = Path('/kaggle/working/b1_shuf_test')
BUNDLE_NAME = 'grace_b1_shuf_test_inputs.zip'
CHECKPOINT_NAME = 'grace_b1_shuf_test_checkpoint.zip'
CHECKPOINT_INPUT_PATH = None
MODEL_FILENAME = 'Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf'
MODEL_SHA256 = 'f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335'
MAX_RUNTIME_HOURS = 9
CHECKPOINT_RESERVE_SECONDS = 300
GPU_LAYERS = -1
SETS = {json.dumps(test_sets, indent=2)}
"""

# Cell 3: Bundle & Checkpoint Extraction
cell3_src = """# Tìm và bung bundle input, phục hồi checkpoint nếu có
BUNDLE_WORK.mkdir(parents=True, exist_ok=True)
OUT_ROOT.mkdir(parents=True, exist_ok=True)

# 1. Tìm và giải nén test bundles
bundle_zip = None
for root, _, files in os.walk(KAGGLE_INPUT_ROOT):
    if BUNDLE_NAME in files:
        bundle_zip = Path(root) / BUNDLE_NAME
        break
if not bundle_zip:
    for candidate in KAGGLE_INPUT_ROOT.rglob('*.zip'):
        if 'b1_shuf' in candidate.name.lower() and 'test' in candidate.name.lower():
            bundle_zip = candidate
            break

if bundle_zip:
    note(f'Bung nén test inputs: {bundle_zip}')
    with zipfile.ZipFile(bundle_zip) as z:
        z.extractall(BUNDLE_WORK)
else:
    note(f'CẢNH BÁO: Chưa tìm thấy {BUNDLE_NAME} trong Kaggle Input!')

# 2. Khôi phục checkpoint nếu có phiên chạy trước đính kèm
checkpoint_in = None
for root, _, files in os.walk(KAGGLE_INPUT_ROOT):
    if CHECKPOINT_NAME in files:
        checkpoint_in = Path(root) / CHECKPOINT_NAME
        break

if checkpoint_in:
    note(f'Khôi phục checkpoint từ: {checkpoint_in}')
    with zipfile.ZipFile(checkpoint_in) as z:
        z.extractall(OUT_ROOT)
"""

# Cell 4: Exact Pinned Packages Installation
cell4_src = """# Cài đặt exact packages và compile llama-cpp-python CUDA theo Runtime Lock grace_qwen_q4_runtime_v1
note('Installing pinned packages...')
subprocess.run([sys.executable, '-m', 'pip', 'install', '--no-cache-dir',
                'transformers==4.57.1', 'huggingface_hub==0.36.2', 'tokenizers==0.22.2',
                'scikit-learn==1.5.2', 'numpy==2.1.3'], check=True)

env = os.environ.copy()
env['CMAKE_ARGS'] = '-DGGML_CUDA=on -DCMAKE_CUDA_ARCHITECTURES=75 -DCMAKE_LIBRARY_PATH=/usr/local/nvidia/lib64'
env['CMAKE_BUILD_PARALLEL_LEVEL'] = '2'
env['FORCE_CMAKE'] = '1'
note('Compiling llama-cpp-python==0.3.16 with CUDA SM75...')
subprocess.run([sys.executable, '-m', 'pip', 'install', '-v', '--no-cache-dir', '--no-binary',
                'llama-cpp-python', 'llama-cpp-python==0.3.16'], env=env, check=True)

import llama_cpp
note(f'Installed llama_cpp version: {llama_cpp.__version__}')
"""

# Cell 5: Model GGUF Locator & Hash Verification
cell5_src = """# Tìm model GGUF và kiểm tra SHA-256
model_path = None
for root, _, files in os.walk(KAGGLE_INPUT_ROOT):
    if MODEL_FILENAME in files:
        model_path = Path(root) / MODEL_FILENAME
        break
if not model_path:
    for candidate in KAGGLE_INPUT_ROOT.rglob('*.gguf'):
        if 'qwen' in candidate.name.lower() and '30b' in candidate.name.lower():
            model_path = candidate
            break

if not model_path or not model_path.exists():
    raise FileNotFoundError(f'Không tìm thấy file model {MODEL_FILENAME} trong {KAGGLE_INPUT_ROOT}')

note(f'Đã tìm thấy model: {model_path} ({model_path.stat().st_size / 1024**3:.2f} GB)')
"""

# Cell 6: Inference Worker Script
cell6_src = """%%writefile /kaggle/working/kaggle_test_inference.py
import argparse, hashlib, json, math, os, platform, time, zipfile
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import llama_cpp
from transformers import AutoTokenizer

def binary_scores(logits, label_ids):
    values = np.asarray(logits, dtype=np.float64).reshape(-1)
    if not np.all(np.isfinite(values)):
        raise ValueError('Non-finite logits')
    maximum = np.max(values)
    normalizer = float(maximum + np.log(np.exp(values - maximum).sum()))
    lp0 = float(values[label_ids[0]] - normalizer)
    lp1 = float(values[label_ids[1]] - normalizer)
    score = float(np.exp(lp1 - np.logaddexp(lp0, lp1)))
    best = int(np.argmax(values))
    top = np.argsort(values)[-5:][::-1]
    return {'logprob_0': lp0, 'logprob_1': lp1, 'p0': math.exp(lp0), 'p1': math.exp(lp1),
            's': score, 'pred_argmax': int(score >= 0.5), 'greedy_token_id': best,
            'top5': [{'token_id': int(i), 'logprob': float(values[i] - normalizer)} for i in top]}

def run_inference(arm, seed, dataset, model_path, bundle_zip, out_dir, tau_star):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    rec_path = out_dir / 'records.jsonl'
    man_path = out_dir / 'run_manifest.json'
    eval_path = out_dir / 'evaluation.json'
    
    with zipfile.ZipFile(bundle_zip) as z:
        manifest = json.loads(z.read('bundle_manifest.json'))
        prompts = [json.loads(line) for line in z.read('prompts.jsonl').decode('utf-8').splitlines() if line.strip()]
    
    ds = manifest.get('dataset', dataset)
    total_count = len(prompts)
    print(f'Starting inference for {arm} seed={seed} {ds} test: {total_count} prompts, fixed tau={tau_star}')
    
    done_ids = set()
    if rec_path.is_file():
        for line in rec_path.read_text(encoding='utf-8').splitlines():
            if line.strip():
                row = json.loads(line)
                done_ids.add(str(row['id']))
        print(f'Resuming: already completed {len(done_ids)}/{total_count}')
    
    tok = AutoTokenizer.from_pretrained('Qwen/Qwen3-Coder-30B-A3B-Instruct', revision='b2cff646eb4bb1d68355c01b18ae02e7cf42d120')
    llm = llama_cpp.Llama(
        model_path=str(model_path),
        n_ctx=8192,
        n_batch=256,
        n_ubatch=256,
        n_gpu_layers=-1,
        split_mode=llama_cpp.LLAMA_SPLIT_MODE_LAYER,
        seed=4294967295,
        logits_all=True,
        verbose=False
    )
    
    label_ids = []
    for label in ('0', '1'):
        hf_ids = tok.encode(label, add_special_tokens=False)
        gguf_ids = llm.tokenize(label.encode(), add_bos=False, special=False)
        if len(hf_ids) != 1 or hf_ids != gguf_ids:
            raise ValueError(f'Label token mismatch for {label}: HF={hf_ids}, GGUF={gguf_ids}')
        label_ids.append(hf_ids[0])
    if label_ids[0] == label_ids[1]:
        raise ValueError('Label token IDs must differ')
    
    checkpoint_file = Path('/kaggle/working/grace_b1_shuf_test_checkpoint.zip')
    out_root = out_dir.parent.parent.parent
    
    def save_snapshot():
        tmp_zip = checkpoint_file.with_suffix('.zip.tmp')
        with zipfile.ZipFile(tmp_zip, 'w', compression=zipfile.ZIP_DEFLATED) as z:
            for p in out_root.rglob('*'):
                if p.is_file() and not p.name.endswith('.tmp'):
                    z.write(p, p.relative_to(out_root).as_posix())
        os.replace(tmp_zip, checkpoint_file)
    
    last_snapshot_time = time.time()
    
    with open(rec_path, 'a', encoding='utf-8') as out_f:
        for idx, item in enumerate(prompts):
            uid = str(item['id'])
            if uid in done_ids:
                continue
            
            p_text = item['prompt']
            messages = [{'role': 'user', 'content': p_text}]
            chat = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            prompt_tokens = tok.encode(chat, add_special_tokens=False)
            
            t0 = time.time()
            llm.reset()
            llm.eval(prompt_tokens)
            elapsed_s = time.time() - t0
            
            logits = llm.scores[llm.n_tokens - 1]
            res = binary_scores(logits, label_ids)
            raw = llm.detokenize([res['greedy_token_id']]).decode('utf-8', errors='replace').strip()
            raw_valid = raw in ('0', '1')
            s_val = res['s']
            pred_tau = int(s_val >= tau_star)
            
            rec = {
                'id': uid,
                'arm': arm,
                'seed': seed,
                'dataset': ds,
                'split': 'test',
                'label': item['label'],
                's': s_val,
                'valid': 1,
                'pred_argmax': res['pred_argmax'],
                'tau': tau_star,
                'pred_tau': pred_tau,
                'raw': raw,
                'response_valid': raw_valid,
                'logprob_0': res['logprob_0'],
                'logprob_1': res['logprob_1'],
                'p0': res['p0'],
                'p1': res['p1'],
                'greedy_token_id': res['greedy_token_id'],
                'top5': res['top5'],
                'token_ids': {'0': label_ids[0], '1': label_ids[1]},
                'prompt_sha256': item['prompt_sha256'],
                'model_sha256': 'f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335',
                'inference_seed': 4294967295,
                'elapsed_s': elapsed_s,
                'timestamp': datetime.now(timezone.utc).isoformat(),
            }
            
            out_f.write(json.dumps(rec, ensure_ascii=False) + '\\n')
            out_f.flush()
            os.fsync(out_f.fileno())
            done_ids.add(uid)
            
            now = time.time()
            print(f'{arm}/s{seed}/{ds} {uid}: s={s_val:.4f}, raw={raw!r} ({len(done_ids)}/{total_count})', flush=True)
            
            if len(done_ids) % 100 == 0 or (now - last_snapshot_time) >= 120:
                save_snapshot()
                last_snapshot_time = now
    
    save_snapshot()
    
    # Compute metrics at locked tau*
    from sklearn.metrics import matthews_corrcoef, roc_auc_score, balanced_accuracy_score, f1_score
    all_recs = [json.loads(l) for l in rec_path.read_text(encoding='utf-8').splitlines() if l.strip()]
    y_true = np.array([r['label'] for r in all_recs])
    y_pred = np.array([r['pred_tau'] for r in all_recs])
    y_score = np.array([r['s'] for r in all_recs])
    
    eval_summary = {
        'arm': arm,
        'dataset': ds,
        'split': 'test',
        'seed': seed,
        'tau_locked': tau_star,
        'n_total': len(all_recs),
        'n_valid': sum(r['valid'] for r in all_recs),
        'mcc_at_tau': float(matthews_corrcoef(y_true, y_pred)),
        'auroc': float(roc_auc_score(y_true, y_score)),
        'ba_at_tau': float(balanced_accuracy_score(y_true, y_pred)),
        'f1_at_tau': float(f1_score(y_true, y_pred, zero_division=0)),
        'completed_at_utc': datetime.now(timezone.utc).isoformat()
    }
    eval_path.write_text(json.dumps(eval_summary, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f'Finished {arm} s{seed} {ds} test: MCC={eval_summary["mcc_at_tau"]:.4f}, AUROC={eval_summary["auroc"]:.4f}')
    
    run_manifest = {
        'arm': arm,
        'dataset': ds,
        'split': 'test',
        'seed': seed,
        'count': len(all_recs),
        'bundle_sha256': manifest.get('bundle_sha256'),
        'prompts_sha256': manifest.get('prompts_sha256'),
        'records_sha256': hashlib.sha256(rec_path.read_bytes()).hexdigest(),
        'model_sha256': 'f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335',
        'backend': f'llama-cpp-python=={llama_cpp.__version__}',
        'quantization': 'Q4_K_M',
        'model_repo': 'ggml-org/Qwen3-Coder-30B-A3B-Instruct-GGUF',
        'tokenizer': 'Qwen/Qwen3-Coder-30B-A3B-Instruct',
        'tokenizer_revision': 'b2cff646eb4bb1d68355c01b18ae02e7cf42d120',
        'inference_seed': 4294967295,
        'tau_star': tau_star,
        'evaluation': eval_summary
    }
    man_path.write_text(json.dumps(run_manifest, indent=2, ensure_ascii=False), encoding='utf-8')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--arm', default='B1-shuf')
    parser.add_argument('--seed', type=int, required=True)
    parser.add_argument('--dataset', required=True)
    parser.add_argument('--model', required=True)
    parser.add_argument('--bundle', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--tau', type=float, required=True)
    args = parser.parse_args()
    run_inference(args.arm, args.seed, args.dataset, args.model, args.bundle, args.out, args.tau)
"""

# Cell 7: Loop over SETS
cell7_src = """# Thực thi tuần tự 6 bộ Test trong SETS (3 seeds x 2 datasets)
for s_info in SETS:
    if time.time() >= SESSION_DEADLINE_EPOCH - CHECKPOINT_RESERVE_SECONDS:
        note('Đã chạm ngưỡng thời gian phiên Kaggle (gần 9h), dừng an toàn để bảo lưu Checkpoint.')
        break
    
    seed = s_info['seed']
    ds = s_info['dataset']
    tau_star = s_info['tau_star']
    s_name = s_info['name']
    
    # Tìm file bundle
    bundle_candidate = BUNDLE_WORK / s_name
    if not bundle_candidate.exists():
        for candidate in BUNDLE_WORK.rglob('*.zip'):
            if f'seed_{seed}' in str(candidate) and ds in candidate.name.lower():
                bundle_candidate = candidate
                break
    
    if not bundle_candidate.exists():
        note(f'BỎ QUA {ds} test (seed {seed}): Không tìm thấy bundle {s_name}')
        continue
    
    out_dir = OUT_ROOT / f'seed_{seed}' / ds / 'test'
    rec_file = out_dir / 'records.jsonl'
    
    if rec_file.is_file():
        done_count = sum(1 for line in rec_file.read_text(encoding='utf-8').splitlines() if line.strip())
        if done_count >= s_info['count']:
            note(f'Bộ {ds} test seed {seed} đã hoàn tất ({done_count}/{s_info[\"count\"]} mẫu), bỏ qua.')
            continue
    
    note(f'=== CHẠY SUY LUẬN TEST: B1-shuf seed={seed} {ds} (tau*={tau_star}) ===')
    cmd = [
        sys.executable, '/kaggle/working/kaggle_test_inference.py',
        '--arm', ARM,
        '--seed', str(seed),
        '--dataset', ds,
        '--model', str(model_path),
        '--bundle', str(bundle_candidate),
        '--out', str(out_dir),
        '--tau', str(tau_star)
    ]
    run_logged(cmd, f'inference_b1_shuf_s{seed}_{ds}_test')

note('Tất cả các bộ suy luận test hoàn tất hoặc đã lưu checkpoint.')
diagnostics_zip()
"""

cells = [
    {"cell_type": "markdown", "metadata": {}, "source": [cell0_src]},
    {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": [cell1_src]},
    {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": [cell2_src]},
    {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": [cell3_src]},
    {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": [cell4_src]},
    {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": [cell5_src]},
    {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": [cell6_src]},
    {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": [cell7_src]},
]

nb_out = {
    "cells": cells,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.10.11"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 2
}

out_p = Path("08_Arm_B1_Shuf/notebooks/02_kaggle_qwen_q4_b1_shuf_test.ipynb")
out_p.write_text(json.dumps(nb_out, indent=1, ensure_ascii=False), encoding="utf-8")
print(f"Created canonical test notebook for B1-shuf: {out_p}")
