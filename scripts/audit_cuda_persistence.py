"""Owned actual CUDA range and fresh same-path evidence, with exact oracles.

Each device case starts in a fresh process/allocator. Test tapes instantiate
declared external stochastic laws; they do not establish a data source law.
No target installation, total-device bound or model-science result is claimed.
"""
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json
import subprocess
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts')]

from fp_reference import ReferenceCompilerRuntime
from fp_reference import cuda_learner as gpu
from fp_reference.cuda_range import check_forward, enclose_cuda, forward_operations
from fp_reference.cuda_prefix import raw_prediction, widened_prediction
from fp_reference.data_usage import StochasticStreamLaw
from fp_reference.float64_bridge import Float64Contract, check_prediction
from fp_reference.persistence import PersistenceContract, PersistenceRule, REFERENCE_PATH, CUDA_PATH
from fp_reference.program import Binding, DelayedStateSpec, Product, Program, Source, State, Sum, Term
from fp_reference.resources import ResourceExceeded
from fp_reference.semantics import ArithmeticUnresolved, evaluate
from audit_cuda_runtime import cuda_contract, configuration, audit_snapshot, raw_model, raw_model_prediction
from audit_cuda_learner import model_initial, model_predict, q, HALF, SINGLE
from audit_reference_construction import contract, domain, rejects, zero_program
from audit_reference_events import online, shared_graph
from audit_reference_persistence import SOURCE_PAIR, identity, event, owned, check_gain, wealth_oracle
from ingress_audit_support import deliver_context


def registration(*, bound=F(3, 4), horizon=8, epoch=1, alpha=F(1, 4)):
    return PersistenceContract(F(3, 4), tuple(
        PersistenceRule(key, epoch, horizon, alpha, F(3, 4), bound, 12, 16, path)
        for key, path in (('ref', REFERENCE_PATH), ('cuda', CUDA_PATH))))


def fixture(*, cfg=None, graph=SOURCE_PAIR, base=None, count=12, rules=None,
            rate=F(0), unit=2, grid=16, float64=False, law=True):
    cfg = replace(configuration(), normalizer_cap=F(3), activation_cap=F(1)) if cfg is None else cfg
    rules = registration() if rules is None else rules
    run = replace(online(cfg, count, unit=unit, rate=rate, grid=grid), persistence=rules,
                  float64=Float64Contract(F(1, 10**10), F(1, 10**10)) if float64 else None)
    if law:
        run = replace(run, data=replace(run.data, stream_law=StochasticStreamLaw('external branch-invariant CUDA audit producer assumption')))
    runtime = ReferenceCompilerRuntime(cfg, zero_program(2) if base is None else base, online=run, cuda=cuda_contract())
    built = runtime.construct_candidate(graph)
    assert built.status == 'BUILT_REFERENCE', built
    return runtime, built.candidate_id


def pair(runtime, candidate):
    r = runtime.admit_reference_persistence(candidate, 'ref')
    c = runtime.admit_cuda_persistence(candidate, 'cuda')
    assert r.identity_id and c.identity_id, (r, c)
    assert identity(runtime, r.identity_id).status == identity(runtime, c.identity_id).status == 'ACTIVE', (r, c)
    return r.identity_id, c.identity_id


