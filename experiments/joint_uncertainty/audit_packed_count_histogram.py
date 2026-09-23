"""Independent exact/native/RNE audits of carry-free histogram construction."""
from collections import Counter
from dataclasses import replace
from fractions import Fraction as F
from itertools import combinations, product
from pathlib import Path
from random import Random
from unittest.mock import patch
import argparse
import json
import math
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(Path(__file__).parent)]
import packed_count_histogram as packed
import audit_count_histogram as prior
import count_histogram as enumerated
from fp_reference import indexed_amp as amp, positive_partition
from fp_reference.indexed_count import CountState, observe
from fp_reference.indexed_execution import IndexedState
from fp_reference.indexed_relation import DecodeAllowance
from fp_reference.float64_bridge import Float64Contract
from fp_reference.semantics import ArithmeticUnresolved

TOLERANCE = Float64Contract(F(1, 100), F(1, 1000))
BOUND = packed.precision_bound()
ARTIFACT = ROOT/'evidence/minimal/FP_PACKED_COUNT_HISTOGRAM.json'


def state(n, values):
    height = sum(map(abs, values))
    return CountState(n, tuple(values), None, height, height)


def fixture(n, kind):
    values = tuple(((-1 if (i+j)%3 else 1)*(1+(i*j)%2) if j-i <= 2 else 0)
                   if kind == 'band' else int(j == i+1) if kind == 'path'
                   else 80 if kind == 'one' and (i, j) == (0, 1) else 0
                   for i, j in combinations(range(n), 2))
    return state(n, values), (0, 1) if kind == 'one' else (0, n-1)


def band_oracle(before, query, width):
    """Independent vertex-by-vertex count DP, not bucket elimination or big packing."""
    edges = dict(zip(combinations(range(before.n), 2), before.counts))
    assert all(j-i <= width or not value for (i, j), value in edges.items())
    # (last width assignment bits, queried parity so far, exact energy) -> multiplicity.
    rows = {(0, 0, 0): 1}
    for vertex in range(1, before.n):
        following = Counter()
        for (tail, parity, energy), count in rows.items():
            for bit in (0, 1):
                extra = 0
                for prior_vertex in range(max(0, vertex-width), vertex):
                    value = edges[prior_vertex, vertex]
                    old = (tail >> (vertex-1-prior_vertex)) & 1
                    extra += abs(value)*int((old ^ bit) == int(value < 0))
                new_parity = parity ^ (bit if query[0] != query[1] and vertex in query else 0)
                following[((tail << 1 | bit) & ((1 << width)-1), new_parity, energy+extra)] += count
        rows = following
    parts = [Counter(), Counter()]
    for (_, parity, energy), count in rows.items():
        parts[parity][energy] += count
    return tuple(tuple(sorted(part.items())) for part in parts)


class Audit:
    def __init__(self):
        self.predictions = self.observations = self.words = self.half = 0
        self.maximum = {key: F(0) for key in ('native', 'normalizer', 'probability',
                                              'proper_mass_division', 'gradient')}

    def check(self, plan):
        reference = packed.reference(plan)
        raw, trace = packed.rounded_prediction(plan)
        relation = amp.check_prediction(reference, raw, TOLERANCE, normalizer_cap=F(18),
                                        activation_cap=F(8), bit_limit=32768)
        measured = dict(zip(('native', 'normalizer', 'probability', 'proper_mass_division'),
            (relation.native_error, relation.normalizer_error, relation.probability_error,
             relation.division_error)))
        measured['gradient'] = F(0)
        self.predictions += 1
        self.words += len(trace)+7
        self.half += sum(width == 16 for _, width, _ in trace)
        for target in (0, 1):
            pending = observe(plan.before, *plan.query, target)
            mass = reference.masses[target]
            complete = IndexedState(pending, (1/mass-F(1, 5), F(4, 5)-8/mass, F(4, 5)))
            arithmetic = amp._Arithmetic(32768)
            actual, _ = amp._observation_schedule(amp.IndexedAmpState(plan.before), raw, target, arithmetic)
            relation = amp.check_state(complete, actual, TOLERANCE, bit_limit=32768)
            assert actual.encoded == pending
            measured['gradient'] = max(measured['gradient'], relation.state_error)
            self.observations += 1
            self.words += len(arithmetic.trace)+3
        for key, value in measured.items():
            assert value <= BOUND[key], (key, value, BOUND[key])
            self.maximum[key] = max(self.maximum[key], value)
        return {'n': plan.before.n, 'query': plan.query, 'span': plan.span,
            'histogram_terms': plan.term_count, 'floating_outputs': plan.output_cells,
            'largest_coefficient_bits': max(h.bit_length() for part in plan.terms for _, h in part),
            'integer_envelope': plan.integer_envelope, 'maximum_integer_bits': plan.maximum_integer_bits,
            'elimination': dict(plan.shape), 'probability0_word': raw.words[5],
            'errors': {key: str(value) for key, value in measured.items()}}


class NativeAdapter:
    @staticmethod
    def reference(before, query):
        plan = packed.prepare(before, query)
        return packed.reference(plan), plan

    @staticmethod
    def rounded_prediction(before, query):
        plan = packed.prepare(before, query)
        raw, trace = packed.rounded_prediction(plan)
        return raw, plan, trace


