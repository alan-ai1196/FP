"""Passive exact relations for an executed reference/binary64 CPU prefix.

No function here owns a Runtime or issues an execution/installation token.
Numeric agreement does not establish how an endpoint was reached. Runtime
must execute both registered trajectories, retain raw binary64 encodings and
pay for each check before it uses the resulting relation.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction as F

from .binary_arithmetic import Float64Arithmetic, Float64Value
from .core import ContractError, natural
from .float64_learner import Float64Evaluation, Float64LearnerState
from .learner import ReferenceLearnerState
from .numerics import compare_exact, compare_reduced_exact, add_reduced_exact
from .program import Program, SemanticRules, name, rational
from .semantics import ArithmeticUnresolved, Evaluation, _guard, _operation


@dataclass(frozen=True)
class Float64Contract:
    state_atol: F
    probability_atol: F
    backend_id: str = field(default=Float64Arithmetic.backend_id, init=False)

    def __post_init__(self):
        object.__setattr__(self, 'state_atol', rational(self.state_atol, 'registered binary64 state tolerance'))
        object.__setattr__(self, 'probability_atol', rational(self.probability_atol, 'registered binary64 probability tolerance'))


@dataclass(frozen=True)
class Float64Relation:
    state_error: F = F(0)
    native_error: F = F(0)
    normalizer_error: F = F(0)
    probability_error: F = F(0)
    division_error: F = F(0)

    def __post_init__(self):
        for label in ('state_error', 'native_error', 'normalizer_error', 'probability_error', 'division_error'):
            value = getattr(self, label)
            if type(value) is not F or value < 0:
                raise ContractError('relation diagnostics must be exact nonnegative Fractions')


def relation_work(program: Program, rules: SemanticRules) -> int:
    """Conservative fixed primitive allowance for either complete relation.

