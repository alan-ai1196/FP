"""Exact and complete owner controls for bounded byte comparison copies.

Only the two comparison implementations differ from committed source.
No corpus, CUDA context, model change or performance certificate.
"""
from contextlib import contextmanager, nullcontext
from itertools import product
from pathlib import Path
from types import FunctionType, SimpleNamespace
from unittest.mock import patch
import argparse
import ast
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts')]
from fp_reference import byte_archive as archive, shared_reference as shared
from fp_reference.core import ContractError
from fp_reference.resources import ResourceExceeded

PREVIOUS = 'd37f9396e91fb3be7ae774e3b6a02f5d8cac05bf'
PATHS = ('src/reference_compiler/fp_reference/byte_archive.py',
         'src/reference_compiler/fp_reference/shared_reference.py')


def previous_sources():
    return {path: subprocess.check_output(['git', 'show', PREVIOUS+':'+path],
        cwd=ROOT, encoding='utf-8') for path in PATHS}


def previous(sources=None):
    sources = previous_sources() if sources is None else sources
    result = []
    for path, owner, method, module in ((PATHS[0], 'Builder', '_compare', archive),
                                       (PATHS[1], None, '_compare_stream', shared)):
        tree = ast.parse(sources[path])
        nodes = tree.body if owner is None else next(
            node.body for node in tree.body if isinstance(node, ast.ClassDef) and node.name == owner)
        node = next(n for n in nodes if isinstance(n, ast.FunctionDef) and n.name == method)
        namespace = dict(vars(module))
        exec(compile(ast.Module(body=[node], type_ignores=[]),
                     'git:'+PREVIOUS+':'+path, 'exec'), namespace)
        result.append(namespace[method])
    return tuple(result)


@contextmanager
def previous_comparisons(old):
    with patch.object(archive.Builder, '_compare', old[0]), \
            patch.object(shared, '_compare_stream', old[1]):
        yield


def outcome(call):
    try:
        return 'VALUE', call()
    except (ContractError, ResourceExceeded) as error:
        return type(error).__name__, str(error)


def candidates(old):
    checks = 0
    for a, b, budget in product(range(256), range(256), (0, 1)):
        left, right = memoryview(bytes((17, a, 19)))[1:2], bytes((b,))
        rows = []
        for compare in (old[0], archive.Builder._compare):
            state = SimpleNamespace(comparison_bytes=3, _comparison_cap=3+budget)
            value = outcome(lambda: compare(state, left, right))
            rows.append((value, state.comparison_bytes))
        assert rows[0] == rows[1]
        assert rows[0] == ((('VALUE', a == b), 4) if budget else
            (('ResourceExceeded', 'archive exact-comparison allowance exhausted'), 3))
        checks += 1
    raw = bytes(range(256))*32
    for backing in (raw, bytearray(raw)):
        for right in (raw, bytes((raw[0] ^ 1,))+raw[1:], raw[:-1]+b'\0'):
            for budget in (8191, 8192, 8193):
                rows = []
                for compare in (old[0], archive.Builder._compare):
                    state = SimpleNamespace(comparison_bytes=0, _comparison_cap=budget)
                    rows.append((outcome(lambda: compare(state, memoryview(backing), right)),
                                 state.comparison_bytes))
                assert rows[0] == rows[1]
                checks += 1
    # Narrow the theorem: numeric equality on signed views is not byte equality.
    signed = memoryview(b'\xff').cast('b')
    assert (signed == b'\xff') is False and bytes(signed) == b'\xff'
    return dict(exact_candidate_decisions=checks,
        comparison_debits_and_refusals_identical=True, signed_view_counterexample=True)


def partitions(raw):
    if not raw:
        return [()]
    result = []
    for mask in range(1 << (len(raw)-1)):
        cuts = [0]+[i for i in range(1, len(raw)) if mask & (1 << (i-1))]+[len(raw)]
        result.append(tuple(raw[a:b] for a, b in zip(cuts, cuts[1:])))
    return result


