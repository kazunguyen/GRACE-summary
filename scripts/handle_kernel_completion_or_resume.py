import os
import sys
import json
import shutil
from pathlib import Path
import builtins

# Monkeypatch builtins.open to force UTF-8 on Windows for Kaggle CLI/SDK
_orig_open = builtins.open
def _utf8_open(file, *args, **kwargs):
    mode = args[0] if args else kwargs.get('mode', 'r')
    if 'b' not in mode and 'encoding' not in kwargs:
        kwargs['encoding'] = 'utf-8'
    return _orig_open(file, *args, **kwargs)
builtins.open = _utf8_open

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from kaggle.api.kaggle_api_extended import KaggleApi
from kagglesdk.kernels.types.kernels_api_service import ApiListKernelSessionOutputRequest

ACCOUNTS = {
    'huuhieu3333': {
        'token': 'KGAT_00cce839fd4e42e96de63ac19f06f316',
        'kernels': [
            {'slug': 'huuhieu3333/grace-b1-full-test', 'arm': 'B1-full', 'expected': 5006, 'split': 'test'},
            {'slug': 'huuhieu3333/grace-b2-rep-test', 'arm': 'B2-rep', 'expected': 5006, 'split': 'test'}
        ]
    },
    'tomandjerry223': {
        'token': 'c78b44e56259c2bb09962d5d1806ddf1',
        'kernels': [
            {'slug': 'tomandjerry223/grace-b2-labelonly-test', 'arm': 'B2-labelonly', 'expected': 5006, 'split': 'test'},
            {'slug': 'tomandjerry223/grace-b2-nolabel-test', 'arm': 'B2-nolabel', 'expected': 5006, 'split': 'test'}
        ]
    },
    'lznt123': {
        'token': 'KGAT_107f196b3b616d0d60398c64eb11f2bd',
        'kernels': [
            {'slug': 'lznt123/grace-b3-validation', 'arm': 'B3', 'expected': 10010, 'split': 'validation'},
            {'slug': 'lznt123/grace-b1-shuf-test', 'arm': 'B1-shuf', 'expected': 5006, 'split': 'test'}
        ]
    }
}

def set_auth(user, token):
    if token.startswith('KGAT_'):
        os.environ['KAGGLE_API_TOKEN'] = token
    else:
        os.environ.pop('KAGGLE_API_TOKEN', None)
    os.environ['KAGGLE_USERNAME'] = user
    os.environ['KAGGLE_KEY'] = token
    api = KaggleApi()
    api.authenticate()
    return api

def inspect_and_handle_all():
    summary = {}
    for user, info in ACCOUNTS.items():
        api = set_auth(user, info['token'])
        print(f"\n==================== Account: {user} ====================")
        for kinfo in info['kernels']:
            slug = kinfo['slug']
            arm = kinfo['arm']
            expected_count = kinfo['expected']
            split = kinfo['split']
            
            st = api.kernels_status(slug)
            status_val = str(getattr(st, 'status', st))
            fail_msg = str(getattr(st, 'failure_message', getattr(st, 'failureMessage', '')))
            print(f"[{slug}] Status: {status_val} | Error: {fail_msg}")
            
            owner, kernel_slug = slug.split('/')
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
                pass
                
            summary[slug] = {
                'status': status_val,
                'error': fail_msg,
                'arm': arm,
                'user': user,
                'split': split,
                'files': file_list
            }
            
            out_dir = Path(f"Runs-management/kernel_outputs_harvest/{slug.replace('/', '_')}")
            out_dir.mkdir(parents=True, exist_ok=True)
            
            if 'COMPLETE' in status_val.upper():
                print(f"   >>> {slug} is COMPLETE! Downloading output artifacts...")
                try:
                    api.kernels_output(slug, path=str(out_dir))
                    files = list(out_dir.glob('*'))
                    print(f"   Downloaded {len(files)} files into {out_dir}:")
                    for f in files:
                        print(f"     - {f.name} ({f.stat().st_size:,} bytes)")
                        
                    records_files = list(out_dir.rglob('records.jsonl'))
                    total_records = 0
                    for rf in records_files:
                        with open(rf, 'r', encoding='utf-8') as fh:
                            c = sum(1 for line in fh if line.strip())
                            total_records += c
                            print(f"       Records in {rf.name}: {c}")
                            
                    summary[slug]['total_records'] = total_records
                    summary[slug]['is_full_census'] = (total_records >= expected_count)
                    
                    if total_records >= expected_count:
                        print(f"   [SUCCESS] {slug} achieved 100% census ({total_records}/{expected_count})!")
                    else:
                        print(f"   [PARTIAL] {slug} completed with partial count ({total_records}/{expected_count}). Ready for resume staging.")
                except Exception as e:
                    print(f"   Error downloading output for {slug}: {e}")
            elif 'RUNNING' in status_val.upper():
                print(f"   >>> {slug} is actively RUNNING.")
                if log_sample:
                    print(f"   Latest log snippet:\n{log_sample}")
            elif 'QUEUED' in status_val.upper():
                print(f"   >>> {slug} is QUEUED in Kaggle scheduler.")
            else:
                print(f"   >>> {slug} status is {status_val}.")
                if log_sample:
                    print(f"   Latest log snippet:\n{log_sample}")
                # If error occurred, check if checkpoint was saved
                if file_list:
                    print(f"   Files in output: {file_list}")
                try:
                    api.kernels_output(slug, path=str(out_dir))
                except Exception:
                    pass
                
    summary_path = Path("Runs-management/live_kernels_harvest_summary.json")
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"\nInspection summary written to {summary_path}")
    return summary

if __name__ == '__main__':
    inspect_and_handle_all()
