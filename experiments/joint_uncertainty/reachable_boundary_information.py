"""Exact count-reachable boundary grids and a dimension/precision counterexample.

All histories use the fixed native relation learner, uniform Gamma and unit U.
Auxiliary vertices describe posterior factors, not architecture actions.
"""
from fractions import Fraction as F
from itertools import combinations, product
from math import comb, prod
from pathlib import Path
import argparse
import json
import random
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts'), str(Path(__file__).parent)]
from fp_reference import ReferenceCompilerRuntime
from fp_reference.indexed_count import CountState
from fp_reference.semantics import evaluate
from audit_indexed_runtime import fixture, literal as native_fixture, step, check_prediction
from audit_reference_construction import validate_residency
from ingress_audit_support import deliver_context
from reachable_boundary_messages import patterns, valuation3


def layout(b, h):
    assert b >= 2 and h >= 0
    vertices, banks = b, []
    for size in range(2, min(2*h+2, b)+1, 2):
        for subset in combinations(range(b), size):
            if size == 2:
                edges = ((*subset, 1),)
            else:
                edges = []
                for signs in patterns(size, 1):
                    edges.extend((v, vertices, s) for v, s in zip(subset, signs))
                    vertices += 1
                edges = tuple(edges)
            banks.append((subset, edges))
    return vertices, tuple(banks)


def grid_state(b, h, levels, word):
    n, banks = layout(b, h)
    assert len(word) == len(banks) and all(0 <= t < levels for t in word)
    values = {tuple(sorted((u,v))): 2*t*s
              for (_,edges),t in zip(banks,word) for u,v,s in edges}
    edge_count = sum(len(edges) for _,edges in banks)
    assert len(values) == edge_count
    clock = 2*(levels-1)*edge_count
    return CountState(n, tuple(values.get(e, 0) for e in combinations(range(n),2)), None, clock, clock)


def grid_history(b, h, levels, word):
    _, banks = layout(b, h)
    return tuple((u,v,y) for (_,edges),t in zip(banks,word) for u,v,s in edges
                 for index in range(levels-1) for y in ((int(s < 0),)*2 if index < t else (0,1)))


