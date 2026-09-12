"""Exact rounded forward checks and monotone bounds for the CUDA schedule.

The model never constructs a device successor or supplies a forecast to the
learner. Runtime compares actual retained forecasts with it before accepting
them, and binds range bounds to its own current master and complete queues.
Thus a finite kernel audit need not be promoted to an all-input theorem.
"""
from dataclasses import dataclass
from fractions import Fraction as F

from .binary_arithmetic import BinaryFormat, Float64Value, RoundedBinary, round_binary
from .core import ContractError, natural
from .numerics import compare_exact
from .program import Product, Source, State, Sum
from .semantics import ArithmeticUnresolved, _guard, _operation


HALF = BinaryFormat(11, -14, 15)
SINGLE = BinaryFormat(24, -126, 127)
FORWARD_ID = 'exact-rne32-ingress-rne16-forward-ordered-rne32-readout-v1'


def widen(word, width):
    """Exact injective finite binary16/32 embedding, including signed zero."""
    if width not in (16, 32) or type(word) is not int or not 0 <= word < 1 << width:
        raise ContractError('raw half/single encoding required')
    fraction_bits, exponent_bits, bias = (10, 5, 15) if width == 16 else (23, 8, 127)
    exponent = (word >> fraction_bits) & ((1 << exponent_bits)-1)
    if exponent == (1 << exponent_bits)-1:
        raise ArithmeticUnresolved('nonfinite CUDA encoding cannot enter an exact forward relation')
    mantissa = word & ((1 << fraction_bits)-1)
    shift = (exponent if exponent else 1)-bias-fraction_bits
    if exponent:
        mantissa += 1 << fraction_bits
    sign = (word >> (width-1)) << 63
    if not mantissa:
        return Float64Value(sign)
    high = mantissa.bit_length()-1
    return Float64Value(sign | ((high+shift+1023) << 52) | ((mantissa << (52-high))-(1 << 52)))


def _read(word, width, bits):
    # The shared binary64 representation has a guarded general decoder.
    if bits < 1075:
        raise ArithmeticUnresolved('CUDA exact encoding check exceeds its reference integer allowance')
    value = widen(word, width)
    exact = value.exact
    _guard(exact, bit_limit=bits)
    if exact < 0:
        raise ContractError('negative native CUDA forward coordinate')
    return RoundedBinary(exact, bool(not exact and value.negative))


def _queue(rules, delayed, bits, *, check_caps):
    if (type(delayed) is not tuple or len(delayed) != len(rules.states)
            or any(type(row) is not tuple or len(row) != 2 for row in delayed)):
        raise ContractError('complete ordered CUDA delayed interface required')
    result = []
    for spec, (key, words) in zip(rules.states, delayed):
        if key != spec.state_id or type(words) is not tuple or len(words) != spec.delay:
            raise ContractError('CUDA forward lost its complete delayed interface')
        values = tuple(_read(word, 16, bits) for word in words)
        if check_caps and any(compare_exact(v.value, spec.upper, bit_limit=bits) > 0 for v in values):
            raise ArithmeticUnresolved('current complete CUDA queue violates its whole-domain invariant')
        result.append((key, values))
    return tuple(result)


def check_queue(rules, delayed, *, bit_limit):
    _queue(rules, delayed, bit_limit, check_caps=True)


class _Arithmetic:
    def __init__(self, bits):
        natural(bits, 'CUDA exact forward integer limit', positive=True)
        if bits < 1075:
            raise ArithmeticUnresolved('CUDA exact forward decoder needs at least 1075 reference bits')
        self.bits, self.operations = bits, 0

    def cast(self, value, width):
        self.operations += 1
        if type(value) is F:
            value = RoundedBinary(value)
        return round_binary(value.value, HALF if width == 16 else SINGLE,
                            bit_limit=self.bits, negative_zero=value.negative_zero)

    def add(self, left, right):
        exact = _operation(left.value, right.value, multiply=False, bit_limit=self.bits)
        return self.cast(RoundedBinary(exact, bool(not exact and left.negative_zero and right.negative_zero)), 32)

    def half_mul(self, left, right):
        exact = _operation(left.value, right.value, multiply=True, bit_limit=self.bits)
        # Actual half multiplication uses single opmath then half storage.
        # Keep both rounds explicitly, even though finite half products fit
        # exactly in single (22 significant bits; exponent range -48..31).
        single = self.cast(RoundedBinary(exact, bool(not exact and left.negative_zero != right.negative_zero)), 32)
        return self.cast(single, 16)

    def div(self, left, right):
        if not right.value:
            raise ArithmeticUnresolved('CUDA rounded forward has zero normalizer')
        exact = _operation(left.value, F(right.value.denominator, right.value.numerator),
                           multiply=True, bit_limit=self.bits)
        return self.cast(RoundedBinary(exact, bool(not exact and left.negative_zero)), 32)


