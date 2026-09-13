"""Native component-average endpoints; no full-state or unrestricted-input equivalence."""
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
import types

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts')]
from fp_reference.data_usage import ObservationRecord
from fp_reference.empirical_bound import empirical_upper
from fp_reference.native_search import GrammarLimits
from fp_reference.relation_proposal import RelationSourceSpec, relation_proposal
from fp_reference.semantics import ArithmeticUnresolved
from fp_reference import ReferenceCompilerRuntime, CompilerPolicy, CompilationStep, CudaCompilerPolicy, CudaCompilationStep
from fp_reference.cuda_installation import CudaInstallContract
from fp_reference.host_resources import HostResourceContract
from fp_reference.persistence import CUDA_PATH, FLOAT64_PATH
from audit_reference_acceleration import fixture_parameters, context
from audit_reference_events import forward_oracle, online
from audit_reference_construction import rejects, validate_residency, zero_program
from audit_paired_cpu_persistence import registration as persistence_registration
from audit_cuda_runtime import cuda_contract, audit_snapshot
from audit_cuda_policy_run import host_record
from audit_float64_runtime import replay
from ingress_audit_support import deliver_context
from windows_job_audit_support import run_in_job

LEGACY = '2f24d18'
HOST_CAP = 4 << 30
CASES = ('disconnected', 'tied', 'scale1', 'grammar', 'zero-future', 'uniform-future')


def partitions(n):
    def visit(labels):
        if len(labels) == n:
            yield tuple(tuple(i for i, value in enumerate(labels) if value == k)
                        for k in range(max(labels)+1))
            return
        for group in range(max(labels)+2):
            yield from visit(labels+(group,))
    yield from visit((0,))


def relative_assignments(n, partition):
    roots = {vertices[0] for vertices in partition}
    free = tuple(i for i in range(n) if i not in roots)
    for bits in product((0, 1), repeat=len(free)):
        h = [0]*n
        for i, bit in zip(free, bits):
            h[i] = bit
        yield tuple(h)


def observations(cfg, counts):
    n = len(cfg.semantics.sources)//2
    result = []
    for i, j, c0, c1 in counts:
        values = context(n, i, j)
        sources = tuple((s.source_id, v) for s, v in zip(cfg.semantics.sources, values))
        for y, count in enumerate((c0, c1)):
            for _ in range(count):
                at = len(result)
                result.append(ObservationRecord(f'o{at}', 'train', 'train', at, values, sources, y))
    return tuple(result)


def limits(n):
    # This explicit audit grammar admits all c<=n witnesses. Actual Runtime
    # fixtures also test refusal under their smaller registered grammar.
    return GrammarLimits(10*n+2, 4*n+2, 4*n, 14*n, 3)


def frozen_forward(proposal, cfg, pattern, values):
    return forward_oracle(proposal.program, cfg.semantics, pattern[:proposal.program.slot_count],
        dict(zip((s.source_id for s in cfg.semantics.sources), values)))[0]


def hard_prediction(assignment, i, j, scale):
    high, low = (scale+1)/(scale+2), 1/(scale+2)
    return (low, high) if assignment[i] ^ assignment[j] else (high, low)


def legacy_module():
    name = 'fp_reference._component_audit_legacy'
    module = types.ModuleType(name)
    module.__package__ = 'fp_reference'
    sys.modules[name] = module
    source = subprocess.check_output(['git', 'show', LEGACY+':src/reference_compiler/fp_reference/relation_proposal.py'], cwd=ROOT)
    exec(compile(source, '<canonical Git '+LEGACY+' relation proposer>', 'exec'), module.__dict__)
    return module


