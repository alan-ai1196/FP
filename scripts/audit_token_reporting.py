"""Exact/CPU audits of terminal frozen-token reporting. No corpus or GPU run."""
from dataclasses import replace
from decimal import Decimal, localcontext
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from types import FunctionType, SimpleNamespace
from contextlib import contextmanager
from unittest.mock import patch
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts'), str(ROOT/'experiments/next_token')]
from fp_reference import ReferenceCompilerRuntime
from fp_reference.core import ContractError
from fp_reference.data_usage import StreamSpec, source_mapping
from fp_reference.encoding import pack
from fp_reference.ingress import encode_context
from fp_reference.numerics import LogInterval
from fp_reference.resources import ResourceExceeded
from fp_reference.semantics import ArithmeticUnresolved, evaluate
from fp_reference.token_reporting import TokenReportingContract, REPORT_PORTS, mass_loss, add_loss
from fp_reference import token_reporting as report
from fp_reference.token_arrays import CPUArrays
from fp_reference.token_array_check import CheckedPrimitives
from fp_reference.token_cuda_prefix import transition, fresh_origin, check_prediction
from fp_reference import token_cuda_prefix as cuda_execution
from fp_reference.cuda_prefix import _CudaPrefix
from fp_reference.token_execution import TokenReferenceMachine
from fp_reference.token_sources import TokenValues, TokenContext
from fp_reference.shared_reference import SharedPlannedObject, decoded_buffer, ROOT_KIND
from fp_reference.machine import PlannedObject
from audit_owned_token_learner import fixture, registration, live
from audit_reference_construction import validate_residency
from audit_shared_token_retention import STORAGE
from audit_token_cuda_owner import cuda_contract
import native_tokens as tokens


def rejects(fn, expected=ContractError):
    try:
        fn()
    except expected:
        return
    raise AssertionError('reporting accepted an invalid operation')


def report_registration(unit=2, count=2, report_count=3, terms=12):
    d, initial = fixture(unit, 'mixed')
    cc, p, online = registration(d, initial, count=count)
    stream = StreamSpec('report', 'validation', tuple(f'report/{i}' for i in range(report_count)))
    online = replace(online, data=replace(online.data, streams=online.data.streams+(stream,)))
    cfg = TokenReportingContract('report', terms, 40)
    return cc, p, online, cfg


def setup(unit=2, count=2, report_count=3, shared=False, terms=12):
    cc, p, online, cfg = report_registration(unit, count, report_count, terms)
    rt = ReferenceCompilerRuntime(cc, p, online=online, reporting=cfg, shared_storage=STORAGE if shared else None)
    return rt, p


def train(rt, targets=(0, 1)):
    for i, target in enumerate(targets):
        assert rt.predict_next(f'train/{i}', encode_context(())).status == 'PREDICTED_REFERENCE'
        assert rt.observe(target).status == 'OBSERVED_REFERENCE'


def decimal(value):
    return Decimal(value.numerator)/Decimal(value.denominator)


def numerical():
    cases = 0
    with localcontext() as ctx:
        ctx.prec = 90
        for masses in product((F(1, 8), F(1, 3), F(5, 2)), repeat=3):
            total = sum(masses, F(0))
            assert sum((m/total for m in masses), F(0)) == 1
            for mass, slack in product(masses, (F(0), F(1, 64))):
                lo, hi = total*(1-slack), total*(1+slack)
                bounds = mass_loss(mass, lo, hi, terms=16, bit_limit=32768)
                loss = -(decimal(mass)/decimal(total)).ln()
                assert decimal(bounds.lower) <= loss <= decimal(bounds.upper)
                cases += 1
        assert mass_loss(F(1), F(1, 2), F(1), terms=16, bit_limit=32768) == LogInterval(F(0), F(0))
    rejects(lambda: mass_loss(F(2), F(1), F(1), terms=2, bit_limit=1024))
    rejects(lambda: mass_loss(F(1), F(2), F(1), terms=2, bit_limit=1024))
    rejects(lambda: mass_loss(F(0), F(1), F(1), terms=2, bit_limit=1024))
    rejects(lambda: add_loss((0, 0), LogInterval(F(-1), F(1)), fractional_bits=10, bit_limit=1024))
    rejects(lambda: add_loss((0, 0), LogInterval(F(0), F(1)), fractional_bits=10**12, bit_limit=1024), ArithmeticUnresolved)
    total, exact = (0, 0), [F(0), F(0)]
    for n in range(1, 65):
        loss = LogInterval(F(n, n+1), F(n+1, n+2))
        total = add_loss(total, loss, fractional_bits=17, bit_limit=32768)
        exact = [x+y for x, y in zip(exact, (loss.lower, loss.upper))]
        lower, upper = (F(x, (1 << 17)*n) for x in total)
        assert lower <= exact[0]/n <= exact[1]/n <= upper
        assert exact[0]/n-lower < F(1, 1 << 17) and upper-exact[1]/n < F(1, 1 << 17)
    return dict(normalized_mass_cases=cases, directed_mean_prefixes=64,
        huge_scale_refused_before_shift=True, precision='exact Fractions; independent Decimal90 loss check')