def forward_operations(program, rules):
    counts = program.counts()
    return (program.slot_count+2*len(rules.sources)+1+2*counts['PRODUCTs']
            +4*counts['SUM_edges']+counts['SUMs']+5*len(rules.base))


def forward_work(program, rules, *, enclosure=False):
    operations = forward_operations(program, rules)
    if enclosure:
        operations += 2*len(rules.states)+len(rules.base)
    return 256*operations+128*(program.slot_count+len(program.nodes)+len(rules.base)
                              +sum(s.delay for s in rules.states)+len(rules.sources))


def _forward(program, rules, theta, coordinates, delayed, arithmetic):
    program.validate(rules)
    if type(theta) is not tuple or len(theta) != program.slot_count:
        raise ContractError('every raw single master slot is required, including unused slots')
    if type(coordinates) is not tuple or len(coordinates) != len(rules.sources):
        raise ContractError('complete exact CUDA source coordinates required')
    for spec, value in zip(rules.sources, coordinates):
        if type(value) is not F or value < 0 or compare_exact(value, spec.upper, bit_limit=arithmetic.bits) > 0:
            raise ContractError('CUDA source point is outside its declared range')
    start = arithmetic.operations
    sources = {s.source_id: arithmetic.cast(arithmetic.cast(value, 32), 16)
               for s, value in zip(rules.sources, coordinates)}
    weights = tuple(arithmetic.cast(_read(word, 32, arithmetic.bits), 16) for word in theta)
    zero = arithmetic.cast(F(0), 32)
    histories, values = dict(delayed), []
    for node in program.nodes:
        if type(node) is Source:
            value = sources[node.source_id]
        elif type(node) is State:
            value = histories[node.state_id][0]
        elif type(node) is Product:
            value = arithmetic.half_mul(values[node.left], values[node.right])
        else:
            assert type(node) is Sum
            accumulator = zero
            for term in node.terms:
                weighted = arithmetic.half_mul(weights[term.slot], values[term.parent])
                accumulator = arithmetic.add(accumulator, arithmetic.cast(weighted, 32))
            value = arithmetic.cast(accumulator, 16)
        values.append(value)
    excesses = tuple(values[h] for h in program.heads)
    base = tuple(arithmetic.cast(b, 32) for b in rules.base)
    masses = tuple(arithmetic.add(b, arithmetic.cast(v, 32)) for b, v in zip(base, excesses))
    normalizer = zero
    for mass in masses:
        normalizer = arithmetic.add(normalizer, mass)
    probabilities = tuple(arithmetic.div(m, normalizer) for m in masses)
    bodies = {b.state_id: values[b.body] for b in program.bindings}
    successor = tuple((key, row[1:]+(bodies[key],)) for key, row in delayed)
    if arithmetic.operations-start != forward_operations(program, rules):
        raise RuntimeError('CUDA exact forward check omitted its registered scalar schedule')
    return (tuple(values), weights, excesses, masses, (normalizer,), probabilities, successor), base


def check_forward(program, rules, raw_state, sources, prediction, *, bit_limit):
    """Check all actual forecast encodings; return paid scalar operation count."""
    if set(sources) != {s.source_id for s in rules.sources}:
        raise ContractError('CUDA forecast differs from the complete source interface')
    arithmetic = _Arithmetic(bit_limit)
    expected, _ = _forward(program, rules, raw_state[0],
        tuple(sources[s.source_id] for s in rules.sources),
        _queue(rules, raw_state[1], bit_limit, check_caps=False), arithmetic)
    if type(prediction) is not tuple or len(prediction) != 7:
        raise ContractError('complete actual CUDA forecast required for exact checking')
    observed = []
    for words, width in zip(prediction[:6], (16, 16, 16, 32, 32, 32)):
        if type(words) is not tuple:
            raise ContractError('actual CUDA forecast needs immutable raw vectors')
        observed.append(tuple(_read(word, width, bit_limit) for word in words))
    observed.append(_queue(rules, prediction[6], bit_limit, check_caps=False))
    if tuple(observed) != expected:
        raise ArithmeticUnresolved('actual CUDA forecast differs from its exact registered rounded forward')
    return arithmetic.operations


