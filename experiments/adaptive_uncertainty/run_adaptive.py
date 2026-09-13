"""RN-4: adaptive native uncertainty and an exact/AMP adaptive posterior.

The FP recorder follows the canonical RN-2 runner; the baseline numerical
pipeline follows RN-1. Each uses this study's data through explicit calls,
without replacing globals or supplying hidden support to Runtime.
"""
import argparse
from dataclasses import asdict, replace
from fractions import Fraction as F
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import traceback

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'experiments/component_uncertainty'))
import run_study as previous
rn1 = previous.rn1
from adaptive_model import (data, context, counts_from_training, unseen_pairs, score,
    diagnostic_cases, new_cases, tasks, support, AdaptivePosterior, exact_audit)
from fp_reference.float64_bridge import Float64Contract
from audit_reference_construction import validate_residency

OUTPUT = ROOT/'evidence/minimal/FP_ADAPTIVE_UNCERTAINTY_EXPERIMENT.json'
PROTOCOL_ORIGIN = '803cdc2'
SOLVER = 'empirical-binary-relation-balanced-readout-v4'
DEPENDENCIES = previous.DEPENDENCIES + (
    'experiments/adaptive_uncertainty/PROTOCOL.md',
    'experiments/adaptive_uncertainty/adaptive_model.py',
    'experiments/adaptive_uncertainty/run_adaptive.py')


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT).decode('utf-8').rstrip('\r\n')


def historical():
    rows, references = {}, []
    for commit, path, kind in (('2ca5b8a', previous.OUTPUT, 'FP'), ('4d04595', rn1.OUTPUT, 'posterior')):
        relative = path.relative_to(ROOT).as_posix()
        report = json.loads(git('show', commit+':'+relative))
        assert report == json.loads(path.read_text(encoding='utf-8')) and report['status'] == 'COMPLETE_EXECUTION'
        selected = [r for r in report['workers'] if r['kind'] == kind and tuple(r['case']) in diagnostic_cases()]
        assert len(selected) == 2
        for row in selected:
            case = tuple(row['case'])
            assert row['counts'] == json.loads(json.dumps(counts_from_training(case[0], data(case)[2])))
            job = row['completed_job']
            assert job['exit_code'] == 0 and not job['timed_out'] and job['attached_before_resume']
            rows[kind, case] = row
        references.append({'journal': relative, 'journal_commit': git('rev-parse', commit),
            'worker_source': report['registration_source'], 'kind': kind, 'reused_cases': diagnostic_cases()})
    assert len({json.dumps(r['device'], sort_keys=True) for r in rows.values()}) == 1
    return rows, references


def configuration(case, rate):
    n = case[0]
    edges = support(case)
    train_count = 10*len(edges)
    cfg, old, _, _, _ = rn1.fixture_parameters(n, groups=(0,)*n, edges=edges)
    pattern = (F(1), F(8))+(F(1),)*(n*(n-1))
    grammar = replace(old.searches[0].grammar, slots=len(pattern))
    cfg = replace(cfg, initializer_pattern=pattern, graph_limits=asdict(grammar),
        activation_cap=F(16), normalizer_cap=F(18))
    run = rn1.online(cfg, train_count+n*n, unit=1, rate=F(rate), grid=16)
    persistence = rn1.registration(bound=F(3), horizon=n*n)
    rules = tuple(replace(rule, rule_id='cuda', score_path=rn1.CUDA_PATH)
                  if rule.score_path == rn1.FLOAT64_PATH else rule for rule in persistence.rules)
    run = replace(run, searches=(replace(old.searches[0], grammar=grammar,
        relation_sources=replace(old.searches[0].relation_sources, solver=SOLVER)),),
        float64=Float64Contract(F(1, 100), F(1, 100)), persistence=replace(persistence, rules=rules),
        data=replace(run.data, stream_law=rn1.StochasticStreamLaw(
            'RN-4 external branch-invariant noise assumption; a seeded tape proves no stochastic premise')))
    policy = rn1.CudaCompilerPolicy((rn1.CudaCompilationStep(train_count, 'native', 1, 'ref', 'cuda'),))
    return cfg, run, policy


def maxima(traces):
    return {key: str(max((getattr(t.relation, key) for t in traces if t.relation is not None), default=F(0)))
        for key in ('state_error', 'native_error', 'normalizer_error', 'probability_error', 'division_error')}


