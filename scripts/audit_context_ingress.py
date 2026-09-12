"""Exact byte-ingress protocol audit, including historical raw-value failure.

Enumerate small wire/fragmentation classes and exercise the actual Runtime.
This is not a proof of total Python heap, bit-time, AMP or ERC-1 closure.
"""
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
from math import gcd
from pathlib import Path
import argparse
import json
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts')]

from fp_reference import ReferenceCompilerRuntime
from fp_reference.core import ContractError
from fp_reference.ingress import IngressContract, decode_context, encode_context
from fp_reference.machine import pack
from fp_reference.resources import ResourceExceeded
from fp_reference.semantics import ArithmeticUnresolved
import fp_reference.ingress as codec
import fp_reference.runtime as execution
from audit_reference_construction import contract, domain, limits, rejects, validate_residency, zero_program
from audit_reference_events import online
from audit_reference_persistence import identity
from audit_float64_runtime import fixture as paired_fixture, replay
from audit_paired_cpu_persistence import config, pair, registration
from ingress_audit_support import deliver_context


def unsigned(value):
    """Independent producer formula: base-128 length, then base-256 body."""
    body = []
    while value:
        value, byte = divmod(value, 256)
        body.append(byte)
    digits, length = [], len(body)
    while length >= 128:
        length, digit = divmod(length, 128)
        digits.append(digit+128)
    return bytes(digits+[length]+list(reversed(body)))


def wire(numerator, denominator):
    return b'FP1'+unsigned(numerator)+unsigned(denominator)


def codec_audit():
    cases = 0
    for bits, numerator, denominator in product((1, 5, 9), range(32), range(32)):
        frame = wire(numerator, denominator)
        legal = denominator > 0 and gcd(numerator, denominator) == 1
        fits = max(numerator.bit_length(), denominator.bit_length()) <= bits
        if legal and fits:
            value = F(numerator, denominator)
            assert decode_context(frame, 1, bits) == (value,)
            assert encode_context((value,)) == frame
        elif not fits:
            rejects(lambda: decode_context(frame, 1, bits), ArithmeticUnresolved)
        else:
            rejects(lambda: decode_context(frame, 1, bits))
        cases += 1
    vectors = 0
    for dimensions in range(4):
        for values in product((F(0), F(1), F(1, 2), F(2, 3)), repeat=dimensions):
            assert decode_context(encode_context(values), dimensions, 8) == values
            vectors += 1
    boundaries = 0
    for length in (1, 2, 16, 127, 128, 129, 16383, 16384):
        for leading_bits in (1, 7, 8):
            value = 1 << (8*(length-1)+leading_bits-1)
            frame = wire(value, 1)
            assert encode_context((F(value),)) == frame
            assert decode_context(frame, 1, value.bit_length()) == (F(value),)
            if value.bit_length() > 1:
                rejects(lambda: decode_context(frame, 1, value.bit_length()-1), ArithmeticUnresolved)
            boundaries += 1
    frame = wire(257, 65537)
    for end in range(len(frame)):
        rejects(lambda: decode_context(frame[:end], 1, 32), ArithmeticUnresolved)
    malformed = (b'BAD\x00\x01\x01', b'FP1\x80\x00\x01\x01',
                 b'FP1\x01\x00\x01\x01', wire(0, 0), wire(2, 2), frame+b'\x00')
    for payload in malformed:
        rejects(lambda: decode_context(payload, 1, 32))
    # Instrument only the integer materialization boundary. Oversize length
    # headers and leading bits must stop before int.from_bytes sees a body.
    with patch.object(codec, 'int', create=True) as materializer:
        materializer.from_bytes.side_effect = AssertionError('oversize body was materialized')
        for payload in (b'FP1\x11', b'FP1'+b'\xff'*100, b'FP1\x02\x80\x00'):
            rejects(lambda: decode_context(payload, 1, 9), ArithmeticUnresolved)
        assert materializer.from_bytes.call_count == 0
    return {'small_integer_pairs_and_widths': cases, 'complete_small_vector_cases': vectors,
            'integer_width_and_varint_boundaries': boundaries, 'all_proper_frame_prefixes': len(frame),
            'malformed_canonical_frames': len(malformed), 'oversize_rejected_before_big_integer_materialization': True}


