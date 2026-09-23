"""Shared-noise factor irreducibility versus positive exact forest decoding.

Passive exact proof audit. No Runtime registration, source substitution,
new learner, physical budget, AMP bridge or GPU execution is supplied.
"""
from collections import Counter
from dataclasses import dataclass, replace
from fractions import Fraction as F
from functools import lru_cache
from itertools import combinations, permutations, product
from math import lcm, prod
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(Path(__file__).parent)]
from fp_reference.learner import initial_state
from fp_reference.profile import attach_boundary
from fp_reference.semantics import evaluate
import noise_acquisition as native
from unknown_noise_decoding import Joint, DEFAULT, OTHER

OUTPUT = ROOT/'evidence/minimal/FP_SHARED_NOISE_FACTOR_CLOSURE.json'


@lru_cache(None)
def product_tensor(values, sizes):
    """Independent exact joint-versus-product-of-marginals identity."""
    positions = tuple(product(*(range(size) for size in sizes)))
    assert len(values) == len(positions) and min(values) > 0
    total = sum(values)
    margins = tuple(tuple(sum(v for v, z in zip(values, positions) if z[j] == a)
                          for a in range(size)) for j, size in enumerate(sizes))
    return all(v*total**(len(sizes)-1) == prod(margins[j][a] for j, a in enumerate(z))
               for v, z in zip(values, positions))


def one_factor(values, sizes):
    positions = tuple(product(*(range(size) for size in sizes)))
    for j, size in enumerate(sizes):
        if all(len({v for v, z in zip(values, positions) if z[j] == a}) == 1
               for a in range(size)):
            return True
    return False


def binary_lemma_audit():
    checks = accepted = 0
    for sizes, denominator in (((2, 2), 6), ((2, 3), 4), ((2, 2, 2), 4)):
        for values in product(range(1, denominator), repeat=prod(sizes)):
            tests = product_tensor(values, sizes), product_tensor(tuple(denominator-v for v in values), sizes)
            both = all(tests)
            assert both == one_factor(values, sizes)
            checks += 1
            accepted += both
    values = (1, 2, 2, 4)
    assert product_tensor(values, (2, 2)) and not product_tensor(tuple(10-v for v in values), (2, 2))
    complement = tuple(1-F(v, 10) for v in values)
    determinant = complement[0]*complement[3]-complement[1]*complement[2]
    assert determinant == -F(1, 10)
    product_tensor.cache_clear()
    return {'normalized_binary_tables': checks, 'both_labels_preserve_products': accepted,
            'one_label_only_counterexample': {'denominator': 10, 'zero_likelihood_numerators': values,
                                             'one_likelihood_determinant': str(determinant)}}


def gf2_rank(values):
    pivots = {}
    for value in values:
        while value:
            pivot = value.bit_length()-1
            if pivot not in pivots:
                pivots[pivot] = value
                break
            value ^= pivots[pivot]
    return len(pivots)


