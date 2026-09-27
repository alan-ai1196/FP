"""Complete compact token states executed only by ReferenceCompilerRuntime.

An immutable committed origin and every pending source/target record decode
the native learner, including every gradient coordinate. Binary64 enclosures
are solver workspace; an optional CUDA owner retains bound forests separately
under complete binding/payment. Only uniquely proved exact grid masters become
a successor. No independent ingress, certificate or install endpoint.
"""
from dataclasses import dataclass, fields, replace
from fractions import Fraction as F
import struct
import sys

from .core import ContractError, natural, stable_hash
from .learner import ReferenceLearnerState
from .machine import ReferenceMachineModel
from .program import Product, Sum, Term
from .semantics import ArithmeticUnresolved, Interval, _guard, _operation
from .token_sources import TokenAtomFamily, TokenValues
from .token_causal import TokenSources, TokenWindow
from .token_native import Definition
from .token_readout import Spec
from .token_enclosures import EnclosureUnresolved


def closed(value, kind):
    if type(value) is not kind or set(vars(value)) != {f.name for f in fields(kind)}:
        raise ContractError('complete immutable '+kind.__name__+' required')


def definition_check(d):
    closed(d, Definition)
    closed(d.sources, TokenSources)
    closed(d.output, Spec)
    try:
        d.__post_init__()
    except ValueError as error:
        raise ContractError(str(error)) from error
    for node in d.nodes:
        closed(node, type(node))
        if type(node) is Sum:
            if type(node.terms) is not tuple:
                raise ContractError('immutable complete SUM edges required')
            for term in node.terms:
                closed(term, Term)


@dataclass(frozen=True)
class TokenProgram:
    definition: Definition

    def __post_init__(self):
        closed(self, TokenProgram)
        definition_check(self.definition)

    @property
    def slot_count(self):
        return self.definition.slot_count

    @property
    def program_id(self):
        return stable_hash(self)

    def counts(self):
        c = self.definition.cardinalities()
        return dict(nodes=c['sources']+c['sum_nodes']+c['product_nodes'],
                    SUMs=c['sum_nodes'], PRODUCTs=c['product_nodes'],
                    edges=c['incoming_edges'], slots=c['parameter_slots'])

    def validate(self, rules):
        self.__post_init__()
        d = self.definition
        if (type(rules.sources) is not TokenAtomFamily or rules.sources.type_id != 'f'
                or (rules.sources.vocabulary, rules.sources.context) != (d.sources.vocabulary, d.sources.context)
                or rules.base != d.output.base or rules.readout_type != 'f'
                or 'f' not in rules.sum_types or rules.states
                or any(type(n) is Product for n in d.nodes) and ('f', 'f', 'f') not in rules.product_rules):
            raise ContractError('token lowering differs from the complete typed native interface')


@dataclass(frozen=True)
class TokenInitializer:
    sources: TokenAtomFamily
    width: int
    output: Spec
    # Cyclic integer-grid patterns for complete flattened E, core and W blocks.
    embedding: tuple[int, ...]
    core: tuple[int, ...]
    readout: tuple[int, ...]
    element_cap: int

    def __post_init__(self):
        closed(self, TokenInitializer)
        if type(self.sources) is not TokenAtomFamily:
            raise ContractError('registered indexed token source family required')
        self.sources.__post_init__()
        closed(self.output, Spec)
        try:
            self.output.__post_init__()
        except ValueError as error:
            raise ContractError(str(error)) from error
        natural(self.width, 'token embedding width', positive=True)
        natural(self.element_cap, 'token solver per-array allowance', positive=True)
        if self.sources.type_id != 'f' or self.sources.vocabulary != self.output.labels:
            raise ContractError('token source and readout alphabets differ')
        for pattern in (self.embedding, self.core, self.readout):
            if type(pattern) is not tuple or not pattern or any(type(q) is not int or not 0 <= q < 1 << 32 for q in pattern):
                raise ContractError('immutable nonempty uint32 initializer patterns required')

    def validate(self, rules):
        self.__post_init__()
        if (rules.sources != self.sources or rules.base != self.output.base
                or rules.states or rules.readout_type != 'f' or 'f' not in rules.sum_types):
            raise ContractError('token Gamma differs from registered source/readout semantics')


