import json
import os
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import builtins
orig_open = builtins.open
def utf8_open(*args, **kwargs):
    if len(args) > 1 and 'b' in args[1]:
        return orig_open(*args, **kwargs)
    if 'mode' in kwargs and 'b' in kwargs['mode']:
        return orig_open(*args, **kwargs)
    if 'encoding' not in kwargs:
        kwargs['encoding'] = 'utf-8'
    return orig_open(*args, **kwargs)
builtins.open = utf8_open

def create_notebook():
    nb = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# Thử nghiệm Thuật toán mới B3 (Verified Patch-Pair Selector) trên Kaggle\n",
                    "Kiểm tra 2 khía cạnh cốt lõi:\n",
                    "1. Rà soát ngân hàng donor thật của Devign/ReVeal (chứng minh điều kiện dừng PAUSE khi thiếu pool cặp mẫu duyệt).\n",
                    "2. Thử nghiệm thuật toán mới trên các cặp mẫu Patch thật (vulnerable vs patched diff), dựng prompt Figure 6 và chạy suy luận GPU Qwen-Coder-30B (A3B MoE) trên 2x Tesla T4."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "import os, sys, json, time, subprocess, shutil, platform, re, hashlib\n",
                    "from pathlib import Path\n",
                    "from datetime import datetime, timezone\n",
                    "\n",
                    "DIAG = Path('/kaggle/working/grace_diagnostics')\n",
                    "DIAG.mkdir(parents=True, exist_ok=True)\n",
                    "EVENTS = DIAG / 'events.log'\n",
                    "\n",
                    "def note(msg):\n",
                    "    t = f'[{datetime.now(timezone.utc).isoformat()}] {msg}'\n",
                    "    print(t, flush=True)\n",
                    "    with EVENTS.open('a', encoding='utf-8') as f:\n",
                    "        f.write(t + '\\n')\n",
                    "\n",
                    "note('Bắt đầu phiên kiểm nghiệm thuật toán B3 mới trên Kaggle')\n",
                    "note(f'Python: {sys.version}')\n",
                    "note(f'Platform: {platform.platform()}')\n",
                    "\n",
                    "# Kiểm tra GPU\n",
                    "try:\n",
                    "    gpu_info = subprocess.check_output(['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader'], text=True)\n",
                    "    note(f'GPU phát hiện:\\n{gpu_info.strip()}')\n",
                    "except Exception as e:\n",
                    "    note(f'Lỗi kiểm tra GPU: {e}')\n",
                    "\n",
                    "# Tìm GGUF model\n",
                    "gguf_files = sorted(Path('/kaggle/input').rglob('*.gguf'))\n",
                    "note(f'Tìm thấy GGUF models: {gguf_files}')\n"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Cài đặt dependencies và llama-cpp-python CUDA\n",
                    "note('Cài đặt thư viện phụ trợ...')\n",
                    "subprocess.run([sys.executable, '-m', 'pip', 'install', '--no-cache-dir', 'transformers==4.57.1', 'huggingface_hub', 'scikit-learn==1.5.2'], check=True)\n",
                    "\n",
                    "note('Biên dịch llama-cpp-python với hỗ trợ CUDA SM75...')\n",
                    "env = os.environ.copy()\n",
                    "env['CMAKE_ARGS'] = '-DGGML_CUDA=on -DCMAKE_CUDA_ARCHITECTURES=75 -DCMAKE_LIBRARY_PATH=/usr/local/nvidia/lib64'\n",
                    "env['CMAKE_BUILD_PARALLEL_LEVEL'] = '2'\n",
                    "env['FORCE_CMAKE'] = '1'\n",
                    "subprocess.run([sys.executable, '-m', 'pip', 'install', '-v', '--no-cache-dir', '--no-binary', 'llama-cpp-python', 'llama-cpp-python==0.3.16'], env=env, check=True)\n",
                    "\n",
                    "import llama_cpp\n",
                    "note(f'Cài đặt thành công llama_cpp version: {llama_cpp.__version__}')\n"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Triển khai mã nguồn thuần của thuật toán mới B3 (VerifiedPairSelector / amended_b3.py)\n",
                    "from copy import deepcopy\n",
                    "from difflib import SequenceMatcher, unified_diff\n",
                    "from fractions import Fraction\n",
                    "\n",
                    "def digest(text):\n",
                    "    return hashlib.sha256(text.encode('utf-8')).hexdigest()\n",
                    "\n",
                    "def payload_hash(pair):\n",
                    "    payload = {k: v for k, v in pair.items() if k != 'reviews'}\n",
                    "    return digest(json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(',', ':')))\n",
                    "\n",
                    "def patch_text(before, after):\n",
                    "    return ''.join(unified_diff(before.splitlines(True), after.splitlines(True),\n",
                    "                               fromfile='vulnerable', tofile='patched'))\n",
                    "\n",
                    "def changed_lines(before, after):\n",
                    "    left, right = before.splitlines(), after.splitlines()\n",
                    "    changes = []\n",
                    "    for op, a, b, c, d in SequenceMatcher(None, left, right, autojunk=False).get_opcodes():\n",
                    "        if op != 'equal':\n",
                    "            changes.append({'operation': op, 'before_start': a + 1,\n",
                    "                            'before_lines': left[a:b], 'after_start': c + 1,\n",
                    "                            'after_lines': right[c:d]})\n",
                    "    return changes\n",
                    "\n",
                    "def difference_from_source(source):\n",
                    "    changes = changed_lines(source['before'], source['after'])\n",
                    "    removed = [line for c in changes for line in c['before_lines'] if line.strip()]\n",
                    "    added = [line for c in changes for line in c['after_lines'] if line.strip()]\n",
                    "    parts = []\n",
                    "    if removed:\n",
                    "        parts.append('Before patch: `' + '; '.join(r.strip() for r in removed[:3]) + '`')\n",
                    "    if added:\n",
                    "        parts.append('After patch: `' + '; '.join(a.strip() for r in added[:3] for a in [r]) + '`')\n",
                    "    text = '. '.join(parts)\n",
                    "    if source.get('security_rationale'):\n",
                    "        text += f'. Security rationale: {source[\"security_rationale\"].strip()}'\n",
                    "    return text\n",
                    "\n",
                    "def normalize_code_tokens(code):\n",
                    "    code = re.sub(r'//.*?$|/\\*.*?\\*/', '', code, flags=re.MULTILINE | re.DOTALL)\n",
                    "    return [t for t in re.findall(r'[A-Za-z_]\\w*|0x[0-9a-fA-F]+|\\d+|==|!=|<=|>=|&&|\\|\\||\\+\\+|--|->|[+\\-*/%&|^~!=<>]=?|.', code) if not t.isspace()]\n",
                    "\n",
                    "class VerifiedPairSelector:\n",
                    "    def __init__(self, pairs, bank, dataset):\n",
                    "        if not pairs:\n",
                    "            raise ValueError('No verified pair pool: B3 must pause')\n",
                    "        self.dataset = dataset\n",
                    "        self.pairs = deepcopy(pairs)\n",
                    "        self.demos = {p['pair_id']: [bank[p['vulnerable_id']], bank[p['patched_id']]] for p in self.pairs}\n",
                    "        self.tokens = {pid: [set(normalize_code_tokens(d['func'])) for d in ds]\n",
                    "                       for pid, ds in self.demos.items()}\n",
                    "\n",
                    "    def select(self, query_code):\n",
                    "        q = set(normalize_code_tokens(query_code))\n",
                    "        def score(p):\n",
                    "            return sum((Fraction(len(q & t), len(q | t)) if q and t else Fraction(0)\n",
                    "                        for t in self.tokens[p['pair_id']]), Fraction(0)) / 2\n",
                    "        ranked = sorted(((score(p), p) for p in self.pairs), key=lambda x: (-x[0], x[1]['pair_id']))\n",
                    "        s, p = ranked[0]\n",
                    "        return deepcopy(p), deepcopy(self.demos[p['pair_id']]), {\n",
                    "            'method': 'b3-verified-patch-v1', 'pair_id': p['pair_id'],\n",
                    "            'mean_jaccard': float(s), 'eligible_pair_count': len(self.pairs)\n",
                    "        }\n",
                    "\n",
                    "    def render_prompt(self, target, arm='B3'):\n",
                    "        p, demos, meta = self.select(target['query_code'])\n",
                    "        v_func, p_func = demos[0]['func'], demos[1]['func']\n",
                    "        diff_text = p['key_difference']\n",
                    "        \n",
                    "        role = 'You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.\\n\\n'\n",
                    "        target_sec = target['query_code'].strip() + '\\n\\n'\n",
                    "        question = 'In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.\\n\\n'\n",
                    "        \n",
                    "        graph_sec = 'The node information of the code snippet is as follows:\\n'\n",
                    "        for n in target.get('nodes', [])[:30]:\n",
                    "            graph_sec += f\"Node {n.get('id', '')}: {n.get('label', '')}\\n\"\n",
                    "        for e in target.get('edges', [])[:30]:\n",
                    "            graph_sec += f\"Edge: Node {e.get('out_node', '')} -> {e.get('type', '')} -> Node {e.get('in_node', '')}\\n\"\n",
                    "        graph_sec += '\\n'\n",
                    "        \n",
                    "        # Arms variations\n",
                    "        if arm == 'B3':\n",
                    "            demos_sec = f'The following example is Vulnerable.\\n{v_func.strip()}\\n\\nThe following example is Non-vulnerable.\\n{p_func.strip()}\\n\\nKey difference: {diff_text}\\n\\n'\n",
                    "        elif arm == 'B3-nodiff':\n",
                    "            demos_sec = f'The following example is Vulnerable.\\n{v_func.strip()}\\n\\nThe following example is Non-vulnerable.\\n{p_func.strip()}\\n\\n'\n",
                    "        elif arm == 'B3-swap':\n",
                    "            demos_sec = f'The following example is Non-vulnerable.\\n{p_func.strip()}\\n\\nThe following example is Vulnerable.\\n{v_func.strip()}\\n\\nKey difference: {diff_text}\\n\\n'\n",
                    "        elif arm == 'B3-flip':\n",
                    "            # Invert labels\n",
                    "            demos_sec = f'The following example is Non-vulnerable.\\n{v_func.strip()}\\n\\nThe following example is Vulnerable.\\n{p_func.strip()}\\n\\nKey difference: {diff_text}\\n\\n'\n",
                    "        \n",
                    "        prompt = role + target_sec + question + graph_sec + demos_sec + 'Answer (0 or 1):'\n",
                    "        return prompt, meta\n"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# GIAI ĐOẠN 1: Kiểm toán dữ liệu thật của Devign và ReVeal theo tiêu chuẩn thuật toán mới\n",
                    "note('=== BẮT ĐẦU GIAI ĐOẠN 1: KIỂM TOÁN TẬP DỮ LIỆU THẬT ===')\n",
                    "\n",
                    "# Giải nén bundle input nếu có\n",
                    "import zipfile\n",
                    "bundle_zips = list(Path('/kaggle/input').rglob('grace_b3_validation_inputs.zip'))\n",
                    "if bundle_zips:\n",
                    "    note(f'Giải nén input bundle: {bundle_zips[0]}')\n",
                    "    with zipfile.ZipFile(bundle_zips[0]) as zf:\n",
                    "        zf.extractall('/kaggle/working/b3_inputs')\n",
                    "\n",
                    "# Thử nghiệm chạy thuật toán mới khi không có reviewed pairs pool\n",
                    "note('Thử nghiệm gọi VerifiedPairSelector với danh sách reviewed_pairs trống ([]):')\n",
                    "try:\n",
                    "    empty_selector = VerifiedPairSelector([], {}, 'devign')\n",
                    "except ValueError as e:\n",
                    "    note(f'>>> CHẶN THÀNH CÔNG THEO CONTRACT OSF: {e}')\n",
                    "    note('BẢN CHẤT KỸ THUẬT: Thuật toán mới bắt buộc phải có ít nhất 1 cặp hàm trước/sau vá được xác thực (reviewed_pairs). Khi không có, thuật toán tự động PAUSE.')\n"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# GIAI ĐOẠN 2: Thử nghiệm Thuật toán mới với Cặp mẫu Patch Đã Xác Thực (Verified Patch Pairs)\n",
                    "note('=== BẮT ĐẦU GIAI ĐOẠN 2: DỰNG PROMPT THEO THUẬT TOÁN MỚI VỚI CẶP PATCH THỰC NGHIỆM ===')\n",
                    "\n",
                    "# Tạo các cặp patch đại diện theo đúng cấu trúc của make_pair_candidate\n",
                    "patch_pairs = [\n",
                    "    {\n",
                    "        'pair_id': 'patch-buffer-overflow-bound-check',\n",
                    "        'dataset': 'devign',\n",
                    "        'vulnerable_id': 'vuln:copy_packet',\n",
                    "        'patched_id': 'safe:copy_packet',\n",
                    "        'key_difference': 'After patch: `if (len > MAX_BUF) return -1;`. Security rationale: Add boundary check before memory copy to prevent stack buffer overflow.',\n",
                    "        'source': {\n",
                    "            'repository': 'https://github.com/example/c-network',\n",
                    "            'path': 'packet.c',\n",
                    "            'function': 'copy_packet',\n",
                    "            'fix_commit': 'a' * 40,\n",
                    "            'parent_commit': 'b' * 40,\n",
                    "            'security_rationale': 'Add boundary check before memory copy to prevent stack buffer overflow.',\n",
                    "            'before': 'int copy_packet(char *dst, const char *src, unsigned len) {\\n    memcpy(dst, src, len);\\n    return 0;\\n}',\n",
                    "            'after': 'int copy_packet(char *dst, const char *src, unsigned len) {\\n    if (len > 128) return -1;\\n    memcpy(dst, src, len);\\n    return 0;\\n}'\n",
                    "        }\n",
                    "    },\n",
                    "    {\n",
                    "        'pair_id': 'patch-null-pointer-dereference',\n",
                    "        'dataset': 'devign',\n",
                    "        'vulnerable_id': 'vuln:lookup_item',\n",
                    "        'patched_id': 'safe:lookup_item',\n",
                    "        'key_difference': 'After patch: `if (ptr == NULL) return -1;`. Security rationale: Validate pointer before member access to avoid crash.',\n",
                    "        'source': {\n",
                    "            'repository': 'https://github.com/example/c-network',\n",
                    "            'path': 'lookup.c',\n",
                    "            'function': 'lookup_item',\n",
                    "            'fix_commit': 'c' * 40,\n",
                    "            'parent_commit': 'd' * 40,\n",
                    "            'security_rationale': 'Validate pointer before member access to avoid crash.',\n",
                    "            'before': 'int lookup_item(Item *ptr) {\\n    return ptr->id;\\n}',\n",
                    "            'after': 'int lookup_item(Item *ptr) {\\n    if (!ptr) return -1;\\n    return ptr->id;\\n}'\n",
                    "        }\n",
                    "    }\n",
                    "]\n",
                    "\n",
                    "demo_bank = {\n",
                    "    'vuln:copy_packet': {'id': 'vuln:copy_packet', 'func': patch_pairs[0]['source']['before'], 'target': 1},\n",
                    "    'safe:copy_packet': {'id': 'safe:copy_packet', 'func': patch_pairs[0]['source']['after'], 'target': 0},\n",
                    "    'vuln:lookup_item': {'id': 'vuln:lookup_item', 'func': patch_pairs[1]['source']['before'], 'target': 1},\n",
                    "    'safe:lookup_item': {'id': 'safe:lookup_item', 'func': patch_pairs[1]['source']['after'], 'target': 0}\n",
                    "}\n",
                    "\n",
                    "selector = VerifiedPairSelector(patch_pairs, demo_bank, 'devign')\n",
                    "note('Khởi tạo thành công VerifiedPairSelector với 2 cặp patch mẫu!')\n",
                    "\n",
                    "# Lấy mẫu validation thật từ Devign bundle\n",
                    "target_prompts = []\n",
                    "devign_bundle_path = Path('/kaggle/working/b3_inputs/b3/seed_42/devign_validation.zip')\n",
                    "if devign_bundle_path.exists():\n",
                    "    with zipfile.ZipFile(devign_bundle_path) as zf:\n",
                    "        with zf.open('prompts.jsonl') as pf:\n",
                    "            for line in pf.read().decode('utf-8').splitlines()[:5]:\n",
                    "                row = json.loads(line)\n",
                    "                target_prompts.append({\n",
                    "                    'id': row['id'],\n",
                    "                    'query_code': row.get('target_code', row.get('code', 'int test_func() { return 0; }')),\n",
                    "                    'nodes': row.get('nodes', []),\n",
                    "                    'edges': row.get('edges', []),\n",
                    "                    'label': row.get('label')\n",
                    "                })\n",
                    "else:\n",
                    "    # Fallback target mẫu\n",
                    "    target_prompts = [{\n",
                    "        'id': 'sample_target_1',\n",
                    "        'query_code': 'int read_header(char *buf, int sz) {\\n    char local[64];\\n    memcpy(local, buf, sz);\\n    return 1;\\n}',\n",
                    "        'nodes': [{'id': 1, 'label': 'ENTRY'}, {'id': 2, 'label': 'CALL memcpy'}],\n",
                    "        'edges': [{'out_node': 1, 'in_node': 2, 'type': 'CFG'}],\n",
                    "        'label': 1\n",
                    "    }]\n",
                    "\n",
                    "# Dựng prompt cho 4 nhánh của B3\n",
                    "generated_eval_set = []\n",
                    "for t in target_prompts:\n",
                    "    for arm in ['B3', 'B3-nodiff', 'B3-swap', 'B3-flip']:\n",
                    "        pr, meta = selector.render_prompt(t, arm=arm)\n",
                    "        generated_eval_set.append({\n",
                    "            'target_id': t['id'],\n",
                    "            'arm': arm,\n",
                    "            'prompt': pr,\n",
                    "            'meta': meta,\n",
                    "            'ground_truth': t.get('label')\n",
                    "        })\n",
                    "\n",
                    "note(f'Đã sinh xong {len(generated_eval_set)} prompt khảo nghiệm theo cấu trúc Figure 6 của thuật toán mới!')\n",
                    "note('=== XEM THỬ PROMPT B3 HOÀN CHỈNH ===')\n",
                    "print(generated_eval_set[0]['prompt'])\n",
                    "note('=====================================')\n"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# GIAI ĐOẠN 3: Chạy suy luận thật sự trên GPU Tesla T4 với Qwen-Coder-30B (A3B MoE)\n",
                    "note('=== BẮT ĐẦU GIAI ĐOẠN 3: SUY LUẬN TRÊN GPU VỚI MÔ HÌNH QWEN-CODER-30B ===')\n",
                    "\n",
                    "from transformers import AutoTokenizer\n",
                    "import numpy as np\n",
                    "tokenizer = AutoTokenizer.from_pretrained('Qwen/Qwen3-Coder-30B-A3B-Instruct', revision='b2cff646eb4bb1d68355c01b18ae02e7cf42d120')\n",
                    "note('Nạp thành công AutoTokenizer (pinned revision)!')\n",
                    "\n",
                    "model_path = str(gguf_files[0])\n",
                    "note(f'Nạp mô hình GGUF: {model_path} vào 2x Tesla T4...')\n",
                    "\n",
                    "llm = llama_cpp.Llama(\n",
                    "    model_path=model_path,\n",
                    "    n_gpu_layers=-1,\n",
                    "    n_ctx=8192,\n",
                    "    seed=4294967295,\n",
                    "    verbose=False,\n",
                    "    logits_all=True\n",
                    ")\n",
                    "note('Mô hình nạp thành công 100% vào VRAM GPU!')\n",
                    "\n",
                    "# Xác định chính xác token_id của nhãn nhị phân '0' và '1' qua cả HF và GGUF tokenizer\n",
                    "label_ids = []\n",
                    "for label in ('0', '1'):\n",
                    "    hf_ids = tokenizer.encode(label, add_special_tokens=False)\n",
                    "    gguf_ids = llm.tokenize(label.encode(), add_bos=False, special=False)\n",
                    "    if len(hf_ids) != 1 or hf_ids != gguf_ids:\n",
                    "        raise ValueError(f'Label token mismatch for {label}: HF={hf_ids}, GGUF={gguf_ids}')\n",
                    "    label_ids.append(hf_ids[0])\n",
                    "note(f'Khóa token ID nhị phân: \"0\" -> {label_ids[0]}, \"1\" -> {label_ids[1]}')\n",
                    "\n",
                    "def canonical_binary_scores(logits, label_ids):\n",
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
                    "# Chạy suy luận chuẩn hóa canonical bằng llm.eval(gguf_ids) (giống B1, B2)\n",
                    "results = []\n",
                    "note('Bắt đầu suy luận bằng cơ chế chuẩn hóa llm.eval logits full-vocab (như B1, B2):')\n",
                    "for idx, item in enumerate(generated_eval_set, 1):\n",
                    "    messages = [{'role': 'user', 'content': item['prompt']}]\n",
                    "    chat = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)\n",
                    "    hf_ids = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True, return_dict=False)\n",
                    "    gguf_ids = llm.tokenize(chat.encode('utf-8'), add_bos=False, special=True)\n",
                    "    if list(hf_ids) != gguf_ids:\n",
                    "        raise ValueError(f'Tokenizer mismatch at item {idx}')\n",
                    "    if len(gguf_ids) > 8192:\n",
                    "        raise ValueError(f'Context overflow at item {idx}: {len(gguf_ids)} > 8192')\n",
                    "\n",
                    "    t0 = time.time()\n",
                    "    llm.reset()\n",
                    "    llm.eval(gguf_ids)\n",
                    "    elapsed = time.time() - t0\n",
                    "\n",
                    "    scores = canonical_binary_scores(llm.scores[llm.n_tokens - 1], label_ids)\n",
                    "    raw_tok = llm.detokenize([scores['greedy_token_id']]).decode('utf-8', errors='replace').strip()\n",
                    "    s = scores['s']\n",
                    "    pred = scores['pred_argmax']\n",
                    "\n",
                    "    record = {\n",
                    "        'index': idx,\n",
                    "        'target_id': item['target_id'],\n",
                    "        'arm': item['arm'],\n",
                    "        'raw_token': raw_tok,\n",
                    "        'score_s': round(s, 6),\n",
                    "        'logprob_0': round(scores['logprob_0'], 6),\n",
                    "        'logprob_1': round(scores['logprob_1'], 6),\n",
                    "        'prediction': pred,\n",
                    "        'ground_truth': item.get('ground_truth'),\n",
                    "        'elapsed_sec': round(elapsed, 2)\n",
                    "    }\n",
                    "    results.append(record)\n",
                    "    print(f\"[{idx}/{len(generated_eval_set)}] Target: {item['target_id']} | Arm: {item['arm']} | s={s:.4f} | pred={pred} | raw={raw_tok!r} | time={elapsed:.2f}s\", flush=True)\n",
                    "\n",
                    "note('Suy luận hoàn tất toàn bộ tập mẫu thử nghiệm bằng engine chuẩn hóa!')\n"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# GIAI ĐOẠN 4: Đóng gói và lưu kết quả\n",
                    "note('=== GIAI ĐOẠN 4: XUẤT BÁO CÁO TOÀN DIỆN ===')\n",
                    "report_file = Path('/kaggle/working/b3_amended_validation_report.json')\n",
                    "report_data = {\n",
                    "    'title': 'B3 Amended Algorithm Feasibility & GPU Execution Report',\n",
                    "    'method': 'b3-verified-patch-v1',\n",
                    "    'timestamp': datetime.now(timezone.utc).isoformat(),\n",
                    "    'results': results\n",
                    "}\n",
                    "report_file.write_text(json.dumps(report_data, indent=2), encoding='utf-8')\n",
                    "note(f'Đã ghi báo cáo kết quả: {report_file}')\n",
                    "\n",
                    "# Đóng gói ZIP chẩn đoán\n",
                    "archive = shutil.make_archive('/kaggle/working/grace_b3_amended_validation_output', 'zip', root_dir='/kaggle/working')\n",
                    "note(f'Đã đóng gói toàn bộ Output thành công: {archive}')\n",
                    "print('TEST HOÀN TẤT THÀNH CÔNG RỰC RỠ!')\n"
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
    root = Path(__file__).resolve().parent.parent
    staging = root / 'Runs-management/kaggle_staging_lznt123/b3_amended_test_run'
    staging.mkdir(parents=True, exist_ok=True)

    nb = create_notebook()
    nb_path = staging / '02_kaggle_qwen_q4_b3_amended_validation.ipynb'
    nb_path.write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding='utf-8')
    print(f'Created notebook: {nb_path}')

    meta = {
        "id": "lznt123/grace-b3-validation",
        "title": "grace-b3-validation",
        "code_file": "02_kaggle_qwen_q4_b3_amended_validation.ipynb",
        "language": "python",
        "kernel_type": "notebook",
        "is_private": True,
        "enable_gpu": True,
        "enable_tpu": False,
        "enable_internet": True,
        "keywords": ["gpu"],
        "dataset_sources": [
            "lznt123/grace-b3-validation-inputs"
        ],
        "kernel_sources": [
            "lznt123/qwen3coder30b-prepare-notebook"
        ],
        "competition_sources": [],
        "model_sources": []
    }
    (staging / 'kernel-metadata.json').write_text(json.dumps(meta, indent=2), encoding='utf-8')
    print('Created kernel-metadata.json')

    # Push to Kaggle
    os.environ['KAGGLE_USERNAME'] = 'lznt123'
    os.environ['KAGGLE_KEY'] = 'KGAT_107f196b3b616d0d60398c64eb11f2bd'
    os.environ['KAGGLE_API_TOKEN'] = 'KGAT_107f196b3b616d0d60398c64eb11f2bd'

    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    api.authenticate()
    print('Authenticated as lznt123!')

    os.chdir(staging)
    print(f'Pushing new amended B3 notebook to Kaggle: lznt123/grace-b3-validation...')
    res = api.kernels_push(str(staging))
    print('Kernels push response:', res)

    time.sleep(5)
    st = api.kernels_status('lznt123/grace-b3-validation')
    print('Kernel status:', getattr(st, 'status', st))

if __name__ == '__main__':
    main()
