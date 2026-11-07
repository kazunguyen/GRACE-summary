import os
import sys
import time
import hashlib
import requests
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

DEST_FILE = Path("01_Author_Baseline_Unified/output/research_freeze_20261101/reveal/donors.tmp")
FINAL_FILE = Path("01_Author_Baseline_Unified/output/research_freeze_20261101/reveal/donors.jsonl")
EXPECTED_SHA256 = "6bf44ab86c8524d239e610fdccff5916cfc402fef7945d7cbe7f695e287abbce"
EXPECTED_TOTAL_BYTES = 1887092268

current_size = DEST_FILE.stat().st_size if DEST_FILE.is_file() else 0
print(f"Current local size: {current_size:,} bytes / {EXPECTED_TOTAL_BYTES:,} bytes ({current_size/EXPECTED_TOTAL_BYTES*100:.1f}%)")

if current_size < EXPECTED_TOTAL_BYTES:
    remaining_bytes = EXPECTED_TOTAL_BYTES - current_size
    print(f"Resuming download for remaining {remaining_bytes:,} bytes (~{remaining_bytes/1024**2:.1f} MB)...")
    url = "https://drive.usercontent.google.com/download?id=162syKwALRE2EvMbP5bBHA4P9eis30hjA&export=download&confirm=t"
    headers = {"Range": f"bytes={current_size}-"}
    
    start_time = time.time()
    downloaded_this_session = 0
    
    with requests.get(url, headers=headers, stream=True, timeout=30) as r:
        if r.status_code not in (200, 206):
            raise RuntimeError(f"HTTP error {r.status_code}: {r.text[:200]}")
        
        with open(DEST_FILE, "ab") as f:
            for chunk in r.iter_content(chunk_size=4 * 1024 * 1024):
                if chunk:
                    f.write(chunk)
                    downloaded_this_session += len(chunk)
                    current_total = current_size + downloaded_this_session
                    pct = current_total / EXPECTED_TOTAL_BYTES * 100
                    elapsed = time.time() - start_time
                    speed_mb = (downloaded_this_session / 1024**2) / max(elapsed, 0.001)
                    print(f"\rProgress: {current_total:,} / {EXPECTED_TOTAL_BYTES:,} bytes ({pct:.1f}%) | Speed: {speed_mb:.2f} MB/s", end="", flush=True)

    print(f"\nDownload finished in {time.time() - start_time:.1f}s!")

# Verify full file SHA-256
print("\nVerifying full file SHA-256 hash...")
h = hashlib.sha256()
line_count = 0
with open(DEST_FILE, "rb") as f:
    for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
        h.update(chunk)
actual_sha = h.hexdigest()
print(f"Calculated SHA-256: {actual_sha}")
print(f"Expected   SHA-256: {EXPECTED_SHA256}")

if actual_sha == EXPECTED_SHA256:
    print("SUCCESS: SHA-256 matches frozen specification 100%!")
    # Count lines
    with open(DEST_FILE, "r", encoding="utf-8") as f:
        for _ in f:
            line_count += 1
    print(f"Total verified donor lines: {line_count:,}")
    assert line_count == 17636, f"Expected 17,636 donors, got {line_count}"
    
    # Rename to final donors.jsonl
    if FINAL_FILE.is_file():
        FINAL_FILE.unlink()
    DEST_FILE.rename(FINAL_FILE)
    print(f"Renamed {DEST_FILE.name} -> {FINAL_FILE.name}")
    print("REVEAL DONORS ARE 100% READY!")
else:
    raise ValueError(f"SHA-256 mismatch! Got {actual_sha}, expected {EXPECTED_SHA256}")
