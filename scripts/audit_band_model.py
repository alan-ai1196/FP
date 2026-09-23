"""Small exhaustive geometry and independent full-posterior control audit."""
from itertools import combinations, product
from pathlib import Path
import argparse
import json
import random
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'experiments/joint_uncertainty'), str(ROOT/'scripts')]
import band_model as band
from fp_reference.indexed_relation import DecodeAllowance, partition_shape_plan
from fp_reference import packed_histogram_decoder as packed
from adaptive_model import AdaptivePosterior
from audit_count_histogram import oracle, state
from audit_reference_construction import rejects


def run():
    shapes, maximum = 0, {'join': 0, 'live': 0, 'operations': 0}
    for n in range(2, 8):
        edges = tuple((i, j) for i, j in combinations(range(n), 2) if j-i <= 2)
        limit = band.bounds(n)
        for mask in range(1 << len(edges)):
            support = tuple(e for k, e in enumerate(edges) if mask >> k & 1)
            for pair in product(range(n), repeat=2):
                shape = partition_shape_plan(n, support, pair, tuple(range(n-1)), DecodeAllowance())
                operations = shape['positive_multiplications']+shape['positive_additions']
                assert shape['largest_join_cells'] <= limit['largest_join_cells']
                assert shape['peak_live_integer_cells'] <= limit['peak_live_integer_cells']
                assert operations <= limit['positive_operations']
                maximum = {'join': max(maximum['join'], shape['largest_join_cells']),
                           'live': max(maximum['live'], shape['peak_live_integer_cells']),
                           'operations': max(maximum['operations'], operations)}
                shapes += 1
    rng = random.Random(2026092301)
    predictions = histories = 0
    for n in range(2, 9):
        pairs = tuple((i, j) for i in range(n) for j in range(n) if abs(i-j) <= 2)
        for _ in range(8):
            joint, full = band.JointPosterior(n), AdaptivePosterior(n, (), 'iid')
            for _ in range(20):
                i, j = rng.choice(pairs)
                assert joint.predict(i, j) == full.predict(i, j)
                y = rng.randrange(2)
                joint.observe(y); full.observe(y)
                predictions += 1
            before = joint.state()
            for pair in ((0, n-1), (n-1, 0), (n-1, n-1)):
                parts, _, _ = band.exact_parts(before, pair)
                assert parts == oracle(before, pair)[1]
                plan = packed.passive_plan(before, pair, packed.PackedHistogramAllowance(
                    live_cells=1024, arithmetic=16384, span_cap=20))
                assert packed.exact_parts(plan) == parts
            histories += 1
    invalid = state(4, (0, 0, 1, 0, 0, 0))
    rejects(lambda: band.exact_parts(invalid, (0, 1)))
    controls = [band.control(case) for case in band.CASES]
    assert 'torch' not in sys.modules
    return {'status': 'PASS_BAND_MODEL_EXACT_CONTROL_AND_GEOMETRY',
        'all_support_and_query_geometry_cases': shapes, 'observed_small_maxima': maximum,
        'independent_full_assignment_histories': histories, 'independent_full_assignment_forecasts': predictions,
        'arbitrary_endpoint_and_diagonal_integer_controls': 3*histories,
        'off_width_nonzero_count_refusals': 1, 'n64_uniform_geometry_bound': band.bounds(64),
        'controls': controls, 'scope': 'exact resource theorem audit and deterministic controls; no actual AMP or population claim'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    report = run()
    if args.write:
        path = ROOT/'evidence/minimal/FP_BAND_MODEL_CONTROL.json'
        assert not path.exists(), 'retain source-bound control outcomes'
        path.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
