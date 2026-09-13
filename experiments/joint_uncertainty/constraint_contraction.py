"""Positive signed-constraint contraction of a finite-window latent posterior.

An initially registered native model, not a Runtime proposer or certificate.
Both constructions receive exactly the same explicitly lagged source interface.
No posterior value, fitted coefficient, or recurrent endpoint is supplied.
"""
from dataclasses import replace
from fractions import Fraction as F
from itertools import combinations, product
from functools import lru_cache
import argparse
import json

import recurrent_control as control
from fp_reference.program import Product, Program, SemanticRules, Source, SourceSpec, Sum, Term
from fp_reference.data_usage import DataContract, SourceRead, StreamSpec
from fp_reference.learner import LearnerSpec
from fp_reference.float64_bridge import Float64Contract
from fp_reference.runtime import OnlineContract
from fp_reference.semantics import evaluate


def partitions(size, blocks):
    """Restricted growth strings: each equality partition appears once."""
    assert size >= 1 and blocks >= 1
    def visit(prefix, largest):
        if len(prefix) == size:
            yield prefix
            return
        for label in range(min(largest + 2, blocks)):
            yield from visit(prefix + (label,), max(largest, label))
    yield from visit((0,), 0)


def constraint_rank(edges, labels):
    """Rank if a labelled GF(2) system is consistent, else None.

    This compile-time calculation concerns endpoint-identity patterns, never
    the latent bits, incoming observations or a supplied posterior vector.
    """
    rows = {}
    for (left, right), label in zip(edges, labels, strict=True):
        mask = (1 << left) ^ (1 << right)
        rhs = label
        while mask:
            pivot = mask.bit_length() - 1
            if pivot not in rows:
                rows[pivot] = (mask, rhs)
                break
            previous, target = rows[pivot]
            mask ^= previous
            rhs ^= target
        if not mask and rhs:
            return None
    return len(rows)


def source_specs(n, window):
    specs = []
    for lag in range(window + 1):
        specs.extend(SourceSpec(f'x{lag}:{side}:{i}', 'mass', lag, F(1))
                     for side in (0, 1) for i in range(n))
        if lag:
            specs.extend(SourceSpec(f'y{lag}:{y}', 'mass', lag, F(1)) for y in (0, 1))
    return tuple(specs)


def point(n, window, history, query):
    result = control.context(n, *query)
    for lag in range(1, window + 1):
        if lag <= len(history):
            i, j, y = history[-lag]
            result += control.context(n, i, j) + (F(y == 0), F(y == 1))
        else:
            result += (F(0),) * (2 * n + 2)
    return result


def histories(n, window):
    alphabet = tuple(product(range(n), range(n), (0, 1)))
    for length in range(window + 1):
        yield from product(alphabet, repeat=length)


def domain(n, window):
    return tuple(point(n, window, history, query)
                 for history in histories(n, window)
                 for query in product(range(n), repeat=2))


class Builder:
    def __init__(self, n, window):
        assert n >= 2 and window >= 1
        self.n = n
        self.rules = SemanticRules(source_specs(n, window), ('mass',),
                                  (('mass', 'mass', 'mass'),), 'mass', (F(1), F(1)))
        self.nodes = [Source(s.source_id) for s in self.rules.sources]
        self.cache = {node: index for index, node in enumerate(self.nodes)}
        self.sources = {s.source_id: i for i, s in enumerate(self.rules.sources)}
        self.one = self.add(self.sources[f'x0:0:{i}'] for i in range(n))
        self.zero = self.add(())
        self.equalities = {}
        self.patterns = {}
        self.labels = {}
        self.coefficients = {}

    def emit(self, node):
        if node not in self.cache:
            self.cache[node] = len(self.nodes)
            self.nodes.append(node)
        return self.cache[node]

    def add(self, parents, slot=0):
        return self.emit(Sum('mass', tuple(Term(parent, slot) for parent in parents)))

    def mul(self, a, b):
        return self.emit(Product('mass', a, b))

    def prod(self, parents):
        parents = tuple(parents)
        if not parents:
            return self.one
        result = parents[0]
        for parent in parents[1:]:
            result = self.mul(result, parent)
        return result

    def equality(self, a, b, same):
        a, b = sorted((a, b))
        key = (a, b, same)
        if key not in self.equalities:
            self.equalities[key] = self.add(
                self.mul(self.sources[f'x{a[0]}:{a[1]}:{i}'],
                         self.sources[f'x{b[0]}:{b[1]}:{j}'])
                for i, j in product(range(self.n), repeat=2) if (i == j) == same)
        return self.equalities[key]

    def pattern(self, positions, partition):
        key = (positions, partition)
        if key not in self.patterns:
            representatives = {}
            factors = []
            for position, block in zip(positions, partition, strict=True):
                if block in representatives:
                    factors.append(self.equality(representatives[block], position, True))
                else:
                    representatives[block] = position
            factors.extend(self.equality(a, b, False)
                           for a, b in combinations(representatives.values(), 2))
            assert factors  # all endpoint positions are tested, including missing frames
            self.patterns[key] = self.prod(factors)
        return self.patterns[key]

    def label_monomial(self, events, labels):
        key = (events, labels)
        if key not in self.labels:
            self.labels[key] = self.prod(self.sources[f'y{lag}:{y}']
                                         for lag, y in zip(events, labels, strict=True))
        return self.labels[key]

    def coefficient(self, count, rank):
        key = (count, rank)
        if key not in self.coefficients:
            # At the actual Gamma=(1,8), 8^count / 2^rank = 8^(count-rank)*4^rank.
            # Four is paid repeated unit syntax, eight uses the actual noise slot.
            two = self.add((self.one, self.one))
            four = self.add((two, two))
            eight = self.add((self.one,), slot=1)
            self.coefficients[key] = self.prod((eight,) * (count - rank) + (four,) * rank)
        return self.coefficients[key]

    def finish(self, heads):
        heads = tuple(heads)
        graph = Program(tuple(self.nodes), 2, heads)
        graph.validate(self.rules)
        return self.rules, graph


