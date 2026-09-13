"""RN-2: fixed prospective-model cases; fresh jobs and retained RN-1 controls."""
import argparse
from dataclasses import asdict
from fractions import Fraction as F
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import traceback

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'experiments/relation_noise'))
import run_experiment as rn1
import analyze_results as rn1_analysis
from model import data, context, counts_from_training, unseen_pairs

OUTPUT = ROOT/'evidence/minimal/FP_PROSPECTIVE_RELATION_EXPERIMENT.json'
HISTORY_COMMIT = '4d04595'
PROTOCOL_COMMIT = '9ec4c33'
DEPENDENCIES = ('src/reference_compiler', 'scripts',
    'experiments/relation_noise/model.py', 'experiments/relation_noise/run_experiment.py',
    'experiments/relation_noise/analyze_results.py',
    'experiments/prospective_relation/PROTOCOL.md', 'experiments/prospective_relation/run.py')


def diagnostic_cases():
    return (tuple((n, 'iid', seed) for n in (8, 16) for seed in range(4))
            + tuple((n, 'conditioned', 0) for n in (8, 16))
            + ((8, 'disconnected-a', 0), (8, 'disconnected-b', 0)))


def new_cases():
    return tuple((n, 'iid', seed) for n in (8, 16) for seed in range(4, 8))


def tasks():
    return (tuple(('FP', case) for case in diagnostic_cases())
            + tuple((kind, case) for case in new_cases() for kind in ('FP', 'posterior')))


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT).decode('utf-8').rstrip('\r\n')


def historical():
    relative = rn1.OUTPUT.relative_to(ROOT).as_posix()
    retained = json.loads(git('show', HISTORY_COMMIT+':'+relative))
    assert retained == json.loads(rn1.OUTPUT.read_text(encoding='utf-8'))
    workers, checked = rn1_analysis.verify()
    assert workers == retained['workers']
    rows = {(r['kind'], tuple(r['case'])): r for r in workers}
    assert all((kind, case) in rows for case in diagnostic_cases() for kind in ('FP', 'posterior'))
    return rows, {'journal': relative, 'journal_commit': git('rev-parse', HISTORY_COMMIT),
        'worker_source': retained['registration_source'],
        'reused_cases': diagnostic_cases(), 'independently_recomputed_RN1_scores':
        checked['independently_recomputed_score_records']}


