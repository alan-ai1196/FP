"""Owned physical-object leases and immutable resource-role routing.

Costs entering this layer must come from the registered machine, not a public
candidate object list. This ledger is an accounting component, not an authority
for feasibility, construction, persistence or installation.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .core import ContractError, freeze_data, natural
from .program import name


class ResourceExceeded(ContractError):
    pass


def vector(values: Mapping[str, int], field: str) -> dict[str, int]:
    if not isinstance(values, Mapping):
        raise ContractError(f'{field} must be a typed integer resource vector')
    result = {}
    for key, value in values.items():
        name(key, 'resource dimension')
        result[key] = natural(value, f'{field}.{key}')
    return result


@dataclass(frozen=True)
class ResourceLimits:
    global_residency: Mapping[str, int]
    role_residency: Mapping[str, Mapping[str, int]]
    role_cumulative: Mapping[str, Mapping[str, int]]

    def __post_init__(self):
        global_caps = vector(self.global_residency, 'global residency')
        residency = {name(role, 'resource role'): vector(v, f'{role} residency') for role, v in self.role_residency.items()}
        cumulative = {name(role, 'resource role'): vector(v, f'{role} cumulative') for role, v in self.role_cumulative.items()}
        if not global_caps or not residency or set(residency) != set(cumulative):
            raise ContractError('complete global and matching role resource caps required')
        if any(set(v) != set(global_caps) for v in residency.values()):
            raise ContractError('each role must declare every residency dimension')
        object.__setattr__(self, 'global_residency', freeze_data(global_caps))
        object.__setattr__(self, 'role_residency', freeze_data(residency))
        object.__setattr__(self, 'role_cumulative', freeze_data(cumulative))


@dataclass(frozen=True)
class ObjectSpec:
    object_id: str
    kind: str
    residency: Mapping[str, int]
    provenance: str

    def __post_init__(self):
        name(self.object_id, 'physical object ID')
        name(self.kind, 'physical object kind')
        name(self.provenance, 'physical realization provenance')
        object.__setattr__(self, 'residency', freeze_data(vector(self.residency, 'object residency')))


@dataclass(frozen=True)
class ResourceEvent:
    sequence: int
    action: str
    owner: str
    object_ids: tuple[str, ...]
    debit: tuple[tuple[str, int], ...]
    note: str


class ResourceLedger:
    def __init__(self, limits: ResourceLimits):
        if type(limits) is not ResourceLimits:
            raise ContractError('immutable resource limits required')
        self._limits = limits
        self._owners: dict[str, str] = {}
        self._closed_owners: set[str] = set()
        self._objects: dict[str, ObjectSpec] = {}
        self._refs: dict[str, dict[str, int]] = {}
        self._retired: set[str] = set()
        self._spent = {role: {key: 0 for key in caps} for role, caps in limits.role_cumulative.items()}
        self._peak = {key: 0 for key in limits.global_residency}
        self._role_peak = {role: {key: 0 for key in caps} for role, caps in limits.role_residency.items()}
        self._events: list[ResourceEvent] = []

    @property
    def limits(self):
        return self._limits

    def _event(self, action, owner, objects=(), debit=(), note=''):
        self._events.append(ResourceEvent(len(self._events), action, owner, tuple(objects), tuple(debit), str(note)))

    def register_owner(self, owner: str, role: str):
        name(owner, 'resource owner')
        if owner in self._owners or role not in self._limits.role_residency:
            raise ContractError('owner already registered or undeclared resource role')
        self._owners[owner] = role
        self._event('register_owner', owner, note=role)

    def _owner(self, owner):
        if owner not in self._owners or owner in self._closed_owners:
            raise ContractError('unknown or closed physical resource owner')
        return self._owners[owner]

    def _residency(self, objects, refs):
        total = {key: 0 for key in self._limits.global_residency}
        roles = {role: dict.fromkeys(total, 0) for role in self._limits.role_residency}
        for key, spec in objects.items():
            if not refs[key] or any(n <= 0 for n in refs[key].values()):
                raise ContractError('physical object without a positive live lease')
            owner_roles = {self._owner(owner) for owner in refs[key]}
            for dimension, size in spec.residency.items():
                total[dimension] += size
                for role in owner_roles:
                    roles[role][dimension] += size
        return total, roles

    def _check_residency(self, objects, refs):
        total, roles = self._residency(objects, refs)
        for dimension, used in total.items():
            if used > self._limits.global_residency[dimension]:
                raise ResourceExceeded(f'global coexistence exceeds {dimension}')
        for role, values in roles.items():
            for dimension, used in values.items():
                if used > self._limits.role_residency[role][dimension]:
                    raise ResourceExceeded(f'{role} coexistence exceeds {dimension}')
        return total, roles

    def _record_peak(self, total, roles):
        for dimension, used in total.items():
            self._peak[dimension] = max(self._peak[dimension], used)
        for role, values in roles.items():
            for dimension, used in values.items():
                self._role_peak[role][dimension] = max(self._role_peak[role][dimension], used)

    def allocate(self, owner: str, objects: tuple[ObjectSpec, ...], *, note=''):
        """Check the actual coexistence set before an atomic allocation batch.

        There is deliberately no implicit release of the incumbent. Prior
        charged profiling/build work is never rolled back by a failed reserve.
        """
        self._owner(owner)
        proposed, refs = dict(self._objects), {key: dict(v) for key, v in self._refs.items()}
        ids = []
        for spec in objects:
            if type(spec) is not ObjectSpec or set(spec.residency) != set(self._limits.global_residency):
                raise ContractError('physical object has an incomplete resource shape')
            if spec.object_id in proposed or spec.object_id in self._retired:
                raise ContractError('physical object identity cannot be overwritten or recycled')
            proposed[spec.object_id] = spec
            refs[spec.object_id] = {owner: 1}
            ids.append(spec.object_id)
        total, roles = self._check_residency(proposed, refs)
        self._objects, self._refs = proposed, refs
        self._record_peak(total, roles)
        self._event('allocate', owner, ids, note=note)

    def acquire(self, owner: str, object_id: str, *, count: int = 1):
        self._owner(owner)
        natural(count, 'object reference count', positive=True)
        if object_id not in self._objects:
            raise ContractError('cannot share a nonexistent or freed physical object')
        refs = {key: dict(v) for key, v in self._refs.items()}
        refs[object_id][owner] = refs[object_id].get(owner, 0)+count
        total, roles = self._check_residency(self._objects, refs)
        self._refs = refs
        self._record_peak(total, roles)
        self._event('acquire', owner, (object_id,), (('references', count),))

    def release(self, owner: str, object_id: str, *, count: int = 1):
        self._owner(owner)
        natural(count, 'object reference count', positive=True)
        if object_id not in self._refs or self._refs[object_id].get(owner, 0) < count:
            raise ContractError('release exceeds this owner\'s actual references')
        remaining = self._refs[object_id][owner]-count
        if remaining:
            self._refs[object_id][owner] = remaining
        else:
            del self._refs[object_id][owner]
        if not self._refs[object_id]:
            del self._refs[object_id]
            del self._objects[object_id]
            self._retired.add(object_id)
        self._event('release', owner, (object_id,), (('references', count),))

    def release_owner(self, owner: str):
        self._owner(owner)
        for object_id, refs in tuple(self._refs.items()):
            if owner in refs:
                self.release(owner, object_id, count=refs[owner])
        # Retain the immutable owner/role assignment. A stale job cannot acquire
        # a recycled identity with a different accounting role.
        self._event('release_owner_objects', owner)

    def close_owner(self, owner: str):
        self.release_owner(owner)
        self._closed_owners.add(owner)
        self._event('close_owner', owner)

    def charge_work(self, role: str, debit: Mapping[str, int], *, note=''):
        if role not in self._spent:
            raise ContractError('undeclared work-accounting role')
        debit = vector(debit, 'work debit')
        if not set(debit) <= set(self._spent[role]):
            raise ContractError('unregistered cumulative resource dimension')
        after = dict(self._spent[role])
        for dimension, amount in debit.items():
            after[dimension] += amount
            if after[dimension] > self._limits.role_cumulative[role][dimension]:
                raise ResourceExceeded(f'{role} cumulative {dimension} exhausted')
        self._spent[role] = after
        self._event('work', role, debit=sorted(debit.items()), note=note)

    def snapshot(self):
        total, roles = self._residency(self._objects, self._refs)
        return freeze_data({'owners': self._owners,
                            'closed_owners': tuple(sorted(self._closed_owners)),
                            'objects': {key: {'kind': spec.kind, 'residency': spec.residency,
                                             'provenance': spec.provenance, 'references': self._refs[key]}
                                        for key, spec in self._objects.items()},
                            'retired_object_ids': tuple(sorted(self._retired)),
                            'current': total, 'peak': self._peak, 'role_current': roles,
                            'role_peak': self._role_peak, 'spent': self._spent,
                            'events': tuple((e.sequence, e.action, e.owner, e.object_ids, e.debit, e.note) for e in self._events)})


class CostRouter:
    def __init__(self, ledger: ResourceLedger, purpose_roles: Mapping[str, str]):
        self._ledger = ledger
        roles = {name(purpose, 'work purpose'): name(role, 'work role') for purpose, role in purpose_roles.items()}
        if any(role not in ledger.limits.role_cumulative for role in roles.values()):
            raise ContractError('work purpose maps to an undeclared role')
        self._roles = freeze_data(roles)

    def ledger_for(self, purpose: str):
        if purpose not in self._roles:
            raise ContractError('work purpose was not registered before execution')
        return _RoleWorkLedger(self._ledger, self._roles[purpose])

    def charge_work(self, purpose: str, debit: Mapping[str, int], note=''):
        self.ledger_for(purpose).charge_work(debit, note=note)

    def snapshot(self):
        return self._roles


@dataclass(frozen=True)
class _RoleWorkLedger:
    """A helper receives only its fixed work role, never a role-switching API."""
    _ledger: ResourceLedger
    _role: str

    def charge_work(self, debit, *, note=''):
        self._ledger.charge_work(self._role, debit, note=note)

    def snapshot(self):
        state = self._ledger.snapshot()
        return freeze_data({'role': self._role, 'spent': state['spent'][self._role]})
