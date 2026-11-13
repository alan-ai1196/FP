#!/usr/bin/env python3
"""Read-only, exact source influence/projection diagnostic for a FROZEN binary table.

JSON input: {"n":2, "values":["1/2","1/3","2/3","1/2"]};
values are lexicographic binary order (00,01,10,11), exact rational strings.
Never a native FP constructor, compiler bridge, or learner-state equivalence.
"""
from __future__ import annotations
import argparse, json
from fractions import Fraction as F
from itertools import product
from pathlib import Path

def audit(n:int, strings:list[str], k:int):
    if n<1 or n>12: raise ValueError('n must be 1..12: exhaustive cube cost is explicit')
    if len(strings)!=(1<<n): raise ValueError('values length must be 2**n')
    if not (0<=k<=n): raise ValueError('k must be 0..n')
    cube=list(product((0,1),repeat=n))
    values=[F(t) for t in strings]
    f=dict(zip(cube,values))
    if not all(0<=v<=1 for v in values): raise ValueError('values must be conditional probabilities in [0,1]')
    imps=[]
    for i in range(n):
        squared=[]
        for x in cube:
            y=list(x);y[i]^=1
            squared.append((f[x]-f[tuple(y)])**2)
        imps.append(sum(squared,F(0))/(1<<n))
    S=sorted(sorted(range(n),key=lambda i: (-imps[i],i))[:k])
    groups={}
    for x in cube:
        key=tuple(x[i] for i in S)
        groups.setdefault(key,[]).append(f[x])
    means={key:sum(z,F(0))/len(z) for key,z in groups.items()}
    error=sum(((f[x]-means[tuple(x[i] for i in S)])**2 for x in cube),F(0))/(1<<n)
    bound=sum((imps[i] for i in range(n) if i not in S),F(0))/4
    assert error<=bound
    return {'n':n, 'selected':S, 'influences':[str(q) for q in imps],
            'uniform_mse':str(error), 'uniform_mse_bound':str(bound),
            'projection_values':{''.join(map(str,key)):str(val) for key,val in sorted(means.items())},
            'scope':'Frozen readout / independent uniform binary inputs only; no deployed or learner certificate.'}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,help='JSON file containing n and exact rational values')
    p.add_argument('--k',type=int,default=1,help='retain top-k bit-flip influence coordinates')
    args=p.parse_args()
    data=json.loads(args.input.read_text()) if args.input else {'n':2,'values':['1/2','1/3','2/3','1/2']}
    print(json.dumps(audit(data['n'],data['values'],args.k),indent=2,ensure_ascii=False))

if __name__=='__main__':
    main()