def fp_worker(case, rate):
    n, law, seed = case
    hidden, edges, train, evaluation = data(case)
    cfg, run, policy = configuration(case, rate)
    rt = rn1.ReferenceCompilerRuntime(cfg, rn1.zero_program(2), online=run, policy=policy,
        cuda=rn1.cuda_contract(install=rn1.CudaInstallContract()),
        host=rn1.HostResourceContract(rn1.HOST_CAP, {'deployment': rn1.HOST_CAP, 'compiler': rn1.HOST_CAP}))
    base = rt.snapshot().deployed_id
    cutoff = None
    for cursor, (i, j, label) in enumerate(train+evaluation):
        prediction = rn1.deliver_context(rt, f'observation-{cursor}', context(n, i, j))
        if prediction.status != 'PREDICTED_REFERENCE':
            assert prediction.status == 'UNRESOLVED'
            break
        observed = rt.observe(label)
        if observed.status != 'OBSERVED_REFERENCE':
            assert observed.status == 'UNRESOLVED'
            break
        if cursor+1 == len(train):
            cutoff = validate_residency(rt)
    final = validate_residency(rt)
    complete = final.halted is None and final.run.status == 'SEALED_CUDA_STREAM'
    assert complete or final.run.status == 'HALTED_UNRESOLVED'
    search = None if cutoff is None else cutoff.searches[0]
    proposal = None if search is None else search.relation_proposal
    candidates = [] if cutoff is None else [c for c in cutoff.candidates if c.candidate_id != base]
    assert len(candidates) <= 1 and len(final.install_receipts) <= 1
    cid = candidates[0].candidate_id if candidates else None
    install = final.install_receipts[0].attempt.cursor if final.install_receipts else None
    phase_checked = (all(t.status == 'CHECKED_FLOAT64_PHASE' for t in final.float64_traces)
                     and all(t.status == 'CHECKED_CUDA_PREFIX_PHASE' for t in final.cuda.phases))
    cuda = rn1.audit_snapshot(rt) if phase_checked else None
    cpu = rn1.replay(rt)[0] if phase_checked else None
    assert cpu is None or cuda['phases'] == cpu
    if complete:
        assert phase_checked and final.cursor == len(train)+len(evaluation) and cutoff is not None
    native = None if not candidates else dict(cutoff.programs)[candidates[0].program_id].counts()
    measured = dict(candidate_stream_unseen=None, candidate_stream_full_domain=None,
                    deployed_stream_unseen=None, deployed_stream_full_domain=None)
    if complete:
        revealed = tuple((*rn1.read_pair(n, row), row.target) for row in cutoff.observations)
        assert revealed == train
        observations = {r.observation_id: r for r in final.observations}
        candidate_mass, candidate_raw, deployed_mass, deployed_raw = {}, {}, {}, {}
        for phase in final.cuda.phases:
            if phase.raw_prediction is None or phase.ordinary_cursor < len(train):
                continue
            pair = rn1.read_pair(n, observations[phase.observation_id])
            masses = tuple(rn1.SINGLE.decode(w) for w in phase.raw_prediction[3])
            p = tuple(v/sum(masses) for v in masses)
            raw = tuple(rn1.SINGLE.decode(w) for w in phase.raw_prediction[5])
            if phase.candidate_id == cid:
                candidate_mass[pair], candidate_raw[pair] = p, raw
            current = cid if install is not None and phase.ordinary_cursor >= install else base
            if phase.candidate_id == current:
                deployed_mass[pair], deployed_raw[pair] = p, raw
        domain = tuple((i, j) for i in range(n) for j in range(n))
        unseen = unseen_pairs(n, edges)
        assert len(deployed_mass) == n*n
        measured.update(deployed_stream_unseen=score(deployed_mass, deployed_raw, hidden, unseen),
                        deployed_stream_full_domain=score(deployed_mass, deployed_raw, hidden, domain))
        if cid is not None:
            assert len(candidate_mass) == n*n
            measured.update(candidate_stream_unseen=score(candidate_mass, candidate_raw, hidden, unseen),
                            candidate_stream_full_domain=score(candidate_mass, candidate_raw, hidden, domain))
    decisions = []
    if final.run.closure is not None:
        for decision in final.run.closure.decisions:
            if search is not None and search.proof_id is None:
                assert decision.decision_status == 'UNRESOLVED' and decision.proof is None
            decisions.append({'status': decision.decision_status, 'has_proof': decision.proof is not None,
                'scope': decision.scope, 'ordinary_cursor': decision.ordinary_cursor, 'grammar': asdict(decision.spec.grammar)})
    return dict(kind='FP', case=case, rate=rate, run_status=final.run.status,
        halted=final.halted, cursor=final.cursor, training_events=len(train), evaluation_events=len(evaluation),
        counts=counts_from_training(n, train),
        proposal_status=None if proposal is None else proposal.status,
        proposal_reason=None if proposal is None else proposal.reason,
        proposal_assignment=None if proposal is None else proposal.assignment,
        components=None if proposal is None else proposal.components,
        proposal_scale=None if proposal is None or proposal.scale is None else str(proposal.scale),
        native_candidate=native, cutoff_search_status=None if search is None else search.status,
        actually_compared=0 if search is None else len(search.rows), reference_proofs=len(final.reference_proofs),
        final_class_decisions=decisions, install_cursor=install, alpha_spent=str(final.alpha_spent),
        final_policy_stage=final.compiler_policy.state.stages[0].status,
        independent_CUDA=cuda, independent_binary64_phases=cpu,
        phase_audit_status='ALL_EXECUTED_PHASES_CHECKED' if phase_checked else 'UNRESOLVED_NUMERICAL_PHASE_RETAINED; NO_COMPLETE_ORACLE_CLAIM',
        float64_relation_maxima=maxima(final.float64_traces), CUDA_relation_maxima=maxima(final.cuda.phases),
        resources={'peak_packed_bytes': final.resources['peak']['reference_payload_bytes'],
            'consumed_native_arena_extent': final.cuda.storage['consumed_arena_extent']},
        device=rn1.device_record(final.cuda.device, final.cuda.contract.execution_identity),
        host=rn1.host_record(final), **measured)


