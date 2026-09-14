"""Exact phase-level encoding of the known-model unit simplex learner.

This mathematical decoder has no Runtime, constructor, resource, source or
installation authority. It does not change the registered CUDA backend.
"""
from dataclasses import dataclass,replace
from fractions import Fraction as F
from itertools import combinations,product
from pathlib import Path
import json
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'src/reference_compiler'),str(Path(__file__).resolve().parent)]
import simplex_gradient as native
from fp_reference.core import ContractError,natural
from fp_reference.learner import (SIMPLEX_GRADIENT,LearnerSpec,ReferenceLearnerState,
    initial_state,observe_event,commit_event)
from fp_reference.profile import attach_boundary
from fp_reference.semantics import ArithmeticUnresolved,Evaluation,evaluate


def world_count(n,cap):
    natural(n,'latent token count'); natural(cap,'decoder world allowance',positive=True)
    if n<2:
        raise ContractError('the declared relation family has at least two tokens')
    if n-1>=cap.bit_length() or (1<<(n-1))>cap:
        raise ArithmeticUnresolved('the declared decoder world allowance is insufficient')
    return 1<<(n-1)


def query(n,i,j,y=None):
    natural(i,'first token'); natural(j,'second token')
    if max(i,j)>=n:
        raise ContractError('query outside the complete declared token interface')
    if y is not None:
        natural(y,'observed target')
        if y>1:
            raise ContractError('target outside the binary readout')


@dataclass(frozen=True)
class CountState:
    n:int
    counts:tuple[int,...]
    pending:tuple[int,int,int]|None
    cursor:int
    steps:int

    def __post_init__(self):
        natural(self.n,'latent token count')
        natural(self.cursor,'actual namespace cursor'); natural(self.steps,'actual optimizer step count')
        if self.n<2 or type(self.counts) is not tuple or len(self.counts)!=self.n*(self.n-1)//2 or any(type(v) is not int for v in self.counts):
            raise ContractError('complete signed nonloop count vector required')
        if sum(abs(v) for v in self.counts)>self.steps:
            raise ContractError('committed counts exceed the actual number of commits')
        if self.pending is not None:
            if (type(self.pending) is not tuple or len(self.pending)!=3 or not self.cursor
                    or type(self.pending[2]) is not int):
                raise ContractError('one actual uncommitted observation is required')
            query(self.n,*self.pending)