def contracted(n, window):
    b = Builder(n, window)
    common = []
    query_terms = [[], []]
    for length in range(window + 1):
        for events in combinations(range(1, window + 1), length):
            for with_query in (False, True):
                if not events and not with_query:
                    continue  # empty subset is exactly the registered base one
                selected = events + ((0,) if with_query else ())
                positions = tuple((lag, side) for lag in selected for side in (0, 1))
                for partition in partitions(len(positions), n):
                    edges = tuple(zip(partition[::2], partition[1::2]))
                    rank = constraint_rank(edges, (0,) * len(edges))
                    for y in ((0, 1) if with_query else (None,)):
                        allowed = tuple(labels for labels in product((0, 1), repeat=length)
                                        if constraint_rank(edges, labels + ((y,) if with_query else ())) is not None)
                        if not allowed:
                            continue
                        labels = b.add(b.label_monomial(events, pattern) for pattern in allowed)
                        term = b.prod((b.pattern(positions, partition), labels,
                                       b.coefficient(len(selected), rank)))
                        (query_terms[y] if with_query else common).append(term)
    common_node = b.add(common)
    return b.finish(b.add((common_node, b.add(terms))) for terms in query_terms)


def enumerated(n, window):
    """Full latent-world positive baseline on exactly the same source interface."""
    b = Builder(n, window)
    worlds = tuple((0,) + z for z in product((0, 1), repeat=n - 1))
    pairs = {(lag, i, j): b.mul(b.sources[f'x{lag}:0:{i}'], b.sources[f'x{lag}:1:{j}'])
             for lag in range(window + 1) for i, j in product(range(n), repeat=2)}
    labelled = {(lag, i, j, y): b.mul(pairs[lag, i, j], b.sources[f'y{lag}:{y}'])
                for lag in range(1, window + 1) for i, j, y in product(range(n), range(n), (0, 1))}
    excesses = []
    query_terms = [[], []]
    for z in worlds:
        excess = b.zero
        for lag in reversed(range(1, window + 1)):
            indicator = b.add(labelled[lag, i, j, z[i] ^ z[j]] for i, j in product(range(n), repeat=2))
            gain = b.mul(indicator, b.add((b.one, excess)))
            excess = b.emit(Sum('mass', (Term(excess, 0), Term(gain, 1))))
        excesses.append(excess)
        weight = b.add((b.one, excess))
        for y in (0, 1):
            indicator = b.add(pairs[0, i, j] for i, j in product(range(n), repeat=2) if z[i] ^ z[j] == y)
            query_terms[y].append(b.mul(weight, indicator))
    common = b.add((b.add((b.one,) * (len(worlds) - 1)),) + tuple(excesses))
    return b.finish(b.emit(Sum('mass', (Term(common, 0), Term(b.add(terms), 1)))) for terms in query_terms)


def masses(n, history, query):
    """Independent uncontracted fair-prior average, over all 2^n assignments."""
    result = [F(0), F(0)]
    for z in product((0, 1), repeat=n):
        weight = 9 ** sum((z[i] ^ z[j]) == y for i, j, y in history)
        for y in (0, 1):
            result[y] += F(weight * (9 if z[query[0]] ^ z[query[1]] == y else 1), 2 ** n)
    return tuple(result)


