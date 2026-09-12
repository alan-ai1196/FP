"""Typed data for Runtime-issued reference-class comparison proofs.

Constructing this object does not issue authority. Runtime accepts only a
matching retained issuance at its current revision and exact decision class.
There is no caller-selected kind or arbitrary verifier/signing callback. The
unsafe historical authority remains reproducible from Git via its audit.
"""
from dataclasses import dataclass, field
from fractions import Fraction as F
from .core import ContractError
from .semantics import _operation


@dataclass(frozen=True)
class ReferenceClassProof:
    proof_id: str
    chi: str
    runtime_id: str
    issued_revision: int
    search_id: str
    decision_class_id: str
    ordinary_cursor: int
    base_lineage_id: str
    winner_lineage_id: str
    program_count: int
    best_likelihood: F
    kind: str = field(default='ordered-native-reference-class-and-baseline-optimum-v1', init=False)
    authority_scope: str = field(default='reference empirical comparison only; no equivalence, persistence, AMP or installation authority', init=False)


def verify_maximum(claimed: F, alternatives: tuple[F, ...], *, bit_limit: int):
    """Fixed proposition check, independent of the solver's selection decision."""
    if type(claimed) is not F or claimed <= 0 or not alternatives:
        raise ContractError('reference maximum needs positive exact likelihood evidence')
    for value in alternatives:
        if type(value) is not F or value <= 0:
            raise ContractError('reference alternative has no exact positive likelihood')
        left = _operation(F(claimed.numerator), F(value.denominator), multiply=True, bit_limit=bit_limit)
        right = _operation(F(value.numerator), F(claimed.denominator), multiply=True, bit_limit=bit_limit)
        if left < right:
            raise ContractError('the claimed reference winner is beaten by a retained alternative')
