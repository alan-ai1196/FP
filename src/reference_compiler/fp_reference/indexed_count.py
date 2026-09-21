"""Exact count coordinates of the fixed unit-simplex relation learner.

Passive immutable data and phase maps; authority belongs to Runtime.
"""
from dataclasses import dataclass, replace
from itertools import combinations
from .core import ContractError, natural
from .semantics import ArithmeticUnresolved


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
