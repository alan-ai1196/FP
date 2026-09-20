"""Exact passive audit of PRODUCT beliefs under the existing native simplex U.

These are ordinary positive Programs with their own complete learner states.
No Runtime candidate, resource certificate, AMP bridge or installation is issued.
"""
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json
import math
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(Path(__file__).resolve().parent)]
from fp_reference.learner import (SIMPLEX_GRADIENT, LearnerSpec, ReferenceLearnerState,
    initial_state, ce_gradient, observe_event, commit_event)
from fp_reference.profile import attach_boundary
from fp_reference.program import Product, Program, SemanticRules, Source, SourceSpec, Sum, Term
from fp_reference.semantics import evaluate
from positive_pair_marginals import forward_fixed_gradient

BITS = 32768


def factors_to_theta(factors):
    m = len(factors)
    assert m and all(sum(q) == 1 and min(q) >= 0 for q in factors)
    return (F(1),)+tuple(x/m for q in factors for x in q)


def worlds_for(sizes):
    return tuple(product(*(range(k) for k in sizes)))


def joint_weights(factors, worlds):
    return tuple(math.prod(q[z[j]] for j, q in enumerate(factors)) for z in worlds)


def marginals(weights, worlds, sizes):
    return tuple(tuple(sum((w for w, z in zip(weights, worlds) if z[j] == b), F(0))
                       for b in range(k)) for j, k in enumerate(sizes))


def posterior(weights, table, target, base):
    raw = tuple(w*(base[target]+c[target]) for w, c in zip(weights, table))
    return tuple(w/sum(raw) for w in raw)


def spec_for(graph, m, rate=None):
    return LearnerSpec(1, F(1, m) if rate is None else rate,
                      optimizer_id=SIMPLEX_GRADIENT,
                      simplex_slots=tuple(range(1, graph.slot_count)))


def tensor_graph(sizes, table, base=(F(1), F(1))):
    """Small explicit tensor oracle graph; integer coefficients are SUM edges."""
    worlds = worlds_for(sizes)
    assert len(table) == len(worlds)
    assert all(len(c) == len(base) and all(type(a) is int and a >= 0 for a in c)
               for c in table)
    rules = SemanticRules((SourceSpec('one', 'mass', 0, F(1)),), ('mass',),
                          (('mass', 'mass', 'mass'),), 'mass', base)
    nodes = [Source('one')]

    def emit(node):
        nodes.append(node)
        return len(nodes)-1

    scale = emit(Sum('mass', (Term(0, 0),)*len(sizes)))
    slot = 1
    leaves = []
    for k in sizes:
        leaves.append(tuple(emit(Sum('mass', (Term(scale, b),)))
                            for b in range(slot, slot+k)))
        slot += k
    monomials = []
    for z in worlds:
        value = leaves[0][z[0]]
        for j in range(1, len(sizes)):
            value = emit(Product('mass', value, leaves[j][z[j]]))
        monomials.append(value)
    heads = tuple(emit(Sum('mass', tuple(Term(v, 0) for v, c in zip(monomials, table)
                                        for _ in range(c[y])))) for y in range(len(base)))
    graph = Program(tuple(nodes), slot, heads)
    graph.validate(rules)
    return rules, graph, worlds


def single_factor_graph(m, *, keep_normalizers=True):
    """Linear-size native graph for noisy queries of one binary factor at a time.

    Constants m and 8 are constructed from the complete one-hot query sources.
    The negative-control graph removes the inactive block sums, not parameters.
    """
    assert type(m) is int and m >= 1
    sources = tuple(SourceSpec(f'query:{j}', 'mass', 0, F(1)) for j in range(m))
    rules = SemanticRules(sources, ('mass',), (('mass', 'mass', 'mass'),),
                          'mass', (F(1), F(1)))
    nodes = [Source(s.source_id) for s in sources]

    def emit(node):
        nodes.append(node)
        return len(nodes)-1

    unit = emit(Sum('mass', tuple(Term(j, 0) for j in range(m))))
    scale = emit(Sum('mass', (Term(unit, 0),)*m))
    leaves = [tuple(emit(Sum('mass', (Term(scale, 1+2*j+b),))) for b in (0, 1))
              for j in range(m)]
    others = None
    if keep_normalizers:
        sums = [emit(Sum('mass', tuple(Term(v, 0) for v in row))) for row in leaves]
        prefix = [unit]
        for s in sums:
            prefix.append(emit(Product('mass', prefix[-1], s)))
        suffix = [unit]*(m+1)
        for j in reversed(range(m)):
            suffix[j] = emit(Product('mass', sums[j], suffix[j+1]))
        others = [emit(Product('mass', prefix[j], suffix[j+1])) for j in range(m)]
    outputs = [[], []]
    for j in range(m):
        for b in (0, 1):
            value = leaves[j][b]
            if others is not None:
                value = emit(Product('mass', value, others[j]))
            value = emit(Product('mass', j, value))
            outputs[b].append(Term(value, 0))
    heads = tuple(emit(Sum('mass', tuple(terms))) for terms in outputs)
    eight = unit
    for _ in range(3):
        eight = emit(Sum('mass', (Term(eight, 0), Term(eight, 0))))
    heads = tuple(emit(Product('mass', head, eight)) for head in heads)
    graph = Program(tuple(nodes), 2*m+1, heads)
    graph.validate(rules)
    return rules, graph


