"""Exact full-native precision witness and fixed-word A2 preflight, no CUDA.

The word and graph are the previously registered mixed profile/install case.
This checks the full rounded schedule, not just its selected commit weights.
"""
from dataclasses import replace
from fractions import Fraction as F
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts'), str(Path(__file__).parent)]
from fp_reference import learner
from fp_reference.semantics import evaluate
from audit_cuda_learner import model_initial, model_predict, model_observe, HALF, SINGLE
from audit_likelihood_encoding import rounded_rational_commit
import rational_likelihood_lowering as gate

OUTPUT = ROOT/'evidence/minimal/FP_RATIONAL_NATIVE_PRECISION.json'


def run():
    original = gate.setup('mixed-profile-install')
    revised = gate.setup('mixed-profile-install-a2')
    cfg, graph, online, tape, bank, cuda, host = original
    assert original[:5] == revised[:5] and host == revised[-1]
    assert replace(cuda, state_atol=F(1, 50)) == revised[-2]
    spec = online.learner
    ref = learner.initial_state(graph, cfg.semantics, cfg.initializer_pattern, 0,
                                spec=spec, bit_limit=cfg.reference_integer_bits)
    physical = model_initial(graph, cfg.semantics, cfg.initializer_pattern)
    joint = bank.prior
    word = list(tape[:2])*2+list(tape[2:])
    maxima, failures, witness = {}, [], None

    def record(metric, error, step):
        assert error >= 0
        if error > maxima.get(metric, (F(-1), -1))[0]:
            maxima[metric] = error, step

    for step, (query, target) in enumerate(word):
        if step == 4:
            # Profile time and ordinary time are different coordinates.
            ref = replace(ref, cursor=2)
            physical = replace(physical, cursor=2)
        sources = dict(zip((s.source_id for s in cfg.semantics.sources), cfg.source_domain[query]))
        exact = evaluate(graph, cfg.semantics, ref.theta, sources, ref.delayed,
                         bit_limit=cfg.reference_integer_bits)
        rounded = model_predict(graph, cfg.semantics, physical, sources)
        stored_sum = sum(rounded['masses'])
        errors = {
            'native_error': max(abs(a-b) for key in ('values', 'excesses', 'masses')
                                for a, b in zip(getattr(exact, key), rounded[key])),
            'normalizer_error': max(abs(a-b) for a, b in
                ((exact.normalizer, rounded['normalizer']), (exact.normalizer, stored_sum),
                 (stored_sum, rounded['normalizer']))),
            'probability_error': max(abs(p-q) for p, mass, raw in
                zip(exact.probabilities, rounded['masses'], rounded['probabilities'])
                for q in (mass/stored_sum, raw)),
            'division_error': max(abs(m/stored_sum-p) for m, p in
                                  zip(rounded['masses'], rounded['probabilities']))}
        master_error = max(abs(a-b) for a, b in zip(ref.theta, physical.theta))
        record('master_error', master_error, step)
        rejected = tuple(k for k, v in errors.items() if v >
                         (cuda.probability_atol if k in ('probability_error', 'division_error') else cuda.state_atol))
        if rejected:
            assert step >= 4
            failures.append({'candidate_step': step, 'ordinary_cursor': step-2, 'metrics': rejected})
            if witness is None:
                assert step == 29 and ref.cursor == 27 and ref.optimizer_steps == 29
                direct = tuple(F(a**29) for a in (18, 2, 15, 5))
                assert ref.theta[1:] == tuple(w/sum(direct) for w in direct)
                assert master_error < F(1, 10**7)
                halves = tuple(HALF.decode(HALF.rounded(v)) for v in physical.theta[1:])
                assert halves == (F(1019, 1024), F(0), F(1319, 262144), F(0))
                assert rounded['masses'] == (F(18), F(129, 64))
                assert exact.normalizer == 20 and rounded['normalizer'] == F(1281, 64)
                assert errors['normalizer_error'] == F(1, 64) > cuda.state_atol
                witness = {
                    'candidate_step': step, 'ordinary_cursor': ref.cursor,
                    'joint_integer_formula': '(18^29,2^29,15^29,5^29)',
                    'master_words': tuple(SINGLE.encode_exact(v) for v in physical.theta),
                    'half_selected': tuple(map(str, halves)),
                    'half_selected_sum': str(sum(halves)),
                    'unrounded_mass_sum_after_half_cast': str(2+18*sum(halves)),
                    'reference_masses': tuple(map(str, exact.masses)),
                    'rounded_masses': tuple(map(str, rounded['masses'])),
                    'reference_normalizer': str(exact.normalizer),
                    'rounded_normalizer': str(rounded['normalizer']),
                    'master_error': str(master_error),
                    'errors': {key: str(value) for key, value in errors.items()}}
        for key, value in errors.items():
            record(key, value, step)
            assert value <= (revised[-2].probability_atol if key in
                             ('probability_error', 'division_error') else revised[-2].state_atol)
        observed = learner.observe_event(graph, ref, spec, exact, target,
                                         bit_limit=cfg.reference_integer_bits)
        physical = model_observe(graph, physical, rounded, target)
        gradient_error = max(abs(a-b) for a, b in zip(observed.gradient_sum, physical.gradient))
        record('gradient_error', gradient_error, step)
        assert gradient_error < cuda.state_atol
        assert (observed.unit_count, observed.cursor, observed.optimizer_steps) == (
            physical.unit, physical.cursor, physical.steps)
        ref = learner.commit_event(observed, spec, bit_limit=cfg.reference_integer_bits)
        joint = tuple(a*b for a, b in zip(joint, bank.factors[query*2+target]))
        assert ref.theta[1:] == tuple(w/sum(joint) for w in joint)
        physical, _, cells = rounded_rational_commit(physical, spec, joint)
        assert cells == 1+3*bank.worlds+2*graph.slot_count
        assert physical.unit == ref.unit_count == 0
        assert physical.gradient == ref.gradient_sum == (F(0),)*graph.slot_count
        assert (physical.cursor, physical.steps) == (ref.cursor, ref.optimizer_steps)
        master_error = max(abs(a-b) for a, b in zip(ref.theta, physical.theta))
        record('master_error', master_error, step+1)
        assert master_error < F(1, 10**6)
    assert [row['ordinary_cursor'] for row in failures] == [27, 34, 40, 41, 42, 43, 46]
    assert physical.cursor == 48 and physical.steps == 50
    assert 'torch' not in sys.modules and witness is not None
    return {'status': 'PASS', 'precision': 'exact rational native and RNE16/RNE32 interpreter; no Torch/CUDA',
            'candidate_complete_native_triples': len(word), 'profile_triples': 4,
            'final_ordinary_cursor': physical.cursor, 'final_optimizer_steps': physical.steps,
            'A1_state_atol': str(cuda.state_atol), 'A2_state_atol': str(revised[-2].state_atol),
            'unchanged_probability_atol': str(cuda.probability_atol),
            'maxima': {key: {'exact': str(value), 'candidate_step': step}
                       for key, (value, step) in maxima.items()},
            'A1_prediction_violations': failures, 'first_witness': witness,
            'scope': 'Fixed previously registered candidate word, including profiles. Subsequent cuts are passive continuations beyond the A1 refusal; no owned execution, fresh evidence, installation or all-history native bound is inferred.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    report = run()
    encoded = json.dumps(report, indent=2)+'\n'
    if args.write:
        OUTPUT.write_text(encoded, encoding='utf-8')
    print(encoded)
