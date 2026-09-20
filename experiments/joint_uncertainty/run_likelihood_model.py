"""Owned likelihood learning on all four retained RN-5 n8 IID cases.

The independent posterior is a passive pre-target comparator, never an input
to construction or learning. Every new bounded attempt is retained.
"""
from dataclasses import asdict, replace
from fractions import Fraction as F
from pathlib import Path
import argparse
import json
import os
import subprocess
import sys
import tempfile
import traceback

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts'), str(Path(__file__).parent)]
import simplex_gradient as native
import run_joint as previous
from joint_model import data, support, counts_from_training, unseen_pairs, score, AdaptivePosterior
from likelihood_lowering import DEPENDENCIES as LOWERING_DEPENDENCIES, host_record
from audit_simplex_learner import fixture
from audit_cuda_runtime import cuda_contract, SINGLE
from audit_likelihood_encoding import audit_snapshot
from audit_float64_runtime import replay
from audit_reference_construction import limits, validate_residency
from audit_reference_persistence import check_gain, wealth_oracle
from audit_paired_cpu_persistence import registration
from ingress_audit_support import deliver_context
from fp_reference import CudaCompilerPolicy, ReferenceCompilerRuntime
from fp_reference.cuda_installation import CudaInstallContract
from fp_reference.cuda_storage import CudaStorageContract
from fp_reference.cuda_prefix import output_cells
from fp_reference.data_usage import StreamSpec, StochasticStreamLaw
from fp_reference.host_resources import HostResourceContract
from fp_reference.likelihood_encoding import (LikelihoodEncodingContract,
    preparation_work, preparation_workspace)
from fp_reference.native_search import GrammarCursor, GrammarLimits
from fp_reference.persistence import REFERENCE_PATH, FLOAT64_PATH, CUDA_PATH
from fp_reference.policy import CudaCompilationStep
from fp_reference.profile import ProfileSpec
from fp_reference.program import Program, Sum
from fp_reference.relation_proposal import RelationSourceSpec
from fp_reference.search import ReferenceSearchSpec
from fp_reference.simplex_relation_proposal import SOLVER

CASES = ((8, 'iid-c2', 16), (8, 'iid-c2', 17), (8, 'iid-c4', 18), (8, 'iid-c4', 19))
CAP, TIMEOUT = 16 << 30, 7_200_000
PACKED, WORK, ARENA, FRAME, CELLS = 8 << 30, 10**15, 256 << 20, 4 << 20, 65536
OUTPUT = ROOT/'evidence/minimal/FP_LIKELIHOOD_MODEL_EXPERIMENT.json'
BASELINE_COMMIT = '6c202ea'
BASELINE_PATH = 'evidence/minimal/FP_JOINT_UNCERTAINTY_EXPERIMENT.json'
PRIOR_FAILURE_PATH = 'evidence/minimal/FP_LIKELIHOOD_MODEL_AUDITOR_FAILURE.json'
PROTOCOL_ORIGIN = '90f38834668546636b420f66b1a831b5969a2a13'
DEPENDENCIES = tuple(dict.fromkeys(previous.DEPENDENCIES+LOWERING_DEPENDENCIES+(
    'experiments/joint_uncertainty/run_likelihood_model.py',
    'experiments/joint_uncertainty/LIKELIHOOD_MODEL_PROTOCOL.md', BASELINE_PATH, PRIOR_FAILURE_PATH)))


def git(*args):
    return subprocess.run(('git', *args), cwd=ROOT, capture_output=True,
                          encoding='utf-8', check=True).stdout.rstrip('\r\n')