def baseline_worker(case):
    n, law, seed = case
    hidden, edges, train, evaluation = data(case)
    decoded = tuple((*rn1.decode_context(n, context(n, i, j)), label) for i, j, label in train)
    counts = counts_from_training(n, decoded)
    learner = AdaptivePosterior(n, counts, law)
    exact, normalized, raw = {}, {}, {}
    import torch
    contract = rn1.cuda_contract()
    device = rn1._CudaDevice(contract.device, 0)
    identity = (torch.__version__, torch.version.git_version, torch.version.cuda,
                torch.cuda.get_device_name(0), torch.cuda.get_device_capability(0))
    assert identity == contract.execution_identity and torch.cuda.memory_allocated() == 0
    maximum_error = F(0)
    for i, j, label in evaluation:
        pair = rn1.decode_context(n, context(n, i, j))
        probabilities = learner.predict(*pair)
        words = []
        for probability in probabilities:
            excess = 10*probability-1
            word = rn1.HALF.rounded(excess)
            if rn1.HALF.decode(word) > excess:
                word -= 1
            assert 0 <= rn1.HALF.decode(word) <= excess
            assert word+1 == rn1.HALF.infinity or rn1.HALF.decode(word+1) > excess
            words.append(word)
        with torch.no_grad():
            half = torch.tensor([float(rn1.HALF.decode(w)) for w in words], dtype=torch.float16, device='cuda').reshape(1, 2)
            addresses = torch.tensor([0], dtype=torch.int64, device='cuda')
            selected = half.index_select(0, addresses)
            values = selected.to(torch.float32)
            masses = values+torch.ones_like(values)
            total = masses[:, 0]+masses[:, 1]
            p0, p1 = masses[:, 0]/total, masses[:, 1]/total
            torch.cuda.synchronize()
            assert tuple(w & 0xffff for w in half.view(torch.int16).cpu().flatten().tolist()) == tuple(words)
            assert tuple(w & 0xffff for w in selected.view(torch.int16).cpu().flatten().tolist()) == tuple(words)
            actual_mass = tuple(masses.view(torch.int32).cpu().flatten().tolist())
            actual_total = total.view(torch.int32).cpu().item()
            actual_p = (p0.view(torch.int32).cpu().item(), p1.view(torch.int32).cpu().item())
        wanted = tuple(rn1.SINGLE.rounded(1+rn1.HALF.decode(w)) for w in words)
        assert actual_mass == wanted
        decoded_mass = tuple(rn1.SINGLE.decode(w) for w in actual_mass)
        expected_total = rn1.SINGLE.rounded(sum(decoded_mass))
        assert actual_total == expected_total and sum(decoded_mass) <= 10
        assert actual_p == tuple(rn1.SINGLE.rounded(v/rn1.SINGLE.decode(expected_total)) for v in decoded_mass)
        exact[pair] = probabilities
        normalized[pair] = tuple(v/sum(decoded_mass) for v in decoded_mass)
        raw[pair] = tuple(rn1.SINGLE.decode(w) for w in actual_p)
        maximum_error = max(maximum_error, *(abs(a-b) for a, b in zip(normalized[pair], probabilities)))
        learner.observe(label)  # After every forecast word has been captured.
        del half, addresses, selected, values, masses, total, p0, p1
    peak, reserved = torch.cuda.max_memory_allocated(), torch.cuda.max_memory_reserved()
    assert peak <= 16 << 20 and reserved <= 32 << 20
    domain = tuple((i, j) for i in range(n) for j in range(n))
    unseen = unseen_pairs(n, edges)
    assert len(exact) == n*n and learner.pending is None
    return {'kind': 'posterior', 'case': case, 'rate': 'none', 'counts': counts,
        'prior': 'independent fair bits; initial conditioned/IID law and all subsequent noisy labels',
        'adaptive_exact_unseen': score(exact, None, hidden, unseen),
        'adaptive_AMP_unseen': score(normalized, raw, hidden, unseen),
        'adaptive_exact_full_domain': score(exact, None, hidden, domain),
        'adaptive_AMP_full_domain': score(normalized, raw, hidden, domain),
        'complete_domain_raw_predictions_checked': n*n,
        'maximum_exact_weight_bits': learner.maximum_weight_bits,
        'maximum_exact_probability_bits': learner.maximum_probability_bits,
        'maximum_AMP_mass_probability_error': str(maximum_error),
        'resources': {'maximum_integer_weight_payload_bytes': learner.maximum_retained_payload_bytes,
            'counted_assignment_visits': learner.work, 'native_tensor_peak_bytes': peak,
            'native_allocator_peak_reserved_bytes': reserved},
        'device': rn1.device_record(device.snapshot(), identity), 'process_id': os.getpid()}