def orbit_audit():
    legacy = legacy_module()
    partitions_checked = models = predictions = briers = legacy_matches = 0
    for n in range(2, 6):
        cfg, run, _, _, _ = fixture_parameters(n)
        registration = run.searches[0].relation_sources
        for partition in partitions(n):
            partitions_checked += 1
            for h in relative_assignments(n, partition):
                edges = tuple((i, j) for vertices in partition for i, j in zip(vertices, vertices[1:])) or ((0, 0),)
                counts = tuple((i, j, 9-8*(h[i]^h[j]), 1+8*(h[i]^h[j])) for i, j in edges)
                records = observations(cfg, counts)
                upper = empirical_upper(records, cfg.semantics, bit_limit=32768)
                proposal = relation_proposal(upper, cfg.semantics, limits(n), cfg.initializer_pattern,
                    registration, bit_limit=32768)
                reversed_proposal = relation_proposal(upper, cfg.semantics, limits(n), cfg.initializer_pattern,
                    RelationSourceSpec(registration.token_atoms[::-1]), bit_limit=32768)
                assert proposal.program is not None and proposal.scale == 8
                assert proposal.assignment == h
                assert {frozenset(c) for c in proposal.components} == {frozenset(c) for c in partition}
                c = len(partition)
                graph = proposal.program.counts()
                assert tuple(graph[k] for k in ('nodes', 'SUMs', 'PRODUCTs', 'edges', 'slots')) == (2*n+8*c+2, 4*c+2, 4*c, 2*n+12*c, 2)
                if c == 1:
                    previous = legacy.relation_proposal(upper, cfg.semantics, limits(n), cfg.initializer_pattern,
                        legacy.RelationSourceSpec(registration.token_atoms), bit_limit=32768)
                    assert proposal.program == previous.program
                    legacy_matches += 1
                family = []
                for flips in product((0, 1), repeat=c):
                    assignment = list(h)
                    for vertices, flip in zip(partition, flips):
                        for i in vertices:
                            assignment[i] ^= flip
                    family.append(assignment)
                for i, j in product(range(n), repeat=2):
                    rows = tuple(hard_prediction(assignment, i, j, F(8)) for assignment in family)
                    averaged = tuple(sum((row[y] for row in rows), F(0))/len(rows) for y in (0, 1))
                    actual = frozen_forward(proposal, cfg, cfg.initializer_pattern, context(n, i, j))
                    assert actual == averaged
                    assert actual == frozen_forward(reversed_proposal, cfg, cfg.initializer_pattern, context(n, i, j))
                    for y in (0, 1):
                        loss = sum((actual[k]-int(y == k))**2 for k in (0, 1))
                        average_loss = sum(sum((row[k]-int(y == k))**2 for k in (0, 1)) for row in rows)/len(rows)
                        assert loss <= average_loss
                        briers += 1
                    predictions += 1
                models += 1
    del sys.modules[legacy.__name__]
    assert (partitions_checked, models, predictions, briers, legacy_matches) == (74, 320, 7320, 14640, 30)
    return {'partitions': partitions_checked, 'relative_assignments': models,
        'exact_orbit_average_and_reversed_presentation_predictions': predictions,
        'exact_labelwise_Brier_inequalities': briers, 'connected_graphs_identical_to_v2': legacy_matches,
        'legacy_source': LEGACY}


