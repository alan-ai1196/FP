"""Proper-score transfer, ideal-law band risk, and owned selection witness.

This is CPU evidence: exact fractions, 70-digit Decimal checks and the
registered RNE simulator. It does not execute CUDA or score model prefixes.
"""
from dataclasses import replace
from decimal import Decimal as D, localcontext
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts'),
               str(ROOT/'experiments/joint_uncertainty')]
from fp_reference import ReferenceCompilerRuntime, CompilerPolicy
from fp_reference import indexed_amp as amp, packed_histogram_amp as physical
from fp_reference import packed_histogram_decoder as hist
from fp_reference.float64_bridge import Float64Contract
from fp_reference.indexed_count import CountState
from audit_indexed_source_binding import predict
from audit_reference_construction import validate_residency
import audit_indexed_runtime as reference

ARTIFACT = ROOT/'evidence/minimal/FP_PREDICTABLE_SCORE_TRANSFER.json'
PREFIX = ((0, 1, 0), (0, 2, 0), (0, 2, 0), (1, 2, 1), (1, 2, 1))
WORDS = (1069162261, 1087469627, 1075646346, 1089566779,
         1092616192, 1048267792, 1061235964)


def decimal(value):
    value = F(value)
    return D(value.numerator)/D(value.denominator)


def entropy(p):
    x = decimal(p)
    return -x*x.ln()-(1-x)*(1-x).ln()


def log_gap(r, p, q):
    return decimal(r)*(decimal(p)/decimal(q)).ln() + (
        1-decimal(r))*(decimal(1-p)/decimal(1-q)).ln()


def grid():
    a, delta = F(1, 10), F(1, 1000)
    sharp = log_gap(a, a, a-delta)
    simple = delta**2/(2*(a-delta)*(1-a+delta))
    assert simple == F(1, 178398) and 0 < sharp <= decimal(simple)
    checked = 0
    for p in (F(k, 10) for k in range(1, 10)):
        for j in range(-10, 11):
            q = p+F(j, 10000)
            regret = log_gap(p, p, q)
            assert D('-1e-65') <= regret <= sharp+D('1e-65')
            brier = p*(2*(q-1)**2-2*(p-1)**2)+(1-p)*(2*q*q-2*p*p)
            assert brier == 2*(q-p)**2 <= 2*delta**2
            checked += 1
    assert checked == 189
    return {'probability_grid_checks': checked, 'delta': str(delta),
        'noise_floor': str(a), 'sharp_log_regret': str(sharp),
        'simple_log_regret_upper': str(simple),
        'binary_Brier_regret_upper': str(2*delta**2)}


def likelihood(label, bit):
    return F(9, 10) if label == bit else F(1, 10)


def local_risk():
    total = informative = F(0)
    first = second = D(0)
    patterns = branches = 0
    for labels in product((0, 1), repeat=4):
        weights = {}
        for b0, b1 in product((0, 1), repeat=2):
            w = F(1, 4)
            for y, bit in zip(labels, (b0, b0, b1, b1)):
                w *= likelihood(y, bit)
            weights[b0 ^ b1] = weights.get(b0 ^ b1, F(0))+w
        prob = sum(weights.values())
        p = sum(w*likelihood(1, bit) for bit, w in weights.items())/prob
        total += prob
        first += decimal(prob)*entropy(p)
        if labels[0] == labels[1] and labels[2] == labels[3]:
            informative += prob
            assert abs(2*p-1) == F(4, 5)*F(40, 41)**2
        else:
            assert p == F(1, 2)
        for target in (0, 1):
            following = {bit: w*likelihood(target, bit) for bit, w in weights.items()}
            mass = sum(following.values())
            next_p = sum(w*likelihood(1, bit) for bit, w in following.items())/mass
            assert next_p == (F(9, 100)/(1-p) if target == 0 else 1-F(9, 100)/p)
            second += decimal(mass)*entropy(next_p)
            branches += 1
        patterns += 1
    assert total == 1 and informative == F(1681, 2500)
    u, a = informative, F(2961, 3362)
    first_formula = decimal(u)*entropy(a)+decimal(1-u)*D(2).ln()
    second_formula = decimal(u)*(decimal(a)*entropy(F(9, 100)/a)
        +decimal(1-a)*entropy(F(9, 100)/(1-a)))+decimal(1-u)*entropy(F(9, 50))
    assert abs(first-first_formula) < D('1e-60')
    assert abs(second-second_formula) < D('1e-60')
    joint = (first_formula+second_formula)/2
    pair = (D(2).ln()+entropy(F(9, 50)))/2
    assert joint < pair
    return {'local_training_patterns': patterns, 'next_label_branches': branches,
        'exact_informative_probability': str(informative),
        'local_first_query_risk': str(first_formula),
        'local_second_query_risk': str(second_formula),
        'band_joint_ideal_law_unseen_risk_upper': str(joint),
        'band_pair_ideal_law_unseen_risk': str(pair),
        'band_joint_advantage_lower': str(pair-joint)}


