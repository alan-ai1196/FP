"""Fixed indexed AMP lowering and passive complete-coordinate relations.

Runtime owns the actual phase, target, arena, evidence and continuation.
The scalar executor reads actual device words; exact arithmetic checks those
words and never supplies a trained parameter or forecast to the device.
"""
from dataclasses import dataclass
from fractions import Fraction as F
from itertools import combinations
import struct

from .binary_arithmetic import round_binary
from .core import ContractError
from .cuda_range import HALF, SINGLE, widen
from .float64_bridge import Float64Contract, Float64Relation, _Check
from .indexed_count import CountState, observe, commit, attach
from .indexed_execution import (IndexedState, IndexedTheta, IndexedEvaluation,
    IndexedInitializer, IndexedLearner, CategoricalPairDomain, COUNTER_CAP)
from .indexed_relation import IndexedRelation, DecodeAllowance, allowance, partition_shape_plan
from .positive_tape import compile_tape
from .semantics import ArithmeticUnresolved, _operation

BACKEND_ID = 'owned-indexed-radix9-half-products-single-readout-v1'
FORWARD_ID = 'indexed-positive-natural-order-exact-power-aliases-rne16-rne32-v1'
ORDERED_FORWARD_ID = 'indexed-positive-paid-order-exact-power-aliases-rne16-rne32-v1'
CUTOFF = 16
MAX_TAPE_CELLS = 262144


def require_count(value):
    if type(value) is not CountState:
        raise ContractError('complete immutable indexed count state required')
    value.__post_init__()
    IndexedRelation(value.n)
    if max(value.cursor, value.steps, sum(map(abs, value.counts))) > COUNTER_CAP:
        raise ArithmeticUnresolved('indexed AMP counter envelope exhausted')


def single(word):
    return widen(word, 32).exact


@dataclass(frozen=True)
class IndexedAmpState:
    encoded: CountState
    gradient_words: tuple[int, ...] = ()

    def __post_init__(self):
        if set(vars(self)) != {'encoded', 'gradient_words'}:
            raise ContractError('unregistered indexed CUDA raw learner coordinate')
        require_count(self.encoded)
        if (type(self.gradient_words) is not tuple
                or len(self.gradient_words) != (3 if self.encoded.pending is not None else 0)):
            raise ContractError('all three actual pending gradient words required')
        for word in self.gradient_words:
            single(word)

    @property
    def theta(self):
        return IndexedTheta(self.encoded.n, self.encoded.counts)

    @property
    def cursor(self):
        return self.encoded.cursor

    @property
    def unit_count(self):
        return int(self.encoded.pending is not None)


@dataclass(frozen=True)
class IndexedAmpPrediction:
    before: CountState
    query: tuple[int, int]
    words: tuple[int, ...]

    def __post_init__(self):
        require_count(self.before)
        if self.before.pending is not None:
            raise ContractError('indexed AMP prediction needs a committed predecessor')
        from .indexed_count import query
        if type(self.query) is not tuple or len(self.query) != 2:
            raise ContractError('complete ordered query required')
        query(self.before.n, *self.query)
        if type(self.words) is not tuple or len(self.words) != 7:
            raise ContractError('all seven actual readout words required')
        for word in self.words:
            single(word)

    def decoded(self):
        values = tuple(single(word) for word in self.words)
        return IndexedEvaluation(self.before, self.query, values[:2], values[2:4],
                                 values[4], values[5:], ())


@dataclass(frozen=True)
class IndexedAmpPlan:
    n: int
    query: tuple[int, int]
    support: tuple[tuple[int, int], ...]
    positions: tuple[int, ...]
    nodes: tuple[tuple, ...]
    partitions: tuple[int, int]
    power_tags: tuple[bool, ...]
    table_shape: tuple[tuple[str, int], ...]
    output_cells: int
    orders: tuple[tuple[int, ...], ...] = ()


