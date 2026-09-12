"""Registered exact ordinary learning, without callbacks or caller-chosen clocks.

The current optimizer is mean cross-entropy projected SGD. Delayed histories
are stop-gradient inputs to each event; this is a declared learner coordinate,
not a claim to implement backpropagation through arbitrary recurrent histories.
The arithmetic helpers below have no Runtime, data or installation authority.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from fractions import Fraction as F

from .core import ContractError, natural
from .program import Product, Program, SemanticRules, Sum, rational
from .semantics import Evaluation, _guard, _operation, parameters, reset_delayed


@dataclass(frozen=True)
class LearnerSpec:
    update_unit: int
    learning_rate: F
    commit_grid_bits: int | None = None
    optimizer_id: str = 'mean-ce-projected-sgd-v1'
    gradient_id: str = 'event-local-stop-delayed-v1'

    def __post_init__(self):
        natural(self.update_unit, 'registered update unit', positive=True)
        object.__setattr__(self, 'learning_rate', rational(self.learning_rate, 'learning rate'))
        if self.commit_grid_bits is not None:
            natural(self.commit_grid_bits, 'registered commit grid bits')
        if self.optimizer_id != 'mean-ce-projected-sgd-v1' or self.gradient_id != 'event-local-stop-delayed-v1':
            raise ContractError('unimplemented registered learner coordinate')


@dataclass(frozen=True)
class ReferenceLearnerState:
    theta: tuple[F, ...]
    delayed: tuple[tuple[str, tuple[F, ...]], ...]
    gradient_sum: tuple[F, ...]
    unit_count: int
    cursor: int
    optimizer_steps: int


def initial_state(program: Program, rules: SemanticRules, theta, cursor: int) -> ReferenceLearnerState:
    natural(cursor, 'birth cursor')
    return ReferenceLearnerState(parameters(program, theta), reset_delayed(rules),
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
