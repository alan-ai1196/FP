"""Audit sound float64 token enclosures and exact native grid decisions."""
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json
import math
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'experiments/next_token'), str(ROOT/'scripts')]
from fp_reference.program import Sum, Term, Product
from causal_tokens import TokenSources
from audit_native_tokens import fixture, complete
import native_tokens as tokens
import native_readout as readout
import enclosed_tokens as bounded

OUTPUT = ROOT/'evidence/minimal/FP_ENCLOSED_TOKENS.json'


def refuses(operation):
    try:
        operation()
    except ValueError:
        return
    raise AssertionError('expected refusal')


def scalar():
    values = (F(-2), F(-3, 2), F(-1, 3), F(-1, 2**1075), F(0), F(1, 2**1075),
              F(1, 2**1074), F(1, 2**1022), F(1, 2**60), F(1, 3), F(1), F(7, 3), F(2**53+1), F(2**1023))
    checks = refusals = 0
    for a, b in product(values, repeat=2):
        x, y = bounded.Interval.exact(a), bounded.Interval.exact(b)
        assert x.contains(a) and y.contains(b)
        for operation, exact in ((lambda: x+y, a+b), (lambda: x-y, a-b), (lambda: x*y, a*b)):
            try:
                assert operation().contains(exact)
                checks += 1
            except bounded.EnclosureUnresolved:
                refusals += 1
        if b:
            try:
                assert (x/y).contains(a/b)
                checks += 1
            except bounded.EnclosureUnresolved:
                refusals += 1
    boxes = ((F(-3, 7), F(-1, 3)), (F(-2), F(3)), (F(0), F(5, 8)), (F(1, 7), F(9, 7)))
    wide_checks = 0
    for (a, b), (c, d) in product(boxes, repeat=2):
        x = bounded.Interval(bounded.Interval.exact(a).lower, bounded.Interval.exact(b).upper)
        y = bounded.Interval(bounded.Interval.exact(c).lower, bounded.Interval.exact(d).upper)
        for u, v in product((a, (a+b)/2, b), (c, (c+d)/2, d)):
            assert (x+y).contains(u+v) and (x-y).contains(u-v) and (x*y).contains(u*v)
            wide_checks += 3
            if c*d > 0:
                assert (x/y).contains(u/v)
                wide_checks += 1
    refuses(lambda: bounded.Interval(float('nan'), 0.0))
    refuses(lambda: bounded.Interval(1.0, 0.0))
    refuses(lambda: bounded.Interval.exact(F(2**1024)))
    refuses(lambda: bounded.Interval.exact(0.1))
    refuses(lambda: bounded.Interval(-1.0, 1.0).reciprocal())
    return dict(exact_ingress_values=len(values), point_operation_enclosures=checks,
        honest_point_operation_refusals=refusals, nonpoint_interior_and_endpoint_checks=wide_checks,
        strict_ingress_nonfinite_order_and_zero_denominator_refusals=5)


def compare_pending(pending, exact):
    assert pending.cursor == exact.cursor and pending.past == exact.past
    assert len(pending.targets) == exact.output.unit_count
    a, b = dict(pending.embedding_gradient), dict(exact.embedding_gradient)
    assert a.keys() == b.keys()
    assert all(a[k].contains(b[k]) for k in a)
    assert all(x.contains(y) for x, y in zip(pending.core_gradient, exact.core_gradient))
    assert all(x.contains(y) for x, y in zip(pending.common, exact.output.common))
    a, b = dict(pending.corrections), dict(exact.output.corrections)
    assert a.keys() == b.keys()
    assert all(x.contains(y) for k in a for x, y in zip(a[k], b[k]))


