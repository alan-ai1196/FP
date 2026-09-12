"""Owned control admission, with the historical unbounded-history witness.

This proves no complete host-memory bound. It excludes free owned control
mutations after the registered cumulative work cannot fund their admission.
"""
from dataclasses import fields, replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json
import subprocess
import sys
import types

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts'), str(ROOT/'theory/numerical_checks')]

from fp_reference import ReferenceCompilerRuntime
from fp_reference.data_usage import StochasticStreamLaw
from fp_reference.float64_bridge import Float64Contract
from fp_reference.info import Moment, QuerySpec
from fp_reference.resources import ResourceExceeded
from fp_reference.search import ReferenceSearchSpec
from audit_cpu_installation import SMALL, fixture as install_fixture, install
from audit_paired_cpu_persistence import SOURCE_PAIR, config, registration
from audit_reference_construction import contract, limits, zero_program
from audit_reference_events import online
from audit_reference_persistence import event
from audit_reference_search import runtime_fixture as search_fixture


HISTORICAL_COMMIT = '8880371'
CASES = ('construct', 'retire', 'query', 'admit-reference', 'admit-float64',
         'cancel-reference', 'cancel-float64', 'start-search', 'advance-search',
         'cancel-search', 'install')


def historical_modules(commit, names):
    # Execute the original machine and Runtime source without keeping another
    # source tree. Dependencies unchanged by this correction remain shared.
    saved = {name: sys.modules[name] for name in names}
    loaded = {}
    try:
        for name in names:
            path = f'src/reference_compiler/{name.replace(".", "/")}.py'
            source = subprocess.check_output(['git', 'show', f'{commit}:{path}'], cwd=ROOT, text=True, encoding='utf-8')
            module = types.ModuleType(name)
            module.__package__ = 'fp_reference'
            sys.modules[name] = module
            exec(compile(source, f'git:{commit}:{path}', 'exec'), module.__dict__)
            loaded[name] = module
        return loaded
    finally:
        sys.modules.update(saved)


def historical_runtime():
    return historical_modules(HISTORICAL_COMMIT, ('fp_reference.machine', 'fp_reference.runtime'))['fp_reference.runtime']


def history_witness():
    old = historical_runtime()
    current_cfg = contract()
    cfg = old.ConstructionContract(**{field.name: getattr(current_cfg, field.name) for field in fields(current_cfg)})
    base = old.ReferenceCompilerRuntime(cfg, zero_program(2)).snapshot()
    cap = base.resources['spent']['compiler']['work']+1
    cfg = replace(cfg, limits=limits(work_cap=cap))
    rt = old.ReferenceCompilerRuntime(cfg, zero_program(2))
    assert rt.construct_candidate(zero_program(2)).status == 'UNRESOLVED'
    before = rt.snapshot()
    for _ in range(64):
        assert rt.construct_candidate(zero_program(2)).status == 'UNRESOLVED'
    after = rt.snapshot()
    assert after.resources['spent'] == before.resources['spent']
    assert after.resources['current'] == before.resources['current']
    assert after.resources['peak'] == before.resources['peak']
    assert after.next_candidate-before.next_candidate == len(after.attempts)-len(before.attempts) == 64
    return {'source_commit': HISTORICAL_COMMIT, 'fixed_compiler_work_cap': cap,
            'extra_unfunded_requests': 64, 'work_current_and_peak_payload_unchanged': True,
            'extra_candidate_ids': after.next_candidate-before.next_candidate,
            'extra_owners': len(after.resources['owners'])-len(before.resources['owners']),
            'extra_resource_events': len(after.resources['events'])-len(before.resources['events']),
            'extra_attempt_records': len(after.attempts)-len(before.attempts)}


