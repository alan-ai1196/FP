"""Exact box law and owned pre-context gain-bound refinement audits."""
from dataclasses import asdict, replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import os
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts')]
from fp_reference.persistence_bounds import paired_mass_ratio_bound, probability_box
from fp_reference.semantics import ArithmeticUnresolved
from audit_reference_construction import rejects

OUTPUT = ROOT/'evidence/minimal/FP_PERSISTENCE_MASS_BOUNDS.json'


def exact_boxes():
    pairs = vertices = endpoints = 0
    for labels, coordinates in ((2, tuple((F(a), F(a+d)) for a in (1, 2) for d in (0, 1, 2))),
                                 (3, tuple((F(1), F(a)) for a in (1, 2, 3)))):
        boxes = tuple(product(coordinates, repeat=labels))
        distributions = {}
        for box in boxes:
            # Independent oracle: enumerate mass corners and normalize the
            # entire vector, rather than reimplementing the endpoint formula.
            values = tuple(tuple(v/sum(row) for v in row) for row in product(*box))
            distributions[box] = values
            bounds = probability_box(box, bit_limit=4096)
            for label, (lower, upper) in enumerate(bounds):
                assert lower == min(row[label] for row in values)
                assert upper == max(row[label] for row in values)
                endpoints += 2
        for base, candidate in product(boxes, repeat=2):
            ratio = paired_mass_ratio_bound((base,), (candidate,), bit_limit=4096)
            maximum = F(1)
            for left, right in product(distributions[base], distributions[candidate]):
                for p, q in zip(left, right):
                    maximum = max(maximum, p/q, q/p)
                    vertices += 1
            assert ratio == maximum
            pairs += 1
    uniform = (((F(1), F(1)), (F(1), F(1))),)
    candidate = (((F(1), F(9)), (F(1), F(9))),)
    assert paired_mass_ratio_bound(uniform, candidate, bit_limit=4096) == 5
    bad = ((), ((F(0), F(1)),), ((F(2), F(1)),), ((1, F(1)),))
    for values in bad:
        rejects(lambda values=values: probability_box(values, bit_limit=4096))
    rejects(lambda: paired_mass_ratio_bound(uniform, candidate*2, bit_limit=4096))
    rejects(lambda: paired_mass_ratio_bound(uniform, (((F(1), F(1)),),), bit_limit=4096))
    rejects(lambda: paired_mass_ratio_bound((1,), (1,), bit_limit=4096))
    rejects(lambda: probability_box(((F(1 << 100), F(1 << 100)),), bit_limit=64), ArithmeticUnresolved)
    return {'box_pairs': pairs, 'normalized_corner_ratio_checks': vertices,
            'sharp_probability_endpoints': endpoints, 'malformed_or_budget_refusals': 8,
            'uniform_vs_mass_1_to_9_ratio_bound': '5'}


