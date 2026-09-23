"""Bounded derivation and exact coordinates for a numerical learner lowering.

Only Runtime may bind this derivation to its actual program, Gamma, complete
source domain and unit simplex U. These helpers have no execution authority.
Non-affine heads, missing source domains, incompatible likelihood radices,
arithmetic exhaustion and counter overflow remain UNRESOLVED.
"""
from dataclasses import dataclass, replace
from fractions import Fraction as F
from math import gcd

from .core import ContractError, natural, stable_hash
from .learner import SIMPLEX_GRADIENT, LearnerSpec
from .program import Product, Program, SemanticRules, Source, State, Sum, rational
from .semantics import ArithmeticUnresolved, _guard, _operation
from . import coprime_coordinates


ENCODING_ID = 'finite-affine-commensurate-likelihood-coordinates-v1'
BACKEND_ID = 'eager-cuda-half-forward-single-gradient-count-decode-v1'
RATIONAL_ENCODING_ID = 'finite-affine-coprime-likelihood-coordinates-v1'
RATIONAL_BACKEND_ID = 'eager-cuda-half-forward-single-gradient-owned-integer-rational-decode-v1'
RATIONAL_WORK_ID = 'prepaid-coprime-factorization-owned-integer-decode-and-CUDA-output-v1'


@dataclass(frozen=True)
class LikelihoodEncodingContract:
    radix: F = F(9)
    counter_bits: int = 64

    def __post_init__(self):
        object.__setattr__(self, 'radix', rational(self.radix, 'likelihood encoding radix', positive=True))
        natural(self.counter_bits, 'likelihood signed counter precision', positive=True)
        if self.radix <= 1 or not 2 <= self.counter_bits <= 64:
            raise ContractError('the registered likelihood representation needs radix>1 and 2..64 counter bits')


@dataclass(frozen=True)
class RationalLikelihoodContract:
    """Finite arithmetic allowances, not an extra native architecture action."""
    counter_bits: int = 64
    basis_cells: int = 16
    factor_work: int = 1_000_000
    decode_work: int = 1_000_000

    def __post_init__(self):
        for key in ('counter_bits', 'basis_cells', 'factor_work', 'decode_work'):
            natural(getattr(self, key), 'rational likelihood '+key, positive=True)
        if not 2 <= self.counter_bits <= 64:
            raise ContractError('rational likelihood counters need 2..64 signed bits')


CONTRACTS = (LikelihoodEncodingContract, RationalLikelihoodContract)


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


def preparation_work(program, rules, spec, source_domain, bit_limit, contract=None):
    """Conservative scalar/structural allowance, paid before model derivation."""
    k = len(spec.simplex_slots)
    q = 1 if source_domain is None else len(source_domain)
    labels = len(program.heads)
    nodes = len(program.nodes)
    edges = sum(len(node.terms) if type(node) is Sum else 2 if type(node) is Product else 1
                for node in program.nodes)
    events = q*labels
    charge = (1024+q*(nodes+edges+labels+len(rules.sources)+1)*64*(k+1)
            +32*(events+1)*(k+1)*bit_limit+64*(events+k+1)*(k+1)**3)
    if type(contract) is RationalLikelihoodContract:
        contract.__post_init__()
        width = k*contract.basis_cells
        charge += contract.factor_work+64*(width+1)*(events+width+1)*(min(width, events)+1)
    return charge


