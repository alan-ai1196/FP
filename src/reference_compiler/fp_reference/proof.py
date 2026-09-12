"""Typed data for Runtime-issued reference-class comparison proofs.

Constructing this object does not issue authority. Runtime accepts only a
matching retained issuance at its current revision and exact decision class.
There is no caller-selected kind or arbitrary verifier/signing callback. The
unsafe historical authority remains reproducible from Git via its audit.
"""
from dataclasses import dataclass, field
from fractions import Fraction as F
from .core import ContractError, natural
from .program import name
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

    def __post_init__(self):
        self.validate()

    def validate(self):
        """Validate typed proposition data before any issuance comparison.

        Python equality alone identifies ints, bools, floats and Fractions
        with equal numerical values; subclasses can also overload equality.
        Those are different encoded evidence types, not identical issuances.
        This validation does not itself grant Runtime authority.
        """
        for key in ('proof_id', 'chi', 'runtime_id', 'search_id', 'decision_class_id',
                    'base_lineage_id', 'winner_lineage_id'):
            name(getattr(self, key), f'reference proof {key}')
        for key in ('issued_revision', 'ordinary_cursor', 'program_count'):
            natural(getattr(self, key), f'reference proof {key}')
        if type(self.best_likelihood) is not F or not 0 < self.best_likelihood <= 1:
            raise ContractError('reference proof likelihood must be an exact positive Fraction at most one')
        if (type(self.kind) is not str or self.kind != 'ordered-native-reference-class-and-baseline-optimum-v1'
                or type(self.authority_scope) is not str
                or self.authority_scope != 'reference empirical comparison only; no equivalence, persistence, AMP or installation authority'):
            raise ContractError('reference proof has a different proposition kind or authority scope')


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


@dataclass(frozen=True)
class BoundedReferenceProof:
    """A feasible owned witness attains a universal empirical objective upper.

    Unlike ReferenceClassProof, this does NOT assert that every member was
    constructed or that the syntactic cursor exhausted the native grammar.
    The declared class remains complete; unvisited members are bounded by
    the explicitly checked larger categorical prediction class.
    """
    proof_id: str
    chi: str
    runtime_id: str
    issued_revision: int
    search_id: str
    decision_class_id: str
    ordinary_cursor: int
    base_lineage_id: str
    winner_lineage_id: str
    evaluated_programs: int
    best_likelihood: F
    kind: str = field(default='native-reference-class-and-baseline-saturated-upper-optimum-v1', init=False)
    authority_scope: str = field(default='historical empirical optimum via universal source-context upper and owned feasible witness; not exhaustive construction, future optimality or installation authority', init=False)

    def __post_init__(self):
        self.validate()

    def validate(self):
        for key in ('proof_id', 'chi', 'runtime_id', 'search_id', 'decision_class_id',
                    'base_lineage_id', 'winner_lineage_id'):
            name(getattr(self, key), f'bounded reference proof {key}')
        for key in ('issued_revision', 'ordinary_cursor', 'evaluated_programs'):
            natural(getattr(self, key), f'bounded reference proof {key}')
        if type(self.best_likelihood) is not F or not 0 < self.best_likelihood <= 1:
            raise ContractError('bounded reference proof requires an exact positive likelihood at most one')
        if (type(self.kind) is not str or self.kind != 'native-reference-class-and-baseline-saturated-upper-optimum-v1'
                or type(self.authority_scope) is not str or self.authority_scope !=
                'historical empirical optimum via universal source-context upper and owned feasible witness; not exhaustive construction, future optimality or installation authority'):
            raise ContractError('bounded reference proof has a different proposition or authority scope')
