import os
import sys
import time
from datetime import datetime, timezone
from kaggle.api.kaggle_api_extended import KaggleApi

def main():
    print("========================================================================================")
    print("                     GRACE VALIDATION 4-ARM CONCURRENT TRACKER                          ")
    print(f"                     Timestamp: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}                       ")
    print("========================================================================================")

    # 1. Check tomandjerry223
    try:
        # Defaults to ~/.kaggle/kaggle.json
        if 'KAGGLE_USERNAME' in os.environ:
            del os.environ['KAGGLE_USERNAME']
        if 'KAGGLE_KEY' in os.environ:
            del os.environ['KAGGLE_KEY']
        if 'KAGGLE_API_TOKEN' in os.environ:
            del os.environ['KAGGLE_API_TOKEN']

        api_tom = KaggleApi()
        api_tom.authenticate()

        tom_runs = [
            ("B1-full", "tomandjerry223/grace-b1-full-validation"),
            ("B2-nolabel", "tomandjerry223/grace-b2-nolabel-validation"),
            ("B1-shuf", "tomandjerry223/grace-b1-shuf-validation"),
        ]
        for arm, slug in tom_runs:
            st = api_tom.kernels_status(slug)
            st_val = str(getattr(st, 'status', st))
            msg = getattr(st, 'failure_message', '') or ''
            print(f"Account: tomandjerry223 | Arm: {arm:<12} | Kernel: {slug:<42} | Status: {st_val} {msg}")
    except Exception as e:
        print(f"Error checking tomandjerry223: {e}")

    # 2. Check thanhduy9a4tv
    try:
        os.environ['KAGGLE_USERNAME'] = 'thanhduy9a4tv'
        os.environ['KAGGLE_KEY'] = 'KGAT_47e27c5341b3301eea2f4e8f3d4743d6'
        os.environ['KAGGLE_API_TOKEN'] = 'KGAT_47e27c5341b3301eea2f4e8f3d4743d6'

        api_thanh = KaggleApi()
        api_thanh.authenticate()

        thanh_runs = [
            ("Model Prep", "thanhduy9a4tv/qwen3coder30b-prepare-notebook"),
            ("B2-labelonly", "thanhduy9a4tv/grace-b2-labelonly-validation"),
            ("B2-rep", "thanhduy9a4tv/grace-b2-rep-validation"),
        ]
        for arm, slug in thanh_runs:
            st = api_thanh.kernels_status(slug)
            st_val = str(getattr(st, 'status', st))
            msg = getattr(st, 'failure_message', '') or ''
            print(f"Account: thanhduy9a4tv  | Arm: {arm:<12} | Kernel: {slug:<42} | Status: {st_val} {msg}")
    except Exception as e:
        print(f"Error checking thanhduy9a4tv: {e}")

    print("========================================================================================")

if __name__ == '__main__':
    main()
