"""Registered owned RTX 3090 audit of the likelihood-coordinate lowering.

Successful runs and deliberately refused continuations have separate outcomes.
The parent binds every report to a completed enforced Windows job and source.
"""
from dataclasses import asdict, replace
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import os
import subprocess
import sys
import tempfile
import traceback

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts'), str(Path(__file__).resolve().parent)]
import simplex_gradient as exact
from simplex_reversal import TAPE, configuration
from audit_simplex_learner import fixture
from audit_likelihood_encoding import audit_snapshot, exact_audit
from audit_reference_construction import limits, validate_residency
from audit_float64_runtime import replay
from audit_cuda_runtime import cuda_contract, SINGLE
from ingress_audit_support import deliver_context
from fp_reference import CudaCompilerPolicy, ReferenceCompilerRuntime
from fp_reference import cuda_prefix, cuda_learner
from fp_reference.core import ContractError
from fp_reference.cuda_installation import CudaInstallContract
from fp_reference.data_usage import StreamSpec, StochasticStreamLaw
from fp_reference.host_resources import HostResourceContract
from fp_reference.likelihood_encoding import LikelihoodEncodingContract, preparation_work
from fp_reference.native_search import GrammarCursor, GrammarLimits
from fp_reference.persistence import REFERENCE_PATH, FLOAT64_PATH, CUDA_PATH
from fp_reference.policy import CudaCompilationStep
from fp_reference.profile import ProfileSpec
from fp_reference.program import Program, Sum
from fp_reference.relation_proposal import RelationSourceSpec
from fp_reference.search import ReferenceSearchSpec, likelihood
from fp_reference.simplex_relation_proposal import SOLVER

CAP, TIMEOUT = 4 << 30, 180_000
CASES = ('reversal', 'profile-install', 'counter-overflow', 'coordinate-corruption',
         'descriptor-corruption', 'work-prepayment', 'scratch-prepayment', 'domain-substitution', 'bounded-class')
OUTPUT = ROOT/'evidence/minimal/FP_LIKELIHOOD_LOWERING_AUDIT.json'
DEPENDENCIES = ('src/reference_compiler', 'scripts',
    'experiments/joint_uncertainty/simplex_gradient.py', 'experiments/joint_uncertainty/predictive_counts.py',
    'experiments/joint_uncertainty/simplex_reversal.py', 'experiments/joint_uncertainty/likelihood_lowering.py',
    'experiments/joint_uncertainty/likelihood_information.py', 'theory/proofs/LIKELIHOOD_RUNTIME_CONTRACT.md')


def host_record(observed):
    return {key: getattr(observed, key) for key in ('process_id', 'creation_100ns',
        'lifetime_process_commit_peak', 'job_commit_peak', 'process_user_100ns',
        'process_kernel_100ns', 'job_user_100ns', 'job_kernel_100ns')}


def setup(case):
    cfg, graph, online = configuration()
    tape, n = TAPE, 2
    cuda = cuda_contract(state_atol=F(1, 100), probability_atol=F(1, 1000),
        phase_output_cells=4096, phase_evidence_bytes=262144,
        likelihood_encoding=LikelihoodEncodingContract(counter_bits=6 if case == 'counter-overflow' else 64))
    policy = CudaCompilerPolicy(())
    if case == 'profile-install':
        from audit_paired_cpu_persistence import registration
        n = 3
        cfg, graph, online, tape = fixture(n)
        tape = tape[:2]+((0, 1, 0),)*40+tape[2:]
        ids = tuple(f'likelihood-{i}' for i in range(len(tape)))
        data = replace(online.data, streams=(StreamSpec('online', 'online', ids),),
            stream_law=StochasticStreamLaw('external branch-invariant stochastic relation producer; audit tape alone proves no probability law'))
        profile = ProfileSpec('warm', ids[:2], 2)
        bounds = GrammarLimits(**{key: graph.counts()[key] for key in cfg.graph_limits})
        source = RelationSourceSpec(tuple((f'x0:{j}', f'x1:{j}') for j in range(n)), solver=SOLVER)
        search = ReferenceSearchSpec('native', bounds, ids[:2], profile.profile_id, relation_sources=source)
        persistence = registration(bound=F(6), horizon=40)
        persistence = replace(persistence, rules=tuple(replace(rule, rule_id='cuda', score_path=CUDA_PATH)
            if rule.score_path == FLOAT64_PATH else rule for rule in persistence.rules))
        online = replace(online, data=data, profiles=(profile,), searches=(search,), persistence=persistence)
        cuda = replace(cuda, install=CudaInstallContract())
        policy = CudaCompilerPolicy((CudaCompilationStep(2, 'native', 1, 'ref', 'cuda'),))
    host = HostResourceContract(CAP, {'deployment': CAP, 'compiler': CAP})
    return cfg, graph, online, tape, n, cuda, policy, host