def scale_audit():
    cfg, run, _, _, _ = fixture_parameters(3)
    checked = 0
    for zeroes in product(range(11), repeat=2):
        records = observations(cfg, tuple((i, i+1, c, 10-c) for i, c in enumerate(zeroes)))
        upper = empirical_upper(records, cfg.semantics, bit_limit=32768)
        # Enumerate all parity assignments satisfying only strict evidence;
        # no reuse of the producer's component extraction or likelihood code.
        family = tuple(h for h in product((0, 1), repeat=3)
            if all(c == 5 or (h[i]^h[i+1]) == int(c < 5) for i, c in enumerate(zeroes)))
        for pattern, slots in (((F(1), F(8)), 2), ((F(1), F(7)), 2),
                               ((F(0), F(1), F(8)), 3), ((F(1), F(8), F(1)), 3), ((F(1), F(8)), 1)):
            values, scores = [], []
            for scale in pattern[:slots]:
                prediction = {(i, j): tuple(sum((hard_prediction(h, i, j, scale)[y] for h in family), F(0))/len(family)
                    for y in (0, 1)) for i, j in product(range(3), repeat=2)}
                values.append(prediction)
                scores.append(prod(prediction[i, i+1][0]**c * prediction[i, i+1][1]**(10-c) for i, c in enumerate(zeroes)))
            proposal = relation_proposal(upper, cfg.semantics, replace(limits(3), slots=slots), pattern,
                run.searches[0].relation_sources, bit_limit=32768)
            assert proposal.program is not None
            best = scores.index(max(scores))
            assert proposal.scale == pattern[best]
            actual = prod(frozen_forward(proposal, cfg, pattern, row.inputs)[row.target] for row in records)
            assert actual == max(scores) <= upper.likelihood
            for pair, expected in values[best].items():
                assert frozen_forward(proposal, cfg, pattern, context(3, *pair)) == expected
            checked += 1
    records = observations(cfg, ((0, 1, 10, 0), (1, 2, 10, 0)))
    upper = empirical_upper(records, cfg.semantics, bit_limit=32768)
    rejects(lambda: relation_proposal(upper, cfg.semantics, limits(3), (F(1), F(8)),
        run.searches[0].relation_sources, bit_limit=8), ArithmeticUnresolved)
    # A balanced chord inside a connected component still changes this
    # constructor's empirical scale likelihood; it cannot be discarded.
    records = observations(cfg, ((0, 1, 9, 1), (1, 2, 9, 1), (0, 2, 5, 5)))
    upper = empirical_upper(records, cfg.semantics, bit_limit=32768)
    proposal = relation_proposal(upper, cfg.semantics, limits(3), cfg.initializer_pattern,
        run.searches[0].relation_sources, bit_limit=32768)
    assert len(proposal.components) == 1 and proposal.scale == 1
    actual = prod(frozen_forward(proposal, cfg, cfg.initializer_pattern, row.inputs)[row.target] for row in records)
    assert actual == F(2, 3)**23*F(1, 3)**7 > F(9, 10)**23*F(1, 10)**7
    assert relation_proposal(upper, cfg.semantics, limits(3), (F(2), F(8)),
        run.searches[0].relation_sources, bit_limit=32768).program is None
    records = observations(cfg, ((0, 1, 9, 1), (1, 2, 9, 1), (0, 2, 1, 9)))
    upper = empirical_upper(records, cfg.semantics, bit_limit=32768)
    assert relation_proposal(upper, cfg.semantics, limits(3), cfg.initializer_pattern,
        run.searches[0].relation_sources, bit_limit=32768).program is None
    assert checked == 605
    return {'count_initializer_slot_cases': checked, 'finite_integer_refusal': True,
        'within_component_balanced_chord_changes_selected_scale': True,
        'absent_unit_and_inconsistent_cycle_refused': True}


def scope_audit():
    cfg, run, _, _, _ = fixture_parameters(2)
    records = observations(cfg, ((0, 0, 9, 1),))
    upper = empirical_upper(records, cfg.semantics, bit_limit=32768)
    proposal = relation_proposal(upper, cfg.semantics, limits(2), cfg.initializer_pattern,
        run.searches[0].relation_sources, bit_limit=32768)
    assert len(proposal.components) == 2 and proposal.scale == 8
    soft = (F(1), F(0), F(1, 2), F(1, 2))
    actual = frozen_forward(proposal, cfg, cfg.initializer_pattern, soft)
    assert actual == (F(5, 6), F(1, 6))
    # Each hard representative has the same normalizer10 at this soft point.
    hard = []
    for h in product((0, 1), repeat=2):
        mass = tuple(1+8*sum(soft[i]*soft[2+j] for i, j in product(range(2), repeat=2) if h[i]^h[j] == y)
                     for y in (0, 1))
        assert sum(mass) == 10
        hard.append(tuple(v/sum(mass) for v in mass))
    average = tuple(sum(row[y] for row in hard)/len(hard) for y in (0, 1))
    assert average == (F(7, 10), F(3, 10)) and average != actual
    # Opposite directed rows are only pooled by the heuristic. Their original
    # distinction must survive in the independent categorical upper.
    records = observations(cfg, ((0, 1, 9, 1), (1, 0, 1, 9)))
    upper = empirical_upper(records, cfg.semantics, bit_limit=32768)
    proposal = relation_proposal(upper, cfg.semantics, limits(2), cfg.initializer_pattern,
        run.searches[0].relation_sources, bit_limit=32768)
    likelihood = prod(frozen_forward(proposal, cfg, cfg.initializer_pattern, row.inputs)[row.target] for row in records)
    assert len(upper.cells) == 2 and likelihood == F(1, 2)**20 < upper.likelihood
    return {'soft_input_component_prediction': list(map(str, actual)),
        'soft_input_true_orbit_average': list(map(str, average)),
        'directed_information_is_retained_in_the_full_upper': True}


def exact_audit():
    result = {'orbit': orbit_audit(), 'scale': scale_audit(), 'scope': scope_audit()}
    assert 'torch' not in sys.modules
    return result


