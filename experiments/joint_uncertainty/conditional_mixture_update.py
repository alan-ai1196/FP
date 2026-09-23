"""Conditional posterior closure versus the actual native simplex update.

Positive native graphs, full gradients and separate exact joint controls.
No Runtime, new optimizer, installed decoder or GPU authority is supplied.
"""
from fractions import Fraction as F
from itertools import product
from math import lcm, prod
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(Path(__file__).parent)]
from fp_reference.program import Program, Product, Source, SourceSpec, Sum, Term, SemanticRules
from fp_reference import float64_learner as f64
from fp_reference.binary_arithmetic import Float64Arithmetic
from fp_reference.float64_bridge import Float64Contract, check_state, check_prediction
import factor_simplex_posterior as native
import likelihood_information as flat

BITS = 32768
RATES = (F(1, 10), F(1, 4))
OUTPUT = ROOT/'evidence/minimal/FP_CONDITIONAL_MIXTURE_UPDATE.json'


def graph_for(rates, bits):
    """SUM of conditional PRODUCTs, retaining every inactive block sum."""
    rows = len(rates)*bits
    sizes = (len(rates),)+(2,)*rows
    blocks = len(sizes)
    scale = lcm(*(eta.denominator for eta in rates))
    sources = tuple(SourceSpec(f'query:{i}', 'mass', 0, F(1)) for i in range(bits+1))
    rules = SemanticRules(sources, ('mass',), (('mass', 'mass', 'mass'),), 'mass', (F(1), F(1)))
    nodes = [Source(s.source_id) for s in sources]
    def emit(node):
        nodes.append(node)
        return len(nodes)-1
    unit = emit(Sum('mass', tuple(Term(i, 0) for i in range(bits+1))))
    multiplier = emit(Sum('mass', (Term(unit, 0),)*blocks))
    leaves, slot = [], 1
    for size in sizes:
        leaves.append(tuple(emit(Sum('mass', (Term(multiplier, i),))) for i in range(slot, slot+size)))
        slot += size
    sums = [emit(Sum('mass', tuple(Term(v, 0) for v in row))) for row in leaves[1:]]
    prefix = [unit]
    for value in sums:
        prefix.append(emit(Product('mass', prefix[-1], value)))
    suffix = [unit]*(rows+1)
    for i in reversed(range(rows)):
        suffix[i] = emit(Product('mass', sums[i], suffix[i+1]))
    others = [emit(Product('mass', prefix[i], suffix[i+1])) for i in range(rows)]
    outputs = [[], []]
    for j, eta in enumerate(rates):
        for query in range(bits+1):
            for value in ((0,) if query == bits else (0, 1)):
                feature = prefix[-1] if query == bits else emit(Product('mass',
                    leaves[1+j*bits+query][value], others[j*bits+query]))
                feature = emit(Product('mass', leaves[0][j], feature))
                feature = emit(Product('mass', query, feature))
                for target in (0, 1):
                    likelihood = 1-eta if value == target else eta
                    coefficient = scale*likelihood-1
                    assert coefficient.denominator == 1 and coefficient >= 0
                    outputs[target].extend((Term(feature, 0),)*int(coefficient))
    heads = tuple(emit(Sum('mass', tuple(row))) for row in outputs)
    graph = Program(tuple(nodes), slot, heads)
    graph.validate(rules)
    return rules, graph, sizes, scale


def inputs(bits, query):
    return {f'query:{i}': F(i == query) for i in range(bits+1)}


def likelihood(eta, value, target):
    return 1-eta if value == target else eta


def exact_conditional(factors, rates, bits, query, target):
    pi = factors[0]
    means = tuple(likelihood(eta, 0, target) if query == bits else
                  sum(q*likelihood(eta, value, target) for value, q in
                      enumerate(factors[1+j*bits+query])) for j, eta in enumerate(rates))
    probability = sum(p*m for p, m in zip(pi, means))
    rho = tuple(p*m/probability for p, m in zip(pi, means))
    after = list(factors)
    after[0] = rho
    if query < bits:
        for j, eta in enumerate(rates):
            index = 1+j*bits+query
            after[index] = tuple(q*likelihood(eta, value, target)/means[j]
                                 for value, q in enumerate(factors[index]))
    return tuple(after), probability, means


def represented_joint(factors, bits):
    return tuple(p*prod(factors[1+j*bits+k][z[k]] for k in range(bits))
                 for j, p in enumerate(factors[0]) for z in product((0, 1), repeat=bits))