def fixture(kind, n=2, window=3, horizon=5):
    rules, graph = {'contracted': contracted, 'enumerated': enumerated}[kind](n, window)
    # Both model controls receive the same envelope. The contraction's smaller
    # attained/theorem upper is recorded separately, not spent as a larger grant.
    cap = 10 * 9 ** window * 2 ** (n - 1)
    cfg = replace(control.contract(source_domain=False, pattern=(F(1), F(8))),
                  semantics=rules, source_domain=domain(n, window),
                  graph_limits={'nodes': 20000, 'SUMs': 10000, 'PRODUCTs': 16000, 'edges': 120000, 'slots': 2},
                  normalizer_cap=F(cap), activation_cap=F(cap), reference_integer_bits=32768,
                  limits=control.limits(byte_cap=2 << 30, work_cap=10 ** 12))
    reads = tuple(SourceRead(f'x{lag}:{side}:{i}', 'input', side * n + i, lag)
                  for lag in range(window + 1) for side in (0, 1) for i in range(n))
    reads += tuple(SourceRead(f'y{lag}:{y}', 'target_atom', y, lag)
                   for lag in range(1, window + 1) for y in (0, 1))
    data = DataContract((StreamSpec('online', 'online', tuple(f'contract-{i}' for i in range(horizon))),),
                        'online', (F(1),) * (2 * n), reads)
    online = OnlineContract(data, LearnerSpec(1, F(0)), float64=Float64Contract(F(1, 100), F(1, 100)))
    return cfg, graph, online


def counts():
    return [{'n': n, 'window': window, 'source_domain_rows': n*n*sum((2*n*n)**j for j in range(window+1)),
             'graphs': {kind: builder(n, window)[1].counts()
                        for kind, builder in (('contracted', contracted), ('enumerated', enumerated))}}
            for n, window in ((2, 2), (2, 3), (3, 2), (3, 3), (8, 2), (8, 3))]


def integer_values(graph, rules, row):
    """Separate exact-integer native interpreter at Gamma=(1,8)."""
    sources = dict(zip((s.source_id for s in rules.sources), row, strict=True))
    values = []
    for node in graph.nodes:
        if isinstance(node, Source):
            value = int(sources[node.source_id])
            assert value == sources[node.source_id]
        elif isinstance(node, Product):
            value = values[node.left] * values[node.right]
        else:
            value = sum((1, 8)[t.slot] * values[t.parent] for t in node.terms)
        values.append(value)
    return tuple(values)


