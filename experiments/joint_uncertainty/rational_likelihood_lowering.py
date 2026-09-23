"""Source-bound owned rational likelihood gate, in enforced Windows CUDA jobs.

The mixed-rate profile/install case uses the existing native constructor and
paired fresh evidence. It makes no class-optimality or model-superiority claim.
"""
from contextlib import nullcontext
from dataclasses import asdict, replace
from fractions import Fraction as F
from itertools import product
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
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts'), str(Path(__file__).parent)]
from fp_reference import CudaCompilerPolicy, ReferenceCompilerRuntime
from fp_reference import cuda_prefix, cuda_learner, likelihood_encoding as encoding
from fp_reference.core import ContractError
from fp_reference.cuda_installation import CudaInstallContract
from fp_reference.data_usage import DataContract, SourceRead, StreamSpec, StochasticStreamLaw
from fp_reference.float64_bridge import Float64Contract
from fp_reference.host_resources import HostResourceContract
from fp_reference.persistence import REFERENCE_PATH, CUDA_PATH
from fp_reference.profile import ProfileSpec
from fp_reference.program import Program, Sum
from fp_reference.runtime import OnlineContract
from audit_cuda_runtime import cuda_contract, SINGLE, phase_payload
from audit_float64_runtime import replay
from audit_likelihood_encoding import audit_snapshot, reverse_bank
from audit_reference_construction import contract, limits, validate_residency
from audit_reference_persistence import check_gain, wealth_oracle
from audit_cuda_persistence import registration
from ingress_audit_support import deliver_context
from audit_rational_likelihood import BUDGET
from likelihood_lowering import host_record
import likelihood_lowering as legacy
import likelihood_information as finite
import noise_acquisition as noise

CAP, TIMEOUT = 4 << 30, 360_000
CASES = ('rational-reversal', 'noise-n3', 'mixed-profile-install', 'counter-overflow',
         'coordinate-corruption', 'descriptor-corruption', 'prepare-work', 'prepare-scratch',
         'domain-substitution', 'decode-work', 'decode-scratch-fault', 'bounded-class', 'legacy-control')
OUTPUT = ROOT/'evidence/minimal/FP_RATIONAL_LIKELIHOOD_CUDA_A1.json'
FOLLOWUP_CASES = ('mixed-profile-install-a2',)
FOLLOWUP_OUTPUT = ROOT/'evidence/minimal/FP_RATIONAL_LIKELIHOOD_CUDA_A2.json'
DEPENDENCIES = ('src/reference_compiler', 'scripts', 'experiments/joint_uncertainty/likelihood_information.py',
    'experiments/joint_uncertainty/noise_acquisition.py', 'experiments/joint_uncertainty/likelihood_lowering.py',
    'experiments/joint_uncertainty/rational_likelihood_lowering.py',
    'experiments/joint_uncertainty/simplex_gradient.py', 'experiments/joint_uncertainty/simplex_reversal.py',
    'experiments/joint_uncertainty/predictive_counts.py', 'theory/proofs/RATIONAL_LIKELIHOOD_RUNTIME.md')


