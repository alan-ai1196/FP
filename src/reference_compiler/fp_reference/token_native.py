"""Complete passive exact token learner from indexed SUMs and a native DAG.

Embedding lookup abbreviates all declared lag/token SUM edges; it is not
a primitive feature oracle. Final readout slots are untied. No Runtime,
physical resource, AMP, search, persistence or installation authority.
"""
from dataclasses import dataclass, replace
from fractions import Fraction as F

from .program import Sum, Product, Term
from .token_causal import TokenSources, TokenWindow
from . import token_readout as readout


@dataclass(frozen=True)
class Definition:
    sources: TokenSources
    width: int
    # Prefix nodes are indexed SUMs e_(lag,k), ordered by lag then channel.
    # These ordinary native nodes follow that prefix, with local core slots.
    nodes: tuple[Sum | Product, ...]
    slots: int
    features: tuple[int, ...]
    output: readout.Spec

    def __post_init__(self):
        if type(self.sources) is not TokenSources or type(self.output) is not readout.Spec:
            raise ValueError('closed source and readout definitions required')
        self.sources.__post_init__()
        self.output.__post_init__()
        readout.natural(self.width, positive=True)
        readout.natural(self.slots)
        if self.sources.vocabulary != self.output.labels:
            raise ValueError('source and target alphabets differ')
        if type(self.nodes) is not tuple or type(self.features) is not tuple or len(self.features) != self.output.features:
            raise ValueError('complete immutable core DAG and feature list required')
        for index, node in enumerate(self.nodes, self.input_nodes):
            if type(node) not in (Sum, Product) or node.type_id != 'f':
                raise ValueError('core admits only declared f SUM/PRODUCT nodes')
            if type(node) is Sum:
                for term in node.terms:
                    if type(term) is not Term:
                        raise ValueError('native parameterized SUM edge required')
                    readout.natural(term.slot)
                    if term.slot >= self.slots:
                        raise ValueError('SUM slot outside the complete core block')
                parents = tuple(term.parent for term in node.terms)
            else:
                parents = (node.left, node.right)
            for parent in parents:
                readout.natural(parent)
                if parent >= index:
                    raise ValueError('same-time parents must precede their node')
        for feature in self.features:
            readout.natural(feature)
            if feature >= self.input_nodes+len(self.nodes):
                raise ValueError('feature outside the complete native core')

    @property
    def input_nodes(self):
        return self.sources.context*self.width

    @property
    def embedding_slots(self):
        return (self.sources.vocabulary+1)*self.width

    @property
    def slot_count(self):
        return self.embedding_slots+self.slots+self.output.labels*self.output.features

    def cardinalities(self):
        sums = self.input_nodes+sum(type(n) is Sum for n in self.nodes)+self.output.labels
        products = sum(type(n) is Product for n in self.nodes)
        edges = self.input_nodes*(self.sources.vocabulary+1)+sum(
            len(n.terms) if type(n) is Sum else 2 for n in self.nodes)+self.output.labels*self.output.features
        return dict(sources=self.sources.source_count, sum_nodes=sums, product_nodes=products,
            incoming_edges=edges, parameter_slots=self.slot_count)


@dataclass(frozen=True)
class Embedding:
    defaults: tuple[int, ...]
    # flattened (token, channel) -> explicit grid master; default is per channel.
    overrides: readout.Node | None = None

    def master(self, coordinate):
        value = readout.get(self.overrides, coordinate)
        return self.defaults[coordinate % len(self.defaults)] if value is None else value

    def write(self, coordinate, master):
        readout.natural(master)
        default = self.defaults[coordinate % len(self.defaults)]
        return replace(self, overrides=readout.put(self.overrides, coordinate, None if master == default else master))


