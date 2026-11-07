import sys
import json
from pathlib import Path

lock_path = Path('configs/inference_runtime_lock.json')
if not lock_path.exists():
    print("Lock file not found!")
    sys.exit(1)

lock = json.loads(lock_path.read_text(encoding='utf-8'))

expected_pkgs = lock.get('packages', {})
expected_model = lock.get('model', {})
expected_tok = lock.get('tokenizer', {})
expected_cons = lock.get('constructor', {})

print("=" * 80)
print("INFERENCE RUNTIME LOCK SPECIFICATION:")
print(f"Contract ID: {lock.get('contract_id')}")
print(f"Inference Seed: {lock.get('user_decisions', {}).get('inference_seed')}")
print("Required Packages:")
for p_name, p_ver in expected_pkgs.items():
    print(f"  - {p_name}=={p_ver}")
print(f"Model GGUF SHA-256: {expected_model.get('sha256')}")
print(f"Tokenizer Revision: {expected_tok.get('revision')}")
print(f"Constructor: n_ctx={expected_cons.get('n_ctx')}, n_batch={expected_cons.get('n_batch')}, n_ubatch={expected_cons.get('n_ubatch')}, seed={expected_cons.get('seed')}, tensor_split={expected_cons.get('tensor_split')}")
print("=" * 80)

notebooks_to_check = [
    # Group 2 test notebooks
    ("Test: B2-rep", Path("05_Arm_B2_Rep/notebooks/02_kaggle_qwen_q4_b2_rep_test.ipynb")),
    ("Test: B1-full", Path("09_Arm_B1_Full/notebooks/02_kaggle_qwen_q4_b1_full_test.ipynb")),
    ("Test: B2-nolabel", Path("10_Arm_B2_NoLabel/notebooks/02_kaggle_qwen_q4_b2_nolabel_test.ipynb")),
    ("Test: B2-labelonly", Path("12_Arm_B2_LabelOnly/notebooks/02_kaggle_qwen_q4_b2_labelonly_test.ipynb")),
    # B3 validation notebook
    ("Val: B3 Amended", Path("13_Arm_B3_Contrastive/notebooks/02_kaggle_qwen_q4_b3_amended_validation.ipynb")),
    # Also check B2-rand test notebooks if present
    ("Test: B2-rand s42", Path("06_Arm_B2_Rand/test_delivery_20261107/02_kaggle_qwen_q4_b2_rand_seed42_test.ipynb")),
    ("Test: B2-rand s43", Path("06_Arm_B2_Rand/test_delivery_20261107/02_kaggle_qwen_q4_b2_rand_seed43_test.ipynb")),
]

results = []

for label, p in notebooks_to_check:
    print(f"\nAUDITING: [{label}] -> {p}")
    if not p.exists():
        print("  FILE NOT FOUND!")
        continue
    
    nb = json.loads(p.read_text(encoding='utf-8'))
    cells_src = []
    for c in nb.get('cells', []):
        cells_src.append("".join(c.get('source', [])))
    full_text = "\n".join(cells_src)
    
    # 1. Package checks
    pkg_status = {}
    for p_name, p_ver in expected_pkgs.items():
        req_hyphen = f"{p_name}=={p_ver}"
        req_underscore = f"{p_name.replace('-', '_')}=={p_ver}"
        found = req_hyphen in full_text or req_underscore in full_text
        pkg_status[p_name] = (found, p_ver)
    
    # 2. Model & Tokenizer checks
    model_sha = expected_model.get('sha256')
    model_sha_found = model_sha in full_text
    
    tok_rev = expected_tok.get('revision')
    tok_rev_found = tok_rev in full_text
    
    # 3. Constructor params
    seed_val = str(expected_cons.get('seed'))
    seed_found = f"seed={seed_val}" in full_text or f"'seed': {seed_val}" in full_text or f'"seed": {seed_val}' in full_text or seed_val in full_text
    
    n_ctx_found = "8192" in full_text
    n_batch_found = "256" in full_text
    
    print("  Package pins:")
    all_pkgs_ok = True
    for p_name, (ok, ver) in pkg_status.items():
        print(f"    - {p_name}=={ver}: {'MATCH' if ok else 'MISSING'}")
        if not ok:
            all_pkgs_ok = False
            
    print(f"  Model SHA-256 ({model_sha[:10]}...): {'MATCH' if model_sha_found else 'MISMATCH'}")
    print(f"  Tokenizer Revision ({tok_rev[:10]}...): {'MATCH' if tok_rev_found else 'MISMATCH'}")
    print(f"  Seed {seed_val}: {'MATCH' if seed_found else 'MISMATCH'}")
    print(f"  n_ctx 8192: {'MATCH' if n_ctx_found else 'MISMATCH'}")
    print(f"  n_batch 256: {'MATCH' if n_batch_found else 'MISMATCH'}")
    
    results.append({
        "label": label,
        "path": str(p),
        "all_pkgs_ok": all_pkgs_ok,
        "model_sha_ok": model_sha_found,
        "tok_rev_ok": tok_rev_found,
        "seed_ok": seed_found,
        "n_ctx_ok": n_ctx_found,
        "n_batch_ok": n_batch_found,
    })

print("\n" + "=" * 80)
print("AUDIT SUMMARY:")
for r in results:
    status = "OK" if all([r['all_pkgs_ok'], r['model_sha_ok'], r['tok_rev_ok'], r['seed_ok'], r['n_ctx_ok'], r['n_batch_ok']]) else "HAS DIFFERENCES"
    print(f"  {r['label']:<20}: {status}")