@dataclass(frozen=True)
class TokenLearner:
    output: Spec

    optimizer_id = 'mean-ce-projected-sgd-v1'

    def __post_init__(self):
        closed(self, TokenLearner)
        closed(self.output, Spec)
        try:
            self.output.__post_init__()
        except ValueError as error:
            raise ContractError(str(error)) from error

    @property
    def update_unit(self):
        return self.output.update_unit

    @property
    def learning_rate(self):
        return self.output.learning_rate

    @property
    def commit_grid_bits(self):
        return self.output.grid_bits


@dataclass(frozen=True)
class TokenTheta:
    embedding: bytes
    core: bytes
    output: bytes


@dataclass(frozen=True)
class TokenZeroSlots:
    count: int


@dataclass(frozen=True)
class TokenState:
    origin: object
    windows: tuple[TokenWindow, ...] = ()
    targets: tuple[int, ...] = ()

    @property
    def theta(self):
        return TokenTheta(self.origin.embedding, self.origin.core, self.origin.output)

    @property
    def delayed(self):
        return ()

    @property
    def unit_count(self):
        return len(self.targets)

    @property
    def cursor(self):
        return self.origin.cursor+self.unit_count

    @property
    def optimizer_steps(self):
        return self.origin.optimizer_steps

    @property
    def source(self):
        return self.windows[-1].append(self.targets[-1]) if self.targets else self.origin.source

    def materialize(self, *, scalar_cap, bit_limit=32768):
        """Caller-funded diagnostic decoder, never a live-state setter."""
        from .token_batch import Unit
        natural(scalar_cap, 'token literal diagnostic allowance', positive=True)
        d = self.origin.definition
        if 2*d.slot_count+3 > scalar_cap:
            raise ArithmeticUnresolved('literal token state exceeds its diagnostic allowance')
        native = Unit(self.origin, self.windows, self.targets).exact_decoder()
        theta = tuple(native.parameter(i) for i in range(d.slot_count))
        gradients = tuple(native.gradient(i) for i in range(d.slot_count))
        _guard(*theta, *gradients, bit_limit=bit_limit)
        return ReferenceLearnerState(theta, (), gradients, self.unit_count, self.cursor, self.optimizer_steps)


def add(x, y, bits):
    return _operation(x, y, multiply=False, bit_limit=bits)


def mul(x, y, bits):
    return _operation(x, y, multiply=True, bit_limit=bits)


def total(values, bits):
    result = F(0)
    for value in values:
        result = add(result, value, bits)
    return result


@dataclass(frozen=True)
class TokenProbabilities:
    origin: object
    features: tuple[F, ...]
    normalizer: F
    bit_limit: int

    def __len__(self):
        return self.origin.definition.output.labels

    def __getitem__(self, label):
        natural(label, 'token prediction label')
        if label >= len(self):
            raise IndexError(label)
        d = self.origin.definition
        excess = total((mul(F(int(q), d.output.grid), z, self.bit_limit)
                        for q, z in zip(self.origin.W[label], self.features)), self.bit_limit)
        mass = add(d.output.base[label], excess, self.bit_limit)
        # The reciprocal is guarded before the exact division operation.
        return mul(mass, F(self.normalizer.denominator, self.normalizer.numerator), self.bit_limit)


@dataclass(frozen=True)
class TokenEvaluation:
    before: TokenState
    window: TokenWindow
    values: tuple[F, ...]
    normalizer: F
    head_upper: F
    probabilities: TokenProbabilities

    @property
    def delayed(self):
        return ()


@dataclass(frozen=True)
class TokenRangeBound:
    values: tuple[Interval, ...]
    normalizer: Interval
    proof: str = 'all-categorical-token-contexts-positive-column-bound-v1'

    def sufficient(self, *, normalizer_cap, activation_cap):
        return self.normalizer.upper <= normalizer_cap and all(v.upper <= activation_cap for v in self.values)


