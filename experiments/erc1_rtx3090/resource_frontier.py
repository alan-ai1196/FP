"""Preregistered known-table ERC-1 resource/precision experiment on RTX 3090."""
import argparse
import ast
from dataclasses import asdict, replace
from fractions import Fraction as F
import json
from math import ceil, lcm
from pathlib import Path
import subprocess
import sys
import tempfile
import traceback

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts'),
               str(ROOT/'theory/numerical_checks')]

from fp_reference import ReferenceCompilerRuntime, CudaCompilerPolicy
from fp_reference.float64_bridge import Float64Contract
from fp_reference.host_resources import HostResourceContract
from fp_reference.machine import pack
from audit_cuda_learner import model_initial, model_predict, model_observe, model_commit, SINGLE, HALF
from audit_cuda_policy_run import owned, host_record
from audit_cuda_runtime import cuda_contract, raw_model, raw_model_prediction
from audit_float64_runtime import cpu_initial, cpu_predict, cpu_observe, cpu_commit, same_state, same_prediction
from audit_reference_construction import contract, domain, limits, translate
from audit_reference_events import online, forward_oracle
from dyadic_cap_total_complexity_audit import primitive_row, singleton_bank, classify
from ingress_audit_support import deliver_context
from node_edge_precision_accuracy_audit import check_native, shared_reciprocal_graph
from normalizer_slack_decoder_audit import dyadic_scale
from source_intersection_product_audit import binary_tables, evaluate_tables
from two_product_support_border_audit import add_sum
from windows_job_audit_support import run_in_job

HOST_CAP = 4 << 30
PATTERN = (F(1, 2), F(1), F(2))
TABLES = {'scalar': ((F(5, 8), F(3, 8)),)*2,
          'mixed': ((F(1, 4), F(3, 8), F(3, 8)), (F(1, 4), F(1, 3), F(5, 12)))}
LEVELS = (4, 8, 16, 24, 32)
METHODS = ('horner', 'fractional-horner', 'reciprocal',
           'exact-horner', 'exact-fractional-horner', 'repaired-reciprocal')


def configurations():
    return tuple((target, method, depth) for target in TABLES for method in METHODS
                 for depth in (LEVELS if method in METHODS[:2] else
                               (1, 2, 3, 4, 5) if method == 'reciprocal' else
                               (1, 2, 3, 4) if target == 'scalar' else (2, 3, 4, 5)))


def fractional_scale(nodes, source, coefficient):
    """Positive fractional Horner; all registered coefficients are in [0,1]."""
    coefficient = F(coefficient)
    assert 0 <= coefficient <= 1 and not coefficient.denominator & (coefficient.denominator-1)
    if coefficient == 1:
        return source
    if not coefficient:
        return add_sum(nodes, ())
    current = None
    for position in range(coefficient.denominator.bit_length()-1):
        terms = [] if current is None else [(current, F(1, 2))]
        if (coefficient.numerator >> position) & 1:
            terms.append((source, F(1, 2)))
        if terms:
            current = add_sum(nodes, terms)
    assert current is not None
    return current


def singleton_graph(masses, fractional):
    nodes, indicators = singleton_bank(1)
    heads = []
    scale = fractional_scale if fractional else dyadic_scale
    for column in zip(*masses):
        groups = {}
        for parent, value in zip(indicators, column):
            if value > 1:
                groups.setdefault(value-1, []).append(parent)
        terms = []
        for coefficient, parents in sorted(groups.items()):
            source = parents[0] if len(parents) == 1 else add_sum(nodes, ((p, 1) for p in parents))
            terms.append(source if coefficient == 1 else scale(nodes, source, coefficient))
        heads.append(terms[0] if len(terms) == 1 else add_sum(nodes, ((p, 1) for p in terms)))
    return nodes, heads


