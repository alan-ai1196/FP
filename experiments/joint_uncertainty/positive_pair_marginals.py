"""Positive shared all-pair marginal circuits and exact passive audits.

This constructs ordinary native Programs, not Runtime candidates or certificates.
The unit source identity is scoped to the complete one-hot pair source domain.
All world weights and the fixed-slot gradient remain explicit learner state.
"""
from dataclasses import replace
from fractions import Fraction as F
from itertools import combinations, product
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(Path(__file__).resolve().parent)]
from fp_reference.core import ContractError, natural
from fp_reference.cuda_prefix import output_cells
from fp_reference.learner import (SIMPLEX_GRADIENT, LearnerSpec, ReferenceLearnerState,
    initial_state, ce_gradient, observe_event, commit_event)
from fp_reference.profile import attach_boundary
from fp_reference.program import Product, Program, SemanticRules, Source, SourceSpec, Sum, Term
from fp_reference.semantics import evaluate
import simplex_gradient as literal

BITS = 32768


def relation_graph(n):
    """O(2**(n-1) + n**2) native incidences; no supplied numeric constants."""
    natural(n, 'relation token count', positive=True)
    if n < 2:
        raise ContractError('at least two tokens are required')
    m = n-1
    worlds = tuple((0,)+z for z in product((0, 1), repeat=m))
    specs = tuple(SourceSpec(f'x{side}:{i}', 'mass', 0, F(1))
                  for side in (0, 1) for i in range(n))
    rules = SemanticRules(specs, ('mass',), (('mass', 'mass', 'mass'),),
                          'mass', (F(1), F(1)))
    nodes = [Source(s.source_id) for s in specs]

    def emit(node):
        nodes.append(node)
        return len(nodes)-1

    def add(terms):
        # Pair adjacent terms at each layer: a balanced binary positive sum.
        # Singleton weighted leaves remain edges until a value is needed.
        terms = list(terms)
        assert terms
        while len(terms) > 1:
            terms = [Term(emit(Sum('mass', tuple(terms[k:k+2]))), 0)
                     if k+1 < len(terms) else terms[k]
                     for k in range(0, len(terms), 2)]
        return terms[0]

    def value(term):
        if term.slot == 0:
            return term.parent
        return emit(Sum('mass', (term,)))

    unit = emit(Sum('mass', tuple(Term(i, 0) for i in range(n))))
    prefix = {z[1:]: Term(unit, k+1) for k, z in enumerate(worlds)}
    marginal_start = len(nodes)
    for depth in range(m-1, -1, -1):
        for p in product((0, 1), repeat=depth):
            prefix[p] = add((prefix[p+(0,)], prefix[p+(1,)]))

    filtered = {}
    for j in range(1, m+1):
        for b in (0, 1):
            for p in product((0, 1), repeat=j-1):
                filtered[p, j, b] = prefix[p+(b,)]
            for depth in range(j-2, -1, -1):
                for p in product((0, 1), repeat=depth):
                    filtered[p, j, b] = add((filtered[p+(0,), j, b],
                                             filtered[p+(1,), j, b]))

    marginals = {(0, j, y): filtered[(), j, y]
                 for j in range(1, m+1) for y in (0, 1)}
    for i, j in combinations(range(1, m+1), 2):
        for y in (0, 1):
            marginals[i, j, y] = add(filtered[p, j, p[-1] ^ y]
                for p in product((0, 1), repeat=i))
    marginal_sums = len(nodes)-marginal_start
    # Only n=2 has a final marginal that is still a weighted leaf.
    marginal_values = {key: value(term) for key, term in marginals.items()}
    total = value(prefix[()])

    queries = {(i, j): emit(Product('mass', i, n+j))
               for i, j in product(range(n), repeat=2)}
    outputs = [[], []]
    for i in range(n):
        outputs[0].append(Term(emit(Product('mass', queries[i, i], total)), 0))
    for i, j in combinations(range(n), 2):
        query = emit(Sum('mass', (Term(queries[i, j], 0), Term(queries[j, i], 0))))
        for y in (0, 1):
            outputs[y].append(Term(emit(Product('mass', query,
                                                marginal_values[i, j, y])), 0))
    heads = tuple(emit(Sum('mass', tuple(terms))) for terms in outputs)
    eight = unit
    for _ in range(3):
        eight = emit(Sum('mass', (Term(eight, 0), Term(eight, 0))))
    heads = tuple(emit(Product('mass', head, eight)) for head in heads)
    graph = Program(tuple(nodes), len(worlds)+1, heads)
    graph.validate(rules)
    assert marginal_sums == 7*len(worlds)-7-m*m-5*m
    return rules, graph, worlds


