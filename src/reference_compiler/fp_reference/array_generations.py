"""Object-bound allocation generations; no allocator or Runtime authority.

This table does not inspect addresses, shapes, dtype, initialization, owners
or resource limits. A physical storage owner must check all of those too.
Weak identity, rather than Tensor equality/hash, distinguishes issued views.
"""
import weakref

from .core import ContractError


class ArrayGenerations:
    def __init__(self):
        self._next = 0
        self._live = set()
        self._views = {}

    def _known(self, view):
        entry = self._views.get(id(view))
        return entry if entry is not None and entry[0]() is view else None

    def issue(self, view):
        """A fresh allocation must have a previously unissued view object."""
        if self._known(view) is not None:
            raise ContractError('an issued array view cannot acquire a new allocation generation')
        reference = weakref.ref(view)  # Validate weak identity before mutation.
        generation = self._next
        # Spend the name before any fallible dictionary/set growth. A failed
        # admission must never let a later issue reuse this generation.
        self._next += 1
        self._views[id(view)] = (reference, generation)
        self._live.add(generation)
        return generation

    def require(self, view):
        entry = self._known(view)
        if entry is None or entry[1] not in self._live:
            raise ContractError('array view has no live issued allocation generation')
        return entry[1]

    def derive(self, parent, view):
        """Only the owner, after checking containment, may admit this view."""
        generation = self.require(parent)
        entry = self._known(view)
        if entry is not None:
            if entry[1] != generation:
                raise ContractError('a derived view cannot rebind an earlier allocation generation')
            return generation
        self._views[id(view)] = (weakref.ref(view), generation)
        return generation

    def retire(self, generation):
        if type(generation) is not int or generation not in self._live:
            raise ContractError('only a live exact allocation generation can retire')
        self._live.remove(generation)

    def prune_dead_views(self):
        # Keep a retired binding while ANY client still holds its view. Such
        # an object must never be reissued/derived under a newer generation.
        self._views = {key: entry for key, entry in self._views.items() if entry[0]() is not None}
