import ast
import hashlib
import io
import json
from pathlib import Path
import re
import zipfile

HERE = Path(__file__).resolve().parent
ARM = HERE.parent
ROOT = ARM.parent
sha = lambda raw: hashlib.sha256(raw).hexdigest()
old_zip = ARM / 'test_delivery_20261107/grace_b2_rand_test_seeds_42_43_bundle.zip'
new_zip = ARM / 'test_delivery_seed44_20261107/grace_b2_rand_test_seed44_bundle.zip'
seed44_notebook = next(new_zip.parent.glob('02_kaggle*seed44_test.ipynb'))
source = json.loads(seed44_notebook.read_bytes())
src = lambda i: ''.join(source['cells'][i]['source'])
runtime_bytes = (ROOT/'configs/inference_runtime_lock.json').read_bytes()
runtime = json.loads(runtime_bytes)
runtime_sha = sha(runtime_bytes)
if source['metadata']['grace_runtime_lock']['sha256'] != runtime_sha:
    raise ValueError('Seed44 bootstrap and current runtime lock differ')
bootstrap = src(1)
for node in ast.parse(bootstrap).body:
    if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'RUNTIME_LOCK_BYTES' for t in node.targets):
        assert ast.literal_eval(node.value) == runtime_bytes
assert runtime['packages']['scipy'] == '1.16.3'

members = {}
inputs = []
outcomes = {}
def rows(raw):
    return [json.loads(l) for l in raw.splitlines() if l.strip()]
def serialize(items):
    return b''.join((json.dumps(row, ensure_ascii=False, separators=(',', ':'))+'\n').encode() for row in items)

with zipfile.ZipFile(old_zip) as before, zipfile.ZipFile(new_zip) as after:
    threshold_bytes = after.read('threshold_lock.json')
    threshold = json.loads(threshold_bytes)
    old_threshold = json.loads(before.read('threshold_lock.json'))
    for key, entry in old_threshold['entries'].items():
        for field in ('tau_star','validation_records_sha256','validation_prompt_set_sha256','model_sha256','split_used'):
            assert entry[field] == threshold['entries'][key][field], (key, field)
    for seed in (42,43,44):
        archive = before if seed < 44 else after
        if seed < 44:
            cp_path = ROOT / f'Runs-management/kaggle_outputs_20261107/b2_rand_seed{seed}_test_latest/grace_b2_rand_seed{seed}_test_checkpoint.zip'
            cp_data = cp_path.read_bytes()
            outcomes[seed] = sha(cp_data)
        for ds in ('devign','reveal'):
            prefix = f'b2_rand_tail_{seed}_{ds}'
            with zipfile.ZipFile(io.BytesIO(archive.read(f'seed_{seed}/{ds}_test.zip'))) as z:
                manifest = json.loads(z.read('bundle_manifest.json'))
                raw = z.read('prompts.jsonl')
            assert manifest['prompts_sha256'] == sha(raw)
            items = rows(raw)
            census_count = len(items)
            by_id = {row['id']:row for row in items}
            assert len(by_id) == census_count == manifest['count']
            entry = threshold['entries'][f'B2-rand/{seed}/{ds}']
            assert manifest['tau_star'] == entry['tau_star']
            completed = 0
            provenance = {}
            if seed < 44:
                with zipfile.ZipFile(io.BytesIO(cp_data)) as checkpoint:
                    prior_raw = checkpoint.read(f'seed_{seed}/{ds}/test/records.jsonl')
                    prior_runtime = sha(checkpoint.read('inference_runtime_lock.json'))
                    assert json.loads(checkpoint.read('threshold_lock.json'))['locked_sha256'] == old_threshold['locked_sha256']
                    expected_count = json.loads(checkpoint.read(f'seed_{seed}_status.json'))['runs'][f'{ds}/test']['completed']
                done = set()
                for row in rows(prior_raw):
                    uid = row['id']
                    assert uid not in done and uid in by_id
                    assert (row['arm'],row['seed'],row['dataset'],row['split']) == ('B2-rand',seed,ds,'test')
                    assert (row['label'],row['prompt_sha256']) == (by_id[uid]['label'],by_id[uid]['prompt_sha256'])
                    assert (row['model_sha256'],row['runtime_contract_sha256'],row['tau']) == (runtime['model']['sha256'],prior_runtime,entry['tau_star'])
                    done.add(uid)
                completed = len(done)
                assert completed == expected_count
                items = [row for row in items if row['id'] not in done]
                provenance = dict(exclusion_basis='verified_checkpoint_ids', prior_records_sha256=sha(prior_raw), prior_checkpoint_sha256=outcomes[seed],
                                  prior_runtime_sha256=prior_runtime)
            else:
                # Use the user's assumed cutoff, indexed by original prompt order.
                completed = census_count if ds == 'devign' else 1900
                if census_count != (2732 if ds == 'devign' else 2274):
                    raise ValueError(f'Unexpected seed 44 census size: {ds}/{census_count}')
                items = items[completed:]
                provenance = dict(exclusion_basis='assumed_seed44_cutoff',
                                  first_selected_position=completed + 1 if items else None)
            filtered = serialize(items)
            manifest.update(count=len(items), prompts_sha256=sha(filtered))
            members[prefix+'_manifest.json'] = json.dumps(manifest).encode()
            members[prefix+'_prompts.jsonl'] = filtered
            inputs.append(dict(seed=seed,dataset=ds,prefix=prefix,census_count=census_count,excluded_before=completed, **provenance))
            print(seed, ds, census_count, completed, len(items))

