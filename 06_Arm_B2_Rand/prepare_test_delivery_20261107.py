"""Lock complete B2-rand validation seeds and prepare resumable Kaggle test notebooks."""
from __future__ import annotations

import hashlib
import json
import math
import pathlib
import zipfile
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE_BUNDLE = ROOT / "Runs-management/kaggle_validation_6arms_20261104/grace_b2_rand_inputs.zip"
OUTPUTS = ROOT / "Runs-management/kaggle_outputs_20261107/b2_rand_latest/grace_b2_rand_checkpoint.zip"
TEMPLATE = ROOT / "11_Arm_B1H2_Evidence/kaggle_b1h2_test_20261106/02_kaggle_qwen_q4_b1_h2_test_20261106.ipynb"
RUNNER = ROOT / "Runs-management/kaggle_outputs_20261107/b1h2_test_latest/kaggle_inference.py"
CONFIG = ROOT / "06_Arm_B2_Rand/config/threshold.json"
OUT = ROOT / "06_Arm_B2_Rand/test_delivery_20261107"
OUT.mkdir(parents=True, exist_ok=True)

MODEL_SHA = "f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335"
MODEL_FILE = "Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf"
TOKENIZER = "Qwen/Qwen3-Coder-30B-A3B-Instruct"
TOKENIZER_REV = "b2cff646eb4bb1d68355c01b18ae02e7cf42d120"
RULES = {
    "version": "validation_mcc_grid_v1",
    "grid": [i / 100 for i in range(1, 100)],
    "objective": "MCC on finite valid validation scores only",
    "comparison": "score >= threshold",
    "tie_break": "within 1e-9: closest to 0.5, then lower threshold",
    "test_usage": "never read test records or metrics to choose threshold",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_sha(value) -> str:
    return sha(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))


