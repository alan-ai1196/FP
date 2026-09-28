"""Private immutable historical array views, activated only by owned sealing.

Current masters, prepared operands, forecasts and carry blocks remain actual
device arrays. This representation only replaces the historical leaf/basis
field occurrences proved unnecessary by TOKEN_WORKSPACE_LIVENESS.md.
"""
from dataclasses import replace
import weakref

from .core import ContractError

VERSION = 'owned-sealed-token-workspace-images-v1'
LEAF_ARRAYS = ('values', 'normalizer', 'target_mass', 'embedding', 'core', 'common', 'corrections')
BASIS_ARRAYS = ('embedding', 'core', 'common', 'corrections')


class _ArchivedArray:
    __slots__ = ('_owner', '_value')

    def __init__(self, owner, value):
        self._owner, self._value = weakref.ref(owner), value


def archived(value):
    return type(value) is _ArchivedArray


def capture(value, arithmetic):
    from .token_cuda_state import ArrayWords
    if archived(value):
        return ArrayWords(*value._value[-1])
    return ArrayWords.capture(value, arithmetic)


def arrays(value):
    """All archival field occurrences, including predecessor references."""
    from .token_cuda_state import Resident, PredictionResident, ReadoutResident
    from .token_streaming import Pending
    if value is None:
        return ()
    if type(value) is PredictionResident:
        return arrays(value.predecessor)
    if type(value) is ReadoutResident:
        return arrays(value.prediction)
    if type(value) is not Resident:
        raise ContractError('workspace images require a complete known token resident')
    if type(value.state) is not Pending:
        return ()
    result = []
    for i, leaf in enumerate(value.state.leaves):
        for key in LEAF_ARRAYS:
            part = getattr(leaf, key)
            if archived(part):
                result.append((('leaf', i, key), part))
    for key in BASIS_ARRAYS:
        part = getattr(value.basis, key)
        if archived(part):
            result.append((('basis', key), part))
    return tuple(result)


def images(value, *, owner):
    # Snapshots and phase plans expose exact builtin values, never wrappers.
    return tuple((path, part._owner() is owner, part._value) for path, part in arrays(value))


def require(prefix, value):
    for path, part in arrays(value):
        if not prefix.contract.archive_workspaces or part._owner() is not prefix:
            raise ContractError('workspace image belongs to a different owner or registration')
        version, (identity, phase, original_path), geometry, words = part._value
        if (version != VERSION or path != original_path or phase not in prefix.arena._sealed
                or phase not in prefix.arena._accepted
                or prefix.arena._phases[phase][1] != identity):
            raise ContractError('workspace image has no matching sealed accepted source phase')
        generation, region, offset, size = geometry
        actual = prefix.arena._regions[region]
        if (prefix.arena._region_generations[region] != generation or offset < actual.offset
                or offset+size > actual.offset+actual.byte_size or len(words[2]) != size):
            raise ContractError('workspace image lost its complete original allocation geometry')


def _array(prefix, identity, phase, path, value, words):
    from .token_cuda_state import ArrayWords
    from .token_execution import closed
    closed(words, ArrayWords)
    words.array()  # Complete typed shape/dtype/extent guard, no numerical rewrite.
    image = (words.shape, words.dtype, words.data)
    if archived(value):
        if (value._owner() is not prefix or value._value[1][2] != path
                or value._value[-1] != image):
            raise ContractError('retained workspace image changed its source field or complete words')
        return value
    arena = prefix.arena
    arena.require_initialized(value)
    region = arena._region_for(value)
    generation = arena._generations.require(value)
    offset, size = value.storage_offset()*value.element_size(), value.numel()*value.element_size()
    if (tuple(value.shape) != words.shape or str(value.dtype).split('.')[-1] != words.dtype
            or size != len(words.data)):
        raise ContractError('archival words differ from their actual typed device view')
    body = (VERSION, (identity, phase, path), (generation, region, offset, size), image)
    return _ArchivedArray(prefix, body)


