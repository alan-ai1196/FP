"""Numerical continuation control for token workspace liveness.

Old leaf arrays/incidences and the previously materialized basis become inaccessible
sentinels after each observation. Complete immutable word images remain for
diagnostic reconstruction; masters, prepared operands and carry roots stay
live. This is a passive CPU dataflow audit, not a Runtime retirement lowering,
resource certificate, CUDA execution or corpus experiment.
"""
from dataclasses import replace
from collections import Counter
from itertools import product
from pathlib import Path
import argparse
import json
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'src/reference_compiler')]

from audit_native_tokens import fixture
from audit_owned_token_learner import registration
from audit_token_amp_schedule import ExactPrimitives
from audit_token_cuda_owner import cuda_contract
from fp_reference.token_arrays import CPUArrays
from fp_reference.token_array_check import CheckedPrimitives
from fp_reference.token_array_events import Kernel
from fp_reference.token_cuda_prefix import transition, fresh_origin
from fp_reference.token_cuda_state import ArrayWords, LeafWords
from fp_reference.token_causal import TokenWindow
from fp_reference import token_amp as amp, token_streaming as stream

FIELDS = ('values', 'normalizer', 'target_mass', 'embedding_ids', 'embedding',
          'core', 'common', 'correction_ids', 'corrections')
CELLS = 4096


class Inaccessible:
    accesses = 0

    def __getattribute__(self, name):
        type(self).accesses += 1
        raise AssertionError('continuation read archived numerical workspace: '+name)

    def __array__(self, *args, **kwargs):
        type(self).accesses += 1
        raise AssertionError('continuation converted archived numerical workspace')


INACCESSIBLE = Inaccessible()


def image(array, arithmetic):
    words = ArrayWords.capture(array, arithmetic)
    return words.shape, words.dtype, words.data


def immutable(value):
    if type(value) is tuple:
        return all(map(immutable, value))
    return type(value) in (int, str, bytes)


def leaf_image(leaf, arithmetic):
    w = leaf.windows[0]
    result = ((w.schema.vocabulary, w.schema.context, w.position, w.past), leaf.targets[0],
        tuple(tuple(map(int, getattr(leaf, k))) if k.endswith('_ids')
              else image(getattr(leaf, k), arithmetic) for k in FIELDS))
    assert immutable(result)
    return result


def leaf_decode(value, origin):
    window, target, fields = value
    vocabulary, context, position, past = window
    assert (vocabulary, context) == (origin.definition.sources.vocabulary, origin.definition.sources.context)
    w = TokenWindow(origin.definition.sources, position, past)
    return LeafWords(w, target, *(part if name.endswith('_ids') else ArrayWords(*part)
        for name, part in zip(FIELDS, fields, strict=True))).cpu(origin)


def basis_image(basis, arithmetic):
    result = (tuple(map(int, basis.embedding_ids)),
        *(image(getattr(basis, k), arithmetic) for k in ('embedding', 'core', 'common')),
        tuple(map(int, basis.correction_ids)), image(basis.corrections, arithmetic))
    assert immutable(result)
    return result


def basis_decode(value):
    ids, embedding, core, common, targets, corrections = value
    return stream.Basis(np.asarray(ids, dtype=np.int64),
        *(ArrayWords(*part).array() for part in (embedding, core, common)),
        np.asarray(targets, dtype=np.int64), ArrayWords(*corrections).array())


def forest_words(pending):
    forests = (pending.core, pending.common, *(f for _, f in pending.embedding),
               *(f for _, f in pending.corrections))
    actual = sum(block.value.size for forest in forests for block in forest.blocks)
    d, t = pending.origin.definition, pending.unit_count
    events_by_token = Counter(token for leaf in pending.leaves for token in set(leaf.windows[0].past))
    events_by_target = Counter(leaf.targets[0] for leaf in pending.leaves)
    assert pending.core.count == pending.common.count == t
    assert {key: f.count for key, f in pending.embedding} == events_by_token
    assert {key: f.count for key, f in pending.corrections} == events_by_target
    assert all(block.value.dtype == np.float32 for forest in forests for block in forest.blocks)
    expected = ((d.slots+d.output.features)*t.bit_count()
        +d.width*sum(n.bit_count() for n in events_by_token.values())
        +d.output.features*sum(n.bit_count() for n in events_by_target.values()))
    assert actual == expected
    return actual


