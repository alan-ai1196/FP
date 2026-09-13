"""An empirical binary-relation solver that emits ordinary native syntax.

The registration aligns observable token atoms at two positions. It supplies
no hidden partition, relation labels, fitted values or running solver state.
A consistent empirical majority system is only a proposal heuristic; its
unknown-population interpretation and unobserved relative component flips
are never certified here. A separate all-program upper must close search.
"""
from dataclasses import dataclass, field
from fractions import Fraction as F

from .core import ContractError
from .empirical_bound import EmpiricalUpper
from .native_search import GrammarLimits
from .numerics import compare_exact
from .program import Program, Source, Sum, Product, Term, name
from .semantics import _guard, _operation


@dataclass(frozen=True)
class RelationSourceSpec:
    token_atoms: tuple[tuple[str, str], ...]
    solver: str = field(default='empirical-binary-relation-initializer-selection-v2', init=False)

    def __post_init__(self):
        atoms = tuple(tuple(pair) for pair in self.token_atoms)
        if len(atoms) < 2 or any(len(pair) != 2 for pair in atoms):
            raise ContractError('two aligned observable token positions are required')
        flat = tuple(name(atom, 'observable token source') for pair in atoms for atom in pair)
        if len(set(flat)) != len(flat):
            raise ContractError('distinct token atoms at both observable positions are required')
        if self.solver != 'empirical-binary-relation-initializer-selection-v2':
            raise ContractError('unregistered empirical relation solver')
        object.__setattr__(self, 'token_atoms', atoms)


@dataclass(frozen=True)
class RelationProposal:
    status: str
    empirical_edges: tuple[tuple[int, int, int, int], ...]
    components: tuple[tuple[int, ...], ...]
    assignment: tuple[int, ...]
    scale: F | None
    program: Program | None
    reason: str
    scope: str = field(default='one proposal from empirical majority constraints; no latent-partition, population or unseen-relation certificate', init=False)


def relation_proposal(upper, rules, grammar, pattern, registration, *, bit_limit):
    if type(upper) is not EmpiricalUpper or type(registration) is not RelationSourceSpec or type(grammar) is not GrammarLimits:
        raise ContractError('registered relation sources and verified empirical data required')
    registration.__post_init__()
    atoms, edges, components, assignment = registration.token_atoms, {}, [], []
    scale = None

    def result(program=None, reason=''):
        return RelationProposal('PROPOSED_NATIVE' if program is not None else 'UNRESOLVED',
            tuple((i, j, counts[0], counts[1]) for (i, j), counts in sorted(edges.items())),
            tuple(components), tuple(assignment), scale, program, reason)

    if len(rules.base) != 2 or rules.base != (F(1), F(1)) or rules.states:
        return result(reason='this proposal solver uses the registered static binary base-one interface')
    specs = {source.source_id: source for source in rules.sources}
    if any(atom not in specs or specs[atom].type_id != rules.readout_type for pair in atoms for atom in pair):
        raise ContractError('relation atom is absent or has a different native type')
    dtype = rules.readout_type
    if dtype not in rules.sum_types or (dtype, dtype, dtype) not in rules.product_rules:
        return result(reason='the registered native type lacks this legal SUM/PRODUCT construction')
    for cell in upper.cells:
        source = dict(cell.sources)
        active = []
        for position in (0, 1):
            values = tuple(source[pair[position]] for pair in atoms)
            if any(value not in (F(0), F(1)) for value in values) or sum(values) != 1:
                return result(reason='observed inputs do not form the registered token partitions')
            active.append(values.index(F(1)))
        edge = tuple(sorted(active))
        counts = edges.setdefault(edge, [0, 0])
        for label in (0, 1):
            counts[label] += cell.counts[label]
    adjacency = [[] for _ in atoms]
    majority = minority = 0
    for (i, j), counts in sorted(edges.items()):
        if counts[0] == counts[1]:
            return result(reason='an empirical relation is tied; no signed constraint is selected')
        relation = int(counts[1] > counts[0])
        adjacency[i].append((j, relation))
        adjacency[j].append((i, relation))
        majority += max(counts)
        minority += min(counts)
    assignment = [-1]*len(atoms)
    for root in range(len(atoms)):
        if assignment[root] != -1:
            continue
        assignment[root], queue = 0, [root]
        for i in queue:
            for j, relation in adjacency[i]:
                expected = assignment[i] ^ relation
                if assignment[j] == -1:
                    assignment[j] = expected
                    queue.append(j)
                elif assignment[j] != expected:
                    return result(reason='the empirical majority constraints are inconsistent; other native programs remain unsearched')
        components.append(tuple(queue))
    # Optimize only values this constructor can actually initialize. No free
    # empirical fit needs to exist, be finite, or equal an initializer value.
    # Counts/proposal remain retained heuristic provenance, not class authority.
    available = pattern[:grammar.slots]
    if F(1) not in available:
        return result(reason='the native grouping requires an available initialized unit slot')
    best = None
    for value in available:
        numerator = _operation(value, F(1), multiply=False, bit_limit=bit_limit)
        denominator = _operation(value, F(2), multiply=False, bit_limit=bit_limit)
        inverse = F(denominator.denominator, denominator.numerator)
        _guard(inverse, bit_limit=bit_limit)
        probability = _operation(numerator, inverse, multiply=True, bit_limit=bit_limit)
        score = F(1)
        for count, factor in ((majority, probability), (minority, inverse)):
            for _ in range(count):
                score = _operation(score, factor, multiply=True, bit_limit=bit_limit)
        if best is None or compare_exact(score, best, bit_limit=bit_limit) > 0:
            scale, best = value, score
    unit_slot, scale_slot = pattern.index(F(1)), pattern.index(scale)
    slots = max(unit_slot, scale_slot)+1
    n = len(atoms)
    if any(needed > getattr(grammar, key) for key, needed in {
            'nodes': 2*n+10, 'SUMs': 6, 'PRODUCTs': 4, 'edges': 2*n+12, 'slots': slots}.items()):
        return result(reason='this native witness exceeds declared construction bounds; not an exclusion of the class')
    nodes = [Source(pair[position]) for position in (0, 1) for pair in atoms]
    groups = []
    for position in (0, 1):
        for group in (0, 1):
            groups.append(len(nodes))
            nodes.append(Sum(dtype, tuple(Term(position*n+i, unit_slot) for i, value in enumerate(assignment) if value == group)))
    cells = []
    for left in (0, 1):
        for right in (0, 1):
            cells.append(len(nodes))
            nodes.append(Product(dtype, groups[left], groups[2+right]))
    heads = []
    for label in (0, 1):
        heads.append(len(nodes))
        nodes.append(Sum(dtype, tuple(Term(cells[2*a+b], scale_slot) for a in (0, 1) for b in (0, 1) if a ^ b == label)))
    program = Program(tuple(nodes), slots, tuple(heads))
    program.validate(rules)
    if not grammar.admits(program):
        raise ContractError('constructed relation syntax differs from its prepaid grammar extent')
    return result(program, 'native witness from empirical constraints; each disconnected component chose its own arbitrary root flip')