def fixture(*, cfg=None, capacity=32, chunk=4):
    cfg = contract(source_domain=False) if cfg is None else cfg
    run = online(cfg, 4, unit=2, grid=16)
    run = replace(run, data=replace(run.data, ingress=IngressContract(capacity, chunk)))
    return ReferenceCompilerRuntime(cfg, zero_program(2), online=run)


def owned(rt):
    snapshot = validate_residency(rt)
    buffers = dict(snapshot.buffers)
    for row in snapshot.ingress:
        identity = row.identity
        assert len(buffers[identity.body_id]) == identity.capacity
        assert buffers[identity.record_id] == pack(identity)
        assert codec.read_control(buffers[identity.control_id], snapshot.online.data.ingress) == (row.received, row.status)
        assert buffers[identity.body_id][row.received:] == bytes(identity.capacity-row.received)
    return snapshot


def compositions(total, bound):
    if not total:
        yield ()
    for first in range(1, min(total, bound)+1):
        for tail in compositions(total-first, bound):
            yield (first,)+tail


def chunking_audit():
    frame = encode_context((F(0), F(0)))
    prefixes, finals = {}, {}
    runs = prefix_checks = 0
    for sizes in compositions(len(frame), 4):
        # Equal initial identities permit exact complete-snapshot comparison.
        # No executed state or frontier is substituted by the audit.
        with patch.object(execution.secrets, 'token_hex', return_value='ingress-audit-fixed-nonce'):
            rt = fixture()
        before = rt.snapshot()
        offer = rt.begin_context('observation-0')
        initial = owned(rt)
        spent = initial.resources['spent']
        assert spent['compiler']['work']-before.resources['spent']['compiler']['work'] == rt.online_contract.data.ingress.work(2)
        for size in (0,)+sizes:
            if size:
                offset = offer.next_offset
                offer = rt.receive_context(offer.ingress_id, offset, frame[offset:offset+size])
            state = owned(rt)
            assert state == prefixes.setdefault(offer.next_offset, state)
            assert state.resources == initial.resources and state.revision == initial.revision
            row = state.ingress[-1]
            assert dict(state.buffers)[row.identity.body_id][:row.received] == frame[:offer.next_offset]
            prefix_checks += 1
        assert rt.finish_context(offer.ingress_id).status == 'PREDICTED_REFERENCE'
        assert owned(rt) == finals.setdefault('predicted', owned(rt))
        assert rt.observe(1).status == 'OBSERVED_REFERENCE'
        assert owned(rt) == finals.setdefault('observed', owned(rt))
        runs += 1
    with patch.object(execution.secrets, 'token_hex', return_value='ingress-audit-convenience-nonce'):
        direct, split = fixture(chunk=32), fixture(chunk=32)
    assert direct.predict_next('observation-0', frame) == deliver_context(split, 'observation-0', (0, 0))
    assert owned(direct) == owned(split)
    return {'frame_bytes': len(frame), 'maximum_chunk_bytes': 4, 'all_legal_chunkings': runs,
            'equal_prefix_complete_snapshot_checks': prefix_checks,
            'prediction_and_observation_independent_of_fragmentation': True,
            'no_owned_counter_or_ledger_event_per_chunk': True,
            'one_chunk_convenience_has_identical_owned_execution': True}


