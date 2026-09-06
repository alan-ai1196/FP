from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Callable, Dict, Mapping, Sequence
from types import MappingProxyType
import copy
import math

from .core import ContractError, require_finite, stable_hash


@dataclass
class CompleteLearnerState:
    lineage_id: str
    cursor: int
    physical_lineage_id: str | None = None
    theta: Dict[str,float]=field(default_factory=dict)
    optimizer_state: Dict[str,float]=field(default_factory=dict)
    accumulator_state: Dict[str,float]=field(default_factory=dict)
    causal_state: Dict[str,float]=field(default_factory=dict)
    rng_state: Any=None
    semantic_graph_id: str=""
    encoding_id: str="reference"
    lowering_id: str="reference"
    optimizer_impl_id: str="registered-optimizer"
    causal_schema_id: str="registered-causal-schema"
    initializer_id: str="registered-initializer"
    profiler_id: str="registered-profile"

    def __post_init__(self)->None:
        if not self.lineage_id or self.cursor<0: raise ContractError("invalid learner lineage/cursor")
        if self.physical_lineage_id is None: self.physical_lineage_id=self.lineage_id
        if not self.physical_lineage_id: raise ContractError('physical_lineage_id required')
        for group_name,group in (("theta",self.theta),("optimizer",self.optimizer_state),("accumulator",self.accumulator_state),("causal",self.causal_state)):
            for k,v in group.items(): require_finite(v,f"{group_name}[{k}]")

    def clone(self)->"CompleteLearnerState": return copy.deepcopy(self)

    @property
    def state_id(self)->str:
        return stable_hash({"lineage":self.lineage_id,"physical_lineage":self.physical_lineage_id,"cursor":self.cursor,"theta":self.theta,"optimizer":self.optimizer_state,
                            "accumulator":self.accumulator_state,"causal":self.causal_state,"rng":repr(self.rng_state),"graph":self.semantic_graph_id,
                            "encoding":self.encoding_id,"lowering":self.lowering_id,"optimizer_impl":self.optimizer_impl_id,
                            "causal_schema":self.causal_schema_id,"initializer":self.initializer_id,"profiler":self.profiler_id})


@dataclass(frozen=True)
class PredictionView:
    lineage_id: str
    physical_lineage_id: str
    cursor: int
    theta: Mapping[str,float]
    optimizer_state: Mapping[str,float]
    causal_state: Mapping[str,float]
    rng_state: Any
    semantic_graph_id: str
    encoding_id: str
    lowering_id: str
    optimizer_impl_id: str
    causal_schema_id: str

    @classmethod
    def from_state(cls,s:CompleteLearnerState)->"PredictionView":
        # Deep copies + mapping proxies prevent the forward callback from mutating
        # the live learner or observing target-derived accumulator state.
        return cls(s.lineage_id,s.physical_lineage_id,s.cursor,
                   MappingProxyType(copy.deepcopy(s.theta)),MappingProxyType(copy.deepcopy(s.optimizer_state)),MappingProxyType(copy.deepcopy(s.causal_state)),copy.deepcopy(s.rng_state),
                   s.semantic_graph_id,s.encoding_id,s.lowering_id,s.optimizer_impl_id,s.causal_schema_id)

@dataclass(frozen=True)
class CandidateBuildRecord:
    chi:str
    base_lineage_id:str
    birth_cursor:int
    candidate_lineage_id:str
    resource_owner_id:str
    build_snapshot_id:str
    transport_kind:str
    initializer_id:str
    profiler_id:str
    proposal_observation_ids:tuple[str,...]
    safety_certificate_id:str
    semantic_graph_id:str
    encoding_id:str
    lowering_id:str
    authority_id:str
    signature:str

    def __post_init__(self):
        if self.birth_cursor<0 or not all([self.chi,self.base_lineage_id,self.candidate_lineage_id,self.resource_owner_id,self.build_snapshot_id,self.transport_kind,self.initializer_id,self.profiler_id,self.safety_certificate_id,self.authority_id,self.signature]):
            raise ContractError('incomplete candidate build record')
        if len(set(self.proposal_observation_ids))!=len(self.proposal_observation_ids): raise ContractError('duplicate proposal observation IDs in build record')


@dataclass(frozen=True)
class EventResult:
    prediction: Any
    loss: float
    cursor_before: int
    cursor_after: int


class RegisteredLearner:
    """Reference causal event-order executor.

    Forward receives only PredictionView, which excludes the target-derived
    accumulator. Callback side effects are checked so current-unit target
    information cannot leak into prediction-visible state before commit.
    """
    def __init__(self, predict_fn:Callable[[PredictionView,Any],Any], score_fn:Callable[[Any,Any],float],
                 causal_update_fn:Callable[[CompleteLearnerState,Any,Any],None],
                 optimizer_accumulate_fn:Callable[[CompleteLearnerState,Any,Any,Any],None],
                 optimizer_commit_fn:Callable[[CompleteLearnerState],None], update_unit:int=1):
        if update_unit<=0: raise ContractError("update_unit must be positive")
        self.predict_fn=predict_fn; self.score_fn=score_fn; self.causal_update_fn=causal_update_fn
        self.optimizer_accumulate_fn=optimizer_accumulate_fn; self.optimizer_commit_fn=optimizer_commit_fn; self.update_unit=update_unit

    @staticmethod
    def _restore(dst:CompleteLearnerState,src:CompleteLearnerState)->None:
        dst.__dict__.clear(); dst.__dict__.update(copy.deepcopy(src.__dict__))

    def _event(self,state:CompleteLearnerState,x:Any,y:Any)->EventResult:
        cb=state.cursor
        pred=self.predict_fn(PredictionView.from_state(state),x)
        loss=require_finite(self.score_fn(pred,y),"loss")
        # Target-derived causal update may change only causal/RNG state.
        before=state.clone()
        try:
            self.causal_update_fn(state,x,y)
            if state.theta!=before.theta or state.optimizer_state!=before.optimizer_state or state.accumulator_state!=before.accumulator_state or state.cursor!=before.cursor:
                raise ContractError('causal update mutated prediction/value/accumulator state outside registered causal fields')
        except Exception:
            self._restore(state,before); raise
        # Accumulation may change only the non-prediction-visible accumulator.
        before_acc=state.clone()
        try:
            self.optimizer_accumulate_fn(state,x,y,pred)
            if state.theta!=before_acc.theta or state.optimizer_state!=before_acc.optimizer_state or state.causal_state!=before_acc.causal_state or state.rng_state!=before_acc.rng_state or state.cursor!=before_acc.cursor:
                raise ContractError('optimizer accumulation leaked into prediction-visible state before commit')
        except Exception:
            self._restore(state,before_acc); raise
        state.cursor+=1
        return EventResult(pred,loss,cb,state.cursor)

    def _commit(self,state:CompleteLearnerState)->None:
        before=state.clone()
        try:
            self.optimizer_commit_fn(state)
            if state.causal_state!=before.causal_state or state.cursor!=before.cursor:
                raise ContractError('optimizer commit mutated causal state/cursor')
        except Exception:
            self._restore(state,before); raise

    def run_unit(self,state:CompleteLearnerState, xs:Sequence[Any], ys:Sequence[Any])->list[EventResult]:
        if len(xs)!=len(ys) or not xs or len(xs)>self.update_unit: raise ContractError("invalid update unit batch")
        out=[self._event(state,x,y) for x,y in zip(xs,ys)]
        self._commit(state)
        return out

    def run_event(self,state:CompleteLearnerState,x:Any,y:Any,*,commit:bool)->EventResult:
        r=self._event(state,x,y)
        if commit:self._commit(state)
        return r