def initialize(n,cursor=0,*,world_cap=64):
    world_count(n,world_cap)
    return CountState(n,(0,)*(n*(n-1)//2),None,cursor,0)


def observe(state,i,j,y):
    if state.pending is not None:
        raise ContractError('the previous full unit must commit first')
    query(state.n,i,j,y)
    return replace(state,pending=(i,j,y),cursor=state.cursor+1)


def commit(state):
    if state.pending is None:
        raise ContractError('no observed complete unit to commit')
    i,j,y=state.pending
    counts=list(state.counts)
    if i!=j:
        edge=tuple(sorted((i,j)))
        index=tuple(combinations(range(state.n),2)).index(edge)
        counts[index]+=1-2*y
    return replace(state,counts=tuple(counts),pending=None,steps=state.steps+1)


def attach(state,ordinary_cursor):
    natural(ordinary_cursor,'actual ordinary attachment cursor')
    if state.pending is not None:
        raise ContractError('profile attachment requires an empty accumulator')
    return replace(state,cursor=ordinary_cursor)


def weights(state,*,world_cap=64,bit_limit=32768):
    K=world_count(state.n,world_cap)
    natural(bit_limit,'decoder exact integer allowance',positive=True)
    # This guard precedes large powers. It is conservative, not an optimal
    # reference operation/space budget or a physical ownership certificate.
    if state.n+4*sum(abs(v) for v in state.counts)+8>bit_limit:
        raise ArithmeticUnresolved('the guarded exact decoder needs more integer precision')
    edges=tuple(combinations(range(state.n),2))
    worlds=tuple((0,)+tail for tail in product((0,1),repeat=state.n-1))
    scores=tuple(sum(d for d,(i,j) in zip(state.counts,edges) if z[i]==z[j]) for z in worlds)
    lowest=min(scores)
    integers=tuple(9**(s-lowest) for s in scores)
    total=sum(integers)
    assert len(integers)==K and max(v.bit_length() for v in (*integers,total))<=bit_limit
    return tuple(F(v,total) for v in integers)


def decode(state,**budgets):
    w=weights(state,**budgets)
    gradient=(F(0),)*(len(w)+1)
    if state.pending is not None:
        i,j,y=state.pending
        worlds=tuple((0,)+tail for tail in product((0,1),repeat=state.n-1))
        match=tuple(int(z[i]^z[j]==y) for z in worlds)
        mass=1+8*sum(p*b for p,b in zip(w,match))
        gradient=(1/mass-F(1,5),)+tuple(F(4,5)-8*b/mass for b in match)
    return ReferenceLearnerState((F(1),)+w,(),gradient,int(state.pending is not None),state.cursor,state.steps)


def prediction(state,i,j,**budgets):
    query(state.n,i,j)
    w=weights(state,**budgets)
    worlds=tuple((0,)+tail for tail in product((0,1),repeat=state.n-1))
    sources=tuple(F(token==(i,j)[side]) for side in (0,1) for token in range(state.n))
    pairs=tuple(F((a,b)==(i,j)) for a,b in product(range(state.n),repeat=2))
    indicators=tuple(F(z[i]^z[j]==y) for z in worlds for y in (0,1))
    excesses=tuple(8*sum((p for p,z in zip(w,worlds) if z[i]^z[j]==y),F(0)) for y in (0,1))
    masses=tuple(1+v for v in excesses)
    return Evaluation(sources+pairs+indicators+excesses,excesses,masses,F(10),tuple(v/10 for v in masses),())


def spec(n,rate=F(1),unit=1):
    return LearnerSpec(unit,rate,optimizer_id=SIMPLEX_GRADIENT,simplex_slots=tuple(range(1,world_count(n,64)+1)))


def native_initial(n,cursor=0):
    rules,graph,worlds=native.relation_graph(n)
    return initial_state(graph,rules,(F(1),)+(F(1,len(worlds)),)*len(worlds),cursor,spec=spec(n),bit_limit=32768)


def step(n,reference,encoded,event,counters):
    rules,graph,_=native.relation_graph(n)
    i,j,y=event
    before=evaluate(graph,rules,reference.theta,native.context(n,i,j),(),bit_limit=32768)
    assert prediction(encoded,i,j)==before
    counters['complete_native_caches']+=1
    reference=observe_event(graph,reference,spec(n),before,y,bit_limit=32768)
    encoded=observe(encoded,i,j,y)
    assert decode(encoded)==reference
    counters['observed_complete_states']+=1
    reference=commit_event(reference,spec(n),bit_limit=32768)
    encoded=commit(encoded)
    assert decode(encoded)==reference
    counters['committed_complete_states']+=1
    return reference,encoded


def exhaustive():
    counters={key:0 for key in ('initialized_states','complete_native_caches','observed_complete_states','committed_complete_states')}
    cases=[]
    for n,depth in ((2,3),(3,2)):
        alphabet=tuple(product(range(n),range(n),(0,1)))
        levels=[(native_initial(n),initialize(n))]
        assert decode(levels[0][1])==levels[0][0]
        counters['initialized_states']+=1
        total=1
        for _ in range(depth):
            following=[]
            for reference,encoded in levels:
                for event in alphabet:
                    following.append(step(n,reference,encoded,event,counters))
            total+=len(following); levels=following
        cases.append({'n':n,'histories':total})
    # A cycle, a path, diagonals and both query orientations at n4.
    patterns=(((0,1),(1,2),(2,0)),((0,1),(1,2),(2,3)),((0,0),(2,2),(3,3)),((0,1),(1,0),(0,1)))
    for pattern in patterns:
        for labels in product((0,1),repeat=3):
            reference,encoded=native_initial(4),initialize(4)
            assert decode(encoded)==reference; counters['initialized_states']+=1
            for (i,j),y in zip(pattern,labels):
                reference,encoded=step(4,reference,encoded,(i,j,y),counters)
    return {'counts':counters,'full_history_cases':cases,'n4_three_event_traces':32}


def profiles():
    counters={key:0 for key in ('complete_native_caches','observed_complete_states','committed_complete_states')}
    history=((0,1,0),(1,2,1),(0,2,0))
    checked=0
    for passes in (1,2,3):
        reference,encoded=native_initial(3),initialize(3)
        for event in history*passes:
            reference,encoded=step(3,reference,encoded,event,counters)
        reference=attach_boundary(reference,20,spec(3)); encoded=attach(encoded,20)
        assert decode(encoded)==reference and encoded.steps==3*passes and encoded.cursor==20
        for event in ((2,0,1),(0,0,0)):
            reference,encoded=step(3,reference,encoded,event,counters)
        checked+=1
    reference,encoded=native_initial(2,7),initialize(2,7)
    for event in ((0,1,0),)*50+((0,1,1),)*50:
        reference,encoded=step(2,reference,encoded,event,counters)
    assert encoded.counts==(0,) and encoded.cursor==107 and encoded.steps==100
    assert reference.theta==(F(1),F(1,2),F(1,2))
    return {'attached_profile_cases':checked,'profile_and_continuation_phase_checks':counters,
            'late_birth_reversal_events':100,'late_birth_final_clock':[107,100]}


def run_reference(history,*,rate=F(1),unit=1):
    rules,graph,_=native.relation_graph(2)
    learner=spec(2,rate,unit)
    state=native_initial(2)
    for i,j,y in history:
        p=evaluate(graph,rules,state.theta,native.context(2,i,j),(),bit_limit=32768)
        state=observe_event(graph,state,learner,p,y,bit_limit=32768)
        if state.unit_count==unit:
            state=commit_event(state,learner,bit_limit=32768)
    return state


def boundaries():
    event=lambda ys:tuple((0,1,y) for y in ys)
    fractional=tuple(run_reference(event(h),rate=F(1,2)).theta[1] for h in ((0,1),(1,0)))
    assert fractional==(F(77,170),F(93,170))
    batched=tuple(run_reference(event(h),unit=2).theta[1] for h in ((0,0,0,1),(0,1,0,0)))
    assert batched==(F(61,82),F(9,10))
    state=initialize(2)
    observed=observe(state,0,0,0)
    assert observed.counts==state.counts and decode(observed).theta==decode(state).theta
    assert decode(observed).gradient_sum==(F(-4,45),)*3 and decode(state).gradient_sum==(F(0),)*3
    failed=0
    for function in (lambda:commit(state),lambda:observe(observed,0,1,0),lambda:attach(observed,3),
                     lambda:decode(CountState(80,(0,)*3160,None,0,0)),
                     lambda:decode(CountState(2,(10**12,),None,10**12,10**12))):
        try:function()
        except (ContractError,ArithmeticUnresolved):failed+=1
        else:raise AssertionError('an invalid phase or unfunded decoder was accepted')
    return {'same_counts_fractional_rate_weights':list(map(str,fractional)),
            'same_counts_batched_weights':list(map(str,batched)),
            'pending_diagonal_gradient':'-4/45 in all slots; counts unchanged',
            'invalid_phase_or_decoder_refusals':failed}


if __name__=='__main__':
    report={'exhaustive':exhaustive(),'profiles':profiles(),'boundaries':boundaries(),
        'scope':'exact complete learner/cache encoding for the fixed unit-step fair-prior model; no Runtime/physical/installation authority'}
    assert 'torch' not in sys.modules
    print(json.dumps(report,indent=2))