def setup(case):
    followup = case == 'mixed-profile-install-a2'
    if followup:
        case = 'mixed-profile-install'
    profile = case == 'mixed-profile-install'
    if case in ('noise-n3', 'mixed-profile-install'):
        n = 3 if case == 'noise-n3' else 2
        bank, rules, graph, spec, scale = noise.native_contract(n)
        domain = tuple(noise.source_point(n, p) for p in product(range(n), repeat=2))
        triplets = ((0, 1, 0), (1, 2, 1), (0, 2, 1), (0, 0, 0), (0, 0, 1), (1, 1, 0),
                    (0, 2, 0), (0, 1, 1), (1, 2, 0), (2, 2, 1), (0, 1, 0), (1, 2, 1)) if n == 3 else (
                    ((0, 1, 0),)*44+((0, 0, 1), (1, 0, 1), (0, 1, 0), (1, 1, 0)))
        tape = tuple((i*n+j, y) for i, j, y in triplets)
    elif case == 'legacy-control':
        from audit_simplex_learner import fixture
        cfg, graph, old_online, triplets = fixture(2)
        rules, spec, domain, scale = cfg.semantics, old_online.learner, cfg.source_domain, 10
        factors = reverse_bank(graph, rules, cfg.initializer_pattern, spec, domain)
        bank = finite.Model(tuple(tuple(factors[i:i+2]) for i in range(0, len(factors), 2)), cfg.initializer_pattern[1:])
        tape = tuple((2*i+j, y) for i, j, y in triplets[:3])
    else:
        bank = finite.bernoulli(((F(1, 3), F(2, 3)), (F(3, 4), F(1, 4))))
        rules, graph, spec, scale = finite.native_graph(bank)
        domain = ((F(1), F(0)), (F(0), F(1)))
        tape = ((0, 0),)*168+((1, 0),)*106
        if case in ('prepare-work', 'prepare-scratch', 'domain-substitution', 'decode-work', 'decode-scratch-fault'):
            tape = tape[:2]
    ids = tuple(f'rational-{i}' for i in range(len(tape)))
    cfg = replace(contract(source_domain=False, pattern=(F(1),)+bank.prior), semantics=rules,
        source_domain=domain, normalizer_cap=F(scale+2), activation_cap=F(scale), reference_integer_bits=32768,
        limits=limits(byte_cap=1 << 30, work_cap=10**11))
    data = DataContract((StreamSpec('online', 'online', ids),), 'online', (F(1),)*len(rules.sources),
        tuple(SourceRead(s.source_id, 'input', i, 0) for i, s in enumerate(rules.sources)))
    online = OnlineContract(data, spec, float64=Float64Contract(F(1, 10**8), F(1, 10**8)))
    budget = replace(BUDGET, counter_bits=6) if case == 'counter-overflow' else (
             replace(BUDGET, decode_work=1) if case == 'decode-work' else BUDGET)
    if case == 'legacy-control':
        budget = encoding.LikelihoodEncodingContract()
    cuda = cuda_contract(state_atol=F(1, 50) if followup else F(1, 100), probability_atol=F(1, 1000),
        phase_output_cells=8192, phase_evidence_bytes=(1 << 20) if case == 'noise-n3' else 262144,
        likelihood_encoding=budget, install=CudaInstallContract() if profile else None)
    if profile:
        data = replace(data, stream_law=StochasticStreamLaw('external branch-invariant audit producer; the selected tape proves no probability law'))
        online = replace(online, data=data, profiles=(ProfileSpec('warm', ids[:2], 2),),
                         persistence=registration(bound=F(6), horizon=40))
    host = HostResourceContract(CAP, {'deployment': CAP, 'compiler': CAP})
    return cfg, graph, online, tape, bank, cuda, host


