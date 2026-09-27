"""CPU storage trace for the token phase continuation roots; no CUDA authority.

Every actual array input is checked against the previous boundary's roots
or the current phase's new allocations. No corpus is read and no device
extent is freed. Compact live-byte totals are not an allocator fit theorem.
"""
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import argparse
import json
import sys
import weakref

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts'), str(ROOT/'experiments/next_token')]
from audit_native_tokens import fixture
from audit_token_reference_host import text_model_fixture
from fp_reference.token_arrays import CPUArrays
from fp_reference.token_cuda_prefix import transition
from fp_reference.token_cuda_state import Resident, PredictionResident, ReadoutResident
from fp_reference.token_batch import Origin
from fp_reference.token_execution import TokenProgram


def resident_arrays(values):
    seen, arrays, stack = set(), [], list(values)
    while stack:
        value = stack.pop()
        if value is None or id(value) in seen:
            continue
        seen.add(id(value))
        assert type(value) in (Resident, PredictionResident, ReadoutResident)
        arrays.extend(tensor for _, tensor in value.tensors())
        if type(value) is PredictionResident:
            stack.append(value.predecessor)
        elif type(value) is ReadoutResident:
            stack.append(value.prediction)
    return tuple(arrays)


class Trace:
    def __init__(self):
        self.registry, self.sizes, self.live = {}, [], set()
        self.inputs = self.phases = self.append_only_bytes = 0
        self.peak_live = self.peak_phase_coexist = self.peak_live_regions = 0
        self.by_kind = {}

    @staticmethod
    def base(value):
        while type(value.base) is np.ndarray:
            value = value.base
        return value

    def allocate(self, value):
        root = self.base(value)
        previous = self.registry.get(id(root))
        assert previous is None or previous[0]() is not root
        sequence = len(self.sizes)
        self.registry[id(root)] = weakref.ref(root), sequence
        size = max(8, (root.nbytes+7)//8*8)
        self.sizes.append(size)
        self.live.add(sequence)
        self.append_only_bytes += size

    def sequence(self, value):
        root = self.base(value)
        entry = self.registry.get(id(root))
        assert entry is not None and entry[0]() is root, 'undeclared array input'
        return entry[1]

    def read(self, value):
        assert self.sequence(value) in self.live, 'future read of an omitted continuation root'
        self.inputs += 1

    def boundary(self, kind, roots):
        # All outputs remain until complete phase checking/capture has ended.
        coexist = sum(self.sizes[i] for i in self.live)+8
        self.peak_phase_coexist = max(self.peak_phase_coexist, coexist)
        keep = {self.sequence(value) for value in resident_arrays(roots)}
        assert keep <= self.live
        self.live = keep
        size = sum(self.sizes[i] for i in keep)
        self.peak_live = max(self.peak_live, size)
        self.peak_live_regions = max(self.peak_live_regions, len(keep))
        row = self.by_kind.setdefault(kind, dict(phases=0, maximum_live_bytes=0, maximum_coexist_bytes=0))
        row['phases'] += 1
        row['maximum_live_bytes'] = max(row['maximum_live_bytes'], size)
        row['maximum_coexist_bytes'] = max(row['maximum_coexist_bytes'], coexist)
        self.phases += 1
        self.append_only_bytes += 8

    def report(self):
        return dict(phases=self.phases, allocated_regions=len(self.sizes), checked_array_inputs=self.inputs,
            append_only_padded_bytes=self.append_only_bytes, peak_live_padded_bytes=self.peak_live,
            peak_live_regions=self.peak_live_regions, peak_phase_coexist_padded_bytes=self.peak_phase_coexist,
            terminal_live_padded_bytes=sum(self.sizes[i] for i in self.live), phases_by_kind=self.by_kind)


def trajectory(definition, origin, targets):
    trace = Trace()
    allocate, read = CPUArrays._new, CPUArrays._input

    def new(self, *args):
        value = allocate(self, *args)
        trace.allocate(value)
        return value

    def checked_input(self, value):
        read(self, value)
        trace.read(value)

    cfg = SimpleNamespace(initializer=SimpleNamespace(element_cap=1 << 24))
    program = TokenProgram(definition)
    current = staged = predicted = None

    def capture(value, a):
        # This is a liveness probe, not a repeat of the native/numerical audit.
        # Read every named resident array (including transitive predecessors)
        # without repeatedly reconstructing/validating the large definition.
        for array in resident_arrays((value,)):
            a.raw(array)

    def phase(kind, before, forecast=None, window=None, target=None):
        a = CPUArrays(element_cap=1 << 24, cell_cap=1 << 22)
        # Reproduce all classes of old-state/forecast and output capture used
        # by the owner. Numerical correctness has its existing independent audit.
        if before is not None:
            capture(before, a)
        if forecast is not None:
            capture(forecast, a)
        result = transition(kind, program, cfg, before, forecast, window, target,
            0 if before is None else before.state.cursor, origin if kind == 'initialize' else None, a)
        a.check()
        capture(result, a)
        if before is not None:
            capture(before, a)
        if forecast is not None:
            capture(forecast, a)
        return result

    with patch.object(CPUArrays, '_new', new), patch.object(CPUArrays, '_input', checked_input):
        current = staged = phase('initialize', None)
        trace.boundary('initialize', (current, staged, predicted))
        for target in targets:
            window = current.state.source
            predicted = phase('predict', current, window=window)
            trace.boundary('predict', (current, staged, predicted))
            staged = phase('observe', current, predicted, window, target)
            # The old current survives evidence retention and commit staging.
            trace.boundary('observe-staged', (current, staged, predicted))
            if staged.state.unit_count == definition.output.update_unit:
                staged = phase('commit', staged)
                trace.boundary('commit-staged', (current, staged, predicted))
            current = staged
            # Publication adds no numerical allocation; release only in the
            # shadow live set, never in actual CPU or CUDA backing storage.
            trace.live = {trace.sequence(value) for value in resident_arrays((current, staged, predicted))}
        assert type(current.state) is not type(origin) and current.state.cursor == len(targets)
        assert current.origin.optimizer_steps == len(targets)//definition.output.update_unit
        for target in (0, 1):
            predicted = phase('predict', current, window=current.state.source)
            trace.boundary('report-predict', (current, staged, predicted))
            scored = phase('readout', current, predicted, current.state.source, target)
            assert type(scored) is ReadoutResident
            trace.boundary('report-readout', (current, staged, predicted))
    return trace.report()


def cpu(full=False):
    d, initial = fixture(4, 'mixed')
    origin = Origin.from_native(initial, element_cap=1 << 24)
    small = trajectory(d, origin, (0, 1, 1, 0, 1, 0, 0, 1))
    result = dict(status='PASS_CPU_TOKEN_CONTINUATION_ROOT_TRACE', small=small,
        scope='synthetic CPU array-access/shape trace; no arena reclamation, device/Runtime authority, allocator-fit or time bound')
    if full:
        d, origin = text_model_fixture()
        targets = tuple((i*7919+17) % d.sources.vocabulary for i in range(2*d.output.update_unit))
        result['full_vocabulary_two_units'] = trajectory(d, origin, targets)
        result['fixture'] = dict(vocabulary=d.sources.vocabulary, context=d.sources.context,
            width=d.width, features=d.output.features, masters=d.slot_count, targets='synthetic affine permutation',
            observations=len(targets), corpus_read=False)
    assert 'torch' not in sys.modules
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--full', action='store_true')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = cpu(args.full)
    if args.write:
        (ROOT/'evidence/minimal/FP_TOKEN_STORAGE_LIVENESS_CPU.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