The coefficient covers signed differences, guarded rational comparisons and
all three readout representations, including reference consistency checks.
Integer sizes have a separate work limit. This is not host heap, bit-time,
elapsed-time or target-device accounting.
"""
    if type(program) is not Program or type(rules) is not SemanticRules:
        raise ContractError('registered native program and rules required')
    # Runtime already owns a validated program. The relation scans value
    # coordinates, not every SUM edge; do not hide a fresh edge traversal in
    # a coordinate-only work estimate.
    natural(program.slot_count, 'registered slot count')
    coordinates = (len(program.nodes)+program.slot_count+sum(s.delay for s in rules.states)
                   +len(program.heads)+len(rules.sources)+1)
    return 512*coordinates


class _Check:
    def __init__(self, contract, bit_limit):
        if type(contract) is not Float64Contract:
            raise ContractError('exact immutable binary64 relation contract required')
        if type(contract.backend_id) is not str or contract.backend_id != Float64Arithmetic.backend_id:
            raise ContractError('binary64 relation names a different scalar backend')
        natural(bit_limit, 'reference integer work limit', positive=True)
        # The passive decoder may construct the full subnormal denominator
        # 2**1074 even for zero. Preflight its format-wide extent before any
        # exact property access, rather than guarding an already allocated
        # oversized integer afterward.
        if bit_limit < 1075:
            raise ArithmeticUnresolved('binary64 decoding exceeds the reference integer work limit')
        self.bit_limit = bit_limit
        self.state_atol = self.exact(contract.state_atol, 'state tolerance', nonnegative=True)
        self.probability_atol = self.exact(contract.probability_atol, 'probability tolerance', nonnegative=True)

    def exact(self, value, label, *, nonnegative=False, positive=False):
        if type(value) is not F:
            raise ContractError(f'{label} must be an exact Fraction')
        _guard(value, bit_limit=self.bit_limit)
        # Comparisons to zero depend only on the guarded numerator's sign.
        if nonnegative and value.numerator < 0 or positive and value.numerator <= 0:
            raise ArithmeticUnresolved(f'{label} violates its required sign')
        return value

    def reference_values(self, values, label, *, nonnegative=False, positive=False):
        if type(values) is not tuple:
            raise ContractError(f'{label} must be an immutable complete value tuple')
        return tuple(self.exact(v, label, nonnegative=nonnegative, positive=positive) for v in values)

    def finite_values(self, values, label, *, nonnegative=False, positive=False):
        if type(values) is not tuple or any(type(v) is not Float64Value for v in values):
            raise ContractError(f'{label} must retain exact immutable binary64 encodings')
        result = []
        for value in values:
            # Revalidate passive data before decoding; a numeric comparison
            # neither erases the stored bits nor identifies the two zero signs.
            Float64Value.__post_init__(value)
            result.append(self.exact(value.exact, label, nonnegative=nonnegative, positive=positive))
        return tuple(result)

    def history(self, history, label, *, finite=False):
        if type(history) is not tuple:
            raise ContractError(f'{label} must retain all immutable delayed queues')
        result, seen = [], set()
        for entry in history:
            if type(entry) is not tuple or len(entry) != 2:
                raise ContractError(f'{label} has a malformed delayed queue')
            state_id, values = entry
            name(state_id, 'paired delayed state ID')
            if state_id in seen or type(values) is not tuple or not values:
                raise ContractError(f'{label} has a duplicate or empty delayed queue')
            seen.add(state_id)
            decoded = (self.finite_values if finite else self.reference_values)(values, label, nonnegative=True)
            result.append((state_id, decoded))
        return tuple(result)

    def compare(self, left, right):
        return compare_exact(left, right, bit_limit=self.bit_limit)

    def add(self, left, right):
        return _operation(left, right, multiply=False, bit_limit=self.bit_limit)

    def mul(self, left, right):
        return _operation(left, right, multiply=True, bit_limit=self.bit_limit)

    def error(self, previous, left, right):
        error = abs(self.add(left, -right))
        return error if self.compare(error, previous) > 0 else previous

    def bound(self, value, cap, label):
        if self.compare(value, cap) > 0:
            raise ArithmeticUnresolved(f'{label} exceeds its registered bound')

    def paired(self, left, right, label, error=F(0)):
        if len(left) != len(right):
            raise ContractError(f'paired {label} shapes differ')
        for a, b in zip(left, right):
            error = self.error(error, a, b)
        return error

    def paired_history(self, left, right, error=F(0)):
        if tuple((key, len(values)) for key, values in left) != tuple((key, len(values)) for key, values in right):
            raise ContractError('paired delayed queues differ in identity, order or full length')
        for (_, a), (_, b) in zip(left, right):
            error = self.paired(a, b, 'delayed histories', error)
        return error


class _ReducedCheck(_Check):
    """Order/value-only verifier; grants no unreduced cross-product witness.

    A registered owner must fund this implementation separately. Native
    semantics and the original raw-product checker retain their old limits.
    """
    def compare(self, left, right):
        return compare_reduced_exact(left, right, bit_limit=self.bit_limit)

    def add(self, left, right):
        return add_reduced_exact(left, right, bit_limit=self.bit_limit)


def check_state(ref: ReferenceLearnerState, finite: Float64LearnerState,
                contract: Float64Contract, *, bit_limit: int) -> Float64Relation:
    """Compare all learner coordinates; no state is adopted or signed."""
    if type(ref) is not ReferenceLearnerState or type(finite) is not Float64LearnerState:
        raise ContractError('the two complete registered learner-state types are required')
    check = _Check(contract, bit_limit)
    for label in ('unit_count', 'cursor', 'optimizer_steps'):
        a, b = getattr(ref, label), getattr(finite, label)
        natural(a, f'reference {label}')
        natural(b, f'binary64 {label}')
        if a != b:
            raise ContractError(f'paired learner {label} differs')
    if ref.unit_count > ref.cursor:
        raise ContractError('paired partial accumulator exceeds its ordinary cursor')
    ref_theta = check.reference_values(ref.theta, 'reference theta', nonnegative=True)
    ref_gradient = check.reference_values(ref.gradient_sum, 'reference gradient accumulator')
    finite_theta = check.finite_values(finite.theta, 'binary64 theta', nonnegative=True)
    finite_gradient = check.finite_values(finite.gradient_sum, 'binary64 gradient accumulator')
    if len(ref_theta) != len(ref_gradient) or len(finite_theta) != len(finite_gradient):
        raise ContractError('parameter and complete gradient-accumulator shapes differ')
    error = check.paired(ref_theta, finite_theta, 'parameters')
    error = check.paired(ref_gradient, finite_gradient, 'gradient accumulators', error)
    ref_delayed = check.history(ref.delayed, 'reference state')
    finite_delayed = check.history(finite.delayed, 'binary64 state', finite=True)
    error = check.paired_history(ref_delayed, finite_delayed, error)
    check.bound(error, check.state_atol, 'complete learner-state error')
    return Float64Relation(state_error=error)


def check_prediction(ref: Evaluation, finite: Float64Evaluation, contract: Float64Contract,
                     rules: SemanticRules, *, normalizer_cap: F, activation_cap: F,
                     bit_limit: int) -> Float64Relation:
    """Check native, stored-mass probability and actual rounded output separately.

