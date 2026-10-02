"""Detached value graphs at the Runtime's caller boundary.

A frozen dataclass can still have writable metadata. No returned or supplied
wrapper is therefore an ownership boundary. Copy wrappers and containers with
one memo, preserving complete metadata and internal sharing. Only the existing
closed immutable scalar/tuple algebra may retain identity across the boundary.
This is not serialization, an identity certificate, or arbitrary Python sandboxing.
"""
from dataclasses import is_dataclass
from enum import Enum
from fractions import Fraction
from types import MappingProxyType, MemberDescriptorType

from .core import ContractError
from .token_values import CapturedTokenValues


def detached(value):
    """Copy a finite FP value graph without caller hooks or constructors.

    Unknown objects and cycles refuse; no coordinate is silently discarded.
    Frozen wrappers with dictionaries copy every actual metadata entry, even
    extra entries, so subsequent semantic validation still sees the full value.
    Registered records also copy every actual slot, including inherited slots.
    Immutable leaves use the scalar fault model of the canonical encoder/image
    owner; mutation of trusted classes/code is outside that model.
    """
    # This existing paid fact is bound to the actual immutable source tuple,
    # never an equal value or a caller hint. All its children are exact scalar
    # leaves, so the ordinary traversal below would return the same identity.
    from .token_base_facts import positive_base_known
    memo, active = {}, set()

    def visit(item):
        kind = type(item)
        if item is None or kind in (bool, int, float, str, bytes, Fraction):
            return item
        if isinstance(item, Enum):
            return item
        identity = id(item)
        if identity in active:
            raise ContractError('cyclic public value has no finite detached representation')
        if identity in memo:
            return memo[identity]
        active.add(identity)
        try:
            if kind is tuple and positive_base_known(item):
                result = item
            elif kind is CapturedTokenValues:
                # Export the same complete builtin tuple as the literal
                # realization, preserving repeated bindings with this memo.
                result = tuple(visit(child) for child in item)
            elif kind in (tuple, list):
                children = tuple(visit(child) for child in item)
                result = (item if all(a is b for a, b in zip(item, children)) else children) if kind is tuple else list(children)
            elif kind in (dict, MappingProxyType):
                entries = {visit(key): visit(child) for key, child in item.items()}
                result = MappingProxyType(entries) if kind is MappingProxyType else entries
            elif is_dataclass(item) and not isinstance(item, type) and kind.__module__.startswith('fp_reference.'):
                result = object.__new__(kind)
                if hasattr(item, '__dict__'):
                    # Copy actual entries as data: an extra entry named like a
                    # descriptor must not invoke that descriptor on the copy.
                    vars(result).update({visit(key): visit(child) for key, child in vars(item).items()})
                for base in kind.__mro__:
                    for descriptor in vars(base).values():
                        if type(descriptor) is MemberDescriptorType:
                            try:
                                child = descriptor.__get__(item, kind)
                            except AttributeError:
                                continue  # Preserve an absent slot as absent.
                            descriptor.__set__(result, visit(child))
            else:
                raise ContractError('unsupported public value type: '+kind.__module__+'.'+kind.__qualname__)
            memo[identity] = result
            return result
        finally:
            active.remove(identity)

    return visit(value)