def streams(old):
    variants = []
    for n in range(5):
        for row in product((0, 255), repeat=n):
            raw = bytes(row)
            variants.extend((raw, parts) for parts in partitions(raw))
    checks = 0
    def tracked(side, parts, log):
        for i, part in enumerate(parts):
            log.append((side, i))
            yield memoryview(part) if side == 'actual' else part
        log.append((side, 'end'))
    for (left, a), (right, b) in product(variants, repeat=2):
        # Include empty chunks without changing the stream, and retain the
        # exact next()/end trace even on early mismatch or size refusal.
        a, b = (b'', *a, b''), (b'', *b, b'')
        for declared in sorted({len(left), len(right), max(len(left), len(right))+1}):
            rows = []
            for compare in (old[1], shared._compare_stream):
                log = []
                result = outcome(lambda: compare(tracked('actual', a, log),
                    tracked('expected', b, log), declared))
                rows.append((result, tuple(log)))
            assert rows[0] == rows[1]
            assert (rows[0][0][0] == 'VALUE') == (left == right and len(left) == declared)
            checks += 1
    # Copying ahead of next(expected) is not equivalent on mutable input
    # whose owner can change it during that call. Reader's immutable pages
    # exclude this case; the exclusion is a real premise, not a general law.
    result = []
    for compare in (old[1], shared._compare_stream):
        raw = bytearray(b'a')
        def expected():
            raw[0] = ord('b')
            yield b'b'
        result.append(outcome(lambda: compare((memoryview(raw),), expected(), 1)))
    assert result[0] == ('VALUE', None) and result[1][0] == 'ContractError'
    return dict(binary_stream_variants=len(variants), exhaustive_partition_decisions=checks,
        independent_iterator_order_identical=True, mutable_input_counterexample=True)


def pages(old):
    from audit_shared_token_retention import raw_pages
    rows = []
    for legacy in (True, False):
        retained, calls = [], []
        with (previous_comparisons(old) if legacy else nullcontext()):
            add, compare = archive.Encoder.add, archive.Builder._compare
            def record(self, raw):
                retained.append(raw)
                return add(self, raw)
            def compared(self, left, right):
                before = self.comparison_bytes
                result = outcome(lambda: compare(self, left, right))
                calls.append((len(right), before, result, self.comparison_bytes))
                if result[0] != 'VALUE':
                    raise ResourceExceeded(result[1])
                return result[1]
            with patch.object(archive.Encoder, 'add', record), \
                    patch.object(archive.Builder, '_compare', compared):
                report = raw_pages()
        rows.append((tuple(retained), tuple(calls), report))
    assert rows[0] == rows[1]
    return dict(**rows[0][2], exact_page_bytes_identical=True,
                identical_ordered_candidate_comparisons=len(rows[0][1]))


def runtime_controls(old):
    import audit_owned_token_workspaces as owned
    from fp_reference.encoding import pack
    cases = [((0, 1, 1, 0), unit, False, False, False) for unit in (1, 2, 4)]
    cases += [((0, 1, 1, 0)*2, 8, False, False, False),
              ((0, 1, 1, 0, 0, 1), 2, True, False, False),
              ((0, 1, 1, 0)*2, 4, False, True, True)]
    phases = retained = words = raw_calls = raw_bytes = page_count = page_bytes = 0
    for word, unit, profile, combined, archived in cases:
        rows = []
        for legacy in (True, False):
            emitted, add = [], archive.Encoder.add
            def capture(self, raw):
                emitted.append(raw)
                return add(self, raw)
            with (previous_comparisons(old) if legacy else nullcontext()), \
                    patch.object(archive.Encoder, 'add', capture), \
                    patch.object(owned, 'numerical_phase', pack):
                result = owned.trajectory(word, archived, unit=unit, profile=profile, combined=combined)
            rows.append((result, tuple(emitted)))
        assert rows[0] == rows[1]
        result, emitted = rows[0]
        phases += len(result['phases'])
        retained += sum(map(len, result['phases']))
        words += result['primitive_words']
        raw_calls += result['raw_calls']
        raw_bytes += result['raw_bytes']
        page_count += len(emitted)
        page_bytes += sum(map(len, emitted))
    return dict(paired_histories=len(cases), complete_phase_bodies=phases,
        complete_phase_bytes=retained, checked_primitive_words=words,
        identical_raw_calls=raw_calls, identical_raw_bytes=raw_bytes,
        identical_archive_pages=page_count, identical_archive_page_bytes=page_bytes,
        full_frames_learners_reports_allocations_and_retirements_equal=True)