def checked_step(bundle, state, factors, rates, bits, query, target, alpha=F(1)):
    rules, graph, sizes, scale = bundle
    blocks = len(sizes)
    spec = native.spec_for(graph, blocks, alpha/blocks)
    source = inputs(bits, query)
    assert state.theta == native.factors_to_theta(factors)
    worlds = native.worlds_for(sizes)
    table = tuple(tuple(int(scale*likelihood(rates[z[0]], 0 if query == bits else
                    z[1+z[0]*bits+query], y))-1 for y in (0, 1)) for z in worlds)
    weights = native.joint_weights(factors, worlds)
    prediction = native.evaluate(graph, rules, state.theta, source, (), bit_limit=BITS)
    masses = tuple(1+sum(w*c[y] for w, c in zip(weights, table)) for y in (0, 1))
    assert prediction.masses == masses and prediction.normalizer == scale
    assert prediction.probabilities == tuple(v/scale for v in masses)
    exact, probability, means = exact_conditional(factors, rates, bits, query, target)
    assert prediction.probabilities[target] == probability
    selected = []
    for j, size in enumerate(sizes):
        for value in range(size):
            coefficient = sum(c[target]*prod(factors[i][z[i]] for i in range(blocks) if i != j)
                              for z, c in zip(worlds, table) if z[j] == value)
            selected.append(blocks*(F(scale-2, scale)-coefficient/masses[target]))
    fixed = native.forward_fixed_gradient(graph, rules, state.theta, source, target)
    gradient = (fixed,)+tuple(selected)
    observed = native.observe_event(graph, state, spec, prediction, target, bit_limit=BITS)
    assert observed == native.ReferenceLearnerState(state.theta, (), gradient, 1, state.cursor+1, state.optimizer_steps)
    posterior = native.posterior(weights, table, target, rules.base)
    marginals = native.marginals(posterior, worlds, sizes)
    updated = tuple(tuple((1-alpha)*a+alpha*b for a, b in zip(row, post))
                    for row, post in zip(factors, marginals))
    formula = list(factors)
    formula[0] = tuple((1-alpha)*a+alpha*b for a, b in zip(factors[0], exact[0]))
    if query < bits:
        for j, rho in enumerate(exact[0]):
            index = 1+j*bits+query
            formula[index] = tuple(a+alpha*rho*(b-a) for a, b in zip(factors[index], exact[index]))
    assert updated == tuple(formula)
    committed = native.commit_event(observed, spec, bit_limit=BITS)
    assert committed == native.ReferenceLearnerState(native.factors_to_theta(updated), (),
        (F(0),)*graph.slot_count, 0, state.cursor+1, state.optimizer_steps+1)
    if alpha == 1:
        gap = exact_conditional(exact, rates, bits, query, target)[1]-exact_conditional(updated, rates, bits, query, target)[1]
        wanted = F(0) if query == bits else sum(rho*(1-rho)*sum(q*(likelihood(eta, value, target)-mean)**2
                    for value, q in enumerate(factors[1+j*bits+query]))/mean
                    for j, (eta, mean, rho) in enumerate(zip(rates, means, exact[0])))
        assert gap == wanted and (gap == 0 if query == bits else gap > 0)
    return committed, updated, prediction, observed


