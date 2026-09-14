"""Bounded derivation and exact coordinates for a numerical learner lowering.

Only Runtime may bind this derivation to its actual program, Gamma, complete
source domain and unit simplex U. These helpers have no execution authority.
Non-affine heads, missing source domains, incompatible likelihood radices,
arithmetic exhaustion and counter overflow remain UNRESOLVED.
"""
from dataclasses import dataclass, replace
from fractions import Fraction as F

from .core import ContractError, natural, stable_hash
from .learner import SIMPLEX_GRADIENT, LearnerSpec
from .program import Product, Program, SemanticRules, Source, State, Sum, rational
from .semantics import ArithmeticUnresolved, _guard, _operation


ENCODING_ID = 'finite-affine-commensurate-likelihood-coordinates-v1'
BACKEND_ID = 'eager-cuda-half-forward-single-gradient-count-decode-v1'


@dataclass(frozen=True)
class LikelihoodEncodingContract:
    radix: F = F(9)
    counter_bits: int = 64

    def __post_init__(self):
        object.__setattr__(self, 'radix', rational(self.radix, 'likelihood encoding radix', positive=True))
        natural(self.counter_bits, 'likelihood signed counter precision', positive=True)
        if self.radix <= 1 or not 2 <= self.counter_bits <= 64:
            raise ContractError('the registered likelihood representation needs radix>1 and 2..64 counter bits')


def require_learner(spec):
    if type(spec) is not LearnerSpec:
        raise ContractError('actual registered learner required for likelihood encoding')
    spec.__post_init__()
    if (spec.optimizer_id != SIMPLEX_GRADIENT or spec.learning_rate != 1
            or spec.update_unit != 1 or spec.commit_grid_bits is not None):
        raise ArithmeticUnresolved('likelihood encoding has no simulation for this actual learner U')


class _Arithmetic:
    def __init__(self, bit_limit, work_limit):
        natural(bit_limit, 'likelihood exact arithmetic precision', positive=True)
        natural(work_limit, 'likelihood derivation work allowance', positive=True)
        self.bit_limit, self.work_limit, self.operations = bit_limit, work_limit, 0

    def take(self, count=1):
        if self.operations+count > self.work_limit:
            raise ArithmeticUnresolved('likelihood derivation exhausted its prepaid work')
        self.operations += count

    def add(self, left, right):
        self.take()
        return _operation(left, right, multiply=False, bit_limit=self.bit_limit)

    def mul(self, left, right):
        self.take()
        return _operation(left, right, multiply=True, bit_limit=self.bit_limit)

    def div(self, left, right):
        self.take()
        _guard(left, right, bit_limit=self.bit_limit)
        if not right:
            raise ArithmeticUnresolved('zero divisor in likelihood encoding derivation')
        return _operation(left, 1/F(right), multiply=True, bit_limit=self.bit_limit)

    def sum(self, values):
        result = F(0)
        for value in values:
            result = self.add(result, value)
        return result


def preparation_work(program, rules, spec, source_domain, bit_limit):
    """Conservative scalar/structural allowance, paid before model derivation."""
    k = len(spec.simplex_slots)
    q = 1 if source_domain is None else len(source_domain)
    labels = len(program.heads)
    nodes = len(program.nodes)
    edges = sum(len(node.terms) if type(node) is Sum else 2 if type(node) is Product else 1
                for node in program.nodes)
    events = q*labels
    return (1024+q*(nodes+edges+labels+len(rules.sources)+1)*64*(k+1)
            +32*(events+1)*(k+1)*bit_limit+64*(events+k+1)*(k+1)**3)


