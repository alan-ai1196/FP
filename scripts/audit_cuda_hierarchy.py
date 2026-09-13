"""The existing noisy token hierarchy on the owned RTX 3090 AMP path.

The broad native class, empirical upper and identifiability controls are
unchanged. A successful finite protocol is not a population-science result.
"""
import argparse
from dataclasses import asdict, replace
from fractions import Fraction as F
from itertools import product
import json
from pathlib import Path
import sys
import tempfile
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts')]

from fp_reference import ReferenceCompilerRuntime, CudaCompilerPolicy, CudaCompilationStep
from fp_reference.cuda_installation import CudaInstallContract
from fp_reference.host_resources import HostResourceContract
from fp_reference.persistence import CUDA_PATH, FLOAT64_PATH
from fp_reference.program import Program, Source, Sum, Term
from fp_reference.proof import BoundedReferenceProof
from audit_cuda_policy_run import owned, forbidden, host_record
from audit_cuda_runtime import cuda_contract, audit_snapshot
from audit_float64_runtime import replay
from audit_reference_acceleration import fixture_parameters, context, ingest
from audit_reference_construction import validate_residency, zero_program
from audit_reference_events import forward_oracle
from windows_job_audit_support import run_in_job

HOST_CAP = 4 << 30
CASES = ('hierarchy', 'wrong-majority', 'disconnected-a', 'disconnected-b', 'sum-tie')


def make(n, case):
    groups, edges = None, None
    if case == 'wrong-majority':
        groups = (0, 1, 0, 1)
    elif case.startswith('disconnected-'):
        groups = (0, 1, 0, 1) if case.endswith('a') else (0, 1, 1, 0)
        edges = ((0, 1), (2, 3))
    cfg, run, hidden, train, fresh = fixture_parameters(n, groups=groups, edges=edges)
    rules = tuple(replace(rule, rule_id='cuda', score_path=CUDA_PATH)
        if rule.score_path == FLOAT64_PATH else rule for rule in run.persistence.rules)
    run = replace(run, persistence=replace(run.persistence, rules=rules), cpu_install=None)
    policy = None if case == 'sum-tie' else CudaCompilerPolicy((
        CudaCompilationStep(len(train), 'native', 1, 'ref', 'cuda'),))
    rt = ReferenceCompilerRuntime(cfg, zero_program(2), online=run,
        host=HostResourceContract(HOST_CAP, {role: HOST_CAP for role in ('deployment', 'compiler')}),
        cuda=cuda_contract(install=CudaInstallContract()), policy=policy)
    return rt, hidden, train, fresh


def selection(state):
    session, proof = state.searches[0], state.reference_proofs[0]
    assert type(proof) is BoundedReferenceProof and proof.evaluated_programs == 1
    assert session.status == 'REFERENCE_CLASS_BOUNDED'
    assert not session.cursor.done and session.cursor.emitted == 0 and len(session.rows) == 1
    candidate = next(row for row in state.candidates if row.candidate_id == proof.winner_lineage_id)
    graph = dict(state.programs)[candidate.program_id]
    return session, proof, candidate, graph


def checked_result(rt, state):
    cuda = audit_snapshot(rt)
    device = state.cuda.device
    return {'independent_CUDA': cuda, 'independent_binary64_phases': replay(rt)[0],
        'resources': {'peak_reference_payload_bytes': state.resources['peak']['reference_payload_bytes'],
            'consumed_native_arena_extent': state.cuda.storage['consumed_arena_extent'],
            'native_allocator_reserved_bytes': state.cuda.storage['actual_allocator_reserved_bytes'],
            'device': {'identity': asdict(device.identity),
                'physical_vram_upper': device.physical_vram_upper,
                'role_physical_vram_upper': dict(device.role_physical_vram_upper), 'scope': device.scope}},
        'host': host_record(state)}


