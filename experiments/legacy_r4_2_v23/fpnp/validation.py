from __future__ import annotations
import hashlib
import numpy as np

VALIDATION_WINDOWS=4096
VALIDATION_SEED=0xF00D2026

def _token_count(tokens_or_count):
    return int(tokens_or_count if np.isscalar(tokens_or_count) else len(tokens_or_count))

def fixed_validation_positions(tokens_or_count,horizon:int=511,n:int=VALIDATION_WINDOWS):
    """Immutable held-out target positions shared by every compared program."""
    token_count=_token_count(tokens_or_count);lo=int(horizon);hi=int(token_count)
    if hi<=lo:raise ValueError('validation token file too short')
    m=min(int(n),hi-lo);rng=np.random.default_rng(VALIDATION_SEED)
    if m==hi-lo:pos=np.arange(lo,hi,dtype=np.int64)
    else:pos=np.sort(rng.choice(hi-lo,size=m,replace=False).astype(np.int64)+lo)
    return np.ascontiguousarray(pos,dtype=np.int64)

def validation_contract(tokens_or_count,horizon:int=511,n:int=VALIDATION_WINDOWS):
    """Hash both selected positions and, when supplied, their exact token windows."""
    token_count=_token_count(tokens_or_count);p=fixed_validation_positions(token_count,horizon,n)
    h=hashlib.sha256();h.update(np.asarray([token_count,horizon,VALIDATION_SEED,p.size],dtype=np.int64).tobytes());h.update(p.tobytes())
    out=dict(kind='fixed_shared_511-history_last-target_windows',token_count=token_count,horizon=int(horizon),examples=int(p.size),seed=int(VALIDATION_SEED),positions_sha256=h.hexdigest())
    if not np.isscalar(tokens_or_count):
        a=tokens_or_count;d=hashlib.sha256()
        # Hash exactly the examples consumed by both validation implementations.
        for pos in p:
            d.update(np.ascontiguousarray(a[int(pos)-horizon:int(pos)+1],dtype=np.uint16).tobytes())
        out['example_tokens_sha256']=d.hexdigest()
    return out