def failing_copy(function, calls):
    def denied(*args, **kwargs):
        calls.append(1)
        raise MemoryError('bounded comparison copy allocation failed')
    return FunctionType(function.__code__, dict(function.__globals__, bytes=denied),
                        function.__name__, function.__defaults__, function.__closure__)


def failures():
    import audit_owned_token_workspaces as owned
    from audit_reference_construction import validate_residency
    from fp_reference.ingress import encode_context
    rows = []
    for target in ('intern', 'stream'):
        for stage in ('native', 'frame'):
            with owned.cpu_device():
                rt, _ = owned.setup(False, unit=4, count=4)
                assert rt.predict_next('train/0', encode_context(())).status == 'PREDICTED_REFERENCE'
                before, calls = rt.snapshot(), []
                owner, name = ((archive.Builder, '_compare') if target == 'intern' else
                               (shared, '_compare_stream'))
                broken = failing_copy(getattr(owner, name), calls)
                seal = shared._SharedReference.seal_cuda_frame
                def during_frame(*args, **kwargs):
                    with patch.object(owner, name, broken):
                        return seal(*args, **kwargs)
                hook = (patch.object(owner, name, broken) if stage == 'native' else
                        patch.object(shared._SharedReference, 'seal_cuda_frame', during_frame))
                with hook:
                    try:
                        rt.observe(1)
                    except MemoryError:
                        pass
                    else:
                        raise AssertionError('comparison copy MemoryError did not escape')
                after = validate_residency(rt)
                assert calls and after.halted and after.cursor == 0
                assert after.observations[-1].target == 1
                assert after.candidates[0].learner == before.candidates[0].learner
                assert after.cuda.current == before.cuda.current and after.cuda.predicted == before.cuda.predicted
                if stage == 'frame':
                    assert rt._cuda.arena._pins
                owned.reject(lambda: rt.predict_next('train/1', encode_context(())))
                rows.append(target+'-'+stage)
    # Explicit comparison credit must be checked before even attempting copy.
    calls = []
    check = failing_copy(archive.Builder._compare, calls)
    state = SimpleNamespace(comparison_bytes=1, _comparison_cap=1)
    assert outcome(lambda: check(state, memoryview(b'a'), b'a'))[0] == 'ResourceExceeded'
    assert not calls and state.comparison_bytes == 1
    from audit_shared_token_retention import funding_boundary, failures as native_failures
    return dict(post_target_copy_memory_failures=rows, target_and_old_learner_retained=True,
        comparison_credit_precedes_copy=True, unpaid_body=funding_boundary(),
        native_faults=native_failures())


def audit():
    old = previous()
    result = dict(candidates=candidates(old), streams=streams(old), pages=pages(old))
    print('PASS exact byte, partition, collision and decision controls', flush=True)
    # This component explicitly requires no Torch import. Keep its scope
    # intact before the complete Runtime controls bind real CPU tensors.
    from audit_shared_cuda_retention import cpu as frame_controls
    result['complete_frame_faults'] = frame_controls()
    result['runtime'] = runtime_controls(old)
    print('PASS complete paired Runtime histories and actual page bytes', flush=True)
    result['failures'] = failures()
    import torch
    assert not torch.cuda.is_initialized()
    return dict(status='PASS_BOUNDED_BYTE_COMPARISONS_CPU', previous_source=PREVIOUS,
                scope=__doc__.strip(), **result)


if __name__ == '__main__':
    if sys.flags.optimize:
        raise RuntimeError('byte comparison audit requires assertions')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = audit()
    body = json.dumps(result, indent=2)+'\n'
    if args.write:
        (ROOT/'evidence/minimal/FP_BYTE_COMPARISONS_CPU.json').write_text(body, encoding='utf-8')
    print(body)
