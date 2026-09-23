"""General rational coordinates and joint-scale readout: exact passive audit.

Native cache/gradient checks use the existing learner. Arithmetic-machine
checks do not execute CUDA or confer Runtime, install or release authority.
"""
from fractions import Fraction as F
from itertools import combinations_with_replacement, product
from math import gcd, prod
from pathlib import Path
import argparse
import json
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts'), str(Path(__file__).parent)]
from fp_reference.core import ContractError
from fp_reference.coprime_coordinates import factor, integer_weights
from fp_reference.learner import initial_state
from fp_reference.likelihood_encoding import _Arithmetic, _affine_heads, _row_basis
from fp_reference.semantics import ArithmeticUnresolved
from audit_cuda_primitives import SINGLE
from audit_likelihood_encoding import reverse_bank
import likelihood_information as finite
import noise_acquisition as noise

BITS, WORK, CELLS = 4096, 10**7, 128
ALLOW = dict(bit_limit=BITS, work_limit=WORK, cell_limit=CELLS)
U, TAU = F(1, 1 << 24), F(1, 1 << 150)
ROUNDINGS = 0


def refusal(action, exception=ArithmeticUnresolved):
    try:
        action()
    except exception:
        return
    raise AssertionError('expected bounded refusal did not occur')


def check_factor(values):
    result = factor(values, **ALLOW)
    assert tuple(sorted(set(result.bases))) == result.bases
    assert all(gcd(a, b) == 1 for a, b in combinations_with_replacement(result.bases, 2) if a != b)
    assert len(result.exponents) == len(values)
    for value, row in zip(values, result.exponents):
        assert len(row) == len(result.bases)
        assert prod((F(b)**e for b, e in zip(result.bases, row)), start=F(1)) == value
    inputs = {n for v in values for n in (v.numerator, v.denominator) if n > 1}
    assert result.splits <= sum(n.bit_length() for n in inputs)
    assert prod(result.bases) * 2**result.splits <= prod(inputs)
    return result


def factor_audit():
    checks = maximum_work = maximum_cells = 0
    for values in combinations_with_replacement(range(1, 33), 3):
        result = check_factor(tuple(map(F, values)))
        maximum_work = max(maximum_work, result.operations)
        maximum_cells = max(maximum_cells, result.peak_basis_cells)
        checks += 1
    rationals = tuple(sorted({F(a, b) for a, b in product(range(1, 9), repeat=2)}))
    for values in product(rationals, repeat=2):
        result = check_factor(values)
        reversed_result = factor(values[::-1], **ALLOW)
        assert reversed_result.bases == result.bases
        assert reversed_result.exponents == result.exponents[::-1]
        checks += 1
    for values in ((), (F(1),)*5, (F(4), F(16)), (F(36), F(216)),
                   (F(12, 25), F(18, 35), F(50, 63), F(12, 25))):
        check_factor(values)
        checks += 1
    assert factor((F(4), F(16)), **ALLOW).bases == (4,)
    assert factor((F(36), F(216)), **ALLOW).bases == (6,)
    composite = ((1 << 127)-1)*((1 << 61)-1)
    result = check_factor((F(composite), F(composite**2)))
    assert result.bases == (composite,) and result.exponents == ((1,), (2,))
    values = (F(12, 25), F(18, 35), F(50, 63))
    before = values
    result = factor(values, **ALLOW)
    assert factor(values, **(ALLOW | {'work_limit': result.operations})) == result
    refusal(lambda: factor(values, **(ALLOW | {'work_limit': result.operations-1})))
    refusal(lambda: factor((F(6), F(10)), **(ALLOW | {'cell_limit': 2})))
    refusal(lambda: factor((F(16),), **(ALLOW | {'bit_limit': 4})))
    for invalid in ((F(0),), (F(-1),), (True,), (0.5,), [F(1)]):
        refusal(lambda v=invalid: factor(v, **ALLOW), ContractError)
    assert before == values
    return {'exact_factorizations': checks+1, 'small_bank_maximum_work': maximum_work,
            'small_bank_peak_basis_cells': maximum_cells, 'bounded_refusals': 3,
            'malformed_input_refusals': 5, 'unfactored_composite_bits': composite.bit_length(),
            'composite_basis_examples': [[4], [6]], 'order_and_duplicate_inputs_checked': True}


def rounded(value):
    """Cross-check the existing oracle by an independent quotient/tie decision."""
    global ROUNDINGS
    assert value >= 0
    word = SINGLE.rounded(value)
    if not value:
        expected = F(0)
    else:
        n, d = value.numerator, value.denominator
        exponent = n.bit_length()-d.bit_length()
        below = n < d << exponent if exponent >= 0 else (n << -exponent) < d
        if below:
            exponent -= 1
        quantum = max(exponent-23, -149)
        scaled_n, scaled_d = (n, d << quantum) if quantum >= 0 else (n << -quantum, d)
        quotient, remainder = divmod(scaled_n, scaled_d)
        quotient += int(2*remainder > scaled_d or 2*remainder == scaled_d and quotient & 1)
        expected = F(quotient << quantum) if quantum >= 0 else F(quotient, 1 << -quantum)
    assert SINGLE.decode(word) == expected
    ROUNDINGS += 1
    return expected