def fp_worker(case):
    n, law, seed = case
    hidden, edges, train, evaluation = data(case)
    cfg, online, policy = rn1.configuration(case)
    rt = rn1.ReferenceCompilerRuntime(cfg, rn1.zero_program(2), online=online, policy=policy,
        cuda=rn1.cuda_contract(install=rn1.CudaInstallContract()),
        host=rn1.HostResourceContract(rn1.HOST_CAP, {'deployment': rn1.HOST_CAP, 'compiler': rn1.HOST_CAP}))
    base = rt.snapshot().deployed_id
    cutoff = None
    for cursor, (i, j, label) in enumerate(train+evaluation):
        prediction = rn1.deliver_context(rt, f'observation-{cursor}', context(n, i, j))
        assert prediction.status == 'PREDICTED_REFERENCE', prediction
        observed = rt.observe(label)
        assert observed.status == 'OBSERVED_REFERENCE', observed
        if cursor+1 == len(train):
            cutoff = rn1.owned(rt)
    final = rn1.owned(rt)
    assert final.halted is None and final.run.status == 'SEALED_CUDA_STREAM'
    assert final.cursor == len(train)+len(evaluation) and cutoff is not None
    revealed_train = tuple((*rn1.read_pair(n, row), row.target) for row in cutoff.observations)
    assert revealed_train == train
    session, = cutoff.searches
    proposal = session.relation_proposal
    candidates = [row for row in cutoff.candidates if row.candidate_id != base]
    assert len(candidates) <= 1 and len(final.install_receipts) <= 1
    cid = candidates[0].candidate_id if candidates else None
    install = final.install_receipts[0].attempt.cursor if final.install_receipts else None
    # Every score reads actual retained device forecasts at the declared cut.
    # Hidden relations never enter Runtime, its search or its evidence rule.
    observations = {row.observation_id: row for row in final.observations}
    mass, raw, deployed_mass, deployed_raw = {}, {}, {}, {}
    for phase in final.cuda.phases:
        if phase.raw_prediction is None or phase.ordinary_cursor < len(train):
            continue
        assert phase.status == 'CHECKED_CUDA_PREFIX_PHASE'
        pair = rn1.read_pair(n, observations[phase.observation_id])
        values = tuple(rn1.SINGLE.decode(w) for w in phase.raw_prediction[3])
        probabilities = tuple(v/sum(values) for v in values)
        outputs = tuple(rn1.SINGLE.decode(w) for w in phase.raw_prediction[5])
        mass.setdefault(phase.candidate_id, {})[pair] = probabilities
        raw.setdefault(phase.candidate_id, {})[pair] = outputs
        current = cid if install is not None and phase.ordinary_cursor >= install else base
        if phase.candidate_id == current:
            deployed_mass[pair], deployed_raw[pair] = probabilities, outputs
    assert all(len(rows) == n*n for rows in mass.values()) and len(deployed_mass) == n*n
    unseen = unseen_pairs(n, edges)
    domain = tuple((i, j) for i in range(n) for j in range(n))
    native, candidate_score, candidate_full = None, None, None
    if cid is not None:
        graph = dict(cutoff.programs)[candidates[0].program_id]
        native = graph.counts()
        assert candidates[0].theta == cfg.initializer_pattern[:graph.slot_count]
        for i, j in mass[cid]:
            sources = dict(zip((s.source_id for s in cfg.semantics.sources), context(n, i, j)))
            p, _ = rn1.forward_oracle(graph, cfg.semantics, candidates[0].theta, sources)
            assert p == mass[cid][i, j]
        candidate_score = rn1.scored(mass[cid], raw[cid], hidden, unseen)
        candidate_full = rn1.scored(mass[cid], raw[cid], hidden, domain)
    decisions = []
    for decision in final.run.closure.decisions:
        if session.proof_id is None:
            assert decision.decision_status == 'UNRESOLVED' and decision.proof is None
        decisions.append({'status': decision.decision_status, 'search_status': decision.search_status,
            'has_proof': decision.proof is not None, 'scope': decision.scope,
            'grammar': asdict(decision.spec.grammar), 'ordinary_cursor': decision.ordinary_cursor})
    assert len(decisions) == 1
    if final.install_receipts:
        assert final.install_receipts[0].attempt.proposal_proof_id == session.proof_id
    cuda = rn1.audit_snapshot(rt)
    cpu_phases = rn1.replay(rt)[0]
    assert cuda['phases'] == cpu_phases
    return {'kind': 'FP', 'case': case, 'run_status': final.run.status,
        'training_events': len(train), 'evaluation_events': len(evaluation),
        'counts': counts_from_training(n, revealed_train),
        'cutoff_search_status': session.status, 'cutoff_search_reason': session.reason,
        'proposal_status': None if proposal is None else proposal.status,
        'proposal_reason': None if proposal is None else proposal.reason,
        'proposal_assignment': None if proposal is None else proposal.assignment,
        'proposal_scale': None if proposal is None or proposal.scale is None else str(proposal.scale),
        'components': None if proposal is None else proposal.components,
        'native_candidate': native, 'actually_compared': len(session.rows),
        'reference_proofs': len(final.reference_proofs), 'final_class_decisions': decisions,
        'final_policy_stage': final.compiler_policy.state.stages[0].status,
        'install_cursor': install, 'alpha_spent': str(final.alpha_spent),
        'frozen_candidate_unseen': candidate_score, 'frozen_candidate_full_domain': candidate_full,
        'deployed_stream_unseen': rn1.scored(deployed_mass, deployed_raw, hidden, unseen),
        'deployed_stream_full_domain': rn1.scored(deployed_mass, deployed_raw, hidden, domain),
        'independent_CUDA': cuda, 'independent_binary64_phases': cpu_phases,
        'resources': {'peak_packed_bytes': final.resources['peak']['reference_payload_bytes'],
            'consumed_native_arena_extent': final.cuda.storage['consumed_arena_extent']},
        'device': rn1.device_record(final.cuda.device, final.cuda.contract.execution_identity),
        'host': rn1.host_record(final)}