def run_contract(cfg, old, count, horizon, *, unit=10, rate=F(0)):
    run = online(cfg, count, unit=unit, rate=rate, grid=16)
    return replace(run, searches=old.searches, float64=old.float64,
        cpu_install=old.cpu_install, persistence=persistence_registration(bound=F(3), horizon=horizon),
        data=replace(run.data, stream_law=old.data.stream_law))


def runtime(cfg, run, path, steps, initial=None):
    if not steps:
        run = replace(run, cpu_install=None)
    if path == 'cuda':
        rules = tuple(replace(r, rule_id='cuda', score_path=CUDA_PATH) if r.score_path == FLOAT64_PATH else r
                      for r in run.persistence.rules)
        run = replace(run, persistence=replace(run.persistence, rules=rules), cpu_install=None)
        policy = CudaCompilerPolicy(tuple(CudaCompilationStep(at, 'native', 1, 'ref', 'cuda') for at in steps))
        cuda = cuda_contract(install=CudaInstallContract() if steps else None)
    else:
        policy = CompilerPolicy(tuple(CompilationStep(at, 'native', 1, 'ref', 'finite') for at in steps))
        cuda = None
    return ReferenceCompilerRuntime(cfg, zero_program(2) if initial is None else initial,
        online=run, policy=policy, cuda=cuda,
        host=HostResourceContract(HOST_CAP, {'deployment': HOST_CAP, 'compiler': HOST_CAP}))


def ingest(rt, tape, *, start=0):
    for at, (values, label) in enumerate(tape, start):
        prediction = deliver_context(rt, f'observation-{at}', values)
        assert prediction.status == 'PREDICTED_REFERENCE', prediction
        observed = rt.observe(label)
        assert observed.status == 'OBSERVED_REFERENCE', observed


def endpoint(path, case):
    edges = ((0, 1),) if case == 'grammar' else ((0, 1), (1, 2), (2, 3)) if case == 'tied' else ((0, 1), (2, 3))
    cfg, old, _, train, _ = fixture_parameters(4, groups=(0, 0, 0, 0), edges=edges)
    if case == 'tied':
        train = tuple((values, at % 2 if 10 <= at < 20 else label) for at, (values, label) in enumerate(train))
    elif case == 'scale1':
        train = tuple((values, int(at % 10 >= 6)) for at, (values, _) in enumerate(train))
    fresh = tuple((context(4, i, j), 0) for _ in range(4) for i, j in product(range(4), repeat=2))
    run = run_contract(cfg, old, len(train)+len(fresh), len(fresh))
    rt = runtime(cfg, run, path, (len(train),))
    ingest(rt, train)
    cutoff = validate_residency(rt)
    search, = cutoff.searches
    proposal = search.relation_proposal
    assert proposal is not None and len(cutoff.observations) == len(train)
    if case == 'grammar':
        assert proposal.program is None and len(proposal.components) == 3
        assert search.status == 'UNRESOLVED' and not cutoff.reference_proofs and cutoff.alpha_spent == 0
    else:
        assert proposal.program is not None and len(proposal.components) == 2
        assert proposal.scale == (1 if case == 'scale1' else 8)
        assert search.status == ('UNRESOLVED' if case == 'scale1' else 'REFERENCE_CLASS_BOUNDED')
        assert cutoff.alpha_spent == F(1, 2)
        graph = proposal.program
        theta = cfg.initializer_pattern[:graph.slot_count]
        for i, j in product(range(4), repeat=2):
            p, _ = forward_oracle(graph, cfg.semantics, theta,
                dict(zip((s.source_id for s in cfg.semantics.sources), context(4, i, j))))
            expected = (F(1, 2), F(1, 2)) if i//2 != j//2 else hard_prediction((0,)*4, i, j, proposal.scale)
            assert p == expected
    ingest(rt, fresh, start=len(train))
    final = validate_residency(rt)
    assert final.run.status == ('SEALED_CUDA_STREAM' if path == 'cuda' else 'SEALED_REFERENCE_STREAM')
    decision, = final.run.closure.decisions
    if case == 'grammar':
        assert not final.install_receipts and decision.decision_status == 'UNRESOLVED'
        outcome = 'uncompressed witness exceeds the unchanged native grammar; no proposal, alpha or false class exclusion'
    else:
        assert len(final.install_receipts) == 1
        assert final.install_receipts[0].attempt.proposal_proof_id == search.proof_id
        assert decision.decision_status == ('UNRESOLVED' if case == 'scale1' else 'HISTORICAL_REFERENCE_CLASS_BOUNDED')
        outcome = 'component candidate installs after its own continuous paired evidence; original class scope retained'
    return rt, {'outcome': outcome, 'components': proposal.components, 'scale': str(proposal.scale),
        'native_graph': None if proposal.program is None else proposal.program.counts(),
        'class_status': decision.decision_status,
        'install_cursors': [r.attempt.cursor for r in final.install_receipts], 'alpha_spent': str(final.alpha_spent)}


