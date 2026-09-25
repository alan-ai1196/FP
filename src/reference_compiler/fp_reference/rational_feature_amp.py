"""Complete rational-feature AMP coordinates and the fixed scalar schedule.

Counts/Gamma encode the exact parameters. Actual device words encode the
readout, every feature coefficient and the full pending gradient basis.
The existing Runtime owns all inputs, parts, storage and publication.
"""
from dataclasses import dataclass
from fractions import Fraction as F
from itertools import product

from .core import ContractError
from .float64_bridge import Float64Relation, _ReducedCheck as _Check
from .indexed_amp import _Arithmetic, _Scalar, _check_execution
from .indexed_execution import CategoricalPairDomain
from .indexed_relation import allowance
from .joint_execution import JointState, JointTheta, JointEvaluation, closed
from .joint_relation import JointRelation, JointCountState, require_state, observe
from .joint_amp import single, _trace
from . import joint_partition_decoder as decoder
from .semantics import ArithmeticUnresolved, Evaluation, _operation

BACKEND_ID = 'owned-indexed-rational-features-full-rate-parts-amp-v1'
FORWARD_ID = 'rational-features-half-excess-single-coefficients-and-full-gradient-v1'
WORK_MODEL = 'prepaid-rational-feature-parts-and-gcd-reduced-complete-native-relation-v2'


def require_model(model):
    closed(model, JointRelation)
    model.__post_init__()
    C = model.feature_scale
    if C is None:
        raise ContractError('rational-feature AMP requires its complete distinct G/Gamma')
    if C.denominator != 1 or not 3 <= C <= 1 << 24:
        raise ArithmeticUnresolved('this rational-feature AMP schedule requires integer native scale in [3, 2^24]')


def _parts(model, parts, normalization):
    if (type(parts) is not tuple or len(parts) != len(model.rates)
            or type(normalization) is not int or normalization <= 0
            or any(type(row) is not tuple or len(row) != 2
                   or any(type(v) is not int or v < 0 for v in row) for row in parts)
            or sum(map(sum, parts)) != normalization):
        raise ContractError('complete rational-feature unnormalized rate/parity parts required')


@dataclass(frozen=True)
class JointAmpState:
    encoded: JointCountState
    gradient_words: tuple[int, ...] = ()

    def __post_init__(self):
        closed(self, JointAmpState)
        require_state(self.encoded)
        require_model(self.encoded.model)
        count = 4*len(self.encoded.model.rates) if self.encoded.pending is not None else 0
        if type(self.gradient_words) is not tuple or len(self.gradient_words) != count:
            raise ContractError('all rational-feature fixed and selected gradient words required')
        for word in self.gradient_words:
            single(word)

    @property
    def theta(self):
        s = self.encoded
        return JointTheta(s.model, s.counts, s.diagonal, s.steps)

    @property
    def cursor(self):
        return self.encoded.cursor

    @property
    def unit_count(self):
        return int(self.encoded.pending is not None)


@dataclass(frozen=True)
class JointAmpPrediction:
    before: JointCountState
    query: tuple[int, int]
    words: tuple[int, ...]
    rate_parts: tuple[tuple[int, int], ...]
    normalization: int

    def __post_init__(self):
        closed(self, JointAmpPrediction)
        require_state(self.before)
        require_model(self.before.model)
        self.before.model.query(self.query)
        if (self.before.pending is not None or type(self.words) is not tuple
                or len(self.words) != 7+self.before.model.fixed_slots):
            raise ContractError('complete rational-feature readout and coefficient words required')
        for word in self.words:
            single(word)
        _parts(self.before.model, self.rate_parts, self.normalization)

    def decoded(self):
        self.__post_init__()
        return DecodedPrediction(self)