def guard_case(case):
    cfg, graph, online, _, _, cuda, host = setup(case)
    prepare, calls = cuda_prefix.prepare_model, []
    def wrapped(*args, **kwargs):
        calls.append(True)
        if case == 'domain-substitution':
            args = args[:4]+(args[4][:1],)+args[5:]
        return prepare(*args, **kwargs)
    if case == 'prepare-work':
        cap = encoding.preparation_work(graph, cfg.semantics, online.learner, cfg.source_domain,
                                        cfg.reference_integer_bits, cuda.likelihood_encoding)-1
        cfg = replace(cfg, limits=limits(byte_cap=1 << 30, work_cap=cap))
    elif case == 'prepare-scratch':
        cfg = replace(cfg, limits=limits(byte_cap=1 << 20, work_cap=10**11))
    rt = ReferenceCompilerRuntime.__new__(ReferenceCompilerRuntime)
    error = None
    with patch.object(cuda_prefix, 'prepare_model', wrapped):
        try:
            rt.__init__(cfg, graph, online=online, cuda=cuda, host=host)
        except (ContractError, RuntimeError) as exc:
            error = str(exc)
    assert error is not None and not rt._candidates and not rt._deployed_id
    assert not rt._install_receipts and not rt._observations and rt._run_closure is None
    retained = sum(len(buf) for key, buf in rt._buffers.items() if key.endswith(':likelihood-scratch'))
    if case == 'domain-substitution':
        assert calls == [True]
        phase, = rt._cuda.phases.values()
        assert phase.status == 'EXECUTION_FAILED' and 'complete source domain' in phase.reason
        assert phase.raw_state is None and not phase.raw_operations and phase.arena_phase is None
        assert retained == encoding.preparation_workspace(graph, cfg.semantics, online.learner,
            cfg.source_domain, cfg.reference_integer_bits, cuda.likelihood_encoding)
    else:
        assert not calls and not rt._cuda.phases and not retained
        assert rt._attempts[-1][1] == 'UNRESOLVED'
    return {'case': case, 'status': 'EXPECTED_REFUSAL', 'prepare_calls': len(calls),
            'retained_failed_scratch_bytes': retained, 'reason': error, 'class_certificate': False,
            'process_id': os.getpid(), 'host': host_record(rt._host.observe())}


def class_case():
    original = legacy.setup
    def configured(case):
        cfg, graph, online, tape, n, cuda, policy, host = original(case)
        return cfg, graph, online, tape, n, replace(cuda, likelihood_encoding=BUDGET, phase_output_cells=8192), policy, host
    with patch.object(legacy, 'setup', configured):
        return legacy.class_case()