def preparation_workspace(program, rules, spec, source_domain, bit_limit):
    """Packed-reference scratch envelope; actual CPython memory needs the host contract."""
    k = len(spec.simplex_slots)
    q = 1 if source_domain is None else len(source_domain)
    events = q*len(program.heads)
    # All affine rows, likelihood/valuation tables and elimination workspace.
    cells = (len(program.nodes)+4*events+8*k+len(rules.sources)+1)*(k+1)
    return 4096+cells*(128+2*((bit_limit+7)//8))


def _radix_power(value, radix, arithmetic):
    _guard(value, radix, bit_limit=arithmetic.bit_limit)
    if value <= 0:
        raise ArithmeticUnresolved('likelihood and prior ratios must stay strictly positive')
    if value == 1:
        return 0
    sign = 1 if value > 1 else -1
    value = value if sign == 1 else arithmetic.div(F(1), value)
    num, den = value.numerator, value.denominator
    rn, rd = radix.numerator, radix.denominator
    power = 0
    # rn>=2, so every successful iteration reduces numerator bit length.
    while num != 1 or den != 1:
        arithmetic.take(8)
        if num % rn or den % rd:
            raise ArithmeticUnresolved('actual likelihood/prior ratio is not an integer power of the registered radix')
        num //= rn
        den //= rd
        power += 1
    return sign*power


def _affine_heads(program, rules, theta, slots, point, arithmetic):
    """Conservative formal affine analysis, retaining nonlinear interior nodes.

    None means unsupported polynomial degree, not deletion of a native node.
    Multiplication by an actual fixed zero can annul that dependence at the
    selected slice; its ambient fixed-slot derivative remains native work.
    """
    k = len(slots)
    selected = {slot: i+1 for i, slot in enumerate(slots)}
    zero = (F(0),)*(k+1)
    source = dict(zip((s.source_id for s in rules.sources), point))

    def multiply(left, right):
        arithmetic.take()
        if left == zero or right == zero:
            return zero
        if left is None or right is None:
            return None
        if any(left[1:]) and any(right[1:]):
            return None
        if any(left[1:]):
            left, right = right, left
        return tuple(arithmetic.mul(left[0], value) for value in right)

    values = []
    for node in program.nodes:
        arithmetic.take()
        if type(node) is Source:
            value = (source[node.source_id],)+(F(0),)*k
        elif type(node) is State:
            raise ArithmeticUnresolved('likelihood encoding has no delayed-state simulation')
        elif type(node) is Product:
            value = multiply(values[node.left], values[node.right])
        else:
            assert type(node) is Sum
            value = zero
            for term in node.terms:
                if term.slot in selected:
                    parameter = tuple(F(i == selected[term.slot]) for i in range(k+1))
                else:
                    parameter = (theta[term.slot],)+(F(0),)*k
                term_value = multiply(parameter, values[term.parent])
                value = (None if value is None or term_value is None else
                         tuple(arithmetic.add(a, b) for a, b in zip(value, term_value)))
        values.append(value)
    heads = tuple(values[i] for i in program.heads)
    if any(row is None for row in heads):
        raise ArithmeticUnresolved('this bounded analyzer cannot prove affine selected heads')
    return tuple((arithmetic.add(base, row[0]),)+row[1:] for base, row in zip(rules.base, heads))


def _row_basis(rows, arithmetic):
    """Independent original rows and a guarded reconstruction of every row."""
    width = len(rows)
    echelon, selected, combinations = [], [], []
    for index, original in enumerate(rows):
        residual = list(map(F, original))
        coefficients = [F(0)]*width
        for pivot, basis, representation in echelon:
            factor = residual[pivot]
            residual = [arithmetic.add(v, -arithmetic.mul(factor, b)) for v, b in zip(residual, basis)]
            coefficients = [arithmetic.add(v, arithmetic.mul(factor, b)) for v, b in zip(coefficients, representation)]
        pivot = next((i for i, value in enumerate(residual) if value), None)
        if pivot is not None:
            ordinal = len(selected)
            selected.append(index)
            divisor = residual[pivot]
            basis = tuple(arithmetic.div(v, divisor) for v in residual)
            representation = tuple(arithmetic.div(arithmetic.add(F(i == ordinal), -v), divisor)
                                   for i, v in enumerate(coefficients))
            echelon.append((pivot, basis, representation))
            coefficients = [F(i == ordinal) for i in range(width)]
        combinations.append(tuple(coefficients))
    rho = len(selected)
    basis = tuple(rows[i] for i in selected)
    combinations = tuple(row[:rho] for row in combinations)
    # A separate reconstruction pass makes the bounded derivation checkable.
    for original, coefficients in zip(rows, combinations):
        for col, value in enumerate(original):
            if arithmetic.sum(arithmetic.mul(c, b[col]) for c, b in zip(coefficients, basis)) != value:
                raise ContractError('likelihood row factorization did not reconstruct its actual input')
    return basis, combinations


@dataclass(frozen=True)
class LikelihoodModel:
    program_id: str
    semantics: SemanticRules
    source_domain: tuple[tuple[F, ...], ...]
    initial_theta: tuple[F, ...]
    learner: LearnerSpec
    contract: LikelihoodEncodingContract
    prior_exponents: tuple[int, ...]
    reference_increment: tuple[int, ...]
    event_increments: tuple[tuple[int, ...], ...]
    reconstruction: tuple[tuple[F, ...], ...]
    preparation_operations: int

    def __post_init__(self):
        if type(self.contract) is not LikelihoodEncodingContract:
            raise ContractError('immutable likelihood numerical representation required')
        self.contract.__post_init__()
        if type(self.semantics) is not SemanticRules or self.semantics.states:
            raise ContractError('complete static native semantics required for likelihood encoding')
        require_learner(self.learner)
        natural(self.preparation_operations, 'actual likelihood preparation work')
        for label in ('source_domain', 'initial_theta',
                      'prior_exponents', 'reference_increment', 'event_increments', 'reconstruction'):
            if type(getattr(self, label)) is not tuple:
                raise ContractError('likelihood descriptor coordinates must be immutable tuples')
        k, rho = len(self.simplex_slots), len(self.event_increments[0]) if self.event_increments else 0
        if (not k or type(self.program_id) is not str or not self.source_domain
                or any(type(v) is not str for v in self.source_ids)
                or len(set(self.source_ids)) != len(self.source_ids)
                or any(type(row) is not tuple or len(row) != len(self.source_ids)
                       or any(type(v) is not F or v < 0 for v in row) for row in self.source_domain)
                or any(type(v) is not F or v < 0 for v in self.initial_theta)
                or any(type(i) is not int or i < 0 or i >= len(self.initial_theta) for i in self.simplex_slots)
                or tuple(sorted(set(self.simplex_slots))) != self.simplex_slots
                or len(self.prior_exponents) != k or len(self.reference_increment) != k
                or len(self.reconstruction) != k
                or len(self.event_increments) != len(self.source_domain)*self.labels
                or any(type(row) is not tuple or len(row) != rho for row in self.event_increments+self.reconstruction)
                or any(type(v) is not int for v in self.prior_exponents+self.reference_increment
                       +tuple(v for row in self.event_increments for v in row))
                or any(type(v) is not F for row in self.reconstruction for v in row)):
            raise ContractError('complete immutable likelihood factorization required')
        if (self.prior_exponents[0] or self.reference_increment[0]
                or any(self.reconstruction[0]) or any(self.event_increments[0])):
            raise ContractError('likelihood factorization lost its reference world/event')

    @property
    def rank(self):
        return len(self.event_increments[0])

    @property
    def simplex_slots(self):
        return self.learner.simplex_slots

    @property
    def labels(self):
        return len(self.semantics.base)

    @property
    def source_ids(self):
        return tuple(s.source_id for s in self.semantics.sources)

    def query_index(self, sources):
        if set(sources) != set(self.source_ids):
            raise ContractError('likelihood query lost its complete source interface')
        point = tuple(sources[key] for key in self.source_ids)
        try:
            return self.source_domain.index(point)
        except ValueError as exc:
            raise ArithmeticUnresolved('actual query lies outside the registered likelihood source domain') from exc


def prepare_model(program, rules, theta, spec, source_domain, contract, *, bit_limit, work_limit):
    if (type(program) is not Program or type(rules) is not SemanticRules
            or type(contract) is not LikelihoodEncodingContract):
        raise ContractError('actual immutable program, semantics and numerical encoding required')
    contract.__post_init__()
    require_learner(spec)
    program.validate(rules)
    if rules.states:
        raise ArithmeticUnresolved('likelihood encoding has no delayed-state simulation')
    if source_domain is None:
        if rules.sources:
            raise ArithmeticUnresolved('likelihood encoding requires the complete finite registered source domain')
        source_domain = ((),)
    if (type(theta) is not tuple or len(theta) != program.slot_count
            or any(type(v) is not F or v < 0 for v in theta)
            or max(spec.simplex_slots) >= len(theta)):
        raise ArithmeticUnresolved('actual initializer does not contain the complete simplex block')
    arithmetic = _Arithmetic(bit_limit, work_limit)
    _guard(*theta, contract.radix, bit_limit=bit_limit)
    prior = tuple(theta[i] for i in spec.simplex_slots)
    if min(prior) <= 0 or arithmetic.sum(prior) != 1:
        raise ArithmeticUnresolved('likelihood representation requires the actual strictly positive simplex prior')
    domain = tuple(dict.fromkeys(source_domain))
    if not domain or any(type(row) is not tuple or len(row) != len(rules.sources)
                         or any(type(v) is not F or v < 0 or v > s.upper for v, s in zip(row, rules.sources))
                         for row in domain):
        raise ContractError('complete bounded immutable likelihood source-domain rows required')
    prior_exponents = tuple(_radix_power(arithmetic.div(v, prior[0]), contract.radix, arithmetic) for v in prior)
    increments = []
    for point in domain:
        _guard(*point, bit_limit=bit_limit)
        heads = _affine_heads(program, rules, theta, spec.simplex_slots, point, arithmetic)
        columns = tuple(arithmetic.sum(row[k+1] for row in heads) for k in range(len(prior)))
        if len(set(columns)) != 1:
            raise ArithmeticUnresolved('actual affine expert normalizers differ on a legal source row')
        for row in heads:
            masses = tuple(arithmetic.add(row[0], coefficient) for coefficient in row[1:])
            increments.append(tuple(_radix_power(arithmetic.div(mass, masses[0]), contract.radix, arithmetic)
                                    for mass in masses))
    reference = increments[0]
    differences = tuple(tuple(a[k]-reference[k] for a in increments) for k in range(len(prior)))
    basis, reconstruction = _row_basis(differences, arithmetic)
    model = LikelihoodModel(program.program_id, rules, domain,
        theta, spec, contract, prior_exponents, reference,
        tuple(tuple(row[i] for row in basis) for i in range(len(increments))),
        reconstruction, arithmetic.operations)
    # Decode the actual prior before any physical initialization is authorized.
    exponents(EncodedLikelihoodState(model, (0,)*model.rank, None), 0, bit_limit=bit_limit)
    return model


def _counter(value, bits):
    if type(value) is not int:
        raise ContractError('exact integer likelihood coordinate required')
    if abs(value) >= 1 << (bits-1):
        raise ArithmeticUnresolved('registered likelihood counter precision exhausted')


@dataclass(frozen=True)
class EncodedLikelihoodState:
    model: LikelihoodModel
    coordinates: tuple[int, ...]
    pending_event: int | None

    def __post_init__(self):
        if type(self.model) is not LikelihoodModel:
            raise ContractError('complete actual likelihood model binding required')
        self.model.__post_init__()
        if type(self.coordinates) is not tuple or len(self.coordinates) != self.model.rank:
            raise ContractError('complete likelihood coordinate vector required')
        for value in self.coordinates:
            _counter(value, self.model.contract.counter_bits)
        if self.pending_event is not None:
            natural(self.pending_event, 'actual uncommitted likelihood event')
            if self.pending_event >= len(self.model.event_increments):
                raise ContractError('uncommitted likelihood event outside the actual interface')

    def observe(self, query, target):
        if self.pending_event is not None:
            raise ContractError('likelihood observation requires an empty unit')
        natural(query, 'actual preceding likelihood query')
        natural(target, 'actual observed likelihood label')
        if query >= len(self.model.source_domain) or target >= self.model.labels:
            raise ContractError('actual likelihood observation is outside its declared interface')
        return replace(self, pending_event=query*self.model.labels+target)

    def commit(self):
        if self.pending_event is None:
            raise ContractError('likelihood commit requires its actual uncommitted event')
        values = tuple(a+b for a, b in zip(self.coordinates, self.model.event_increments[self.pending_event]))
        return replace(self, coordinates=values, pending_event=None)

    def raw(self):
        # This independent primitive digest binds the paid descriptor. Keeping
        # the descriptor object itself here would alias old phase records and
        # fail to expose a later mutation of that private object. The complete
        # descriptor is retained once in its initialization phase.
        return (ENCODING_ID, stable_hash(self.model), self.coordinates, self.pending_event)

    def validate_phase(self, slots, unit_count, steps, delayed):
        self.__post_init__()
        if (slots != len(self.model.initial_theta) or delayed
                or unit_count != int(self.pending_event is not None)):
            raise ContractError('likelihood coordinates do not represent the complete current learner phase')
        natural(steps, 'actual likelihood optimizer steps')
        _counter(steps, self.model.contract.counter_bits)


def phase_work(model):
    # Validation, domain matching, coordinate update and guarded reconstruction;
    # the CUDA primitive/output work remains paid by the enclosing prefix.
    k, rho, q = len(model.simplex_slots), model.rank, len(model.source_domain)
    return (1024+64*(k+len(model.event_increments)+1)*(rho+1)
            +64*(q+1)*(len(model.source_ids)+1)+64*len(model.initial_theta))


def exponents(state, steps, *, bit_limit):
    if type(state) is not EncodedLikelihoodState:
        raise ContractError('complete likelihood state required for decoding')
    state.__post_init__()
    natural(steps, 'actual committed likelihood optimizer steps')
    _counter(steps, state.model.contract.counter_bits)
    arithmetic = _Arithmetic(bit_limit, phase_work(state.model))
    result = []
    for prior, reference, coefficients in zip(state.model.prior_exponents,
                                              state.model.reference_increment, state.model.reconstruction):
        value = arithmetic.add(F(prior), arithmetic.mul(F(steps), F(reference)))
        value = arithmetic.add(value, arithmetic.sum(arithmetic.mul(c, F(q))
                                                    for c, q in zip(coefficients, state.coordinates)))
        if value.denominator != 1:
            raise ContractError('likelihood coordinates no longer decode to integer powers')
        _counter(value.numerator, state.model.contract.counter_bits)
        result.append(value.numerator)
    return tuple(result)


def power_schedule(state, steps, *, bit_limit):
    values = exponents(state, steps, bit_limit=bit_limit)
    maximum = max(values)
    differences = tuple(maximum-value for value in values)
    return differences, max(differences).bit_length()