def build(target, method, depth):
    goal = TABLES[target]
    critical = max(1/min(row) for row in goal)
    exact = method.startswith('exact-') or method == 'repaired-reciprocal'
    common = lcm(*((q/min(row)-1).denominator for row in goal for q in row))
    cap = critical+(critical*(common-1)*F(1, 4)**(2**depth) if exact else 0)
    assert 0 <= cap-critical <= 1
    if 'reciprocal' in method:
        nodes, heads, _ = shared_reciprocal_graph(1, goal, cap, depth, exact=exact)
    else:
        if exact:
            assert classify(1, goal, cap)['status'] == 'EXACT_LOCAL'
            masses = []
            for row in goal:
                integer = primitive_row(row)
                bits = 0
                while True:
                    scale = F(ceil(F(2**bits, min(integer))), 2**bits)
                    if scale*sum(integer) <= cap:
                        break
                    bits += 1
                masses.append(tuple(scale*a for a in integer))
        else:
            masses = tuple(tuple(1+F(int((q/min(row)-1)*2**depth), 2**depth) for q in row) for row in goal)
        nodes, heads = singleton_graph(masses, 'fractional' in method)
    report = check_native(1, nodes, heads, goal, cap, exact=exact)
    graph = translate(nodes, heads, PATTERN)
    assert graph.counts()['edges'] == report['edges']
    cfg = replace(contract(1, len(goal[0]), cap=cap, peak=max(F(1), cap-len(goal[0]))),
                  reference_integer_bits=32768, limits=limits(byte_cap=1 << 30, work_cap=10**13))
    for x, sources in enumerate(domain(1)):
        p, gradients, values = forward_oracle(graph, cfg.semantics, PATTERN,
            dict(zip((s.source_id for s in cfg.semantics.sources), sources)), return_values=True)
        assert p == report['probabilities'][x]
        assert values == tuple(row[x] for row in report['values'])
        assert all(len(row) == 3 for row in gradients)
    tape = tuple((x, label) for x, row in enumerate(goal)
                 for label, count in enumerate(primitive_row(row)) for _ in range(count))
    run = replace(online(cfg, len(tape), unit=2, rate=F(0), grid=16),
                  float64=Float64Contract(F(1, 1 << 24), F(1, 1 << 24)))
    return cfg, graph, run, tape, report


def preflight():
    for numerator in range(257):
        nodes, _ = singleton_bank(1)
        head = fractional_scale(nodes, 0, F(numerator, 256))
        values = evaluate_tables(nodes, binary_tables(1))
        assert values[head] == (F(numerator, 256), F(0))
        assert all(0 <= v <= 1 for row in values for v in row)
    cases = configurations()
    assert len(cases) == 54 and len(set(cases)) == 54
    maximum_nodes = 0
    for case in cases:
        cfg, graph, run, tape, exact = build(*case)
        assert len(tape) == (16 if case[0] == 'scalar' else 20)
        assert run.data.stream_law == 'declared-exogenous-no-probability-guarantee'
        counts = graph.counts()
        assert all(counts[key] <= value for key, value in cfg.graph_limits.items())
        maximum_nodes = max(maximum_nodes, counts['nodes'])
    assert 'torch' not in sys.modules
    return {'exact_configurations': len(cases), 'fractional_coefficients_checked': 257,
            'maximum_nodes': maximum_nodes,
            'no_Torch_import': True}


def observations(state):
    rows = {row.observation_id: row for row in state.observations}
    if state.pending is not None:
        rows.setdefault(state.pending.record.observation_id, state.pending.record)
    return rows


