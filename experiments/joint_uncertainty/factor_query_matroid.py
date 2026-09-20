"""Exact factor-closure audits under arbitrary latent-world re-encodings.

Passive proof evidence only. No production solver, state quotient or AMP
authority; current model tapes are read only for declared structural diagnostics.
"""
from collections import Counter
from dataclasses import replace
from fractions import Fraction as F
from itertools import combinations, permutations, product
from pathlib import Path
import argparse
import json
import math

import factor_simplex_posterior as native
from fp_reference.program import Program, Product, Source, SourceSpec, Sum, Term, SemanticRules
from joint_model import data, new_cases


def rank(vectors):
    pivots = {}
    for value in vectors:
        while value:
            bit = value.bit_length()-1
            if bit not in pivots:
                pivots[bit] = value
                break
            value ^= pivots[bit]
    return len(pivots)


def components(vectors):
    """Fundamental binary circuits; no graph-specific component routine."""
    assert len(set(vectors)) == len(vectors) and all(v > 0 for v in vectors)
    parents = list(range(len(vectors)))
    def find(i):
        while parents[i] != i:
            parents[i] = parents[parents[i]]
            i = parents[i]
        return i
    pivots = {}
    for i, value in enumerate(vectors):
        support = 1 << i
        while value:
            bit = value.bit_length()-1
            if bit not in pivots:
                pivots[bit] = value, support
                break
            old, word = pivots[bit]
            value ^= old
            support ^= word
        if not value:
            indices = [j for j in range(i+1) if support >> j & 1]
            for j in indices[1:]:
                parents[find(j)] = find(indices[0])
    groups = {}
    for i in range(len(vectors)):
        groups.setdefault(find(i), []).append(i)
    result = tuple(sorted(tuple(g) for g in groups.values()))
    assert sum(rank(vectors[i] for i in g) for g in result) == rank(vectors)
    return result


def edge_vector(edge):
    i, j = edge
    return (0 if i == 0 else 1 << (i-1)) ^ (0 if j == 0 else 1 << (j-1))


def truth(vector, world):
    return (vector & world).bit_count() % 2


def dependencies(values, sizes):
    worlds = native.worlds_for(sizes)
    lookup = dict(zip(worlds, values))
    return tuple(j for j, k in enumerate(sizes) if any(
        lookup[z] != lookup[z[:j]+(b,)+z[j+1:]]
        for z in worlds for b in range(k)))


def separable(values, sizes):
    """Independent exact flattening minors, including all categorical rows."""
    worlds = native.worlds_for(sizes)
    lookup = dict(zip(worlds, values))
    for j, k in enumerate(sizes):
        columns = [tuple(lookup[z[:j]+(b,)+z[j+1:]] for b in range(k))
                   for z in worlds if z[j] == 0]
        first = columns[0]
        if any(first[a]*column[b] != first[b]*column[a]
               for column in columns for a in range(k) for b in range(k)):
            return False
    return True


def all_encoding_audit():
    shapes = ((2, 4), (2, 2, 2))
    allowed = {}
    tensor_checks = 0
    for sizes in shapes:
        accepted = set()
        for mask in range(256):
            bits = tuple(mask >> i & 1 for i in range(8))
            one_factor = len(dependencies(bits, sizes)) <= 1
            for target in (0, 1):
                assert separable(tuple(1+8*int(b == target) for b in bits), sizes) == one_factor
                tensor_checks += 1
            if one_factor:
                accepted.add(mask)
        allowed[sizes] = accepted
    edges = tuple(combinations(range(4), 2))
    vectors = tuple(map(edge_vector, edges))
    histograms = {sizes: Counter() for sizes in shapes}
    affine = 0
    for order in permutations(range(8)):
        masks = tuple(sum(truth(v, z) << i for i, z in enumerate(order)) for v in vectors)
        for sizes in shapes:
            accepted = sum(int(mask in allowed[sizes]) << i for i, mask in enumerate(masks))
            histograms[sizes][accepted] += 1
        affine += all(order[a ^ b] == order[a] ^ order[b] ^ order[0]
                      for a in range(8) for b in range(8))
    assert affine == 8*7*6*4
    graph_checks = 0
    examples = []
    for graph_mask in range(64):
        selected = tuple(v for i, v in enumerate(vectors) if graph_mask >> i & 1)
        ranks = tuple(rank(selected[i] for i in g) for g in components(selected))
        counts = []
        for sizes in shapes:
            count = sum(number for accepted, number in histograms[sizes].items()
                        if graph_mask & accepted == graph_mask)
            capacity = 2 if sizes == (2, 4) else 1
            assert bool(count) == (max(ranks, default=0) <= capacity)
            graph_checks += 1
            counts.append(count)
        chosen = tuple(e for i, e in enumerate(edges) if graph_mask >> i & 1)
        if chosen in (edges, ((0, 1), (0, 2), (0, 3)),
                      ((0, 1), (0, 2), (0, 3), (1, 2))):
            examples.append({'edges': chosen, 'component_ranks': ranks,
                             'valid_bijections_in_shape_order': counts})
    return {'worlds': 8, 'bijections': math.factorial(8), 'affine_bijections': affine,
            'nonlinear_bijections': math.factorial(8)-affine, 'factor_shapes': shapes,
            'encoding_shape_checks': 2*math.factorial(8), 'graph_shape_existence_checks': graph_checks,
            'two_valued_tensor_minor_checks': tensor_checks,
            'separable_binary_tables_in_shape_order': [len(allowed[s]) for s in shapes],
            'examples': examples}