@dataclass(frozen=True)
class TokenReferenceMachine(ReferenceMachineModel):
    pattern: TokenInitializer
    shared_storage: bool = False

    initializer_id = 'registered-token-block-cyclic-grid-initializer-v1'
    program_type = TokenProgram

    def __post_init__(self):
        if type(self.shared_storage) is not bool:
            raise ContractError('fixed token reference storage registration required')

    @property
    def model_id(self):
        return ('packed-complete-token-record-reference-v1' if not self.shared_storage else
                'complete-token-record-shared-byte-reference-v1')

    def realize(self, object_id, kind, value, provenance):
        if self.shared_storage and kind != 'reserved_target':
            from .shared_reference import SharedPlannedObject, ROOT_BYTES
            from .resources import ObjectSpec
            return SharedPlannedObject(ObjectSpec(object_id, kind,
                {'reference_payload_bytes': ROOT_BYTES, 'physical_objects': 1}, provenance), value)
        return super().realize(object_id, kind, value, provenance)

    def require_program(self, program):
        closed(program, TokenProgram)
        d, p = program.definition, self.pattern
        if (d.sources.vocabulary, d.sources.context, d.width, d.output) != (p.sources.vocabulary, p.sources.context, p.width, p.output):
            raise ContractError('native token program differs from registered Gamma/U shapes')

    def node_count(self, program):
        d = program.definition
        return d.sources.source_count+d.input_nodes+len(d.nodes)+d.output.labels

    def state_work(self, program):
        return program.slot_count+1

    def construction_work(self, program, rules):
        self.require_program(program)
        d = program.definition
        return 16*(d.slot_count+d.input_nodes+sum(len(n.terms) if type(n) is Sum else 2 for n in d.nodes)+1)

    def evaluation_work(self, program, rules):
        return self.construction_work(program, rules)

    def observation_work(self, program):
        # Revalidate the complete pre-target cache and append one source point.
        return self.construction_work(program, None)+4*(program.definition.sources.context+program.definition.output.update_unit+1)

    def commit_work(self, program, spec=None):
        d = program.definition
        edges = sum(len(n.terms) if type(n) is Sum else 2 for n in d.nodes)
        n = d.output.update_unit
        # Conservative abstract tariff includes every prefix incidence and
        # grouped reduction round. Not a physical time or heap claim.
        return 256*(d.slot_count+n*(d.input_nodes+len(d.nodes)+edges+d.output.features+1)*(n*d.sources.context+1).bit_length()+d.output.labels)

    def initializer_validation_work(self, program, spec):
        return 0

    def zero_payload(self, program, rules):
        return TokenZeroSlots(program.slot_count), ()

    def initializer(self, slot_count, pattern):
        p = self.pattern
        if pattern != p or sys.byteorder != 'little' or p.output.grid_bits > 32 or p.output.labels > 1 << 20:
            raise ArithmeticUnresolved('registered token packed word/grid/column realization unavailable')
        e, w = (p.sources.vocabulary+1)*p.width, p.output.labels*p.output.features
        c = slot_count-e-w
        if c < 0:
            raise ContractError('native token slot blocks disagree')
        if max(e, c, w) > p.element_cap:
            raise ArithmeticUnresolved('token master array allowance exhausted before allocation')
        def block(count, values):
            raw = b''.join(struct.pack('<I', q) for q in values[:min(count, len(values))])
            return raw*(count//len(values))+raw[:4*(count % len(values))]
        return TokenTheta(block(e, p.embedding), block(c, p.core), block(w, p.readout))

    def _learner(self, spec):
        if type(spec) is not TokenLearner or spec.output != self.pattern.output:
            raise ContractError('token Gamma and U require the same registered update')

    def initial_state(self, program, rules, theta, cursor, *, spec, bit_limit):
        from .token_batch import Origin, Kernel
        self.require_program(program)
        self._learner(spec)
        d = program.definition
        try:
            Kernel(d, element_cap=self.pattern.element_cap)
            source = TokenWindow(d.sources, 0, (d.sources.padding,)*d.sources.context)
            result = TokenState(Origin(d, theta.embedding, theta.core, theta.output, cursor, 0, source))
        except EnclosureUnresolved as error:
            raise ArithmeticUnresolved(str(error)) from error
        _guard(F((1 << 32)-1, d.output.grid), bit_limit=bit_limit)
        return result

    def _forward(self, origin, inputs, bit_limit):
        d = origin.definition
        values = list(inputs)
        for node in d.nodes:
            if type(node) is Sum:
                value = total((mul(F(int(origin.C[t.slot]), d.output.grid), values[t.parent], bit_limit) for t in node.terms), bit_limit)
            else:
                value = mul(values[node.left], values[node.right], bit_limit)
            values.append(value)
        features = tuple(values[i] for i in d.features)
        # Integer column sums are exact: V <= 2^20, each q < 2^32.
        columns = origin.W.sum(axis=0, dtype='int64')
        normalizer = add(total(d.output.base, bit_limit), total((mul(F(int(q), d.output.grid), z, bit_limit) for q, z in zip(columns, features)), bit_limit), bit_limit)
        head = total((mul(F(int(q), d.output.grid), z, bit_limit) for q, z in zip(origin.W.max(axis=0), features)), bit_limit)
        return tuple(values), normalizer, head, features

    def predict(self, program, rules, state, sources, *, bit_limit):
        self.require_program(program)
        if (type(state) is not TokenState or state.origin.definition != program.definition
                or state.unit_count >= self.pattern.output.update_unit):
            raise ContractError('token prediction requires a complete eligible predecessor')
        if type(sources) is not TokenValues or sources.context.family != rules.sources:
            raise ContractError('token prediction requires the owned complete source interface')
        context, d = sources.context, program.definition
        context.__post_init__()
        window = TokenWindow(d.sources, context.position, context.past)
        inputs = tuple(F(int(q), d.output.grid) for token in window.past for q in state.origin.E[token])
        values, z, head, features = self._forward(state.origin, inputs, bit_limit)
        return TokenEvaluation(state, window, values, z, head, TokenProbabilities(state.origin, features, z, bit_limit))

    def observe(self, program, state, spec, prediction, target, *, rules, sources, bit_limit):
        self.require_program(program)
        self._learner(spec)
        natural(target, 'token observation target')
        if target >= spec.output.labels or type(prediction) is not TokenEvaluation or prediction.before is not state:
            raise ContractError('token observation lost its actual pre-target predecessor')
        closed(prediction, TokenEvaluation)
        closed(prediction.probabilities, TokenProbabilities)
        expected = self.predict(program, rules, state, sources, bit_limit=bit_limit)
        if prediction != expected:
            raise ContractError('token cache differs from the actual retained source/predecessor')
        return TokenState(state.origin, state.windows+(prediction.window,), state.targets+(target,))

    def commit(self, state, spec, *, bit_limit):
        from .token_batch import Kernel
        self._learner(spec)
        if state.unit_count != spec.update_unit or state.cursor % spec.update_unit:
            raise ContractError('token commit requires a whole owned update unit')
        try:
            kernel = Kernel(state.origin.definition, element_cap=self.pattern.element_cap)
            bounds = kernel.bound(state.origin, state.windows, state.targets)
            return TokenState(bounds.commit())
        except EnclosureUnresolved as error:
            # Runtime already owns the target, observation trace and complete
            # pending recipe. No partial numerical successor is published.
            raise ArithmeticUnresolved(str(error)) from error

    def attach(self, state, cursor, spec):
        self._learner(spec)
        natural(cursor, 'token ordinary attachment cursor')
        if state.unit_count or state.cursor % spec.update_unit or cursor % spec.update_unit:
            raise ContractError('token attachment requires complete update boundaries')
        return replace(state, origin=replace(state.origin, cursor=cursor))

    @staticmethod
    def activation_values(prediction):
        return (F(1),)+prediction.values+(prediction.head_upper,)

    def range_bound(self, program, rules, theta, *, bit_limit):
        from .token_batch import Origin
        self.require_program(program)
        d = program.definition
        source = TokenWindow(d.sources, 0, (d.sources.padding,)*d.sources.context)
        origin = Origin(d, theta.embedding, theta.core, theta.output, 0, 0, source)
        maximum = tuple(F(int(q), d.output.grid) for q in origin.E.max(axis=0))
        values, z, head, _ = self._forward(origin, maximum*d.sources.context, bit_limit)
        return TokenRangeBound(tuple(Interval(F(0), v) for v in (F(1),)+values+(head,)),
                               Interval(total(d.output.base, bit_limit), z))