def guard_case(case):
    cfg, graph, online, _, _, cuda, policy, host = setup(case)
    prepare = cuda_prefix.prepare_model
    calls = []
    def checked_prepare(*args, **kwargs):
        calls.append(True)
        if case == 'domain-substitution':
            args = args[:4]+(args[4][:1],)+args[5:]
        return prepare(*args, **kwargs)
    if case == 'work-prepayment':
        cfg = replace(cfg, limits=limits(byte_cap=512 << 20, work_cap=preparation_work(
            graph, cfg.semantics, online.learner, cfg.source_domain, cfg.reference_integer_bits)-1))
    elif case == 'scratch-prepayment':
        cfg = replace(cfg, limits=limits(byte_cap=1 << 20, work_cap=10**11))
    rt = ReferenceCompilerRuntime.__new__(ReferenceCompilerRuntime)
    error = None
    with patch.object(cuda_prefix, 'prepare_model', checked_prepare):
        try:
            rt.__init__(cfg, graph, online=online, cuda=cuda, policy=policy, host=host)
        except (ContractError, RuntimeError) as exc:
            error = f'{type(exc).__name__}: {exc}'
    assert error is not None and not rt._candidates and not rt._deployed_id
    assert not rt._install_receipts and not rt._observations and rt._run_closure is None
    if case == 'domain-substitution':
        assert calls == [True] and 'registered CUDA execution violated' in error
        phase, = rt._cuda.phases.values()
        assert phase.status == 'EXECUTION_FAILED' and 'complete source domain' in phase.reason
        assert phase.raw_state is None and phase.raw_operations == () and phase.arena_phase is None
        assert rt._attempts[-1][1] == 'EXECUTION_FAILED'
    else:
        assert not calls and not rt._cuda.phases and rt._attempts[-1][1] == 'UNRESOLVED'
        assert ('work' if case == 'work-prepayment' else 'reference_payload_bytes') in error
    assert not any('likelihood-scratch' in key for key in rt._buffers)
    return {'case': case, 'status': 'EXPECTED_REFUSAL', 'prepare_calls': len(calls),
        'attempt_status': rt._attempts[-1][1], 'reason': rt._attempts[-1][2],
        'seal': False, 'install': False, 'retained_observations': 0,
        'process_id': os.getpid(), 'host': host_record(rt._host.observe())}


