from __future__ import annotations
from pathlib import Path
import numpy as np

VOCAB=50257
HORIZON=511

class TokenFile:
    def __init__(self,path:Path,vocab:int=VOCAB):
        self.path=Path(path); self.a=np.memmap(self.path,dtype=np.uint16,mode='r')
        self.vocab=vocab
        if self.a.size<4096: raise RuntimeError(f'token file too small: {path}')
        sample=np.asarray(self.a[:min(self.a.size,1_000_000)])
        if int(sample.max())>=vocab: raise RuntimeError(f'token id >= vocab in {path}; expected uint16 GPT-2 compatible token file')
    def __len__(self): return int(self.a.size)

class SequentialCursor:
    def __init__(self,tokens:TokenFile,horizon=HORIZON,start=None):
        self.tokens=tokens;self.h=horizon;self.pos=max(horizon,int(start or horizon));self.epoch=0
    def clone(self):
        c=SequentialCursor(self.tokens,self.h,self.pos);c.epoch=self.epoch;return c
    def next_range(self,n:int):
        n=int(n)
        if n<=0 or n>len(self.tokens)-self.h:raise ValueError(f'invalid sequential chunk {n} for token file length {len(self.tokens)} and horizon {self.h}')
        if self.pos+n>len(self.tokens):
            self.pos=self.h;self.epoch+=1
        s=self.pos;self.pos+=n
        return s,n
    def context_targets(self,start,n):
        a=self.tokens.a
        return np.asarray(a[start-self.h:start+n]),np.asarray(a[start:start+n])

class BlockPermutationBatcher:
    def __init__(self,tokens:TokenFile,seq=512,micro=16,seed=1337):
        self.t=tokens;self.seq=seq;self.micro=micro;self.rng=np.random.default_rng(seed)
        self.max_start=len(tokens)-seq-2
    def next_cpu(self):
        starts=self.rng.integers(0,self.max_start,size=self.micro,dtype=np.int64)
        x=np.empty((self.micro,self.seq),np.int64);y=np.empty_like(x)
        a=self.t.a
        for i,s in enumerate(starts):
            chunk=np.asarray(a[s:s+self.seq+1],dtype=np.int64);x[i]=chunk[:-1];y[i]=chunk[1:]
        return x,y
