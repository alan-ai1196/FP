"""Fixed joint-noise AMP coordinates, scalar schedule and passive relations.

The existing Runtime owns execution, causal inputs, storage and authority.
Exact count coordinates encode parameters; device words encode the actual
readout and pending gradient basis of the original joint native graph.
"""
from dataclasses import dataclass
from fractions import Fraction as F

from .core import ContractError
from .cuda_range import widen
from .float64_bridge import Float64Relation, _Check
from .indexed_amp import _Arithmetic, _Scalar, _check_execution
from .indexed_execution import CategoricalPairDomain
from .indexed_relation import allowance
from .joint_execution import JointState, JointTheta, JointEvaluation, closed
from .joint_relation import JointRelation, JointCountState, require_state, observe
from . import joint_partition_decoder as decoder
from .semantics import ArithmeticUnresolved, _operation

BACKEND_ID = 'owned-indexed-joint-noise-half-mantissas-single-readout-v1'
FORWARD_ID = 'joint-noise-integer-excess-half-mantissas-single-readout-v1'
WORK_MODEL = 'prepaid-joint-noise-integer-parts-and-full-rne-basis-v1'


def single(word):
    return widen(word, 32).exact


def require_unit_feature_model(model):
    closed(model, JointRelation)
    model.__post_init__()
    if model.feature_scale is not None:
        raise ContractError('rational-feature G/Gamma requires its own complete AMP gradient and cache registration')


@dataclass(frozen=True)
class JointAmpState:
    encoded: JointCountState
    gradient_words: tuple[int, ...] = ()

    def __post_init__(self):
        closed(self, JointAmpState)
        require_state(self.encoded)
        require_unit_feature_model(self.encoded.model)
        count = 2*len(self.encoded.model.rates)+1 if self.encoded.pending is not None else 0
        if type(self.gradient_words) is not tuple or len(self.gradient_words) != count:
            raise ContractError('complete joint AMP pending gradient words required')
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

    def __post_init__(self):
        closed(self, JointAmpPrediction)
        require_state(self.before)
        require_unit_feature_model(self.before.model)
        self.before.model.query(self.query)
        if self.before.pending is not None or type(self.words) is not tuple or len(self.words) != 7:
            raise ContractError('complete committed joint AMP prediction required')
        for word in self.words:
            single(word)

    def decoded(self):
        self.__post_init__()
        values = tuple(single(word) for word in self.words)
        return JointEvaluation(self.before, self.query, values[:2], values[2:4], values[4], values[5:], ())


@dataclass(frozen=True, eq=False)
class ResidentState:
    encoded: JointCountState
    gradient: object = None

    def __post_init__(self):
        closed(self, ResidentState)
        require_state(self.encoded)
        require_unit_feature_model(self.encoded.model)
        if self.gradient is None:
            if self.encoded.pending is not None:
                raise ContractError('pending joint AMP state lost its resident gradient')
        else:
            from .cuda_learner import _tensor
            _tensor(self.gradient, 'float32', dimension=1)
            if self.encoded.pending is None or self.gradient.numel() != 2*len(self.encoded.model.rates)+1:
                raise ContractError('joint AMP gradient has the wrong complete extent')

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

    def __post_init__(self):
        closed(self, ResidentPrediction)
        require_state(self.before)
        require_unit_feature_model(self.before.model)
        self.before.model.query(self.query)
        from .cuda_learner import _tensor
        _tensor(self.readout, 'float32', dimension=1)
        if self.before.pending is not None or self.readout.numel() != 7:
            raise ContractError('complete committed joint AMP readout required')

    def raw(self):
        from .cuda_learner import raw_tensor
        self.__post_init__()
        return JointAmpPrediction(self.before, self.query, raw_tensor(self.readout))


def forward_work(model, budget, output_cap):
    # Construction plus independent actual-input reconstruction, scalar RNE
    # replay and complete coordinate scans. Not a bigint or host-time bound.
    require_unit_feature_model(model)
    envelope = model.n+model.prior_scale.bit_length()+(budget.step_cap+1)*(model.scale-1).bit_length()
    return 2*decoder.construction_work(model, budget)+1024*(envelope+len(model.rates)+1)+128*(model.n+1)*output_cap


def _prepare_prediction(program, state, rules, sources, *, output_cap, budget, workspace, bit_limit):
    closed(state, JointAmpState)
    state.__post_init__()
    if state.unit_count:
        raise ContractError('joint AMP prediction requires its complete committed state')
    with memoryview(workspace) as borrowed:
        plan = decoder.prepare_bound(program, state.encoded, rules, sources, budget, borrowed, bit_limit=bit_limit)
    allowance(plan.output_cells, output_cap, 'joint AMP prediction output allowance')
    return plan


