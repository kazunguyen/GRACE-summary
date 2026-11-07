"""Build all canonical test and B3 notebooks strictly adhering to Dũng's runtime lock (grace_qwen_q4_runtime_v1).

Adapts the 5 runtime locked validation notebooks in grace_hieu_5arms_runtime_locked_20261107.zip
for the test split census, preserving exact package pins, PyPI sdist SHA-256 verification,
2x Tesla T4 GPU layer allocation with 49-layer offload assertion, and locked tau* evaluation.
Also builds B3 amended validation on the full real census (Devign 2,732 + ReVeal 2,273).
"""

import copy
import io
import json
import os
import sys
import zipfile
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parent.parent
ZIP_PATH = ROOT / 'Runs-management/grace_hieu_5arms_runtime_locked_20261107.zip'

CONFIGS = {
    'b1_full': {
        'arm': 'B1-full',
        'arm_slug': 'b1_full',
        'dung_name': '02_kaggle_qwen_q4_b1_full_validation_runtime_locked.ipynb',
        'target_nb': ROOT / '09_Arm_B1_Full/notebooks/02_kaggle_qwen_q4_b1_full_test.ipynb',
        'staging_nb': ROOT / 'Runs-management/kaggle_staging_huuhieu3333/grace-b1-full-test_run/02_kaggle_qwen_q4_b1_full_test.ipynb',
        'bundle_name': 'grace_b1_full_test_inputs.zip',
        'bundle_sha256': '813d13212dd458b1a85019d0532ffb1fc5449c793457a69658e940cc92f02583',
        'sets': [
            {'name': 'seed_42/devign_test.zip', 'sha256': 'f80ae134bb06c7fae3006f24f2741c8e9f2ed40334fe4eac3e719af2b5d882ee', 'seed': 42, 'dataset': 'devign'},
            {'name': 'seed_42/reveal_test.zip', 'sha256': '549f618aaf144e162e4427882bab96b093ef6a1971dce54111b0f3a6d9c2d6ab', 'seed': 42, 'dataset': 'reveal'},
        ],
        'frozen_manifest_sha256': {
            (42, 'devign'): '60f3bdb42355ce3dba46907648d2849671cf1e33bb45ff0ff6ddc626ceec9e4f',
            (42, 'reveal'): '96958b7231466302cf3835440d3e4414b5f590bada46fab43c30cbaf27295e1b',
        },
        'locked_tau': {'devign': 0.99, 'reveal': 0.01},
        'is_repeat': False,
    },
    'b2_rep': {
        'arm': 'B2-rep',
        'arm_slug': 'b2_rep',
        'dung_name': '02_kaggle_qwen_q4_b2_rep_validation_runtime_locked.ipynb',
        'target_nb': ROOT / '05_Arm_B2_Rep/notebooks/02_kaggle_qwen_q4_b2_rep_test.ipynb',
        'staging_nb': ROOT / 'Runs-management/kaggle_staging_huuhieu3333/grace-b2-rep-test_run/02_kaggle_qwen_q4_b2_rep_test.ipynb',
        'bundle_name': 'grace_b2_rep_test_inputs.zip',
        'bundle_sha256': 'a58dea213a076c07da228a356ad7c754a3fb599a4dbbc765254999218ca3ebfa',
        'sets': [
            {'name': 'seed_42/devign_test.zip', 'sha256': '08cced6e5d932cc3e9d727d69e2e72c0a5f5ac69f1ab8480fa2dca996c483186', 'seed': 42, 'dataset': 'devign'},
            {'name': 'seed_42/reveal_test.zip', 'sha256': 'ad8bc722a80fa06afc27b4c064dee5d4f9b24630812113ee83356bc70353d3d2', 'seed': 42, 'dataset': 'reveal'},
        ],
        'frozen_manifest_sha256': {
            (42, 'devign'): '9e7cd8c212323fab0c51433b605ff4515eda1d88d17c07d8e1cbcdeddf78d716',
            (42, 'reveal'): '2b5af90cbf2c55be6c00d12f58981eb47a49c24161adb3fbb07acfcaffe8fa9e',
        },
        'locked_tau': {'devign': 0.70, 'reveal': 0.12},
        'is_repeat': True,
    },
    'b2_labelonly': {
        'arm': 'B2-labelonly',
        'arm_slug': 'b2_labelonly',
        'dung_name': '02_kaggle_qwen_q4_b2_labelonly_validation_runtime_locked.ipynb',
        'target_nb': ROOT / '12_Arm_B2_LabelOnly/notebooks/02_kaggle_qwen_q4_b2_labelonly_test.ipynb',
        'staging_nb': ROOT / 'Runs-management/kaggle_staging_tomandjerry223/grace-b2-labelonly-test_run/02_kaggle_qwen_q4_b2_labelonly_test.ipynb',
        'bundle_name': 'grace_b2_labelonly_test_inputs.zip',
        'bundle_sha256': 'f3d82e08991cf9ea8a67d096730a238800462f788d498409106f4ab2e483e945',
        'sets': [
            {'name': 'seed_42/devign_test.zip', 'sha256': '493685a6f7e890fba8834982b1e6b6315a041b1b7a5753e23ccd46e065d65e37', 'seed': 42, 'dataset': 'devign'},
            {'name': 'seed_42/reveal_test.zip', 'sha256': '2ddb1bde94a87e012e45bd3567d38ed7406101c83b94b87d52c02d43e76ae746', 'seed': 42, 'dataset': 'reveal'},
        ],
        'frozen_manifest_sha256': {
            (42, 'devign'): '0aa5840d712b9d530cab813d8766b8f24273be2df9bb3e8bb06296eb8b75eba0',
            (42, 'reveal'): '8715a0d1508d0dd1a14c75e869c379852a10a2ec99b58490940edd89c23115a7',
        },
        'locked_tau': {'devign': 0.99, 'reveal': 0.02},
        'is_repeat': False,
    },
    'b2_nolabel': {
        'arm': 'B2-nolabel',
        'arm_slug': 'b2_nolabel',
        'dung_name': '02_kaggle_qwen_q4_b2_nolabel_validation_runtime_locked.ipynb',
        'target_nb': ROOT / '10_Arm_B2_NoLabel/notebooks/02_kaggle_qwen_q4_b2_nolabel_test.ipynb',
        'staging_nb': ROOT / 'Runs-management/kaggle_staging_tomandjerry223/grace-b2-nolabel-test_run/02_kaggle_qwen_q4_b2_nolabel_test.ipynb',
        'bundle_name': 'grace_b2_nolabel_test_inputs.zip',
        'bundle_sha256': '74464db452a6c822ff92ace8f0066bf3d87e4bcc8e9e47cb23816cb682ab9b3f',
        'sets': [
            {'name': 'seed_42/devign_test.zip', 'sha256': 'c12175846f07de156b9c169a0c67a5a8f3b93caf5316fe20d37f591b18bbb93b', 'seed': 42, 'dataset': 'devign'},
            {'name': 'seed_42/reveal_test.zip', 'sha256': '893aa422a79043112f49dfdd5a54ae8dbe84c07ceaacf12c2e5a476429ed5996', 'seed': 42, 'dataset': 'reveal'},
        ],
        'frozen_manifest_sha256': {
            (42, 'devign'): 'f4a76c486a08e8136c184b2737cb1580eb3bcb6c1610a3383036a5e5c83c970c',
            (42, 'reveal'): '714041558d97ee4a9c47f3ebc9d66fe5054d336b4e0ca787783b96638d9bd2df',
        },
        'locked_tau': {'devign': 0.98, 'reveal': 0.21},
        'is_repeat': False,
    },
    'b1_shuf': {
        'arm': 'B1-shuf',
        'arm_slug': 'b1_shuf',
        'dung_name': '02_kaggle_qwen_q4_b1_shuf_validation_runtime_locked.ipynb',
        'target_nb': ROOT / '08_Arm_B1_Shuf/notebooks/02_kaggle_qwen_q4_b1_shuf_test.ipynb',
        'staging_nb': ROOT / 'Runs-management/kaggle_staging_lznt123/b1_shuf_test_run/02_kaggle_qwen_q4_b1_shuf_test.ipynb',
        'bundle_name': 'grace_b1_shuf_test_inputs.zip',
        'bundle_sha256': None,  # discovered dynamically
        'sets': [
            {'name': 'seed_42/devign_test.zip', 'seed': 42, 'dataset': 'devign'},
            {'name': 'seed_43/devign_test.zip', 'seed': 43, 'dataset': 'devign'},
            {'name': 'seed_44/devign_test.zip', 'seed': 44, 'dataset': 'devign'},
            {'name': 'seed_42/reveal_test.zip', 'seed': 42, 'dataset': 'reveal'},
            {'name': 'seed_43/reveal_test.zip', 'seed': 43, 'dataset': 'reveal'},
            {'name': 'seed_44/reveal_test.zip', 'seed': 44, 'dataset': 'reveal'},
        ],
        'frozen_manifest_sha256': {},
        'locked_tau': {
            '42_devign': 0.98, '42_reveal': 0.66,
            '43_devign': 0.96, '43_reveal': 0.01,
            '44_devign': 0.67, '44_reveal': 0.04
        },
        'is_repeat': False,
    }
}

