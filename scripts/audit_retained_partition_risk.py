"""Exact posterior/AMP error and KL enclosures from retained model readouts."""
from decimal import Decimal, localcontext
from fractions import Fraction as F
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'experiments/joint_uncertainty')]
import run_direct_partition_model as direct
import integer_partition as arithmetic
from fp_reference import indexed_amp as amp

GRID = 96
UNIT = 1 << GRID


def kl_interval(p, q):
    """Integrate (q-p)/(q*(1-q)); bound the positive denominator on its segment."""
    assert 0 < p < 1 and 0 < q < 1
    ends = (p*(1-p), q*(1-q))
    maximum = F(1, 4) if min(p, q) <= F(1, 2) <= max(p, q) else max(ends)
    square = (p-q)**2
    return square/(2*maximum), square/(2*min(ends))


def grid_interval(low, high):
    assert 0 <= low <= high
    a, b = low*UNIT, high*UNIT
    return a.numerator//a.denominator, -(-b.numerator//b.denominator)


def interval_checks():
    pairs = ((F(1, 10), F(1, 10)), (F(1, 10), F(9, 10)),
        (F(2, 5), F(3, 5)), (F(1, 10), F(1001, 10000)),
        (F(1, 2), F(4999, 10000)), (F(9, 10), F(8999, 10000)))
    with localcontext() as context:
        context.prec = 80
        def decimal(value):
            return Decimal(value.numerator)/Decimal(value.denominator)
        for p, q in pairs+tuple((q, p) for p, q in pairs):
            low, high = kl_interval(p, q)
            x, y = decimal(p), decimal(q)
            actual = x*(x/y).ln()+(1-x)*((1-x)/(1-y)).ln()
            assert decimal(low) <= actual <= decimal(high)
    return {'exact_segment_bound_decimal_checks': 12, 'interior_one_half_case_checked': True}


def audit_case(case, rows):
    _, _, train, evaluation = direct.band.data(case)
    groups = {name: set(pairs) for name, pairs in direct.band.scoring_groups(case)}
    reader = direct.band.JointPosterior(case[0], (), case[1])
    for i, j, target in train:
        reader.predict(i, j)
        reader.observe(target)
    bound = arithmetic.precision_bound()
    totals = {mode: {name: {'count': 0, 'kl_low': 0, 'kl_high': 0,
        'brier_low': 0, 'brier_high': 0, 'error': F(0), 'error_index': 0}
        for name in groups} for mode in rows}
    for index, (i, j, target) in enumerate(evaluation):
        p = reader.predict(i, j)[0]
        assert F(1, 10) <= p <= F(9, 10)
        for mode, result in rows.items():
            words = result['evaluation_readouts'][index]
            masses = tuple(amp.single(word) for word in words[:2])
            assert all(1 <= mass <= 9 for mass in masses)
            q = masses[0]/sum(masses)
            error = abs(p-q)
            assert F(1, 10) <= q <= F(9, 10) and error <= F(1, 1000)
            if mode == 'direct-partition':
                assert error <= bound['probability']
                raw = tuple(amp.single(word) for word in words[2:])
                assert max(abs(raw[0]-p), abs(raw[1]-(1-p))) <= bound['probability']
                assert max(abs(raw[0]-q), abs(raw[1]-(1-q))) <= bound['proper_mass_division']
            lower, upper = grid_interval(*kl_interval(p, q))
            brier_low, brier_high = grid_interval(2*error**2, 2*error**2)
            for name, pairs in groups.items():
                if (i, j) not in pairs:
                    continue
                acc = totals[mode][name]
                acc['count'] += 1
                acc['kl_low'] += lower
                acc['kl_high'] += upper
                acc['brier_low'] += brier_low
                acc['brier_high'] += brier_high
                if error > acc['error']:
                    acc['error'], acc['error_index'] = error, index
        reader.observe(target)
    results = []
    for mode, values in totals.items():
        for name, acc in values.items():
            count = acc['count']
            assert count == len(groups[name])
            lo, hi = (F(acc['kl_'+side], count*UNIT) for side in ('low', 'high'))
            maximum = acc['error']
            # Both proper probabilities are in [1/10,9/10], so the entire
            # segment has r*(1-r)>=9/100. This needs no logarithm rounding.
            assert 0 <= lo <= hi <= F(50, 9)*maximum**2+F(1, UNIT)
            results.append({'mode': mode, 'group': name, 'contexts': count,
                'maximum_probability_error_exact': str(maximum),
                'maximum_probability_error_binary64': float(maximum),
                'maximum_error_evaluation_index': acc['error_index'],
                'mean_reference_to_proper_AMP_KL_exact_enclosure': [str(lo), str(hi)],
                'mean_KL_upper_binary64': float(hi),
                'mean_conditional_Brier_excess_exact_enclosure': [
                    str(F(acc['brier_'+side], count*UNIT)) for side in ('low', 'high')],
                'fixed_teacher_expected_CE_gap_binary64': rows[mode]['scores']['AMP_'+name]['expected_CE_binary64']
                    -rows[mode]['scores']['reference_'+name]['expected_CE_binary64']})
    return {'case': case, 'rows': results}


def run():
    direct.baseline.read(ROOT/direct.CONTROLS)
    controls = json.loads((ROOT/direct.CONTROLS).read_text())
    first = json.loads((ROOT/direct.FIRST_ATTEMPT).read_text())
    second_path = ROOT/'evidence/minimal/FP_DIRECT_PARTITION_MODEL_A2.json'
    second = json.loads(second_path.read_text())
    direct.completed_first_attempt()
    direct.read(second_path)
    assert second['registration']['prior_completed_attempt'] == json.loads(json.dumps(direct.completed_first_attempt()))
    model_rows = controls['workers']+first['workers']+second['workers']
    cases = []
    for case in direct.band.CASES:
        selected = [row for row in model_rows if tuple(row['case']) == case]
        assert len(selected) == 4 and len({row['mode'] for row in selected}) == 4
        assert all(row['result']['result']['status'] == 'COMPLETE_MODEL' for row in selected)
        cases.append(audit_case(case, {row['mode']: row['result']['result'] for row in selected}))
    assert 'torch' not in sys.modules
    return {'status': 'PASS_RETAINED_POSTERIOR_AMP_RISK_ENCLOSURES',
        'scope': 'exact per-query errors and rational KL/Brier enclosures on exposed completed evaluation paths; no population or completion-selected risk estimate; no new GPU execution',
        'arithmetic': 'Fraction; 96-bit outward grids; Decimal only for separate interval checks',
        'interval_checks': interval_checks(), 'proper_probability_interval': ['1/10', '9/10'],
        'sources': {'controls': controls['execution_source'], 'direct_seed0': first['execution_source'],
                    'direct_seed1': second['execution_source']},
        'cases': cases}


if __name__ == '__main__':
    report = run()
    output = ROOT/'evidence/minimal/FP_RETAINED_PARTITION_RISK.json'
    if output.exists():
        assert json.loads(output.read_text()) == json.loads(json.dumps(report))
    else:
        output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