def class_case():
    from audit_reference_search import brute_grammar, finish
    cfg, graph, online, _, _, cuda, _, host = setup('bounded-class')
    bounds = GrammarLimits(1, 1, 0, 0, 3)
    search = ReferenceSearchSpec('tiny', bounds, online.data.active.observation_ids[:1])
    online = replace(online, profiles=(), searches=(search,))
    zero = Program((Sum('mass', ()),), graph.slot_count, (0, 0))
    rt = ReferenceCompilerRuntime(cfg, zero, online=online, cuda=cuda, host=host)
    assert deliver_context(rt, online.data.active.observation_ids[0],
        tuple(exact.context(2, 0, 1).values())).status == 'PREDICTED_REFERENCE'
    assert rt.observe(0).status == 'OBSERVED_REFERENCE'
    result = finish(rt, rt.start_reference_search('tiny'))
    snapshot = validate_residency(rt)
    session, = snapshot.searches
    expected = set(brute_grammar(cfg.semantics, bounds))
    assert session.cursor.done and {row.program for row in session.rows} == expected
    assert len(expected) == len(session.rows) == 20 and session.unresolved == 15
    assert result.status == 'UNRESOLVED' and result.programs_compared == 5
    assert not result.proof_id and not snapshot.reference_proofs and not snapshot.install_receipts
    assert all((row.status == 'COMPARED_REFERENCE') == (row.program.slot_count == 3) for row in session.rows)
    device = audit_snapshot(rt)
    f64, *_ = replay(rt)
    snapshot = validate_residency(rt)
    return {'case': 'bounded-class', 'status': result.status, 'class_members': 20,
        'compared': 5, 'unresolved_members': 15, 'grammar_complete': True,
        'class_certificate': False, 'seal': False, 'install': False,
        'decision_class': 'registered <=1-node, <=1-SUM, no edges/PRODUCT, <=3-slot initializer endpoints plus actual deployed baseline; full U and source domain',
        'independent_binary64_phases': f64, 'CUDA': device,
        'process_id': os.getpid(), 'host': host_record(snapshot.host_resources)}


