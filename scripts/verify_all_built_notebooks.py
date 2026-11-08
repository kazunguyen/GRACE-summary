import json
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

notebooks = [
    Path("09_Arm_B1_Full/notebooks/02_kaggle_qwen_q4_b1_full_test.ipynb"),
    Path("05_Arm_B2_Rep/notebooks/02_kaggle_qwen_q4_b2_rep_test.ipynb"),
    Path("12_Arm_B2_LabelOnly/notebooks/02_kaggle_qwen_q4_b2_labelonly_test.ipynb"),
    Path("10_Arm_B2_NoLabel/notebooks/02_kaggle_qwen_q4_b2_nolabel_test.ipynb"),
    Path("08_Arm_B1_Shuf/notebooks/02_kaggle_qwen_q4_b1_shuf_test.ipynb"),
    Path("13_Arm_B3_Contrastive/notebooks/02_kaggle_qwen_q4_b3_amended_validation.ipynb")
]

for nb_path in notebooks:
    assert nb_path.is_file(), f"Missing notebook: {nb_path}"
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    cells = nb.get("cells", [])
    assert len(cells) == 9, f"{nb_path}: Expected 9 cells, got {len(cells)}"
    
    # Check cell types
    assert cells[0]["cell_type"] == "markdown"
    for i in range(1, 9):
        assert cells[i]["cell_type"] == "code", f"{nb_path} cell {i} is not code"
        
    c2_src = "".join(cells[2]["source"])
    c4_src = "".join(cells[4]["source"])
    c6_src = "".join(cells[6]["source"])
    c7_src = "".join(cells[7]["source"])
    c8_src = "".join(cells[8]["source"])
    
    assert "MODEL_FILENAME = 'Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf'" in c2_src
    assert "transformers==4.57.1" in c4_src
    assert "huggingface_hub==0.36.2" in c4_src
    assert "llama-cpp-python==0.3.16" in c4_src
    assert "KAGGLE_INPUT_ROOT.rglob(MODEL_FILENAME)" in c6_src
    assert "kaggle_inference.py" in c7_src
    assert "diagnostics_zip" in c8_src
    
    print(f"PASS: {nb_path.name} (9 cells, standard architecture verified)")

print("\nALL 6 NOTEBOOKS FULLY COMPLY WITH PIPELINE STANDARDS!")