def graph_component_audit():
    total = 0
    for n in range(2, 6):
        edges = tuple(combinations(range(n), 2))
        # Enumerate simple cycles independently by ordered distinct vertices.
        edge_ids = {e: i for i, e in enumerate(edges)}
        cycles = set()
        for length in range(3, n+1):
            for vertices in permutations(range(n), length):
                cycle = sum(1 << edge_ids[tuple(sorted((vertices[i], vertices[(i+1) % length])))]
                            for i in range(length))
                cycles.add(cycle)
        for mask in range(1 << len(edges)):
            ids = tuple(i for i in range(len(edges)) if mask >> i & 1)
            expected = {i: {i} for i in ids}
            for cycle in cycles:
                if cycle & mask != cycle:
                    continue
                touched = [i for i in ids if cycle >> i & 1]
                union = set().union(*(expected[i] for i in touched))
                for i in union:
                    expected[i] = union
            reference = {tuple(sorted(g)) for g in expected.values()}
            vectors = tuple(edge_vector(edges[i]) for i in ids)
            actual = {tuple(ids[j] for j in group) for group in components(vectors)}
            assert actual == reference
            total += 1
    return {'all_simple_graphs_through_n': 5, 'graphs_checked': total,
            'independent_reference': 'all simple cycles, rather than fundamental GF(2) circuits'}


def snapshot_audit():
    """Actual finite count posteriors under every invertible binary map."""
    vectors = tuple(edge_vector(e) for e in combinations(range(4), 2))
    orders = []
    for columns in product(range(1, 8), repeat=3):
        if rank(columns) != 3:
            continue
        order = []
        for x in range(8):
            z = 0
            for i, column in enumerate(columns):
                if x >> i & 1:
                    z ^= column
            order.append(z)
        orders.append(tuple(order))
    assert len(set(orders)) == len(orders) == 168
    profiles = checks = irreducible = 0
    for counts in product((-1, 0, 1), repeat=6):
        exponents = tuple(sum(c*int(truth(v, z) == 0) for c, v in zip(counts, vectors))
                          for z in range(8))
        weights = tuple(9**(e-min(exponents)) for e in exponents)
        active = tuple(v for v, c in zip(vectors, counts) if c)
        width = max((rank(active[i] for i in g) for g in components(active)), default=0)
        found = [False, False]
        for order in orders:
            values = tuple(weights[z] for z in order)
            for i, sizes in enumerate(((2, 4), (2, 2, 2))):
                found[i] |= separable(values, sizes)
                checks += 1
        assert found == [width <= 2, width <= 1]
        irreducible += not found[0]
        profiles += 1
    return {'signed_counts_per_pair': [-1, 0, 1], 'legal_count_profiles': profiles,
            'invertible_binary_maps': len(orders), 'exact_posterior_factorization_checks': checks,
            'profiles_with_no_nontrivial_linear_product_encoding': irreducible,
            'scope': 'snapshot necessity only for linear parity coordinates; arbitrary-bijection theorem concerns future closure'}


def encoding(d, vectors):
    basis, sizes = [], []
    for group in components(vectors):
        before = len(basis)
        for i in group:
            if rank(basis+[vectors[i]]) > len(basis):
                basis.append(vectors[i])
        sizes.append(1 << (len(basis)-before))
    for bit in range(d):
        if rank(basis+[1 << bit]) > len(basis):
            basis.append(1 << bit)
            sizes.append(2)
    assert len(basis) == d
    inverse = {sum(truth(v, z) << i for i, v in enumerate(basis)): z for z in range(1 << d)}
    order = []
    for coordinates in native.worlds_for(sizes):
        packed = offset = 0
        for value, size in zip(coordinates, sizes):
            packed |= value << offset
            offset += size.bit_length()-1
        order.append(inverse[packed])
    return tuple(sizes), tuple(order)