def preparation_workspace(program, rules, spec, source_domain, bit_limit, contract=None):
    """Packed-reference scratch envelope; actual CPython memory needs the host contract."""
    k = len(spec.simplex_slots)
    q = 1 if source_domain is None else len(source_domain)
    events = q*len(program.heads)
    # All affine rows, likelihood/valuation tables and elimination workspace.
    cells = (len(program.nodes)+4*events+8*k+len(rules.sources)+1)*(k+1)
    if type(contract) is RationalLikelihoodContract:
        contract.__post_init__()
        width = k*contract.basis_cells
        cells += 4*(width+1)*(events+width+1)+8*contract.basis_cells
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
    # Absence means an identically zero formal coefficient at this registered
    # source point, for every selected-parameter value. It is not a threshold
    # on the current theta. Other source points are analyzed independently.
    selected = {slot: (F(0), {i: F(1)}) for i, slot in enumerate(slots)}
    zero = (F(0), {})
    source = dict(zip((s.source_id for s in rules.sources), point))

    def is_zero(value):
        return value is not None and not value[0] and not value[1]

    def multiply(left, right):
        arithmetic.take()
        if is_zero(left) or is_zero(right):
            return zero
        if left is None or right is None:
            return None
        if left[1] and right[1]:
            return None
        if left[1]:
            left, right = right, left
        return (arithmetic.mul(left[0], right[0]),
                {i: arithmetic.mul(left[0], value) for i, value in right[1].items()})

    values = []
    for node in program.nodes:
        arithmetic.take()
        if type(node) is Source:
            value = (source[node.source_id], {})
        elif type(node) is State:
            raise ArithmeticUnresolved('likelihood encoding has no delayed-state simulation')
        elif type(node) is Product:
            value = multiply(values[node.left], values[node.right])
        else:
            assert type(node) is Sum
            # This fresh dictionary belongs only to this SUM. Parent maps and
            # the shared zero/variable forms are read-only throughout analysis.
            value = (F(0), {})
            for term in node.terms:
                parameter = selected[term.slot] if term.slot in selected else (theta[term.slot], {})
                term_value = multiply(parameter, values[term.parent])
                if value is None or term_value is None:
                    value = None
                else:
                    coefficients = value[1]
                    for i, coefficient in term_value[1].items():
                        coefficients[i] = arithmetic.add(coefficients.get(i, F(0)), coefficient)
                    value = (arithmetic.add(value[0], term_value[0]), coefficients)
        values.append(value)
    heads = tuple(values[i] for i in program.heads)
    if any(row is None for row in heads):
        raise ArithmeticUnresolved('this bounded analyzer cannot prove affine selected heads')
    return tuple((arithmetic.add(base, row[0]),)+tuple(row[1].get(i, F(0)) for i in range(k))
                 for base, row in zip(rules.base, heads))


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
        rational_model = type(self) is RationalLikelihoodModel
        expected_contract = RationalLikelihoodContract if rational_model else LikelihoodEncodingContract
        if type(self) not in MODELS or type(self.contract) is not expected_contract:
            raise ContractError('immutable likelihood numerical representation required')
        self.contract.__post_init__()
        if rational_model:
            if (type(self.factor_bases) is not tuple or len(self.factor_bases) > self.contract.basis_cells
                    or any(type(v) is not int or v < 2 for v in self.factor_bases)
                    or tuple(sorted(set(self.factor_bases))) != self.factor_bases
                    or any(gcd(a, b) != 1 for i, a in enumerate(self.factor_bases) for b in self.factor_bases[i+1:])):
                raise ContractError('complete immutable coprime-basis descriptor required')
        if type(self.semantics) is not SemanticRules or self.semantics.states:
            raise ContractError('complete static native semantics required for likelihood encoding')
        require_learner(self.learner)
        natural(self.preparation_operations, 'actual likelihood preparation work')
        for label in ('source_domain', 'initial_theta',
                      'prior_exponents', 'reference_increment', 'event_increments', 'reconstruction'):
            if type(getattr(self, label)) is not tuple:
                raise ContractError('likelihood descriptor coordinates must be immutable tuples')
        k, rho = len(self.simplex_slots), len(self.event_increments[0]) if self.event_increments else 0
        block = len(self.factor_bases) if rational_model else 1
        width = k*block
        if (not k or type(self.program_id) is not str or not self.source_domain
                or any(type(v) is not str for v in self.source_ids)
                or len(set(self.source_ids)) != len(self.source_ids)
                or any(type(row) is not tuple or len(row) != len(self.source_ids)
                       or any(type(v) is not F or v < 0 for v in row) for row in self.source_domain)
                or any(type(v) is not F or v < 0 for v in self.initial_theta)
                or any(type(i) is not int or i < 0 or i >= len(self.initial_theta) for i in self.simplex_slots)
                or tuple(sorted(set(self.simplex_slots))) != self.simplex_slots
                or len(self.prior_exponents) != width or len(self.reference_increment) != width
                or len(self.reconstruction) != width
                or len(self.event_increments) != len(self.source_domain)*self.labels
                or any(type(row) is not tuple or len(row) != rho for row in self.event_increments+self.reconstruction)
                or any(type(v) is not int for v in self.prior_exponents+self.reference_increment
                       +tuple(v for row in self.event_increments for v in row))
                or any(type(v) is not F for row in self.reconstruction for v in row)):
            raise ContractError('complete immutable likelihood factorization required')
        if (any(self.prior_exponents[:block]) or any(self.reference_increment[:block])
                or any(v for row in self.reconstruction[:block] for v in row) or any(self.event_increments[0])):
            raise ContractError('likelihood factorization lost its reference world/event')

    @property
    def encoding_id(self):
        return RATIONAL_ENCODING_ID if type(self) is RationalLikelihoodModel else ENCODING_ID

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


@dataclass(frozen=True)
class RationalLikelihoodModel(LikelihoodModel):
    contract: RationalLikelihoodContract
    factor_bases: tuple[int, ...]


MODELS = (LikelihoodModel, RationalLikelihoodModel)