def run(unit, kind, word, *, profile=False):
    definition, root = fixture(unit, kind)
    cc, program, online = registration(definition, root)
    cfg, oracle = cuda_contract(cc.initializer_pattern), ExactPrimitives()
    result = dict(events=0, commits=0, phases=0, compared_output_arrays=0,
                  compared_output_words=0, reconstructed_states=0,
                  forest_coordinate_checks=0, leaf_alias_witnesses=0)

    def phase(kind, before=None, forecast=None, window=None, target=None):
        checker = CheckedPrimitives(cfg.exact_cell_cap)
        def audit(*args):
            checker(*args)
            oracle(*args)
        arithmetic = CPUArrays(element_cap=cfg.initializer.element_cap, cell_cap=CELLS, audit=audit)
        birth = fresh_origin(program, cfg, 0, online.learner, cc.semantics, 32768) if kind == 'initialize' else None
        cursor = 0 if before is None else before.state.cursor
        value = transition(kind, program, cfg, before, forecast, window, target, cursor, birth, arithmetic)
        arithmetic.check()
        outputs = tuple((tag, image(array, arithmetic)) for tag, array in arithmetic.records)
        return value, outputs, arithmetic

    def paired(kind, left=None, right=None, forecasts=(None, None), window=None, target=None):
        l, lo, la = phase(kind, left, forecasts[0], window, target)
        r, ro, ra = phase(kind, right, forecasts[1], window, target)
        assert lo == ro and (la.cells, la.bytes) == (ra.cells, ra.bytes)
        result['phases'] += 1
        result['compared_output_arrays'] += len(lo)
        result['compared_output_words'] += sum(int(np.prod(shape)) for _, (shape, _, _) in lo)
        return l, r, ra

    left, right, arithmetic = paired('initialize')
    assert left.raw() == right.raw()
    archives, archived_basis = (), None
    original_windows = tuple(definition.sources.window(word, i) for i in range(len(word)))
    order = ((3, 0)*(len(word)//2) if profile == 'repeat' else
             tuple(reversed(range(len(word)))) if profile else tuple(range(len(word))))
    # A profile retains the original complete window/target, independent of
    # its replay cursor, including repeated references to original records.
    for j in order:
        target = word[j]
        window = original_windows[j] if profile else left.state.source
        lp, rp, _ = paired('predict', left, right, window=window)
        assert lp.raw() == rp.raw()
        # Passive per-label recipe exercises its numerical inputs. This call
        # does not grant a pending Runtime reporting or target-ingress port.
        for y in range(definition.output.labels):
            outputs = []
            for owner, forecast in ((left, lp), (right, rp)):
                a = CPUArrays(element_cap=cfg.initializer.element_cap, cell_cap=CELLS,
                              audit=CheckedPrimitives(cfg.exact_cell_cap))
                mass, division = Kernel(definition, element_cap=cfg.initializer.element_cap).readout_label(
                    owner.prepared, forecast.forecast, y, a)
                outputs.append((image(mass, a), image(division, a)))
            assert outputs[0] == outputs[1]
        left, right, arithmetic = paired('observe', left, right, (lp, rp), window, target)
        p = right.state
        assert p.unit_count == len(archives)+1
        archives += (leaf_image(p.leaves[-1], arithmetic),)
        archived_basis = basis_image(right.basis, arithmetic)
        assert forest_words(p) == forest_words(left.state)
        result['forest_coordinate_checks'] += 1
        for key in ('core', 'common'):
            if any(np.shares_memory(getattr(p.leaves[-1], key), b.value) for b in getattr(p, key).blocks):
                result['leaf_alias_witnesses'] += 1
        # Leaf array/incidence slots lose access. The arrays also referenced by
        # live carry blocks stay available through those blocks.
        right = replace(right, state=replace(p, leaves=tuple(replace(leaf,
            **{name: INACCESSIBLE for name in FIELDS}) for leaf in p.leaves)), basis=INACCESSIBLE)
        # Every original diagnostic word remains recoverable from immutable
        # images plus actual live roots, without touching any sentinel.
        hydrated = replace(right, state=replace(right.state,
            leaves=tuple(leaf_decode(item, right.origin) for item in archives)),
            basis=basis_decode(archived_basis))
        assert hydrated.raw(arithmetic) == left.raw()
        result['reconstructed_states'] += 1
        result['events'] += 1
        if right.state.unit_count == unit:
            left, right, arithmetic = paired('commit', left, right)
            assert left.raw() == right.raw()
            archives, archived_basis = (), None
            result['commits'] += 1
    assert not archives  # All cases finish complete units, including profiles.
    result['exactly_checked_primitive_words'] = oracle.words
    return result


def alias_counterexample():
    a = amp.Arithmetic()
    leaf = np.asarray([1], dtype=np.float32)
    forest = stream.Forest().append(leaf, a)
    assert np.shares_memory(leaf, forest.blocks[0].value)
    archive = leaf.tobytes()
    expected = forest.append(np.asarray([2], dtype=np.float32), a).root(a).copy()
    leaf.fill(0)  # Simulates reusing storage while a carry-root alias is live.
    changed = forest.append(np.asarray([2], dtype=np.float32), a).root(a)
    assert expected[0] == 3 and changed[0] == 2 and np.frombuffer(archive, np.float32)[0] == 1
    return dict(archived_leaf_unchanged=True, root_alias_was_live=True,
                expected_next_root=3, next_root_after_unsafe_reuse=2)


def audit():
    totals = {}
    histories = profiles = 0
    cases = [(unit, kind, word, False) for unit, kind, word in
        product((1, 2, 4), ('mixed', 'zero-embedding', 'zero-core'), product((0, 1), repeat=4))]
    cases += [(8, kind, word, False) for kind in ('mixed', 'zero-embedding', 'zero-core')
              for word in ((0,)*8, (0, 1, 1, 0)*2)]
    cases += [(4, 'mixed', (0, 1, 1, 0)*2, 'reverse'), (2, 'zero-core', (0, 1, 1, 0)*2, 'repeat')]
    for unit, kind, word, profile in cases:
        row = run(unit, kind, word, profile=profile)
        for key, value in row.items():
            totals[key] = totals.get(key, 0)+value
        histories += 1
        profiles += int(bool(profile))
    assert Inaccessible.accesses == 0 and 'torch' not in sys.modules
    return dict(status='PASS_NUMERICAL_TOKEN_WORKSPACE_LIVENESS_CPU', histories=histories,
        profile_histories=profiles, **totals, old_workspace_accesses=Inaccessible.accesses,
        alias_counterexample=alias_counterexample(), scope=__doc__.strip())


if __name__ == '__main__':
    if sys.flags.optimize:
        raise RuntimeError('workspace-liveness audit requires assertions')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = audit()
    body = json.dumps(result, indent=2)+'\n'
    if args.write:
        (ROOT/'evidence/minimal/FP_TOKEN_WORKSPACE_LIVENESS_CPU.json').write_text(body, encoding='utf-8')
    print(body)