@dataclass(frozen=True)
class DecodedPrediction:
    """Passive complete native cache view; never an input to a Runtime phase."""
    raw: JointAmpPrediction

    def __post_init__(self):
        closed(self, DecodedPrediction)
        closed(self.raw, JointAmpPrediction)
        self.raw.__post_init__()

    @property
    def excesses(self):
        return tuple(single(w) for w in self.raw.words[:2])

    @property
    def masses(self):
        return tuple(single(w) for w in self.raw.words[2:4])

    @property
    def normalizer(self):
        return single(self.raw.words[4])

    @property
    def probabilities(self):
        return tuple(single(w) for w in self.raw.words[5:7])

    @property
    def coefficients(self):
        return tuple(single(w) for w in self.raw.words[7:])

    def activation_basis(self):
        return (F(0), F(1))+self.coefficients+self.excesses

    def materialize(self, *, scalar_cap):
        self.__post_init__()
        model, query = self.raw.before.model, self.raw.query
        allowance(model.counts()['nodes']+7, scalar_cap, 'rational-feature cache output allowance')
        sources = tuple(F(v == query[side]) for side in (0, 1) for v in range(model.n))
        pairs = tuple(F((i, j) == query) for i, j in product(range(model.n), repeat=2))
        coefficients, features = self.coefficients, []
        for rank in range(model.K):
            rate, world = model.hypothesis(rank)
            parity = model.world_bit(world, query[0])^model.world_bit(world, query[1])
            features.extend(coefficients[2*rate+int(parity != y)] for y in (0, 1))
        return Evaluation(sources+pairs+tuple(features)+self.excesses, self.excesses,
                          self.masses, self.normalizer, self.probabilities, ())


@dataclass(frozen=True, eq=False)
class ResidentState:
    encoded: JointCountState
    gradient: object = None

    def __post_init__(self):
        closed(self, ResidentState)
        require_state(self.encoded)
        require_model(self.encoded.model)
        if self.gradient is None:
            if self.encoded.pending is not None:
                raise ContractError('pending rational-feature state lost its resident gradients')
        else:
            from .cuda_learner import _tensor
            _tensor(self.gradient, 'float32', dimension=1)
            if self.encoded.pending is None or self.gradient.numel() != 4*len(self.encoded.model.rates):
                raise ContractError('rational-feature gradients have the wrong complete extent')

    @property
    def cursor(self):
        return self.encoded.cursor

    def tensors(self):
        return () if self.gradient is None else (('gradient', self.gradient),)

    def raw(self):
        from .cuda_learner import raw_tensor
        self.__post_init__()
        return JointAmpState(self.encoded, () if self.gradient is None else raw_tensor(self.gradient))


@dataclass(frozen=True, eq=False)
class ResidentPrediction:
    before: JointCountState
    query: tuple[int, int]
    readout: object
    rate_parts: tuple[tuple[int, int], ...]
    normalization: int

    def __post_init__(self):
        closed(self, ResidentPrediction)
        require_state(self.before)
        require_model(self.before.model)
        self.before.model.query(self.query)
        _parts(self.before.model, self.rate_parts, self.normalization)
        from .cuda_learner import _tensor
        _tensor(self.readout, 'float32', dimension=1)
        if self.before.pending is not None or self.readout.numel() != 7+self.before.model.fixed_slots:
            raise ContractError('complete rational-feature resident cache extent required')

    def raw(self):
        from .cuda_learner import raw_tensor
        self.__post_init__()
        return JointAmpPrediction(self.before, self.query, raw_tensor(self.readout), self.rate_parts, self.normalization)


