import json
import shutil
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

staging_tasks = [
    {
        "user": "huuhieu3333",
        "slug": "grace-b1-full-test",
        "stage_dir": Path("Runs-management/kaggle_staging_huuhieu3333/grace-b1-full-test_run"),
        "code_file": "02_kaggle_qwen_q4_b1_full_test.ipynb",
        "src_path": Path("09_Arm_B1_Full/notebooks/02_kaggle_qwen_q4_b1_full_test.ipynb"),
        "dataset_sources": ["huuhieu3333/grace-b1-full-test-inputs"],
        "kernel_sources": ["huuhieu3333/qwen3coder30b-prepare-notebook"]
    },
    {
        "user": "huuhieu3333",
        "slug": "grace-b2-rep-test",
        "stage_dir": Path("Runs-management/kaggle_staging_huuhieu3333/grace-b2-rep-test_run"),
        "code_file": "02_kaggle_qwen_q4_b2_rep_test.ipynb",
        "src_path": Path("05_Arm_B2_Rep/notebooks/02_kaggle_qwen_q4_b2_rep_test.ipynb"),
        "dataset_sources": ["huuhieu3333/grace-b2-rep-test-inputs"],
        "kernel_sources": ["huuhieu3333/qwen3coder30b-prepare-notebook"]
    },
    {
        "user": "tomandjerry223",
        "slug": "grace-b2-labelonly-test",
        "stage_dir": Path("Runs-management/kaggle_staging_tomandjerry223/grace-b2-labelonly-test_run"),
        "code_file": "02_kaggle_qwen_q4_b2_labelonly_test.ipynb",
        "src_path": Path("12_Arm_B2_LabelOnly/notebooks/02_kaggle_qwen_q4_b2_labelonly_test.ipynb"),
        "dataset_sources": ["tomandjerry223/grace-b2-labelonly-test-inputs"],
        "kernel_sources": ["quangdung1111/qwen3coder30b-prepare-notebook"]
    },
    {
        "user": "tomandjerry223",
        "slug": "grace-b2-nolabel-test",
        "stage_dir": Path("Runs-management/kaggle_staging_tomandjerry223/grace-b2-nolabel-test_run"),
        "code_file": "02_kaggle_qwen_q4_b2_nolabel_test.ipynb",
        "src_path": Path("10_Arm_B2_NoLabel/notebooks/02_kaggle_qwen_q4_b2_nolabel_test.ipynb"),
        "dataset_sources": ["tomandjerry223/grace-b2-nolabel-test-inputs"],
        "kernel_sources": ["quangdung1111/qwen3coder30b-prepare-notebook"]
    },
    {
        "user": "lznt123",
        "slug": "grace-b3-validation",
        "stage_dir": Path("Runs-management/kaggle_staging_lznt123/b3_amended_test_run"),
        "code_file": "02_kaggle_qwen_q4_b3_amended_validation.ipynb",
        "src_path": Path("13_Arm_B3_Contrastive/notebooks/02_kaggle_qwen_q4_b3_amended_validation.ipynb"),
        "dataset_sources": ["lznt123/grace-b3-validation-inputs"],
        "kernel_sources": ["lznt123/qwen3coder30b-prepare-notebook"]
    }
]

for task in staging_tasks:
    task["stage_dir"].mkdir(parents=True, exist_ok=True)
    dst_nb = task["stage_dir"] / task["code_file"]
    shutil.copy2(task["src_path"], dst_nb)
    
    meta = {
        "id": f"{task['user']}/{task['slug']}",
        "title": task["slug"],
        "code_file": task["code_file"],
        "language": "python",
        "kernel_type": "notebook",
        "is_private": True,
        "enable_gpu": True,
        "enable_tpu": False,
        "enable_internet": True,
        "keywords": ["gpu"],
        "dataset_sources": task["dataset_sources"],
        "kernel_sources": task["kernel_sources"],
        "competition_sources": [],
        "model_sources": []
    }
    meta_path = task["stage_dir"] / "kernel-metadata.json"
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"Staged {task['user']}/{task['slug']} -> {dst_nb}")

print("\nAll staging directories and metadata prepared successfully!")
