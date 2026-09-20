"""Exact passive checks for the positive count-partition decoder lower bound.

The arithmetic DAG is an analysis object, not a native source interface or
Runtime candidate. Native checks separately use the actual world-slot learner.
"""
from collections import Counter, defaultdict
from fractions import Fraction as F
from itertools import combinations, product
from math import comb
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(Path(__file__).resolve().parent)]
from fp_reference.learner import SIMPLEX_GRADIENT, LearnerSpec, initial_state, observe_event, commit_event
from fp_reference.semantics import evaluate
import simplex_gradient as literal

BITS = 32768


def cut_words(n):
    edges = tuple(combinations(range(n), 2))
    worlds = tuple((0,)+z for z in product((0, 1), repeat=n-1))
    words = tuple(sum((z[i] ^ z[j]) << e for e, (i, j) in enumerate(edges)) for z in worlds)
    assert len(set(words)) == 1 << (n-1)
    return edges, worlds, words


def components(n, edges, mask):
    parent = list(range(n))

    def root(i):
        while parent[i] != i:
            i = parent[i]
        return i

    for e, (i, j) in enumerate(edges):
        if mask >> e & 1:
            parent[root(i)] = root(j)
    return len({root(i) for i in range(n)})


def lower_exponent(n):
    degree = comb(n, 2)
    return next(r-1 for r in range(2, n+1) if 3*comb(r, 2) >= degree)


def rectangle_audit():
    rows = []
    for n in range(3, 7):
        edges, _, words = cut_words(n)
        degree, checked, maximum = len(edges), 0, 0
        full = (1 << degree)-1
        for left in range(1 << degree):
            if not degree <= 3*left.bit_count() <= 2*degree:
                continue
            right = full ^ left
            # Enumerate the actual compatibility relation, independently of the
            # component formula. Its bipartite components are complete rectangles.
            adjacency = defaultdict(set)
            for word in words:
                adjacency[word & left].add(word & right)
            blocks = Counter(frozenset(neighbors) for neighbors in adjacency.values())
            union = set()
            for neighbors in blocks:
                assert not union.intersection(neighbors)
                union.update(neighbors)
            observed = max(len(neighbors)*count for neighbors, count in blocks.items())
            c_left, c_right = components(n, edges, left), components(n, edges, right)
            assert observed == 1 << (c_left+c_right-2)
            assert len(blocks) == 1 << (n+1-c_left-c_right)
            assert sum(len(neighbors)*count for neighbors, count in blocks.items()) == len(words)
            assert min(c_left, c_right) == 1
            assert observed <= 1 << (n-1-lower_exponent(n))
            maximum = max(maximum, observed)
            checked += 1
        rows.append({'n': n, 'balanced_edge_partitions': checked,
                     'largest_actual_rectangle': maximum,
                     'actual_rectangle_cover_lower': len(words)//maximum,
                     'proved_completed_polynomial_gate_lower': 1 << lower_exponent(n)})
    return {'partitions_checked': sum(r['balanced_edge_partitions'] for r in rows), 'cases': rows}


class Circuit:
    """Binary nonnegative arithmetic DAG with exact symbolic multilinear audit."""
    def __init__(self):
        self.nodes = []
        self.memo = {}

    def emit(self, node):
        if node not in self.memo:
            self.memo[node] = len(self.nodes)
            self.nodes.append(node)
        return self.memo[node]

    def symbolics(self):
        polynomials = []
        for tag, *args in self.nodes:
            if tag == 'one':
                p = {0: 1}
            elif tag == 'var':
                p = {1 << args[0]: 1}
            else:
                left, right = (polynomials[i] for i in args)
                if tag == 'add':
                    p = dict(left)
                    for monomial, coefficient in right.items():
                        p[monomial] = p.get(monomial, 0)+coefficient
                else:
                    assert tag == 'mul'
                    p = {}
                    for a, c in left.items():
                        for b, d in right.items():
                            assert not a & b, 'multilinearity was not retained'
                            p[a | b] = p.get(a | b, 0)+c*d
            polynomials.append(p)
        return polynomials

    def scalar(self, inputs, head):
        values = []
        for tag, *args in self.nodes:
            if tag == 'one':
                v = 1
            elif tag == 'var':
                v = inputs[args[0]]
            elif tag == 'add':
                v = values[args[0]]+values[args[1]]
            else:
                v = values[args[0]]*values[args[1]]
            values.append(v)
        return values[head]

    def operations(self):
        return sum(node[0] in ('add', 'mul') for node in self.nodes)


def cut_circuit(n):
    edges, _, words = cut_words(n)
    circuit = Circuit()
    one = circuit.emit(('one',))
    variables = tuple(circuit.emit(('var', e)) for e in range(len(edges)))
    terms = []
    for word in words:
        factors = [variables[e] for e in range(len(edges)) if word >> e & 1]
        head = factors[0] if factors else one
        for value in factors[1:]:
            head = circuit.emit(('mul', head, value))
        terms.append(head)
    while len(terms) > 1:
        terms = [circuit.emit(('add', terms[i], terms[i+1])) if i+1 < len(terms) else terms[i]
                 for i in range(0, len(terms), 2)]
    return circuit, terms[0]