def query_input(m, j):
    return {f'query:{i}': F(i == j) for i in range(m)}


def query_table(worlds, j):
    return tuple(tuple(8*int(z[j] == y) for y in (0, 1)) for z in worlds)


def checked_step(rules, graph, state, spec, inputs, factors, worlds, table, target):
    """Check native gradients and both complete state boundaries independently."""
    m, sizes = len(factors), tuple(map(len, factors))
    assert state.theta == factors_to_theta(factors)
    totals = tuple(map(sum, table))
    assert len(set(totals)) == 1
    c = totals[0]
    weights = joint_weights(factors, worlds)
    masses = tuple(b+sum(w*col[y] for w, col in zip(weights, table))
                   for y, b in enumerate(rules.base))
    prediction = evaluate(graph, rules, state.theta, inputs, (), bit_limit=BITS)
    assert prediction.masses == masses
    assert prediction.normalizer == sum(rules.base)+c
    assert prediction.probabilities == tuple(a/sum(masses) for a in masses)
    selected = []
    for j, k in enumerate(sizes):
        for b in range(k):
            conditional = sum((col[target]*math.prod(factors[i][z[i]]
                              for i in range(m) if i != j)
                              for z, col in zip(worlds, table) if z[j] == b), F(0))
            selected.append(m*(F(c, sum(masses))-conditional/masses[target]))
    fixed = forward_fixed_gradient(graph, rules, state.theta, inputs, target)
    gradient = (fixed,)+tuple(selected)
    assert ce_gradient(graph, state.theta, prediction, target, bit_limit=BITS) == gradient
    observed = observe_event(graph, state, spec, prediction, target, bit_limit=BITS)
    assert observed == ReferenceLearnerState(state.theta, (), gradient, 1,
                                             state.cursor+1, state.optimizer_steps)
    exact_joint = posterior(weights, table, target, rules.base)
    updated = marginals(exact_joint, worlds, sizes)
    committed = commit_event(observed, spec, bit_limit=BITS)
    assert committed == ReferenceLearnerState(factors_to_theta(updated), (),
        (F(0),)*graph.slot_count, 0, state.cursor+1, state.optimizer_steps+1)
    return committed, updated, exact_joint


