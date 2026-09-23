"""CPU fault checks of the shared model reader; no actual CUDA claim."""
from dataclasses import replace
from fractions import Fraction as F
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts'),
               str(ROOT/'experiments/joint_uncertainty')]
from fp_reference import ReferenceCompilerRuntime, CompilerPolicy, indexed_amp as amp, projected_amp
from fp_reference import histogram_decoder as hist, histogram_amp
from fp_reference.cuda_prefix import IndexedCudaPhase
from fp_reference.float64_bridge import Float64Contract
from fp_reference.indexed_count import commit
from audit_owned_histogram import BUDGET, operations
from audit_indexed_source_binding import predict
from audit_indexed_runtime import fixture
from audit_reference_construction import rejects
import run_indexed_model as model

TAPE = ((0, 1, 0), (1, 2, 1), (0, 2, 0))


def fixture_snapshot(kind):
    cfg, schema, online = fixture(3, 3)
    cfg = replace(cfg, indexed_histogram=BUDGET if kind == 'histogram' else None)
    rt = ReferenceCompilerRuntime(cfg, schema, online=online, policy=CompilerPolicy(()))
    for i, j, target in TAPE:
        assert predict(rt, schema, (i, j)).status == 'PREDICTED_REFERENCE'
        assert rt.observe(target).status == 'OBSERVED_REFERENCE'
    snapshot = rt.snapshot()
    tolerance = Float64Contract(F(1, 100), F(1, 1000))
    phases = []
    current = amp.IndexedAmpState(snapshot.event_traces[0].before.encoded)
    def append(kind, trace, reference, raw, *, prediction=None, arithmetic=None, plan=None,
               input_id=None, prediction_id=None):
        identity = 'passive-reader-phase:'+str(len(phases))
        relation = (amp.check_prediction(trace.prediction, prediction, tolerance,
            normalizer_cap=F(18), activation_cap=F(8), bit_limit=32768) if kind == 'predict'
            else amp.check_state(reference, raw, tolerance, bit_limit=32768))
        tape = () if arithmetic is None else operations(arithmetic)
        phases.append(IndexedCudaPhase(identity, snapshot.deployed_id, schema.program_id,
            ('construction:' if kind == 'initialize' else 'ordinary:')+kind,
            reference.cursor, None if trace is None else trace.observation_id,
            input_id, prediction_id, reference, None if trace is None else trace.prediction,
            raw, prediction, tape, relation,
            plan.output_cells if kind == 'predict' else 13 if kind == 'observe' else 0,
            None, 'CHECKED_CUDA_PREFIX_PHASE', '', len(tape) if kind == 'predict' else 0,
            execution_plan=plan))
        return identity
    current_id = append('initialize', None, snapshot.event_traces[0].before, current)
    planner = histogram_amp if kind == 'histogram' else projected_amp if kind == 'projected' else amp
    kernel = histogram_amp if kind == 'histogram' else amp
    for trace, (i, j, target) in zip(snapshot.event_traces, TAPE):
        if kind == 'histogram':
            plan = hist.passive_plan(current.encoded, (i, j), BUDGET)
        else:
            plan = planner._prepare_prediction(schema, current, schema.rules(), schema.source_row(i*3+j),
                                              output_cap=model.CELLS)
        arithmetic = amp._Arithmetic(32768)
        prediction, _ = kernel._prediction_schedule(plan, current, arithmetic)
        prediction_id = append('predict', trace, trace.before, current, prediction=prediction,
            arithmetic=arithmetic, plan=plan, input_id=current_id)
        arithmetic = amp._Arithmetic(32768)
        observed, _ = amp._observation_schedule(current, prediction, target, arithmetic)
        observed_id = append('observe', trace, trace.after_observe, observed, arithmetic=arithmetic,
                             input_id=current_id, prediction_id=prediction_id)
        current = amp.IndexedAmpState(commit(observed.encoded))
        current_id = append('commit', trace, trace.after_commit, current, input_id=observed_id)
    contract = SimpleNamespace(histogram=BUDGET if kind == 'histogram' else None,
                               order_search=False, forward_id=planner.FORWARD_ID)
    return replace(snapshot, cuda=SimpleNamespace(contract=contract, phases=tuple(phases)))


def audit():
    result = {'status': 'PASS_HISTOGRAM_MODEL_READER_CPU',
        'scope': 'passive rounded records attached to real reference histories; no actual device evidence',
        'paths': []}
    with patch.object(model, 'data', lambda case: (None, None, TAPE, ())):
        for kind in ('global', 'projected', 'histogram'):
            snapshot = fixture_snapshot(kind)
            mode = 'global' if kind == 'histogram' else kind
            checked = model.audit_prefix(snapshot, (3, 'reader-fixture', 0), mode)
            assert checked['checked_CUDA_phases'] == 10 and checked['native_committed_units'] == 3
            result['paths'].append({'kind': kind, 'phases': 10})
            if kind != 'histogram':
                continue
            position = next(i for i, p in enumerate(snapshot.cuda.phases) if p.phase == 'ordinary:predict')
            phase = snapshot.cuda.phases[position]
            plan = phase.execution_plan
            k, h = plan.terms[0][0]
            changes = (
                replace(phase, execution_plan=replace(plan, terms=(((k, h+1),)+plan.terms[0][1:], plan.terms[1]))),
                replace(phase, raw_prediction=replace(phase.raw_prediction,
                    words=phase.raw_prediction.words[:5]+(phase.raw_prediction.words[5]^1,)+phase.raw_prediction.words[6:])),
                replace(phase, raw_operations=phase.raw_operations[:-1]))
            for changed in changes:
                rows = snapshot.cuda.phases[:position]+(changed,)+snapshot.cuda.phases[position+1:]
                malformed = replace(snapshot, cuda=SimpleNamespace(contract=snapshot.cuda.contract, phases=rows))
                rejects(lambda: model.audit_prefix(malformed, (3, 'reader-fixture', 0), mode))
            result['histogram_coefficient_endpoint_and_trace_refusals'] = len(changes)
    assert 'torch' not in sys.modules
    return result


if __name__ == '__main__':
    report = audit()
    print(json.dumps(report, indent=2))
