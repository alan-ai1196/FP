"""Exact acquisition-prefix and unknown-noise forecast-hardness audit.

No supplied noise posterior, discarded rate, Runtime authority or GPU job.
All graph branching explores every decision consistent with the error promise.
"""
from fractions import Fraction as F
from itertools import combinations, product
from math import lcm
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(Path(__file__).parent)]
from fp_reference.learner import initial_state
import noise_acquisition as native

OUTPUT = ROOT/'evidence/minimal/FP_UNKNOWN_NOISE_DECODING.json'
DEFAULT = ((F(1, 10), F(1, 4)), (F(1, 2), F(1, 2)))
OTHER = ((F(1, 8), F(1, 5), F(1, 3)), (F(1, 7), F(2, 7), F(4, 7)))


def calibrated(rates, prior, horizon, delta):
    assert tuple(sorted(rates)) == rates and len(set(rates)) == len(rates)
    assert len(rates) >= 2 and all(0 < p < F(1, 2) for p in rates)
    assert len(prior) == len(rates) and min(prior) > 0 and sum(prior) == 1
    assert type(horizon) is int and horizon >= 0 and 0 < delta < 1
    q = (1-rates[1])/(1-rates[0])
    limit = delta/(1-delta)*rates[0]**horizon
    odds = (1-prior[0])/prior[0]
    repetitions = 0
    while odds > limit:
        odds *= q
        repetitions += 1
    assert odds <= limit and (repetitions == 0 or odds/q > limit)
    return repetitions, odds/rates[0]**horizon


class Joint:
    def __init__(self, n, rates, prior):
        self.n, self.rates, self.prior = n, rates, prior
        self.worlds = tuple((0,)+z for z in product((0, 1), repeat=n-1))
        self.edges = tuple(combinations(range(n), 2))
        self.scale = lcm(*(eta.denominator for eta in rates))
        denominator = lcm(*(p.denominator for p in prior))
        self.initial = tuple(int(p*denominator) for p in prior for _ in self.worlds)
        self.hypotheses = tuple((eta, z) for eta in rates for z in self.worlds)
        self.factors = {(i, j, y): tuple(int(self.scale*((1-eta) if z[i]^z[j] == y else eta))
                        for eta, z in self.hypotheses)
                        for i, j, y in product(range(n), range(n), range(2))}

    def update(self, weights, event, repetitions=1):
        return tuple(w*a**repetitions for w, a in zip(weights, self.factors[event]))

    def forecast(self, weights, event):
        return F(sum(w*a for w, a in zip(weights, self.factors[event])), self.scale*sum(weights))

    def minority(self, weights):
        return F(sum(weights[len(self.worlds):]), sum(weights))

    def counts(self, total, signed, diagonal):
        result = []
        for index, (eta, z) in enumerate(self.hypotheses):
            twice = total+diagonal+sum(d*(1-2*(z[i]^z[j])) for d, (i, j) in zip(signed, self.edges))
            assert twice % 2 == 0 and 0 <= twice//2 <= total
            matches = twice//2
            a, b = int(self.scale*(1-eta)), int(self.scale*eta)
            result.append(self.initial[index]*a**matches*b**(total-matches))
        return tuple(result)