def range_audit():
    cfg = replace(configuration(), normalizer_cap=F(10000), activation_cap=F(10000))
    rules = cfg.semantics
    graph = Program((Source('x0_0'), Source('x0_1'), Sum('mass', (Term(0, 0), Term(1, 1))),
                     Product('mass', 2, 2), Sum('mass', ())), 2, (3, 4))
    grid = (F(0), F(1, 8), F(1, 3), F(2, 3), F(1))
    scopes, cases = 0, 0
    def bound_for(graph, rules, state, **kw):
        return enclose_cuda(graph, rules, raw_model(state), normalizer_cap=kw.get('cap', F(10000)),
            activation_cap=kw.get('peak', F(10000)), source_point=kw.get('point'), bit_limit=32768)
    def compare(graph, rules, state, inputs, bound):
        prediction = model_predict(graph, rules, state, inputs)
        checked = check_forward(graph, rules, raw_model(state), inputs, raw_model_prediction(prediction), bit_limit=32768)
        assert checked == forward_operations(graph, rules)
        assert all(v <= b for v, b in zip(prediction['values'], bound.values_upper))
        assert all(lo <= v <= hi for lo, v, hi in zip(bound.base_lower, prediction['masses'], bound.masses_upper))
        assert sum(prediction['masses'], F(0)) <= bound.stored_mass_sum_upper
        assert prediction['normalizer'] <= bound.rounded_normalizer_upper
        assert all(0 < lo <= v <= 1 for lo, v in zip(bound.raw_probability_lower, prediction['probabilities']))
        return prediction
    for theta in product((F(0), F(1, 3), F(1), F(2)), repeat=2):
        state = model_initial(graph, rules, theta)
        bound = bound_for(graph, rules, state)
        for row in product(grid, repeat=2):
            compare(graph, rules, state, dict(zip(('x0_0', 'x0_1'), row)), bound)
            cases += 1
        scopes += 1
    rules = replace(rules, states=(DelayedStateSpec('h', 'mass', 2, F(1)),))
    graph = Program((Source('x0_0'), State('h'), Sum('mass', (Term(0, 0), Term(1, 0))),
                     Product('mass', 2, 2), Sum('mass', ())), 1, (3, 4), (Binding('h', 2),))
    state = model_initial(graph, rules, (F(1, 4),))
    bound = bound_for(graph, rules, state)
    recurrent = 0
    for source, head, tail in product(grid, repeat=3):
        current = replace(state, delayed=(('h', (q(head, HALF), q(tail, HALF))),))
        pred = compare(graph, rules, current, {'x0_0': source, 'x0_1': 1-source}, bound)
        assert all(v <= 1 for _, row in pred['delayed'] for v in row)
        recurrent += 1
    bad_tail = replace(state, delayed=(('h', (F(0), F(1025, 1024))),))
    rejects(lambda: bound_for(graph, rules, bad_tail), ArithmeticUnresolved)
    rules = cfg.semantics
    unsafe = replace(rules, sources=tuple(replace(s, upper=F(3, 10)) for s in rules.sources))
    state = model_initial(SOURCE_PAIR, unsafe, ())
    rejects(lambda: bound_for(SOURCE_PAIR, unsafe, state, peak=F(3, 10)), ArithmeticUnresolved)
    # Every slot is cast, even when the graph has no parameter edge.
    unused = replace(zero_program(2), slot_count=1)
    state = model_initial(unused, rules, (F(65520),))
    rejects(lambda: bound_for(unused, rules, state), ArithmeticUnresolved)
    # A real range-safe product may overflow after source rounding to 256.
    unsafe = replace(rules, sources=tuple(replace(s, upper=F(25599, 100)) for s in rules.sources))
    square = Program((Source('x0_0'), Product('mass', 0, 0)), 0, (1, 1))
    rejects(lambda: bound_for(square, unsafe, model_initial(square, unsafe, ()), cap=F(10**6), peak=F(10**6)), ArithmeticUnresolved)
    # Different failures of positivity, stored sum and rounded normalizer.
    for base, cap in (((F(1, 1 << 150), F(1)), F(2)),
                      ((F(1, 1 << 149), F(1 << 100)), F(1 << 101)),
                      ((F(1), F(1, 1 << 24)), F(1)),
                      ((F(1), F(3, 1 << 24)), F(1)+F(3, 1 << 24))):
        unsafe = replace(rules, base=base)
        rejects(lambda: bound_for(zero_program(2), unsafe, model_initial(zero_program(2), unsafe, ()), cap=cap), ArithmeticUnresolved)
    # Exact source -> single -> half must not collapse to a direct half cast.
    x = F(1, 2)+F(1, 1 << 12)+F(1, 1 << 26)
    assert q(q(x), HALF) == F(1, 2) and q(x, HALF) == F(1025, 2048)
    return {'independent_product_sum_boxes': scopes, 'independent_context_checks': cases,
            'complete_recurrent_queue_checks': recurrent,
            'full_tail_unused_slot_source_rounding_product_overflow_and_both_normalizers_rejected': True,
            'two_stage_source_witness': str(x)}


