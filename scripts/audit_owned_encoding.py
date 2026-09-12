"""Injective source identity and materialization before/after exact audits.

Historical serializers and Runtime execute from Git. Allocation tracing is
a lower diagnostic of traced Python blocks, not total heap or device memory.
"""
from dataclasses import dataclass, fields, replace
from enum import Enum
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from types import SimpleNamespace
import argparse
import gc
import hashlib
import json
import sys
import tracemalloc
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts')]

import fp_reference.core as core
import fp_reference.machine as machine
import fp_reference.program as programs
import fp_reference.runtime as execution
from fp_reference.encoding import fragments, packed_size, write_packed
from fp_reference.ingress import encode_context
from fp_reference.program import Program, Source, SourceSpec, Sum, Term
from fp_reference.resources import ResourceExceeded
from audit_control_admission import historical_modules
from audit_reference_construction import contract, limits, rejects, validate_residency, zero_program
from audit_reference_events import online
from audit_cpu_installation import SMALL
from audit_reference_search import runtime_fixture as search_fixture


HISTORICAL = '532d713'


def old_serializers():
    modules = historical_modules(HISTORICAL, ('fp_reference.core', 'fp_reference.machine'))
    return modules['fp_reference.core'], modules['fp_reference.machine']


def source_case(rt_module):
    first, second = '\U0001f600', '\ud83d\ude00'
    graphs = tuple(Program((Source(name), Sum('mass', ())), 0, (0, 1)) for name in (first, second))
    cfg = contract(source_domain=False)
    cfg = replace(cfg, semantics=replace(cfg.semantics, sources=tuple(
        SourceSpec(name, 'mass', 0, F(1)) for name in (first, second))))
    registered = rt_module.ConstructionContract(**{f.name: getattr(cfg, f.name) for f in fields(cfg)})
    run = online(cfg, 2, unit=2, grid=16)
    run = rt_module.OnlineContract(run.data, run.learner)
    rt = rt_module.ReferenceCompilerRuntime(registered, graphs[0], online=run)
    return rt, graphs