def retained_baselines():
    report = json.loads(git('show', BASELINE_COMMIT+':'+BASELINE_PATH))
    current = json.loads((ROOT/BASELINE_PATH).read_text(encoding='utf-8'))
    # A later RN-5 prefix may append completed jobs. The referenced prefix and
    # its registration must remain identical; new rows cannot change a control.
    assert current['workers'][:len(report['workers'])] == report['workers']
    assert {k:v for k,v in current.items() if k not in ('status', 'workers')} == {
        k:v for k,v in report.items() if k not in ('status', 'workers')}
    rows = [r for r in report['workers'] if r.get('kind') == 'posterior' and tuple(r['case']) in CASES]
    assert tuple(tuple(r['case']) for r in rows) == CASES
    for row in rows:
        job = row['completed_job']
        assert row['worker_status'] == 'EXECUTED' and row['rate'] == 'none'
        assert job['exit_code'] == 0 and not job['timed_out'] and job['attached_before_resume']
        assert job['limit_terminated_processes'] == 0 and job['peak_job_commit'] <= job['commit_limit']
        assert row['process_id'] == job['process_id']
        assert row['complete_domain_raw_predictions_checked'] == 64
    return rows, {'journal': BASELINE_PATH, 'journal_commit': git('rev-parse', BASELINE_COMMIT),
                  'execution_source': report['registration_source'], 'cases': CASES,
                  'scope': 'completed retained exact/AMP adaptive posterior; no new baseline execution'}


def prior_auditor_failure(registration_value):
    prior = json.loads((ROOT/PRIOR_FAILURE_PATH).read_text(encoding='utf-8'))
    assert prior['status'] == 'STOPPED_AUDITOR_FAILURE'
    assert prior['registration_source'] == PROTOCOL_ORIGIN
    row, = prior['workers']
    assert row['case_index'] == 0 and tuple(row['case']) == CASES[0]
    assert row['execution_source'] == PROTOCOL_ORIGIN and row['worker_status'] == 'FAILED'
    job = row['completed_job']
    assert job['exit_code'] == 1 and not job['timed_out'] and job['attached_before_resume']
    assert 'audit_reference_persistence.py' in row['result']['traceback']
    assert 'AssertionError' in row['result']['traceback']
    # The correction changes the independent checker, never the registered
    # model, data, baseline, budgets, tolerances, learning or evidence rule.
    assert prior['registration'] == registration_value
    return {'journal': PRIOR_FAILURE_PATH, 'execution_source': PROTOCOL_ORIGIN,
            'attempted_workers': 1, 'case': list(CASES[0]),
            'model_and_resource_registration_identical': True,
            'scope': 'original failed attempt retained; no inferred model score or complete phase count'}


def setup(case, *, gain_bound=F(6)):
    assert case in CASES
    n, cutoff = case[0], 10*len(support(case))
    cfg, graph, online, _ = fixture(n)
    grammar = GrammarLimits(**{key: 2*graph.counts()[key] for key in cfg.graph_limits})
    cfg = replace(cfg, graph_limits=asdict(grammar), limits=limits(PACKED, WORK))
    ids = tuple(f'likelihood-model-{i}' for i in range(cutoff+n*n))
    stream = replace(online.data, streams=(StreamSpec('online', 'online', ids),),
        stream_law=StochasticStreamLaw('RN-5 external branch-invariant noise premise; retained tapes are a retrospective mechanism test'))
    profile = ProfileSpec('warm', ids[:cutoff], 1)
    source = RelationSourceSpec(tuple((f'x0:{j}', f'x1:{j}') for j in range(n)), solver=SOLVER)
    search = ReferenceSearchSpec('native', grammar, ids[:cutoff], profile.profile_id, relation_sources=source)
    persistence = registration(bound=gain_bound, horizon=n*n)
    persistence = replace(persistence, rules=tuple(replace(rule, rule_id='cuda', score_path=CUDA_PATH)
        if rule.score_path == FLOAT64_PATH else rule for rule in persistence.rules))
    online = replace(online, data=stream, profiles=(profile,), searches=(search,), persistence=persistence)
    storage = CudaStorageContract(ARENA, 2*ARENA, {role: (ARENA, 2*ARENA) for role in ('deployment', 'compiler')})
    cuda = cuda_contract(storage=storage, state_atol=F(1, 100), probability_atol=F(1, 1000),
        phase_output_cells=CELLS, phase_evidence_bytes=FRAME, install=CudaInstallContract(),
        likelihood_encoding=LikelihoodEncodingContract())
    policy = CudaCompilerPolicy((CudaCompilationStep(cutoff, 'native', 1, 'ref', 'cuda'),))
    host = HostResourceContract(CAP, {'deployment': CAP, 'compiler': CAP})
    return cfg, graph, online, cuda, policy, host