def json_bytes(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")


def zip_bytes(files: dict[str, bytes]) -> bytes:
    import io
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 11, 7, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o600 << 16
            z.writestr(info, data)
    return buffer.getvalue()


def read_inner(raw: bytes):
    import io
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        prompt_bytes = z.read("prompts.jsonl")
        manifest_bytes = z.read("bundle_manifest.json")
        rows = [json.loads(line) for line in prompt_bytes.decode("utf-8").splitlines() if line.strip()]
        manifest = json.loads(manifest_bytes)
    if sha(prompt_bytes) != manifest["prompts_sha256"]:
        raise ValueError("Frozen prompts hash does not match manifest")
    if len(rows) != manifest["count"] or len({str(r["id"]) for r in rows}) != len(rows):
        raise ValueError("Frozen bundle count/ID mismatch")
    for row in rows:
        if sha(row["prompt"].encode("utf-8")) != row["prompt_sha256"]:
            raise ValueError(f"Prompt hash mismatch: {row['id']}")
    return prompt_bytes, manifest, rows


def mcc(labels, preds):
    tp = sum(y == 1 and p == 1 for y, p in zip(labels, preds))
    tn = sum(y == 0 and p == 0 for y, p in zip(labels, preds))
    fp = sum(y == 0 and p == 1 for y, p in zip(labels, preds))
    fn = sum(y == 1 and p == 0 for y, p in zip(labels, preds))
    den = math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    return (tp * tn - fp * fn) / den if den else None


def fit(rows):
    valid = [r for r in rows if r.get("valid") and isinstance(r.get("s"), (int, float)) and math.isfinite(r["s"])]
    if len(valid) != len(rows) or {r["label"] for r in valid} != {0, 1}:
        raise ValueError("Expected all validation rows to have finite valid scores and both labels")
    grid = []
    best_tau = 0.5
    best_mcc = None
    for tau in RULES["grid"]:
        value = mcc([r["label"] for r in valid], [int(r["s"] >= tau) for r in valid])
        grid.append({"tau": tau, "mcc": value})
        if value is None:
            continue
        if best_mcc is None or value > best_mcc + 1e-9 or (
            abs(value - best_mcc) <= 1e-9 and (abs(tau - 0.5), tau) < (abs(best_tau - 0.5), best_tau)
        ):
            best_tau, best_mcc = tau, value
    return best_tau, best_mcc, grid


with zipfile.ZipFile(SOURCE_BUNDLE) as z:
    frozen_inputs = {n: z.read(n) for n in z.namelist()}
with zipfile.ZipFile(OUTPUTS) as z:
    checkpoint = {n: z.read(n) for n in z.namelist() if not n.endswith("/")}

entries = {}
validation_source = {}
test_sources = {}
for seed in (42, 43):
    for dataset, expected_n in (("devign", 2732), ("reveal", 2273)):
        validation_name = f"seed_{seed}/{dataset}/validation/records.jsonl"
        manifest_name = f"seed_{seed}/{dataset}/validation/run_manifest.json"
        records_bytes = checkpoint[validation_name]
        records = [json.loads(line) for line in records_bytes.decode("utf-8").splitlines() if line.strip()]
        run_manifest = json.loads(checkpoint[manifest_name])
        input_name = f"seed_{seed}/{dataset}_validation_b2_rand_seed_{seed}_kaggle.zip"
        prompt_bytes, val_manifest, prompts = read_inner(frozen_inputs[input_name])
        if len(records) != expected_n or len(prompts) != expected_n:
            raise ValueError(f"Incomplete validation set {seed}/{dataset}: {len(records)}/{expected_n}")
        expected = {str(r["id"]): r for r in prompts}
        observed = {}
        for row in records:
            uid = str(row["id"])
            if uid in observed:
                raise ValueError(f"Duplicate validation ID: {seed}/{dataset}/{uid}")
            if (row.get("arm"), row.get("seed"), row.get("dataset"), row.get("split"), row.get("model_sha256")) != (
                "B2-rand", seed, dataset, "validation", MODEL_SHA
            ):
                raise ValueError(f"Validation identity mismatch: {seed}/{dataset}/{uid}")
            if uid not in expected or row.get("prompt_sha256") != expected[uid]["prompt_sha256"] or row.get("label") != expected[uid]["label"]:
                raise ValueError(f"Validation ID/prompt/label mismatch: {seed}/{dataset}/{uid}")
            observed[uid] = row
        if set(observed) != set(expected):
            raise ValueError(f"Validation ID coverage mismatch: {seed}/{dataset}")
        if run_manifest.get("model_sha256") != MODEL_SHA or run_manifest.get("llama_cpp_python") != "0.3.16":
            raise ValueError(f"Validation runtime/model mismatch: {seed}/{dataset}")
        ordered = [observed[uid] for uid in sorted(observed)]
        tau, validation_mcc, grid = fit(ordered)
        evidence = [{k: r.get(k) for k in ("id", "label", "prompt_sha256", "model_sha256", "seed", "s", "valid")} for r in ordered]
        entries[f"B2-rand/{seed}/{dataset}"] = {
            "arm": "B2-rand", "seed": seed, "dataset": dataset, "split_used": "validation",
            "tau_star": tau, "validation_mcc": validation_mcc, "n_total": expected_n,
            "n_valid": len(ordered), "tie_rule": "within 1e-9: closest to 0.5, then lower tau",
            "validation_prompt_set_sha256": val_manifest["prompts_sha256"],
            "validation_bundle_sha256": sha(frozen_inputs[input_name]),
            "validation_records_sha256": sha(records_bytes),
            "validation_evidence_sha256": canonical_sha(evidence), "grid": grid,
            "model_sha256": MODEL_SHA, "backend": "llama-cpp-python==0.3.16",
            "inference_seed": 4294967295, "inference_seed_policy": "llama_cpp_default",
            "source_run_manifest": run_manifest,
        }
        validation_source[f"{seed}/{dataset}"] = {
            "count": len(records), "records_sha256": sha(records_bytes),
            "bundle_sha256": sha(frozen_inputs[input_name]), "tau_star": tau,
            "validation_mcc": validation_mcc,
        }
        test_name = f"seed_{seed}/{dataset}_test_b2_rand_seed_{seed}_kaggle.zip"
        test_sources[test_name] = frozen_inputs[test_name]

lock_candidate = {
    "schema": "b2_rand_seed_validation_threshold_lock_v1",
    "arm": "B2-rand", "split": "validation", "locked_at_utc": datetime.now(timezone.utc).isoformat(),
    "rules": RULES, "rules_sha256": canonical_sha(RULES), "model_sha256": MODEL_SHA,
    "backend": "llama-cpp-python==0.3.16", "tokenizer": TOKENIZER,
    "tokenizer_revision": TOKENIZER_REV, "quantization": "Q4_K_M", "context_tokens": 8192,
    "seed_policy": "thresholds are independent for each prompt seed and dataset",
    "entries": entries,
}
CONFIG.parent.mkdir(parents=True, exist_ok=True)
if CONFIG.exists():
    lock = json.loads(CONFIG.read_text(encoding="utf-8"))
    for key in ("schema", "arm", "split", "rules", "rules_sha256", "model_sha256", "backend", "tokenizer", "tokenizer_revision", "quantization", "context_tokens", "seed_policy", "entries"):
        if lock.get(key) != lock_candidate.get(key):
            raise ValueError(f"Existing threshold lock is immutable and differs at {key}; do not overwrite it")
    seal = lock.get("locked_sha256")
    if seal != canonical_sha({k: v for k, v in lock.items() if k != "locked_sha256"}):
        raise ValueError("Existing B2-rand threshold lock seal is invalid")
else:
    lock = lock_candidate
    lock["locked_sha256"] = canonical_sha(lock)
    CONFIG.write_bytes(json_bytes(lock))
lock_bytes = json_bytes(lock)

wrapped = {}
bundle_manifest = {
    "schema": "b2_rand_test_bundle_v1", "arm": "B2-rand", "split": "test",
    "threshold_lock_sha256": lock["locked_sha256"], "model_sha256": MODEL_SHA,
    "source_inputs_sha256": sha(SOURCE_BUNDLE.read_bytes()), "seeds": [42, 43],
    "created_at_utc": lock["locked_at_utc"], "members": {},
}
for name, raw in sorted(test_sources.items()):
    prompt_bytes, source_manifest, rows = read_inner(raw)
    seed = int(name.split("/")[0].split("_")[1])
    dataset = "devign" if "/devign_" in name else "reveal"
    lock_entry = entries[f"B2-rand/{seed}/{dataset}"]
    test_manifest = dict(source_manifest)
    test_manifest.update({
        "threshold_lock_sha256": lock["locked_sha256"], "tau_star": lock_entry["tau_star"],
        "threshold_validation_evidence_sha256": lock_entry["validation_evidence_sha256"],
        "source_bundle_sha256": sha(raw), "model_sha256": MODEL_SHA,
        "model_repo": "ggml-org/Qwen3-Coder-30B-A3B-Instruct-GGUF",
        "tokenizer": TOKENIZER, "tokenizer_revision": TOKENIZER_REV,
        "prompt_budget_tokens": 8192,
    })
    # The prompt rows are preserved byte-for-byte; test labels remain outside prompt text.
    inner = zip_bytes({"prompts.jsonl": prompt_bytes, "bundle_manifest.json": json_bytes(test_manifest), "threshold_lock.json": lock_bytes})
    dest_name = f"seed_{seed}/{dataset}_test.zip"
    wrapped[dest_name] = inner
    bundle_manifest["members"][dest_name] = {"sha256": sha(inner), "count": len(rows), "tau_star": lock_entry["tau_star"], "source_bundle_sha256": sha(raw)}
bundle_manifest_bytes = json_bytes(bundle_manifest)
test_bundle_bytes = zip_bytes({**wrapped, "threshold_lock.json": lock_bytes, "delivery_manifest.json": bundle_manifest_bytes})
BUNDLE_PATH = OUT / "grace_b2_rand_test_seeds_42_43_bundle.zip"
BUNDLE_PATH.write_bytes(test_bundle_bytes)
BUNDLE_SHA = sha(test_bundle_bytes)


def notebook_for(seed):
    nb = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    nb["cells"][0]["source"] = (f"""# B2-rand — test seed {seed}, resumable, 9-hour session budget

Upload `grace_b2_rand_test_seeds_42_43_bundle.zip` as a Kaggle Dataset and attach it plus the same pinned GGUF model used for validation. Select GPU T4 x2 and Internet ON.
This notebook runs only B2-rand test for prompt seed {seed}; thresholds are fixed from complete validation for this seed and each dataset. It never reads test labels to fit thresholds.
The 9-hour wall-clock budget starts at the first cell and includes package/CUDA setup. A 5-minute reserve stops new records and exports a per-ID fsynced checkpoint.
To resume after a disconnect, download `{f'grace_b2_rand_seed{seed}_test_checkpoint.zip'}` from the previous Kaggle Output, upload it as a Kaggle Dataset, and attach that dataset. The runner verifies prompt/model/threshold identities and skips completed IDs.
""").splitlines(keepends=True)
    nb["cells"][2]["source"] = f"""import math
ARM = 'B2-rand'
PROMPT_SEED = {seed}
KAGGLE_INPUT_ROOT = Path('/kaggle/input')
BUNDLE_WORK = Path('/kaggle/working/b2_rand_test_bundles')
OUT_ROOT = Path('/kaggle/working/b2_rand_seed{seed}_test')
BUNDLE_NAME = 'grace_b2_rand_test_seeds_42_43_bundle.zip'
BUNDLE_SHA256 = '{BUNDLE_SHA}'
CHECKPOINT_NAME = 'grace_b2_rand_seed{seed}_test_checkpoint.zip'
CHECKPOINT_INPUT_PATH = None
MODEL_FILENAME = '{MODEL_FILE}'
MODEL_SHA256 = '{MODEL_SHA}'
MAX_RUNTIME_HOURS = 9
CHECKPOINT_RESERVE_SECONDS = 300
GPU_LAYERS = -1
THRESHOLD_LOCK_SHA256 = '{lock['locked_sha256']}'
SETS = [
    {{'name':'seed_{seed}/devign_test.zip','sha256':'{sha(wrapped[f'seed_{seed}/devign_test.zip'])}','seed':{seed},'dataset':'devign','count':2732}},
    {{'name':'seed_{seed}/reveal_test.zip','sha256':'{sha(wrapped[f'seed_{seed}/reveal_test.zip'])}','seed':{seed},'dataset':'reveal','count':2274}},
]
""".splitlines(keepends=True)
    nb["cells"][3]["source"] = f"""def hash_bytes(data):
    return hashlib.sha256(data).hexdigest()

BUNDLE_WORK.mkdir(parents=True, exist_ok=True)
OUT_ROOT.mkdir(parents=True, exist_ok=True)
archives = sorted(KAGGLE_INPUT_ROOT.rglob(BUNDLE_NAME))
if len(archives) != 1:
    raise ValueError(f'Expected exactly one {{BUNDLE_NAME}}; found {{archives}}')
if hash_bytes(archives[0].read_bytes()) != BUNDLE_SHA256:
    raise ValueError('Test bundle SHA-256 mismatch')
with zipfile.ZipFile(archives[0]) as outer:
    expected_names = {{s['name'] for s in SETS}}
    all_prompt_members = {{n for n in outer.namelist() if n.endswith('_test.zip') and n.startswith('seed_')}}
    if all_prompt_members != {{f'seed_{{s}}/{{ds}}_test.zip' for s in (42,43) for ds in ('devign','reveal')}}:
        raise ValueError('Unexpected seed/dataset members in common test bundle')
    payloads = {{spec['name']: outer.read(spec['name']) for spec in SETS}}

bundles = {{}}
expected = {{}}
for spec in SETS:
    seed, ds = spec['seed'], spec['dataset']
    raw = payloads[spec['name']]
    if hash_bytes(raw) != spec['sha256']:
        raise ValueError(f'Inner test bundle hash mismatch: {{spec["name"]}}')
    bundle_path = BUNDLE_WORK / Path(spec['name']).name
    bundle_path.write_bytes(raw)
    with zipfile.ZipFile(bundle_path) as inner:
        prompt_bytes = inner.read('prompts.jsonl')
        manifest = json.loads(inner.read('bundle_manifest.json'))
        lock_payload = json.loads(inner.read('threshold_lock.json'))
        seal = lock_payload.get('locked_sha256')
        actual = hash_bytes(json.dumps({{k:v for k,v in lock_payload.items() if k!='locked_sha256'}},sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())
        if seal != actual or seal != THRESHOLD_LOCK_SHA256 or manifest.get('threshold_lock_sha256') != seal:
            raise ValueError('Threshold lock integrity mismatch')
        lock_key = f'B2-rand/{{seed}}/{{ds}}'
        entry = lock_payload['entries'][lock_key]
        if (manifest.get('arm'),manifest.get('seed'),manifest.get('split')) != ('B2-rand',seed,'test'):
            raise ValueError('Wrong test manifest identity')
        if manifest.get('tau_star') != entry['tau_star'] or manifest.get('model_sha256') != MODEL_SHA256:
            raise ValueError('Test bundle threshold/model does not match validation lock')
        if hash_bytes(prompt_bytes) != manifest['prompts_sha256']:
            raise ValueError('Prompt payload hash mismatch')
        rows = [json.loads(line) for line in prompt_bytes.decode('utf-8').splitlines() if line.strip()]
    if len(rows) != spec['count'] or len({{str(r['id']) for r in rows}}) != spec['count']:
        raise ValueError(f'Wrong count or duplicate IDs in {{seed}}/{{ds}}')
    for row in rows:
        if (row.get('arm'),row.get('seed'),row.get('dataset'),row.get('split')) != ('B2-rand',seed,ds,'test'):
            raise ValueError('Wrong prompt row identity')
        if hash_bytes(row['prompt'].encode()) != row['prompt_sha256']:
            raise ValueError('Prompt text hash mismatch')
    bundles[seed,ds] = bundle_path
    expected[seed,ds] = {{str(r['id']):(r['prompt_sha256'],r['label']) for r in rows}}

# Load only the checkpoint from this seed, if one is attached. Its entries are
# copied under the same OUT_ROOT layout and then checked by validate_records().
allowed = {{f'seed_{{PROMPT_SEED}}/{{ds}}/test/{{name}}' for ds in ('devign','reveal') for name in ('records.jsonl','run_manifest.json')}}
if CHECKPOINT_INPUT_PATH is not None:
    checkpoint = Path(CHECKPOINT_INPUT_PATH)
else:
    matches = sorted(KAGGLE_INPUT_ROOT.rglob(CHECKPOINT_NAME))
    if len(matches) > 1: raise ValueError('Multiple seed checkpoints attached; specify CHECKPOINT_INPUT_PATH')
    checkpoint = matches[0] if matches else None
if checkpoint:
    with zipfile.ZipFile(checkpoint) as source:
        names = [n for n in source.namelist() if n in allowed]
        if not any(n.endswith('records.jsonl') for n in names): raise ValueError('Checkpoint has no records for this seed')
        for name in names:
            target = OUT_ROOT / name
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(source.read(name))

def validate_records():
    progress = {{}}
    for (seed,ds), prompts in expected.items():
        folder = OUT_ROOT / f'seed_{{seed}}' / ds / 'test'
        path = folder / 'records.jsonl'
        seen = set()
        if path.exists():
            if not (folder/'run_manifest.json').is_file(): raise ValueError(f'Missing manifest: {{path}}')
            for line in path.read_text(encoding='utf-8').splitlines():
                if not line.strip(): continue
                row = json.loads(line); uid = str(row['id'])
                lock_entry = lock_payload['entries'][f'B2-rand/{{seed}}/{{ds}}']
                if (uid in seen or (row.get('arm'),row.get('seed'),row.get('dataset'),row.get('split'),row.get('model_sha256')) != ('B2-rand',seed,ds,'test',MODEL_SHA256)
                    or prompts.get(uid) != (row.get('prompt_sha256'),row.get('label'))
                    or not math.isfinite(row.get('s',float('nan')))
                    or row.get('threshold_lock_sha256') != THRESHOLD_LOCK_SHA256
                    or row.get('tau') != lock_entry['tau_star']
                    or row.get('pred_tau') != int(row['s'] >= row['tau'])
                    or row.get('inference_seed') != 4294967295):
                    raise ValueError(f'Unexpected checkpoint row: {{uid}}')
                seen.add(uid)
        progress[seed,ds] = len(seen)
    return progress

if (OUT_ROOT/'threshold_lock.json').exists():
    if hash_bytes((OUT_ROOT/'threshold_lock.json').read_bytes()) != hash_bytes(json.dumps(lock_payload,indent=2,ensure_ascii=False).encode()):
        raise ValueError('Existing threshold lock differs from the attached test bundle')
else:
    (OUT_ROOT/'threshold_lock.json').write_text(json.dumps(lock_payload,indent=2,ensure_ascii=False),encoding='utf-8')
""".splitlines(keepends=True)
    nb["cells"][3]["source"] = ''.join(nb["cells"][3]["source"]).replace("%%", "") .splitlines(keepends=True)
    nb["cells"][7]["source"] = ("%%writefile /kaggle/working/kaggle_inference.py\n" + RUNNER.read_text(encoding="utf-8")).splitlines(keepends=True)
    runner = ''.join(nb["cells"][7]["source"])
    runner = runner.replace("EXPECTED_LOCK_SEAL = 'b5dc7e0da070f75cfabc10c366a08675d1c3f471f1e11fb86ee826a22ce674f8'", f"EXPECTED_LOCK_SEAL = '{lock['locked_sha256']}'")
    a = runner.index('def load_bundle(bundle):')
    b = runner.index('\n\ndef evaluate_output(output):', a)
    loader = '''def load_bundle(bundle):
    with zipfile.ZipFile(bundle) as z:
        manifest = json.loads(z.read('bundle_manifest.json'))
        prompt_bytes = z.read('prompts.jsonl')
        lock = json.loads(z.read('threshold_lock.json'))
    seal = lock.get('locked_sha256')
    unsigned = {k:v for k,v in lock.items() if k!='locked_sha256'}
    actual = hashlib.sha256(json.dumps(unsigned,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
    if seal != actual or seal != EXPECTED_LOCK_SEAL or manifest.get('threshold_lock_sha256') != seal:
        raise ValueError('B2-rand validation lock integrity mismatch')
    ds, seed = manifest['dataset'], manifest['seed']
    entry = lock['entries'][f"B2-rand/{seed}/{ds}"]
    if (manifest.get('arm'), manifest.get('split')) != ('B2-rand','test'):
        raise ValueError('Only B2-rand test bundles are accepted')
    if manifest.get('tau_star') != entry['tau_star'] or lock.get('model_sha256') != manifest.get('model_sha256'):
        raise ValueError('Test bundle does not use its locked validation threshold/model')
    if hashlib.sha256(prompt_bytes).hexdigest() != manifest['prompts_sha256']:
        raise ValueError(f'Prompt bundle hash mismatch: {bundle}')
    rows = [json.loads(line) for line in prompt_bytes.decode('utf-8').splitlines() if line.strip()]
    if len(rows) != manifest['count'] or len({str(r['id']) for r in rows}) != len(rows):
        raise ValueError('Prompt count/unique ID mismatch')
    for row in rows:
        if (row.get('arm'),row.get('seed'),row.get('dataset'),row.get('split')) != ('B2-rand',seed,ds,'test'):
            raise ValueError('Wrong test prompt identity')
        if hashlib.sha256(row['prompt'].encode('utf-8')).hexdigest() != row['prompt_sha256']:
            raise ValueError('Test prompt hash mismatch')
    manifest['model_repo'] = 'ggml-org/Qwen3-Coder-30B-A3B-Instruct-GGUF'
    manifest['prompt_budget_tokens'] = 8192
    return manifest, rows
'''
    runner = runner[:a] + loader + runner[b:]
    runner = runner.replace("if arm != 'B1-H2' or prompt_seed != 42 or limit is not None or not runs or any(r[1] != 'test' for r in runs):\n        raise ValueError('Only the complete B1-H2 test census is allowed')", f"if arm != 'B2-rand' or prompt_seed != {seed} or limit is not None or len(runs) != 2 or any(r[1] != 'test' for r in runs):\n        raise ValueError('Only complete B2-rand test census for prompt seed {seed} is allowed')")
    runner = runner.replace("n_gpu_layers=gpu_layers, split_mode=llama_cpp.LLAMA_SPLIT_MODE_LAYER, tensor_split=[1.0, 1.0],\n                logits_all=True, seed=inference_seed, verbose=True)", "n_gpu_layers=gpu_layers, logits_all=True, verbose=True)")
    runner = runner.replace("'n_batch': 256, 'tensor_split': [1.0,1.0], 'split_mode': 'layer'", "'n_batch': 256")
    runner = runner.replace("('B1-H2', 42, dataset, split)", f"('B2-rand', {seed}, dataset, split)")
    runner = runner.replace("('B1-H2', 42, prompt_seed", f"('B2-rand', {seed}, prompt_seed")
    runner = runner.replace("('B1-H2', 42, ds, 'test')", f"('B2-rand', {seed}, ds, 'test')")
    runner = runner.replace("if arm != 'B1-H2'", "if arm != 'B2-rand'")
    runner = runner.replace("'B1-H2'", "'B2-rand'")
    # Enforce only the per-notebook prompt seed at the CLI and in the embedded runner.
    if f"prompt_seed != {seed}" not in runner:
        raise ValueError("Test runner seed gate replacement failed")
    nb["cells"][7]["source"] = runner.splitlines(keepends=True)
    cell8 = ''.join(nb["cells"][8]["source"])
    cell8 = cell8.replace("{'devign':0.09,'reveal':0.21}", "{ds: json.loads(zipfile.ZipFile(bundles[PROMPT_SEED, ds]).read('threshold_lock.json'))['entries'][f'B2-rand/{PROMPT_SEED}/{ds}']['tau_star'] for ds in ('devign','reveal')}")
    cell8 = cell8.replace("'B1-H2'", "'B2-rand'").replace("for seed in sorted({seed for seed, ds in bundles})", "for seed in (PROMPT_SEED,)")
    cell8 = cell8.replace("CHECKPOINT_NAME.removesuffix('.zip')", "CHECKPOINT_NAME.removesuffix('.zip')")
    nb["cells"][8]["source"] = cell8.splitlines(keepends=True)
    from fix_test_input_discovery import patch_notebook
    nb = patch_notebook(nb)
    from integrate_test_runtime_lock import integrate
    nb = integrate(nb)
    # Kaggle code settings and clean execution outputs for a new kernel version.
    nb["metadata"].setdefault("kaggle", {})
    nb["metadata"]["kaggle"].update({"accelerator":"nvidiaTeslaT4", "isGpuEnabled":True, "isInternetEnabled":True, "dataSources":[], "sourceType":"notebook", "language":"python"})
    nb["metadata"]["language_info"]["version"] = "3.13.15"
    nb["metadata"].pop("papermill", None)
    for index, cell in enumerate(nb["cells"]):
        cell["metadata"] = {}
        if cell["cell_type"] == "code":
            cell["execution_count"] = None
            cell["outputs"] = []
            code = ''.join(cell["source"])
            if code.startswith("%%writefile "):
                code = code.split("\n", 1)[1]
            compile(code, f"cell_{index}", "exec")
    path = OUT / f"02_kaggle_qwen_q4_b2_rand_seed{seed}_test.ipynb"
    path.write_bytes((json.dumps(nb, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    return path


notebooks = [notebook_for(seed) for seed in (42, 43)]
resume_paths = [
    ROOT / "06_Arm_B2_Rand/notebooks/02_kaggle_qwen_q4_b2_rand.ipynb",
    ROOT / "Runs-management/kaggle_validation_6arms_20261104/02_kaggle_qwen_q4_b2_rand.ipynb",
]
resume_note = """# B2-rand — tiếp tục validation từ output mới nhất

Add Input `grace_b2_rand_inputs.zip`, GGUF Q4_K_M đã pin, và **checkpoint mới nhất** `grace_b2_rand_checkpoint.zip` từ phiên I-12. Output đã kiểm tra tại `Runs-management/kaggle_outputs_20261107/b2_rand_latest/`; SHA-256 checkpoint: `CHECKPOINT_SHA`.

I-12 đã đủ validation cho seed 42 và 43 (mỗi seed 5.005/5.005). Seed 44 có Devign 2.426/2.732; ReVeal 0/2.273. Tổng lũy kế **12.436/15.015**, còn **2.579**: seed 44 Devign 306 và ReVeal 2.273.

Notebook tự nhận checkpoint I-12 hoặc hậu duệ có nguyên prefix I-11, bỏ qua ID đã hoàn tất và chỉ chạy validation. Giới hạn 9 giờ gồm cả setup/model load. Khi hết phiên, tải checkpoint mới từ Output và dùng nó để resume. Notebook dừng khi validation đủ; không tự fit ngưỡng và không chạy test.
""".replace("CHECKPOINT_SHA", sha(OUTPUTS.read_bytes()))
for resume_path in resume_paths:
    resume_nb = json.loads(resume_path.read_text(encoding="utf-8"))
    resume_nb["cells"][0]["source"] = resume_note.splitlines(keepends=True)
    resume_nb.setdefault("metadata", {}).setdefault("kaggle", {}).update({"accelerator":"nvidiaTeslaT4", "isGpuEnabled":True})
    resume_path.write_bytes((json.dumps(resume_nb, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
manifest = {
    "schema":"b2_rand_test_delivery_v1", "created_at_utc":lock["locked_at_utc"],
    "source_inputs_sha256":sha(SOURCE_BUNDLE.read_bytes()), "source_checkpoint_sha256":sha(OUTPUTS.read_bytes()),
    "threshold_config":"06_Arm_B2_Rand/config/threshold.json", "threshold_lock_sha256":lock["locked_sha256"],
    "validation_sources":validation_source, "bundle":"06_Arm_B2_Rand/test_delivery_20261107/grace_b2_rand_test_seeds_42_43_bundle.zip",
    "bundle_sha256":BUNDLE_SHA,
    "notebooks":{p.name:sha(p.read_bytes()) for p in notebooks},
    "resume_notebooks":{p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in resume_paths},
    "expected_test_rows":{"42/devign":2732,"42/reveal":2274,"43/devign":2732,"43/reveal":2274},
}
(OUT/"delivery_manifest.json").write_bytes(json_bytes(manifest))
print(json.dumps({"threshold_lock_sha256":lock["locked_sha256"],"entries":{k:{"tau_star":v["tau_star"],"validation_mcc":v["validation_mcc"],"n_total":v["n_total"]} for k,v in entries.items()},"bundle_sha256":BUNDLE_SHA,"notebooks":manifest["notebooks"]},indent=2))
