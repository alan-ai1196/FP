"""Actual continuous mixed-precision native learners; no Runtime authority.

ReferenceCompilerRuntime now owns this executor through its private CUDA prefix.
Torch is imported only on execution. It retains real CUDA tensors for the
complete learner and computes no successor from a cast reference endpoint.
Every arithmetic intermediate survives until the phase's finite check.
The helper itself has no data, resource, evidence or installation authority.

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
from .learner import SIMPLEX_GRADIENT, LearnerSpec
from .likelihood_encoding import (EncodedLikelihoodState, RationalLikelihoodModel,
    MODELS as LIKELIHOOD_MODELS, power_schedule, joint_inputs)
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
            or value.dtype != getattr(torch, dtype) or value.requires_grad or not value.is_contiguous()
            or dimension is not None and value.ndim != dimension):
        raise ContractError('registered CUDA tensor, dtype, shape and manual-gradient path required')
    width = 16 if value.dtype == torch.float16 else 32
    exponent = 0x7c00 if width == 16 else 0x7f800000
    sign = 1 << (width-1)
    words = raw_tensor(value)
    if any(word & exponent == exponent for word in words):
        raise ArithmeticUnresolved('nonfinite actual CUDA learner or prediction')
    if nonnegative and any(word & sign and word & (sign-1) for word in words):
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
    encoding: EncodedLikelihoodState | None = None

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
        if self.encoding is not None:
            if type(self.encoding) is not EncodedLikelihoodState:
                raise ContractError('registered complete CUDA likelihood encoding required')
            self.encoding.validate_phase(self.theta.numel(), self.unit_count, self.optimizer_steps, self.delayed)


@dataclass(frozen=True, eq=False)
class CudaEvaluation:
    values: object
    theta_half: object
    excesses: object
    masses: object
    normalizer: object
    probabilities: object
    delayed: tuple
    encoding_query: int | None = None

    def __post_init__(self):
        for label in ('values', 'theta_half', 'excesses'):
            _tensor(getattr(self, label), 'float16', dimension=1, nonnegative=True)
        for label in ('masses', 'probabilities'):
            _tensor(getattr(self, label), 'float32', dimension=1, nonnegative=True)
        _tensor(self.normalizer, 'float32', dimension=0, nonnegative=True)
        _histories(self.delayed)
        if self.excesses.shape != self.masses.shape or self.masses.shape != self.probabilities.shape:
            raise ContractError('CUDA readout shapes differ')
        if any(word & 0x7fffffff == 0 for word in raw_tensor(self.masses)+raw_tensor(self.normalizer)):
            raise ArithmeticUnresolved('actual CUDA readout lost a positive base or normalizer')
        if self.encoding_query is not None:
            natural(self.encoding_query, 'actual CUDA likelihood source row')


class CudaArithmetic:
    """One actual device phase with a retained intermediate diagnostic tape.

    The tape and all device/host workspace need paid Runtime ownership before
    this can be an authorized backend. Raw trace capture is read-only evidence,
    never a signer. Public helpers check the tape before returning success.
    """
    backend_id = BACKEND_ID

    def __init__(self, bit_limit: int, device=0, *, workspace=None, output_cell_limit=None,
                 readout_buffer=None, likelihood_workspace=None):
        natural(bit_limit, 'CUDA reference integer work limit', positive=True)
        natural(device, 'CUDA device ordinal')
        torch = _torch()
        if not torch.cuda.is_available() or device >= torch.cuda.device_count():
            raise ArithmeticUnresolved('actual CUDA device unavailable; no CPU fallback')
        self.bit_limit = bit_limit
        self.device = torch.device('cuda', device)
        self._records = []
        if workspace is not None:
            from .cuda_storage import CudaWorkspace
            if type(workspace) is not CudaWorkspace or workspace.arena.device != self.device:
                raise ContractError('registered owned CUDA workspace required')
            workspace._open()
        self._workspace = workspace
        if output_cell_limit is not None:
            natural(output_cell_limit, 'prepaid CUDA output-cell allowance', positive=True)
        self.output_cell_limit = output_cell_limit
        self.output_cells = 0
        if readout_buffer is not None and (workspace is None or type(readout_buffer) is not bytearray):
            raise ContractError('bulk raw observation requires an owned phase and actual host workspace')
        self._readout_buffer = readout_buffer
        self.likelihood_workspace = likelihood_workspace

    def _keep(self, operation, value):
        if self._workspace is not None:
            self._workspace.written(value)
        self._operands(value)
        self._records.append((operation, value))
        return value

    def _operands(self, *values):
        torch = _torch()
        if (any(type(value) is not torch.Tensor or value.device != self.device
                or value.dtype not in (torch.float16, torch.float32) or value.requires_grad
                or not value.is_contiguous() for value in values)
                or len({value.dtype for value in values}) != 1):
            raise ContractError('CUDA phase needs resident matching-dtype tensors without automatic gradients')
        if self._workspace is not None:
            for value in values:
                self._workspace.require_initialized(value)

    def _empty(self, shape, dtype, operation):
        from math import prod
        cells = max(1, prod(shape))
        if self.output_cell_limit is not None and self.output_cells+cells > self.output_cell_limit:
            from .resources import ResourceExceeded
            raise ResourceExceeded('CUDA phase exhausted its prepaid output-cell allowance')
        self.output_cells += cells
        if self._workspace is None:
            return _torch().empty(shape, dtype=dtype, device=self.device)
        return self._workspace.empty(tuple(shape), dtype, operation)

    def _written(self, value):
        if self._workspace is not None:
            self._workspace.written(value)
        return value

    def repeat(self, value, count):
        self._operands(value)
        if value.numel() != 1:
            raise ContractError('registered CUDA repetition needs one scalar')
        result = self._empty((count,), value.dtype, 'repeat-copy')
        result.copy_(value)
        return self._written(result)

    def stack(self, values):
        if not values:
            raise ContractError('CUDA scalar stack cannot be empty')
        for value in values:
            self._operands(value)
            if value.ndim != 0 or value.dtype != values[0].dtype:
                raise ContractError('registered CUDA stack needs matching scalar views')
        result = self._empty((len(values),), values[0].dtype, 'stack-copy')
        for index, value in enumerate(values):
            result[index].copy_(value)
        return self._written(result)

    def concatenate(self, values):
        for value in values:
            self._operands(value)
            if value.ndim != 1 or value.dtype != values[0].dtype:
                raise ContractError('registered CUDA concatenation needs matching vectors')
        result = self._empty((sum(value.numel() for value in values),), values[0].dtype, 'queue-copy')
        position = 0
        for value in values:
            result[position:position+value.numel()].copy_(value)
            position += value.numel()
        return self._written(result)

    def ingress(self, values):
        if type(values) is not tuple or any(type(value) is not F for value in values):
            raise ContractError('CUDA ingress needs a complete exact rational tuple')
        # This is an explicitly registered host input encoding, not conversion
        # of a trained reference theta/gradient into a pretend device successor.
        torch = _torch()
        result = self._empty((len(values),), torch.float32, 'host-RNE32-ingress')
        rounded = [round_binary(value, SINGLE, bit_limit=self.bit_limit) for value in values]
        encoded = torch.tensor([-0.0 if value.negative_zero else float(value.value) for value in rounded],
                               dtype=torch.float32, device='cpu')
        result.copy_(encoded)
        return self._keep('host-RNE32-ingress', result)

    def constant(self, value):
        return self.ingress((value,))[0]

    def cast(self, value, dtype):
        self._operands(value)
        if dtype not in ('float16', 'float32'):
            raise ContractError('unregistered CUDA cast')
        result = self._empty(tuple(value.shape), getattr(_torch(), dtype), 'cast-'+dtype)
        result.copy_(value)
        return self._keep('cast-'+dtype, result)

    def add(self, left, right):
        self._operands(left, right)
        torch = _torch()
        result = self._empty(tuple(torch.broadcast_shapes(left.shape, right.shape)), left.dtype, 'add')
        torch.add(left, right, out=result)
        return self._keep('add', result)

    def mul(self, left, right):
        self._operands(left, right)
        torch = _torch()
        result = self._empty(tuple(torch.broadcast_shapes(left.shape, right.shape)), left.dtype, 'mul')
        torch.mul(left, right, out=result)
        return self._keep('mul', result)

    def div(self, left, right):
        # Both operands stay tensors on the registered device. A Python/CPU
        # scalar divisor would select a different PyTorch numerical operation.
        self._operands(left, right)
        torch = _torch()
        result = self._empty(tuple(torch.broadcast_shapes(left.shape, right.shape)), left.dtype, 'div')
        torch.div(left, right, out=result)
        return self._keep('div', result)

    def neg(self, value):
        self._operands(value)
        result = self._empty(tuple(value.shape), value.dtype, 'neg')
        _torch().neg(value, out=result)
        return self._keep('neg', result)

    def positive_part(self, value):
        self._operands(value)
        torch = _torch()
        shape = tuple(value.shape)
        zero = self._empty(shape, value.dtype, 'projection-zero')
        zero.zero_()
        self._written(zero)
        mask = self._empty(shape, torch.bool, 'projection-mask')
        torch.gt(value, zero, out=mask)
        self._written(mask)
        result = self._empty(shape, value.dtype, 'positive-part')
        # Explicitly canonicalize either zero sign, as the exact projection.
        torch.where(mask, value, zero, out=result)
        return self._keep('positive-part', result)

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
        shape = tuple(value.shape)
        integer = lambda label: self._empty(shape, torch.int32, 'grid-'+label)
        word, exponent, shift, drop = (integer(label) for label in ('word', 'exponent', 'shift', 'drop'))
        torch.bitwise_and(value.view(torch.int32), 0x7fffffff, out=word)
        torch.bitwise_right_shift(word, 23, out=exponent)
        torch.bitwise_and(exponent, 255, out=exponent)
        mask = self._empty(shape, torch.bool, 'grid-mask')
        torch.ne(exponent, 0, out=mask)
        torch.sub(exponent, 150, out=shift)
        constant = integer('constant')
        constant.fill_(-149)
        torch.where(mask, shift, constant, out=shift)
        # Every finite single value already lies on the 2^-149 grid; this
        # exact reduction also avoids converting an enormous legal grid index
        # to an overflowing device integer scalar.
        torch.neg(shift, out=drop)
        torch.sub(drop, min(bits, 149), out=drop)
        torch.clamp(drop, min=0, max=24, out=drop)
        constant.fill_(-1)
        torch.bitwise_left_shift(constant, drop, out=constant)
        torch.bitwise_and(word, constant, out=word)
        torch.ge(drop, 24, out=mask)
        constant.zero_()
        result = self._empty(shape, torch.float32, 'floor-grid')
        torch.where(mask, constant, word, out=result.view(torch.int32))
        for temporary in (word, exponent, shift, drop, mask, constant):
            self._written(temporary)
        return self._keep('floor-grid', result)

    def check(self):
        for (_, value), words in zip(self._records, self._raw_words()):
            mask = 0x7c00 if value.dtype == _torch().float16 else 0x7f800000
            if any(word & mask == mask for word in words):
                raise ArithmeticUnresolved('nonfinite actual CUDA phase intermediate retained')
        if self._workspace is not None:
            self._workspace.arena.check()

    def raw_trace(self):
        """Raw results including a failed phase's infinities/NaNs, no authority."""
        torch = _torch()
        return tuple((operation, 16 if value.dtype == torch.float16 else 32, words)
                     for (operation, value), words in zip(self._records, self._raw_words()))

    def _raw_words(self):
        values = tuple(value for _, value in self._records)
        if self._readout_buffer is not None:
            return self._workspace.raw_words(values, self._readout_buffer)
        return tuple(raw_tensor(value) for value in values)


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
    if state.theta.device != arith.device:
        raise ContractError('CUDA learner and arithmetic devices differ')
    for value in (state.theta, state.gradient_sum, *(values for _, values in state.delayed)):
        arith._operands(value)
    state.__post_init__()  # Ownership precedes reading any numeric payload.
    if tuple((key, value.numel()) for key, value in state.delayed) != tuple((s.state_id, s.delay) for s in rules.states):
        raise ContractError('CUDA delayed histories differ from the registered interface')
    if state.encoding is not None:
        model = state.encoding.model
        if model.program_id != program.program_id or model.semantics != rules:
            raise ContractError('CUDA likelihood coordinates belong to a different native program or semantics')