def parity_values(size, t):
    if size == 2:
        return 9**(2*t), 1
    response = [1, 1]
    for r in range(size//2+1):
        multiplicity = comb(size,r)//2 if r == size//2 else comb(size,r)
        response[r % 2] *= (9**(2*t*r)+9**(2*t*(size-r)))**multiplicity
    return tuple(response)


def boundary_response(b, h, word):
    _, banks = layout(b, h)
    values = tuple(parity_values(len(subset), t) for (subset,_),t in zip(banks,word))
    return tuple(prod(pair[sum(sigma[v] for v in subset) % 2]
                      for (subset,_),pair in zip(banks,values))
                 for tail in product((0,1), repeat=b-1) for sigma in ((0,)+tail,))


def selected_moments(b, h, response):
    assignments = tuple((0,)+tail for tail in product((0,1), repeat=b-1))
    return tuple(F(sum(value*(-1)**sum(sigma[v] for v in subset)
                       for value,sigma in zip(response,assignments)), sum(response))
                 for subset,_ in layout(b,h)[1])


def full_world_response(state, b):
    """Independent literal world sum; never use star elimination here."""
    n = state.n
    assert n <= 8
    edges = tuple(combinations(range(n),2))
    response = [0]*(1 << (b-1))
    for word in range(1 << (n-1)):
        bits = (0,)+tuple((word >> (n-1-v)) & 1 for v in range(1,n))
        exponent = sum(max(d,0) if bits[u] == bits[v] else max(-d,0)
                       for (u,v),d in zip(edges,state.counts))
        response[word >> (n-b)] += 9**exponent
    return tuple(F(value,sum(response)) for value in response)


def discrete_parameters():
    checks = 0
    for size in (2,4,6,8,10):
        ratios = set()
        for t in range(5):
            a,b = parity_values(size,t)
            factor = 1 if size == 2 else (-1)**(size//2)*comb(size-2,size//2-1)
            assert valuation3(a)-valuation3(b) == 4*t*factor
            ratios.add(F(a,b))
            checks += 1
        assert len(ratios) == 5
    return checks


def grid_cases():
    results = []
    for b,h,levels in ((2,0,8),(3,0,4),(4,0,3),(4,1,3),(6,1,2)):
        n,banks = layout(b,h)
        dimension = len(banks)
        exhaustive = n <= 8
        if exhaustive:
            words = product(range(levels), repeat=dimension)
        else:
            rng = random.Random(20260921)
            integers = {0,(1 << dimension)-1}
            integers.update(1 << k for k in range(dimension))
            integers.update(((1 << dimension)-1) ^ (1 << k) for k in range(dimension))
            integers.update(rng.getrandbits(dimension) for _ in range(128))
            words = (tuple((word >> k) & 1 for k in range(dimension)) for word in sorted(integers))
        seen, native, largest = set(), 0, 0
        for word in words:
            state = grid_state(b,h,levels,word)
            response = boundary_response(b,h,word)
            moments = selected_moments(b,h,response)
            assert moments not in seen
            seen.add(moments)
            largest = max(largest, *(value.bit_length() for value in response))
            if exhaustive:
                assert full_world_response(state,b) == tuple(F(value,sum(response)) for value in response)
                native += 1
        assert not exhaustive or len(seen) == levels**dimension
        results.append({'boundary_vertices': b, 'boundary_horizon': h, 'native_vertices': n,
            'coordinate_count': dimension, 'levels': levels, 'common_observation_clock': state.steps,
            'grid_words_checked': len(seen), 'exhaustive_grid': exhaustive,
            'independent_full_world_marginals_checked': native,
            'maximum_unnormalized_message_bits': largest,
            'proved_family_class_count': levels**dimension,
            'proved_fixed_width_code_bits': (levels**dimension-1).bit_length()})
    return results


def owned_grid(word):
    b,h,levels = 4,1,2
    events = grid_history(b,h,levels,word)
    expected = grid_state(b,h,levels,word)
    assert len(events) == expected.steps == 44
    cfg,schema,online = fixture(expected.n, len(events)+1, byte_cap=1 << 30)
    runtime = ReferenceCompilerRuntime(cfg,schema,online=online)
    candidate = runtime.snapshot().candidates[0].candidate_id
    models = {candidate: native_fixture(expected.n)}
    for event in events:
        step(runtime,schema,event,models)
    before = validate_residency(runtime)
    assert before.candidates[0].learner.encoded == expected
    key = before.online.data.active.observation_ids[before.cursor]
    assert deliver_context(runtime,key,tuple(schema.source_row(1).values())).status == 'PREDICTED_REFERENCE'
    after = validate_residency(runtime)
    prediction = dict(after.pending.predictions)[candidate]
    rules,graph,spec,state = models[candidate]
    check_prediction(prediction,evaluate(graph,rules,state.theta,schema.source_row(1),(),bit_limit=32768))
    response = boundary_response(b,h,word)
    q0 = sum(response[:len(response)//2], 0)/F(sum(response))
    assert prediction.probabilities[0] == (1+8*q0)/10
    assert after.pending.record.target is None and after.cursor == 44
    return {'grid_word': list(word), 'actual_observations': 44,
        'full_native_caches_checked': 45, 'full_native_observed_and_committed_states_checked_each': 44,
        'owned_pre_target_query': [0,1], 'owned_noisy_forecast': str(prediction.probabilities[0]),
        'final_target_revealed': False,
        'packed_current_bytes': after.resources['current']['reference_payload_bytes']}


def two_path_precision():
    output = []
    for levels in (1,2,4,8,16,32):
        seen = {}
        for a,b in product(range(1,levels+1),repeat=2):
            odds = F((81**(2*a)+1)*(81**(2*b)+1),4*81**(a+b))
            assert valuation3(odds.numerator)-valuation3(odds.denominator) == -4*(a+b)
            seen.setdefault(odds,[]).append((a,b))
            values = {(0,2): 2*a, (1,2): 2*a, (0,3): 2*b, (1,3): 2*b}
            state = CountState(4,tuple(values.get(e,0) for e in combinations(range(4),2)),None,8*levels,8*levels)
            response = full_world_response(state,2)
            assert response[0]/response[1] == odds
            assert (1+8*response[0])/10 == (9*odds+1)/(10*(odds+1))
        assert len(seen) == comb(levels+1,2)
        assert all(set(rows) == {tuple(sorted(rows[0])),tuple(sorted(rows[0],reverse=True))} for rows in seen.values())
        output.append({'levels': levels, 'common_observation_clock': 8*levels,
            'ordered_count_states_checked': levels**2, 'distinct_boundary_future_classes': len(seen),
            'fixed_width_code_bits': (len(seen)-1).bit_length(), 'boundary_response_dimension': 1,
            'only_collisions': 'exchange of the two interior vertices'})
    return output


def audit():
    parameter_checks = discrete_parameters()
    grids = grid_cases()
    zero,one = (0,)*7,(1,)*7
    assert tuple(row[:2] for row in grid_history(4,1,2,zero)) == tuple(row[:2] for row in grid_history(4,1,2,one))
    owned = [owned_grid(word) for word in (zero,one)]
    return {'status': 'PASS_REACHABLE_BOUNDARY_INFORMATION',
        'scope': 'exact restricted boundary response in the fixed native count learner; legal common-clock histories, no complete Compiler quotient or physical saving',
        'discrete_parameter_valuation_checks': parameter_checks, 'grid_cases': grids, 'owned_CPU_cases': owned,
        'dimension_is_not_a_precision_upper_bound': two_path_precision(),
        'arbitrary_linear_message_grid_reachability': 'NOT_CLAIMED; a distinct reachable exponential family is proved'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true')
    args = parser.parse_args()
    report = audit()
    if args.write:
        (ROOT/'evidence/minimal/FP_REACHABLE_BOUNDARY_INFORMATION.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))
