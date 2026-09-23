"""Exact independent-control audit before the four unknown-noise model jobs."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json
import random
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'experiments/joint_uncertainty')]
import unknown_noise_model as model
from unknown_noise_decoding import Joint, DEFAULT, OTHER
from fp_reference.joint_relation import JointRelation, JointCountState
from fp_reference import joint_partition_decoder as decoder

BUDGET = decoder.JointPartitionAllowance(join_cells=64, live_cells=1024, arithmetic=32768, step_cap=396)
OUTPUT = ROOT/'evidence/minimal/FP_UNKNOWN_NOISE_MODEL_CPU.json'


def run():
    forecasts = coordinates = native_parts = 0
    for n in range(2, 6):
        for rates, prior in (DEFAULT, OTHER):
            schema = JointRelation(n, rates, prior)
            for seed in range(4):
                rng = random.Random(923700+100*n+seed)
                full, independent = Joint(n, rates, prior), model.JointControl(n, rates, prior)
                weights = full.initial
                pairs = tuple((i, j) for i in range(n) for j in range(n) if abs(i-j) <= 2)
                for step in range(12):
                    pair = rng.choice(pairs)
                    result = independent.predict(*pair)
                    expected = tuple(full.forecast(weights, pair+(y,)) for y in (0, 1))
                    assert result.joint == expected
                    assert result.rate_posterior == tuple(F(sum(weights[j*len(full.worlds):(j+1)*len(full.worlds)]), sum(weights))
                                                         for j in range(len(rates)))
                    for j in range(len(rates)):
                        expected_parts = tuple(sum(w for w, z in zip(weights[j*len(full.worlds):(j+1)*len(full.worlds)], full.worlds)
                                                    if z[pair[0]]^z[pair[1]] == y) for y in (0, 1))
                        assert result.rate_parts[j] == expected_parts
                    d, s, t = independent.coordinates()
                    before = JointCountState(schema, d, s, step, t)
                    assert full.counts(t, d, s) == weights
                    plan = decoder.passive_plan(before, pair, BUDGET)
                    assert sum(sum(v) for v in result.rate_parts) == plan.normalization
                    assert decoder.reference(plan)[-2:] == result.joint
                    native_parts += 1
                    forecasts += 1
                    target = rng.randrange(2)
                    independent.observe(target)
                    weights = full.update(weights, pair+(target,))
                    coordinates += 1
                # A nonlocal query does not alter the retained width class.
                for pair in ((0, n-1), (n-1, 0), (n-1, n-1)):
                    assert independent.forecast(pair).joint == tuple(full.forecast(weights, pair+(y,)) for y in (0, 1))
                    forecasts += 1
    # Every label word on a four-edge forest leaves the full rate prior intact.
    forest_words = 0
    for labels in product((0, 1), repeat=4):
        control = model.JointControl(5)
        for i, target in enumerate(labels):
            answer = control.predict(i, i+1)
            assert answer.rate_posterior == model.PRIOR and answer.joint == (F(1, 2),)*2
            control.observe(target)
        assert control.forecast((0, 4)).rate_posterior == model.PRIOR
        forest_words += 1
    refused = model.JointControl(4)
    refused.labels[0, 3][0] = 1
    try:
        refused.forecast((0, 1))
    except AssertionError:
        pass
    else:
        raise AssertionError('off-band history was silently erased')
    geometry = json.loads((ROOT/'evidence/minimal/FP_BAND_MODEL_CONTROL.json').read_text())
    assert geometry['status'] == 'PASS_BAND_MODEL_EXACT_CONTROL_AND_GEOMETRY'
    assert geometry['all_support_and_query_geometry_cases'] == 122576
    # Geometry already has an exhaustive audit. This proof adds rate aggregation
    # and powers, rather than rerunning the same support enumeration.
    bound = 2*(212*64-195+4*375+14)
    assert bound == 29774 < BUDGET.arithmetic
    schema = JointRelation(64, *DEFAULT)
    declaration = []
    for case in model.CASES:
        hidden, train, evaluation = model.data(case)
        assert len(hidden) == 64 and len(train) == 126 and len(evaluation) == 250
        assert len({(i, j) for i, j, _ in evaluation}) == 250
        assert sum(abs(i-j) == 2 for i, j, _ in evaluation) == 124
        assert tuple((i, j) for i, j, _ in train[:63]) == tuple((i, i+1) for i in range(63))
        assert tuple((i, j) for i, j, _ in train[63:]) == tuple((i, i+1) for i in range(63))
        declaration.append({'case': case, 'forest_events': 63, 'repeat_events': 63, 'evaluation_events': 250})
    assert 'torch' not in sys.modules
    return {'status': 'PASS_UNKNOWN_NOISE_MODEL_CPU', 'small_full_assignment_forecasts': forecasts,
        'complete_unsigned_count_matches': coordinates, 'packed_native_partition_checks': native_parts,
        'all_four_edge_forest_label_words': forest_words, 'off_band_refusals': 1,
        'retained_geometry_cases': 122576, 'all_labels_bounds': {'join': 32, 'live_cells': 832,
            'joint_positive_operations': bound, 'integer_envelope': 1946, 'readout_bit_guard': 2970,
            'prediction_outputs': 29, 'observation_outputs': 22},
        'paid_workspace_bytes': decoder.workspace_bytes(schema, BUDGET), 'declaration': declaration,
        'scope': 'exact control/native resource audit; no actual model score inspected, Torch or device execution'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = run()
    if args.write:
        assert not OUTPUT.exists(), 'retain original pre-model audit'
        OUTPUT.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
