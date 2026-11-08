import os
import sys
import json
import time
from pathlib import Path
import builtins

# Monkey-patch builtins.open to use utf-8 by default on Windows
_orig_open = builtins.open
def _utf8_open(file, *args, **kwargs):
    mode = args[0] if args else kwargs.get('mode', 'r')
    if 'b' not in mode and 'encoding' not in kwargs:
        kwargs['encoding'] = 'utf-8'
    return _orig_open(file, *args, **kwargs)
builtins.open = _utf8_open

from kaggle.api.kaggle_api_extended import KaggleApi
from kagglesdk.kernels.types.kernels_api_service import ApiListKernelSessionOutputRequest

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

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
        "lznt123/grace-b3-validation"
    ])
]

report = {}

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
        
        # Check files via ApiListKernelSessionOutputRequest
        owner, kernel_slug = s.split('/')
        file_list = []
        log_sample = ""
        try:
            with api.build_kaggle_client() as client:
                req = ApiListKernelSessionOutputRequest()
                req.user_name = owner
                req.kernel_slug = kernel_slug
                res = client.kernels.kernels_api_client.list_kernel_session_output(req)
                file_list = [f.file_name for f in res.files]
                log_data = res.log or ""
                if log_data:
                    lines = [l for l in log_data.splitlines() if l.strip()]
                    log_sample = "\n".join(lines[-10:])
        except Exception as e:
            print(f"   (Error listing files/log: {e})")
            
        print(f"   Files available ({len(file_list)}): {file_list[:10]}")
        if log_sample:
            print(f"   Latest log snippet:\n{log_sample}")
            
        # Download files if any
        out_dir = Path(f"Runs-management/kernel_logs/audit_cycle2/{s.replace('/', '_')}")
        out_dir.mkdir(parents=True, exist_ok=True)
        if file_list:
            try:
                api.kernels_output(s, path=str(out_dir), quiet=True)
                for p in out_dir.glob("*"):
                    print(f"   -> Downloaded: {p.name} ({p.stat().st_size} bytes)")
                    if p.name.endswith(".log") or p.name.endswith(".json"):
                        txt = p.read_text(encoding="utf-8", errors="replace")
                        lines = txt.splitlines()
                        print(f"      Lines: {len(lines)}, latest:")
                        for l in lines[-5:]:
                            print("        ", l[:140])
            except Exception as e:
                print(f"   (Output download error: {e})")
                
        report[s] = {
            "status": str(status_val),
            "failure_message": str(fail_msg),
            "files": file_list
        }

out_summary = Path("Runs-management/audit_cycle2_summary.json")
out_summary.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print("\nAudit finished and saved to Runs-management/audit_cycle2_summary.json")
