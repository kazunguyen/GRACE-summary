"""Independent sklearn cross-check of locked validation thresholds (never reads test)."""
import json,math
from pathlib import Path
from sklearn.metrics import matthews_corrcoef
from validation_lock import RULES,file_sha256
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
data=json.loads((HERE/'thresholds.json').read_text(encoding='utf-8'))
for key,e in data['entries'].items():
    merged={}
    for src in e['source_evidence']:
        p=ROOT/src['path']
        assert p.parent.name=='validation' and file_sha256(p)==src['records_sha256']
        for line in p.read_text(encoding='utf-8').splitlines():
            r=json.loads(line);assert r['split']=='validation';merged[r['id']]=r
    valid=[r for r in merged.values() if r['valid'] and math.isfinite(r['s'])]
    y=[r['label'] for r in valid];scores=[r['s'] for r in valid]
    best_t=.5;best=None
    for tau in RULES['grid']:
        pred=[int(v>=tau) for v in scores]
        if len(set(pred))<2:continue
        value=float(matthews_corrcoef(y,pred))
        if best is None or value>best+1e-9 or (abs(value-best)<=1e-9 and (abs(tau-.5),tau)<(abs(best_t-.5),best_t)):best_t,best=tau,value
    assert best_t==e['tau']
    assert best is None and e['validation_mcc'] is None or abs(best-e['validation_mcc'])<1e-12
    print(key,'tau',e['tau'],'MCC',e['validation_mcc'],'verified by sklearn')
