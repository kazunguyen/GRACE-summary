import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent.resolve()
diag_src = root_dir / "01_Author_Baseline_Unified" / "diagnostic_kit" / "src"
grace_src = root_dir / "grace_diag_kit" / "src"

for p in [str(root_dir), str(diag_src), str(grace_src)]:
    if p not in sys.path:
        sys.path.insert(0, p)
