"""Stage 1: embed raw train/validation/test only, with resumable batch checkpoints."""
import argparse
try:
    import fcntl
except ImportError:
    fcntl = None
import hashlib
import json
import os
import time
from pathlib import Path
import numpy as np
from embedding_engine import CodeT5Embedder

MODEL = 'Salesforce/codet5-base@02cd2d31bb7c6d0e4d91156167b2de044989c733'
def code_hash(code):
    return hashlib.sha256(code.encode('utf-8')).hexdigest()

def read_codes(path):
    rows = []
    seen = set()
    with Path(path).open(encoding='utf-8') as f:
        for line in f:
            if not line.strip(): continue
            row = json.loads(line)
            key = str(row['id'])
            if key in seen: raise ValueError('Duplicate ID: ' + key)
            seen.add(key)
            code = str(row['func']).strip()
            if not code: raise ValueError('Empty code: ' + key)
            rows.append((key, code))
    return rows

def save_json(path, value):
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False), encoding='utf-8')
    os.replace(tmp, path)

class CachedEmbedder:
    """Read-only lookup; never loads CodeT5 or computes missing embeddings."""
    def __init__(self, directory):
        self.lookup = {}
        self.arrays = []
        for split in ('train', 'validation', 'test'):
            root = Path(directory) / split
            meta = json.loads((root / 'manifest.json').read_text())
            if meta['model'] != MODEL or meta['completed'] != len(meta['rows']):
                raise ValueError(f'Incomplete/incompatible cache: {root}')
            vectors = np.load(root / 'vectors.npy', mmap_mode='r')
            if vectors.shape != (len(meta['rows']), 768) or vectors.dtype != np.float32:
                raise ValueError(f'Invalid cache shape/dtype: {root}')
            self.arrays.append(vectors)
            for i, row in enumerate(meta['rows']):
                self.lookup.setdefault(row['code_sha256'], (vectors, i))
    def encode(self, codes, batch_size=16):
        if not codes: return np.empty((0, 768), dtype=np.float32)
        result = []
        for code in codes:
            key = code_hash(code)
            if key not in self.lookup: raise ValueError('Code missing/stale embedding cache: ' + key)
            vectors, i = self.lookup[key]
            result.append(vectors[i])
        return np.asarray(result, dtype=np.float32)

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--raw-dir', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--batch-size', type=int, default=64)
    args = ap.parse_args()
    if args.batch_size < 1: ap.error('batch-size must be positive')
    args.out.mkdir(parents=True, exist_ok=True)
    lock = (args.out / '.lock').open('a')
    if fcntl is not None:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    embedder = None
    for split in ('train', 'validation', 'test'):
        rows = read_codes(args.raw_dir / (split + '.jsonl'))
        if not rows: raise ValueError('Empty split: ' + split)
        identity = [{'id': key, 'code_sha256': code_hash(code)} for key, code in rows]
        root = args.out / split
        root.mkdir(parents=True, exist_ok=True)
        manifest = root / 'manifest.json'
        if manifest.exists():
            meta = json.loads(manifest.read_text())
            if meta['model'] != MODEL or meta['rows'] != identity:
                raise ValueError(f'Stale cache, use a new output directory: {root}')
            vectors = np.load(root / 'vectors.npy', mmap_mode='r+')
            if vectors.shape != (len(rows), 768) or vectors.dtype != np.float32:
                raise ValueError('Invalid cache array')
        else:
            vectors = np.lib.format.open_memmap(root / 'vectors.npy', mode='w+', dtype=np.float32, shape=(len(rows), 768))
            meta = {'model': MODEL, 'max_length': 512, 'pooling': 'masked_mean', 'rows': identity, 'completed': 0}
            save_json(manifest, meta)
        start = meta['completed']
        if not 0 <= start <= len(rows): raise ValueError('Invalid checkpoint')
        if start == len(rows):
            print(f'{split}: cache complete {start}/{len(rows)}', flush=True)
            continue
        if embedder is None: embedder = CodeT5Embedder()
        began = time.monotonic()
        for i in range(start, len(rows), args.batch_size):
            batch = rows[i:i + args.batch_size]
            vectors[i:i + len(batch)] = embedder.encode([code for _, code in batch], batch_size=args.batch_size)
            vectors.flush()
            meta['completed'] = i + len(batch)
            save_json(manifest, meta)
            rate = (meta['completed'] - start) / (time.monotonic() - began)
            eta = (len(rows) - meta['completed']) / max(rate, 1e-9)
            print(f'{split}: {meta["completed"]}/{len(rows)} ({100*meta["completed"]/len(rows):.1f}%) | {rate:.2f} samples/s | ETA {eta/60:.1f} min', flush=True)

if __name__ == '__main__': main()