def histories():
    rows = []
    for unit, kind in product((1, 2), ('mixed', 'zero-embedding', 'zero-core')):
        d, origin = fixture(unit, kind)
        observations = commits = unresolved = completed = checked_gradients = 0
        reasons = {}
        for word in product(range(2), repeat=6):
            exact, pending = origin, bounded.begin(origin)
            for target in word:
                prediction, reference = pending.predict(), exact.predict()
                assert all(a.contains(b) for a, b in zip(prediction.values, reference.values))
                assert prediction.normalizer.contains(reference.output.normalizer)
                assert all(prediction.mass(y).contains(reference.output.mass(y)) for y in range(2))
                pending = pending.observe(prediction, target)
                exact = exact.observe(reference, target)
                compare_pending(pending, exact)
                assert all(pending.gradient(i).contains(exact.gradient(i)) for i in range(d.slot_count))
                checked_gradients += d.slot_count
                observations += 1
                if len(pending.targets) == unit:
                    try:
                        following = pending.commit()
                    except bounded.EnclosureUnresolved as error:
                        unresolved += 1
                        reasons[str(error)] = reasons.get(str(error), 0)+1
                        decoded = pending.exact_decoder()
                        assert complete(decoded) == complete(exact)
                        assert tuple(decoded.gradient(i) for i in range(d.slot_count)) == tuple(exact.gradient(i) for i in range(d.slot_count))
                        assert decoded.past == exact.past and pending.targets[-1] == target
                        break  # No exact-oracle fallback resumes this word.
                    exact = exact.commit()
                    assert complete(following) == complete(exact) and following.past == exact.past
                    assert following.output.optimizer_steps == exact.output.optimizer_steps
                    assert following.cursor == exact.cursor
                    assert all(following.gradient(i) == 0 for i in range(d.slot_count))
                    pending = bounded.begin(following)
                    commits += 1
            else:
                completed += 1
        rows.append(dict(update_unit=unit, initializer=kind, requested_words=64, completed_words=completed,
            observations=observations, full_pending_gradient_checks=checked_gradients,
            resolved_exact_commits=commits, terminal_unresolved_words=unresolved, unresolved_reasons=reasons,
            oracle_resumptions=0))
        print(f'PASS enclosed histories unit={unit} initializer={kind}', flush=True)
    return rows


def boundary_witnesses():
    gradient = F(1, 2**60)
    assert math.floor(1.0-float(gradient)) == 1
    assert (F(1)-gradient).numerator//(F(1)-gradient).denominator == 0
    enclosure = bounded.ONE-bounded.Interval.exact(gradient)
    refuses(lambda: bounded.project_grid(enclosure, 'rounding witness'))

    d = tokens.Definition(TokenSources(2, 1), 1, (), 0, (0,),
        readout.Spec((F(1, 2),)*2, 1, 8, F(1, 8), 1))
    origin = tokens.initialize(d, (128,), (), (64,))
    state = bounded.begin(origin)
    cache = state.predict()
    pending = state.observe(cache, 0)
    exact = pending.exact_decoder()
    assert exact.gradient(2) == 0 and pending.gradient(2).contains(0)
    refuses(lambda: pending.commit())
    assert pending.targets == (0,) and pending.origin is origin and origin.cursor == 0
    assert pending.exact_decoder() == exact
    refuses(lambda: pending.observe(cache, 1))
    refuses(lambda: state.observe(replace(cache, normalizer=bounded.Interval.exact(99)), 0))
    refuses(lambda: state.commit())
    refuses(lambda: bounded.begin(exact))
    # Prediction fits, but a newly revealed rare target needs a reciprocal
    # beyond binary64. Retain that target and an exact decoder, not stale
    # pre-observation gradient bounds.
    rare = tokens.Definition(TokenSources(2, 1), 1, (), 0, (0,),
        readout.Spec((F(1, 2**1024), F(1)), 1, 0, F(1, 2**1024), 1))
    rare_origin = tokens.initialize(rare, (1,), (), (1,), output_overrides=((0, 0, 0),))
    rare_state = bounded.begin(rare_origin)
    prediction = rare_state.predict()
    try:
        rare_state.observe(prediction, 0)
    except bounded.EnclosureUnresolved as error:
        retained = error.retained_unit
        assert type(retained) is bounded.RetainedUnit and retained.origin is rare_origin
        assert retained.targets == (0,) and retained.past == (0,)
        decoded = retained.exact_decoder()
        native = rare_origin.observe(rare_origin.predict(), 0)
        assert complete(decoded) == complete(native)
        assert tuple(decoded.gradient(i) for i in range(rare.slot_count)) == tuple(native.gradient(i) for i in range(rare.slot_count))
        assert decoded.cursor == 1 and rare_state.cursor == 0
    else:
        raise AssertionError('expected newly revealed target arithmetic refusal')
    return dict(naive_float64_grid_master=1, exact_grid_master=0, grid_cell_refusal=True,
        symmetric_exact_zero_gradient=str(exact.gradient(2)), nonzero_enclosure_width=pending.gradient(2).upper-pending.gradient(2).lower,
        unresolved_origin_target_context_and_complete_exact_decoder_retained=True,
        failed_observation_new_target_and_exact_unit_retained=True, no_stale_gradient_enclosure_published=True,
        stale_forged_and_clock_refusals=4)