def replay_cuda(rt, state):
    """Check raw complete outputs even at a failed bridge, without promoting it."""
    graphs, rows, buffers = dict(state.programs), observations(state), dict(state.buffers)
    expected, checked, failed = {}, 0, 0
    admission_only, largest_attempted_frame = 0, 0
    state_error = F(0)
    for record in state.cuda.phases:
        assert record.status in ('CHECKED_CUDA_PREFIX_PHASE', 'UNRESOLVED'), record
        assert not failed, 'no continuation is planned after a failed CUDA phase'
        graph, kind = graphs[record.program_id], record.phase.split(':')[1]
        before = None if record.input_phase is None else expected[record.input_phase]
        if kind == 'initialize':
            result = model_initial(graph, rt.contract.semantics, record.reference.theta, record.reference.cursor)
        elif kind == 'predict':
            result = model_predict(graph, rt.contract.semantics, before, dict(rows[record.observation_id].sources))
            assert record.raw_prediction == raw_model_prediction(result)
            assert record.raw_state == raw_model(before)
        elif kind == 'observe':
            result = model_observe(graph, before, expected[record.prediction_phase], rows[record.observation_id].target)
        else:
            assert kind == 'commit'
            result = model_commit(before, rt.online_contract.learner)
        if kind != 'predict':
            assert record.raw_state == raw_model(result)
        expected[record.object_id] = result
        frame = buffers[record.object_id]
        size = int.from_bytes(frame[:8], 'big')
        if frame[8:8+size] != pack(record):
            assert record.status == 'UNRESOLVED' and 'CUDA evidence retention failed: ' in record.reason
            assert frame[8:8+size] == pack((record.object_id, 'ADMITTED_CUDA_PHASE'))
            prior = record.reason.split('; CUDA evidence retention failed: ')[0]
            assert not prior or prior.startswith('ArithmeticUnresolved:')
            attempted = replace(record, reason=prior,
                status='UNRESOLVED' if prior else 'CHECKED_CUDA_PREFIX_PHASE')
            attempted_size = len(pack(attempted))+8
            assert attempted_size > len(frame)
            admission_only += 1
        else:
            attempted_size = size+8
        largest_attempted_frame = max(largest_attempted_frame, attempted_size)
        assert not any(frame[8+size:])
        assert len(frame) == state.cuda.contract.phase_evidence_bytes
        raw = record.raw_state
        assert raw is not None
        state_error = max(state_error, *(abs(SINGLE.decode(a)-b) for words, values in
            ((raw[0], record.reference.theta), (raw[2], record.reference.gradient_sum))
            for a, b in zip(words, values)))
        if record.status == 'CHECKED_CUDA_PREFIX_PHASE':
            assert record.relation is not None
            checked += 1
        else:
            assert record.reason
            failed += 1
    for cid, phase in state.cuda.current:
        candidate = next(c for c in state.candidates if c.candidate_id == cid)
        actual = expected[phase]
        assert (actual.cursor, actual.unit, actual.steps) == (
            candidate.learner.cursor, candidate.learner.unit_count, candidate.learner.optimizer_steps)
    storage = state.cuda.storage
    assert storage['native_allocation_counter_current'] == storage['native_allocation_counter_at_binding'] == (1, 16 << 20, 1)
    return {'checked': checked, 'failed_complete_outputs_replayed': failed,
            'admission_only_frames': admission_only,
            'largest_attempted_phase_frame_bytes': largest_attempted_frame,
            'max_complete_state_error_including_failure': str(state_error)}


def replay_cpu(rt, state):
    graphs, rows = dict(state.programs), observations(state)
    current, predictions = {}, {}
    checked, failed = 0, 0
    for trace in state.float64_traces:
        assert trace.status in ('CHECKED_FLOAT64_PHASE', 'UNRESOLVED'), trace
        graph, kind, cid = graphs[trace.program_id], trace.phase.split(':')[1], trace.candidate_id
        if kind == 'initialize':
            result = cpu_initial(graph, rt.contract.semantics, PATTERN, trace.ordinary_cursor)
        elif kind == 'predict':
            prediction = cpu_predict(graph, rt.contract.semantics, current[cid], dict(rows[trace.observation_id].sources))
            predictions[cid] = prediction
            same_prediction(trace.float64_prediction, prediction)
            result = current[cid]
        elif kind == 'observe':
            result = cpu_observe(graph, current[cid], predictions[cid], rows[trace.observation_id].target)
        else:
            assert kind == 'commit'
            result = cpu_commit(current[cid], rt.online_contract.learner)
        same_state(trace.float64, result)
        current[cid] = result
        if trace.status == 'CHECKED_FLOAT64_PHASE':
            checked += 1
        else:
            failed += 1
    # A CUDA failure can leave checked CPU staged outputs unpublished.
    # Do not confuse the replay's last staged output with the current learner.
    return {'checked': checked, 'failed_complete_outputs_replayed': failed}


def reference_events(rt, state):
    graphs, rows = dict(state.programs), observations(state)
    for event in state.event_traces:
        probabilities, gradients = forward_oracle(graphs[event.program_id], rt.contract.semantics,
            event.before.theta, dict(rows[event.observation_id].sources))
        assert event.prediction.probabilities == probabilities
        gradient = gradients[rows[event.observation_id].target]
        assert event.after_observe.gradient_sum == tuple(a+b for a, b in zip(event.before.gradient_sum, gradient))
        assert event.after_observe.theta == PATTERN
        if event.after_commit is not None:
            assert event.after_commit.theta == PATTERN and not any(event.after_commit.gradient_sum)
    return len(state.event_traces)


