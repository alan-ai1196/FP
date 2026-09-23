"""Exact joint-noise realization inside the existing Reference Runtime.

Immutable declarations and fixed numerical kernels have no independent
ledger, ingress, signer, persistence or installation endpoint.
"""
from dataclasses import dataclass, fields, replace
from fractions import Fraction as F
from itertools import combinations

from .core import ContractError
from .indexed_execution import CategoricalPairDomain
from .indexed_relation import allowance, index
from .joint_relation import JointRelation, JointCountState, require_state, initialize, observe, commit, attach
from . import joint_partition_decoder as decoder
from .learner import SIMPLEX_GRADIENT, ReferenceLearnerState
from .machine import ReferenceMachineModel
from .semantics import ArithmeticUnresolved, Evaluation, Interval, _guard

MODEL_ID = 'packed-indexed-joint-noise-integer-partition-reference-v1'
ARITHMETIC_ID = 'indexed-joint-noise-count-excess-partition-reference-v1'


def closed(value, kind):
    if type(value) is not kind or set(vars(value)) != {f.name for f in fields(kind)}:
        raise ContractError('complete immutable '+kind.__name__+' required')


@dataclass(frozen=True)
class JointInitializer:
    schema: JointRelation

    def __post_init__(self):
        closed(self, JointInitializer)
        closed(self.schema, JointRelation)
        self.schema.__post_init__()

    @property
    def n(self):
        return self.schema.n


@dataclass(frozen=True)
class JointLearner:
    schema: JointRelation

    update_unit = 1
    learning_rate = F(1)
    commit_grid_bits = None
    optimizer_id = SIMPLEX_GRADIENT

    def __post_init__(self):
        closed(self, JointLearner)
        closed(self.schema, JointRelation)
        self.schema.__post_init__()


@dataclass(frozen=True)
class JointTheta:
    schema: JointRelation
    counts: tuple[int, ...]
    diagonal: int
    steps: int

    def __post_init__(self):
        closed(self, JointTheta)
        JointCountState(self.schema, self.counts, self.diagonal, 0, self.steps)


@dataclass(frozen=True)
class JointZeroSlots:
    schema: JointRelation

    def __post_init__(self):
        closed(self, JointZeroSlots)
        closed(self.schema, JointRelation)
        self.schema.__post_init__()


def _parameter(before, normalization, slot, *, bit_limit):
    model = before.model
    index(slot, model.slot_count, 'joint native parameter slot')
    if slot == 0:
        return F(1)
    rate, world = model.hypothesis(slot-1)
    score = before.diagonal+sum(d*(1-2*(model.world_bit(world, i)^model.world_bit(world, j)))
        for (i, j), d in zip(combinations(range(model.n), 2), before.counts))
    matches = (before.steps+score)//2
    if not 0 <= matches <= before.steps or (before.steps+score) % 2:
        raise ContractError('joint parameter point lost its reachable count lattice')
    a = int(model.scale*model.rates[rate])
    weight = int(model.prior[rate]*model.prior_scale)*(model.scale-a)**matches*a**(before.steps-matches)
    value = F(weight, normalization)
    _guard(value, bit_limit=bit_limit)
    return value


@dataclass(frozen=True)
class JointState:
    encoded: JointCountState
    gradient_forms: tuple[F, ...] = ()

    def __post_init__(self):
        closed(self, JointState)
        require_state(self.encoded)
        expected = 2*len(self.encoded.model.rates)+1 if self.encoded.pending is not None else 0
        if (type(self.gradient_forms) is not tuple or len(self.gradient_forms) != expected
                or any(type(v) is not F for v in self.gradient_forms)):
            raise ContractError('complete exact joint pending gradient basis required')

    @property
    def theta(self):
        s = self.encoded
        return JointTheta(s.model, s.counts, s.diagonal, s.steps)

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
        model = self.encoded.model
        index(slot, model.slot_count, 'joint native gradient slot')
        if not self.unit_count:
            return F(0)
        if slot == 0:
            return self.gradient_forms[0]
        rate, world = model.hypothesis(slot-1)
        i, j, target = self.encoded.pending
        mismatch = int(model.world_bit(world, i)^model.world_bit(world, j) != target)
        return self.gradient_forms[1+2*rate+mismatch]

    def materialize(self, *, scalar_cap, budget=decoder.JointPartitionAllowance(), bit_limit=32768):
        """Explicit caller-allocated diagnostic, never an owner state setter."""
        self.__post_init__()
        model = self.encoded.model
        allowance(2*model.slot_count+3, scalar_cap, 'literal joint learner output allowance')
        # The query here only constructs Z. Pending counts still encode the
        # pre-observation parameters, independently of the current cursor.
        before = replace(self.encoded, pending=None)
        plan = decoder.passive_plan(before, (0, 0), budget, bit_limit=bit_limit)
        theta = tuple(_parameter(before, plan.normalization, slot, bit_limit=bit_limit) for slot in range(model.slot_count))
        return ReferenceLearnerState(theta, (), tuple(self.gradient(slot) for slot in range(model.slot_count)),
                                     self.unit_count, self.cursor, self.optimizer_steps)


