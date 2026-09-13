"""Registered exact ordinary learning, without callbacks or caller-chosen clocks.

The registered optimizers are mean cross-entropy projected SGD and an explicit
normalized simplex gradient on a declared slot block, with other slots fixed.
Delayed histories are stop-gradient inputs to each event; this is a declared
learner coordinate, not backpropagation through arbitrary recurrent histories.
The arithmetic helpers below have no Runtime, data or installation authority.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from fractions import Fraction as F

from .core import ContractError, natural
from .program import Product, Program, SemanticRules, Sum, rational
from .semantics import ArithmeticUnresolved, Evaluation, _guard, _operation, parameters, reset_delayed


SIMPLEX_GRADIENT = 'mean-ce-normalized-simplex-gradient-v1'


@dataclass(frozen=True)
class LearnerSpec:
    update_unit: int
    learning_rate: F
    commit_grid_bits: int | None = None
    optimizer_id: str = 'mean-ce-projected-sgd-v1'
    gradient_id: str = 'event-local-stop-delayed-v1'
    simplex_slots: tuple[int, ...] = ()

    def __post_init__(self):
        natural(self.update_unit, 'registered update unit', positive=True)
        object.__setattr__(self, 'learning_rate', rational(self.learning_rate, 'learning rate'))
        if self.commit_grid_bits is not None:
            natural(self.commit_grid_bits, 'registered commit grid bits')
        slots = tuple(self.simplex_slots)
        for slot in slots:
            natural(slot, 'simplex parameter slot')
        if tuple(sorted(set(slots))) != slots:
            raise ContractError('simplex slots must be distinct and in registered order')
        object.__setattr__(self, 'simplex_slots', slots)
        if self.gradient_id != 'event-local-stop-delayed-v1':
            raise ContractError('unimplemented registered learner coordinate')
        if self.optimizer_id == 'mean-ce-projected-sgd-v1':
            if slots:
                raise ContractError('SGD has no implicit simplex block')
        elif self.optimizer_id == SIMPLEX_GRADIENT:
            if not slots or self.learning_rate > 1 or self.commit_grid_bits is not None:
                raise ContractError('simplex gradient requires a nonempty block, rate in [0,1], and no commit grid')
        else:
            raise ContractError('unimplemented registered learner coordinate')


@dataclass(frozen=True)
class ReferenceLearnerState:
    theta: tuple[F, ...]
    delayed: tuple[tuple[str, tuple[F, ...]], ...]
    gradient_sum: tuple[F, ...]
    unit_count: int
    cursor: int
    optimizer_steps: int


def initial_state(program: Program, rules: SemanticRules, theta, cursor: int, *,
                  spec: LearnerSpec | None = None, bit_limit: int | None = None) -> ReferenceLearnerState:
    natural(cursor, 'birth cursor')
    theta = parameters(program, theta)
    if spec is not None and spec.optimizer_id == SIMPLEX_GRADIENT:
        if bit_limit is None:
            raise ContractError('simplex initialization needs its registered reference arithmetic bound')
        if spec.simplex_slots[-1] >= len(theta):
            raise ArithmeticUnresolved('native initializer does not contain the declared simplex block')
        total = F(0)
        for slot in spec.simplex_slots:
            total = _operation(total, theta[slot], multiply=False, bit_limit=bit_limit)
        if total != 1:
            raise ArithmeticUnresolved('actual initializer values do not sum to one on the declared simplex block')
    return ReferenceLearnerState(theta, reset_delayed(rules),
                                 (F(0),)*program.slot_count, 0, cursor, 0)


def ce_gradient(program: Program, theta: tuple[F, ...], prediction: Evaluation,
                target: int, *, bit_limit: int) -> tuple[F, ...]:
    """Exact reverse derivative of log(T)-log(M_target), retaining all edges.

    Derivatives are signed optimizer values. Native activations and persistent
    parameters remain nonnegative. Repeated parents/heads/slots accumulate;
    unused slots stay explicit zeros. No numerical logarithm is needed here.
    """
    natural(target, 'target label')
    if target >= len(program.heads):
        raise ContractError('target outside the registered readout')
    if len(prediction.values) != len(program.nodes) or len(theta) != program.slot_count:
        raise ContractError('gradient inputs do not match the complete program')
    add = lambda a, b: _operation(a, b, multiply=False, bit_limit=bit_limit)
    mul = lambda a, b: _operation(a, b, multiply=True, bit_limit=bit_limit)
    inverse_t = F(1)/prediction.normalizer
    inverse_y = F(1)/prediction.masses[target]
    _guard(inverse_t, inverse_y, bit_limit=bit_limit)
    adjoint = [F(0)]*len(program.nodes)
    gradient = [F(0)]*program.slot_count
    for label, head in enumerate(program.heads):
        seed = add(inverse_t, -inverse_y) if label == target else inverse_t
        adjoint[head] = add(adjoint[head], seed)
    for index in range(len(program.nodes)-1, -1, -1):
        node, seed = program.nodes[index], adjoint[index]
        if type(node) is Sum:
            for term in node.terms:
                gradient[term.slot] = add(gradient[term.slot], mul(seed, prediction.values[term.parent]))
                adjoint[term.parent] = add(adjoint[term.parent], mul(seed, theta[term.slot]))
        elif type(node) is Product:
            # Two separate incidences also when left == right (shared square).
            adjoint[node.left] = add(adjoint[node.left], mul(seed, prediction.values[node.right]))
            adjoint[node.right] = add(adjoint[node.right], mul(seed, prediction.values[node.left]))
    return tuple(gradient)


def observe_event(program: Program, state: ReferenceLearnerState, spec: LearnerSpec,
                  prediction: Evaluation, target: int, *, bit_limit: int) -> ReferenceLearnerState:
    if state.unit_count != state.cursor % spec.update_unit:
        raise ContractError('learner accumulator differs from its registered absolute clock')
    gradient = ce_gradient(program, state.theta, prediction, target, bit_limit=bit_limit)
    accumulated = tuple(_operation(a, b, multiply=False, bit_limit=bit_limit)
                        for a, b in zip(state.gradient_sum, gradient))
    return replace(state, delayed=prediction.delayed, gradient_sum=accumulated,
                   unit_count=state.unit_count+1, cursor=state.cursor+1)


def commit_event(state: ReferenceLearnerState, spec: LearnerSpec, *, bit_limit: int) -> ReferenceLearnerState:
    if state.unit_count != spec.update_unit or state.cursor % spec.update_unit:
        raise ContractError('optimizer commit outside its full registered update unit')
    scale = _operation(spec.learning_rate, F(1, spec.update_unit), multiply=True, bit_limit=bit_limit)
    if spec.optimizer_id == SIMPLEX_GRADIENT:
        add = lambda a, b: _operation(a, b, multiply=False, bit_limit=bit_limit)
        mul = lambda a, b: _operation(a, b, multiply=True, bit_limit=bit_limit)
        def div(a, b):
            if b <= 0:
                raise ArithmeticUnresolved('simplex optimizer has no positive normalizer')
            inverse = F(1)/b
            _guard(inverse, bit_limit=bit_limit)
            return mul(a, inverse)
        if spec.simplex_slots[-1] >= len(state.theta):
            raise ContractError('complete learner state lacks its registered simplex block')
        total = weighted = F(0)
        for slot in spec.simplex_slots:
            value = state.theta[slot]
            if value < 0:
                raise ContractError('negative reference simplex parameter')
            total = add(total, value)
            weighted = add(weighted, mul(value, state.gradient_sum[slot]))
        if total != 1:
            raise ContractError('reference simplex state lost its exact unit total')
        mean = div(weighted, total)
        theta = list(state.theta)
        normalizer = F(0)
        for slot in spec.simplex_slots:
            direction = add(state.gradient_sum[slot], -mean)
            updated = mul(state.theta[slot], add(F(1), -mul(scale, direction)))
            if updated < 0:
                raise ArithmeticUnresolved('simplex gradient successor leaves its registered nonnegative domain')
            theta[slot] = updated
            normalizer = add(normalizer, updated)
        # This operation is explicit on both reference and rounded paths.
        # No projection or caller-supplied normalization replaces the update.
        for slot in spec.simplex_slots:
            theta[slot] = div(theta[slot], normalizer)
        return replace(state, theta=tuple(theta), gradient_sum=(F(0),)*len(theta),
                       unit_count=0, optimizer_steps=state.optimizer_steps+1)
    theta = []
    for value, gradient in zip(state.theta, state.gradient_sum):
        step = _operation(scale, gradient, multiply=True, bit_limit=bit_limit)
        value = max(F(0), _operation(value, -step, multiply=False, bit_limit=bit_limit))
        if spec.commit_grid_bits is not None:
            # Projection and floor are fixed value operations, never a hidden
            # fit, adaptive precision choice or a structure-supplied constant.
            if spec.commit_grid_bits >= bit_limit:
                raise ContractError('commit grid exceeds the registered reference integer limit')
            denominator = 1 << spec.commit_grid_bits
            scaled = _operation(value, F(denominator), multiply=True, bit_limit=bit_limit)
            value = F(scaled.numerator//scaled.denominator, denominator)
        theta.append(value)
    return replace(state, theta=tuple(theta), gradient_sum=(F(0),)*len(theta),
                   unit_count=0, optimizer_steps=state.optimizer_steps+1)