def _prepare_prediction(program, state, rules, sources, *, output_cap, order_search=None, orders=None):
    if type(program) is not IndexedRelation or type(state) is not IndexedAmpState or state.unit_count:
        raise ContractError('owned indexed syntax and committed AMP state required')
    state.__post_init__()
    if state.encoded.n != program.n:
        raise ContractError('indexed AMP state differs from its program')
    query, _ = program.source_query(rules, sources)
    active = tuple((p, edge) for p, edge in enumerate(combinations(range(program.n), 2)) if state.encoded.counts[p])
    positions, support = tuple(p for p, _ in active), tuple(edge for _, edge in active)
    order = tuple(range(program.n-1))
    if orders is not None:
        if order_search is not None or type(orders) is not tuple or len(orders) != 1:
            raise ContractError('one complete global query order required')
        order = orders[0]
    elif order_search is not None:
        budget = DecodeAllowance()
        order = order_search(program.n, support, query, budget.join_cells, budget.live_cells)
    shape = partition_shape_plan(program.n, support, query, order, DecodeAllowance())
    tape_cells = sum(2 if i == 0 else 4 for i, j in support)+shape['positive_multiplications']+shape['positive_additions']+6
    allowance(tape_cells, MAX_TAPE_CELLS, 'indexed AMP tape-cell allowance')
    if sum(map(abs, state.encoded.counts))+tape_cells+4 > COUNTER_CAP:
        raise ArithmeticUnresolved('indexed AMP exponent envelope exhausted before execution')
    tape, _ = compile_tape(program.n, support, query, order=order)
    if len(tape.nodes) != tape_cells:
        raise ContractError('indexed AMP tape differs from its metadata preflight')
    return _finish_plan(program.n,query,support,positions,tuple(tape.nodes),
                        tape.partition_heads,tuple(shape.items()),output_cap,orders=(order,))


def _finish_plan(n,query,support,positions,nodes,partitions,shape,output_cap,*,orders=()):
    """Common syntactic power aliases and the unchanged scalar output tariff."""
    powers, general, additions = [], 0, 0
    for tag, *args in nodes:
        if tag in ('zero', 'one', 'nine', 'factor'):
            powers.append(tag != 'zero')
        else:
            a, b = args
            if tag == 'mul':
                general += int(not (powers[a] or powers[b]))
                powers.append(powers[a] and powers[b])
            elif tag == 'add':
                additions += 1
                powers.append(False)
            else:
                raise ContractError('unregistered indexed positive operation')
    # 18 constants/power-table outputs; four outputs per positive addition,
    # six per non-power product; twenty for the complete seven-value readout.
    cells = 38+6*general+4*additions
    allowance(cells, output_cap, 'indexed AMP numeric output allowance')
    return IndexedAmpPlan(n,query,support,positions,nodes,partitions,tuple(powers),shape,cells,orders)


def prepare_prediction(program, state, rules, sources, *, output_cap):
    """Construct a passive plan; its returned binding is checked by Runtime."""
    return _prepare_prediction(program,state,rules,sources,output_cap=output_cap)


def _same_plan_value(actual, expected):
    # Ordinary Python equality admits False==0 and 1.0==1. The registered
    # plan consists only of exact primitive types and finite tuples.
    if type(actual) is not type(expected):
        return False
    if type(expected) is tuple:
        return len(actual) == len(expected) and all(_same_plan_value(a,b) for a,b in zip(actual,expected))
    return type(expected) in (str,int,bool) and actual == expected


def check_prediction_plan(plan, program, state, rules, sources, *, output_cap, allow_orders=False):
    """Bind every plan coordinate to independently supplied owned inputs.

    This trusted reconstruction does not invoke the replaceable preparation
    helper. It checks the declared plan before execution and again before
    accepting the returned operation trace. No hashes or external plan IDs.
    """
    if type(allow_orders) is not bool or type(plan) is not IndexedAmpPlan:
        raise ContractError('registered plan and immutable order-class flag required')
    expected = _prepare_prediction(program,state,rules,sources,output_cap=output_cap,
                                   orders=plan.orders if allow_orders else None)
    _check_plan(plan,expected)


def _check_plan(plan,expected):
    if (type(plan) is not IndexedAmpPlan or vars(plan).keys() != vars(expected).keys()
            or any(not _same_plan_value(value,vars(expected)[key]) for key,value in vars(plan).items())):
        raise ContractError('indexed AMP plan differs from the declared owned input mapping')


