"""Exact synthetic attainability audit for the fixed-sign real relaxation.

This reads no target tape and constructs no legal Runtime parameter state.
Rational excesses below specify real amplitudes by a quadratic equation;
they are not claimed to be reachable initializer/profile endpoints.
"""
from fractions import Fraction as F
from itertools import product
import json
from math import prod
import sys


def construction(residual_counts, epsilon):
    c=len(residual_counts)
    assert c>=2 and 0<epsilon<F(1,2)
    rho=tuple(F(a-b,a+b) for a,b in residual_counts)
    worlds=tuple((1,)+tail for tail in product((-1,1),repeat=c-1))
    K=len(worlds)
    independent=lambda z:prod((1+r*s)/2 for r,s in zip(rho,z))
    pi=tuple((1-2*epsilon)*(independent(z)+independent(tuple(-s for s in z)))
        +2*epsilon/K for z in worlds)
    # T=1/epsilon makes every excess nonnegative. A real amplitude is
    # (sqrt(1+4*w)-1)/2; this need not be a legal reference scalar.
    excess=tuple(p/epsilon-F(2,K) for p in pi)
    W=sum((a+b)**2 for a,b in residual_counts)
    L=sum(a*a+b*b for a,b in residual_counts)
    q_in=epsilon+(1-2*epsilon)*F(L,W)
    scale=(2*q_in-1)/(1-q_in)
    return worlds,pi,excess,scale


def likelihood(residual_counts, epsilon, inside, cross):
    """Exponentiated negative expected loss, with a common integer power."""
    numerator,denominator=epsilon.numerator,epsilon.denominator
    value=F(1)
    # Enumerate individual residual bits independently of the block formulas.
    residuals=[(0,)*a+(1,)*b for a,b in residual_counts]
    for C,D in product(range(len(residuals)),repeat=2):
        p=inside if C==D else cross[C,D]
        for e,f in product(residuals[C],residuals[D]):
            preferred=p if e==f else 1-p
            value*=preferred**(denominator-numerator)*(1-preferred)**numerator
    return value


def audit():
    types=tuple((a,size-a) for size in (1,2) for a in range(size+1))
    mixtures=coordinates=blocks=likelihood_checks=0
    for c in (2,3,4):
        for counts,epsilon in product(product(types,repeat=c),(F(1,10),F(1,4))):
            worlds,pi,w,t=construction(counts,epsilon)
            K=len(worlds);T=2+sum(w)
            assert sum(pi)==1 and min(pi)>=2*epsilon/K>0
            assert min(w)>=0 and T==1/epsilon and t>=0
            assert all(1+4*v>=1 for v in w)
            residuals=[(0,)*a+(1,)*b for a,b in counts]
            inside=(1+t)/(2+t)
            pooled=[int(e==f) for group in residuals for e,f in product(group,repeat=2)]
            target_inside=epsilon+(1-2*epsilon)*F(sum(pooled),len(pooled))
            assert inside==target_inside>=F(1,2)
            cross={}
            for C,D in product(range(c),repeat=2):
                if C==D:
                    continue
                matching=tuple(k for k,z in enumerate(worlds) if z[C]==z[D])
                Q=(1+sum(w[k] for k in matching))/T
                assert Q==sum(pi[k] for k in matching)
                bits=[int(e==f) for e,f in product(residuals[C],residuals[D])]
                target=epsilon+(1-2*epsilon)*F(sum(bits),len(bits))
                assert Q==target and epsilon<=Q<=1-epsilon
                cross[C,D]=Q;blocks+=1
            optimum=likelihood(counts,epsilon,inside,cross)
            neutral=F(1,2)**(epsilon.denominator*sum(map(len,residuals))**2)
            assert optimum>=neutral
            # A nonuniform positive orientation mixture is a second actual
            # relaxed competitor. It uses the same shared internal scale.
            alternative=tuple(F(k+1,K*(K+1)//2) for k in range(K))
            alternative_cross={(C,D):sum(p for z,p in zip(worlds,alternative) if z[C]==z[D])
                for C,D in cross}
            assert optimum>=likelihood(counts,epsilon,F(9,10),alternative_cross)
            mixtures+=1;coordinates+=K;likelihood_checks+=2
    # Independent block optima need not be jointly consistent in general.
    # Three binary orientations cannot disagree on all three edges.
    assert {sum(z[i]==z[j] for i,j in ((0,1),(0,2),(1,2)))
        for z in product((-1,1),repeat=3)}=={1,3}
    assert 3*F(1,10)<1
    diagnostic=((1,1),(2,0),(2,0),(2,0))
    worlds,pi,w,t=construction(diagnostic,F(1,10))
    assert sorted(pi)==[F(1,40)]*6+[F(17,40)]*2
    assert sorted(w)==[F(0)]*6+[F(4)]*2 and t==3
    assert mixtures==1550 and blocks==16600 and 'torch' not in sys.modules
    return {'synthetic_real_relaxation_optima':mixtures,
        'exact_orientation_probabilities':coordinates,
        'jointly_attained_ordered_cross_blocks':blocks,
        'exact_likelihood_comparisons':likelihood_checks,
        'incompatible_arbitrary_block_target_counterexample':'three equal-parity probabilities 1/10 have sum below 1',
        'registered_diagnostic_algebra':{'orientation_probabilities':list(map(str,sorted(pi))),
            'polynomial_excesses':list(map(str,sorted(w))),'internal_scale':str(t)},
        'scope':'fixed-state real relaxation; no target forecasts, legal scalar state, resource certificate or prequential optimum'}


if __name__=='__main__':
    print(json.dumps(audit(),indent=2))
