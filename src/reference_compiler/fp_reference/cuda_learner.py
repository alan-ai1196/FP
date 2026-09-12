"""Actual continuous mixed-precision native learners; no Runtime authority.

This mechanical executor is not yet wired into ReferenceCompilerRuntime.
Torch is imported only on execution. It retains real CUDA tensors for the
complete learner and computes no successor from a cast reference endpoint.
Every arithmetic intermediate survives until the phase's finite check.
Runtime must still own data, resources, phase evidence and installation.

Schedule v1: exact host RNE32 ingress; half source/coefficient/node/delay
storage and forward products; ordered single SUM accumulation then half
storage; single base/readout, backward, gradient accumulator and master SGD.
Backward uses the stored half operands with explicit single operations and
the usual straight-through cast derivative. There is no loss scaling,
automatic differentiation, contraction or implicit CPU-scalar division.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from fractions import Fraction as F
from typing import Mapping

from .binary_arithmetic import BinaryFormat, round_binary
from .core import ContractError, natural
from .learner import LearnerSpec
from .numerics import compare_exact
from .program import Product, Program, SemanticRules, Source, State, Sum, name
from .semantics import ArithmeticUnresolved


BACKEND_ID = 'eager-cuda-half-forward-single-sum-readout-backward-master-v1'
SINGLE = BinaryFormat(24, -126, 127)


def _torch():
    import torch
    return torch


def _tensor(value, dtype, *, dimension=None, nonnegative=False):
    torch = _torch()
    if (type(value) is not torch.Tensor or not value.is_cuda
            or value.dtype != getattr(torch, dtype) or value.requires_grad
            or dimension is not None and value.ndim != dimension):
        raise ContractError('registered CUDA tensor, dtype, shape and manual-gradient path required')
    if not bool(torch.isfinite(value).all().item()):
        raise ArithmeticUnresolved('nonfinite actual CUDA learner or prediction')
    if nonnegative and bool((value < 0).any().item()):
        raise ContractError('negative native CUDA state')


def _histories(delayed):
    if type(delayed) is not tuple:
        raise ContractError('complete ordered CUDA delayed interface required')
    seen = set()
    for entry in delayed:
        if type(entry) is not tuple or len(entry) != 2:
            raise ContractError('CUDA delayed queue needs its state ID')
        key, value = entry
        name(key, 'CUDA delayed state ID')
        if key in seen:
            raise ContractError('duplicate CUDA delayed state ID')
        seen.add(key)
        _tensor(value, 'float16', dimension=1, nonnegative=True)
        if not value.numel():
            raise ContractError('empty CUDA delayed queue')


@dataclass(frozen=True, eq=False)
class CudaLearnerState:
    theta: object
    delayed: tuple
    gradient_sum: object
    unit_count: int
    cursor: int
    optimizer_steps: int

    def __post_init__(self):
        _tensor(self.theta, 'float32', dimension=1, nonnegative=True)
        _tensor(self.gradient_sum, 'float32', dimension=1)
        _histories(self.delayed)
        if self.theta.shape != self.gradient_sum.shape:
            raise ContractError('CUDA master and gradient accumulator shapes differ')
        tensors = [self.gradient_sum, *(value for _, value in self.delayed)]
        if any(value.device != self.theta.device for value in tensors):
            raise ContractError('complete CUDA learner must reside on one device')
        for label in ('unit_count', 'cursor', 'optimizer_steps'):
            natural(getattr(self, label), 'CUDA '+label)
        if self.unit_count > self.cursor:
            raise ContractError('CUDA accumulator exceeds its local clock')


@dataclass(frozen=True, eq=False)
class CudaEvaluation:
    values: object
    theta_half: object
    excesses: object
    masses: object
    normalizer: object
    probabilities: object
    delayed: tuple

    def __post_init__(self):
        for label in ('values', 'theta_half', 'excesses'):
            _tensor(getattr(self, label), 'float16', dimension=1, nonnegative=True)
        for label in ('masses', 'probabilities'):
            _tensor(getattr(self, label), 'float32', dimension=1, nonnegative=True)
        _tensor(self.normalizer, 'float32', dimension=0, nonnegative=True)
        _histories(self.delayed)
        if self.excesses.shape != self.masses.shape or self.masses.shape != self.probabilities.shape:
            raise ContractError('CUDA readout shapes differ')
        if not bool((self.masses > 0).all().item()) or not bool((self.normalizer > 0).item()):
            raise ArithmeticUnresolved('actual CUDA readout lost a positive base or normalizer')


class CudaArithmetic:
    """One actual device phase with a retained intermediate diagnostic tape.

    The tape and all device/host workspace need paid Runtime ownership before
    this can be an authorized backend. Raw trace capture is read-only evidence,
    never a signer. Public helpers check the tape before returning success.
    """
    backend_id = BACKEND_ID

    def __init__(self, bit_limit: int, device=0):
        natural(bit_limit, 'CUDA reference integer work limit', positive=True)
        natural(device, 'CUDA device ordinal')
        torch = _torch()
        if not torch.cuda.is_available() or device >= torch.cuda.device_count():
            raise ArithmeticUnresolved('actual CUDA device unavailable; no CPU fallback')
        self.bit_limit = bit_limit
        self.device = torch.device('cuda', device)
        self._records = []

    def _keep(self, operation, value):
        self._operands(value)
        self._records.append((operation, value))
        return value

    def _operands(self, *values):
        torch = _torch()
        if (any(type(value) is not torch.Tensor or value.device != self.device
                or value.dtype not in (torch.float16, torch.float32) or value.requires_grad for value in values)
                or len({value.dtype for value in values}) != 1):
            raise ContractError('CUDA phase needs resident matching-dtype tensors without automatic gradients')

    def ingress(self, values):
        if type(values) is not tuple or any(type(value) is not F for value in values):
            raise ContractError('CUDA ingress needs a complete exact rational tuple')
        # This is an explicitly registered host input encoding, not conversion
        # of a trained reference theta/gradient into a pretend device successor.
        rounded = [round_binary(value, SINGLE, bit_limit=self.bit_limit) for value in values]
        torch = _torch()
        return self._keep('host-RNE32-ingress', torch.tensor(
            [-0.0 if value.negative_zero else float(value.value) for value in rounded],
            dtype=torch.float32, device=self.device))

    def constant(self, value):
        return self.ingress((value,))[0]

    def cast(self, value, dtype):
        self._operands(value)
        if dtype not in ('float16', 'float32'):
            raise ContractError('unregistered CUDA cast')
        return self._keep('cast-'+dtype, value.to(getattr(_torch(), dtype)))

    def add(self, left, right):
        self._operands(left, right)
        return self._keep('add', left+right)

    def mul(self, left, right):
        self._operands(left, right)
        return self._keep('mul', left*right)

    def div(self, left, right):
        # Both operands stay tensors on the registered device. A Python/CPU
        # scalar divisor would select a different PyTorch numerical operation.
        self._operands(left, right)
        return self._keep('div', left/right)

    def neg(self, value):
        self._operands(value)
        return self._keep('neg', -value)

    def positive_part(self, value):
        self._operands(value)
        torch = _torch()
        zero = torch.zeros_like(value)
        # Explicitly canonicalize either zero sign, as the exact projection.
        return self._keep('positive-part', torch.where(value > zero, value, zero))

    def floor_grid(self, value, bits):
        self._operands(value)
        _tensor(value, 'float32', nonnegative=True)
        natural(bits, 'CUDA dyadic grid bits')
        if bits+1 > self.bit_limit:
            raise ArithmeticUnresolved('CUDA grid exceeds its registered reference integer limit')
        torch = _torch()
        # No large floating scale or reciprocal is materialized. The input is
        # nonnegative single precision after projection. Nonfinite earlier
        # results still remain on the tape and cannot be masked by this step.
        word = value.view(torch.int32) & 0x7fffffff
        exponent = (word >> 23) & 255
        shift = torch.where(exponent != 0, exponent-150, torch.full_like(exponent, -149))
        # Every finite single value already lies on the 2^-149 grid; this
        # exact reduction also avoids converting an enormous legal grid index
        # to an overflowing device integer scalar.
        drop = (-min(bits, 149)-shift).clamp(min=0, max=24)
        kept = torch.where(drop >= 24, torch.zeros_like(word), word & (-1 << drop))
        return self._keep('floor-grid', kept.view(torch.float32))

    def check(self):
        torch = _torch()
        if self._records:
            values = torch.cat([value.reshape(-1).to(torch.float32) for _, value in self._records])
            if not bool(torch.isfinite(values).all().item()):
                raise ArithmeticUnresolved('nonfinite actual CUDA phase intermediate retained')

    def raw_trace(self):
        """Raw results including a failed phase's infinities/NaNs, no authority."""
        torch = _torch()
        result = []
        for operation, value in self._records:
            width = 16 if value.dtype == torch.float16 else 32
            words = value.reshape(-1).view(getattr(torch, 'int'+str(width))).cpu().tolist()
            result.append((operation, width, tuple(word & ((1 << width)-1) for word in words)))
        return tuple(result)