@dataclass(frozen=True, eq=False)
class ResidentState:
    encoded: CountState
    gradient: object = None

    def __post_init__(self):
        if set(vars(self)) != {'encoded', 'gradient'}:
            raise ContractError('unregistered indexed CUDA learner coordinate')
        require_count(self.encoded)
        if self.gradient is None:
            if self.encoded.pending is not None:
                raise ContractError('pending indexed CUDA state lost its resident gradient')
        else:
            from .cuda_learner import _tensor
            _tensor(self.gradient, 'float32', dimension=1)
            if self.encoded.pending is None or self.gradient.numel() != 3:
                raise ContractError('indexed CUDA gradient has the wrong complete extent')

    @property
    def cursor(self):
        return self.encoded.cursor

    def tensors(self):
        return () if self.gradient is None else (('gradient', self.gradient),)

    def raw(self):
        from .cuda_learner import raw_tensor
        self.__post_init__()
        return IndexedAmpState(self.encoded, () if self.gradient is None else raw_tensor(self.gradient))


@dataclass(frozen=True, eq=False)
class ResidentPrediction:
    before: CountState
    query: tuple[int, int]
    readout: object

    def __post_init__(self):
        if set(vars(self)) != {'before', 'query', 'readout'}:
            raise ContractError('unregistered indexed CUDA prediction coordinate')
        require_count(self.before)
        from .cuda_learner import _tensor
        _tensor(self.readout, 'float32', dimension=1)
        if self.readout.numel() != 7 or self.before.pending is not None:
            raise ContractError('complete committed indexed CUDA readout required')

    def raw(self):
        from .cuda_learner import raw_tensor
        self.__post_init__()
        return IndexedAmpPrediction(self.before, self.query, raw_tensor(self.readout))


@dataclass(frozen=True)
class _Scalar:
    word: int
    width: int
    tensor: object = None

    @property
    def value(self):
        return widen(self.word, self.width).exact


class _Arithmetic:
    """One fixed scalar schedule; optional actual owned CudaArithmetic."""
    def __init__(self, bits, device_arithmetic=None):
        if bits < 1075:
            raise ArithmeticUnresolved('indexed AMP word checks need 1075 reference bits')
        self.bits, self.device = bits, device_arithmetic
        self.trace = []

    def op(self, tag, a=None, b=None, *, half=False, constant=None):
        width = 16 if half else 32
        negative_zero = False
        if tag == 'constant':
            exact = F(constant)
            negative_zero = False
        elif tag == 'cast':
            exact = a.value
            negative_zero = bool(a.word >> (a.width-1))
        else:
            av, bv = a.value, b.value
            if tag == 'div':
                if not bv:
                    raise ArithmeticUnresolved('indexed AMP division by zero')
                exact = _operation(av, F(bv.denominator, bv.numerator), multiply=True, bit_limit=self.bits)
            else:
                exact = _operation(av, bv, multiply=tag == 'mul', bit_limit=self.bits)
            sa, sb = a.word >> (a.width-1), b.word >> (b.width-1)
            negative_zero = bool(sa and sb) if tag == 'add' else bool(sa ^ sb)
        rounded = round_binary(exact, HALF if half else SINGLE, bit_limit=self.bits,
                               negative_zero=bool(not exact and negative_zero))
        number = -0.0 if not rounded.value and rounded.negative_zero else float(rounded.value)
        expected = int.from_bytes(struct.pack('<e' if half else '<f', number), 'little')
        tensor, word = None, expected
        if self.device is not None:
            if tag == 'constant':
                tensor = self.device.constant(F(constant))
            elif tag == 'cast':
                tensor = self.device.cast(a.tensor, 'float16' if half else 'float32')
            else:
                tensor = getattr(self.device, tag)(a.tensor, b.tensor)
            # A fresh read of the current phase's actual paid extent. Host
            # exponent/alias decisions below use this observed word.
            word = self.device._workspace.raw_words((tensor,), self.device._readout_buffer)[0][0]
            if word != expected:
                raise ContractError('actual indexed AMP operation differs from exact RNE')
        self.trace.append((tag, width, word))
        return _Scalar(word, width, tensor)

    def stack(self, scalars):
        if self.device is None:
            return None
        output = self.device.stack(tuple(s.tensor for s in scalars))
        actual = self.device._workspace.raw_words((output,), self.device._readout_buffer)[0]
        if actual != tuple(s.word for s in scalars):
            raise ContractError('indexed AMP output copy changed its actual source words')
        return output