def admission_audit():
    # Budget encodings are part of the paid immutable manifest. Calibrate
    # with newly registered roots until this very cap is one work unit short;
    # measuring a different-budget root no longer locates the boundary.
    work_cap = 10_000_000
    for _ in range(16):
        cfg = replace(contract(source_domain=False), limits=limits(work_cap=work_cap))
        denied = fixture(cfg=cfg)
        base_work = denied.snapshot().resources['spent']['compiler']['work']
        prepaid = denied.online_contract.data.ingress.work(2)
        boundary = base_work+prepaid-1
        if work_cap == boundary:
            break
        work_cap = boundary
    else:
        raise AssertionError('immutable ingress work boundary did not stabilize')
    before = denied.snapshot()
    for _ in range(64):
        offer = denied.begin_context('observation-0')
        assert offer.status == 'UNRESOLVED' and offer.ingress_id is None
        assert denied.snapshot() == before
    # A trillion-byte registration is rejected by real residency caps BEFORE
    # any empty body allocation, even though its work could be paid.
    cfg = replace(contract(source_domain=False), limits=limits(work_cap=10**15))
    huge = fixture(cfg=cfg, capacity=10**12, chunk=64)
    before = huge.snapshot()
    with patch.object(execution, 'PackedObject', side_effect=AssertionError('unfunded body created')):
        result = huge.begin_context('observation-0')
    after = owned(huge)
    assert result.status == 'UNRESOLVED' and result.ingress_id is None
    assert after.buffers == before.buffers and not after.ingress and after.event_phase == 'idle'
    assert after.resources['spent']['compiler']['work'] > before.resources['spent']['compiler']['work']
    # Failure after actual empty storage allocation but before publication.
    rt = fixture()
    before = rt.snapshot()
    real_result, calls = execution.IngressResult, 0
    def fail_result(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise ResourceExceeded('injected prepublication result allocation')
        return real_result(*args, **kwargs)
    with patch.object(execution, 'IngressResult', side_effect=fail_result):
        result = rt.begin_context('observation-0')
    failed = owned(rt)
    assert result.status == 'UNRESOLVED' and failed.buffers == before.buffers
    assert not failed.ingress and failed.active_ingress is None and failed.event_phase == 'idle'
    assert failed.resources['peak']['reference_payload_bytes'] > before.resources['peak']['reference_payload_bytes']
    assert len(failed.resources['retired_object_ids']) == len(before.resources['retired_object_ids'])+3
    assert rt.begin_context('observation-0').status == 'RECEIVING'
    assert owned(rt).ingress[-1].identity.ingress_id != failed.attempts[-1][0]
    return {'unchanged_unfunded_denials': 64, 'unallocatable_registered_capacity_bytes': 10**12,
            'actual_immutable_initial_work': base_work, 'prepaid_ingress_work': prepaid,
            'calibrated_work_cap': work_cap,
            'residency_preflight_precedes_window_creation': True,
            'failed_empty_preparation_keeps_paid_work_peak_and_retired_ids': True,
            'retry_publishes_fresh_identity_without_dangling_old_window': True}


def failure_audit():
    rt = fixture()
    before = rt.snapshot()
    rejects(lambda: rt.predict_next('observation-0', (F(1), F(0))))
    rejects(lambda: rt.predict_next('observation-0', b'x'*5))
    rejects(lambda: rt.begin_context('observation-1'))
    assert rt.snapshot() == before
    offer = rt.begin_context('observation-0')
    offer = rt.receive_context(offer.ingress_id, 0, b'FP')
    before = owned(rt)
    bad = ((offer.ingress_id, 0, b'1'), (offer.ingress_id, 2, b''),
           (offer.ingress_id, 2, b'12345'), (offer.ingress_id, 2, bytearray(b'1')),
           ('foreign', 2, b'1'), (offer.ingress_id, True, b'1'))
    for args in bad:
        rejects(lambda: rt.receive_context(*args))
        assert owned(rt) == before
    assert rt.finish_context(offer.ingress_id).status == 'UNRESOLVED'
    failed = owned(rt)
    assert failed.event_phase == 'halted' and failed.ingress[-1].status == 'UNRESOLVED' and failed.pending is None
    rejects(lambda: rt.finish_context(offer.ingress_id))
    rejects(lambda: rt.receive_context(offer.ingress_id, 2, b'1'))
    assert owned(rt) == failed
    # Even when no ordinary prediction work remains after admission, the
    # terminal header and all received bytes already have physical storage.
    probe = fixture()
    base_work = probe.snapshot().resources['spent']['compiler']['work']
    prepaid = probe.online_contract.data.ingress.work(2)
    cfg = replace(contract(source_domain=False), limits=limits(work_cap=base_work+prepaid))
    exhausted = fixture(cfg=cfg)
    assert deliver_context(exhausted, 'observation-0', (0, 0)).status == 'UNRESOLVED'
    after = owned(exhausted)
    assert after.pending is None and after.ingress[-1].status == 'UNRESOLVED'
    assert after.resources['spent']['compiler']['work'] == base_work+prepaid
    assert dict(after.buffers)[after.ingress[-1].identity.body_id][:9] == encode_context((0, 0))
    rows = []
    for exponent in (256, 1024, 4096):
        cfg = replace(contract(source_domain=False), reference_integer_bits=128)
        rt = fixture(cfg=cfg, capacity=1024, chunk=32)
        frame = encode_context((F(1, 1 << exponent), F(0)))
        before = rt.snapshot()
        assert deliver_context(rt, 'observation-0', (F(1, 1 << exponent), F(0))).status == 'UNRESOLVED'
        after = owned(rt)
        row = after.ingress[-1]
        assert after.pending is None and after.event_phase == 'halted' and row.status == 'UNRESOLVED'
        assert dict(after.buffers)[row.identity.body_id][:row.received] == frame
        assert after.resources['current']['reference_payload_bytes'] > before.resources['current']['reference_payload_bytes']
        assert after.resources['spent']['compiler']['work']-before.resources['spent']['compiler']['work'] == rt.online_contract.data.ingress.work(2)
        rows.append({'semantic_denominator_bits': exponent+1, 'received_paid_bytes': row.received,
                     'prepaid_window_bytes': row.identity.capacity})
    # An incomplete capacity prefix retains exactly the offered bytes. No
    # producer suffix is passed to a Runtime method or stored in pending.
    rt = fixture(capacity=8, chunk=3)
    frame = encode_context((F(1, 65537), F(0)))
    assert deliver_context(rt, 'observation-0', (F(1, 65537), F(0))).status == 'UNRESOLVED'
    after = owned(rt)
    row = after.ingress[-1]
    assert row.received == 8 and dict(after.buffers)[row.identity.body_id] == frame[:8] and after.pending is None
    # Noncanonical and out-of-domain bytes have already arrived; neither may
    # roll back to an unread idle state.
    for payload in (b'BAD', encode_context((F(2), F(0)))):
        rt = fixture(chunk=32)
        rejects(lambda: rt.predict_next('observation-0', payload))
        after = owned(rt)
        assert after.event_phase == 'halted' and after.ingress[-1].status == 'INVALID_INPUT'
        assert dict(after.buffers)[after.ingress[-1].identity.body_id][:len(payload)] == payload
    for error in (RuntimeError, ContractError):
        rt = fixture(chunk=32)
        before = rt.snapshot()
        with patch.object(execution, 'evaluate', side_effect=error('injected predictor defect')):
            rejects(lambda: rt.predict_next('observation-0', encode_context((0, 0))), error)
        after = owned(rt)
        assert after.halted[0] == 'predict' and len(after.attempts) == len(before.attempts)+1
        assert after.ingress[-1].status == 'EXECUTION_FAILED'
    return {'invalid_chunk_prefixes_rejected_without_mutation': len(bad), 'raw_value_bypass_rejected': True,
            'terminal_bytes_and_status_survive_post_admission_work_exhaustion': True,
            'numeric_guard_witnesses': rows, 'capacity_prefix_bytes_retained_without_unread_suffix': 8,
            'invalid_domain_or_frame_retains_terminal_prefix': True,
            'internal_contract_failure_is_execution_failed_not_invalid_input': True,
            'unexpected_prediction_cause_preserved_without_double_halt': True}


def filtration_audit():
    rt, candidate = paired_fixture(cfg=config(cap=100, peak=100), count=4,
                                    persistence=registration(bound=F(6), horizon=4))
    rid, fid = pair(rt, candidate)
    start = rt.snapshot()
    offer = rt.begin_context('observation-0')
    row = owned(rt).ingress[-1]
    assert row.identity.persistence_ids == (rid, fid)
    assert row.identity.candidate_ids == tuple(s.candidate_id for s in start.candidates if s.range_safe)
    frame = encode_context(domain(1)[0])
    actions = (lambda: rt.construct_candidate(zero_program(2)), lambda: rt.retire_candidate(candidate),
               lambda: rt.admit_reference_persistence(candidate, 'ref'),
               lambda: rt.admit_float64_persistence(candidate, 'finite'),
               lambda: rt.cancel_reference_persistence(rid), lambda: rt.cancel_float64_persistence(fid),
               lambda: rt.observe(0), lambda: rt.begin_context('observation-0'),
               lambda: rt.query('unregistered', ('observation-0',)))
    positions = 0
    for byte in frame:
        before = rt.snapshot()
        for action in actions:
            rejects(action)
            assert rt.snapshot() == before
            positions += 1
        offer = rt.receive_context(offer.ingress_id, offer.next_offset, bytes((byte,)))
    assert rt.finish_context(offer.ingress_id).status == 'PREDICTED_REFERENCE'
    assert rt.snapshot().pending.persistence_ids == (rid, fid)
    assert rt.observe(0).status == 'OBSERVED_REFERENCE'
    for _ in range(3):
        cursor = rt.snapshot().cursor
        assert deliver_context(rt, f'observation-{cursor}', domain(1)[cursor % 2]).status == 'PREDICTED_REFERENCE'
        assert rt.observe(cursor % 2).status == 'OBSERVED_REFERENCE'
    after = owned(rt)
    assert after.cursor == 4 and after.pending is None and after.active_ingress is None
    assert all(s.learner.cursor == s.float64.cursor == 4 for s in after.candidates)
    assert len(after.ingress) == 4 and all(row.status == 'PREDICTED' for row in after.ingress)
    assert identity(rt, rid).start_cursor == identity(rt, fid).start_cursor == 0
    phase_checks, state_differences, normalization_differences = replay(rt)
    return {'locked_action_prefix_positions': positions, 'received_contexts': 4,
            'preadmitted_reference_and_binary64_identities_survive_the_same_ingress': True,
            'independent_bitwise_phase_checks': phase_checks,
            'actual_finite_coordinates_differing_from_recast_exact_endpoints': state_differences,
            'rounded_normalization_differences': normalization_differences}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--section', choices=('codec', 'chunking', 'admission', 'failures', 'filtration'))
    args = parser.parse_args()
    sections = {'codec': codec_audit, 'chunking': chunking_audit, 'admission': admission_audit,
                'failures': failure_audit, 'filtration': filtration_audit}
    if args.section:
        print(json.dumps(sections[args.section](), indent=2))
        return
    result = {'status': 'PASS', 'scope': 'mandatory prepaid exact byte ingress in the serialized packed-payload Runtime',
              **{key: fn() for key, fn in sections.items()},
              'not_closed': ['complete Python heap and arithmetic scratch accounting',
                             'complete ERC-1 enforcement and Runtime release', 'actual target AMP and RTX 3090 science']}
    if args.write:
        (ROOT/'evidence/minimal/FP_CONTEXT_INGRESS_AUDIT.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
