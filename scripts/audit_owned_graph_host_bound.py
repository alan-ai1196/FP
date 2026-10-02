"""Disjoint host-allocation lower for the qualified ordinary native graph.

Conditional on the installed CPython 3.12 x64 standard pymalloc realization.
No corpus, device, timing, universal memory optimum or completed model claim.
"""
from collections import Counter
from dataclasses import fields, replace
from itertools import product
from pathlib import Path
from types import MappingProxyType
import argparse
import ctypes
import gc
import json
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'src/reference_compiler')]
from audit_owned_value_graph_runtime import setup, event
from audit_owned_graph_schedule import schedule
from fp_reference import value_graph as graph
from fp_reference.owned_maps import _walk
from fp_reference.resources import ResourceEvent


def rounded(n):
    return (n+15)//16*16 if n <= 512 else n


def abi():
    assert __debug__ and sys.implementation.name == 'cpython' and sys.version_info[:2] == (3, 12)
    assert struct.calcsize('P') == 8
    name = ctypes.pythonapi._PyMem_GetCurrentAllocatorName
    name.argtypes, name.restype = [], ctypes.c_char_p
    assert name() == b'pymalloc'
    assert (sys.getsizeof(''), sys.getsizeof(b''), sys.getsizeof(())) == (41, 33, 40)
    return dict(version=sys.version.split()[0], pointer_bytes=8, small_block_quantum=16,
        actual_mem_obj_allocator=name().decode('ascii'),
        standard_arena_allocator_is_an_explicit_premise=True)


def lower(t, b, context, masters, nodes_per_prediction, report_ids, distinct, non_small):
    """Selected lower, not an upper estimate. Changed-master count is zero."""
    assert t > 0 and 0 < distinct <= t and 0 <= non_small <= distinct*context
    s = schedule(t, b, 0)
    m, o, i, j, w = (s[k] for k in ('pages', 'live_objects', 'retired_objects', 'events', 'pending_references'))
    c = t//b
    n = 14*t+report_ids+2*c-1+distinct
    result = dict(
        pending_vectors=197*t+80*w,
        lease_and_buffer_metadata=1328*o+64*max(0, o-257),
        retired_index_metadata=256*i+32*max(0, i-257),
        resource_event_shells=176*j+32*max(0, j-257),
        event_object_tuples=48*(7*m+4*t+1),
        event_debit_tuples=112*(5*m+7*t+2*c+2),
        forced_record_definitions=sum((117+32*k)*count for k, count in
            ((12,t),(6,t),(10,t),(9,t),(10,t+c),(6,t+c),(4,t),(6,t-1))),
        private_name_definitions=1108*t,
        original_private_names=323*t,
        declared_train_name_definitions=146*t,
        page_headers=73*m,
        surviving_root_buffers=73*(4*t+c),
        original_ingress_payload=4096*t,
        committed_master_payload=4*masters*c,
        original_context_tuples=(40+8*context)*t,
        native_record_shells=48*(7*t+c)+264*t+24*c+64*(6*t+c),
        captured_containers=(120+8*nodes_per_prediction)*t,
        executed_fraction_shells=48*nodes_per_prediction*t,
        graph_node_metadata=216*n+64*max(0,n-257),
        distinct_context_definitions=117*distinct+32*distinct*context+32*non_small)
    return result


class Selection:
    """A passive set of actual live allocations; a duplicate invalidates a sum."""
    def __init__(self):
        self.seen, self.amounts = {}, Counter()

    def add(self, group, value, amount=None):
        if id(value) in self.seen:
            raise AssertionError(('double counted actual allocation', group, self.seen[id(value)][0], type(value)))
        self.seen[id(value)] = group, value
        size = rounded(sys.getsizeof(value))
        assert amount is None or amount <= size
        self.amounts[group] += size if amount is None else amount

    def integer(self, group, value):
        if value > 256:
            assert type(value) is int and sys.getsizeof(value) >= 28
            self.add(group, value, 32)

    def managed(self, group, value, cell_bytes, *, materialized=False):
        # Attribute reads and GC traversal do not request __dict__.
        before = tuple(x for x in gc.get_referents(value) if type(x) is dict)
        assert all(hasattr(value, field.name) for field in fields(value))
        self.add(group, value, 48)
        self.amounts[group] += cell_bytes
        if materialized:
            assert len(before) == 1
            self.add(group, before[0], 64)  # shell only; attribute cells counted above
        assert tuple(x for x in gc.get_referents(value) if type(x) is dict) == before

    def mapping(self, group, value):
        assert type(value) is MappingProxyType
        self.add(group, value, 48)
        referents = gc.get_referents(value)
        assert len(referents) == 1 and type(referents[0]) is dict
        self.add(group, referents[0], 192)

    def owned_map(self, group, value, *, weighted=False):
        for node in _walk(value._version.lookup):
            self.add(group, node, 96)
            self.add(group, node.value, 64)
            self.integer(group, node.value.ordinal)
            if weighted:
                assert len(node.weight) == len(node.total) == 6
                self.add(group, node.weight, 96)
                self.add(group, node.total, 96)
        for node in _walk(value._version.order):
            self.add(group, node, 96)


