"""Exact native evaluation and conservative whole-range bounds.

This pure arithmetic layer cannot acquire observations, initialize a live
candidate or authorize installation. The complete Runtime must own those acts.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as F
from typing import Mapping, Sequence

from .core import ContractError, natural
from .program import Product, Program, SemanticRules, Source, State, Sum, rational


@dataclass(frozen=True)
class Interval:
    lower: F
    upper: F

    def __post_init__(self):
        object.__setattr__(self, 'lower', rational(self.lower, 'interval lower'))
        object.__setattr__(self, 'upper', rational(self.upper, 'interval upper'))
        if self.lower > self.upper:
            raise ContractError('reversed nonnegative enclosure')

    def __add__(self, other):
        return Interval(self.lower+other.lower, self.upper+other.upper)

    def __mul__(self, other):
        return Interval(self.lower*other.lower, self.upper*other.upper)


@dataclass(frozen=True)
class Evaluation:
    values: tuple[F, ...]
    excesses: tuple[F, ...]
    masses: tuple[F, ...]
    normalizer: F
    probabilities: tuple[F, ...]
    delayed: tuple[tuple[str, tuple[F, ...]], ...]


@dataclass(frozen=True)
class RangeBound:
    values: tuple[Interval, ...]
    masses: tuple[Interval, ...]
    normalizer: Interval
    delayed_invariant: bool

    def sufficient(self, *, normalizer_cap, activation_cap) -> bool:
        r = rational(normalizer_cap, 'normalizer cap', positive=True)
        a = rational(activation_cap, 'activation cap', positive=True)
        return self.delayed_invariant and self.normalizer.upper <= r and all(v.upper <= a for v in self.values)


class ArithmeticUnresolved(ContractError):
    """The exact reference work representation cannot close this computation."""


def _guard(*values, bit_limit):
    if bit_limit is None:
        return
    natural(bit_limit, 'reference integer work limit', positive=True)
    for value in values:
        entries = (value.lower, value.upper) if type(value) is Interval else (F(value),)
        if any(max(v.numerator.bit_length(), v.denominator.bit_length()) > bit_limit for v in entries):
            raise ArithmeticUnresolved('exact reference integer work limit exceeded')


def _operation(left, right, *, multiply, bit_limit):
    _guard(left, right, bit_limit=bit_limit)
    if bit_limit is not None:
        a = (left.lower, left.upper) if type(left) is Interval else (F(left),)
        b = (right.lower, right.upper) if type(right) is Interval else (F(right),)
        # Conservative preflight on raw rational integer operations. Failure is
        # UNRESOLVED; cancellations or a better arithmetic backend may fit.
        for x in a:
            for y in b:
                nx, dx, ny, dy = x.numerator.bit_length(), x.denominator.bit_length(), y.numerator.bit_length(), y.denominator.bit_length()
                upper = max(nx+ny, dx+dy) if multiply else max(nx+dy, ny+dx, dx+dy)+1
                if upper > bit_limit:
                    raise ArithmeticUnresolved('reference operation may exceed its integer work limit')
    result = left*right if multiply else left+right
    _guard(result, bit_limit=bit_limit)
    return result


def parameters(program: Program, values: Sequence) -> tuple[F, ...]:
    result = tuple(rational(v, 'persistent SUM value') for v in values)
    if len(result) != program.slot_count:
        raise ContractError('complete slot state has the wrong size')
    return result


def reset_delayed(rules: SemanticRules) -> tuple[tuple[str, tuple[F, ...]], ...]:
    return tuple((s.state_id, (F(0),)*s.delay) for s in rules.states)


def _evaluate_nodes(program, source_values, state_values, slot_values, zero, bit_limit=None):
    result = []
    for node in program.nodes:
        if type(node) is Source:
            value = source_values[node.source_id]
        elif type(node) is State:
            value = state_values[node.state_id]
        elif type(node) is Sum:
            value = zero
            for term in node.terms:
                term_value = _operation(slot_values[term.slot], result[term.parent], multiply=True, bit_limit=bit_limit)
                value = _operation(value, term_value, multiply=False, bit_limit=bit_limit)
        else:
            assert type(node) is Product
            value = _operation(result[node.left], result[node.right], multiply=True, bit_limit=bit_limit)
        _guard(value, bit_limit=bit_limit)
        result.append(value)
    return tuple(result)


def evaluate(program: Program, rules: SemanticRules, theta: Sequence,
             source_values: Mapping[str, F], delayed: Sequence[tuple[str, Sequence[F]]] = (), *, bit_limit=None) -> Evaluation:
    program.validate(rules)
    slot_values = parameters(program, theta)
    if set(source_values) != {s.source_id for s in rules.sources}:
        raise ContractError('source observation differs from the registered complete interface')
    observed = {s.source_id: rational(source_values[s.source_id], 'source observation') for s in rules.sources}
    if any(observed[s.source_id] > s.upper for s in rules.sources):
        raise ContractError('source observation exceeds its registered range')
    histories = dict(delayed)
    if len(histories) != len(delayed) or set(histories) != {s.state_id for s in rules.states}:
        raise ContractError('missing, duplicate or undeclared delayed state')
    for spec in rules.states:
        history = tuple(rational(v, 'delayed state value') for v in histories[spec.state_id])
        if len(history) != spec.delay or any(v > spec.upper for v in history):
            raise ContractError('delayed history length or range mismatch')
        histories[spec.state_id] = history
    values = _evaluate_nodes(program, observed, {key: vals[0] for key, vals in histories.items()}, slot_values, F(0), bit_limit)
    excesses = tuple(values[h] for h in program.heads)
    masses = tuple(_operation(b, e, multiply=False, bit_limit=bit_limit) for b, e in zip(rules.base, excesses))
    normalizer = F(0)
    for mass in masses:
        normalizer = _operation(normalizer, mass, multiply=False, bit_limit=bit_limit)
    bodies = {binding.state_id: values[binding.body] for binding in program.bindings}
    next_delayed = []
    for spec in rules.states:
        if bodies[spec.state_id] > spec.upper:
            raise ContractError('positive recurrent update exceeds its registered state range')
        next_delayed.append((spec.state_id, histories[spec.state_id][1:]+(bodies[spec.state_id],)))
    inverse = F(normalizer.denominator, normalizer.numerator)
    probabilities = tuple(_operation(v, inverse, multiply=True, bit_limit=bit_limit) for v in masses)
    return Evaluation(values, excesses, masses, normalizer, probabilities, tuple(next_delayed))


def enclose(program: Program, rules: SemanticRules, theta: Sequence, *, source_point=None, bit_limit=None) -> RangeBound:
    """An independent-source/state-box upper. Inconclusive is never rejection.

    This can be loose for mutually exclusive unary sources. Complete finite
    domain checking or a stronger registered enclosure may establish safety.
    """
    program.validate(rules)
    slot_values = tuple(Interval(v, v) for v in parameters(program, theta))
    source_bounds = {s.source_id: Interval(0, s.upper) for s in rules.sources}
    if source_point is not None:
        if set(source_point) != set(source_bounds):
            raise ContractError('incomplete declared source point')
        source_bounds = {key: Interval(value, value) for key, value in source_point.items()}
        if any(source_bounds[s.source_id].upper > s.upper for s in rules.sources):
            raise ContractError('source point exceeds its registered range')
    state_bounds = {s.state_id: Interval(0, s.upper) for s in rules.states}
    values = _evaluate_nodes(program, source_bounds, state_bounds, slot_values, Interval(0, 0), bit_limit)
    masses = tuple(_operation(Interval(b, b), values[h], multiply=False, bit_limit=bit_limit) for b, h in zip(rules.base, program.heads))
    normalizer = Interval(0, 0)
    for mass in masses:
        normalizer = _operation(normalizer, mass, multiply=False, bit_limit=bit_limit)
    state_caps = {s.state_id: s.upper for s in rules.states}
    invariant = all(values[b.body].upper <= state_caps[b.state_id] for b in program.bindings)
    return RangeBound(values, masses, normalizer, invariant)
