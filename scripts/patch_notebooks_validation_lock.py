"""Patch Kaggle inference notebooks to embed validation_lock helper and test gate."""
import json
import ast
from pathlib import Path

root = Path(__file__).resolve().parents[1]
core = (root / 'Runs-management/validation_lock.py').read_text(encoding='utf-8').strip()

def patch_notebook(rel_path, arm_name):
    nb_path = root / rel_path
    if not nb_path.exists():
        print(f"Skipping {rel_path} (not found)")
        return
    d = json.loads(nb_path.read_text(encoding='utf-8'))

    helper_cell = {
        'cell_type': 'code',
        'execution_count': None,
        'id': 'validation-threshold-helper',
        'metadata': {},
        'outputs': [],
        'source': ['%%writefile /kaggle/working/validation_lock.py\n'] + [line + '\n' for line in core.splitlines()]
    }

    # Find helper cell if it already exists
    cell_idx = next((i for i, c in enumerate(d['cells']) if c.get('id') == 'validation-threshold-helper'), None)
    
    # Find kaggle script cell
    k_idx = next(i for i, c in enumerate(d['cells']) if ''.join(c.get('source', [])).startswith('%%writefile /kaggle/working/kaggle_'))
    
    if cell_idx is not None:
        d['cells'][cell_idx] = helper_cell
    else:
        d['cells'].insert(k_idx, helper_cell)
        k_idx += 1

    src = ''.join(d['cells'][k_idx]['source'])

    # 1. Add imports if not present
    if 'from validation_lock import' not in src:
        import_target = '\nimport numpy as np\n'
        import_replacement = (
            "\nimport numpy as np\n\n"
            "# Shared validation-only analysis; helper is embedded by the Kaggle notebook.\n"
            "import sys\n"
            "if str(Path(__file__).resolve().parent.parent / 'Runs-management') not in sys.path:\n"
            "    sys.path.insert(0,str(Path(__file__).resolve().parent.parent / 'Runs-management'))\n"
            "from validation_lock import make_lock,persist_lock,require_test_lock,evaluate_at_locked_threshold,read_jsonl,file_sha256\n"
        )
        src = src.replace(import_target, import_replacement, 1)

    # 2. Update run_batch signature and thresholds_path
    if 'thresholds_path=None' not in src:
        sig_old = 'checkpoint_reserve_seconds, status_path):'
        sig_new = (
            'checkpoint_reserve_seconds, status_path, thresholds_path=None):\n'
            '    thresholds_path = Path(thresholds_path) if thresholds_path else Path(status_path).parent / "thresholds.json"'
        )
        src = src.replace(sig_old, sig_new)

    # 3. Add test gate before identity_file
    if 'require_test_lock(thresholds_path' not in src:
        gate_target = "        identity_file = out / 'run_manifest.json'"
        gate_replacement = (
            "        locked_threshold = None\n"
            "        if split == 'test':\n"
            "            val_hash = None\n"
            "            for vd,vs,vb,vo in runs:\n"
            "                if vd == dataset and vs == 'validation':\n"
            "                    val_hash = load_bundle(vb)[0]['prompts_sha256']\n"
            "                    break\n"
            f"            locked_threshold = require_test_lock(thresholds_path,'{arm_name}',dataset,identity,val_hash)\n"
            "            print(f'Test threshold locked: {dataset} tau={locked_threshold[\"tau\"]}',flush=True)\n"
            "        identity_file = out / 'run_manifest.json'"
        )
        src = src.replace(gate_target, gate_replacement)

    # 4. Add validation lock
    if "if split == 'validation' and limit is None:" not in src:
        val_target = "        metrics = evaluate_output(output)"
        val_replacement = (
            "        if split == 'validation' and limit is None:\n"
            f"            locked_threshold = persist_lock(thresholds_path,make_lock(rows,list(done.values()),'{arm_name}',dataset,identity,\n"
            "                manifest['prompts_sha256'],[{'path':str(output),'records_sha256':file_sha256(output)}]))\n"
            "            write_json_atomic(out/'threshold_lock.json',locked_threshold)\n"
            "            print(f'Validation threshold auto-locked: {dataset} tau={locked_threshold[\"tau\"]}',flush=True)\n"
            "        metrics = evaluate_output(output)\n"
            "        if locked_threshold is not None:\n"
            "            metrics['score_threshold_validation_locked'] = evaluate_at_locked_threshold(list(done.values()),locked_threshold)"
        )
        src = src.replace(val_target, val_replacement)

    # 5. Add CLI argument
    if '--thresholds' not in src:
        cli_old = "    ap.add_argument('--model', required=True)"
        cli_new = (
            "    ap.add_argument('--thresholds', help='Defaults to thresholds.json beside checkpoint_status.json')\n"
            "    ap.add_argument('--model', required=True)"
        )
        src = src.replace(cli_old, cli_new)
        call_old = "args.deadline_epoch, args.checkpoint_reserve_seconds, args.status)"
        call_new = "args.deadline_epoch, args.checkpoint_reserve_seconds, args.status, args.thresholds)"
        src = src.replace(call_old, call_new)

    # Verify AST
    code_to_parse = src.split('\n', 1)[1]
    ast.parse(code_to_parse)

    # Update cell source
    d['cells'][k_idx]['source'] = [l + '\n' for l in src.splitlines()]
    if not d['cells'][k_idx]['source'][-1].endswith('\n'):
        d['cells'][k_idx]['source'][-1] += '\n'

    nb_path.write_text(json.dumps(d, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f"Patched {rel_path} successfully!")

if __name__ == '__main__':
    patch_notebook('01_Author_Baseline_Unified/notebooks/02_kaggle_qwen_q4_b2.ipynb', 'B2')
    patch_notebook('03_Arm_B1_Graph_Only/notebooks/02_kaggle_qwen_q4_b1.ipynb', 'B1')