def acquisition_audit():
    rows = []
    for rates, prior in (DEFAULT, OTHER):
        for n, horizon in ((2, 3), (3, 2)):
            model = Joint(n, rates, prior)
            delta = F(1, 16)
            repetitions, bound = calibrated(rates, prior, horizon, delta)
            initial = model.update(model.initial, (0, 0, 0), repetitions)
            levels = [(initial, (0,)*len(model.edges), repetitions)]
            checked = forecasts = 0
            worst = F(0)
            for time in range(horizon+1):
                following = []
                for weights, signed, diagonal in levels:
                    assert weights == model.counts(repetitions+time, signed, diagonal)
                    beta = model.minority(weights)
                    assert beta <= bound/(1+bound) <= delta
                    worst = max(worst, beta)
                    conditioned = weights[:len(model.worlds)]
                    for i, j in product(range(n), repeat=2):
                        p0 = rates[0]+(1-2*rates[0])*F(sum(w for w, z in zip(conditioned, model.worlds) if z[i]^z[j]), sum(conditioned))
                        assert abs(model.forecast(weights, (i, j, 1))-p0) <= beta
                        forecasts += 1
                    checked += 1
                    if time == horizon:
                        continue
                    for event in model.factors:
                        i, j, label = event
                        counts = list(signed)
                        s = diagonal
                        if i == j:
                            s += 1-2*label
                        else:
                            counts[model.edges.index(tuple(sorted((i, j))))] += 1-2*label
                        following.append((model.update(weights, event), tuple(counts), s))
                levels = following
            rows.append({'n': n, 'rates': tuple(map(str, rates)), 'prior': tuple(map(str, prior)),
                         'continuation_horizon': horizon, 'calibration_events': repetitions,
                         'all_prefixes_checked': checked, 'all_pair_forecasts_checked': forecasts,
                         'maximum_other_rate_mass': str(worst), 'uniform_mass_bound': str(bound/(1+bound))})
    # A prefix calibrated for time zero cannot delete the other rate forever.
    model = Joint(2, *DEFAULT)
    repetitions, _ = calibrated(*DEFAULT, 0, F(1, 20))
    weights = model.update(model.initial, (0, 0, 0), repetitions)
    before = model.minority(weights)
    opposite = 0
    while model.minority(weights) <= F(1, 2):
        weights = model.update(weights, (0, 0, 1))
        opposite += 1
    assert before <= F(1, 20)
    return {'cases': rows, 'unprotected_prefix_counterexample': {
        'diagonal_zero_prefix': repetitions, 'initial_other_rate_mass': str(before),
        'subsequent_diagonal_ones': opposite, 'final_other_rate_mass': str(model.minority(weights))}}


def parameters(n, edges, rates, prior, error):
    margin = F(1, 2)-rates[0]-error
    assert margin > 0
    delta = margin/2
    gamma = delta/(1-2*rates[0])
    ratio = (1-rates[0])/rates[0]
    repetitions, factor = 0, F(1)
    while gamma*factor < 2**n:
        repetitions += 1
        factor *= ratio
    horizon = repetitions*(len(edges)+n-1)
    calibration, bound = calibrated(rates, prior, horizon, delta)
    return delta, gamma, repetitions, factor, horizon, calibration, bound


def reduction_audit():
    rows = []
    settings = [(DEFAULT, (F(0), F(1, 1000), F(39, 100), F(399, 1000)), 4),
                (OTHER, (F(0), F(374, 1000)), 3)]
    for (rates, prior), errors, largest in settings:
        for error in errors:
            graphs = states = branches = leaves = 0
            maximum_total = maximum_calibration = maximum_bits = 0
            for n in range(2, largest+1):
                model = Joint(n, rates, prior)
                for mask in range(1 << len(model.edges)):
                    edges = tuple(e for j, e in enumerate(model.edges) if mask >> j & 1)
                    delta, gamma, repeat, factor, horizon, calibration, bound = parameters(n, edges, rates, prior, error)
                    cuts = tuple(sum(z[i]^z[j] for i, j in edges) for z in model.worlds)
                    optimum = max(cuts)
                    signed = tuple(-repeat if e in edges else 0 for e in model.edges)
                    weights = model.update(model.initial, (0, 0, 0), calibration)
                    for i, j in edges:
                        weights = model.update(weights, (i, j, 1), repeat)
                    pending = [((), weights, signed)]
                    while pending:
                        prefix, weights, signed = pending.pop()
                        time = repeat*(len(edges)+len(prefix))
                        assert time <= horizon
                        assert weights == model.counts(calibration+time, signed, calibration)
                        assert model.minority(weights) <= bound/(1+bound) <= delta
                        component = weights[:len(model.worlds)]
                        good = tuple(cut == optimum and z[1:len(prefix)+1] == prefix
                                     for z, cut in zip(model.worlds, cuts))
                        assert any(good)
                        bad = F(sum(w for w, valid in zip(component, good) if not valid), sum(component))
                        assert bad <= len(model.worlds)/factor <= gamma/2 < gamma
                        states += 1
                        maximum_bits = max(maximum_bits, *(w.bit_length() for w in weights))
                        if len(prefix) == n-1:
                            chosen = (0,)+prefix
                            assert sum(chosen[i]^chosen[j] for i, j in edges) == optimum
                            leaves += 1
                            continue
                        query = len(prefix)+1
                        p = model.forecast(weights, (0, query, 1))
                        latent = F(sum(w for w, z in zip(component, model.worlds) if z[query]), sum(component))
                        p0 = rates[0]+(1-2*rates[0])*latent
                        assert abs(p-p0) <= delta
                        allowed = tuple(label for label, ok in ((0, p-error < F(1, 2)),
                                                               (1, p+error >= F(1, 2))) if ok)
                        assert allowed
                        for label in allowed:
                            assert (latent if label else 1-latent) >= gamma > bad
                            assert any(valid and z[query] == label for z, valid in zip(model.worlds, good))
                            updated = list(signed)
                            updated[model.edges.index((0, query))] += repeat*(1-2*label)
                            pending.append((prefix+(label,), model.update(weights, (0, query, label), repeat), tuple(updated)))
                            branches += 1
                    maximum_total = max(maximum_total, calibration+horizon)
                    maximum_calibration = max(maximum_calibration, calibration)
                    graphs += 1
            rows.append({'rates': tuple(map(str, rates)), 'prior': tuple(map(str, prior)),
                         'forecast_error': str(error), 'largest_n': largest, 'all_simple_graphs': graphs,
                         'all_allowed_adaptive_states': states, 'allowed_decisions': branches,
                         'terminal_optimal_cuts': leaves, 'maximum_history_length': maximum_total,
                         'maximum_calibration_length': maximum_calibration, 'maximum_integer_weight_bits': maximum_bits})
    return rows


