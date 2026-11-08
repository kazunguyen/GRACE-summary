import json
from pathlib import Path

# 1. Update B3 notebook
p_nb = Path("13_Arm_B3_Contrastive/notebooks/02_kaggle_qwen_q4_b3_amended_validation.ipynb")
nb = json.loads(p_nb.read_text(encoding="utf-8"))

# Cell 2: Pinned dependencies
c2 = "".join(nb["cells"][2]["source"])
c2 = c2.replace(
    "'transformers==4.57.1', 'huggingface_hub', 'scikit-learn==1.5.2'",
    "'transformers==4.57.1', 'huggingface_hub==0.36.2', 'tokenizers==0.22.2', 'scikit-learn==1.5.2', 'numpy==2.1.3'"
)
c2 = c2.replace(
    "'llama-cpp-python'",
    "'llama-cpp-python', 'llama-cpp-python==0.3.16'"
)
nb["cells"][2]["source"] = [c2]

# Cell 6: Constructor
c6 = "".join(nb["cells"][6]["source"])
old_cons = """llm = llama_cpp.Llama(
    model_path=model_path,
    n_gpu_layers=-1,
    n_ctx=8192,
    seed=4294967295,
    verbose=False,
    logits_all=True
)"""

new_cons = """llm = llama_cpp.Llama(
    model_path=model_path,
    n_ctx=8192,
    n_batch=256,
    n_ubatch=256,
    n_gpu_layers=-1,
    split_mode=llama_cpp.LLAMA_SPLIT_MODE_LAYER,
    seed=4294967295,
    logits_all=True,
    verbose=False
)"""

if old_cons in c6:
    c6 = c6.replace(old_cons, new_cons)
    nb["cells"][6]["source"] = [c6]
    print("Updated cell 6 constructor in B3 notebook.")
else:
    print("Warning: old_cons not found in cell 6")

p_nb.write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding="utf-8")
print("B3 notebook successfully written.")

# 2. Update builder script
p_bld = Path("Runs-management/build_and_launch_b3_amended_kaggle.py")
bld_text = p_bld.read_text(encoding="utf-8")
bld_text = bld_text.replace(
    "'transformers==4.57.1', 'huggingface_hub', 'scikit-learn==1.5.2'",
    "'transformers==4.57.1', 'huggingface_hub==0.36.2', 'tokenizers==0.22.2', 'scikit-learn==1.5.2', 'numpy==2.1.3'"
)
bld_text = bld_text.replace(
    "'llama-cpp-python'",
    "'llama-cpp-python', 'llama-cpp-python==0.3.16'"
)
bld_text = bld_text.replace(old_cons, new_cons)
p_bld.write_text(bld_text, encoding="utf-8")
print("B3 builder script successfully updated.")
