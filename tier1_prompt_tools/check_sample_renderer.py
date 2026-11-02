"""Verify one cached target per split with the actual cached Qwen tokenizer; no export."""
import json
from transformers import AutoTokenizer
from prepare_cached import BASELINE,cache_paths,rows,render_paired,TokenCounter
root=BASELINE/'output/local_full/bundles_recovered_joern_final_20261031'
tokenizer=AutoTokenizer.from_pretrained('Qwen/Qwen3-Coder-30B-A3B-Instruct',revision='b2cff646eb4bb1d68355c01b18ae02e7cf42d120',local_files_only=True)
c=TokenCounter(None);c.tok=tokenizer;c.approx=False
for d in ('devign','reveal'):
    for s in ('validation','test'):
        files,m=cache_paths(d,s,root)
        spec=next(rows(files['specs']))
        ref=next(r for r in rows(files['prompts']) if str(r['id'])==str(spec['id']))
        for arm in ('B1','B2-flip','B2-rep'):
            p,e=render_paired(arm,spec,ref['prompt'],c)
            assert len(tokenizer.apply_chat_template([{'role':'user','content':p}],tokenize=True,add_generation_prompt=True))+64<=8192
            if arm=='B2-rep': assert p==ref['prompt']
        print(d,s,'real tokenizer: B2 parity + B1/flip/rep OK',flush=True)