def identity_audit():
    old_core, old_machine = old_serializers()
    with patch.object(core, 'stable_hash', old_core.stable_hash), patch.object(programs, 'stable_hash', old_core.stable_hash):
        old = historical_modules(HISTORICAL, ('fp_reference.machine', 'fp_reference.runtime'))['fp_reference.runtime']
        rt, (first, second) = source_case(old)
        initial = rt.snapshot()
        assert first != second and first.program_id == second.program_id
        assert old_machine.pack(first) == old_machine.pack(second)
        result = rt.construct_candidate(second)
        assert result.status == 'BUILT_REFERENCE'
        assert rt.snapshot().deployed_id == initial.deployed_id
        assert dict(rt.snapshot().programs)[first.program_id] == second
        forecast = rt.predict_next('observation-0', encode_context((1, 0)))
        assert forecast.status == 'PREDICTED_REFERENCE'
        wrong_probability = dict(forecast.predictions)[initial.deployed_id][0]
        assert wrong_probability == F(1, 2) != F(2, 3)
    rt, (first, second) = source_case(execution)
    initial = rt.snapshot()
    assert first.program_id != second.program_id and machine.pack(first) != machine.pack(second)
    result = rt.construct_candidate(second)
    assert result.status == 'BUILT_REFERENCE'
    assert dict(rt.snapshot().programs)[first.program_id] == first
    forecast = rt.predict_next('observation-0', encode_context((1, 0)))
    probabilities = dict(forecast.predictions)
    assert probabilities[initial.deployed_id][0] == F(2, 3)
    assert probabilities[result.candidate_id][0] == F(1, 2)
    validate_residency(rt)
    # A digest is a locator, not an equality proof. Inject an actual address
    # collision, even with the new injective pre-hash encoding in place.
    with patch.object(Program, 'program_id', property(lambda self: 'forced-collision-address')):
        rt, (first, second) = source_case(execution)
        before = rt.snapshot()
        result = rt.construct_candidate(second)
        after = validate_residency(rt)
        assert result.status == 'UNRESOLVED' and result.candidate_id is None
        assert 'collision' in result.reason
        assert after.candidates == before.candidates and after.programs == before.programs
        assert after.resources['spent']['compiler']['work'] > before.resources['spent']['compiler']['work']
        forecast = rt.predict_next('observation-0', encode_context((1, 0)))
        assert dict(forecast.predictions)[before.deployed_id][0] == F(2, 3)
    unicode_cfg = rt.contract
    searched, _ = search_fixture(cfg=unicode_cfg, bounds=SMALL)
    result = searched.start_reference_search('native')
    result = searched.advance_reference_search(result.search_id, transitions=1000)
    assert result.status == 'REFERENCE_CLASS_EXHAUSTED' and result.programs_compared == 35
    assert result.best_likelihood == F(4, 9)
    assert searched.reference_class_proof(result.proof_id, decision_class_id=result.decision_class_id).best_likelihood == F(4, 9)
    # The same finite class with forced ambiguous addresses cannot issue a
    # completeness proof merely because its syntax cursor has exhausted.
    with patch.object(Program, 'program_id', property(lambda self: 'forced-collision-address')):
        failed, _ = search_fixture(cfg=unicode_cfg, bounds=SMALL)
        result = failed.start_reference_search('native')
        result = failed.advance_reference_search(result.search_id, transitions=1000)
        assert result.status == 'UNRESOLVED' and result.programs_compared == 1 and result.unresolved_programs == 34 and result.proof_id is None
        assert failed.snapshot().searches[-1].cursor.done and len(failed.snapshot().searches[-1].rows) == 35
        assert not failed.snapshot().reference_proofs
    return {'source_commit': HISTORICAL, 'different_source_codepoint_lengths': [1, 2],
            'historical_different_programs_had_identical_ids_and_packed_bytes': True,
            'historical_deployed_probability_after_candidate_construction': str(wrong_probability),
            'required_and_current_deployed_probability': '2/3',
            'current_candidate_probability': '1/2',
            'forced_address_collision_is_unresolved_without_overwriting_owned_code': True,
            'complete_unicode_native_class_programs': 35, 'complete_class_best_likelihood': '4/9',
            'forced_collision_unresolved_class_members': 34,
            'address_collision_blocks_complete_class_authority': True}


@dataclass(frozen=True)
class Record:
    name: str
    values: tuple


class Choice(Enum):
    FIRST = 'first'