def complete_edges(original):
    """Multilinear monotone circuits admit edge completion with O(E) overhead."""
    lifted = Circuit()
    heads, supports = [], []
    for tag, *args in original.nodes:
        if tag == 'one':
            support, head = 0, lifted.emit(('one',))
        elif tag == 'var':
            support, head = 1 << args[0], lifted.emit(('var', 2*args[0]+1))
        else:
            a, b = args
            support = supports[a] | supports[b]
            children = [heads[a], heads[b]]
            if tag == 'mul':
                assert not supports[a] & supports[b]
            else:
                assert tag == 'add'
                for j, old in enumerate((a, b)):
                    missing = support ^ supports[old]
                    while missing:
                        low = missing & -missing
                        e = low.bit_length()-1
                        children[j] = lifted.emit(('mul', children[j], lifted.emit(('var', 2*e))))
                        missing ^= low
            head = lifted.emit((tag, *children))
        heads.append(head)
        supports.append(support)
    return lifted, heads


def completion_audit():
    rows = []
    for n in range(3, 8):
        edges, _, words = cut_words(n)
        original, head = cut_circuit(n)
        assert original.symbolics()[head] == {word: 1 for word in words}
        lifted, heads = complete_edges(original)
        expected = {sum(1 << (2*e+((word >> e) & 1)) for e in range(len(edges))): 1
                    for word in words}
        assert lifted.symbolics()[heads[head]] == expected
        assert lifted.operations() <= (len(edges)+1)*original.operations()
        rows.append({'n': n, 'monomials': len(words), 'original_operations': original.operations(),
                     'completed_operations': lifted.operations(),
                     'general_overhead_bound': (len(edges)+1)*original.operations()})
    return rows


def native_count_audit():
    commits = forecasts = histories = 0
    for n, levels in ((3, (0, 1, 2)), (4, (0, 1))):
        edges, worlds, _ = cut_words(n)
        circuit, head = cut_circuit(n)
        rules, graph, native_worlds = literal.relation_graph(n)
        assert worlds == native_worlds
        spec = LearnerSpec(1, F(1), optimizer_id=SIMPLEX_GRADIENT,
                          simplex_slots=tuple(range(1, len(worlds)+1)))
        for counts in product(levels, repeat=len(edges)):
            state = initial_state(graph, rules, (F(1),)+(F(1, len(worlds)),)*len(worlds),
                                  0, spec=spec, bit_limit=BITS)
            for (i, j), count in zip(edges, counts):
                for _ in range(count):
                    prediction = evaluate(graph, rules, state.theta, literal.context(n, i, j), (), bit_limit=BITS)
                    state = commit_event(observe_event(graph, state, spec, prediction, 0, bit_limit=BITS),
                                         spec, bit_limit=BITS)
                    commits += 1
            weights = tuple(F(1, 9**sum(c for (i, j), c in zip(edges, counts) if z[i] ^ z[j]))
                            for z in worlds)
            partition = circuit.scalar(tuple(F(1, 9**c) for c in counts), head)
            assert partition == sum(weights)
            assert state.theta[1:] == tuple(F(w, partition) for w in weights)
            for i, j in product(range(n), repeat=2):
                prediction = evaluate(graph, rules, state.theta, literal.context(n, i, j), (), bit_limit=BITS)
                oracle = F(1, 10)+F(4, 5)*sum((w for z, w in zip(worlds, state.theta[1:])
                                             if z[i] ^ z[j]), F(0))
                assert prediction.normalizer == 10 and prediction.probabilities[1] == oracle
                forecasts += 1
            histories += 1
    return {'independent_count_grid_histories': histories, 'native_commits': commits,
            'all_pair_native_forecasts': forecasts}


def scope_counterexample():
    # A hard shared positive polynomial can cancel from normalized forecasts.
    circuit, head = cut_circuit(4)
    values = []
    for inputs in ((1,)*6, (9,)*6, (1, 9, 81, 9, 1, 81)):
        z = circuit.scalar(tuple(F(1, x) for x in inputs), head)
        assert F(1+z, 2+2*z) == F(1, 2)
        values.append({'partition': str(z), 'heads_with_positive_bases': [str(1+z)]*2,
                       'normalized_probability': '1/2'})
    return {'constant_forecast_despite_hard_common_mass': values,
            'general_normalized_forecast_lower_bound_claimed': False,
            'finite_horizon_or_approximate_lower_bound_claimed': False,
            'Runtime_source_or_installation_authority_claimed': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = {'status': 'PASS', 'arithmetic': 'exact integers and native Fractions',
              'scope': 'fixed nonnegative scalar arithmetic circuit for exact unnormalized partition',
              'cut_rectangles': rectangle_audit(), 'edge_completion': completion_audit(),
              'actual_count_grid': native_count_audit(), 'scope_counterexample': scope_counterexample()}
    text = json.dumps(result, indent=2)+'\n'
    if args.output:
        args.output.write_text(text, encoding='utf-8')
    print(text)


if __name__ == '__main__':
    main()