def factor_query_graph(sizes, tables):
    """Local factor sums when justified; full tensor for a coupled witness."""
    worlds = native.worlds_for(sizes)
    sources = tuple(SourceSpec(f'query:{i}', 'mass', 0, F(1)) for i in range(len(tables)))
    rules = SemanticRules(sources, ('mass',), (('mass', 'mass', 'mass'),), 'mass', (F(1), F(1)))
    nodes = [Source(s.source_id) for s in sources]
    def emit(node):
        nodes.append(node)
        return len(nodes)-1
    unit = emit(Sum('mass', tuple(Term(i, 0) for i in range(len(tables)))))
    scale = emit(Sum('mass', (Term(unit, 0),)*len(sizes)))
    leaves, slot = [], 1
    for size in sizes:
        leaves.append(tuple(emit(Sum('mass', (Term(scale, j),))) for j in range(slot, slot+size)))
        slot += size
    sums = [emit(Sum('mass', tuple(Term(v, 0) for v in row))) for row in leaves]
    prefix, suffix = [unit], [unit]*(len(sizes)+1)
    for value in sums:
        prefix.append(emit(Product('mass', prefix[-1], value)))
    for j in reversed(range(len(sizes))):
        suffix[j] = emit(Product('mass', sums[j], suffix[j+1]))
    others = [emit(Product('mass', prefix[j], suffix[j+1])) for j in range(len(sizes))]
    monomials = None
    outputs = [[], []]
    for query, values in enumerate(tables):
        dependent = dependencies(values, sizes)
        assert dependent
        for label in (0, 1):
            if len(dependent) == 1:
                j = dependent[0]
                categories = {z[j] for z, y in zip(worlds, values) if y == label}
                value = emit(Sum('mass', tuple(Term(leaves[j][b], 0) for b in sorted(categories))))
                value = emit(Product('mass', value, others[j]))
            else:
                if monomials is None:
                    monomials = []
                    for z in worlds:
                        value = leaves[0][z[0]]
                        for j in range(1, len(sizes)):
                            value = emit(Product('mass', value, leaves[j][z[j]]))
                        monomials.append(value)
                value = emit(Sum('mass', tuple(Term(v, 0) for v, y in zip(monomials, values) if y == label)))
            outputs[label].append(Term(emit(Product('mass', query, value)), 0))
    eight = unit
    for _ in range(3):
        eight = emit(Sum('mass', (Term(eight, 0), Term(eight, 0))))
    heads = tuple(emit(Product('mass', emit(Sum('mass', tuple(row))), eight)) for row in outputs)
    graph = Program(tuple(nodes), slot, heads)
    graph.validate(rules)
    return rules, graph


def inputs(count, query):
    return {f'query:{i}': F(i == query) for i in range(count)}


def native_audit():
    cases = [(4, ((0, 1), (1, 2), (2, 3)), 3, 'forest'),
             (5, ((0, 1), (0, 2), (1, 2), (0, 3), (0, 4), (3, 4)), 2, 'two_triangles_sharing_one_vertex'),
             (4, tuple(combinations(range(4), 2)), 2, 'complete_graph'),
             (4, ((0, 1),), 3, 'nonlinear_bijection')]
    rows, checks = [], 0
    for n, edges, depth, name in cases:
        vectors = tuple(map(edge_vector, edges))
        sizes, order = encoding(n-1, vectors)
        if name == 'nonlinear_bijection':
            sizes = (2, 4)
            order = tuple(a | ((b & 1) << 1) | (((b >> 1) ^ (a & b & 1)) << 2)
                          for a, b in native.worlds_for(sizes))
            assert not all(order[a ^ b] == order[a] ^ order[b] ^ order[0]
                           for a in range(8) for b in range(8))
        tables = tuple(tuple(truth(v, z) for z in order) for v in vectors)
        assert all(len(dependencies(t, sizes)) == 1 for t in tables)
        rules, graph = factor_query_graph(sizes, tables)
        spec = native.spec_for(graph, len(sizes))
        factors = tuple((F(1, k),)*k for k in sizes)
        state = native.initial_state(graph, rules, native.factors_to_theta(factors), 0, spec=spec, bit_limit=native.BITS)
        start = state, factors, (F(1, 1 << (n-1)),)*(1 << (n-1))
        before = checks
        def step(item, query, label):
            nonlocal checks
            state, factors, oracle = item
            table = tuple((8*int(y == 0), 8*int(y == 1)) for y in tables[query])
            committed, updated, exact = native.checked_step(rules, graph, state, spec,
                inputs(len(edges), query), factors, native.worlds_for(sizes), table, label)
            raw = tuple(w*(9 if truth(vectors[query], z) == label else 1) for z, w in enumerate(oracle))
            new_oracle = tuple(w/sum(raw) for w in raw)
            assert native.joint_weights(updated, native.worlds_for(sizes)) == exact == tuple(new_oracle[z] for z in order)
            checks += 1
            return committed, updated, new_oracle
        frontier = [start]
        for _ in range(depth):
            frontier = [step(item, q, y) for item in frontier for q in range(len(edges)) for y in (0, 1)]
        profiled, factors, oracle = step(step(start, 0, 0), 0, 0)
        attached = native.attach_boundary(profiled, 12, spec)
        assert attached == replace(profiled, cursor=12)
        step((attached, factors, oracle), 0, 1)
        rows.append({'case': name, 'n': n, 'edges': edges, 'factor_sizes': sizes,
                     'native': graph.counts(), 'native_units': checks-before})
    return {'cases': rows, 'native_units': checks, 'complete_state_checks': 2*checks,
            'profile_attachments': len(cases)}