def encoding_audit():
    old_core, old_machine = old_serializers()
    # Independent old tree folds, with only the documented Unicode transport
    # and its key-sort encoding changed. No Runtime state is replaced.
    def utf_json(*args, **kwargs):
        kwargs['ensure_ascii'] = False
        return json.dumps(*args, **kwargs).replace('\x7f', '\\u007f')
    atoms = (None, False, True, -17, 0, 17, F(-1, 3), F(0), F(1, 3), '', 'A', '\\"\n')
    values = list(atoms)
    values.extend(tuple(row) for row in product(atoms[:6], repeat=3))
    values.extend((list(atoms), {-1: 'a', 'x': F(3, 7), (1, 'a'): [False, None]},
                   {'\U0001f600': 1, '\ud83d\ude00': 2, '\ud800': 3, '\ue000': 4},
                   Record('typed record', atoms), Record('\ud800', (1, F(3, 7))),
                   -(1 << 4095), F(1, 1 << 4095)))
    packed_cases = identity_cases = ascii_compatible = 0
    with patch.object(old_core, 'json', SimpleNamespace(dumps=utf_json)), patch.object(old_machine, 'json', SimpleNamespace(dumps=utf_json)):
        for value in values:
            expected = utf_json(old_machine._data(value), separators=(',', ':')).encode('utf-8', 'surrogatepass')
            assert packed_size(value) == len(expected)
            output = bytearray(len(expected))
            write_packed(value, output)
            assert bytes(output) == machine.pack(value) == expected
            packed_cases += 1
            expected_id = utf_json(old_core._canonical(value), separators=(',', ':')).encode('utf-8', 'surrogatepass')
            assert ''.join(fragments(value)).encode('utf-8', 'surrogatepass') == expected_id
            assert core.stable_hash(value) == hashlib.sha256(expected_id).hexdigest()
            identity_cases += 1
            if expected_id.isascii():
                assert old_core.stable_hash(value) == core.stable_hash(value)
                ascii_compatible += 1
        for value in (0.0, -0.0, 1.25, b'\x00\xff', Choice.FIRST):
            expected = utf_json(old_core._canonical(value), separators=(',', ':')).encode('utf-8', 'surrogatepass')
            assert core.stable_hash(value) == hashlib.sha256(expected).hexdigest()
            rejects(lambda: machine.pack(value))
            identity_cases += 1
    # Every single BMP code point, including all surrogates, plus complete
    # selected surrogate-pair/astral equivalence classes at boundary lows.
    bmp = pairs = 0
    for code in range(65536):
        value = chr(code)
        encoded = machine.pack(value)
        assert len(encoded) == packed_size(value)
        assert json.loads(encoded.decode('utf-8', 'surrogatepass')) == ['str', value]
        if code < 128:
            assert encoded == old_machine.pack(value)
            assert core.stable_hash(value) == old_core.stable_hash(value)
        bmp += 1
    for high, low in product(range(0xd800, 0xdc00), (0xdc00, 0xde00, 0xdfff)):
        units = chr(high)+chr(low)
        scalar = chr(0x10000+((high-0xd800) << 10)+(low-0xdc00))
        assert scalar != units and machine.pack(scalar) != machine.pack(units)
        assert json.loads(machine.pack(units).decode('utf-8', 'surrogatepass')) == ['str', units]
        pairs += 1
    for value in ('a'*255+'\U0001f600'+'\ud800'+'z'*257, '"\\\n'*257):
        assert json.loads(machine.pack(value).decode('utf-8', 'surrogatepass')) == ['str', value]
        assert len(machine.pack(value)) == packed_size(value)
    assert machine.pack(True) != machine.pack(1) != machine.pack(F(1))
    assert core.stable_hash(-0.0) != core.stable_hash(0.0)
    return {'independent_packed_tree_checks': packed_cases, 'independent_identity_checks': identity_cases,
            'unchanged_ASCII_identity_cases': ascii_compatible, 'all_single_BMP_codepoints': bmp,
            'surrogate_pair_vs_astral_boundary_classes': pairs,
            'typed_numeric_signed_zero_and_chunk_boundaries_preserved': True}


def planned_audit():
    rt = execution.ReferenceCompilerRuntime(contract(), zero_program(2))
    before = rt.snapshot()
    plan = rt._machine.realize('external-audit-plan', 'audit_only', tuple(range(10000)), rt.chi)
    assert type(plan) is machine.PlannedObject and not hasattr(plan, 'payload')
    assert rt.snapshot() == before  # passive size calculation gives no lease
    bad = replace(plan, spec=replace(plan.spec, residency={'reference_payload_bytes': 1, 'physical_objects': 1}))
    owner = before.candidates[0].physical_owner
    rejects(lambda: rt._allocate(owner, (bad,)))
    assert rt.snapshot() == before
    # Real low capacity must deny before any output-buffer writer runs.
    cfg = replace(contract(pattern=(0,)), limits=limits(byte_cap=8192))
    graph = Program((Source('x0_0'), Sum('mass', (Term(0, 0),)*1000)), 1, (1, 1))
    rt = execution.ReferenceCompilerRuntime(cfg, zero_program(2))
    before = rt.snapshot()
    with patch.object(execution, 'write_packed', side_effect=AssertionError('unfunded materialization ran')):
        result = rt.construct_candidate(graph)
    assert result.status == 'UNRESOLVED'
    after = validate_residency(rt)
    assert after.buffers == before.buffers and after.candidates == before.candidates
    # A failure after output allocation is a paid partial construction, not
    # an admissibility proof or a free rollback of the observed peak.
    rt = execution.ReferenceCompilerRuntime(contract(), zero_program(2))
    before = rt.snapshot()
    def partial(value, output):
        output[0] = 91
        raise ResourceExceeded('injected admitted encoder failure')
    with patch.object(execution, 'write_packed', side_effect=partial):
        result = rt.construct_candidate(zero_program(2))
    after = validate_residency(rt)
    assert result.status == 'UNRESOLVED' and after.candidates == before.candidates
    assert after.resources['peak']['reference_payload_bytes'] > before.resources['peak']['reference_payload_bytes']
    assert after.resources['spent']['compiler']['work'] > before.resources['spent']['compiler']['work']
    return {'plans_have_no_buffer_or_lease_authority': True, 'false_extent_rejected_before_mutation': True,
            'actual_capacity_refusal_precedes_output_materialization': True,
            'admitted_partial_encoding_failure_keeps_cost_and_peak_without_publishing_candidate': True}


