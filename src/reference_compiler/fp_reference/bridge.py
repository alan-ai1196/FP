from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping
import hashlib, hmac, secrets

from .core import BridgeError, ClaimContract, stable_hash
from .learner import CompleteLearnerState


@dataclass(frozen=True)
class BridgeKey:
    chi: str
    physical_lineage_id: str
    reference_lineage_id: str
    amp_lineage_id: str

    @property
    def key(self)->str: return stable_hash(self)


@dataclass
class BridgeCertificate:
    """Low-level session state. It is not install authorization by itself."""
    key: BridgeKey
    relation_id: str
    init_verified: bool=False
    verified_event_count: int=0
    last_cursor: int|None=None
    alive: bool=True

    def verify_initialization(self, ref_state:CompleteLearnerState, amp_state:CompleteLearnerState, relation:Callable[[CompleteLearnerState,CompleteLearnerState],bool])->None:
        if ref_state.lineage_id!=self.key.reference_lineage_id or amp_state.lineage_id!=self.key.amp_lineage_id: raise BridgeError('bridge lineage mismatch at initialization')
        if ref_state.physical_lineage_id!=self.key.physical_lineage_id or amp_state.physical_lineage_id!=self.key.physical_lineage_id: raise BridgeError('bridge physical lineage mismatch')
        if ref_state.cursor!=amp_state.cursor: raise BridgeError('bridge initialization cursor mismatch')
        if not relation(ref_state,amp_state): raise BridgeError('bridge initialization relation failed')
        self.init_verified=True; self.last_cursor=ref_state.cursor

    def verify_event(self, ref_state:CompleteLearnerState, amp_state:CompleteLearnerState, relation:Callable[[CompleteLearnerState,CompleteLearnerState],bool])->None:
        if not self.init_verified or not self.alive: raise BridgeError('bridge not initialized/alive')
        if ref_state.lineage_id!=self.key.reference_lineage_id or amp_state.lineage_id!=self.key.amp_lineage_id: raise BridgeError('bridge lineage mismatch')
        if ref_state.physical_lineage_id!=self.key.physical_lineage_id or amp_state.physical_lineage_id!=self.key.physical_lineage_id: raise BridgeError('bridge physical lineage mismatch')
        if ref_state.cursor!=amp_state.cursor: raise BridgeError('bridge cursor mismatch')
        if self.last_cursor is None or ref_state.cursor < self.last_cursor: raise BridgeError('bridge cursor moved backwards')
        if ref_state.cursor == self.last_cursor: raise BridgeError('bridge event did not advance cursor')
        if not relation(ref_state,amp_state): raise BridgeError('event relation failed')
        self.last_cursor=ref_state.cursor; self.verified_event_count+=1

    def assert_matches(self,*,chi:str,physical_lineage_id:str,reference_lineage_id:str,amp_lineage_id:str)->None:
        if not self.alive or not self.init_verified: raise BridgeError('bridge not valid')
        expected=BridgeKey(chi,physical_lineage_id,reference_lineage_id,amp_lineage_id)
        if expected != self.key: raise BridgeError(f'bridge key mismatch expected={expected.key} actual={self.key.key}')


@dataclass(frozen=True)
class BridgeAuthorization:
    key: BridgeKey
    relation_id: str
    reference_state_id: str
    amp_state_id: str
    cursor: int
    verified_event_count: int
    authority_id: str
    signature: str