def bounded(kind, case, rate):
    with tempfile.TemporaryDirectory(prefix='fp-adaptive-model-', dir=ROOT) as temporary:
        assert Path(temporary).resolve().parent == ROOT
        output = Path(temporary)/'result.json'
        job = rn1.run_in_job(__file__, ('--worker', kind, '--case', *map(str, case), '--rate', rate, '--worker-output', output),
            commit_limit=rn1.HOST_CAP, timeout_ms=1200000)
        # A failed attempt remains a recorded outcome; no score or completion
        # is inferred from a timeout, missing report or partial execution.
        raw = output.read_bytes() if output.exists() else b''
        try:
            assert len(raw) <= 20480
            result = json.loads(raw)
        except Exception:
            result = {'worker_status': 'FAILED', 'reason': 'missing or invalid bounded worker report',
                'report_tail': raw[-8192:].decode('utf-8', errors='replace')}
        result.update(kind=kind, case=case, rate=rate, completed_job=asdict(job))
        if result['worker_status'] == 'EXECUTED':
            try:
                assert job.exit_code == 0 and not job.timed_out and job.attached_before_resume
                assert max(job.peak_process_commit, job.peak_job_commit) <= rn1.HOST_CAP
                assert job.limit_terminated_processes == 0
                if kind == 'FP':
                    host = result['host']
                    assert (host['process_id'], host['creation_100ns']) == (job.process_id, job.process_creation_100ns)
                    assert host['lifetime_process_commit_peak'] <= job.peak_process_commit
                else:
                    assert result['process_id'] == job.process_id
            except Exception:
                result.update(worker_status='FAILED', validation_error=traceback.format_exc()[-8192:])
        return result


def source_clean(revision):
    assert git('rev-parse', 'HEAD') == revision
    assert not git('diff', revision, '--', *DEPENDENCIES)
    assert not git('ls-files', '--others', '--exclude-standard', '--', *DEPENDENCIES)