def histories():
    words = events = source_differences = roots = 0
    for training, reporting in product(product((0, 1), repeat=2), product((0, 1), repeat=3)):
        expected = {}
        allocation = ReferenceCompilerRuntime._allocate
        def capture(rt, owner, objects):
            for obj in objects:
                if type(obj) in (PlannedObject, SharedPlannedObject):
                    expected[obj.spec.object_id] = pack(obj.value)
            return allocation(rt, owner, objects)
        shared = bool(words % 2)
        with patch.object(ReferenceCompilerRuntime, '_allocate', capture):
            rt, p = setup(unit=1 if words % 2 else 2, shared=shared)
            train(rt, training)
            before = validate_residency(rt)
            state = live(before)
            owned_state = rt._candidates[before.deployed_id].learner
            literal = state.materialize(scalar_cap=1000)
            rules, graph = tokens.materialize(p.definition)
            assert rt.begin_report().status == 'REPORTING'
            assert rt.report_result().native_mean is None
            for t, target in enumerate(reporting):
                assert rt.predict_report(f'report/{t}').status == 'PREDICTED_REPORT'
                pending = rt.snapshot().token_report.pending
                wanted_past = tuple(p.definition.sources.vocabulary if lag > t else reporting[t-lag]
                                   for lag in range(1, p.definition.sources.context+1))
                assert pending.record.sources.past == wanted_past
                assert pending.record.sources.position == t
                assert pending.prediction.before.cursor == len(training)
                source_differences += pending.prediction.window != state.source
                expected_prediction = evaluate(graph, rules, literal.theta, source_mapping(pending.record.sources),
                                               literal.delayed, bit_limit=32768)
                assert tuple(pending.prediction.probabilities) == expected_prediction.probabilities
                assert rt.observe_report(target).status == ('COMPLETE_REPORT' if t == len(reporting)-1 else 'SCORED_REPORT')
                snapshot = validate_residency(rt)
                assert snapshot.candidates == before.candidates and live(snapshot) == state
                assert rt._candidates[before.deployed_id].learner is owned_state
                assert snapshot.cursor == before.cursor and snapshot.observations == before.observations
                assert snapshot.event_traces == before.event_traces and snapshot.queries == before.queries
                assert snapshot.data_uses[-1].purpose == 'report'
                event = snapshot.token_report.events[-1]
                assert event.native_probability == expected_prediction.probabilities[target]
                assert event.record.target == target and event.physical_loss is None
                with localcontext() as ctx:
                    ctx.prec = 90
                    true_loss = -decimal(event.native_probability).ln()
                    assert decimal(event.native_loss.lower) <= true_loss <= decimal(event.native_loss.upper)
                events += 1
            result = rt.report_result()
            assert result.status == 'COMPLETE_REPORT' and result.completed == result.declared == 3
            with localcontext() as ctx:
                ctx.prec = 90
                exact = sum((-decimal(e.native_probability).ln() for e in rt.snapshot().token_report.events), Decimal(0))/3
                assert decimal(result.native_mean.lower) <= exact <= decimal(result.native_mean.upper)
            snapshot = validate_residency(rt)
            buffers = dict(snapshot.buffers)
            for object_id, spec in snapshot.resources['objects'].items():
                if ':report:' not in object_id or spec['kind'] == 'reserved_target':
                    continue
                actual = (b''.join(decoded_buffer(snapshot, object_id, byte_cap=STORAGE.expanded_cap,
                                                  reference_cap=STORAGE.reference_cap))
                          if spec['kind'].startswith(ROOT_KIND) else buffers[object_id])
                assert actual == expected[object_id]
                roots += 1
        words += 1
    return dict(histories=words, report_events=events, source_clocks_distinct_from_frozen_learner=source_differences,
        complete_reporting_records_decoded=roots, exact_literal_predictions=True, all_learner_and_training_records_unchanged=True)


