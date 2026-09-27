"""Exact guard-decision and complete Runtime controls for owned token base facts.

No corpus, CUDA execution, wall-time claim or class certificate. The only
reused input is an actually owned immutable tuple of declared base Fractions.
"""
from contextlib import nullcontext
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'src/reference_compiler')]

from audit_token_reporting import report_registration
from audit_token_snapshot_bounds import cpu_device, phase_frame
from audit_token_cuda_owner import cuda_contract
from audit_reference_construction import limits, validate_residency
from audit_shared_cuda_retention import STORAGE
from fp_reference import ReferenceCompilerRuntime, runtime
from fp_reference import token_base_facts as facts, token_execution as execution, token_readout as readout
from fp_reference.core import ContractError
from fp_reference.encoding import pack
from fp_reference.resources import ResourceExceeded
from fp_reference.semantics import ArithmeticUnresolved
from fp_reference.ingress import encode_context
from fp_reference.profile import ProfileSpec

CAP = 1 << 20


def rejects(call, errors=(ContractError, ValueError, TypeError, AttributeError)):
    try:
        call()
    except errors:
        return
    raise AssertionError('invalid base-fact continuation admitted')


def outcome(values, bits):
    try:
        return ('VALUE', execution.total(values, bits))
    except ArithmeticUnresolved as error:
        return ('UNRESOLVED', str(error))


def thresholds():
    alphabet = (F(-8), F(-2, 3), F(0), F(1, 7), F(1, 3), F(2, 3), F(9))
    tuples = decisions = 0
    for size in range(5):
        for values in product(alphabet, repeat=size):
            total, required = facts.guarded_fold(values, bit_limit=None)
            assert total == sum(values, F(0))
            for bits in range(1, required+3):
                result = outcome(values, bits)
                assert (result[0] == 'VALUE') == (bits >= required)
                if result[0] == 'VALUE':
                    assert result[1] == total
                    assert facts.guarded_fold(values, bit_limit=bits) == (total, required)
                else:
                    rejects(lambda: facts.guarded_fold(values, bit_limit=bits), ArithmeticUnresolved)
                decisions += 1
            tuples += 1
    values = (F(1, 3), F(2, 3))
    total, required = facts.guarded_fold(values, bit_limit=None)
    assert total == 1 and required == 5 and outcome(values, 4)[0] == 'UNRESOLVED'
    return dict(finite_tuples=tuples, original_guard_decisions=decisions,
        signed_zero_and_positive_inputs=True, all_thresholds_exact=True,
        final_sum_only_counterexample=dict(values=list(map(str, values)), sum=str(total),
            final_integer_width=1, guard_threshold=required, refused_allowance=4))


def setup(enabled, *, unit=2, count=4, profile=False, composed=False):
    cc, program, online, report = report_registration(unit, count, 2)
    cc = replace(cc, limits=limits(256 << 20, 10**14))
    if profile:
        online = replace(online, profiles=(ProfileSpec('reverse-repeat', ('train/3', 'train/0'), 2),))
    rt = ReferenceCompilerRuntime(cc, program, online=online, reporting=report,
        cuda=replace(cuda_contract(cc.initializer_pattern), composed_native=composed),
        shared_storage=replace(STORAGE, token_invariant_bytes=CAP if enabled else 0))
    return rt, program