@dataclass(frozen=True)
class JointEvaluation:
    before: JointCountState
    query: tuple[int, int]
    excesses: tuple[F, F]
    masses: tuple[F, F]
    normalizer: F
    probabilities: tuple[F, F]
    table_work: tuple[tuple[str, int], ...]

    def __post_init__(self):
        closed(self, JointEvaluation)
        require_state(self.before)
        self.before.model.query(self.query)
        if self.before.pending is not None:
            raise ContractError('joint cache requires its complete committed predecessor')
        for key in ('excesses', 'masses', 'probabilities'):
            values = getattr(self, key)
            if type(values) is not tuple or len(values) != 2 or any(type(v) is not F for v in values):
                raise ContractError('complete exact joint readout coordinates required')
        if type(self.normalizer) is not F or type(self.table_work) is not tuple:
            raise ContractError('joint cache lost its normalization or operation record')

    @property
    def delayed(self):
        return ()

    def activation_basis(self):
        model = self.before.model
        return (F(0), F(1))+tuple(F(c) for j in range(len(model.rates)) for c in model.coefficients(j))+self.excesses

    def materialize(self, *, scalar_cap):
        self.__post_init__()
        model = self.before.model
        allowance(model.counts()['nodes']+7, scalar_cap, 'literal joint cache output allowance')
        sources = tuple(F(v == self.query[side]) for side in (0, 1) for v in range(model.n))
        pairs = tuple(F((i, j) == self.query) for i in range(model.n) for j in range(model.n))
        features = []
        for rank in range(model.K):
            rate, world = model.hypothesis(rank)
            parity = model.world_bit(world, self.query[0])^model.world_bit(world, self.query[1])
            features.extend(F(model.coefficients(rate)[int(parity != target)]) for target in (0, 1))
        return Evaluation(sources+pairs+tuple(features)+self.excesses, self.excesses,
                          self.masses, self.normalizer, self.probabilities, ())


@dataclass(frozen=True)
class JointRangeBound:
    schema: JointRelation
    domain: CategoricalPairDomain
    proof: str = 'joint-positive-count-weights-all-categorical-mass-box-v1'

    @property
    def masses(self):
        low = self.schema.scale*min(self.schema.rates)
        return (Interval(low, self.schema.scale-low),)*2

    @property
    def normalizer(self):
        return Interval(F(self.schema.scale), F(self.schema.scale))

    def sufficient(self, *, normalizer_cap, activation_cap):
        closed(self, JointRangeBound)
        closed(self.schema, JointRelation)
        self.schema.__post_init__()
        closed(self.domain, CategoricalPairDomain)
        self.domain.__post_init__()
        if (self.domain.n != self.schema.n or type(self.proof) is not str
                or self.proof != type(self).proof):
            raise ContractError('joint whole-domain range lost its complete declaration')
        maximum = max(1, max(c for j in range(len(self.schema.rates)) for c in self.schema.coefficients(j)))
        return normalizer_cap >= self.schema.scale and activation_cap >= maximum


def _prepare_owned_prediction(program, rules, state, sources, budget, workspace, *, bit_limit):
    """Fixed owner kernel; no Runtime planner or result proposal port."""
    closed(state, JointState)
    state.__post_init__()
    if state.unit_count:
        raise ContractError('joint reference prediction requires an empty update unit')
    return decoder.prepare_bound(program, state.encoded, rules, sources, budget, workspace, bit_limit=bit_limit)