def direct_masses(worlds, weights, query):
    i, j = query
    return tuple(F(1)+8*sum(w for z, w in zip(worlds, weights)
                           if z[i] ^ z[j] == y) for y in (0, 1))


def forward_fixed_gradient(graph, rules, theta, inputs, target):
    """Independent forward dual propagation, not reverse-adjoint reuse."""
    values = []
    derivatives = []
    for node in graph.nodes:
        if type(node) is Source:
            value, derivative = inputs[node.source_id], F(0)
        elif type(node) is Sum:
            value = sum((theta[t.slot]*values[t.parent] for t in node.terms), F(0))
            derivative = sum((theta[t.slot]*derivatives[t.parent]
                + (values[t.parent] if t.slot == 0 else 0) for t in node.terms), F(0))
        else:
            assert type(node) is Product
            value = values[node.left]*values[node.right]
            derivative = (derivatives[node.left]*values[node.right]
                          + values[node.left]*derivatives[node.right])
        values.append(value)
        derivatives.append(derivative)
    masses = tuple(base+values[head] for base, head in zip(rules.base, graph.heads))
    slopes = tuple(derivatives[head] for head in graph.heads)
    return sum(slopes)/sum(masses)-slopes[target]/masses[target]


def checked_prediction(n, rules, graph, worlds, weights, query):
    theta = (F(1),)+weights
    inputs = literal.context(n, *query)
    prediction = evaluate(graph, rules, theta, inputs, (), bit_limit=BITS)
    masses = direct_masses(worlds, weights, query)
    assert prediction.masses == masses and prediction.normalizer == 10
    assert prediction.probabilities == tuple(m/10 for m in masses)
    assert min(prediction.values) >= 0 and max(prediction.values) <= 8
    for target in (0, 1):
        gradient = ce_gradient(graph, theta, prediction, target, bit_limit=BITS)
        selected = tuple(F(4, 5)-F(8*int(z[query[0]] ^ z[query[1]] == target), masses[target])
                         for z in worlds)
        assert gradient[1:] == selected
        assert gradient[0] == forward_fixed_gradient(graph, rules, theta, inputs, target)
        degree = n+4 if n >= 3 else (6 if query[0] == query[1] else 7)
        assert gradient[0] == degree*(1/masses[target]-F(1, 5))
    return prediction