def all_encoding_audit():
    # World bits encode (noise index, two independent latent parity bits).
    # Query 0 is diagonal; 1,2,3 are all nonzero binary linear forms.
    shapes = ((2, 4), (2, 2, 2))
    priors = ((1, 1), (1, 2))
    tables = tuple(tuple((18, 15)[w//4] if (v & (w % 4)).bit_count() % 2 == 0
                         else (2, 5)[w//4] for w in range(8)) for v in range(4))
    histograms = {(prior, shape): Counter() for prior in priors for shape in shapes}
    initial_counts = Counter()
    posterior_checks = 0
    for order in permutations(range(8)):
        for prior in priors:
            gamma = tuple(prior[w//4] for w in order)
            for shape in shapes:
                if not product_tensor(gamma, shape):
                    continue
                initial_counts[prior, shape] += 1
                mask = 0
                for v, table in enumerate(tables):
                    posterior_zero = tuple(g*table[w] for g, w in zip(gamma, order))
                    posterior_one = tuple(g*(20-table[w]) for g, w in zip(gamma, order))
                    tests = product_tensor(posterior_zero, shape), product_tensor(posterior_one, shape)
                    closed = all(tests)
                    assert closed == one_factor(tuple(table[w] for w in order), shape)
                    mask |= int(closed) << v
                    posterior_checks += 2
                histograms[prior, shape][mask] += 1
    rows = []
    for prior in priors:
        families = []
        for family in range(16):
            selected = tuple(v for v in range(4) if family >> v & 1)
            required = 1 if not selected else 2**(1+gf2_rank(selected))
            valid = tuple(sum(count for mask, count in histograms[prior, shape].items()
                              if mask & family == family) for shape in shapes)
            assert all(bool(count) == (max(shape) >= required) for count, shape in zip(valid, shapes))
            if family in (0, 1, 2, 6, 15):
                families.append({'queries': selected, 'required_joint_factor_categories': required,
                                 'valid_bijections_in_shape_order': valid})
        rows.append({'prior_ratio': prior,
                     'product_initializers_in_shape_order': tuple(initial_counts[prior, s] for s in shapes),
                     'families': families})
    product_tensor.cache_clear()
    return {'bijections': 40320, 'shapes': shapes, 'prior_count': len(priors),
            'encoding_shape_prior_cases': 40320*len(shapes)*len(priors),
            'complete_one_event_posterior_checks': posterior_checks,
            'query_family_shape_prior_checks': 16*len(shapes)*len(priors), 'cases': rows}


class OutsideForest(Exception):
    pass


class IntegerAllowance(Exception):
    pass


@dataclass
class Arithmetic:
    bound: int
    multiplies: int = 0
    adds: int = 0
    largest: int = 1

    def value(self, v):
        assert type(v) is int and v >= 0 and v.bit_length() <= self.bound
        self.largest = max(self.largest, v.bit_length())
        return v

    def mul(self, a, b):
        self.multiplies += 1
        return self.value(a*b)

    def add(self, a, b):
        self.adds += 1
        return self.value(a+b)

    def power(self, base, exponent):
        value = 1
        while exponent:
            if exponent & 1:
                value = self.mul(value, base)
            exponent >>= 1
            if exponent:
                base = self.mul(base, base)
        return value


def forest_decode(n, total, signed, diagonal, query, rates, prior, *, integer_bits=32768):
    """Decode the original joint weights; never update conditional parameters."""
    edges = tuple(combinations(range(n), 2))
    assert n >= 2 and len(signed) == len(edges) and all(type(v) is int for v in signed)
    assert type(total) is int and type(diagonal) is int and total >= 0
    assert len(rates) == len(prior) and sum(prior) == 1 and min(prior) > 0
    assert all(0 < eta < F(1, 2) for eta in rates)
    assert len(query) == 2 and all(type(i) is int and 0 <= i < n for i in query)
    height = sum(map(abs, signed))
    assert height+abs(diagonal) <= total and (total-height-diagonal) % 2 == 0
    matches, mismatches = (total+diagonal-height)//2, (total-diagonal-height)//2
    scale = lcm(*(eta.denominator for eta in rates))
    prior_scale = lcm(*(p.denominator for p in prior))
    bound = n+prior_scale.bit_length()+(total+1)*(scale-1).bit_length()
    if bound > integer_bits:
        raise IntegerAllowance('positive integer envelope exceeds the declared passive allowance')
    active = tuple((edge, d) for edge, d in zip(edges, signed) if d)
    adjacency = [[] for _ in range(n)]
    for index, ((u, v), _) in enumerate(active):
        adjacency[u].append((v, index))
        adjacency[v].append((u, index))
    component = [-1]*n
    for origin in range(n):
        if component[origin] != -1:
            continue
        component[origin] = origin
        stack = [(origin, -1)]
        while stack:
            u, previous_edge = stack.pop()
            for v, index in adjacency[u]:
                if index == previous_edge:
                    continue
                if component[v] != -1:
                    raise OutsideForest('active signed support is cyclic; retained counts are unchanged')
                component[v] = origin
                stack.append((v, index))
    start, finish = query
    same = component[start] == component[finish]
    path = set()
    if same:
        previous = {start: None}
        stack = [start]
        while stack and finish not in previous:
            u = stack.pop()
            for v, index in adjacency[u]:
                if v not in previous:
                    previous[v] = u, index
                    stack.append(v)
        v = finish
        while v != start:
            u, index = previous[v]
            path.add(index)
            v = u
    arithmetic = Arithmetic(bound)
    parts, constants, factors = [], [], []
    components = n-len(active)
    for eta, pi in zip(rates, prior):
        a, b = int(scale*eta), int(scale*(1-eta))
        constant = arithmetic.mul(int(pi*prior_scale), arithmetic.mul(
            arithmetic.power(b, matches), arithmetic.power(a, mismatches)))
        even, odd, rest = 1, 0, 1
        row = []
        for index, (_, d) in enumerate(active):
            small, large = arithmetic.power(a, abs(d)), arithmetic.power(b, abs(d))
            u, v = (large, small) if d > 0 else (small, large)
            row.append((u, v))
            if index in path:
                even, odd = (arithmetic.add(arithmetic.mul(even, u), arithmetic.mul(odd, v)),
                             arithmetic.add(arithmetic.mul(even, v), arithmetic.mul(odd, u)))
            else:
                rest = arithmetic.mul(rest, arithmetic.add(u, v))
        if same:
            common = arithmetic.mul(1 << (components-1), arithmetic.mul(constant, rest))
            pair = arithmetic.mul(common, even), arithmetic.mul(common, odd)
        else:
            common = arithmetic.mul(1 << (components-2), arithmetic.mul(constant, rest))
            pair = common, common
        parts.append(pair)
        constants.append(constant)
        factors.append(tuple(row))
    denominator = numerator = 0
    for eta, (even, odd) in zip(rates, parts):
        denominator = arithmetic.add(denominator, arithmetic.add(even, odd))
        numerator = arithmetic.add(numerator, arithmetic.add(
            arithmetic.mul(int(scale*(1-eta)), even), arithmetic.mul(int(scale*eta), odd)))
    forecast = F(numerator, arithmetic.mul(scale, denominator))
    return {'parts': tuple(parts), 'normalizer': denominator, 'forecast_zero': forecast,
            'constants': tuple(constants), 'factors': tuple(factors), 'active': active,
            'stats': {'positive_multiplications': arithmetic.multiplies,
                      'positive_additions': arithmetic.adds, 'integer_envelope': bound,
                      'largest_integer_bits': arithmetic.largest}}


def point_weight(result, rate, z):
    value = result['constants'][rate]
    for ((i, j), _), factors in zip(result['active'], result['factors'][rate]):
        value *= factors[z[i]^z[j]]
    return F(value, result['normalizer'])


def counter_states(dimension, depth):
    states = {(0,)*dimension}
    yield 0, states
    for t in range(1, depth+1):
        states = {state[:j]+(state[j]+delta,)+state[j+1:]
                  for state in states for j in range(dimension) for delta in (-1, 1)}
        yield t, states


def decoder_audit():
    cases = []
    for rates, prior in (DEFAULT, OTHER):
        cuts = forecasts = points = refusals = largest = 0
        for n in (2, 3, 4):
            model = Joint(n, rates, prior)
            for total, states in counter_states(len(model.edges)+1, 3):
                for counts in sorted(states):
                    weights = model.counts(total, counts[:-1], counts[-1])
                    for query in product(range(n), repeat=2):
                        try:
                            result = forest_decode(n, total, counts[:-1], counts[-1], query, rates, prior)
                        except OutsideForest:
                            refusals += 1
                            # An independent triangle search suffices: T<=3.
                            assert any(all(counts[model.edges.index(e)] for e in combinations(vertices, 2))
                                       for vertices in combinations(range(n), 3))
                            continue
                        expected = tuple(tuple(sum(w for w, (eta, z) in zip(weights, model.hypotheses)
                                                   if eta == rate and z[query[0]]^z[query[1]] == parity)
                                               for parity in (0, 1)) for rate in rates)
                        assert result['parts'] == expected
                        assert result['forecast_zero'] == model.forecast(weights, (*query, 0))
                        assert 1-result['forecast_zero'] == model.forecast(weights, (*query, 1))
                        assert result['normalizer'] == sum(weights)
                        largest = max(largest, result['stats']['largest_integer_bits'])
                        forecasts += 1
                        if query == (0, 0):
                            for index, (eta, z) in enumerate(model.hypotheses):
                                assert point_weight(result, rates.index(eta), z) == F(weights[index], sum(weights))
                                points += 1
                            cuts += 1
        cases.append({'rates': tuple(map(str, rates)), 'prior': tuple(map(str, prior)),
                      'all_reachable_forest_cuts_n2_to_n4_through_time3': cuts,
                      'ordered_query_partitions_and_both_forecasts': forecasts,
                      'complete_weight_point_checks': points, 'cyclic_query_refusals': refusals,
                      'maximum_integer_bits': largest})
    try:
        forest_decode(2, 1000, (1000,), 0, (0, 1), *DEFAULT, integer_bits=64)
    except IntegerAllowance:
        pass
    else:
        raise AssertionError('bit allowance must refuse before any power')
    return {'cases': cases, 'pre_power_integer_refusals': 1}


def native_audit():
    n = 3
    rates, prior = DEFAULT
    bundle = native.native_contract(n)
    model, rules, graph, spec, scale = bundle
    initial = initial_state(graph, rules, (F(1),)+model.prior, 0, spec=spec, bit_limit=32768)
    alphabet = tuple((i, j, y) for i, j in ((0, 0), (0, 1), (1, 2)) for y in (0, 1))
    levels = [(initial, ())]
    triples = caches = state_points = 0
    for _ in range(3):
        following = []
        for state, history in levels:
            total, counts = native.coordinates(n, history)
            # Every ordered current query, including a possible closing edge.
            for query in product(range(n), repeat=2):
                result = forest_decode(n, total, counts[:-1], counts[-1], query, rates, prior)
                weights = tuple(point_weight(result, j, (0,)+z) for j in range(len(rates))
                                for z in product((0, 1), repeat=n-1))
                assert state.theta == (F(1),)+weights
                point = native.source_point(n, query)
                cache = evaluate(graph, rules, state.theta, dict(zip((s.source_id for s in rules.sources), point)), (), bit_limit=32768)
                assert cache.probabilities == (result['forecast_zero'], 1-result['forecast_zero'])
                original = native.finite.cache_oracle(model, weights, query[0]*n+query[1], scale)
                assert cache == replace(original, values=point+tuple(point[a]*point[n+b]
                    for a, b in product(range(n), repeat=2))+original.values[n*n:])
                caches += 1
                state_points += len(weights)
            for event in alphabet:
                after = native.native_step(n, bundle, state, event)
                assert after.unit_count == 0 and after.delayed == ()
                next_history = history+(event,)
                total, counts = native.coordinates(n, next_history)
                decoded = forest_decode(n, total, counts[:-1], counts[-1], event[:2], rates, prior)
                expected = tuple(point_weight(decoded, j, (0,)+z) for j in range(len(rates))
                                 for z in product((0, 1), repeat=n-1))
                assert after.theta == (F(1),)+expected
                following.append((after, next_history))
                triples += 1
        levels = following
    # A closing observation must not be discarded to keep the decoder cheap.
    history = ((0, 1, 0), (1, 2, 0), (0, 2, 0))
    state = initial
    for event in history:
        state = native.native_step(n, bundle, state, event)
        triples += 1
    total, counts = native.coordinates(n, history)
    try:
        forest_decode(n, total, counts[:-1], counts[-1], (0, 2), rates, prior)
    except OutsideForest:
        pass
    else:
        raise AssertionError('closing-cycle counts must be retained and refused')
    # Opposite evidence cancels that edge but retains its two-event noise cost.
    event = (0, 2, 1)
    state = native.native_step(n, bundle, state, event)
    triples += 1
    total, counts = native.coordinates(n, history+(event,))
    decoded = forest_decode(n, total, counts[:-1], counts[-1], (0, 2), rates, prior)
    expected = tuple(point_weight(decoded, j, (0,)+z) for j in range(len(rates))
                     for z in product((0, 1), repeat=n-1))
    assert state.theta == (F(1),)+expected
    noise_mass = sum(expected[:4])
    assert noise_mass != F(1, 2)
    profile = ((0, 1, 0), (1, 2, 1))*2
    profiled = initial
    for event in profile:
        profiled = native.native_step(n, bundle, profiled, event)
        triples += 1
    attached = attach_boundary(profiled, 2, spec)
    assert attached.cursor == 2 and attached.optimizer_steps == 4
    assert attached.theta == profiled.theta and attached.gradient_sum == profiled.gradient_sum
    total, counts = native.coordinates(n, profile)
    result = forest_decode(n, total, counts[:-1], counts[-1], (0, 2), rates, prior)
    assert attached.theta[1:] == tuple(point_weight(result, j, (0,)+z)
        for j in range(len(rates)) for z in product((0, 1), repeat=n-1))
    following = native.native_step(n, bundle, attached, (0, 0, 0))
    triples += 1
    assert following.cursor == 3 and following.optimizer_steps == 5
    total, counts = native.coordinates(n, profile+((0, 0, 0),))
    result = forest_decode(n, total, counts[:-1], counts[-1], (0, 2), rates, prior)
    assert following.theta[1:] == tuple(point_weight(result, j, (0,)+z)
        for j in range(len(rates)) for z in product((0, 1), repeat=n-1))
    return {'native_graph': graph.counts(), 'complete_native_triples': triples,
            'additional_all_query_cache_checks': caches, 'additional_native_weight_points': state_points,
            'closing_cycle_refused': True, 'cancellation_recovered_rate_zero_mass': str(noise_mass),
            'cancellation_recovered_next_zero_forecast': str(decoded['forecast_zero']),
            'profile_attachment_cursor_and_steps': (attached.cursor, attached.optimizer_steps),
            'profile_continuation_cursor_and_steps': (following.cursor, following.optimizer_steps)}


def large_forest_audit():
    reports = []
    for n in (64, 256):
        rates, prior = OTHER
        edges = tuple(combinations(range(n), 2))
        signed = tuple((1 if i % 2 else -1)*(1+i % 4) if j == i+1 and i != n//2 else 0 for i, j in edges)
        diagonal = -3
        total = sum(map(abs, signed))+7
        queries = ((0, 0), (0, n//2), (0, n-1), (n//2+1, n-1))
        for query in queries:
            decoded = forest_decode(n, total, signed, diagonal, query, rates, prior)
            # Independent conditional path-correlation identity; signed proof
            # arithmetic is not an operation in the positive decoder.
            u, v = sorted(query)
            disconnected = u <= n//2 < v
            scale = lcm(*(eta.denominator for eta in rates))
            prior_scale = lcm(*(p.denominator for p in prior))
            expected = []
            height = sum(map(abs, signed))
            for eta, pi in zip(rates, prior):
                a, b = int(scale*eta), int(scale*(1-eta))
                mass = int(pi*prior_scale)*a**((total-diagonal-height)//2)*b**((total+diagonal-height)//2)
                correlation = F(0) if disconnected else F(1)
                for (i, j), d in zip(edges, signed):
                    if not d:
                        continue
                    p, q = b**abs(d), a**abs(d)
                    mass *= p+q
                    if u <= i < v:
                        correlation *= (1 if d > 0 else -1)*F(p-q, p+q)
                mass *= 2  # Two components, with only the global flip anchored.
                pair = mass*(1+correlation)/2, mass*(1-correlation)/2
                assert all(value.denominator == 1 for value in pair)
                expected.append(tuple(map(int, pair)))
            assert decoded['parts'] == tuple(expected)
            reports.append({'n': n, 'events': total, 'query': query,
                            'required_fixed_factor_categories_on_this_forest': str(len(rates)*2**(n-2)),
                            **decoded['stats']})
    return reports


def run():
    result = {'status': 'PASS', 'precision': 'exact integers and Fraction; no Torch',
              'binary_likelihood_lemma': binary_lemma_audit(), 'all_reencodings': all_encoding_audit(),
              'positive_joint_decoder': decoder_audit(), 'complete_native_relation': native_audit(),
              'large_forest_separation': large_forest_audit(),
              'scope': 'Fixed independent-factor closure lower; positive forest snapshot decoder of retained joint counts. No all-encoding memory lower, new native optimizer, Runtime certificate or AMP authority.'}
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