def trajectory(word, enabled, *, unit=2, profile=False, composed=False):
    with cpu_device(), patch.object(runtime.secrets, 'token_hex', return_value='token-base-facts-control'):
        rt, program = setup(enabled, unit=unit, count=len(word), profile=profile, composed=composed)
        base = program.definition.output.base
        counts, inside = dict(positive_checks=0, guarded_base_additions=0), [False]
        original_exact, original_total, original_add = readout.exact, execution.total, execution.add
        def exact(value, positive=False):
            if positive:
                counts['positive_checks'] += 1
            return original_exact(value, positive=positive)
        def total(values, bits):
            old, inside[0] = inside[0], values is base
            try:
                return original_total(values, bits)
            finally:
                inside[0] = old
        def add(x, y, bits):
            counts['guarded_base_additions'] += int(inside[0])
            return original_add(x, y, bits)
        frozen = []
        with patch.object(readout, 'exact', exact), patch.object(execution, 'total', total), patch.object(execution, 'add', add):
            for i, target in enumerate(word):
                if profile and i == 4:
                    result = rt.construct_candidate(program, profile_id='reverse-repeat')
                    assert result.status == 'BUILT_REFERENCE', result.reason
                result = rt.predict_next(f'train/{i}', encode_context(()))
                assert result.status == 'PREDICTED_REFERENCE', result.reason
                result = rt.observe(target)
                assert result.status == 'OBSERVED_REFERENCE', result.reason
                snap = rt.snapshot()
                frozen.append((snap, tuple(pack(p) for p in snap.cuda.phases)))
                assert not facts.positive_base_known(base) and facts.known_total(base, None) is None
            assert rt.begin_report().status == 'REPORTING'
            for i, target in enumerate((0, 1)):
                assert rt.predict_report(f'report/{i}').status == 'PREDICTED_REPORT'
                result = rt.observe_report(target)
                assert result.status in ('SCORED_REPORT', 'COMPLETE_REPORT'), result.reason
        snap = validate_residency(rt)
        if enabled:
            identity, source, total, threshold, buffer, size = snap.reference_archive.token_base_facts
            assert source is base and identity == facts.FACT_ID
            assert (total, threshold) == facts.guarded_fold(base, bit_limit=None)
            assert dict(snap.buffers)[buffer] == pack((identity, source, total, threshold))
            assert len(dict(snap.buffers)[buffer]) == size <= CAP
            # Both compiler and deployment must carry the same actual artifact.
            owners = rt._ledger._refs[buffer]
            assert rt._data_owner in owners and rt._reference_archive.deployment_owner in owners
        else:
            assert not snap.reference_archive.token_base_facts
        for old, bodies in frozen:
            assert tuple(pack(p) for p in old.cuda.phases) == bodies
        bodies = []
        for phase in snap.cuda.phases:
            assert phase.status == 'CHECKED_CUDA_PREFIX_PHASE'
            body = pack(phase)
            frame = phase_frame(snap, phase.object_id, True)
            assert int.from_bytes(frame[:8], 'big') == len(body) and frame[8:8+len(body)] == body
            bodies.append(body)
        return dict(bodies=tuple(bodies), learners=tuple(c.learner for c in snap.candidates),
            reports=(snap.token_report.native_total, snap.token_report.physical_total), counts=counts,
            checked_words=sum(p.forward_operations for p in snap.cuda.phases))


def histories():
    pairs = phases = words = bytes_checked = 0
    totals = [dict(positive_checks=0, guarded_base_additions=0) for _ in range(2)]
    cases = [(word, 2, False, False) for word in product((0, 1), repeat=4)]
    cases += [((0, 1, 1, 0)*2, 4, False, True), ((0, 1, 1, 0), 1, False, False),
              ((0, 1, 1, 0, 0, 1), 2, True, False)]
    for word, unit, profile, composed in cases:
        left, right = (trajectory(word, enabled, unit=unit, profile=profile, composed=composed) for enabled in (False, True))
        for key in ('bodies', 'learners', 'reports', 'checked_words'):
            assert left[key] == right[key], key
        for i, result in enumerate((left, right)):
            for key, value in result['counts'].items():
                totals[i][key] += value
        assert not any(right['counts'].values()), right['counts']
        pairs += 1
        phases += len(right['bodies'])
        bytes_checked += sum(map(len, right['bodies']))
        words += right['checked_words']
    return dict(paired_histories=pairs, identical_complete_phase_bodies=phases,
        identical_complete_phase_body_bytes=bytes_checked, identical_checked_primitive_words=words,
        identical_complete_learners_and_reports=True, baseline_hot_counts=totals[0], owned_hot_counts=totals[1])


