"""Exact CPU audits of complete token readout decoding and normalization."""
from dataclasses import replace
from fractions import Fraction as F
from pathlib import Path
import argparse
import json
import sys
import numpy as np
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'experiments/next_token'), str(ROOT/'scripts')]
import amp_tokens as amp
import batched_tokens as batch
import readout_relation as relation
import native_tokens as tokens
import native_readout as readout
from causal_tokens import TokenSources
from enclosed_tokens import EnclosureUnresolved
from fp_reference.binary_arithmetic import round_binary
from fp_reference.semantics import ArithmeticUnresolved
from audit_token_amp_schedule import ExactPrimitives
from audit_native_tokens import fixture


def refuses(operation):
    try:
        operation()
    except (ValueError, ArithmeticUnresolved):
        return
    raise AssertionError('expected unresolved or invalid full-readout check')


def decoder_audit():
    bits = np.asarray((0, 0x80000000, 1, 0x80000001, 0x7fffff, 0x800000, 0x3effffff,
        0x3f000000, 0x3f800000, 0xbf800000, 0x3f800001, 0x3eaaaaab, 0x7f7fffff, 0xff7fffff), dtype=np.uint32)
    values = bits.view(np.float32)
    decoder, audit = relation.Binary32Decoder(1000), ExactPrimitives()
    overflow = zero = checks = 0
    for operation in ('add', 'mul', 'div'):
        for a in values:
            for b in values:
                if operation == 'div' and not b:
                    refuses(lambda: decoder.op(operation, np.asarray(a), np.asarray(b)))
                    zero += 1
                    continue
                x, y = F(float(a)), F(float(b))
                exact = x+y if operation == 'add' else x*y if operation == 'mul' else x/y
                try:
                    round_binary(exact, amp.SINGLE, bit_limit=4096)
                except ArithmeticUnresolved:
                    refuses(lambda: decoder.op(operation, np.asarray(a), np.asarray(b)))
                    overflow += 1
                    continue
                result = decoder.op(operation, np.asarray(a), np.asarray(b))
                audit(operation, result, np.asarray(a), np.asarray(b))
                checks += 1
    # Zero division's signed output straddles the conservative enclosure;
    # exhausting its exact verifier allowance cannot silently pick a cell.
    refuses(lambda: relation.Binary32Decoder(0).op('div', np.asarray(0, dtype=np.float32), np.asarray(1, dtype=np.float32)))
    rng = np.random.default_rng(276)
    raw = rng.integers(0, 0x7f800000, (2, 2000), dtype=np.uint32)
    x, y = raw.view(np.float32)
    sampled = 0
    for operation in ('add', 'mul', 'div'):
        for a, b in zip(x, y):
            exact = F(float(a))+F(float(b)) if operation == 'add' else F(float(a))*F(float(b)) if operation == 'mul' else F(float(a))/F(float(b))
            try:
                round_binary(exact, amp.SINGLE, bit_limit=4096)
            except ArithmeticUnresolved:
                continue
            audit(operation, decoder.op(operation, np.asarray(a), np.asarray(b)), np.asarray(a), np.asarray(b))
            sampled += 1
    return dict(boundary_RNE_words=checks, fixed_seed_RNE_words=sampled,
        overflow_refusals=overflow, zero_denominator_refusals=zero,
        exact_ambiguous_rounding_cells=decoder.exact_cells, exhausted_tie_allowance_refuses=True)


def totals_audit():
    words = np.asarray([(e << 23) | m for e in range(255) for m in (0, 1, 1 << 22, (1 << 23)-1)], dtype=np.uint32)
    values = np.stack((words, np.roll(words, 17), words[::-1]), axis=1).view(np.float32)
    totals = relation.MassTotal(len(values), 3, element_cap=10000)
    refuses(totals.finish)
    for first in range(0, len(values), 17):
        totals.add(values[first:first+17])
    exact = tuple(sum((F(float(x)) for x in values[:, i]), F(0)) for i in range(3))
    assert totals.finish() == exact
    refuses(lambda: totals.add(values[:1]))
    for bad in (0x80000000, 0xbf800000, 0x7f800000, 0x7fc00000):
        negative = np.asarray([[bad]], dtype=np.uint32).view(np.float32)
        refuses(lambda: relation.MassTotal(1, 1, element_cap=1000).add(negative))
    refuses(lambda: relation.MassTotal((1 << 20)+1, 1, element_cap=1000))
    refuses(lambda: relation.MassTotal(1, 3, element_cap=761))
    return dict(exponent_fields=255, mass_words=values.size, exact_full_sums=len(exact),
        maximum_numerator_bits=max(v.numerator.bit_length() for v in exact), malformed_or_incomplete_refusals=8)