def long_unit_fixture():
    V, L, D, N = 50257, 4, 2, 512
    nodes = (Sum('f', tuple(Term(2*i, i) for i in range(4))), Product('f', 8, 0), Product('f', 1, 7))
    d = tokens.Definition(TokenSources(V, L), D, nodes, 4, (0, 8, 9, 10),
        readout.Spec((F(1, V),)*V, 4, 16, F(1, 1024), N))
    word = tuple(1000+i for i in range(N))
    overrides = tuple((token, k, 1+((i+1)*(7919+2*k)) % 65521) for i, token in enumerate(word) for k in range(D))
    origin = tokens.initialize(d, (32768, 16384), (32768, 16384, 8192, 49152), (1, 0, 0, 0),
        embedding_overrides=overrides, output_overrides=((17, 0, 2),))
    return d, origin, word


def long_unit():
    d, origin, word = long_unit_fixture()
    V, L, N = d.output.labels, d.sources.context, d.output.update_unit
    pending, exact = bounded.begin(origin), origin
    checkpoints = []
    for count, target in enumerate(word, 1):
        prediction, reference = pending.predict(), exact.predict()
        assert all(a.contains(b) for a, b in zip(prediction.values, reference.values))
        assert prediction.normalizer.contains(reference.output.normalizer)
        assert prediction.mass(target).contains(reference.output.mass(target))
        pending, exact = pending.observe(prediction, target), exact.observe(reference, target)
        if count in (1, 8, 64, 128, 256, N):
            compare_pending(pending, exact)
            checkpoints.append(dict(events=count, maximum_common_gradient_denominator_bits=max(v.denominator.bit_length() for v in exact.output.common)))
            print(f'PASS long unit checkpoint {count}', flush=True)
    try:
        following = pending.commit()
    except bounded.EnclosureUnresolved as error:
        outcome = dict(status='UNRESOLVED', reason=str(error), endpoint_published=False)
        assert pending.targets == word and pending.origin is origin
    else:
        native = exact.commit()
        assert complete(following) == complete(native)
        assert following.past == native.past and following.cursor == native.cursor
        outcome = dict(status='EXACT_NATIVE_COMMIT', complete_parameter_checks=d.slot_count)
    return dict(vocabulary=V, context=L, events=N, native_parameter_slots=d.slot_count,
        exact_gradient_basis_checkpoint_comparisons=len(checkpoints), checkpoints=checkpoints, outcome=outcome,
        scope='synthetic-token numerical audit with separate unbounded exact control; no model score, owned work/bit cap, timing or AMP claim')


def main():
    result = dict(status='PASS_SOUND_NATIVE_TOKEN_ENCLOSURES', scope='conditional binary64 enclosures, complete retained exact unit and exact grid decisions; passive only')
    for name, function in dict(scalars=scalar, native_histories=histories, boundary_witnesses=boundary_witnesses, long_unit=long_unit).items():
        result[name] = function()
        print('PASS '+name, flush=True)
    assert 'torch' not in sys.modules
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = main()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
