"""Exact, passive native/rounding/resource audit of exponent histograms."""
from collections import Counter
from fractions import Fraction as F
from itertools import combinations, product
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(Path(__file__).parent)]
import count_histogram as decoder
import count_learner_encoding as native
from fp_reference import indexed_amp as amp
from fp_reference.binary_arithmetic import round_binary
from fp_reference.core import ContractError
from fp_reference.cuda_range import SINGLE
from fp_reference.float64_bridge import Float64Contract
from fp_reference.indexed_count import CountState, observe, commit, attach
from fp_reference.indexed_execution import IndexedState
from fp_reference.indexed_relation import DecodeAllowance, partition_shape_plan
from fp_reference.learner import observe_event, commit_event
from fp_reference.profile import attach_boundary
from fp_reference.semantics import ArithmeticUnresolved, evaluate
from joint_model import data

TOLERANCE = Float64Contract(F(1, 100), F(1, 1000))
BOUND = decoder.precision_bound()


def oracle(state, query):
    """Independent lexicographic worlds and signed equality scores, no Gray update."""
    edges = tuple(combinations(range(state.n), 2))
    offset = sum(-d for d in state.counts if d < 0)
    bins, totals = [Counter(), Counter()], [0, 0]
    for tail in product((0, 1), repeat=state.n-1):
        bits = (0,)+tail
        score = sum(d for (i, j), d in zip(edges, state.counts) if bits[i] == bits[j])
        degree = score+offset
        parity = bits[query[0]] ^ bits[query[1]]
        bins[parity][degree] += 1
        totals[parity] += 9**degree
    return tuple(tuple(sorted(part.items())) for part in bins), tuple(totals)


def state(n, counts):
    H = sum(map(abs, counts))
    return CountState(n, tuple(counts), None, H, H)


class NumericalAudit:
    def __init__(self):
        self.predictions = self.observations = self.words = self.half = 0
        self.maximum = {key: F(0) for key in ('native', 'normalizer', 'probability',
                                             'proper_mass_division', 'gradient')}

    def check(self, before, query):
        hist = decoder.histogram(before, query)
        bins, parts = oracle(before, query)
        assert hist.terms == bins and decoder.exact_parts(hist) == parts
        reference, _ = decoder.reference(before, query)
        assert reference.excesses == tuple(F(8*z, sum(parts)) for z in parts)
        raw, physical_hist, trace = decoder.rounded_prediction(before, query)
        assert physical_hist == hist and raw.before == before and raw.query == query
        relation = amp.check_prediction(reference, raw, TOLERANCE, normalizer_cap=F(18),
                                        activation_cap=F(8), bit_limit=32768)
        measured = dict(zip(('native', 'normalizer', 'probability', 'proper_mass_division'),
            (relation.native_error, relation.normalizer_error,
             relation.probability_error, relation.division_error)))
        measured['gradient'] = F(0)
        self.predictions += 1
        self.words += len(trace)+7
        self.half += sum(width == 16 for _, width, _ in trace)
        for target in (0, 1):
            following = observe(before, *query, target)
            mass = reference.masses[target]
            complete = IndexedState(following, (1/mass-F(1, 5), F(4, 5)-8/mass, F(4, 5)))
            rounded, trace = decoder.rounded_observation(before, raw, target)
            relation = amp.check_state(complete, rounded, TOLERANCE, bit_limit=32768)
            assert rounded.encoded == following
            measured['gradient'] = max(measured['gradient'], relation.state_error)
            self.observations += 1
            self.words += len(trace)+3
        for key, value in measured.items():
            assert value <= BOUND[key], (before, query, key, value, BOUND[key])
            self.maximum[key] = max(self.maximum[key], value)
        return {'H': hist.span, 'world_visits': hist.world_visits,
            'incident_visits': hist.incident_visits, 'nonzero_terms': hist.term_count,
            'output_cells': hist.output_cells, 'half_outputs': 3*hist.term_count,
            'exact_probability0': str(reference.probabilities[0]),
            'RNE_probability0_word': raw.words[5],
            'errors': {key: str(value) for key, value in measured.items()}}

    def report(self):
        return {'predictions': self.predictions, 'both_target_observations': self.observations,
            'RNE_words_including_declared_output_copies': self.words,
            'binary16_words': self.half,
            'maximum_errors': {key: str(value) for key, value in self.maximum.items()},
            'maximum_errors_binary64_display': {key: float(value) for key, value in self.maximum.items()}}