def refresh_refusal():
    from fp_reference import ReferenceCompilerRuntime
    from fp_reference.data_usage import StochasticStreamLaw
    from fp_reference.persistence import PersistenceContract
    from fp_reference.program import Program, Source, Sum, Term
    from audit_reference_construction import contract, zero_program
    from audit_reference_events import online
    from audit_reference_persistence import rule, identity, event, owned
    cfg = contract(cap=16, peak=16, pattern=(F(0),))
    graph = Program((Source('x0_0'), Sum('mass', (Term(0, 0),)), Sum('mass', ())), 1, (1, 2))
    registration = PersistenceContract(F(3, 4), (rule(horizon=4, bound=F(1, 4)),))
    run = online(cfg, 4, unit=1, rate=F(8), grid=None)
    run = replace(run, persistence=registration, data=replace(run.data,
        stream_law=StochasticStreamLaw('external branch-invariant audit producer assumption')))
    runtime = ReferenceCompilerRuntime(cfg, zero_program(2), online=run)
    candidate = runtime.construct_candidate(graph).candidate_id
    admitted = runtime.admit_reference_persistence(candidate, 'future')
    initial = identity(runtime, admitted.identity_id)
    assert initial.status == 'ACTIVE' and initial.ratio_bound == 1
    assert initial.ratio_bound_kind == 'current-native-mass-box'
    event(runtime, 0)
    failed = identity(runtime, admitted.identity_id)
    assert failed.status == 'UNRESOLVED' and 'current whole-domain mass boxes' in failed.reason
    snapshot = owned(runtime)
    actual = next(c for c in snapshot.candidates if c.candidate_id == candidate)
    assert actual.theta == (F(4),) and actual.range_safe and snapshot.cursor == 1
    assert len(snapshot.persistence_events) == 1 and snapshot.persistence_events[0].wealth_after == 1
    assert snapshot.alpha_spent == F(1, 4)
    event(runtime, 1)
    assert identity(runtime, admitted.identity_id) == failed and runtime.snapshot().cursor == 2
    return {'initial_ratio': '1', 'updated_candidate_theta': '4',
            'updated_native_range_still_safe': True, 'refinement_stops_before_next_context': True,
            'current_zero_gain_retained_and_spent_alpha_not_refunded': True,
            'no_revival_on_another_ordinary_event': True}


def domain_and_work_refusals():
    from fp_reference.persistence import PersistenceContract
    from fp_reference.program import Program, Source, Sum, Term
    import fp_reference.runtime as execution
    from audit_reference_construction import contract, limits
    from audit_reference_persistence import fixture, rule, identity, event, owned
    graph = Program((Source('x0_0'), Sum('mass', (Term(0, 0),)), Sum('mass', ())), 1, (1, 2))
    cfg = contract(cap=16, peak=16, pattern=(F(8),))
    registration = PersistenceContract(F(3, 4), (rule(horizon=4, bound=F(3, 4)),))
    runtime, candidate = fixture(cfg=cfg, count=4, graph=graph, registration=registration)
    result = runtime.admit_reference_persistence(candidate, 'future')
    assert result.status == 'UNRESOLVED' and 'current whole-domain mass boxes' in result.reason
    failed = identity(runtime, result.identity_id)
    harmless = next(row for row in cfg.source_domain if row[0] == 0)
    event(runtime, 0, harmless)
    assert identity(runtime, result.identity_id) == failed and not runtime.snapshot().persistence_events
    owned(runtime)

    # Measure only the work consumed before entering refinement. A second
    # root's immutable cap ends there, so the new arithmetic must not execute.
    cfg = contract(cap=16, peak=1)
    registration = PersistenceContract(F(3, 4), (rule(horizon=4, bound=F(1, 2)),))
    entered = []
    original = execution.ReferenceCompilerRuntime._persistence_mass_ratio

    def capture(root, *args):
        entered.append(root._ledger.snapshot()['spent']['compiler']['work'])
        return original(root, *args)

    runtime, candidate = fixture(cfg=cfg, count=4, registration=registration)
    with patch.object(execution.ReferenceCompilerRuntime, '_persistence_mass_ratio', capture):
        good = runtime.admit_reference_persistence(candidate, 'future')
    assert identity(runtime, good.identity_id).status == 'ACTIVE' and len(entered) == 1
    limited = replace(cfg, limits=limits(work_cap=entered[0]))
    runtime, candidate = fixture(cfg=limited, count=4, registration=registration)
    with patch.object(execution, 'paired_mass_ratio_bound', side_effect=AssertionError('unpaid mass arithmetic')):
        bad = runtime.admit_reference_persistence(candidate, 'future')
    assert bad.status == 'UNRESOLVED' and 'ResourceExceeded' in bad.reason
    assert runtime.snapshot().alpha_spent == F(1, 4)
    owned(runtime)
    return {'unseen_bad_context_prevents_tight_admission': True,
            'later_harmless_context_does_not_revive_failed_identity': True,
            'refinement_work_paid_before_arithmetic': True,
            'failed_refinement_admission_keeps_spent_alpha': True,
            'work_refusal_cap': entered[0]}