def _arithmetic(arith):
    if type(arith) is not CudaArithmetic or arith._records:
        raise ContractError('a new registered CUDA arithmetic phase is required')


def _state(program, rules, state, arith):
    if type(program) is not Program or type(rules) is not SemanticRules:
        raise ContractError('exact immutable native program and rules required')
    program.validate(rules)
    _arithmetic(arith)
    if type(state) is not CudaLearnerState or state.theta.numel() != program.slot_count:
        raise ContractError('complete CUDA learner does not match its program')
    state.__post_init__()  # Detect a caller's mutable-tensor corruption too.
    if state.theta.device != arith.device:
        raise ContractError('CUDA learner and arithmetic devices differ')
    if tuple((key, value.numel()) for key, value in state.delayed) != tuple((s.state_id, s.delay) for s in rules.states):
        raise ContractError('CUDA delayed histories differ from the registered interface')


def initialize(program: Program, rules: SemanticRules, theta: tuple[F, ...],
               cursor: int, arith: CudaArithmetic) -> CudaLearnerState:
    if type(program) is not Program or type(rules) is not SemanticRules:
        raise ContractError('exact immutable native program and rules required')
    program.validate(rules)
    _arithmetic(arith)
    natural(cursor, 'CUDA birth cursor')
    if type(theta) is not tuple or len(theta) != program.slot_count or any(type(v) is not F or v < 0 for v in theta):
        raise ContractError('CUDA birth requires every registered nonnegative initializer slot')
    values = arith.ingress(theta)
    zero = arith.constant(F(0))
    half_zero = arith.cast(zero, 'float16')
    delayed = tuple((s.state_id, half_zero.repeat(s.delay)) for s in rules.states)
    arith.check()
    return CudaLearnerState(values, delayed, zero.repeat(program.slot_count), 0, cursor, 0)


