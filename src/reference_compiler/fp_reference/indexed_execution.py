"""The fixed indexed reference realization used by the existing Runtime.

These immutable declarations and phase functions have no independent signer,
ingress, ledger, lineage or installation path. Runtime owns all of those.
The explicit native code remains the one in INDEXED_RELATION_REFERENCE.md.
"""
from dataclasses import dataclass, replace
from fractions import Fraction as F

from .core import ContractError, natural
from . import indexed_count as counts, positive_partition as partition
from . import query_projection as projection
from .indexed_relation import IndexedRelation, DecodeAllowance, ReferenceView, allowance, index, partition_plan
from .learner import SIMPLEX_GRADIENT, ReferenceLearnerState
from .machine import ReferenceMachineModel
from .program import rational
from .semantics import ArithmeticUnresolved, Evaluation, Interval, _guard

COUNTER_CAP = (1 << 62)-1


@dataclass(frozen=True)
class IndexedInitializer:
    n: int

    def __post_init__(self):
        IndexedRelation(self.n)


@dataclass(frozen=True)
class IndexedLearner:
    n: int

    def __post_init__(self):
        IndexedRelation(self.n)

    update_unit = 1
    learning_rate = F(1)
    commit_grid_bits = None
    optimizer_id = SIMPLEX_GRADIENT


@dataclass(frozen=True)
class CategoricalPairDomain:
    n: int

    def __post_init__(self):
        IndexedRelation(self.n)

    def contains(self, values):
        if type(values) is not tuple or len(values) != 2*self.n:
            return False
        if any(type(v) not in (int, F) or v not in (0, 1) for v in values):
            return False
        return sum(values[:self.n]) == sum(values[self.n:]) == 1


@dataclass(frozen=True)
class IndexedTheta:
    n: int
    signed: tuple[int, ...]

    def __post_init__(self):
        IndexedRelation(self.n)
        if (type(self.signed) is not tuple or len(self.signed) != self.n*(self.n-1)//2
                or any(type(v) is not int for v in self.signed)):
            raise ContractError('complete indexed parameter encoding required')


@dataclass(frozen=True)
class IndexedZeroSlots:
    """All K+1 zero slots during construction, before registered Gamma."""
    n: int

    def __post_init__(self):
        IndexedRelation(self.n)


@dataclass(frozen=True)
class IndexedState:
    encoded: counts.CountState
    gradient_forms: tuple[F, ...] = ()

    def __post_init__(self):
        if type(self.encoded) is not counts.CountState:
            raise ContractError('complete immutable indexed count state required')
        IndexedRelation(self.encoded.n)
        if max(self.encoded.cursor, self.encoded.steps, sum(map(abs, self.encoded.counts))) > COUNTER_CAP:
            raise ArithmeticUnresolved('indexed reference counter envelope exhausted')
        if (type(self.gradient_forms) is not tuple
                or len(self.gradient_forms) != (3 if self.encoded.pending is not None else 0)
                or any(type(v) is not F for v in self.gradient_forms)):
            raise ContractError('complete exact pending gradient forms required')

    @property
    def theta(self):
        return IndexedTheta(self.encoded.n, self.encoded.counts)

    @property
    def delayed(self):
        return ()

    @property
    def cursor(self):
        return self.encoded.cursor

    @property
    def optimizer_steps(self):
        return self.encoded.steps

    @property
    def unit_count(self):
        return int(self.encoded.pending is not None)

    def gradient(self, slot):
        schema = IndexedRelation(self.encoded.n)
        index(slot, schema.slot_count, 'indexed gradient slot')
        if not self.unit_count:
            return F(0)
        if slot == 0:
            return self.gradient_forms[0]
        i, j, y = self.encoded.pending
        matching = (schema.world_bit(slot-1, i) ^ schema.world_bit(slot-1, j)) == y
        return self.gradient_forms[1 if matching else 2]

    def materialize(self, *, scalar_cap, budget=DecodeAllowance()):
        schema = IndexedRelation(self.encoded.n)
        allowance(2*schema.slot_count+3, scalar_cap, 'explicit indexed learner output allowance')
        view = ReferenceView.bind(schema, self.encoded, schema.rules(), schema.source_row(0), budget=budget)
        return ReferenceLearnerState(tuple(view.theta(k) for k in range(schema.slot_count)), (),
            tuple(self.gradient(k) for k in range(schema.slot_count)), self.unit_count, self.cursor, self.optimizer_steps)