def prediction_metrics(state, target):
    rows, retained, statuses = observations(state), {}, {}
    minimum, underflows = None, 0
    for phase in state.cuda.phases:
        if phase.raw_prediction is None:
            continue
        x = domain(1).index(tuple(value for _, value in rows[phase.observation_id].sources))
        raw = phase.raw_prediction
        if x in retained:
            assert retained[x] == raw
        retained[x], statuses[x] = raw, phase.status
        values = tuple(HALF.decode(word) for word in raw[0])
        positive = [v for v in values if v > 0]
        minimum = min([minimum] + positive) if minimum is not None else min(positive)
        underflows += sum(a > 0 and b == 0 for a, b in zip(phase.reference_prediction.values, values))
    complete = (state.run.status == 'SEALED_CUDA_STREAM' and set(retained) == {0, 1}
                and all(s == 'CHECKED_CUDA_PREFIX_PHASE' for s in statuses.values()))
    errors, outputs = [], []
    for x, raw in sorted(retained.items()):
        masses = tuple(SINGLE.decode(w) for w in raw[3])
        total = sum(masses)
        rounded = tuple(SINGLE.decode(w) for w in raw[5])
        q = TABLES[target][x]
        a = max(abs(m/total-p) for m, p in zip(masses, q))
        b = max(abs(v-p) for v, p in zip(rounded, q))
        errors.append((a, b))
        outputs.append({'context': x, 'status': statuses[x], 'mass_words': raw[3],
            'normalizer_word': raw[4][0], 'prediction_words': raw[5],
            'mathematical_mass_error': str(a), 'rounded_prediction_error': str(b)})
    return {'complete_checked_context_domain': complete,
        'mathematical_mass_error': str(max(e[0] for e in errors)) if complete else None,
        'rounded_prediction_error': str(max(e[1] for e in errors)) if complete else None,
        'minimum_positive_activation': None if minimum is None else str(minimum),
        'positive_reference_to_zero_occurrences': underflows, 'retained_contexts': outputs}


def worker(case):
    cfg, graph, run, tape, exact = build(*case)
    rt = ReferenceCompilerRuntime(cfg, graph, online=run, policy=CudaCompilerPolicy(()),
        cuda=cuda_contract(), host=HostResourceContract(HOST_CAP, {'deployment': HOST_CAP, 'compiler': HOST_CAP}))
    endpoint_failure = None
    for cursor, (x, target) in enumerate(tape):
        predicted = deliver_context(rt, f'observation-{cursor}', domain(1)[x])
        if predicted.status != 'PREDICTED_REFERENCE':
            assert predicted.status == 'UNRESOLVED', predicted
            endpoint_failure = ('predict', cursor, predicted.reason)
            break
        observed = rt.observe(target)
        if observed.status != 'OBSERVED_REFERENCE':
            assert observed.status == 'UNRESOLVED', observed
            endpoint_failure = ('observe', cursor, observed.reason)
            break
    state = owned(rt)
    sealed = state.run.status == 'SEALED_CUDA_STREAM'
    if sealed:
        assert endpoint_failure is None and state.halted is None and state.cursor == len(tape)
        counts = [[0]*len(TABLES[case[0]][0]) for _ in range(2)]
        for row in state.observations:
            x = domain(1).index(tuple(v for _, v in row.sources))
            counts[x][row.target] += 1
        assert tuple(tuple(F(v, sum(row)) for v in row) for row in counts) == TABLES[case[0]]
    else:
        assert endpoint_failure is not None and state.run.closure is None
    assert not state.install_receipts and not state.reference_proofs and state.alpha_spent == 0
    checked_cuda, checked_cpu = replay_cuda(rt, state), replay_cpu(rt, state)
    device = state.cuda.device
    positive = [v for row in exact['values'] for v in row if v]
    return {'case': case, 'cap': str(cfg.normalizer_cap), 'native': graph.counts(),
        'reference': {'error': str(exact['error']), 'minimum_positive_activation': str(min(positive)),
            'maximum_significand_bits': exact['maximum_significand_bits'],
            'direct_materialization_bits': exact['direct_bit_volume'],
            'probabilities_included_bits': exact['including_rational_predictions_bits']},
        'run_status': state.run.status, 'cursor': state.cursor, 'endpoint_failure': endpoint_failure,
        'cuda': checked_cuda, 'binary64': checked_cpu,
        'independent_reference_events': reference_events(rt, state),
        'predictions': prediction_metrics(state, case[0]),
        'resources': {'peak_packed_bytes': state.resources['peak']['reference_payload_bytes'],
            'consumed_native_arena_extent': state.cuda.storage['consumed_arena_extent'],
            'largest_phase_frame_used': max(int.from_bytes(dict(state.buffers)[p.object_id][:8], 'big')+8 for p in state.cuda.phases),
            'maximum_output_cells': max(p.output_cells for p in state.cuda.phases)},
        'device': {'identity': asdict(device.identity), 'physical_vram_upper': device.physical_vram_upper,
                   'role_physical_vram_upper': dict(device.role_physical_vram_upper), 'scope': device.scope},
        'host': host_record(state)}