@dataclass(frozen=True)
class _Wide:
    mantissa: _Scalar
    exponent: int


def _prediction_schedule(plan, state, arithmetic):
    if type(plan) is not IndexedAmpPlan or type(state) is not IndexedAmpState or state.unit_count:
        raise ContractError('complete indexed AMP plan/predecessor required')
    arith = arithmetic
    zero, one, nine = (arith.op('constant', constant=v) for v in (0, 1, 9))
    powers = [one]
    for _ in range(1, CUTOFF):
        powers.append(arith.op('div', powers[-1], nine))

    def normalized(mantissa, exponent):
        for _ in range(2):
            take = mantissa.value >= 9
            divided = arith.op('div', mantissa, nine)
            if take:
                mantissa, exponent = divided, exponent+1
        if not mantissa.value:
            exponent = 0
        if (mantissa.value and not 1 <= mantissa.value < 9) or not 0 <= exponent <= COUNTER_CAP:
            raise ArithmeticUnresolved('indexed AMP normalized coordinate exceeds its envelope')
        return _Wide(mantissa, exponent)

    values = []
    for k, (tag, *args) in enumerate(plan.nodes):
        if tag in ('zero', 'one', 'nine'):
            result = _Wide(zero if tag == 'zero' else one, int(tag == 'nine'))
        elif tag == 'factor':
            edge, parity = args
            d = state.encoded.counts[plan.positions[edge]]
            result = _Wide(one, max(d, 0) if parity == 0 else max(-d, 0))
        else:
            a, b = args
            left, right = values[a], values[b]
            if tag == 'mul':
                exponent = left.exponent+right.exponent
                if exponent+2 > COUNTER_CAP:
                    raise ArithmeticUnresolved('indexed AMP product exponent exhausted')
                if plan.power_tags[a] or plan.power_tags[b]:
                    power, other = (left, right) if plan.power_tags[a] else (right, left)
                    if power.mantissa.value != 1:
                        raise ContractError('indexed power alias lost its syntactic invariant')
                    result = _Wide(other.mantissa, exponent if other.mantissa.value else 0)
                else:
                    x, y = arith.op('cast', left.mantissa, half=True), arith.op('cast', right.mantissa, half=True)
                    product = arith.op('cast', arith.op('mul', x, y, half=True))
                    result = normalized(product, exponent)
            else:
                high, low = (left, right) if left.exponent >= right.exponent else (right, left)
                if high.exponent+2 > COUNTER_CAP:
                    raise ArithmeticUnresolved('indexed AMP sum exponent exhausted')
                difference = high.exponent-low.exponent
                coefficient = zero if difference >= CUTOFF else powers[difference]
                result = normalized(arith.op('add', high.mantissa,
                    arith.op('mul', low.mantissa, coefficient)), high.exponent)
        values.append(result)
    parts = tuple(values[k] for k in plan.partitions)
    high = max(p.exponent for p in parts)
    aligned = tuple(arith.op('mul', p.mantissa, zero if high-p.exponent >= CUTOFF else powers[high-p.exponent]) for p in parts)
    denominator = arith.op('add', *aligned)
    marginals = tuple(arith.op('div', p, denominator) for p in aligned)
    eight = arith.op('constant', constant=8)
    excesses = tuple(arith.op('mul', eight, p) for p in marginals)
    masses = tuple(arith.op('add', one, e) for e in excesses)
    normalizer = arith.op('add', *masses)
    probabilities = tuple(arith.op('div', m, normalizer) for m in masses)
    columns = excesses+masses+(normalizer,)+probabilities
    words = tuple(value.word for value in columns)
    raw = IndexedAmpPrediction(state.encoded, plan.query, words)
    result = arith.stack(columns)
    return raw, None if result is None else ResidentPrediction(state.encoded, plan.query, result)