@dataclass(frozen=True)
class Learner:
    definition: Definition
    embedding: Embedding
    theta: tuple[int, ...]
    output: readout.State
    past: tuple[int, ...]
    embedding_gradient: tuple[tuple[int, F], ...]
    core_gradient: tuple[F, ...]
    # Default contiguous source-reader position, distinct from U's clock.
    source_position: int = 0

    @property
    def cursor(self):
        return self.output.cursor

    def parameter(self, slot):
        readout.natural(slot)
        d, grid = self.definition, self.definition.output.grid
        if slot < d.embedding_slots:
            return F(self.embedding.master(slot), grid)
        slot -= d.embedding_slots
        if slot < d.slots:
            return F(self.theta[slot], grid)
        slot -= d.slots
        return self.output.parameter(slot//d.output.features, slot % d.output.features)

    def gradient(self, slot):
        readout.natural(slot)
        d = self.definition
        if slot < d.embedding_slots:
            return next((g for s, g in self.embedding_gradient if s == slot), F(0))
        slot -= d.embedding_slots
        if slot < d.slots:
            return self.core_gradient[slot]
        slot -= d.slots
        return self.output.gradient(slot//d.output.features, slot % d.output.features)

    def source_window(self, window=None):
        if window is None:
            window = TokenWindow(self.definition.sources, self.source_position, self.past)
        if type(window) is not TokenWindow or window.schema != self.definition.sources:
            raise ValueError('complete registered token source point required')
        window.__post_init__()
        return window

    def predict(self, window=None):
        d, grid = self.definition, self.definition.output.grid
        window = self.source_window(window)
        values = [F(self.embedding.master(token*d.width+k), grid)
                  for token in window.past for k in range(d.width)]
        for node in d.nodes:
            if type(node) is Sum:
                values.append(sum((F(self.theta[t.slot], grid)*values[t.parent] for t in node.terms), F(0)))
            else:
                values.append(values[node.left]*values[node.right])
        values = tuple(values)
        return Prediction(self, window, values, self.output.predict(tuple(values[i] for i in d.features)))

    def observe(self, prediction, target, *, window=None):
        if type(prediction) is not Prediction or prediction.state is not self:
            raise ValueError('prediction lost its actual complete token learner')
        # The actual source point is an independent argument supplied by its
        # owner, not reconstructed from potentially altered cache metadata.
        expected = self.predict(window)
        if (prediction.window != expected.window or prediction.values != expected.values
                or prediction.output.features != expected.output.features
                or prediction.output.state is not self.output):
            raise ValueError('token/core cache differs from the actual causal predecessor')
        following_output, feature_adjoints = self.output.observe(prediction.output, target)
        d, grid = self.definition, self.definition.output.grid
        adjoints = [F(0)]*len(prediction.values)
        for index, seed in zip(d.features, feature_adjoints):
            adjoints[index] += seed
        core_gradient = list(self.core_gradient)
        for index in range(len(prediction.values)-1, d.input_nodes-1, -1):
            node, seed = d.nodes[index-d.input_nodes], adjoints[index]
            if type(node) is Sum:
                for term in node.terms:
                    core_gradient[term.slot] += seed*prediction.values[term.parent]
                    adjoints[term.parent] += seed*F(self.theta[term.slot], grid)
            else:
                # Separate incidences are essential for squares/shared parents.
                adjoints[node.left] += seed*prediction.values[node.right]
                adjoints[node.right] += seed*prediction.values[node.left]
        embedding_gradient = dict(self.embedding_gradient)
        for lag, token in enumerate(expected.window.past):
            for k in range(d.width):
                coordinate = token*d.width+k
                embedding_gradient[coordinate] = embedding_gradient.get(coordinate, F(0))+adjoints[lag*d.width+k]
        following_window = expected.window.append(target)
        return replace(self, output=following_output, past=following_window.past, source_position=following_window.position,
            embedding_gradient=tuple(sorted(embedding_gradient.items())), core_gradient=tuple(core_gradient))

    def commit(self):
        # The readout checks the registered complete unit and owns the clocks.
        following_output = self.output.commit()
        scale = self.definition.output.grid*self.definition.output.learning_rate/self.definition.output.update_unit
        def update(master, gradient):
            value = master-scale*gradient
            return max(0, value.numerator//value.denominator)
        embedding = self.embedding
        for coordinate, gradient in self.embedding_gradient:
            embedding = embedding.write(coordinate, update(self.embedding.master(coordinate), gradient))
        theta = tuple(update(q, g) for q, g in zip(self.theta, self.core_gradient))
        return replace(self, embedding=embedding, theta=theta, output=following_output,
            embedding_gradient=(), core_gradient=(F(0),)*self.definition.slots)


@dataclass(frozen=True)
class Prediction:
    state: Learner
    window: TokenWindow
    values: tuple[F, ...]
    output: readout.Prediction


def initialize(definition, embedding_defaults, core_masters, output_defaults, *, embedding_overrides=(), output_overrides=()):
    if type(definition) is not Definition:
        raise ValueError('closed native token definition required')
    definition.__post_init__()
    if (type(embedding_defaults) is not tuple or len(embedding_defaults) != definition.width
            or type(core_masters) is not tuple or len(core_masters) != definition.slots):
        raise ValueError('complete initializer dimensions required')
    for master in embedding_defaults+core_masters:
        readout.natural(master)
    embedding = Embedding(embedding_defaults)
    seen = set()
    for token, channel, master in embedding_overrides:
        readout.natural(token)
        readout.natural(channel)
        readout.natural(master)
        coordinate = token*definition.width+channel
        if token > definition.sources.vocabulary or channel >= definition.width or coordinate in seen:
            raise ValueError('duplicate or foreign embedding initializer')
        seen.add(coordinate)
        embedding = embedding.write(coordinate, master)
    output = readout.initialize(definition.output, output_defaults, output_overrides)
    return Learner(definition, embedding, core_masters, output, (definition.sources.padding,)*definition.sources.context,
        (), (F(0),)*definition.slots)


def materialize(definition):
    """Literal audit expansion of the indexed G. Caller must fund its size."""
    from .program import Source, SourceSpec, SemanticRules, Program
    d, width, vocabulary = definition, definition.width, definition.sources.vocabulary
    names = tuple(f'lag{lag}/token{token}' for lag in range(1, d.sources.context+1) for token in range(vocabulary+1))
    rules = SemanticRules(tuple(SourceSpec(f'lag{lag}/token{token}', 'f', lag, F(1))
        for lag in range(1, d.sources.context+1) for token in range(vocabulary+1)),
        ('f',), (('f', 'f', 'f'),), 'f', d.output.base)
    nodes = [Source(name) for name in names]
    offset = len(nodes)
    for lag in range(d.sources.context):
        for channel in range(width):
            nodes.append(Sum('f', tuple(Term(lag*(vocabulary+1)+token, token*width+channel) for token in range(vocabulary+1))))
    for node in d.nodes:
        if type(node) is Sum:
            nodes.append(Sum('f', tuple(Term(offset+t.parent, d.embedding_slots+t.slot) for t in node.terms)))
        else:
            nodes.append(Product('f', offset+node.left, offset+node.right))
    heads = []
    output_offset = d.embedding_slots+d.slots
    for label in range(vocabulary):
        heads.append(len(nodes))
        nodes.append(Sum('f', tuple(Term(offset+feature, output_offset+label*d.output.features+k) for k, feature in enumerate(d.features))))
    program = Program(tuple(nodes), d.slot_count, tuple(heads))
    program.validate(rules)
    return rules, program