def inspect(rt):
    select, a, ledger = Selection(), rt._reference_archive, rt._ledger
    for source in (ledger._leases, rt._buffers):
        select.owned_map('lease_and_buffer_metadata', source, weighted=source is ledger._leases)
    for lease in ledger._leases.values():
        select.add('lease_and_buffer_metadata', lease, 48)
        select.mapping('lease_and_buffer_metadata', lease.refs)
        select.managed('lease_and_buffer_metadata', lease.spec, 48)
        select.mapping('lease_and_buffer_metadata', lease.spec.residency)
    select.owned_map('retired_index_metadata', ledger._retired)
    tail = ledger._events._tail
    while tail is not None:
        resource, previous = tail
        select.add('resource_event_shells', tail, 64)
        select.managed('resource_event_shells', resource, 64)
        select.integer('resource_event_shells', resource.sequence)
        if resource.object_ids:
            select.add('event_object_tuples', resource.object_ids, 48)
        if resource.debit:
            assert len(resource.debit) == 1
            select.add('event_debit_tuples', resource.debit, 48)
            select.add('event_debit_tuples', resource.debit[0], 64)
        tail = previous
    for node, metric in zip(a.reader.nodes, a.reader.metrics):
        select.add('graph_node_metadata', node, 64)
        select.managed('graph_node_metadata', metric, 48)
    for values in (a.encoder.index.raw, a.reader.index.raw, a.reader.nodes, a.reader.metrics, a.reader.references):
        select.add('graph_node_metadata', values, 8*len(values))
    for index in (a.encoder.index, a.reader.index):
        for values in index.buckets.values():
            select.add('graph_node_metadata', values, 8*len(values))
            for value in values:
                select.integer('graph_node_metadata', value)
    index = {raw: n for n, raw in enumerate(a.reader.index.raw)}
    root = lambda value: graph._OwnedWalk(index.__getitem__, {}, a.limits).value(value)[0]
    selected_nodes = set()
    def definition(group, node):
        assert node not in selected_nodes
        selected_nodes.add(node)
        select.add(group, a.encoder.index.raw[node])
        select.add(group, a.reader.index.raw[node])
        select.amounts[group] += 8+len(a.reader.index.raw[node])
        tag, value = a.reader.nodes[node]
        select.add(group, value)
        return tag, value
    for identity in rt._ingress_identities.values():
        definition('forced_record_definitions', root(identity))
        for key in ('ingress_id','body_id','control_id','record_id'):
            value = getattr(identity,key)
            definition('private_name_definitions', root(value))
            select.add('original_private_names', value)
    for name in rt._online.data.active.observation_ids:
        definition('declared_train_name_definitions', root(name))
    contexts, non_small = set(), 0
    for record, trace in zip(rt._observations, rt._event_traces):
        native = (record, record.sources, trace.prediction.window, trace.after_observe,
                  trace.prediction, trace, trace.prediction.probabilities)
        for value in native:
            select.managed('native_record_shells', value, 8*len(fields(value)), materialized=value is not record)
        if trace.after_commit is not None:
            select.managed('native_record_shells', trace.after_commit, 24, materialized=True)
            for key in ('embedding','core','output'):
                value = getattr(trace.after_commit.origin,key)
                select.add('committed_master_payload',value,len(value))
        values = (record.sources,replace(record,target=None),trace.prediction,
            replace(trace,after_commit=None),trace.after_observe,
            (trace.candidate_id,trace.program_id,trace.before,trace.prediction),trace.prediction.window)
        for value in values:
            definition('forced_record_definitions',root(value))
        if trace.after_commit is not None:
            definition('forced_record_definitions',root(trace))
            definition('forced_record_definitions',root(trace.after_commit))
        tag, children = definition('pending_vectors',root(trace.after_observe.windows))
        assert tag == b'u' and all(value > 256 for value in children)
        for value in children:
            select.integer('pending_vectors',value)
        for value in (trace.after_observe.windows,trace.after_observe.targets):
            select.add('pending_vectors',value)
        past = record.sources.past
        select.add('original_context_tuples',past)
        node = root(past)
        if node not in contexts:
            contexts.add(node)
            tag, children = definition('distinct_context_definitions',node)
            assert tag == b'u'
            for value in children:
                select.integer('distinct_context_definitions',value)
                non_small += value > 256
        capture = trace.prediction.values
        tail = tuple.__getitem__(capture,4)
        for value in (capture,tail):
            select.add('captured_containers',value)
        for value in tail:
            select.add('executed_fraction_shells',value,48)
    for key in a.pages:
        select.add('page_headers',rt._buffers[key],73)
    for key,spec in ledger._objects.items():
        if spec.kind.startswith('shared_reference_root:'):
            select.add('surviving_root_buffers',rt._buffers[key],73)
        elif spec.kind == 'reserved_context':
            select.add('original_ingress_payload',rt._buffers[key],len(rt._buffers[key]))
    return dict(select.amounts), len(contexts), non_small


