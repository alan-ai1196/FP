"""RN-3: component uncertainty, complete owned runs and separate strong AMP controls.

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
sys.path.insert(0, str(ROOT/'experiments/relation_noise'))
import run_experiment as rn1
import analyze_results as rn1_analysis
from study import data, context, counts_from_training, unseen_pairs, posterior, score
from study import diagnostic_cases, new_cases, tasks, support
from run_experiment import (HALF, SINGLE, cuda_contract, _CudaDevice, device_record,
    decode_context, scored)

sys.path.insert(0, str(ROOT/'experiments/prospective_relation'))
import analyze as rn2_analysis

OUTPUT = ROOT/'evidence/minimal/FP_COMPONENT_UNCERTAINTY_EXPERIMENT.json'
HISTORY_COMMIT = '2f24d18'
RN1_HISTORY_COMMIT = '4d04595'
PROTOCOL_COMMIT = 'ad2c350'
DEPENDENCIES = ('src/reference_compiler', 'scripts',
    'experiments/relation_noise/model.py', 'experiments/relation_noise/run_experiment.py',
    'experiments/relation_noise/analyze_results.py',
    'experiments/prospective_relation/run.py', 'experiments/prospective_relation/analyze.py',
    'experiments/component_uncertainty/PROTOCOL.md',
    'experiments/component_uncertainty/study.py', 'experiments/component_uncertainty/run_study.py')


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT).decode('utf-8').rstrip('\r\n')


def historical():
    rows, references = {}, []
    for commit, path, kind in ((HISTORY_COMMIT, rn2_analysis.experiment.OUTPUT, 'FP'),
                              (RN1_HISTORY_COMMIT, rn1.OUTPUT, 'posterior')):
        relative = path.relative_to(ROOT).as_posix()
        retained = json.loads(git('show', commit+':'+relative))
        assert retained == json.loads(path.read_text(encoding='utf-8'))
        assert retained['status'] == 'COMPLETE_EXECUTION'
        selected = [r for r in retained['workers'] if r['kind'] == kind and tuple(r['case']) in diagnostic_cases()]
        assert len(selected) == 2
        for row in selected:
            case = tuple(row['case'])
            if kind == 'FP':
                assert row['worker_status'] == 'EXECUTED'
            else:
                # RN-1 predates the explicit worker-status field. Its
                # original bounded runner retained only successful jobs.
                job = row['completed_job']
                assert job['exit_code'] == 0 and not job['timed_out']
                assert job['attached_before_resume'] and not job['limit_terminated_processes']
            assert row['counts'] == json.loads(json.dumps(counts_from_training(case[0], data(case)[2])))
            rows[kind, case] = row
        references.append({'journal': relative, 'journal_commit': git('rev-parse', commit),
            'worker_source': retained['registration_source'], 'kind': kind, 'reused_cases': diagnostic_cases()})
    assert len({json.dumps(r['device'], sort_keys=True) for r in rows.values()}) == 1
    return rows, references


def configuration(case):
    # Registration depends only on support and length, never hidden bits or
    # realized labels. No component list is delivered to the proposal policy.
    n = case[0]
    edges = support(case)
    train_count = 10*len(edges)
    cfg, old, _, _, _ = rn1.fixture_parameters(n, groups=(0,)*n, edges=edges)
    run = rn1.online(cfg, train_count+n*n, unit=10, rate=F(0), grid=16)
    persistence = rn1.registration(bound=F(3), horizon=n*n)
    rules = tuple(replace(rule, rule_id='cuda', score_path=rn1.CUDA_PATH)
                  if rule.score_path == rn1.FLOAT64_PATH else rule for rule in persistence.rules)
    run = replace(run, searches=old.searches, float64=old.float64,
        persistence=replace(persistence, rules=rules),
        data=replace(run.data, stream_law=rn1.StochasticStreamLaw(
            'RN-3 external branch-invariant noise assumption; seeded tapes alone prove no stochastic premise')))
    policy = rn1.CudaCompilerPolicy((rn1.CudaCompilationStep(train_count, 'native', 1, 'ref', 'cuda'),))
    return cfg, run, policy


def fp_worker(case):
    n, law, seed = case
    hidden, edges, train, evaluation = data(case)
    cfg, online, policy = configuration(case)
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


def baseline_worker(case):
    n,law,seed = case
    hidden,edges,train,evaluation = data(case)
    # The learner below receives exactly this revealed training statistic.
    # Hidden bits are used only by scored(), after outputs have been captured.
    retained_training = tuple((context(n,i,j),label) for i,j,label in train)
    decoded_training = tuple((*decode_context(n,inputs),label) for inputs,label in retained_training)
    counts = counts_from_training(n,decoded_training)
    exact = posterior(n,counts,'iid' if law.startswith('iid') else law)
    maximum_bits = max(max(v.numerator.bit_length(),v.denominator.bit_length()) for row in exact.values() for v in row)
    assert maximum_bits <= 32768
    pairs = tuple((i,j) for i in range(n) for j in range(n))
    retained_queries = tuple(context(n,i,j) for i,j,_ in evaluation)
    queries = tuple(decode_context(n,inputs) for inputs in retained_queries)
    indices = tuple(i*n+j for i,j in queries)
    assert set(queries)==set(pairs) and len(queries)==len(pairs)
    words = []
    for pair in pairs:
        for value in exact[pair]:
            excess = 10*value-1
            word = HALF.rounded(excess)
            if HALF.decode(word)>excess:
                word -= 1
            assert 0 <= HALF.decode(word) <= excess
            if word+1 < HALF.infinity:
                assert HALF.decode(word+1)>excess
            words.append(word)
    import torch
    contract = cuda_contract()
    device = _CudaDevice(contract.device,0)
    identity = (torch.__version__,torch.version.git_version,torch.version.cuda,
                torch.cuda.get_device_name(0),torch.cuda.get_device_capability(0))
    assert identity == contract.execution_identity
    assert torch.cuda.memory_allocated()==0
    with torch.no_grad():
        half = torch.tensor([float(HALF.decode(w)) for w in words],dtype=torch.float16,device='cuda').reshape(n*n,2)
        addresses = torch.tensor(indices,dtype=torch.int64,device='cuda')
        selected = half.index_select(0,addresses)
        values = selected.to(torch.float32)
        masses = values+torch.ones_like(values)
        total = masses[:,0]+masses[:,1]
        p0,p1 = masses[:,0]/total,masses[:,1]/total
        torch.cuda.synchronize()
        actual_half = tuple(w & 0xffff for w in half.view(torch.int16).cpu().flatten().tolist())
        actual_selected = tuple(w & 0xffff for w in selected.view(torch.int16).cpu().flatten().tolist())
        actual_mass = masses.view(torch.int32).cpu().tolist()
        actual_total = total.view(torch.int32).cpu().tolist()
        actual_p0 = p0.view(torch.int32).cpu().tolist()
        actual_p1 = p1.view(torch.int32).cpu().tolist()
    assert actual_half == tuple(words)
    assert actual_selected == tuple(words[2*index+j] for index in indices for j in (0,1))
    normalized,raw = {},{}
    for index,pair in enumerate(queries):
        address = indices[index]
        expected_mass = tuple(SINGLE.rounded(1+HALF.decode(w)) for w in words[2*address:2*address+2])
        assert tuple(actual_mass[index]) == expected_mass
        decoded = tuple(SINGLE.decode(w) for w in expected_mass)
        expected_total = SINGLE.rounded(sum(decoded))
        assert actual_total[index] == expected_total
        assert sum(decoded)<=10 and SINGLE.decode(expected_total)<=10
        outputs = actual_p0[index],actual_p1[index]
        assert outputs == tuple(SINGLE.rounded(v/SINGLE.decode(expected_total)) for v in decoded)
        normalized[pair] = tuple(v/sum(decoded) for v in decoded)
        raw[pair] = tuple(SINGLE.decode(w) for w in outputs)
    peak, reserved = torch.cuda.max_memory_allocated(),torch.cuda.max_memory_reserved()
    assert peak <= 16 << 20 and reserved <= 32 << 20
    domain = unseen_pairs(n,edges)
    return {'kind':'posterior','case':case,'counts':counts,
        'prior':'independent fair token bits; registered conditioned or IID edge law',
        'exact_unseen':score(exact,hidden,domain),
        'AMP_unseen':scored(normalized,raw,hidden,domain),
        'exact_full_domain':score(exact,hidden,pairs),
        'AMP_full_domain':scored(normalized,raw,hidden,pairs),
        'complete_domain_raw_predictions_checked':n*n,
        'maximum_exact_integer_bits':maximum_bits,
        'maximum_AMP_mass_probability_error':str(max(abs(a-b) for pair in pairs for a,b in zip(normalized[pair],exact[pair]))),
        'resources':{'materialized_half_table_bytes':len(words)*2,
            'native_tensor_peak_bytes':peak,'native_allocator_peak_reserved_bytes':reserved},
        'device':device_record(device.snapshot(),identity),'process_id':os.getpid()}


def bounded(kind, case):
    with tempfile.TemporaryDirectory(prefix='fp-component-model-', dir=ROOT) as temporary:
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
    # No call to data(new_case): preflight must not inspect a target label.
    assert len(diagnostic_cases()) == 2 and len(new_cases()) == 8 and len(tasks()) == 18
    assert len(set(tasks())) == 18 and not set(diagnostic_cases()) & set(new_cases())
    for case in diagnostic_cases()+new_cases():
        cfg, online, policy = configuration(case)
        n = case[0]
        expected = 10*len(support(case))
        assert len(online.data.active.observation_ids) == expected+n*n
        assert cfg.initializer_pattern == (F(1), F(8)) and policy.steps[0].after_cursor == expected
        assert online.searches[0].relation_sources.solver == 'empirical-binary-relation-component-symmetry-v3'
        assert asdict(online.searches[0].grammar) == dict(nodes=2*n+n*n+2, SUMs=n*n+6,
            PRODUCTs=n*n+4, edges=4*n*n+2*n+12, slots=2)
    _, reference = historical()
    _, rn2_check = rn2_analysis.verify()
    assert not git('diff', PROTOCOL_COMMIT, '--', 'experiments/component_uncertainty/PROTOCOL.md')
    assert 'torch' not in sys.modules
    return {'new_workers': len(tasks()), 'previously_unexecuted_cases': len(new_cases()),
        'new_seed_labels_not_inspected': True, 'historical_control': reference,
        'historical_RN1_scores_checked': rn2_check['original_RN1_recomputed_score_records'],
        'historical_RN2_scores_checked': rn2_check['recomputed_new_score_records'],
        'historical_RN2_decisions_checked': rn2_check['recomputed_prospective_decisions']}


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
            result = fp_worker(case) if args.worker == 'FP' else baseline_worker(case)
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
        report = {'experiment': 'RN-3', 'status': 'PARTIAL_EXECUTION', 'registration_source': revision,
            'protocol_commit': git('rev-parse', PROTOCOL_COMMIT), 'historical_control': reference, 'workers': []}
    assert [(r['kind'], tuple(r['case'])) for r in report['workers']] == list(tasks()[:len(report['workers'])])
    for kind, case in tasks()[len(report['workers']):]:
        result = bounded(kind, case)
        if result['worker_status'] == 'EXECUTED':
            try:
                assert result['device'] == expected_device
                if case in diagnostic_cases():
                    assert result['counts'] == old['FP', case]['counts']
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