def initialize(program: Program, rules: SemanticRules, theta: tuple[F, ...],
               cursor: int, arith: CudaArithmetic, *, encoding_model=None) -> CudaLearnerState:
    if type(program) is not Program or type(rules) is not SemanticRules:
        raise ContractError('exact immutable native program and rules required')
    program.validate(rules)
    _arithmetic(arith)
    natural(cursor, 'CUDA birth cursor')
    if type(theta) is not tuple or len(theta) != program.slot_count or any(type(v) is not F or v < 0 for v in theta):
        raise ContractError('CUDA birth requires every registered nonnegative initializer slot')
    encoding = None
    if encoding_model is not None:
        if (type(encoding_model) not in LIKELIHOOD_MODELS or encoding_model.program_id != program.program_id
                or encoding_model.semantics != rules or encoding_model.initial_theta != theta):
            raise ContractError('CUDA likelihood initialization lost its actual program, semantics or Gamma')
        encoding = EncodedLikelihoodState(encoding_model, (0,)*encoding_model.rank, None)
    values = arith.ingress(theta)
    zero = arith.constant(F(0))
    half_zero = arith.cast(zero, 'float16')
    delayed = tuple((s.state_id, arith.repeat(half_zero, s.delay)) for s in rules.states)
    gradient = arith.repeat(zero, program.slot_count)
    arith.check()
    return CudaLearnerState(values, delayed, gradient, 0, cursor, 0, encoding)