def authority():
    rt, p = setup()
    rejects(rt.begin_report)
    rejects(lambda: rt.predict_report('report/0'))
    train(rt)
    assert rt.begin_report().status == 'REPORTING'
    rejected = []
    for name, method in vars(ReferenceCompilerRuntime).items():
        if not name.startswith('_') and type(method) is FunctionType and name not in REPORT_PORTS | {'snapshot'}:
            rejects(lambda name=name: getattr(rt, name)())
            rejected.append(name)
    rejects(lambda: rt.predict_report('train/0'))
    class CallbackID:
        def __eq__(self, other):
            raise AssertionError('an observation ID invoked caller code')
    rejects(lambda: rt.predict_report(CallbackID()))
    rejects(lambda: rt.predict_report('report/1'))
    rejects(lambda: rt.observe_report(0))
    assert rt.predict_report('report/0').status == 'PREDICTED_REPORT'
    rejects(lambda: rt.predict_report('report/0'))
    rejects(lambda: rt.observe_report(2))
    assert rt.observe_report(0).status == 'SCORED_REPORT'
    rejects(lambda: rt.observe_report(0))
    for i in (1, 2):
        assert rt.predict_report(f'report/{i}').status == 'PREDICTED_REPORT'
        rt.observe_report(1)
    rejects(lambda: rt.predict_report('report/3'))
    rejects(rt.begin_report)
    rejects(lambda: rt._data_usage.record(rt.snapshot().token_report.records, 'ordinary', rt._runtime_id, 0))
    rejects(lambda: rt._data_usage.record(rt.snapshot().observations, 'report', rt._runtime_id, 0))
    cfg = rt.contract
    rejects(lambda: ReferenceCompilerRuntime(cfg, p, online=rt.online_contract,
                                            reporting=TokenReportingContract('train', 12, 40)))
    rejects(lambda: ReferenceCompilerRuntime(cfg, p, online=rt.online_contract,
                                            reporting=TokenReportingContract('report', 12, 10**12)), ArithmeticUnresolved)
    rejects(lambda: setup(unit=2, count=3))
    return dict(permanently_frozen_public_ports=rejected, split_roles_and_order_preserved=True,
                partial_training_and_unbounded_precision_refused=True)


def failures():
    results = []
    for stage in ('score-work', 'scored-retention', 'accumulator-retention', 'changed-forecast', 'host-memory'):
        rt, _ = setup(shared=True)
        train(rt)
        before = rt.snapshot()
        rt.begin_report()
        rt.predict_report('report/0')
        paid, retain = report._pay, report._retain
        def fee(runtime, label, work):
            if label == 'score' and stage == 'score-work':
                raise ResourceExceeded('deliberate report work boundary')
            return paid(runtime, label, work)
        def retention(runtime, label, value):
            if label.endswith('scored') and stage in ('scored-retention', 'host-memory'):
                raise MemoryError('deliberate reporting host boundary') if stage == 'host-memory' else ResourceExceeded('deliberate report payload boundary')
            if label.endswith('accumulator') and stage == 'accumulator-retention':
                raise ResourceExceeded('deliberate report accumulator boundary')
            return retain(runtime, label, value)
        if stage == 'changed-forecast':
            pending = rt._token_report.pending
            rt._token_report = replace(rt._token_report, pending=replace(pending,
                prediction=replace(pending.prediction, normalizer=2*pending.prediction.normalizer)))
        with patch.object(report, '_pay', fee), patch.object(report, '_retain', retention):
            if stage == 'changed-forecast':
                rejects(lambda: rt.observe_report(1))
            elif stage == 'host-memory':
                rejects(lambda: rt.observe_report(1), MemoryError)
            else:
                assert rt.observe_report(1).status == 'UNRESOLVED'
        snapshot = validate_residency(rt)
        assert snapshot.halted is not None and snapshot.event_phase == 'halted'
        assert snapshot.candidates == before.candidates and snapshot.observations == before.observations
        assert snapshot.token_report.records[-1].target == 1
        pending = snapshot.token_report.pending
        assert pending.record.target == 1 and dict(snapshot.buffers)[pending.target_object_id] == pack(rt._target_slot(1))
        assert not snapshot.token_report.events
        rejects(lambda: rt.observe_report(1))
        rejects(lambda: rt.construct_candidate(dict(snapshot.programs)[snapshot.candidates[0].program_id]))
        results.append(stage)
    rt, _ = setup(terms=2000)
    train(rt)
    rt.begin_report()
    rt.predict_report('report/0')
    result = rt.observe_report(1)
    assert result.status == 'UNRESOLVED' and 'integer' in result.reason
    assert rt.snapshot().token_report.records[-1].target == 1 and not rt.snapshot().token_report.events
    results.append('actual-logarithm-integer-limit')
    return dict(post_target_failures=results, actual_target_and_forecast_retained=True, no_successor_or_score_published=True)