def owned(case):
    if case in ('prepare-work', 'prepare-scratch', 'domain-substitution'):
        return guard_case(case)
    if case == 'bounded-class':
        return class_case()
    cfg, graph, online, tape, bank, cuda, host = setup(case)
    profile = case in ('mixed-profile-install', 'mixed-profile-install-a2')
    root = Program((Sum('mass', ()),), graph.slot_count, (0, 0)) if profile else graph
    rt = ReferenceCompilerRuntime(cfg, root, online=online, cuda=cuda, host=host,
        policy=None if profile else CudaCompilerPolicy(()))
    base = rt.snapshot().deployed_id
    candidate, identities, install_cursor = None, None, None
    actual_history, saved, scores, checkpoints = [], [], {}, []
    failure = None
    inputs = cuda_learner.joint_inputs
    def short_scratch(*args, **kwargs):
        return inputs(*args, **(kwargs | {'workspace': kwargs['workspace'][:-1]}))
    for cursor, (query, target) in enumerate(tape):
        if cursor == 168 and case in ('coordinate-corruption', 'descriptor-corruption'):
            physical = rt._cuda._values[rt._cuda.current[base]]
            before = cuda_learner.raw_state(physical)
            assert before[0][1:] == (0, 1065353216)
            if case == 'coordinate-corruption':
                changed = (physical.encoding.coordinates[0]+1,)+physical.encoding.coordinates[1:]
                object.__setattr__(physical, 'encoding', replace(physical.encoding, coordinates=changed))
            else:
                saved.append((graph.program_id, replace(physical.encoding.model)))
                object.__setattr__(physical.encoding.model, 'factor_bases', (2, 5))
            assert cuda_learner.raw_state(physical)[:6] == before[:6]
            assert cuda_learner.raw_state(physical)[6] != before[6]
        obs = online.data.active.observation_ids[cursor]
        try:
            event = deliver_context(rt, obs, cfg.source_domain[query])
        except RuntimeError as exc:
            assert cursor == 168 and case in ('coordinate-corruption', 'descriptor-corruption'), (cursor, rt.snapshot().halted)
            assert isinstance(exc.__cause__, ContractError)
            event = None
        if event is None or event.status != 'PREDICTED_REFERENCE':
            assert cursor == 168 and case in ('coordinate-corruption', 'descriptor-corruption'), (cursor, event, rt.snapshot().halted)
            failure = 'private CUDA predecessor changed after its owned phase'
            assert rt.snapshot().pending.record.target is None
            break
        before = rt.snapshot()
        assert before.pending.record.target is None
        if candidate is not None and install_cursor is None:
            forecasts = dict(event.predictions)
            scores[obs, REFERENCE_PATH] = tuple(forecasts[key][target] for key in (base, candidate))
            finite_scores = []
            for key in (base, candidate):
                phase = next(p for p in reversed(before.cuda.phases) if p.raw_prediction is not None
                             and p.observation_id == obs and p.candidate_id == key)
                masses = tuple(SINGLE.decode(w) for w in phase.raw_prediction[3])
                finite_scores.append(masses[target]/sum(masses))
            scores[obs, CUDA_PATH] = tuple(finite_scores)
        context = patch.object(cuda_learner, 'joint_inputs', short_scratch) if case == 'decode-scratch-fault' else nullcontext()
        try:
            with context:
                result = rt.observe(target)
        except RuntimeError as exc:
            assert case == 'decode-scratch-fault' and cursor == 0 and isinstance(exc.__cause__, ContractError)
            result = None
        if result is None or result.status != 'OBSERVED_REFERENCE':
            assert case in ('counter-overflow', 'decode-work', 'decode-scratch-fault'), (cursor, result, rt.snapshot().halted)
            expected_cut = 31 if case == 'counter-overflow' else 0
            assert cursor == expected_cut
            failure = ('registered likelihood counter precision exhausted' if case == 'counter-overflow' else
                       'coprime arithmetic exhausted' if case == 'decode-work' else 'exact paid writable scratch extent')
            failed = rt.snapshot()
            observed, refused = failed.cuda.phases[-2:]
            assert observed.phase.endswith(':observe') and refused.phase.endswith(':commit')
            assert refused.raw_state == observed.raw_state and observed.raw_state[3:6] == (1, cursor+1, cursor)
            assert any(observed.raw_state[2]) and len(failed.observations) == cursor+1
            assert any(key.endswith(':likelihood-scratch') for key, _ in failed.buffers)
            break
        if not profile or candidate is not None:
            actual_history.append((query, target))
            wanted = bank.history(actual_history)
            tracked = base if candidate is None else candidate
            learner = next(c.learner for c in rt.snapshot().candidates if c.candidate_id == tracked)
            assert learner.theta[1:] == wanted
        if profile and cursor+1 == 2:
            built = rt.construct_candidate(graph, profile_id='warm')
            assert built.status == 'BUILT_REFERENCE'
            candidate = built.candidate_id
            actual_history = list(tape[:2])*2
            learner = next(c.learner for c in rt.snapshot().candidates if c.candidate_id == candidate)
            assert learner.cursor == 2 and learner.optimizer_steps == 4 and learner.theta[1:] == bank.history(actual_history)
            reference = rt.admit_reference_persistence(candidate, 'ref')
            physical = rt.admit_cuda_persistence(candidate, 'cuda')
            identities = reference.identity_id, physical.identity_id
            assert all(identities)
        if profile and identities is not None and install_cursor is None:
            paired = rt.paired_cuda_persistence_result(*identities)
            if paired.status == 'PAIRED_CUDA_CROSSED':
                installed = rt.install_cuda(candidate, reference_identity=identities[0], cuda_identity=identities[1])
                assert installed.status == 'INSTALLED_CUDA'
                install_cursor = cursor+1
        if cursor+1 in (1, 31, 149, 168, 180, 274) or cursor+1 == len(tape):
            now = rt.snapshot()
            phase_id = dict(now.cuda.current)[now.deployed_id]
            phase = next(p for p in now.cuda.phases if p.object_id == phase_id)
            checkpoints.append({'cursor': cursor+1, 'theta_words': phase.raw_state[0], 'metadata': phase.raw_state[6]})
    snapshot = validate_residency(rt)
    assert not snapshot.reference_proofs
    if failure is None:
        assert snapshot.halted is None and len(snapshot.observations) == len(tape)
        if not profile:
            assert snapshot.run.status == 'SEALED_CUDA_STREAM'
        assert not any(key.endswith(':likelihood-scratch') for key, _ in snapshot.buffers)
    else:
        assert snapshot.halted is not None and not snapshot.install_receipts
    if case == 'rational-reversal':
        by_cut = {row['cursor']: row for row in checkpoints}
        assert by_cut[168]['theta_words'][1:] == (0, 1065353216)
        assert by_cut[274]['theta_words'][1:] == (1056982124, 1056929575)
    if profile:
        assert install_cursor is not None and install_cursor < len(tape) and snapshot.deployed_id == candidate
        assert snapshot.alpha_spent == F(1, 2) and len(snapshot.install_receipts) == 1
        states = {p.identity_id: p for p in snapshot.persistence_identities}
        wealth, crossings = {key: F(1) for key in states}, {}
        for event in snapshot.persistence_events:
            rule = states[event.identity_id].rule
            assert event.cursor >= 2 and event.wealth_before == wealth[event.identity_id]
            assert (event.base_probability, event.candidate_probability) == scores[event.observation_id, rule.score_path]
            check_gain(event)
            wealth[event.identity_id] = wealth_oracle(event.wealth_before, event.gain.lower, 1, rule)
            assert event.wealth_after == wealth[event.identity_id]
            if event.wealth_after*rule.alpha >= 1:
                crossings.setdefault(event.identity_id, event.cursor+1)
        assert len(crossings) == 2 and install_cursor == max(crossings.values())
        receipt, = snapshot.install_receipts
        assert receipt.attempt.proposal_proof_id is None
        phases = {p.object_id: p for p in snapshot.cuda.phases}
        for _, phase_id, raw, leases in receipt.cuda_transport.current:
            assert raw == phases[phase_id].raw_state and raw[6][0] == encoding.RATIONAL_ENCODING_ID and leases
        assert next(c.learner for c in snapshot.candidates if c.candidate_id == candidate).optimizer_steps == len(tape)+2
    audited = audit_snapshot(rt, expected_failure=failure, pre_attack_models=saved)
    f64, *_ = replay(rt)
    snapshot = validate_residency(rt)
    maxima = {key: str(max((getattr(p.relation, key) for p in snapshot.cuda.phases if p.relation is not None), default=F(0)))
              for key in ('state_error', 'native_error', 'normalizer_error', 'probability_error')}
    return {'case': case, 'status': snapshot.run.status, 'expected_refusal': failure, 'cursor': snapshot.cursor,
            'observations': len(snapshot.observations), 'profile_events': len(snapshot.profile_events),
            'CUDA': audited, 'binary64_phases': f64, 'checkpoints': checkpoints, 'CUDA_maxima': maxima,
            'fresh_score_checks': len(snapshot.persistence_events), 'install_cursor': install_cursor,
            'class_certificate': False, 'constructor_search_performed': False,
            'retained_failed_scratch_bytes': sum(len(b) for k, b in snapshot.buffers if k.endswith(':likelihood-scratch')),
            'packed_peak': snapshot.resources['peak']['reference_payload_bytes'],
            'process_id': os.getpid(), 'host': host_record(snapshot.host_resources)}