def evaluate(program: Program, rules: SemanticRules, state: CudaLearnerState,
             source_values: Mapping[str, F], arith: CudaArithmetic) -> CudaEvaluation:
    _state(program, rules, state, arith)
    if not isinstance(source_values, Mapping) or set(source_values) != {s.source_id for s in rules.sources}:
        raise ContractError('CUDA input differs from the complete registered source interface')
    for spec in rules.sources:
        value = source_values[spec.source_id]
        if type(value) is not F or value < 0 or compare_exact(value, spec.upper, bit_limit=arith.bit_limit) > 0:
            raise ContractError('CUDA source exceeds its registered exact input range')
    encoding_query = None if state.encoding is None else state.encoding.model.query_index(source_values)
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
    values = arith.stack(values)
    excesses = arith.stack([values[h] for h in program.heads])
    masses = arith.add(arith.ingress(rules.base), arith.cast(excesses, 'float32'))
    normalizer = zero
    for mass in masses:
        normalizer = arith.add(normalizer, mass)
    probabilities = arith.div(masses, normalizer)
    bodies = {binding.state_id: values[binding.body] for binding in program.bindings}
    delayed = tuple((s.state_id, arith.concatenate((histories[s.state_id][1:], bodies[s.state_id].reshape(1)))) for s in rules.states)
    arith.check()
    return CudaEvaluation(values, theta_half, excesses, masses, normalizer, probabilities, delayed, encoding_query)


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
    for value in (prediction.values, prediction.theta_half, prediction.excesses, prediction.masses,
                  prediction.normalizer, prediction.probabilities, *(values for _, values in prediction.delayed)):
        arith._operands(value)
    prediction.__post_init__()
    encoding = state.encoding
    if encoding is not None:
        if spec != encoding.model.learner or prediction.encoding_query is None:
            raise ContractError('CUDA likelihood observation lost its actual U or pre-target query')
        encoding = encoding.observe(prediction.encoding_query, target)
    elif prediction.encoding_query is not None:
        raise ContractError('a likelihood prediction cannot change an ordinary CUDA learner representation')
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
    current = arith.stack(gradient) if gradient else arith.repeat(zero, 0)
    accumulated = arith.add(state.gradient_sum, current)
    arith.check()
    return replace(state, delayed=prediction.delayed, gradient_sum=accumulated,
                   unit_count=state.unit_count+1, cursor=state.cursor+1, encoding=encoding)