def closing_cycle_witness():
    forest = (edge_vector((0, 1)), edge_vector((1, 2)))
    sizes, order = encoding(2, forest)
    vectors = forest+(edge_vector((0, 2)),)
    tables = tuple(tuple(truth(v, z) for z in order) for v in vectors)
    rules, graph = factor_query_graph(sizes, tables)
    spec = native.spec_for(graph, 2)
    factors = ((F(1, 2), F(1, 2)),)*2
    state = native.initial_state(graph, rules, native.factors_to_theta(factors), 0, spec=spec, bit_limit=native.BITS)
    for query in (0, 1, 2):
        table = tuple((8*int(y == 0), 8*int(y == 1)) for y in tables[query])
        state, factors, exact = native.checked_step(rules, graph, state, spec,
            inputs(3, query), factors, native.worlds_for(sizes), table, 0)
        if query < 2:
            assert native.joint_weights(factors, native.worlds_for(sizes)) == exact
    assert native.joint_weights(factors, native.worlds_for(sizes)) != exact
    prediction = native.evaluate(graph, rules, state.theta, inputs(3, 2), (), bit_limit=native.BITS)
    oracle = sum(w*F(9 if y == 0 else 1, 10) for w, y in zip(exact, tables[2]))
    assert prediction.probabilities[0] == F(761, 882) and oracle == F(37, 42)
    return {'history': [[0, 1, 0], [1, 2, 0], [0, 2, 0]], 'native_units': 3,
            'native_next_probability0': str(prediction.probabilities[0]),
            'full_posterior_next_probability0': str(oracle),
            'absolute_gap': str(oracle-prediction.probabilities[0]),
            'first_two_updates_preserve_independence_third_does_not': True}


def tape_structure_audit():
    rows = []
    for case in new_cases():
        n = case[0]
        _, _, training, evaluation = data(case)
        counts = Counter()
        first_joint = None
        widths = []
        initial = None
        for cursor, (i, j, label) in enumerate(training+evaluation, 1):
            if i != j:
                edge = tuple(sorted((i, j)))
                counts[edge] += 1 if label == 0 else -1
            vectors = tuple(edge_vector(e) for e, c in sorted(counts.items()) if c)
            ranks = sorted(rank(vectors[i] for i in g) for g in components(vectors))
            if cursor == len(training):
                initial = ranks
            if cursor >= len(training):
                widths.append(max(ranks, default=0))
                if ranks == [n-1] and first_joint is None:
                    first_joint = cursor
        rows.append({'case': case, 'training_events': len(training), 'evaluation_events': len(evaluation),
                     'training_active_component_ranks': initial, 'final_active_component_ranks': ranks,
                     'first_single_full_rank_block_cursor': first_joint,
                     'largest_active_block_rank_at_or_after_training': max(widths),
                     'post_training_cuts_with_full_rank_block': widths.count(n-1)})
    return {'scope': 'passive active signed-count graph; snapshot parity coordinates only, not GPU/model outcomes',
            'cases': rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = {'status': 'PASS', 'scope': 'fixed product encodings, exact closure and native passive audits',
              'arbitrary_bijections': all_encoding_audit(), 'cycle_components': graph_component_audit(),
              'linear_snapshot_posteriors': snapshot_audit(),
              'native_learner': native_audit(), 'legal_closing_cycle': closing_cycle_witness(),
              'retained_tape_structure': tape_structure_audit()}
    text = json.dumps(result, indent=2)+'\n'
    if args.output:
        args.output.write_text(text, encoding='utf-8')
    print(text)


if __name__ == '__main__':
    main()