members['b2_rand_tail_threshold_lock.json'] = threshold_bytes
members['b2_rand_tail_delivery.json'] = (json.dumps(dict(inputs=inputs, runtime_contract_sha256=runtime_sha,
                                                         threshold_lock_sha256=threshold['locked_sha256']), indent=2)+'\n').encode()
bundle = HERE/'grace_b2_rand_three_seed_test_tail_inputs.zip'
with zipfile.ZipFile(bundle,'w') as z:
    for name,data in sorted(members.items()):
        info = zipfile.ZipInfo(name)
        z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED)
bundle_sha = sha(bundle.read_bytes())
header = f'BUNDLE_NAME = {bundle.name!r}\nBUNDLE_SHA256 = {bundle_sha!r}\n'
header += f'THRESHOLD_LOCK_SHA256 = {threshold["locked_sha256"]!r}\nMEMBERS = {dict(sorted((n,sha(v)) for n,v in members.items()))!r}\n\n'

worker = src(7)
def replace(old,new,count=1):
    global worker
    if worker.count(old) != count:
        raise ValueError(f'Unexpected source shape for {old}')
    worker = worker.replace(old,new)
replace('status_path, prompt_seed, expected_model_sha256, arm):','status_path, expected_model_sha256, arm):')
replace("if arm != 'B2-rand' or prompt_seed != 44 or limit is not None or not (1 <= len(runs) <= 2) or any(r[1] != 'test' for r in runs):\n        raise ValueError('Only complete B2-rand test census for prompt seed 44 is allowed')",
        "if arm != 'B2-rand' or limit is not None or not (1 <= len(runs) <= 6) or any(s not in (42, 43, 44) or d not in ('devign', 'reveal') or split != 'test' for s, d, split, _, _ in runs):\n        raise ValueError('Only B2-rand test tails for seeds 42, 43 and 44 are allowed')\n    if len({(s,d) for s,d,_,_,_ in runs}) != len(runs):\n        raise ValueError('Duplicate seed/dataset run')")
