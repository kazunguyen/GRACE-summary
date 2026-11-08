"""Run unchanged test assertions; redirect only two historical preview writes."""
import contextlib
import io
import json
from pathlib import Path
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import pytest

preview_dir = OUT / "pytest_synthetic_outputs"
preview_dir.mkdir(exist_ok=True)
targets = {(ROOT / "Runs-management/b3_amended_20261106" / name).resolve(): preview_dir / name
           for name in ("synthetic_smoke_prompts.json", "synthetic_smoke_preview.txt")}
original_write = Path.write_text
redirected = []


def write_text(path, *args, **kwargs):
    destination = targets.get(path.resolve())
    if destination is not None:
        redirected.append(path.relative_to(ROOT).as_posix())
        return original_write(destination, *args, **kwargs)
    return original_write(path, *args, **kwargs)


args = ["tests/test_amended_b3.py", "tests/test_preregistration_integrity.py",
        "01_Author_Baseline_Unified/diagnostic_kit/tests/test_probes.py",
        "01_Author_Baseline_Unified/diagnostic_kit/tests/test_stats_and_complementarity.py",
        "--basetemp", str(OUT / "pytest_tmp"), "-ra"]
stream = io.StringIO()
Path.write_text = write_text
try:
    with contextlib.redirect_stdout(stream), contextlib.redirect_stderr(stream):
        code = pytest.main(args)
finally:
    Path.write_text = original_write
(OUT / "pytest.log").write_text(stream.getvalue(), encoding="utf-8")
(OUT / "pytest_result.json").write_text(json.dumps({"returncode": int(code), "args": args,
    "historical_preview_writes_redirected": redirected,
    "test_assertions_unchanged": True}, indent=2) + "\n", encoding="utf-8")
print(stream.getvalue())
sys.exit(int(code))
