"""A solver's writable scratch must not carry unpaid resize authority."""
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts')]
from fp_reference import ReferenceCompilerRuntime, query_order
from audit_indexed_runtime import fixture
from audit_indexed_source_binding import predict, native


def probe(expect):
    cfg, schema, online = fixture(3, 3)
    rt = ReferenceCompilerRuntime(replace(cfg, indexed_order_search=True), schema, online=online)
    assert predict(rt, schema, (0, 1)).status == 'PREDICTED_REFERENCE'
    assert rt.observe(0).status == 'OBSERVED_REFERENCE'
    before = rt.snapshot()
    assert all(type(b) is bytes for _, b in before.buffers)
    old_storage = next(b for k, b in before.buffers if 'query-order-storage' in k)
    retained, attempts = [], []
    original = query_order.search
    def changed(n, support, query, join, live, workspace, **kwargs):
        backing = workspace.obj if type(workspace) is memoryview else workspace
        # On the second call, use only the handle retained from the first.
        target = retained[0] if retained else backing
        try:
            target.extend(b'x')
            attempts.append('RESIZED')
        except BufferError:
            attempts.append('RESIZE_BLOCKED')
        retained.append(backing)
        return original(n, support, query, join, live, workspace, **kwargs)
    history = ((0, 1, 0),)
    with patch.object(query_order, 'search', changed):
        for k in range(2):
            assert predict(rt, schema, (0, 1)).status == 'PREDICTED_REFERENCE'
            expected, _ = native(schema, history, (0, 1))
            assert rt.snapshot().pending.predictions[0][1].materialize(scalar_cap=1000) == expected
            if k == 0:
                assert rt.observe(0).status == 'OBSERVED_REFERENCE'
                history += ((0, 1, 0),)
    after = rt.snapshot()
    key, value = next((k, b) for k, b in after.buffers if 'query-order-storage' in k)
    billed = after.resources['objects'][key]['residency']['reference_payload_bytes']
    mismatch = sum(len(b) for _, b in after.buffers)-after.resources['current']['reference_payload_bytes']
    assert old_storage == next(b for k, b in before.buffers if 'query-order-storage' in k)
    assert after.cursor == 2 and after.pending.record.target is None
    if expect == 'unbounded':
        assert attempts == ['RESIZED', 'RESIZED'] and len(value) == billed+2 and mismatch == 2
    else:
        assert attempts == ['RESIZE_BLOCKED', 'RESIZE_BLOCKED'] and len(value) == billed and mismatch == 0
    return {'status': 'UNPAID_SCRATCH_RESIZE_COUNTEREXAMPLE' if expect == 'unbounded' else 'PASS_PINNED_SCRATCH_FRAME',
        'scope': 'actual CPU Runtime; supplied scratch and a later retained backing handle only; no owner globals or native-input mutation',
        'attempts': attempts, 'billed_scratch_bytes': billed, 'actual_scratch_bytes': len(value),
        'unpaid_payload_bytes': mismatch, 'published_correct_native_forecasts': 2,
        'ordinary_cursor': after.cursor, 'next_target_revealed': False,
        'earlier_snapshot_bytes_unchanged': True}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--expect', choices=('unbounded', 'bounded'), required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = probe(args.expect)
    if args.output:
        assert not args.output.exists(), 'retain each source-bound outcome separately'
        args.output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
