"""Exact ordered-version, augmentation and allocation-failure controls."""
from itertools import permutations
from pathlib import Path
from random import Random
from unittest.mock import patch
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src/reference_compiler'))
from fp_reference import owned_maps as maps


def weight(key, value):
    return (value, 1, value if key % 2 else 0, value if key % 3 else 0)


def validate(actual, expected):
    assert list(actual.items()) == list(expected.items())
    assert list(actual.values()) == list(expected.values())
    assert tuple(actual) == tuple(expected) and len(actual) == len(expected)
    for key, value in expected.items():
        assert actual[key] == value
    def tree(node, width):
        if node is None:
            return 0, 0, (0,)*width, ()
        lh, ln, lt, lk = tree(node.left, width)
        rh, rn, rt, rk = tree(node.right, width)
        assert abs(lh-rh) <= 1
        assert node.height == 1+max(lh, rh) and node.size == ln+rn+1
        assert node.total == tuple(lt[i]+node.weight[i]+rt[i] for i in range(width))
        assert all(k < node.key for k in lk) and all(k > node.key for k in rk)
        return node.height, node.size, node.total, lk+(node.key,)+rk
    h, n, total, _ = tree(actual._version.lookup, 4)
    _, m, _, _ = tree(actual._version.order, 0)
    assert n == m == len(expected) and 2**h <= (n+1)**2
    assert total == actual.total == tuple(sum(weight(k, v)[i] for k, v in expected.items()) for i in range(4))
    left = {node.key: node.value for node in maps._walk(actual._version.lookup)}
    for node in maps._walk(actual._version.order):
        assert node.value is left[node.value.key] and node.key == node.value.ordinal


def exhaustive():
    paths = states = 0
    for insertion in permutations(range(5)):
        initial, expected = maps.OwnedMap(width=4), {}
        for key in insertion:
            initial.set_weighted(key, key+1, weight(key, key+1))
            expected[key] = key+1
            validate(initial, expected)
            states += 1
        for deletion in permutations(range(5)):
            actual, wanted = initial.copy(), dict(expected)
            for key in deletion:
                del actual[key]
                del wanted[key]
                validate(actual, wanted)
                validate(initial, expected)
                states += 1
            paths += 1
    # Every ordered dictionary state over three keys/two values is reached;
    # every insertion, replacement and successful/failed deletion is checked.
    todo, seen, decisions = [(maps.OwnedMap(width=4), {})], set(), 0
    while todo:
        actual, wanted = todo.pop()
        identity = tuple(wanted.items())
        if identity in seen:
            continue
        seen.add(identity)
        for key in range(3):
            for value in (None, 0, 1):
                branch, reference = actual.copy(), dict(wanted)
                if value is None:
                    try:
                        del reference[key]
                    except KeyError:
                        before = branch._version
                        try:
                            del branch[key]
                        except KeyError:
                            pass
                        else:
                            raise AssertionError('missing deletion accepted')
                        assert branch._version is before
                    else:
                        del branch[key]
                else:
                    branch.set_weighted(key, value, weight(key, value))
                    reference[key] = value
                validate(branch, reference)
                validate(actual, wanted)
                todo.append((branch, reference))
                decisions += 1
    assert len(seen) == 79 and decisions == 711
    return dict(all_five_key_insertion_deletion_paths=paths,
        permutation_complete_state_checks=states, ordered_three_key_two_value_states=len(seen),
        exact_state_action_decisions=decisions, both_indices_weights_and_insertion_order_checked=True)


def versions_and_cost():
    rng, current, reference = Random(31907), maps.OwnedMap(width=4), {}
    saved, operations, maximum_nodes, total_nodes = [], 0, 0, 0
    original = maps._make
    for index in range(4096):
        if index % 64 == 0:
            saved.append((current.copy(), dict(reference)))
        key, value = rng.randrange(1024), rng.randrange(1 << 16)
        nodes = []
        def counted(*args):
            node = original(*args)
            nodes.append(node)
            return node
        h = max(maps._height(current._version.lookup), maps._height(current._version.order))
        with patch.object(maps, '_make', counted):
            if key in reference and index % 3 == 0:
                del current[key]
                del reference[key]
            else:
                current.set_weighted(key, value, weight(key, value))
                reference[key] = value
        # A conservative structural bound, not a wall-time benchmark.
        assert len(nodes) <= 32*(h+1)
        maximum_nodes = max(maximum_nodes, len(nodes))
        total_nodes += len(nodes)
        if index % 64 == 0:
            validate(current, reference)
        operations += 1
    validate(current, reference)
    for old, wanted in saved:
        validate(old, wanted)
    return dict(operations=operations, retained_versions=len(saved), final_entries=len(current),
        constructed_index_nodes=total_nodes, maximum_nodes_per_operation=maximum_nodes,
        exact_logarithmic_height_bound_and_node_work_bound_pass=True)


def failures():
    original = maps._make
    base, wanted = maps.OwnedMap(width=4), {}
    for key in range(31):
        base.set_weighted(key, key+1, weight(key, key+1))
        wanted[key] = key+1
    actions = (lambda x: x.set_weighted(40, 5, weight(40, 5)),
        lambda x: x.set_weighted(15, 7, weight(15, 7)),
        lambda x: x.__delitem__(15), lambda x: x.__delitem__(30))
    checked = 0
    for action in actions:
        made = []
        def counted(*args):
            made.append(None)
            return original(*args)
        with patch.object(maps, '_make', counted):
            action(base.copy())
        for stop in range(len(made)):
            branch, calls = base.copy(), []
            before = branch._version
            def fail(*args):
                if len(calls) == stop:
                    raise MemoryError('before an immutable index node exists')
                calls.append(None)
                return original(*args)
            with patch.object(maps, '_make', fail):
                try:
                    action(branch)
                except MemoryError:
                    pass
                else:
                    raise AssertionError('injected preparation failure was ignored')
            assert branch._version is before
            validate(branch, wanted)
            validate(base, wanted)
            checked += 1
        branch, before = base.copy(), base._version
        with patch.object(maps, '_Version', side_effect=MemoryError('before complete version exists')):
            try:
                action(branch)
            except MemoryError:
                pass
            else:
                raise AssertionError('failed complete version was published')
        assert branch._version is before
        checked += 1
    log, old_logs = maps.OwnedLog(), []
    for i in range(1024):
        old_logs.append(log)
        log = log.appended(i)
    assert tuple(log) == tuple(range(1024)) and log[-1] == 1023
    assert all(tuple(old) == tuple(range(i)) for i, old in enumerate(old_logs))
    return dict(atomic_node_and_version_failures=checked, all_predecessor_roots_unchanged=True,
        complete_immutable_log_versions=len(old_logs))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = dict(status='PASS_OWNED_MAPS_CPU', scope=__doc__.strip())
    for name, fn in (('exhaustive', exhaustive), ('versions_and_cost', versions_and_cost), ('failures', failures)):
        result[name] = fn()
        print('PASS '+name, flush=True)
    if args.write:
        (ROOT/'evidence/minimal/FP_OWNED_MAPS_CPU.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    if not __debug__:
        raise RuntimeError('assertions are required')
    main()