def bounded_case(case):
    from windows_job_audit_support import run_in_job
    temporary = Path(tempfile.mkdtemp(prefix='fp-rational-audit-', dir=ROOT))
    assert temporary.resolve().parent == ROOT.resolve()
    output = temporary/'result.json'
    job = run_in_job(__file__, ('--worker', case, '--output', str(output)), commit_limit=CAP, timeout_ms=TIMEOUT)
    row = {'worker_status': 'FAILED', 'completed_job': asdict(job)}
    if output.exists():
        payload = output.read_bytes()
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


def preflight(attempt=1):
    declaration = {'cases': CASES, 'host_cap': CAP, 'timeout_ms': TIMEOUT, 'packed_cap': 1 << 30,
            'work_per_role': 10**11, 'reference_integer_bits': 32768, 'arithmetic': asdict(BUDGET),
            'backend': encoding.RATIONAL_BACKEND_ID, 'work_model': encoding.RATIONAL_WORK_ID,
            'state_atol': '1/100', 'probability_atol': '1/1000', 'binary64_atol': '1/100000000',
            'phase_output_cells': 8192, 'phase_frame_bytes': {'noise-n3': 1 << 20, 'otherwise': 262144},
            'bounded_class': 'existing <=1-node/no-edge/no-PRODUCT/<=3-slot declared class under the new representation; 20 members, 15 expected unresolved',
            'bounded_class_overrides': {'packed_cap': 512 << 20, 'binary64_atol': '1/1000000000', 'native_caps': '16'},
            'profile_install': 'two prior events replayed twice at cursor2; joint unknown-rate n2; 48 ordinary events; both fresh paths and continued learning',
            'reversal': '168 ratio2 events then106 ratio1/3 events; full native phases',
            'scope': 'owned numerical component; no model superiority, constructor completeness or full indexed release'}
    if attempt == 2:
        declaration.update(cases=FOLLOWUP_CASES, state_atol='1/50',
            previous='A1 at 5937e1b retains twelve executed cases and a failed mixed-profile-install worker; none is overwritten',
            reason='Exact passive replay proves the original 1/100 full-native tolerance fails at ordinary cursor27: normalizer error1/64. A2 changes only that tolerance and failure diagnostics, not production arithmetic, graph, U, tape, probability tolerance or resource limits.',
            numerical_preflight='FP_RATIONAL_NATIVE_PRECISION.json checks all50 candidate updates including four profile events; this is a fixed-word calculation, not an all-history native error theorem')
    else:
        assert attempt == 1
    return declaration