def prepare_model(program, rules, theta, spec, source_domain, contract, *, bit_limit, work_limit):
    if (type(program) is not Program or type(rules) is not SemanticRules
            or type(contract) not in CONTRACTS):
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
    rational_model = type(contract) is RationalLikelihoodContract
    _guard(*theta, *((contract.radix,) if not rational_model else ()), bit_limit=bit_limit)
    prior = tuple(theta[i] for i in spec.simplex_slots)
    if min(prior) <= 0 or arithmetic.sum(prior) != 1:
        raise ArithmeticUnresolved('likelihood representation requires the actual strictly positive simplex prior')
    domain = tuple(dict.fromkeys(source_domain))
    if not domain or any(type(row) is not tuple or len(row) != len(rules.sources)
                         or any(type(v) is not F or v < 0 or v > s.upper for v, s in zip(row, rules.sources))
                         for row in domain):
        raise ContractError('complete bounded immutable likelihood source-domain rows required')
    if rational_model:
        prior_exponents = tuple(arithmetic.div(v, prior[0]) for v in prior)
    else:
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
            if rational_model:
                increments.append(tuple(arithmetic.div(mass, masses[0]) for mass in masses))
            else:
                increments.append(tuple(_radix_power(arithmetic.div(mass, masses[0]), contract.radix, arithmetic)
                                        for mass in masses))
    if rational_model:
        remaining = min(contract.factor_work, work_limit-arithmetic.operations)
        if remaining <= 0:
            raise ArithmeticUnresolved('rational likelihood derivation has no remaining factor work')
        ratios = prior_exponents+tuple(v for row in increments for v in row)
        factors = coprime_coordinates.factor(ratios, bit_limit=bit_limit,
            work_limit=remaining, cell_limit=contract.basis_cells)
        arithmetic.take(factors.operations)
        k = len(prior)
        prior_exponents = tuple(v for row in factors.exponents[:k] for v in row)
        increments = tuple(tuple(v for row in factors.exponents[i:i+k] for v in row)
                           for i in range(k, len(factors.exponents), k))
    reference = increments[0]
    differences = tuple(tuple(a[k]-reference[k] for a in increments) for k in range(len(prior_exponents)))
    basis, reconstruction = _row_basis(differences, arithmetic)
    model_type = RationalLikelihoodModel if rational_model else LikelihoodModel
    model = model_type(program.program_id, rules, domain,
        theta, spec, contract, prior_exponents, reference,
        tuple(tuple(row[i] for row in basis) for i in range(len(increments))),
        reconstruction, arithmetic.operations, **({'factor_bases': factors.bases} if rational_model else {}))
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
        if type(self.model) not in MODELS:
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
        return (self.model.encoding_id, stable_hash(self.model), self.coordinates, self.pending_event)

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
    if type(model) is RationalLikelihoodModel:
        k = max(k, len(model.prior_exponents))
    return (1024+64*(k+len(model.event_increments)+1)*(rho+1)
            +64*(q+1)*(len(model.source_ids)+1)+64*len(model.initial_theta)
            +(64*(len(model.factor_bases)+1)**2 if type(model) is RationalLikelihoodModel else 0))


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
    if type(state.model) is not LikelihoodModel:
        raise ContractError('single-radix power schedule cannot decode a rational coprime model')
    values = exponents(state, steps, bit_limit=bit_limit)
    maximum = max(values)
    differences = tuple(maximum-value for value in values)
    return differences, max(differences).bit_length()


def decode_workspace(model, bit_limit):
    """Packed scratch includes all exponent tables, integer weights and ingress.

    A distinct enclosing host-job cap still covers actual Python heap costs.
    """
    if type(model) is not RationalLikelihoodModel:
        return 0
    natural(bit_limit, 'rational likelihood workspace integer bits', positive=True)
    k, b = len(model.simplex_slots), len(model.factor_bases)
    return 4096+(4*k*b+8*k+4*b+8)*(128+2*((bit_limit+7)//8))


def decode_work(model, bit_limit):
    if type(model) is not RationalLikelihoodModel:
        return 0
    return model.contract.decode_work+8*decode_workspace(model, bit_limit)


def require_workspace(workspace, size):
    if (type(workspace) is not memoryview or workspace.readonly or not workspace.c_contiguous
            or workspace.format != 'B' or workspace.ndim != 1 or len(workspace) != size):
        raise ContractError('rational likelihood arithmetic needs its exact paid writable scratch extent')


def joint_inputs(state, steps, *, bit_limit, workspace):
    """Materialize only from physical counters, in the Runtime-funded extent."""
    model = state.model
    if type(model) is not RationalLikelihoodModel:
        raise ContractError('joint integer readout needs its distinct rational likelihood model')
    require_workspace(workspace, decode_workspace(model, bit_limit))
    values = exponents(state, steps, bit_limit=bit_limit)
    k, width = len(model.simplex_slots), len(model.factor_bases)
    rows = tuple(values[i*width:(i+1)*width] for i in range(k))
    plan = coprime_coordinates.integer_weights(model.factor_bases, rows, bit_limit=bit_limit,
        work_limit=model.contract.decode_work, cell_limit=k)
    stride = (bit_limit+7)//8
    for i, weight in enumerate(plan.weights):
        workspace[i*stride:(i+1)*stride] = weight.to_bytes(stride, 'little')
    # Actual weight bytes occupy the owned extent, not an uncharged helper
    # result. Python arithmetic temporaries also remain inside the host job.
    loaded = tuple(int.from_bytes(workspace[i*stride:(i+1)*stride], 'little') for i in range(k))
    if loaded != plan.weights:
        raise ContractError('owned integer likelihood scratch changed before ingress')
    return tuple(F(value, 1 << plan.binary_shift) for value in loaded)
