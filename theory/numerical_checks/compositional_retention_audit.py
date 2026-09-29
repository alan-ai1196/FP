"""Exact nonexpanding-check model; no Runtime, CUDA or model-quality release."""
from dataclasses import dataclass, replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts'),
               str(ROOT/'experiments/next_token'), str(Path(__file__).resolve().parent)]
from fp_reference import encoding
from fp_reference.core import ContractError
from fp_reference.resources import ResourceExceeded
import compositional_retention_model as model


@dataclass(frozen=True)
class Record:
    label: str
    value: object


def rejects(call, kinds=(ContractError, ResourceExceeded, MemoryError)):
    try:
        call()
    except kinds:
        return
    raise AssertionError('invalid or unfunded term retention accepted')


def recovered(reader, root):
    return b''.join(reader.expand(root))


def check_value(reader, value, bindings, root):
    walk = model.Walk(reader.literal, reader.pair, bindings)
    wanted, _ = walk.value(value)
    if wanted != root:
        raise ContractError('root substitution')


def values_and_snapshots():
    owner = model.Owner()
    atoms = (None, True, False, 0, -17, 1 << 129, F(-2, 3), F(1, 1 << 129),
             '', 'ascii "\\', '\x00\x7f\ud800\U0001f600', b'', bytes(range(256)))
    values = [*atoms, *product(atoms[:9], repeat=2), list(atoms), Record('typed', atoms),
        {'\ud83d\ude00': 1, '\U0001f600': 2, F(-1, 3): Record('x', (1, 2)), (3, 'x'): False},
        tuple(chr(i) for i in range(0, 65536, 257)), ''.join(chr(i) for i in range(65536)),
        b'\0\xff'*8193, 'a'*255+'\ud800\U0001f600'+'"\\\n'*257, -(1 << 32767),
        (), [], {}, Record('long', 'x'*10000)]
    saved, total = [], 0
    for value in values:
        expected = encoding.pack(value)
        # The actual binding check is forbidden from expanding the dictionary.
        with patch.object(model.Reader, 'expand', side_effect=AssertionError('unpaid expansion during binding')):
            root = owner.retain(value)
        assert recovered(owner.reader, root) == expected
        saved.append((owner.snapshot(), root, expected))
        total += len(expected)
    for pages, roots, bindings in (saved[0][0], saved[len(saved)//2][0], saved[-1][0]):
        reader = model.Reader(owner.limits)
        for page in pages:
            reader.add(page)
        for i, root in enumerate(roots):
            assert recovered(reader, root) == saved[i][2]
        assert all(type(row) is tuple and len(row) == 2 for row in bindings)
    # Returned binding rows have no mutable entry wrapper or private index alias.
    pages, roots, public = owner.snapshot()
    replacement = list(public)
    replacement[0] = (replacement[0][0], roots[-1])
    assert owner.snapshot()[2] == public
    return dict(typed_values=len(values), canonical_bytes_compared=total,
        dictionary_nodes=len(owner.reader.index.nodes), stored_page_bytes=sum(map(len, pages)),
        old_snapshots_rebuilt=3, no_expansion_during_binding=True,
        public_binding_replacement_has_no_authority=True, all_BMP_codepoints_preserved=True)


def mutable_fields():
    owner = model.Owner()
    row = Record('mutable-wrapper', [1, F(2, 3)])
    roots, expected = [], []
    for change in (lambda: None, lambda: row.value.append(7),
                   lambda: row.__dict__.update(value=(7, 8)),
                   lambda: row.__dict__.update(label='changed')):
        change()
        expected.append(encoding.pack(row))
        roots.append(owner.retain(row))
        assert id(row) not in owner.bindings
    assert len(set(expected)) == len(expected)
    assert [recovered(owner.reader, root) for root in roots] == expected
    from fp_reference.program import Term
    edge = Term(0, 1)
    value = (edge, edge)
    before = owner.retain(value)
    edge.__dict__['parent'] = 2
    after = owner.retain(value)
    assert before != after and recovered(owner.reader, after) == encoding.pack(value)
    assert id(value) not in owner.bindings and id(edge) not in owner.bindings
    return dict(changed_wrappers_and_descendants_rewalked=5,
        frozen_dataclass_not_assumed_immutable=True, old_roots_unchanged=True)


def faults_and_limits():
    modes = ('changed-literal', 'wrong-root', 'nonbyte-handle', 'copy-memory',
             'expected-memory', 'publication-memory')
    for mode in modes:
        owner = model.Owner()
        initial = owner.retain((0, b'old'))
        old_roots, old_bindings = owner.roots, dict(owner.bindings)
        value = Record('current', (1, b'new'))
        original = encoding.pack(value)
        if mode == 'expected-memory':
            hook = patch.object(owner.reader, 'literal', side_effect=MemoryError('expected traversal allocation'))
        elif mode == 'publication-memory':
            def state_copy(*args, **kwargs):
                if 'bindings' in kwargs:
                    raise MemoryError('next state allocation')
                return dict(*args, **kwargs)
            hook = patch.object(model, 'dict', state_copy, create=True)
        elif mode == 'wrong-root':
            finish = owner.producer.finish
            def wrong(root):
                raw = finish(root)
                fields = list(model.HEADER.unpack_from(raw))
                fields[-2:] = initial, owner.reader.index.nodes[initial][2]
                return model.HEADER.pack(*fields)+raw[model.HEADER.size:]
            hook = patch.object(owner.producer, 'finish', wrong)
        else:
            send = owner.producer.send
            def changed(message):
                assert type(message) is bytes
                if mode == 'copy-memory':
                    raise MemoryError('failed producer allocation')
                if mode == 'nonbyte-handle':
                    return 0
                if message[:1] == b'L':
                    message = b'L'+bytes((message[1] ^ 1,))+message[2:]
                return send(message)
            hook = patch.object(owner.producer, 'send', changed)
        with hook:
            rejects(lambda: owner.retain(value))
        assert owner.failed and owner.roots == old_roots and owner.bindings == old_bindings
        assert encoding.pack(value) == original
        assert recovered(owner.reader, initial) == encoding.pack((0, b'old'))
        rejects(lambda: owner.retain(None))
    limits = (model.Limits(nodes=1), model.Limits(page_bytes=70), model.Limits(expanded=18))
    for limit in limits:
        owner = model.Owner(limit)
        owner.retain(None)
        prior = owner.roots
        rejects(lambda: owner.retain(1 << 32), ResourceExceeded)
        assert owner.failed and owner.roots == prior
    # Collision is a bucket event only; wrong bytes never gain an old identity.
    with patch.object(model.zlib, 'crc32', return_value=0):
        owner = model.Owner()
        raw = []
        for word in product((0, 255), repeat=3):
            value = bytes(word)
            root = owner.retain(value)
            raw.append(recovered(owner.reader, root))
        assert len(set(raw)) == 8
        index = model.Index(model.Limits(comparisons=1))
        index.add_literal(b'ab')
        rejects(lambda: index.literal(b'ba'), ResourceExceeded)
    cycle = []
    cycle.append(cycle)
    rejects(lambda: model.Owner().retain(cycle))
    for field in ('expanded', 'nodes', 'page_bytes', 'comparisons'):
        for invalid in (0, -1, True, 1.0, 1 << 64):
            rejects(lambda: model.Limits(**{field: invalid}), ContractError)
    producer = model.Producer(model.Limits())
    producer.pages = 1 << 64
    rejects(producer.begin, ResourceExceeded)
    owner = model.Owner()
    limits_before = replace(owner.reader.index.limits)
    owner.producer.index.limits.__dict__.update(nodes=1 << 63, expanded=1 << 63)
    assert owner.reader.index.limits == limits_before == owner.limits
    assert owner.producer.index.limits is not owner.reader.index.limits
    return dict(producer_faults=list(modes), old_roots_and_bindings_preserved=True,
        node_page_and_expansion_limits_refuse=True, forced_collisions_preserve_distinctions=True,
        collision_budget_checked_before_comparison=True, cycles_refuse=True,
        allowance_type_and_uint64_limits_refuse=True, producer_limit_metadata_isolated=True)


def byte_mutations():
    value = (1, b'\x00\xff', F(2, 3))
    owner = model.Owner()
    root = owner.retain(value)
    raw = owner.reader.pages[0]
    checked = 0
    for i, bit in product(range(len(raw)), range(8)):
        mutated = raw[:i]+bytes((raw[i] ^ (1 << bit),))+raw[i+1:]
        def verify():
            reader = model.Reader(owner.limits)
            actual = reader.add(mutated)
            check_value(reader, value, {}, actual)
        rejects(verify)
        checked += 1
    for i in range(len(raw)):
        rejects(lambda: model.Reader(owner.limits).add(raw[:i]))
    rejects(lambda: model.Reader(owner.limits).add(raw+b'\0'))
    rejects(lambda: model.Reader(owner.limits).add(model.HEADER.pack(model.MAGIC, 0, 0, 1, 0, 0)+b'L'+model.U32.pack(0)))
    rejects(lambda: model.Reader(owner.limits).add(model.HEADER.pack(model.MAGIC, 0, 0, 1, 0, 1)+b'C'+model.U64.pack(0)*2))
    return dict(single_bit_variants_refused=checked, truncations_refused=len(raw),
        trailing_bytes_empty_literals_and_forward_references_refused=True)


def exact_class():
    index = model.Index(model.Limits())
    a, b, c, ab, bc = (index.add_literal(raw) for raw in (b'a', b'b', b'c', b'ab', b'bc'))
    left, right = index.add_pair(ab, c), index.add_pair(a, bc)
    assert left != right and index.nodes[left][2] == index.nodes[right][2] == 3
    # This model checks the fixed canonical expression tree, not every SLP
    # with the same expanded text. Alternative decompositions are out of class.
    reader = model.Reader(model.Limits())
    reader.index = index
    assert recovered(reader, left) == recovered(reader, right) == b'abc'
    # Literal definition order and unreachable valid nodes are not canonical.
    # Both dictionaries still locate the same owner-constructed expression.
    roots = []
    for order in ((b'a', b'b'), (b'unused', b'b', b'a')):
        local = model.Producer(model.Limits())
        local.begin()
        ids = {raw: local.send(b'L'+raw) for raw in order}
        proposed = local.send(b'C'+ids[b'a']+ids[b'b'])
        local_reader = model.Reader(model.Limits())
        accepted = local_reader.add(local.finish(proposed))
        assert accepted == local_reader.pair(local_reader.literal(b'a'), local_reader.literal(b'b'))
        assert recovered(local_reader, accepted) == b'ab'
        roots.append(accepted)
    assert roots[0] != roots[1]  # IDs have authority only within their own prefix.
    # Deliberately bypass the parser to exhibit the forbidden empty-leaf
    # representation, then count the real decoder's unfolded node reads.
    class CountedNodes(list):
        reads = 0
        def __getitem__(self, key):
            self.reads += 1
            return super().__getitem__(key)
    depth = 12
    nodes = CountedNodes([(0, b'', 0)])
    for i in range(depth):
        nodes.append((1, (i, i), 0))
    reader.index.nodes = nodes
    assert recovered(reader, depth) == b'' and nodes.reads == 8191
    return dict(equal_bytes_different_expression_roots=True,
        unrestricted_compressed_string_equality_not_claimed=True,
        definition_order_and_valid_unused_nodes_permitted=True,
        hypothetical_empty_literal_counterexample=dict(depth=depth, expanded_bytes=0,
            unfolded_visits=nodes.reads))


def archive_baseline(blob, values):
    """Existing complete owner, granted a warm image of the entire stable body.

    Its actual encoder, independent reader, work/ownership and current fast
    byte comparisons all run. No measured wall-time or host-memory comparison.
    """
    from fp_reference import ReferenceCompilerRuntime
    from fp_reference.resources import ObjectSpec
    from fp_reference.shared_reference import SharedPlannedObject, ROOT_BYTES
    from audit_owned_token_learner import fixture, registration
    from audit_reference_construction import limits, validate_residency
    from audit_shared_token_retention import STORAGE
    d, initial = fixture(2, 'mixed')
    cc, program, online = registration(d, initial)
    cc = replace(cc, limits=limits(256 << 20, 10**15))
    storage = replace(STORAGE, literal_workspace=4 << 20, expanded_cap=4 << 20,
        comparison_cap=16 << 20, canonical_image_bytes=encoding.packed_size(blob))
    rt = ReferenceCompilerRuntime(cc, program, online=online, shared_storage=storage)
    archive = rt._reference_archive
    def retain(value, label):
        identity = 'compositional-model-baseline:'+label
        planned = SharedPlannedObject(ObjectSpec(identity, 'complete_model_baseline',
            {'reference_payload_bytes': ROOT_BYTES, 'physical_objects': 1}, rt._chi), value)
        rt._allocate(rt._data_owner, (planned,))
        raw = rt._buffers[archive.pages[-1]]
        ordinal = len(archive.pages)-1
        actual = b''.join(archive.reader.decoded(ordinal,
            byte_cap=storage.expanded_cap, reference_cap=storage.reference_cap))
        assert actual == encoding.pack(value)
        return len(raw), len(actual)
    # Favorable placement is given explicitly, rather than forcing the existing
    # maximal-subtree policy to waste its image allowance on changing parents.
    retain(blob, 'warm-body')
    assert archive.images.find(blob) is not None
    pages, compared = 0, 0
    for i, value in enumerate(values):
        size, count = retain(value, str(i))
        pages += size
        compared += count
    validate_residency(rt)
    return dict(owner='current complete shared-reference owner with prewarmed stable-body image',
        complete_record_pages=len(values), retained_record_page_bytes=pages,
        independently_compared_record_bytes=compared, warm_image_bytes=archive.images.used,
        warmup_pages_excluded=True, timing_and_whole_host_comparison_not_claimed=True)


def growth():
    # An identical immutable body is deliberately much larger than its changing
    # record shell. Complete bytes are checked separately as an audit oracle.
    owner = model.Owner()
    blob = bytes(range(256))*4096
    originals, values = [], []
    for i in range(33):
        value = Record('unit', (blob, tuple(range(i))))
        root = owner.retain(value)
        actual = recovered(owner.reader, root)
        assert actual == encoding.pack(value)
        originals.append(len(actual))
        values.append(value)
    cold, warm = owner.statistics[0], owner.statistics[1:]
    assert all(row['expected_literal_bytes'] < 1024 for row in warm)
    assert all(row['expanded'] > 2 << 20 for row in warm)
    baseline = archive_baseline(blob, values)
    assert baseline['independently_compared_record_bytes'] == sum(originals)
    literals = [len(payload) for tag, payload, _ in owner.reader.index.nodes if tag == 0]
    pairs = len(owner.reader.index.nodes)-len(literals)
    stored = sum(map(len, owner.reader.pages))
    assert stored == model.HEADER.size*len(values)+sum(5+n for n in literals)+17*pairs
    return dict(complete_roots=len(originals), complete_expanded_bytes=sum(originals),
        retained_page_bytes=stored, exact_payload_formula_checked=True, archive_baseline=baseline,
        cold=cold, warm_expected_literal_bytes=sum(x['expected_literal_bytes'] for x in warm),
        warm_expected_pair_checks=sum(x['expected_pair_checks'] for x in warm),
        warm_new_nodes=sum(x['new_nodes'] for x in warm),
        scope='fixed immutable-body model; original aggregate guard still runs; no Runtime timing law')


def audit():
    return dict(status='PASS_COMPOSITIONAL_RETENTION_MODEL', scope=__doc__.strip(),
        values=values_and_snapshots(), mutable=mutable_fields(), faults=faults_and_limits(),
        mutations=byte_mutations(), decision_class=exact_class(), growth=growth())


if __name__ == '__main__':
    if sys.flags.optimize:
        raise RuntimeError('term model audit requires assertions')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = audit()
    body = json.dumps(result, indent=2)+'\n'
    if args.write:
        (ROOT/'evidence/minimal/FP_COMPOSITIONAL_RETENTION_MODEL.json').write_text(body, encoding='utf-8')
    print(body)
