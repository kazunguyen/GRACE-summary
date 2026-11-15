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

def run_inference(arm, model_path, bundle_zip, out_dir, tau_star, is_repeat=False, cache_tag=None):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    rec_path = out_dir / 'records.jsonl'
    man_path = out_dir / 'run_manifest.json'
    eval_path = out_dir / 'evaluation.json'
    
    with zipfile.ZipFile(bundle_zip) as z:
        manifest = json.loads(z.read('bundle_manifest.json'))
        prompts = [json.loads(line) for line in z.read('prompts.jsonl').decode('utf-8').splitlines() if line.strip()]
    
    ds = manifest['dataset']
    total_count = len(prompts)
    print(f'Starting inference for {arm} {ds} test: {total_count} prompts, fixed tau={tau_star}')
    
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
    
    arm_slug = arm.lower().replace('-', '_')
    checkpoint_file = Path('/kaggle/working') / f'grace_{arm_slug}_test_checkpoint.zip'
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
            hf_ids = tok.apply_chat_template(messages, tokenize=True, add_generation_prompt=True, return_dict=False)
            gguf_ids = llm.tokenize(chat.encode('utf-8'), add_bos=False, special=True)
            if list(hf_ids) != gguf_ids:
                raise ValueError(f'Tokenizer mismatch at {ds}/{uid}; abort rather than alter prompt')
            if len(gguf_ids) > 8192:
                raise ValueError(f'Prompt exceeded context budget: {len(gguf_ids)} > 8192')
            
            start = time.monotonic()
            llm.reset()
            llm.eval(gguf_ids)
            last_logits = llm.scores[llm.n_tokens - 1]
            res = binary_scores(last_logits, label_ids)
            elapsed_s = time.monotonic() - start
            
            raw = llm.detokenize([res['greedy_token_id']]).decode('utf-8', errors='replace').strip()
            raw_valid = raw in ('0', '1')
            s_val = res['s']
            pred_tau = int(s_val >= tau_star)
            
            rec = {
                'id': uid,
                'arm': arm,
                'seed': 42,
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
            if is_repeat:
                rec['repeat'] = True
                rec['tag'] = cache_tag or 'repeat'
            
            out_f.write(json.dumps(rec, ensure_ascii=False) + '\n')
            out_f.flush()
            os.fsync(out_f.fileno())
            done_ids.add(uid)
            
            now = time.time()
            print(f'{arm}/{ds} {uid}: s={s_val:.4f}, raw={raw!r} ({len(done_ids)}/{total_count})', flush=True)
            
            if len(done_ids) % 100 == 0 or (now - last_snapshot_time) >= 120:
                save_snapshot()
                last_snapshot_time = now
    
    save_snapshot()
    
    # Compute final test metrics at fixed tau*
    from sklearn.metrics import matthews_corrcoef, roc_auc_score, balanced_accuracy_score, f1_score
    all_recs = [json.loads(l) for l in rec_path.read_text(encoding='utf-8').splitlines() if l.strip()]
    y_true = np.array([r['label'] for r in all_recs])
    y_pred = np.array([r['pred_tau'] for r in all_recs])
    y_score = np.array([r['s'] for r in all_recs])
    
    eval_summary = {
        'arm': arm,
        'dataset': ds,
        'split': 'test',
        'seed': 42,
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
    print(f'Finished {arm} {ds} test: MCC={eval_summary["mcc_at_tau"]:.4f}, AUROC={eval_summary["auroc"]:.4f}')
    
    run_manifest = {
        'arm': arm,
        'dataset': ds,
        'split': 'test',
        'seed': 42,
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
    if is_repeat:
        run_manifest['repeat'] = True
        run_manifest['tag'] = cache_tag or 'repeat'
    man_path.write_text(json.dumps(run_manifest, indent=2, ensure_ascii=False), encoding='utf-8')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--arm', required=True)
    parser.add_argument('--model', required=True)
    parser.add_argument('--bundle', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--tau', type=float, required=True)
    parser.add_argument('--repeat', action='store_true')
    parser.add_argument('--tag', default='repeat')
    args = parser.parse_args()
    run_inference(args.arm, args.model, args.bundle, args.out, args.tau, args.repeat, args.tag)