def hierarchy(n, case):
    rt, hidden, train, fresh = make(n, case)
    tape = tuple((values, target ^ int(i < 10)) for i, (values, target) in enumerate(train)) if case == 'wrong-majority' else train
    ingest(rt, tape)
    initial = owned(rt)
    stage = initial.compiler_policy.state.stages[0]
    assert stage.status == 'EVIDENCE', (stage, [(i.status, i.reason) for i in initial.persistence_identities])
    session, proof, candidate, graph = selection(initial)
    proposal = session.relation_proposal
    assert len(proposal.components) == (2 if case.startswith('disconnected-') else 1)
    domain_checked = 0
    for i, j in product(range(n), repeat=2):
        sources = {spec.source_id: value for spec, value in zip(rt.contract.semantics.sources, context(n, i, j))}
        probabilities, _ = forward_oracle(graph, rt.contract.semantics, candidate.theta, sources)
        label = proposal.assignment[i] ^ proposal.assignment[j]
        assert probabilities[label] == F(9, 10)
        if case == 'hierarchy':
            assert label == hidden[i] ^ hidden[j]
        domain_checked += 1
    ingest(rt, fresh, start=len(train))
    final = owned(rt)
    assert final.halted is None and final.run.status == 'SEALED_CUDA_STREAM'
    assert final.cursor == 2*len(train)+2 and final.alpha_spent == F(1, 2)
    assert final.run.closure.decisions[0].decision_status == 'HISTORICAL_REFERENCE_CLASS_BOUNDED'
    if case == 'wrong-majority':
        assert proposal.assignment != hidden and not final.install_receipts
        assert all(i.status == 'UNRESOLVED' for i in final.persistence_identities)
        assert final.compiler_policy.state.stages[0].status == 'UNRESOLVED'
    else:
        assert [r.attempt.cursor for r in final.install_receipts] == [len(train)+20]
        assert final.compiler_policy.state.stages[0].status == 'INSTALLED_CUDA'
    syntax_lower = (2*n)**session.spec.grammar.nodes
    assert syntax_lower > rt.contract.limits.role_cumulative['compiler']['work']
    result = {'tokens': n, 'ordinary_training_events': len(train),
        'optimizer_update_unit': rt.online_contract.learner.update_unit,
        'complete_domain_reference_predictions_checked': domain_checked,
        'native_graph': graph.counts(), 'full_native_class_caps': asdict(session.spec.grammar),
        'source_only_class_cardinality_at_least_power_of_two': syntax_lower.bit_length()-1,
        'actually_evaluated_native_witnesses': 1, 'unexecuted_syntax_cursor_not_declared_exhausted': True,
        'install_cursors': [r.attempt.cursor for r in final.install_receipts],
        'sealed_at': final.cursor, 'partial_optimizer_events': final.run.closure.partial_optimizer_events,
        'stage_status': final.compiler_policy.state.stages[0].status,
        'alpha_spent': str(final.alpha_spent), 'sealed_port_denials': forbidden(rt, sealed=True)}
    if case.startswith('disconnected-'):
        # These small complete fields permit direct equality across workers;
        # no digest substitutes for the observational-equivalence witness.
        result['observable_result'] = {'ordinary_labels': [target for _, target in train+fresh],
            'assignment': proposal.assignment, 'components': proposal.components,
            'train_likelihood': str(proof.best_likelihood), 'graph': asdict(graph)}
        result['external_unseen_relation_0_2'] = hidden[0] ^ hidden[2]
    return dict(result, **checked_result(rt, final))


def sum_tie():
    rt, _, train, _ = make(4, 'sum-tie')
    ingest(rt, train)
    started = rt.start_reference_search('native')
    result = rt.advance_reference_search(started.search_id, transitions=1)
    assert result.status == 'REFERENCE_CLASS_BOUNDED'
    initial = validate_residency(rt)
    session, proof, candidate, graph = selection(initial)
    # Derive the left-token labels from the actual training counts. Hidden
    # task bits supply neither this graph nor the hierarchy's proposal.
    counts = {}
    for values, label in train:
        left = values[:4].index(F(1))
        counts.setdefault(left, [0, 0])[label] += 1
    lefts = tuple(sorted(counts))
    majorities = {left: int(counts[left][1] > counts[left][0]) for left in lefts}
    assert all(sorted(counts[left]) == [1, 9] for left in lefts)
    nodes = [Source(f'p0:t{left}') for left in lefts]
    heads = []
    for label in range(2):
        heads.append(len(nodes))
        nodes.append(Sum('mass', tuple(Term(i, 1) for i, left in enumerate(lefts) if majorities[left] == label)))
    cheaper = Program(tuple(nodes), 2, tuple(heads))
    assert session.spec.grammar.admits(cheaper)
    built = rt.construct_candidate(cheaper)
    assert built.status == 'BUILT_REFERENCE', built
    exact_score = F(1)
    for values, label in train:
        sources = {spec.source_id: value for spec, value in zip(rt.contract.semantics.sources, values)}
        a, _ = forward_oracle(graph, rt.contract.semantics, candidate.theta, sources)
        b, _ = forward_oracle(cheaper, rt.contract.semantics, (F(1), F(8)), sources)
        assert a == b
        exact_score *= b[label]
    assert exact_score == proof.best_likelihood
    assert cheaper.counts()['PRODUCTs'] == 0 and cheaper.counts()['nodes'] < graph.counts()['nodes']
    # Repeat the revealed train contexts as subsequent ordinary events so
    # both retained actual device learners execute the comparison. No GPU
    # evaluator bypass or borrowed historical forecast supplies these words.
    ingest(rt, train+train[:2], start=len(train))
    final = validate_residency(rt)
    predictions = {}
    for phase in final.cuda.phases:
        if phase.raw_prediction is not None and phase.ordinary_cursor >= len(train):
            predictions[phase.candidate_id, phase.ordinary_cursor] = phase.raw_prediction[5]
    comparisons = 0
    for cursor in range(len(train), 2*len(train)):
        assert predictions[candidate.candidate_id, cursor] == predictions[built.candidate_id, cursor]
        comparisons += 1
    assert final.halted is None and final.run.status == 'MANUAL_PARTIAL'
    assert not final.install_receipts and final.alpha_spent == 0
    return {'actual_AMP_train_context_probability_equalities': comparisons,
        'exact_reference_train_likelihood_tied': True, 'hierarchy': graph.counts(), 'SUM_only': cheaper.counts(),
        'scope': 'smaller training-optimal control, not a strong population SUM comparator or an owned policy run',
        **checked_result(rt, final)}