@dataclass(frozen=True)
class IndexedEvaluation:
    before: counts.CountState
    query: tuple[int, int]
    excesses: tuple[F, F]
    masses: tuple[F, F]
    normalizer: F
    probabilities: tuple[F, F]
    table_work: tuple[tuple[str, int], ...]

    @property
    def delayed(self):
        return ()

    def activation_basis(self):
        # 0 and 1 both occur in the complete source/cache array for n>=2.
        # Only the two final heads have any other possible values.
        return (F(0), F(1))+self.excesses

    def materialize(self, *, scalar_cap):
        schema = IndexedRelation(self.before.n)
        allowance(schema.counts()['nodes']+7, scalar_cap, 'explicit indexed cache output allowance')
        i, j = self.query
        sources = tuple(F(v == self.query[side]) for side in (0, 1) for v in range(schema.n))
        pairs = tuple(F((u, v) == self.query) for u in range(schema.n) for v in range(schema.n))
        indicators = tuple(F((schema.world_bit(k, i) ^ schema.world_bit(k, j)) == y)
                           for k in range(schema.K) for y in (0, 1))
        return Evaluation(sources+pairs+indicators+self.excesses, self.excesses,
                          self.masses, self.normalizer, self.probabilities, ())


@dataclass(frozen=True)
class IndexedPredictionPlan:
    before: counts.CountState
    query: tuple[int, int]
    projection: projection.ProjectionPlan
    bit_limit: int


def _prepare_owned_prediction(program, rules, state, sources, *, budget, bit_limit, order_search=None):
    """Build and bound the owner's selected exact schedule."""
    if type(state) is not IndexedState or state.encoded.n != program.n or state.unit_count:
        raise ContractError('owned committed indexed predecessor required')
    query, _ = program.source_query(rules, sources)
    budget = replace(budget, integer_bits=min(budget.integer_bits, bit_limit))
    plan = projection.prepare(state.encoded, query, budget, order_search=order_search)
    return IndexedPredictionPlan(state.encoded, query, plan, bit_limit)