def preflight():
    assert len(tasks()) == len(set(tasks())) == 30
    for case in diagnostic_cases()+new_cases():
        for rate in ('1/8', '4'):
            cfg, run, policy = configuration(case, rate)
            n = case[0]
            assert len(run.data.active.observation_ids) == 10*len(support(case))+n*n
            assert run.learner.update_unit == 1 and run.learner.learning_rate == F(rate)
            assert cfg.normalizer_cap == 18 and cfg.activation_cap == 16
            assert cfg.initializer_pattern == (F(1), F(8))+(F(1),)*(n*(n-1))
    _, old = historical()
    exact = exact_audit()
    assert 'torch' not in sys.modules
    return {'new_workers': 30, 'new_seed_labels_not_inspected': True, 'posterior_check': exact,
        'historical_controls': old}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preflight', action='store_true')
    parser.add_argument('--worker', choices=('FP', 'posterior'))
    parser.add_argument('--case', nargs=3)
    parser.add_argument('--worker-output')
    parser.add_argument('--rate', choices=('1/8', '4', 'none'))
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args()
    if args.preflight:
        assert not (args.worker or args.case or args.rate or args.write or args.resume or args.worker_output)
        print(json.dumps(preflight(), indent=2))
        return
    case = None if args.case is None else (int(args.case[0]), args.case[1], int(args.case[2]))
    if args.worker:
        assert args.worker_output and (args.worker, case, args.rate) in tasks() and not (args.write or args.resume)
        try:
            result = fp_worker(case, args.rate) if args.worker == 'FP' else baseline_worker(case)
            result['worker_status'] = 'EXECUTED'
        except Exception:
            result = {'worker_status': 'FAILED', 'traceback': traceback.format_exc()[-12288:], 'process_id': os.getpid()}
            Path(args.worker_output).write_text(json.dumps(result), encoding='utf-8')
            raise
        Path(args.worker_output).write_text(json.dumps(result), encoding='utf-8')
        return
    assert args.write and case is None and args.rate is None and not args.worker_output
    revision = git('rev-parse', 'HEAD')
    source_clean(revision)
    old, reference = historical()
    expected_device = next(iter(old.values()))['device']
    if args.resume:
        report = json.loads(OUTPUT.read_text(encoding='utf-8'))
        assert report['status'] == 'PARTIAL_EXECUTION' and report['registration_source'] == revision
        assert report['historical_control'] == json.loads(json.dumps(reference))
    else:
        assert not OUTPUT.exists()
        report = {'experiment': 'RN-4', 'status': 'PARTIAL_EXECUTION', 'registration_source': revision,
            'protocol_origin': git('rev-parse', PROTOCOL_ORIGIN), 'final_protocol_source': revision, 'historical_control': reference, 'workers': []}
    assert [(r['kind'], tuple(r['case']), r['rate']) for r in report['workers']] == list(tasks()[:len(report['workers'])])
    for kind, case, rate in tasks()[len(report['workers']):]:
        result = bounded(kind, case, rate)
        if result['worker_status'] == 'EXECUTED':
            try:
                assert result['device'] == expected_device
                if case in diagnostic_cases():
                    assert result['counts'] == old['FP', case]['counts']
                else:
                    peers = [r for r in report['workers'] if tuple(r['case']) == case and r['worker_status'] == 'EXECUTED']
                    assert all(r['counts'] == result['counts'] for r in peers)
            except Exception:
                result.update(worker_status='FAILED', validation_error=traceback.format_exc()[-8192:])
        report['workers'].append(dict(result, execution_source=revision))
        source_clean(revision)
        if len(report['workers']) == len(tasks()):
            report['status'] = ('COMPLETE_EXECUTION' if all(r['worker_status'] == 'EXECUTED' for r in report['workers'])
                                else 'COMPLETE_WITH_FAILURES')
        OUTPUT.write_text(json.dumps(report, indent=1)+'\n', encoding='utf-8')
        print(kind+' '+str(case)+' rate='+rate+' '+result['worker_status']+' '+result.get('run_status', ''), flush=True)
    print(json.dumps({'status': report['status'], 'workers': len(report['workers'])}, indent=2))


if __name__ == '__main__':
    main()
