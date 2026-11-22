"""Infer deterministic one-bit actions from observable next-token probability blocks."""
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction as F

from learner import FitWork, solve


def determinant(m):
    return m[0][0]*m[1][1] - m[0][1]*m[1][0]


@dataclass
class Blocks:
    anchor: tuple
    basis: list
    counts: list
    initial: F


def moments(tokens, alphabet):
    n=len(tokens)-2
    if n<1:
        return None
    previous,middle,pairs=Counter(),Counter(),Counter()
    for t in range(1,len(tokens)-1):
        p,a=tokens[t-1],tokens[t]
        previous[p]+=1
        middle[a]+=1
        pairs[p,a]+=1
    # Departures from independence sum to zero. A nonzero table has a positive entry.
    best=0
    anchor=None
    for (p,s),count in pairs.items():
        covariance=n*count-previous[p]*middle[s]
        if covariance>best or (covariance==best and covariance>0 and (p,s)<anchor):
            best,anchor=covariance,(p,s)
    if anchor is None:
        return None
    p,s=anchor
    basis=[[n,middle[s]],[previous[p],pairs[p,s]]]
    counts=[[[0,0],[0,0]] for _ in range(alphabet)]
    for t in range(1,len(tokens)-1):
        before,a,after=tokens[t-1],tokens[t],tokens[t+1]
        m=counts[a]
        m[0][0]+=1
        m[0][1]+=after==s
        m[1][0]+=before==p
        m[1][1]+=(before==p and after==s)
    return Blocks(anchor,basis,counts,F(middle[s],n))


def ratios(blocks):
    denominator=determinant(blocks.basis)
    return tuple(F(determinant(m),denominator) for m in blocks.counts)


def operators(blocks):
    work=FitWork()
    return [solve(blocks.basis,m,work) for m in blocks.counts],work


def observation(current, op):
    mass=op[0][0]+current*op[1][0]
    joint=op[0][1]+current*op[1][1]
    return mass, joint


def exact_closure(blocks):
    """Test the synchronizing, irreducible, full-support class in a known rank-two realization."""
    if blocks is None:
        return None,"no rank-two anchor"
    reset=next((i for i,r in enumerate(ratios(blocks)) if not r),None)
    if reset is None:
        return None,"no singular letter"
    ops,_=operators(blocks)
    mass,joint=observation(blocks.initial,ops[reset])
    if mass <= 0 or not 0 <= joint <= mass:
        return None, "invalid reset probability"
    states=[joint/mass]
    transitions=[]
    emissions=[]
    for z in states:
        row=[]
        probabilities=[]
        for op in ops:
            mass,joint=observation(z,op)
            if mass<=0 or not 0<=joint<=mass:
                return None,"invalid reachable probability"
            target=joint/mass
            if target not in states:
                states.append(target)
                if len(states)>2:
                    return None,"third distinct post-reset forecast"
            row.append(states.index(target))
            probabilities.append(mass)
        if sum(probabilities)!=1:
            return None,"unnormalized emission row"
        transitions.append(row)
        emissions.append(probabilities)
    if len(states)!=2 or 1 not in transitions[0] or 0 not in transitions[1]:
        return None,"two recurrent states required"
    mixture=(blocks.initial-states[0])/(states[1]-states[0])
    if not 0<=mixture<=1:
        return None,"initial forecast outside the two-state interval"
    next_second = sum(weight * emissions[i][a]
                      for i, weight in enumerate((1-mixture, mixture))
                      for a, destination in enumerate(transitions[i]) if destination == 1)
    if next_second != mixture:
        return None, "initial two-state mixture is nonstationary"
    return dict(actions=tuple(zip(*transitions,strict=True)),emissions=emissions,
                initial_second=mixture,coordinates=states),"closed"


def discover(tokens, blocks, emission_floor):
    if blocks is None:
        return None
    scores=ratios(blocks)
    resets=[a for a,r in enumerate(scores) if abs(r)<=emission_floor**2/2]
    if not resets or any(not m[0][0] for m in blocks.counts):
        return None
    z=max(resets,key=lambda a:blocks.counts[a][0][0])
    s=blocks.anchor[1]
    single={a:F(blocks.counts[a][0][1],blocks.counts[a][0][0]) for a in resets}
    totals=Counter()
    hits=Counter()
    for t in range(1,len(tokens)-1):
        before,a,after=tokens[t-1],tokens[t],tokens[t+1]
        if before==z:
            totals[a]+=1
            hits[a]+=after==s
    if len(totals)!=len(scores):
        return None
    points=[single[z],*(F(hits[a],n) for a,n in totals.items())]
    lo,hi=min(points),max(points)
    if lo==hi:
        return None
    actions=[]
    for a,r in enumerate(scores):
        if a in single:
            bit=int(abs(single[a]-hi)<abs(single[a]-lo))
            actions.append((bit,bit))
        else:
            actions.append((0,1) if r>0 else (1,0))
    if not all(any(op[i]==1-i for op in actions) for i in (0,1)):
        return None
    return tuple(actions)


def emission_counts(tokens, actions, state=None):
    """A pending initial state becomes known on the first identified reset."""
    counts=[[0]*len(actions) for _ in range(2)]
    skipped=0
    for a in tokens:
        left,right=actions[a]
        if state is None:
            skipped+=1
            if left==right:
                state=left
        else:
            counts[state][a]+=1
            state=actions[a][state]
    return counts,state,skipped


def smoothed(counts):
    probabilities = []
    for row in counts:
        denominator = sum(row) + len(row)
        probabilities.append(tuple(F(n+1, denominator) for n in row))
    return tuple(probabilities)
