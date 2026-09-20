"""A paid fixed-prior affine proposal for the registered simplex learner.

Only ordinary native syntax is emitted. Runtime creates all parameter values
through its actual initializer and profile, then performs the real comparison.
"""
from dataclasses import dataclass, field
from fractions import Fraction as F
from itertools import product

from .core import ContractError
from .data_usage import DataContract
from .empirical_bound import EmpiricalUpper
from .learner import SIMPLEX_GRADIENT, LearnerSpec
from .native_search import GrammarLimits
from .pair_marginal_program import SOLVER as MARGINAL_SOLVER, marginal_counts, _emit_pair_marginals
from .profile import ProfileSpec
from .program import Product, Program, Source, Sum, Term
from .relation_proposal import RelationSourceSpec
from .semantics import _guard


SOLVER = 'native-binary-relation-simplex-posterior-v7'
SOLVERS = (SOLVER, MARGINAL_SOLVER)


@dataclass(frozen=True)
class SimplexRelationProposal:
    status: str
    program: Program | None
    worlds: int
    prior_per_world: F | None
    reason: str
    scope: str = field(default='one fixed-prior affine syntax proposal; actual profile/continuation is owned; no class or model-quality certificate', init=False)


def proposal_work_bound(n, domain_rows, grammar):
    # K is checked against grammar.slots before exponentiation or allocation.
    # The same conservative n^2*K envelope covers both literal emission and
    # the shared emitter's O(K+n^2) integer-indexed nodes/edges and layer scans.
    return 4096+128*(n*n*(grammar.slots+1)+n*domain_rows+grammar.slots+1)


def simplex_relation_proposal(upper, rules, grammar, pattern, registration, *,
                              data, learner, source_domain, profile, bit_limit):
    if (type(upper) is not EmpiricalUpper or type(grammar) is not GrammarLimits
            or type(registration) is not RelationSourceSpec or type(data) is not DataContract
            or type(learner) is not LearnerSpec):
        raise ContractError('the complete registered simplex proposal context is required')
    registration.__post_init__()
    K, prior = 0, None
    def outcome(program=None, reason=''):
        return SimplexRelationProposal('PROPOSED_NATIVE' if program is not None else 'UNRESOLVED',
            program, K, prior, reason)
    if registration.solver not in SOLVERS or learner.optimizer_id != SIMPLEX_GRADIENT:
        return outcome(reason='this emitter requires its registered simplex learner')
    if learner.update_unit != 1 or learner.learning_rate != 1 or learner.commit_grid_bits is not None:
        return outcome(reason='the posterior interpretation requires the declared unit event/update and no grid')
    if rules.states or rules.base != (F(1), F(1)) or type(profile) is not ProfileSpec:
        return outcome(reason='the affine model requires static base-one heads and an actual registered profile')
    n = len(registration.token_atoms)
    if n-1 >= grammar.slots.bit_length():
        return outcome(reason='the whole latent simplex exceeds the declared slot count')
    K = 1 << (n-1)
    counts = {'nodes': 2*n+n*n+2*K+2, 'SUMs': 2*K+2, 'PRODUCTs': n*n,
              'edges': 2*n*n+K*n*n+16*K, 'slots': K+1}
    if registration.solver == MARGINAL_SOLVER:
        counts = marginal_counts(n, K)
    if any(value > getattr(grammar, key) for key, value in counts.items()):
        return outcome(reason='the declared affine native graph exceeds its registered grammar')
    if learner.simplex_slots != tuple(range(1, K+1)):
        return outcome(reason='the actual learner block does not match the full latent simplex')
    prior = F(1, K)
    _guard(prior, bit_limit=bit_limit)
    theta = tuple(pattern[j % len(pattern)] for j in range(K+1))
    if theta != (F(1),)+(prior,)*K:
        return outcome(reason='the actual cyclic initializer does not supply the unit feature and fair prior')
    names = tuple(a for pair in registration.token_atoms for a in pair)
    specs = {s.source_id: s for s in rules.sources}
    reads = {s.source_id: s for s in data.source_reads}
    dtype = rules.readout_type
    if (set(specs) != set(names) or any(specs[a].type_id != dtype or specs[a].availability_delay != 0
            or specs[a].upper != 1 or a not in reads or reads[a].kind != 'input' or reads[a].lag != 0 for a in names)
            or dtype not in rules.sum_types or (dtype, dtype, dtype) not in rules.product_rules):
        return outcome(reason='the complete interface does not provide the two current categorical query roles')
    if not source_domain or len(source_domain) != n*n:
        return outcome(reason='the proposal requires the full ordered-pair source domain')
    indices = {s.source_id: i for i, s in enumerate(rules.sources)}
    seen = set()
    for row in source_domain:
        active = []
        for side in (0, 1):
            values = tuple(row[indices[pair[side]]] for pair in registration.token_atoms)
            if any(v not in (F(0), F(1)) for v in values) or sum(values) != 1:
                return outcome(reason='the full source domain is not categorical')
            active.append(values.index(F(1)))
        seen.add(tuple(active))
    if len(seen) != n*n:
        return outcome(reason='the source domain omits a legal ordered pair')
    if registration.solver == MARGINAL_SOLVER:
        graph = _emit_pair_marginals(rules, registration.token_atoms, K)
        graph.validate(rules)
        if not grammar.admits(graph) or any(graph.counts()[key] != value for key, value in counts.items()):
            raise ContractError('shared marginal emission disagrees with its prepaid native count')
        return outcome(graph, 'positive shared marginals; actual initializer, complete profile, comparison and evidence remain owned')
    nodes = [Source(s.source_id) for s in rules.sources]
    def emit(node):
        nodes.append(node)
        return len(nodes)-1
    pairs = {(i, j): emit(Product(dtype, indices[registration.token_atoms[i][0]],
                                           indices[registration.token_atoms[j][1]]))
             for i, j in product(range(n), repeat=2)}
    terms = [[], []]
    for slot, tail in enumerate(product((0, 1), repeat=n-1), 1):
        z = (0,)+tail
        for y in (0, 1):
            selected = emit(Sum(dtype, tuple(Term(pairs[i, j], 0) for i, j in pairs if z[i]^z[j] == y)))
            terms[y].extend([Term(selected, slot)]*8)
    heads = tuple(emit(Sum(dtype, tuple(t))) for t in terms)
    graph = Program(tuple(nodes), K+1, heads)
    graph.validate(rules)
    if not grammar.admits(graph) or any(graph.counts()[key] != value for key, value in counts.items()):
        raise ContractError('simplex syntax emission disagrees with its prepaid literal count')
    return outcome(graph, 'fixed-prior affine syntax; initializer, profile, comparison and fresh evidence remain owned')
