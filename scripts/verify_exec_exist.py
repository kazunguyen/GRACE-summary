import json
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Verify executed notebooks exist
exec_dir = Path("Runs-management/downloaded_executed_notebooks")
arms = ["b1_full", "b2_rep", "b2_labelonly", "b2_nolabel", "b1_shuf"]
for arm in arms:
    p = exec_dir / f"02_kaggle_qwen_q4_{arm}_validation_executed.ipynb"
    assert p.is_file(), f"Missing executed validation notebook: {p}"
print("All 5 executed validation notebooks exist and are verified.")