def owned(case):
    if case == 'bounded-class':
        return class_case()
    if case in ('work-prepayment', 'scratch-prepayment', 'domain-substitution'):
        return guard_case(case)
    cfg, graph, online, tape, n, cuda, policy, host = setup(case)
    profiles = case == 'profile-install'
    zero = Program((Sum('mass', ()),), graph.slot_count, (0, 0))
    rt = ReferenceCompilerRuntime(cfg, zero if profiles else graph, online=online,
                                 cuda=cuda, policy=policy, host=host)
    base_id = rt.snapshot().deployed_id
    candidate_id, scores, checkpoints, pre_attack_models = None, {}, [], []
    failure = None
    for cursor, (i, j, y) in enumerate(tape):
        if case in ('coordinate-corruption', 'descriptor-corruption') and cursor == 50:
            physical = rt._cuda._values[rt._cuda.current[base_id]]
            before = cuda_learner.raw_state(physical)
            assert before[0] == (1065353216, 1065353216, 0)
            if case == 'coordinate-corruption':
                object.__setattr__(physical, 'encoding', replace(physical.encoding, coordinates=(-49,)))
            else:
                pre_attack_models.append((graph.program_id, replace(physical.encoding.model)))
                object.__setattr__(physical.encoding.model, 'reference_increment', (0, 1))
            assert cuda_learner.raw_state(physical)[:6] == before[:6]
            assert cuda_learner.raw_state(physical)[6] != before[6]
        obs = online.data.active.observation_ids[cursor]
        try:
            event = deliver_context(rt, obs, tuple(exact.context(n, i, j).values()))
        except RuntimeError as exc:
            assert case in ('coordinate-corruption', 'descriptor-corruption') and cursor == 50
            assert isinstance(exc.__cause__, ContractError)
            assert str(exc.__cause__) == 'private CUDA predecessor changed after its owned phase'
            event = None
        snapshot = rt.snapshot()
        if event is None or event.status != 'PREDICTED_REFERENCE':
            assert case in ('coordinate-corruption', 'descriptor-corruption') and cursor == 50, event
            assert snapshot.pending.record.target is None and len(snapshot.observations) == 50
            failure = 'private CUDA predecessor changed after its owned phase'
            break
        assert snapshot.pending.record.target is None
        if candidate_id is not None:
            predictions = dict(event.predictions)
            scores[obs, REFERENCE_PATH] = tuple(predictions[key][y] for key in (base_id, candidate_id))
            values = []
            for key in (base_id, candidate_id):
                phase = next(p for p in reversed(snapshot.cuda.phases)
                    if p.raw_prediction is not None and p.observation_id == obs and p.candidate_id == key)
                masses = tuple(SINGLE.decode(w) for w in phase.raw_prediction[3])
                values.append(masses[y]/sum(masses))
            scores[obs, CUDA_PATH] = tuple(values)
        result = rt.observe(y)
        snapshot = rt.snapshot()
        if result.status != 'OBSERVED_REFERENCE':
            assert case == 'counter-overflow' and cursor == 31, result
            failure = 'registered likelihood counter precision exhausted'
            assert snapshot.cursor == 31 and len(snapshot.observations) == 32
            before = snapshot.cuda.phases[-2]
            assert before.phase.endswith(':observe') and before.raw_state[3:6] == (1, 32, 31)
            assert before.raw_state[6][2:] == ((-31,), 2) and any(before.raw_state[2])
            assert snapshot.cuda.phases[-1].raw_state == before.raw_state
            break
        if profiles and cursor+1 == 2:
            session, = snapshot.searches
            assert session.status == 'UNRESOLVED' and session.cursor == GrammarCursor() and not session.proof_id
            assert len(session.rows) == 1 and session.rows[0].status == 'COMPARED_REFERENCE'
            assert session.relation_proposal.program == graph
            candidate_id = session.best_candidate_id
            candidate = next(c for c in snapshot.candidates if c.candidate_id == candidate_id)
            assert candidate.profile_id == 'warm' and candidate.birth_cursor == 2
            assert candidate.learner == snapshot.profiles[0].attached
            assert candidate.learner.cursor == 2 and candidate.learner.optimizer_steps == 4
            assert session.best_likelihood == likelihood(graph, cfg.semantics, candidate.learner,
                snapshot.observations, bit_limit=cfg.reference_integer_bits)
            assert len(snapshot.persistence_identities) == 2
            assert all(p.start_cursor == 2 and p.wealth == 1 for p in snapshot.persistence_identities)
        if not profiles and cursor+1 in (31, 48, 50, 53, 60, 97, 100):
            current = dict(snapshot.cuda.current)[base_id]
            phase = next(p for p in snapshot.cuda.phases if p.object_id == current)
            checkpoints.append({'events': cursor+1, 'theta_words': phase.raw_state[0],
                                'coordinates': phase.raw_state[6][2]})
    snapshot = validate_residency(rt)
    assert not snapshot.reference_proofs
    if failure is None:
        assert snapshot.halted is None and snapshot.run.status == 'SEALED_CUDA_STREAM'
        assert len(snapshot.observations) == len(tape)
    else:
        assert snapshot.halted is not None and snapshot.run.status != 'SEALED_CUDA_STREAM'
        assert not snapshot.install_receipts
    if case == 'reversal':
        assert snapshot.candidates[0].theta == (F(1), F(1, 2), F(1, 2))
        by_event = {row['events']: row for row in checkpoints}
        assert by_event[48]['theta_words'][2] == by_event[50]['theta_words'][2] == 0
        assert by_event[53]['theta_words'][2] == 1
        assert by_event[100]['theta_words'] == (1065353216, 1056964608, 1056964608)
    if profiles:
        from audit_reference_persistence import check_gain, wealth_oracle
        assert len(snapshot.install_receipts) == 1 and snapshot.deployed_id == candidate_id
        assert all(d.decision_status == 'UNRESOLVED' and d.proof is None for d in snapshot.run.closure.decisions)
        identities = {p.identity_id: p for p in snapshot.persistence_identities}
        wealth, crossings = {key: F(1) for key in identities}, {}
        for event in snapshot.persistence_events:
            rule = identities[event.identity_id].rule
            assert event.cursor >= 2 and event.epoch_finished and event.wealth_before == wealth[event.identity_id]
            assert (event.base_probability, event.candidate_probability) == scores[event.observation_id, rule.score_path]
            check_gain(event)
            assert event.wealth_after == wealth_oracle(event.wealth_before, event.gain.lower, 1, rule)
            wealth[event.identity_id] = event.wealth_after
            if event.wealth_after*rule.alpha >= 1:
                crossings.setdefault(event.identity_id, event.cursor+1)
        assert len(crossings) == 2 and all(crossings[p.identity_id] == p.crossing_cursor for p in identities.values())
        receipt, = snapshot.install_receipts
        assert receipt.attempt.cursor == max(crossings.values()) == 22
        assert snapshot.alpha_spent == F(1, 2)
        phases = {p.object_id: p for p in snapshot.cuda.phases}
        for key, phase_id, raw, leases in receipt.cuda_transport.current:
            assert raw == phases[phase_id].raw_state and len(raw) == 7 and raw[6][3] is None and leases
        assert {row[0] for row in receipt.cuda_transport.current} == {base_id, candidate_id}
    device = audit_snapshot(rt, expected_failure=failure, pre_attack_models=pre_attack_models)
    f64, *_ = replay(rt)
    snapshot = validate_residency(rt)
    maxima = lambda traces: {key: str(max((getattr(p.relation, key) for p in traces if p.relation is not None), default=F(0)))
        for key in ('state_error', 'native_error', 'normalizer_error', 'probability_error', 'division_error')}
    return {'case': case, 'status': snapshot.run.status, 'expected_refusal': failure,
        'observed_cursor': snapshot.cursor, 'retained_observations': len(snapshot.observations),
        'profile_events': len(snapshot.profile_events), 'checkpoints': checkpoints,
        'independent_binary64_phases': f64, 'CUDA': device,
        'fresh_score_checks': len(snapshot.persistence_events),
        'install_cursor': snapshot.install_receipts[0].attempt.cursor if profiles else None,
        'class_certificate': False, 'historical_class': 'UNRESOLVED' if profiles else None,
        'binary64_maxima': maxima(snapshot.float64_traces), 'CUDA_maxima': maxima(snapshot.cuda.phases),
        'packed_peak': snapshot.resources['peak']['reference_payload_bytes'],
        'device': {'identity': asdict(snapshot.cuda.device.identity), 'execution_identity': snapshot.cuda.contract.execution_identity,
                   'physical_vram_upper': snapshot.cuda.device.physical_vram_upper, 'scope': snapshot.cuda.device.scope},
        'process_id': os.getpid(), 'host': host_record(snapshot.host_resources)}