The exact sum of decoded stored masses is not silently replaced by the
rounded normalizer, nor are displayed probabilities used as mathematical
normalization. All checks concern this observed context only.
"""
    if type(ref) is not Evaluation or type(finite) is not Float64Evaluation or type(rules) is not SemanticRules:
        raise ContractError('registered reference/binary64 evaluations and semantic rules required')
    check = _Check(contract, bit_limit)
    cap = check.exact(normalizer_cap, 'normalizer cap', positive=True)
    activation = check.exact(activation_cap, 'activation cap', positive=True)
    references, decoded = {}, {}
    for label in ('values', 'excesses', 'masses', 'probabilities'):
        positive = label in ('masses', 'probabilities')
        references[label] = check.reference_values(getattr(ref, label), f'reference {label}', nonnegative=True, positive=positive)
        decoded[label] = check.finite_values(getattr(finite, label), f'binary64 {label}', nonnegative=True, positive=positive)
        if len(references[label]) != len(decoded[label]):
            raise ContractError(f'paired {label} shapes differ')
    if not references['values'] or any(len(references[key]) != len(rules.base) for key in ('excesses', 'masses', 'probabilities')):
        raise ContractError('prediction has an empty native graph or incomplete registered readout')
    ref_t = check.exact(ref.normalizer, 'reference normalizer', positive=True)
    finite_t, = check.finite_values((finite.normalizer,), 'binary64 rounded normalizer', positive=True)
    check.bound(ref_t, cap, 'reference normalizer')
    check.bound(finite_t, cap, 'binary64 rounded normalizer')
    native_error = F(0)
    for label in ('values', 'excesses', 'masses'):
        native_error = check.paired(references[label], decoded[label], label, native_error)
    for value in references['values']+decoded['values']:
        check.bound(value, activation, 'native activation')
    ref_delayed = check.history(ref.delayed, 'reference prediction')
    finite_delayed = check.history(finite.delayed, 'binary64 prediction', finite=True)
    expected = tuple((state.state_id, state.delay) for state in rules.states)
    if tuple((key, len(values)) for key, values in ref_delayed) != expected:
        raise ContractError('prediction differs from the complete registered delayed-state interface')
    native_error = check.paired_history(ref_delayed, finite_delayed, native_error)
    for state, (_, ref_values), (_, finite_values) in zip(rules.states, ref_delayed, finite_delayed):
        state_cap = check.exact(state.upper, 'registered delayed-state cap', nonnegative=True)
        for value in ref_values+finite_values:
            check.bound(value, state_cap, 'predicted delayed-state coordinate')

    ref_sum, finite_sum = F(0), F(0)
    for base, excess, ref_mass, finite_mass in zip(rules.base, references['excesses'], references['masses'], decoded['masses']):
        check.exact(base, 'registered positive base', positive=True)
        if check.compare(check.add(base, excess), ref_mass) != 0:
            raise ContractError('reference mass differs from its base and excess')
        ref_sum, finite_sum = check.add(ref_sum, ref_mass), check.add(finite_sum, finite_mass)
    if check.compare(ref_sum, ref_t) != 0:
        raise ContractError('reference normalizer is not its exact mass sum')
    check.bound(finite_sum, cap, 'exact sum of binary64 stored masses')
    normalizer_error = check.error(F(0), ref_t, finite_t)
    normalizer_error = check.error(normalizer_error, ref_t, finite_sum)
    normalizer_error = check.error(normalizer_error, finite_t, finite_sum)
    inverse_ref = F(ref_t.denominator, ref_t.numerator)
    inverse_sum = F(finite_sum.denominator, finite_sum.numerator)
    probability_error, division_error = F(0), F(0)
    for ref_mass, finite_mass, ref_probability, raw_probability in zip(
            references['masses'], decoded['masses'], references['probabilities'], decoded['probabilities']):
        check.bound(ref_probability, F(1), 'reference probability')
        check.bound(raw_probability, F(1), 'binary64 raw probability')
        if check.compare(check.mul(ref_mass, inverse_ref), ref_probability) != 0:
            raise ContractError('reference probability is not its exact normalized mass')
        proper_probability = check.mul(finite_mass, inverse_sum)
        probability_error = check.error(probability_error, ref_probability, proper_probability)
        probability_error = check.error(probability_error, ref_probability, raw_probability)
        division_error = check.error(division_error, proper_probability, raw_probability)
    check.bound(native_error, check.state_atol, 'native prediction error')
    check.bound(normalizer_error, check.state_atol, 'normalizer error')
    check.bound(probability_error, check.probability_atol, 'probability error')
    check.bound(division_error, check.probability_atol, 'stored-mass versus raw-division probability error')
    return Float64Relation(native_error=native_error, normalizer_error=normalizer_error,
                           probability_error=probability_error, division_error=division_error)