def fresh_audit(snapshot, exact_scores, cuda_scores, base, candidate, *, detailed=False):
    identities = {p.identity_id: p for p in snapshot.persistence_identities}
    wealth, crossings = {key: F(1) for key in identities}, {}
    for event in snapshot.persistence_events:
        identity = identities[event.identity_id]
        rule = identity.rule
        expected = exact_scores if rule.score_path == REFERENCE_PATH else cuda_scores
        assert rule.score_path in (REFERENCE_PATH, CUDA_PATH)
        assert event.cursor >= identity.start_cursor and event.epoch_finished
        assert event.wealth_before == wealth[event.identity_id]
        assert event.identity_id not in crossings, 'a numerically crossed path cannot score another event'
        assert (event.base_probability, event.candidate_probability) == expected[event.observation_id]
        check_gain(event)
        assert event.wealth_after == wealth_oracle(event.wealth_before, event.gain.lower, 1, rule)
        wealth[event.identity_id] = event.wealth_after
        if event.wealth_after*rule.alpha >= 1:
            crossings.setdefault(event.identity_id, event.cursor+1)
    for key, identity in identities.items():
        if detailed and identity.crossing_cursor is None and key in crossings:
            assert identity.status == 'UNRESOLVED', 'an unretained crossing cannot remain active'
        else:
            assert identity.crossing_cursor == crossings.get(key)
    owned_crossings = sorted(p.crossing_cursor for p in identities.values() if p.crossing_cursor is not None)
    if snapshot.install_receipts:
        receipt, = snapshot.install_receipts
        assert len(owned_crossings) == 2 and snapshot.deployed_id == candidate
        assert receipt.attempt.cursor == max(owned_crossings)
        phases = {p.object_id: p for p in snapshot.cuda.phases}
        for key, phase_id, raw, leases in receipt.cuda_transport.current:
            assert raw == phases[phase_id].raw_state and len(raw) == 7 and raw[6][3] is None and leases
        assert {row[0] for row in receipt.cuda_transport.current} == {base, candidate}
    result = {'events': len(snapshot.persistence_events), 'identities': len(identities),
              'crossings': owned_crossings, 'install_transport_checked': bool(snapshot.install_receipts)}
    if detailed:
        result['numerical_crossings'] = sorted(crossings.values())
        result['paths'] = []
        for key, identity in identities.items():
            events = tuple(e for e in snapshot.persistence_events if e.identity_id == key)
            prefix = key+':current-whole-domain-mass-ratio:'
            charges = tuple(e for e in snapshot.resources['events'] if e[1] == 'work' and e[5].startswith(prefix))
            result['paths'].append({'score_path': identity.rule.score_path, 'status': identity.status,
                'start_cursor': identity.start_cursor, 'cursor': identity.cursor,
                'bound': str(identity.rule.bound), 'bet': str(identity.rule.bet), 'alpha': str(identity.rule.alpha),
                'ratio_bound_kind': identity.ratio_bound_kind,
                'ratio_bound': None if identity.ratio_bound is None else str(identity.ratio_bound),
                'epochs_completed': identity.epochs_completed, 'epoch_events': identity.epoch_events,
                'wealth': str(identity.wealth), 'crossing_cursor': identity.crossing_cursor,
                'crossing_wealth': None if identity.crossing_wealth is None else str(identity.crossing_wealth),
                'numerical_crossing_cursor': crossings.get(key), 'reason': identity.reason,
                'score_records': [(e.cursor, str(e.wealth_after)) for e in events],
                'refinement_charge_cursors': [int(e[5][len(prefix):]) for e in charges],
                'refinement_charged_work': sum(dict(e[4])['work'] for e in charges)})
    return result


