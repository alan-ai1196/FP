from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Sequence, Tuple
from .core import ClaimContract, QueryError, require_finite, stable_hash
from .resources import CostRouter
from .data_usage import DataUsageLedger


def _quantize_registered(x:float, *, lo:float, hi:float, bits:int)->float:
    """Map a legal scalar query result to at most 2**bits registered levels.

    This makes the declared information payload operational rather than metadata.
    Endpoints are included.  For very large bits Python float has fewer distinct
    representable points; that only *reduces* the information alphabet.
    """
    x=require_finite(x,'query result')
    if x < lo or x > hi:
        raise QueryError(f'query result {x} outside registered range [{lo},{hi}]')
    levels=(1<<bits)-1
    # Avoid constructing giant intermediate arrays. Python integers are exact.
    t=(x-lo)/(hi-lo)
    q=round(t*levels)
    return require_finite(lo+(hi-lo)*(q/levels),'quantized query result')

@dataclass(frozen=True)
class QueryRecord:
    query_name:str; data_id:str; observation_ids:Tuple[str,...]; input_snapshot_id:str; precision_bits:int; output_dim:int; work_cost:float; memory_cost:float; success:bool; result_hash:str|None; error:str|None=None

class InformationInterface:
    def __init__(self, contract:ClaimContract, cost_router:CostRouter, data_usage:DataUsageLedger):
        self.contract=contract;self.cost_router=cost_router;self.ledger=cost_router.ledger_for('query');self.data_usage=data_usage;self.records=[]
    def query(self,name:str,*,data_id:str,observation_ids:Sequence[str],snapshot_id:str,fn:Callable[[],Sequence[float]|float])->Tuple[float,...]:
        if name not in self.contract.query_specs: raise QueryError(f'query {name!r} is not registered')
        spec=self.contract.query_specs[name];role=self.contract.data_role(data_id)
        if role not in spec.allowed_data_roles or not role.may_drive_compiler: raise QueryError(f'data role {role.value} cannot drive query {name}')
        obs=tuple(observation_ids)
        if spec.requires_observation_ids and not obs: raise QueryError('registered query requires explicit observation IDs')
        if len(set(obs))!=len(obs) or any(not x for x in obs): raise QueryError('query observation IDs must be unique/nonempty')
        # Seeing data makes it proposal/profile data even if the downstream query later fails.
        for oid in obs:self.data_usage.mark_proposal(oid,f'query:{name}:{snapshot_id}')
        self.cost_router.charge_work('query',{'work':spec.work_cost},f'query:{name}:{snapshot_id}')
        if spec.memory_cost:self.cost_router.charge_work('query',{'memory_work':spec.memory_cost},f'query-memory:{name}:{snapshot_id}')
        try:
            raw=fn(); vals_raw=(require_finite(raw,'query result'),) if isinstance(raw,(int,float)) and not isinstance(raw,bool) else tuple(require_finite(x,'query result') for x in raw)
            vals=tuple(_quantize_registered(x,lo=spec.output_lo,hi=spec.output_hi,bits=spec.precision_bits) for x in vals_raw)
            if len(vals)==0 or len(vals)>spec.max_output_dim:raise QueryError(f'query output dim {len(vals)} exceeds registered bound {spec.max_output_dim}')
            self.records.append(QueryRecord(name,data_id,obs,snapshot_id,spec.precision_bits,len(vals),spec.work_cost,spec.memory_cost,True,stable_hash(vals)));return vals
        except Exception as exc:
            self.records.append(QueryRecord(name,data_id,obs,snapshot_id,spec.precision_bits,0,spec.work_cost,spec.memory_cost,False,None,repr(exc)));raise
