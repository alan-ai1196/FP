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
    solver: str = 'empirical-binary-relation-component-symmetry-v3'

    def __post_init__(self):
        atoms = tuple(tuple(pair) for pair in self.token_atoms)
        if len(atoms) < 2 or any(len(pair) != 2 for pair in atoms):
            raise ContractError('two aligned observable token positions are required')
        flat = tuple(name(atom, 'observable token source') for pair in atoms for atom in pair)
        if len(set(flat)) != len(flat):
            raise ContractError('distinct token atoms at both observable positions are required')
        if self.solver not in ('empirical-binary-relation-component-symmetry-v3',
                               'empirical-binary-relation-balanced-readout-v4'):
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
    for (i, j), counts in sorted(edges.items()):
        if counts[0] == counts[1]:
            continue  # Keep the counts; they impose no preferred parity.
        relation = int(counts[1] > counts[0])
        adjacency[i].append((j, relation))
        adjacency[j].append((i, relation))
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
    component_of = [0]*len(atoms)
    for component, vertices in enumerate(components):
        for i in vertices:
            component_of[i] = component
    majority = minority = 0
    for (i, j), counts in edges.items():
        if component_of[i] == component_of[j]:
            preferred = assignment[i] ^ assignment[j]
            majority += counts[preferred]
            minority += counts[1-preferred]
        # Across components the emitted endpoint is uniform for every scale.
        # Its constant likelihood factor need not enter the scale argmax.
    # Optimize only values this constructor can actually initialize. No free
    # empirical fit needs to exist, be finite, or equal an initializer value.
    # Counts/proposal remain retained heuristic provenance, not class authority.
    available = pattern[:grammar.slots]
    if not available:
        return result(reason='no initialized readout value is available in this slot budget')
    if registration.solver == 'empirical-binary-relation-component-symmetry-v3' and F(1) not in available:
        return result(reason='the native grouping requires an available initialized unit slot')
    eligible = available
    if registration.solver == 'empirical-binary-relation-balanced-readout-v4':
        needed_units = len(components)*(len(components)-1)
        unit_count = sum(value == 1 for value in available)
        eligible = tuple(value for value in available if unit_count-int(value == 1) >= needed_units)
        if not eligible:
            return result(reason='independent balanced coefficients are absent from the available initializer prefix')
    best = None
    for value in eligible:
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
    scale_slot = pattern.index(scale)
    if registration.solver == 'empirical-binary-relation-balanced-readout-v4':
        # A separately registered search algorithm over the same native
        # grammar. Its balanced readout coefficients retain parameter
        # directions on queries where v3 has structurally zero evidence.
        n, c = len(atoms), len(components)
        units = [i for i, value in enumerate(available) if value == 1 and i != scale_slot]
        required = c*(c-1)
        if len(units) < required:
            return result(reason='independent balanced coefficients are absent from the available initializer prefix')
        pair_slots, at = {}, 0
        for left in range(c):
            for right in range(left+1, c):
                pair_slots[left, right] = tuple(units[at:at+2])
                at += 2
        slots = max([scale_slot]+units[:required])+1
        within = sum(len(vertices)**2 for vertices in components)
        needed = {'nodes': 2*n+n*n+2, 'SUMs': 2, 'PRODUCTs': n*n,
                  'edges': 4*n*n-within, 'slots': slots}
        if any(value > getattr(grammar, key) for key, value in needed.items()):
            return result(reason='the balanced native witness exceeds declared construction bounds; not an exclusion of the class')
        nodes = [Source(pair[position]) for position in (0, 1) for pair in atoms]
        terms = [[], []]
        for i in range(n):
            for j in range(n):
                feature = len(nodes)
                nodes.append(Product(dtype, i, n+j))
                parity = assignment[i] ^ assignment[j]
                if component_of[i] == component_of[j]:
                    terms[parity].append(Term(feature, scale_slot))
                else:
                    pair = tuple(sorted((component_of[i], component_of[j])))
                    for label in (0, 1):
                        terms[label].append(Term(feature, pair_slots[pair][label ^ parity]))
        heads = []
        for row in terms:
            heads.append(len(nodes))
            nodes.append(Sum(dtype, tuple(row)))
        program = Program(tuple(nodes), slots, tuple(heads))
        program.validate(rules)
        if not grammar.admits(program):
            raise ContractError('balanced relation syntax differs from its prepaid grammar extent')
        return result(program, 'native balanced readouts preserve initialized uncertainty and distinct learnable component-pair coefficients')
    unit_slot = pattern.index(F(1))
    slots = max(unit_slot, scale_slot)+1
    n, c = len(atoms), len(components)
    if any(needed > getattr(grammar, key) for key, needed in {
            'nodes': 2*n+8*c+2, 'SUMs': 4*c+2, 'PRODUCTs': 4*c,
            'edges': 2*n+12*c, 'slots': slots}.items()):
        return result(reason='this native witness exceeds declared construction bounds; not an exclusion of the class')
    nodes = [Source(pair[position]) for position in (0, 1) for pair in atoms]
    cells = [[], []]
    for component in components:
        vertices, groups = sorted(component), []
        for position in (0, 1):
            for group in (0, 1):
                groups.append(len(nodes))
                nodes.append(Sum(dtype, tuple(Term(position*n+i, unit_slot)
                    for i in vertices if assignment[i] == group)))
        for left in (0, 1):
            for right in (0, 1):
                cells[left ^ right].append(len(nodes))
                nodes.append(Product(dtype, groups[left], groups[2+right]))
    heads = []
    for label in (0, 1):
        heads.append(len(nodes))
        nodes.append(Sum(dtype, tuple(Term(cell, scale_slot) for cell in cells[label])))
    program = Program(tuple(nodes), slots, tuple(heads))
    program.validate(rules)
    if not grammar.admits(program):
        raise ContractError('constructed relation syntax differs from its prepaid grammar extent')
    return result(program, 'native component-invariant endpoint; unobserved relative flips remain uniform on the one-hot domain')