def scores_case():
    runtime, candidate = fixture(cfg=configuration(), graph=shared_graph(), count=12, float64=True,
        rules=registration(bound=F(6), horizon=4, epoch=3), rate=F(1, 8))
    rid, cid = pair(runtime, candidate)
    wealth, sums, counts = ({key: F(1) for key in (rid, cid)}, {key: F(0) for key in (rid, cid)}, {key: 0 for key in (rid, cid)})
    changed = differences = raw_differences = checked = 0
    for context, target in ((0, 0), (1, 1), (0, 1), (1, 0))*3:
        before = identity(runtime, cid)
        cursor = runtime.snapshot().cursor
        assert deliver_context(runtime, f'observation-{cursor}', domain(1)[context]).status == 'PREDICTED_REFERENCE'
        pending = runtime.snapshot()
        forecasts = {p.candidate_id: p for p in pending.cuda.phases if p.phase == 'ordinary:predict' and p.ordinary_cursor == cursor}
        rejects(lambda: runtime.admit_cuda_persistence(candidate, 'cuda'))
        rejects(lambda: runtime.cancel_cuda_persistence(cid))
        assert runtime.observe(target).status == 'OBSERVED_REFERENCE'
        rows = runtime.snapshot().persistence_events[-2:]
        for row in rows:
            for lineage, actual in ((row.base_lineage_id, row.base_probability), (row.candidate_lineage_id, row.candidate_probability)):
                if row.score_path == CUDA_PATH:
                    words = forecasts[lineage].raw_prediction
                    masses = tuple(SINGLE.decode(w) for w in words[3])
                    expected = masses[target]/sum(masses, F(0))
                    raw_differences += int(expected != SINGLE.decode(words[5][target]))
                else:
                    expected = dict(pending.pending.predictions)[lineage].probabilities[target]
                assert actual == expected
            check_gain(row)
            key = row.identity_id
            sums[key] += row.gain.lower
            counts[key] += 1
            if counts[key] == 3:
                wealth[key] = wealth_oracle(wealth[key], sums[key], 3, identity(runtime, key).rule)
                sums[key], counts[key] = F(0), 0
            assert row.wealth_after == identity(runtime, key).wealth == wealth[key]
            checked += 1
        differences += int(rows[0].candidate_probability != rows[1].candidate_probability)
        after = identity(runtime, cid)
        if before.candidate_cuda_range[0].theta != after.candidate_cuda_range[0].theta:
            changed += 1
        else:
            assert after.candidate_cuda_range is before.candidate_cuda_range
        phases = {p.object_id: p for p in runtime.snapshot().cuda.phases}
        assert all(b.theta == phases[after.current_candidate_cuda].raw_state[0] for b in after.candidate_cuda_range)
        assert after.base_cuda_range is before.base_cuda_range
    assert changed == 6 and differences and raw_differences
    assert runtime.snapshot().alpha_spent == F(1, 2)
    owned(runtime)
    result = audit_snapshot(runtime)
    result.update(independent_score_log_and_wealth_checks=checked, optimizer_range_recomputations=changed,
                  reference_CUDA_score_differences=differences, proper_probability_differs_from_raw_division=raw_differences,
                  unchanged_theta_reuses_its_owned_range=True, CPU_binary64_phases=len(runtime.snapshot().float64_traces))
    return result


def null_case(index):
    labels = tuple(product((0, 1), repeat=5))[index]
    runtime, candidate = fixture(count=6, rules=registration(horizon=5, alpha=F(1, 3)))
    ids = pair(runtime, candidate)
    wealth, crossings = [[], []], []
    for target in labels:
        event(runtime, target)
        for i, iid in enumerate(ids):
            wealth[i].append(str(identity(runtime, iid).wealth))
    for iid in ids:
        crossings.append(identity(runtime, iid).crossing_cursor is not None)
    owned(runtime)
    phases = audit_snapshot(runtime)['phases']
    return {'labels': labels, 'wealth': wealth, 'crossings': crossings, 'phases': phases}


def crossing_case():
    runtime, candidate = fixture()
    ids = pair(runtime, candidate)
    for _ in range(6):
        event(runtime, 0)
    assert runtime.paired_cuda_persistence_result(*ids).status == 'PAIRED_CUDA_CROSSED'
    wealth = tuple(identity(runtime, iid).wealth for iid in ids)
    event(runtime, 1)
    assert tuple(identity(runtime, iid).wealth for iid in ids) == wealth
    assert runtime.paired_cuda_persistence_result(*ids).status == 'PAIRED_CUDA_CROSSED'
    phases = audit_snapshot(runtime)['phases']
    before = runtime.snapshot()
    deliver_context(runtime, 'observation-7', domain(1)[0])
    fault = RuntimeError('actual CUDA commit failed after two crossings')
    with patch.object(gpu, 'commit_event', side_effect=fault):
        try:
            runtime.observe(1)
        except RuntimeError as exc:
            assert exc is fault
        else:
            raise AssertionError('failed CUDA commit acquired evidence authority')
    after = runtime.snapshot()
    assert after.halted and after.pending.record.target == 1 and after.cuda.current == before.cuda.current
    assert after.candidates == before.candidates
    assert runtime.paired_cuda_persistence_result(*ids).status == 'UNRESOLVED'
    assert after.alpha_spent == F(1, 2) and tuple(identity(runtime, iid).wealth for iid in ids) == wealth
    return {'crossing_cursor': 6, 'phases_before_failure': phases,
            'both_published_paths_and_spent_alpha_preserved_after_injected_CUDA_commit_failure': True}


