import json
from pathlib import Path

targets = [
    '13_Arm_B3_Contrastive/notebooks/02_kaggle_qwen_q4_b3_validation.ipynb',
    '14_Arm_B3_NoDiff/notebooks/02_kaggle_qwen_q4_b3_nodiff_validation.ipynb',
    'Runs-management/kaggle_staging_lznt123/b3_validation_run/02_kaggle_qwen_q4_b3_validation.ipynb',
    'Runs-management/kaggle_staging_lznt123/b3_nodiff_validation_run/02_kaggle_qwen_q4_b3_nodiff_validation.ipynb',
    'Runs-management/kaggle_staging_huuhieu/b3_nodiff_validation_run/02_kaggle_qwen_q4_b3_nodiff_validation.ipynb',
    'Runs-management/kaggle_staging_thanhduy/b3_validation_run/02_kaggle_qwen_q4_b3_validation.ipynb'
]

pattern = "is_inference = name.startswith('validation_') or name.startswith('resume_seed_')"
replacement = "is_inference = name.startswith('resume_seed_')"

for t in targets:
    p = Path(t)
    if not p.exists():
        print(f"Skipping non-existent: {t}")
        continue
    nb = json.loads(p.read_text(encoding='utf-8'))
    modified = False
    for cell in nb.get('cells', []):
        src = cell.get('source', [])
        new_src = []
        for line in src:
            if pattern in line:
                new_src.append(line.replace(pattern, replacement))
                modified = True
            else:
                new_src.append(line)
        cell['source'] = new_src
    if modified:
        p.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
        print(f"Successfully updated: {t}")
    else:
        print(f"Pattern not found in: {t}")
