"""Owned physical-object leases and immutable resource-role routing.

Costs entering this layer must come from the registered machine, not a public
candidate object list. This ledger is an accounting component, not an authority
for feasibility, construction, persistence or installation.
"""
from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Mapping

from .core import ContractError, freeze_data, natural
from .owned_maps import OwnedMap, OwnedLog
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


@dataclass(frozen=True, slots=True)
class _Lease:
    spec: ObjectSpec
    refs: Mapping[str, int]


class _LeaseView(Mapping):
    """Read-only field projection of one complete owned lease-map version."""
    __slots__ = ('_data', '_field')

    def __init__(self, data, field):
        self._data, self._field = data, field

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def __getitem__(self, key):
        return getattr(self._data[key], self._field)

    def items(self):
        return ((key, getattr(value, self._field)) for key, value in self._data.items())

    def values(self):
        return (getattr(value, self._field) for value in self._data.values())


class ResourceLedger:
    def __init__(self, limits: ResourceLimits):
        if type(limits) is not ResourceLimits:
            raise ContractError('immutable resource limits required')
        self._limits = limits
        self._owners = OwnedMap()
        self._closed_owners = OwnedMap()
        self._leases = OwnedMap(width=len(limits.global_residency)*(1+len(limits.role_residency)))
        self._retired = OwnedMap()
        self._spent = {role: {key: 0 for key in caps} for role, caps in limits.role_cumulative.items()}
        self._peak = {key: 0 for key in limits.global_residency}
        self._role_peak = {role: {key: 0 for key in caps} for role, caps in limits.role_residency.items()}
        self._events = OwnedLog()

    @property
    def _objects(self):
        return _LeaseView(self._leases, 'spec')

    @property
    def _refs(self):
        return _LeaseView(self._leases, 'refs')

    @property
    def limits(self):
        return self._limits

    def _event(self, action, owner, objects=(), debit=(), note=''):
        event = ResourceEvent(len(self._events), action, owner, tuple(objects), tuple(debit), str(note))
        self._events = self._events.appended(event)

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
        if (type(objects) is _LeaseView and type(refs) is _LeaseView
                and objects._field == 'spec' and refs._field == 'refs'
                and objects._data is refs._data):
            # The same complete leaves establish global and role-support
            # weights. Every owned mutation prepares their exact augmentation;
            # no externally supplied summary or validity flag is accepted.
            dimensions = tuple(self._limits.global_residency)
            width, values = len(dimensions), objects._data.total
            total = dict(zip(dimensions, values[:width]))
            roles = {role: dict(zip(dimensions, values[(i+1)*width:(i+2)*width]))
                     for i, role in enumerate(self._limits.role_residency)}
            return total, roles
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

    def _set_lease(self, proposed, spec, refs):
        if not refs or any(n <= 0 for n in refs.values()):
            raise ContractError('physical object without a positive live lease')
        owner_roles = {self._owner(owner) for owner in refs}
        dimensions = tuple(self._limits.global_residency)
        sizes = tuple(spec.residency[key] for key in dimensions)
        weights = sizes + tuple(size if role in owner_roles else 0
            for role in self._limits.role_residency for size in sizes)
        proposed.set_weighted(spec.object_id, _Lease(spec, freeze_data(refs)), weights)

    def _checked(self, proposed):
        return self._check_residency(_LeaseView(proposed, 'spec'), _LeaseView(proposed, 'refs'))

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
        proposed, ids, total, roles = self._allocation_plan(owner, objects)
        self._leases = proposed
        self._record_peak(total, roles)
        self._event('allocate', owner, ids, note=note)

    def _allocation_plan(self, owner, objects):
        """The same complete admission checks for preflight and publication."""
        self._owner(owner)
        proposed = self._leases.copy()
        ids = []
        for spec in objects:
            if type(spec) is not ObjectSpec or set(spec.residency) != set(self._limits.global_residency):
                raise ContractError('physical object has an incomplete resource shape')
            if spec.object_id in proposed or spec.object_id in self._retired:
                raise ContractError('physical object identity cannot be overwritten or recycled')
            self._set_lease(proposed, spec, {owner: 1})
            ids.append(spec.object_id)
        total, roles = self._checked(proposed)
        return proposed, ids, total, roles

    def acquire(self, owner: str, object_id: str, *, count: int = 1):
        self._owner(owner)
        natural(count, 'object reference count', positive=True)
        if object_id not in self._objects:
            raise ContractError('cannot share a nonexistent or freed physical object')
        proposed, refs = self._leases.copy(), dict(self._refs[object_id])
        refs[owner] = refs.get(owner, 0)+count
        self._set_lease(proposed, self._objects[object_id], refs)
        total, roles = self._checked(proposed)
        self._leases = proposed
        self._record_peak(total, roles)
        self._event('acquire', owner, (object_id,), (('references', count),))

    def release(self, owner: str, object_id: str, *, count: int = 1):
        self._owner(owner)
        natural(count, 'object reference count', positive=True)
        if object_id not in self._refs or self._refs[object_id].get(owner, 0) < count:
            raise ContractError('release exceeds this owner\'s actual references')
        proposed, retired = self._leases.copy(), self._retired.copy()
        refs = dict(self._refs[object_id])
        remaining = refs[owner]-count
        if remaining:
            refs[owner] = remaining
        else:
            del refs[owner]
        if refs:
            self._set_lease(proposed, self._objects[object_id], refs)
        else:
            del proposed[object_id]
            retired[object_id] = None
        self._leases, self._retired = proposed, retired
        self._event('release', owner, (object_id,), (('references', count),))

    def release_owner(self, owner: str):
        self._owner(owner)
        for object_id, refs in tuple(self._refs.items()):
            if owner in refs:
                self.release(owner, object_id, count=refs[owner])
        # Retain the immutable owner/role assignment. A stale job cannot acquire
        # a recycled identity with a different accounting role.
        self._event('release_owner_objects', owner)

    def release_many(self, releases: tuple[tuple[str, str, int], ...]):
        """Prevalidate all successor-publication releases before changing leases."""
        proposed, retired = self._leases.copy(), self._retired.copy()
        for owner, object_id, count in releases:
            self._owner(owner)
            natural(count, 'object reference count', positive=True)
            if object_id not in proposed or proposed[object_id].refs.get(owner, 0) < count:
                raise ContractError('release batch exceeds an actual owned reference')
            before = proposed[object_id]
            refs = dict(before.refs)
            refs[owner] -= count
            if refs[owner] == 0:
                del refs[owner]
            if refs:
                self._set_lease(proposed, before.spec, refs)
            else:
                del proposed[object_id]
                retired[object_id] = None
        self._leases, self._retired = proposed, retired
        for owner, object_id, count in releases:
            self._event('release', owner, (object_id,), (('references', count),))

    def close_owner(self, owner: str):
        self.release_owner(owner)
        self._closed_owners[owner] = None
        self._event('close_owner', owner)

    def prepare_transfer(self, moves: tuple[tuple[str, str, str, int], ...],
                         releases: tuple[tuple[str, str, int], ...] = (),
                         close_owners: tuple[str, ...] = ()) -> ResourceLedger:
        """Prepare one atomic lease transition without modifying this ledger.

The registered CPU machine may change owners of existing buffers without
copying them. This is not acquire-before-release: only the complete proposed
lease map becomes observable at Runtime's root publication. All existing
preparation allocations, work, peaks and history are retained in the copy.
There is no resource or installation authority outside the owning Runtime.
"""
        proposed = self._detached()
        # Every source debit is checked against the original leases. A move
        # cannot launder an acquired lease through another move in this batch.
        debits = {}
        for source, destination, object_id, count in moves:
            self._owner(source)
            self._owner(destination)
            natural(count, 'transferred reference count', positive=True)
            if source == destination or object_id not in self._refs:
                raise ContractError('atomic transfer requires distinct live owners and an existing object')
            key = (source, object_id)
            debits[key] = debits.get(key, 0)+count
        for source, object_id, count in releases:
            self._owner(source)
            natural(count, 'released reference count', positive=True)
            key = (source, object_id)
            debits[key] = debits.get(key, 0)+count
        if any(self._refs.get(obj, {}).get(owner, 0) < count for (owner, obj), count in debits.items()):
            raise ContractError('atomic transfer/release exceeds original owned references')
        changed = {obj: dict(self._refs[obj]) for _, obj in debits}
        for (owner, obj), count in debits.items():
            changed[obj][owner] -= count
            if not changed[obj][owner]:
                del changed[obj][owner]
        for source, destination, obj, count in moves:
            changed[obj][destination] = changed[obj].get(destination, 0)+count
        for obj, refs in changed.items():
            if refs:
                proposed._set_lease(proposed._leases, self._objects[obj], refs)
            else:
                del proposed._leases[obj]
                proposed._retired[obj] = None
        if len(set(close_owners)) != len(close_owners):
            raise ContractError('duplicate owner closure in atomic transfer')
        for owner in close_owners:
            self._owner(owner)
            if any(owner in refs for refs in proposed._refs.values()):
                raise ContractError('atomic owner closure would discard a retained lease')
            proposed._closed_owners[owner] = None
        total, roles = proposed._check_residency(proposed._objects, proposed._refs)
        proposed._record_peak(total, roles)
        proposed._event('atomic_transfer_begin', 'machine')
        for source, destination, obj, count in moves:
            proposed._event('transfer', source, (obj,), (('references', count),), destination)
        for owner, obj, count in releases:
            proposed._event('release', owner, (obj,), (('references', count),))
        for owner in close_owners:
            proposed._event('close_owner', owner)
        proposed._event('atomic_transfer_end', 'machine')
        return proposed

    def prepare_allocation(self, owner: str, objects: tuple[ObjectSpec, ...]) -> ResourceLedger:
        """Validate a detached allocation before the actual ingress buffer exists."""
        proposed = self._detached()
        proposed.allocate(owner, objects)
        return proposed

    def check_allocation(self, owner: str, objects: tuple[ObjectSpec, ...]):
        """Preflight only; no successor, ledger mutation or reusable authority.

        The caller must still perform the actual checked allocation. Avoid
        cloning history when the only requested result is admission/refusal.
        """
        self._require_complete()
        self._allocation_plan(owner, objects)

    def _require_complete(self):
        fields = {'_limits', '_owners', '_closed_owners', '_leases', '_retired',
                  '_spent', '_peak', '_role_peak', '_events'}
        if type(self) is not ResourceLedger or set(self.__dict__) != fields:
            raise ContractError('physical preparation needs the complete registered ledger state')

    def _detached(self) -> ResourceLedger:
        self._require_complete()
        proposed = object.__new__(ResourceLedger)
        proposed.__dict__ = dict(self.__dict__)
        proposed._owners = self._owners.copy()
        proposed._closed_owners = self._closed_owners.copy()
        proposed._leases = self._leases.copy()
        proposed._retired = self._retired.copy()
        proposed._spent = {key: dict(value) for key, value in self._spent.items()}
        proposed._peak = dict(self._peak)
        proposed._role_peak = {key: dict(value) for key, value in self._role_peak.items()}
        # Every old immutable event remains reachable from both roots. A later
        # append publishes only to its own ledger's event pointer.
        proposed._events = self._events
        return proposed

    def _shrink_object(self, spec):
        """Existing trusted frame relocation; no new object/install authority."""
        prior = self._objects[spec.object_id]
        if (type(spec) is not ObjectSpec or set(spec.residency) != set(prior.residency)
                or spec.provenance != prior.provenance
                or any(spec.residency[key] > prior.residency[key] for key in prior.residency)):
            raise ContractError('owned relocation must preserve identity/provenance and decrease extent')
        proposed = self._leases.copy()
        self._set_lease(proposed, spec, self._refs[spec.object_id])
        self._checked(proposed)
        self._leases = proposed

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