def algebra():
    from audit_cuda_primitives import HALF, SINGLE
    rank_checks = native_checks = formal_checks = rounded_checks = 0
    # Independent brute force checks the signed-rank identity, including loops,
    # parallel edges and all possible parity inconsistency patterns through k=4.
    for length in range(1, 5):
        for partition in partitions(2 * length, 3):
            edges = tuple(zip(partition[::2], partition[1::2]))
            assignments = tuple(product((0, 1), repeat=max(partition) + 1))
            for labels in product((0, 1), repeat=length):
                count = sum(all((z[a] ^ z[b]) == y for (a, b), y in zip(edges, labels)) for z in assignments)
                rank = constraint_rank(edges, labels)
                assert F(count, len(assignments)) == (F(0) if rank is None else F(1, 2 ** rank))
                rank_checks += 1
    seen_values = set()
    @lru_cache(None)
    def exact_half(value):
        return HALF.decode(HALF.encode_exact(F(value))) == value
    cases = []
    maximum_native = maximum_normalizer = 0
    for n, window in ((2, 2), (2, 3), (3, 2), (3, 3)):
        rules, graph = contracted(n, window)
        baseline_rules, baseline = enumerated(n, window)
        assert rules == baseline_rules
        if window == 3 and n == 3:
            samples = ((),) + tuple(tuple((i, j, y) for (i, j), y in zip(edges, labels))
                for edges in (((0, 1), (1, 2), (0, 2)), ((0, 1),) * 3,
                              ((0, 0), (0, 1), (1, 1)))
                for labels in product((0, 1), repeat=3))
        else:
            samples = tuple(histories(n, window))
        count = 0
        # Caching the independent latent sum avoids repeating it for formal and
        # rounded checks; it never enters a Program or Runtime SourceRead.
        for history in samples:
            for query in product(range(n), repeat=2):
                row = point(n, window, history, query)
                wanted = masses(n, history, query)
                values = integer_values(graph, rules, row)
                actual = tuple(F(1 + values[h]) for h in graph.heads)
                assert actual == wanted
                assert sum(actual) <= 10 * 9 ** window
                assert max(values) <= 10 * 9 ** window
                assert all(exact_half(value) for value in values)
                seen_values.update(values)
                base_values = integer_values(baseline, baseline_rules, row)
                assert tuple(1 + base_values[h] for h in baseline.heads) == tuple(2 ** (n - 1) * x for x in wanted)
                maximum_native = max(maximum_native, max(values))
                maximum_normalizer = max(maximum_normalizer, sum(actual))
                # Formal Fraction semantics and independent rounded semantics on
                # every label pattern of the selected maximum-length diagnostics.
                diagnostic = (len(history) == window and query == (0, 1)
                              and tuple((i, j) for i, j, _ in history) in
                              (((0, 1),) * window, ((0, 1), (1, 2), (0, 2))))
                if diagnostic or not history:
                    inputs = dict(zip((s.source_id for s in rules.sources), row, strict=True))
                    reference = evaluate(graph, rules, (F(1), F(8)), inputs, (), bit_limit=32768)
                    assert reference.masses == wanted
                    rounded = control.model_predict(graph, rules, control.model_initial(graph, rules, (F(1), F(8))), inputs)
                    assert rounded['values'] == values and rounded['masses'] == wanted
                    assert all(p == SINGLE.decode(SINGLE.rounded(m / sum(wanted)))
                               for p, m in zip(rounded['probabilities'], wanted))
                    formal_checks += 1
                    rounded_checks += 1
                count += 1
        native_checks += count
        cases.append({'n': n, 'window': window, 'native_forecasts': count,
                      'history_scope': 'all causal histories' if (n, window) != (3, 3) else
                                       'empty and all labels on triangle, repeated-edge and diagonal diagnostics'})
    # A rounding witness under the SAME expanded interface and base, retaining
    # the full latent baseline's actual half error rather than weakening it.
    witness = {}
    for kind, build in (('contracted', contracted), ('enumerated', enumerated)):
        rules, graph = build(2, 3)
        row = point(2, 3, ((0, 0, 0),) * 3, (0, 0))
        inputs = dict(zip((s.source_id for s in rules.sources), row, strict=True))
        reference = evaluate(graph, rules, (F(1), F(8)), inputs, (), bit_limit=32768)
        rounded = control.model_predict(graph, rules, control.model_initial(graph, rules, (F(1), F(8))), inputs)
        witness[kind] = {'reference_masses': list(map(str, reference.masses)),
                         'rounded_masses': list(map(str, rounded['masses']))}
        assert (rounded['masses'] == reference.masses) == (kind == 'contracted')
    assert 'torch' not in control.sys.modules
    return {'signed_rank_checks': rank_checks, 'native_forecasts': native_checks,
            'formal_fraction_forecasts': formal_checks, 'rounded_interpreter_forecasts': rounded_checks,
            'distinct_exact_half_node_values': len(seen_values), 'maximum_node_value': maximum_native,
            'maximum_normalizer': str(maximum_normalizer), 'cases': cases, 'rounding_witness': witness,
            'scope': 'exact model identity and finite numerical checks; no owned Runtime or target authority'}


def boundaries():
    from audit_reference_events import forward_oracle
    gradients = {}
    soft_probabilities = {}
    for kind, build in (('contracted', contracted), ('enumerated', enumerated)):
        rules, graph = build(2, 2)
        row = point(2, 2, ((0, 1, 0),), (0, 1))
        inputs = dict(zip((s.source_id for s in rules.sources), row, strict=True))
        probabilities, derivative = forward_oracle(graph, rules, (F(1), F(8)), inputs)
        assert probabilities == (F(41, 50), F(9, 50))
        gradients[kind] = tuple(map(str, derivative[0]))
        row = list(point(2, 2, ((0, 1, 0), (0, 1, 1)), (0, 1)))
        row[4:6] = (F(1, 2), F(1, 2))  # newest history's first token is soft
        inputs = dict(zip((s.source_id for s in rules.sources), row, strict=True))
        soft_probabilities[kind] = tuple(map(str, evaluate(graph, rules, (F(1), F(8)), inputs, (), bit_limit=32768).probabilities))
    assert gradients == {'contracted': ('-96/205', '-18/1025'), 'enumerated': ('-256/1025', '-4/205')}
    assert soft_probabilities == {'contracted': ('59/98', '39/98'), 'enumerated': ('43/70', '27/70')}
    return {'same_probability_different_target0_gradients': gradients,
            'out_of_domain_soft_history_predictions': soft_probabilities,
            'scope': 'no full-learner quotient or soft-input extension'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--counts', action='store_true')
    parser.add_argument('--algebra', action='store_true')
    parser.add_argument('--boundaries', action='store_true')
    args = parser.parse_args()
    print(json.dumps(boundaries() if args.boundaries else algebra() if args.algebra else counts(), indent=2))