def one_step_audit():
    reports = []
    for rates, bits in ((RATES, 1), (RATES, 2), ((F(1, 10), F(1, 5), F(3, 10)), 1)):
        bundle = graph_for(rates, bits)
        rules, graph, sizes, _ = bundle
        biases = tuple(product((F(1, 4), F(1, 2), F(3, 4)), repeat=len(rates))) if bits == 1 else (
            (F(1, 2),)*4, (F(1, 4),)*4, (F(3, 4),)*4, (F(1, 4), F(1, 2), F(3, 4), F(1, 4)))
        priors = ((F(1, len(rates)),)*len(rates), tuple(F(j+1, len(rates)*(len(rates)+1)//2) for j in range(len(rates))))
        checked = 0
        for prior, bias in product(priors, biases):
            factors = (prior,)+tuple((v, 1-v) for v in bias)
            state = native.initial_state(graph, rules, native.factors_to_theta(factors), 0,
                                          spec=native.spec_for(graph, len(sizes)), bit_limit=BITS)
            for query, target, alpha in product(range(bits+1), (0, 1), (F(1, 2), F(1))):
                checked_step(bundle, state, factors, rates, bits, query, target, alpha)
                checked += 1
        reports.append({'rates': tuple(map(str, rates)), 'conditional_binary_factors': bits,
                        'native_graph': graph.counts(), 'complete_native_triples': checked})
    return reports


def closure_control():
    rates, bits = RATES, 2
    worlds = tuple((j, z) for j in range(len(rates)) for z in product((0, 1), repeat=bits))
    initial = ((F(1, 2),)*2,)+( (F(1, 2),)*2,)*(len(rates)*bits)
    table = tuple(tuple(tuple(likelihood(rates[j], 0 if query == bits else z[query], y)
                              for j, z in worlds) for y in (0, 1)) for query in range(bits+1))
    bank = flat.Model(table, represented_joint(initial, bits))
    bundle = flat.native_graph(bank)
    rules, graph, spec, _ = bundle
    state = native.initial_state(graph, rules, (F(1),)+bank.prior, 0, spec=spec, bit_limit=BITS)
    levels = [(state, initial)]
    checked = 0
    for _ in range(3):
        following = []
        for state, factors in levels:
            for query, target in bank.events:
                exact, p, _ = exact_conditional(factors, rates, bits, query, target)
                assert p == bank.forecast(state.theta[1:], (query, target))
                after = flat.native_step(bank, bundle, state, (query, target))
                assert after.theta[1:] == represented_joint(exact, bits)
                following.append((after, exact))
                checked += 1
        levels = following
    return {'conditional_binary_factors': bits, 'all_three_event_prefixes': checked,
            'complete_exact_joint_native_triples': checked, 'native_graph': graph.counts()}


def witnesses():
    bundle = graph_for(RATES, 1)
    rules, graph, sizes, _ = bundle
    initial = ((F(1, 2),)*2,)*3
    reports = []
    numerical = Float64Contract(F(1, 10**10), F(1, 10**10))
    for alpha, count in ((F(1), 1), (F(2), 2)):
        spec = native.spec_for(graph, len(sizes), alpha/len(sizes))
        state = native.initial_state(graph, rules, native.factors_to_theta(initial), 0, spec=spec, bit_limit=BITS)
        arithmetic = Float64Arithmetic(BITS)
        floating = f64.initialize(graph, rules, state.theta, 0, arithmetic)
        current = truth = initial
        errors, phases = [check_state(state, floating, numerical, bit_limit=BITS).state_error], 1
        for _ in range(count):
            state, current, p, observed = checked_step(bundle, state, current, RATES, 1, 0, 0, alpha)
            truth, _, _ = exact_conditional(truth, RATES, 1, 0, 0)
            fp = f64.evaluate(graph, rules, floating, inputs(1, 0), arithmetic)
            rel = check_prediction(p, fp, numerical, rules, normalizer_cap=F(21), activation_cap=F(20), bit_limit=BITS)
            fo = f64.observe_event(graph, floating, spec, fp, 0, arithmetic)
            ro = check_state(observed, fo, numerical, bit_limit=BITS)
            floating = f64.commit_event(fo, spec, arithmetic)
            rc = check_state(state, floating, numerical, bit_limit=BITS)
            errors.extend((rel.native_error, rel.normalizer_error, rel.probability_error, ro.state_error, rc.state_error))
            phases += 3
        exact_prediction = native.evaluate(graph, rules, state.theta, inputs(1, 0), (), bit_limit=BITS)
        fp = f64.evaluate(graph, rules, floating, inputs(1, 0), arithmetic)
        relation = check_prediction(exact_prediction, fp, numerical, rules, normalizer_cap=F(21), activation_cap=F(20), bit_limit=BITS)
        errors.extend((relation.native_error, relation.normalizer_error, relation.probability_error))
        phases += 1
        actual = exact_prediction.probabilities[0]
        correct = exact_conditional(truth, RATES, 1, 0, 0)[1]
        if alpha == 1:
            assert actual == F(489, 800) and correct == F(289, 400) and correct-actual == F(89, 800)
            assert current[0] == truth[0] == (F(1, 2), F(1, 2))
        else:
            assert current[0] == (F(367, 578), F(211, 578))
            assert truth[0] == (F(164, 289), F(125, 289))
            assert current[0] != truth[0]
        reports.append({'rate': str(spec.learning_rate), 'ordinary_events': count,
                        'native_factors': [[str(v) for v in row] for row in current],
                        'exact_conditional_factors': [[str(v) for v in row] for row in truth],
                        'next_native_forecast': str(actual), 'next_exact_forecast': str(correct),
                        'signed_exact_minus_native': str(correct-actual),
                        'binary64_phases': phases, 'maximum_binary64_relation_error': str(max(errors))})
    # Tangent requirements for ANY ambient extension of this conditional law.
    truth1, _, _ = exact_conditional(initial, RATES, 1, 0, 0)
    truth2, _, means = exact_conditional(truth1, RATES, 1, 0, 0)
    assert means == (F(41, 50), F(5, 8)) and len(set(means)) == 2
    rate = F(1, 2)  # Forced by first-event conditional rows and second-event gate.
    required = tuple(rate*rho for rho in truth2[0])
    assert required != (F(1, 4), F(1, 4))
    return {'native': reports, 'fixed_block_mass_contradiction': {
        'forced_common_rate': str(rate), 'forced_gate_mass': '1/2',
        'first_event_required_conditional_masses': ['1/4', '1/4'],
        'second_event_required_conditional_masses': tuple(map(str, required))}}


def run():
    result = {'status': 'PASS', 'precision': 'exact Fraction native guard32768; independent executed binary64',
              'one_step': one_step_audit(), 'exact_conditional_closure': closure_control(), 'witnesses': witnesses(),
              'scope': 'Fixed block-scaled conditional-mixture parameters and one global native simplex step. No impossibility for all encodings, Foundation change, Runtime certificate or GPU/model performance claim.'}
    assert 'torch' not in sys.modules
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    encoded = json.dumps(run(), indent=2)+'\n'
    if args.write:
        OUTPUT.write_text(encoded, encoding='utf-8')
    print(encoded)