def tensor_audit():
    rows = []
    checks = 0
    for sizes in ((2,), (2, 2), (2, 3), (2, 2, 2), (2, 3, 2)):
        worlds = worlds_for(sizes)
        tables = [tuple((8*int(sum(z) % 2 == 0), 8*int(sum(z) % 2 == 1)) for z in worlds),
                  tuple((k % 9, 8-k % 9) for k in range(len(worlds))),
                  tuple((k % 3, (2*k+1) % 3, 6-k % 3-(2*k+1) % 3)
                        for k in range(len(worlds)))]
        priors = [tuple(tuple(F(1, k) for _ in range(k)) for k in sizes),
                  tuple(tuple(F(b+1, k*(k+1)//2) for b in range(k)) for k in sizes)]
        # All vertices audit zero coordinates without dividing by a marginal.
        priors += [tuple(tuple(F(b == z[j]) for b in range(k))
                         for j, k in enumerate(sizes)) for z in worlds]
        for table in tables:
            base = tuple(F(1+y, 2) for y in range(len(table[0])))
            rules, graph, _ = tensor_graph(sizes, table, base)
            spec = spec_for(graph, len(sizes))
            for factors in priors:
                state = initial_state(graph, rules, factors_to_theta(factors), 0,
                                      spec=spec, bit_limit=BITS)
                for target in range(len(base)):
                    checked_step(rules, graph, state, spec, {'one': F(1)},
                                 factors, worlds, table, target)
                    checks += 1
        rows.append({'factor_sizes': sizes, 'prior_cases': len(priors),
                     'tables': len(tables), 'targets_per_prior': 7})
    return {'native_marginal_updates': checks, 'complete_state_checks': 2*checks,
            'cases': rows}


def factorization_boundary_audit():
    """Exhaust all small likelihood tensors, testing closure via independent minors."""
    rows = []
    for sizes, levels in (((2, 2), (0, 1, 2)), ((2, 2, 2), (0, 8))):
        worlds = worlds_for(sizes)
        checks = separable = 0
        for first_column in product(levels, repeat=len(worlds)):
            table = tuple((a, max(levels)-a) for a in first_column)
            rules, graph, _ = tensor_graph(sizes, table)
            spec = spec_for(graph, len(sizes))
            for target in (0, 1):
                likelihood = {z: F(1+c[target]) for z, c in zip(worlds, table)}
                # Every two-by-two minor of every single-factor flattening.
                rank_one = True
                for j in range(len(sizes)):
                    pairs = [(likelihood[z], likelihood[z[:j]+(1,)+z[j+1:]])
                             for z in worlds if z[j] == 0]
                    rank_one &= all(a*d == b*c for a, b in pairs for c, d in pairs)
                for factors in (tuple((F(1, 2), F(1, 2)) for _ in sizes),
                                tuple((F(j+1, 2*j+3), F(j+2, 2*j+3))
                                      for j in range(len(sizes)))):
                    state = initial_state(graph, rules, factors_to_theta(factors), 0,
                                          spec=spec, bit_limit=BITS)
                    _, updated, exact = checked_step(rules, graph, state, spec,
                        {'one': F(1)}, factors, worlds, table, target)
                    assert (joint_weights(updated, worlds) == exact) == rank_one
                    checks += 1
                    separable += int(rank_one)
        rows.append({'factor_sizes': sizes, 'coefficient_levels': levels,
                     'complete_tables': len(levels)**len(worlds),
                     'native_updates_and_closure_checks': checks,
                     'factorized_posteriors': separable,
                     'correlated_posteriors': checks-separable})
    return {'cases': rows, 'native_updates': sum(r['native_updates_and_closure_checks'] for r in rows)}


def rate_audit():
    checks = 0
    for m in (1, 2, 3):
        rules, graph = single_factor_graph(m)
        worlds = worlds_for((2,)*m)
        factors = tuple((F(1, 3), F(2, 3)) for _ in range(m))
        for eta in (F(0), F(1, 2*m), F(1, m)):
            spec = spec_for(graph, m, eta)
            state = initial_state(graph, rules, factors_to_theta(factors), 0,
                                  spec=spec, bit_limit=BITS)
            for j, y in product(range(m), (0, 1)):
                prediction = evaluate(graph, rules, state.theta, query_input(m, j), (), bit_limit=BITS)
                committed = commit_event(observe_event(graph, state, spec, prediction, y, bit_limit=BITS),
                                         spec, bit_limit=BITS)
                exact = posterior(joint_weights(factors, worlds), query_table(worlds, j), y, rules.base)
                posterior_factors = marginals(exact, worlds, (2,)*m)
                expected = tuple(tuple((1-m*eta)*a+m*eta*b for a, b in zip(q, new))
                                 for q, new in zip(factors, posterior_factors))
                assert committed.theta == factors_to_theta(expected)
                assert (expected == posterior_factors) == (eta == F(1, m))
                checks += 1
    return {'native_damped_marginal_updates': checks,
            'informative_exact_Bayes_rate': '1/m; other tested rates give the derived damping'}


def history_audit():
    checks = profiles = 0
    rows = []
    for m, depth in ((1, 3), (2, 4), (3, 3)):
        rules, graph = single_factor_graph(m)
        worlds = worlds_for((2,)*m)
        spec = spec_for(graph, m)
        for prior in (tuple((F(1, 2), F(1, 2)) for _ in range(m)),
                      tuple((F(j+1, 2*j+3), F(j+2, 2*j+3)) for j in range(m))):
            initial = initial_state(graph, rules, factors_to_theta(prior), 0,
                                    spec=spec, bit_limit=BITS)
            frontier = [(initial, prior, joint_weights(prior, worlds))]

            def step(state, factors, full_posterior, j, y):
                nonlocal checks
                table = query_table(worlds, j)
                next_state, next_factors, current_posterior = checked_step(
                    rules, graph, state, spec, query_input(m, j), factors, worlds, table, y)
                history_posterior = posterior(full_posterior, table, y, rules.base)
                assert current_posterior == history_posterior
                assert joint_weights(next_factors, worlds) == history_posterior
                checks += 1
                return next_state, next_factors, history_posterior

            for _ in range(depth):
                frontier = [step(*item, j, y) for item in frontier
                            for j, y in product(range(m), (0, 1))]
            state, factors, full = initial, prior, joint_weights(prior, worlds)
            for j, y in ((0, 0), (m-1, 1))*2:
                state, factors, full = step(state, factors, full, j, y)
            attached = attach_boundary(state, 12, spec)
            assert attached == replace(state, cursor=12)
            step(attached, factors, full, 0, 1)
            profiles += 1
        rows.append({'factors': m, 'exhaustive_depth': depth, 'event_alphabet': 2*m,
                     'priors': 2, 'terminal_histories_per_prior': (2*m)**depth})
    return {'native_observe_commit_pairs': checks, 'complete_state_checks': 2*checks,
            'two_pass_profile_cases': profiles, 'cases': rows}


def correlation_counterexample():
    sizes = (2, 2)
    worlds = worlds_for(sizes)
    table = tuple((8*int(z[0] == z[1]), 8*int(z[0] != z[1])) for z in worlds)
    rules, graph, _ = tensor_graph(sizes, table)
    factors = ((F(1, 2), F(1, 2)),)*2
    spec = spec_for(graph, 2)
    state = initial_state(graph, rules, factors_to_theta(factors), 0,
                          spec=spec, bit_limit=BITS)
    state, updated, exact = checked_step(rules, graph, state, spec, {'one': F(1)},
                                         factors, worlds, table, 0)
    assert updated == factors and joint_weights(updated, worlds) != exact
    prediction = evaluate(graph, rules, state.theta, {'one': F(1)}, (), bit_limit=BITS)
    true_next = sum(w*F(1+c[0], 10) for w, c in zip(exact, table))
    assert prediction.probabilities[0] == F(1, 2) and true_next == F(41, 50)
    assert ce_gradient(graph, state.theta, prediction, 0, bit_limit=BITS) == (F(0),)*5
    return {'exact_joint_posterior': list(map(str, exact)),
            'native_next_probability': str(prediction.probabilities[0]),
            'whole_history_Bayes_next_probability': str(true_next),
            'complete_gradient_is_zero': True, 'no_learning_rate_can_repair_this_step': True}


def erasure_counterexample():
    m = 2
    factors = ((F(1, 2), F(1, 2)),)*m
    runs = []
    for keep in (True, False):
        rules, graph = single_factor_graph(m, keep_normalizers=keep)
        spec = spec_for(graph, m)
        state = initial_state(graph, rules, factors_to_theta(factors), 0,
                              spec=spec, bit_limit=BITS)
        gradients, forecasts, states = [], [], []
        for _ in range(2):
            prediction = evaluate(graph, rules, state.theta, query_input(m, 0), (), bit_limit=BITS)
            forecasts.append(prediction.probabilities[0])
            gradients.append(ce_gradient(graph, state.theta, prediction, 0, bit_limit=BITS))
            state = commit_event(observe_event(graph, state, spec, prediction, 0, bit_limit=BITS),
                                 spec, bit_limit=BITS)
            states.append(state)
        final = evaluate(graph, rules, state.theta, query_input(m, 0), (), bit_limit=BITS)
        runs.append((states, gradients, forecasts, final.probabilities[0]))
    intact, stripped = runs
    assert intact[2] == stripped[2] == [F(1, 2), F(41, 50)]
    assert intact[0][0] == stripped[0][0]
    assert intact[1][1][1:] != stripped[1][1][1:]
    assert sum(intact[0][-1].theta[3:]) == F(1, 2)
    assert sum(stripped[0][-1].theta[3:]) != F(1, 2)
    assert intact[3] == F(73, 82) and intact[3] != stripped[3]
    return {'identical_first_two_forecasts': list(map(str, intact[2])),
            'identical_first_complete_commit': True,
            'third_intact_probability': str(intact[3]),
            'third_erased_probability': str(stripped[3]),
            'intact_block_masses': ['1/2', '1/2'],
            'erased_block_masses': [str(sum(stripped[0][-1].theta[1:3])),
                                     str(sum(stripped[0][-1].theta[3:]))],
            'second_selected_gradients_intact': list(map(str, intact[1][1][1:])),
            'second_selected_gradients_erased': list(map(str, stripped[1][1][1:]))}


def counts_audit():
    rows = []
    for m in (1, 2, 3, 8, 16, 32, 64):
        _, graph = single_factor_graph(m)
        counts = graph.counts()
        assert counts['nodes'] == 11*m+9
        assert counts['SUMs'] == 3*m+7 and counts['PRODUCTs'] == 7*m+2
        assert counts['SUM_edges'] == 8*m+6 and counts['edges'] == 22*m+10
        assert graph.slot_count == 2*m+1
        rows.append({'factors': m, 'represented_joint_worlds': 2**m, 'native': counts})
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = {'status': 'PASS', 'arithmetic': 'exact Fraction; guarded native bound 32768 bits',
              'scope': 'passive native Programs; no Runtime or AMP authority',
              'tensor_marginal_audit': tensor_audit(),
              'factorization_boundary_audit': factorization_boundary_audit(),
              'rate_audit': rate_audit(),
              'factorized_history_audit': history_audit(),
              'correlation_counterexample': correlation_counterexample(),
              'value_one_erasure_counterexample': erasure_counterexample(),
              'actual_graph_counts': counts_audit()}
    payload = json.dumps(result, indent=2)+'\n'
    if args.output:
        args.output.write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()
