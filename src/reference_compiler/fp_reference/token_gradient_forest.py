"""Immutable binary64 gradient enclosures for a fixed-origin token unit.

Only the owned constructor/append induction establishes soundness. A caller
constructing a tuple or calling these passive helpers acquires no authority.
All persistent numeric data are bytes inside exact builtin tuples. No NumPy
array, dataclass wrapper, mutable container or historical forward cache is
retained. Original records and native commit remain with their Runtime owner.
"""
import numpy as np

from . import token_batch as ref
from .program import Sum
from .token_execution import closed, definition_check, TokenState
from .token_causal import TokenWindow
from .core import ContractError

VERSION = 'owned-token-native-gradient-forest-v1'


def origin_key(origin):
    """An exact immutable value image, not an identity hash or a live wrapper."""
    closed(origin, ref.Origin)
    d = origin.definition
    definition_check(d)
    nodes = tuple(('sum', n.type_id, tuple((t.parent, t.slot) for t in n.terms))
                  if type(n) is Sum else ('product', n.type_id, n.left, n.right) for n in d.nodes)
    spec = d.output
    # Fractions are copied to integer pairs, so no producer object is trusted.
    definition = ((d.sources.vocabulary, d.sources.context), d.width, nodes, d.slots,
                  d.features, (tuple((x.numerator, x.denominator) for x in spec.base),
                  spec.features, spec.grid_bits, (spec.learning_rate.numerator, spec.learning_rate.denominator),
                  spec.update_unit))
    origin.__post_init__()
    return (definition, origin.embedding, origin.core, origin.output, origin.cursor,
            origin.optimizer_steps, window_key(origin.source))


def window_key(window):
    closed(window, TokenWindow)
    window.__post_init__()
    return ((window.schema.vocabulary, window.schema.context), window.position, window.past)


def binding(state):
    closed(state, TokenState)
    if type(state.windows) is not tuple or type(state.targets) is not tuple:
        raise ContractError('immutable native source/target recipe required')
    if len(state.windows) != len(state.targets) or len(state.targets) > state.origin.definition.output.update_unit:
        raise ContractError('complete registered native prefix required')
    if any(type(t) is not int or not 0 <= t < state.origin.definition.output.labels for t in state.targets):
        raise ContractError('revealed native target outside the registered alphabet')
    return (origin_key(state.origin), tuple(window_key(w) for w in state.windows), state.targets)


def encode(value):
    if type(value) is not ref.ArrayInterval:
        raise ContractError('complete binary64 gradient interval required')
    return (value.lower.shape, value.lower.tobytes(order='C'), value.upper.tobytes(order='C'))


def decode(value, *, element_cap):
    if (type(value) is not tuple or len(value) != 3 or type(value[0]) is not tuple
            or any(type(n) is not int or n < 0 for n in value[0])
            or type(value[1]) is not bytes or type(value[2]) is not bytes):
        raise ContractError('immutable complete binary64 gradient image required')
    ref.size_check(value[0], element_cap)
    count = int(np.prod(value[0], dtype=object))
    if len(value[1]) != 8*count or len(value[2]) != 8*count:
        raise ContractError('gradient image extent differs from its complete shape')
    # frombuffer(bytes) cannot be made writable by setflags(write=True).
    return ref.ArrayInterval(*(np.frombuffer(b, dtype=np.float64).reshape(value[0]) for b in value[1:]))


def empty():
    return (0, (), (), (), ())


def append(forest, value, *, element_cap):
    """Carry only adjacent equal-sized perfect trees. Exact zeros stay exact."""
    blocks, size = list(forest), 1
    while blocks and blocks[-1][0] == size:
        previous = decode(blocks.pop()[1], element_cap=element_cap)
        if previous.lower.shape != value.lower.shape:
            raise ContractError('native gradient forest changed coordinate shape')
        value = previous+value
        size *= 2
    return tuple(blocks)+((size, encode(value)),)


def root(forest, count, shape, *, element_cap):
    expected = tuple(1 << bit for bit in range(count.bit_length()-1, -1, -1) if count >> bit & 1)
    if type(forest) is not tuple or tuple(b[0] for b in forest) != expected or not expected:
        raise ContractError('complete nonempty native carry forest required')
    values = tuple(decode(b[1], element_cap=element_cap) for b in forest)
    if any(v.lower.shape != shape for v in values):
        raise ContractError('native carry forest changed its registered coordinate shape')
    # The right fold is the ragged spine of the explicit balanced reducer.
    value = values[-1]
    for previous in reversed(values[:-1]):
        value = previous+value
    return value


def extend(cache, leaf, *, element_cap):
    """One internally computed event, under the same immutable bound origin."""
    if type(leaf) is not ref.Bounds or leaf.unit_count != 1:
        raise ContractError('one complete native event enclosure required')
    n, core, common, embeddings, corrections = cache
    if n >= leaf.unit.origin.definition.output.update_unit:
        raise ContractError('native gradient forest must reset at the registered commit')

    def update(entries, ids, values):
        result = dict(entries)
        for index, key in enumerate(ids):
            key = int(key)
            count, forest = result.get(key, (0, ()))
            result[key] = (count+1, append(forest, values[index], element_cap=element_cap))
        return tuple(sorted(result.items()))

    return (n+1, append(core, leaf.core, element_cap=element_cap),
            append(common, leaf.common, element_cap=element_cap),
            update(embeddings, leaf.embedding_ids, leaf.embedding),
            update(corrections, leaf.correction_ids, leaf.corrections))