def bounded_case(case):
    from windows_job_audit_support import run_in_job
    temporary = Path(tempfile.mkdtemp(prefix='fp-likelihood-audit-', dir=ROOT))
    assert temporary.resolve().parent == ROOT.resolve()
    output = temporary/'result.json'
    job = run_in_job(__file__, ('--worker', case, '--output', str(output)), commit_limit=CAP, timeout_ms=TIMEOUT)
    row = {'worker_status': 'FAILED', 'completed_job': asdict(job)}
    if output.exists():
        with output.open('rb') as stream:
            payload = stream.read(65537)
        assert len(payload) <= 65536
        row['result'] = json.loads(payload)
    if job.exit_code == 0 and not job.timed_out and job.attached_before_resume and not job.limit_terminated_processes:
        result, observed = row['result'], row['result']['host']
        assert result['process_id'] == job.process_id
        assert (observed['process_id'], observed['creation_100ns']) == (job.process_id, job.process_creation_100ns)
        assert observed['lifetime_process_commit_peak'] <= job.peak_process_commit <= CAP
        assert observed['job_commit_peak'] <= job.peak_job_commit <= CAP
        for clock in ('user', 'kernel'):
            assert max(observed[f'process_{clock}_100ns'], observed[f'job_{clock}_100ns']) <= getattr(job, f'{clock}_100ns')
        row['worker_status'] = 'EXECUTED'
    if output.exists():
        output.unlink()
    temporary.rmdir()
    return row