def setup(d, origin, targets):
    packed = batch.Origin.from_native(origin, element_cap=1 << 20)
    windows = tuple(d.sources.window(targets, i) for i in range(len(targets)))
    exact = batch.Kernel(d, element_cap=1 << 20).bound(packed, windows, targets)
    a = amp.Arithmetic()
    kernel = amp.Kernel(d, a, element_cap=1 << 20)
    pending = kernel.unit(amp.State.initialize(packed, a), windows, targets)
    return exact, pending, kernel


def check_literal(bounds, pending, kernel, result):
    V, N = pending.origin.definition.output.labels, len(pending.targets)
    excess, masses, raw = kernel.mass_block(pending, 0, V)
    state = bounds.unit.origin.to_native()
    exact_totals = tuple(sum((F(float(masses[y, t])) for y in range(V)), F(0)) for t in range(N))
    assert result['exact_stored_sum'] == exact_totals
    compared = 0
    for t, window in enumerate(pending.windows):
        prediction = state.predict(window)
        for y in range(V):
            native = prediction.output.mass(y)/prediction.output.normalizer
            proper = F(float(masses[y, t]))/exact_totals[t]
            physical = F(float(raw[y, t]))
            assert max(abs(native-proper), abs(native-physical)) <= F(result['probability_error_upper'])
            assert abs(proper-physical) <= F(result['division_error_upper'])
            compared += 1
    return compared


def prediction_audit():
    contract = relation.PredictionContract(F(1000), F(1000), F(1, 10), F(1, 1000), F(1, 10**7), 1, 10000, 1000)
    d, origin = fixture(2, 'mixed')
    bounds, pending, kernel = setup(d, origin, (0, 1))
    result = relation.check(bounds, pending, kernel, contract)
    comparisons = check_literal(bounds, pending, kernel, result)
    refuses(lambda: relation.check(bounds, pending, kernel, replace(contract, probability_atol=F(0))))
    fake = replace(pending, targets=(1, 0))
    refuses(lambda: relation.check(bounds, fake, kernel, contract))
    original = kernel.mass_block
    def wrong_unobserved(record, first, stop):
        excess, masses, probabilities = original(record, first, stop)
        masses = masses.copy()
        # Event0's target is0. Corrupt an unobserved label while preserving
        # that target's cached mass; a target-only check would miss this.
        if first <= 1 < stop:
            masses[1-first, 0] = np.nextafter(masses[1-first, 0], np.float32(np.inf))
        return excess, masses, probabilities
    with patch.object(kernel, 'mass_block', side_effect=wrong_unobserved):
        refuses(lambda: relation.check(bounds, pending, kernel, contract))
    d = tokens.Definition(TokenSources(3, 1), 1, (), 0, (0,),
        readout.Spec((F(1, 3),)*3, 1, 16, F(1, 16), 1))
    root = tokens.initialize(d, (0,), (), (0,))
    bounds, pending, kernel = setup(d, root, (0,))
    normalized = relation.check(bounds, pending, kernel, contract)
    comparisons += check_literal(bounds, pending, kernel, normalized)
    stored_sum, = normalized['exact_stored_sum']
    assert stored_sum == F(33554433, 33554432)
    assert F(float(pending.normalizer[0])) == 1
    _, masses, raw = kernel.mass_block(pending, 0, 3)
    assert sum((F(float(v)) for v in raw[:, 0]), F(0)) == stored_sum != 1
    assert all(F(float(v))/stored_sum == F(1, 3) for v in masses[:, 0])
    refuses(lambda: relation.check(bounds, pending, kernel, replace(contract, native_atol=F(0))))
    old = kernel.base.copy()
    kernel.base[1] = np.nextafter(kernel.base[1], np.float32(np.inf))
    refuses(lambda: relation.check(bounds, pending, kernel, contract))
    kernel.base[:] = old
    refuses(lambda: relation.check(bounds, pending, kernel, replace(contract, element_cap=253)))
    return dict(literal_probability_comparisons=comparisons, binding_tolerance_and_unobserved_label_refusals=6,
        rounded_normalizer='1', exact_stored_mass_sum=str(stored_sum), raw_probability_sum=str(stored_sum),
        proper_probability='1/3', normalization_gap=str(stored_sum-1),
        complete_vocabulary_relation_passes_registered_nonzero_tolerances=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = dict(status='PASS_COMPLETE_TOKEN_READOUT_RELATION', scope='passive complete observed-context prediction relation; no Runtime, learner-state or issued bridge')
    for name, function in (('binary32_decoder', decoder_audit), ('exact_mass_totals', totals_audit), ('predictions', prediction_audit)):
        result[name] = function()
        print('PASS '+name, flush=True)
    assert 'torch' not in sys.modules
    if args.write:
        (ROOT/'evidence/minimal/FP_TOKEN_READOUT_RELATION.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