def nontransfer_case():
    delta = F(1, 1 << 25)
    cfg = replace(configuration(), normalizer_cap=2+delta, activation_cap=F(1), initializer_pattern=(delta,))
    graph = Program((Source('x0_0'), Sum('mass', (Term(0, 0),)), Sum('mass', ())), 1, (1, 2))
    runtime, candidate = fixture(cfg=cfg, graph=graph, rules=registration(bound=delta), grid=None)
    rid, cid = pair(runtime, candidate)
    for _ in range(8):
        event(runtime, 0)
    assert runtime.reference_persistence_result(rid).status == 'REFERENCE_CROSSED'
    assert identity(runtime, rid).crossing_cursor == 5
    assert identity(runtime, cid).wealth == 1 and identity(runtime, cid).crossing_cursor is None
    assert all(row.gain.lower == row.gain.upper == 0 for row in runtime.snapshot().persistence_events if row.score_path == CUDA_PATH)
    assert runtime.paired_cuda_persistence_result(rid, cid).status == 'UNRESOLVED'
    rejects(lambda: runtime.cuda_persistence_result(rid))
    rejects(lambda: runtime.reference_persistence_result(cid))
    assert runtime.install(candidate, runtime.paired_cuda_persistence_result(rid, cid)).status == 'UNRESOLVED'
    owned(runtime)
    return {'delta': str(delta), 'reference_crossing_cursor': 5, 'CUDA_gain': '0', 'CUDA_wealth': '1',
            'reference_evidence_transfer_rejected': True, 'phases': audit_snapshot(runtime)['phases']}


def range_case(refresh):
    if refresh:
        cfg = replace(configuration(), initializer_pattern=(F(0),), source_domain=None,
                      semantics=replace(configuration().semantics, states=(DelayedStateSpec('h', 'mass', 2, F(3, 10)),)))
        graph = Program((Source('x0_0'), Sum('mass', (Term(0, 0),)), Sum('mass', ())), 1, (1, 2), (Binding('h', 1),))
        base = replace(zero_program(2), bindings=(Binding('h', 0),))
        runtime, candidate = fixture(cfg=cfg, graph=graph, base=base, unit=1, rate=F(3, 5), grid=None, rules=registration(bound=F(6)))
        rid, cid = pair(runtime, candidate)
        before = identity(runtime, cid)
        event(runtime, 0)
        after = identity(runtime, cid)
        # The exact update lies within the delayed cap; the future half cast
        # is above it. The current physical queue is still the actual old zero.
        assert identity(runtime, rid).status == 'ACTIVE'
        assert after.status == 'UNRESOLVED' and 'delayed-state invariant' in after.reason
        assert after.wealth == before.wealth and not runtime.snapshot().halted
        assert next(s for s in runtime.snapshot().candidates if s.candidate_id == candidate).theta == (F(3, 10),)
        assert runtime.snapshot().cursor == 1 and runtime.snapshot().alpha_spent == F(1, 2)
        assert all(row.score_path == REFERENCE_PATH for row in runtime.snapshot().persistence_events)
        return {'exact_new_theta': '3/10', 'future_half_theta': str(q(q(F(3, 10)), HALF)),
                'ordinary_successor_published_but_unproved_future_CUDA_evidence_stopped': True}
    cfg = replace(configuration(), activation_cap=F(3, 10), normalizer_cap=F(3), source_domain=None,
                  semantics=replace(configuration().semantics, sources=tuple(replace(s, upper=F(3, 10)) for s in configuration().semantics.sources)))
    runtime, candidate = fixture(cfg=cfg)
    ref = runtime.admit_reference_persistence(candidate, 'ref')
    result = runtime.admit_cuda_persistence(candidate, 'cuda')
    assert identity(runtime, ref.identity_id).status == 'ACTIVE'
    assert result.identity_id and identity(runtime, result.identity_id).status == 'UNRESOLVED'
    assert 'whole-domain activation' in result.reason and runtime.snapshot().alpha_spent == F(1, 2)
    assert not runtime.snapshot().observations and not runtime.snapshot().pending
    event(runtime, 0, (F(0), F(0)))
    assert not any(row.score_path == CUDA_PATH for row in runtime.snapshot().persistence_events)
    return {'reference_safe_but_actual_half_range_unproved': True, 'failed_admission_alpha_retained': '1/4',
            'harmless_context_does_not_reactivate_failed_identity': True}


