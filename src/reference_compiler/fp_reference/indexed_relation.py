"""Indexed description and exact point decoders for the literal relation code.

No record or point decoder supplies Runtime admission or installation authority.
"""
from dataclasses import dataclass, field
from fractions import Fraction as F
from itertools import combinations
from . import indexed_count as counts, positive_partition as frontier
from .core import ContractError, natural, stable_hash
from .learner import SIMPLEX_GRADIENT, LearnerSpec, ReferenceLearnerState
from .program import Product, Program, SemanticRules, Source, SourceSpec, Sum, Term, rational
from .semantics import ArithmeticUnresolved, Evaluation

SCHEMA = 'literal-anchored-relation-index-v1'
MAX_N = 1024                       # Prototype bound, not a mathematical limit.


def index(value, stop, name):
    natural(value, name)
    if value >= stop:
        raise ContractError(f'{name} outside the declared finite index set')
    return value


def allowance(required, cap, name):
    natural(cap, name, positive=True)
    if required > cap:
        raise ArithmeticUnresolved(f'{name} is insufficient for this explicit read')


@dataclass(frozen=True)
class NodeHeader:
    kind: str
    type_id: str = 'mass'
    source_id: str | None = None
    parents: tuple[int, ...] = ()
    arity: int = 0


@dataclass(frozen=True)
class IndexedRelation:
    n: int

    def __post_init__(self):
        natural(self.n, 'declared token count')
        if self.n < 2:
            raise ContractError('the indexed relation family requires at least two tokens')
        if self.n > MAX_N:
            raise ArithmeticUnresolved('indexed prototype token allowance exceeded')

    @property
    def descriptor(self):
        # This is NOT the hash/program_id of the fully serialized native graph.
        return SCHEMA, self.n

    @property
    def program_id(self):
        # Runtime identity of this exact description, in a separate namespace
        # from Program.program_id's fully serialized native syntax.
        return stable_hash(('indexed-native-description-v1', self.descriptor))

    def counts(self):
        return self.graph_counts()

    def validate(self, rules):
        # The indexing theorem proves the complete native typing judgment;
        # this checks its entire external declaration, not sampled nodes.
        if type(rules) is not SemanticRules or rules != self.rules():
            raise ContractError('indexed code requires its complete fixed semantic declarations')

    @property
    def K(self):
        return 1 << (self.n-1)

    @property
    def first_indicator(self):
        return 2*self.n+self.n*self.n

    @property
    def heads(self):
        first = self.first_indicator+2*self.K
        return first, first+1

    @property
    def slot_count(self):
        return self.K+1

    def graph_counts(self):
        n, K = self.n, self.K
        return {'nodes': self.first_indicator+2*K+2, 'sources': 2*n,
                'state_reads': 0, 'SUMs': 2*K+2, 'PRODUCTs': n*n,
                'SUM_edges': K*(n*n+16), 'edges': K*(n*n+16)+2*n*n,
                'slots': K+1, 'bindings': 0}

    def rules(self):
        sources = tuple(SourceSpec(f'x{side}:{i}', 'mass', 0, F(1))
                        for side in (0, 1) for i in range(self.n))
        return SemanticRules(sources, ('mass',), (('mass', 'mass', 'mass'),),
                             'mass', (F(1), F(1)))

    def world_bit(self, world, vertex):
        index(world, self.K, 'native world index')
        index(vertex, self.n, 'native world vertex')
        # itertools.product((0,1), repeat=n-1) uses this big-endian order.
        return 0 if vertex == 0 else (world >> (self.n-1-vertex)) & 1

    def selected_slot(self, rank):
        return index(rank, self.K, 'selected-slot rank')+1

    def gamma(self, slot):
        index(slot, self.slot_count, 'initializer slot')
        return F(1) if slot == 0 else F(1, self.K)

    def materialize_learner(self, *, slot_cap):
        allowance(self.slot_count, slot_cap, 'literal learner slot allowance')
        return LearnerSpec(1, F(1), optimizer_id=SIMPLEX_GRADIENT,
                           simplex_slots=tuple(range(1, self.slot_count)))

    def source_row(self, rank):
        index(rank, self.n*self.n, 'categorical source row')
        return {f'x{side}:{v}': F(v == (rank//self.n, rank % self.n)[side])
                for side in (0, 1) for v in range(self.n)}

    def source_query(self, rules, source_values):
        if type(rules) is not SemanticRules or rules != self.rules():
            raise ContractError('source/types/bases/delays differ from the indexed schema')
        names = tuple(s.source_id for s in rules.sources)
        if len(source_values) != 2*self.n or set(source_values) != set(names):
            raise ContractError('complete categorical source interface required')
        values = tuple(rational(source_values[name], 'categorical source value') for name in names)
        query = []
        for side in (0, 1):
            row = values[side*self.n:(side+1)*self.n]
            if any(v not in (0, 1) for v in row) or sum(row) != 1:
                raise ContractError('this decoder requires exactly one categorical token per side')
            query.append(row.index(F(1)))
        return tuple(query), values

    def header(self, node):
        index(node, self.graph_counts()['nodes'], 'native node index')
        n, A = self.n, self.first_indicator
        if node < 2*n:
            return NodeHeader('SOURCE', source_id=f'x{node//n}:{node % n}')
        if node < A:
            pair = node-2*n
            return NodeHeader('PRODUCT', parents=(pair//n, n+pair % n))
        if node < self.heads[0]:
            world, y = divmod(node-A, 2)
            ones = world.bit_count()
            zeros = n-ones
            return NodeHeader('SUM', arity=zeros*zeros+ones*ones if y == 0 else 2*zeros*ones)
        return NodeHeader('SUM', arity=8*self.K)

    def term(self, node, rank):
        header = self.header(node)
        if header.kind != 'SUM':
            raise ContractError('only native SUM nodes have slot-bound terms')
        index(rank, header.arity, 'ordered SUM incidence')
        if node >= self.heads[0]:
            world = rank//8
            return Term(self.first_indicator+2*world+node-self.heads[0], world+1)
        world, y = divmod(node-self.first_indicator, 2)
        groups = [[], []]
        bits = tuple(self.world_bit(world, v) for v in range(self.n))
        for v, bit in enumerate(bits):
            groups[bit].append(v)
        for i, bit in enumerate(bits):
            candidates = groups[bit ^ y]
            if rank < len(candidates):
                return Term(2*self.n+i*self.n+candidates[rank], 0)
            rank -= len(candidates)
        raise AssertionError('indicator arity and incidence rank disagree')

    def materialize_node(self, node, *, term_cap):
        header = self.header(node)
        allowance(header.arity, term_cap, 'literal node term allowance')
        if header.kind == 'SOURCE':
            return Source(header.source_id)
        if header.kind == 'PRODUCT':
            return Product('mass', *header.parents)
        if node >= self.heads[0]:
            return Sum('mass', tuple(self.term(node, t) for t in range(header.arity)))
        world, y = divmod(node-self.first_indicator, 2)
        bits = tuple(self.world_bit(world, v) for v in range(self.n))
        return Sum('mass', tuple(Term(2*self.n+i*self.n+j, 0)
                                for i in range(self.n) for j in range(self.n)
                                if bits[i] ^ bits[j] == y))

    def materialize_program(self, *, node_cap, term_cap, slot_cap):
        sizes = self.graph_counts()
        # All preflights precede the first node/term/slot output allocation.
        allowance(sizes['nodes'], node_cap, 'literal Program node allowance')
        allowance(sizes['SUM_edges'], term_cap, 'literal Program term allowance')
        allowance(sizes['slots'], slot_cap, 'literal Program slot allowance')
        return Program(tuple(self.materialize_node(i, term_cap=term_cap)
                             for i in range(sizes['nodes'])), self.slot_count, self.heads)

    def compare_literal(self, program, rules, gamma, learner, *, node_cap, term_cap, slot_cap):
        """Full structural comparison, not a compact unchecked program-ID match."""
        expected = self.materialize_program(node_cap=node_cap, term_cap=term_cap, slot_cap=slot_cap)
        if (type(program) is not Program or program != expected or
                type(rules) is not SemanticRules or rules != self.rules() or
                type(gamma) is not tuple or any(type(v) not in (int, F) for v in gamma) or
                gamma != tuple(self.gamma(k) for k in range(self.slot_count)) or
                type(learner) is not LearnerSpec or learner != self.materialize_learner(slot_cap=slot_cap)):
            raise ContractError('literal G/Gamma/U/interface differs from the indexed family')
        program.validate(rules)


@dataclass(frozen=True)
class DecodeAllowance:
    join_cells: int = 4096
    live_cells: int = 32768
    arithmetic: int = 2_000_000
    integer_bits: int = frontier.BITS

    def __post_init__(self):
        for name in ('join_cells', 'live_cells', 'arithmetic', 'integer_bits'):
            natural(getattr(self, name), name, positive=True)
        if self.integer_bits > frontier.BITS:
            raise ContractError('requested integer allowance exceeds the fixed decoder implementation')


def partition_plan(state, query, order, budget):
    """Metadata-only simulation of the actual positive decoder table schedule."""
    # The extra eight bits also cover the fixed rational readout/gradient
    # multipliers, not just the positive partition's n+4*height bound.
    if state.n+4*sum(map(abs, state.counts))+8 > budget.integer_bits:
        raise ArithmeticUnresolved('partition integer envelope exceeds its declared allowance')
    support = tuple(edge for edge, d in zip(combinations(range(state.n), 2), state.counts) if d)
    return partition_shape_plan(state.n, support, query, order, budget)


def partition_shape_plan(n, support, query, order, budget):
    """Table geometry only; mantissa/exponent execution has its own bit guard."""
    counts.query(n, *query)
    if (type(support) is not tuple or any(type(e) is not tuple or len(e) != 2 for e in support)
            or tuple(sorted(set(support))) != support):
        raise ContractError('complete ordered distinct active edge support required')
    for i, j in support:
        counts.query(n, i, j)
        if i >= j:
            raise ContractError('active support uses canonical nonloop edges')
    if (type(order) is not tuple or any(type(v) is not int for v in order)
            or sorted(order) != list(range(n-1))):
        raise ContractError('complete declared elimination order required')
    scopes = []
    initial = 0
    for i, j in support:
        scope = tuple(v for v in (i, j) if v)
        initial += 1 << len(scope)
        allowance(initial, budget.live_cells, 'initial partition cell allowance')
        scopes.append(scope)
    kept = tuple(sorted({v for v in query if v}))
    multiply = add = 0
    peak_join, peak_live = 1, initial

    def check():
        allowance(peak_join, budget.join_cells, 'partition join-cell allowance')
        allowance(peak_live, budget.live_cells, 'partition live-cell allowance')
        allowance(multiply+add, budget.arithmetic, 'partition arithmetic allowance')

    for zero_based in order:
        v = zero_based+1
        if v in kept:
            continue
        bucket = [s for s in scopes if v in s]
        scope = tuple(sorted({v}.union(*(set(s) for s in bucket))))
        joined = 1 << len(scope)
        multiply += len(bucket)*joined
        add += joined//2
        peak_join = max(peak_join, joined)
        peak_live = max(peak_live, sum(1 << len(s) for s in scopes)+joined+joined//2)
        check()
        scopes = [s for s in scopes if v not in s]+[tuple(u for u in scope if u != v)]
    final = 1 << len(kept)
    multiply += len(scopes)*final
    add += final+1
    peak_join = max(peak_join, final)
    peak_live = max(peak_live, sum(1 << len(s) for s in scopes)+final)
    check()
    return {'positive_multiplications': multiply, 'positive_additions': add,
            'largest_join_cells': peak_join, 'peak_live_integer_cells': peak_live}


@dataclass(frozen=True)
class ReferenceView:
    schema: IndexedRelation
    state: counts.CountState
    query: tuple[int, int]
    source_values: tuple[F, ...]
    budget: DecodeAllowance
    order: tuple[int, ...]
    _partitions: dict = field(default_factory=dict, init=False, compare=False, repr=False)

    def __post_init__(self):
        if type(self.schema) is not IndexedRelation or type(self.state) is not counts.CountState:
            raise ContractError('exact indexed schema and complete count state required')
        if self.schema.n != self.state.n:
            raise ContractError('count state belongs to another indexed program')
        if type(self.query) is not tuple or len(self.query) != 2:
            raise ContractError('ordered categorical query required')
        counts.query(self.schema.n, *self.query)
        expected = tuple(F(v == self.query[side]) for side in (0, 1) for v in range(self.schema.n))
        if (type(self.source_values) is not tuple or any(type(v) not in (int, F) for v in self.source_values)
                or self.source_values != expected):
            raise ContractError('cache source values differ from its complete ordered query')
        if type(self.budget) is not DecodeAllowance:
            raise ContractError('explicit decoder allowance required')
        if (type(self.order) is not tuple or any(type(v) is not int for v in self.order)
                or sorted(self.order) != list(range(self.schema.n-1))):
            raise ContractError('complete declared elimination order required')

    @classmethod
    def bind(cls, schema, state, rules, source_values, *, budget=DecodeAllowance(), order=None):
        if type(schema) is not IndexedRelation:
            raise ContractError('exact indexed schema required')
        query, values = schema.source_query(rules, source_values)
        # No heuristic order search is hidden in a point read.
        order = tuple(range(schema.n-1)) if order is None else order
        return cls(schema, state, query, values, budget, order)

    def require_binding(self, schema, state, rules, source_values):
        if type(schema) is not IndexedRelation or type(state) is not counts.CountState:
            raise ContractError('exact indexed schema and complete count state required')
        query, values = schema.source_query(rules, source_values)
        if (schema != self.schema or state != self.state or query != self.query or values != self.source_values):
            raise ContractError('reference view belongs to another complete state or ordered query')

    @property
    def unit_count(self):
        return int(self.state.pending is not None)

    @property
    def cursor(self):
        return self.state.cursor

    @property
    def optimizer_steps(self):
        return self.state.steps

    @property
    def delayed(self):
        return ()

    @property
    def normalizer(self):
        return F(10)

    def partition(self, query):
        if type(query) is not tuple or len(query) != 2:
            raise ContractError('ordered categorical partition query required')
        counts.query(self.schema.n, *query)
        if query not in (self.query, self.state.pending[:2] if self.state.pending else self.query):
            raise ContractError('a view retains only its bound and pending-event query partitions')
        if query not in self._partitions:
            plan = partition_plan(self.state, query, self.order, self.budget)
            parts, stats = frontier.decode(self.schema.n, self.state.counts, query, order=self.order)
            assert all(stats[key] == value for key, value in plan.items())
            self._partitions[query] = (parts, stats)
        return self._partitions[query]

    def theta(self, slot):
        index(slot, self.schema.slot_count, 'reference parameter slot')
        if slot == 0:
            return F(1)
        parts, _ = self.partition(self.query)  # Guards precede the power below.
        world = slot-1
        exponent = sum(abs(d) for (i, j), d in zip(combinations(range(self.schema.n), 2), self.state.counts)
                       if d and (self.schema.world_bit(world, i) ^ self.schema.world_bit(world, j)) == int(d < 0))
        return F(9**exponent, sum(parts))

    def gradient(self, slot):
        index(slot, self.schema.slot_count, 'reference gradient slot')
        if self.state.pending is None:
            return F(0)
        i, j, y = self.state.pending
        parts, _ = self.partition((i, j))
        mass = 1+F(8*parts[y], sum(parts))
        if slot == 0:
            return 1/mass-F(1, 5)
        match = (self.schema.world_bit(slot-1, i) ^ self.schema.world_bit(slot-1, j)) == y
        return F(4, 5)-8*match/mass

    def value(self, node):
        index(node, self.schema.graph_counts()['nodes'], 'reference cache node')
        n, A = self.schema.n, self.schema.first_indicator
        if node < 2*n:
            return self.source_values[node]
        if node < A:
            return F(divmod(node-2*n, n) == self.query)
        if node < self.schema.heads[0]:
            world, y = divmod(node-A, 2)
            return F((self.schema.world_bit(world, self.query[0]) ^ self.schema.world_bit(world, self.query[1])) == y)
        parts, _ = self.partition(self.query)
        return F(8*parts[node-self.schema.heads[0]], sum(parts))

    def excess(self, label):
        index(label, 2, 'reference readout label')
        return self.value(self.schema.heads[label])

    def mass(self, label):
        return 1+self.excess(label)

    def probability(self, label):
        return self.mass(label)/self.normalizer

    def materialize_state(self, *, scalar_cap):
        allowance(2*self.schema.slot_count+3, scalar_cap, 'complete learner scalar allowance')
        return ReferenceLearnerState(tuple(self.theta(k) for k in range(self.schema.slot_count)), self.delayed,
                                     tuple(self.gradient(k) for k in range(self.schema.slot_count)),
                                     self.unit_count, self.cursor, self.optimizer_steps)

    def materialize_cache(self, *, scalar_cap):
        nodes = self.schema.graph_counts()['nodes']
        allowance(nodes+7, scalar_cap, 'complete cache scalar allowance')
        values = tuple(self.value(k) for k in range(nodes))
        excesses = tuple(self.excess(y) for y in (0, 1))
        masses = tuple(self.mass(y) for y in (0, 1))
        return Evaluation(values, excesses, masses, self.normalizer,
                          tuple(self.probability(y) for y in (0, 1)), self.delayed)


def bound_view(schema, state, query, **kwargs):
    counts.query(schema.n, *query)
    i, j = query
    return ReferenceView.bind(schema, state, schema.rules(), schema.source_row(i*schema.n+j), **kwargs)
