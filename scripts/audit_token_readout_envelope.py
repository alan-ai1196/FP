"""Exact controls and CPU cost for the algebraic all-label token envelope."""
from dataclasses import replace
from fractions import Fraction as F
from pathlib import Path
import argparse
import json
import sys
import time
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'experiments/next_token'), str(ROOT/'scripts')]
import amp_tokens as amp
import batched_tokens as ref
import native_readout as readout
import native_tokens as tokens
import readout_envelope as envelope
from readout_relation import PredictionContract
from causal_tokens import TokenSources
from audit_native_tokens import fixture
from audit_token_readout_relation import refuses, setup


def exact_comparison(bounds, pending, kernel, result):
    d, a = pending.origin.definition, kernel.a
    excesses, masses, probabilities = (a.raw(v) for v in kernel.mass_block(pending, 0, d.output.labels))
    physical_values, normalizers = a.raw(pending.values), a.raw(pending.normalizer)
    state = bounds.unit.origin.to_native()
    checks = 0
    for t, window in enumerate(pending.windows):
        native = state.predict(window)
        S = sum((F(float(m)) for m in masses[:, t]), F(0))
        Z, R = F(float(normalizers[t])), native.output.normalizer
        assert F(result['stored_sum_lower'][t]) <= S <= F(result['stored_sum_upper'][t])
        assert max(abs(S-Z), abs(S-R), abs(Z-R)) <= F(result['normalizer_error_upper'])
        for r, value in zip(native.values, physical_values[:, t]):
            assert abs(r-F(float(value))) <= F(result['native_error_upper'])
        for y in range(d.output.labels):
            M, m, e, raw = native.output.mass(y), F(float(masses[y, t])), F(float(excesses[y, t])), F(float(probabilities[y, t]))
            assert max(abs(M-m), abs(M-d.output.base[y]-e)) <= F(result['native_error_upper'])
            assert max(abs(M/R-m/S), abs(M/R-raw)) <= F(result['probability_error_upper'])
            assert abs(m/S-raw) <= F(result['division_error_upper'])
            checks += 1
    return checks


def trajectories():
    contract = PredictionContract(F(1000), F(1000), F(1, 10), F(1, 1000), F(1, 10000), 1, 1 << 20, 1000)
    units = coordinates = 0
    for unit in (1, 2):
        for kind in ('mixed', 'zero-embedding', 'zero-core'):
            d, root = fixture(unit, kind)
            origin = ref.Origin.from_native(root, element_cap=1 << 20)
            a = amp.Arithmetic()
            state = amp.State.initialize(origin, a)
            kernel, control = amp.Kernel(d, a, element_cap=1 << 20), ref.Kernel(d, element_cap=1 << 20)
            word = (0, 1, 1, 0, 0, 1)
            for first in range(0, len(word), unit):
                windows = tuple(d.sources.window(word, t) for t in range(first, first+unit))
                targets = word[first:first+unit]
                bounds, pending = control.bound(origin, windows, targets), kernel.unit(state, windows, targets)
                result = envelope.bound(bounds, pending, kernel, contract)
                assert result['unqueried_label_contexts_executed'] == 0
                coordinates += exact_comparison(bounds, pending, kernel, result)
                origin, state = bounds.commit(), pending.commit(a)
                units += 1
    return dict(independent_native_AMP_units=units, exact_all_label_probability_comparisons=coordinates,
        all_normalizer_and_core_mass_bounds_checked=True)