def selection():
    budget = hist.PackedHistogramAllowance(live_cells=64, arithmetic=512, span_cap=5)
    before = CountState(3, (1, 2, -2), None, 5, 5)
    plan = hist.passive_plan(before, (0, 1), budget)
    native = hist.reference(plan)
    arithmetic = amp._Arithmetic(32768)
    rounded, _ = physical._prediction_schedule(plan, amp.IndexedAmpState(before), arithmetic)
    relation = amp.check_prediction(native, rounded, Float64Contract(F(1, 100), F(1, 1000)),
        normalizer_cap=F(18), activation_cap=F(8), bit_limit=32768)
    masses = tuple(amp.single(word) for word in rounded.words[2:4])
    p, q = native.probabilities[1], masses[1]/sum(masses)
    assert p == F(15129, 20050) and q == F(3164991, 4194304)
    assert rounded.words == WORDS and 0 < q-p <= F(1, 1000)
    assert relation.probability_error <= F(1, 1000)
    # Separate literal generative weights, independent of the histogram.
    weights = []
    for tail in product((0, 1), repeat=2):
        bits, w = (0,)+tail, F(1, 4)
        for i, j, target in PREFIX:
            w *= likelihood(target, bits[i] ^ bits[j])
        weights.append((w, likelihood(1, bits[0] ^ bits[1])))
    total = sum(w for w, _ in weights)
    assert sum(w*r for w, r in weights)/total == p
    r = sum(w*s*s for w, s in weights)/(total*p)
    assert r == F(2961, 3362)
    rows = []
    for target, suffix in ((0, None), (1, 0), (1, 1)):
        cfg, schema, online = reference.fixture(3, 7)
        rt = ReferenceCompilerRuntime(replace(cfg, indexed_histogram=budget), schema,
            online=online, policy=CompilerPolicy(()))
        models = {rt.snapshot().deployed_id: reference.literal(3)}
        for event in PREFIX:
            reference.step(rt, schema, event, models)
        assert rt.snapshot().candidates[0].learner.encoded == before
        reference.step(rt, schema, (0, 1, target), models)
        cut = validate_residency(rt)
        assert cut.event_traces[-1].prediction.probabilities[1] == p
        span = sum(map(abs, cut.candidates[0].learner.encoded.counts))
        assert span == (6 if target == 0 else 4)
        if suffix is None:
            outcome = predict(rt, schema, (0, 1))
            assert outcome.status == 'UNRESOLVED'
            after = validate_residency(rt)
            assert after.cursor == 6 and after.pending.record.target is None
            assert after.candidates == cut.candidates and after.observations == cut.observations
            assert after.run.status == 'HALTED_UNRESOLVED'
            next_prediction = outcome.status
        else:
            reference.step(rt, schema, (0, 1, suffix), models)
            after = validate_residency(rt)
            assert after.cursor == 7 and after.run.status == 'SEALED_REFERENCE_STREAM'
            assert not after.run.closure.decisions
            next_prediction = 'PREDICTED_REFERENCE'  # Asserted inside the real step.
        rows.append({'scored_target': target, 'suffix_target': suffix,
            'next_prediction': next_prediction, 'status': after.run.status,
            'cursor': after.cursor, 'after_scored_span': span})
    unconditional = log_gap(p, p, q)
    observed = log_gap(F(1), p, q)
    teacher = log_gap(r, p, q)
    correction = decimal(r-p)*(decimal(p*(1-q)/(q*(1-p)))).ln()
    assert abs(teacher-(unconditional+correction)) < D('1e-60')
    prior_brier = 2*(q-p)**2
    selected_brier = prior_brier+4*(q-p)*(p-r)
    assert unconditional > 0 > observed and teacher < 0 and selected_brier < 0
    return {'prefix': PREFIX, 'before_counts': before.counts, 'query': (0, 1),
        'span_cap': budget.span_cap, 'native_p1': str(p), 'proper_RNE_p1': str(q),
        'forecast_words': rounded.words, 'delta': str(q-p),
        'completion_condition': 'scored target is1, regardless of suffix target',
        'conditional_hidden_noise_p1': str(r),
        'prior_expected_log_regret': str(unconditional),
        'selected_realized_target_log_gap': str(observed),
        'selected_hidden_noise_log_gap': str(teacher),
        'prior_expected_Brier_regret': str(prior_brier),
        'selected_hidden_noise_Brier_gap': str(selected_brier),
        'owned_reference_branches': rows}


def compare(actual, retained, key=''):
    if isinstance(actual, dict):
        assert actual.keys() == retained.keys(), key
        for field in actual:
            if field != 'source':
                compare(actual[field], retained[field], field)
    elif isinstance(actual, list):
        assert len(actual) == len(retained), key
        for a, b in zip(actual, retained):
            compare(a, b, key)
    elif isinstance(actual, str) and any(c in actual for c in '.Ee'):
        try:
            assert abs(D(actual)-D(retained)) < D('1e-60'), key
        except ArithmeticError:
            assert actual == retained, key
    else:
        assert actual == retained, (key, actual, retained)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, help='write a new artifact; never overwrite')
    args = parser.parse_args()
    with localcontext() as context:
        context.prec = 70
        result = {'status': 'PASS_PREDICTABLE_SCORE_TRANSFER_CPU',
            'source': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'scope': 'exact rational identities, 70-digit Decimal checks, real owned Reference continuation and passive registered RNE; no actual CUDA or population measurement',
            **grid(), **local_risk(), 'selection_witness': selection()}
        result = json.loads(json.dumps(result))
        if args.output:
            with args.output.open('x', encoding='utf-8') as stream:
                json.dump(result, stream, indent=2)
                stream.write('\n')
        else:
            compare(result, json.loads(ARTIFACT.read_text(encoding='utf-8')))
        print(json.dumps({'status': result['status'],
            'retained_artifact_checked': not bool(args.output),
            'probability_grid_checks': result['probability_grid_checks'],
            'local_training_patterns': result['local_training_patterns'],
            'owned_reference_branches': len(result['selection_witness']['owned_reference_branches'])}))


if __name__ == '__main__':
    main()