def scope_and_binding():
    with cpu_device():
        rt, program = setup(True)
        other, _ = setup(True)
        base, foreign = program.definition.output.base, other._contract.initializer_pattern.output.base
        fact, second = rt._reference_archive.base_facts, other._reference_archive.base_facts
        assert base is not foreign
        assert not facts.positive_base_known(base)
        def outer():
            assert facts.positive_base_known(base) and not facts.positive_base_known(foreign)
            for bits in (None, *range(1, fact.required_bits+3), 0, -1, True, 'invalid'):
                try:
                    actual = ('VALUE', execution.total(base, bits))
                except Exception as error:
                    actual = (type(error).__name__, str(error))
                # A distinct equal tuple must take every original operation.
                copied = tuple(list(base))
                assert copied is not base
                try:
                    expected = ('VALUE', execution.total(copied, bits))
                except Exception as error:
                    expected = (type(error).__name__, str(error))
                assert actual == expected
            def inner():
                assert facts.positive_base_known(foreign) and not facts.positive_base_known(base)
            second.run(inner)
            def disabled():
                assert not facts.positive_base_known(base) and not facts.positive_base_known(foreign)
            facts._run(None, disabled)
            assert facts.positive_base_known(base)
            rejects(lambda: readout.Spec((F(0), F(1)), 1, 2, F(0), 2), ValueError)
            # Replacing a field in a public frozen wrapper cannot inherit the
            # original tuple's proof, even when tuple length is unchanged.
            spec = readout.Spec(base, 1, 2, F(0), 2)
            spec.__dict__['base'] = (F(-1), F(1))
            rejects(spec.__post_init__, ValueError)
        fact.run(outer)
        assert not facts.positive_base_known(base)
        for error in (RuntimeError, MemoryError):
            def fail():
                raise error('scope fault')
            try:
                fact.run(fail)
            except error:
                pass
            assert not facts.positive_base_known(base)
        # Failure after installing the new variable must restore the original
        # context too; cleanup must not call ContextVar.reset.
        active = facts._ACTIVE
        class FailAfterSet:
            def get(self):
                return active.get()
            def set(self, value):
                active.set(value)
                raise MemoryError('after isolated context binding')
            def reset(self, token):
                raise AssertionError('allocating reset used for failure cleanup')
        with patch.object(facts, '_ACTIVE', FailAfterSet()):
            rejects(lambda: fact.run(lambda: None), MemoryError)
        assert not facts.positive_base_known(base)
        with patch.object(facts, 'copy_context', side_effect=MemoryError('before isolated context')):
            rejects(lambda: fact.run(lambda: None), MemoryError)
        assert not facts.positive_base_known(base)
        snap = rt.snapshot()
        original = fact.snapshot()
        rejects(lambda: snap.reference_archive.token_base_facts.__setitem__(2, F(999)))
        snap.reference_archive.__dict__['token_base_facts'] = ('forged',)
        assert fact.snapshot() == original
        # The real Runtime failure boundary must also clear its dynamic scope.
        assert rt.predict_next('train/0', encode_context(())).status == 'PREDICTED_REFERENCE'
        with patch.object(execution.TokenReferenceMachine, 'observe', side_effect=MemoryError('during actual observation')):
            rejects(lambda: rt.observe(0), MemoryError)
        assert not facts.positive_base_known(base)
        failed = rt.snapshot()
        assert failed.cursor == 0 and failed.observations[-1].target == 0 and failed.halted[0] == 'host-memory'
    return dict(same_identity_only=True, changed_invalid_base_refuses=True, malformed_and_tight_guards_preserved=True,
        distinct_and_disabled_owner_scopes=True, isolated_context_failure_restoration=True,
        snapshot_replacement_has_no_authority=True,
        actual_post_target_memory_failure_retains_target_and_clears_scope=True)


def admissions():
    results = []
    for failure in ('capacity', 'unpaid', 'writer', 'copy-memory'):
        cc, program, online, _ = report_registration()
        cc = replace(cc, limits=limits(256 << 20, 10**14))
        cfg = replace(STORAGE, token_invariant_bytes=1 if failure == 'capacity' else CAP)
        rt = object.__new__(ReferenceCompilerRuntime)
        from fp_reference.resources import ResourceLedger
        if failure == 'unpaid':
            original = ResourceLedger.charge_work
            def deny(self, role, cost, **kwargs):
                if kwargs.get('note') == 'owned-token-base-facts':
                    raise ResourceExceeded('unpaid immutable base facts')
                return original(self, role, cost, **kwargs)
            hook = patch.object(ResourceLedger, 'charge_work', deny)
        elif failure in ('writer', 'copy-memory'):
            original_write = facts.write_packed
            def corrupt(value, buffer):
                original_write(value, buffer)
                if failure == 'copy-memory':
                    raise MemoryError('after base fact writer')
                buffer[0] ^= 1
            hook = patch.object(facts, 'write_packed', corrupt)
        else:
            hook = nullcontext()
        with cpu_device(), hook:
            rejects(lambda: rt.__init__(cc, program, online=online, shared_storage=cfg),
                    (ContractError, MemoryError))
        assert rt._reference_archive is None and not rt._candidates and rt._cuda is None
        assert not facts.positive_base_known(program.definition.output.base)
        if failure in ('writer', 'copy-memory'):
            buffers = [k for k in rt._buffers if 'token-base-facts' in k]
            assert buffers and all(k in rt._ledger._objects for k in buffers)
        results.append(failure)
    return results


def audit():
    exact = thresholds()
    print('PASS exact guard thresholds', flush=True)
    owned = histories()
    print('PASS complete Runtime preservation', flush=True)
    binding, failures = scope_and_binding(), admissions()
    assert 'torch' not in sys.modules
    return dict(status='PASS_OWNED_TOKEN_BASE_FACTS_CPU', exact=exact, owned=owned,
        binding=binding, admission_failures=failures, scope=__doc__.strip())


if __name__ == '__main__':
    if sys.flags.optimize:
        raise RuntimeError('base-fact audit requires assertions')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = audit()
    body = json.dumps(result, indent=2)+'\n'
    if args.write:
        (ROOT/'evidence/minimal/FP_TOKEN_BASE_FACTS_CPU.json').write_text(body, encoding='utf-8')
    print(body)