def theta_bound(k):
    assert 1 <= k <= 1 << 23
    gamma = (k-1)*U/(1-(k-1)*U)
    epsilon = U+2*k*TAU
    return epsilon+gamma/(1-gamma)+U+TAU


def round_weights(weights):
    """One common exact scale, RNE32 ingress, ordered sum and divisions."""
    assert weights and all(type(v) is int and v > 0 for v in weights)
    shift = max(v.bit_length() for v in weights)
    a = tuple(F(v, 1 << shift) for v in weights)
    b = tuple(rounded(v) for v in a)
    assert F(1, 2) <= max(a) < 1 and F(1, 2) <= max(b) <= 1
    total = F(0)
    for value in b:
        total = rounded(total+value)
    assert max(b) <= total <= len(b)
    A, B, k = sum(a), sum(b), len(a)
    epsilon, gamma = U+2*k*TAU, (k-1)*U/(1-(k-1)*U)
    assert sum(abs(x-y) for x, y in zip(a, b)) <= epsilon*A
    assert abs(total-B) <= gamma*B
    assert all(abs(y/B-x/A) <= epsilon for x, y in zip(a, b))
    result = tuple(rounded(v/total) for v in b)
    error = max(abs(x/A-y) for x, y in zip(a, result))
    assert error <= theta_bound(k)
    return result, error


def check_plan(bases, rows):
    plan = integer_weights(bases, rows, **ALLOW)
    raw = tuple(prod((F(b)**e for b, e in zip(bases, row)), start=F(1)) for row in rows)
    assert finite.normalize(plan.weights) == finite.normalize(raw)
    assert plan.binary_shift == max(v.bit_length() for v in plan.weights)
    assert all(v.bit_length() <= bound for v, bound in zip(plan.weights, plan.integer_envelopes))
    if all(gcd(a, b) == 1 for a, b in combinations_with_replacement(bases, 2) if a != b):
        assert gcd(*plan.weights) == 1
    return plan