def boundaries():
    contract = PredictionContract(F(1000), F(1000), F(1), F(1, 100), F(1, 100), 1, 10000, 1000)
    # q near2^32 rounds upward to the exactly represented integer2^32.
    # Nonuniform bases and repeated features are retained in the definition.
    d = tokens.Definition(TokenSources(3, 1), 2, (), 0, (0, 1, 0),
        readout.Spec((F(1, 7), F(2, 7), F(4, 7)), 3, 32, F(1, 1024), 1))
    root = tokens.initialize(d, ((1 << 31), (1 << 30)), (), ((1 << 32)-1, (1 << 24)+1, 0),
        output_overrides=((1, 0, 0), (2, 0, (1 << 32)-129)))
    bounds, pending, kernel = setup(d, root, (1,))
    result = envelope.bound(bounds, pending, kernel, contract)
    checks = exact_comparison(bounds, pending, kernel, result)
    refuses(lambda: envelope.bound(bounds, pending, kernel, replace(contract, probability_atol=F(0))))
    refuses(lambda: envelope.bound(bounds, replace(pending, targets=(2,)), kernel, contract))
    refuses(lambda: envelope.bound(bounds, pending, kernel, replace(contract, element_cap=8)))
    fake = pending.target_mass.copy()
    fake[0] = np.nextafter(fake[0], np.float32(np.inf))
    refuses(lambda: envelope.bound(bounds, replace(pending, target_mass=fake), kernel, contract))
    kernel.base[2] = np.nextafter(kernel.base[2], np.float32(np.inf))
    refuses(lambda: envelope.bound(bounds, pending, kernel, contract))
    d = tokens.Definition(TokenSources(3, 1), 1, (), 0, (0,),
        readout.Spec((F(1, 3),)*3, 1, 16, F(1, 16), 1))
    root = tokens.initialize(d, (0,), (), (0,))
    bounds, pending, kernel = setup(d, root, (0,))
    result = envelope.bound(bounds, pending, kernel, contract)
    checks += exact_comparison(bounds, pending, kernel, result)
    exact_sum = F(33554433, 33554432)
    assert F(result['stored_sum_lower'][0]) <= exact_sum <= F(result['stored_sum_upper'][0])
    # A valid extremely tiny readout need not be certified by a coarse
    # additive-underflow envelope. Preserve the honest unresolved result.
    tiny = replace(d, output=replace(d.output, base=(F(1, 1 << 149),)*3))
    bounds, pending, kernel = setup(tiny, tokens.initialize(tiny, (0,), (), (0,)), (0,))
    refuses(lambda: envelope.bound(bounds, pending, kernel, contract))
    return dict(exact_extreme_master_and_normalization_coordinates=checks, invalid_binding_or_contract_refusals=5,
        valid_underflow_envelope_unresolved=True,
        rounded_master_reaches_integer_2_to_32=True, unequal_stored_mass_sum_preserved=True)


def actual_text():
    # CPU-only evaluation of the new envelope. No old CUDA job, commit,
    # loss, validation/test file or exhaustive vocabulary scan is replayed.
    from audit_token_reference_host import text_fixture
    d, origin, windows, targets, identity = text_fixture()
    a = amp.Arithmetic()
    kernel = amp.Kernel(d, a, element_cap=1 << 24)
    pending = kernel.unit(amp.State.initialize(origin, a), windows, targets)
    bounds = ref.Kernel(d, element_cap=1 << 24).bound(origin, windows, targets)
    contract = PredictionContract(F(2), F(64), F(1, 100), F(1, 10**6), F(1, 10**7), 256, 1 << 24, 4096)
    started = time.perf_counter()
    result = envelope.bound(bounds, pending, kernel, contract)
    result['envelope_seconds'] = time.perf_counter()-started
    del result['stored_sum_lower'], result['stored_sum_upper']
    result['source'] = identity
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = dict(status='PASS_CONDITIONAL_READOUT_ENVELOPE_CPU', scope='exact finite controls and unbounded-host CPU timing; no owned or actual-device bridge')
    for name, function in (('trajectories', trajectories), ('boundaries', boundaries), ('real_context512', actual_text)):
        result[name] = function()
        print('PASS '+name, flush=True)
    assert 'torch' not in sys.modules
    if args.write:
        (ROOT/'evidence/minimal/FP_TOKEN_READOUT_ENVELOPE.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
