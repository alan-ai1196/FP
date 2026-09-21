"""Indexed literal code and complete exact reference coordinates.

This passive representation has no Runtime, source-acquisition, ownership,
phase-evidence, initialization or installation authority. It indexes the
existing finite relation Program; it does not introduce a native constructor.
"""
from dataclasses import dataclass, field, replace
from fractions import Fraction as F
from itertools import combinations, permutations, product
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(Path(__file__).resolve().parent)]
import count_learner_encoding as counts
import positive_frontier_decoder as frontier
import simplex_gradient as native
from fp_reference.core import ContractError, natural
from fp_reference.learner import (SIMPLEX_GRADIENT, LearnerSpec, ReferenceLearnerState,
                                  initial_state, observe_event, commit_event)
from fp_reference.profile import attach_boundary
from fp_reference.program import (Product, Program, SemanticRules, Source, SourceSpec,
                                  DelayedStateSpec, Sum, Term, rational)
from fp_reference.semantics import ArithmeticUnresolved, Evaluation, evaluate

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
        return native.context(self.n, rank//self.n, rank % self.n)

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
    counts.query(state.n, *query)
    # The extra eight bits also cover the fixed rational readout/gradient
    # multipliers, not just the positive partition's n+4*height bound.
    if state.n+4*sum(map(abs, state.counts))+8 > budget.integer_bits:
        raise ArithmeticUnresolved('partition integer envelope exceeds its declared allowance')
    if (type(order) is not tuple or any(type(v) is not int for v in order)
            or sorted(order) != list(range(state.n-1))):
        raise ContractError('complete declared elimination order required')
    scopes = []
    initial = 0
    for (i, j), d in zip(combinations(range(state.n), 2), state.counts):
        if d:
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


def code_audit():
    rows = []
    limits = dict(node_cap=100_000, term_cap=2_000_000, slot_cap=65536)
    for n in range(2, 9):
        schema = IndexedRelation(n)
        rules, graph, worlds = native.relation_graph(n)
        gamma = (F(1),)+(F(1, len(worlds)),)*len(worlds)
        learner = LearnerSpec(1, F(1), optimizer_id=SIMPLEX_GRADIENT,
                              simplex_slots=tuple(range(1, len(worlds)+1)))
        schema.compare_literal(graph, rules, gamma, learner, **limits)
        assert schema.graph_counts() == graph.counts()
        assert all(tuple(schema.world_bit(k, v) for v in range(n)) == z for k, z in enumerate(worlds))
        terms = 0
        for k, node in enumerate(graph.nodes):
            h = schema.header(k)
            if type(node) is Sum:
                assert h == NodeHeader('SUM', arity=len(node.terms))
                for rank, term in enumerate(node.terms):
                    assert schema.term(k, rank) == term
                    terms += 1
            elif type(node) is Source:
                assert h == NodeHeader('SOURCE', source_id=node.source_id)
            else:
                assert h == NodeHeader('PRODUCT', parents=(node.left, node.right))
        for rank in range(n*n):
            assert schema.source_query(rules, schema.source_row(rank))[0] == divmod(rank, n)
        rows.append({'n': n, 'nodes': len(graph.nodes), 'ordered_SUM_terms': terms, 'slots': graph.slot_count})
    return rows


def phase_audit():
    totals = dict(boundary_states=0, native_caches=0, observed_states=0, committed_states=0)
    rows = []
    for n, depth in ((2, 3), (3, 2)):
        schema = IndexedRelation(n)
        rules, graph, _ = native.relation_graph(n)
        learner = schema.materialize_learner(slot_cap=64)
        gamma = tuple(schema.gamma(k) for k in range(schema.slot_count))
        initial = initial_state(graph, rules, gamma, 0, spec=learner, bit_limit=32768)
        alphabet = tuple(product(range(n), range(n), (0, 1)))
        level = [(initial, counts.initialize(n))]
        boundaries = transitions = 0
        for cut in range(depth+1):
            following = []
            for reference, encoded in level:
                assert bound_view(schema, encoded, (0, 0)).materialize_state(scalar_cap=100) == reference
                boundaries += 1
                totals['boundary_states'] += 1
                caches = {}
                for query in product(range(n), repeat=2):
                    actual = evaluate(graph, rules, reference.theta, native.context(n, *query), (), bit_limit=32768)
                    assert bound_view(schema, encoded, query).materialize_cache(scalar_cap=1000) == actual
                    caches[query] = actual
                    totals['native_caches'] += 1
                if cut == depth:
                    continue
                for i, j, y in alphabet:
                    observed = observe_event(graph, reference, learner, caches[i, j], y, bit_limit=32768)
                    pending = counts.observe(encoded, i, j, y)
                    # Deliberately bind another query: gradient belongs to the pending event.
                    assert bound_view(schema, pending, (j, 0)).materialize_state(scalar_cap=100) == observed
                    committed = commit_event(observed, learner, bit_limit=32768)
                    successor = counts.commit(pending)
                    assert bound_view(schema, successor, (i, j)).materialize_state(scalar_cap=100) == committed
                    following.append((committed, successor))
                    totals['observed_states'] += 1
                    totals['committed_states'] += 1
                    transitions += 1
            level = following
        rows.append({'n': n, 'depth': depth, 'boundary_histories': boundaries, 'transitions': transitions})
    return {'cases': rows, 'checks': totals}


def profile_audit():
    schema = IndexedRelation(3)
    rules, graph, _ = native.relation_graph(3)
    learner = schema.materialize_learner(slot_cap=64)
    checked = 0
    for passes in (1, 2, 3):
        reference, state = counts.native_initial(3), counts.initialize(3)
        for event in ((0, 1, 0), (1, 2, 1), (0, 2, 0))*passes:
            prediction = evaluate(graph, rules, reference.theta, native.context(3, *event[:2]), (), bit_limit=32768)
            reference = observe_event(graph, reference, learner, prediction, event[2], bit_limit=32768)
            state = counts.observe(state, *event)
            assert bound_view(schema, state, (2, 1)).materialize_state(scalar_cap=100) == reference
            reference = commit_event(reference, learner, bit_limit=32768)
            state = counts.commit(state)
            assert bound_view(schema, state, (2, 1)).materialize_state(scalar_cap=100) == reference
            checked += 2
        reference = attach_boundary(reference, 20, learner)
        state = counts.attach(state, 20)
        assert bound_view(schema, state, (1, 2)).materialize_state(scalar_cap=100) == reference
        checked += 1
    return {'profiles': 3, 'complete_state_comparisons': checked}


def schedule_audit():
    """All n4 active graphs, all free-variable orders and all ordered queries."""
    n = 4
    edges = tuple(combinations(range(n), 2))
    queries = tuple(product(range(n), repeat=2))
    checked = 0
    peak = dict(largest_join_cells=0, peak_live_integer_cells=0, positive_arithmetic=0)
    for mask in range(1 << len(edges)):
        signed = tuple((1 if e % 2 else -1) if mask >> e & 1 else 0 for e in range(len(edges)))
        state = counts.CountState(n, signed, None, mask.bit_count(), mask.bit_count())
        exact = frontier.enumeration(n, signed, queries)
        for order in permutations(range(n-1)):
            for query, expected in zip(queries, exact):
                plan = partition_plan(state, query, order, DecodeAllowance())
                parts, actual = frontier.decode(n, signed, query, order=order)
                assert parts == expected
                assert all(actual[key] == value for key, value in plan.items())
                for key in ('largest_join_cells', 'peak_live_integer_cells'):
                    peak[key] = max(peak[key], plan[key])
                peak['positive_arithmetic'] = max(peak['positive_arithmetic'],
                    plan['positive_multiplications']+plan['positive_additions'])
                checked += 1
    return {'active_graphs': 64, 'orders_per_graph': 6, 'ordered_queries_per_order': 16,
            'complete_plan_and_partition_comparisons': checked, 'maximum_logical_work': peak}


def refusal(function, exception=ContractError):
    try:
        function()
    except exception:
        return 1
    raise AssertionError('unsupported binding or unfunded read was accepted')


def boundary_audit():
    schema = IndexedRelation(3)
    rules, graph, _ = native.relation_graph(3)
    gamma = tuple(schema.gamma(k) for k in range(schema.slot_count))
    learner = schema.materialize_learner(slot_cap=64)
    limits = dict(node_cap=1000, term_cap=1000, slot_cap=64)
    swapped = list(graph.nodes)
    last = swapped[graph.heads[0]]
    swapped[graph.heads[0]] = Sum('mass', last.terms[::-1])
    retied = list(graph.nodes)
    retied[graph.heads[0]] = Sum('mass', (replace(last.terms[0], slot=2),)+last.terms[1:])
    mismatches = [
        (replace(graph, heads=graph.heads[::-1]), rules, gamma, learner),
        (replace(graph, nodes=tuple(swapped)), rules, gamma, learner),
        (replace(graph, nodes=tuple(retied)), rules, gamma, learner),
        (graph, replace(rules, base=(F(2), F(1))), gamma, learner),
        (graph, replace(rules, sources=rules.sources[::-1]), gamma, learner),
        (graph, replace(rules, sources=(replace(rules.sources[0], source_id='renamed'),)+rules.sources[1:]), gamma, learner),
        (graph, replace(rules, sources=(replace(rules.sources[0], availability_delay=1),)+rules.sources[1:]), gamma, learner),
        (graph, replace(rules, sources=(replace(rules.sources[0], upper=F(2)),)+rules.sources[1:]), gamma, learner),
        (graph, replace(rules, states=(DelayedStateSpec('extra', 'mass', 1, F(1)),)), gamma, learner),
        (graph, rules, (F(1), F(1, 2), F(1, 6), F(1, 6), F(1, 6)), learner),
        (graph, rules, gamma, replace(learner, learning_rate=F(1, 2))),
        (graph, rules, gamma, replace(learner, update_unit=2)),
        (graph, rules, gamma, replace(learner, simplex_slots=(1, 2, 3))),
        (graph, rules, tuple(float(v) for v in gamma), learner),
    ]
    binding = sum(refusal(lambda args=args: schema.compare_literal(*args, **limits)) for args in mismatches)
    soft = native.context(3, 0, 1)
    soft['x0:0'], soft['x0:1'] = F(1, 2), F(1, 2)
    state = counts.initialize(3)
    view = bound_view(schema, state, (0, 1))
    source = schema.source_row(1)
    invalid_sources = [soft, {**source, 'extra': F(0)}, {k: v for k, v in source.items() if k != 'x1:2'},
                       {**source, 'x0:0': 1.0}, {**source, 'x0:1': F(1)}]
    sources = sum(refusal(lambda values=values: ReferenceView.bind(schema, state, rules, values))
                  for values in invalid_sources)
    stale = sum(refusal(lambda other=other: view.require_binding(schema, other, rules, source)) for other in (
        replace(state, cursor=1), replace(state, steps=1), counts.observe(state, 0, 0, 0)))
    stale += refusal(lambda: view.require_binding(schema, state, rules, schema.source_row(3)))
    assert view.state == state and not view._partitions
    original = frontier.decode
    def forbidden(*args, **kwargs):
        raise AssertionError('a rejected preflight entered the numerical table decoder')
    frontier.decode = forbidden
    try:
        n = 16
        dense = counts.CountState(n, (1,)*(n*(n-1)//2), None, n*(n-1)//2, n*(n-1)//2)
        large = IndexedRelation(n)
        guarded = bound_view(large, dense, (0, 1), budget=DecodeAllowance(join_cells=1024))
        guards = refusal(lambda: guarded.theta(1), ArithmeticUnresolved)
        assert not guarded._partitions
        small = IndexedRelation(2)
        tall = counts.CountState(2, (10**12,), None, 10**12, 10**12)
        guarded = bound_view(small, tall, (0, 1))
        guards += refusal(lambda: guarded.theta(1), ArithmeticUnresolved)
        assert not guarded._partitions
        for budget in (DecodeAllowance(live_cells=1), DecodeAllowance(arithmetic=1), DecodeAllowance(integer_bits=5)):
            guarded = bound_view(schema, counts.commit(counts.observe(state, 0, 1, 0)), (0, 1), budget=budget)
            guards += refusal(lambda: guarded.theta(1), ArithmeticUnresolved)
            assert not guarded._partitions
    finally:
        frontier.decode = original
    cached = bound_view(schema, state, (0, 1))
    cached.partition((0, 1))
    indices = sum(refusal(function) for function in (
        lambda: bound_view(schema, state, (0, 3)),
        lambda: schema.world_bit(True, 0), lambda: schema.world_bit(schema.K, 0),
        lambda: schema.header(schema.graph_counts()['nodes']),
        lambda: schema.term(0, 0), lambda: schema.term(schema.first_indicator+1, 0),
        lambda: schema.term(schema.heads[0], 8*schema.K),
        lambda: schema.selected_slot(schema.K), lambda: view.theta(schema.slot_count),
        lambda: cached.partition((False, 1)),
        lambda: ReferenceView.bind(schema, state, rules, source, order=(0, 0)),
        lambda: IndexedRelation(MAX_N+1)))
    return {'literal_binding_refusals': binding, 'complete_source_refusals': sources,
            'stale_clock_pending_or_orientation_refusals': stale, 'preallocation_partition_refusals': guards,
            'invalid_index_order_or_prototype_refusals': indices}


def large_index_audit():
    n = 256
    schema = IndexedRelation(n)
    K = schema.K
    initial = counts.CountState(n, (0,)*(n*(n-1)//2), None, 0, 0)
    state = counts.commit(counts.observe(initial, 0, 1, 0))
    view = bound_view(schema, state, (0, 1))
    parts, stats = view.partition((0, 1))
    assert parts == (9*(K//2), K//2)
    slots = (1, 2, K//2, K//2+1, K)
    for slot in slots:
        expected = F(9 if schema.world_bit(slot-1, 1) == 0 else 1, 5*K)
        assert view.theta(slot) == expected
    assert view.value(schema.heads[0]) == F(36, 5)
    assert view.value(schema.heads[1]) == F(4, 5)
    assert view.probability(0) == F(41, 50) and view.probability(1) == F(9, 50)
    assert view.mass(0) == F(41, 5) and view.normalizer == 10 and view.delayed == ()
    # A diagonal has a nonzero full gradient even though committed d is unchanged.
    diagonal = counts.observe(state, 0, 0, 0)
    pending = bound_view(schema, diagonal, (1, 0))
    assert all(pending.gradient(slot) == F(-4, 45) for slot in (0,)+slots)
    assert (pending.unit_count, pending.cursor, pending.optimizer_steps) == (1, 2, 1)
    after = counts.commit(diagonal)
    assert after.counts == state.counts and after.steps == 2 and after.cursor == 2
    relative = counts.commit(counts.observe(after, 1, 2, 0))
    attached = counts.attach(relative, 20)
    final = bound_view(schema, attached, (1, 2))
    assert final.value(schema.heads[0]) == F(36, 5)
    assert (final.unit_count, final.cursor, final.optimizer_steps) == (0, 20, 3)
    for slot in slots:
        world = slot-1
        a, b = schema.world_bit(world, 1), schema.world_bit(world, 2)
        assert final.theta(slot) == F((9 if a == 0 else 1)*(9 if a == b else 1), 25*K)
    # Native orientation is retained in all source and pair cache coordinates.
    reverse = bound_view(schema, state, (1, 0))
    assert view.value(0) == 1 and reverse.value(0) == 0
    assert view.value(2*n+1) == 1 and reverse.value(2*n+1) == 0
    checks = 0
    for world in (0, 1, K//2, K-1):
        z = tuple(schema.world_bit(world, v) for v in range(n))
        for y in (0, 1):
            node = schema.first_indicator+2*world+y
            header = schema.header(node)
            expected = tuple((i, j) for i in range(n) for j in range(n) if z[i] ^ z[j] == y)
            assert header.arity == len(expected)
            for rank in sorted({0, header.arity//2, header.arity-1}) if header.arity else ():
                i, j = expected[rank]
                assert schema.term(node, rank) == Term(2*n+i*n+j, 0)
                checks += 1
        for y in (0, 1):
            for repetition in (0, 7):
                assert schema.term(schema.heads[y], 8*world+repetition) == Term(schema.first_indicator+2*world+y, world+1)
                checks += 1
    unopened = bound_view(schema, initial, (0, 1))
    refusals = sum(refusal(function, ArithmeticUnresolved) for function in (
        lambda: schema.materialize_program(node_cap=100_000, term_cap=2_000_000, slot_cap=65536),
        lambda: schema.materialize_node(schema.heads[0], term_cap=2_000_000),
        lambda: schema.materialize_learner(slot_cap=65536),
        lambda: unopened.materialize_state(scalar_cap=100_000),
        lambda: unopened.materialize_cache(scalar_cap=100_000)))
    assert unopened.state == initial and not unopened._partitions
    return {'n': n, 'logical_worlds_power_of_two': n-1, 'signed_count_coordinates': len(state.counts),
            'logical_nodes': '2^256 + 66050', 'logical_SUM_terms': '65552 * 2^255',
            'native_index_witnesses': checks, 'sampled_parameter_slots_per_state': len(slots),
            'actual_count_reference_commits': 3, 'profile_attachment_cursor': attached.cursor,
            'anchor_probability': str(view.probability(0)),
            'anchor_partition_integer_bits': max(v.bit_length() for v in (*parts, sum(parts))),
            'anchor_partition_work': stats, 'explicit_full_read_refusals': refusals,
            'scope': 'exact symbolic/reference execution; no large native Program or K-entry state is materialized'}


def audit():
    code = code_audit()
    phases = phase_audit()
    profiles = profile_audit()
    schedules = schedule_audit()
    boundaries = boundary_audit()
    # Keep the independent native builder unavailable during the large example.
    original = native.relation_graph
    def forbidden(_):
        raise AssertionError('large indexed execution tried to materialize a native world graph')
    native.relation_graph = forbidden
    try:
        large = large_index_audit()
    finally:
        native.relation_graph = original
    assert 'torch' not in sys.modules
    return {'schema': SCHEMA, 'exact_literal_code': code, 'native_phase_audit': phases,
            'profile_audit': profiles, 'schedule_audit': schedules,
            'boundary_audit': boundaries, 'large_index_audit': large,
            'scope': 'exact indexed G/Gamma/U and reference coordinates; no Runtime admission, AMP bridge, physical resource or completeness certificate'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = audit()
    encoded = json.dumps(report, indent=2)+'\n'
    if args.output:
        args.output.write_text(encoded, encoding='utf-8')
    print(encoded)