def setup(case, cfg):
    if case == 'install':
        rt, proposal, ids = install_fixture(cfg=cfg)
        return rt, lambda: install(rt, proposal, ids)
    query = QuerySpec('labels', (Moment((), 1),), (F(0),), (F(1),), 2, 4)
    run = replace(online(cfg, 80, unit=2, rate=F(0), grid=16, queries=(query,)),
                  float64=Float64Contract(F(1, 1 << 24), F(1, 1 << 24)),
                  persistence=registration(bound=F(3), horizon=10),
                  searches=(ReferenceSearchSpec('native', SMALL, ('observation-0', 'observation-1')),))
    run = replace(run, data=replace(run.data, stream_law=StochasticStreamLaw('external audit producer')))
    rt = ReferenceCompilerRuntime(cfg, zero_program(2), online=run)
    candidate = rt.construct_candidate(SOURCE_PAIR).candidate_id
    assert candidate
    event(rt, 0)
    event(rt, 1)
    actions = {'construct': lambda: rt.construct_candidate(SOURCE_PAIR),
               'retire': lambda: rt.retire_candidate(candidate),
               'query': lambda: rt.query('labels', ('observation-0', 'observation-1')),
               'admit-reference': lambda: rt.admit_reference_persistence(candidate, 'ref'),
               'admit-float64': lambda: rt.admit_float64_persistence(candidate, 'finite'),
               'start-search': lambda: rt.start_reference_search('native')}
    if case.startswith('cancel-') and case != 'cancel-search':
        physical = case == 'cancel-float64'
        admitted = (rt.admit_float64_persistence(candidate, 'finite') if physical else
                    rt.admit_reference_persistence(candidate, 'ref'))
        assert admitted.identity_id
        actions[case] = (lambda: rt.cancel_float64_persistence(admitted.identity_id)) if physical else (
            lambda: rt.cancel_reference_persistence(admitted.identity_id))
    if case in ('advance-search', 'cancel-search'):
        search = rt.start_reference_search('native')
        assert search.search_id and search.status == 'UNRESOLVED'
        actions[case] = (lambda: rt.advance_reference_search(search.search_id, transitions=10)) if case == 'advance-search' else (
            lambda: rt.cancel_reference_search(search.search_id))
    return rt, actions[case]


def exhausted_prefix(cfg, prepare, role='compiler'):
    # The immutable budget declaration is itself paid payload. Find the
    # actual fixed point using new preregistered diagnostic roots; never edit
    # a running Runtime's limits or assume changing a cap has zero cost.
    for _ in range(8):
        rt, result = prepare(cfg)
        spent = rt.snapshot().resources['spent'][role]['work']
        if spent == cfg.limits.role_cumulative[role]['work']:
            return cfg, rt, result
        budgets = {key: dict(value) for key, value in cfg.limits.role_cumulative.items()}
        budgets[role]['work'] = spent
        cfg = replace(cfg, limits=replace(cfg.limits, role_cumulative=budgets))
    raise AssertionError('diagnostic budget encoding did not stabilize')


def denied_endpoints():
    rows = []
    for case in CASES:
        cfg = config(cap=4, peak=1)
        role = 'deployment' if case == 'install' else 'compiler'
        bounded, rt, action = exhausted_prefix(cfg, lambda config: setup(case, config), role)
        cap = bounded.limits.role_cumulative[role]['work']
        before = rt.snapshot()
        assert before.resources['spent'][role]['work'] == cap
        for _ in range(64):
            try:
                result = action()
                assert result.status == 'UNRESOLVED', (case, result)
            except ResourceExceeded:
                assert case in ('retire', 'cancel-reference', 'cancel-float64', 'cancel-search')
            assert rt.snapshot() == before, case
        rows.append({'endpoint': case, 'role': role, 'work_cap': cap, 'unchanged_denials': 64})
    return rows


def bounded_control_trees():
    base_cfg, _, _ = exhausted_prefix(contract(), lambda cfg: (ReferenceCompilerRuntime(cfg, zero_program(2)), None))
    bootstrap = base_cfg.limits.role_cumulative['compiler']['work']
    cases = calls = admitted = 0
    for extra in range(0, 41, 8):
        cfg = replace(base_cfg, limits=replace(base_cfg.limits, role_cumulative={
            'compiler': {'work': bootstrap+extra}, 'deployment': {'work': 10_000_000}}))
        for commands in product(('construct', 'retire'), repeat=4):
            rt = ReferenceCompilerRuntime(cfg, zero_program(2))
            for command in commands:
                before = rt.snapshot()
                if command == 'construct':
                    rt.construct_candidate(zero_program(2))
                else:
                    shadows = [state.candidate_id for state in before.candidates if state.candidate_id != before.deployed_id]
                    if shadows:
                        try:
                            rt.retire_candidate(shadows[-1])
                        except ResourceExceeded:
                            pass
                after = rt.snapshot()
                if after != before:
                    assert after.resources['spent']['compiler']['work'] > before.resources['spent']['compiler']['work']
                    new_events = after.resources['events'][len(before.resources['events']):]
                    assert new_events[0][1] == 'work' and new_events[0][-1].startswith('control-admission:')
                    admitted += 1
                else:
                    assert after.next_candidate == before.next_candidate and after.revision == before.revision
                assert after.resources['spent']['compiler']['work'] <= bootstrap+extra
                calls += 1
            cases += 1
    return {'complete_four_command_trees': cases, 'endpoint_positions': calls,
            'funded_state_changing_requests': admitted,
            'every_changed_prefix_starts_with_positive_paid_admission': True}