def owned_model(path):
    import audit_simplex_learner as fixture
    import audit_paired_cpu_persistence as rules
    from fp_reference.runtime import ReferenceCompilerRuntime
    original_rule, original_bound = rules.registration, ReferenceCompilerRuntime._persistence_mass_ratio
    calls = []

    def registration(**kwargs):
        assert kwargs['bound'] == 6
        return original_rule(**{**kwargs, 'bound': F(13, 8)})

    def checked(runtime, identity, base, candidate):
        if identity.status == 'INITIALIZING':
            assert identity.cursor == runtime._cursor and runtime._pending is None
        else:
            assert identity.cursor == runtime._cursor+1 and runtime._pending is not None
            assert runtime._pending.record.target is not None
        bound = original_bound(runtime, identity, base, candidate)
        calls.append((identity.rule.score_path, bound))
        return bound

    with patch.object(rules, 'registration', registration), patch.object(
            ReferenceCompilerRuntime, '_persistence_mass_ratio', checked):
        result = fixture.owned(n=2, profiles=True, cuda=path == 'cuda', bounded=True)
    assert result['status'] == ('SEALED_CUDA_STREAM' if path == 'cuda' else 'SEALED_REFERENCE_STREAM')
    assert result['install_cursor'] is not None and calls
    scores = sorted({key for key, _ in calls})
    assert len(scores) == 2
    return {'status': 'OWNED_REFINED_GAIN_PROFILE_INSTALL_PASS', 'path': path,
        'registered_bound': '13/8', 'registered_bet_fraction': '3/4',
        'registered_gain_coefficient': '6/13',
        'bound_computations': {key: {'count': sum(k == key for k, _ in calls),
            'maximum_ratio': str(max(v for k, v in calls if k == key))} for key in scores},
        'pre_context_or_post_previous_target_cut_checked': True, 'complete_owned_result': result,
        'process_id': os.getpid()}


def bounded_models():
    from windows_job_audit_support import run_in_job
    jobs = []
    for path, cap in (('cpu', 512 << 20), ('cuda', 4 << 30)):
        with tempfile.TemporaryDirectory(prefix='mass-bound-', dir=ROOT/'runs') as directory:
            temporary = Path(directory)
            assert temporary.resolve().parent == (ROOT/'runs').resolve()
            output = temporary/'result.json'
            job = run_in_job(__file__, ('--worker', path, '--output', str(output)),
                             commit_limit=cap, timeout_ms=180000)
            result = json.loads(output.read_text(encoding='utf-8')) if output.exists() else None
        assert job.exit_code == 0 and not job.timed_out and not job.limit_terminated_processes
        assert job.attached_before_resume and job.peak_job_commit <= cap
        assert result is not None and result['process_id'] == job.process_id
        jobs.append({'path': path, 'completed_job': asdict(job), 'result': result})
    return jobs


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--worker', choices=('cpu', 'cuda'))
    parser.add_argument('--output', type=Path)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--exact-only', action='store_true')
    args = parser.parse_args()
    assert bool(args.worker) == bool(args.output)
    assert not args.worker or not (args.write or args.exact_only)
    if args.worker:
        result = owned_model(args.worker)
    else:
        result = {'status': 'DEVELOPMENT_MASS_BOUND_AUDIT_PASS', 'exact': exact_boxes(),
                  'current_state_refusal': refresh_refusal(),
                  'domain_and_work_refusals': domain_and_work_refusals()}
        if not args.exact_only:
            result['workers'] = bounded_models()
    text = json.dumps(result, indent=2)+'\n'
    if args.worker:
        args.output.write_text(text, encoding='utf-8')
    elif args.write:
        assert not args.exact_only
        OUTPUT.write_text(text, encoding='utf-8')
    print(text, end='')