def memory_case(rt_module, edges):
    cfg = contract(pattern=(0,))
    caps = dict(cfg.graph_limits)
    caps['edges'] = 100000
    cfg = replace(cfg, graph_limits=caps, limits=limits(byte_cap=8192, work_cap=10000000))
    cfg = rt_module.ConstructionContract(**{f.name: getattr(cfg, f.name) for f in fields(cfg)})
    graph = Program((Source('x0_0'), Sum('mass', (Term(0, 0),)*edges)), 1, (1, 1))
    rt = rt_module.ReferenceCompilerRuntime(cfg, zero_program(2))
    before = rt.snapshot()
    gc.collect()
    tracemalloc.start()
    try:
        result = rt.construct_candidate(graph)
        current, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    after = rt.snapshot()
    assert result.status == 'UNRESOLVED'
    assert after.resources['current'] == before.resources['current']
    assert after.resources['peak']['reference_payload_bytes'] < 8192
    return {'edges': edges, 'registered_payload_cap': 8192,
            'recorded_packed_peak': after.resources['peak']['reference_payload_bytes'],
            'new_traced_current': current, 'new_traced_peak': peak,
            'paid_construction_work': after.resources['spent']['compiler']['work']-before.resources['spent']['compiler']['work']}


def workspace_audit():
    old_core, _ = old_serializers()
    # Warm imported implementations before measuring only newly allocated
    # blocks inside construction. Producer graphs and bootstrap precede start.
    memory_case(execution, 1000)
    with patch.object(core, 'stable_hash', old_core.stable_hash), patch.object(programs, 'stable_hash', old_core.stable_hash):
        old = historical_modules(HISTORICAL, ('fp_reference.machine', 'fp_reference.runtime'))['fp_reference.runtime']
        memory_case(old, 1000)
        historical = [memory_case(old, n) for n in (1000, 10000, 100000)]
    current = [memory_case(execution, n) for n in (1000, 10000, 100000)]
    assert historical[-1]['new_traced_peak'] > 1000000
    assert current[-1]['new_traced_peak'] < historical[-1]['new_traced_peak']//20
    assert current[-1]['new_traced_peak'] < 2*current[0]['new_traced_peak']
    return {'source_commit': HISTORICAL, 'fixed_declared_edge_cap': 100000,
            'historical': historical, 'current': current,
            'scope': 'traced newly allocated Python blocks; excludes preexisting producer/import/bootstrap objects, untraced allocations and tracing metadata; not total host memory',
            'measurement_reference': 'https://docs.python.org/3.12/library/tracemalloc.html#tracemalloc.get_traced_memory'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--section', choices=('identity', 'encoding', 'planned', 'workspace'))
    args = parser.parse_args()
    sections = {'identity': identity_audit, 'encoding': encoding_audit, 'planned': planned_audit, 'workspace': workspace_audit}
    if args.section:
        print(json.dumps(sections[args.section](), indent=2))
        return
    result = {'status': 'PASS', 'scope': 'owned native identity and admitted streaming payload materialization',
              **{key: fn() for key, fn in sections.items()},
              'not_closed': ['all host metadata/arithmetic/allocator workspace', 'complete ERC-1 and Runtime release', 'actual target AMP and GPU science']}
    if args.write:
        (ROOT/'evidence/minimal/FP_OWNED_ENCODING_AUDIT.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