def physical_recipe():
    phases = labels = 0
    for kind in ('mixed', 'zero-embedding', 'zero-core'):
        d, initial = fixture(2, kind)
        cc, p, online = registration(d, initial)
        cfg = cuda_contract(cc.initializer_pattern)
        m = TokenReferenceMachine(cc.initializer_pattern)
        native = m.initial_state(p, cc.semantics, m.initializer(p.slot_count, cc.initializer_pattern),
                                 0, spec=online.learner, bit_limit=32768)
        def phase(kind, before=None, prediction=None, window=None, target=None, birth=None):
            nonlocal phases
            a = CPUArrays(element_cap=cfg.initializer.element_cap, cell_cap=cfg.phase_output_cells,
                          audit=CheckedPrimitives(cfg.exact_cell_cap))
            value = transition(kind, p, cfg, before, prediction, window, target, native.cursor, birth, a)
            a.check()
            phases += 1
            return value
        physical = phase('initialize', birth=fresh_origin(p, cfg, 0, online.learner, cc.semantics, 32768))
        before = physical.raw()
        for history in product((0, 1), repeat=3):
            context = TokenContext(cfg.initializer.sources, 3, history)
            native_prediction = m.predict(p, cc.semantics, native, TokenValues(context), bit_limit=32768)
            prediction = phase('predict', physical, window=native_prediction.window)
            pre = prediction.raw()
            bounds = check_prediction(native, native_prediction, before, pre, cfg, F(100), F(100))
            readouts = [phase('readout', physical, prediction, native_prediction.window, y) for y in (0, 1)]
            masses = [F(float(r.raw().mass.array())) for r in readouts]
            total = sum(masses, F(0))
            assert bounds['stored_sum_lower'][0] <= total <= bounds['stored_sum_upper'][0]
            assert sum((mass/total for mass in masses), F(0)) == 1
            assert physical.raw() == before and prediction.raw() == pre
            with localcontext() as ctx:
                ctx.prec = 90
                for mass in masses:
                    loss = mass_loss(mass, bounds['stored_sum_lower'][0], bounds['stored_sum_upper'][0],
                                     terms=16, bit_limit=32768)
                    expected = -(decimal(mass)/decimal(total)).ln()
                    assert decimal(loss.lower) <= expected <= decimal(loss.upper)
                    labels += 1
            wrong = replace(prediction, predecessor=before.cpu())
            rejects(lambda: phase('readout', physical, wrong, native_prediction.window, 0))
    # Complete uniform V=3 mass normalization differs from stored-Z division.
    mass = F(11184811, 33554432)
    total = 3*mass
    assert total == F(33554433, 33554432) and mass/total == F(1, 3) and mass/F(1) != F(1, 3)
    return dict(checked_cpu_phases=phases, normalized_label_losses=labels, original_residents_unchanged=True,
                stored_Z_counterexample=True, device_authority=False)


