"""Owned balanced readouts learn after equal initialized predictions; exact/CPU/AMP audit."""
import argparse
from dataclasses import asdict, replace
from fractions import Fraction as F
from itertools import product
import json
from math import prod
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import traceback
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts')]
from fp_reference.relation_proposal import RelationSourceSpec, relation_proposal
from fp_reference.native_search import GrammarLimits
from fp_reference.empirical_bound import empirical_upper
from fp_reference.resources import ResourceExceeded
from fp_reference.core import ContractError
from fp_reference.float64_bridge import Float64Contract
from audit_component_symmetry import (partitions, relative_assignments, observations,
    run_contract, runtime, ingest, HOST_CAP)
from audit_reference_acceleration import fixture_parameters, context
from audit_reference_events import forward_oracle
from audit_reference_construction import validate_residency, rejects
from audit_cuda_runtime import audit_snapshot
from audit_float64_runtime import replay
import audit_float64_runtime as cpu_audit
from audit_cuda_policy_run import host_record
from ingress_audit_support import deliver_context
from windows_job_audit_support import run_in_job

SOLVER = 'empirical-binary-relation-balanced-readout-v4'
CASES = ('adapt', 'opposite', 'incomplete', 'slots', 'tight', 'work')


def exact_audit():
    predictions = gradient_directions = transfers = models = 0
    for n in range(2, 6):
        cfg, old, _, _, _ = fixture_parameters(n)
        pattern = (F(1), F(8))+(F(1),)*(n*(n-1))
        grammar = GrammarLimits(2*n+n*n+2, 2, n*n, 4*n*n, len(pattern))
        registration = replace(old.searches[0].relation_sources, solver=SOLVER)
        rejects(lambda: replace(registration, solver='unregistered-solver'), ContractError)
        for partition in partitions(n):
            for h in relative_assignments(n, partition):
                edges = tuple((i, j) for vertices in partition for i, j in zip(vertices, vertices[1:])) or ((0, 0),)
                counts = tuple((i, j, 9-8*(h[i]^h[j]), 1+8*(h[i]^h[j])) for i, j in edges)
                upper = empirical_upper(observations(cfg, counts), cfg.semantics, bit_limit=32768)
                proposed = relation_proposal(upper, cfg.semantics, grammar, pattern, registration, bit_limit=32768)
                assert proposed.program is not None and proposed.scale == 8
                graph, theta = proposed.program, pattern[:proposed.program.slot_count]
                c = len(partition)
                component = {i: k for k, vertices in enumerate(partition) for i in vertices}
                pair_coordinates = {}
                counts_graph = graph.counts()
                assert tuple(counts_graph[k] for k in ('nodes', 'SUMs', 'PRODUCTs', 'edges')) == (
                    2*n+n*n+2, 2, n*n, 4*n*n-sum(len(v)**2 for v in partition))
                for i, j in product(range(n), repeat=2):
                    inputs = dict(zip((s.source_id for s in cfg.semantics.sources), context(n, i, j)))
                    p, gradients = forward_oracle(graph, cfg.semantics, theta, inputs)
                    cross = component[i] != component[j]
                    expected = (F(1, 2), F(1, 2)) if cross else (
                        (F(1, 10), F(9, 10)) if h[i]^h[j] else (F(9, 10), F(1, 10)))
                    assert p == expected
                    predictions += 1
                    if cross:
                        active = tuple(k for k, g in enumerate(gradients[0]) if g)
                        assert len(active) == 2 and 1 not in active
                        assert sorted(gradients[0][k] for k in active) == [F(-1, 4), F(1, 4)]
                        assert gradients[1] == tuple(-v for v in gradients[0])
                        pair = tuple(sorted((component[i], component[j])))
                        if pair in pair_coordinates:
                            assert active == pair_coordinates[pair]
                        else:
                            assert all(not set(active) & set(v) for v in pair_coordinates.values())
                            pair_coordinates[pair] = active
                        for label in (0, 1):
                            updated = tuple(max(F(0), v-g/8) for v, g in zip(theta, gradients[label]))
                            after, _ = forward_oracle(graph, cfg.semantics, updated, inputs)
                            assert after[label] == F(65, 128) and after[1-label] == F(63, 128)
                            transfers += 1
                        gradient_directions += 2
                    else:
                        parity = h[i]^h[j]
                        assert gradients[parity][1] == F(-1, 90)
                        assert gradients[1-parity][1] == F(1, 10)
                        assert all(not g for row in gradients for k, g in enumerate(row) if k != 1)
                models += 1
    # Exact selection must account for coefficients reserved by the chosen
    # scale. Otherwise an infeasible best scale hides a feasible alternative.
    cfg, old, _, _, _ = fixture_parameters(3)
    registration = replace(old.searches[0].relation_sources, solver=SOLVER)
    scale_cases = 0
    for a, b in product(range(11), repeat=2):
        counts = ((0, 1, a, 10-a), (1, 2, b, 10-b))
        upper = empirical_upper(observations(cfg, counts), cfg.semantics, bit_limit=32768)
        c = 1+int(a == 5)+int(b == 5)
        M, m = sum(max(x, 10-x) for x in (a, b) if x != 5), sum(min(x, 10-x) for x in (a, b) if x != 5)
        for slots in (2, 3, 4, 8):
            pattern = (F(1), F(8))+(F(1),)*6
            grammar = GrammarLimits(17, 2, 9, 36, slots)
            proposed = relation_proposal(upper, cfg.semantics, grammar, pattern, registration, bit_limit=32768)
            feasible = tuple(v for v in (F(1), F(8)) if slots-1-int(v == 1) >= c*(c-1))
            if not feasible:
                assert proposed.program is None
            else:
                scores = [((v+1)/(v+2))**M * (1/(v+2))**m for v in feasible]
                assert proposed.program is not None and proposed.scale == feasible[scores.index(max(scores))]
                theta = pattern[:proposed.program.slot_count]
                likelihood = prod(forward_oracle(proposed.program, cfg.semantics, theta, dict(row.sources))[0][row.target]
                    for row in observations(cfg, counts))
                assert likelihood == max(scores)*F(1, 2)**(10*((a == 5)+(b == 5))) <= upper.likelihood
            scale_cases += 1
    upper = empirical_upper(observations(cfg, ((0, 1, 9, 1), (1, 2, 9, 1))), cfg.semantics, bit_limit=32768)
    connected = relation_proposal(upper, cfg.semantics, GrammarLimits(17, 2, 9, 36, 1),
        (F(8),), registration, bit_limit=32768)
    assert connected.program is not None and connected.program.slot_count == 1
    assert 'torch' not in sys.modules
    return {'models': models, 'initialized_one_hot_predictions': predictions,
        'cross_label_gradient_directions': gradient_directions, 'exact_one_step_responses': transfers,
        'count_slot_feasibility_cases': scale_cases, 'no_internal_unit_needed_for_connected_graph': True}