def view(cache, unit, *, element_cap):
    """Disposable projection for the complete gradient/parameter predicate.

    The complete Unit remains the exact decoder for any historical query.
    This does not claim to provide a Bounds.mass or a grid-commit decision.
    """
    n, core, common, embeddings, corrections = cache
    d = unit.origin.definition
    if n != len(unit.targets) or n != len(unit.windows) or not 1 <= n <= d.output.update_unit:
        raise ContractError('native forest lost its complete source/target binding')

    def rows(entries, width, alphabet):
        ids = tuple(key for key, _ in entries)
        if not ids or ids != tuple(sorted(set(ids))) or any(type(k) is not int or not 0 <= k < alphabet for k in ids):
            raise ContractError('native forest lost its sparse coordinate keys')
        ref.size_check((len(ids), width), element_cap)
        values = []
        for _, (count, forest) in entries:
            if type(count) is not int or not 1 <= count <= n:
                raise ContractError('native sparse forest has an impossible event count')
            values.append(root(forest, count, (width,), element_cap=element_cap).reshape((1, width)))
        return np.frombuffer(np.asarray(ids, dtype=np.int64).tobytes(), dtype=np.int64), ref.join(tuple(values))

    ids, embedding = rows(embeddings, d.width, d.sources.vocabulary+1)
    targets, correction = rows(corrections, d.output.features, d.output.labels)
    return ref.GradientBounds(unit, ids, embedding,
        root(core, n, (d.slots,), element_cap=element_cap),
        root(common, n, (d.output.features,), element_cap=element_cap), targets, correction)


def work(definition):
    """Extra primitive tariff for images, sparse carry updates and projections.

    Existing phase work still pays native single-event arithmetic. This bound
    pays two bindings/projections per phase, including full immutable masters.
    It is not a bit-time, Python-heap or wall-time guarantee.
    """
    d, n = definition, definition.output.update_unit
    edges = sum(len(node.terms) if type(node) is Sum else 2 for node in d.nodes)
    coordinates = d.slots+d.output.features+n*(d.sources.context*d.width+d.output.features)
    return 4096*(d.slot_count+edges+n*d.sources.context+
                 coordinates*(n*d.sources.context+1).bit_length()+1)


def prepare(prefix, object_id, input_id, kind, reference):
    """Private owner transition; no caller-supplied cache or binding input.

    Admission/work payment precedes this call. A proposal remains complete
    on failure; only the existing sealed-phase acceptance can make its phase
    ID a current/staged root. Public phase wrappers are never the cache source.
    """
    key = binding(reference)
    cap = prefix.contract.initializer.element_cap
    if kind == 'initialize':
        if input_id is not None or reference.unit_count:
            raise ContractError('native forest birth requires the actual fresh committed origin')
        cache = empty()
    else:
        previous, cache = prefix._native_bounds[input_id]
        # Check the newly materialized exact image before sharing immutable
        # old subtrees. No live wrapper or caller-supplied digest is trusted.
        if key[0][0] == previous[0][0]:
            origin = (previous[0][0],)+key[0][1:]
            if origin == previous[0]:
                origin = previous[0]
            key = (origin, key[1], key[2])
        if kind in ('predict', 'readout'):
            if key != previous:
                raise ContractError('native forest lost its exact owned origin or retained records')
            key = previous
        elif kind == 'observe':
            if (key[0] != previous[0] or key[1][:-1] != previous[1] or key[2][:-1] != previous[2]
                    or len(key[2]) != len(previous[2])+1):
                raise ContractError('native forest append differs from the actual revealed successor')
            leaf = ref.Kernel(reference.origin.definition, element_cap=cap).prefix(
                reference.origin, (reference.windows[-1],), (reference.targets[-1],))
            cache = extend(cache, leaf, element_cap=cap)
            key = (previous[0], previous[1]+(key[1][-1],), previous[2]+(key[2][-1],))
        elif kind == 'commit':
            n = reference.origin.definition.output.update_unit
            if (reference.unit_count or cache[0] != n or key[0][0] != previous[0][0]
                    or reference.cursor != previous[0][4]+n
                    or reference.optimizer_steps != previous[0][5]+1):
                raise ContractError('native forest reset lost its complete registered commit')
            cache = empty()
        elif kind == 'attach':
            if (reference.unit_count or cache[0] or key[0][:4] != previous[0][:4]
                    or key[0][5:] != previous[0][5:]):
                raise ContractError('native forest attachment changed a committed learner')
            cache = empty()
        else:
            raise ContractError('unregistered native forest owner transition')
    entry = (key, cache)
    prefix._native_bounds[object_id] = entry
    return (reference.origin if not reference.unit_count else
            view(cache, ref.Unit(reference.origin, reference.windows, reference.targets), element_cap=cap))