def owned_phase_control():
    """CPU substitute only at the array backend; execute the full phase logic."""
    class Arena:
        @contextmanager
        def phase(self, identity):
            yield SimpleNamespace(index=0)
        def require_initialized(self, value):
            pass  # This control makes no arena ownership/device claim.
    def arrays(workspace, readout_buffer, **kwargs):
        return CPUArrays(**kwargs)
    d, initial = fixture(2, 'mixed')
    cc, p, online = registration(d, initial)
    cfg = cuda_contract(cc.initializer_pattern)
    m = TokenReferenceMachine(cc.initializer_pattern)
    native = m.initial_state(p, cc.semantics, m.initializer(p.slot_count, cc.initializer_pattern),
                             0, spec=online.learner, bit_limit=32768)
    owner = SimpleNamespace(contract=cfg, arena=Arena(), current={}, staged={}, predicted={}, phases={}, _values={}, token=True)
    def execute(kind, reference, context=None, forecast=None, target=None, origin='ordinary', observation_id=None):
        with patch.object(cuda_execution, 'CudaArrays', arrays):
            row, error = cuda_execution.execute(owner, f'cpu-phase:{len(owner.phases)}', kind, p, 'incumbent', reference,
                rules=cc.semantics, spec=online.learner, bit_limit=32768, ordinary_cursor=reference.cursor,
                origin=origin, observation_id=observation_id, sources=context, reference_prediction=forecast,
                target=target, normalizer_cap=F(100), activation_cap=F(100), source_domain=None, readout_buffer=None)
        if error is None:
            _CudaPrefix.accept(owner, row)
        return row, error
    row, error = execute('initialize', native, origin='construction')
    assert error is None
    owner.current['incumbent'] = row.object_id
    for t, target in enumerate((0, 1)):
        context = TokenValues(TokenContext(cfg.initializer.sources, native.source.position, native.source.past))
        forecast = m.predict(p, cc.semantics, native, context, bit_limit=32768)
        row, error = execute('predict', native, context, forecast, observation_id=f'train/{t}')
        assert error is None
        observed = m.observe(p, native, online.learner, forecast, target,
                             rules=cc.semantics, bit_limit=32768, sources=context)
        row, error = execute('observe', observed, context, forecast, target, observation_id=f'train/{t}')
        assert error is None
        native = observed
        if native.unit_count == online.learner.update_unit:
            native = m.commit(native, online.learner, bit_limit=32768)
            row, error = execute('commit', native)
            assert error is None
        owner.current['incumbent'] = row.object_id
    frozen = dict(owner.current), dict(owner.staged)
    context = TokenValues(TokenContext(cfg.initializer.sources, 0, (2,)*3))
    forecast = m.predict(p, cc.semantics, native, context, bit_limit=32768)
    prediction, error = execute('predict', native, context, forecast, origin='report', observation_id='report/0')
    assert error is None
    row, error = execute('readout', native, context, forecast, 1, origin='report', observation_id='report/0')
    assert error is None and row.phase == 'report:readout'
    assert (owner.current, owner.staged) == frozen
    assert row.raw_state == owner.phases[frozen[0]['incumbent']].raw_state
    assert row.prediction_phase == prediction.object_id and row.raw_prediction.label == 1
    for wrong_origin, wrong_id in (('ordinary', 'report/0'), ('report', 'report/1')):
        failed, error = execute('readout', native, context, forecast, 1, origin=wrong_origin, observation_id=wrong_id)
        assert type(error) is ContractError and failed.status == 'EXECUTION_FAILED'
        assert (owner.current, owner.staged) == frozen
    actual = owner._values[prediction.object_id]
    owner._values[prediction.object_id] = replace(actual, forecast=replace(actual.forecast, window=actual.forecast.window.append(1)))
    failed, error = execute('readout', native, context, forecast, 1, origin='report', observation_id='report/0')
    assert type(error) is ContractError and 'pre-target words changed' in failed.reason
    assert (owner.current, owner.staged) == frozen
    return dict(checked_phases=8, readout_does_not_publish_staged_or_current_learner=True,
                altered_origin_identity_or_forecast_refusals=3, actual_device=False)


