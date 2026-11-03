#!/usr/bin/env python3
import hashlib
import json
import shutil
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parents[1]
GRACE_ROOT = REPO_ROOT.parent / "GRACE"

data_specs = REPO_ROOT / "data" / "specs"
data_specs.mkdir(parents=True, exist_ok=True)
data_manifests = REPO_ROOT / "data" / "manifests"
data_manifests.mkdir(parents=True, exist_ok=True)

files_to_sync = [
    # data/specs
    (GRACE_ROOT / "data/specs/devign_validation.jsonl", data_specs / "devign_validation.jsonl"),
    (GRACE_ROOT / "data/specs/devign_test.jsonl", data_specs / "devign_test.jsonl"),
    (GRACE_ROOT / "data/specs/reveal_validation.jsonl", data_specs / "reveal_validation.jsonl"),
    (GRACE_ROOT / "data/specs/reveal_test.jsonl", data_specs / "reveal_test.jsonl"),
    (GRACE_ROOT / "data/specs/devign_val_subset600.jsonl", data_specs / "devign_val_subset600.jsonl"),
    (GRACE_ROOT / "data/specs/reveal_val_subset600.jsonl", data_specs / "reveal_val_subset600.jsonl"),
    # data/manifests
    (GRACE_ROOT / "data/manifests/devign_donor_clean.jsonl", data_manifests / "devign_donor_clean.jsonl"),
    (GRACE_ROOT / "data/manifests/reveal_donor_clean.jsonl", data_manifests / "reveal_donor_clean.jsonl"),
]

for src, dst in files_to_sync:
    if src.exists():
        if not dst.exists() or src.stat().st_size != dst.stat().st_size:
            print(f"Copying {src.name} -> {dst}...")
            shutil.copy2(src, dst)
        h = hashlib.sha256(dst.read_bytes()).hexdigest()
        print(f"[OK] {dst.relative_to(REPO_ROOT)}: {h}")
    else:
        print(f"[ERROR] Missing source: {src}")

print("Sync completed.")