def commit_event(state: CudaLearnerState, spec: LearnerSpec,
                 arith: CudaArithmetic) -> CudaLearnerState:
    _arithmetic(arith)
    if type(state) is not CudaLearnerState or type(spec) is not LearnerSpec:
        raise ContractError('complete CUDA learner and registered optimizer required')
    for value in (state.theta, state.gradient_sum, *(values for _, values in state.delayed)):
        arith._operands(value)
    state.__post_init__()
    if state.theta.device != arith.device or state.unit_count != spec.update_unit or state.cursor % spec.update_unit:
        raise ContractError('CUDA commit is outside a full registered update unit or device')
    if state.encoding is not None:
        return _commit_encoded(state, spec, arith)
    scale = arith.div(arith.constant(spec.learning_rate), arith.constant(F(spec.update_unit)))
    if spec.optimizer_id == SIMPLEX_GRADIENT:
        if spec.simplex_slots[-1] >= state.theta.numel():
            raise ContractError('CUDA learner lacks its registered simplex block')
        weights = arith.stack(tuple(state.theta[slot] for slot in spec.simplex_slots))
        gradients = arith.stack(tuple(state.gradient_sum[slot] for slot in spec.simplex_slots))
        zero, one = arith.constant(F(0)), arith.constant(F(1))
        def ordered_sum(values):
            result = zero
            for index in range(values.numel()):
                result = arith.add(result, values[index])
            return result
        def positive_total(value):
            arith.check()
            word = raw_tensor(value)[0]
            if word & 0x80000000 or not word & 0x7fffffff:
                raise ArithmeticUnresolved('CUDA simplex has no positive normalizer')
        total = ordered_sum(weights)
        weighted = ordered_sum(arith.mul(weights, gradients))
        positive_total(total)
        mean = arith.div(weighted, total)
        direction = arith.add(gradients, arith.neg(mean))
        factor = arith.add(one, arith.neg(arith.mul(scale, direction)))
        values = arith.mul(weights, factor)
        arith.check()
        if any(word & 0x80000000 and word & 0x7fffffff for word in raw_tensor(values)):
            raise ArithmeticUnresolved('CUDA simplex gradient leaves its nonnegative domain')
        normalizer = ordered_sum(values)
        positive_total(normalizer)
        # Negativity/nonfinite checks precede this representation-only zero
        # canonicalization, so it cannot conceal an invalid update.
        normalized = arith.positive_part(arith.div(values, normalizer))
        selected = dict(zip(spec.simplex_slots, range(len(spec.simplex_slots))))
        theta = arith.stack(tuple(normalized[selected[slot]] if slot in selected else state.theta[slot]
                                  for slot in range(state.theta.numel())))
        gradient = arith.repeat(zero, state.theta.numel())
        arith.check()
        return replace(state, theta=theta, gradient_sum=gradient,
                       unit_count=0, optimizer_steps=state.optimizer_steps+1)
    step = arith.mul(scale, state.gradient_sum)
    updated = arith.positive_part(arith.add(state.theta, arith.neg(step)))
    if spec.commit_grid_bits is not None:
        updated = arith.floor_grid(updated, spec.commit_grid_bits)
    zero = arith.constant(F(0))
    gradient = arith.repeat(zero, state.theta.numel())
    arith.check()  # Check even an overflow later hidden by projection to zero.
    return replace(state, theta=updated, gradient_sum=gradient,
                   unit_count=0, optimizer_steps=state.optimizer_steps+1)