def relation_work(model):
    require_model(model)
    # The registered exact value/order verifier prices the GCD/quotient work;
    # it does not inherit the cheaper raw-product relation tariff.
    # Prediction arithmetic is <= 592*J+4504 primitives, state <= 640*J+72;
    # the larger allowance also funds complete closed-type/value validation.
    return 2048*(model.n*(model.n-1)//2+2*model.n+8*len(model.rates)+32)


def forward_work(model, budget, output_cap):
    require_model(model)
    envelope = (model.n+model.prior_scale.bit_length()+(budget.step_cap+1)*(model.scale-1).bit_length()
                +model.partition_extra_bits)
    return 2*decoder.construction_work(model, budget)+1024*(envelope+4*len(model.rates)+1)+128*(model.n+1)*output_cap


def prediction_output_cells(plan):
    return plan.output_cells+2*plan.before.model.fixed_slots


def observation_output_cells(prediction):
    prediction.__post_init__()
    parts = prediction.rate_parts
    return 6+20*len(parts)+3*sum(bool(sum(row))+sum(bool(v) for v in row) for row in parts)


def _prepare_prediction(program, state, rules, sources, *, output_cap, budget, workspace, bit_limit):
    closed(state, JointAmpState)
    state.__post_init__()
    if state.unit_count:
        raise ContractError('rational-feature AMP requires its complete committed state')
    with memoryview(workspace) as borrowed:
        plan = decoder.prepare_bound(program, state.encoded, rules, sources, budget, borrowed, bit_limit=bit_limit)
    allowance(prediction_output_cells(plan), output_cap, 'rational-feature prediction output allowance')
    return plan


def check_prediction_plan(plan, program, state, rules, sources, **kwargs):
    expected = _prepare_prediction(program, state, rules, sources, **kwargs)
    if not decoder._same(plan, expected):
        raise ContractError('rational-feature plan differs from its complete actual input and paid extent')


def _prediction_schedule(plan, state, arithmetic):
    closed(plan, decoder.JointPartitionPlan)
    closed(state, JointAmpState)
    state.__post_init__()
    if plan.before != state.encoded or state.unit_count or arithmetic.bits != plan.bit_limit:
        raise ContractError('rational-feature schedule lost its complete predecessor or precision')
    _parts(state.encoded.model, plan.rate_parts, plan.normalization)
    common = max(value.bit_length() for value in plan.excesses)
    scaled = []
    for value in plan.excesses:
        if not value:
            scaled.append(arithmetic.op('constant', constant=0))
            continue
        bits = value.bit_length()
        mantissa = arithmetic.op('constant', constant=F(value, 1 << bits))
        quantized = arithmetic.op('cast', arithmetic.op('cast', mantissa, half=True))
        power = F(0) if bits-common < -149 else F(1, 1 << (common-bits))
        scaled.append(arithmetic.op('mul', quantized, arithmetic.op('constant', constant=power)))
    denominator = arithmetic.op('add', *scaled)
    fractions = tuple(arithmetic.op('div', value, denominator) for value in scaled)
    model = state.encoded.model
    one, scale = (arithmetic.op('constant', constant=v) for v in (1, model.native_scale-2))
    excesses = tuple(arithmetic.op('mul', scale, value) for value in fractions)
    masses = tuple(arithmetic.op('add', one, value) for value in excesses)
    normalizer = arithmetic.op('add', *masses)
    probabilities = tuple(arithmetic.op('div', value, normalizer) for value in masses)
    coefficients = tuple(arithmetic.op('constant', constant=c)
                         for j in range(len(model.rates)) for c in model.coefficients(j))
    columns = excesses+masses+(normalizer,)+probabilities+coefficients
    output = arithmetic.stack(columns)
    raw = JointAmpPrediction(plan.before, plan.query, tuple(v.word for v in columns), plan.rate_parts, plan.normalization)
    return raw, None if output is None else ResidentPrediction(plan.before, plan.query, output, plan.rate_parts, plan.normalization)


def _observation_schedule(state, prediction, target, arithmetic, *, resident_prediction=None):
    closed(state, JointAmpState)
    closed(prediction, JointAmpPrediction)
    state.__post_init__()
    prediction.__post_init__()
    if state.encoded != prediction.before:
        raise ContractError('rational-feature observation lost its actual predecessor prediction')
    following = observe(state.encoded, prediction.query, target)
    mass = _Scalar(prediction.words[2+target], 32,
        None if resident_prediction is None else resident_prediction.readout[2+target])
    scale = state.encoded.model.native_scale
    one, common, inverse_scale, negative = (arithmetic.op('constant', constant=v)
        for v in (1, (scale-2)/scale, 1/scale, -1))
    inverse_mass = arithmetic.op('div', one, mass)
    total_bits = prediction.normalization.bit_length()
    denominator = arithmetic.op('constant', constant=F(prediction.normalization, 1 << total_bits))

    def fraction(numerator):
        if not numerator:
            return arithmetic.op('constant', constant=0)
        bits = numerator.bit_length()
        mantissa = arithmetic.op('constant', constant=F(numerator, 1 << bits))
        quotient = arithmetic.op('div', mantissa, denominator)
        power = F(0) if bits-total_bits < -149 else F(1, 1 << (total_bits-bits))
        return arithmetic.op('mul', quotient, arithmetic.op('constant', constant=power))

    fixed = []
    for row in prediction.rate_parts:
        marginal = fraction(sum(row))
        first = arithmetic.op('mul', marginal, inverse_scale)
        for y in (target, 1-target):
            match = fraction(row[y])
            second = arithmetic.op('mul', match, inverse_mass)
            fixed.append(arithmetic.op('add', first, arithmetic.op('mul', negative, second)))
    selected = tuple(arithmetic.op('add', common, arithmetic.op('mul', inverse_mass,
        arithmetic.op('constant', constant=-c))) for j in range(len(state.encoded.model.rates))
        for c in state.encoded.model.coefficients(j))
    columns = tuple(fixed)+selected
    output = arithmetic.stack(columns)
    raw = JointAmpState(following, tuple(v.word for v in columns))
    return raw, None if output is None else ResidentState(following, output)


def check_prediction_execution(plan, before, actual, operations, *, bit_limit):
    closed(actual, JointAmpPrediction)
    actual.__post_init__()
    _trace(operations)
    arithmetic = _Arithmetic(bit_limit)
    expected, _ = _prediction_schedule(plan, before, arithmetic)
    return _check_execution(expected, actual, arithmetic, operations)


def check_observation_execution(before, prediction, target, actual, operations, *, bit_limit):
    closed(actual, JointAmpState)
    actual.__post_init__()
    _trace(operations)
    arithmetic = _Arithmetic(bit_limit)
    expected, _ = _observation_schedule(before, prediction, target, arithmetic)
    return _check_execution(expected, actual, arithmetic, operations)


def check_state(reference, raw, tolerance, *, bit_limit):
    closed(reference, JointState)
    closed(raw, JointAmpState)
    reference.__post_init__()
    raw.__post_init__()
    if reference.encoded != raw.encoded:
        raise ContractError('rational-feature complete model/counts/clocks/pending state differ')
    check, error = _Check(tolerance, bit_limit), F(0)
    if raw.unit_count:
        i, j, target = raw.encoded.pending
        J = len(raw.encoded.model.rates)
        modes = (0, 1) if i != j else (target,)
        active = tuple(range(2*J))+tuple(2*J+2*k+m for k in range(J) for m in modes)
        for k in active:
            error = check.error(error, reference.gradient_forms[k], single(raw.gradient_words[k]))
    check.bound(error, check.state_atol, 'complete rational-feature native gradient error')
    return Float64Relation(state_error=error)


def check_prediction(reference, raw, tolerance, *, normalizer_cap, activation_cap, bit_limit):
    closed(reference, JointEvaluation)
    closed(raw, JointAmpPrediction)
    reference.__post_init__()
    raw.__post_init__()
    if (reference.before != raw.before or reference.query != raw.query
            or reference.rate_parts != raw.rate_parts or reference.normalization != raw.normalization):
        raise ContractError('rational-feature cache lost its complete actual parts or native inputs')
    check = _Check(tolerance, bit_limit)
    cap = check.exact(normalizer_cap, 'rational-feature normalizer cap', positive=True)
    activation = check.exact(activation_cap, 'rational-feature activation cap', positive=True)
    actual = raw.decoded()
    native = check.paired(reference.activation_basis()+reference.masses,
                          actual.activation_basis()+actual.masses, 'complete rational-feature native cache')
    normalizer = check.error(F(0), reference.normalizer, actual.normalizer)
    probabilities = check.paired(reference.probabilities, actual.probabilities, 'rational-feature probabilities')
    for value in reference.activation_basis()+actual.activation_basis():
        check.exact(value, 'rational-feature activation', nonnegative=True)
        check.bound(value, activation, 'rational-feature activation')
    for value in reference.masses+reference.probabilities+(reference.normalizer,)+actual.masses+actual.probabilities+(actual.normalizer,):
        check.exact(value, 'rational-feature positive readout', positive=True)
    ref_sum, actual_sum = check.add(*reference.masses), check.add(*actual.masses)
    if (reference.normalizer != reference.before.model.native_scale or check.compare(ref_sum, reference.normalizer) != 0
            or any(check.compare(check.add(F(1), e), m) != 0 for e, m in zip(reference.excesses, reference.masses))):
        raise ContractError('rational-feature exact reference readout lost its native normalization')
    for value in (reference.normalizer, actual.normalizer, actual_sum):
        check.bound(value, cap, 'rational-feature normalizer or actual stored-mass sum')
    normalizer = check.error(normalizer, reference.normalizer, actual_sum)
    normalizer = check.error(normalizer, actual.normalizer, actual_sum)
    inverse_ref, inverse_actual = 1/ref_sum, 1/actual_sum
    division = F(0)
    for rm, am, rp, ap in zip(reference.masses, actual.masses, reference.probabilities, actual.probabilities):
        check.bound(rp, F(1), 'rational-feature reference probability')
        check.bound(ap, F(1), 'rational-feature rounded probability')
        if check.compare(check.mul(rm, inverse_ref), rp) != 0:
            raise ContractError('rational-feature reference probability is not its normalized mass')
        proper = check.mul(am, inverse_actual)
        probabilities = check.error(probabilities, rp, proper)
        division = check.error(division, proper, ap)
    for error, limit, label in ((native, tolerance.state_atol, 'native coordinate'),
            (normalizer, tolerance.state_atol, 'normalizer'), (probabilities, tolerance.probability_atol, 'probability'),
            (division, tolerance.probability_atol, 'stored-mass versus rounded probability')):
        check.bound(error, limit, 'rational-feature '+label+' error')
    return Float64Relation(native_error=native, normalizer_error=normalizer,
                          probability_error=probabilities, division_error=division)


@dataclass(frozen=True)
class JointAmpRange:
    theta: JointTheta
    domain: CategoricalPairDomain
    proof: str = 'rational-feature-positive-excess-and-rounded-coefficient-whole-domain-box-v1'

    def __post_init__(self):
        closed(self, JointAmpRange)
        closed(self.theta, JointTheta)
        self.theta.__post_init__()
        require_model(self.theta.schema)
        closed(self.domain, CategoricalPairDomain)
        self.domain.__post_init__()
        if self.domain.n != self.theta.schema.n or type(self.proof) is not str or self.proof != type(self).proof:
            raise ContractError('rational-feature range lost its complete native declaration')

    @property
    def masses_upper(self):
        return (self.theta.schema.native_scale-1,)*2

    @property
    def base_lower(self):
        return (F(1),)*2

    @property
    def stored_mass_sum_upper(self):
        return 2*(self.theta.schema.native_scale-1)

    @property
    def rounded_normalizer_upper(self):
        return self.stored_mass_sum_upper


def range_bound(program, rules, raw, domain, *, normalizer_cap, activation_cap):
    closed(program, JointRelation)
    closed(raw, JointAmpState)
    closed(domain, CategoricalPairDomain)
    program.validate(rules)
    raw.__post_init__()
    domain.__post_init__()
    if raw.encoded.model != program or domain.n != program.n:
        raise ContractError('rational-feature whole-domain range lost its actual model/state/input')
    if normalizer_cap < 2*(program.native_scale-1) or activation_cap < program.native_scale-2:
        raise ArithmeticUnresolved('rational-feature whole-domain box exceeds the registered range caps')
    return JointAmpRange(raw.theta, domain)


def stored_probability(prediction, target, *, bit_limit):
    closed(prediction, JointAmpPrediction)
    prediction.__post_init__()
    if type(target) is not int or target not in (0, 1):
        raise ContractError('independently observed actual binary target required')
    masses = tuple(single(word) for word in prediction.words[2:4])
    if min(masses) <= 0:
        raise ArithmeticUnresolved('rational-feature stored masses are not positive')
    total = _operation(*masses, multiply=False, bit_limit=bit_limit)
    return _operation(masses[target], F(total.denominator, total.numerator), multiply=True, bit_limit=bit_limit)