def prepare(prefix, identity, phase, resident, raw):
    """Propose a complete immutable representation before frame retention.

    No generation is retired here. The existing arena pins every unsealed
    allocation; accept requires the complete frame to have been sealed first.
    """
    from .token_cuda_state import Resident, StateWords
    from .token_streaming import Pending
    from .token_execution import closed
    closed(resident, Resident)
    closed(raw, StateWords)
    closed(resident.state, Pending)
    if len(resident.state.leaves) != len(raw.leaves):
        raise ContractError('workspace proposal lost complete event fields')
    leaves = tuple(replace(leaf, **{key: _array(prefix, identity, phase, ('leaf', i, key),
        getattr(leaf, key), getattr(raw.leaves[i], key)) for key in LEAF_ARRAYS})
        for i, leaf in enumerate(resident.state.leaves))
    basis_words = dict(zip(BASIS_ARRAYS, (raw.basis[1], raw.basis[2], raw.basis[3], raw.basis[5]), strict=True))
    basis = replace(resident.basis, **{key: _array(prefix, identity, phase, ('basis', key),
        getattr(resident.basis, key), basis_words[key]) for key in BASIS_ARRAYS})
    return replace(resident, state=replace(resident.state, leaves=leaves), basis=basis)


def validate(prefix, identity, phase, original, proposed, raw, prior_images):
    """Check a producer proposal against the actual operands and fresh words.

    This does not use the producer's geometry builder as an oracle. Old image
    bodies were saved before invoking the producer, including owner binding.
    """
    from .token_cuda_state import Resident
    from . import token_streaming as stream, token_amp as amp
    from .token_execution import closed
    closed(proposed, Resident)
    closed(proposed.state, stream.Pending)
    closed(proposed.basis, stream.Basis)
    if (proposed.prepared is not original.prepared or proposed.arithmetic is not original.arithmetic
            or any(getattr(proposed.state, key) is not getattr(original.state, key)
                   for key in ('origin', 'core', 'common', 'embedding', 'corrections'))
            or len(proposed.state.leaves) != len(original.state.leaves)):
        raise ContractError('workspace producer substituted live continuation operands')
    prior = {path: (bound, body) for path, bound, body in prior_images}

    def same(path, old, new, words):
        if not archived(new) or new._owner() is not prefix:
            raise ContractError('workspace producer supplied an unowned image')
        payload = (words.shape, words.dtype, words.data)
        if archived(old):
            if new is not old or prior[path] != (True, new._value) or new._value[-1] != payload:
                raise ContractError('workspace producer rewrote a prior complete image')
            return
        arena = prefix.arena
        arena.require_initialized(old)
        generation = arena._generations.require(old)
        region = arena._generation_regions[generation]
        geometry = (generation, region, old.storage_offset()*old.element_size(), old.numel()*old.element_size())
        expected = (VERSION, (identity, phase, path), geometry, payload)
        if new._value != expected:
            raise ContractError('workspace producer changed checked words, geometry or source identity')

    for i, (old, new, words) in enumerate(zip(original.state.leaves, proposed.state.leaves, raw.leaves, strict=True)):
        closed(new, amp.Pending)
        if any(getattr(new, key) is not getattr(old, key)
               for key in ('origin', 'windows', 'targets', 'embedding_ids', 'correction_ids')):
            raise ContractError('workspace producer changed complete leaf metadata')
        for key in LEAF_ARRAYS:
            same(('leaf', i, key), getattr(old, key), getattr(new, key), getattr(words, key))
    if any(getattr(proposed.basis, key) is not getattr(original.basis, key)
           for key in ('embedding_ids', 'correction_ids')):
        raise ContractError('workspace producer changed complete basis incidence')
    for key, words in zip(BASIS_ARRAYS, (raw.basis[1], raw.basis[2], raw.basis[3], raw.basis[5]), strict=True):
        same(('basis', key), getattr(original.basis, key), getattr(proposed.basis, key), words)


def work(prefix):
    # Complete image/view walks and independent frame binding stay prepaid.
    # Serialized payload is inside the existing admitted phase frame; actual
    # tuples/weak bindings/bytes are also covered by the enforced host cap.
    cfg = prefix.contract
    return 16*cfg.phase_evidence_bytes+1024*(7*cfg.initializer.output.update_unit+4)