def double_round_case():
    x = F(1, 2)+F(1, 1 << 12)+F(1, 1 << 26)
    cfg = replace(configuration(), source_domain=((x, F(0)),))
    runtime, candidate = fixture(cfg=cfg, rules=registration(bound=F(6)))
    _, cid = pair(runtime, candidate)
    bound = identity(runtime, cid).candidate_cuda_range[0]
    assert bound.source_point == (x, F(0)) and bound.values_upper[0] == F(1, 2)
    event(runtime, 0, (x, F(0)))
    assert audit_snapshot(runtime)['phases'] == 6
    return {'exact_source': str(x), 'actual_R16_R32_source': '1/2', 'wrong_direct_R16_source': '1025/2048',
            'owned_bound_and_actual_forecast_preserve_both_roundings': True}


def mismatch_case():
    runtime, candidate = fixture()
    ids = pair(runtime, candidate)
    before = runtime.snapshot()
    original = gpu.evaluate
    import torch
    def changed(*args, **kwargs):
        result = original(*args, **kwargs)
        # Change one stored mass by one ULP, within the registered reference
        # tolerance, without a foreign GPU allocation or a changed schedule.
        words = list(gpu.raw_tensor(result.masses))
        words[0] += 1
        result.masses.view(torch.int32).copy_(torch.tensor(words, dtype=torch.int32, device='cpu'))
        # Execute the previous tolerance relation too: it really accepts this
        # perturbed baseline forecast. Exact conformance is an extra premise.
        reference = evaluate(args[0], args[1], (), args[3])
        check_prediction(reference, widened_prediction(raw_prediction(result)), Float64Contract(F(1, 100), F(1, 100)),
            args[1], normalizer_cap=runtime.contract.normalizer_cap, activation_cap=runtime.contract.activation_cap, bit_limit=32768)
        return result
    with patch.object(gpu, 'evaluate', changed):
        result = deliver_context(runtime, 'observation-0', domain(1)[0])
    assert result.status == 'UNRESOLVED'
    after = runtime.snapshot()
    assert after.halted and after.pending.record.target is None and not after.observations
    assert after.candidates == before.candidates and after.cuda.current == before.cuda.current
    assert 'exact registered rounded forward' in after.cuda.phases[-1].reason
    assert all(identity(runtime, iid).status == 'UNRESOLVED' for iid in ids)
    assert after.alpha_spent == F(1, 2) and not after.persistence_events
    return {'one_ULP_forecast_error_within_reference_tolerance_rejected_before_target': True,
            'actual_output_retained_without_repair_from_reference': True}


def freshness_case():
    runtime, candidate = fixture()
    rid, cid = pair(runtime, candidate)
    event(runtime, 0)
    event(runtime, 0)
    old = identity(runtime, cid)
    runtime.cancel_cuda_persistence(cid)
    fresh = runtime.admit_cuda_persistence(candidate, 'cuda')
    new = identity(runtime, fresh.identity_id)
    assert old.wealth > 1 and new.wealth == 1 and new.start_cursor == 2
    assert new.initial_candidate_cuda != old.initial_candidate_cuda
    assert runtime.snapshot().alpha_spent == F(3, 4)
    rejects(lambda: runtime.paired_cuda_persistence_result(rid, fresh.identity_id))
    event(runtime, 0)
    assert not any(e.identity_id == fresh.identity_id and e.cursor < 2 for e in runtime.snapshot().persistence_events)
    runtime.cancel_cuda_persistence(fresh.identity_id)
    event(runtime, 0)
    result = runtime.admit_cuda_persistence(candidate, 'cuda')
    assert result.status == 'UNRESOLVED' and result.identity_id is None
    before = runtime.snapshot()
    runtime.retire_candidate(candidate)
    assert runtime.reference_persistence_result(rid).status == 'UNRESOLVED'
    assert runtime.snapshot().cuda.phases == before.cuda.phases
    assert runtime.snapshot().alpha_spent == F(3, 4)
    return {'cancel_readmit_retire_cannot_refund_or_inherit_alpha_wealth_or_old_targets': True,
            'different_starting_device_trajectories_cannot_pair': True}