def evaluate(program: Program, rules: SemanticRules, state: CudaLearnerState,
             source_values: Mapping[str, F], arith: CudaArithmetic) -> CudaEvaluation:
    _state(program, rules, state, arith)
    if not isinstance(source_values, Mapping) or set(source_values) != {s.source_id for s in rules.sources}:
        raise ContractError('CUDA input differs from the complete registered source interface')
    for spec in rules.sources:
        value = source_values[spec.source_id]
        if type(value) is not F or value < 0 or compare_exact(value, spec.upper, bit_limit=arith.bit_limit) > 0:
            raise ContractError('CUDA source exceeds its registered exact input range')
    sources = arith.cast(arith.ingress(tuple(source_values[s.source_id] for s in rules.sources)), 'float16')
    available = {s.source_id: sources[i] for i, s in enumerate(rules.sources)}
    theta_half = arith.cast(state.theta, 'float16')
    zero = arith.constant(F(0))
    histories, values = dict(state.delayed), []
    for node in program.nodes:
        if type(node) is Source:
            value = available[node.source_id]
        elif type(node) is State:
            value = histories[node.state_id][0]
        elif type(node) is Product:
            value = arith.mul(values[node.left], values[node.right])
        else:
            accumulator = zero
            for term in node.terms:
                weighted = arith.mul(theta_half[term.slot], values[term.parent])
                accumulator = arith.add(accumulator, arith.cast(weighted, 'float32'))
            value = arith.cast(accumulator, 'float16')
        values.append(value)
    torch = _torch()
    values = torch.stack(values)
    excesses = torch.stack([values[h] for h in program.heads])
    masses = arith.add(arith.ingress(rules.base), arith.cast(excesses, 'float32'))
    normalizer = zero
    for mass in masses:
        normalizer = arith.add(normalizer, mass)
    probabilities = arith.div(masses, normalizer)
    bodies = {binding.state_id: values[binding.body] for binding in program.bindings}
    delayed = tuple((s.state_id, torch.cat((histories[s.state_id][1:], bodies[s.state_id].reshape(1)))) for s in rules.states)
    arith.check()
    return CudaEvaluation(values, theta_half, excesses, masses, normalizer, probabilities, delayed)


