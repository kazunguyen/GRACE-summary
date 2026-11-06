import json
from pathlib import Path

src_nb_path = Path('13_Arm_B3_Contrastive/notebooks/02_kaggle_qwen_q4_b3_validation.ipynb')
with open(src_nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Modify markdown
nb['cells'][0]['source'] = [
    "# Arm B3-nodiff — Contrastive Demonstration Without Key Difference (Validation)\n",
    "\n",
    "Chạy chẩn đoán B3-nodiff trên tập validation census (5.005 prompt):\n",
    "- **B3-nodiff**: Prompt gồm code mục tiêu + CPG graph prefix + cặp demo (safe & vuln) KHÔNG có Key difference.\n",
    "\n",
    "Model: Qwen3-Coder-30B-A3B-Instruct Q4_K_M trên 2x Tesla T4 GPU."
]

# Modify Cell 2 RUN_SPECS to only B3-nodiff
c2 = ''.join(nb['cells'][2]['source'])
c2 = c2.replace("CHECKPOINT_NAME = 'grace_b3_validation_checkpoint.zip'", "CHECKPOINT_NAME = 'grace_b3_nodiff_validation_checkpoint.zip'")
idx_specs = c2.find('RUN_SPECS = [')
specs_code = '''RUN_SPECS = [
    {
        "arm": "B3-nodiff",
        "seed": 42,
        "dataset": "devign",
        "member_path": "b3_nodiff/seed_42/devign_validation.zip",
        "inner_sha256": "63a5ec41df4e8c85600b49676e92f34fec29cfb36d864313778c5e8744d9a9d7",
        "prompts_sha256": "4a40f20bfebf1e0b607f72304430aec08e7221b91f47a85fd9211f03432afa43",
        "count": 2732
    },
    {
        "arm": "B3-nodiff",
        "seed": 42,
        "dataset": "reveal",
        "member_path": "b3_nodiff/seed_42/reveal_validation.zip",
        "inner_sha256": "4a5dd84f0632611cc4e5322ef3bf842bd827d70bee0542110d8e95af26a0d686",
        "prompts_sha256": "91c9f04212e2490fc7701118ee2d5c2870bb604fdde4c5b425894d819bfc9740",
        "count": 2273
    }
]
'''
c2 = c2[:idx_specs] + specs_code
nb['cells'][2]['source'] = [c2]

# Modify Cell 8 loop
c8 = ''.join(nb['cells'][8]['source'])
c8 = c8.replace("for arm in ['B3', 'B3-nodiff']:", "for arm in ['B3-nodiff']:")
c8 = c8.replace("'arms': ['B3', 'B3-nodiff']", "'arms': ['B3-nodiff']")
nb['cells'][8]['source'] = [c8]

out_dir = Path('14_Arm_B3_NoDiff/notebooks')
out_dir.mkdir(parents=True, exist_ok=True)
out_path = out_dir / '02_kaggle_qwen_q4_b3_nodiff_validation.ipynb'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=2)
print('Generated dedicated B3-nodiff notebook at', out_path)
