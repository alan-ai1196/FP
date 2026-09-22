"""Exact packed order DP against complete independent tape enumeration."""
from dataclasses import asdict
from itertools import combinations
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'experiments/joint_uncertainty')]
from fp_reference import query_order as packed
from fp_reference.core import ContractError
from fp_reference.resources import ResourceExceeded
from fp_reference.semantics import ArithmeticUnresolved
import query_order_resource_frontier as oracle

TAIL = b'untouched outer extent'
buffers = {}


def adapter(n, support, query, join_cap=4096, live_cap=32768, objective='outputs'):
    try:
        size = packed.workspace_bytes(n, query)
    except ArithmeticUnresolved as exc:
        # The existing exhaustive enumerator expects its passive guard type.
        # The production kernel still exposes ArithmeticUnresolved.
        raise ValueError(str(exc)) from exc
    buffer = buffers.setdefault(size, bytearray(b'\xa5'*size+TAIL))
    result = packed.search(n, support, query, join_cap, live_cap, buffer, objective=objective)
    assert bytes(buffer[size:]) == TAIL
    return None if result is None else {'order': result.order,
        'partition_only_output_cells': result.output_cells, 'partition_only_tape_nodes': result.tape_nodes,
        'subset_states': result.subset_states, 'transitions': result.transitions}


def guards():
    rows = []
    good = (4, ((0, 1), (1, 2)), (0, 3), 4096, 32768)
    attacks = (
        ('vertex-class', (17, (), (0, 0), 4096, 32768), None),
        ('bool-query', (4, (), (False, 3), 4096, 32768), None),
        ('bool-edge', (4, ((False, 1),), (0, 3), 4096, 32768), None),
        ('noncanonical-edge', (4, ((1, 0),), (0, 3), 4096, 32768), None),
        ('duplicate-edge', (4, ((0, 1), (0, 1)), (0, 3), 4096, 32768), None),
        ('bad-cap', (4, (), (0, 3), True, 32768), None),
        ('bad-objective', good, 'precision'),
        ('short-buffer', good, None),
        ('immutable-buffer', good, None),
    )
    for name, args, objective in attacks:
        size = packed.workspace_bytes(4, (0, 3))
        buffer = bytearray(b'\xa5'*(size-1 if name == 'short-buffer' else size))
        if name == 'immutable-buffer':
            buffer = bytes(buffer)
        before = bytes(buffer)
        try:
            packed.search(*args, buffer, objective=objective or 'outputs')
        except (ContractError, ResourceExceeded, ArithmeticUnresolved):
            pass
        else:
            raise AssertionError('invalid search input was accepted: '+name)
        assert bytes(buffer) == before
        rows.append(name)
    return {'refused_before_any_scratch_write': rows, 'resource_refusal_is_not_empty_class': True}


def large():
    n = 16
    rows = []
    for name, support, query, join, live in (
        ('all-subsets-empty-support', (), (0, 0), 4096, 32768),
        ('chain', tuple((v, v+1) for v in range(n-1)), (0, 15), 4096, 32768),
        ('dense-refusal', tuple(combinations(range(n), 2)), (0, 15), 4096, 32768),
        ('dense-wide', tuple(combinations(range(n), 2)), (0, 15), 32768, 1 << 24),
    ):
        size = packed.workspace_bytes(n, query)
        buffer = bytearray(b'\xa5'*size+TAIL)
        result = packed.search(n, support, query, join, live, buffer)
        expected = oracle.subset_costs(n, support, query, join, live)
        assert bytes(buffer[size:]) == TAIL
        assert (None if result is None else (result.order, result.output_cells, result.tape_nodes,
            result.subset_states, result.transitions)) == (None if expected is None else (
                expected['order'], expected['partition_only_output_cells'], expected['partition_only_tape_nodes'],
                expected['subset_states'], expected['transitions']))
        rows.append({'case': name, 'scratch_bytes': size, 'prepaid_work_tariff': packed.search_work(n, len(support), query),
                     'minimum': None if result is None else asdict(result)})
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    with patch.object(oracle, 'subset_costs', adapter):
        complete = oracle.small_audit()
    report = {'status': 'PASS_PACKED_QUERY_ORDER_STORAGE',
        'scope': 'passive exact structural search with actual packed DP bytes; no Runtime debit, precision, GPU or installation authority',
        'complete_independent_tape_enumeration': complete,
        'guard_cases': guards(), 'maximum_class_cases': large(),
        'row_bytes': 12, 'maximum_free_vertices': 15, 'maximum_scratch_bytes': 393216,
        'work_model': packed.WORK_MODEL, 'outside_extent_and_reused_buffer_checks': 'PASS'}
    if args.write:
        (ROOT/'evidence/minimal/FP_QUERY_ORDER_STORAGE.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