def actual(case):
    """One fresh actual owner, inside the launcher-attached 4-GiB host job."""
    from fp_reference.host_resources import HostResourceContract
    from audit_reference_construction import limits
    cc, program, online, reporting = report_registration(count=4, report_count=4)
    cc = replace(cc, limits=limits(384 << 20, 10**15))
    cfg = cuda_contract(cc.initializer_pattern)
    rt = ReferenceCompilerRuntime(cc, program, online=online, reporting=reporting,
        cuda=cfg, shared_storage=STORAGE,
        host=HostResourceContract(4 << 30, {role: 4 << 30 for role in ('deployment', 'compiler')}))
    train(rt, (0, 1, 1, 0))
    before = validate_residency(rt)
    frozen_current, frozen_staged = dict(rt._cuda.current), dict(rt._cuda.staged)
    frozen_words = rt._cuda.phases[frozen_current[rt._deployed_id]].raw_state
    assert rt.begin_report().status == 'REPORTING'
    targets = (1, 0, 0, 1)
    for t, target in enumerate(targets):
        assert rt.predict_report(f'report/{t}').status == 'PREDICTED_REPORT'
        if case == 'forecast-forgery':
            identity = rt._cuda.predicted[rt._deployed_id]
            original = rt._cuda._values[identity]
            wrong = original.forecast.window.append(1)
            rt._cuda._values[identity] = replace(original, forecast=replace(original.forecast, window=wrong))
            rejects(lambda: rt.observe_report(target), RuntimeError)
            snapshot = validate_residency(rt)
            assert snapshot.halted and snapshot.token_report.records[-1].target == target
            pending = snapshot.token_report.pending
            assert dict(snapshot.buffers)[pending.target_object_id] == pack(rt._target_slot(target))
            assert not snapshot.token_report.events
            failure = tuple(rt._cuda.phases.values())[-1]
            assert failure.phase == 'report:readout' and failure.status == 'EXECUTION_FAILED'
            assert 'pre-target words changed' in failure.reason
            break
        result = rt.observe_report(target)
        assert result.status == ('COMPLETE_REPORT' if t == 3 else 'SCORED_REPORT'), result.reason
        snapshot = validate_residency(rt)
        assert snapshot.token_report.events[-1].physical_loss is not None
        assert snapshot.token_report.events[-1].record.sources.position == t
    after = validate_residency(rt)
    assert after.candidates == before.candidates and after.observations == before.observations
    assert after.cursor == before.cursor == 4
    assert (rt._cuda.current, rt._cuda.staged) == (frozen_current, frozen_staged)
    assert rt._cuda._values[frozen_current[rt._deployed_id]].raw() == frozen_words
    for port in ('begin_report', 'observe', 'construct_candidate', 'query', 'install_cuda'):
        rejects(lambda port=port: getattr(rt, port)())
    rows = tuple(rt._cuda.phases.values())
    outcome = dict(training_events=4, complete_training_units=2, report_events=len(after.token_report.events),
        report_targets=len(after.token_report.records), checked_phases=sum(p.status == 'CHECKED_CUDA_PREFIX_PHASE' for p in rows),
        checked_device_words=sum(p.forward_operations for p in rows), frozen_native_and_physical_learners_preserved=True,
        owned_reference_peak=after.resources['peak']['reference_payload_bytes'])
    if case == 'frozen-report':
        result = rt.report_result()
        assert result.status == 'COMPLETE_REPORT' and result.native_mean is not None and result.physical_mean is not None
        outcome.update(native_mean_nats=[str(result.native_mean.lower), str(result.native_mean.upper)],
            physical_mean_nats=[str(result.physical_mean.lower), str(result.physical_mean.upper)],
            finite_toy_control_only=True)
    else:
        outcome.update(changed_actual_forecast_refused_after_target=True, no_loss_or_learner_published=True)
    rt._cuda.check()
    arena = rt._cuda.arena
    outcome['arena'] = dict(native_allocation_counter=arena._counter, current_allocation_counter=arena._allocation_counter(),
        consumed_bytes=arena._cursor, phases=len(arena._phases), regions=len(arena._regions), **arena._last_usage)
    return outcome, rt


def worker(case, output):
    from dataclasses import asdict
    import time
    import traceback
    from fp_reference.host_resources import HostResourceContract, _WindowsProcessHost
    from audit_token_reference_host import measured
    host = _WindowsProcessHost(HostResourceContract(4 << 30, {r: 4 << 30 for r in ('deployment', 'compiler')}))
    before, start = measured(host), time.perf_counter()
    result, code = dict(status='RUNNING', case=case, before=before), 0
    Path(output).write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    try:
        import torch
        torch.set_num_threads(1)
        outcome, rt = actual(case)
        result.update(status='PASS_ACTUAL_FROZEN_TOKEN_REPORTING', outcome=outcome,
                      device=asdict(rt._cuda._device.check()))
    except Exception as error:
        code = 2
        result.update(status='FAILED', error_type=type(error).__name__, reason=str(error)[:2000],
                      traceback=traceback.format_exc()[-5000:])
    result.update(after=measured(host), worker_wall_seconds=time.perf_counter()-start)
    Path(output).write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    return code


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--worker', choices=('frozen-report', 'forecast-forgery'))
    parser.add_argument('--output')
    args = parser.parse_args()
    if args.worker:
        if not args.output:
            parser.error('worker requires output and the externally preattached host job')
        raise SystemExit(worker(args.worker, args.output))
    results = {}
    for section in (numerical, histories, authority, failures, physical_recipe, owned_phase_control):
        results[section.__name__] = section()
        print(section.__name__+': PASS', flush=True)
    result = dict(status='PASS_EXACT_AND_CPU_CONTROL', scope='finite frozen reporting only; no corpus, device or model-quality result', **results)
    assert 'torch' not in sys.modules
    if args.write:
        (ROOT/'evidence/minimal/FP_TOKEN_REPORTING_CPU.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