def _prediction_execution_work(plan):
    closed(plan, decoder.JointPartitionPlan)
    # Remaining exact ratios, complete coordinate binding and bounded record
    # scans. All integer tables/powers were already funded before preparation.
    return 128*(plan.before.n*(plan.before.n-1)//2+len(plan.before.model.rates)+plan.integer_envelope+32)


def _execute_owned_prediction(plan, schema):
    closed(plan, decoder.JointPartitionPlan)
    if type(schema) is not JointRelation or plan.before.model != schema or plan.before.pending is not None:
        raise ContractError('joint prediction plan lost its actual complete native predecessor')
    values = decoder.reference(plan)
    statistics = plan.shape+(('joint_multiplications', plan.multiplications), ('joint_additions', plan.additions),
        ('compacted_cells', plan.compacted_cells), ('integer_envelope', plan.integer_envelope),
        ('maximum_integer_bits', plan.maximum_integer_bits), ('workspace_bytes', plan.workspace_bytes))
    return JointEvaluation(plan.before, plan.query, values[:2], values[2:4], values[4], values[5:], statistics)


@dataclass(frozen=True)
class JointReferenceMachine(ReferenceMachineModel):
    schema: JointRelation
    budget: decoder.JointPartitionAllowance

    model_id = MODEL_ID
    initializer_id = 'indexed-joint-rate-prior-fair-world-unit-simplex-initializer-v1'
    program_type = JointRelation

    def __post_init__(self):
        closed(self, JointReferenceMachine)
        decoder.workspace_bytes(self.schema, self.budget)

    def require_program(self, program):
        closed(program, JointRelation)
        program.__post_init__()
        if program != self.schema:
            raise ContractError('joint native description differs from its registered model/Gamma')

    def node_count(self, program):
        self.require_program(program)
        return program.counts()['nodes']

    def state_work(self, program):
        self.require_program(program)
        return program.n*(program.n-1)//2+8*len(program.rates)+32

    def construction_work(self, program, rules):
        self.require_program(program)
        return 16*self.state_work(program)+32*program.n+64

    def evaluation_work(self, program, rules):
        self.require_program(program)
        return decoder.construction_work(program, self.budget)

    def observation_work(self, program):
        return 8*self.state_work(program)+64

    def commit_work(self, program, spec=None):
        return 4*self.state_work(program)+32

    def initializer_validation_work(self, program, spec):
        return 4*self.state_work(program)+32*program.n

    def zero_payload(self, program, rules):
        self.require_program(program)
        return JointZeroSlots(program), ()

    def initializer(self, slot_count, pattern):
        closed(pattern, JointInitializer)
        pattern.__post_init__()
        if pattern.schema != self.schema or slot_count != self.schema.slot_count:
            raise ContractError('joint Gamma differs from its registered complete model')
        return JointTheta(self.schema, (0,)*(self.schema.n*(self.schema.n-1)//2), 0, 0)

    def _learner(self, spec):
        closed(spec, JointLearner)
        spec.__post_init__()
        if spec.schema != self.schema:
            raise ContractError('joint U refers to another ordered native model')

    def initial_state(self, program, rules, theta, cursor, *, spec, bit_limit):
        self.require_program(program)
        program.validate(rules)
        self._learner(spec)
        closed(theta, JointTheta)
        theta.__post_init__()
        if theta.schema != program or theta.steps or theta.diagonal or any(theta.counts):
            raise ContractError('joint construction must start at its registered prior')
        if program.n+program.prior_scale.bit_length()+8 > bit_limit:
            raise ArithmeticUnresolved('joint initializer exceeds its exact reference integer allowance')
        return JointState(initialize(program, cursor))

    def observe(self, program, state, spec, prediction, target, *, bit_limit):
        self.require_program(program)
        self._learner(spec)
        closed(state, JointState)
        closed(prediction, JointEvaluation)
        state.__post_init__()
        prediction.__post_init__()
        if state.unit_count or state.encoded.model != program or prediction.before != state.encoded:
            raise ContractError('joint observation lost its owned pre-target state and prediction')
        following = observe(state.encoded, prediction.query, target)
        scale, mass = program.scale, prediction.masses[target]
        gradients = (1/mass-F(2, scale),)+tuple(F(scale-2, scale)-F(c)/mass
            for j in range(len(program.rates)) for c in program.coefficients(j))
        _guard(*gradients, bit_limit=bit_limit)
        return JointState(following, gradients)

    def commit(self, state, spec, *, bit_limit):
        self._learner(spec)
        closed(state, JointState)
        state.__post_init__()
        if state.encoded.model != self.schema:
            raise ContractError('joint commit belongs to another native state')
        return JointState(commit(state.encoded))

    def attach(self, state, cursor, spec):
        self._learner(spec)
        closed(state, JointState)
        state.__post_init__()
        if state.encoded.model != self.schema:
            raise ContractError('joint attachment belongs to another native state')
        return JointState(attach(state.encoded, cursor))

    @staticmethod
    def activation_values(prediction):
        closed(prediction, JointEvaluation)
        return prediction.activation_basis()

    def range_bound(self, program, rules, theta, domain):
        self.require_program(program)
        program.validate(rules)
        closed(theta, JointTheta)
        theta.__post_init__()
        if (theta.schema != program or type(domain) is not CategoricalPairDomain
                or vars(domain) != {'n': program.n}):
            raise ContractError('joint range requires its complete encoded parameters and entire categorical domain')
        domain.__post_init__()
        return JointRangeBound(program, domain)
