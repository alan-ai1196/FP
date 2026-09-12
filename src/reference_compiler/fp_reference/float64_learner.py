"""Registered ordered binary64 native learner, without execution authority.

Every scalar transition runs through Float64Arithmetic. This is a separate
finite-arithmetic learner trajectory: it never casts an already-computed exact
gradient or exact optimizer endpoint and calls that binary64 execution.
Runtime owns observations, construction/profile provenance, range/bridge
checks, physical resources and authority. The helpers expose no callbacks.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from fractions import Fraction as F
from typing import Mapping

from .binary_arithmetic import Float64Arithmetic, Float64Value
from .core import ContractError, natural
from .learner import LearnerSpec
from .numerics import compare_exact
from .program import Product, Program, SemanticRules, Source, State, Sum, Term, name


def _values(values, label: str, *, nonnegative=False):
    if type(values) is not tuple or any(type(value) is not Float64Value for value in values):
        raise ContractError(f'{label} must retain immutable binary64 value encodings')
    for value in values:
        exact = value.exact  # The arithmetic representation rejects nonfinite encodings.
        if nonnegative and exact < 0:
            raise ContractError(f'{label} contains a negative native value')


def _histories(histories):
    if type(histories) is not tuple:
        raise ContractError('binary64 delayed histories must be immutable')
    seen = set()
    for entry in histories:
        if type(entry) is not tuple or len(entry) != 2:
            raise ContractError('a delayed history needs its registered state ID')
        state_id, values = entry
        name(state_id, 'binary64 delayed state ID')
        if state_id in seen or not values:
            raise ContractError('duplicate or empty binary64 delayed history')
        seen.add(state_id)
        _values(values, 'binary64 delayed history', nonnegative=True)


@dataclass(frozen=True)
class Float64LearnerState:
    theta: tuple[Float64Value, ...]
    delayed: tuple[tuple[str, tuple[Float64Value, ...]], ...]
    gradient_sum: tuple[Float64Value, ...]
    unit_count: int
    cursor: int
    optimizer_steps: int

    def __post_init__(self):
        _values(self.theta, 'binary64 parameters', nonnegative=True)
        _values(self.gradient_sum, 'binary64 gradient accumulator')
        _histories(self.delayed)
        if len(self.theta) != len(self.gradient_sum):
            raise ContractError('binary64 parameter and accumulator shapes differ')
        natural(self.unit_count, 'binary64 accumulated event count')
        natural(self.cursor, 'binary64 ordinary cursor')
        natural(self.optimizer_steps, 'binary64 optimizer step count')
        if self.unit_count > self.cursor:
            raise ContractError('binary64 accumulator exceeds its executed local clock')


@dataclass(frozen=True)
class Float64Evaluation:
    values: tuple[Float64Value, ...]
    excesses: tuple[Float64Value, ...]
    masses: tuple[Float64Value, ...]
    normalizer: Float64Value
    probabilities: tuple[Float64Value, ...]
    delayed: tuple[tuple[str, tuple[Float64Value, ...]], ...]

    def __post_init__(self):
        for label in ('values', 'excesses', 'masses', 'probabilities'):
            _values(getattr(self, label), f'binary64 {label}', nonnegative=True)
        _values((self.normalizer,), 'binary64 normalizer', nonnegative=True)
        _histories(self.delayed)
        if not len(self.excesses) == len(self.masses) == len(self.probabilities):
            raise ContractError('binary64 readout arrays have different shapes')


def _program(program: Program):
    if type(program) is not Program:
        raise ContractError('an exact immutable native Program is required')
    for index, node in enumerate(program.nodes):
        if type(node) is Sum:
            for term in node.terms:
                if type(term) is not Term:
                    raise ContractError('binary64 SUM edges need registered slots')
                natural(term.parent, 'binary64 SUM parent')
                natural(term.slot, 'binary64 SUM slot')
                if term.parent >= index or term.slot >= program.slot_count:
                    raise ContractError('binary64 SUM edge is outside its completed prefix')
        elif type(node) is Product:
            natural(node.left, 'binary64 PRODUCT left parent')
            natural(node.right, 'binary64 PRODUCT right parent')
            if node.left >= index or node.right >= index:
                raise ContractError('binary64 PRODUCT parents must precede their node')
    for head in program.heads:
        natural(head, 'binary64 readout head')
        if head >= len(program.nodes):
            raise ContractError('binary64 readout is outside the native graph')


def _state(program: Program, state: Float64LearnerState):
    _program(program)
    if type(state) is not Float64LearnerState or len(state.theta) != program.slot_count:
        raise ContractError('binary64 complete learner state does not match its program')


def _arithmetic(arith):
    if type(arith) is not Float64Arithmetic:
        raise ContractError('registered checked binary64 arithmetic is required')


def initialize_operations(program: Program, rules: SemanticRules) -> int:
    """Scalar API calls, excluding separately charged validation/packing."""
    program.validate(rules)
    return program.slot_count+1


def evaluate_operations(program: Program, rules: SemanticRules) -> int:
    """All source/base/zero casts plus each ordered forward scalar operation."""
    program.validate(rules)
    counts = program.counts()
    return len(rules.sources)+1+2*counts['SUM_edges']+counts['PRODUCTs']+4*len(rules.base)


def observe_operations(program: Program) -> int:
    """Rounded reciprocal/adjoint operations and within-unit accumulation."""
    _program(program)
    counts = program.counts()
    return 6+len(program.heads)+4*counts['SUM_edges']+4*counts['PRODUCTs']+program.slot_count


def commit_operations(state: Float64LearnerState, spec: LearnerSpec) -> int:
    """Scale casts/division, separate step/neg/add/projection and optional floor."""
    if type(state) is not Float64LearnerState or type(spec) is not LearnerSpec:
        raise ContractError('registered binary64 learner and optimizer required')
    return 4+len(state.theta)*(4+int(spec.commit_grid_bits is not None))


def initialize(program: Program, rules: SemanticRules, theta: tuple[F, ...],
               cursor: int, arith: Float64Arithmetic) -> Float64LearnerState:
    program.validate(rules)
    _arithmetic(arith)
    natural(cursor, 'binary64 birth cursor')
    if type(theta) is not tuple or len(theta) != program.slot_count or any(type(v) is not F or v < 0 for v in theta):
        raise ContractError('binary64 initialization needs every exact nonnegative registered slot value')
    values = tuple(arith.cast(value) for value in theta)
    zero = arith.cast(F(0))
    delayed = tuple((state.state_id, (zero,)*state.delay) for state in rules.states)
    return Float64LearnerState(values, delayed, (zero,)*program.slot_count, 0, cursor, 0)


def evaluate(program: Program, rules: SemanticRules, state: Float64LearnerState,
             source_values: Mapping[str, F], arith: Float64Arithmetic) -> Float64Evaluation:
    program.validate(rules)
    _state(program, state)
    _arithmetic(arith)
    if not isinstance(source_values, Mapping) or set(source_values) != {spec.source_id for spec in rules.sources}:
        raise ContractError('binary64 input differs from its complete registered source interface')
    sources = {}
    for spec in rules.sources:
        value = source_values[spec.source_id]
        if type(value) is not F or value < 0:
            raise ContractError('binary64 sources must originate in exact nonnegative observations')
        if compare_exact(value, spec.upper, bit_limit=arith.bit_limit) > 0:
            raise ContractError('binary64 source input exceeds its declared exact input range')
        sources[spec.source_id] = arith.cast(value)
    histories = dict(state.delayed)
    if set(histories) != {spec.state_id for spec in rules.states}:
        raise ContractError('binary64 learner has missing or undeclared delayed coordinates')
    for spec in rules.states:
        if len(histories[spec.state_id]) != spec.delay:
            raise ContractError('binary64 learner has an incorrect delayed history length')

    zero = arith.cast(F(0))
    values = []
    for node in program.nodes:
        if type(node) is Source:
            value = sources[node.source_id]
        elif type(node) is State:
            value = histories[node.state_id][0]
        elif type(node) is Sum:
            value = zero
            for term in node.terms:
                value = arith.add(value, arith.mul(state.theta[term.slot], values[term.parent]))
        else:
            value = arith.mul(values[node.left], values[node.right])
        values.append(value)
    excesses = tuple(values[head] for head in program.heads)
    masses = tuple(arith.add(arith.cast(base), excess) for base, excess in zip(rules.base, excesses))
    normalizer = zero
    for mass in masses:
        normalizer = arith.add(normalizer, mass)
    # Division is performed separately for each mass. A rounded reciprocal
    # followed by multiplication would be a different registered forward path.
    probabilities = tuple(arith.div(mass, normalizer) for mass in masses)
    bodies = {binding.state_id: values[binding.body] for binding in program.bindings}
    delayed = tuple((spec.state_id, histories[spec.state_id][1:]+(bodies[spec.state_id],)) for spec in rules.states)
    return Float64Evaluation(tuple(values), excesses, masses, normalizer, probabilities, delayed)


def observe_event(program: Program, state: Float64LearnerState, spec: LearnerSpec,
                  prediction: Float64Evaluation, target: int,
                  arith: Float64Arithmetic) -> Float64LearnerState:
    _state(program, state)
    _arithmetic(arith)
    if type(spec) is not LearnerSpec:
        raise ContractError('registered binary64 optimizer/update unit required')
    if state.unit_count != state.cursor % spec.update_unit:
        raise ContractError('binary64 accumulator differs from its registered absolute clock')
    natural(target, 'binary64 target label')
    if target >= len(program.heads):
        raise ContractError('binary64 target is outside its registered readout')
    if (type(prediction) is not Float64Evaluation or len(prediction.values) != len(program.nodes)
            or len(prediction.masses) != len(program.heads)):
        raise ContractError('binary64 gradient inputs do not match the complete program')
    if tuple((key, len(values)) for key, values in prediction.delayed) != tuple((key, len(values)) for key, values in state.delayed):
        raise ContractError('binary64 observation changed its delayed-state interface')

    zero, one = arith.cast(F(0)), arith.cast(F(1))
    inverse_t = arith.div(one, prediction.normalizer)
    inverse_y = arith.div(one, prediction.masses[target])
    target_seed = arith.add(inverse_t, arith.neg(inverse_y))
    adjoint = [zero]*len(program.nodes)
    gradient = [zero]*program.slot_count
    for label, head in enumerate(program.heads):
        adjoint[head] = arith.add(adjoint[head], target_seed if label == target else inverse_t)
    for index in range(len(program.nodes)-1, -1, -1):
        node, seed = program.nodes[index], adjoint[index]
        if type(node) is Sum:
            for term in node.terms:
                gradient[term.slot] = arith.add(gradient[term.slot], arith.mul(seed, prediction.values[term.parent]))
                adjoint[term.parent] = arith.add(adjoint[term.parent], arith.mul(seed, state.theta[term.slot]))
        elif type(node) is Product:
            # The two incidences remain distinct even for a shared square.
            adjoint[node.left] = arith.add(adjoint[node.left], arith.mul(seed, prediction.values[node.right]))
            adjoint[node.right] = arith.add(adjoint[node.right], arith.mul(seed, prediction.values[node.left]))
    accumulated = tuple(arith.add(old, new) for old, new in zip(state.gradient_sum, gradient))
    return replace(state, delayed=prediction.delayed, gradient_sum=accumulated,
                   unit_count=state.unit_count+1, cursor=state.cursor+1)


def commit_event(state: Float64LearnerState, spec: LearnerSpec,
                 arith: Float64Arithmetic) -> Float64LearnerState:
    _arithmetic(arith)
    if type(state) is not Float64LearnerState or type(spec) is not LearnerSpec:
        raise ContractError('registered binary64 learner and optimizer required')
    if state.unit_count != spec.update_unit or state.cursor % spec.update_unit:
        raise ContractError('binary64 optimizer commit is outside a full registered update unit')
    scale = arith.div(arith.cast(spec.learning_rate), arith.cast(F(spec.update_unit)))
    theta = []
    for value, gradient in zip(state.theta, state.gradient_sum):
        step = arith.mul(scale, gradient)
        updated = arith.positive_part(arith.add(value, arith.neg(step)))
        if spec.commit_grid_bits is not None:
            updated = arith.floor_grid(updated, spec.commit_grid_bits)
        theta.append(updated)
    zero = arith.cast(F(0))
    return replace(state, theta=tuple(theta), gradient_sum=(zero,)*len(theta),
                   unit_count=0, optimizer_steps=state.optimizer_steps+1)
