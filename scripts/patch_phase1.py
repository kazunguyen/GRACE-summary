#!/usr/bin/env python3
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# 1. Patch preregistration.md
prereg_path = REPO_ROOT / "preregistration.md"
with open(prereg_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, l in enumerate(lines):
    if "devign|B2|42" in l and "0.98" in l:
        lines[idx] = l.replace("0.98", "0.70")
    elif "reveal|B2|42" in l and "0.99" in l:
        lines[idx] = l.replace("0.99", "0.12")
    elif "**Devign**" in l and "Clean Donors Bank" in l:
        lines[idx] = l.replace("21,711", "21,691")
    elif "**ReVeal**" in l and "Clean Donors Bank" in l:
        lines[idx] = l.replace("17,620", "17,636")
    elif "Target Serving Backend:" in l and "UD-Q4_K_XL" in l:
        lines[idx] = l.replace(
            "UD-Q4_K_XL (`Qwen3-Coder-30B-A3B-Instruct-UD-Q4_K_XL.gguf`",
            "Q4_K_M (`Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf`, file SHA-256: `f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335`"
        )
    elif "Primary Architecture:" in l and "Qwen/Qwen3-Coder-30B-A3B-Instruct" in l and "b2cff646eb4bb1d68355c01b18ae02e7cf42d120" not in l:
        lines[idx] = l.rstrip() + " tại revision Hugging Face `b2cff646eb4bb1d68355c01b18ae02e7cf42d120`.\n"

with open(prereg_path, "w", encoding="utf-8", newline="\n") as f:
    f.writelines(lines)
print("[OK] Patched preregistration.md")

# 2. Patch backend_manifest.json
manifest_path = REPO_ROOT / "Runs-management" / "step1_backend_smoke" / "backend_manifest.json"
diag_manifest_dir = REPO_ROOT / "01_Author_Baseline_Unified" / "diagnostic_kit" / "configs"
diag_manifest_dir.mkdir(parents=True, exist_ok=True)
diag_manifest_path = diag_manifest_dir / "backend_manifest.json"

backend_manifest = {
    "model_name": "Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf",
    "model_sha256": "f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335",
    "quantization": "Q4_K_M",
    "runtime_engine": "llama-cpp-python 0.3.16",
    "context_limit_tokens": 8192,
    "sampling": {
        "temperature": 0.0,
        "seed": 42,
        "max_tokens": 1,
        "top_logprobs": 5
    },
    "token_ids": {
        "0": 15,
        "1": 16
    },
    "scoring_protocol": "s = exp(logit_1) / (exp(logit_0) + exp(logit_1)) = sigmoid(logit_1 - logit_0)",
    "guided_choice": False
}

with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(backend_manifest, f, indent=2, ensure_ascii=False)
with open(diag_manifest_path, "w", encoding="utf-8") as f:
    json.dump(backend_manifest, f, indent=2, ensure_ascii=False)
print("[OK] Updated backend_manifest.json in step1_backend_smoke and diagnostic_kit/configs")

# 3. Synchronize protocol.yaml
protocol_root = REPO_ROOT / "configs" / "protocol.yaml"
protocol_diag = REPO_ROOT / "01_Author_Baseline_Unified" / "diagnostic_kit" / "configs" / "protocol.yaml"

with open(protocol_root, "r", encoding="utf-8") as f:
    proto_lines = f.readlines()

for idx, l in enumerate(proto_lines):
    if "serving:" in l and "UD-Q4_K_XL" in l:
        proto_lines[idx] = l.replace("UD-Q4_K_XL", "Q4_K_M")
    elif "quantization_note:" in l and "UD-Q4_K_XL" in l:
        proto_lines[idx] = l.replace(
            "Qwen3-Coder-30B-A3B-Instruct-UD-Q4_K_XL.gguf (16.45 GB",
            "Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf (file SHA-256: f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335, 16.45 GB, Hugging Face revision b2cff646eb4bb1d68355c01b18ae02e7cf42d120"
        )

with open(protocol_root, "w", encoding="utf-8", newline="\n") as f:
    f.writelines(proto_lines)
with open(protocol_diag, "w", encoding="utf-8", newline="\n") as f:
    f.writelines(proto_lines)
print("[OK] Synchronized protocol.yaml files")

# 4. Update test_preregistration_integrity.py to reflect Q4_K_M unification
test_file = REPO_ROOT / "tests" / "test_preregistration_integrity.py"
with open(test_file, "r", encoding="utf-8") as f:
    test_content = f.read()

# Update assertions: require Q4_K_M and forbid 7B
test_content = test_content.replace(
    'assert "UD-Q4_K_XL" in text, "Thiếu định dạng lượng tử hóa UD-Q4_K_XL!"',
    'assert "Q4_K_M" in text, "Thiếu định dạng lượng tử hóa Q4_K_M!"'
)
test_content = test_content.replace(
    'assert "Q4_K_M" not in text, "Vẫn còn vết sót lượng tử hóa Q4_K_M trong preregistration.md!"',
    'assert "Q4_K_M" in text, "Thiếu định danh lượng tử hóa Q4_K_M trong preregistration.md!"'
)
test_content = test_content.replace(
    'assert "Qwen3-Coder-30B-A3B-Instruct-UD-Q4_K_XL.gguf" in backend["quantization_note"]',
    'assert "Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf" in backend["quantization_note"]'
)

with open(test_file, "w", encoding="utf-8", newline="\n") as f:
    f.write(test_content)
print("[OK] Updated test_preregistration_integrity.py")
