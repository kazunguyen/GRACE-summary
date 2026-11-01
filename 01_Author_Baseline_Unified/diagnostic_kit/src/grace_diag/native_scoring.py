"""Canonical unconstrained first-token scoring shared by every research arm.

Top-5 is diagnostic only. Both label logits must be available and finite.
Raw greedy validity and score validity are separate quantities.
"""
import hashlib
import math
from pathlib import Path

SCORING_POLICY = 'unconstrained_first_token_logits_v1'

def binary_scores(logits, label_ids):
    import numpy as np
    values=np.asarray(logits,dtype=np.float64).reshape(-1)
    if len(label_ids)!=2 or label_ids[0]==label_ids[1] or min(label_ids)<0 or max(label_ids)>=len(values):
        raise ValueError('Invalid binary token IDs')
    if not np.all(np.isfinite(values)):
        raise ValueError('Non-finite logits')
    normalizer=float(np.max(values)+np.log(np.exp(values-np.max(values)).sum()))
    lp0=float(values[label_ids[0]]-normalizer); lp1=float(values[label_ids[1]]-normalizer)
    s=float(np.exp(lp1-np.logaddexp(lp0,lp1)))
    top=np.argsort(values)[-5:][::-1]
    return {'logprob_0':lp0,'logprob_1':lp1,'p0':math.exp(lp0),'p1':math.exp(lp1),'s':s,
            'pred_argmax':int(s>=0.5),'greedy_token_id':int(np.argmax(values)),
            'top5':[{'token_id':int(i),'logprob':float(values[i]-normalizer)} for i in top]}

class NativeFirstTokenScorer:
    """llama-cpp-python backend, matching existing Kaggle B2 without grammar."""
    def __init__(self,cfg,cache_dir=None):
        from llama_cpp import Llama, __version__
        from transformers import AutoTokenizer
        from .llm_backend import ScoreResult
        self.cfg=cfg; self.ScoreResult=ScoreResult
        if __version__ != '0.3.16':
            raise ValueError('Research backend pinned to llama-cpp-python 0.3.16')
        if cfg.guided_choice or cfg.temperature!=0 or cfg.max_tokens!=1:
            raise ValueError('Canonical scoring requires greedy unconstrained first token')
        path=Path(cfg.model_path or '')
        h=hashlib.sha256()
        with path.open('rb') as f:
            for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
        if h.hexdigest()!=cfg.model_sha256: raise ValueError('Model SHA256 mismatch')
        self.tokenizer=AutoTokenizer.from_pretrained(cfg.tokenizer,revision=cfg.tokenizer_revision)
        self.llm=Llama(model_path=str(path),n_ctx=8192,n_batch=256,n_gpu_layers=-1,logits_all=True,seed=cfg.seed,verbose=False)
        self.label_ids=[]
        for label in ('0','1'):
            ids=self.tokenizer.encode(label,add_special_tokens=False)
            if len(ids)!=1 or ids!=self.llm.tokenize(label.encode(),add_bos=False,special=False):
                raise ValueError('Label tokenizer mismatch')
            self.label_ids.append(ids[0])

    def score(self,prompt,use_cache=True):
        import time
        start=time.monotonic()
        text=self.tokenizer.apply_chat_template([{'role':'user','content':prompt}],tokenize=False,add_generation_prompt=True)
        ids=self.tokenizer.encode(text,add_special_tokens=False)
        if ids!=self.llm.tokenize(text.encode(),add_bos=False,special=True): raise ValueError('Chat tokenizer mismatch')
        if len(ids)+64>8192: raise ValueError('Context overflow')
        self.llm.reset(); self.llm.eval(ids)
        scores=binary_scores(self.llm.scores[len(ids)-1],self.label_ids)
        raw=self.llm.detokenize([scores['greedy_token_id']]).decode('utf-8',errors='replace').strip()
        # No response cache: B2-rep always measures a fresh model evaluation.
        return self.ScoreResult(scores['s'],scores['p0'],scores['p1'],scores['pred_argmax'],True,raw,
                                {str(x['token_id']):x['logprob'] for x in scores['top5']},
                                {'prompt_tokens':len(ids),'completion_tokens':1},time.monotonic()-start,
                                logprob_0=scores['logprob_0'],logprob_1=scores['logprob_1'],response_valid=raw in ('0','1'))
