"""Static AST comparison of downloaded Kaggle notebooks with the delivery ZIP.

Does not execute downloaded code. Uses actual Llama calls and helper code,
not presence of expected numbers inside comments or embedded policy text.
"""
import ast
import hashlib
import json
from pathlib import Path
import re
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "Runs-management/runtime_audit_20261108"
LOCK = ROOT / "configs/inference_runtime_lock.json"


def sha(value):
    return hashlib.sha256(value).hexdigest()


def analyze(raw, label):
    notebook = json.loads(raw)
    units = []
    queue = []
    for i, cell in enumerate(notebook.get("cells", [])):
        if cell.get("cell_type") != "code":
            continue
        source = "".join(cell.get("source", []))
        if source.lstrip().startswith("%%writefile"):
            source = source.split("\n", 1)[1]
        queue.append((f"cell_{i}", source))
    seen = set()
    while queue:
        location, source = queue.pop(0)
        if source in seen:
            continue
        seen.add(source)
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue
        units.append((location, source, tree))
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and "\ndef " in node.value:
                queue.append((location + ":embedded_python", node.value))
    calls, models, constants, functions, lock_bytes = [], [], {}, {}, []
    installed = []
    for location, source, tree in units:
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                try:
                    value = ast.literal_eval(node.value)
                except (ValueError, TypeError, SyntaxError):
                    continue
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        if isinstance(value, (str, int, float, bool, dict, list, bytes, type(None))):
                            constants[target.id] = value
                        if target.id == "RUNTIME_LOCK_BYTES" and isinstance(value, bytes):
                            lock_bytes.append(value)
            if isinstance(node, ast.FunctionDef):
                functions[node.name] = {"location": location, "line": node.lineno,
                                        "ast_sha256": sha(ast.dump(node, include_attributes=False).encode())}
            if not isinstance(node, ast.Call):
                continue
            name = ast.unparse(node.func)
            calls.append(name)
            if name in ["Llama", "llama_cpp.Llama", "load_locked_model"]:
                models.append({"location": location, "line": node.lineno, "call": ast.get_source_segment(source, node),
                               "kwargs": {k.arg or "**": ast.unparse(k.value) for k in node.keywords}})
            if name.endswith("run_logged") or name.endswith("subprocess.run") or name.endswith("subprocess.check_call"):
                segment = ast.get_source_segment(source, node)
                if "pip" in segment and "install" in segment:
                    installed.append({"location": location, "line": node.lineno, "call": segment[:1800]})
    full = "\n".join(s for _, s, _ in units)
    expected_lock = LOCK.read_bytes()
    expected_contract = json.loads(expected_lock)
    return {"path": label, "sha256": sha(raw), "code_cells": sum(c.get("cell_type") == "code" for c in notebook.get("cells", [])),
            "embedded_contract_bytes_match": bool(lock_bytes) and all(b == expected_lock for b in lock_bytes),
            "embedded_contract_json_matches": bool(lock_bytes) and all(json.loads(b) == expected_contract for b in lock_bytes),
            "embedded_contract_matches_lf_bytes_diagnostic": bool(lock_bytes) and all(b == expected_lock.replace(b"\r\n", b"\n") for b in lock_bytes),
            "embedded_contract_sha256": [sha(b) for b in lock_bytes],
            "constructor_calls": models,
            "enforcement_calls": {k: k in calls for k in ["load_contract", "assert_runtime", "load_locked_model", "provenance"]},
            "helper_function_hashes": {k: functions[k] for k in functions if k in ["load_contract", "assert_runtime", "load_locked_model", "provenance", "binary_scores"]},
            "pip_calls": installed,
            "critical_constants": {k: constants[k] for k in ["ARM", "IS_REPEAT", "CACHE_TAG", "LOCKED_THRESHOLDS", "BUNDLE_SHA256", "MODEL_SHA256", "MAX_RUNTIME_HOURS", "CHECKPOINT_RESERVE_SECONDS", "RESUME_FROM_CHECKPOINT", "GPU_LAYERS"] if k in constants},
            "has_sdist_hash": "34ed0f9bd9431af045bb63d9324ae620ad0536653740e9bb163a2e1fcb973be6" in full,
            "has_full_offload_guard_source": "Full {required}/{required} GPU offload not verified" in full,
            "has_direct_logits_scoring": "llm.eval" in calls and "llm.reset" in calls,
            "recorded_inference_seed": bool(re.search(r"inference_seed", full)),
            "source_note": "AST evidence only; does not certify a running process or installation without matching session logs."}


def main():
    package = ROOT / "Runs-management/grace_hieu_5arms_runtime_locked_20261107.zip"
    with ZipFile(package) as z:
        reference = [analyze(z.read(n), "ZIP::" + n) for n in z.namelist() if n.endswith(".ipynb")]
    live = [analyze(p.read_bytes(), p.relative_to(ROOT).as_posix()) for p in sorted((BASE / "live").glob("*/*/source/*.ipynb"))]
    local_paths = ["05_Arm_B2_Rep/notebooks/02_kaggle_qwen_q4_b2_rep_test.ipynb",
                   "09_Arm_B1_Full/notebooks/02_kaggle_qwen_q4_b1_full_test.ipynb",
                   "10_Arm_B2_NoLabel/notebooks/02_kaggle_qwen_q4_b2_nolabel_test.ipynb",
                   "12_Arm_B2_LabelOnly/notebooks/02_kaggle_qwen_q4_b2_labelonly_test.ipynb",
                   "08_Arm_B1_Shuf/notebooks/02_kaggle_qwen_q4_b1_shuf_test.ipynb",
                   "13_Arm_B3_Contrastive/notebooks/02_kaggle_qwen_q4_b3_amended_validation.ipynb"]
    local = [analyze((ROOT / p).read_bytes(), p) for p in local_paths if (ROOT / p).exists()]
    log_evidence = []
    output_files = [p for directory in (BASE / "live").glob("*/*/output") for p in directory.rglob("*")]
    for p in sorted(output_files):
        if not p.is_file() or p.suffix not in [".log", ".txt", ".json"]:
            continue
        if p.stat().st_size > 20_000_000:
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        hits = []
        for lineno, line in enumerate(text.splitlines(), 1):
            if any(s in line for s in ["offloaded ", "CUDA0 model buffer", "CUDA1 model buffer", "n_ctx ", "n_batch ", "n_ubatch ", "Successfully installed", "inference_seed", "runtime_contract_sha256", "Traceback", "RuntimeError:", "ValueError:", "constructor"]):
                # Package logs and native offload diagnostics only; don't copy arbitrary secrets.
                if any(s in line.lower() for s in ["api_key", "api_token", "kgat_", "kaggle_key"]):
                    continue
                hits.append({"line": lineno, "text": line[:1800]})
        if hits:
            log_evidence.append({"path": p.relative_to(ROOT).as_posix(), "sha256": sha(p.read_bytes()), "hits": hits[:100]})
    report = {"package_sha256": sha(package.read_bytes()), "contract_file_sha256": sha(LOCK.read_bytes()),
              "reference_notebooks": reference, "downloaded_notebooks": live, "local_notebooks": local,
              "log_evidence": log_evidence}
    target = BASE / "source_comparison.json"
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("ZIP", report["package_sha256"])
    for r in reference + live + local:
        print(r["path"], "contract_JSON", r["embedded_contract_json_matches"], "enforcement", r["enforcement_calls"], "models", len(r["constructor_calls"]))
    print("Log files with relevant evidence:", len(log_evidence))


if __name__ == "__main__":
    main()
