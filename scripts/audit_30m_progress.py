import os
from pathlib import Path
from kaggle.api.kaggle_api_extended import KaggleApi

configs = [
    ("huuhieu3333", "KGAT_00cce839fd4e42e96de63ac19f06f316", [
        "huuhieu3333/grace-b2-rep-test",
        "huuhieu3333/grace-b1-full-test"
    ]),
    ("tomandjerry223", "c78b44e56259c2bb09962d5d1806ddf1", [
        "tomandjerry223/grace-b2-labelonly-test",
        "tomandjerry223/grace-b2-nolabel-test"
    ]),
    ("lznt123", "KGAT_107f196b3b616d0d60398c64eb11f2bd", [
        "lznt123/grace-b3-validation",
        "lznt123/grace-b1-shuf-test"
    ])
]

for user, token, slugs in configs:
    print(f"\n==================== Account: {user} ====================")
    if token.startswith("KGAT_"):
        os.environ["KAGGLE_API_TOKEN"] = token
    else:
        os.environ.pop("KAGGLE_API_TOKEN", None)
    os.environ["KAGGLE_USERNAME"] = user
    os.environ["KAGGLE_KEY"] = token
    api = KaggleApi()
    api.authenticate()
    for s in slugs:
        st = api.kernels_status(s)
        status_val = getattr(st, 'status', str(st))
        fail_msg = getattr(st, 'failure_message', getattr(st, 'failureMessage', ''))
        print(f"[{s}] Status: {status_val} | Error: {fail_msg}")
        
        # Download output files
        out_dir = Path(f"Runs-management/kernel_logs/check_30m/{s.replace('/', '_')}")
        out_dir.mkdir(parents=True, exist_ok=True)
        try:
            api.kernels_output(s, path=str(out_dir))
            for p in out_dir.glob("*"):
                print(f"   -> {p.name} ({p.stat().st_size} bytes)")
                if p.suffix in [".log", ".txt"]:
                    lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
                    print(f"      Entries ({len(lines)}), latest:")
                    for l in lines[-8:]:
                        print("       ", l[:140])
        except Exception as e:
            print(f"   (Output download: {e})")