def worker(case, *, gain_bound=F(6), detailed_fresh=False):
    hidden, edges, train, evaluation = data(case)
    cfg, graph, online, cuda, policy, host = setup(case, gain_bound=gain_bound)
    zero = Program((Sum('mass', ()),), graph.slot_count, (0, 0))
    rt = ReferenceCompilerRuntime(cfg, zero, online=online, cuda=cuda, policy=policy, host=host)
    base = rt.snapshot().deployed_id
    candidate = None
    cutoff_record = None
    oracle = None
    exact_predictions, exact_scores = {}, {}
    ids = online.data.active.observation_ids
    for cursor, (i, j, label) in enumerate(train+evaluation):
        event = deliver_context(rt, ids[cursor], tuple(native.context(case[0], i, j).values()))
        if event.status != 'PREDICTED_REFERENCE':
            assert event.status == 'UNRESOLVED'
            break
        expected = None
        if cursor >= len(train):
            expected = oracle.predict(i, j)
            predictions = dict(event.predictions)
            if candidate is not None:
                assert predictions[candidate] == expected, 'native candidate differs from the same-cut exact posterior'
                exact_scores[ids[cursor]] = (predictions[base][label], predictions[candidate][label])
            exact_predictions[i, j] = expected
        observed = rt.observe(label)
        if expected is not None:
            oracle.observe(label)
        if observed.status != 'OBSERVED_REFERENCE':
            assert observed.status == 'UNRESOLVED'
            break
        if cursor+1 == len(train):
            boundary = validate_residency(rt)
            assert len(boundary.observations) == len(train)
            session, = boundary.searches
            assert session.status == 'UNRESOLVED' and session.cursor == GrammarCursor() and not session.proof_id
            compared = [row for row in session.rows if row.status == 'COMPARED_REFERENCE']
            others = [row for row in boundary.candidates if row.candidate_id != base]
            assert len(others) <= 1
            if others:
                actual, = others
                candidate = actual.candidate_id
                assert session.relation_proposal.program == graph and len(compared) == 1
                assert actual.profile_id == 'warm' and actual.birth_cursor == len(train)
                assert actual.learner == boundary.profiles[0].attached
                assert actual.learner.cursor == actual.learner.optimizer_steps == len(train)
            cutoff_record = {'search_status': session.status, 'compared_members': len(compared),
                'proposal_status': None if session.relation_proposal is None else session.relation_proposal.status,
                'candidate_created': candidate is not None,
                'candidate_selected': candidate is not None and session.best_candidate_id == candidate}
            oracle = AdaptivePosterior(case[0], counts_from_training(case[0], train), case[1])
            del boundary
    snapshot = validate_residency(rt)
    complete = snapshot.halted is None and snapshot.run.status == 'SEALED_CUDA_STREAM'
    assert complete or snapshot.run.status == 'HALTED_UNRESOLVED'
    assert not snapshot.reference_proofs
    assert snapshot.run.closure is None or all(d.decision_status == 'UNRESOLVED' and d.proof is None
                                              for d in snapshot.run.closure.decisions)
    phase_checked = (all(p.status == 'CHECKED_CUDA_PREFIX_PHASE' for p in snapshot.cuda.phases)
                     and all(p.status == 'CHECKED_FLOAT64_PHASE' for p in snapshot.float64_traces))
    if complete:
        assert phase_checked and snapshot.cursor == len(train)+len(evaluation)
    observations = {r.observation_id: r for r in snapshot.observations}
    for cursor, row in enumerate(snapshot.observations):
        i, j, label = (train+evaluation)[cursor]
        assert row.observation_id == ids[cursor] and row.target == label
        assert dict(row.sources) == native.context(case[0], i, j)
    pair_by_id = {ids[len(train)+k]: (i, j) for k, (i, j, _) in enumerate(evaluation)}
    mass, raw, readouts = {}, {}, []
    for phase in snapshot.cuda.phases:
        if phase.raw_prediction is None or phase.observation_id not in pair_by_id:
            continue
        key = phase.candidate_id, phase.observation_id
        assert key not in mass
        masses = tuple(SINGLE.decode(w) for w in phase.raw_prediction[3])
        mass[key] = tuple(w/sum(masses) for w in masses)
        raw[key] = tuple(SINGLE.decode(w) for w in phase.raw_prediction[5])
        readouts.append({'candidate': 'posterior' if phase.candidate_id == candidate else 'baseline',
            'cursor': phase.ordinary_cursor, 'pair': pair_by_id[phase.observation_id],
            'mass_words': phase.raw_prediction[3], 'division_words': phase.raw_prediction[5]})
    cuda_scores = {obs: tuple(mass[key, obs][observations[obs].target] for key in (base, candidate))
                   for obs in exact_scores if all((key, obs) in mass for key in (base, candidate))}
    fresh = fresh_audit(snapshot, exact_scores, cuda_scores, base, candidate, detailed=detailed_fresh) if phase_checked else None
    install = snapshot.install_receipts[0].attempt.cursor if snapshot.install_receipts else None
    measured = {}
    maximum_posterior_error = None
    if complete:
        domain = tuple((i, j) for i in range(case[0]) for j in range(case[0]))
        unseen = unseen_pairs(case[0], edges)
        assert len(exact_predictions) == 64
        for name, pairs in (('unseen', unseen), ('full_domain', domain)):
            measured['adaptive_exact_'+name] = score(exact_predictions, None, hidden, pairs)
        for name in ('candidate', 'deployed'):
            probabilities, divisions = {}, {}
            if name == 'candidate' and candidate is None:
                continue
            for index, (i, j, _) in enumerate(evaluation):
                cursor = len(train)+index
                key = candidate if name == 'candidate' or (install is not None and cursor >= install) else base
                probabilities[i, j], divisions[i, j] = mass[key, ids[cursor]], raw[key, ids[cursor]]
            for label, pairs in (('unseen', unseen), ('full_domain', domain)):
                measured[name+'_stream_'+label] = score(probabilities, divisions, hidden, pairs)
        if candidate is not None:
            maximum_posterior_error = max(abs(p-q) for obs, pair in pair_by_id.items()
                for p, q in zip(mass[candidate, obs], exact_predictions[pair]))
            assert maximum_posterior_error <= cuda.probability_atol
    # Release the passive snapshot before each independent replay. No Runtime
    # evidence is dropped; each replay obtains and validates the complete state.
    result = {'case': case, 'run_status': snapshot.run.status, 'halted': snapshot.halted,
        'cursor': snapshot.cursor, 'training_events': len(train), 'evaluation_events': len(evaluation),
        'counts': counts_from_training(case[0], train), 'cutoff': cutoff_record,
        'install_cursor': install, 'alpha_spent': str(snapshot.alpha_spent),
        'class_certificate': False, 'candidate_native': graph.counts() if candidate is not None else None,
        'reference_posterior_forecast_checks': len(exact_scores), 'fresh': fresh,
        'maximum_candidate_mass_posterior_error': None if maximum_posterior_error is None else str(maximum_posterior_error),
        'scores': measured, 'CUDA_readouts': readouts if complete else [],
        'phase_audit_status': 'ALL_EXECUTED_PHASES_CHECKED' if phase_checked else 'NUMERICAL_REFUSAL; NO_COMPLETE_REPLAY_CLAIM',
        'binary64_maxima': previous.maxima(snapshot.float64_traces),
        'CUDA_maxima': previous.maxima(snapshot.cuda.phases),
        'packed_peak': snapshot.resources['peak']['reference_payload_bytes'],
        'process_id': os.getpid(), 'host': host_record(snapshot.host_resources),
        'device': previous.rn1.device_record(snapshot.cuda.device, snapshot.cuda.contract.execution_identity)}
    del snapshot
    result['independent_CUDA'] = audit_snapshot(rt) if phase_checked else None
    result['independent_binary64_phases'] = replay(rt)[0] if phase_checked else None
    if phase_checked:
        assert result['independent_CUDA']['checked_phases'] == result['independent_binary64_phases']
    final = validate_residency(rt)
    result['host'] = host_record(final.host_resources)
    return result


