"""Check extracted package files against MANIFEST_SHA256.json (files present only; absent = not extracted)."""
import hashlib
import json
import sys
from pathlib import Path

pkg, out = Path(sys.argv[1]), Path(sys.argv[2])
m = json.load(open(pkg / 'MANIFEST_SHA256.json', encoding='utf-8'))
ok = bad = absent = 0
bad_list = []
by_top = {}
for f in m['files']:
    p = pkg / f['path']
    top = f['path'].split('/')[0]
    if not p.exists():
        absent += 1
        by_top.setdefault(top, [0, 0, 0])[2] += 1
        continue
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    if h == f['sha256'] and p.stat().st_size == f['bytes']:
        ok += 1
        by_top.setdefault(top, [0, 0, 0])[0] += 1
    else:
        bad += 1
        bad_list.append(f['path'])
        by_top.setdefault(top, [0, 0, 0])[1] += 1
res = {'manifest_sha256': hashlib.sha256((pkg / 'MANIFEST_SHA256.json').read_bytes()).hexdigest(),
       'manifest_entries': len(m['files']), 'present_match': ok, 'present_mismatch': bad, 'not_extracted': absent,
       'mismatch_paths': bad_list, 'by_top_level_dir_match_mismatch_absent': by_top}
out.write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding='utf-8')
print(json.dumps({k: v for k, v in res.items() if k != 'by_top_level_dir_match_mismatch_absent'}, ensure_ascii=False))
for k, v in sorted(by_top.items()):
    print(f'{k:40} match={v[0]} mismatch={v[1]} absent={v[2]}')
sys.exit(1 if bad else 0)