def _owned_prediction_work(plan):
    """Numeric tariff for the owner's already constructed fixed plan."""
    n = plan.before.n
    shape = dict(plan.projection.shape)
    return (32*(n+1)*(shape['positive_multiplications']+shape['positive_additions'])
            +64*(n*(n-1)//2+8)+64)


def _execute_owned_prediction(plan, n):
    """Fixed exact kernel; Runtime never delegates this call to a planner.

    Its records belong to the owner. The replaceable proposal port sees
    immutable values only and cannot retain any of these argument aliases.
    This arithmetic remains in the explicitly trusted reference kernel.
    """
    if type(plan) is not IndexedPredictionPlan or plan.before.n != n:
        raise ContractError('complete indexed execution plan required')
    before, query = plan.before, plan.query
    parts, stats = projection.execute(before, query, plan.projection)
    total = sum(parts)
    excesses = tuple(F(8*v, total) for v in parts)
    masses = tuple(1+v for v in excesses)
    probabilities = tuple(v/10 for v in masses)
    _guard(*excesses, *masses, *probabilities, F(10), bit_limit=plan.bit_limit)
    return IndexedEvaluation(before, query, excesses, masses, F(10), probabilities, tuple(stats.items()))


@dataclass(frozen=True)
class IndexedRangeBound:
    descriptor: tuple[str, int]
    domain: CategoricalPairDomain
    proof: str = 'indexed-unit-simplex-all-categorical-count-states-range-v1'

    @property
    def masses(self):
        return (Interval(F(1), F(9)),)*2

    @property
    def normalizer(self):
        return Interval(F(10), F(10))

    def sufficient(self, *, normalizer_cap, activation_cap):
        schema = IndexedRelation(self.domain.n)
        if self.descriptor != schema.descriptor or self.proof != type(self).proof:
            raise ContractError('indexed range evidence lost its complete declaration binding')
        return (rational(normalizer_cap, 'normalizer cap', positive=True) >= 10
                and rational(activation_cap, 'activation cap', positive=True) >= 8)


@dataclass(frozen=True)
class IndexedReferenceMachine(ReferenceMachineModel):
    schema: IndexedRelation
    budget: DecodeAllowance
    model_id = 'packed-indexed-reference-payload-v3'
    initializer_id = 'indexed-uniform-unit-simplex-initializer-v1'
    program_type = IndexedRelation

    def __init__(self, n, budget):
        object.__setattr__(self, 'schema', IndexedRelation(n))
        if type(budget) is not DecodeAllowance:
            raise ContractError('registered indexed decoder allowance required')
        object.__setattr__(self, 'budget', budget)

    def require_program(self, program):
        if type(program) is not IndexedRelation or program != self.schema:
            raise ContractError('candidate differs from the registered indexed code family')

    def construction_work(self, program, rules):
        self.require_program(program)
        return 8*self.state_work(program)+16*program.n+32

    def node_count(self, program):
        self.require_program(program)
        return program.counts()['nodes']

    def evaluation_work(self, program, rules):
        self.require_program(program)
        n, d = program.n, program.n*(program.n-1)//2
        # Pay the metadata schedule before planning. Numeric tables receive
        # a separate debit for their actual planned shape, including index
        # visits; the full unused table allowance is not spent each event.
        # One private fixed-plan construction. Keep the former conservative
        # two-pass metadata envelope; the redundant value-transfer fee goes.
        return 64*(n+1)**2*(d+n+1)+128*(d+n+1)

    def observation_work(self, program):
        self.require_program(program)
        return 4*self.state_work(program)+64

    def commit_work(self, program, spec=None):
        self.require_program(program)
        return 4*self.state_work(program)+16

    def state_work(self, program):
        self.require_program(program)
        return program.n*(program.n-1)//2+8

    def initializer_validation_work(self, program, spec):
        return self.state_work(program)+2*program.n

    def zero_payload(self, program, rules):
        self.require_program(program)
        return IndexedZeroSlots(program.n), ()

    def initializer(self, slot_count, pattern):
        if type(pattern) is not IndexedInitializer or pattern.n != self.schema.n or slot_count != self.schema.slot_count:
            raise ContractError('indexed initializer differs from the registered Gamma')
        return IndexedTheta(pattern.n, (0,)*(pattern.n*(pattern.n-1)//2))

    def initial_state(self, program, rules, theta, cursor, *, spec, bit_limit):
        self.require_program(program)
        program.validate(rules)
        if (type(spec) is not IndexedLearner or spec.n != program.n
                or type(theta) is not IndexedTheta or theta.n != program.n or any(theta.signed)):
            raise ContractError('indexed initial state requires its complete registered Gamma and U')
        if program.n+8 > min(self.budget.integer_bits, bit_limit):
            raise ArithmeticUnresolved('indexed initial decoder exceeds the reference integer allowance')
        return IndexedState(counts.CountState(program.n, theta.signed, None, cursor, 0))

    def prepare_prediction(self, program, rules, state, sources, *, bit_limit):
        # Passive convenience. The fixed Runtime class has no plan producer
        # whose answer can differ from the private checker's unique result.
        self.require_program(program)
        return _prepare_owned_prediction(program, rules, state, sources, budget=self.budget, bit_limit=bit_limit)

    def prediction_execution_work(self, plan):
        if type(plan) is not IndexedPredictionPlan or plan.before.n != self.schema.n:
            raise ContractError('complete indexed execution plan required')
        budget = replace(self.budget, integer_bits=min(self.budget.integer_bits, plan.bit_limit))
        from .indexed_values import freeze, same, reference_cells
        expected = projection.prepare(plan.before, plan.query, budget)
        limit = reference_cells(self.schema.n)
        if not same(freeze(plan.projection, cells=limit, bits=plan.bit_limit),
                    freeze(expected, cells=limit, bits=plan.bit_limit)):
            raise ContractError('indexed projection differs from complete input preflight')
        # Each scalar join includes its at-most-n projection/index visits.
        # Guarded powers use at most 2*14 multiplications per active factor
        # under the fixed <=32768-bit integer envelope. GCD/bit complexity
        # and Python heap are outside this declared logical work metric.
        return _owned_prediction_work(plan)

    def execute_prediction(self, plan):
        # Passive convenience for arithmetic audits. Runtime uses the fixed
        # private kernel after accepting a value-only metadata proposal.
        return _execute_owned_prediction(plan, self.schema.n)

    def observe(self, program, state, spec, prediction, target, *, bit_limit):
        self.require_program(program)
        if (type(state) is not IndexedState or type(prediction) is not IndexedEvaluation
                or type(spec) is not IndexedLearner or spec.n != program.n
                or prediction.before != state.encoded or state.unit_count):
            raise ContractError('indexed observation differs from its complete preceding prediction')
        counts.query(program.n, *prediction.query, target)
        mass = prediction.masses[target]
        gradients = (1/mass-F(1, 5), F(4, 5)-8/mass, F(4, 5))
        _guard(*gradients, bit_limit=bit_limit)
        # The target is supplied by Runtime's actual ObservationRecord. No
        # pending state or numerical helper reports which event occurred.
        return IndexedState(counts.observe(state.encoded, *prediction.query, target), gradients)

    def commit(self, state, spec, *, bit_limit):
        if (type(state) is not IndexedState or type(spec) is not IndexedLearner
                or spec.n != state.encoded.n or spec.n != self.schema.n):
            raise ContractError('indexed commit requires the complete fixed learner state')
        return IndexedState(counts.commit(state.encoded))

    def attach(self, state, cursor, spec):
        if (type(state) is not IndexedState or type(spec) is not IndexedLearner
                or spec.n != state.encoded.n or spec.n != self.schema.n):
            raise ContractError('indexed profile attachment differs from its learner')
        return IndexedState(counts.attach(state.encoded, cursor))

    @staticmethod
    def activation_values(prediction):
        if type(prediction) is not IndexedEvaluation:
            raise ContractError('complete indexed prediction required')
        return prediction.activation_basis()

    def range_bound(self, program, rules, theta, domain):
        self.require_program(program)
        program.validate(rules)
        if (type(theta) is not IndexedTheta or theta.n != program.n
                or type(domain) is not CategoricalPairDomain or domain != CategoricalPairDomain(program.n)):
            raise ContractError('indexed range requires its complete parameter and domain encoding')
        return IndexedRangeBound(program.descriptor, domain)