def bounded(case, n):
    with tempfile.TemporaryDirectory(prefix='fp-cuda-hierarchy-', dir=ROOT) as temporary:
        assert Path(temporary).resolve().parent == ROOT
        output = Path(temporary)/'result.json'
        job = run_in_job(__file__, ('--case', case, '--size', str(n), '--worker-output', output),
            commit_limit=HOST_CAP, timeout_ms=1800000)
        assert job.exit_code == 0 and not job.timed_out, (job, output.read_text()[:8192] if output.exists() else '')
        raw = output.read_bytes()
        assert len(raw) <= 8192
        result = json.loads(raw)
        host = result['host']
        assert (host['process_id'], host['creation_100ns']) == (job.process_id, job.process_creation_100ns)
        assert job.attached_before_resume and host['lifetime_process_commit_peak'] <= job.peak_process_commit <= HOST_CAP
        assert job.peak_job_commit <= HOST_CAP
        return dict(result, completed_job=asdict(job))


def report_results(results):
    report = {'status': 'PASS', 'scope': 'existing hierarchical fixture and negative controls on actual owned AMP',
        'cases': results, 'not_claimed': ['population identification', 'resource-forced unique hierarchy',
            'a deterministic tape proves stochastic freshness', 'target release or model-science authority']}
    if set(results) == set(CASES):
        a, b = results['disconnected-a'], results['disconnected-b']
        assert a['observable_result'] == b['observable_result']
        assert a['external_unseen_relation_0_2'] != b['external_unseen_relation_0_2']
        common = a.pop('observable_result')
        b.pop('observable_result')
        report['disconnected_witness'] = {
            'identical_observable_data_proposal_graph_and_train_objective': True,
            'shared_assignment': common['assignment'], 'components': common['components'],
            'opposite_external_unseen_relations': [a['external_unseen_relation_0_2'], b['external_unseen_relation_0_2']]}
    # Equality is checked before discarding repeated report fields. All
    # actual worker identities and separate resource peaks remain below.
    devices = [row['resources'].pop('device') for row in results.values()]
    assert devices and all(value == devices[0] for value in devices)
    report['common_actual_device'] = devices[0]
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', choices=CASES)
    parser.add_argument('--size', type=int, default=32)
    parser.add_argument('--worker-output')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    if args.worker_output:
        assert args.case and not args.write
        try:
            result = sum_tie() if args.case == 'sum-tie' else hierarchy(args.size, args.case)
        except Exception:
            Path(args.worker_output).write_text(traceback.format_exc()[-8192:], encoding='utf-8')
            raise
        Path(args.worker_output).write_text(json.dumps(result), encoding='utf-8')
        return
    results = {}
    for case in (args.case,) if args.case else CASES:
        results[case] = bounded(case, args.size if case == 'hierarchy' else 4)
        print(case+' PASS', flush=True)
    report = report_results(results)
    if args.write:
        assert args.case is None and args.size == 32
        (ROOT/'evidence/minimal/FP_CUDA_HIERARCHY_AUDIT.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