def current_proof_after_denial():
    def completed(cfg):
        rt, _ = search_fixture(cfg=cfg, bounds=SMALL)
        result = rt.start_reference_search('native')
        result = rt.advance_reference_search(result.search_id, transitions=1000)
        assert result.status == 'REFERENCE_CLASS_EXHAUSTED'
        return rt, result
    _, rt, result = exhausted_prefix(contract(cap=4, peak=1), completed)
    proof = rt.reference_class_proof(result.proof_id, decision_class_id=result.decision_class_id)
    before = rt.snapshot()
    for _ in range(16):
        assert rt.construct_candidate(zero_program(2)).status == 'UNRESOLVED'
        assert rt.verify_reference_class_proof(proof, decision_class_id=result.decision_class_id) == proof
        assert rt.snapshot() == before
    return {'complete_program_class': result.programs_compared, 'unadmitted_requests': 16,
            'same_owned_current_proof_remains_valid_without_revision_change': True}


def historical_ingress_witness():
    # Execute the real pre-wire Runtime, machine and data registration. Do not
    # rebuild a second implementation of the failing assignment ordering.
    commit = '5055f3e'
    modules = historical_modules(commit, ('fp_reference.data_usage', 'fp_reference.machine', 'fp_reference.runtime'))
    old, data = modules['fp_reference.runtime'], modules['fp_reference.data_usage']
    rows = []
    for exponent in (256, 1024, 4096):
        current_cfg = replace(contract(source_domain=False), reference_integer_bits=128)
        cfg = old.ConstructionContract(**{field.name: getattr(current_cfg, field.name) for field in fields(current_cfg)})
        stream = data.StreamSpec('ordinary', 'online', ('observation-0', 'observation-1'))
        reads = tuple(data.SourceRead(s.source_id, 'input', i, 0) for i, s in enumerate(cfg.semantics.sources))
        registered = data.DataContract((stream,), 'ordinary', tuple(s.upper for s in cfg.semantics.sources), reads)
        run = old.OnlineContract(registered, online(current_cfg, 2, unit=2, grid=16).learner)
        rt = old.ReferenceCompilerRuntime(cfg, zero_program(2), online=run)
        before = rt.snapshot()
        result = rt.predict_next('observation-0', (F(1, 1 << exponent), F(0)))
        after = rt.snapshot()
        assert result.status == 'UNRESOLVED' and after.event_phase == 'halted'
        assert after.pending.record.inputs[0].denominator.bit_length() == exponent+1
        assert after.resources['current'] == before.resources['current']
        assert after.resources['spent'] == before.resources['spent']
        rows.append(exponent+1)
    return {'status': 'HISTORICAL_COUNTEREXAMPLE', 'source_commit': commit, 'reference_integer_limit': 128,
            'retained_input_denominator_bits': rows, 'halted_unresolved_without_payload_or_work_debit': True,
            'implication': 'finite admitted request count alone cannot bound raw ingress/diagnostic storage',
            'current_correction': 'mandatory paid bounded byte ingress; see audit_context_ingress.py; full host accounting still open'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--section', choices=('history', 'endpoints', 'trees', 'authority', 'ingress'))
    args = parser.parse_args()
    sections = {'history': history_witness, 'endpoints': denied_endpoints, 'trees': bounded_control_trees,
                'authority': current_proof_after_denial, 'ingress': historical_ingress_witness}
    if args.section:
        print(json.dumps(sections[args.section](), indent=2))
        return
    result = {'status': 'PASS', 'scope': 'paid Compiler control admission; no complete host/device memory claim',
              **{key: fn() for key, fn in sections.items()}}
    if args.write:
        (ROOT/'evidence/minimal/FP_CONTROL_ADMISSION_AUDIT.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
