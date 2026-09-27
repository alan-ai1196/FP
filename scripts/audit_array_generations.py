"""CPU counterexample to address-only reuse and exact issued-view controls.

The production CUDA arena remains append-only. Its spatial predicate is
called on CPU Tensor metadata here; no device or complete Runtime authority.
"""
from itertools import product
from pathlib import Path
import argparse
import gc
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src/reference_compiler'))
from fp_reference.array_generations import ArrayGenerations
from fp_reference.core import ContractError
from fp_reference.cuda_storage import CudaArena, CudaRegion


def refuses(operation):
    try:
        operation()
    except ContractError:
        return
    raise AssertionError('expected a closed generation refusal')


def cpu():
    import torch
    assert not torch.cuda.is_initialized()
    cases, refusals = [], 0
    for dtype in (torch.float16, torch.float32, torch.int64):
        backing = torch.empty(64, dtype=torch.uint8, device='cpu')
        old = backing[8:16].view(dtype)
        old.fill_(11)
        recorded = old.numpy().tobytes()
        leases = ArrayGenerations()
        first = leases.issue(old)
        alias = old.reshape(1, -1)
        assert leases.derive(old, alias) == first and leases.require(alias) == first
        leases.retire(first)
        current = backing[8:16].view(dtype)
        current.fill_(22)
        second = leases.issue(current)
        assert second > first and leases.require(current) == second

        # Invoke the real spatial predicate in the counterfactual state that
        # an unsound free-list addition would create. No CUDA constructor or
        # authority is called, and the current append-only arena forbids reuse.
        spatial = object.__new__(CudaArena)
        spatial.device = torch.device('cpu')
        spatial._pointer = backing.untyped_storage().data_ptr()
        spatial._starts = [8]
        spatial._regions = [CudaRegion(1, 1, 'next', 'new', 8, 8, 8, tuple(current.shape), str(dtype), True)]
        spatial.require_initialized(old)
        assert spatial._region_for(old) == spatial._region_for(current)
        assert old.numpy().tobytes() != recorded and torch.equal(old, current)
        for operation in (lambda: leases.require(old), lambda: leases.require(alias),
                lambda: leases.derive(old, old.reshape(-1)), lambda: leases.issue(old),
                lambda: leases.derive(current, old), lambda: leases.derive(current, alias),
                lambda: leases.retire(first), lambda: leases.retire(True)):
            refuses(operation)
            refusals += 1
        leases.prune_dead_views()
        refuses(lambda: leases.derive(current, old))
        assert leases.require(current) == second
        refusals += 1
        cases.append(dict(dtype=str(dtype), reused_offset=8, bytes=8,
                          stale_view_passes_spatial_guard=True, changed_words_visible=True,
                          stale_generation_refused=True))

    class View:
        pass
    histories = operations = 0
    # Independent finite oracle: issued identity -> generation and a live set.
    # Enumerate every length-five action word; invalid actions must not alter
    # which previously issued views retain admission.
    for actions in product(('issue', 'alias', 'retire', 'reissue', 'rebind'), repeat=5):
        table, views, assignment, live = ArrayGenerations(), [], [], set()
        for action in actions:
            before = tuple(i in live for i in assignment)
            if action == 'issue':
                value = View()
                generation = table.issue(value)
                assert generation == len({*assignment})
                views.append(value)
                assignment.append(generation)
                live.add(generation)
            elif views and action == 'alias':
                value = View()
                if assignment[-1] in live:
                    assert table.derive(views[-1], value) == assignment[-1]
                    views.append(value)
                    assignment.append(assignment[-1])
                else:
                    refuses(lambda: table.derive(views[-1], value))
            elif views and action == 'retire':
                if assignment[-1] in live:
                    table.retire(assignment[-1])
                    live.remove(assignment[-1])
                else:
                    refuses(lambda: table.retire(assignment[-1]))
            elif views and action == 'reissue':
                refuses(lambda: table.issue(views[0]))
                assert tuple(i in live for i in assignment) == before
            elif views and action == 'rebind':
                if assignment[-1] in live and assignment[0] == assignment[-1]:
                    assert table.derive(views[-1], views[0]) == assignment[0]
                else:
                    refuses(lambda: table.derive(views[-1], views[0]))
            for value, generation in zip(views, assignment, strict=True):
                if generation in live:
                    assert table.require(value) == generation
                else:
                    refuses(lambda: table.require(value))
            operations += 1
        histories += 1
    value = View()
    table = ArrayGenerations()
    generation = table.issue(value)
    del value
    gc.collect()
    table.prune_dead_views()
    assert not table._views and generation in table._live
    # Garbage collection of a view alone never frees its physical allocation.
    table.retire(generation)
    # Failed metadata growth must spend its generation, even if a partial
    # view binding already exists. Resource/phase rollback is the owner's job.
    failed_admissions = 0
    for after in (False, True):
        class FailingSet(set):
            def add(self, value):
                if after:
                    super().add(value)
                raise MemoryError('injected generation admission failure')
        table, failed = ArrayGenerations(), View()
        table._live = FailingSet()
        try:
            table.issue(failed)
        except MemoryError:
            pass
        else:
            raise AssertionError('expected metadata failure')
        table._live = set(table._live)
        following = View()
        assert table.issue(following) == 1
        refuses(lambda: table.derive(following, failed))
        failed_admissions += 1
    assert not torch.cuda.is_initialized()
    return dict(status='PASS_CPU_GENERATION_GUARD_CONTROL', spatial_counterexamples=cases,
        tensor_refusals=refusals, action_histories=histories, actions=operations,
        failed_admissions_keep_generations_distinct=failed_admissions,
        dead_view_does_not_retire_allocation=True, cuda_initialized=False,
        scope='CPU counterfactual spatial predicate and passive generation table; no reusable allocator or Runtime integration')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = cpu()
    if args.write:
        (ROOT/'evidence/minimal/FP_ARRAY_GENERATIONS_CPU.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
