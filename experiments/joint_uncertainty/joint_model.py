"""RN-5 registered cases; reuse the audited adaptive posterior and score algebra."""
from itertools import product
from pathlib import Path
import random
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'experiments/adaptive_uncertainty'))
from adaptive_model import (AdaptivePosterior,score,context,counts_from_training,
    unseen_pairs,exact_audit,diagnostic_cases,data as previous_data)

RATES=('1','4')
STRESS=(8,'iid-stress-c4',20)


def new_cases():
    return tuple((n,'iid-c'+str(c),seed) for c,seeds in ((2,(16,17)),(4,(18,19)))
                 for n in (8,16) for seed in seeds)


def cases():
    return diagnostic_cases()+new_cases()+(STRESS,)


def tasks():
    return tuple((kind,case,rate) for case in cases()
        for kind,rate in (tuple(('FP',rate) for rate in RATES)
            + (() if case in diagnostic_cases() else (('posterior','none'),))))


def support(case):
    assert case in cases()
    n,law,_=case
    c=2 if law.startswith('disconnected') else int(law.rsplit('c',1)[1])
    return tuple((i,i+1) for i in range(n-1) if (i+1)%(n//c))


def data(case):
    if case in diagnostic_cases():
        return previous_data(case)
    n,law,seed=case
    edges=support(case)
    if case==STRESS:
        # A declared low-probability IID-likelihood tape, selected as a
        # diagnostic. This is not a fresh IID population sample.
        hidden=(0,)*n
        train=tuple((i,j,int(repetition>=(4 if edge==0 else 9)))
            for edge,(i,j) in enumerate(edges) for repetition in range(10))
    else:
        rng=random.Random(2026091300+100*n+seed)
        hidden=tuple(rng.randrange(2) for _ in range(n))
        noise=random.Random(2026091400+100*n+seed)
        train=tuple((i,j,(hidden[i]^hidden[j])^int(noise.randrange(10)==0))
            for i,j in edges for _ in range(10))
    pairs=list(product(range(n),repeat=2))
    random.Random(2026091600+100*n+seed).shuffle(pairs)
    noise=random.Random(2026091500+100*n+seed)
    evaluation=tuple((i,j,(hidden[i]^hidden[j])^int(noise.randrange(10)==0)) for i,j in pairs)
    return hidden,edges,train,evaluation