def future_endpoint(path, case):
    cfg, old, _, _, _ = fixture_parameters(2)
    cfg = replace(cfg, initializer_pattern=(F(0), F(1)), graph_limits=asdict(limits(2)))
    rows = observations(cfg, ((0, 1, 5, 5),))
    upper = empirical_upper(rows, cfg.semantics, bit_limit=32768)
    proposal = relation_proposal(upper, cfg.semantics, limits(2), cfg.initializer_pattern,
        old.searches[0].relation_sources, bit_limit=32768)
    assert proposal.program is not None and proposal.scale == 0
    initial = proposal.program if case == 'zero-future' else zero_program(2)
    run = replace(run_contract(cfg, old, 2, 2, unit=1, rate=F(1, 8)), searches=())
    rt = runtime(cfg, run, path, (), initial)
    initial_state = rt.snapshot().candidates[0]
    prediction = deliver_context(rt, 'observation-0', context(2, 0, 0))
    assert dict(prediction.predictions)[initial_state.candidate_id] == (F(1, 2), F(1, 2))
    assert rt.observe(0).status == 'OBSERVED_REFERENCE'
    state = rt.snapshot().candidates[0]
    expected = (F(17, 33), F(16, 33)) if case == 'zero-future' else (F(1, 2), F(1, 2))
    assert state.theta == ((F(1, 16), F(1)) if case == 'zero-future' else ())
    prediction = deliver_context(rt, 'observation-1', context(2, 0, 0))
    assert dict(prediction.predictions)[state.candidate_id] == expected
    assert rt.observe(0).status == 'OBSERVED_REFERENCE'
    final = validate_residency(rt)
    assert final.run.status == ('SEALED_CUDA_STREAM' if path == 'cuda' else 'SEALED_REFERENCE_STREAM')
    assert final.alpha_spent == 0 and not final.reference_proofs and not final.install_receipts
    return rt, {'outcome': 'equal initialized predictions diverge after a legal observed update' if case == 'zero-future' else
        'the zero-slot comparator remains uniform under the same legal continuation',
        'initial_prediction': ['1/2', '1/2'], 'after_one_update': list(map(str, expected)),
        'theta_after_one_update': list(map(str, state.theta))}


def worker(path, case):
    rt, result = future_endpoint(path, case) if case.endswith('-future') else endpoint(path, case)
    cpu = replay(rt)[0]
    cuda = audit_snapshot(rt) if path == 'cuda' else None
    assert cuda is None or cuda['phases'] == cpu
    final = rt.snapshot()
    result.update(path=path, case=case, binary64_phases=cpu, CUDA=cuda,
        run_status=final.run.status, host=host_record(final),
        peak_packed_bytes=final.resources['peak']['reference_payload_bytes'], process_id=os.getpid(),
        device=None if final.cuda is None else {'identity': asdict(final.cuda.device.identity),
            'physical_vram_upper': final.cuda.device.physical_vram_upper, 'scope': final.cuda.device.scope},
        execution_identity=None if final.cuda is None else final.cuda.contract.execution_identity)
    return result


def bounded(path, case):
    with tempfile.TemporaryDirectory(prefix='fp-component-audit-', dir=ROOT) as temporary:
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
        output = ROOT/'evidence/minimal'/('FP_COMPONENT_SYMMETRY_'+args.path.upper()+'_AUDIT.json')
        output.write_text(json.dumps(report, indent=1)+'\n', encoding='utf-8')
    print(json.dumps({'workers': len(report['workers']),
        'binary64_phases': sum(r['binary64_phases'] for r in report['workers']), 'exact': report['exact']}, indent=2))


if __name__ == '__main__':
    main()