def matrix(write=False, resume=False, attempt=1):
    output = OUTPUT if attempt == 1 else FOLLOWUP_OUTPUT
    cases = CASES if attempt == 1 else FOLLOWUP_CASES
    def git(*args):
        return subprocess.run(('git', *args), cwd=ROOT, capture_output=True, encoding='utf-8', check=True).stdout.strip()
    source = git('rev-parse', 'HEAD')
    def clean():
        assert git('rev-parse', 'HEAD') == source
        assert not git('status', '--porcelain', '--', *DEPENDENCIES), 'commit execution dependencies before running'
    clean()
    registration = json.loads(json.dumps(preflight(attempt)))
    if resume:
        report = json.loads(output.read_text(encoding='utf-8'))
        assert report['status'] == 'PARTIAL_EXECUTION' and report['registration_source'] == source
        assert report['registration'] == registration
        assert [r['case_index'] for r in report['workers']] == list(range(len(report['workers'])))
    else:
        assert not write or not output.exists(), 'retain terminal evidence; no silent rerun'
        report = {'status': 'PARTIAL_EXECUTION', 'registration_source': source, 'registration': registration, 'workers': []}
    def publish():
        if write:
            temporary = output.with_suffix('.tmp')
            temporary.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
            temporary.replace(output)
    publish()
    for index in range(len(report['workers']), len(cases)):
        clean()
        row = bounded_case(cases[index])
        row.update(case_index=index, case=cases[index], execution_source=source)
        report['workers'].append(row)
        clean()
        publish()
        print(json.dumps({'case': cases[index], 'worker_status': row['worker_status']}), flush=True)
    report['status'] = 'COMPLETE_EXECUTION' if all(r['worker_status'] == 'EXECUTED' for r in report['workers']) else 'COMPLETE_WITH_FAILURES'
    publish()
    return {'status': report['status'], 'workers': len(report['workers'])}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--worker', choices=CASES+FOLLOWUP_CASES)
    parser.add_argument('--attempt', type=int, choices=(1, 2), default=1)
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
        assert args.matrix or args.preflight
        print(json.dumps(matrix(args.write, args.resume, args.attempt) if args.matrix else preflight(args.attempt), indent=2))
