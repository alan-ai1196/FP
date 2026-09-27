"""CPU reproduction of a public-snapshot write into owned reporting bounds.

Runs the real Runtime/phase/reporting/retention logic, substituting only the
device binding, arena checks and array backend. No CUDA authority is claimed.
"""
from collections.abc import Mapping
from contextlib import contextmanager
from dataclasses import replace
from decimal import Decimal, localcontext
from fractions import Fraction as F
from pathlib import Path
from types import FunctionType, MappingProxyType, SimpleNamespace
from unittest.mock import patch
import argparse
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts'), str(ROOT/'experiments/next_token')]
from audit_token_reporting import report_registration, train
from audit_token_cuda_owner import cuda_contract
from audit_reference_construction import limits
from audit_shared_token_retention import STORAGE
from fp_reference import ReferenceCompilerRuntime
from fp_reference import runtime, token_cuda_prefix as execution, token_reporting
from fp_reference.cuda_prefix import _CudaPrefix
from fp_reference.encoding import pack
from fp_reference.token_arrays import CPUArrays
from fp_reference.token_array_events import Kernel
from fp_reference.shared_reference import decoded_buffer

LEGACY = 'a7d2232'


@contextmanager
def legacy_implementation():
    """Reproduce the old value-container/consumer code, not a GPU job."""
    def method(module, attribute):
        relative = 'src/reference_compiler/fp_reference/'+module.__name__.split('.')[-1]+'.py'
        source = subprocess.check_output(['git', 'show', LEGACY+':'+relative], cwd=ROOT).decode('utf-8')
        namespace = dict(__name__=module.__name__, __package__=module.__package__)
        exec(compile(source, LEGACY+':'+relative, 'exec'), namespace)
        original = namespace[attribute]
        value = FunctionType(original.__code__, module.__dict__, attribute, original.__defaults__)
        value.__kwdefaults__ = original.__kwdefaults__
        return value
    with patch.object(execution, 'execute', method(execution, 'execute')), \
            patch.object(token_reporting, '_observe', method(token_reporting, '_observe')):
        yield


def mutable_containers(value):
    if isinstance(value, Mapping):
        return {key: mutable_containers(child) for key, child in value.items()}
    if type(value) is tuple:
        return tuple(mutable_containers(child) for child in value)
    return value


def immutable_containers(value):
    if isinstance(value, Mapping):
        assert type(value) is MappingProxyType
        for child in value.values():
            immutable_containers(child)
    elif type(value) is tuple:
        for child in value:
            immutable_containers(child)
    else:
        assert type(value) is not list


def phase_frame(snapshot, identity, shared):
    return (b''.join(decoded_buffer(snapshot, identity, byte_cap=STORAGE.expanded_cap,
        reference_cap=STORAGE.reference_cap)) if shared else dict(snapshot.buffers)[identity])


class Arena:
    def __init__(self):
        self._failure, self.count = None, 0

    @contextmanager
    def phase(self, identity):
        index = self.count
        self.count += 1
        yield SimpleNamespace(index=index)

    def check(self):
        pass

    def require_initialized(self, value):
        pass

    def snapshot(self):
        return dict(scope='CPU substitution, not actual device storage', phases=self.count)


def cpu_prefix(contract):
    value = object.__new__(_CudaPrefix)
    value.contract, value.arena = contract, Arena()
    value._device = SimpleNamespace(check=lambda: None, snapshot=lambda: None)
    value.current, value.staged, value.predicted, value.phases, value._values = {}, {}, {}, {}, {}
    value._native_bounds = {}
    return value


@contextmanager
def cpu_device():
    def arrays(workspace, readout_buffer, **kwargs):
        return CPUArrays(**kwargs)
    with patch.object(runtime, '_CudaPrefix', cpu_prefix), patch.object(execution, 'CudaArrays', arrays):
        yield


