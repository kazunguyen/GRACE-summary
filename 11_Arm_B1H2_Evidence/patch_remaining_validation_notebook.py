import json
from pathlib import Path

path = Path(__file__).parent / "notebooks" / "colab_l4_b1h2_remaining_validation_20261106.ipynb"
notebook = json.loads(path.read_text(encoding="utf-8"))
setup_cell = '''# Pin dependencies and build llama.cpp with logs on Colab's local disk.
# Google Drive FUSE can disconnect during a long CUDA build, so never stream compiler output to OUT.
LOCAL_LOG_DIR = Path('/content/b1h2_l4_setup_logs')
LOCAL_LOG_DIR.mkdir(parents=True, exist_ok=True)

def sync_setup_log(name):
    source = LOCAL_LOG_DIR / name
    try:
        OUT.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, OUT / name)
        print(f'Saved setup log to Drive: {OUT / name}', flush=True)
    except OSError as exc:
        print(f'Could not copy {name} to Drive ({exc}); local copy remains at {source}', flush=True)

packages = [
    'numpy==2.1.3',
    'huggingface-hub==0.36.2',
    'tokenizers==0.22.2',
    'transformers==4.57.1',
    'scikit-learn==1.5.2',
]
name = 'install_python_dependencies.log'
with (LOCAL_LOG_DIR / name).open('w', encoding='utf-8') as log:
    p = subprocess.Popen([sys.executable, '-m', 'pip', 'install', '--no-cache-dir', *packages], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    line_count = 0
    for line in p.stdout:
        log.write(line); line_count += 1
        if line_count % 50 == 0: print(f'Python dependencies: captured {line_count} lines', flush=True)
    result = p.wait()
sync_setup_log(name)
if result != 0: raise RuntimeError(f'Pinned Python dependency installation failed; local log: {LOCAL_LOG_DIR / name}')

os.environ['CMAKE_ARGS'] = '-DGGML_CUDA=on -DCMAKE_CUDA_ARCHITECTURES=89'
os.environ['CMAKE_BUILD_PARALLEL_LEVEL'] = '2'
os.environ['FORCE_CMAKE'] = '1'
name = 'install_llama_cpp_cuda.log'
with (LOCAL_LOG_DIR / name).open('w', encoding='utf-8') as log:
    cmd = [sys.executable, '-m', 'pip', 'install', '-v', '--no-cache-dir', '--no-binary', 'llama-cpp-python', 'llama-cpp-python==0.3.16']
    log.write(f'Command: {cmd}\\nCMAKE_ARGS={os.environ["CMAKE_ARGS"]}\\n'); log.flush()
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, env=os.environ.copy())
    line_count = 0
    for line in p.stdout:
        log.write(line); line_count += 1
        if line_count % 100 == 0: print(f'CUDA build: captured {line_count} lines', flush=True)
    result = p.wait()
sync_setup_log(name)
if result != 0: raise RuntimeError(f'CUDA build of llama-cpp-python failed; local log: {LOCAL_LOG_DIR / name}')
'''
inference_cell = '''# Resume-safe inference over all remaining validation prompts; one record is fsynced after each completed prompt.
import numpy as np

def binary_scores(logits, ids):
    values = np.asarray(logits, dtype=np.float64).reshape(-1)
    if not np.all(np.isfinite(values)):
        raise ValueError('Non-finite logits')
    m = float(np.max(values))
    normalizer = m + float(np.log(np.exp(values - m).sum()))
    lp0 = float(values[ids[0]] - normalizer)
    lp1 = float(values[ids[1]] - normalizer)
    s = float(np.exp(lp1 - np.logaddexp(lp0, lp1)))
    top = np.argsort(values)[-5:][::-1]
    return {
        'logprob_0': lp0, 'logprob_1': lp1,
        'p0': math.exp(lp0), 'p1': math.exp(lp1), 's': s,
        'pred_argmax': int(s >= 0.5),
        'greedy_token_id': int(np.argmax(values)),
        'top5': [{'token_id': int(i), 'logprob': float(values[i] - normalizer)} for i in top],
    }

records_path = OUT / 'records.jsonl'
done = {}
if records_path.exists():
    for line in records_path.read_text(encoding='utf-8').splitlines():
        if line.strip():
            r = json.loads(line)
            if r['id'] in done:
                raise ValueError(f'Duplicate checkpoint ID: {r["id"]}')
            done[r['id']] = r

with records_path.open('a', encoding='utf-8', newline='\\n') as f:
    for ix, item in enumerate(rows, 1):
        if time.monotonic() - PILOT_START >= MAX_RUNTIME_SECONDS:
            note('Reached the 9-hour safety limit; completed records are preserved for resume.')
            break
        if item['id'] in done:
            if done[item['id']]['prompt_sha256'] != item['prompt_sha256']:
                raise ValueError(f'Checkpoint prompt mismatch: {item["id"]}')
            continue
        if hashlib.sha256(item['prompt'].encode('utf-8')).hexdigest() != item['prompt_sha256']:
            raise ValueError(f'Prompt hash mismatch: {item["id"]}')
        chat = tokenizer.apply_chat_template([{'role':'user','content':item['prompt']}], tokenize=False, add_generation_prompt=True)
        hf_ids = tokenizer.apply_chat_template([{'role':'user','content':item['prompt']}], tokenize=True, add_generation_prompt=True)
        gguf_ids = llm.tokenize(chat.encode('utf-8'), add_bos=False, special=True)
        if list(hf_ids) != gguf_ids:
            raise ValueError(f'Tokenizer mismatch at {item["id"]}')
        if len(gguf_ids) > 8192:
            raise ValueError(f'Context overflow at {item["id"]}: {len(gguf_ids)}')
        started = time.monotonic()
        llm.reset()
        llm.eval(gguf_ids)
        scores = binary_scores(llm.scores[llm.n_tokens - 1], label_ids)
        raw = llm.detokenize([scores['greedy_token_id']]).decode('utf-8', errors='replace').strip()
        row = {k:item[k] for k in ('id','dataset','split','arm','seed','prompt_variant','prompt_sha256')}
        if 'label' in item:
            row['label'] = item['label']
        row.update(scores, raw=raw, response_valid=raw in ('0','1'), token_ids={'0':label_ids[0],'1':label_ids[1]}, prompt_tokens=len(gguf_ids), model_sha256=model_digest, model_repo=MODEL_REPO, model_repo_revision='local-sha256:'+model_digest, quantization='Q4_K_M', backend='llama-cpp-python', llama_cpp_python=llama_cpp_version, gpu=gpu, seed=42, elapsed_s=time.monotonic()-started, pilot_only=False, validation_only=True)
        f.write(json.dumps(row, ensure_ascii=False, allow_nan=False)+'\\n')
        f.flush()
        os.fsync(f.fileno())
        done[item['id']] = row
        note(f'[{ix}/{len(rows)}] {item["id"]}: logprob_0={scores["logprob_0"]:.6f} logprob_1={scores["logprob_1"]:.6f} s={scores["s"]:.6f} raw={raw!r}')

status = {'status':'complete','expected':len(rows),'gpu':gpu,'all_layers_offloaded':all_layers_offloaded,'runtime_cap_seconds':MAX_RUNTIME_SECONDS,'expected_records':len(rows)}
status['records_written'] = sum(1 for line in records_path.read_text(encoding='utf-8').splitlines() if line.strip())
status['status'] = 'complete' if status['records_written'] == len(rows) else 'incomplete_or_timed_out'
(OUT / 'pilot_status.json').write_text(json.dumps(status, indent=2), encoding='utf-8')
archive = shutil.make_archive(str(OUT), 'zip', root_dir=OUT)
note(f'Validation output archive: {archive}')
'''
for cell in notebook["cells"]:
    if cell.get("cell_type") != "code":
        continue
    source = "".join(cell["source"])
    source = source.replace(
        "'sample_seed':20261106,'pilot_only':True,'validation_only':True",
        "'validation_continuation':True,'pilot_only':False,'validation_only':True",
    )
    source = source.replace("pilot_only=True)", "pilot_only=False, validation_only=True)")
    if "install_llama_cpp_cuda.log" in source:
        source = setup_cell
    if "# Resume-safe inference over all remaining validation prompts" in source:
        source = inference_cell
    cell["source"] = source.splitlines(keepends=True)
    cell["execution_count"] = None
    cell["outputs"] = []
path.write_text(json.dumps(notebook, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
for index, cell in enumerate(notebook["cells"]):
    if cell.get("cell_type") == "code":
        compile("".join(cell["source"]), f"cell-{index}", "exec")
assert sum(len(cell.get("outputs", [])) for cell in notebook["cells"]) == 0
assert "1FuYcMkEuMBAFYexmg0c1HL5BxPB_L_Vg" in path.read_text(encoding="utf-8")
print(f"Patched {path}")