def bounded(index, *, worker_script=None, directory_prefix='fp-likelihood-model-'):
    from windows_job_audit_support import run_in_job
    directory = Path(tempfile.mkdtemp(prefix=directory_prefix, dir=ROOT))
    assert directory.resolve().parent == ROOT.resolve()
    output = directory/'result.json'
    job = run_in_job(__file__ if worker_script is None else worker_script,
                     ('--worker', str(index), '--output', str(output)), commit_limit=CAP, timeout_ms=TIMEOUT)
    row = {'worker_status': 'FAILED', 'completed_job': asdict(job)}
    try:
        if output.exists():
            with output.open('rb') as stream:
                payload = stream.read(262145)
            assert len(payload) <= 262144, 'worker report exceeds the registered minimal-report bound'
            row['result'] = json.loads(payload)
        if job.exit_code == 0 and not job.timed_out and job.attached_before_resume and not job.limit_terminated_processes:
            result = row['result']
            observed = result['host']
            assert result['process_id'] == job.process_id == observed['process_id']
            assert observed['creation_100ns'] == job.process_creation_100ns
            assert observed['lifetime_process_commit_peak'] <= job.peak_process_commit <= CAP
            assert observed['job_commit_peak'] <= job.peak_job_commit <= CAP
            for clock in ('user', 'kernel'):
                assert max(observed[f'process_{clock}_100ns'], observed[f'job_{clock}_100ns']) <= getattr(job, f'{clock}_100ns')
            row['worker_status'] = 'EXECUTED'
    except Exception:
        row['report_audit_failure'] = traceback.format_exc()
    if output.exists():
        output.unlink()
    directory.rmdir()
    return row


