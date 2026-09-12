"""Monotone whole-domain bounds for the registered ordered binary64 forward.

These passive calculations create neither learner states nor observations.
Runtime must bind the result to the actual current theta, full source domain,
delayed invariant and arithmetic implementation before a pre-context claim.
"""
from dataclasses import dataclass
from fractions import Fraction as F

from .binary_arithmetic import Float64Arithmetic, Float64Value
from .core import ContractError
from .numerics import compare_exact
from .program import Product, Program, SemanticRules, Source, State, Sum
from .semantics import ArithmeticUnresolved, _guard, _operation


@dataclass(frozen=True)
class Float64Range:
    theta: tuple[Float64Value, ...]
    source_point: tuple[F, ...] | None
    values_upper: tuple[Float64Value, ...]
    masses_upper: tuple[Float64Value, ...]
    base_lower: tuple[Float64Value, ...]
    stored_mass_sum_upper: F
    rounded_normalizer_upper: Float64Value
    raw_probability_lower: tuple[Float64Value, ...]
    scalar_operations: int


def enclosure_operations(program: Program, rules: SemanticRules) -> int:
    program.validate(rules)
    counts = program.counts()
    return len(rules.sources)+len(rules.states)+1+2*counts['SUM_edges']+counts['PRODUCTs']+4*len(rules.base)


def enclose_float64(program: Program, rules: SemanticRules, theta, *,
                    source_point=None, normalizer_cap: F, activation_cap: F,
                    arith: Float64Arithmetic) -> Float64Range:
    """Enclose a source box/point and every legal delayed queue read.

Nonnegative RN-even addition and multiplication are monotone in each input.
Evaluating upper endpoints thus encloses every stored activation and mass.
Final division is not monotone in the shared sources: bound its numerator
and denominator separately, and retain the proper stored-mass sum too.
An inconclusive bound is UNRESOLVED, never graph inadmissibility.
"""
    program.validate(rules)
    if type(arith) is not Float64Arithmetic or type(theta) is not tuple:
        raise ContractError('registered arithmetic and complete raw theta required')
    if len(theta) != program.slot_count or any(type(v) is not Float64Value for v in theta):
        raise ContractError('complete raw binary64 parameter encoding required')
    bits = arith.bit_limit
    for value in theta:
        if arith._value(value) < 0:
            raise ContractError('negative native parameter')
    if type(normalizer_cap) is not F or type(activation_cap) is not F or normalizer_cap <= 0 or activation_cap <= 0:
        raise ContractError('exact positive range caps required')
    _guard(normalizer_cap, activation_cap, bit_limit=bits)
    point = None if source_point is None else tuple(source_point)
    if point is not None and len(point) != len(rules.sources):
        raise ContractError('incomplete registered source-domain point')
    coordinates = tuple(s.upper for s in rules.sources) if point is None else point
    for spec, value in zip(rules.sources, coordinates):
        if type(value) is not F or value < 0 or compare_exact(value, spec.upper, bit_limit=bits) > 0:
            raise ContractError('source point is outside its declared range')
    start = arith.operations
    sources = {s.source_id: arith.cast(value) for s, value in zip(rules.sources, coordinates)}
    # A nearest-rounded cap encloses every representable number <= that cap,
    # including when rounding the real cap itself goes downward.
    states = {s.state_id: arith.cast(s.upper) for s in rules.states}
    zero = arith.cast(F(0))
    values = []
    for node in program.nodes:
        if type(node) is Source:
            value = sources[node.source_id]
        elif type(node) is State:
            value = states[node.state_id]
        elif type(node) is Sum:
            value = zero
            for term in node.terms:
                value = arith.add(value, arith.mul(theta[term.slot], values[term.parent]))
        else:
            assert type(node) is Product
            value = arith.mul(values[node.left], values[node.right])
        values.append(value)
    base = tuple(arith.cast(b) for b in rules.base)
    masses = tuple(arith.add(b, values[h]) for b, h in zip(base, program.heads))
    normalizer, stored_sum = zero, F(0)
    for mass in masses:
        normalizer = arith.add(normalizer, mass)
        stored_sum = _operation(stored_sum, mass.exact, multiply=False, bit_limit=bits)
    def at_most(value, cap, label):
        if compare_exact(value, cap, bit_limit=bits) > 0:
            raise ArithmeticUnresolved(f'binary64 whole-domain {label} is not bounded by its registered cap')
    for value in values:
        at_most(value.exact, activation_cap, 'activation')
    at_most(stored_sum, normalizer_cap, 'stored-mass sum')
    at_most(normalizer.exact, normalizer_cap, 'rounded normalizer')
    caps = {s.state_id: s.upper for s in rules.states}
    for binding in program.bindings:
        at_most(values[binding.body].exact, caps[binding.state_id], 'delayed-state invariant')
    if any(b.exact <= 0 for b in base):
        raise ArithmeticUnresolved('registered positive base loses positivity in binary64')
    lower = tuple(arith.div(b, normalizer) for b in base)
    if any(p.exact <= 0 for p in lower):
        raise ArithmeticUnresolved('whole-domain binary64 final division may underflow to zero')
    operations = arith.operations-start
    if operations != enclosure_operations(program, rules):
        raise RuntimeError('binary64 range executor omitted its registered scalar schedule')
    return Float64Range(theta, point, tuple(values), masses, base, stored_sum,
                        normalizer, lower, operations)


def stored_probability(prediction, target: int, *, bit_limit: int) -> F:
    """Exact probability of the retained finite masses, not rounded output."""
    from .float64_learner import Float64Evaluation
    from .core import natural
    if type(prediction) is not Float64Evaluation:
        raise ContractError('checked complete binary64 prediction required')
    natural(bit_limit, 'reference integer work limit', positive=True)
    if bit_limit < 1075:
        raise ArithmeticUnresolved('stored-mass decoding exceeds the reference integer work limit')
    natural(target, 'stored-mass target label')
    if target >= len(prediction.masses):
        raise ContractError('target outside the retained mass vector')
    total = F(0)
    for mass in prediction.masses:
        value = mass.exact
        if value <= 0:
            raise ArithmeticUnresolved('stored mass is not strictly positive')
        total = _operation(total, value, multiply=False, bit_limit=bit_limit)
    return _operation(prediction.masses[target].exact, F(total.denominator, total.numerator),
                      multiply=True, bit_limit=bit_limit)
