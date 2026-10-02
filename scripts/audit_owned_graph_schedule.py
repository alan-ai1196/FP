"""Exact native graph schedule counts and disjoint pending-vector storage.

No corpus, timing, device run, new representation or whole-host fit claim.
Only completed ordinary native histories with their original records count.
"""
from collections import Counter
from dataclasses import replace
from itertools import product
from pathlib import Path
import argparse
import json
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'src/reference_compiler')]
from audit_owned_value_graph_runtime import setup, event
from fp_reference import value_graph as graph


def schedule(t, b, q):
    c, r = divmod(t, b)
    assert 0 <= q <= c
    return dict(pages=5*t+c+q, events=50*t+9*c+10*q+2*bool(t),
        live_objects=12*t+2*c+q, retired_objects=6*t+c+2*q,
        pending_references=c*b*(b+1)//2+r*(r+1)//2,
        forced_new_nodes=13*t+2*c-1 if t else 0)


def counters(rt):
    return dict(pages=len(rt._reference_archive.pages), events=len(rt._ledger._events),
        live_objects=len(rt._ledger._objects), retired_objects=len(rt._ledger._retired))


def inspect(rt, initial_nodes):
    owner, traces = rt._reference_archive, rt._event_traces
    # A passive exact byte-key index; no owner meter/cache is changed.
    index = {raw: i for i, raw in enumerate(owner.reader.index.raw)}
    assert len(index) == len(owner.reader.nodes)
    def root(value):
        return graph._OwnedWalk(index.__getitem__, {}, owner.limits).value(value)[0]
    forced = set()
    for identity in rt._ingress_identities.values():
        forced.add(root(identity))
        forced.update(root(getattr(identity, key)) for key in
            ('ingress_id', 'body_id', 'control_id', 'record_id'))
    vector_roots, containers, integers = set(), {}, {}
    references = selected = q = 0
    for record, trace in zip(rt._observations, traces):
        values = (record.sources, replace(record, target=None), trace.prediction,
            replace(trace, after_commit=None), trace.after_observe,
            trace.after_observe.windows,
            (trace.candidate_id, trace.program_id, trace.before, trace.prediction),
            trace.prediction.window)
        forced.update(map(root, values))
        if trace.after_commit is not None:
            forced.update((root(trace), root(trace.after_commit)))
            q += trace.before.theta != trace.after_commit.theta
        windows, targets = trace.after_observe.windows, trace.after_observe.targets
        node = root(windows)
        assert node not in vector_roots and node >= initial_nodes
        vector_roots.add(node)
        tag, children = owner.reader.nodes[node]
        assert tag == b'u' and len(children) == len(windows) == len(targets)
        assert all(type(n) is int and n > 256 for n in children)
        left, right = owner.encoder.index.raw[node], owner.reader.index.raw[node]
        assert left == right == graph.vector(b'u', children)
        assert left is not right
        # Count only actual live objects, once by identity. No temporary raw
        # slice or decoded source object contributes an allocation here.
        for value in (left, right, children, windows, targets):
            assert id(value) not in containers
            containers[id(value)] = value
        for value in children:
            assert id(value) not in integers
            integers[id(value)] = value
        references += len(children)
        # Each selected definition occupies a disjoint length/tag/reference
        # extent in its actual immutable page. Page headers are excluded.
        selected += 8+len(right)
    assert not containers.keys() & integers.keys()
    selected += sum(map(sys.getsizeof, containers.values()))
    selected += sum(map(sys.getsizeof, integers.values()))
    assert sum(n >= initial_nodes for n in forced) >= (13*len(traces)+2*sum(
        trace.after_commit is not None for trace in traces)-1 if traces else 0)
    assert selected == 76*references+197*len(traces)
    return dict(changed_commits=q, pending_references=references,
        selected_live_bytes=selected, distinct_selected_containers=len(containers),
        distinct_parsed_reference_integers=len(integers),
        forced_new_nodes=sum(n >= initial_nodes for n in forced))


def abi():
    assert sys.implementation.name == 'cpython' and struct.calcsize('P') == 8
    assert sys.getsizeof(()) == 40 and sys.getsizeof((None,)) == 48
    assert sys.getsizeof(b'') == 33 and sys.getsizeof(bytes(9)) == 42
    pair = tuple(x[0] for x in struct.iter_unpack('>Q', struct.pack('>2Q', 1000, 1000)))
    assert pair[0] == pair[1] and pair[0] is not pair[1]
    assert all(sys.getsizeof(n) == 28 for n in pair)
    # An occurrence count cannot stand in for distinct objects in this ABI.
    shared = tuple([1000]*8)
    assert len({id(shared) for _ in range(10)}) == 1
    assert len({id(n) for n in shared}) == 1
    return dict(implementation=sys.implementation.name, version=sys.version.split()[0],
        pointer_bytes=8, tuple_header_bytes=40, bytes_header_bytes=33,
        selected_integer_bytes=28, shared_occurrences_not_counted_as_new_objects=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if not __debug__:
        parser.error('assertions required')
    layout, totals = abi(), Counter()
    # All 93 binary histories through length four, plus complete longer units
    # so both several commits and nontrivial pending vectors are exercised.
    cases = [(b, word) for b in (1, 2, 4) for t in range(5) for word in product((0, 1), repeat=t)]
    cases += [(b, word) for b in (1, 2, 4, 8) for word in ((0,)*16, tuple(i%2 for i in range(16)))]
    for b, word in cases:
        rt = setup(unit=b, count=max(1, (len(word)+b-1)//b)*b, memo=128)
        start, initial_nodes = counters(rt), len(rt._reference_archive.reader.nodes)
        for i, target in enumerate(word):
            event(rt, i, target)
        measured = inspect(rt, initial_nodes)
        expected = schedule(len(word), b, measured['changed_commits'])
        for key, now in counters(rt).items():
            assert now-start[key] == expected[key], (b, word, key, now-start[key], expected[key])
        assert measured['pending_references'] == expected['pending_references']
        assert measured['forced_new_nodes'] >= expected['forced_new_nodes']
        totals['histories'] += 1
        totals['targets'] += len(word)
        totals['commits'] += len(word)//b
        for key in ('pending_references', 'selected_live_bytes', 'forced_new_nodes'):
            totals[key] += measured[key]
    t, b, host = 1 << 20, 512, 96 << 30
    low, high = schedule(t, b, 0), schedule(t, b, t//b)
    full = dict(train=t, update_unit=b, commits=t//b,
        schedule_lower=low, schedule_upper=high,
        pending_vector_wire_bytes=9*t+8*low['pending_references'],
        pending_vector_selected_live_byte_lower=76*low['pending_references']+197*t,
        qualification_node_cap=1 << 22, qualification_cap_cannot_complete=True,
        host_cap=host, whole_host_fit='UNRESOLVED', whole_host_exclusion_proved=False,
        actual_time_or_model_result=False)
    assert low['forced_new_nodes'] > full['qualification_node_cap']
    assert full['pending_vector_selected_live_byte_lower'] < host
    result = dict(status='PASS_OWNED_GRAPH_SCHEDULE_CPU', scope=__doc__.strip(),
        abi=layout, exact_histories=dict(totals), full_native_schedule=full)
    if args.output is not None:
        with args.output.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(result, indent=2)+'\n')
    else:
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
