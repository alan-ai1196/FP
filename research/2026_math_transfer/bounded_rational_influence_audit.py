#!/usr/bin/env python3
"""Passive exact tests of the 2026 conditional FP rational influence transfer.

No Foundation change, full native runtime, AMP, install, or model authority.
"""
from __future__ import annotations
from fractions import Fraction as F
from decimal import Decimal, localcontext
from itertools import product, combinations
from random import Random
from math import sqrt, pi

SEED=20261113
C_AA=8*sqrt(15)/(125*pi**4)

def dec(q):
    return Decimal(q.numerator)/Decimal(q.denominator)

def cube(n):
    return list(product((0,1),repeat=n))

def poly_eval(poly,x):
    return sum((v for term,v in poly.items() if all(x[i] for i in term)),F(0))

def poly_random(rng,n,d):
    p={():F(rng.randint(1,4),8)}
    terms=[term for k in range(1,d+1) for term in combinations(range(n),k)]
    rng.shuffle(terms)
    for term in terms[:min(len(terms),rng.randint(1,2*n+1))]:
        p[term]=F(rng.randint(1,6),rng.choice((4,8,16)))
    return p

def avg(xs):
    return sum(xs,F(0))/len(xs)

def var(f):
    m=avg(list(f.values()))
    return avg([(t-m)**2 for t in f.values()])

def influence(f,n):
    result=[]
    for i in range(n):
        vals=[]
        for x,v in f.items():
            y=list(x);y[i]^=1
            vals.append((v-f[tuple(y)])**2)
        result.append(avg(vals))
    return result

def transfer_trial(rng,n):
    d=min(3,n)
    P=poly_random(rng,n,d); R=poly_random(rng,n,d)
    pts=cube(n)
    p={x:poly_eval(P,x) for x in pts}
    q={x:p[x]+poly_eval(R,x) for x in pts}
    a=min(q.values());b=max(q.values())
    assert 0<a<=b
    f={x:p[x]/q[x] for x in pts}
    v=var(f); fi=influence(f,n)
    deg=max(map(len, [*P,*R]))
    assert deg>=1
    for m in (1,2,3,5,8,12,20,40):
        delta=(1-a/b)**m
        g={x:p[x]/b*sum(((1-q[x]/b)**k for k in range(m)),F(0)) for x in pts}
        assert all(0<=g[x]<=f[x]<=1 and f[x]-g[x]<=delta for x in pts)
        gi=influence(g,n);vg=var(g)
        with localcontext() as ctx:
            ctx.prec=90
            slack=Decimal('1e-65')
            assert dec(vg).sqrt()+slack >= max(Decimal(0),dec(v).sqrt()-dec(delta))
            assert all(dec(fi[i]).sqrt()+2*dec(delta)+slack>=dec(gi[i]).sqrt() for i in range(n))
        # External Aaronson-Ambainis theorem only sanity-tested, not re-proved.
        imported_lower=C_AA*float(vg)**2.5/(m*deg)**6
        assert max(map(float,gi))+1e-16>=imported_lower
        transfer_bound=max(0,sqrt(C_AA)*max(0,sqrt(float(v))-float(delta))**2.5/(m*deg)**3-2*float(delta))**2
        assert max(map(float,fi))+1e-16>=transfer_bound
    return 8

def projection_trial(rng,n):
    P=poly_random(rng,n,min(3,n));R=poly_random(rng,n,min(3,n))
    pts=cube(n)
    f={x:poly_eval(P,x)/(poly_eval(P,x)+poly_eval(R,x)) for x in pts}
    inf=influence(f,n)
    for mask in range(1<<n):
        S=[i for i in range(n) if mask>>i&1]
        groups={}
        for x in pts:
            groups.setdefault(tuple(x[i] for i in S),[]).append(f[x])
        means={k:avg(vals) for k,vals in groups.items()}
        err=avg([(f[x]-means[tuple(x[i] for i in S)])**2 for x in pts])
        bound=sum((inf[i] for i in range(n) if i not in S),F(0))/4
        assert err<=bound
    return 1<<n

def monotone_rectangles(n):
    checks=0
    for i in range(n):
        for j in range(n):
            legal={(('A',i,k),('B',k,j)) for k in range(n)}
            for am in range(1,1<<n):
                for bm in range(1,1<<n):
                    got={(('A',i,k),('B',t,j)) for k in range(n) if am>>k&1
                                                    for t in range(n) if bm>>t&1}
                    if got<=legal: assert len(got)==1
                    checks+=1
    return checks

def main():
    rng=Random(SEED)
    t=0;p=0;r=0
    for n in range(2,7):
        for _ in range(6):
            t+=transfer_trial(rng,n)
        p+=projection_trial(rng,n)
    for n in range(1,6):
        r+=monotone_rectangles(n)
    print('PASS: 240 rational geometric transfer cases, 124 uniform-cube projection cases, 28103 monotone rectangles')
    print(f'SEED={SEED}; transfer_cases={t}; projections={p}; rectangle_checks={r}')
    assert (t,p,r)==(240,124,28103)

if __name__=='__main__':
    main()