def preflight():
    _, baseline = retained_baselines()
    configurations = []
    for case in CASES:
        cfg, graph, online, cuda, _, _ = setup(case)
        configurations.append({'case': case, 'training_events': len(online.profiles[0].observation_ids),
            'native': graph.counts(), 'grammar': dict(cfg.graph_limits),
            'prepaid_derivation_work': preparation_work(graph, cfg.semantics, online.learner, cfg.source_domain, 32768),
            'prepaid_scratch_bytes': preparation_workspace(graph, cfg.semantics, online.learner, cfg.source_domain, 32768),
            'predict_cells': output_cells('predict', graph, cfg.semantics, online.learner),
            'observe_cells': output_cells('observe', graph, cfg.semantics, online.learner)})
    assert 'torch' not in sys.modules
    return {'cases': configurations, 'baseline': baseline, 'host_cap': CAP, 'timeout_ms': TIMEOUT,
        'packed_cap': PACKED, 'work_per_role': WORK, 'phase_frame_bytes': FRAME, 'phase_output_cells': CELLS,
        'arena_bytes': ARENA, 'allocator_bytes': 2*ARENA, 'reference_bits': 32768,
        'native_cap': '16', 'binary64_tolerances': '1/1000000000',
        'AMP_state_native_normalizer_tolerance': '1/100', 'AMP_probability_tolerance': '1/1000',
        'Gamma': 'feature1; 128 selected weights1/128', 'unit': 1, 'rate': '1', 'profile_passes': 1,
        'likelihood_radix': '9', 'counter_bits': 64, 'execution_identity': cuda.execution_identity,
        'scope': 'retrospective matched mechanism matrix; no new IID sample, class certificate or timing claim'}


