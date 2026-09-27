"""Immutable typed native skeletons. Numerical values belong to learner state.

No constructor issues a build, safety, persistence or completeness certificate.
The source/delay declarations are fixed by the enclosing execution contract.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as F

from .core import ContractError, natural, stable_hash
from .token_sources import TokenAtomFamily, TokenSourceTypes


def name(value: str, field: str) -> str:
    if type(value) is not str or not value:
        raise ContractError(f'{field} must be a nonempty string')
    return value


def rational(value, field: str, *, positive: bool = False) -> F:
    # Float conversion is an explicit value operation, never an implicit theorem
    # audit cast. In particular a tiny Fraction must not underflow through float.
    if type(value) not in (int, F) or value < 0 or (positive and value == 0):
        raise ContractError(f'{field} must be an exact {"positive" if positive else "nonnegative"} rational')
    return F(value)


@dataclass(frozen=True)
class SourceSpec:
    source_id: str
    type_id: str
    availability_delay: int
    upper: F

    def __post_init__(self):
        name(self.source_id, 'source ID')
        name(self.type_id, 'source type')
        natural(self.availability_delay, 'source availability delay')
        object.__setattr__(self, 'upper', rational(self.upper, 'source range'))


@dataclass(frozen=True)
class DelayedStateSpec:
    state_id: str
    type_id: str
    delay: int
    upper: F

    def __post_init__(self):
        name(self.state_id, 'delayed state ID')
        name(self.type_id, 'delayed state type')
        natural(self.delay, 'recurrent delay', positive=True)
        object.__setattr__(self, 'upper', rational(self.upper, 'delayed state range'))


@dataclass(frozen=True)
class SemanticRules:
    sources: tuple[SourceSpec, ...] | TokenAtomFamily
    sum_types: tuple[str, ...]
    product_rules: tuple[tuple[str, str, str], ...]
    readout_type: str
    base: tuple[F, ...]
    states: tuple[DelayedStateSpec, ...] = ()

    def __post_init__(self):
        indexed = type(self.sources) is TokenAtomFamily
        if indexed:
            self.sources.__post_init__()
        else:
            object.__setattr__(self, 'sources', tuple(self.sources))
        object.__setattr__(self, 'sum_types', tuple(self.sum_types))
        object.__setattr__(self, 'product_rules', tuple(tuple(rule) for rule in self.product_rules))
        object.__setattr__(self, 'states', tuple(self.states))
        object.__setattr__(self, 'base', tuple(rational(v, 'readout base', positive=True) for v in self.base))
        if not self.sources or not indexed and any(type(s) is not SourceSpec for s in self.sources):
            raise ContractError('a fixed nonempty typed source family is required')
        if not indexed and len({s.source_id for s in self.sources}) != len(self.sources):
            raise ContractError('duplicate source declaration')
        if any(type(s) is not DelayedStateSpec for s in self.states) or len({s.state_id for s in self.states}) != len(self.states):
            raise ContractError('invalid or duplicate delayed state declaration')
        if not self.sum_types or len(set(self.sum_types)) != len(self.sum_types):
            raise ContractError('distinct compatible SUM types are required')
        for type_id in self.sum_types:
            name(type_id, 'SUM result type')
        if any(len(rule) != 3 or any(type(t) is not str or not t for t in rule) for rule in self.product_rules):
            raise ContractError('PRODUCT rules must explicitly name left, right and result types')
        if len(set(self.product_rules)) != len(self.product_rules):
            raise ContractError('duplicate PRODUCT rule')
        name(self.readout_type, 'readout type')
        if len(self.base) < 2:
            raise ContractError('at least two positive readout heads are required')


@dataclass(frozen=True)
class Source:
    source_id: str


@dataclass(frozen=True)
class State:
    state_id: str


@dataclass(frozen=True)
class Term:
    parent: int
    slot: int


@dataclass(frozen=True)
class Sum:
    type_id: str
    terms: tuple[Term, ...]

    def __post_init__(self):
        object.__setattr__(self, 'terms', tuple(self.terms))


@dataclass(frozen=True)
class Product:
    type_id: str
    left: int
    right: int


@dataclass(frozen=True)
class Binding:
    state_id: str
    body: int


Node = Source | State | Sum | Product


@dataclass(frozen=True)
class Program:
    nodes: tuple[Node, ...]
    slot_count: int
    heads: tuple[int, ...]
    bindings: tuple[Binding, ...] = ()

    def __post_init__(self):
        natural(self.slot_count, 'parameter slot count')
        object.__setattr__(self, 'nodes', tuple(self.nodes))
        object.__setattr__(self, 'heads', tuple(self.heads))
        object.__setattr__(self, 'bindings', tuple(self.bindings))
        if any(type(n) not in (Source, State, Sum, Product) for n in self.nodes):
            raise ContractError('undeclared native node constructor')

    @property
    def program_id(self) -> str:
        return stable_hash(self)

    def node_types(self, rules: SemanticRules) -> tuple[str, ...]:
        """Validate an ordered native prefix, independently of its final roots."""
        if type(rules) is not SemanticRules:
            raise ContractError('registered semantic rules required')
        source_types = TokenSourceTypes(rules.sources) if type(rules.sources) is TokenAtomFamily else {s.source_id: s.type_id for s in rules.sources}
        state_types = {s.state_id: s.type_id for s in rules.states}
        types = []

        def parent(index, stop):
            natural(index, 'native parent index')
            if index >= stop:
                raise ContractError('same-time parents must precede their node')
            return types[index]

        for index, node in enumerate(self.nodes):
            if type(node) is Source:
                if type(node.source_id) is not str or node.source_id not in source_types:
                    raise ContractError('undeclared primitive source')
                result = source_types[node.source_id]
            elif type(node) is State:
                if type(node.state_id) is not str or node.state_id not in state_types:
                    raise ContractError('undeclared delayed state')
                result = state_types[node.state_id]
            elif type(node) is Sum:
                name(node.type_id, 'SUM type')
                if node.type_id not in rules.sum_types:
                    raise ContractError('unregistered SUM type')
                for term in node.terms:
                    if type(term) is not Term:
                        raise ContractError('SUM edges bind parameter slots, not numeric literals')
                    if parent(term.parent, index) != node.type_id:
                        raise ContractError('SUM parent/result types are incompatible')
                    natural(term.slot, 'SUM slot index')
                    if term.slot >= self.slot_count:
                        raise ContractError('SUM slot outside the complete parameter state')
                result = node.type_id
            else:
                name(node.type_id, 'PRODUCT type')
                left, right = parent(node.left, index), parent(node.right, index)
                if (left, right, node.type_id) not in rules.product_rules:
                    raise ContractError('PRODUCT lacks a registered typed composition rule')
                result = node.type_id
            types.append(result)
        return tuple(types)

    def validate(self, rules: SemanticRules) -> tuple[str, ...]:
        types = self.node_types(rules)
        state_types = {s.state_id: s.type_id for s in rules.states}

        def parent(index, stop):
            natural(index, 'native root index')
            if index >= stop:
                raise ContractError('native root is outside the completed graph')
            return types[index]

        if len(self.heads) != len(rules.base):
            raise ContractError('readout head count differs from its positive base')
        for head in self.heads:
            if parent(head, len(self.nodes)) != rules.readout_type:
                raise ContractError('readout type mismatch')
        seen = set()
        for binding in self.bindings:
            if type(binding) is not Binding or type(binding.state_id) is not str or binding.state_id not in state_types or binding.state_id in seen:
                raise ContractError('invalid or repeated delayed state binding')
            if parent(binding.body, len(self.nodes)) != state_types[binding.state_id]:
                raise ContractError('delayed binding type mismatch')
            seen.add(binding.state_id)
        # Every declared state advances by its own body. No hidden identity or
        # reset transition is invented when a body is missing.
        if seen != set(state_types):
            raise ContractError('every declared delayed coordinate needs a positive transition body')
        return tuple(types)

    def counts(self) -> dict[str, int]:
        sums = sum(type(n) is Sum for n in self.nodes)
        products = sum(type(n) is Product for n in self.nodes)
        sum_edges = sum(len(n.terms) for n in self.nodes if type(n) is Sum)
        return {'nodes': len(self.nodes), 'sources': sum(type(n) is Source for n in self.nodes),
                'state_reads': sum(type(n) is State for n in self.nodes),
                'SUMs': sums, 'PRODUCTs': products, 'SUM_edges': sum_edges,
                'edges': sum_edges+2*products, 'slots': self.slot_count, 'bindings': len(self.bindings)}
