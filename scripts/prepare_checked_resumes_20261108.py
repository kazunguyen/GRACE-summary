"""Prepare reviewable recovery artifacts only; never upload or launch a kernel."""
import ast
import copy
import hashlib
import json
from pathlib import Path
import re
import types
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "Runs-management/acceptance_6arms_20261108"
OUT = BASE / "resume_delivery"
HARVEST = ROOT / "Runs-management/kernel_outputs_harvest"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def rewrite_helper(source):
    tree = ast.parse(source)
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "load_locked_model")
    assignment = next(n for n in function.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "gpu_devices" for t in n.targets))
    following = function.body[function.body.index(assignment) + 1]
    assert isinstance(following, ast.If) and "gpu_devices" in ast.unparse(following.test)
    replacement = r'''    # Both historical headers and the captured current backend format are accepted.
    # Prefer devices actually used for model load when those lines are present.
    loaded_ids = set(re.findall(
        r'(?mi)^\s*(?:[\w.]+:\s*)?using device CUDA(\d+)\s+\([^\n)]*\bT4\b[^\n)]*\)', text))
    legacy_ids = set(re.findall(r'(?mi)^\s*Device\s+(\d+):[^\n]*\bT4\b', text))
    observed_ids = loaded_ids if loaded_ids else legacy_ids
    expected_ids = {str(i) for i in range(c['gpu']['device_count'])}
    if observed_ids != expected_ids:
        model.close()
        raise RuntimeError(f'Expected T4 device IDs {expected_ids}, observed {observed_ids}; inspect {path}')'''
    lines = source.splitlines()
    lines[assignment.lineno - 1:following.end_lineno] = replacement.splitlines()
    revised = "\n".join(lines) + "\n"
    compile(revised, "patched_runtime_helper", "exec")
    # All preceding offload/context guards remain byte-identical at AST level.
    before = [n for n in function.body if n.lineno < assignment.lineno]
    patched = next(n for n in ast.parse(revised).body if isinstance(n, ast.FunctionDef) and n.name == function.name)
    assert [ast.dump(n, include_attributes=False) for n in before] == [ast.dump(n, include_attributes=False) for n in patched.body[:len(before)]]
    return revised


def edit_notebook(notebook, helper_transform=None, assignments=None):
    nb = copy.deepcopy(notebook)
    helper_count = 0
    updates = set()
    for cell in nb["cells"]:
        if cell.get("cell_type") != "code":
            continue
        cell["outputs"] = []
        cell["execution_count"] = None
        s = "".join(cell.get("source", []))
        if s.lstrip().startswith("%%"):
            continue
        try:
            tree = ast.parse(s)
        except SyntaxError:
            continue
        replacements = []
        if helper_transform:
            for n in ast.walk(tree):
                if isinstance(n, ast.Constant) and isinstance(n.value, str) and "def load_locked_model" in n.value:
                    old = ast.get_source_segment(s, n)
                    replacements.append((old, repr(helper_transform(n.value))))
                    helper_count += 1
        if assignments:
            for n in tree.body:
                if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name) and n.targets[0].id in assignments:
                    name = n.targets[0].id
                    replacements.append((ast.get_source_segment(s, n), name + " = " + assignments[name]))
                    updates.add(name)
        for old, new in replacements:
            assert s.count(old) == 1
            s = s.replace(old, new, 1)
        cell["source"] = s.splitlines(keepends=True)
    if helper_transform:
        assert helper_count == 1
    if assignments:
        assert updates == set(assignments)
    return nb