def stored_probability(prediction, target, *, bit_limit):
    """Proper probability from a complete already checked raw CUDA forecast.

    Only masses are decoded here, so scoring work is linear in label count.
    Runtime separately checks the owned full forecast/lineage before calling;
    this passive arithmetic function grants no conformance or evidence claim.
    """
    natural(target, 'CUDA stored-mass target label')
    natural(bit_limit, 'CUDA stored-mass integer limit', positive=True)
    if (type(prediction) is not tuple or len(prediction) != 7
            or type(prediction[3]) is not tuple or target >= len(prediction[3])):
        raise ContractError('complete retained CUDA forecast and in-range target required')
    total, selected = F(0), None
    for index, word in enumerate(prediction[3]):
        value = _read(word, 32, bit_limit).value
        if value <= 0:
            raise ArithmeticUnresolved('CUDA stored mass is not strictly positive')
        total = _operation(total, value, multiply=False, bit_limit=bit_limit)
        if index == target:
            selected = value
    return _operation(selected, F(total.denominator, total.numerator), multiply=True, bit_limit=bit_limit)


@dataclass(frozen=True)
class CudaRange:
    theta: tuple[int, ...]
    source_point: tuple[F, ...] | None
    values_upper: tuple[F, ...]
    masses_upper: tuple[F, ...]
    base_lower: tuple[F, ...]
    stored_mass_sum_upper: F
    rounded_normalizer_upper: F
    raw_probability_lower: tuple[F, ...]
    scalar_operations: int


def enclose_cuda(program, rules, raw_state, *, source_point=None,
                 normalizer_cap, activation_cap, bit_limit):
    """Sufficient bound on the full declared domain and every legal queue.

    The range claim is about the registered rounded mathematical predictor.
    Every accepted physical forecast must separately pass check_forward.
    A loose bound, underflow, overflow or arithmetic cap is UNRESOLVED.
    """
    arithmetic = _Arithmetic(bit_limit)
    if (type(normalizer_cap) is not F or type(activation_cap) is not F
            or normalizer_cap <= 0 or activation_cap <= 0):
        raise ContractError('exact positive CUDA range caps required')
    _guard(normalizer_cap, activation_cap, bit_limit=bit_limit)
    check_queue(rules, raw_state[1], bit_limit=bit_limit)
    point = None if source_point is None else tuple(source_point)
    coordinates = tuple(s.upper for s in rules.sources) if point is None else point
    # For every representable half z <= u, R16(R32(z))=z and monotonicity
    # gives z <= R16(R32(u)), including downward rounding of a real cap.
    delayed = tuple((s.state_id, (arithmetic.cast(arithmetic.cast(s.upper, 32), 16),)*s.delay)
                    for s in rules.states)
    prediction, base = _forward(program, rules, raw_state[0], coordinates, delayed, arithmetic)
    values, _, _, masses, (normalizer,), _, _ = prediction
    stored_sum = F(0)
    for mass in masses:
        stored_sum = _operation(stored_sum, mass.value, multiply=False, bit_limit=bit_limit)
    def at_most(value, cap, label):
        if compare_exact(value, cap, bit_limit=bit_limit) > 0:
            raise ArithmeticUnresolved(f'CUDA whole-domain {label} is not bounded by its registered cap')
    for value in values:
        at_most(value.value, activation_cap, 'activation')
    at_most(stored_sum, normalizer_cap, 'stored-mass sum')
    at_most(normalizer.value, normalizer_cap, 'rounded normalizer')
    caps = {s.state_id: s.upper for s in rules.states}
    for binding in program.bindings:
        at_most(values[binding.body].value, caps[binding.state_id], 'delayed-state invariant')
    if any(b.value <= 0 for b in base):
        raise ArithmeticUnresolved('registered positive base loses positivity in single precision')
    lower = tuple(arithmetic.div(b, normalizer).value for b in base)
    if any(v <= 0 for v in lower):
        raise ArithmeticUnresolved('whole-domain CUDA final division may underflow to zero')
    operations = forward_operations(program, rules)+2*len(rules.states)+len(rules.base)
    if arithmetic.operations != operations:
        raise RuntimeError('CUDA range check omitted its registered scalar schedule')
    return CudaRange(raw_state[0], point, tuple(v.value for v in values), tuple(m.value for m in masses),
                     tuple(b.value for b in base), stored_sum, normalizer.value, lower, operations)