def check_prediction_plan(plan, program, state, rules, sources, **kwargs):
    expected = _prepare_prediction(program, state, rules, sources, **kwargs)
    if not decoder._same(plan, expected):
        raise ContractError('joint AMP plan differs from its independently retained actual inputs')


def _prediction_schedule(plan, state, arithmetic):
    closed(plan, decoder.JointPartitionPlan)
    closed(state, JointAmpState)
    state.__post_init__()
    if plan.before != state.encoded or state.unit_count or arithmetic.bits != plan.bit_limit:
        raise ContractError('joint AMP schedule lost its complete predecessor or arithmetic allowance')
    common = max(value.bit_length() for value in plan.excesses)
    scaled = []
    for value in plan.excesses:
        if value == 0:
            scaled.append(arithmetic.op('constant', constant=0))
            continue
        bits = value.bit_length()
        mantissa = arithmetic.op('constant', constant=F(value, 1 << bits))
        quantized = arithmetic.op('cast', arithmetic.op('cast', mantissa, half=True))
        power = F(0) if bits-common < -149 else F(1, 1 << (common-bits))
        scaled.append(arithmetic.op('mul', quantized, arithmetic.op('constant', constant=power)))
    denominator = arithmetic.op('add', *scaled)
    fractions = tuple(arithmetic.op('div', value, denominator) for value in scaled)
    one, scale = (arithmetic.op('constant', constant=v) for v in (1, state.encoded.model.scale-2))
    excesses = tuple(arithmetic.op('mul', scale, value) for value in fractions)
    masses = tuple(arithmetic.op('add', one, value) for value in excesses)
    normalizer = arithmetic.op('add', *masses)
    probabilities = tuple(arithmetic.op('div', value, normalizer) for value in masses)
    columns = excesses+masses+(normalizer,)+probabilities
    output = arithmetic.stack(columns)
    raw = JointAmpPrediction(plan.before, plan.query, tuple(v.word for v in columns))
    return raw, None if output is None else ResidentPrediction(plan.before, plan.query, output)


def _observation_schedule(state, prediction, target, arithmetic, *, resident_prediction=None):
    closed(state, JointAmpState)
    closed(prediction, JointAmpPrediction)
    state.__post_init__()
    prediction.__post_init__()
    if state.encoded != prediction.before:
        raise ContractError('joint AMP observation lost its complete predecessor prediction')
    following = observe(state.encoded, prediction.query, target)
    mass = _Scalar(prediction.words[2+target], 32,
        None if resident_prediction is None else resident_prediction.readout[2+target])
    scale = state.encoded.model.scale
    one, common, constant = (arithmetic.op('constant', constant=v) for v in (1, F(scale-2, scale), F(-2, scale)))
    reciprocal = arithmetic.op('div', one, mass)
    fixed = arithmetic.op('add', reciprocal, constant)
    gradients = tuple(arithmetic.op('add', common, arithmetic.op('mul', reciprocal,
        arithmetic.op('constant', constant=-c))) for j in range(len(state.encoded.model.rates))
        for c in state.encoded.model.coefficients(j))
    columns = (fixed,)+gradients
    output = arithmetic.stack(columns)
    raw = JointAmpState(following, tuple(v.word for v in columns))
    return raw, None if output is None else ResidentState(following, output)


def _trace(operations):
    if type(operations) is not tuple:
        raise ContractError('complete immutable joint AMP operation trace required')
    for row in operations:
        if (type(row) is not tuple or len(row) != 3 or type(row[0]) is not str
                or type(row[1]) is not int or row[1] not in (16, 32)
                or type(row[2]) is not tuple or len(row[2]) != 1 or type(row[2][0]) is not int):
            raise ContractError('joint AMP trace lost its closed operation/word types')
        widen(row[2][0], row[1])


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
        raise ContractError('joint reference/AMP complete model, counts, diagonal, clocks or pending event differ')
    check = _Check(tolerance, bit_limit)
    error = F(0)
    if raw.unit_count:
        i, j, target = raw.encoded.pending
        modes = (0, 1) if i != j else (target,)
        active = (0,)+tuple(1+2*k+m for k in range(len(raw.encoded.model.rates)) for m in modes)
        for k in active:
            error = check.error(error, reference.gradient_forms[k], single(raw.gradient_words[k]))
    check.bound(error, check.state_atol, 'complete joint native gradient error')
    return Float64Relation(state_error=error)