def exhaustive(audit):
    cases = []
    for n in range(2, 5):
        states = queries = 0
        for counts in product((-1, 0, 1), repeat=n*(n-1)//2):
            before = state(n, counts)
            for query in product(range(n), repeat=2):
                audit.check(before, query)
                queries += 1
            states += 1
        cases.append({'n': n, 'complete_signed_states': states, 'ordered_queries': queries})
    return cases


def native_histories():
    counters = Counter()
    def step(n, reference, encoded, event):
        i, j, target = event
        rules, graph, _ = native.native.relation_graph(n)
        actual = evaluate(graph, rules, reference.theta, native.native.context(n, i, j), (), bit_limit=32768)
        decoded, _ = decoder.reference(encoded, (i, j))
        assert decoded.materialize(scalar_cap=10000) == actual
        observed = observe_event(graph, reference, native.spec(n), actual, target, bit_limit=32768)
        pending = observe(encoded, i, j, target)
        mass = decoded.masses[target]
        indexed = IndexedState(pending, (1/mass-F(1, 5), F(4, 5)-8/mass, F(4, 5)))
        assert tuple(indexed.gradient(k) for k in range(len(observed.theta))) == observed.gradient_sum
        assert native.decode(pending) == observed
        committed = commit_event(observed, native.spec(n), bit_limit=32768)
        following = commit(pending)
        assert native.decode(following) == committed
        counters['complete_native_caches'] += 1
        counters['full_observed_states'] += 1
        counters['full_committed_states'] += 1
        return committed, following

    for n, depth in ((2, 3), (3, 2)):
        levels = [(native.native_initial(n), native.initialize(n))]
        for _ in range(depth):
            levels = [step(n, actual, encoded, event) for actual, encoded in levels
                      for event in product(range(n), range(n), (0, 1))]
        counters['terminal_native_histories'] += len(levels)
    profile = ((0, 1, 0), (1, 2, 1), (0, 2, 0))
    for passes in (1, 2, 3):
        actual, encoded = native.native_initial(3), native.initialize(3)
        for event in profile*passes:
            actual, encoded = step(3, actual, encoded, event)
        actual = attach_boundary(actual, 20, native.spec(3))
        encoded = attach(encoded, 20)
        assert native.decode(encoded) == actual
        for event in ((2, 0, 1), (0, 0, 0)):
            actual, encoded = step(3, actual, encoded, event)
        counters['profile_attachment_continuations'] += 1
    # A term rounds to zero at the physical endpoint, but its native weight
    # survives in the retained counts and returns under legal contrary data.
    actual, encoded = native.native_initial(2, 7), native.initialize(2, 7)
    midpoint = None
    for k, event in enumerate(((0, 1, 0),)*52+((0, 1, 1),)*52):
        actual, encoded = step(2, actual, encoded, event)
        if k == 51:
            raw, _, trace = decoder.rounded_prediction(encoded, (0, 1))
            midpoint = {'counts': encoded.counts, 'rounded_unlikely_excess': str(amp.single(raw.words[1])),
                'native_unlikely_excess': str(decoder.reference(encoded, (0, 1))[0].excesses[1]),
                'half_operations': sum(width == 16 for _, width, _ in trace)}
            assert amp.single(raw.words[1]) == 0 and decoder.reference(encoded, (0, 1))[0].excesses[1] > 0
    raw, _, _ = decoder.rounded_prediction(encoded, (0, 1))
    assert encoded.counts == (0,) and encoded.cursor == 111 and encoded.steps == 104
    assert actual.theta == (F(1), F(1, 2), F(1, 2)) and amp.single(raw.words[5]) == F(1, 2)
    return {'checks': dict(counters), 'reversal': {'midpoint': midpoint,
        'events': 104, 'final_counts': encoded.counts, 'final_clock': (encoded.cursor, encoded.steps),
        'final_probability0': str(amp.single(raw.words[5]))}}


def dense_obstructions(audit):
    n, support = 16, tuple(combinations(range(16), 2))
    reports = []
    for sign, query in ((1, (0, 1)), (-1, (1, 2))):
        before = state(n, (sign,)*120)
        forbidden = 0
        for first in range(1, n):
            if first in query:
                continue
            # All possible first eliminated vertices; later order is irrelevant
            # because its first complete-graph join already has32768 cells.
            order = (first-1,)+tuple(v for v in range(n-1) if v != first-1)
            try:
                partition_shape_plan(n, support, query, order, DecodeAllowance())
            except ArithmeticUnresolved:
                forbidden += 1
            else:
                raise AssertionError('complete-graph first join unexpectedly fits4096')
        assert forbidden == n-1-len(set(query)-{0})
        row = audit.check(before, query)
        assert row['nonzero_terms'] == 17 and row['output_cells'] == 170
        row.update({'sign': sign, 'query': query, 'every_first_elimination_refused': forbidden,
                    'first_join_cells_for_every_order': 32768, 'join_limit': 4096})
        reports.append(row)
    return reports


def model_cuts(audit):
    cases = (((16, 'iid-c2', 16), 194, (6, 9)),
             ((16, 'iid-c2', 17), 332, (8, 7)),
             ((16, 'iid-c4', 18), 276, (2, 5)),
             ((16, 'iid-c4', 18), 372, (15, 1)),
             ((16, 'iid-c4', 19), 368, (4, 13)))
    reports = []
    for case, cursor, query in cases:
        _, _, train, evaluation = data(case)
        tape = train+evaluation
        assert tape[cursor][:2] == query
        indices = {edge: k for k, edge in enumerate(combinations(range(case[0]), 2))}
        counts = [0]*len(indices)
        for i, j, target in tape[:cursor]:
            if i != j:
                counts[indices[tuple(sorted((i, j)))]] += 1-2*target
        before = CountState(case[0], tuple(counts), None, cursor, cursor)
        row = audit.check(before, query)
        row.update({'case': case, 'cursor': cursor, 'query': query,
            'scope': 'passive exposed-prefix decode; no Runtime continuation or model score'})
        reports.append(row)
    return reports


def future_counterexample():
    left, right = state(3, (1, 1, 0)), state(3, (1, 0, 1))
    a, b = (decoder.reference(v, (0, 1)) for v in (left, right))
    assert a[1].terms == b[1].terms and a[0].probabilities == b[0].probabilities
    later = tuple(decoder.reference(v, (0, 2))[0].probabilities[0] for v in (left, right))
    assert later == (F(41, 50), F(189, 250))
    assert native.decode(left) != native.decode(right)
    return {'legal_histories': (((0, 1, 0), (0, 2, 0)), ((0, 1, 0), (1, 2, 0))),
        'same_histogram_query': (0, 1), 'current_probability0': str(a[0].probabilities[0]),
        'later_query': (0, 2), 'later_probability0': tuple(map(str, later)),
        'histogram_is_a_complete_persistent_state': False}


def unfunded_scale_shortcut(audit):
    before, query = state(3, (-80, -80, -80)), (0, 1)
    hist = decoder.histogram(before, query)
    top = max(k for part in hist.terms for k, _ in part)
    assert (hist.span, top) == (240, 160)
    # Giving even exact terms a single RNE32 rounding cannot rescue this
    # looser scale: all three grouped terms fall below half a subnormal.
    loose = tuple(F(h, 9**(hist.span-k)) for part in hist.terms for k, h in part)
    assert max(loose) < F(1, 1 << 150)
    rounded = tuple(round_binary(v, SINGLE, bit_limit=32768).value for v in loose)
    assert rounded == (F(0),)*3
    correct = audit.check(before, query)
    return {'n': 3, 'counts': before.counts, 'query': query, 'H': hist.span,
        'actual_maximum_occupied_exponent': top, 'H_scaled_RNE32_terms': list(map(str, rounded)),
        'H_scaled_denominator': '0', 'correct_occupied_scale': correct,
        'scope': 'the registered schedule cannot replace its computed occupied maximum by H for free'}


def refusals():
    ordinary = state(3, (1, -1, 1))
    inputs = ((object(), (0, 1), {}), (observe(ordinary, 0, 1, 0), (0, 1), {}),
        (ordinary, [0, 1], {}), (ordinary, (False, 1), {}), (ordinary, (0, 3), {}),
        (ordinary, (0, 1), {'world_cap': 3}), (ordinary, (0, 1), {'span_cap': 2}),
        (ordinary, (0, 1), {'bit_limit': 100}), (ordinary, (0, 1), {'span_cap': True}),
        (state(17, (0,)*136), (0, 1), {}), (state(16, (1,)*120), (0, 1), {'world_cap': 32767}))
    checked = 0
    with patch.object(decoder, '_enumerate', side_effect=AssertionError('unfunded enumeration')) as entry:
        for before, query, limits in inputs:
            try:
                decoder.histogram(before, query, **limits)
            except (ContractError, ArithmeticUnresolved):
                checked += 1
            else:
                raise AssertionError('invalid or short declaration accepted')
        assert entry.call_count == 0
    cells = decoder.histogram(ordinary, (0, 1)).output_cells
    with patch.object(decoder, '_Arithmetic', side_effect=AssertionError('unfunded rounding')) as entry:
        try:
            decoder.rounded_prediction(ordinary, (0, 1), output_cap=cells-1)
        except ArithmeticUnresolved:
            checked += 1
        else:
            raise AssertionError('short numerical output allowance accepted')
        assert entry.call_count == 0
    return {'before_enumeration': len(inputs), 'before_rounding': 1, 'total': checked,
            'excluded_kernel_calls': 0, 'no_complete_class_certificate': True}


def bounds():
    result = []
    for limit in (794, 32768):
        bound = decoder.precision_bound(limit)
        assert max(bound['native'], bound['normalizer'], bound['gradient']) < F(1, 100)
        assert max(bound['probability'], bound['proper_mass_division']) < F(1, 1000)
        result.append({key: str(value) if type(value) is F else value for key, value in bound.items()})
    for q in (F(0), F(1, 10), F(1, 2), F(9, 10), F(1)):
        assert (1+8*q)**2-36*q*(1-q) == (1-10*q)**2
        assert q*(1-q)/(1+8*q)**2 <= F(1, 36)
    assert F(1, 10)*F(9, 10)/(1+8*F(1, 10))**2 == F(1, 36)
    return result


def run():
    audit = NumericalAudit()
    small = exhaustive(audit)
    print('PASS exhaustive histograms and complete rounded coordinates', flush=True)
    native_cases = native_histories()
    dense = dense_obstructions(audit)
    cuts = model_cuts(audit)
    stress = []
    for before, query in ((state(2, (396,)), (0, 1)), (state(2, (-396,)), (1, 0)),
                         (state(4, (198, -100, 40, -20, 20, -18)), (0, 3))):
        stress.append(audit.check(before, query))
    scale_shortcut = unfunded_scale_shortcut(audit)
    return {'status': 'PASS_SCOPED_EXACT_HISTOGRAM_AND_RNE_AUDIT',
        'scope': 'passive decoder, exact native states and RNE; no actual CUDA or Runtime registration',
        'small_complete_grid': small, 'native': native_cases,
        'numerical': audit.report(), 'exact_uniform_bounds': bounds(),
        'dense_all_order_obstructions': dense, 'exposed_model_cuts': cuts,
        'range_stress': stress, 'future_histogram_counterexample': future_counterexample(),
        'local_upper_bound_scale_counterexample': scale_shortcut,
        'preflight_refusals': refusals()}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--output', type=Path, default=ROOT/'evidence/minimal/FP_COUNT_HISTOGRAM.json')
    args = parser.parse_args()
    report = run()
    if args.check:
        assert json.loads(args.output.read_text(encoding='utf-8')) == json.loads(json.dumps(report))
    else:
        args.output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], **report['numerical']}), flush=True)