def _observation_schedule(state, prediction, target, arithmetic, *, resident_prediction=None):
    if type(state) is not IndexedAmpState or type(prediction) is not IndexedAmpPrediction or state.encoded != prediction.before:
        raise ContractError('indexed observation lost its complete predecessor prediction')
    following = observe(state.encoded, *prediction.query, target)
    require_count(following)
    arith = arithmetic
    mass = _Scalar(prediction.words[2+target], 32,
        None if resident_prediction is None else resident_prediction.readout[2+target])
    one, eight, minus_one, minus_fifth, four_fifths = (arith.op('constant', constant=v)
        for v in (1, 8, -1, F(-1, 5), F(4, 5)))
    fixed = arith.op('add', arith.op('div', one, mass), minus_fifth)
    matching = arith.op('add', four_fifths, arith.op('mul', minus_one, arith.op('div', eight, mass)))
    columns = fixed, matching, four_fifths
    raw = IndexedAmpState(following, tuple(value.word for value in columns))
    output = arith.stack(columns)
    return raw, None if output is None else ResidentState(following, output)


def execute_prediction(plan, state, arithmetic):
    """Passive convenience; Runtime owns the fixed schedule directly.

    This function is not a delegated Runtime numerical port. A numerical
    workspace is authority over physical effects and stays in the owner.
    """
    return _prediction_schedule(plan, state, arithmetic)


def execute_observation(state, prediction, target, arithmetic, *, resident_prediction=None):
    """Passive convenience, with no Runtime continuation authority."""
    return _observation_schedule(state, prediction, target, arithmetic,
                                 resident_prediction=resident_prediction)


def _check_execution(expected, actual, arithmetic, operations):
    # Interpret the fixed schedule on independently retained inputs. The
    # helper's local trace/copy assertions cannot certify its later return.
    expected_operations = tuple(('host-RNE32-ingress' if tag == 'constant' else
        'cast-float'+str(width) if tag == 'cast' else tag, width, (word,))
        for tag, width, word in arithmetic.trace)
    if operations != expected_operations:
        raise ContractError('indexed AMP retained operations differ from the fixed RNE schedule')
    if actual != expected:
        raise ContractError('indexed AMP final endpoint differs from the fixed RNE schedule')
    return len(expected_operations)


def check_prediction_execution(plan, before, actual, operations, *, bit_limit):
    """Passive conformance check; neither adopts an endpoint nor signs it."""
    arithmetic = _Arithmetic(bit_limit)
    expected, _ = _prediction_schedule(plan, before, arithmetic)
    return _check_execution(expected, actual, arithmetic, operations)


def check_observation_execution(before, prediction, target, actual, operations, *, bit_limit):
    arithmetic = _Arithmetic(bit_limit)
    expected, _ = _observation_schedule(before, prediction, target, arithmetic)
    return _check_execution(expected, actual, arithmetic, operations)


def check_state(reference, raw, tolerance, *, bit_limit):
    if type(reference) is not IndexedState or type(raw) is not IndexedAmpState or reference.encoded != raw.encoded:
        raise ContractError('complete indexed reference/AMP count, clock or pending state differs')
    check = _Check(tolerance, bit_limit)
    if not raw.unit_count:
        return Float64Relation()
    i, j, target = raw.encoded.pending
    active = (0, 1, 2) if i != j else (0, 1 if target == 0 else 2)
    error = F(0)
    for k in active:
        error = check.error(error, reference.gradient_forms[k], single(raw.gradient_words[k]))
    check.bound(error, check.state_atol, 'complete indexed gradient error')
    return Float64Relation(state_error=error)