def check_prediction(reference, raw, tolerance, *, normalizer_cap, activation_cap, bit_limit):
    closed(reference, JointEvaluation)
    closed(raw, JointAmpPrediction)
    reference.__post_init__()
    raw.__post_init__()
    if reference.before != raw.before or reference.query != raw.query:
        raise ContractError('joint AMP cache lost its actual complete predecessor or ordered source query')
    check = _Check(tolerance, bit_limit)
    cap = check.exact(normalizer_cap, 'joint normalizer cap', positive=True)
    activation = check.exact(activation_cap, 'joint activation cap', positive=True)
    actual = raw.decoded()
    native = check.paired(reference.excesses+reference.masses, actual.excesses+actual.masses, 'joint native readout')
    normalizer = check.error(F(0), reference.normalizer, actual.normalizer)
    probabilities = check.paired(reference.probabilities, actual.probabilities, 'joint probabilities')
    for value in reference.activation_basis()+actual.activation_basis():
        check.exact(value, 'joint activation', nonnegative=True)
        check.bound(value, activation, 'joint activation')
    for value in reference.masses+reference.probabilities+(reference.normalizer,)+actual.masses+actual.probabilities+(actual.normalizer,):
        check.exact(value, 'joint positive readout', positive=True)
    ref_sum, actual_sum = check.add(*reference.masses), check.add(*actual.masses)
    if (reference.normalizer != reference.before.model.scale or check.compare(ref_sum, reference.normalizer) != 0
            or any(check.compare(check.add(F(1), e), m) != 0 for e, m in zip(reference.excesses, reference.masses))):
        raise ContractError('joint exact reference masses lost their native normalization')
    for value in (reference.normalizer, actual.normalizer, actual_sum):
        check.bound(value, cap, 'joint normalizer or actual stored-mass sum')
    normalizer = check.error(normalizer, reference.normalizer, actual_sum)
    normalizer = check.error(normalizer, actual.normalizer, actual_sum)
    inverse_ref, inverse_actual = 1/ref_sum, 1/actual_sum
    division = F(0)
    for rm, am, rp, ap in zip(reference.masses, actual.masses, reference.probabilities, actual.probabilities):
        check.bound(rp, F(1), 'joint reference probability')
        check.bound(ap, F(1), 'joint rounded probability')
        if check.compare(check.mul(rm, inverse_ref), rp) != 0:
            raise ContractError('joint reference probability is not its exact normalized mass')
        proper = check.mul(am, inverse_actual)
        probabilities = check.error(probabilities, rp, proper)
        division = check.error(division, proper, ap)
    for error, limit, label in ((native, tolerance.state_atol, 'native coordinate'),
            (normalizer, tolerance.state_atol, 'normalizer'), (probabilities, tolerance.probability_atol, 'probability'),
            (division, tolerance.probability_atol, 'stored-mass versus rounded probability')):
        check.bound(error, limit, 'joint '+label+' error')
    return Float64Relation(native_error=native, normalizer_error=normalizer,
        probability_error=probabilities, division_error=division)


@dataclass(frozen=True)
class JointAmpRange:
    theta: JointTheta
    domain: CategoricalPairDomain
    proof: str = 'joint-positive-excess-rne-mass-box-for-all-admitted-categorical-forecasts-v1'

    def __post_init__(self):
        closed(self, JointAmpRange)
        closed(self.theta, JointTheta)
        self.theta.__post_init__()
        require_unit_feature_model(self.theta.schema)
        closed(self.domain, CategoricalPairDomain)
        self.domain.__post_init__()
        if self.domain.n != self.theta.schema.n or type(self.proof) is not str or self.proof != type(self).proof:
            raise ContractError('joint AMP range lost its complete native declaration')

    @property
    def masses_upper(self):
        return (F(self.theta.schema.scale-1),)*2

    @property
    def base_lower(self):
        return (F(1),)*2

    @property
    def stored_mass_sum_upper(self):
        return F(2*(self.theta.schema.scale-1))

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
        raise ContractError('joint AMP whole-domain range lost its complete model/state/input binding')
    # Each rounded positive part/shared sum is in [0,1]. Multiplication by
    # the exact representable integer S-2 and addition of one give [1,S-1].
    if normalizer_cap < 2*(program.scale-1) or activation_cap < program.scale-2:
        raise ArithmeticUnresolved('joint AMP whole-domain mass box exceeds the registered range caps')
    return JointAmpRange(raw.theta, domain)


def stored_probability(prediction, target, *, bit_limit):
    closed(prediction, JointAmpPrediction)
    prediction.__post_init__()
    if type(target) is not int or target not in (0, 1):
        raise ContractError('independently observed actual binary target required')
    masses = tuple(single(word) for word in prediction.words[2:4])
    if min(masses) <= 0:
        raise ArithmeticUnresolved('joint AMP stored masses are not positive')
    total = _operation(*masses, multiply=False, bit_limit=bit_limit)
    return _operation(masses[target], F(total.denominator, total.numerator), multiply=True, bit_limit=bit_limit)