def native_audit():
    rows = []
    for edges, error in (((), F(0)), (((0, 1),), F(399, 1000))):
        n = 2
        model = Joint(n, *DEFAULT)
        bundle = native.native_contract(n)
        bank, rules, graph, spec, _ = bundle
        _, _, repeat, _, horizon, calibration, _ = parameters(n, edges, *DEFAULT, error)
        state = initial_state(graph, rules, (F(1),)+bank.prior, 0, spec=spec, bit_limit=32768)
        weights = model.initial
        def event(i, j, label):
            nonlocal state, weights
            state = native.native_step(n, bundle, state, (i, j, label))
            weights = model.update(weights, (i, j, label))
            assert state.theta == (F(1),)+tuple(F(w, sum(weights)) for w in weights)
            assert not any(state.gradient_sum) and state.unit_count == 0
        for _ in range(calibration):
            event(0, 0, 0)
        for i, j in edges:
            for _ in range(repeat):
                event(i, j, 1)
        assignment = [0]
        for i in range(1, n):
            p = model.forecast(weights, (0, i, 1))
            label = int(p+error >= F(1, 2))
            assignment.append(label)
            for _ in range(repeat):
                event(0, i, label)
        assert sum(assignment[i]^assignment[j] for i, j in edges) == len(edges)
        assert state.cursor == state.optimizer_steps == calibration+horizon
        rows.append({'n': n, 'edges': edges, 'forecast_error': str(error),
                     'ordinary_calibration_events': calibration, 'complete_native_triples': state.cursor,
                     'returned_cut': sum(assignment[i]^assignment[j] for i, j in edges)})
    return rows


def run():
    threshold = F(1, 2)-DEFAULT[0][0]
    assert all(max(abs(F(1, 2)-eta), abs(F(1, 2)-(1-eta))) <= threshold for eta in DEFAULT[0])
    assignment = (0, 1, 1)
    returned = assignment[1] ^ assignment[2]
    optimum = max(z[0] ^ z[1] for z in product((0, 1), repeat=2))
    assert returned == 0 and optimum == 1
    result = {'status': 'PASS', 'precision': 'exact integer/Fraction; native guard32768 bits',
              'acquisition': acquisition_audit(), 'reduction': reduction_audit(), 'native': native_audit(),
              'sharp_threshold': {'noise_min': str(DEFAULT[0][0]), 'constant_forecast': '1/2', 'uniform_error': str(threshold),
                                  'n3_single_edge_12_tie_assignment': assignment, 'returned_cut': returned, 'optimum': optimum},
              'scope': 'Mathematical worst-case conditional forecast problems for fixed finite rates/prior and complete pair queries. No average-case acquisition claim, Runtime certificate, GPU/model experiment or unconditional exponential-time lower bound.'}
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