def preflight():
    cuda = setup('reversal')[5]
    return {'cases': CASES, 'backend': cuda.backend_id, 'exact_audit': exact_audit(),
        'unit': 1, 'rate': '1', 'radix': '9', 'counter_bits': 64, 'overflow_case_bits': 6,
        'ordinary_reversal': '50 copies of (0,1,label0), then 50 copies of (0,1,label1)',
        'profile_install': 'n3; exact registered two-pass warm profile at cursor2; 46 ordinary events; both fresh paths',
        'corruption_cut': 50, 'host_cap': CAP, 'timeout_ms': TIMEOUT,
        'packed_cap': 512 << 20, 'work_per_role': 10**11, 'reference_integer_bits': 32768,
        'native_caps': '16', 'binary64_tolerances': '1/1000000000',
        'AMP_state_native_normalizer_tolerance': '1/100', 'AMP_probability_tolerance': '1/1000',
        'arena_bytes': 16 << 20, 'allocator_bytes': 32 << 20, 'output_cells': 4096, 'phase_frame_bytes': 262144,
        'execution_identity': cuda.execution_identity,
        'scope': 'finite owned numerical-lowering audit; no class completeness, model superiority, GPU exclusivity or timing claim'}


def matrix(write=False, resume=False):
    def git(*args):
        return subprocess.run(('git', *args), cwd=ROOT, capture_output=True, encoding='utf-8', check=True).stdout.strip()
    source = git('rev-parse', 'HEAD')
    def source_clean():
        assert git('rev-parse', 'HEAD') == source
        assert not git('status', '--porcelain', '--', *DEPENDENCIES), 'commit complete execution dependencies first'
    source_clean()
    registration = json.loads(json.dumps(preflight()))
    if resume:
        report = json.loads(OUTPUT.read_text(encoding='utf-8'))
        assert report['status'] == 'PARTIAL_EXECUTION' and report['registration_source'] == source
        assert report['registration'] == registration
        assert [r['case_index'] for r in report['workers']] == list(range(len(report['workers'])))
    else:
        assert not write or not OUTPUT.exists(), 'retain earlier evidence; no silent rerun'
        report = {'status': 'PARTIAL_EXECUTION', 'registration_source': source, 'registration': registration, 'workers': []}
    def publish():
        if write:
            temporary = OUTPUT.with_suffix('.tmp')
            temporary.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
            temporary.replace(OUTPUT)
    publish()
    for index in range(len(report['workers']), len(CASES)):
        source_clean()
        row = bounded_case(CASES[index])
        row.update(case_index=index, case=CASES[index], execution_source=source)
        report['workers'].append(row)
        source_clean()
        publish()
        print(json.dumps({'case': CASES[index], 'worker_status': row['worker_status']}), flush=True)
    report['status'] = 'COMPLETE_EXECUTION' if all(r['worker_status'] == 'EXECUTED' for r in report['workers']) else 'COMPLETE_WITH_FAILURES'
    publish()
    return {'status': report['status'], 'workers': len(report['workers']),
            'executed': sum(r['worker_status'] == 'EXECUTED' for r in report['workers'])}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', choices=CASES, default='reversal')
    parser.add_argument('--worker', choices=CASES)
    parser.add_argument('--output')
    parser.add_argument('--preflight', action='store_true')
    parser.add_argument('--matrix', action='store_true')
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args()
    assert bool(args.worker) == bool(args.output)
    assert not args.resume or args.matrix and args.write
    assert not args.write or args.matrix
    assert not args.worker or not (args.matrix or args.preflight)
    if args.worker:
        try:
            result = owned(args.worker)
        except Exception:
            Path(args.output).write_text(json.dumps({'traceback': traceback.format_exc(), 'process_id': os.getpid()}), encoding='utf-8')
            raise
        Path(args.output).write_text(json.dumps(result), encoding='utf-8')
    else:
        print(json.dumps(matrix(args.write, args.resume) if args.matrix else preflight() if args.preflight
                         else bounded_case(args.case), indent=2))