def bounded(case):
    with tempfile.TemporaryDirectory(prefix='fp-erc1-rtx3090-', dir=ROOT) as temporary:
        assert Path(temporary).resolve().parent == ROOT
        output = Path(temporary)/'result.json'
        job = run_in_job(__file__, ('--case', *map(str, case), '--worker-output', output),
                         commit_limit=HOST_CAP, timeout_ms=600000)
        assert job.exit_code == 0 and not job.timed_out, (job, output.read_text()[:8192] if output.exists() else '')
        raw = output.read_bytes()
        assert len(raw) <= 8192
        result = json.loads(raw)
        host = result['host']
        assert (host['process_id'], host['creation_100ns']) == (job.process_id, job.process_creation_100ns)
        assert job.attached_before_resume and host['lifetime_process_commit_peak'] <= job.peak_process_commit <= HOST_CAP
        assert job.peak_job_commit <= HOST_CAP
        return dict(result, completed_job=asdict(job))


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).rstrip('\r\n')


def unchanged_registration(revision):
    # A report/replay bug may be corrected without discarding completed
    # science. Preserve each execution source; never change its experiment.
    assert not git('diff', revision, 'HEAD', '--', 'src', 'scripts', 'theory/numerical_checks',
                   'experiments/erc1_rtx3090/README.md')
    old = git('show', revision+':experiments/erc1_rtx3090/resource_frontier.py')
    def science(source):
        return [ast.dump(node) for node in ast.parse(source).body
                if isinstance(node, ast.Assign) or isinstance(node, ast.FunctionDef)
                and node.name in ('configurations', 'fractional_scale', 'singleton_graph', 'build')]
    assert science(old) == science(Path(__file__).read_text(encoding='utf-8'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preflight', action='store_true')
    parser.add_argument('--case', nargs=3)
    parser.add_argument('--worker-output')
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args()
    if args.preflight:
        assert not (args.case or args.worker_output or args.write or args.resume)
        print(json.dumps(preflight(), indent=2))
        return
    case = (args.case[0], args.case[1], int(args.case[2])) if args.case else None
    assert case is None or case in configurations()
    if args.worker_output:
        assert case is not None and not args.write
        try:
            result = worker(case)
        except Exception:
            Path(args.worker_output).write_text(traceback.format_exc()[-8192:], encoding='utf-8')
            raise
        Path(args.worker_output).write_text(json.dumps(result), encoding='utf-8')
        return
    output = ROOT/'evidence/minimal/FP_ERC1_RTX3090_FRONTIER.json'
    allowed = output.relative_to(ROOT).as_posix()
    def clean():
        assert all(line[3:] == allowed for line in git('status', '--porcelain', '--untracked-files=all').splitlines()), (
            'commit the protocol and code before execution')
    clean()
    revision = git('rev-parse', 'HEAD')
    rows = []
    registration = revision
    device = None
    if args.resume:
        assert args.write and case is None
        previous = json.loads(output.read_text(encoding='utf-8'))
        assert previous['execution_status'] == 'PARTIAL_EXECUTION'
        registration = previous['registration_source']
        unchanged_registration(registration)
        rows, device = previous['results'], previous['common_actual_device']
        assert [tuple(row['case']) for row in rows] == list(configurations()[:len(rows)])
    elif args.write:
        assert case is None and not output.exists(), 'use --resume only for an incomplete recorded run'
    for key in ((case,) if case else configurations())[len(rows):]:
        result = bounded(key)
        actual = result.pop('device')
        if device is None:
            device = actual
        assert actual == device
        rows.append(dict(result, execution_source=revision))
        clean()
        assert git('rev-parse', 'HEAD') == revision
        if args.write:
            report = {'experiment': 'ERC1-RTX3090-1', 'registration_source': registration,
                'execution_status': 'COMPLETE_EXECUTION' if len(rows) == 54 else 'PARTIAL_EXECUTION',
                'scope': 'registered known-table fixed-initializer Programs; no class-optimality or population claim',
                'executed_configurations': len(rows), 'common_actual_device': device, 'results': rows}
            output.write_text(json.dumps(report, indent=1)+'\n', encoding='utf-8')
        print(' '.join(map(str, key))+' '+result['run_status'], flush=True)
    print(json.dumps({'executed': len(rows), 'sealed': sum(r['run_status'] == 'SEALED_CUDA_STREAM' for r in rows),
                      'source': revision}, indent=2))


if __name__ == '__main__':
    main()
