"""Literal finite-noise relation syntax and complete count coordinates.

Explicitly distinguishes unit-slot integer copies and rational feature slots.
Each description binds its complete native G/Gamma and the existing simplex U.
These passive declarations grant no Runtime, ledger or installation authority.
"""
from dataclasses import dataclass, fields, replace
from fractions import Fraction as F
from math import lcm

from .core import ContractError, natural, stable_hash
from .indexed_relation import MAX_N, NodeHeader, allowance, index
from .learner import SIMPLEX_GRADIENT, LearnerSpec
from .program import Product, Program, SemanticRules, Source, SourceSpec, Sum, Term, rational
from .semantics import ArithmeticUnresolved

SCHEMA = 'literal-anchored-finite-noise-relation-index-v1'
RATIONAL_SCHEMA = 'literal-anchored-rational-feature-noise-relation-index-v1'
COUNTER_CAP = (1 << 62)-1


def _same_native(actual, expected):
    """Closed typed comparison; Python equality alone admits False == 0."""
    if type(actual) is not type(expected):
        return False
    if type(expected) is tuple:
        return len(actual) == len(expected) and all(_same_native(a, b) for a, b in zip(actual, expected))
    if type(expected) in (Program, SemanticRules, SourceSpec, Source, Product, Sum, Term, LearnerSpec):
        keys = {f.name for f in fields(expected)}
        return set(vars(actual)) == set(vars(expected)) == keys and all(
            _same_native(vars(actual)[key], vars(expected)[key]) for key in keys)
    return type(expected) in (int, str, F, type(None)) and actual == expected