def bounded(kind, case):
    with tempfile.TemporaryDirectory(prefix='fp-prospective-model-', dir=ROOT) as temporary:
        assert Path(temporary).resolve().parent == ROOT
        output = Path(temporary)/'result.json'
        job = rn1.run_in_job(__file__, ('--worker', kind, '--case', *map(str, case), '--worker-output', output),
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
        result.update(kind=kind, case=case, completed_job=asdict(job))
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
    # Do not inspect the new seeds. The reused registrations depend on n,
    # edge support and length, not the realized labels or hidden bits.
    assert len(diagnostic_cases()) == 12 and len(new_cases()) == 8 and len(tasks()) == 28
    assert len(set(tasks())) == 28 and not set(diagnostic_cases()) & set(new_cases())
    for case in diagnostic_cases():
        cfg, online, policy = rn1.configuration(case)
        n = case[0]
        expected = 10*(n-1-int(case[1].startswith('disconnected')))
        assert len(online.data.active.observation_ids) == expected+n*n
        assert cfg.initializer_pattern == (F(1), F(8)) and policy.steps[0].after_cursor == expected
    _, reference = historical()
    assert not git('diff', PROTOCOL_COMMIT, '--', 'experiments/prospective_relation/PROTOCOL.md')
    assert 'torch' not in sys.modules
    return {'new_workers': len(tasks()), 'previously_unexecuted_cases': len(new_cases()),
        'new_seed_labels_not_inspected': True, 'historical_control': reference}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preflight', action='store_true')
    parser.add_argument('--worker', choices=('FP', 'posterior'))
    parser.add_argument('--case', nargs=3)
    parser.add_argument('--worker-output')
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args()
    if args.preflight:
        assert not (args.worker or args.case or args.write or args.resume or args.worker_output)
        print(json.dumps(preflight(), indent=2))
        return
    case = None if args.case is None else (int(args.case[0]), args.case[1], int(args.case[2]))
    if args.worker:
        assert args.worker_output and (args.worker, case) in tasks() and not (args.write or args.resume)
        try:
            result = fp_worker(case) if args.worker == 'FP' else rn1.baseline_worker(case)
            result['worker_status'] = 'EXECUTED'
        except Exception:
            result = {'worker_status': 'FAILED', 'traceback': traceback.format_exc()[-12288:], 'process_id': os.getpid()}
            Path(args.worker_output).write_text(json.dumps(result), encoding='utf-8')
            raise
        Path(args.worker_output).write_text(json.dumps(result), encoding='utf-8')
        return
    assert args.write and case is None and not args.worker_output
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
        report = {'experiment': 'RN-2', 'status': 'PARTIAL_EXECUTION', 'registration_source': revision,
            'protocol_commit': git('rev-parse', PROTOCOL_COMMIT), 'historical_control': reference, 'workers': []}
    assert [(r['kind'], tuple(r['case'])) for r in report['workers']] == list(tasks()[:len(report['workers'])])
    for kind, case in tasks()[len(report['workers']):]:
        result = bounded(kind, case)
        if result['worker_status'] == 'EXECUTED':
            try:
                assert result['device'] == expected_device
                if case in diagnostic_cases():
                    assert result['counts'] == old['posterior', case]['counts']
                elif kind == 'posterior' and report['workers'][-1]['worker_status'] == 'EXECUTED':
                    assert result['counts'] == report['workers'][-1]['counts']
            except Exception:
                result.update(worker_status='FAILED', validation_error=traceback.format_exc()[-8192:])
        report['workers'].append(dict(result, execution_source=revision))
        source_clean(revision)
        if len(report['workers']) == len(tasks()):
            report['status'] = ('COMPLETE_EXECUTION' if all(r['worker_status'] == 'EXECUTED' for r in report['workers'])
                                else 'COMPLETE_WITH_FAILURES')
        OUTPUT.write_text(json.dumps(report, indent=1)+'\n', encoding='utf-8')
        print(kind+' '+str(case)+' '+result['worker_status']+' '+result.get('cutoff_search_status', ''), flush=True)
    print(json.dumps({'status': report['status'], 'workers': len(report['workers'])}, indent=2))


if __name__ == '__main__':
    main()