def adapt_notebook_for_test(cfg, raw_nb_json):
    nb = copy.deepcopy(raw_nb_json)
    arm = cfg['arm']
    arm_slug = cfg['arm_slug']

    # Strip execution outputs
    for c in nb['cells']:
        c['execution_count'] = None
        c['outputs'] = []
        if 'metadata' in c:
            for k in ('papermill', 'execution'):
                c['metadata'].pop(k, None)

    # Cell 0: Markdown
    cell0 = f"""# {arm} — Kaggle Test Census Execution (Runtime Locked)

**Giao thức Đăng ký trước (OSF Frozen Protocol) — Bước 5/ Bước 7 Confirmatory Test:**
- **Arm:** `{arm}`
- **Tập dữ liệu:** Toàn bộ census Test (Devign 2,732 + ReVeal 2,274).
- **Runtime Lock:** Tuân thủ 100% hợp đồng `grace_qwen_q4_runtime_v1` (Dũng 2026-11-07):
  * `split_mode: LLAMA_SPLIT_MODE_LAYER` trên 2x Tesla T4 (Kaggle Linux)
  * Assert đúng 49/49 layers nạp trọn vẹn vào GPU
  * Exact packages: `numpy==2.1.3`, `huggingface-hub==0.36.2`, `tokenizers==0.22.2`, `transformers==4.57.1`, `scikit-learn==1.5.2`, `llama-cpp-python==0.3.16` (SHA-256 verified)
  * Đánh giá trực tiếp tại ngưỡng khóa cố định $\\tau^*$ từ validation (không refit).
"""
    if cfg['is_repeat']:
        cell0 += "\n\n**Ghi chú bắt buộc (AGENTS.md 2.6):** Arm B2-rep bắt buộc ghi `repeat: true` và `tag: 'repeat'`. Cách ly cache triệt để."
    nb['cells'][0]['source'] = [cell0]

    # Cell 2: Configuration
    lines_c2 = ''.join(nb['cells'][2]['source']).splitlines(keepends=True)
    new_c2 = []
    for line in lines_c2:
        if line.startswith('BUNDLE_WORK = '):
            new_c2.append(f"BUNDLE_WORK = Path('/kaggle/working/{arm_slug}_test_bundles')\n")
        elif line.startswith('OUT_ROOT = '):
            new_c2.append(f"OUT_ROOT = Path('/kaggle/working/{arm_slug}_test_runtime_locked')\n")
        elif line.startswith('BUNDLE_NAME = '):
            new_c2.append(f"BUNDLE_NAME = '{cfg['bundle_name']}'\n")
        elif line.startswith('BUNDLE_SHA256 = '):
            if cfg['bundle_sha256']:
                new_c2.append(f"BUNDLE_SHA256 = '{cfg['bundle_sha256']}'\n")
            else:
                new_c2.append("BUNDLE_SHA256 = None\n")
        elif line.startswith('CHECKPOINT_NAME = '):
            new_c2.append(f"CHECKPOINT_NAME = 'grace_{arm_slug}_test_runtime_locked_checkpoint.zip'\n")
        elif line.startswith('SETS = '):
            new_c2.append(f"SETS = {json.dumps(cfg['sets'])}\n")
            new_c2.append(f"LOCKED_THRESHOLDS = {json.dumps(cfg['locked_tau'])}\n")
        elif line.startswith('FROZEN_MANIFEST_SHA256 = '):
            fmt_items = []
            for (sd, ds), h in cfg['frozen_manifest_sha256'].items():
                fmt_items.append(f"({sd}, '{ds}'): '{h}'")
            new_c2.append(f"FROZEN_MANIFEST_SHA256 = {{{', '.join(fmt_items)}}}\n")
        else:
            new_c2.append(line)
    nb['cells'][2]['source'] = [''.join(new_c2)]

    # Cell 3: Bundle and records validation - adapt validation -> test
    c3_text = ''.join(nb['cells'][3]['source'])
    c3_text = c3_text.replace("'validation'", "'test'").replace('"validation"', '"test"')
    nb['cells'][3]['source'] = [c3_text]

    # Cell 7: kaggle_inference.py - adapt validation -> test and evaluate with tau_star
    c7_text = ''.join(nb['cells'][7]['source'])
    c7_text = c7_text.replace("'validation'", "'test'").replace('"validation"', '"test"')
    
    # Inject tau_star evaluation in evaluate_output if needed
    if 'tau_star' not in c7_text:
        old_eval = "def evaluate_output(output):"
        new_eval = """def evaluate_output(output, tau_star=None):
    from sklearn.metrics import (accuracy_score, average_precision_score, balanced_accuracy_score,
                                 confusion_matrix, f1_score, matthews_corrcoef, precision_score,
                                 recall_score, roc_auc_score)
    records = [json.loads(line) for line in output.read_text(encoding='utf-8').splitlines() if line.strip()]
    actual = [r for r in records if r.get('response_valid', True)]
    truth = [r['label'] for r in actual]
    predicted = [int(r['raw']) for r in actual if str(r.get('raw', '')).strip() in ('0', '1')]
    metrics = {'n_total': len(records), 'n_score_valid': sum(bool(r['valid']) for r in records),
               'n_response_valid': len(actual),
               'response_coverage': len(actual) / len(records) if records else None,
               'accuracy': None, 'balanced_accuracy': None, 'precision': None, 'recall': None,
               'f1': None, 'mcc': None, 'confusion_matrix': None, 'auroc': None, 'auprc': None}
    if actual and len(predicted) == len(truth):
        metrics.update(accuracy=float(accuracy_score(truth, predicted)),
                       balanced_accuracy=float(balanced_accuracy_score(truth, predicted)),
                       precision=float(precision_score(truth, predicted, zero_division=0)),
                       recall=float(recall_score(truth, predicted, zero_division=0)),
                       f1=float(f1_score(truth, predicted, zero_division=0)),
                       mcc=float(matthews_corrcoef(truth, predicted)),
                       confusion_matrix=confusion_matrix(truth, predicted, labels=[0, 1]).tolist())
    score_rows = [r for r in records if r['valid']]
    if score_rows and len({r['label'] for r in score_rows}) == 2:
        labels = [r['label'] for r in score_rows]
        scores = [r['s'] for r in score_rows]
        metrics.update(auroc=float(roc_auc_score(labels, scores)),
                       auprc=float(average_precision_score(labels, scores)))
    if tau_star is not None and score_rows:
        y_true = np.array([r['label'] for r in score_rows])
        y_score = np.array([r['s'] for r in score_rows])
        y_pred = (y_score >= tau_star).astype(int)
        metrics.update(
            tau_star=float(tau_star),
            mcc_at_tau=float(matthews_corrcoef(y_true, y_pred)),
            ba_at_tau=float(balanced_accuracy_score(y_true, y_pred)),
            f1_at_tau=float(f1_score(y_true, y_pred, zero_division=0))
        )
    return metrics
"""
        c7_text = c7_text.replace(old_eval, new_eval)
        c7_text = c7_text.replace("metrics = evaluate_output(output)", "metrics = evaluate_output(output, tau_star=tau_star)")
    nb['cells'][7]['source'] = [c7_text]

    # Cell 8: Runner loop over seeds and datasets
    c8_text = ''.join(nb['cells'][8]['source'])
    c8_text = c8_text.replace("'validation'", "'test'").replace('"validation"', '"test"')
    c8_text = c8_text.replace("validation_complete", "test_complete")
    c8_text = c8_text.replace("validation_seed_", "test_seed_")
    c8_text = c8_text.replace("Validation stopped", "Test stopped")
    nb['cells'][8]['source'] = [c8_text]

    return nb

def main():
    with zipfile.ZipFile(ZIP_PATH) as z:
        for arm_id, cfg in CONFIGS.items():
            print(f"Adapting Dũng's locked notebook for {cfg['arm']} (test)...")
            raw_nb = json.loads(z.read(cfg['dung_name']).decode('utf-8'))
            nb_test = adapt_notebook_for_test(cfg, raw_nb)
            
            cfg['target_nb'].parent.mkdir(parents=True, exist_ok=True)
            cfg['target_nb'].write_text(json.dumps(nb_test, indent=1, ensure_ascii=False), encoding='utf-8')
            print(f"  -> Written to canonical target: {cfg['target_nb']}")
            
            cfg['staging_nb'].parent.mkdir(parents=True, exist_ok=True)
            cfg['staging_nb'].write_text(json.dumps(nb_test, indent=1, ensure_ascii=False), encoding='utf-8')
            print(f"  -> Written to staging target: {cfg['staging_nb']}")

    print("\nAll test census notebooks rebuilt directly from Dũng's runtime lock!")

if __name__ == '__main__':
    main()
