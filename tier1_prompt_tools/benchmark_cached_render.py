"""Compare old/new rendering on real cached samples without exporting prompts."""
import time
from itertools import islice
from transformers import AutoTokenizer
from prepare_cached import BASELINE,rows,TokenCounter,render_paired,render_paired_slow

tok=AutoTokenizer.from_pretrained('Qwen/Qwen3-Coder-30B-A3B-Instruct',revision='b2cff646eb4bb1d68355c01b18ae02e7cf42d120',local_files_only=True)
c=TokenCounter(None);c.tok=tok;c.approx=False
folder=BASELINE/'output/local_full/bundles_recovered_joern_final_20261031/devign/validation'
refs={str(r['id']):r for r in rows(folder/'prompts.jsonl')}
slow=fast=0
for s in islice(rows(folder/'specs.jsonl'),5):
    r=refs[str(s['id'])]
    t=time.perf_counter(); p,_=render_paired_slow('B1',s,r['prompt'],c); slow+=time.perf_counter()-t
    t=time.perf_counter(); q,_=render_paired('B1',s,r['prompt'],c,reference=r); fast+=time.perf_counter()-t
    assert p==q
    print(s['id'],'identical B1 prompt',flush=True)
print(f'5 samples: old={slow:.3f}s new={fast:.3f}s speedup={slow/max(fast,1e-9):.1f}x',flush=True)