def run(attack, shared=False, legacy=False):
    cc, program, online, reporting = report_registration(report_count=1)
    cc = replace(cc, limits=limits(256 << 20, 10**14))
    originals, relation = [], execution.check_prediction

    def producer(*args, **kwargs):
        result = relation(*args, **kwargs)
        originals.append(result)
        return result

    with cpu_device(), patch.object(execution, 'check_prediction', producer):
        rt = ReferenceCompilerRuntime(cc, program, online=online, reporting=reporting,
            cuda=cuda_contract(cc.initializer_pattern), shared_storage=STORAGE if shared else None)
        train(rt)
        assert rt.begin_report().status == 'REPORTING'
        assert rt.predict_report('report/0').status == 'PREDICTED_REPORT'
        snapshot = rt.snapshot()
        phase = next(p for p in snapshot.cuda.phases if p.object_id == snapshot.token_report.pending.cuda_prediction)
        original = pack(phase)
        resident = phase.raw_state.cpu()
        forecast = phase.raw_prediction.cpu(resident.prepared)
        a = CPUArrays(element_cap=1 << 20, cell_cap=4096)
        masses = tuple(F(float(Kernel(program.definition, element_cap=1 << 20).readout_label(
            resident.prepared, forecast, y, a)[0])) for y in range(program.definition.output.labels))
        probability = masses[0]/sum(masses, F(0))
        assert 0 < probability < 1
        refused = False
        if attack == 'snapshot':
            try:
                # The attack uses only the returned public snapshot. It
                # touches no private Runtime attribute, tensor or writer.
                phase.relation['stored_sum_lower'] = (masses[0],)
                phase.relation['stored_sum_upper'] = (masses[0],)
            except TypeError:
                refused = True
        elif attack == 'producer':
            originals[-1]['stored_sum_lower'] = (masses[0],)
            originals[-1]['stored_sum_upper'] = (masses[0],)
        changed = pack(phase) != original
        result = rt.observe_report(0)
        assert result.status == 'COMPLETE_REPORT', result.reason
        outcome = rt.report_result()
        final = rt.snapshot()
        event = final.token_report.events[0]
        frame = phase_frame(final, phase.object_id, shared)
        count = int.from_bytes(frame[:8], 'big')
        frame_matches = frame[8:8+count] == pack(phase)
        phase_bytes = 0
        if legacy:
            assert attack == 'snapshot' and not refused and changed and not frame_matches
            assert outcome.physical_mean.lower == outcome.physical_mean.upper == 0
        else:
            assert not changed and frame_matches
            assert refused == (attack == 'snapshot')
            assert event.physical_sum[0] <= sum(masses, F(0)) <= event.physical_sum[1]
            with localcontext() as context:
                context.prec = 90
                loss = -(Decimal(probability.numerator)/Decimal(probability.denominator)).ln()
                low, high = outcome.physical_mean.lower, outcome.physical_mean.upper
                assert Decimal(low.numerator)/Decimal(low.denominator) <= loss <= Decimal(high.numerator)/Decimal(high.denominator)
            for row in final.cuda.phases:
                immutable_containers(row.relation)
                immutable_containers(row.execution_plan)
                flat = phase_frame(final, row.object_id, shared)
                size = int.from_bytes(flat[:8], 'big')
                assert flat[8:8+size] == pack(row) and not any(flat[8+size:])
                # Freezing these actual mappings preserves all canonical bytes.
                assert pack(row) == pack(replace(row, relation=mutable_containers(row.relation),
                    execution_plan=mutable_containers(row.execution_plan)))
                phase_bytes += size
                try:
                    row.execution_plan['target'] = 1
                except TypeError:
                    pass
                else:
                    raise AssertionError('public plan remained writable')
        return dict(attack=attack, shared_storage=shared, snapshot_write_refused=refused,
            snapshot_phase_changed=changed, forecast_frame_matches_public_record=frame_matches, status=outcome.status,
            true_physical_probability=str(probability), physical_mean=(str(outcome.physical_mean.lower), str(outcome.physical_mean.upper)),
            native_mean=(str(outcome.native_mean.lower), str(outcome.native_mean.upper)),
            used_sum=tuple(map(str, event.physical_sum)), original_sum=str(sum(masses, F(0))),
            complete_phase_bytes_checked=phase_bytes, checked_phases=len(final.cuda.phases))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    with legacy_implementation():
        legacy = [run('snapshot', shared, legacy=True) for shared in (False, True)]
    corrected = [run(attack, shared) for shared in (False, True) for attack in ('none', 'snapshot', 'producer')]
    assert all(row['physical_mean'] == corrected[0]['physical_mean'] for row in corrected)
    result = dict(status='PASS_IMMUTABLE_TOKEN_SNAPSHOT_BOUNDS_CPU',
        scope='CPU complete Runtime control, no actual device certificate',
        counterexample_source=LEGACY, counterexamples=legacy, corrected_cases=corrected)
    assert 'torch' not in sys.modules
    if args.write:
        (ROOT/'evidence/minimal/FP_TOKEN_SNAPSHOT_BOUNDS_CPU.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
