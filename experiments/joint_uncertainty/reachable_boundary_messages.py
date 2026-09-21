"""Reach pure higher-order boundary messages by legal native count histories.

The factor graph below describes a posterior inside the existing fixed
relation program. It is not a new learner architecture or parameter upload.
"""
from fractions import Fraction as F
from itertools import combinations, product
from math import comb, prod
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts'), str(Path(__file__).parent)]
from fp_reference import ReferenceCompilerRuntime
from fp_reference.indexed_count import CountState
from audit_indexed_runtime import fixture, literal as native_fixture, step, check_prediction
from audit_reference_construction import validate_residency
from ingress_audit_support import deliver_context
from query_block_projection import literal


def patterns(b, sign):
    assert b >= 4 and b % 2 == 0 and sign in (-1, 1)
    return tuple((1,)+tail for tail in product((-1, 1), repeat=b-1) if prod(tail) == sign)


def history(b, sign):
    return tuple((v, b+h, int(s < 0)) for h, row in enumerate(patterns(b, sign)) for v, s in enumerate(row))


def count_state(b, sign):
    events = history(b, sign)
    n = b+(1 << (b-2))
    values = {(i,j): 1-2*y for i,j,y in events}
    assert len(values) == len(events) == b*(1 << (b-2))
    return CountState(n, tuple(values.get(e, 0) for e in combinations(range(n), 2)), None, len(events), len(events))


def boundary_message(b, sign):
    representatives = patterns(b, sign)
    factors = tuple(9**r+9**(b-r) for r in range(b+1))
    output = []
    for assignment in product((1, -1), repeat=b-1):
        sigma = (1,)+assignment
        output.append(prod(factors[sum(s == t for s,t in zip(row,sigma))] for row in representatives))
    return tuple(output)


def valuation3(value):
    result = 0
    while value % 3 == 0:
        value //= 3
        result += 1
    return result


def closed_pair(b):
    result = [1, 1]
    for r in range(b//2+1):
        multiplicity = comb(b,r)//2 if r == b//2 else comb(b,r)
        result[r % 2] *= (9**r+9**(b-r))**multiplicity
    return tuple(result)


def transformed(values):
    """Exact Fourier audit; signed arithmetic supplies no native operation."""
    values = list(values)
    width = 1
    while width < len(values):
        for block in range(0, len(values), 2*width):
            for k in range(block, block+width):
                a, b = values[k], values[k+width]
                values[k], values[k+width] = a+b, a-b
        width *= 2
    return tuple(values)


def symbolic_cases():
    results = []
    for b in (4, 6, 8, 10):
        a, c = closed_pair(b)
        difference = valuation3(a)-valuation3(c)
        assert difference == 2*(-1)**(b//2)*comb(b-2,b//2-1) != 0
        messages = tuple(boundary_message(b, sign) for sign in (1, -1))
        for message, sign in zip(messages, (1, -1)):
            for word, value in enumerate(message):
                expected = (a,c) if sign == 1 else (c,a)
                assert value == expected[word.bit_count() % 2]
            fourier = transformed(message)
            assert all(value == 0 for k,value in enumerate(fourier) if k not in (0,len(message)-1))
            assert fourier[-1] != 0
            encoded = count_state(b, sign)
            assert encoded.steps == b*(1 << (b-2)) and max(map(abs, encoded.counts)) == 1
        results.append({'boundary_vertices': b, 'interior_vertices': 1 << (b-2),
            'native_vertices': b+(1 << (b-2)), 'legal_observations_per_history': b*(1 << (b-2)),
            'nonzero_count_magnitude': 1, 'boundary_assignments_per_history': 1 << (b-1),
            'nonconstant_Fourier_support': 'full boundary character only',
            'valuation3_difference': difference, 'maximum_message_integer_bits': max(a.bit_length(),c.bit_length()),
            'indistinguishable_boundary_horizon': b//2-2,
            'first_distinguishing_boundary_observation_count': b//2-1})
    return results


def owned_case(sign):
    b, n = 4, 8
    events = history(b, sign)
    expected_count = count_state(b, sign)
    cfg, schema, online = fixture(n, len(events)+2, byte_cap=1 << 30)
    rt = ReferenceCompilerRuntime(cfg, schema, online=online)
    candidate = rt.snapshot().candidates[0].candidate_id
    models = {candidate: native_fixture(n)}
    for event in events:
        step(rt, schema, event, models)
    snapshot = validate_residency(rt)
    actual = snapshot.candidates[0].learner
    assert actual.encoded == expected_count
    all_pairs, weights = literal(n, expected_count.counts)
    assert all(all_pairs[pair] == F(1,2) for pair in combinations(range(b),2))
    assert models[candidate][3].theta[1:] == weights
    message = boundary_message(b, sign)
    projected = []
    for prefix in range(1 << (b-1)):
        # Both literal and native oracles use most-significant earlier vertices.
        selected = weights[prefix << (n-b):(prefix+1) << (n-b)]
        projected.append(sum(selected))
    assert projected == [F(value,sum(message)) for value in message]
    step(rt, schema, (0,1,0), models)
    before = rt.snapshot()
    key = before.online.data.active.observation_ids[before.cursor]
    result = deliver_context(rt, key, tuple(schema.source_row(2*n+3).values()))
    assert result.status == 'PREDICTED_REFERENCE', result
    snapshot = validate_residency(rt)
    prediction = dict(snapshot.pending.predictions)[candidate]
    rules, graph, spec, state = models[candidate]
    from fp_reference.semantics import evaluate
    check_prediction(prediction, evaluate(graph, rules, state.theta, schema.source_row(2*n+3), (), bit_limit=32768))
    a, c = closed_pair(b)
    strength = F(a-c,a+c)*sign
    expected = F(1,2)+F(8,25)*strength
    assert prediction.probabilities[0] == expected
    assert snapshot.cursor == len(events)+1 and snapshot.pending.record.target is None
    return {'pattern_sign': sign, 'actual_history': list(map(list,events)),
        'native_vertices': n, 'actual_observations': snapshot.cursor,
        'full_native_caches_checked': len(events)+2,
        'full_native_observed_and_committed_states_checked_each': len(events)+1,
        'all_current_boundary_pair_forecasts': '1/2',
        'common_boundary_observation': [0,1,0], 'next_owned_query': [2,3],
        'owned_noisy_forecast': str(expected), 'final_target_revealed': False,
        'packed_current_bytes': snapshot.resources['current']['reference_payload_bytes']}


def audit():
    cases = symbolic_cases()
    owned = [owned_case(sign) for sign in (1,-1)]
    assert [row['owned_noisy_forecast'] for row in owned] == ['726561/3091522','2364961/3091522']
    a,c = closed_pair(4)
    return {'status': 'PASS_REACHABLE_BOUNDARY_MESSAGES',
        'scope': 'legal histories inside the existing native count learner; restricted boundary future sharpness; no new architecture, GPU run or resource advantage',
        'general_identity': 'v3(M_even)-v3(M_odd)=2*(-1)^(b/2)*binom(b-2,b/2-1)',
        'symbolic_cases': cases, 'small_exact_message_values': [a,c],
        'small_absolute_parity_coefficient': str(F(abs(a-c),a+c)), 'owned_CPU_cases': owned,
        'arbitrary_message_grid_reachability': 'NOT_CLAIMED'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    report = audit()
    if args.write:
        (ROOT/'evidence/minimal/FP_REACHABLE_BOUNDARY_MESSAGES.json').write_text(json.dumps(report,indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report,indent=2))