def main():
    if OUT.exists():
        raise FileExistsError("Preserve previous delivery; choose a new version before regenerating")
    OUT.mkdir(parents=True)
    manifest = {"scope": "Local recovery/preparation only. No kernel launch. No prompt, threshold, runtime contract or model changes.", "artifacts": []}

    # B1-shuf had zero inference records. Correct only the false-negative native-log guard.
    original_path = ROOT / "08_Arm_B1_Shuf/notebooks/02_kaggle_qwen_q4_b1_shuf_test.ipynb"
    original = json.loads(original_path.read_text(encoding="utf-8"))
    patched = edit_notebook(original, helper_transform=rewrite_helper)
    target = OUT / "02_kaggle_b1_shuf_test_gpu_log_guard_fixed.ipynb"
    target.write_text(json.dumps(patched, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    captured = HARVEST / "lznt123_grace-b1-shuf-test/b1_shuf_test_runtime_locked/runtime_provenance/seed_42_tt2427_c/model_load_offload.log"
    actual_log = captured.read_text(encoding="utf-8")
    native_count = len(set(re.findall(r"using device CUDA(\d+) \([^\n)]*T4", actual_log)))
    assert native_count == 2 and "offloaded 49/49 layers to GPU" in actual_log
    # Exercise the actual revised function with the real saved native log, not an invented format.
    helper_old = (HARVEST / "lznt123_grace-b1-shuf-test/grace_runtime_contract.py").read_text(encoding="utf-8")
    helper = types.ModuleType("revised_helper")
    exec(compile(rewrite_helper(helper_old), "revised_helper", "exec"), helper.__dict__)
    contract = json.loads((ROOT / "configs/inference_runtime_lock.json").read_text(encoding="utf-8"))
    import sys
    state = {"log": actual_log}
    calls = []

    class FakeModel:
        def __init__(self, **kwargs):
            calls.append(kwargs)
            print(state["log"], file=sys.stderr)

        def close(self):
            pass

    fake = types.ModuleType("llama_cpp")
    fake.Llama = FakeModel
    fake.LLAMA_SPLIT_MODE_LAYER = 1
    fake.llama_supports_gpu_offload = lambda: True
    previous = sys.modules.get("llama_cpp")
    sys.modules["llama_cpp"] = fake
    checks = []
    tm = {"tokenizer": contract["tokenizer"]["repo"], "tokenizer_revision": contract["tokenizer"]["revision"], "prompt_budget_tokens": 8192}
    import contextlib
    import io

    def load():
        with contextlib.redirect_stdout(io.StringIO()):
            return helper.load_locked_model(contract, "fake.gguf", tm, -1, OUT / "temporary_guard_log.txt", contract["model"]["sha256"])

    try:
        load()
        checks.append("real_saved_two_T4_49of49_log_accepts")
        assert calls[-1]["tensor_split"] is None and calls[-1]["n_ctx"] == 8192
        for name, bad_log in [
            ("one_device_rejects", re.sub(r"(?m)^.*using device CUDA1[^\n]*\n?", "", actual_log)),
            ("duplicate_CUDA0_rejects", actual_log.replace("using device CUDA1", "using device CUDA0")),
            ("48of49_rejects", actual_log.replace("offloaded 49/49", "offloaded 48/49")),
            ("wrong_context_rejects", re.sub(r"(n_ctx\s*=\s*)8192", r"\g<1>4096", actual_log)),
            ("non_T4_rejects", actual_log.replace("Tesla T4", "NVIDIA A100")),
        ]:
            state["log"] = bad_log
            try:
                load()
            except RuntimeError:
                checks.append(name)
            else:
                raise AssertionError(name)
    finally:
        (OUT / "temporary_guard_log.txt").unlink(missing_ok=True)
        if previous is None:
            sys.modules.pop("llama_cpp", None)
        else:
            sys.modules["llama_cpp"] = previous
    manifest["b1_shuf_guard_tests"] = {"scope": "Saved native log replay with fake model; no GPU inference", "passed": checks}
    manifest["artifacts"].append({"path": target.name, "sha256": sha(target.read_bytes()), "source": str(original_path.relative_to(ROOT)), "source_sha256": sha(original_path.read_bytes()), "change": "Only device-log parsing; prompts, tau, package versions, constructor and contract unchanged."})

    # Preserve all 2850 B1-full loose records; the original periodic ZIP has only 2846.
    origin = HARVEST / "huuhieu3333_grace-b1-full-test/b1_full_test"
    recovery = OUT / "grace_b1_full_test_recovered_2850.zip"
    member_info = []
    with ZipFile(recovery, "w", ZIP_DEFLATED) as z:
        for path in sorted(origin.rglob("*")):
            if path.is_file() and path.name in ["records.jsonl", "run_manifest.json", "evaluation.json"]:
                raw = path.read_bytes()
                name = path.relative_to(origin).as_posix()
                z.writestr(name, raw)
                member_info.append({"name": name, "sha256": sha(raw), "records": sum(bool(l.strip()) for l in raw.splitlines()) if path.name == "records.jsonl" else None})
        z.writestr("RECOVERY_NOTICE.json", json.dumps({"classification": "forensic recovery, not a runtime-lock certification", "original_records_are_byte_preserved": True,
            "partial_reveal_manifest": "absent in original; none fabricated", "warning": "B1-full prompt budget failure remains unresolved. Do not resume unchanged or silently truncate/skip the failing ID.", "members": member_info}, ensure_ascii=False, indent=2))
    assert sum(r["records"] or 0 for r in member_info) == 2850
    manifest["artifacts"].append({"path": recovery.name, "sha256": sha(recovery.read_bytes()), "members": member_info, "ready_for_gpu_resume": False})

    # Prepare B3 historical continuation separately, preserving the exact historical runner.
    source_path = BASE / "network_verified/lznt123/grace-b3-validation/source/grace-b3-validation.ipynb"
    nb = json.loads(source_path.read_text(encoding="utf-8"))
    revised = edit_notebook(nb, assignments={"CHECKPOINT_INPUT_PATH": "None"})
    output_path = OUT / "02_kaggle_b3_historical_validation_resume.ipynb"
    output_path.write_text(json.dumps(revised, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    checkpoint = HARVEST / "lznt123_grace-b3-validation/grace_b3_validation_checkpoint.zip"
    checkpoint_target = OUT / checkpoint.name
    checkpoint_target.write_bytes(checkpoint.read_bytes())
    manifest["artifacts"].append({"path": output_path.name, "sha256": sha(output_path.read_bytes()), "source": str(source_path.relative_to(ROOT)), "change": "Outputs cleared; same historical runner and checkpoint auto-discovery. Not upgraded silently to runtime-locked/amended B3."})
    manifest["artifacts"].append({"path": checkpoint_target.name, "sha256": sha(checkpoint_target.read_bytes()), "records": 4029, "remaining_B3_REVEAL": 976, "remaining_B3_nodiff": 5005})
    (OUT / "delivery_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Prepared local delivery; log-parser checks", len(checks), "/6; B1-full recovered 2850; B3 checkpoint copied byte-for-byte. No upload/launch.")


if __name__ == "__main__":
    main()
