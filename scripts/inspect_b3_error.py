import os
from pathlib import Path
from kaggle.api.kaggle_api_extended import KaggleApi

user = "lznt123"
token = "KGAT_107f196b3b616d0d60398c64eb11f2bd"
os.environ["KAGGLE_API_TOKEN"] = token
os.environ["KAGGLE_USERNAME"] = user
os.environ["KAGGLE_KEY"] = token

api = KaggleApi()
api.authenticate()

slug = "lznt123/grace-b3-validation"
out_dir = Path("Runs-management/kernel_logs/lznt_b3_err")
out_dir.mkdir(parents=True, exist_ok=True)
api.kernels_output(slug, path=str(out_dir))
for p in out_dir.glob("*"):
    print(p.name, p.stat().st_size)
    if p.suffix in [".log", ".txt"]:
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
        print(f"Total lines: {len(lines)}")
        for l in lines[-30:]:
            print(l[:150])