def run():
    audit = Audit()
    checks = Counter()
    for n in range(2, 5):
        for values in product((-1, 0, 1), repeat=n*(n-1)//2):
            before = state(n, values)
            checks['ternary_states'] += 1
            for query in product(range(n), repeat=2):
                plan = packed.prepare(before, query)
                expected, parts = prior.oracle(before, query)
                assert plan.terms == expected and packed.exact_parts(plan) == parts
                audit.check(plan)
                checks['lexicographic_world_histograms'] += 1
    print('small exact/native/RNE queries PASS', flush=True)

    rng = Random(20260923)
    for n in range(5, 9):
        for _ in range(12):
            values = tuple(rng.randint(-3, 3) for _ in range(n*(n-1)//2))
            before = state(n, values)
            query = rng.randrange(n), rng.randrange(n)
            order = list(range(n-1))
            rng.shuffle(order)
            plan = packed.prepare(before, query, order=tuple(order))
            expected, parts = prior.oracle(before, query)
            assert plan.terms == expected and packed.exact_parts(plan) == parts
            audit.check(plan)
            checks['random_dense_histograms'] += 1
    for n in range(2, 9):
        before, query = fixture(n, 'band')
        assert band_oracle(before, query, 2) == prior.oracle(before, query)[0]
        checks['independent_band_oracle_checks'] += 1

    larger = []
    for n, kind in ((32, 'band'), (64, 'band'), (128, 'path'), (256, 'empty'), (256, 'one')):
        before, query = fixture(n, kind)
        plan = packed.prepare(before, query)
        if kind == 'band':
            expected = band_oracle(before, query, 2)
        elif kind == 'path':
            expected = tuple(tuple((k, math.comb(n-1, k)) for k in range(n)
                                   if (n-1-k)%2 == y) for y in (0, 1))
        elif kind == 'empty':
            expected = (((0, 1 << (n-2)),),)*2
        else:
            expected = (((80, 1 << (n-2)),), ((0, 1 << (n-2)),))
        assert plan.terms == expected
        # A second arithmetic control at the native base, without rounded answers.
        assert packed.exact_parts(plan) == positive_partition.decode(n, before.counts, query, plan.order)[0]
        row = audit.check(plan)
        row.update({'kind': kind, 'anchored_world_count': str(1 << (n-1)),
                    'world_enumeration': False})
        larger.append(row)
    print('larger generic elimination and independent coefficients PASS', flush=True)

    with patch.object(prior, 'decoder', NativeAdapter):
        native = prior.native_histories()

    before = state(4, (1,)*6)
    cases = [({'budget': DecodeAllowance(integer_bits=1024)}, 'integer'),
             ({'span_cap': 5}, 'span'),
             ({'budget': DecodeAllowance(join_cells=1)}, 'join'),
             ({'budget': DecodeAllowance(live_cells=1)}, 'live'),
             ({'budget': DecodeAllowance(arithmetic=1)}, 'arithmetic')]
    for kwargs, name in cases:
        with patch.object(packed, '_eliminate', side_effect=AssertionError('numeric entry before admission')):
            try:
                packed.prepare(before, (0, 1), **kwargs)
            except ArithmeticUnresolved:
                checks['pre_numeric_refusals'] += 1
            else:
                raise AssertionError(name)
    dense = state(16, (1,)*120)
    try:
        packed.prepare(dense, (0, 1))
    except ArithmeticUnresolved:
        checks['dense_width_refusals'] += 1
    else:
        raise AssertionError('integer packing does not erase table width')
    plan = packed.prepare(before, (0, 1))
    with patch.object(packed, 'schedule', side_effect=AssertionError('unfunded rounded entry')):
        try:
            packed.rounded_prediction(plan, output_cap=plan.output_cells-1)
        except ArithmeticUnresolved:
            checks['floating_output_refusals'] += 1
        else:
            raise AssertionError('output preflight')

    # The uniform digit bound n is necessary if diagonal queries are included.
    n = 3
    worlds = 1 << (n-1)
    short_base = 1 << (n-1)
    low_digit, carry = worlds % short_base, worlds // short_base
    assert (low_digit, carry) == (0, 1)
    # Extending the old occupied-energy-only scale beyond n16 is unsound.
    before, query = fixture(256, 'empty')
    old = enumerated.Histogram(256, query, 0, (((0, 1 << 254),),)*2, 0, 0)
    try:
        enumerated._rounded_schedule(before, old, amp._Arithmetic(32768))
    except ArithmeticUnresolved as error:
        scale_failure = str(error)
    else:
        raise AssertionError('old coefficient-blind scale unexpectedly finite')
    bounds = packed.precision_bound()
    assert bounds['native'] < F(1, 100) and bounds['gradient'] < F(1, 100)
    assert bounds['probability'] < F(1, 1000)
    return {'status': 'PASS_PASSIVE_PACKED_COUNT_HISTOGRAM',
        'scope': 'exact/native/RNE research; no owned Runtime, actual CUDA or certificate claim',
        'checks': dict(checks), 'native_history_checks': native,
        'numerical': {'predictions': audit.predictions, 'both_target_observations': audit.observations,
            'words_including_copies': audit.words, 'half_words': audit.half,
            'maximum_errors': {k: str(v) for k, v in audit.maximum.items()},
            'maximum_errors_binary64_display': {k: float(v) for k, v in audit.maximum.items()}},
        'larger_cases': larger,
        'uniform_bounds': {k: str(v) for k, v in bounds.items()},
        'uniform_bounds_binary64_display': {k: float(v) for k, v in bounds.items()},
        'counterexamples': {'short_digit': {'n': n, 'worlds': worlds,
            'digit_width': n-1, 'wrong_constant_digit': low_digit, 'spurious_degree_one': carry},
            'old_scale_outside_its_class': {'n': 256, 'counts': 'all zero', 'query': query,
                'failure': scale_failure, 'old_n_le_16_theorem': 'unchanged'}}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--write', action='store_true')
    group.add_argument('--check', action='store_true')
    args = parser.parse_args()
    report = run()
    if args.write:
        ARTIFACT.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    else:
        assert json.loads(ARTIFACT.read_text(encoding='utf-8')) == report
    print(json.dumps(report, indent=2))