def _commit_encoded(state, spec, arith):
    """Actual GPU decoder of paid integer coordinates, never reference theta.

    The native observed gradient is retained in the predecessor. Its exact
    unit-simplex transition has the proved integer-coordinate simulation.
    The legacy path uses binary32 powers on device. The distinct rational
    path combines factors in paid host integers before exact RNE32 ingress;
    its normalization and the native forward/gradient remain on device.
    """
    if spec != state.encoding.model.learner:
        raise ContractError('CUDA likelihood commit differs from its actual registered U')
    encoding = state.encoding.commit()
    if type(encoding.model) is RationalLikelihoodModel:
        inputs = joint_inputs(encoding, state.optimizer_steps+1, bit_limit=arith.bit_limit,
                              workspace=arith.likelihood_workspace)
        weights = arith.ingress(inputs)
        zero = arith.constant(F(0))
        total = zero
        for value in weights:
            total = arith.add(total, value)
        normalized = arith.div(weights, total)
    else:
        differences, bits = power_schedule(encoding, state.optimizer_steps+1, bit_limit=arith.bit_limit)
        radix_inverse = arith.constant(1/encoding.model.contract.radix)
        one, zero = arith.constant(F(1)), arith.constant(F(0))
        powers = [radix_inverse]
        for _ in range(1, bits):
            powers.append(arith.mul(powers[-1], powers[-1]))
        weights = []
        for exponent in differences:
            value = one
            for bit in range(bits):
                if exponent & (1 << bit):
                    value = arith.mul(value, powers[bit])
            weights.append(value)
        total = zero
        for value in weights:
            total = arith.add(total, value)
        normalized = arith.div(arith.stack(weights), total)
    selected = {slot: k for k, slot in enumerate(spec.simplex_slots)}
    updated = arith.stack([normalized[selected[i]] if i in selected else state.theta[i]
                          for i in range(state.theta.numel())])
    gradient = arith.repeat(zero, state.theta.numel())
    arith.check()
    return replace(state, theta=updated, gradient_sum=gradient, unit_count=0,
                   optimizer_steps=state.optimizer_steps+1, encoding=encoding)


def attach_clock(state: CudaLearnerState, cursor: int, spec: LearnerSpec) -> CudaLearnerState:
    """Mechanical full-unit profile clock attachment; no profile authority."""
    natural(cursor, 'CUDA attached cursor')
    if (type(state) is not CudaLearnerState or type(spec) is not LearnerSpec or state.unit_count
            or state.cursor % spec.update_unit or cursor % spec.update_unit):
        raise ContractError('CUDA profile attachment requires a whole update unit')
    state.__post_init__()
    if state.encoding is not None and spec != state.encoding.model.learner:
        raise ContractError('CUDA likelihood profile attachment changed its registered U')
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
    numeric = (raw_tensor(state.theta), tuple((key, raw_tensor(value)) for key, value in state.delayed),
               raw_tensor(state.gradient_sum), state.unit_count, state.cursor, state.optimizer_steps)
    return numeric if state.encoding is None else numeric+(state.encoding.raw(),)