def arbitrary_weight_audit():
    rows = []
    forecasts = gradients = 0
    counterexample = None
    for n in range(2, 6):
        rules, graph, worlds = relation_graph(n)
        old_rules, old_graph, _ = literal.relation_graph(n)
        k = len(worlds)
        positive = tuple(F(i+1, k*(k+1)//2) for i in range(k))
        weights_cases = [(F(1, k),)*k, positive]
        weights_cases += [tuple(F(i == j) for i in range(k)) for j in range(k)]
        for weights in weights_cases:
            for query in product(range(n), repeat=2):
                prediction = checked_prediction(n, rules, graph, worlds, weights, query)
                old = evaluate(old_graph, old_rules, (F(1),)+weights,
                               literal.context(n, *query), (), bit_limit=BITS)
                assert prediction.probabilities == old.probabilities
                for y in (0, 1):
                    old_g = ce_gradient(old_graph, (F(1),)+weights, old, y, bit_limit=BITS)
                    new_g = ce_gradient(graph, (F(1),)+weights, prediction, y, bit_limit=BITS)
                    assert old_g[1:] == new_g[1:]
                    if old_g[0] != new_g[0] and counterexample is None:
                        counterexample = {'n': n, 'weights': list(map(str, weights)),
                            'query': query, 'target': y, 'masses': list(map(str, prediction.masses)),
                            'literal_fixed_gradient': str(old_g[0]),
                            'shared_fixed_gradient': str(new_g[0])}
                forecasts += 1
                gradients += 2
        rows.append({'n': n, 'weight_cases': len(weights_cases), 'ordered_queries': n*n,
                     'shared': graph.counts(), 'literal': old_graph.counts()})
    assert counterexample
    return {'forecasts': forecasts, 'complete_gradient_checks': gradients,
            'fixed_slot_counterexample': counterexample, 'cases': rows}


def history_audit():
    """Compare actual complete new-Program states with an independent oracle."""
    rows = []
    transitions = profiles = 0
    for n, depth in ((2, 3), (3, 2)):
        rules, graph, worlds = relation_graph(n)
        k = len(worlds)
        spec = LearnerSpec(1, F(1), optimizer_id=SIMPLEX_GRADIENT,
                           simplex_slots=tuple(range(1, k+1)))
        initial = initial_state(graph, rules, (F(1),)+(F(1, k),)*k, 0,
                                spec=spec, bit_limit=BITS)
        frontier = [(initial, initial.theta[1:])]
        alphabet = tuple(product(range(n), range(n), (0, 1)))

        def step(state, weights, event):
            nonlocal transitions
            i, j, y = event
            inputs = literal.context(n, i, j)
            prediction = checked_prediction(n, rules, graph, worlds, weights, (i, j))
            masses = direct_masses(worlds, weights, (i, j))
            selected = tuple(F(4, 5)-F(8*int(z[i] ^ z[j] == y), masses[y]) for z in worlds)
            full = (forward_fixed_gradient(graph, rules, state.theta, inputs, y),)+selected
            observed = observe_event(graph, state, spec, prediction, y, bit_limit=BITS)
            expected = ReferenceLearnerState(state.theta, (), full, 1,
                                             state.cursor+1, state.optimizer_steps)
            assert observed == expected
            posterior = tuple(w*F(1+8*int(z[i] ^ z[j] == y), masses[y])
                              for z, w in zip(worlds, weights))
            committed = commit_event(observed, spec, bit_limit=BITS)
            expected = ReferenceLearnerState((F(1),)+posterior, (), (F(0),)*(k+1),
                                             0, state.cursor+1, state.optimizer_steps+1)
            assert committed == expected
            transitions += 1
            return committed, posterior

        for _ in range(depth):
            frontier = [step(state, weights, event) for state, weights in frontier for event in alphabet]
        # Two fixed profile passes, followed by a legal ordinary clock attachment.
        for labels in product((0, 1), repeat=2):
            events = ((0, 1, labels[0]), (1, 0, labels[1]))*2
            state, weights = initial, initial.theta[1:]
            for event in events:
                state, weights = step(state, weights, event)
            attached = attach_boundary(state, 12, spec)
            assert attached == replace(state, cursor=12)
            # Every other coordinate survives the attachment and next actual update.
            step(attached, weights, (0, 1, 1))
            profiles += 1
        rows.append({'n': n, 'exhaustive_depth': depth, 'alphabet': len(alphabet),
                     'histories_at_maximum_depth': len(frontier)})
    return {'native_observe_commit_pairs': transitions, 'two_pass_profile_cases': profiles,
            'complete_state_checks': 2*transitions, 'cases': rows}


def circuit_counts():
    rows = []
    for n in (2, 3, 4, 5, 8, 12, 16):
        rules, graph, worlds = relation_graph(n)
        k, m = len(worlds), n-1
        a = 7*k-7-m*m-5*m
        c = graph.counts()
        extra = 2 if n == 2 else 0
        assert c['SUMs'] == a+n*(n-1)//2+6+extra
        assert c['PRODUCTs'] == 2*n*n+2
        assert c['SUM_edges'] == 2*a+2*n*n+6+extra
        slots = k+1
        # Actual registered generic output-cell schedule, no execution claim.
        predict = slots+4*n+1+c['PRODUCTs']+3*c['SUM_edges']+c['SUMs']+c['nodes']+12
        observe = 8+c['nodes']+3*slots+4*(c['SUM_edges']+c['PRODUCTs'])
        spec = LearnerSpec(1, F(1), optimizer_id=SIMPLEX_GRADIENT,
                           simplex_slots=tuple(range(1, slots)))
        assert predict == output_cells('predict', graph, rules, spec)
        assert observe == output_cells('observe', graph, rules, spec)
        rows.append({'n': n, 'worlds': k, 'shared': c,
            'literal_nodes': 2*n+n*n+2*k+2,
            'literal_edges': k*(n*n+16)+2*n*n,
            'shared_predict_output_cells': predict, 'shared_observe_output_cells': observe,
            'literal_predict_output_cells': k*(3*n*n+53)+2*n*n+6*n+18,
            'literal_observe_output_cells': k*(4*n*n+69)+5*n*n+2*n+13})
    return rows


def scope_audit():
    # Typed source ranges alone do not imply the one-hot source identity.
    n = 3
    rules, graph, worlds = relation_graph(n)
    old_rules, old_graph, _ = literal.relation_graph(n)
    theta = (F(1),)+(F(1, len(worlds)),)*len(worlds)
    inputs = literal.context(n, 0, 0)
    inputs['x0:1'] = F(1)
    new = evaluate(graph, rules, theta, inputs, (), bit_limit=BITS)
    old = evaluate(old_graph, old_rules, theta, inputs, (), bit_limit=BITS)
    assert new.probabilities != old.probabilities
    # Every pair of unread coordinates has an observable anchor-query witness.
    # These are independent simplex weights, not a reachable-history lower bound.
    witnesses = 0
    for n in range(2, 6):
        worlds = tuple((0,)+z for z in product((0, 1), repeat=n-1))
        k = len(worlds)
        weights = (F(1, k),)*k
        for a, b in combinations(range(k), 2):
            j = next(j for j in range(1, n) if worlds[a][j] != worlds[b][j])
            changed = list(weights)
            changed[a] += F(1, 2*k)
            changed[b] -= F(1, 2*k)
            assert min(changed) > 0 and sum(changed) == 1
            assert direct_masses(worlds, weights, (0, j)) != direct_masses(worlds, changed, (0, j))
            assert all(changed[c] == weights[c] for c in range(k) if c not in (a, b))
            witnesses += 1
    return {'unread_pair_witnesses': witnesses,
        'source_range_without_one_hot_counterexample': {
            'n': 3, 'active_sources': ['x0:0', 'x0:1', 'x1:0'],
            'literal_probabilities': list(map(str, old.probabilities)),
            'shared_probabilities': list(map(str, new.probabilities))},
        'lower_bound_scope': 'independent simplex coordinates in an explicit-slot circuit; not encoded histories',
        'complete_learner_equivalence_claimed': False,
        'runtime_reachability_or_GPU_execution_claimed': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = {'status': 'PASS', 'scope': 'exact passive native Program construction; no Runtime certificate',
        'arithmetic': 'fractions.Fraction with 32768-bit registered exact operation bound',
        'arbitrary_weights': arbitrary_weight_audit(), 'learner': history_audit(),
        'circuit_counts': circuit_counts(), 'scope_checks': scope_audit()}
    raw = json.dumps(result, indent=2)+'\n'
    if args.output:
        args.output.write_text(raw, encoding='utf-8')
    else:
        print(raw, end='')


if __name__ == '__main__':
    main()
