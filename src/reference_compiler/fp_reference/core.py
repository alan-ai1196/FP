"""Strict value objects for the recovering reference execution kernel.

This is not an implementation-freeze contract. Registered Python implementations
are trusted code, not a sandbox; their IDs name fixed, deterministic semantics.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
import hashlib
import math
from types import MappingProxyType
from typing import Any


class ContractError(ValueError):
    pass


class BridgeError(ContractError):
    pass


class QueryError(ContractError):
    pass


class IdentityUnresolved(ContractError):
    """A physical content address cannot distinguish required native code."""
    pass


def require_finite(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float, Fraction)):
        raise ContractError(f'{name} must be a finite real number')
    try:
        result = float(value)
    except (OverflowError, ValueError) as exc:
        raise ContractError(f'{name} must be finite') from exc
    if not math.isfinite(result):
        raise ContractError(f'{name} must be finite')
    return result


def natural(value: Any, name: str, *, positive: bool = False) -> int:
    if type(value) is not int or value < int(positive):
        raise ContractError(f'{name} must be a {"positive" if positive else "nonnegative"} integer')
    return value


def stable_hash(value: Any) -> str:
    from .encoding import fragments
    digest = hashlib.sha256()
    for fragment in fragments(value):
        digest.update(fragment.encode('utf-8', 'surrogatepass'))
    return digest.hexdigest()


def freeze_data(value: Any) -> Any:
    """Detach and recursively freeze certificate/contract payload data."""
    if isinstance(value, Mapping):
        return MappingProxyType({freeze_data(k): freeze_data(v) for k, v in value.items()})
    if type(value) in (list, tuple):
        return tuple(freeze_data(x) for x in value)
    if value is None or type(value) in (bool, str, int, float, Fraction, bytes):
        if type(value) is float:
            require_finite(value, 'state coordinate')
        return value
    if isinstance(value, Enum):
        return value
    raise ContractError(f'unsupported immutable payload type: {type(value).__name__}')


class CertificateKind(Enum):
    UPPER_BOUND = 'upper_bound'
    SAFETY = 'safety'
    EQUIVALENCE = 'equivalence'
    COMPLETENESS = 'completeness'


@dataclass(frozen=True)
class ClaimContract:
    """Kernel registration scope, not yet the whole FP XVIII contract.

    `declaration` must describe the fixed implementations and assumptions. An ID
    is provenance; registration does not prove that arbitrary Python is sound.
    """
    declaration: Mapping[str, Any]
    proof_verifier_ids: tuple[str, ...] = ()
    bridge_relation_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, 'declaration', freeze_data(self.declaration))
        for name in ('proof_verifier_ids', 'bridge_relation_ids'):
            values = tuple(getattr(self, name))
            if len(set(values)) != len(values) or any(type(x) is not str or not x for x in values):
                raise ContractError(f'invalid {name}')
            object.__setattr__(self, name, values)

    @property
    def chi(self) -> str:
        return stable_hash(self)


@dataclass(frozen=True)
class CertificateProvenance:
    chi: str
    base_lineage_id: str
    snapshot_id: str
    decision_class_id: str = ''
    subject_id: str = ''

    def __post_init__(self) -> None:
        if any(type(x) is not str or not x for x in (self.chi, self.base_lineage_id, self.snapshot_id)):
            raise ContractError('incomplete certificate provenance')

    @property
    def key(self) -> str:
        return stable_hash(self)


@dataclass(frozen=True)
class Certificate:
    kind: CertificateKind
    provenance: CertificateProvenance
    payload: Mapping[str, Any]

    def __post_init__(self) -> None:
        if not isinstance(self.kind, CertificateKind):
            raise ContractError('unknown certificate kind')
        object.__setattr__(self, 'payload', freeze_data(self.payload))

    @property
    def certificate_id(self) -> str:
        return stable_hash(self)

    def assert_current(self, *, chi: str, base_lineage_id: str, snapshot_id: str) -> None:
        p = self.provenance
        if (p.chi, p.base_lineage_id, p.snapshot_id) != (chi, base_lineage_id, snapshot_id):
            raise ContractError('certificate is stale for the complete claim state')