def endpoint(path, case):
    cfg, old, _, train, _ = fixture_parameters(4, groups=(0,)*4, edges=((0, 1), (2, 3)))
    slots = 2 if case == 'slots' else 4
    grammar = replace(old.searches[0].grammar, slots=slots)
    cfg = replace(cfg, initializer_pattern=(F(1), F(8), F(1), F(1)), graph_limits=asdict(grammar),
        activation_cap=F(8 if case == 'tight' else 16), normalizer_cap=F(10 if case == 'tight' else 18))
    if case == 'incomplete':
        train = tuple((values, label ^ int(at == 8)) for at, (values, label) in enumerate(train))
    opposite = case == 'opposite'
    first_label = int(opposite)
    fresh = ((context(4, 0, 2), first_label), (context(4, 1, 3), first_label))+tuple(
        (context(4, i, j), int(opposite and i//2 != j//2)) for _ in range(4) for i, j in product(range(4), repeat=2))
    if case == 'tight':
        fresh = ((context(4, 0, 1), 0),)
    old = replace(old, searches=(replace(old.searches[0], grammar=grammar,
        relation_sources=replace(old.searches[0].relation_sources, solver=SOLVER)),))
    run = run_contract(cfg, old, len(train)+len(fresh), len(fresh), unit=1, rate=F(1, 8))
    # Floors can separate independently rounded learners by a grid quantum.
    # This declared tolerance is checked at every phase, not inferred from
    # the exact first update. Numerical uncertainty must still halt honestly.
    run = replace(run, float64=Float64Contract(F(1, 100), F(1, 100)))
    rt = runtime(cfg, run, path, (len(train),))
    if case == 'work':
        original = rt._event_router.charge_work
        checked = []
        def refuse(role, costs, note):
            if note.endswith(':empirical-upper-and-proposal'):
                expected = (4096+64*sum(map(len, rt._buffers.values()))
                    +64*len(cfg.initializer_pattern)*(len(train)+1)+64*4*4)
                assert costs == {'work': expected}
                checked.append(expected)
                raise ResourceExceeded('audit: quadratic proposal work unavailable')
            return original(role, costs, note)
        with patch.object(rt._event_router, 'charge_work', refuse):
            ingest(rt, train)
        assert len(checked) == 1
    else:
        ingest(rt, train)
    cutoff = validate_residency(rt)
    search, = cutoff.searches
    proposal = search.relation_proposal
    first_prediction = second_prediction = after_theta = None
    if case in ('slots', 'work'):
        assert not cutoff.reference_proofs and cutoff.alpha_spent == 0
        assert proposal is None if case == 'work' else proposal.program is None
        ingest(rt, fresh, start=len(train))
    else:
        assert proposal.program is not None and proposal.scale == 8
        assert len(proposal.components) == 2 and proposal.program.slot_count == 3
        assert cutoff.alpha_spent == F(1, 2)
        cid = search.best_candidate_id
        if case == 'tight':
            assert deliver_context(rt, f'observation-{len(train)}', fresh[0][0]).status == 'PREDICTED_REFERENCE'
            observed = rt.observe(fresh[0][1])
            assert observed.status == 'UNRESOLVED', observed
            assert rt.snapshot().halted is not None and not rt.snapshot().install_receipts
        else:
            for offset, (values, label) in enumerate(fresh):
                prediction = deliver_context(rt, f'observation-{len(train)+offset}', values)
                assert prediction.status == 'PREDICTED_REFERENCE', prediction
                p = dict(prediction.predictions)[cid]
                if offset == 0:
                    first_prediction = p
                    assert p == (F(1, 2), F(1, 2))
                elif offset == 1:
                    second_prediction = p
                    assert p[first_label] == F(65, 128) and p[1-first_label] == F(63, 128)
                assert rt.observe(label).status == 'OBSERVED_REFERENCE'
                if offset == 0:
                    after_theta = next(c.theta for c in rt.snapshot().candidates if c.candidate_id == cid)
                    assert after_theta == ((F(31, 32), F(8), F(33, 32)) if opposite else (F(33, 32), F(8), F(31, 32)))
    final = validate_residency(rt)
    if case != 'tight':
        assert final.run.status == ('SEALED_CUDA_STREAM' if path == 'cuda' else 'SEALED_REFERENCE_STREAM')
        decision, = final.run.closure.decisions
        assert decision.decision_status == ('UNRESOLVED' if case in ('slots', 'work', 'incomplete') else 'HISTORICAL_REFERENCE_CLASS_BOUNDED')
        if case in ('slots', 'work'):
            assert not final.install_receipts
        else:
            assert len(final.install_receipts) == 1
            assert final.install_receipts[0].attempt.proposal_proof_id == search.proof_id
    outcomes = {'adapt': 'owned balanced candidate learns cross labels and installs its continuous learner',
        'opposite': 'the same initial uncertainty learns the opposite revealed relation and installs',
        'incomplete': 'adaptive installation preserves the unresolved full training class',
        'slots': 'insufficient distinct initialized coefficients retain unresolved class and spend no alpha',
        'tight': 'nonzero within-component update violates the old tight range and halts without installation',
        'work': 'quadratic emission work is prepaid; refusal grants no proposal or evidence'}
    return rt, {'case': case, 'path': path, 'outcome': outcomes[case],
        'first_cross_prediction': None if first_prediction is None else list(map(str, first_prediction)),
        'after_first_cross_theta': None if after_theta is None else list(map(str, after_theta)),
        'next_cross_prediction': None if second_prediction is None else list(map(str, second_prediction)),
        'native_graph': None if proposal is None or proposal.program is None else proposal.program.counts(),
        'class_status': search.status, 'reference_proofs': len(final.reference_proofs),
        'alpha_spent': str(final.alpha_spent), 'install_cursors': [r.attempt.cursor for r in final.install_receipts],
        'halted': final.halted}


def worker(path, case):
    rt, result = endpoint(path, case)
    cpu = replay(rt)[0]
    cuda = audit_snapshot(rt) if path == 'cuda' else None
    assert cuda is None or cuda['phases'] == cpu
    final = rt.snapshot()
    if case == 'tight':
        # The replay must reject promoting checked but unsafe staged values
        # into the published root merely because they are the latest traces.
        latest = {trace.candidate_id: trace for trace in final.float64_traces}
        fake = replace(final, candidates=tuple(replace(candidate,
            learner=latest[candidate.candidate_id].reference, float64=latest[candidate.candidate_id].float64)
            for candidate in final.candidates))
        with patch.object(cpu_audit, 'owned', return_value=fake):
            rejects(lambda: replay(rt), AssertionError)
        result['unpublished_successors_replayed_and_false_publication_rejected'] = True
    errors = lambda traces: {field: str(max((getattr(t.relation, field) for t in traces if t.relation is not None), default=F(0)))
        for field in ('state_error', 'native_error', 'normalizer_error', 'probability_error', 'division_error')}
    result['float64_relation_maxima'] = errors(final.float64_traces)
    if path == 'cuda':
        result['CUDA_relation_maxima'] = errors(final.cuda.phases)
    result.update(binary64_phases=cpu, CUDA=cuda, run_status=final.run.status,
        host=host_record(final), peak_packed_bytes=final.resources['peak']['reference_payload_bytes'], process_id=os.getpid(),
        device=None if final.cuda is None else {'identity': asdict(final.cuda.device.identity),
            'physical_vram_upper': final.cuda.device.physical_vram_upper, 'scope': final.cuda.device.scope},
        execution_identity=None if final.cuda is None else final.cuda.contract.execution_identity)
    return result


def bounded(path, case):
    with tempfile.TemporaryDirectory(prefix='fp-balanced-audit-', dir=ROOT) as temporary:
        assert Path(temporary).resolve().parent == ROOT
        output = Path(temporary)/'result.json'
        job = run_in_job(__file__, ('--worker', '--path', path, '--case', case, '--output', output),
            commit_limit=HOST_CAP, timeout_ms=1200000)
        assert job.exit_code == 0 and not job.timed_out, (case, job, output.read_text(encoding='utf-8') if output.exists() else '')
        assert output.stat().st_size <= 16384
        result = json.loads(output.read_text(encoding='utf-8'))
        assert result['process_id'] == job.process_id and job.attached_before_resume
        assert max(job.peak_process_commit, job.peak_job_commit) <= HOST_CAP and not job.limit_terminated_processes
        host = result['host']
        assert (host['process_id'], host['creation_100ns']) == (job.process_id, job.process_creation_100ns)
        assert host['lifetime_process_commit_peak'] <= job.peak_process_commit
        return dict(result, completed_job=asdict(job))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exact', action='store_true')
    parser.add_argument('--path', choices=('cpu', 'cuda'), default='cpu')
    parser.add_argument('--case', choices=CASES)
    parser.add_argument('--worker', action='store_true')
    parser.add_argument('--output')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    if args.exact:
        assert not (args.worker or args.case or args.output or args.write)
        print(json.dumps(exact_audit(), indent=2))
        return
    if args.worker:
        assert args.case and args.output and not args.write
        try:
            result = worker(args.path, args.case)
        except Exception:
            Path(args.output).write_text(traceback.format_exc()[-16384:], encoding='utf-8')
            raise
        Path(args.output).write_text(json.dumps(result), encoding='utf-8')
        return
    assert not args.output and (not args.write or args.case is None)
    source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    if args.write:
        assert not subprocess.check_output(['git', 'diff', 'HEAD', '--', 'src', 'scripts'], cwd=ROOT)
    report = {'source_revision': source, 'exact': exact_audit() if args.case is None else None, 'workers': []}
    for case in CASES if args.case is None else (args.case,):
        result = bounded(args.path, case)
        if report['workers']:
            assert result['device'] == report['workers'][0]['device']
            assert result['execution_identity'] == report['workers'][0]['execution_identity']
        report['workers'].append(result)
        print(args.path+' '+case+': '+result['outcome'], flush=True)
    if args.write:
        output = ROOT/'evidence/minimal'/('FP_BALANCED_UNCERTAINTY_'+args.path.upper()+'_AUDIT.json')
        output.write_text(json.dumps(report, indent=1)+'\n', encoding='utf-8')
    print(json.dumps({'workers': len(report['workers']),
        'binary64_phases': sum(r['binary64_phases'] for r in report['workers']), 'exact': report['exact']}, indent=2))


if __name__ == '__main__':
    main()