replace('for dataset, split, bundle, out in runs:', 'for prompt_seed, dataset, split, bundle, out in runs:',2)
replace('for dataset, split, bundle, out_text in runs:', 'for prompt_seed, dataset, split, bundle, out_text in runs:')
replace("key = f'{dataset}/{split}'","key = f'{prompt_seed}/{dataset}/{split}'",2)
replace('load_bundle(runs[0][2])','load_bundle(runs[0][3])')
replace("All four bundles must use the same tokenizer revision and context budget","All bundles must use the same tokenizer revision and context budget")
replace("        metrics = evaluate_output(output)\n        (out / 'evaluation.json').write_text(json.dumps(metrics, indent=2, allow_nan=False), encoding='utf-8')\n        progress.update(state='complete', completed=len(rows), evaluation=str(out / 'evaluation.json'))",
        "        progress.update(state='complete', completed=len(rows))")
replace("    ap.add_argument('--prompt-seed', type=int, required=True, help='Frozen prompt-set seed; inference uses llama.cpp default seed')\n","")
replace("nargs=4, metavar=('DATASET', 'SPLIT', 'BUNDLE', 'OUT')","nargs=5, metavar=('SEED', 'DATASET', 'SPLIT', 'BUNDLE', 'OUT')")
replace("    run_batch(args.run,", "    runs = [(int(seed), ds, split, bundle, out) for seed, ds, split, bundle, out in args.run]\n    run_batch(runs,")
replace("args.status, args.prompt_seed, args.expected_model_sha256","args.status, args.expected_model_sha256")
replace("""                print(f'{key} {row_id}: s={scores["s"]:.4f}, raw={raw!r} ({len(done)}/{len(rows)})', flush=True)""",
        """                if len(done) % 25 == 0 or len(done) == len(rows):
                    print(f'{key}: {len(done)}/{len(rows)}', flush=True)""")

markdown = '''# B2-rand: finish test for seeds 42, 43 and 44 in one Kaggle session

Select T4 x2 and enable Internet. Attach the three-seed tail bundle and the pinned GGUF. Attach a tail checkpoint only when resuming this notebook.

The bundle includes 257 verified missing REVEAL prompts for seed 42, 246 for seed 43 and original positions 1901 through 2274 for seed 44. The seed 44 cutoff assumes all Devign and the first 1900 REVEAL prompts were scored by the earlier run. Reconcile against its actual output before combining results.

One worker loads the model once and scores the three groups in the same session. The notebook applies the current runtime lock and fixed validation thresholds and saves outputs separately from earlier runs. The nine-hour budget includes setup and reserves five minutes for export.
'''
driver = (HERE/'run_tail.py').read_text(encoding='utf-8')
loader = (HERE/'prepare_inputs.py').read_text(encoding='utf-8')
cells = []
for i, value in enumerate((markdown,bootstrap,header+loader,src(4),src(5),src(6),worker,driver)):
    cell = dict(cell_type='markdown' if i==0 else 'code', metadata={}, source=value.splitlines(keepends=True))
    if i:
        compile(value.split('\n',1)[1] if value.startswith('%%writefile') else value,f'cell{i}','exec')
        cell.update(execution_count=None, outputs=[])
    cells.append(cell)
notebook = dict(cells=cells, metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},
                'language_info':{'name':'python'},'grace_runtime_lock':source['metadata']['grace_runtime_lock']},
                nbformat=4,nbformat_minor=4)
path = HERE/'03_kaggle_qwen_q4_b2_rand_three_seed_test_tail.ipynb'
path.write_bytes((json.dumps(notebook,indent=2,ensure_ascii=False)+'\n').encode())
(HERE/'delivery_manifest.json').write_bytes((json.dumps(dict(bundle=bundle.name,bundle_sha256=bundle_sha,
    notebook=path.name,notebook_sha256=sha(path.read_bytes()),runtime_contract_sha256=runtime_sha,
    threshold_lock_sha256=threshold['locked_sha256'],inputs=inputs),indent=2)+'\n').encode())
print('Notebook',path)
print('Bundle',bundle,bundle_sha)