def matrix(write=False, resume=False):
    source = git('rev-parse', 'HEAD')
    def source_clean():
        assert git('rev-parse', 'HEAD') == source
        assert not git('status', '--porcelain', '--', *DEPENDENCIES), 'commit all execution dependencies first'
    source_clean()
    registration_value = json.loads(json.dumps(preflight()))
    baselines, _ = retained_baselines()
    prior_failure = prior_auditor_failure(registration_value)
    if resume:
        report = json.loads(OUTPUT.read_text(encoding='utf-8'))
        assert report['status'] == 'PARTIAL_EXECUTION' and report['registration_source'] == source
        assert report['registration'] == registration_value
        assert report['prior_auditor_failure'] == prior_failure
        assert [r['case_index'] for r in report['workers']] == list(range(len(report['workers'])))
    else:
        assert not write or not OUTPUT.exists(), 'retain earlier evidence; no silent rerun'
        report = {'status': 'PARTIAL_EXECUTION', 'registration_source': source,
                  'protocol_origin': PROTOCOL_ORIGIN, 'prior_auditor_failure': prior_failure,
                  'registration': registration_value, 'workers': []}
    def publish():
        if write:
            temporary = OUTPUT.with_suffix('.tmp')
            temporary.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
            temporary.replace(OUTPUT)
    publish()
    for index in range(len(report['workers']), len(CASES)):
        source_clean()
        row = bounded(index)
        row.update(case_index=index, case=CASES[index], execution_source=source)
        if row['worker_status'] == 'EXECUTED' and row['result']['run_status'] == 'SEALED_CUDA_STREAM':
            try:
                for key in ('adaptive_exact_unseen', 'adaptive_exact_full_domain'):
                    assert row['result']['scores'][key] == baselines[index][key]
                assert row['result']['device'] == baselines[index]['device']
            except Exception:
                row['worker_status'] = 'FAILED'
                row['report_audit_failure'] = traceback.format_exc()
        report['workers'].append(row)
        source_clean()
        publish()
        print(json.dumps({'case': CASES[index], 'worker_status': row['worker_status']}), flush=True)
        failure = row.get('result', {}).get('traceback', '')
        if 'report_audit_failure' in row or failure and 'MemoryError' not in failure:
            report['status'] = 'STOPPED_AUDITOR_FAILURE'
            publish()
            return {'status': report['status'], 'attempted_workers': len(report['workers'])}
    report['status'] = 'COMPLETE_EXECUTION' if all(r['worker_status'] == 'EXECUTED' for r in report['workers']) else 'COMPLETE_WITH_FAILURES'
    publish()
    return {'status': report['status'], 'workers': len(report['workers']),
            'executed': sum(r['worker_status'] == 'EXECUTED' for r in report['workers'])}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preflight', action='store_true')
    parser.add_argument('--matrix', action='store_true')
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--worker', type=int, choices=range(len(CASES)))
    parser.add_argument('--output')
    args = parser.parse_args()
    assert (args.worker is not None) == bool(args.output)
    assert not args.resume or args.matrix and args.write
    assert not args.write or args.matrix
    assert args.worker is None or not (args.matrix or args.preflight)
    if args.worker is not None:
        try:
            result = worker(CASES[args.worker])
        except Exception:
            Path(args.output).write_text(json.dumps({'traceback': traceback.format_exc(), 'process_id': os.getpid()}), encoding='utf-8')
            raise
        Path(args.output).write_text(json.dumps(result), encoding='utf-8')
    else:
        assert args.preflight or args.matrix
        print(json.dumps(preflight() if args.preflight else matrix(args.write, args.resume), indent=2))