class BridgeAuthority:
    """Owns event-level reference↔AMP bridge sessions and issues current-boundary tokens."""
    def __init__(self, contract:ClaimContract, relations:Mapping[str,Callable[[CompleteLearnerState,CompleteLearnerState],bool]]):
        unknown=set(relations)-set(contract.bridge_relation_ids); missing=set(contract.bridge_relation_ids)-set(relations)
        if unknown: raise BridgeError(f'undeclared bridge relations: {sorted(unknown)}')
        if missing: raise BridgeError(f'missing declared bridge relations: {sorted(missing)}')
        self.contract=contract; self.relations=dict(relations); self.sessions:dict[str,BridgeCertificate]={}
        self._secret=secrets.token_bytes(32); self.authority_id=hashlib.sha256(self._secret).hexdigest()[:24]

    def _sign(self,fields:tuple)->str:
        return hmac.new(self._secret,stable_hash(fields).encode('ascii'),hashlib.sha256).hexdigest()

    def initialize(self, *, physical_lineage_id:str, reference_state:CompleteLearnerState, amp_state:CompleteLearnerState, relation_id:str)->BridgeKey:
        if relation_id not in self.relations: raise BridgeError('unregistered bridge relation')
        key=BridgeKey(self.contract.chi,physical_lineage_id,reference_state.lineage_id,amp_state.lineage_id)
        if key.key in self.sessions: raise BridgeError('bridge session already exists')
        c=BridgeCertificate(key,relation_id); c.verify_initialization(reference_state,amp_state,self.relations[relation_id]); self.sessions[key.key]=c; return key

    def verify_event(self, key:BridgeKey, reference_state:CompleteLearnerState, amp_state:CompleteLearnerState)->None:
        if key.key not in self.sessions: raise BridgeError('unknown bridge session')
        c=self.sessions[key.key]; c.verify_event(reference_state,amp_state,self.relations[c.relation_id])

    def authorize(self, key:BridgeKey, reference_state:CompleteLearnerState, amp_state:CompleteLearnerState)->BridgeAuthorization:
        if key.key not in self.sessions: raise BridgeError('unknown bridge session')
        c=self.sessions[key.key]; c.assert_matches(chi=self.contract.chi,physical_lineage_id=key.physical_lineage_id,reference_lineage_id=reference_state.lineage_id,amp_lineage_id=amp_state.lineage_id)
        if reference_state.cursor!=amp_state.cursor or c.last_cursor!=reference_state.cursor: raise BridgeError('bridge authorization not at current verified cursor')
        if not self.relations[c.relation_id](reference_state,amp_state): raise BridgeError('bridge relation no longer holds at authorization')
        fields=(key.key,c.relation_id,reference_state.state_id,amp_state.state_id,reference_state.cursor,c.verified_event_count,self.authority_id)
        return BridgeAuthorization(key,c.relation_id,reference_state.state_id,amp_state.state_id,reference_state.cursor,c.verified_event_count,self.authority_id,self._sign(fields))

    def verify_authorization(self,auth:BridgeAuthorization, *, physical_lineage_id:str,reference_state:CompleteLearnerState,amp_state:CompleteLearnerState)->None:
        if auth.authority_id!=self.authority_id: raise BridgeError('bridge authorization from different authority')
        expected=BridgeKey(self.contract.chi,physical_lineage_id,reference_state.lineage_id,amp_state.lineage_id)
        if auth.key!=expected: raise BridgeError('bridge authorization key mismatch')
        if expected.key not in self.sessions: raise BridgeError('bridge session is not live')
        c=self.sessions[expected.key]
        fields=(auth.key.key,auth.relation_id,auth.reference_state_id,auth.amp_state_id,auth.cursor,auth.verified_event_count,auth.authority_id)
        if not hmac.compare_digest(auth.signature,self._sign(fields)): raise BridgeError('invalid bridge authorization signature')
        if (auth.reference_state_id,auth.amp_state_id,auth.cursor)!=(reference_state.state_id,amp_state.state_id,reference_state.cursor): raise BridgeError('bridge authorization stale for current states')
        if amp_state.cursor!=reference_state.cursor or c.last_cursor!=reference_state.cursor: raise BridgeError('bridge session cursor is stale')
        if c.relation_id!=auth.relation_id or c.verified_event_count!=auth.verified_event_count: raise BridgeError('bridge session changed after authorization')
        if not self.relations[c.relation_id](reference_state,amp_state): raise BridgeError('current bridge relation failed')

    def snapshot(self)->dict:
        return {'authority_id':self.authority_id,'sessions':{k:{'key':v.key,'relation_id':v.relation_id,'init_verified':v.init_verified,'events':v.verified_event_count,'last_cursor':v.last_cursor,'alive':v.alive} for k,v in sorted(self.sessions.items())}}