def parsed_context_control():
    limits = graph.Limits(nodes=1024, page_bytes=32768)
    producer, reader = graph.Producer(limits), graph.Reader(limits)
    producer.begin(bytearray(limits.page_bytes))
    for value in range(512):
        assert graph.U64.unpack(producer.send(b'i'+format(value, 'x').encode()))[0] == value
    contexts = (tuple(range(512)), (300,)*512)
    roots = [graph.U64.unpack(producer.send(graph.vector(b'u', past)))[0] for past in contexts]
    producer.finish(graph.U64.pack(roots[-1]))
    output = bytearray(producer.extent)
    producer.write(output)
    producer.accept()
    reader.add(bytes(output))
    selection, non_small = Selection(), 0
    for node in roots:
        for raw in (producer.index.raw[node], reader.index.raw[node]):
            selection.add('contexts', raw)
        selection.amounts['contexts'] += 8+len(reader.index.raw[node])
        tag, children = reader.nodes[node]
        assert tag == b'u'
        selection.add('contexts', children)
        for value in children:
            selection.integer('contexts', value)
            non_small += value > 256
    assert non_small == 767
    assert selection.amounts['contexts'] >= 117*2+32*2*512+32*non_small
    return dict(distinct_contexts=2, non_small_reference_allocations=non_small,
        disjoint_selected_allocation_lower=selection.amounts['contexts'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    layout = abi()
    # Necessity control: a dict requested by the observer is not original heap.
    witness=ResourceEvent(1000,'control','control',(),(),'control')
    assert not any(type(x)is dict for x in gc.get_referents(witness))
    vars(witness)
    assert sum(type(x)is dict for x in gc.get_referents(witness))==1
    parsed_contexts = parsed_context_control()
    cases=[(b,word) for b in (1,2,4) for word in product((0,1),repeat=4)]
    cases += [(b,(0,)*16) for b in (1,2,4,8)]
    totals=Counter()
    for b,word in cases:
        rt=setup(unit=b,count=len(word),memo=128)
        for i,target in enumerate(word): event(rt,i,target)
        measured,d,non_small=inspect(rt)
        # Check every term against disjoint actual allocations. Initial
        # metadata is included by the observer but omitted by the lower.
        spec=rt._contract.initializer_pattern
        expected=lower(len(word),b,spec.sources.context,rt._candidates[rt._deployed_id].learner.origin.definition.slot_count,
            len(rt._programs[rt._candidates[rt._deployed_id].program_id].definition.nodes),2,d,non_small)
        for key,value in expected.items():
            assert measured.get(key,0)>=value,(key,measured.get(key,0),value,b,word)
        totals['histories']+=1
        totals['targets']+=len(word)
        totals['distinct_contexts']+=d
        totals['non_small_context_references']+=non_small
        totals['disjoint_selected_allocation_lower']+=sum(measured.values())
    assert abi() == layout
    result=dict(status='PASS_OWNED_GRAPH_HOST_BOUND_CPU',scope=__doc__.strip(),
        abi=layout, observer_materialization_control=True, all_lower_terms_checked=True,
        finite_controls=dict(totals), parsed_context_control=parsed_contexts,
        corpus_census_performed=False,whole_host_exclusion_proved=False)
    if args.output:
        with args.output.open('x',encoding='utf-8') as stream: stream.write(json.dumps(result,indent=2)+'\n')
    else: print(json.dumps(result,indent=2))


if __name__=='__main__': main()