@dataclass(frozen=True)
class JointRelation:
    n: int
    rates: tuple[F, ...]
    prior: tuple[F, ...]
    # None preserves the original unit-slot/integer-incidence program. An
    # explicit rational scale selects the proved rational-feature G/Gamma.
    feature_scale: F | None = None

    def __post_init__(self):
        if set(vars(self)) != {'n', 'rates', 'prior', 'feature_scale'}:
            raise ContractError('unregistered joint native description coordinate')
        natural(self.n, 'joint native token count')
        if not 2 <= self.n <= MAX_N:
            raise ArithmeticUnresolved('joint native token count exceeds the indexed implementation class')
        if (type(self.rates) is not tuple or type(self.prior) is not tuple
                or not self.rates or len(self.rates) != len(self.prior)
                or any(type(v) is not F for v in self.rates+self.prior)
                or len(set(self.rates)) != len(self.rates)
                or any(not 0 < v < F(1, 2) for v in self.rates)
                or min(self.prior) <= 0 or sum(self.prior) != 1):
            raise ContractError('complete ordered distinct rational rate bank and positive prior required')
        if self.feature_scale is not None and (type(self.feature_scale) is not F
                or self.feature_scale*min(self.rates) < 1):
            raise ContractError('rational features require their explicit positive base-one native scale')
        if self.feature_scale is None and self.scale > 1 << 24:
            raise ArithmeticUnresolved('joint native coefficients exceed the exact binary32 integer class')

    @property
    def scale(self):
        return lcm(*(v.denominator for v in self.rates))

    @property
    def prior_scale(self):
        return lcm(*(v.denominator for v in self.prior))

    @property
    def native_scale(self):
        return F(self.scale) if self.feature_scale is None else self.feature_scale

    @property
    def fixed_slots(self):
        return 1 if self.feature_scale is None else 2*len(self.rates)

    @property
    def excess_denominator(self):
        return 1 if self.feature_scale is None else self.feature_scale.denominator*self.scale

    @property
    def partition_extra_bits(self):
        if self.feature_scale is None:
            return 0
        # Includes raw coefficient products and rational denominator metadata,
        # even when cancellation makes the final coefficient numerator small.
        return self.feature_scale.numerator.bit_length()+self.feature_scale.denominator.bit_length()

    @property
    def descriptor(self):
        original = SCHEMA, self.n, self.rates, self.prior
        return original if self.feature_scale is None else (RATIONAL_SCHEMA, self.n, self.rates, self.prior, self.feature_scale)

    @property
    def program_id(self):
        # Identity of the complete indexed declaration, not Program's fully
        # expanded syntax hash and not an equivalence or authority certificate.
        return stable_hash(('indexed-native-description-v1', self.descriptor))

    @property
    def worlds_per_rate(self):
        return 1 << (self.n-1)

    @property
    def K(self):
        return len(self.rates)*self.worlds_per_rate

    @property
    def slot_count(self):
        return self.K+self.fixed_slots

    @property
    def first_feature(self):
        return 2*self.n+self.n*self.n

    @property
    def heads(self):
        first = self.first_feature+2*self.K
        return first, first+1

    def counts(self):
        n, k = self.n, self.K
        sums = k*((self.scale-2)*n*n+2) if self.feature_scale is None else 2*k*(n*n+1)
        return {'nodes': self.first_feature+2*k+2, 'sources': 2*n,
                'state_reads': 0, 'SUMs': 2*k+2, 'PRODUCTs': n*n,
                'SUM_edges': sums, 'edges': sums+2*n*n, 'slots': self.slot_count, 'bindings': 0}

    def rules(self):
        sources = tuple(SourceSpec(f'x{side}:{v}', 'mass', 0, F(1))
                        for side in (0, 1) for v in range(self.n))
        return SemanticRules(sources, ('mass',), (('mass', 'mass', 'mass'),),
                             'mass', (F(1), F(1)))

    def validate(self, rules):
        self.__post_init__()
        if not _same_native(rules, self.rules()):
            raise ContractError('joint native source/type/base declaration differs')

    def query(self, query):
        if (type(query) is not tuple or len(query) != 2
                or any(type(v) is not int or not 0 <= v < self.n for v in query)):
            raise ContractError('complete ordered joint native source query required')

    def source_row(self, rank):
        index(rank, self.n*self.n, 'joint native categorical source row')
        return {f'x{side}:{v}': F(v == (rank//self.n, rank % self.n)[side])
                for side in (0, 1) for v in range(self.n)}

    def source_query(self, rules, sources):
        self.validate(rules)
        names = tuple(s.source_id for s in rules.sources)
        if len(sources) != 2*self.n or set(sources) != set(names):
            raise ContractError('complete joint categorical source interface required')
        values = tuple(rational(sources[name], 'joint source value') for name in names)
        query = []
        for side in (0, 1):
            row = values[side*self.n:(side+1)*self.n]
            if any(v not in (0, 1) for v in row) or sum(row) != 1:
                raise ContractError('one categorical token per side required')
            query.append(row.index(F(1)))
        return tuple(query), values

    def hypothesis(self, rank):
        index(rank, self.K, 'native joint hypothesis rank')
        return divmod(rank, self.worlds_per_rate)

    def world_bit(self, world, vertex):
        index(world, self.worlds_per_rate, 'anchored world index')
        index(vertex, self.n, 'world vertex')
        return 0 if vertex == 0 else (world >> (self.n-1-vertex)) & 1

    def coefficients(self, rate):
        index(rate, len(self.rates), 'native noise rate')
        if self.feature_scale is not None:
            return self.feature_scale*(1-self.rates[rate])-1, self.feature_scale*self.rates[rate]-1
        a = int(self.scale*self.rates[rate])
        return self.scale-a-1, a-1

    def coefficient_integers(self, rate):
        index(rate, len(self.rates), 'native noise rate')
        if self.feature_scale is None:
            return self.coefficients(rate)
        a, S = int(self.scale*self.rates[rate]), self.scale
        numerator, denominator = self.feature_scale.numerator, self.feature_scale.denominator
        return numerator*(S-a)-denominator*S, numerator*a-denominator*S

    def gamma(self, slot):
        index(slot, self.slot_count, 'joint native initializer slot')
        if slot < self.fixed_slots:
            return F(1) if self.feature_scale is None else self.coefficients(slot//2)[slot % 2]
        return self.prior[self.hypothesis(slot-self.fixed_slots)[0]]/self.worlds_per_rate

    def header(self, node):
        index(node, self.counts()['nodes'], 'joint native node')
        n = self.n
        if node < 2*n:
            return NodeHeader('SOURCE', source_id=f'x{node//n}:{node % n}')
        if node < self.first_feature:
            pair = node-2*n
            return NodeHeader('PRODUCT', parents=(pair//n, n+pair % n))
        if node >= self.heads[0]:
            return NodeHeader('SUM', arity=self.K)
        if self.feature_scale is not None:
            return NodeHeader('SUM', arity=n*n)
        hypothesis, target = divmod(node-self.first_feature, 2)
        rate, world = self.hypothesis(hypothesis)
        ones, zeros = world.bit_count(), n-world.bit_count()
        equal = zeros*zeros+ones*ones
        matching = equal if target == 0 else n*n-equal
        c, d = self.coefficients(rate)
        return NodeHeader('SUM', arity=c*matching+d*(n*n-matching))

    def term(self, node, rank):
        header = self.header(node)
        if header.kind != 'SUM':
            raise ContractError('joint native incidence read requires a SUM')
        index(rank, header.arity, 'ordered joint native SUM incidence')
        if node >= self.heads[0]:
            return Term(self.first_feature+2*rank+node-self.heads[0], rank+self.fixed_slots)
        hypothesis, target = divmod(node-self.first_feature, 2)
        rate, world = self.hypothesis(hypothesis)
        if self.feature_scale is not None:
            i, j = divmod(rank, self.n)
            mismatch = int(self.world_bit(world, i)^self.world_bit(world, j) != target)
            return Term(2*self.n+rank, 2*rate+mismatch)
        coefficients = self.coefficients(rate)
        for i in range(self.n):
            for j in range(self.n):
                copies = coefficients[int(self.world_bit(world, i)^self.world_bit(world, j) != target)]
                if rank < copies:
                    return Term(2*self.n+i*self.n+j, 0)
                rank -= copies
        raise AssertionError('joint native arity differs from its ordered incidence')

    def materialize_program(self, *, node_cap, term_cap, slot_cap):
        self.__post_init__()
        sizes = self.counts()
        for key, cap in (('nodes', node_cap), ('SUM_edges', term_cap), ('slots', slot_cap)):
            allowance(sizes[key], cap, 'literal joint Program '+key+' allowance')
        nodes = []
        for node in range(sizes['nodes']):
            header = self.header(node)
            nodes.append(Source(header.source_id) if header.kind == 'SOURCE' else
                         Product('mass', *header.parents) if header.kind == 'PRODUCT' else
                         Sum('mass', tuple(self.term(node, rank) for rank in range(header.arity))))
        return Program(tuple(nodes), self.slot_count, self.heads)

    def materialize_learner(self, *, slot_cap):
        self.__post_init__()
        allowance(self.slot_count, slot_cap, 'literal joint learner slot allowance')
        return LearnerSpec(1, F(1), optimizer_id=SIMPLEX_GRADIENT,
                           simplex_slots=tuple(range(self.fixed_slots, self.slot_count)))

    def compare_literal(self, program, rules, gamma, learner, *, node_cap, term_cap, slot_cap):
        expected = self.materialize_program(node_cap=node_cap, term_cap=term_cap, slot_cap=slot_cap)
        self.validate(rules)
        if (not _same_native(program, expected)
                or type(gamma) is not tuple or any(type(v) is not F for v in gamma)
                or gamma != tuple(self.gamma(k) for k in range(self.slot_count))
                or not _same_native(learner, self.materialize_learner(slot_cap=slot_cap))):
            raise ContractError('actual literal G/Gamma/U differs from the complete joint description')
        program.validate(rules)


@dataclass(frozen=True)
class JointCountState:
    model: JointRelation
    counts: tuple[int, ...]
    diagonal: int
    cursor: int
    steps: int
    pending: tuple[int, int, int] | None = None

    def __post_init__(self):
        if (set(vars(self)) != {'model', 'counts', 'diagonal', 'cursor', 'steps', 'pending'}
                or type(self.model) is not JointRelation):
            raise ContractError('complete closed joint native count encoding required')
        self.model.__post_init__()
        if (type(self.counts) is not tuple or len(self.counts) != self.n*(self.n-1)//2
                or any(type(v) is not int for v in self.counts)
                or any(type(v) is not int for v in (self.diagonal, self.cursor, self.steps))
                or min(self.cursor, self.steps) < 0):
            raise ContractError('complete exact joint counts, diagonal evidence and clocks required')
        height = sum(map(abs, self.counts))
        if height+abs(self.diagonal) > self.steps or (self.steps-height-self.diagonal) % 2:
            raise ContractError('joint counts violate the reachable event lattice')
        if max(self.cursor, self.steps) > COUNTER_CAP:
            raise ArithmeticUnresolved('joint count implementation counter envelope exhausted')
        if self.pending is not None:
            if (type(self.pending) is not tuple or len(self.pending) != 3 or not self.cursor
                    or type(self.pending[2]) is not int or self.pending[2] not in (0, 1)):
                raise ContractError('complete actual pending joint observation required')
            self.model.query(self.pending[:2])

    @property
    def n(self):
        return self.model.n


def require_state(state):
    if type(state) is not JointCountState:
        raise ContractError('complete immutable joint count predecessor required')
    state.__post_init__()


def initialize(model, cursor=0):
    if type(model) is not JointRelation:
        raise ContractError('declared joint native description required')
    model.__post_init__()
    return JointCountState(model, (0,)*(model.n*(model.n-1)//2), 0, cursor, 0)


def observe(state, query, target):
    require_state(state)
    state.model.query(query)
    if state.pending is not None or type(target) is not int or target not in (0, 1):
        raise ContractError('committed joint predecessor and actual binary target required')
    return replace(state, pending=(*query, target), cursor=state.cursor+1)


def commit(state):
    require_state(state)
    if state.pending is None:
        raise ContractError('joint count commit requires its actual observed unit')
    i, j, target = state.pending
    values, diagonal = list(state.counts), state.diagonal
    if i == j:
        diagonal += 1-2*target
    else:
        i, j = sorted((i, j))
        edge = i*(2*state.n-i-1)//2+j-i-1
        values[edge] += 1-2*target
    return replace(state, counts=tuple(values), diagonal=diagonal, steps=state.steps+1, pending=None)


def attach(state, cursor):
    require_state(state)
    if state.pending is not None:
        raise ContractError('joint profile attachment requires an empty unit')
    return replace(state, cursor=cursor)