def failed_crossing_case():
    runtime, candidate = fixture()
    rid, cid = pair(runtime, candidate)
    for _ in range(5):
        event(runtime, 0)
    original = runtime._machine.realize
    def fail(object_id, kind, value, chi):
        if kind == 'cuda_persistence_state' and value.status == 'CUDA_CROSSED':
            raise ResourceExceeded('prepaid CUDA crossing state cannot be retained')
        return original(object_id, kind, value, chi)
    with patch.object(runtime._machine, 'realize', fail):
        event(runtime, 0)
    assert runtime.reference_persistence_result(rid).status == 'REFERENCE_CROSSED'
    assert runtime.cuda_persistence_result(cid).status == 'UNRESOLVED'
    assert identity(runtime, cid).crossing_cursor is None and runtime.snapshot().alpha_spent == F(1, 2)
    assert runtime.paired_cuda_persistence_result(rid, cid).status == 'UNRESOLVED'
    assert any(e.identity_id == cid and e.wealth_after >= 4 for e in runtime.snapshot().persistence_events)
    event(runtime, 0)
    assert runtime.cuda_persistence_result(cid).status == 'UNRESOLVED'
    return {'retained_threshold_score_does_not_replace_failed_owned_crossing_state': True,
            'ordinary_continuation_does_not_resume_failed_identity': True}


CASES = {'scores': scores_case, 'crossing': crossing_case, 'nontransfer': nontransfer_case,
         'range-admission': lambda: range_case(False), 'range-refresh': lambda: range_case(True),
         'double-round': double_round_case, 'mismatch': mismatch_case, 'freshness': freshness_case,
         'failed-crossing': failed_crossing_case}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--case')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    if args.case:
        if args.write:
            parser.error('a subcase cannot replace canonical evidence')
        result = range_audit() if args.case == 'range' else null_case(int(args.case[5:])) if args.case.startswith('null-') else CASES[args.case]()
        print(json.dumps(result))
        return
    report = {'status': 'PASS', 'scope': 'current CUDA whole-domain bounds, exact actual forecasts and owned fresh same-path evidence; no install/release',
              'range': range_audit()}
    print('exact range and independent rounded model PASS', flush=True)
    def execute(case):
        completed = subprocess.run([sys.executable, '-B', str(Path(__file__)), '--case', case],
                                   capture_output=True, text=True, timeout=60)
        if completed.returncode:
            raise RuntimeError(completed.stdout+completed.stderr)
        return json.loads(completed.stdout)
    trees, crossings, phases = ({(): F(1)}, {(): F(1)}), [0, 0], 0
    for index in range(32):
        row = execute('null-'+str(index))
        labels = tuple(row['labels'])
        for leg in (0, 1):
            for t, wealth in enumerate(row['wealth'][leg]):
                assert trees[leg].setdefault(labels[:t+1], F(wealth)) == F(wealth)
            crossings[leg] += int(row['crossings'][leg])
        phases += row['phases']
        if (index+1) % 8 == 0:
            print(str(index+1)+' complete actual CUDA null branches PASS', flush=True)
    checks = 0
    for tree in trees:
        for prefix, wealth in tree.items():
            if len(prefix) < 5:
                assert (tree[prefix+(0,)]+tree[prefix+(1,)])/2 <= wealth
                checks += 1
    probabilities = tuple(F(n, 32) for n in crossings)
    assert all(0 < p <= F(1, 3) for p in probabilities)
    report['null'] = {'complete_fair_label_paths': 32, 'ordinary_events': 160, 'independent_owned_CUDA_phase_checks': phases,
        'two_path_conditional_wealth_inequalities': checks, 'crossing_probabilities': list(map(str, probabilities)),
        'each_path_alpha': '1/3', 'external_null': 'fair independent labels; both fixed mass ratio products are 8/9 < 1'}
    for key in CASES:
        report[key] = execute(key)
        print(key+' PASS', flush=True)
    if args.write:
        (ROOT/'evidence/minimal/FP_CUDA_PERSISTENCE_AUDIT.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
