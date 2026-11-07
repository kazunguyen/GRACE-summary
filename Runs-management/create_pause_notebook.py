import os
import json
from pathlib import Path

pause_dir = Path('Runs-management/kaggle_staging_thanhduy/pause_kernel')
pause_dir.mkdir(parents=True, exist_ok=True)

nb = {
    "cells": [
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": ["print('Kernel paused by user request to preserve GPU quota.')"]
        }
    ],
    "metadata": {
        "language_info": {"name": "python"}
    },
    "nbformat": 4,
    "nbformat_minor": 4
}

with open(pause_dir / 'pause.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=2)

meta = {
    "id": "thanhduy9a4tv/grace-b1-shuf-validation",
    "title": "grace-b1-shuf-validation",
    "code_file": "pause.ipynb",
    "language": "python",
    "kernel_type": "notebook",
    "is_private": True,
    "enable_gpu": False,
    "enable_tpu": False,
    "enable_internet": False,
    "keywords": [],
    "dataset_sources": [],
    "kernel_sources": [],
    "competition_sources": [],
    "model_sources": []
}

with open(pause_dir / 'kernel-metadata.json', 'w', encoding='utf-8') as f:
    json.dump(meta, f, indent=2)

print('Pause notebook created in', pause_dir)