def check_prediction(reference, raw, tolerance, *, normalizer_cap, activation_cap, bit_limit):
    if (type(reference) is not IndexedEvaluation or type(raw) is not IndexedAmpPrediction
            or reference.before != raw.before or reference.query != raw.query):
        raise ContractError('indexed AMP cache lost its complete predecessor or ordered query')
    check = _Check(tolerance, bit_limit)
    cap = check.exact(normalizer_cap, 'indexed normalizer cap', positive=True)
    activation = check.exact(activation_cap, 'indexed activation cap', positive=True)
    observed = raw.decoded()
    for value in reference.masses+reference.probabilities+(reference.normalizer,):
        check.exact(value, 'indexed reference positive readout', positive=True)
    native = check.paired(reference.excesses+reference.masses, observed.excesses+observed.masses, 'indexed native heads')
    normalizer = check.error(F(0), reference.normalizer, observed.normalizer)
    probabilities = check.paired(reference.probabilities, observed.probabilities, 'indexed probabilities')
    for value in reference.activation_basis()+observed.activation_basis():
        check.exact(value, 'indexed activation', nonnegative=True)
        check.bound(value, activation, 'indexed activation')
    for value in observed.masses+observed.probabilities+(observed.normalizer,):
        check.exact(value, 'indexed positive readout', positive=True)
    ref_sum = check.add(*reference.masses)
    actual_sum = check.add(*observed.masses)
    if check.compare(ref_sum, reference.normalizer) != 0 or any(
            check.compare(check.add(F(1), e), m) != 0 for e, m in zip(reference.excesses, reference.masses)):
        raise ContractError('indexed reference readout is not its exact base/excess normalization')
    for value in (reference.normalizer, observed.normalizer, actual_sum):
        check.bound(value, cap, 'indexed normalizer or stored-mass sum')
    normalizer = check.error(normalizer, reference.normalizer, actual_sum)
    normalizer = check.error(normalizer, observed.normalizer, actual_sum)
    inverse_ref = F(ref_sum.denominator, ref_sum.numerator)
    inverse_actual = F(actual_sum.denominator, actual_sum.numerator)
    division = F(0)
    for rm, am, rp, ap in zip(reference.masses, observed.masses, reference.probabilities, observed.probabilities):
        check.bound(rp, F(1), 'indexed reference probability')
        check.bound(ap, F(1), 'indexed rounded probability')
        if check.compare(check.mul(rm, inverse_ref), rp) != 0:
            raise ContractError('indexed reference probability is not its exact normalized mass')
        proper = check.mul(am, inverse_actual)
        probabilities = check.error(probabilities, rp, proper)
        division = check.error(division, proper, ap)
    check.bound(native, tolerance.state_atol, 'indexed native coordinate error')
    check.bound(normalizer, tolerance.state_atol, 'indexed normalizer error')
    check.bound(probabilities, tolerance.probability_atol, 'indexed probability error')
    check.bound(division, tolerance.probability_atol, 'indexed stored-mass versus rounded probability error')
    return Float64Relation(native_error=native, normalizer_error=normalizer,
                           probability_error=probabilities, division_error=division)


@dataclass(frozen=True)
class IndexedAmpRange:
    theta: IndexedTheta
    domain: CategoricalPairDomain
    proof: str = 'indexed-radix9-positive-mass-box-for-all-admitted-categorical-forecasts-v1'

    masses_upper = (F(9), F(9))
    base_lower = (F(1), F(1))
    stored_mass_sum_upper = F(18)
    rounded_normalizer_upper = F(18)


def range_bound(program, rules, raw, domain, *, normalizer_cap, activation_cap):
    program.validate(rules)
    if (type(raw) is not IndexedAmpState or raw.encoded.n != program.n
            or type(domain) is not CategoricalPairDomain or domain.n != program.n):
        raise ContractError('indexed AMP range lost its complete state and domain binding')
    # The rounded sum of two nonnegative single values is >= either input.
    # Thus aligned-part / rounded-sum lies in [0,1], its rounded product by
    # eight in [0,8], and each stored mass in [1,9]. Two masses sum to <=18.
    # Guards can stop a prediction before a target; no failed phase is scored.
    if normalizer_cap < 18 or activation_cap < 8:
        raise ArithmeticUnresolved('indexed AMP full-domain mass box exceeds the registered range caps')
    return IndexedAmpRange(raw.theta, domain)


def stored_probability(prediction, target, *, bit_limit):
    if type(prediction) is not IndexedAmpPrediction or type(target) is not int or target not in (0, 1):
        raise ContractError('complete indexed forecast and independently observed target required')
    masses = tuple(single(word) for word in prediction.words[2:4])
    if min(masses) <= 0:
        raise ArithmeticUnresolved('indexed CUDA stored mass is not positive')
    total = _operation(*masses, multiply=False, bit_limit=bit_limit)
    return _operation(masses[target], F(total.denominator, total.numerator), multiply=True, bit_limit=bit_limit)