def plan_audit():
    checks, maximum = 0, F(0)
    for four in product(range(-3, 4), repeat=4):
        rows = ((0, 0), four[:2], four[2:])
        plan = check_plan((2, 3), rows)
        _, error = round_weights(plan.weights)
        maximum = max(maximum, error)
        checks += 1
    for bases, rows in (((), ((),)), ((), ((),)*8), ((4, 9), ((0, 0), (3, -2))),
                        ((6, 10), ((0, 0), (3, -2)))):
        check_plan(bases, rows)
        checks += 1
    original = ((0, 0), (168, -106))
    plan = check_plan((2, 3), original)
    shifted = tuple((a+10000, b-10000) for a, b in original)
    assert integer_weights((2, 3), shifted, **ALLOW).weights == plan.weights
    assert integer_weights((3, 2), tuple(row[::-1] for row in original), **ALLOW).weights == plan.weights
    assert integer_weights((2, 3), original, **(ALLOW | {'work_limit': plan.operations})) == plan
    refusal(lambda: integer_weights((2, 3), original, **(ALLOW | {'work_limit': plan.operations-1})))
    refusal(lambda: integer_weights((2, 3), original, **(ALLOW | {'cell_limit': 1})))
    refusal(lambda: integer_weights((2, 3), original, **(ALLOW | {'bit_limit': max(plan.integer_envelopes)})))
    for bases, rows in (((1,), ((0,),)), ((2,), ((True,),)), ((2,), ((),)), ((2,), ())):
        refusal(lambda b=bases, r=rows: integer_weights(b, r, **ALLOW), ContractError)
    boundaries = [(1, 1), (1, 2)]
    for power in (23, 24, 126, 127, 148, 149, 150, 151, 256):
        boundaries.extend((small, (1 << power)+offset) for small in (1, 2, 3) for offset in (-1, 0, 1))
    wide = {}
    for k in (2, 8, 128):
        max_error, count = F(0), 0
        for power in (0, 1, 23, 24, 25, 126, 149, 150, 256):
            for position in sorted({0, k//2, k-1}):
                weights = [1]*k
                weights[position] = 1 << power
                _, error = round_weights(tuple(weights))
                max_error = max(max_error, error)
                count += 1
        wide[str(k)] = {'vectors': count, 'maximum_error': str(max_error),
                        'uniform_bound': str(theta_bound(k)), 'bound_binary64': float(theta_bound(k))}
    for weights in boundaries:
        round_weights(weights)
    halfway_plus = F((1 << 79)+(1 << 55)+1, 1 << 80)
    direct_word = SINGLE.encode_exact(rounded(halfway_plus))
    via_double = int.from_bytes(struct.pack('>f', float(halfway_plus)), 'big')
    assert direct_word == 0x3f000001 and via_double == 0x3f000000
    round_weights(((1 << 79)+(1 << 55)+1, 1))
    return {'exact_integer_plans': checks+1, 'exhaustive_three_world_vectors': 7**4,
            'three_world_maximum_error': str(maximum), 'underflow_and_tie_boundary_vectors': len(boundaries),
            'widths': wide, 'bounded_refusals': 3, 'malformed_input_refusals': 4,
            'double_rounding_witness': {'exact_RNE32_word': direct_word, 'via_binary64_word': via_double},
            'common_exponent_shift_and_basis_permutation_checked': True}


class Coordinates:
    """Passive compression prototype; receives no owned Runtime object."""
    def __init__(self, model):
        self.model = model
        k = model.worlds
        ratios = tuple(p/model.prior[0] for p in model.prior)
        ratios += tuple(v/row[0] for row in model.factors for v in row)
        encoded = factor(ratios, **ALLOW)
        self.bases, self.prior = encoded.bases, encoded.exponents[:k]
        self.events = tuple(encoded.exponents[i:i+k] for i in range(k, len(encoded.exponents), k))
        rows = tuple(tuple(event[w][j] for event in self.events) for w in range(k) for j in range(len(self.bases)))
        differences = tuple(tuple(e-row[0] for e in row) for row in rows)
        arithmetic = _Arithmetic(BITS, WORK)
        basis, self.reconstruction = _row_basis(differences, arithmetic)
        self.increments = tuple(tuple(row[a] for row in basis) for a in range(len(self.events)))
        self.rho = len(basis)
        # Independent prime valuation computation is restricted to this audit's
        # small bank. Production factor() never performs prime factorization.
        self.prime = finite.Coordinates(model)
        assert self.rho == self.prime.rho

    def exponents(self, steps, q):
        flat = tuple(F(prior[j]+steps*self.events[0][w][j])+sum(c*x for c, x in zip(coefficients, q))
                     for (w, j), coefficients in zip(product(range(self.model.worlds), range(len(self.bases))),
                                                     self.reconstruction)
                     for prior in (self.prior[w],))
        assert all(v.denominator == 1 for v in flat)
        width = len(self.bases)
        return tuple(tuple(int(v) for v in flat[w*width:(w+1)*width]) for w in range(self.model.worlds))

    def decode(self, steps, q):
        plan = integer_weights(self.bases, self.exponents(steps, q), **ALLOW)
        return finite.normalize(plan.weights), plan


def derive_actual_bank(bundle, domain):
    model, rules, graph, spec, _ = bundle
    arithmetic = _Arithmetic(BITS, WORK)
    rows = []
    for point in domain:
        heads = _affine_heads(graph, rules, (F(1),)+model.prior, spec.simplex_slots, point, arithmetic)
        masses = tuple(tuple(row[0]+v for v in row[1:]) for row in heads)
        totals = tuple(map(sum, zip(*masses)))
        assert len(set(totals)) == 1
        rows.extend(tuple(v/totals[k] for k, v in enumerate(row)) for row in masses)
    independently = reverse_bank(graph, rules, (F(1),)+model.prior, spec, domain)
    assert tuple(rows) == independently == model.factors


def native_audit():
    results = []
    fixtures = []
    banks = finite.models() | {'prior_only_factor':
        (finite.bernoulli(((F(1, 2),)*2,), (F(1, 8), F(7, 8))), 3, 0)}
    for name, (model, depth, _) in banks.items():
        rules, graph, spec, scale = finite.native_graph(model)
        bundle = (model, rules, graph, spec, scale)
        domain = tuple(tuple(F(i == x) for i in range(len(model.table))) for x in range(len(model.table)))
        step = lambda state, event, m=model, b=(rules, graph, spec, scale): finite.native_step(m, b, state, event)
        fixtures.append((name, bundle, domain, step, depth))
    for n, depth in ((2, 3), (3, 2)):
        bundle = noise.native_contract(n)
        domain = tuple(noise.source_point(n, pair) for pair in product(range(n), repeat=2))
        step = lambda state, event, n=n, b=bundle: noise.native_step(n, b, state, (event[0]//n, event[0]%n, event[1]))
        fixtures.append((f'joint_noise_n{n}', bundle, domain, step, depth))
    for name, bundle, domain, step, depth in fixtures:
        model, rules, graph, spec, _ = bundle
        derive_actual_bank(bundle, domain)
        coordinates = Coordinates(model)
        state = initial_state(graph, rules, (F(1),)+model.prior, 0, spec=spec, bit_limit=32768)
        levels = [(state, (0,)*coordinates.rho, (0,)*len(model.events))]
        transitions, classes = 0, [1]
        for time in range(1, depth+1):
            following, mapping, reverse = [], {}, {}
            for before, q, counts in levels:
                for a, event in enumerate(model.events):
                    after = step(before, event)
                    following_q = tuple(v+d for v, d in zip(q, coordinates.increments[a]))
                    following_counts = tuple(c+int(i == a) for i, c in enumerate(counts))
                    exact, plan = coordinates.decode(time, following_q)
                    assert exact == after.theta[1:]
                    assert exact == coordinates.prime.decode(time, coordinates.prime.key(following_counts))
                    independent = finite.normalize(tuple(model.prior[k]*prod(row[k]**c for row, c in zip(model.factors, following_counts))
                                                         for k in range(model.worlds)))
                    assert exact == independent
                    assert mapping.setdefault(following_q, exact) == exact
                    assert reverse.setdefault(exact, following_q) == following_q
                    round_weights(plan.weights)
                    following.append((after, following_q, following_counts))
                    transitions += 1
            levels = following
            classes.append(len(mapping))
        results.append({'model': name, 'bases': list(coordinates.bases), 'rank': coordinates.rho,
                        'native_cache_observe_commit_checks': transitions, 'fixed_cut_classes': classes})
    return results


def reversal_audit():
    model = finite.bernoulli(((F(1, 3), F(2, 3)), (F(3, 4), F(1, 4))))
    bundle = finite.native_graph(model)
    rules, graph, spec, _ = bundle
    coordinates = Coordinates(model)
    assert coordinates.bases == (2, 3) and coordinates.rho == 2
    state = initial_state(graph, rules, (F(1),)+model.prior, 0, spec=spec, bit_limit=32768)
    q = (0,)*coordinates.rho
    cuts, zero_cuts = {}, []
    history = ((0, 0),)*168+((1, 0),)*106
    for time, event in enumerate(history, 1):
        state = finite.native_step(model, bundle, state, event)
        increment = coordinates.increments[model.events.index(event)]
        q = tuple(v+d for v, d in zip(q, increment))
        exact, plan = coordinates.decode(time, q)
        assert exact == state.theta[1:]
        theta, _ = round_weights(plan.weights)
        if min(theta) == 0:
            zero_cuts.append(time)
        if time in (168, 274):
            cuts[str(time)] = {'exact_world1': str(exact[1]), 'readout_words': [SINGLE.encode_exact(v) for v in theta],
                               'primitive_integer_bits': [v.bit_length() for v in plan.weights],
                               'coordinates': list(q), 'binary_shift': plan.binary_shift}
    assert zero_cuts and min(theta) > F(49, 100)
    powers = coordinates.exponents(len(history), q)
    assert powers == ((0, 0), (168, -106))
    # The tempting extension of max-exponent scaling separately to each basis
    # loses BOTH worlds, even with exact products before the final rounding.
    maxima = tuple(max(row[j] for row in powers) for j in range(2))
    independently_scaled = tuple(prod((F(b)**(e-m) for b, e, m in zip(coordinates.bases, row, maxima)), start=F(1))
                                 for row in powers)
    assert independently_scaled == (F(1, 2**168), F(1, 3**106))
    bad = tuple(rounded(v) for v in independently_scaled)
    assert bad == (0, 0)
    assert plan.weights == (3**106, 2**168)
    assert abs(theta[1]-exact[1]) < F(1, 10**10)
    return {'events': len(history), 'rank': coordinates.rho, 'bases': list(coordinates.bases),
            'full_native_phase_triples': len(history), 'temporary_zero_cuts': [min(zero_cuts), max(zero_cuts)],
            'temporary_zero_cut_count': len(zero_cuts), 'cuts': cuts,
            'per_basis_max_scaled_words': [SINGLE.encode_exact(v) for v in bad],
            'endpoint_world1_binary64': float(exact[1]), 'endpoint_RNE32_error': str(abs(theta[1]-exact[1])),
            'scope': 'passive exact/RNE32 sequence; no device execution or full AMP bridge'}


def run():
    report = {'status': 'EXACT_NATIVE_AND_RNE32_PASS', 'factorization': factor_audit(),
              'integer_and_rounding': plan_audit(), 'native_banks': native_audit(), 'reversal': reversal_audit()}
    report['independently_cross_checked_roundings'] = ROUNDINGS
    report['scope'] = 'general finite rational bank component; no Runtime/GPU authority, heap theorem or full native AMP error bound'
    assert 'torch' not in sys.modules
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    report = run()
    if args.write:
        (ROOT/'evidence/minimal/FP_COPRIME_LIKELIHOOD.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