def observe_event(program: Program, rules: SemanticRules, state: CudaLearnerState,
                  spec: LearnerSpec, prediction: CudaEvaluation, target: int,
                  arith: CudaArithmetic) -> CudaLearnerState:
    _state(program, rules, state, arith)
    if type(spec) is not LearnerSpec or state.unit_count != state.cursor % spec.update_unit:
        raise ContractError('CUDA accumulator differs from its registered update clock')
    natural(target, 'CUDA target label')
    if target >= len(program.heads):
        raise ContractError('CUDA target is outside the registered readout')
    if type(prediction) is not CudaEvaluation:
        raise ContractError('complete actual CUDA prediction required')
    prediction.__post_init__()
    if (prediction.values.numel() != len(program.nodes) or prediction.theta_half.numel() != program.slot_count
            or prediction.masses.numel() != len(program.heads)
            or tuple((key, value.numel()) for key, value in prediction.delayed)
               != tuple((key, value.numel()) for key, value in state.delayed)):
        raise ContractError('CUDA prediction differs from its registered learner shape')
    zero, one = arith.constant(F(0)), arith.constant(F(1))
    inverse_t = arith.div(one, prediction.normalizer)
    inverse_y = arith.div(one, prediction.masses[target])
    target_seed = arith.add(inverse_t, arith.neg(inverse_y))
    adjoint = [zero]*len(program.nodes)
    gradient = [zero]*program.slot_count
    for label, head in enumerate(program.heads):
        adjoint[head] = arith.add(adjoint[head], target_seed if label == target else inverse_t)
    # The cast derivative is identity; operands are the actual stored forward
    # values, with every reverse arithmetic operation explicitly single.
    forward = arith.cast(prediction.values, 'float32')
    weights = arith.cast(prediction.theta_half, 'float32')
    for index in range(len(program.nodes)-1, -1, -1):
        node, seed = program.nodes[index], adjoint[index]
        if type(node) is Sum:
            for term in node.terms:
                gradient[term.slot] = arith.add(gradient[term.slot], arith.mul(seed, forward[term.parent]))
                adjoint[term.parent] = arith.add(adjoint[term.parent], arith.mul(seed, weights[term.slot]))
        elif type(node) is Product:
            adjoint[node.left] = arith.add(adjoint[node.left], arith.mul(seed, forward[node.right]))
            adjoint[node.right] = arith.add(adjoint[node.right], arith.mul(seed, forward[node.left]))
    current = _torch().stack(gradient) if gradient else zero.repeat(0)
    accumulated = arith.add(state.gradient_sum, current)
    arith.check()
    return replace(state, delayed=prediction.delayed, gradient_sum=accumulated,
                   unit_count=state.unit_count+1, cursor=state.cursor+1)


def commit_event(state: CudaLearnerState, spec: LearnerSpec,
                 arith: CudaArithmetic) -> CudaLearnerState:
    _arithmetic(arith)
    if type(state) is not CudaLearnerState or type(spec) is not LearnerSpec:
        raise ContractError('complete CUDA learner and registered optimizer required')
    state.__post_init__()
    if state.theta.device != arith.device or state.unit_count != spec.update_unit or state.cursor % spec.update_unit:
        raise ContractError('CUDA commit is outside a full registered update unit or device')
    scale = arith.div(arith.constant(spec.learning_rate), arith.constant(F(spec.update_unit)))
    step = arith.mul(scale, state.gradient_sum)
    updated = arith.positive_part(arith.add(state.theta, arith.neg(step)))
    if spec.commit_grid_bits is not None:
        updated = arith.floor_grid(updated, spec.commit_grid_bits)
    zero = arith.constant(F(0))
    arith.check()  # Check even an overflow later hidden by projection to zero.
    return replace(state, theta=updated, gradient_sum=zero.repeat(state.theta.numel()),
                   unit_count=0, optimizer_steps=state.optimizer_steps+1)


def attach_clock(state: CudaLearnerState, cursor: int, spec: LearnerSpec) -> CudaLearnerState:
    """Mechanical full-unit profile clock attachment; no profile authority."""
    natural(cursor, 'CUDA attached cursor')
    if (type(state) is not CudaLearnerState or type(spec) is not LearnerSpec or state.unit_count
            or state.cursor % spec.update_unit or cursor % spec.update_unit):
        raise ContractError('CUDA profile attachment requires a whole update unit')
    state.__post_init__()
    return replace(state, cursor=cursor)


def raw_tensor(value):
    torch = _torch()
    if type(value) is not torch.Tensor or not value.is_cuda or value.dtype not in (torch.float16, torch.float32):
        raise ContractError('actual supported CUDA tensor required for raw observation')
    width = 16 if value.dtype == torch.float16 else 32
    return tuple(word & ((1 << width)-1) for word in
                 value.reshape(-1).view(getattr(torch, 'int'+str(width))).cpu().tolist())


def raw_state(state: CudaLearnerState):
    if type(state) is not CudaLearnerState:
        raise ContractError('complete CUDA learner required for raw observation')
    return (raw_tensor(state.theta), tuple((key, raw_tensor(value)) for key, value in state.delayed),
            raw_tensor(state.gradient_sum), state.unit_count, state.cursor, state.optimizer_steps)
